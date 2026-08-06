from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from pathlib import Path

import sys

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from boi_compatibility import builtin_validate, load_boi_wiki_okf, validate_with_boi_wiki


def projection(document_type: str = "boi/knowledge", visibility: str = "team") -> dict:
    metadata = {
        "okf_version": "0.1",
        "boi_profile_version": "0.1",
        "type": document_type,
        "title": "Canonical contract fixture",
        "description": "Non-sensitive synthetic fixture",
        "timestamp": "2026-08-01T00:00:00+09:00",
        "boi_id": "boi:pending:abcdef012345",
        "visibility": visibility,
        "classification": "internal" if visibility == "team" else "public",
        "owner": "authenticated-principal",
        "acl_policy": "remote-derived",
        "status": "draft",
        "source_refs": [{"type": "url", "ref": "https://example.com/source", "note": "synthetic"}],
        "review": {"reviewer": "knowledge-reviewer", "review_status": "pending"},
        "promotion_reason": "Contract test",
    }
    if visibility == "team":
        metadata["team_id"] = "platform"
    value = {
        "schema": "boi-wiki-promotion-projection/v1",
        "candidate": {"metadata": metadata, "body": "# Fixture\n\nValidated content.\n"},
        "submit_contract": {
            "principal": "authenticated-principal",
            "acl_resolution": "remote",
            "expected_revision": None,
            "expected_revision_status": "required_at_submit",
            "idempotency_key": "",
            "candidate_sha256": "",
            "harness_release": "harness-2.0-test",
            "harness_checksum": "c" * 64,
            "remote_submit_allowed": False,
            "user_confirmed": False,
        },
    }
    import hashlib

    candidate_sha = hashlib.sha256(
        json.dumps(value["candidate"], ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    value["submit_contract"]["candidate_sha256"] = candidate_sha
    value["submit_contract"]["idempotency_key"] = hashlib.sha256(
        f"{visibility}|{metadata.get('team_id', '')}|{candidate_sha}|{'c' * 64}".encode("utf-8")
    ).hexdigest()
    return value


class PromotionContractTests(unittest.TestCase):
    def test_supported_candidate_types_pass_builtin_contract(self) -> None:
        types = [
            "boi/knowledge",
            "boi/public-guide",
            "boi/sop",
            "boi/dictionary-term",
            "boi/event-specification",
            "boi/action-specification",
            "boi/context-pack",
            "boi/weekly-report",
        ]
        for document_type in types:
            with self.subTest(document_type=document_type):
                self.assertEqual([], builtin_validate(projection(document_type)))

    def test_unsafe_local_and_malformed_contracts_are_blocked(self) -> None:
        mutations = []

        item = projection()
        item["candidate"]["metadata"]["boi_profile_version"] = "0.1-local"
        mutations.append(item)
        item = projection()
        item["candidate"]["metadata"]["visibility"] = "local-private"
        mutations.append(item)
        item = projection()
        item["candidate"]["metadata"].pop("team_id")
        mutations.append(item)
        item = projection()
        item["candidate"]["metadata"]["review"] = {"review_status": "pending"}
        mutations.append(item)
        item = projection()
        item["candidate"]["metadata"]["source_refs"] = ["https://example.com"]
        mutations.append(item)
        item = projection()
        item["candidate"]["body"] = "C:\\Users\\someone\\private note"
        mutations.append(item)
        item = projection()
        item["candidate"]["metadata"]["owner"] = "7654321"
        mutations.append(item)
        item = projection()
        item["submit_contract"]["remote_submit_allowed"] = True
        mutations.append(item)
        item = projection()
        item["candidate"]["body"] += "Changed after approval\n"
        mutations.append(item)
        item = projection()
        item["submit_contract"]["idempotency_key"] = "d" * 64
        mutations.append(item)

        for index, unsafe in enumerate(mutations):
            with self.subTest(case=index):
                self.assertTrue(builtin_validate(unsafe))

    @unittest.skipUnless(os.getenv("BOI_WIKI_ROOT"), "set BOI_WIKI_ROOT for actual target contract test")
    def test_actual_boi_wiki_validator_and_markdown_media_contract(self) -> None:
        root = Path(os.environ["BOI_WIKI_ROOT"]).resolve()
        for document_type in (
            "boi/knowledge",
            "boi/public-guide",
            "boi/sop",
            "boi/dictionary-term",
            "boi/event-specification",
            "boi/action-specification",
            "boi/context-pack",
            "boi/weekly-report",
        ):
            self.assertEqual([], validate_with_boi_wiki(projection(document_type), root))

        module = load_boi_wiki_okf(root)
        approved = copy.deepcopy(projection()["candidate"]["metadata"])
        approved["status"] = "approved"
        self.assertIn("approved BoI requires review.reviewed_at", module.validate_boi_profile_metadata(approved, promotion=True))
        approved["review"]["reviewed_at"] = "2026-08-01T01:00:00+09:00"
        self.assertEqual([], module.validate_boi_profile_metadata(approved, promotion=True))

        with tempfile.TemporaryDirectory() as temp:
            boi_root = Path(temp)
            source = boi_root / "guide.md"
            media = boi_root / "_media" / "figure.png"
            media.parent.mkdir()
            media.write_bytes(b"synthetic-png-fixture")
            source.write_text("[Guide](other.md)\n![Figure](_media/figure.png)\n", encoding="utf-8")
            (boi_root / "other.md").write_text("# Other\n", encoding="utf-8")
            self.assertEqual([], module.lint_media_links(source, source.read_text(encoding="utf-8"), boi_root))
            edges = module.markdown_link_edges(source, source.read_text(encoding="utf-8"), boi_root)
            self.assertTrue(edges[0]["resolved"])


if __name__ == "__main__":
    unittest.main()
