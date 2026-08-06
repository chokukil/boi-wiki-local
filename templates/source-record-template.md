---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-note
title: "{{title}}"
description: "읽을 수 없거나 격리가 필요한 원본의 Local Private 정보 문서"
tags: [LocalPrivate, SecondBrain, SourceRecord]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:source:{{source_id}}
visibility: local-private
classification: internal
owner: "{{employee_id}}"
employee_id: "{{employee_id}}"
local_owner_ref: local-private:{{employee_id}}
local_only: true
promotion_status: local_only
retention_class: source
retention_until: ""
archive_status: active
artifact_visibility: background
lifecycle_state: protected
memory_candidate: true
cleanup_policy: keep
review_after: {{review_after}}
contains_sensitive: unknown
knowledge_role: source-record
evidence_id: "{{source_id}}"
evidence_type: "{{source_type}}"
evidence_sha256: "{{source_sha256}}"
original_filename: "{{original_filename}}"
origin_ref: "{{origin_ref}}"
raw_path: "{{local_copy_path}}"
intake_method: agent-source-folder
source_refs:
  - type: local-file
    ref: "{{local_copy_path}}"
    sha256: "{{source_sha256}}"
generated_from:
  - type: local-file
    ref: "{{local_copy_path}}"
    sha256: "{{source_sha256}}"
---

# {{title}}

원본 파일은 변경하지 않습니다. 이 문서는 현재 에이전트가 신뢰성 있게 읽을 수 없는 바이너리, 지원하지 않는 형식, 저신뢰·불완전 렌더링 또는 검토 전 격리가 필요한 파일의 출처와 SHA256만 기록합니다. 승인 후 실제로 내용을 확인할 수 있는 이메일·웹·Markdown·텍스트·표·PDF·이미지에는 이 템플릿을 쓰지 않고 `source-knowledge-template.md`로 같은 작업 안에서 재사용 가능한 지식 한 문서를 만듭니다.
