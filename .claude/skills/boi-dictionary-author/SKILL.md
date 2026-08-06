---
name: boi-dictionary-author
description: Use when creating or updating BoI dictionary terms, aliases, acronyms, or ontology mappings in a Local Private workspace.
---

# BoI Dictionary Author

Use `boi-wiki-local` as the parent contract before this Skill. Every substantive Local Markdown output must pass OKF 0.1 + BoI Profile 0.1-local, structured provenance, and the Local Private promotion boundary; this Skill adds only the Dictionary-specific content contract.

Use this skill when the user asks to define a term, acronym, shop-floor phrase, domain concept, synonym, or dictionary mapping.

## Process

1. Read `AGENTS.md`, `data/boi/index.md`, and `data/boi/private/{employee_id}/dictionary/index.md`.
2. Confirm the term, aliases/abbreviations, meaning, example usage, and linked BoI concept if known.
3. If remote MCP is configured, call `dictionary_resolve` first, then `ontology_search` only if broader SOP/Event/Action context is needed.
4. Create or update a Local Private dictionary term under `data/boi/private/{employee_id}/dictionary/`.
5. If the user wants Team/Public sharing, create a promotion draft and wait for explicit approval before remote submit.

## Bulk Curation

When the user provides many candidate terms, do not change importer code or resolver behavior for each term. Capture decisions in candidate data, override notes, manifest rows, or promotion drafts.

Use one action per candidate:

- `keep`
- `replace_with_canonical`
- `split_into_terms`
- `alias_to_existing`
- `exclude`
- `needs_parent_curation`

Slash bundles, numeric bundles, condition bundles, mode/test variants, and vendor shorthand are not promoted as standalone Team/Public canonical terms by default. First identify the broader parent concept, alias, and broader/narrower relation. If the parent is unclear, keep the item local or mark it `needs_parent_curation`.

## Required Shape

Use `type: boi/dictionary-term` and include:

- `term`
- `definition`
- `aliases` when known
- `term_kind` when useful: `concept`, `acronym`, `test-method`, `variant-group`, or `variant`
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

For `test-method`, `variant-group`, or `variant`, include `broader` or `related_terms` parent links before proposing Team/Public promotion.

## Self-check

- The definition is short enough for a human to review.
- The term does not override Team/Public meaning without saying it is a private interpretation.
- Links use Markdown concept links where possible.
- Dictionary mappings help search and interpretation only; they do not change permissions, approval policy, or action execution behavior.
- Local Private metadata, `index.md`, and `log.md` are updated.
