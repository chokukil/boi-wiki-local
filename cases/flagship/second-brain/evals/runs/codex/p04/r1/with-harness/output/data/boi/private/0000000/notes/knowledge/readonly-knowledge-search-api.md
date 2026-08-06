---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-knowledge
title: "Read-only knowledge search API"
description: "ACL-visible canonical knowledge를 조회하는 합성 읽기 전용 API 메모"
tags: [Synthetic, SecondBrainEval, API, ReadOnly]
timestamp: 2026-08-02T00:00:00+09:00
boi_id: boi:private:0000000:knowledge:readonly-knowledge-search-api
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
    ref: sources/14-readonly-api-note.md
    sha256: 97e7d613c9254f6412c08793670ae7a792f3e56f583ca69119a1e7d6c4562006
generated_from:
  - type: local-file
    ref: sources/14-readonly-api-note.md
    sha256: 97e7d613c9254f6412c08793670ae7a792f3e56f583ca69119a1e7d6c4562006
---

# Read-only knowledge search API

- Endpoint: `GET /knowledge/search`
- Purpose: read-only lookup of ACL-visible canonical knowledge.
- Mutation capability: none.
- Required citation: canonical BoI ID, revision, and visibility.
- Boundary: do not infer a write endpoint or include Local paths in a query.

This is a Local Private draft and is not approved for publication.
