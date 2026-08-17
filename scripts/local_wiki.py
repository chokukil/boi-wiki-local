#!/usr/bin/env python3
"""Operate the OKF + BoI Profile Local LLM Wiki without remote mutation."""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import os
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse

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
    sha256_file,
    slugify,
    split_frontmatter,
    workspace_employee_id,
)
from local_case import case_dir, refresh_case_hub_evidence, require_case_id
from local_lint import active_markdown, lint_workspace

INGEST_PLAN_SCHEMA = "boi-local-wiki-ingest-plan/v1"
QUERY_PACK_SCHEMA = "boi-local-wiki-query-pack/v2"
ANSWER_GENERATION_RECEIPT_SCHEMA = "boi-local-answer-generation-receipt/v1"
REMOTE_REF_RE = re.compile(r"^[^|]+\|[^|]+\|(private|team|public)\|.+$")
GENERIC_REVIEW_ROLES = {
    "comparison",
    "commonality",
    "timeline",
    "continuous-log",
    "decision-record",
    "recurrence-fingerprint",
}
EVIDENCE_TYPE_ALIASES = {
    "outlook-email": "email",
    "analysis-report": "document",
    "analysis-image": "image",
    "wafer-map-image": "image",
    "external-source-note": "web-clip",
}

COMPILED_KNOWLEDGE_ROLES = {
    "case-hub",
    "hypothesis",
    "continuous-log",
    "signal-summary",
    "comparison",
    "cohort-comparison",
    "commonality",
    "timeline",
    "decision-record",
    "recurrence-fingerprint",
    "saved-query",
}
QUERY_EXCLUDED_SUBTYPES = {
    "answer-snapshot",
    "external-communication",
    "presentation-support",
    "query-verification",
    "review-queue",
    "selection-record",
}
PUBLIC_ORIGIN_IDENTIFIER_RE = re.compile(
    r"^(?:doi:10\.\d{4,9}/\S+|arxiv:\d{4}\.\d{4,5}(?:v\d+)?|acl:[A-Za-z0-9.-]+)$",
    re.IGNORECASE,
)
PUBLIC_DNS_LABEL_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$", re.IGNORECASE)
NON_PUBLIC_DNS_SUFFIXES = {"internal", "local", "localhost", "test", "example", "invalid"}
FACET_EVIDENCE_TERMS = {
    "source-preservation": ("파라메트릭 기억", "외부 문서 인덱스", "교체 가능한 외부", "외부 기억"),
    "knowledge-structuring": ("비교 가능한 속성", "prompting method", "number of shots", "metric", "실험 레코드"),
    "grounded-answering": ("검색 누락", "문맥 미사용", "noise 민감성", "무근거 생성", "claim 단위"),
    "change-maintenance": ("시간 일관성", "과거 사실", "복합 시간", "유효 시점", "현재 사실"),
    "relationship-fit": ("graphrag", "multi-hop", "온톨로지", "도메인 규칙", "엔터티 연결"),
    "retrieval-vs-persistent": ("rag", "llm wiki", "persistent", "지속 지식", "지속 markdown"),
    "retrieval-foundation": ("파라메트릭 기억", "외부 문서 인덱스", "retrieval-augmented generation"),
    "wiki-persistence": ("llm wiki", "persistent markdown", "지속 지식", "wiki compilation"),
    "wiki-synthesis-limit": ("living wiki", "answer synthesis", "hybrid rag", "전체 답변 합성"),
    "approval-boundary": ("사람 판정", "사람 보정", "승인", "review", "공유 경계"),
    "quality-evaluation": ("retrieval evaluation", "distractor", "ragchecker", "검색 품질", "답변 품질"),
    "conflict-resolution": ("충돌", "시간 일관성", "유효 시점", "기억 진화", "invalidation"),
    "temporal-validity": ("유효 시점", "기록 시점", "과거 사실", "현재 사실", "temporal"),
    "memory-evolution": ("기억 진화", "기존 기억", "동적 연결", "관련 과거 기억", "a-mem"),
    "context-selection-risk": ("lost in the middle", "hard distractor", "긴 문맥", "문맥 중간", "방해 문맥"),
    "claim-diagnosis": ("ragchecker", "claim 단위", "검색 누락", "문맥 미사용", "무근거 생성"),
    "automated-evaluation": ("ragas", "faithfulness", "answer relevance", "context relevance", "자동 사전 점검"),
}
INTENT_ROLE_BOOSTS = {
    "recurrence": {"recurrence-fingerprint": 30, "decision-record": 8, "hypothesis": 5},
    "decision": {"decision-record": 60, "hypothesis": 14, "case-hub": 4, "continuous-log": 5},
    "hypothesis": {"hypothesis": 60, "decision-record": 18, "case-hub": 4, "continuous-log": 4},
    "verification": {"decision-record": 12, "hypothesis": 10, "comparison": 8, "continuous-log": 6},
    "promotion": {"decision-record": 60, "recurrence-fingerprint": 18, "case-hub": 4},
    "history": {"continuous-log": 18, "timeline": 14, "decision-record": 6},
    "synthesis": {"comparison": 36, "case-hub": 6, "decision-record": 4},
    "comparison": {"comparison": 40, "cohort-comparison": 32, "commonality": 10},
    "evaluation": {"comparison": 30, "decision-record": 10, "hypothesis": 8},
    "explanation": {"comparison": 24, "case-hub": 8},
    "change-tracking": {"comparison": 24, "timeline": 18, "continuous-log": 16, "decision-record": 8},
    "general": {"decision-record": 10, "case-hub": 8, "hypothesis": 6, "recurrence-fingerprint": 5},
}


