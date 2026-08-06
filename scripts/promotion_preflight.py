#!/usr/bin/env python3
"""Build a local-only BoI Wiki promotion preview and canonical package.

This command never submits remotely.  It produces three Local Private files:

* a human-readable Markdown preview;
* a package containing local provenance plus the canonical candidate; and
* a sanitized remote projection that excludes local paths and employee IDs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from boi_local_common import (
    append_index_link,
    append_log,
    atomic_write,
    workspace_employee_id,
    local_frontmatter,
    now_kst,
    parse_frontmatter,
    private_root,
    relative_to_root,
    require_private_path,
    sha256_text,
    slugify,
    split_frontmatter,
    verify_locked_source,
)

PACKAGE_SCHEMA = "boi-local-promotion-package/v1"
REMOTE_SCHEMA = "boi-wiki-promotion-projection/v1"
SECRET_PATTERNS = {
    "secret-like value": re.compile(r"(?i)(password|secret|token|api[_ -]?key)\s*[:=]\s*['\"]?[^\s,'\"]+"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "authorization header": re.compile(r"(?i)authorization\s*:\s*(?:bearer|basic)\s+\S+"),
}
EMPLOYEE_ID_PATTERN = re.compile(r"(?<![0-9])[0-9]{7}(?![0-9])")
INTERNAL_PATH_PATTERN = re.compile(r"(?:\\\\wsl\$\\|/home/[^/]+/|[A-Z]:\\\\Users\\\\[^\\]+\\\\|data/boi/private/)", re.IGNORECASE)
CITATION_PATTERN = re.compile(r"(?:https?://[^\s)>,]+|boi:[A-Za-z0-9:._-]+)")
CANONICAL_TYPE_MAP: dict[str, tuple[str, str]] = {
    "boi/local-knowledge": ("boi/knowledge", ""),
    "boi/local-knowledge-note": ("boi/knowledge", ""),
    "boi/local-guide": ("boi/public-guide", ""),
    "boi/local-recurrence-fingerprint": ("boi/knowledge", "recurrence-fingerprint"),
    "boi/local-context-pack": ("boi/context-pack", ""),
    "boi/local-sop": ("boi/sop", ""),
    "boi/local-sop-draft": ("boi/sop", ""),
}
NON_PROMOTABLE_LOCAL_TYPES = {
    "boi/local-evidence",
    "boi/local-capture",
    "boi/local-hypothesis",
    "boi/local-analysis-log",
    "boi/local-analysis-case",
}
NON_PROMOTABLE_KNOWLEDGE_ROLES = {"agent-memory", "source-record"}
CONFIGURED_HARNESS_BLOCKER = (
    "configured Local Harness cards cannot be promoted directly; distill a generic guide "
    "or package a reviewed Community Case first"
)


def check_workspace(root: Path, employee_id: str) -> dict[str, object]:
    base = private_root(root, employee_id)
    required = [base / "promotion-drafts", base / "notes"]
    missing = [relative_to_root(root, path) for path in required if not path.exists()]
    return {"ok": not missing, "employee_id": employee_id, "missing": missing}


def is_configured_harness_card(source_path: Path, base: Path, source_meta: dict[str, str]) -> bool:
    try:
        parts = source_path.resolve().relative_to(base.resolve()).parts
    except ValueError:
        parts = ()
    path_owned = len(parts) >= 3 and parts[:2] == ("notes", "harnesses")
    tag_owned = "ConfiguredHarness" in source_meta.get("tags", "")
    return path_owned or tag_owned


def has_nonempty_source_refs(source_text: str) -> bool:
    header, _ = split_frontmatter(source_text)
    match = re.search(r"(?ms)^source_refs:\s*(.*?)(?=^[A-Za-z_][A-Za-z0-9_-]*:|\Z)", header)
    if not match:
        return False
    value = match.group(1).strip()
    return bool(value and value != "[]" and re.search(r"(?m)^\s+(?:-\s+)?ref:\s*\S+", value))


def parse_explicit_source_ref(raw: str) -> dict[str, str]:
    """Parse TYPE=REF or TYPE|REF|NOTE into a canonical source reference."""
    if "|" in raw:
        parts = [part.strip() for part in raw.split("|", 2)]
        if len(parts) < 2 or not parts[0] or not parts[1]:
            raise ValueError("--source-ref must be TYPE=REF or TYPE|REF|NOTE")
        result = {"type": parts[0], "ref": parts[1]}
        if len(parts) == 3 and parts[2]:
            result["note"] = parts[2]
        return result
    if "=" not in raw:
        raise ValueError("--source-ref must be TYPE=REF or TYPE|REF|NOTE")
    source_type, ref = (part.strip() for part in raw.split("=", 1))
    if not source_type or not ref:
        raise ValueError("--source-ref must contain a non-empty type and ref")
    return {"type": source_type, "ref": ref}


def is_remote_safe_ref(ref: dict[str, str]) -> bool:
    value = str(ref.get("ref", ""))
    serialized = json.dumps(ref, ensure_ascii=False)
    if not value or INTERNAL_PATH_PATTERN.search(serialized) or EMPLOYEE_ID_PATTERN.search(serialized):
        return False
    return value.startswith(("https://", "http://", "boi:"))


def is_public_safe_ref(ref: dict[str, str]) -> bool:
    value = str(ref.get("ref", "")).strip().lower()
    return value.startswith(("https://", "http://", "boi:public:"))


def structured_source_refs(candidate_body: str, explicit: list[str]) -> tuple[list[dict[str, str]], list[str]]:
    refs: list[dict[str, str]] = []
    errors: list[str] = []
    for raw in explicit:
        try:
            item = parse_explicit_source_ref(raw)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if not is_remote_safe_ref(item):
            errors.append(f"source ref is not remote-safe: {item.get('ref', '')}")
            continue
        refs.append(item)
    for citation in sorted(set(CITATION_PATTERN.findall(candidate_body))):
        item = {
            "type": "url" if citation.startswith(("https://", "http://")) else "boi",
            "ref": citation,
            "note": "citation from sanitized promotion candidate",
        }
        if is_remote_safe_ref(item):
            refs.append(item)
    unique: dict[tuple[str, str], dict[str, str]] = {}
    for item in refs:
        unique[(item["type"], item["ref"])] = item
    return list(unique.values()), errors


def findings_for(
    candidate_body: str,
    source_text: str,
    target_visibility: str,
    team_id: str,
    reviewer: str,
    remote_refs: list[dict[str, str]],
) -> tuple[list[str], list[str]]:
    blockers = [label for label, pattern in SECRET_PATTERNS.items() if pattern.search(candidate_body)]
    warnings: list[str] = []
    if not has_nonempty_source_refs(source_text):
        blockers.append("source_refs is missing or empty in the Local Private source")
    if not reviewer.strip():
        blockers.append("Team/Public promotion requires --reviewer")
    if target_visibility == "team" and not team_id.strip():
        blockers.append("Team promotion requires --team-id")
    if not remote_refs:
        blockers.append("Team/Public candidate needs at least one structured remote-safe source_ref")
    if target_visibility == "public":
        non_public_refs = sorted(
            str(item.get("ref", "")) for item in remote_refs if not is_public_safe_ref(item)
        )
        if non_public_refs:
            blockers.append(
                "Public candidate contains non-public source_refs: " + ", ".join(non_public_refs)
            )
        if remote_refs and not any(is_public_safe_ref(item) for item in remote_refs):
            blockers.append("Public candidate needs at least one public URL or boi:public source_ref")
    if EMPLOYEE_ID_PATTERN.search(candidate_body):
        blockers.append("7-digit employee ID may be present")
    if INTERNAL_PATH_PATTERN.search(candidate_body):
        blockers.append("Local Private or user path may be present")
    if target_visibility == "public" and re.search(r"(?i)internal|사내|team only|confidential", candidate_body):
        warnings.append("internal-scope wording needs public-scope review")
    return sorted(set(blockers)), sorted(set(warnings))


def harness_contract(root: Path) -> dict[str, str]:
    lock_path = root / "harness.lock"
    if not lock_path.exists():
        return {"release": "missing", "checksum": "missing"}
    try:
        payload = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"release": "invalid", "checksum": "invalid"}
    return {"release": str(payload.get("release", "missing")), "checksum": str(payload.get("checksum", "missing"))}


def canonical_candidate(
    *,
    source_meta: dict[str, str],
    body: str,
    target_visibility: str,
    team_id: str,
    reviewer: str,
    source_refs: list[dict[str, str]],
    promotion_reason: str,
    candidate_body_sha: str,
    timestamp: str,
    canonical_type: str,
    knowledge_subtype: str = "",
) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "okf_version": "0.1",
        "boi_profile_version": "0.1",
        "type": canonical_type,
        "title": source_meta.get("title", "Promoted BoI document"),
        "description": source_meta.get("description", "Promoted BoI document"),
        "tags": ["BoI", "PromotionCandidate"],
        "timestamp": timestamp,
        "boi_id": f"boi:{target_visibility}:pending:{candidate_body_sha[:12]}",
        "boi_id_assignment": "remote",
        "visibility": target_visibility,
        # BoI Wiki separates publication scope (visibility) from information
        # classification. Public documents still use an allowed BoI
        # classification value; the public-source and sensitive-content gates
        # below decide whether the visibility may be public.
        "classification": "internal",
        "owner": "<authenticated-principal>",
        "owner_resolution": "authenticated-principal",
        "author": {"type": "human-or-agent", "agent_id": "boi-wiki-local"},
        "acl_policy": "<remote-derived>",
        "acl_resolution": "remote-from-authenticated-principal-and-target-scope",
        "status": "draft",
        "source_refs": source_refs,
        "review": {"reviewer": reviewer, "review_status": "pending"},
        "promotion": {"promotion_reason": promotion_reason, "candidate_body_sha256": candidate_body_sha},
    }
    if target_visibility == "team":
        metadata["team_id"] = team_id
    if knowledge_subtype:
        metadata["knowledge_subtype"] = knowledge_subtype
        metadata["tags"].append("RecurrenceFingerprint")
    return {"metadata": metadata, "body": body.strip() + "\n"}


def candidate_sha256(candidate: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(candidate, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--employee-id", default="")
    parser.add_argument("--source", default="")
    parser.add_argument("--sanitized-file", default="")
    parser.add_argument("--sanitized-title", default="")
    parser.add_argument("--sanitized-description", default="")
    parser.add_argument("--target-visibility", "--visibility", dest="target_visibility", choices=["team", "public"], default="team")
    parser.add_argument("--team-id", default="")
    parser.add_argument("--reviewer", default="")
    parser.add_argument("--promotion-reason", default="User explicitly requested promotion.")
    parser.add_argument("--source-ref", action="append", default=[], help="TYPE=REF or TYPE|REF|NOTE; repeatable")
    parser.add_argument("--expected-revision", default="")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    try:
        employee_id, _ = workspace_employee_id(root, args.employee_id)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    check = check_workspace(root, employee_id)
    if args.check:
        print(json.dumps(check, ensure_ascii=False, indent=2))
        return 0 if check["ok"] else 1
    if not check["ok"]:
        print(json.dumps(check, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1
    if not args.source:
        raise SystemExit("--source is required")

    source_path = require_private_path(root, employee_id, root / args.source)
    source_bytes = source_path.read_bytes()
    source_text = source_bytes.decode("utf-8")
    source_meta = parse_frontmatter(source_text)
    locked_ok, locked_message = verify_locked_source(source_text, source_meta)
    if not locked_ok:
        raise SystemExit(f"source integrity check failed: {locked_message}")
    _, source_body = split_frontmatter(source_text)
    candidate_body = Path(args.sanitized_file).resolve().read_text(encoding="utf-8") if args.sanitized_file else source_body
    candidate_meta = dict(source_meta)
    if args.sanitized_title.strip():
        candidate_meta["title"] = args.sanitized_title.strip()
    if args.sanitized_description.strip():
        candidate_meta["description"] = args.sanitized_description.strip()
    source_sha = hashlib.sha256(source_bytes).hexdigest()
    body_sha = sha256_text(candidate_body)
    remote_refs, ref_errors = structured_source_refs(candidate_body, args.source_ref)
    blockers, warnings = findings_for(
        candidate_body,
        source_text,
        args.target_visibility,
        args.team_id,
        args.reviewer,
        remote_refs,
    )
    sensitivity = str(source_meta.get("contains_sensitive", "unknown")).strip().lower() or "unknown"
    if sensitivity != "false":
        blockers.append(
            "Team/Public promotion requires contains_sensitive: false after review; "
            f"current value is {sensitivity}"
        )
    blockers.extend(ref_errors)
    local_type = source_meta.get("type", "")
    mapped = CANONICAL_TYPE_MAP.get(local_type)
    if local_type in NON_PROMOTABLE_LOCAL_TYPES:
        blockers.append(f"{local_type} must be distilled to a promotable OKF/BoI document type first")
    if source_meta.get("knowledge_role", "") in NON_PROMOTABLE_KNOWLEDGE_ROLES:
        blockers.append(
            f"{source_meta.get('knowledge_role')} is Local-only and must be distilled to ordinary knowledge, context pack, or SOP first"
        )
    elif mapped is None:
        blockers.append(f"no explicit canonical type mapping for Local type: {local_type or '<missing>'}")
    if is_configured_harness_card(source_path, private_root(root, employee_id), source_meta):
        blockers.append(CONFIGURED_HARNESS_BLOCKER)
    canonical_type, knowledge_subtype = mapped or ("boi/unsupported", "")
    harness = harness_contract(root)
    if harness["release"] in {"missing", "invalid"} or harness["checksum"] in {"missing", "invalid"}:
        blockers.append("valid Harness lock is required")

    current = now_kst()
    title = candidate_meta.get("title") or source_path.stem
    candidate = canonical_candidate(
        source_meta=candidate_meta,
        body=candidate_body,
        target_visibility=args.target_visibility,
        team_id=args.team_id,
        reviewer=args.reviewer,
        source_refs=remote_refs,
        promotion_reason=args.promotion_reason,
        candidate_body_sha=body_sha,
        timestamp=current.isoformat(),
        canonical_type=canonical_type,
        knowledge_subtype=knowledge_subtype,
    )
    case_id = source_meta.get("case_id", "").strip()
    remote_candidate_text = json.dumps(candidate, ensure_ascii=False)
    if case_id and case_id in remote_candidate_text:
        blockers.append("Local case ID remains in the canonical candidate; provide sanitized title, description, and body")
    if employee_id in remote_candidate_text:
        blockers.append("Local employee ID remains in the canonical candidate")
    if re.search(r"(?i)(?:data[/\\]boi[/\\]private|local-private|boi:private:|[A-Za-z]:[/\\]Users[/\\])", remote_candidate_text):
        blockers.append("Local path or Local Profile identifier remains in the canonical candidate")
    if re.search(r"(?i)(?:\blocal[\s_-]+private\b|\blocal_only\b|\blocal_owner_ref\b)", remote_candidate_text):
        blockers.append(
            "Local-only boundary wording remains in the canonical candidate; "
            "provide sanitized body and metadata"
        )
    exact_candidate_sha = candidate_sha256(candidate)
    idempotency_key = hashlib.sha256(
        f"{args.target_visibility}|{args.team_id}|{exact_candidate_sha}|{harness['checksum']}".encode("utf-8")
    ).hexdigest()
    submit_contract = {
        "principal": "authenticated-principal",
        "acl_resolution": "remote",
        "expected_revision": args.expected_revision or None,
        "expected_revision_status": "provided" if args.expected_revision else "required_at_submit",
        "idempotency_key": idempotency_key,
        "candidate_sha256": exact_candidate_sha,
        "harness_release": harness["release"],
        "harness_checksum": harness["checksum"],
        "user_confirmed": False,
        "remote_submit_allowed": False,
    }
    remote_projection = {"schema": REMOTE_SCHEMA, "candidate": candidate, "submit_contract": submit_contract}

    target_dir = private_root(root, employee_id) / "promotion-drafts"
    stem = (
        f"{current.strftime('%Y%m%d-%H%M%S')}-{slugify(title)}-"
        f"{args.target_visibility}-{exact_candidate_sha[:8]}-preflight"
    )
    preview_path = target_dir / f"{stem}.md"
    package_path = target_dir / f"{stem}.package.json"
    remote_path = target_dir / f"{stem}.remote.json"
    source_rel = relative_to_root(root, source_path)
    package = {
        "schema": PACKAGE_SCHEMA,
        "local_provenance": {
            "source_path": source_rel,
            "local_boi_id": source_meta.get("boi_id", ""),
            "source_sha256": source_sha,
            "candidate_body_sha256": body_sha,
            "candidate_sha256": exact_candidate_sha,
            "review_status": "blocked" if blockers else "preview_ready",
            "contains_sensitive": sensitivity,
        },
        "remote_projection": remote_projection,
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
    }
    frontmatter = local_frontmatter(
        employee_id=employee_id,
        doc_type="boi/local-promotion-draft",
        title=f"{title} promotion preflight",
        description="기존 BoI Wiki 호환 canonical candidate의 Local Private 검증 및 미리보기",
        boi_id=f"boi:private:{employee_id}:promotion-preflight:{current.strftime('%Y%m%d%H%M%S')}:{exact_candidate_sha[:12]}",
        tags=["LocalPrivate", "Promotion", "OKF", "BoIProfile"],
        source_refs=[{"type": "local-private", "ref": source_rel, "sha256": source_sha}],
        timestamp=current,
        promotion_status="pending_user_approval",
        retention_class="promoted_source",
        lifecycle_state="protected",
        memory_candidate=False,
        review_after_days=14,
        extra={
            "target_visibility": args.target_visibility,
            "candidate_sha256": exact_candidate_sha,
            "reviewer": args.reviewer,
            "review_status": "blocked" if blockers else "preview_ready",
            "harness_release": harness["release"],
            "harness_checksum": harness["checksum"],
            "idempotency_key": idempotency_key,
            "remote_submit_allowed": False,
            "requires_explicit_user_approval": True,
        },
    )
    report = (
        frontmatter
        + "\n# Promotion 미리보기\n\n"
        + f"- 대상 공개 범위: `{args.target_visibility}`\n"
        + f"- Team ID: `{args.team_id or '해당 없음'}`\n"
        + f"- 검토자: `{args.reviewer or '미지정'}`\n"
        + f"- Local 원문: `{source_rel}`\n"
        + f"- Local 원문 SHA256: `{source_sha}`\n"
        + f"- canonical candidate SHA256: `{exact_candidate_sha}`\n"
        + f"- Harness: `{harness['release']}` / `{harness['checksum']}`\n"
        + f"- 차단 항목: `{', '.join(sorted(set(blockers))) if blockers else '없음'}`\n"
        + f"- 경고: `{', '.join(sorted(set(warnings))) if warnings else '없음'}`\n\n"
        + "# Local → canonical 변환\n\n"
        + "- OKF `0.1`은 유지합니다.\n"
        + "- Local BoI Profile `0.1-local`은 canonical `0.1` candidate로 변환합니다.\n"
        + "- Local 경로, 사번, Local boi_id는 remote projection에서 제거합니다.\n"
        + "- 최종 owner, acl_policy, boi_id는 인증된 BoI Wiki가 결정합니다.\n\n"
        + "```json\n"
        + json.dumps(remote_projection, ensure_ascii=False, indent=2)
        + "\n```\n\n"
        + "# 정제된 후보 본문\n\n"
        + candidate_body.strip()
        + "\n\n# 원격 등록 경계\n\n"
        + "- 이 명령은 원격 등록을 실행하지 않습니다.\n"
        + "- 차단 항목을 해결하고 같은 candidate hash를 다시 확인해야 합니다.\n"
        + "- 사용자 승인 뒤에도 원격 promotion capability와 expected revision이 확인될 때만 제출할 수 있습니다.\n"
        + "- MCP 연결만으로 Local Private 문서가 자동 업로드되지 않습니다.\n"
    )
    result = {
        "ok": not blockers,
        "path": relative_to_root(root, preview_path),
        "package_path": relative_to_root(root, package_path),
        "remote_projection_path": relative_to_root(root, remote_path),
        "target_visibility": args.target_visibility,
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "source_refs": remote_refs,
        "candidate_sha256": exact_candidate_sha,
        "harness_release": harness["release"],
        "harness_checksum": harness["checksum"],
        "idempotency_key": idempotency_key,
        "requires_explicit_user_approval": True,
        "remote_submit_allowed": False,
        "remote_submitted": False,
        "dry_run": args.dry_run,
    }
    if args.dry_run:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if not blockers else 2

    atomic_write(preview_path, report)
    atomic_write(package_path, json.dumps(package, ensure_ascii=False, indent=2) + "\n")
    atomic_write(remote_path, json.dumps(remote_projection, ensure_ascii=False, indent=2) + "\n")
    append_index_link(target_dir / "index.md", f"{title} {args.target_visibility} promotion preflight", preview_path.name)
    append_log(root, f"Promotion 미리보기 생성: [{title}]({relative_to_root(root, preview_path)}), 대상 `{args.target_visibility}`, 원격 등록 안 함")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not blockers else 2


if __name__ == "__main__":
    raise SystemExit(main())
