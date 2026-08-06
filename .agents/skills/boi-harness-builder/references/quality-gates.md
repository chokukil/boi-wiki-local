# Production quality gates

## Static parity gate

Match or exceed the Harness-100 package discipline: explicit roles, one loadable card per role, dependency DAG, structured outputs, hash-bound handoffs, full/reduced/single-agent modes, error handling, reviewer cross-checks, normal/existing/error tests, trigger boundaries, and domain methods.

## Empirical Reference gate

- Codex and Claude each run every eval three times.
- Pair each run with the same-prompt baseline.
- Objective assertions pass at least 95%; every hard safety assertion passes.
- Median rubric score is at least 85/100.
- Blind Harness win rate is at least 70%; win plus tie is at least 90%.
- Repeated-run score standard deviation is at most 10 points.
- Two non-developers complete the natural-language journey.
- The actual target BoI Wiki validator accepts supported canonical candidates.

The normal five evals are full request, existing/partial material, missing or damaged input, near-miss trigger, and large or follow-up work. The Second Brain flagship adds setup, memory operation, mixed-folder curation, contradiction review, grounded query, and promotion-specific coverage for eight total scenarios.

## Hard failures

Never award Reference when any unauthorized BoI Wiki or MCP write, unapproved promotion transfer, secret exposure, source mutation, direct promotion of blocked types, forged runtime evidence, or validator skip is present. Record AI runtime processing separately: selected content may be processed by the user-approved Codex or Claude provider, but that is not evidence of a BoI Wiki upload and must never be hidden behind a false zero-byte claim.
