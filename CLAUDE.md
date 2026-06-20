# Claude Rules for BoI Wiki Local

This folder is a Local Private BoI workspace.

- Keep personal content local unless the user explicitly confirms sharing.
- Store notes in `data/boi/private/me/notes/`.
- Store SOP drafts in `data/boi/private/me/sop-drafts/`.
- Store diagrams in `data/boi/private/me/diagrams/`.
- Store event/workflow plans in `data/boi/private/me/event-drafts/` or `data/boi/private/me/workflow-simulations/`.
- Store context packs in `data/boi/private/me/context-packs/`.
- Store reports in `data/boi/private/me/reports/`.
- Use `visibility: local-private`, `local_only: true`, and lifecycle metadata.
- Update `data/boi/index.md`, the relevant folder `index.md`, and `data/boi/log.md`.
- Validate with the checklist in `AGENTS.md` before reporting completion.
- MCP is optional. If unavailable, work from local files and user-provided sources. The official MCP is the shared BoI Wiki MCP; do not require a local MCP server.
- Sharing creates a promotion draft and preflight first; after explicit user confirmation, submit only the sanitized promotion candidate for remote sync validation/publish. Remote validation, commit, publish, and HOTL status are handled by BoI Wiki; do not ask the user to run Git commands.
