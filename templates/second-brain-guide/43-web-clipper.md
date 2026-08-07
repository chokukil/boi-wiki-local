---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "Obsidian Web Clipper로 웹 자료 수집"
description: "공식 브라우저 확장을 선택 설치해 웹 자료를 Local evidence 후보로 저장하는 방법"
tags: [LocalPrivate, SecondBrain, Guide, Obsidian, WebClipper]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:web-clipper
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
guide_release: "3.1.0"
guide_audience: "공개 웹 자료를 Local Second Brain에 모으는 사용자"
guide_duration_minutes: 10
guide_prerequisites: "지원 브라우저, Obsidian Vault, 사용자 설치 승인"
guide_execution: "공식 확장을 수동 설치하고 별도 수집 폴더에 저장한 뒤 intake preview를 확인한다"
guide_success: "URL과 수집일이 있는 Markdown을 Local evidence로 검토했다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "42-omnisearch.md"
guide_boundary: "optional-obsidian-local"
source_refs:
  - type: official-doc
    ref: https://obsidian.md/help/web-clipper
  - type: source-repository
    ref: https://github.com/obsidianmd/obsidian-clipper
---

# Obsidian Web Clipper로 웹 자료 수집

공식 Web Clipper는 웹 페이지와 하이라이트를 Local Markdown으로 저장하는 선택형 브라우저 확장입니다. 자동 크롤러가 아니며, 설치·사이트 접근·저장은 사용자가 직접 실행합니다. Obsidian이 없어도 페이지를 Markdown으로 저장해 자료 폴더에 넣고 AI에게 같은 정리 여정을 요청할 수 있습니다.

## 설치와 최소 설정

1. [Obsidian 공식 Web Clipper 안내](https://obsidian.md/help/web-clipper)에서 현재 브라우저의 공식 스토어 링크를 엽니다.
2. 확장 권한과 사이트 접근 범위를 확인하고 사용자가 직접 설치를 승인합니다.
3. 기본 저장 위치를 Local Private Vault의 별도 수집 폴더로 지정합니다.
4. 템플릿에는 최소한 원문 제목, 원 URL, 수집 시각을 남깁니다.
5. Interpreter 같은 추가 처리 기능은 사내 정책과 데이터 경계를 별도로 확인하기 전에는 사용하지 않습니다.

## BoI intake로 넘기기

클립 파일은 아직 canonical evidence가 아닙니다. 먼저 preview에서 hash, 유형, 출처와 Local Private 경계를 확인합니다.

```text
자료 폴더의 article.md를 Local Private 웹 자료로 정리해줘.
원본은 바꾸지 말고 URL, 수집일, SHA256을 보존해.
기존 지식과 비교해서 재사용할 주장·제약·불확실성을 같은 작업에서 정리하고,
아직 Team/Public로 공유하지 마.
```

저장된 본문이 원 페이지 전체와 다를 수 있으므로 제목·URL·날짜와 핵심 문단을 사람이 대조합니다. 로그인 페이지, 사내 전용 페이지, 실제 업무 원문은 공개 출처처럼 취급하지 않습니다.

## 정상 결과와 경계

원본 클립과 SHA256이 있는 원본 정보가 Local에 남고, 재사용 가능한 지식이 `source_refs`로 이를 가리키면 정상입니다. Web Clipper 설치만으로 MCP 조회나 Team/Public 등록은 일어나지 않습니다. 제거 후에도 Markdown은 남으므로 AI의 자료 정리와 근거 검색을 계속 사용할 수 있습니다.

이전: [QuickAdd](41-quickadd.md) · 다음: [Omnisearch 도입 판단](42-omnisearch.md)
