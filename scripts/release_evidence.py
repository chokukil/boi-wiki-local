#!/usr/bin/env python3
"""Validate de-identified generic product acceptance and optional use-case review evidence."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import re
from pathlib import Path


COMMIT_RE = re.compile(r"^(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})$")
EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
EMPLOYEE_ID_RE = re.compile(r"(?<![A-Za-z0-9])\d{7}(?![A-Za-z0-9])")
PRIVATE_PATH_RE = re.compile(
    r"(?i)(?:[A-Z]:\\Users\\[^\\\s]+|\\\\wsl(?:\.localhost|\$)\\|data[\\/]boi[\\/]private[\\/]\d{7})"
)
FORBIDDEN_IDENTITY_KEYS = {
    "employee_id",
    "email",
    "local_path",
    "name",
    "raw_content",
    "raw_notes",
    "reviewer_name",
    "screen_recording",
    "tester_name",
    "user_id",
    "username",
    "vault_path",
}
TOP_LEVEL_KEYS = {
    "schema",
    "build_commit",
    "tested_at",
    "reviewer_role",
    "testers",
    "domain_review",
    "reviewer_confirmed",
}
TESTER_KEYS = {"journey", "tester_profile", "windows_native", "obsidian", "security", "ux_observations", "tester_confirmed"}
NESTED_KEYS = {
    "windows_native": {
        "approved_git_clone_succeeded",
        "install_from_wiki_succeeded",
        "first_capture_succeeded",
        "search_succeeded",
        "promotion_preview_succeeded",
        "duration_minutes",
        "install_duration_minutes",
        "first_knowledge_duration_minutes",
        "promotion_preview_duration_minutes",
    },
    "obsidian": {
        "support_claimed",
        "app_version",
        "vault_opened",
        "external_file_watcher_succeeded",
        "properties_succeeded",
        "backlinks_succeeded",
        "graph_succeeded",
    },
    "security": {
        "local_private_uploaded",
        "remote_mutations_before_approval",
        "usage_telemetry_observed",
    },
}
UX_OBSERVATION_KEYS = {"blocked_steps", "misclicked_steps", "helpful_capture_ids"}
UX_STEP_IDS = {
    "ai-setup", "preset", "folder-curation", "memory-correction",
    "install", "first-capture", "distill", "search", "promotion-preview",
    "vault-open", "properties", "backlinks", "graph", "bases", "canvas",
}
CAPTURE_ID_RE = re.compile(r"^screen-(?:0[1-9]|[12][0-9]|3[0-4])$")
DOMAIN_REVIEW_KEYS = {
    "reviewer_profile",
    "synthetic_case_reviewed",
    "workflow_plausibility_confirmed",
    "claims_marked_synthetic",
    "domain_persona_validated",
}


def identity_findings(value: object, path: str = "") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            item_path = f"{path}.{key}" if path else str(key)
            if str(key).lower() in FORBIDDEN_IDENTITY_KEYS:
                findings.append(f"forbidden identity field: {item_path}")
            findings.extend(identity_findings(item, item_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            findings.extend(identity_findings(item, f"{path}[{index}]"))
    elif isinstance(value, str):
        if EMAIL_RE.search(value):
            findings.append(f"email-like value is not allowed: {path}")
        if EMPLOYEE_ID_RE.search(value):
            findings.append(f"7-digit identifier is not allowed: {path}")
        if PRIVATE_PATH_RE.search(value):
            findings.append(f"private local path is not allowed: {path}")
    return findings


def validate(payload: dict, expected_build_commit: str = "") -> dict[str, object]:
    errors: list[str] = []
    if payload.get("schema") not in {"boi-local-release-acceptance/v3", "boi-local-release-acceptance/v4"}:
        errors.append("invalid evidence schema")
    unknown_top = sorted(set(payload) - TOP_LEVEL_KEYS)
    if unknown_top:
        errors.append(f"unknown top-level evidence fields: {', '.join(unknown_top)}")

    build_commit = str(payload.get("build_commit", "")).strip()
    if not COMMIT_RE.fullmatch(build_commit):
        errors.append("build_commit must be a full 40- or 64-character Git object ID")
    expected = expected_build_commit.strip().lower()
    if expected and build_commit.lower() != expected:
        errors.append("build_commit does not match the release-gate checkout HEAD")

    tested_at = str(payload.get("tested_at", "")).strip()
    try:
        tested_time = datetime.fromisoformat(tested_at)
        if tested_time.tzinfo is None or tested_time.utcoffset() is None:
            raise ValueError("timezone required")
    except ValueError:
        errors.append("tested_at must be an ISO 8601 timestamp with timezone")

    reviewer_role = str(payload.get("reviewer_role", "")).strip()
    if not reviewer_role or reviewer_role.startswith("replace-"):
        errors.append("missing completed field: reviewer_role")
    testers = payload.get("testers")
    if not isinstance(testers, list) or len(testers) != 2:
        errors.append("exactly two non-developer tester journeys are required")
        testers = []
    journeys: set[str] = set()
    obsidian_support_claimed = False
    time_targets: list[bool] = []
    for index, tester in enumerate(testers):
        prefix = f"testers[{index}]"
        if not isinstance(tester, dict):
            errors.append(f"{prefix} must be an object")
            continue
        unknown_tester = sorted(set(tester) - TESTER_KEYS)
        if unknown_tester:
            errors.append(f"unknown {prefix} fields: {', '.join(unknown_tester)}")
        journey_name = str(tester.get("journey", ""))
        if journey_name not in {"no-obsidian", "obsidian-core"}:
            errors.append(f"{prefix}.journey must be no-obsidian or obsidian-core")
        journeys.add(journey_name)
        if tester.get("tester_profile") != "non-developer":
            errors.append(f"{prefix}.tester_profile must be non-developer")
        journey = tester.get("windows_native") or {}
        unknown = sorted(set(journey) - NESTED_KEYS["windows_native"]) if isinstance(journey, dict) else []
        if unknown:
            errors.append(f"unknown {prefix}.windows_native fields: {', '.join(unknown)}")
        for field in (
            "approved_git_clone_succeeded",
            "install_from_wiki_succeeded",
            "first_capture_succeeded",
            "search_succeeded",
            "promotion_preview_succeeded",
        ):
            if not isinstance(journey, dict) or journey.get(field) is not True:
                errors.append(f"Windows journey not confirmed for {journey_name or prefix}: {field}")
        duration = journey.get("duration_minutes") if isinstance(journey, dict) else None
        if not isinstance(duration, (int, float)) or isinstance(duration, bool) or not 1 <= duration <= 240:
            errors.append(f"{prefix}.duration_minutes must be measured between 1 and 240")
        phase_targets = {
            "install_duration_minutes": 10,
            "first_knowledge_duration_minutes": 10,
            "promotion_preview_duration_minutes": 5,
        }
        for field, target in phase_targets.items():
            measured = journey.get(field) if isinstance(journey, dict) else None
            valid = isinstance(measured, (int, float)) and not isinstance(measured, bool) and 1 <= measured <= 240
            if not valid:
                errors.append(f"{prefix}.{field} must be measured between 1 and 240")
            else:
                time_targets.append(measured <= target)
        obsidian = tester.get("obsidian") or {}
        unknown = sorted(set(obsidian) - NESTED_KEYS["obsidian"]) if isinstance(obsidian, dict) else []
        if unknown:
            errors.append(f"unknown {prefix}.obsidian fields: {', '.join(unknown)}")
        if journey_name == "obsidian-core":
            obsidian_support_claimed = obsidian.get("support_claimed") is True
            if not obsidian_support_claimed:
                errors.append("obsidian-core tester must claim Obsidian support")
            if not str(obsidian.get("app_version", "")).strip():
                errors.append("Obsidian app_version is required for the obsidian-core tester")
            for field in ("vault_opened", "external_file_watcher_succeeded", "properties_succeeded", "backlinks_succeeded", "graph_succeeded"):
                if obsidian.get(field) is not True:
                    errors.append(f"Obsidian support not confirmed: {field}")
        elif isinstance(obsidian, dict) and obsidian.get("support_claimed") is not False:
            errors.append("no-obsidian tester must not claim Obsidian support")
        security = tester.get("security") or {}
        unknown = sorted(set(security) - NESTED_KEYS["security"]) if isinstance(security, dict) else []
        if unknown:
            errors.append(f"unknown {prefix}.security fields: {', '.join(unknown)}")
        for field in ("local_private_uploaded", "remote_mutations_before_approval", "usage_telemetry_observed"):
            if not isinstance(security, dict) or security.get(field) is not False:
                errors.append(f"security invariant not confirmed false for {journey_name or prefix}: {field}")
        observations = tester.get("ux_observations") or {}
        if not isinstance(observations, dict):
            errors.append(f"{prefix}.ux_observations must be an object")
            observations = {}
        unknown_observations = sorted(set(observations) - UX_OBSERVATION_KEYS)
        if unknown_observations:
            errors.append(f"unknown {prefix}.ux_observations fields: {', '.join(unknown_observations)}")
        for field in ("blocked_steps", "misclicked_steps"):
            values = observations.get(field)
            if not isinstance(values, list) or any(value not in UX_STEP_IDS for value in values):
                errors.append(f"{prefix}.ux_observations.{field} contains an invalid step ID")
        capture_ids = observations.get("helpful_capture_ids")
        if not isinstance(capture_ids, list) or any(not isinstance(value, str) or not CAPTURE_ID_RE.fullmatch(value) for value in capture_ids):
            errors.append(f"{prefix}.ux_observations.helpful_capture_ids contains an invalid capture ID")
        if tester.get("tester_confirmed") is not True:
            errors.append(f"tester confirmation is required for {journey_name or prefix}")
    if journeys != {"no-obsidian", "obsidian-core"}:
        errors.append("tester journeys must include one no-obsidian and one obsidian-core participant")

    domain_review = payload.get("domain_review") or {}
    if not isinstance(domain_review, dict):
        errors.append("domain_review must be an object")
        domain_review = {}
    unknown_domain = sorted(set(domain_review) - DOMAIN_REVIEW_KEYS)
    if unknown_domain:
        errors.append(f"unknown domain_review fields: {', '.join(unknown_domain)}")
    review_fields = (
        "synthetic_case_reviewed",
        "workflow_plausibility_confirmed",
        "claims_marked_synthetic",
        "domain_persona_validated",
    )
    domain_review_claimed = any(domain_review.get(field) is True for field in review_fields)
    domain_example_validated = bool(
        domain_review_claimed
        and str(domain_review.get("reviewer_profile", "")).strip()
        and not str(domain_review.get("reviewer_profile", "")).startswith("pending-")
        and all(domain_review.get(field) is True for field in review_fields)
    )
    if domain_review_claimed and not domain_example_validated:
        errors.append("a claimed use-case review requires a named reviewer profile and all review confirmations")
    if payload.get("reviewer_confirmed") is not True:
        errors.append("reviewer confirmation is required")
    identity_errors = identity_findings(payload)
    errors.extend(identity_errors)
    return {
        "ok": not errors,
        "schema": payload.get("schema"),
        "build_commit": build_commit,
        "build_commit_matches_expected": not expected or build_commit.lower() == expected,
        "tested_at": payload.get("tested_at"),
        "non_developer_journeys": not any(error.startswith("Windows journey") or "tester journey" in error for error in errors),
        "obsidian_support_claimed": obsidian_support_claimed,
        "time_targets_met": len(time_targets) == 6 and all(time_targets),
        "domain_persona_validated": domain_example_validated,
        "domain_example_validated": domain_example_validated,
        "errors": errors,
        "contains_personal_identity": bool(identity_errors),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--expected-build-commit", default="")
    args = parser.parse_args()
    try:
        payload = json.loads(Path(args.evidence).resolve().read_text(encoding="utf-8"))
        result = validate(payload, args.expected_build_commit)
    except (OSError, json.JSONDecodeError) as exc:
        result = {"ok": False, "errors": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
