# 업데이트 후보로 답한 고정 Query

확인 시점 2026-08-08의 공개 자료를 포함한 **승인 전 후보 답변**이다.

> 현재 확보한 공개 자료를 기준으로 실제 채택·실험 판단을 바꿀 만한 AI 기술 변화는 무엇이며, Agentic AI와 Physical AI는 어디에서 연결되고, 근거가 부족하거나 아직 검증할 수 없는 것은 무엇인가?

## 답변

가장 큰 변화는 채택과 평가의 단위가 더 명확해졌다는 점이다. 이제 agent는 모델이나 framework 이름으로 비교하기보다 **model + harness + tools + policy + state + evaluator**를 묶은 versioned system으로 비교해야 한다. final answer만 평가해서는 부족하고, 실제 environment outcome, 전체 trajectory, tool call, interruption과 recovery까지 함께 봐야 한다. Microsoft Agent Framework core·workflow의 1.0, ADK의 다중 언어 확장과 MCP 2026 release candidate는 생태계 성숙 신호지만, 각각 preview surface와 RC 경계를 남긴다.

Physical AI에서는 GR00T·Cosmos·LeRobot·openpi 같은 공개 surface가 늘어 직접 실험하기 쉬워졌고, VLA·world model·Digital Twin이 하나의 evaluation loop로 가까워졌다. 그러나 GR00T N1.7이 Early Access라는 사실과 vendor·testbed 중심 evidence는 “실험 가능”과 “양산 가능”을 분리해야 함을 보여준다.

두 축은 다음에서 연결된다.

1. Digital Twin을 physical agent의 정상·경계·실패 trajectory 평가 환경으로 사용한다.
2. ontology를 world state와 허용 action의 contract 후보로 사용한다.
3. MCP·A2A는 연결 계층으로만 쓰고 AAS·OPC UA와 safety policy를 별도로 검증한다.
4. 실제 action 전에는 사람 승인, 중단·복구와 event-time audit를 요구한다.

지금 바꿀 수 있는 판단은 **pilot 설계**다. agent pilot에는 trajectory replay와 memory conflict test를, Physical AI pilot에는 sim-to-real, hardware-in-the-loop, emergency stop과 temporal consistency를 넣어야 한다. 반면 특정 제조 적용의 성능·비용·ROI, VLA의 일반화, ontology 이식성, MCP·A2A의 산업 보안과 SK하이닉스 적용성은 여전히 unknown이다.
