---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-knowledge-note
title: "Knowledge reconciliation review - 2026-08-02"
description: "Conflict, staleness, and evidence review for SYN-SB-001-v1"
tags: [Synthetic, SecondBrainEval, ReviewRequired]
boi_id: boi:private:0000000:eval:reconciliation-review-2026-08-02
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
knowledge_role: reconciliation-review
claim_status: mixed-unverified
source_refs:
  - type: synthetic-fixture
    ref: sources/08-conflicting-review-day.md
  - type: synthetic-fixture
    ref: sources/11-research-note.md
  - type: synthetic-fixture
    ref: sources/13-onboarding-faq.md
  - type: synthetic-fixture
    ref: sources/15-incident-retrospective.md
generated_from:
  - type: local-comparison
    ref: data/boi/private/0000000/notes/knowledge/
---

# Knowledge reconciliation review

검토 기준일: 2026-08-02

## 처리 원칙

- 이 문서는 기존 지식을 덮어쓰는 결정문이 아니라 review_required 상태의 비교 기록이다.
- review-schedule.md의 reviewed 결정(매주 금요일 15:00)은 그대로 유지한다.
- 충돌한 주장은 둘 다 기록하되, 권위 있는 근거가 확인되기 전에는 새 주장으로 교체하거나 승격하지 않는다.
- agent-memory와 근거가 없는 결론은 직접 승격하지 않는다.
- 이번 검토에서는 기존 지식 문서의 본문, 상태, review_after를 변경하지 않았다.

## 요약

| ID | 분류 | 현재 판정 | 자동 반영 여부 |
|---|---|---|---|
| REV-01 | conflict / review_required | reviewed 금요일 15:00과 미검증 목요일 15:00이 충돌 | 반영 안 함; 금요일 결정 유지 |
| TERM-01 | status_mismatch / confirmation_required | “선호 용어 후보”와 “개정된 용어 결정”의 성숙도 표현이 다름 | 반영 안 함 |
| FAQ-01 | stale_downstream | 온보딩 FAQ가 검토 기한을 넘겼고 용어 결정 링크가 없음 | 날짜·내용 자동 갱신 안 함 |
| RES-01 | evidence_missing | 점진적 요약 주장에 실제 공개 출처가 없음 | 미검증 유지 |
| RES-02 | unsupported | 폴더 분류만으로 회상을 보장한다는 결론은 근거 없음 | 현재 종합에서 제외 |
| FAQ-02 | partially_supported | agent-memory 직접 승격 금지는 기존 메모와 일치하지만 원 근거를 확인할 수 없음 | 정책으로 승격 안 함 |
| FAQ-03 | unsupported_or_overbroad | Obsidian·MCP·충돌 보관에 관한 일반화에 권위 있는 정책 근거가 없음 | 운영 규칙으로 승격 안 함 |
| INC-01 | not_independently_verified | FAQ 사용 2회, 기여 요인, reminder 상태를 입증할 로그가 제공되지 않음 | 사실·근본 원인으로 확정 안 함 |

## 상세 비교와 다음 검증

### REV-01 — 지식 검토 요일 충돌

- 기존 reviewed 지식: review-schedule.md는 매주 금요일 15:00으로 기록한다.
- 보조 메모: agent-memory.md도 금요일 15:00 재확인을 말하지만 claim_status: inferred이고 직접 승격이 차단돼 있다.
- 상충 주장: sources/08-conflicting-review-day.md는 목요일 15:00이라고 하지만, 작성자를 알 수 없고 회의 링크나 결정 기록도 없다. 원문 자체도 reviewed 금요일 결정을 덮어쓰지 말라고 명시한다.
- 판정: 목요일 주장은 unverified conflict candidate이다. reviewed 금요일 결정을 변경할 근거가 아니다.
- 확인 필요: 일정 소유자 또는 결정권자가 실제 최신 요일을 확인해야 한다.
- 다음 검증:
  1. 기존 지식이 참조하는 sources/01-decision-chat.txt와 sources/10-review-day-reconfirmation.txt 원본을 확보해 작성자·시각·결정 문맥을 확인한다.
  2. 같은 기간의 공식 캘린더 초대나 회의 결정 기록에서 반복 일정과 변경 이력을 확인한다.
  3. 권위 있는 변경 결정이 확인된 경우에만 소유자 review를 거쳐 reviewed 지식과 downstream 문서를 함께 갱신한다.

### TERM-01 — 용어 상태와 downstream FAQ

- 기존 reviewed 지식: atlas-ledger.md는 “Atlas Ledger”를 preferred term candidate로 두고, 사전 소유자 검토 전까지 “Blue Ledger”를 별칭으로 유지한다.
- sources/15-incident-retrospective.md는 이를 revised terminology decision이라고 부른다.
- 판정: 두 문장은 용어 자체로 정면 충돌하지 않지만, 하나는 후보/검토 대기이고 다른 하나는 결정 완료처럼 표현해 상태가 일치하지 않는다.
- 확인 필요: 사전 소유자가 Atlas Ledger를 최종 승인했는지, Blue Ledger 별칭의 유지 기간이 정해졌는지 확인해야 한다.
- 다음 검증:
  1. atlas-ledger.md가 참조하지만 현재 제공 범위에 없는 sources/02-project-update.eml을 확보해 결정 주체와 승인 상태를 확인한다.
  2. 용어 사전 또는 결정 로그에서 canonical 명칭과 별칭 정책을 확인한다.
  3. 승인 상태가 확인된 뒤 FAQ가 연결할 canonical 문서를 정한다.

### FAQ-01 — 오래된 downstream 문서

