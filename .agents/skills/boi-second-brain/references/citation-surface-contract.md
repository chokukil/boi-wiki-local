# Citation Surface contract

The Answer Surface, Citation Surface, and Evidence Receipt are three views of one in-memory Query Pack. They do not create a new knowledge schema or runtime.

## Identity and display

- One evidence identity always has one display number in an answer.
- Assign `[1]` through `[5]` in deterministic first-use order. Do not assign several numbers to the same identity.
- AI synthesis never receives a source citation. A synthesis may guide retrieval, but a public-research citation must resolve to hash-verified source bytes and a declared original identity that binds the evidence ID and exact SHA256 to its expected exact public URL or accepted DOI, arXiv, or ACL stable identifier. A merely public-looking URL is not authority. Carry the same binding through the Query Pack display map, generation receipt, and benchmark evaluation. Local policy or Local evidence uses a separately declared Local route and must never masquerade as a public original.
- A Local display entry may expose `open_target` only after the Markdown file is reread and its SHA256 is verified. The target must be a directly openable, profile-relative `.md` path inside the active Local Private Profile. Reject absolute paths, `..` traversal, files outside the Profile, missing files, non-Markdown extensions, Obsidian-only wikilinks, and invented heading anchors.
- The display entry's optional `source_markdown` is the complete source-list line, for example `[1] [문서 제목](notes/example.md) — 내 자료 · 검토 전`. Claims may bind to verified `discovery_evidence`, never to a search-only `discovery_results` row.
- Codex and Claude may phrase prose differently, but must keep the same selected evidence identities and display mapping for the same grounded input.

## Disclosure

The default answer shows readable titles and safe status labels. It hides internal evidence classes, absolute Local paths, private identifiers, revisions, snapshots, manifests, query-pack names, and full digests. Detailed evidence may show workspace-relative paths and shortened digests. Review, audit, and promotion may show full canonical identities and SHA256 values.

## Citation critic

Reject or repair once when a citation is fabricated, orphaned, unused, duplicated under another number, unsupported by the cited source, bound to AI synthesis, or rendered with a manipulated number, dead link, or unsafe target. Also reject when more than five material sources appear, an unreviewed source is presented as reviewed, or material counterevidence or unknowns disappear. Presentation repair must not repeat retrieval or write Knowledge, Current, History, or Review files.

For benchmarked answers, record a claim binding for every material narrative paragraph. Each binding fixes the paragraph hash, declared claim or uncertainty, binding kind, visible citation markers, and resolved evidence identities. The declared marker list must exactly equal the paragraph's unique markers in visible order. A numbered citation that merely appears somewhere in the answer is not claim support; it must appear in and be bound to the paragraph whose claim it supports.
