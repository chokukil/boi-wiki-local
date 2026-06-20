---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-workflow-simulation
title: "Local Only Runbook"
description: "MCP나 원격 publish 없이 Local Private만 사용하는 실행 기준"
timestamp: 2026-06-20T22:08:00+09:00
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
  - type: local-example
    ref: ../usage-examples/natural-language-poc/local-only-mode.md
---

# Rules

- Use only files under `data/boi/private/{employee_id}/`.
- Do not call remote MCP, remote publish, or Action Gateway invoke.
- Keep source material under local evidence paths.
- When remote context is required, ask the user to provide a link or pasted source.

# Verification

Run `sh check.sh` when possible. If tools are unavailable, manually confirm `employee_id`, `local_owner_ref`, `visibility`, `local_only`, and index updates.
