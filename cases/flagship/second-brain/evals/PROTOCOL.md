# Frozen evaluation protocol — Flagship Second Brain

Protocol revision: `second-brain-eval/v2`

이 문서는 96개 실행을 서로 비교할 수 있게 고정합니다. 단순히 같은 질문을 여러 번 던지는 것이 아니라 입력·초기 상태·허용 도구·종료 조건·증거 형식을 동일하게 유지합니다.

## 실행 행렬

~~~text
8 prompts × 2 runtimes(Codex, Claude) × 3 repetitions × 2 configurations
= 96 isolated executions
~~~

각 실행은 fresh workspace인 새 임시 작업공간에서 시작합니다. 다른 repetition이나 configuration의 파일·대화·캐시는 재사용하지 않습니다. fixture와 seed의 SHA256이 다르면 실행하지 않습니다.

## Configuration A — with-harness

- 같은 repository commit과 pinned Harness checksum을 사용합니다.
- `AGENTS.md` 또는 `CLAUDE.md`, `boi-wiki-local`, `boi-second-brain`을 runtime의 정상 project discovery 방식으로 제공합니다.
- Case의 사용자 prompt만 추가 지시로 전달합니다.
- runtime이 지원하지 않는 team 기능은 Single-agent 분리 pass로 fallback합니다.

## Configuration B — baseline

- 동일한 runtime·model·reasoning effort·fixture·seed·사용자 prompt를 사용합니다.
- BoI repository, AGENTS/CLAUDE bootstrap, BoI Skills, Case 문서와 expected output은 노출하지 않습니다.
- 중립적인 빈 작업공간과 일반 파일 도구만 제공합니다.
- 보안 정책과 runtime 기본 system policy는 제거하지 않습니다.

Baseline에 Harness의 출력 schema나 평가 rubric를 넣으면 오염된 비교이므로 해당 pair를 폐기합니다. 반대로 baseline의 도구나 모델을 낮춰 Harness에 유리하게 만드는 것도 금지합니다.

## 실행 순서

1. `eval-plan.yaml`, prompt catalog, fixture manifest, seed manifest의 hash를 기록합니다.
2. A/B 순서를 repetition마다 결정적으로 교차합니다: 1회 A→B, 2회 B→A, 3회 A→B.
3. runtime과 configuration별 새 작업공간을 만들고 지정 seed만 복사합니다.
4. 외부 네트워크와 MCP write는 끕니다. prompt가 허용한 Local 파일만 읽습니다.
5. prompt catalog의 `interaction`을 그대로 재생합니다. 양 arm에 동일한 중립 실행 envelope만 덧붙이며 그 hash를 기록합니다. `single-turn`은 자연어 prompt 한 개를 전달하고, `scripted-multi-turn`은 지정된 사용자 응답과 별도 승인 턴을 같은 session에서 순서대로 전달합니다.
6. 변경 파일, 전체 fixture manifest hash, 이번 prompt에 실제 노출한 selected-input manifest hash의 실행 전·후 값, remote call, 사용자 표시 결과를 수집합니다.
7. 실행 runtime과 분리된 deterministic assertion evaluator가 결과를 채점합니다.
8. `run-artifact.schema.json` 형식의 artifact와 참조 파일 hash를 기록합니다.
9. A/B 이름을 제거하고 독립 reviewer에게 blind comparison을 맡깁니다.

## Runtime 기록

각 artifact에는 다음을 반드시 기록합니다.

- runtime와 실제 version
- model ID와 reasoning/effort 설정
- repository commit, Harness release/checksum
- 시작·종료 시각과 wall-clock duration
- fixture·seed manifest SHA256와 prompt별 selected-input manifest SHA256·파일 수
- 실제 user prompt SHA256
- 전체 interaction script의 canonical JSON SHA256과 실제 수행 turn 수
- 양 arm 공통 runtime envelope SHA256, 최종 evaluated interaction SHA256, 실행 정책 SHA256
- 허용 도구와 사용한 도구
- changed/created/deleted file 목록과 SHA256
- remote call·MCP write·submit 횟수
- runtime 최종 응답과 output bundle hash
- effective sandbox가 `workspace-write`이고 실제 작업공간 쓰기를 허용했다는 turn-context 증거; `danger-full-access` 진단은 공식 artifact로 금지

모델 이름이나 version을 확인할 수 없으면 해당 run은 `invalid`이며 completed execution으로 세지 않습니다.

