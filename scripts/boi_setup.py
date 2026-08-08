#!/usr/bin/env python3
"""Non-destructive setup and verification for BoI Wiki Local."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from boi_local_common import now_kst, private_root, relative_to_root, workspace_employee_id

GUIDE_RELEASE = "3.2.0"
GUIDE_RELEASE_TIMESTAMP = "2026-08-07T00:00:00+09:00"
GUIDE_REVIEW_AFTER = "2027-02-01"
OBSIDIAN_MANIFEST = "boi-wiki-local-managed.json"
FOLDER_DESCRIPTIONS = {
    "notes": "회의록, 수집 원문, 정제 지식",
    "notes/capture-inbox": "수정하지 않는 수집 원문",
    "notes/knowledge": "원문에서 정제한 지식",
    "notes/memory": "AI가 대화와 자료에서 확인한 장기 활용 지식",
    "notes/guide": "설치와 사용을 설명하는 연결형 Wiki",
    "notes/harnesses": "승인된 개인 Harness 카드와 다음 세션 재사용 계약",
    "cases": "근거·가설·판정·재발 fingerprint를 연결하는 Local Case Hub",
    "evidence": "원본 bytes와 provenance sidecar를 보존하는 Local evidence",
    "sop-drafts": "SOP 초안",
    "action-drafts": "Action과 업무 요청 초안",
    "event-drafts": "Event와 업무 흐름 초안",
    "dictionary": "개인 도메인 용어와 별칭",
    "diagrams": "Mermaid와 SVG 초안",
    "context-packs": "에이전트용 로컬 context pack",
    "workflow-simulations": "실행 전 workflow 검토",
    "langflow-plans": "BoI 연계 Langflow 설계",
    "reports": "보고서와 업무 증빙",
    "promotion-drafts": "Team/Public 공유 전 로컬 미리보기",
    "usage-examples": "사용자가 선택해 참고하는 예제 영역",
    "_archive": "보관 문서",
}


def render_root_index(employee_id: str) -> str:
    return f"""# 내 BoI Wiki Local

사번 `{employee_id}`의 개인 Meta Harness와 Local Private 지식 공간입니다. 이 폴더의 내용은 명시적인 promotion 승인 없이 원격으로 전송하지 않습니다.

## 먼저 할 일

1. [내 업무용 BoI Harness 만들기](notes/guide/02-build-your-harness.md) - 업무 설명을 역할·Skill·작업 흐름·검토 계약으로 구성
2. [Flagship Second Brain 설정](notes/guide/12-ai-assisted-setup.md) - 대화와 자료에서 오래 쓸 지식을 축적·교정·재사용
3. [처음 시작하기](notes/guide/00-start-here.md) - 전체 제품 구조와 Local/Remote 경계 확인
4. [승인된 개인 Harness](notes/harnesses/index.md) - 다음 세션에도 다시 사용할 실행 계약

## 내 작업 공간

* [Inbox](inbox.md) - 아직 분류하지 않은 입력
* [Notes](notes/) - 수집 원문과 정제 지식
* [SOP Drafts](sop-drafts/)
* [Action Drafts](action-drafts/)
* [Event Drafts](event-drafts/)
* [Dictionary](dictionary/)
* [Context Packs](context-packs/)
* [Reports](reports/)
* [Promotion Drafts](promotion-drafts/)
* [Archive](_archive/)
"""


def render_inbox() -> str:
    return """# Inbox

아직 분류하지 않은 짧은 메모를 적습니다. 에이전트에게 "Inbox를 불변 원문으로 수집하고 정제해줘"라고 요청할 수 있습니다.

Local Private 원문은 사용자 승인 전에는 원격 서비스로 보내지 않습니다.
"""


def render_harness_index() -> str:
    return """# 승인된 개인 Harness

이곳은 AI가 업무 설명에서 구성하고 사용자가 승인한 재사용 실행 계약을 찾는 시작 페이지입니다. Harness 카드는 Local Private로 유지되며 그 자체를 Team/Public으로 직접 공유하지 않습니다.

## 새 Harness 만들기

