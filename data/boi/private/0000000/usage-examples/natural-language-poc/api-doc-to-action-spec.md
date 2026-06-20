---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-example
title: "API 문서에서 BoI Action Spec 초안 만들기"
description: "기존 API 설명을 BoI Action Gateway spec 후보로 변환하는 예제"
timestamp: 2026-06-20T21:55:00+09:00
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
    ref: ../../action-drafts/smarttas-response-trend-action-draft.md
---

# Prompt

```text
기존 API 문서를 BoI Action Spec 초안으로 만들어줘.
Response Trend 확인 API라고 가정하고, payload schema, risk level, dry-run, approval 필요 여부를 같이 정리해줘.
```

# Generated Output

- 생성 문서: [smarttas-response-trend-action-draft.md](../../action-drafts/smarttas-response-trend-action-draft.md)
- action key 후보: `smarttas.response_trend.query`
- connector kind 후보: `api`

# Evidence

- 근거 SOP stage: `Response Trend 확인`
- 비교 가능한 live action: shared `boi-wiki` action catalog의 `sop.equipment.request_trend_history`
- live smoke trace에서 `sop.equipment.request_trend_history`가 `invoked`로 기록됐다.

# How to Verify

1. 기존 API 문서가 있으면 endpoint, auth, request/response schema를 source_refs에 추가한다.
2. 실제 connector가 없으면 `missing_system_action` 또는 `candidate` 상태로 둔다.
3. high risk이면 Action Gateway가 `approval_required`로 막는지 별도 smoke를 설계한다.

# Real vs Simulated

Action Spec Markdown은 실제 local draft다. smartTAS API connector는 아직 live 검증되지 않았으므로 candidate로 표시한다.
