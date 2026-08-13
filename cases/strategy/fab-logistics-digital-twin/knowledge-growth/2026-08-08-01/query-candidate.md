# FAB Logistics Digital Twin — 고정 Query 후보 답변

> GEM300 공개 개념, 제조 Digital Twin과 Object·Link·Action을 어떤 경계로 연결해야 하며 실제 FAB 적용 전에 무엇을 검증해야 하는가?

공개 근거가 바꾼 판단은 Digital Twin을 단일 제품 모델로 시작하지 않는다는 점이다. GEM300의 Carrier·Substrate·Control Job은 domain vocabulary 후보로 두되, 자산 identity와 lifecycle representation에는 AAS의 exact release part를, transport mapping에는 OPC UA for AAS를 별도로 검토해야 한다.

Palantir식 Object·Link·Action은 상태 탐색, decision proposal과 승인된 action을 연결하는 application semantic layer로 유용하다. 그러나 이는 표준 자산 identity나 equipment source of truth를 대체하지 않는다. vendor ontology와 표준 representation 사이에는 명시적 mapping, revision, permission, action log와 rollback 경계가 필요하다.

첫 pilot은 다음 순서가 안전하다.

1. Carrier·Substrate·Control Job event를 변경하지 않고 mirror한다.
2. identity, timestamp, state transition과 누락 event를 검증한다.
3. historical replay와 물류 simulation으로 decision proposal을 비교한다.
4. 사람 승인과 audit log를 유지한 advisory workflow를 검증한다.
5. 별도의 운영 승인·복구 증거가 생기기 전에는 live equipment action을 연결하지 않는다.

실제 object identity, SEMI normative field mapping, MES·AMHS·equipment 간 authoritative state, latency, fidelity, ACL, baseline KPI와 운영 효과는 unknown이다. 공개 자료만으로 특정 vendor 선정이나 SK하이닉스 적용성을 결론내릴 수 없다.

이 답변은 Community 후보이며 현재 baseline을 자동 변경하지 않는다.
