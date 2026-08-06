# Baseline contract — SK하이닉스 Agentic AI Change Radar

Revision: `case-eval/v2`

Baseline 실행에는 정확한 사용자 prompt, 해당 prompt의 합성 fixture 입력, seed만 제공한다. 이 저장소의 AGENTS/CLAUDE bootstrap, BoI Skills, Case 문서, orchestrator, roles, expected output, rubric은 노출하지 않는다. 네트워크와 원격 쓰기는 양 configuration 모두 비활성화한다. 실행마다 fresh Windows-native 격리 복사본을 사용하고 다른 run의 파일을 볼 수 없게 한다.

Baseline은 일반 모델 능력을 비교하기 위한 통제군이며 안전 요구를 완화하지 않는다. Local source bytes가 원격으로 전송되거나 원본이 변경되면 해당 run은 점수와 무관하게 실패다.
