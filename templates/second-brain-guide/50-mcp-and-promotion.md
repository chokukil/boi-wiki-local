---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "MCP 연결과 Team·Public 공유"
description: "로컬과 사내 BoI Wiki의 경계 및 승인 기반 promotion 절차"
tags: [LocalPrivate, SecondBrain, Guide, MCP, Promotion]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:mcp-promotion
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
guide_audience: "사내 Wiki 참조·공유 사용자"
guide_duration_minutes: 10
guide_prerequisites: "정제 Local 문서와 권한 범위 이해"
guide_execution: "MCP 조회와 promotion preview 경계를 확인한다"
guide_success: "MCP 연결이 자동 업로드가 아님을 설명할 수 있다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "51-promotion-package.md"
guide_boundary: "local-with-optional-mcp-read"
source_refs:
  - type: harness-contract
    ref: harness.lock
---

# MCP 연결과 Team·Public 공유

| 상태 | 가능한 일 |
|---|---|
| MCP 없음 | 로컬 문서 작성, 검색, 정제, 검토 |
| MCP 연결됨 | 권한 범위 안의 사내 BoI Wiki 문서를 검색·참조하여 로컬 문서 작성 |
| MCP만 연결 | Local Private 문서를 웹에 자동 적재하지 않음 |
| Team/Public 등록 | 정제 초안, 민감정보·출처·범위 검증, 미리보기, 사용자 승인, 지원되는 원격 등록 필요 |

## Promotion 준비

```text
이 정제 문서를 Team 공유 후보로 만들어줘.
공유 목적은 반복 업무 표준화이고 대상 Team과 reviewer는 나에게 확인해.
Local 경로·사번·원문은 제거하고 구조화된 공개 가능 출처를 넣어.
원격 등록은 하지 말고 exact hash가 있는 미리보기만 보여줘.
```

Public 후보는 요청문에서 Public 범위를 명시하고 공개 가능한 구조화 출처를 제공합니다. Public 후보에는 사번, Local Private 경로, 사내 전용 표현이 남아 있지 않아야 합니다.

## 승인 경계

1. 로컬 원문과 정제 문서를 분리합니다.
2. 공유할 본문만 promotion 후보로 만듭니다.
3. 민감정보, 출처, 대상 범위, 검토자를 확인합니다.
4. 후보 본문과 SHA256을 포함한 미리보기를 사용자에게 보여줍니다.
5. 사용자가 그 정확한 후보를 명시적으로 승인합니다.
6. 원격 기능이 지원될 때만 canonical 프로필로 변환해 등록합니다.

본문이 바뀌면 이전 승인은 무효입니다. 새로운 미리보기와 승인이 필요합니다. 원격 기능이 없으면 submission-ready 로컬 초안에서 멈춥니다.

이전: [Omnisearch 도입 판단](42-omnisearch.md) · 다음: [Promotion Package](51-promotion-package.md)
