---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-example
title: "MCP 없이 Local Only 작업 예제"
description: "MCP 설정 없이 local files만 사용해 BoI 작업을 완료하는 예제"
timestamp: 2026-06-20T22:00:00+09:00
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
    ref: ../../workflow-simulations/local-only-runbook.md
---

# Prompt

```text
MCP 설정은 모르겠으니 local만 써줘.
이 SOP 이미지와 회의 내용을 내 PC 안에서만 정리하고, 원격 검색이나 공유는 하지 마.
```

# Generated Output

- 생성 문서: [local-only-runbook.md](../../workflow-simulations/local-only-runbook.md)
- agent는 원격 MCP 검색, promotion submit, action invoke를 생략하고 local Markdown만 작성한다.

# Evidence

- README와 AGENTS 규칙은 MCP를 optional로 정의한다.
- `local_only: true`, `visibility: local-private`, `promotion_status: local_only` metadata가 유지된다.

# How to Verify

1. 원격 URL 호출이나 MCP tool call 없이 local file만 변경됐는지 확인한다.
2. source image와 generated docs가 같은 local private tree 아래에 있는지 확인한다.
3. 공유 요청이 나오면 별도 promotion draft부터 생성하는지 확인한다.

# Real vs Simulated

Local-only runbook은 실제 local output이다. 원격 BoI Wiki 조회와 live action 실행은 의도적으로 수행하지 않는다.
