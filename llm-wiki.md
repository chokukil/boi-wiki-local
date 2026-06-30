# Local LLM Wiki

이 파일 하나만으로도 시작할 수 있습니다.

Agent에게 다음처럼 말하세요.

```text
이 파일을 내 BoI Wiki Local inbox처럼 써줘.
```

커지면 agent가 7자리 사번을 확인한 뒤 `data/boi/private/{7자리사번}/` 아래 OKF Markdown 문서로 나눕니다.

## Inbox

- 아직 정리되지 않은 개인 메모를 여기에 임시로 둡니다.

## Core Rules

- Local Private content stays local unless the user explicitly approves sharing.
- MCP is optional. The official remote MCP is shared BoI Wiki MCP; do not require a local MCP server.
- Use skills or the same rules for work BoI notes, SOP diagrams, workflow-definition plans, work request specs, context packs, pre-execution simulations, and Langflow plans.
- SOP is important for standardized work, but one-off or repeated personal work can start as a Local Private work BoI without forcing an SOP.
- Bulk dictionary candidates are curated in data/override/manifest or promotion drafts, not by changing code per term.
- Before sharing, create a sanitized promotion draft and show preview/diff for confirmation.

## Useful Requests

```text
설비 이상 대응 SOP를 Mermaid 프로세스 플로우로 그려줘.
이 이벤트가 발생하면 어떤 업무 BoI와 업무 흐름이 이어지는지 알려줘.
기존 API 문서를 Action 초안으로 만들고 업무 흐름에 연결해줘.
이번 회의 내용을 비정형 업무 BoI로 정리해줘.
매주 반복하는 FAB Trend 보고 업무를 SOP 추가 초안과 Action 연결 후보로 정리해줘.
대량 dictionary 후보를 canonical, alias, 제외, parent curation 후보로 정리해줘.
원격 BoI Wiki를 검색해서 이번 업무용 context pack을 만들어줘.
MCP 설정은 모르겠으니 local만 써줘.
```
