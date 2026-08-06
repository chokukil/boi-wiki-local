# Harness design result template

Use this structure for a completed Harness design. Replace every placeholder with concrete content or `not applicable` plus a reason. Do not create empty wrapper pages.

For an approved personal Harness, save this body inside the following Local Profile envelope. Compute the capture file SHA256 mechanically and replace every placeholder; do not leave the example values in a completed card.

```yaml
---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-guide
title: "<Harness name>"
description: "<recurring work and reusable result>"
tags: [LocalPrivate, MetaHarness, ConfiguredHarness]
timestamp: <ISO-8601 timestamp>
boi_id: boi:private:<employee-id>:harness:<slug>
visibility: local-private
classification: internal
owner: "<employee-id>"
employee_id: "<employee-id>"
local_owner_ref: local-private:<employee-id>
local_only: true
promotion_status: local_only
retention_class: working
archive_status: active
artifact_visibility: working
lifecycle_state: working
memory_candidate: true
cleanup_policy: keep
review_after: <YYYY-MM-DD>
contains_sensitive: unknown
source_refs:
  - type: local-document
    ref: <approved-request-capture-path>
    sha256: <exact-capture-file-sha256>
generated_from:
  - type: local-document
    ref: <approved-request-capture-path>
    sha256: <exact-capture-file-sha256>
---
```

## 1. 사용자 요청과 결과 (User request and outcome)

- Copyable one-sentence request:
- Target user and recurring work:
- Reusable result:
- Measurable success:
- Failure conditions and exclusions:

## 2. 감사와 변경 미리보기 (Audit and change preview)

- Mode: `create | extend | audit | evolve | evaluate`
- Existing Harness, Case, and Skills inspected:
- Nearest reusable Case and duplication decision:
- Files or contracts to change:
- User content and evidence to preserve:
- External checks that remain pending:
- Approval state:

## 3. 지식 흐름 (Knowledge flow)

Describe the work-specific meaning of each stage.

```text
Capture → Distill → Query → Lint → Review
```

- Capture and source integrity:
- Distilled reusable knowledge:
- Questions the Harness must answer with sources:
- Contradiction, staleness, unsupported-claim, and schema lint:
- Human review and review cadence:

## 4. 재사용 Skills와 책임 (Reused Skills and ownership)

| Capability | Existing Skill or Case | Reuse or extension | Why this layer owns it |
|---|---|---|---|
|  |  |  |  |

New generic Skill proposal: `none` by default. A proposal requires the same stable need in at least three independent Cases plus reusable improvement evidence.

## 5. 역할과 독립 검토 (Roles and independent review)

| Role | Responsibility | Inputs | Outputs | Exit or hard-fail condition |
|---|---|---|---|---|
|  |  |  |  |  |

- Reviewer authority:
- How reviewer independence is preserved in Single-agent mode:

## 6. 의존 DAG와 인계 (Dependency DAG and handoffs)

Provide a small Mermaid or text DAG, then state:

- phase exits;
- required handoff fields and source hashes;
- retry, skip, block, and resume behavior;
- handling of missing or contradictory evidence.

## 7. 실행 규모 (Scale modes)

| Mode | Role projection | Review separation | Output contract changes |
|---|---|---|---|
| Single-agent |  |  | none |
| Reduced |  |  | none |
| Full |  |  | none |
| No-team fallback |  |  | none |

## 8. 산출물 계약 (Artifact contracts)

| Stage | Required artifact | Required fields or sections | Validation | Failure artifact |
|---|---|---|---|---|
| Input |  |  |  |  |
| Intermediate |  |  |  |  |
| Final Local |  |  |  |  |

Readable source material must become reusable knowledge in the same work when possible. Preserve claims, decisions, constraints, uncertainty, counter-evidence, source references, and review state in the body as well as metadata.

## 9. 오류, 대안과 재개 (Error, fallback, and resume)

- Missing input:
- Damaged or unsupported input:
- Ambiguous request:
- Access denied or unavailable external system:
- Interrupted run and resume marker:
- Conflicting evidence and review-required path:

## 10. OKF, BoI와 Local/Remote 경계 (OKF, BoI, and Local/Remote boundary)

- Local output contract: `OKF 0.1 + BoI Profile 0.1-local`
- Local Private source and intermediate artifacts:
- Directly blocked promotion types:
- Distilled types eligible for promotion preview:
- Sanitization rules for Local paths, IDs, raw source, and sensitive content:
- MCP read behavior and why it never implies upload:
- Target visibility, reviewer, structured remote-safe sources, blockers, and exact candidate hash:
- User approval and approval invalidation conditions:

## 11. 비개발자 사용 순서 (Non-developer walkthrough)

1. Natural-language start request:
2. At most three plain-language questions:
3. Change preview shown before mutation:
4. Local execution without Python, Obsidian, MCP, or team features:
5. Local Harness card path under `data/boi/private/<employee-id>/notes/harnesses/`:
6. Copyable next-session request that loads the card without rebuilding it:
7. Result, search, correction, and resume examples:
8. Optional promotion preview and explicit approval boundary:
9. Troubleshooting next step:

## 12. 검증과 상태 (Validation and status)

- trigger and near-miss boundary:
- source and hash integrity:
- output contract and failure-path checks:
- OKF and BoI lint:
- Local/Remote and security checks:
- independent review evidence:
- runtime, user, and actual BoI Wiki evidence:
- current status and claims that remain prohibited:

## 13. 개선 이력 (Evolution record)

- Previous Harness version: `none (initial creation)` or `_archive/harnesses/<timestamp>/<slug>.md` plus its exact SHA256
- Approved change preview: exact preview SHA256 and approval state
- Change reason and user approval: initial approved design or the concrete defect and explicit approval
- Feedback or failure:
- Smallest owning layer: `Case method | orchestration | generic Skill | fixture or prompt | validator | runtime`
- Preserved failure evidence:
- Minimal change and affected regression:
- Evidence needed before promoting behavior into a generic Skill:
- Next review owner and date:
