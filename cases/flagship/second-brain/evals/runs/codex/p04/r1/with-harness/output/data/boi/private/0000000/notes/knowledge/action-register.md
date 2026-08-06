---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-knowledge
title: "Synthetic action register"
description: "검토가 필요한 지속 업무 항목과 현재 상태"
tags: [Synthetic, SecondBrainEval, ActionRegister]
timestamp: 2026-08-02T00:00:00+09:00
boi_id: boi:private:0000000:knowledge:action-register
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
review_after: 2026-08-05
contains_sensitive: false
knowledge_role: working-knowledge
claim_status: direct
source_refs:
  - type: local-file
    ref: sources/04-action-register.csv
    sha256: 27f8da41d9560b604e9b8fdb44db72d39da0b5a13a7702fdda9db967617d2cac
  - type: local-file
    ref: sources/14-readonly-api-note.md
    sha256: 97e7d613c9254f6412c08793670ae7a792f3e56f583ca69119a1e7d6c4562006
  - type: local-file
    ref: sources/15-incident-retrospective.md
    sha256: e0f7c994becf1125cbef6f670670564b95384ac591fffbe9e851315ae6e41e1e
  - type: local-file
    ref: sources/17-weekly-report.md
    sha256: 8fbb6e1ff9d684767b17fea8a3b897cccae818b7968493364f7dff6a08e25887
generated_from:
  - type: local-file
    ref: sources/04-action-register.csv
    sha256: 27f8da41d9560b604e9b8fdb44db72d39da0b5a13a7702fdda9db967617d2cac
  - type: local-file
    ref: sources/14-readonly-api-note.md
    sha256: 97e7d613c9254f6412c08793670ae7a792f3e56f583ca69119a1e7d6c4562006
  - type: local-file
    ref: sources/15-incident-retrospective.md
    sha256: e0f7c994becf1125cbef6f670670564b95384ac591fffbe9e851315ae6e41e1e
  - type: local-file
    ref: sources/17-weekly-report.md
    sha256: 8fbb6e1ff9d684767b17fea8a3b897cccae818b7968493364f7dff6a08e25887
---

# Synthetic action register

| ID | Action | Owner role | Status | Due |
|---|---|---|---|---|
| SYN-A01 | Confirm Atlas Ledger aliases | knowledge-steward | open | 2026-08-07 |
| SYN-A02 | Recover missing email checklist | project-owner | blocked | 2026-08-05 |
| SYN-A03 | Review stale onboarding FAQ | onboarding-owner | open | 2026-08-14 |
| SYN-A04 | Publish approved read-only API note | api-owner | draft | 2026-08-21 |

The row explicitly marked `not-knowledge` was excluded from durable knowledge.

## Evidence history

- 2026-08-02 — The read-only API note supplied the draft content for SYN-A04; publication remains unapproved.
- 2026-08-02 — The incident retrospective confirmed the stale FAQ review action and directed link and review-date repair without blaming search as the root cause.
- 2026-08-02 — The weekly report reconfirmed the missing checklist, conflict resolution, and alias validation as open work.
