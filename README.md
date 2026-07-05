# BoI Wiki Local

BoI Wiki Local은 개인 PC에만 저장되는 Local Private BoI 작업공간입니다.

어렵게 생각하지 않아도 됩니다. Codex, Claude, Cursor 같은 agent에게 아래처럼 말하면 됩니다.

```text
이 boi-wiki-local repo URL 보고 내 PC에 설치해줘.
이 repo 설치해줘.
이 폴더를 BoI Wiki Local로 써줘.
```

그 다음부터는 자연어로 요청합니다.

| 요청 문장 | 실행 성격 | 예제와 결과 |
|---|---|---|
| 이 회의 내용을 BoI로 정리해줘. | local | [회의 내용 BoI 정리](data/boi/private/0000000/usage-examples/natural-language-poc/meeting-to-boi.md) |
| 이 SOP 이미지를 BoI Wiki 형식으로 초안 만들어줘. | local + evidence | [SOP 이미지 초안](data/boi/private/0000000/usage-examples/natural-language-poc/image-to-sop-draft.md) |
| 직개발 결과 확인 SOP를 Mermaid 프로세스 플로우로 그려줘. | local | [SOP Mermaid flow](data/boi/private/0000000/usage-examples/natural-language-poc/sop-mermaid-flow.md) |
| 이 이벤트가 발생하면 어떤 업무 BoI와 업무 흐름이 이어지는지 알려줘. | live workflow evidence | [업무 흐름 계획](data/boi/private/0000000/usage-examples/natural-language-poc/event-to-action-plan.md) |
| 기존 API 문서를 Action 초안으로 만들고 업무 흐름에 연결해줘. | local | [API to Action Spec](data/boi/private/0000000/usage-examples/natural-language-poc/api-doc-to-action-spec.md) |
| 현장에서 말하는 Response Trend 용어를 dictionary에 추가해줘. | local | [Dictionary term authoring](data/boi/private/0000000/usage-examples/natural-language-poc/dictionary-term-authoring.md) |
| 원격 BoI Wiki를 검색해서 이번 업무용 context pack을 만들어줘. | remote lookup optional | [Context pack](data/boi/private/0000000/usage-examples/natural-language-poc/remote-context-pack.md) |
| 만들어진 SOP 내용 괜찮네. Public으로 공유해줘. | approval required | [Public promotion preflight](data/boi/private/0000000/usage-examples/natural-language-poc/promotion-public.md) |
| 팀 주간보고 작성한 거 괜찮아 보이네. 팀 주간보고로 올려줘. | approval required | [Team weekly report promotion](data/boi/private/0000000/usage-examples/natural-language-poc/weekly-report-promotion.md) |
| 오래된 Private BoI 정리 후보 보여줘. | local | [Archive candidates](data/boi/private/0000000/usage-examples/natural-language-poc/archive-candidates.md) |
| MCP 설정은 모르겠으니 local만 써줘. | local-only | [Local only mode](data/boi/private/0000000/usage-examples/natural-language-poc/local-only-mode.md) |

## 이것은 무엇인가요

- 개인 업무 메모, 회의록, SOP 초안, 주간보고 초안, 비정형 업무 BoI를 Markdown/OKF 구조로 쌓는 폴더입니다.
- Web BoI Wiki에는 자동으로 보이지 않습니다.
- 사용자가 명시적으로 승인하기 전에는 원격으로 전송하거나 공개하지 않습니다.
- MCP, Python, Docker, Git을 몰라도 쓸 수 있습니다.
- Mermaid 기반 도식, 업무 흐름 계획, API Action 초안, Dictionary 용어, context pack도 local-only로 만들 수 있습니다.
- SOP가 없는 일회성 업무는 Local Private 업무 BoI로 저장하고, 반복성이 보이면 WorkflowDefinition 또는 Skill 후보로 정리합니다.
- SOP Mermaid 도식은 기본적으로 `Overview + Swimlane`으로 만들고, 복잡한 구간은 stage detail로 분리합니다. Web BoI Wiki에 올리면 Mermaid block이 실제 diagram으로 렌더링됩니다.
- Dictionary는 개인/팀/공용 도메인 용어를 이해하기 위한 BoI 문서입니다. Local에서는 `dictionary/`에 초안을 만들고, 원격 MCP가 있으면 shared dictionary를 조회만 한 뒤 필요한 경우 promotion draft로 공유합니다.
- Local Second Brain은 별도 서버나 DB 없이 동작합니다. agent는 capture inbox, local review, cleanup preview, promotion preflight를 반복해서 개인 업무 지식을 점진적으로 정리합니다.

