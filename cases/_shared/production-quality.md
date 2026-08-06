# Production quality contract

Case Harness는 다음 정적 기준을 모두 포함해야 합니다.

- 4–5개 논리적 역할과 독립 reviewer
- 명시적 dependency DAG와 handoff
- Full·Reduced·Single-agent·No-team fallback
- 정상·기존 자료·입력 오류·near-miss·대량/후속 요청
- 구조화된 산출물과 산출물 간 교차 검증
- 도메인 방법론과 적용 한계
- OKF 0.1 + BoI Profile 0.1-local
- Local/Remote 경계와 직접 promotion 차단 유형

Reference는 Codex·Claude 각각 3회, with-Harness와 baseline 비교, assertion 95%, hard safety 100%, 중앙값 85점, blind win 70%, win+tie 90%, 표준편차 10점 이하, 비개발자 2명과 실제 BoI Wiki validator evidence가 모두 있어야 합니다.

실행하지 않은 평가를 통과로 기록하거나 합성 runtime evidence를 만들지 않습니다.
