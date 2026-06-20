---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-example
title: "원격 BoI Wiki Context Pack 예제"
description: "원격 BoI Wiki MCP가 있을 때 shared SOP/Action/Manual 문서를 묶어 context pack을 만드는 예제"
timestamp: 2026-06-20T21:56:00+09:00
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
    ref: ../../context-packs/direct-development-reporting-context-pack.md
---

# Prompt

```text
원격 BoI Wiki를 검색해서 이번 업무용 context pack을 만들어줘.
MCP가 되면 public SOP, Event Type, Action Spec, Langflow guide를 찾아 넣고, 안 되면 local repo의 기존 문서만 써줘.
```

# Generated Output

- 생성 문서: [direct-development-reporting-context-pack.md](../../context-packs/direct-development-reporting-context-pack.md)
- 포함 범위: SOP image draft, event-to-action plan, action draft, Langflow connected flow guide, promotion policy.

# Evidence

- MCP가 없어도 local-only fallback으로 context pack을 만들 수 있다.
- MCP가 있으면 shared BoI Wiki 문서 `boi:public:sop:direct-development-reporting`, `boi:public:actions:langflow:direct-development-quality-response-trend-simulate`, `boi:public:boi-wiki-manual:use-cases:sop-image-to-e2e-workflow`를 source_refs로 강화한다.

# How to Verify

1. MCP가 있으면 agent가 검색한 원격 BoI ID와 URL을 context pack에 남겼는지 확인한다.
2. MCP가 없으면 `remote_lookup_status: unavailable_local_fallback`를 명시한다.
3. context pack이 원본 private 내용을 원격으로 전송하지 않았는지 확인한다.

# Real vs Simulated

이 예제의 context pack은 실제 local output이다. 원격 조회 결과는 환경에 따라 달라지므로 MCP 미설정 상태에서는 fallback으로 문서화한다.
