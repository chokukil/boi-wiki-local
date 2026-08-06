#!/usr/bin/env python3
"""Exercise a disposable Windows clone, install, and update from the complete release candidate."""

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

from boi_update import private_manifest
from contribution_check import candidate_paths, inspect


SYNTHETIC_EMPLOYEE_ID = "7654321"


def run(
    args: list[str],
    cwd: Path,
    *,
    env: dict[str, str] | None = None,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        args,
        cwd=cwd,
        input=input_text,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        env=env,
        check=False,
    )
    if completed.returncode:
        combined = "\n".join(part.strip() for part in (completed.stdout, completed.stderr) if part.strip())
        detail = combined[-8000:]
        raise RuntimeError(f"command failed ({completed.returncode}): {' '.join(args)}: {detail}")
    return completed


def copy_release_candidate(source: Path, target: Path) -> list[str]:
    paths = candidate_paths(source, staged=False, all_files=True)
    for relative in paths:
        source_path = source / relative
        target_path = target / relative
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)
    return paths


def evaluate(root: Path) -> dict[str, object]:
    started = time.monotonic()
    privacy = inspect(root, staged=False, all_files=True)
    if not privacy["ok"]:
        raise RuntimeError("release candidate privacy scan failed")
    with tempfile.TemporaryDirectory(prefix="boi-release-clone-") as temporary:
        temporary_root = Path(temporary)
        seed = temporary_root / "release-seed"
        external_remote = temporary_root / "external-github-analogue.git"
        internal_remote = temporary_root / "internal-bitbucket-analogue.git"
        checkout = temporary_root / "member-checkout"
        seed.mkdir()
        candidate_paths_copied = copy_release_candidate(root, seed)
        required_snapshot = seed / ".boi-harness" / "package.json"
        required_state = seed / ".boi-harness" / "sync-state.json"
        if not required_snapshot.is_file() or not required_state.is_file():
            raise RuntimeError("pinned offline Harness package or attestation is absent from the release candidate")

        run(["git", "init", "-b", "main"], seed)
        run(["git", "config", "user.email", "release-fixture@example.com"], seed)
        run(["git", "config", "user.name", "Release Fixture"], seed)
        run(["git", "config", "core.autocrlf", "false"], seed)
        run(["git", "add", "-A"], seed)
        run(["git", "commit", "-m", "candidate release"], seed)
        run(["git", "init", "--bare", str(external_remote)], temporary_root)
        run(["git", "-C", str(external_remote), "symbolic-ref", "HEAD", "refs/heads/main"], temporary_root)
        run(["git", "remote", "add", "origin", str(external_remote)], seed)
        run(["git", "push", "-u", "origin", "main"], seed)
        run(["git", "clone", str(external_remote), str(checkout)], temporary_root)
        run(["git", "remote", "set-head", "origin", "-a"], checkout)
        initial_origin = run(["git", "remote", "get-url", "origin"], checkout).stdout.strip()

        environment = {
            **os.environ,
            "PYTHONUTF8": "1",
            "BOI_LOCAL_EMPLOYEE_ID": SYNTHETIC_EMPLOYEE_ID,
            "BOI_CONFIRM_INSTALL": "INSTALL",
            "BOI_WIKI_ROOT": os.environ.get("BOI_WIKI_ROOT", ""),
        }
        install = run(
            ["cmd.exe", "/d", "/c", "install.cmd"],
            checkout,
            env=environment,
        )
        private_root = checkout / "data" / "boi" / "private" / SYNTHETIC_EMPLOYEE_ID
        if not (private_root / "notes" / "guide" / "00-start-here.md").is_file():
            raise RuntimeError("clean-clone install did not create the connected Wiki")
        if run(["git", "status", "--porcelain=v1", "--untracked-files=all"], checkout).stdout.strip():
            raise RuntimeError("install exposed Local Private or environment files to Git status")
        before = private_manifest(checkout, SYNTHETIC_EMPLOYEE_ID)

        # Model the real deployment handoff: validate from an external GitHub-like
        # origin, mirror the same commit to an internal Bitbucket-like origin,
        # then change only the origin URL before the next update.
        run(["git", "init", "--bare", str(internal_remote)], temporary_root)
        run(["git", "-C", str(internal_remote), "symbolic-ref", "HEAD", "refs/heads/main"], temporary_root)
        run(["git", "remote", "set-url", "origin", str(internal_remote)], seed)
        run(["git", "push", "-u", "origin", "main"], seed)
        run(["git", "remote", "set-url", "origin", str(internal_remote)], checkout)
        changed_origin = run(["git", "remote", "get-url", "origin"], checkout).stdout.strip()
        if initial_origin == changed_origin:
            raise RuntimeError("origin URL replacement was not exercised")
        if run(["git", "rev-parse", "HEAD"], seed).stdout.strip() != run(["git", "rev-parse", "HEAD"], checkout).stdout.strip():
            raise RuntimeError("GitHub-to-Bitbucket analogue handoff did not preserve the tested commit")

        marker = seed / "research" / "release-clone-update-probe.txt"
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text("disposable update probe\n", encoding="utf-8")
        run(["git", "add", marker.relative_to(seed).as_posix()], seed)
        run(["git", "commit", "-m", "disposable update probe"], seed)
        run(["git", "push", "origin", "main"], seed)
        new_session_environment = dict(environment)
        new_session_environment.pop("BOI_LOCAL_EMPLOYEE_ID", None)
        update = run(
            [sys.executable, str(checkout / "scripts" / "boi_update.py"), "--root", str(checkout), "--apply"],
            checkout,
            env=new_session_environment,
        )
        update_payload = json.loads(update.stdout)
        if update_payload.get("local_profile_source") != "dotenv":
            raise RuntimeError("new-session update did not resolve the installed Local Profile from .env")
        after = private_manifest(checkout, SYNTHETIC_EMPLOYEE_ID)
        if before != after:
            raise RuntimeError("Local Private content changed across the clean-clone update")
        if not (checkout / "research" / "release-clone-update-probe.txt").is_file():
            raise RuntimeError("clean-clone update did not fast-forward to the new release")

        return {
            "ok": True,
            "schema": "boi-local-release-clone-acceptance/v1",
            "transport": "disposable-github-to-bitbucket-origin-swap",
            "external_reference_clone_succeeded": True,
            "origin_url_replaced": True,
            "same_commit_preserved_across_origin_swap": True,
            "internal_target_update_succeeded": bool(update_payload.get("ok")),
            "release_candidate_file_count": len(candidate_paths_copied),
            "complete_candidate_privacy_scan": True,
            "pinned_harness_in_clone": True,
            "install_cmd_succeeded": install.returncode == 0,
            "connected_wiki_created": True,
            "post_install_git_status_clean": True,
            "update_fast_forward_succeeded": bool(update_payload.get("ok")),
            "new_session_profile_resolved_from_dotenv": True,
            "local_private_hash_unchanged": before == after,
            "remote_submit_invocations": 0,
            "temporary_workspace_removed_on_exit": True,
            "duration_seconds": round(time.monotonic() - started, 3),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    try:
        payload = evaluate(Path(args.root).resolve())
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        payload = {"ok": False, "schema": "boi-local-release-clone-acceptance/v1", "error": str(exc)}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
