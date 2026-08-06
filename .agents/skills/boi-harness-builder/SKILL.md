---
name: boi-harness-builder
description: Build or audit a reusable BoI Wiki Local Harness from a user's work description. Use when a user wants roles, existing Skill composition, orchestration, output contracts, review criteria, a reusable Case, or a safe Local-to-BoI promotion flow. Do not use for ordinary one-off document authoring or merely running an existing Case.
---

# BoI Harness Builder — Meta Harness Core

Turn a user's work description into a reusable way to create high-quality, BoI-compatible knowledge. This is the Meta Harness corresponding to the product core. The `cases/` directory is the example collection it produces; it is not the Meta Harness itself.

The Flagship Second Brain is a cross-cutting capability that can add durable capture, maintenance, query, and reuse to a Harness. It does not replace this builder or the business Case.

## Required inputs

Obtain only what is necessary:

- the work the user performs and the result they want;
- target users and a concrete success condition;
- available source material and important exclusions;
- the Local/Remote boundary and whether any result may become Team/Public knowledge;
- constraints such as missing access, required reviewer, or single-agent-only execution.

If required information is missing, ask at most three plain-language questions. Do not start with schema, DAG, hook, manifest, or evaluator terminology.

## Before work

1. Read `boi-wiki-local`, the pinned HarnessPackage, and the root bootstrap.
2. Read `references/factory-workflow.md` and `references/harness-design-template.md`.
3. Read `references/architecture-selection.md` when selecting roles or orchestration.
4. Audit the active Profile's saved Harness cards, existing generic Skills, the Case catalog, and the nearest similar Case.
5. Read `references/trigger-evolution.md` when classifying feedback or changing triggers.
6. Read `references/case-contract.md` and `quality-gates.md` only when the user explicitly asks to package a Community Case, evaluate a Case, or make a Verified/Reference status claim. They are not prerequisites for creating or running a personal Local Harness.
7. Preserve existing user changes and show the intended change surface before mutation.

## Factory lifecycle (Phase 0–7)

### Phase 0 — Audit

Select `create`, `extend`, `audit`, `evolve`, or `evaluate`. Inspect the pinned HarnessPackage, existing generic Skills, active Case catalog, nearest similar Case, dirty worktree, and available evidence. Record what will change, what must be preserved, and which external gates cannot run.

Show that change surface as a plain-language preview before creating or editing a Harness. Apply only after the user approves the preview. Exit only when ownership is clear. If an existing Case owns the outcome, extend it instead of duplicating it.

### Phase 1 — Frame the reusable outcome

Define the target user, recurring job, one-sentence natural-language request, real inputs, exclusions, reusable result, measurable success condition, and failure conditions.

If the outcome is one-off or cannot be evaluated, keep it as a Local document instead of creating a Case Harness.

### Phase 2 — Reuse Skills and design the knowledge flow

Search the shipped generic BoI Skills and existing Cases first. **Reuse existing generic Skills** before proposing any new capability.

- Specify how `Capture → Distill → Query → Lint → Review` applies to this work.
- Reuse or compose existing Skills whenever they own the operation.
- Extend the nearest Case when it owns the outcome but lacks a branch or failure path.
- Keep domain terminology, method, fixtures, and examples inside the Case.
- Do not create a domain Skill for one example.
- Propose a new generic Skill only after the same stable operation appears in at least three independent Cases and evidence shows reusable improvement.

## Existing Skill routing

Choose the smallest owner set below. `boi-wiki-local` is the parent document and promotion contract for every composing Skill; do not list it as a substitute for the content owner. Compose multiple Skills only when one Skill's declared output is a dependency of the next DAG node.

| User intent or required capability | Primary owner | Close near-miss and correct owner |
|---|---|---|
| Create, validate, review, archive, or preview promotion of a Local BoI document | `boi-wiki-local` | Designing a reusable multi-stage work pattern → `boi-harness-builder` |
| Retain durable conversation knowledge, curate a source folder, correct memory, grounded query, or long-term review | `boi-second-brain` | Produce one immediate BoI document without retention → the matching authoring Skill |
| Turn API, webhook, MCP, manual, broker, or Langflow endpoint material into an Action draft | `boi-action-author` | Decide what happens after an event → `boi-event-workflow-planner` |
| Collect bounded BoI, SOP, Event, Action, trace, and source context for another task | `boi-context-pack-builder` | Maintain the material as long-term personal knowledge → `boi-second-brain` |
| Define or curate terms, aliases, acronyms, or ontology mappings | `boi-dictionary-author` | Explain a term only inside a one-off document → the document's owning Skill |
| Plan event trigger, SOP stages, actions, approvals, and generated records | `boi-event-workflow-planner` | Dry-run one payload through an existing plan → `boi-workflow-simulator` |
| Plan a Langflow-specific connection to BoI components | `boi-langflow-connector-planner` | Specify a plain API or manual Action → `boi-action-author` |
| Visualize an SOP or process as source-mapped Mermaid | `boi-sop-flow-visualizer` | Author or revise the SOP content itself → `boi-wiki-local` |
| Safely dry-run an event payload without live actions | `boi-workflow-simulator` | Start a real workflow or invoke an action → outside Local simulation; require supported remote capability and explicit approval |

