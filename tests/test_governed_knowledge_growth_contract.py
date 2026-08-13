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


class GovernedKnowledgeGrowthContractTests(unittest.TestCase):
    def make_profile_fixture(self, root: Path) -> tuple[str, str, Path, Path]:
        employee_id = "1234567"
        case_id = "governed-growth"
        base = root / "data" / "boi" / "private" / employee_id
        knowledge = base / "notes" / "knowledge"
        knowledge.mkdir(parents=True)
        raw = base / "evidence" / case_id / "public-source.md"
        raw.parent.mkdir(parents=True)
        raw.write_text("Governed inference remains searchable when evidence is conflict-free.\n", encoding="utf-8")
        raw_sha = hashlib.sha256(raw.read_bytes()).hexdigest()

        source = knowledge / "source.md"
        source.write_text(
            f'''---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-knowledge-note
title: "Governed source"
description: "Public fixture source"
boi_id: boi:private:{employee_id}:source:governed
visibility: local-private
classification: internal
owner: "{employee_id}"
employee_id: "{employee_id}"
local_owner_ref: local-private:{employee_id}
local_only: true
promotion_status: local_only
archive_status: active
artifact_visibility: memory
lifecycle_state: memory
review_after: 2026-12-31
contains_sensitive: false
claim_status: observed
knowledge_role: comparison
case_id: {case_id}
evidence_id: governed-source
evidence_type: document
evidence_sha256: "{raw_sha}"
raw_path: "{raw.as_posix()}"
origin_ref: "https://example.test/governed-source"
source_refs:
  - type: local-file
    ref: "{raw.as_posix()}"
    sha256: "{raw_sha}"
    evidence_id: governed-source
generated_from:
  - type: local-file
    ref: "{raw.as_posix()}"
    sha256: "{raw_sha}"
    evidence_id: governed-source
---

# Governed source

Conflict-free evidence for governed inference.
''',
            encoding="utf-8",
        )
        current = knowledge / "current.md"
        current.write_text(
            f'''---
okf_version: "0.1"
boi_profile_version: "0.1-local"
type: boi/local-knowledge-note
title: "Reviewed Current"
description: "Question-scoped current baseline"
boi_id: boi:private:{employee_id}:current:governed
visibility: local-private
classification: internal
owner: "{employee_id}"
employee_id: "{employee_id}"
local_owner_ref: local-private:{employee_id}
local_only: true
promotion_status: local_only
archive_status: active
artifact_visibility: memory
lifecycle_state: protected
review_after: 2026-12-31
contains_sensitive: false
claim_status: decision
knowledge_role: decision-record
case_id: {case_id}
---

# Reviewed Current

The approved baseline remains unchanged until a human accepts a material change.
''',
            encoding="utf-8",
        )
        return employee_id, case_id, source, current

    def run_curation(
        self,
        root: Path,
        employee_id: str,
        case_id: str,
        source: Path,
        current: Path | None,
        *,
        title: str,
        claim: str,
        material_change: bool,
        conflict: bool,
        apply_local: bool = False,
        source_sha256: str | None = None,
        evidence_sha256: str | None = None,
        confidence: str = "medium",
        inference_support: str = "supported",
        contains_sensitive: bool = False,
        sharing_scope_change: bool = False,
    ) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        source_hash = source_sha256 or hashlib.sha256(source.read_bytes()).hexdigest()
        source_text = source.read_text(encoding="utf-8")
        declared_evidence_hash = evidence_sha256 or (
            source_text.split('evidence_sha256: "', 1)[1].split('"', 1)[0]
            if 'evidence_sha256: "' in source_text
            else "0" * 64
        )
        command = [
            sys.executable,
            str(REPO / "scripts" / "local_wiki.py"),
            "--root",
            str(root),
            "--employee-id",
            employee_id,
            "curate-knowledge",
            "--case-id",
            case_id,
            "--title",
            title,
            "--claim",
            claim,
            "--claim-status",
            "inferred",
            "--source-path",
            source.relative_to(root).as_posix(),
            "--source-sha256",
            source_hash,
            "--evidence-sha256",
            declared_evidence_hash,
            "--confidence",
            confidence,
            "--inference-support",
            inference_support,
        ]
        if current is not None:
            command.extend(["--current-path", current.relative_to(root).as_posix()])
        if material_change:
            command.append("--material-change")
        if conflict:
            command.append("--conflict")
        if contains_sensitive:
            command.append("--contains-sensitive")
        if sharing_scope_change:
            command.append("--sharing-scope-change")
        if apply_local:
            command.append("--apply-local")
        else:
            command.append("--preview")
        result = subprocess.run(command, check=False, capture_output=True, text=True)
        payload = json.loads(result.stdout) if result.stdout.strip() else {"ok": False, "error": result.stderr}
        return result, payload

    def test_curation_auto_manages_conflict_free_inferred_without_touching_current(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            employee_id, case_id, source, current = self.make_profile_fixture(root)
            current_before = current.read_bytes()
            current_sha = hashlib.sha256(current_before).hexdigest()

            preview_process, preview = self.run_curation(
                root,
                employee_id,
                case_id,
                source,
                current,
                title="Conflict-free inferred knowledge",
                claim="Governed inference is immediately searchable without document review.",
                material_change=False,
                conflict=False,
            )
            self.assertEqual(0, preview_process.returncode, preview_process.stdout + preview_process.stderr)
            self.assertTrue(preview["preview"])
            self.assertEqual("auto-managed", preview["proposed_status"])
            self.assertFalse((root / preview["path"]).exists())

            process, result = self.run_curation(
                root,
                employee_id,
                case_id,
                source,
                current,
                title="Conflict-free inferred knowledge",
                claim="Governed inference is immediately searchable without document review.",
                material_change=False,
                conflict=False,
                apply_local=True,
            )
            self.assertEqual(0, process.returncode, process.stdout + process.stderr)

            self.assertEqual("auto-managed", result["status"])
            self.assertFalse(result["review_created"])
            self.assertEqual(current_before, current.read_bytes())
            self.assertEqual(current_sha, hashlib.sha256(current.read_bytes()).hexdigest())
            self.assertFalse((root / "data" / "boi" / "private" / employee_id / "notes" / "review").exists())
            query = subprocess.run(
                [
                    sys.executable,
                    str(REPO / "scripts" / "local_wiki.py"),
                    "--root",
                    str(root),
                    "--employee-id",
                    employee_id,
                    "query-pack",
                    "--question",
                    "Which governed inference is immediately searchable?",
                    "--case-id",
                    case_id,
                    "--limit",
                    "8",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, query.returncode, query.stdout + query.stderr)
            pack = json.loads(query.stdout)
            self.assertIn(result["path"], {item["path"] for item in pack["compiled_sources"]})

    def test_curation_rejects_convenience_only_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            employee_id, case_id, source, current = self.make_profile_fixture(root)
            raw = root / "data" / "boi" / "private" / employee_id / "evidence" / case_id / "public-source.md"
            source_text = source.read_text(encoding="utf-8")
            structured = f'''source_refs:
  - type: local-file
    ref: "{raw.as_posix()}"
    sha256: "{hashlib.sha256(raw.read_bytes()).hexdigest()}"
    evidence_id: governed-source
generated_from:
  - type: local-file
    ref: "{raw.as_posix()}"
    sha256: "{hashlib.sha256(raw.read_bytes()).hexdigest()}"
    evidence_id: governed-source
'''
            source.write_text(source_text.replace(structured, "source_refs: []\ngenerated_from: []\n"), encoding="utf-8")

            process, result = self.run_curation(
                root,
                employee_id,
                case_id,
                source,
                current,
                title="Convenience-only provenance",
                claim="Convenience fields alone must not establish source lineage.",
                material_change=False,
                conflict=False,
                apply_local=True,
            )

            self.assertEqual(2, process.returncode)
            self.assertFalse(result["ok"])
            self.assertIn("structured provenance", result["error"])

    def test_curation_duplicate_source_is_no_change_even_when_title_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            employee_id, case_id, source, current = self.make_profile_fixture(root)
            first_process, first = self.run_curation(
                root,
                employee_id,
                case_id,
                source,
                current,
                title="Original title",
                claim="The first source-derived inference is searchable.",
                material_change=False,
                conflict=False,
                apply_local=True,
            )
            self.assertEqual(0, first_process.returncode, first_process.stdout + first_process.stderr)
            before = {
                path.relative_to(root).as_posix(): path.read_bytes()
                for path in sorted((root / "data" / "boi" / "private" / employee_id).rglob("*"))
                if path.is_file()
            }

            for title in ("Original title", "Different title cannot bypass identity"):
                with self.subTest(title=title):
                    process, result = self.run_curation(
                        root,
                        employee_id,
                        case_id,
                        source,
                        current,
                        title=title,
                        claim="The repeated evidence must not create another Local note.",
                        material_change=False,
                        conflict=False,
                        apply_local=True,
                    )
                    self.assertEqual(0, process.returncode, process.stdout + process.stderr)
                    self.assertEqual("no-change", result["status"])
                    self.assertEqual(first["path"], result["path"])
                    self.assertFalse(result["review_created"])

            after = {
                path.relative_to(root).as_posix(): path.read_bytes()
                for path in sorted((root / "data" / "boi" / "private" / employee_id).rglob("*"))
                if path.is_file()
            }
            self.assertEqual(before, after)

    def test_curation_review_gates_preserve_current_and_remote_boundary(self) -> None:
        gate_cases = (
            ("low confidence", {"confidence": "low"}, "low-confidence"),
            ("unsupported inference", {"inference_support": "unsupported"}, "unsupported-inference"),
            ("sensitive content", {"contains_sensitive": True}, "sensitive-content"),
            ("sharing scope", {"sharing_scope_change": True}, "sharing-scope-change"),
            ("material Current change", {"material_change": True}, "material-change"),
            ("conflict", {"conflict": True}, "conflict"),
        )
        for label, overrides, reason in gate_cases:
            with self.subTest(gate=label), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                employee_id, case_id, source, current = self.make_profile_fixture(root)
                current_before = current.read_bytes()
                gate_kwargs = {
                    "material_change": False,
                    "conflict": False,
                    "apply_local": True,
                }
                gate_kwargs.update(overrides)
                process, result = self.run_curation(
                    root,
                    employee_id,
                    case_id,
                    source,
                    current,
                    title=f"{label} candidate",
                    claim="A governed gate must create only a Local Review candidate.",
                    **gate_kwargs,
                )

                self.assertEqual(0, process.returncode, process.stdout + process.stderr)
                self.assertEqual("review-required", result["status"])
                self.assertTrue(result["review_created"])
                self.assertIn(reason, result["review_reasons"])
                self.assertTrue((root / result["path"]).is_file())
                self.assertEqual(current_before, current.read_bytes())
                self.assertTrue(result["local_only"])
                self.assertFalse(result["remote_submitted"])

    def test_curation_routes_material_contradiction_to_review_without_touching_current(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            employee_id, case_id, source, current = self.make_profile_fixture(root)
            current_before = current.read_bytes()
            current_sha = hashlib.sha256(current_before).hexdigest()

            process, result = self.run_curation(
                root,
                employee_id,
                case_id,
                source,
                current,
                title="Material contradiction candidate",
                claim="New evidence contradicts the reviewed Current baseline.",
                material_change=True,
                conflict=True,
                apply_local=True,
            )
            self.assertEqual(0, process.returncode, process.stdout + process.stderr)

            self.assertEqual("review-required", result["status"])
            self.assertTrue(result["review_created"])
            self.assertTrue((root / result["path"]).is_file())
            self.assertEqual(current_before, current.read_bytes())
            self.assertEqual(current_sha, hashlib.sha256(current.read_bytes()).hexdigest())

    def test_curation_moves_one_identity_between_searchable_knowledge_and_review_without_stale_links(self) -> None:
        """A missing cross-state transition would leave both old knowledge and Review active."""
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            employee_id, case_id, source, current = self.make_profile_fixture(root)
            base = root / "data" / "boi" / "private" / employee_id
            current_before = current.read_bytes()
            title = "Omega transition identity"

            def curate(*, conflict: bool) -> dict[str, object]:
                process, payload = self.run_curation(
                    root,
                    employee_id,
                    case_id,
                    source,
                    current,
                    title=title,
                    claim="omega-transition-claim belongs to exactly one active curation state.",
                    material_change=conflict,
                    conflict=conflict,
                    apply_local=True,
                )
                self.assertEqual(0, process.returncode, process.stdout + process.stderr)
                return payload

            def active_curations() -> list[Path]:
                paths = []
                for directory in (base / "notes" / "knowledge", base / "notes" / "review"):
                    for path in sorted(directory.glob("*.md")) if directory.is_dir() else []:
                        text = path.read_text(encoding="utf-8")
                        if "curation_status:" in text and re.search(
                            rf'(?m)^case_id:\s*["\']?{re.escape(case_id)}["\']?\s*$', text
                        ):
                            paths.append(path)
                return paths

            def query_paths() -> set[str]:
                query = subprocess.run(
                    [
                        sys.executable,
                        str(REPO / "scripts" / "local_wiki.py"),
                        "--root",
                        str(root),
                        "--employee-id",
                        employee_id,
                        "query-pack",
                        "--question",
                        "Where is omega-transition-claim active?",
                        "--case-id",
                        case_id,
                        "--limit",
                        "8",
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(0, query.returncode, query.stdout + query.stderr)
                return {str(item["path"]) for item in json.loads(query.stdout)["compiled_sources"]}

            supported = curate(conflict=False)
            supported_path = root / str(supported["path"])
            supported_text = supported_path.read_text(encoding="utf-8")
            supported_frontmatter = supported_text.split("---", 2)[1]
            self.assertEqual([supported_path], active_curations())
            self.assertIn(str(supported["path"]), query_paths())

            review = curate(conflict=True)
            review_path = root / str(review["path"])
            self.assertEqual([review_path], active_curations())
            self.assertFalse(supported_path.exists())
            self.assertNotIn(str(review["path"]), query_paths())
            archived_supported = [
                path for path in (base / "_archive").rglob(supported_path.name) if path.is_file()
            ]
            self.assertEqual(1, len(archived_supported))
            archived_text = archived_supported[0].read_text(encoding="utf-8")
            self.assertEqual(supported_frontmatter, archived_text.split("---", 2)[1])
            archived_links = re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", archived_text)
            self.assertEqual(2, len(archived_links))
            self.assertEqual(
                {source.resolve(), current.resolve()},
                {(archived_supported[0].parent / link).resolve() for link in archived_links},
            )
            self.assertTrue(all((archived_supported[0].parent / link).resolve().is_file() for link in archived_links))
            knowledge_index = (base / "notes" / "knowledge" / "index.md").read_text(encoding="utf-8")
            review_index = (base / "notes" / "review" / "index.md").read_text(encoding="utf-8")
            self.assertNotIn(supported_path.name, knowledge_index)
            self.assertIn(review_path.name, review_index)

            restored = curate(conflict=False)
            restored_path = root / str(restored["path"])
            self.assertEqual([restored_path], active_curations())
            self.assertFalse(review_path.exists())
            self.assertIn(str(restored["path"]), query_paths())
            self.assertNotIn(review_path.name, (base / "notes" / "review" / "index.md").read_text(encoding="utf-8"))
            self.assertIn(restored_path.name, (base / "notes" / "knowledge" / "index.md").read_text(encoding="utf-8"))
            self.assertEqual(current_before, current.read_bytes())

            unchanged_before = {
                path.relative_to(root).as_posix(): path.read_bytes()
                for path in sorted(base.rglob("*"))
                if path.is_file()
            }
            no_change = curate(conflict=False)
            unchanged_after = {
                path.relative_to(root).as_posix(): path.read_bytes()
                for path in sorted(base.rglob("*"))
                if path.is_file()
            }
            self.assertEqual("no-change", no_change["status"])
            self.assertEqual(unchanged_before, unchanged_after)

            log = (root / "data" / "boi" / "log.md").read_text(encoding="utf-8")
            self.assertEqual(3, log.count("Local knowledge curation:"))
            self.assertIn("archive", log.casefold())

    def test_curation_target_identity_collision_fails_before_any_transition_mutation(self) -> None:
        """Archiving before target ownership validation would corrupt the still-active identity."""
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            employee_id, case_id, first_source, current = self.make_profile_fixture(root)
            base = root / "data" / "boi" / "private" / employee_id
            first_raw = Path(
                first_source.read_text(encoding="utf-8").split('raw_path: "', 1)[1].split('"', 1)[0]
            )
            first_raw_sha = hashlib.sha256(first_raw.read_bytes()).hexdigest()
            second_raw = first_raw.with_name("different-public-source.md")
            second_raw.write_text("A different evidence identity owns the same display slug.\n", encoding="utf-8")
            second_raw_sha = hashlib.sha256(second_raw.read_bytes()).hexdigest()
            second_source = first_source.with_name("different-source.md")
            second_source.write_text(
                first_source.read_text(encoding="utf-8")
                .replace('title: "Governed source"', 'title: "Different governed source"')
                .replace("boi:private:1234567:source:governed", "boi:private:1234567:source:different")
                .replace("evidence_id: governed-source", "evidence_id: different-governed-source")
                .replace(first_raw.as_posix(), second_raw.as_posix())
                .replace(first_raw_sha, second_raw_sha)
                .replace(
                    "Conflict-free evidence for governed inference.",
                    "Different evidence for a separate curation identity.",
                ),
                encoding="utf-8",
            )

            first_review_process, first_review = self.run_curation(
                root,
                employee_id,
                case_id,
                first_source,
                current,
                title="Shared collision slug",
                claim="The first identity already owns the Review destination.",
                material_change=True,
                conflict=True,
                apply_local=True,
            )
            self.assertEqual(0, first_review_process.returncode, first_review_process.stdout + first_review_process.stderr)
            second_supported_process, second_supported = self.run_curation(
                root,
                employee_id,
                case_id,
                second_source,
                current,
                title="Shared collision slug",
                claim="The second identity is active knowledge before its attempted transition.",
                material_change=False,
                conflict=False,
                apply_local=True,
            )
            self.assertEqual(
                0,
                second_supported_process.returncode,
                second_supported_process.stdout + second_supported_process.stderr,
            )
            self.assertTrue((root / str(first_review["path"])).is_file())
            self.assertTrue((root / str(second_supported["path"])).is_file())

            def exact_state() -> tuple[set[str], dict[str, bytes]]:
                directories = {
                    path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_dir()
                }
                files = {
                    path.relative_to(root).as_posix(): path.read_bytes()
                    for path in sorted(root.rglob("*"))
                    if path.is_file()
                }
                return directories, files

            before = exact_state()
            transition_process, transition = self.run_curation(
                root,
                employee_id,
                case_id,
                second_source,
                current,
                title="Shared collision slug",
                claim="The second identity must not displace the first Review identity.",
                material_change=True,
                conflict=True,
                apply_local=True,
            )
            after = exact_state()

            self.assertEqual(2, transition_process.returncode)
            self.assertFalse(transition["ok"])
            self.assertEqual(before, after)
            self.assertIn("different curation identity", str(transition["error"]))
            self.assertTrue((root / str(first_review["path"])).is_file())
            self.assertTrue((root / str(second_supported["path"])).is_file())
            self.assertEqual(0, len(list((base / "_archive").rglob("*.md"))) if (base / "_archive").exists() else 0)

    def test_curation_without_current_creates_local_synthesis_or_review_without_current_bindings(self) -> None:
        """Requiring Current would incorrectly block a valid Local-only Profile synthesis."""
        for label, conflict, expected_status in (
            ("supported", False, "auto-managed"),
            ("review", True, "review-required"),
        ):
            with self.subTest(state=label), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                employee_id, case_id, source, current = self.make_profile_fixture(root)
                current.unlink()
                process, result = self.run_curation(
                    root,
                    employee_id,
                    case_id,
                    source,
                    None,
                    title=f"No Current {label}",
                    claim="Local synthesis remains usable without inventing an approved Current.",
                    material_change=conflict,
                    conflict=conflict,
                    apply_local=True,
                )

                self.assertEqual(0, process.returncode, process.stdout + process.stderr)
                self.assertEqual(expected_status, result["status"])
                self.assertEqual("", result["current_path"])
                self.assertEqual("", result["current_sha256"])
                artifact = root / str(result["path"])
                text = artifact.read_text(encoding="utf-8")
                self.assertNotIn("current_baseline_path:", text)
                self.assertNotIn("current_baseline_sha256:", text)
                self.assertNotRegex(text, r"(?im)^- Current baseline:")
                self.assertIn("not an approved Current", text)
                self.assertFalse(result["remote_submitted"])

    def test_curation_rejects_stale_declared_source_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            employee_id, case_id, source, current = self.make_profile_fixture(root)
            current_before = current.read_bytes()

            process, result = self.run_curation(
                root,
                employee_id,
                case_id,
                source,
                current,
                title="Stale provenance candidate",
                claim="A stale source hash must not become auto-managed knowledge.",
                material_change=False,
                conflict=False,
                apply_local=True,
                source_sha256="0" * 64,
            )

            self.assertEqual(2, process.returncode)
            self.assertFalse(result["ok"])
            self.assertIn("source SHA256", result["error"])
            self.assertEqual(current_before, current.read_bytes())
            self.assertFalse((root / "data" / "boi" / "private" / employee_id / "notes" / "review").exists())

    def test_curation_rejects_stale_declared_evidence_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            employee_id, case_id, source, current = self.make_profile_fixture(root)
            current_before = current.read_bytes()

            process, result = self.run_curation(
                root,
                employee_id,
                case_id,
                source,
                current,
                title="Stale evidence provenance candidate",
                claim="A stale evidence hash must not become auto-managed knowledge.",
                material_change=False,
                conflict=False,
                apply_local=True,
                evidence_sha256="f" * 64,
            )

            self.assertEqual(2, process.returncode)
            self.assertFalse(result["ok"])
            self.assertIn("evidence SHA256", result["error"])
            self.assertEqual(current_before, current.read_bytes())

    def test_curation_rejects_source_path_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            employee_id, case_id, _, current = self.make_profile_fixture(root)
            escaped = root / "escaped-source.md"
            escaped.write_text("outside Local Private profile", encoding="utf-8")
            current_before = current.read_bytes()

            process, result = self.run_curation(
                root,
                employee_id,
                case_id,
                escaped,
                current,
                title="Escaped provenance candidate",
                claim="An escaped source path must not become auto-managed knowledge.",
                material_change=False,
                conflict=False,
                apply_local=True,
            )

            self.assertEqual(2, process.returncode)
            self.assertFalse(result["ok"])
            self.assertIn("Local Private profile", result["error"])
            self.assertEqual(current_before, current.read_bytes())

    def test_public_golden_journey_keeps_auto_curated_knowledge_searchable_and_current_protected(self) -> None:
        golden_journey = (REPO / "cases" / "GOLDEN-JOURNEYS.md").read_text(encoding="utf-8")

        for required in (
            "source integrity",
            "Local auto-managed knowledge",
            "question-scoped Current",
            "Review candidates",
            "Team/Public promotion",
            "33 auto-curated sources",
            "not document-level Review items",
            "inferred does not mean pending",
            "never overwrites Current before human approval",
        ):
            self.assertIn(required, golden_journey)

    def test_changed_public_case_markdown_links_resolve_from_clean_head(self) -> None:
        """A link that resolves only to an untracked private artifact is broken in a public clone."""
        base = "901b8823a2e4d9d55635f95e3309e87f60a50174"
        changed = subprocess.run(
            ["git", "diff", "--name-only", f"{base}..HEAD", "--", "cases/*.md", "cases/**/*.md"],
            cwd=REPO,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        public_pages = [path for path in changed if path.endswith(".md")]
        self.assertIn("cases/GOLDEN-JOURNEYS.md", public_pages)

        broken: list[str] = []
        for relative in public_pages:
            shown = (REPO / relative).read_text(encoding="utf-8")
            for target in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", shown):
                clean_target = target.strip().strip("<>").split("#", 1)[0]
                if not clean_target or re.match(r"^[a-z][a-z0-9+.-]*:", clean_target, re.IGNORECASE):
                    continue
                resolved = (Path(relative).parent / clean_target).as_posix()
                normalized: list[str] = []
                for part in Path(resolved).parts:
                    if part == "..":
                        if normalized:
                            normalized.pop()
                    elif part not in {"", "."}:
                        normalized.append(part)
                target_path = "/".join(normalized)
                exists = subprocess.run(
                    ["git", "cat-file", "-e", f"HEAD:{target_path}"],
                    cwd=REPO,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                if exists.returncode != 0:
                    broken.append(f"{relative} -> {clean_target}")

        self.assertEqual([], broken)

    def test_auto_curate_keeps_33_supported_sources_out_of_document_review(self) -> None:
        powershell = shutil.which("powershell.exe") or shutil.which("powershell")
        if not powershell:
            self.skipTest("Windows PowerShell is not available")

        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "public-sources"
            source.mkdir()
            for index in range(33):
                (source / f"source-{index:02d}.md").write_text(
                    f"# Public source {index}\n\nUnique public evidence {index}.\n",
                    encoding="utf-8",
                )

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
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            inventory = json.loads(result.stdout)

        self.assertEqual("ready-for-agent-processing", inventory["status"])
        self.assertEqual(33, inventory["unique_source_count"])
        self.assertEqual(33, len(inventory["items"]))
        self.assertTrue(all(not item["review_required"] for item in inventory["items"]))

    def test_public_review_candidates_preserve_current_and_promotion_boundaries(self) -> None:
        for relative in (
            "cases/strategy/fab-logistics-digital-twin/knowledge-growth/2026-08-08-01",
            "cases/strategy/scientific-foundation-model-knowledge/knowledge-growth/2026-08-08-01",
        ):
            run = REPO / relative
            status = json.loads((run / "run-status.json").read_text(encoding="utf-8"))
            reviewer = json.loads((run / "reviewer-report.json").read_text(encoding="utf-8"))
            handoff = json.loads((run / "handoff.json").read_text(encoding="utf-8"))

            self.assertEqual("awaiting-human-review", status["status"])
            self.assertFalse(status["current_snapshot_changed"])
            self.assertTrue(reviewer["human_review_required"])
            self.assertFalse(reviewer["current_snapshot_changed"])
            self.assertFalse(reviewer["self_approval"])
            self.assertEqual("not-requested", status["promotion_status"])
            self.assertEqual("none", handoff["remote_effect"])


if __name__ == "__main__":
    unittest.main()
