# BoI Wiki Local Agent Rules

You are working inside a user's Local Private BoI workspace.

## Core Rule

Local Private content stays local unless the user explicitly asks to share and confirms the final preview.

## Navigation

- Start from `data/boi/index.md`.
- Then read the closest folder `index.md`.
- Do not scan every file first unless the user asks for broad cleanup/search.

## Write Targets

- Notes and meetings: `data/boi/private/me/notes/`
- SOP drafts: `data/boi/private/me/sop-drafts/`
- Action drafts: `data/boi/private/me/action-drafts/`
- Reports: `data/boi/private/me/reports/`
- Promotion drafts: `data/boi/private/me/promotion-drafts/`
- Archive: `data/boi/private/me/_archive/YYYY/MM/`

## Required Local Private Metadata

Every non-reserved Markdown BoI document must include YAML frontmatter:

```yaml
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-note
title: ...
description: ...
timestamp: ...
visibility: local-private
local_only: true
promotion_status: local_only
retention_class: working
retention_until: ""
archive_status: active
review_after: ...
contains_sensitive: unknown
source_refs: []
```

Reserved files `index.md` and `log.md` must not contain BoI concept frontmatter.

## Lifecycle Defaults

- Workflow or one-time execution record: `retention_class: ephemeral`
- Meeting note or work memo: `retention_class: working`
- Weekly report or evidence record: `retention_class: record`
- Source kept after promotion: `retention_class: promoted_source`

## Validation

The user will not run lint manually. You must validate before and after writing.

Level 0 self-check, always:

- Correct path under `data/boi/private/me/`
- Required metadata present
- `visibility: local-private`
- `local_only: true`
- lifecycle metadata present
- `index.md` updated
- `log.md` updated
- citations or source_refs present when source material exists
- no remote publish without explicit confirmation

Level 1, if possible:

- Run `check.sh` on Linux/WSL/macOS.
- Run `check.ps1` on Windows PowerShell.

Level 2, optional:

- If Python and a local linter are available, run it.

## Sharing and Promotion

If the user says "Public으로 공유해줘" or "팀 주간보고로 올려줘":

1. Create a local promotion draft.
2. Show the target visibility and preview/diff.
3. Remove or flag sensitive content.
4. Ask for explicit confirmation before any remote draft request.
5. Never publish the Local Private original directly.

## MCP

MCP is optional. If configured, use BoI Wiki MCP to search shared SOPs, Event Types, Actions, and workflow status. If it is not configured, continue with local files and ask the user for a Web link or pasted source when remote context is required.

