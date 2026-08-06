#!/usr/bin/env python3
"""Create a derived Local Private knowledge note without changing its source."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

from boi_local_common import (
    append_index_link,
    append_log,
    atomic_write,
    workspace_employee_id,
    local_frontmatter,
    normalize_text,
    now_kst,
    parse_frontmatter,
    private_root,
    relative_to_root,
    require_private_path,
    sha256_text,
    slugify,
    verify_locked_source,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--employee-id", default="")
    parser.add_argument("--source", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--description", default="원문에서 정제한 Local Private 지식 문서")
    parser.add_argument("--body", default="")
    parser.add_argument("--file", default="")
    parser.add_argument("--stdin", action="store_true")
    parser.add_argument("--memory", action="store_true")
    parser.add_argument(
        "--contains-sensitive",
        choices=["true", "false", "unknown"],
        default="unknown",
        help="Record the human/agent sensitivity review result in the Local Profile.",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    try:
        employee_id, _ = workspace_employee_id(root, args.employee_id)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    source_path = require_private_path(root, employee_id, root / args.source)
    if not source_path.is_file():
        raise SystemExit(f"source does not exist: {source_path}")
    source_bytes_before = source_path.read_bytes()
    source_text = source_bytes_before.decode("utf-8")
    source_meta = parse_frontmatter(source_text)
    locked_ok, locked_message = verify_locked_source(source_text, source_meta)
    if not locked_ok:
        raise SystemExit(f"source integrity check failed: {locked_message}")

    body = args.body
    if args.file:
        body = Path(args.file).read_text(encoding="utf-8")
    elif args.stdin:
        body = sys.stdin.read()
    body = normalize_text(body)
    if not body:
        raise SystemExit("distilled body is required")

    current = now_kst()
    digest = sha256_text(body)
    target_dir = private_root(root, employee_id) / "notes" / "knowledge"
    filename = f"{current.strftime('%Y%m%d-%H%M%S')}-{slugify(args.title)}.md"
    target = target_dir / filename
    source_rel = relative_to_root(root, source_path)
    source_hash = hashlib.sha256(source_bytes_before).hexdigest()
    target_rel = relative_to_root(root, target)
    link = os.path.relpath(source_path, target.parent).replace(os.sep, "/")
    frontmatter = local_frontmatter(
        employee_id=employee_id,
        doc_type="boi/local-knowledge-note",
        title=args.title,
        description=args.description,
        boi_id=f"boi:private:{employee_id}:knowledge:{current.strftime('%Y%m%d%H%M%S')}:{digest[:12]}",
        tags=["LocalPrivate", "SecondBrain", "Distilled"],
        source_refs=[
            {
                "type": "local-private",
                "ref": source_rel,
                "sha256": source_hash,
            }
        ],
        timestamp=current,
        retention_class="working",
        artifact_visibility="memory" if args.memory else "working",
        lifecycle_state="memory" if args.memory else "working",
        memory_candidate=not args.memory,
        contains_sensitive=args.contains_sensitive,
        generated_from=[
            {
                "type": "local-document",
                "ref": source_rel,
                "sha256": source_hash,
            }
        ],
    )
    document = (
        frontmatter
        + "\n# 정제한 지식\n\n"
        + body
        + "\n\n# 근거\n\n"
        + f"- [원문]({link})\n"
        + f"- 원문 무결성: `{locked_message}`\n"
    )
    result = {
        "ok": True,
        "employee_id": employee_id,
        "source": source_rel,
        "path": target_rel,
        "source_unchanged": True,
        "dry_run": args.dry_run,
    }
    if args.dry_run:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    atomic_write(target, document)
    if source_path.read_bytes() != source_bytes_before:
        target.unlink(missing_ok=True)
        raise SystemExit("source changed during distillation; derived document was removed")
    append_index_link(target_dir / "index.md", args.title, filename)
    append_log(root, f"지식 문서 정제: [{args.title}]({target_rel}), 원문 `{source_rel}`")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
