---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/dictionary-term
title: "Response Trend"
description: "품질 시스템 또는 설비 분석에서 시간에 따른 response 값을 비교해 이상 여부를 판단하는 현장 용어"
timestamp: 2026-06-23T09:00:00+09:00
employee_id: "0000000"
local_owner_ref: local-private:0000000
visibility: local-private
local_only: true
promotion_status: local_only
retention_class: working
retention_until: ""
archive_status: active
review_after: 2026-09-23
contains_sensitive: no
term: "Response Trend"
term_kind: concept
definition: "시간 순서로 수집된 response 값을 기준선, 최근 변화, 공정 조건과 비교해 이상 징후를 판단하는 분석 관점"
aliases:
  - response trend
  - 응답 트렌드
  - 반응 추세
domain: semiconductor-quality
examples:
  - "직개발 결과 확인에서 Response Trend가 기준선과 다르면 Map View와 함께 단면검사 필요성을 검토한다."
links:
  - ../action-drafts/quality-system-response-trend-action-draft.md
related_terms:
  - time-series-forecast
  - defect
  - metrology
source_refs:
  - type: local-example
    ref: ../usage-examples/natural-language-poc/dictionary-term-authoring.md
---

# Summary

Response Trend는 단일 측정값보다 시간에 따른 변화 방향과 패턴을 보는 용어다. Local Private에서는 개인 업무 맥락의 약어와 해석을 먼저 정리하고, Team/Public 공유가 필요하면 promotion draft로 승격한다.

# Usage

- 품질 시스템 response 데이터가 기준 대비 안정적인지 확인한다.
- 시계열 예측이나 이상탐지 action이 필요할 때 입력 evidence로 사용한다.
- Map View, 검사 결과, 설비 event와 함께 의사결정 근거로 기록한다.

# Related Links

- [Quality System Response Trend Action Draft](../action-drafts/quality-system-response-trend-action-draft.md)

# Citations

1. Local usage example: [Dictionary Term Authoring](../usage-examples/natural-language-poc/dictionary-term-authoring.md)
