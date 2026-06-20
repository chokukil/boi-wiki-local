---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-example
title: SOP Mermaid Flow 예제
description: SOP를 Mermaid 기반 프로세스 플로우로 그리는 대표 요청
timestamp: 2026-06-20T00:00:00+09:00
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
    ref: boi-sop-flow-visualizer
---

# Prompt

```text
설비 이상 대응 SOP를 BoI Wiki 형식으로 읽고, 각 단계가 보이도록 Mermaid 프로세스 플로우로 그려줘. MCP가 연결되어 있으면 원격 BoI Wiki에서 SOP와 Action을 찾아서 반영하고, 없으면 내가 제공한 SOP 텍스트만으로 local 초안을 만들어줘.
```

# Expected Agent Behavior

1. `boi-sop-flow-visualizer` skill을 사용한다.
2. SOP stage, event type, automated action, manual handoff를 추출한다.
3. `data/boi/private/0000000/diagrams/`에 Mermaid 문서를 저장한다.
4. 공유는 사용자가 별도 승인하기 전까지 하지 않는다.

# Output Example

```mermaid
flowchart TD
  A["Event: equipment.alarm.raised.v1"] --> B["Stage: 이상 감지"]
  B --> C["Action: Trend / Raw Data 확인"]
  C --> D["Event: root_cause.analysis.requested.v1"]
  D --> E["Stage: 원인 분석"]
  E --> F["Manual: 원인 후보 검토"]
```

# Citations

- Skill: `boi-sop-flow-visualizer`
