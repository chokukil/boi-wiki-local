#!/usr/bin/env python3
"""Create a local promotion preflight draft from a private BoI Markdown file."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

KST = timezone(timedelta(hours=9))
SECRET_RE = re.compile(r"(password|secret|token|api[_ -]?key)\s*[:=]\s*['\"]?[^\\s,'\"]+", re.IGNORECASE)


def employee_id_from_env(raw: str | None) -> str:
    employee_id = raw or os.getenv("BOI_LOCAL_EMPLOYEE_ID") or "0000000"
    if not re.fullmatch(r"[0-9]{7}", employee_id):
        raise SystemExit("BOI_LOCAL_EMPLOYEE_ID must be a numeric 7-digit employee ID")
    return employee_id


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip().lower()).strip("-")
    return slug[:80] or "promotion-preflight"


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta: dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" not in line or line.startswith(" "):
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"')
    return meta, parts[2].lstrip()


def check_workspace(root: Path, employee_id: str) -> dict[str, object]:
    base = root / "data" / "boi" / "private" / employee_id
    required = [base / "promotion-drafts", base / "notes"]
    missing = [str(path.relative_to(root)) for path in required if not path.exists()]
    return {"ok": not missing, "employee_id": employee_id, "missing": missing}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--employee-id", default="")
    parser.add_argument("--source", default="")
    parser.add_argument("--target-visibility", choices=["team", "public"], default="team")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    employee_id = employee_id_from_env(args.employee_id)
    check = check_workspace(root, employee_id)
    if args.check:
        print(json.dumps(check, ensure_ascii=False, indent=2))
        return 0 if check["ok"] else 1
    if not check["ok"]:
        print(json.dumps(check, ensure_ascii=False, indent=2))
        return 1
    if not args.source:
        raise SystemExit("--source is required")
    source_path = (root / args.source).resolve()
    source_path.relative_to(root)
    text = source_path.read_text(encoding="utf-8")
    meta, body = split_frontmatter(text)
    title = meta.get("title") or source_path.stem
    source_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    findings = []
    if SECRET_RE.search(text):
        findings.append("potential secret-like value")
    if not meta.get("source_refs"):
        findings.append("source_refs should be reviewed before remote submit")
    now = datetime.now(KST)
    target_dir = root / "data" / "boi" / "private" / employee_id / "promotion-drafts"
    filename = f"{now.strftime('%Y%m%d-%H%M%S')}-{slugify(title)}-{args.target_visibility}-preflight.md"
    target = target_dir / filename
    report = f"""---
okf_version: "0.1"
boi_profile_version: "0.1"
type: boi/local-promotion-draft
title: {json.dumps(title + " promotion preflight", ensure_ascii=False)}
description: "Local preflight before remote BoI Wiki promotion"
tags: [LocalPrivate, Promotion, Preflight]
timestamp: {now.isoformat()}
boi_id: boi:private:{employee_id}:promotion-preflight:{now.strftime('%Y%m%d%H%M%S')}:{source_sha[:8]}
visibility: private
classification: internal
owner: "{employee_id}"
employee_id: "{employee_id}"
local_owner_ref: local-private:{employee_id}
promotion_status: pending_user_approval
artifact_visibility: working
lifecycle_state: protected
cleanup_policy: keep
review_after: {(now + timedelta(days=14)).date().isoformat()}
source_refs:
  - type: local-private
    ref: {json.dumps(str(source_path.relative_to(root)), ensure_ascii=False)}
    sha256: {source_sha}
review:
  reviewer: local-owner
  review_status: preflight
---

# Preview Summary

- Target visibility: `{args.target_visibility}`
- Source path: `{source_path.relative_to(root)}`
- Source SHA256: `{source_sha}`
- Findings: `{", ".join(findings) if findings else "none"}`

# Sanitized Candidate

{body.strip()}

# Remote Submit Boundary

Do not call remote `promotion_submit` until the user explicitly approves this preview.
"""
    result = {"ok": not findings, "path": str(target.relative_to(root)), "findings": findings, "dry_run": args.dry_run}
    if args.dry_run:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    target_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(report, encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
