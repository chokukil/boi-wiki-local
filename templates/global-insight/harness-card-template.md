---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "SK하이닉스 Global Insight Meta Harness"
description: "공개 자료와 승인된 Local 자료에서 claim 변화를 추적하고 현재 지식을 재사용하는 반복 운영체계"
tags: [LocalPrivate, MetaHarness, ConfiguredHarness, GlobalInsight]
timestamp: "{{timestamp}}"
boi_id: boi:private:{{employee_id}}:harness:sk-hynix-global-insight
visibility: local-private
classification: internal
owner: "{{employee_id}}"
employee_id: "{{employee_id}}"
local_owner_ref: local-private:{{employee_id}}
local_only: true
promotion_status: local_only
retention_class: working
archive_status: active
artifact_visibility: working
lifecycle_state: working
memory_candidate: true
cleanup_policy: keep
review_after: "{{review_after}}"
contains_sensitive: unknown
source_refs:
  - type: local-document
    ref: "{{approved_request_capture_path}}"
    sha256: "{{capture_sha256}}"
generated_from:
  - type: local-document
    ref: "{{approved_request_capture_path}}"
    sha256: "{{capture_sha256}}"
---

# SK하이닉스 Global Insight Meta Harness

이 파일은 실제 `0000000`이 아닌 7자리 Local Profile에서만 materialize합니다. 승인 원문 capture의 exact SHA256이 없으면 생성하지 않습니다. 이 개인 설정 카드는 직접 promotion할 수 없습니다.

## 실행 계약

- 사용자 인터페이스: Capture, Update, Query, DeepResearch, Health, Review, Promote
- 기본 결과: change set과 review queue
- Golden Journey: SK하이닉스 Agentic AI Change Radar
- 후속 Case: FAB Logistics Digital Twin, Scientific Foundation Model Knowledge
- 실행 모드: Full, Reduced, Single-agent, No-team fallback
- 원격 기본값: 비활성

## 다음 세션 요청

```text
저장된 SK하이닉스 Global Insight Meta Harness를 불러와 이번 자료를 처리해줘. 기존 claim과 source hash를 먼저 확인하고, 보고서 대신 변경 세트와 검토 목록을 보여줘.
```

상세 수명주기와 artifact 계약은 저장소의 `templates/global-insight/`와 해당 Case package를 따릅니다.
