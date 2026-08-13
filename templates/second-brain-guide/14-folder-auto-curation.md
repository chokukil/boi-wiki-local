---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "자료 폴더에 파일 넣고 정리하기"
description: "이메일·웹·표·PDF·이미지를 지정 폴더에 모아 다음 AI 세션에서 안전하게 정리하는 방법"
tags: [LocalPrivate, SecondBrain, Guide, Inbox]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:folder-auto-curation
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
guide_audience: "여러 자료를 한 번에 정리하려는 구성원"
guide_duration_minutes: 8
guide_prerequisites: "초기 설정에서 자료 폴더를 지정함"
guide_execution: "자료 폴더에 파일을 복사하고 다음 AI 세션에서 결과 요약 확인"
guide_success: "원본이 보존되고 중복·보강·신규·확인 필요·남은 자료가 묶음으로 보고됨"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "15-memory-review-and-correction.md"
guide_boundary: "local-only"
source_refs:
  - type: local-guide-source
    ref: templates/second-brain-guide/14-folder-auto-curation.md
---

# 자료 폴더에 파일 넣고 정리하기

기본 폴더는 `%USERPROFILE%\Documents\BoI-Second-Brain-Inbox`입니다. 이 하나의 공통 원본 폴더에 Outlook에서 저장한 `.eml`, Web Clipper Markdown, 일반 Markdown·텍스트, CSV, PDF, 이미지와 지원 문서를 함께 넣습니다. `web-clips/` 같은 전용 하위 폴더는 필요하지 않습니다.

## 동작 시점

상주 프로그램은 없습니다. AI를 실행하지 않은 동안에는 아무 작업도 하지 않습니다. `알아서 정리`와 `정리 전 확인`에서는 새 Codex 또는 Claude 작업의 첫 AI 응답에서 새 파일과 바뀐 파일을 한 번 확인합니다. 같은 작업에서는 사용자가 다시 요청하지 않는 한 반복 검사하지 않습니다. `요청할 때만`에서는 세션 시작 때 경로나 목록도 열지 않으며, 사용자가 `자료 폴더를 정리해줘`라고 요청한 뒤에만 확인합니다.

## AI가 하는 일

1. 경로·크기·수정 시각으로 후보를 좁히고 SHA256을 확인해 같은 원본을 중복 처리하지 않습니다. 경로나 자료 유형이 달라도 같은 SHA256이면 한 번만 처리합니다.
2. 임시 파일, 저장 중인 파일, 지원하지 않는 형식은 건너뜁니다.
3. 원본은 이동·수정·삭제하지 않고 Local Private 사본과 정확한 출처·SHA256을 보존합니다.
4. 읽을 수 있는 이메일·웹·Markdown·텍스트·표 자료는 같은 작업에서 주장·결정·제약·근거·반대 근거·unknown·검토 상태와 Local/Remote 경계가 있는 재사용 가능한 OKF 0.1 + BoI Profile 0.1-local 후보 하나로 정리합니다.
5. PDF·이미지도 승인 후 AI가 실제 페이지나 화면 영역을 열어 확인할 수 있으면 같은 방식으로 정리합니다. 확인한 페이지·영역과 읽기 어려운 부분을 함께 남기며, 보이지 않은 내용을 추측하거나 OCR을 몰래 사용하지 않습니다.
6. 현재 AI가 신뢰성 있게 읽을 수 없는 파일, 지원하지 않는 형식, 불완전하게 보이는 자료, 격리가 필요한 자료만 출처 정보와 검토 필요 상태로 보류합니다. 내용을 읽었다고 주장하지 않습니다. 기존 승인 지식과 비교한 결과는 신규·강화·수정·충돌·stale·폐기 검토·unknown으로 나눕니다.
7. 자료가 많으면 주제별 묶음으로 처리하고 다음 세션에 이어갑니다.

파일 개수는 고정 처리 한도가 아닙니다. 자료 수, 형식, 중복, 연결 정도에 따라 AI가 안전한 묶음 크기를 정합니다.

## 처음 정리할 때 한 번 확인

처음에는 파일을 만들지 않고 대상 파일 수, 중복, 정리 묶음, 기존 지식과의 관계, 원본 보존과 원격 업로드 꺼짐을 미리 보여줍니다. 범위가 맞으면 “이 미리보기의 자료와 범위대로 정리해줘”라고 한 번 승인합니다. 이후에는 파일마다 승인을 반복하지 않습니다.

세션이 끝나 일부만 처리됐으면 “승인했던 자료 폴더 정리를 중단된 지점부터 이어서 해줘”라고 말합니다. AI는 승인한 계획과 현재 파일을 다시 대조합니다. 그대로면 다음 묶음부터 이어가고, 파일이나 범위가 달라졌으면 쓰기 전에 새 미리보기를 보여줍니다. 이미 반영한 파일은 다시 만들지 않습니다.

## 결과 예시

```text
자료 폴더 정리 결과

- 기존 지식 보강: 12개
- 새로운 주제 생성: 3개
- 이미 반영됨: 28개
- 내용 확인 필요: 2개
- 아직 처리 중: 47개
```

`알아서 정리`에서는 파일마다 승인을 묻지 않습니다. 해시가 확인된 출처 지식과 충돌 없는 주제 종합은 **Local 자동 관리 지식**으로 바로 검색하고 질문에 활용할 수 있습니다. `observed`와 `inferred`는 지식이 만들어진 방식을 뜻하며, 문서별 승인 대기 상태가 아닙니다.

review queue에는 충돌, 낮은 신뢰, 근거가 부족한 추론, 민감정보, 공유 범위 변경, 또는 승인된 기준 결론을 바꾸는 **중요한 판단 변화**만 남깁니다. Current는 모든 문서에 붙는 상태가 아니라 질문이나 판단별로 승인한 기준선입니다. 변경 후보는 사용자 승인 전에 그 기준선을 덮어쓰지 않습니다. 신규 unique hash가 없으면 `no-change`로 끝내고 보고서·문서·index·log·revision을 만들거나 바꾸지 않습니다.

## 바로 쓸 수 있는 요청

```text
방금 원본 자료 폴더에 넣은 새 자료만 처리해줘.
이전에 같은 SHA256으로 처리한 자료는 건너뛰고,
원문과 지식 후보를 분리해줘.
```

```text
방금 저장한 웹 클립만 처리해줘.
같은 SHA256으로 이미 반영된 자료는 건너뛰고 원문은 변경하지 마.
```

```text
지난 세션 이후 추가된 원본과 처리 대기·실패·검토 항목을
자료 유형별로 보여줘.
```

`웹 클립만` 또는 `새 PDF만`처럼 범위를 제한하면 선택하지 않은 신규 자료는 완료 처리하지 않고 다음 작업을 위해 남겨 둡니다.

웹 주소를 직접 크롤링하거나 Outlook 서버에 자동 접속하지 않습니다. 사용자가 저장한 로컬 자료만 다룹니다. 자세한 형식별 주의점은 [안전한 evidence 수집](28-safe-evidence-intake.md)을 참고합니다.

다음: [생성·갱신·보류 결과 검토하기](15-memory-review-and-correction.md)

## 공개 사례와 연결하기

공통 원본 폴더에서 만든 후보는 [Obsidian Golden Journey](32-obsidian-golden-journey.md)의 change set·review queue와 같은 방식으로 기존 승인 지식과 비교합니다. 같은 SHA256은 중복 후보를 만들지 않고, 선택하지 않은 신규 유형은 다음 처리 대상으로 남깁니다.
