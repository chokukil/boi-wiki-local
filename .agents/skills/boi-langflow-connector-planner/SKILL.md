---
name: boi-langflow-connector-planner
description: Use when planning a Langflow workflow that connects to BoI SOPs, Events, Actions, and generated BoI records.
---

# BoI Langflow Connector Planner

Use this skill when the user asks to connect Langflow with a BoI SOP workflow, design a Langflow stage analysis flow, or document required BoI components.

## Process

1. Read `AGENTS.md`, `data/boi/index.md`, and `data/boi/private/{employee_id}/langflow-plans/index.md`.
2. Identify whether Langflow is actually needed. Prefer API/manual/event actions when LLM reasoning is not needed.
3. If remote MCP is configured, search shared Langflow guides, action specs, SOPs, and workflow status.
4. Draft the Langflow plan under `data/boi/private/{employee_id}/langflow-plans/`.
5. Do not claim the flow is live unless runtime smoke evidence exists.

## Output Shape

Include:

- Flow purpose
- Inputs
- Expected BoI context loaded
- Required components
- Action Gateway integration
- Output BoI policy
- Validation checklist
- Citations

## Self-check

- Disconnected canvas nodes are treated as incomplete.
- Prompt output boundaries are explicit.
- Local Private metadata, `index.md`, and `log.md` are updated.
