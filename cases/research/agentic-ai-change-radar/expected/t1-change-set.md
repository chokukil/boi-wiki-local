# T1 expected change set

Fixture: `PUB-AAI-RADAR-001-v1`

| Delta | Claim | Expected result | Evidence and reason |
|---|---|---|---|
| new | AAI-006 | visual workflow versioning과 centrally managed connector registry가 새 orchestration 선택지로 등장 | `06-t1-openai-agentkit.md` / `b79c2634183cb02875121be947691fc2c9dfc1c2249f61752c66bed4aa5288a6` |
| strengthened | AAI-002 | tracing 방향이 dataset, trace grading과 workflow-level evaluation으로 확장되어 근거 강화 | T0 `02` + T1 `06` |
| revised | AAI-003 | TypeScript SDK가 현재 문서화되어 “Node.js 지원은 향후 계획”이라는 시점 한정 문장을 수정 | `04-t1-openai-agents-typescript.md` / `3002b305f0a04404061d3794e1ff64defa541e9c07776eecb78025aadd50ee98` |
| contradicted | AAI-004 | 현재 authorization-server discovery를 MCP server base URL fallback만으로 설명하면 2025-06 revision과 충돌 | `05-t1-mcp-key-changes-2025-06.md` / `03eaedc393b03459971ff018504e7a203d09d0ac49c39cff3b3b083fa78f6dda` |
| stale | AAI-003 | T0 roadmap 문장은 역사 기록으로는 유효하지만 현재 지원 상태 설명으로는 stale | T0 `02` + T1 `04` |
| retirement-candidate | AAI-004 | 2025-03 discovery 규칙을 현재 normative guidance에서 제거 후보로 올리되 history는 보존 | T0 `03` + T1 `05` |
| unknown | AAI-005 | 공개 vendor·spec 자료만으로 SK하이닉스 적용 효과, 비용, 보안 적합성을 확정할 수 없음 | 내부 검증과 사람 Review 필요 |

이 change set은 deterministic oracle입니다. 실제 live Update에서는 원문을 다시 확인하고 source hash와 최신 version을 기록합니다.
