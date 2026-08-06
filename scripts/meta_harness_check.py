#!/usr/bin/env python3
"""Validate the BoI Meta Factory and example-collection boundary.

This is an administrator/CI oracle. It is not required for ordinary employee use.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


REFERENCE_FILES = (
    "factory-workflow.md",
    "architecture-selection.md",
    "case-contract.md",
    "quality-gates.md",
    "trigger-evolution.md",
    "harness-design-template.md",
)

TEMPLATE_LITERALS = (
    "## 1. 사용자 요청과 결과 (User request and outcome)",
    "## 2. 감사와 변경 미리보기 (Audit and change preview)",
    "Capture → Distill → Query → Lint → Review",
    "## 5. 역할과 독립 검토 (Roles and independent review)",
    "## 6. 의존 DAG와 인계 (Dependency DAG and handoffs)",
    "## 7. 실행 규모 (Scale modes)",
    "## 8. 산출물 계약 (Artifact contracts)",
    "## 10. OKF, BoI와 Local/Remote 경계 (OKF, BoI, and Local/Remote boundary)",
    "OKF 0.1 + BoI Profile 0.1-local",
    "## 11. 비개발자 사용 순서 (Non-developer walkthrough)",
    "## 12. 검증과 상태 (Validation and status)",
    "## 13. 개선 이력 (Evolution record)",
    "Previous Harness version:",
    "Approved change preview:",
    "Change reason and user approval:",
)

SKILL_LITERALS = (
    "Meta Harness Core",
    "`cases/` directory is the example collection it produces",
    "Factory lifecycle (Phase 0–7)",
    "Phase 0 — Audit",
    "Phase 7 — Evolve",
    "Capture → Distill → Query → Lint → Review",
    "Reuse existing generic Skills",
    "Existing Skill routing",
    "smallest owner set",
    "notes/harnesses/<slug>.md",
    "copyable next-session request",
    "configured card itself is directly non-promotable",
    "boi-action-author",
    "boi-context-pack-builder",
    "boi-dictionary-author",
    "boi-event-workflow-planner",
    "boi-langflow-connector-planner",
    "boi-sop-flow-visualizer",
    "boi-workflow-simulator",
    "three independent Cases",
    "**Full:**",
    "**Reduced:**",
    "**Single-agent:**",
    "**No-team fallback:**",
    "Flagship Second Brain",
    "OKF 0.1",
    "BoI Profile 0.1-local",
)

WIKI_LOCAL_CONTRACT_LITERALS = (
    'okf_version: "0.1"',
    'boi_profile_version: "0.1-local"',
    "structured `source_refs`",
    "structured `generated_from`",
    "source-registration wrapper",
    "directly non-promotable",
    "`ConfiguredHarness` tag",
    "exact candidate hash",
    "MCP read access never implies upload",
)

COMPOSED_BOI_SKILLS = (
    "boi-action-author",
    "boi-context-pack-builder",
    "boi-dictionary-author",
    "boi-event-workflow-planner",
    "boi-langflow-connector-planner",
    "boi-sop-flow-visualizer",
    "boi-workflow-simulator",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(root: Path) -> dict:
    root = root.resolve()
    errors: list[str] = []
    agent_root = root / ".agents" / "skills" / "boi-harness-builder"
    claude_root = root / ".claude" / "skills" / "boi-harness-builder"

    for runtime, skill_root in (("codex", agent_root), ("claude", claude_root)):
        skill_path = skill_root / "SKILL.md"
        if not skill_path.is_file():
            errors.append(f"{runtime}: missing boi-harness-builder/SKILL.md")
            continue
        text = skill_path.read_text(encoding="utf-8")
        for literal in SKILL_LITERALS:
            if literal not in text:
                errors.append(f"{runtime}: Meta Factory contract missing {literal}")
        for name in REFERENCE_FILES:
            if not (skill_root / "references" / name).is_file():
                errors.append(f"{runtime}: missing Meta Factory reference {name}")
        template_path = skill_root / "references" / "harness-design-template.md"
        if template_path.is_file():
            template = template_path.read_text(encoding="utf-8")
            for literal in TEMPLATE_LITERALS:
                if literal not in template:
                    errors.append(f"{runtime}: Harness design template missing {literal}")

    if agent_root.is_dir() and claude_root.is_dir():
        agent_files = sorted(path.relative_to(agent_root) for path in agent_root.rglob("*") if path.is_file())
        claude_files = sorted(path.relative_to(claude_root) for path in claude_root.rglob("*") if path.is_file())
        if agent_files != claude_files:
            errors.append("Codex and Claude Meta Factory file inventories differ")
        else:
            for relative in agent_files:
                if sha256(agent_root / relative) != sha256(claude_root / relative):
                    errors.append(f"Codex and Claude Meta Factory mirrors differ: {relative.as_posix()}")

    wiki_agent = root / ".agents" / "skills" / "boi-wiki-local" / "SKILL.md"
    wiki_claude = root / ".claude" / "skills" / "boi-wiki-local" / "SKILL.md"
    for runtime, path in (("codex", wiki_agent), ("claude", wiki_claude)):
        if not path.is_file():
            errors.append(f"{runtime}: missing shared boi-wiki-local Skill")
            continue
        text = path.read_text(encoding="utf-8")
        for literal in WIKI_LOCAL_CONTRACT_LITERALS:
            if literal not in text:
                errors.append(f"{runtime}: shared Local Profile contract missing {literal}")
    if wiki_agent.is_file() and wiki_claude.is_file() and sha256(wiki_agent) != sha256(wiki_claude):
        errors.append("Codex and Claude shared boi-wiki-local contracts differ")

    for skill_name in COMPOSED_BOI_SKILLS:
        agent_skill = root / ".agents" / "skills" / skill_name / "SKILL.md"
        claude_skill = root / ".claude" / "skills" / skill_name / "SKILL.md"
        for runtime, path in (("codex", agent_skill), ("claude", claude_skill)):
            if not path.is_file():
                errors.append(f"{runtime}: missing composed Skill {skill_name}")
                continue
            text = path.read_text(encoding="utf-8")
            for literal in (
                "Use `boi-wiki-local` as the parent contract",
                "OKF 0.1 + BoI Profile 0.1-local",
                "structured provenance",
                "Local Private promotion boundary",
            ):
                if literal not in text:
                    errors.append(f"{runtime}: {skill_name} does not inherit shared contract {literal}")
        if agent_skill.is_file() and claude_skill.is_file() and sha256(agent_skill) != sha256(claude_skill):
            errors.append(f"Codex and Claude composed Skill mirrors differ: {skill_name}")

    readme_path = root / "README.md"
    readme_ko_path = root / "README_KO.md"
    cases_readme_path = root / "cases" / "README.md"
    ledger_path = root / "research" / "meta-harness-source-ledger.md"
    for path in (readme_path, readme_ko_path, cases_readme_path, ledger_path):
        if not path.is_file():
            errors.append(f"missing architecture evidence: {path.relative_to(root).as_posix()}")

    if readme_path.is_file():
        readme = readme_path.read_text(encoding="utf-8")
        if "Production-grade 품질 목표의 Meta Harness Candidate" not in readme or "실사례 모음" not in readme:
            errors.append("README does not distinguish the Meta Harness Core from the Case collection")
        if "production-ready를 주장하지 않습니다" not in readme:
            errors.append("README must not overclaim production readiness before external gates")
        if "Flagship Reference Case" in readme:
            errors.append("README must not label a Community Case as Reference")
    if readme_ko_path.is_file():
        readme_ko = readme_ko_path.read_text(encoding="utf-8")
        if "Production-grade 품질 목표의 Meta Harness Candidate" not in readme_ko:
            errors.append("README_KO must present the current product as a candidate")
        if "Flagship Reference Case" in readme_ko:
            errors.append("README_KO must not label a Community Case as Reference")
    if cases_readme_path.is_file():
        cases_readme = cases_readme_path.read_text(encoding="utf-8")
        for literal in ("실사례 모음", "Meta Factory 자체", "revfactory/harness-100"):
            if literal not in cases_readme:
                errors.append(f"Case catalog boundary missing {literal}")
    if ledger_path.is_file():
        ledger = ledger_path.read_text(encoding="utf-8")
        for literal in (
            "cceac68ea1d0ad198ef4b7b906cd238375836387",
            "8e8d35c6a19166614d1af1df85512266d51121ae",
            "Meta Harness Factory",
            "실사례·산출물 예시 모음",
        ):
            if literal not in ledger:
                errors.append(f"source ledger missing audited distinction {literal}")

    second_brain = root / ".agents" / "skills" / "boi-second-brain" / "SKILL.md"
    if not second_brain.is_file():
        errors.append("Flagship Second Brain cross-cutting Harness is missing")
    for bootstrap_name in ("AGENTS.md", "CLAUDE.md"):
        bootstrap_path = root / bootstrap_name
        if not bootstrap_path.is_file():
            errors.append(f"missing runtime bootstrap: {bootstrap_name}")
            continue
        bootstrap_text = bootstrap_path.read_text(encoding="utf-8")
        normalized_bootstrap = " ".join(bootstrap_text.split())
        if "turn a recurring work description into a reusable" not in normalized_bootstrap:
            errors.append(f"{bootstrap_name}: natural-language Meta Harness routing is missing")
        if "ordinary one-off document authoring" not in normalized_bootstrap:
            errors.append(f"{bootstrap_name}: one-off authoring boundary is missing")
        if "notes/harnesses/" not in normalized_bootstrap:
            errors.append(f"{bootstrap_name}: configured Local Harness activation routing is missing")
    if (root / ".agents" / "skills" / "boi-yield-analysis").exists():
        errors.append("removed domain prototype must not be reintroduced as a global Skill")

    catalog_path = root / "cases" / "catalog.json"
    case_count = 0
    if not catalog_path.is_file():
        errors.append("Case example collection catalog is missing")
    else:
        try:
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            if catalog.get("catalog_scope") != "public-candidate":
                errors.append("Case catalog scope must be public-candidate")
            case_count = len(catalog.get("cases", []))
            flagship_entries = [
                entry
                for entry in catalog.get("cases", [])
                if entry.get("case_id") == "second-brain" and entry.get("flagship") is True
            ]
            if len(flagship_entries) != 1:
                errors.append("Case catalog must register the Flagship Second Brain exactly once")
            expected_global_insight = {
                "agentic-ai-change-radar",
                "fab-logistics-digital-twin",
                "scientific-foundation-model-knowledge",
            }
            catalog_ids = {str(entry.get("case_id")) for entry in catalog.get("cases", [])}
            missing_global_insight = sorted(expected_global_insight - catalog_ids)
            if missing_global_insight:
                errors.append(f"Global Insight Cases missing from catalog: {missing_global_insight}")
            for entry in catalog.get("cases", []):
                case_path = root / "cases" / str(entry.get("path", "")) / "case.yaml"
                if not case_path.is_file():
                    continue
                case = json.loads(case_path.read_text(encoding="utf-8"))
                if entry.get("case_id") == "second-brain":
                    continue
                if "boi-second-brain" in case.get("required_skills", []):
                    errors.append(f"{entry.get('case_id')}: Second Brain must not be a required Skill")
                if "boi-second-brain" not in case.get("optional_features", []):
                    errors.append(f"{entry.get('case_id')}: optional Second Brain integration is missing")
                if entry.get("case_id") in expected_global_insight:
                    if case.get("status") != "community" or case.get("fixture_policy") != "public-only":
                        errors.append(f"{entry.get('case_id')}: Global Insight Case must remain public-only Community")
                    manifest_path = case_path.parent / "fixtures" / "manifest.json"
                    if not manifest_path.is_file():
                        errors.append(f"{entry.get('case_id')}: public fixture manifest is missing")
                    else:
                        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                        if manifest.get("synthetic") is not False or manifest.get("fixture_policy") != "public-only":
                            errors.append(f"{entry.get('case_id')}: fixture public-only boundary is invalid")
        except json.JSONDecodeError:
            errors.append("Case example collection catalog is invalid JSON")

    global_contract = root / "templates" / "global-insight" / "README.md"
    if not global_contract.is_file():
        errors.append("Global Insight natural-language tool contract is missing")
    else:
        contract_text = global_contract.read_text(encoding="utf-8")
        for literal in (
            "| Capture | `capture` |",
            "| Update | `update` |",
            "| Query | `query` |",
            "| DeepResearch | `deep-research` |",
            "| Health | `health` |",
            "| Review | `review` |",
            "| Promote | `promote` |",
            "retirement-candidate",
            "No-team fallback",
        ):
            if literal not in contract_text:
                errors.append(f"Global Insight contract missing {literal}")

    golden_expected = root / "cases" / "research" / "agentic-ai-change-radar" / "expected" / "t1-change-set.md"
    if not golden_expected.is_file():
        errors.append("Agentic AI Golden Journey delta oracle is missing")
    else:
        delta_text = golden_expected.read_text(encoding="utf-8")
        for delta in ("new", "strengthened", "revised", "contradicted", "stale", "retirement-candidate", "unknown"):
            if f"| {delta} |" not in delta_text:
                errors.append(f"Agentic AI Golden Journey oracle missing {delta}")

    return {
        "schema": "boi-local-meta-harness-validation/v1",
        "ok": not errors,
        "meta_factory": "boi-harness-builder",
        "example_collection": "cases/",
        "flagship_cross_cutting_harness": "boi-second-brain",
        "case_count": case_count,
        "internal_bitbucket_verified": False,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    result = inspect(Path(args.root))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
