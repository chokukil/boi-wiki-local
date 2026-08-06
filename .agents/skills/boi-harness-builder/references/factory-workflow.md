# BoI Meta Harness Factory workflow

`boi-harness-builder` is the product factory. Its default result is an approved, reusable Local Harness card for the user's recurring work. `cases/` is a separately approved example collection that may later be produced from successful, de-identified Harness use; it is not the default output and not the factory itself.

The factory is judged first by whether a non-developer can describe work in natural language, approve a clear preview, save the resulting contract, and reuse it in another session. Packaging or evaluating a Case is a separate administrator or maintainer workflow.

## Factory input and output

| Input | Factory decision | Default output |
|---|---|---|
| recurring work description | reusable or one-off | approved Local Harness card or ordinary Local document |
| request to run a saved Harness | execute or input-blocked | Local work result; do not rebuild the card |
| request to change a saved Harness | local defect or contract change | hash-bound preview, archived prior card, evolved active card |
| explicit request to share a reusable method | generic guide or Case packaging | de-identified review candidate; never the personal card itself |
| explicit Case status claim | evidence complete or incomplete | honest Community, Verified, or Reference decision |

Every run begins with a change preview. Record the target files, preserved user files, source policy, validation surface, and gates that cannot be executed. Do not turn an unavailable external system into simulated proof.

## Factory lifecycle: Phase 0–7

### 0. Audit

Inspect the pinned HarnessPackage, active Profile's saved Harness cards, generic BoI Skills, Case catalog, nearest Case, Wiki links, and dirty worktree. Inspect runtime cards or evaluation evidence only when Case packaging, evaluation, or a status claim is in scope. Produce an audit note containing:

- selected mode: `create`, `extend`, `audit`, `evolve`, or `evaluate`
- existing assets to reuse
- collisions and drift
- intended change surface
- preserved Local Private and user-authored files

Exit only when ownership is clear. If an existing Case already owns the outcome, select `extend`.

### 1. Frame the reusable outcome

Define the non-developer start sentence, audience, durable result, real inputs, excluded actions, success evidence, and failure conditions. Separate:

- Local-only intermediate artifacts
- promotable distilled artifacts
- optional Second Brain value
- optional Obsidian or MCP views

Exit only when the outcome is repeatable and has concrete success and failure conditions. Otherwise keep an ordinary Local document instead of inventing a Harness.

### 2. Select architecture

Use `architecture-selection.md`. Produce logical roles, independent reviewer, dependency DAG, phase exits, retries, blocked paths, scale mappings, and hash-bound handoffs. Logical roles are portable; a specific agent-team feature is not required.

### 3. Reuse Skills and decide optional capabilities

Reuse existing generic Skills first and select the smallest owning set. Add `boi-second-brain` only when durable retention, later retrieval, correction history, review cadence, or promotion candidates are required. Obsidian, MCP, and team-agent execution remain optional. Do not create a domain Skill for one user's Harness. A new generic Skill needs evidence from at least three independent Cases, stable input/output semantics, close trigger boundaries, and measured baseline improvement.

### 4. Build and preview the Local Harness

Use `harness-design-template.md` to produce a substantive preview with the natural-language request, roles, DAG, scale modes, artifact and failure contracts, reviewer authority, Local/Remote boundary, promotion rules, walkthrough, and evolution owner. Do not write the card before approval. If the request itself is the material design source, preserve only the exact approved request as a Local capture and bind the preview to its hash.

### 5. Save, activate, and validate

After approval, save one `boi/local-guide` card under `notes/harnesses/`, link it from `notes/harnesses/index.md`, and validate OKF 0.1 + BoI Profile 0.1-local, source hashes, substantive contracts, and direct-promotion blocking. Return a copyable next-session request. Running that request loads and executes the card without rewriting it.

### 6. Optionally package a reusable example

Only after an explicit user request, de-identify the method and choose a separate generic guide or Community Case. For a Case, read `case-contract.md`, replace personal sources with synthetic or public fixtures, keep domain content in the Case, and request separate approval before catalog registration. Static checks can grant only Community status; Verified and Reference require the evidence in `quality-gates.md`.

### 7. Evolve

Use `trigger-evolution.md`. Classify feedback, change the smallest reusable layer, preserve unsuccessful attempts, and rerun affected plus cross-Case regression. A Case failure must not automatically create a new Skill.

## Finish report

For ordinary users, report the one-sentence request, saved card path, reused Skills, roles and scale mode, expected outputs, Local/Remote boundary, validation result, and copyable next-session request. Report Case status and evaluation gates only when Case packaging or evaluation was explicitly requested.
