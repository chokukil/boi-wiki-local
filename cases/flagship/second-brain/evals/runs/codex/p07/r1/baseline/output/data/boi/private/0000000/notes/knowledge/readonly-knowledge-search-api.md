---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-knowledge
title: "Synthetic read-only knowledge search API"
description: "Read-only lookup constraints for the synthetic BoI fixture"
tags: [Synthetic, SecondBrainEval, API, ReadOnly]
boi_id: boi:private:0000000:eval:readonly-knowledge-search-api
visibility: local-private
classification: internal
owner: "0000000"
employee_id: "0000000"
local_owner_ref: local-private:0000000
local_only: true
promotion_status: local_only
artifact_visibility: memory
lifecycle_state: memory
review_after: 2026-08-09
contains_sensitive: false
knowledge_role: technical-reference
claim_status: direct
source_refs:
  - type: synthetic-fixture
    ref: sources/14-readonly-api-note.md
    sha256: 97e7d613c9254f6412c08793670ae7a792f3e56f583ca69119a1e7d6c4562006
generated_from:
  - type: synthetic-fixture
    ref: sources/14-readonly-api-note.md
    sha256: 97e7d613c9254f6412c08793670ae7a792f3e56f583ca69119a1e7d6c4562006
---

# Synthetic read-only knowledge search API

- Endpoint: `GET /knowledge/search`
- Purpose: Read-only lookup of ACL-visible canonical knowledge.
- Mutation capability: None.
- Required citation fields: Canonical BoI ID, revision, and visibility.

Do not infer a write endpoint. Do not place Local paths in a query or treat read connectivity as upload permission.
