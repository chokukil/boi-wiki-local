#!/usr/bin/env python3
"""Check navigation, screenshots, and release metadata in the Second Brain guide Wiki."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

GUIDE_RELEASE = "3.2.0"
MEDIA_SCHEMA = "boi-local-guide-media/v1"
MAX_MEDIA_BYTES = 600 * 1024
MAX_MEDIA_WIDTH = 1760
MIN_MEDIA_WIDTH = 800
EXPECTED_MEDIA_COUNT = 19
ALLOWED_CAPTURE_METHODS = {"windows-graphics-capture"}
LARGE_CASE_SCREEN_IDS = {f"screen-{number:02d}" for number in range(35, 41)}
MIN_LARGE_SCREEN_WIDTH = 1400
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
WIKILINK_RE = re.compile(r"\[\[[^\]]+\]\]")
PYTHON_COMMAND_RE = re.compile(r"(?im)^\s*(?:python(?:3)?\s+scripts[\\/]|py\s+-3\b)")
ADMIN_PYTHON_PAGES = {
    "71-contributing-via-pr.md",
    "80-admin-release-and-contract.md",
    "90-release-acceptance.md",
}
INTERNAL_USER_TERM_RE = re.compile(
    r"(?i)\b(?:hooks?|manifest|sidecar|NOOP|supersede)\b|plan hash|"
    r"(?:boi_setup|local_[a-z_]+|promotion_preflight)\.py"
)
ADMIN_TECHNICAL_PAGES = ADMIN_PYTHON_PAGES | {"81-agent-auto-check-admin.md"}
MANUAL_SCRIPT_RE = re.compile(r"(?i)(?<![a-z0-9_.-])[a-z0-9_.-]+\.(?:ps1|cmd)(?![a-z0-9_.-])")
MANUAL_SCRIPT_PAGES = ADMIN_TECHNICAL_PAGES | {
    "10-install-repository.md",
    "12-ai-assisted-setup.md",
    "70-update-and-rollback.md",
}
REQUIRED_PAGES = {
    "00-start-here.md",
    "01-meta-harness-map.md",
    "02-build-your-harness.md",
    "05-choose-your-path.md",
    "10-install-repository.md",
    "11-first-setup.md",
    "12-ai-assisted-setup.md",
    "13-conversation-memory.md",
    "14-folder-auto-curation.md",
    "15-memory-review-and-correction.md",
    "20-first-10-minutes.md",
    "21-okf-and-boi-profile.md",
    "22-local-vs-canonical-profile.md",
    "23-capture-distill-review.md",
    "24-daily-weekly-review.md",
    "25-use-case-playbook.md",
    "26-no-obsidian.md",
    "27-research-backed-second-brain.md",
    "28-safe-evidence-intake.md",
    "29-investigation-pattern.md",
    "30-obsidian-install-and-vault.md",
    "31-obsidian-core-settings.md",
    "32-obsidian-golden-journey.md",
    "33-hypothesis-evidence-review.md",
    "34-continuous-analysis-log.md",
    "35-recurrence-fingerprint.md",
    "36-outlook-to-case.md",
    "37-grounded-query.md",
    "40-community-plugin-safety.md",
    "41-quickadd.md",
    "42-omnisearch.md",
    "43-web-clipper.md",
    "50-mcp-and-promotion.md",
    "51-promotion-package.md",
    "52-mode-matrix.md",
    "53-organization-knowledge-loop.md",
    "60-troubleshooting.md",
    "70-update-and-rollback.md",
    "71-contributing-via-pr.md",
    "72-security-and-source-review.md",
    "80-admin-release-and-contract.md",
    "81-agent-auto-check-admin.md",
    "90-release-acceptance.md",
    "use-cases/01-meeting-and-weekly-report.md",
    "use-cases/02-research-and-onboarding.md",
    "use-cases/03-incident-quality-and-sop.md",
    "use-cases/04-api-event-and-workflow.md",
}
JOURNEY_FIELDS = {
    "guide_audience",
    "guide_duration_minutes",
    "guide_prerequisites",
    "guide_execution",
    "guide_success",
    "guide_failure_page",
    "guide_next_page",
    "guide_boundary",
}
GUIDE_BOUNDARIES = {
    "local-only",
    "repository-only",
    "optional-obsidian-local",
    "local-with-optional-mcp-read",
    "promotion-preview-only",
    "release-validation-only",
}


def metadata_value(text: str, field: str) -> str:
    match = re.search(rf'(?m)^{re.escape(field)}:\s*(?:"([^"]*)"|([^\r\n#]+))\s*$', text)
    if not match:
        return ""
    return (match.group(1) if match.group(1) is not None else match.group(2)).strip()


def webp_dimensions(data: bytes) -> tuple[int, int]:
    if len(data) < 30 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        raise ValueError("not a WebP file")
    chunk = data[12:16]
    if chunk == b"VP8X":
        return int.from_bytes(data[24:27], "little") + 1, int.from_bytes(data[27:30], "little") + 1
    if chunk == b"VP8L" and data[20] == 0x2F:
        bits = int.from_bytes(data[21:25], "little")
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    if chunk == b"VP8 " and data[23:26] == b"\x9d\x01\x2a":
        return struct.unpack_from("<H", data, 26)[0] & 0x3FFF, struct.unpack_from("<H", data, 28)[0] & 0x3FFF
    raise ValueError("unsupported WebP encoding")


def relative_page(guide: Path, path: Path) -> str:
    return path.relative_to(guide).as_posix()


def check_media(
    guide: Path,
    image_refs: dict[str, list[tuple[str, str]]],
    errors: list[dict[str, str]],
) -> tuple[int, list[dict[str, str]]]:
    manifest_path = guide / "_media" / "manifest.json"
    if not manifest_path.exists():
        errors.append({"path": "_media/manifest.json", "issue": "missing media manifest"})
        return 0, []
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append({"path": "_media/manifest.json", "issue": f"invalid media manifest: {exc}"})
        return 0, []
    if payload.get("schema") != MEDIA_SCHEMA:
        errors.append({"path": "_media/manifest.json", "issue": f"schema must be {MEDIA_SCHEMA}"})
    if payload.get("guide_release") != GUIDE_RELEASE:
        errors.append({"path": "_media/manifest.json", "issue": f"guide_release must be {GUIDE_RELEASE}"})
    items = payload.get("items")
    if not isinstance(items, list):
        errors.append({"path": "_media/manifest.json", "issue": "items must be a list"})
        return 0, []
    if len(items) != EXPECTED_MEDIA_COUNT:
        errors.append({"path": "_media/manifest.json", "issue": f"expected {EXPECTED_MEDIA_COUNT} screenshots, found {len(items)}"})
    seen_ids: set[str] = set()
    seen_files: set[str] = set()
    recapture_required: list[dict[str, str]] = []
    for item in items:
        if not isinstance(item, dict):
            errors.append({"path": "_media/manifest.json", "issue": "media item must be an object"})
            continue
        media_id = str(item.get("id", "")).strip()
        filename = str(item.get("file", "")).strip()
        item_path = f"_media/{filename}"
        if item.get("requires_recapture_for_release") is True:
            recapture_required.append(
                {
                    "id": media_id,
                    "file": filename,
                    "reason": str(item.get("recapture_reason", "")).strip(),
                }
            )
        if not media_id or media_id in seen_ids:
            errors.append({"path": "_media/manifest.json", "issue": f"missing or duplicate media id: {media_id}"})
        if not filename or filename in seen_files or Path(filename).name != filename:
            errors.append({"path": "_media/manifest.json", "issue": f"invalid or duplicate media file: {filename}"})
        seen_ids.add(media_id)
        seen_files.add(filename)
        media_path = guide / "_media" / filename
        if not media_path.exists():
            errors.append({"path": item_path, "issue": "manifest file is missing"})
            continue
        data = media_path.read_bytes()
        if len(data) > MAX_MEDIA_BYTES:
            errors.append({"path": item_path, "issue": f"file exceeds {MAX_MEDIA_BYTES} bytes"})
        if item.get("bytes") != len(data):
            errors.append({"path": item_path, "issue": "manifest byte count mismatch"})
        digest = hashlib.sha256(data).hexdigest()
        if item.get("sha256") != digest:
            errors.append({"path": item_path, "issue": "manifest SHA256 mismatch"})
        try:
            width, height = webp_dimensions(data)
            if width > MAX_MEDIA_WIDTH:
                errors.append({"path": item_path, "issue": f"image width exceeds {MAX_MEDIA_WIDTH}px"})
            if width < MIN_MEDIA_WIDTH:
                errors.append({"path": item_path, "issue": f"guide screen width must be at least {MIN_MEDIA_WIDTH}px"})
            if media_id in LARGE_CASE_SCREEN_IDS and width < MIN_LARGE_SCREEN_WIDTH:
                errors.append({"path": item_path, "issue": f"case journey screen width must be at least {MIN_LARGE_SCREEN_WIDTH}px"})
            if item.get("width") != width or item.get("height") != height:
                errors.append({"path": item_path, "issue": "manifest dimensions mismatch"})
        except ValueError as exc:
            errors.append({"path": item_path, "issue": str(exc)})
        if not str(item.get("alt", "")).strip():
            errors.append({"path": item_path, "issue": "manifest alt text is empty"})
        for required in ("app", "app_version", "captured_at"):
            if not str(item.get(required, "")).strip():
                errors.append({"path": item_path, "issue": f"manifest {required} is empty"})
        capture_method = str(item.get("capture_method", "")).strip()
        if capture_method not in ALLOWED_CAPTURE_METHODS:
            errors.append({"path": item_path, "issue": "manifest capture_method is missing or invalid"})
        if not str(item.get("capture_source", "")).strip():
            errors.append({"path": item_path, "issue": "manifest capture_source is empty"})
        if capture_method and capture_method != "windows-graphics-capture":
            errors.append({"path": item_path, "issue": "capture_method must be windows-graphics-capture"})
        if item.get("synthetic_data") is not True or item.get("contains_sensitive") is not False:
            errors.append({"path": item_path, "issue": "screenshots must use non-sensitive demonstration data"})
        if item.get("synthetic_ui") is not False:
            errors.append({"path": item_path, "issue": "screenshots must be actual application UI, not synthetic UI"})
        if item.get("readability_verified") is not True:
            errors.append({"path": item_path, "issue": "screenshot readability must be explicitly verified"})
        if item.get("local_private_included") is not False:
            errors.append({"path": item_path, "issue": "screenshot must not include Local Private material"})
        references = image_refs.get(item_path, [])
        if item.get("requires_recapture_for_release") is True and not references:
            continue
        if not references:
            errors.append({"path": item_path, "issue": "screenshot is not referenced by any Wiki page"})
            continue
        target_pages = item.get("target_pages")
        if not isinstance(target_pages, list) or sorted(target_pages) != sorted({page for page, _ in references}):
            errors.append({"path": item_path, "issue": "manifest target_pages do not match Markdown references"})
        for _, alt in references:
            if alt != item.get("alt"):
                errors.append({"path": item_path, "issue": "Markdown alt text does not match manifest"})
    for item_path in sorted(set(image_refs) - {f"_media/{name}" for name in seen_files}):
        errors.append({"path": item_path, "issue": "Markdown image is absent from media manifest"})
    return len(items), recapture_required


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--guide-root", default="templates/second-brain-guide")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    guide = (root / args.guide_root).resolve()
    errors: list[dict[str, str]] = []
    paths = sorted(guide.rglob("*.md")) if guide.exists() else []
    pages = {relative_page(guide, path) for path in paths}
    for missing in sorted(REQUIRED_PAGES - pages):
        errors.append({"path": args.guide_root, "issue": f"missing required page: {missing}"})
    image_refs: dict[str, list[tuple[str, str]]] = {}
    inbound: dict[str, int] = {page: 0 for page in pages}
    for path in paths:
        page = relative_page(guide, path)
        text = path.read_text(encoding="utf-8")
        if 'okf_version: "0.1"' not in text:
            errors.append({"path": page, "issue": "missing OKF 0.1 contract"})
        if 'boi_profile_version: "0.1-local"' not in text:
            errors.append({"path": page, "issue": "missing local BoI profile"})
        if WIKILINK_RE.search(text):
            errors.append({"path": page, "issue": "Obsidian wikilink is not allowed; use standard Markdown links"})
        if page not in ADMIN_PYTHON_PAGES and PYTHON_COMMAND_RE.search(text):
            errors.append({"path": page, "issue": "ordinary-user guide must use natural-language agent requests instead of Python commands"})
        parts = text.split("---", 2)
        body = parts[2] if len(parts) == 3 else text
        if page not in ADMIN_TECHNICAL_PAGES and INTERNAL_USER_TERM_RE.search(body):
            errors.append({"path": page, "issue": "ordinary-user guide exposes administrator implementation terminology"})
        if page not in MANUAL_SCRIPT_PAGES and MANUAL_SCRIPT_RE.search(body):
            errors.append({"path": page, "issue": "ordinary-user guide exposes a manual script outside the installation or update fallback"})
        if f'guide_release: "{GUIDE_RELEASE}"' not in text:
            errors.append({"path": page, "issue": f"guide release is not {GUIDE_RELEASE}"})
        metadata = {field: metadata_value(text, field) for field in JOURNEY_FIELDS}
        for field, value in metadata.items():
            if not value:
                errors.append({"path": page, "issue": f"missing journey metadata: {field}"})
        duration = metadata.get("guide_duration_minutes", "")
        if duration and (not duration.isdigit() or int(duration) <= 0):
            errors.append({"path": page, "issue": "guide_duration_minutes must be a positive integer"})
        boundary = metadata.get("guide_boundary", "")
        if boundary and boundary not in GUIDE_BOUNDARIES:
            errors.append({"path": page, "issue": f"unsupported guide boundary: {boundary}"})
        for field in ("guide_failure_page", "guide_next_page"):
            target = metadata.get(field, "")
            if target and not (path.parent / target).resolve().exists():
                errors.append({"path": page, "issue": f"{field} does not resolve: {target}"})
        resolved_links: set[Path] = set()
        for target in LINK_RE.findall(text):
            target = target.split("#", 1)[0].strip().strip("<>")
            if not target or target.startswith(("http://", "https://", "mailto:", "boi:")):
                continue
            resolved = (path.parent / target).resolve()
            resolved_links.add(resolved)
            if not resolved.exists():
                errors.append({"path": page, "issue": f"broken link: {target}"})
            else:
                try:
                    linked_page = resolved.relative_to(guide).as_posix()
                except ValueError:
                    linked_page = ""
                if linked_page in inbound:
                    inbound[linked_page] += 1
        next_target = metadata.get("guide_next_page", "")
        if next_target and (path.parent / next_target).resolve() not in resolved_links:
            errors.append({"path": page, "issue": f"guide_next_page is not a visible Markdown link: {next_target}"})
        for alt, target in IMAGE_RE.findall(text):
            clean_target = target.split("#", 1)[0].strip()
            if not alt.strip():
                errors.append({"path": page, "issue": f"empty image alt text: {clean_target}"})
            if clean_target.startswith(("http://", "https://")):
                errors.append({"path": page, "issue": f"external image is not allowed: {clean_target}"})
                continue
            resolved = (path.parent / clean_target).resolve()
            if not resolved.exists():
                errors.append({"path": page, "issue": f"broken image: {clean_target}"})
                continue
            if resolved not in resolved_links:
                errors.append({"path": page, "issue": f"missing full-size image link: {clean_target}"})
            try:
                item_path = resolved.relative_to(guide).as_posix()
            except ValueError:
                errors.append({"path": page, "issue": f"image is outside guide: {clean_target}"})
                continue
            image_refs.setdefault(item_path, []).append((page, alt.strip()))
    media_count, recapture_required = check_media(guide, image_refs, errors)
    for page, count in sorted(inbound.items()):
        if page != "00-start-here.md" and count == 0:
            errors.append({"path": page, "issue": "orphan guide page has no inbound Markdown link"})
    payload = {
        "ok": not errors,
        "guide_root": str(guide),
        "guide_release": GUIDE_RELEASE,
        "page_count": len(pages),
        "media_count": media_count,
        "release_screen_ready": not recapture_required,
        "recapture_required": recapture_required,
        "errors": errors,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
