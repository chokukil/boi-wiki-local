---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "장애·품질 이상과 SOP 사례"
description: "합성 장애와 품질 이상 기록을 재발 방지 지식과 검토 가능한 SOP 후보로 만드는 방법"
tags: [LocalPrivate, Incident, Quality, SOP, UseCase]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:use-case-incident-quality
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
guide_audience: "장애 대응, 설비, 품질 업무 구성원"
guide_duration_minutes: 15
guide_prerequisites: "비민감 합성 또는 승인된 Local 원문"
guide_execution: "관찰·타임라인·가설·검증·조치를 분리하고 재발 방지 SOP 후보를 만든다"
guide_success: "사실과 가설이 구분되고 human checkpoint가 있는 SOP 초안이 만들어졌다"
guide_failure_page: "../60-troubleshooting.md"
guide_next_page: "04-api-event-and-workflow.md"
guide_boundary: "promotion-preview-only"
source_refs:
  - type: local-guide-source
    ref: templates/second-brain-guide/use-cases/03-incident-quality-and-sop.md
---

# 장애·품질 이상과 SOP 사례

## 언제 쓰는가

장애나 품질 이상이 해결된 뒤 원인과 검증 과정이 개인 기억에만 남거나, 비슷한 상황에서 같은 확인을 반복할 때 사용합니다.

## 첫 요청문

```text
이 합성 장애 기록을 수정하지 않는 원문으로 수집하고 관찰 사실, 타임라인,
가설, 가설별 검증, 수행 조치, 결과, 미확인 위험으로 정제해줘.
원인으로 확정되지 않은 내용은 후보로 표시해줘.
```

합성 품질 이상에는 다음처럼 요청합니다.

```text
설비 A의 합성 응답 추세 이상 사례를 Event 후보, 확인 단계, 자동화 가능한 Action,
사람이 판정해야 하는 지점으로 나눠 SOP 초안을 만들어줘. 실제 실행은 하지 마.
```

## 만들어지는 Local 파일

- `notes/capture-inbox/`: 시각별 관찰과 원본 로그 설명
- `notes/knowledge/`: 사실·가설·검증 결과·재발 조건
- `sop-drafts/`: 재현, 진단, 완화, 복구, 사후 검증 단계
- `event-drafts/`, `action-drafts/`: 확정되지 않은 Event/Action 후보
- `workflow-simulations/`: 실제 실행 없는 dry-run

## 원문과 정제본의 차이

원문은 당시 관찰 순서를 보존합니다. 정제본은 사후에 알게 된 사실을 당시 사실처럼 섞지 않고 가설이 언제 어떤 근거로 기각되거나 채택됐는지 표시합니다.

## 다시 찾고 연결하기

증상, Event 후보, Dictionary 용어로 검색합니다. Obsidian Graph는 관련 문서를 찾는 보조 수단일 뿐 원인 관계를 자동 증명하지 않습니다. SOP 단계와 근거는 `source_refs`와 Source Mapping으로 확인합니다.

## 일간·주간 review 질문

- 관찰 사실과 원인 가설이 섞였는가?
- 완화 조치와 영구 조치가 구분됐는가?
- 자동 Action 전에 승인 또는 중단 조건이 있는가?
- 새 사례가 기존 SOP의 오래된 주장을 무효화하는가?

## 조직 공유 판단

재현 가능하고 reviewer가 안전성을 확인할 수 있으면 Team SOP 후보로 만듭니다. 실제 설비·제품·고객 식별자, 접근 제한 로그, 미확인 원인, 임시 우회는 제거하거나 Local에 유지합니다. Public 후보는 별도의 공개 가능한 출처와 표현이 없으면 만들지 않습니다.

## 정상 결과와 다음 여정

SOP 초안에 입력, 단계, 예외, 중단 조건, human checkpoint, 검증 결과가 있고 실제 Action을 호출하지 않았으면 정상입니다. 다음은 [API·Event·Workflow](04-api-event-and-workflow.md)입니다.
