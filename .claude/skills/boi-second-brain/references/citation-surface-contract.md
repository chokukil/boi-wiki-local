# Citation Surface contract

The Answer Surface, Citation Surface, and Evidence Receipt are three views of one in-memory Query Pack. They do not create a new knowledge schema or runtime.

## Identity and display

- One evidence identity always has one display number in an answer.
- Assign `[1]` through `[5]` in deterministic first-use order. Do not assign several numbers to the same identity.
- AI synthesis never receives a source citation. A synthesis may guide retrieval, but a public-research citation must resolve to hash-verified source bytes and a declared original identity that binds the evidence ID and exact SHA256 to its expected exact public URL or accepted DOI, arXiv, or ACL stable identifier. A merely public-looking URL is not authority. Carry the same binding through the Query Pack display map, generation receipt, and benchmark evaluation. Local policy or Local evidence uses a separately declared Local route and must never masquerade as a public original.
- Codex and Claude may phrase prose differently, but must keep the same selected evidence identities and display mapping for the same grounded input.

## Disclosure

The default answer shows readable titles and safe status labels. It hides internal evidence classes, absolute Local paths, private identifiers, revisions, snapshots, manifests, query-pack names, and full digests. Detailed evidence may show workspace-relative paths and shortened digests. Review, audit, and promotion may show full canonical identities and SHA256 values.

## Citation critic

Reject or repair once when a citation is fabricated, orphaned, unused, duplicated under another number, unsupported by the cited source, or bound to AI synthesis. Also reject when more than five material sources appear, an unapproved candidate is labeled Current, or material counterevidence or unknowns disappear. Presentation repair must not repeat retrieval or write Knowledge, Current, History, or Review files.

For benchmarked answers, record a claim binding for every material narrative paragraph. Each binding fixes the paragraph hash, declared claim or uncertainty, binding kind, visible citation markers, and resolved evidence identities. The declared marker list must exactly equal the paragraph's unique markers in visible order. A numbered citation that merely appears somewhere in the answer is not claim support; it must appear in and be bound to the paragraph whose claim it supports.
