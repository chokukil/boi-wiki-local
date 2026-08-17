# BoI AI Second Brain Broadcast and Quality Integration Plan

**Goal:** Preserve the existing 2055186 Local corpus and auto-curate boundaries while repairing the canonical query and quality path, producing a Markdown-first public AI research broadcast package, and publishing only public-safe repository changes through a reviewed squash merge.

## Global Constraints

- Preserve the active 2055186 corpus: 33 public source artifacts, 33 observed source-knowledge pages, eight inferred topic pages, and zero active Review candidates unless a material judgment change is actually found.
- `auto-curate` makes conflict-free Local knowledge immediately usable. Human approval is reserved for a material question-scoped Current change, conflict or low confidence, sensitive content, and Team/Public promotion.
- Do not approve Current, ingest a new T1 source, promote Local knowledge, perform BoI Remote writes, or modify `.obsidian`.
- Do not build a new Wiki, GraphRAG engine, ontology database, resident runtime, background watcher, or required Obsidian/Python dependency.
- Python and PowerShell remain maintainer and CI validators. The ordinary path is an AI agent reading, searching, hashing, and composing Markdown.
- Ordinary research search excludes report, ledger, audit, presentation-support, guide, and broadcast documents. Those are available only through explicit support scope.
- User-facing answers cite three to five actual original sources with readable `[1]` to `[5]` markers. AI synthesis may guide retrieval but is never cited as original evidence.
- The default Answer Surface is `natural-expert`, conclusion-first, question-shaped, and free of mandatory seven-section output. At most one presentation-only critic pass is allowed; it cannot change evidence or write knowledge.
- General-audience broadcast surfaces say “원문 보존”, “출처 확인”, “현재 기준 답변”, and “중요한 변경 후보”; they do not foreground SHA256, Manifest, Query Pack, revision, or runtime terms.
- Obsidian Canvas, Bases, and Local Graph are optional views of the same Markdown and are never presented as GraphRAG or canonical provenance.
- Public Git history must exclude `data/boi/private/2055186`, the source PPT, internal footage, `.obsidian`, Current/T1/promotion results, temporary files, environment data, and unrelated existing work.

## Task 1: Governed knowledge-growth and auto-curate contract

**Commit:** `feat(second-brain): add governed knowledge-growth golden journeys`

- Finish the existing public Golden Journey artifacts without changing their semantic conclusions or claiming production readiness.
- Make the shared Second Brain contract distinguish source integrity, Local auto-managed knowledge, question-scoped Current, Review candidates, and Team/Public promotion.
- Ensure ordinary `observed` and conflict-free `inferred` knowledge remains searchable without document-by-document approval.
- Preserve no-change behavior, duplicate-hash behavior, material-change Review gating, and promotion preview boundaries.
- Keep unrelated Global Insight and private Case work unstaged unless it is required by this task and passes the public-safe review.
- Add or retain behavior tests that fail when 33 auto-curated sources produce document-level Review items, when inferred means pending, or when a candidate overwrites Current.

## Task 2: Grounded retrieval and real Answer Surface quality

**Commit:** `fix(second-brain): enforce grounded retrieval and natural answer quality`

- Replace keyword-vote intent routing with deterministic question-purpose and facet planning for synthesis, comparison, evaluation, decision, and verification questions.
- Separate ordinary research retrieval from explicit support retrieval and prevent reports, ledgers, audits, guides, and presentation documents from leaking into ordinary answers.
- Require quality benchmark v2 to evaluate actual generated Markdown, not embedded pre-authored answer objects.
- Bind a generated answer to the question, query-plan fingerprint, selected citation display map, evidence identities, and answer bytes through a local generation receipt. A manually placed answer without this receipt must fail Answer Surface validation.
- Report retrieval, evidence binding, and Answer Surface as independent axes. A composite 1.0 is not sufficient when any axis lacks real generation or claim-support evidence.
- Add claim-to-citation binding checks for material answer paragraphs so numbered citations are not merely present and hash-valid but are connected to declared supported claims. Preserve explicit counterevidence and uncertainty.
- Restore canonical `natural-expert` and one-pass presentation critic behavior in both Codex and Claude Skill mirrors, with byte parity and Runtime Manifest parity.
- Synchronize the verified canonical query/evaluator files into the installed 2055186 checkout through the existing package/update boundary; do not edit its 33 sources, 41 Local knowledge pages, Current, Review, Inbox, or Obsidian state.
- Regenerate the representative answer and five auxiliary answers through the canonical agent contract, create their receipts, and run the three-axis evaluator against those six actual answers.

## Task 3: Markdown-first broadcast package and publication

**Commit:** `docs(second-brain): restore auto-curate and Markdown-first knowledge flows`

- Add four canonical Mermaid/fallback flows: Local auto-curate, the actual public AI research corpus, Personal Local to Team/Public, and SOP/Event AI Native Workflow.
- Keep the existing 17-node, 20-edge private Canvas and Base as optional views. Move any material explanation out of Canvas-only text into profiled Markdown. Do not modify `.obsidian`.
- Update the broadcast hub, five-minute cue sheet, expected Q&A, and broadcaster reply to describe an actual working AI research Second Brain rather than a staged demo.
- Correct the public corpus wording to 33 public research artifacts: 25 paper PDFs, two public text sources, and six GitHub snapshots. Do not call all 33 papers.
- Explain that the 41 Local knowledge pages are auto-managed and immediately usable, while only material judgment changes and sharing transitions need human review.
- Present the manufacturing/SOP/Event material as a separately supplied, de-identified organizational direction. Do not mix internal content into the public research Vault.
- Create and retain two original Korean PNG infographics: Personal Local to Team/Public knowledge, and SOP/Event AI Native Workflow knowledge loop. Preserve original bytes and dimensions; do not modify the reference PPT or re-export from it.
- Validate Markdown fallback readability, Mermaid syntax, 1080p legibility, image text, public-safe content, and the five-minute rehearsal order.
- Run focused tests, Harness verification, `check.ps1 -NativeOnly`, `wiki_check.py`, `query_quality.py`, and the full regression suite.
- Stage only an explicit allowlist. Push the three commits to `codex/second-brain-markdown-first-quality`, open a Draft PR to `main`, verify the remote tree, complete one whole-branch review, mark ready, squash merge with the expected head SHA, and verify the merged `main` tree equals the reviewed feature tree.

## Final Deliverables

- Verified public AI research Second Brain status and internal source ledger
- Six grounded answers and three-axis quality evidence
- Zero-change Review state unless a real material change is found
- Markdown hub, four Mermaid/fallback flows, optional Obsidian views
- Two original PNG infographics
- Five-minute cue sheet, expected Q&A, and copy-ready broadcaster reply
- Three scoped commits, pushed PR, squash merge commit, and post-merge tree parity evidence
- Explicit list of deferred approvals: question-scoped Current, new T1 intake, Team/Public promotion, and internal footage release
