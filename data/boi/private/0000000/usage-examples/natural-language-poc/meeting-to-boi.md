---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-example
title: "회의 내용 BoI 정리 예제"
description: "회의 메모를 Local Private BoI note로 정리하는 자연어 요청 예제"
timestamp: 2026-06-20T21:51:00+09:00
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
    ref: ../../notes/sample-meeting-to-boi.md
---

# Prompt

```text
이 회의 내용을 BoI로 정리해줘.
회의 주제는 직개발 결과 확인 및 Reporting SOP를 AI-native workflow로 PoC하는 것이다.
결정사항, 액션 아이템, 관련 업무 BoI/SOP/Event/업무 요청 후보, 다음 확인 질문을 나눠줘.
```

# Generated Output

- 생성 문서: [sample-meeting-to-boi.md](../../notes/sample-meeting-to-boi.md)
- 주요 결과: 의사결정, 액션 아이템, SOP 후보, Event 후보, Action 후보, open question을 Local Private note로 분리했다.

# Evidence

- Local file evidence: `data/boi/private/0000000/notes/sample-meeting-to-boi.md`
- 이 예제는 원격 게시 없이 local-only로 완료된다.

# How to Verify

1. `data/boi/private/{7자리사번}/notes/`에 같은 형식의 회의록이 생성되는지 확인한다.
2. frontmatter의 `employee_id`와 `local_owner_ref`가 실제 사번 폴더와 일치하는지 확인한다.
3. 공유 요청이 없으면 원격 BoI Wiki URL이나 publish draft가 생기지 않아야 한다.

# Real vs Simulated

이 예제의 Markdown 산출물은 실제 local output이다. 회의 원문은 PoC용 샘플이므로 민감정보를 포함하지 않는다.
