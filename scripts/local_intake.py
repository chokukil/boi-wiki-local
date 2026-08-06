#!/usr/bin/env python3
"""Register a manually saved local evidence file without changing its bytes."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

from boi_local_common import (
    append_index_link,
    append_log,
    atomic_write,
    local_frontmatter,
    now_kst,
    parse_frontmatter,
    private_root,
    relative_to_root,
    sha256_file,
    slugify,
    workspace_employee_id,
)
from local_case import refresh_case_hub_evidence

SUPPORTED_TYPES = {
    ".eml": "email",
    ".md": "web-clip",
    ".txt": "meeting-note",
    ".csv": "tabular-data",
    ".pdf": "document",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".webp": "image",
}
EVIDENCE_TYPES = {
    "email",
    "web-clip",
    "tabular-data",
    "document",
    "image",
    "meeting-note",
    "analysis-export",
    # Read-compatible aliases for 2.2 evidence sidecars. New intake never
    # selects these values automatically.
    "outlook-email",
    "analysis-report",
    "analysis-image",
    "wafer-map-image",
    "external-source-note",
}
DEPRECATED_EVIDENCE_TYPES = {
    "outlook-email": "email",
    "analysis-report": "document",
    "analysis-image": "image",
    "wafer-map-image": "image",
    "external-source-note": "web-clip",
}
CASE_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{2,63}")


def unique_target(directory: Path, name: str, digest: str) -> Path:
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-.") or "evidence.bin"
    return directory / f"{digest[:12]}-{safe_name}"


def existing_registration(base: Path, case_id: str, digest: str) -> Path | None:
    for path in sorted((base / "evidence").rglob("*.md")) if (base / "evidence").is_dir() else []:
        meta = parse_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        if meta.get("case_id") == case_id and meta.get("evidence_sha256") == digest:
            return path
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--employee-id", default="")
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--title", default="")
    parser.add_argument("--evidence-type", choices=sorted(EVIDENCE_TYPES), default="")
    parser.add_argument("--source-ref", default="manual-local-save")
    parser.add_argument("--sensitivity", choices=["internal", "restricted", "public"], default="internal")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    employee_id, _ = workspace_employee_id(root, args.employee_id)
    case_id = args.case_id.strip()
    if not CASE_RE.fullmatch(case_id):
        raise SystemExit("case ID must use 3-64 letters, digits, dot, underscore, or hyphen")
    source = Path(args.source).expanduser().resolve()
    if not source.is_file():
        raise SystemExit(f"source file is missing: {source}")
    detected_type = SUPPORTED_TYPES.get(source.suffix.lower(), "")
    if not detected_type:
        raise SystemExit(f"unsupported evidence extension: {source.suffix.lower() or '<none>'}")
    evidence_type = args.evidence_type or detected_type
    evidence_type_deprecated = evidence_type in DEPRECATED_EVIDENCE_TYPES
    digest = sha256_file(source)
    base = private_root(root, employee_id)
    hub = base / "cases" / case_id / "case-hub.md"
    if not hub.is_file():
        raise SystemExit(f"case hub is missing: {hub}")
    duplicate = existing_registration(base, case_id, digest)
    if duplicate:
        print(json.dumps({
            "ok": False,
            "duplicate": True,
            "case_id": case_id,
            "evidence_sha256": digest,
            "existing_path": relative_to_root(root, duplicate),
            "remote_submitted": False,
        }, ensure_ascii=False, indent=2))
        return 2

    raw_dir = base / "evidence" / case_id / "sources"
    raw_path = unique_target(raw_dir, source.name, digest)
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    if raw_path.exists() and sha256_file(raw_path) != digest:
        raise SystemExit(f"refusing to overwrite a different local evidence file: {raw_path}")
    if not raw_path.exists():
        shutil.copyfile(source, raw_path)
    if sha256_file(source) != digest or sha256_file(raw_path) != digest:
        raise SystemExit("source changed during intake or copied bytes do not match")

    evidence_id = f"E-{digest[:12].upper()}"
    title = args.title.strip() or source.stem.replace("_", " ").replace("-", " ")
    captured_at = now_kst()
    note_path = base / "evidence" / case_id / f"{evidence_id.lower()}-{slugify(title)}.md"
    raw_relative = relative_to_root(root, raw_path)
    contains_sensitive = {"restricted": "true", "public": "false", "internal": "unknown"}[args.sensitivity]
    frontmatter = local_frontmatter(
        employee_id=employee_id,
        doc_type="boi/local-evidence",
        title=title,
        description=f"{case_id}의 수동 등록 evidence. 원본 bytes는 SHA256으로 잠겼다.",
        boi_id=f"boi:private:{employee_id}:evidence:{case_id.lower()}:{digest[:12]}",
        tags=["second-brain", "evidence", case_id.lower(), evidence_type],
        source_refs=[{"type": "local-file", "ref": raw_relative, "sha256": digest, "note": args.source_ref}],
        generated_from=[{"type": "local-file", "ref": raw_relative, "sha256": digest}],
        timestamp=captured_at,
        contains_sensitive=contains_sensitive,
        extra={
            "case_id": case_id,
            "knowledge_role": "evidence-sidecar",
            "claim_status": "observed",
            "evidence_id": evidence_id,
            "evidence_type": evidence_type,
            "evidence_sha256": digest,
            "raw_path": raw_relative,
            "original_filename": source.name,
            "origin_ref": args.source_ref,
            "intake_method": "manual-local-file",
            "sensitivity": args.sensitivity,
        },
    )
    body = (
        f"\n# {title}\n\n"
        f"- Case: [{case_id} Case Hub](../../cases/{case_id}/case-hub.md)\n"
        f"- Evidence ID: `{evidence_id}`\n"
        f"- 유형: `{evidence_type}`\n"
        f"- 원본: `{raw_relative}`\n"
        f"- SHA256: `{digest}`\n\n"
        "원본 파일은 Local Private에만 보존되며 이 문서는 원본의 provenance sidecar입니다. "
        "내용 해석과 판단은 Case Hub 또는 파생 지식 문서에 작성합니다.\n"
    )
    atomic_write(note_path, frontmatter + body)
    append_index_link(base / "evidence" / "index.md", title, note_path.relative_to(base / "evidence").as_posix())
    hub_result = refresh_case_hub_evidence(root, employee_id, case_id)
    append_log(root, f"Local evidence `{evidence_id}`를 `{case_id}`에 수동 등록하고 SHA256을 고정함. 원격 전송 없음.")
    print(json.dumps({
        "ok": True,
        "duplicate": False,
        "case_id": case_id,
        "evidence_id": evidence_id,
        "evidence_type": evidence_type,
        "evidence_type_deprecated": evidence_type_deprecated,
        "recommended_evidence_type": DEPRECATED_EVIDENCE_TYPES.get(evidence_type, evidence_type),
        "evidence_sha256": digest,
        "source_unchanged": sha256_file(source) == digest,
        "path": relative_to_root(root, note_path),
        "raw_path": raw_relative,
        "case_hub": hub_result,
        "local_only": True,
        "remote_submitted": False,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
