---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "내 사용 경로 선택"
description: "설치, Obsidian, MCP, 공유 목적에 맞는 시작 경로"
tags: [LocalPrivate, SecondBrain, Guide, Journey]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:choose-path
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
guide_release: "3.2.0"
guide_audience: "처음 사용자와 기존 사용자"
guide_duration_minutes: 3
guide_prerequisites: "가이드 홈 확인"
guide_execution: "Obsidian과 MCP 사용 여부 및 역할에 맞는 경로를 선택한다"
guide_success: "자신에게 필요한 최소 구성과 다음 문서를 정했다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "10-install-repository.md"
guide_boundary: "local-only"
source_refs:
  - type: local-guide-source
    ref: templates/second-brain-guide/05-choose-your-path.md
---

# 내 사용 경로 선택

대상은 모든 신규 사용자이며, 약 2분이 걸립니다. 선행 조건은 없습니다.

## 선택

| 질문 | 선택 | 다음 문서 |
|---|---|---|
| 처음 설치합니까? | 예 | [Windows·Git 저장소 설치](10-install-repository.md) |
| 설치가 끝났습니까? | 예 | [첫 설정](11-first-setup.md) |
| Obsidian 없이 씁니까? | 예 | [Obsidian 없는 사용법](26-no-obsidian.md) |
| Obsidian도 씁니까? | 예 | [Obsidian 설치](30-obsidian-install-and-vault.md) |
| MCP가 있습니까? | 없음/조회/승격 | [모드별 기능](52-mode-matrix.md) |
| 조직에 공유합니까? | Team/Public | [Promotion Package](51-promotion-package.md) |
| 가이드나 코드를 개선합니까? | 예 | [PR 기여](71-contributing-via-pr.md) |

## 정상 결과와 실패 시 이동

자신에게 필요한 다음 문서 하나를 선택했다면 정상입니다. 선택이 어렵다면 Obsidian과 MCP가 모두 없는 기본 경로로 시작해도 됩니다. 설치 문제는 [문제 해결](60-troubleshooting.md)로 이동합니다.

## Local/Remote 경계와 다음 여정

경로 선택은 기능을 켜거나 원격 작업을 만들지 않습니다. 기본 상태는 항상 Local Private입니다. 다음: [Windows·Git 저장소 설치](10-install-repository.md)
