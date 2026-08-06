---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-knowledge
title: "Stale onboarding FAQ incident"
description: "SYN-SB-001 adaptive batch 2 local synthesis"
tags: [Synthetic, SecondBrainEval, Incident]
boi_id: boi:private:0000000:eval:stale-onboarding-faq-incident
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
review_after: 2026-08-14
contains_sensitive: false
knowledge_role: incident-knowledge
claim_status: direct
source_refs:
  - type: synthetic-fixture
    ref: sources/15-incident-retrospective.md
    sha256: e0f7c994becf1125cbef6f670670564b95384ac591fffbe9e851315ae6e41e1e
  - type: synthetic-fixture
    ref: sources/04-action-register.csv
    sha256: 27f8da41d9560b604e9b8fdb44db72d39da0b5a13a7702fdda9db967617d2cac
generated_from:
  - type: synthetic-fixture
    ref: sources/15-incident-retrospective.md
    sha256: e0f7c994becf1125cbef6f670670564b95384ac591fffbe9e851315ae6e41e1e
  - type: synthetic-fixture
    ref: sources/04-action-register.csv
    sha256: 27f8da41d9560b604e9b8fdb44db72d39da0b5a13a7702fdda9db967617d2cac
---

# Stale onboarding FAQ incident

## Finding

An outdated onboarding FAQ was used twice after its review date. The downstream FAQ did not link to the revised terminology decision.

## Counterevidence and unknowns

Search returned the new term correctly when queried directly. Whether the reminder was delivered is unknown.

## Decision

Repair the link and review date. Do not classify search failure as the root cause. The action register keeps the FAQ review open until 2026-08-14.
