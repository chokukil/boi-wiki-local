---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-example
title: "API 문서에서 업무 요청 초안 만들기"
description: "기존 API 설명을 BoI 업무 요청 후보로 변환하고 업무 흐름에 연결하는 예제"
boi_id: boi:private:0000000:legacy:api-doc-to-action-spec:0373e90e00
classification: internal
owner: "0000000"
artifact_visibility: working
lifecycle_state: working
memory_candidate: false
cleanup_policy: keep
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
    ref: ../../action-drafts/quality-system-response-trend-action-draft.md
---

# Prompt

```text
기존 API 문서를 BoI 업무 요청 초안으로 만들고 업무 흐름에 연결해줘.
Response Trend 확인 API라고 가정하고, payload schema, risk level, 실행 전 확인, approval 필요 여부, 기존 WorkflowDefinition 중복 확인을 같이 정리해줘.
```

# Generated Output

- 생성 문서: [quality-system-response-trend-action-draft.md](../../action-drafts/quality-system-response-trend-action-draft.md)
- action key 후보: `quality_system.response_trend.query`
- connector kind 후보: `api`

# Evidence

- 근거 SOP stage: `Response Trend 확인`
- 비교 가능한 live simulator action: shared `boi-wiki` action catalog의 `direct_development.quality_response_trend.simulate`
- live smoke trace `trace-f91b32904db0434db27c3f84307103ad`에서 해당 action이 `langflow_invoked`, `SIMULATED`, `real_system_connected=false`로 기록됐다.

# How to Verify

1. 기존 API 문서가 있으면 endpoint, auth, request/response schema를 source_refs에 추가한다.
2. 실제 connector가 없으면 `missing_system_action` 또는 `candidate` 상태로 둔다.
3. high risk이면 Action Gateway가 `approval_required`로 막는지 별도 smoke를 설계한다.

# Real vs Simulated

업무 요청 Spec Markdown은 실제 local draft다. 품질 시스템 실제 connector는 아직 연결하지 않고, shared BoI Wiki에서는 `BoI Universal Action Simulator Flow` 기반 `SIMULATED` 업무 요청으로 검증한다.
