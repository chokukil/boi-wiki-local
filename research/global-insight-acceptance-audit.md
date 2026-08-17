# Global Insight Meta Harness — requirement-by-requirement acceptance audit

Audit date: 2026-08-08
Branch: `codex/ai-radar-golden-journey`

판정 기준:

- `proven`: 현재 checkout의 파일 또는 실행 결과가 요구사항 전체를 직접 증명
- `contract-proven`: 실행 계약과 결정론적 oracle은 증명됐지만 외부 runtime·사용자 evidence는 아직 없음
- `privacy-verified`: Local-only 존재와 제외 경계만 확인했으며 내용·경로를 release evidence에 싣지 않음
- `pending-external`: 실제 사용자, 실제 Local Profile 또는 다른 runtime이 있어야 증명 가능

## 제품과 인터페이스

| Requirement | Evidence | Result |
|---|---|---|
| 반복 운영체계와 7개 도구 | `templates/global-insight/README.md`; `runtime-contract.json`; `tests/test_global_insight.py` | proven |
| 사용자-facing 이름은 DeepResearch | 같은 README의 tool table과 routing; 금지 이름 repository search 0건 | proven |
| change set과 review queue가 기본, 보고서는 주문형 | README, `artifact-contract.md`, 각 Case output contract | proven |
| 7개 delta와 과거 snapshot 보존 | `artifact-contract.md`; Golden Journey `expected/t0-snapshot.md`, `expected/t1-change-set.md` | proven |
| evidence·counterevidence·contradiction·unknown 보존 | artifact contract, role cards, assertions, output contracts | proven |
| Health가 의미 결론을 자동 수정하지 않음 | machine contract, scoped-lint fixture, native checker completion message | proven |
| Query가 Local knowledge만 사용하고 DeepResearch를 자동 실행하지 않음 | machine contract와 eval prompt contract | proven |
| DeepResearch는 명시 요청·승인 후 native research로만 실행 | machine contract, Case methods와 role hard-fail | proven |

## 안전과 Local/Remote 경계

| Requirement | Evidence | Result |
|---|---|---|
| Local Private 자동 원격 전송 금지 | common artifact contract, all Case manifests, hard assertions | proven |
| raw source·evidence·hypothesis·analysis log·agent memory·개인 Harness 직접 promotion 금지 | manifests와 `case_harness_check.py` | proven |
| exact candidate hash, reviewer, target scope와 승인 무효화 | Golden Journey `expected/promotion-preview.json`; native hash check | proven |
| reviewer가 원문·manifest부터 확인, self-approval 금지 | role cards, runtime manifests, orchestrator, assertions | proven |
| `0000000`에 개인 Harness를 만들지 않음 | scaffold inventory와 테스트 | proven |
| 실제 Local Profile의 승인 원문·개인 Harness | Local-only로 존재하며 release tree·diff·evidence bundle에서 제외 | privacy-verified |
| 공개 계약 변경에 따른 개인 card hash invalidation | 표준 Local Profile lint가 mismatch를 fail-closed 검출; 개인 파일은 수정하지 않음 | proven |

## Python-free와 runtime-neutral 경로

| Requirement | Evidence | Result |
|---|---|---|
| Windows NativeOnly가 Python을 호출하지 않음 | `check.ps1`; `tests/test_global_insight.py` | proven |
| Python 없는 clean distribution에서 계약과 Case hash 검사 | Git 배포 대상 759파일만 복사한 `.git` 없는 폴더에서 `check.ps1 -NativeOnly` pass | proven |
| `setup.cmd` 기본 preview가 Python 없이 동작 | `setup.cmd` → `scripts/setup-native.ps1`; mutation false preview pass | proven |
| qmd·Obsidian·MCP·agent-team optional | README와 runtime dispatch | proven |
| Codex·Claude·Single-agent·No-team이 동일 artifact·안전 계약 사용 | case/runtime manifests와 dispatch | contract-proven |
| 실제 Codex·Claude 동일 입력 반복 evidence | 각 새 Case benchmark 0/60 | pending-external |

## Case와 Golden Journey

| Requirement | Evidence | Result |
|---|---|---|
| Agentic AI T0/T1 공식 공개 fixture와 exact SHA256 | `cases/research/agentic-ai-change-radar/fixtures/manifest.json`; public source records 6개 | proven |
| T1이 new·strengthened·revised·contradicted·stale·retirement-candidate·unknown 재현 | `expected/t1-change-set.md`; validator와 test | proven |
| FAB Logistics Digital Twin이 GEM300·물류 twin·Object-Link-Action을 연결하고 유료 전문을 추정하지 않음 | FAB Case method, public fixture 5개, output contract | proven |
| Scientific Foundation Model이 law·assumption·prediction·reproduction·counterexample을 분리 | Scientific Case method, public fixture 5개, output contract | proven |
| AI Radar가 승인 revision 1을 보존하고 새 공개 근거를 revision 2 review 후보와 동일 Query diff로 연결 | `research/ai-radar/runs/2026-08-08-01/` | proven |
| FAB Case가 baseline을 AAS·OPC UA·ontology action delta와 단계형 pilot 가설로 성장 | `cases/strategy/fab-logistics-digital-twin/knowledge-growth/2026-08-08-01/` | contract-proven |
| Scientific Case가 baseline을 물리 제약 위치·scope·artifact/reproduction delta로 성장 | `cases/strategy/scientific-foundation-model-knowledge/knowledge-growth/2026-08-08-01/` | contract-proven |
| 세 Case 모두 Community이며 generic Skill을 조기 생성하지 않음 | catalog, manifests, tests, `.agents/.claude` inventory | proven |
| 3 Cases의 stable operation·baseline improvement·cross-Case regression 후에만 Skill 제안 | knowledge-growth 후보는 존재하지만 frozen cross-runtime benchmark와 사람 Acceptance는 없음 | pending-external |

## 오류·resume와 검증 계층

| Requirement | Evidence | Result |
|---|---|---|
| source retry 1회, partial/blocked, access limitation, hash invalidation, duplicate skip, contradiction review | executable native fixtures, artifact contract, Case orchestrators/methods | proven |
| post-write fast gate와 scoped lint/Health/Review 분리 | runtime contract, executable fixtures, `global_insight_native_check.ps1` | proven |
| public fixture·role·DAG·runtime·eval·hash·Reference 과장 검사 | `case_harness_check.py`, `meta_harness_check.py`, generated builders | proven |
| 관리자 전체 gate | public clean checkout `check.ps1`; unittest 118 pass, 1 skip | proven |
| 최소 비개발자 2명 자연어 Acceptance | 실제 tester evidence 없음 | pending-external |

## 결론

저장소 안에서 구현·정적 검증·Python-free clean distribution으로 증명할 수 있는 항목은 완료됐습니다. Local Private 개인 카드는 release 후보에서 제외되며, 공개 계약 hash drift는 자동 수정하지 않고 Review 대상으로 남습니다. 다음 세 항목은 현재 agent가 임의로 만들거나 대체할 수 없는 외부 evidence입니다.

1. Claude를 포함한 frozen cross-runtime 반복·baseline·blind comparison
2. 비개발자 2명의 자연어 Acceptance
3. 실제 BoI Wiki validator evidence

이 세 항목 전에는 새 Case 상태를 `verified` 또는 `reference`로 올리거나 generic Skill을 제안하지 않습니다.
