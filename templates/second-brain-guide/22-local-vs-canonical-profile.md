---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "Local Profile과 canonical Profile"
description: "개인 Second Brain과 기존 BoI Wiki 사이의 compatibility boundary"
tags: [LocalPrivate, Canonical, Promotion, Guide]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:profile-boundary
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
guide_audience: "공유 후보 작성자와 reviewer"
guide_duration_minutes: 7
guide_prerequisites: "OKF와 BoI Profile 기본 이해"
guide_execution: "Local 필드와 canonical 변환 필드를 대응한다"
guide_success: "Local 파일을 원격 payload로 직접 쓰면 안 되는 이유를 안다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "50-mcp-and-promotion.md"
guide_boundary: "promotion-preview-only"
source_refs:
  - type: local-guide-source
    ref: templates/second-brain-guide/22-local-vs-canonical-profile.md
---

# Local Profile과 canonical Profile

대상은 공유 후보를 만드는 사용자와 관리자이며 약 7분이 걸립니다. [OKF와 BoI Profile](21-okf-and-boi-profile.md)을 먼저 읽습니다.

## 변환 원칙

| Local Private | canonical candidate |
|---|---|
| `boi_profile_version: 0.1-local` | `0.1` |
| `visibility: local-private` | 사용자가 고른 `team` 또는 `public` |
| Local `boi_id` | provenance에만 남고 최종 ID는 원격 발급 |
| 사번과 로컬 경로 | 원격 projection에서 제거 |
| `promotion_status` | `status: draft`, `review: pending` |
| 공개 가능한 출처 | `{type, ref, note}` 객체 목록 |
| Local owner/ACL | 인증 principal과 target scope로 원격 결정 |

## 정상 결과와 실패 시 이동

`.remote.json`에 `0.1-local`, `local-private`, 로컬 경로, 사번이 없고 reviewer와 구조화 출처가 있으면 정상입니다. 하나라도 남으면 제출하지 말고 [보안·출처 검토](72-security-and-source-review.md)로 이동합니다.

## Local/Remote 경계와 다음 여정

현재 로컬 도구는 package와 sanitized projection만 만들며 원격 submit은 하지 않습니다. 다음: [MCP와 promotion 경계](50-mcp-and-promotion.md)
