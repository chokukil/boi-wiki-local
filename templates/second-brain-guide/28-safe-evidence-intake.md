---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "Outlook·웹·CSV·PDF·이미지 안전 수집"
description: "업무 자료의 원본 bytes를 바꾸지 않고 Local Private 지식으로 정리한다."
tags: [second-brain, evidence, intake, local-private]
timestamp: "{{timestamp}}"
boi_id: boi:private:{{employee_id}}:guide:safe-evidence-intake
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
guide_release: "3.1.0"
guide_audience: "여러 형식의 업무 자료를 Local Second Brain에 넣는 구성원"
guide_duration_minutes: 8
guide_prerequisites: "Windows 설치 완료와 승인된 Local 자료"
guide_execution: "AI에게 자료 폴더 정리를 요청하고 원본 보존·중복·지식 반영 결과를 확인한다"
guide_success: "원본 SHA256이 유지되고 읽을 수 있는 자료가 재사용 가능한 지식으로 정리된다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "29-investigation-pattern.md"
guide_boundary: "local-only"
source_refs:
  - type: local-guide-source
    ref: templates/second-brain-guide/28-safe-evidence-intake.md
---

# Outlook·웹·CSV·PDF·이미지 안전 수집

AI는 메일 서버나 웹사이트를 임의로 순회하지 않습니다. 사용자가 승인한 폴더의 이메일·웹 Markdown·CSV·PDF·이미지·회의 메모만 확인하고 원본 SHA256을 기록합니다.

## AI에게 전달할 요청

~~~text
이 폴더의 이메일, 웹 저장 문서, CSV, PDF, 이미지를 내 Second Brain에 정리해줘.
먼저 원본 hash, 중복, 기존 지식과의 관계, Local Private 유지 범위를 보여주고
승인한 자료만 기존 지식 보강·교정·신규·확인 필요로 나눠 반영해줘.
~~~

웹 자료는 공개 URL과 함께 Markdown 또는 PDF로 저장하고, Outlook 메일은 회사 정책이 허용할 때만 EML로 저장합니다. 자동 다운로드, 사서함 전체 연결, 링크 자동 방문은 기본 동작이 아닙니다.

## 미리보기에서 확인할 것

- 원본 경로·크기·SHA256과 동일 hash 중복
- 글·표처럼 바로 읽을 수 있는 자료와, 승인 후 실제 화면 확인이 필요한 PDF·이미지
- 보강할 기존 지식과 새로 만들 주제
- 충돌·민감정보·출처 불명으로 보류할 자료
- Local Private 유지와 원격 자동 업로드 꺼짐

승인 전에는 Profile 문서를 만들거나 고치지 않습니다. 승인 후에도 원본 파일은 이동·수정·삭제하지 않습니다.

승인 후 PDF·이미지를 실제로 열어 확인할 수 있으면, 확인한 페이지·화면 영역과 읽기 어려운 부분을 기록하고 같은 작업 안에서 재사용 지식으로 정리합니다. 현재 AI가 신뢰성 있게 볼 수 없는 파일, 불완전하게 보이는 자료, 격리가 필요한 자료만 출처 정보 문서로 보류합니다. 보이지 않은 문장·도표·결론은 추측하지 않으며 OCR은 기본 동작이 아닙니다.

## 정상 결과

- 원본 bytes와 SHA256이 보존됩니다.
- 같은 hash를 다시 넣으면 이미 반영됨으로 처리됩니다.
- 읽을 수 있는 자료는 hash 등록 문서로 끝내지 않고 주장·결정·제약·불확실성·검토 상태가 있는 재사용 지식으로 정리됩니다.
- 구조화된 source_refs와 generated_from이 표준 Markdown 링크와 함께 남습니다.
- OCR, 자동 다운로드, MCP write, 원격 submit은 일어나지 않습니다.

다음: [범용 Investigation Pattern](29-investigation-pattern.md)
