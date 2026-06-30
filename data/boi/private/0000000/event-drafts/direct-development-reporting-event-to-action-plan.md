---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-event-plan
title: "직개발 Reporting 업무 흐름 계획"
description: "직개발 결과 확인 업무를 Event/업무 요청/Manual/Langflow 흐름으로 연결하는 계획"
timestamp: 2026-06-20T22:04:00+09:00
employee_id: "0000000"
local_owner_ref: local-private:0000000
visibility: local-private
local_only: true
promotion_status: local_only
retention_class: working
retention_until: ""
archive_status: active
review_after: 2026-07-20
contains_sensitive: no
source_refs:
  - type: sop-draft
    ref: ../sop-drafts/direct-development-reporting-sop-draft.md
  - type: shared-runtime-trace
    ref: trace-f91b32904db0434db27c3f84307103ad
---

# Trigger Candidate

| Field | Value |
|---|---|
| event_type | `direct_development.result_check.requested.v1` |
| actor | process engineer or agent |
| payload minimum | product, tech, lot_id, wafer_id, work_id, source_image_ref |
| first SOP stage | Response Trend 확인 |

# 업무 요청 Chain

| Order | Stage | Action key | Type | Runtime status |
|---|---|---|---|---|
| 10 | Response Trend 확인 | `direct_development.quality_response_trend.simulate` | Langflow | SIMULATED, 실제 품질 시스템 호출 아님 |
| 20 | Map View Image 확인 | `direct_development.map_view.simulate` | Langflow | SIMULATED, 실제 Map 분석 시스템 호출 아님 |
| 30 | 단면검사 필요 여부 | `manual.direct_development.decide_cross_section` | manual | manual_required |
| 40 | 단면검사 의뢰 | `direct_development.cross_section_request.simulate` | Langflow | SIMULATED, 실제 단면 검사 시스템 호출 아님 |
| 50 | 단면검사 결과 확인 | `direct_development.cross_section_result.simulate` | Langflow | SIMULATED, 실제 단면 검사 시스템 호출 아님 |
| 60 | 연구소-양산 FAB 비교 Trend 확인 | `direct_development.fab_trend_compare.simulate` | Langflow | SIMULATED, 실제 품질 시스템 호출 아님 |
| 70 | 결과 Reporting | `direct_development.reporting.simulate` | Langflow | SIMULATED |
| 80 | 협의체 공유 Preview | `direct_development.messenger_share_preview.simulate` | Langflow | SIMULATED, 실제 메신저 발송 아님 |
| 90 | 협의체 공유 실행 | `direct_development.messenger_share.publish` | webhook | approval_required |

# Existing Live Reference

Shared runtime trace `trace-f91b32904db0434db27c3f84307103ad` confirms the pattern below.

| Evidence | Confirmed |
|---|---|
| Event Broker chain | yes |
| Action Gateway dispatch | yes |
| BoI Writer generated docs | yes |
| Langflow invocation | `BoI Universal Action Simulator Flow`, 7 simulator actions |
| Manual handoff | `manual.direct_development.decide_cross_section` -> `manual_required` |
| Approval guard | `direct_development.messenger_share.publish` -> `approval_required` |
| Simulation marker | every simulator action has `SIMULATED`, `real_system_connected=false` |

# Manual Stop Rule

사람이 실제로 해야 하는 단계에서는 workflow가 `manual_required` 상태로 멈춘다. 담당자가 완료를 확인하면 `manual_step.completed.v1` 또는 업무별 completion event가 발행되고 다음 action으로 넘어간다.
