---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-knowledge
title: "Second Brain onboarding FAQ"
description: "Local Private 운영 경계에 관한 합성 온보딩 질문과 답변"
tags: [Synthetic, SecondBrainEval, Onboarding, FAQ]
timestamp: 2026-08-02T00:00:00+09:00
boi_id: boi:private:0000000:knowledge:second-brain-onboarding-faq
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
lifecycle_state: review-required
memory_candidate: true
cleanup_policy: keep
review_after: 2026-08-09
contains_sensitive: false
knowledge_role: distilled-knowledge
claim_status: direct
source_refs:
  - type: local-file
    ref: sources/13-onboarding-faq.md
    sha256: 69cb0bc9c07a8bcf74cff589aa60e369a7800ab26f9ac78a0c6f7fefd5f485bf
  - type: local-file
    ref: sources/15-incident-retrospective.md
    sha256: e0f7c994becf1125cbef6f670670564b95384ac591fffbe9e851315ae6e41e1e
generated_from:
  - type: local-file
    ref: sources/13-onboarding-faq.md
    sha256: 69cb0bc9c07a8bcf74cff589aa60e369a7800ab26f9ac78a0c6f7fefd5f485bf
  - type: local-file
    ref: sources/15-incident-retrospective.md
    sha256: e0f7c994becf1125cbef6f670670564b95384ac591fffbe9e851315ae6e41e1e
---

# Second Brain onboarding FAQ

## Is Obsidian required?

No. Markdown and an AI agent are sufficient.

## Does MCP upload Local Private files?

No. Read connectivity does not grant upload permission.

## Can agent-memory be promoted directly?

No. It must first be distilled into an eligible BoI type and reviewed.

## Where are conflicts kept?

In a review-required Local state with both claims preserved.

## Review status

The incident retrospective found that the downstream FAQ lacked a link to the revised terminology decision and had been used after its review date. Repair the link and review date before treating this FAQ as current.

## Evidence history

- 2026-08-02 — The incident retrospective moved this FAQ to review-required; direct search for the new term worked, so search failure is not recorded as the root cause.
