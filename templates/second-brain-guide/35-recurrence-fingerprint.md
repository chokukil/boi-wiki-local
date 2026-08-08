---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "재발 패턴과 주간 review"
description: "반복 업무에서 재사용할 신호 조합, 제외 조건, 검토 상태를 정제한다."
tags: [second-brain, recurrence, pattern, review]
timestamp: "{{timestamp}}"
boi_id: boi:private:{{employee_id}}:guide:recurrence-pattern
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
memory_candidate: true
cleanup_policy: keep
review_after: "{{review_after}}"
contains_sensitive: false
guide_release: "3.2.0"
guide_audience: "반복되는 문제와 업무 신호를 재사용 지식으로 남기는 구성원"
guide_duration_minutes: 6
guide_prerequisites: "사람의 검토가 끝난 지식 또는 조사 기록"
guide_execution: "재검색 단서·제외 조건·검증 상태를 일반 knowledge로 정리한다"
guide_success: "다음 유사 업무에서 검색할 질문과 과잉 일반화를 막는 조건이 함께 남는다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "24-daily-weekly-review.md"
guide_boundary: "promotion-preview-only"
source_refs:
  - type: local-guide-source
    ref: templates/second-brain-guide/35-recurrence-fingerprint.md
---

# 재발 패턴과 주간 review

반복되는 장애, 문의, 검토 이슈, 의사결정을 다음 업무에서 다시 찾기 위한 지식입니다.

- 다시 검색할 신호와 질문
- 함께 비교해야 할 맥락
- 과거에 오탐이었던 제외 조건
- 어떤 출처로 검증했는지
- 아직 검증하지 않은 범위
- review 날짜와 책임자

재발 패턴은 자동 판정 규칙이 아닙니다. 새 상황을 빠르게 시작하기 위한 질문과 검색 단서이며, 조직 공유 시 개인 경로·식별자·Local 원문을 제거합니다.

공유할 가치가 있으면 일반 knowledge로 정제해 reviewer·Team ID·구조화된 공개 가능 출처를 갖춘 promotion preview를 만듭니다. Local 조사 기록이나 agent-memory를 직접 promotion하지 않습니다.

다음: [일간·주간 review](24-daily-weekly-review.md)
