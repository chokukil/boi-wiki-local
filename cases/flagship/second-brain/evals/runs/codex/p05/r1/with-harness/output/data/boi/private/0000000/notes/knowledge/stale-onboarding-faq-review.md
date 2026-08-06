---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-analysis-case
title: "Stale downstream onboarding FAQ review"
description: "Independent downstream-staleness review for SYN-SB-001-v1"
tags: [Synthetic, SecondBrainEval, ReviewRequired]
boi_id: boi:private:0000000:eval:stale-onboarding-faq-review
visibility: local-private
classification: internal
owner: "0000000"
employee_id: "0000000"
local_owner_ref: local-private:0000000
local_only: true
promotion_status: local_only
artifact_visibility: memory
lifecycle_state: working
archive_status: active
review_after: 2026-08-09
contains_sensitive: false
knowledge_role: comparison
claim_status: observed
source_refs:
  - type: synthetic-fixture
    ref: sources/13-onboarding-faq.md
    sha256: 69cb0bc9c07a8bcf74cff589aa60e369a7800ab26f9ac78a0c6f7fefd5f485bf
  - type: synthetic-fixture
    ref: sources/15-incident-retrospective.md
    sha256: e0f7c994becf1125cbef6f670670564b95384ac591fffbe9e851315ae6e41e1e
  - type: local-knowledge
    ref: data/boi/private/0000000/notes/knowledge/onboarding-faq.md
    sha256: 801fc5e936fd047c8c627fb9f7d2b610f1854e7369f8c74e5a5fd479773f8d65
  - type: local-knowledge
    ref: data/boi/private/0000000/notes/knowledge/atlas-ledger.md
    sha256: c50d55d03676c8271641932d982d62f78263fe8a5f1a03af5776f69df94371d7
generated_from:
  - type: synthetic-fixture
    ref: sources/13-onboarding-faq.md
    sha256: 69cb0bc9c07a8bcf74cff589aa60e369a7800ab26f9ac78a0c6f7fefd5f485bf
  - type: synthetic-fixture
    ref: sources/15-incident-retrospective.md
    sha256: e0f7c994becf1125cbef6f670670564b95384ac591fffbe9e851315ae6e41e1e
  - type: local-knowledge
    ref: data/boi/private/0000000/notes/knowledge/onboarding-faq.md
    sha256: 801fc5e936fd047c8c627fb9f7d2b610f1854e7369f8c74e5a5fd479773f8d65
  - type: local-knowledge
    ref: data/boi/private/0000000/notes/knowledge/atlas-ledger.md
    sha256: c50d55d03676c8271641932d982d62f78263fe8a5f1a03af5776f69df94371d7
---

# Stale downstream onboarding FAQ review

## Observed condition

- The compiled onboarding FAQ has `review_after: 2026-07-31`, which is before this review date of 2026-08-02.
- The incident retrospective reports that the outdated FAQ was used twice after its review date.
- The compiled FAQ states that it lacks a link to the revised terminology decision, and it contains no Markdown link to the Atlas Ledger terminology page.
- The FAQ's recorded source hash matches the current `sources/13-onboarding-faq.md` bytes.

## Supporting evidence

- `sources/13-onboarding-faq.md` states the current onboarding boundaries for Obsidian, MCP upload permission, agent-memory promotion, and conflict preservation.
- `sources/15-incident-retrospective.md` identifies the missing downstream link as a contributing factor.

## Counterevidence

- Direct search returned the new term correctly when queried, so the selected evidence does not support claiming search failure as the root cause.

## Unknowns

- Whether the review reminder was delivered.
- Whether the dictionary owner has completed review of “Atlas Ledger” as the preferred term; the existing terminology page still describes it as a candidate and keeps “Blue Ledger” as an alias pending that review.

## Decision boundary

Do not edit the onboarding FAQ, Atlas Ledger terminology page, or incident conclusion in this review. Do not claim that search failure was the root cause.

## Next validation

1. Confirm whether the reminder was delivered.
2. Confirm the dictionary owner's terminology decision status.
3. After human review, separately approve repair of the FAQ link and review date.

Confidence: high that the downstream FAQ is overdue and missing the link; medium confidence that the missing link contributed to the two uses because that attribution comes from the retrospective.
