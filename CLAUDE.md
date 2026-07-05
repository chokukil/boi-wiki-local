# Claude Rules for BoI Wiki Local

This folder is a Local Private BoI workspace.

- Keep personal content local unless the user explicitly confirms sharing.
- Before creating personal BoI content, confirm a numeric 7-digit employee ID from `BOI_LOCAL_EMPLOYEE_ID` or the user.
- Store notes in `data/boi/private/{employee_id}/notes/`.
- Store SOP drafts in `data/boi/private/{employee_id}/sop-drafts/`.
- Store diagrams in `data/boi/private/{employee_id}/diagrams/`.
- Store event/workflow-definition plans in `data/boi/private/{employee_id}/event-drafts/` or `data/boi/private/{employee_id}/workflow-simulations/`.
- One-off or repeated personal work can start as a Local Private work BoI without forcing an SOP.
- Store dictionary terms in `data/boi/private/{employee_id}/dictionary/`.
- For bulk dictionary candidates, record curation decisions in local candidate/override/manifest or promotion drafts instead of changing code per term. Use `keep`, `replace_with_canonical`, `split_into_terms`, `alias_to_existing`, `exclude`, or `needs_parent_curation`.
- Store context packs in `data/boi/private/{employee_id}/context-packs/`.
- Store reports in `data/boi/private/{employee_id}/reports/`.
- Use `employee_id`, `local_owner_ref`, `visibility: local-private`, `local_only: true`, and lifecycle metadata.
- Update `data/boi/index.md`, the relevant folder `index.md`, and `data/boi/log.md`.
- Validate with the checklist in `AGENTS.md` before reporting completion.
- MCP is optional. If unavailable, work from local files and user-provided sources. The official MCP is the shared BoI Wiki MCP; do not require a local MCP server.
- If local helper scripts are available, use `scripts/local_capture.py`, `scripts/local_review.py`, and `scripts/promotion_preflight.py` for capture inbox, memory/cleanup review, and sharing preview.
- If MCP is available, prefer `dictionary_resolve` for terminology before interpreting acronyms, `ontology_search` for broad SOP/Event/Action/Dictionary/runtime lookup, `workflow_definitions_search` and `workflow_definition_deduplicate` as internal duplicate checks before proposing new shared connections, `boi_agent_chat` for page-aware questions, `boi_inbox` for assigned reports/tasks, `agent_memory_review` for Web Private memory candidates, `promotion_preview` before remote promotion submit, `source_wiki_plan` before repo wiki generation, `harness_acceptance` for release readiness, and `boi_search` only for document-only BoI search. Treat `agent_inbox` as a deprecated compatibility alias. Present user-facing links as BoI Wiki, SOP, Event, Action, or BoI Inbox destinations, not as WorkflowDefinition pages.
- Sharing creates a promotion draft and preflight first; after explicit user confirmation, submit only the sanitized promotion candidate for remote sync validation/publish. Remote validation, commit, publish, and HOTL status are handled by BoI Wiki; do not ask the user to run Git commands.
