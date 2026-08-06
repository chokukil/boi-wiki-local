---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-note
title: "SYNTHETIC read-only API note source record"
description: "읽기 전용 지식 검색 API의 목적과 금지 조건을 보존한 Local Private 정보 문서"
tags: [LocalPrivate, SecondBrain, SourceRecord, API]
timestamp: 2026-08-02
boi_id: boi:private:0000000:source:14-readonly-api-note-97e7d613
visibility: local-private
classification: internal
owner: "0000000"
employee_id: "0000000"
local_owner_ref: local-private:0000000
local_only: true
promotion_status: local_only
retention_class: source
retention_until: ""
archive_status: active
artifact_visibility: background
lifecycle_state: protected
memory_candidate: true
cleanup_policy: keep
review_after: 2026-08-09
contains_sensitive: false
knowledge_role: source-record
claim_status: observed
evidence_id: "14-readonly-api-note-97e7d613"
evidence_type: "document"
evidence_sha256: "97e7d613c9254f6412c08793670ae7a792f3e56f583ca69119a1e7d6c4562006"
original_filename: "14-readonly-api-note.md"
origin_ref: "sources/14-readonly-api-note.md"
raw_path: "sources/14-readonly-api-note.md"
intake_method: agent-source-folder
source_refs:
  - type: local-file
    ref: "sources/14-readonly-api-note.md"
    sha256: "97e7d613c9254f6412c08793670ae7a792f3e56f583ca69119a1e7d6c4562006"
generated_from:
  - type: local-file
    ref: "sources/14-readonly-api-note.md"
    sha256: "97e7d613c9254f6412c08793670ae7a792f3e56f583ca69119a1e7d6c4562006"
---

# SYNTHETIC API note

## 인터페이스

- 엔드포인트: GET /knowledge/search
- 목적: ACL로 볼 수 있는 canonical knowledge를 읽기 전용으로 조회한다.
- 변경 기능: 없음.
- 필요한 인용 정보: canonical BoI ID, revision, visibility.

## 금지 조건

- 이 메모만으로 쓰기 엔드포인트가 있다고 추론하지 않는다.
- 조회문에 Local 경로를 업로드하지 않는다.

이 정보 문서는 원본 API 메모를 변경하지 않고 읽기 전용 경계를 보존한다. 원격 쓰기나 Local Private 자료 전송 권한을 부여하지 않는다.
