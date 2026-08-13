#!/usr/bin/env python3
"""Evaluate Local research retrieval, original-evidence binding, and the real generated Answer Surface."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from boi_local_common import parse_frontmatter, private_root, relative_to_root, split_frontmatter
from local_wiki import (
    ANSWER_GENERATION_RECEIPT_SCHEMA,
    answer_material_paragraphs,
    answer_receipt_path,
    build_query_pack,
    canonical_public_origin,
    fingerprint_payload,
    normalize_original_identity_bindings,
    original_identity_binding_matches,
)

BENCHMARK_SCHEMA = "boi-local-query-quality-benchmark/v2"
RESULT_SCHEMA = "boi-local-query-quality-result/v2"
LEGACY_BENCHMARK_SCHEMA = "boi-local-query-quality-benchmark/v1"
INTERNAL_SURFACE_TERMS = (
    "query pack",
    "manifest",
    "snapshot sha",
    "full sha256",
    "local current",
    "unified discovery",
    "federated current",
    "l/s/d/c",
)
FIXED_OUTLINE_HEADINGS = {
    "direct answer",
    "supporting evidence",
    "counterevidence",
    "unknowns and limits",
    "next checks",
    "confidence",
    "citations",
    "직접 답변",
    "지지 근거",
    "반대 근거",
    "미확인 사항과 한계",
    "다음 확인 사항",
    "신뢰도",
    "인용",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def axis_result(checks: list[dict[str, object]]) -> dict[str, object]:
    passed = sum(1 for check in checks if check["ok"])
    return {
        "ok": bool(checks) and passed == len(checks),
        "score": passed / len(checks) if checks else 0.0,
        "checks": checks,
    }


def check_recorder(checks: list[dict[str, object]]):
    def record(name: str, ok: bool, detail: object) -> None:
        checks.append({"name": name, "ok": bool(ok), "detail": detail})

    return record


def evidence_id(source: dict[str, object], root: Path) -> str:
    direct = str(source.get("evidence_id", ""))
    if direct:
        return direct
    path_text = str(source.get("path", ""))
    path = root / path_text
    if not path.is_file():
        return ""
    return parse_frontmatter(path.read_text(encoding="utf-8", errors="replace")).get("evidence_id", "")


def generated_answer(root: Path, employee_id: str, item: dict[str, object]) -> dict[str, object]:
    path_text = str(item.get("answer_path", "")).strip()
    if not path_text:
        return {"ok": False, "reason": "generated-answer-missing", "path": "", "body": "", "text": "", "sha256": ""}
    path = (root / path_text).resolve()
    profile = private_root(root, employee_id).resolve()
    try:
        path.relative_to(profile)
        local_private = True
    except ValueError:
        local_private = False
    if not local_private:
        return {
            "ok": False,
            "reason": "generated-answer-outside-local-private",
            "path": path_text,
            "body": "",
            "text": "",
            "sha256": "",
        }
    if not path.is_file():
        return {"ok": False, "reason": "generated-answer-missing", "path": path_text, "body": "", "text": "", "sha256": ""}
    text = path.read_text(encoding="utf-8", errors="replace")
    _, body = split_frontmatter(text)
    return {
        "ok": bool(body.strip()),
        "reason": "" if body.strip() else "generated-answer-empty",
        "path": path_text,
        "body": body.strip(),
        "text": text,
        "bytes": len(path.read_bytes()),
        "sha256": sha256(path),
    }


def answer_paragraphs(text: str) -> list[str]:
    paragraphs = []
    for part in re.split(r"\n\s*\n", text.strip()):
        cleaned = part.strip()
        if not cleaned:
            continue
        if all(line.lstrip().startswith("#") for line in cleaned.splitlines()):
            continue
        paragraphs.append(cleaned)
    return paragraphs


def contains_unnegated_claim(text: str, phrase: str) -> bool:
    """Treat an explicitly rejected overclaim as a limitation, not as the overclaim itself."""
    lowered = text.casefold()
    needle = phrase.casefold()
    starts = [match.start() for match in re.finditer(re.escape(needle), lowered)]
    if not starts:
        return False
    negations = (
        "아니다",
        "아닙니다",
        "맞지 않",
        "보장하지 않",
        "뜻은 아니",
        "간주할 수 없",
        "할 수 없",
        "해서는 안",
        "주장은 틀",
        "주장은 과장",
    )
    for start in starts:
        context = lowered[max(0, start - 40) : min(len(lowered), start + len(needle) + 140)]
        if not any(term in context for term in negations):
            return True
    return False


def expected_receipt_evidence(pack: dict[str, object], root: Path) -> list[dict[str, str]]:
    sources = {
        evidence_id(source, root): source
        for source in pack.get("evidence_sources", [])
        if evidence_id(source, root)
    }
    rows: list[dict[str, str]] = []
    for display in (pack.get("citation_surface") or {}).get("display_map", []):
        item_id = str(display.get("evidence_id", ""))
        source = sources.get(item_id, {})
        rows.append(
            {
                "evidence_id": item_id,
                "path": str(source.get("path", "")),
                "sha256": str(source.get("sha256", "")),
                "origin_ref": str(source.get("origin_ref", "")),
                "original_identity_binding": dict(source.get("original_identity_binding", {})),
            }
        )
    return rows


def generation_receipt_checks(
    root: Path,
    employee_id: str,
    question: str,
    pack: dict[str, object],
    item: dict[str, object],
    answer: dict[str, object],
) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    record = check_recorder(checks)
    answer_path = (root / str(answer["path"])).resolve()
    receipt_text = str(item.get("receipt_path", "")).strip()
    receipt_path = (root / receipt_text).resolve() if receipt_text else answer_receipt_path(answer_path)
    profile = private_root(root, employee_id).resolve()
    try:
        receipt_path.relative_to(profile)
        receipt_local = True
    except ValueError:
        receipt_local = False
    if not receipt_local or not receipt_path.is_file():
        record(
            "generation_receipt_missing",
            False,
            relative_to_root(root, receipt_path) if receipt_local else str(receipt_path),
        )
        return checks
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        record("generation_receipt_invalid", False, str(exc))
        return checks

    record(
        "generation_receipt_schema",
        receipt.get("schema") == ANSWER_GENERATION_RECEIPT_SCHEMA,
        receipt.get("schema"),
    )
    expected_answer = {
        "path": str(answer["path"]),
        "bytes": int(answer.get("bytes", 0)),
        "sha256": str(answer["sha256"]),
    }
    record("generation_receipt_answer_binding", receipt.get("answer") == expected_answer, receipt.get("answer"))
    expected_question_hash = hashlib.sha256(question.encode("utf-8")).hexdigest()
    record(
        "generation_receipt_question_binding",
        receipt.get("question_sha256") == expected_question_hash,
        receipt.get("question_sha256"),
    )
    expected_plan = fingerprint_payload(pack.get("query_plan", {}))
    record(
        "generation_receipt_query_plan_binding",
        receipt.get("query_plan_fingerprint") == expected_plan,
        receipt.get("query_plan_fingerprint"),
    )
    display_map = list((pack.get("citation_surface") or {}).get("display_map", []))
    expected_display = fingerprint_payload(display_map)
    record(
        "generation_receipt_citation_map_binding",
        receipt.get("citation_display_map_fingerprint") == expected_display,
        receipt.get("citation_display_map_fingerprint"),
    )
    expected_evidence = expected_receipt_evidence(pack, root)
    record(
        "generation_receipt_evidence_binding",
        receipt.get("evidence") == expected_evidence and bool(expected_evidence),
        receipt.get("evidence"),
    )
    critic = receipt.get("presentation_critic") or {}
    record(
        "generation_receipt_composer",
        receipt.get("composer") == "natural-expert"
        and critic.get("max_passes") == 1
        and critic.get("passes") in {0, 1},
        {"composer": receipt.get("composer"), "presentation_critic": critic},
    )

    paragraphs = answer_material_paragraphs(str(answer.get("text", "")))
    bindings = receipt.get("claim_bindings")
    display_to_evidence = {
        str(row.get("display_id", "")): str(row.get("evidence_id", "")) for row in display_map
    }
    valid_bindings = isinstance(bindings, list) and len(bindings) == len(paragraphs) and bool(paragraphs)
    seen: set[int] = set()
    if valid_bindings:
        for binding in bindings:
            if not isinstance(binding, dict):
                valid_bindings = False
                break
            index = int(binding.get("paragraph_index", 0))
            if index < 1 or index > len(paragraphs) or index in seen:
                valid_bindings = False
                break
            seen.add(index)
            paragraph = paragraphs[index - 1]
            citations = [str(value) for value in binding.get("citations", [])]
            kind = str(binding.get("binding_kind", ""))
            paragraph_markers = re.findall(r"\[\d+\]", paragraph)
            valid_bindings = (
                binding.get("paragraph_sha256") == hashlib.sha256(paragraph.encode("utf-8")).hexdigest()
                and bool(str(binding.get("claim", "")).strip())
                and kind in {"supported-claim", "counterevidence", "uncertainty", "local-policy"}
                and len(paragraph_markers) == len(set(paragraph_markers))
                and len(citations) == len(set(citations))
                and citations == paragraph_markers
                and all(marker in display_to_evidence for marker in citations)
                and (kind in {"uncertainty", "local-policy"} or bool(citations))
                and binding.get("evidence_ids") == [display_to_evidence[marker] for marker in citations]
            )
            if not valid_bindings:
                break
        valid_bindings = valid_bindings and seen == set(range(1, len(paragraphs) + 1))
    record(
        "generation_receipt_claim_bindings",
        valid_bindings and receipt.get("material_paragraph_count") == len(paragraphs),
        {"material_paragraphs": len(paragraphs), "bindings": bindings},
    )
    return checks


def evaluate_retrieval(root: Path, pack: dict[str, object], item: dict[str, object]) -> dict[str, object]:
    checks: list[dict[str, object]] = []
    record = check_recorder(checks)
    compiled = list(pack.get("compiled_sources", []))
    evidence = list(pack.get("evidence_sources", []))
    roles = {str(source.get("knowledge_role", "")) for source in compiled}
    evidence_ids = {evidence_id(source, root) for source in evidence} - {""}
    actual_intent = str(pack.get("query_intent", ""))
    expected_intent = str(item.get("expected_intent", actual_intent))
    record("intent", actual_intent == expected_intent, {"actual": actual_intent, "expected": expected_intent})
    primary = str(compiled[0].get("knowledge_role", "")) if compiled else ""
    expected_primary = str(item.get("primary_role", primary))
    record("primary_role", primary == expected_primary, {"actual": primary, "expected": expected_primary})
    required_roles = set(item.get("required_compiled_roles", []))
    record("compiled_roles", required_roles <= roles, {"actual": sorted(roles), "required": sorted(required_roles)})
    required_evidence = set(item.get("required_evidence_ids", []))
    record(
        "evidence_retrieval",
        required_evidence <= evidence_ids,
        {"actual": sorted(evidence_ids), "required": sorted(required_evidence)},
    )
    expected_scope = str(item.get("expected_retrieval_scope", ""))
    if expected_scope:
        record(
            "retrieval_scope",
            pack.get("retrieval_scope") == expected_scope,
            {"actual": pack.get("retrieval_scope"), "expected": expected_scope},
        )
    if str(pack.get("retrieval_scope", "")).startswith("ordinary-"):
        support_paths = [
            str(source.get("path", ""))
            for source in compiled
            if "/reports/" in str(source.get("path", "")).replace("\\", "/")
            or "/notes/guide/" in str(source.get("path", "")).replace("\\", "/")
        ]
        record("ordinary_research_excludes_support", not support_paths, support_paths)
    return axis_result(checks)


def evaluate_evidence_binding(
    root: Path,
    pack: dict[str, object],
    item: dict[str, object],
    answer: dict[str, object],
) -> dict[str, object]:
    checks: list[dict[str, object]] = []
    record = check_recorder(checks)
    if not answer["ok"]:
        record(str(answer["reason"]), False, answer["path"])
        return axis_result(checks)
    narrative = "\n\n".join(answer_material_paragraphs(str(answer.get("text", answer["body"]))))
    used_markers = sorted(set(re.findall(r"\[(\d+)\]", narrative)), key=int)
    display_map = {
        str(row.get("display_id", "")): str(row.get("evidence_id", ""))
        for row in (pack.get("citation_surface") or {}).get("display_map", [])
    }
    marker_labels = [f"[{marker}]" for marker in used_markers]
    mapped_ids = [display_map.get(marker, "") for marker in marker_labels]
    minimum = int(item.get("minimum_citations", 3))
    record(
        "citation_count",
        minimum <= len(marker_labels) <= 5,
        {"actual": len(marker_labels), "minimum": minimum, "maximum": 5},
    )
    record(
        "citation_display_binding",
        bool(marker_labels) and all(marker in display_map for marker in marker_labels),
        {"used": marker_labels, "available": sorted(display_map)},
    )
    required_citations = set(item.get("required_citation_ids", item.get("required_evidence_ids", [])))
    record(
        "required_original_citations",
        required_citations <= set(mapped_ids),
        {"actual": mapped_ids, "required": sorted(required_citations)},
    )
    sources = {
        evidence_id(source, root): source
        for source in pack.get("evidence_sources", [])
        if evidence_id(source, root)
    }
    cited_sources = [sources.get(item_id) for item_id in mapped_ids if item_id]
    citation_route = str(item.get("citation_evidence_route", "public-research"))
    record(
        "citation_evidence_route",
        citation_route in {"public-research", "local-policy"},
        citation_route,
    )
    common_source_ok = bool(cited_sources) and all(
        source is not None
        and source.get("layer") == "source-evidence"
        and source.get("raw_integrity") == "verified"
        for source in cited_sources
    )
    source_detail = [
        {
            "evidence_id": mapped_ids[index],
            "layer": source.get("layer") if source else "missing",
            "raw_integrity": source.get("raw_integrity") if source else "missing",
            "origin_ref": source.get("origin_ref", "") if source else "",
            "evidence_authority": source.get("evidence_authority", "") if source else "missing",
            "original_identity_binding": source.get("original_identity_binding", {}) if source else {},
        }
        for index, source in enumerate(cited_sources)
    ]
    if citation_route == "local-policy":
        record("citations_are_explicit_local_evidence", common_source_ok, source_detail)
    else:
        declared_bindings = normalize_original_identity_bindings(item.get("required_original_bindings", []))
        declared_by_id = {row["evidence_id"]: row for row in declared_bindings}
        identity_checks = []
        for source in cited_sources:
            if source is None:
                identity_checks.append({"ok": False, "reason": "missing-source"})
                continue
            item_id = evidence_id(source, root)
            expected = declared_by_id.get(item_id)
            carried = source.get("original_identity_binding") or {}
            identity_checks.append(
                {
                    "ok": bool(expected)
                    and carried == expected
                    and original_identity_binding_matches(source, expected),
                    "evidence_id": item_id,
                    "expected": expected or {},
                    "carried": carried,
                    "origin_ref": source.get("origin_ref", ""),
                    "sha256": source.get("sha256", ""),
                }
            )
        record(
            "citations_match_declared_original_identity",
            bool(identity_checks) and all(row["ok"] for row in identity_checks),
            identity_checks,
        )
        record(
            "citations_are_canonical_public_originals",
            common_source_ok
            and all(
                source.get("evidence_authority") == "canonical-public-original"
                and canonical_public_origin(str(source.get("origin_ref", "")))
                for source in cited_sources
                if source
            ),
            source_detail,
        )
    byte_checks: list[dict[str, object]] = []
    for source in cited_sources:
        if source is None:
            byte_checks.append({"ok": False, "reason": "missing-source"})
            continue
        raw_text = str(source.get("raw_path", ""))
        raw = Path(raw_text).expanduser()
        if not raw.is_absolute():
            raw = root / raw
        exists = raw.is_file()
        actual_hash = sha256(raw) if exists else ""
        expected_hash = str(source.get("sha256", ""))
        byte_checks.append(
            {
                "ok": exists and actual_hash == expected_hash,
                "evidence_id": evidence_id(source, root),
                "exists": exists,
                "expected_sha256": expected_hash,
                "actual_sha256": actual_hash,
            }
        )
    record("original_bytes_verified", bool(byte_checks) and all(row["ok"] for row in byte_checks), byte_checks)
    return axis_result(checks)


def evaluate_answer_surface(
    root: Path,
    employee_id: str,
    question: str,
    pack: dict[str, object],
    item: dict[str, object],
    answer: dict[str, object],
) -> dict[str, object]:
    checks: list[dict[str, object]] = []
    record = check_recorder(checks)
    if not answer["ok"]:
        record(str(answer["reason"]), False, answer["path"])
        return axis_result(checks)
    checks.extend(generation_receipt_checks(root, employee_id, question, pack, item, answer))
    text = str(answer["body"])
    lowered = text.casefold()
    paragraphs = answer_paragraphs(text)
    first = paragraphs[0] if paragraphs else ""
    system_first = any(term in first.casefold() for term in ("실행 상태", "검증 결과:", "시스템 상태", "query pack", "manifest"))
    record("conclusion_first", bool(first) and not system_first and len(first) >= 40, first[:240])
    record(
        "internal_audit_terms_hidden",
        not any(term in lowered for term in INTERNAL_SURFACE_TERMS),
        [term for term in INTERNAL_SURFACE_TERMS if term in lowered],
    )
    headings = {
        re.sub(r"^#{1,6}\s*", "", line).strip().casefold()
        for line in text.splitlines()
        if re.match(r"^#{1,6}\s+", line)
    }
    fixed = sorted(headings & FIXED_OUTLINE_HEADINGS)
    record("no_fixed_seven_section_outline", len(fixed) < 4, fixed)
    record("natural_expert_depth", 120 <= len(text) <= 5000, {"characters": len(text)})
    for phrase in item.get("must_include", []):
        record(f"must_include:{phrase}", str(phrase).casefold() in lowered, phrase)
    for phrase in item.get("must_not_include", []):
        record(
            f"must_not_include:{phrase}",
            not contains_unnegated_claim(text, str(phrase)),
            phrase,
        )
    contract = pack.get("answer_contract") or {}
    presentation = contract.get("presentation") or {}
    critic = contract.get("presentation_critic") or {}
    record(
        "natural_expert_contract",
        presentation.get("surface_style") == "natural-expert"
        and presentation.get("fixed_outline_required") is False,
        presentation,
    )
    record("one_pass_presentation_critic", critic.get("max_repairs") == 1, critic)
    return axis_result(checks)


def evaluate_question(root: Path, employee_id: str, case_id: str, item: dict[str, object]) -> dict[str, object]:
    question = str(item["question"])
    pack = build_query_pack(
        root,
        employee_id,
        question,
        case_id,
        8,
        [],
        "ordinary",
        item.get("required_original_bindings", []),
    )
    answer = generated_answer(root, employee_id, item)
    axes = {
        "retrieval": evaluate_retrieval(root, pack, item),
        "evidence_binding": evaluate_evidence_binding(root, pack, item, answer),
        "answer_surface": evaluate_answer_surface(root, employee_id, question, pack, item, answer),
    }
    score = sum(float(axis["score"]) for axis in axes.values()) / len(axes)
    compiled = list(pack.get("compiled_sources", []))
    evidence = list(pack.get("evidence_sources", []))
    return {
        "id": item["id"],
        "question": question,
        "ok": all(axis["ok"] for axis in axes.values()),
        "score": score,
        "quality_axes": axes,
        "retrieved": {
            "intent": pack.get("query_intent"),
            "query_plan": pack.get("query_plan", {}),
            "retrieval_scope": pack.get("retrieval_scope", ""),
            "compiled": [source.get("path", "") for source in compiled],
            "evidence": [source.get("path", "") for source in evidence],
            "evidence_ids": [evidence_id(source, root) for source in evidence],
            "remote_sources": len(pack.get("remote_sources", [])),
        },
        "generated_answer": {
            "path": answer["path"],
            "sha256": answer["sha256"],
            "evaluated": bool(answer["ok"]),
        },
    }


def evaluate(root: Path, benchmark_path: Path) -> dict[str, object]:
    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    schema = benchmark.get("schema")
    if schema == LEGACY_BENCHMARK_SCHEMA:
        raise ValueError(
            "legacy benchmark embeds pre-authored answers and cannot prove Answer Surface quality; migrate to v2 answer_path"
        )
    if schema != BENCHMARK_SCHEMA:
        raise ValueError(f"benchmark schema must be {BENCHMARK_SCHEMA}")
    employee_id = str(benchmark["employee_id"])
    case_id = str(benchmark["case_id"])
    results = [evaluate_question(root, employee_id, case_id, item) for item in benchmark.get("questions", [])]
    axis_scores = {
        name: sum(float(result["quality_axes"][name]["score"]) for result in results) / len(results)
        if results
        else 0.0
        for name in ("retrieval", "evidence_binding", "answer_surface")
    }
    return {
        "schema": RESULT_SCHEMA,
        "ok": bool(results) and all(result["ok"] for result in results),
        "benchmark": relative_to_root(root, benchmark_path),
        "case_id": case_id,
        "question_count": len(results),
        "actual_answer_count": sum(1 for result in results if result["generated_answer"]["evaluated"]),
        "preauthored_benchmark_answers_evaluated": 0,
        "quality_axis_scores": axis_scores,
        "average_score": sum(float(result["score"]) for result in results) / len(results) if results else 0.0,
        "average_score_is_composite_not_answer_surface": True,
        "questions": results,
        "local_only": True,
        "mcp_invocations": 0,
        "remote_mutations": 0,
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--benchmark", required=True, help="Path to a v2 query benchmark with generated answer_path values")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    benchmark = (root / args.benchmark).resolve()
    try:
        payload = evaluate(root, benchmark)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        payload = {"schema": RESULT_SCHEMA, "ok": False, "error": str(exc)}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
