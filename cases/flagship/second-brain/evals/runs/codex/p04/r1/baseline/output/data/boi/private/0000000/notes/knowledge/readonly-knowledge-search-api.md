---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-knowledge
title: "Read-only knowledge search API"
description: "SYN-SB-001 adaptive batch 2 local draft"
tags: [Synthetic, SecondBrainEval, API]
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
archive_status: active
review_after: 2026-08-21
contains_sensitive: false
knowledge_role: draft-knowledge
document_status: draft
claim_status: direct
source_refs:
  - type: synthetic-fixture
    ref: sources/14-readonly-api-note.md
    sha256: 97e7d613c9254f6412c08793670ae7a792f3e56f583ca69119a1e7d6c4562006
  - type: synthetic-fixture
    ref: sources/04-action-register.csv
    sha256: 27f8da41d9560b604e9b8fdb44db72d39da0b5a13a7702fdda9db967617d2cac
generated_from:
  - type: synthetic-fixture
    ref: sources/14-readonly-api-note.md
    sha256: 97e7d613c9254f6412c08793670ae7a792f3e56f583ca69119a1e7d6c4562006
  - type: synthetic-fixture
    ref: sources/04-action-register.csv
    sha256: 27f8da41d9560b604e9b8fdb44db72d39da0b5a13a7702fdda9db967617d2cac
---

# Read-only knowledge search API

- Endpoint: `GET /knowledge/search`
- Purpose: read-only lookup of ACL-visible canonical knowledge
- Mutation capability: none
- Required citation: canonical BoI ID, revision, and visibility

Do not infer a write endpoint. Do not place Local Private paths in a query. This note remains a Local Private draft until its publication action is approved and completed.
