---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "가설·지지 근거·반증 검토"
description: "조사 가설마다 supporting, contradicting, missing evidence를 분리한다."
tags: [second-brain, hypothesis, evidence, review]
timestamp: "{{timestamp}}"
boi_id: boi:private:{{employee_id}}:guide:hypothesis-evidence-review
visibility: local-private
classification: internal
owner: "{{employee_id}}"
employee_id: "{{employee_id}}"
local_owner_ref: local-private:{{employee_id}}
local_only: true
promotion_status: local_only
retention_class: reference
retention_until: ""
archive_status: active
artifact_visibility: reference
lifecycle_state: protected
memory_candidate: true
cleanup_policy: keep
review_after: "{{review_after}}"
contains_sensitive: false
guide_release: "3.1.0"
guide_audience: "원인 후보를 비교하고 검토하는 구성원과 reviewer"
guide_duration_minutes: 8
guide_prerequisites: "조사 질문과 출처가 있는 자료"
guide_execution: "가설마다 지지·반증·누락 근거와 다음 확인을 분리한다"
guide_success: "가설 상태와 남은 검증 조건이 실제 출처로 설명된다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "34-continuous-analysis-log.md"
guide_boundary: "local-only"
source_refs:
  - type: local-guide-source
    ref: templates/second-brain-guide/33-hypothesis-evidence-review.md
---

# 가설·지지 근거·반증 검토

조사·장애·품질·정책 비교처럼 하나의 설명으로 바로 결론 내리기 어려운 업무에 사용합니다.

~~~text
이 자료에서 가능한 가설을 분리하고, 각 가설의 지지 근거·반증·누락 자료·
다음 확인을 실제 출처와 함께 정리해줘. 근거가 부족한 가설은 확정하지 말고
Local Private 확인 필요 상태로 남겨줘.
~~~

- 같은 evidence가 어느 관계에서 지지이고 어느 관계에서 반증인지 주체를 명시합니다.
- 존재하지 않는 출처나 측정 결과를 모델 기억으로 채우지 않습니다.
- reviewed 결정과 새 경쟁 주장을 섞지 않고 현재 결론을 바꾸는지 표시합니다.
- 가설이 supported여도 확정 원인을 뜻하지 않습니다.
- 사람의 판정과 검토 일자를 별도로 기록합니다.

다음: [지속 분석 로그](34-continuous-analysis-log.md)