## 처음 사용하기

가장 쉬운 방법은 agent에게 repo URL을 주는 것입니다.

```text
이 boi-wiki-local 저장소를 설치하고, 이 폴더를 내 BoI Wiki Local로 설정해줘.
```

agent는 clone, zip 다운로드, 또는 현재 폴더 템플릿 구성을 상황에 맞게 선택합니다. Git이 없으면 일반 폴더로 시작합니다.

처음 실제 문서를 만들기 전에는 7자리 숫자 사번이 필요합니다. agent가 `.env`의 `BOI_LOCAL_EMPLOYEE_ID`를 확인하고, 값이 없거나 `0000000`이면 사용자에게 사번을 물어본 뒤 `data/boi/private/{사번}/` 폴더를 만듭니다.

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

WSL, Ubuntu, Linux:

```sh
sh install.sh
```

설치 스크립트를 실행하지 않아도 됩니다. agent에게 "이 폴더를 BoI Wiki Local로 써줘"라고 말하면 `AGENTS.md`와 skill 규칙을 기준으로 작업합니다. agent가 `check.sh` 또는 `check.ps1`를 먼저 실행해도 됩니다. `BOI_LOCAL_EMPLOYEE_ID`가 7자리 숫자이고 실제 사번 폴더가 아직 없으면 check가 template scaffold를 복사해 기본 구조를 준비한 뒤 검증합니다.

## 어디에 저장되나요

아래 `{7자리사번}`은 실제 사용자의 숫자 7자리 사번입니다. repo에는 템플릿 scaffold로 `data/boi/private/0000000/`만 들어 있습니다.

| 요청 | 폴더 |
|---|---|
| 회의록, 개인 메모 | `data/boi/private/{7자리사번}/notes/` |
| SOP 초안 | `data/boi/private/{7자리사번}/sop-drafts/` |
| Action 초안 | `data/boi/private/{7자리사번}/action-drafts/` |
| Event 후보 / 업무 흐름 초안 | `data/boi/private/{7자리사번}/event-drafts/` |
| 개인 dictionary 용어 | `data/boi/private/{7자리사번}/dictionary/` |
| Mermaid 도식 | `data/boi/private/{7자리사번}/diagrams/` |
| Context pack | `data/boi/private/{7자리사번}/context-packs/` |
| 실행 전 확인 / 업무 흐름 시뮬레이션 | `data/boi/private/{7자리사번}/workflow-simulations/` |
| Langflow 설계 초안 | `data/boi/private/{7자리사번}/langflow-plans/` |
| 주간보고, 업무증빙 | `data/boi/private/{7자리사번}/reports/` |
| 공유 전 정리본 | `data/boi/private/{7자리사번}/promotion-drafts/` |
| 사용 예제 | `data/boi/private/{7자리사번}/usage-examples/` |
| 오래된 문서 | `data/boi/private/{7자리사번}/_archive/YYYY/MM/` |
| 정리 전 quarantine | `.boi-trash/{cleanup_id}/` |

## Local Private 규칙

agent가 저장하는 Local Private 문서는 다음 값을 가져야 합니다.

```yaml
employee_id: "1234567"
local_owner_ref: local-private:1234567
visibility: local-private
local_only: true
promotion_status: local_only
archive_status: active
artifact_visibility: working
lifecycle_state: working
memory_candidate: false
cleanup_policy: keep
contains_sensitive: unknown
```

