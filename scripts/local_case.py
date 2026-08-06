#!/usr/bin/env python3
"""Create and maintain Local Private evidence-driven analysis cases."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from boi_local_common import (
    append_index_link,
    append_log,
    atomic_write,
    local_frontmatter,
    now_kst,
    parse_frontmatter,
    parse_frontmatter_list,
    private_root,
    relative_to_root,
    replace_frontmatter_list,
    workspace_employee_id,
)

CASE_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{2,63}")
HYPOTHESIS_RE = re.compile(r"H[0-9]{1,3}")
HYPOTHESIS_STATES = {"open", "supported", "weakened", "rejected", "closed"}
EVIDENCE_START = "<!-- boi-case-evidence:start -->"
EVIDENCE_END = "<!-- boi-case-evidence:end -->"


def pipe(values: list[str]) -> str:
    return "|".join(dict.fromkeys(value.strip() for value in values if value.strip()))


def case_dir(root: Path, employee_id: str, case_id: str) -> Path:
    return private_root(root, employee_id) / "cases" / case_id


def require_case_id(raw: str) -> str:
    value = raw.strip()
    if not CASE_RE.fullmatch(value):
        raise ValueError("case ID must use 3-64 letters, digits, dot, underscore, or hyphen")
    return value


def case_evidence(root: Path, employee_id: str, case_id: str) -> list[dict[str, str]]:
    base = private_root(root, employee_id)
    directory = base / "evidence" / case_id
    records: list[dict[str, str]] = []
    for path in sorted(directory.glob("*.md")) if directory.is_dir() else []:
        meta = parse_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        if meta.get("type") != "boi/local-evidence" or meta.get("case_id") != case_id:
            continue
        records.append(
            {
                "evidence_id": meta.get("evidence_id", ""),
                "evidence_type": meta.get("evidence_type", ""),
                "original_filename": meta.get("original_filename", path.name),
                "title": meta.get("title", path.stem),
                "path": relative_to_root(root, path),
                "filename": path.name,
            }
        )
    return sorted(records, key=lambda item: (item["original_filename"].lower(), item["evidence_id"]))


def refresh_case_hub_evidence(root: Path, employee_id: str, case_id: str) -> dict[str, object]:
    """Rebuild the Case Hub evidence catalog and structured OKF source_refs."""
    hub = case_dir(root, employee_id, case_id) / "case-hub.md"
    if not hub.is_file():
        raise FileNotFoundError(hub)
    text = hub.read_text(encoding="utf-8")
    records = case_evidence(root, employee_id, case_id)
    refs = [
        ref
        for ref in parse_frontmatter_list(text, "source_refs")
        if not str(ref.get("note", "")).startswith("case evidence ")
    ]
    refs.extend(
        {
            "type": "local-document",
            "ref": record["path"],
            "note": f"case evidence {record['evidence_id']}",
        }
        for record in records
    )
    text = replace_frontmatter_list(text, "source_refs", refs)
    lines = ["## Evidence Catalog", "", EVIDENCE_START]
    if records:
        lines.extend(
            f"- [{record['title']}](../../evidence/{case_id}/{record['filename']}) — "
            f"`{record['evidence_id']}` · `{record['evidence_type']}`"
            for record in records
        )
    else:
        lines.append("- 등록된 evidence가 없습니다.")
    lines.extend([EVIDENCE_END, ""])
    catalog = "\n".join(lines)
    pattern = re.compile(
        rf"(?ms)^## Evidence Catalog\n\n{re.escape(EVIDENCE_START)}.*?{re.escape(EVIDENCE_END)}\n?"
    )
    if pattern.search(text):
        text = pattern.sub(catalog, text, count=1)
    else:
        anchor = "## 가설과 반증"
        text = text.replace(anchor, catalog + "\n" + anchor, 1) if anchor in text else text.rstrip() + "\n\n" + catalog
    atomic_write(hub, text, overwrite=True)
    return {"path": relative_to_root(root, hub), "evidence_count": len(records)}


def create_case(root: Path, employee_id: str, args: argparse.Namespace) -> dict[str, object]:
    case_id = require_case_id(args.case_id)
    directory = case_dir(root, employee_id, case_id)
    hub = directory / "case-hub.md"
    if hub.exists():
        raise FileExistsError(hub)
    title = args.title.strip()
    question = args.question.strip()
    if not title or not question:
        raise ValueError("case title and investigation question are required")
    fm = local_frontmatter(
        employee_id=employee_id,
        doc_type="boi/local-analysis-case",
        title=title,
        description=question,
        boi_id=f"boi:private:{employee_id}:case:{case_id.lower()}",
        tags=["second-brain", "investigation", "case-hub", case_id.lower()],
        source_refs=[],
        memory_candidate=True,
        review_after_days=7,
        extra={
            "case_id": case_id,
            "knowledge_role": "case-hub",
            "claim_status": "open-question",
            "case_status": "investigating",
            "investigation_question": question,
            "most_supported_hypothesis": "unconfirmed",
            "decision_owner": "human-review-required",
        },
    )
    body = f"""