def json_hash(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def locate_evidence(root: Path, employee_id: str, case_id: str, evidence_id: str) -> tuple[Path, dict[str, str]]:
    directory = private_root(root, employee_id) / "evidence" / case_id
    for path in sorted(directory.glob("*.md")) if directory.is_dir() else []:
        meta = parse_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        if meta.get("evidence_id", "").upper() == evidence_id.upper():
            return path, meta
    raise FileNotFoundError(f"evidence is not registered for {case_id}: {evidence_id}")


def affected_hypotheses(root: Path, employee_id: str, case_id: str, evidence_id: str) -> list[Path]:
    directory = case_dir(root, employee_id, case_id) / "hypotheses"
    paths: list[Path] = []
    for path in sorted(directory.glob("*.md")) if directory.is_dir() else []:
        meta = parse_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        refs = set(filter(None, (meta.get("supports", "") + "|" + meta.get("contradicts", "")).split("|")))
        if evidence_id in refs:
            paths.append(path)
    return paths


def downstream_review_targets(root: Path, employee_id: str, case_id: str) -> list[dict[str, str]]:
    """List derived pages that require human review without claiming an automatic evidence link."""
    directory = case_dir(root, employee_id, case_id)
    candidates: list[dict[str, str]] = []
    for path in sorted(directory.rglob("*.md")) if directory.is_dir() else []:
        meta = parse_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        role = meta.get("knowledge_role", "")
        if role not in GENERIC_REVIEW_ROLES | {"cohort-comparison"}:
            continue
        candidates.append(
            {
                "path": relative_to_root(root, path),
                "knowledge_role": role,
                "current_sha256": sha256_file(path),
                "action": "human-review-for-evidence-impact",
                "automatic_claim_change": False,
            }
        )
    return candidates


def build_ingest_plan(root: Path, employee_id: str, case_id: str, evidence_id: str) -> dict[str, object]:
    case_id = require_case_id(case_id)
    evidence_path, evidence_meta = locate_evidence(root, employee_id, case_id, evidence_id)
    raw = (root / evidence_meta.get("raw_path", "")).resolve()
    if not raw.is_file():
        raise FileNotFoundError(f"raw evidence is missing: {raw}")
    raw_sha = sha256_file(raw)
    if raw_sha != evidence_meta.get("evidence_sha256"):
        raise ValueError("raw evidence SHA256 does not match its OKF evidence sidecar")
    hub = case_dir(root, employee_id, case_id) / "case-hub.md"
    if not hub.is_file():
        raise FileNotFoundError(hub)
    related = affected_hypotheses(root, employee_id, case_id, evidence_meta["evidence_id"])
    targets = [hub, *related]
    raw_evidence_type = evidence_meta.get("evidence_type", "")
    evidence_type = EVIDENCE_TYPE_ALIASES.get(raw_evidence_type, raw_evidence_type)
    role_hints = {
        "email": ["signal-summary", "timeline"],
        "tabular-data": ["comparison", "commonality", "timeline"],
        "image": ["comparison"],
        "document": ["decision-record"],
        "meeting-note": ["decision-record", "continuous-log"],
        "web-clip": ["decision-record"],
        "analysis-export": ["comparison", "commonality", "timeline"],
    }.get(evidence_type, ["case-hub"])
    plan_core = {
        "schema": INGEST_PLAN_SCHEMA,
        "employee_id": employee_id,
        "case_id": case_id,
        "evidence": {
            "evidence_id": evidence_meta["evidence_id"],
            "evidence_type": evidence_type,
            "source_evidence_type": raw_evidence_type,
            "evidence_type_deprecated": raw_evidence_type in EVIDENCE_TYPE_ALIASES,
            "sidecar": relative_to_root(root, evidence_path),
            "sidecar_sha256": sha256_file(evidence_path),
            "raw_sha256": raw_sha,
        },
        "profile_contract": {
            "okf_version": "0.1",
            "boi_profile_version": "0.1-local",
            "visibility": "local-private",
            "local_only": True,
        },
        "targets": [
            {
                "path": relative_to_root(root, path),
                "current_sha256": sha256_file(path),
                "actions": ["refresh-structured-source-refs", "refresh-standard-markdown-evidence-links"]
                if path == hub
                else ["add-structured-evidence-source-ref"],
            }
            for path in targets
        ],
        "review_targets": downstream_review_targets(root, employee_id, case_id),
        "suggested_knowledge_roles": role_hints,
        "domain_interpretation_required": evidence_type in {"image", "tabular-data", "analysis-export"},
        "raw_mutation_allowed": False,
        "remote_mutation_allowed": False,
    }
    return {**plan_core, "plan_hash": json_hash(plan_core)}


def add_evidence_ref(path: Path, root: Path, evidence_path: Path, evidence_id: str) -> None:
    text = path.read_text(encoding="utf-8")
    refs = parse_frontmatter_list(text, "source_refs")
    ref = {
        "type": "local-document",
        "ref": relative_to_root(root, evidence_path),
        "note": f"case evidence {evidence_id}",
    }
    if not any(item.get("ref") == ref["ref"] for item in refs):
        refs.append(ref)
        atomic_write(path, replace_frontmatter_list(text, "source_refs", refs), overwrite=True)


def apply_ingest(root: Path, employee_id: str, case_id: str, evidence_id: str, confirmation: str) -> dict[str, object]:
    plan = build_ingest_plan(root, employee_id, case_id, evidence_id)
    if confirmation != plan["plan_hash"]:
        raise ValueError(f"ingest apply requires --confirm-plan-hash {plan['plan_hash']}")
    timestamp = now_kst().strftime("%Y%m%d-%H%M%S")
    archive = private_root(root, employee_id) / "_archive" / "wiki-plans" / f"{timestamp}-{str(plan['plan_hash'])[:12]}"
    for target in plan["targets"]:
        path = (root / str(target["path"])).resolve()
        if sha256_file(path) != target["current_sha256"]:
            raise ValueError(f"target changed after preview; run ingest-preview again: {target['path']}")
        backup = archive / path.relative_to(private_root(root, employee_id))
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup)
    evidence_path, evidence_meta = locate_evidence(root, employee_id, case_id, evidence_id)
    hub_result = refresh_case_hub_evidence(root, employee_id, case_id)
    for path in affected_hypotheses(root, employee_id, case_id, evidence_meta["evidence_id"]):
        add_evidence_ref(path, root, evidence_path, evidence_meta["evidence_id"])
    raw = root / evidence_meta["raw_path"]
    if sha256_file(raw) != plan["evidence"]["raw_sha256"]:
        raise ValueError("raw evidence changed during ingest apply")
    append_log(
        root,
        f"Local Wiki ingest 적용: `{case_id}` / `{evidence_meta['evidence_id']}` / plan `{str(plan['plan_hash'])[:12]}`. 원격 전송 없음.",
    )
    return {
        "ok": True,
        "schema": INGEST_PLAN_SCHEMA,
        "case_id": case_id,
        "evidence_id": evidence_meta["evidence_id"],
        "plan_hash": plan["plan_hash"],
        "archive": relative_to_root(root, archive),
        "case_hub": hub_result,
        "raw_source_unchanged": True,
        "local_only": True,
        "remote_submitted": False,
        "review_targets_not_mutated": [item["path"] for item in plan["review_targets"]],
    }


