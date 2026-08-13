#!/usr/bin/env python3
"""Operate the OKF + BoI Profile Local LLM Wiki without remote mutation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
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
    sha256_file,
    slugify,
    split_frontmatter,
    workspace_employee_id,
)
from local_case import case_dir, refresh_case_hub_evidence, require_case_id
from local_lint import active_markdown, lint_workspace

INGEST_PLAN_SCHEMA = "boi-local-wiki-ingest-plan/v1"
QUERY_PACK_SCHEMA = "boi-local-wiki-query-pack/v2"
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
INTENT_KEYWORDS = {
    "recurrence": {"재발", "반복", "유사", "fingerprint", "recurrence", "again"},
    "decision": {"결론", "판단", "원인", "기여", "root", "supported", "지지", "현재"},
    "hypothesis": {"가설", "약화", "반증", "기각", "hypothesis", "weakened", "rejected"},
    "verification": {"검증", "확인", "다음", "추가", "누락", "미확인", "next", "missing", "verify"},
    "promotion": {"공유", "team", "public", "promotion", "승인", "sanitize"},
    "history": {"시간", "변경", "경과", "로그", "timeline", "history", "언제"},
}
INTENT_ROLE_BOOSTS = {
    "recurrence": {"recurrence-fingerprint": 30, "decision-record": 8, "hypothesis": 5},
    "decision": {"decision-record": 60, "hypothesis": 14, "case-hub": 4, "continuous-log": 5},
    "hypothesis": {"hypothesis": 60, "decision-record": 18, "case-hub": 4, "continuous-log": 4},
    "verification": {"decision-record": 12, "hypothesis": 10, "comparison": 8, "continuous-log": 6},
    "promotion": {"decision-record": 60, "recurrence-fingerprint": 18, "case-hub": 4},
    "history": {"continuous-log": 18, "timeline": 14, "decision-record": 6},
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
    return [token.lower() for token in re.findall(r"[0-9A-Za-z가-힣._-]+", question) if len(token) > 1]


def query_intent(question: str) -> str:
    lowered = question.lower()
    scores = {
        intent: sum(1 for keyword in keywords if keyword in lowered)
        for intent, keywords in INTENT_KEYWORDS.items()
    }
    best = max(scores, key=scores.get)
    return best if scores[best] else "general"


def answer_excerpt(text: str, terms: list[str], limit: int = 900) -> str:
    """Return a compact human-readable excerpt without treating it as a generated answer."""
    _, body = split_frontmatter(text)
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    informative = [
        line for line in lines
        if not line.startswith("<!--") and line not in {"---"}
    ]
    matched = [line for line in informative if any(term in line.lower() for term in terms)]
    selected: list[str] = []
    for line in [*matched, *informative]:
        if line in selected:
            continue
        selected.append(line)
        if len("\n".join(selected)) >= limit:
            break
    return "\n".join(selected)[:limit]


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
) -> dict[str, object] | None:
    lowered = text.lower()
    matched = [term for term in terms if term in lowered]
    role = meta.get("knowledge_role", "")
    is_evidence = meta.get("type") == "boi/local-evidence" or role == "evidence-sidecar"
    same_case = bool(case_id and meta.get("case_id") == case_id)
    if not force and not matched and not (same_case and not is_evidence and role in COMPILED_KNOWLEDGE_ROLES):
        return None
    term_score = sum(min(lowered.count(term), 5) * 3 for term in matched)
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


def build_query_pack(
    root: Path,
    employee_id: str,
    question: str,
    case_id: str,
    limit: int,
    remote_refs: list[str],
) -> dict[str, object]:
    terms = query_tokens(question)
    if not terms:
        raise ValueError("question must contain at least one searchable term")
    base = private_root(root, employee_id)
    intent = query_intent(question)
    compiled_matches: list[dict[str, object]] = []
    evidence_matches: list[dict[str, object]] = []
    evidence_by_path: dict[str, dict[str, object]] = {}
    evidence_by_id: dict[str, dict[str, object]] = {}
    for path in active_markdown(base):
        text = path.read_text(encoding="utf-8", errors="replace")
        meta = parse_frontmatter(text)
        if case_id and meta.get("case_id") not in {case_id, ""}:
            continue
        is_evidence = meta.get("type") == "boi/local-evidence" or meta.get("knowledge_role") == "evidence-sidecar"
        source = query_source(root, path, text, meta, terms, intent, case_id, force=bool(is_evidence and case_id and meta.get("case_id") == case_id))
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
    evidence = sorted(
        referenced.values(),
        key=lambda item: (-int(item.get("evidence_relevance", 0)), -int(item["score"]), str(item["path"])),
    )[:evidence_limit]
    local = [*compiled, *evidence]
    return {
        "ok": True,
        "schema": QUERY_PACK_SCHEMA,
        "question": question,
        "query_intent": intent,
        "case_id": case_id,
        "profile_contract": {"okf_version": "0.1", "boi_profile_version": "0.1-local"},
        "compiled_sources": compiled,
        "evidence_sources": evidence,
        "local_sources": local,
        "remote_sources": parsed_remote,
        "read_order": [item["path"] for item in local],
        "answer_contract": {
            "required_sections": [
                "direct_answer",
                "supporting_evidence",
                "counterevidence",
                "unknowns_and_limits",
                "next_checks",
                "confidence",
                "citations",
            ],
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
            payload = build_query_pack(root, employee_id, args.question, args.case_id, args.limit, args.remote_ref)
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
