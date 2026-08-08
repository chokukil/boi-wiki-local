---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "가이드·템플릿 PR 기여"
description: "Local Private를 노출하지 않고 저장소 개선을 공유하는 방법"
tags: [GitHub, Bitbucket, PullRequest, Contribution, Security]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:contributing
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
guide_audience: "가이드·템플릿 개선 기여자"
guide_duration_minutes: 10
guide_prerequisites: "Git branch와 PR 권한"
guide_execution: "privacy scan 후 코드·템플릿만 branch와 PR로 기여한다"
guide_success: "실제 Local Private와 비밀정보 없이 검토 가능한 PR이 준비됐다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "72-security-and-source-review.md"
guide_boundary: "repository-only"
source_refs:
  - type: local-guide-source
    ref: templates/second-brain-guide/71-contributing-via-pr.md
---

# 가이드·템플릿 PR 기여

대상은 저장소 개선 기여자이며 약 15분이 걸립니다. 외부 기준 저장소에서는 GitHub PR, 사내 mirror에서는 Bitbucket PR 권한이 필요합니다.

## 실행 단계

1. stable에서 feature branch를 만듭니다.
2. `templates/`, `scripts/`, `tests/`, 공용 예제만 수정합니다.
3. `powershell.exe -NoLogo -NoProfile -ExecutionPolicy RemoteSigned -File .\check.ps1`과 `python scripts\contribution_check.py`를 실행합니다.
4. diff에 사번, 실제 업무 내용, PAT, `.env`, `.obsidian`, 개인 Profile, 실제 파일럿 acceptance evidence가 없는지 직접 확인합니다.
5. 현재 provider의 PR에서 목적, 테스트 결과, 호환성 영향을 같은 형식으로 설명합니다.

## 정상 결과와 실패 시 이동

검사 통과와 reviewer 승인이 있으면 정상입니다. private leak 경고가 하나라도 있으면 commit/push하지 말고 [보안·출처 검토](72-security-and-source-review.md)로 이동합니다.

## Local/Remote 경계와 다음 여정

실제 Local Private 지식은 Git PR로 공유하지 않습니다. Team/Public 공유에는 promotion을 사용하고 파일럿 evidence는 저장소 밖에 둡니다. 다음: [보안·출처 검토](72-security-and-source-review.md)
