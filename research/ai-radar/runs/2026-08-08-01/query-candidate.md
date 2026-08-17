# AI Radar 고정 Query — 교정 업데이트 후보 답변

상태: **승인 전 후보 · revision 1 유지**

> 현재 확보한 공개 자료를 기준으로 실제 채택·실험 판단을 바꿀 만한 AI 기술 변화는 무엇이며, Agentic AI와 Physical AI는 어디에서 연결되고, 근거가 부족하거나 아직 검증할 수 없는 것은 무엇인가?

## 실제 판단을 바꾸는 변화

1. MCP 2026-07-28은 RC가 아니라 정식 규격이 됐다. 이제 “확정 대기”보다 stateless core·MRTR·header routing·authorization hardening의 client/server 호환과 migration을 검증해야 한다.
2. Microsoft Agent Framework는 core harness를 release했지만 background agents·file access·looping·shell은 같은 안정 수준이 아니다. framework 전체를 하나의 production-ready 상태로 평가하면 안 된다.
3. 중앙 Skill 배포가 MCP와 catalog 형태로 등장하면서 versioned harness의 범위가 source revision, content hash, trust policy와 rollback까지 넓어졌다.
4. agent 평가는 model benchmark가 아니라 model+harness+environment, heterogeneous workspace 결과와 full trajectory를 함께 고정하는 방향으로 강화됐다.
5. 고위험 agent는 결과 이후 검사만으로 부족하다. resource access·information flow를 실행 중 감시하고 고위험 action 전에 차단하는 control layer를 평가해야 한다.

## 제조 Physical AI와의 연결

LeRobot 0.6은 world model, reward, simulation evaluation과 human correction을 하나의 실험 loop로 묶었다. NVIDIA의 Physical AI skills는 agent가 simulation·data generation·training·evaluation·deployment workflow를 실행하는 연결을 보여준다. 따라서 첫 연결 실험은 로봇의 무제한 자율 action보다 Digital Twin과 개발·검증 workflow 자동화에 두는 편이 현재 근거에 맞다.

안전은 모델 성능만이 아니라 compute·sensor·OS·application·inspection과 certification preparation을 잇는 system gate로 확장해야 한다. 다만 Halos의 full-stack framing은 vendor claim이고 blueprint는 early access이며 certification 완료 증거가 아니다.

## 유지되는 conflict와 unknown

- 중앙 Skill update의 편의와 공급망 통제 부담은 함께 존재한다.
- Halos의 certification-ready 표현과 실제 early-access·인증 준비 상태를 구분해야 한다.
- HarnessOpt-Bench, DataSpace, HarnessAudit, W2-VLA와 DyPES-VLA는 이번 실행에서 abstract만 확인했다.
- 새 VLA 결과는 shortlist를 늘렸지만 제조 일반화·독립 real-robot 재현 판단을 바꾸지 못했다.
- 특정 조직의 데이터·설비·보안·비용·ROI와 실제 적용성은 여전히 unknown이다.

이 답변은 승인 전 후보다. 현재 Query의 공식 답은 계속 [revision 1 답변](../../13-updated-query-answer-candidate.md)이며, 사람 승인 전에는 revision을 올리지 않는다.