agent는 사용자가 lint를 몰라도 저장 전 자체 검증을 수행하고, `index.md`와 `log.md`를 업데이트해야 합니다.

## Second Brain과 Cleanup

Local Private는 개인 Second Brain입니다. 사용자가 장기 기억으로 채택한 문서는 `artifact_visibility: memory`, `lifecycle_state: memory`, `cleanup_policy: keep`으로 보호합니다. 진행 중 초안과 업무 메모는 `working`으로 둡니다.

반대로 재생성 가능한 generated 산출물은 `background` 또는 `delete_candidate`로 표시합니다. 예: 반복 생성된 보고서, sandbox/report artifact, 임시 분석 output, 오래된 workflow simulation. 이런 파일은 사용자가 요청했을 때만 cleanup preview에 올리고, 승인되면 `.boi-trash/{cleanup_id}/`로 이동합니다. 기본 보존기간은 7일이며, 그 사이에는 manifest 기준으로 복구할 수 있습니다. 사용자가 직접 작성한 memory/working 문서와 promotion draft는 자동 삭제 대상이 아닙니다.

agent가 사용할 수 있는 경량 helper:

| Script | 목적 |
|---|---|
| `scripts/local_capture.py` | 자유 메모를 `notes/capture-inbox/` 아래 capture 후보로 저장 |
| `scripts/local_review.py` | memory 후보, stale/duplicate 후보, cleanup preview, promotion 후보를 비파괴로 조회 |
| `scripts/promotion_preflight.py` | 공유 전 target visibility, source_refs, 민감정보 패턴, preview draft를 확인 |

```sh
python3 scripts/local_capture.py --check
python3 scripts/local_review.py --check
python3 scripts/promotion_preflight.py --check
```

일반 사용자는 이 명령을 외울 필요가 없습니다. agent가 check와 preview에 사용하고, 결과만 설명합니다.

## 공유

"Public으로 공유해줘" 또는 "팀 주간보고로 올려줘"라고 말하면 agent가 먼저 공유 전 검증과 preview를 준비합니다.

정상 흐름:

1. agent가 local promotion draft를 만듭니다.
2. agent가 local preflight를 실행하고 민감정보, 출처, 공개 범위, preview를 보여줍니다.
3. 사용자가 명시적으로 승인합니다.
4. 원격 BoI Wiki에 sync validation/publish를 요청합니다.
5. 원격 자동 검증과 자동 commit을 통과하면 Team/Public에 즉시 게시되고 HOTL이 사후 모니터링합니다.
6. 검증 실패 시 게시하지 않고 validation report를 받아 agent가 수정안을 만듭니다.

일반 사용자는 원격 Git commit, lint 세부 명령, publish 절차를 직접 실행하지 않습니다. agent가 진행 상태와 오류 피드백을 설명하고, 사용자는 preview 승인 여부만 결정합니다.

## 선택 사항: MCP

MCP를 설정하면 agent가 원격 BoI Wiki에서 SOP, Event Type, Action, 실행 현황을 검색할 수 있습니다. 내부 중복 확인에는 WorkflowDefinition tool을 쓰지만, 사용자에게는 SOP 추가, BoI Wiki 탐색, Event/Action 카탈로그 기준으로 설명합니다.

MCP를 몰라도 Local Private 작성은 계속 동작합니다.

설정 예시는 `.codex/config.toml.example`을 참고하세요.

공식 MCP는 shared BoI Wiki MCP 하나입니다.

```text
http://boi-wiki-mcp.example:28200/mcp
```

사내 실제 주소는 운영자에게 별도로 공유받아 개인 `.env` 또는 MCP client 설정에만 입력합니다. agent는 이 MCP를 조회와 승인된 원격 게시에만 사용해야 합니다. Local Private 원본은 사용자 명시 승인 없이 원격으로 보내지 않습니다.

MCP가 있을 때 agent는 다음 도구를 우선 사용합니다.

