---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "일간·주간 Inbox Review"
description: "Second Brain을 신뢰할 수 있게 유지하는 짧은 운영 습관"
tags: [LocalPrivate, Inbox, Review, Lifecycle]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:review-rhythm
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
guide_audience: "지식을 꾸준히 관리하는 사용자"
guide_duration_minutes: 10
guide_prerequisites: "capture와 distill 경험"
guide_execution: "일간 inbox와 주간 lifecycle review를 수행한다"
guide_success: "미분류·검토기한·archive 후보가 정리됐다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "25-use-case-playbook.md"
guide_boundary: "local-only"
source_refs:
  - type: local-guide-source
    ref: templates/second-brain-guide/24-daily-weekly-review.md
---

# 일간·주간 Inbox Review

대상은 모든 사용자입니다. 일간 5분, 주간 20분이 필요하며 capture가 하나 이상 있어야 합니다.

## 일간 단계

1. 오늘 capture를 열고 민감정보 표시가 맞는지 확인합니다.
2. 다시 쓸 내용은 distill하고, 일회성 메모는 그대로 보존하거나 archive 후보로 표시합니다.
3. 후속 작업의 담당·기한을 확인합니다.

## 주간 단계

1. AI에게 `이번 주 Second Brain에서 오래된 문서, 끊어진 출처, 검토 기한과 공유 후보를 확인해줘. 바꾸기 전에는 미리 보여줘`라고 요청합니다.
2. 오래된 inbox, 끊어진 출처, review 기한, promotion 후보를 확인합니다.
3. 조직에 반복 가치가 있는 지식만 Team/Public 후보로 보냅니다.

지난 승인 이후 달라진 내용만 조사하고 revision을 관리하려면 [지식 변화 운영과 사용자 프롬프트](38-knowledge-change-operations.md)의 정기 업데이트 요청문을 사용합니다.

## 정상 결과, 실패, 다음 여정

미분류 inbox 수와 overdue review가 설명 가능한 상태면 정상입니다. hash·link 오류는 [문제 해결](60-troubleshooting.md)로 이동합니다. Review는 Local 파일만 읽으며 자동 업로드하지 않습니다. 다음: [활용 사례](25-use-case-playbook.md)
