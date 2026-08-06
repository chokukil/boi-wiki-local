#!/usr/bin/env python3
"""Aggregate automated and manual evidence for the Windows BoI Wiki Local release gate."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

from release_evidence import validate as validate_release_evidence
from migration_audit import audit as audit_migration


def json_command(root: Path, *args: str) -> dict:
    completed = subprocess.run(
        args,
        cwd=root,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
        env={**os.environ, "PYTHONUTF8": "1"},
    )
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        payload = {"ok": False, "error": (completed.stderr or completed.stdout).strip()[:1000]}
    payload["command_exit_code"] = completed.returncode
    return payload


def origin_check(root: Path, required_pattern: str) -> dict[str, object]:
    completed = subprocess.run(
        ["git", "-C", str(root), "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    raw = completed.stdout.strip()
    credentialed = False
    host = ""
    if "://" in raw:
        parsed = urlsplit(raw)
        scheme = parsed.scheme.lower()
        credentialed = parsed.password is not None or (
            scheme in {"http", "https"} and parsed.username is not None
        )
        host = parsed.hostname or ""
    else:
        host = raw.split(":", 1)[0] if ":" in raw else raw
    matches = not required_pattern or bool(re.search(required_pattern, host, re.IGNORECASE))
    return {
        "ok": completed.returncode == 0 and bool(raw) and not credentialed and matches,
        "host": host,
        "credentialed_url": credentialed,
        "required_pattern": required_pattern,
        "matches_required_pattern": matches,
    }


def migration_check(source: str, target: Path) -> dict[str, object]:
    if not source:
        return {"status": "not_requested", "ok": True}
    try:
        return {"status": "checked", **audit_migration(Path(source), target)}
    except (OSError, ValueError) as exc:
        return {"status": "failed", "ok": False, "error": str(exc)}


def git_head(root: Path) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else ""


def readiness(automated_ready: bool, automated: dict[str, object], manual: dict[str, object]) -> dict[str, bool]:
    user_acceptance_ready = automated_ready and bool(manual.get("ok"))
    generic_ux_qa_ready = bool((automated.get("ux") or {}).get("ok"))
    second_brain_query_quality_ready = bool((automated.get("query_quality") or {}).get("ok"))
    domain_example_validated = bool(manual.get("domain_example_validated"))
    origin_host = str((automated.get("origin") or {}).get("host", ""))
    internal_distribution_origin_ready = "bitbucket" in origin_host.lower()
    agent_driven_setup_ready = automated_ready and generic_ux_qa_ready
    zero_ui_setup_ready = agent_driven_setup_ready and bool(manual.get("zero_ui_setup_validated"))
    adaptive_memory_ready = agent_driven_setup_ready and bool(manual.get("adaptive_memory_validated"))
    agent_auto_check_ready = agent_driven_setup_ready and bool(manual.get("agent_auto_check_validated"))
    folder_autocuration_ready = agent_driven_setup_ready and bool(manual.get("folder_autocuration_validated"))
    case_harness = automated.get("case_harness") or {}
    meta_harness_ready = automated_ready and bool(case_harness.get("ok"))
    case_factory_ready = meta_harness_ready
    cross_runtime_eval_ready = bool(case_harness.get("production_quality_gate_passed"))
    second_brain_case = next(
        (item for item in case_harness.get("cases", []) if item.get("case_id") == "second-brain"),
        {},
    )
    second_brain_reference_ready = (
        cross_runtime_eval_ready
        and second_brain_case.get("status") == "reference"
        and second_brain_case.get("reference_eligible") is True
    )
    production_quality_gate_passed = (
        case_factory_ready and cross_runtime_eval_ready and second_brain_reference_ready
    )
    boi_contract_ready = bool((automated.get("ux") or {}).get("checks", {}).get("actual_boi_contract_checked"))
    non_developer_acceptance_ready = user_acceptance_ready
    release_screen_ready = bool((automated.get("wiki") or {}).get("release_screen_ready"))
    return {
        "core_automated_ready": automated_ready,
        "generic_ux_qa_ready": generic_ux_qa_ready,
        "second_brain_query_quality_ready": second_brain_query_quality_ready,
        "user_acceptance_ready": user_acceptance_ready,
        "release_screen_ready": release_screen_ready,
        "obsidian_support_ready": (
            user_acceptance_ready
            and release_screen_ready
            and bool(manual.get("obsidian_support_claimed"))
        ),
        "domain_example_validated": domain_example_validated,
        "internal_distribution_origin_ready": internal_distribution_origin_ready,
        "agent_driven_setup_ready": agent_driven_setup_ready,
        "zero_ui_setup_ready": zero_ui_setup_ready,
        "adaptive_memory_ready": adaptive_memory_ready,
        "agent_auto_check_ready": agent_auto_check_ready,
        "folder_autocuration_ready": folder_autocuration_ready,
        "meta_harness_ready": meta_harness_ready,
        "second_brain_reference_ready": second_brain_reference_ready,
        "case_factory_ready": case_factory_ready,
        "cross_runtime_eval_ready": cross_runtime_eval_ready,
        "production_quality_gate_passed": production_quality_gate_passed,
        "boi_contract_ready": boi_contract_ready,
        "non_developer_acceptance_ready": non_developer_acceptance_ready,
        "full_release_ready": all(
            (
                user_acceptance_ready,
                internal_distribution_origin_ready,
                zero_ui_setup_ready,
                adaptive_memory_ready,
                agent_auto_check_ready,
                folder_autocuration_ready,
                production_quality_gate_passed,
                boi_contract_ready,
                release_screen_ready,
            )
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--boi-wiki-root", required=True)
    parser.add_argument("--wsl-source", default="")
    parser.add_argument("--origin-host-pattern", default="")
    parser.add_argument("--acceptance-evidence", default="")
    parser.add_argument("--require-manual-evidence", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    python = sys.executable
    harness = json_command(root, python, str(root / "scripts" / "harness_sync.py"), "verify", "--root", str(root))
    harness["ok"] = harness.get("command_exit_code") == 0 and harness.get("status") == "valid"
    privacy_full = json_command(
        root,
        python,
        str(root / "scripts" / "contribution_check.py"),
        "--root",
        str(root),
        "--all",
    )
    privacy = {
        "ok": bool(privacy_full.get("ok")),
        "mode": privacy_full.get("mode"),
        "checked_count": len(privacy_full.get("checked", [])),
        "errors": privacy_full.get("errors", []),
        "command_exit_code": privacy_full.get("command_exit_code"),
    }
    automated = {
        "windows_native_path": {"ok": os.name == "nt" and not str(root).startswith("\\\\wsl$"), "path": str(root)},
        "origin": origin_check(root, args.origin_host_pattern),
        "migration": migration_check(args.wsl_source, root),
        "harness": harness,
        "wiki": json_command(root, python, str(root / "scripts" / "wiki_check.py"), "--root", str(root)),
        "query_quality": json_command(root, python, str(root / "scripts" / "query_quality.py"), "--root", str(root)),
        "privacy": privacy,
        "clean_clone": json_command(
            root,
            python,
            str(root / "scripts" / "release_clone_acceptance.py"),
            "--root",
            str(root),
        ),
        "ux": json_command(
            root,
            python,
            str(root / "scripts" / "ux_acceptance.py"),
            "--root",
            str(root),
            "--boi-wiki-root",
            str(Path(args.boi_wiki_root).resolve()),
        ),
        "plugins": json_command(
            root, python, str(root / "scripts" / "obsidian_plugin_check.py"), "--root", str(root)
        ),
        "case_harness": json_command(
            root, python, str(root / "scripts" / "case_harness_check.py"), "--root", str(root)
        ),
    }
    automated_ready = all(bool(item.get("ok")) for item in automated.values())
    current_head = git_head(root)
    if args.acceptance_evidence:
        try:
            manual = validate_release_evidence(
                json.loads(Path(args.acceptance_evidence).resolve().read_text(encoding="utf-8")),
                expected_build_commit=current_head,
            )
        except (OSError, json.JSONDecodeError) as exc:
            manual = {"ok": False, "errors": [str(exc)], "obsidian_support_claimed": False}
    else:
        manual = {
            "ok": False,
            "status": "missing",
            "obsidian_support_claimed": False,
            "domain_example_validated": False,
            "errors": ["two non-developer Windows journeys and an independent knowledge-steward review are required"],
            "next_step": "pilot-acceptance.cmd preflight -> start -> review -> validate (store evidence outside the repository); use-case-review is optional when a packaged domain Case is in release scope",
        }
    release_status = readiness(automated_ready, automated, manual)
    payload = {
        "schema": "boi-local-release-gate/v1",
        "automated_release_ready": automated_ready,
        **release_status,
        "release_checkout_head": current_head,
        "automated": automated,
        "manual_acceptance": manual,
        "remote_submit_capability_included": False,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if not automated_ready:
        return 1
    if args.require_manual_evidence and not release_status["full_release_ready"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
