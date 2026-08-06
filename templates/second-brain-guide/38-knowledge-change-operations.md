---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "지식 변화 운영과 사용자 프롬프트 가이드"
description: "승인된 기준 지식에서 변화 후보를 만들고 검토·승인·revision 이력을 안전하게 운영하는 방법"
tags: [LocalPrivate, SecondBrain, KnowledgeChange, Revision, PromptGuide]
timestamp: "{{timestamp}}"
boi_id: boi:private:{{employee_id}}:guide:knowledge-change-operations
visibility: local-private
classification: internal
owner: "{{employee_id}}"
employee_id: "{{employee_id}}"
local_owner_ref: local-private:{{employee_id}}
local_only: true
promotion_status: local_only
retention_class: reference
retention_until: ""
archive_status: active
artifact_visibility: reference
lifecycle_state: protected
memory_candidate: true
cleanup_policy: keep
review_after: "{{review_after}}"
contains_sensitive: false
guide_release: "3.0.0"
guide_audience: "Second Brain의 지식을 정기적으로 갱신하고 검토하는 구성원"
guide_duration_minutes: 15
guide_prerequisites: "검토할 주제 또는 승인된 기준 지식"
guide_execution: "공개 Golden Journey로 흐름을 익힌 뒤 주제별 업데이트 후보를 검토하고 승인된 revision만 현재 지식에 반영한다"
guide_success: "현재 승인 지식과 업데이트 후보가 분리되고 이전 판단·근거·반증·변화 이력이 보존된다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "35-recurrence-fingerprint.md"
guide_boundary: "local-only"
source_refs:
  - type: local-guide-source
    ref: templates/second-brain-guide/38-knowledge-change-operations.md
  - type: local-community-case
    ref: cases/research/agentic-ai-change-radar/CASE.md
    note: "Community 상태의 공개 Golden Journey 재현성 사례"
generated_from:
  - type: local-document
    ref: cases/research/agentic-ai-change-radar/CASE.md
    sha256: 2ed579e252873a22179bb04f8c54c356197ece7d9a9f2d17f2f333e45df23284
  - type: local-document
    ref: cases/research/agentic-ai-change-radar/golden-journey/runs/2026-08-06/query-diff.md
    sha256: 2ba91556128a4c0f93470a3d2c872e7dc6aeffa6fbc06a0ba5198181ebf22f7c
---

# 지식 변화 운영과 사용자 프롬프트 가이드

Second Brain의 지식은 새 자료가 들어올 때마다 곧바로 덮어쓰는 메모가 아닙니다. **승인된 현재 지식**, **이번에 검토할 변화 후보**, **이전 판단과 그 판단을 바꾼 근거**를 분리해야 시간이 지나도 믿고 다시 사용할 수 있습니다.

## 1. 기존 Golden Journey로 먼저 이해하기

[SK하이닉스 Agentic AI Change Radar](../../cases/research/agentic-ai-change-radar/CASE.md)는 공개 공식 자료만 사용해 지식이 자라는 과정을 재현한 Community 사례입니다. 이 사례에서는 다음 변화가 실제로 분리되어 있습니다.

- 과거에는 Node.js 지원이 향후 계획이었지만, 새 자료에서는 TypeScript SDK와 지속 세션 지원이 확인되어 기존 판단의 수정 후보가 됐습니다.
- MCP의 기존 discovery 설명은 후속 보안 규격의 Protected Resource Metadata 요구와 충돌해 새 검토가 필요해졌습니다.
- 출시 당시의 Agent Builder 판단은 후속 종료 공지로 오래된 판단과 폐기 검토 후보가 됐습니다.
- 공개 자료만으로 SK하이닉스 업무 적용성을 판단할 수 없다는 항목은 근거를 꾸며내지 않고 `unknown`으로 유지됐습니다.

같은 질문을 업데이트 전후에 다시 실행하면 새로 알게 된 내용과 여전히 모르는 내용을 구분할 수 있습니다. 다만 답이 달라졌다는 사실만으로 새 판단이 승인되는 것은 아닙니다. 변화 후보와 검토 목록을 사람이 확인한 뒤 승인해야 현재 지식이 바뀝니다.

