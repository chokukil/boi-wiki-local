---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-action-draft
title: "품질 시스템 Response Trend Query Action Draft"
description: "Response Trend 확인 단계를 위한 품질 시스템 API action 후보"
timestamp: 2026-06-20T22:05:00+09:00
employee_id: "0000000"
local_owner_ref: local-private:0000000
visibility: local-private
local_only: true
promotion_status: local_only
retention_class: working
retention_until: ""
archive_status: active
review_after: 2026-07-20
contains_sensitive: unknown
source_refs:
  - type: sop-draft
    ref: ../sop-drafts/direct-development-reporting-sop-draft.md
---

# 업무 요청 Spec Candidate

```yaml
action_key: quality_system.response_trend.query
action_name: Response Trend 확인
connector_kind: api
risk_level: low
approval_required: false
dry_run_supported: true
status: candidate_missing_connector
input_schema:
  type: object
  required: [product, tech, work_id, lot_id, wafer_id]
  properties:
    product:
      type: string
    tech:
      type: string
    work_id:
      type: string
    lot_id:
      type: string
    wafer_id:
      type: string
output_schema:
  type: object
  required: [trend_status, evidence_ref, recommended_next_stage]
  properties:
    trend_status:
      enum: [normal, anomaly_detected, inconclusive]
    evidence_ref:
      type: string
    recommended_next_stage:
      type: string
```

# Draft Notes

- Shared simulator action: `direct_development.quality_response_trend.simulate`.
- 실제 품질 시스템 endpoint, auth method, response schema는 API 문서 확인 전까지 비워 둔다.
- trend가 `anomaly_detected`이면 Map View Image 확인 또는 단면검사 판단으로 이어진다.
