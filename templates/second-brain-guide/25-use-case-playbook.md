---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "BoI Wiki Local 활용 사례"
description: "범용 Harness를 회의, 조사, 장애, 온보딩, API 업무에 적용하고 Second Brain으로 확장하는 사례 지도"
tags: [LocalPrivate, MetaHarness, UseCase, SecondBrain, Guide]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:use-cases
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
guide_audience: "업무 사례를 찾는 전 구성원"
guide_duration_minutes: 5
guide_prerequisites: "기본 Local lifecycle 이해"
guide_execution: "현재 업무와 가까운 사례를 골라 capture부터 promotion preview까지 따라 한다"
guide_success: "한 업무 원문이 재사용 가능한 Local 지식과 안전한 조직 공유 후보로 이어졌다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "27-research-backed-second-brain.md"
guide_boundary: "local-only"
source_refs:
  - type: local-guide-source
    ref: templates/second-brain-guide/25-use-case-playbook.md
---

# BoI Wiki Local 활용 사례

이 페이지는 Meta Harness가 만들 수 있는 결과의 예시 지도이지, 제품 기능 목록이나 검증된 Reference 목록이 아닙니다. 먼저 자신의 업무를 자연어로 설명해 [내 업무용 BoI Harness](02-build-your-harness.md)를 구성하고, 아래 walkthrough는 역할·산출물·검토 지점을 정할 때 참고합니다. 모든 예시는 합성 데이터이며 실제 제품, 고객, 설비 식별자를 포함하지 않습니다. Second Brain을 연결하지 않아도 업무 Harness를 실행할 수 있고, 연결하면 장기 축적·검색·재사용이 확장됩니다.

저장소의 `cases/catalog.json`에 현재 공개 후보로 등록된 사례는 `community` 상태의 범용 Second Brain 하나뿐입니다. 아래 업무 예시는 사용법을 설명하는 비공식 walkthrough이며 실제 실행·담당자 검토·BoI Wiki contract evidence 없이 Verified 또는 Reference로 표시하지 않습니다.

```text
내가 하는 업무와 성공 조건, 사용하는 자료, 반드시 사람이 판단할 지점을 설명할게.
기존 BoI Skills를 먼저 확인하고 역할, 작업 순서, 산출물, 검토 기준,
Local/Remote 경계를 가진 재사용 가능한 Harness로 구성해줘.
```

사례에 관계없이 여러 자료의 근거·가설·결정을 계속 관리해야 한다면 [범용 Investigation Pattern](29-investigation-pattern.md)을 선택적으로 사용합니다.

## 비공식 walkthrough에서 가까운 흐름 찾기

| 현재 업무 | 따라 할 문서 | Local 결과 | 조직 공유 후보 |
|---|---|---|---|
| 회의 결정과 주간 성과가 흩어짐 | [회의와 주간보고](use-cases/01-meeting-and-weekly-report.md) | 결정 기록, 근거, 리스크 | Team 결정 기록, 주간보고 |
| 조사 결과와 인수인계 질문이 반복됨 | [기술 조사와 온보딩](use-cases/02-research-and-onboarding.md) | 비교표, FAQ, Context Pack | 기술 가이드, Dictionary, 온보딩 문서 |
| 장애·품질 이상 대응이 사람 기억에 의존함 | [장애·품질과 SOP](use-cases/03-incident-quality-and-sop.md) | 타임라인, 가설, 검증 결과 | 재발 방지 SOP, Event/Action 후보 |
| API와 반복 업무를 실행 계약으로 바꾸고 싶음 | [API·Event·Workflow](use-cases/04-api-event-and-workflow.md) | Action spec, 예외, human checkpoint | Action/Event specification, SOP |

## 공통 성공 기준

1. capture 원문의 잠긴 구간과 SHA256은 바뀌지 않습니다.
2. 정제 문서는 결정, 근거, 미해결 사항, 후속 작업을 원문과 분리합니다.
3. 검색 결과는 실제 Local 경로를 근거로 반환합니다.
4. 개인 맥락과 불확실한 주장은 Local에 남깁니다.
5. Team/Public 후보는 reviewer, 구조화 출처, scope, exact hash를 확인하고도 submit하지 않습니다.

## 사례를 내 업무에 맞추는 법

예시의 시스템명이나 용어를 그대로 복사하지 말고, 자신의 업무 입력·판단·출력·검증 지점으로 바꿉니다. 문서 종류를 고르기 어렵다면 먼저 Local 지식 문서로 정제한 뒤 review에서 SOP, Dictionary, Event, Action, Context Pack 중 재사용 가치가 있는 형태를 고릅니다.

이전: [Capture에서 지식까지](23-capture-distill-review.md) · 다음: [조사 기반 Second Brain 원칙](27-research-backed-second-brain.md)

## 자료가 여러 형식으로 들어올 때

- [Outlook 메일을 안전하게 보관하기](36-outlook-to-case.md)
- [Outlook·웹·CSV·PDF·이미지 안전 수집](28-safe-evidence-intake.md)
- [근거·가설·결정을 관리하는 범용 Investigation Pattern](29-investigation-pattern.md)
