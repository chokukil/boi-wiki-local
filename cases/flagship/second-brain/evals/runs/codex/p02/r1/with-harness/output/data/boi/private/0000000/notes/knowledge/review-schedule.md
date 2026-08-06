---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-knowledge
title: "Synthetic knowledge review schedule"
description: "SYN-SB-001-v1 evaluation seed"
tags: [Synthetic, SecondBrainEval]
boi_id: boi:private:0000000:eval:review-schedule
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
review_after: 2026-08-09
contains_sensitive: false
knowledge_role: reviewed-knowledge
claim_status: direct
source_refs:
  - type: synthetic-fixture
    ref: sources/01-decision-chat.txt
    sha256: 5be16cc0e29d799b9ed63670979e18a88ae2c849beb55d3dbb59bac09b216463
  - type: document
    ref: sources/10-review-day-reconfirmation.txt
    sha256: 99c99d87357b5a76b2212bc184606877878eb5ce37b77dd600b474f64317c1c0
generated_from:
  - type: synthetic-fixture
    ref: sources/01-decision-chat.txt
    sha256: 5be16cc0e29d799b9ed63670979e18a88ae2c849beb55d3dbb59bac09b216463
  - type: document
    ref: sources/10-review-day-reconfirmation.txt
    sha256: 99c99d87357b5a76b2212bc184606877878eb5ce37b77dd600b474f64317c1c0
---

# Synthetic knowledge review schedule

Reviewed decision: knowledge review occurs every Friday at 15:00.

Evidence history: 2026-08-02 — The project owner reconfirmed the existing Friday 15:00 review schedule.
