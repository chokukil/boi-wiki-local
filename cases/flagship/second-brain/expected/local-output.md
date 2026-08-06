---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-knowledge
title: "합성 지식 검토 운영 방식"
description: "SYN-SB-001-v1에서 정제한 검토 일정·용어·충돌 처리 지식"
tags: [Synthetic, CaseHarness, LocalPrivate]
boi_id: boi:private:0000000:case:second-brain:expected
visibility: local-private
classification: internal
owner: "0000000"
employee_id: "0000000"
local_owner_ref: local-private:0000000
local_only: true
promotion_status: local_only
artifact_visibility: working
lifecycle_state: working
archive_status: active
review_after: 2027-02-01
contains_sensitive: false
source_refs:
  - type: synthetic-fixture
    ref: ../fixtures/sources/01-decision-chat.txt
    sha256: 5be16cc0e29d799b9ed63670979e18a88ae2c849beb55d3dbb59bac09b216463
  - type: synthetic-email
    ref: ../fixtures/sources/02-project-update.eml
    sha256: b1f652f17ac06c5fcb45cb489ed887ff92af7187e480618c6d6029bd1bf6165c
---

# 합성 지식 검토 운영 방식

이 문서는 raw 대화나 메일 복사본이 아니라 두 Local source에서 정제한 재사용 가능한 knowledge 예시입니다.

## 관찰

- reviewed 검토 일정은 Friday 15:00이다.
- preferred term 후보는 Atlas Ledger이며 Blue Ledger는 alias로 보존한다.

## 지지 근거와 반증

- 대화 결정과 project update email이 Friday 일정을 지지한다.
- 출처 없는 Thursday 메모는 충돌이며 reviewed 결정을 덮어쓰지 않는다.

## 미확인과 실패 경로

- Email이 언급한 checklist는 fixture에 없다. 내용과 승인 상태는 미확인이다.
- Dictionary owner의 Atlas Ledger 검토가 남아 있다.

## 사람의 판단과 reviewer 판정

- Friday 일정을 active knowledge로 유지한다.
- Thursday claim과 alias 검토는 review queue에서 사람이 판정한다.
- 다음 검증은 missing checklist intake와 dictionary owner review다.

## Local/Remote 경계

- 이 파일은 Local Private다.
- Team 후보에는 재사용 가능한 검토 방법만 포함하고 raw chat, email, Local path와 식별자는 제외한다.
- canonical preview와 새 사용자 승인이 없으면 원격 등록하지 않는다.
