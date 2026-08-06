# Runtime-neutral architecture selection

Architecture describes logical collaboration, not a vendor feature. The same Case contract must work with Codex, Claude, a two-role review, one agent in separated passes, or no team feature.

## Selection questions

1. Does the work require different expertise or independent judgment?
2. Can source collection or analysis run independently?
3. Must specialists challenge each other before integration?
4. Is there an objective reviewer gate?
5. Is the workload known before execution or discovered while running?

## Patterns

| Pattern | Use when | Required control |
|---|---|---|
| pipeline | each stage depends on the prior artifact | explicit phase exit and stale downstream detection |
| fan-out/fan-in | independent perspectives inspect the same or partitioned input | source boundaries and an integration reviewer |
| specialist pool | input type selects one of several methods | routing rule and unsupported-type fallback |
| producer-reviewer | objective quality or safety checks exist | independent review and bounded retries |
| supervisor | tasks are discovered or rebalanced during work | visible work queue and partial completion policy |
| hierarchical | the outcome decomposes into nested domains | maximum depth and lossless file handoffs |

Use a hybrid only when each transition is explicit. Do not add roles to meet a numeric target; split roles by expertise, context isolation, parallelism, or independent verification.

## Scale projection

| Logical mode | Execution |
|---|---|
| Full | separate logical roles and independent reviewer follow the DAG |
| Reduced | one producer and one independent reviewer combine compatible roles |
| Single-agent | one agent performs role passes sequentially and reviews source-first in a separated pass |
| No-team fallback | the same role cards, files, exits, and handoffs run without team APIs |

The output schema, Local/Remote boundary, source hashes, and hard safety assertions never change with scale.

## Handoff contract

Every dependency crossing uses `boi-local-case-handoff/v1` and records:

- Case, run, source role, and target role
- exact artifact paths and SHA256 values
- claims supported by each artifact
- unknowns, contradictions, blockers, and review questions
- phase exit status

A chat summary or Canvas/Graph edge is not a handoff. Missing evidence remains unknown.

## Reviewer independence

The reviewer starts from the source manifest, expected contract, and candidate output. It must not rely only on the producer's conclusion. In Single-agent mode, separate the reviewer pass, reload the source contract, and record that independence is procedural rather than multi-agent.

## Failure behavior

- one specialist fails: bounded retry, then continue only if its output is optional and mark the gap
- required source missing or hash mismatch: block the dependent phase
- conflicting evidence: preserve both, record the conflict, and require a human decision when the contract demands it
- reviewer failure: do not self-approve
- optional runtime feature unavailable: fall back to the next scale mode without weakening the output or safety contract
