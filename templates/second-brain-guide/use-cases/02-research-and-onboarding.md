---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "기술 조사와 온보딩 사례"
description: "여러 출처와 반복 질문을 비교 가능한 지식과 온보딩 Context Pack으로 만드는 방법"
tags: [LocalPrivate, Research, Onboarding, UseCase]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:use-case-research-onboarding
visibility: local-private
classification: internal
owner: "{{employee_id}}"
employee_id: "{{employee_id}}"
local_owner_ref: local-private:{{employee_id}}
local_only: true
promotion_status: local_only
retention_class: working
retention_until: ""
artifact_visibility: memory
lifecycle_state: memory
memory_candidate: false
cleanup_policy: keep
review_after: {{review_after}}
archive_status: active
contains_sensitive: false
guide_release: "3.1.0"
guide_audience: "기술 조사자와 인수인계 담당자"
guide_duration_minutes: 15
guide_prerequisites: "출처 URL 또는 Local 자료"
guide_execution: "출처별 사실과 비교 기준을 분리하고 반복 질문을 Context Pack으로 묶는다"
guide_success: "주장마다 출처가 있고 신규 사용자가 같은 질문을 반복하지 않아도 된다"
guide_failure_page: "../60-troubleshooting.md"
guide_next_page: "03-incident-quality-and-sop.md"
guide_boundary: "local-with-optional-mcp-read"
source_refs:
  - type: local-guide-source
    ref: templates/second-brain-guide/use-cases/02-research-and-onboarding.md
---

# 기술 조사와 온보딩 사례

## 언제 쓰는가

여러 문서를 매번 다시 읽어 비교하거나, 신규 구성원이 같은 용어·절차·담당 범위를 반복해서 질문할 때 사용합니다.

## 첫 요청문

```text
이 자료들을 출처별로 수집하고 질문, 사실, 대안, 비교 기준, 검증 결과,
추가 확인이 필요한 주장을 분리해줘. 답변에서 쓸 근거 경로를 남기고
충돌하는 주장은 하나로 합치지 말고 표시해줘.
```

온보딩에는 다음처럼 요청합니다.

```text
신규 구성원이 첫 주에 반복해서 묻는 질문을 용어, 관련 SOP, 확인 방법,
도움을 요청할 역할로 정리한 Local Context Pack을 만들어줘.
```

## 만들어지는 Local 파일

- `notes/capture-inbox/`: 출처별 원문 또는 관찰 기록
- `notes/knowledge/`: 출처 요약, 비교표, 현재 판단, 반증 조건
- `dictionary/`: 공유 가치가 있는 용어와 alias 후보
- `context-packs/`: 특정 조사 또는 온보딩용 연결 문서

## 원문과 정제본의 차이

출처 요약은 원문이 말한 내용을 보존하고, 종합 문서는 여러 출처가 함께 지지하거나 충돌하는 지점을 설명합니다. 최신 출처라는 이유만으로 기존 근거를 지우지 않고 superseded 또는 재검토 필요 상태를 남깁니다.

## 다시 찾고 연결하기

검색 중심 사용자는 AI에게 질문의 핵심어와 관련된 Local 문서를 근거 경로와 함께 찾아 달라고 요청합니다. 링크 중심 사용자는 조사 Context Pack을 hub로 삼아 출처 요약, Dictionary, 판단 문서로 이동합니다. 두 방식 모두 `index.md`와 실제 링크를 근거로 사용합니다.

## 일간·주간 review 질문

- 주장과 의견이 구분됐는가?
- 접근할 수 없는 출처에만 의존하는가?
- 새 출처가 기존 결론과 충돌하는가?
- 자주 반복되는 질문을 Dictionary나 Context Pack으로 승격할 가치가 있는가?

## 조직 공유 판단

다른 구성원이 독립적으로 확인할 수 있는 출처와 재사용 가능한 설명이 있으면 Team 가이드나 Dictionary 후보로 만듭니다. 개인 학습 메모, 출처 없는 요약, 라이선스가 불명확한 전문은 Local에 유지합니다.

## 정상 결과와 다음 여정

질문에서 관련 페이지와 출처까지 두세 단계 안에 도달하고 충돌 주장이 숨겨지지 않으면 정상입니다. 다음은 [장애·품질과 SOP](03-incident-quality-and-sop.md)입니다.
