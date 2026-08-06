---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "10분 Second Brain 튜토리얼"
description: "원문 수집, 정제, 검색, 검토를 한 번씩 수행하는 첫 사용 안내"
tags: [LocalPrivate, SecondBrain, Guide, Tutorial]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:first-ten-minutes
visibility: local-private
classification: internal
owner: "{{employee_id}}"
employee_id: "{{employee_id}}"
local_owner_ref: local-private:{{employee_id}}
local_only: true
promotion_status: local_only
retention_class: working
retention_until: ""
archive_status: active
artifact_visibility: memory
lifecycle_state: memory
memory_candidate: false
cleanup_policy: keep
review_after: {{review_after}}
contains_sensitive: false
guide_release: "3.0.0"
guide_audience: "첫 지식을 만드는 사용자"
guide_duration_minutes: 10
guide_prerequisites: "Local Private 초기 설정 완료"
guide_execution: "합성 메모를 capture하고 distill, search, review한다"
guide_success: "원문과 정제 문서가 분리되고 검색 근거가 나온다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "23-capture-distill-review.md"
guide_boundary: "local-only"
source_refs:
  - type: methodology
    ref: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
---

# 10분 Second Brain 튜토리얼

## 1. 원문 수집

에이전트에게 다음과 같이 요청합니다.

```text
오늘 회의 메모를 수정하지 않는 원문으로 수집해줘.
```

생성된 원문에는 SHA256과 `source_immutability: locked`가 기록됩니다.

## 2. 지식으로 정제

```text
방금 수집한 원문을 핵심 결정, 근거, 후속 작업으로 정제해줘. 원문은 고치지 마.
```

정제 문서는 `notes/knowledge/`에 생성되고 원문을 `source_refs`로 가리킵니다.

## 3. 다시 찾기

```text
첫 회의 메모와 관련된 로컬 문서를 근거 경로와 함께 찾아줘.
```

AI는 정제 문서를 먼저 찾고, 답변에 실제 Local 문서 경로와 근거를 붙입니다. Obsidian을 사용한다면 Core Search에서도 같은 키워드로 확인할 수 있습니다.

## 4. 검토

```text
방금 만든 원문과 정제 문서의 출처, 링크, 검토 기한과 Local Private 경계를
확인해줘. 오래됐거나 근거가 부족한 내용은 고치지 말고 확인 필요로 보여줘.
```

오래된 초안, 기억 후보, promotion 후보를 보여줄 뿐 자동 삭제하거나 공유하지 않습니다.

이전: [첫 설정과 확인](11-first-setup.md) · 다음 선택: [Obsidian 설치](30-obsidian-install-and-vault.md) 또는 [MCP와 공유](50-mcp-and-promotion.md)
## 화면 08 — Core Search로 다시 찾기

![Obsidian Core Search에서 합성 품질 지식을 다시 찾는 화면](_media/08-core-search.webp)

[화면 08을 원본 크기로 열기](_media/08-core-search.webp)

검색어를 입력하면 capture, 정제 지식, 사례 Wiki가 함께 나타납니다. 검색 결과가 너무 많으면 `path:notes/knowledge`를 더합니다.

다음: [Capture에서 정제·검토까지](23-capture-distill-review.md)