> 내가 반복하는 업무를 설명할게. 기존 BoI Skills를 먼저 확인하고 역할, 작업 흐름, 산출물, 검토 기준이 있는 Harness 미리보기를 만들어줘. 내가 승인하면 이 폴더에 저장해줘.

## 저장된 Harness 다시 사용하기

> 저장된 Harness 이름으로 이번 자료를 처리해줘. 먼저 필요한 입력과 변경 범위를 확인하고 기존 역할·DAG·검토 계약을 그대로 사용해줘.

## 기존 Harness 개선하기

> 저장된 Harness 이름에서 실제로 막힌 부분을 분석하고, 기존 파일과 실패 evidence를 보존하는 변경 미리보기를 먼저 보여줘.

## 저장된 Harness

승인된 카드가 생기면 AI가 이 아래에 표준 Markdown 링크를 추가합니다. 카드가 아직 없어도 오류가 아닙니다.

## 공유 경계

개인 Harness 카드에는 Local 경로와 실행 설정이 있으므로 직접 promotion할 수 없습니다. 조직에 공유하려면 개인 설정을 제거한 일반 가이드나 검토된 Community Case로 별도 정제합니다.
"""


def render_folder_index(relative: str, description: str) -> str:
    title = relative.split("/")[-1].replace("-", " ").title()
    return f"# {title}\n\n{description}을(를) 보관합니다.\n"


def repository_url(root: Path) -> str:
    """Return the configured origin without ever rendering embedded credentials."""
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except FileNotFoundError:
        return "<배포 Git 저장소 주소>"
    if completed.returncode != 0:
        return "<배포 Git 저장소 주소>"
    value = completed.stdout.strip()
    if not value:
        return "<배포 Git 저장소 주소>"
    # HTTPS remotes may contain a user name or token. The generated Wiki must not.
    if "://" in value:
        from urllib.parse import urlsplit, urlunsplit

        parsed = urlsplit(value)
        host = parsed.hostname or ""
        if parsed.port:
            host = f"{host}:{parsed.port}"
        if parsed.scheme.lower() == "ssh" and parsed.username == "git" and parsed.password is None:
            host = f"git@{host}"
        return urlunsplit((parsed.scheme, host, parsed.path, parsed.query, parsed.fragment))
    return value


def render_guide(template: Path, employee_id: str, repo_url: str) -> str:
    return (
        template.read_text(encoding="utf-8")
        .replace("{{employee_id}}", employee_id)
        .replace("{{timestamp}}", GUIDE_RELEASE_TIMESTAMP)
        .replace("{{review_after}}", GUIDE_REVIEW_AFTER)
        .replace("{{repository_url}}", repo_url)
        .replace("](../../cases/", "](../../../../../../cases/")
    )


def desired_files(root: Path, employee_id: str) -> dict[Path, str]:
    base = private_root(root, employee_id)
    files = {base / "index.md": render_root_index(employee_id), base / "inbox.md": render_inbox()}
    for relative, description in FOLDER_DESCRIPTIONS.items():
        if relative == "notes/guide":
            continue
        files[base / relative / "index.md"] = (
            render_harness_index() if relative == "notes/harnesses" else render_folder_index(relative, description)
        )
    guide_root = root / "templates" / "second-brain-guide"
    # The tracked 0000000 profile is a deployment-neutral example. Never bake
    # a maintainer's development origin into the Wiki shipped to employees.
    repo_url = "<배포 Git 저장소 주소>" if employee_id == "0000000" else repository_url(root)
    for template in sorted(guide_root.rglob("*.md")):
        relative = template.relative_to(guide_root)
        files[base / "notes" / "guide" / relative] = render_guide(template, employee_id, repo_url)
    return files


def desired_guide_assets(root: Path, employee_id: str) -> dict[Path, bytes]:
    guide_root = root / "templates" / "second-brain-guide"
    media_root = guide_root / "_media"
    if not media_root.is_dir():
        return {}
    target_root = private_root(root, employee_id) / "notes" / "guide" / "_media"
    return {
        target_root / source.relative_to(media_root): source.read_bytes()
        for source in sorted(media_root.rglob("*"))
        if source.is_file()
    }


def env_plan(root: Path, employee_id: str) -> tuple[str, str]:
    path = root / ".env"
    if not path.exists():
        template = root / ".env.example"
        content = template.read_text(encoding="utf-8") if template.exists() else "BOI_LOCAL_ROOT=.\n"
        content = content.replace("BOI_LOCAL_EMPLOYEE_ID=0000000", f"BOI_LOCAL_EMPLOYEE_ID={employee_id}")
        return "create", content
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()
    found = False
    current_value = ""
    output = []
    for line in lines:
        if line.startswith("BOI_LOCAL_EMPLOYEE_ID="):
            found = True
            current_value = line.split("=", 1)[1].strip()
            output.append(f"BOI_LOCAL_EMPLOYEE_ID={employee_id}" if current_value in {"", "0000000", employee_id} else line)
        else:
            output.append(line)
    if not found:
        output.append(f"BOI_LOCAL_EMPLOYEE_ID={employee_id}")
    updated = "\n".join(output).rstrip() + "\n"
    if current_value not in {"", "0000000", employee_id}:
        return "conflict", content
    return ("unchanged" if updated == content else "update"), updated


def build_plan(root: Path, employee_id: str) -> dict[str, object]:
    create, unchanged, preserved_custom, guide_updates = [], [], [], []
    asset_create, asset_unchanged, asset_updates = [], [], []
    guide_dir = private_root(root, employee_id) / "notes" / "guide"
    for path, content in desired_files(root, employee_id).items():
        rel = relative_to_root(root, path)
        if not path.exists():
            create.append(rel)
        elif path.read_text(encoding="utf-8") == content:
            unchanged.append(rel)
        elif path.is_relative_to(guide_dir):
            guide_updates.append(rel)
        else:
            preserved_custom.append(rel)
    for path, content in desired_guide_assets(root, employee_id).items():
        rel = relative_to_root(root, path)
        if not path.exists():
            create.append(rel)
            asset_create.append(rel)
        elif path.read_bytes() == content:
            asset_unchanged.append(rel)
        else:
            asset_updates.append(rel)
    env_action, _ = env_plan(root, employee_id)
    return {
        "ok": env_action != "conflict",
        "employee_id": employee_id,
        "guide_release": GUIDE_RELEASE,
        "create": create,
        "unchanged": unchanged,
        "preserved_custom": preserved_custom,
        "guide_updates_available": guide_updates,
        "guide_asset_create": asset_create,
        "guide_asset_updates_available": asset_updates,
        "guide_asset_unchanged": asset_unchanged,
        "conflicts": [".env: BOI_LOCAL_EMPLOYEE_ID belongs to another user"] if env_action == "conflict" else [],
        "env_action": env_action,
        "private_root": relative_to_root(root, private_root(root, employee_id)),
        "overwrites_planned": False,
    }


def is_wsl_runtime() -> bool:
    if os.environ.get("WSL_DISTRO_NAME") or os.environ.get("WSL_INTEROP"):
        return True
    try:
        return "microsoft" in Path("/proc/sys/kernel/osrelease").read_text(encoding="utf-8").lower()
    except OSError:
        return False


def vault_transport(root: Path) -> str:
    normalized = str(root).replace("\\", "/").lower()
    if normalized.startswith("//wsl$/") or normalized.startswith("//wsl.localhost/"):
        return "wsl-unc"
    if os.name == "nt" or (len(normalized) >= 3 and normalized[1:3] == ":/"):
        return "windows-native"
    if is_wsl_runtime():
        return "wsl-posix"
    return "linux-native"


def obsidian_compatibility(root: Path, requested_host: str = "auto") -> dict[str, object]:
    host = requested_host if requested_host != "auto" else ("windows" if os.name == "nt" else "linux")
    transport = vault_transport(root)
    blocked = host == "windows" and transport in {"wsl-unc", "wsl-posix"}
    if blocked:
        return {
            "ok": False,
            "host": host,
            "vault_transport": transport,
            "status": "blocked-verified",
            "reason": "Windows Obsidian 1.12.7 failed to watch this WSL Vault with EISDIR",
            "recommended_action": "skip-obsidian-and-continue-local",
            "shadow_copy_allowed": False,
        }
    return {
        "ok": True,
        "host": host,
        "vault_transport": transport,
        "status": "eligible-for-vault-smoke-test",
        "reason": "No verified transport blocker; opening the Vault and checking file watching is still required",
        "recommended_action": "preview-then-open-vault-before-configuring",
        "shadow_copy_allowed": False,
    }


def doctor(root: Path, employee_id: str, obsidian_host: str = "auto") -> dict[str, object]:
    harness = root / "scripts" / "harness_sync.py"
    harness_ok = False
    harness_message = "missing"
    if harness.exists():
        completed = subprocess.run(
            [sys.executable, str(harness), "verify", "--root", str(root)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        harness_ok = completed.returncode == 0
        harness_message = "valid" if harness_ok else (completed.stderr or completed.stdout).strip()[:500]
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    obsidian_candidates = []
    if local_app_data:
        obsidian_candidates = [
            Path(local_app_data) / "Obsidian" / "Obsidian.exe",
            Path(local_app_data) / "Programs" / "Obsidian" / "Obsidian.exe",
        ]
    compatibility = obsidian_compatibility(root, obsidian_host)
    return {
        "ok": (root / "AGENTS.md").exists() and harness_ok,
        "employee_id": employee_id,
        "python": sys.version.split()[0],
        "git": shutil.which("git") or "not-found",
        "obsidian_detected": any(path.exists() for path in obsidian_candidates) or bool(shutil.which("obsidian")),
        "obsidian_compatibility": compatibility,
        "harness": harness_message,
        "mcp_required": False,
        "obsidian_required": False,
    }


def apply_setup(root: Path, employee_id: str) -> dict[str, object]:
    plan = build_plan(root, employee_id)
    created = []
    for path, content in desired_files(root, employee_id).items():
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        created.append(relative_to_root(root, path))
    for path, content in desired_guide_assets(root, employee_id).items():
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        created.append(relative_to_root(root, path))
    env_action, env_content = env_plan(root, employee_id)
    if env_action in {"create", "update"}:
        (root / ".env").write_text(env_content, encoding="utf-8", newline="\n")
    return {
        "ok": env_action != "conflict",
        "employee_id": employee_id,
        "created": created,
        "preserved_existing": len(plan["unchanged"]) + len(plan["preserved_custom"]) + len(plan["guide_updates_available"]) + len(plan["guide_asset_unchanged"]) + len(plan["guide_asset_updates_available"]),
        "conflicts": plan["conflicts"],
        "guide_updates_available": plan["guide_updates_available"],
        "guide_asset_create": plan["guide_asset_create"],
        "guide_asset_updates_available": plan["guide_asset_updates_available"],
        "guide_asset_unchanged": plan["guide_asset_unchanged"],
        "env_action": env_action,
        "overwritten": [],
    }


def guide_update_preview(root: Path, employee_id: str) -> dict[str, object]:
    base = private_root(root, employee_id) / "notes" / "guide"
    changes = []
    for path, desired in desired_files(root, employee_id).items():
        if not path.is_relative_to(base):
            continue
        current = path.read_text(encoding="utf-8") if path.exists() else ""
        if current == desired:
            continue
        diff = list(difflib.unified_diff(current.splitlines(), desired.splitlines(), fromfile="current", tofile=f"guide-{GUIDE_RELEASE}", lineterm=""))
        changes.append({"path": relative_to_root(root, path), "action": "update" if path.exists() else "create", "diff": diff[:200]})
    asset_create, asset_updates, asset_unchanged = [], [], []
    for path, desired in desired_guide_assets(root, employee_id).items():
        relative = relative_to_root(root, path)
        if not path.exists():
            asset_create.append(relative)
            changes.append({"path": relative, "action": "create", "asset_sha256": hashlib.sha256(desired).hexdigest()})
        elif path.read_bytes() == desired:
            asset_unchanged.append(relative)
        else:
            asset_updates.append(relative)
            changes.append({
                "path": relative,
                "action": "update",
                "current_sha256": file_sha256(path),
                "asset_sha256": hashlib.sha256(desired).hexdigest(),
            })
    return {
        "ok": True,
        "employee_id": employee_id,
        "guide_release": GUIDE_RELEASE,
        "changes": changes,
        "guide_asset_create": asset_create,
        "guide_asset_updates_available": asset_updates,
        "guide_asset_unchanged": asset_unchanged,
        "requires_confirmation": bool(changes),
    }


def guide_update_apply(root: Path, employee_id: str, confirmation: str) -> dict[str, object]:
    if confirmation != GUIDE_RELEASE:
        raise ValueError(f"guide update requires --confirm-guide-release {GUIDE_RELEASE}")
    base = private_root(root, employee_id) / "notes" / "guide"
    archive = private_root(root, employee_id) / "_archive" / "guides" / now_kst().strftime("%Y%m%d-%H%M%S")
    updated, created = [], []
    asset_updated, asset_created, asset_unchanged = [], [], []
    for path, desired in desired_files(root, employee_id).items():
        if not path.is_relative_to(base):
            continue
        if path.exists() and path.read_text(encoding="utf-8") == desired:
            continue
        if path.exists():
            backup = archive / path.relative_to(base)
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, backup)
            updated.append(relative_to_root(root, path))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            created.append(relative_to_root(root, path))
        path.write_text(desired, encoding="utf-8", newline="\n")
    for path, desired in desired_guide_assets(root, employee_id).items():
        if path.exists() and path.read_bytes() == desired:
            asset_unchanged.append(relative_to_root(root, path))
            continue
        if path.exists():
            backup = archive / path.relative_to(base)
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, backup)
            updated.append(relative_to_root(root, path))
            asset_updated.append(relative_to_root(root, path))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            created.append(relative_to_root(root, path))
            asset_created.append(relative_to_root(root, path))
        path.write_bytes(desired)
    return {
        "ok": True,
        "employee_id": employee_id,
        "updated": updated,
        "created": created,
        "guide_asset_create": asset_created,
        "guide_asset_updates_available": asset_updated,
        "guide_asset_unchanged": asset_unchanged,
        "backup": relative_to_root(root, archive) if updated else "",
        "guide_release": GUIDE_RELEASE,
    }


def obsidian_configs(base: Path) -> dict[Path, object]:
    return {
        base / ".obsidian" / "app.json": {"alwaysUpdateLinks": True, "attachmentFolderPath": "_media", "newFileLocation": "folder", "newFileFolderPath": "notes/capture-inbox"},
        base / ".obsidian" / "core-plugins.json": {
            plugin_id: True
            for plugin_id in (
                "file-explorer",
                "global-search",
                "switcher",
                "graph",
                "backlink",
                "outgoing-link",
                "properties",
                "bases",
                "canvas",
                "templates",
                "bookmarks",
                "page-preview",
            )
        },
        base / ".obsidian" / "graph.json": {"collapse-filter": False, "search": "-path:notes/capture-inbox -path:notes/guide -path:promotion-drafts -path:usage-examples -path:_archive"},
    }


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def obsidian_plan(root: Path, employee_id: str, obsidian_host: str = "auto") -> dict[str, object]:
    base = private_root(root, employee_id)
    targets = list(obsidian_configs(base))
    compatibility = obsidian_compatibility(root, obsidian_host)
    return {
        "ok": base.exists() and bool(compatibility["ok"]),
        "employee_id": employee_id,
        "vault": str(base),
        "compatibility": compatibility,
        "create": [relative_to_root(root, path) for path in targets if not path.exists()],
        "preserve": [relative_to_root(root, path) for path in targets if path.exists()],
        "managed_manifest": relative_to_root(root, base / ".obsidian" / OBSIDIAN_MANIFEST),
        "requires_confirmation": bool(compatibility["ok"]),
        "installs_obsidian_app": False,
        "installs_community_plugins": False,
    }


def obsidian_apply(root: Path, employee_id: str, confirmed: bool, obsidian_host: str = "auto") -> dict[str, object]:
    if not confirmed:
        raise ValueError("Obsidian configuration requires --confirm-obsidian-config")
    base = private_root(root, employee_id)
    if not base.exists():
        raise ValueError("run setup apply before Obsidian configuration")
    compatibility = obsidian_compatibility(root, obsidian_host)
    if not compatibility["ok"]:
        raise ValueError(str(compatibility["reason"]))
    configs = obsidian_configs(base)
    created, preserved = [], []
    for path, payload in configs.items():
        if path.exists():
            preserved.append(relative_to_root(root, path))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        created.append(relative_to_root(root, path))
    manifest_path = base / ".obsidian" / OBSIDIAN_MANIFEST
    prior_entries: dict[str, str] = {}
    if manifest_path.exists():
        try:
            prior_entries = dict(json.loads(manifest_path.read_text(encoding="utf-8")).get("created_files", {}))
        except (json.JSONDecodeError, TypeError, ValueError):
            raise ValueError(f"invalid managed manifest: {relative_to_root(root, manifest_path)}")
    for relative in created:
        path = root / relative
        prior_entries[path.name] = file_sha256(path)
    if prior_entries:
        manifest = {
            "schema_version": 1,
            "employee_id": employee_id,
            "created_at": now_kst().isoformat(),
            "created_files": prior_entries,
            "recovery_command": "boi_setup.py obsidian-recover-preview then obsidian-recover-apply",
        }
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return {
        "ok": True,
        "employee_id": employee_id,
        "compatibility": compatibility,
        "created": created,
        "preserved": preserved,
        "managed_manifest": relative_to_root(root, manifest_path) if prior_entries else "",
        "recovery_available": bool(prior_entries),
        "community_plugins_installed": [],
    }


def obsidian_recovery_preview(root: Path, employee_id: str) -> dict[str, object]:
    base = private_root(root, employee_id)
    config_dir = base / ".obsidian"
    manifest_path = config_dir / OBSIDIAN_MANIFEST
    if not manifest_path.exists():
        return {
            "ok": True,
            "employee_id": employee_id,
            "managed_manifest": "",
            "remove_safe": [],
            "preserve_modified": [],
            "missing": [],
            "requires_confirmation": False,
        }
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        entries = dict(manifest.get("created_files", {}))
    except (json.JSONDecodeError, TypeError, ValueError):
        raise ValueError(f"invalid managed manifest: {relative_to_root(root, manifest_path)}")
    allowed = {path.name for path in obsidian_configs(base)}
    invalid = sorted(name for name in entries if name not in allowed or Path(name).name != name)
    if invalid:
        raise ValueError(f"managed manifest contains unsafe entries: {', '.join(invalid)}")
    remove_safe, preserve_modified, missing = [], [], []
    for name, expected_hash in sorted(entries.items()):
        path = config_dir / name
        rel = relative_to_root(root, path)
        if not path.exists():
            missing.append(rel)
        elif file_sha256(path) == expected_hash:
            remove_safe.append(rel)
        else:
            preserve_modified.append(rel)
    return {
        "ok": True,
        "employee_id": employee_id,
        "managed_manifest": relative_to_root(root, manifest_path),
        "remove_safe": remove_safe,
        "preserve_modified": preserve_modified,
        "missing": missing,
        "requires_confirmation": bool(remove_safe or missing),
    }


def obsidian_recovery_apply(root: Path, employee_id: str, confirmed: bool) -> dict[str, object]:
    if not confirmed:
        raise ValueError("Obsidian recovery requires --confirm-obsidian-recovery")
    preview = obsidian_recovery_preview(root, employee_id)
    base = private_root(root, employee_id)
    manifest_path = base / ".obsidian" / OBSIDIAN_MANIFEST
    removed = []
    for relative in preview["remove_safe"]:
        path = root / str(relative)
        path.unlink()
        removed.append(str(relative))
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        remaining_names = {Path(path).name for path in preview["preserve_modified"]}
        remaining = {name: value for name, value in dict(manifest.get("created_files", {})).items() if name in remaining_names}
        if remaining:
            manifest["created_files"] = remaining
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        else:
            manifest_path.unlink()
    return {
        "ok": True,
        "employee_id": employee_id,
        "removed": removed,
        "preserved_modified": preview["preserve_modified"],
        "already_missing": preview["missing"],
        "manifest_removed": not manifest_path.exists(),
        "vault_directory_removed": False,
    }


def verify(root: Path, employee_id: str) -> dict[str, object]:
    from local_lint import lint_workspace

    plan = build_plan(root, employee_id)
    lint = lint_workspace(root, employee_id)
    return {
        "ok": not plan["create"] and not plan["conflicts"] and plan["env_action"] == "unchanged" and lint["ok"],
        "employee_id": employee_id,
        "missing": plan["create"],
        "conflicts": plan["conflicts"],
        "preserved_custom": plan["preserved_custom"],
        "guide_updates_available": plan["guide_updates_available"],
        "guide_asset_create": plan["guide_asset_create"],
        "guide_asset_updates_available": plan["guide_asset_updates_available"],
        "guide_asset_unchanged": plan["guide_asset_unchanged"],
        "lint": {"ok": lint["ok"], "checked": lint.get("checked", 0), "error_count": lint.get("error_count", 0), "errors": lint.get("errors", [])[:20]},
    }


def next_steps(root: Path, employee_id: str) -> dict[str, object]:
    base = private_root(root, employee_id)
    return {
        "ok": base.exists(),
        "employee_id": employee_id,
        "guide": relative_to_root(root, base / "notes" / "guide" / "00-start-here.md"),
        "requests": [
            "오늘 회의 메모를 수정하지 않는 원문으로 수집해줘.",
            "방금 수집한 원문을 결정, 근거, 후속 작업으로 정제해줘.",
            "관련된 로컬 문서를 근거 경로와 함께 찾아줘.",
            "이 문서를 Team 공유 후보로 만들고 미리보기까지만 해줘.",
        ],
        "optional": ["Obsidian 설치와 Vault 연결", "QuickAdd", "공식 Web Clipper", "shared BoI Wiki MCP"],
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["doctor", "preview", "apply", "verify", "next-steps", "guide-preview", "guide-apply", "obsidian-preview", "obsidian-apply", "obsidian-recover-preview", "obsidian-recover-apply"])
    parser.add_argument("--root", default=".")
    parser.add_argument("--employee-id", default="")
    parser.add_argument("--allow-template", action="store_true")
    parser.add_argument("--confirm-guide-release", default="")
    parser.add_argument("--confirm-obsidian-config", action="store_true")
    parser.add_argument("--confirm-obsidian-recovery", action="store_true")
    parser.add_argument("--obsidian-host", choices=["auto", "windows", "linux"], default="auto")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    try:
        employee_id, _ = workspace_employee_id(root, args.employee_id, allow_template=args.allow_template)
        handlers = {
            "doctor": lambda: doctor(root, employee_id, args.obsidian_host),
            "preview": lambda: build_plan(root, employee_id),
            "apply": lambda: apply_setup(root, employee_id),
            "verify": lambda: verify(root, employee_id),
            "next-steps": lambda: next_steps(root, employee_id),
            "guide-preview": lambda: guide_update_preview(root, employee_id),
            "guide-apply": lambda: guide_update_apply(root, employee_id, args.confirm_guide_release),
            "obsidian-preview": lambda: obsidian_plan(root, employee_id, args.obsidian_host),
            "obsidian-apply": lambda: obsidian_apply(root, employee_id, args.confirm_obsidian_config, args.obsidian_host),
            "obsidian-recover-preview": lambda: obsidian_recovery_preview(root, employee_id),
            "obsidian-recover-apply": lambda: obsidian_recovery_apply(root, employee_id, args.confirm_obsidian_recovery),
        }
        payload = handlers[args.command]()
    except (ValueError, FileNotFoundError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
