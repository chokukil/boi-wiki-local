# BoI Wiki Local Meta Harness 현재 단계 상태

기준일: 2026-08-03

이 문서는 active 상태로 진행 중인 제품 작업을 사용자 기능과 관리자 평가 evidence로 분리해 기록합니다. benchmark 횟수는 제품 정의를 결정하지 않습니다.

현재 단계는 **Meta Harness Core와 Second Brain Flagship의 내부 후보 산출물을 마무리하는 범위**입니다. 외부 시스템이나 별도 참여자가 필요한 검증은 내부 작업을 멈추게 하는 blocker가 아니라, 향후 Reference·full release 승격을 위한 `pending external gate`로 관리합니다.

## 제품 정의

BoI Wiki Local은 사용자의 업무 설명을 BoI Wiki 활용 Harness로 구성하고, 개인 지식을 Local Second Brain에서 안전하게 축적한 뒤 검토된 조직 지식으로 연결하는 Meta Harness입니다.

## 네 계층

| 계층 | 유지 자산 | 사용자 노출 |
|---|---|---|
| A. Meta Harness Core | boi-harness-builder, 기존 BoI Skills 조합, 역할·DAG·산출물·review, OKF·BoI·promotion 경계 | 기본 |
| B. Flagship Capability | boi-second-brain, 대화·메일·웹·문서·자료 폴더, 보강·교정·충돌·Query·Lint·Review | 기본 선택 |
| C. Flagship Case Candidate | cases/flagship/second-brain (`community`) | 사례 허브 |
| D. Admin·CI | fixture builders, evaluator, oracle, blind comparison, importer, benchmark evidence | 관리자 문서만 |

도메인별 합성 사례는 현재 공개 범위에 포함하지 않습니다. 실제 담당자가 방법론·입력·검토 책임을 소유한 Case를 제안할 때만 Meta Harness 계약으로 다시 검토하며, 전역 release gate에는 도메인 전용 상태나 검토자를 두지 않습니다.

README·연결형 Wiki·공식 Case catalog·Meta Harness Core·Second Brain Skill에는 합성 수율 사례나 수율 전용 Skill 참조가 없습니다. `wafer-map-image` 문자열은 2.2 시절 Local 문서를 읽기 위한 deprecated evidence type 별칭으로만 남아 있고 신규 자료에는 범용 `image`를 생성합니다. pinned HarnessPackage와 기존 개인 예제 문서의 wafer 용어는 별도 기존 자산이므로 합성 수율 Case로 간주해 삭제하지 않습니다.

공식 `cases/catalog.json`에는 Flagship Second Brain 하나만 등록합니다. 회의·조사·장애·온보딩·API 초안은 삭제하지 않았지만 공개 후보와 현재 검증 분모에서 제외한 실험 자산입니다.

README·Start Here·Case catalog·Flagship CASE의 로컬 링크를 제품 진입점 회귀로 검사합니다. Flagship CASE는 현재 `community` 상태와 검증·미검증 범위만 사용자 언어로 설명하고, run artifact·assertion·blind comparison 같은 실행 세부는 관리자 BENCHMARK로 분리합니다.

Meta Harness Core는 Phase 0–7의 `Audit → Frame → Skill·지식 흐름 → 역할·DAG → Local/Remote 계약 → Build → Validate → Evolve`를 사용합니다. 실제 실패는 가장 작은 소유 계층에 환류하며 Case 실패 하나만으로 범용 Skill을 추가하지 않습니다.

## 현재 evidence

