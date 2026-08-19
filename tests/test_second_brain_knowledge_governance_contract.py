from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from local_wiki import build_query_pack


class SecondBrainKnowledgeGovernanceContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.codex = REPO / ".agents" / "skills" / "boi-second-brain"
        self.claude = REPO / ".claude" / "skills" / "boi-second-brain"

    def test_auto_curate_uses_low_risk_local_knowledge_without_document_approval(self) -> None:
        skill = (self.codex / "SKILL.md").read_text(encoding="utf-8")

        for required in (
            "Local auto-managed knowledge",
            "Do not put every source-derived or inferred page in the Review Queue",
            "conflict, low confidence, unsupported inference, material Current change, sensitive content, or sharing-scope change",
            "`observed` and `inferred` describe how a claim was formed",
            "Current is question- or decision-scoped",
        ):
            self.assertIn(required, skill)

        self.assertNotIn("Put every candidate in the review queue", skill)

    def test_current_query_contract_is_progressive_disclosure_not_a_new_runtime(self) -> None:
        skill = (self.codex / "SKILL.md").read_text(encoding="utf-8")
        for required in (
            "## Automatic source-folder maintenance",
            "references/local-current-query.md",
            "references/answer-surface-contract.md",
            "references/citation-surface-contract.md",
            "references/query-pack-v4.example.json",
            "The Query Pack is an in-memory agent contract, not an application or resident runtime",
            "ordinary question automatically continues with bounded Local discovery",
            "검토한 내용만으로 답해줘",
            "does not approve, promote, or write",
        ):
            self.assertIn(required, skill)

    def test_answer_and_citation_surface_hide_internal_audit_details(self) -> None:
        answer = (self.codex / "references" / "answer-surface-contract.md").read_text(encoding="utf-8")
        citation = (self.codex / "references" / "citation-surface-contract.md").read_text(encoding="utf-8")

        for required in (
            "Answer the question in the first paragraph",
            "`natural-expert`",
            "not a mandatory visible outline",
            "one to five plain numbered citations",
            "Never show internal L/S/D/C markers",
            "full SHA256",
            "at most one",
            "one meaning-preserving presentation repair",
            "[1] [문서 제목](notes/example.md)",
            "Do not add `자세히 보기`",
        ):
            self.assertIn(required, answer)
        for required in (
            "One evidence identity always has one display number",
            "AI synthesis never receives a source citation",
            "absolute Local paths",
            "material counterevidence or unknowns",
            "profile-relative `.md`",
            "source_markdown",
        ):
            self.assertIn(required, citation)

    def test_current_manifest_and_query_pack_are_local_question_scoped(self) -> None:
        manifest = json.loads(
            (self.codex / "references" / "current-knowledge-manifest.example.json").read_text(encoding="utf-8")
        )
        pack = json.loads((self.codex / "references" / "query-pack-v4.example.json").read_text(encoding="utf-8"))

        self.assertEqual("boi-current-knowledge-manifest/v1", manifest["schema"])
        self.assertEqual("question-or-decision", manifest["current_scope"])
        self.assertEqual([], manifest["approved_remote_artifacts"])
        self.assertTrue(manifest["local_only"])
        self.assertEqual("boi-second-brain-query-pack/v4", pack["schema"])
        self.assertEqual("local-current", pack["query_mode"])
        self.assertEqual([], pack["discovery_evidence"])
        self.assertFalse(pack["runtime"]["writes_performed"])
        self.assertEqual([], pack["shared_evidence"])

    def test_codex_claude_and_core_manifest_cover_the_same_contract_files(self) -> None:
        left = sorted(path.relative_to(self.codex) for path in self.codex.rglob("*") if path.is_file())
        right = sorted(path.relative_to(self.claude) for path in self.claude.rglob("*") if path.is_file())
        self.assertEqual(left, right)
        for relative in left:
            self.assertEqual(
                hashlib.sha256((self.codex / relative).read_bytes()).hexdigest(),
                hashlib.sha256((self.claude / relative).read_bytes()).hexdigest(),
                relative.as_posix(),
            )

        manifest = json.loads((REPO / ".boi-harness" / "core-runtime-manifest.json").read_text(encoding="utf-8"))
        actual = sorted(path.relative_to(self.codex).as_posix() for path in self.codex.rglob("*") if path.is_file())
        self.assertEqual(actual, sorted(manifest["skills"]["boi-second-brain"]))

    def test_employee_guides_use_material_change_review_boundary(self) -> None:
        auto_curate = (REPO / "templates" / "second-brain-guide" / "14-folder-auto-curation.md").read_text(
            encoding="utf-8"
        )
        grounded_query = (REPO / "templates" / "second-brain-guide" / "37-grounded-query.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Local 자동 관리 지식", auto_curate)
        self.assertIn("중요한 판단 변화", auto_curate)
        self.assertNotIn("모든 새 후보는 review queue에 둡니다", auto_curate)
        self.assertIn("사용자 답변에는 `[1]`부터 `[5]`", grounded_query)
        self.assertIn("기본 답변에는 전체 SHA256과 절대 경로를 노출하지 않습니다", grounded_query)

    def test_query_pack_traverses_topic_knowledge_to_original_source_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profile = root / "data" / "boi" / "private" / "2055186"
            knowledge = profile / "notes" / "knowledge"
            raw = root / "inbox" / "paper.md"
            knowledge.mkdir(parents=True)
            raw.parent.mkdir(parents=True)
            raw.write_text("RAG keeps external source memory separate and replaceable.\n", encoding="utf-8")
            raw_sha = hashlib.sha256(raw.read_bytes()).hexdigest()

            source = knowledge / "paper-source.md"
            source.write_text(
                """---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-knowledge-note
title: "Source 001"
description: "기초 기록"
boi_id: boi:private:2055186:source:rag
visibility: local-private
classification: internal
owner: "2055186"
employee_id: "2055186"
local_owner_ref: local-private:2055186
local_only: true
promotion_status: local_only
archive_status: active
artifact_visibility: memory
lifecycle_state: memory
review_after: 2026-09-13
contains_sensitive: false
claim_status: observed
evidence_id: rag-paper
evidence_type: document
evidence_sha256: "%s"
raw_path: "%s"
origin_ref: "https://example.org/rag-paper"
source_refs:
  - type: local-file
    ref: "%s"
    sha256: "%s"
generated_from:
  - type: local-file
    ref: "%s"
    sha256: "%s"
---

# Source 001

외부 메모리와 내부 파라미터를 분리한다.
"""
                % (raw_sha, raw.as_posix(), raw.as_posix(), raw_sha, raw.as_posix(), raw_sha),
                encoding="utf-8",
            )
            source_sha = hashlib.sha256(source.read_bytes()).hexdigest()

            topic = knowledge / "topic-source-to-knowledge.md"
            topic.write_text(
                """---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-knowledge-note
title: "원문에서 지식으로"
description: "원문 보존과 근거 기반 질문을 통합한 주제 지식"
boi_id: boi:private:2055186:topic:source-to-knowledge
visibility: local-private
classification: internal
owner: "2055186"
employee_id: "2055186"
local_owner_ref: local-private:2055186
local_only: true
promotion_status: local_only
archive_status: active
artifact_visibility: memory
lifecycle_state: memory
review_after: 2026-09-13
contains_sensitive: false
claim_status: inferred
knowledge_role: comparison
case_id: ai-research-second-brain
source_refs:
  - type: local-knowledge
    ref: "data/boi/private/2055186/notes/knowledge/paper-source.md"
    sha256: "%s"
generated_from:
  - type: local-knowledge
    ref: "data/boi/private/2055186/notes/knowledge/paper-source.md"
    sha256: "%s"
---

# 원문에서 지식으로

제타카파 연결은 주제 지식에서 근거 원문으로 이어진다.
"""
                % (source_sha, source_sha),
                encoding="utf-8",
            )

            presentation = profile / "reports" / "ai-research-second-brain" / "broadcast-cue.md"
            presentation.parent.mkdir(parents=True)
            presentation.write_text(
                """---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-knowledge-note
title: "방송 큐시트"
description: "질의 결과를 설명하기 위한 발표 지원물"
boi_id: boi:private:2055186:presentation:broadcast-cue
visibility: local-private
classification: internal
owner: "2055186"
employee_id: "2055186"
local_owner_ref: local-private:2055186
local_only: true
promotion_status: local_only
archive_status: active
artifact_visibility: memory
lifecycle_state: memory
review_after: 2026-09-13
contains_sensitive: false
claim_status: inferred
knowledge_role: comparison
knowledge_subtype: presentation-support
case_id: ai-research-second-brain
---

# 방송 큐시트

제타카파 연결을 설명하는 발표 문서다.
""",
                encoding="utf-8",
            )

            pack = build_query_pack(
                root,
                "2055186",
                "제타카파 연결은 무엇인가?",
                "ai-research-second-brain",
                8,
                [],
            )

            self.assertEqual(1, len(pack["evidence_sources"]))
            evidence = pack["evidence_sources"][0]
            self.assertEqual("source-evidence", evidence["layer"])
            self.assertEqual("rag-paper", evidence["evidence_id"])
            self.assertEqual(raw_sha, evidence["sha256"])
            self.assertEqual("verified", evidence["raw_integrity"])
            self.assertNotIn(
                "data/boi/private/2055186/reports/ai-research-second-brain/broadcast-cue.md",
                {item["path"] for item in pack["compiled_sources"]},
            )
            self.assertEqual("paper-source.md", Path(evidence["source_note_path"]).name)
            self.assertEqual(
                [
                    {
                        "display_id": "[1]",
                        "evidence_id": "rag-paper",
                        "title": "Source 001",
                        "open_target": "notes/knowledge/paper-source.md",
                        "source_markdown": "[1] [Source 001](notes/knowledge/paper-source.md)",
                    }
                ],
                pack["citation_surface"]["display_map"],
            )

    def test_native_intake_resumes_exact_plan_when_only_mtime_changes(self) -> None:
        powershell = shutil.which("powershell.exe") or shutil.which("powershell")
        if not powershell:
            self.skipTest("Windows PowerShell is not available")

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source"
            state = root / ".boi-local"
            source.mkdir()
            state.mkdir()
            paper = source / "paper.md"
            paper.write_text("# Stable source\n\nThe bytes do not change.\n", encoding="utf-8")
            digest = hashlib.sha256(paper.read_bytes()).hexdigest()
            manifest = [{"path": "paper.md", "sha256": digest, "bytes": paper.stat().st_size}]
            manifest_hash = hashlib.sha256(
                json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            plan = {
                "schema": "boi-local-source-folder-plan/v1",
                "employee_id": "2055186",
                "scope": "local-private",
                "preserve_originals": True,
                "remote_auto_upload": False,
                "user_confirmed": True,
                "source_folder": str(source.resolve()),
                "source_manifest_hash": manifest_hash,
                "source_manifest": manifest,
                "ordered_batches": [{"batch_id": "batch-01", "source_refs": ["paper.md"]}],
            }
            plan_path = state / "source-folder-plan.json"
            plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            approved_plan_bytes = plan_path.read_bytes()
            progress = {
                "schema": "boi-local-source-folder-progress/v1",
                "approved_plan_hash": hashlib.sha256(plan_path.read_bytes()).hexdigest(),
                "source_manifest_hash": manifest_hash,
                "completed_sha256": [digest],
                "already_reflected_sha256": [],
                "remaining_source_refs": [],
                "next_batch": {},
                "status": "completed",
            }
            progress_path = state / "source-folder-progress.json"
            progress_path.write_text(json.dumps(progress, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            def inventory() -> dict[str, object]:
                result = subprocess.run(
                    [
                        powershell,
                        "-NoLogo",
                        "-NoProfile",
                        "-ExecutionPolicy",
                        "Bypass",
                        "-File",
                        str(REPO / "scripts" / "common-source-intake.ps1"),
                        "-SourceFolder",
                        str(source),
                        "-ConversationMode",
                        "auto-curate",
                        "-ExplicitRequest",
                        "-ProgressPath",
                        str(progress_path),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                return json.loads(result.stdout)

            first = inventory()
            self.assertEqual("no-change", first["status"], first)
            self.assertTrue(first["resume_contract_valid"])
            self.assertEqual(manifest_hash, first["source_manifest_hash"])
            self.assertEqual([], first["remaining_source_refs"])
            self.assertEqual({}, first["next_batch"])
            self.assertFalse(first["writes_performed"])

            stat = paper.stat()
            os.utime(paper, (stat.st_atime + 10, stat.st_mtime + 10))
            mtime_only = inventory()
            self.assertEqual("no-change", mtime_only["status"])
            self.assertTrue(mtime_only["resume_contract_valid"])
            self.assertEqual(manifest_hash, mtime_only["source_manifest_hash"])

            plan_path.write_bytes(approved_plan_bytes + b"\n")
            plan_tampered = inventory()
            self.assertEqual("preview-required", plan_tampered["status"])
            self.assertFalse(plan_tampered["resume_contract_valid"])
            self.assertEqual("approved-plan-hash-mismatch", plan_tampered["resume_invalidation_reason"])
            plan_path.write_bytes(approved_plan_bytes)

            paper.write_text("# Stable source\n\nThe bytes changed.\n", encoding="utf-8")
            changed = inventory()
            self.assertEqual("preview-required", changed["status"])
            self.assertFalse(changed["resume_contract_valid"])
            self.assertEqual("source-manifest-changed", changed["resume_invalidation_reason"])


if __name__ == "__main__":
    unittest.main()
