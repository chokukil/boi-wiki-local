---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-knowledge
title: "Stale-link recurrence candidate review"
description: "SYN-SB-001 adaptive batch 5 recurrence review"
tags: [Synthetic, SecondBrainEval, ReviewRequired, Recurrence]
boi_id: boi:private:0000000:eval:stale-link-recurrence-candidate
visibility: local-private
classification: internal
owner: "0000000"
employee_id: "0000000"
local_owner_ref: local-private:0000000
local_only: true
promotion_status: local_only
artifact_visibility: memory
lifecycle_state: review-required
archive_status: active
review_after: 2026-08-09
contains_sensitive: false
knowledge_role: review-required
claim_status: candidate-unconfirmed
fingerprint_status: not-confirmed
human_review_required: true
related_to: boi:private:0000000:eval:stale-onboarding-faq-incident
source_refs:
  - type: synthetic-fixture
    ref: sources/19-recurrence-note.md
    sha256: b25d3a36cf95c94af54967ffabd16041d3177b389768264c6ff0e122724898cd
generated_from:
  - type: synthetic-fixture
    ref: sources/19-recurrence-note.md
    sha256: b25d3a36cf95c94af54967ffabd16041d3177b389768264c6ff0e122724898cd
---

# Stale-link recurrence candidate review

- Signal: an expired FAQ lacks a link to the latest reviewed decision.
- Reuse condition: confirm that the document is stale and the canonical term changed.
- Exclusion: a search-ranking issue without a stale link is a different case.

This is a recurrence candidate, not a confirmed recurrence fingerprint. Human review remains required.
