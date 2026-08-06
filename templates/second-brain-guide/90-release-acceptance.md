---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "사내 배포 전 사용자 Acceptance"
description: "비개발자 Windows 여정과 선택형 Obsidian 지원을 실제 사용자 환경에서 확인하는 마지막 게이트"
tags: [Release, Acceptance, Windows, Obsidian]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:release-acceptance
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
guide_audience: "배포 관리자, knowledge steward, 비개발자 pilot"
guide_duration_minutes: 30
guide_prerequisites: "승인된 GitHub 또는 사내 Bitbucket 저장소와 Windows test PC"
guide_execution: "Wiki-only 사용자 여정과 선택형 Obsidian을 파일럿 마법사로 비식별 검증한다"
guide_success: "commit 일치 evidence가 통과하고 지원 범위가 분리 표시된다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "00-start-here.md"
guide_boundary: "release-validation-only"
source_refs:
  - type: local-guide-source
    ref: templates/second-brain-guide/90-release-acceptance.md
---

# 사내 배포 전 사용자 Acceptance

대상은 배포 관리자, knowledge steward, 비개발자 pilot 사용자입니다. 약 30분이 필요하며 외부에서는 승인된 GitHub 저장소, 사내에서는 origin만 바꾼 Bitbucket mirror와 Windows test PC를 사용합니다. 실제 사번이나 업무 원문 대신 합성 자료를 사용합니다.

## 비개발자 두 명의 여정

1. 비개발자 A는 Codex에 [한 문장 설정 요청](12-ai-assisted-setup.md)을 전달하고 Obsidian 없이 대화 기억, 자료 폴더 정리, 검색, Team preview를 완료합니다.
2. 비개발자 B는 Claude에 같은 요청을 전달하고 Obsidian Core로 같은 합성 여정을 수행한 뒤 Properties, Backlinks, Graph를 확인합니다.
3. 두 사람 모두 Python과 터미널 명령을 직접 입력하지 않고, 질문은 최대 세 개이며, 승인 전 개인 Profile 변경이 없어야 합니다.
4. 이름·사번·화면 녹화 대신 걸린 시간과 막힌 단계만 비식별 evidence에 남깁니다.
5. `이 기억은 틀렸어` 요청으로 이력을 보존한 교정을 완료하고, 자동 기능을 자연어 한 문장으로 끄거나 변경합니다.

각 사용자는 설치, 첫 지식 생성, promotion preview 시간을 따로 잽니다. 목표는 각각 10분, 10분, 5분이며 초과해도 결과를 숨기지 않습니다. 마법사의 UX 관찰에는 자유서술 대신 아래 고정 ID만 입력합니다.

- 단계 ID: `ai-setup`, `preset`, `folder-curation`, `memory-correction`, `install`, `first-capture`, `distill`, `search`, `promotion-preview`, `vault-open`, `properties`, `backlinks`, `graph`, `bases`, `canvas`
- 캡처 ID: `screen-01`부터 `screen-15`, `screen-28`부터 `screen-34`
- 예: 막힌 단계 `graph`, 잘못 클릭한 단계 `vault-open`, 도움 된 화면 `screen-10`

## 3.0.0 상태 분리

다음 상태는 독립적으로 기록합니다.

- `agent_driven_setup_ready`: Harness·Skill 기준의 자연어 설정 경로가 자동 검증됨
- `zero_ui_setup_ready`: 실제 Codex·Claude에서 외부 창 없이 설정한 사용자 evidence가 있음
- `adaptive_memory_ready`: 중복·보강·교정·확인 필요 동작을 실제 사용자 여정으로 검증함
- `agent_auto_check_ready`: 자동 확인을 선택한 Profile에서만 다음 AI 세션에 자료 폴더 변경을 이어서 확인하고, `explicit-only`에서는 요청 전 접근하지 않음
- `folder_autocuration_ready`: 대량 자료의 중복 제거와 중단 재개를 검증함

실제 사용자 evidence가 없는 네 상태를 자동 테스트만으로 참으로 만들지 않습니다. 이 상태들과 기존 Bitbucket·BoI Wiki contract가 모두 충족되기 전에는 `full_release_ready: false`입니다.

