# Scientific Foundation Model Knowledge — 지식 성장 실행 01

상태: **Community · baseline snapshot 1 → snapshot 2 candidate · review-required**

이 실행은 기존 baseline의 “task별 prediction evidence와 법칙 준수를 분리한다”는 판단을 세 가지 후속 사례로 시험한다. MetaFO, CLOUD와 NEP89은 foundation model이라는 같은 이름을 쓰지만 물리 제약의 위치, 일반화 범위, 데이터·코드 공개와 검증 상태가 서로 다르다.

## Second Brain 흐름

1. 현재 기준: [baseline Query](../../contract-validation/runs/2026-08-06/query-answer.md)
2. 새 근거: [source manifest](source-manifest.json)와 [evidence](evidence.json)
3. 변화 후보: [claim delta](claim-delta.json)
4. 독립 검토: [reviewer report](reviewer-report.json)와 [review queue](review-queue.md)
5. 재사용 검증: [동일 Query 후보 답변](query-candidate.md)과 [답변 차이](query-diff.md)

## 실제로 달라진 판단

- “physics-informed”는 모델 전체가 모든 법칙을 보장한다는 뜻이 아니다. representation, loss, differentiable module, synthetic data 또는 evaluation constraint 중 어디에 물리가 들어가는지 분해해야 한다.
- OOD·zero-shot·universal 표현은 반드시 학습한 geometry, loading, element, thermodynamic regime와 task 경계 안에서 읽어야 한다.
- peer-reviewed publication과 공개 dataset·code는 증거 상태를 강화하지만 독립 재현과 semiconductor 적용성을 자동으로 만들지 않는다.
- 장기 지식의 최소 단위는 논문 제목이 아니라 `가정 → 물리 제약 위치 → prediction → 검증 범위 → 반례·failure envelope → 재현 상태`다.

사람 검토 전에는 새 snapshot을 현재 지식으로 간주하지 않는다. 이 Case는 개별 모델의 보편적 법칙 준수나 반도체 적용성을 주장하지 않는다.
