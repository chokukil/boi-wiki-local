#!/usr/bin/env python3
"""Search Local Private Markdown with path-backed citations."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from boi_local_common import parse_frontmatter, private_root, relative_to_root, split_frontmatter, workspace_employee_id


def tokens(query: str) -> list[str]:
    return [item.lower() for item in re.findall(r"[0-9A-Za-z가-힣_-]+", query) if len(item) > 1]


def first_matching_line(text: str, terms: list[str]) -> tuple[int, str]:
    lines = text.splitlines()
    for number, line in enumerate(lines, 1):
        lowered = line.lower()
        if any(term in lowered for term in terms):
            return number, re.sub(r"\s+", " ", line).strip()[:240]
    return 1, re.sub(r"\s+", " ", text).strip()[:240]


def search(root: Path, employee_id: str, query: str, limit: int, *, include_archive: bool = False) -> list[dict[str, object]]:
    terms = tokens(query)
    if not terms:
        raise ValueError("query must contain at least one searchable term")
    base = private_root(root, employee_id)
    results: list[dict[str, object]] = []
    for path in sorted(base.rglob("*.md")):
        if ".obsidian" in path.parts:
            continue
        relative_parts = path.relative_to(base).parts
        archived = "_archive" in relative_parts
        if archived and not include_archive:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        meta = parse_frontmatter(text)
        _, body = split_frontmatter(text)
        title = meta.get("title", path.stem)
        title_lower = title.lower()
        body_lower = body.lower()
        path_lower = path.as_posix().lower()
        matched = [term for term in terms if term in title_lower or term in body_lower or term in path_lower]
        if not matched:
            continue
        score = sum(8 for term in terms if term in title_lower)
        score += sum(3 for term in terms if term in path_lower)
        score += sum(min(body_lower.count(term), 5) for term in terms)
        line, snippet = first_matching_line(body, matched)
        results.append(
            {
                "score": score,
                "title": title,
                "path": relative_to_root(root, path),
                "line": line,
                "snippet": snippet,
                "matched_terms": matched,
                "boi_id": meta.get("boi_id", ""),
                "archived": archived,
            }
        )
    return sorted(results, key=lambda item: (-int(item["score"]), str(item["path"])))[:limit]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    parser.add_argument("--root", default=".")
    parser.add_argument("--employee-id", default="")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--include-archive", action="store_true", help="include archived snapshots in results")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    try:
        employee_id, _ = workspace_employee_id(root, args.employee_id)
        results = search(root, employee_id, args.query, max(1, args.limit), include_archive=args.include_archive)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    payload = {
        "ok": True,
        "query": args.query,
        "employee_id": employee_id,
        "include_archive": args.include_archive,
        "count": len(results),
        "results": results,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif not results:
        print("검색 결과가 없습니다.")
    else:
        for item in results:
            print(f"- {item['title']} — {item['path']}:{item['line']}")
            print(f"  {item['snippet']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
