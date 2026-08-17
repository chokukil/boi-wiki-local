# Second Brain 개선 계획 — 2026-08-17

상태 기준: 2026-08-17 e2e 검증 완료 시점
- harness repo: `C:\AI\second-brain` @ `codex/second-brain-markdown-first-quality` (origin sync)
- profile repo: `C:\AI\second-brain-2055186` @ `codex/broadcast-ai-paper-demo-2055186`
- generated-answers 6/6 receipts 전수 PASS (identity binding 6건 복구 후)
- SDD `2026-08-13-second-brain-answer-quality-drift`: 3 task 완료, 175 tests pass — **미병합** (`codex/second-brain-answer-quality`)

범위 원칙: Local-only. Remote mutation 0건. Local Private는 preview 없이는 공유 금지.

---

## Phase 0 — 위생 커밋 (두 repo, 로컬)

목표: 현재 상태가 git에 고정되도록 커밋. 이후 어떤 Phase든 원점 복귀 가능.

1. profile repo:
   - `git add -A && git commit` — 대상: 5개 복구 receipts, `e2e-verification-2026-08-17.json`, skill/scripts 변경, `research/broadcast-ai-paper-demo/`, `tmp/`(평가 시 제외 판단)
   - 커밋 메시지: `fix(answer-surface): repair empty identity bindings + 8/17 e2e verification`
2. harness repo:
   - untracked `docs/`(plans), `tests/test_second_brain_knowledge_governance_contract.py`, `research/ai-radar/`, `cases/promotion-preview/` 검토 → 커밋 또는 `.gitignore`
   - `_workspace/`는 임시 → ignore
3. 검증: `git status` 깨끗, `git log` 최근 커밋 확인

완료 기준: 두 repo 모두 working tree clean.

---

## Phase 1 — identity binding fail-closed (핵심)

근본 원인: `scripts/local_wiki.py:1129` — binding이 비면 `{}`로 조용히 통과 (fail-open).
6건의 빈 binding이 바로 이 경로에서 생성됨.

1. RED: receipt evidence 항목의 `original_identity_binding`이 빈 객체인 fixture 추가
   - `tests/`에 regression test: 빈 binding receipt는 **기각** 또는 `origin_binding_valid: false` 강제
   - `query_quality.py` 검증 경로도 동일 규칙 적용 확인 (418행 부근)
2. GREEN: `local_wiki.py` receipt writer가 source-evidence 항목의 비어 있는 binding을 기각하도록 수정
   - 선택안 A(권장): binding 없음 → receipt 생성 거부 + 명확한 error (composer가 다시 선언하게)
   - 선택안 B: 생성은 허용하되 answer-surface 검증에서 fail-closed
3. 재검증: 기존 6 receipts PASS 유지 (이미 binding 복구 완료)
4. 완료 기준: 빈 binding fixture가 RED→GREEN, 전체 회귀 test pass

---

## Phase 2 — 코드/스킬 중복 제거 (drift 방지)

문제: `local_wiki.py`, `query_quality.py`, `boi-second-brain/SKILL.md`가
harness repo와 profile repo에 **각 2부** 존재. profile 쪽이 오래된 버전으로
receipt를 쓴 것이 빈 binding의 실제 경로일 가능성.

1. canonical 결정: harness repo가 소스 of truth (harness.lock/bootstrap 체계 존재)
2. profile repo의 scripts/skills를 **bootstrap 관리 영역**으로 표시하거나
   harness에서 sync/검증 스크립트 추가:
   - `scripts/verify_profile_sync.py` (또는 ps1): harness ↔ profile의 scripts+SKILL.md SHA256 비교
   - mismatch 시 fail + 어떤 파일이 drift인지 보고
3. `.agents/skills` ↔ `.claude/skills` 2부도 동일 검증 대상
4. 완료 기준: sync 검증 스크립트가 현재 state에서 drift 0건 보고 (또는 drift 목록을 보고 후 sync)

---

## Phase 3 — 브랜치 통합

현재 8개 브랜치 + main은 뒤처짐. SDD 성과가 미병합.

1. `codex/second-brain-answer-quality` (SDD 완료, 3 commits, 175 tests) →
   `codex/second-brain-markdown-first-quality` merge (또는 main으로)
   - merge 전: 해당 브랜치에서 full regression 재실행
