---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-example
title: "오래된 Private BoI 정리 후보 예제"
description: "Local Private 문서 중 review_after가 지난 문서를 정리 후보로 보여주는 예제"
timestamp: 2026-06-20T21:59:00+09:00
employee_id: "0000000"
local_owner_ref: local-private:0000000
visibility: local-private
local_only: true
promotion_status: local_only
retention_class: record
retention_until: ""
archive_status: active
review_after: 2026-09-20
contains_sensitive: no
source_refs:
  - type: generated-output
    ref: ../../reports/archive-cleanup-candidates.md
---

# Prompt

```text
오래된 Private BoI 정리 후보 보여줘.
```

# Generated Output

- 생성 문서: [archive-cleanup-candidates.md](../../reports/archive-cleanup-candidates.md)
- 후보 분류: archive candidate, keep, promote candidate, needs owner review.

# Evidence

- Local Private 문서의 `review_after`, `retention_class`, `archive_status` metadata를 기준으로 한다.
- 삭제가 아니라 후보 목록을 먼저 보여준다.

# How to Verify

1. agent가 `data/boi/private/{사번}/` 아래만 대상으로 삼았는지 확인한다.
2. `_archive/` 이동이나 삭제는 사용자 승인 전 실행하지 않는다.
3. `promoted_source`는 임의로 삭제 후보에 넣지 않는다.

# Real vs Simulated

이 예제의 후보 보고서는 실제 local output이다. 실제 archive 이동은 별도 승인 후 수행한다.
