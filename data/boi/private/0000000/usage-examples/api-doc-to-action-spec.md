---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-example
title: API Doc to 업무 요청 Spec 예제
description: 기존 시스템 API 문서를 업무 요청 초안으로 만들고 업무 흐름에 연결하는 요청
timestamp: 2026-06-20T00:02:00+09:00
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
    ref: boi-action-author
---

# Prompt

```text
이 API 문서를 BoI Wiki 업무 요청 초안으로 만들고 기존 업무 흐름에 연결해줘. 실제 토큰이나 비밀값은 넣지 말고, request/response schema, curl 예시, approval policy, WorkflowDefinition 중복 확인, catalog patch draft까지 만들어줘.
```

# Expected Agent Behavior

1. `boi-action-author` skill을 사용한다.
2. connector kind를 `api`, `webhook`, `mcp`, `langflow`, `manual`, `event_broker` 중 하나로 분류한다.
3. `workflow_definitions_search` 또는 local 자료로 기존 업무 흐름 재사용 가능성을 확인한다.
4. `data/boi/private/0000000/action-drafts/`에 초안을 저장한다.
5. Team/Public 공유는 promotion draft와 사용자 승인 이후에만 진행한다.

# Citations

- Skill: `boi-action-author`
