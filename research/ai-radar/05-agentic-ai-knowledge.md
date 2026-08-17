# Agentic AI 지식 후보

## 채택 판단에 재사용할 claim

| ID | 현재 후보 판단 | 변화 | 근거 수준 | source |
|---|---|---|---|---|
| A-K01 | agent가 필요하다는 가정부터 하지 말고, 결정적 workflow로 충분한지 먼저 확인한다. | 유지 | primary-checked | A03 |
| A-K02 | agent runtime의 최소 단위는 model call이 아니라 tool, trace, state와 실패 처리를 포함한 실행 경계다. | 강화 | corroborated | A01, A02, G01 |
| A-K03 | MCP는 tool/context 연결, A2A는 agent 간 task·message·artifact 상호운용을 다루며 서로 대체하지 않는다. | 강화 | corroborated | A09, A10, G05, G06 |
| A-K04 | memory는 대화 저장 하나가 아니라 context 선별, checkpoint, 외부 store, conflict와 retention 정책의 조합이다. | 강화 | corroborated | A04, A13, R01, R04 |
| A-K05 | tool permission은 prompt의 주의문이 아니라 sandbox, allowlist, 승인과 credential 격리로 구현해야 한다. | 강화 | primary-checked | A05, G01, G03 |
| A-K06 | 장기 작업은 resume 가능한 checkpoint, progress artifact와 명시적 handoff가 있어야 한다. | 강화 | corroborated | A06, A08, A12, A13 |
| A-K07 | agent 평가는 최종 문장뿐 아니라 environment outcome, 전체 trajectory, tool call과 grader 신뢰성을 함께 봐야 한다. | 신규 | corroborated | A07, R02, R03 |
| A-K08 | Microsoft Agent Framework의 core·workflow는 기준일의 preview에서 1.0으로 바뀌었지만 일부 주변 기능은 여전히 preview다. | 수정 | primary-checked | A12, G07 |
| A-K09 | multi-agent는 역할 수가 아니라 분해 가능성, 독립 검증, 통신 비용과 실패 격리로 선택한다. | 신규 | review-required | A08, A12, R03 |
| A-K10 | agent security는 단일 tool call 검증을 넘어 memory poisoning, prompt injection과 장기 trajectory의 누적 위험을 다뤄야 한다. | 신규 | review-required | A05, R02, signal PA-03·04·06 |
| A-K11 | 실제 채택 단위는 모델 이름보다 model과 harness, tools, policy, evaluator를 묶은 versioned system이다. | 신규 | corroborated | A07, A08, A12 |
| A-K12 | framework의 1.0, GitHub 인기와 기능 목록은 특정 업무의 신뢰성·비용·보안을 증명하지 않는다. | 신규 | primary-checked | A09, A12, G01~G08 |

## 실제 실험 전에 필요한 조건

1. 한 업무와 실패 비용을 고정한다.
2. 동일 task·environment·권한에서 workflow baseline과 agent 후보를 비교한다.
3. final answer, 실제 outcome과 전체 trajectory를 함께 저장한다.
4. tool별 최소 권한, 사용자 승인과 중단 조건을 명시한다.
5. checkpoint·resume·idempotency·rollback을 강제한다.
6. memory의 쓰기·충돌·삭제·retention을 평가한다.
7. 모델 또는 harness가 바뀌면 동일 fixture로 회귀한다.

## 과장하지 않는 결론

- 1.0 release는 API 안정성 신호이지 특정 조직의 production readiness 증명이 아니다.
- MCP release candidate 기능은 채택 계획에 반영할 수 있지만 확정 표준처럼 고정하면 안 된다.
- 공개 benchmark는 shortlist를 만드는 데 도움이 되지만 업무별 acceptance를 대체하지 않는다.

