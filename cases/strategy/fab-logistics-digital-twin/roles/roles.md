# Roles — FAB Logistics Digital Twin

각 역할은 `boi-local-case-handoff/v1`으로 source hash, output hash, unknown, blocker와 review question을 넘깁니다.

| Role | 책임 | 주 산출물 | Exit criteria | Hard fail |
|---|---|---|---|---|
| research-coordinator | 공개 범위, 제외 범위, 의사결정 질문과 검토 주기를 고정 | `intermediate/request-contract.json` | 유료 표준·내부 데이터·벤더 선정이 제외됨 | 비공개 조건 또는 normative field 추정 |
| standards-source-researcher | SEMI 공개 요약과 제조·물류 digital twin 1차 자료를 manifest로 수집 | `intermediate/source-manifest.json` | GEM300 공개 범위와 접근 제한이 분리됨 | 유료 전문을 확인했다고 주장 |
| twin-model-analyst | Carrier·Substrate·Control Job, 물류 자산·상태·event·simulation을 capability map으로 연결 | `intermediate/twin-capability-map.md` | 관측 사실, 표준 개념, vendor claim과 가설이 구분됨 | 공개 case signal을 SK하이닉스 성과로 일반화 |
| ontology-workflow-curator | Object·Link·Action 후보와 human checkpoint가 있는 pilot hypothesis 작성 | `ontology-map.md와 pilot-hypotheses.md` | 각 Action은 권한·검증·rollback unknown을 가짐 | 실제 action 실행 또는 Palantir 종속 schema 확정 |
| independent-reviewer | source→표준 개념→twin→ontology→pilot 추론 사슬을 독립 검토 | `reviewer-report.json` | 추론 leap와 내부 검증 필요 항목이 명시됨 | 벤더 문서만으로 효과·적합성 승인 |

Independent Reviewer는 producer 요약이 아니라 source manifest와 원문 record부터 읽습니다. Single-agent에서도 reviewer pass를 별도로 시작하며 중요한 의미 변경은 사람 Review 없이는 승인하지 않습니다.
