#!/usr/bin/env python3
"""Preview or apply a safe origin-driven BoI Wiki Local update."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from boi_setup import guide_update_apply, guide_update_preview
from boi_local_common import workspace_employee_id


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def checked(root: Path, *args: str) -> str:
    result = run(root, *args)
    if result.returncode:
        raise ValueError((result.stderr or result.stdout).strip() or f"git {' '.join(args)} failed")
    return result.stdout.strip()


def safe_remote(value: str) -> str:
    if "://" not in value:
        return value
    parsed = urlsplit(value)
    host = parsed.hostname or ""
    if parsed.port:
        host = f"{host}:{parsed.port}"
    if parsed.scheme.lower() == "ssh" and parsed.username == "git" and parsed.password is None:
        host = f"git@{host}"
    return urlunsplit((parsed.scheme, host, parsed.path, parsed.query, parsed.fragment))


def private_manifest(root: Path, employee_id: str) -> dict[str, str]:
    base = root / "data" / "boi" / "private" / employee_id
    output = {}
    if not base.exists():
        return output
    for path in sorted(item for item in base.rglob("*") if item.is_file()):
        relative = path.relative_to(base).as_posix()
        if relative.startswith("notes/guide/") or relative.startswith("_archive/guides/"):
            continue
        output[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return output


def call(root: Path, *args: str) -> None:
    completed = subprocess.run(
        args,
        cwd=root,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        combined = "\n".join(part.strip() for part in (completed.stdout, completed.stderr) if part.strip())
        detail = combined[-6000:]
        raise ValueError(f"command failed ({completed.returncode}): {' '.join(args)}: {detail}")


def update(root: Path, apply: bool, confirm_guide_release: str) -> dict[str, object]:
    if not (root / ".git").exists():
        raise ValueError(f"not a Git checkout: {root}")
    employee_id, employee_id_source = workspace_employee_id(root)
    before = private_manifest(root, employee_id)
    origin = checked(root, "remote", "get-url", "origin")
    status = checked(root, "status", "--porcelain=v1", "--untracked-files=all").splitlines()
    branch = checked(root, "branch", "--show-current")
    if not branch:
        raise ValueError("detached HEAD is not supported")
    checked(root, "fetch", "--prune", "origin")
    head = run(root, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
    if head.returncode == 0 and head.stdout.strip().startswith("origin/"):
        stable = head.stdout.strip().split("/", 1)[1]
    elif run(root, "show-ref", "--verify", "--quiet", "refs/remotes/origin/main").returncode == 0:
        stable = "main"
    else:
        raise ValueError("cannot determine stable branch; configure origin/HEAD or origin/main")
    incoming = checked(root, "log", "--oneline", f"{branch}..origin/{stable}").splitlines()
    changed = checked(root, "diff", "--name-status", f"{branch}...origin/{stable}").splitlines()
    result: dict[str, object] = {
        "ok": True,
        "mode": "apply" if apply else "preview",
        "origin": safe_remote(origin),
        "current_branch": branch,
        "stable_branch": stable,
        "local_profile_source": employee_id_source,
        "dirty": bool(status),
        "incoming_commits": incoming,
        "incoming_files": changed,
        "local_private_hash_unchanged": True,
    }
    if not apply:
        if private_manifest(root, employee_id) != before:
            raise ValueError("Local Private content changed during update preview")
        result["next"] = "Review the preview, clean the stable branch, then run update.cmd --apply"
        return result
    if status:
        raise ValueError("working tree is not clean; update never auto-stashes or resets")
    if branch != stable:
        raise ValueError(f"apply is allowed only on stable branch {stable}")
    counts = checked(root, "rev-list", "--left-right", "--count", f"{branch}...origin/{stable}").split()
    if len(counts) != 2 or int(counts[0]) > 0:
        raise ValueError("local stable branch has unpushed or diverged commits; use a reviewed branch or fresh clone")
    checked(root, "pull", "--ff-only", "origin", stable)
    call(root, sys.executable, str(root / "scripts" / "harness_sync.py"), "verify", "--root", str(root))
    preview = guide_update_preview(root, employee_id)
    result["guide_preview"] = preview
    if confirm_guide_release:
        result["guide_apply"] = guide_update_apply(root, employee_id, confirm_guide_release)
    call(
        root,
        "powershell.exe",
        "-NoLogo",
        "-NoProfile",
        "-ExecutionPolicy",
        "RemoteSigned",
        "-File",
        str(root / "check.ps1"),
    )
    after = private_manifest(root, employee_id)
    if after != before:
        raise ValueError("Local Private content changed during update; compare with backup before retrying")
    result["local_private_hash_unchanged"] = True
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--confirm-guide-release", default="")
    args = parser.parse_args()
    try:
        payload = update(Path(args.root).resolve(), args.apply, args.confirm_guide_release)
    except (OSError, ValueError) as exc:
        payload = {"ok": False, "error": str(exc)}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
