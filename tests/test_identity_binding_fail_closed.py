"""Fail-closed original identity binding contract for answer receipts.

Regression background: six generated answers shipped receipts whose
``evidence[].original_identity_binding`` was an empty object because
``answer-receipt`` accepted public-origin source evidence without any
declared binding (fail-open). Public-origin evidence in an answer receipt
must carry a complete, matching original identity binding:
``evidence_id`` + ``evidence_sha256`` + ``expected_origin_ref``.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import query_quality

EMPLOYEE_ID = "1234567"
ORIGIN_REF = "https://arxiv.org/abs/2005.11401"
ANSWER_REL = f"data/boi/private/{EMPLOYEE_ID}/reports/case/generated-answer.md"
BINDINGS_REL = f"data/boi/private/{EMPLOYEE_ID}/reports/case/claim-bindings.json"
RECEIPT_REL = f"data/boi/private/{EMPLOYEE_ID}/reports/case/generated-answer.receipt.json"


def build_fixture(root: Path) -> tuple[str, str]:
    """Public-origin source evidence + grounded answer + claim bindings. Returns (question, raw sha256)."""
    profile = root / "data" / "boi" / "private" / EMPLOYEE_ID
    knowledge = profile / "notes" / "knowledge"
    answer = profile / "reports" / "case" / "generated-answer.md"
    raw = root / "inbox" / "paper.md"
    bindings = profile / "reports" / "case" / "claim-bindings.json"
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
        f"""---
type: boi/local-knowledge-note
title: "RAG paper"
boi_id: boi:private:{EMPLOYEE_ID}:source:rag
claim_status: observed
evidence_id: rag-paper
evidence_type: document
evidence_sha256: "{raw_sha}"
raw_path: "{raw.as_posix()}"
origin_ref: "{ORIGIN_REF}"
---

RAG retrieves external evidence, while retrieval alone does not preserve reusable knowledge.
""",
        encoding="utf-8",
    )
    source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
    (knowledge / "topic.md").write_text(
        f"""---
type: boi/local-knowledge-note
title: "RAG and Wiki comparison"
boi_id: boi:private:{EMPLOYEE_ID}:topic:rag-wiki
knowledge_role: comparison
case_id: ib-case
claim_status: inferred
source_refs:
  - type: local-knowledge
    ref: "data/boi/private/{EMPLOYEE_ID}/notes/knowledge/paper-source.md"
    sha256: "{source_sha}"
---

RAG retrieves evidence for a question; a maintained Wiki preserves reusable knowledge.
""",
        encoding="utf-8",
    )
    answer.write_text(
        "RAG retrieves evidence for the current question, while a maintained Wiki preserves reusable knowledge. [1]\n\n"
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
    return "Compare ordinary RAG vs a maintained Wiki.", raw_sha


def run_receipt_cli(root: Path, question: str, extra_args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(REPO / "scripts" / "local_wiki.py"),
            "--root",
            str(root),
            "--employee-id",
            EMPLOYEE_ID,
            "answer-receipt",
            "--question",
            question,
            "--case-id",
            "ib-case",
            "--answer-file",
            ANSWER_REL,
            "--claim-bindings-file",
            BINDINGS_REL,
            *extra_args,
        ],
        cwd=REPO,
        text=True,
        capture_output=True,
    )


class ReceiptIdentityBindingFailClosedTests(unittest.TestCase):
    def test_receipt_rejects_empty_original_identity_binding_for_public_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            question, raw_sha = build_fixture(root)

            result = run_receipt_cli(root, question, [])

            self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["ok"])
            error = str(payload.get("error", ""))
            for element in ("evidence_id", "evidence_sha256", "expected_origin_ref"):
                self.assertIn(element, error)
            self.assertIn("rag-paper", error)
            self.assertFalse((root / RECEIPT_REL).exists(), "no receipt may be written for an unbound public citation")

    def test_receipt_accepts_complete_valid_binding(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            question, raw_sha = build_fixture(root)

            result = run_receipt_cli(root, question, ["--original-binding", f"rag-paper|{raw_sha}|{ORIGIN_REF}"])

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            receipt = json.loads((root / RECEIPT_REL).read_text(encoding="utf-8"))
            self.assertEqual(
                {
                    "evidence_id": "rag-paper",
                    "evidence_sha256": raw_sha,
                    "expected_origin_ref": ORIGIN_REF,
                },
                receipt["evidence"][0]["original_identity_binding"],
            )

    def test_receipt_rejects_binding_with_mismatched_evidence_sha(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            question, _ = build_fixture(root)

            result = run_receipt_cli(
                root,
                question,
                ["--original-binding", f"rag-paper|{'0' * 64}|{ORIGIN_REF}"],
            )

            self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("rag-paper", result.stdout + result.stderr)
            self.assertFalse((root / RECEIPT_REL).exists())

    def test_receipt_rejects_partial_binding_missing_expected_origin(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            question, raw_sha = build_fixture(root)

            result = run_receipt_cli(root, question, ["--original-binding", f"rag-paper|{raw_sha}|not-a-url"])

            self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("expected_origin_ref", result.stdout + result.stderr)
            self.assertFalse((root / RECEIPT_REL).exists())


class EvidenceBindingAxisFailClosedTests(unittest.TestCase):
    def test_evidence_axis_rejects_public_source_without_valid_identity_binding(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            raw = root / "inbox" / "paper.md"
            raw.parent.mkdir(parents=True)
            raw.write_text("RAG retrieves external evidence.\n", encoding="utf-8")
            raw_sha = hashlib.sha256(raw.read_bytes()).hexdigest()
            pack = {
                "citation_surface": {
                    "display_map": [{"display_id": "[1]", "evidence_id": "rag-paper", "title": "RAG paper"}]
                },
                "evidence_sources": [
                    {
                        "evidence_id": "rag-paper",
                        "path": "data/boi/private/1234567/notes/knowledge/paper-source.md",
                        "raw_path": raw.as_posix(),
                        "sha256": raw_sha,
                        "origin_ref": ORIGIN_REF,
                        "evidence_authority": "public-origin-candidate",
                        "original_identity_binding": {},
                        "origin_binding_valid": False,
                        "layer": "source-evidence",
                        "raw_integrity": "verified",
                    }
                ],
            }
            answer = {
                "ok": True,
                "path": f"data/boi/private/{EMPLOYEE_ID}/reports/case/generated-answer.md",
                "body": "RAG retrieves evidence for the question. [1]\n",
                "text": "RAG retrieves evidence for the question. [1]\n",
                "sha256": hashlib.sha256(b"RAG retrieves evidence for the question. [1]\n").hexdigest(),
            }
            item = {"minimum_citations": 1, "required_citation_ids": ["rag-paper"]}

            result = query_quality.evaluate_evidence_binding(root, pack, item, answer)

            self.assertFalse(result["ok"], result)
            failed = {row["name"] for row in result["checks"] if not row["ok"]}
            self.assertIn("citations_match_declared_original_identity", failed)


if __name__ == "__main__":
    unittest.main()