2. stale 브랜치 정리: `boi-wiki-local-rc-pre-squash`, `agent/second-brain-knowledge-change-guide` 등
   - 각 브랜치에 unique commit이 있는지 `git log main..branch` 확인 후 삭제 or 보존 결정
3. `codex/second-brain-query-latency`, `codex/ai-radar-golden-journey`, `codex/agentic-ai-golden-journey` —
   각 목적 확인, 필요하면 Phase 목록에 추가, 아니면 archive
4. 완료 기준: 활성 브랜치 2개 이하 (main + 작업 브랜치 1), SDD 성과가 통합 브랜치에 포함

---

## Phase 4 — Skill pitfall 패치

`/mnt/c/AI/second-brain/.agents/skills/boi-second-brain/SKILL.md` (canonical)에 기록:

1. **검색 엄격성 pitfall** — 재현 확인 후:
   - 다중 단어 query가 0건 반환되는 조건 (AND 매칭?)
   - 대응: 단어 분리 검색 또는 필드 단위 검색 권장 패턴
2. **빈 identity binding pitfall** (Phase 1과 세트):
   - receipt evidence 항목에 `original_identity_binding`을 항상 3요소(evidence_id, evidence_sha256, expected_origin_ref)로 선언할 것
   - 빈 `{}`는 Answer Surface 검증 fail
3. 완료 기준: skill에 두 pitfall 섹션 존재, profile repo 부본도 sync (Phase 2 스크립트로 확인)

---

## Phase 5 — 백업 갱신 + ops 문서

1. `C:\AI\second-brain-backup-2026-07-12` → 최신 backup 생성 (두 repo + profile data)
   - 날짜 접미사: `second-brain-backup-2026-08-17`
2. 단일 ops/handoff 문서 작성 (기존 8/13 HANDOFF는 디스크에 없음):
   - repo 지도 (harness / profile / backup / Inbox 원문 위치)
   - 검증 runbook: `e2e-verification-2026-08-17.json`을 템플릿으로 하는 receipt 검증 절차
   - 금지/주의: Local Private 공유 경계, Remote mutation, Python-free 경로
   - 위치: harness repo `docs/ops/handoff-2026-08-17.md`
3. 완료 기준: 백업 확인 가능, handoff 문서로 신규 세션이 상태 복원 가능

---

## Phase 6 — (선택, external) cross-runtime benchmark

`global-insight-acceptance-audit`의 유일한 pending-external:
Codex·Claude 동일 입력 반복 evidence 0/60.

- 새 세션에서 두 runtime으로 동일 query 집합 실행 → artifact 동등성 검증
- Local Private 내용 포함 주의 (release tree 제외 규칙 준수)
- 완료 기준: acceptance audit의 해당 항목 `pending-external` → `proven`

---

## 우선순위와 의존

```
Phase 0 (위생) ──┬─→ Phase 1 (fail-closed) ──→ Phase 4 (skill pitfall)
                 ├─→ Phase 2 (dedup/sync) ─────→ Phase 4 (skill sync 검증)
                 ├─→ Phase 3 (브랜치 통합)
                 └─→ Phase 5 (백업/ops)
Phase 6: 독립 (external runtime 필요)
```

- 0 → 1 → 2 → 4는 직렬 (코드 변경 + 검증 사슬)
- 3, 5는 1/2와 병렬 가능
- 전체 완료 시: receipt 무결성이 코드 수준에서 보장되고, drift가 검출되며, 신규 세션이 handoff만으로 복원 가능

## 리스크

| 리스크 | 대응 |
|---|---|
| Phase 1 fail-closed가 기존 6 receipts를 깨뜨림 | 이미 binding 복구 완료 → 영향 없음, 추가 fixture로 RED 검증 |
| Phase 3 merge 시 test 충돌 | merge 전 full regression, autosquash 관례 유지 |
| Phase 2 sync가 profile의 의도적 local 변경을 지움 | sync는 **검증만** 수행, 자동 rewrite 금지 — drift 보고 후 수동 결정 |
| Local Private가 commit에 섞임 | Phase 0 커밋 전 `git diff --stat` + 경로 감사, `.boi/private/` 제외 확인 |
