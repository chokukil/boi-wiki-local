# Agentic AI 공식 source records

확인일: 2026-08-08. 아래 hash는 [manifest](../03-source-manifest.json)에 있다.

| ID | 확인한 내용 | 사용한 근거 | 제한 |
|---|---|---|---|
| A01·A02 | Responses API, built-in tools, Agents SDK, tracing | runtime·tool·observability가 모델 호출과 분리된 계층이 됨 | OpenAI 제품 설명 |
| A03 | workflow와 agent의 구분, 단순 pattern 우선 | B-A01 | Anthropic 경험 기반 |
| A04 | context curation, compaction, 외부 저장 | B-A04 | 일반화 전 runtime별 확인 필요 |
| A05 | sandbox와 permission 경계 | B-A05 | Claude Code 구현 사례 |
| A06 | initializer, progress artifact, session handoff | B-A06 | 독립 재현 없음 |
| A07 | transcript·outcome·grader·harness를 함께 평가 | U-A01 | 벤더 방법론, 개별 도메인 적용 필요 |
| A08 | planner·generator·evaluator와 장기 harness | U-A02 | coding 실험, 다른 도메인 일반화 미확인 |
| A09 | stateless core, extensions, tasks, apps, auth hardening, deprecation policy | U-A03 | 2026-07-28 release candidate |
| A10·A11 | ADK, A2A, Java 1.0 | B-A03, U-A04 | Google 생태계 구현 |
| A12 | .NET·Python core/workflow 1.0과 preview surface 구분 | U-A05 | 벤더의 production-ready 표현을 그대로 일반화하지 않음 |
| A13 | checkpoint, thread, store 기반 persistence | B-A04 | LangGraph 구현 계약 |

## 판정 메모

- A09는 새 기능의 존재를 확인하는 근거지만 정식 사양 채택 근거는 아니다.
- A12는 기준일의 preview 판단을 수정한다. 다만 DevUI·hosted integration·managed eval 등 일부 surface는 같은 발표 안에서도 preview다.
- framework feature list는 실제 신뢰성·비용·보안 성과를 증명하지 않는다.