| 항목 | 현재 상태 | 해석 |
|---|---|---|
| Codex p01~p07 repetition 1 | with-Harness/baseline 14회 보존 | 부분 evidence |
| blind comparison | 7쌍 모두 with-Harness 승리 | 서로 다른 prompt의 1회 표본 |
| with-Harness deterministic assertions | 7/7 통과 | frozen scenario의 객관 assertion |
| with-Harness rubric 중앙값 | 95/100 | 반복 안정성 또는 일반 사용자 품질 증명 아님 |
| p07 | 18/18, blind 98; 실패 이력 별도 보존 | 중단 후 재개 시나리오 부분 evidence |
| p08 | 미실행 | prompt·assertion·관리자 코드 초안만 동결 |
| Claude | pending external gate | cross-runtime evidence 없음; 이번 단계 실행 금지 |
| 비개발자 Acceptance | pending external gate | 사용자 배포 evidence 없음 |
| 실제 BoI Wiki validator | pending external gate | canonical 호환 완료 주장 불가 |
| 사내 Bitbucket | pending external gate | 현재 외부 접속 불가; GitHub origin 기준만 검증 |

## 현재 단계 완료 범위

- `boi-harness-builder`가 범용 업무 설명을 기존 BoI Skills, 역할, DAG, 산출물, 독립 review, Local/Remote 경계로 구성하는 Meta Harness Core 계약을 제공한다.
- `boi-second-brain`이 자연어 설정, 대화 지식 유지관리, 혼합 자료 폴더 preview·승인·재개, 중복·교정·충돌 처리, 출처 기반 query, 일반 knowledge promotion preview를 제공한다.
- 모든 Profile 대상 Local Markdown은 OKF 0.1 + BoI Profile 0.1-local과 Local Private 경계를 유지하며, canonical 후보는 별도 compiler 경계에서만 만든다.
- Python·Obsidian·MCP 없이 일반 사용자 핵심 여정을 수행할 수 있고, Obsidian과 MCP는 선택 기능으로 남는다.
- README_KO, Start Here, 설치 요청문, 자동 정리 성향, 자료 폴더, 기억 교정, 재개, promotion 경계, 문제 해결, CASE와 BENCHMARK가 실제 현재 동작에 맞춰 연결된다.
- 공식 Case catalog는 Flagship Second Brain 하나만 공개 후보로 등록하며, 합성 도메인 사례는 현재 제품 범위와 검증 분모에서 제외한다.

## 이번 단계에서 시작하지 않는 작업

- 전체 456회 benchmark
- Codex repetition 2·3와 Claude 실행
- p08 및 새 oracle 확장
- 신규 Reference Case와 도메인 fixture
- 커뮤니티 플러그인 설치
- 새 화면 촬영
- remote submit와 MCP write
- 평가 통과를 위한 fixture 특화 Skill 수정

기존 p01~p07 실행 결과, 실패 ledger, p08 prompt·assertion·관리자 코드 초안은 삭제하지 않고 Admin·CI 자산으로 보존합니다.

## 사용자에게 보이는 진입점

1. README_KO.md의 업무 Harness 한 문장 요청
2. README_KO.md의 Second Brain 한 문장 요청
3. templates/second-brain-guide/00-start-here.md
4. templates/second-brain-guide/01-meta-harness-map.md
5. templates/second-brain-guide/02-build-your-harness.md
6. cases/flagship/second-brain/CASE.md

Python·Obsidian·MCP는 기본 사용자 요구사항이 아닙니다. 일반 사용자 Wiki는 자연어 Agent 요청을 사용하며 Python 명령과 관리자 구현 용어를 정적 검사로 차단합니다. Windows `setup.cmd`, `install.cmd`, `install.ps1`, `update.cmd`, `update.ps1`은 PowerShell-native 사용자 경로를 사용하고 `ExecutionPolicy Bypass`를 사용하지 않습니다. Agent-driven setup은 파일을 바꾸지 않는 `boi-local-setup-preview/v1`을 먼저 만들고, 채팅에서 승인한 같은 Profile·정리 방식·자료 폴더의 exact plan hash만 적용합니다. hash가 다르면 `.env`, Profile, 자료 폴더를 만들기 전에 중단하며 사용자는 기술값을 복사하지 않습니다. Native check는 Meta Harness·Core Skills·Local Profile·연결형 Wiki·Windows 진입점만 요구하며 evaluator·fixture builder·benchmark·acceptance·contract oracle 파일은 Admin·CI manifest에서만 검사합니다. 일반 업데이트는 Harness lock·offline snapshot 일치를 reduced verification으로 확인하고, canonical checksum·전체 lint·contract oracle은 관리자·CI 계층에 남깁니다. Codex·Claude는 `C:\Users\<계정>\Projects\boi-wiki-local` Windows clone 자체를 작업 폴더로 열어야 프로젝트의 Meta Harness·Second Brain Skill을 발견합니다. 설치기는 WSL 경로와 핵심 Skill이 빠진 불완전 clone을 개인 Profile 작성 전에 차단하고 `notes/harnesses/`를 함께 구성합니다. WSL clone이나 전역 Skill 복사로 우회하지 않습니다.

