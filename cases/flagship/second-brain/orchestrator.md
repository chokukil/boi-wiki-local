# Orchestrator — Flagship Second Brain

Pattern: `supervisor → fan-out ingest → knowledge consolidation → generate/validate → human checkpoint`

이 Orchestrator의 목표는 파일 수를 늘리는 것이 아니라, 원본과 이력을 보존하면서 기존 지식을 보강하고 재사용 가능한 답과 promotion 후보를 만드는 것입니다.

## Dependency DAG

~~~text
P0 authorization + selected-source integrity verification
 ├─ P1 source-curator: inventory, SHA256, duplicate groups
 └─ P2 memory-maintainer: existing topic/index/state inventory
             │
             └──── fan-in ────┐
                              ▼
P3 knowledge-distiller: noop / append / revise / supersede / create / queue-review
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
P4 grounded-query-analyst          P5 promotion compiler
                 └────────────┬────────────┘
                              ▼
P6 privacy-reviewer: source↔claim, history, projection, UX cross-check
                 ├─ pass → Local completion
                 ├─ revise → one causal correction and re-review
                 └─ block → evidence gap + safe resume point
~~~

P4는 query scenario에서만, P5는 promotion scenario에서만 실행합니다. 모든 단계는 P6 이전에 자기 결과를 final로 선언할 수 없습니다.

## P0 — 사용자 실행 계약 잠금

입력:

- 자연어 user prompt 하나
- 활성 Local Profile과 저장된 Second Brain 설정
- 사용자가 선택한 대화 범위 또는 자료 폴더 source subset
- 기존 Local 지식과 처리 재개 상태
- repository commit, Harness release/checksum

동작:

1. Local/Remote 경계와 원본 보존을 확인합니다.
2. 선택된 source의 현재 경로·크기·SHA256과 기존 지식의 before hash를 읽기 전용으로 기록합니다.
3. 사용자가 승인한 대화·폴더·문서 범위 밖의 source를 읽지 않습니다.
4. 이미 승인된 재개 계획이 있으면 plan·source·progress hash를 다시 검증하고, 달라졌으면 쓰기 전에 새 preview로 돌아갑니다.
5. 합성 walkthrough나 Admin/CI 평가에서만 fixture·seed manifest와 [frozen protocol](evals/PROTOCOL.md)을 추가로 적용합니다. 이는 일반 구성원 실행의 입력 계약이 아닙니다.

종료조건: 사용자 범위, Local/Remote 경계, 입력 hash와 재개 지점을 기록했으며 변경 파일은 아직 0개입니다.

## P1 — Source inventory

논리적 handoff에는 다음이 포함됩니다.

- path, bytes, SHA256, media category
- supported / duplicate / incomplete / review-required
- intentional duplicate group
- source before-hash

파일명만 보고 의미를 추측하지 않습니다. PNG는 image, CSV는 tabular-data로 먼저 분류하고 도메인 의미는 파생 문서에서 검토합니다.

종료조건: 사용자가 선택한 source가 한 번씩 분류되고, duplicate는 대표 하나와 alias path로 표현됩니다. Single-agent 일반 실행에서는 이 정보를 agent 작업 맥락과 승인된 plan에 유지하며 별도 `intermediate/source-inventory.json` 파일을 기본 생성하지 않습니다. Reduced·Full 역할 handoff 또는 Admin/CI 증거에서만 구조화 파일로 materialize합니다.

## P2 — Existing knowledge inventory

논리적 handoff에는 다음이 포함됩니다.

- topic page와 memory_key
- claim status와 review date
- incoming/outgoing standard Markdown links
- source hash coverage
- processing checkpoint

종료조건: 새 자료를 보기 전에 기존 topic owner를 결정할 수 있고, 중단 재개 시 완료 source와 pending source가 분리됩니다. 이 inventory도 별도 역할 handoff나 재현 가능한 관리자 검증이 필요한 경우에만 파일로 저장합니다.

## P3 — Consolidation decision

각 source/topic 조합에 정확히 하나의 operation을 부여합니다.

