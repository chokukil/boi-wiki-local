# Flagship Second Brain

상태: **Community — Codex p01~p07 repetition 1 partial evidence 보유, Reference 아님**

대상: 별도 지식관리 시스템을 구축하지 않고도 AI와 Local Markdown으로 개인 지식을 장기 자산화하려는 구성원

## 한 문장으로 시작

~~~text
이 저장소를 내 BoI Wiki Local Second Brain으로 설정해줘. 대화와 자료 폴더에서 오래 쓸 지식을 정리하고, 공유할 가치가 있는 내용만 BoI Wiki promotion 후보로 만들어줘. 원격 자동 업로드는 하지 마.
~~~

AI가 먼저 보여줄 것은 명령어가 아니라 자동화 범위, 자료 폴더, 원본 보존, 원격 업로드 꺼짐을 설명하는 짧은 설정 요약입니다. Python·Obsidian·MCP는 없어도 됩니다.

## 해결하는 문제

~~~text
대화·메일·웹·표·PDF·이미지·회의 메모
→ Local 원본과 SHA256
→ 기존 topic 검색
→ noop / 근거 추가 / 수정 / 이력 보존 교체 / 신규 / 확인 필요
→ 출처 있는 질문·답변과 재사용
→ 일반 knowledge 정제
→ 승인 전 Team/Public exact preview
~~~

문서마다 새 노트를 만드는 것이 목표가 아닙니다. 같은 주제는 기존 지식에 합치고, 중복은 만들지 않으며, 충돌은 history를 보존한 채 review queue로 보냅니다.

## 실제 합성 입력

`SYN-SB-001-v1`은 설명용 목록이 아니라 EML·CSV·PDF·PNG·Markdown·text로 된 실제 파일 20개입니다.

- byte-identical 중복 2개
- reviewed Friday 결정과 근거 없는 Thursday 충돌
- 누락 email checklist
- stale downstream FAQ
- 원격 projection에서 제거해야 하는 합성 경로·식별자
- 중단 후 10개부터 재개하는 seed

[Fixture 개요](fixtures/fixture.md) · [20개 파일 ledger](fixtures/source-pack.md) · [manifest](fixtures/manifest.json)

## 논리 역할

1. source-curator — 원본·hash·중복 inventory
2. memory-maintainer — 기존 topic·history·checkpoint 검색
3. knowledge-distiller — 유지관리 operation과 Local 문서 생성
4. grounded-query-analyst — 출처·반증·미확인 답변
5. privacy-reviewer — 독립 hard safety·quality 검증

Full·Reduced·Single-agent·No-team fallback 모두 같은 파일 계약과 reviewer gate를 사용합니다. 자세한 순서는 [Orchestrator](orchestrator.md)에 있습니다.

## 안전 경계

- 원본 파일 변경·이동·삭제 금지
- 원시 대화 transcript 기본 저장 금지
- evidence·capture·agent-memory 직접 promotion 금지
- MCP 연결만으로 Local Private 업로드 금지
- Team/Public는 sanitized preview와 exact hash를 본 뒤 별도 승인
- Local 경로·식별자·Local BoI ID·raw bytes의 projection 포함 0건

## 현재 검증 상태

현재 Codex에서 일곱 가지 핵심 여정을 한 차례씩 비교 검증했고, 보존된 결과에서는 Harness를 사용한 쪽이 baseline보다 나았습니다. 하지만 한 runtime의 단일 실행만으로 전사 배포 품질이나 반복 안정성을 증명할 수는 없습니다.

- 현재 등급: `community`
- 확인됨: Codex 단일 반복의 설정·기억·중복·교정·자료 정리·충돌·재개 여정
- 아직 확인 필요: 남은 공유 여정, Claude 반복, 비개발자 Acceptance, 실제 BoI Wiki contract
- Reference·production-ready 주장: 하지 않음

실행별 hash, assertion, blind comparison, 실패 이력과 미검증 항목은 일반 사용 절차와 분리한 [관리자 BENCHMARK](evals/BENCHMARK.md)에 보존합니다.

## 다음

- 처음 실행: [비개발자 Walkthrough](walkthrough/01-run.md)
- 출력 개발자: [Output contract](expected/OUTPUT-CONTRACT.md)
- 배포 관리자: [검증 protocol](evals/PROTOCOL.md) · [BENCHMARK](evals/BENCHMARK.md)
