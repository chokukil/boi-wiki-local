# Deterministic synthetic source pack — Flagship Second Brain

Fixture ID: `SYN-SB-001-v1`

모든 파일은 합성이며 실제 사용자 대화, 사내 업무, 고객, 제품, 설비, 인증정보를 포함하지 않습니다. `manifest.json`의 20개 파일과 SHA256이 평가 입력의 전부입니다. `source_count`는 설명 문단 수가 아니라 실제 파일 수입니다.

| # | 실제 파일 | 자료 유형 | 평가할 동작 |
|---:|---|---|---|
| 1 | [decision chat](sources/01-decision-chat.txt) | 대화에서 추출한 합성 결정 | 장기 가치와 일회성 내용 분리 |
| 2 | [project update](sources/02-project-update.eml) | EML | 결정 보강과 누락 첨부 표시 |
| 3 | [public web clip](sources/03-public-web-clip.md) | Web clip Markdown | 공개 출처와 해석 분리 |
| 4 | [action register](sources/04-action-register.csv) | CSV | action과 지식이 아닌 항목 분리 |
| 5 | [operating guide](sources/05-operating-guide.pdf) | 2페이지 PDF | PDF 원본 보존과 핵심 원칙 정제 |
| 6 | [whiteboard](sources/06-whiteboard-decisions.png) | PNG | 이미지 원본과 설명·미확인 분리 |
| 7 | [meeting note](sources/07-meeting-note.md) | 회의 메모 | 결정·근거·미해결·Action 정제 |
| 8 | [conflicting review day](sources/08-conflicting-review-day.md) | 상충 메모 | reviewed 사실 자동 덮어쓰기 차단 |
| 9 | [duplicate web clip](sources/09-public-web-clip-copy.md) | 중복 파일 | 동일 SHA256 재생성 방지 |
| 10 | [review day reconfirmation](sources/10-review-day-reconfirmation.txt) | 후속 대화 | 기존 문서에 evidence 추가 |
| 11 | [research note](sources/11-research-note.md) | 조사 메모 | 근거 없는 주장 격리 |
| 12 | [SOP draft](sources/12-sop-draft.md) | 미승인 SOP | 실행·직접 promotion 차단 |
| 13 | [onboarding FAQ](sources/13-onboarding-faq.md) | FAQ | 오래된 downstream 지식 탐지 |
| 14 | [read-only API note](sources/14-readonly-api-note.md) | API 메모 | read/write 경계 보존 |
| 15 | [incident retrospective](sources/15-incident-retrospective.md) | 회고 | 관찰·기여 요인·반증 분리 |
| 16 | [dictionary candidate](sources/16-dictionary.md) | Dictionary 후보 | preferred term·alias 검토 |
| 17 | [weekly report](sources/17-weekly-report.md) | 주간보고 | 성과·근거·리스크 연결 |
| 18 | [sensitive review note](sources/18-sensitive-review-note.md) | 민감정보 검토 fixture | Local 경로·식별자 projection 차단 |
| 19 | [recurrence note](sources/19-recurrence-note.md) | 재발 후보 | fingerprint 오탐 방지 |
| 20 | [promotion candidate](sources/20-promotion-candidate.md) | promotion 입력 | sanitized exact preview |

3번과 9번은 의도적으로 byte-identical합니다. 이를 두 문서로 만들면 중복 제거 assertion이 실패합니다. 8번은 reviewed Friday 결정을 근거 없는 Thursday 주장으로 교체하려는 충돌입니다. 18번의 식별자와 경로는 합성이어도 원격 projection에서 제거되어야 합니다.

생성·검사는 관리자용 `scripts/build_second_brain_fixture.py`가 담당합니다. 일반 사용자는 이 스크립트나 Python을 필요로 하지 않습니다.
