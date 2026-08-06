# T0 Query answer

Query SHA256: `2d9541b2df6271e8fcfcc812529e2006e5c069b6b57ae83e7fb03772350c7b13`

## Answer

T0 공개 지식에서 채택 판단에 쓸 수 있는 기준은 “가능하면 단순한 workflow에서 시작하고, 복잡도·autonomy·tool 수를 늘릴 때 측정 가능한 성공 기준을 둔다”는 것입니다. 구현 후보로는 Responses API, built-in web/file/computer tools, Agents SDK, handoff·guardrail·tracing과 MCP HTTP authorization이 확인됩니다. 다만 Node.js SDK는 당시 roadmap이었고, memory는 개념 수준이라 persistent session·compaction·resume 선택을 결정할 근거가 부족합니다.

## Evidence

- 단순·조합 가능한 pattern과 workflow/agent 구분: `PUB-AAI-RADAR-002-v1:01` / `ab34858a1c3227328e2142198f3eb8f227db69a8b85820d483b865bd8b1e31fb`
- Responses API, built-in tools, Agents SDK, tracing과 Node.js roadmap: `PUB-AAI-RADAR-002-v1:02` / `18dc8a38ea052c0cc70a1a1ff68b59e68977c52ad03e900c7a2f1bb13030854d`
- MCP 2025-03-26 HTTP authorization과 discovery: `PUB-AAI-RADAR-002-v1:03` / `a2a76a099a2b59f4de4478fa431b0bbf07fc6c7187c834da77c6d8e3aa7f54f6`

## Counterevidence

T0 cutoff 안에서 위 제품·설계 선택의 비교 효과를 반증하거나 우월성을 입증하는 독립 benchmark는 확보하지 못했습니다. 따라서 vendor 제공 사실을 조직 적용 결론으로 확대하지 않습니다.

## Unknowns

- SK하이닉스 업무별 baseline과 성공 기준
- 내부 데이터 등급, ACL, network·model processing boundary
- persistent memory의 보존·삭제·resume 정책
- 비용, latency, 품질, human approval trade-off
- 대상 MCP implementation version과 conformance

## Next checks

Node.js/TypeScript SDK 구현 여부, MCP 후속 revision, durable memory·context 관리, multi-turn evaluation, bounded execution과 agent interoperability의 공식 후속 자료를 확인합니다.

## Confidence

공개 제품·spec 존재와 T0 문장에는 `high`, 특정 조직의 채택 판단에는 `unknown`입니다.