def curate_knowledge(
    root: Path,
    employee_id: str,
    *,
    case_id: str,
    title: str,
    claim: str,
    source_path: Path,
    source_sha256: str,
    evidence_sha256: str,
    claim_status: str,
    current_path: Path | None,
    material_change: bool,
    conflict: bool,
    confidence: str,
    inference_support: str,
    contains_sensitive: bool,
    sharing_scope_change: bool,
    apply_local: bool,
) -> dict[str, object]:
    """Preview or apply Local-only curation without changing Current or Remote."""
    case_id = require_case_id(case_id)
    if claim_status not in {"observed", "inferred"}:
        raise ValueError("curation claim_status must be observed or inferred")
    if not title.strip() or not claim.strip():
        raise ValueError("curation title and claim are required")
    if confidence not in {"low", "medium", "high"}:
        raise ValueError("curation confidence must be low, medium, or high")
    if inference_support not in {"supported", "unsupported"}:
        raise ValueError("curation inference_support must be supported or unsupported")

    base = private_root(root, employee_id).resolve()

    def local_file(path: Path, label: str) -> Path:
        resolved = path.resolve()
        try:
            resolved.relative_to(base)
        except ValueError as exc:
            raise ValueError(f"{label} must stay inside the Local Private profile") from exc
        if not resolved.is_file():
            raise FileNotFoundError(f"{label} is missing: {resolved}")
        return resolved

    def local_document(path: Path, label: str) -> Path:
        resolved = local_file(path, label)
        if resolved.suffix.lower() != ".md":
            raise FileNotFoundError(f"{label} is not Markdown: {resolved}")
        return resolved

    def required_sha256(value: str, label: str) -> str:
        normalized = value.lower()
        if not re.fullmatch(r"[0-9a-f]{64}", normalized):
            raise ValueError(f"{label} must be a SHA256 digest")
        return normalized

    source = local_document(source_path, "curation source")
    declared_source_sha = required_sha256(source_sha256, "declared source SHA256")
    actual_source_sha = sha256_file(source)
    if actual_source_sha != declared_source_sha:
        raise ValueError("declared source SHA256 does not match curation source bytes")
    source_meta = parse_frontmatter(source.read_text(encoding="utf-8", errors="replace"))
    if source_meta.get("case_id", "") != case_id:
        raise ValueError("curation source case_id does not match the requested case")

    declared_evidence_sha = required_sha256(evidence_sha256, "declared evidence SHA256")
    source_evidence_sha = required_sha256(source_meta.get("evidence_sha256", ""), "source evidence SHA256")
    if source_evidence_sha != declared_evidence_sha:
        raise ValueError("declared evidence SHA256 does not match the source provenance")
    source_raw_path = source_meta.get("raw_path", "")
    if not source_raw_path:
        raise ValueError("curation source is missing raw_path provenance")
    raw_path = Path(source_raw_path)
    if not raw_path.is_absolute():
        raw_path = root / raw_path
    raw = local_file(raw_path, "curation source evidence")
    if sha256_file(raw) != declared_evidence_sha:
        raise ValueError("declared evidence SHA256 does not match curation evidence bytes")
    if not source_meta.get("evidence_id", ""):
        raise ValueError("curation source is missing evidence_id provenance")

    def structured_ref_matches(entry: dict[str, str]) -> bool:
        declared_ref = entry.get("ref", "")
        if not declared_ref or entry.get("sha256", "").lower() != declared_evidence_sha:
            return False
        declared_path = Path(declared_ref)
        if not declared_path.is_absolute():
            declared_path = root / declared_path
        return (
            declared_path.resolve() == raw
            and entry.get("evidence_id", "") == source_meta["evidence_id"]
            and entry.get("type", "") == "local-file"
        )

    structured_provenance = [
        *parse_frontmatter_list(source.read_text(encoding="utf-8", errors="replace"), "source_refs"),
        *parse_frontmatter_list(source.read_text(encoding="utf-8", errors="replace"), "generated_from"),
    ]
    if not any(structured_ref_matches(entry) for entry in structured_provenance):
        raise ValueError("curation source is missing structured provenance binding for the declared evidence")

    current: Path | None = None
    current_meta: dict[str, str] = {}
    if current_path is not None:
        current = local_document(current_path, "Current baseline")
        current_meta = parse_frontmatter(current.read_text(encoding="utf-8", errors="replace"))
        if current_meta.get("case_id", "") != case_id:
            raise ValueError("Current baseline case_id does not match the requested case")

    source_ref = {
        "type": "local-document",
        "ref": relative_to_root(root, source),
        "sha256": actual_source_sha,
    }
    evidence_ref = {
        "type": "local-file",
        "ref": relative_to_root(root, raw),
        "sha256": declared_evidence_sha,
        "evidence_id": source_meta["evidence_id"],
    }
    current_ref = (
        {
            "type": "local-document",
            "ref": relative_to_root(root, current),
            "sha256": sha256_file(current),
        }
        if current is not None
        else None
    )
    reasons = []
    if material_change:
        reasons.append("material-change")
    if conflict:
        reasons.append("conflict")
    if confidence == "low":
        reasons.append("low-confidence")
    if inference_support == "unsupported":
        reasons.append("unsupported-inference")
    if contains_sensitive:
        reasons.append("sensitive-content")
    if sharing_scope_change:
        reasons.append("sharing-scope-change")
    review_required = bool(reasons)
    effective_claim_status = "conflicted" if conflict else claim_status
    target_dir = base / "notes" / ("review" if review_required else "knowledge")
    prefix = "review-" if review_required else ""
    target = target_dir / f"{prefix}{slugify(title)}.md"
    curation_status = "review-required" if review_required else "auto-managed"

    def matching_existing_curation(path: Path) -> bool:
        text = path.read_text(encoding="utf-8", errors="replace")
        meta = parse_frontmatter(text)
        if meta.get("case_id", "") != case_id or meta.get("curation_status", "") not in {
            "auto-managed",
            "review-required",
        }:
            return False
        refs = [
            *parse_frontmatter_list(text, "source_refs"),
            *parse_frontmatter_list(text, "generated_from"),
        ]
        source_bound = any(
            entry.get("type", "") == source_ref["type"]
            and entry.get("ref", "") == source_ref["ref"]
            and entry.get("sha256", "").lower() == source_ref["sha256"]
            for entry in refs
        )
        evidence_bound = any(
            entry.get("type", "") == evidence_ref["type"]
            and entry.get("ref", "") == evidence_ref["ref"]
            and entry.get("sha256", "").lower() == evidence_ref["sha256"]
            and entry.get("evidence_id", "") == evidence_ref["evidence_id"]
            for entry in refs
        )
        return source_bound and evidence_bound

    active_matches = [
        path
        for directory in (base / "notes" / "knowledge", base / "notes" / "review")
        for path in (sorted(directory.glob("*.md")) if directory.is_dir() else [])
        if matching_existing_curation(path)
    ]
    same_state = [
        path
        for path in active_matches
        if parse_frontmatter(path.read_text(encoding="utf-8", errors="replace")).get("curation_status")
        == curation_status
    ]
    stale_active = [path for path in active_matches if path not in same_state]
    if len(same_state) == 1 and not stale_active:
        existing = same_state[0]
        return {
            "ok": True,
            "status": "no-change",
            "proposed_status": "no-change",
            "path": relative_to_root(root, existing),
            "review_created": False,
            "current_path": current_ref["ref"] if current_ref else "",
            "current_sha256": current_ref["sha256"] if current_ref else "",
            "source_sha256": actual_source_sha,
            "evidence_sha256": declared_evidence_sha,
            "review_reasons": reasons,
            "preview": not apply_local,
            "local_only": True,
            "remote_submitted": False,
        }
    if target.exists() and (not target.is_file() or not matching_existing_curation(target)):
        raise ValueError(
            f"curation target belongs to a different curation identity: {relative_to_root(root, target)}"
        )
    fm = local_frontmatter(
        employee_id=employee_id,
        doc_type="boi/local-knowledge-note",
        title=title.strip(),
        description="Local knowledge curation result with an optional question-scoped Current boundary.",
        boi_id=f"boi:private:{employee_id}:curation:{case_id.lower()}:{slugify(title)}",
        tags=["second-brain", "knowledge-curation", case_id.lower(), curation_status],
        source_refs=[source_ref, evidence_ref, *([current_ref] if review_required and current_ref else [])],
        generated_from=[source_ref, evidence_ref],
        artifact_visibility="working" if review_required else "memory",
        lifecycle_state="working" if review_required else "memory",
        memory_candidate=not review_required,
        review_after_days=7 if review_required else 30,
        contains_sensitive="true" if contains_sensitive else "false",
        extra={
            "case_id": case_id,
            "knowledge_role": "comparison",
            "claim_status": effective_claim_status,
            "curation_status": curation_status,
            **(
                {
                    "current_baseline_path": current_ref["ref"],
                    "current_baseline_sha256": current_ref["sha256"],
                }
                if current_ref
                else {}
            ),
            "review_reason": "|".join(reasons),
            "confidence": confidence,
            "inference_support": inference_support,
            "sharing_scope_change": sharing_scope_change,
        },
    )
    boundary = (
        "This is a Review candidate. A human decision is required before any Current baseline changes."
        if review_required and current_ref
        else "This is a Review candidate. It is not an approved Current, and no Current baseline is invented."
        if review_required
        else "This conflict-free Local knowledge is immediately available to Local search; it does not change Current."
        if current_ref
        else "This conflict-free Local synthesis is immediately available to Local search; it is not an approved Current."
    )
    current_link = (
        f"- Current baseline: [{current_meta.get('title', current.stem)}]"
        f"({Path(os.path.relpath(current, target_dir)).as_posix()})\n"
        if current is not None
        else ""
    )
    body = (
        f"\n# {title.strip()}\n\n"
        f"## Claim\n\n{claim.strip()}\n\n"
        "## Governance boundary\n\n"
        f"{boundary}\n\n"
        f"{current_link}"
        f"- Source: [{source_meta.get('title', source.stem)}]({Path(os.path.relpath(source, target_dir)).as_posix()})\n"
    )
    result = {
        "ok": True,
        "status": curation_status if apply_local else "preview",
        "proposed_status": curation_status,
        "path": relative_to_root(root, target),
        "review_created": review_required if apply_local else False,
        "current_path": current_ref["ref"] if current_ref else "",
        "current_sha256": current_ref["sha256"] if current_ref else "",
        "source_sha256": actual_source_sha,
        "evidence_sha256": declared_evidence_sha,
        "review_reasons": reasons,
        "preview": not apply_local,
        "local_only": True,
        "remote_submitted": False,
    }
    if not apply_local:
        return result
    archived: list[str] = []
    transition_time = now_kst().strftime("%Y%m%d-%H%M%S-%f")
    duplicates = same_state[1:] if same_state else []
    archive_moves = []
    for stale in [*stale_active, *duplicates]:
        archive = (
            base
            / "_archive"
            / "knowledge-curation"
            / case_id.lower()
            / transition_time
            / stale.parent.name
            / stale.name
        )
        if archive.exists():
            raise FileExistsError(archive)
        archive_moves.append((stale, archive))
    archive_plan = []
    for stale, archive in archive_moves:
        stale_text = stale.read_text(encoding="utf-8")
        frontmatter_match = re.match(r"\A(---\r?\n.*?\r?\n---\r?\n)(.*)\Z", stale_text, re.DOTALL)
        if frontmatter_match is None:
            raise ValueError(f"active curation is missing valid frontmatter: {relative_to_root(root, stale)}")

        def rebase_link(match: re.Match[str]) -> str:
            raw_target = match.group(2)
            wrapped = raw_target.startswith("<") and raw_target.endswith(">")
            link_target = raw_target[1:-1] if wrapped else raw_target
            path_part, separator, fragment = link_target.partition("#")
            if not path_part or Path(path_part).is_absolute() or re.match(r"^[a-z][a-z0-9+.-]*:", path_part, re.I):
                return match.group(0)
            resolved = (stale.parent / path_part).resolve()
            rebased = Path(os.path.relpath(resolved, archive.parent)).as_posix()
            rendered = f"{rebased}{separator}{fragment}" if separator else rebased
            if wrapped:
                rendered = f"<{rendered}>"
            return f"[{match.group(1)}]({rendered})"

        archived_body = re.sub(
            r"(?<!!)\[([^\]]+)\]\(([^)]+)\)",
            rebase_link,
            frontmatter_match.group(2),
        )
        archived_text = frontmatter_match.group(1) + archived_body
        archive_plan.append((stale, archive, stale_text, archived_text))
    for stale, archive, stale_text, archived_text in archive_plan:
        archive.parent.mkdir(parents=True, exist_ok=True)
        stale.replace(archive)
        if archived_text != stale_text:
            atomic_write(archive, archived_text, overwrite=True)
        index_path = stale.parent / "index.md"
        if index_path.is_file():
            index_text = index_path.read_text(encoding="utf-8")
            kept = [
                line
                for line in index_text.splitlines()
                if not re.search(rf"\]\({re.escape(stale.name)}(?:#[^)]*)?\)\s*$", line)
            ]
            updated = "\n".join(kept).rstrip() + "\n"
            if updated != index_text.replace("\r\n", "\n"):
                atomic_write(index_path, updated, overwrite=True)
        archived.append(relative_to_root(root, archive))
    if same_state:
        target = same_state[0]
        result["path"] = relative_to_root(root, target)
        result["review_created"] = False
    else:
        atomic_write(target, fm + body)
    append_index_link(target.parent / "index.md", title.strip(), target.name)
    result["archived_paths"] = archived
    append_log(
        root,
        f"Local knowledge curation: `{case_id}` / `{title.strip()}` / `{curation_status}`. "
        f"Local archive transitions: {len(archived)}. Remote submission: none.",
    )
    return result


