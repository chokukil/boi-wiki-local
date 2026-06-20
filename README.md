# BoI Wiki Local

BoI Wiki Local은 개인 PC에만 저장되는 Local Private BoI 작업공간입니다.

어렵게 생각하지 않아도 됩니다. Codex, Claude, Cursor 같은 agent에게 아래처럼 말하면 됩니다.

```text
이 boi-wiki-local repo URL 보고 내 PC에 설치해줘.
이 repo 설치해줘.
이 폴더를 BoI Wiki Local로 써줘.
```

그 다음부터는 자연어로 요청합니다.

```text
이 회의 내용을 BoI로 정리해줘.
이 SOP 이미지를 BoI Wiki 형식으로 초안 만들어줘.
설비 이상 대응 SOP를 Mermaid 프로세스 플로우로 그려줘.
이 이벤트가 발생하면 어떤 SOP와 Action이 이어지는지 알려줘.
기존 API 문서를 BoI Action Spec 초안으로 만들어줘.
원격 BoI Wiki를 검색해서 이번 업무용 context pack을 만들어줘.
만들어진 SOP 내용 괜찮네. Public으로 공유해줘.
팀 주간보고 작성한 거 괜찮아 보이네. 팀 주간보고로 올려줘.
오래된 Private BoI 정리 후보 보여줘.
MCP 설정은 모르겠으니 local만 써줘.
```

## 이것은 무엇인가요

- 개인 업무 메모, 회의록, SOP 초안, 주간보고 초안을 Markdown/OKF 구조로 쌓는 폴더입니다.
- Web BoI Wiki에는 자동으로 보이지 않습니다.
- 사용자가 명시적으로 승인하기 전에는 원격으로 전송하거나 공개하지 않습니다.
- MCP, Python, Docker, Git을 몰라도 쓸 수 있습니다.
- Mermaid 기반 도식, Event-to-Action 계획, API Action 초안, context pack도 local-only로 만들 수 있습니다.

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

설치 스크립트를 실행하지 않아도 됩니다. agent에게 "이 폴더를 BoI Wiki Local로 써줘"라고 말하면 `AGENTS.md`와 skill 규칙을 기준으로 작업합니다.

## 어디에 저장되나요

아래 `{7자리사번}`은 실제 사용자의 숫자 7자리 사번입니다. repo에는 템플릿 scaffold로 `data/boi/private/0000000/`만 들어 있습니다.

| 요청 | 폴더 |
|---|---|
| 회의록, 개인 메모 | `data/boi/private/{7자리사번}/notes/` |
| SOP 초안 | `data/boi/private/{7자리사번}/sop-drafts/` |
| Action 초안 | `data/boi/private/{7자리사번}/action-drafts/` |
| Event 후보 | `data/boi/private/{7자리사번}/event-drafts/` |
| Mermaid 도식 | `data/boi/private/{7자리사번}/diagrams/` |
| Context pack | `data/boi/private/{7자리사번}/context-packs/` |
| Workflow dry-run | `data/boi/private/{7자리사번}/workflow-simulations/` |
| Langflow 설계 초안 | `data/boi/private/{7자리사번}/langflow-plans/` |
| 주간보고, 업무증빙 | `data/boi/private/{7자리사번}/reports/` |
| 공유 전 정리본 | `data/boi/private/{7자리사번}/promotion-drafts/` |
| 사용 예제 | `data/boi/private/{7자리사번}/usage-examples/` |
| 오래된 문서 | `data/boi/private/{7자리사번}/_archive/YYYY/MM/` |

## Local Private 규칙

agent가 저장하는 Local Private 문서는 다음 값을 가져야 합니다.

```yaml
employee_id: "1234567"
local_owner_ref: local-private:1234567
visibility: local-private
local_only: true
promotion_status: local_only
archive_status: active
contains_sensitive: unknown
```

agent는 사용자가 lint를 몰라도 저장 전 자체 검증을 수행하고, `index.md`와 `log.md`를 업데이트해야 합니다.

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

MCP를 설정하면 agent가 원격 BoI Wiki에서 SOP, Event Type, Action Spec, Workflow Status를 검색할 수 있습니다.

MCP를 몰라도 Local Private 작성은 계속 동작합니다.

설정 예시는 `.codex/config.toml.example`을 참고하세요.

공식 MCP는 shared BoI Wiki MCP 하나입니다.

```text
http://boi-wiki-mcp.example:28200/mcp
```

사내 실제 주소는 운영자에게 별도로 공유받아 개인 `.env` 또는 MCP client 설정에만 입력합니다. agent는 이 MCP를 조회와 승인된 원격 게시에만 사용해야 합니다. Local Private 원본은 사용자 명시 승인 없이 원격으로 보내지 않습니다.

## 활용 사례

아래 문서를 agent에게 보여주거나 그대로 요청 문장으로 복사해도 됩니다.

- [SOP Mermaid Flow](data/boi/private/0000000/usage-examples/sop-mermaid-flow.md)
- [Event to Action Plan](data/boi/private/0000000/usage-examples/event-to-action-plan.md)
- [API Doc to Action Spec](data/boi/private/0000000/usage-examples/api-doc-to-action-spec.md)
- [Meeting to BoI](data/boi/private/0000000/usage-examples/meeting-to-boi.md)
- [AI Native Workflow Draft](data/boi/private/0000000/usage-examples/ai-native-workflow-draft.md)
- [Local Only Mode](data/boi/private/0000000/usage-examples/local-only-mode.md)
- [Remote Context Pack](data/boi/private/0000000/usage-examples/remote-context-pack.md)

## 작업별 Skills

agent가 skill을 지원하면 다음 skill을 우선 사용합니다. 지원하지 않아도 `AGENTS.md` 규칙만으로 같은 방식으로 진행할 수 있습니다.

- `boi-wiki-local`
- `boi-sop-flow-visualizer`
- `boi-event-workflow-planner`
- `boi-action-author`
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
