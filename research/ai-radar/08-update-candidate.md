# 업데이트 후보 — revision 2

기간: 2025-12-01~2026-08-08

상태: 사용자 승인 전

## 후보 요약

| 후보 | 이전 판단 | 새 근거 | 변경 이유 | 영향 | 분류 |
|---|---|---|---|---|---|
| U-A01 | final output 위주 평가 | transcript·outcome·harness를 함께 평가 | multi-turn 실패가 final answer에 숨을 수 있음 | trajectory 저장이 필수 | 신규 |
| U-A02 | 단일 agent handoff 중심 | planner·generator·evaluator 구조 | 장기 작업의 독립 검증 필요 | 역할보다 evaluator 계약 우선 | 신규 |
| U-A03 | MCP 2025 사양 | 2026 RC에 tasks·apps·stateless core·auth hardening | protocol 운영 범위 확대 | RC와 정식판 분리 | 강화 |
| U-A04 | ADK·A2A 초기 공개 | ADK Java 1.0과 다중 언어 구현 | 상호운용 실험 가능성 증가 | 언어 간 contract test 가능 | 강화 |
| U-A05 | Microsoft Agent Framework preview | core·workflow 1.0 | 기준 판단의 상태 변화 | preview 표기를 core에서 제거 | 수정 |
| U-A06 | context 관리 중심 | memory benchmark·prospective memory 신호 | 저장보다 회수·충돌·미래 task가 중요 | memory acceptance 확대 | 강화 |
| U-A07 | tool call별 보안 | 장기 trajectory·memory 공격 signal | 위험이 여러 turn에 누적 | trajectory assurance 필요 | 신규 |
| U-A08 | model 중심 비교 | harness·policy·evaluator 단위 평가 | runtime이 성능·안전을 바꿈 | versioned system 비교 | 신규 |
| U-P01 | VLA 발표 중심 | GR00T·Cosmos·LeRobot·openpi 공개 revision | 직접 실험 surface 확대 | license·hardware 고정 필요 | 강화 |
| U-P02 | Digital Twin은 simulation 기반 | AI·world model·agent testbed 결합 | evaluation 역할 확대 | twin을 agent test harness로 검토 | 강화 |
| U-P03 | 3D·asset·ontology 층이 혼재 | OpenUSD 26.08, AAS 26-01, OPC UA mapping | 역할 경계가 더 명확해짐 | 표준 조합을 층별 평가 | 수정 |
| U-P04 | 제조 적용 발표 증가 | GR00T EA, DTC testbed, vendor case | 발표와 양산 증거 간 간극 | production-ready 주장 차단 | 충돌 |
| U-P05 | world model은 독립 연구 축 | VLA·simulation·control과 결합 signal | physical policy 평가와 연결 | sim-to-real gate 추가 | 신규 |
| U-C01 | ontology는 정보 모델 | action·function·security와 agent-based twin testbed | world/action contract 가능성 | action allowlist 가설 | 신규 |
| U-C02 | protocol 연결이 핵심 | protocol별 층·governance gap 확인 | 연결만으로 의미·안전 미해결 | bridge acceptance 강화 | 신규 |
| U-C03 | 로그 보존 | event time·revision·provenance 정합 필요 | physical state는 시간에 민감 | temporal test 필요 | 신규 |
| U-C04 | human-in-the-loop 일반 원칙 | 물리 trajectory별 승인·중단·복구 필요 | 실패 비용이 비가역적 | physical safety gate 별도 | unknown |

## 승인하지 않는 것

- MCP 2026 RC를 정식 표준으로 고정하는 것
- Microsoft가 사용한 `production-ready` 표현을 특정 조직의 준비 완료로 일반화하는 것
- GR00T Early Access나 vendor demo를 양산 성숙도로 승격하는 것
- Palantir Ontology의 제품 설명을 벤더 중립 표준으로 표현하는 것
- 공개 자료만으로 SK하이닉스 적용성·효과·비용을 판단하는 것
