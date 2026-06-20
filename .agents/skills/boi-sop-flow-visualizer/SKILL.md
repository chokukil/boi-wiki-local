---
name: boi-sop-flow-visualizer
description: Use when turning a BoI SOP or user-provided process into a Mermaid workflow diagram or diagram draft.
---

# BoI SOP Flow Visualizer

Use this skill when the user asks to see an SOP as a process flow, Mermaid diagram, SVG draft, stage map, or workflow picture.

## Inputs

- Local SOP draft under `data/boi/private/{employee_id}/sop-drafts/`
- User-provided SOP text, image description, or meeting note
- Optional remote BoI Wiki context from `boi-wiki-mcp` if already configured

## Process

1. Read `AGENTS.md`, `data/boi/index.md`, and the closest folder `index.md`.
2. Identify stages, entry event, emitted event, automated actions, manual actions, outputs, and failure modes.
3. Prefer Mermaid in Markdown. Use SVG/PNG only when the user asks for a fixed image.
4. Save diagram BoI drafts under `data/boi/private/{employee_id}/diagrams/`.
5. If remote MCP is available, use it only for shared SOP/Event/Action lookup. Do not submit or apply remote changes without explicit approval.

## Output Shape

Create a Local Private document with:

- `type: boi/local-diagram`
- `retention_class: working`
- `# Summary`
- `# Mermaid`
- `# Stage Notes`
- `# Citations`

## Self-check

- Mermaid syntax is fenced as `mermaid`.
- Every diagram node maps to a source stage, event, action, or manual handoff.
- Local Private metadata is present.
- `index.md` and `log.md` are updated.
