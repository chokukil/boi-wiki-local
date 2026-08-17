# 범위와 판정법

## 시간 경계

- 기준 지식: 2025-11-30까지 공개된 자료만 사용해 회고적으로 재구성한다.
- 업데이트 후보: 2025-12-01부터 2026-08-08까지 공개·수정된 자료를 사용한다.
- 현재 시점의 사실을 기준 지식에 소급하지 않는다.
- 웹 페이지가 계속 바뀌는 경우 확인 시점의 bytes SHA256과 확인 범위를 함께 기록한다.

## 두 축

### Agentic AI

runtime·harness, orchestration, multi-agent, tool use, MCP·A2A, memory·context, evaluation·observability, permission·sandbox, durable execution·recovery를 다룬다.

### Physical AI — 제조 중심

VLA·robotics foundation model, world model, simulation·synthetic data·sim-to-real, 자율 물류, Digital Twin·virtual commissioning, OpenUSD·AAS·OPC UA, ontology·Object-Link-Action, 물리 action의 안전과 human-in-the-loop를 다룬다.

## 발견과 근거의 분리

| 단계 | 의미 | claim 사용 |
|---|---|---|
| 관찰 | 커뮤니티·Trending·Daily Papers에서 발견 | 불가 |
| 원문 확인 | 공식 문서·원 논문·공식 저장소 범위를 확인 | 확인 범위 안에서 가능 |
| 지식 후보 | 기존 지식과 비교해 재사용 가능한 문장으로 정제 | review 전 후보 |
| 검토 필요 | 충돌·과장·접근 제한·중요 판단이 있음 | 사람 검토 필요 |
| 제외 | 중복, 광고성, 범위 밖, 원문 확인 실패 | 불가 |

근거 수준은 `signal`, `primary-checked`, `corroborated`, `review-required`, `unknown`을 사용한다. 중요한 비벤더 claim은 가능한 경우 공식 문서와 논문·표준·코드 중 독립된 두 근거로 보강한다.

## 원 출처 확인 규칙

- 검색 snippet은 발견에만 사용하고 claim의 단독 근거로 삼지 않는다.
- 논문은 arXiv ID, version, 제출·수정일, abstract/full-text 확인 범위, peer-review·코드·데이터 공개 여부를 분리한다.
- 이번 실행에서 arXiv 논문은 abstract 페이지를 확인했다. PDF 전문을 검증했다고 주장하지 않는다.
- GitHub는 canonical URL과 2026-08-08에 읽은 HEAD commit을 기록한다. 별 수와 Trending 순위는 성숙도 증거가 아니다.
- 벤더의 성능·효과 문장은 벤더 주장으로 표시한다. 독립된 재현 결과 없이 일반화하지 않는다.
- 시뮬레이션·testbed·데모·Early Access는 실환경 양산 성과와 분리한다.

## 중복 제거

- 논문: arXiv ID
- 저장소: canonical GitHub URL
- 제품·사양: 공식 release 또는 specification revision
- 같은 원 출처가 여러 발견 채널에 나타나면 신호 관찰은 보존하되, 지식 근거는 하나의 source ID로 연결한다.

## 변화 판정

`신규`, `강화`, `수정`, `충돌`, `stale`, `폐기 검토`, `unknown`으로 분류한다. 이전 판단·새 근거·반대 근거·변경 이유·영향을 함께 보존한다. 자료가 추가됐더라도 채택 판단이 달라지지 않으면 지식 변화로 세지 않는다.

## 제한

- 공개 자료만 사용했다.
- SK하이닉스 내부 설비, 데이터 품질, 보안 정책, 비용과 성과를 추정하지 않았다.
- 코드 실행·benchmark 재현·로봇 실험·현장 검증은 수행하지 않았다.
- 이 결과는 Community 수준의 research candidate이며 Verified, Reference 또는 production-ready가 아니다.

