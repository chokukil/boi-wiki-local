# Output contract — FAB Logistics Digital Twin

## Required Local envelope

Durable Local knowledge는 다음을 사용합니다.

```yaml
okf_version: "0.1"
boi_profile_version: "0.1-local"
visibility: local-private
local_only: true
source_refs: []
generated_from: []
```

## Normal artifacts

| Artifact | Required content |
|---|---|
| `source-manifest.json` | public standard scope, vendor docs, access limitations, hashes |
| `twin-capability-map.md` | asset, state, event, simulation, control boundary, evidence |
| `ontology-map.md` | Object, Property, Link, Event, Action, governance, unknown |
| `pilot-hypotheses.md` | hypothesis, public rationale, required internal data, safety gate, falsifier |

해당 실행에 필요하지 않은 artifact는 만들지 않습니다. 변화가 없으면 빈 change set이 정상 결과이고 보고서는 생성하지 않습니다.

## Review and failure artifacts

- `reviewer-report.json`: decision, reviewed source hashes, material claims, contradictions, unresolved, reviewer identity
- `partial.json` 또는 `blocked.json`: failure phase, verified artifacts, invalidated dependents, retry count, checkpoint hash, resume condition
- `promotion-preview.json`: sanitized body, reviewer, target scope, remote-safe source refs, exact candidate SHA256, `approved=false`, `submitted=false`

Promotion candidate의 내용, source, reviewer, scope 또는 hash가 바뀌면 기존 승인은 무효입니다.
