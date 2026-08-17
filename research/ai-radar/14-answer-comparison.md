# 같은 Query의 답변 비교

## 실제로 성장한 부분

| 관점 | 기준 답변 | 업데이트 후보 답변 | 근거가 만든 변화 |
|---|---|---|---|
| 채택 단위 | runtime과 model을 함께 봄 | versioned harness system을 명시 | eval·framework 1.0·harness 자료 |
| 평가 | trace와 결과를 확인 | outcome·trajectory·tool call·recovery를 함께 평가 | A07, R02, R03 |
| framework | Microsoft 통합 framework는 preview | core·workflow 1.0, 주변 preview 분리 | A12, G07 |
| MCP | tool 연결 사양 | tasks·apps·stateless·auth hardening RC까지 확대 | A09, G06 |
| memory | context·checkpoint·외부 상태 | conflict·prospective memory·retention 평가 추가 | A04, A13, R01, R04 |
| Physical AI | VLA와 simulation 방향 | 공개 실험 surface와 world model 연결 확대 | G09~G12, R05~R08 |
| 제조 성숙도 | 실환경 evidence 부족 | EA·testbed 경계가 확인되어 caution 강화 | G09, P11 |
| 교차 연결 | ontology·twin 가능성 | evaluation environment와 world/action contract 가설 | P05~P11 |
| 안전 | sandbox와 사람 승인 | trajectory assurance·event-time·recovery까지 확대 | A05, R02 |

## 바뀌지 않은 부분

- 단순 workflow가 충분하면 agent를 쓰지 않는다.
- vendor 발표와 demo를 독립된 운영 성과로 보지 않는다.
- simulation 결과를 실환경 성과로 부르지 않는다.
- 공개 자료로 SK하이닉스 적용성·성과·비용을 추정하지 않는다.

## 지식 성장 판정

새 링크가 늘어서가 아니라 다음 세 가지 때문에 성장으로 인정한다.

1. preview였던 framework 상태가 1.0으로 바뀌어 과거 판단을 수정했다.
2. 평가와 안전의 단위가 final output·개별 tool call에서 trajectory·outcome·recovery로 확장됐다.
3. Physical AI의 공개 실험 가능성은 커졌지만 EA·testbed evidence가 양산 판단을 더 엄격하게 만들었다.

이 차이는 [change set](09-knowledge-change-set.md)의 24개 분류와 일치한다.

