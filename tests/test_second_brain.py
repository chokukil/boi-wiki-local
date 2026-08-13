from __future__ import annotations

import json
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    from PIL import Image
except ImportError:  # Optional administrator-only screenshot mutation tests.
    Image = None


REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
sys.path.insert(0, str(SCRIPTS))

from boi_setup import desired_files, desired_guide_assets, obsidian_compatibility
from boi_local_common import local_frontmatter, parse_frontmatter, parse_frontmatter_list, workspace_employee_id
from boi_update import safe_remote
from contribution_check import inspect as inspect_contribution
from migration_audit import audit as audit_migration
from ux_acceptance import run_journey
from obsidian_plugin_check import detect_windows_runtime_version, evaluate as evaluate_obsidian_plugins
from release_evidence import validate as validate_release_evidence
from release_gate import origin_check, readiness as release_readiness
from pilot_acceptance import build_tester_evidence, domain_reviewed_candidate, evidence_path, reviewed_candidate
from query_quality import evaluate as evaluate_query_quality
from local_lint import provenance_issues


class SecondBrainCliTests(unittest.TestCase):
    def test_frontmatter_accepts_windows_utf8_bom_and_crlf(self) -> None:
        text = "\ufeff---\r\nokf_version: \"0.1\"\r\nboi_profile_version: \"0.1-local\"\r\n---\r\nBody\r\n"
        self.assertEqual("0.1", parse_frontmatter(text)["okf_version"])
        self.assertEqual("0.1-local", parse_frontmatter(text)["boi_profile_version"])

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "data" / "boi").mkdir(parents=True)
        (self.root / "data" / "boi" / "log.md").write_text("# Local BoI Log\n", encoding="utf-8")
        shutil.copytree(REPO / "templates", self.root / "templates")
        for relative in (
            "CASE.md",
            "golden-journey/runs/2026-08-06/query-diff.md",
            "golden-journey/runs/2026-08-06/t0/claim-snapshot.md",
            "golden-journey/runs/2026-08-06/t1/change-set.json",
            "golden-journey/runs/2026-08-06/t1/review-queue.md",
        ):
            source = REPO / "cases" / "research" / "agentic-ai-change-radar" / relative
            target = self.root / "cases" / "research" / "agentic-ai-change-radar" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        shutil.copy2(REPO / "harness.lock", self.root / "harness.lock")
        (self.root / ".env.example").write_text("BOI_LOCAL_ROOT=.\nBOI_LOCAL_EMPLOYEE_ID=0000000\nBOI_WIKI_PAT=\n", encoding="utf-8")
        self.employee_id = "7654321"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_cli(self, script: str, *args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run(
            [sys.executable, str(SCRIPTS / script), *args],
            cwd=REPO,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            env={**os.environ, "PYTHONUTF8": "1"},
            check=False,
        )
        self.assertEqual(expected, completed.returncode, completed.stdout + completed.stderr)
        return completed

    def setup_workspace(self) -> None:
        self.run_cli("boi_setup.py", "apply", "--root", str(self.root), "--employee-id", self.employee_id)

    def copy_core_runtime_distribution(self, target_root: Path) -> None:
        shutil.copy2(REPO / "AGENTS.md", target_root / "AGENTS.md")
        shutil.copy2(REPO / "CLAUDE.md", target_root / "CLAUDE.md")
        for runtime in (".agents", ".claude"):
            for skill_name in ("boi-harness-builder", "boi-second-brain", "boi-wiki-local"):
                shutil.copytree(
                    REPO / runtime / "skills" / skill_name,
                    target_root / runtime / "skills" / skill_name,
                )

    def copy_native_setup_distribution(self) -> None:
        shutil.copytree(REPO / "scripts", self.root / "scripts")
        shutil.copy2(REPO / "harness.lock", self.root / "harness.lock")
        shutil.copytree(REPO / ".boi-harness", self.root / ".boi-harness")
        self.copy_core_runtime_distribution(self.root)

    def test_structured_generated_from_verifies_parent_sha256(self) -> None:
        parent = self.root / "data" / "parent.txt"
        parent.write_bytes(b"immutable parent evidence\n")
        digest = hashlib.sha256(parent.read_bytes()).hexdigest()
        derived = self.root / "data" / "derived.md"
        text = (
            "---\n"
            "generated_from:\n"
            "  - type: local-file\n"
            "    ref: data/parent.txt\n"
            f"    sha256: {digest}\n"
            "---\n\nDerived knowledge.\n"
        )
        derived.write_text(text, encoding="utf-8")
        self.assertEqual([], provenance_issues(self.root, derived, text, parse_frontmatter(text)))

        parent.write_bytes(b"changed parent evidence\n")
        issues = provenance_issues(self.root, derived, text, parse_frontmatter(text))
        self.assertTrue(any("generated_from hash mismatch" in issue for issue in issues))

    def test_structured_generated_from_requires_complete_exact_identity(self) -> None:
        derived = self.root / "data" / "derived.md"
        text = (
            "---\n"
            "generated_from:\n"
            "  - type: local-file\n"
            "    ref: data/missing.txt\n"
            "---\n\nDerived knowledge.\n"
        )
        derived.write_text(text, encoding="utf-8")
        issues = provenance_issues(self.root, derived, text, parse_frontmatter(text))
        self.assertIn("generated_from item is missing SHA256: data/missing.txt", issues)
        self.assertIn("generated_from target is missing: data/missing.txt", issues)

    def test_setup_is_clean_and_non_destructive(self) -> None:
        preview = json.loads(self.run_cli("boi_setup.py", "preview", "--root", str(self.root), "--employee-id", self.employee_id).stdout)
        self.assertTrue(preview["create"])
        self.assertFalse(preview["overwrites_planned"])
        self.setup_workspace()
        base = self.root / "data" / "boi" / "private" / self.employee_id
        self.assertTrue((base / "notes" / "guide" / "00-start-here.md").exists())
        self.assertTrue((base / "notes" / "guide" / "use-cases" / "04-api-event-and-workflow.md").exists())
        self.assertTrue((base / "notes" / "guide" / "29-investigation-pattern.md").exists())
        self.assertEqual(19, len(list((base / "notes" / "guide" / "_media").glob("*.webp"))))
        self.assertTrue((base / "notes" / "guide" / "_media" / "manifest.json").exists())
        self.assertEqual(22, len(desired_guide_assets(self.root, self.employee_id)))
        self.assertEqual([base / "usage-examples" / "index.md"], list((base / "usage-examples").glob("*.md")))
        profile_index = (base / "index.md").read_text(encoding="utf-8")
        self.assertIn("# 내 BoI Wiki Local", profile_index)
        self.assertIn("[내 업무용 BoI Harness 만들기](notes/guide/02-build-your-harness.md)", profile_index)
        self.assertIn("[Flagship Second Brain 설정](notes/guide/12-ai-assisted-setup.md)", profile_index)
        self.assertIn("[승인된 개인 Harness](notes/harnesses/index.md)", profile_index)
        harness_index = (base / "notes" / "harnesses" / "index.md").read_text(encoding="utf-8")
        self.assertIn("## 새 Harness 만들기", harness_index)
        self.assertIn("## 저장된 Harness 다시 사용하기", harness_index)
        self.assertIn("## 기존 Harness 개선하기", harness_index)
        self.assertIn("직접 promotion할 수 없습니다", harness_index)

        second_preview = json.loads(self.run_cli("boi_setup.py", "preview", "--root", str(self.root), "--employee-id", self.employee_id).stdout)
        self.assertEqual([], second_preview["create"])
        self.assertEqual([], second_preview["guide_updates_available"])
        review = json.loads(self.run_cli("local_review.py", "--root", str(self.root), "--employee-id", self.employee_id, "--check").stdout)
        self.assertTrue(review["check_ok"])
        self.assertEqual(0, review["summary"]["duplicate_group_count"])

        custom = base / "notes" / "guide" / "00-start-here.md"
        custom.write_text(custom.read_text(encoding="utf-8") + "\n사용자 메모\n", encoding="utf-8")
        applied = json.loads(self.run_cli("boi_setup.py", "apply", "--root", str(self.root), "--employee-id", self.employee_id).stdout)
        self.assertIn(custom.relative_to(self.root).as_posix(), applied["guide_updates_available"])
        self.assertIn("사용자 메모", custom.read_text(encoding="utf-8"))
        self.assertEqual([], applied["overwritten"])

    def test_second_brain_skill_keeps_python_out_of_employee_runtime(self) -> None:
        skill = (REPO / ".agents" / "skills" / "boi-second-brain" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Never require Python", skill)
        self.assertIn("administrator and CI validation tools only", skill)
        self.assertIn("raw transcripts", skill)
        self.assertIn("agent-memory", skill)
        self.assertIn("source folder", skill)
        self.assertNotIn("second_brain_hook.py", skill)
        self.assertIn("templates/source-knowledge-template.md", skill)
        self.assertIn(
            "Use `templates/source-record-template.md` only for binary content the current runtime cannot inspect reliably",
            skill,
        )
        self.assertIn("A PDF or image counts as readable only after approval", skill)
        self.assertIn("Do not silently introduce OCR", skill)
        source_knowledge = (REPO / "templates" / "source-knowledge-template.md").read_text(encoding="utf-8")
        for literal in (
            'okf_version: "0.1"',
            'boi_profile_version: "0.1-local"',
            "type: boi/local-knowledge-note",
            "evidence_sha256:",
            "source_refs:",
            "generated_from:",
            "## 재사용할 지식",
            "## 근거와 반증",
            "## 불확실성과 다음 확인",
            "## 검토와 공유 경계",
        ):
            self.assertIn(literal, source_knowledge)
        for bootstrap in ("AGENTS.md", "CLAUDE.md"):
            text = (REPO / bootstrap).read_text(encoding="utf-8")
            self.assertIn("Local Second Brain session check", text)
            self.assertIn("must not require Python", text)

        common_skill = (REPO / ".agents" / "skills" / "boi-wiki-local" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("check.ps1 -NativeOnly", common_skill)
        self.assertIn("do not require Python or the full Admin/CI suite", common_skill)
        self.assertIn("do not edit an index or log", common_skill)

        update_cmd = (REPO / "update.cmd").read_text(encoding="utf-8").lower()
        update_ps1 = (REPO / "update.ps1").read_text(encoding="utf-8")
        self.assertNotIn("python", update_cmd)
        self.assertNotIn("Get-Command python", update_ps1)
        self.assertNotIn("scripts\\boi_update.py", update_ps1)
        self.assertIn("reduced offline lock/snapshot match", update_ps1)

        native_check = (REPO / "check.ps1").read_text(encoding="utf-8")
        native_contract, admin_contract = native_check.split(
            "# Admin and CI only: these files are not part of the employee Native contract.",
            1,
        )
        for required_native in (
            "boi-harness-builder/SKILL.md",
            "boi-second-brain/SKILL.md",
            "boi-wiki-local/SKILL.md",
            "templates/source-knowledge-template.md",
            "templates/source-record-template.md",
            "cases/flagship/second-brain/CASE.md",
        ):
            self.assertIn(required_native, native_contract)
        for admin_only in (
            "scripts/case_benchmark.py",
            "scripts/build_reference_case_evals.py",
            "scripts/pilot_acceptance.py",
            "scripts/boi_compatibility.py",
        ):
            self.assertNotIn(admin_only, native_contract)
            self.assertIn(admin_only, admin_contract)

    def test_readable_source_knowledge_template_instantiates_as_valid_profile(self) -> None:
        self.setup_workspace()
        base = self.root / "data" / "boi" / "private" / self.employee_id
        raw = base / "evidence" / "inbox" / "sources" / "source-note.md"
        raw.parent.mkdir(parents=True, exist_ok=True)
        raw.write_text("# 검토 원문\n\n결정은 출처와 반증을 함께 남긴다.\n", encoding="utf-8")
        digest = hashlib.sha256(raw.read_bytes()).hexdigest()
        relative_raw = raw.relative_to(self.root).as_posix()
        document = (REPO / "templates" / "source-knowledge-template.md").read_text(encoding="utf-8")
        replacements = {
            "{{title}}": "출처와 반증을 함께 남기는 검토 원칙",
            "{{timestamp}}": "2026-08-03T12:00:00+09:00",
            "{{employee_id}}": self.employee_id,
            "{{source_id}}": digest[:12],
            "{{review_after}}": "2026-08-17",
            "{{claim_status}}": "decision",
            "{{source_type}}": "web-clip",
            "{{source_sha256}}": digest,
            "{{original_filename}}": raw.name,
            "{{origin_ref}}": "manual-local-save",
            "{{local_copy_path}}": relative_raw,
            "{{reusable_knowledge}}": "검토 결론은 출처와 반증을 함께 남겨야 다시 사용할 수 있다.",
            "{{decisions_constraints_and_instructions}}": "결론만 기록하지 않고 근거·제약·검토자를 함께 기록한다.",
            "{{evidence_and_counterevidence}}": "공개 검토 원칙 https://example.com/review-principle 을 근거로 삼는다. 현재 반증 자료는 없다.",
            "{{unknowns_and_next_validation}}": "다른 문서 유형에서도 같은 원칙이 유지되는지 다음 검토에서 확인한다.",
            "{{review_state_and_local_remote_boundary}}": "Local Private 초안이며 Team/Public 공유 전 별도 검토와 promotion preview가 필요하다.",
        }
        for placeholder, value in replacements.items():
            document = document.replace(placeholder, value)
        document = document.replace("contains_sensitive: unknown", "contains_sensitive: false")
        self.assertNotIn("{{", document)
        target = base / "notes" / "knowledge" / "source-review-principle.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(document, encoding="utf-8")
        knowledge_index = target.parent / "index.md"
        knowledge_index.write_text(
            knowledge_index.read_text(encoding="utf-8")
            + "\n- [출처와 반증을 함께 남기는 검토 원칙](source-review-principle.md)\n",
            encoding="utf-8",
        )

        lint = json.loads(
            self.run_cli("local_lint.py", "--root", str(self.root), "--employee-id", self.employee_id).stdout
        )
        self.assertTrue(lint["ok"], lint)
        self.assertEqual([], lint["errors"])

        blocked = json.loads(
            self.run_cli(
                "promotion_preflight.py",
                "--root", str(self.root),
                "--employee-id", self.employee_id,
                "--source", target.relative_to(self.root).as_posix(),
                "--target-visibility", "public",
                "--reviewer", "public-knowledge-reviewer",
                expected=2,
            ).stdout
        )
        self.assertFalse(blocked["ok"])

        self.assertIn(
            "Local-only boundary wording remains in the canonical candidate; provide sanitized body and metadata",
            blocked["blockers"],
        )
        blocked_compatibility = json.loads(
            self.run_cli(
                "boi_compatibility.py",
                "--projection",
                str(self.root / blocked["remote_projection_path"]),
                expected=1,
            ).stdout
        )
        self.assertIn(
            "remote projection contains Local-only boundary wording",
            blocked_compatibility["builtin_contract"]["errors"],
        )

        sanitized = self.root / "sanitized-public-knowledge.md"
        sanitized.write_text(
            "# 출처와 반증을 함께 남기는 검토 원칙\n\n"
            "검토 결론은 출처와 반증을 함께 남겨야 다시 사용할 수 있다.\n\n"
            "공개 근거: https://example.com/review-principle\n",
            encoding="utf-8",
        )
        preflight = json.loads(
            self.run_cli(
                "promotion_preflight.py",
                "--root", str(self.root),
                "--employee-id", self.employee_id,
                "--source", target.relative_to(self.root).as_posix(),
                "--sanitized-file", str(sanitized),
                "--sanitized-description", "출처와 반증을 함께 보존하는 공개 검토 원칙",
                "--target-visibility", "public",
                "--reviewer", "public-knowledge-reviewer",
            ).stdout
        )
        self.assertTrue(preflight["ok"], preflight)
        self.assertFalse(preflight["remote_submitted"])
        projection = json.loads((self.root / preflight["remote_projection_path"]).read_text(encoding="utf-8"))
        metadata = projection["candidate"]["metadata"]
        self.assertEqual("boi/knowledge", metadata["type"])
        serialized_projection = json.dumps(projection, ensure_ascii=False)
        self.assertNotIn(self.employee_id, serialized_projection)
        self.assertNotIn("data/boi/private", serialized_projection)
        self.assertNotIn("Local Private", serialized_projection)
        self.assertFalse(projection["submit_contract"]["remote_submit_allowed"])

    def test_web_clipper_template_uses_common_source_contract_without_remote_processing(self) -> None:
        template_path = REPO / "templates" / "obsidian" / "web-clipper" / "boi-common-source.json"
        template = json.loads(template_path.read_text(encoding="utf-8"))
        self.assertEqual("0.1.0", template["schemaVersion"])
        self.assertEqual("create", template["behavior"])
        self.assertEqual("", template["path"])
        properties = {item["name"]: item["value"] for item in template["properties"]}
        self.assertEqual("web-clip", properties["source_kind"])
        for required in (
            "source_url", "source_title", "source_author", "source_site",
            "published_at", "captured_at",
        ):
            self.assertIn(required, properties)
        serialized = json.dumps(template, ensure_ascii=False)
        self.assertNotIn('{{"', serialized)
        self.assertNotIn("interpreter", serialized.lower())
        self.assertNotIn("endpoint", serialized.lower())
        self.assertNotIn("web-clips/", serialized.lower())

    def test_inspected_pdf_and_image_use_one_valid_source_knowledge_profile_each(self) -> None:
        self.setup_workspace()
        base = self.root / "data" / "boi" / "private" / self.employee_id
        sources = base / "evidence" / "inbox" / "sources"
        sources.mkdir(parents=True, exist_ok=True)
        knowledge = base / "notes" / "knowledge"
        knowledge_index = knowledge / "index.md"
        template = (REPO / "templates" / "source-knowledge-template.md").read_text(encoding="utf-8")

        links = []
        for suffix, evidence_type, inspected_scope in (
            ("pdf", "document", "1~2페이지를 직접 확인했으며 3페이지 이후는 확인하지 않았다."),
            ("png", "image", "전체 이미지를 직접 확인했으며 작은 각주 문자는 판독하지 못했다."),
        ):
            raw = sources / f"inspected-source.{suffix}"
            raw.write_bytes(f"synthetic inspected {suffix} fixture".encode("utf-8"))
            digest = hashlib.sha256(raw.read_bytes()).hexdigest()
            relative_raw = raw.relative_to(self.root).as_posix()
            title = f"확인 범위를 남긴 {suffix.upper()} 지식"
            document = template
            replacements = {
                "{{title}}": title,
                "{{timestamp}}": "2026-08-03T12:00:00+09:00",
                "{{employee_id}}": self.employee_id,
                "{{source_id}}": digest[:12],
                "{{review_after}}": "2026-08-17",
                "{{claim_status}}": "inferred",
                "{{source_type}}": evidence_type,
                "{{source_sha256}}": digest,
                "{{original_filename}}": raw.name,
                "{{origin_ref}}": "approved-local-inspection",
                "{{local_copy_path}}": relative_raw,
                "{{reusable_knowledge}}": "실제로 확인한 범위에서 재사용할 수 있는 핵심 내용을 정리한다.",
                "{{decisions_constraints_and_instructions}}": "확인한 범위 밖의 내용은 결론으로 사용하지 않는다.",
                "{{evidence_and_counterevidence}}": f"원본 SHA256과 확인 범위를 근거로 남긴다. {inspected_scope}",
                "{{unknowns_and_next_validation}}": "확인하지 못한 범위는 다음 검토 전까지 미확인으로 유지한다.",
                "{{review_state_and_local_remote_boundary}}": "Local Private 초안이며 원본이나 로컬 경로는 원격으로 보내지 않는다.",
            }
            for placeholder, value in replacements.items():
                document = document.replace(placeholder, value)
            document = document.replace("contains_sensitive: unknown", "contains_sensitive: false")
            self.assertNotIn("{{", document)
            target = knowledge / f"inspected-{suffix}-knowledge.md"
            target.write_text(document, encoding="utf-8")
            links.append(f"- [{title}]({target.name})")

        knowledge_index.write_text(
            knowledge_index.read_text(encoding="utf-8") + "\n" + "\n".join(links) + "\n",
            encoding="utf-8",
        )
        lint = json.loads(
            self.run_cli("local_lint.py", "--root", str(self.root), "--employee-id", self.employee_id).stdout
        )
        self.assertTrue(lint["ok"], lint)
        self.assertEqual([], lint["errors"])

    @unittest.skipUnless(os.name == "nt", "Windows native no-Python setup test")
    def test_native_setup_uses_windows_builtins_and_creates_preferences(self) -> None:
        self.copy_native_setup_distribution()
        inbox = self.root / "UserInbox"
        script = self.root / "scripts" / "setup-native.ps1"
        self.assertNotIn("python", script.read_text(encoding="utf-8").lower())
        self.assertIn("Windows 네이티브 설치는 WSL 경로에서 실행할 수 없습니다", script.read_text(encoding="utf-8"))
        completed = subprocess.run(
            [
                "powershell.exe", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "RemoteSigned",
                "-File", str(script), "-EmployeeId", self.employee_id,
                "-Mode", "auto-curate", "-Inbox", str(inbox), "-Approve",
            ],
            cwd=self.root,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            env={
                **os.environ,
                "PATH": os.pathsep.join(
                    part for part in os.environ.get("PATH", "").split(os.pathsep)
                    if "python" not in part.lower()
                ),
            },
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("설치 결과 확인: 통과", completed.stdout)
        preferences = json.loads(
            (self.root / "data" / "boi" / "private" / self.employee_id / ".boi-local" / "second-brain-preferences.json")
            .read_text(encoding="utf-8-sig")
        )
        self.assertEqual("boi-local-second-brain-preferences/v1", preferences["schema"])
        self.assertEqual("auto-curate", preferences["conversation_mode"])
        self.assertTrue(preferences["agent_session_check"])
        self.assertIn("알아서 반영", preferences["authorization"]["approved_summary"])
        self.assertTrue(preferences["preserve_originals"])
        self.assertFalse(preferences["copy_raw_transcripts"])
        self.assertFalse(preferences["remote_auto_upload"])
        profile = self.root / "data" / "boi" / "private" / self.employee_id
        self.assertTrue((profile / "notes" / "guide" / "12-ai-assisted-setup.md").exists())
        self.assertTrue((profile / "index.md").exists())
        self.assertTrue((profile / "inbox.md").exists())
        for folder in (
            "sop-drafts", "promotion-drafts", "action-drafts", "event-drafts", "dictionary",
            "diagrams", "context-packs", "workflow-simulations", "langflow-plans", "usage-examples",
            "notes/harnesses",
        ):
            self.assertTrue((profile / folder).is_dir(), folder)
        profile_index = (profile / "index.md").read_text(encoding="utf-8")
        self.assertIn("# 내 BoI Wiki Local", profile_index)
        self.assertIn("[승인된 개인 Harness](notes/harnesses/index.md)", profile_index)
        self.assertIn("[Flagship Second Brain 설정](notes/guide/12-ai-assisted-setup.md)", profile_index)
        harness_index = profile / "notes" / "harnesses" / "index.md"
        self.assertTrue(harness_index.is_file())
        harness_index_text = harness_index.read_text(encoding="utf-8")
        self.assertIn("# 승인된 개인 Harness", harness_index_text)
        self.assertIn("## 새 Harness 만들기", harness_index_text)
        self.assertIn("## 저장된 Harness 다시 사용하기", harness_index_text)
        self.assertIn("## 기존 Harness 개선하기", harness_index_text)
        self.assertIn("직접 promotion할 수 없습니다", harness_index_text)
        self.assertFalse((self.root / ".codex").exists())
        self.assertTrue((self.root / ".claude" / "skills" / "boi-second-brain" / "SKILL.md").exists())
        self.assertFalse((self.root / ".claude" / "settings.local.json").exists())

    @unittest.skipUnless(os.name == "nt", "Windows native hash-bound setup test")
    def test_native_setup_preview_is_non_mutating_and_apply_is_hash_bound(self) -> None:
        self.copy_native_setup_distribution()
        inbox = self.root / "HashBoundInbox"
        script = self.root / "scripts" / "setup-native.ps1"
        environment = {
            **os.environ,
            "PATH": os.pathsep.join(
                part for part in os.environ.get("PATH", "").split(os.pathsep)
                if "python" not in part.lower()
            ),
        }
        base_command = [
            "powershell.exe", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "RemoteSigned",
            "-File", str(script), "-EmployeeId", self.employee_id,
            "-Mode", "suggest", "-Inbox", str(inbox),
        ]
        preview = subprocess.run(
            [*base_command, "-PreviewOnly"],
            cwd=self.root,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            env=environment,
            check=False,
        )
        self.assertEqual(0, preview.returncode, preview.stdout + preview.stderr)
        payload = json.loads(preview.stdout)
        self.assertEqual("boi-local-setup-preview/v1", payload["schema"])
        self.assertRegex(payload["plan_hash"], r"^[0-9a-f]{64}$")
        self.assertFalse(payload["mutation_performed"])
        self.assertFalse((self.root / ".env").exists())
        self.assertFalse((self.root / "data" / "boi" / "private" / self.employee_id).exists())
        self.assertFalse(inbox.exists())

        rejected = subprocess.run(
            [*base_command, "-Approve", "-ConfirmPlanHash", "0" * 64],
            cwd=self.root,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            env=environment,
            check=False,
        )
        self.assertNotEqual(0, rejected.returncode)
        self.assertIn("승인한 설정과 현재 설정 계획이 일치하지 않습니다", rejected.stdout + rejected.stderr)
        self.assertFalse((self.root / ".env").exists())
        self.assertFalse((self.root / "data" / "boi" / "private" / self.employee_id).exists())
        self.assertFalse(inbox.exists())

        applied = subprocess.run(
            [*base_command, "-Approve", "-ConfirmPlanHash", payload["plan_hash"]],
            cwd=self.root,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            env=environment,
            check=False,
        )
        self.assertEqual(0, applied.returncode, applied.stdout + applied.stderr)
        self.assertIn("설치 결과 확인: 통과", applied.stdout)
        preferences = json.loads(
            (
                self.root
                / "data"
                / "boi"
                / "private"
                / self.employee_id
                / ".boi-local"
                / "second-brain-preferences.json"
            ).read_text(encoding="utf-8-sig")
        )
        self.assertEqual("suggest", preferences["conversation_mode"])

    @unittest.skipUnless(os.name == "nt", "Windows native explicit-only setup test")
    def test_native_setup_explicit_only_disables_session_check(self) -> None:
        self.copy_native_setup_distribution()
        inbox = self.root / "ExplicitInbox"
        completed = subprocess.run(
            [
                "powershell.exe", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "RemoteSigned",
                "-File", str(self.root / "scripts" / "setup-native.ps1"),
                "-EmployeeId", self.employee_id, "-Mode", "explicit-only",
                "-Inbox", str(inbox), "-Approve",
            ],
            cwd=self.root,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        preferences = json.loads(
            (self.root / "data" / "boi" / "private" / self.employee_id / ".boi-local" / "second-brain-preferences.json")
            .read_text(encoding="utf-8-sig")
        )
        self.assertEqual("explicit-only", preferences["conversation_mode"])
        self.assertFalse(preferences["agent_session_check"])
        self.assertIn("명시적으로 요청한", preferences["authorization"]["approved_summary"])

    @unittest.skipUnless(os.name == "nt", "Windows native no-Python update test")
    def test_native_update_preview_runs_without_python(self) -> None:
        work = self.root / "native-update-work"
        remote = self.root / "native-update-origin.git"
        work.mkdir()
        subprocess.run(["git", "init", "-b", "main"], cwd=work, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "fixture@example.com"], cwd=work, check=True)
        subprocess.run(["git", "config", "user.name", "Fixture"], cwd=work, check=True)
        shutil.copy2(REPO / "harness.lock", work / "harness.lock")
        shutil.copytree(REPO / ".boi-harness", work / ".boi-harness")
        self.copy_core_runtime_distribution(work)
        (work / "README.md").write_text("native update fixture\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=work, check=True)
        subprocess.run(["git", "commit", "-m", "fixture"], cwd=work, check=True, capture_output=True)
        subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(remote), "symbolic-ref", "HEAD", "refs/heads/main"], check=True)
        subprocess.run(["git", "remote", "add", "origin", str(remote)], cwd=work, check=True)
        subprocess.run(["git", "push", "-u", "origin", "main"], cwd=work, check=True, capture_output=True)
        subprocess.run(["git", "remote", "set-head", "origin", "-a"], cwd=work, check=True, capture_output=True)

        completed = subprocess.run(
            [
                "powershell.exe", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "RemoteSigned",
                "-File", str(REPO / "update.ps1"), "-Root", str(work),
            ],
            cwd=work,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            env={
                key: value
                for key, value in {
                    **os.environ,
                    "PATH": os.pathsep.join(
                        part for part in os.environ.get("PATH", "").split(os.pathsep)
                        if "python" not in part.lower()
                    ),
                }.items()
                if key != "BOI_LOCAL_EMPLOYEE_ID"
            },
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("Harness verification: reduced offline lock/snapshot match", completed.stdout)
        self.assertIn("Mode: PREVIEW", completed.stdout)
        self.assertIn("Preview complete", completed.stdout)

        (work / ".env").write_text("BOI_LOCAL_EMPLOYEE_ID=2345678\n", encoding="utf-8")
        conflicted = subprocess.run(
            [
                "powershell.exe", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "RemoteSigned",
                "-File", str(REPO / "update.ps1"), "-Root", str(work),
            ],
            cwd=work,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            env={**os.environ, "BOI_LOCAL_EMPLOYEE_ID": "7654321"},
            check=False,
        )
        self.assertNotEqual(0, conflicted.returncode)
        conflict_output = conflicted.stdout + conflicted.stderr
        self.assertIn("Local Private Profile", conflict_output)
        self.assertIn(".env", conflict_output)

    @unittest.skipUnless(os.name == "nt", "Windows native no-Python update apply test")
    def test_native_update_apply_fast_forwards_without_python_and_preserves_private(self) -> None:
        seed = self.root / "native-update-seed"
        remote = self.root / "native-update-apply-origin.git"
        checkout = self.root / "native-update-checkout"
        seed.mkdir()
        subprocess.run(["git", "init", "-b", "main"], cwd=seed, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "fixture@example.com"], cwd=seed, check=True)
        subprocess.run(["git", "config", "user.name", "Fixture"], cwd=seed, check=True)
        (seed / ".gitignore").write_text(".env\ndata/boi/private/7654321/\n", encoding="utf-8")
        (seed / "README.md").write_text("release 1\n", encoding="utf-8")
        (seed / "check.ps1").write_text(
            "param([string]$Root, [switch]$NativeOnly)\n"
            "if (-not $NativeOnly) { Write-Error 'update must request native-only check'; exit 9 }\n"
            "Write-Host 'native check passed'\nexit 0\n",
            encoding="utf-8",
        )
        shutil.copy2(REPO / "harness.lock", seed / "harness.lock")
        shutil.copytree(REPO / ".boi-harness", seed / ".boi-harness")
        self.copy_core_runtime_distribution(seed)
        shutil.copytree(REPO / "templates" / "second-brain-guide", seed / "templates" / "second-brain-guide")
        subprocess.run(["git", "add", "."], cwd=seed, check=True)
        subprocess.run(["git", "commit", "-m", "release 1"], cwd=seed, check=True, capture_output=True)
        subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(remote), "symbolic-ref", "HEAD", "refs/heads/main"], check=True)
        subprocess.run(["git", "remote", "add", "origin", str(remote)], cwd=seed, check=True)
        subprocess.run(["git", "push", "-u", "origin", "main"], cwd=seed, check=True, capture_output=True)
        subprocess.run(["git", "clone", str(remote), str(checkout)], check=True, capture_output=True)
        subprocess.run(["git", "remote", "set-head", "origin", "-a"], cwd=checkout, check=True, capture_output=True)

        private = checkout / "data" / "boi" / "private" / "7654321" / "notes" / "private.md"
        private.parent.mkdir(parents=True)
        private.write_text("local private fixture\n", encoding="utf-8")
        (checkout / ".env").write_text("BOI_LOCAL_EMPLOYEE_ID=7654321\n", encoding="utf-8")
        private_before = private.read_bytes()
        (seed / "README.md").write_text("release 2\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=seed, check=True)
        subprocess.run(["git", "commit", "-m", "release 2"], cwd=seed, check=True, capture_output=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=seed, check=True, capture_output=True)

        completed = subprocess.run(
            [
                "powershell.exe", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "RemoteSigned",
                "-File", str(REPO / "update.ps1"), "-Root", str(checkout), "-Apply",
                "-ConfirmGuideRelease", "3.2.0",
            ],
            cwd=checkout,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            env={
                key: value
                for key, value in {
                    **os.environ,
                    "PATH": os.pathsep.join(
                        part for part in os.environ.get("PATH", "").split(os.pathsep)
                        if "python" not in part.lower()
                    ),
                }.items()
                if key != "BOI_LOCAL_EMPLOYEE_ID"
            },
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("Mode: APPLY", completed.stdout)
        self.assertIn("Guide apply:", completed.stdout)
        self.assertIn("native check passed", completed.stdout)
        self.assertIn("Local Private content hash is unchanged", completed.stdout)
        self.assertEqual("release 2\n", (checkout / "README.md").read_text(encoding="utf-8"))
        self.assertEqual(private_before, private.read_bytes())
        self.assertTrue((checkout / "data" / "boi" / "private" / "7654321" / "notes" / "guide" / "00-start-here.md").exists())

        drifted = seed / ".claude" / "skills" / "boi-harness-builder" / "references" / "factory-workflow.md"
        drifted.write_bytes(drifted.read_bytes() + b"\n")
        subprocess.run(
            ["git", "add", ".claude/skills/boi-harness-builder/references/factory-workflow.md"],
            cwd=seed,
            check=True,
        )
        subprocess.run(["git", "commit", "-m", "broken release 3"], cwd=seed, check=True, capture_output=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=seed, check=True, capture_output=True)

        rejected = subprocess.run(
            [
                "powershell.exe", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "RemoteSigned",
                "-File", str(REPO / "update.ps1"), "-Root", str(checkout), "-Apply",
            ],
            cwd=checkout,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            env={
                key: value
                for key, value in {
                    **os.environ,
                    "PATH": os.pathsep.join(
                        part for part in os.environ.get("PATH", "").split(os.pathsep)
                        if "python" not in part.lower()
                    ),
                }.items()
                if key != "BOI_LOCAL_EMPLOYEE_ID"
            },
            check=False,
        )
        self.assertNotEqual(0, rejected.returncode)
        rejection_output = rejected.stdout + rejected.stderr
        self.assertIn("UPDATE_CORE_SKILL_MIRROR_MISMATCH", rejection_output)
        self.assertIn("boi-harness-builder", rejection_output)
        self.assertEqual("release 2\n", (checkout / "README.md").read_text(encoding="utf-8"))
        self.assertEqual(private_before, private.read_bytes())

    @unittest.skipUnless(os.name == "nt", "Windows native incomplete-clone safety test")
    def test_native_setup_rejects_incomplete_clone_before_profile_write(self) -> None:
        shutil.copytree(REPO / "scripts", self.root / "scripts")
        shutil.copy2(REPO / "harness.lock", self.root / "harness.lock")
        shutil.copytree(REPO / ".boi-harness", self.root / ".boi-harness")
        completed = subprocess.run(
            [
                "powershell.exe", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "RemoteSigned",
                "-File", str(self.root / "scripts" / "setup-native.ps1"),
                "-EmployeeId", self.employee_id, "-Mode", "explicit-only",
                "-Inbox", str(self.root / "UserInbox"), "-Approve",
            ],
            cwd=self.root,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(0, completed.returncode)
        self.assertIn("완전한 BoI Wiki Local Windows clone", completed.stdout + completed.stderr)
        self.assertFalse((self.root / "data" / "boi" / "private" / self.employee_id).exists())

    @unittest.skipUnless(os.name == "nt", "Windows native cross-runtime Core Skill safety test")
    def test_native_setup_rejects_any_missing_core_skill_before_profile_write(self) -> None:
        self.copy_native_setup_distribution()
        required_runtime_files = [
            Path("AGENTS.md"),
            Path("CLAUDE.md"),
            Path(".boi-harness/core-runtime-manifest.json"),
            *[
            Path(runtime) / "skills" / skill_name / "SKILL.md"
            for runtime in (".agents", ".claude")
            for skill_name in ("boi-harness-builder", "boi-second-brain", "boi-wiki-local")
            ],
        ]
        for relative in required_runtime_files:
            with self.subTest(missing=relative.as_posix()):
                target = self.root / relative
                target.unlink()
                inbox = self.root / "UserInbox"
                completed = subprocess.run(
                    [
                        "powershell.exe", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "RemoteSigned",
                        "-File", str(self.root / "scripts" / "setup-native.ps1"),
                        "-EmployeeId", self.employee_id, "-Mode", "explicit-only",
                        "-Inbox", str(inbox), "-Approve",
                    ],
                    cwd=self.root,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    capture_output=True,
                    check=False,
                )
                self.assertNotEqual(0, completed.returncode)
                self.assertIn(str(relative).replace("/", "\\"), completed.stdout + completed.stderr)
                self.assertFalse((self.root / "data" / "boi" / "private" / self.employee_id).exists())
                self.assertFalse(inbox.exists())
                shutil.copy2(REPO / relative, target)

        missing_relative = Path("skills/boi-harness-builder/references/factory-workflow.md")
        missing_targets = [self.root / runtime / missing_relative for runtime in (".agents", ".claude")]
        for target in missing_targets:
            target.unlink()
        inbox = self.root / "UserInbox"
        completed = subprocess.run(
            [
                "powershell.exe", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "RemoteSigned",
                "-File", str(self.root / "scripts" / "setup-native.ps1"),
                "-EmployeeId", self.employee_id, "-Mode", "explicit-only",
                "-Inbox", str(inbox), "-Approve",
            ],
            cwd=self.root,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(0, completed.returncode)
        self.assertIn("Core runtime manifest와 실제 Skill 파일 구성", completed.stdout + completed.stderr)
        self.assertFalse((self.root / "data" / "boi" / "private" / self.employee_id).exists())
        self.assertFalse(inbox.exists())
        for runtime, target in zip((".agents", ".claude"), missing_targets, strict=True):
            shutil.copy2(REPO / runtime / missing_relative, target)

    @unittest.skipUnless(os.name == "nt", "Windows native Core Skill integrity test")
    def test_native_setup_rejects_empty_or_drifted_core_skill_before_profile_write(self) -> None:
        self.copy_native_setup_distribution()
        inbox = self.root / "UserInbox"
        script = self.root / "scripts" / "setup-native.ps1"

        for runtime in (".agents", ".claude"):
            for skill_name in ("boi-harness-builder", "boi-second-brain", "boi-wiki-local"):
                with self.subTest(empty=f"{runtime}/{skill_name}"):
                    target = self.root / runtime / "skills" / skill_name / "SKILL.md"
                    original = target.read_bytes()
                    target.write_bytes(b"")
                    completed = subprocess.run(
                        [
                            "powershell.exe", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "RemoteSigned",
                            "-File", str(script), "-EmployeeId", self.employee_id, "-Mode", "explicit-only",
                            "-Inbox", str(inbox), "-Approve",
                        ],
                        cwd=self.root,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                        capture_output=True,
                        check=False,
                    )
                    self.assertNotEqual(0, completed.returncode)
                    self.assertIn(f"Core Skill 파일 내용이 비어 있습니다({skill_name}/SKILL.md)", completed.stdout + completed.stderr)
                    self.assertFalse((self.root / "data" / "boi" / "private" / self.employee_id).exists())
                    self.assertFalse(inbox.exists())
                    target.write_bytes(original)

        drifted = self.root / ".claude" / "skills" / "boi-harness-builder" / "SKILL.md"
        original = drifted.read_bytes()
        drifted.write_bytes(original + b"\n")
        completed = subprocess.run(
            [
                "powershell.exe", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "RemoteSigned",
                "-File", str(script), "-EmployeeId", self.employee_id, "-Mode", "explicit-only",
                "-Inbox", str(inbox), "-Approve",
            ],
            cwd=self.root,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(0, completed.returncode)
        self.assertIn("Codex와 Claude의 Core Skill 내용이 일치하지 않습니다(boi-harness-builder/SKILL.md)", completed.stdout + completed.stderr)
        self.assertFalse((self.root / "data" / "boi" / "private" / self.employee_id).exists())
        self.assertFalse(inbox.exists())
        drifted.write_bytes(original)

        drifted_reference = (
            self.root
            / ".claude"
            / "skills"
            / "boi-harness-builder"
            / "references"
            / "factory-workflow.md"
        )
        original_reference = drifted_reference.read_bytes()
        drifted_reference.write_bytes(original_reference + b"\n")
        completed = subprocess.run(
            [
                "powershell.exe", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "RemoteSigned",
                "-File", str(script), "-EmployeeId", self.employee_id, "-Mode", "explicit-only",
                "-Inbox", str(inbox), "-Approve",
            ],
            cwd=self.root,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(0, completed.returncode)
        self.assertIn(
            "boi-harness-builder/references/factory-workflow.md",
            completed.stdout + completed.stderr,
        )
        self.assertFalse((self.root / "data" / "boi" / "private" / self.employee_id).exists())
        self.assertFalse(inbox.exists())
        drifted_reference.write_bytes(original_reference)

    @unittest.skipUnless(os.name == "nt", "Windows native connected Wiki safety test")
    def test_native_setup_rejects_missing_required_guide_before_profile_write(self) -> None:
        self.copy_native_setup_distribution()
        (self.root / "templates" / "second-brain-guide" / "50-mcp-and-promotion.md").unlink()
        inbox = self.root / "UserInbox"
        completed = subprocess.run(
            [
                "powershell.exe", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "RemoteSigned",
                "-File", str(self.root / "scripts" / "setup-native.ps1"),
                "-EmployeeId", self.employee_id, "-Mode", "explicit-only",
                "-Inbox", str(inbox), "-Approve",
            ],
            cwd=self.root,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(0, completed.returncode)
        self.assertIn("templates\\second-brain-guide\\50-mcp-and-promotion.md", completed.stdout + completed.stderr)
        self.assertFalse((self.root / "data" / "boi" / "private" / self.employee_id).exists())
        self.assertFalse(inbox.exists())

    @unittest.skipUnless(os.name == "nt", "Windows native existing Profile safety test")
    def test_native_setup_rejects_conflicting_env_before_any_profile_write(self) -> None:
        self.copy_native_setup_distribution()
        env_path = self.root / ".env"
        original_env = b"BOI_LOCAL_ROOT=.\nBOI_LOCAL_EMPLOYEE_ID=2345678\n"
        env_path.write_bytes(original_env)
        inbox = self.root / "UserInbox"
        completed = subprocess.run(
            [
                "powershell.exe", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "RemoteSigned",
                "-File", str(self.root / "scripts" / "setup-native.ps1"),
                "-EmployeeId", self.employee_id, "-Mode", "auto-curate",
                "-Inbox", str(inbox), "-Approve",
            ],
            cwd=self.root,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(0, completed.returncode)
        self.assertIn(".env가 다른 Local Profile", completed.stdout + completed.stderr)
        self.assertEqual(original_env, env_path.read_bytes())
        self.assertFalse((self.root / "data" / "boi" / "private" / self.employee_id).exists())
        self.assertFalse(inbox.exists())

    @unittest.skipUnless(os.name == "nt", "Windows native Harness mismatch test")
    def test_native_setup_rejects_harness_mismatch_before_profile_write(self) -> None:
        self.copy_native_setup_distribution()
        lock_path = self.root / "harness.lock"
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        lock["checksum"] = "0" * 64
        lock_path.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        inbox = self.root / "UserInbox"
        completed = subprocess.run(
            [
                "powershell.exe", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "RemoteSigned",
                "-File", str(self.root / "scripts" / "setup-native.ps1"),
                "-EmployeeId", self.employee_id, "-Mode", "explicit-only",
                "-Inbox", str(inbox), "-Approve",
            ],
            cwd=self.root,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            env={
                **os.environ,
                "PATH": os.pathsep.join(
                    part for part in os.environ.get("PATH", "").split(os.pathsep)
                    if "python" not in part.lower()
                ),
            },
            check=False,
        )
        self.assertNotEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertFalse((self.root / "data" / "boi" / "private" / self.employee_id).exists())
        self.assertFalse(inbox.exists())

    def test_wiki_media_manifest_blocks_tamper_empty_alt_and_oversize(self) -> None:
        guide = self.root / "templates" / "second-brain-guide"
        page = guide / "26-no-obsidian.md"
        page.write_text(
            page.read_text(encoding="utf-8").replace(
                "![Windows 메모장에서 OKF 0.1과 BoI Profile 0.1-local Markdown을 여는 화면]",
                "![]",
            ),
            encoding="utf-8",
        )
        image = guide / "_media" / "02-notepad-markdown.webp"
        image.write_bytes(image.read_bytes() + (b"0" * (600 * 1024)))
        result = json.loads(
            self.run_cli("wiki_check.py", "--root", str(self.root), expected=1).stdout
        )
        issues = "\n".join(item["issue"] for item in result["errors"])
        self.assertIn("empty image alt text", issues)
        self.assertIn("file exceeds", issues)
        self.assertIn("manifest SHA256 mismatch", issues)

    def test_ordinary_user_wiki_rejects_python_commands(self) -> None:
        guide = self.root / "templates" / "second-brain-guide"
        page = guide / "20-first-10-minutes.md"
        page.write_text(
            page.read_text(encoding="utf-8")
            + "\n```powershell\npython scripts/local_search.py --query test\n```\n",
            encoding="utf-8",
        )
        result = json.loads(self.run_cli("wiki_check.py", "--root", str(self.root), expected=1).stdout)
        issues = "\n".join(item["issue"] for item in result["errors"])
        self.assertIn("ordinary-user guide must use natural-language agent requests", issues)

    def test_ordinary_user_wiki_rejects_internal_implementation_terms(self) -> None:
        guide = self.root / "templates" / "second-brain-guide"
        page = guide / "20-first-10-minutes.md"
        page.write_text(
            page.read_text(encoding="utf-8") + "\n사용자가 plan hash와 sidecar를 확인합니다.\n",
            encoding="utf-8",
        )
        result = json.loads(self.run_cli("wiki_check.py", "--root", str(self.root), expected=1).stdout)
        issues = "\n".join(item["issue"] for item in result["errors"])
        self.assertIn("ordinary-user guide exposes administrator implementation terminology", issues)

    def test_ordinary_user_wiki_rejects_manual_scripts_outside_fallback_pages(self) -> None:
        guide = self.root / "templates" / "second-brain-guide"
        page = guide / "26-no-obsidian.md"
        page.write_text(
            page.read_text(encoding="utf-8") + "\n사용자가 check.ps1을 직접 실행합니다.\n",
            encoding="utf-8",
        )
        result = json.loads(self.run_cli("wiki_check.py", "--root", str(self.root), expected=1).stdout)
        issues = "\n".join(item["issue"] for item in result["errors"])
        self.assertIn("ordinary-user guide exposes a manual script outside the installation or update fallback", issues)

    def test_wiki_media_manifest_requires_capture_provenance(self) -> None:
        guide = self.root / "templates" / "second-brain-guide"
        manifest_path = guide / "_media" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["items"][0].pop("capture_method", None)
        manifest["items"][1]["capture_source"] = ""
        target = next(item for item in manifest["items"] if item["id"] == "screen-35")
        target["capture_method"] = "invalid-capture-method"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result = json.loads(self.run_cli("wiki_check.py", "--root", str(self.root), expected=1).stdout)
        issues = "\n".join(item["issue"] for item in result["errors"])
        self.assertIn("manifest capture_method is missing or invalid", issues)
        self.assertIn("manifest capture_source is empty", issues)
        self.assertIn("manifest capture_method is missing or invalid", issues)
        self.assertIn("capture_method must be windows-graphics-capture", issues)

    def test_every_guide_screen_has_a_full_size_markdown_link(self) -> None:
        guide = self.root / "templates" / "second-brain-guide"
        page = guide / "26-no-obsidian.md"
        text = page.read_text(encoding="utf-8")
        text = text.replace(
            "[화면 02를 원본 크기로 열기](_media/02-notepad-markdown.webp)\n",
            "",
        )
        page.write_text(text, encoding="utf-8")
        result = json.loads(self.run_cli("wiki_check.py", "--root", str(self.root), expected=1).stdout)
        issues = "\n".join(error["issue"] for error in result["errors"])
        self.assertIn("missing full-size image link: _media/02-notepad-markdown.webp", issues)

    @unittest.skipIf(Image is None, "Pillow is optional and not installed")
    def test_golden_journey_screens_enforce_readable_width(self) -> None:
        guide = self.root / "templates" / "second-brain-guide"
        manifest_path = guide / "_media" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        item = next(value for value in manifest["items"] if value["id"] == "screen-35")
        image_path = guide / "_media" / item["file"]
        with Image.open(image_path) as image:
            resized = image.resize((1024, round(image.height * 1024 / image.width)), Image.Resampling.LANCZOS)
            resized.save(image_path, format="WEBP", quality=88, method=6)
        data = image_path.read_bytes()
        item["width"] = 1024
        item["height"] = resized.height
        item["bytes"] = len(data)
        item["sha256"] = hashlib.sha256(data).hexdigest()
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result = json.loads(self.run_cli("wiki_check.py", "--root", str(self.root), expected=1).stdout)
        issues = "\n".join(error["issue"] for error in result["errors"])
        self.assertIn("case journey screen width must be at least 1400px", issues)

    @unittest.skipIf(Image is None, "Pillow is optional and not installed")
    def test_all_guide_screens_enforce_minimum_readable_width(self) -> None:
        guide = self.root / "templates" / "second-brain-guide"
        manifest_path = guide / "_media" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        item = next(value for value in manifest["items"] if value["id"] == "screen-03")
        image_path = guide / "_media" / item["file"]
        with Image.open(image_path) as image:
            resized = image.resize((640, round(image.height * 640 / image.width)), Image.Resampling.LANCZOS)
            resized.save(image_path, format="WEBP", quality=88, method=6)
        data = image_path.read_bytes()
        item["width"] = 640
        item["height"] = resized.height
        item["bytes"] = len(data)
        item["sha256"] = hashlib.sha256(data).hexdigest()
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        result = json.loads(self.run_cli("wiki_check.py", "--root", str(self.root), expected=1).stdout)
        issues = "\n".join(error["issue"] for error in result["errors"])
        self.assertIn("guide screen width must be at least 800px", issues)

    def test_research_wiki_keeps_clickable_primary_sources_and_video_limits(self) -> None:
        ledger = (REPO / "research" / "second-brain-source-ledger.md").read_text(encoding="utf-8")
        guide = (REPO / "templates" / "second-brain-guide" / "27-research-backed-second-brain.md").read_text(encoding="utf-8")
        playbook = (REPO / "templates" / "second-brain-guide" / "25-use-case-playbook.md").read_text(encoding="utf-8")
        self.assertNotIn("| https://", ledger)
        self.assertIn("Core Search의 재현 가능한 부족이 확인될 때만 검토", ledger)
        self.assertIn("QuickAdd", ledger)
        self.assertIn("SHA256", ledger)
        self.assertIn("YouTube 직접 페이지는 429·fetch 제한", ledger)
        self.assertIn("oembed-metadata-only", ledger)
        self.assertIn("transcript는 검토하지 않았으므로", ledger)
        for url in (
            "https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f",
            "https://fortelabs.com/blog/para/",
            "https://www.youtube.com/watch?v=z4AbijUCoKU",
            "https://obsidian.md/help/web-clipper",
        ):
            self.assertIn(url, guide)
        self.assertIn("범용 Investigation Pattern", playbook)

    def test_workspace_profile_resolution_is_persisted_and_unambiguous(self) -> None:
        private_root = self.root / "data" / "boi" / "private"
        private_root.mkdir(parents=True)
        (self.root / ".env").write_text(
            "BOI_LOCAL_ROOT=.\nBOI_LOCAL_EMPLOYEE_ID=7654321\n",
            encoding="utf-8",
        )
        with patch.dict(os.environ, {"BOI_LOCAL_EMPLOYEE_ID": ""}):
            self.assertEqual(("7654321", "dotenv"), workspace_employee_id(self.root))
            self.assertEqual(("7654321", "argument"), workspace_employee_id(self.root, "7654321"))

            (self.root / ".env").write_text(
                "BOI_LOCAL_ROOT=.\nBOI_LOCAL_EMPLOYEE_ID=0000000\n",
                encoding="utf-8",
            )
            (private_root / "7654321").mkdir()
            self.assertEqual(("7654321", "profile-directory"), workspace_employee_id(self.root))
            (private_root / "2345678").mkdir()
            with self.assertRaisesRegex(ValueError, "multiple Local Private profiles"):
                workspace_employee_id(self.root)

        with patch.dict(os.environ, {"BOI_LOCAL_EMPLOYEE_ID": "7654321"}):
            self.assertEqual(("7654321", "environment"), workspace_employee_id(self.root))

        (self.root / ".env").write_text(
            "BOI_LOCAL_ROOT=.\nBOI_LOCAL_EMPLOYEE_ID=2345678\n",
            encoding="utf-8",
        )
        with patch.dict(os.environ, {"BOI_LOCAL_EMPLOYEE_ID": "0000000"}):
            self.assertEqual(("2345678", "dotenv"), workspace_employee_id(self.root))
        with patch.dict(os.environ, {"BOI_LOCAL_EMPLOYEE_ID": "7654321"}):
            with self.assertRaisesRegex(ValueError, "different Local Private profiles"):
                workspace_employee_id(self.root)
            self.assertEqual(("7654321", "argument"), workspace_employee_id(self.root, "7654321"))

    def test_new_session_commands_resolve_profile_from_dotenv(self) -> None:
        self.setup_workspace()
        environment = {**os.environ, "PYTHONUTF8": "1"}
        environment.pop("BOI_LOCAL_EMPLOYEE_ID", None)
        completed = subprocess.run(
            [sys.executable, str(SCRIPTS / "local_lint.py"), "--root", str(self.root)],
            cwd=REPO,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            env=environment,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(self.employee_id, payload["employee_id"])

    def test_tracked_template_guide_never_embeds_maintainer_origin(self) -> None:
        subprocess.run(["git", "init", "-b", "main"], cwd=self.root, check=True, capture_output=True)
        subprocess.run(
            ["git", "remote", "add", "origin", "https://github.example/maintainer/boi-wiki-local.git"],
            cwd=self.root,
            check=True,
        )
        planned = desired_files(self.root, "0000000")
        guide_path = (
            self.root
            / "data"
            / "boi"
            / "private"
            / "0000000"
            / "notes"
            / "guide"
            / "10-install-repository.md"
        )
        guide = planned[guide_path]
        self.assertIn("<배포 Git 저장소 주소>", guide)
        self.assertNotIn("github.example", guide)
        employee_guide_path = (
            self.root
            / "data"
            / "boi"
            / "private"
            / self.employee_id
            / "notes"
            / "guide"
            / "10-install-repository.md"
        )
        self.assertIn("https://github.example/maintainer/boi-wiki-local.git", desired_files(self.root, self.employee_id)[employee_guide_path])

    @unittest.skipUnless(os.name == "nt", "Windows native installer test")
    def test_windows_cmd_installer_creates_full_guide_without_policy_bypass(self) -> None:
        installer = (REPO / "install.cmd").read_text(encoding="utf-8").lower()
        self.assertNotIn("executionpolicy bypass", installer)
        self.assertIn("setup.cmd", installer)
        self.copy_native_setup_distribution()
        shutil.copy2(REPO / "install.cmd", self.root / "install.cmd")
        shutil.copy2(REPO / "setup.cmd", self.root / "setup.cmd")
        completed = subprocess.run(
            ["cmd.exe", "/d", "/c", "install.cmd"],
            cwd=self.root,
            input="\n\nY\n",
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            env={
                **os.environ,
                "PYTHONUTF8": "1",
                "BOI_LOCAL_EMPLOYEE_ID": self.employee_id,
                "PATH": os.pathsep.join(
                    part for part in os.environ.get("PATH", "").split(os.pathsep)
                    if "python" not in part.lower()
                ),
            },
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        guide = self.root / "data" / "boi" / "private" / self.employee_id / "notes" / "guide"
        self.assertTrue((guide / "00-start-here.md").exists())
        self.assertTrue((guide / "80-admin-release-and-contract.md").exists())
        self.assertFalse((self.root / ".obsidian").exists())

    @unittest.skipUnless(os.name == "nt", "Windows native interactive installer test")
    def test_windows_cmd_installer_prompts_for_employee_id_when_environment_is_absent(self) -> None:
        self.copy_native_setup_distribution()
        shutil.copy2(REPO / "install.cmd", self.root / "install.cmd")
        shutil.copy2(REPO / "setup.cmd", self.root / "setup.cmd")
        environment = {
            **os.environ,
            "PYTHONUTF8": "1",
            "BOI_CONFIRM_INSTALL": "INSTALL",
            "PATH": os.pathsep.join(
                part for part in os.environ.get("PATH", "").split(os.pathsep)
                if "python" not in part.lower()
            ),
        }
        environment.pop("BOI_LOCAL_EMPLOYEE_ID", None)
        completed = subprocess.run(
            ["cmd.exe", "/d", "/c", "install.cmd"],
            cwd=self.root,
            input=f"{self.employee_id}\n",
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            env=environment,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertTrue((self.root / "data" / "boi" / "private" / self.employee_id / "notes" / "guide" / "00-start-here.md").exists())
        self.assertIn(f"BOI_LOCAL_EMPLOYEE_ID={self.employee_id}", (self.root / ".env").read_text(encoding="utf-8"))

    @unittest.skipUnless(os.name == "nt", "Windows native PowerShell installer test")
    def test_windows_powershell_installer_requires_exact_confirmation(self) -> None:
        installer = (REPO / "install.ps1").read_text(encoding="utf-8").lower()
        self.assertNotIn("python", installer)
        self.assertIn("scripts/setup-native.ps1", installer)
        self.assertNotIn("enter your numeric", installer)
        self.assertNotIn("read-host", installer.lower())
        self.copy_native_setup_distribution()
        shutil.copy2(REPO / "install.ps1", self.root / "install.ps1")
        environment = {
            **os.environ,
            "PYTHONUTF8": "1",
            "BOI_LOCAL_EMPLOYEE_ID": self.employee_id,
            "PATH": os.pathsep.join(
                part for part in os.environ.get("PATH", "").split(os.pathsep)
                if "python" not in part.lower()
            ),
        }
        refused = subprocess.run(
            ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "RemoteSigned", "-File", "install.ps1", "-Root", str(self.root), "-ConfirmInstall", "NO"],
            cwd=self.root,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            env=environment,
            check=False,
        )
        refused_output = refused.stdout + refused.stderr
        if refused.returncode != 2 and "running scripts is disabled" in refused_output:
            self.skipTest("Windows execution policy blocks .ps1; install.cmd is the supported no-bypass entry point")
        self.assertEqual(2, refused.returncode, refused_output)
        self.assertFalse((self.root / "data" / "boi" / "private" / self.employee_id).exists())
        accepted = subprocess.run(
            [
                "powershell.exe", "-NoProfile", "-ExecutionPolicy", "RemoteSigned",
                "-File", "install.ps1", "-Root", str(self.root),
                "-Mode", "suggest", "-Inbox", str(self.root / "LegacyInbox"),
                "-ConfirmInstall", "INSTALL",
            ],
            cwd=self.root,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            env=environment,
            check=False,
        )
        self.assertEqual(0, accepted.returncode, accepted.stdout + accepted.stderr)
        self.assertTrue((self.root / "data" / "boi" / "private" / self.employee_id / "notes" / "guide" / "00-start-here.md").exists())
        preferences = json.loads(
            (self.root / "data" / "boi" / "private" / self.employee_id / ".boi-local" / "second-brain-preferences.json")
            .read_text(encoding="utf-8-sig")
        )
        self.assertEqual("suggest", preferences["conversation_mode"])
        self.assertTrue(preferences["agent_session_check"])
        self.assertIn("변경 요약을 확인한 뒤", preferences["authorization"]["approved_summary"])

    def test_release_candidate_privacy_scan_includes_unchanged_tracked_files(self) -> None:
        repo = self.root / "privacy-repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
        subprocess.run(["git", "config", "core.autocrlf", "false"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.email", "fixture@example.com"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "Fixture"], cwd=repo, check=True)
        (repo / "tracked-secret.txt").write_text("API_KEY=synthetic-but-forbidden\n", encoding="utf-8")
        (repo / ".gitignore").write_text("data/boi/private/*/\n!data/boi/private/0000000/\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", "fixture"], cwd=repo, check=True, capture_output=True)
        ignored = repo / "data" / "boi" / "private" / "7654321" / "private.md"
        ignored.parent.mkdir(parents=True)
        ignored.write_text("local only\n", encoding="utf-8")
        self.assertTrue(inspect_contribution(repo, staged=False)["ok"])
        (repo / "release-acceptance.json").write_text(
            json.dumps({"schema": "boi-local-release-acceptance/v3"}),
            encoding="utf-8",
        )
        (repo / "legacy-release-acceptance.json").write_text(
            json.dumps({"schema": "boi-local-release-acceptance/v1"}),
            encoding="utf-8",
        )
        full = inspect_contribution(repo, staged=False, all_files=True)
        self.assertFalse(full["ok"])
        self.assertEqual("release-candidate", full["mode"])
        self.assertIn("tracked-secret.txt", full["checked"])
        self.assertIn("release-acceptance.json", full["checked"])
        self.assertIn("legacy-release-acceptance.json", full["checked"])
        blocked_evidence = {
            item["path"] for item in full["errors"]
            if item["issue"] == "pilot acceptance evidence must remain outside the repository"
        }
        self.assertEqual(
            {"legacy-release-acceptance.json", "release-acceptance.json"},
            blocked_evidence,
        )
        self.assertIn(
            "pilot acceptance evidence must remain outside the repository",
            {item["issue"] for item in full["errors"]},
        )
        self.assertNotIn("data/boi/private/7654321/private.md", full["checked"])

    def test_update_preview_uses_configured_origin_and_redacts_credentials(self) -> None:
        work = self.root / "update-work"
        remote = self.root / "bitbucket-like-remote.git"
        work.mkdir()
        subprocess.run(["git", "init", "-b", "main"], cwd=work, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "fixture@example.com"], cwd=work, check=True)
        subprocess.run(["git", "config", "user.name", "Fixture"], cwd=work, check=True)
        (work / "README.md").write_text("fixture\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=work, check=True)
        subprocess.run(["git", "commit", "-m", "fixture"], cwd=work, check=True, capture_output=True)
        subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(remote), "symbolic-ref", "HEAD", "refs/heads/main"], check=True)
        subprocess.run(["git", "remote", "add", "origin", str(remote)], cwd=work, check=True)
        subprocess.run(["git", "push", "-u", "origin", "main"], cwd=work, check=True, capture_output=True)
        subprocess.run(["git", "remote", "set-head", "origin", "-a"], cwd=work, check=True, capture_output=True)
        preview = json.loads(self.run_cli("boi_update.py", "--root", str(work)).stdout)
        self.assertEqual(str(remote), preview["origin"])
        self.assertEqual("main", preview["stable_branch"])
        self.assertTrue(preview["local_private_hash_unchanged"])
        credentialed = "https://employee:" + "synthetic-token@bitbucket.example/repo.git"
        self.assertEqual("https://bitbucket.example/repo.git", safe_remote(credentialed))
        ssh_origin = "ssh://git@bitbucket.example/repo.git"
        self.assertEqual(ssh_origin, safe_remote(ssh_origin))
        self.assertEqual(
            "ssh://bitbucket.example/repo.git",
            safe_remote("ssh://employee:" + "synthetic-token@bitbucket.example/repo.git"),
        )
        subprocess.run(["git", "remote", "set-url", "origin", ssh_origin], cwd=work, check=True)
        self.assertTrue(origin_check(work, "bitbucket")["ok"])
        subprocess.run(
            ["git", "remote", "set-url", "origin", "https://github.com/example/boi-wiki-local.git"],
            cwd=work,
            check=True,
        )
        self.assertTrue(origin_check(work, r"github[.]com|bitbucket")["ok"])

    def test_wsl_migration_audit_hashes_exact_and_evolved_files_and_blocks_missing(self) -> None:
        source = self.root / "wsl-source"
        target = self.root / "windows-target"
        source.mkdir()
        subprocess.run(["git", "init", "-b", "main"], cwd=source, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "fixture@example.com"], cwd=source, check=True)
        subprocess.run(["git", "config", "user.name", "Fixture"], cwd=source, check=True)
        (source / "tracked.md").write_text("base\n", encoding="utf-8")
        subprocess.run(["git", "add", "tracked.md"], cwd=source, check=True)
        subprocess.run(["git", "commit", "-m", "base"], cwd=source, check=True, capture_output=True)
        subprocess.run(["git", "clone", str(source), str(target)], check=True, capture_output=True)
        (source / "tracked.md").write_text("imported change\n", encoding="utf-8")
        (source / "untracked.md").write_text("new source file\n", encoding="utf-8")
        shutil.copy2(source / "tracked.md", target / "tracked.md")
        shutil.copy2(source / "untracked.md", target / "untracked.md")
        (target / "tracked.md").write_text("imported change\npost-migration improvement\n", encoding="utf-8")

        result = audit_migration(source, target)
        self.assertTrue(result["ok"], result)
        self.assertEqual(2, result["source_changed_file_count"])
        self.assertEqual(1, result["changed_exact_count"])
        self.assertEqual(1, result["changed_evolved_in_windows_count"])
        self.assertEqual([], result["missing_in_windows_target"])
        self.assertEqual(64, len(result["source_hash_ledger_sha256"]))

        (target / "untracked.md").unlink()
        missing = audit_migration(source, target)
        self.assertFalse(missing["ok"])
        self.assertEqual(["untracked.md"], missing["missing_in_windows_target"])

    def test_update_apply_fast_forwards_and_preserves_ignored_private_content(self) -> None:
        seed = self.root / "seed"
        remote = self.root / "internal-bitbucket.git"
        checkout = self.root / "member-checkout"
        seed.mkdir()
        subprocess.run(["git", "init", "-b", "main"], cwd=seed, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "fixture@example.com"], cwd=seed, check=True)
        subprocess.run(["git", "config", "user.name", "Fixture"], cwd=seed, check=True)
        subprocess.run(["git", "config", "core.autocrlf", "false"], cwd=seed, check=True)
        (seed / "README.md").write_text("release 1\n", encoding="utf-8")
        (seed / ".gitignore").write_text(".env\ndata/boi/private/7654321/\n", encoding="utf-8")
        (seed / "scripts").mkdir()
        shutil.copy2(REPO / "scripts" / "harness_sync.py", seed / "scripts" / "harness_sync.py")
        shutil.copytree(REPO / "templates", seed / "templates")
        shutil.copytree(REPO / ".boi-harness", seed / ".boi-harness")
        for name in ("harness.lock", "AGENTS.md", "CLAUDE.md"):
            shutil.copy2(REPO / name, seed / name)
        (seed / "check.ps1").write_text("exit 0\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=seed, check=True)
        subprocess.run(["git", "commit", "-m", "release 1"], cwd=seed, check=True, capture_output=True)
        subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(remote), "symbolic-ref", "HEAD", "refs/heads/main"], check=True)
        subprocess.run(["git", "remote", "add", "origin", str(remote)], cwd=seed, check=True)
        subprocess.run(["git", "push", "-u", "origin", "main"], cwd=seed, check=True, capture_output=True)
        subprocess.run(["git", "clone", str(remote), str(checkout)], check=True, capture_output=True)
        subprocess.run(["git", "remote", "set-head", "origin", "-a"], cwd=checkout, check=True, capture_output=True)

        private = checkout / "data" / "boi" / "private" / "7654321" / "notes" / "private.md"
        private.parent.mkdir(parents=True)
        private.write_text("local private fixture\n", encoding="utf-8")
        (checkout / ".env").write_text("BOI_LOCAL_EMPLOYEE_ID=7654321\n", encoding="utf-8")
        private_before = private.read_bytes()
        (seed / "README.md").write_text("release 2\n", encoding="utf-8")
        subprocess.run(["git", "add", "README.md"], cwd=seed, check=True)
        subprocess.run(["git", "commit", "-m", "release 2"], cwd=seed, check=True, capture_output=True)
        subprocess.run(["git", "push", "origin", "main"], cwd=seed, check=True, capture_output=True)

        applied = subprocess.run(
            [sys.executable, str(SCRIPTS / "boi_update.py"), "--root", str(checkout), "--apply"],
            cwd=REPO,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            env={key: value for key, value in {**os.environ, "PYTHONUTF8": "1"}.items() if key != "BOI_LOCAL_EMPLOYEE_ID"},
            check=False,
        )
        self.assertEqual(0, applied.returncode, applied.stdout + applied.stderr)
        payload = json.loads(applied.stdout)
        self.assertTrue(payload["local_private_hash_unchanged"])
        self.assertEqual("dotenv", payload["local_profile_source"])
        self.assertEqual("release 2\n", (checkout / "README.md").read_text(encoding="utf-8"))
        self.assertEqual(private_before, private.read_bytes())

        (checkout / "README.md").write_text("dirty local edit\n", encoding="utf-8")
        blocked = subprocess.run(
            [sys.executable, str(SCRIPTS / "boi_update.py"), "--root", str(checkout), "--apply"],
            cwd=REPO,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            env={key: value for key, value in {**os.environ, "PYTHONUTF8": "1"}.items() if key != "BOI_LOCAL_EMPLOYEE_ID"},
            check=False,
        )
        self.assertEqual(1, blocked.returncode)
        self.assertIn("never auto-stashes or resets", json.loads(blocked.stdout)["error"])
        self.assertEqual(private_before, private.read_bytes())

    def test_disposable_beginner_ux_has_no_persistent_usage_log_or_remote_mutation(self) -> None:
        result = run_journey(REPO, os.getenv("BOI_WIKI_ROOT", ""))
        self.assertTrue(result["ok"], result)
        self.assertFalse(result["persistent_usage_log_created"])
        self.assertEqual(0, result["mcp_invocations"])
        self.assertEqual(0, result["remote_mutations"])
        self.assertTrue(result["temporary_workspace_removed_on_exit"])

    def test_optional_plugins_select_versions_compatible_with_obsidian_1_12_7(self) -> None:
        snapshot = json.loads((REPO / "research" / "obsidian-plugin-compatibility.json").read_text(encoding="utf-8"))
        result = evaluate_obsidian_plugins(snapshot, "1.12.7")
        selected = {item["id"]: item["selected"]["version"] for item in result["plugins"]}
        self.assertEqual("2.12.3", selected["quickadd"])
        self.assertEqual("1.29.3", selected["omnisearch"])
        statuses = {item["id"]: item["status"] for item in result["plugins"]}
        self.assertEqual("deferred-until-core-search-gap", statuses["omnisearch"])
        self.assertFalse(result["plugins_required_for_local_second_brain"])
        self.assertFalse(result["plugins_installed"])

    def test_optional_plugins_select_latest_for_runtime_1_13_4(self) -> None:
        snapshot = json.loads((REPO / "research" / "obsidian-plugin-compatibility.json").read_text(encoding="utf-8"))
        result = evaluate_obsidian_plugins(snapshot, "1.13.4", app_version_source="fixture-runtime-asar")
        selected = {item["id"]: item["selected"]["version"] for item in result["plugins"]}
        self.assertEqual("2.21.0", selected["quickadd"])
        self.assertEqual("1.30.1", selected["omnisearch"])
        statuses = {item["id"]: item["status"] for item in result["plugins"]}
        self.assertEqual("deferred-until-core-search-gap", statuses["omnisearch"])
        self.assertEqual("fixture-runtime-asar", result["app_version_source"])
        quickadd = next(item for item in result["plugins"] if item["id"] == "quickadd")
        artifacts = {item["file"]: item for item in quickadd["distribution_artifacts"]}
        self.assertEqual({"main.js", "manifest.json", "styles.css"}, set(artifacts))
        self.assertEqual(
            "8636198aef29cd64b53def1bf921baef5ddf83070c8a77c5457c9276617a81ad",
            artifacts["main.js"]["sha256"],
        )

    def test_obsidian_runtime_detection_prefers_newest_appdata_asar(self) -> None:
        appdata = self.root / "AppData" / "Roaming"
        obsidian = appdata / "obsidian"
        obsidian.mkdir(parents=True)
        (obsidian / "obsidian-1.12.7.asar").write_bytes(b"fixture")
        (obsidian / "obsidian-1.13.4.asar").write_bytes(b"fixture")
        detected = detect_windows_runtime_version(appdata)
        self.assertTrue(detected["detected"])
        self.assertEqual("1.13.4", detected["version"])
        self.assertEqual("appdata-runtime-asar", detected["source"])

    def test_release_evidence_requires_real_non_developer_and_obsidian_results(self) -> None:
        example = json.loads((REPO / "research" / "release-acceptance-evidence.example.json").read_text(encoding="utf-8"))
        self.assertFalse(validate_release_evidence(example)["ok"])
        windows = {
            "approved_git_clone_succeeded": True,
            "install_from_wiki_succeeded": True,
            "first_capture_succeeded": True,
            "search_succeeded": True,
            "promotion_preview_succeeded": True,
            "duration_minutes": 18,
            "install_duration_minutes": 8,
            "first_knowledge_duration_minutes": 7,
            "promotion_preview_duration_minutes": 3,
        }
        security = {
            "local_private_uploaded": False,
            "remote_mutations_before_approval": False,
            "usage_telemetry_observed": False,
        }
        completed = {
            "schema": "boi-local-release-acceptance/v3",
            "build_commit": "abcdef0123456789abcdef0123456789abcdef01",
            "tested_at": "2026-08-01T14:00:00+09:00",
            "reviewer_role": "knowledge-steward",
            "testers": [
                {
                    "journey": "no-obsidian", "tester_profile": "non-developer",
                    "windows_native": windows,
                    "obsidian": {"support_claimed": False, "app_version": "", "vault_opened": False, "external_file_watcher_succeeded": False, "properties_succeeded": False, "backlinks_succeeded": False, "graph_succeeded": False},
                    "security": security,
                    "ux_observations": {"blocked_steps": [], "misclicked_steps": [], "helpful_capture_ids": ["screen-20"]},
                    "tester_confirmed": True,
                },
                {
                    "journey": "obsidian-core", "tester_profile": "non-developer",
                    "windows_native": windows,
                    "obsidian": {"support_claimed": True, "app_version": "1.13.4", "vault_opened": True, "external_file_watcher_succeeded": True, "properties_succeeded": True, "backlinks_succeeded": True, "graph_succeeded": True},
                    "security": security,
                    "ux_observations": {"blocked_steps": [], "misclicked_steps": ["graph"], "helpful_capture_ids": ["screen-22"]},
                    "tester_confirmed": True,
                },
            ],
            "domain_review": {
                "reviewer_profile": "domain-expert",
                "synthetic_case_reviewed": True,
                "workflow_plausibility_confirmed": True,
                "claims_marked_synthetic": True,
                "domain_persona_validated": True,
            },
            "reviewer_confirmed": True,
        }
        result = validate_release_evidence(completed, completed["build_commit"])
        self.assertTrue(result["ok"], result)
        self.assertTrue(result["obsidian_support_claimed"])
        self.assertTrue(result["time_targets_met"])
        self.assertFalse(result["contains_personal_identity"])

        mismatched = validate_release_evidence(completed, "1" * 40)
        self.assertFalse(mismatched["ok"])
        self.assertIn("build_commit does not match the release-gate checkout HEAD", mismatched["errors"])

        identified = json.loads(json.dumps(completed))
        identified["tester_name"] = "홍길동"
        identified["testers"][0]["windows_native"]["vault_path"] = r"C:\Users\employee\Projects\boi-wiki-local"
        identified_result = validate_release_evidence(identified)
        self.assertFalse(identified_result["ok"])
        self.assertTrue(identified_result["contains_personal_identity"])

    def test_release_readiness_keeps_obsidian_optional(self) -> None:
        automated = {
            "ux": {"ok": True},
            "query_quality": {"ok": True},
            "wiki": {"release_screen_ready": True},
            "origin": {"host": "github.com"},
        }
        without_obsidian = release_readiness(
            True,
            automated,
            {"ok": True, "obsidian_support_claimed": False},
        )
        self.assertTrue(without_obsidian["core_automated_ready"])
        self.assertTrue(without_obsidian["generic_ux_qa_ready"])
        self.assertTrue(without_obsidian["second_brain_query_quality_ready"])
        self.assertFalse(without_obsidian["full_release_ready"])
        self.assertFalse(without_obsidian["obsidian_support_ready"])

        with_obsidian = release_readiness(
            True,
            {**automated, "origin": {"host": "bitbucket.internal.example"}},
            {"ok": True, "obsidian_support_claimed": True, "domain_example_validated": True},
        )
        self.assertFalse(with_obsidian["full_release_ready"])
        self.assertTrue(with_obsidian["obsidian_support_ready"])
        self.assertFalse(with_obsidian["zero_ui_setup_ready"])
        self.assertFalse(with_obsidian["adaptive_memory_ready"])

    def test_generic_core_does_not_promote_yield_terms_to_product_contracts(self) -> None:
        generic_files = [
            REPO / "README_KO.md",
            REPO / "README.md",
            REPO / "AGENTS.md",
            REPO / "CLAUDE.md",
            REPO / "cases" / "README.md",
            REPO / "cases" / "catalog.json",
            REPO / "cases" / "flagship" / "second-brain" / "CASE.md",
            REPO / "templates" / "second-brain-guide" / "00-start-here.md",
            REPO / "templates" / "second-brain-guide" / "01-meta-harness-map.md",
            REPO / "templates" / "second-brain-guide" / "25-use-case-playbook.md",
            SCRIPTS / "release_gate.py",
            SCRIPTS / "release_evidence.py",
            SCRIPTS / "pilot_acceptance.py",
        ]
        for runtime_root in (REPO / ".agents" / "skills", REPO / ".claude" / "skills"):
            for skill_name in ("boi-harness-builder", "boi-second-brain", "boi-wiki-local"):
                generic_files.extend(
                    path for path in (runtime_root / skill_name).rglob("*") if path.is_file()
                )
        combined = "\n".join(path.read_text(encoding="utf-8") for path in generic_files)
        self.assertNotIn("internal-yield-process-expert", combined)
        self.assertNotIn("SYN-YLD-001-v2", combined)
        self.assertNotIn("SYN-YLD-001-v3", combined)
        self.assertNotIn("boi-yield-analysis", combined)
        self.assertNotIn("합성 수율", combined)
        self.assertNotIn("yield-analysis", combined.lower())
        self.assertIn("Investigation pattern", combined)

    def test_pilot_wizard_builds_deidentified_two_party_evidence_outside_repo(self) -> None:
        commit = "a" * 40
        payload = build_tester_evidence(
            build_commit=commit,
            duration_minutes=18,
            windows_native={
                "approved_git_clone_succeeded": True,
                "install_from_wiki_succeeded": True,
                "first_capture_succeeded": True,
                "search_succeeded": True,
                "promotion_preview_succeeded": True,
            },
            obsidian={"support_claimed": False},
            security={
                "local_private_uploaded": False,
                "remote_mutations_before_approval": False,
                "usage_telemetry_observed": False,
            },
            tester_confirmed=True,
            phase_durations={"install_duration_minutes": 8, "first_knowledge_duration_minutes": 7, "promotion_preview_duration_minutes": 3},
            ux_observations={"blocked_steps": [], "misclicked_steps": [], "helpful_capture_ids": ["screen-20"]},
            second_windows_native={
                "approved_git_clone_succeeded": True,
                "install_from_wiki_succeeded": True,
                "first_capture_succeeded": True,
                "search_succeeded": True,
                "promotion_preview_succeeded": True,
            },
            second_obsidian={
                "support_claimed": True,
                "app_version": "1.13.4",
                "vault_opened": True,
                "external_file_watcher_succeeded": True,
                "properties_succeeded": True,
                "backlinks_succeeded": True,
                "graph_succeeded": True,
            },
            second_security={
                "local_private_uploaded": False,
                "remote_mutations_before_approval": False,
                "usage_telemetry_observed": False,
            },
            second_tester_confirmed=True,
            second_phase_durations={"install_duration_minutes": 9, "first_knowledge_duration_minutes": 8, "promotion_preview_duration_minutes": 4},
            second_ux_observations={"blocked_steps": [], "misclicked_steps": ["graph"], "helpful_capture_ids": ["screen-22"]},
            tested_at="2026-08-01T16:30:00+09:00",
        )
        self.assertFalse(payload["reviewer_confirmed"])
        payload = domain_reviewed_candidate(payload, {
            "synthetic_case_reviewed": True,
            "workflow_plausibility_confirmed": True,
            "claims_marked_synthetic": True,
            "domain_persona_validated": True,
        })
        candidate, result = reviewed_candidate(payload, "knowledge-steward", commit)
        self.assertTrue(result["ok"], result)
        self.assertTrue(candidate["reviewer_confirmed"])
        self.assertFalse(result["contains_personal_identity"])

        with self.assertRaisesRegex(ValueError, "outside the repository"):
            evidence_path(self.root, str(self.root / "release-acceptance.json"), must_exist=False)
        external = self.root.parent / f"{self.root.name}-release-acceptance.json"
        self.assertEqual(external.resolve(), evidence_path(self.root, str(external), must_exist=False))

        _, mismatched = reviewed_candidate(payload, "knowledge-steward", "b" * 40)
        self.assertFalse(mismatched["ok"])

    @unittest.skipUnless(os.name == "nt", "Windows native pilot wizard test")
    def test_windows_pilot_wizard_start_review_validate_creates_no_repo_log(self) -> None:
        repo = self.root / "pilot-repo"
        scripts = repo / "scripts"
        scripts.mkdir(parents=True)
        for name in ("pilot_acceptance.py", "release_evidence.py", "release_gate.py", "migration_audit.py"):
            shutil.copy2(SCRIPTS / name, scripts / name)
        (repo / ".gitignore").write_text("__pycache__/\n*.pyc\n", encoding="utf-8")
        subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "fixture@example.com"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "Fixture"], cwd=repo, check=True)
        subprocess.run(["git", "add", "."], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-m", "pilot fixture"], cwd=repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "remote", "add", "origin", "https://github.com/example/boi-wiki-local.git"],
            cwd=repo,
            check=True,
        )
        evidence = self.root / "pilot-release-acceptance.json"
        preflight = subprocess.run(
            [sys.executable, str(scripts / "pilot_acceptance.py"), "preflight", "--evidence", str(evidence)],
            cwd=repo,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, preflight.returncode, preflight.stdout + preflight.stderr)
        preflight_payload = json.loads(preflight.stdout)
        self.assertTrue(preflight_payload["clean_checkout"])
        self.assertTrue(preflight_payload["evidence_outside_repository"])
        self.assertFalse(preflight_payload["evidence_created_by_preflight"])
        self.assertTrue(preflight_payload["evidence_will_be_created_by_start"])
        self.assertFalse(evidence.exists())
        start_input = "\n".join((
            "y", "y", "y", "y", "8", "7", "3", "", "", "screen-20", "n", "n", "n", "CONFIRM",
            "y", "y", "y", "y", "9", "8", "4", "", "graph", "screen-22", "1.13.4", "y", "y", "y", "y", "y", "n", "n", "n", "CONFIRM",
        )) + "\n"
        started = subprocess.run(
            [sys.executable, str(scripts / "pilot_acceptance.py"), "start", "--evidence", str(evidence)],
            cwd=repo,
            input=start_input,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, started.returncode, started.stdout + started.stderr)
        draft = json.loads(evidence.read_text(encoding="utf-8"))
        self.assertFalse(draft["reviewer_confirmed"])
        domain_reviewed = subprocess.run(
            [
                sys.executable,
                str(scripts / "pilot_acceptance.py"),
                "domain-review",
                "--evidence",
                str(evidence),
            ],
            cwd=repo,
            input="y\ny\ny\ny\nDOMAIN-APPROVE\n",
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, domain_reviewed.returncode, domain_reviewed.stdout + domain_reviewed.stderr)
        reviewed = subprocess.run(
            [
                sys.executable,
                str(scripts / "pilot_acceptance.py"),
                "review",
                "--evidence",
                str(evidence),
                "--reviewer-role",
                "knowledge-steward",
            ],
            cwd=repo,
            input="APPROVE\n",
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, reviewed.returncode, reviewed.stdout + reviewed.stderr)
        validated = subprocess.run(
            [sys.executable, str(scripts / "pilot_acceptance.py"), "validate", "--evidence", str(evidence)],
            cwd=repo,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, validated.returncode, validated.stdout + validated.stderr)
        self.assertTrue(json.loads(validated.stdout)["ok"])
        self.assertEqual("", subprocess.run(["git", "status", "--porcelain"], cwd=repo, check=True, capture_output=True, text=True).stdout)
        self.assertNotIn("employee_id", evidence.read_text(encoding="utf-8"))

    def test_capture_distill_search_and_lint(self) -> None:
        self.setup_workspace()
        captured = json.loads(
            self.run_cli(
                "local_capture.py",
                "--root",
                str(self.root),
                "--employee-id",
                self.employee_id,
                "--title",
                "품질 회의 메모",
                "--body",
                "응답 추세를 다음 주에 다시 검토한다.",
            ).stdout
        )
        source = self.root / captured["path"]
        before = source.read_bytes()
        text = source.read_text(encoding="utf-8")
        self.assertIn("source_immutability: \"locked\"", text)
        self.assertIn("visibility: local-private", text)

        distilled = json.loads(
            self.run_cli(
                "local_distill.py",
                "--root",
                str(self.root),
                "--employee-id",
                self.employee_id,
                "--source",
                captured["path"],
                "--title",
                "응답 추세 검토 지식",
                "--body",
                "결정: 다음 주에 응답 추세를 재검토한다. 근거는 품질 회의 메모다.",
            ).stdout
        )
        self.assertTrue((self.root / distilled["path"]).exists())
        distilled_text = (self.root / distilled["path"]).read_text(encoding="utf-8")
        generated = parse_frontmatter_list(distilled_text, "generated_from")
        self.assertEqual(1, len(generated))
        self.assertEqual(captured["path"], generated[0]["ref"])
        self.assertEqual(hashlib.sha256(before).hexdigest(), generated[0]["sha256"])
        self.assertEqual(before, source.read_bytes())

        search = json.loads(
            self.run_cli(
                "local_search.py",
                "응답 추세",
                "--root",
                str(self.root),
                "--employee-id",
                self.employee_id,
                "--json",
            ).stdout
        )
        self.assertGreaterEqual(search["count"], 2)
        self.assertTrue(all(item["path"].startswith(f"data/boi/private/{self.employee_id}/") for item in search["results"]))

        lint = json.loads(self.run_cli("local_lint.py", "--root", str(self.root), "--employee-id", self.employee_id).stdout)
        self.assertTrue(lint["ok"])

    def test_locked_source_tamper_is_detected(self) -> None:
        self.setup_workspace()
        captured = json.loads(
            self.run_cli(
                "local_capture.py",
                "--root",
                str(self.root),
                "--employee-id",
                self.employee_id,
                "--title",
                "잠금 테스트",
                "--body",
                "원래 내용",
            ).stdout
        )
        source = self.root / captured["path"]
        source.write_text(source.read_text(encoding="utf-8").replace("원래 내용", "바뀐 내용"), encoding="utf-8")
        lint = json.loads(self.run_cli("local_lint.py", "--root", str(self.root), "--employee-id", self.employee_id, expected=1).stdout)
        self.assertEqual(1, lint["error_count"])
        self.assertIn("source hash mismatch", " ".join(lint["errors"][0]["issues"]))
        review = json.loads(
            self.run_cli("local_review.py", "--root", str(self.root), "--employee-id", self.employee_id, "--check", expected=1).stdout
        )
        self.assertFalse(review["check_ok"])
        self.assertEqual(1, review["summary"]["integrity_failure_count"])

    def test_safe_intake_blocks_duplicate_and_detects_raw_tamper(self) -> None:
        self.setup_workspace()
        case_id = "TEST-INTAKE-001"
        self.run_cli(
            "local_case.py",
            "--root", str(self.root),
            "--employee-id", self.employee_id,
            "create",
            "--case-id", case_id,
            "--title", "합성 업무 변경 조사",
            "--question", "기존 결정과 새 확인 근거를 어떻게 구분할 것인가?",
        )
        source = REPO / "cases" / "flagship" / "second-brain" / "fixtures" / "sources" / "02-project-update.eml"
        before = source.read_bytes()
        intake = json.loads(
            self.run_cli(
                "local_intake.py",
                "--root", str(self.root),
                "--employee-id", self.employee_id,
                "--case-id", case_id,
                "--source", str(source),
                "--source-ref", "synthetic-fixture",
            ).stdout
        )
        self.assertTrue(intake["source_unchanged"])
        self.assertEqual(before, source.read_bytes())
        raw = self.root / intake["raw_path"]
        self.assertEqual(before, raw.read_bytes())
        sidecar = self.root / intake["path"]
        sidecar_text = sidecar.read_text(encoding="utf-8")
        generated = parse_frontmatter_list(sidecar_text, "generated_from")
        refs = parse_frontmatter_list(sidecar_text, "source_refs")
        self.assertEqual(
            [{"type": "local-file", "ref": intake["raw_path"], "sha256": intake["evidence_sha256"]}],
            generated,
        )
        self.assertEqual(intake["evidence_sha256"], refs[0]["sha256"])

        duplicate = json.loads(
            self.run_cli(
                "local_intake.py",
                "--root", str(self.root),
                "--employee-id", self.employee_id,
                "--case-id", case_id,
                "--source", str(source),
                expected=2,
            ).stdout
        )
        self.assertTrue(duplicate["duplicate"])

        raw.write_bytes(raw.read_bytes() + b"tampered")
        lint = json.loads(
            self.run_cli(
                "local_lint.py",
                "--root", str(self.root),
                "--employee-id", self.employee_id,
                expected=1,
            ).stdout
        )
        issues = " ".join(issue for item in lint["errors"] for issue in item["issues"])
        self.assertIn("evidence hash mismatch", issues)

    def test_safe_intake_covers_supported_evidence_formats_and_blocks_unsupported_override(self) -> None:
        self.setup_workspace()
        case_id = "TEST-INTAKE-FORMATS"
        self.run_cli(
            "local_case.py",
            "--root", str(self.root),
            "--employee-id", self.employee_id,
            "create",
            "--case-id", case_id,
            "--title", "합성 evidence 형식 검사",
            "--question", "지원되는 각 자료 형식이 원본 변경 없이 등록되는가?",
        )
        fixture = REPO / "cases" / "flagship" / "second-brain" / "fixtures" / "sources"
        expected_types = {
            ".eml": "email",
            ".md": "web-clip",
            ".txt": "meeting-note",
            ".csv": "tabular-data",
            ".pdf": "document",
            ".png": "image",
        }
        seen_extensions: set[str] = set()
        for filename in (
            "02-project-update.eml",
            "04-action-register.csv",
            "06-whiteboard-decisions.png",
            "05-operating-guide.pdf",
            "01-decision-chat.txt",
            "03-public-web-clip.md",
        ):
            source = fixture / filename
            before = source.read_bytes()
            intake = json.loads(
                self.run_cli(
                    "local_intake.py",
                    "--root", str(self.root),
                    "--employee-id", self.employee_id,
                    "--case-id", case_id,
                    "--source", str(source),
                    "--source-ref", "synthetic-format-test",
                ).stdout
            )
            suffix = source.suffix.lower()
            seen_extensions.add(suffix)
            self.assertEqual(expected_types[suffix], intake["evidence_type"])
            self.assertEqual(before, source.read_bytes())
            self.assertEqual(before, (self.root / intake["raw_path"]).read_bytes())
            self.assertTrue(intake["local_only"])
            self.assertFalse(intake["remote_submitted"])
        self.assertEqual(set(expected_types), seen_extensions)

        ordinary_markdown = self.root / "ordinary-note.md"
        ordinary_markdown.write_text(
            "---\nsource_kind: meeting-note\n---\n\n# Ordinary Markdown\n",
            encoding="utf-8",
        )
        ordinary = json.loads(
            self.run_cli(
                "local_intake.py",
                "--root", str(self.root),
                "--employee-id", self.employee_id,
                "--case-id", case_id,
                "--source", str(ordinary_markdown),
            ).stdout
        )
        self.assertEqual("meeting-note", ordinary["evidence_type"])

        unsupported = self.root / "unsupported.bin"
        unsupported.write_bytes(b"synthetic unsupported evidence")
        rejected = self.run_cli(
            "local_intake.py",
            "--root", str(self.root),
            "--employee-id", self.employee_id,
            "--case-id", case_id,
            "--source", str(unsupported),
            "--evidence-type", "external-source-note",
            expected=1,
        )
        self.assertIn("unsupported evidence extension", rejected.stderr)

        missing = self.run_cli(
            "local_intake.py",
            "--root", str(self.root),
            "--employee-id", self.employee_id,
            "--case-id", case_id,
            "--source", str(self.root / "missing.pdf"),
            expected=1,
        )
        self.assertIn("source file is missing", missing.stderr)

    def test_case_hypothesis_evidence_relationship_warnings(self) -> None:
        self.setup_workspace()
        case_id = "TEST-RELATION-002"
        self.run_cli(
            "local_case.py", "--root", str(self.root), "--employee-id", self.employee_id,
            "create", "--case-id", case_id, "--title", "합성 결정 근거 조사",
            "--question", "새 자료가 기존 결정을 지지하거나 반박하는가?",
        )
        source = REPO / "cases" / "flagship" / "second-brain" / "fixtures" / "sources" / "04-action-register.csv"
        intake = json.loads(
            self.run_cli(
                "local_intake.py", "--root", str(self.root), "--employee-id", self.employee_id,
                "--case-id", case_id, "--source", str(source),
            ).stdout
        )
        evidence_id = intake["evidence_id"]
        self.run_cli(
            "local_case.py", "--root", str(self.root), "--employee-id", self.employee_id,
            "hypothesis", "--case-id", case_id, "--hypothesis-id", "H1",
            "--statement", "합성 Action register가 기존 결정을 지지한다", "--status", "open",
            "--supports", evidence_id, "--contradicts", evidence_id,
        )
        self.run_cli(
            "local_case.py", "--root", str(self.root), "--employee-id", self.employee_id,
            "hypothesis", "--case-id", case_id, "--hypothesis-id", "H2",
            "--statement", "추가 자료가 필요하다", "--status", "open",
            "--supports", "E-DEADBEEF0000",
        )
        review = json.loads(
            self.run_cli(
                "local_case.py", "--root", str(self.root), "--employee-id", self.employee_id,
                "review", "--case-id", case_id,
            ).stdout
        )
        self.assertEqual(1, len(review["evidence"]))
        self.assertEqual(2, len(review["hypotheses"]))
        lint = json.loads(
            self.run_cli("local_lint.py", "--root", str(self.root), "--employee-id", self.employee_id).stdout
        )
        warnings = " ".join(item["issue"] for item in lint["warnings"])
        self.assertIn("both support and contradiction", warnings)
        self.assertIn("unknown evidence reference", warnings)

    def test_local_lint_blocks_llm_invented_type_and_field(self) -> None:
        self.setup_workspace()
        case_id = "TEST-SCHEMA-001"
        self.run_cli(
            "local_case.py", "--root", str(self.root), "--employee-id", self.employee_id,
            "create", "--case-id", case_id, "--title", "Schema contract test",
            "--question", "Can an LLM invent a page schema?",
        )
        hub = self.root / "data" / "boi" / "private" / self.employee_id / "cases" / case_id / "case-hub.md"
        text = hub.read_text(encoding="utf-8")
        text = text.replace("type: boi/local-analysis-case", "type: boi/local-invented-page")
        text = text.replace("case_id:", "invented_llm_field: true\ncase_id:")
        hub.write_text(text, encoding="utf-8")
        lint = json.loads(
            self.run_cli("local_lint.py", "--root", str(self.root), "--employee-id", self.employee_id, expected=1).stdout
        )
        issues = " ".join(issue for item in lint["errors"] for issue in item["issues"])
        self.assertIn("type is not allowed by the Local schema", issues)
        self.assertIn("field is not allowed by the Local schema: invented_llm_field", issues)

    def test_semantic_lint_detects_downstream_gap_conflict_and_stale_claim(self) -> None:
        self.setup_workspace()
        case_id = "TEST-SEMANTIC-001"
        self.run_cli(
            "local_case.py", "--root", str(self.root), "--employee-id", self.employee_id,
            "create", "--case-id", case_id, "--title", "Semantic lint test",
            "--question", "Which evidence has reached a downstream claim?",
        )
        source = REPO / "cases" / "flagship" / "second-brain" / "fixtures" / "sources" / "04-action-register.csv"
        intake = json.loads(
            self.run_cli(
                "local_intake.py", "--root", str(self.root), "--employee-id", self.employee_id,
                "--case-id", case_id, "--source", str(source),
            ).stdout
        )
        first_lint = json.loads(
            self.run_cli("local_lint.py", "--root", str(self.root), "--employee-id", self.employee_id).stdout
        )
        first_warnings = " ".join(item["issue"] for item in first_lint["warnings"])
        self.assertIn("not reflected in any downstream compiled page", first_warnings)

        for hypothesis_id, status in (("H1", "open"), ("H2", "supported")):
            self.run_cli(
                "local_case.py", "--root", str(self.root), "--employee-id", self.employee_id,
                "hypothesis", "--case-id", case_id, "--hypothesis-id", hypothesis_id,
                "--statement", f"Synthetic hypothesis {hypothesis_id}", "--status", status,
                "--supports", intake["evidence_id"],
            )
        h2 = self.root / "data" / "boi" / "private" / self.employee_id / "cases" / case_id / "hypotheses" / "h2.md"
        text = h2.read_text(encoding="utf-8")
        text = text.replace('hypothesis_id: "H2"', 'hypothesis_id: "H1"')
        text = text.replace("review_after: ", "review_after: 2000-01-01 # was ", 1)
        h2.write_text(text, encoding="utf-8")
        lint = json.loads(
            self.run_cli("local_lint.py", "--root", str(self.root), "--employee-id", self.employee_id).stdout
        )
        warnings = " ".join(item["issue"] for item in lint["warnings"])
        self.assertIn("contradicting hypothesis states for H1", warnings)
        self.assertIn("stale claim review date elapsed", warnings)

    def test_llm_wiki_ingest_requires_exact_plan_and_preserves_raw_evidence(self) -> None:
        self.setup_workspace()
        case_id = "TEST-INGEST-001"
        self.run_cli(
            "local_case.py", "--root", str(self.root), "--employee-id", self.employee_id,
            "create", "--case-id", case_id, "--title", "Synthetic knowledge investigation",
            "--question", "Which evidence changes the current hypothesis?",
        )
        source = REPO / "cases" / "flagship" / "second-brain" / "fixtures" / "sources" / "04-action-register.csv"
        intake = json.loads(
            self.run_cli(
                "local_intake.py", "--root", str(self.root), "--employee-id", self.employee_id,
                "--case-id", case_id, "--source", str(source),
            ).stdout
        )
        self.run_cli(
            "local_case.py", "--root", str(self.root), "--employee-id", self.employee_id,
            "hypothesis", "--case-id", case_id, "--hypothesis-id", "H1",
            "--statement", "The action register supports the current decision", "--supports", intake["evidence_id"],
        )
        raw = self.root / intake["raw_path"]
        raw_before = raw.read_bytes()
        preview = json.loads(
            self.run_cli(
                "local_wiki.py", "--root", str(self.root), "--employee-id", self.employee_id,
                "ingest-preview", "--case-id", case_id, "--evidence-id", intake["evidence_id"],
            ).stdout
        )
        self.assertEqual("0.1", preview["profile_contract"]["okf_version"])
        self.assertEqual("0.1-local", preview["profile_contract"]["boi_profile_version"])
        self.assertFalse(preview["raw_mutation_allowed"])
        self.assertIn("review_targets", preview)
        self.run_cli(
            "local_wiki.py", "--root", str(self.root), "--employee-id", self.employee_id,
            "ingest-apply", "--case-id", case_id, "--evidence-id", intake["evidence_id"],
            "--confirm-plan-hash", "wrong-hash", expected=2,
        )
        applied = json.loads(
            self.run_cli(
                "local_wiki.py", "--root", str(self.root), "--employee-id", self.employee_id,
                "ingest-apply", "--case-id", case_id, "--evidence-id", intake["evidence_id"],
                "--confirm-plan-hash", preview["plan_hash"],
            ).stdout
        )
        self.assertTrue((self.root / applied["archive"]).is_dir())
        self.assertEqual(raw_before, raw.read_bytes())
        self.assertTrue(applied["raw_source_unchanged"])
        self.assertFalse(applied["remote_submitted"])
        self.assertTrue(any(path.endswith("analysis-log.md") for path in applied["review_targets_not_mutated"]))
        hypothesis = self.root / "data" / "boi" / "private" / self.employee_id / "cases" / case_id / "hypotheses" / "h1.md"
        self.assertIn(intake["path"], hypothesis.read_text(encoding="utf-8"))

    def test_llm_wiki_query_separates_remote_refs_and_saves_okf_profile(self) -> None:
        self.setup_workspace()
        case_id = "TEST-QUERY-001"
        created = json.loads(
            self.run_cli(
                "local_case.py", "--root", str(self.root), "--employee-id", self.employee_id,
                "create", "--case-id", case_id, "--title", "Synthetic recurrence query",
                "--question", "What evidence supports recurrence?",
            ).stdout
        )
        pack = json.loads(
            self.run_cli(
                "local_wiki.py", "--root", str(self.root), "--employee-id", self.employee_id,
                "query-pack", "--case-id", case_id, "--question", "recurrence evidence",
                "--remote-ref", "boi:team:yield:guide|r17|team|Yield guide",
            ).stdout
        )
        self.assertTrue(pack["local_sources"])
        self.assertEqual("boi-local-wiki-query-pack/v2", pack["schema"])
        self.assertIn("compiled_sources", pack)
        self.assertIn("evidence_sources", pack)
        self.assertEqual("local path + exact SHA256; remote BoI ID + revision + visibility", pack["answer_contract"]["citation_format"])
        self.assertEqual("remote-boi", pack["remote_sources"][0]["type"])
        self.assertEqual("read-only-references-provided", pack["mcp_mode"])
        self.assertFalse(pack["remote_mutation_allowed"])
        answer = self.root / "reviewed-answer.md"
        answer.write_text("Current evidence is suggestive; an additional controlled comparison is required.\n", encoding="utf-8")
        saved = json.loads(
            self.run_cli(
                "local_wiki.py", "--root", str(self.root), "--employee-id", self.employee_id,
                "query-save", "--case-id", case_id, "--question", "What supports recurrence?",
                "--answer-file", str(answer), "--citation", created["path"],
                "--contradiction", "Retest evidence remains unresolved", "--unknown", "Missing trace window",
            ).stdout
        )
        saved_path = self.root / saved["path"]
        metadata = parse_frontmatter(saved_path.read_text(encoding="utf-8"))
        generated = parse_frontmatter_list(saved_path.read_text(encoding="utf-8"), "generated_from")
        self.assertEqual("0.1", metadata["okf_version"])
        self.assertEqual("0.1-local", metadata["boi_profile_version"])
        self.assertEqual("boi/local-knowledge-note", metadata["type"])
        self.assertEqual("saved-query", metadata["knowledge_role"])
        self.assertEqual(1, len(generated))
        self.assertEqual(created["path"], generated[0]["ref"])
        self.assertEqual(64, len(generated[0]["sha256"]))
        self.assertFalse(saved["remote_submitted"])

    def test_archive_search_is_opt_in(self) -> None:
        self.setup_workspace()
        archived = self.root / "data" / "boi" / "private" / self.employee_id / "_archive" / "legacy.md"
        archived.parent.mkdir(parents=True, exist_ok=True)
        archived.write_text("archive-only-signal\n", encoding="utf-8")
        default = json.loads(
            self.run_cli(
                "local_search.py", "archive-only-signal", "--root", str(self.root),
                "--employee-id", self.employee_id, "--json",
            ).stdout
        )
        included = json.loads(
            self.run_cli(
                "local_search.py", "archive-only-signal", "--root", str(self.root),
                "--employee-id", self.employee_id, "--json", "--include-archive",
            ).stdout
        )
        self.assertEqual(0, default["count"])
        self.assertEqual(1, included["count"])
        self.assertTrue(included["results"][0]["archived"])
        default_lint = json.loads(
            self.run_cli("local_lint.py", "--root", str(self.root), "--employee-id", self.employee_id).stdout
        )
        archive_lint = json.loads(
            self.run_cli(
                "local_lint.py", "--root", str(self.root), "--employee-id", self.employee_id,
                "--include-archive", expected=1,
            ).stdout
        )
        self.assertTrue(default_lint["ok"])
        self.assertIn("missing YAML frontmatter", " ".join(issue for item in archive_lint["errors"] for issue in item["issues"]))
        review = json.loads(
            self.run_cli("local_review.py", "--root", str(self.root), "--employee-id", self.employee_id, "--check").stdout
        )
        serialized_review = json.dumps(review, ensure_ascii=False)
        self.assertNotIn("legacy.md", serialized_review)

    def test_recurrence_fingerprint_has_explicit_canonical_mapping(self) -> None:
        self.setup_workspace()
        base = self.root / "data" / "boi" / "private" / self.employee_id
        source = base / "notes" / "knowledge" / "recurrence.md"
        source.write_text(
            local_frontmatter(
                employee_id=self.employee_id,
                doc_type="boi/local-recurrence-fingerprint",
                title="Synthetic recurrence fingerprint",
                description="Reusable synthetic signal pattern",
                boi_id=f"boi:private:{self.employee_id}:recurrence:synthetic",
                tags=["second-brain", "recurrence"],
                source_refs=[{"type": "local-document", "ref": "synthetic-case"}],
                contains_sensitive="false",
                extra={"case_id": "LOCAL-CASE-001"},
            ) + "\n# Synthetic recurrence fingerprint\n\nReviewed synthetic pattern.\n",
            encoding="utf-8",
        )
        preflight = json.loads(
            self.run_cli(
                "promotion_preflight.py", "--root", str(self.root), "--employee-id", self.employee_id,
                "--source", source.relative_to(self.root).as_posix(),
                "--sanitized-title", "Recurrence fingerprint", "--sanitized-description", "Reviewed reusable pattern",
                "--target-visibility", "team",
                "--team-id", "knowledge-operations", "--reviewer", "knowledge-reviewer",
                "--source-ref", "boi=boi:team:knowledge:synthetic-source",
            ).stdout
        )
        projection = json.loads((self.root / preflight["remote_projection_path"]).read_text(encoding="utf-8"))
        metadata = projection["candidate"]["metadata"]
        self.assertEqual("boi/knowledge", metadata["type"])
        self.assertEqual("recurrence-fingerprint", metadata["knowledge_subtype"])
        self.assertNotIn("LOCAL-CASE-001", json.dumps(projection))
        self.assertNotIn(self.employee_id, json.dumps(projection))
        self.assertFalse(projection["submit_contract"]["remote_submit_allowed"])

    def test_markdown_web_clip_is_raw_evidence_not_a_profile_document(self) -> None:
        self.setup_workspace()
        case_id = "TEST-WEB-CLIP"
        self.run_cli(
            "local_case.py", "--root", str(self.root), "--employee-id", self.employee_id,
            "create", "--case-id", case_id, "--title", "외부 조사 자료",
            "--question", "공개 자료가 현재 분석 질문에 어떤 원칙을 제공하는가?",
        )
        source = REPO / "cases" / "flagship" / "second-brain" / "fixtures" / "sources" / "03-public-web-clip.md"
        self.run_cli(
            "local_intake.py", "--root", str(self.root), "--employee-id", self.employee_id,
            "--case-id", case_id, "--source", str(source), "--sensitivity", "public",
            "--source-ref", "https://example.invalid/synthetic-public-source",
        )
        lint = json.loads(
            self.run_cli("local_lint.py", "--root", str(self.root), "--employee-id", self.employee_id).stdout
        )
        self.assertTrue(lint["ok"])

    def test_promotion_preflight_blocks_secret_and_never_submits(self) -> None:
        self.setup_workspace()
        captured = json.loads(
            self.run_cli(
                "local_capture.py",
                "--root",
                str(self.root),
                "--employee-id",
                self.employee_id,
                "--title",
                "민감정보 테스트",
                "--body",
                "api_key=do-not-share",
            ).stdout
        )
        preflight = json.loads(
            self.run_cli(
                "promotion_preflight.py",
                "--root",
                str(self.root),
                "--employee-id",
                self.employee_id,
                "--source",
                captured["path"],
                "--target-visibility",
                "public",
                "--reviewer",
                "security-reviewer",
                expected=2,
            ).stdout
        )
        self.assertFalse(preflight["ok"])
        self.assertIn("secret-like value", preflight["blockers"])
        self.assertFalse(preflight["remote_submitted"])
        draft = (self.root / preflight["path"]).read_text(encoding="utf-8")
        self.assertIn("remote_submit_allowed: false", draft)
        self.assertIn("requires_explicit_user_approval: true", draft)

    def test_agent_memory_must_be_distilled_before_promotion(self) -> None:
        self.setup_workspace()
        memory = self.root / "data" / "boi" / "private" / self.employee_id / "notes" / "memory" / "review-policy.md"
        memory.parent.mkdir(parents=True, exist_ok=True)
        memory.write_text(
            local_frontmatter(
                employee_id=self.employee_id,
                doc_type="boi/local-knowledge-note",
                title="Review policy memory",
                description="Conversation-derived Local-only memory",
                boi_id=f"boi:private:{self.employee_id}:memory:review-policy",
                tags=["second-brain", "agent-memory"],
                source_refs=[{"type": "agent-session", "ref": "agent-session:test:abc", "note": "raw transcript not copied"}],
                promotion_status="local_only",
                artifact_visibility="memory",
                lifecycle_state="memory",
                memory_candidate=True,
                extra={
                    "knowledge_role": "agent-memory",
                    "memory_key": "review-policy",
                    "memory_kind": "decision",
                    "memory_status": "active",
                    "memory_operation": "create",
                    "claim_status": "direct",
                },
            )
            + "\n# Review policy\n\nSource: https://example.invalid/review-policy\n",
            encoding="utf-8",
        )
        preflight = json.loads(
            self.run_cli(
                "promotion_preflight.py", "--root", str(self.root), "--employee-id", self.employee_id,
                "--source", memory.relative_to(self.root).as_posix(), "--target-visibility", "team",
                "--team-id", "TEAM-QA", "--reviewer", "knowledge-reviewer", "--dry-run", expected=2,
            ).stdout
        )
        self.assertFalse(preflight["ok"])
        self.assertTrue(any("agent-memory is Local-only" in item for item in preflight["blockers"]))
        self.assertFalse(preflight["remote_submitted"])

    def test_public_preflight_contains_harness_acl_and_idempotency_contract(self) -> None:
        self.setup_workspace()
        captured = json.loads(
            self.run_cli(
                "local_capture.py",
                "--root",
                str(self.root),
                "--employee-id",
                self.employee_id,
                "--title",
                "공개 가이드 근거",
                "--body",
                "Vault 근거: https://help.obsidian.md/vault",
            ).stdout
        )
        distilled = json.loads(
            self.run_cli(
                "local_distill.py",
                "--root",
                str(self.root),
                "--employee-id",
                self.employee_id,
                "--source",
                captured["path"],
                "--title",
                "Public guide evidence",
                "--body",
                "Vault evidence: https://help.obsidian.md/vault",
                "--contains-sensitive",
                "false",
            ).stdout
        )
        preflight = json.loads(
            self.run_cli(
                "promotion_preflight.py",
                "--root",
                str(self.root),
                "--employee-id",
                self.employee_id,
                "--source",
                distilled["path"],
                "--target-visibility",
                "public",
                "--reviewer",
                "public-reviewer",
                "--sanitized-description",
                "공개 가능한 Vault 근거",
            ).stdout
        )
        self.assertTrue(preflight["ok"])
        self.assertEqual("harness-2.0-44d7fde6838a", preflight["harness_release"])
        self.assertEqual(64, len(preflight["idempotency_key"]))
        self.assertFalse(preflight["remote_submitted"])
        self.assertTrue((self.root / preflight["package_path"]).exists())
        self.assertTrue((self.root / preflight["remote_projection_path"]).exists())
        package = json.loads((self.root / preflight["package_path"]).read_text(encoding="utf-8"))
        self.assertEqual("false", package["local_provenance"]["contains_sensitive"])
        self.assertEqual("url", preflight["source_refs"][0]["type"])
        draft = (self.root / preflight["path"]).read_text(encoding="utf-8")
        self.assertIn('"acl_policy": "<remote-derived>"', draft)
        self.assertIn('"expected_revision_status": "required_at_submit"', draft)
        self.assertIn('"user_confirmed": false', draft)

        projection = json.loads((self.root / preflight["remote_projection_path"]).read_text(encoding="utf-8"))
        metadata = projection["candidate"]["metadata"]
        self.assertEqual("0.1", metadata["okf_version"])
        self.assertEqual("0.1", metadata["boi_profile_version"])
        self.assertEqual("public", metadata["visibility"])
        self.assertEqual("internal", metadata["classification"])
        self.assertEqual("public-reviewer", metadata["review"]["reviewer"])
        self.assertNotIn("employee_id", json.dumps(projection, ensure_ascii=False))
        self.assertNotIn("data/boi/private", json.dumps(projection, ensure_ascii=False))

        compatibility_args = ["--projection", str(self.root / preflight["remote_projection_path"])]
        if os.environ.get("BOI_WIKI_ROOT"):
            compatibility_args.extend(["--boi-wiki-root", os.environ["BOI_WIKI_ROOT"]])
        compatibility = json.loads(self.run_cli("boi_compatibility.py", *compatibility_args).stdout)
        self.assertTrue(compatibility["ok"])

    def test_promotion_requires_explicit_sensitive_false(self) -> None:
        self.setup_workspace()
        captured = json.loads(
            self.run_cli(
                "local_capture.py", "--root", str(self.root), "--employee-id", self.employee_id,
                "--title", "Unreviewed sensitivity", "--body", "Source: https://example.com/public",
            ).stdout
        )
        distilled = json.loads(
            self.run_cli(
                "local_distill.py", "--root", str(self.root), "--employee-id", self.employee_id,
                "--source", captured["path"], "--title", "Unreviewed public candidate",
                "--body", "Public claim: https://example.com/public",
            ).stdout
        )
        source_text = (self.root / distilled["path"]).read_text(encoding="utf-8")
        self.assertIn("contains_sensitive: unknown", source_text)
        preflight = json.loads(
            self.run_cli(
                "promotion_preflight.py", "--root", str(self.root), "--employee-id", self.employee_id,
                "--source", distilled["path"], "--target-visibility", "public",
                "--reviewer", "public-reviewer", "--dry-run", expected=2,
            ).stdout
        )
        self.assertFalse(preflight["ok"])
        self.assertIn(
            "Team/Public promotion requires contains_sensitive: false after review; current value is unknown",
            preflight["blockers"],
        )
        self.assertFalse(preflight["remote_submitted"])

    def test_public_preflight_blocks_internal_boi_source_refs(self) -> None:
        self.setup_workspace()
        captured = json.loads(
            self.run_cli(
                "local_capture.py", "--root", str(self.root), "--employee-id", self.employee_id,
                "--title", "Internal-only source", "--body", "Internal source boi:team:knowledge:restricted",
            ).stdout
        )
        distilled = json.loads(
            self.run_cli(
                "local_distill.py", "--root", str(self.root), "--employee-id", self.employee_id,
                "--source", captured["path"], "--title", "Public candidate",
                "--body", "Claim supported only by boi:team:knowledge:restricted",
            ).stdout
        )
        preflight = json.loads(
            self.run_cli(
                "promotion_preflight.py", "--root", str(self.root), "--employee-id", self.employee_id,
                "--source", distilled["path"], "--target-visibility", "public",
                "--reviewer", "public-reviewer", expected=2,
            ).stdout
        )
        self.assertFalse(preflight["ok"])
        self.assertTrue(any("non-public source_refs" in item for item in preflight["blockers"]))
        self.assertTrue(any("public URL or boi:public" in item for item in preflight["blockers"]))
        self.assertFalse(preflight["remote_submitted"])
        compatibility = json.loads(
            self.run_cli(
                "boi_compatibility.py", "--projection",
                str(self.root / preflight["remote_projection_path"]), expected=1,
            ).stdout
        )
        self.assertFalse(compatibility["ok"])
        self.assertTrue(any(
            "non-public source_refs" in item for item in compatibility["builtin_contract"]["errors"]
        ))

    def test_team_preflight_requires_team_id_reviewer_and_remote_safe_refs(self) -> None:
        self.setup_workspace()
        captured = json.loads(
            self.run_cli(
                "local_capture.py",
                "--root",
                str(self.root),
                "--employee-id",
                self.employee_id,
                "--title",
                "Team knowledge",
                "--body",
                "Decision without a shared citation",
            ).stdout
        )
        distilled = json.loads(
            self.run_cli(
                "local_distill.py",
                "--root",
                str(self.root),
                "--employee-id",
                self.employee_id,
                "--source",
                captured["path"],
                "--title",
                "Team knowledge",
                "--body",
                "Decision supported by the team canonical citation.",
                "--contains-sensitive",
                "false",
            ).stdout
        )
        blocked = json.loads(
            self.run_cli(
                "promotion_preflight.py",
                "--root",
                str(self.root),
                "--employee-id",
                self.employee_id,
                "--source",
                distilled["path"],
                "--target-visibility",
                "team",
                expected=2,
            ).stdout
        )
        self.assertIn("Team promotion requires --team-id", blocked["blockers"])
        self.assertIn("Team/Public promotion requires --reviewer", blocked["blockers"])

        ready = json.loads(
            self.run_cli(
                "promotion_preflight.py",
                "--root",
                str(self.root),
                "--employee-id",
                self.employee_id,
                "--source",
                distilled["path"],
                "--target-visibility",
                "team",
                "--team-id",
                "platform",
                "--reviewer",
                "platform-lead",
                "--sanitized-description",
                "검토된 Team 지식",
                "--source-ref",
                "boi=boi:team:platform:source",
            ).stdout
        )
        self.assertTrue(ready["ok"])
        projection = json.loads((self.root / ready["remote_projection_path"]).read_text(encoding="utf-8"))
        self.assertEqual("platform", projection["candidate"]["metadata"]["team_id"])

    def test_obsidian_config_and_guide_update_require_confirmation_and_recover(self) -> None:
        self.setup_workspace()
        base = self.root / "data" / "boi" / "private" / self.employee_id
        preview = json.loads(self.run_cli("boi_setup.py", "obsidian-preview", "--root", str(self.root), "--employee-id", self.employee_id).stdout)
        self.assertTrue(preview["requires_confirmation"])
        self.assertFalse(preview["installs_community_plugins"])
        self.run_cli("boi_setup.py", "obsidian-apply", "--root", str(self.root), "--employee-id", self.employee_id, expected=1)
        applied = json.loads(
            self.run_cli(
                "boi_setup.py",
                "obsidian-apply",
                "--root",
                str(self.root),
                "--employee-id",
                self.employee_id,
                "--confirm-obsidian-config",
            ).stdout
        )
        self.assertEqual([], applied["community_plugins_installed"])
        self.assertTrue((base / ".obsidian" / "core-plugins.json").exists())
        core_plugins = json.loads((base / ".obsidian" / "core-plugins.json").read_text(encoding="utf-8"))
        self.assertIsInstance(core_plugins, dict)
        for plugin_id in ("global-search", "graph", "backlink", "properties", "bases", "canvas"):
            self.assertIs(core_plugins.get(plugin_id), True)
        graph = json.loads((base / ".obsidian" / "graph.json").read_text(encoding="utf-8"))
        self.assertIn("-path:notes/capture-inbox", graph["search"])
        self.assertIn("-path:notes/guide", graph["search"])
        self.assertIn("-path:promotion-drafts", graph["search"])
        self.assertNotIn('path:"capture-inbox" OR', graph["search"])
        self.assertTrue(applied["recovery_available"])
        self.assertTrue((base / ".obsidian" / "boi-wiki-local-managed.json").exists())

        app_config = base / ".obsidian" / "app.json"
        app_config.write_text(app_config.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        recovery_preview = json.loads(
            self.run_cli("boi_setup.py", "obsidian-recover-preview", "--root", str(self.root), "--employee-id", self.employee_id).stdout
        )
        self.assertIn(app_config.relative_to(self.root).as_posix(), recovery_preview["preserve_modified"])
        self.assertIn((base / ".obsidian" / "core-plugins.json").relative_to(self.root).as_posix(), recovery_preview["remove_safe"])
        self.run_cli("boi_setup.py", "obsidian-recover-apply", "--root", str(self.root), "--employee-id", self.employee_id, expected=1)
        recovered = json.loads(
            self.run_cli(
                "boi_setup.py",
                "obsidian-recover-apply",
                "--root",
                str(self.root),
                "--employee-id",
                self.employee_id,
                "--confirm-obsidian-recovery",
            ).stdout
        )
        self.assertTrue(app_config.exists())
        self.assertFalse((base / ".obsidian" / "core-plugins.json").exists())
        self.assertIn(app_config.relative_to(self.root).as_posix(), recovered["preserved_modified"])

        guide = base / "notes" / "guide" / "00-start-here.md"
        newly_added_guide = base / "notes" / "guide" / "05-choose-your-path.md"
        newly_added_guide.unlink()
        guide.write_text(guide.read_text(encoding="utf-8") + "\n사용자 수정\n", encoding="utf-8")
        update_preview = json.loads(self.run_cli("boi_setup.py", "guide-preview", "--root", str(self.root), "--employee-id", self.employee_id).stdout)
        self.assertTrue(update_preview["requires_confirmation"])
        self.run_cli("boi_setup.py", "guide-apply", "--root", str(self.root), "--employee-id", self.employee_id, expected=1)
        update = json.loads(
            self.run_cli(
                "boi_setup.py",
                "guide-apply",
                "--root",
                str(self.root),
                "--employee-id",
                self.employee_id,
                "--confirm-guide-release",
                "3.2.0",
            ).stdout
        )
        self.assertTrue(update["backup"])
        self.assertIn(newly_added_guide.relative_to(self.root).as_posix(), update["created"])
        self.assertTrue(newly_added_guide.exists())
        self.assertNotIn("사용자 수정", guide.read_text(encoding="utf-8"))
        self.assertTrue((self.root / update["backup"] / "00-start-here.md").exists())

        media = base / "notes" / "guide" / "_media" / "01-explorer-repository.webp"
        original_media = media.read_bytes()
        media.write_bytes(original_media + b"user-edit")
        asset_preview = json.loads(
            self.run_cli("boi_setup.py", "guide-preview", "--root", str(self.root), "--employee-id", self.employee_id).stdout
        )
        relative_media = media.relative_to(self.root).as_posix()
        self.assertIn(relative_media, asset_preview["guide_asset_updates_available"])
        self.assertTrue(media.read_bytes().endswith(b"user-edit"))
        asset_update = json.loads(
            self.run_cli(
                "boi_setup.py",
                "guide-apply",
                "--root",
                str(self.root),
                "--employee-id",
                self.employee_id,
                "--confirm-guide-release",
                "3.2.0",
            ).stdout
        )
        self.assertIn(relative_media, asset_update["guide_asset_updates_available"])
        self.assertEqual(original_media, media.read_bytes())
        self.assertTrue((self.root / asset_update["backup"] / "_media" / media.name).exists())

    def test_windows_obsidian_is_blocked_for_wsl_vault_transport(self) -> None:
        compatibility = obsidian_compatibility(Path("//wsl.localhost/Ubuntu-22.04/home/user/boi-wiki-local"), "windows")
        self.assertFalse(compatibility["ok"])
        self.assertEqual("blocked-verified", compatibility["status"])
        self.assertEqual("skip-obsidian-and-continue-local", compatibility["recommended_action"])
        self.assertFalse(compatibility["shadow_copy_allowed"])

        native = obsidian_compatibility(Path("C:/Users/example/boi-wiki-local"), "windows")
        self.assertTrue(native["ok"])
        self.assertEqual("windows-native", native["vault_transport"])


if __name__ == "__main__":
    unittest.main()