Codex와 Claude의 managed bootstrap은 “반복 업무 설명을 재사용 가능한 BoI Harness로 구성”하는 자연어 요청을 `boi-harness-builder`로 라우팅합니다. 온라인 Harness sync가 수행돼도 이 로컬 Meta Harness·Second Brain 진입 계약이 재생성되도록 generator 회귀 검사를 둡니다.

`boi-harness-builder`의 기본 factory 결과는 사용자 승인 후 `notes/harnesses/`에 저장되는 개인 Local Harness 카드입니다. 일반 생성·재사용에는 Case contract나 quality gate를 선행 로드하지 않으며, Case packaging·평가·Verified/Reference 상태 주장은 사용자가 별도로 요청한 관리자 흐름에서만 시작합니다. 완료 카드는 `create | extend | ...` 또는 가능한 책임 계층 전체를 그대로 남길 수 없고 이번 실행의 mode와 evolution owner를 하나로 확정해야 합니다.

Flagship Second Brain의 실제 orchestrator와 output contract도 구성원 실행을 기준으로 분리했습니다. 일반 실행 입력은 활성 Local Profile, 사용자가 선택한 대화·자료 범위, 기존 지식과 재개 상태이며, 결과는 해당 Local Profile의 재사용 지식과 채팅 완료 요약입니다. fixture·seed·prompt catalog, `output/` evaluator bundle과 구조화된 assertion report는 Admin·CI 격리 실행에만 추가됩니다. 범용 Skill의 batch 크기는 source 수에 하드코딩하지 않고 현재 context·자료 복잡도·충돌 위험·기존 지식 비교량으로 결정합니다.

비개발자 walkthrough와 output contract는 실제 사용자 경로인 `promotion-drafts/<시각>-<제목>-<범위>-<hash>-preflight.*`를 안내합니다. Source·knowledge inventory와 consolidation plan은 Single-agent 일반 실행에서 논리적 handoff 또는 승인·재개 상태로 유지하며 별도 `intermediate/*.json`을 기본 생성하지 않습니다. 구조화 intermediate bundle은 Reduced·Full 역할 handoff 또는 Admin·CI evidence에만 materialize합니다. 사용자 답변에는 근거 문서 링크와 상태를 먼저 보여주고 Local path·SHA256·candidate hash는 검증 세부 정보로 둡니다.

승인된 개인 Harness는 채팅 설계로 끝내지 않고 active Local Profile의 `notes/harnesses/<slug>.md`에 `boi/local-guide` Profile 카드로 보존합니다. 정확한 승인 요청은 Local capture와 SHA256 provenance로 연결하고, 다음 세션에는 저장된 카드를 찾아 같은 역할·DAG·산출물·검토 계약을 실행합니다. 기존 카드 실행은 builder 재호출·새 Skill 생성·카드 재작성을 요구하지 않습니다. 계약 변경 때만 `audit` 또는 `evolve`를 사용하며, 현재·변경 후보 hash 미리보기 승인 후 기존 카드를 `_archive/harnesses/<시각>/`에 byte-for-byte 보존합니다. 새 카드는 동일한 logical `boi_id`와 기존 provenance를 유지하고 이전 카드 경로·SHA256, 승인 preview hash, 변경 이유·승인 상태를 evolution 기록에 연결합니다.