def query_tokens(question: str) -> list[str]:
    raw_tokens = re.findall(r"[A-Za-z0-9][A-Za-z0-9._-]*|[\uac00-\ud7a3]+", question.casefold())
    particles = (
        "으로", "에서", "에게", "처럼", "보다", "까지", "부터", "하며", "하고", "이면", "라면",
        "은", "는", "이", "가", "을", "를", "의", "에", "로", "와", "과", "도", "만", "면",
    )
    tokens: list[str] = []
    for token in raw_tokens:
        if len(token) <= 1:
            continue
        tokens.append(token)
        if re.fullmatch(r"[\uac00-\ud7a3]+", token):
            for particle in particles:
                if token.endswith(particle) and len(token) - len(particle) >= 2:
                    tokens.append(token[: -len(particle)])
                    break
    return list(dict.fromkeys(tokens))


def term_occurrences(text: str, term: str) -> int:
    lowered = text.casefold()
    if re.fullmatch(r"[a-z0-9][a-z0-9._-]*", term):
        pattern = rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])"
        return len(re.findall(pattern, lowered))
    return lowered.count(term)


def query_facets(question: str) -> list[str]:
    """Identify the material work requested by a question, not keyword votes."""
    text = " ".join(question.casefold().split())
    facets: list[str] = []
    rules = (
        ("source-preservation", "원문" in text and any(term in text for term in ("보존", "해시", "원본"))),
        ("knowledge-structuring", "지식" in text and any(term in text for term in ("정리", "구조", "적재"))),
        ("grounded-answering", "답변" in text and any(term in text for term in ("근거", "인용", "한계"))),
        (
            "change-maintenance",
            any(term in text for term in ("새 논문", "신규 논문", "변경 후보", "갱신", "업데이트")),
        ),
        ("relationship-fit", any(term in text for term in ("graphrag", "온톨로지", "multi-hop", "관계"))),
        (
            "retrieval-vs-persistent",
            "rag" in text and any(term in text for term in ("wiki", "세컨드 브레인", "지속")),
        ),
        ("approval-boundary", "승인" in text and any(term in text for term in ("경계", "어디", "team", "public"))),
        ("quality-evaluation", "품질" in text and any(term in text for term in ("좋아", "평가", "자동"))),
        ("conflict-resolution", any(term in text for term in ("충돌", "반대 근거", "상충"))),
    )
    for name, matched in rules:
        if matched:
            facets.append(name)
    if "conflict-resolution" in facets:
        facets.extend(["temporal-validity", "memory-evolution"])
    if "quality-evaluation" in facets:
        facets.extend(["context-selection-risk", "claim-diagnosis"])
    if "approval-boundary" in facets:
        facets.extend(["claim-diagnosis", "automated-evaluation"])
    if "retrieval-vs-persistent" in facets:
        facets.extend(["retrieval-foundation", "wiki-persistence", "wiki-synthesis-limit"])
    return facets


def query_purposes(question: str) -> list[str]:
    """Return an ordered, multi-purpose plan for the native agent composer."""
    text = " ".join(question.casefold().split())
    facets = query_facets(question)
    purposes: list[str] = []

    def add(value: str) -> None:
        if value not in purposes:
            purposes.append(value)

    if len(set(facets) & {"source-preservation", "knowledge-structuring", "grounded-answering", "change-maintenance"}) >= 3:
        add("synthesis")
    if any(term in text for term in ("차이", "비교", " vs ", "언제 일반", "어떤 질문에서 유용")):
        add("comparison")
    if "quality-evaluation" in facets or any(term in text for term in ("자동으로 좋아", "충분한가", "타당한가")):
        add("evaluation")
    if "approval-boundary" in facets or "conflict-resolution" in facets or any(
        term in text for term in ("어디에 두어야", "어떻게 유지", "채택해야", "결정해야")
    ):
        add("decision")
    if any(term in text for term in ("검증", "확인", "근거 있는", "누락", "정확")):
        add("verification")
    if "change-maintenance" in facets or any(term in text for term in ("변경 이력", "유효 시점", "시간에 따라")):
        add("change-tracking")
    if any(term in text for term in ("무엇", "왜", "어떻게", "설명")):
        add("explanation")
    return purposes or ["general"]


def evidence_facet_matches(text: str, requested_facets: list[str]) -> list[str]:
    lowered = text.casefold()
    return [
        facet
        for facet in requested_facets
        if any(term in lowered for term in FACET_EVIDENCE_TERMS.get(facet, ()))
    ]


def evidence_facet_scores(text: str, requested_facets: list[str]) -> dict[str, int]:
    lowered = text.casefold()
    return {
        facet: sum(min(lowered.count(term), 5) for term in FACET_EVIDENCE_TERMS.get(facet, ()))
        for facet in requested_facets
    }


def query_intent(question: str) -> str:
    purposes = query_purposes(question)
    if "synthesis" in purposes:
        return "synthesis"
    for purpose in ("comparison", "evaluation", "decision", "verification", "change-tracking", "explanation"):
        if purpose in purposes:
            return purpose
    return purposes[0]


def answer_excerpt(text: str, terms: list[str], limit: int = 900) -> str:
    """Return a compact human-readable excerpt without treating it as a generated answer."""
    _, body = split_frontmatter(text)
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    informative = [
        line for line in lines
        if not line.startswith("<!--") and line not in {"---"}
    ]
    matched = [line for line in informative if any(term_occurrences(line, term) for term in terms)]
    selected: list[str] = []
    for line in [*matched, *informative]:
        if line in selected:
            continue
        selected.append(line)
        if len("\n".join(selected)) >= limit:
            break
    return "\n".join(selected)[:limit]


def is_query_support_artifact(root: Path, path: Path, meta: dict[str, str]) -> bool:
    """Keep operational/support prose out of ordinary knowledge retrieval regardless of case layout."""
    normalized = "/" + relative_to_root(root, path).replace("\\", "/")
    artifact_tokens = set(re.findall(r"[a-z0-9]+", path.stem.casefold()))
    support_classes = {"report", "ledger", "audit", "guide", "presentation", "broadcast"}
    return (
        "/reports/" in normalized
        or "/notes/guide/" in normalized
        or meta.get("type", "") in {"boi/local-report", "boi/local-guide"}
        or bool(artifact_tokens & support_classes)
        or meta.get("knowledge_subtype", "") in QUERY_EXCLUDED_SUBTYPES
    )


def canonical_public_origin(origin_ref: str) -> bool:
    """Accept a canonical public URL or stable scholarly identifier, never a Local path or host."""
    value = origin_ref.strip()
    if not value:
        return False
    if PUBLIC_ORIGIN_IDENTIFIER_RE.fullmatch(value):
        return True
    parsed = urlparse(value)
    if parsed.scheme.casefold() not in {"http", "https"} or not parsed.hostname:
        return False
    if parsed.username is not None or parsed.password is not None:
        return False
    try:
        parsed.port
    except ValueError:
        return False
    hostname = parsed.hostname.casefold().rstrip(".")
    if not hostname:
        return False
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        try:
            ascii_hostname = hostname.encode("idna").decode("ascii")
        except UnicodeError:
            return False
        labels = ascii_hostname.split(".")
        if len(ascii_hostname) > 253 or len(labels) < 2:
            return False
        if any(not PUBLIC_DNS_LABEL_RE.fullmatch(label) for label in labels):
            return False
        suffix = labels[-1]
        if suffix in NON_PUBLIC_DNS_SUFFIXES:
            return False
        # Dependency-free public-domain sanity check: a DNS name needs a plausible
        # alphabetic or IDNA public suffix, not a numeric/internal pseudo-TLD.
        if len(suffix) < 2 or not (suffix.isalpha() or suffix.startswith("xn--")):
            return False
        return True
    return address.is_global


def stable_scholarly_identifier(origin_ref: str) -> str:
    """Return a deterministic DOI/arXiv/ACL identity when the reference declares one."""
    value = origin_ref.strip()
    match = PUBLIC_ORIGIN_IDENTIFIER_RE.fullmatch(value)
    if match:
        prefix, identifier = value.split(":", 1)
        return f"{prefix.casefold()}:{identifier.casefold()}"
    parsed = urlparse(value)
    hostname = (parsed.hostname or "").casefold().rstrip(".")
    path = parsed.path.strip("/")
    if hostname == "doi.org" and path.casefold().startswith("10."):
        return f"doi:{path.casefold()}"
    if hostname == "arxiv.org":
        arxiv = re.fullmatch(r"(?:abs|pdf)/(\d{4}\.\d{4,5}(?:v\d+)?)(?:\.pdf)?", path, re.IGNORECASE)
        if arxiv:
            return f"arxiv:{arxiv.group(1).casefold()}"
    if hostname == "aclanthology.org":
        acl_id = re.fullmatch(r"([A-Za-z0-9.-]+?)(?:\.pdf)?", path)
        if acl_id:
            return f"acl:{acl_id.group(1).casefold()}"
    return ""


