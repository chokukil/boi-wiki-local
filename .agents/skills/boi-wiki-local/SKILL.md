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
   - Use `dictionary_resolve` for terms and acronyms.
   - Prefer `ontology_search` for broad shared Wiki lookup.
   - Prefer `boi_agent_chat` for page-aware BoI Agent questions.
   - Use `boi_inbox` for assigned BoI Inbox reports and manual/approval tasks. Treat `agent_inbox` as a deprecated compatibility alias only.
   - Use `boi_search` only when a document-only list is needed.

## Common Requests

- "이 회의 내용을 BoI로 정리해줘" -> create a working note.
- "이 SOP 이미지를 BoI Wiki 형식으로 초안 만들어줘" -> create an SOP draft with citations.
- "설비 이상 대응 SOP를 Mermaid 프로세스 플로우로 그려줘" -> use `boi-sop-flow-visualizer` and save a diagram draft.
- "이 이벤트가 발생하면 어떤 SOP와 Action이 이어지는지 알려줘" -> use `boi-event-workflow-planner` and save an event/workflow plan.
- "기존 API 문서를 BoI Action Spec 초안으로 만들어줘" -> use `boi-action-author`.
- "이 현장 용어를 dictionary에 추가해줘" -> use `boi-dictionary-author`.
- "원격 BoI Wiki를 검색해서 context pack을 만들어줘" -> use `boi-context-pack-builder`; remote lookup is optional and read-oriented.
- "팀 주간보고로 올려줘" -> create a promotion draft, run preflight, show preview, then require confirmation before remote sync validation/publish; remote validation, commit, publish, and HOTL status are handled by BoI Wiki.
- "오래된 Private BoI 정리 후보 보여줘" -> list archive candidates, do not delete.

## Remote MCP Policy

The official optional MCP is shared BoI Wiki MCP. Do not require a local MCP server. Use remote write or execution tools only after explicit user confirmation.

Do not send Local Private source text to remote Agent tools unless the user explicitly asks for remote validation/promotion and approves the preview. For local-only work, build a local context pack first.

## Required Metadata

Use `visibility: local-private`, `local_only: true`, `promotion_status: local_only`, `archive_status: active`, and lifecycle metadata.

## Validation

Run Level 0 self-check always. Run `check.sh` or `check.ps1` if possible. For Team/Public promotion, also check target visibility, source_refs, sensitive content, and preview before remote submit.

For dictionary terms, confirm at least `term`, `definition`, aliases/abbreviations when known, examples when available, source_refs, and any links to SOP/Event/Action/BoI concepts. If shared MCP is available, check existing terms with `dictionary_resolve` before creating a new term.

## After Work

Update:

- relevant folder `index.md`
- `data/boi/log.md`
- any citation/source links

Report:

- created/updated files
- validation result
- whether anything stayed local or needs user confirmation for sharing
- remote promotion publish/status result when a confirmed promotion was submitted
