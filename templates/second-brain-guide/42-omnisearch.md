---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "Omnisearch 도입 보류와 판단 기준"
description: "Core Search의 한계가 검증된 경우에만 Omnisearch를 다시 검토하는 기준"
tags: [LocalPrivate, SecondBrain, Guide, Obsidian, Search]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:omnisearch
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
guide_audience: "Core Search의 한계를 확인한 사용자와 배포 관리자"
guide_duration_minutes: 5
guide_prerequisites: "Obsidian Core Search와 AI 검색 사용 기록"
guide_execution: "검색 누락을 재현하고 도입 필요성을 검토한다"
guide_success: "설치 없이 기본 검색을 유지하거나 검증된 근거로만 도입 후보가 됐다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "50-mcp-and-promotion.md"
guide_boundary: "optional-obsidian-local"
source_refs:
  - type: source-repository
    ref: https://github.com/scambier/obsidian-omnisearch
---

# Omnisearch 도입 보류와 판단 기준

현재 배포판은 Omnisearch를 설치하지 않습니다. 기본 검색은 Obsidian Core Search와 AI의 파일 근거 검색이며, 별도 검색 플러그인이 필요하다는 사용자 검증 근거가 생기기 전에는 Core 경로를 유지합니다.

## 다시 검토할 조건

다음 조건을 모두 만족할 때만 배포 관리자가 후보를 다시 평가합니다.

1. 동일한 검색어와 문서 집합에서 Core Search 누락을 재현했습니다.
2. 파일명·본문·Properties 검색으로 해결되지 않았습니다.
3. AI에게 같은 검색을 요청해도 사용자 여정 목표 시간을 넘었습니다.
4. 플러그인 버전, 권한, 네트워크 기능, 인덱스 위치와 복구 절차를 검토했습니다.
5. Local Private 문서가 외부로 전송되지 않음을 별도 테스트했습니다.

배포 관리자가 호환성·권한·네트워크 검사를 통과시켜도 그 결과는 설치 승인이 아닙니다. 도입 전에도 OKF 0.1, BoI Profile 0.1-local, 표준 Markdown 링크가 원천 계약으로 유지되어야 합니다.

## 현재 fallback

```text
"검색어"와 관련된 Local 문서를 찾아줘. 정제된 지식을 먼저 보여주고,
근거 파일 경로와 현재 출처 hash를 함께 알려줘.
```

검색 결과는 실제 Markdown 경로와 줄 번호를 근거로 사용합니다. 자동 요약이나 시각적 연결만으로 provenance를 만들지 않습니다.

이전: [Web Clipper](43-web-clipper.md) · 다음: [MCP와 Team·Public 공유](50-mcp-and-promotion.md)
