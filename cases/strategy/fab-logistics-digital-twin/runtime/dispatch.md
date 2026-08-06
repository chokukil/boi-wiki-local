# Runtime dispatch — FAB Logistics Digital Twin

Contract: `boi-local-case-runtime/v1`

이 문서는 Codex·Claude·Single-agent가 같은 Case 산출물 계약을 실행하기 위한 얇은 adapter입니다. 별도 도메인 Skill이나 OKF schema를 만들지 않습니다.

## Load order

1. [Case manifest](../case.yaml)와 [orchestrator DAG](../orchestrator.md)
2. 선택한 scale mode에서 필요한 역할 카드만
3. [domain method](../references/method.md)와 [output contract](../expected/OUTPUT-CONTRACT.md)
4. [fixture manifest](../fixtures/manifest.json)와 해당 source subset
5. 실제 평가일 때만 [frozen protocol](../evals/PROTOCOL.md)

## Role cards

- [research-coordinator](../roles/research-coordinator.md)
- [standards-source-researcher](../roles/standards-source-researcher.md)
- [twin-model-analyst](../roles/twin-model-analyst.md)
- [ontology-workflow-curator](../roles/ontology-workflow-curator.md)
- [independent-reviewer](../roles/independent-reviewer.md)

Reviewer: **independent-reviewer**

## Runtime mapping

- **Codex Full:** DAG에서 독립적인 역할만 병렬 agent로 보내고, 모든 handoff 파일이 완성된 뒤 reviewer를 실행한다.
- **Claude Full:** 같은 역할 카드와 DAG를 사용한다. Team 기능이 없으면 Reduced 또는 Single-agent로 자동 축소한다.
- **Reduced:** creator 1명과 독립 reviewer 1명으로 실행한다.
- **Single-agent/No-team:** 역할별 pass를 순차 수행하고 reviewer pass에서는 source부터 다시 읽는다.

어떤 runtime도 입력·산출물 schema, hard fail, Local/Remote 경계, reviewer exit criteria를 줄일 수 없다.

## Handoff envelope

모든 역할 전환은 [boi-local-case-handoff/v1](../../../_schema/handoff.schema.json)을 사용한다. 단순 채팅 요약만으로 다음 역할을 시작하지 않는다. output file hash와 source-integrity hash가 없으면 해당 handoff는 실패다.

## Stop conditions

- source hash drift 또는 허용 source 밖 접근
- 누락 evidence를 사실처럼 채움
- reviewer와 creator 독립성 상실
- Local path·식별자·raw bytes가 remote projection에 포함됨
- 승인 없는 MCP write 또는 remote submit

중단 시 완료를 주장하지 않고 blocker와 안전한 resume point를 Local에 남긴다.
