---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-note
title: "Knowledge review day conflict"
description: "검토된 금요일 결정과 출처 불명 목요일 주장 사이의 충돌"
tags: [LocalPrivate, SecondBrain, ReviewRequired, Conflict]
timestamp: 2026-08-02T00:00:00+09:00
boi_id: boi:private:0000000:review:knowledge-review-day-conflict
visibility: local-private
classification: internal
owner: "0000000"
employee_id: "0000000"
local_owner_ref: local-private:0000000
local_only: true
promotion_status: local_only
retention_class: review
retention_until: ""
archive_status: active
artifact_visibility: memory
lifecycle_state: review-required
memory_candidate: true
cleanup_policy: keep
review_after: 2026-08-09
contains_sensitive: false
knowledge_role: review-queue
claim_status: conflicted
source_refs:
  - type: local-file
    ref: sources/08-conflicting-review-day.md
    sha256: 1b6154bc142104502974e5e85d48e1bc7f4a5123fb75c1aaae3ebc5f69223e18
  - type: local-knowledge
    ref: data/boi/private/0000000/notes/knowledge/review-schedule.md
    sha256: 17c7e8d1bb487f7c40af83ccbd61ef44671f120e9463d31014a7987e53fd4106
generated_from:
  - type: local-file
    ref: sources/08-conflicting-review-day.md
    sha256: 1b6154bc142104502974e5e85d48e1bc7f4a5123fb75c1aaae3ebc5f69223e18
  - type: local-knowledge
    ref: data/boi/private/0000000/notes/knowledge/review-schedule.md
    sha256: 17c7e8d1bb487f7c40af83ccbd61ef44671f120e9463d31014a7987e53fd4106
---

# Knowledge review day conflict

## Current reviewed decision

The knowledge review remains Friday at 15:00. This page does not change that decision.

## Conflicting claim

A source with an unknown author claims Thursday at 15:00, but provides no meeting link or decision record.

## Required review

A human reviewer must supply authoritative evidence before the current decision can be revised. Both claims and their provenance are preserved here.