def origin_matches_expected(origin_ref: str, expected_origin_ref: str) -> bool:
    """Match an exact declared URL, or the same accepted stable scholarly identity."""
    actual = origin_ref.strip()
    expected = expected_origin_ref.strip()
    if not canonical_public_origin(actual) or not canonical_public_origin(expected):
        return False
    if actual == expected:
        return True
    expected_identifier = stable_scholarly_identifier(expected)
    return bool(expected_identifier and stable_scholarly_identifier(actual) == expected_identifier)


def normalize_original_identity_bindings(bindings: object) -> list[dict[str, str]]:
    """Validate evidence ID + exact bytes + declared public-original identity bindings."""
    if bindings is None:
        return []
    if not isinstance(bindings, list):
        raise ValueError("original identity bindings must be a list")
    normalized: list[dict[str, str]] = []
    seen: set[str] = set()
    for raw in bindings:
        if not isinstance(raw, dict):
            raise ValueError("each original identity binding must be an object")
        evidence_id = str(raw.get("evidence_id", "")).strip()
        evidence_sha = str(raw.get("evidence_sha256", "")).strip().casefold()
        expected_origin = str(raw.get("expected_origin_ref", "")).strip()
        if not evidence_id or evidence_id in seen:
            raise ValueError("original identity bindings require unique evidence_id values")
        if not re.fullmatch(r"[0-9a-f]{64}", evidence_sha):
            raise ValueError(f"original identity binding requires evidence_sha256: {evidence_id}")
        if not canonical_public_origin(expected_origin):
            raise ValueError(f"original identity binding requires a public expected_origin_ref: {evidence_id}")
        seen.add(evidence_id)
        normalized.append(
            {
                "evidence_id": evidence_id,
                "evidence_sha256": evidence_sha,
                "expected_origin_ref": expected_origin,
            }
        )
    return normalized


