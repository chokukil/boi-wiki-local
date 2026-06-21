---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-example
title: "SOP Mermaid 프로세스 플로우 예제"
description: "SOP 초안을 Mermaid flowchart로 변환하는 자연어 요청 예제"
timestamp: 2026-06-20T21:53:00+09:00
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
  - type: generated-output
    ref: ../../diagrams/direct-development-reporting-mermaid.md
---

# Prompt

```text
직개발 결과 확인 SOP를 Mermaid 프로세스 플로우로 그려줘.
각 stage가 어떤 시스템, 사람, AI action으로 이어지는지 같이 보여줘.
```

# Generated Output

- 생성 문서: [direct-development-reporting-mermaid.md](../../diagrams/direct-development-reporting-mermaid.md)
- 포함 요소: 품질 시스템, Map 분석 시스템, 단면 검사 시스템, manual step, 메신저 공유, human approval decision.

# Evidence

- 입력 근거: [SOP 이미지 예제](image-to-sop-draft.md)의 `sop_sample_image.png`
- 산출 근거: SOP draft의 stage 표와 동일한 순서로 Mermaid node를 구성했다.

# How to Verify

1. Overview Mermaid가 10개 이하 node로 전체 흐름을 보여주는지 확인한다.
2. Swimlane Mermaid가 Event, SOP Stage, Action, Manual Handoff, Generated BoI lane을 분리하는지 확인한다.
3. Mermaid preview에서 decision node `단면검사 필요 여부`가 labeled edge로 표시되는지 확인한다.
4. 사람이 해야 하는 stage와 AI 자동화 stage가 Source Mapping에 남아 있는지 확인한다.
5. flow가 종료 node까지 닫히고 Diagram QA가 통과하는지 확인한다.

# Real vs Simulated

Mermaid 문서는 실제 local output이다. live runtime evidence는 direct-development trace `trace-f91b32904db0434db27c3f84307103ad`로 검증했다. 사내 시스템 호출은 실제 호출이 아니라 `SIMULATED` Langflow simulator action으로 표시한다.
