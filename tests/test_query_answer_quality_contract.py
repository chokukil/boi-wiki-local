from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import os
from pathlib import Path
from unittest import mock


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import query_quality
import local_wiki
from local_wiki import build_query_pack, query_facets, query_intent


def powershell_executable() -> str:
    """Resolve powershell.exe on PATH, else the WSL-mounted Windows copy."""
    found = shutil.which("powershell.exe") or shutil.which("powershell")
    if found:
        return found
    wsl_fallback = Path("/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe")
    if wsl_fallback.exists():
        return str(wsl_fallback)
    return "powershell.exe"


class QueryAnswerQualityContractTests(unittest.TestCase):
    def test_ordinary_query_falls_back_to_verified_review_markdown_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            review = root / "data" / "boi" / "private" / "1234567" / "notes" / "review"
            review.mkdir(parents=True)
            candidate = review / "ai-design-lab.md"
            candidate.write_text(
                '''---
type: boi/local-knowledge-note
title: "SK하이닉스 AI Design Lab 채용·조직 소개"
boi_id: boi:private:1234567:review:ai-design-lab
knowledge_role: comparison
claim_status: observed
curation_status: review-required
memory_candidate: true
---

AI Design Lab은 AI Board 운영과 현업의 AI 활용 확산을 지원하는 조직으로 소개된다.
''',
                encoding="utf-8",
            )
            before = {path: path.read_bytes() for path in root.rglob("*") if path.is_file()}

            pack = build_query_pack(root, "1234567", "AI Design Lab이 뭐니?", "", 8, [])

            after = {path: path.read_bytes() for path in root.rglob("*") if path.is_file()}
            self.assertEqual(before, after)
            self.assertEqual("ordinary-local-candidate", pack["retrieval_scope"])
            self.assertEqual([], pack["compiled_sources"])
            self.assertIn("discovery_evidence", pack)
            self.assertEqual(1, len(pack["discovery_evidence"]))
            evidence = pack["discovery_evidence"][0]
            self.assertFalse(evidence["current_authority"])
            self.assertEqual("review", evidence["state"])
            self.assertEqual("내 자료 · 검토 중", evidence["status"])
            self.assertEqual("notes/review/ai-design-lab.md", evidence["open_target"])
            self.assertEqual(hashlib.sha256(candidate.read_bytes()).hexdigest(), evidence["sha256"])
            self.assertEqual(
                {
                    "display_id": "[1]",
                    "evidence_id": evidence["evidence_id"],
                    "title": "SK하이닉스 AI Design Lab 채용·조직 소개",
                    "open_target": "notes/review/ai-design-lab.md",
                    "status": "내 자료 · 검토 중",
                    "source_markdown": "[1] [SK하이닉스 AI Design Lab 채용·조직 소개](notes/review/ai-design-lab.md) — 내 자료 · 검토 중",
                },
                pack["citation_surface"]["display_map"][0],
            )
            answer = (
                "AI Design Lab은 AI Board 운영과 현업의 AI 활용 확산을 지원하는 조직으로 소개돼 있어요.[1]\n"
                "다만 이 답변은 아직 검토 중인 소개 자료를 바탕으로 했습니다.[1]\n\n"
                "출처\n"
                f"{pack['citation_surface']['display_map'][0]['source_markdown']}\n"
            )
            self.assertEqual(
                [],
                local_wiki.validate_answer_source_list(
                    root / "data" / "boi" / "private" / "1234567",
                    answer,
                    pack["citation_surface"]["display_map"],
                ),
            )
            for internal_term in ("Current", "Candidate", "Manifest", "승인 지식", "현재 채택", "자세히 보기"):
                self.assertNotIn(internal_term, answer)
            self.assertFalse(pack["runtime"]["writes_performed"])

    def test_review_candidate_is_not_selected_when_reviewed_knowledge_matches(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profile = root / "data" / "boi" / "private" / "1234567"
            knowledge = profile / "notes" / "knowledge"
            review = profile / "notes" / "review"
            knowledge.mkdir(parents=True)
            review.mkdir(parents=True)
            (knowledge / "ai-design-lab.md").write_text(
                '''---
type: boi/local-knowledge-note
title: "검토한 AI Design Lab 설명"
boi_id: boi:private:1234567:knowledge:ai-design-lab
knowledge_role: comparison
case_id: ai-design-lab
claim_status: direct
memory_candidate: false
---

AI Design Lab은 현업 AI 활용을 지원한다.
''',
                encoding="utf-8",
            )
            (review / "ai-design-lab-change.md").write_text(
                '''---
type: boi/local-knowledge-note
title: "AI Design Lab 변경 후보"
boi_id: boi:private:1234567:review:ai-design-lab-change
knowledge_role: comparison
case_id: ai-design-lab
claim_status: conflicted
curation_status: review-required
memory_candidate: true
---

AI Design Lab의 역할이 달라졌다는 검토 전 주장이다.
''',
                encoding="utf-8",
            )

            pack = build_query_pack(root, "1234567", "AI Design Lab은 무엇인가?", "ai-design-lab", 8, [])

            self.assertEqual("ordinary-research", pack["retrieval_scope"])
            self.assertEqual(
                ["data/boi/private/1234567/notes/knowledge/ai-design-lab.md"],
                [row["path"] for row in pack["compiled_sources"]],
            )
            self.assertEqual([], pack["discovery_evidence"])

    def test_direct_local_markdown_is_labeled_discovery_not_reviewed_knowledge(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            notes = root / "data" / "boi" / "private" / "1234567" / "notes"
            notes.mkdir(parents=True)
            note = notes / "ai-design-lab.md"
            note.write_text(
                '''---
type: boi/local-note
title: "AI Design Lab 메모"
boi_id: boi:private:1234567:note:ai-design-lab
claim_status: observed
memory_candidate: true
---

AI Design Lab은 현업의 AI 활용 확산을 지원한다.
''',
                encoding="utf-8",
            )

            pack = build_query_pack(root, "1234567", "AI Design Lab이 뭐니?", "", 8, [])

            self.assertEqual([], pack["compiled_sources"])
            self.assertEqual("ordinary-local-candidate", pack["retrieval_scope"])
            self.assertEqual(1, len(pack["discovery_evidence"]))
            evidence = pack["discovery_evidence"][0]
            self.assertEqual("candidate", evidence["state"])
            self.assertEqual("내 자료 · 검토 전", evidence["status"])
            self.assertEqual("notes/ai-design-lab.md", evidence["open_target"])

    def test_source_candidate_nested_under_knowledge_stays_discovery_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profile = root / "data" / "boi" / "private" / "1234567"
            candidates = profile / "notes" / "knowledge" / "source-candidates"
            candidates.mkdir(parents=True)
            candidate = candidates / "ai-design-lab.md"
            candidate.write_text(
                '''---
type: boi/local-knowledge-note
title: "SK하이닉스 AI Design Lab 채용·조직 소개"
boi_id: boi:private:1234567:source-knowledge:ai-design-lab
visibility: local-private
local_only: true
promotion_status: local_only
archive_status: active
artifact_visibility: memory
lifecycle_state: memory
memory_candidate: true
claim_status: observed
---

AI Design Lab은 현업의 AI 활용 확산을 지원하는 조직으로 소개된다.
''',
                encoding="utf-8",
            )
            before = {path: path.read_bytes() for path in root.rglob("*") if path.is_file()}

            pack = build_query_pack(root, "1234567", "AI Design Lab이 뭐니?", "", 8, [])

            after = {path: path.read_bytes() for path in root.rglob("*") if path.is_file()}
            self.assertEqual(before, after)
            self.assertEqual([], pack["compiled_sources"])
            self.assertEqual("ordinary-local-candidate", pack["retrieval_scope"])
            self.assertEqual(1, len(pack["discovery_evidence"]))
            evidence = pack["discovery_evidence"][0]
            self.assertEqual("candidate", evidence["state"])
            self.assertEqual("내 자료 · 검토 전", evidence["status"])
            self.assertEqual(
                "notes/knowledge/source-candidates/ai-design-lab.md",
                evidence["open_target"],
            )
            self.assertEqual(hashlib.sha256(candidate.read_bytes()).hexdigest(), evidence["sha256"])
            self.assertFalse(pack["runtime"]["writes_performed"])

    def test_profile_markdown_open_target_rejects_unsafe_or_non_markdown_paths(self) -> None:
        self.assertTrue(hasattr(local_wiki, "safe_profile_markdown_target"))
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profile = root / "data" / "boi" / "private" / "1234567"
            note = profile / "notes" / "knowledge" / "safe.md"
            note.parent.mkdir(parents=True)
            note.write_text("safe", encoding="utf-8")
            outside = root / "outside.md"
            outside.write_text("outside", encoding="utf-8")
            text_file = profile / "notes" / "knowledge" / "unsafe.txt"
            text_file.write_text("unsafe", encoding="utf-8")
            anchored = profile / "notes" / "knowledge" / "unsafe#heading.md"
            anchored.write_text("unsafe", encoding="utf-8")

            self.assertEqual(
                "notes/knowledge/safe.md",
                local_wiki.safe_profile_markdown_target(profile, note),
            )
            with self.assertRaisesRegex(ValueError, "inside the Local Private profile"):
                local_wiki.safe_profile_markdown_target(profile, outside)
            with self.assertRaisesRegex(ValueError, "explicit .md extension"):
                local_wiki.safe_profile_markdown_target(profile, text_file)
            with self.assertRaisesRegex(ValueError, "heading anchors"):
                local_wiki.safe_profile_markdown_target(profile, anchored)

    def test_plain_source_block_is_not_treated_as_a_material_answer_paragraph(self) -> None:
        text = (
            "AI Design Lab은 현업의 AI 활용을 지원합니다.[1]\n\n"
            "출처\n"
            "[1] [AI Design Lab 소개](notes/review/ai-design-lab.md) — 내 자료 · 검토 전\n"
        )
        self.assertEqual(
            ["AI Design Lab은 현업의 AI 활용을 지원합니다.[1]"],
            local_wiki.answer_material_paragraphs(text),
        )

    def test_answer_source_list_rejects_manipulated_unused_and_dead_links(self) -> None:
        self.assertTrue(hasattr(local_wiki, "validate_answer_source_list"))
        with tempfile.TemporaryDirectory() as temp:
            profile = Path(temp)
            source = profile / "notes" / "review" / "ai-design-lab.md"
            source.parent.mkdir(parents=True)
            source.write_text("AI Design Lab source", encoding="utf-8")
            display_map = [
                {
                    "display_id": "[1]",
                    "evidence_id": "local-source",
                    "title": "AI Design Lab 소개",
                    "open_target": "notes/review/ai-design-lab.md",
                    "status": "내 자료 · 검토 전",
                    "source_markdown": "[1] [AI Design Lab 소개](notes/review/ai-design-lab.md) — 내 자료 · 검토 전",
                }
            ]
            valid = (
                "AI Design Lab은 현업의 AI 활용을 지원합니다.[1]\n\n"
                "출처\n"
                "[1] [AI Design Lab 소개](notes/review/ai-design-lab.md) — 내 자료 · 검토 전\n"
            )
            self.assertEqual([], local_wiki.validate_answer_source_list(profile, valid, display_map))

            manipulated = valid.replace("[1] [AI Design", "[2] [AI Design")
            self.assertIn(
                "source-list-mismatch",
                local_wiki.validate_answer_source_list(profile, manipulated, display_map),
            )
            unused = valid.replace(".[1]", ".")
            self.assertIn(
                "unused-source-line",
                local_wiki.validate_answer_source_list(profile, unused, display_map),
            )
            source.unlink()
            self.assertIn(
                "dead-or-unsafe-open-target",
                local_wiki.validate_answer_source_list(profile, valid, display_map),
            )

    def test_check_wrapper_explicit_template_environment_overrides_private_dotenv(self) -> None:
        environment = {**os.environ, "BOI_LOCAL_EMPLOYEE_ID": "0000000"}
        result = subprocess.run(
            [
                powershell_executable(),
                "-NoLogo",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(REPO / "check.ps1"),
                "-NativeOnly",
            ],
            cwd=REPO,
            env=environment,
            text=True,
            capture_output=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("validation target: 0000000 (environment-template)", result.stdout)

    def test_source_list_marker_without_narrative_claim_is_not_evidence_binding(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            raw = root / "paper.md"
            raw.write_text("original evidence\n", encoding="utf-8")
            digest = hashlib.sha256(raw.read_bytes()).hexdigest()
            text = "The material answer paragraph has no citation.\n\n## Sources\n\n- [1] Original evidence\n"
            answer = {
                "ok": True,
                "path": "data/boi/private/1234567/reports/answer.md",
                "body": text,
                "text": text,
                "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            }
            pack = {
                "citation_surface": {
                    "display_map": [{"display_id": "[1]", "evidence_id": "paper", "title": "Original"}]
                },
                "evidence_sources": [
                    {
                        "evidence_id": "paper",
                        "path": "source-note.md",
                        "raw_path": raw.as_posix(),
                        "sha256": digest,
                        "layer": "source-evidence",
                        "raw_integrity": "verified",
                    }
                ],
            }
            result = query_quality.evaluate_evidence_binding(
                root,
                pack,
                {"minimum_citations": 1, "required_citation_ids": ["paper"]},
                answer,
            )

            self.assertFalse(result["ok"], result)
            self.assertIn("citation_count", {row["name"] for row in result["checks"] if not row["ok"]})

    def test_claims_bind_to_verified_discovery_evidence_not_search_results(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            note = root / "data" / "boi" / "private" / "1234567" / "notes" / "review" / "candidate.md"
            note.parent.mkdir(parents=True)
            note.write_text("Verified candidate bytes", encoding="utf-8")
            digest = hashlib.sha256(note.read_bytes()).hexdigest()
            answer_text = "This claim comes from a verified Local candidate. [1]\n"
            answer = {
                "ok": True,
                "path": "data/boi/private/1234567/reports/answer.md",
                "body": answer_text,
                "text": answer_text,
                "sha256": hashlib.sha256(answer_text.encode("utf-8")).hexdigest(),
            }
            display = [{"display_id": "[1]", "evidence_id": "local-candidate", "title": "Candidate"}]
            evidence = {
                "evidence_id": "local-candidate",
                "path": "data/boi/private/1234567/notes/review/candidate.md",
                "sha256": digest,
                "layer": "discovery-evidence",
                "source_integrity": "sha256-verified",
                "current_authority": False,
            }
            item = {
                "minimum_citations": 1,
                "required_citation_ids": ["local-candidate"],
                "citation_evidence_route": "local-discovery",
            }

            verified = query_quality.evaluate_evidence_binding(
                root,
                {
                    "citation_surface": {"display_map": display},
                    "evidence_sources": [],
                    "discovery_results": [{"evidence_id": "local-candidate"}],
                    "discovery_evidence": [evidence],
                },
                item,
                answer,
            )
            self.assertTrue(verified["ok"], verified)
            self.assertIn(
                "citations_are_verified_discovery_evidence",
                {row["name"] for row in verified["checks"] if row["ok"]},
            )

            search_only = query_quality.evaluate_evidence_binding(
                root,
                {
                    "citation_surface": {"display_map": display},
                    "evidence_sources": [],
                    "discovery_results": [{"evidence_id": "local-candidate"}],
                    "discovery_evidence": [],
                },
                item,
                answer,
            )
            self.assertFalse(search_only["ok"], search_only)

    def test_question_purpose_is_not_a_keyword_vote(self) -> None:
        self.assertEqual(
            "synthesis",
            query_intent(
                "AI 논문 세컨드 브레인은 원문을 어떻게 보존하고 지식으로 정리하며 "
                "근거 있는 답변을 만들고 새 논문에 따라 기존 지식을 어떻게 검증·갱신해야 하는가?"
            ),
        )
        self.assertEqual(
            "comparison",
            query_intent("GraphRAG와 온톨로지는 어떤 질문에서 유용하고 언제 일반 RAG면 충분한가?"),
        )
        self.assertEqual(
            "decision",
            query_intent("사람 손을 최소화하면서 검증 책임을 잃지 않으려면 승인 경계를 어디에 두어야 하는가?"),
        )
        self.assertEqual(
            ["conflict-resolution", "temporal-validity", "memory-evolution"],
            query_facets("논문 결론이 충돌하면 질문별 Current 지식을 어떻게 유지하는가?"),
        )
        self.assertEqual(
            ["quality-evaluation", "context-selection-risk", "claim-diagnosis"],
            query_facets("논문과 그래프의 규모가 커지면 답변 품질도 자동으로 좋아지는가?"),
        )
        self.assertEqual(
            ["approval-boundary", "claim-diagnosis", "automated-evaluation"],
            query_facets("사람 손을 최소화하면서 검증 책임을 잃지 않으려면 승인 경계를 어디에 두어야 하는가?"),
        )
        self.assertEqual(
            ["retrieval-vs-persistent", "retrieval-foundation", "wiki-persistence", "wiki-synthesis-limit"],
            query_facets("일반 RAG와 LLM Wiki형 세컨드 브레인의 차이는 무엇인가?"),
        )

    def test_ordinary_research_query_excludes_same_case_support_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profile = root / "data" / "boi" / "private" / "1234567"
            knowledge = profile / "notes" / "knowledge"
            reports = profile / "reports" / "ai-research-second-brain"
            guides = profile / "notes" / "guide"
            raw = root / "inbox" / "paper.md"
            knowledge.mkdir(parents=True)
            reports.mkdir(parents=True)
            guides.mkdir(parents=True)
            raw.parent.mkdir(parents=True)
            raw.write_text("GraphRAG supports global questions; graph construction also adds cost.\n", encoding="utf-8")
            raw_sha = hashlib.sha256(raw.read_bytes()).hexdigest()

            source = knowledge / "paper-source.md"
            source.write_text(
                f'''---
type: boi/local-knowledge-note
title: "GraphRAG paper"
boi_id: boi:private:1234567:source:graphrag
claim_status: observed
evidence_id: graphrag-paper
evidence_type: document
evidence_sha256: "{raw_sha}"
raw_path: "{raw.as_posix()}"
origin_ref: "https://example.org/graphrag"
---

GraphRAG는 전역 질문에서 유용할 수 있지만 그래프 구축 비용이 있다.
''',
                encoding="utf-8",
            )
            source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
            topic = knowledge / "topic-graph-fit.md"
            topic.write_text(
                f'''---
type: boi/local-knowledge-note
title: "GraphRAG와 일반 RAG의 질문 적합성"
boi_id: boi:private:1234567:topic:graph-fit
knowledge_role: comparison
case_id: ai-research-second-brain
claim_status: inferred
source_refs:
  - type: local-knowledge
    ref: "data/boi/private/1234567/notes/knowledge/paper-source.md"
    sha256: "{source_sha}"
---

GraphRAG와 온톨로지는 관계·전역 질문에, 일반 RAG는 단일 사실 질문에 적합하다.
''',
                encoding="utf-8",
            )
            for path, title in (
                (reports / "positioning.md", "방송 포지셔닝"),
                (reports / "source-ledger.md", "논문 원장"),
                (reports / "case-hub.md", "방송용 Case 허브"),
                (guides / "research-presentation.md", "연구 발표 안내"),
            ):
                path.write_text(
                    f'''---
type: boi/local-knowledge-note
title: "{title}"
boi_id: boi:private:1234567:support:{path.stem}
knowledge_role: comparison
case_id: ai-research-second-brain
claim_status: inferred
---

GraphRAG와 온톨로지를 방송 발표와 원장에서 설명한다.
''',
                    encoding="utf-8",
                )

            pack = build_query_pack(
                root,
                "1234567",
                "GraphRAG와 온톨로지는 어떤 질문에서 유용하고 언제 일반 RAG면 충분한가?",
                "ai-research-second-brain",
                8,
                [],
            )

            compiled = {str(item["path"]) for item in pack["compiled_sources"]}
            self.assertIn(
                "data/boi/private/1234567/notes/knowledge/topic-graph-fit.md",
                compiled,
            )
            self.assertTrue(compiled)
            self.assertTrue(all("/notes/knowledge/" in path for path in compiled), compiled)
            self.assertEqual("ordinary-research", pack["retrieval_scope"])

    def test_actual_cli_ordinary_query_excludes_every_support_class_without_case_knowledge(self) -> None:
        support_classes = {
            "report": ("notes/support/research-report.md", "boi/local-report"),
            "ledger": ("notes/support/source-ledger.md", "boi/local-knowledge-note"),
            "audit": ("notes/support/completion-audit.md", "boi/local-knowledge-note"),
            "guide": ("notes/support/research-guide.md", "boi/local-guide"),
            "presentation": ("notes/support/research-presentation.md", "boi/local-knowledge-note"),
            "broadcast": ("notes/support/broadcast-brief.md", "boi/local-knowledge-note"),
        }
        for support_class, (relative, document_type) in support_classes.items():
            with self.subTest(support_class=support_class), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                profile = root / "data" / "boi" / "private" / "1234567"
                path = profile / relative
                path.parent.mkdir(parents=True)
                path.write_text(
                    f'''---
type: {document_type}
title: "Quantum launch {support_class}"
boi_id: boi:private:1234567:support:{support_class}
knowledge_role: comparison
case_id: support-only-case
claim_status: inferred
---

Quantum launch readiness is described by this {support_class} support artifact.
''',
                    encoding="utf-8",
                )

                base_command = [
                    sys.executable,
                    str(REPO / "scripts" / "local_wiki.py"),
                    "--root",
                    str(root),
                    "--employee-id",
                    "1234567",
                    "query-pack",
                    "--question",
                    "What determines quantum launch readiness?",
                    "--case-id",
                    "support-only-case",
                ]
                ordinary = subprocess.run(base_command, cwd=REPO, text=True, capture_output=True)
                self.assertEqual(0, ordinary.returncode, ordinary.stdout + ordinary.stderr)
                ordinary_pack = json.loads(ordinary.stdout)
                self.assertEqual([], ordinary_pack["compiled_sources"], ordinary_pack)
                self.assertTrue(str(ordinary_pack["retrieval_scope"]).startswith("ordinary-"))

                support = subprocess.run(
                    [*base_command, "--query-scope", "support"],
                    cwd=REPO,
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(0, support.returncode, support.stdout + support.stderr)
                support_pack = json.loads(support.stdout)
                self.assertEqual(
                    [f"data/boi/private/1234567/{relative}"],
                    [row["path"] for row in support_pack["compiled_sources"]],
                    support_pack,
                )

    def test_query_pack_keeps_analytical_requirements_off_the_visible_outline(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profile = root / "data" / "boi" / "private" / "1234567" / "notes" / "knowledge"
            profile.mkdir(parents=True)
            (profile / "note.md").write_text(
                '''---
type: boi/local-knowledge-note
title: "RAG 비교"
boi_id: boi:private:1234567:topic:rag
knowledge_role: comparison
case_id: ai-research-second-brain
claim_status: inferred
---

일반 RAG와 LLM Wiki의 차이를 비교한다.
''',
                encoding="utf-8",
            )
            pack = build_query_pack(
                root,
                "1234567",
                "일반 RAG와 LLM Wiki형 세컨드 브레인의 차이는 무엇인가?",
                "ai-research-second-brain",
                8,
                [],
            )

            contract = pack["answer_contract"]
            self.assertNotIn("required_sections", contract)
            self.assertEqual("natural-expert", contract["presentation"]["surface_style"])
            self.assertFalse(contract["presentation"]["fixed_outline_required"])
            self.assertEqual(1, contract["presentation_critic"]["max_repairs"])

    def test_citation_surface_prioritizes_question_matching_original_not_first_topic_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            knowledge = root / "data" / "boi" / "private" / "1234567" / "notes" / "knowledge"
            raw = root / "inbox"
            knowledge.mkdir(parents=True)
            raw.mkdir(parents=True)

            def source(name: str, evidence: str, body: str) -> tuple[Path, str]:
                original = raw / f"{name}.md"
                original.write_text(body, encoding="utf-8")
                digest = hashlib.sha256(original.read_bytes()).hexdigest()
                path = knowledge / f"{name}.md"
                path.write_text(
                    f'''---
type: boi/local-knowledge-note
title: "{name}"
boi_id: boi:private:1234567:source:{name}
claim_status: observed
evidence_id: {evidence}
evidence_type: document
evidence_sha256: "{digest}"
raw_path: "{original.as_posix()}"
---

{body}
''',
                    encoding="utf-8",
                )
                return path, hashlib.sha256(path.read_bytes()).hexdigest()

            first, first_sha = source("first-source", "first", "일반적인 배경 자료다.")
            second, second_sha = source(
                "direct-source",
                "direct",
                "원문 보존과 근거 답변을 검증한다. 원문 보존, 근거 답변, 원문 검증을 직접 다룬다.",
            )
            (knowledge / "topic-first.md").write_text(
                f'''---
type: boi/local-knowledge-note
title: "원문 보존 근거 답변 검증을 여러 번 언급하는 첫 주제"
boi_id: boi:private:1234567:topic:first
knowledge_role: comparison
case_id: ai-research-second-brain
claim_status: inferred
source_refs:
  - type: local-knowledge
    ref: "data/boi/private/1234567/notes/knowledge/{first.name}"
    sha256: "{first_sha}"
---

원문 보존 근거 답변 검증 원문 보존 근거 답변 검증
''',
                encoding="utf-8",
            )
            (knowledge / "topic-second.md").write_text(
                f'''---
type: boi/local-knowledge-note
title: "보조 주제"
boi_id: boi:private:1234567:topic:second
knowledge_role: comparison
case_id: ai-research-second-brain
claim_status: inferred
source_refs:
  - type: local-knowledge
    ref: "data/boi/private/1234567/notes/knowledge/{second.name}"
    sha256: "{second_sha}"
---

관련 연구를 연결한다.
''',
                encoding="utf-8",
            )

            pack = build_query_pack(
                root,
                "1234567",
                "원문을 어떻게 보존하고 근거 답변을 검증하는가?",
                "ai-research-second-brain",
                8,
                [],
            )
            self.assertEqual("direct", pack["citation_surface"]["display_map"][0]["evidence_id"])

    def test_ascii_rag_token_does_not_match_inside_graphrag(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            knowledge = root / "data" / "boi" / "private" / "1234567" / "notes" / "knowledge"
            knowledge.mkdir(parents=True)
            for name, body in (
                ("topic-rag", "RAG는 외부 문서를 답변 문맥으로 사용한다."),
                ("topic-graphrag", "GraphRAG는 전역 관계 질문을 다룬다."),
            ):
                (knowledge / f"{name}.md").write_text(
                    f'''---
type: boi/local-knowledge-note
title: "{name}"
boi_id: boi:private:1234567:{name}
knowledge_role: comparison
case_id: ai-research-second-brain
claim_status: inferred
---

{body}
''',
                    encoding="utf-8",
                )
            pack = build_query_pack(
                root,
                "1234567",
                "일반 RAG는 무엇인가?",
                "ai-research-second-brain",
                8,
                [],
            )
            rows = {Path(str(item["path"])).stem: item for item in pack["compiled_sources"]}
            self.assertIn("rag", rows["topic-rag"]["matched_terms"])
            self.assertNotIn("rag", rows["topic-graphrag"]["matched_terms"])

    def test_pre_authored_benchmark_answer_is_not_treated_as_generated_answer(self) -> None:
        pack = {
            "query_intent": "comparison",
            "compiled_sources": [],
            "evidence_sources": [],
            "citation_surface": {"display_map": []},
            "remote_sources": [],
            "answer_contract": {},
        }
        item = {
            "id": "false-positive",
            "question": "RAG와 Wiki의 차이는?",
            "expected_intent": "comparison",
            "primary_role": "",
            "answer": {
                "direct_answer": "미리 작성한 정답",
                "supporting_evidence": ["미리 작성한 근거"],
                "counterevidence": ["미리 작성한 반대 근거"],
                "unknowns_and_limits": ["미리 작성한 한계"],
                "next_checks": ["미리 작성한 점검"],
                "confidence": "high",
                "citations": [],
            },
        }
        with tempfile.TemporaryDirectory() as temp, mock.patch.object(
            query_quality, "build_query_pack", return_value=pack
        ):
            result = query_quality.evaluate_question(Path(temp), "1234567", "case", item)

        self.assertFalse(result["quality_axes"]["answer_surface"]["ok"])
        self.assertIn(
            "generated-answer-missing",
            {check["name"] for check in result["quality_axes"]["answer_surface"]["checks"] if not check["ok"]},
        )
        self.assertNotIn("reviewed_answer", result)

    def test_answer_without_generation_receipt_fails_answer_surface_even_when_other_axes_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profile = root / "data" / "boi" / "private" / "1234567"
            raw = root / "inbox" / "paper.md"
            note = profile / "notes" / "knowledge" / "paper-source.md"
            answer = profile / "reports" / "case" / "generated-answer.md"
            raw.parent.mkdir(parents=True)
            note.parent.mkdir(parents=True)
            answer.parent.mkdir(parents=True)
            raw.write_text("RAG retrieves external evidence but retrieval does not guarantee support.\n", encoding="utf-8")
            raw_sha = hashlib.sha256(raw.read_bytes()).hexdigest()
            note.write_text(
                f'''---
type: boi/local-knowledge-note
title: "RAG paper"
evidence_id: rag-paper
evidence_sha256: "{raw_sha}"
raw_path: "{raw.as_posix()}"
origin_ref: "https://example.org/research/rag-paper"
---

RAG는 외부 근거를 검색하지만 검색 결과가 답을 지지한다고 보장하지 않는다.
''',
                encoding="utf-8",
            )
            answer.write_text(
                "일반 RAG는 질문할 때 외부 문서를 찾아 답변 문맥으로 쓰지만, "
                "지속형 Wiki는 검토 가능한 지식과 변경 이력을 유지한다. [1]\n\n"
                "다만 검색된 문서가 답을 실제로 지지하는지는 별도 검증해야 하며, "
                "이 한계 때문에 두 방식을 단순한 우열로 말할 수 없다. "
                "Wiki가 항상 우수하다는 주장은 맞지 않는다. [1]\n",
                encoding="utf-8",
            )
            pack = {
                "query_intent": "comparison",
                "retrieval_scope": "ordinary-research",
                "compiled_sources": [
                    {
                        "path": "data/boi/private/1234567/notes/knowledge/topic.md",
                        "knowledge_role": "comparison",
                    }
                ],
                "evidence_sources": [
                    {
                        "path": "data/boi/private/1234567/notes/knowledge/paper-source.md",
                        "evidence_id": "rag-paper",
                        "sha256": raw_sha,
                        "raw_path": raw.as_posix(),
                        "raw_integrity": "verified",
                        "layer": "source-evidence",
                        "origin_ref": "https://arxiv.org/abs/2005.11401",
                        "evidence_authority": "canonical-public-original",
                        "original_identity_binding": {
                            "evidence_id": "rag-paper",
                            "evidence_sha256": raw_sha,
                            "expected_origin_ref": "https://arxiv.org/abs/2005.11401",
                        },
                    }
                ],
                "citation_surface": {
                    "display_map": [{"display_id": "[1]", "evidence_id": "rag-paper", "title": "RAG paper"}]
                },
                "remote_sources": [],
                "answer_contract": {
                    "presentation": {"surface_style": "natural-expert", "fixed_outline_required": False},
                    "presentation_critic": {"max_repairs": 1},
                },
            }
            item = {
                "id": "actual-answer",
                "question": "일반 RAG와 지속형 Wiki의 차이는 무엇인가?",
                "expected_intent": "comparison",
                "expected_retrieval_scope": "ordinary-research",
                "primary_role": "comparison",
                "required_compiled_roles": ["comparison"],
                "required_evidence_ids": ["rag-paper"],
                "required_citation_ids": ["rag-paper"],
                "required_original_bindings": [
                    {
                        "evidence_id": "rag-paper",
                        "evidence_sha256": raw_sha,
                        "expected_origin_ref": "https://arxiv.org/abs/2005.11401",
                    }
                ],
                "minimum_citations": 1,
                "answer_path": "data/boi/private/1234567/reports/case/generated-answer.md",
                "must_include": ["변경 이력", "한계"],
                "must_not_include": ["Wiki가 항상 우수하다"],
            }
            with mock.patch.object(query_quality, "build_query_pack", return_value=pack):
                result = query_quality.evaluate_question(root, "1234567", "case", item)

            self.assertFalse(result["ok"], result)
            self.assertEqual(
                {"retrieval", "evidence_binding", "answer_surface"},
                set(result["quality_axes"]),
            )
            self.assertTrue(result["quality_axes"]["retrieval"]["ok"], result)
            self.assertTrue(result["quality_axes"]["evidence_binding"]["ok"], result)
            self.assertFalse(result["quality_axes"]["answer_surface"]["ok"], result)
            self.assertIn(
                "generation_receipt_missing",
                {
                    check["name"]
                    for check in result["quality_axes"]["answer_surface"]["checks"]
                    if not check["ok"]
                },
            )
            self.assertRegex(result["generated_answer"]["sha256"], r"^[0-9a-f]{64}$")

    def test_explicit_local_policy_evidence_route_does_not_masquerade_as_public_research(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            raw = root / "local-policy.md"
            raw.write_text("Local approval is required before sharing.\n", encoding="utf-8")
            digest = hashlib.sha256(raw.read_bytes()).hexdigest()
            answer_text = "Local approval is required before sharing. [1]\n"
            answer = {
                "ok": True,
                "path": "data/boi/private/1234567/reports/answer.md",
                "body": answer_text,
                "text": answer_text,
                "sha256": hashlib.sha256(answer_text.encode("utf-8")).hexdigest(),
            }
            pack = {
                "citation_surface": {
                    "display_map": [{"display_id": "[1]", "evidence_id": "local-policy", "title": "Local policy"}]
                },
                "evidence_sources": [
                    {
                        "evidence_id": "local-policy",
                        "path": "data/boi/private/1234567/notes/knowledge/local-policy.md",
                        "raw_path": raw.as_posix(),
                        "sha256": digest,
                        "layer": "source-evidence",
                        "raw_integrity": "verified",
                        "origin_ref": "",
                    }
                ],
            }
            result = query_quality.evaluate_evidence_binding(
                root,
                pack,
                {
                    "minimum_citations": 1,
                    "required_citation_ids": ["local-policy"],
                    "citation_evidence_route": "local-policy",
                },
                answer,
            )

            self.assertTrue(result["ok"], result)
            self.assertIn(
                "citations_are_explicit_local_evidence",
                {row["name"] for row in result["checks"] if row["ok"]},
            )

    def test_public_research_rejects_hash_valid_local_evidence_without_canonical_origin(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            raw = root / "private-note.md"
            raw.write_text("A private observation is not a public research original.\n", encoding="utf-8")
            digest = hashlib.sha256(raw.read_bytes()).hexdigest()
            answer_text = "A private observation is not public research. [1]\n"
            answer = {
                "ok": True,
                "path": "data/boi/private/1234567/reports/answer.md",
                "body": answer_text,
                "text": answer_text,
                "sha256": hashlib.sha256(answer_text.encode("utf-8")).hexdigest(),
            }
            pack = {
                "citation_surface": {
                    "display_map": [{"display_id": "[1]", "evidence_id": "private-note", "title": "Private note"}]
                },
                "evidence_sources": [
                    {
                        "evidence_id": "private-note",
                        "path": "data/boi/private/1234567/notes/knowledge/private-note.md",
                        "raw_path": raw.as_posix(),
                        "sha256": digest,
                        "layer": "source-evidence",
                        "raw_integrity": "verified",
                        "origin_ref": "",
                    }
                ],
            }
            result = query_quality.evaluate_evidence_binding(
                root,
                pack,
                {"minimum_citations": 1, "required_citation_ids": ["private-note"]},
                answer,
            )

            self.assertFalse(result["ok"], result)
            self.assertIn(
                "citations_are_canonical_public_originals",
                {row["name"] for row in result["checks"] if not row["ok"]},
            )

    def test_actual_cli_public_origin_accepts_only_public_domains_or_stable_scholarly_ids(self) -> None:
        rejected_origins = [
            "https://intranet/paper",
            "https://research.internal/paper",
            "https://research.local/paper",
            "https://research.localhost/paper",
            "https://research.test/paper",
            "https://research.example/paper",
            "https://research.invalid/paper",
            "https://127.0.0.1/paper",
            "https://10.20.30.40/paper",
            "https://169.254.10.20/paper",
            "https://[::1]/paper",
            "https://" + "user:password@" + "arxiv.org/abs/2005.11401",
            "ftp://arxiv.org/abs/2005.11401",
        ]
        accepted_origins = [
            "https://arxiv.org/abs/2005.11401",
            "https://aclanthology.org/2024.naacl-long.20/",
            "https://github.com/org/repository",
            "doi:10.1145/1234567.1234568",
            "arxiv:2005.11401",
            "acl:2024.naacl-long.20",
        ]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profile = root / "data" / "boi" / "private" / "1234567"
            knowledge = profile / "notes" / "knowledge"
            raw = root / "inbox" / "paper.md"
            knowledge.mkdir(parents=True)
            raw.parent.mkdir(parents=True)
            raw.write_text("RAG retrieves public research evidence.\n", encoding="utf-8")
            raw_sha = hashlib.sha256(raw.read_bytes()).hexdigest()
            source = knowledge / "paper-source.md"

            def classify(origin_ref: str, *, declare_binding: bool) -> str:
                source.write_text(
                    f'''---
type: boi/local-knowledge-note
title: "RAG public paper"
boi_id: boi:private:1234567:source:rag-public
claim_status: observed
evidence_id: rag-public-paper
evidence_type: document
evidence_sha256: "{raw_sha}"
raw_path: "{raw.as_posix()}"
origin_ref: {json.dumps(origin_ref)}
---

RAG retrieves public research evidence.
''',
                    encoding="utf-8",
                )
                command = [
                        sys.executable,
                        str(REPO / "scripts" / "local_wiki.py"),
                        "--root",
                        str(root),
                        "--employee-id",
                        "1234567",
                        "query-pack",
                        "--question",
                        "How does RAG retrieve public research evidence?",
                    ]
                if declare_binding:
                    command.extend(["--original-binding", f"rag-public-paper|{raw_sha}|{origin_ref}"])
                result = subprocess.run(
                    command,
                    cwd=REPO,
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                payload = json.loads(result.stdout)
                evidence = next(
                    item for item in payload["evidence_sources"] if item.get("evidence_id") == "rag-public-paper"
                )
                return str(evidence["evidence_authority"])

            for origin_ref in rejected_origins:
                with self.subTest(origin_ref=origin_ref):
                    self.assertEqual("local-evidence", classify(origin_ref, declare_binding=False))
            for origin_ref in accepted_origins:
                with self.subTest(origin_ref=origin_ref):
                    self.assertEqual("canonical-public-original", classify(origin_ref, declare_binding=True))

    def test_actual_cli_receipt_binds_question_plan_citations_evidence_answer_and_claims(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profile = root / "data" / "boi" / "private" / "1234567"
            knowledge = profile / "notes" / "knowledge"
            answer = profile / "reports" / "case" / "generated-answer.md"
            raw = root / "inbox" / "paper.md"
            bindings = profile / "reports" / "case" / "claim-bindings.json"
            benchmark = profile / "reports" / "case" / "benchmark.json"
            knowledge.mkdir(parents=True)
            answer.parent.mkdir(parents=True)
            raw.parent.mkdir(parents=True)
            raw.write_text(
                "RAG retrieves external evidence, while a maintained Wiki preserves reusable knowledge.\n",
                encoding="utf-8",
            )
            raw_sha = hashlib.sha256(raw.read_bytes()).hexdigest()
            source = knowledge / "paper-source.md"
            source.write_text(
                f'''---
type: boi/local-knowledge-note
title: "RAG paper"
boi_id: boi:private:1234567:source:rag
claim_status: observed
evidence_id: rag-paper
evidence_type: document
evidence_sha256: "{raw_sha}"
raw_path: "{raw.as_posix()}"
origin_ref: "https://arxiv.org/abs/2005.11401"
---

RAG retrieves external evidence, while retrieval alone does not preserve reusable knowledge.
''',
                encoding="utf-8",
            )
            source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
            (knowledge / "topic.md").write_text(
                f'''---
type: boi/local-knowledge-note
title: "RAG and Wiki comparison"
boi_id: boi:private:1234567:topic:rag-wiki
knowledge_role: comparison
case_id: receipt-case
claim_status: inferred
source_refs:
  - type: local-knowledge
    ref: "data/boi/private/1234567/notes/knowledge/paper-source.md"
    sha256: "{source_sha}"
---

RAG retrieves evidence for a question; a maintained Wiki preserves reusable knowledge.
''',
                encoding="utf-8",
            )
            answer.write_text(
                "RAG retrieves evidence for the current question, while a maintained Wiki preserves reusable knowledge and its change history. [1]\n\n"
                "This distinction does not prove that a Wiki is always superior; the right choice still depends on the question and maintenance cost. [1] [2]\n\n"
                "Human review before changing an approved baseline is a declared Local operating boundary.\n\n"
                "출처\n"
                "[1] [RAG paper](notes/knowledge/paper-source.md)\n",
                encoding="utf-8",
            )
            bindings.write_text(
                json.dumps(
                    [
                        {
                            "paragraph_index": 1,
                            "binding_kind": "supported-claim",
                            "claim": "RAG retrieval and Wiki persistence serve different purposes.",
                            "citations": ["[1]"],
                        },
                        {
                            "paragraph_index": 2,
                            "binding_kind": "counterevidence",
                            "claim": "The comparison does not establish universal Wiki superiority.",
                            "citations": ["[1]"],
                        },
                        {
                            "paragraph_index": 3,
                            "binding_kind": "local-policy",
                            "claim": "Approved baseline changes remain human-reviewed by Local policy.",
                            "citations": [],
                        },
                    ],
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            question = "Compare ordinary RAG vs a maintained Wiki."
            benchmark.write_text(
                json.dumps(
                    {
                        "schema": "boi-local-query-quality-benchmark/v2",
                        "employee_id": "1234567",
                        "case_id": "receipt-case",
                        "questions": [
                            {
                                "id": "receipt-answer",
                                "question": question,
                                "expected_intent": "comparison",
                                "expected_retrieval_scope": "ordinary-research",
                                "primary_role": "comparison",
                                "required_compiled_roles": ["comparison"],
                                "required_evidence_ids": ["rag-paper"],
                                "required_citation_ids": ["rag-paper"],
                                "required_original_bindings": [
                                    {
                                        "evidence_id": "rag-paper",
                                        "evidence_sha256": raw_sha,
                                        "expected_origin_ref": "https://arxiv.org/abs/2005.11401",
                                    }
                                ],
                                "minimum_citations": 1,
                                "answer_path": "data/boi/private/1234567/reports/case/generated-answer.md",
                            }
                        ],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            receipt_cli = subprocess.run(
                [
                    sys.executable,
                    str(REPO / "scripts" / "local_wiki.py"),
                    "--root",
                    str(root),
                    "--employee-id",
                    "1234567",
                    "answer-receipt",
                    "--question",
                    question,
                    "--case-id",
                    "receipt-case",
                    "--answer-file",
                    "data/boi/private/1234567/reports/case/generated-answer.md",
                    "--claim-bindings-file",
                    "data/boi/private/1234567/reports/case/claim-bindings.json",
                    "--original-binding",
                    f"rag-paper|{raw_sha}|https://arxiv.org/abs/2005.11401",
                ],
                cwd=REPO,
                text=True,
                capture_output=True,
            )
            self.assertNotEqual(0, receipt_cli.returncode, receipt_cli.stdout + receipt_cli.stderr)
            self.assertIn("exactly equal", receipt_cli.stdout + receipt_cli.stderr)

            answer.write_text(
                answer.read_text(encoding="utf-8").replace("[1] [2]", "[1]"),
                encoding="utf-8",
            )
            receipt_cli = subprocess.run(
                [
                    sys.executable,
                    str(REPO / "scripts" / "local_wiki.py"),
                    "--root",
                    str(root),
                    "--employee-id",
                    "1234567",
                    "answer-receipt",
                    "--question",
                    question,
                    "--case-id",
                    "receipt-case",
                    "--answer-file",
                    "data/boi/private/1234567/reports/case/generated-answer.md",
                    "--claim-bindings-file",
                    "data/boi/private/1234567/reports/case/claim-bindings.json",
                    "--original-binding",
                    f"rag-paper|{raw_sha}|https://arxiv.org/abs/2005.11401",
                ],
                cwd=REPO,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, receipt_cli.returncode, receipt_cli.stdout + receipt_cli.stderr)
            receipt_payload = json.loads(receipt_cli.stdout)
            receipt_path = root / str(receipt_payload["receipt_path"])
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertEqual("boi-local-answer-generation-receipt/v1", receipt["schema"])
            self.assertEqual("natural-expert", receipt["composer"])
            self.assertEqual(1, receipt["presentation_critic"]["max_passes"])
            self.assertEqual(3, len(receipt["claim_bindings"]))
            self.assertEqual(
                {
                    "evidence_id": "rag-paper",
                    "evidence_sha256": raw_sha,
                    "expected_origin_ref": "https://arxiv.org/abs/2005.11401",
                },
                receipt["evidence"][0]["original_identity_binding"],
            )

            quality_cli = subprocess.run(
                [
                    sys.executable,
                    str(REPO / "scripts" / "query_quality.py"),
                    "--root",
                    str(root),
                    "--benchmark",
                    "data/boi/private/1234567/reports/case/benchmark.json",
                ],
                cwd=REPO,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, quality_cli.returncode, quality_cli.stdout + quality_cli.stderr)
            bound_result = json.loads(quality_cli.stdout)
            self.assertTrue(bound_result["ok"], bound_result)

            source.write_text(
                source.read_text(encoding="utf-8").replace(
                    'origin_ref: "https://arxiv.org/abs/2005.11401"',
                    'origin_ref: "https://example.org/research/rag-paper"',
                ),
                encoding="utf-8",
            )
            quality_cli = subprocess.run(
                [
                    sys.executable,
                    str(REPO / "scripts" / "query_quality.py"),
                    "--root",
                    str(root),
                    "--benchmark",
                    "data/boi/private/1234567/reports/case/benchmark.json",
                ],
                cwd=REPO,
                text=True,
                capture_output=True,
            )
            self.assertEqual(1, quality_cli.returncode, quality_cli.stdout + quality_cli.stderr)
            unrelated = json.loads(quality_cli.stdout)
            evidence_checks = unrelated["questions"][0]["quality_axes"]["evidence_binding"]["checks"]
            self.assertIn(
                "citations_match_declared_original_identity",
                {row["name"] for row in evidence_checks if not row["ok"]},
            )

            source.write_text(
                source.read_text(encoding="utf-8").replace(
                    'origin_ref: "https://example.org/research/rag-paper"',
                    'origin_ref: "https://arxiv.org/abs/2005.11401"',
                ),
                encoding="utf-8",
            )
            restored_cli = subprocess.run(
                [
                    sys.executable,
                    str(REPO / "scripts" / "query_quality.py"),
                    "--root",
                    str(root),
                    "--benchmark",
                    "data/boi/private/1234567/reports/case/benchmark.json",
                ],
                cwd=REPO,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, restored_cli.returncode, restored_cli.stdout + restored_cli.stderr)
            result = json.loads(restored_cli.stdout)
            self.assertEqual(
                {"retrieval": 1.0, "evidence_binding": 1.0, "answer_surface": 1.0},
                result["quality_axis_scores"],
            )

            answer.write_text(answer.read_text(encoding="utf-8") + "\nStale bytes.\n", encoding="utf-8")
            stale_cli = subprocess.run(
                [
                    sys.executable,
                    str(REPO / "scripts" / "query_quality.py"),
                    "--root",
                    str(root),
                    "--benchmark",
                    "data/boi/private/1234567/reports/case/benchmark.json",
                ],
                cwd=REPO,
                text=True,
                capture_output=True,
            )
            self.assertEqual(1, stale_cli.returncode, stale_cli.stdout + stale_cli.stderr)
            stale = json.loads(stale_cli.stdout)
            checks = stale["questions"][0]["quality_axes"]["answer_surface"]["checks"]
            self.assertIn("generation_receipt_answer_binding", {row["name"] for row in checks if not row["ok"]})


if __name__ == "__main__":
    unittest.main()
