---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-example
title: "SOP 이미지에서 BoI Wiki SOP 초안 만들기"
description: "사용자가 제공한 SOP 이미지를 근거로 BoI Wiki 형식 SOP 초안을 만드는 예제"
boi_id: boi:private:0000000:legacy:image-to-sop-draft:5c42d957fc
classification: internal
owner: "0000000"
artifact_visibility: working
lifecycle_state: working
memory_candidate: false
cleanup_policy: keep
timestamp: 2026-06-20T21:52:00+09:00
employee_id: "0000000"
local_owner_ref: local-private:0000000
visibility: local-private
local_only: true
promotion_status: local_only
retention_class: record
retention_until: ""
archive_status: active
review_after: 2026-09-20
contains_sensitive: no
source_refs:
  - type: image
    ref: evidence/sop_sample_image.png
  - type: generated-output
    ref: ../../sop-drafts/direct-development-reporting-sop-draft.md
---

# Prompt

```text
이 SOP 이미지를 BoI Wiki 형식으로 초안 만들어줘.
이미지 파일명은 sop_sample_image.png로 남기고, 원본 이미지와 생성된 SOP 초안의 근거 관계를 문서에 표시해줘.
```

# Generated Output

- 원본 이미지: ![SOP sample image](evidence/sop_sample_image.png)
- 생성 문서: [direct-development-reporting-sop-draft.md](../../sop-drafts/direct-development-reporting-sop-draft.md)
- 생성 내용: stage, system, actor, TAT before/after, manual handoff, candidate action gap을 BoI SOP 초안으로 구조화했다.

# Evidence

- Source image SHA-256: `002cd35720977227fde31bb523d0a34a0039665e6e891e8ecad7dc907fd1b462`
- 이미지에서 확인한 제목: `직개발 결과 확인 및 Reporting`
- 이미지에서 확인한 TAT 절감: `7.3h`, `16.5h -> 9.2h`

# How to Verify

1. 이미지와 SOP 초안의 stage 번호가 일치하는지 확인한다.
2. 품질 시스템, Map 분석 시스템, 단면 검사 시스템, 메신저는 실제 시스템 호출이 아니라 `SIMULATED` simulator action으로 표시됐는지 확인한다.
3. Public 공유는 [Public Promotion](promotion-public.md) 예제처럼 승인 전 draft/preflight까지만 진행한다.

# Real vs Simulated

원본 PNG와 SOP 초안은 실제 local output이다. 이미지 해석 결과 중 사내 시스템 연결은 실제 호출하지 않고, shared BoI Wiki에서는 `BoI Universal Action Simulator Flow` 기반 `SIMULATED` evidence로 검증한다.
