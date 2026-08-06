# Second Brain 연구 Source Ledger

조사 기준일: 2026-08-01

이 원장은 BoI Wiki Local Second Brain 설계와 Wiki 가이드 작성에 사용한 외부 근거를 기록합니다. Local Private 원문이나 사내 문서는 포함하지 않습니다.

## LLM Wiki와 지식 운영

| 출처 | 설계에 반영한 내용 |
|---|---|
| [Andrej Karpathy, LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) | 원문을 불변으로 보존하고 LLM이 정제 Wiki를 유지한다. Ingest, Query, Lint를 분리하며 Obsidian은 IDE로 사용할 수 있다. |
| [Forte Labs, Building a Second Brain](https://fortelabs.com/blog/basboverview/) | Capture, Organize, Distill, Express 순환을 참고하되 저장 구조는 PARA가 아니라 BoI-native로 유지한다. |
| [Forte Labs, PARA](https://fortelabs.com/blog/para/) | 행동 가능성 중심 분류 원칙만 참고하고 별도 PARA 폴더 체계는 도입하지 않는다. |
| [Zettelkasten overview](https://zettelkasten.de/overview/) | 작은 지식 단위, 명시적 연결, 지속적인 재사용 원칙을 적용한다. |
| [Andy Matuschak, About these notes](https://notes.andymatuschak.org/About_these_notes) | 정제 문서는 점진적으로 축적하고 서로 연결된 evergreen 성격을 갖게 한다. |

## Obsidian 공식 문서

| 출처 | 확인 항목 |
|---|---|
| [Vault](https://help.obsidian.md/vault) | 기존 Local Private 폴더를 Vault로 직접 열 수 있다. |
| [Properties](https://help.obsidian.md/properties) | YAML frontmatter를 Properties로 사용할 수 있으며 중첩 구조는 제한된다. |
| [Bases](https://help.obsidian.md/bases) | Properties를 기반으로 문서 목록과 뷰를 만들 수 있다. |
| [Links](https://help.obsidian.md/links) | 표준 Markdown 링크와 내부 링크 탐색을 지원한다. |
| [Backlinks](https://help.obsidian.md/plugins/backlinks) | 현재 문서를 참조하는 문서를 탐색할 수 있다. |
| [Community plugins](https://help.obsidian.md/community-plugins) | 커뮤니티 플러그인은 제3자 코드를 실행하므로 별도 신뢰 검토가 필요하다. |
| [Plugin security](https://obsidian.md/help/plugin-security) | Restricted Mode는 커뮤니티 플러그인의 실행을 막지만 설치 파일 자체를 자동 제거하지 않으며, 플러그인은 Obsidian과 같은 파일·네트워크 접근 수준을 가질 수 있다. |
| [Web Clipper](https://help.obsidian.md/web-clipper) | 웹 수집 확장 가능성이 있으나 기본 설치 범위에서는 제외한다. |
| [License](https://obsidian.md/license) | 앱 사용 조건과 상업적 사용 정책을 공식 문서에서 확인한다. |

## 플러그인 및 확장 후보

| 후보 | 판단 |
|---|---|
| [QuickAdd](https://github.com/chhoumann/quickadd) · [manifest](https://raw.githubusercontent.com/chhoumann/quickadd/master/manifest.json) | 기본 후보. 2026-08-01 확인값은 2.20.0, 최소 Obsidian 1.13.0이다. 입력 시작점 하나만 사용하고 JavaScript macro, 외부 API, 시스템 명령은 사용하지 않는다. |
| [Omnisearch](https://github.com/scambier/obsidian-omnisearch) · [manifest](https://raw.githubusercontent.com/scambier/obsidian-omnisearch/master/manifest.json) | 기본 후보. 2026-08-01 호환성 snapshot의 선택값은 1.30.1, 최소 Obsidian 1.13.3이다. 로컬 검색만 사용하고 opt-in HTTP server는 비활성화한다. |
| [Tasks](https://github.com/obsidian-tasks-group/obsidian-tasks) | 선택 기능. 지식 관리와 업무 실행을 섞지 않도록 별도 활성화한다. |
| [Dataview](https://github.com/blacksmithgu/obsidian-dataview) | Bases로 부족할 때만 검토한다. DataviewJS는 기본 제외한다. |
| [Templater](https://github.com/SilentVoid13/Templater) | 기본 제외. JavaScript와 시스템 명령 실행 범위가 현재 필요보다 넓다. |
| [Smart Connections](https://github.com/brianpetro/obsidian-smart-connections) | 실험 기능. 모델, 네트워크, 개인정보, 라이선스를 별도 검토한다. |
| [Obsidian LLM Wiki](https://github.com/green-dalii/obsidian-llm-wiki) | 생산 구성에서 제외. 별도 Wiki schema와 LLM provider가 OKF·BoI Profile 원천과 충돌할 수 있다. |
| [qmd](https://github.com/tobi/qmd) | 문서 규모가 커졌을 때 로컬 BM25/vector/reranking 검색 확장으로 검토한다. |

## 채택 원칙

1. Markdown과 OKF·BoI Profile이 원천이며 앱과 플러그인은 교체 가능해야 한다.
2. 수집 원문과 정제 문서를 분리한다.
3. Local Private 자료는 사용자 승인 전까지 로컬 경계를 넘지 않는다.
4. 시각화는 Obsidian에 맡기고 플랫폼에는 별도 그래프 UI를 만들지 않는다.
5. Public/Team 공유는 동일한 로컬 원문에서 별도의 정제본과 promotion 미리보기를 만든다.
6. 플러그인의 현재 버전과 최소 앱 버전은 설치 직전 manifest에서 다시 확인하고, Vault 파일 감시가 검증되기 전에는 플러그인을 설치하지 않는다.
## 2.1 활용 사례·영상 조사 원장

확인일은 2026-08-01이며, 외부 제작자의 화면·Vault 구조·유료 템플릿은 복제하지 않았다. 링크는 더 보기용이고 핵심 절차는 `templates/second-brain-guide/` 안에서 완결한다.

| 제목 | URL | BoI Wiki Local에 반영 | 비채택 |
|---|---|---|---|
| Andrej Karpathy, LLM Wiki | [원문](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) | 불변 raw capture, LLM 유지 정제 Wiki, OKF·BoI schema, capture/search/lint 분리 | Local 원문 전체를 매 질의마다 모델에 전달하는 방식 |
| Tiago Forte, PARA | [원문](https://fortelabs.com/blog/para/) | 지금 행동 가능한 지식과 재검토 대상을 구분 | 별도 PARA 폴더 트리 강제 |
| Tiago Forte, Progressive Summarization | [원문](https://fortelabs.com/blog/progressive-summarization-a-practical-technique-for-designing-discoverable-notes/) | capture를 보존한 채 결정·근거·질문으로 점진적 정제 | 원문 덮어쓰기와 과도한 강조 레이어 |
| Nick Milo, Obsidian for Beginners | [영상](https://www.youtube.com/watch?v=z4AbijUCoKU) | Local Markdown, Links, Backlinks, 작은 초기 구조와 Core 우선 | 제작자 Vault·영상 프레임·플러그인 묶음 복제 |
| Nicole van der Hoeven, How Real People Process Notes | [글](https://nicolevanderhoeven.com/blog/20220512-how-real-people-process-notes/) | inbox 보류, `review_after`, archive를 정상 상태로 안내 | Inbox Zero 강제와 미정리 노트 실패 판정 |
| Obsidian Use Among Early Career Industry Researchers | [논문](https://arxiv.org/abs/2509.20187) | 검색 중심과 링크 중심 사용자를 함께 지원하고 검색 방식이 작성·유지 방식에 미치는 영향을 설명 | Graph 밀도나 링크 수를 지식 품질 KPI로 사용 |
| NicholasSpisak/second-brain | [저장소](https://github.com/NicholasSpisak/second-brain) | 공개 구현 사례의 Markdown·버전관리 원칙을 비교 참고 | 외부 schema·폴더·자동화를 그대로 이식 |

조사 결과를 실제 업무 여정으로 번역한 문서는 `templates/second-brain-guide/25-use-case-playbook.md`와 연결된 범용 사례 Wiki다. 모든 화면은 합성 Profile `0000000`과 합성 업무 데이터로 제작했고, 실제 앱 캡처와 교육용 목업을 media manifest에서 구분했다.

## 2.2 Second Brain 영상 BP

| 영상 | URL | 채택한 여정 | 비채택 |
|---|---|---|---|
| Linking Your Thinking with Nick Milo, How to create a workflow to support your research and knowledge creation efforts | [영상](https://www.youtube.com/watch?v=fGJv6hiXPmk) | source note → 질문 → MOC/Case Hub → writing으로 번역 | 제작자의 Vault 구조 복제 |
| Nicole van der Hoeven, Taking notes for work with Obsidian | [영상](https://www.youtube.com/watch?v=0g38K_DtxFI) | 지속적인 개발·시험 로그와 재사용으로 번역 | 특정 플러그인 의존 |
| Nicole van der Hoeven, How to create things with your notes | [영상](https://www.youtube.com/watch?v=4zrs_vVRwD4) | bottom-up note → 재사용 가능한 산출물로 번역 | 출처 없는 자동 synthesis |
| Tiago Forte, Stop Highlighting Blindly: The Progressive Summarization Secret! | [영상](https://www.youtube.com/watch?v=73s6Dgg3NZ0) | 원문을 보존한 점진적 distill로 번역 | 원문 직접 편집과 무차별 highlight |
| Linking Your Thinking with Nick Milo, Give Me 15 Minutes. I'll Teach You 80% of Obsidian | [영상](https://www.youtube.com/watch?v=z4AbijUCoKU) | Local Markdown, links, Backlinks, 단순 시작으로 번역 | 복잡한 초기 폴더와 plugin stack |

2.3의 실제 번역은 `Source → preview → 기존 지식 비교 → Query → Lint → Distill → Review → Promote`다. 이 흐름은 범용 `boi-second-brain` Skill의 운영 계약이다.

## 2.2.1 검증 수준과 OKF 우선순위

| 출처 | 검증 수준 | 사용 범위 |
|---|---|---|
| Andrej Karpathy, LLM Wiki gist | `primary-text` | 불변 raw, LLM-maintained Wiki, schema, Ingest·Query·Lint의 기준 |
| Nick Milo research workflow | `oembed-metadata-only` | 확인된 제목·채널을 바탕으로 연구 source와 지식 생성 workflow를 선택 참고 |
| Nicole van der Hoeven, Taking notes for work | `oembed-metadata-only` | 확인된 제목·채널을 바탕으로 지속적인 업무 노트와 재사용 동기를 선택 참고 |
| Nicole van der Hoeven, Create things with your notes | `oembed-metadata-only` | 확인된 제목·채널을 바탕으로 노트에서 검토 가능한 산출물로 이어지는 과정을 선택 참고 |
| Tiago Forte, Progressive Summarization | `oembed-metadata-only` | 확인된 제목·채널을 바탕으로 점진적 정제 원칙을 선택 참고 |
| Nick Milo, 80% of Obsidian | `oembed-metadata-only` | 확인된 제목·채널을 바탕으로 Local Markdown과 단순한 시작을 선택 참고 |

`oembed-metadata-only`는 공개 oEmbed 호환 응답으로 제목·채널을 다시 확인했다는 뜻이며 영상 본문이나 전체 transcript를 검토했다는 뜻이 아니다. 표의 “채택한 여정”은 검증된 영상 내용의 복제가 아니라 제목과 공개 맥락을 BoI 업무 흐름으로 번역한 설계 선택이다. 외부 사례는 운영 순환만 참고하며 schema 우선순위는 **기존 BoI Wiki → OKF 0.1 → BoI Profile → Local Private 경계 → LLM Wiki 방식 → Obsidian**으로 고정한다.

2026-08-01 재검증에서 Karpathy 원문의 immutable raw, maintained Markdown Wiki, schema, Ingest·Query·Lint, answer filing, Web Clipper·Graph의 선택 사용을 다시 확인했다. YouTube 직접 페이지는 429·fetch 제한으로 재현성 있게 열리지 않았지만 공개 oEmbed 호환 응답으로 위 5개 링크의 제목과 채널은 다시 확인했다. transcript는 검토하지 않았으므로 영상은 여전히 선택형 더 보기이며 핵심 Wiki 절차의 단독 근거로 사용하지 않는다.

## 2.3 재검증 — 범용 Skill과 실제 사용자 흐름

확인일: 2026-08-02. 아래 표는 제품 Core에 반영한 근거와 대표 사례에만 반영한 근거를 분리한다.

| 출처 | 확인 범위 | 범용 Core에 채택 | 채택하지 않은 부분 |
|---|---|---|---|
| [Andrej Karpathy, LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) | 원문 전체, 특히 Architecture·Operations·Tips | immutable raw → maintained wiki → schema, 한 자료가 여러 페이지를 갱신하는 ingest, citation이 있는 query 저장, contradiction·stale·orphan lint, index·append-only log | 별도 schema로 OKF·BoI Profile 대체, LLM 무승인 일괄 수정, `[[wikilink]]`를 canonical 관계로 사용 |
| [Nick Milo / Bianca Pereira, research workflow](https://www.youtube.com/watch?v=fGJv6hiXPmk) | 공개 설명과 chapter 01:13–10:33 | source 수집 → note 추출 → 질문·MOC/Case Hub → 결과물 작성, history 보존, normal Markdown links | 제작자의 Vault 구조·query stack·화면 프레임 복제 |
| [Nick Milo, 80% of Obsidian](https://www.youtube.com/watch?v=z4AbijUCoKU) | 공개 영상 메타데이터 | Local Markdown, links, Backlinks, 작은 초기 구조 | 초보자에게 많은 폴더·플러그인 선설치 |
| [Nicole van der Hoeven, Taking notes for work](https://www.youtube.com/watch?v=0g38K_DtxFI) | 공개 영상 메타데이터 | 지속되는 업무 로그와 재사용 가능한 지식의 분리 | 특정 개인 workflow·플러그인 의존 |
| [Nicole van der Hoeven, How to create things with your notes](https://www.youtube.com/watch?v=4zrs_vVRwD4) | 공개 영상 메타데이터 | query 결과를 비교·SOP·Context Pack 같은 durable output으로 저장 | 출처 없는 자동 synthesis |
| [Obsidian Web Clipper 공식 문서](https://obsidian.md/help/web-clipper) | 설치·사용·privacy 설명 | 공개 웹 자료를 URL·수집일이 있는 Local Markdown으로 수동 수집 | 자동 크롤링, 로그인 페이지 일괄 수집, Interpreter 기본 활성화 |
| [Obsidian Graph](https://obsidian.md/help/plugins/graph) · [Bases](https://obsidian.md/help/bases) · [Canvas](https://obsidian.md/help/plugins/canvas) | 공식 Core 기능 문서 | Graph=관계·orphan 탐색, Bases=Properties 목록, Canvas=임시 사고 공간 | 화면의 edge·card를 provenance로 간주 |

판단은 명확하다. 영상에서 보이는 “자료를 넣으면 정리와 그래프가 생기는” 경험은 거대한 앱이나 도메인 전용 Skill로 만들지 않는다. `boi-second-brain` Skill이 입력을 review 가능한 단위로 나누어 preview를 만들고, 사람이 승인한 뒤 OKF·BoI Profile 문서와 표준 Markdown 링크를 갱신한다. Obsidian은 그 결과를 Graph·Bases·Canvas로 보여주는 선택형 IDE다.

## 2.3.1 에이전트 주도 자동 유지관리

확인일: 2026-08-02. 자동 유지관리는 별도 Python 앱이나 상주 서비스가 아니라 Harness bootstrap과 `boi-second-brain` Skill의 세션 계약으로 채택했다.

| 출처 | 확인 범위 | 채택 | 비채택 |
|---|---|---|---|
| [Claude Code memory](https://code.claude.com/docs/en/memory) | 공식 memory 구조와 프로젝트 지침 | 짧은 bootstrap, 주제별 지식, 프로젝트 안의 명시적 운영 지침 | 공급자 전용 memory를 OKF 원본으로 사용 |
| [Claude Code hooks](https://code.claude.com/docs/en/hooks) | 공식 lifecycle hook 문서 | 조직 관리자가 선택적으로 세션 시작·종료 확인을 연결할 수 있다는 운영 가능성 | 일반 사용자에게 hook 개념 노출, 신뢰 승인 우회, 필수 설치 |
| [Codex hooks](https://learn.chatgpt.com/docs/hooks) | 공식 lifecycle hook 문서 | 지원 환경에서 선택형 자동 확인을 구성할 수 있다는 관리자 참고 | GitHub 기본 배포판에 공급자별 설정 강제 |
| [Codex memories](https://learn.chatgpt.com/docs/customization/memories) | 공식 memory 개요 | 일회성 대화와 장기 지식을 구분하는 사용자 경험 | 원시 transcript 복사, Local OKF·BoI 계약 밖의 원천 데이터 |
| [A-MEM](https://arxiv.org/abs/2502.12110) | 논문 초록·방법 | 새 기억을 기존 기억과 연결하고 시간이 지나며 보강·교정하는 원칙 | 연구 구현과 자체 schema의 직접 도입 |
| [ReadDirectoryChangesExW](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-readdirectorychangesexw) | Microsoft API 문서 | 파일 변경 이벤트보다 현재 파일과 SHA256 재검사를 신뢰해야 한다는 판단 | 상주 Windows watcher 서비스 |

일반 사용자 PC에 Python이 없을 수 있으므로 대화 판단, 자료 폴더 검사, SHA256, 문서 생성은 Codex·Claude의 자체 파일 도구가 수행한다. 저장소의 Python 스크립트는 OKF·BoI Profile, 링크, promotion 경계를 릴리스 전에 검사하는 관리자·CI 도구로만 유지한다. `알아서 정리`는 최초 승인된 범위 안에서 묶음 결과만 보고하고, `정리 전 확인`은 변경 요약을 승인받으며, `요청할 때만`은 명시적 자연어 요청에만 반응한다.
