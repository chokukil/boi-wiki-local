---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-example
title: "팀 주간보고 승격 예제"
description: "Local Private 주간보고를 Team visibility 후보로 정리하는 예제"
boi_id: boi:private:0000000:legacy:weekly-report-promotion:c28b128d50
classification: internal
owner: "0000000"
artifact_visibility: working
lifecycle_state: working
memory_candidate: false
cleanup_policy: keep
timestamp: 2026-06-20T21:58:00+09:00
employee_id: "0000000"
local_owner_ref: local-private:0000000
visibility: local-private
local_only: true
promotion_status: local_only
retention_class: record
retention_until: ""
archive_status: active
review_after: 2026-09-20
contains_sensitive: no
source_refs:
  - type: generated-output
    ref: ../../reports/sample-weekly-report.md
  - type: generated-output
    ref: ../../promotion-drafts/sample-weekly-report-team-promotion-draft.md
---

# Prompt

```text
팀 주간보고 작성한 거 괜찮아 보이네. 팀 주간보고로 올려줘.
```

# Generated Output

- 작성본: [sample-weekly-report.md](../../reports/sample-weekly-report.md)
- 승격 후보: [sample-weekly-report-team-promotion-draft.md](../../promotion-drafts/sample-weekly-report-team-promotion-draft.md)
- target visibility는 `team`이고, 최종 게시 전 사용자 승인이 필요하다.

# Evidence

- 보고 내용은 local report로 먼저 남긴다.
- Team promotion draft는 source_refs와 redaction checklist를 포함한다.

# How to Verify

1. 주간보고 원본과 promotion draft가 분리되어 있는지 확인한다.
2. target audience, 제외할 민감정보, 게시 후 rollback/contact가 포함됐는지 확인한다.
3. 사용자가 승인하기 전 remote publish가 실행되지 않았는지 확인한다.

# Real vs Simulated

주간보고와 promotion draft는 실제 local output이다. Team 게시 자체는 approval required로 남긴다.
