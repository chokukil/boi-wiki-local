# BoI Wiki Local Case Harness Catalog

이 카탈로그는 `boi-harness-builder` Meta Factory가 만들어 내는 실사례 모음입니다. `revfactory/harness-100`이 `revfactory/harness`의 결과물 예시를 모아 놓은 것처럼, 이 디렉터리는 BoI Wiki와 Second Brain에 적용한 결과물의 수준을 보여 줍니다. Meta Factory 자체는 `.agents/skills/boi-harness-builder/`에 있으며 이 카탈로그와 동일한 것이 아닙니다.

각 사례는 비개발자도 한 문장으로 재사용할 수 있는 실행 패키지입니다. 도메인별 제품 기능이나 전역 Skill이 아니라 기존 범용 BoI Skill을 조합하며, 반복 실행에서 공통 동작이 검증된 경우에만 Meta Factory가 범용 Skill 승격을 제안합니다.

## 이번 단계의 공개 범위

- `community`: 정적 계약과 보안 검사를 통과했지만 실제 반복 실행 검증 전
- `verified`: 최소 한 런타임의 실제 실행 evidence 보유
- `reference`: Codex·Claude 반복 비교, 사용자 Acceptance, BoI Wiki contract를 모두 통과

제품의 횡단 기반 사례는 하나를 유지하고, Global Insight 계획에서 사용자가 명시적으로 승인한 공개 source 기반 Case 세 개를 추가합니다.

- [Flagship Second Brain](flagship/second-brain/CASE.md) — 가장 중요한 횡단 Harness
- [SK하이닉스 Agentic AI Change Radar](research/agentic-ai-change-radar/CASE.md) — 첫 Golden Journey
- [FAB Logistics Digital Twin](strategy/fab-logistics-digital-twin/CASE.md) — 두 번째 전략 Case
- [Scientific Foundation Model Knowledge](strategy/scientific-foundation-model-knowledge/CASE.md) — 세 번째 장기 지식 Case

세 사례의 Meta Harness 실행, Second Brain revision 성장과 BoI Wiki promotion 경계를 한 흐름으로 보려면 [세 Golden Journey 통합 지도](GOLDEN-JOURNEYS.md)를 봅니다.

현재 Flagship Second Brain의 일부 Codex 실행만 실제 Windows evidence를 보유합니다. 세 Global Insight Case에는 public source record와 정적 계약뿐 아니라 baseline→후보 delta, source-first review와 동일 Query 비교를 포함한 knowledge-growth artifact가 있습니다. 다만 실제 Codex·Claude 반복, 비개발자 Acceptance, domain review와 실제 BoI Wiki contract는 `pending external gate`입니다. 이 gate들은 Case 산출물 자체의 blocker가 아니지만, 통과 전에는 어떤 Case도 Verified·Reference·production-ready로 표시하지 않습니다.

세 Case가 존재한다는 사실만으로 새 generic Skill을 만들지 않습니다. 동일한 stable operation, baseline 개선, cross-Case regression과 maintainer 승인이 실제 evidence로 확인된 뒤에만 Meta Factory가 Skill 승격을 제안합니다.

구조적 기준과 비채택 항목은 [Meta Harness source ledger](../research/meta-harness-source-ledger.md)에 기록했습니다. `scripts/case_harness_check.py`는 정적 계약과 허위 Reference 주장을 검사하고, `scripts/case_benchmark.py`는 실제 저장된 run artifact·SHA256·assertion·blind comparison만 집계합니다. 두 도구는 관리자·CI용이며 일반 사용자 요구사항이 아닙니다.

## 보존된 범용 실험 Case 초안

아래 초안은 삭제하지 않지만 `catalog.json`의 공식 공개 후보, 현재 검증 범위, 제품 대표 사례에는 포함하지 않습니다. 앞으로 도메인 사례는 실제 담당자가 방법론·입력·검토 기준을 소유하고 사용 성공을 검증한 뒤에만 Meta Harness의 `audit` 또는 `evolve` 모드로 등록합니다.

- 회의와 주간 활동 — 로컬에 보존된 실험 초안
- 기술 조사 — 로컬에 보존된 실험 초안
- 장애와 품질 이슈 — 로컬에 보존된 실험 초안
- 인수인계와 온보딩 — 로컬에 보존된 실험 초안
- API·Event·Workflow — 로컬에 보존된 실험 초안

## 한 문장으로 시작

```text
내가 하는 업무를 설명할게. 이 업무에서 좋은 지식을 만들고 BoI Wiki에 축적할 수 있도록 역할, Skill, 작업 흐름, 검토 기준을 포함한 Harness를 구성해줘.
```

새 사례 등록:

```text
방금 성공한 업무 흐름을 기존 Case와 Skill에 중복되지 않는지 먼저 확인하고, 다른 구성원도 재사용할 수 있는 Community Case 후보로 정리해줘. 실제 업무 데이터는 제거하고 합성 예제로 바꿔줘.
```
