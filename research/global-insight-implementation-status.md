# SK하이닉스 Global Insight Meta Harness — implementation status

기준 시점: 2026-08-08

요구사항별 증거 판정은 [acceptance audit](global-insight-acceptance-audit.md)을 참고합니다.

## 구현 완료

- Capture, Update, Query, DeepResearch, Health, Review, Promote의 자연어 routing과 책임 경계
- 일곱 도구와 delta·artifact·안전 기본값의 machine-readable runtime contract
- change set과 review queue를 기본 결과로 하는 lifecycle
- `new`, `strengthened`, `revised`, `contradicted`, `stale`, `retirement-candidate`, `unknown` delta 계약
- source manifest, evidence, claim history, handoff, partial·blocked, resume와 promotion preview 계약
- Full, Reduced, Single-agent, No-team fallback의 동일 artifact·안전 계약
- Python-free Windows native fast gate와 `check.ps1 -NativeOnly` 연결
- 빈 Update, evidence, handoff, failure·resume, hash invalidation, scoped lint와 promotion preview의 native executable fixture
- Agentic AI T0/T1 public fixture, deterministic delta oracle, review queue와 exact promotion preview
- FAB Logistics Digital Twin public Case
- Scientific Foundation Model Knowledge public Case
- AI Radar 승인 revision 1과 revision 2 review 후보의 source→evidence→delta→review→동일 Query 성장 실행
- FAB Logistics Digital Twin baseline→AAS·OPC UA·ontology action knowledge-growth 후보 실행
- Scientific Foundation Model baseline→physics constraint 위치·scope·artifact/reproduction knowledge-growth 후보 실행
- 승인된 AI Radar revision 1에서 만든 sanitized BoI Wiki promotion preview와 미승인 두 Case의 fail-closed eligibility receipt
- 세 Case의 runtime-neutral role cards, DAG, 5개 eval prompt, 3개 seed, frozen Codex·Claude comparison protocol
- public-only fixture policy를 검증하는 Native와 Python administrator oracle
- pinned HarnessPackage와 Codex·Claude Core Skill mirror 비변경
- generic Global Insight Skill 미생성

## 현재 검증 evidence

- `check.ps1 -NativeOnly`: pass
- `scripts/global_insight_native_check.ps1`: pass
- `scripts/case_harness_check.py`: 4 Cases pass, Global Insight 3 Cases는 각 `community`
- knowledge-growth artifact: 3건, 모두 source-first review·동일 Query 비교·hash invalidation 경계 보유
- frozen runtime benchmark: 0/60이며 knowledge-growth artifact를 benchmark run으로 계산하지 않음
- `scripts/meta_harness_check.py`: pass
- fixture, docs, eval, runtime generated-builder `--check`: pass
- 전체 unittest: 118 pass, 1 skip
- 관리자 `check.ps1`: public clean checkout 기준으로 판정
- `setup.cmd` Python-free preview: pass, mutation false
- pinned `harness_sync.py verify`: pass, private files overwritten false

## Local Private 검증 경계

- 실제 Local Profile의 승인 원문과 개인 Harness card는 이미 Local Private에 존재하지만 release 후보와 evidence bundle에는 포함하지 않음
- 공개 계약 문서가 갱신되면서 개인 카드의 `generated_from` hash drift가 발생했고, 표준 Local Profile lint가 이를 fail-closed로 검출함
- 이번 release에서는 Local Private 파일을 수정하지 않는 경계를 우선하므로 개인 카드 hash refresh는 수행하지 않고 `stale · review-required`로 남김

## 의도적으로 미완료인 외부 gate

- Codex·Claude 각 3회 with-Harness/baseline 실행과 blind comparison 미수행
- 비개발자 2명 자연어 Acceptance 미수행
- 실제 BoI Wiki validator evidence 미수집
- 실제 MCP endpoint `initialize`·`tools/list`와 promotion submit round trip 미수집; descriptor·sanitized preview는 완료, 상태는 `pending-external-system`
- 어떤 새 Case도 Verified·Reference·production-ready가 아님

이 외부 gate들은 공개 Community Case와 Local 실행 계약 사용을 막지 않지만, 상태 승격과 generic Skill 제안에는 필수입니다. `0000000` scaffold에 개인 카드를 만들거나 Local-only evidence를 공개 release evidence로 가장하지 않습니다.

## 다음 승인 경계

1. RC merge 뒤 개인 카드의 public source hash refresh를 별도 Local-only preview와 승인으로 처리합니다.
2. 두 명의 비개발자가 Golden Journey를 자연어로 실행하고 일곱 도구와 approval boundary를 설명합니다.
3. Codex·Claude frozen protocol evidence를 수집한 뒤 evaluator가 상태 승격 여부를 판정합니다.
4. 세 Case의 지식 성장 후보를 사람이 검토하고, 이후 stable operation·baseline improvement와 cross-Case regression이 확인된 경우에만 generic Skill을 제안합니다.
