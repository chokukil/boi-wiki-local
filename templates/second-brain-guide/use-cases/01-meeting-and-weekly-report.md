---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "회의 결정과 주간보고 사례"
description: "회의 원문과 주간 활동을 근거 있는 결정 기록과 Team 보고 후보로 만드는 방법"
tags: [LocalPrivate, Meeting, WeeklyReport, UseCase]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:use-case-meeting-report
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
guide_audience: "회의와 정기 보고를 수행하는 구성원"
guide_duration_minutes: 12
guide_prerequisites: "첫 capture와 distill 완료"
guide_execution: "회의 또는 주간 활동을 capture하고 결정·근거·리스크로 정제한 뒤 공유 가치를 검토한다"
guide_success: "원문과 정제본이 분리되고 Team 후보에서 개인 맥락이 제거됐다"
guide_failure_page: "../60-troubleshooting.md"
guide_next_page: "02-research-and-onboarding.md"
guide_boundary: "promotion-preview-only"
source_refs:
  - type: local-guide-source
    ref: templates/second-brain-guide/use-cases/01-meeting-and-weekly-report.md
---

# 회의 결정과 주간보고 사례

## 언제 쓰는가

같은 결정이 다시 논의되거나, 주간보고를 작성할 때 근거를 여러 대화와 파일에서 다시 찾는 경우에 사용합니다.

## 첫 요청문

```text
이 합성 회의 메모를 수정하지 않는 원문으로 수집해줘. 결정, 결정 근거,
미해결 질문, 담당 역할, 다음 확인 시점을 별도 지식 문서로 정제해줘.
원문은 고치지 말고 아직 공유하지 마.
```

주간보고에는 다음처럼 요청합니다.

```text
이번 주 Local 문서에서 완료 결과, 확인 가능한 근거, 남은 리스크,
다음 주 우선순위를 정리해줘. 추정은 사실처럼 쓰지 말고 근거 경로를 붙여줘.
```

## 만들어지는 Local 파일

- `notes/capture-inbox/`: 회의 또는 주간 활동 원문, `source_immutability: locked`
- `notes/knowledge/`: 결정·근거·미해결·후속 작업 정제본
- `reports/`: 주간 성과와 리스크 초안
- `promotion-drafts/`: Team 결정 기록 또는 주간보고 미리보기

## 원문과 정제본의 차이

원문에는 발언 순서와 불완전한 문장이 남을 수 있습니다. 정제본은 누가 말했는지가 아니라 무엇이 결정됐고 어떤 근거가 있으며 무엇을 다시 확인해야 하는지를 기록합니다. 근거 없는 합의나 개인 평가는 Local에 남깁니다.

## 다시 찾고 연결하기

Obsidian에서는 프로젝트 또는 결정 문서의 Backlinks로 관련 회의와 후속 보고를 찾습니다. Obsidian이 없으면 AI에게 `결정 키워드와 관련된 Local 문서를 근거 경로와 함께 찾아줘`라고 요청합니다. 같은 결정이 반복되면 새 폴더보다 관련 문서를 연결하는 작은 hub 또는 Context Pack을 만듭니다.

## 일간·주간 review 질문

- 오늘 기록 중 결정과 단순 논의를 구분했는가?
- 다음 확인 시점이 지났는데 근거가 갱신되지 않은 문서가 있는가?
- 이번 주 결과가 활동량이 아니라 검증 가능한 변화로 표현됐는가?
- 다른 구성원이 반복해서 물을 내용인가?

## 조직 공유 판단

반복 사용 가치와 접근 가능한 출처가 있으면 Team 후보로 만듭니다. 개인 평가, 참석자별 발언, 미확인 추정, 로컬 경로는 제거합니다. reviewer와 exact hash가 없는 후보는 Local에 유지합니다.

## 정상 결과와 다음 여정

결정 기록에서 capture 원문으로 역추적할 수 있고, promotion preview가 `user_confirmed: false`, `remote_submit_allowed: false`이면 정상입니다. 실패하면 [문제 해결](../60-troubleshooting.md)을 보고, 다음으로 [기술 조사와 온보딩](02-research-and-onboarding.md)을 봅니다.