## Obsidian 지원을 표시할 때

Obsidian은 최종 사용자에게 선택 사항입니다. 그러나 2.3 배포판이 선택 경로까지 안전하게 안내하는지 확인하기 위해 release acceptance에는 Obsidian Core 사용자 1명이 필요합니다. 다음 항목은 그 사용자의 evidence에서 확인합니다.

1. Windows-native Local Private 폴더를 Vault로 엽니다.
2. 외부 편집기로 합성 Markdown을 만들고 재시작 없이 나타나는지 확인합니다.
3. Properties, Backlinks, Graph가 실제 파일을 표시하는지 확인합니다.
4. 플러그인은 [호환성 검사](41-quickadd.md)를 통과하고 사용자가 설치를 승인한 경우에만 별도로 확인합니다.

## 증거 기록과 검증

가장 쉬운 방법은 Windows 파일럿 마법사를 사용하는 것입니다. 먼저 비개발자 tester가 clean GitHub checkout에서 실행합니다. 사내에서는 같은 commit이 반입된 clean Bitbucket checkout에서도 동일하게 실행할 수 있습니다.

```powershell
.\pilot-acceptance.cmd preflight `
  --evidence C:\approved-test-evidence\release-acceptance.json

.\pilot-acceptance.cmd start `
  --evidence C:\approved-test-evidence\release-acceptance.json
```

`preflight`는 파일을 만들지 않고 Windows-native 경로, 승인된 Git host, clean branch, 전체 commit ID, 저장소 밖의 새 evidence 경로를 먼저 확인합니다. 기본 허용 패턴은 `github.com` 또는 hostname에 `bitbucket`이 포함된 저장소입니다. 그 다음 `start`가 Wiki 설치, capture, search, promotion preview, 선택형 Obsidian, 보안 invariant를 차례로 묻습니다. 이름·사번·업무 원문·화면 녹화는 묻거나 기록하지 않습니다. 결과는 저장소 밖의 지정 경로에만 기록하며 기존 evidence를 덮어쓰지 않습니다.

tester draft가 만들어지면 knowledge steward가 같은 commit의 clean checkout에서 검토합니다.

```powershell
.\pilot-acceptance.cmd domain-review `
  --evidence C:\approved-test-evidence\release-acceptance.json

.\pilot-acceptance.cmd review `
  --evidence C:\approved-test-evidence\release-acceptance.json `
  --reviewer-role knowledge-steward

.\pilot-acceptance.cmd validate `
  --evidence C:\approved-test-evidence\release-acceptance.json
```

사내 Git hostname이 기본 패턴과 다르면 조직이 승인한 hostname 정규식을 subcommand 앞에 지정합니다.

```powershell
.\pilot-acceptance.cmd --origin-host-pattern "git[.]corp[.]example" start `
  --evidence C:\approved-test-evidence\release-acceptance.json
```

JSON을 직접 작성해야 할 때만 `research/release-acceptance-evidence.example.json`을 저장소 밖의 승인된 test evidence 위치로 복사해 결과를 채웁니다. `build_commit`에는 pilot이 실제 clone한 전체 40자리 또는 64자리 Git object ID를 기록합니다. 이름·사번·이메일·사용자 홈 경로·업무 원문·화면 녹화는 넣지 않습니다. 검사기는 알려지지 않은 필드와 개인 식별자 형태를 차단합니다.

```powershell
$testedCommit = git rev-parse HEAD
python scripts\release_evidence.py `
  --evidence C:\approved-test-evidence\release-acceptance.json `
  --expected-build-commit $testedCommit
```

## 정상 결과와 Local/Remote 경계

Obsidian 미사용 비개발자, Obsidian Core 비개발자, knowledge steward가 모두 확인하고 검사 결과가 `ok: true`일 때만 “사내 배포 완료”라고 표시합니다. 이 evidence는 원격 문서 등록 권한을 부여하지 않으며 Local Private 원문을 포함하지 않습니다. 실패하면 해당 기능은 조건부 또는 미지원으로 유지합니다.

이전: [관리자 호환 점검](80-admin-release-and-contract.md) · 다음: [가이드 홈](00-start-here.md)
