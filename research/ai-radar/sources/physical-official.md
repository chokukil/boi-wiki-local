# Physical AI·Digital Twin 공식 source records

| ID | 확인한 내용 | 지식 사용 | 제한 |
|---|---|---|---|
| P01 | Gemini Robotics의 VLA·embodied reasoning 발표 | B-P01 | vendor-authored evaluation |
| P02·P03·P04 | 제조 simulation, virtual factory, Digital Twin 구조와 효과 주장 | B-P03 | 독립 ROI·현장 benchmark 없음 |
| P05·P06·P07 | object·link·action·function·security를 묶는 Ontology와 Digital Twin 제품 설명 | B-P06, U-C02 | Palantir 경계의 vendor claim |
| P08 | OpenUSD 26.08 문서와 scene interchange·composition | B-P04 | 제조 semantics·action safety 표준은 아님 |
| P09 | OPC UA에 AAS information model을 mapping하는 공식 companion specification | B-P05 | 구버전 AAS와 최신 AAS 호환 변화 검토 필요 |
| P10 | IDTA Release 26-01의 metamodel·API·data·security·AASX 사양 묶음 | U-P04 | 구현 간 interoperability test 미실행 |
| P11 | agent-based twins와 ontology 상호운용을 검증하려는 DTC testbed 목표 | U-C01 | 목표 설명이며 완료 성과가 아님 |

## 중요한 분리

- Digital Twin이 simulation과 상태 통합을 제공할 수 있다는 문장과, 실제 공장의 성능·비용을 개선했다는 문장은 다르다.
- Palantir Ontology가 action과 security를 모델링한다는 문장과, 타 플랫폼에서도 같은 계약이 이식된다는 문장은 다르다.
- OpenUSD, AAS, OPC UA, ontology는 서로 다른 층을 다룬다. 하나를 채택한다고 다른 층이 자동 해결되지 않는다.

