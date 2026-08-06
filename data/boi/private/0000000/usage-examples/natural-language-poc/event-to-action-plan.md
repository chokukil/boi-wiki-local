---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-example
title: "Event to SOP/Action/Langflow 계획 예제"
description: "업무 이벤트가 발생했을 때 SOP, Action, Manual handoff, Langflow가 이어지는 흐름을 계획하는 예제"
boi_id: boi:private:0000000:legacy:event-to-action-plan:06835aa10e
classification: internal
owner: "0000000"
artifact_visibility: working
lifecycle_state: working
memory_candidate: false
cleanup_policy: keep
timestamp: 2026-06-20T21:54:00+09:00
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
  - type: shared-runtime-trace
    ref: trace-f91b32904db0434db27c3f84307103ad
  - type: generated-output
    ref: ../../event-drafts/direct-development-reporting-event-to-action-plan.md
---

# Prompt

```text
이 이벤트가 발생하면 어떤 SOP와 Action이 이어지는지 알려줘.
사람이 해야 하는 단계, AI가 할 수 있는 단계, 현재 live action이 있는 단계, 아직 없는 시스템 action을 구분해줘.
```

# Generated Output

- 생성 문서: [direct-development-reporting-event-to-action-plan.md](../../event-drafts/direct-development-reporting-event-to-action-plan.md)
- workflow simulation: [direct-development-reporting-human-ai-flow.md](../../workflow-simulations/direct-development-reporting-human-ai-flow.md)
- Langflow plan: [direct-development-reporting-langflow-harness-plan.md](../../langflow-plans/direct-development-reporting-langflow-harness-plan.md)

# Evidence

Shared BoI Wiki live smoke trace `trace-f91b32904db0434db27c3f84307103ad`에서 아래가 확인됐다.

- Events: `direct_development.result_check.requested.v1`, `direct_development.map_view.requested.v1`, `direct_development.cross_section.decision_required.v1`, `direct_development.cross_section.requested.v1`, `direct_development.fab_trend.compare_requested.v1`, `direct_development.reporting.requested.v1`, `direct_development.share.requested.v1`
- Langflow actions: `direct_development.quality_response_trend.simulate`, `direct_development.map_view.simulate`, `direct_development.cross_section_request.simulate`, `direct_development.cross_section_result.simulate`, `direct_development.fab_trend_compare.simulate`, `direct_development.reporting.simulate`, `direct_development.messenger_share_preview.simulate`
- Approval guard: `direct_development.messenger_share.publish`는 `approval_required`
- Manual handoff: `manual.direct_development.decide_cross_section`은 `manual_required`
- Simulation boundary: 모든 simulator action은 `SIMULATED`, `real_system_connected=false`, "실제 시스템 호출 아님"으로 기록된다.

# How to Verify

1. shared `boi-wiki`에서 `SERVICE_TOKEN="$SERVICE_TOKEN" python scripts/run_direct_development_sop_poc.py`를 실행한다.
2. output의 `trace_id`, generated BoI, `langflow_invoked`, `approval_required_actions`, `manual_required_actions`를 확인한다.
3. 이 local 문서의 action 분류가 live evidence와 candidate gap을 혼동하지 않는지 확인한다.

# Real vs Simulated

direct-development SOP smoke는 실제 runtime evidence다. 단, 품질 시스템/Map 분석 시스템/단면 검사 시스템/메신저 호출은 실제 시스템 호출이 아니라 `BoI Universal Action Simulator Flow` 기반 `SIMULATED` evidence다.
