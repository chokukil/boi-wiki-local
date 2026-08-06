# SK하이닉스 Agentic AI Change Radar

상태: **Community — deterministic public source records 6개, 실제 runtime evidence 미수집**

Case type: `golden-journey`
기본 검토 주기: 주간 또는 사용자가 요청할 때

## 한 문장으로 시작

```text
이번 주 Agentic AI runtime, orchestration, tool use, memory·context, evaluation과 security에서 바뀐 내용만 기존 지식과 비교해 변경 세트와 검토 목록으로 보여줘.
```

## Trigger boundary

- 실행: 기존 claim snapshot과 새 공개 자료를 비교해 변화만 반영 후보로 만들 때
- Near-miss: URL 하나의 단순 요약, 무승인 최신 외부 조사, 주문하지 않은 주간 보고서 생성
- 기본 결과: 주문형 보고서가 아니라 change set, review queue 또는 현재 지식 기반 답변

## 검증 입력

Fixture `PUB-AAI-RADAR-001-v1`는 공개 1차 자료의 확인 범위와 SHA256을 고정한 source record 6개입니다. 원문 전체 복제본이 아닙니다.

[Fixture 설명](fixtures/fixture.md) · [source pack](fixtures/source-pack.md) · [manifest](fixtures/manifest.json)

## Orchestration

Pattern: `route and scope → source capture → evidence comparison → delta curation → independent review`

5개 논리 역할 중 마지막 역할이 Independent Reviewer입니다. On-demand Synthesizer는 승인된 durable knowledge에서 요청된 brief·표·제안만 만드는 선택 pass이며 claim 상태를 변경하지 않습니다.

[역할과 hard fail](roles/roles.md) · [Dependency DAG](orchestrator.md) · [output contract](expected/OUTPUT-CONTRACT.md)

## 정상 결과

T0→T1에서 TypeScript 지원은 stale/revised, MCP discovery는 contradicted/revised, 평가 도구는 strengthened, Agent Builder는 new, SK하이닉스 적용성은 unknown으로 남는다.

## Second Brain 연결 — 선택

- Second Brain이 없어도 현재 실행, review queue와 promotion preview까지 완료됩니다.
- 연결하면 검토된 durable knowledge만 기존 주제와 비교해 보강·교정하고 다음 Query와 Update에 재사용합니다.
- raw source, intermediate와 agent-memory는 기억으로 복사하거나 직접 promotion하지 않습니다.

## Local/Remote 경계

- promotion 가능: 사람이 검토한 정제 지식과 주문된 sanitized brief candidate
- 직접 promotion 차단: raw source, evidence, hypothesis, analysis log, agent memory, 개인 Harness card
- MCP read와 agent runtime 사용은 remote upload 승인이 아님
- reviewer, target scope, sanitized exact hash와 별도 승인 전 remote submit 없음

이 Case는 아직 Verified, Reference 또는 production-ready를 주장하지 않습니다.

## Golden Journey oracle

[T0 baseline snapshot](expected/t0-snapshot.md) · [T1 expected change set](expected/t1-change-set.md) · [expected review queue](expected/review-queue.md)
