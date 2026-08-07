---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "첫 설정과 확인"
description: "사번, Harness, Local Private 구조를 확인하는 첫 설정 절차"
tags: [LocalPrivate, SecondBrain, Guide, Setup]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:first-setup
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
guide_audience: "설치를 마친 사용자"
guide_duration_minutes: 5
guide_prerequisites: "설치 완료, 7자리 사번"
guide_execution: "Harness와 Local Profile을 검증하고 선택 기능 경로를 고른다"
guide_success: "Harness와 Local Profile 계약을 확인하고 다음 사용 경로를 선택했다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "20-first-10-minutes.md"
guide_boundary: "local-only"
source_refs:
  - type: local-guide-source
    ref: templates/second-brain-guide/11-first-setup.md
---

# 첫 설정과 확인

## 1. 현재 사용자 확인

AI에게 `내 Local Profile 식별자와 개인 폴더가 올바르게 연결됐는지 확인해줘`라고 요청합니다. 개인 콘텐츠를 `0000000` 아래에 만들면 안 됩니다. 실제 Profile이 둘 이상이면 AI가 임의로 선택하지 않고 어떤 Profile을 사용할지 묻습니다.

## 2. Harness 확인

```text
고정된 BoI Harness가 정상인지 확인해줘. 문제가 없다면 release와 checksum은
기술 로그에만 남기고, 내가 알아야 할 결과만 쉽게 알려줘.
```

오프라인 스냅샷을 사용했다는 메시지는 오류가 아닙니다. 고정된 release, checksum, signature가 모두 유효해야 합니다.

## 3. Local Private 프로필 확인

```text
내 Local Private 문서가 OKF 0.1과 BoI Profile 0.1-local 규칙을 지키는지 확인해줘.
고칠 내용이 있으면 파일을 바꾸기 전에 쉬운 말로 미리 보여줘.
```

정상 문서는 `boi_profile_version: 0.1-local`, `visibility: local-private`, `local_only: true`를 가집니다. 일반 사용자는 Python이나 터미널 명령을 입력하지 않습니다.

## 4. 연결 모드 선택

처음에는 MCP와 Obsidian을 모두 사용하지 않는 구성이 기본입니다. 이후 필요한 기능만 추가합니다.

- 로컬 파일만 사용: 바로 [10분 튜토리얼](20-first-10-minutes.md)로 이동
- Obsidian 추가: [Obsidian 설치와 Vault 연결](30-obsidian-install-and-vault.md)
- 사내 BoI Wiki 참조: [MCP와 Team·Public 공유](50-mcp-and-promotion.md)

이전: [저장소 설치](10-install-repository.md) · 다음: [10분 튜토리얼](20-first-10-minutes.md)
