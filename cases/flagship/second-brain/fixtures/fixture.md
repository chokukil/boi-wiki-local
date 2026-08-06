# Fixture — SYN-SB-001-v1

이 fixture는 한 구성원이 대화·메일·웹·CSV·PDF·이미지·회의 메모를 Local Private Second Brain에 누적하고, 충돌과 중복을 처리한 뒤 조직지식 후보를 만드는 3주간의 합성 여정입니다.

## 고정 사실

- 검토 일정의 reviewed 결정은 Friday 15:00입니다.
- Thursday 15:00 주장은 출처가 없는 충돌입니다.
- `Blue Ledger`는 이전 명칭이고 `Atlas Ledger`가 검토 중인 preferred term입니다.
- 이메일이 언급한 checklist는 입력에 없습니다. 내용을 추정하면 실패입니다.
- 공개 Web clip 두 파일은 byte-identical 중복입니다.
- Local 경로와 식별자가 있는 자료는 합성이라도 remote projection에서 제거합니다.

## 시간축

1. Day 1: 대화·메일·회의 결정과 첫 knowledge 작성
2. Day 2: 여러 형식 20개 자료의 원본 보존·중복 제거·기존 지식 보강
3. Day 3: 상충 주장·stale FAQ·누락 checklist를 review queue로 분리
4. Week 3: recurrence note로 기존 지식을 검색하고 일반 knowledge를 Team preview로 정제

## 입력 경계

평가 런은 [manifest](manifest.json)에 기록된 파일만 근거로 사용할 수 있습니다. 모델의 일반 지식은 fixture의 누락 사실을 채우는 근거가 아닙니다. 모든 입력은 합성이며 실제 업무 표준을 주장하지 않습니다.

다음: [20개 실제 파일과 의도](source-pack.md) · [실행 프로토콜](../evals/PROTOCOL.md)
