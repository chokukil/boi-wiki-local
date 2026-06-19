# Claude Rules for BoI Wiki Local

This folder is a Local Private BoI workspace.

- Keep personal content local unless the user explicitly confirms sharing.
- Store notes in `data/boi/private/me/notes/`.
- Store SOP drafts in `data/boi/private/me/sop-drafts/`.
- Store reports in `data/boi/private/me/reports/`.
- Use `visibility: local-private`, `local_only: true`, and lifecycle metadata.
- Update `data/boi/index.md`, the relevant folder `index.md`, and `data/boi/log.md`.
- Validate with the checklist in `AGENTS.md` before reporting completion.
- MCP is optional. If unavailable, work from local files and user-provided sources.
- Sharing creates a promotion draft first; do not send Local Private originals remotely without explicit user confirmation.

