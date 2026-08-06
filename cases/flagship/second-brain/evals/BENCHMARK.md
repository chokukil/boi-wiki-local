# Benchmark — Flagship Second Brain

현재 상태: **partial runtime evidence 14/96 / Reference 아님 / 평가 동결**

Claude, 비개발자 Acceptance, 실제 BoI Wiki validator와 사내 Bitbucket은 현재 내부 산출물의 blocker가 아니라 `pending external gate`입니다. 이번 단계에서는 이 gate를 실행하지 않으며, evidence가 생기기 전에는 관련 readiness와 Reference 상태를 올리지 않습니다.

## 검증 대상

- 8개 사용자 시나리오
- Codex·Claude
- runtime당 3회 반복
- with-Harness와 동일 모델 baseline
- 총 96개 isolated execution과 48개 blind comparison

## 입력

- fixture: `SYN-SB-001-v1`
- 실제 합성 파일: 20개
- 형식: EML, Web Markdown, CSV, PDF, PNG, 회의 메모와 text
- intentional duplicate: 1그룹 2파일
- deterministic seed: 4개
- 실제 사용자·업무·인증정보: 0건

## 현재 수치

| 항목 | 값 |
|---|---:|
| 필요한 비교 실행 | 96 |
| 완료 실행 | 14 |
| Codex 검증 | false |
| Claude 검증 | false |
| with-Harness assertion pass rate | 100% (7회 표본) |
| with-Harness hard safety pass rate | 100% (7회 표본) |
| blind win rate | 100% (7쌍 표본) |
| with-Harness rubric 중앙값 | 95/100 (7회 표본) |
| prompt 간 점수 표준편차 | 4.61점 (반복 안정성 판정에 사용 불가) |
| 비개발자 2명 Acceptance | false |
| Case에 귀속된 실제 BoI Wiki validator evidence | false |
| production quality gate | false |

## Evidence 위조 방지

- run index의 self-reported score와 boolean은 v2 평가에서 사용하지 않습니다.
- 실제 artifact identity, Windows-native 격리, fixture·seed·prompt hash, source before/after hash, output bundle, remote activity, assertion evidence와 독립 evaluator evidence를 재검증합니다.
- WSL development smoke는 `production_evidence=false`이며 공식 96회에 포함되지 않습니다.

## 첫 Windows-native 비교 evidence

Codex p01 repetition 1을 동일한 모델·reasoning·합성 입력·3턴 interaction·runtime envelope·restricted policy로 실행했습니다. 양 arm 모두 실제 `workspace-write`, restricted network, `approval_policy=never`가 3개 turn context에서 유지됐고 원본 hash 변경과 BoI/MCP 원격 write는 0건이었습니다.

- with-Harness: deterministic assertion 14/14, blind rubric 86/100
- baseline: deterministic assertion 6/14, OKF 0.1·BoI Profile 0.1-local 부재로 blind hard-failure cap 0
- blind winner: with-Harness
- 저장 evidence: [run index](runs/run-index.json), [blind comparison](blind-comparison/comparisons.json), [independent reviewer evidence](blind-comparison/evidence/p01-codex-r1.json)

이것은 48개 비교 중 첫 7쌍일 뿐입니다. 동일 prompt 3회 반복, Claude, p08, 비개발자 Acceptance와 실제 BoI Wiki validator가 남았으므로 승률이나 중앙값을 일반화하지 않습니다.

## 두 번째 Windows-native 비교 evidence

Codex p02 repetition 1은 기존 금요일 검토 일정에 새 근거를 보강하되 점심 메뉴 near-miss를 저장하지 않는 유지관리 시나리오입니다.

- with-Harness: deterministic assertion 16/16, blind rubric 87/100
- baseline: deterministic assertion 16/16, blind rubric 86/100
- blind winner: with-Harness
- 차이: with-Harness는 기존 주장과 새 확인 근거를 날짜가 있는 evidence history로 분리하고 `source_refs`·`generated_from`을 함께 유지했습니다.
- 저장 evidence: [run index](runs/run-index.json), [blind comparison](blind-comparison/comparisons.json), [independent reviewer evidence](blind-comparison/evidence/p02-codex-r1.json)

p02 최초 실행에서는 seed가 이미 lunch near-miss 메타 문장을 보유한 채 `zero lunch knowledge`를 요구하는 모순을 발견했습니다. 이후 본문 미갱신, `generated_from` 누락, completion summary 길이, PowerShell/Python canonical hash 불일치도 순차적으로 드러났습니다. 실패한 pair는 execution credit 0으로 [failure ledger](failures/failures.json)에 보존했고, seed·manifest·oracle·Skill·runner를 교정한 최종 재실행만 공식 2회 evidence로 가져왔습니다.

