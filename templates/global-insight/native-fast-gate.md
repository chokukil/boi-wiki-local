# Python-free native fast gate

일반 사용자는 명령을 입력하지 않습니다. AI가 artifact를 쓴 직후 `scripts/global_insight_native_check.ps1`을 실행하거나 동일 계약을 native 파일 기능으로 확인합니다.

검사 항목:

1. 공통 계약과 Case 필수 파일 존재
2. 일곱 도구 이름과 내부 식별자
3. delta enum과 빈 change set 규칙
4. source file의 exact SHA256과 bytes
5. `source_refs`, `generated_from`, 접근 상태와 확인 범위
6. Local Private, promotion preview, approval 무효화 경계
7. placeholder, 빈 본문, metadata-only wrapper
8. Markdown 내부 링크가 Case 밖으로 탈출하지 않는지 여부

기본 실행은 `runtime-contract.json`과 `examples/`의 source manifest, evidence, 빈 change set, handoff, failure·resume, hash invalidation, scoped lint, promotion preview를 모두 읽습니다. 따라서 파일 존재만 확인하지 않고 candidate bytes·SHA256 drift, 잘못된 delta, 누락된 resume 필드, semantic lint mutation과 승인된 것처럼 표시된 preview를 실제 실패로 차단합니다.

이 gate는 기계적 오류만 차단합니다. confidence, contradiction 해소, 폐기, 적용 가능성 같은 의미 판단은 수정하지 않고 Review에 남깁니다.

관리자와 CI는 Python oracle, benchmark, 전체 lint와 audit를 추가로 실행할 수 있습니다. Python 검사 미실행은 일반 사용자 작업 실패가 아닙니다.
