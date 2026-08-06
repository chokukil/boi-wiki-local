# Method — FAB Logistics Digital Twin

## Source policy

공식 문서, 공식 저장소, 원 논문과 1차 자료를 우선합니다. 중요한 주장은 가능한 경우 독립된 복수 근거로 확인합니다. snippet, 제목-only, 접근하지 못한 전문은 확정 evidence가 아닙니다. 발행일, 확인일, version, 접근 상태와 실제 확인 범위를 기록합니다.

## Analysis policy

fact, inference, hypothesis, counterevidence, contradiction과 unknown을 분리합니다. 기존 snapshot을 덮어쓰지 않고 change reason과 downstream 영향을 보존합니다. `stale`은 재검토 필요 상태이지 거짓 또는 폐기가 아닙니다.

## Case-specific normal result

GEM300의 Carrier·Substrate·Control Job 공개 개념을 twin 상태·event와 연결하고 Object·Link·Action 후보를 만들되, 실제 FAB 데이터 매핑과 효과는 unknown 및 내부 검증 항목으로 남긴다.

## Error matrix

| 문제 | 안전한 fallback | resume 조건 |
|---|---|---|
| 필수 source 접근 불가 | partial 또는 blocked와 실제 확인 범위를 기록 | source 확보 또는 범위 재승인 |
| source hash 변경 | dependent artifact와 기존 preview 승인 무효화 | 새 hash로 Capture부터 재개 |
| contradiction | 양쪽 evidence를 보존하고 review queue 등록 | 사람의 Review 결정 |
| agent-team 없음 | 동일 파일·handoff로 No-team sequential pass | 없음; 정상 fallback |
| 유료 표준 전문 필요 | 공개 요약까지만 partial | 정당한 접근권한과 reviewer |

## Exclusions

유료 SEMI 전문 내용을 추정, 실제 FAB 성능 수치 생성, 운영 Action 실행 또는 특정 벤더 선정. 사용자 승인 없는 DeepResearch, 내부 데이터 추정, 자동 promotion과 주문 없는 보고서 생성은 하지 않습니다.