Use `boi-harness-builder` itself only when the user wants this reusable composition, roles, DAG, output contracts, review, or evolution. Merely running an existing Case or producing one document is a near-miss. Connect `boi-second-brain` only when the user needs durable topics, future retrieval, correction history, review cadence, or later promotion candidates.

### Phase 3 — Select roles and execution architecture

Choose only the logical roles needed for expertise, context isolation, and independent review. Define the dependency DAG, hash-bound handoffs, phase exits, retry/skip/block behavior, and reviewer authority. Missing evidence remains unknown.

The same output contract must work in:

- **Single-agent:** separated role passes and a fresh source-first review pass;
- **Reduced:** one creator and one independent reviewer;
- **Full:** independent logical roles following the DAG;
- **No-team fallback:** the same files and handoffs without agent-team features.

### Phase 4 — Design Local work and promotion contracts

Keep work Local Private by default.

```text
source material
→ Capture and Local intermediate evidence
→ Distill into reusable knowledge
→ Query · Lint · Review
→ OKF 0.1 + BoI Profile 0.1-local validation
→ optional sanitized canonical promotion preview
→ user approval
```

Define the input, intermediate, final, and failure output contracts. State which outputs may become knowledge, context pack, SOP, guide, dictionary, action, or workflow candidates. Raw evidence, captures, agent memory, hypotheses, and analysis logs are not directly promotable.

MCP read access never implies Local upload. Remote owner, ACL, revision, BoI ID, reviewer, and target scope remain the target BoI Wiki's responsibility.

Every promotion candidate must expose target visibility, reviewer, structured remote-safe sources, blockers, and the exact candidate hash. Candidate or scope changes invalidate the approval and require a new preview.

### Phase 5 — Build the Harness and user guide

Produce the minimum output contract below using `references/harness-design-template.md`. When a reusable example is in scope, follow `boi-local-case-harness/v1` and `references/case-contract.md`.

Keep AGENTS.md and CLAUDE.md thin. Load detailed role cards and domain references only when the current DAG node needs them. The walkthrough must work for a non-developer without Python, Obsidian, MCP, or team-agent features.

Connect Second Brain only when durable topics, reuse questions, review cadence, and promotion candidates are clear. Never force it into basic Case execution.

#### Persist and activate a configured Local Harness

A design shown only in chat is not a reusable Harness. After the user approves the exact design preview, save the configured personal Harness as one substantive `boi/local-guide` Profile page under:

```text
data/boi/private/<employee-id>/notes/harnesses/<slug>.md
```

The page must instantiate the full Local OKF 0.1 + BoI Profile 0.1-local contract and contain the concrete request, success and failure conditions, reused Skills, roles, DAG, scale modes, artifact contracts, fallbacks, review authority, Local/Remote boundary, execution examples, and evolution owner. It is a configured Local Harness card, not a new global Skill, Case manifest, background service, or new OKF type.

After saving the approved card, preserve the existing `notes/harnesses/index.md` content and add one standard Markdown link under its saved-Harness section. The link text must use the human-readable Harness name and the target must be the card filename with the `.md` extension. Do not replace the index with a generated inventory, and do not list an unapproved preview as active.

If the approved work description exists only in the conversation and is material to the design, preserve that exact approved description as a Local Private `boi/local-capture` first and derive the Harness card from that concrete file with structured `source_refs` and `generated_from` plus its exact SHA256. Do not use an unhashed pseudo-source or copy unrelated raw conversation text.

On a later request such as “저장된 `<name>` Harness로 이번 자료를 처리해줘”, search the active Profile's `notes/harnesses/` directory, load the matching card, validate its declared inputs and source hashes, and execute the same DAG and output contract. Merely running the card does not invoke this builder and must not rewrite the card.

