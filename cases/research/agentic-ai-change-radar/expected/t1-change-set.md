# T1 expected change set

Fixture: `PUB-AAI-RADAR-002-v1`

| Delta | Claim | Expected result | Evidence and reason |
|---|---|---|---|
| new | AAI-008 | remote MCP, background execution과 encrypted reasoning items가 runtime 선택지로 추가 | `07` / `cf41e8038d89d8814852d8cbe44622d16887ac3f407269b98349afd1a6b4923a` |
| new | AAI-009 | A2A가 cross-vendor agent interoperability 후보로 등장 | `08` / `2bcfea3c9c07c793410299602ac1ba2847ca6ca10a2e05c848bad3916a2bab06` |
| new | AAI-010 | 소수의 명확한 agent-oriented tool, namespacing과 context-efficient result가 설계 기준으로 추가 | `09` / `c743229967e427c7173f7ab657146654449743e52086f7b0afd7555df805a9ea` |
| new | AAI-011 | persistent session, structured note, compaction과 resume가 memory·context 구현 선택으로 구체화 | `04` + `10` |
| new | AAI-012 | filesystem와 network isolation이 bounded execution의 product-specific pattern으로 추가 | `11` / `d0cc99b57262561cd77374b3dd25a98032a1d8e593abf96c02138f4b2ee8077c` |
| new | AAI-013 | initializer, incremental progress와 structured handoff가 long-running resume pattern으로 추가 | `12` / `253460fc984957367a80f9733f2e409913e52ea2c065e8b16a44f91111fdd284` |
| strengthened | AAI-002 | tracing 방향이 multi-turn·multiple trials, outcome/transcript grader, regression suite와 human calibration으로 구체화 | T0 `02` + T1 `13` |
| strengthened | AAI-001 | 단순하게 시작하되 model capability가 바뀌면 load-bearing하지 않은 harness phase를 제거한다는 evolution rule 추가 | T0 `01` + T1 `14` |
| revised | AAI-003 | TypeScript-first SDK와 Sessions가 현재 문서화되어 T0 Node.js roadmap을 수정 | `04` / `60c26ff8d79a5654b67143ba3732f890f2a50e8660474b8ca7b849705f16332b` |
| contradicted | AAI-004 | current MCP authorization을 base URL fallback만으로 설명하면 Protected Resource Metadata·Resource Indicators와 충돌 | `03` + `05` |
| contradicted | AAI-016 | Agent Builder/Evals의 launch framing은 같은 공식 페이지의 2026 wind-down notice와 장기 채택 판단에서 충돌 | `06` / `4c91e8105b0e1c001909b7597bf431896cd5784d406cc99775a601ed4277bb7c` |
| stale | AAI-003 | T0 roadmap 문장은 history로 유효하지만 current support 설명으로는 stale | T0 `02` + T1 `04` |
| stale | AAI-016 | Agent Builder/Evals launch는 history로 보존하되 장기 신규 채택 후보로는 stale | `06` launch + wind-down |
| retirement-candidate | AAI-004 | 2025-03 discovery model을 current normative guidance에서 제거 후보로 올리되 history 보존 | `03` + `05` |
| retirement-candidate | AAI-016 | Agent Builder/Evals를 2026-11-30 이후 신규 채택 guidance에서 제거 후보로 올리되 migration history 보존 | `06` |
| unknown | AAI-005 | 공개 선택지는 늘어도 SK하이닉스 적용 효과, 비용, ACL, 보안·data boundary는 계속 판단 불가 | 내부 validation과 사람 Review 필요 |

이 oracle은 [실제 실행 change set](../golden-journey/runs/2026-08-06/t1/change-set.json)에서 같은 delta 유형, source hash와 history binding으로 재현됩니다.