관리자 회귀는 실제 임시 Profile에서 승인 요청 capture를 생성하고 그 파일 hash를 `source_refs`와 `generated_from`에 가진 Harness 카드를 실체화해 Local lint를 통과시킵니다. `notes/harnesses/` 카드에는 요청·감사·지식 흐름·Skill 소유권·역할과 독립 검토·DAG·scale mode·산출물·오류와 재개·OKF/BoI 경계·비개발자 walkthrough·검증 상태·evolution 기록의 13개 본문 계약을 요구합니다. 제목만 있는 카드, 실질 신호가 빠진 카드, `TODO`·`TBD`·꺾쇠괄호 자리표시자는 차단합니다. 필수 오류 처리 섹션, 다음 세션 실행 요청문, reviewer 권한, exact candidate hash 같은 핵심 내용을 제거한 카드도 lint에서 실패합니다.

개인 Harness 카드는 `boi/local-guide` 형식을 사용하더라도 직접 promotion할 수 없습니다. compiler는 `notes/harnesses/` 경로와 `ConfiguredHarness` 태그를 모두 검사하며, 별도의 sanitized body·공개 출처·reviewer가 주어져도 개인 카드 자체를 차단합니다. 조직 공유는 개인 실행 설정을 제거한 별도 일반 가이드 또는 비식별 fixture와 검토 evidence를 갖춘 Community Case로 정제한 뒤 진행합니다.

공통 `boi-wiki-local` Skill은 Second Brain에 한정하지 않고 모든 substantive Local Markdown에 OKF 0.1, BoI Profile 0.1-local, 전체 Local Profile 필드, 구조화된 `source_refs`·`generated_from`, 빈 wrapper 금지, 직접 promotion 차단과 sanitized canonical preview 계약을 요구합니다. 구조화된 `generated_from`은 `type`·`ref`·정확한 SHA256을 린트하며 Local parent가 바뀌면 hash mismatch로 차단합니다. 기존 scalar BoI ID 표현은 이전 Profile 호환을 위해 계속 읽습니다. Codex와 Claude Core Skill은 `SKILL.md`만이 아니라 builder references와 runtime metadata를 포함한 전체 필수 트리를 `.boi-harness/core-runtime-manifest.json`과 byte-identical mirror로 검증합니다. Windows 설치와 native check는 양쪽에서 같은 필수 파일이 빠진 경우, 한쪽만 누락된 경우, 0바이트와 hash 불일치를 모두 Profile 작성 전에 차단합니다. update도 fetch한 stable 후보의 manifest·bootstrap·전체 Core Skill Git blob을 pull 전에 검사해 손상 release로의 fast-forward를 막습니다.

공통 Skill의 일반 구성원 repository 검증은 `check.ps1 -NativeOnly`이며 Python 기반 full suite는 관리자·CI에서만 실행합니다. 읽기 전용 검색·설명, 변경 전 preview, 차단된 작업, `이미 반영됨` 결과에서는 단순 실행 사실을 남기기 위해 index나 `data/boi/log.md`를 변경하지 않습니다. 실제 Local 문서·archive·promotion preview가 materialize된 경우에만 영향을 받은 navigation과 audit surface를 갱신합니다.

승인 후 현재 Agent가 실제로 열어 확인할 수 있는 이메일·웹·Markdown·텍스트·표·PDF·이미지는 원본 SHA256과 확인 범위를 보존하면서 같은 작업 안에서 재사용 가능한 `source-knowledge` 한 문서로 정리합니다. PDF·이미지는 확인한 페이지·화면 영역과 읽지 못한 부분을 명시하며, 보이지 않은 내용을 추측하거나 OCR을 기본 동작으로 사용하지 않습니다. 현재 runtime이 신뢰성 있게 읽을 수 없는 바이너리, 지원하지 않는 형식, 불완전 렌더링, 격리 대상만 `source-record`로 보류합니다.

