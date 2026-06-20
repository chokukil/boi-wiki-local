# Claude Rules for BoI Wiki Local

This folder is a Local Private BoI workspace.

- Keep personal content local unless the user explicitly confirms sharing.
- Before creating personal BoI content, confirm a numeric 7-digit employee ID from `BOI_LOCAL_EMPLOYEE_ID` or the user.
- Store notes in `data/boi/private/{employee_id}/notes/`.
- Store SOP drafts in `data/boi/private/{employee_id}/sop-drafts/`.
- Store diagrams in `data/boi/private/{employee_id}/diagrams/`.
- Store event/workflow plans in `data/boi/private/{employee_id}/event-drafts/` or `data/boi/private/{employee_id}/workflow-simulations/`.
- Store context packs in `data/boi/private/{employee_id}/context-packs/`.
- Store reports in `data/boi/private/{employee_id}/reports/`.
- Use `employee_id`, `local_owner_ref`, `visibility: local-private`, `local_only: true`, and lifecycle metadata.
- Update `data/boi/index.md`, the relevant folder `index.md`, and `data/boi/log.md`.
- Validate with the checklist in `AGENTS.md` before reporting completion.
- MCP is optional. If unavailable, work from local files and user-provided sources. The official MCP is the shared BoI Wiki MCP; do not require a local MCP server.
- Sharing creates a promotion draft and preflight first; after explicit user confirmation, submit only the sanitized promotion candidate for remote sync validation/publish. Remote validation, commit, publish, and HOTL status are handled by BoI Wiki; do not ask the user to run Git commands.
