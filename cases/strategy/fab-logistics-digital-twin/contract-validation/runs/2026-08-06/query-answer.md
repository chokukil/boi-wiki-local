# FAB Logistics Digital Twin baseline Query

Fixed Query SHA256: `a5346d896245d8e38e6bebbb4eda77555c0a793e689a5376f9c54cccb880c964`

## Answer

공개 근거에서 채택할 수 있는 것은 개념 연결 가설이다. GEM300의 Carrier·Substrate·Control Job을 object/event 후보로, 관계를 Link로, 승인된 상태 변경을 Action 후보로 놓고, Digital Twin을 먼저 관측·시각화 계층에서 시작한 뒤 simulation이나 control로 확장할 수 있다. 실제 FAB 적용 판단은 아직 할 수 없다.

## Evidence

- SEMI 공개 overview는 E40·E87·E90·E94의 책임 범위를 구분한다.
- Palantir 공식 문서는 Object·Property·Link·Action과 governance를 설명한다.
- NVIDIA 공식 자료는 warehouse twin 구성요소와 fab twin 사례 신호를 제공한다.

## Counterevidence

- 유료 SEMI 전문을 확인하지 않았고 vendor 자료는 독립 성능 검증이 아니다.
- warehouse architecture를 semiconductor FAB 효과로 일반화할 수 없다.

## Unknowns

- 실제 object identity, event semantics, ACL, latency, simulation fidelity, KPI baseline과 운영 효과
- SK하이닉스 적용 적합성과 특정 vendor 선정

## Next checks

사람 Review 후 승인된 내부 pilot에서 read-only event mapping, data-quality profile, 안전 경계와 baseline KPI를 먼저 검증한다.

## Confidence

공개 개념 연결은 medium, 실제 FAB 적용성과 효과는 unknown이다.
