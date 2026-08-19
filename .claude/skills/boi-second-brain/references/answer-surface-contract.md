# Answer Surface and Evidence Receipt

The natural Answer Surface and the detailed Evidence Receipt are two views of the same grounded plan. They preserve the same judgment, evidence, counterevidence, unknowns, freshness, and approval boundary.

## Natural Answer Surface

- The default overlay is `natural-expert`: professional, conversational Korean with depth and structure adapted to the question.
- Answer the question in the first paragraph in professional, conversational Korean.
- Direct answer, evidence, counterevidence, unknowns, next checks, confidence, and citations are analytical requirements, not a mandatory visible outline. Use headings only when they materially improve comprehension.
- Use one to five plain numbered citations in deterministic first-use order when citations materially help: normally one or two for a simple answer and three to five for a substantive judgment or comparison. Never pad the count. Never show internal L/S/D/C markers.
- Cite actual source evidence, not search results, indexes, Obsidian graphs, or AI synthesis pages.
- Preserve material counterevidence, conflict, application limits, and unknowns in the narrative.
- When a source has not finished review, state the limitation once in ordinary language. Do not expose `Current`, `Candidate`, `Manifest`, `승인 지식`, or `현재 채택` as default user-facing vocabulary.
- Hide Manifest, Query Pack, snapshot, revision, runtime names, absolute Local paths, employee identifiers, and full SHA256 values from the default answer.
- End with a plain `출처` block containing only sources actually cited. Reuse a document's first-use number and render a Local link as `[1] [문서 제목](notes/example.md)`. Use only the needed plain status: `내 자료 · 검토 전`, `내 자료 · 검토 중`, `원문 · 정리 전`, `이전 내용`, `저장한 답변`, or `조직 자료 · 새로 찾음`. Omit status when every source is reviewed.
- Do not add `자세히 보기`, a source drawer, a side panel, or source cards. The Markdown link is the detail path.

## Evidence Receipt

Show the Receipt only for a detailed-evidence request, Review, audit, or promotion. It retains relative Local paths, exact SHA256 values, source URLs and versions, inspected scope, Current identity, selected evidence, counterevidence, exclusions, and the citation display map.

## Local generation receipt

Every benchmarked answer must have a sibling `boi-local-answer-generation-receipt/v1` produced by the canonical agent path. The receipt binds the exact question hash, query-plan fingerprint, citation display-map fingerprint, selected evidence IDs, paths and hashes, each public original's evidence-ID + exact-byte + expected-origin binding, answer path, byte count and hash, `composer: natural-expert`, zero or one presentation-critic pass, and every material answer paragraph to a declared claim plus its citation identities. An uncertainty paragraph or an explicitly identified Local operating policy may have no citation; supported claims and counterevidence must bind at least one citation present in that paragraph. The receipt proves declared claim-evidence binding and staleness, not semantic truth. A missing, manually fabricated, stale, or mismatched receipt fails Answer Surface validation even when retrieval and original-file checks pass.

## One-pass critic

After grounding is complete, perform at most one meaning-preserving presentation repair when the answer does not lead with a direct answer, exposes internal details, overuses a fixed outline, fabricates or duplicates a citation, cites AI synthesis as source fact, or loses material counterevidence or uncertainty. A repair cannot add facts, repeat retrieval, change the evidence set, write a document, or alter an approval boundary.
