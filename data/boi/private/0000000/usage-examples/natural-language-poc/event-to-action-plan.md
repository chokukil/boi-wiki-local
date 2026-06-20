---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-example
title: "Event to SOP/Action/Langflow 계획 예제"
description: "업무 이벤트가 발생했을 때 SOP, Action, Manual handoff, Langflow가 이어지는 흐름을 계획하는 예제"
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
    ref: trace-442fd8c619794e73883ee22833abdab2
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

Shared BoI Wiki live smoke trace `trace-442fd8c619794e73883ee22833abdab2`에서 아래가 확인됐다.

- Events: `equipment.alarm.raised.v1`, `root_cause.analysis.requested.v1`, `maintenance.guide.requested.v1`, `corrective_action.requested.v1`
- Langflow actions: `langflow.boi.reference_flow`, `langflow.equipment.stage_analysis`
- Approval guard: `sop.equipment.block_process_progress`, `sop.equipment.change_spec_rule`는 `approval_required`
- Manual handoff: `manual.equipment.review_root_cause` 등은 `manual_required`

# How to Verify

1. shared `boi-wiki`에서 `python scripts/run_equipment_sop_poc.py`를 실행한다.
2. output의 `trace_id`, generated BoI, `langflow_invoked`, `approval_required_actions`, `manual_handoffs`를 확인한다.
3. 이 local 문서의 action 분류가 live evidence와 candidate gap을 혼동하지 않는지 확인한다.

# Real vs Simulated

설비 이상 SOP smoke는 실제 runtime evidence다. 직개발 결과 확인 SOP의 품질 시스템/Map 분석 시스템/단면 검사 시스템/메신저 action은 현재 candidate gap이며, live connector가 생기면 이 계획을 Action Spec으로 승격한다.
