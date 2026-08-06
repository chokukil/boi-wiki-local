# Roles — Scientific Foundation Model Knowledge

각 역할은 `boi-local-case-handoff/v1`으로 source hash, output hash, unknown, blocker와 review question을 넘깁니다.

| Role | 책임 | 주 산출물 | Exit criteria | Hard fail |
|---|---|---|---|---|
| research-coordinator | 연구 질문, discipline, validation level, review trigger와 주문 산출물을 고정 | `intermediate/request-contract.json` | 근본 법칙과 빠른 동향의 검토 주기가 분리됨 | 모든 분야를 하나의 foundation claim으로 합침 |
| paper-source-researcher | 원 논문, 정정·철회, 코드·데이터와 후속 연구를 우선 수집 | `intermediate/source-manifest.json` | abstract/full text, peer-review, version, access가 구분됨 | abstract-only를 full-text verified로 표시 |
| scientific-evidence-analyst | 법칙, model assumption, prediction, benchmark, physical validation, 반례를 분리 | `intermediate/scientific-evidence-matrix.md` | 주장마다 적용 domain과 falsifier가 있음 | 성능을 물리적 정확성 또는 인과로 동일시 |
| change-curator | 후속·정정·재현으로 바뀐 claim만 delta로 기록하고 stable knowledge는 재작성하지 않음 | `change-set.md와 review-queue.md` | revision reason과 다음 검토 trigger가 source-linked | 새 논문 수만으로 confidence 상향 또는 negative result 삭제 |
| independent-reviewer | 논문 record와 실제 확인 범위부터 prediction·반례·재현 상태를 검토 | `reviewer-report.json` | 근본 법칙, 모델 가정, empirical claim과 unknown이 구분됨 | producer 해석 또는 인용 횟수만으로 승인 |

Independent Reviewer는 producer 요약이 아니라 source manifest와 원문 record부터 읽습니다. Single-agent에서도 reviewer pass를 별도로 시작하며 중요한 의미 변경은 사람 Review 없이는 승인하지 않습니다.
