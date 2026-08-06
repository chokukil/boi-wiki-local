# Method — Scientific Foundation Model Knowledge

## Source policy

공식 문서, 공식 저장소, 원 논문과 1차 자료를 우선합니다. 중요한 주장은 가능한 경우 독립된 복수 근거로 확인합니다. snippet, 제목-only, 접근하지 못한 전문은 확정 evidence가 아닙니다. 발행일, 확인일, version, 접근 상태와 실제 확인 범위를 기록합니다.

## Analysis policy

fact, inference, hypothesis, counterevidence, contradiction과 unknown을 분리합니다. 기존 snapshot을 덮어쓰지 않고 change reason과 downstream 영향을 보존합니다. `stale`은 재검토 필요 상태이지 거짓 또는 폐기가 아닙니다.

## Case-specific normal result

MatterGen·GraphCast·physics-guided models의 서로 다른 prediction evidence를 보존하고, 법칙 준수·generalization·재현 여부를 같은 것으로 취급하지 않으며 불확실성은 unknown으로 남긴다.

## Error matrix

| 문제 | 안전한 fallback | resume 조건 |
|---|---|---|
| 필수 source 접근 불가 | partial 또는 blocked와 실제 확인 범위를 기록 | source 확보 또는 범위 재승인 |
| source hash 변경 | dependent artifact와 기존 preview 승인 무효화 | 새 hash로 Capture부터 재개 |
| contradiction | 양쪽 evidence를 보존하고 review queue 등록 | 사람의 Review 결정 |
| agent-team 없음 | 동일 파일·handoff로 No-team sequential pass | 없음; 정상 fallback |
| full text 또는 재현 artifact 없음 | abstract-only·not-reproduced 상태로 partial | 전문·코드·데이터 또는 독립 재현 |

## Exclusions

논문 초록만으로 full-text 검증 주장, 벤치마크를 보편 법칙 준수로 확대, 변화 없는 지식의 주기적 재작성. 사용자 승인 없는 DeepResearch, 내부 데이터 추정, 자동 promotion과 주문 없는 보고서 생성은 하지 않습니다.
