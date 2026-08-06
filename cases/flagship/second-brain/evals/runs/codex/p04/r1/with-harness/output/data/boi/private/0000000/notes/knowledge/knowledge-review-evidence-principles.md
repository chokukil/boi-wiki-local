---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-knowledge
title: "Knowledge review evidence principles"
description: "지속 가능한 지식 문서에서 근거와 해석을 구분하는 원칙"
tags: [Synthetic, SecondBrainEval, KnowledgeReview]
timestamp: 2026-08-02T00:00:00+09:00
boi_id: boi:private:0000000:knowledge:knowledge-review-evidence-principles
visibility: local-private
classification: internal
owner: "0000000"
employee_id: "0000000"
local_owner_ref: local-private:0000000
local_only: true
promotion_status: local_only
retention_class: knowledge
retention_until: ""
archive_status: active
artifact_visibility: memory
lifecycle_state: draft
memory_candidate: true
cleanup_policy: keep
review_after: 2026-08-09
contains_sensitive: false
knowledge_role: distilled-knowledge
claim_status: direct
source_refs:
  - type: local-file
    ref: sources/03-public-web-clip.md
    sha256: bae4daa95a7cdaee037e60833467b9c4173f109fda59628e6f20e3ee43fa8c71
  - type: local-file
    ref: sources/05-operating-guide.pdf
    sha256: 6b2b928c844f99b1d8eddc01384ef9cc59429f171ab3810ff14e1d2a2b35dc92
generated_from:
  - type: local-file
    ref: sources/03-public-web-clip.md
    sha256: bae4daa95a7cdaee037e60833467b9c4173f109fda59628e6f20e3ee43fa8c71
  - type: local-file
    ref: sources/05-operating-guide.pdf
    sha256: 6b2b928c844f99b1d8eddc01384ef9cc59429f171ab3810ff14e1d2a2b35dc92
---

# Knowledge review evidence principles

- Keep the source statement, author interpretation, counterevidence, and next review date distinct.
- Preserve source bytes and do not rewrite history when evidence conflicts.
- Require human review to resolve conflicts.
- Treat a graph as a view over explicit links, not as evidence by itself.
- Require a sanitized exact preview and separate approval before promotion.

These principles remain draft until reviewed.

## Evidence history

- 2026-08-02 — The operating guide reinforced source preservation and added explicit conflict and promotion safeguards.
