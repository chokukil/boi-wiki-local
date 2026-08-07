---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "내 업무용 BoI Harness 만들기"
description: "비개발자가 업무를 자연어로 설명하고 역할·Skill·작업 흐름·검토 계약이 있는 Harness를 구성하는 안내"
tags: [LocalPrivate, MetaHarness, HarnessBuilder, Beginner, Guide]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:build-your-harness
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
guide_release: "3.1.0"
guide_audience: "AI로 반복 업무를 더 잘 수행하고 싶은 비개발자 포함 전 구성원"
guide_duration_minutes: 10
guide_prerequisites: "00-start-here.md와 01-meta-harness-map.md 확인"
guide_execution: "업무·자료·성공 조건을 자연어로 설명하고 Harness 미리보기와 Local 경계를 확인한다"
guide_success: "역할·기존 Skill·DAG·산출물·오류 처리·검토·promotion 경계를 갖춘 재사용 가능한 Harness가 구성됐다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "12-ai-assisted-setup.md"
guide_boundary: "local-only"
source_refs:
  - type: local-guide-source
    ref: templates/second-brain-guide/02-build-your-harness.md
---

# 내 업무용 BoI Harness 만들기

코드나 폴더 구조를 먼저 정할 필요가 없습니다. 반복해서 수행하는 업무, 사용하는 자료, 좋은 결과의 기준을 AI에게 평소 말하듯 설명합니다.

기본 결과는 `cases/`에 새 사례를 등록하는 것이 아니라 내 Local Profile에 저장되는 **개인 Harness 카드 한 개**입니다. Case packaging과 평가 evidence는 이 Harness를 실제로 사용한 뒤 조직에 사례로 배포하겠다고 별도로 요청할 때만 진행합니다.

## 1. 이 문장으로 시작

```text
내가 하는 업무를 설명할게. 이 업무에서 좋은 지식을 만들고 BoI Wiki에 축적할 수 있도록
역할, 기존 Skill, 작업 흐름, 산출물, 검토 기준을 포함한 Harness를 구성해줘.
원본 자료는 Local Private로 유지하고, 공유는 미리보기와 내 승인 뒤에만 진행해줘.
```

## 2. AI가 확인하는 것

필요할 때만 쉬운 질문을 최대 세 개 받습니다.

1. 어떤 일을 반복하며, 완료됐다고 판단하는 기준은 무엇인가?
2. 메일·웹·문서·표·회의 메모 중 어떤 자료를 사용하는가?
3. 결과는 개인 Local에만 둘 것인가, 나중에 Team/Public 후보가 될 수 있는가?

사번, 시스템명, 실제 업무 원문이 아직 없다면 합성 예시나 빈 입력 계약으로 먼저 설계할 수 있습니다. 확인되지 않은 사실은 AI가 채워 넣지 않습니다.

## 3. 승인 전에 보는 미리보기

AI는 파일을 바꾸기 전에 다음을 사람의 언어로 요약합니다.

- 목표와 성공 조건
- 재사용할 기존 BoI Skills와 새 Skill을 만들지 않은 이유
- 작성·검토 역할과 dependency DAG
- Capture·Distill·Query·Lint·Review 흐름 및 산출물
- Local Private 유지 범위와 promotion 가능한 정제 결과

내용이 맞으면 “이 미리보기대로 진행해줘”라고 승인합니다. 범위·자료·공개 수준이 바뀌면 새 미리보기를 받아야 합니다.

## 4. 만들어져야 하는 Harness

정상 결과에는 최소한 다음이 포함됩니다.

| 영역 | 확인할 내용 |
|---|---|
| 시작 요청 | 다른 구성원도 그대로 전달할 한 문장 |
| 작업 모드 | `create`, `extend`, `audit`, `evolve`, `evaluate` 중 이번 작업에 해당하는 하나만 선택 |
| 사용 범위 | 이 Harness를 실행해야 하는 요청과 비슷하지만 다른 `near-miss` 요청의 경계 |
| 역할 | 작성자·분석자·독립 reviewer의 책임과 승인 권한 |
| Skill | 기존 범용 Skill의 선택과 조합, 중복 검사 |
| 작업 흐름 | 단계별 입력·출력·dependency DAG와 종료 조건 |
| 실행 규모 | Single-agent·Reduced·Full·No-team fallback |
| 산출물 | 입력·중간·최종·실패 결과의 계약 |
| 오류 처리 | 자료 누락·손상·접근 불가·충돌·중단 후 재개 |
| 지식 품질 | 주장·결정·제약·반증·미확인·검토 상태 |
| BoI 계약 | OKF 0.1 + BoI Profile 0.1-local |
| 공유 경계 | 정제 가능한 결과와 직접 promotion이 금지된 원본 |
| 승인 계약 | candidate·출처·reviewer·scope 변경 시 기존 승인이 무효가 되는 조건 |
| 사용 안내 | 비개발자 walkthrough와 정상 결과 |
| 개선 방식 | 실제 실패가 생겼을 때 고칠 책임 계층과 필요한 evidence |
| 다음 사용 | Local Harness 카드 경로와 그대로 복사할 재실행 요청문 |

메타데이터만 맞는 빈 문서, 원본 등록만 하고 “나중에 정제”하는 문서, 도메인마다 새 Skill을 만드는 설계는 정상 결과가 아닙니다.

