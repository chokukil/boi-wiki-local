#!/usr/bin/env python3
"""Build or verify the deterministic 20-file Second Brain reference fixture.

This is a maintainer/CI fixture builder. It is not part of the employee runtime.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import zlib
from pathlib import Path


CASE_ID = "second-brain"
FIXTURE_SCHEMA = "boi-local-case-fixture-manifest/v2"
FIXED_AT = "2026-08-02T09:00:00+09:00"


PUBLIC_CLIP = """---
synthetic: true
source_kind: web-clip
source_url: https://example.invalid/knowledge-review
captured_at: 2026-08-02T09:05:00+09:00
---

# SYNTHETIC public knowledge review note

A durable note should separate the source statement, the author's interpretation,
counterevidence, and the next review date. A graph is a view over explicit links;
it is not evidence by itself.
"""


TEXT_FILES = {
    "01-decision-chat.txt": """SYNTHETIC CHAT EXTRACT — not a raw user transcript

Durable decision: the shared knowledge review happens every Friday at 15:00.
Reason: action owners can close the weekly loop before the reporting cut-off.
Transient note: order lunch after this discussion. This must not become memory.
""",
    "02-project-update.eml": """From: synthetic.owner@example.invalid
To: synthetic.team@example.invalid
Date: Sun, 02 Aug 2026 09:03:00 +0900
Message-ID: <second-brain-02@example.invalid>
Subject: [SYNTHETIC] Atlas glossary rename and review decision
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8

This is synthetic training data. Rename the internal term Blue Ledger to Atlas Ledger.
The Friday 15:00 knowledge review remains unchanged. The attached checklist is not included;
record it as missing evidence rather than inventing its contents.
""",
    "03-public-web-clip.md": PUBLIC_CLIP,
    "04-action-register.csv": """action_id,title,owner_role,status,due_date,source
SYN-A01,Confirm Atlas Ledger aliases,knowledge-steward,open,2026-08-07,meeting
SYN-A02,Recover missing email checklist,project-owner,blocked,2026-08-05,email
SYN-A03,Review stale onboarding FAQ,onboarding-owner,open,2026-08-14,weekly-review
SYN-A04,Publish approved read-only API note,api-owner,draft,2026-08-21,api-note
SYN-A05,Delete lunch reminder,none,not-knowledge,2026-08-02,chat
""",
    "07-meeting-note.md": """# SYNTHETIC meeting note

## Decisions

- Keep the durable knowledge review on Friday at 15:00.
- Use Atlas Ledger as the preferred term; preserve Blue Ledger as an alias.

## Evidence

- The project update email confirms both decisions.
- The referenced checklist is missing.

## Open items

- Validate the alias with the dictionary owner.
- Do not promote raw meeting notes.
""",
    "08-conflicting-review-day.md": """# SYNTHETIC conflicting note

Unverified claim: the knowledge review occurs every Thursday at 15:00.
Source: memory from an unknown author. No meeting link or decision record is present.
Status: conflict candidate; do not overwrite the reviewed Friday decision.
""",
    "09-public-web-clip-copy.md": PUBLIC_CLIP,
    "10-review-day-reconfirmation.txt": """SYNTHETIC FOLLOW-UP

The project owner explicitly reconfirmed Friday at 15:00 on 2026-08-02.
Treat this as new evidence for the existing review-schedule knowledge, not a new topic page.
""",
    "11-research-note.md": """# SYNTHETIC research comparison

Claim A: progressive summarization can improve later retrieval when source layers remain visible.
Claim B: folder taxonomies alone guarantee recall.

Evidence status: Claim A has a public source placeholder; Claim B is unsupported and must be
reported as a rejected or unverified claim. Do not fill either claim from model memory.
""",
    "12-sop-draft.md": """# SYNTHETIC draft SOP — promotion is prohibited

1. Find the reviewed schedule decision.
2. Check links, source hashes, conflicts, and review date.
3. Ask a human reviewer to resolve conflicts.
4. Produce a promotion preview only when the distilled document is eligible.

