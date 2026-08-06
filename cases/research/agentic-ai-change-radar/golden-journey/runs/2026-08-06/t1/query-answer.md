# T1 Query answer

Query SHA256: `2d9541b2df6271e8fcfcc812529e2006e5c069b6b57ae83e7fb03772350c7b13`

## Answer

현재 공개 지식으로는 하나의 “최고 agent stack”을 고르는 대신 다음 채택 기준을 사용할 수 있습니다.

1. Runtime은 TypeScript-first Agents SDK, persistent Sessions·resume·compaction, remote MCP와 background execution까지 선택지가 넓어졌습니다. 기능 존재와 내부 data boundary 승인은 분리해야 합니다.
2. Orchestration은 단순 pattern에서 시작하되 long-running 작업에는 explicit progress artifact와 clean handoff를 두고, planner·evaluator가 실제 baseline 대비 lift를 낼 때만 유지합니다.
3. Tool use는 API 수를 늘리기보다 agent가 구분하기 쉬운 소수의 목적별 tool, namespacing, context-efficient result와 held-out eval을 우선합니다. A2A는 agent-to-agent, MCP는 tool/context 연결의 상호보완 후보지만 conformance와 governance는 아직 검증 대상입니다.
4. Memory·context는 persistent session, structured note, just-in-time retrieval과 compaction을 조합할 수 있습니다. compaction 정보 손실과 retention·삭제 정책은 명시적으로 시험해야 합니다.
5. Evaluation은 단일 답 검사보다 multiple trials, outcome와 transcript grader, capability·regression suite 구분, human calibration을 요구합니다.
6. Security는 MCP version·token audience를 고정하고, product-specific 사례가 제시한 filesystem와 network isolation 같은 bounded execution을 대상 환경에서 다시 검증해야 합니다.

Agent Builder와 Evals는 2025년 출시 사실을 history로 보존하지만, 공식 2026년 wind-down 공지 때문에 장기 신규 채택 후보로는 stale·retirement-candidate입니다.

## Evidence

- Runtime·memory: `04` / `60c26ff8d79a5654b67143ba3732f890f2a50e8660474b8ca7b849705f16332b`, `07` / `cf41e8038d89d8814852d8cbe44622d16887ac3f407269b98349afd1a6b4923a`
- MCP security revision: `03` / `a2a76a099a2b59f4de4478fa431b0bbf07fc6c7187c834da77c6d8e3aa7f54f6`, `05` / `03eaedc393b03459971ff018504e7a203d09d0ac49c39cff3b3b083fa78f6dda`
- Interoperability·tools: `08` / `2bcfea3c9c07c793410299602ac1ba2847ca6ca10a2e05c848bad3916a2bab06`, `09` / `c743229967e427c7173f7ab657146654449743e52086f7b0afd7555df805a9ea`
- Context·sandbox: `10` / `26e312fa1b1fb23724af1c405ca7da3668446cbb753772ccac81fcf44782310e`, `11` / `d0cc99b57262561cd77374b3dd25a98032a1d8e593abf96c02138f4b2ee8077c`
- Harness·evaluation: `12` / `253460fc984957367a80f9733f2e409913e52ea2c065e8b16a44f91111fdd284`, `13` / `abcc41429426d453a6959005605d05a7fb4c8cd186799c78e4c421202e58127d`, `14` / `eb90b01b52af6f06969d3261fb464aa9548655b182083aa73bc33ce368bab171`
- AgentKit lifecycle: `06` / `4c91e8105b0e1c001909b7597bf431896cd5784d406cc99775a601ed4277bb7c`

## Counterevidence

- T0 MCP base-URL 중심 설명은 June revision의 Protected Resource Metadata 요구와 현재 guidance에서 충돌합니다.
- Agent Builder launch는 같은 페이지의 wind-down notice와 장기 채택 판단에서 충돌합니다.
- Compaction은 장기 coherence를 돕지만 subtle state를 잃을 수 있습니다.
- Planner·evaluator는 어려운 task에서 도움이 될 수 있지만 model capability가 올라가면 일부 decomposition은 overhead가 됩니다.
- Vendor engineering report는 독립된 cross-runtime benchmark나 SK하이닉스 운영 증거가 아닙니다.

## Unknowns

- SK하이닉스 업무별 허용 data·model·network boundary와 ACL
- 대표 task의 baseline, 품질·latency·cost, failure tolerance
- A2A/MCP 실제 conformance, identity와 audit mapping
- memory retention·deletion·compaction recall 기준
- sandbox residual risk와 credential scope
- Agent Builder/Evals migration parity와 실제 종료 후 상태

## Next checks

공개 source만으로는 위 unknown을 해소할 수 없습니다. 다음 단계는 내부 데이터를 넣는 것이 아니라, 먼저 비민감 synthetic task와 명시된 금지 데이터 경계로 baseline·evaluation·security checklist를 설계하고 사람 승인을 받는 것입니다.

## Confidence

공식 기능·version·lifecycle 변화에는 `high`, 설계 지침의 타 domain 전이에는 `medium-to-low`, SK하이닉스 채택 효과에는 `unknown`입니다.
