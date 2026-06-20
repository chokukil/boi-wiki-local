---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-event-plan
title: "직개발 Reporting Event to Action Plan"
description: "직개발 결과 확인 SOP를 Event/Action/Manual/Langflow 흐름으로 연결하는 계획"
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
    ref: trace-442fd8c619794e73883ee22833abdab2
---

# Trigger Candidate

| Field | Value |
|---|---|
| event_type | `direct_development.result_check.requested.v1` |
| actor | process engineer or agent |
| payload minimum | product, tech, lot_id, wafer_id, work_id, source_image_ref |
| first SOP stage | Response Trend 확인 |

# Action Chain

| Order | Stage | Action key | Type | Runtime status |
|---|---|---|---|---|
| 10 | Response Trend 확인 | `quality_system.response_trend.query` | AI/API | missing system action |
| 20 | Map View Image 확인 | `map_analysis_system.map_view.inspect` | AI/API | missing system action |
| 30 | 단면검사 필요 여부 | `manual.direct_development.decide_cross_section` | manual | manual_required |
| 40 | 단면검사 의뢰 | `cross_section_inspection_system.cross_section.request` | API | missing system action |
| 50 | 단면검사 결과 확인 | `cross_section_inspection_system.cross_section.result.read` | API | missing system action |
| 60 | 연구소-양산 FAB 비교 Trend 확인 | `quality_system.fab_trend.compare` | AI/API | missing system action |
| 70 | 결과 Reporting | `langflow.direct_development.reporting` | Langflow | candidate AI action |
| 80 | 협의체 공유 | `messenger.committee.share` | webhook/API | missing system action |

# Existing Live Reference

Shared runtime trace `trace-442fd8c619794e73883ee22833abdab2` confirms the pattern below.

| Evidence | Confirmed |
|---|---|
| Event Broker chain | yes |
| Action Gateway dispatch | yes |
| BoI Writer generated docs | yes |
| Langflow invocation | `langflow.boi.reference_flow`, `langflow.equipment.stage_analysis` |
| Manual handoff | `manual_required` |
| Approval guard | `approval_required` |

# Manual Stop Rule

사람이 실제로 해야 하는 단계에서는 workflow가 `manual_required` 상태로 멈춘다. 담당자가 완료를 확인하면 `manual_step.completed.v1` 또는 업무별 completion event가 발행되고 다음 action으로 넘어간다.
