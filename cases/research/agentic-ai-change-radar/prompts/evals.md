# Evaluation prompts

1. T0 전체를 Capture하고 baseline claim snapshot을 만들어줘.
2. T1을 Update하고 new·strengthened·revised·contradicted·stale·unknown만 보여줘.
3. 현재 지식만 사용해 Agent Memory 방식을 비교하고 부족한 근거는 unknown으로 표시해줘.
4. 이 URL 하나만 요약해줘 — near-miss이므로 Change Radar 전체를 실행하지 마.
5. 중단된 T1 Update를 같은 hash에서 재개하고 reviewer가 원문 record부터 확인하게 해줘.
