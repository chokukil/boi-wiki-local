#!/usr/bin/env python3
"""Create generic two-user Windows acceptance and optional use-case review evidence."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import sys

from release_evidence import identity_findings, validate
from release_gate import origin_check


def git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode:
        raise ValueError((completed.stderr or completed.stdout).strip() or f"git {' '.join(args)} failed")
    return completed.stdout.strip()


def checkout_context(root: Path, origin_host_pattern: str) -> dict[str, str]:
    root = root.resolve()
    if os.name != "nt" or str(root).lower().startswith(("\\\\wsl$", "\\\\wsl.localhost")):
        raise ValueError("pilot acceptance must run from a Windows-native checkout")
    origin = origin_check(root, origin_host_pattern)
    if not origin.get("ok"):
        raise ValueError(f"origin is not an approved Git host: {origin.get('host', '')}")
    head = git(root, "rev-parse", "HEAD")
    branch = git(root, "branch", "--show-current")
    if not branch:
        raise ValueError("detached HEAD is not supported for pilot acceptance")
    if git(root, "status", "--porcelain=v1", "--untracked-files=all"):
        raise ValueError("pilot acceptance requires a clean checkout of the tested commit")
    return {"build_commit": head, "branch": branch, "origin_host": str(origin.get("host", ""))}


def evidence_path(root: Path, value: str, *, must_exist: bool) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise ValueError("evidence path must be absolute and outside the repository")
    resolved = path.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        pass
    else:
        raise ValueError("acceptance evidence must be stored outside the repository")
    if must_exist and not resolved.is_file():
        raise ValueError(f"evidence file does not exist: {resolved}")
    if not must_exist and resolved.exists():
        raise ValueError("evidence already exists; choose a new path instead of overwriting it")
    return resolved


def build_tester_evidence(
    *,
    build_commit: str,
    duration_minutes: int,
    windows_native: dict[str, bool],
    obsidian: dict[str, object],
    security: dict[str, bool],
    tester_confirmed: bool,
    phase_durations: dict[str, int] | None = None,
    ux_observations: dict[str, list[str]] | None = None,
    second_windows_native: dict[str, bool] | None = None,
    second_obsidian: dict[str, object] | None = None,
    second_security: dict[str, bool] | None = None,
    second_tester_confirmed: bool = False,
    second_phase_durations: dict[str, int] | None = None,
    second_ux_observations: dict[str, list[str]] | None = None,
    tested_at: str = "",
) -> dict[str, object]:
    second_windows_native = second_windows_native or {}
    second_obsidian = second_obsidian or {}
    second_security = second_security or {}
    phase_durations = phase_durations or {}
    second_phase_durations = second_phase_durations or {}
    ux_observations = ux_observations or {}
    second_ux_observations = second_ux_observations or {}

    def tester(journey: str, windows: dict[str, bool], obsidian_values: dict[str, object], security_values: dict[str, bool], confirmed: bool, phases: dict[str, int], observations: dict[str, list[str]]) -> dict[str, object]:
        return {
            "journey": journey,
            "tester_profile": "non-developer",
            "windows_native": {
                "approved_git_clone_succeeded": bool(windows.get("approved_git_clone_succeeded")),
                "install_from_wiki_succeeded": bool(windows.get("install_from_wiki_succeeded")),
                "first_capture_succeeded": bool(windows.get("first_capture_succeeded")),
                "search_succeeded": bool(windows.get("search_succeeded")),
                "promotion_preview_succeeded": bool(windows.get("promotion_preview_succeeded")),
                "duration_minutes": duration_minutes,
                "install_duration_minutes": int(phases.get("install_duration_minutes", 0)),
                "first_knowledge_duration_minutes": int(phases.get("first_knowledge_duration_minutes", 0)),
                "promotion_preview_duration_minutes": int(phases.get("promotion_preview_duration_minutes", 0)),
            },
            "obsidian": {
                "support_claimed": bool(obsidian_values.get("support_claimed")),
                "app_version": str(obsidian_values.get("app_version", "")),
                "vault_opened": bool(obsidian_values.get("vault_opened")),
                "external_file_watcher_succeeded": bool(obsidian_values.get("external_file_watcher_succeeded")),
                "properties_succeeded": bool(obsidian_values.get("properties_succeeded")),
                "backlinks_succeeded": bool(obsidian_values.get("backlinks_succeeded")),
                "graph_succeeded": bool(obsidian_values.get("graph_succeeded")),
            },
            "security": {
                "local_private_uploaded": bool(security_values.get("local_private_uploaded")),
                "remote_mutations_before_approval": bool(security_values.get("remote_mutations_before_approval")),
                "usage_telemetry_observed": bool(security_values.get("usage_telemetry_observed")),
            },
            "ux_observations": {
                "blocked_steps": list(observations.get("blocked_steps", [])),
                "misclicked_steps": list(observations.get("misclicked_steps", [])),
                "helpful_capture_ids": list(observations.get("helpful_capture_ids", [])),
            },
            "tester_confirmed": confirmed,
        }

    return {
        "schema": "boi-local-release-acceptance/v4",
        "build_commit": build_commit,
        "tested_at": tested_at or datetime.now().astimezone().isoformat(timespec="seconds"),
        "reviewer_role": "pending-review",
        "testers": [
            tester("no-obsidian", windows_native, obsidian, security, tester_confirmed, phase_durations, ux_observations),
            tester("obsidian-core", second_windows_native, second_obsidian, second_security, second_tester_confirmed, second_phase_durations, second_ux_observations),
        ],
        "domain_review": {
            "reviewer_profile": "pending-domain-review",
            "synthetic_case_reviewed": False,
            "workflow_plausibility_confirmed": False,
            "claims_marked_synthetic": False,
            "domain_persona_validated": False,
        },
        "reviewer_confirmed": False,
    }


def reviewed_candidate(payload: dict, reviewer_role: str, expected_build_commit: str) -> tuple[dict, dict[str, object]]:
    candidate = json.loads(json.dumps(payload))
    candidate["reviewer_role"] = reviewer_role.strip()
    candidate["reviewer_confirmed"] = True
    result = validate(candidate, expected_build_commit)
    return candidate, result


def domain_reviewed_candidate(
    payload: dict,
    confirmations: dict[str, bool],
    reviewer_profile: str = "domain-expert",
) -> dict:
    candidate = json.loads(json.dumps(payload))
    candidate["domain_review"] = {
        "reviewer_profile": reviewer_profile.strip(),
        "synthetic_case_reviewed": bool(confirmations.get("synthetic_case_reviewed")),
        "workflow_plausibility_confirmed": bool(confirmations.get("workflow_plausibility_confirmed")),
        "claims_marked_synthetic": bool(confirmations.get("claims_marked_synthetic")),
        "domain_persona_validated": bool(confirmations.get("domain_persona_validated")),
    }
    return candidate


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def ask_yes(prompt: str) -> bool:
    while True:
        answer = input(f"{prompt} [y/n]: ").strip().lower()
        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False
        print("y 또는 n으로 답하세요.")


def ask_duration(label: str) -> int:
    while True:
        raw = input(f"{label} 소요 시간(분, 1~240): ").strip()
        if raw.isdigit() and 1 <= int(raw) <= 240:
            return int(raw)
        print("1에서 240 사이의 분 단위를 입력하세요.")


def ask_windows_journey(label: str) -> tuple[dict[str, bool], dict[str, int]]:
    print(f"\n{label}")
    values = {
        "approved_git_clone_succeeded": True,
        "install_from_wiki_succeeded": ask_yes("Wiki만 보고 install.cmd 설치를 완료했습니까?"),
        "first_capture_succeeded": ask_yes("합성 자료로 첫 case/capture를 완료했습니까?"),
        "search_succeeded": ask_yes("근거 경로가 포함된 local search를 완료했습니까?"),
        "promotion_preview_succeeded": ask_yes("원격 등록 없이 promotion preview를 완료했습니까?"),
    }
    phases = {
        "install_duration_minutes": ask_duration("clone부터 설치 완료까지"),
        "first_knowledge_duration_minutes": ask_duration("첫 capture부터 distill·search 완료까지"),
        "promotion_preview_duration_minutes": ask_duration("promotion preview 생성"),
    }
    return values, phases


def ask_id_list(prompt: str) -> list[str]:
    raw = input(f"{prompt} (쉼표 구분, 없으면 Enter): ").strip()
    return [value.strip() for value in raw.split(",") if value.strip()]


def ask_ux_observations() -> dict[str, list[str]]:
    return {
        "blocked_steps": ask_id_list("막힌 단계 ID"),
        "misclicked_steps": ask_id_list("잘못 클릭한 단계 ID"),
        "helpful_capture_ids": ask_id_list("도움 된 캡처 ID 예: screen-19"),
    }


def ask_security() -> dict[str, bool]:
    return {
        "local_private_uploaded": ask_yes("Local Private가 웹이나 원격 서비스에 업로드된 사실이 있습니까?"),
        "remote_mutations_before_approval": ask_yes("사용자 승인 전에 원격 변경이 발생했습니까?"),
        "usage_telemetry_observed": ask_yes("제품이 사용자 행동 telemetry를 기록한 사실이 있습니까?"),
    }


def start(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    context = checkout_context(root, args.origin_host_pattern)
    path = evidence_path(root, args.evidence, must_exist=False)
    print("이 마법사는 이름·사번·업무 원문·화면 녹화를 묻거나 저장하지 않습니다.")
    print(f"시험 commit: {context['build_commit']}")
    print(f"Approved Git host: {context['origin_host']}")
    windows, phases = ask_windows_journey("비개발자 A - Obsidian 미사용 경로")
    duration = sum(phases.values())
    ux_observations = ask_ux_observations()
    security = ask_security()
    confirmed = input("A의 답변이 사실이며 비식별 결과만 저장됨을 확인하려면 CONFIRM 입력: ").strip() == "CONFIRM"

    second_windows, second_phases = ask_windows_journey("비개발자 B - Obsidian Core 경로")
    second_duration = sum(second_phases.values())
    second_ux_observations = ask_ux_observations()
    second_obsidian: dict[str, object] = {
        "support_claimed": True,
        "app_version": input("Obsidian runtime 버전: ").strip(),
        "vault_opened": ask_yes("Windows-native Vault가 열렸습니까?"),
        "external_file_watcher_succeeded": ask_yes("외부 Markdown이 재시작 없이 나타났습니까?"),
        "properties_succeeded": ask_yes("Properties가 표시됐습니까?"),
        "backlinks_succeeded": ask_yes("Backlinks가 표시됐습니까?"),
        "graph_succeeded": ask_yes("Graph가 표시됐습니까?"),
    }
    second_security = ask_security()
    second_confirmed = input("B의 답변이 사실이며 비식별 결과만 저장됨을 확인하려면 CONFIRM 입력: ").strip() == "CONFIRM"
    payload = build_tester_evidence(
        build_commit=context["build_commit"],
        duration_minutes=duration,
        windows_native=windows,
        obsidian={"support_claimed": False},
        security=security,
        tester_confirmed=confirmed,
        phase_durations=phases,
        ux_observations=ux_observations,
        second_windows_native=second_windows,
        second_obsidian=second_obsidian,
        second_security=second_security,
        second_tester_confirmed=second_confirmed,
        second_phase_durations=second_phases,
        second_ux_observations=second_ux_observations,
    )
    payload["testers"][1]["windows_native"]["duration_minutes"] = second_duration
    findings = identity_findings(payload)
    if findings:
        raise ValueError("evidence contains prohibited identity fields")
    write_json(path, payload)
    preview = validate(payload, context["build_commit"])
    print(json.dumps({"stage": "tester-draft", "evidence": str(path), "validation": preview}, ensure_ascii=False, indent=2))
    print("knowledge steward가 같은 commit에서 review를 실행해야 최종 evidence가 됩니다. 배포 범위에 담당 전문가가 소유한 도메인 Case가 있을 때만 use-case-review를 추가합니다.")
    return 0


def preflight(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    context = checkout_context(root, args.origin_host_pattern)
    path = evidence_path(root, args.evidence, must_exist=False)
    payload = {
        "ok": True,
        "schema": "boi-local-pilot-preflight/v1",
        "windows_native_checkout": True,
        "origin_host": context["origin_host"],
        "branch": context["branch"],
        "build_commit": context["build_commit"],
        "clean_checkout": True,
        "evidence_path": str(path),
        "evidence_outside_repository": True,
        "evidence_created_by_preflight": False,
        "evidence_will_be_created_by_start": True,
        "next": "pilot-acceptance.cmd start --evidence <same-absolute-path>",
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def domain_review(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    context = checkout_context(root, args.origin_host_pattern)
    path = evidence_path(root, args.evidence, must_exist=True)
    payload = json.loads(path.read_text(encoding="utf-8"))
    example_id = args.example_id.strip() or "packaged-example"
    domain_label = args.domain_label.strip() or "packaged use case"
    confirmations = {
        "synthetic_case_reviewed": ask_yes(f"{example_id} 합성 사례 전체를 검토했습니까?"),
        "workflow_plausibility_confirmed": ask_yes(f"{domain_label} 여정이 실무상 타당합니까?"),
        "claims_marked_synthetic": ask_yes("내부 사실로 오해할 표현 없이 합성임이 명확합니까?"),
        "domain_persona_validated": ask_yes(f"{domain_label} 전문가 관점에서 persona 검증을 완료했습니까?"),
    }
    if input("내부 전문가 검토 결과를 확정하려면 DOMAIN-APPROVE 입력: ").strip() != "DOMAIN-APPROVE":
        print("검토를 확정하지 않았습니다. evidence는 변경되지 않았습니다.")
        return 2
    candidate = domain_reviewed_candidate(payload, confirmations, args.reviewer_profile)
    if candidate.get("build_commit") != context["build_commit"]:
        raise ValueError("build_commit does not match the domain-review checkout HEAD")
    write_json(path, candidate)
    print(json.dumps({"stage": "domain-reviewed", "evidence": str(path), "domain_review": candidate["domain_review"]}, ensure_ascii=False, indent=2))
    return 0


def review(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    context = checkout_context(root, args.origin_host_pattern)
    path = evidence_path(root, args.evidence, must_exist=True)
    payload = json.loads(path.read_text(encoding="utf-8"))
    reviewer_role = args.reviewer_role or input("reviewer 역할(예: knowledge-steward): ").strip()
    candidate, result = reviewed_candidate(payload, reviewer_role, context["build_commit"])
    if not result["ok"]:
        print(json.dumps({"stage": "review-blocked", "validation": result}, ensure_ascii=False, indent=2))
        return 2
    summary = {
        "build_commit": candidate["build_commit"],
        "tested_at": candidate["tested_at"],
        "reviewer_role": candidate["reviewer_role"],
        "testers": candidate["testers"],
        "domain_review": candidate["domain_review"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if input("이 비식별 결과를 승인하려면 APPROVE 입력: ").strip() != "APPROVE":
        print("승인하지 않았습니다. evidence는 변경되지 않았습니다.")
        return 2
    write_json(path, candidate)
    print(json.dumps({"stage": "approved", "evidence": str(path), "validation": result}, ensure_ascii=False, indent=2))
    return 0


def validate_command(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    context = checkout_context(root, args.origin_host_pattern)
    path = evidence_path(root, args.evidence, must_exist=True)
    payload = json.loads(path.read_text(encoding="utf-8"))
    result = validate(payload, context["build_commit"])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--origin-host-pattern", default=r"github[.]com|bitbucket")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("preflight", "start", "domain-review", "use-case-review", "review", "validate"):
        child = subparsers.add_parser(command)
        child.add_argument("--evidence", required=True, help="absolute path outside the repository")
        if command in {"domain-review", "use-case-review"}:
            child.add_argument("--reviewer-profile", default="domain-expert")
            child.add_argument("--example-id", default="packaged-example")
            child.add_argument("--domain-label", default="packaged use case")
        if command == "review":
            child.add_argument("--reviewer-role", default="")
    args = parser.parse_args()
    try:
        if args.command == "preflight":
            return preflight(args)
        if args.command == "start":
            return start(args)
        if args.command in {"domain-review", "use-case-review"}:
            return domain_review(args)
        if args.command == "review":
            return review(args)
        return validate_command(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
