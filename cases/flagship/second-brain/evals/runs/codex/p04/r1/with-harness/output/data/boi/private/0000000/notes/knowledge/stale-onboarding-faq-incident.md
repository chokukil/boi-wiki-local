---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-analysis-case
title: "Stale onboarding FAQ incident"
description: "검토 기한이 지난 FAQ 사용과 용어 링크 누락에 관한 합성 사고 분석"
tags: [Synthetic, SecondBrainEval, Incident, Onboarding]
timestamp: 2026-08-02T00:00:00+09:00
boi_id: boi:private:0000000:analysis:stale-onboarding-faq
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
knowledge_role: analysis-case
claim_status: direct
source_refs:
  - type: local-file
    ref: sources/15-incident-retrospective.md
    sha256: e0f7c994becf1125cbef6f670670564b95384ac591fffbe9e851315ae6e41e1e
generated_from:
  - type: local-file
    ref: sources/15-incident-retrospective.md
    sha256: e0f7c994becf1125cbef6f670670564b95384ac591fffbe9e851315ae6e41e1e
---

# Stale onboarding FAQ incident

## Observation

An outdated onboarding FAQ was used twice after its review date.

## Contributing factor

The downstream FAQ did not link to the revised terminology decision. This is a supported contributor, not a confirmed root cause.

## Counterevidence

Direct search for the new term returned the updated term correctly. Search failure must not be recorded as the root cause.

## Unknown

Whether the reminder was delivered remains unknown.

## Decision

Repair the terminology link and the review date, then verify the reminder path separately.