## 세 번째 Windows-native 비교 evidence

Codex p03 repetition 1은 동일 hash 웹 클립 통합, 새 일정 근거 보강, 명칭 교정 이력 보존을 2턴 preview·승인 흐름으로 실행했습니다.

- with-Harness: deterministic assertion 16/16, blind rubric 92/100
- baseline: deterministic assertion 13/16, blind rubric 62/100
- blind winner: with-Harness
- 발견·교정: 신규 중복 hash의 canonical record 누락, 승인 턴이 없는 frozen interaction, source-record의 `generated_from` 누락, 2턴 oracle의 잘못된 최종 메시지 선택
- 실패한 모든 중간 실행: execution credit 0, [failure ledger](failures/failures.json)에 보존
- 저장 evidence: [run index](runs/run-index.json), [blind comparison](blind-comparison/comparisons.json), [independent reviewer evidence](blind-comparison/evidence/p03-codex-r1.json)

## 네 번째 Windows-native 비교 evidence

Codex p04 repetition 1은 EML·Web·CSV·PDF·PNG·회의 메모를 포함한 합성 파일 20개를 read-only preview 후 고유 SHA256 최대 4개씩 처리하는 대량 자료 정리 시나리오입니다.

- with-Harness: deterministic assertion 17/17, blind rubric 96/100, 42분 28초
- baseline: deterministic assertion 9/17, blind rubric 93/100, 23분 43초
- blind winner: with-Harness
- 차이: baseline은 더 빨랐지만 read-only preview, Local-only promotion, 전체 provenance·자료 유형, 중복 canonical record, history, resumable progress를 실패했습니다.
- 발견·교정: unbounded batch timeout, preview 단계 mutation, 누락 email source record, progress key alias, Local knowledge `generated_from` parent hash 누락
- 실패한 모든 중간 실행: execution credit 0, [failure ledger](failures/failures.json)에 보존
- 저장 evidence: [run index](runs/run-index.json), [blind comparison](blind-comparison/comparisons.json), [independent reviewer evidence](blind-comparison/evidence/p04-codex-r1.json)

## 다섯 번째 Windows-native 비교 evidence

Codex p05 repetition 1은 상충 주장, 근거 없는 연구 주장, stale downstream FAQ를 reviewed 결정에 덮어쓰지 않고 독립 검토 문서로 격리하는 시나리오입니다.

- with-Harness: deterministic assertion 18/18, blind rubric 95/100, 첫 턴 read-only preview 후 승인 적용
- baseline: deterministic assertion 12/18, blind rubric 83/100, 첫 턴부터 파일 생성 및 canonical promotion 상태·provenance 계약 실패
- blind winner: with-Harness
- 차이: with-Harness는 `Claim B` 식별자, 독립 claim 상태, exact source hash, `generated_from`, 반증·미확인 사항·다음 검증을 일관되게 보존했습니다.
- 발견·교정: fixture review date 모순, 임의 enum, 63자리 SHA256, 승인 턴 누락, Windows 편집 재시도 timeout, substantive plain index, canonical package checksum과 raw file SHA256의 잘못된 비교
- 실패한 모든 중간 실행과 첫 블라인드 baseline 승리: execution credit 0, [failure ledger](failures/failures.json)에 보존
- 저장 evidence: [run index](runs/run-index.json), [blind comparison](blind-comparison/comparisons.json), [independent reviewer evidence](blind-comparison/evidence/p05-codex-r1.json)

## 여섯 번째 Windows-native 비교 evidence

Codex p06 repetition 1은 기존 Local Wiki에서 검토 일정과 Atlas Ledger 명칭 상태를 찾아 exact SHA256, 반증, 미확인 자료, 다음 확인, 신뢰도를 분리해 답하는 읽기 전용 질의 시나리오입니다.

- with-Harness: deterministic assertion 18/18, blind rubric 98/100
- baseline: deterministic assertion 18/18, 내용 평가는 강했지만 근거 없는 Git clean·HEAD 상태 주장을 추가해 blind hard-failure cap 0
- blind winner: with-Harness
- 차이: with-Harness는 합성 Local Wiki 범위를 명시하고, 검토된 금요일 결론과 미검증 목요일 주장의 효력, 명칭 변경 지시와 사전 승인 상태를 분리했습니다.
- 발견·교정: 반증이 현재 결론을 바꾸는지 명시하지 않은 첫 응답, 한국어 체크리스트·별칭·사전 소유자 동의어를 놓친 oracle, 읽기 전용 답변 폴더 생성 오류, 기존 seed Profile을 누락한 blind input bundle
- 실패한 첫 실행과 불완전한 0:0 blind bundle: execution credit 0, [failure ledger](failures/failures.json)에 보존
- 저장 evidence: [run index](runs/run-index.json), [blind comparison](blind-comparison/comparisons.json), [independent reviewer evidence](blind-comparison/evidence/p06-codex-r1.json)

