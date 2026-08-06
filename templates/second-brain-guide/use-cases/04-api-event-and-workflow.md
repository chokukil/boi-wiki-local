---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "API·Event·Workflow 사례"
description: "API 자료와 반복 업무를 검토 가능한 Action, Event, SOP와 workflow simulation으로 만드는 방법"
tags: [LocalPrivate, API, Event, Action, Workflow, UseCase]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:use-case-api-workflow
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
guide_release: "3.0.0"
guide_audience: "API 연계와 반복 업무를 설계하는 구성원"
guide_duration_minutes: 15
guide_prerequisites: "비밀값이 제거된 API 또는 업무 단계 자료"
guide_execution: "입출력·오류·승인·예외를 정리하고 실행 없는 workflow simulation을 만든다"
guide_success: "재사용 가능한 계약과 사람이 확인할 지점이 분리됐다"
guide_failure_page: "../60-troubleshooting.md"
guide_next_page: "../53-organization-knowledge-loop.md"
guide_boundary: "promotion-preview-only"
source_refs:
  - type: local-guide-source
    ref: templates/second-brain-guide/use-cases/04-api-event-and-workflow.md
---

# API·Event·Workflow 사례

## 언제 쓰는가

API 문서가 요청 예시만 있고 업무 의미와 승인 조건이 없거나, 반복 업무가 사람마다 다른 순서로 수행될 때 사용합니다.

## 첫 요청문

```text
이 비밀값이 제거된 API 자료를 인증 방식의 종류, request/response schema,
오류, 멱등성, 승인 정책, 예시로 정리해 Action spec 초안을 만들어줘.
토큰은 만들거나 기록하지 말고 실제 호출도 하지 마.
```

반복 업무에는 다음처럼 요청합니다.

```text
이 반복 업무를 시작 Event, SOP 단계, 자동화 후보, 수동 판정,
실패·재시도·중단 조건으로 정리하고 합성 payload로 simulation해줘.
```

## 만들어지는 Local 파일

- `notes/capture-inbox/`: API 문서 또는 현행 업무 설명
- `action-drafts/`: connector kind와 request/response 계약
- `event-drafts/`: versioned Event Type 후보
- `sop-drafts/`: 사람이 이해하는 실행 단계와 예외
- `workflow-simulations/`: 합성 payload dry-run

## 원문과 정제본의 차이

API 원문은 엔드포인트 사실을 보존합니다. Action 초안은 업무 의도, 입력 계약, 오류 처리, approval과 idempotency를 추가하되 원문에 없는 동작을 실제 지원 기능처럼 확정하지 않습니다.

## 다시 찾고 연결하기

Event 이름, connector kind, 업무 용어로 검색합니다. Context Pack은 관련 SOP·Event·Action을 한 업무 질문에 맞춰 연결하지만 원본 계약을 복제하지 않습니다.

## 일간·주간 review 질문

- secret 예시나 실제 토큰이 남았는가?
- 같은 WorkflowDefinition 또는 Action을 재사용할 수 있는가?
- 실패·재시도·중단 조건이 있는가?
- 자동화 후보와 실제 지원 capability를 혼동했는가?

## 조직 공유 판단

입출력, 오류, 승인, owner와 검증 출처가 명확하면 Team Action/Event 후보로 만듭니다. 자격증명, 실제 endpoint 내부 주소, 테스트되지 않은 동작, 사용자 승인 없는 invoke 단계는 Local에 유지합니다.

## 정상 결과와 다음 여정

simulation은 실제 외부 호출 0건이고 각 단계의 근거와 human checkpoint를 보여야 합니다. 다음은 [개인 지식을 조직 지식으로 쌓는 법](../53-organization-knowledge-loop.md)입니다.
