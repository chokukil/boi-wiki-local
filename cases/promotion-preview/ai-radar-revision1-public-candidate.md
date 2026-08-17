---
okf_version: "0.1"
boi_profile_version: "0.1"
type: boi/knowledge
title: "Agentic AI와 제조 Physical AI 채택 검토 원칙"
description: "공개 원 출처에서 검토한 agent harness, 평가, protocol과 Physical AI 연결의 재사용 가능한 원칙"
visibility: public
classification: public
status: draft
review: pending
contains_sensitive: false
source_refs:
  - type: url
    ref: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
  - type: url
    ref: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
  - type: url
    ref: https://developers.googleblog.com/en/agents-adk-agent-engine-a2a-enhancements-google-io/
  - type: url
    ref: https://deepmind.google/blog/gemini-robotics-brings-ai-into-the-physical-world/
  - type: url
    ref: https://industrialdigitaltwin.org/en/content-hub/aasspecifications
---

# Agentic AI와 제조 Physical AI 채택 검토 원칙

Agentic AI는 모델의 단일 응답 성능만으로 채택하지 않는다. 장기 실행의 상태 지속, artifact와 checkpoint, tool 권한, 실패 복구와 handoff를 포함한 harness를 하나의 평가 단위로 본다.

평가는 최종 답변뿐 아니라 trajectory, tool call, recovery와 근거 연결을 함께 본다. 모델·harness·실행 환경이 달라지면 결과의 비교 가능성도 다시 검토한다.

MCP나 A2A 같은 agent protocol은 tool·context 연결과 agent 간 상호운용을 돕지만 산업 자산의 의미, 설비 권한과 물리 안전을 대신하지 않는다.

Agentic AI와 제조 Physical AI의 첫 연결은 무제한 설비 action보다 simulation, data generation, training과 evaluation workflow에서 검토하는 편이 안전하다. Digital Twin과 표준 자산 representation은 world state와 실험 환경 후보가 될 수 있으나 실제 제조 효과와 vendor 간 이식성은 별도 증거가 필요하다.

이 문서는 공개 자료에 근거한 일반 원칙 초안이다. 특정 조직의 적용성, 비용, 보안 적합성, vendor 선정 또는 production readiness를 결론내리지 않는다.
