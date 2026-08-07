# FAB Logistics Digital Twin

상태: **Community — deterministic public source records 5개, Codex baseline contract 실행 1건, production benchmark 0/60**

Case type: `strategy-case`
기본 검토 주기: 월간 또는 SEMI·vendor 공식 변경 시

## 한 문장으로 시작

```text
SEMI GEM300 공개 자료와 제조·물류 Digital Twin, Palantir식 Object·Link·Action을 연결해 FAB 물류 적용 가설과 검증 질문을 만들어줘. 내부 운영 조건은 추정하지 마.
```

## Trigger boundary

- 실행: Carrier·Substrate·Control Job과 물류 twin·ontology의 연결고리를 검토할 때
- Near-miss: 유료 SEMI 전문 내용을 추정, 실제 FAB 성능 수치 생성, 운영 Action 실행 또는 특정 벤더 선정
- 기본 결과: 주문형 보고서가 아니라 change set, review queue 또는 현재 지식 기반 답변

## 검증 입력

Fixture `PUB-FAB-DT-001-v1`는 공개 1차 자료의 확인 범위와 SHA256을 고정한 source record 5개입니다. 원문 전체 복제본이 아닙니다.

[Fixture 설명](fixtures/fixture.md) · [source pack](fixtures/source-pack.md) · [manifest](fixtures/manifest.json)

공개 fixture를 대상으로 고정 Query, evidence·counterevidence·unknown, review handoff와 privacy 경계를 실행한 [baseline contract validation](contract-validation/README.md)이 있습니다. 이는 실제 FAB domain validation이 아닙니다.

## Orchestration

Pattern: `public standards boundary → twin capability map → ontology mapping → pilot hypothesis → independent review`

5개 논리 역할 중 마지막 역할이 Independent Reviewer입니다. On-demand Synthesizer는 승인된 durable knowledge에서 요청된 brief·표·제안만 만드는 선택 pass이며 claim 상태를 변경하지 않습니다.

[역할과 hard fail](roles/roles.md) · [Dependency DAG](orchestrator.md) · [output contract](expected/OUTPUT-CONTRACT.md)

## 정상 결과

GEM300의 Carrier·Substrate·Control Job 공개 개념을 twin 상태·event와 연결하고 Object·Link·Action 후보를 만들되, 실제 FAB 데이터 매핑과 효과는 unknown 및 내부 검증 항목으로 남긴다.

## Second Brain 연결 — 선택

- Second Brain이 없어도 현재 실행, review queue와 promotion preview까지 완료됩니다.
- 연결하면 검토된 durable knowledge만 기존 주제와 비교해 보강·교정하고 다음 Query와 Update에 재사용합니다.
- raw source, intermediate와 agent-memory는 기억으로 복사하거나 직접 promotion하지 않습니다.
- 사용자 용어로 기준 지식, 업데이트 후보, 현재 지식과 이후 revision을 운영하는 방법은 [지식 변화 운영과 사용자 프롬프트 가이드](https://github.com/chokukil/boi-wiki-local/blob/main/templates/second-brain-guide/38-knowledge-change-operations.md)를 참고합니다.

## Local/Remote 경계

- promotion 가능: 검토된 개념 map과 내부 검증 전제의 pilot proposal candidate
- 직접 promotion 차단: 유료 표준 본문, 추정한 FAB 수치, raw internal data, 실행 가능한 운영 Action
- MCP read와 agent runtime 사용은 remote upload 승인이 아님
- reviewer, target scope, sanitized exact hash와 별도 승인 전 remote submit 없음

이 Case는 아직 Verified, Reference 또는 production-ready를 주장하지 않습니다.
