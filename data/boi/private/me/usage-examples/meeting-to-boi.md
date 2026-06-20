---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-example
title: Meeting to BoI 예제
description: 회의 내용을 Local Private BoI로 정리하고 관련 Event 후보를 제안하는 요청
timestamp: 2026-06-20T00:03:00+09:00
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
이 회의 내용을 BoI로 정리해줘. 결정사항, 액션 아이템, 관련 SOP/Event Type 후보, 다음 회의에서 확인할 질문을 나눠줘.
```

# Expected Agent Behavior

1. 기본 `boi-wiki-local` skill을 사용한다.
2. 회의록은 `data/boi/private/me/notes/`에 저장한다.
3. event/action 후보는 확정하지 않고 후보로 표시한다.
4. 공유 요청이 있으면 promotion draft를 따로 만든다.

# Citations

- Skill: `boi-wiki-local`