def parse_original_binding_args(values: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for value in values:
        parts = value.split("|", 2)
        if len(parts) != 3:
            raise ValueError("--original-binding must be EVIDENCE_ID|SHA256|EXPECTED_ORIGIN_REF")
        rows.append(
            {
                "evidence_id": parts[0],
                "evidence_sha256": parts[1],
                "expected_origin_ref": parts[2],
            }
        )
    return normalize_original_identity_bindings(rows)


def original_identity_binding_matches(source: dict[str, object], binding: dict[str, str]) -> bool:
    return (
        str(source.get("evidence_id", "")) == binding["evidence_id"]
        and str(source.get("sha256", "")).casefold() == binding["evidence_sha256"]
        and origin_matches_expected(str(source.get("origin_ref", "")), binding["expected_origin_ref"])
    )


def query_source(
    root: Path,
    path: Path,
    text: str,
    meta: dict[str, str],
    terms: list[str],
    intent: str,
    case_id: str,
    *,
    force: bool = False,
    include_support: bool = False,
) -> dict[str, object] | None:
    lowered = text.casefold()
    matched = [term for term in terms if term_occurrences(lowered, term)]
    role = meta.get("knowledge_role", "")
    if not include_support and is_query_support_artifact(root, path, meta):
        return None
    is_evidence = meta.get("type") == "boi/local-evidence" or role == "evidence-sidecar"
    same_case = bool(case_id and meta.get("case_id") == case_id)
    if not force and not matched and not (same_case and not is_evidence and role in COMPILED_KNOWLEDGE_ROLES):
        return None
    term_score = sum(min(term_occurrences(lowered, term), 5) * 3 for term in matched)
    role_score = INTENT_ROLE_BOOSTS.get(intent, INTENT_ROLE_BOOSTS["general"]).get(role, 0)
    case_score = 4 if same_case and not is_evidence else 0
    source = {
        "type": "local-document",
        "layer": "evidence" if is_evidence else "compiled-wiki",
        "path": relative_to_root(root, path),
        "sha256": sha256_file(path),
        "boi_id": meta.get("boi_id", ""),
        "title": meta.get("title", path.stem),
        "description": meta.get("description", ""),
        "case_id": meta.get("case_id", ""),
        "knowledge_role": role,
        "claim_status": meta.get("claim_status", ""),
        "hypothesis_status": meta.get("hypothesis_status", ""),
        "hypothesis_id": meta.get("hypothesis_id", ""),
        "supports": [item for item in meta.get("supports", "").split("|") if item],
        "contradicts": [item for item in meta.get("contradicts", "").split("|") if item],
        "source_refs": parse_frontmatter_list(text, "source_refs"),
        "score": term_score + role_score + case_score,
        "matched_terms": matched,
        "excerpt": answer_excerpt(text, terms),
    }
    return source


def source_evidence_identity(
    root: Path,
    path: Path,
    text: str,
    meta: dict[str, str],
    terms: list[str],
) -> dict[str, object] | None:
    """Resolve a source-knowledge page to the immutable original it describes."""
    evidence_sha = meta.get("evidence_sha256", "").lower()
    raw_path_text = meta.get("raw_path", "")
    evidence_id = meta.get("evidence_id", "")
    if not evidence_id or not re.fullmatch(r"[0-9a-f]{64}", evidence_sha) or not raw_path_text:
        return None

    raw_path = Path(raw_path_text).expanduser()
    if not raw_path.is_absolute():
        raw_path = root / raw_path
    raw_path = raw_path.resolve()
    if not raw_path.is_file():
        integrity = "missing"
    elif sha256_file(raw_path) != evidence_sha:
        integrity = "mismatch"
    else:
        integrity = "verified"
    if integrity != "verified":
        return None

    lowered = text.casefold()
    matched = [term for term in terms if term_occurrences(lowered, term)]
    origin_ref = meta.get("origin_ref", "")
    return {
        "type": "local-source-evidence",
        "layer": "source-evidence",
        "path": relative_to_root(root, path),
        "source_note_path": relative_to_root(root, path),
        "source_note_sha256": sha256_file(path),
        "evidence_id": evidence_id,
        "evidence_type": meta.get("evidence_type", "document"),
        "title": meta.get("title", path.stem),
        "origin_ref": origin_ref,
        "evidence_authority": "canonical-public-original" if canonical_public_origin(origin_ref) else "local-evidence",
        "raw_path": raw_path_text,
        "sha256": evidence_sha,
        "raw_integrity": integrity,
        "claim_status": meta.get("claim_status", "observed"),
        "matched_terms": matched,
        "score": sum(min(term_occurrences(lowered, term), 5) * 3 for term in matched),
        "relations": ["source-lineage"],
        "relation_contexts": [],
    }


def build_query_pack(
    root: Path,
    employee_id: str,
    question: str,
    case_id: str,
    limit: int,
    remote_refs: list[str],
    query_scope: str = "ordinary",
    original_identity_bindings: object = None,
) -> dict[str, object]:
    terms = query_tokens(question)
    if not terms:
        raise ValueError("question must contain at least one searchable term")
    base = private_root(root, employee_id)
    intent = query_intent(question)
    purposes = query_purposes(question)
    facets = query_facets(question)
    if query_scope not in {"ordinary", "support"}:
        raise ValueError("query_scope must be ordinary or support")
    normalized_origin_bindings = normalize_original_identity_bindings(original_identity_bindings)
    origin_bindings_by_id = {row["evidence_id"]: row for row in normalized_origin_bindings}
    compiled_matches: list[dict[str, object]] = []
    evidence_matches: list[dict[str, object]] = []
    evidence_by_path: dict[str, dict[str, object]] = {}
    evidence_by_id: dict[str, dict[str, object]] = {}
    source_knowledge_by_path: dict[str, tuple[Path, str, dict[str, str]]] = {}
    documents: list[tuple[Path, str, dict[str, str]]] = []
    for path in active_markdown(base):
        text = path.read_text(encoding="utf-8", errors="replace")
        meta = parse_frontmatter(text)
        documents.append((path, text, meta))
    curated_case_knowledge = bool(case_id) and any(
        meta.get("case_id") == case_id
        and path.relative_to(base).parts[:2] == ("notes", "knowledge")
        for path, _, meta in documents
    )
    retrieval_scope = (
        "support"
        if query_scope == "support"
        else "ordinary-research"
        if curated_case_knowledge
        else "ordinary-local"
    )
    for path, text, meta in documents:
        if case_id and meta.get("case_id", "") not in {case_id, ""}:
            continue
        if query_scope == "ordinary" and path.relative_to(base).parts[:2] == ("notes", "review"):
            continue
        if curated_case_knowledge and query_scope == "ordinary":
            if path.relative_to(base).parts[:2] != ("notes", "knowledge"):
                continue
        source_identity = source_evidence_identity(root, path, text, meta, terms)
        if source_identity is not None:
            source_knowledge_by_path[relative_to_root(root, path)] = (path, text, meta)
        is_evidence = meta.get("type") == "boi/local-evidence" or meta.get("knowledge_role") == "evidence-sidecar"
        source = query_source(
            root,
            path,
            text,
            meta,
            terms,
            intent,
            case_id,
            force=bool(is_evidence and case_id and meta.get("case_id") == case_id),
            include_support=query_scope == "support",
        )
        if source is None:
            continue
        if source["layer"] == "evidence":
            evidence_by_path[str(source["path"])] = source
            evidence_id = meta.get("evidence_id", "")
            if evidence_id:
                evidence_by_id[evidence_id] = source
            if source["matched_terms"]:
                evidence_matches.append(source)
        else:
            compiled_matches.append(source)
    parsed_remote: list[dict[str, str]] = []
    for raw in remote_refs:
        if not REMOTE_REF_RE.fullmatch(raw):
            raise ValueError("--remote-ref must be BOI_ID|REVISION|VISIBILITY|TITLE")
        boi_id, revision, visibility, title = raw.split("|", 3)
        parsed_remote.append(
            {"type": "remote-boi", "boi_id": boi_id, "revision": revision, "visibility": visibility, "title": title}
        )
    compiled = sorted(compiled_matches, key=lambda item: (-int(item["score"]), str(item["path"])))[: max(1, limit)]
    source_evidence: list[dict[str, object]] = []
    source_evidence_keys: set[tuple[str, str]] = set()
    source_queue: list[tuple[str, str, int]] = []
    for item in compiled:
        source_queue.append((str(item["path"]), "direct-match", int(item["score"])))
        for ref in item.get("source_refs", []):
            source_queue.append((str(ref.get("ref", "")), str(item.get("title", "source-ref")), int(item["score"])))

    visited_source_notes: set[str] = set()
    while source_queue:
        path_key, relation_owner, owner_score = source_queue.pop(0)
        if path_key in visited_source_notes:
            continue
        registered = source_knowledge_by_path.get(path_key)
        if registered is None:
            continue
        visited_source_notes.add(path_key)
        source_path, source_text, source_meta = registered
        identity = source_evidence_identity(root, source_path, source_text, source_meta, terms)
        if identity is None:
            continue
        binding = origin_bindings_by_id.get(str(identity["evidence_id"]))
        identity["original_identity_binding"] = dict(binding) if binding else {}
        identity["origin_binding_valid"] = bool(binding and original_identity_binding_matches(identity, binding))
        identity["evidence_authority"] = (
            "canonical-public-original"
            if identity["origin_binding_valid"]
            else "public-origin-candidate"
            if canonical_public_origin(str(identity.get("origin_ref", "")))
            else "local-evidence"
        )
        identity_key = (str(identity["evidence_id"]), str(identity["sha256"]))
        source_match_score = int(identity.get("score", 0))
        combined_relevance = max(1, owner_score) + (source_match_score * 5)
        matched_facets = evidence_facet_matches(source_text, facets)
        facet_scores = evidence_facet_scores(source_text, facets)
        if identity_key not in source_evidence_keys:
            source_evidence_keys.add(identity_key)
            identity["evidence_relevance"] = combined_relevance
            identity["topic_relevance"] = max(1, owner_score)
            identity["direct_source_relevance"] = source_match_score
            identity["matched_facets"] = matched_facets
            identity["facet_scores"] = facet_scores
            identity["relation_contexts"] = [f"{relation_owner}:source-lineage"]
            source_evidence.append(identity)
        else:
            existing = next(
                item
                for item in source_evidence
                if (str(item["evidence_id"]), str(item["sha256"])) == identity_key
            )
            existing["evidence_relevance"] = max(int(existing["evidence_relevance"]), combined_relevance)
            contexts = set(existing.get("relation_contexts", []))
            contexts.add(f"{relation_owner}:source-lineage")
            existing["relation_contexts"] = sorted(contexts)
            existing["matched_facets"] = sorted(set(existing.get("matched_facets", [])) | set(matched_facets))
            existing_scores = dict(existing.get("facet_scores", {}))
            for facet, score in facet_scores.items():
                existing_scores[facet] = max(int(existing_scores.get(facet, 0)), score)
            existing["facet_scores"] = existing_scores
        for ref in parse_frontmatter_list(source_text, "source_refs"):
            source_queue.append((str(ref.get("ref", "")), str(identity["evidence_id"]), owner_score))

    ranked_source_evidence = sorted(
        source_evidence,
        key=lambda item: (-int(item.get("evidence_relevance", 0)), -int(item.get("score", 0)), str(item["evidence_id"])),
    )
    diversified_source_evidence: list[dict[str, object]] = []
    diversified_ids: set[tuple[str, str]] = set()
    for facet in facets:
        candidates = [
            item
            for item in ranked_source_evidence
            if facet in item.get("matched_facets", [])
            and (str(item["evidence_id"]), str(item["sha256"])) not in diversified_ids
        ]
        candidate = max(
            candidates,
            key=lambda item: (
                int(item.get("facet_scores", {}).get(facet, 0)),
                int(item.get("direct_source_relevance", 0)),
                int(item.get("evidence_relevance", 0)),
            ),
            default=None,
        )
        if candidate is not None:
            diversified_source_evidence.append(candidate)
            diversified_ids.add((str(candidate["evidence_id"]), str(candidate["sha256"])))
    for item in ranked_source_evidence:
        key = (str(item["evidence_id"]), str(item["sha256"]))
        if key in diversified_ids:
            continue
        diversified_source_evidence.append(item)
        diversified_ids.add(key)
    source_evidence = diversified_source_evidence[: max(4, min(8, limit))]
    referenced: dict[str, dict[str, object]] = {}
    reference_counts: dict[str, int] = {}
    reference_relations: dict[str, set[str]] = {}
    relation_contexts: dict[str, set[str]] = {}
    expansion_depth = 2 if intent in {"recurrence", "promotion"} else min(6, len(compiled))
    for item in compiled[:expansion_depth]:
        relation_owner = str(item.get("hypothesis_id") or item.get("knowledge_role") or item.get("title"))
        for ref in item.get("source_refs", []):
            target = evidence_by_path.get(str(ref.get("ref", "")))
            if target is None:
                continue
            path_key = str(target["path"])
            referenced[path_key] = target
            source_ref_weight = 3 if intent == "verification" and relation_owner in {"decision-record", "continuous-log"} else 1
            reference_counts[path_key] = reference_counts.get(path_key, 0) + source_ref_weight
            reference_relations.setdefault(path_key, set()).add("source_ref")
            relation_contexts.setdefault(path_key, set()).add(f"{relation_owner}:source_ref")
        for relation in ("supports", "contradicts"):
            for evidence_id in item.get(relation, []):
                target = evidence_by_id.get(str(evidence_id))
                if target is None:
                    continue
                path_key = str(target["path"])
                referenced[path_key] = target
                reference_counts[path_key] = reference_counts.get(path_key, 0) + 2
                reference_relations.setdefault(path_key, set()).add(relation)
                relation_contexts.setdefault(path_key, set()).add(f"{relation_owner}:{relation}")
    for item in evidence_matches:
        referenced[str(item["path"])] = item
        reference_counts[str(item["path"])] = reference_counts.get(str(item["path"]), 0) + 3
        reference_relations.setdefault(str(item["path"]), set()).add("term_match")
        relation_contexts.setdefault(str(item["path"]), set()).add("query:term_match")
    for path_key, item in referenced.items():
        item["evidence_relevance"] = reference_counts[path_key]
        item["relations"] = sorted(reference_relations[path_key])
        item["relation_contexts"] = sorted(relation_contexts[path_key])
    evidence_limit = max(4, min(8, limit))
    linked_evidence = sorted(
        referenced.values(),
        key=lambda item: (-int(item.get("evidence_relevance", 0)), -int(item["score"]), str(item["path"])),
    )[:evidence_limit]
    evidence = [*source_evidence, *linked_evidence][:evidence_limit]
    citation_display: list[dict[str, str]] = []
    displayed: set[str] = set()
    for item in evidence:
        evidence_id = str(item.get("evidence_id") or item.get("path", ""))
        if not evidence_id or evidence_id in displayed:
            continue
        displayed.add(evidence_id)
        display_row: dict[str, object] = {
            "display_id": f"[{len(citation_display) + 1}]",
            "evidence_id": evidence_id,
            "title": str(item.get("title", evidence_id)),
        }
        if item.get("layer") == "source-evidence" and item.get("original_identity_binding"):
            display_row["original_identity_binding"] = dict(item.get("original_identity_binding", {}))
        citation_display.append(display_row)
        if len(citation_display) == 5:
            break
    local = [*compiled, *evidence]
    return {
        "ok": True,
        "schema": QUERY_PACK_SCHEMA,
        "question": question,
        "query_intent": intent,
        "query_plan": {
            "primary_purpose": intent,
            "purposes": purposes,
            "facets": facets,
        },
        "retrieval_scope": retrieval_scope,
        "case_id": case_id,
        "profile_contract": {"okf_version": "0.1", "boi_profile_version": "0.1-local"},
        "compiled_sources": compiled,
        "evidence_sources": evidence,
        "citation_surface": {
            "display_map": citation_display,
            "rules": [
                "one evidence identity has one display number",
                "AI synthesis is not a source citation",
                "default answers hide absolute paths and full SHA256 values",
            ],
        },
        "local_sources": local,
        "remote_sources": parsed_remote,
        "read_order": [item["path"] for item in local],
        "answer_contract": {
            "analysis_requirements": [
                "direct_answer",
                "supporting_evidence",
                "counterevidence",
                "unknowns_and_limits",
                "next_checks",
                "confidence",
                "citations",
            ],
            "presentation": {
                "surface_style": "natural-expert",
                "conclusion_first": True,
                "fixed_outline_required": False,
                "evidence_receipt": "separate-on-request",
                "internal_audit_terms_hidden": True,
            },
            "presentation_critic": {
                "max_repairs": 1,
                "presentation_only": True,
                "may_change_evidence": False,
                "may_write_knowledge": False,
            },
            "citation_format": "local path + exact SHA256; remote BoI ID + revision + visibility",
            "rules": [
                "separate observed facts, inference, and human decision",
                "cite every material claim from this pack",
                "include counterevidence and unresolved items",
                "do not promote a supported contributor to confirmed root cause",
                "state when the retrieved Wiki is insufficient instead of filling gaps",
            ],
        },
        "mcp_mode": "read-only-references-provided" if parsed_remote else "not-used",
        "remote_mutation_allowed": False,
    }


def fingerprint_payload(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def answer_material_paragraphs(text: str) -> list[str]:
    """Return narrative answer paragraphs, excluding headings and the human-readable source list."""
    _, body = split_frontmatter(text)
    paragraphs: list[str] = []
    in_sources = False
    for part in re.split(r"\n\s*\n", body.strip()):
        cleaned = part.strip()
        if not cleaned:
            continue
        heading = re.fullmatch(r"#{1,6}\s+(.+)", cleaned)
        if heading:
            title = heading.group(1).strip().casefold()
            if title in {"sources", "source", "citations", "citation", "출처", "인용"}:
                in_sources = True
            continue
        if in_sources:
            continue
        paragraphs.append(cleaned)
    return paragraphs


def answer_receipt_path(answer_path: Path) -> Path:
    return answer_path.with_suffix(".receipt.json")


def create_answer_receipt(root: Path, employee_id: str, args: argparse.Namespace) -> dict[str, object]:
    """Bind an agent-composed Markdown answer to its grounded query plan without claiming semantic truth."""
    base = private_root(root, employee_id).resolve()

    def local_file(raw: str, label: str) -> Path:
        path = Path(raw).expanduser()
        if not path.is_absolute():
            path = root / path
        path = path.resolve()
        try:
            path.relative_to(base)
        except ValueError as exc:
            raise ValueError(f"{label} must stay inside the Local Private profile") from exc
        if not path.is_file():
            raise FileNotFoundError(path)
        return path

    answer_path = local_file(args.answer_file, "answer file")
    bindings_path = local_file(args.claim_bindings_file, "claim bindings file")
    answer_text = answer_path.read_text(encoding="utf-8")
    paragraphs = answer_material_paragraphs(answer_text)
    if not paragraphs:
        raise ValueError("answer has no material narrative paragraphs")
    raw_bindings = json.loads(bindings_path.read_text(encoding="utf-8"))
    if isinstance(raw_bindings, dict):
        raw_bindings = raw_bindings.get("claim_bindings", [])
    if not isinstance(raw_bindings, list):
        raise ValueError("claim bindings must be a JSON list")

    pack = build_query_pack(
        root,
        employee_id,
        args.question,
        require_case_id(args.case_id) if args.case_id else "",
        args.limit,
        [],
        args.query_scope,
        parse_original_binding_args(args.original_binding),
    )
    display_map = list((pack.get("citation_surface") or {}).get("display_map", []))
    display_to_evidence = {
        str(row.get("display_id", "")): str(row.get("evidence_id", "")) for row in display_map
    }
    evidence_by_id = {
        str(row.get("evidence_id", "")): row
        for row in pack.get("evidence_sources", [])
        if row.get("evidence_id")
    }
    evidence: list[dict[str, str]] = []
    for row in display_map:
        evidence_id = str(row.get("evidence_id", ""))
        source = evidence_by_id.get(evidence_id)
        if source is None:
            raise ValueError(f"citation display map does not resolve to source evidence: {evidence_id}")
        binding = source.get("original_identity_binding") or {}
        if str(source.get("evidence_authority", "")) != "local-evidence":
            missing = [
                key
                for key in ("evidence_id", "evidence_sha256", "expected_origin_ref")
                if not str(binding.get(key, "")).strip()
            ]
            if missing or not source.get("origin_binding_valid"):
                detail = (
                    ", ".join(missing)
                    if missing
                    else "origin does not match the declared original identity"
                )
                raise ValueError(
                    f"answer receipt requires a valid original identity binding for {evidence_id} "
                    f"({detail}); provide --original-binding EVIDENCE_ID|SHA256|EXPECTED_ORIGIN_REF"
                )
        evidence.append(
            {
                "evidence_id": evidence_id,
                "path": str(source.get("path", "")),
                "sha256": str(source.get("sha256", "")),
                "origin_ref": str(source.get("origin_ref", "")),
                "original_identity_binding": dict(binding),
            }
        )

    normalized_bindings: list[dict[str, object]] = []
    seen_indices: set[int] = set()
    allowed_kinds = {"supported-claim", "counterevidence", "uncertainty", "local-policy"}
    for raw_binding in raw_bindings:
        if not isinstance(raw_binding, dict):
            raise ValueError("each claim binding must be an object")
        index = int(raw_binding.get("paragraph_index", 0))
        if index < 1 or index > len(paragraphs) or index in seen_indices:
            raise ValueError("claim bindings must name each material paragraph exactly once")
        seen_indices.add(index)
        paragraph = paragraphs[index - 1]
        claim = str(raw_binding.get("claim", "")).strip()
        if not claim:
            raise ValueError("claim binding must declare the supported claim or uncertainty")
        kind = str(raw_binding.get("binding_kind", ""))
        if kind not in allowed_kinds:
            raise ValueError(f"binding_kind must be one of {sorted(allowed_kinds)}")
        citations = [str(value) for value in raw_binding.get("citations", [])]
        paragraph_citations = re.findall(r"\[\d+\]", paragraph)
        if (
            len(paragraph_citations) != len(set(paragraph_citations))
            or len(citations) != len(set(citations))
            or citations != paragraph_citations
            or any(citation not in display_to_evidence for citation in citations)
        ):
            raise ValueError(
                "claim binding citations must be unique, deterministic, and exactly equal to the visible paragraph markers"
            )
        if kind not in {"uncertainty", "local-policy"} and not citations:
            raise ValueError("supported claims and counterevidence require at least one citation")
        normalized_bindings.append(
            {
                "paragraph_index": index,
                "paragraph_sha256": hashlib.sha256(paragraph.encode("utf-8")).hexdigest(),
                "binding_kind": kind,
                "claim": claim,
                "citations": citations,
                "evidence_ids": [display_to_evidence[citation] for citation in citations],
            }
        )
    if seen_indices != set(range(1, len(paragraphs) + 1)):
        raise ValueError("every material answer paragraph requires a claim binding")
    normalized_bindings.sort(key=lambda row: int(row["paragraph_index"]))

    receipt_path = answer_receipt_path(answer_path)
    receipt = {
        "schema": ANSWER_GENERATION_RECEIPT_SCHEMA,
        "question_sha256": hashlib.sha256(args.question.encode("utf-8")).hexdigest(),
        "query_plan_fingerprint": fingerprint_payload(pack.get("query_plan", {})),
        "citation_display_map_fingerprint": fingerprint_payload(display_map),
        "evidence": evidence,
        "answer": {
            "path": relative_to_root(root, answer_path),
            "bytes": len(answer_path.read_bytes()),
            "sha256": sha256_file(answer_path),
        },
        "composer": "natural-expert",
        "presentation_critic": {"passes": args.critic_passes, "max_passes": 1},
        "material_paragraph_count": len(paragraphs),
        "claim_bindings": normalized_bindings,
        "local_only": True,
        "remote_mutations": 0,
    }
    atomic_write(receipt_path, json.dumps(receipt, ensure_ascii=False, indent=2) + "\n")
    return {
        "ok": True,
        "schema": ANSWER_GENERATION_RECEIPT_SCHEMA,
        "receipt_path": relative_to_root(root, receipt_path),
        "answer_sha256": receipt["answer"]["sha256"],
        "claim_binding_count": len(normalized_bindings),
        "local_only": True,
        "remote_submitted": False,
    }


def save_query(root: Path, employee_id: str, args: argparse.Namespace) -> dict[str, object]:
    case_id = require_case_id(args.case_id) if args.case_id else ""
    answer_path = Path(args.answer_file).expanduser().resolve()
    if not answer_path.is_file():
        raise FileNotFoundError(answer_path)
    answer = answer_path.read_text(encoding="utf-8").strip()
    if not answer:
        raise ValueError("answer file is empty")
    base = private_root(root, employee_id)
    citations: list[tuple[Path, dict[str, str]]] = []
    for raw in args.citation:
        path = (root / raw).resolve()
        try:
            path.relative_to(base.resolve())
        except ValueError as exc:
            raise ValueError(f"citation must stay inside the Local Private profile: {raw}") from exc
        if not path.is_file() or "_archive" in path.relative_to(base).parts:
            raise ValueError(f"citation is missing or archived: {raw}")
        citations.append((path, parse_frontmatter(path.read_text(encoding="utf-8", errors="replace"))))
    if not citations:
        raise ValueError("query-save requires at least one --citation")
    current = now_kst()
    target_dir = base / "notes" / "knowledge" / "queries"
    target = target_dir / f"{current.strftime('%Y%m%d-%H%M%S')}-{slugify(args.question)}.md"
    source_refs = [
        {"type": "local-document", "ref": relative_to_root(root, path), "sha256": sha256_file(path)}
        for path, _ in citations
    ]
    fm = local_frontmatter(
        employee_id=employee_id,
        doc_type="boi/local-knowledge-note",
        title=args.title.strip() or args.question.strip(),
        description=f"출처가 고정된 Local Wiki query: {args.question.strip()}",
        boi_id=f"boi:private:{employee_id}:query:{current.strftime('%Y%m%d%H%M%S')}:{slugify(args.question)}",
        tags=["second-brain", "llm-wiki", "saved-query", *( [case_id.lower()] if case_id else [])],
        source_refs=source_refs,
        generated_from=source_refs,
        memory_candidate=True,
        review_after_days=14,
        extra={
            "case_id": case_id,
            "knowledge_role": "saved-query",
            "claim_status": args.claim_status,
            "answer_confidence": args.confidence,
        },
    )
    body = [f"\n# {args.title.strip() or args.question.strip()}", "", "## 질문", "", args.question.strip(), "", "## 답변", "", answer, "", "## 출처", ""]
    for path, meta in citations:
        link = Path(os.path.relpath(path, target_dir)).as_posix()
        body.append(f"- [{meta.get('title', path.stem)}]({link}) — `{sha256_file(path)}`")
    body.extend(["", "## 반증", "", args.contradiction.strip() or "- 확인된 반증 없음", "", "## 미확인 항목", "", args.unknown.strip() or "- 추가 확인 항목 없음", ""])
    if case_id:
        hub = case_dir(root, employee_id, case_id) / "case-hub.md"
        if not hub.is_file():
            raise FileNotFoundError(hub)
        body.extend([f"Case: [{case_id} Case Hub]({Path(os.path.relpath(hub, target_dir)).as_posix()})", ""])
    atomic_write(target, fm + "\n".join(body))
    append_index_link(base / "notes" / "knowledge" / "index.md", args.title.strip() or args.question.strip(), f"queries/{target.name}")
    append_log(root, f"Local Wiki query 저장: [{args.question.strip()}]({relative_to_root(root, target)}). 원격 전송 없음.")
    return {
        "ok": True,
        "path": relative_to_root(root, target),
        "citation_count": len(citations),
        "local_only": True,
        "remote_submitted": False,
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--employee-id", default="")
    sub = parser.add_subparsers(dest="command", required=True)

    preview = sub.add_parser("ingest-preview")
    preview.add_argument("--case-id", required=True)
    preview.add_argument("--evidence-id", required=True)

    apply = sub.add_parser("ingest-apply")
    apply.add_argument("--case-id", required=True)
    apply.add_argument("--evidence-id", required=True)
    apply.add_argument("--confirm-plan-hash", required=True)

    curate = sub.add_parser(
        "curate-knowledge",
        help="administrator/reference Local-only curation; previews by default and never submits Remote changes",
    )
    curate.add_argument("--case-id", required=True)
    curate.add_argument("--title", required=True)
    curate.add_argument("--claim", required=True)
    curate.add_argument("--claim-status", choices=["observed", "inferred"], required=True)
    curate.add_argument("--source-path", required=True)
    curate.add_argument("--source-sha256", required=True)
    curate.add_argument("--evidence-sha256", required=True)
    curate.add_argument("--current-path", default="")
    curate.add_argument("--material-change", action="store_true")
    curate.add_argument("--conflict", action="store_true")
    curate.add_argument("--confidence", choices=["low", "medium", "high"], default="medium")
    curate.add_argument("--inference-support", choices=["supported", "unsupported"], default="supported")
    curate.add_argument("--contains-sensitive", action="store_true")
    curate.add_argument("--sharing-scope-change", action="store_true")
    curate_execution = curate.add_mutually_exclusive_group()
    curate_execution.add_argument("--preview", action="store_true")
    curate_execution.add_argument("--apply-local", action="store_true")

    query = sub.add_parser("query-pack")
    query.add_argument("--question", required=True)
    query.add_argument("--case-id", default="")
    query.add_argument("--limit", type=int, default=12)
    query.add_argument("--remote-ref", action="append", default=[])
    query.add_argument("--query-scope", choices=["ordinary", "support"], default="ordinary")
    query.add_argument("--original-binding", action="append", default=[])

    receipt = sub.add_parser(
        "answer-receipt",
        help="administrator/reference validation receipt for an agent-composed grounded Markdown answer",
    )
    receipt.add_argument("--question", required=True)
    receipt.add_argument("--case-id", default="")
    receipt.add_argument("--answer-file", required=True)
    receipt.add_argument("--claim-bindings-file", required=True)
    receipt.add_argument("--limit", type=int, default=8)
    receipt.add_argument("--query-scope", choices=["ordinary", "support"], default="ordinary")
    receipt.add_argument("--critic-passes", type=int, choices=[0, 1], default=0)
    receipt.add_argument("--original-binding", action="append", default=[])

    save = sub.add_parser("query-save")
    save.add_argument("--question", required=True)
    save.add_argument("--title", default="")
    save.add_argument("--case-id", default="")
    save.add_argument("--answer-file", required=True)
    save.add_argument("--citation", action="append", default=[])
    save.add_argument("--contradiction", default="")
    save.add_argument("--unknown", default="")
    save.add_argument("--confidence", choices=["low", "medium", "high"], default="medium")
    save.add_argument("--claim-status", choices=["inferred", "decision"], default="inferred")

    health = sub.add_parser("wiki-lint")
    health.add_argument("--include-archive", action="store_true")

    args = parser.parse_args()
    root = Path(args.root).resolve()
    try:
        employee_id, _ = workspace_employee_id(root, args.employee_id)
        if args.command == "ingest-preview":
            payload = build_ingest_plan(root, employee_id, args.case_id, args.evidence_id)
        elif args.command == "ingest-apply":
            payload = apply_ingest(root, employee_id, args.case_id, args.evidence_id, args.confirm_plan_hash)
        elif args.command == "curate-knowledge":
            payload = curate_knowledge(
                root,
                employee_id,
                case_id=args.case_id,
                title=args.title,
                claim=args.claim,
                source_path=root / args.source_path,
                source_sha256=args.source_sha256,
                evidence_sha256=args.evidence_sha256,
                claim_status=args.claim_status,
                current_path=root / args.current_path if args.current_path else None,
                material_change=args.material_change,
                conflict=args.conflict,
                confidence=args.confidence,
                inference_support=args.inference_support,
                contains_sensitive=args.contains_sensitive,
                sharing_scope_change=args.sharing_scope_change,
                apply_local=args.apply_local,
            )
        elif args.command == "query-pack":
            payload = build_query_pack(
                root,
                employee_id,
                args.question,
                args.case_id,
                args.limit,
                args.remote_ref,
                args.query_scope,
                parse_original_binding_args(args.original_binding),
            )
        elif args.command == "answer-receipt":
            payload = create_answer_receipt(root, employee_id, args)
        elif args.command == "query-save":
            payload = save_query(root, employee_id, args)
        else:
            payload = lint_workspace(root, employee_id, include_archive=args.include_archive)
    except (ValueError, FileNotFoundError, FileExistsError) as exc:
        print(json.dumps({"ok": False, "error": str(exc), "remote_submitted": False}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("ok", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
