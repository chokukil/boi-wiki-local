# Agentic AI 저장소·논문 source records

## 저장소

G01~G08의 remote HEAD를 2026-08-08 비대화형 `git ls-remote`로 확인했다. commit은 존재성과 관찰 revision을 고정할 뿐, 보안·성숙도·성능을 보증하지 않는다.

| ID | 저장소 | 재사용 포인트 | 제한 |
|---|---|---|---|
| G01·G02 | OpenAI Agents SDK | handoff, guardrail, tracing, MCP와 sandbox surface | release별 회귀 미실행 |
| G03·G04 | Google ADK | multi-agent, tool confirmation, A2A, 다중 언어 | 운영 benchmark 미실행 |
| G05 | A2A | 독립 agent 간 task/message/artifact 상호운용 | 산업 의미·설비 권한은 범위 밖 |
| G06 | MCP spec | tool/context 연결의 공식 revision | 최신 revision은 RC |
| G07 | Microsoft Agent Framework | framework 통합과 1.0 | 일부 기능은 preview |
| G08 | LangGraph | checkpoint·thread·store persistence | 특정 framework 구현 |

## 논문

R01~R04와 signal ledger의 추가 arXiv 논문은 abstract와 version metadata만 확인했다. 전문 검증·코드 실행·benchmark 재현·peer-review 확인을 하지 않았으므로 claim 강화가 아니라 검토 질문 생성에 사용했다.

- R01은 agent memory를 구조화하는 survey signal이다.
- R02는 장기 trajectory의 assurance 필요성을 제안하는 최신 signal이다.
- R03은 agent laboratory/evaluation 접근의 signal이다.
- R04는 prospective memory 평가의 signal이다.
- 단일 benchmark 순위는 framework 채택 판단으로 승격하지 않았다.

