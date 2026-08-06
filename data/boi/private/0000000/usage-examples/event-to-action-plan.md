---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-example
title: 업무 흐름 계획 예제
description: 업무 이벤트가 발생했을 때 필요한 업무 BoI, SOP 또는 업무 흐름, 업무 요청, 수동 조치를 계획하는 요청
boi_id: boi:private:0000000:legacy:event-to-action-plan:5d084f5cf9
classification: internal
owner: "0000000"
artifact_visibility: working
lifecycle_state: working
memory_candidate: false
cleanup_policy: keep
timestamp: 2026-06-20T00:01:00+09:00
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
  - type: local-template
    ref: boi-event-workflow-planner
---

# Prompt

```text
이런 이벤트가 발생했을 때 BoI Wiki 기준으로 어떤 업무 BoI를 채워야 하고 어떤 업무 흐름과 업무 요청이 이어져야 하는지 계획해줘.
event_type 후보는 direct_development.result_check.requested.v1이고 payload는 아래와 같아.
```

# Expected Agent Behavior

1. `boi-event-workflow-planner` skill을 사용한다.
2. 기존 event type이 있으면 재사용하고, 없으면 versioned event type 후보를 만든다.
3. 필요한 업무 BoI, SOP stage 또는 업무 단계, 업무 요청, 수동 조치, generated BoI 후보를 정리한다.
4. 실제 action invoke는 하지 않는다.

# Citations

- Skill: `boi-event-workflow-planner`
