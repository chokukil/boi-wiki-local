---
name: boi-action-author
description: Use when converting API, webhook, MCP, Langflow, manual, or event broker documentation into a BoI Action Spec draft.
---

# BoI Action Author

Use `boi-wiki-local` as the parent contract before this Skill. Every substantive Local Markdown output must pass OKF 0.1 + BoI Profile 0.1-local, structured provenance, and the Local Private promotion boundary; this Skill adds only the Action-specific content contract.

Use this skill when the user provides system API documentation, a webhook spec, MCP tool description, manual task, or Langflow endpoint and asks to make it usable by BoI Wiki.

## Process

1. Read `AGENTS.md`, `data/boi/index.md`, and `data/boi/private/{employee_id}/action-drafts/index.md`.
2. Classify the connector kind: `api`, `webhook`, `mcp`, `langflow`, `manual`, `event_broker`, or `boi_writer`.
3. If remote MCP is configured, resolve domain terms with `dictionary_resolve`, then search existing shared action specs first. Reuse before creating a new draft.
4. Create the action draft under `data/boi/private/{employee_id}/action-drafts/`.
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
- Dictionary Terms Used
- Citations

## Self-check

- No secrets or real tokens are stored.
- High-risk actions default to dry-run and require manual approval.
- The draft distinguishes user-facing example URLs from internal runtime URLs.
- Local Private metadata, `index.md`, and `log.md` are updated.
