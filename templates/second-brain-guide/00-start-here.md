---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "BoI Wiki Local 시작하기"
description: "비개발자가 업무용 Harness를 구성하고 선택적으로 Second Brain을 연결하는 시작 안내"
tags: [LocalPrivate, MetaHarness, SecondBrain, Guide, Onboarding]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:start-here
visibility: local-private
classification: internal
owner: "{{employee_id}}"
employee_id: "{{employee_id}}"
local_owner_ref: local-private:{{employee_id}}
local_only: true
promotion_status: local_only
retention_class: working
retention_until: ""
archive_status: active
artifact_visibility: memory
lifecycle_state: memory
memory_candidate: false
cleanup_policy: keep
review_after: {{review_after}}
contains_sensitive: false
guide_release: "3.2.0"
guide_audience: "전체 구성원"
guide_duration_minutes: 3
guide_prerequisites: "없음"
guide_execution: "Harness 구성 또는 Second Brain 설정 중 하나를 AI에게 요청한다"
guide_success: "Meta Harness와 Second Brain의 역할 차이를 설명하고 첫 요청을 전달할 수 있다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "01-meta-harness-map.md"
guide_boundary: "local-only"
source_refs:
  - type: local-guide-source
    ref: templates/second-brain-guide/00-start-here.md
---

# BoI Wiki Local 시작하기

BoI Wiki Local은 사용자의 업무 설명을 **BoI Wiki를 잘 쓰기 위한 Harness**로 구성하고, 개인 지식을 Local Private에서 안전하게 축적한 뒤 검토된 조직 지식으로 연결하는 **Meta Harness**입니다. 별도 앱이나 Python 프로그램이 아니므로 비개발자도 AI에게 자연어로 요청할 수 있습니다.

![Obsidian 1.13.4에서 sanitized Agentic AI Golden Journey 홈과 공개 파일 트리를 보는 화면](_media/35-golden-journey-home.webp)

[화면 35를 원본 크기로 열기](_media/35-golden-journey-home.webp)

대표 화면은 공개 자료만 담은 Agentic AI Change Radar Community Golden Journey를 실제 Obsidian 1.13.4에서 연 예시입니다. Obsidian이 없어도 아래 요청문과 연결 문서를 일반 Markdown으로 그대로 사용할 수 있습니다.

| 선택 | 가능한 작업 | 추가 설치 |
|---|---|---|
| Local only | 공통 원본 수집·지식 정제·Query·Review | 없음 |
| + Obsidian | Golden Journey·Backlinks·Bases·Canvas 탐색 | Obsidian |
| + MCP | 권한 범위의 공유 BoI Wiki 조회 | MCP client 연결 |
| 둘 다 | Local 지식 탐색과 공유 Wiki 조회 | Obsidian + MCP |

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

## 1. 업무용 BoI Harness 구성

```text
내가 하는 업무를 설명할게. 이 업무에서 좋은 지식을 만들고 BoI Wiki에
축적할 수 있도록 역할, Skill, 작업 흐름, 검토 기준을 포함한 Harness를 구성해줘.
```

## 2. Flagship Second Brain 설정

```text
이 저장소를 내 BoI Wiki Local Second Brain으로 설정해줘. 대화와 자료 폴더에서
오래 쓸 지식을 정리하고, 공유할 가치가 있는 내용만 BoI Wiki promotion 후보로
만들어줘. 원격 자동 업로드는 하지 마.
```

AI는 필요한 질문만 최대 3개 하고, 변경 내용을 쉬운 말로 보여준 뒤 승인받아 설정합니다. Python, 터미널, Obsidian, MCP는 필수가 아닙니다. 자세한 절차는 [AI에게 설치 맡기기](12-ai-assisted-setup.md)를 참고합니다.

## 제품의 네 계층

