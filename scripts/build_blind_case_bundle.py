#!/usr/bin/env python3
"""Build an identity-free A/B bundle from two isolated Case Harness runs.

This is an administrator/CI utility.  It never runs a model and never changes
either source workspace.  The private A/B mapping is written outside the
reviewer-visible bundle.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


SCHEMA = "boi-local-blind-bundle/v1"
EXCLUDED_PREFIXES = (
    ".agents/",
    ".claude/",
    ".boi-harness/",
    ".codex/",
    "sources/",
    "templates/",
)
EXCLUDED_FILES = {"AGENTS.md", "CLAUDE.md", "harness.lock"}
MATCH_FIELDS = (
    "case_id",
    "protocol_revision",
    "prompt_id",
    "runtime",
    "runtime_version",
    "runtime_sha256",
    "model_id",
    "reasoning_setting",
    "repetition",
    "fixture_manifest_sha256",
    "seed_manifest_sha256",
    "user_prompt_sha256",
    "interaction_script_sha256",
    "runtime_envelope_sha256",
    "evaluated_interaction_sha256",
    "runtime_policy_sha256",
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def changed_files(workspace: Path) -> list[Path]:
    completed = subprocess.run(
        ["git", "-C", str(workspace), "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        check=True,
        capture_output=True,
    )
    rows = completed.stdout.decode("utf-8", errors="strict").split("\0")
    result: list[Path] = []
    for row in rows:
        if not row:
            continue
        relative = row[3:].replace("\\", "/")
        if relative in EXCLUDED_FILES or relative.startswith(EXCLUDED_PREFIXES):
            continue
        path = workspace / relative
        if path.is_file():
            result.append(path)
    return sorted(result, key=lambda item: item.relative_to(workspace).as_posix())


def copy_outputs(run_dir: Path, target: Path) -> list[dict]:
    workspace = run_dir / "workspace"
    target.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    for source in changed_files(workspace):
        relative = source.relative_to(workspace)
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        rows.append({"path": relative.as_posix(), "sha256": sha256(source), "bytes": source.stat().st_size})
    completion_messages = sorted((run_dir / "control").glob("turn-*-last-message.txt"))
    if not completion_messages:
        raise ValueError(f"run has no captured completion message: {run_dir}")
    completion = target / "COMPLETION_SUMMARY.txt"
    shutil.copy2(completion_messages[-1], completion)
    rows.append({"path": completion.name, "sha256": sha256(completion), "bytes": completion.stat().st_size})
    return rows


def copy_seed_inputs(case_root: Path, prompt: dict, reviewer: Path, expected_manifest_sha256: str) -> list[dict]:
    seed_catalog = load(case_root / "evals" / "seeds" / "seed-catalog.json")
    seed = next(row for row in seed_catalog["seeds"] if row["seed_id"] == prompt["seed_id"])
    manifest_path = case_root / "evals" / "seeds" / seed["manifest"]
    if sha256(manifest_path) != expected_manifest_sha256 or seed["manifest_sha256"] != expected_manifest_sha256:
        raise ValueError("seed manifest does not match the isolated execution capture")
    manifest = load(manifest_path)
    seed_root = manifest_path.parent
    rows: list[dict] = []
    for row in manifest["files"]:
        source = seed_root / row["path"]
        if sha256(source) != row["sha256"] or source.stat().st_size != row["bytes"]:
            raise ValueError(f"seed input integrity mismatch: {row['path']}")
        visible_path = Path("data") / "boi" / "private" / "0000000" / row["path"]
        destination = reviewer / "INPUT" / visible_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        rows.append({"kind": "existing-local-wiki", "path": visible_path.as_posix(), "sha256": row["sha256"], "bytes": row["bytes"]})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_one", type=Path)
    parser.add_argument("run_two", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--case-root", type=Path, default=Path("cases/flagship/second-brain"))
    args = parser.parse_args()

    runs = [args.run_one.resolve(), args.run_two.resolve()]
    captures = [load(run / "control" / "execution-capture.json") for run in runs]
    if {capture.get("configuration") for capture in captures} != {"with-harness", "baseline"}:
        raise ValueError("blind comparison requires one with-harness and one baseline run")
    for field in MATCH_FIELDS:
        if captures[0].get(field) != captures[1].get(field):
            raise ValueError(f"comparison field mismatch: {field}")
    for capture in captures:
        effective = capture.get("effective_sandbox", {})
        if not (
            capture.get("configured_sandbox_mode") == "workspace-write"
            and effective.get("sandbox_type") == "workspace-write"
            and effective.get("workspace_write") is True
            and effective.get("permission_network") == "restricted"
            and capture.get("unsandboxed_synthetic_pilot") is False
        ):
            raise ValueError("comparison run lacks restricted workspace-write evidence")

    capture_hashes = [sha256(run / "control" / "execution-capture.json") for run in runs]
    order_seed = hashlib.sha256("".join(sorted(capture_hashes)).encode()).digest()[0]
    ordered = [0, 1] if order_seed % 2 == 0 else [1, 0]
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    reviewer = output / "reviewer-bundle"
    control = output / "control"
    reviewer.mkdir(parents=True)
    control.mkdir(parents=True)

    labels = {"A": ordered[0], "B": ordered[1]}
    output_rows = {label: copy_outputs(runs[index], reviewer / label) for label, index in labels.items()}
    case_root = args.case_root.resolve()
    shutil.copy2(case_root / "evals" / "rubric.json", reviewer / "rubric.json")
    prompt_catalog = load(case_root / "evals" / "prompts" / "prompt-catalog.json")
    prompt = next(row for row in prompt_catalog["prompts"] if row["prompt_id"] == captures[0]["prompt_id"])
    fixture_manifest = load(case_root / "fixtures" / "manifest.json")
    selected = []
    for row in fixture_manifest["files"]:
        if any(Path(row["path"]).match(selector) for selector in prompt["inputs"]):
            source = case_root / "fixtures" / row["path"]
            destination = reviewer / "INPUT" / row["path"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            selected.append({"kind": "selected-source", **row})
    selected.extend(copy_seed_inputs(case_root, prompt, reviewer, captures[0]["seed_manifest_sha256"]))
    (reviewer / "USER_REQUEST.txt").write_text(prompt["user_prompt"] + "\n", encoding="utf-8")
    profile_contract = """# Reviewer-visible Local Profile contract

