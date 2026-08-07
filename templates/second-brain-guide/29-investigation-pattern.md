---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "범용 Investigation Pattern"
description: "여러 출처를 case, evidence, hypothesis, decision으로 정리하는 범용 Second Brain 패턴"
tags: [LocalPrivate, SecondBrain, Investigation, Guide]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:investigation-pattern
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
guide_release: "3.1.0"
guide_audience: "조사·장애·품질·감사·기술 검토를 수행하는 구성원"
guide_duration_minutes: 8
guide_prerequisites: "첫 설정 완료; 정리할 자료가 하나 이상 있음"
guide_execution: "case를 만들고 evidence, hypothesis, decision을 표준 링크와 Properties로 연결한다"
guide_success: "원본을 바꾸지 않고 지지·반증·미확인 근거가 구분된 Case Hub를 만들었다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "28-safe-evidence-intake.md"
guide_boundary: "local-only"
source_refs:
  - type: local-guide-source
    ref: templates/second-brain-guide/29-investigation-pattern.md
---

# 범용 Investigation Pattern

회의 조사, 장애 분석, 품질 검토, 기술 비교처럼 여러 자료를 함께 판단해야 할 때 사용합니다. 이것은 새로운 분석 제품이나 도메인 Skill이 아니라 `boi-second-brain`의 범용 문서 패턴입니다.

## 구성

| 역할 | Local type | 기록하는 것 |
|---|---|---|
| Case Hub | `boi/local-analysis-case` | 질문, 범위, 현재 판단, 다음 검토 |
| Evidence | `boi/local-evidence` | 불변 원본 경로, SHA256, 출처, 민감도 |
| Hypothesis | `boi/local-hypothesis` | 지지·반증 evidence ID, 상태, 검토일 |
| Analysis log | `boi/local-analysis-log` | 관찰과 판단이 바뀐 시간 순서 |
| Knowledge | `boi/local-knowledge` | 검토된 재사용 지식과 공유 후보 |

`Graph`나 `Canvas`의 선은 시각화일 뿐 provenance가 아닙니다. 관계의 원본은 `source_refs`, `supports`, `contradicts`, `generated_from`과 표준 Markdown 링크입니다.

가설의 상태와 지지·반증을 검토하는 방법은 [가설·근거·미확인 항목 검토](33-hypothesis-evidence-review.md)를 참고합니다.

## 에이전트에게 전달할 요청문

```text
이 폴더의 자료를 Local Private Second Brain으로 정리해줘.
원본 파일은 수정하지 말고 SHA256이 있는 원본 정보 문서를 만들어줘.
먼저 case, evidence, hypothesis, decision에 반영될 내용을 미리 보여주고 승인할 변경 확인값을 알려줘.
지지 근거와 반증, 미확인 항목을 구분하고 승인 전에는 적용하거나 공유하지 마.
```

## 자료 유형

신규 자료는 `email`, `web-clip`, `tabular-data`, `document`, `image`, `meeting-note`, `analysis-export` 같은 범용 유형으로 기록합니다. 이미지나 표의 업무 의미는 태그와 사람이 검토한 파생 문서에서 설명합니다.

## 정상 결과와 경계

원본 hash가 그대로이고 모든 evidence가 Case Hub 또는 명시적 보류 상태에 연결되면 정상입니다. evidence·hypothesis·analysis log는 직접 promotion할 수 없습니다. 검토한 `knowledge`, `context pack`, `SOP`로 정제한 뒤에만 promotion preview를 만듭니다.

이전: [Second Brain 활용 사례](25-use-case-playbook.md) · 다음: [Outlook·웹·CSV·PDF·이미지 안전 수집](28-safe-evidence-intake.md)
