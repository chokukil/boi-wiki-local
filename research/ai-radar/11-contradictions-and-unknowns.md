# Contradictions와 unknown

## 중요한 contradiction

### 1. protocol 확장과 안정성

- supporting: MCP 2026 RC는 stateless core, extensions, tasks, apps와 auth hardening을 제안한다.
- counterevidence: 관찰 시점에는 release candidate다.
- 판단: 설계 검토에는 반영하되 고정 production contract로 사용하지 않는다.

### 2. framework 1.0과 업무 준비도

- supporting: Microsoft Agent Framework의 core와 workflow는 1.0으로 발표됐다.
- counterevidence: 같은 발표에서 일부 managed integration·DevUI·skills·harness surface는 preview로 구분된다.
- 판단: “전체 preview”는 stale이지만 “모든 기능 production-ready”도 잘못이다.

### 3. Physical AI 가속과 양산 성숙도

- supporting: VLA·world model·simulation과 공개 저장소가 빠르게 늘었다.
- counterevidence: GR00T N1.7은 EA이며 vendor demo·testbed가 독립된 양산 성과를 제공하지 않는다.
- 판단: 실험 접근성은 강화됐지만 양산 채택 판단은 유지한다.

### 4. Digital Twin 효과

- supporting: vendor와 consortium은 commissioning·monitoring·optimization 효과를 제시한다.
- counterevidence: 이번 source set에는 독립된 현장 before/after와 실패 사례가 충분하지 않다.
- 판단: evaluation environment 가설로 사용하고 ROI claim은 보류한다.

### 5. ontology의 운영 가치와 이식성

- supporting: Palantir 문서는 object·link·action·function·security의 통합 계층을 설명한다.
- counterevidence: 벤더 중립 표준 및 cross-platform round-trip evidence가 없다.
- 판단: architecture candidate로 유지하되 표준으로 부르지 않는다.

### 6. persistent memory의 가치와 위험

- supporting: 여러 runtime과 연구가 persistence·long-term memory를 강화한다.
- counterevidence: 오래된 오류, poisoning, privacy, conflict와 retention 비용도 함께 커진다.
- 판단: 저장량보다 쓰기 승인·conflict·삭제·평가 계약을 우선한다.

## 아직 알 수 없는 것

- 특정 제조 셀에서 VLA가 사람 또는 기존 automation 대비 제공하는 안정적 이득
- simulation에서 실제 설비로 이동할 때 성능 저하와 위험 분포
- world model이 실제 commissioning 시간이나 사고 위험을 얼마나 줄이는지
- ontology action과 AAS·OPC UA operation 사이의 벤더 중립 mapping
- MCP·A2A를 산업망에 배치할 때 identity·authorization·audit의 공통 구현
- 여러 agent의 조정 이익이 비용·지연·실패 전파를 넘는 업무 조건
- 장기 memory가 시간이 지난 지식의 충돌과 철회를 정확히 처리하는 방법
- SK하이닉스의 데이터, 설비, 보안, ROI와 실제 적용성