이 Golden Journey는 흐름을 연습하고 결과를 재현하기 위한 공개 사례입니다. 실제 사용자의 승인된 Second Brain 지식이나 SK하이닉스 운영 검증 완료 결과로 취급하지 않습니다. 사례도 현재 `Community` 상태이며 기존 고정 실행 자료는 수정하지 않습니다.

### 공개 사례로 먼저 연습하기

```text
저장소의 SK하이닉스 Agentic AI Change Radar Golden Journey만 읽고,
외부 조사나 파일 변경 없이 지식 변화 흐름을 설명해줘.

최초 기준 지식, 새 자료에서 발견된 업데이트 후보, 충돌·오래된 판단·
unknown, 같은 질문의 답변 변화, 사람이 승인해야 할 항목으로 나눠 보여줘.
이 사례를 실제 승인 지식이나 운영 검증 완료 결과라고 표현하지 마.
```

## 2. 사용자가 보는 다섯 가지 지식

| 사용자 용어 | 의미 | 운영 기준 |
|---|---|---|
| 기준 지식 | 이번 비교가 출발하는 승인된 지식 | 최초 운영에서는 처음 승인한 지식, 반복 운영에서는 현재 revision |
| 이전 승인 지식 | 현재 revision 바로 전에 승인됐던 지식 | 과거 판단과 변경 이유를 확인할 때 사용 |
| 이번 업데이트 후보 | 새 근거와 비교해 만든 변경 제안 | 승인 전에는 현재 지식이 아님 |
| 현재 지식 | 해당 주제에서 가장 최근에 승인된 revision | Query가 기본으로 사용하는 지식 |
| 지식 변화 이력 | 이전 판단, 새 근거, 반대 근거, 검토 결과와 변경 이유 | 삭제하거나 최신 문장으로 덮어쓰지 않음 |

`stale`은 거짓이나 즉시 폐기를 뜻하지 않습니다. 마지막 검토 이후 상황이 달라졌을 수 있어 다시 확인해야 한다는 뜻입니다. `unknown`도 실패가 아니라 현재 근거로는 답할 수 없음을 정확하게 보존한 상태입니다.

## 3. revision 운영 규칙

1. 사용자가 최초 기준 지식을 승인하면 해당 주제의 `revision 1`이 됩니다.
2. 검토된 변경을 사용자가 승인해 현재 지식에 반영할 때만 revision이 증가합니다.
3. 새 자료나 의미 있는 변화가 없으면 빈 변경 결과로 끝내고 revision을 증가시키지 않습니다.
4. 거절, 일부만 확인된 조사, 진행 불가, 근거 부족 결과는 실행 이력에 남기되 현재 revision은 유지합니다.
5. 이전 판단, 당시 근거와 이를 바꾼 새 근거를 삭제하거나 덮어쓰지 않습니다.
6. Agentic AI, FAB Logistics Digital Twin, Scientific Foundation Model Knowledge처럼 주제가 다르면 revision과 변화 이력도 각각 독립적으로 관리합니다.

업데이트 실행 횟수와 승인 revision 수는 같지 않을 수 있습니다. 예를 들어 revision 3 이후 두 번의 조사에서 하나는 변화 없음, 하나는 근거 부족으로 끝났다면 현재 지식은 계속 revision 3입니다.

## 4. 사용자 여정

```text
최초 기준 지식 작성
→ 사용자 검토와 승인
→ 현재 지식으로 Query
→ 지난 승인 이후 새 자료 범위 제안
→ 사용자 승인 후 외부 조사
→ 업데이트 후보와 검토 목록 작성
→ 이전 지식과 후보 답변 비교
→ contradiction·unknown·오래된 판단 Review
→ 사용자가 승인한 변경만 다음 revision에 반영
```

업데이트 후보를 검토할 때는 최소한 다음을 함께 봅니다.

