---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "Outlook 메일을 Second Brain 자료로 쓰기"
description: "승인된 Outlook 메일을 안전하게 저장하고 Local Private 지식으로 정리한다."
tags: [second-brain, outlook, email, local-private]
timestamp: "{{timestamp}}"
boi_id: boi:private:{{employee_id}}:guide:outlook-to-case
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
guide_audience: "업무 메일을 Second Brain 자료로 쓰는 구성원"
guide_duration_minutes: 7
guide_prerequisites: "Windows Outlook과 Local 보관이 승인된 메일"
guide_execution: "메일과 필요한 첨부를 수동 저장하고 AI에게 Local Private 정리를 요청한다"
guide_success: "메일 원본과 attachment가 Local hash로 고정되고 자동 서버 연결은 발생하지 않는다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "28-safe-evidence-intake.md"
guide_boundary: "local-only"
source_refs:
  - type: url
    ref: https://support.microsoft.com/en-us/outlook/mail/save-an-outlook-message-as-a-eml-file-a-pdf-file-or-as-a-draft
    note: Outlook 메시지 저장 공식 도움말
---

# Outlook 메일을 Second Brain 자료로 쓰기

실제 사용자는 회사 보안 정책이 허용하는 범위에서 Outlook의 저장 기능을 사용합니다. 메일 자동 연결이나 전체 사서함 수집은 기본 동작이 아닙니다.

1. 메일이 Local 보관 가능한 자료인지 먼저 확인합니다.
2. Outlook의 다른 이름으로 저장으로 EML을 승인된 자료 폴더에 저장합니다.
3. 필요한 첨부파일만 별도로 저장합니다. 링크를 자동으로 따라가지 않습니다.
4. AI에게 해당 폴더를 Local Private로 정리해 달라고 요청합니다.
5. 결정·Action·근거·제약·확인 필요 항목과 기존 지식 반영 위치를 검토합니다.

~~~text
이 메일과 첨부를 원본 그대로 보존하고, 오래 쓸 결정·Action·근거·제약만
기존 Second Brain 지식과 비교해 반영해줘. 민감하거나 불확실한 내용은
확인 필요로 남기고 원격 업로드는 하지 마.
~~~

MCP나 Outlook connector는 필요하지 않습니다. 이 가이드는 메일 읽기·쓰기 권한을 요청하지 않으며 Local Private 파일을 자동 업로드하지 않습니다.

다음: [Outlook·웹·CSV·PDF·이미지 안전 수집](28-safe-evidence-intake.md)
