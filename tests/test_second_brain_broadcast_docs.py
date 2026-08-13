"""Public-safety and Markdown-first checks for the broadcast package."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
import struct
import tempfile
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "templates" / "second-brain-guide"
WIKI_CHECK_PATH = ROOT / "scripts" / "wiki_check.py"
GUIDE_REVIEW_BOUNDARY = (
    "\ucda9\ub3cc \uc5c6\uc774 \uadfc\uac70\uac00 \ud655\uc778\ub41c \ubcf4\uac15\uc740 \uc790\ub3d9\uc73c\ub85c \ubc18\uc601\ud55c\ub2e4. "
    "\uc0ac\ub78c \uac80\ud1a0\ub294 \uc911\uc694\ud55c \ud310\ub2e8 \ubcc0\ud654, \ucda9\ub3cc, \ub0ae\uc740 \uc2e0\ub8b0\ub3c4, "
    "\uadfc\uac70\uac00 \ubd80\uc871\ud55c \ucd94\ub860, \ubbfc\uac10 \uc815\ubcf4, \uacf5\uc720 \ubc94\uc704 \ubcc0\uacbd\uc5d0\uc11c \ud544\uc694\ud558\ub2e4. "
    "\uac19\uc740 \uc790\ub8cc\ub97c \ub2e4\uc2dc \ub123\uc73c\uba74 \uc0c8 \ubb38\uc11c\ub098 \uac80\ud1a0 \ud56d\ubaa9\uc744 \ub9cc\ub4e4\uc9c0 \uc54a\ub294\ub2e4."
)
REPLY_REVIEW_BOUNDARY = (
    "\ucda9\ub3cc \uc5c6\uc774 \uadfc\uac70\uac00 \ud655\uc778\ub41c \ubcf4\uac15\uc740 \uc790\ub3d9\uc73c\ub85c \ubc18\uc601\ub429\ub2c8\ub2e4. "
    "\uc0ac\ub78c \uac80\ud1a0\ub294 \uc911\uc694\ud55c \ud310\ub2e8 \ubcc0\ud654, \ucda9\ub3cc, \ub0ae\uc740 \uc2e0\ub8b0\ub3c4, "
    "\uadfc\uac70\uac00 \ubd80\uc871\ud55c \ucd94\ub860, \ubbfc\uac10 \uc815\ubcf4, \uacf5\uc720 \ubc94\uc704 \ubcc0\uacbd\uc5d0\uc11c \ud544\uc694\ud569\ub2c8\ub2e4. "
    "\uac19\uc740 \uc790\ub8cc\ub97c \ub2e4\uc2dc \ub123\uc73c\uba74 \uc0c8 \ubb38\uc11c\ub098 \uac80\ud1a0 \ud56d\ubaa9\uc744 \ub9cc\ub4e4\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4."
)
EXHAUSTIVE_REVIEW = re.compile(
    r"(?:\uc911\uc694\ud55c )?\ud310\ub2e8(?: \ubcc0\ud654)?[^.!?]{0,60}?\ub9cc\s*"
    r"(?:\uc0ac\ub78c(?:\uc774|\uc5d0\uac8c)?|\uac80\ud1a0)"
)


def load_wiki_check_module():
    spec = importlib.util.spec_from_file_location("task3_wiki_check", WIKI_CHECK_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def review_boundary_issues(text: str) -> list[str]:
    """Reject an exhaustive human-review claim that drops any Review trigger."""
    return [
        f"incomplete exhaustive human-review boundary: {match.group(0)}"
        for match in EXHAUSTIVE_REVIEW.finditer(text)
    ]


class SecondBrainBroadcastDocsTests(unittest.TestCase):
    def run_wiki_check(self, root: Path = ROOT) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python", str(WIKI_CHECK_PATH), "--root", str(root)],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
        )

    def copied_guide_root(self):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        guide = root / "templates" / "second-brain-guide"
        shutil.copytree(GUIDE, guide)
        return temp, root, guide

    def test_hub_has_four_mermaid_flows_and_adjacent_readable_fallbacks(self) -> None:
        hub_path = GUIDE / "54-broadcast-hub.md"
        self.assertTrue(hub_path.is_file(), "broadcast hub must be Markdown-first")
        hub = hub_path.read_text(encoding="utf-8")

        self.assertEqual(4, hub.count("```mermaid"))
        for fallback in (
            "아래 흐름의 요지는",
            "이 흐름은 방송용 예시가 아니라",
            "개인 논문·메모·업무 문서는",
            "다음은 공개 연구 시스템과 구분된",
        ):
            self.assertIn(fallback, hub)

        for required in (
            "새 원문",
            "AI source knowledge",
            "Local auto-managed",
            "근거 있는 답변",
            "변경 후보",
            "공개 연구 아티팩트 33개",
            "PDF 25 + 공개 텍스트 2 + GitHub 스냅샷 6",
            "원문 지식 33개",
            "주제 지식 8개",
            "대표 질문 + 보조 질문 5개",
            "개인 Local 논문·메모·업무 문서",
            "민감성·근거·범위 검사",
            "SOP Task",
            "판단 질문·필요 근거·완료 조건",
            "Manual / Copilot / Autopilot",
        ):
            self.assertIn(required, hub)

    def test_images_are_integrated_without_reencoding(self) -> None:
        expected = {
            "16-personal-to-organization-knowledge.png": ("fd9b0f55f7bc0a454a5f87a719ab17e9dd873515b7d00d316e008a18af70eea8", 1316685),
            "17-ai-native-workflow-knowledge-loop.png": ("a56a478415a50e44543d9d2954effb04d4205388fb74a94cfeca91723aebfa31", 1396298),
        }
        manifest = json.loads((GUIDE / "_media" / "manifest.json").read_text(encoding="utf-8"))
        items = {item["file"]: item for item in manifest["items"]}
        hub_path = GUIDE / "54-broadcast-hub.md"
        self.assertTrue(hub_path.is_file(), "broadcast hub must integrate both original images")
        hub = hub_path.read_text(encoding="utf-8")

        for name, (digest, byte_count) in expected.items():
            content = (GUIDE / "_media" / name).read_bytes()
            self.assertEqual(digest, hashlib.sha256(content).hexdigest())
            self.assertEqual(byte_count, len(content))
            self.assertEqual(b"\x89PNG\r\n\x1a\n", content[:8])
            self.assertEqual((1672, 941), struct.unpack(">II", content[16:24]))
            self.assertIn(name, hub)
            self.assertEqual(digest, items[name]["sha256"])
            self.assertEqual(byte_count, items[name]["bytes"])
            self.assertEqual(1672, items[name]["width"])
            self.assertEqual(941, items[name]["height"])

    def test_cue_sheet_has_exact_five_minute_order(self) -> None:
        cue_path = GUIDE / "55-five-minute-cue-sheet.md"
        self.assertTrue(cue_path.is_file(), "five-minute cue sheet must exist")
        cue = cue_path.read_text(encoding="utf-8")
        expected_order = (
            "0:00–0:35",
            "0:35–1:05",
            "1:05–2:00",
            "2:00–2:55",
            "2:55–3:35",
            "3:35–4:25",
            "4:25–4:45",
            "4:45–5:00",
        )
        positions = [cue.index(stamp) for stamp in expected_order]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("PoC는 완료", cue)
        self.assertIn("Pilot 운영을 준비", cue)
        self.assertIn("전사 확산", cue)

    def test_broadcast_docs_are_public_safe_and_distinguish_future_direction(self) -> None:
        files = [
            GUIDE / "54-broadcast-hub.md",
            GUIDE / "55-five-minute-cue-sheet.md",
            GUIDE / "56-expected-qa.md",
            GUIDE / "57-broadcaster-reply.md",
        ]
        self.assertTrue(all(path.is_file() for path in files), "all four broadcast documents must exist")
        combined = "\n".join(path.read_text(encoding="utf-8") for path in files)

        for forbidden in (
            "data/boi/private/2055186",
            ".obsidian/",
            "SOP 기반 AI Native Workflow_R5_Strategy_KO.pptx",
            "SHA256",
            "Manifest",
            "Query Pack",
            "WiCER",
        ):
            self.assertNotIn(forbidden, combined)
        self.assertIn("실제로 동작하는 공개 AI 연구 Second Brain", combined)
        self.assertIn("별도의 비식별 조직 적용 방향", combined)
        self.assertIn("공개 연구 Vault", combined)
        self.assertIn("유관부서와의 PoC는 완료", combined)

    def test_every_broadcast_doc_has_a_complete_non_exhaustive_review_boundary(self) -> None:
        expected_by_name = {
            "54-broadcast-hub.md": GUIDE_REVIEW_BOUNDARY,
            "55-five-minute-cue-sheet.md": GUIDE_REVIEW_BOUNDARY,
            "56-expected-qa.md": GUIDE_REVIEW_BOUNDARY,
            "57-broadcaster-reply.md": REPLY_REVIEW_BOUNDARY,
        }
        for name, boundary in expected_by_name.items():
            text = (GUIDE / name).read_text(encoding="utf-8")
            self.assertIn("\uc6d0\ubb38\uc5d0\uc11c \ud655\uc778\ud55c 33\uac1c\uc640 \uc5ec\ub7ec \uc6d0\ubb38\uc744 \uc5ee\uc5b4 \ucd94\ub860\ud55c \uc8fc\uc81c 8\uac1c", text)
            self.assertIn(boundary, text, f"{name} must state the complete review boundary")
            self.assertEqual([], review_boundary_issues(text), f"{name} contains a contradictory review boundary")

    def test_incomplete_only_material_change_claim_fails_even_with_supported_inference_rule_present(self) -> None:
        text = GUIDE_REVIEW_BOUNDARY + " \uc911\uc694\ud55c \ud310\ub2e8 \ubcc0\ud654\ub9cc \uc0ac\ub78c\uc774 \ud655\uc778\ud55c\ub2e4."
        issues = review_boundary_issues(text)
        self.assertEqual(1, len(issues))
        self.assertIn("incomplete exhaustive human-review boundary", issues[0])

    def test_declared_original_broadcast_pngs_pass_without_weakening_screenshot_policy(self) -> None:
        result = self.run_wiki_check()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

        temp, root, guide = self.copied_guide_root()
        try:
            manifest_path = guide / "_media" / "manifest.json"
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            item = next(value for value in payload["items"] if value["id"] == "infographic-16")
            item["asset_kind"] = "screenshot"
            manifest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            rejected = self.run_wiki_check(root)
            self.assertNotEqual(0, rejected.returncode, rejected.stdout + rejected.stderr)
            issues = "\n".join(error["issue"] for error in json.loads(rejected.stdout)["errors"])
            self.assertIn("not a WebP file", issues)
        finally:
            temp.cleanup()

    def test_public_broadcast_boundary_is_accepted_but_unknown_boundary_is_rejected(self) -> None:
        result = self.run_wiki_check()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

        temp, root, guide = self.copied_guide_root()
        try:
            hub_path = guide / "54-broadcast-hub.md"
            original = hub_path.read_text(encoding="utf-8")
            hub_path.write_text(
                original.replace(
                    'guide_boundary: "public-research-description-only"',
                    'guide_boundary: "unexpected-boundary"',
                ),
                encoding="utf-8",
            )
            rejected = self.run_wiki_check(root)
            self.assertNotEqual(0, rejected.returncode, rejected.stdout + rejected.stderr)
            issues = "\n".join(error["issue"] for error in json.loads(rejected.stdout)["errors"])
            self.assertIn("unsupported guide boundary: unexpected-boundary", issues)
        finally:
            temp.cleanup()

    def test_infographic_width_diagnostic_uses_its_own_limit(self) -> None:
        temp, _, guide = self.copied_guide_root()
        try:
            checker = load_wiki_check_module()
            checker.MAX_ORIGINAL_BROADCAST_INFOGRAPHIC_WIDTH = 1600
            errors: list[dict[str, str]] = []
            checker.check_media(
                guide,
                {
                    "_media/16-personal-to-organization-knowledge.png": [
                        ("54-broadcast-hub.md", "개인 Local 지식이 검토와 승인을 거쳐 조직 재사용 후보로 이어지는 Korean infographic")
                    ],
                    "_media/17-ai-native-workflow-knowledge-loop.png": [
                        ("54-broadcast-hub.md", "SOP/Event 판단과 기록이 다음 업무로 이어지는 Korean infographic"),
                        ("57-broadcaster-reply.md", "SOP/Event 판단과 기록이 다음 업무로 이어지는 Korean infographic"),
                    ],
                },
                errors,
            )
            issues = "\n".join(error["issue"] for error in errors)
            self.assertIn("image width exceeds 1600px", issues)
            self.assertNotIn("image width exceeds 1760px", issues)
        finally:
            temp.cleanup()


if __name__ == "__main__":
    unittest.main()
