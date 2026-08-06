---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "근거 기반으로 질문하고 답을 검증하기"
description: "정제된 Wiki를 먼저 읽고 원본 evidence로 검증하는 답변 순서와 품질 계약을 익힌다."
tags: [second-brain, query, provenance, answer-quality]
timestamp: "{{timestamp}}"
boi_id: boi:private:{{employee_id}}:guide:grounded-query
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
guide_release: "3.0.0"
guide_audience: "Second Brain에 질문하고 출처까지 검증하려는 모든 구성원"
guide_duration_minutes: 8
guide_prerequisites: "정제 문서와 evidence가 연결된 Local Case 또는 지식 문서"
guide_execution: "query-pack의 읽기 순서와 답변 계약에 따라 정제 Wiki, 지지 근거, 반증, 미확인 항목을 함께 확인한다"
guide_success: "답변의 각 주장에 Local 문서 경로와 SHA256이 있고 관찰·추론·사람의 판정이 구분된다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "35-recurrence-fingerprint.md"
guide_boundary: "local-with-optional-mcp-read"
source_refs:
  - type: local-guide-source
    ref: templates/second-brain-guide/37-grounded-query.md
---

# 근거 기반으로 질문하고 답을 검증하기

Second Brain의 품질은 파일 개수나 Graph 모양이 아니라, 질문했을 때 **정제된 판단을 먼저 찾고 원본 evidence와 반증까지 추적할 수 있는가**로 판단합니다. BoI Wiki Local의 `query-pack`은 관련 파일을 한꺼번에 던지는 대신 다음 순서를 만듭니다.

```text
질문 의도 판별
→ decision·hypothesis·fingerprint 등 정제된 Wiki 우선
→ source_refs·supports·contradicts를 따라 evidence 확장
→ 직접 답변·지지 근거·반증·미확인·다음 확인·신뢰도·인용으로 답변
```

## 1. 질문 패키지 만들기

```text
내 Second Brain에서 이 질문과 관련된 검토된 지식을 먼저 찾고,
지지 근거·반증·미확인 항목·다음 확인·신뢰도·Local 출처를 분리해 답해줘.
```

정상 결과에는 다음이 분리되어 나타납니다.

- `compiled_sources`: decision record, hypothesis, fingerprint 같은 정제 Wiki
- `evidence_sources`: 정제 문서가 실제로 참조한 불변 evidence
- `read_order`: 답을 만들 때 읽을 순서
- `answer_contract`: 답변에 반드시 들어갈 일곱 항목
- 각 인용의 현재 `sha256`: 답변 이후 원문이 바뀌지 않았는지 확인하는 값

`compiled_sources`가 비어 있는데 raw evidence만 많다면 바로 결론을 만들지 않습니다. 먼저 [Capture에서 지식까지](23-capture-distill-review.md) 또는 [범용 Investigation Pattern](29-investigation-pattern.md)으로 돌아가 정제 문서를 만듭니다.

## 2. 답변의 일곱 항목

답변은 다음 형식을 지킵니다.

1. `direct_answer`: 한두 문장으로 현재 답을 말합니다.
2. `supporting_evidence`: 어떤 evidence가 어느 가설이나 판정을 지지하는지 씁니다.
3. `counterevidence`: 반증이나 경쟁 가설에 유리한 자료를 숨기지 않습니다.
4. `unknowns_and_limits`: 누락 trace, 제한된 표본, 아직 하지 않은 시험을 씁니다.
5. `next_checks`: 불확실성을 줄일 사람이 수행할 확인을 씁니다.
6. `confidence`: `low`, `medium`, `high` 중 하나와 이유를 씁니다.
7. `citations`: Local 경로와 exact SHA256을 붙입니다. MCP 자료라면 canonical BoI ID·revision·visibility를 씁니다.

정제 Wiki가 `검토된 결정`이라고 말한 범위를 넘어서 확정하지 않습니다. 경쟁 주장이나 반증이 있으면 현재 결론을 바꾸는지, 아직 미검증인지 구분하고 다음 확인 조건을 함께 제시합니다.

## 3. 답변이 자료를 넘어서지 않았는지 확인하기

다음이면 답변을 저장하거나 공유하지 않습니다.

- 인용이 실제 `query-pack`에 없거나 SHA256이 다름
- 지지·반증 관계의 주체가 사라져 어느 가설의 자료인지 알 수 없음
- `supported contributor`를 `confirmed root cause`로 바꿈
- 사람이 내린 판정을 측정된 관찰처럼 표현함
- 자료가 부족한데 모델 기억이나 일반 상식으로 빈칸을 채움

자료가 부족하면 “현재 Local Wiki만으로는 답할 수 없음”이라고 쓰고, 필요한 intake·distill·review를 `next_checks`로 제안하는 것이 정상 동작입니다.

## 4. 배포판의 질문 품질 회귀 검사

관리자·CI 회귀 검사는 정제 문서가 먼저 검색되는지, 필요한 지지·반증 evidence가 포함되는지, 인용 hash가 현재 파일과 같은지, 과도한 확정 표현이 없는지를 별도로 확인합니다. 일반 사용자는 Python 도구를 실행할 필요가 없습니다.

이 점수는 사용자의 실제 업무 문서가 자동으로 좋은 품질이라는 뜻은 아닙니다. 실제 문서는 source relationship, 정제 수준, review 상태를 [일간·주간 검토](24-daily-weekly-review.md)에서 별도로 확인해야 합니다.

## 정상 결과와 Local/Remote 경계

질문은 Local Private 정제 Wiki와 evidence를 근거로 재현 가능한 답을 만들며, 단순 MCP 조회만으로 Local 문서가 원격에 올라가지 않습니다. 답을 조직지식으로 공유하려면 검토된 `boi/local-knowledge`, context pack 또는 SOP로 정제한 뒤 [Team/Public promotion preview](50-mcp-and-promotion.md)를 거쳐야 합니다.

이전: [지속 분석 로그와 인수인계](34-continuous-analysis-log.md) · 다음: [재발 fingerprint](35-recurrence-fingerprint.md)
