---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "조사 기반 Second Brain 원칙"
description: "LLM Wiki, CODE, PARA, linked notes 사례를 BoI 방식으로 적용한 기준"
tags: [LocalPrivate, Research, LLMWiki, Method]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:research-backed-method
visibility: local-private
classification: internal
owner: "{{employee_id}}"
employee_id: "{{employee_id}}"
local_owner_ref: local-private:{{employee_id}}
local_only: true
promotion_status: local_only
retention_class: working
retention_until: ""
artifact_visibility: memory
lifecycle_state: memory
memory_candidate: false
cleanup_policy: keep
review_after: {{review_after}}
archive_status: active
contains_sensitive: false
guide_release: "3.0.0"
guide_audience: "Second Brain 운영 원리를 이해하려는 구성원"
guide_duration_minutes: 8
guide_prerequisites: "활용 사례 지도 확인"
guide_execution: "외부 방법론에서 채택한 원칙과 BoI-native 경계를 비교한다"
guide_success: "폴더나 플러그인보다 불변 원문·정제·검색·검토·공유 경계를 우선한다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "24-daily-weekly-review.md"
guide_boundary: "local-only"
source_refs:
  - type: external-method
    ref: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
  - type: external-method
    ref: https://fortelabs.com/blog/para/
  - type: external-video
    ref: https://www.youtube.com/watch?v=z4AbijUCoKU
  - type: external-video
    ref: https://www.youtube.com/watch?v=fGJv6hiXPmk
  - type: official-doc
    ref: https://obsidian.md/help/web-clipper
---

# 조사 기반 Second Brain 원칙

핵심 절차는 이 Wiki만으로 완결됩니다. 아래 링크는 배경을 더 알고 싶은 사용자를 위한 선택 자료이며 접속할 수 없어도 기능에는 영향이 없습니다.

## 우리 방식으로 번역한 원칙

| 외부 패턴 | BoI Wiki Local 적용 | 채택하지 않는 부분 |
|---|---|---|
| LLM Wiki의 immutable raw·wiki·schema | 잠긴 capture, 정제 지식, AGENTS/Skill 계약 | LLM이 원문이나 공유 범위를 임의 변경 |
| Ingest·Query·Lint | capture/distill, local search, lint/review | 매 질문마다 원문 전체를 다시 합성 |
| CODE의 Capture·Organize·Distill·Express | 수집, Profile/index/link, 정제, promotion preview | 즉시 외부 게시 또는 개인 맥락 전체 공유 |
| PARA의 actionability | lifecycle, memory candidate, archive, promotion 상태 | 별도 PARA 최상위 폴더 복제 |
| Linked notes와 MOC | Markdown 링크, index, Context Pack, Backlinks | 링크 수를 품질로 간주하거나 자동 연결을 사실로 취급 |
| 실제 사용자 note processing | inbox를 비우는 대신 보류·재검토·archive 허용 | Inbox Zero 강제와 매일 모든 문서 정리 |

이 표의 운영 패턴은 OKF·BoI Profile 위에서만 동작합니다. 외부 Vault의 page type, 폴더, wikilink, 플러그인 schema는 가져오지 않으며 모든 Local 파생 문서는 OKF `0.1` + BoI Profile `0.1-local`을 유지합니다.

## 사람이 맡는 일과 에이전트가 맡는 일

사람은 출처 선택, 업무 의미, 민감도, 최종 판단과 공유 승인을 맡습니다. 에이전트는 요약, 연결 후보, 중복·누락·충돌 탐지, 파일 정리와 검증을 돕습니다. 에이전트가 만든 연결은 제안이며 출처와 사용자의 검토가 없으면 canonical 사실이 아닙니다.

## 처음에는 단순하게

1. 플러그인 없이 capture 한 건을 만듭니다.
2. 원문과 정제본을 분리합니다.
3. 검색 또는 관련 문서 링크 중 편한 방식으로 다시 찾습니다.
4. 주간 review에서 오래된 주장과 고립 문서를 확인합니다.
5. 반복 가치가 증명된 문서만 promotion preview로 보냅니다.

## 선택형 더 보기

