---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-report
title: "오래된 Private BoI 정리 후보"
description: "Local Private 문서 정리 후보 예시"
boi_id: boi:private:0000000:legacy:archive-cleanup-candidates:0fd3cf53a6
classification: internal
owner: "0000000"
artifact_visibility: working
lifecycle_state: working
memory_candidate: false
cleanup_policy: keep
timestamp: 2026-06-20T22:13:00+09:00
employee_id: "0000000"
local_owner_ref: local-private:0000000
visibility: local-private
local_only: true
promotion_status: local_only
retention_class: working
retention_until: ""
archive_status: active
review_after: 2026-07-20
contains_sensitive: no
source_refs:
  - type: local-example
    ref: ../usage-examples/natural-language-poc/archive-candidates.md
---

# Candidate Rules

| Rule | Action |
|---|---|
| `review_after` is older than today and `archive_status: active` | show as review candidate |
| `retention_class: ephemeral` and retention expired | archive candidate |
| `promotion_status: promoted` | keep as promoted source unless owner approves |
| `contains_sensitive: yes` | do not delete automatically |

# Example Candidates

| Path | Reason | Recommendation |
|---|---|---|
| `workflow-simulations/old-preflight.md` | ephemeral review date passed | archive after owner approval |
| `notes/old-meeting.md` | working note, no source refs | ask owner |
| `promotion-drafts/public-sop.md` | pending approval | keep |
