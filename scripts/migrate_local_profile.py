#!/usr/bin/env python3
"""Preview or apply additive Local Private profile metadata migration."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from boi_local_common import parse_frontmatter, private_root, relative_to_root, slugify, split_frontmatter, workspace_employee_id

ADDITIVE_FIELDS = (
    "boi_id",
    "classification",
    "owner",
    "artifact_visibility",
    "lifecycle_state",
    "memory_candidate",
    "cleanup_policy",
)


def values_for(employee_id: str, path: Path, text: str) -> dict[str, str]:
    relative = path.as_posix()
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:10]
    protected = "promotion-drafts" in path.parts
    return {
        "boi_id": f"boi:private:{employee_id}:legacy:{slugify(path.stem)}:{digest}",
        "classification": "internal",
        "owner": f'"{employee_id}"',
        "artifact_visibility": "working",
        "lifecycle_state": "protected" if protected else "working",
        "memory_candidate": "false",
        "cleanup_policy": "keep",
    }


def migrated_text(employee_id: str, path: Path, text: str) -> tuple[str, list[str]]:
    header, body = split_frontmatter(text)
    if not header:
        return text, []
    meta = parse_frontmatter(text)
    values = values_for(employee_id, path, text)
    missing = [field for field in ADDITIVE_FIELDS if field not in meta]
    if not missing:
        return text, []
    lines = header.splitlines()
    insert_at = next((index + 1 for index, line in enumerate(lines) if line.startswith("description:")), len(lines))
    additions = [f"{field}: {values[field]}" for field in missing]
    lines[insert_at:insert_at] = additions
    return "---\n" + "\n".join(lines) + "\n---\n" + body, missing


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--employee-id", default="")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--allow-template", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    try:
        employee_id, _ = workspace_employee_id(root, args.employee_id, allow_template=args.allow_template)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    base = private_root(root, employee_id)
    changes = []
    for path in sorted(base.rglob("*.md")):
        if path.name == "index.md" or path == base / "inbox.md" or ".obsidian" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        updated, fields = migrated_text(employee_id, path, text)
        if not fields:
            continue
        changes.append({"path": relative_to_root(root, path), "add_fields": fields})
        if args.apply:
            path.write_text(updated, encoding="utf-8", newline="\n")
    print(json.dumps({"ok": True, "employee_id": employee_id, "mode": "apply" if args.apply else "preview", "change_count": len(changes), "changes": changes}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
