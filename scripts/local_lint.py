#!/usr/bin/env python3
"""Validate Local Private OKF, BoI Profile, provenance, links, and wiki health."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import unquote

from boi_local_common import (
    MARKDOWN_LINK_RE,
    REQUIRED_LOCAL_FIELDS,
    parse_frontmatter,
    parse_frontmatter_list,
    private_root,
    relative_to_root,
    split_frontmatter,
    verify_locked_source,
    workspace_employee_id,
)

WIKILINK_RE = re.compile(r"\[\[[^\]]+\]\]")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REMOTE_PREFIXES = ("http://", "https://", "mailto:", "boi:", "plugin://")
ALLOWED_KNOWLEDGE_ROLES = {
    "agent-memory",
    "case-hub",
    "evidence-sidecar",
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
    "source-record",
}
CANONICAL_EVIDENCE_TYPES = {
    "email", "web-clip", "tabular-data", "document", "image",
    "meeting-note", "analysis-export",
}
DEPRECATED_EVIDENCE_TYPES = {
    "outlook-email", "analysis-report", "analysis-image",
    "wafer-map-image", "external-source-note",
}
ALLOWED_CLAIM_STATES = {"observed", "inferred", "direct", "conflicted", "decision", "open-question", "superseded"}
ALLOWED_LOCAL_TYPES = {
    "boi/dictionary-term",  # explicit legacy-compatible local fixture
    "boi/local-action-draft",
    "boi/local-analysis-case",
    "boi/local-analysis-log",
    "boi/local-capture",
    "boi/local-context-pack",
    "boi/local-diagram",
    "boi/local-event-plan",
    "boi/local-evidence",
    "boi/local-example",
    "boi/local-guide",
    "boi/local-hypothesis",
    "boi/local-knowledge-note",
    "boi/local-langflow-plan",
    "boi/local-note",
    "boi/local-promotion-draft",
    "boi/local-recurrence-fingerprint",
    "boi/local-report",
    "boi/local-sop-draft",
    "boi/local-workflow-simulation",
}
ALLOWED_PROFILE_FIELDS = {
    "aliases", "answer_confidence", "archive_status", "artifact_visibility", "boi_id", "boi_profile_version",
    "candidate_sha256", "capture_kind", "case_id", "case_status", "claim_status",
    "classification", "cleanup_policy", "contains_sensitive", "contradicts", "decision_owner",
    "definition", "description", "domain", "domain_persona_validated", "employee_id", "evidence_id",
    "evidence_sha256", "evidence_type", "examples", "expected_revision", "fingerprint_status",
    "generated_from", "guide_audience", "guide_boundary", "guide_duration_minutes", "guide_execution",
    "guide_failure_page", "guide_next_page", "guide_prerequisites", "guide_release", "guide_success",
    "harness_checksum", "harness_release", "hypothesis_id", "hypothesis_status", "idempotency_key",
    "intake_method", "investigation_question", "knowledge_role", "knowledge_subtype", "lifecycle_state",
    "links", "local_only", "local_owner_ref", "log_entry_count", "memory_candidate", "memory_key",
    "memory_kind", "memory_operation", "memory_status",
    "most_supported_hypothesis", "okf_version", "origin_ref", "original_filename", "owner",
    "promotion_reason", "promotion_status", "raw_path", "related_terms", "remote_submit_allowed",
    "requires_explicit_user_approval", "retention_class", "retention_until", "review_after",
    "review_status", "reviewed_at", "reviewer", "sensitivity", "source_hash_scope",
    "source_immutability", "source_refs", "source_sha256", "status", "supports", "tags", "target_visibility",
    "team_id", "term", "term_kind", "timestamp", "title", "type", "visibility",
}
HARNESS_CARD_REQUIRED_SECTIONS = (
    ("## 1. User request and outcome", ("## 1. User request and outcome", "## 1. 사용자 요청과 결과")),
    ("## 2. Audit and change preview", ("## 2. Audit and change preview", "## 2. 감사와 변경 미리보기")),
    ("## 3. Knowledge flow", ("## 3. Knowledge flow", "## 3. 지식 흐름")),
    ("## 4. Reused Skills and ownership", ("## 4. Reused Skills and ownership", "## 4. 재사용 Skills와 책임")),
    ("## 5. Roles and independent review", ("## 5. Roles and independent review", "## 5. 역할과 독립 검토")),
    ("## 6. Dependency DAG and handoffs", ("## 6. Dependency DAG and handoffs", "## 6. 의존 DAG와 인계")),
    ("## 7. Scale modes", ("## 7. Scale modes", "## 7. 실행 규모")),
    ("## 8. Artifact contracts", ("## 8. Artifact contracts", "## 8. 산출물 계약")),
    ("## 9. Error, fallback, and resume", ("## 9. Error, fallback, and resume", "## 9. 오류, 대안과 재개")),
    ("## 10. OKF, BoI, and Local/Remote boundary", ("## 10. OKF, BoI, and Local/Remote boundary", "## 10. OKF, BoI와 Local/Remote 경계")),
    ("## 11. Non-developer walkthrough", ("## 11. Non-developer walkthrough", "## 11. 비개발자 사용 순서")),
    ("## 12. Validation and status", ("## 12. Validation and status", "## 12. 검증과 상태")),
    ("## 13. Evolution record", ("## 13. Evolution record", "## 13. 개선 이력")),
)
HARNESS_CARD_REQUIRED_SIGNALS = (
    ("copyable request", ("copyable one-sentence request:", "복사 가능한 한 문장 요청:")),
    ("target user and recurring work", ("target user and recurring work:", "대상 사용자와 반복 업무:")),
    ("reusable result", ("reusable result:", "재사용 결과:")),
    ("measurable success", ("measurable success:", "측정 가능한 성공:")),
    ("failure conditions", ("failure conditions and exclusions:", "실패 조건과 제외 범위:")),
    ("factory mode", ("mode:", "모드:")),
    ("complete knowledge flow", ("capture → distill → query → lint → review",)),
    ("capture and source integrity", ("capture and source integrity:", "수집과 출처 무결성:")),
    ("distilled reusable knowledge", ("distilled reusable knowledge:", "정제된 재사용 지식:")),
    ("human review cadence", ("human review and review cadence:", "사람 검토와 검토 주기:")),
    ("Skill ownership decision", ("new generic skill proposal:", "새 범용 skill 제안:")),
    ("reviewer authority", ("reviewer authority:", "reviewer 권한:", "검토자 권한:")),
    ("Single-agent reviewer independence", ("how reviewer independence is preserved in single-agent mode:", "single-agent 모드의 검토 독립성:")),
    ("DAG phase exits", ("phase exits:", "단계 종료 조건:")),
    ("hash-bound handoff contract", ("required handoff fields and source hashes:", "필수 인계 필드와 출처 hash:")),
    ("Single-agent mode", ("| single-agent |",)),
    ("Reduced mode", ("| reduced |",)),
    ("Full mode", ("| full |",)),
    ("No-team fallback", ("| no-team fallback |",)),
    ("input artifact contract", ("| input |",)),
    ("intermediate artifact contract", ("| intermediate |",)),
    ("final Local artifact contract", ("| final local |",)),
    ("missing-input behavior", ("missing input:", "입력 누락:")),
    ("access-denied fallback", ("access denied or unavailable external system:", "접근 거부 또는 외부 시스템 사용 불가:")),
    ("interrupted-run resume marker", ("interrupted run and resume marker:", "중단 후 재개 표식:")),
    ("conflicting-evidence review path", ("conflicting evidence and review-required path:", "충돌 근거와 검토 필요 경로:")),
    ("Local OKF and BoI contract", ("okf 0.1 + boi profile 0.1-local",)),
    ("remote sanitization contract", ("sanitization rules for local paths, ids, raw source, and sensitive content:", "local 경로·id·원문·민감정보 제거 규칙:")),
    ("exact promotion candidate hash", ("exact candidate hash", "정확한 candidate hash")),
    ("approval invalidation conditions", ("user approval and approval invalidation conditions:", "사용자 승인과 승인 무효화 조건:")),
    ("saved Harness card path", ("notes/harnesses/",)),
    ("next-session activation request", ("copyable next-session request", "다음 세션 요청문")),
    ("trigger and near-miss boundary", ("trigger and near-miss boundary:", "trigger와 near-miss 경계:")),
    ("independent review evidence", ("independent review evidence:", "독립 검토 evidence:")),
    ("external validation evidence", ("runtime, user, and actual boi wiki evidence:", "runtime·사용자·실제 boi wiki evidence:")),
    ("honest status boundary", ("current status and claims that remain prohibited:", "현재 상태와 금지된 주장:")),
    ("previous Harness evolution lineage", ("previous harness version:", "이전 harness 버전:")),
    ("approved Harness change preview", ("approved change preview:", "승인한 변경 미리보기:")),
    ("Harness evolution approval reason", ("change reason and user approval:", "변경 이유와 사용자 승인:")),
    ("smallest evolution owner", ("smallest owning layer:", "가장 작은 소유 계층:")),
    ("preserved failure evidence", ("preserved failure evidence:", "보존한 실패 evidence:")),
    ("generic Skill promotion evidence threshold", ("evidence needed before promoting behavior into a generic skill:", "범용 skill 승격 전 필요한 evidence:")),
    ("next review owner and date", ("next review owner and date:", "다음 검토 책임자와 날짜:")),
)
HARNESS_CARD_PLACEHOLDER_RE = re.compile(
    r"(?:<[^>\n]+>|\b(?:todo|tbd)\b|concrete contract for)",
    re.IGNORECASE,
)
HARNESS_CARD_UNSELECTED_CHOICES = (
    ("mode", re.compile(r"create\s*\|\s*extend\s*\|\s*audit\s*\|\s*evolve\s*\|\s*evaluate", re.IGNORECASE)),
    (
        "evolution owner",
        re.compile(
            r"case method\s*\|\s*orchestration\s*\|\s*generic skill\s*\|\s*fixture or prompt\s*\|\s*validator\s*\|\s*runtime",
            re.IGNORECASE,
        ),
    ),
)


def active_markdown(base: Path, include_archive: bool = False) -> list[Path]:
    paths: list[Path] = []
    for path in sorted(base.rglob("*.md")):
        parts = path.relative_to(base).parts
        if ".obsidian" in parts or ("_archive" in parts and not include_archive):
            continue
        if parts and parts[0] == "evidence" and "sources" in parts:
            # Markdown web clips under sources are immutable raw bytes. Their
            # OKF evidence sidecars own profile metadata and hash validation.
            continue
        paths.append(path)
    return paths


def resolve_local_ref(root: Path, source: Path, raw: str) -> Path | None:
    target = unquote(raw.split("#", 1)[0].strip().strip("<>"))
    if not target or target.startswith(REMOTE_PREFIXES):
        return None
    if target.startswith("data/") or target.startswith("templates/") or target.startswith("fixtures/") or target.startswith("research/"):
        return (root / target).resolve()
    return (source.parent / target).resolve()


def markdown_link_issues(root: Path, path: Path, text: str) -> tuple[list[str], set[Path]]:
    issues: list[str] = []
    targets: set[Path] = set()
    if WIKILINK_RE.search(text):
        issues.append("Obsidian wikilink is not allowed; use a standard Markdown link with an explicit file extension")
    for _, raw_target in MARKDOWN_LINK_RE.findall(text):
        target = resolve_local_ref(root, path, raw_target)
        if target is None:
            continue
        targets.add(target)
        if not target.exists():
            issues.append(f"broken Markdown link: {raw_target}")
    return issues, targets


def provenance_issues(root: Path, path: Path, text: str, meta: dict[str, str]) -> list[str]:
    issues: list[str] = []
    for item in parse_frontmatter_list(text, "source_refs"):
        ref = str(item.get("ref", "")).strip()
        source_type = str(item.get("type", "")).strip()
        source_hash = str(item.get("sha256", "")).strip()
        if not ref:
            issues.append("source_refs item is missing ref")
            continue
        if source_hash and not SHA256_RE.fullmatch(source_hash):
            issues.append(f"source_refs item has invalid SHA256: {ref}")
        if source_type not in {"local-file", "local-document"}:
            continue
        # Symbolic identifiers remain legal, but path-shaped local references
        # must resolve. This preserves compatibility with older operational IDs.
        if not (ref.startswith(("data/", "../", "./")) or Path(ref).suffix):
            continue
        target = resolve_local_ref(root, path, ref)
        if target is not None and not target.exists():
            issues.append(f"source_refs target is missing: {ref}")

    generated_items = parse_frontmatter_list(text, "generated_from")
    for item in generated_items:
        ref = str(item.get("ref", "")).strip()
        source_type = str(item.get("type", "")).strip()
        source_hash = str(item.get("sha256", "")).strip()
        if not source_type:
            issues.append("generated_from item is missing type")
        if not ref:
            issues.append("generated_from item is missing ref")
        if not source_hash:
            issues.append(f"generated_from item is missing SHA256: {ref or '<unknown>'}")
        elif not SHA256_RE.fullmatch(source_hash):
            issues.append(f"generated_from item has invalid SHA256: {ref or '<unknown>'}")
        if not ref or source_type not in {"local-file", "local-document", "local-private"}:
            continue
        target = resolve_local_ref(root, path, ref)
        if target is None:
            continue
        if not target.exists():
            issues.append(f"generated_from target is missing: {ref}")
            continue
        if target.is_file() and SHA256_RE.fullmatch(source_hash):
            actual_hash = hashlib.sha256(target.read_bytes()).hexdigest()
            if actual_hash != source_hash:
                issues.append(
                    f"generated_from hash mismatch: {ref}; expected {source_hash}, got {actual_hash}"
                )

    # Older Local documents may point to a capture by BoI ID or a scalar path.
    # Keep that representation readable while all newly structured provenance
    # receives the stronger path + exact SHA256 validation above.
    generated_from = meta.get("generated_from", "").strip()
    if not generated_items and generated_from and not generated_from.startswith("boi:"):
        target = resolve_local_ref(root, path, generated_from)
        if target is not None and not target.exists():
            issues.append(f"generated_from target is missing: {generated_from}")
    return issues


def configured_harness_issues(base: Path, path: Path, text: str, meta: dict[str, str]) -> list[str]:
    try:
        parts = path.relative_to(base).parts
    except ValueError:
        return []
    if len(parts) < 3 or parts[:2] != ("notes", "harnesses"):
        return []

    issues: list[str] = []
    if meta.get("type") != "boi/local-guide":
        issues.append("configured Harness card must use boi/local-guide")
    if not parse_frontmatter_list(text, "generated_from"):
        issues.append("configured Harness card requires structured generated_from")
    _, body = split_frontmatter(text)
    for section, alternatives in HARNESS_CARD_REQUIRED_SECTIONS:
        if not any(alternative in body for alternative in alternatives):
            issues.append(f"configured Harness card missing section: {section}")
    placeholder = HARNESS_CARD_PLACEHOLDER_RE.search(body)
    if placeholder:
        issues.append(f"configured Harness card contains placeholder text: {placeholder.group(0)}")
    for label, pattern in HARNESS_CARD_UNSELECTED_CHOICES:
        if pattern.search(body):
            issues.append(f"configured Harness card contains unselected choice list: {label}")
    factory_mode = re.search(r"(?im)^-\s*(?:Mode|모드):\s*`?([a-z-]+)`?\s*$", body)
    if factory_mode and factory_mode.group(1).lower() not in {"create", "extend", "audit", "evolve", "evaluate"}:
        issues.append(f"configured Harness card has invalid factory mode: {factory_mode.group(1)}")
    normalized_body = body.lower()
    for label, alternatives in HARNESS_CARD_REQUIRED_SIGNALS:
        if not any(signal.lower() in normalized_body for signal in alternatives):
            issues.append(f"configured Harness card missing substantive contract signal: {label}")

    previous = re.search(
        r"(?im)^-\s*(?:Previous Harness version|이전 Harness 버전):\s*(.+)$",
        body,
    )
    if previous:
        value = previous.group(1).strip()
        initial = value.lower().startswith("none (initial creation)") or value.startswith("없음 (최초 생성)")
        if not initial:
            normalized_value = value.replace("\\", "/")
            archive_match = re.search(r"(?:^|[\s`])([^\s`]*_archive/harnesses/[^\s`]+)", normalized_value)
            hash_match = re.search(r"\b[0-9a-f]{64}\b", value)
            if not archive_match or not hash_match:
                issues.append(
                    "configured Harness evolution must name none for initial creation or an archived previous card path with exact SHA256"
                )
            else:
                previous_path = archive_match.group(1).lstrip("./")
                previous_hash = hash_match.group(0)
                generated_items = parse_frontmatter_list(text, "generated_from")
                if not any(
                    str(item.get("ref", "")).replace("\\", "/").endswith(previous_path)
                    and str(item.get("sha256", "")) == previous_hash
                    for item in generated_items
                ):
                    issues.append(
                        "configured Harness evolution requires the archived previous card path and SHA256 in structured generated_from"
                    )

    approved_preview = re.search(
        r"(?im)^-\s*(?:Approved change preview|승인한 변경 미리보기):\s*(.+)$",
        body,
    )
    if approved_preview:
        value = approved_preview.group(1).strip()
        if not re.search(r"\b[0-9a-f]{64}\b", value) or not re.search(r"(?i)approved|승인", value):
            issues.append("configured Harness evolution requires an exact approved change preview SHA256")

    change_reason = re.search(
        r"(?im)^-\s*(?:Change reason and user approval|변경 이유와 사용자 승인):\s*(.+)$",
        body,
    )
    if change_reason and not re.search(r"(?i)approved|승인", change_reason.group(1)):
        issues.append("configured Harness evolution requires an explicit user approval state")
    return issues


def configured_harness_index_issues(
    root: Path,
    base: Path,
    documents: list[tuple[Path, str, dict[str, str]]],
) -> list[dict[str, str]]:
    harness_dir = base / "notes" / "harnesses"
    cards = [
        path
        for path, _, _ in documents
        if path.parent == harness_dir and path.name != "index.md"
    ]
    if not cards:
        return []

    index = harness_dir / "index.md"
    if not index.is_file():
        return [{
            "path": relative_to_root(root, index),
            "issue": "configured Harness index is missing; active cards must be discoverable in the next session",
        }]

    index_text = index.read_text(encoding="utf-8", errors="replace")
    _, targets = markdown_link_issues(root, index, index_text)
    resolved_targets = {target.resolve() for target in targets}
    return [
        {
            "path": relative_to_root(root, card),
            "issue": "active configured Harness card is missing from notes/harnesses/index.md as a standard Markdown link",
        }
        for card in cards
        if card.resolve() not in resolved_targets
    ]


def lint_document(root: Path, base: Path, employee_id: str, path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    link_issues, _ = markdown_link_issues(root, path, text)
    if path.name == "index.md" or path == base / "inbox.md":
        return link_issues
    if not text.strip():
        return ["zero-byte or empty Profile document"]
    header, _ = split_frontmatter(text)
    if not header:
        return ["missing YAML frontmatter", *link_issues]
    meta = parse_frontmatter(text)
    errors = [f"missing field: {field}" for field in REQUIRED_LOCAL_FIELDS if field not in meta]
    expected = {
        "okf_version": "0.1",
        "boi_profile_version": "0.1-local",
        "visibility": "local-private",
        "local_only": "true",
        "archive_status": "active",
        "employee_id": employee_id,
        "local_owner_ref": f"local-private:{employee_id}",
    }
    for field, value in expected.items():
        if field in meta and meta[field] != value:
            errors.append(f"{field} must be {value!r}, got {meta[field]!r}")
    document_type = meta.get("type", "")
    if document_type and document_type not in ALLOWED_LOCAL_TYPES:
        errors.append(f"type is not allowed by the Local schema: {document_type}")
    for field in sorted(set(meta) - ALLOWED_PROFILE_FIELDS):
        errors.append(f"field is not allowed by the Local schema: {field}")
    if meta.get("promotion_status") not in {"local_only", "pending_user_approval", "promotion_ready"}:
        errors.append("promotion_status is not a supported local state")
    if meta.get("lifecycle_state") not in {"working", "memory", "background", "archived", "delete_candidate", "protected"}:
        errors.append("lifecycle_state is invalid")
    role = meta.get("knowledge_role", "")
    if role and role not in ALLOWED_KNOWLEDGE_ROLES:
        errors.append(f"knowledge_role is not allowed by the Local schema: {role}")
    claim_status = meta.get("claim_status", "")
    if claim_status and claim_status not in ALLOWED_CLAIM_STATES:
        errors.append(f"claim_status is not allowed by the Local schema: {claim_status}")
    if role == "agent-memory":
        if document_type != "boi/local-knowledge-note":
            errors.append("agent-memory must use boi/local-knowledge-note")
        if meta.get("memory_status") not in {"active", "provisional", "superseded", "review-required"}:
            errors.append("agent-memory memory_status is invalid")
        if meta.get("memory_kind") not in {"preference", "decision", "procedure", "resolved-problem", "open-loop"}:
            errors.append("agent-memory memory_kind is invalid")
        if meta.get("promotion_status") != "local_only":
            errors.append("agent-memory cannot be promotion-ready")
        if meta.get("memory_operation") not in {"append-evidence", "revise", "supersede", "create", "queue-review"}:
            errors.append("agent-memory memory_operation is invalid")
    locked_ok, locked_message = verify_locked_source(text, meta)
    if not locked_ok:
        errors.append(locked_message)
    if meta.get("type") == "boi/local-evidence":
        for field in ("case_id", "evidence_id", "evidence_type", "evidence_sha256", "raw_path", "origin_ref", "intake_method"):
            if not meta.get(field):
                errors.append(f"missing evidence field: {field}")
        raw_path = meta.get("raw_path", "")
        evidence_type = meta.get("evidence_type", "")
        if evidence_type not in CANONICAL_EVIDENCE_TYPES | DEPRECATED_EVIDENCE_TYPES:
            errors.append(f"unsupported evidence_type: {evidence_type}")
        if raw_path:
            raw = (root / raw_path).resolve()
            try:
                raw.relative_to(base.resolve())
            except ValueError:
                errors.append("raw evidence path must stay inside the Local Private profile")
            else:
                if not raw.is_file():
                    errors.append("raw evidence file is missing")
                else:
                    digest = hashlib.sha256(raw.read_bytes()).hexdigest()
                    if digest != meta.get("evidence_sha256"):
                        errors.append(f"evidence hash mismatch: expected {meta.get('evidence_sha256', '')}, got {digest}")
    if role == "source-record":
        if document_type != "boi/local-note":
            errors.append("source-record must use boi/local-note")
        for field in ("evidence_id", "evidence_type", "evidence_sha256", "raw_path", "origin_ref", "intake_method"):
            if not meta.get(field):
                errors.append(f"missing source-record field: {field}")
        if meta.get("evidence_type", "") not in CANONICAL_EVIDENCE_TYPES:
            errors.append("source-record evidence_type must use a generic evidence category")
        raw_path = meta.get("raw_path", "")
        if raw_path:
            raw = (root / raw_path).resolve()
            try:
                raw.relative_to(base.resolve())
            except ValueError:
                errors.append("source-record raw path must stay inside the Local Private profile")
            else:
                if not raw.is_file():
                    errors.append("source-record raw file is missing")
                elif hashlib.sha256(raw.read_bytes()).hexdigest() != meta.get("evidence_sha256"):
                    errors.append("source-record evidence hash mismatch")
    errors.extend(link_issues)
    errors.extend(provenance_issues(root, path, text, meta))
    errors.extend(configured_harness_issues(base, path, text, meta))
    return sorted(set(errors))


def case_health(
    documents: list[tuple[Path, str, dict[str, str]]],
    root: Path,
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    evidence_by_case: dict[str, dict[str, Path]] = {}
    hubs: dict[str, tuple[Path, str]] = {}
    downstream_evidence: set[str] = set()
    hypothesis_states: dict[str, list[tuple[Path, str]]] = {}
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    for path, text, meta in documents:
        case_id = meta.get("case_id", "")
        if meta.get("type") == "boi/local-evidence":
            evidence_by_case.setdefault(case_id, {})[meta.get("evidence_id", "")] = path
        if meta.get("type") == "boi/local-analysis-case":
            hubs[case_id] = (path, text)
        for ref in parse_frontmatter_list(text, "source_refs"):
            note = str(ref.get("note", ""))
            match = re.search(r"\bE-[A-F0-9]{12}\b", note)
            if match and meta.get("knowledge_role") not in {"case-hub", "evidence-sidecar"}:
                downstream_evidence.add(match.group(0))

    for path, _, meta in documents:
        if meta.get("type") != "boi/local-hypothesis":
            continue
        case_id = meta.get("case_id", "")
        supports = {item for item in meta.get("supports", "").split("|") if item}
        contradicts = {item for item in meta.get("contradicts", "").split("|") if item}
        downstream_evidence.update(supports | contradicts)
        hypothesis_id = meta.get("hypothesis_id", "")
        if hypothesis_id:
            hypothesis_states.setdefault(hypothesis_id, []).append((path, meta.get("hypothesis_status", "")))
        if not supports and not contradicts:
            warnings.append({"path": relative_to_root(root, path), "issue": "hypothesis has no supporting or contradicting evidence"})
        for item in sorted(supports & contradicts):
            warnings.append({"path": relative_to_root(root, path), "issue": f"evidence {item} is listed as both support and contradiction"})
        known = evidence_by_case.get(case_id, {})
        for item in sorted((supports | contradicts) - set(known)):
            warnings.append({"path": relative_to_root(root, path), "issue": f"unknown evidence reference for {case_id}: {item}"})

    for hypothesis_id, states in sorted(hypothesis_states.items()):
        distinct = {status for _, status in states if status}
        if len(distinct) > 1:
            paths = ", ".join(relative_to_root(root, path) for path, _ in states)
            warnings.append({"path": paths, "issue": f"contradicting hypothesis states for {hypothesis_id}: {', '.join(sorted(distinct))}"})

    for case_id, items in evidence_by_case.items():
        hub = hubs.get(case_id)
        if not hub:
            for evidence_id, path in items.items():
                errors.append({"path": relative_to_root(root, path), "issue": f"case hub is missing for {case_id} ({evidence_id})"})
            continue
        hub_path, hub_text = hub
        for evidence_id, evidence_path in items.items():
            if evidence_path.name not in hub_text:
                errors.append({"path": relative_to_root(root, hub_path), "issue": f"Case Hub is missing evidence link: {evidence_id}"})
            if evidence_id not in downstream_evidence:
                warnings.append({"path": relative_to_root(root, evidence_path), "issue": f"evidence is not reflected in any downstream compiled page: {evidence_id}"})
    return errors, warnings


def lint_workspace(root: Path, employee_id: str, *, include_archive: bool = False) -> dict[str, object]:
    base = private_root(root, employee_id)
    if not base.exists():
        return {"ok": False, "employee_id": employee_id, "errors": [{"path": relative_to_root(root, base), "issues": ["private root is missing"]}]}
    errors: list[dict[str, object]] = []
    warnings: list[dict[str, str]] = []
    documents: list[tuple[Path, str, dict[str, str]]] = []
    inbound: dict[Path, int] = {}
    ids: dict[str, list[Path]] = {}
    paths = active_markdown(base, include_archive)
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        meta = parse_frontmatter(text)
        documents.append((path, text, meta))
        boi_id = meta.get("boi_id", "")
        if boi_id:
            ids.setdefault(boi_id, []).append(path)
        _, targets = markdown_link_issues(root, path, text)
        for target in targets:
            inbound[target] = inbound.get(target, 0) + 1
        issues = lint_document(root, base, employee_id, path)
        if issues:
            errors.append({"path": relative_to_root(root, path), "issues": issues})
        if meta.get("type") == "boi/local-evidence" and meta.get("evidence_type") in DEPRECATED_EVIDENCE_TYPES:
            warnings.append({
                "path": relative_to_root(root, path),
                "issue": f"deprecated evidence_type remains readable but new intake should use a generic type: {meta.get('evidence_type')}",
            })

    for boi_id, duplicate_paths in ids.items():
        if len(duplicate_paths) > 1:
            errors.append(
                {
                    "path": relative_to_root(root, duplicate_paths[0]),
                    "issues": [f"duplicate active boi_id: {boi_id} ({len(duplicate_paths)} documents)"],
                }
            )

    for item in configured_harness_index_issues(root, base, documents):
        errors.append({"path": item["path"], "issues": [item["issue"]]})

    case_errors, case_warnings = case_health(documents, root)
    for item in case_errors:
        errors.append({"path": item["path"], "issues": [item["issue"]]})
    warnings.extend(case_warnings)

    today = date.today().isoformat()
    for path, _, meta in documents:
        if not meta.get("boi_id") or path.name == "index.md":
            continue
        if inbound.get(path.resolve(), 0) == 0 and meta.get("knowledge_role") not in {"case-hub"}:
            warnings.append({"path": relative_to_root(root, path), "issue": "orphan Profile page has no inbound Markdown link"})
        if meta.get("claim_status") in {"inferred", "decision"} and meta.get("review_after", "") < today:
            warnings.append({"path": relative_to_root(root, path), "issue": "stale claim review date elapsed"})

    return {
        "ok": not errors,
        "employee_id": employee_id,
        "include_archive": include_archive,
        "checked": len(paths),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--employee-id", default="")
    parser.add_argument("--include-archive", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    try:
        employee_id, _ = workspace_employee_id(root, args.employee_id)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    payload = lint_workspace(root, employee_id, include_archive=args.include_archive)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
