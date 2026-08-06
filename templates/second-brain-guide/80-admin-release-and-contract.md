---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "관리자용 BoI Wiki 호환 점검"
description: "실제 validator, Harness, Windows 배포를 함께 확인하는 release gate"
tags: [Admin, Contract, Harness, Release]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:admin-release
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
guide_release: "3.0.0"
guide_audience: "배포 관리자와 BoI Wiki maintainer"
guide_duration_minutes: 30
guide_prerequisites: "실제 boi-wiki-run, Windows test clone, pinned Harness"
guide_execution: "migration, contract, privacy, clean clone, UX, plugin, release gate를 실행한다"
guide_success: "자동 게이트와 미충족 수동 evidence가 분리돼 표시된다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "90-release-acceptance.md"
guide_boundary: "release-validation-only"
source_refs:
  - type: local-guide-source
    ref: templates/second-brain-guide/80-admin-release-and-contract.md
---

# 관리자용 BoI Wiki 호환 점검

대상은 배포 관리자와 BoI Wiki maintainer이며 환경당 약 30분이 걸립니다. 실제 대상 `boi-wiki-run`, Windows test clone, 최신 pinned Harness가 필요합니다.

Codex·Claude의 자동 확인과 Python 없는 일반 사용자 경로는 먼저 [관리자용 Codex·Claude 자동 확인 계약](81-agent-auto-check-admin.md)에서 검토합니다.

## 실행 단계

```powershell
$env:BOI_WIKI_ROOT="C:\path\to\boi-wiki-run"
python scripts\harness_sync.py verify
python scripts\migration_audit.py --source "\\wsl$\Ubuntu-22.04\home\<계정>\boi-wiki-local" --target .
python -m unittest discover -s tests -p "test_*.py"
python scripts\ux_acceptance.py --boi-wiki-root $env:BOI_WIKI_ROOT
python scripts\release_clone_acceptance.py --root .
python scripts\obsidian_plugin_check.py
powershell.exe -NoLogo -NoProfile -ExecutionPolicy RemoteSigned -File .\check.ps1
```

모든 자동 증거와 실제 사용자 acceptance를 한 번에 판정할 때는 다음을 사용합니다. evidence의 `build_commit`은 이 checkout의 `HEAD`와 정확히 일치해야 합니다.

비개발자와 reviewer evidence는 [사용자 Acceptance](90-release-acceptance.md)의 `preflight → start → domain-review → review → validate` 순서로 만들며 저장소 밖에 보관합니다.

```powershell
python scripts\release_gate.py --boi-wiki-root $env:BOI_WIKI_ROOT --wsl-source "\\wsl$\Ubuntu-22.04\home\<계정>\boi-wiki-local" --origin-host-pattern "github[.]com|bitbucket" --acceptance-evidence C:\approved-test-evidence\release-acceptance.json --require-manual-evidence
```

Team, Public, SOP, Dictionary, Event/Action, Context pack, 주간보고 candidate를 실제 `validate_okf_core_metadata`와 `validate_boi_profile_metadata(..., promotion=True)`에 통과시킵니다. 잘못된 Local version/visibility, 문자열 source refs, reviewer/team ID 누락, owner/ACL 위조, revision/hash/idempotency/Harness 불일치는 반드시 실패해야 합니다.

Windows 신규 설치, origin 변경, update preview/apply, offline·dirty·diverged, Obsidian 없음과 선택 기능 추가/제거도 검사합니다. `migration_audit.py`는 WSL과 Windows의 공통 HEAD, 전체 후보 경로, source SHA256 ledger, 동일 파일과 Windows 후속 변경을 분리하고 누락·실사용자 Private 포함을 차단합니다. `release_clone_acceptance.py`는 외부 GitHub analogue에서 clone한 뒤 같은 commit을 가진 사내 Bitbucket analogue로 origin URL만 교체하고 `install.cmd`, pinned Harness, clean Git 상태, fast-forward update, Local Private hash 불변을 확인합니다. 실제 사내 인증·네트워크는 제품 코드가 아니라 사내 반입 절차에서 확인합니다.

## 정상 결과와 실패 시 이동

실제 대상 contract, golden package, Windows journey, 승인 없는 BoI Wiki·MCP mutation 0건과 promotion 전송 0건을 모두 증명해야 release 가능합니다. AI 런타임이 선택 입력을 처리한 사실은 별도 `model_context` evidence로 기록하며 이를 Local 무전송으로 과장하지 않습니다. `full_release_ready`는 실제 사내 Bitbucket origin, 비개발자 Windows 여정, 도메인 대표 사례 검토까지 통과했을 때만 참입니다. 외부 GitHub는 설치·업데이트와 origin 교체를 검증하는 기준 저장소일 뿐 사내 배포 완료의 증거가 아닙니다. Obsidian은 선택 사항이므로 별도 `obsidian_support_ready`로 판정합니다. pinned fixture만 통과하면 호환으로 판정하지 않습니다.

## Local/Remote 경계와 다음 여정

contract test가 실패하면 submit capability를 배포하지 않고 schema 차이를 먼저 해결합니다. 자동 검사가 끝나면 [사내 배포 전 사용자 Acceptance](90-release-acceptance.md)로 이동합니다.
