# Answer Surface and Evidence Receipt

The natural Answer Surface and the detailed Evidence Receipt are two views of the same grounded plan. They preserve the same judgment, evidence, counterevidence, unknowns, freshness, and approval boundary.

## Natural Answer Surface

- The default overlay is `natural-expert`: professional, conversational Korean with depth and structure adapted to the question.
- Answer the question in the first paragraph in professional, conversational Korean.
- Direct answer, evidence, counterevidence, unknowns, next checks, confidence, and citations are analytical requirements, not a mandatory visible outline. Use headings only when they materially improve comprehension.
- Use three to five plain numbered citations in deterministic first-use order when citations materially help. Never show internal L/S/D/C markers.
- Cite actual source evidence, not search results, indexes, Obsidian graphs, or AI synthesis pages.
- Preserve material counterevidence, conflict, application limits, and unknowns in the narrative.
- State whether the answer is Local auto-managed synthesis, approved Current, or an unapproved change candidate only when that status changes how it may be used.
- Hide Manifest, Query Pack, snapshot, revision, runtime names, absolute Local paths, employee identifiers, and full SHA256 values from the default answer.
- Show a short source list with readable titles and human-readable status such as `공개 논문 원문 · 확인 완료`, `내 승인 지식`, or `조직 Wiki · 현재 채택`.

## Evidence Receipt

Show the Receipt only for a detailed-evidence request, Review, audit, or promotion. It retains relative Local paths, exact SHA256 values, source URLs and versions, inspected scope, Current identity, selected evidence, counterevidence, exclusions, and the citation display map.

## Local generation receipt

Every benchmarked answer must have a sibling `boi-local-answer-generation-receipt/v1` produced by the canonical agent path. The receipt binds the exact question hash, query-plan fingerprint, citation display-map fingerprint, selected evidence IDs, paths and hashes, each public original's evidence-ID + exact-byte + expected-origin binding, answer path, byte count and hash, `composer: natural-expert`, zero or one presentation-critic pass, and every material answer paragraph to a declared claim plus its citation identities. An uncertainty paragraph or an explicitly identified Local operating policy may have no citation; supported claims and counterevidence must bind at least one citation present in that paragraph. The receipt proves declared claim-evidence binding and staleness, not semantic truth. A missing, manually fabricated, stale, or mismatched receipt fails Answer Surface validation even when retrieval and original-file checks pass.

## One-pass critic

After grounding is complete, perform at most one meaning-preserving presentation repair when the answer does not lead with a direct answer, exposes internal details, overuses a fixed outline, fabricates or duplicates a citation, cites AI synthesis as source fact, or loses material counterevidence or uncertainty. A repair cannot add facts, repeat retrieval, change the evidence set, write a document, or alter an approval boundary.
