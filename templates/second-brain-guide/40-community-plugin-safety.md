---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "Obsidian 확장 기능 보안"
description: "Local Private Vault에서 커뮤니티 플러그인과 브라우저 확장을 안전하게 검토하는 기준"
tags: [LocalPrivate, SecondBrain, Guide, Obsidian, Security]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:plugin-safety
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
guide_audience: "Obsidian 확장 기능을 검토하는 사용자"
guide_duration_minutes: 7
guide_prerequisites: "Obsidian Core 기능 확인"
guide_execution: "권한, 네트워크, 저장 위치, 복구 방법을 검토한다"
guide_success: "설치 여부와 중단·복구 기준이 문서화됐다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "41-quickadd.md"
guide_boundary: "optional-obsidian-local"
source_refs:
  - type: official-doc
    ref: https://help.obsidian.md/community-plugins
  - type: official-doc
    ref: https://obsidian.md/help/plugin-security
---

# Obsidian 확장 기능 보안

Obsidian Core만으로 Properties, Search, Backlinks, Graph, Bases, Canvas를 사용할 수 있습니다. 커뮤니티 플러그인과 브라우저 확장은 필수가 아니며, 사용자가 기능별로 직접 검토하고 승인할 때만 설치합니다.

## 기본 정책

- 기본 경로: Obsidian Core만 사용
- 선택 후보: 입력을 빠르게 여는 QuickAdd, 웹 페이지를 Local Markdown으로 저장하는 공식 Web Clipper
- 보류: Omnisearch는 Core Search의 실제 부족이 검증될 때까지 설치하지 않음
- 배포 제외: 별도 provider·schema·wikilink를 만드는 LLM Wiki 플러그인, 자동 Git 동기화, 외부 AI 연결

Web Clipper는 Obsidian 커뮤니티 플러그인이 아니라 브라우저 확장입니다. 설치 위치와 권한이 다르므로 QuickAdd와 별도 승인·복구 단위로 취급합니다.

## 설치 전 확인

1. 먼저 Core 기능으로 동일한 업무를 완료할 수 있는지 확인합니다.
2. 공식 배포 위치, 제작자, 최근 release와 지원 버전을 확인합니다.
3. Vault 파일 읽기·쓰기, 네트워크, 시스템 명령 등 권한 범위를 확인합니다.
4. 설치 목적과 성공 기준, Disable·제거 후 fallback을 적습니다.
5. 설치·Enable 직전에 사용자가 직접 승인합니다.

## 실패 시 복구

문제가 있는 확장 하나만 Disable하고, Markdown과 evidence 원본은 삭제하지 않습니다. Core Search 또는 AI에게 `이 키워드와 관련된 Local 문서를 근거와 함께 찾아줘`라고 요청해 업무가 계속되는지 확인한 뒤 해당 확장만 제거합니다. `.obsidian/plugins/` 전체를 삭제하거나 Vault를 새로 만들지 않습니다.

이전: [Obsidian Core 기능 설정](31-obsidian-core-settings.md) · 다음: [QuickAdd](41-quickadd.md)