1. Meta Harness Core — 업무를 분석하고 기존 Skill·역할·DAG·산출물·검토 기준을 구성
2. Flagship Capability — Second Brain으로 대화와 자료를 장기 지식으로 유지
3. Case Candidate — Core가 만든 결과를 깊이 보여 주며 현재 `community` 상태인 범용 Second Brain Flagship
4. Admin·CI — fixture·평가기·benchmark·release evidence; 일반 사용자에게는 숨김

자세한 구분은 [Core·Flagship·Case·Admin 계층 지도](01-meta-harness-map.md)를 참고합니다. 실제 업무를 Harness로 구성하는 전체 여정은 [내 업무용 BoI Harness 만들기](02-build-your-harness.md)에서 이어집니다.

## 무엇을 하려는지에 따라 선택하세요

- 다른 구성원이 만든 비공식 walkthrough와 현재 검증 상태를 참고하려면 [활용 사례 허브](25-use-case-playbook.md)
- OKF와 BoI 문서 구조를 이해하려면 [OKF와 BoI Profile](21-okf-and-boi-profile.md)
- 대화·메일·웹·문서를 오래 축적하고 재사용하려면 [Capture에서 지식까지](23-capture-distill-review.md)
- 승인된 지식을 기준으로 지난 검토 이후 무엇이 달라졌는지 관리하려면 [지식 변화 운영과 사용자 프롬프트](38-knowledge-change-operations.md)
- 여러 자료로 근거·가설·판정을 관리하려면 [범용 Investigation Pattern](29-investigation-pattern.md)
- Obsidian 없이 사용하려면 [Obsidian 없는 사용법](26-no-obsidian.md)
- Obsidian으로 링크·Graph·Bases·Canvas를 보려면 [Obsidian 설치와 Vault 연결](30-obsidian-install-and-vault.md)
- 공개 Golden Journey를 실제 화면으로 따라 하려면 [Obsidian Golden Journey](32-obsidian-golden-journey.md)
- 사내 Wiki 조회와 조직 공유 경계를 보려면 [MCP와 Team·Public 공유](50-mcp-and-promotion.md)
- GitHub clone을 사내 Bitbucket origin으로 바꾸거나 업데이트하려면 [업데이트와 rollback](70-update-and-rollback.md)
- 문제가 생기면 [문제 해결과 FAQ](60-troubleshooting.md)

## Second Brain의 고정 지식 순환

Second Brain은 BoI Wiki Local의 중요한 횡단 Harness입니다. 모든 사용자에게 강제되지는 않지만 연결하면 다음 순환을 장기간 유지할 수 있습니다.

```text
대화·메일·웹·문서·업무 자료
→ Local Private 지식 축적
→ 기존 지식 보강·교정·연결
→ 업무 사례에서 검색·재사용
→ OKF·BoI 기준 정제
→ 검토된 조직 지식으로 promotion
```

원시 대화 transcript는 기본 저장하지 않고, 가치 없는 대화는 새 문서를 만들지 않습니다. 원본은 보존하고, 기존 지식과 같으면 `이미 반영됨`으로 처리합니다. 새 근거는 기존 문서에 보강하고, 명시적 교정은 이전 이력을 보존한 채 최신 내용으로 교체합니다.

## Local/Remote 경계

1. MCP 없음: boi-wiki-local의 로컬 문서만 작성·검색·정리합니다.
2. MCP 연결됨: 권한 범위의 사내 boi-wiki 문서를 검색·참조하여 로컬 문서를 작성할 수 있습니다.
3. 단순 MCP 연결만으로 Local Private 문서가 웹에 자동 적재되지 않습니다.
4. Team/Public 적재는 promotion 초안 → 민감정보·출처·공개 범위 검증 → 미리보기 → 사용자 승인 → 지원되는 원격 등록 순서를 지킵니다.

정상 결과는 Local Private가 기본 상태이고, 다음에 읽을 페이지를 하나 고른 상태입니다. 실패하면 [문제 해결과 FAQ](60-troubleshooting.md)로 이동합니다.

다음: [제품 계층 지도](01-meta-harness-map.md) → [AI에게 설치 맡기기](12-ai-assisted-setup.md)
