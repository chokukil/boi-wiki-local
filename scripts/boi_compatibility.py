#!/usr/bin/env python3
"""Validate a promotion package against local and existing BoI Wiki contracts."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

LOCAL_ONLY_FIELDS = {
    "employee_id",
    "local_owner_ref",
    "local_only",
    "promotion_status",
    "artifact_visibility",
    "lifecycle_state",
    "review_after",
    "archive_status",
    "contains_sensitive",
}
REQUIRED_CANONICAL_FIELDS = {
    "okf_version",
    "boi_profile_version",
    "type",
    "title",
    "description",
    "timestamp",
    "boi_id",
    "visibility",
    "classification",
    "owner",
    "acl_policy",
    "status",
    "source_refs",
    "review",
}
INTERNAL_PATH_PATTERN = re.compile(r"(?:\\\\wsl\$\\|/home/[^/]+/|[A-Z]:\\\\Users\\\\[^\\]+\\\\|data/boi/private/)", re.IGNORECASE)
LOCAL_BOUNDARY_WORDING_PATTERN = re.compile(
    r"(?:\blocal[\s_-]+private\b|\blocal_only\b|\blocal_owner_ref\b)",
    re.IGNORECASE,
)
EMPLOYEE_ID_PATTERN = re.compile(r"(?<![0-9])[0-9]{7}(?![0-9])")


def contains_employee_id(value: Any, key: str = "") -> bool:
    """Scan semantic fields without treating timestamps or hashes as employee IDs."""
    ignored = {"timestamp", "candidate_sha256", "candidate_body_sha256", "harness_checksum", "idempotency_key"}
    if key in ignored or key.endswith("sha256"):
        return False
    if isinstance(value, dict):
        return any(contains_employee_id(child, str(child_key)) for child_key, child in value.items())
    if isinstance(value, list):
        return any(contains_employee_id(child, key) for child in value)
    if isinstance(value, str):
        if key == "boi_id" and ":pending:" in value:
            return False
        return bool(EMPLOYEE_ID_PATTERN.search(value))
    return False


def builtin_validate(projection: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if projection.get("schema") != "boi-wiki-promotion-projection/v1":
        errors.append("invalid remote projection schema")
    candidate = projection.get("candidate")
    if not isinstance(candidate, dict):
        return errors + ["candidate must be an object"]
    metadata = candidate.get("metadata")
    body = candidate.get("body")
    if not isinstance(metadata, dict) or not isinstance(body, str):
        return errors + ["candidate.metadata must be an object and candidate.body must be text"]
    for field in sorted(REQUIRED_CANONICAL_FIELDS - set(metadata)):
        errors.append(f"missing canonical field: {field}")
    if metadata.get("okf_version") != "0.1":
        errors.append("okf_version must be 0.1")
    if metadata.get("boi_profile_version") != "0.1":
        errors.append("boi_profile_version must be 0.1")
    if metadata.get("visibility") not in {"team", "public"}:
        errors.append("promotion visibility must be team or public")
    if metadata.get("status") != "draft":
        errors.append("promotion candidate status must be draft")
    if metadata.get("visibility") == "team" and not metadata.get("team_id"):
        errors.append("Team promotion requires team_id")
    refs = metadata.get("source_refs")
    if not isinstance(refs, list) or not refs:
        errors.append("source_refs must be a non-empty list")
    elif any(not isinstance(item, dict) or not item.get("type") or not item.get("ref") for item in refs):
        errors.append("each source_ref must contain type and ref")
    elif metadata.get("visibility") == "public":
        public_refs = []
        non_public_refs = []
        for item in refs:
            ref = str(item.get("ref", "")).strip().lower()
            if ref.startswith(("https://", "http://", "boi:public:")):
                public_refs.append(ref)
            else:
                non_public_refs.append(str(item.get("ref", "")))
        if non_public_refs:
            errors.append("Public projection contains non-public source_refs: " + ", ".join(sorted(non_public_refs)))
        if not public_refs:
            errors.append("Public projection requires at least one public URL or boi:public source_ref")
    review = metadata.get("review")
    if not isinstance(review, dict) or not review.get("reviewer") or review.get("review_status") != "pending":
        errors.append("promotion candidate requires pending review with reviewer")
    forbidden = sorted(LOCAL_ONLY_FIELDS & set(metadata))
    if forbidden:
        errors.append(f"canonical metadata contains Local-only fields: {', '.join(forbidden)}")
    serialized = json.dumps(projection, ensure_ascii=False)
    if INTERNAL_PATH_PATTERN.search(serialized):
        errors.append("remote projection contains a Local Private or user path")
    if LOCAL_BOUNDARY_WORDING_PATTERN.search(serialized):
        errors.append("remote projection contains Local-only boundary wording")
    if contains_employee_id(projection):
        errors.append("remote projection contains a 7-digit employee ID")
    submit = projection.get("submit_contract")
    if not isinstance(submit, dict):
        errors.append("submit_contract must be an object")
    else:
        for field in ("idempotency_key", "candidate_sha256", "harness_release", "harness_checksum"):
            if not submit.get(field):
                errors.append(f"submit_contract missing {field}")
        if submit.get("remote_submit_allowed") is not False or submit.get("user_confirmed") is not False:
            errors.append("preflight must keep remote submission and user confirmation false")
        exact_candidate_sha = hashlib.sha256(
            json.dumps(candidate, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        if submit.get("candidate_sha256") != exact_candidate_sha:
            errors.append("candidate_sha256 does not match the exact candidate")
        expected_idempotency = hashlib.sha256(
            f"{metadata.get('visibility', '')}|{metadata.get('team_id', '')}|{exact_candidate_sha}|{submit.get('harness_checksum', '')}".encode(
                "utf-8"
            )
        ).hexdigest()
        if submit.get("idempotency_key") != expected_idempotency:
            errors.append("idempotency_key does not match visibility, team, candidate, and Harness")
    return errors


def validate_harness_contract(projection: dict[str, Any], local_root: Path) -> list[str]:
    lock_path = local_root / "harness.lock"
    if not lock_path.exists():
        return [f"Harness lock not found: {lock_path}"]
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"Harness lock is invalid: {exc}"]
    submit = projection.get("submit_contract") or {}
    errors = []
    if submit.get("harness_release") != lock.get("release"):
        errors.append("Harness release does not match harness.lock")
    if submit.get("harness_checksum") != lock.get("checksum"):
        errors.append("Harness checksum does not match harness.lock")
    return errors


def load_boi_wiki_okf(boi_wiki_root: Path) -> ModuleType:
    module_path = boi_wiki_root / "boi_api" / "app" / "okf.py"
    if not module_path.exists():
        raise FileNotFoundError(f"BoI Wiki OKF validator not found: {module_path}")
    spec = importlib.util.spec_from_file_location("boi_wiki_contract_okf", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load BoI Wiki validator: {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate_with_boi_wiki(projection: dict[str, Any], boi_wiki_root: Path) -> list[str]:
    module = load_boi_wiki_okf(boi_wiki_root)
    metadata = projection["candidate"]["metadata"]
    errors = list(module.validate_okf_core_metadata(metadata))
    errors.extend(module.validate_boi_profile_metadata(metadata, promotion=True))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--projection", required=True)
    parser.add_argument("--boi-wiki-root", default=os.getenv("BOI_WIKI_ROOT", ""))
    parser.add_argument("--local-root", default=".")
    args = parser.parse_args()
    projection_path = Path(args.projection).resolve()
    projection = json.loads(projection_path.read_text(encoding="utf-8"))
    builtin_errors = builtin_validate(projection)
    builtin_errors.extend(validate_harness_contract(projection, Path(args.local_root).resolve()))
    external_errors: list[str] = []
    external_status = "not_requested"
    if args.boi_wiki_root:
        external_status = "checked"
        try:
            external_errors = validate_with_boi_wiki(projection, Path(args.boi_wiki_root).resolve())
        except Exception as exc:  # contract loading failures must fail closed
            external_errors = [f"BoI Wiki contract load failed: {exc}"]
            external_status = "failed"
    payload = {
        "ok": not builtin_errors and not external_errors,
        "projection": str(projection_path),
        "builtin_contract": {"ok": not builtin_errors, "errors": builtin_errors},
        "boi_wiki_contract": {"status": external_status, "ok": not external_errors, "errors": external_errors},
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
