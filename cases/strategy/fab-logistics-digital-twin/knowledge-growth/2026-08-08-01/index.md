# FAB Logistics Digital Twin — 지식 성장 실행 01

상태: **Community · baseline snapshot 1 → snapshot 2 candidate · review-required**

이 실행은 기존 공개 baseline의 개념 연결을 AAS Release 26-01, OPC UA for AAS와 ontology action governance 근거로 다시 검토한다. 실제 FAB 데이터나 유료 SEMI 전문을 사용하지 않으며, 조직 적용성과 운영 효과는 unknown으로 유지한다.

## Second Brain 흐름

1. 현재 기준: [baseline Query](../../contract-validation/runs/2026-08-06/query-answer.md)
2. 새 근거: [source manifest](source-manifest.json)와 [evidence](evidence.json)
3. 변화 후보: [claim delta](claim-delta.json)
4. 독립 검토: [reviewer report](reviewer-report.json)와 [review queue](review-queue.md)
5. 재사용 검증: [동일 Query 후보 답변](query-candidate.md)과 [답변 차이](query-diff.md)

## 실제로 달라진 판단

- Digital Twin의 공통 의미층은 특정 제품 ontology 하나가 아니라 AAS metamodel·API·security·package의 고정 revision과 OPC UA mapping을 함께 검토해야 한다.
- Palantir식 Object·Link·Action은 유용한 운영 모델이지만 표준 자산 식별과 설비 source of truth를 대체하지 않는다.
- 첫 pilot은 실시간 제어가 아니라 read-only event mirror, time-aligned replay, simulation, decision proposal 순으로 진행한다.
- Action은 별도 승인·권한·로그·복구 계약이 준비된 뒤에만 검토한다.

사람 검토 전에는 새 snapshot을 현재 지식으로 간주하지 않으며, 이 Case는 실제 FAB domain validation이나 production readiness를 주장하지 않는다.
