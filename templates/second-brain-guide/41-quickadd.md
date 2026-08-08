---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "QuickAdd 설치와 BoI Capture 설정"
description: "Obsidian에서 Local Private 수집을 빠르게 시작하는 최소 QuickAdd 설정"
tags: [LocalPrivate, SecondBrain, Guide, Obsidian, QuickAdd]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:quickadd
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
guide_audience: "반복 capture를 단축하려는 사용자"
guide_duration_minutes: 10
guide_prerequisites: "사내 허용 정책, 호환성 검사, 사용자 설치 승인"
guide_execution: "호환 버전을 확인하고 승인된 경우에만 최소 설정한다"
guide_success: "QuickAdd 없이도 fallback이 있고 자동 설치가 없다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "43-web-clipper.md"
guide_boundary: "optional-obsidian-local"
source_refs:
  - type: source-repository
    ref: https://github.com/chhoumann/quickadd
  - type: official-version-list
    ref: https://raw.githubusercontent.com/chhoumann/quickadd/master/versions.json
  - type: official-release
    ref: https://github.com/chhoumann/quickadd/releases/tag/2.21.0
---

# QuickAdd 설치와 BoI Capture 설정

QuickAdd는 수집 입력을 빠르게 시작하는 선택형 플러그인입니다. 설치하지 않아도 AI에게 자연어로 수집을 요청할 수 있습니다.

## 설치

조사 기준일 2026-08-08의 QuickAdd 2.21.0은 공식 플러그인 정보와 버전 목록에서 Obsidian 1.13.0 이상을 요구합니다. 공식 2.21.0 release의 배포 파일은 다음 SHA256으로 고정했습니다.

| 파일 | 크기 | SHA256 |
|---|---:|---|
| 실행 파일 | 1,309,273 bytes | `8636198aef29cd64b53def1bf921baef5ddf83070c8a77c5457c9276617a81ad` |
| 플러그인 정보 파일 | 372 bytes | `0ba9b423bb47ee29de20854f9006c4806f775085d7b9b582e09f8cd4baced231` |
| 스타일 파일 | 33,270 bytes | `729d8362fc6c518633c12caae1c7bb5051a9ebe9aaf62cfe39fb895002fe04b7` |

실제 설치 전에 대상 sanitized 데모 Vault, 버전, 위 세 파일의 URL·크기·SHA256, 변경될 `.obsidian/plugins/quickadd/` 파일과 복구 방법을 하나의 변경 미리보기로 확인합니다. 후보 내용이나 대상 Vault가 바뀌면 새 미리보기가 필요합니다. 사내 정책이 플러그인을 허용하지 않거나 호환 버전·hash를 확인할 수 없으면 설치하지 않습니다.

```text
QuickAdd 설치 preview를 보여줘.
개인 Vault가 아니라 sanitized Golden Journey 데모 Vault만 대상으로 하고,
버전·배포 파일 SHA256·변경 파일·복구 방법을 먼저 보여줘.
```

이 요청은 설치를 수행하지 않습니다. 현재 release 후보는 정확한 preview까지만 제공하며 실제 설치는 별도 사용자 승인이 필요합니다.

1. Settings → Community plugins → Browse를 엽니다.
2. `QuickAdd`와 제작자 정보를 확인합니다.
3. 표시된 요구 Obsidian 버전과 현재 앱 버전이 맞는지 확인합니다. 확실하지 않으면 AI 또는 배포 관리자에게 호환성 확인을 요청합니다.
4. 정확한 변경 미리보기를 승인한 뒤에만 Install 후 Enable을 선택합니다.

## 최소 설정

1. QuickAdd 설정에서 새 Choice를 만듭니다.
2. 이름은 `BoI Capture`로 지정합니다.
3. 외부 API, JavaScript 매크로, 시스템 명령 실행은 추가하지 않습니다.
4. 입력 대상은 Second Brain 설정에서 이미 승인한 공통 원본 자료 폴더로 지정합니다. 전용 QuickAdd 폴더나 Web Clipper 폴더를 만들지 않습니다.

QuickAdd만으로 지식 후보나 임의 YAML을 직접 생성하면 필수 프로필이나 원문 해시가 빠질 수 있습니다. QuickAdd는 공통 원본 폴더에 입력을 남기는 시작점으로만 사용하고, SHA256 판정과 OKF + BoI 후보·review queue 생성은 다음 AI 작업에서 수행합니다.

## 검증

- 캡처 후 파일이 승인한 공통 원본 자료 폴더에 있고 원본 bytes가 바뀌지 않았는지 확인합니다.
- AI에게 `방금 원본 자료 폴더에 넣은 새 자료만 처리해줘. 같은 SHA256은 건너뛰고 원문과 지식 후보를 분리해줘`라고 요청합니다.
- 후보가 review queue에 있고 승인 전 현재 지식 revision이 바뀌지 않았는지 확인합니다.

## 복구

QuickAdd가 원치 않는 파일을 만들거나 오류를 내면 즉시 Disable하고 `BoI Capture` Choice를 제거한 뒤 플러그인을 제거합니다. 생성된 Markdown은 자동 삭제하지 말고 원문 해시와 profile을 먼저 검사합니다. 이후에도 AI에게 같은 수집 흐름을 자연어로 요청할 수 있습니다.

이전: [플러그인 보안](40-community-plugin-safety.md) · 다음: [Web Clipper](43-web-clipper.md)
