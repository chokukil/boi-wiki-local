---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-example
title: Local Only Mode 예제
description: MCP 설정 없이 Local Private workspace만 사용하는 요청
timestamp: 2026-06-20T00:05:00+09:00
visibility: local-private
local_only: true
promotion_status: local_only
retention_class: record
retention_until: ""
archive_status: active
review_after: 2026-09-20
contains_sensitive: no
source_refs:
  - type: local-template
    ref: boi-wiki-local
---

# Prompt

```text
MCP 설정은 모르겠으니 local만 써줘. 이 폴더 안에서만 회의록과 SOP 초안을 정리하고, 원격 공유는 하지 마.
```

# Expected Agent Behavior

1. 원격 MCP를 찾거나 요구하지 않는다.
2. local 파일과 사용자가 제공한 자료만 사용한다.
3. 원격 context가 꼭 필요하면 Web 링크나 붙여넣기 자료를 요청한다.

# Citations

- Skill: `boi-wiki-local`
