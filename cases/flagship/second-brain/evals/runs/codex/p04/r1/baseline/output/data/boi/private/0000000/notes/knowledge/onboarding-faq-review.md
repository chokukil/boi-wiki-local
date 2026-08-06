---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-knowledge
title: "Onboarding FAQ review"
description: "SYN-SB-001 adaptive batch 4 stale FAQ review"
tags: [Synthetic, SecondBrainEval, ReviewRequired, Onboarding]
boi_id: boi:private:0000000:eval:onboarding-faq-review
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
review_after: 2026-08-14
contains_sensitive: false
knowledge_role: review-required
claim_status: stale-review
freshness_status: stale
related_to: boi:private:0000000:eval:stale-onboarding-faq-incident
source_refs:
  - type: synthetic-fixture
    ref: sources/13-onboarding-faq.md
    sha256: 69cb0bc9c07a8bcf74cff589aa60e369a7800ab26f9ac78a0c6f7fefd5f485bf
generated_from:
  - type: synthetic-fixture
    ref: sources/13-onboarding-faq.md
    sha256: 69cb0bc9c07a8bcf74cff589aa60e369a7800ab26f9ac78a0c6f7fefd5f485bf
---

# Onboarding FAQ review

The source currently states:

- Obsidian is not required; Markdown and an AI agent are sufficient.
- MCP read connectivity does not grant permission to upload Local Private files.
- Agent memory must be distilled into an eligible BoI type and reviewed before promotion.
- Conflicts remain in a review-required Local state with both claims preserved.

This FAQ is stale according to the incident record. It is not canonical until its terminology link and review date are repaired and a reviewer confirms the answers.
