#!/usr/bin/env python3
"""Capture a local work note as a private BoI Markdown candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

KST = timezone(timedelta(hours=9))


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip().lower()).strip("-")
    return slug[:80] or "local-capture"


def employee_id_from_env(raw: str | None) -> str:
    employee_id = raw or os.getenv("BOI_LOCAL_EMPLOYEE_ID") or "0000000"
    if not re.fullmatch(r"[0-9]{7}", employee_id):
        raise SystemExit("BOI_LOCAL_EMPLOYEE_ID must be a numeric 7-digit employee ID")
    return employee_id


def private_root(root: Path, employee_id: str) -> Path:
    return root / "data" / "boi" / "private" / employee_id


def check_workspace(root: Path, employee_id: str) -> dict[str, object]:
    base = private_root(root, employee_id)
    required = [base / "notes", base / "promotion-drafts", base / "reports"]
    missing = [str(path.relative_to(root)) for path in required if not path.exists()]
    return {"ok": not missing, "employee_id": employee_id, "missing": missing}


def markdown_doc(employee_id: str, title: str, body: str, source: str, kind: str) -> str:
    now = datetime.now(KST)
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()[:12]
    review_after = (now + timedelta(days=30)).date().isoformat()
    metadata = f"""---
okf_version: "0.1"
boi_profile_version: "0.1"
type: boi/local-capture
title: {json.dumps(title, ensure_ascii=False)}
description: {json.dumps("Local Private capture candidate", ensure_ascii=False)}
tags: [LocalPrivate, SecondBrain, Capture]
timestamp: {now.isoformat()}
boi_id: boi:private:{employee_id}:capture:{now.strftime('%Y%m%d%H%M%S')}:{digest}
visibility: private
classification: internal
owner: "{employee_id}"
employee_id: "{employee_id}"
local_owner_ref: local-private:{employee_id}
promotion_status: local_only
artifact_visibility: working
lifecycle_state: working
memory_candidate: true
cleanup_policy: keep
retention_class: working_note
review_after: {review_after}
source_refs:
  - type: local-capture
    ref: {json.dumps(source or kind, ensure_ascii=False)}
review:
  reviewer: local-owner
  review_status: draft
---
"""
    return metadata + "\n# Summary\n\n" + body.strip() + "\n\n# Review Checklist\n\n- Keep as working note, mark as memory, archive, or create a promotion draft.\n- Do not send raw local content to remote BoI Wiki without explicit approval.\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--employee-id", default="")
    parser.add_argument("--title", default="Local capture")
    parser.add_argument("--source", default="")
    parser.add_argument("--kind", default="note")
    parser.add_argument("--body", default="")
    parser.add_argument("--file", default="")
    parser.add_argument("--stdin", action="store_true")
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
        print(json.dumps(check, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    body = args.body
    if args.file:
        body = Path(args.file).read_text(encoding="utf-8")
    elif args.stdin:
        body = sys.stdin.read()
    if not body.strip():
        raise SystemExit("capture body is required")
    target_dir = private_root(root, employee_id) / "notes" / "capture-inbox"
    filename = f"{datetime.now(KST).strftime('%Y%m%d-%H%M%S')}-{slugify(args.title)}.md"
    target = target_dir / filename
    result = {"ok": True, "employee_id": employee_id, "path": str(target.relative_to(root)), "dry_run": args.dry_run}
    if args.dry_run:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    target_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(markdown_doc(employee_id, args.title, body, args.source, args.kind), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
