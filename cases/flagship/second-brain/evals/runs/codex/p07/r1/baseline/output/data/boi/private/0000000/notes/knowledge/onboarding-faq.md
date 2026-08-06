---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-knowledge
title: "Synthetic onboarding FAQ"
description: "Local onboarding answers for the synthetic BoI fixture"
tags: [Synthetic, SecondBrainEval, Onboarding, FAQ]
boi_id: boi:private:0000000:eval:onboarding-faq
visibility: local-private
classification: internal
owner: "0000000"
employee_id: "0000000"
local_owner_ref: local-private:0000000
local_only: true
promotion_status: local_only
artifact_visibility: memory
lifecycle_state: memory
review_after: 2026-08-09
contains_sensitive: false
knowledge_role: reference
claim_status: direct
source_refs:
  - type: synthetic-fixture
    ref: sources/13-onboarding-faq.md
    sha256: 69cb0bc9c07a8bcf74cff589aa60e369a7800ab26f9ac78a0c6f7fefd5f485bf
generated_from:
  - type: synthetic-fixture
    ref: sources/13-onboarding-faq.md
    sha256: 69cb0bc9c07a8bcf74cff589aa60e369a7800ab26f9ac78a0c6f7fefd5f485bf
---

# Synthetic onboarding FAQ

## Is Obsidian required?

No. Markdown and an AI agent are sufficient.

## Does MCP upload Local Private files?

No. Read connectivity does not grant upload permission.

## Can agent-memory be promoted directly?

No. It must first be distilled into an eligible BoI type and reviewed.

## Where are conflicts kept?

In a review-required Local state, with both claims preserved.