- onboarding-faq.md의 review_after는 2026-07-31로, 기준일보다 이르다.
- sources/13-onboarding-faq.md에는 Atlas Ledger/Blue Ledger 결정으로 가는 링크가 없다.
- sources/15-incident-retrospective.md는 이 FAQ가 검토일 이후 두 번 사용됐다고 기록하고, 누락된 용어 링크를 기여 요인으로 지목한다.
- 판정: onboarding-faq.md와 그 원본 FAQ는 stale_downstream / review_required이다. 단, 사용 횟수와 인과관계는 회고의 진술일 뿐 현재 자료로 독립 검증되지 않았다.
- 확인 필요: FAQ 소유자가 네 답변과 용어 안내를 다시 검토하고, reminder 전달 여부를 확인해야 한다.
- 다음 검증:
  1. FAQ 사용 기록 또는 사건 티켓에서 검토일 이후 사용 2회를 확인한다.
  2. TERM-01 확인 후 canonical 용어 문서 링크를 추가한다.
  3. 아래 FAQ 주장들을 정책·권한 설정과 대조해 내용 검토를 마친 뒤에만 새 review_after를 부여한다. 날짜만 뒤로 미루지 않는다.
  4. 알림 시스템의 발송·전달 로그에서 reminder 전달 여부를 확인한다.

### RES-01/02 — 연구 메모의 근거 수준

- Claim A: “source layers가 보이는 점진적 요약은 이후 검색을 개선할 수 있다.” 메모에는 public source placeholder만 있고 실제 인용, 연구 조건, 측정값이 없다.
  - 판정: plausible but unverified; 모델의 기존 지식으로 빈 근거를 채우지 않는다.
  - 다음 검증: 실제 공개 출처를 연결하고, 원문이 같은 조건의 retrieval 개선을 뒷받침하는지 확인한 뒤 작은 검색 평가로 재현한다.
- Claim B: “folder taxonomies alone guarantee recall.” 보장 범위, 비교 기준, 출처가 없다.
  - 판정: unsupported; 현재 지식 종합과 추천에서 제외한다. “거짓으로 입증됨”으로 바꾸지는 않는다.
  - 다음 검증: 주장을 유지할 필요가 있다면 “보장” 대신 측정 가능한 가설로 다시 쓰고, taxonomy-only 기준선과 검색 성공률을 비교할 근거를 제시한다.

### FAQ-02/03 — 온보딩 답변별 근거

| FAQ 주장 | 비교 결과 | 확인 필요와 다음 검증 |
|---|---|---|
| Obsidian은 필수가 아니며 Markdown과 AI agent면 충분하다 | 제공 자료에 충분성의 범위, 요구사항, 실험 근거가 없다. unsupported | 지원 대상 워크플로와 필수 기능을 정의하고 도구 비종속성 정책 또는 호환성 시험으로 확인 |
| MCP read connectivity는 Local Private 파일 업로드 권한을 주지 않는다 | seed.json의 remote_enabled: false와 기존 문서의 local_only: true는 이 fixture의 원격 비활성 상태만 뒷받침한다. 모든 MCP의 실제 권한을 증명하지는 않는다. overbroad | 해당 connector의 capability/permission 설정과 업로드 경로를 점검하고 fixture 범위의 문장으로 한정 |
| agent-memory는 직접 승격할 수 없고 eligible BoI type으로 정제·검토해야 한다 | agent-memory.md의 “directly promotion-blocked”와 일치한다. 다만 eligible type 절차의 정책 근거와 참조 원본이 제공되지 않았다. partially_supported | sources/10-review-day-reconfirmation.txt와 승격 정책을 확인하고, 정제 산출물의 reviewer를 지정 |
| 충돌은 두 주장을 보존한 review-required Local 상태에 둔다 | sources/08-conflicting-review-day.md의 보존 지시 및 기존 local-only 관행과 일치하지만 권위 있는 보관 정책은 없다. provisional | 충돌 처리 정책과 상태 전이 규칙을 확인하고, REV-01을 실제 사례로 검증 |

### INC-01 — 사건 회고의 관찰·인과·결정 분리

- 보고된 관찰: 오래된 FAQ가 검토일 이후 두 번 사용됐다. 현재 자료에는 사용 로그나 사건 식별자가 없어 not independently verified로 둔다.
- 인과 주장: 누락된 용어 링크는 기여 요인으로 기록됐지만, 단독 또는 근본 원인으로 입증되지는 않았다.
- 반대 근거: 새 용어를 직접 검색했을 때는 검색이 성공했다. 따라서 제공 자료만으로 “검색 실패가 근본 원인”이라고 결론내리면 안 된다.
- 미확인: reminder 전달 여부는 알 수 없다. 전달 실패로 단정하지 않는다.
- 기록된 조치: 링크와 review date를 수리한다. 다만 TERM-01 및 FAQ 내용 검토가 끝나기 전에는 링크 대상이나 날짜를 자동 변경하지 않는다.
- 다음 검증: FAQ 진입 경로를 재현하고 직접 검색 경로와 비교한 뒤, 사용 로그·검색 로그·알림 전달 로그를 같은 사건 시간대 기준으로 대조한다.

## 출처 및 추적성 공백

- 기존 지식의 source_refs가 가리키는 sources/01-decision-chat.txt, sources/02-project-update.eml, sources/10-review-day-reconfirmation.txt는 현재 제공된 작업공간에 없다. 따라서 해당 reviewed/inferred 주장의 원 출처 내용과 해시는 이번 검토에서 재확인하지 못했다.
- sources/11-research-note.md와 sources/15-incident-retrospective.md에는 외부 인용, 로그, 사건 식별자가 없다.
- 이 공백들이 해소될 때까지 본 문서와 미검증 주장은 Local review_required로 유지하고 promotion하지 않는다.
