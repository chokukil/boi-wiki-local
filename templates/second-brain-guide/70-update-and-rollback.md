---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "Git 저장소 업데이트와 origin 전환"
description: "GitHub 또는 Bitbucket origin 기반 preview, fast-forward update, 가이드 백업과 복구"
tags: [Windows, GitHub, Bitbucket, Update, Rollback]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:update-rollback
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
guide_release: "3.1.0"
guide_audience: "기존 설치 업데이트 사용자"
guide_duration_minutes: 10
guide_prerequisites: "clean stable branch와 Git for Windows"
guide_execution: "PowerShell-native update.cmd로 origin fetch preview 후 ff-only update와 guide backup을 수행한다"
guide_success: "Harness와 check가 통과하고 개인 문서 hash가 동일하다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "71-contributing-via-pr.md"
guide_boundary: "repository-only"
source_refs:
  - type: local-guide-source
    ref: templates/second-brain-guide/70-update-and-rollback.md
---

# Git 저장소 업데이트와 origin 전환

대상은 설치된 사용 환경을 업데이트하는 사람이며 약 10분이 걸립니다. Git for Windows와 clean stable branch만 필요하며 Python은 필요하지 않습니다.

## 실행 단계

```powershell
.\update.cmd
.\update.cmd --apply
.\update.cmd --apply --confirm-guide-release 3.1.0
```

update preview는 fetch 전에 사내 Bitbucket을 우선 검사하고 `Repository source state`, 선택 이유, origin 변경 후보와 일회성 승인 코드를 보여줍니다. 사내망에 도달하지 못할 때만 GitHub로 fallback하며, 사내 인증·저장소 권한 실패는 우회하지 않습니다. origin 변경 후보가 있으면 다음처럼 그 preview 승인 코드를 함께 전달합니다.

```powershell
.\update.cmd --apply --confirm-source-plan <preview에 표시된 승인 코드>
```

origin drift, mirror revision 불일치 또는 승인 코드 변경이 감지되면 적용하지 않고 새 preview를 요구합니다. feature branch와 작업 파일은 바꾸지 않으며, 외부 origin 선택은 push 승인으로 취급하지 않습니다.

첫 명령은 현재 `origin`을 fetch하고 incoming commit/file만 보여줍니다. Apply는 stable branch에서 `git pull --ff-only`만 사용합니다. 가이드 적용은 release 문자열을 명시할 때만 수행하며 기존 가이드는 `_archive/guides/<시각>/`에 백업됩니다.

`update.cmd`는 Windows PowerShell만 사용합니다. Harness lock과 offline snapshot의 release·checksum·signature 일치를 확인하고, Python이 없는 환경에서는 이를 `reduced offline verification`으로 명확히 표시합니다. Native 검사는 Meta Harness·Core Skills·Local Profile·연결형 Wiki·Windows 진입점만 요구합니다. Python evaluator, fixture builder, benchmark, acceptance와 contract oracle은 관리자·CI 계층이며 일반 사용자 설치·업데이트의 파일 의존성이 아닙니다.

환경 변수와 `.env`가 서로 다른 실제 Local Profile을 가리키면 업데이트는 어느 쪽도 추측하지 않고 중단합니다. `0000000` 예제 값은 실제 `.env` Profile보다 우선하지 않습니다. native 검사는 현재 작업본과 fetch한 stable 후보에서 `AGENTS.md`·`CLAUDE.md`와 양 runtime Core Skill의 존재·non-empty·동일 내용을 확인합니다. 후보가 손상됐으면 pull 전에 중단하므로 현재 release와 Local Private를 그대로 유지합니다.

업데이트는 새 PowerShell 세션에서도 현재 환경변수, `.env`, 단 하나의 실제 Profile 디렉터리 순으로 대상을 찾고 화면에는 사번 대신 선택 근거만 표시합니다. 실제 Profile이 둘 이상이면 중단합니다. 선택된 Profile의 가이드와 archive를 제외한 Local Private 파일 SHA256을 업데이트 전후 비교하므로, 템플릿이 아니라 실제 개인 문서가 보호됩니다.

외부 GitHub 기준 checkout을 사내 Bitbucket mirror로 전환할 때는 동일한 commit이 mirror에 있는지 관리자가 먼저 확인합니다. 사용자는 자격증명을 파일에 넣지 말고 origin만 바꿉니다.

```powershell
git remote set-url origin <사내 Bitbucket URL>
git remote -v
git fetch origin
```

그 다음 `update.cmd` preview에서 `origin`, stable branch, incoming commit을 확인합니다. 스크립트·Wiki·Profile schema는 provider를 구분하지 않으므로 URL 이외의 설정 파일을 수정하지 않습니다.

## 정상 결과와 실패 시 이동

Harness의 고정 정보와 Windows 기본 구조 검사가 통과하고 Local Private 비관리 파일 hash가 전후 동일하면 일반 사용자 업데이트는 정상입니다. 전체 OKF·BoI·평가 검사는 관리자·CI 릴리스 단계에서 별도로 수행합니다. dirty·diverged·offline 상태에서는 자동 stash/reset 없이 중단합니다. 문제는 [문제 해결](60-troubleshooting.md)을 봅니다.

## Local/Remote 경계와 다음 여정

Git update는 프로그램과 템플릿을 갱신할 뿐 Local Private 문서를 전송하지 않습니다. 다음: [PR 기여](71-contributing-via-pr.md)
