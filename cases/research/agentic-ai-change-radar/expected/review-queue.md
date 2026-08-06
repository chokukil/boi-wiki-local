# Expected review queue

| Priority | Item | Why human Review is required | Next validation |
|---|---|---|---|
| high | AAI-004 current MCP authorization guidance | normative security guidance가 version 사이에 바뀌었음 | 현재 MCP spec 원문과 구현 대상 version 확인 |
| high | AAI-005 SK하이닉스 적용 가설 | 공개 자료만으로 내부 ACL, data boundary, 운영효과를 알 수 없음 | 승인된 내부 validation question과 안전한 pilot 범위 정의 |
| medium | AAI-003 T0 roadmap retirement | history 보존과 current guidance 분리가 필요 | 현재 TypeScript SDK version과 support status 확인 |
| medium | AAI-006 visual orchestration option | product announcement은 비교 효과 evidence가 아님 | 단순 composable baseline과 동일 eval로 비교 |

Reviewer는 T0/T1 source record와 manifest부터 읽고 producer 요약으로 self-approval하지 않습니다.
