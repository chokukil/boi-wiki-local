#!/usr/bin/env python3
"""Validate BoI Wiki Local Case Harness packages and honest Reference claims.

This is a release/CI validator. Ordinary employees do not need Python to run a Case Harness.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path

from case_benchmark import summarize as summarize_benchmark


REQUIRED_MANIFEST = {
    "schema",
    "case_id",
    "title",
    "category",
    "status",
    "version",
    "audience",
    "start_prompt",
    "logical_roles",
    "reviewer_role",
    "orchestration_pattern",
    "scale_modes",
    "required_skills",
    "optional_features",
    "fixture_policy",
    "expected_local_types",
    "direct_promotion_blocked_types",
    "direct_promotion_blocked_roles",
    "eval_prompt_count",
    "evaluation_protocol",
    "fixture_id",
    "runtime_contract",
    "runtime_manifest",
    "handoff_schema",
    "reference_gate",
    "domain_validation",
}
REQUIRED_FILES = (
    "CASE.md",
    "case.yaml",
    "orchestrator.md",
    "roles/roles.md",
    "runtime/dispatch.md",
    "runtime/runtime.yaml",
    "prompts/evals.md",
    "references/method.md",
    "fixtures/fixture.md",
    "fixtures/source-pack.md",
    "fixtures/manifest.json",
    "expected/local-output.md",
    "expected/OUTPUT-CONTRACT.md",
    "walkthrough/01-run.md",
    "evals/eval-plan.yaml",
    "evals/assertions.json",
    "evals/prompts/prompt-catalog.json",
    "evals/runs/run-index.json",
    "evals/blind-comparison/comparisons.json",
    "evals/failures/failures.json",
    "evals/external-evidence.example.json",
    "evals/benchmark.json",
    "evals/BENCHMARK.md",
)
FLAGSHIP_REQUIRED_FILES = (
    "evals/PROTOCOL.md",
    "evals/baseline.md",
    "evals/run-artifact.schema.json",
    "evals/rubric.json",
    "evals/seeds/seed-catalog.json",
)
SCALE_MODES = {"full", "reduced", "single-agent", "no-team-fallback"}
BLOCKED_TYPES = {
    "boi/local-evidence",
    "boi/local-capture",
    "boi/local-hypothesis",
    "boi/local-analysis-log",
    "boi/local-analysis-case",
}
BLOCKED_ROLES = {"agent-memory", "source-record"}
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def markdown_contract_errors(base: Path, case_id: str, cases_root: Path) -> list[str]:
    errors: list[str] = []
    for path in base.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        controls = sorted({ord(char) for char in text if ord(char) < 32 and char not in "\n\r\t"})
        if controls:
            errors.append(f"{case_id}: control characters {controls} in {path.relative_to(base).as_posix()}")
        for target in MARKDOWN_LINK.findall(text):
            clean = target.split("#", 1)[0].strip()
            if not clean or re.match(r"^(?:https?://|mailto:)", clean, re.IGNORECASE):
                continue
            resolved = (path.parent / clean).resolve()
            try:
                resolved.relative_to(base.resolve())
            except ValueError:
                try:
                    shared_relative = resolved.relative_to((cases_root / "_schema").resolve())
                except ValueError:
                    errors.append(f"{case_id}: link escapes Case package: {target}")
                    continue
                if not shared_relative.parts:
                    errors.append(f"{case_id}: link targets shared schema directory, not a file: {target}")
                    continue
            if not resolved.exists():
                errors.append(
                    f"{case_id}: broken link in {path.relative_to(base).as_posix()}: {target}"
                )
    return errors


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid JSON-compatible YAML/JSON: {path}: {exc}") from exc


def finite_at_least(value: object, threshold: float) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(value) and value >= threshold


def finite_at_most(value: object, threshold: float) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(value) and value <= threshold


def frozen_protocol_errors(
    *,
    base: Path,
    case: dict,
    plan: dict,
    assertions: dict,
    prompts: list[dict],
    fixture_manifest: dict,
) -> list[str]:
    """Validate the common v2 evidence contract used by non-flagship Cases."""
    errors: list[str] = []
    case_id = str(case.get("case_id"))
    expected_revision = str(case.get("evaluation_protocol", ""))
    try:
        seed_catalog = load_json(base / "evals" / "seeds" / "seed-catalog.json")
        rubric = load_json(base / "evals" / "rubric.json")
        artifact_schema = load_json(base / "evals" / "run-artifact.schema.json")
    except ValueError as exc:
        return [str(exc)]
    if expected_revision != "case-eval/v2":
        errors.append(f"{case_id}: non-flagship evaluation_protocol must be case-eval/v2")
    if plan.get("schema") != "boi-local-case-eval-plan/v2" or plan.get("protocol_revision") != expected_revision:
        errors.append(f"{case_id}: frozen protocol v2 is required")
    if case.get("fixture_id") != fixture_manifest.get("fixture_id"):
        errors.append(f"{case_id}: case and fixture manifest fixture_id differ")
    if plan.get("fresh_workspace_per_execution") is not True:
        errors.append(f"{case_id}: fresh_workspace_per_execution must be true")
    if plan.get("cross_run_state_allowed") is not False or plan.get("network_enabled") is not False:
        errors.append(f"{case_id}: cross-run state and network must be disabled")
    if plan.get("configurations") != ["with-harness", "baseline"]:
        errors.append(f"{case_id}: with-Harness and baseline configurations are required")
    expected_refs = {
        "baseline_contract": "baseline.md",
        "run_artifact_schema": "run-artifact.schema.json",
        "rubric": "rubric.json",
        "fixture_manifest": "../fixtures/manifest.json",
        "seed_catalog": "seeds/seed-catalog.json",
    }
    for field, expected in expected_refs.items():
        if plan.get(field) != expected:
            errors.append(f"{case_id}: plan {field} must be {expected}")
    if assertions.get("schema") != "boi-local-case-assertions/v2":
        errors.append(f"{case_id}: assertion contract v2 is required")
    required_prompt_fields = {
        "prompt_id",
        "scenario",
        "label",
        "user_prompt",
        "interaction",
        "seed_id",
        "inputs",
        "expected_operations",
        "required_outcomes",
        "forbidden_outcomes",
    }
    fixture_paths = {str(item.get("path", "")) for item in fixture_manifest.get("files", [])}
    for prompt in prompts:
        prompt_id = str(prompt.get("prompt_id"))
        missing_prompt_fields = required_prompt_fields - set(prompt)
        if missing_prompt_fields:
            errors.append(f"{case_id}: {prompt_id} missing prompt fields {sorted(missing_prompt_fields)}")
        if len(str(prompt.get("user_prompt", ""))) < 80:
            errors.append(f"{case_id}: {prompt_id} user_prompt is not execution-ready")
        interaction = prompt.get("interaction", {})
        turns = interaction.get("turns", []) if isinstance(interaction, dict) else []
        if interaction.get("mode") not in {"single-turn", "scripted-multi-turn"}:
            errors.append(f"{case_id}: {prompt_id} interaction mode is invalid")
        if not isinstance(turns, list) or not turns:
            errors.append(f"{case_id}: {prompt_id} interaction turns are empty")
        else:
            expected_turns = list(range(1, len(turns) + 1))
            actual_turns = [turn.get("turn") for turn in turns if isinstance(turn, dict)]
            if actual_turns != expected_turns:
                errors.append(f"{case_id}: {prompt_id} interaction turns are not sequential")
            if any(turn.get("role") != "user" or not str(turn.get("text", "")).strip() for turn in turns):
                errors.append(f"{case_id}: {prompt_id} interaction contains an invalid user turn")
            if str(turns[0].get("text", "")) != str(prompt.get("user_prompt", "")):
                errors.append(f"{case_id}: {prompt_id} first interaction turn differs from user_prompt")
            if interaction.get("mode") == "single-turn" and len(turns) != 1:
                errors.append(f"{case_id}: {prompt_id} single-turn interaction has extra turns")
        for field in ("inputs", "expected_operations", "required_outcomes", "forbidden_outcomes"):
            value = prompt.get(field)
            if not isinstance(value, list) or (not value and not (prompt_id == "p04" and field == "inputs")):
                errors.append(f"{case_id}: {prompt_id} {field} is empty")
        for input_path in prompt.get("inputs", []):
            value = str(input_path)
            if value.endswith("/*"):
                prefix = value[:-1]
                if not any(path.startswith(prefix) for path in fixture_paths):
                    errors.append(f"{case_id}: {prompt_id} input glob matches no fixture")
            elif value not in fixture_paths:
                errors.append(f"{case_id}: {prompt_id} input is not in fixture manifest: {value}")
    seed_entries = seed_catalog.get("seeds", [])
    seed_ids = {entry.get("seed_id") for entry in seed_entries}
    if seed_catalog.get("schema") != "boi-local-eval-seed-catalog/v1" or len(seed_ids) != 3:
        errors.append(f"{case_id}: three deterministic evaluation seeds are required")
    if seed_catalog.get("fixture_id") != fixture_manifest.get("fixture_id"):
        errors.append(f"{case_id}: seed and fixture catalog identity differ")
    used_prompt_ids: list[str] = []
    for entry in seed_entries:
        manifest_relative = str(entry.get("manifest", ""))
        manifest_path = (base / "evals" / "seeds" / manifest_relative).resolve()
        try:
            manifest_path.relative_to((base / "evals" / "seeds").resolve())
        except ValueError:
            errors.append(f"{case_id}: seed manifest escapes seed root")
            continue
        if not manifest_path.is_file():
            errors.append(f"{case_id}: missing seed manifest {manifest_relative}")
            continue
        manifest_bytes = manifest_path.read_bytes()
        if hashlib.sha256(manifest_bytes).hexdigest() != entry.get("manifest_sha256"):
            errors.append(f"{case_id}: seed manifest hash mismatch {manifest_relative}")
        try:
            seed_manifest = json.loads(manifest_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            errors.append(f"{case_id}: invalid seed manifest {manifest_relative}")
            continue
        if seed_manifest.get("schema") != "boi-local-eval-seed-manifest/v1":
            errors.append(f"{case_id}: invalid seed manifest schema {manifest_relative}")
        seed_root = manifest_path.parent
        for seed_file in seed_manifest.get("files", []):
            seed_path = (seed_root / str(seed_file.get("path", ""))).resolve()
            try:
                seed_path.relative_to(seed_root.resolve())
            except ValueError:
                errors.append(f"{case_id}: seed file escapes seed root")
                continue
            if not seed_path.is_file():
                errors.append(f"{case_id}: missing seed file {seed_file.get('path')}")
                continue
            if (
                hashlib.sha256(seed_path.read_bytes()).hexdigest() != seed_file.get("sha256")
                or seed_path.stat().st_size != seed_file.get("bytes")
            ):
                errors.append(f"{case_id}: seed hash or size mismatch {seed_file.get('path')}")
        used_prompt_ids.extend(entry.get("used_by_prompts", []))
    prompt_ids = {prompt.get("prompt_id") for prompt in prompts}
    if set(used_prompt_ids) != prompt_ids or len(used_prompt_ids) != len(prompt_ids):
        errors.append(f"{case_id}: every prompt must map to exactly one seed")
    for prompt in prompts:
        if prompt.get("seed_id") not in seed_ids:
            errors.append(f"{case_id}: {prompt.get('prompt_id')} references an unknown seed")
    if rubric.get("schema") != "boi-local-case-rubric/v2" or sum(
        int(item.get("points", 0)) for item in rubric.get("dimensions", [])
    ) != 100:
        errors.append(f"{case_id}: rubric must total 100 points")
    if artifact_schema.get("$id") != "boi-local-case-run-artifact/v2":
        errors.append(f"{case_id}: run artifact schema v2 is required")
    schema_required = set(artifact_schema.get("required", []))
    schema_properties = artifact_schema.get("properties", {})
    if not schema_required or not schema_required.issubset(set(schema_properties)):
        errors.append(f"{case_id}: run artifact required fields and properties differ")
    if schema_properties.get("case_id", {}).get("const") != case_id:
        errors.append(f"{case_id}: run artifact case_id is not frozen")
    if schema_properties.get("protocol_revision", {}).get("const") != expected_revision:
        errors.append(f"{case_id}: run artifact protocol revision is not frozen")
    if "interaction_script_sha256" not in schema_required:
        errors.append(f"{case_id}: run artifact must bind the interaction script")
    protocol_text = (base / "evals" / "PROTOCOL.md").read_text(encoding="utf-8")
    for literal in ("fresh", "baseline", "SHA256", "blind", "runtime", expected_revision):
        if literal.lower() not in protocol_text.lower():
            errors.append(f"{case_id}: protocol is missing {literal}")
    return errors


def reference_gate_errors(case: dict, plan: dict, benchmark: dict) -> list[str]:
    errors: list[str] = []
    required = int(plan.get("required_executions", 0))
    checks = {
        "completed executions": benchmark.get("completed_executions") == required and required > 0,
        "objective assertions": finite_at_least(benchmark.get("objective_assertion_pass_rate"), 0.95),
        "hard safety": finite_at_least(benchmark.get("hard_safety_pass_rate"), 1.0),
        "median score": finite_at_least(benchmark.get("median_score"), 85),
        "blind win": finite_at_least(benchmark.get("blind_win_rate"), 0.70),
        "blind win or tie": finite_at_least(benchmark.get("blind_win_or_tie_rate"), 0.90),
        "score stability": finite_at_most(benchmark.get("score_stddev"), 10),
        "Codex": benchmark.get("codex_validated") is True,
        "Claude": benchmark.get("claude_validated") is True,
        "non-developer acceptance": benchmark.get("non_developer_acceptance") is True,
        "actual BoI validator": benchmark.get("actual_boi_validator") is True,
        "production gate": benchmark.get("production_quality_gate_passed") is True,
        "reference eligibility": benchmark.get("reference_eligible") is True,
    }
    for label, ok in checks.items():
        if not ok:
            errors.append(f"{case['case_id']}: Reference gate missing {label}")
    return errors


def validate_case(base: Path, catalog_entry: dict, cases_root: Path) -> tuple[list[str], dict]:
    errors: list[str] = []
    required_files = REQUIRED_FILES + FLAGSHIP_REQUIRED_FILES
    for relative in required_files:
        if not (base / relative).is_file():
            errors.append(f"{catalog_entry.get('case_id')}: missing {relative}")
    if errors:
        return errors, {}
    try:
        case = load_json(base / "case.yaml")
        plan = load_json(base / "evals" / "eval-plan.yaml")
        assertions = load_json(base / "evals" / "assertions.json")
        benchmark = load_json(base / "evals" / "benchmark.json")
        prompt_catalog = load_json(base / "evals" / "prompts" / "prompt-catalog.json")
        fixture_manifest = load_json(base / "fixtures" / "manifest.json")
    except ValueError as exc:
        return [str(exc)], {}

    missing = sorted(REQUIRED_MANIFEST - set(case))
    if missing:
        errors.append(f"{case.get('case_id')}: missing manifest fields {missing}")
    if case.get("schema") != "boi-local-case-harness/v1":
        errors.append(f"{case.get('case_id')}: wrong case schema")
    if case.get("case_id") != catalog_entry.get("case_id"):
        errors.append(f"{base}: catalog and manifest case_id differ")
    if case.get("status") != catalog_entry.get("status"):
        errors.append(f"{case.get('case_id')}: catalog and manifest status differ")
    if case.get("status") not in {"community", "verified", "reference"}:
        errors.append(f"{case.get('case_id')}: invalid status")
    if case.get("runtime_contract") != "boi-local-case-runtime/v1":
        errors.append(f"{case.get('case_id')}: runtime contract v1 is required")
    if case.get("runtime_manifest") != "runtime/runtime.yaml":
        errors.append(f"{case.get('case_id')}: runtime manifest path is not canonical")
    if case.get("handoff_schema") != "cases/_schema/handoff.schema.json":
        errors.append(f"{case.get('case_id')}: common handoff schema is required")
    roles = case.get("logical_roles", [])
    if not isinstance(roles, list) or not 4 <= len(roles) <= 5 or len(set(roles)) != len(roles):
        errors.append(f"{case.get('case_id')}: logical_roles must contain 4–5 unique roles")
    if case.get("reviewer_role") not in roles:
        errors.append(f"{case.get('case_id')}: reviewer_role must be one of logical_roles")
    required_skills = set(case.get("required_skills", []))
    optional_features = set(case.get("optional_features", []))
    overlap = sorted(required_skills & optional_features)
    if overlap:
        errors.append(f"{case.get('case_id')}: required skills cannot also be optional features: {overlap}")
    roles_text = (base / "roles" / "roles.md").read_text(encoding="utf-8")
    for role in roles:
        if role not in roles_text:
            errors.append(f"{case.get('case_id')}: role page is missing {role}")
        role_path = base / "roles" / f"{role}.md"
        if not role_path.is_file():
            errors.append(f"{case.get('case_id')}: progressive role card is missing {role}")
            continue
        role_card = role_path.read_text(encoding="utf-8")
        for literal in (
            f"name: {role}",
            f"case_id: {case.get('case_id')}",
            "boi-local-case-handoff/v1",
            "## Exit criteria",
            "## Hard fail",
            "## Scale behavior",
        ):
            if literal not in role_card:
                errors.append(f"{case.get('case_id')}: {role} card is missing {literal}")
        expected_reviewer = role == case.get("reviewer_role")
        if f"independent_reviewer: {str(expected_reviewer).lower()}" not in role_card:
            errors.append(f"{case.get('case_id')}: {role} reviewer flag is wrong")
    for literal in ("exit criteria", "hard fail", "independent"):
        if literal.lower() not in roles_text.lower():
            errors.append(f"{case.get('case_id')}: role contract is missing {literal}")
    try:
        runtime = load_json(base / "runtime" / "runtime.yaml")
    except ValueError as exc:
        errors.append(str(exc))
        runtime = {}
    if runtime.get("schema") != "boi-local-case-runtime/v1" or runtime.get("case_id") != case.get("case_id"):
        errors.append(f"{case.get('case_id')}: runtime manifest identity is invalid")
    runtime_roles = runtime.get("role_cards", [])
    if {item.get("role") for item in runtime_roles} != set(roles) or len(runtime_roles) != len(roles):
        errors.append(f"{case.get('case_id')}: runtime role card set differs from manifest")
    reviewer_rows = [item for item in runtime_roles if item.get("independent_reviewer") is True]
    if len(reviewer_rows) != 1 or reviewer_rows[0].get("role") != case.get("reviewer_role"):
        errors.append(f"{case.get('case_id')}: runtime independent reviewer mapping is invalid")
    dispatch_text = (base / "runtime" / "dispatch.md").read_text(encoding="utf-8")
    for literal in ("Load order", "Runtime mapping", "Handoff envelope", "Stop conditions"):
        if literal.lower() not in dispatch_text.lower():
            errors.append(f"{case.get('case_id')}: runtime dispatch is missing {literal}")
    orchestrator_text = (base / "orchestrator.md").read_text(encoding="utf-8")
    for literal in ("Dependency DAG", "Scale modes", "Failure", "source hash", "review"):
        if literal.lower() not in orchestrator_text.lower():
            errors.append(f"{case.get('case_id')}: orchestrator is missing {literal}")
    if not SCALE_MODES.issubset(set(case.get("scale_modes", []))):
        errors.append(f"{case.get('case_id')}: all scale modes are required")
    if not BLOCKED_TYPES.issubset(set(case.get("direct_promotion_blocked_types", []))):
        errors.append(f"{case.get('case_id')}: direct promotion block list is incomplete")
    if not BLOCKED_ROLES.issubset(set(case.get("direct_promotion_blocked_roles", []))):
        errors.append(f"{case.get('case_id')}: role-based direct promotion block list is incomplete")
    expected_prompts = 8 if catalog_entry.get("flagship") else 5
    if case.get("eval_prompt_count") != expected_prompts:
        errors.append(f"{case.get('case_id')}: expected {expected_prompts} eval prompts")
    required_runs = expected_prompts * 2 * 3 * 2
    if plan.get("required_executions") != required_runs:
        errors.append(f"{case.get('case_id')}: required_executions must be {required_runs}")
    if plan.get("runtimes") != ["codex", "claude"] or plan.get("repetitions") != 3:
        errors.append(f"{case.get('case_id')}: cross-runtime repetition contract is incomplete")
    prompts = prompt_catalog.get("prompts", [])
    if len(prompts) != expected_prompts or any(len(str(item.get("label", ""))) < 20 for item in prompts):
        errors.append(f"{case.get('case_id')}: eval prompts must be complete natural-language requests")
    if not any("near-miss" in str(item.get("label", "")).lower() for item in prompts):
        errors.append(f"{case.get('case_id')}: near-miss prompt is missing")
    if assertions.get("case_id") != case.get("case_id") or not assertions.get("hard"):
        errors.append(f"{case.get('case_id')}: assertion contract is incomplete")
    if prompt_catalog.get("schema") != "boi-local-case-prompt-catalog/v2":
        errors.append(f"{case.get('case_id')}: prompt catalog v2 is required")
    expected_text = (base / "expected" / "local-output.md").read_text(encoding="utf-8")
    required_expected_literals = [
        'okf_version: "0.1"',
        'boi_profile_version: "0.1-local"',
        "visibility: local-private",
        "local_only: true",
    ]
    if case.get("case_id") in {
        "agentic-ai-change-radar",
        "fab-logistics-digital-twin",
        "scientific-foundation-model-knowledge",
    }:
        required_expected_literals.extend(
            [
                "type:",
                "title:",
                "description:",
                "classification: internal",
                "owner:",
                "employee_id:",
                "local_owner_ref:",
                "promotion_status: local_only",
                "retention_class:",
                "archive_status: active",
                "artifact_visibility:",
                "lifecycle_state:",
                "memory_candidate:",
                "cleanup_policy:",
                "review_after:",
                "contains_sensitive:",
                "source_refs:",
                "generated_from:",
            ]
        )
    for literal in required_expected_literals:
        if literal not in expected_text:
            errors.append(f"{case.get('case_id')}: expected output missing {literal}")
    if case.get("case_id") in {
        "agentic-ai-change-radar",
        "fab-logistics-digital-twin",
        "scientific-foundation-model-knowledge",
    }:
        generated_block = re.search(r"(?ms)^generated_from:\s*\n(?P<body>(?:[ \t]+.*\n?)*)", expected_text)
        generated_items = (
            re.findall(
                r"(?ms)^\s+-\s+type:\s*[^\n]+\n\s+ref:\s*([^\n]+)\n\s+sha256:\s*([0-9a-f]{64})\s*$",
                generated_block.group("body"),
            )
            if generated_block
            else []
        )
        if not generated_items:
            errors.append(f"{case.get('case_id')}: expected output requires hash-bound generated_from")
        for raw_ref, expected_hash in generated_items:
            ref = raw_ref.strip().strip('"').strip("'")
            generated_path = ((base / "expected") / ref).resolve()
            if not generated_path.is_file():
                errors.append(f"{case.get('case_id')}: expected output generated_from target missing: {ref}")
                continue
            if hashlib.sha256(generated_path.read_bytes()).hexdigest() != expected_hash:
                errors.append(f"{case.get('case_id')}: expected output generated_from hash mismatch: {ref}")
    fixture_text = (base / "fixtures" / "fixture.md").read_text(encoding="utf-8")
    if not re.search(r"synthetic|합성|public", fixture_text, re.IGNORECASE):
        errors.append(f"{case.get('case_id')}: fixture policy is not visible")
    fixture_policy = case.get("fixture_policy")
    manifest_synthetic = fixture_manifest.get("synthetic")
    fixture_policy_valid = (
        (fixture_policy == "synthetic-only" and manifest_synthetic is True)
        or (fixture_policy == "public-only" and manifest_synthetic is False)
        or (fixture_policy == "synthetic-or-public" and isinstance(manifest_synthetic, bool))
    )
    if fixture_manifest.get("case_id") != case.get("case_id") or not fixture_policy_valid:
        errors.append(f"{case.get('case_id')}: fixture manifest identity or fixture policy flag is invalid")
    if fixture_manifest.get("fixture_policy", fixture_policy) != fixture_policy:
        errors.append(f"{case.get('case_id')}: case and fixture manifest policy differ")
    minimum_sources = 20 if catalog_entry.get("flagship") else 5
    if fixture_manifest.get("source_count", 0) < minimum_sources:
        errors.append(f"{case.get('case_id')}: fixture needs at least {minimum_sources} deterministic sources")
    fixture_files = fixture_manifest.get("files", [])
    if fixture_manifest.get("source_count") != len(fixture_files):
        errors.append(f"{case.get('case_id')}: source_count must equal the number of manifest files")
    fixture_hashes: dict[str, str] = {}
    fixture_paths: set[str] = set()
    for item in fixture_files:
        item_path = str(item.get("path", ""))
        if item_path in fixture_paths:
            errors.append(f"{case.get('case_id')}: duplicate fixture manifest path {item_path}")
        fixture_paths.add(item_path)
        fixture_path = (base / "fixtures" / str(item.get("path", ""))).resolve()
        try:
            fixture_path.relative_to((base / "fixtures").resolve())
        except ValueError:
            errors.append(f"{case.get('case_id')}: fixture path escapes package")
            continue
        if not fixture_path.is_file():
            errors.append(f"{case.get('case_id')}: missing fixture file {item.get('path')}")
            continue
        digest = hashlib.sha256(fixture_path.read_bytes()).hexdigest()
        fixture_hashes[item_path] = digest
        if digest != item.get("sha256") or fixture_path.stat().st_size != item.get("bytes"):
            errors.append(f"{case.get('case_id')}: fixture hash or size mismatch for {item.get('path')}")
    if fixture_manifest.get("schema") != "boi-local-case-fixture-manifest/v2":
        errors.append(f"{case.get('case_id')}: fixture manifest must use v2 with real files")
    if catalog_entry.get("flagship"):
        suffixes = {Path(path).suffix.lower() for path in fixture_paths}
        for suffix in {".eml", ".md", ".csv", ".pdf", ".png", ".txt"}:
            if suffix not in suffixes:
                errors.append(f"{case.get('case_id')}: flagship fixture missing {suffix} input")
        required_media = set(fixture_manifest.get("required_media", []))
        if not {"email", "web-clip", "tabular-data", "pdf", "image", "meeting-note"}.issubset(required_media):
            errors.append(f"{case.get('case_id')}: flagship fixture media coverage is incomplete")
        duplicate_groups = fixture_manifest.get("intentional_duplicate_groups", [])
        if not duplicate_groups:
            errors.append(f"{case.get('case_id')}: deterministic duplicate group is missing")
        for group in duplicate_groups:
            paths = group.get("paths", [])
            hashes = {fixture_hashes.get(path) for path in paths}
            if len(paths) < 2 or None in hashes or len(hashes) != 1 or group.get("sha256") not in hashes:
                errors.append(f"{case.get('case_id')}: intentional duplicate group does not match file hashes")

        try:
            seed_catalog = load_json(base / "evals" / "seeds" / "seed-catalog.json")
            rubric = load_json(base / "evals" / "rubric.json")
            artifact_schema = load_json(base / "evals" / "run-artifact.schema.json")
        except ValueError as exc:
            errors.append(str(exc))
            seed_catalog, rubric, artifact_schema = {}, {}, {}
        if plan.get("schema") != "boi-local-case-eval-plan/v2" or plan.get("protocol_revision") != "second-brain-eval/v2":
            errors.append(f"{case.get('case_id')}: flagship frozen protocol v2 is required")
        for flag in ("fresh_workspace_per_execution",):
            if plan.get(flag) is not True:
                errors.append(f"{case.get('case_id')}: {flag} must be true")
        if plan.get("cross_run_state_allowed") is not False or plan.get("network_enabled") is not False:
            errors.append(f"{case.get('case_id')}: cross-run state and network must be disabled")
        required_prompt_fields = {
            "prompt_id",
            "scenario",
            "label",
            "user_prompt",
            "interaction",
            "seed_id",
            "inputs",
            "expected_operations",
            "required_outcomes",
            "forbidden_outcomes",
        }
        for prompt in prompts:
            missing_prompt_fields = required_prompt_fields - set(prompt)
            if missing_prompt_fields:
                errors.append(
                    f"{case.get('case_id')}: {prompt.get('prompt_id')} missing prompt fields {sorted(missing_prompt_fields)}"
                )
            if len(str(prompt.get("user_prompt", ""))) < 80:
                errors.append(f"{case.get('case_id')}: {prompt.get('prompt_id')} user_prompt is not execution-ready")
            interaction = prompt.get("interaction", {})
            turns = interaction.get("turns", []) if isinstance(interaction, dict) else []
            scripted_turns = {"p01": 3, "p03": 2, "p04": 6, "p05": 2}
            expected_turn_count = scripted_turns.get(prompt.get("prompt_id"), 1)
            expected_mode = "scripted-multi-turn" if expected_turn_count > 1 else "single-turn"
            if interaction.get("mode") != expected_mode or len(turns) != expected_turn_count:
                errors.append(
                    f"{case.get('case_id')}: {prompt.get('prompt_id')} interaction must be "
                    f"{expected_mode} with {expected_turn_count} user turn(s)"
                )
            if turns:
                actual_turns = [turn.get("turn") for turn in turns if isinstance(turn, dict)]
                if actual_turns != list(range(1, len(turns) + 1)):
                    errors.append(f"{case.get('case_id')}: {prompt.get('prompt_id')} interaction turns are not sequential")
                if any(turn.get("role") != "user" or not str(turn.get("text", "")).strip() for turn in turns):
                    errors.append(f"{case.get('case_id')}: {prompt.get('prompt_id')} interaction contains an invalid user turn")
                if str(turns[0].get("text", "")) != str(prompt.get("user_prompt", "")):
                    errors.append(f"{case.get('case_id')}: {prompt.get('prompt_id')} first turn differs from user_prompt")
            for field in ("inputs", "expected_operations", "required_outcomes", "forbidden_outcomes"):
                if not isinstance(prompt.get(field), list) or not prompt.get(field):
                    errors.append(f"{case.get('case_id')}: {prompt.get('prompt_id')} {field} is empty")
            for input_path in prompt.get("inputs", []):
                value = str(input_path)
                if value.endswith("/*"):
                    prefix = value[:-1]
                    if not any(path.startswith(prefix) for path in fixture_paths):
                        errors.append(f"{case.get('case_id')}: {prompt.get('prompt_id')} input glob matches no fixture")
                elif value not in fixture_paths:
                    errors.append(f"{case.get('case_id')}: {prompt.get('prompt_id')} input is not in fixture manifest: {value}")
        seed_entries = seed_catalog.get("seeds", [])
        seed_ids = {entry.get("seed_id") for entry in seed_entries}
        if seed_catalog.get("schema") != "boi-local-eval-seed-catalog/v1" or len(seed_ids) != 4:
            errors.append(f"{case.get('case_id')}: four deterministic evaluation seeds are required")
        used_prompt_ids: list[str] = []
        for entry in seed_entries:
            manifest_relative = str(entry.get("manifest", ""))
            manifest_path = (base / "evals" / "seeds" / manifest_relative).resolve()
            try:
                manifest_path.relative_to((base / "evals" / "seeds").resolve())
            except ValueError:
                errors.append(f"{case.get('case_id')}: seed manifest escapes seed root")
                continue
            if not manifest_path.is_file():
                errors.append(f"{case.get('case_id')}: missing seed manifest {manifest_relative}")
                continue
            manifest_bytes = manifest_path.read_bytes()
            if hashlib.sha256(manifest_bytes).hexdigest() != entry.get("manifest_sha256"):
                errors.append(f"{case.get('case_id')}: seed manifest hash mismatch {manifest_relative}")
            try:
                seed_manifest = json.loads(manifest_bytes.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                errors.append(f"{case.get('case_id')}: invalid seed manifest {manifest_relative}")
                continue
            seed_root = manifest_path.parent
            for seed_file in seed_manifest.get("files", []):
                seed_path = (seed_root / str(seed_file.get("path", ""))).resolve()
                try:
                    seed_path.relative_to(seed_root.resolve())
                except ValueError:
                    errors.append(f"{case.get('case_id')}: seed file escapes seed root")
                    continue
                if not seed_path.is_file():
                    errors.append(f"{case.get('case_id')}: missing seed file {seed_file.get('path')}")
                    continue
                if (
                    hashlib.sha256(seed_path.read_bytes()).hexdigest() != seed_file.get("sha256")
                    or seed_path.stat().st_size != seed_file.get("bytes")
                ):
                    errors.append(f"{case.get('case_id')}: seed hash or size mismatch {seed_file.get('path')}")
            used_prompt_ids.extend(entry.get("used_by_prompts", []))
        prompt_ids = {prompt.get("prompt_id") for prompt in prompts}
        if set(used_prompt_ids) != prompt_ids or len(used_prompt_ids) != len(prompt_ids):
            errors.append(f"{case.get('case_id')}: every prompt must map to exactly one seed")
        for prompt in prompts:
            if prompt.get("seed_id") not in seed_ids:
                errors.append(f"{case.get('case_id')}: {prompt.get('prompt_id')} references an unknown seed")
        if rubric.get("schema") != "boi-local-case-rubric/v2" or sum(
            int(item.get("points", 0)) for item in rubric.get("dimensions", [])
        ) != 100:
            errors.append(f"{case.get('case_id')}: flagship rubric must total 100 points")
        if artifact_schema.get("$id") != "boi-local-case-run-artifact/v2":
            errors.append(f"{case.get('case_id')}: run artifact schema v2 is required")
        schema_required = set(artifact_schema.get("required", []))
        schema_properties = set(artifact_schema.get("properties", {}))
        if not schema_required or not schema_required.issubset(schema_properties):
            errors.append(f"{case.get('case_id')}: run artifact required fields and properties differ")
        if "interaction_script_sha256" not in schema_required:
            errors.append(f"{case.get('case_id')}: run artifact must bind the interaction script")
        protocol_text = (base / "evals" / "PROTOCOL.md").read_text(encoding="utf-8")
        for literal in ("fresh", "baseline", "SHA256", "blind", "runtime", "second-brain-eval/v2"):
            if literal.lower() not in protocol_text.lower():
                errors.append(f"{case.get('case_id')}: protocol is missing {literal}")
    else:
        errors.extend(
            frozen_protocol_errors(
                base=base,
                case=case,
                plan=plan,
                assertions=assertions,
                prompts=prompts,
                fixture_manifest=fixture_manifest,
            )
        )
    markdown = "\n".join(path.read_text(encoding="utf-8") for path in base.rglob("*.md"))
    if "[[" in markdown or "]]" in markdown:
        errors.append(f"{case.get('case_id')}: Obsidian-only wikilink found")
    errors.extend(markdown_contract_errors(base, str(case.get("case_id")), cases_root))
    if benchmark.get("case_id") != case.get("case_id"):
        errors.append(f"{case.get('case_id')}: benchmark case_id differs")
    calculated = summarize_benchmark(base)
    if calculated.get("errors"):
        errors.extend(f"{case.get('case_id')}: benchmark evidence: {item}" for item in calculated["errors"])
    if case.get("status") == "reference":
        errors.extend(reference_gate_errors(case, plan, benchmark))
        comparable = {key: value for key, value in calculated.items() if key != "errors"}
        if benchmark != comparable:
            errors.append(f"{case.get('case_id')}: benchmark.json does not match recorded evidence")
    elif benchmark.get("reference_eligible") is True or benchmark.get("production_quality_gate_passed") is True:
        errors.append(f"{case.get('case_id')}: non-Reference case claims a passed production gate")
    return errors, {
        "case_id": case.get("case_id"),
        "status": case.get("status"),
        "required_executions": required_runs,
        "completed_executions": benchmark.get("completed_executions", 0),
        "reference_eligible": benchmark.get("reference_eligible", False),
    }


def inspect(root: Path) -> dict:
    cases_root = root / "cases"
    errors: list[str] = []
    handoff_schema_path = cases_root / "_schema" / "handoff.schema.json"
    try:
        handoff_schema = load_json(handoff_schema_path)
        if handoff_schema.get("$id") != "boi-local-case-handoff/v1":
            errors.append("invalid common Case handoff schema")
        required = set(handoff_schema.get("required", []))
        properties = set(handoff_schema.get("properties", {}))
        if not required or not required.issubset(properties):
            errors.append("handoff schema required fields and properties differ")
    except ValueError as exc:
        errors.append(str(exc))
    try:
        catalog = load_json(cases_root / "catalog.json")
    except ValueError as exc:
        return {"ok": False, "errors": [str(exc)], "cases": []}
    entries = catalog.get("cases", [])
    if catalog.get("schema") != "boi-local-case-catalog/v1" or not isinstance(entries, list):
        errors.append("invalid case catalog")
        entries = []
    seen: set[str] = set()
    results: list[dict] = []
    for entry in entries:
        case_id = entry.get("case_id")
        if case_id in seen:
            errors.append(f"duplicate catalog case_id: {case_id}")
            continue
        seen.add(case_id)
        case_errors, result = validate_case(cases_root / str(entry.get("path", "")), entry, cases_root)
        errors.extend(case_errors)
        if result:
            results.append(result)
    required_total = sum(int(item.get("required_executions", 0)) for item in results)
    return {
        "schema": "boi-local-case-validation/v1",
        "ok": not errors,
        "case_count": len(results),
        "required_comparison_executions": required_total,
        "reference_count": sum(item.get("status") == "reference" for item in results),
        "production_quality_gate_passed": bool(results) and all(item.get("reference_eligible") for item in results),
        "cases": results,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    payload = inspect(Path(args.root).resolve())
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
