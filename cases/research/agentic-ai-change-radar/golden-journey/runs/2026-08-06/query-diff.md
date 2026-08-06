# Same-Query T0 → T1 difference

Fixed Query SHA256: `2d9541b2df6271e8fcfcc812529e2006e5c069b6b57ae83e7fb03772350c7b13`

| Axis | T0 answer | T1 answer | Knowledge growth |
|---|---|---|---|
| runtime | Responses API·built-in tools·Python SDK, Node.js roadmap | TypeScript-first SDK, persistent Sessions·resume·compaction, remote MCP·background mode | roadmap가 현재 구현으로 revised되고 long-running runtime option이 추가됨 |
| orchestration | 단순 composable pattern, routing·parallelization·orchestrator-worker | structured progress·clean handoff, planner-generator-evaluator를 baseline lift에 따라 유지·제거 | 고정 구조가 아니라 model/task dependent harness evolution으로 강화 |
| tool use | built-in tools와 MCP integration | agent-oriented tool contract, namespacing, context-efficient result, A2A interoperability | tool 수가 아니라 agent affordance와 eval이 판단 기준으로 추가됨 |
| memory·context | augmented LLM의 memory 개념, 구현은 unknown | persistent session, structured note, just-in-time retrieval, compaction과 손실 위험 | 구현 선택과 counterevidence가 함께 생김 |
| evaluation | tracing·evaluation availability와 일반적 측정 원칙 | multiple trials, outcome/transcript graders, capability/regression, human calibration | 평가 계약이 구체화되고 confidence 상향 조건이 강화됨 |
| security | MCP 2025-03 OAuth discovery와 base URL fallback | MCP Protected Resource Metadata·Resource Indicators, filesystem+network isolation pattern | version contradiction과 bounded execution 검증 질문이 생김 |
| product lifecycle | Agent Builder 없음 | launch history와 wind-down notice를 동시에 보존 | “new”만 기록하던 판단이 stale·retirement-candidate로 성장 |
| organization fit | unknown | 선택지는 늘었지만 unknown 유지 | 내부 근거 없이 confidence를 올리지 않는 것이 재검증됨 |

T1은 T0 파일을 덮어쓰지 않습니다. `change-set.json`의 모든 revised·contradicted·stale·retirement-candidate 항목은 T0 snapshot SHA256 `61f1573cab61d5eeb87a9366893adfb2fda26c65872ce312ab6f3ad62b0240f0`을 참조합니다.
