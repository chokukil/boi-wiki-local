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
| 2 | `smarttas.response_trend.query` | candidate/dry-run | AI/API |
| 3 | `smartyes.map_view.inspect` | candidate/dry-run | AI/API |
| 4 | `manual.direct_development.decide_cross_section` | manual_required | human |
| 5 | `smartaps.cross_section.request` | candidate | system |
| 6 | `langflow.direct_development.reporting` | candidate | AI |
| 7 | `cube.committee.share` | approval_required or manual_required | human + system |

# Human Handoff

단면검사 필요 여부가 결정되지 않으면 workflow는 멈춘다. 사람이 "단면검사 필요, In-Line Wafer로 진행 완료"처럼 완료 내용을 알려주면 completion event가 발행되고 다음 stage로 넘어간다.

# Runtime Reference

Shared trace `trace-442fd8c619794e73883ee22833abdab2`는 같은 구조의 live evidence다. 설비 이상 workflow에서는 manual handoff와 approval_required action이 실제로 남았다.
