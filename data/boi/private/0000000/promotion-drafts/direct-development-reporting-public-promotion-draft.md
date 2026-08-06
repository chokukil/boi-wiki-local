---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-promotion-draft
title: "직개발 Reporting SOP Public Promotion Draft"
description: "직개발 Reporting SOP를 Public BoI Wiki로 공유하기 전 preview/preflight 초안"
boi_id: boi:private:0000000:legacy:direct-development-reporting-public-promotion-draft:182548e584
classification: internal
owner: "0000000"
artifact_visibility: working
lifecycle_state: protected
memory_candidate: false
cleanup_policy: keep
timestamp: 2026-06-20T22:10:00+09:00
employee_id: "0000000"
local_owner_ref: local-private:0000000
visibility: local-private
local_only: true
promotion_status: pending_user_approval
retention_class: working
retention_until: ""
archive_status: active
review_after: 2026-07-20
contains_sensitive: unknown
source_refs:
  - type: sop-draft
    ref: ../sop-drafts/direct-development-reporting-sop-draft.md
  - type: image
    ref: ../usage-examples/natural-language-poc/evidence/sop_sample_image.png
---

# Target

| Field | Value |
|---|---|
| target_visibility | public |
| target_doc_type | `boi/sop` |
| approval_required | yes |
| remote_submit_status | not_submitted |

# Preflight Checklist

- [ ] 원본 SOP 이미지 공개 가능성 확인
- [ ] 사내 시스템명 공개 범위 확인
- [ ] 품질 시스템/Map 분석 시스템/단면 검사 시스템/메신저 connector gap을 live action처럼 쓰지 않았는지 확인
- [ ] source_refs와 evidence image를 포함했는지 확인
- [ ] 사용자 최종 승인 획득

# Preview Summary

Public 후보는 절차 구조와 action gap을 공유하되, 실제 사번/lot/wafer/설비 식별자는 포함하지 않는다.
