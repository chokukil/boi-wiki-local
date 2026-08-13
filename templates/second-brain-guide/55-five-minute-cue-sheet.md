---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "AI Research Second Brain 5분 방송 큐시트"
description: "구현된 공개 연구 Second Brain과 향후 조직 적용 방향을 분리해 설명하는 5분 순서"
tags: [SecondBrain, Broadcast, CueSheet]
timestamp: "{{timestamp}}"
boi_id: boi:private:{{employee_id}}:guide:broadcast-cue-sheet
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
guide_audience: "5분 방송 발표자"
guide_duration_minutes: 5
guide_prerequisites: "54-broadcast-hub.md"
guide_execution: "시간 순서에 따라 원문·답변·변경 후보·조직 방향을 구분해 설명한다"
guide_success: "실제 구현, 오프라인 방송 자산, 향후 조직 방향의 경계가 분명하다"
guide_failure_page: "54-broadcast-hub.md"
guide_next_page: "56-expected-qa.md"
guide_boundary: "public-research-description-only"
source_refs:
  - type: local-guide-source
    ref: templates/second-brain-guide/55-five-minute-cue-sheet.md
---

# AI Research Second Brain 5분 방송 큐시트

이 순서는 5분 안에 실제 공개 연구 시스템을 먼저 보여 주고, 내부 제조/SOP 방향은 마지막에 별도 미래 방향으로만 소개한다. Private 답변 본문, 개인 파일, 내부 영상은 화면이나 설명에 사용하지 않는다.

방송에서 41개 Local 지식 페이지는 **원문에서 확인한 33개와 여러 원문을 엮어 추론한 주제 8개**라고 설명한다. 충돌 없이 근거가 확인된 보강은 자동으로 반영한다. 사람 검토는 중요한 판단 변화, 충돌, 낮은 신뢰도, 근거가 부족한 추론, 민감 정보, 공유 범위 변경에서 필요하다. 같은 자료를 다시 넣으면 새 문서나 검토 항목을 만들지 않는다.

| 시간 | 화면·동작 | 말할 핵심 |
| --- | --- | --- |
| 0:00–0:35 | 이미지 1 | 개인 Local 지식은 먼저 Local에서 재사용하며, 공유는 가치 판단과 승인 뒤에만 후보가 된다. |
| 0:35–1:05 | 실제 코퍼스 허브와 33→41 Mermaid | 공개 연구 아티팩트 33개는 PDF 25개, 공개 텍스트 2개, GitHub 스냅샷 6개다. 원문 지식 33개와 주제 지식 8개가 자동 관리된다. |
| 1:05–2:00 | 실제 근거 있는 답변과 공개 원문 | 여섯 질문 예시 중 하나를 고르고, 답이 AI 요약만이 아니라 공개 원문 3~5개와 근거·한계를 함께 보인다고 설명한다. |
| 2:00–2:55 | 새 근거 비교 | 새 근거가 같은 판단을 보강하면 바로 Local에 반영되고, 결론에 실질적 변화를 주면 변경 후보가 된다. |
| 2:55–3:35 | 사람 검토 경계 | 모든 문서를 검토 대기열로 보내지 않는다. 사람 검토는 위의 완전한 경계에서만 필요하며, 일반적인 자동 보강은 승인 대기 상태가 아니다. |
| 3:35–4:25 | 이미지 2와 SOP/Event 흐름 | 이는 별도의 비식별 조직 적용 방향이다. Event마다 판단 질문·필요 근거·완료 조건을 제공하고, 수행 기록을 다음 업무에 연결한다. |
| 4:25–4:45 | 선택형 Canvas/Local Graph | Canvas·Bases·Local Graph은 Markdown을 탐색하는 선택형 화면일 뿐, 별도의 GraphRAG가 아니다. |
| 4:45–5:00 | 마무리 | 유관부서 PoC는 완료했고 Pilot 운영을 준비 중이며, 목표는 전사 확산이다. 실제 공개 연구 Vault와 내부 방향은 계속 분리한다. |

다음: [예상 Q&A](56-expected-qa.md)

이전: [방송 허브](54-broadcast-hub.md)
