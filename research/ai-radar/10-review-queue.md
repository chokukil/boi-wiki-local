# Review queue

| 우선순위 | 항목 | 검토 질문 | 필요한 근거 | 현재 상태 |
|---:|---|---|---|---|
| 1 | MCP 2026 RC | 정식 release에서 tasks·apps·auth가 유지되는가? | 최종 spec·migration note | review-required |
| 2 | Agent Framework 1.0 | stable surface와 preview surface 경계가 실제 package와 일치하는가? | release tag·API compatibility | review-required |
| 3 | trajectory evaluation | transcript와 outcome grader가 실제 실패를 더 잘 잡는가? | 업무 fixture·blind review | unknown |
| 4 | memory | prospective memory와 conflict resolution이 업무 성과를 높이는가? | full text·code·reproduction | unknown |
| 5 | multi-agent | evaluator 추가 이익이 token·latency·coordination 비용을 넘는가? | controlled comparison | unknown |
| 6 | agent security | memory poisoning·cross-tool injection을 어떤 policy로 차단하는가? | threat model·red-team trace | unknown |
| 7 | GR00T N1.7 | EA에서 GA로 바뀌었고 benchmark·license가 안정됐는가? | official GA release | review-required |
| 8 | VLA generalization | 다른 embodiment·task·환경에서 재현되는가? | independent real-robot study | unknown |
| 9 | Digital Twin ROI | simulation·commissioning 효과가 독립 측정됐는가? | before/after 운영 지표 | unknown |
| 10 | ontology portability | Object·Link·Action을 AAS·OPC UA 또는 다른 platform으로 이식할 수 있는가? | mapping·round-trip test | unknown |
| 11 | temporal consistency | agent memory와 설비 event time 충돌을 어떻게 검출·복구하는가? | event-sourced fixture | unknown |
| 12 | SK하이닉스 적용성 | 공개 사실과 내부 조건을 섞지 않고 어떤 질문부터 확인할 것인가? | 승인된 내부 scoping만 | blocked-by-boundary |

## Reviewer 지침

- producer 요약이 아니라 source manifest와 원문부터 확인한다.
- vendor claim과 독립 evidence를 한 칸에 합치지 않는다.
- abstract-only 논문을 full-text verified로 올리지 않는다.
- `unknown`을 낙관적 추정으로 해소하지 않는다.
- 승인 시 exact claim ID와 source revision을 기록한다.