- 이전 판단과 당시 상태
- 새 근거와 실제 확인 범위
- 반대 근거 또는 충돌하는 주장
- 왜 바꿔야 하는지 또는 왜 유지해야 하는지
- 연결된 다른 판단과 후속 업무에 미치는 영향
- 다음 검토일과 아직 확인해야 할 질문

## 5. 바로 복사해 쓰는 프롬프트

### 최초 기준 지식 생성

```text
[주제]에 대한 최초 기준 지식을 만들어줘.

먼저 현재 Second Brain에 같은 주제의 승인 지식이 있는지 확인해줘.
없다면 조사할 범위, 기준 시점과 우선 확인할 공식 자료 후보를 먼저 보여줘.
내가 승인하기 전에는 DeepResearch를 시작하지 마.

조사 후에는 주장별 근거, 반대 근거, unknown, 확인 범위와 마지막 검토일을
분리하고 최초 기준 지식 후보로 보여줘. 내가 승인하기 전에는 revision 1이나
현재 지식으로 확정하지 말고, 요청하지 않은 보고서도 만들지 마.
```

### 정기 업데이트 기본 프롬프트

```text
[주제]에서 지난 승인 이후 달라진 내용만 업데이트해줘.

먼저 현재 기준 지식, 이전 승인 지식, 현재 revision과 마지막 검토일을 확인해줘.
외부 조사가 필요하면 조사 범위, 기준 시점과 우선 확인할 공식 자료 후보를
먼저 제안하고 멈춰줘. 내가 승인하기 전에는 DeepResearch를 시작하지 마.

승인된 범위의 조사 결과는 신규, 강화, 수정, 충돌, stale, 폐기 검토,
unknown으로 구분해줘. 각 항목에 이전 판단, 새 근거, 반대 근거,
변경 이유와 연결된 지식·업무에 미치는 영향을 표시해줘.

변화가 없으면 빈 변경 결과로 끝내고 revision을 올리지 마.
거절되거나 일부만 확인됐거나 진행할 수 없거나 unknown인 결과는 실행 이력에
남기되 현재 지식은 바꾸지 마. 내가 최종 승인하기 전에는 업데이트 후보를
현재 지식에 반영하지 말고, 요청하지 않은 보고서나 발표 자료를 만들지 마.
```

### 외부 조사 없이 기존 지식만 비교

```text
[주제]의 이전 승인 지식과 현재 승인 지식을 Second Brain 안에서만 비교해줘.
외부 검색이나 DeepResearch는 실행하지 마.

추가·강화·수정·충돌·오래된 판단·폐기 검토·unknown을 구분하고,
각 변화가 승인된 revision과 근거를 가리키게 해줘. 근거가 부족한 차이는
추정하지 말고 unknown으로 표시해줘.
```

### 현재 승인 지식으로 질문

```text
현재 승인된 [주제] 지식만 사용해서 [질문]에 답해줘.

직접 답변, 지지 근거, 반대 근거, unknown과 한계, 다음 확인,
신뢰도와 출처를 분리해줘. 현재 승인 지식으로 답할 수 없으면 추정하거나
자동으로 외부 조사하지 말고, 필요한 조사 범위만 제안해줘.
```

### 짧게 요청하기

```text
Agentic AI에서 지난번 이후 달라진 것만 찾아줘.
```

```text
Digital Twin 현재 승인 지식과 지난 revision의 차이만 보여줘. 외부 조사는 하지 마.
```

```text
Scientific Foundation Model에서 충돌하거나 오래된 판단만 검토 목록으로 보여줘.
```

짧은 요청을 받으면 AI는 먼저 주제, 현재 승인 지식과 조사 필요 여부를 확인합니다. 외부 조사가 필요하면 범위와 공식 자료 후보를 제안하고 사용자의 승인을 기다립니다.

## 6. 같은 주제에 다음 내용을 추가하는 방법

Golden Journey의 고정 실행 자료는 재현성 기준이므로 이후 실제 조사 결과를 그 파일에 이어 쓰지 않습니다. 실제 반복 운영은 Second Brain의 최신 승인 revision에서 새 업데이트 후보를 만듭니다.

