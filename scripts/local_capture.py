#!/usr/bin/env python3
"""Capture an immutable Local Private source note."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from boi_local_common import (
    SOURCE_END,
    SOURCE_START,
    append_index_link,
    append_log,
    atomic_write,
    workspace_employee_id,
    local_frontmatter,
    normalize_text,
    now_kst,
    private_root,
    relative_to_root,
    sha256_text,
    slugify,
)


def check_workspace(root: Path, employee_id: str) -> dict[str, object]:
    base = private_root(root, employee_id)
    required = [base / "notes", base / "promotion-drafts", base / "reports"]
    missing = [relative_to_root(root, path) for path in required if not path.exists()]
    return {"ok": not missing, "employee_id": employee_id, "missing": missing}


def markdown_doc(employee_id: str, title: str, body: str, source: str, kind: str) -> str:
    current = now_kst()
    normalized = normalize_text(body)
    digest = sha256_text(normalized)
    frontmatter = local_frontmatter(
        employee_id=employee_id,
        doc_type="boi/local-capture",
        title=title,
        description="수정하지 않고 보존하는 Local Private 원문 수집 자료",
        boi_id=f"boi:private:{employee_id}:capture:{current.strftime('%Y%m%d%H%M%S')}:{digest[:12]}",
        tags=["LocalPrivate", "SecondBrain", "Capture"],
        source_refs=[{"type": "local-capture", "ref": source or kind}],
        timestamp=current,
        retention_class="working",
        memory_candidate=True,
        extra={
            "capture_kind": kind,
            "source_sha256": digest,
            "source_hash_scope": "captured_source_section",
            "source_immutability": "locked",
        },
    )
    return (
        frontmatter
        + "\n# 수집 원문\n\n"
        + SOURCE_START
        + "\n"
        + normalized
        + "\n"
        + SOURCE_END
        + "\n\n# 다음 작업\n\n"
        + "- 원문은 직접 고치지 않습니다. 수정이 필요하면 새 원문을 수집합니다.\n"
        + "- 정제할 때는 `local_distill.py` 또는 에이전트에게 정제를 요청합니다.\n"
        + "- 원격 공유 전에는 별도의 promotion 초안과 미리보기가 필요합니다.\n"
    )


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
    try:
        employee_id, _ = workspace_employee_id(root, args.employee_id)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
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

    current = now_kst()
    target_dir = private_root(root, employee_id) / "notes" / "capture-inbox"
    filename = f"{current.strftime('%Y%m%d-%H%M%S')}-{slugify(args.title)}.md"
    target = target_dir / filename
    result = {
        "ok": True,
        "employee_id": employee_id,
        "path": relative_to_root(root, target),
        "source_sha256": sha256_text(body),
        "dry_run": args.dry_run,
    }
    if args.dry_run:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    atomic_write(target, markdown_doc(employee_id, args.title, body, args.source, args.kind))
    append_index_link(target_dir / "index.md", args.title, filename)
    append_log(root, f"수집 원문 생성: [{args.title}]({relative_to_root(root, target)})")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
