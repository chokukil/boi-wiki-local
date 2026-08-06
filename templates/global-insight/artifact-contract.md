# Global Insight Harness-local artifact contract

이 계약은 새로운 전역 OKF schema가 아닙니다. Local 문서는 기존 `OKF 0.1 + BoI Profile 0.1-local`을 사용하고, 아래 필드는 Harness와 Case 실행 artifact에만 둡니다.

## 공통 입력

- 사용자 요청과 도구 식별자
- 목적, 성공 조건, 범위와 제외 범위
- 기준 시점과 Local/Remote 경계
- 관련 claim snapshot과 주문형 산출물
- reviewer와 실행 모드

## Source manifest

각 source row는 `source_ref`, 로컬 경로 또는 URL, SHA256, `primary | secondary | community-signal`, 발행일, 확인일, 버전, 접근 상태, 실제 확인 범위, 처리 runtime, `source_refs`, `generated_from`을 가집니다.

- 검색 snippet은 확정 evidence가 아닙니다.
- abstract-only는 full-text verified가 아닙니다.
- 유료·접근 불가 전문은 우회하지 않고 `partial` 또는 `blocked` 사유로 남깁니다.
- 동일 SHA256 source는 기존 ref에 연결하고 새 복사본을 만들지 않습니다.

## Evidence

- claim ref와 정규화된 claim 문장
- supporting evidence와 counterevidence
- source별 verification level
- uncertainty, access limitation, unknown
- source locator와 exact source SHA256

## Claim snapshot과 delta

| 필드 | 계약 |
|---|---|
| previous | 이전 문장, 상태, snapshot hash |
| current | 새 문장과 상태 |
| delta_type | `new`, `strengthened`, `revised`, `contradicted`, `stale`, `retirement-candidate`, `unknown` |
| reason | source-linked 변경 이유 |
| contradiction | 양쪽 evidence ref를 모두 보존 |
| next_review_at | 다음 검토일 |
| downstream_impact | 직접 영향 문서와 claim |

새 source가 없거나 claim 변화가 없으면 정상 결과는 빈 change set입니다. 보고서나 새 claim을 만들지 않습니다.

## Handoff

- phase와 `from_role`, `to_role`
- input/output path, bytes, SHA256
- supported claims, counterevidence, unknown, contradiction
- blocker, 다음 phase 진입 조건
- source manifest before/after hash와 changed source files 0건

Case 실행은 `boi-local-case-handoff/v1`을 사용합니다.

## 실패와 resume

- 상태: `partial | blocked`
- 실패 phase와 검증 완료 artifact
- 무효화된 dependent artifact
- source별 최대 한 번의 재시도 결과
- resume checkpoint와 입력 hash
- 재개 조건

입력 hash가 동일할 때만 마지막 검증 checkpoint부터 resume합니다. 필수 source hash가 달라지면 dependent artifact와 기존 승인은 무효입니다.

## Review decision

중요 claim의 confidence 상향, contradiction 해소, 폐기, promotion은 사람 Review가 필요합니다. reviewer는 producer 요약이 아니라 manifest와 원문부터 확인합니다. 판정은 `approve | revise | partial | blocked | reject` 중 하나이며 미해결 항목과 다음 검증 조건을 포함합니다.

## Promotion preview

- sanitized candidate body
- target visibility와 target scope
- reviewer identity와 review decision ref
- 구조화된 remote-safe source refs
- exact candidate SHA256
- `approved: false`, `submitted: false`

후보 내용, source, reviewer, target scope 또는 hash가 바뀌면 승인은 무효입니다. raw source, evidence, hypothesis, analysis log, agent memory, 개인 Harness card는 직접 promotion할 수 없습니다.

## 실행 가능한 계약 예제

`examples/`의 JSON artifact는 문서 예시가 아니라 Windows native fast gate가 매 실행에서 읽고 실패 경로까지 검증하는 결정론적 계약 fixture입니다. `runtime-contract.json`의 일곱 도구와 연결되며 다음을 증명합니다.

- 새 source가 없는 Update는 report와 새 claim 없이 빈 change set으로 끝남
- source hash 변경은 dependent artifact와 기존 승인을 무효화하고 Capture부터 재개함
- failure artifact는 한 번의 source 재시도, 검증 완료 artifact, checkpoint hash와 resume 조건을 보존함
- scoped lint는 변경·연결·영향 범위만 검사하고 semantic mutation을 만들지 않음
- promotion preview는 reviewer, target visibility·scope, remote-safe source, candidate bytes·SHA256을 고정하고 제출을 비활성화함
