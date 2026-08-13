---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "AI Research Second Brain 예상 Q&A"
description: "실제 Local 답변 여섯 개를 공개 안전한 질문 수준에서 소개하는 방송 보조 자료"
tags: [SecondBrain, Broadcast, QA, Research]
timestamp: "{{timestamp}}"
boi_id: boi:private:{{employee_id}}:guide:broadcast-qa
visibility: local-private
classification: internal
owner: "{{employee_id}}"
employee_id: "{{employee_id}}"
local_owner_ref: local-private:{{employee_id}}
local_only: true
promotion_status: local_only
retention_class: reference
retention_until: ""
archive_status: active
artifact_visibility: reference
lifecycle_state: protected
memory_candidate: false
cleanup_policy: keep
review_after: "{{review_after}}"
contains_sensitive: false
guide_release: "3.2.0"
guide_audience: "방송 진행자와 질의응답 담당자"
guide_duration_minutes: 4
guide_prerequisites: "54-broadcast-hub.md"
guide_execution: "질문 유형과 답변 원칙을 소개하되 Local 답변 본문은 공개하지 않는다"
guide_success: "원문 중심 답변·한계·검토 경계를 짧게 설명한다"
guide_failure_page: "54-broadcast-hub.md"
guide_next_page: "57-broadcaster-reply.md"
guide_boundary: "public-research-description-only"
source_refs:
  - type: local-guide-source
    ref: templates/second-brain-guide/56-expected-qa.md
---

# AI Research Second Brain 예상 Q&A

아래 여섯 질문은 실제 Local에서 검증한 답변의 **질문 범위**를 공개 안전하게 소개한 것이다. 답변 본문이나 개인 경로는 이 문서에 싣지 않는다. 시연에서는 질문 하나를 선택해 공개 원문 3~5개, 그 원문이 뒷받침하는 주장, 남는 한계를 함께 보여 준다.

41개 Local 지식 페이지는 **원문에서 확인한 33개와 여러 원문을 엮어 추론한 주제 8개**다. 충돌 없이 근거가 확인된 보강은 자동으로 반영한다. 사람 검토는 중요한 판단 변화, 충돌, 낮은 신뢰도, 근거가 부족한 추론, 민감 정보, 공유 범위 변경에서 필요하다. 같은 자료를 다시 넣으면 새 문서나 검토 항목을 만들지 않는다.

| 질문 예시 | 짧은 답변 원칙 |
| --- | --- |
| AI 연구 Second Brain은 무엇을 실제로 하나요? | 33개 공개 연구 아티팩트를 원문과 연결해, 질문에 맞는 근거 중심 답변으로 재사용한다. |
| RAG와 Wiki는 어떻게 함께 쓰이나요? | 검색은 후보를 찾는 데 쓰고, 답변은 선택한 공개 원문과 지식 구조를 다시 확인해 만든다. |
| Graph·온톨로지는 꼭 필요한가요? | 아니다. Markdown과 원문 연결이 기본이며, Canvas·Bases·Local Graph은 선택형 탐색 화면이다. |
| 새 연구가 기존 판단과 다르면 어떻게 하나요? | 차이가 중요한 판단을 바꾸면 변경 후보로 올리고, 근거가 부족한 추론은 사람 검토로 보낸다. 그 전에는 자동 보강 또는 한계 표시로 다룬다. |
| 규모가 커져도 품질을 어떻게 보나요? | 검색 적합성, 원문과 주장 연결, 사람이 읽는 답변 품질을 서로 분리해 확인한다. |
| 사람 승인은 언제 필요한가요? | 중요한 판단 변화, 충돌, 낮은 신뢰도, 근거가 부족한 추론, 민감 정보, Team/Public 공유 범위 변경에서 필요하다. |

방송에서는 AI가 만든 요약을 원문처럼 인용하지 않는다. 공개 원문은 읽기 쉬운 제목과 번호로 표시하고, 한계가 있으면 함께 말한다. 이 원칙은 실제 구현된 공개 연구 시스템에 적용되며, 조직 SOP/Event 방향은 별도 내부 적용 과제로 구분한다.

다음: [방송자 회신](57-broadcaster-reply.md)
