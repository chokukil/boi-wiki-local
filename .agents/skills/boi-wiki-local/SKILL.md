---
name: boi-wiki-local
description: Use when creating, updating, validating, archiving, or promoting Local Private BoI documents in this workspace.
---

# BoI Wiki Local Skill

Use this skill for Local Private BoI work.

## Before Work

1. Read `AGENTS.md`.
2. Read `data/boi/index.md`.
3. Read the closest folder `index.md` for the target area.
4. Use MCP only if it is already configured or the user asks for remote lookup.

## Common Requests

- "이 회의 내용을 BoI로 정리해줘" -> create a working note.
- "이 SOP 이미지를 BoI Wiki 형식으로 초안 만들어줘" -> create an SOP draft with citations.
- "팀 주간보고로 올려줘" -> create a promotion draft, then require confirmation before remote draft.
- "오래된 Private BoI 정리 후보 보여줘" -> list archive candidates, do not delete.

## Required Metadata

Use `visibility: local-private`, `local_only: true`, `promotion_status: local_only`, `archive_status: active`, and lifecycle metadata.

## Validation

Run Level 0 self-check always. Run `check.sh` or `check.ps1` if possible.

## After Work

Update:

- relevant folder `index.md`
- `data/boi/log.md`
- any citation/source links

Report:

- created/updated files
- validation result
- whether anything stayed local or needs user confirmation for sharing

