# T1 review queue

Run: `agentic-ai-golden-journey-2026-08-06`<br>
Reviewer pass: `codex-single-agent-source-first-review`
Semantic owner: human reviewer

| Priority | Claim | Evidence and counterevidence | Why human Review is required | Next validation | Review date |
|---|---|---|---|---|---|
| high | AAI-004 MCP authorization guidance | March base-URL fallback `03` vs June Protected Resource Metadata `05` | normative security version을 실제 구현에 맞춰 선택해야 함 | client/server negotiated version과 resource indicator conformance 확인 | 2026-08-20 |
| high | AAI-005 SK하이닉스 applicability | 모든 source가 public vendor/spec/method 자료 | 내부 data boundary, ACL, 비용, 품질과 업무 성공 기준이 없음 | 승인된 내부 pilot 질문과 금지 데이터 범위 정의 | 2026-09-06 |
| high | AAI-016 Agent Builder/Evals lifecycle | 같은 공식 페이지의 launch와 2026-06-03 wind-down | 신규 채택·migration 판단과 역사 보존을 분리해야 함 | 2026-11-30 availability와 migration parity 재확인 | 2026-11-30 |
| medium | AAI-011 memory·context | TypeScript Sessions와 context engineering; compaction loss warning | 보존·삭제·resume 정책은 제품 기능만으로 결정 불가 | representative task에서 recall·cost·privacy 측정 | 2026-09-06 |
| medium | AAI-012 bounded execution | Claude Code filesystem+network isolation report | product-specific report를 범용 control로 일반화할 수 없음 | 대상 Windows/runtime에서 filesystem, egress, credential test | 2026-09-06 |
| medium | AAI-009 A2A interoperability | official launch, no conformance result in source pack | protocol 발표와 운영 maturity는 다름 | identity, ACL, failure semantics와 version compatibility 시험 | 2026-09-06 |
| medium | AAI-015 harness complexity | planner/evaluator benefit와 sprint removal이 같은 연구에 공존 | model capability가 바뀌면 load-bearing phase도 바뀜 | single-agent baseline과 동일 task·rubric 비교 | 2026-09-06 |

이 queue는 의미를 자동 수정하지 않습니다. `retirement-candidate`는 삭제가 아니라 현재 지침에서 제거할지 사람이 판단할 항목이며, 원래 문장과 source hash는 유지합니다.
