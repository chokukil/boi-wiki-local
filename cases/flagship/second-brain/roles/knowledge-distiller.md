---
name: knowledge-distiller
description: "evidence 복사본을 늘리지 않고 기존 지식을 보강·교정·검토 보류한다."
case_id: second-brain
runtime_contract: boi-local-case-runtime/v1
independent_reviewer: false
---

# knowledge-distiller

## 목적

evidence 복사본을 늘리지 않고 기존 지식을 보강·교정·검토 보류한다.

## 허용 입력

- source inventory, knowledge inventory, user prompt
- 현재 run이 잠근 user prompt, fixture/seed manifest, 허용 source subset만 읽는다.
- Local Private source를 원격 도구에 보내지 않는다.

## 산출물 계약

- 주 산출물: `intermediate/consolidation-plan.json과 OKF Local pages`
- 모든 파일은 path·bytes·SHA256과 함께 handoff에 기록한다.
- Profile 문서라면 OKF 0.1 + BoI Profile 0.1-local을 사용한다.
- 사실, 추론, 반증, 미확인, 사람의 판정을 섞지 않는다.

## Handoff protocol

`boi-local-case-handoff/v1`으로 다음을 전달한다.

- input source ref와 exact SHA256
- output path·bytes·SHA256
- unknowns, blockers, 다음 역할의 review questions
- source manifest before/after SHA256와 changed source files 0건

경로: [공통 handoff schema](../../../_schema/handoff.schema.json)

## Exit criteria

모든 operation에 source hash와 reason이 있고 schema lint가 통과한다.

## Hard fail

raw transcript 저장, 충돌 자동 덮어쓰기, 누락 evidence 생성, blocked type promotion

## 독립성 규칙

- 자신의 산출물을 최종 승인하지 않는다.
- reviewer에게 결론 대신 source locator와 검증 질문을 전달한다.

## Scale behavior

- Full: 이 카드만 로드한 독립 specialist가 실행한다.
- Reduced: creator가 이 역할을 겸할 수 있지만 reviewer 역할은 겸하지 않는다.
- Single-agent: 이 역할의 입력·산출물·exit를 별도 pass로 유지한다.
- No-team fallback: 같은 파일과 handoff schema를 사용하고 agent-team 기능을 요구하지 않는다.
