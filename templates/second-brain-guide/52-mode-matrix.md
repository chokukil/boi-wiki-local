---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "Obsidian·MCP·Promotion 모드별 기능"
description: "선택 기능의 존재 여부에 따라 가능한 작업과 금지되는 작업"
tags: [LocalPrivate, MCP, Obsidian, Mode]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:mode-matrix
visibility: local-private
classification: internal
owner: "{{employee_id}}"
employee_id: "{{employee_id}}"
local_owner_ref: local-private:{{employee_id}}
local_only: true
promotion_status: local_only
retention_class: working
retention_until: ""
artifact_visibility: memory
lifecycle_state: memory
memory_candidate: false
cleanup_policy: keep
review_after: {{review_after}}
archive_status: active
contains_sensitive: false
guide_release: "3.1.0"
guide_audience: "구성별 기능을 선택하는 사용자"
guide_duration_minutes: 5
guide_prerequisites: "없음"
guide_execution: "Obsidian, MCP, promotion capability 조합을 비교한다"
guide_success: "현재 모드에서 가능한 작업과 금지 작업을 구분했다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "05-choose-your-path.md"
guide_boundary: "local-only"
source_refs:
  - type: local-guide-source
    ref: templates/second-brain-guide/52-mode-matrix.md
---

# Obsidian·MCP·Promotion 모드별 기능

대상은 모든 사용자이며 약 5분이 걸립니다. 선행 조건은 없습니다.

## 기능 표

| 구성 | 가능한 작업 | 불가능한 작업 |
|---|---|---|
| MCP 없음·Obsidian 없음 | capture, distill, search, lint, review, preview | 사내 Wiki 조회·원격 등록 |
| Obsidian만 있음 | 로컬 탐색, backlink, Graph, Properties | MCP 조회·자동 등록 |
| MCP 조회 연결 | 권한 내 BoI Wiki 검색·인용, local context 작성 | Local Private 자동 업로드 |
| MCP 인증 만료 | local-only fallback | ACL 우회·숨겨진 문서 조회 |
| promotion capability 없음 | canonical package·preview | submit |
| promotion capability 있음 | remote schema preview·validation | 승인 전 submit |
| 승인 완료 | exact hash가 같은 candidate submit | 승인 후 본문·scope 변경 |

## 반드시 기억할 경계

- MCP 없음: boi-wiki-local의 로컬 문서만 작성·검색·정리
- MCP 연결됨: 사내 boi-wiki 문서를 검색·참조하여 로컬 문서 작성 가능
- 단순 MCP 연결만으로는: Local Private 문서가 웹에 자동 적재되지 않음
- Team/Public 적재: promotion 초안 → 민감정보·출처·공개 범위 검증 → 미리보기 → 사용자 승인 → 원격 등록 기능이 지원될 때만 가능

## 정상 결과, 실패, 다음 여정

현재 모드에서 할 수 없는 작업을 도구가 명확히 거절하면 정상입니다. 연결 실패 시 local-only로 계속 사용하고 [문제 해결](60-troubleshooting.md)을 봅니다. 다음: [조직 지식 순환](53-organization-knowledge-loop.md)
## 화면 13 — 현재 모드에서 가능한 작업

![Obsidian과 MCP 구성에 따른 가능 작업과 금지 작업 표를 보는 화면](_media/13-mode-matrix.webp)

[화면 13을 원본 크기로 열기](_media/13-mode-matrix.webp)

표의 핵심은 MCP 연결과 원격 등록 권한을 구분하는 것입니다. MCP 조회가 가능해도 Local Private 문서가 자동 업로드되지는 않습니다.

다음: [사용 경로 선택](05-choose-your-path.md)
