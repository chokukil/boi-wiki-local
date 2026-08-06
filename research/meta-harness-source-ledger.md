# Meta Harness source ledger

확인일: 2026-08-02

이 문서는 BoI Wiki Local 3.0의 구조적 기준이 어디서 왔고 무엇을 그대로 채택하지 않았는지 기록합니다. 외부 저장소의 문구·템플릿·도메인 산출물을 복제하지 않고 운영 원칙만 BoI 계약에 맞게 번역합니다.

## Harness

- 원문: [revfactory/harness 한국어 README](https://github.com/revfactory/harness/blob/main/README_KO.md)
- 감사 snapshot: 2026-08-02 기준 commit `cceac68ea1d0ad198ef4b7b906cd238375836387`.
- 확인 내용: 도메인 설명을 팀 아키텍처와 Skill로 전환하는 Meta-Factory, pipeline·fan-out/fan-in·specialist pool·generate-validate·supervisor·hierarchical delegation 패턴, progressive disclosure, trigger 검증, dry run, with/without 비교를 제시합니다.
- 역할 판정: 이것이 **Meta Harness Factory** 기준입니다. 기존 자산 감사, 생성·확장·유지보수 모드, 아키텍처 선택, agent·Skill 중복 방지, progressive disclosure, orchestration, with/baseline 검증, feedback 기반 진화를 `boi-harness-builder`에 적용합니다.
- 채택: 한 문장 진입, 논리적 역할, 명시적 orchestration, 독립 reviewer, 기존 Skill 재사용, Case 진화 feedback.
- 비채택: 모든 업무마다 새 agent·Skill을 생성하는 방식. BoI Wiki Local은 기존 범용 Skill 조합을 우선하고 반복 증거가 있을 때만 generic Skill 승격을 검토합니다.
- 주의: README에 인용된 품질 수치는 저자 자체 실험으로 표시되어 있으므로 우리 품질 주장에 전용하지 않습니다.

## Harness-100

- 원문: [revfactory/harness-100](https://github.com/revfactory/harness-100)
- 역할 판정: 이것은 Meta Factory가 아니라 **실사례·산출물 예시 모음**입니다. 우리 저장소에서는 `cases/`가 이 역할을 맡습니다.
- 확인 내용: 한국어·영어 각 100개 사례, 사례당 4–5개 전문 역할, orchestrator, 2–3개 확장 Skill, structured output, dependency DAG, 오류 처리, Full·Reduced·Single-agent, 정상·기존 파일·오류 테스트, should/not-trigger 경계를 품질 기준으로 제시합니다.
- 저장소 트리 정적 감사: 2026-08-02 기준 commit `8e8d35c6a19166614d1af1df85512266d51121ae`의 한국어 100개 패키지·906개 Markdown을 확인했습니다. 역할 수는 5개 89건·4개 11건, Skill 수는 3개 85건·4개 15건이며 모든 패키지에 별도 역할 파일, 오류 처리, test scenario, trigger 설명이 있습니다.
- evidence 한계: 해당 snapshot의 한국어 패키지는 Markdown 이외 파일 0개이며 저장된 runtime run, assertion 결과, blind comparison, 반복 편차 evidence가 없습니다. 따라서 “production-grade” 표시는 정적 패키지 품질 주장으로만 참고합니다.
- 채택: 위 정적 구조를 Community Case의 최소 골격으로 사용합니다. 역할을 한 문서에만 모으지 않고 역할별 progressive-disclosure card를 제공하며, 채팅 요약 대신 file·SHA256·unknown·blocker가 있는 `boi-local-case-handoff/v1`을 사용합니다.
- 추가 기준: 외부 컬렉션의 ready-to-use 표시는 우리 `reference` 증거로 간주하지 않습니다. BoI Reference는 Codex·Claude 3회 반복, baseline, 객관 assertion, blind comparison, 안정성, 비개발자 Acceptance, 실제 BoI Wiki validator를 별도로 요구합니다.

## 두 저장소를 우리 구조에 대응

```text
revfactory/harness      -> boi-harness-builder Meta Factory
revfactory/harness-100  -> cases/ 실사례·품질 기준 모음
LLM Wiki 운영 원칙      -> Flagship Second Brain 횡단 Harness
BoI Wiki 계약           -> OKF 0.1·BoI Profile·ACL·revision·promotion 최상위 경계
```

Second Brain은 Meta Factory의 대체물이 아닙니다. Meta Factory가 만든 모든 Case가 필요에 따라 연결할 수 있는 핵심 횡단 Harness이며, 그 자체도 가장 깊게 검증하는 Flagship Case를 가집니다.

## Karpathy LLM Wiki와 후속 논의

- 원문: [Karpathy llm-wiki Gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- 채택: raw source → schema-bound ingest → compiled Wiki → query → lint → review, 기존 엔터티와의 중복 해결, 지속적인 지식 유지관리.
- 후속 구현 사례에서 참고한 위험: 모든 대화를 저장하는 것보다 장기 가치 선별이 어렵고, 새 finding은 매번 새 문서가 아니라 기존 문서를 보강·교정해야 하며, 근거가 없는 질문에는 Wiki가 충분하지 않다고 답할 수 있어야 합니다.
- BoI 번역: OKF 0.1 + BoI Profile이 schema 경계를 지배하고, raw transcript 기본 저장 금지, source hash, `noop`·근거 추가·교정·검토 보류, 반증·미확인, direct promotion 차단을 적용합니다.
- 비채택: 외부 구현의 자체 frontmatter, wikilink-only graph, 자동 session capture, provider·plugin 종속 구조.

## 우리 품질 주장 규칙

1. 정적 구조가 좋다는 사실과 실제 결과 품질이 좋다는 주장을 분리합니다.
2. `community`는 schema·link·privacy·fixture·trigger 검사를 통과한 후보입니다.
3. `verified`는 최소 한 runtime의 재현 가능한 실행 evidence가 필요합니다.
4. `reference`는 저장된 양 runtime benchmark와 hard gate를 모두 통과해야 합니다.
5. 실행하지 않은 비교 결과, 가상의 사용자 Acceptance, 가상의 BoI Wiki validator 통과를 채우지 않습니다.
