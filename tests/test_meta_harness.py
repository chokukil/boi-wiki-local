from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from case_harness_check import inspect  # noqa: E402
from case_benchmark import summarize  # noqa: E402
from meta_harness_check import inspect as inspect_meta_factory  # noqa: E402
from release_gate import readiness  # noqa: E402
from harness_sync import managed_bootstrap  # noqa: E402
from boi_local_common import SOURCE_END, SOURCE_START, local_frontmatter, sha256_text  # noqa: E402
from local_lint import HARNESS_CARD_REQUIRED_SECTIONS, lint_document, lint_workspace  # noqa: E402


class MetaHarnessTests(unittest.TestCase):
    def test_configured_local_harness_card_is_profiled_reusable_and_nonempty(self) -> None:
        employee_id = "7654321"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = root / "data" / "boi" / "private" / employee_id
            capture = base / "notes" / "capture-inbox" / "approved-weekly-review-request.md"
            capture.parent.mkdir(parents=True)
            approved_request = (
                "매주 팀 활동 자료를 근거와 함께 검토 가능한 지식으로 정리하고, "
                "공유 전에는 반드시 내 승인을 받아줘."
            )
            capture.write_text(
                local_frontmatter(
                    employee_id=employee_id,
                    doc_type="boi/local-capture",
                    title="승인된 주간 검토 Harness 요청",
                    description="개인 Harness 설계의 정확한 승인 입력",
                    boi_id=f"boi:private:{employee_id}:capture:weekly-review-request",
                    tags=["LocalPrivate", "MetaHarness", "Capture"],
                    source_refs=[
                        {
                            "type": "agent-session",
                            "ref": "approved-harness-request:weekly-review",
                            "note": "exact approved request only; raw transcript excluded",
                        }
                    ],
                    extra={
                        "capture_kind": "note",
                        "source_sha256": sha256_text(approved_request),
                        "source_hash_scope": "captured_source_section",
                        "source_immutability": "locked",
                    },
                )
                + f"\n# 승인 요청\n\n{SOURCE_START}\n{approved_request}\n{SOURCE_END}\n",
                encoding="utf-8",
            )
            capture_hash = hashlib.sha256(capture.read_bytes()).hexdigest()
            capture_ref = capture.relative_to(root).as_posix()
            approved_preview_hash = hashlib.sha256(b"approved weekly harness preview").hexdigest()

            card = base / "notes" / "harnesses" / "weekly-knowledge-review.md"
            card.parent.mkdir(parents=True)
            frontmatter = local_frontmatter(
                employee_id=employee_id,
                doc_type="boi/local-guide",
                title="주간 지식 검토 Harness",
                description="주간 자료를 출처 있는 Local 지식과 검토 후보로 만드는 반복 계약",
                boi_id=f"boi:private:{employee_id}:harness:weekly-knowledge-review",
                tags=["LocalPrivate", "MetaHarness", "ConfiguredHarness"],
                source_refs=[{"type": "local-document", "ref": capture_ref, "sha256": capture_hash}],
                memory_candidate=True,
            )
            frontmatter = frontmatter.removesuffix("---\n") + (
                "generated_from:\n"
                "  - type: local-document\n"
                f"    ref: {capture_ref}\n"
                f"    sha256: {capture_hash}\n"
                "---\n"
            )
            body = f"""
# 주간 지식 검토 Harness

## 1. User request and outcome

- Copyable one-sentence request: 저장된 주간 지식 검토 Harness로 이번 주 자료를 처리해줘.
- Target user and recurring work: 매주 팀 활동 자료를 정리하는 구성원
- Reusable result: 출처와 검토 상태가 있는 주간 지식
- Measurable success: 모든 결론이 원본 hash와 연결되고 미해결 항목이 표시된다.
- Failure conditions and exclusions: 필수 자료 누락, 원본 hash 불일치, 승인 없는 원격 공유

## 2. Audit and change preview

- Mode: `create`
- Existing Harness, Case, and Skills inspected: boi-wiki-local, boi-second-brain
- Nearest reusable Case and duplication decision: Flagship Second Brain을 재사용하고 새 Skill은 만들지 않는다.
- Files or contracts to change: 이 Local Harness 카드와 정제 지식
- User content and evidence to preserve: 승인 요청 capture와 모든 원본
- External checks that remain pending: 실제 BoI Wiki validator
- Approval state: approved for Local apply only

## 3. Knowledge flow

Capture → Distill → Query → Lint → Review

- Capture and source integrity: 원본과 SHA256을 보존한다.
- Distilled reusable knowledge: 결정, 근거, 제약, 불확실성을 정리한다.
- Questions the Harness must answer with sources: 이번 주 결정과 남은 위험은 무엇인가?
- Contradiction, staleness, unsupported-claim, and schema lint: 충돌과 무근거 결론을 보류한다.
- Human review and review cadence: 매주 금요일 사용자가 검토한다.

## 4. Reused Skills and ownership

| Capability | Existing Skill or Case | Reuse or extension | Why this layer owns it |
|---|---|---|---|
| Local 문서 계약 | boi-wiki-local | reuse | OKF, BoI, promotion 경계 소유 |
| 장기 지식 유지 | boi-second-brain | reuse | 검색, 교정, review cadence 소유 |

New generic Skill proposal: none; 두 기존 Skill이 전체 동작을 소유한다.

## 5. Roles and independent review

| Role | Responsibility | Inputs | Outputs | Exit or hard-fail condition |
|---|---|---|---|---|
| Curator | 자료와 기존 지식을 비교 | 원본 manifest | 정제 후보 | 필수 원본 누락 시 block |
| Reviewer | 출처와 결론을 독립 확인 | 원본과 정제 후보 | review 기록 | 근거 없는 결론 시 reject |

- Reviewer authority: 근거 없는 결론과 promotion 후보를 거부할 수 있다.
- How reviewer independence is preserved in Single-agent mode: 새 source-first pass에서 생산자 결론을 보지 않고 원본부터 검토한다.

## 6. Dependency DAG and handoffs

Capture → Curator → Reviewer → Local result → optional promotion preview

- phase exits: source hash 확인, 정제 완료, 독립 review 통과
- required handoff fields and source hashes: artifact path, SHA256, unknowns, blockers
- retry, skip, block, and resume behavior: 선택 자료만 skip하고 필수 자료 실패는 block한다.
- handling of missing or contradictory evidence: 양쪽 근거를 보존하고 review-required로 둔다.

## 7. Scale modes

| Mode | Role projection | Review separation | Output contract changes |
|---|---|---|---|
| Single-agent | 역할을 순차 수행 | 별도 source-first pass | none |
| Reduced | curator와 reviewer | 독립 reviewer | none |
| Full | 수집, 정제, 검토 역할 분리 | 독립 reviewer | none |
| No-team fallback | 같은 역할 카드를 순차 실행 | 별도 검토 단계 | none |

## 8. Artifact contracts

| Stage | Required artifact | Required fields or sections | Validation | Failure artifact |
|---|---|---|---|---|
| Input | source manifest | path, SHA256, access state | hash check | missing-source record |
| Intermediate | distilled draft | claims, decisions, constraints, uncertainty, counter-evidence | provenance lint | review-required record |
| Final Local | weekly knowledge | OKF, BoI Profile, sources, review state | Local lint | blocked result |

## 9. Error, fallback, and resume

- Missing input: 필요한 자료와 영향을 표시하고 의존 단계를 중단한다.
- Damaged or unsupported input: 원본을 바꾸지 않고 보류한다.
- Ambiguous request: 최대 세 가지 쉬운 질문을 한다.
- Access denied or unavailable external system: Local-only로 계속하고 원격 검증은 pending으로 둔다.
- Interrupted run and resume marker: 마지막 완료 artifact hash와 다음 DAG node를 기록한다.
- Conflicting evidence and review-required path: 양쪽 출처를 보존하고 사람 판단을 요청한다.

## 10. OKF, BoI, and Local/Remote boundary

- Local output contract: `OKF 0.1 + BoI Profile 0.1-local`
- Local Private source and intermediate artifacts: 원본, capture, review 기록
- Directly blocked promotion types: capture, evidence, agent-memory, 이 개인 Harness 카드
- Distilled types eligible for promotion preview: knowledge와 context pack
- Sanitization rules for Local paths, IDs, raw source, and sensitive content: canonical 후보에서 모두 제거한다.
- MCP read behavior and why it never implies upload: 조회 권한은 Local 업로드 권한이 아니다.
- Target visibility, reviewer, structured remote-safe sources, blockers, and exact candidate hash: 미리보기에 모두 표시한다.
- User approval and approval invalidation conditions: 본문, 출처, reviewer, scope 변경 시 승인을 무효화한다.

## 11. Non-developer walkthrough

1. Natural-language start request: 저장된 주간 지식 검토 Harness로 이번 자료를 처리해줘.
2. At most three plain-language questions: 자료 위치, 성공 조건, 공유 범위를 확인한다.
3. Change preview shown before mutation: 생성과 갱신 내용을 쉬운 말로 보여준다.
4. Local execution without Python, Obsidian, MCP, or team features: 기본 파일 도구만 사용한다.
5. Local Harness card path under `data/boi/private/7654321/notes/harnesses/`: weekly-knowledge-review.md
6. Copyable next-session request: 저장된 주간 지식 검토 Harness로 이번 주 자료를 처리해줘.
7. Result, search, correction, and resume examples: 결과를 검색하고 틀린 결론을 교정하며 마지막 hash부터 재개한다.
8. Optional promotion preview and explicit approval boundary: exact preview를 보여주고 제출하지 않는다.
9. Troubleshooting next step: 문제 해결 Wiki로 이동한다.

## 12. Validation and status

- trigger and near-miss boundary: 반복 주간 정리는 trigger, 한 문서 작성은 near-miss다.
- source and hash integrity: capture와 source manifest hash를 확인한다.
- output contract and failure-path checks: 정상, 누락, 충돌, 중단 경로를 검사한다.
- OKF and BoI lint: Local Profile을 검사한다.
- Local/Remote and security checks: 원격 write 0건을 확인한다.
- independent review evidence: reviewer 기록을 보존한다.
- runtime, user, and actual BoI Wiki evidence: 실제 validator와 사용자 evidence는 pending이다.
- current status and claims that remain prohibited: Local candidate이며 reference와 production-ready 주장을 금지한다.

## 13. Evolution record

- Previous Harness version: none (initial creation)
- Approved change preview: {approved_preview_hash} (approved)
- Change reason and user approval: 최초 설계를 사용자가 승인함
- Feedback or failure: 아직 없음
- Smallest owning layer: not applicable — initial approved design; no defect classified
- Preserved failure evidence: 실패가 생기면 Local ledger에 hash와 함께 보존한다.
- Minimal change and affected regression: 가장 작은 소유 계층과 관련 회귀만 변경한다.
- Evidence needed before promoting behavior into a generic Skill: 독립 Case 세 개와 baseline 개선이 필요하다.
- Next review owner and date: Local owner, 2026-08-10
"""
            valid_card_text = frontmatter + body
            card.write_text(valid_card_text, encoding="utf-8")

            harness_index = card.parent / "index.md"
            harness_index.write_text(
                "# 승인된 개인 Harness\n\n"
                "## 저장된 Harness\n\n"
                "- [주간 지식 검토 Harness](weekly-knowledge-review.md)\n",
                encoding="utf-8",
            )

            self.assertEqual([], lint_document(root, base, employee_id, capture))
            self.assertEqual([], lint_document(root, base, employee_id, card))
            self.assertIn(
                "[주간 지식 검토 Harness](weekly-knowledge-review.md)",
                harness_index.read_text(encoding="utf-8"),
            )
            self.assertTrue(lint_workspace(root, employee_id)["ok"])

            harness_index.write_text(
                "# 승인된 개인 Harness\n\n## 저장된 Harness\n\n아직 등록된 카드가 없습니다.\n",
                encoding="utf-8",
            )
            missing_link = lint_workspace(root, employee_id)
            self.assertFalse(missing_link["ok"])
            self.assertTrue(any(
                "active configured Harness card is missing from notes/harnesses/index.md"
                in issue
                for error in missing_link["errors"]
                for issue in error["issues"]
            ))

            harness_index.write_text(
                "# 승인된 개인 Harness\n\n"
                "## 저장된 Harness\n\n"
                "- [주간 지식 검토 Harness](wrong-card.md)\n",
                encoding="utf-8",
            )
            wrong_link = lint_workspace(root, employee_id)
            self.assertFalse(wrong_link["ok"])
            self.assertTrue(any(
                "broken Markdown link: wrong-card.md" in issue
                for error in wrong_link["errors"]
                for issue in error["issues"]
            ))

            harness_index.write_text(
                "# 승인된 개인 Harness\n\n"
                "## 저장된 Harness\n\n"
                "- [주간 지식 검토 Harness](weekly-knowledge-review.md)\n",
                encoding="utf-8",
            )

            korean_headings = {
                "## 1. User request and outcome": "## 1. 사용자 요청과 결과",
                "## 2. Audit and change preview": "## 2. 감사와 변경 미리보기",
                "## 3. Knowledge flow": "## 3. 지식 흐름",
                "## 4. Reused Skills and ownership": "## 4. 재사용 Skills와 책임",
                "## 5. Roles and independent review": "## 5. 역할과 독립 검토",
                "## 6. Dependency DAG and handoffs": "## 6. 의존 DAG와 인계",
                "## 7. Scale modes": "## 7. 실행 규모",
                "## 8. Artifact contracts": "## 8. 산출물 계약",
                "## 9. Error, fallback, and resume": "## 9. 오류, 대안과 재개",
                "## 10. OKF, BoI, and Local/Remote boundary": "## 10. OKF, BoI와 Local/Remote 경계",
                "## 11. Non-developer walkthrough": "## 11. 비개발자 사용 순서",
                "## 12. Validation and status": "## 12. 검증과 상태",
                "## 13. Evolution record": "## 13. 개선 이력",
                "Copyable one-sentence request:": "복사 가능한 한 문장 요청:",
                "Target user and recurring work:": "대상 사용자와 반복 업무:",
                "Reusable result:": "재사용 결과:",
                "Measurable success:": "측정 가능한 성공:",
                "Failure conditions and exclusions:": "실패 조건과 제외 범위:",
                "Mode:": "모드:",
                "Capture and source integrity:": "수집과 출처 무결성:",
                "Distilled reusable knowledge:": "정제된 재사용 지식:",
                "Human review and review cadence:": "사람 검토와 검토 주기:",
                "New generic Skill proposal:": "새 범용 Skill 제안:",
                "Reviewer authority:": "검토자 권한:",
                "How reviewer independence is preserved in Single-agent mode:": "Single-agent 모드의 검토 독립성:",
                "phase exits:": "단계 종료 조건:",
                "required handoff fields and source hashes:": "필수 인계 필드와 출처 hash:",
                "Missing input:": "입력 누락:",
                "Access denied or unavailable external system:": "접근 거부 또는 외부 시스템 사용 불가:",
                "Interrupted run and resume marker:": "중단 후 재개 표식:",
                "Conflicting evidence and review-required path:": "충돌 근거와 검토 필요 경로:",
                "Sanitization rules for Local paths, IDs, raw source, and sensitive content:": "Local 경로·ID·원문·민감정보 제거 규칙:",
                "User approval and approval invalidation conditions:": "사용자 승인과 승인 무효화 조건:",
                "Copyable next-session request:": "다음 세션 요청문:",
                "trigger and near-miss boundary:": "trigger와 near-miss 경계:",
                "independent review evidence:": "독립 검토 evidence:",
                "runtime, user, and actual BoI Wiki evidence:": "runtime·사용자·실제 BoI Wiki evidence:",
                "current status and claims that remain prohibited:": "현재 상태와 금지된 주장:",
                "Previous Harness version:": "이전 Harness 버전:",
                "Approved change preview:": "승인한 변경 미리보기:",
                "Change reason and user approval:": "변경 이유와 사용자 승인:",
                "Smallest owning layer:": "가장 작은 소유 계층:",
                "Preserved failure evidence:": "보존한 실패 evidence:",
                "Evidence needed before promoting behavior into a generic Skill:": "범용 Skill 승격 전 필요한 evidence:",
                "Next review owner and date:": "다음 검토 책임자와 날짜:",
            }
            korean_card_text = valid_card_text
            for english, korean in korean_headings.items():
                korean_card_text = korean_card_text.replace(english, korean)
            card.write_text(korean_card_text, encoding="utf-8")
            self.assertEqual([], lint_document(root, base, employee_id, card))
            card.write_text(valid_card_text, encoding="utf-8")

            shutil.copy2(REPO / "harness.lock", root / "harness.lock")
            (base / "promotion-drafts").mkdir()
            sanitized = root / "generic-method.md"
            sanitized.write_text(
                "# Generic weekly knowledge review\n\nA reviewed reusable method with no personal execution configuration.\n",
                encoding="utf-8",
            )
            preflight = subprocess.run(
                [
                    sys.executable,
                    str(REPO / "scripts" / "promotion_preflight.py"),
                    "--root",
                    str(root),
                    "--employee-id",
                    employee_id,
                    "--source",
                    card.relative_to(root).as_posix(),
                    "--sanitized-file",
                    str(sanitized),
                    "--sanitized-title",
                    "Generic weekly knowledge review",
                    "--sanitized-description",
                    "Reviewed reusable method",
                    "--target-visibility",
                    "public",
                    "--reviewer",
                    "knowledge-reviewer",
                    "--source-ref",
                    "url=https://example.com/generic-review-method",
                    "--dry-run",
                ],
                cwd=REPO,
                text=True,
                encoding="utf-8",
                capture_output=True,
                check=False,
            )
            self.assertEqual(2, preflight.returncode, preflight.stdout + preflight.stderr)
            payload = json.loads(preflight.stdout)
            self.assertFalse(payload["ok"])
            self.assertIn(
                "configured Local Harness cards cannot be promoted directly; distill a generic guide or package a reviewed Community Case first",
                payload["blockers"],
            )
            self.assertFalse(payload["remote_submitted"])

            card.write_text(card.read_text(encoding="utf-8").replace(
                "## 9. Error, fallback, and resume", "## Error handling omitted"
            ), encoding="utf-8")
            issues = lint_document(root, base, employee_id, card)
            self.assertIn(
                "configured Harness card missing section: ## 9. Error, fallback, and resume",
                issues,
            )

            card.write_text(
                valid_card_text.replace("Copyable next-session request:", "Activation details omitted:"),
                encoding="utf-8",
            )
            issues = lint_document(root, base, employee_id, card)
            self.assertIn(
                "configured Harness card missing substantive contract signal: next-session activation request",
                issues,
            )

            card.write_text(
                valid_card_text.replace(
                    "trigger and near-miss boundary:",
                    "trigger scope omitted:",
                ),
                encoding="utf-8",
            )
            issues = lint_document(root, base, employee_id, card)
            self.assertIn(
                "configured Harness card missing substantive contract signal: trigger and near-miss boundary",
                issues,
            )

            card.write_text(
                valid_card_text.replace(
                    "User approval and approval invalidation conditions:",
                    "Approval details omitted:",
                ),
                encoding="utf-8",
            )
            issues = lint_document(root, base, employee_id, card)
            self.assertIn(
                "configured Harness card missing substantive contract signal: approval invalidation conditions",
                issues,
            )

            card.write_text(valid_card_text.replace("아직 없음", "TODO"), encoding="utf-8")
            issues = lint_document(root, base, employee_id, card)
            self.assertIn("configured Harness card contains placeholder text: TODO", issues)

            card.write_text(
                valid_card_text.replace("Mode: `create`", "Mode: `create | extend | audit | evolve | evaluate`"),
                encoding="utf-8",
            )
            issues = lint_document(root, base, employee_id, card)
            self.assertIn("configured Harness card contains unselected choice list: mode", issues)

            card.write_text(
                valid_card_text.replace(
                    "Smallest owning layer: not applicable — initial approved design; no defect classified",
                    "Smallest owning layer: `Case method | orchestration | generic Skill | fixture or prompt | validator | runtime`",
                ),
                encoding="utf-8",
            )
            issues = lint_document(root, base, employee_id, card)
            self.assertIn("configured Harness card contains unselected choice list: evolution owner", issues)

            card.write_text(
                valid_card_text.replace(
                    "Previous Harness version: none (initial creation)",
                    "Previous Harness version: archived somewhere",
                ),
                encoding="utf-8",
            )
            issues = lint_document(root, base, employee_id, card)
            self.assertIn(
                "configured Harness evolution must name none for initial creation or an archived previous card path with exact SHA256",
                issues,
            )

            card.write_text(
                valid_card_text.replace(approved_preview_hash, "not-a-hash"),
                encoding="utf-8",
            )
            issues = lint_document(root, base, employee_id, card)
            self.assertIn(
                "configured Harness evolution requires an exact approved change preview SHA256",
                issues,
            )

            archive_card = (
                base
                / "_archive"
                / "harnesses"
                / "20260803-000000"
                / "weekly-knowledge-review.md"
            )
            archive_card.parent.mkdir(parents=True)
            archive_card.write_text(valid_card_text, encoding="utf-8")
            archive_hash = hashlib.sha256(archive_card.read_bytes()).hexdigest()
            archive_ref = archive_card.relative_to(root).as_posix()
            generated_block = (
                "generated_from:\n"
                "  - type: local-document\n"
                f"    ref: {capture_ref}\n"
                f"    sha256: {capture_hash}\n"
                "---\n"
            )
            evolved_generated_block = (
                "generated_from:\n"
                "  - type: local-document\n"
                f"    ref: {capture_ref}\n"
                f"    sha256: {capture_hash}\n"
                "  - type: local-document\n"
                f"    ref: {archive_ref}\n"
                f"    sha256: {archive_hash}\n"
                "---\n"
            )
            evolved_preview_hash = hashlib.sha256(b"approved evolution preview").hexdigest()
            evolved_text = valid_card_text.replace(generated_block, evolved_generated_block, 1)
            evolved_text = evolved_text.replace(
                "Previous Harness version: none (initial creation)",
                f"Previous Harness version: {archive_ref} SHA256 {archive_hash}",
            )
            evolved_text = evolved_text.replace(approved_preview_hash, evolved_preview_hash)
            evolved_text = evolved_text.replace(
                "Change reason and user approval: 최초 설계를 사용자가 승인함",
                "Change reason and user approval: 재개 계약 결함 수정을 사용자가 승인함",
            )
            card.write_text(evolved_text, encoding="utf-8")
            self.assertEqual([], lint_document(root, base, employee_id, card))

            card.write_text(
                evolved_text.replace(
                    "  - type: local-document\n"
                    f"    ref: {archive_ref}\n"
                    f"    sha256: {archive_hash}\n",
                    "",
                    1,
                ),
                encoding="utf-8",
            )
            issues = lint_document(root, base, employee_id, card)
            self.assertIn(
                "configured Harness evolution requires the archived previous card path and SHA256 in structured generated_from",
                issues,
            )

    def test_current_catalog_is_valid_but_does_not_claim_reference(self) -> None:
        catalog = json.loads((REPO / "cases" / "catalog.json").read_text(encoding="utf-8"))
        self.assertEqual("public-candidate", catalog["catalog_scope"])
        self.assertEqual(
            [
                "second-brain",
                "agentic-ai-change-radar",
                "fab-logistics-digital-twin",
                "scientific-foundation-model-knowledge",
            ],
            [entry["case_id"] for entry in catalog["cases"]],
        )
        result = inspect(REPO)
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual(4, result["case_count"])
        self.assertEqual(276, result["required_comparison_executions"])
        self.assertEqual(0, result["reference_count"])
        self.assertFalse(result["production_quality_gate_passed"])
        flagship = json.loads(
            (REPO / "cases" / "flagship" / "second-brain" / "case.yaml").read_text(encoding="utf-8")
        )
        self.assertNotIn("boi/local-knowledge-note", flagship["direct_promotion_blocked_types"])
        self.assertIn("boi/local-analysis-case", flagship["direct_promotion_blocked_types"])
        self.assertEqual(
            {"agent-memory", "source-record"},
            set(flagship["direct_promotion_blocked_roles"]),
        )
        self.assertEqual("synthetic-only", flagship["fixture_policy"])
        self.assertEqual("deterministic-20-real-files", flagship["fixture_profile"])
        schema = json.loads((REPO / "cases" / "_schema" / "case-harness.schema.json").read_text(encoding="utf-8"))
        for manifest_path in sorted((REPO / "cases").rglob("case.yaml")):
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertTrue(set(schema["required"]).issubset(manifest), manifest_path.as_posix())
            self.assertIn(
                manifest["fixture_policy"],
                schema["properties"]["fixture_policy"]["enum"],
                manifest_path.as_posix(),
            )
            self.assertNotIn(
                "boi/local-knowledge-note",
                manifest["direct_promotion_blocked_types"],
                manifest_path.as_posix(),
            )
            self.assertIn(
                "boi/local-analysis-case",
                manifest["direct_promotion_blocked_types"],
                manifest_path.as_posix(),
            )
            self.assertTrue(
                {"agent-memory", "source-record"}.issubset(
                    set(manifest["direct_promotion_blocked_roles"])
                ),
                manifest_path.as_posix(),
            )

    def test_reference_claim_without_runtime_evidence_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shutil.copytree(REPO / "cases", root / "cases")
            catalog_path = root / "cases" / "catalog.json"
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            catalog["cases"][0]["status"] = "reference"
            catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
            case_path = root / "cases" / catalog["cases"][0]["path"] / "case.yaml"
            case = json.loads(case_path.read_text(encoding="utf-8"))
            case["status"] = "reference"
            case_path.write_text(json.dumps(case, ensure_ascii=False, indent=2), encoding="utf-8")

            result = inspect(root)
            self.assertFalse(result["ok"])
            self.assertTrue(any("Reference gate missing" in error for error in result["errors"]))

    def test_flagship_benchmark_records_only_the_imported_partial_pairs(self) -> None:
        result = summarize(REPO / "cases" / "flagship" / "second-brain")
        self.assertEqual([], result["errors"])
        self.assertEqual("partial", result["status"])
        self.assertEqual(96, result["required_executions"])
        self.assertEqual(14, result["completed_executions"])
        self.assertEqual(1.0, result["objective_assertion_pass_rate"])
        self.assertEqual(1.0, result["hard_safety_pass_rate"])
        self.assertEqual(95.0, result["median_score"])
        self.assertEqual(1.0, result["blind_win_rate"])
        self.assertFalse(result["production_quality_gate_passed"])
        self.assertFalse(result["reference_eligible"])

    def test_content_addressed_runtime_evidence_is_git_binary(self) -> None:
        attributes = (REPO / ".gitattributes").read_text(encoding="utf-8")
        self.assertIn("cases/**/fixtures/** -text", attributes)
        self.assertIn("cases/**/evals/seeds/** -text", attributes)
        self.assertIn("cases/**/evals/prompts/** -text", attributes)
        self.assertIn("cases/**/evals/runs/** -text", attributes)
        self.assertIn("cases/**/evals/blind-comparison/** -text", attributes)

    def test_flagship_fixture_contains_twenty_real_mixed_files_and_deterministic_seeds(self) -> None:
        case = REPO / "cases" / "flagship" / "second-brain"
        manifest = json.loads((case / "fixtures" / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual("boi-local-case-fixture-manifest/v2", manifest["schema"])
        self.assertEqual(20, manifest["source_count"])
        self.assertEqual(20, len(manifest["files"]))
        suffixes = {Path(item["path"]).suffix for item in manifest["files"]}
        self.assertTrue({".eml", ".md", ".csv", ".pdf", ".png", ".txt"}.issubset(suffixes))
        for item in manifest["files"]:
            path = case / "fixtures" / item["path"]
            self.assertTrue(path.is_file(), item["path"])
            self.assertEqual(item["bytes"], path.stat().st_size)
            self.assertEqual(item["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
        duplicate = manifest["intentional_duplicate_groups"][0]
        self.assertEqual(
            {duplicate["sha256"]},
            {
                hashlib.sha256((case / "fixtures" / path).read_bytes()).hexdigest()
                for path in duplicate["paths"]
            },
        )

        seeds = json.loads((case / "evals" / "seeds" / "seed-catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(4, len(seeds["seeds"]))
        mapped = [prompt for seed in seeds["seeds"] for prompt in seed["used_by_prompts"]]
        self.assertEqual([f"p{number:02d}" for number in range(1, 9)], sorted(mapped))

    def test_every_case_source_count_is_backed_by_real_hashed_files(self) -> None:
        catalog = json.loads((REPO / "cases" / "catalog.json").read_text(encoding="utf-8"))
        source_total = 0
        for entry in catalog["cases"]:
            case = REPO / "cases" / entry["path"]
            manifest = json.loads((case / "fixtures" / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual("boi-local-case-fixture-manifest/v2", manifest["schema"], entry["case_id"])
            self.assertEqual(manifest["source_count"], len(manifest["files"]), entry["case_id"])
            self.assertGreaterEqual(manifest["source_count"], 5, entry["case_id"])
            source_total += manifest["source_count"]
            for item in manifest["files"]:
                path = case / "fixtures" / item["path"]
                self.assertTrue(path.is_file(), f"{entry['case_id']}: {item['path']}")
                self.assertEqual(item["bytes"], path.stat().st_size)
                self.assertEqual(item["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertEqual(44, source_total)

    def test_every_case_uses_a_frozen_v2_runtime_protocol(self) -> None:
        catalog = json.loads((REPO / "cases" / "catalog.json").read_text(encoding="utf-8"))
        for entry in catalog["cases"]:
            case_root = REPO / "cases" / entry["path"]
            case = json.loads((case_root / "case.yaml").read_text(encoding="utf-8"))
            plan = json.loads((case_root / "evals" / "eval-plan.yaml").read_text(encoding="utf-8"))
            prompts = json.loads(
                (case_root / "evals" / "prompts" / "prompt-catalog.json").read_text(encoding="utf-8")
            )
            seeds = json.loads(
                (case_root / "evals" / "seeds" / "seed-catalog.json").read_text(encoding="utf-8")
            )
            artifact_schema = json.loads(
                (case_root / "evals" / "run-artifact.schema.json").read_text(encoding="utf-8")
            )
            expected_revision = "second-brain-eval/v2" if entry["flagship"] else "case-eval/v2"
            expected_prompts = 8 if entry["flagship"] else 5
            expected_seeds = 4 if entry["flagship"] else 3
            self.assertEqual(expected_revision, case["evaluation_protocol"], entry["case_id"])
            self.assertEqual("boi-local-case-eval-plan/v2", plan["schema"], entry["case_id"])
            self.assertEqual(expected_revision, plan["protocol_revision"], entry["case_id"])
            self.assertTrue(plan["fresh_workspace_per_execution"], entry["case_id"])
            self.assertFalse(plan["cross_run_state_allowed"], entry["case_id"])
            self.assertFalse(plan["network_enabled"], entry["case_id"])
            self.assertEqual(expected_prompts, len(prompts["prompts"]), entry["case_id"])
            self.assertEqual(expected_seeds, len(seeds["seeds"]), entry["case_id"])
            mapped = [prompt_id for seed in seeds["seeds"] for prompt_id in seed["used_by_prompts"]]
            self.assertEqual(
                [f"p{number:02d}" for number in range(1, expected_prompts + 1)],
                sorted(mapped),
                entry["case_id"],
            )
            for prompt in prompts["prompts"]:
                self.assertGreaterEqual(len(prompt["user_prompt"]), 80, entry["case_id"])
                interaction = prompt["interaction"]
                self.assertIn(interaction["mode"], {"single-turn", "scripted-multi-turn"})
                self.assertEqual(prompt["user_prompt"], interaction["turns"][0]["text"])
                self.assertEqual(
                    list(range(1, len(interaction["turns"]) + 1)),
                    [turn["turn"] for turn in interaction["turns"]],
                )
                for field in ("expected_operations", "required_outcomes", "forbidden_outcomes"):
                    self.assertTrue(prompt[field], f"{entry['case_id']} {prompt['prompt_id']} {field}")
                if prompt["prompt_id"] != "p04":
                    self.assertTrue(prompt["inputs"], f"{entry['case_id']} {prompt['prompt_id']} inputs")
            self.assertEqual(entry["case_id"], artifact_schema["properties"]["case_id"]["const"])
            self.assertEqual(expected_revision, artifact_schema["properties"]["protocol_revision"]["const"])
            self.assertIn("interaction_script_sha256", artifact_schema["required"])
            self.assertIn("runtime_envelope_sha256", artifact_schema["required"])
            self.assertIn("evaluated_interaction_sha256", artifact_schema["required"])
            self.assertIn("runtime_policy_sha256", artifact_schema["required"])
            self.assertIn("model_context", artifact_schema["required"])
            self.assertIn("boi_remote_source_bytes", artifact_schema["properties"]["remote_activity"]["required"])
            self.assertNotIn("local_source_bytes_sent", artifact_schema["properties"]["remote_activity"]["properties"])
            assertions = json.loads((case_root / "evals" / "assertions.json").read_text(encoding="utf-8"))
            self.assertIn("no_boi_remote_source_transmission", assertions["hard"])
            self.assertNotIn("no_local_source_transmission", assertions["hard"])
            benchmark = summarize(case_root)
            self.assertEqual([], benchmark["errors"], entry["case_id"])
            run_index = json.loads(
                (case_root / "evals" / "runs" / "run-index.json").read_text(encoding="utf-8")
            )
            expected_status = "partial" if run_index["runs"] else "not-run"
            self.assertEqual(expected_status, benchmark["status"], entry["case_id"])
            self.assertEqual(len(run_index["runs"]), benchmark["completed_executions"], entry["case_id"])
            self.assertFalse(benchmark["reference_eligible"], entry["case_id"])

    def test_self_reported_scores_cannot_replace_v2_run_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            case = Path(temp) / "second-brain"
            shutil.copytree(REPO / "cases" / "flagship" / "second-brain", case)
            fake = case / "evals" / "runs" / "fake.json"
            fake.write_text("{}\n", encoding="utf-8")
            assertions = json.loads((case / "evals" / "assertions.json").read_text(encoding="utf-8"))
            names = assertions["hard"] + assertions["quality"]
            index = {
                "schema": "boi-local-case-run-index/v1",
                "case_id": "second-brain",
                "runs": [
                    {
                        "prompt_id": "p01",
                        "runtime": "codex",
                        "repetition": 1,
                        "configuration": "with-harness",
                        "artifact": "evals/runs/fake.json",
                        "artifact_sha256": hashlib.sha256(fake.read_bytes()).hexdigest(),
                        "assertions": {name: True for name in names},
                        "score": 100,
                    }
                ],
            }
            (case / "evals" / "runs" / "run-index.json").write_text(
                json.dumps(index, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            result = summarize(case)
            self.assertEqual("partial", result["status"])
            self.assertIsNone(result["objective_assertion_pass_rate"])
            self.assertTrue(any("run artifact" in error for error in result["errors"]))

    def test_case_markdown_has_no_hidden_control_characters(self) -> None:
        for path in (REPO / "cases").rglob("*.md"):
            controls = [
                ord(char)
                for char in path.read_text(encoding="utf-8")
                if ord(char) < 32 and char not in "\n\r\t"
            ]
            self.assertEqual([], controls, path.as_posix())

    def test_meta_skill_is_generic_and_case_first(self) -> None:
        skill = (REPO / ".agents" / "skills" / "boi-harness-builder" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        lower = skill.lower()
        self.assertIn("reuse existing generic skills", lower)
        self.assertIn("existing skill routing", lower)
        self.assertIn("smallest owner set", lower)
        for name in (
            "boi-wiki-local",
            "boi-second-brain",
            "boi-action-author",
            "boi-context-pack-builder",
            "boi-dictionary-author",
            "boi-event-workflow-planner",
            "boi-langflow-connector-planner",
            "boi-sop-flow-visualizer",
            "boi-workflow-simulator",
        ):
            self.assertIn(name, lower)
        self.assertIn("three independent cases", lower)
        self.assertIn("near-miss", lower)
        self.assertIn("notes/harnesses/<slug>.md", lower)
        self.assertIn("notes/harnesses/index.md", lower)
        self.assertIn("one standard markdown link", lower)
        self.assertIn("copyable next-session request", lower)
        self.assertIn("a design shown only in chat is not a reusable harness", lower)
        self.assertNotIn("boi-yield-analysis", lower)

    def test_shared_boi_skill_enforces_the_full_local_profile_boundary(self) -> None:
        codex = REPO / ".agents" / "skills" / "boi-wiki-local" / "SKILL.md"
        claude = REPO / ".claude" / "skills" / "boi-wiki-local" / "SKILL.md"
        self.assertEqual(codex.read_bytes(), claude.read_bytes())
        text = codex.read_text(encoding="utf-8")
        for literal in (
            'okf_version: "0.1"',
            'boi_profile_version: "0.1-local"',
            "structured `source_refs`",
            "structured `generated_from`",
            "directly non-promotable",
            "exact candidate hash",
            "MCP read access never implies upload",
        ):
            self.assertIn(literal, text)

    def test_composed_boi_skills_inherit_the_shared_contract(self) -> None:
        names = (
            "boi-action-author",
            "boi-context-pack-builder",
            "boi-dictionary-author",
            "boi-event-workflow-planner",
            "boi-langflow-connector-planner",
            "boi-sop-flow-visualizer",
            "boi-workflow-simulator",
        )
        for name in names:
            codex = REPO / ".agents" / "skills" / name / "SKILL.md"
            claude = REPO / ".claude" / "skills" / name / "SKILL.md"
            self.assertEqual(codex.read_bytes(), claude.read_bytes(), name)
            text = codex.read_text(encoding="utf-8")
            self.assertIn("Use `boi-wiki-local` as the parent contract", text, name)
            self.assertIn("OKF 0.1 + BoI Profile 0.1-local", text, name)
            self.assertIn("structured provenance", text, name)
            self.assertIn("Local Private promotion boundary", text, name)

    def test_managed_bootstrap_routes_natural_language_harness_requests(self) -> None:
        package = json.loads((REPO / ".boi-harness" / "package.json").read_text(encoding="utf-8"))
        for client in ("codex", "claude"):
            bootstrap = json.loads(
                (REPO / ".boi-harness" / "bootstrap" / f"{client}.json").read_text(encoding="utf-8")
            )
            generated = managed_bootstrap(client, package, bootstrap)
            normalized = " ".join(generated.split())
            self.assertIn("turn a recurring work description into a reusable BoI Harness", normalized)
            self.assertIn("ordinary one-off document authoring", normalized)
            self.assertIn("notes/harnesses/", normalized)
            self.assertIn("load the matching profiled Harness card", generated)
            self.assertIn("Local Second Brain session check", generated)
            self.assertIn("must not require Python", generated)
            self.assertIn("agent_session_check` is true", generated)
            self.assertIn("In `explicit-only` mode", generated)
            self.assertIn("act only after an explicit natural-language request", generated)
            self.assertNotIn("run `python3 scripts/harness_sync.py verify`", generated)

        self.assertIn("Load project Skills from `.claude/skills/`", managed_bootstrap("claude", package, bootstrap))

    def test_meta_factory_and_example_collection_are_explicitly_separated(self) -> None:
        result = inspect_meta_factory(REPO)
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual("boi-harness-builder", result["meta_factory"])
        self.assertEqual("cases/", result["example_collection"])
        self.assertEqual("boi-second-brain", result["flagship_cross_cutting_harness"])
        self.assertEqual(4, result["case_count"])
        self.assertFalse(result["internal_bitbucket_verified"])

    def test_second_brain_is_flagship_and_optional_for_other_cases(self) -> None:
        catalog = json.loads((REPO / "cases" / "catalog.json").read_text(encoding="utf-8"))
        for entry in catalog["cases"]:
            case_root = REPO / "cases" / entry["path"]
            case = json.loads((case_root / "case.yaml").read_text(encoding="utf-8"))
            if entry["case_id"] == "second-brain":
                self.assertIn("boi-second-brain", case["required_skills"])
                self.assertNotIn("boi-second-brain", case["optional_features"])
                continue
            self.assertNotIn("boi-second-brain", case["required_skills"], entry["case_id"])
            self.assertIn("boi-second-brain", case["optional_features"], entry["case_id"])
            case_page = (case_root / "CASE.md").read_text(encoding="utf-8")
            walkthrough = (case_root / "walkthrough" / "01-run.md").read_text(encoding="utf-8")
            self.assertIn("Second Brain 연결 — 선택", case_page, entry["case_id"])
            self.assertIn("Second Brain이 없어도", walkthrough, entry["case_id"])

    def test_second_brain_runtime_contract_is_employee_first(self) -> None:
        case_root = REPO / "cases" / "flagship" / "second-brain"
        case_page = (case_root / "CASE.md").read_text(encoding="utf-8")
        walkthrough = (case_root / "walkthrough" / "01-run.md").read_text(encoding="utf-8")
        folder_guide = (REPO / "templates" / "second-brain-guide" / "14-folder-auto-curation.md").read_text(
            encoding="utf-8"
        )
        orchestrator = (case_root / "orchestrator.md").read_text(encoding="utf-8")
        output_contract = (case_root / "expected" / "OUTPUT-CONTRACT.md").read_text(encoding="utf-8")
        skill = (REPO / ".agents" / "skills" / "boi-second-brain" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("현재 등급: `community`", case_page)
        self.assertIn("관리자 BENCHMARK", case_page)
        for evaluator_jargon in ("planned full-reference executions", "preserved completed executions", "v2 run artifact"):
            self.assertNotIn(evaluator_jargon, case_page)
        self.assertIn("사용자 실행 계약 잠금", orchestrator)
        self.assertIn("일반 구성원 실행의 입력 계약이 아닙니다", orchestrator)
        self.assertIn("별도 `intermediate/source-inventory.json` 파일을 기본 생성하지 않습니다", orchestrator)
        self.assertIn("불필요한 intermediate 파일이나 team 기능을 요구하지 않습니다", orchestrator)
        self.assertIn("일반 구성원 실행 결과", output_contract)
        self.assertIn("일반 사용자 산출물이 아닙니다", output_contract)
        self.assertIn("promotion-drafts/", output_contract)
        employee_output_contract = output_contract.split("## Admin/CI 평가 evidence", 1)[0]
        self.assertNotIn("└─ promotion/", employee_output_contract)
        self.assertIn("근거 문서를 다시 열 수 있는 링크", walkthrough)
        self.assertNotIn("Local path와 SHA256이 있는 citation", walkthrough)
        self.assertIn("## 5. 중단됐던 자료 정리 이어가기", walkthrough)
        self.assertIn("파일과 범위가 그대로면 추가 승인 없이 다음 묶음부터", walkthrough)
        self.assertIn("파일이 바뀌었거나 계획이 맞지 않으면 쓰기 전에 새 미리보기", walkthrough)
        self.assertIn("## 처음 정리할 때 한 번 확인", folder_guide)
        self.assertIn("이후에는 파일마다 승인을 반복하지 않습니다", folder_guide)
        self.assertIn("그대로면 다음 묶음부터 이어가고", folder_guide)
        self.assertNotIn("15-or-more-source", skill)
        self.assertNotIn("at most four unique source hashes", skill)

    def test_primary_product_entrypoints_have_no_broken_local_links(self) -> None:
        entrypoints = (
            REPO / "README_KO.md",
            REPO / "README.md",
            REPO / "templates" / "second-brain-guide" / "00-start-here.md",
            REPO / "cases" / "README.md",
            REPO / "cases" / "flagship" / "second-brain" / "CASE.md",
        )
        missing: list[str] = []
        for source in entrypoints:
            text = source.read_text(encoding="utf-8")
            for raw_target in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", text):
                target = raw_target.split("#", 1)[0].strip()
                if not target or target.startswith(("http://", "https://", "mailto:", "plugin://", "#")):
                    continue
                resolved = (source.parent / target).resolve()
                if not resolved.exists():
                    missing.append(f"{source.relative_to(REPO).as_posix()} -> {target}")
        self.assertEqual([], missing)

    def test_meta_factory_defaults_to_a_saved_local_harness_not_a_case_pack(self) -> None:
        skill_root = REPO / ".agents" / "skills" / "boi-harness-builder"
        skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        workflow = (skill_root / "references" / "factory-workflow.md").read_text(encoding="utf-8")

        self.assertIn("default result is an approved, reusable Local Harness card", workflow)
        self.assertIn("Optionally package a reusable example", workflow)
        self.assertIn("only when the user explicitly asks", skill)
        self.assertNotIn("### 4. Build the Case Pack", workflow)

    def test_codex_and_claude_skill_mirrors_match(self) -> None:
        codex_root = REPO / ".agents" / "skills"
        claude_root = REPO / ".claude" / "skills"
        codex_files = sorted(path.relative_to(codex_root) for path in codex_root.rglob("*") if path.is_file())
        claude_files = sorted(path.relative_to(claude_root) for path in claude_root.rglob("*") if path.is_file())
        self.assertEqual(codex_files, claude_files)
        for relative in codex_files:
            left = hashlib.sha256((codex_root / relative).read_bytes()).hexdigest()
            right = hashlib.sha256((claude_root / relative).read_bytes()).hexdigest()
            self.assertEqual(left, right, relative.as_posix())

    def test_agent_skill_files_are_utf8(self) -> None:
        for root in (REPO / ".agents" / "skills", REPO / ".claude" / "skills"):
            for path in root.rglob("*"):
                if path.is_file():
                    path.read_text(encoding="utf-8")

    def test_employee_check_does_not_require_python(self) -> None:
        check = (REPO / "check.cmd").read_text(encoding="utf-8").lower()
        self.assertNotIn("where python", check)
        self.assertNotIn("python 3 is required", check)
        self.assertNotIn("executionpolicy bypass", check)
        self.assertIn("executionpolicy remotesigned", check)
        self.assertIn("check.ps1", check)
        self.assertIn("-nativeonly", check)

        check_ps1 = (REPO / "check.ps1").read_text(encoding="utf-8")
        admin_update = (REPO / "scripts" / "boi_update.py").read_text(encoding="utf-8")
        self.assertIn('str(root / "check.ps1")', admin_update)
        self.assertNotIn('str(root / "check.cmd")', admin_update)
        second_brain_skill = (REPO / ".agents" / "skills" / "boi-second-brain" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("-File .\\check.ps1", second_brain_skill)
        self.assertNotIn(".\\check.cmd", second_brain_skill)
        update_ps1 = (REPO / "update.ps1").read_text(encoding="utf-8")
        self.assertIn("[switch]$NativeOnly", check_ps1)
        self.assertIn('check.ps1") -Root $Root -NativeOnly', update_ps1)
        self.assertIn("administrator CI and contract-oracle checks were not requested", check_ps1)
        self.assertIn("Get-ChildItem -LiteralPath $codexRoot -Recurse -File", check_ps1)
        self.assertIn("Core Skill file sets differ", check_ps1)
        self.assertIn("UPDATE_CORE_SKILL_FILESET_MISMATCH", update_ps1)
        manifest = json.loads((REPO / ".boi-harness" / "core-runtime-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual("boi-local-core-runtime-manifest/v1", manifest["schema"])
        self.assertIn("references/factory-workflow.md", manifest["skills"]["boi-harness-builder"])
        for required in (
            'Check-File "CLAUDE.md"',
            'Check-File ".agents/skills/boi-wiki-local/SKILL.md"',
            'Check-File ".claude/skills/boi-harness-builder/SKILL.md"',
            'Check-File ".claude/skills/boi-second-brain/SKILL.md"',
            'Check-File ".claude/skills/boi-wiki-local/SKILL.md"',
        ):
            self.assertIn(required, check_ps1)

        setup = (REPO / "setup.cmd").read_text(encoding="utf-8").lower()
        self.assertNotIn("executionpolicy bypass", setup)
        self.assertIn("executionpolicy remotesigned", setup)

        installer = (REPO / "install.ps1").read_text(encoding="utf-8").lower()
        self.assertNotIn("python", installer)
        self.assertIn("scripts/setup-native.ps1", installer)

    def test_windows_case_eval_runner_is_synthetic_and_evidence_first(self) -> None:
        runner = (REPO / "tools" / "ci" / "Invoke-CaseEval.ps1").read_text(encoding="utf-8")
        self.assertIn("ConfirmSyntheticRun", runner)
        self.assertIn("ConfirmUnsandboxedSyntheticPilot", runner)
        self.assertIn("fresh Git workspace", (REPO / "tools" / "ci" / "README.md").read_text(encoding="utf-8"))
        self.assertIn("production_evidence = $false", runner)
        self.assertIn("mcp_tools_exposed = $false", runner)
        self.assertIn("boi_remote_source_bytes = 0", runner)
        self.assertIn("selected_input_bytes", runner)
        self.assertIn("temporary_user_rule_removed", runner)
        self.assertIn("CodexSandboxMode = 'workspace-write'", runner)
        self.assertIn('windows.sandbox=\"unelevated\"', runner)
        self.assertIn("evaluated_interaction_sha256", runner)
        self.assertIn("finally", runner)
        self.assertIn("Timed-out process released without a writable stderr audit file", runner)
        self.assertIn("Start-Sleep -Milliseconds 50", runner)
        self.assertIn("selected_input_manifest_unchanged", runner)
        self.assertIn("workspace_status = $turnGitStatus", runner)
        self.assertNotIn("dangerously-bypass-approvals-and-sandbox", runner)
        self.assertNotIn("--ephemeral", runner)

        policy = (REPO / "tools" / "ci" / "codex-readonly-eval.rules").read_text(encoding="utf-8")
        for prefix in ('["git", "status"]', '["git", "ls-tree"]', '["git", "diff"]', '["git", "rev-parse"]', '["rg"]'):
            self.assertIn(prefix, policy)
        for forbidden in ("Copy-Item", "Set-Content", "Remove-Item", "Invoke-WebRequest", "curl"):
            self.assertIn(f'pattern=["{forbidden}"]', policy)
        self.assertGreaterEqual(policy.count('decision="forbidden"'), 10)

    def test_failed_windows_pilot_is_recorded_without_execution_credit(self) -> None:
        ledger = json.loads(
            (REPO / "cases" / "flagship" / "second-brain" / "evals" / "failures" / "failures.json").read_text(
                encoding="utf-8"
            )
        )
        failure = next(
            item
            for item in ledger["failures"]
            if item["failure_id"] == "windows-pilot-20260802-codex-p01-sandbox-resume"
        )
        self.assertEqual("failed", failure["result"])
        self.assertEqual(0, failure["completed_execution_credit"])
        self.assertEqual(0, failure["boi_remote_source_bytes"])
        self.assertEqual(0, failure["source_mutations"])
        self.assertEqual(8, failure["deterministic_assertions_failed"])

    def test_p01_deterministic_oracle_rejects_an_empty_workspace(self) -> None:
        from case_run_assertions import evaluate_p01

        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp)
            (run / "workspace" / "sources").mkdir(parents=True)
            (run / "control").mkdir(parents=True)
            (run / "workspace" / "sources" / "01-decision-chat.txt").write_text(
                "Durable decision: Friday at 15:00.\n",
                encoding="utf-8",
            )
            capture = {
                "changed_source_files": [],
                "selected_input_manifest_sha256_before": "a" * 64,
                "selected_input_manifest_sha256_after": "a" * 64,
                "boi_remote_activity": {
                    "mcp_writes": 0,
                    "remote_submits": 0,
                    "boi_remote_source_bytes": 0,
                },
            }
            (run / "control" / "execution-capture.json").write_text(
                json.dumps(capture),
                encoding="utf-8",
            )
            result = evaluate_p01(run, capture)
            self.assertFalse(result["passed"])
            self.assertFalse(result["assertions"]["okf_0_1"]["passed"])
            self.assertFalse(result["assertions"]["promotion_boundary"]["passed"])

    def test_p03_deterministic_oracle_rejects_missing_maintenance_outputs(self) -> None:
        from case_run_assertions import evaluate_p03

        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp)
            sources = run / "workspace" / "sources"
            sources.mkdir(parents=True)
            (run / "control").mkdir(parents=True)
            for name in (
                "02-project-update.eml",
                "03-public-web-clip.md",
                "09-public-web-clip-copy.md",
                "10-review-day-reconfirmation.txt",
            ):
                (sources / name).write_text("synthetic\n", encoding="utf-8")
            capture = {
                "changed_source_files": [],
                "selected_input_count": 4,
                "selected_input_manifest_sha256_before": "a" * 64,
                "selected_input_manifest_sha256_after": "a" * 64,
                "boi_remote_activity": {
                    "mcp_writes": 0,
                    "remote_submits": 0,
                    "boi_remote_source_bytes": 0,
                },
            }
            (run / "control" / "execution-capture.json").write_text(
                json.dumps(capture),
                encoding="utf-8",
            )
            result = evaluate_p03(run, capture)
            self.assertFalse(result["passed"])
            self.assertFalse(result["assertions"]["duplicate_handling"]["passed"])
            self.assertFalse(result["assertions"]["history_preservation"]["passed"])

    def test_p04_deterministic_oracle_rejects_an_unprocessed_source_folder(self) -> None:
        from case_run_assertions import evaluate_p04

        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp)
            sources = run / "workspace" / "sources"
            sources.mkdir(parents=True)
            (run / "control").mkdir(parents=True)
            for number in range(1, 21):
                (sources / f"{number:02d}-source.txt").write_text(f"synthetic {number}\n", encoding="utf-8")
            capture = {
                "changed_source_files": [],
                "selected_input_count": 20,
                "selected_input_manifest_sha256_before": "a" * 64,
                "selected_input_manifest_sha256_after": "a" * 64,
                "boi_remote_activity": {"mcp_writes": 0, "remote_submits": 0, "boi_remote_source_bytes": 0},
            }
            (run / "control" / "execution-capture.json").write_text(json.dumps(capture), encoding="utf-8")
            result = evaluate_p04(run, capture)
            self.assertFalse(result["passed"])
            self.assertFalse(result["assertions"]["structured_outputs"]["passed"])
            self.assertFalse(result["assertions"]["duplicate_handling"]["passed"])

    def test_p04_progress_accounts_for_new_and_already_reflected_hashes(self) -> None:
        from case_run_assertions import source_folder_progress_complete, structured_source_ref

        unique_hashes = {"a" * 64, "b" * 64, "c" * 64}
        progress = {
            "schema": "boi-local-source-folder-progress/v1",
            "approved_plan_hash": "d" * 64,
            "source_manifest_hash": "e" * 64,
            "completed_sha256": ["a" * 64, "b" * 64],
            "already_reflected_sha256": ["c" * 64],
            "remaining_source_refs": [],
            "status": "completed",
        }
        self.assertTrue(source_folder_progress_complete(progress, unique_hashes))
        progress["already_reflected_sha256"] = ["b" * 64, "c" * 64]
        self.assertFalse(source_folder_progress_complete(progress, unique_hashes))
        self.assertTrue(structured_source_ref({"type": "local-file", "ref": "sources/a", "sha256": "a" * 64}))
        self.assertTrue(structured_source_ref({"type": "local-knowledge", "ref": "notes/a.md", "note": "dependency"}))
        self.assertFalse(structured_source_ref({"type": "local-knowledge", "ref": "notes/a.md"}))

        template = json.loads((REPO / "templates" / "source-folder-progress.example.json").read_text(encoding="utf-8"))
        self.assertEqual(
            {
                "schema", "approved_plan_hash", "source_manifest_hash", "completed_sha256",
                "already_reflected_sha256", "remaining_source_refs", "next_batch", "status",
            },
            set(template),
        )
        runner = (REPO / "tools" / "ci" / "Invoke-CaseEval.ps1").read_text(encoding="utf-8")
        self.assertIn("source-folder-progress.example.json", runner)

    def test_p05_preserves_preview_then_approval_boundary(self) -> None:
        catalog = json.loads(
            (REPO / "cases" / "flagship" / "second-brain" / "evals" / "prompts" / "prompt-catalog.json")
            .read_text(encoding="utf-8")
        )
        prompt = next(item for item in catalog["prompts"] if item["prompt_id"] == "p05")
        self.assertEqual("scripted-multi-turn", prompt["interaction"]["mode"])
        self.assertEqual([1, 2], [turn["turn"] for turn in prompt["interaction"]["turns"]])
        approval = prompt["interaction"]["turns"][1]["text"]
        self.assertIn("승인", approval)
        self.assertIn("동일한 변경 확인값", approval)
        self.assertIn("원격 업로드도 하지 마", approval)
        skill = (REPO / ".agents" / "skills" / "boi-second-brain" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("the first turn is read-only", skill)
        self.assertIn("Preserve source claim identifiers", skill)
        self.assertIn("`open-question` for an unsupported claim", skill)
        self.assertIn("Do not retry the same failed write", skill)
        self.assertIn("Do not create a new index solely for a bounded review", skill)
        self.assertIn("never decisions, claim status, risk summaries, or review conclusions", skill)
        self.assertIn("canonical package checksum is not the raw `.boi-harness/package.json` file SHA256", skill)

    def test_p05_deterministic_oracle_rejects_missing_review_outputs(self) -> None:
        from case_run_assertions import evaluate_p05

        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp)
            sources = run / "workspace" / "sources"
            sources.mkdir(parents=True)
            (run / "control").mkdir(parents=True)
            for name in (
                "08-conflicting-review-day.md",
                "11-research-note.md",
                "13-onboarding-faq.md",
                "15-incident-retrospective.md",
            ):
                (sources / name).write_text(f"synthetic {name}\n", encoding="utf-8")
            capture = {
                "changed_source_files": [],
                "selected_input_count": 4,
                "selected_input_manifest_sha256_before": "a" * 64,
                "selected_input_manifest_sha256_after": "a" * 64,
                "turns": [{"changed_source_files": [], "selected_input_manifest_unchanged": True}],
                "boi_remote_activity": {"mcp_writes": 0, "remote_submits": 0, "boi_remote_source_bytes": 0},
            }
            (run / "control" / "execution-capture.json").write_text(json.dumps(capture), encoding="utf-8")
            result = evaluate_p05(run, capture)
            self.assertFalse(result["passed"])
            self.assertFalse(result["assertions"]["structured_outputs"]["passed"])
            self.assertFalse(result["assertions"]["counterevidence"]["passed"])
            self.assertFalse(result["assertions"]["unknowns"]["passed"])
            self.assertFalse(result["assertions"]["history_preservation"]["passed"])

    def test_p06_deterministic_oracle_rejects_an_uncited_empty_answer(self) -> None:
        from case_run_assertions import evaluate_p06

        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp)
            sources = run / "workspace" / "sources"
            sources.mkdir(parents=True)
            control = run / "control"
            control.mkdir(parents=True)
            for name in (
                "01-decision-chat.txt",
                "02-project-update.eml",
                "08-conflicting-review-day.md",
                "16-dictionary.md",
            ):
                (sources / name).write_text(f"synthetic {name}\n", encoding="utf-8")
            (control / "turn-01-last-message.txt").write_text("근거 없이 답할 수 없습니다.\n", encoding="utf-8")
            capture = {
                "git_status": [],
                "changed_source_files": [],
                "selected_input_count": 4,
                "selected_input_manifest_sha256_before": "a" * 64,
                "selected_input_manifest_sha256_after": "a" * 64,
                "turns": [{
                    "workspace_status": [],
                    "changed_source_files": [],
                    "selected_input_manifest_unchanged": True,
                }],
                "boi_remote_activity": {"mcp_writes": 0, "remote_submits": 0, "boi_remote_source_bytes": 0},
            }
            (control / "execution-capture.json").write_text(json.dumps(capture), encoding="utf-8")
            result = evaluate_p06(run, capture)
            self.assertFalse(result["passed"])
            self.assertFalse(result["assertions"]["grounded_citations"]["passed"])
            self.assertFalse(result["assertions"]["counterevidence"]["passed"])
            self.assertFalse(result["assertions"]["unknowns"]["passed"])

    def test_p06_oracle_accepts_korean_checklist_and_explicit_non_override(self) -> None:
        from case_run_assertions import evaluate_p06

        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp)
            sources = run / "workspace" / "sources"
            sources.mkdir(parents=True)
            control = run / "control"
            control.mkdir(parents=True)
            refs = {}
            for name in (
                "01-decision-chat.txt",
                "02-project-update.eml",
                "08-conflicting-review-day.md",
                "16-dictionary.md",
            ):
                path = sources / name
                path.write_text(f"synthetic {name}\n", encoding="utf-8")
                refs[f"sources/{name}"] = hashlib.sha256(path.read_bytes()).hexdigest()
            citations = "; ".join(f"{ref} {digest}" for ref, digest in refs.items())
            answer = (
                "## 답변\n금요일 15:00 일정은 확정입니다. Atlas Ledger가 우선이며 Blue Ledger는 별칭입니다.\n"
                f"## 출처\n{citations}\n"
                "## 반증\n목요일 15:00 메모는 미확인이며 검토된 금요일 결론을 덮어쓰지 않습니다.\n"
                "## 미확인\n사전 소유자 검토가 pending이고 첨부 체크리스트는 없습니다.\n"
                "## 다음 확인\n사전 소유자에게 확인하고 체크리스트를 요청합니다.\n"
                "## 신뢰도\n금요일 일정 높음, 사전 승인 미확인.\n"
            )
            (control / "turn-01-last-message.txt").write_text(answer, encoding="utf-8")
            capture = {
                "git_status": [],
                "changed_source_files": [],
                "selected_input_count": 4,
                "selected_input_manifest_sha256_before": "a" * 64,
                "selected_input_manifest_sha256_after": "a" * 64,
                "turns": [{
                    "workspace_status": [],
                    "changed_source_files": [],
                    "selected_input_manifest_unchanged": True,
                }],
                "boi_remote_activity": {"mcp_writes": 0, "remote_submits": 0, "boi_remote_source_bytes": 0},
            }
            (control / "execution-capture.json").write_text(json.dumps(capture), encoding="utf-8")
            result = evaluate_p06(run, capture)
            self.assertTrue(result["assertions"]["grounded_citations"]["passed"])
            self.assertTrue(result["assertions"]["counterevidence"]["passed"])
            self.assertTrue(result["assertions"]["unknowns"]["passed"])
            self.assertTrue(result["assertions"]["failure_path"]["passed"])

    def test_p07_seed_is_an_exact_approved_resume_contract(self) -> None:
        seed = REPO / "cases" / "flagship" / "second-brain" / "evals" / "seeds" / "s30-interrupted"
        plan_path = seed / ".boi-local" / "source-folder-plan.json"
        progress = json.loads((seed / ".boi-local" / "source-folder-progress.json").read_text(encoding="utf-8"))
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        canonical_manifest_hash = hashlib.sha256(
            json.dumps(plan["source_manifest"], ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        self.assertEqual("boi-local-source-folder-plan/v1", plan["schema"])
        self.assertTrue(plan["user_confirmed"])
        self.assertEqual(hashlib.sha256(plan_path.read_bytes()).hexdigest(), progress["approved_plan_hash"])
        self.assertEqual(canonical_manifest_hash, progress["source_manifest_hash"])
        self.assertEqual(9, len(progress["completed_sha256"]))
        self.assertEqual(10, len(progress["remaining_source_refs"]))
        self.assertEqual(progress["remaining_source_refs"][:4], progress["next_batch"]["source_refs"])

    def test_p07_summary_accepts_natural_korean_inflection(self) -> None:
        from case_run_assertions import p07_summary_valid

        summary = "\n".join([
            "기존 10개를 확인하고 다음 묶음만 처리했습니다.",
            "새 자료 4개를 Local Private로 정리했습니다.",
            "처리할 자료는 6개가 남았습니다.",
        ])
        self.assertTrue(p07_summary_valid(summary))

    def test_p07_readable_source_requires_useful_knowledge_not_wrapper(self) -> None:
        from case_run_assertions import p07_artifact_is_useful

        useful = """Claim A: progressive summarization is unverified because the public source is a placeholder.
Claim B is rejected as unsupported. Do not fill the missing evidence from model memory."""
        wrapper = "The source hash was recorded. A distilled page will be created later."
        self.assertTrue(p07_artifact_is_useful("sources/11-research-note.md", useful))
        self.assertFalse(p07_artifact_is_useful("sources/11-research-note.md", wrapper))

        korean = """Claim A: 점진적 요약은 공개 출처 자리표시자만 있어 미검증이다.
Claim B는 근거 없음으로 기각한다. 모델 기억으로 빈 출처를 채우지 않는다."""
        self.assertTrue(p07_artifact_is_useful("sources/11-research-note.md", korean))

        sop = """promotion 초안이다. 사람 검토자가 확인하며 실행 승인을 받지 않았다.
이 문서를 실행 지침으로 사용하지 않는다."""
        self.assertTrue(p07_artifact_is_useful("sources/12-sop-draft.md", sop))

    def test_p07_oracle_rejects_an_untouched_interrupted_seed(self) -> None:
        from case_run_assertions import evaluate_p07

        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp) / "run"
            workspace = run / "workspace"
            control = run / "control"
            profile = workspace / "data" / "boi" / "private" / "0000000"
            shutil.copytree(REPO / "cases" / "flagship" / "second-brain" / "fixtures" / "sources", workspace / "sources")
            shutil.copytree(
                REPO / "cases" / "flagship" / "second-brain" / "evals" / "seeds" / "s30-interrupted",
                profile,
                ignore=shutil.ignore_patterns("manifest.json"),
            )
            control.mkdir(parents=True)
            (control / "turn-01-last-message.txt").write_text("아직 아무 작업도 하지 않았습니다.\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q", str(workspace)], check=True)
            subprocess.run(["git", "-C", str(workspace), "add", "."], check=True)
            subprocess.run(
                ["git", "-C", str(workspace), "-c", "user.name=Eval", "-c", "user.email=eval@example.invalid", "commit", "-qm", "seed"],
                check=True,
            )
            capture = {
                "selected_input_count": 20,
                "selected_input_manifest_sha256_before": "a" * 64,
                "selected_input_manifest_sha256_after": "a" * 64,
                "changed_source_files": [],
                "turns": [{"changed_source_files": [], "selected_input_manifest_unchanged": True}],
                "boi_remote_activity": {"mcp_writes": 0, "remote_submits": 0, "boi_remote_source_bytes": 0},
            }
            (control / "execution-capture.json").write_text(json.dumps(capture), encoding="utf-8")
            result = evaluate_p07(run, capture)
            self.assertFalse(result["passed"])
            self.assertTrue(result["assertions"]["source_integrity"]["passed"])
            self.assertFalse(result["assertions"]["resume_idempotency"]["passed"])
            self.assertFalse(result["assertions"]["structured_outputs"]["passed"])

            progress_path = profile / ".boi-local" / "source-folder-progress.json"
            progress = json.loads(progress_path.read_text(encoding="utf-8"))
            progress["next_batch"] = None
            progress_path.write_text(json.dumps(progress, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            null_next_result = evaluate_p07(run, capture)
            self.assertFalse(null_next_result["passed"])
            self.assertFalse(null_next_result["assertions"]["resume_idempotency"]["passed"])

    def test_blind_bundle_keeps_read_only_completion_as_user_output(self) -> None:
        from build_blind_case_bundle import copy_outputs

        with tempfile.TemporaryDirectory() as temp:
            run = Path(temp) / "run"
            workspace = run / "workspace"
            control = run / "control"
            target = Path(temp) / "reviewer" / "A"
            workspace.mkdir(parents=True)
            control.mkdir(parents=True)
            subprocess.run(["git", "init", "-q", str(workspace)], check=True)
            (workspace / "seed.txt").write_text("synthetic\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(workspace), "add", "seed.txt"], check=True)
            subprocess.run(
                ["git", "-C", str(workspace), "-c", "user.name=Eval", "-c", "user.email=eval@example.invalid", "commit", "-qm", "seed"],
                check=True,
            )
            (control / "turn-01-last-message.txt").write_text("read-only answer\n", encoding="utf-8")
            rows = copy_outputs(run, target)
            self.assertEqual(["COMPLETION_SUMMARY.txt"], [row["path"] for row in rows])
            self.assertEqual("read-only answer\n", (target / "COMPLETION_SUMMARY.txt").read_text(encoding="utf-8"))
            self.assertFalse((target / "NO_USER_OUTPUT.txt").exists())

    def test_eval_import_namespaces_only_before_state_path_collisions(self) -> None:
        from import_case_eval_pair import copy_input_tree

        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "source"
            destination = Path(temp) / "destination"
            progress = source / "data" / "boi" / "private" / "0000000" / ".boi-local" / "source-folder-progress.json"
            raw = source / "sources" / "11-note.md"
            progress.parent.mkdir(parents=True)
            raw.parent.mkdir(parents=True)
            progress.write_text('{"status":"before"}\n', encoding="utf-8")
            raw.write_text("synthetic\n", encoding="utf-8")
            collision = progress.relative_to(source).as_posix()
            rows = copy_input_tree(source, destination, {collision})
            paths = {row["path"] for row in rows}
            self.assertIn(f"_input-before/{collision}", paths)
            self.assertIn("sources/11-note.md", paths)

    def test_blind_bundle_includes_hash_verified_existing_local_wiki_seed(self) -> None:
        from build_blind_case_bundle import copy_seed_inputs

        prompt_catalog = json.loads(
            (REPO / "cases" / "flagship" / "second-brain" / "evals" / "prompts" / "prompt-catalog.json").read_text(encoding="utf-8")
        )
        prompt = next(row for row in prompt_catalog["prompts"] if row["prompt_id"] == "p06")
        with tempfile.TemporaryDirectory() as temp:
            reviewer = Path(temp) / "reviewer-bundle"
            rows = copy_seed_inputs(
                REPO / "cases" / "flagship" / "second-brain",
                prompt,
                reviewer,
                "bb1c5719b41d0066f20805f25c6d084ce7bd44567ee39781a5c33e649d683a44",
            )
            paths = {row["path"] for row in rows}
            self.assertIn("data/boi/private/0000000/notes/knowledge/review-schedule.md", paths)
            self.assertIn("data/boi/private/0000000/notes/knowledge/atlas-ledger.md", paths)
            self.assertTrue(all(row["kind"] == "existing-local-wiki" for row in rows))

    def test_readme_is_harness_first_and_keeps_second_brain_flagship(self) -> None:
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        readme_ko = (REPO / "README_KO.md").read_text(encoding="utf-8")
        self.assertIn("Production-grade 품질 목표의 Meta Harness Candidate", readme)
        self.assertIn("production-ready를 주장하지 않습니다", readme)
        self.assertIn("Flagship Capability: boi-second-brain", readme)
        self.assertIn("Python·Obsidian·MCP는 일반 사용자 필수 요구사항이 아닙니다", readme)
        self.assertNotIn("Flagship Reference Case", readme)
        self.assertIn("Production-grade 품질 목표의 Meta Harness Candidate", readme_ko)
        self.assertIn("notes/harnesses/<이름>.md", readme_ko)
        self.assertIn("저장된 `<이름>` Harness로 이번 자료를 처리해줘", readme_ko)
        self.assertIn("clone 자체를 Codex·Claude의 작업 폴더", readme_ko)
        self.assertNotIn("Flagship Reference Case", readme_ko)
        self.assertIn("full_release_ready", readme_ko)
        self.assertNotIn("총 456회", readme)
        second_brain_skill = (REPO / ".agents" / "skills" / "boi-second-brain" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("-PreviewOnly", second_brain_skill)
        self.assertIn("-ConfirmPlanHash <approved hash>", second_brain_skill)

    def test_release_statuses_remain_false_without_external_evidence(self) -> None:
        automated = {
            "ux": {"ok": True, "checks": {"actual_boi_contract_checked": False}},
            "query_quality": {"ok": True},
            "origin": {"host": "github.com"},
            "case_harness": inspect(REPO),
        }
        result = readiness(True, automated, {"ok": False})
        self.assertTrue(result["meta_harness_ready"])
        self.assertTrue(result["case_factory_ready"])
        self.assertFalse(result["second_brain_reference_ready"])
        self.assertFalse(result["cross_runtime_eval_ready"])
        self.assertFalse(result["production_quality_gate_passed"])
        self.assertFalse(result["boi_contract_ready"])
        self.assertFalse(result["non_developer_acceptance_ready"])
        self.assertFalse(result["full_release_ready"])

        status = (REPO / "research" / "meta-harness-release-status.md").read_text(encoding="utf-8")
        self.assertIn("active 상태로 진행 중", status)
        self.assertIn("Pending external gates", status)
        for gate in ("실제 대상 BoI Wiki validator", "사내 Bitbucket", "Claude", "비개발자 Acceptance"):
            self.assertIn(gate, status)
        self.assertIn("이 네 항목의 부재는 blocker나 실패로 기록하지 않고", status)

    def test_release_screens_are_an_explicit_gate(self) -> None:
        manifest = json.loads(
            (REPO / "templates" / "second-brain-guide" / "_media" / "manifest.json").read_text(
                encoding="utf-8"
            )
        )
        pending = {
            item["id"]
            for item in manifest["items"]
            if item.get("requires_recapture_for_release") is True
        }
        self.assertEqual({f"screen-{number:02d}" for number in range(28, 35)}, pending)
        captured = {item["id"] for item in manifest["items"]}
        self.assertTrue({"screen-01", "screen-04"}.issubset(captured))
        by_id = {item["id"]: item for item in manifest["items"]}
        self.assertEqual("windows-graphics-capture", by_id["screen-01"]["capture_method"])
        self.assertEqual("windows-graphics-capture", by_id["screen-04"]["capture_method"])
        for media_id in pending:
            self.assertEqual("synthetic-training-mockup", by_id[media_id]["capture_method"])

        automated = {
            "ux": {"ok": True, "checks": {"actual_boi_contract_checked": True}},
            "query_quality": {"ok": True},
            "wiki": {"release_screen_ready": False},
            "origin": {"host": "bitbucket.internal.example"},
            "case_harness": inspect(REPO),
        }
        result = readiness(
            True,
            automated,
            {
                "ok": True,
                "obsidian_support_claimed": True,
                "domain_example_validated": True,
            },
        )
        self.assertFalse(result["release_screen_ready"])
        self.assertFalse(result["obsidian_support_ready"])
        self.assertFalse(result["full_release_ready"])


if __name__ == "__main__":
    unittest.main()
