---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "BoI Wiki Local 제품 계층 지도"
description: "Meta Harness Core, Second Brain, Case Candidate, 관리자 검증 자산을 구분하는 안내"
tags: [LocalPrivate, MetaHarness, SecondBrain, ReferenceCase, Architecture]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:meta-harness-map
visibility: local-private
classification: internal
owner: "{{employee_id}}"
employee_id: "{{employee_id}}"
local_owner_ref: local-private:{{employee_id}}
local_only: true
promotion_status: local_only
retention_class: working
retention_until: ""
archive_status: active
artifact_visibility: memory
lifecycle_state: memory
memory_candidate: false
cleanup_policy: keep
review_after: {{review_after}}
contains_sensitive: false
guide_release: "3.2.0"
guide_audience: "전체 구성원"
guide_duration_minutes: 4
guide_prerequisites: "00-start-here.md"
guide_execution: "네 계층 중 현재 필요한 계층과 다음 요청을 고른다"
guide_success: "Core, Flagship, Case, Admin 자산을 서로 혼동하지 않는다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "02-build-your-harness.md"
guide_boundary: "local-only"
source_refs:
  - type: local-guide-source
    ref: templates/second-brain-guide/01-meta-harness-map.md
---

# BoI Wiki Local 제품 계층 지도

BoI Wiki Local의 중심은 평가 도구나 사례 모음이 아니라 **업무를 좋은 BoI 지식 생산 Harness로 바꾸는 Meta Harness Core**입니다.

```text
A. Meta Harness Core
   boi-harness-builder + 기존 BoI Skills + OKF·BoI·promotion 계약
                    │
                    ├── B. Flagship Capability
                    │      boi-second-brain
                    │
                    └── C. Flagship Case Candidate
                           범용 Second Brain (community)

D. Admin·CI Evaluation
   위 세 계층을 검증하지만 일반 사용자 흐름에는 나타나지 않음
```

## A. Meta Harness Core

사용자의 업무와 성공 조건을 분석하고 기존 Skill을 조합해 역할, dependency DAG, 산출물 계약, reviewer, Local/Remote 경계, promotion 흐름을 구성합니다. `boi-harness-builder`가 여기에 해당합니다.

Core는 `Audit → Frame → Capture·Distill·Query·Lint·Review 설계 → 역할·DAG → Local/Remote 계약 → Validate → Evolve`를 반복합니다. 실제 실패는 Case, orchestration, 범용 Skill, validator, runtime 중 소유 계층을 먼저 판정하고 가장 작은 계층에 환류합니다.

## B. Flagship Capability

`boi-second-brain`은 대화·메일·웹·문서·자료 폴더에서 오래 쓸 지식을 축적하고 기존 지식을 보강·교정·검토하는 횡단 Harness입니다. 매우 중요한 기능이지만 Meta Harness 자체나 모든 업무 Case를 대체하지 않습니다.

## C. Flagship Case Candidate

Case는 Meta Harness로 만든 결과를 실제 입력, 역할, DAG, 산출물, 오류 처리, walkthrough로 보여 주는 재사용 사례입니다. 현재 범용 Second Brain은 `community` 후보이며, 양 runtime 반복·비개발자 Acceptance·실제 BoI Wiki validator를 통과하기 전에는 Reference가 아닙니다.

- [범용 Second Brain 활용 사례 허브](25-use-case-playbook.md)

도메인 사례는 실제 담당자가 업무 방법론과 검토 책임을 가지고 구성해야 합니다. 검증되지 않은 합성 도메인 사례를 제품 대표로 배포하지 않습니다.

## D. Admin·CI Evaluation

Python evaluator, fixture builder, deterministic oracle, blind comparison, benchmark importer와 release evidence는 제품 품질을 검증하는 관리자 자산입니다. 일반 사용자는 이를 설치하거나 실행할 필요가 없습니다. 검증 수치가 Core의 제품 구조를 결정하거나 사용자 Wiki의 첫 화면을 차지해서는 안 됩니다.

## 변하지 않는 호환 경계

- Local Profile: OKF 0.1 + BoI Profile 0.1-local + `local-private`
- canonical 후보: OKF 0.1 + BoI Profile 0.1 + `team` 또는 `public`
- MCP 조회만으로 Local Private 자동 업로드 없음
- 민감정보·출처·범위 검증과 exact preview 후 사용자 승인
- 실제 대상 BoI Wiki validator가 없으면 호환 완료를 주장하지 않음

다음: [내 업무용 BoI Harness 만들기](02-build-your-harness.md)