1. 최신 승인 revision과 마지막 검토일을 확인합니다.
2. 지난 승인 이후의 기간, 포함·제외 범위와 공식 자료 후보를 정합니다.
3. 사용자가 외부 조사 범위를 승인합니다.
4. 새 자료를 업데이트 후보와 검토 목록으로 만듭니다.
5. 같은 질문으로 현재 승인 지식과 후보 답변의 차이를 확인합니다.
6. 사용자가 승인하면 새 snapshot ID와 다음 revision을 부여합니다.
7. 승인되지 않으면 현재 지식은 유지하고 실행 결과와 재개 조건만 남깁니다.

```text
[주제]의 현재 승인 revision에서 다음 업데이트 후보를 만들어줘.
지난 revision 이후 달라진 내용만 대상으로 하고, 기존 Golden Journey의 고정
실행 자료는 수정하지 마. 먼저 조사 범위와 공식 자료 후보를 보여주고 내 승인을
기다려줘. 조사 후에도 현재 지식에는 반영하지 말고 변화 후보, 검토 목록,
같은 질문의 답변 차이와 승인할 항목만 보여줘.
```

새 주제는 다른 주제의 revision 번호를 이어받지 않습니다. 먼저 그 주제의 기준 지식을 만들고 승인한 시점부터 별도의 revision 1과 변화 이력을 시작합니다.

## 7. 안전 경계

- Query는 현재 Second Brain에서 승인된 지식만 사용합니다.
- 근거가 부족하면 모델 기억이나 추정으로 채우지 않고 `unknown`으로 표시합니다.
- 외부 조사는 범위와 공식 자료 후보를 사용자가 승인한 뒤에만 시작합니다.
- 업데이트 후보는 사용자 승인 전까지 현재 지식에 반영하지 않습니다.
- Local Private 자료는 exact sanitized preview와 사용자 승인 없이 외부로 전송하거나 promotion하지 않습니다.
- Obsidian, Python, qmd, MCP와 별도 검색 플러그인이 없어도 Markdown과 AI의 기본 파일·검색 기능으로 같은 흐름을 수행할 수 있어야 합니다.

## 관리자·재현성 참고

Golden Journey에서는 최초 기준 snapshot을 `T0`, 이후 시점의 snapshot을 `T1`, `T2`처럼 표시합니다. 이는 같은 입력과 질문으로 지식 변화가 재현되는지 검증하기 위한 내부 표기입니다.

- [T0 기준 snapshot](../../cases/research/agentic-ai-change-radar/golden-journey/runs/2026-08-06/t0/claim-snapshot.md)
- [T1 변경 후보](../../cases/research/agentic-ai-change-radar/golden-journey/runs/2026-08-06/t1/change-set.json)
- [T1 검토 목록](../../cases/research/agentic-ai-change-radar/golden-journey/runs/2026-08-06/t1/review-queue.md)
- [동일 Query의 T0·T1 답변 차이](../../cases/research/agentic-ai-change-radar/golden-journey/runs/2026-08-06/query-diff.md)

실제 반복 운영에서는 T0/T1 대신 주제별 `revision`과 고유한 `snapshot ID`를 사용합니다. snapshot은 실행 후보로 남을 수 있지만 revision은 승인된 변경이 현재 지식에 반영될 때만 증가합니다. 따라서 T1이 만들어졌다고 자동으로 revision 2가 되는 것은 아닙니다.

`AS-IS/TO-BE`는 현재 조직 상태와 목표 상태를 비교할 때 사용합니다. 지식 변화에는 시간에 따른 근거, 반증, 승인 여부와 이력이 필요하므로 AS-IS/TO-BE로 표현하면 과거 판단이 왜 바뀌었는지와 승인되지 않은 후보를 구분하기 어렵습니다.

이전: [근거 기반으로 질문하고 답을 검증하기](37-grounded-query.md) · 다음: [재발 패턴과 주간 review](35-recurrence-fingerprint.md)
