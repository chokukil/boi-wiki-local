# Physical AI 지식 후보 — 제조 중심

## 채택 판단에 재사용할 claim

| ID | 현재 후보 판단 | 변화 | 근거 수준 | source |
|---|---|---|---|---|
| P-K01 | VLA는 vision·language·proprioception을 action으로 연결하는 유력 방향이지만 범용 로봇 신뢰성은 아직 입증되지 않았다. | 강화 | corroborated | P01, R06, R07 |
| P-K02 | GR00T, Cosmos, LeRobot와 openpi는 공개 실험 가능성을 넓혔지만 license·hardware·checkpoint·EA 경계를 함께 고정해야 한다. | 신규 | primary-checked | G09~G12 |
| P-K03 | Digital Twin과 simulation은 설계·synthetic data·virtual commissioning·agent 평가 환경 후보이며, 실환경 성과는 별도 gate다. | 강화 | corroborated | P03, P04, R05, R08 |
| P-K04 | OpenUSD는 3D scene composition, AAS는 자산의 표준 디지털 표현, OPC UA mapping은 산업 정보 교환을 다룬다. 세 층은 상호보완적이다. | 수정 | corroborated | P08, P09, P10 |
| P-K05 | ontology의 object·link·action·function·security 구조는 agent의 world/action contract 후보지만 Palantir 밖의 이식성은 미확인이다. | 강화 | review-required | P05, P06, P07, P11 |
| P-K06 | world model과 VLA의 결합은 simulation·prediction·control을 가깝게 만들지만 공개 결과만으로 실제 제조 일반화를 판단할 수 없다. | 신규 | review-required | G10, signal PA-16·20 |
| P-K07 | 제조 Physical AI의 공개 자료는 demo·testbed·vendor case가 많아 양산 성숙도나 ROI를 직접 뒷받침하지 않는다. | 충돌 | corroborated | P02~P04, P11, G09 |
| P-K08 | 물리 action에는 속도·공간·설비 상태에 따른 승인, 중단, 복구와 감사 가능한 trajectory gate가 필요하지만 공통 공개 기준은 부족하다. | 신규 | unknown | R02, P09, P10 |

## 제조 실험을 위한 evidence ladder

1. offline dataset에서 policy·world model을 비교한다.
2. Digital Twin에서 정상·경계·실패 trajectory를 재현한다.
3. hardware-in-the-loop에서 sensor delay·actuator constraint·network failure를 넣는다.
4. 제한된 실제 셀에서 사람 승인과 emergency stop을 포함해 검증한다.
5. 품질·cycle time뿐 아니라 intervention, near-miss, recovery와 audit completeness를 측정한다.

## 표준과 제품의 역할 분리

| 층 | 후보 | 해결하는 문제 | 해결하지 않는 문제 |
|---|---|---|---|
| 3D scene | OpenUSD | scene composition·interchange | 제조 의미·권한 정책 |
| asset twin | AAS | asset·submodel·semantic ID | agent reasoning 품질 |
| industrial transport/model | OPC UA mapping | 산업 정보 접근·교환 | LLM tool permission |
| operational ontology | Object·Link·Action | 업무 상태와 action 모델 | 벤더 간 이식성 자동 보장 |
| agent protocol | MCP·A2A | tool/context 또는 agent 상호운용 | 설비 safety certification |

