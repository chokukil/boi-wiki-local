---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-note
title: "직개발 Reporting SOP PoC 회의 정리"
description: "SOP 이미지 기반 BoI Wiki Local 활용 사례와 shared runtime evidence 자산화 회의 정리"
timestamp: 2026-06-20T22:01:00+09:00
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
  - type: local-example
    ref: ../usage-examples/natural-language-poc/meeting-to-boi.md
---

# Summary

직개발 결과 확인 및 Reporting SOP를 BoI Wiki Local에서 자연어 요청으로 만들고, shared BoI Wiki runtime의 Event/Action/Langflow evidence와 연결해 PoC 자산으로 남기기로 했다.

# Decisions

| 결정 | 내용 |
|---|---|
| 원본 이미지 보존 | `sop_sample_image.png`를 evidence로 저장한다. |
| Local 산출물 | SOP draft, Mermaid, Action draft, context pack, promotion draft를 모두 Local Private에 만든다. |
| Runtime evidence | shared BoI Wiki의 설비 이상 SOP smoke trace를 live evidence로 연결한다. |
| Approval boundary | Public/Team promotion과 high-risk action invoke는 preview/preflight까지만 자동화한다. |

# Action Items

| Owner | Action | Output |
|---|---|---|
| Agent | SOP 이미지 해석 | SOP draft |
| Agent | SOP를 Mermaid로 변환 | Mermaid diagram |
| Agent | Event to Action 분류 | event/action plan |
| Human | Public/Team 공유 승인 | approval decision |
| Agent + Runtime | smoke trace 확인 | Event/Action/Langflow evidence |

# Open Questions

- smartTAS, smartYES, smartAPS, CUBE API가 Action Gateway connector로 공개될 수 있는가?
- 단면검사 의뢰/결과 확인은 사람 승인 단계인지, system action으로 자동화 가능한지?
- Public 공유 시 원본 SOP 이미지 공개 가능 범위는 어디까지인가?
