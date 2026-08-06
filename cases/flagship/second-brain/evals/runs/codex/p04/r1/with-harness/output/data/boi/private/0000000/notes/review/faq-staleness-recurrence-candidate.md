---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-hypothesis
title: "FAQ staleness recurrence candidate"
description: "오래된 FAQ와 최신 결정 링크 누락이 반복되는지 검토하는 후보"
tags: [LocalPrivate, SecondBrain, ReviewRequired, Recurrence]
timestamp: 2026-08-02T00:00:00+09:00
boi_id: boi:private:0000000:hypothesis:faq-staleness-recurrence
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
knowledge_role: recurrence-candidate
claim_status: inferred
source_refs:
  - type: local-file
    ref: sources/19-recurrence-note.md
    sha256: b25d3a36cf95c94af54967ffabd16041d3177b389768264c6ff0e122724898cd
  - type: local-analysis
    ref: data/boi/private/0000000/notes/knowledge/stale-onboarding-faq-incident.md
    sha256: 0782f8df129f0a675b807c462246cc4c6df3549b467e201c3b4cbf0567fbc145
generated_from:
  - type: local-file
    ref: sources/19-recurrence-note.md
    sha256: b25d3a36cf95c94af54967ffabd16041d3177b389768264c6ff0e122724898cd
  - type: local-analysis
    ref: data/boi/private/0000000/notes/knowledge/stale-onboarding-faq-incident.md
    sha256: 0782f8df129f0a675b807c462246cc4c6df3549b467e201c3b4cbf0567fbc145
---

# FAQ staleness recurrence candidate

## Candidate signal

An expired FAQ lacks a link to the latest reviewed decision.

## Reuse condition

Confirm that the document is stale and the canonical term changed.

## Exclusion

A search-ranking issue without a stale link is a different case.

Human review is required before this can be called a recurrence fingerprint.
