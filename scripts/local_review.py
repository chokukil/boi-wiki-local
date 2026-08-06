#!/usr/bin/env python3
"""Review Local Private Second Brain lifecycle candidates."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

from boi_local_common import parse_frontmatter, verify_locked_source, workspace_employee_id


def item_for(root: Path, path: Path, meta: dict[str, str], reason: str) -> dict[str, str]:
    return {
        "path": str(path.relative_to(root)),
        "title": meta.get("title", path.stem),
        "boi_id": meta.get("boi_id", ""),
        "lifecycle_state": meta.get("lifecycle_state", ""),
        "artifact_visibility": meta.get("artifact_visibility", ""),
        "promotion_status": meta.get("promotion_status", ""),
        "review_after": meta.get("review_after", ""),
        "reason": reason,
    }


def review(root: Path, employee_id: str) -> dict[str, object]:
    base = root / "data" / "boi" / "private" / employee_id
    if not base.exists():
        return {"ok": False, "employee_id": employee_id, "error": f"missing private root: {base}"}
    today = date.today().isoformat()
    stale = []
    memory_candidates = []
    promotion_candidates = []
    cleanup_candidates = []
    protected = []
    integrity_failures = []
    by_title: dict[str, list[dict[str, str]]] = defaultdict(list)
    for path in sorted(base.rglob("*.md")):
        if "_archive" in path.relative_to(base).parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        meta = parse_frontmatter(text)
        integrity_ok, integrity_message = verify_locked_source(text, meta)
        if not integrity_ok:
            integrity_failures.append(item_for(root, path, meta, integrity_message))
        lifecycle = meta.get("lifecycle_state", "")
        visibility = meta.get("artifact_visibility", "")
        title_key = re.sub(r"\s+", " ", meta.get("title", path.stem).lower()).strip()
        if path.name != "index.md":
            by_title[title_key].append(item_for(root, path, meta, "same_title"))
        if lifecycle in {"memory", "working", "protected"} or visibility == "memory":
            protected.append(item_for(root, path, meta, "protected_or_working"))
        review_after = meta.get("review_after", "")
        if review_after and review_after < today and lifecycle not in {"memory", "protected"}:
            stale.append(item_for(root, path, meta, "review_after_elapsed"))
        if meta.get("memory_candidate", "").lower() == "true" or lifecycle == "working":
            memory_candidates.append(item_for(root, path, meta, "memory_candidate"))
        if "promotion-drafts" in path.parts or meta.get("promotion_status") in {"pending_user_approval", "promotion_ready"}:
            promotion_candidates.append(item_for(root, path, meta, "promotion_candidate"))
        if lifecycle in {"background", "archived", "delete_candidate"}:
            cleanup_candidates.append(item_for(root, path, meta, "generated_cleanup_candidate"))
    duplicates = [items for key, items in by_title.items() if key and len(items) > 1]
    return {
        "ok": True,
        "employee_id": employee_id,
        "summary": {
            "stale_count": len(stale),
            "duplicate_group_count": len(duplicates),
            "memory_candidate_count": len(memory_candidates),
            "promotion_candidate_count": len(promotion_candidates),
            "cleanup_candidate_count": len(cleanup_candidates),
            "protected_count": len(protected),
            "integrity_failure_count": len(integrity_failures),
        },
        "stale": stale[:50],
        "duplicate_groups": duplicates[:20],
        "memory_candidates": memory_candidates[:50],
        "promotion_candidates": promotion_candidates[:50],
        "cleanup_candidates": cleanup_candidates[:50],
        "protected": protected[:50],
        "integrity_failures": integrity_failures[:50],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--employee-id", default="")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    try:
        employee_id, _ = workspace_employee_id(root, args.employee_id)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    payload = review(root, employee_id)
    payload["check_ok"] = bool(payload.get("ok")) and not payload.get("integrity_failures")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.check:
        return 0 if payload["check_ok"] else 1
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
