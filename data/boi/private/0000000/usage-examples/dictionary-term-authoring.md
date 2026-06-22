---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-example
title: "Dictionary Term Authoring"
description: "현장 용어를 Local Private dictionary BoI로 정리하는 예제"
timestamp: 2026-06-23T09:05:00+09:00
employee_id: "0000000"
local_owner_ref: local-private:0000000
visibility: local-private
local_only: true
promotion_status: local_only
retention_class: working
retention_until: ""
archive_status: active
review_after: 2026-09-23
contains_sensitive: no
source_refs:
  - type: local-example
    ref: ../dictionary/response-trend.md
---

# Request

```text
현장에서 말하는 Response Trend 용어를 dictionary에 추가해줘.
```

# Agent Behavior

1. 7자리 사번을 확인한다.
2. MCP가 있으면 `dictionary_resolve`로 shared dictionary에 같은 용어가 있는지 먼저 확인한다.
3. MCP가 없으면 local 문서와 사용자가 제공한 설명만으로 초안을 만든다.
4. 기본 입력 5개를 정리한다: 용어, 별칭/약어, 뜻, 예시, 연결 문서.
5. `data/boi/private/{7자리사번}/dictionary/response-trend.md`에 Local Private dictionary BoI를 저장한다.
6. `index.md`와 `log.md`를 업데이트하고 self-check 결과를 보고한다.

# Output

- [Response Trend Dictionary Term](../dictionary/response-trend.md)

# Notes

Dictionary는 검색과 해석을 돕지만 실행 권한, 승인 정책, action dispatch를 바꾸지 않는다. Team/Public 공유는 별도 promotion draft와 사용자 승인이 필요하다.
