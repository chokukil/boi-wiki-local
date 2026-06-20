---
name: boi-action-author
description: Use when converting API, webhook, MCP, Langflow, manual, or event broker documentation into a BoI Action Spec draft.
---

# BoI Action Author

Use this skill when the user provides system API documentation, a webhook spec, MCP tool description, manual task, or Langflow endpoint and asks to make it usable by BoI Wiki.

## Process

1. Read `AGENTS.md`, `data/boi/index.md`, and `data/boi/private/me/action-drafts/index.md`.
2. Classify the connector kind: `api`, `webhook`, `mcp`, `langflow`, `manual`, `event_broker`, or `boi_writer`.
3. If remote MCP is configured, search existing shared action specs first. Reuse before creating a new draft.
4. Create the action draft under `data/boi/private/me/action-drafts/`.
5. If the user asks to share, create a sanitized promotion draft and wait for explicit approval before remote submit.

## Required Draft Sections

- Summary
- Connector Kind
- Execution Mode
- Request Schema
- Response Schema
- Example Request
- Example Result
- Security Notes
- Approval Policy
- Catalog Patch Draft
- Citations

## Self-check

- No secrets or real tokens are stored.
- High-risk actions default to dry-run and require manual approval.
- The draft distinguishes user-facing example URLs from internal runtime URLs.
- Local Private metadata, `index.md`, and `log.md` are updated.
