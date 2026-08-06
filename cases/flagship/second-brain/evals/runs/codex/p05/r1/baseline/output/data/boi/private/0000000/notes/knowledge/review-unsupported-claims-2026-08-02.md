---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-knowledge-note
title: "Independent review - unsupported claims"
description: "Approved Local Private review of unsupported and insufficiently evidenced claims"
tags: [Synthetic, SecondBrainEval, ReviewRequired, Unsupported]
boi_id: boi:private:0000000:eval:review-unsupported-claims-2026-08-02
visibility: local-private
classification: internal
owner: "0000000"
employee_id: "0000000"
local_owner_ref: local-private:0000000
local_only: true
promotion_status: blocked_pending_review
artifact_visibility: memory
lifecycle_state: review_required
archive_status: active
review_after: 2026-08-09
contains_sensitive: false
knowledge_role: evidence-review
claim_status: mixed-unverified
approval_scope: local-private-only
change_confirmation_sha256: "39f96600e65ce85f3c394dd5332216764d125650222cd5521ed150579f01f3de"
change_confirmation_status: matched
source_hash_verification: matched
remote_upload: false
source_refs:
  - type: synthetic-fixture
    ref: sources/11-research-note.md
    sha256: ee2faef63c53eb1b0f37834ccd55f756d27e4db542b6bad86e57cf92effb43c5
  - type: synthetic-fixture
    ref: sources/13-onboarding-faq.md
    sha256: 69cb0bc9c07a8bcf74cff589aa60e369a7800ab26f9ac78a0c6f7fefd5f485bf
  - type: synthetic-fixture
    ref: sources/15-incident-retrospective.md
    sha256: e0f7c994becf1125cbef6f670670564b95384ac591fffbe9e851315ae6e41e1e
comparison_refs:
  - ref: data/boi/private/0000000/seed.json
    sha256: 8614eca74f6c6d937e483cd75646537c4582b55473bcb6ba6fad0c218d6bd2d8
  - ref: data/boi/private/0000000/notes/knowledge/agent-memory.md
    sha256: 2597568afdf5262ab0aff5f522dc8285cbc638744bc36dc8fd83267c99cba5be
---

# 근거 없는 주장 독립 검토

검토 기준일: 2026-08-02

## 승인 및 무결성 확인

- 승인 범위는 방금 미리보기한 Local Private 변경에 한정된다.
- 세 독립 문서가 같은 change_confirmation_sha256을 사용한다.
- source_refs와 comparison_refs의 SHA-256은 기록 직전에 일치함을 확인했다.
- 이 문서의 판정은 원문 수정이나 reviewed 지식 승격을 승인하지 않는다. 원격 업로드도 수행하지 않는다.

## 주장별 판정

| ID | 주장 | 판정 | 이유 |
|---|---|---|---|
| UNSUP-01 | source layers가 보이는 progressive summarization은 이후 retrieval을 개선할 수 있다 | evidence_missing / unverified | public source placeholder만 있고 실제 인용, 조건, 측정값이 없음 |
| UNSUP-02 | folder taxonomies alone guarantee recall | unsupported | 보장 범위, 비교 기준, 인용이 없음 |
| UNSUP-03 | Obsidian은 필요 없고 Markdown과 AI agent면 충분하다 | unsupported | 충분성의 범위와 요구사항, 정책 또는 시험 근거가 없음 |
| UNSUP-04 | MCP read connectivity는 Local Private 파일을 업로드하지 않는다 | overbroad | remote_enabled: false와 local_only는 현재 fixture 상태만 보이며 모든 connector 권한을 증명하지 않음 |
| UNSUP-05 | agent-memory는 eligible BoI type으로 정제·검토해야만 승격할 수 있다 | partially_supported | agent-memory.md의 directly promotion-blocked와 일치하지만 eligible type 절차의 정책 근거가 없음 |
| UNSUP-06 | 충돌은 두 주장을 보존한 review-required Local 상태에 둔다 | provisional | 상충 source의 지시 및 local-only 관행과 일치하지만 권위 있는 상태 전이 정책이 없음 |
| UNSUP-07 | 오래된 FAQ가 검토일 뒤 두 번 사용됐다 | reported_not_verified | 사용 로그나 사건 식별자가 없음 |
| UNSUP-08 | 용어 링크 누락이 사건의 기여 요인이다 | causal_claim_unverified | 회고의 결론 외에 경로 비교나 행동 증거가 없음 |
| UNSUP-09 | 검색 실패가 사건의 근본 원인이다 | contradicted_by_provided_counterevidence | 직접 검색에서는 새 용어가 반환됐으므로 이 결론을 채택하면 안 됨 |
| UNSUP-10 | reminder가 전달되지 않았다 | unknown | 원문이 전달 여부를 unknown으로 명시함 |

## 처리 결정

- UNSUP-02는 현재 지식 종합과 추천에서 제외한다. 단, 거짓으로 입증됐다고 바꾸지 않는다.
- UNSUP-09는 제공된 반대 근거 때문에 근본 원인 결론으로 사용하지 않는다.
- 나머지는 Local review_required 또는 provisional 상태로 유지하며 모델의 기존 지식으로 빈 근거를 채우지 않는다.
- 기존 source, reviewed 지식, FAQ, incident retrospective는 변경하지 않는다.

## 다음 검증

1. UNSUP-01: 실제 공개 출처를 연결하고 같은 조건의 retrieval 효과인지 확인한 뒤 소규모 검색 평가로 재현한다.
2. UNSUP-02: 유지할 필요가 있다면 guarantee를 측정 가능한 가설로 바꾸고 taxonomy-only 기준선과 검색 성공률을 비교한다.
3. UNSUP-03: 지원할 워크플로와 필수 기능을 정의한 뒤 도구 비종속성 정책 또는 호환성 시험으로 검증한다.
4. UNSUP-04: 해당 connector의 capability, permission, upload path를 직접 점검하고 문장을 fixture 범위로 제한한다.
5. UNSUP-05/06: promotion 및 conflict-state 정책 원문과 reviewer 책임을 확인한다.
6. UNSUP-07/08/10: 사용 기록, 사건 티켓, FAQ 진입 경로, 검색 로그, 알림 발송·전달 로그를 동일 시간대 기준으로 대조한다.
