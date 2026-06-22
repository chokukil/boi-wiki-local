---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-example
title: "자연어 요청: Dictionary 용어 작성"
description: "현장 용어를 Local Private dictionary로 만들고 shared dictionary 조회를 선택적으로 사용하는 예제"
timestamp: 2026-06-23T09:10:00+09:00
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
    ref: ../../dictionary/response-trend.md
---

# User Request

```text
현장에서 말하는 Response Trend 용어를 dictionary에 추가해줘.
```

# Expected Agent Flow

1. `boi-dictionary-author` skill을 사용한다.
2. `BOI_LOCAL_EMPLOYEE_ID` 또는 사용자 확인으로 7자리 사번을 확보한다.
3. remote MCP가 있으면 `dictionary_resolve("Response Trend")`로 shared dictionary를 먼저 조회한다.
4. 같은 의미가 없거나 개인 해석이 필요하면 Local Private dictionary를 작성한다.
5. 용어, 별칭, 정의, 예시, 연결 action/SOP/BoI, source_refs를 정리한다.
6. 결과는 [Response Trend](../../dictionary/response-trend.md)처럼 local-only로 저장한다.

# Result

이 예제의 산출물은 [Response Trend dictionary term](../../dictionary/response-trend.md)이다.

# Self-check

- `visibility: local-private`
- `employee_id`와 경로 일치
- 용어와 정의 존재
- 연결 문서와 source_refs 존재
- shared publish 없음
