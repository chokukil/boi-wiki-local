---
name: boi-workflow-simulator
description: Use when dry-running an event payload through an SOP workflow without invoking live actions.
---

# BoI Workflow Simulator

Use `boi-wiki-local` as the parent contract before this Skill. Every substantive Local Markdown output must pass OKF 0.1 + BoI Profile 0.1-local, structured provenance, and the Local Private promotion boundary; this Skill adds only the safe simulation contract.

Use this skill when the user asks what would happen for a given event payload, wants a safe dry-run, or wants to understand generated BoI and manual handoff outcomes.

## Process

1. Read `AGENTS.md`, `data/boi/index.md`, and `data/boi/private/{employee_id}/workflow-simulations/index.md`.
2. Identify event type, payload, actor, trace candidate, SOP, stages, and action candidates.
3. If remote MCP is configured, use `dictionary_resolve` plus shared SOP/Event/Action documents to improve the simulation. Do not call `workflow_start`, `action_invoke`, or remote apply tools unless the user explicitly asks and approves.
4. For each stage/action, identify prerequisite evidence from SOP text, action specs, and prior local BoI records.
5. If prerequisite evidence is missing but the action spec defines a simulation/result contract, create a clearly labeled `SIMULATED evidence packet` instead of silently failing. Mark provenance as `simulated_prerequisite` and state that no real internal system was called.
6. Save the dry-run under `data/boi/private/{employee_id}/workflow-simulations/`.

## Output Shape

Include:

- Input Event
- Expected SOP Stages
- Expected Actions
- Manual Handoffs
- Generated BoI Records
- Risk and Approval Notes
- Mermaid Trace
- Evidence Packets and Provenance
- Dictionary Terms Used
- Citations

## Self-check

- Clearly label the document as a simulation.
- Do not imply that actions were actually invoked.
- Do not mark missing real system data as pass unless the document contains a contract-based SIMULATED evidence packet.
- Evidence packets list `evidence_key`, source action/spec, required fields, provenance, and limitations.
- Local Private metadata, `index.md`, and `log.md` are updated.
