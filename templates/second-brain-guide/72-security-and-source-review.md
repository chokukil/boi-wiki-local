---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "민감정보·출처·공개 범위 검토"
description: "Promotion과 PR 전에 수행하는 최소 보안 검토"
tags: [Security, Source, Classification, Promotion]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:security-review
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
guide_audience: "promotion 작성자와 reviewer"
guide_duration_minutes: 10
guide_prerequisites: "promotion preview"
guide_execution: "민감정보, 출처, 공개 범위, reviewer, exact hash를 검토한다"
guide_success: "승인할 정확한 후보와 차단 사유가 명확하다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "80-admin-release-and-contract.md"
guide_boundary: "promotion-preview-only"
source_refs:
  - type: local-guide-source
    ref: templates/second-brain-guide/72-security-and-source-review.md
---

# 민감정보·출처·공개 범위 검토

대상은 promotion 작성자, reviewer, PR 기여자이며 후보당 5~15분이 걸립니다. 분류 정책과 target scope를 알아야 합니다.

## 검토 단계

1. 사번, 로컬 경로, 토큰, 인증정보, 개인정보, 미공개 업무정보를 찾습니다.
2. 각 주장에 Team/Public에서 접근 가능한 구조화 출처 `{type, ref, note}`가 있는지 확인합니다.
3. Team은 team ID와 reviewer, Public은 외부 공개 가능한 표현과 출처를 추가 확인합니다.
4. authenticated principal이 owner가 되고 ACL은 target scope에서 원격 생성되는지 확인합니다.
5. preview의 exact candidate hash와 승인 대상이 같은지 확인합니다.
6. Local case ID가 제목·설명·본문에 남았다면 AI에게 공유용 제목·설명·본문에서 제거하도록 요청하고 새 hash를 검토합니다.

## 정상 결과와 실패 시 이동

하나라도 불확실하면 Local에 유지하는 것이 정상적인 실패 처리입니다. 오류를 숨기거나 classification을 낮추지 않습니다. 지원 요청에는 민감 원문 대신 오류 코드와 재현 가능한 비민감 예시를 사용합니다.

## 사용 로그와 telemetry

BoI Wiki Local은 사용자 행동 telemetry나 analytics를 전송하지 않습니다. `data/boi/log.md`는 사용 빈도나 화면 행동이 아니라 사용자가 생성·정제·promotion한 문서 변경을 추적하는 Local Private 지식 이력입니다. 자동 acceptance는 임시 workspace에서 실행되고 종료 시 제거됩니다.

## AI 처리와 BoI Wiki 적재는 다릅니다

`Local Private`는 자료가 BoI Wiki·MCP·Team/Public로 자동 적재되지 않는다는 뜻입니다. Codex·Claude로 자료를 정리하면 선택한 자료는 회사가 승인한 AI 서비스 정책에 따라 모델 문맥에서 처리될 수 있습니다. 민감한 업무 자료는 승인된 사내 AI 런타임에서만 다루고, 개인용·미승인 AI 서비스에는 넣지 않습니다. 평가 결과도 AI가 처리한 입력 byte와 BoI Wiki·MCP로 보낸 byte를 분리해 기록합니다. 실제 대상 BoI Wiki validator와 release 검사는 [관리자 호환 점검](80-admin-release-and-contract.md)에서 수행하며 일반 사용자가 Python을 실행할 필요는 없습니다.

## Local/Remote 경계와 다음 여정

Local 경로·사번·Local `boi_id`·원문은 remote projection에 들어가면 안 됩니다. 다음: [관리자 호환 점검](80-admin-release-and-contract.md)
