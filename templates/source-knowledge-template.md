---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-knowledge-note
title: "{{title}}"
description: "읽을 수 있는 이메일·웹·Markdown·텍스트·표·PDF·이미지에서 즉시 재사용할 수 있도록 정제한 Local Private 지식"
tags: [LocalPrivate, SecondBrain, SourceKnowledge]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:source-knowledge:{{source_id}}
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
memory_candidate: true
cleanup_policy: keep
review_after: {{review_after}}
contains_sensitive: unknown
claim_status: "{{claim_status}}"
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

## 재사용할 지식

{{reusable_knowledge}}

## 결정·제약·지침

{{decisions_constraints_and_instructions}}

## 근거와 반증

{{evidence_and_counterevidence}}

## 불확실성과 다음 확인

{{unknowns_and_next_validation}}

## 검토와 공유 경계

{{review_state_and_local_remote_boundary}}
