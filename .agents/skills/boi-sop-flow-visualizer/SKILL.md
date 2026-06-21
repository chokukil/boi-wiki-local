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
3. Build a small graph model before writing Mermaid: stable node id, node kind, short label, source reference, and outgoing edge labels.
4. Produce two Mermaid diagrams by default:
   - `Overview`: 4-8 high-level nodes for the main process.
   - `Swimlane`: Event -> SOP Stage -> Action -> Manual Handoff -> Generated BoI lanes.
5. Split complex flows into stage detail diagrams when a diagram would exceed 10 nodes, has more than 14 edges, or has many crossing branches.
6. Prefer `flowchart TD`. Use `LR` only for short flows with compact labels.
7. Keep Korean labels short. Move long descriptions, systems, owners, and evidence into `Source Mapping` and `Stage Notes` tables instead of one large node.
8. Prefer Mermaid in Markdown. Use SVG/PNG only when the user asks for a fixed image.
9. Save diagram BoI drafts under `data/boi/private/{employee_id}/diagrams/`.
10. If remote MCP is available, use it only for shared SOP/Event/Action lookup. Do not submit or apply remote changes without explicit approval.

## Output Shape

Create a Local Private document with:

- `type: boi/local-diagram`
- `retention_class: working`
- `# Summary`
- `# Overview Mermaid`
- `# Swimlane Mermaid`
- `# Stage Detail Mermaid` when needed
- `# Source Mapping`
- `# Stage Notes`
- `# Diagram QA`
- `# Citations`

## Self-check

- Mermaid syntax is fenced as `mermaid`.
- Every diagram node maps to a source stage, event, action, manual handoff, or generated BoI.
- Node ids are ASCII stable ids such as `evt_detect`, `stage_analyze`, `act_trend`, `manual_review`.
- Decision nodes have explicit edge labels such as `yes`, `no`, `approval required`, or `skip`.
- Raw HTML line breaks such as `<br/>` are not required for readability. Split nodes or use source tables when labels become long.
- The output includes `Source Mapping` with node id, kind, label, and source reference.
- The output includes `Diagram QA` with syntax, source mapping, link, index/log, and complexity checks.
- Local Private metadata is present.
- `index.md` and `log.md` are updated.
