#!/usr/bin/env python3
"""Summarize recorded Case Harness runs without executing agents or inventing evidence.

This is a maintainer/CI evidence oracle. It is not required for employee use.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import math
import statistics
from pathlib import Path


RUNTIMES = ("codex", "claude")
CONFIGURATIONS = ("with-harness", "baseline")
HEX_64 = set("0123456789abcdef")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_inside(root: Path, relative: object) -> Path | None:
    path = (root / str(relative or "")).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        return None
    return path


def resolve_from(base: Path, allowed_root: Path, relative: object) -> Path | None:
    path = (base / str(relative or "")).resolve()
    try:
        path.relative_to(allowed_root.resolve())
    except ValueError:
        return None
    return path


def is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and set(value) <= HEX_64


def bundle_digest(rows: list[tuple[str, str, int]]) -> str:
    payload = "".join(f"{path}\0{sha256}\0{size}\n" for path, sha256, size in sorted(rows))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def v2_run_results(
    *,
    case_root: Path,
    evals: Path,
    case_id: str,
    protocol_revision: str,
    entry: dict,
    artifact: dict,
    prompt: dict,
    all_names: set[str],
    hard_names: set[str],
    fixture_manifest_hash: str,
    fixture_manifest: dict,
    seed_hashes: dict[str, str],
    baseline_hash: str,
) -> tuple[list[str], dict[str, bool], float | None]:
    errors: list[str] = []
    key = (
        entry.get("prompt_id"),
        entry.get("runtime"),
        entry.get("repetition"),
        entry.get("configuration"),
    )
    exact = {
        "schema": "boi-local-case-run-artifact/v2",
        "case_id": case_id,
        "protocol_revision": protocol_revision,
        "prompt_id": key[0],
        "runtime": key[1],
        "configuration": key[3],
        "repetition": key[2],
    }
    artifact_schema = load(evals / "run-artifact.schema.json")
    allowed_root = set(artifact_schema.get("properties", {}))
    if set(artifact) != allowed_root:
        unexpected = sorted(set(artifact) - allowed_root)
        missing = sorted(allowed_root - set(artifact))
        errors.append(f"run artifact root property mismatch: {key} unexpected={unexpected} missing={missing}")
    for field, field_schema in artifact_schema.get("properties", {}).items():
        if not isinstance(field_schema, dict) or field_schema.get("additionalProperties") is not False:
            continue
        value = artifact.get(field)
        if isinstance(value, dict):
            allowed = set(field_schema.get("properties", {}))
            if set(value) != allowed:
                unexpected = sorted(set(value) - allowed)
                missing = sorted(allowed - set(value))
                errors.append(
                    f"run artifact {field} property mismatch: {key} unexpected={unexpected} missing={missing}"
                )
    for field, expected in exact.items():
        if artifact.get(field) != expected:
            errors.append(f"run artifact {field} mismatch: {key}")
    for field in ("runtime_version", "model_id", "reasoning_setting", "started_at", "finished_at"):
        if not str(artifact.get(field, "")).strip():
            errors.append(f"run artifact missing {field}: {key}")
    if not isinstance(artifact.get("duration_seconds"), (int, float)) or artifact.get("duration_seconds", 0) <= 0:
        errors.append(f"run artifact invalid duration: {key}")
    environment = artifact.get("execution_environment", {})
    if (
        environment.get("os") != "windows-native"
        or environment.get("runtime_transport") not in {"desktop-app", "windows-cli"}
        or environment.get("workspace_kind") != "isolated-temporary-copy"
        or environment.get("sandbox_mode") != "workspace-write"
        or environment.get("effective_workspace_write") is not True
        or environment.get("unsandboxed_synthetic_pilot") is not False
        or not str(environment.get("os_version", "")).strip()
    ):
        errors.append(f"run artifact is not a Windows-native isolated execution: {key}")
    if not isinstance(artifact.get("workspace_commit"), str) or len(artifact.get("workspace_commit", "")) != 40:
        errors.append(f"run artifact invalid workspace commit: {key}")
    if not str(artifact.get("harness_release", "")).strip() or not is_sha256(artifact.get("harness_checksum")):
        errors.append(f"run artifact missing Harness identity: {key}")
    if artifact.get("fixture_manifest_sha256") != fixture_manifest_hash:
        errors.append(f"run artifact fixture manifest mismatch: {key}")
    expected_seed_hash = seed_hashes.get(str(prompt.get("seed_id", "")))
    if not expected_seed_hash or artifact.get("seed_manifest_sha256") != expected_seed_hash:
        errors.append(f"run artifact seed manifest mismatch: {key}")
    prompt_hash = hashlib.sha256(str(prompt.get("user_prompt", "")).encode("utf-8")).hexdigest()
    if artifact.get("user_prompt_sha256") != prompt_hash:
        errors.append(f"run artifact user prompt mismatch: {key}")
    interaction_bytes = json.dumps(
        prompt.get("interaction", {}), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    interaction_hash = hashlib.sha256(interaction_bytes).hexdigest()
    if artifact.get("interaction_script_sha256") != interaction_hash:
        errors.append(f"run artifact interaction script mismatch: {key}")

    isolation = artifact.get("isolation", {})
    if (
        isolation.get("fresh_workspace") is not True
        or isolation.get("cross_run_files_visible") is not False
        or isolation.get("baseline_contract_sha256") != baseline_hash
        or isolation.get("baseline_exposure_files") != []
    ):
        errors.append(f"run artifact isolation contract failed: {key}")
    tools = artifact.get("tool_evidence", {})
    if tools.get("network_enabled") is not False or not isinstance(tools.get("used"), list):
        errors.append(f"run artifact tool evidence is incomplete: {key}")
    integrity = artifact.get("source_integrity", {})
    selected_rows: list[tuple[str, str, int]] = []
    selectors = [str(item) for item in prompt.get("inputs", [])]
    for item in fixture_manifest.get("files", []):
        path = str(item.get("path", ""))
        if any(fnmatch.fnmatchcase(path, selector) for selector in selectors):
            selected_rows.append((path, str(item.get("sha256", "")), int(item.get("bytes", 0))))
    selected_hash = bundle_digest(selected_rows)
    if (
        integrity.get("before_manifest_sha256") != fixture_manifest_hash
        or integrity.get("after_manifest_sha256") != fixture_manifest_hash
        or integrity.get("selected_input_manifest_sha256_before") != selected_hash
        or integrity.get("selected_input_manifest_sha256_after") != selected_hash
        or integrity.get("selected_input_count") != len(selected_rows)
        or integrity.get("changed_source_files") != []
    ):
        errors.append(f"run artifact source integrity failed: {key}")
    remote = artifact.get("remote_activity", {})
    if any(remote.get(field) != 0 for field in ("mcp_writes", "remote_submits", "boi_remote_source_bytes")):
        errors.append(f"run artifact remote safety failed: {key}")
    context = artifact.get("model_context", {})
    expected_provider = {"codex": "openai", "claude": "anthropic"}.get(str(key[1]))
    selected_input_bytes = sum(row[2] for row in selected_rows)
    if (
        context.get("provider") != expected_provider
        or context.get("runtime") != key[1]
        or context.get("synthetic_evaluation") is not True
        or context.get("selected_input_bytes") != selected_input_bytes
        or context.get("data_classification") != "synthetic"
        or context.get("user_authorized_runtime_processing") is not True
    ):
        errors.append(f"run artifact model-context disclosure failed: {key}")

    output = artifact.get("output_bundle", {})
    bundle_root = resolve_inside(case_root, output.get("path"))
    listed_rows: list[tuple[str, str, int]] = []
    listed_paths: set[str] = set()
    if bundle_root is None or not bundle_root.is_dir():
        errors.append(f"run output bundle missing or outside Case: {key}")
    else:
        for row in output.get("files", []):
            relative = str(row.get("path", ""))
            if relative in listed_paths:
                errors.append(f"duplicate output bundle file: {key} {relative}")
                continue
            listed_paths.add(relative)
            output_file = resolve_inside(bundle_root, relative)
            if output_file is None or not output_file.is_file():
                errors.append(f"missing output bundle file: {key} {relative}")
                continue
            actual_sha = digest(output_file)
            actual_size = output_file.stat().st_size
            if row.get("sha256") != actual_sha or row.get("bytes") != actual_size:
                errors.append(f"output bundle file hash mismatch: {key} {relative}")
            listed_rows.append((relative, actual_sha, actual_size))
        actual_paths = {
            path.relative_to(bundle_root).as_posix() for path in bundle_root.rglob("*") if path.is_file()
        }
        if actual_paths != listed_paths:
            errors.append(f"output bundle manifest is not exact: {key}")
        if output.get("sha256") != bundle_digest(listed_rows):
            errors.append(f"output bundle digest mismatch: {key}")

    result_rows = artifact.get("assertions", {})
    results: dict[str, bool] = {}
    if set(result_rows) != all_names:
        errors.append(f"run artifact assertion set mismatch: {key}")
    for name in all_names:
        row = result_rows.get(name, {})
        if not isinstance(row.get("passed"), bool):
            errors.append(f"run artifact assertion result missing: {key} {name}")
            continue
        if row.get("method") not in {"deterministic", "reviewer"} or not isinstance(row.get("evidence"), list) or not row.get("evidence"):
            errors.append(f"run artifact assertion evidence missing: {key} {name}")
            continue
        if name in hard_names and row.get("method") != "deterministic":
            errors.append(f"hard assertion is not deterministic: {key} {name}")
        results[name] = row["passed"]

    rubric = artifact.get("rubric", {})
    score = rubric.get("score")
    dimensions = rubric.get("dimensions", {})
    if not isinstance(score, (int, float)) or not math.isfinite(score) or not 0 <= score <= 100:
        errors.append(f"invalid run artifact rubric score: {key}")
        score = None
    if not isinstance(dimensions, dict) or len(dimensions) < 7:
        errors.append(f"run artifact rubric dimensions incomplete: {key}")
    else:
        dimension_total = 0.0
        for dimension, row in dimensions.items():
            if not isinstance(row, dict) or not isinstance(row.get("score"), (int, float)) or not isinstance(row.get("max"), (int, float)):
                errors.append(f"invalid rubric dimension: {key} {dimension}")
                continue
            if not 0 <= row["score"] <= row["max"] or not row.get("evidence"):
                errors.append(f"rubric dimension evidence or range invalid: {key} {dimension}")
            dimension_total += float(row["score"])
        if score is not None and not math.isclose(dimension_total, float(score), abs_tol=0.001):
            errors.append(f"rubric score does not equal dimension sum: {key}")

    evaluator = artifact.get("evaluator", {})
    evaluator_path = resolve_inside(case_root, evaluator.get("evidence_path"))
    if (
        evaluator.get("independent_from_runtime") is not True
        or not str(evaluator.get("evaluator_id", "")).strip()
        or not str(evaluator.get("evaluator_version", "")).strip()
        or evaluator_path is None
        or not evaluator_path.is_file()
        or digest(evaluator_path) != evaluator.get("evidence_sha256")
    ):
        errors.append(f"independent evaluator evidence invalid: {key}")
    return errors, results, float(score) if score is not None else None


def expected_keys(plan: dict) -> set[tuple[str, str, int, str]]:
    prompt_ids = [item["prompt_id"] for item in plan["prompts"]]
    return {
        (prompt_id, runtime, repetition, configuration)
        for prompt_id in prompt_ids
        for runtime in RUNTIMES
        for repetition in range(1, int(plan["repetitions"]) + 1)
        for configuration in CONFIGURATIONS
    }


def summarize(case_root: Path) -> dict:
    evals = case_root / "evals"
    case = load(case_root / "case.yaml")
    plan = load(evals / "eval-plan.yaml")
    prompt_catalog = load(evals / "prompts" / "prompt-catalog.json")
    plan = {**plan, "prompts": prompt_catalog.get("prompts", [])}
    prompts_by_id = {item["prompt_id"]: item for item in plan["prompts"]}
    assertions = load(evals / "assertions.json")
    run_index = load(evals / "runs" / "run-index.json")
    comparisons = load(evals / "blind-comparison" / "comparisons.json")
    external_path = evals / "external-evidence.json"
    external = load(external_path) if external_path.exists() else {}

    errors: list[str] = []
    expected = expected_keys(plan)
    seen: set[tuple[str, str, int, str]] = set()
    run_hashes: dict[tuple[str, str, int, str], str] = {}
    objective_results: list[bool] = []
    hard_results: list[bool] = []
    harness_scores: list[float] = []
    hard_names = set(assertions.get("hard", []))
    all_names = hard_names | set(assertions.get("quality", []))
    v2_protocol = plan.get("schema") == "boi-local-case-eval-plan/v2"
    fixture_manifest_path = resolve_from(evals, case_root, plan.get("fixture_manifest")) if v2_protocol else None
    baseline_path = resolve_from(evals, case_root, plan.get("baseline_contract")) if v2_protocol else None
    seed_catalog_path = resolve_from(evals, case_root, plan.get("seed_catalog")) if v2_protocol else None
    fixture_manifest_hash = digest(fixture_manifest_path) if fixture_manifest_path and fixture_manifest_path.is_file() else ""
    fixture_manifest = load(fixture_manifest_path) if fixture_manifest_path and fixture_manifest_path.is_file() else {}
    baseline_hash = digest(baseline_path) if baseline_path and baseline_path.is_file() else ""
    seed_hashes: dict[str, str] = {}
    if seed_catalog_path and seed_catalog_path.is_file():
        for seed in load(seed_catalog_path).get("seeds", []):
            seed_hashes[str(seed.get("seed_id", ""))] = str(seed.get("manifest_sha256", ""))
    if v2_protocol and (not fixture_manifest_hash or not baseline_hash or not seed_hashes):
        errors.append("frozen protocol inputs are missing")

    for entry in run_index.get("runs", []):
        key = (
            entry.get("prompt_id"),
            entry.get("runtime"),
            entry.get("repetition"),
            entry.get("configuration"),
        )
        if key not in expected:
            errors.append(f"unexpected run key: {key}")
        if key in seen:
            errors.append(f"duplicate run key: {key}")
        seen.add(key)
        artifact = (case_root / str(entry.get("artifact", ""))).resolve()
        try:
            artifact.relative_to(case_root.resolve())
        except ValueError:
            errors.append(f"run artifact escapes Case package: {entry.get('artifact')}")
            continue
        if not artifact.is_file():
            errors.append(f"missing run artifact: {entry.get('artifact')}")
            continue
        actual_hash = digest(artifact)
        if actual_hash != entry.get("artifact_sha256"):
            errors.append(f"run artifact hash mismatch: {entry.get('artifact')}")
        run_hashes[key] = actual_hash
        if v2_protocol:
            try:
                artifact_payload = load(artifact)
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"invalid run artifact JSON: {key}: {exc}")
                continue
            artifact_errors, results, score = v2_run_results(
                case_root=case_root,
                evals=evals,
                case_id=str(case.get("case_id", "")),
                protocol_revision=str(plan.get("protocol_revision", "")),
                entry=entry,
                artifact=artifact_payload,
                prompt=prompts_by_id.get(str(entry.get("prompt_id")), {}),
                all_names=all_names,
                hard_names=hard_names,
                fixture_manifest_hash=fixture_manifest_hash,
                fixture_manifest=fixture_manifest,
                seed_hashes=seed_hashes,
                baseline_hash=baseline_hash,
            )
            errors.extend(artifact_errors)
            if set(results) != all_names:
                continue
        else:
            results = entry.get("assertions", {})
            if set(results) != all_names or not all(isinstance(value, bool) for value in results.values()):
                errors.append(f"incomplete assertion results: {key}")
                continue
            score = entry.get("score")
        if entry.get("configuration") == "with-harness":
            # Baseline exists to measure the Harness delta.  Its expected
            # contract failures must not dilute the Harness production safety
            # gate; otherwise a useful baseline makes Reference eligibility
            # mathematically impossible.  Baseline quality is represented by
            # the blinded pairwise comparison below.
            objective_results.extend(results.values())
            hard_results.extend(results[name] for name in hard_names)
            if not isinstance(score, (int, float)) or not math.isfinite(score) or not 0 <= score <= 100:
                errors.append(f"invalid score: {key}")
            else:
                harness_scores.append(float(score))

    comparison_rows = comparisons.get("comparisons", [])
    valid_winners = {"with-harness", "baseline", "tie"}
    expected_comparisons = {(prompt_id, runtime, repetition) for prompt_id, runtime, repetition, _ in expected}
    comparison_keys: set[tuple[str, str, int]] = set()
    for row in comparison_rows:
        comparison_key = (row.get("prompt_id"), row.get("runtime"), row.get("repetition"))
        if comparison_key not in expected_comparisons:
            errors.append(f"unexpected blind comparison key: {comparison_key}")
        if comparison_key in comparison_keys:
            errors.append(f"duplicate blind comparison key: {comparison_key}")
        comparison_keys.add(comparison_key)
        if row.get("winner") not in valid_winners:
            errors.append(f"invalid blind comparison winner: {comparison_key}")
        if not str(row.get("reviewer_id", "")).strip() or row.get("blind_order") not in {"A-B", "B-A"}:
            errors.append(f"blind comparison reviewer or randomized order missing: {comparison_key}")
        prompt_id, runtime, repetition = comparison_key
        if row.get("with_harness_sha256") != run_hashes.get((prompt_id, runtime, repetition, "with-harness")):
            errors.append(f"with-Harness comparison hash mismatch: {comparison_key}")
        if row.get("baseline_sha256") != run_hashes.get((prompt_id, runtime, repetition, "baseline")):
            errors.append(f"baseline comparison hash mismatch: {comparison_key}")
    wins = sum(row.get("winner") == "with-harness" for row in comparison_rows)
    ties = sum(row.get("winner") == "tie" for row in comparison_rows)
    comparison_count = len(comparison_keys)
    complete = seen == expected and len(seen) == int(plan.get("required_executions", 0))
    objective_rate = sum(objective_results) / len(objective_results) if objective_results else None
    hard_rate = sum(hard_results) / len(hard_results) if hard_results else None
    median = statistics.median(harness_scores) if harness_scores else None
    stddev = statistics.pstdev(harness_scores) if len(harness_scores) > 1 else None
    blind_win = wins / comparison_count if comparison_count else None
    blind_win_tie = (wins + ties) / comparison_count if comparison_count else None
    codex = complete and all(key[1] != "codex" or key in seen for key in expected)
    claude = complete and all(key[1] != "claude" or key in seen for key in expected)
    blind_complete = comparison_keys == expected_comparisons
    tester_rows = external.get("testers", [])
    non_developer_acceptance = (
        external.get("non_developer_acceptance") is True
        and isinstance(tester_rows, list)
        and len(tester_rows) >= 2
        and all(row.get("natural_language_only") is True and row.get("success") is True for row in tester_rows)
    )
    validator_artifact = (case_root / str(external.get("boi_validator_artifact", ""))).resolve()
    validator_hash_ok = False
    try:
        validator_artifact.relative_to(case_root.resolve())
        validator_hash_ok = (
            validator_artifact.is_file()
            and hashlib.sha256(validator_artifact.read_bytes()).hexdigest()
            == external.get("boi_validator_sha256")
        )
    except ValueError:
        validator_hash_ok = False
    actual_boi_validator = external.get("actual_boi_validator") is True and validator_hash_ok
    gate = all(
        (
            not errors,
            complete,
            objective_rate is not None and objective_rate >= 0.95,
            hard_rate == 1.0,
            median is not None and median >= 85,
            blind_complete,
            blind_win is not None and blind_win >= 0.70,
            blind_win_tie is not None and blind_win_tie >= 0.90,
            stddev is not None and stddev <= 10,
            codex,
            claude,
            non_developer_acceptance,
            actual_boi_validator,
        )
    )
    return {
        "schema": "boi-local-case-benchmark/v1",
        "case_id": case["case_id"],
        "status": "complete" if complete else "not-run" if not seen else "partial",
        "required_executions": len(expected),
        "completed_executions": len(seen),
        "objective_assertion_pass_rate": objective_rate,
        "hard_safety_pass_rate": hard_rate,
        "median_score": median,
        "blind_win_rate": blind_win,
        "blind_win_or_tie_rate": blind_win_tie,
        "score_stddev": stddev,
        "codex_validated": codex,
        "claude_validated": claude,
        "non_developer_acceptance": non_developer_acceptance,
        "actual_boi_validator": actual_boi_validator,
        "production_quality_gate_passed": gate,
        "reference_eligible": gate,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_root")
    parser.add_argument("--write", action="store_true", help="update evals/benchmark.json with this exact summary")
    args = parser.parse_args()
    case_root = Path(args.case_root).resolve()
    result = summarize(case_root)
    if args.write:
        (case_root / "evals" / "benchmark.json").write_text(
            json.dumps({key: value for key, value in result.items() if key != "errors"}, ensure_ascii=False, indent=2)
            + "\n",
            encoding="utf-8",
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
