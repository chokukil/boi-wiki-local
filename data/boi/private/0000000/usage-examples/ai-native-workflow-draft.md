---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-example
title: AI Native Workflow Draft 예제
description: 업무 요청을 SOP, Event, Action 중심의 AI Native Workflow 초안으로 바꾸는 요청
boi_id: boi:private:0000000:legacy:ai-native-workflow-draft:0029acedb0
classification: internal
owner: "0000000"
artifact_visibility: working
lifecycle_state: working
memory_candidate: false
cleanup_policy: keep
timestamp: 2026-06-20T00:04:00+09:00
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
    ref: boi-workflow-simulator
---

# Prompt

```text
이 업무 요청을 AI Native Workflow 초안으로 만들어줘. 어떤 이벤트가 시작점이고, 어떤 SOP 단계와 Action, 사람이 확인할 지점이 필요한지 정리해줘.
```

# Expected Agent Behavior

1. `boi-event-workflow-planner`와 `boi-workflow-simulator` 관점으로 정리한다.
2. 실제 실행이 아니라 초안/시뮬레이션임을 명시한다.
3. `data/boi/private/0000000/workflow-simulations/`에 저장한다.

# Citations

- Skill: `boi-workflow-simulator`