This is a draft. It is not approved for execution or Team publication.
""",
    "13-onboarding-faq.md": """# SYNTHETIC onboarding FAQ

Q: Is Obsidian required?
A: No. Markdown and an AI agent are sufficient.

Q: Does MCP upload Local Private files?
A: No. Read connectivity does not grant upload permission.

Q: Can agent-memory be promoted directly?
A: No. It must be distilled into an eligible BoI type and reviewed.

Q: Where are conflicts kept?
A: In a review-required Local state with both claims preserved.
""",
    "14-readonly-api-note.md": """# SYNTHETIC API note

Endpoint: GET /knowledge/search
Purpose: read-only lookup of ACL-visible canonical knowledge.
Mutation capability: none.
Required citation: canonical BoI ID, revision, and visibility.
Do not infer a write endpoint or upload Local paths in a query.
""",
    "15-incident-retrospective.md": """# SYNTHETIC incident retrospective

Observed: an outdated onboarding FAQ was used twice after its review date.
Contributing factor: the downstream FAQ did not link to the revised terminology decision.
Counterevidence: search returned the new term correctly when queried directly.
Unknown: whether the reminder was delivered.
Decision: repair the link and review date; do not claim search failure as the root cause.
""",
    "16-dictionary.md": """# SYNTHETIC dictionary candidate

Preferred term: Atlas Ledger
Aliases: Blue Ledger; AL; Project Atlas knowledge ledger
Definition: the synthetic reviewed knowledge collection used in this fixture.
Validation state: dictionary owner review pending.
""",
    "17-weekly-report.md": """# SYNTHETIC weekly report

Outcome: glossary rename decision captured with source evidence.
Evidence: project update email and meeting note.
Risk: missing checklist and unresolved Thursday/Friday conflict note.
Next: reviewer resolves the conflict and validates the alias before promotion.
""",
    "18-sensitive-review-note.md": """# SYNTHETIC review-required note

This source intentionally contains the token EMPLOYEE-PLACEHOLDER-0000000 and a local path
C:\\SyntheticUser\\Private\\draft.txt. They are synthetic, but the item must still be classified
as review-required and excluded from every remote projection.
""",
    "19-recurrence-note.md": """# SYNTHETIC recurrence note

Signal: an expired FAQ lacks a link to the latest reviewed decision.
Reuse condition: confirm the document is stale and the canonical term changed.
Exclusion: a search ranking issue without a stale link is a different case.
Human review is required before calling this a recurrence fingerprint.
""",
    "20-promotion-candidate.md": """# SYNTHETIC promotion candidate input