Every created Profile Markdown artifact must include the literal fields `okf_version: 0.1`,
`boi_profile_version: 0.1-local`, `visibility: local-private`, `local_only: true`,
`promotion_status: local_only`, `archive_status: active`, `artifact_visibility`,
`lifecycle_state`, `review_after`, and `contains_sensitive`.

Allowed `lifecycle_state` values are `working`, `memory`, `background`, `archived`,
`delete_candidate`, and `protected`. Allowed `claim_status` values are `observed`,
`inferred`, `direct`, `conflicted`, `decision`, `open-question`, and `superseded`;
`mixed` is invalid. Allowed `knowledge_role` values are `agent-memory`, `case-hub`,
`evidence-sidecar`, `hypothesis`, `continuous-log`, `signal-summary`, `comparison`,
`cohort-comparison`, `commonality`, `timeline`, `decision-record`,
`recurrence-fingerprint`, `saved-query`, and `source-record`.

For an approved source-folder resume, each new readable source must have exactly one
immediately useful Profile artifact with an exact 64-character `evidence_sha256`, one of
`email`, `web-clip`, `tabular-data`, `document`, `image`, `meeting-note`, or
`analysis-export` as `evidence_type`, and hash-bound structured `source_refs` and
`generated_from`. A metadata wrapper that only promises later distillation is not useful.
Missing or invalid required Profile metadata is a schema hard failure.
"""
    contract_path = reviewer / "PROFILE_CONTRACT.md"
    contract_path.write_text(profile_contract, encoding="utf-8")
    selected.append({
        "kind": "evaluation-contract",
        "path": "PROFILE_CONTRACT.md",
        "sha256": sha256(contract_path),
        "bytes": contract_path.stat().st_size,
    })
    review_prompt = """You are the independent blind quality reviewer for a synthetic BoI Wiki Local case evaluation.

Read USER_REQUEST.txt, PROFILE_CONTRACT.md, INPUT/, rubric.json, and every user-facing file under A/ and B/. The labels are randomized. Do not guess which system produced either output. Score each rubric dimension up to its declared points. Missing or invalid required OKF/BoI metadata on a created Profile artifact, unsafe promotion boundary, source mutation claim without evidence, or invented fact is a hard failure. A read-only query may correctly create no Profile artifact; in that case verify its claims against the existing Local Wiki and selected sources under INPUT/. Prefer evidence in the files over polished prose.

Return ONLY one JSON object with this exact shape:
{"schema":"boi-local-blind-review-result/v1","winner":"A|B|tie","scores":{"A":{"dimensions":{"schema-and-structure":0,"source-and-provenance":0,"knowledge-maintenance":0,"grounded-reasoning":0,"review-and-failure-path":0,"promotion-boundary":0,"non-developer-ux":0},"total":0},"B":{"dimensions":{"schema-and-structure":0,"source-and-provenance":0,"knowledge-maintenance":0,"grounded-reasoning":0,"review-and-failure-path":0,"promotion-boundary":0,"non-developer-ux":0},"total":0}},"hard_failures":{"A":[],"B":[]},"evidence":{"A":[],"B":[]},"rationale":"..."}
"""
    (reviewer / "REVIEW_PROMPT.md").write_text(review_prompt, encoding="utf-8")

    visible_manifest = {
        "schema": SCHEMA,
        "case_id": captures[0]["case_id"],
        "prompt_id": captures[0]["prompt_id"],
        "runtime": captures[0]["runtime"],
        "repetition": captures[0]["repetition"],
        "labels": {label: rows for label, rows in output_rows.items()},
        "inputs": selected,
    }
    write_json(reviewer / "bundle-manifest.json", visible_manifest)
    mapping = {
        "schema": "boi-local-blind-mapping/v1",
        "A": captures[labels["A"]]["configuration"],
        "B": captures[labels["B"]]["configuration"],
        "run_dirs": {label: str(runs[index]) for label, index in labels.items()},
        "capture_sha256": {label: capture_hashes[index] for label, index in labels.items()},
        "reviewer_bundle_sha256": hashlib.sha256(
            json.dumps(visible_manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    }
    write_json(control / "private-mapping.json", mapping)
    print(json.dumps({"reviewer_bundle": str(reviewer), "control": str(control), "labels_hidden": True}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
