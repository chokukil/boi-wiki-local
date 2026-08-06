---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "관리자용 Codex·Claude 자동 확인 계약"
description: "세션 시작·종료 확인, 설정 보존, 감사와 fallback을 검증하는 관리자 문서"
tags: [LocalPrivate, SecondBrain, Guide, Admin]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:agent-auto-check-admin
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
guide_audience: "배포 관리자와 문제 해결 담당자"
guide_duration_minutes: 10
guide_prerequisites: "Harness·Skill 구조와 에이전트 정책을 이해함"
guide_execution: "bootstrap, preferences, Skill fallback, 무화면 동작과 감사 경계를 검사"
guide_success: "별도 런타임 없이 두 에이전트가 같은 Local Private 계약을 수행함"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "80-admin-release-and-contract.md"
guide_boundary: "local-only"
source_refs:
  - type: local-guide-source
    ref: templates/second-brain-guide/81-agent-auto-check-admin.md
  - type: web
    ref: https://learn.chatgpt.com/docs/hooks
  - type: web
    ref: https://code.claude.com/docs/en/hooks
---

# 관리자용 Codex·Claude 자동 확인 계약

일반 사용자에게는 `AI 시작·종료 시 자동 확인`으로만 설명합니다. 구현 기준선은 `AGENTS.md`·`CLAUDE.md`의 짧은 bootstrap과 `boi-second-brain` Skill입니다.

## 기본 계층

- 외부 Python·Node 런타임 없음
- 상주 서비스와 OS 폴더 감시 없음
- 세션 시작: preferences를 읽고 `agent_session_check: true`일 때만 지정 폴더 상태 확인
- `explicit-only`: 시작·종료 자동 확인 없이 명시적 자연어 요청에만 동작
- 응답 종료 전: 장기 가치 판단과 기존 지식 비교
- 원시 transcript 기본 저장 안 함
- Local Private 원격 자동 업로드 안 함

Codex 또는 Claude가 프로젝트 로컬 hook을 지원하더라도 GitHub 기본 배포판에서는 별도 hook 설정 파일을 만들지 않습니다. 조직 정책으로 hook을 추가할 때도 기존 사용자 설정을 병합·보존하고, 신뢰 승인을 우회하지 않으며, 실행 실패 시 Harness·Skill 방식으로 돌아가야 합니다.

## 감사 항목

1. 사용자가 승인한 쉬운 설정 요약
2. 적용된 preset과 Local Profile
3. 원본 보존·transcript 미복사·원격 업로드 차단
4. 생성·보강·교정·확인 필요의 문서 이력
5. OKF 0.1 + BoI Profile 0.1-local 린트 결과

`plan hash`, manifest, JSON, hook 이벤트는 관리자 증적에만 표시합니다. 일반 사용자 화면에는 노출하지 않습니다.

다음: [배포와 BoI Wiki 계약 검증](80-admin-release-and-contract.md)
