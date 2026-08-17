# 세 Golden Journey — BoI Wiki promotion 상태

이 폴더는 Local·Case 지식이 BoI Wiki 조직 지식으로 넘어가는 경계를 보여주는 **전송 전 preview**다. MCP 조회 가능 여부와 promotion 권한은 별개이며, 어떤 파일도 원격 endpoint로 제출하지 않는다.

| Case | 현재 지식 상태 | preview 상태 | 이유 |
|---|---|---|---|
| AI Radar | public research revision 1 승인 | exact sanitized candidate 생성 가능 | 승인 범위 안의 공개 atomic claim만 사용 |
| FAB Logistics Digital Twin | Community baseline + 미승인 update 후보 | blocked | domain review와 candidate 승인 없음 |
| Scientific Foundation Model | Community baseline + 미승인 update 후보 | blocked | scientific review와 candidate 승인 없음 |

[AI Radar sanitized candidate](ai-radar-revision1-public-candidate.md)는 raw source, evidence, 개인 결정과 조직별 적용 추정을 포함하지 않는다. [preview receipt](ai-radar-revision1-public-preview.json)은 candidate hash, source, reviewer, target과 차단 조건을 고정하며 `approved`, `submitted`, `remote_submit_allowed`를 모두 false로 유지한다.

나머지 두 Case의 [eligibility receipt](pending-case-eligibility.json)은 현재 왜 promotion할 수 없는지 기록한다. 사람 Review가 끝나더라도 새 sanitized candidate와 exact preview를 다시 만들어야 하며, 기존 receipt를 재사용할 수 없다.

실제 BoI Wiki validator와 endpoint round trip은 접근 가능한 배포 환경에서 별도 검증해야 한다. 현재 상태는 `pending-external-system`이다.
