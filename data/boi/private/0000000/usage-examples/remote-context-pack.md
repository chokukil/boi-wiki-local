---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-example
title: Remote Context Pack 예제
description: 원격 BoI Wiki MCP가 있을 때 shared SOP/WorkflowDefinition/Event/업무 요청을 검색해 context pack을 만드는 요청
timestamp: 2026-06-20T00:06:00+09:00
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
    ref: boi-context-pack-builder
---

# Prompt

```text
원격 BoI Wiki MCP가 연결되어 있으면 설비 이상 SOP, 관련 WorkflowDefinition, Event Types, 업무 요청 Specs를 찾아서 이번 업무용 context pack을 만들어줘. 원본 private 내용은 원격으로 보내지 마.
```

# Expected Agent Behavior

1. `boi-context-pack-builder` skill을 사용한다.
2. remote MCP가 있으면 `boi_search`, `boi_get`, `actions_search`, `workflow_status` 같은 조회 tool만 쓴다.
3. apply, invoke, promotion 계열 원격 쓰기 tool은 사용자 승인 없이 쓰지 않는다.

# Citations

- Skill: `boi-context-pack-builder`
