<!-- boi-harness-bootstrap:managed -->
# Codex Bootstrap for BoI Wiki Local

This file is a thin client bootstrap generated from the pinned BoI Wiki HarnessPackage.
It is not the canonical policy source.

- Harness release: `harness-2.0-44d7fde6838a`
- Harness checksum: `b7b9afe61d88b07279e3460de25c0feb1186ac9d5d3cfbed0564c7b4cbf04ffa`
- Canonical snapshot: `.boi-harness/package.json`
- Local lock: `harness.lock`

Before using shared BoI capabilities, read the pinned package contracts. If an optional
validation runtime is available, run `scripts/harness_sync.py verify`; otherwise compare the
embedded release, canonical checksum, signature, and signature algorithm in the lock and snapshot
and label the reduced check. The canonical package checksum is not the raw `package.json` file
SHA256; never compare those two values. If the shared endpoint is unavailable, continue with the
pinned offline snapshot and Local Private files only.

- Fetch the current HarnessPackage before claiming or executing work.
- Use the authenticated principal ACL and package checksum on every TaskPackage.
- Preview mutations and require the shared confirmation contract.

Local Private source text under `data/boi/private/` must never be published to BoI Wiki, MCP,
Team, or Public scope without an explicit user-approved preview. A user-selected AI runtime may
process selected content under the approved provider and company policy; record that separately
from BoI remote activity and never claim false zero-byte processing. Shared execution must inherit
the authenticated principal ACL, use expected revision and idempotency, and follow preview then confirmation.

## Local Second Brain session check

When a real Local Profile contains `.boi-local/second-brain-preferences.json`, use the
`boi-second-brain` Skill. Check the configured source folder at session start only when
`agent_session_check` is true. In `suggest` mode, show a grouped preview before knowledge writes.
In `explicit-only` mode, do not inspect the folder or retain conversation knowledge automatically;
act only after an explicit natural-language request. Never copy raw chat transcripts. This check
must not require Python, open an external window, run without the agent, or upload Local Private content.

## Meta Harness and Case Harnesses

Use `boi-harness-builder` when a user wants to turn a recurring work description into a
reusable BoI Harness, or to package, evaluate, register, or evolve that repeatable pattern.
Do not use it for ordinary one-off document authoring or merely running an existing Case.
When a user asks to run a previously configured personal Harness, search the active Local Profile's
`notes/harnesses/` directory, load the matching profiled Harness card, and execute its declared DAG
and output contract. Invoke the builder again only to audit or evolve that card. Reuse existing generic
BoI Skills before proposing a new Skill. Case-specific domain knowledge
belongs under `cases/`; it must not silently create a new OKF schema or global domain Skill.
Never call a Case `reference` or `production-ready` unless its stored cross-runtime benchmark,
hard safety assertions, blind review, non-developer acceptance, and actual BoI Wiki contract
evidence satisfy the production gates.