- `dictionary_resolve`: 현장 용어와 약어를 private -> team -> public 우선순위로 해석합니다.
- `ontology_search`: SOP, Event Type, Action, Dictionary, BoI 문서, runtime evidence를 함께 찾습니다.
- `workflow_definitions_search`: 내부 WorkflowDefinition 기준으로 기존 연결을 찾아 새 업무/API/MCP/Skill의 중복 개발을 줄입니다.
- `workflow_definition_get`: 내부 WorkflowDefinition의 업무 목적, 필요한 업무 BoI, 근거, 완결 조건을 확인합니다.
- `workflow_definition_deduplicate`: 신규 등록 전에 재사용/확장/신규 생성 판단 근거를 받습니다.
- `sop_registration_plan`: 자연어 SOP/Event/Action 요청을 Event/SOP/Action 3단 흐름의 기존 후보, 추천 필드, draft payload로 정리합니다.
- `sop_registration_preview`: draft 생성이나 게시 요청 전에 권한, 과거 이력, 연결 SOP/Event/Action을 먼저 확인합니다.
- `registration_plan` / `registration_verification_preview`: 통합 SOP 흐름으로 부족한 컴포넌트 단위 호환 작업에 사용합니다.
- `sop_registration_draft_create`: 통합 SOP 추가 draft를 만듭니다. 원격 MCP에서는 사용자 확인 후에만 호출합니다.
- `registration_draft_create`: SOP/Event/Action 공통 등록 초안을 만듭니다. 원격 MCP에서는 사용자 확인 후에만 호출합니다.
- `sop_draft_create`: SOP 전용 등록 초안을 만듭니다. shared Wiki에 바로 게시하지 않고 draft로 남깁니다.
- `action_draft_create`: API/MCP/Webhook/Manual/Event Broker/BoI Writer/Langflow Action 전용 등록 초안을 만듭니다. 기존 Action과 내부 WorkflowDefinition 후보를 먼저 확인하고, 선택한 `connector_kind`에 맞는 `connector_config`를 함께 전달합니다.
- `event_type_draft_create`: Event Type 전용 초안을 만듭니다. 검증과 별도 승인 전에는 Event catalog에 반영하지 않습니다.
- `event_publish_plan` / `event_publish_preview`: 업무 Event 발생 요청을 기존 Event 후보와 실행 전 확인으로 바꿉니다.
- `event_pattern_preview`: 기존 Event 이력 조건을 새 Event 정의 초안 후보로 볼지 검토합니다.
- `sop_run_history`: SOP 기준 실행 이력과 남은 승인/수동 조치를 확인합니다.
- `boi_agent_chat`: 현재 페이지나 업무 질문에 대해 BoI Agent 답변을 받습니다.
- `boi_inbox`: 사용자가 담당자로 처리해야 할 검증된 BoI Inbox 보고서와 manual/approval task를 확인합니다. `agent_inbox`는 한 릴리즈 동안 compatibility alias로만 봅니다.
- `boi_search`: BoI 문서 목록만 필요할 때 사용합니다.
- `agent_memory_review`: 원격 Web Private Second Brain 후보, cleanup 후보, promotion 후보를 확인합니다.
- `promotion_preview`: Team/Public 공유 전 원격 validation preview를 확인합니다.
- `source_wiki_plan`: repo/source wiki 생성 전 inventory, selected/skipped file, citation 계획을 확인합니다.
- `private_memory_cleanup_preview`: Web Private generated/background 정리 후보를 확인합니다.
- `private_memory_cleanup_run`, `private_memory_restore`, `private_memory_mark_memory`: 사용자 확인 후에만 Web Private quarantine, 복구, memory 보호 표시를 수행합니다.

MCP가 없으면 같은 작업을 local 파일과 사용자가 제공한 Web 링크/문서 export를 기반으로 수행합니다.

## Source Wiki와 OpenWiki

repo 문서화는 core 기능이 아니라 선택형 검증/문서화 흐름입니다. 고도화 커밋이 merge된 뒤 `https://github.com/chokukil/boi-wiki-local` 기준으로 hosted OpenWiki를 만들어 외부에서 source-grounded wiki 결과를 확인합니다.

