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
- Work request / Action drafts: `data/boi/private/{employee_id}/action-drafts/`
- Event drafts and workflow-definition drafts: `data/boi/private/{employee_id}/event-drafts/`
- Dictionary terms: `data/boi/private/{employee_id}/dictionary/`
- Diagrams: `data/boi/private/{employee_id}/diagrams/`
- Context packs: `data/boi/private/{employee_id}/context-packs/`
- Pre-execution checks and workflow simulations: `data/boi/private/{employee_id}/workflow-simulations/`
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
artifact_visibility: working
lifecycle_state: working
memory_candidate: false
cleanup_policy: keep
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
- User-adopted Second Brain memory: `artifact_visibility: memory`, `lifecycle_state: memory`, `cleanup_policy: keep`
- Generated report/sandbox/workflow artifact: `artifact_visibility: background`, `lifecycle_state: background`
- Duplicate or superseded generated artifact: `lifecycle_state: delete_candidate`
- Pinned or promotion draft/source: `lifecycle_state: protected`

## Cleanup

Do not let Local Private become a generated-log dump. When the user asks to clean up, first produce a preview that separates `memory`, `working`, `protected`, and generated cleanup candidates. Do not move or delete files without explicit confirmation.

Cleanup flow:

1. Preview candidates and reasons.
2. Move confirmed candidates to `.boi-trash/{cleanup_id}/` with a manifest.
3. Keep `original_path`, BoI ID, title, reason, moved time, `delete_after`, and restore instructions in the manifest.
4. Default quarantine duration is 7 days.
5. Restore from `.boi-trash` if the user asks during the retention window.
6. Hard delete only after quarantine expires and only for generated/background artifacts.

Never auto-delete `memory`, `working`, `protected`, pinned, promotion, or manually edited documents.

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
- cleanup metadata present for generated/background artifacts
- `index.md` updated
- `log.md` updated
- citations or source_refs present when source material exists
- dictionary terms include at least `term`, `definition`, aliases when known, examples when available, and links/source_refs when mapped to BoI concepts
- dictionary terms may include `term_kind` (`concept`, `acronym`, `test-method`, `variant-group`, `variant`). Detailed test/mode/variant terms need `broader` or `related_terms` parent links before Team/Public promotion.
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

MCP is optional. The official remote MCP is shared BoI Wiki MCP, not a local MCP product. If configured, use BoI Wiki MCP to search shared SOPs, Event Types, Actions, Dictionary, ontology search results, Agent answers, action inbox, and workflow status. Use WorkflowDefinition tools only as internal duplicate/connection checks; describe results to users as SOP, BoI Wiki, Event, or Action links. If MCP is not configured, continue with local files and ask the user for a Web link or pasted source when remote context is required.

When MCP is available:

- Use `dictionary_resolve` before interpreting acronyms, aliases, or shop-floor terms.
- Use `ontology_search` for broad domain questions across SOP/Event/Action/Dictionary/runtime evidence.
- Use `workflow_definitions_search` before creating a new workflow, API/MCP connector, event, action, or skill, but treat it as an internal WorkflowDefinition check.
- Use `workflow_definition_get` to inspect the business goal, work BoI outputs, evidence, and completion conditions of an internal shared WorkflowDefinition.
- Use `workflow_definition_deduplicate` before proposing a new shared workflow definition.
- Use `sop_registration_plan` and `sop_registration_preview` before remote draft creation when the user describes a new SOP, Event, or Action in natural language. Treat Event and Action as optional sections inside the SOP addition flow.
- Use `registration_plan` and `registration_verification_preview` only for compatibility or component-level draft work after the integrated SOP flow is not enough.
- Use `event_publish_plan` and `event_publish_preview` before asking to publish a business Event. Use `event_pattern_preview` when the user wants to turn repeated Event history into a new Event definition.
- Use `sop_run_history` when the user asks for SOP execution history; do not send them to a raw Event Stream first.
- Use `sop_registration_draft_create`, `registration_draft_create`, `sop_draft_create`, `event_type_draft_create`, or `action_draft_create` only after showing reusable candidates and getting explicit user confirmation for the remote draft request. For Action drafts, choose one connector kind first: API, MCP, Webhook, Manual, Event Broker, BoI Writer, or Langflow, then pass the matching `connector_config`.
- Use `boi_agent_chat` for page-aware questions and recommendations.
- Use `agent_inbox` when the user asks what they need to act on.
- Use `boi_search` only for document-only BoI list searches.
- Use `private_memory_cleanup_preview` before proposing remote Private cleanup.
- Use `private_memory_cleanup_run`, `private_memory_restore`, and `private_memory_mark_memory` only after explicit user confirmation.

Use remote write or execution tools only after explicit user approval:

- `source_apply`
- `doc_body_apply`
- `promotion_submit`
- `registration_draft_create`
- `registration_plan`
- `registration_verification_preview`
- `sop_registration_plan`
- `sop_registration_preview`
- `sop_registration_draft_create`
- `sop_registration_validate`
- `sop_registration_publish`
- `sop_draft_create`
- `event_type_draft_create`
- `action_draft_create`
- `registration_draft_publish`
- `event_pattern_promote_to_draft`
- `action_invoke`

## Dictionary Bulk Curation

For many candidate terms, do not edit importer code, API resolver logic, or route tests per term. Normal term decisions belong in source candidate data, curator override notes, local manifest rows, or promotion drafts.

Code changes are only appropriate when the dictionary schema, resolver matching policy, scope priority, context budget, or common quality gates change.

Record each candidate with one action:

| Action | Meaning |
|---|---|
| `keep` | Candidate is suitable as a canonical local/team/public term |
| `replace_with_canonical` | Candidate should become an alias or variant of a broader canonical term |
| `split_into_terms` | Candidate expression contains more than one independent term |
| `alias_to_existing` | Preserve only as an alias of an existing term |
| `exclude` | Noise, extractor error, duplicate, or not suitable for sharing |
| `needs_parent_curation` | Parent concept or relation is unclear |

Slash bundles, numeric bundles, condition bundles, mode/test variants, and vendor shorthand should not be promoted as standalone Team/Public canonical terms by default. First decide the parent concept, alias, and broader/narrower relation. If the parent is missing, keep the item local or mark it `needs_parent_curation`.

## Task Skills

If the agent supports skills, use the narrowest applicable skill:

- `boi-sop-flow-visualizer` for Mermaid/SVG SOP flow drafts
- `boi-event-workflow-planner` for event-to-work-BoI/workflow-definition plans
- `boi-action-author` for API/Webhook/MCP/Langflow/Manual work request specs connected to a workflow definition draft
- `boi-dictionary-author` for private/team/public terminology and ontology mapping drafts
- `boi-context-pack-builder` for agent-ready context packs
- `boi-workflow-simulator` for pre-execution workflow simulations
- `boi-langflow-connector-planner` for Langflow workflow plans
