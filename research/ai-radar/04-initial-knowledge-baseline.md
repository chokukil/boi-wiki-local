# 기준 지식 후보 — revision 1

기준일: **2025-11-30**

상태: 회고적으로 재구성한 승인 전 후보

이 문서는 기준일 이전 공개 자료만으로 같은 Query에 답하기 위한 지식 snapshot이다. 이후 자료는 포함하지 않았다.

## Agentic AI

| Claim | 기준 판단 | 근거 수준 | source |
|---|---|---|---|
| B-A01 | 복잡한 agent보다 결정적 workflow와 작은 composable pattern부터 선택해야 한다. | primary-checked | A03 |
| B-A02 | Responses API, built-in tools와 tracing은 agent runtime을 모델 호출 바깥의 운영 계층으로 확장했다. | primary-checked | A01, A02 |
| B-A03 | MCP는 tool·resource·prompt 연결, A2A는 독립 agent 간 상호운용이라는 서로 다른 문제를 겨냥한다. | corroborated | A10, GH-06, GH-07 |
| B-A04 | 장기 작업은 context를 무한 누적하기보다 compaction·외부 메모리·handoff artifact로 관리해야 한다. | corroborated | A04, A06, A13 |
| B-A05 | tool 사용 agent는 최소 권한, sandbox와 승인 경계가 필요하다. | primary-checked | A05 |
| B-A06 | 장시간 실행의 핵심은 다음 session이 이어받을 수 있는 상태·진행 기록·검증 checkpoint다. | primary-checked | A06 |
| B-A07 | Microsoft Agent Framework는 AutoGen·Semantic Kernel 통합 preview로 주목할 가치가 있지만 안정판 채택 근거는 부족하다. | primary-checked | 공식 2025-10 발표 |

## Physical AI — 제조 중심

| Claim | 기준 판단 | 근거 수준 | source |
|---|---|---|---|
| B-P01 | Gemini Robotics와 GR00T N1은 vision·language·action을 결합한 범용 로봇 정책 방향을 구체화했다. | corroborated | P01, R06 |
| B-P02 | 로봇 foundation model은 다양한 embodiment와 task 데이터가 필요하지만 데이터의 일반화·품질 효과는 공개 근거가 제한적이다. | review-required | P01, R06 |
| B-P03 | simulation과 Digital Twin은 안전한 설계·학습·commissioning 환경 후보지만 sim-to-real 성과와 운영 ROI는 별도 검증해야 한다. | corroborated | P03, P04, R08 |
| B-P04 | OpenUSD는 3D scene composition과 도구 간 interchange 기반이며, 제조 의미 표준 전체를 제공하는 것은 아니다. | primary-checked | P08 |
| B-P05 | AAS와 OPC UA mapping은 자산의 표준 디지털 표현과 제조 시스템 상호운용의 구체적 표준 경로다. | primary-checked | P09 |
| B-P06 | Palantir Ontology는 object·link·action·function·security를 운영 계층으로 묶지만, 효과 주장은 해당 벤더 경계 안에서 읽어야 한다. | review-required | P05, P06, P07 |
| B-P07 | 제조 Physical AI에서 사람 승인·중단·복구·감사 가능한 action 경계는 미해결 핵심 조건이다. | unknown | 공개 자료로 충분한 공통 기준 없음 |

## 기준일의 채택 판단

- Agentic AI: 제한된 workflow부터 시작하고, state·trace·sandbox·handoff를 먼저 검증한다.
- Physical AI: simulation·Digital Twin을 실험 환경으로 쓰되 데모를 양산 증거로 간주하지 않는다.
- 교차 영역: ontology와 Digital Twin은 유망한 연결 계층이지만 agent action의 실제 권한·안전 계약은 미확인이다.

이 기준 지식에 대한 고정 Query 답은 [12-initial-query-answer.md](12-initial-query-answer.md)에 있다.
