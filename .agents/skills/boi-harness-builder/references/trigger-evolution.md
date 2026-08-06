# Trigger boundaries and evidence-led evolution

This reference prevents a growing Case catalog from becoming noisy and prevents one successful Case from creating a premature generic Skill.

## Discovery contract

For a new reusable Skill, write 8-10 natural should-trigger requests and 8-10 close near-miss requests. For a Case, cover at least:

- full new request
- follow-up or partial rerun
- existing material update
- damaged or missing input
- adjacent Case with overlapping vocabulary
- ordinary one-off BoI authoring that should use an authoring Skill instead
- evaluation or audit request that should invoke the Meta Factory
- explicit Second Brain retention request versus ordinary Case execution

Near-miss examples must be genuinely close. Unrelated programming or trivia prompts do not test a useful boundary.

## Collision audit

Before adding a Case or changing a Skill description:

1. collect existing Skill descriptions and Case start prompts
2. identify the nearest three alternatives
3. run should-trigger and near-miss queries against the proposed boundary
4. explain why each collision resolves to the selected owner
5. prefer extending an existing owner over adding a synonym

## Feedback classification

Classify a real defect before editing:

| Defect | Smallest owning layer |
|---|---|
| wrong domain interpretation | Case reference or role card |
| missing or stale handoff | orchestration/runtime contract |
| poor discoverability | Case start prompt or Skill description |
| malformed result | Case output contract |
| confusing non-developer journey | walkthrough or Wiki |
| repeated operation across Cases | generic Skill candidate |
| OKF, BoI, privacy, or promotion violation | shared BoI contract; hard fail |

Record the failing prompt, runtime, source fixture checksum, observed evidence, expected behavior, changed layer, and affected regression set. Do not store real Local Private source or raw user transcripts as public evolution evidence.

## Generic Skill promotion gate

Promote repeated behavior into a generic Skill only when all are true:

- it appears in at least three independent Cases
- its inputs, outputs, errors, and safety boundary are stable
- it is not a domain vocabulary pack or thin template
- should-trigger and near-miss boundaries are discriminating
- with-Skill results beat an isolated baseline on meaningful assertions
- at least one cross-Case regression shows reuse without domain leakage
- a maintainer approves the promotion

If any condition is missing, improve the Case or shared reference instead.

## Evolution loop

```text
real run or feedback
-> classify defect
-> preserve failing evidence
-> preview smallest change
-> apply after required approval
-> rerun affected prompt
-> rerun cross-Case safety and trigger regression
-> record result and unresolved gates
```

Do not overwrite failed iterations, backfill fabricated scores, or tune only to one fixture. An external gate that cannot be executed remains pending.
