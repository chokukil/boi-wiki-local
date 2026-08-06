#!/usr/bin/env python3
"""Run a disposable, no-telemetry beginner journey and print only its result."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SYNTHETIC_EMPLOYEE_ID = "7654321"


def command(
    script_root: Path,
    workspace: Path,
    script: str,
    *args: str,
    expected: tuple[int, ...] = (0,),
    inject_root: bool = True,
) -> dict:
    command_args = [sys.executable, str(script_root / script)]
    if inject_root:
        command_args.extend(["--root", str(workspace)])
    command_args.extend(args)
    completed = subprocess.run(
        command_args,
        cwd=workspace,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        env={**os.environ, "PYTHONUTF8": "1"},
        check=False,
    )
    if completed.returncode not in expected:
        raise RuntimeError(f"{script} failed ({completed.returncode}): {(completed.stderr or completed.stdout).strip()[:1000]}")
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"{script} returned invalid JSON") from exc


def prepare(source: Path, target: Path) -> None:
    (target / "data" / "boi").mkdir(parents=True)
    (target / "data" / "boi" / "log.md").write_text("# Disposable acceptance log\n", encoding="utf-8")
    for name in ("templates", ".boi-harness"):
        shutil.copytree(source / name, target / name)
    shutil.copytree(
        source / "cases" / "flagship" / "second-brain" / "fixtures",
        target / "cases" / "flagship" / "second-brain" / "fixtures",
    )
    for name in ("harness.lock", "AGENTS.md", "CLAUDE.md", ".env.example"):
        shutil.copy2(source / name, target / name)


def run_journey(source: Path, boi_wiki_root: str) -> dict[str, object]:
    started = time.monotonic()
    scripts = source / "scripts"
    with tempfile.TemporaryDirectory(prefix="boi-ux-acceptance-") as temporary:
        workspace = Path(temporary)
        prepare(source, workspace)
        harness = command(scripts, workspace, "harness_sync.py", "verify")
        preview = command(scripts, workspace, "boi_setup.py", "preview", "--employee-id", SYNTHETIC_EMPLOYEE_ID)
        setup = command(scripts, workspace, "boi_setup.py", "apply", "--employee-id", SYNTHETIC_EMPLOYEE_ID)
        verify = command(scripts, workspace, "boi_setup.py", "verify", "--employee-id", SYNTHETIC_EMPLOYEE_ID)
        case = command(
            scripts,
            workspace,
            "local_case.py",
            "--employee-id", SYNTHETIC_EMPLOYEE_ID,
            "create",
            "--case-id", "SYN-INV-UX-001",
            "--title", "합성 업무 변경 조사 여정",
            "--question", "검토 일정 결정과 새 확인 근거를 어떻게 구분할 것인가?",
        )
        evidence_source = workspace / "cases" / "flagship" / "second-brain" / "fixtures" / "sources" / "02-project-update.eml"
        evidence_before = evidence_source.read_bytes()
        intake = command(
            scripts,
            workspace,
            "local_intake.py",
            "--employee-id", SYNTHETIC_EMPLOYEE_ID,
            "--case-id", "SYN-INV-UX-001",
            "--source", str(evidence_source),
            "--source-ref", "synthetic-fixture",
        )
        command(
            scripts,
            workspace,
            "local_case.py",
            "--employee-id", SYNTHETIC_EMPLOYEE_ID,
            "hypothesis",
            "--case-id", "SYN-INV-UX-001",
            "--hypothesis-id", "H1",
            "--statement", "새 메일이 기존 검토 일정을 재확인한다",
            "--status", "open",
            "--supports", str(intake["evidence_id"]),
        )
        case_review = command(
            scripts,
            workspace,
            "local_case.py",
            "--employee-id", SYNTHETIC_EMPLOYEE_ID,
            "review",
            "--case-id", "SYN-INV-UX-001",
        )
        captured = command(
            scripts,
            workspace,
            "local_capture.py",
            "--employee-id",
            SYNTHETIC_EMPLOYEE_ID,
            "--title",
            "첫 회의 메모",
            "--body",
            "결정 근거는 https://example.com/boi-ux-fixture 에서 확인한다.",
        )
        capture_path = workspace / str(captured["path"])
        capture_before = capture_path.read_bytes()
        distilled = command(
            scripts,
            workspace,
            "local_distill.py",
            "--employee-id",
            SYNTHETIC_EMPLOYEE_ID,
            "--source",
            str(captured["path"]),
            "--title",
            "재사용 가능한 회의 결정",
            "--body",
            "결정: 같은 검증 절차를 반복한다. 근거: https://example.com/boi-ux-fixture",
            "--contains-sensitive",
            "false",
        )
        search = command(
            scripts,
            workspace,
            "local_search.py",
            "--employee-id",
            SYNTHETIC_EMPLOYEE_ID,
            "--json",
            "회의 결정",
        )
        review = command(scripts, workspace, "local_review.py", "--employee-id", SYNTHETIC_EMPLOYEE_ID, "--check")
        lint = command(scripts, workspace, "local_lint.py", "--employee-id", SYNTHETIC_EMPLOYEE_ID)
        promotion = command(
            scripts,
            workspace,
            "promotion_preflight.py",
            "--employee-id",
            SYNTHETIC_EMPLOYEE_ID,
            "--source",
            str(distilled["path"]),
            "--visibility",
            "team",
            "--team-id",
            "synthetic-team",
            "--reviewer",
            "synthetic-reviewer",
            "--sanitized-description",
            "검토된 회의 결정과 공개 가능한 근거",
            "--source-ref",
            "url=https://example.com/boi-ux-fixture",
            "--promotion-reason",
            "Disposable UX acceptance",
        )
        compatibility_args = [
            "--projection",
            str(workspace / str(promotion["remote_projection_path"])),
            "--local-root",
            str(workspace),
        ]
        if boi_wiki_root:
            compatibility_args.extend(["--boi-wiki-root", boi_wiki_root])
        compatibility = command(scripts, workspace, "boi_compatibility.py", *compatibility_args, inject_root=False)
        obsidian = command(
            scripts,
            workspace,
            "boi_setup.py",
            "obsidian-preview",
            "--employee-id",
            SYNTHETIC_EMPLOYEE_ID,
            "--obsidian-host",
            "windows",
        )
        guide_root = workspace / "data" / "boi" / "private" / SYNTHETIC_EMPLOYEE_ID / "notes" / "guide"
        remote_projection = json.loads((workspace / str(promotion["remote_projection_path"])).read_text(encoding="utf-8"))
        serialized_projection = json.dumps(remote_projection, ensure_ascii=False)
        checks = {
            "preview_before_apply": bool(preview.get("create")),
            "existing_files_overwritten": bool(setup.get("overwritten")),
            "setup_verified": bool(verify.get("ok")),
            "wiki_page_count": len(list(guide_root.rglob("*.md"))),
            "case_created": bool(case.get("ok")),
            "evidence_intake_ok": bool(intake.get("ok")),
            "evidence_source_immutable": evidence_source.read_bytes() == evidence_before,
            "case_review_ok": bool(case_review.get("ok")),
            "capture_immutable": capture_path.read_bytes() == capture_before,
            "search_result_count": int(search.get("count", 0)),
            "review_ok": bool(review.get("check_ok")),
            "lint_ok": bool(lint.get("ok")),
            "promotion_ready": bool(promotion.get("ok")),
            "remote_submitted": bool(promotion.get("remote_submitted")),
            "compatibility_ok": bool(compatibility.get("ok")),
            "actual_boi_contract_checked": compatibility.get("boi_wiki_contract", {}).get("status") == "checked",
            "obsidian_optional": obsidian.get("installs_obsidian_app") is False and obsidian.get("installs_community_plugins") is False,
            "employee_id_leaked_to_projection": SYNTHETIC_EMPLOYEE_ID in serialized_projection,
            "local_path_leaked_to_projection": "data/boi/private" in serialized_projection,
            "harness_network_accessed": bool(harness.get("network_accessed")),
        }
        ok = (
            checks["preview_before_apply"]
            and not checks["existing_files_overwritten"]
            and checks["setup_verified"]
            and checks["wiki_page_count"] >= 39
            and checks["case_created"]
            and checks["evidence_intake_ok"]
            and checks["evidence_source_immutable"]
            and checks["case_review_ok"]
            and checks["capture_immutable"]
            and checks["search_result_count"] >= 1
            and checks["review_ok"]
            and checks["lint_ok"]
            and checks["promotion_ready"]
            and not checks["remote_submitted"]
            and checks["compatibility_ok"]
            and (not boi_wiki_root or checks["actual_boi_contract_checked"])
            and checks["obsidian_optional"]
            and not checks["employee_id_leaked_to_projection"]
            and not checks["local_path_leaked_to_projection"]
            and not checks["harness_network_accessed"]
        )
        return {
            "ok": ok,
            "schema": "boi-local-ux-acceptance/v1",
            "duration_seconds": round(time.monotonic() - started, 3),
            "checks": checks,
            "persistent_usage_log_created": False,
            "mcp_invocations": 0,
            "remote_mutations": 0,
            "temporary_workspace_removed_on_exit": True,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--boi-wiki-root", default=os.getenv("BOI_WIKI_ROOT", ""))
    args = parser.parse_args()
    try:
        payload = run_journey(Path(args.root).resolve(), args.boi_wiki_root)
    except Exception as exc:
        payload = {"ok": False, "schema": "boi-local-ux-acceptance/v1", "error": str(exc)}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
