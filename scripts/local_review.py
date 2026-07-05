#!/usr/bin/env python3
"""Review Local Private Second Brain lifecycle candidates."""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import defaultdict
from datetime import date
from pathlib import Path


def employee_id_from_env(raw: str | None) -> str:
    employee_id = raw or os.getenv("BOI_LOCAL_EMPLOYEE_ID") or "0000000"
    if not re.fullmatch(r"[0-9]{7}", employee_id):
        raise SystemExit("BOI_LOCAL_EMPLOYEE_ID must be a numeric 7-digit employee ID")
    return employee_id


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    meta: dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" not in line or line.startswith(" "):
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"')
    return meta


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
    by_title: dict[str, list[dict[str, str]]] = defaultdict(list)
    for path in sorted(base.rglob("*.md")):
        meta = parse_frontmatter(path)
        lifecycle = meta.get("lifecycle_state", "")
        visibility = meta.get("artifact_visibility", "")
        title_key = re.sub(r"\s+", " ", meta.get("title", path.stem).lower()).strip()
        by_title[title_key].append(item_for(root, path, meta, "same_title"))
        if lifecycle in {"memory", "working", "protected"} or visibility == "memory":
            protected.append(item_for(root, path, meta, "protected_or_working"))
        review_after = meta.get("review_after", "")
        if review_after and review_after < today and lifecycle not in {"memory", "protected"}:
            stale.append(item_for(root, path, meta, "review_after_elapsed"))
        if meta.get("memory_candidate", "").lower() == "true" or lifecycle == "working":
            memory_candidates.append(item_for(root, path, meta, "memory_candidate"))
        if "promotion-drafts" in str(path) or meta.get("promotion_status") in {"pending_user_approval", "local_only"}:
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
        },
        "stale": stale[:50],
        "duplicate_groups": duplicates[:20],
        "memory_candidates": memory_candidates[:50],
        "promotion_candidates": promotion_candidates[:50],
        "cleanup_candidates": cleanup_candidates[:50],
        "protected": protected[:50],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--employee-id", default="")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    employee_id = employee_id_from_env(args.employee_id)
    payload = review(root, employee_id)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
