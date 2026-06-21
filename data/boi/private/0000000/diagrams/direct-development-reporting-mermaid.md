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

# Summary

직개발 결과 확인 및 Reporting SOP를 한 장짜리 복잡한 그림으로만 표현하지 않고, 빠른 이해용 Overview와 추적 가능한 Swimlane으로 나눈 Mermaid 초안이다. 긴 시스템명과 담당 방식은 node 안에 모두 넣지 않고 Source Mapping 표로 분리한다.

# Overview Mermaid

```mermaid
flowchart TD
  start["직개발 모니터링"] --> trend["Response Trend 확인"]
  trend --> map["Map View 확인"]
  map --> need_section{"단면검사 필요?"}
  need_section -- "yes" --> section["Wafer 대응 및 검사"]
  need_section -- "no" --> compare["연구소-양산 비교"]
  section --> compare
  compare --> report["결과 Reporting"]
  report --> share["협의체 공유"]
  share --> done["종료"]
```

# Swimlane Mermaid

```mermaid
flowchart TD
  subgraph events["Event"]
    evt_result["result_check.requested"]
    evt_map["map_view.requested"]
    evt_report["report.requested"]
    evt_share["share.requested"]
  end

  subgraph stages["SOP Stage"]
    stage_trend["Response Trend 확인"]
    stage_map["Map View 확인"]
    stage_section["단면검사 판단"]
    stage_report["Reporting"]
    stage_share["공유"]
  end

  subgraph actions["Action"]
    act_trend["quality_response_trend"]
    act_map["map_view_analysis"]
    act_report["report_draft"]
    act_share["messenger_share"]
  end

  subgraph manual["Manual Handoff"]
    manual_section{"단면검사 필요 여부"}
    manual_wafer{"Wafer 처리 방식"}
  end

  subgraph boi["Generated BoI"]
    boi_trace["workflow trace BoI"]
    boi_report["report draft BoI"]
  end

  evt_result --> stage_trend --> act_trend --> evt_map
  evt_map --> stage_map --> act_map --> manual_section
  manual_section -- "needed" --> stage_section --> manual_wafer --> boi_trace
  manual_section -- "not needed" --> evt_report
  manual_wafer -- "In-Line" --> evt_report
  manual_wafer -- "FAB-Out" --> evt_report
  evt_report --> stage_report --> act_report --> boi_report --> evt_share
  evt_share --> stage_share --> act_share
```

# Stage Detail Mermaid

```mermaid
flowchart TD
  map["Map View 확인"] --> decision{"단면검사 필요?"}
  decision -- "yes" --> wafer["Wafer 대응 검토"]
  wafer --> route{"Wafer 처리 방식"}
  route -- "In-Line" --> request_inline["의뢰서 작성 및 전달"]
  route -- "FAB-Out" --> request_fabout["단면검사 요청"]
  request_inline --> result["단면검사 결과 확인"]
  request_fabout --> result
  decision -- "no" --> compare["연구소-양산 비교"]
  result --> compare
```

# Source Mapping

| Node ID | Kind | Label | Source |
|---|---|---|---|
| `evt_result` | event | result_check.requested | SOP draft stage 1 |
| `stage_trend` | stage | Response Trend 확인 | SOP draft stage 1 |
| `stage_map` | stage | Map View 확인 | SOP draft stage 2 |
| `manual_section` | manual decision | 단면검사 필요 여부 | SOP draft stage 3 |
| `manual_wafer` | manual decision | Wafer 처리 방식 | SOP draft stage 4/6 |
| `act_report` | action | report_draft | SOP draft stage 8 |
| `act_share` | action | messenger_share | SOP draft stage 9 |

# Stage Notes

- stage 번호 5와 6은 원본 이미지의 배치 순서를 보존하되, 실행 흐름은 `단면검사 요청 -> 결과 확인`으로 해석한다.
- 품질 시스템, Map 분석 시스템, 단면 검사 시스템, 메신저는 candidate connector다.
- 사람이 판단해야 하는 node는 decision/manual node로 남긴다.

# Diagram QA

| Check | Status |
|---|---|
| Mermaid fenced block | pass |
| Overview node count <= 10 | pass |
| Swimlane separates Event, Stage, Action, Manual, BoI | pass |
| Decision edges have labels | pass |
| Source Mapping includes every important node kind | pass |
| No legacy non-numeric private path | pass |

# Citations

- [Direct development reporting SOP draft](../sop-drafts/direct-development-reporting-sop-draft.md)
