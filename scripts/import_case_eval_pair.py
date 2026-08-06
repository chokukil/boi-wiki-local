#!/usr/bin/env python3
"""Import one independently reviewed A/B execution pair as auditable evidence.

This is a maintainer/CI utility, not an employee runtime dependency.  It copies
only synthetic user-facing outputs and validated evaluation evidence into the
Case package; raw model transcripts and temporary workspaces stay external.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
from pathlib import Path

from case_run_assertions import evaluate


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def bundle_digest(rows: list[dict]) -> str:
    payload = "".join(
        f"{row['path']}\0{row['sha256']}\0{row['bytes']}\n"
        for row in sorted(rows, key=lambda item: item["path"])
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def copy_tree(source: Path, destination: Path) -> list[dict]:
    rows: list[dict] = []
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        rows.append({"path": relative.as_posix(), "sha256": digest(target), "bytes": target.stat().st_size})
    return rows


def copy_input_tree(source: Path, destination: Path, generated_paths: set[str]) -> list[dict]:
    """Keep provenance inputs resolvable and namespace only before/after collisions."""
    rows: list[dict] = []
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        target_relative = relative
        if relative.as_posix() in generated_paths:
            target_relative = Path("_input-before") / relative
        target = destination / target_relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        rows.append({
            "path": target_relative.as_posix(),
            "sha256": digest(target),
            "bytes": target.stat().st_size,
        })
    return rows


def validated_review(blind_root: Path, rubric: dict, mappings: dict) -> dict:
    result_path = blind_root / "control" / "review-result.json"
    result = load(result_path)
    if result.get("schema") != "boi-local-blind-review-result/v1" or result.get("winner") not in {"A", "B", "tie"}:
        raise ValueError("invalid blind review result")
    maximums = {row["id"]: row["points"] for row in rubric["dimensions"]}
    capped: dict[str, int | float] = {}
    for label in ("A", "B"):
        dimensions = result.get("scores", {}).get(label, {}).get("dimensions", {})
        if set(dimensions) != set(maximums):
            raise ValueError(f"blind review dimensions mismatch: {label}")
        raw_total = 0
        for key, score in dimensions.items():
            if not isinstance(score, (int, float)) or not 0 <= score <= maximums[key]:
                raise ValueError(f"invalid blind score: {label} {key}")
            raw_total += score
        hard = result.get("hard_failures", {}).get(label, [])
        expected = rubric["hard_failure_score_cap"] if hard else raw_total
        if result["scores"][label].get("total") != expected:
            raise ValueError(f"blind review total/cap mismatch: {label}")
        capped[label] = expected
    expected_winner = "tie" if capped["A"] == capped["B"] else max(capped, key=capped.get)
    if result["winner"] != expected_winner:
        raise ValueError("blind review winner does not match validated capped totals")
    result["validated_capped_totals"] = capped
    result["review_result_sha256"] = digest(result_path)
    result["mapping_capture_sha256"] = mappings["capture_sha256"]
    return result


def assertions_for(oracle: dict, assertion_contract: dict, prompt_id: str) -> dict:
    required_for_prompt = set(assertion_contract["per_prompt"].get(prompt_id, []))
    result: dict[str, dict] = {}
    all_names = assertion_contract["hard"] + assertion_contract["quality"]
    for name in all_names:
        if name in oracle["assertions"]:
            result[name] = oracle["assertions"][name]
        elif name not in required_for_prompt:
            result[name] = {
                "passed": True,
                "method": "reviewer",
                "evidence": [f"not applicable to {prompt_id} under the frozen per_prompt assertion matrix"],
            }
        else:
            result[name] = {
                "passed": False,
                "method": "reviewer",
                "evidence": [f"required {prompt_id} assertion has no independent evidence"],
            }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--with-run", required=True, type=Path)
    parser.add_argument("--baseline-run", required=True, type=Path)
    parser.add_argument("--blind-root", required=True, type=Path)
    parser.add_argument("--case-root", type=Path, default=Path("cases/flagship/second-brain"))
    parser.add_argument("--replace", action="store_true", help="replace this exact prompt/runtime/repetition evidence pair")
    args = parser.parse_args()

    case_root = args.case_root.resolve()
    runs = {"with-harness": args.with_run.resolve(), "baseline": args.baseline_run.resolve()}
    captures = {name: load(run / "control" / "execution-capture.json") for name, run in runs.items()}
    oracles = {name: evaluate(run) for name, run in runs.items()}
    for name, capture in captures.items():
        if capture.get("configuration") != name:
            raise ValueError(f"configuration mismatch: {name}")
        if digest(runs[name] / "control" / "execution-capture.json") != oracles[name]["capture_sha256"]:
            raise ValueError(f"oracle/capture mismatch: {name}")
        effective = capture.get("effective_sandbox", {})
        if not (
            capture.get("configured_sandbox_mode") == "workspace-write"
            and effective.get("sandbox_type") == "workspace-write"
            and effective.get("workspace_write") is True
            and effective.get("permission_network") == "restricted"
            and capture.get("unsandboxed_synthetic_pilot") is False
        ):
            raise ValueError(f"restricted workspace-write evidence missing: {name}")

    mapping = load(args.blind_root / "control" / "private-mapping.json")
    label_for = {configuration: label for label, configuration in (("A", mapping["A"]), ("B", mapping["B"]))}
    for configuration, label in label_for.items():
        actual = digest(runs[configuration] / "control" / "execution-capture.json")
        if mapping["capture_sha256"][label] != actual:
            raise ValueError(f"blind mapping capture mismatch: {configuration}")
    rubric_contract = load(case_root / "evals" / "rubric.json")
    review = validated_review(args.blind_root, rubric_contract, mapping)
    assertion_contract = load(case_root / "evals" / "assertions.json")
    harness = load(case_root.parents[2] / "harness.lock")
    prompt_id = captures["with-harness"]["prompt_id"]
    runtime = captures["with-harness"]["runtime"]
    repetition = captures["with-harness"]["repetition"]
    evidence_rel = Path("evals") / "blind-comparison" / "evidence" / f"{prompt_id}-{runtime}-r{repetition}.json"
    evidence_path = case_root / evidence_rel
    evidence = {
        "schema": "boi-local-independent-evaluator-evidence/v1",
        "reviewer_id": f"{runtime}-blind-{captures['with-harness']['model_id']}",
        "reviewer_runtime_version": captures["with-harness"]["runtime_version"],
        "independent_session": True,
        "blind_order": f"{mapping['A']}-then-{mapping['B']}",
        "reviewer_bundle_sha256": mapping["reviewer_bundle_sha256"],
        "result": review,
    }
    write(evidence_path, evidence)
    evaluator_hash = digest(evidence_path)

    artifacts: dict[str, Path] = {}
    for configuration in ("with-harness", "baseline"):
        capture = captures[configuration]
        label = label_for[configuration]
        destination_root = case_root / "evals" / "runs" / runtime / prompt_id / f"r{repetition}" / configuration
        if destination_root.exists():
            expected_parent = case_root / "evals" / "runs" / runtime / prompt_id / f"r{repetition}"
            if not args.replace or destination_root.parent.resolve() != expected_parent.resolve():
                raise FileExistsError(destination_root)
            shutil.rmtree(destination_root)
        output_root = destination_root / "output"
        output_rows = copy_tree(args.blind_root / "reviewer-bundle" / label, output_root)
        existing_paths = {row["path"] for row in output_rows}
        # Preserve the selected synthetic inputs inside the evidence bundle so
        # unchanged relative provenance links remain resolvable after the
        # external temporary workspace is gone.  These bytes are copied
        # identically from the reviewer-visible INPUT tree, never regenerated.
        input_rows = copy_input_tree(
            args.blind_root / "reviewer-bundle" / "INPUT",
            output_root,
            existing_paths,
        )
        output_rows.extend(input_rows)
        oracle_path = destination_root / "deterministic-evaluation.json"
        write(oracle_path, oracles[configuration])
        hard_failures = review["hard_failures"][label]
        raw_dimensions = review["scores"][label]["dimensions"]
        capped = review["validated_capped_totals"][label]
        dimension_rows = {}
        for row in rubric_contract["dimensions"]:
            score = 0 if hard_failures else raw_dimensions[row["id"]]
            evidence_text = (
                f"hard failure cap applied; reviewer pre-cap score {raw_dimensions[row['id']]}/{row['points']}"
                if hard_failures
                else f"independent blind reviewer score {score}/{row['points']}"
            )
            dimension_rows[row["id"]] = {"score": score, "max": row["points"], "evidence": [evidence_text]}
        baseline_contract = case_root / "evals" / "baseline.md"
        artifact = {
            "schema": "boi-local-case-run-artifact/v2",
            "case_id": capture["case_id"],
            "protocol_revision": capture["protocol_revision"],
            "prompt_id": prompt_id,
            "runtime": runtime,
            "runtime_version": capture["runtime_version"],
            "model_id": capture["model_id"],
            "reasoning_setting": capture["reasoning_setting"],
            "configuration": configuration,
            "repetition": repetition,
            "started_at": capture["started_at"],
            "finished_at": capture["finished_at"],
            "duration_seconds": capture["duration_seconds"],
            "execution_environment": {
                "os": "windows-native",
                "os_version": platform.version() or "Windows",
                "runtime_transport": "windows-cli",
                "workspace_kind": "isolated-temporary-copy",
                "sandbox_mode": capture["effective_sandbox"]["sandbox_type"],
                "effective_workspace_write": capture["effective_sandbox"]["workspace_write"],
                "unsandboxed_synthetic_pilot": capture["unsandboxed_synthetic_pilot"],
            },
            "workspace_commit": capture["workspace_commit"],
            "harness_release": harness["release"],
            "harness_checksum": harness["checksum"],
            "fixture_manifest_sha256": capture["fixture_manifest_sha256"],
            "seed_manifest_sha256": capture["seed_manifest_sha256"],
            "user_prompt_sha256": capture["user_prompt_sha256"],
            "interaction_script_sha256": capture["interaction_script_sha256"],
            "runtime_envelope_sha256": capture["runtime_envelope_sha256"],
            "evaluated_interaction_sha256": capture["evaluated_interaction_sha256"],
            "runtime_policy_sha256": capture["runtime_policy_sha256"],
            "isolation": {
                "fresh_workspace": True,
                "cross_run_files_visible": False,
                "baseline_contract_sha256": digest(baseline_contract),
                "baseline_exposure_files": [],
            },
            "tool_evidence": {
                "allowed": ["read", "search", "workspace-scoped file change"],
                "used": ["command_execution", "file_change"],
                "network_enabled": False,
            },
            "source_integrity": {
                "before_manifest_sha256": capture["fixture_manifest_sha256"],
                "after_manifest_sha256": capture["fixture_manifest_sha256"],
                "selected_input_manifest_sha256_before": capture["selected_input_manifest_sha256_before"],
                "selected_input_manifest_sha256_after": capture["selected_input_manifest_sha256_after"],
                "selected_input_count": capture["selected_input_count"],
                "changed_source_files": capture["changed_source_files"],
            },
            "output_bundle": {
                "path": output_root.relative_to(case_root).as_posix(),
                "sha256": bundle_digest(output_rows),
                "files": output_rows,
            },
            "remote_activity": {
                "mcp_writes": capture["boi_remote_activity"]["mcp_writes"],
                "remote_submits": capture["boi_remote_activity"]["remote_submits"],
                "boi_remote_source_bytes": capture["boi_remote_activity"]["boi_remote_source_bytes"],
            },
            "model_context": capture["model_context"],
            "assertions": assertions_for(oracles[configuration], assertion_contract, prompt_id),
            "rubric": {"score": capped, "dimensions": dimension_rows},
            "evaluator": {
                "evaluator_id": evidence["reviewer_id"],
                "evaluator_version": captures["with-harness"]["runtime_version"],
                "independent_from_runtime": True,
                "evidence_path": evidence_rel.as_posix(),
                "evidence_sha256": evaluator_hash,
            },
        }
        artifact_path = destination_root / "artifact.json"
        write(artifact_path, artifact)
        artifacts[configuration] = artifact_path

    run_index_path = case_root / "evals" / "runs" / "run-index.json"
    run_index = load(run_index_path)
    if args.replace:
        run_index["runs"] = [
            row for row in run_index["runs"]
            if not (
                row.get("prompt_id") == prompt_id
                and row.get("runtime") == runtime
                and row.get("repetition") == repetition
            )
        ]
    for configuration, artifact_path in artifacts.items():
        run_index["runs"].append(
            {
                "prompt_id": prompt_id,
                "runtime": runtime,
                "repetition": repetition,
                "configuration": configuration,
                "artifact": artifact_path.relative_to(case_root).as_posix(),
                "artifact_sha256": digest(artifact_path),
            }
        )
    run_index["runs"].sort(key=lambda row: (row["prompt_id"], row["runtime"], row["repetition"], row["configuration"]))
    write(run_index_path, run_index)

    comparisons_path = case_root / "evals" / "blind-comparison" / "comparisons.json"
    comparisons = load(comparisons_path)
    if args.replace:
        comparisons["comparisons"] = [
            row for row in comparisons["comparisons"]
            if not (
                row.get("prompt_id") == prompt_id
                and row.get("runtime") == runtime
                and row.get("repetition") == repetition
            )
        ]
    winner = "tie" if review["winner"] == "tie" else mapping[review["winner"]]
    comparisons["comparisons"].append(
        {
            "prompt_id": prompt_id,
            "runtime": runtime,
            "repetition": repetition,
            "winner": winner,
            "reviewer_id": evidence["reviewer_id"],
            "blind_order": "A-B",
            "with_harness_sha256": digest(artifacts["with-harness"]),
            "baseline_sha256": digest(artifacts["baseline"]),
            "evidence_path": evidence_rel.as_posix(),
            "evidence_sha256": evaluator_hash,
        }
    )
    write(comparisons_path, comparisons)
    print(json.dumps({"imported": True, "prompt_id": prompt_id, "runtime": runtime, "runs": 2, "winner": winner}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