Use `audit` or `evolve` only when the user asks to change it or runtime evidence shows a contract defect. First show a change preview bound to the current card SHA256 and proposed card SHA256. After explicit approval, copy the current card byte-for-byte to `_archive/harnesses/<timestamp>/<slug>.md`, keep the same logical `boi_id`, and update the active card instead of creating a duplicate. Preserve all original source provenance and add a structured `generated_from` entry for the archived previous card with its exact SHA256. The new Evolution record must identify the previous card path and hash, approved change preview hash, change reason and approval state, smallest owning layer, preserved failure evidence, and affected regression. If any hash or approved scope changes, stop and request a new preview.

Packaging a successful personal Harness as a Community Case is a separate, explicit step. Remove personal inputs, replace them with synthetic or public fixtures, run the Case gates, and require the user's approval before adding it to `cases/`.

The configured card itself is directly non-promotable even though it uses `boi/local-guide`. It contains personal execution configuration and provenance. To share the method, create a separate generic guide stripped of Local paths, personal inputs, and runtime configuration, or package a reviewed Community Case. Only that separately reviewed artifact may enter the normal canonical promotion preview.

### Phase 6 — Validate OKF, BoI, security, and quality

Before reporting success, validate:

- the one-sentence request triggers this Harness and not a near-miss;
- roles, DAG, handoffs, scale modes, and output contracts agree;
- generated Profile pages use OKF 0.1 + BoI Profile 0.1-local;
- every active configured Harness card is discoverable from `notes/harnesses/index.md` through one standard Markdown link;
- source integrity, structured provenance, Local Private status, and blocked output types;
- reviewer independence, unsupported-claim handling, error paths, and recovery;
- canonical preview removes Local paths, IDs, raw source, and sensitive content;
- the user guide describes the actual behavior.

Static checks may support a Community candidate only. Runtime, user, and actual BoI Wiki evidence decide Verified or Reference status. Admin evaluation never dictates fixture-specific Skill behavior.

Level 0 Local lint must reject heading-only configured Harness cards, metadata-only wrappers, and unresolved placeholders such as `TODO`, `TBD`, or angle-bracket tokens. A passing card must contain concrete requests, measurable conditions, ownership, reviewer authority, scale-mode and artifact contracts, recovery, exact promotion safety, saved-path activation, honest status, and evolution content; section names alone are never sufficient.

### Phase 7 — Evolve the Harness

Classify feedback as a Case method defect, orchestration defect, generic Skill defect, fixture/prompt defect, validator defect, or runtime defect. Change the smallest owning layer, preserve failed attempts, and rerun affected plus cross-Case regression.

Promote behavior into a generic Skill only after at least three independent Cases demonstrate the same stable need and baseline evidence shows reusable improvement. A Case failure alone never creates a new Skill or weakens OKF, BoI, or the Local/Remote boundary.

## Minimum outputs

Every completed Harness design must contain:

1. a one-sentence request the user can copy;
2. target work, target user, and success conditions;
3. existing Skills reused and any duplication decision;
4. roles, responsibilities, and reviewer authority;
5. a dependency DAG and phase exit criteria;
6. Single, Reduced, Full, and No-team behavior;
7. input, intermediate, and final output contracts;
8. missing, damaged, ambiguous, and access-denied fallback;
9. the Local/Remote boundary;
10. promotable outputs and directly blocked artifacts;
11. an OKF·BoI·security·quality checklist;
12. a non-developer walkthrough;
13. an evolution record stating which layer owns future feedback and what evidence would justify a generic Skill change.
14. the Local Harness card path and a copyable next-session request that reactivates it without rebuilding it.

Do not substitute benchmark scaffolding, empty templates, or metadata-only wrappers for these outputs.

## Case and status rules

- `cases/` contains results produced by the Meta Harness.
- This recovery phase publicly maintains only the Flagship Second Brain as a representative Case; generic drafts remain preserved experimental assets.
- `community`: static contract and safety checks pass.
- `verified`: at least one supported runtime and required user verification have reproducible evidence.
- `reference`: both runtimes, repetitions, baseline, independent review, non-developer acceptance, and actual BoI Wiki contract all pass.

An inaccessible external system remains an explicit pending gate. Never convert simulation or static similarity into production evidence.

## Finish

Report in user language:

- the one-sentence request and success condition;
- reused Skills, roles, DAG, and scale mode;
- inputs and expected outputs;
- Local/Remote and promotion boundary;
- validation result and unresolved gates;
- evolution decision and the smallest owning layer;
- where the walkthrough starts.

Do not lead with evaluator internals or benchmark counts. Never call a Harness production-ready merely because its files resemble a high-quality example collection.
