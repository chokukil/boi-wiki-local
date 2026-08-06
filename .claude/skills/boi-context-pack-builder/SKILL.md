---
name: boi-context-pack-builder
description: Use when collecting BoI, SOP, Event Type, Action, trace, and source links into an agent-ready context pack.
---

# BoI Context Pack Builder

Use `boi-wiki-local` as the parent contract before this Skill. Every substantive Local Markdown output must pass OKF 0.1 + BoI Profile 0.1-local, structured provenance, and the Local Private promotion boundary; this Skill adds only the Context Pack-specific content contract.

Use this skill when the user wants an agent to understand a work item, incident, meeting, SOP, or workflow without rereading everything manually.

## Process

1. Read `AGENTS.md`, `data/boi/index.md`, and `data/boi/private/{employee_id}/context-packs/index.md`.
2. Identify the task boundary: decision, SOP, incident, report, action authoring, or workflow simulation.
3. Gather local docs first. If remote MCP is configured, resolve terminology with `dictionary_resolve`, then search shared BoI Wiki for relevant SOPs, Event Types, Actions, workflow status, dictionary terms, and graph links.
4. Save the context pack under `data/boi/private/{employee_id}/context-packs/`.
5. Keep copied remote excerpts concise and cite source links.

## Output Shape

Include:

- Purpose
- Relevant BoI docs
- SOP and stage references
- Event Types
- Actions and manual handoffs
- Dictionary terms and aliases used
- Open gaps
- Suggested next agent actions
- Citations

## Self-check

- The pack contains links, not uncontrolled full dumps.
- Sensitive local context stays local unless user approves sharing.
- Local Private metadata, `index.md`, and `log.md` are updated.