| Operation | 선택 조건 | 필수 증거 |
|---|---|---|
| `noop` | 동일 SHA 또는 장기 가치 없음 | 기존 source hash 또는 near-miss 이유 |
| `append-evidence` | 같은 claim을 보강 | 기존 topic과 새 source hash |
| `revise` | 같은 topic의 설명·구조 개선 | 바뀐 문장과 유지된 claim |
| `supersede` | 사용자가 명시적으로 교정 | 이전 claim, 새 claim, 교정 source |
| `create` | 기존 topic이 소유할 수 없음 | nearest-topic search 결과 |
| `queue-review` | 충돌·민감정보·낮은 확신 | 양쪽 claim과 필요한 reviewer |

산출물:

- OKF 0.1 + BoI Profile 0.1-local 파생 문서
- 실제 변경이 있을 때의 변경 전 Local archive
- 자료 폴더 재개가 필요할 때의 승인 plan과 processing checkpoint
- Reduced·Full 역할 handoff 또는 Admin/CI 검증에서만 구조화된 consolidation plan

종료조건: source마다 operation과 reason이 있고, raw source bytes와 기존 history hash가 그대로입니다.

## P4 — Grounded query

순서:

1. compiled/reviewed knowledge를 먼저 검색합니다.
2. 문서의 `source_refs`로 연결된 evidence만 펼칩니다.
3. direct answer, supporting evidence, counterevidence, unknowns, next checks, confidence, citations를 채웁니다.
4. Local citation은 path + exact SHA256, remote citation은 BoI ID + revision + visibility로 분리합니다.

종료조건: material claim마다 citation이 있거나 “근거 부족”으로 명시됐습니다.

## P5 — Promotion compiler

원본·agent-memory·evidence·hypothesis·analysis log는 직접 compiler 입력이 될 수 없습니다. 먼저 일반 knowledge/context pack/SOP로 정제합니다.

산출물:

- Local preview
- canonical OKF 0.1 + BoI Profile 0.1 candidate
- sanitized remote projection
- reviewer, scope, structured source refs, exact candidate hash
- `user_confirmed: false`, `remote_submit_allowed: false`

종료조건: Local path, Local ID, employee identifier, raw bytes가 projection에 0건이며 remote call은 0건입니다.

## P6 — Independent review

Reviewer는 저자의 요약을 먼저 읽지 않고 다음 순서로 교차검증합니다.

1. 사용자가 승인한 source 범위와 before/after source hash
2. source inventory와 consolidation operation
3. 파생 문서의 metadata·links·claim text
4. 답변 또는 promotion projection
5. 사용자용 완료 요약

Reviewer 결과는 `pass`, `revise`, `block` 중 하나입니다. `revise`는 한 causal defect와 수정 대상 surface를 지정합니다. 두 번 재검토 후에도 같은 hard defect가 남으면 완료가 아니라 block입니다.

## Scale modes

- **Full:** P1·P2를 병렬 specialist가 수행하고 P3·P4/P5·P6를 독립 역할이 수행합니다.
- **Reduced:** creator가 P1–P5를 수행하고 별도 reviewer가 P6를 수행합니다.
- **Single-agent:** 한 agent가 P1–P5를 순차 수행한 뒤 결론을 접고 source부터 별도 P6 pass를 수행합니다.
- **No-team fallback:** 같은 논리적 handoff와 exit criteria를 사용하지만 불필요한 intermediate 파일이나 team 기능을 요구하지 않습니다.

Scale mode가 바뀌어도 산출물 schema, source integrity, reviewer checklist와 promotion 경계는 바뀌지 않습니다.

## Failure and recovery matrix

| Failure | 즉시 동작 | 재개 조건 |
|---|---|---|
| source hash drift | 해당 batch 중단 | 새 manifest와 사용자 확인 |
| 누락 email 첨부 | `unknown`으로 기록 | 실제 첨부가 intake됨 |
| duplicate path | 대표 hash에 alias 연결 | 추가 파일 생성 없음 |
| reviewed claim 충돌 | 양쪽 보존·review queue | reviewer 결정 source |
| context limit | completed/pending checkpoint | 다음 세션에서 pending부터 |
| validator unavailable | Local 결과만 완료 | 실제 validator 연결 |
| sensitive projection token | promotion block | projection 재생성·재검증 |
| remote capability 발견 | 사용하지 않음 | 별도 사용자 승인 전까지 없음 |

다음: [논리 역할](roles/roles.md) · [출력 계약](expected/OUTPUT-CONTRACT.md) · [평가 프로토콜](evals/PROTOCOL.md)
