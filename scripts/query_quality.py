#!/usr/bin/env python3
"""Verify that Local LLM Wiki queries retrieve enough grounded context for reviewed answers."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from boi_local_common import parse_frontmatter, private_root, relative_to_root
from local_wiki import build_query_pack

BENCHMARK_SCHEMA = "boi-local-query-quality-benchmark/v1"
RESULT_SCHEMA = "boi-local-query-quality-result/v1"
ANSWER_FIELDS = {
    "direct_answer",
    "supporting_evidence",
    "counterevidence",
    "unknowns_and_limits",
    "next_checks",
    "confidence",
    "citations",
}


def flatten_text(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " ".join(flatten_text(item) for item in value)
    if isinstance(value, dict):
        return " ".join(flatten_text(item) for item in value.values())
    return str(value)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate_question(root: Path, employee_id: str, case_id: str, item: dict[str, object]) -> dict[str, object]:
    question = str(item["question"])
    pack = build_query_pack(root, employee_id, question, case_id, 8, [])
    checks: list[dict[str, object]] = []

    def record(name: str, ok: bool, detail: object) -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})

    compiled = list(pack["compiled_sources"])
    evidence = list(pack["evidence_sources"])
    all_sources = [*compiled, *evidence]
    source_paths = {str(source["path"]) for source in all_sources}
    roles = {str(source.get("knowledge_role", "")) for source in compiled}
    evidence_ids = set()
    for source in evidence:
        path = root / str(source["path"])
        evidence_ids.add(parse_frontmatter(path.read_text(encoding="utf-8", errors="replace")).get("evidence_id", ""))

    record("intent", pack["query_intent"] == item["expected_intent"], {"actual": pack["query_intent"], "expected": item["expected_intent"]})
    primary = str(compiled[0].get("knowledge_role", "")) if compiled else ""
    record("primary_role", primary == item["primary_role"], {"actual": primary, "expected": item["primary_role"]})
    required_roles = set(item.get("required_compiled_roles", []))
    record("compiled_roles", required_roles <= roles, {"actual": sorted(roles), "required": sorted(required_roles)})
    required_evidence = set(item.get("required_evidence_ids", []))
    record("evidence_retrieval", required_evidence <= evidence_ids, {"actual": sorted(evidence_ids), "required": sorted(required_evidence)})

    answer = dict(item.get("answer", {}))
    record("answer_sections", ANSWER_FIELDS <= set(answer), {"actual": sorted(answer), "required": sorted(ANSWER_FIELDS)})
    record("confidence", answer.get("confidence") in {"low", "medium", "high"}, answer.get("confidence"))
    answer_text = flatten_text(answer).lower()
    for phrase in item.get("must_include", []):
        record(f"must_include:{phrase}", str(phrase).lower() in answer_text, phrase)
    for phrase in item.get("must_not_include", []):
        record(f"must_not_include:{phrase}", str(phrase).lower() not in answer_text, phrase)

    citation_results = []
    for citation in answer.get("citations", []):
        path_text = str(citation.get("path", ""))
        path = (root / path_text).resolve()
        try:
            path.relative_to(private_root(root, employee_id).resolve())
            local_private = True
        except ValueError:
            local_private = False
        exists = path.is_file()
        in_pack = path_text in source_paths
        support_note = bool(str(citation.get("supports", "")).strip())
        citation_results.append(
            {
                "path": path_text,
                "exists": exists,
                "in_query_pack": in_pack,
                "local_private": local_private,
                "supports_note": support_note,
                "sha256": sha256(path) if exists else "",
            }
        )
    record(
        "citations",
        bool(citation_results) and all(
            result["exists"] and result["in_query_pack"] and result["local_private"] and result["supports_note"]
            for result in citation_results
        ),
        citation_results,
    )
    record("answer_contract", set(pack["answer_contract"]["required_sections"]) == ANSWER_FIELDS, pack["answer_contract"])
    passed = sum(1 for check in checks if check["ok"])
    return {
        "id": item["id"],
        "question": question,
        "ok": passed == len(checks),
        "score": passed / len(checks) if checks else 0.0,
        "checks": checks,
        "retrieved": {
            "intent": pack["query_intent"],
            "compiled": [source["path"] for source in compiled],
            "evidence": [source["path"] for source in evidence],
            "remote_sources": len(pack["remote_sources"]),
        },
        "reviewed_answer": answer,
    }


def evaluate(root: Path, benchmark_path: Path) -> dict[str, object]:
    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    if benchmark.get("schema") != BENCHMARK_SCHEMA:
        raise ValueError(f"benchmark schema must be {BENCHMARK_SCHEMA}")
    employee_id = str(benchmark["employee_id"])
    case_id = str(benchmark["case_id"])
    results = [evaluate_question(root, employee_id, case_id, item) for item in benchmark.get("questions", [])]
    return {
        "schema": RESULT_SCHEMA,
        "ok": bool(results) and all(result["ok"] for result in results),
        "benchmark": relative_to_root(root, benchmark_path),
        "case_id": case_id,
        "question_count": len(results),
        "average_score": sum(float(result["score"]) for result in results) / len(results) if results else 0.0,
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
    parser.add_argument("--benchmark", required=True, help="Path to an administrator-approved query benchmark")
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