# {title}

> 합성 또는 승인된 Local 자료만 연결합니다. 원본 자료와 사람의 판정을 구분합니다.

## 조사 질문

{question}

## 관찰과 자료 신뢰성

- 최초 관찰:
- 출처와 수집 조건:
- 비교할 기준:

## 관련 흐름과 시간축

1. 사건 또는 요청의 시작
2. 관련 결정과 변경
3. 지지 근거와 경쟁 설명
4. 아직 확보하지 못한 자료
5. 다음 확인과 사람의 판단

## 가설과 반증

가설 문서는 `hypotheses/`에 두고 evidence ID로 지지·반증을 연결합니다.

## Evidence Catalog

<!-- boi-case-evidence:start -->
- 등록된 evidence가 없습니다.
<!-- boi-case-evidence:end -->

## 현재 판단

현재 근거로 가장 지지되는 기여 요인: **미확정**

- 반증:
- 누락 데이터:
- 추가 검증 조건:
- 사람의 판정:

## 재발 fingerprint

- 신호 조합:
- 제외 조건:
- review 주기:

## 공유 판단

Local 원문은 공유하지 않습니다. 재사용 가치가 있는 정제본만 promotion preview로 검토합니다.

관련 문서: [지속 분석 로그](analysis-log.md)
"""
    atomic_write(hub, fm + body)
    log = directory / "analysis-log.md"
    log_fm = local_frontmatter(
        employee_id=employee_id,
        doc_type="boi/local-analysis-log",
        title=f"{case_id} 지속 분석 로그",
        description="관찰·가설·판정 변경을 시간순으로 기록한다.",
        boi_id=f"boi:private:{employee_id}:case:{case_id.lower()}:analysis-log",
        tags=["second-brain", "analysis-log", case_id.lower()],
        source_refs=[{"type": "local-document", "ref": relative_to_root(root, hub), "note": "case hub"}],
        review_after_days=7,
        extra={"case_id": case_id, "knowledge_role": "continuous-log", "claim_status": "observed", "log_entry_count": 0},
    )
    atomic_write(log, log_fm + f"\n# {case_id} 지속 분석 로그\n\n")
    base = private_root(root, employee_id)
    append_index_link(base / "cases" / "index.md", title, f"{case_id}/case-hub.md")
    append_log(root, f"Local analysis case `{case_id}`를 생성함. 원격 전송 없음.")
    return {"ok": True, "case_id": case_id, "path": relative_to_root(root, hub), "analysis_log": relative_to_root(root, log), "remote_submitted": False}


def add_hypothesis(root: Path, employee_id: str, args: argparse.Namespace) -> dict[str, object]:
    case_id = require_case_id(args.case_id)
    hypothesis_id = args.hypothesis_id.strip().upper()
    if not HYPOTHESIS_RE.fullmatch(hypothesis_id):
        raise ValueError("hypothesis ID must look like H1 through H999")
    status = args.status.strip().lower()
    if status not in HYPOTHESIS_STATES:
        raise ValueError(f"unsupported hypothesis status: {status}")
    directory = case_dir(root, employee_id, case_id)
    hub = directory / "case-hub.md"
    if not hub.exists():
        raise FileNotFoundError(hub)
    supports = pipe(args.supports)
    contradicts = pipe(args.contradicts)
    path = directory / "hypotheses" / f"{hypothesis_id.lower()}.md"
    fm = local_frontmatter(
        employee_id=employee_id,
        doc_type="boi/local-hypothesis",
        title=f"{case_id} {hypothesis_id}: {args.statement.strip()}",
        description="Evidence로 지지·반증 상태를 추적하는 Local 가설.",
        boi_id=f"boi:private:{employee_id}:case:{case_id.lower()}:hypothesis:{hypothesis_id.lower()}",
        tags=["second-brain", "hypothesis", case_id.lower(), hypothesis_id.lower()],
        source_refs=[{"type": "local-document", "ref": relative_to_root(root, hub), "note": "case hub"}],
        review_after_days=7,
        extra={
            "case_id": case_id,
            "knowledge_role": "hypothesis",
            "claim_status": "inferred",
            "hypothesis_id": hypothesis_id,
            "hypothesis_status": status,
            "supports": supports,
            "contradicts": contradicts,
        },
    )
    body = (
        f"\n# {hypothesis_id}: {args.statement.strip()}\n\n"
        f"- Case: [{case_id} Case Hub](../case-hub.md)\n"
        f"- 상태: `{status}`\n"
        f"- 지지 evidence: `{supports or '없음'}`\n"
        f"- 반증 evidence: `{contradicts or '없음'}`\n\n"
        "## 판단 메모\n\n사실, 해석, 미확인 조건을 구분해 기록합니다.\n"
    )
    atomic_write(path, fm + body, overwrite=args.overwrite)
    append_log(root, f"`{case_id}`의 `{hypothesis_id}` 가설 상태를 `{status}`로 기록함.")
    return {"ok": True, "case_id": case_id, "hypothesis_id": hypothesis_id, "status": status, "path": relative_to_root(root, path), "remote_submitted": False}


def append_analysis(root: Path, employee_id: str, args: argparse.Namespace) -> dict[str, object]:
    case_id = require_case_id(args.case_id)
    path = case_dir(root, employee_id, case_id) / "analysis-log.md"
    if not path.exists():
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8")
    meta = parse_frontmatter(text)
    count = int(meta.get("log_entry_count", "0")) + 1
    text = re.sub(r"(?m)^log_entry_count: .*?$", f"log_entry_count: {count}", text, count=1)
    evidence = pipe(args.evidence_ref)
    evidence_ids = [item for item in evidence.split("|") if item]
    known = {item["evidence_id"]: item for item in case_evidence(root, employee_id, case_id)}
    unknown = sorted(set(evidence_ids) - set(known))
    if unknown:
        raise ValueError(f"analysis log references unknown evidence for {case_id}: {', '.join(unknown)}")
    refs = parse_frontmatter_list(text, "source_refs")
    for evidence_id in evidence_ids:
        record = known[evidence_id]
        ref = {
            "type": "local-document",
            "ref": record["path"],
            "note": f"analysis log evidence {evidence_id}",
        }
        if not any(item.get("ref") == ref["ref"] for item in refs):
            refs.append(ref)
    text = replace_frontmatter_list(text, "source_refs", refs)
    entry = f"\n## {now_kst().isoformat()} — {args.entry.strip()}\n\n- Evidence: `{evidence or '없음'}`\n- 다음 확인: {args.next_check.strip() or '미정'}\n"
    atomic_write(path, text.rstrip() + "\n" + entry, overwrite=True)
    return {"ok": True, "case_id": case_id, "log_entry_count": count, "path": relative_to_root(root, path), "remote_submitted": False}


def review_case(root: Path, employee_id: str, args: argparse.Namespace) -> dict[str, object]:
    case_id = require_case_id(args.case_id)
    base = private_root(root, employee_id)
    directory = case_dir(root, employee_id, case_id)
    evidence = []
    for path in sorted((base / "evidence" / case_id).glob("*.md")) if (base / "evidence" / case_id).is_dir() else []:
        meta = parse_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        evidence.append({"id": meta.get("evidence_id", ""), "type": meta.get("evidence_type", ""), "path": relative_to_root(root, path)})
    hypotheses = []
    for path in sorted((directory / "hypotheses").glob("*.md")) if (directory / "hypotheses").is_dir() else []:
        meta = parse_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        hypotheses.append({"id": meta.get("hypothesis_id", ""), "status": meta.get("hypothesis_status", ""), "supports": meta.get("supports", ""), "contradicts": meta.get("contradicts", "")})
    issues = []
    if not (directory / "case-hub.md").exists():
        issues.append("case hub is missing")
    if not evidence:
        issues.append("no evidence registered")
    if not hypotheses:
        issues.append("no hypotheses registered")
    return {"ok": not issues, "case_id": case_id, "evidence": evidence, "hypotheses": hypotheses, "issues": issues, "local_only": True, "remote_submitted": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--employee-id", default="")
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create")
    create.add_argument("--case-id", required=True)
    create.add_argument("--title", required=True)
    create.add_argument("--question", required=True)

    hypothesis = sub.add_parser("hypothesis")
    hypothesis.add_argument("--case-id", required=True)
    hypothesis.add_argument("--hypothesis-id", required=True)
    hypothesis.add_argument("--statement", required=True)
    hypothesis.add_argument("--status", default="open")
    hypothesis.add_argument("--supports", action="append", default=[])
    hypothesis.add_argument("--contradicts", action="append", default=[])
    hypothesis.add_argument("--overwrite", action="store_true")

    log = sub.add_parser("log")
    log.add_argument("--case-id", required=True)
    log.add_argument("--entry", required=True)
    log.add_argument("--evidence-ref", action="append", default=[])
    log.add_argument("--next-check", default="")

    review = sub.add_parser("review")
    review.add_argument("--case-id", required=True)

    args = parser.parse_args()
    root = Path(args.root).resolve()
    try:
        employee_id, _ = workspace_employee_id(root, args.employee_id)
        handlers = {"create": create_case, "hypothesis": add_hypothesis, "log": append_analysis, "review": review_case}
        payload = handlers[args.command](root, employee_id, args)
    except (ValueError, FileNotFoundError, FileExistsError) as exc:
        print(json.dumps({"ok": False, "error": str(exc), "remote_submitted": False}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