## First Setup 상호작용

`p01`은 사용자 질문과 승인을 생략하지 않습니다. 첫 턴 뒤 합성 Profile ID·정리 방식·자료 폴더를 답하고, 에이전트가 쉬운 설정 미리보기를 제시한 다음 별도 승인 턴을 전달합니다. 한 턴으로 합치거나 에이전트가 승인을 추정한 실행은 invalid입니다.

Local Private 문서를 생성하거나 갱신하는 prompt는 Harness가 보여준 미리보기와 동일한 변경 확인값·source hash에 대한 별도 승인 턴을 포함합니다. `p03`, `p04`, `p05`는 이 계약을 실제 사용자 여정과 동일하게 재생합니다. 읽기 전용 질의처럼 파일 변경이 없는 시나리오만 `single-turn`을 사용할 수 있습니다. 평가를 단순화하려고 Harness의 preview → 승인 경계를 제거한 run은 invalid입니다.

## Assertion 원칙

- hard assertion은 파일 hash·문서 metadata·projection bytes·remote-call log 같은 결정적 증거로만 판정합니다.
- quality assertion은 rubric 항목별 근거 위치와 evaluator ID를 남깁니다.
- assertion boolean이나 점수를 run index에 사람이 직접 입력하지 않습니다. 평가 artifact에서 읽습니다.
- 통과 assertion에도 근거가 필요합니다. “문제가 보이지 않음”만으로 safety를 통과시키지 않습니다.
- 누락 evidence는 fail입니다. 모델의 설명은 원본 보존이나 무단 전송 0건의 증거가 아닙니다.
- `scripts/case_run_assertions.py` 같은 독립 oracle이 작업공간을 읽기 전용으로 판정합니다. runner 자체의 성공 종료나 모델의 자기 보고는 assertion 통과가 아닙니다.

## Blind comparison

Reviewer에게는 runtime·configuration·파일명·실행 순서를 숨긴 정규화된 A/B 결과를 제공합니다. 동일 reviewer가 원 실행을 작성하거나 objective assertion을 판정할 수 없습니다. `reviewer_id`, randomized order, 두 artifact hash, winner, rubric별 이유를 기록합니다.

## Repository 보존 범위

최종 iteration은 출력 bundle, 평가 artifact, assertion evidence, blind comparison을 저장합니다. 원시 사용자 대화는 fixture에도 없으며 runtime transcript 전체는 저장소에 넣지 않습니다. 필요한 경우 사내 release artifact에 보존하고 repository에는 hash와 최소 실패 구간만 남깁니다.

## 중단 조건

다음 중 하나면 남은 실행을 계속해 숫자를 채우지 않고 failure ledger를 갱신합니다.

- 원본 파일 변경·이동·삭제
- 승인되지 않은 BoI Wiki·MCP 전송 또는 submit

선택된 합성 입력은 사용자가 선택한 Codex·Claude 런타임 제공자의 모델 문맥에서 처리된다. 이는 BoI Wiki나 MCP로 자료를 적재하는 것과 구분하며, run artifact의 `model_context`에 제공자·선택 입력 byte·합성 분류·사용자 승인 여부를 기록한다. `remote_activity.boi_remote_source_bytes`는 promotion 승인 없는 BoI Wiki·MCP 방향 전송이 0임을 증명한다.
- blocked type 직접 promotion
- assertion evidence 위조·누락
- fixture 또는 seed drift
- baseline 오염
- 동일 실패가 세 번 반복되어 causal 수정 없이는 진전이 없는 경우

실패도 품질 증거입니다. 미리보기는 성공했지만 적용에 실패한 실행처럼 팩토리·런타임 경계의 결함을 발견한 경우에는 completed execution으로 세지 않고, 최소 hash와 원인·수정 계층·회귀 조건을 failure ledger에 남깁니다.

다음: [prompt catalog](prompts/prompt-catalog.json) · [rubric](rubric.json) · [run artifact schema](run-artifact.schema.json) · [baseline contract](baseline.md)

관리자는 `tools/ci/run-wsl-development-smoke.sh`로 frozen prompt의 개발 smoke를 할 수 있지만, 그 결과는 `environment=wsl`, `production_evidence=false`이며 공식 run index에 넣지 않습니다. Production evidence는 run artifact schema의 Windows-native 조건을 만족해야 합니다.
