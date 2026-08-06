---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-knowledge
title: "Sensitive source review"
description: "SYN-SB-001 adaptive batch 4 sanitized Local Private review"
tags: [Synthetic, SecondBrainEval, ReviewRequired, Sensitive]
boi_id: boi:private:0000000:eval:sensitive-source-review
visibility: local-private
classification: restricted
owner: "0000000"
employee_id: "0000000"
local_owner_ref: local-private:0000000
local_only: true
promotion_status: local_only
artifact_visibility: memory
lifecycle_state: review-required
archive_status: active
review_after: 2026-08-09
contains_sensitive: true
knowledge_role: review-required
claim_status: sensitive-review
remote_projection_allowed: false
remote_submit_allowed: false
source_refs:
  - type: synthetic-fixture
    ref: sources/18-sensitive-review-note.md
    sha256: de7331ebf1fe35797eb840e958f20ce168a886eba6595dbca1a4d1638891dc98
generated_from:
  - type: synthetic-fixture
    ref: sources/18-sensitive-review-note.md
    sha256: de7331ebf1fe35797eb840e958f20ce168a886eba6595dbca1a4d1638891dc98
---

# Sensitive source review

The source contains a synthetic personal-identifier token and a Local Private filesystem path. Their literal values are intentionally omitted from this derived record.

Keep this item in Local Private review-required state. It is excluded from every remote projection and is not eligible for remote submission.