검사는 표의 제목만 있는지도 함께 확인합니다. 복사 가능한 시작 요청, 측정 가능한 성공·실패 조건, 기존 Skill의 책임, 독립 reviewer의 승인 권한, 네 가지 실행 규모, 입력·중간·최종 산출물, 중단 후 재개 방법, exact candidate hash, 저장 경로와 다음 세션 요청문이 실제 내용으로 채워져야 합니다. `TODO`, `TBD`, 꺾쇠괄호로 남긴 자리표시자는 완료된 Harness로 인정하지 않습니다.

본문의 13개 구조 제목은 한국어 또는 영어로 작성할 수 있습니다. 다만 AI와 BoI Wiki가 기계적으로 읽는 frontmatter의 `okf_version`, `boi_profile_version`, `type`, `source_refs`, `generated_from` 같은 필드명과 허용값은 번역하거나 바꾸지 않습니다.

## 5. 저장하고 다음 세션에서 다시 실행

승인된 Harness는 채팅 답변으로만 끝내지 않습니다. AI가 다음 Local Private 경로에 OKF 0.1 + BoI Profile 0.1-local 문서로 보존합니다.

```text
data/boi/private/<내 Local Profile ID>/notes/harnesses/<Harness 이름>.md
```

AI는 저장 후 같은 폴더의 `index.md`에 표준 Markdown 링크를 추가합니다. Profile 홈에서 **승인된 개인 Harness**를 누르면 새로 만든 카드와 아래의 재실행 문장을 함께 찾을 수 있습니다. 승인 전 미리보기는 이 목록에 등록하지 않습니다.

이 문서에는 승인한 요청, 성공·실패 조건, 기존 Skills, 역할, DAG, 산출물, 오류 처리, 검토 권한과 Local/Remote 경계가 함께 있어야 합니다. 설계의 근거가 된 승인 요청은 별도 Local capture로 보존하고 정확한 파일 SHA256으로 연결합니다. 일반 대화 전체를 복사하지 않습니다.

다음 세션에서는 다음처럼 요청합니다.

```text
저장된 <Harness 이름> Harness로 이번 자료를 처리해줘.
먼저 필요한 입력과 변경 범위를 확인하고, 기존 역할·DAG·검토 계약을 그대로 사용해줘.
```

AI는 새 Harness를 다시 만들지 않고 저장된 카드를 찾아 실행하며, 실행만 했다는 이유로 카드를 다시 쓰지 않습니다. 계약을 바꾸고 싶을 때만 “이 Harness를 개선해줘”라고 요청합니다. AI는 현재 카드와 변경 후보의 확인값을 보여주고, 승인 뒤 이전 카드를 `_archive/harnesses/<시각>/`에 원문 그대로 보존합니다. 새 카드는 같은 Harness ID를 유지하면서 이전 파일 경로·SHA256, 승인한 변경 확인값, 변경 이유를 연결하므로 언제 무엇이 바뀌었는지 확인할 수 있습니다. 여러 구성원에게 배포할 Case로 전환하는 것은 개인 Harness 실행과 별도의 승인·비식별화·검증 단계입니다.

개인 Harness 카드는 `boi/local-guide` 형식을 쓰지만 그 카드 자체를 Team/Public으로 직접 promotion할 수는 없습니다. 개인 경로·입력·실행 설정을 제거한 별도 일반 가이드로 정제하거나, 합성·공개 fixture와 검토 evidence를 갖춘 Community Case로 패키징한 뒤 그 결과만 공유 후보로 검토합니다.

## 6. 일회성 업무와 반복 Harness 구분

- 이번 한 번만 필요한 요약·번역·문서 작성이면 Local 문서로 끝냅니다.
- 같은 입력·판단·검토가 반복되고 다른 구성원도 재사용할 수 있을 때 Harness로 만듭니다.
- 기존 Case가 거의 같다면 새 Case를 만들지 않고 기존 Case의 누락 경로나 산출물 계약을 보강합니다.

## 7. 사용 후 개선하기

실제 사용 중 막혔다면 다음처럼 요청합니다.

```text
방금 사용한 Harness에서 막힌 단계와 실제 결과를 비교해줘.
Case 방법론, orchestration, 범용 Skill, validator, runtime 중 어디의 문제인지 먼저 판정하고
가장 작은 책임 계층만 수정할 개선안을 미리보기로 보여줘.
```

한 사례의 실패만으로 범용 Skill을 바꾸지 않습니다. 같은 안정적인 동작이 세 개 이상의 독립 사례에서 반복되고 개선 evidence가 있을 때만 범용 Skill 후보로 올립니다.

## Local/Remote 경계

Harness 구성과 실행은 Local Private에서 시작합니다. MCP 조회 연결은 사내 BoI Wiki를 검색·인용하는 선택 기능이며 Local 문서를 자동 업로드하지 않습니다. 공유할 때는 정제본을 canonical 후보로 변환하고 민감정보·출처·범위·reviewer를 검토한 exact preview에 사용자가 승인해야 합니다.

이전: [제품 계층 지도](01-meta-harness-map.md) · 다음: [AI에게 Second Brain 설정 맡기기](12-ai-assisted-setup.md)
