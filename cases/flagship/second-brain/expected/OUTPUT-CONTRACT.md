# Output contract — Flagship Second Brain

이 문서는 정답 문구를 제공하는 golden answer가 아닙니다. 먼저 일반 구성원이 실제로 사용하는 Local Profile 산출물을 정의하고, 마지막에 Admin/CI가 그 실행을 평가 evidence로 포장하는 방식을 별도로 정의합니다.

## 일반 구성원 실행 결과

~~~text
data/boi/private/<Local Profile ID>/
├─ notes/knowledge/*.md
├─ notes/review-required/*.md       # 충돌·민감정보·낮은 확신이 있을 때만
├─ .boi-local/
│  ├─ second-brain-preferences.json
│  ├─ source-folder-plan.json       # 자료 폴더 작업을 승인했을 때만
│  └─ source-folder-progress.json   # 중단 후 재개가 필요할 때만
└─ promotion-drafts/                # 사용자가 preview를 요청했을 때만
   ├─ <시각>-<제목>-<범위>-<hash>-preflight.md
   ├─ <시각>-<제목>-<범위>-<hash>-preflight.package.json
   └─ <시각>-<제목>-<범위>-<hash>-preflight.remote.json
~~~

AI는 완료 결과를 채팅에서 쉬운 말로 요약합니다. 일반 구성원 실행을 위해 별도의 `output/`, `user-result.md`, evaluator bundle 또는 intermediate JSON 세트를 만들지 않습니다. 실행하지 않은 단계의 디렉터리나 빈 placeholder도 만들지 않습니다.

자료 폴더 정리처럼 hash-bound 재개가 필요한 작업만 plan·progress 상태를 남깁니다. 한두 문서의 명시적 정리나 질문에는 해당 상태 파일을 강제하지 않습니다. `intermediate/*.json`은 Reduced·Full 역할 handoff나 Admin/CI 증거에만 필요하며 일반 Single-agent 실행의 기본 산출물이 아닙니다.

## Source inventory 계약

자료 폴더 작업에서는 승인 preview 또는 Local plan에 각 지정 source의 다음 정보를 기록합니다.

- relative path, bytes, SHA256
- evidence category
- status: supported, duplicate, incomplete, review-required
- duplicate representative
- source changed: 항상 false

## 지식 반영 계획

각 topic/source에 정확히 하나의 operation과 reason을 기록합니다. `create`에는 nearest-topic search 결과가, `supersede`에는 previous/new claim과 correction source가 필요합니다. `suggest` 모드와 범위 변경에서는 적용 전 preview에 포함하고, `auto-curate`의 이미 승인된 범위에서는 Local audit state에 남깁니다.

## Local Profile Markdown

모든 Profile page는 최소 다음을 포함합니다.

- `okf_version: "0.1"`
- `boi_profile_version: "0.1-local"`
- 허용된 `boi/local-*` type
- `visibility: local-private`, `local_only: true`
- lifecycle, review, archive, promotion metadata
- 구조화된 `source_refs`와 exact source SHA256
- 표준 Markdown links

Capture/evidence와 파생 knowledge는 같은 파일이 아닙니다. Agent-memory는 `promotion_status: local_only`이며 직접 promotion 대상이 아닙니다.

## 사용자 완료 요약

비개발자가 이해할 수 있는 표현으로 채팅에서 다음만 우선 보여줍니다.

- 기존 지식 보강 수
- 새 주제 수
- 이미 반영됨 수
- 확인 필요 수
- 남은 자료 수
- 원본 보존 켜짐
- 원격 자동 업로드 꺼짐

schema, 자동 연결 방식, 처리 상태 파일, hash는 “검증 세부 정보” 뒤에 둡니다. 별도 결과 파일은 사용자가 요청하거나 후속 업무의 입력 계약일 때만 만듭니다.

## promotion bundle

사용자가 promotion preview를 요청한 경우 `remote.json`은 canonical OKF 0.1 + BoI Profile 0.1 candidate의 sanitized projection입니다. 다음이 없으면 실패합니다.

- team scope와 reviewer
- structured remote-safe source refs
- expected revision, idempotency key, Harness checksum
- exact candidate hash
- `user_confirmed: false`
- `remote_submit_allowed: false`

Local path, employee identifier, Local BoI ID, agent-memory body, raw source bytes는 0건이어야 합니다.

## Reviewer report

일반 실행의 reviewer는 source integrity, 지식 반영, history, Local/Remote 경계와 완료 요약을 독립 pass에서 확인하고 `pass`, `revise`, `block`으로 판정합니다. 구조화된 reviewer 파일은 Reduced·Full handoff 또는 감사 가능한 실행에서만 필요합니다.

## Admin/CI 평가 evidence

Admin/CI 평가에서는 위 Local 결과의 격리 복사본을 다음처럼 포장할 수 있습니다.

~~~text
output/
├─ user-result.md
├─ intermediate/
│  ├─ source-inventory.json
│  ├─ knowledge-inventory.json
│  ├─ consolidation-plan.json
│  └─ reviewer-report.json
├─ local-profile/
└─ promotion/                 # promotion 시나리오만
~~~

이 bundle은 Harness와 baseline을 같은 기준으로 검증하기 위한 Admin/CI evidence이며 일반 사용자 산출물이 아닙니다. 각 assertion은 passed, method, evidence locator를 가지며 hard assertion은 deterministic method만 허용합니다.

다음: [대표 Local page](local-output.md) · [run artifact schema](../evals/run-artifact.schema.json)
