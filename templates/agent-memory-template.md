---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-knowledge-note
title: "{{title}}"
description: "대화와 로컬 자료에서 확인한 장기 활용 지식"
tags: [LocalPrivate, SecondBrain, AgentMemory]
timestamp: {{timestamp}}
boi_id: boi:private:{{employee_id}}:memory:{{memory_key}}
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
knowledge_role: agent-memory
memory_key: "{{memory_key}}"
memory_kind: "{{memory_kind}}"
memory_status: "{{memory_status}}"
memory_operation: "{{memory_operation}}"
claim_status: "{{claim_status}}"
source_refs:
  - type: agent-session
    ref: "{{source_fingerprint}}"
    note: "원시 대화 transcript는 복사하지 않음"
---

# {{title}}

## 현재 지식

{{summary}}

## 근거와 한계

{{evidence_and_limits}}

## 변경 이력

- {{timestamp}} — {{change_summary}}
