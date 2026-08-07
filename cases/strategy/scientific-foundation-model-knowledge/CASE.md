# Scientific Foundation Model Knowledge

상태: **Community — deterministic public source records 5개, Codex baseline contract 실행 1건, production benchmark 0/60**

Case type: `long-term-knowledge-case`
기본 검토 주기: 분기 또는 정정·철회·반례·중요 후속 연구 발생 시

## 한 문장으로 시작

```text
Scientific Foundation Model 자료를 법칙·가정·prediction·재현·반례·철회 상태로 정리하고, 시간이 지나도 유지할 지식과 다시 검토할 주장을 구분해줘.
```

## Trigger boundary

- 실행: 논문과 후속 연구에서 물리·화학적 grounding과 실제 prediction evidence를 장기 비교할 때
- Near-miss: 논문 초록만으로 full-text 검증 주장, 벤치마크를 보편 법칙 준수로 확대, 변화 없는 지식의 주기적 재작성
- 기본 결과: 주문형 보고서가 아니라 change set, review queue 또는 현재 지식 기반 답변

## 검증 입력

Fixture `PUB-SFM-001-v1`는 공개 1차 자료의 확인 범위와 SHA256을 고정한 source record 5개입니다. 원문 전체 복제본이 아닙니다.

[Fixture 설명](fixtures/fixture.md) · [source pack](fixtures/source-pack.md) · [manifest](fixtures/manifest.json)

공개 fixture를 대상으로 고정 Query, evidence·counterevidence·unknown, review handoff와 privacy 경계를 실행한 [baseline contract validation](contract-validation/README.md)이 있습니다. 이는 독립 scientific review나 재현 evidence가 아닙니다.

## Orchestration

Pattern: `paper integrity → claim and assumption extraction → prediction/reproduction matrix → change curation → independent review`

5개 논리 역할 중 마지막 역할이 Independent Reviewer입니다. On-demand Synthesizer는 승인된 durable knowledge에서 요청된 brief·표·제안만 만드는 선택 pass이며 claim 상태를 변경하지 않습니다.

[역할과 hard fail](roles/roles.md) · [Dependency DAG](orchestrator.md) · [output contract](expected/OUTPUT-CONTRACT.md)

## 정상 결과

MatterGen·GraphCast·physics-guided models의 서로 다른 prediction evidence를 보존하고, 법칙 준수·generalization·재현 여부를 같은 것으로 취급하지 않으며 불확실성은 unknown으로 남긴다.

## Second Brain 연결 — 선택

- Second Brain이 없어도 현재 실행, review queue와 promotion preview까지 완료됩니다.
- 연결하면 검토된 durable knowledge만 기존 주제와 비교해 보강·교정하고 다음 Query와 Update에 재사용합니다.
- raw source, intermediate와 agent-memory는 기억으로 복사하거나 직접 promotion하지 않습니다.
- 사용자 용어로 기준 지식, 업데이트 후보, 현재 지식과 이후 revision을 운영하는 방법은 [지식 변화 운영과 사용자 프롬프트 가이드](https://github.com/chokukil/boi-wiki-local/blob/main/templates/second-brain-guide/38-knowledge-change-operations.md)를 참고합니다.

## Local/Remote 경계

- promotion 가능: 검토된 scientific claim map과 재현 상태가 명시된 장기 지식
- 직접 promotion 차단: 저작권 원문, abstract 기반 확정 결론, 삭제된 negative result, 검토 전 적용 권고
- MCP read와 agent runtime 사용은 remote upload 승인이 아님
- reviewer, target scope, sanitized exact hash와 별도 승인 전 remote submit 없음

이 Case는 아직 Verified, Reference 또는 production-ready를 주장하지 않습니다.
