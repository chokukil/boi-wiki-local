# AI Radar 교정 실행 review queue

| 우선 | delta | 유형 | 사람 검토 질문 | 상태 |
|---:|---|---|---|---|
| 1 | RUN01-D01 | revised | MCP 정식 규격을 revision 2에 반영하고 migration gate를 추가할 것인가? | review-required |
| 2 | RUN01-D03 | new | 원격 Skill에 revision·hash·trust·rollback을 필수 채택 조건으로 둘 것인가? | review-required |
| 3 | RUN01-D05 | strengthened | monitor coverage·recall·time-to-response와 고위험 동기 차단을 agent security gate에 넣을 것인가? | review-required |
| 4 | RUN01-D08 | strengthened/conflicted | Halos의 system safety 관점만 채택하고 early-access·미인증 경계를 함께 유지할 것인가? | review-required |
| 5 | RUN01-D02 | revised | Agent Framework core harness와 미출시 주변 기능의 경계를 revision 2에 반영할 것인가? | review-required |
| 6 | RUN01-D04 | strengthened | model+harness+environment 비교를 pilot 필수 평가 단위로 올릴 것인가? | review-required |
| 7 | RUN01-D06 | strengthened | Physical AI pilot에 reward·simulation·human correction loop를 추가할 것인가? | review-required |
| 8 | RUN01-D07 | strengthened | Agentic–Physical 첫 실험을 설비 action보다 개발·검증 workflow에 둘 것인가? | review-required |
| 9 | RUN01-D09 | unknown | VLA 두 논문은 full text·code·독립 재현 전까지 shortlist로만 유지할 것인가? | unknown |

## Reviewer 결과

source-first pass는 D01~D08을 사람 검토 가능한 후보로, D09를 unknown 유지로 판정했다. 이는 current knowledge 승인이 아니다.

## 승인 경계

전체 승인, 일부 승인 또는 거절을 claim ID로 기록한다. 승인 전에는 current revision 1과 현재 Query 답변을 유지한다. source bytes·repository revision·candidate 내용이 달라지면 관련 review 결정을 무효화한다.
