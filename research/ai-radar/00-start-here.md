# AI Radar Golden Journey

상태: **Community · 현재 승인 지식 revision 1**

기준 지식 시점: **2025-11-30**

업데이트 확인 시점: **2026-08-08**

이 폴더는 공개된 최신 AI 신호를 발견하고 원 출처로 검증해, 같은 질문에 대한 답이 근거와 함께 어떻게 달라지는지 보여주는 실제 지식 성장 사례다. 제품 기능이나 SK하이닉스의 실제 운영 성과를 검증한 자료가 아니다.

## 고정 Query

> 현재 확보한 공개 자료를 기준으로 실제 채택·실험 판단을 바꿀 만한 AI 기술 변화는 무엇이며, Agentic AI와 Physical AI는 어디에서 연결되고, 근거가 부족하거나 아직 검증할 수 없는 것은 무엇인가?

## 읽는 순서

1. [범위와 판정법](01-scope-and-method.md)
2. [발견 신호 원장](02-signal-ledger.md)
3. [기준 지식 후보](04-initial-knowledge-baseline.md)
4. [Agentic AI 지식](05-agentic-ai-knowledge.md)과 [Physical AI 지식](06-physical-ai-knowledge.md)
5. [두 축의 연결](07-cross-axis-connections.md)
6. [업데이트 후보](08-update-candidate.md)와 [변경 세트](09-knowledge-change-set.md)
7. [검토 목록](10-review-queue.md)과 [충돌·미확인](11-contradictions-and-unknowns.md)
8. [기준 답변](12-initial-query-answer.md)과 [업데이트 답변 후보](13-updated-query-answer-candidate.md)의 [비교](14-answer-comparison.md)
9. [지식 이력](15-knowledge-history.md), [현재 승인 지식](17-current-approved-knowledge.md)과 [다음 실행](16-next-radar-run.md)
10. [revision 2 교정 실행 후보](runs/2026-08-08-01/index.md) — 원 출처 재검증부터 review queue까지, 승인 전 상태

## 이번 실행의 규모

| 항목 | 결과 |
|---|---:|
| 발견 신호 | 76 |
| 원 출처 확인 shortlist | 44 |
| 직접 확인한 원 출처 | 44 |
| 재사용 가능한 claim | 24 |
| 변경 후보 | 24 |
| 사람 검토 필요 항목 | 12 |

신호 수는 완성도를 뜻하지 않는다. GeekNews, GitHub Trending, Hugging Face 반응은 발견 경로일 뿐 claim 근거로 사용하지 않았고, 논문도 확인 범위가 abstract이면 그 이상을 주장하지 않았다.

## 중요한 결론

- Agentic AI의 채택 기준은 모델 단독 성능보다 **harness, 상태 지속, 평가, 권한과 복구 계약**으로 이동했다.
- MCP와 A2A는 각각 tool/context 연결과 agent 간 상호운용을 다루지만, 산업 설비의 의미·권한·안전 표준을 대신하지 않는다.
- Physical AI는 VLA, world model, simulation과 공개 로봇 도구 생태계가 빠르게 결합하고 있으나, 데모와 Early Access를 양산 성숙도로 읽으면 안 된다.
- Digital Twin과 ontology는 agent의 평가 환경과 world/action contract가 될 가능성이 있지만, 벤더 간 이식성과 독립된 운영 효과는 아직 검증이 부족하다.
- 공개 자료만으로 SK하이닉스 적용성·성과·비용은 판단하지 않는다.

## 승인 경계

2026-08-08 통합 후보는 exact candidate hash에 대한 사용자 승인으로 **최초 승인 지식 revision 1**이 됐다. contradiction과 unknown은 해결된 사실로 승격하지 않고 현재 지식의 검토 상태로 보존한다. 이 승인은 Local 연구 지식에만 적용되며 commit, 원격 Wiki와 promotion 승인이 아니다.

## 지식이 실제로 자라는 다음 단계

[교정 실행 01](runs/2026-08-08-01/index.md)은 revision 1의 MCP release 상태 오류를 덮어쓰지 않고 `revised` 후보로 남긴다. 같은 실행에서 Agent Framework의 안정·미출시 경계, 원격 Skill 공급망, harness 평가, trajectory safety, Physical AI 실험 loop와 system safety를 새 근거로 비교했다.

이 묶음은 source-first review와 동일 Query 비교까지 끝났지만 아직 사람 승인을 받지 않았다. 따라서 현재 승인 지식은 계속 revision 1이며, 후보 중 일부 또는 전부가 승인될 때만 다음 revision이 생긴다.
