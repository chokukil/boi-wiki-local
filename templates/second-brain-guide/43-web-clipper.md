---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "Obsidian Web Clipper로 웹 자료 수집"
description: "공식 브라우저 확장을 선택 설치해 웹 자료를 공통 원본 폴더의 web-clip 유형으로 저장하는 방법"
tags: [LocalPrivate, SecondBrain, Guide, Obsidian, WebClipper]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:guide:web-clipper
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
guide_audience: "공개 웹 자료를 Local Second Brain에 모으는 사용자"
guide_duration_minutes: 10
guide_prerequisites: "지원 브라우저, Obsidian Vault, 사용자 설치 승인"
guide_execution: "공식 확장을 수동 설치하고 기존 공통 원본 폴더에 저장한 뒤 지식 후보 미리보기를 확인한다"
guide_success: "URL과 수집일이 있는 Markdown을 Local evidence로 검토했다"
guide_failure_page: "60-troubleshooting.md"
guide_next_page: "42-omnisearch.md"
guide_boundary: "optional-obsidian-local"
source_refs:
  - type: official-doc
    ref: https://obsidian.md/help/web-clipper
  - type: source-repository
    ref: https://github.com/obsidianmd/obsidian-clipper
---

# Obsidian Web Clipper로 웹 자료 수집

공식 Web Clipper는 웹 페이지와 하이라이트를 Local Markdown으로 저장하는 선택형 브라우저 확장입니다. 자동 크롤러가 아니며, 설치·사이트 접근·저장은 사용자가 직접 실행합니다. Obsidian이 없어도 페이지를 Markdown으로 저장해 자료 폴더에 넣고 AI에게 같은 정리 여정을 요청할 수 있습니다.

## 설치와 최소 설정

Web Clipper 브라우저 확장 설치·사이트 권한과 QuickAdd 설치는 서로 다른 변경 미리보기와 승인 단위입니다. 다음 요청은 공식 확장 설치 방식, 사이트 권한, 공통 원본 폴더와 import할 템플릿 SHA256을 보여줄 뿐 설치하지 않습니다.

```text
Web Clipper 설치 preview를 보여줘.
브라우저 확장 권한, 내가 승인한 공통 원본 자료 폴더,
import할 템플릿 SHA256과 복구 방법을 QuickAdd와 분리해서 보여줘.
```

현재 `BoI Common Raw Source` 템플릿 SHA256은 `0523e566ca0e0b2ec29388049a33c2a7fa4bc6937ddba61ea4513f774d44ea4d`입니다. 템플릿이 바뀌면 기존 승인을 재사용하지 않습니다.

1. [Obsidian 공식 Web Clipper 안내](https://obsidian.md/help/web-clipper)에서 현재 브라우저의 공식 스토어 링크를 엽니다.
2. 확장 권한과 사이트 접근 범위를 확인하고 사용자가 직접 설치를 승인합니다.
3. 기본 저장 위치를 Second Brain 설정에서 이미 승인한 공통 원본 자료 폴더로 지정합니다. `web-clips/` 전용 폴더를 만들거나 기존 파일을 이동하지 않습니다.
4. 제공되는 `BoI Common Raw Source` 템플릿을 import하고 `source_kind: web-clip`, URL, 제목, 작성자·사이트, 게시일, 수집 시각과 본문을 확인합니다.
5. Interpreter 같은 추가 처리 기능은 사내 정책과 데이터 경계를 별도로 확인하기 전에는 사용하지 않습니다.

템플릿의 저장 위치가 빈 값이면 사용자가 이미 선택한 공통 원본 폴더를 Vault 기준 경로로 지정합니다. 해당 폴더가 현재 Vault에서 접근되지 않으면 다른 위치로 조용히 저장하지 말고, 공통 폴더를 포함하는 Vault를 선택하거나 Second Brain 폴더 설정 변경안을 먼저 확인합니다.

```text
Web Clipper로 저장한 자료를 새 AI 세션이 시작될 때 자동으로 확인해줘.
원문은 변경하지 말고, 새 자료만 OKF + BoI Profile 지식 후보와 review queue로 정리해.
승인 전에는 현재 지식이나 원격 Wiki에 반영하지 마.
```

이 요청은 Web Clipper 전용 설정을 만들지 않고, 기존 공통 원본 폴더와 세션 시작 확인 설정을 그대로 사용합니다.

## BoI intake로 넘기기

클립 파일은 아직 승인 지식이 아닙니다. 다른 원본과 같은 방식으로 경로·크기·수정 시각을 확인하고 SHA256으로 신규·중복을 판정합니다. 폴더 이름이 아니라 `source_kind: web-clip`과 URL·수집 시각으로 유형을 구분합니다.

```text
방금 저장한 웹 클립만 처리해줘.
같은 SHA256으로 이미 반영된 자료는 건너뛰고 원문은 변경하지 마.
```

저장된 본문이 원 페이지 전체와 다를 수 있으므로 제목·URL·날짜와 핵심 문단을 사람이 대조합니다. 로그인 페이지, 사내 전용 페이지, 실제 업무 원문은 공개 출처처럼 취급하지 않습니다.

상태만 확인하려면 다음처럼 요청합니다.

```text
지난 세션 이후 Web Clipper로 새로 저장된 자료와
처리 대기·실패·검토 항목을 보여줘.
```

## 정상 결과와 경계

원본 클립은 bytes·이름·위치가 그대로 남고, 새 unique SHA256 하나가 OKF 0.1 + BoI Profile 0.1-local 지식 후보 하나와 review queue 항목 하나로 정리되면 정상입니다. 후보에는 `source_refs`, `generated_from`, 근거, 반대 근거, unknown과 Local/Remote 경계가 있어야 합니다. 같은 SHA256이면 새 문서·review 항목·revision을 만들지 않습니다.

Web Clipper 설치만으로 MCP 조회나 Team/Public 등록은 일어나지 않습니다. AI가 실행되지 않을 때는 폴더를 감시하거나 처리하지 않습니다. 후보는 승인 전 현재 지식 revision을 증가시키지 않으며, 새 자료가 없으면 `no-change`로 끝나고 보고서를 만들지 않습니다. 확장을 제거해도 Markdown 원문은 남습니다.

이전: [QuickAdd](41-quickadd.md) · 다음: [Omnisearch 도입 판단](42-omnisearch.md)
