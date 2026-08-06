#!/usr/bin/env python3
"""Fail a repository contribution that appears to include Local Private data or secrets."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

PRIVATE_PROFILE_RE = re.compile(r"^data/boi/private/(\d{7})/")
ACCEPTANCE_SCHEMA_RE = re.compile(r'"schema"\s*:\s*"boi-local-release-acceptance/v[0-9]+"')
ACCEPTANCE_EXAMPLE = "research/release-acceptance-evidence.example.json"
SECRET_PATTERNS = [
    ("PAT assignment", re.compile(r"(?im)^\s*(?:BOI_WIKI_PAT|BITBUCKET_TOKEN|API_KEY)\s*=\s*[^\s<][^\r\n]*$")),
    ("private key", re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----")),
    ("credentialed URL", re.compile(r"(?:https?|ssh)://[^/\s:@]+:[^/\s@]+@")),
]


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def candidate_paths(root: Path, staged: bool, all_files: bool) -> list[str]:
    if all_files:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise ValueError(result.stderr.decode("utf-8", errors="replace").strip())
        return sorted({item.decode("utf-8", errors="surrogateescape") for item in result.stdout.split(b"\0") if item})
    args = ("diff", "--cached", "--name-only", "--diff-filter=ACMR") if staged else (
        "status", "--porcelain=v1", "--untracked-files=all"
    )
    result = git(root, *args)
    if result.returncode != 0:
        raise ValueError((result.stderr or result.stdout).strip())
    if staged:
        return sorted({line.strip() for line in result.stdout.splitlines() if line.strip()})
    paths = []
    for line in result.stdout.splitlines():
        value = line[3:].strip()
        if " -> " in value:
            value = value.split(" -> ", 1)[1]
        if value:
            paths.append(value.strip('"'))
    return sorted(set(paths))


def inspect(root: Path, staged: bool, all_files: bool = False) -> dict[str, object]:
    errors: list[dict[str, str]] = []
    paths = candidate_paths(root, staged, all_files)
    for relative in paths:
        normalized = relative.replace("\\", "/")
        parts = normalized.split("/")
        if normalized == ".env" or ".obsidian" in parts:
            errors.append({"path": normalized, "issue": "private environment or Obsidian state must not be contributed"})
        profile = PRIVATE_PROFILE_RE.match(normalized)
        if profile and profile.group(1) != "0000000":
            errors.append({"path": normalized, "issue": "real Local Private profile must use promotion, not Git PR"})
        path = root / relative
        if not path.is_file() or path.stat().st_size > 2_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if normalized.lower().endswith(".json") and ACCEPTANCE_SCHEMA_RE.search(text) and normalized != ACCEPTANCE_EXAMPLE:
            errors.append({"path": normalized, "issue": "pilot acceptance evidence must remain outside the repository"})
        for label, pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append({"path": normalized, "issue": label})
    mode = "release-candidate" if all_files else ("staged" if staged else "working-tree")
    return {"ok": not errors, "mode": mode, "checked": paths, "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--staged", action="store_true")
    mode.add_argument("--all", action="store_true", dest="all_files", help="inspect the complete tracked and unignored release candidate")
    args = parser.parse_args()
    try:
        payload = inspect(Path(args.root).resolve(), args.staged, args.all_files)
    except ValueError as exc:
        payload = {"ok": False, "errors": [{"path": "git", "issue": str(exc)}]}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
