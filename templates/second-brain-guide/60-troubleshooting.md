---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "문제 해결과 FAQ"
description: "설치, AI 작업 폴더, 사번, 원문 무결성, Obsidian, MCP 문제를 해결하는 안내"
tags: [LocalPrivate, SecondBrain, Guide, Troubleshooting, FAQ]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:troubleshooting
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
guide_audience: "오류를 해결하는 사용자와 지원 담당자"
guide_duration_minutes: 10
guide_prerequisites: "오류 메시지와 현재 모드 확인"
guide_execution: "증상별 안전 진단과 fallback을 적용한다"
guide_success: "데이터 손실 없이 정상 경로 또는 지원 요청으로 이동했다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "00-start-here.md"
guide_boundary: "local-only"
source_refs:
  - type: local-guide-source
    ref: templates/second-brain-guide/60-troubleshooting.md
---

# 문제 해결과 FAQ

## `0000000`이라고 나옵니다

템플릿 사번입니다. AI에게 `내 숫자 7자리 Local Profile 식별자로 설정 변경안을 다시 보여줘`라고 요청하고, 미리보기를 확인한 뒤 승인합니다.

## `multiple Local Private profiles found`라고 나옵니다

한 작업본에 실제 사번 형식의 Profile 디렉터리가 둘 이상 있어 안전하게 자동 선택할 수 없다는 뜻입니다. 다른 사람의 Profile을 복사하거나 공유하지 말고, AI에게 이번 작업에서 사용할 본인 Profile을 명시합니다. AI는 다른 Profile을 삭제하거나 합치지 않습니다.

## 설치가 기존 파일과 충돌합니다

설치기는 기존 파일을 덮어쓰지 않습니다. preview의 `conflicts`를 확인하고 사용자 문서를 보존한 채 파일별로 병합합니다. 가이드 업데이트도 먼저 차이를 확인합니다.

## AI가 `boi-harness-builder` 또는 Second Brain Skill을 찾지 못합니다

설치된 경로와 현재 AI 작업 폴더가 다를 가능성이 큽니다. 특히 예전 `\\wsl$\...\boi-wiki-local` 작업과 Windows clone을 동시에 가지고 있으면, Windows에 설치했더라도 WSL 작업에서는 새 project Skill이 보이지 않습니다.

AI에게 다음처럼 요청합니다.

```text
현재 작업 폴더가 어느 boi-wiki-local인지 확인해줘.
AGENTS.md·.agents/skills와 CLAUDE.md·.claude/skills가 같은 Windows clone 안에 없으면
아무 파일도 복사하거나 전역 설치하지 말고, 내가 새 작업으로 열 정확한 Windows 경로만 알려줘.
```

정상 경로는 보통 `C:\Users\<내계정>\Projects\boi-wiki-local`입니다. 새 Codex·Claude 작업에서 그 폴더를 열고 원래 요청을 다시 전달합니다. WSL 사본은 rollback 용도로 그대로 두며 자동 overlay나 양방향 동기화를 만들지 않습니다.

설치기가 “완전한 Windows clone이 아니다”라고 멈추면 누락된 Skill만 다른 위치에서 복사하지 않습니다. 배포 저장소를 다시 clone하거나 회사의 정상 update 절차로 복구합니다. 기존 `.env`가 다른 Local Profile을 가리킨다는 메시지가 나오면 설치기는 새 Profile이나 Inbox를 만들지 않으므로, 기존 사용자를 확인한 뒤 지원 채널에서 Profile 선택을 조정합니다.

## 원문 해시 검사가 실패합니다

잠긴 원문의 `boi-source` 구간이 수정됐다는 뜻입니다. 원본을 되돌리거나, 변경된 내용을 새 원문으로 다시 수집합니다. 해시 값만 새로 계산해 변경을 숨기지 않습니다.

## Obsidian에서 WSL 파일이 바로 안 보입니다

Windows Obsidian 1.12.7에서 WSL Vault를 연 실제 검증에서는 `EISDIR: illegal operation on a directory, watch` 오류가 발생했습니다. 재시작 후에도 같거나 Vault가 열리지 않으면 Obsidian 연동만 중단합니다. Local Second Brain 자체는 계속 사용할 수 있습니다.

문서 사본을 Windows 폴더에 자동 생성하거나 양방향 동기화를 임시로 붙이지 않습니다. Windows-native 저장소 또는 Linux/WSLg Obsidian으로 전환하려면 사용자가 저장 위치, 백업, 접근권한과 전환 범위를 먼저 결정해야 합니다.

연결하기 전에 AI에게 다음처럼 요청해 같은 문제를 차단할 수 있습니다.

```text
Windows Obsidian으로 이 Local Private 폴더를 열어도 안전한지 확인해줘.
WSL 경로나 파일 감시 문제가 예상되면 설정을 바꾸지 말고 중단 이유만 알려줘.
```

`blocked-verified`는 선택 기능을 건너뛰라는 결과이며 Local Second Brain 설치 실패가 아닙니다.

## 플러그인이 검색되지 않습니다

인터넷과 회사 정책, Restricted Mode 상태를 확인합니다. 비공식 zip 파일을 대신 설치하지 않습니다.

## MCP가 없으면 사용할 수 없나요?

아닙니다. MCP는 사내 BoI Wiki 검색·참조를 확장하는 선택 기능입니다. 로컬 수집, 정제, 검색, review, promotion 초안은 MCP 없이 동작합니다.

## Obsidian을 지우면 문서도 없어지나요?

아닙니다. 문서는 일반 Markdown 파일입니다. 다만 앱 삭제 전에 Vault가 외부 동기화 폴더가 아닌 Local Private 경로인지 확인합니다.

## 자동 Core 설정만 되돌리고 싶습니다

AI에게 `내가 수정한 설정과 Markdown은 보존하고, AI가 만든 Obsidian Core 설정만 되돌릴 대상을 먼저 보여줘`라고 요청합니다. AI가 생성한 설정으로 입증되지 않는 파일은 자동 제거하지 않습니다.

## 용어 정리

- OKF: BoI Markdown 문서의 기본 필드와 구조
- BoI Profile: 문서 종류와 공개 범위에 맞춘 메타데이터 규칙
- Local Private: 현재 사용자의 PC와 개인 디렉터리에만 있는 문서 범위
- Vault: Obsidian이 하나의 지식 공간으로 여는 폴더
- Promotion: Local Private 정제본을 검증과 승인 후 Team/Public 후보로 변환하는 과정

이전: [MCP와 Team·Public 공유](50-mcp-and-promotion.md) · 처음으로: [가이드 홈](00-start-here.md)
