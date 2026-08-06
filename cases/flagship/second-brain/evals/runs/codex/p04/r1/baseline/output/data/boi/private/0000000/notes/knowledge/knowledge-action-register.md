---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-knowledge
title: "Synthetic knowledge action register"
description: "SYN-SB-001 adaptive batch 2 local synthesis"
tags: [Synthetic, SecondBrainEval, Actions]
boi_id: boi:private:0000000:eval:knowledge-action-register
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
review_after: 2026-08-05
contains_sensitive: false
knowledge_role: action-register
claim_status: direct
source_refs:
  - type: synthetic-fixture
    ref: sources/04-action-register.csv
    sha256: 27f8da41d9560b604e9b8fdb44db72d39da0b5a13a7702fdda9db967617d2cac
generated_from:
  - type: synthetic-fixture
    ref: sources/04-action-register.csv
    sha256: 27f8da41d9560b604e9b8fdb44db72d39da0b5a13a7702fdda9db967617d2cac
---

# Synthetic knowledge action register

| Action | Owner role | Status | Due date |
|---|---|---|---|
| Confirm Atlas Ledger aliases | knowledge-steward | open | 2026-08-07 |
| Recover the missing email checklist | project-owner | blocked | 2026-08-05 |
| Review the stale onboarding FAQ | onboarding-owner | open | 2026-08-14 |
| Publish the approved read-only API note | api-owner | draft | 2026-08-21 |

This is a source-status snapshot. It does not imply that blocked, draft, or pending actions have been completed.