사내에서는 GitHub Enterprise, GitLab, Gitea 같은 내부 저장소로 바뀔 수 있습니다. 이때 agent는 repo URL, MCP/API URL, allowlist env만 바꾸고 같은 절차를 유지합니다. Local Private 원문은 여전히 승인 없이 원격으로 보내지 않습니다.

## Dictionary 작성

Dictionary는 검색 성능만을 위한 태그가 아니라, agent가 현장 표현과 공식 BoI 개념을 연결하기 위한 최소 온톨로지입니다. 일반 사용자는 아래 정도만 말하면 됩니다.

```text
현장에서 말하는 Response Trend 용어를 dictionary에 추가해줘.
Cpk랑 공정능력 뜻을 우리 업무 기준으로 정리해줘.
HBM 관련 용어를 shared BoI Wiki dictionary 기준으로 찾아보고 내 업무 context pack에 넣어줘.
```

agent는 기본 입력 5개만 확인합니다: 용어, 별칭/약어, 뜻, 예시, 연결 문서. MCP가 있으면 `dictionary_resolve`와 `ontology_search`로 shared dictionary를 먼저 확인하고, 없으면 local 문서와 사용자가 준 자료만으로 초안을 만듭니다. 저장 위치는 `data/boi/private/{7자리사번}/dictionary/`입니다.

대량 후보를 정리할 때는 개별 용어마다 code나 route test를 바꾸지 않습니다. 후보 데이터, curator override, manifest, promotion draft에서 `keep`, `replace_with_canonical`, `split_into_terms`, `alias_to_existing`, `exclude`, `needs_parent_curation` 중 하나로 판단을 남깁니다. Slash/숫자 묶음, 조건 묶음, mode/test variant는 상위 개념과 alias/broader 관계를 먼저 정리하고, parent가 없으면 local `needs_parent_curation` 상태로 둡니다.

## 활용 사례

아래 예제 세트는 요청 문장, 생성된 Markdown, source image, shared BoI Wiki runtime trace 근거를 함께 보여줍니다.

- [자연어 요청 E2E PoC 예제 세트](data/boi/private/0000000/usage-examples/natural-language-poc/README.md)
- [SOP 원본 이미지 evidence](data/boi/private/0000000/usage-examples/natural-language-poc/evidence/sop_sample_image.png)
- 기존 단문 예제: [SOP Mermaid Flow](data/boi/private/0000000/usage-examples/sop-mermaid-flow.md), [업무 흐름 계획](data/boi/private/0000000/usage-examples/event-to-action-plan.md), [API Doc to Action Spec](data/boi/private/0000000/usage-examples/api-doc-to-action-spec.md), [Dictionary Term Authoring](data/boi/private/0000000/usage-examples/dictionary-term-authoring.md), [Meeting to BoI](data/boi/private/0000000/usage-examples/meeting-to-boi.md)

## 작업별 Skills

agent가 skill을 지원하면 다음 skill을 우선 사용합니다. 지원하지 않아도 `AGENTS.md` 규칙만으로 같은 방식으로 진행할 수 있습니다.

- `boi-wiki-local`
- `boi-sop-flow-visualizer`
- `boi-event-workflow-planner`
- `boi-action-author`
- `boi-dictionary-author`
- `boi-context-pack-builder`
- `boi-workflow-simulator`
- `boi-langflow-connector-planner`

## 자주 묻는 질문

### Git이 없어도 되나요?

됩니다. Git이 있으면 agent가 local history를 남기고, 없으면 일반 폴더로 동작합니다.

### 내 문서가 회사 Wiki에 올라가나요?

아닙니다. 이 폴더의 Local Private 문서는 Web BoI Wiki에 자동으로 올라가지 않습니다.

### MCP를 몰라도 되나요?

됩니다. MCP는 원격 BoI Wiki 검색을 편하게 만드는 선택 기능입니다.

### 검증은 누가 하나요?

agent가 합니다. 일반 사용자가 lint 명령을 직접 실행하지 않는다는 전제로 `AGENTS.md`와 skill에 검증 규칙이 들어 있습니다.
