---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-knowledge
title: "Synthetic knowledge review schedule"
description: "SYN-SB-001-v1 evaluation seed"
tags: [Synthetic, SecondBrainEval]
boi_id: boi:private:0000000:eval:review-schedule
visibility: local-private
classification: internal
owner: "0000000"
employee_id: "0000000"
local_owner_ref: local-private:0000000
local_only: true
promotion_status: local_only
artifact_visibility: memory
lifecycle_state: memory
archive_status: active
review_after: 2026-08-09
contains_sensitive: false
knowledge_role: reviewed-knowledge
claim_status: direct
source_refs:
  - type: synthetic-fixture
    ref: sources/01-decision-chat.txt
    sha256: 5be16cc0e29d799b9ed63670979e18a88ae2c849beb55d3dbb59bac09b216463
  - type: local-file
    ref: sources/02-project-update.eml
    sha256: b1f652f17ac06c5fcb45cb489ed887ff92af7187e480618c6d6029bd1bf6165c
  - type: local-file
    ref: sources/10-review-day-reconfirmation.txt
    sha256: 99c99d87357b5a76b2212bc184606877878eb5ce37b77dd600b474f64317c1c0
  - type: local-file
    ref: sources/05-operating-guide.pdf
    sha256: 6b2b928c844f99b1d8eddc01384ef9cc59429f171ab3810ff14e1d2a2b35dc92
  - type: local-file
    ref: sources/07-meeting-note.md
    sha256: aa91ab6bcedec80ea716e17a4b90c6b97d5cf18c54cd1b9966042604d14daf61
generated_from:
  - type: synthetic-fixture
    ref: sources/01-decision-chat.txt
    sha256: 5be16cc0e29d799b9ed63670979e18a88ae2c849beb55d3dbb59bac09b216463
  - type: local-file
    ref: sources/02-project-update.eml
    sha256: b1f652f17ac06c5fcb45cb489ed887ff92af7187e480618c6d6029bd1bf6165c
  - type: local-file
    ref: sources/10-review-day-reconfirmation.txt
    sha256: 99c99d87357b5a76b2212bc184606877878eb5ce37b77dd600b474f64317c1c0
  - type: local-file
    ref: sources/05-operating-guide.pdf
    sha256: 6b2b928c844f99b1d8eddc01384ef9cc59429f171ab3810ff14e1d2a2b35dc92
  - type: local-file
    ref: sources/07-meeting-note.md
    sha256: aa91ab6bcedec80ea716e17a4b90c6b97d5cf18c54cd1b9966042604d14daf61
---

# Synthetic knowledge review schedule

Reviewed decision: knowledge review occurs every Friday at 15:00.

## Evidence history

- 2026-08-02 — The project update email reconfirmed Friday at 15:00 and identified the referenced checklist as missing evidence.
- 2026-08-02 — The project owner explicitly reconfirmed Friday at 15:00.
- 2026-08-02 — The operating guide and meeting note independently reconfirmed Friday at 15:00.