- [Andrej Karpathy, LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [Forte Labs, PARA](https://fortelabs.com/blog/para/)
- [Forte Labs, Progressive Summarization](https://fortelabs.com/blog/progressive-summarization-a-practical-technique-for-designing-discoverable-notes/)
- [Nick Milo, Give Me 15 Minutes. I'll Teach You 80% of Obsidian](https://www.youtube.com/watch?v=z4AbijUCoKU)
- [Nicole van der Hoeven, How Real People Process Notes](https://nicolevanderhoeven.com/blog/20220512-how-real-people-process-notes/)
- [산업 연구자의 Obsidian Second Brain 사례 연구](https://arxiv.org/abs/2509.20187)

이전: [Second Brain 활용 사례](25-use-case-playbook.md) · 다음: [일간·주간 review](24-daily-weekly-review.md)

## 업무형 Second Brain BP를 BoI 방식으로 번역

- [Bianca Pereira와 Nick Milo의 research workflow](https://www.youtube.com/watch?v=fGJv6hiXPmk): source note에서 질문과 MOC를 거쳐 산출물로 발전시키는 흐름
- [Nicole van der Hoeven의 업무 노트 사례](https://www.youtube.com/watch?v=0g38K_DtxFI): 개발·시험 로그를 계속 누적하고 다시 사용하는 방식
- [How to create things with your notes](https://www.youtube.com/watch?v=4zrs_vVRwD4): 노트를 최종 산출물로 표현하는 흐름
- [Obsidian Web Clipper 공식 안내](https://obsidian.md/web-clipper): 웹 자료를 Local Markdown으로 수동 수집하는 선택 기능

BoI Wiki Local은 이를 **Source → preview → 기존 지식 비교 → Query → Lint → Distill → Review → Promote**로 적용합니다. 제작자의 Vault 구조나 플러그인 조합은 복제하지 않습니다.

## 영상에서 보이는 자동 정리를 우리 방식으로 쓰는 법

Karpathy의 원문은 한 자료가 summary, entity, concept, index, log 등 여러 Wiki 페이지를 갱신할 수 있고, batch ingest도 가능하다고 설명합니다. BoI Wiki Local은 이 경험을 범용 `boi-second-brain` Skill로 제공하되 무승인 자동 수정을 허용하지 않습니다.

1. 이메일·웹·표·PDF·이미지·회의 메모를 불변 source로 모읍니다.
2. Skill이 자료 수와 컨텍스트를 보고 review 가능한 batch로 나눕니다.
3. AI가 바뀔 Case Hub, 개념, 비교, index, log와 승인할 변경 확인값을 먼저 보여줍니다.
4. 사용자가 같은 hash를 승인한 경우에만 compiled Markdown을 갱신합니다.
5. `query` 결과도 출처·반증·미확인 항목을 갖춘 문서로 저장할 수 있습니다.
6. `lint`가 contradiction, stale claim, unsupported conclusion, orphan, downstream stale을 찾습니다.
7. Obsidian Graph·Bases·Canvas는 이 canonical Markdown과 Properties를 시각화합니다.

[Nick Milo와 Bianca Pereira의 research workflow 영상](https://www.youtube.com/watch?v=fGJv6hiXPmk)은 source 수집, note 추출, 질문과 MOC, history 보존, 결과물 작성의 연결을 보여줍니다. [Obsidian 공식 Web Clipper](https://obsidian.md/help/web-clipper)는 공개 웹 자료를 Local Markdown으로 수집하는 선택 경로입니다. 두 사례의 동작 원리는 채택하지만 Vault 구조와 영상 화면은 복제하지 않습니다.

## 출처 검증 수준

설계 근거는 `primary-text`, `oembed-metadata-only`, `transcript-reviewed`, `unverified`로 구분합니다. 현재 5개 영상은 공개 oEmbed 호환 응답으로 제목과 채널만 재검증한 `oembed-metadata-only`이며 transcript를 검토한 것으로 표시하지 않습니다. 표의 업무 여정은 영상 내용을 사실처럼 복제한 것이 아니라 공개 맥락을 BoI 방식으로 번역한 설계 선택입니다. 핵심 Ingest·Query·Lint 계약은 Karpathy 원문과 실제 저장소 contract test를 기준으로 하며, YouTube가 429 또는 fetch 제한으로 열리지 않아도 기능에는 영향이 없습니다.
