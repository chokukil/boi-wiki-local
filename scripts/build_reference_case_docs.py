#!/usr/bin/env python3
"""Build documentation for the three Global Insight public Cases.

Generated pages are plain runtime-neutral distribution artifacts. Python is a
maintainer oracle only and is not needed to run the Cases.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


COMMON_FAILURES = [
    ("필수 source 접근 불가", "partial 또는 blocked와 실제 확인 범위를 기록", "source 확보 또는 범위 재승인"),
    ("source hash 변경", "dependent artifact와 기존 preview 승인 무효화", "새 hash로 Capture부터 재개"),
    ("contradiction", "양쪽 evidence를 보존하고 review queue 등록", "사람의 Review 결정"),
    ("agent-team 없음", "동일 파일·handoff로 No-team sequential pass", "없음; 정상 fallback"),
]


CASES = {
    "cases/research/agentic-ai-change-radar": {
        "title": "SK하이닉스 Agentic AI Change Radar",
        "audience": "공개 자료로 Agentic AI 변화와 적용 가설을 검토하는 연구·기술기획 구성원",
        "prompt": "이번 주 Agentic AI runtime, orchestration, tool use, memory·context, evaluation과 security에서 바뀐 내용만 기존 지식과 비교해 변경 세트와 검토 목록으로 보여줘.",
        "trigger": "기존 claim snapshot과 새 공개 자료를 비교해 변화만 반영 후보로 만들 때",
        "near_miss": "URL 하나의 단순 요약, 무승인 최신 외부 조사, 주문하지 않은 주간 보고서 생성",
        "pattern": "route and scope → source capture → evidence comparison → delta curation → independent review",
        "roles": [
            ("research-coordinator", "요청을 일곱 도구 중 하나로 라우팅하고 범위·성공 조건·phase exit를 고정", "사용자 요청, 기존 topic, 승인 범위", "intermediate/request-contract.json", "도구, 범위, 기준 시점, reviewer와 주문형 산출물이 명시됨", "claim 승인 또는 DeepResearch 무승인 실행"),
            ("source-researcher", "공식 문서·저장소·원 논문을 우선 수집하고 manifest와 접근 제한을 기록", "T0/T1 source records와 승인된 live source", "intermediate/source-manifest.json", "모든 source에 URL, date, checked scope, hash와 verification level이 있음", "snippet을 확정 근거로 사용하거나 읽지 못한 전문을 읽었다고 주장"),
            ("evidence-analyst", "claim, evidence, counterevidence, contradiction과 unknown을 분리", "source manifest와 기존 claim snapshot", "intermediate/evidence-matrix.md", "material claim마다 양방향 evidence와 unknown이 연결됨", "기존 판단 덮어쓰기 또는 SK하이닉스 비공개 조건 추정"),
            ("change-curator", "delta를 분류하고 이전 snapshot, 이유, downstream 영향과 다음 검토일을 보존", "evidence matrix와 기존 history", "change-set.md와 review-queue.md", "모든 변화가 허용 delta enum과 source ref를 가짐", "confidence·폐기·contradiction을 독단 확정하거나 변화 없는데 보고서 생성"),
            ("independent-reviewer", "원문 record와 manifest부터 재검토해 approve·revise·partial·blocked 판정", "T0/T1 records, manifest, evidence, change set", "reviewer-report.json", "중요 claim과 contradiction의 evidence locator가 독립 확인됨", "producer 요약만 읽거나 self-approval"),
        ],
        "artifacts": [
            ("source-manifest.json", "URL, dates, checked scope, SHA256, source_refs, generated_from"),
            ("evidence-matrix.md", "claim, support, counterevidence, verification, uncertainty"),
            ("change-set.md", "new, strengthened, revised, contradicted, stale, retirement-candidate, unknown"),
            ("review-queue.md", "priority, reason, reviewer, next review date, follow-up question"),
        ],
        "failures": COMMON_FAILURES + [("새 자료 또는 변화 없음", "빈 change set으로 정상 종료", "다음 정기 검토")],
        "eligible": "사람이 검토한 정제 지식과 주문된 sanitized brief candidate",
        "blocked": "raw source, evidence, hypothesis, analysis log, agent memory, 개인 Harness card",
        "normal": "T0→T1에서 TypeScript 지원은 stale/revised, MCP discovery는 contradicted/revised, 평가 도구는 strengthened, Agent Builder는 new, SK하이닉스 적용성은 unknown으로 남는다.",
        "cadence": "주간 또는 사용자가 요청할 때",
        "case_type": "golden-journey",
    },
    "cases/strategy/fab-logistics-digital-twin": {
        "title": "FAB Logistics Digital Twin",
        "audience": "SEMI 표준, FAB 물류 자동화, Digital Twin과 Ontology 연결을 공개 자료로 검토하는 구성원",
        "prompt": "SEMI GEM300 공개 자료와 제조·물류 Digital Twin, Palantir식 Object·Link·Action을 연결해 FAB 물류 적용 가설과 검증 질문을 만들어줘. 내부 운영 조건은 추정하지 마.",
        "trigger": "Carrier·Substrate·Control Job과 물류 twin·ontology의 연결고리를 검토할 때",
        "near_miss": "유료 SEMI 전문 내용을 추정, 실제 FAB 성능 수치 생성, 운영 Action 실행 또는 특정 벤더 선정",
        "pattern": "public standards boundary → twin capability map → ontology mapping → pilot hypothesis → independent review",
        "roles": [
            ("research-coordinator", "공개 범위, 제외 범위, 의사결정 질문과 검토 주기를 고정", "사용자 질문과 public-only policy", "intermediate/request-contract.json", "유료 표준·내부 데이터·벤더 선정이 제외됨", "비공개 조건 또는 normative field 추정"),
            ("standards-source-researcher", "SEMI 공개 요약과 제조·물류 digital twin 1차 자료를 manifest로 수집", "public source records", "intermediate/source-manifest.json", "GEM300 공개 범위와 접근 제한이 분리됨", "유료 전문을 확인했다고 주장"),
            ("twin-model-analyst", "Carrier·Substrate·Control Job, 물류 자산·상태·event·simulation을 capability map으로 연결", "source manifest", "intermediate/twin-capability-map.md", "관측 사실, 표준 개념, vendor claim과 가설이 구분됨", "공개 case signal을 SK하이닉스 성과로 일반화"),
            ("ontology-workflow-curator", "Object·Link·Action 후보와 human checkpoint가 있는 pilot hypothesis 작성", "capability map과 ontology docs", "ontology-map.md와 pilot-hypotheses.md", "각 Action은 권한·검증·rollback unknown을 가짐", "실제 action 실행 또는 Palantir 종속 schema 확정"),
            ("independent-reviewer", "source→표준 개념→twin→ontology→pilot 추론 사슬을 독립 검토", "모든 intermediate와 output", "reviewer-report.json", "추론 leap와 내부 검증 필요 항목이 명시됨", "벤더 문서만으로 효과·적합성 승인"),
        ],
        "artifacts": [
            ("source-manifest.json", "public standard scope, vendor docs, access limitations, hashes"),
            ("twin-capability-map.md", "asset, state, event, simulation, control boundary, evidence"),
            ("ontology-map.md", "Object, Property, Link, Event, Action, governance, unknown"),
            ("pilot-hypotheses.md", "hypothesis, public rationale, required internal data, safety gate, falsifier"),
        ],
        "failures": COMMON_FAILURES + [("유료 표준 전문 필요", "공개 요약까지만 partial", "정당한 접근권한과 reviewer")],
        "eligible": "검토된 개념 map과 내부 검증 전제의 pilot proposal candidate",
        "blocked": "유료 표준 본문, 추정한 FAB 수치, raw internal data, 실행 가능한 운영 Action",
        "normal": "GEM300의 Carrier·Substrate·Control Job 공개 개념을 twin 상태·event와 연결하고 Object·Link·Action 후보를 만들되, 실제 FAB 데이터 매핑과 효과는 unknown 및 내부 검증 항목으로 남긴다.",
        "cadence": "월간 또는 SEMI·vendor 공식 변경 시",
        "case_type": "strategy-case",
    },
    "cases/strategy/scientific-foundation-model-knowledge": {
        "title": "Scientific Foundation Model Knowledge",
        "audience": "물리·화학 법칙, 예측 성능과 반례를 장기적으로 추적하는 연구·기술기획 구성원",
        "prompt": "Scientific Foundation Model 자료를 법칙·가정·prediction·재현·반례·철회 상태로 정리하고, 시간이 지나도 유지할 지식과 다시 검토할 주장을 구분해줘.",
        "trigger": "논문과 후속 연구에서 물리·화학적 grounding과 실제 prediction evidence를 장기 비교할 때",
        "near_miss": "논문 초록만으로 full-text 검증 주장, 벤치마크를 보편 법칙 준수로 확대, 변화 없는 지식의 주기적 재작성",
        "pattern": "paper integrity → claim and assumption extraction → prediction/reproduction matrix → change curation → independent review",
        "roles": [
            ("research-coordinator", "연구 질문, discipline, validation level, review trigger와 주문 산출물을 고정", "사용자 질문과 기존 paper graph", "intermediate/request-contract.json", "근본 법칙과 빠른 동향의 검토 주기가 분리됨", "모든 분야를 하나의 foundation claim으로 합침"),
            ("paper-source-researcher", "원 논문, 정정·철회, 코드·데이터와 후속 연구를 우선 수집", "public paper records", "intermediate/source-manifest.json", "abstract/full text, peer-review, version, access가 구분됨", "abstract-only를 full-text verified로 표시"),
            ("scientific-evidence-analyst", "법칙, model assumption, prediction, benchmark, physical validation, 반례를 분리", "source manifest와 기존 claims", "intermediate/scientific-evidence-matrix.md", "주장마다 적용 domain과 falsifier가 있음", "성능을 물리적 정확성 또는 인과로 동일시"),
            ("change-curator", "후속·정정·재현으로 바뀐 claim만 delta로 기록하고 stable knowledge는 재작성하지 않음", "evidence matrix와 claim history", "change-set.md와 review-queue.md", "revision reason과 다음 검토 trigger가 source-linked", "새 논문 수만으로 confidence 상향 또는 negative result 삭제"),
            ("independent-reviewer", "논문 record와 실제 확인 범위부터 prediction·반례·재현 상태를 검토", "manifest, matrix, delta", "reviewer-report.json", "근본 법칙, 모델 가정, empirical claim과 unknown이 구분됨", "producer 해석 또는 인용 횟수만으로 승인"),
        ],
        "artifacts": [
            ("source-manifest.json", "paper version, review/access status, code/data, correction/retraction links"),
            ("scientific-evidence-matrix.md", "law, assumption, prediction, validation, counterexample, domain"),
            ("change-set.md", "only source-backed changes; stable claims untouched"),
            ("review-queue.md", "replication gap, contradiction, correction/retraction and next trigger"),
        ],
        "failures": COMMON_FAILURES + [("full text 또는 재현 artifact 없음", "abstract-only·not-reproduced 상태로 partial", "전문·코드·데이터 또는 독립 재현")],
        "eligible": "검토된 scientific claim map과 재현 상태가 명시된 장기 지식",
        "blocked": "저작권 원문, abstract 기반 확정 결론, 삭제된 negative result, 검토 전 적용 권고",
        "normal": "MatterGen·GraphCast·physics-guided models의 서로 다른 prediction evidence를 보존하고, 법칙 준수·generalization·재현 여부를 같은 것으로 취급하지 않으며 불확실성은 unknown으로 남긴다.",
        "cadence": "분기 또는 정정·철회·반례·중요 후속 연구 발생 시",
        "case_type": "long-term-knowledge-case",
    },
}


def case_page(spec: dict, fixture_id: str, source_count: int) -> str:
    golden_link = (
        "\n## Golden Journey oracle\n\n"
        "[T0 baseline snapshot](expected/t0-snapshot.md) · "
        "[T1 expected change set](expected/t1-change-set.md) · "
        "[expected review queue](expected/review-queue.md)\n"
        if spec["case_type"] == "golden-journey" else ""
    )
    return f'''# {spec["title"]}

상태: **Community — deterministic public source records {source_count}개, 실제 runtime evidence 미수집**

Case type: `{spec["case_type"]}`
기본 검토 주기: {spec["cadence"]}

## 한 문장으로 시작

```text
{spec["prompt"]}
```

## Trigger boundary

- 실행: {spec["trigger"]}
- Near-miss: {spec["near_miss"]}
- 기본 결과: 주문형 보고서가 아니라 change set, review queue 또는 현재 지식 기반 답변

## 검증 입력

Fixture `{fixture_id}`는 공개 1차 자료의 확인 범위와 SHA256을 고정한 source record {source_count}개입니다. 원문 전체 복제본이 아닙니다.

[Fixture 설명](fixtures/fixture.md) · [source pack](fixtures/source-pack.md) · [manifest](fixtures/manifest.json)

## Orchestration

Pattern: `{spec["pattern"]}`

5개 논리 역할 중 마지막 역할이 Independent Reviewer입니다. On-demand Synthesizer는 승인된 durable knowledge에서 요청된 brief·표·제안만 만드는 선택 pass이며 claim 상태를 변경하지 않습니다.

[역할과 hard fail](roles/roles.md) · [Dependency DAG](orchestrator.md) · [output contract](expected/OUTPUT-CONTRACT.md)

## 정상 결과

{spec["normal"]}

## Second Brain 연결 — 선택

- Second Brain이 없어도 현재 실행, review queue와 promotion preview까지 완료됩니다.
- 연결하면 검토된 durable knowledge만 기존 주제와 비교해 보강·교정하고 다음 Query와 Update에 재사용합니다.
- raw source, intermediate와 agent-memory는 기억으로 복사하거나 직접 promotion하지 않습니다.

## Local/Remote 경계

- promotion 가능: {spec["eligible"]}
- 직접 promotion 차단: {spec["blocked"]}
- MCP read와 agent runtime 사용은 remote upload 승인이 아님
- reviewer, target scope, sanitized exact hash와 별도 승인 전 remote submit 없음

이 Case는 아직 Verified, Reference 또는 production-ready를 주장하지 않습니다.
{golden_link}'''


def roles_page(spec: dict) -> str:
    rows = "\n".join(
        f"| {name} | {purpose} | `{output}` | {exit_criteria} | {hard_fail} |"
        for name, purpose, _inputs, output, exit_criteria, hard_fail in spec["roles"]
    )
    return f'''# Roles — {spec["title"]}

각 역할은 `boi-local-case-handoff/v1`으로 source hash, output hash, unknown, blocker와 review question을 넘깁니다.

| Role | 책임 | 주 산출물 | Exit criteria | Hard fail |
|---|---|---|---|---|
{rows}

Independent Reviewer는 producer 요약이 아니라 source manifest와 원문 record부터 읽습니다. Single-agent에서도 reviewer pass를 별도로 시작하며 중요한 의미 변경은 사람 Review 없이는 승인하지 않습니다.
'''


def orchestrator_page(spec: dict) -> str:
    roles = [row[0] for row in spec["roles"]]
    return f'''# Orchestrator — {spec["title"]}

## Dependency DAG

```mermaid
flowchart TD
    A["자연어 요청"] --> B["{roles[0]}: route·scope"]
    B --> C["{roles[1]}: source manifest"]
    C --> D["post-write fast gate"]
    D --> E["{roles[2]}: evidence·unknown"]
    E --> F["{roles[3]}: delta·history"]
    F --> G["scoped lint"]
    G --> H["{roles[4]}: independent review"]
    H -->|revise| E
    H -->|partial| I["partial + unresolved"]
    H -->|blocked| J["blocked + resume condition"]
    H -->|approve| K["사용자 승인 대기"]
    K -->|승인| L["Local durable knowledge"]
    K -->|거절| M["기존 상태 유지"]
    L --> N["Query·후속 Update"]
    L -->|명시 요청| O["On-demand Synthesizer"]
```

## Phase exit

각 phase는 input/output exact SHA256, supported claims, counterevidence, unknown, contradiction, blocker와 다음 진입 조건을 handoff에 기록합니다. source hash와 source manifest hash가 바뀌면 dependent artifact와 승인은 무효입니다.

## Scale modes

- Full: 역할을 독립 실행하고 reviewer는 모든 handoff 뒤에 실행합니다.
- Reduced: creator와 Independent Reviewer로 축소합니다.
- Single-agent: 역할별 순차 pass를 수행하고 reviewer pass에서 source부터 다시 읽습니다.
- No-team fallback: agent-team 없이 같은 파일, exit criteria와 handoff로 순차 실행합니다.

어떤 모드도 artifact나 안전 계약을 줄이지 않습니다.

## Failure, retry and resume

- source 접근 실패는 source별 한 번만 재시도합니다.
- 필수 source가 없으면 blocked, 비필수면 partial입니다.
- contradiction은 양쪽을 보존하고 review queue에 둡니다.
- reviewer 실패는 한 번 재시도한 뒤 blocked이며 producer self-approval은 없습니다.
- 입력 hash가 같을 때만 마지막 검증 checkpoint부터 resume합니다.
- 새 자료나 변화가 없으면 빈 change set으로 정상 종료합니다.
'''


def method_page(spec: dict) -> str:
    failures = "\n".join(f"| {problem} | {fallback} | {resume} |" for problem, fallback, resume in spec["failures"])
    return f'''# Method — {spec["title"]}

## Source policy

공식 문서, 공식 저장소, 원 논문과 1차 자료를 우선합니다. 중요한 주장은 가능한 경우 독립된 복수 근거로 확인합니다. snippet, 제목-only, 접근하지 못한 전문은 확정 evidence가 아닙니다. 발행일, 확인일, version, 접근 상태와 실제 확인 범위를 기록합니다.

## Analysis policy

fact, inference, hypothesis, counterevidence, contradiction과 unknown을 분리합니다. 기존 snapshot을 덮어쓰지 않고 change reason과 downstream 영향을 보존합니다. `stale`은 재검토 필요 상태이지 거짓 또는 폐기가 아닙니다.

## Case-specific normal result

{spec["normal"]}

## Error matrix

| 문제 | 안전한 fallback | resume 조건 |
|---|---|---|
{failures}

## Exclusions

{spec["near_miss"]}. 사용자 승인 없는 DeepResearch, 내부 데이터 추정, 자동 promotion과 주문 없는 보고서 생성은 하지 않습니다.
'''


def output_page(spec: dict) -> str:
    artifacts = "\n".join(f"| `{name}` | {fields} |" for name, fields in spec["artifacts"])
    return f'''# Output contract — {spec["title"]}

## Required Local envelope

Durable Local knowledge는 다음을 사용합니다.

```yaml
okf_version: "0.1"
boi_profile_version: "0.1-local"
visibility: local-private
local_only: true
source_refs: []
generated_from: []
```

## Normal artifacts

| Artifact | Required content |
|---|---|
{artifacts}

해당 실행에 필요하지 않은 artifact는 만들지 않습니다. 변화가 없으면 빈 change set이 정상 결과이고 보고서는 생성하지 않습니다.

## Review and failure artifacts

- `reviewer-report.json`: decision, reviewed source hashes, material claims, contradictions, unresolved, reviewer identity
- `partial.json` 또는 `blocked.json`: failure phase, verified artifacts, invalidated dependents, retry count, checkpoint hash, resume condition
- `promotion-preview.json`: sanitized body, reviewer, target scope, remote-safe source refs, exact candidate SHA256, `approved=false`, `submitted=false`

Promotion candidate의 내용, source, reviewer, scope 또는 hash가 바뀌면 기존 승인은 무효입니다.
'''


def walkthrough_page(spec: dict) -> str:
    return f'''# 비개발자 실행 — {spec["title"]}

1. 다음 문장으로 시작합니다.

   ```text
   {spec["prompt"]}
   ```

2. AI가 목적, 범위, 결과가 모호할 때만 쉬운 질문을 최대 세 개 묻습니다.
3. Capture·Update·Query·DeepResearch·Health·Review·Promote 중 선택된 경로와 변경 미리보기를 확인합니다.
4. Python, qmd, Obsidian, MCP 또는 agent-team 없이 Local 파일 경로로 실행합니다.
5. change set, review queue, unknown과 다음 검토일을 확인합니다.
6. reviewer가 revise·partial·blocked이면 추정으로 완료하지 않고 resume 조건을 따릅니다.
7. 보고서나 비교표가 필요할 때만 별도로 요청합니다.
8. 공유가 필요하면 exact promotion preview를 보고 별도로 승인합니다. AI는 자동 전송하지 않습니다.

Second Brain이 없어도 위 실행은 완료됩니다. 연결할 때만 검토된 durable knowledge를 기존 topic과 비교해 반영합니다.

Near-miss: {spec["near_miss"]}. 이 경우 Case를 억지로 실행하지 않습니다.
'''


def expected_files(case_root: Path, spec: dict) -> dict[Path, str]:
    manifest = json.loads((case_root / "fixtures" / "manifest.json").read_text(encoding="utf-8"))
    return {
        case_root / "CASE.md": case_page(spec, manifest["fixture_id"], manifest["source_count"]),
        case_root / "roles" / "roles.md": roles_page(spec),
        case_root / "orchestrator.md": orchestrator_page(spec),
        case_root / "references" / "method.md": method_page(spec),
        case_root / "expected" / "OUTPUT-CONTRACT.md": output_page(spec),
        case_root / "walkthrough" / "01-run.md": walkthrough_page(spec),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    errors: list[str] = []
    written = 0
    for relative, spec in CASES.items():
        case_root = root / relative
        for path, text in expected_files(case_root, spec).items():
            payload = text.encode("utf-8")
            if args.check:
                if not path.is_file() or path.read_bytes() != payload:
                    errors.append(f"documentation mismatch: {path.relative_to(root).as_posix()}")
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                if not path.is_file() or path.read_bytes() != payload:
                    path.write_bytes(payload)
                    written += 1
    result = {"schema": "boi-local-reference-case-doc-build-result/v1", "ok": not errors, "case_count": len(CASES), "written": written, "errors": errors}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
