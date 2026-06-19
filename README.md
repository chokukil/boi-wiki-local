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
만들어진 SOP 내용 괜찮네. Public으로 공유해줘.
팀 주간보고 작성한 거 괜찮아 보이네. 팀 주간보고로 올려줘.
오래된 Private BoI 정리 후보 보여줘.
MCP 설정은 모르겠으니 local만 써줘.
```

## What This Is

- 개인 업무 메모, 회의록, SOP 초안, 주간보고 초안을 Markdown/OKF 구조로 쌓는 폴더입니다.
- Web BoI Wiki에는 자동으로 보이지 않습니다.
- 사용자가 명시적으로 승인하기 전에는 원격으로 전송하거나 공개하지 않습니다.
- MCP, Python, Docker, Git을 몰라도 쓸 수 있습니다.

## First Use

가장 쉬운 방법은 agent에게 repo URL을 주는 것입니다.

```text
이 boi-wiki-local 저장소를 설치하고, 이 폴더를 내 BoI Wiki Local로 설정해줘.
```

Agent는 clone, zip 다운로드, 또는 현재 폴더 템플릿 구성을 상황에 맞게 선택합니다. Git이 없으면 일반 폴더로 시작합니다.

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

WSL, Ubuntu, Linux:

```sh
sh install.sh
```

설치 스크립트를 실행하지 않아도 됩니다. agent에게 "이 폴더를 BoI Wiki Local로 써줘"라고 말하면 `AGENTS.md`와 skill 규칙을 기준으로 작업합니다.

## Where Things Go

| Request | Folder |
|---|---|
| 회의록, 개인 메모 | `data/boi/private/me/notes/` |
| SOP 초안 | `data/boi/private/me/sop-drafts/` |
| Action 초안 | `data/boi/private/me/action-drafts/` |
| 주간보고, 업무증빙 | `data/boi/private/me/reports/` |
| 공유 전 정리본 | `data/boi/private/me/promotion-drafts/` |
| 오래된 문서 | `data/boi/private/me/_archive/YYYY/MM/` |

## Local Private Rules

Agent가 저장하는 Local Private 문서는 다음 값을 가져야 합니다.

```yaml
visibility: local-private
local_only: true
promotion_status: local_only
archive_status: active
contains_sensitive: unknown
```

Agent는 사용자가 lint를 몰라도 저장 전 자체 검증을 수행하고, `index.md`와 `log.md`를 업데이트해야 합니다.

## Sharing

"Public으로 공유해줘" 또는 "팀 주간보고로 올려줘"라고 말해도 바로 공개되지 않습니다.

정상 흐름:

1. agent가 local promotion draft를 만듭니다.
2. agent가 민감정보, 출처, 공개 범위, preview를 보여줍니다.
3. 사용자가 명시적으로 승인합니다.
4. 원격 BoI Wiki에는 draft-only로 요청합니다.
5. shared repo에서 별도 검증과 commit이 필요합니다.

## Optional MCP

MCP를 설정하면 agent가 원격 BoI Wiki에서 SOP, Event Type, Action Spec을 검색할 수 있습니다.

MCP를 몰라도 Local Private 작성은 계속 동작합니다.

설정 예시는 `.codex/config.toml.example`을 참고하세요.

## FAQ

### Git이 없어도 되나요?

됩니다. Git이 있으면 agent가 local history를 남기고, 없으면 일반 폴더로 동작합니다.

### 내 문서가 회사 Wiki에 올라가나요?

아닙니다. 이 폴더의 Local Private 문서는 Web BoI Wiki에 자동으로 올라가지 않습니다.

### MCP를 몰라도 되나요?

됩니다. MCP는 원격 BoI Wiki 검색을 편하게 만드는 선택 기능입니다.

### 검증은 누가 하나요?

agent가 합니다. 일반 사용자가 lint 명령을 직접 실행하지 않는다는 전제로 `AGENTS.md`와 skill에 검증 규칙이 들어 있습니다.
