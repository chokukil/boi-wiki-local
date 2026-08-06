# Evaluation prompts — 사용자 의도 요약

실제 실행 문구, seed, 입력 파일, required/forbidden outcome은 [prompt catalog](../evals/prompts/prompt-catalog.json)에 동결되어 있습니다. 아래 문구를 임의로 확장해 점수를 유리하게 만들지 않습니다.

1. Python·Obsidian·MCP 없는 Windows 최초 설정과 첫 durable knowledge
2. 기존 지식 보강과 일회성 near-miss `noop`
3. 동일 hash·새 근거·명시적 교정의 서로 다른 maintenance operation
4. EML·웹·CSV·PDF·PNG·회의 메모 실제 20파일 정리
5. 상충 주장·stale downstream·unsupported conclusion review queue
6. exact Local citation·반증·미확인·다음 확인·confidence가 있는 질문 답변
7. 10/20 처리 후 중단된 상태의 idempotent resume
8. agent-memory 정제 후 미승인 Team exact preview

각 prompt는 Codex와 Claude에서 세 번, with-Harness와 baseline으로 실행합니다. 실행자가 모델·도구·입력을 바꾸거나 baseline에 Harness schema를 알려주면 해당 pair는 무효입니다.

다음: [Frozen protocol](../evals/PROTOCOL.md) · [Assertions](../evals/assertions.json) · [Rubric](../evals/rubric.json)