## 일곱 번째 Windows-native 비교 evidence

Codex p07 repetition 1은 20개 자료 중 10개가 처리된 중단 지점에서 승인된 exact plan을 확인하고, 다음 고유 hash 4개만 재개한 뒤 이어서 처리할 batch를 남기는 시나리오입니다.

- with-Harness: deterministic assertion 18/18, blind rubric 98/100
- baseline: deterministic assertion 14/18이지만 Profile 필수 필드와 허용 enum 위반으로 blind hard-failure cap 0
- blind winner: with-Harness
- 차이: with-Harness는 처리 완료 hash와 중복 path를 구분하고, 읽을 수 있는 자료를 즉시 재사용 가능한 지식으로 정리하며, 정확한 다음 batch와 Local-only 경계를 보존했습니다.
- 실패·수정 이력: ambiguity, timeout, wrapper-only 결과와 reviewer 결과 JSON 종결 오류를 [failure ledger](failures/failures.json)에 보존했습니다.
- 저장 evidence: [run index](runs/run-index.json), [blind comparison](blind-comparison/comparisons.json), [independent reviewer evidence](blind-comparison/evidence/p07-codex-r1.json)

## 현재 source-knowledge 계약과 과거 evidence의 경계

p01·p03·p04의 저장 산출물은 당시 계약에 따라 읽을 수 있는 자료에도 metadata 중심 `source-record`를 만들었으므로, 현재의 “읽을 수 있는 자료 하나당 즉시 재사용 가능한 지식 한 문서” 계약을 증명하지 않습니다. p07 산출물은 주장·결정·제약·불확실성을 같은 문서 본문에 담아 wrapper-only 문제를 해결했지만, 여전히 legacy `knowledge_role: source-record`를 사용했습니다.

현재 Skill은 읽을 수 있는 이메일·웹·Markdown·텍스트·표 자료에 `templates/source-knowledge-template.md`를 사용하고, `source-record`는 읽을 수 없는 바이너리·지원하지 않는 입력·격리 자료에만 사용하도록 교정했습니다. 이 새 역할 분리는 실제 Local Profile 인스턴스와 lint 회귀로 확인했지만, 새 runtime 비교 실행은 수습 범위에서 금지되어 수행하지 않았습니다. 따라서 과거 점수와 artifact는 수정하지 않고 역사적 evidence로 보존하며, 현재 source-knowledge 계약의 cross-runtime 또는 Reference evidence로 과장하지 않습니다.

첨부 수습 지시에 따라 p08, 새 oracle 확장, Claude, repetition 2·3과 추가 benchmark 실행은 중단했습니다. p08 관련 기존 prompt·assertion·관리자 코드 초안은 삭제하지 않고 미검증 실험 자산으로 보존합니다.

## 비프로덕션 진단과 수정 이력

2026-08-02 개발 smoke에서 Codex와 Claude 모두 모델 실행 전 인증 401로 중단됐습니다. 이후 Windows Codex 파일럿은 비활성 Windows sandbox가 `workspace-write`를 read-only로 내리는 문제와, 초기 Skill이 `okf/profile_version/id`처럼 필드명을 축약하는 실제 결함을 발견했습니다. 실패는 모두 completed execution credit 0으로 [failure ledger](failures/failures.json)에 남겼습니다.

Skill이 source-record와 agent-memory 템플릿을 직접 사용하도록 교정한 뒤, 같은 Codex p01 비격리 합성 진단은 14/14 결정 검사를 통과했습니다. 동일 조건 baseline은 6/14였고 OKF Profile page를 만들지 못했습니다. 이 결과와 artifact hash는 [non-production comparison](failures/p01-codex-nonproduction-comparison.json)에 기록했습니다. 이 초기 비격리 결과는 현재 공식 14회 evidence와 별개이며 96회나 승률에 포함하지 않습니다.

토큰, 원시 인증 로그, 전체 모델 transcript는 저장소에 보존하지 않았습니다. 선택된 합성 자료가 사용자 승인 AI 제공자 문맥에서 처리된 사실과 BoI/MCP 원격 전송 0건은 서로 구분해 기록합니다.

실제 runtime evidence 없이 점수나 통과 결과를 채우지 않습니다. 자세한 실행 조건은 [frozen protocol](PROTOCOL.md)을 따릅니다.