자료 폴더의 첫 정리는 Profile을 쓰지 않는 preview로 대상·중복·묶음·기존 지식 관계·Local 경계를 먼저 보여주고 사용자가 범위를 한 번 승인합니다. 이후 파일마다 승인을 반복하지 않습니다. 중단 후에는 승인 plan hash, 현재 source manifest hash, completed·remaining·next batch 순서를 다시 검증해 동일하면 추가 승인 없이 다음 묶음부터 재개하고, 하나라도 달라지면 쓰기 전에 새 preview로 돌아갑니다. walkthrough와 연결형 Wiki는 이 자연어 재개 요청과 중복 방지 결과를 동일하게 안내합니다.

정제된 Local knowledge라도 기본 설명·검토 본문에 `Local Private`, `local_only`, `local_owner_ref` 같은 Local 전용 운영 문구가 남아 있으면 Team/Public canonical preview를 차단합니다. compiler가 원문을 임의로 잘라내지 않으며, 사용자가 검토한 공유용 제목·설명·본문과 remote-safe source refs를 별도로 제공한 경우에만 preview-ready가 됩니다. 회귀는 미정제 source-knowledge 차단, 정제본 통과, reviewer·team scope·Public 출처·민감정보·projection sanitization을 함께 확인합니다.

Action Author, Context Pack Builder, Dictionary Author, Event Workflow Planner, Langflow Planner, SOP Flow Visualizer, Workflow Simulator도 모두 `boi-wiki-local`을 부모 계약으로 먼저 적용합니다. 따라서 Meta Harness가 어느 기존 범용 Skill을 조합해도 공통 Profile·provenance·Local promotion 경계가 빠지지 않으며, 각 Skill은 자기 도메인 산출물 계약만 추가합니다.

`boi-harness-builder`에는 기존 Skill의 최소 소유권 라우팅 표를 둡니다. Action·Context Pack·Dictionary·Event Workflow·Langflow·SOP 시각화·Workflow simulation·Second Brain 요청의 should-trigger와 가까운 near-miss를 구분하고, 둘 이상의 Skill은 앞 Skill의 선언된 산출물이 다음 DAG 노드의 입력일 때만 조합합니다. Second Brain은 장기 보존·재검색·교정 이력·review cadence가 필요한 경우에만 연결합니다.

## 화면 상태

- 현재 제품 범위와 맞지 않는 과거 도메인 전용 화면은 media manifest와 배포 자산에서 제거했습니다.
- screen-01은 최대화된 Windows File Explorer에서 Windows clone과 `setup.cmd`를 보여 주는 1760px 화면으로 재촬영했습니다.
- screen-04는 Obsidian 1.13.4에서 Harness-first Start Here를 보여 주는 1760px 화면으로 재촬영했습니다.
- 두 화면은 Wiki 본문과 원본 크기 링크에 다시 연결했고 media manifest SHA256·크기·합성 여부 검사를 통과했습니다.
- screen-28~34는 실제 Codex·Claude 앱 캡처가 아니라 흐름 설명용 합성 교육 이미지입니다. 현재 가이드의 보조 그림으로는 유지하지만 실제 사용자 화면으로 오인하지 않도록 모두 재촬영 대상으로 표시했습니다.
- 기능과 Wiki 계약이 동결된 뒤 현재 Windows Codex 또는 Claude 앱에서 이 7장을 다시 촬영해야 합니다. 그전까지 `release_screen_ready: false`이며, 이번 정리에서는 이미지 파일이나 hash를 변경하지 않았습니다.
- guide release `3.0.0`을 합성 Profile `0000000`에 preview → confirmation → backup → apply 순서로 동기화했습니다. 화면 28~34의 `requires_recapture_for_release: true`가 설치본 media manifest에도 반영됐고, 재확인 preview는 변경 0건입니다. 이전 manifest는 `_archive/guides/20260803-024950/`에 보존했으며 이미지 bytes는 변경하지 않았습니다.

