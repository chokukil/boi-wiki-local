---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-langflow-plan
title: "직개발 Reporting Langflow Harness Plan"
description: "직개발 Reporting stage를 Langflow harness로 연결하기 위한 설계 초안"
timestamp: 2026-06-20T22:09:00+09:00
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
  - type: event-plan
    ref: ../event-drafts/direct-development-reporting-event-to-action-plan.md
---

# Flow Candidate

| Node | Role |
|---|---|
| Event Input | 직개발 result check payload 수신 |
| BoI Wiki Reader | SOP draft, action plan, source refs 조회 |
| Prompt Composer | trend/map/cross-section evidence를 reporting prompt로 구성 |
| LLM | 결과 reporting 초안 작성 |
| Policy Guard | 공개 가능 범위와 source refs 확인 |
| BoI Writer | Local 또는 Private BoI 결과 저장 |
| Action Invoker | 메신저 공유는 approval_required 전까지 preview만 생성 |

# Live Reference

`BoI Universal Action Simulator Flow`는 shared runtime trace `trace-c8649f71e3e44b5b8b6a8f70963af446`에서 `langflow_invoked`로 검증됐다. 직개발 reporting flow는 이 official simulator harness를 사용하며, 품질 시스템/Map 분석 시스템/단면 검사 시스템/메신저 connector가 실제로 연결되기 전까지 모든 결과를 `SIMULATED`, `real_system_connected=false`, "실제 시스템 호출 아님"으로 남긴다.
