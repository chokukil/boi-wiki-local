from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
CASE_PATHS = (
    "cases/research/agentic-ai-change-radar",
    "cases/strategy/fab-logistics-digital-twin",
    "cases/strategy/scientific-foundation-model-knowledge",
)


class GlobalInsightTests(unittest.TestCase):
    def run_native_gate(self, *artifact_paths: Path) -> subprocess.CompletedProcess[str]:
        command = [
            "powershell.exe",
            "-NoLogo",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(REPO / "scripts" / "global_insight_native_check.ps1"),
            "-Root",
            str(REPO),
        ]
        if artifact_paths:
            command += ["-ArtifactPath", *[str(path) for path in artifact_paths]]
        return subprocess.run(
            command,
            cwd=REPO,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

    def test_seven_natural_language_tools_and_safety_boundaries_are_explicit(self) -> None:
        text = (REPO / "templates" / "global-insight" / "README.md").read_text(encoding="utf-8")
        for name, identifier in (
            ("Capture", "capture"),
            ("Update", "update"),
            ("Query", "query"),
            ("DeepResearch", "deep-research"),
            ("Health", "health"),
            ("Review", "review"),
            ("Promote", "promote"),
        ):
            self.assertIn(f"| {name} | `{identifier}` |", text)
        self.assertIn("변화가 없을 때 보고서 생성", text)
        self.assertIn("외부 조사 자동 실행", text)
        self.assertIn("의미적 결론 자동 수정", text)
        self.assertIn("승인 전 전송", text)

    def test_all_three_cases_are_public_only_community_packages(self) -> None:
        for relative in CASE_PATHS:
            root = REPO / relative
            case = json.loads((root / "case.yaml").read_text(encoding="utf-8"))
            manifest = json.loads((root / "fixtures" / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual("community", case["status"])
            self.assertEqual("public-only", case["fixture_policy"])
            self.assertFalse(manifest["synthetic"])
            self.assertEqual("public-only", manifest["fixture_policy"])
            self.assertEqual(manifest["source_count"], len(manifest["files"]))
            self.assertGreaterEqual(manifest["source_count"], 5)
            for row in manifest["files"]:
                path = root / "fixtures" / row["path"]
                self.assertEqual(row["bytes"], path.stat().st_size)
                self.assertEqual(row["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())

    def test_machine_readable_runtime_contract_matches_the_user_interface(self) -> None:
        contract = json.loads(
            (REPO / "templates" / "global-insight" / "runtime-contract.json").read_text(encoding="utf-8")
        )
        self.assertEqual("boi-global-insight-runtime/v1", contract["schema"])
        self.assertEqual(
            [
                ("Capture", "capture"),
                ("Update", "update"),
                ("Query", "query"),
                ("DeepResearch", "deep-research"),
                ("Health", "health"),
                ("Review", "review"),
                ("Promote", "promote"),
            ],
            [(tool["name"], tool["id"]) for tool in contract["tools"]],
        )
        query = next(tool for tool in contract["tools"] if tool["id"] == "query")
        research = next(tool for tool in contract["tools"] if tool["id"] == "deep-research")
        health = next(tool for tool in contract["tools"] if tool["id"] == "health")
        promote = next(tool for tool in contract["tools"] if tool["id"] == "promote")
        self.assertEqual("current-local-only", query["knowledge_scope"])
        self.assertFalse(query["auto_deep_research"])
        self.assertEqual(["explicit-user-request", "approved-query-scope"], research["start_policy"])
        self.assertFalse(health["semantic_mutation"])
        self.assertTrue(promote["requires_exact_preview_approval"])
        self.assertTrue(all(tool["remote_submit"] is False for tool in contract["tools"]))

    @unittest.skipUnless(os.name == "nt", "Windows native PowerShell gate")
    def test_native_contract_examples_pass_and_fail_closed(self) -> None:
        valid = self.run_native_gate()
        self.assertEqual(0, valid.returncode, valid.stdout + valid.stderr)

        examples = REPO / "templates" / "global-insight" / "examples"
        with tempfile.TemporaryDirectory() as temporary:
            temp = Path(temporary)
            candidate = temp / "promotion-candidate.md"
            preview = temp / "promotion-preview.json"
            shutil.copy2(examples / candidate.name, candidate)
            shutil.copy2(examples / preview.name, preview)
            candidate.write_text(candidate.read_text(encoding="utf-8") + "\nchanged\n", encoding="utf-8")
            drift = self.run_native_gate(preview)
            self.assertNotEqual(0, drift.returncode)
            self.assertIn("promotion candidate hash or bytes drift", drift.stdout)

            failure = json.loads((examples / "failure-resume.json").read_text(encoding="utf-8"))
            del failure["resume_condition"]
            broken_failure = temp / "failure-resume.json"
            broken_failure.write_text(json.dumps(failure, ensure_ascii=False), encoding="utf-8")
            missing_resume = self.run_native_gate(broken_failure)
            self.assertNotEqual(0, missing_resume.returncode)
            self.assertIn("missing required field: resume_condition", missing_resume.stdout)

            invalidation = json.loads((examples / "hash-invalidation.json").read_text(encoding="utf-8"))
            invalidation["invalidated_dependent_artifacts"] = []
            broken_invalidation = temp / "hash-invalidation.json"
            broken_invalidation.write_text(json.dumps(invalidation, ensure_ascii=False), encoding="utf-8")
            rejected_invalidation = self.run_native_gate(broken_invalidation)
            self.assertNotEqual(0, rejected_invalidation.returncode)
            self.assertIn("hash change did not invalidate dependents", rejected_invalidation.stdout)

    def test_golden_journey_reproduces_all_delta_categories(self) -> None:
        root = REPO / "cases" / "research" / "agentic-ai-change-radar"
        expected = (root / "expected" / "t1-change-set.md").read_text(encoding="utf-8")
        for delta in ("new", "strengthened", "revised", "contradicted", "stale", "retirement-candidate", "unknown"):
            self.assertIn(f"| {delta} |", expected)
        self.assertIn("T0 baseline claim snapshot", (root / "expected" / "t0-snapshot.md").read_text(encoding="utf-8"))
        self.assertIn("Expected review queue", (root / "expected" / "review-queue.md").read_text(encoding="utf-8"))
        preview = json.loads((root / "expected" / "promotion-preview.json").read_text(encoding="utf-8"))
        candidate = root / "expected" / preview["candidate_path"]
        self.assertEqual(preview["candidate_sha256"], hashlib.sha256(candidate.read_bytes()).hexdigest())
        self.assertFalse(preview["approved"])
        self.assertFalse(preview["submitted"])

    def test_native_only_path_runs_without_invoking_python(self) -> None:
        check = (REPO / "check.ps1").read_text(encoding="utf-8")
        native_branch = check.index("if ($NativeOnly)")
        python_branch = check.index("elseif ($python)", native_branch)
        self.assertLess(native_branch, python_branch)
        self.assertIn("global_insight_native_check.ps1", check[:native_branch])
        if os.name == "nt":
            completed = subprocess.run(
                ["powershell.exe", "-NoLogo", "-NoProfile", "-ExecutionPolicy", "RemoteSigned", "-File", str(REPO / "check.ps1"), "-NativeOnly"],
                cwd=REPO,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
            self.assertIn("Global Insight native check passed", completed.stdout)

    def test_generic_skill_is_not_created_from_unexecuted_cases(self) -> None:
        for root in (REPO / ".agents" / "skills", REPO / ".claude" / "skills"):
            self.assertFalse((root / "global-insight").exists())
            self.assertFalse((root / "agentic-ai-change-radar").exists())


if __name__ == "__main__":
    unittest.main()