Candidate value: reusable weekly knowledge-review method and conflict-handling checklist.
Exclude: raw chat, raw email, local paths, Local BoI IDs, synthetic personal identifiers,
and the unresolved checklist claim.
Required preview: Team scope, reviewer, structured safe sources, exact candidate hash,
user_confirmed false, and remote_submit_allowed false.
""",
}


def _chunk(kind: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + kind
        + data
        + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    )


FONT_5X7 = {
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    ":": ("00000", "00100", "00100", "00000", "00100", "00100", "00000"),
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01110"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    " ": ("00000",) * 7,
}


def _draw_text(
    pixels: bytearray,
    width: int,
    x: int,
    y: int,
    text: str,
    scale: int,
    color: tuple[int, int, int],
) -> None:
    cursor = x
    for character in text:
        glyph = FONT_5X7[character]
        for glyph_y, row in enumerate(glyph):
            for glyph_x, value in enumerate(row):
                if value != "1":
                    continue
                for dy in range(scale):
                    for dx in range(scale):
                        px = cursor + glyph_x * scale + dx
                        py = y + glyph_y * scale + dy
                        offset = (py * width + px) * 3
                        pixels[offset : offset + 3] = bytes(color)
        cursor += 6 * scale


def whiteboard_png(width: int = 1200, height: int = 700) -> bytes:
    """Return a deterministic synthetic card-board PNG with embedded text metadata."""
    pixels = bytearray((246, 248, 251) * (width * height))
    cards = (
        (70, 130, 350, 480, (205, 231, 255)),
        (425, 130, 705, 480, (220, 245, 218)),
        (780, 130, 1060, 480, (255, 232, 201)),
    )
    for left, top, right, bottom, card_color in cards:
        for y in range(top, bottom + 1):
            for x in range(left, right + 1):
                color = (52, 64, 84) if x in {left, right} or y in {top, bottom} else card_color
                offset = (y * width + x) * 3
                pixels[offset : offset + 3] = bytes(color)
    _draw_text(pixels, width, 438, 45, "SYNTHETIC", 6, (30, 41, 59))
    _draw_text(pixels, width, 128, 225, "FRIDAY", 5, (30, 41, 59))
    _draw_text(pixels, width, 135, 300, "15:00", 7, (30, 41, 59))
    _draw_text(pixels, width, 482, 225, "ATLAS", 5, (30, 41, 59))
    _draw_text(pixels, width, 462, 300, "LEDGER", 5, (30, 41, 59))
    _draw_text(pixels, width, 824, 225, "MISSING", 4, (30, 41, 59))
    _draw_text(pixels, width, 802, 300, "CHECKLIST", 4, (30, 41, 59))
    text = (
        b"Title\x00SYNTHETIC Second Brain whiteboard; "
        b"cards=Friday 15:00 review|Atlas Ledger rename|missing checklist"
    )
    rows = []
    stride = width * 3
    for y in range(height):
        rows.append(b"\x00" + bytes(pixels[y * stride : (y + 1) * stride]))
    raw = b"".join(rows)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + _chunk(b"tEXt", text)
        + _chunk(b"IDAT", zlib.compress(raw, 9))
        + _chunk(b"IEND", b"")
    )


def operating_guide_pdf() -> bytes:
    pages = [
        [
            "SYNTHETIC SECOND BRAIN OPERATING GUIDE",
            "Page 1 - Review durable knowledge every Friday at 15:00.",
            "Preserve source bytes and separate evidence from interpretation.",
        ],
        [
            "SYNTHETIC SECOND BRAIN OPERATING GUIDE",
            "Page 2 - Conflicts require human review; do not overwrite history.",
            "Promotion requires a sanitized exact preview and separate approval.",
        ],
    ]
    objects: list[bytes] = []
    # 1 catalog, 2 pages, 3/4 page objects, 5 font, 6/7 streams.
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objects.append(b"<< /Type /Pages /Kids [3 0 R 4 0 R] /Count 2 >>")
    objects.append(
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 6 0 R >>"
    )
    objects.append(
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 7 0 R >>"
    )
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    for lines in pages:
        content = "BT /F1 11 Tf 48 748 Td " + " ".join(
            f"({line}) Tj 0 -24 Td" for line in lines
        ) + " ET"
        encoded = content.encode("ascii")
        objects.append(f"<< /Length {len(encoded)} >>\nstream\n".encode("ascii") + encoded + b"\nendstream")

    data = bytearray(b"%PDF-1.4\n%SYNTHETIC\n")
    offsets = [0]
    for index, body in enumerate(objects, 1):
        offsets.append(len(data))
        data.extend(f"{index} 0 obj\n".encode("ascii") + body + b"\nendobj\n")
    xref = len(data)
    data.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("ascii"))
    for offset in offsets[1:]:
        data.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    data.extend(
        f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode(
            "ascii"
        )
    )
    return bytes(data)


def fixture_files() -> dict[str, bytes]:
    files = {name: text.encode("utf-8") for name, text in TEXT_FILES.items()}
    files["05-operating-guide.pdf"] = operating_guide_pdf()
    files["06-whiteboard-decisions.png"] = whiteboard_png()
    return dict(sorted(files.items()))


def build_manifest(files: dict[str, bytes]) -> dict:
    items = []
    for name, data in files.items():
        items.append(
            {
                "path": f"sources/{name}",
                "sha256": hashlib.sha256(data).hexdigest(),
                "bytes": len(data),
                "synthetic": True,
            }
        )
    duplicate_hash = hashlib.sha256(files["03-public-web-clip.md"]).hexdigest()
    return {
        "schema": FIXTURE_SCHEMA,
        "case_id": CASE_ID,
        "fixture_id": "SYN-SB-001-v1",
        "fixed_at": FIXED_AT,
        "synthetic": True,
        "source_count": len(items),
        "required_media": ["email", "web-clip", "tabular-data", "pdf", "image", "meeting-note"],
        "intentional_duplicate_groups": [
            {
                "sha256": duplicate_hash,
                "paths": [
                    "sources/03-public-web-clip.md",
                    "sources/09-public-web-clip-copy.md",
                ],
            }
        ],
        "files": items,
    }


def _local_page(
    *,
    boi_id: str,
    title: str,
    knowledge_role: str,
    claim_status: str,
    source_path: str,
    source_sha256: str,
    body: str,
    page_type: str = "boi/local-knowledge",
    review_after: str = "2026-08-09",
) -> bytes:
    text = f'''---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: {page_type}
title: "{title}"
description: "SYN-SB-001-v1 evaluation seed"
tags: [Synthetic, SecondBrainEval]
boi_id: {boi_id}
visibility: local-private
classification: internal
owner: "0000000"
employee_id: "0000000"
local_owner_ref: local-private:0000000
local_only: true
promotion_status: local_only
artifact_visibility: memory
lifecycle_state: memory
archive_status: active
review_after: {review_after}
contains_sensitive: false
knowledge_role: {knowledge_role}
claim_status: {claim_status}
source_refs:
  - type: synthetic-fixture
    ref: {source_path}
    sha256: {source_sha256}
generated_from:
  - type: synthetic-fixture
    ref: {source_path}
    sha256: {source_sha256}
---

# {title}

{body}
'''
    return text.encode("utf-8")


def evaluation_seeds(source_files: dict[str, bytes]) -> dict[str, dict[str, bytes]]:
    def digest(name: str) -> str:
        return hashlib.sha256(source_files[name]).hexdigest()

    schedule = _local_page(
        boi_id="boi:private:0000000:eval:review-schedule",
        title="Synthetic knowledge review schedule",
        knowledge_role="reviewed-knowledge",
        claim_status="direct",
        source_path="sources/01-decision-chat.txt",
        source_sha256=digest("01-decision-chat.txt"),
        body="Reviewed decision: knowledge review occurs every Friday at 15:00.",
    )
    term = _local_page(
        boi_id="boi:private:0000000:eval:atlas-ledger",
        title="Atlas Ledger terminology",
        knowledge_role="reviewed-knowledge",
        claim_status="direct",
        source_path="sources/02-project-update.eml",
        source_sha256=digest("02-project-update.eml"),
        body="Preferred term candidate: Atlas Ledger. Blue Ledger remains an alias until dictionary owner review.",
    )
    faq = _local_page(
        boi_id="boi:private:0000000:eval:onboarding-faq",
        title="Second Brain onboarding FAQ",
        knowledge_role="compiled-knowledge",
        claim_status="direct",
        source_path="sources/13-onboarding-faq.md",
        source_sha256=digest("13-onboarding-faq.md"),
        body="This FAQ is intentionally overdue for review and lacks a link to the terminology decision.",
        review_after="2026-07-31",
    )
    memory = _local_page(
        boi_id="boi:private:0000000:eval:agent-memory",
        title="Agent memory for weekly review",
        knowledge_role="agent-memory",
        claim_status="inferred",
        source_path="sources/10-review-day-reconfirmation.txt",
        source_sha256=digest("10-review-day-reconfirmation.txt"),
        body="Provisional memory: Friday 15:00 was reconfirmed. This page is directly promotion-blocked.",
        page_type="boi/local-knowledge-note",
    )

    seed_state = {
        "schema": "boi-local-eval-seed/v1",
        "fixture_id": "SYN-SB-001-v1",
        "employee_id": "0000000",
        "remote_enabled": False,
        "synthetic": True,
    }
    empty_state = {**seed_state, "seed_id": "s00-empty", "description": "No Local Profile exists"}
    reviewed_state = {**seed_state, "seed_id": "s10-reviewed", "description": "Reviewed schedule and terminology exist"}
    curated_state = {**seed_state, "seed_id": "s20-curated", "description": "Reviewed knowledge, stale FAQ, and agent-memory exist"}

    ordered_names = list(source_files)
    processed_names = ordered_names[:10]
    interrupted_state = {
        **seed_state,
        "seed_id": "s30-interrupted",
        "description": "First ten sources were processed; ten remain",
        "processed": [
            {"path": f"sources/{name}", "sha256": digest(name)} for name in processed_names
        ],
        "pending": [
            {"path": f"sources/{name}", "sha256": digest(name)} for name in ordered_names[10:]
        ],
    }
    source_rows = [
        {"path": f"sources/{name}", "sha256": digest(name), "bytes": len(source_files[name])}
        for name in ordered_names
    ]
    source_manifest_hash = hashlib.sha256(
        json.dumps(source_rows, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    batch_names = (
        ordered_names[:4],
        ordered_names[4:8],
        ordered_names[8:10],
        ordered_names[10:14],
        ordered_names[14:18],
        ordered_names[18:20],
    )
    source_plan = {
        "schema": "boi-local-source-folder-plan/v1",
        "fixture_id": "SYN-SB-001-v1",
        "employee_id": "0000000",
        "synthetic": True,
        "scope": "local-private",
        "preserve_originals": True,
        "remote_auto_upload": False,
        "approved_at": "2026-08-02T09:30:00+09:00",
        "user_confirmed": True,
        "source_manifest_hash": source_manifest_hash,
        "source_manifest": source_rows,
        "ordered_batches": [
            {
                "batch_id": f"batch-{index:02d}",
                "source_refs": [f"sources/{name}" for name in names],
            }
            for index, names in enumerate(batch_names, start=1)
        ],
    }
    source_plan_bytes = (json.dumps(source_plan, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    source_progress = {
        "schema": "boi-local-source-folder-progress/v1",
        "approved_plan_hash": hashlib.sha256(source_plan_bytes).hexdigest(),
        "source_manifest_hash": source_manifest_hash,
        "completed_sha256": sorted({digest(name) for name in processed_names}),
        "already_reflected_sha256": [],
        "remaining_source_refs": [f"sources/{name}" for name in ordered_names[10:]],
        "next_batch": {
            "batch_id": "batch-04",
            "source_refs": [f"sources/{name}" for name in ordered_names[10:14]],
        },
        "status": "in_progress",
    }
    source_progress_bytes = (json.dumps(source_progress, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    return {
        "s00-empty": {"seed.json": (json.dumps(empty_state, ensure_ascii=False, indent=2) + "\n").encode("utf-8")},
        "s10-reviewed": {
            "seed.json": (json.dumps(reviewed_state, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
            "notes/knowledge/review-schedule.md": schedule,
            "notes/knowledge/atlas-ledger.md": term,
        },
        "s20-curated": {
            "seed.json": (json.dumps(curated_state, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
            "notes/knowledge/review-schedule.md": schedule,
            "notes/knowledge/atlas-ledger.md": term,
            "notes/knowledge/onboarding-faq.md": faq,
            "notes/knowledge/agent-memory.md": memory,
        },
        "s30-interrupted": {
            "seed.json": (json.dumps(interrupted_state, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
            "notes/knowledge/review-schedule.md": schedule,
            ".boi-local/source-folder-plan.json": source_plan_bytes,
            ".boi-local/source-folder-progress.json": source_progress_bytes,
        },
    }


def build_seed_catalog(seeds: dict[str, dict[str, bytes]]) -> tuple[dict, dict[str, bytes]]:
    seed_manifests: dict[str, bytes] = {}
    entries = []
    prompts = {
        "s00-empty": ["p01"],
        "s10-reviewed": ["p02", "p03", "p04"],
        "s20-curated": ["p05", "p06", "p08"],
        "s30-interrupted": ["p07"],
    }
    for seed_id, files in seeds.items():
        manifest = {
            "schema": "boi-local-eval-seed-manifest/v1",
            "seed_id": seed_id,
            "synthetic": True,
            "files": [
                {
                    "path": path,
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "bytes": len(data),
                }
                for path, data in sorted(files.items())
            ],
        }
        manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        seed_manifests[seed_id] = manifest_bytes
        entries.append(
            {
                "seed_id": seed_id,
                "manifest": f"{seed_id}/manifest.json",
                "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
                "used_by_prompts": prompts[seed_id],
            }
        )
    catalog = {
        "schema": "boi-local-eval-seed-catalog/v1",
        "case_id": CASE_ID,
        "fixture_id": "SYN-SB-001-v1",
        "seeds": entries,
    }
    return catalog, seed_manifests


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    fixture_root = root / "cases" / "flagship" / "second-brain" / "fixtures"
    source_root = fixture_root / "sources"
    files = fixture_files()
    manifest = build_manifest(files)
    expected_manifest = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    seeds_root = root / "cases" / "flagship" / "second-brain" / "evals" / "seeds"
    seeds = evaluation_seeds(files)
    seed_catalog, seed_manifests = build_seed_catalog(seeds)
    expected_seed_catalog = json.dumps(seed_catalog, ensure_ascii=False, indent=2) + "\n"

    errors: list[str] = []
    if args.check:
        for name, data in files.items():
            path = source_root / name
            if not path.is_file() or path.read_bytes() != data:
                errors.append(f"fixture mismatch: sources/{name}")
        manifest_path = fixture_root / "manifest.json"
        if not manifest_path.is_file() or manifest_path.read_text(encoding="utf-8") != expected_manifest:
            errors.append("fixture mismatch: manifest.json")
        catalog_path = seeds_root / "seed-catalog.json"
        if not catalog_path.is_file() or catalog_path.read_text(encoding="utf-8") != expected_seed_catalog:
            errors.append("fixture mismatch: evals/seeds/seed-catalog.json")
        for seed_id, seed_files in seeds.items():
            for relative, data in seed_files.items():
                path = seeds_root / seed_id / relative
                if not path.is_file() or path.read_bytes() != data:
                    errors.append(f"fixture mismatch: evals/seeds/{seed_id}/{relative}")
            manifest_path = seeds_root / seed_id / "manifest.json"
            if not manifest_path.is_file() or manifest_path.read_bytes() != seed_manifests[seed_id]:
                errors.append(f"fixture mismatch: evals/seeds/{seed_id}/manifest.json")
    else:
        source_root.mkdir(parents=True, exist_ok=True)
        for name, data in files.items():
            (source_root / name).write_bytes(data)
        (fixture_root / "manifest.json").write_text(expected_manifest, encoding="utf-8")
        seeds_root.mkdir(parents=True, exist_ok=True)
        (seeds_root / "seed-catalog.json").write_text(expected_seed_catalog, encoding="utf-8")
        for seed_id, seed_files in seeds.items():
            seed_root = seeds_root / seed_id
            for relative, data in seed_files.items():
                destination = seed_root / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
            (seed_root / "manifest.json").write_bytes(seed_manifests[seed_id])

    payload = {
        "schema": "boi-local-fixture-build-result/v1",
        "ok": not errors,
        "case_id": CASE_ID,
        "source_count": len(files),
        "seed_count": len(seeds),
        "fixture_root": str(fixture_root),
        "errors": errors,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
