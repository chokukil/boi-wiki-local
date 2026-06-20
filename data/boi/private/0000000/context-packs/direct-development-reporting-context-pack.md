---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-context-pack
title: "직개발 Reporting PoC Context Pack"
description: "SOP 이미지 기반 직개발 Reporting PoC를 수행하는 agent용 context pack"
timestamp: 2026-06-20T22:06:00+09:00
employee_id: "0000000"
local_owner_ref: local-private:0000000
visibility: local-private
local_only: true
promotion_status: local_only
retention_class: working
retention_until: ""
archive_status: active
review_after: 2026-07-20
contains_sensitive: no
source_refs:
  - type: local-sop
    ref: ../sop-drafts/direct-development-reporting-sop-draft.md
  - type: local-event-plan
    ref: ../event-drafts/direct-development-reporting-event-to-action-plan.md
---

# Mission

SOP 이미지에서 직개발 결과 확인 및 Reporting workflow를 만들고, BoI Wiki Local 산출물과 shared runtime evidence를 연결한다.

# Required Local Sources

- [SOP image evidence](../usage-examples/natural-language-poc/evidence/sop_sample_image.png)
- [SOP draft](../sop-drafts/direct-development-reporting-sop-draft.md)
- [Mermaid flow](../diagrams/direct-development-reporting-mermaid.md)
- [Event to Action plan](../event-drafts/direct-development-reporting-event-to-action-plan.md)
- [Action draft](../action-drafts/quality-system-response-trend-action-draft.md)

# Remote Sources When MCP Is Available

| BoI | Purpose |
|---|---|
| `boi:public:sop:equipment-abnormal-response` | live SOP workflow pattern |
| `boi:public:actions:langflow:stage-analysis` | Langflow action pattern |
| `boi:public:boi-wiki-manual:actions:multi-action-connector-guide` | connector classification |
| `boi:public:boi-wiki-manual:local-private:promotion-flow` | promotion approval boundary |

# Working Rules

- Do not publish Local Private originals.
- Mark unavailable systems as gaps, not as completed actions.
- Preserve source image evidence and cite it in every derived SOP/action document.
- Stop at manual_required when a human must decide.
