# Frozen evaluation protocol — FAB Logistics Digital Twin

Protocol revision: `case-eval/v2`

각 prompt는 Codex와 Claude에서 3회, with-Harness와 baseline으로 실행한다. 매 실행은 fresh Windows-native 임시 복사본이며 cross-run 상태와 network를 허용하지 않는다. fixture, seed, 사용자 prompt, output bundle, 독립 evaluator evidence를 SHA256으로 고정한다.

with-Harness와 baseline은 같은 합성 입력과 seed를 받지만 baseline에는 Harness·Skill·Case 지침이 노출되지 않는다. 순서는 repetition별로 교대하고, reviewer는 출력 출처를 가린 blind comparison을 수행한다. runtime·model·version·reasoning·소요 시간과 실제 파일 hash를 run artifact에 기록한다. 자기보고 assertion이나 자기보고 점수만 있는 run은 evidence로 인정하지 않는다.

실행 실패도 삭제하지 않고 `failures/failures.json`에 pre-model 여부, 전송 byte, 비용, 재시도 조건을 기록한다. 60개 비교 실행과 외부 evidence gate가 모두 채워지기 전에는 Reference를 주장하지 않는다.
