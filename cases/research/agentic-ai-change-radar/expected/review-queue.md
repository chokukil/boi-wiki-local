# Expected review queue

| Priority | Item | Why human Review is required | Next validation |
|---|---|---|---|
| high | AAI-004 current MCP authorization guidance | normative security guidance가 version 사이에 바뀌었음 | 대상 client/server version과 Protected Resource Metadata·Resource Indicator conformance 확인 |
| high | AAI-005 SK하이닉스 적용 가설 | 공개 자료만으로 내부 ACL, data boundary, 비용과 운영효과를 알 수 없음 | 승인된 내부 validation question과 안전한 synthetic pilot 범위 정의 |
| high | AAI-016 Agent Builder/Evals lifecycle | 같은 공식 페이지에 launch와 wind-down이 함께 있어 history와 current choice를 분리해야 함 | 2026-11-30 availability와 migration parity 확인 |
| medium | AAI-003 T0 roadmap retirement | history 보존과 current TypeScript support 분리가 필요 | 현재 SDK version과 support policy 확인 |
| medium | AAI-011 memory·context policy | persistence와 compaction 기능이 retention·삭제·recall 기준을 결정하지 않음 | representative task에서 recall, cost와 privacy 측정 |
| medium | AAI-012 bounded execution | Claude Code 사례를 범용 security guarantee로 확대할 수 없음 | 대상 runtime의 filesystem, network와 credential boundary 시험 |
| medium | AAI-015 harness complexity | model capability가 바뀌면 decomposition과 evaluator 비용 대비 효용도 바뀜 | 동일 task의 single-agent baseline과 비교 |

Reviewer는 14개 T0/T1 source record와 manifest부터 읽습니다. Single-agent reviewer pass는 절차적으로 분리되지만 사람의 독립 승인이나 Reference evidence를 대신하지 않습니다.
