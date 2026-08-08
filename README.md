# BoI Wiki Local

BoI Wiki Local은 사용자의 업무를 BoI Wiki용 Harness로 구성하고, 개인 지식을 Local Private에서 안전하게 축적해 검토된 조직 지식으로 연결하는 **Production-grade 품질 목표의 Meta Harness Candidate**입니다. 실제 외부 검증이 끝나기 전에는 production-ready를 주장하지 않습니다.

한국어 전체 안내: [README_KO.md](README_KO.md)

## Choose the easiest path

| Choice | What it enables | Extra install |
|---|---|---|
| Local only | Common-source intake, curation, Query, Review | None |
| + Obsidian | Golden Journey, Backlinks, Bases, Canvas | Obsidian |
| + MCP | Read shared BoI Wiki within the principal ACL | MCP client connection |
| Both | Explore Local knowledge and query shared Wiki | Obsidian + MCP |

Copy one request into Codex or Claude:

```text
이 저장소를 설치하고 Second Brain을 설정해줘.
```

```text
Obsidian으로 Golden Journey를 안전하게 열어줘.
```

```text
QuickAdd와 Web Clipper 설치 preview를 보여줘.
```

```text
BoI Wiki MCP를 현재 AI 클라이언트에 연결해줘.
```

![Sanitized Agentic AI Golden Journey in Obsidian 1.13.4](templates/second-brain-guide/_media/35-golden-journey-home.webp)

Walkthrough: [Obsidian Golden Journey](templates/second-brain-guide/32-obsidian-golden-journey.md)

Windows 배포에서는 `C:\Users\<계정>\Projects\boi-wiki-local` clone 자체를 Codex·Claude의 작업 폴더로 엽니다. WSL 사본이나 다른 폴더에는 이 clone의 project Skill이 자동 활성화되지 않습니다.

## 가장 쉬운 시작

BoI Harness 구성:

> 내가 하는 업무를 설명할게. 이 업무에서 좋은 지식을 만들고 BoI Wiki에 축적할 수 있도록 역할, Skill, 작업 흐름, 검토 기준을 포함한 Harness를 구성해줘.

Second Brain 설정:

> 이 저장소를 내 BoI Wiki Local Second Brain으로 설정해줘. 대화와 자료 폴더에서 오래 쓸 지식을 정리하고, 공유할 가치가 있는 내용만 BoI Wiki promotion 후보로 만들어줘. 원격 자동 업로드는 하지 마.

Global Insight Golden Journey:

> 이번 주 Agentic AI에서 바뀐 내용만 기존 지식과 비교해 반영 후보로 보여줘. 보고서는 만들지 말고 변경 세트와 검토 목록만 만들어줘.

## 제품 구조

```text
Meta Harness Core: boi-harness-builder + OKF·BoI·promotion 계약
Flagship Capability: boi-second-brain
Flagship Case Candidate: 범용 Second Brain (현재 community)
Global Insight Cases: Agentic AI Change Radar + FAB Digital Twin + Scientific Foundation Model (community)
Admin·CI: fixture, evaluator, benchmark, release evidence
```

Core lifecycle: `Audit → Frame → Capture·Distill·Query·Lint·Review 설계 → 역할·DAG → Validate → Evolve`.

승인된 개인 Harness는 채팅 답변으로 끝내지 않고 Local Profile의 `notes/harnesses/<이름>.md`에 OKF 0.1 + BoI Profile 0.1-local 카드로 보존합니다. 다음 세션에는 “저장된 `<이름>` Harness로 이번 자료를 처리해줘”라고 요청해 같은 역할·DAG·산출물·검토 계약을 다시 사용합니다.

- 사용자 Wiki: [Start Here](templates/second-brain-guide/00-start-here.md)
- 계층 지도: [Core·Flagship·Case·Admin](templates/second-brain-guide/01-meta-harness-map.md)
- 실사례 모음: [cases/README.md](cases/README.md)
- Global Insight 계약: [templates/global-insight/README.md](templates/global-insight/README.md)
- Global Insight 검증 상태: [research/global-insight-implementation-status.md](research/global-insight-implementation-status.md)

Python·Obsidian·MCP는 일반 사용자 필수 요구사항이 아닙니다. Local Private 원문은 자동으로 원격 등록되지 않으며, Team/Public는 정제·검증·미리보기·사용자 승인 후 지원되는 기능에서만 등록할 수 있습니다.

설치와 업데이트는 사내 Bitbucket 읽기를 우선 확인하고 네트워크로 도달할 수 없을 때만 GitHub source를 사용합니다. 사내 인증 또는 저장소 권한 실패는 fallback하지 않습니다. `MCP 설치해줘`라는 자연어 요청은 고정된 connection descriptor를 이용한 Codex·Claude 설정 preview로 라우팅되며, Git origin에서 MCP endpoint를 추정하거나 Local Private 자료를 전송하지 않습니다. endpoint·인증·필수 도구가 없으면 성공을 꾸미지 않고 `pending-external-system`으로 남깁니다.
