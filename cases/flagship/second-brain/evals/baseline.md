# Baseline isolation contract

Baseline은 “Harness 파일을 읽지 않은 동일 모델”입니다. 더 약한 모델이나 더 적은 도구를 쓰는 비교군이 아닙니다.

## 동일하게 유지

- runtime, model, reasoning effort와 호출 제한
- Windows-native 임시 작업공간
- prompt text와 지정 fixture·seed bytes
- Local 파일 읽기·쓰기·hash 도구
- 네트워크 차단과 일반 안전 정책
- wall-clock 제한과 최대 turn 제한
- 동일한 Windows workspace-write sandbox와 합성 평가용 실행 정책

## 제거

- BoI Wiki Local repository
- AGENTS.md와 CLAUDE.md
- `.agents/skills`, `.claude/skills`, pinned HarnessPackage
- Case Harness, expected output, assertion, rubric
- OKF·BoI schema에 대한 추가 설명

## 무효 비교

- baseline에 with-Harness 결과나 문서 일부를 제공
- baseline만 다른 모델·temperature·도구 제한을 사용
- A와 B가 서로의 작업공간을 읽음
- baseline prompt에 OKF frontmatter 예시를 추가
- runtime 기본 안전 정책까지 제거

각 run artifact는 `baseline_isolation` 항목에 이 계약의 hash와 발견된 노출 파일 목록 0건을 기록해야 합니다.
