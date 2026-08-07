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
4. Use MCP only if it is already configured, the user asks to install or connect it, or the user asks for remote lookup.
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

When the user says `MCP 설치해줘`, `BoI Wiki MCP 연결해줘`, or an equivalent natural-language request, do not conclude that the MCP does not exist merely because no tool is currently configured. First run `scripts/select-repository-source.ps1 -Mode Preview` through the agent's hidden shell and read the selected BoI Wiki provenance. If the internal host is reachable but authentication or repository access fails, stop without GitHub fallback and explain that Bitbucket login and BOI repository Read access are required. Repository selection never selects or guesses an MCP endpoint.

Next read `templates/mcp/boi-wiki-mcp-connection.json`, resolve the endpoint only from an explicit user value, `BOI_WIKI_MCP_EXTERNAL_URL`, or an approved deployment descriptor, and run `scripts/connect-boi-wiki-mcp.ps1 -Mode Preview` for Codex or Claude Code. Show the selected client, sanitized endpoint, authentication mode, configuration target, restart requirement, and exact plan hash. Apply only after approval of that preview with the same hash. Never put token values in a command, diff, receipt, or log. After the client restarts, verify MCP `initialize` and `tools/list`; report a missing endpoint, login, or required tool as a precise pending gate. Installing a connection does not upload Local Private content and is not promotion approval.

Do not publish Local Private source text to BoI Wiki or MCP write tools unless the user explicitly asks for remote validation/promotion and approves the preview. A user-selected AI runtime may process selected content under the approved provider and company policy; disclose that separately from BoI remote activity. For local-only work, build a local context pack first.

## Required Local Profile contract

Every substantive Local Markdown page produced by this Skill or a composing Skill must use the exact shared contract. This includes knowledge, guides, SOPs, dictionary entries, actions, workflows, captures, evidence, hypotheses, analysis logs, and context packs. Do not abbreviate field names or substitute a Case manifest for the document Profile.

At minimum require:

- `okf_version: "0.1"` and `boi_profile_version: "0.1-local"`;
- `type`, `title`, `description`, `timestamp`, and a Local `boi_id`;
- `visibility: local-private`, `classification: internal`, `owner`, `employee_id`, and `local_owner_ref`;
- `local_only: true`, `promotion_status: local_only`, and `archive_status: active`;
- `retention_class`, `artifact_visibility`, `lifecycle_state`, `memory_candidate`, `cleanup_policy`, `review_after`, and `contains_sensitive`;
- structured `source_refs` items with `type`, `ref`, and `note` or `sha256` as appropriate;
- structured `generated_from` items with an exact SHA256 whenever the page is derived from a file or another Local document.

A navigation-only `index.md` may remain plain Markdown only when it contains links and labels. If it owns a conclusion, decision, risk, status, or summary, it is a Profile page and must satisfy the same contract. A source-registration wrapper that postpones readable-material distillation is not a successful knowledge result.

## Promotion boundary

Local capture, evidence, hypothesis, analysis case, analysis log, source record, and agent memory are directly non-promotable. Distill supported content into an allowed knowledge, context pack, SOP, guide, dictionary, action, or workflow candidate first.

A configured personal Harness card under `notes/harnesses/`, or carrying the `ConfiguredHarness` tag, is also directly non-promotable. Its `boi/local-guide` type does not override that restriction. Distill a separate generic guide without personal execution configuration, or package a reviewed Community Case, before promotion preview.

Canonical preview must:

- preserve `okf_version: "0.1"` and convert only `boi_profile_version` to `"0.1"`;
- use only `team` or `public`, require reviewer and structured remote-safe `source_refs`, and require `team_id` for Team;
- remove Local paths, employee/Profile identifiers, Local `boi_id`, raw source, sensitive content, and Local-only operating wording such as `Local Private`, `local_only`, or `local_owner_ref`;
- leave final owner, ACL, BoI ID, and revision to the authenticated target BoI Wiki principal and scope;
- show blockers, target scope, exact candidate hash, and that remote submit is still disabled.

Any candidate body, source set, reviewer, or scope change invalidates approval. MCP read access never implies upload, and no remote submit may occur before the user approves the exact preview.

## Validation

Run Level 0 self-check always with the agent's native file and hashing tools: literal required fields, allowed values, structured provenance, links, source integrity, Local Private status, and direct-promotion blocks. For an ordinary Windows employee flow, use `check.ps1 -NativeOnly` when repository-level validation is useful; do not require Python or the full Admin/CI suite. Run the full repository checks only for maintainer, release, or contract-oracle work. Never ask an ordinary user to type these commands. For Team/Public promotion, also check target visibility, reviewer, team scope when applicable, remote-safe sources, sensitive content, sanitized projection, and exact preview before remote submit.

For dictionary terms, confirm at least `term`, `definition`, aliases/abbreviations when known, examples when available, source_refs, and any links to SOP/Event/Action/BoI concepts. If shared MCP is available, check existing terms with `dictionary_resolve` before creating a new term.

## After Work

When substantive Local documents were created, updated, archived, or a promotion preview was materialized, update only the affected navigation and audit surfaces:

- relevant folder `index.md`
- `data/boi/log.md`
- any citation/source links

For read-only search, explanation, validation preview, a blocked attempt before mutation, or an `already reflected`/no-change result, do not edit an index or log merely to record that the agent ran.

Report:

- created/updated files
- validation result
- whether anything stayed local or needs user confirmation for sharing
- remote promotion publish/status result when a confirmed promotion was submitted
