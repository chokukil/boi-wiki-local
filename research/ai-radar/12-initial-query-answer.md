# 기준 지식으로 답한 고정 Query

기준일 2025-11-30의 공개 자료만 사용했다.

> 현재 확보한 공개 자료를 기준으로 실제 채택·실험 판단을 바꿀 만한 AI 기술 변화는 무엇이며, Agentic AI와 Physical AI는 어디에서 연결되고, 근거가 부족하거나 아직 검증할 수 없는 것은 무엇인가?

## 답변

실제 채택 판단을 바꿀 만큼 분명한 변화는 agent를 “큰 prompt가 달린 모델”이 아니라 tool, state, trace, permission과 handoff를 포함한 runtime으로 봐야 한다는 점이다. 복잡한 agent보다 결정적 workflow를 우선하고, Responses API·MCP·A2A 같은 연결 계층은 역할을 분리해 실험해야 한다. 장기 작업은 context를 계속 누적하기보다 외부 상태와 session handoff로 이어가며, sandbox와 최소 권한을 전제로 해야 한다.

Physical AI에서는 Gemini Robotics와 GR00T N1이 VLA 방향을 구체화했고, Digital Twin·simulation은 로봇과 제조 시스템을 실제 설비 전에 시험할 후보 환경이다. OpenUSD는 3D scene interchange, AAS·OPC UA는 asset representation과 산업 상호운용, Palantir식 ontology는 object·link·action의 운영 모델을 제공할 수 있다. 그러나 이 층들이 실제 agent action과 안전하게 연결됐다는 공개 evidence는 부족하다.

따라서 기준일의 실험 우선순위는 다음과 같다.

1. bounded workflow와 agent를 같은 업무에서 비교한다.
2. trace·state·permission·handoff를 먼저 고정한다.
3. Physical AI는 simulation을 거치고 human-in-the-loop로 제한한다.
4. ontology와 protocol은 가능성만 검토하고 실제 설비 action은 연결하지 않는다.

근거가 부족한 것은 agent의 장기 신뢰성, multi-agent의 순효과, VLA의 실환경 일반화, Digital Twin ROI, ontology 이식성과 SK하이닉스 적용성이다.
