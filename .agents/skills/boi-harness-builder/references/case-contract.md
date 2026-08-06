# Case Harness contract

Use `boi-local-case-harness/v1` for distribution metadata. This contract does not add an OKF or canonical BoI type.

## Required package

- `CASE.md`: audience, value, one-sentence request, boundaries, next step.
- `case.yaml`: JSON-compatible YAML manifest.
- `orchestrator.md`: phases, dependency DAG, handoffs, scale modes, failures.
- `roles/roles.md`: 4–5 logical roles including an independent reviewer.
- `roles/<role>.md`: one progressive-disclosure execution card per logical role with input, output, handoff, exit, hard-fail, and scale behavior.
- `runtime/runtime.yaml` and `runtime/dispatch.md`: runtime-neutral Codex·Claude·single-agent mapping and exact role-card inventory.
- `prompts/evals.md`: five realistic evals; the Second Brain flagship uses eight.
- `references/`: domain methods loaded only for that Case.
- `fixtures/`: synthetic or public inputs and source ledger.
- `expected/`: representative Local outputs using OKF 0.1 and BoI Profile 0.1-local.
- `walkthrough/`: non-developer journey that works without optional tools.
- `evals/`: plan, assertions, benchmark, failures, and runtime evidence.

## Manifest fields

Require `schema`, `case_id`, `title`, `category`, `status`, `version`, `audience`, `start_prompt`, `logical_roles`, `reviewer_role`, `orchestration_pattern`, `scale_modes`, `required_skills`, `optional_features`, `fixture_policy`, `expected_local_types`, `direct_promotion_blocked_types`, `eval_prompt_count`, `evaluation_protocol`, `fixture_id`, `runtime_contract`, `runtime_manifest`, `handoff_schema`, `reference_gate`, and `domain_validation`.

Runtime projection uses `boi-local-case-runtime/v1`; every transition uses `boi-local-case-handoff/v1`. These are distribution and execution metadata, not new OKF or canonical BoI types.

Allowed status values are `community`, `verified`, and `reference`. Only the production evaluator may set `reference`.

## Output boundary

Every profile output uses Local OKF 0.1 + BoI Profile 0.1-local. Evidence, capture, hypothesis, analysis log, and agent-memory stay Local. Promotion starts only from a supported distilled type and creates a sanitized canonical preview.
