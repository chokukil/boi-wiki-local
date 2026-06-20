---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-workflow-simulation
title: "직개발 Reporting Human + AI Workflow Simulation"
description: "사람과 AI가 함께 진행하는 직개발 Reporting workflow dry-run"
timestamp: 2026-06-20T22:07:00+09:00
employee_id: "0000000"
local_owner_ref: local-private:0000000
visibility: local-private
local_only: true
promotion_status: local_only
retention_class: ephemeral
retention_until: 2026-09-18
archive_status: active
review_after: 2026-07-20
contains_sensitive: no
source_refs:
  - type: event-plan
    ref: ../event-drafts/direct-development-reporting-event-to-action-plan.md
---

# Dry Run Timeline

| Step | Event or Action | Expected status | Who |
|---|---|---|---|
| 1 | `direct_development.result_check.requested.v1` | published | human or agent |
| 2 | `direct_development.quality_response_trend.simulate` | SIMULATED / langflow_invoked | AI |
| 3 | `direct_development.map_view.simulate` | SIMULATED / langflow_invoked | AI |
| 4 | `manual.direct_development.decide_cross_section` | manual_required | human |
| 5 | `direct_development.cross_section_request.simulate` + `direct_development.cross_section_result.simulate` | SIMULATED / langflow_invoked | AI |
| 6 | `direct_development.reporting.simulate` | SIMULATED / langflow_invoked | AI |
| 7 | `direct_development.messenger_share.publish` | approval_required | human + system |

# Human Handoff

단면검사 필요 여부가 결정되지 않으면 workflow는 멈춘다. 사람이 "단면검사 필요, In-Line Wafer로 진행 완료"처럼 완료 내용을 알려주면 completion event가 발행되고 다음 stage로 넘어간다.

# Runtime Reference

Shared trace `trace-f91b32904db0434db27c3f84307103ad`는 direct-development SOP 자체의 live evidence다. manual handoff는 `manual_required`로 남고, 협의체 공유 실행은 `approval_required`로 멈춘다. 품질 시스템/Map 분석 시스템/단면 검사 시스템/메신저 호출은 실제 시스템 호출이 아니라 `SIMULATED` action이다.