## Obsidian 선택 경로 감사

- Obsidian은 계속 선택 기능이며, Core Search·Properties·Backlinks·Graph·Bases·Canvas만으로 안내한다. Community plugin은 자동 설치하지 않는다.
- Graph 기본 필터는 `notes/capture-inbox`, `notes/guide`, `promotion-drafts`, `usage-examples`, `_archive`를 `-path:`로 제외한다. Graph와 Canvas의 선은 provenance가 아니며 canonical 관계는 `source_refs`, `generated_from`, 표준 Markdown 링크다.
- 새 Vault에서 설정 파일이 없을 때 생성하는 `core-plugins.json`은 실제 Windows Obsidian 1.13.4와 같은 boolean-object 형식을 사용한다.
- 기존 `.obsidian/app.json`, `core-plugins.json`, `graph.json`은 모두 보존한다. 기존 Vault에서는 사용자가 Graph의 **Filters → Search files**에 필터를 붙여 넣는다.
- 공식 Obsidian 문서 기준으로 Graph·Canvas·Bases는 Core 기능이고, Search는 `path:` 연산자와 앞의 `-`를 사용한 제외를 지원한다.
- `obsidian-preview`는 앱·Community plugin을 설치하지 않았고 합성 Profile `0000000`의 기존 설정 3개를 모두 `preserve`로 판정했다.

## readiness

| 상태 | 값 | 이유 |
|---|---:|---|
| meta_harness_ready | true | Meta Harness·Case 경계 정적 검사와 전체 로컬 regression 통과 |
| core_automated_ready | true | 관리자용 111개 단위 회귀와 일반 사용자용 Native `check.cmd`가 각각 통과; hash-bound PowerShell-native 무-Python setup·update, Core Skill 전체 트리 manifest, 제품 진입점 링크, 읽을 수 있는 PDF·이미지의 단일 재사용 지식 변환, 원본·파생 provenance와 Local Harness 카드 계약 실패 0건 |
| second_brain_codex_rc1_ready | false | p08 미실행 상태로 범위를 동결 |
| second_brain_reference_ready | false | 양 runtime·반복·Acceptance 미완료 |
| cross_runtime_eval_ready | false | Claude 미실행 |
| non_developer_acceptance_ready | false | 비개발자 검증 미완료 |
| boi_contract_ready | false | 실제 대상 validator 미완료 |
| full_release_ready | false | pending external gate 미완료 |

## Pending external gates

다음 네 항목은 현재 내부 산출물 완료를 막지 않습니다. 다만 검증 evidence가 들어오기 전까지 해당 상위 상태와 `full_release_ready`를 참으로 만들 수 없습니다.

| gate | 현재 기록 | 해제 시 가능한 주장 |
|---|---|---|
| 실제 대상 BoI Wiki validator | pending external gate | `boi_contract_ready` 검토 |
| 사내 Bitbucket clone·origin 교체 | pending external gate | 사내 배포 경로 검증 |
| Claude 동일 계약 실행 | pending external gate | `cross_runtime_eval_ready` 검토 |
| 비개발자 Acceptance | pending external gate | `non_developer_acceptance_ready` 검토 |

이번 단계에서는 validator 호출, Bitbucket 접속, Claude 평가, 사용자 파일럿을 시도하지 않았습니다. 이 네 항목의 부재는 blocker나 실패로 기록하지 않고, 미실행 외부 gate로만 기록합니다.

## 다음 단계 후보

1. 문서·Skill·정적 regression만 안정화하고 RC 구조를 동결
2. 비개발자 두 명의 자연어 사용자 여정을 먼저 검증
3. 실제 BoI Wiki validator 접근이 가능해질 때 canonical contract만 검증
4. 담당 엔지니어가 제안하는 도메인 Case를 별도 review
