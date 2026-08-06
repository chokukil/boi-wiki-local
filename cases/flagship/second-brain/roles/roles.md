# Logical roles — Flagship Second Brain

논리 역할은 직함이 아니라 검증 가능한 책임 경계입니다. Agent team이 없어도 같은 역할을 분리 pass로 수행하며, 각 역할의 `exit` 항목이 exit criteria입니다.

Reviewer: **privacy-reviewer**

## 1. source-curator

목적: 원본 bytes와 자료 provenance를 보존한 deterministic inventory를 만듭니다.

- 입력: 지정 source subset, fixture manifest
- 읽을 수 있음: raw source, source metadata
- 변경 가능: `intermediate/source-inventory.json`만
- 변경 금지: raw source와 기존 knowledge
- 산출물: path·size·SHA256·media type·duplicate group·support status
- handoff: knowledge-distiller와 privacy-reviewer
- exit: 모든 지정 source가 정확히 한 상태이며 before hash가 manifest와 일치
- hard fail: source 변경, 누락 source를 읽었다고 주장, file extension에서 도메인 결론 추론

## 2. memory-maintainer

목적: 새 파일을 만들기 전에 기존 topic과 history owner를 찾습니다.

- 입력: seed vault, processing checkpoint, source-curator inventory
- 읽을 수 있음: Local indexes, memory_key, links, review dates
- 변경 가능: `intermediate/knowledge-inventory.json`만
- 산출물: nearest topic, claim status, source coverage, completed/pending state
- handoff: knowledge-distiller
- exit: source마다 기존 owner 또는 “no suitable owner” 근거가 있음
- hard fail: 검색 없이 신규 생성, archive/history 삭제, 완료 source 재생성

## 3. knowledge-distiller

목적: evidence를 지식으로 복사하는 대신 기존 지식을 유지관리합니다.

- 입력: source inventory, knowledge inventory, user prompt
- 허용 operation: noop, append-evidence, revise, supersede, create, queue-review
- 산출물: `intermediate/consolidation-plan.json`, OKF Local pages, archive/checkpoint
- 필수 내용: observation·inference·counterevidence·unknown·human decision 분리
- handoff: grounded-query-analyst 또는 promotion compiler, privacy-reviewer
- exit: 모든 operation에 source hash와 reason이 있고 schema lint가 통과
- hard fail: raw transcript 저장, 충돌 자동 덮어쓰기, 누락 checklist 생성, agent-memory direct promotion

## 4. grounded-query-analyst

목적: compiled Wiki에서 시작해 source-backed 답을 만듭니다.

- 입력: reviewed/compiled pages와 명시적 source_refs
- 산출물: direct answer, supporting evidence, counterevidence, unknowns, next checks, confidence, exact citations
- citation: Local path + SHA256; remote BoI ID + revision + visibility
- handoff: privacy-reviewer
- exit: material claim citation coverage 100% 또는 명시적 insufficient result
- hard fail: model memory로 fixture 빈칸 보충, remote/local citation 혼합, reviewer 없는 확정 표현

## 5. privacy-reviewer — independent reviewer

목적: 생성자와 독립적으로 source·history·projection·사용자 경험을 교차검증합니다.

- 입력 순서: manifest → inventory → Local outputs → answer/projection → user summary
- 생성자의 결론을 첫 입력으로 사용하지 않음
- 산출물: assertion evidence, rubric dimension, pass/revise/block와 causal reason
- 필수 hard check: source integrity, OKF/BoI, local-private, remote activity 0, blocked type, projection leak, raw transcript
- 필수 quality check: duplicate decision, history preservation, counterevidence, unknowns, failure path, non-developer summary
- exit: 모든 assertion에 evidence locator가 있고 누락 evidence는 fail 처리
- independence: runtime 작성 역할과 evaluator/reviewer ID가 달라야 함

## 역할 충돌 규칙

- source-curator는 지식 결론을 승인하지 않습니다.
- knowledge-distiller는 자신의 결과를 reviewer pass로 승인하지 않습니다.
- grounded-query-analyst는 없는 evidence를 요청할 수 있지만 만들 수 없습니다.
- privacy-reviewer는 실패를 숨기기 위해 rubric 점수를 보정하지 않습니다.
- Single-agent라도 reviewer pass에서 intermediate conclusion을 입력으로 삼지 않고 source부터 다시 확인합니다.

다음: [Orchestrator](../orchestrator.md) · [Rubric](../evals/rubric.json)
