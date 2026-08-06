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
guide_release: "3.0.0"
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
  - type: plugin-manifest
    ref: https://raw.githubusercontent.com/chhoumann/quickadd/master/manifest.json
---

# QuickAdd 설치와 BoI Capture 설정

QuickAdd는 수집 입력을 빠르게 시작하는 선택형 플러그인입니다. 설치하지 않아도 AI에게 자연어로 수집을 요청할 수 있습니다.

## 설치

조사 기준일 2026-08-01의 최신 QuickAdd 2.20.0은 Obsidian 1.13.0 이상을 요구합니다. 현재 Windows runtime 1.13.4에서는 2.20.0, 이전 1.12.7 환경에서는 공식 `versions.json`상 2.12.3이 호환 후보입니다. 실행 파일 속성보다 `%APPDATA%\obsidian\obsidian-<version>.asar`의 실제 업데이트 runtime을 기준으로 판정합니다. Community Plugins 화면이 선택한 버전을 확인하고, 사내 정책이 구버전 플러그인을 허용하지 않거나 호환 버전이 제공되지 않으면 설치하지 않습니다.

1. Settings → Community plugins → Browse를 엽니다.
2. `QuickAdd`와 제작자 정보를 확인합니다.
3. 표시된 요구 Obsidian 버전과 현재 앱 버전이 맞는지 확인합니다. 확실하지 않으면 AI 또는 배포 관리자에게 호환성 확인을 요청합니다.
4. 설치 직전 사용자가 승인하고 Install 후 Enable을 선택합니다.

## 최소 설정

1. QuickAdd 설정에서 새 Choice를 만듭니다.
2. 이름은 `BoI Capture`로 지정합니다.
3. 외부 API, JavaScript 매크로, 시스템 명령 실행은 추가하지 않습니다.
4. 입력은 우선 `inbox.md` 또는 로컬 캡처 명령으로 전달합니다.

QuickAdd만으로 임의 YAML을 직접 생성하면 필수 프로필이나 원문 해시가 빠질 수 있습니다. 실제 불변 캡처 문서는 AI가 BoI Skill과 템플릿을 사용해 만들도록 합니다. QuickAdd는 입력 시작점으로만 사용합니다.

## 검증

- 캡처 후 파일이 `notes/capture-inbox/`에 있는지 확인합니다.
- `source_immutability: locked`와 `source_sha256`이 있는지 확인합니다.
- AI에게 `방금 만든 캡처가 OKF 0.1과 BoI Profile 0.1-local 규칙을 지키는지 확인해줘`라고 요청합니다.

## 복구

QuickAdd가 원치 않는 파일을 만들거나 오류를 내면 즉시 Disable하고 `BoI Capture` Choice를 제거한 뒤 플러그인을 제거합니다. 생성된 Markdown은 자동 삭제하지 말고 원문 해시와 profile을 먼저 검사합니다. 이후에도 AI에게 같은 수집 흐름을 자연어로 요청할 수 있습니다.

이전: [플러그인 보안](40-community-plugin-safety.md) · 다음: [Web Clipper](43-web-clipper.md)
