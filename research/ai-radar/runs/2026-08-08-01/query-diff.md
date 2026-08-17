# AI Radar 고정 Query — revision 1과 후보 답변 차이

| 답변 변화 | 연결 delta | 일치 판정 |
|---|---|---|
| MCP RC 대기 → 정식 규격 migration·deprecation 검증 | RUN01-D01 revised | 일치 |
| Agent Framework 1.0 일반 구분 → core harness와 미출시 주변 기능의 구체적 경계 | RUN01-D02 revised | 일치 |
| versioned harness → 원격 Skill revision·hash·trust·rollback 포함 | RUN01-D03 new | 일치 |
| outcome·trajectory 평가 → model+harness+environment와 heterogeneous workspace 결과 포함 | RUN01-D04 strengthened | 일치 |
| 장기 trajectory 위험 → 실행 중 monitor와 고위험 action 차단 | RUN01-D05 strengthened | 일치 |
| world model·VLA 방향 → reward·simulation·human correction을 잇는 공개 loop | RUN01-D06 strengthened | 일치 |
| twin·ontology 연결 가설 → agent-executable Physical AI 개발·검증 workflow | RUN01-D07 strengthened | 일치 |
| 물리 action gate → system-level safety와 certification preparation 경계 | RUN01-D08 strengthened | 일치 |
| VLA 일반화 unknown → 새 논문 shortlist 추가, 판단 유지 | RUN01-D09 unknown | 일치 |

답변에만 생기고 delta에 없는 변화는 없다. delta가 있는데 후보 답변에서 빠진 항목도 없다. 동일 Query 비교 계약은 통과했지만 사람 승인이 없으므로 현재 revision은 1로 유지한다.
