---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-sop-draft
title: "직개발 결과 확인 및 Reporting SOP 초안"
description: "SOP 이미지에서 추출한 직개발 결과 확인 및 Reporting 절차의 BoI Wiki 초안"
timestamp: 2026-06-20T22:02:00+09:00
employee_id: "0000000"
local_owner_ref: local-private:0000000
visibility: local-private
local_only: true
promotion_status: local_only
retention_class: working
retention_until: ""
archive_status: active
review_after: 2026-07-20
contains_sensitive: no
source_refs:
  - type: image
    ref: ../usage-examples/natural-language-poc/evidence/sop_sample_image.png
---

# Summary

`직개발 결과 확인 및 Reporting` SOP는 DRAM Tech-A 직개발 결과를 확인하고, 단면검사 필요 여부를 판단한 뒤, 결과를 reporting 및 협의체 공유까지 연결하는 절차다.

# Extracted Metadata

| 항목 | 값 |
|---|---|
| Product | DRAM |
| Tech | Tech-A |
| Work ID | 1.10 |
| 수행 조직 | 공정 |
| TAT 개선 | 16.5h -> 9.2h |
| TAT 절감 | 7.3h |

# SOP Stages

| No | Stage | System | Actor | TAT | Automation status |
|---|---|---|---|---|---|
| 1 | Response Trend 확인 | 품질 시스템 | AI 보조 | 2h -> 0.5h | candidate AI action |
| 2 | Map View Image 확인 | Map 분석 시스템 | 사람 + AI | 2h -> 1h | candidate vision/action |
| D1 | 단면검사 필요 여부 판단 | Manual | 사람 | 1h | manual decision |
| 3 | 단면검사 Wafer 대응 검토 | Manual | 사람 | 1h | manual action |
| 4 | 단면검사 의뢰서 작성 및 검사용 Wafer 전달 | 단면 검사 시스템 | 사람 | 2h | candidate system action |
| 6 | 단면검사 요청 | Manual | 사람 + AI | 2h -> 1h | manual + AI draft |
| 5 | 단면검사 결과 확인 | 단면 검사 시스템 | 사람 | 2h | candidate system action |
| 7 | 연구소-양산 FAB 비교 Trend 확인 | 품질 시스템 | AI 보조 | 2h -> 0.5h | candidate AI action |
| 8 | 직개발 결과 Reporting | Manual | AI 자동화 | 2h -> 0.1h | candidate Langflow/report action |
| 9 | 직개발 결과 협의체 공유 | 메신저 | AI 자동화 | 0.5h -> 0.1h | candidate messenger action |

# Action Gaps

| Stage | Current classification | Reuse or gap |
|---|---|---|
| Response Trend 확인 | missing system action | `sop.equipment.request_trend_history` 패턴 재사용 가능 |
| Map View Image 확인 | missing system action | Map 분석 시스템 connector 필요 |
| 단면검사 Wafer 대응 검토 | manual action | 사람이 판단하고 완료 event를 발행 |
| 단면검사 의뢰/결과 확인 | missing system action | 단면 검사 시스템 connector 필요 |
| Reporting | AI action candidate | Langflow harness로 report draft 생성 가능 |
| 협의체 공유 | missing system action | 메신저 connector 필요 |

# Completion Criteria

- stage별 evidence source가 남아 있다.
- 사람 승인 단계와 AI/action 단계가 분리되어 있다.
- 없는 action은 없는 것으로 표시하고, candidate draft로만 남긴다.
- Public 공유 전 promotion preflight를 통과한다.
