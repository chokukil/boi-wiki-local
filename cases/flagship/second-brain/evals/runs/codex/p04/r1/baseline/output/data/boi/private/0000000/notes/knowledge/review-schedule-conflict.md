---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-knowledge
title: "Knowledge review schedule conflict"
description: "SYN-SB-001 adaptive batch 3 conflict record"
tags: [Synthetic, SecondBrainEval, ReviewRequired, Conflict]
boi_id: boi:private:0000000:eval:review-schedule-conflict
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
claim_status: conflict
conflicts_with: boi:private:0000000:eval:review-schedule
source_refs:
  - type: synthetic-fixture
    ref: sources/08-conflicting-review-day.md
    sha256: 1b6154bc142104502974e5e85d48e1bc7f4a5123fb75c1aae3ebc5f69223e18
generated_from:
  - type: synthetic-fixture
    ref: sources/08-conflicting-review-day.md
    sha256: 1b6154bc142104502974e5e85d48e1bc7f4a5123fb75c1aae3ebc5f69223e18
---

# Knowledge review schedule conflict

## Preserved claims

- Reviewed decision: the knowledge review occurs every Friday at 15:00.
- Unverified conflicting claim: the knowledge review occurs every Thursday at 15:00.

The Thursday claim comes from an unknown author's memory and has no meeting link or decision record. It remains a conflict candidate and does not overwrite the reviewed Friday decision. Human resolution is required.
