# 지식 변경 세트

기준: revision 1 후보

대상: revision 2 후보

승인 상태: 미승인

## 변경 분류별 수

| 분류 | 수 | 대표 항목 |
|---|---:|---|
| 신규 | 8 | trajectory 평가, harness 단위, world model 연결, temporal consistency |
| 강화 | 5 | MCP·A2A, memory, durable execution, 공개 robotics 생태계, Digital Twin 평가 |
| 수정 | 2 | Microsoft Agent Framework 1.0, 표준 층 역할 |
| 충돌 | 3 | MCP RC와 안정 기대, vendor 제조 효과와 독립 근거, ontology 이식성 |
| stale | 1 | Agent Framework 전체를 preview로 묶은 과거 표현 |
| 폐기 검토 | 1 | model leaderboard 중심의 agent 채택 판단 |
| unknown | 4 | 물리 safety 공통 gate, sim-to-real, temporal consistency 효과, SK 적용성 |
| 합계 | 24 | 중복 없이 대표 판정 하나를 부여함 |

## 현재 지식을 실제로 바꾸는 핵심

1. **평가 단위 변경:** 답변 점수에서 environment outcome과 trajectory로 확장한다.
2. **채택 단위 변경:** model 또는 framework 이름에서 versioned harness system으로 확장한다.
3. **상태 수정:** Microsoft Agent Framework core·workflow를 preview가 아닌 1.0으로 수정하되 preview 기능을 분리한다.
4. **protocol 경계 강화:** MCP·A2A의 성숙을 인정하되 산업 의미·권한·안전 대체재가 아님을 명시한다.
5. **Physical AI gate 강화:** 공개 도구가 늘었어도 EA·demo·simulation과 양산을 분리한다.
6. **연결 가설 추가:** Digital Twin을 physical agent evaluation environment로, ontology를 world/action contract로 검토한다.

## downstream 영향

- 기술 shortlist는 GitHub 인기보다 workload fixture와 failure cost를 먼저 요구한다.
- Agentic AI pilot에는 trajectory capture·replay와 reviewer independence가 들어간다.
- Digital Twin pilot에는 sim-to-real, time synchronization과 emergency stop evidence가 들어간다.
- ontology 평가에는 action permission과 vendor-neutral export 가능성을 포함한다.
- 현재 revision은 사용자 승인 전까지 증가하지 않는다.
