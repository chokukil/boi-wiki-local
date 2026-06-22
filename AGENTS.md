# BoI Wiki Local Agent Rules

You are working inside a user's Local Private BoI workspace.

## Core Rule

Local Private content stays local unless the user explicitly asks to share and confirms the final preview.

## Navigation

- Start from `data/boi/index.md`.
- Then read the closest folder `index.md`.
- Do not scan every file first unless the user asks for broad cleanup/search.

## Employee ID Rule

- Local Private work is keyed by a numeric 7-digit employee ID.
- Read `BOI_LOCAL_EMPLOYEE_ID` from `.env` or environment when available.
- If no valid 7-digit employee ID is available, ask the user for it before creating personal BoI content.
- The template scaffold is `data/boi/private/0000000/`. Do not use `0000000` for real personal work.
- Never create or use a non-numeric placeholder private folder.

## Write Targets

- Notes and meetings: `data/boi/private/{employee_id}/notes/`
- SOP drafts: `data/boi/private/{employee_id}/sop-drafts/`
- Action drafts: `data/boi/private/{employee_id}/action-drafts/`
- Event drafts: `data/boi/private/{employee_id}/event-drafts/`
- Diagrams: `data/boi/private/{employee_id}/diagrams/`
- Context packs: `data/boi/private/{employee_id}/context-packs/`
- Workflow simulations: `data/boi/private/{employee_id}/workflow-simulations/`
- Langflow plans: `data/boi/private/{employee_id}/langflow-plans/`
- Reports: `data/boi/private/{employee_id}/reports/`
- Promotion drafts: `data/boi/private/{employee_id}/promotion-drafts/`
- Archive: `data/boi/private/{employee_id}/_archive/YYYY/MM/`

## Required Local Private Metadata

Every non-reserved Markdown BoI document must include YAML frontmatter:

```yaml
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-note
title: ...
description: ...
timestamp: ...
employee_id: "1234567"
local_owner_ref: local-private:1234567
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

- Valid 7-digit `employee_id`
- Correct path under `data/boi/private/{employee_id}/`
- `employee_id` and `local_owner_ref` metadata match the path
- Required metadata present
- `visibility: local-private`
- `local_only: true`
- lifecycle metadata present
- `index.md` updated
- `log.md` updated
- citations or source_refs present when source material exists
- no remote publish without explicit confirmation
- for Team/Public promotion, local promotion draft, target visibility, source_refs, sensitive-content check, and preview are present

Level 1, if possible:

- Run `check.sh` on Linux/WSL/macOS.
- Run `check.ps1` on Windows PowerShell.

Level 2, optional:

- If Python and a local linter are available, run it.

## Sharing and Promotion

If the user says "Public으로 공유해줘" or "팀 주간보고로 올려줘":

1. Create a local promotion draft.
2. Run local preflight if possible.
3. Show target visibility, source_refs/citations, sensitive-content findings, and preview/diff.
4. Ask for explicit confirmation before any remote promotion submit.
5. Submit only the sanitized promotion candidate to remote sync validation/publish; do not ask the user to run Git, lint, or commit commands.
6. If remote validation and auto-commit pass, report the Team/Public publish status and HOTL watching status.
7. If remote validation fails, do not retry silently; revise the draft and ask for user confirmation again.
8. Never publish the Local Private original directly.

## MCP

MCP is optional. The official remote MCP is shared BoI Wiki MCP, not a local MCP product. If configured, use BoI Wiki MCP to search shared SOPs, Event Types, Actions, Dictionary, ontology search results, Agent answers, action inbox, and workflow status. If it is not configured, continue with local files and ask the user for a Web link or pasted source when remote context is required.

When MCP is available:

- Use `ontology_search` for broad domain questions across SOP/Event/Action/Dictionary/runtime evidence.
- Use `boi_agent_chat` for page-aware questions and recommendations.
- Use `dictionary_resolve` before interpreting acronyms, aliases, or shop-floor terms.
- Use `agent_inbox` when the user asks what they need to act on.
- Use `boi_search` only for document-only BoI list searches.

Use remote write or execution tools only after explicit user approval:

- `source_apply`
- `doc_body_apply`
- `promotion_submit`
- `action_invoke`

## Task Skills

If the agent supports skills, use the narrowest applicable skill:

- `boi-sop-flow-visualizer` for Mermaid/SVG SOP flow drafts
- `boi-event-workflow-planner` for event-to-SOP/action plans
- `boi-action-author` for API/Webhook/MCP/Langflow/Manual action specs
- `boi-context-pack-builder` for agent-ready context packs
- `boi-workflow-simulator` for dry-run workflow simulations
- `boi-langflow-connector-planner` for Langflow workflow plans
