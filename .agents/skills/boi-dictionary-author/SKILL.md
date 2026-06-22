---
name: boi-dictionary-author
description: Use when creating or updating BoI dictionary terms, aliases, acronyms, or ontology mappings in a Local Private workspace.
---

# BoI Dictionary Author

Use this skill when the user asks to define a term, acronym, shop-floor phrase, domain concept, synonym, or dictionary mapping.

## Process

1. Read `AGENTS.md`, `data/boi/index.md`, and `data/boi/private/{employee_id}/dictionary/index.md`.
2. Confirm the term, aliases/abbreviations, meaning, example usage, and linked BoI concept if known.
3. If remote MCP is configured, call `dictionary_resolve` first, then `ontology_search` only if broader SOP/Event/Action context is needed.
4. Create or update a Local Private dictionary term under `data/boi/private/{employee_id}/dictionary/`.
5. If the user wants Team/Public sharing, create a promotion draft and wait for explicit approval before remote submit.

## Required Shape

Use `type: boi/dictionary-term` and include:

- `term`
- `definition`
- `aliases` when known
- `domain`
- `examples`
- `links` to local or shared SOP/Event/Action/BoI concepts when available
- `source_refs`

Optional relation fields:

- `related_terms`
- `broader`
- `narrower`
- `same_as`
- `maps_to_event_type`
- `maps_to_action_key`
- `maps_to_sop`

## Self-check

- The definition is short enough for a human to review.
- The term does not override Team/Public meaning without saying it is a private interpretation.
- Links use Markdown concept links where possible.
- Dictionary mappings help search and interpretation only; they do not change permissions, approval policy, or action execution behavior.
- Local Private metadata, `index.md`, and `log.md` are updated.
