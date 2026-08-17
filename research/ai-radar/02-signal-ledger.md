# 발견 신호 원장

발견 시각은 모두 2026-08-08 KST다. `원문 확인`은 링크된 공식 원 출처를 직접 열어 확인했다는 뜻이며, 커뮤니티 설명을 근거로 승격했다는 뜻이 아니다.

각 행의 ID·발견 링크·축·새로움·상태는 이 원장에, 최종 원 출처의 날짜·revision·확인 범위·hash·근거 수준은 [source manifest](03-source-manifest.json)에, 기존 판단을 바꿀 가능성과 다음 질문은 [업데이트 후보](08-update-candidate.md)와 [review queue](10-review-queue.md)에 연결했다. shortlist로 승격하지 않은 관찰은 최종 원 출처가 확인될 때까지 claim에 사용하지 않는다.

## GeekNews 발견 신호

| ID    | 발견 링크                                                                  | 축        | 무엇을 확인할 후보였나                | 상태    |
| ----- | ---------------------------------------------------------------------- | -------- | --------------------------- | ----- |
| GN-01 | [Physical AI 머니볼](https://news.hada.io/topic?id=31456)                 | Physical | 로봇 데이터 품질·실험 설계             | 원문 확인 |
| GN-02 | [Physical AI 기업 동향](https://news.hada.io/topic?id=25803)               | Physical | CES 발표와 실제 성숙도 분리           | 지식 후보 |
| GN-03 | [agentic E2E testing](https://news.hada.io/topic?go=comments&id=30744) | Agentic  | trajectory 평가 수요            | 원문 확인 |
| GN-04 | [coding agent workflow](https://news.hada.io/comment?id=51742)         | Agentic  | harness 실무 패턴               | 관찰    |
| GN-05 | [Odysseus workspace](https://news.hada.io/topic?id=30217)              | Agentic  | self-hosted agent workspace | 원문 확인 |
| GN-06 | [long-running agents](https://news.hada.io/topic?id=29153)             | Agentic  | session handoff·resume      | 지식 후보 |
| GN-07 | [production agent 운영](https://news.hada.io/topic?id=24091)             | Agentic  | 운영 상태·관찰성                   | 관찰    |
| GN-08 | [coding agent 비교](https://news.hada.io/topic?id=26920)                 | Agentic  | workflow 차이                 | 관찰    |
| GN-09 | [Stash memory layer](https://news.hada.io/topic?go=comments&id=28917)  | Agentic  | memory persistence          | 원문 확인 |
| GN-10 | [Hephaestus agent OS](https://news.hada.io/topic?id=31044)             | Agentic  | durable runtime             | 원문 확인 |
| GN-11 | [Kimi agent benchmark](https://news.hada.io/topic?id=30441)            | Agentic  | benchmark 과장 가능성            | 검토 필요 |
| GN-12 | [agent economy](https://news.hada.io/topic?id=29171)                   | 교차       | agent 간 거래·권한               | 관찰    |
| GN-13 | [WordPress MCP adapter](https://news.hada.io/topic?id=26453)           | Agentic  | MCP 생태계 확장                  | 원문 확인 |
| GN-14 | [Chrome WebMCP](https://news.hada.io/topic?id=29693)                   | Agentic  | 브라우저 action 노출              | 검토 필요 |
| GN-15 | [Google agent trends](https://news.hada.io/topic?id=25511)             | Agentic  | 벤더 전망                       | 제외    |
| GN-16 | [오픈소스 AI 동향](https://news.hada.io/topic?id=31538)                      | 교차       | 공개 생태계 후보                   | 관찰    |
| GN-17 | [Cursor 3.0](https://news.hada.io/topic?id=28222)                      | Agentic  | coding agent UI             | 원문 확인 |
| GN-18 | [Deep Research Agent API](https://news.hada.io/topic?id=28815)         | Agentic  | managed research agent      | 원문 확인 |
| GN-19 | [.NET 10 agent framework](https://news.hada.io/topic?id=24321)         | Agentic  | framework 통합                | 지식 후보 |
| GN-20 | [Muse Spark 1.1](https://news.hada.io/topic?id=31279)                  | Physical | world model 후보              | 원문 확인 |
| GN-21 | [YC agent RFS](https://news.hada.io/topic?id=29009)                    | Agentic  | 시장 관심                       | 제외    |
| GN-22 | [skills와 MCP 논의](https://news.hada.io/topic?id=24673)                  | Agentic  | capability packaging        | 검토 필요 |
| GN-23 | [Google I/O AI 발표](https://news.hada.io/topic?id=29729)                | 교차       | 공식 발표 후보                    | 원문 확인 |
| GN-24 | [agent 안전 논의](https://news.hada.io/topic?id=24091)                     | Agentic  | 권한·감사                       | 원문 확인 |

### GeekNews에서 지식 후보로 승격한 연결

- GN-03 → A07·R03: final output이 아닌 trajectory·outcome 평가
- GN-06 → A06·A08: 장기 작업의 handoff와 evaluator harness
- GN-19 → A12·G07: Microsoft Agent Framework 상태 변화
- GN-22 → A09·G06: capability packaging과 MCP 사양 변화
- GN-23 → A10·P01: agent interoperability와 Physical AI 공식 발표
- GN-24 → A05·R02: permission과 trajectory assurance

나머지 GeekNews 관찰은 source manifest에 연결되지 않았으며 claim의 근거로 사용하지 않았다.

## GitHub·Trending 발견 신호

발견 채널은 [GitHub Trending](https://github.com/trending)과 공개 repository search다. 최종 원 출처는 각 행의 canonical repository이며, 성숙도는 Trending 순위가 아니라 source manifest의 revision·release 상태·license 확인 범위로 판정했다.

| ID | 원 출처 | 축 | 확인한 revision | 상태 |
|---|---|---|---|---|
| GH-01 | [GitHub Trending](https://github.com/trending) | 교차 | 2026-08-08 화면 | 관찰 |
| GH-02 | [openai-agents-python](https://github.com/openai/openai-agents-python) | Agentic | `fd4db5609c2f` | 지식 후보 |
| GH-03 | [openai-agents-js](https://github.com/openai/openai-agents-js) | Agentic | `ccb85cfada2b` | 원문 확인 |
| GH-04 | [google/adk-python](https://github.com/google/adk-python) | Agentic | `3d2975025bfe` | 지식 후보 |
| GH-05 | [google/adk-java](https://github.com/google/adk-java) | Agentic | `e5aba3aa08c5` | 지식 후보 |
| GH-06 | [A2A](https://github.com/a2aproject/A2A) | Agentic | `19598c4baddb` | 지식 후보 |
| GH-07 | [MCP specification](https://github.com/modelcontextprotocol/modelcontextprotocol) | Agentic | `9d4a9115126f` | 검토 필요 |
| GH-08 | [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) | Agentic | `5eb3eb745e16` | 지식 후보 |
| GH-09 | [LangGraph](https://github.com/langchain-ai/langgraph) | Agentic | `fde306897067` | 원문 확인 |
| GH-10 | [NVIDIA Isaac-GR00T](https://github.com/NVIDIA/Isaac-GR00T) | Physical | `b9955401d50c` | 검토 필요 |
| GH-11 | [NVIDIA Cosmos](https://github.com/nvidia/cosmos) | Physical | `f76cd8705dc0` | 지식 후보 |
| GH-12 | [LeRobot](https://github.com/huggingface/lerobot) | Physical | `22bd7a2f489b` | 원문 확인 |
| GH-13 | [openpi](https://github.com/Physical-Intelligence/openpi) | Physical | `15a9616a0094` | 원문 확인 |
| GH-14 | [ECC](https://github.com/affaan-m/ECC) | Agentic | `59a99d669f54` | 관찰 |
| GH-15 | [superpowers](https://github.com/obra/superpowers) | Agentic | `44c9b2d6e889` | 관찰 |
| GH-16 | [airi](https://github.com/moeru-ai/airi) | Physical | `c10d16ec8d63` | 관찰 |
| GH-17 | [Odysseus](https://github.com/pewdiepie-archdaemon/Odysseus) | Agentic | `e4fa4ae5dd1d` | 관찰 |

## 논문·Daily Papers 발견 신호

발견 채널은 [Hugging Face Daily Papers](https://huggingface.co/papers)와 [arXiv](https://arxiv.org)다. 최종 원 출처는 각 행의 arXiv record다. manifest에 승격된 R01~R08은 abstract page와 PDF bytes hash를 고정했지만, PDF 내용은 읽지 않았으므로 full-text checked로 표시하지 않았다. 나머지는 다음 radar에서 full text·코드·데이터를 확인할 관찰이다.

| ID | 원 논문 | 축 | 확인 범위 | 상태 |
|---|---|---|---|---|
| PA-01 | [Memory for Autonomous LLM Agents, 2603.07670](https://arxiv.org/abs/2603.07670) | Agentic | abstract·version | 지식 후보 |
| PA-02 | [AI Agent Systems survey, 2601.01743](https://arxiv.org/abs/2601.01743) | Agentic | abstract·version | 원문 확인 |
| PA-03 | [Agentic AI and Cybersecurity, 2601.05293](https://arxiv.org/abs/2601.05293) | Agentic | abstract·version | 검토 필요 |
| PA-04 | [Secure Agentic Web, 2603.01564](https://arxiv.org/abs/2603.01564) | Agentic | abstract·version | 검토 필요 |
| PA-05 | [Trajectory Assurance, 2608.01558](https://arxiv.org/abs/2608.01558) | 교차 | abstract·version | 지식 후보 |
| PA-06 | [AgenTRIM, 2601.12449](https://arxiv.org/abs/2601.12449) | Agentic | abstract·version | 원문 확인 |
| PA-07 | [Efficient Agents, 2601.14192](https://arxiv.org/abs/2601.14192) | Agentic | abstract·version | 원문 확인 |
| PA-08 | [AgentCompass, 2607.13705](https://arxiv.org/abs/2607.13705) | Agentic | abstract·version | 원문 확인 |
| PA-09 | [AgentCL, 2606.02461](https://arxiv.org/abs/2606.02461) | Agentic | abstract·version | 원문 확인 |
| PA-10 | [EvoMemBench, 2605.18421](https://arxiv.org/abs/2605.18421) | Agentic | abstract·version | 지식 후보 |
| PA-11 | [MemoryAgentBench, 2507.05257](https://arxiv.org/abs/2507.05257) | Agentic | abstract·version | 원문 확인 |
| PA-12 | [PM-Bench, 2607.12385](https://arxiv.org/abs/2607.12385) | Agentic | abstract·version | 지식 후보 |
| PA-13 | [AgentLAB, 2602.16901](https://arxiv.org/abs/2602.16901) | Agentic | abstract·version | 지식 후보 |
| PA-14 | [MCP·A2A governance gaps, 2606.31498](https://arxiv.org/abs/2606.31498) | 교차 | abstract·version | 검토 필요 |
| PA-15 | [Digital Twin AI, 2601.01321](https://arxiv.org/abs/2601.01321) | Physical | abstract·version | 지식 후보 |
| PA-16 | [explicit world model, 2603.13825](https://arxiv.org/abs/2603.13825) | Physical | abstract·version | 원문 확인 |
| PA-17 | [VLA review, 2510.07077](https://arxiv.org/abs/2510.07077) | Physical | abstract·version | 지식 후보 |
| PA-18 | [interactive digital twins, 2506.13761](https://arxiv.org/abs/2506.13761) | Physical | abstract·version | 원문 확인 |
| PA-19 | [GR00T N1, 2503.14734](https://arxiv.org/abs/2503.14734) | Physical | abstract·version | 지식 후보 |
| PA-20 | [VLA with world model, 2606.11618](https://arxiv.org/abs/2606.11618) | Physical | abstract·version | 원문 확인 |

## 공식 발표·표준 발견 신호

발견 채널은 공식 연구소·벤더 engineering blog, release note, 표준기관 문서다. 최종 원 출처와 관찰 hash는 source manifest의 A·P source ID로 연결한다.

| ID | 원 출처 | 축 | 의미 | 상태 |
|---|---|---|---|---|
| OF-01 | [OpenAI Responses API tools](https://openai.com/index/new-tools-for-building-agents/) | Agentic | tool runtime·tracing | 지식 후보 |
| OF-02 | [Anthropic effective agents](https://www.anthropic.com/engineering/building-effective-agents) | Agentic | workflow/agent 선택 | 지식 후보 |
| OF-03 | [Anthropic context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | Agentic | context curation | 지식 후보 |
| OF-04 | [long-running harness](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | Agentic | session handoff | 지식 후보 |
| OF-05 | [agent evals](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | Agentic | trajectory·outcome 평가 | 지식 후보 |
| OF-06 | [MCP 2026 release candidate](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/) | Agentic | tasks·apps·auth hardening | 검토 필요 |
| OF-07 | [ADK·A2A](https://developers.googleblog.com/en/agents-adk-agent-engine-a2a-enhancements-google-io/) | Agentic | agent interoperability | 지식 후보 |
| OF-08 | [Microsoft Agent Framework 1.0](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/) | Agentic | framework 통합·GA | 지식 후보 |
| OF-09 | [Gemini Robotics](https://deepmind.google/blog/gemini-robotics-brings-ai-into-the-physical-world/) | Physical | VLA·embodied reasoning | 지식 후보 |
| OF-10 | [NVIDIA manufacturing](https://www.nvidia.com/en-us/industries/manufacturing/) | Physical | simulation·factory claim | 검토 필요 |
| OF-11 | [Palantir Ontology](https://www.palantir.com/docs/foundry/ontology/overview) | 교차 | object·link·action layer | 검토 필요 |
| OF-12 | [OpenUSD](https://openusd.org/release/) | Physical | 3D scene interchange | 지식 후보 |
| OF-13 | [OPC UA for AAS](https://reference.opcfoundation.org/specs/OPC-30270/4.1) | Physical | asset representation interoperability | 지식 후보 |
| OF-14 | [IDTA AAS Release 26-01](https://industrialdigitaltwin.org/en/content-hub/aasspecifications) | Physical | metamodel·API·security specs | 지식 후보 |
| OF-15 | [DTC cognitive orchestration testbed](https://www.digitaltwinconsortium.org/initiatives/digital-twin-testbeds/cognitive-network-orchestration/) | 교차 | agent-based twins·ontology testbed | 검토 필요 |

## 집계

- 발견 신호 76개를 기록했다. 같은 원 출처를 가리키는 관찰은 source manifest에서 하나로 중복 제거했다.
- 44개 원 출처를 shortlist하고 직접 확인했다.
- 제외 3개는 시장 전망·중복·원문 대비 정보 증가가 없는 항목이다.
- 원문 확인 범위와 bytes hash는 [source manifest](03-source-manifest.json)에 고정했다.
