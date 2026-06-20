---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-diagram
title: "직개발 결과 확인 및 Reporting Mermaid Flow"
description: "SOP 이미지 기반 직개발 결과 확인 workflow Mermaid 도식"
timestamp: 2026-06-20T22:03:00+09:00
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
---

# Mermaid

```mermaid
flowchart LR
  S["(1.8) 직개발 수행 및 모니터링"] --> A["1 Response Trend 확인<br/>smartTAS / AI 보조"]
  A --> B["2 Map View Image 확인<br/>smartYES / 사람+AI"]
  B --> D{"단면검사 필요 여부"}
  D -- "Y" --> C["3 단면검사 Wafer 대응 검토<br/>Manual / 사람"]
  C --> E{"Wafer 처리"}
  E -- "In-Line Wafer 필요" --> F["4 의뢰서 작성 및 Wafer 전달<br/>smartAPS / 사람"]
  E -- "FAB-Out" --> G["6 단면검사 요청<br/>Manual / 사람+AI"]
  F --> H["5 단면검사 결과 확인<br/>smartAPS / 사람"]
  G --> H
  D -- "N" --> I["7 연구소-양산FAB 비교 Trend 확인<br/>smartTAS / AI 보조"]
  H --> I
  I --> J["8 직개발 결과 Reporting<br/>Manual / AI 자동화"]
  J --> K["9 직개발 결과 협의체 공유<br/>CUBE / AI 자동화"]
  K --> Z["종료"]
```

# Notes

- stage 번호 5와 6은 원본 이미지의 배치 순서를 보존하되, 실행 흐름은 `단면검사 요청 -> 결과 확인`으로 해석한다.
- smartTAS, smartYES, smartAPS, CUBE는 candidate connector다.
- 사람이 판단해야 하는 node는 decision/manual node로 남긴다.
