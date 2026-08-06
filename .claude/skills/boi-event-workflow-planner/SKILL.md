---
name: boi-event-workflow-planner
description: Use when planning what should happen when a business event occurs in BoI Wiki style.
---

# BoI Event Workflow Planner

Use `boi-wiki-local` as the parent contract before this Skill. Every substantive Local Markdown output must pass OKF 0.1 + BoI Profile 0.1-local, structured provenance, and the Local Private promotion boundary; this Skill adds only the Event and Workflow planning contract.

Use this skill when the user asks "when this event happens, what should happen?", asks to filter/create event types, or wants an AI Native Workflow plan.

## Process

1. Read `AGENTS.md`, `data/boi/index.md`, and local event/workflow draft folders.
2. Determine whether the request is about an existing event, a new event candidate, or a one-time manual workflow.
3. If remote MCP is configured, resolve event/action/domain terms with `dictionary_resolve`, then search shared Event Types, SOPs, and Actions before drafting. If not, ask for a Web link, copied source, or proceed local-only.
4. Draft the event-to-workflow plan under `data/boi/private/{employee_id}/event-drafts/` or `data/boi/private/{employee_id}/workflow-simulations/`.
5. Do not publish or invoke remote workflow/action tools without explicit user approval.

## Output Shape

Include:

- event name and event type candidate
- trigger condition
- related SOP/stage
- expected automated actions
- manual handoffs and approval needs
- expected generated BoI records
- gaps and next questions
- dictionary terms that changed interpretation

## Self-check

- New event names use a versioned event type pattern, e.g. `domain.signal.requested.v1`.
- Manual approval is called out for high-risk actions.
- Local Private metadata, `index.md`, and `log.md` are updated.
