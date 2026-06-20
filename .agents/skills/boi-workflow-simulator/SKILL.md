---
name: boi-workflow-simulator
description: Use when dry-running an event payload through an SOP workflow without invoking live actions.
---

# BoI Workflow Simulator

Use this skill when the user asks what would happen for a given event payload, wants a safe dry-run, or wants to understand generated BoI and manual handoff outcomes.

## Process

1. Read `AGENTS.md`, `data/boi/index.md`, and `data/boi/private/me/workflow-simulations/index.md`.
2. Identify event type, payload, actor, trace candidate, SOP, stages, and action candidates.
3. If remote MCP is configured, use shared SOP/Event/Action documents to improve the simulation. Do not call `workflow_start`, `action_invoke`, or remote apply tools unless the user explicitly asks and approves.
4. Save the dry-run under `data/boi/private/me/workflow-simulations/`.

## Output Shape

Include:

- Input Event
- Expected SOP Stages
- Expected Actions
- Manual Handoffs
- Generated BoI Records
- Risk and Approval Notes
- Mermaid Trace
- Citations

## Self-check

- Clearly label the document as a simulation.
- Do not imply that actions were actually invoked.
- Local Private metadata, `index.md`, and `log.md` are updated.
