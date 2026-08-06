# Roles — SK하이닉스 Agentic AI Change Radar

각 역할은 `boi-local-case-handoff/v1`으로 source hash, output hash, unknown, blocker와 review question을 넘깁니다.

| Role | 책임 | 주 산출물 | Exit criteria | Hard fail |
|---|---|---|---|---|
| research-coordinator | 요청을 일곱 도구 중 하나로 라우팅하고 범위·성공 조건·phase exit를 고정 | `intermediate/request-contract.json` | 도구, 범위, 기준 시점, reviewer와 주문형 산출물이 명시됨 | claim 승인 또는 DeepResearch 무승인 실행 |
| source-researcher | 공식 문서·저장소·원 논문을 우선 수집하고 manifest와 접근 제한을 기록 | `intermediate/source-manifest.json` | 모든 source에 URL, date, checked scope, hash와 verification level이 있음 | snippet을 확정 근거로 사용하거나 읽지 못한 전문을 읽었다고 주장 |
| evidence-analyst | claim, evidence, counterevidence, contradiction과 unknown을 분리 | `intermediate/evidence-matrix.md` | material claim마다 양방향 evidence와 unknown이 연결됨 | 기존 판단 덮어쓰기 또는 SK하이닉스 비공개 조건 추정 |
| change-curator | delta를 분류하고 이전 snapshot, 이유, downstream 영향과 다음 검토일을 보존 | `change-set.md와 review-queue.md` | 모든 변화가 허용 delta enum과 source ref를 가짐 | confidence·폐기·contradiction을 독단 확정하거나 변화 없는데 보고서 생성 |
| independent-reviewer | 원문 record와 manifest부터 재검토해 approve·revise·partial·blocked 판정 | `reviewer-report.json` | 중요 claim과 contradiction의 evidence locator가 독립 확인됨 | producer 요약만 읽거나 self-approval |

Independent Reviewer는 producer 요약이 아니라 source manifest와 원문 record부터 읽습니다. Single-agent에서도 reviewer pass를 별도로 시작하며 중요한 의미 변경은 사람 Review 없이는 승인하지 않습니다.
