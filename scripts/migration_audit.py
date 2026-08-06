#!/usr/bin/env python3
"""Audit preservation of a WSL working tree in an evolved Windows-native release tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


REAL_PROFILE = re.compile(r"^data/boi/private/(\d{7})/")


def git_bytes(root: Path, *args: str) -> bytes:
    safe = str(root).replace("\\", "/")
    completed = subprocess.run(
        ["git", "-c", f"safe.directory={safe}", "-C", str(root), *args],
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise ValueError(completed.stderr.decode("utf-8", errors="replace").strip())
    return completed.stdout


def nul_paths(root: Path, *args: str) -> list[str]:
    return sorted(
        {
            item.decode("utf-8", errors="surrogateescape")
            for item in git_bytes(root, *args).split(b"\0")
            if item
        }
    )


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def audit(source: Path, target: Path) -> dict[str, object]:
    source = source.resolve()
    target = target.resolve()
    source_head = git_bytes(source, "rev-parse", "HEAD").decode("ascii").strip()
    target_head = git_bytes(target, "rev-parse", "HEAD").decode("ascii").strip()
    candidates = nul_paths(source, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    changed = set(nul_paths(source, "diff", "--name-only", "-z", "HEAD"))
    changed.update(nul_paths(source, "ls-files", "-z", "--others", "--exclude-standard"))
    forbidden: list[str] = []
    missing: list[str] = []
    type_mismatch: list[str] = []
    ledger: list[dict[str, object]] = []
    changed_rows: list[dict[str, str]] = []

    for relative in candidates:
        normalized = relative.replace("\\", "/")
        profile = REAL_PROFILE.match(normalized)
        parts = normalized.split("/")
        if normalized == ".env" or ".obsidian" in parts or (profile and profile.group(1) != "0000000"):
            forbidden.append(normalized)
        source_path = source / relative
        target_path = target / relative
        if not source_path.exists():
            if target_path.exists():
                missing.append(normalized + " (source deletion not preserved)")
            continue
        if not target_path.exists():
            missing.append(normalized)
            continue
        if source_path.is_file() != target_path.is_file():
            type_mismatch.append(normalized)
            continue
        if not source_path.is_file():
            continue
        source_sha = digest(source_path)
        target_sha = digest(target_path)
        ledger.append({"path": normalized, "sha256": source_sha, "bytes": source_path.stat().st_size})
        if normalized in changed:
            changed_rows.append(
                {
                    "path": normalized,
                    "status": "exact" if source_sha == target_sha else "evolved-in-windows",
                    "source_sha256": source_sha,
                    "target_sha256": target_sha,
                }
            )

    serialized_ledger = json.dumps(ledger, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    exact = sum(item["status"] == "exact" for item in changed_rows)
    evolved = sum(item["status"] == "evolved-in-windows" for item in changed_rows)
    ok = source_head == target_head and not missing and not type_mismatch and not forbidden and source.exists()
    return {
        "ok": ok,
        "schema": "boi-local-wsl-migration-audit/v1",
        "source_preserved": source.exists(),
        "source_head": source_head,
        "target_head": target_head,
        "common_base_head": source_head == target_head,
        "source_candidate_file_count": len(ledger),
        "source_changed_file_count": len(changed_rows),
        "changed_exact_count": exact,
        "changed_evolved_in_windows_count": evolved,
        "missing_in_windows_target": missing,
        "type_mismatches": type_mismatch,
        "forbidden_private_candidates": forbidden,
        "source_hash_ledger_sha256": hashlib.sha256(serialized_ledger).hexdigest(),
        "evolved_files": [item["path"] for item in changed_rows if item["status"] == "evolved-in-windows"],
        "proof_scope": "Current WSL release-candidate inventory is present in Windows; exact files match by SHA256 and evolved files remain recoverable from the preserved WSL rollback tree.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--target", default=".")
    args = parser.parse_args()
    try:
        payload = audit(Path(args.source), Path(args.target))
    except (OSError, ValueError) as exc:
        payload = {"ok": False, "schema": "boi-local-wsl-migration-audit/v1", "error": str(exc)}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
