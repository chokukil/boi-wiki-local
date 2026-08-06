#!/usr/bin/env python3
"""Build deterministic public-source records for Global Insight Cases.

This is a maintainer/CI builder. Runtime research is native and approval-bound;
ordinary users do not need Python. The fixture files are short verified-scope
records, not copies of the referenced publications.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


SCHEMA = "boi-local-case-fixture-manifest/v2"
FIXED_AT = "2026-08-06T09:00:00+09:00"


def record(*, title: str, url: str, published: str, snapshot: str, source_type: str, scope: str, summary: str, limitation: str) -> str:
    return f'''---
title: "{title}"
source_url: "{url}"
source_type: {source_type}
published_at: "{published}"
checked_at: "2026-08-06"
snapshot: {snapshot}
access_status: accessible
verification_level: primary-source-page
verified_scope: "{scope}"
---

# {title}

Verified summary: {summary}

Access limitation: {limitation}

This fixture preserves the checked scope and URL, not the copyrighted source body. Re-open the source before a live high-risk decision.
'''


CASE_FIXTURES: dict[str, dict] = {
    "cases/research/agentic-ai-change-radar": {
        "fixture_id": "PUB-AAI-RADAR-001-v1",
        "required_media": ["official-engineering", "official-product", "official-specification"],
        "files": {
            "01-t0-anthropic-effective-agents.md": (
                "T0 orchestration baseline",
                record(
                    title="Building effective agents",
                    url="https://www.anthropic.com/engineering/building-effective-agents",
                    published="2024-12-19",
                    snapshot="T0",
                    source_type="primary",
                    scope="Article title, publication date, workflow/agent distinction, simple composable pattern recommendation",
                    summary="Anthropic distinguishes predefined workflows from agents and reports that simple composable patterns often outperform unnecessary framework complexity.",
                    limitation="Official engineering guidance, not a universal benchmark or SK hynix deployment result.",
                ),
            ),
            "02-t0-openai-agent-building-blocks.md": (
                "T0 runtime, tools and evaluation baseline",
                record(
                    title="New tools for building agents",
                    url="https://openai.com/index/new-tools-for-building-agents/",
                    published="2025-03-11",
                    snapshot="T0",
                    source_type="primary",
                    scope="Responses API, built-in tools, Agents SDK, handoffs, guardrails, tracing and stated Node.js roadmap",
                    summary="OpenAI introduced Responses API, built-in web/file/computer tools and a Python Agents SDK with handoffs, guardrails and tracing; the article said Node.js support was coming later.",
                    limitation="Launch article; future roadmap statements require later verification.",
                ),
            ),
            "03-t0-mcp-authorization-2025-03.md": (
                "T0 tool security baseline",
                record(
                    title="MCP Authorization 2025-03-26",
                    url="https://modelcontextprotocol.io/specification/2025-03-26/basic/authorization",
                    published="2025-03-26",
                    snapshot="T0",
                    source_type="primary",
                    scope="HTTP authorization scope, OAuth requirements, authorization server discovery and base URL fallback",
                    summary="The March specification described optional HTTP authorization and an authorization-server discovery flow rooted in the MCP server base URL.",
                    limitation="Versioned specification; later revisions can replace normative details.",
                ),
            ),
            "04-t1-openai-agents-typescript.md": (
                "T1 runtime revision",
                record(
                    title="OpenAI Agents SDK TypeScript",
                    url="https://openai.github.io/openai-agents-js/",
                    published="unknown",
                    snapshot="T1",
                    source_type="primary",
                    scope="Current TypeScript SDK overview, installation, tools, handoffs, sessions, tracing and human-in-the-loop features",
                    summary="A supported TypeScript Agents SDK is now documented, making the T0 roadmap statement that Node.js support was still forthcoming stale.",
                    limitation="Living documentation; checked date is authoritative for this fixture, not an inferred first release date.",
                ),
            ),
            "05-t1-mcp-key-changes-2025-06.md": (
                "T1 security revision and contradiction",
                record(
                    title="MCP 2025-06-18 key changes",
                    url="https://modelcontextprotocol.io/specification/2025-06-18/changelog",
                    published="2025-06-18",
                    snapshot="T1",
                    source_type="primary",
                    scope="Protected resource metadata, resource indicators, structured tool output and authorization changes",
                    summary="The June revision classifies MCP servers as OAuth resource servers, adds protected resource metadata discovery and requires resource indicators, revising the T0 discovery model.",
                    limitation="The changelog summarizes changes; live implementation conformance remains unknown.",
                ),
            ),
            "06-t1-openai-agentkit.md": (
                "T1 orchestration and evaluation expansion",
                record(
                    title="Introducing AgentKit",
                    url="https://openai.com/index/introducing-agentkit/",
                    published="2025-10-06",
                    snapshot="T1",
                    source_type="primary",
                    scope="Agent Builder, Connector Registry, ChatKit, workflow versioning, datasets and trace grading",
                    summary="OpenAI expanded from SDK primitives to visual versioned workflows, centrally managed connectors and a broader evaluation toolchain, strengthening the T0 tracing/evaluation direction while adding new orchestration choices.",
                    limitation="Product announcement; comparative effectiveness and SK hynix fit are unknown.",
                ),
            ),
        },
    },
    "cases/strategy/fab-logistics-digital-twin": {
        "fixture_id": "PUB-FAB-DT-001-v1",
        "required_media": ["standards-overview", "ontology-doc", "digital-twin-doc", "fab-case"],
        "files": {
            "01-semi-gem300-overview.md": (
                "SEMI public standards overview",
                record(
                    title="GEM300 Tutorial Overview",
                    url="https://www.semi.org/en/standards-watch-2021Dec/gem300-tutorial-overview",
                    published="2021-12-02",
                    snapshot="baseline",
                    source_type="primary",
                    scope="Public descriptions of E40 Processing, E87 Carrier, E90 Substrate and E94 Control Job management",
                    summary="SEMI describes GEM300 as a group of standards for automated 300 mm equipment, including Processing, Carrier, Substrate Tracking and Control Job responsibilities.",
                    limitation="The paid normative standard texts were not accessed; field-level conformance claims are out of scope.",
                ),
            ),
            "02-palantir-ontology-overview.md": (
                "Ontology semantic and kinetic layers",
                record(
                    title="Palantir Ontology overview",
                    url="https://www.palantir.com/docs/foundry/ontology/overview",
                    published="unknown",
                    snapshot="baseline",
                    source_type="primary",
                    scope="Ontology semantic elements, actions/functions, governance and decision workflows",
                    summary="Palantir describes an operational layer that maps data to objects, properties and links and adds actions, functions and governance for operational decisions.",
                    limitation="Vendor documentation; no claim that Foundry is required or selected for SK hynix.",
                ),
            ),
            "03-palantir-types-reference.md": (
                "Object, link and action definitions",
                record(
                    title="Palantir object and link types reference",
                    url="https://www.palantir.com/docs/foundry/object-link-types/type-reference",
                    published="unknown",
                    snapshot="baseline",
                    source_type="primary",
                    scope="Definitions of object type, property, link type and action type",
                    summary="Object types model real entities or events, link types model relationships, and action types define governed changes and side effects.",
                    limitation="Conceptual mapping only; actual data model, ACL and actions require local validation.",
                ),
            ),
            "04-nvidia-warehouse-digital-twin.md": (
                "Logistics digital twin components",
                record(
                    title="Building Warehouse Digital Twins with NVIDIA Omniverse",
                    url="https://docs.omniverse.nvidia.com/digital-twins/latest/building-warehouse-digital-twins.html",
                    published="unknown",
                    snapshot="baseline",
                    source_type="primary",
                    scope="Data pipelines, visualization, physics simulation, autonomous systems and real-world connections",
                    summary="NVIDIA separates warehouse digital twins into data/visualization, physics simulation, autonomous system training and live operational connection components.",
                    limitation="Warehouse reference architecture is not evidence of semiconductor fab performance.",
                ),
            ),
            "05-nvidia-fab-digital-twin-session.md": (
                "Public semiconductor fab case signal",
                record(
                    title="Omniverse-Based Fab Digital Twin Platform for Semiconductor Industry",
                    url="https://www.nvidia.com/en-us/on-demand/session/gtc24-s62610/",
                    published="2024-03",
                    snapshot="baseline",
                    source_type="primary",
                    scope="Session description for fab architecture, infrastructure simulation and manufacturing planning",
                    summary="A public GTC session describes a semiconductor fab digital-twin effort focused on architecture, infrastructure simulation and manufacturing planning.",
                    limitation="Session description is a case signal, not independently verified benefit or SK hynix applicability.",
                ),
            ),
        },
    },
    "cases/strategy/scientific-foundation-model-knowledge": {
        "fixture_id": "PUB-SFM-001-v1",
        "required_media": ["peer-reviewed-paper", "primary-paper", "preprint", "research-page"],
        "files": {
            "01-materials-foundation-model-perspective.md": (
                "Field baseline and open gaps",
                record(
                    title="Foundation models for materials discovery — current state and future directions",
                    url="https://www.nature.com/articles/s41524-025-01538-0",
                    published="2025-03-06",
                    snapshot="baseline",
                    source_type="secondary",
                    scope="Open-access perspective abstract, field scope, data and benchmark limitations",
                    summary="The perspective surveys property prediction, synthesis planning and molecular generation and describes foundation-scale materials modeling as nascent with dataset and benchmark gaps.",
                    limitation="Perspective evidence is field synthesis, not direct validation of a particular model.",
                ),
            ),
            "02-mattergen-primary-paper.md": (
                "Generative materials claim and physical validation",
                record(
                    title="A generative model for inorganic materials design",
                    url="https://www.nature.com/articles/s41586-025-08628-5",
                    published="2025",
                    snapshot="baseline",
                    source_type="primary",
                    scope="Peer-reviewed abstract, stated benchmarks, one synthesized candidate and measured target deviation",
                    summary="MatterGen generates conditioned inorganic crystal candidates; the paper reports benchmark improvements and a proof-of-concept synthesis whose measured property was within 20 percent of target.",
                    limitation="One proof-of-concept does not establish universal physical correctness or fab readiness.",
                ),
            ),
            "03-graphcast-primary-publication.md": (
                "Scientific prediction benchmark",
                record(
                    title="GraphCast: Learned Global Weather Forecasting",
                    url="https://deepmind.google/research/publications/22598/",
                    published="2023-11-14",
                    snapshot="baseline",
                    source_type="primary",
                    scope="Publication abstract, forecast grid, variables, lead time, benchmark and runtime claims",
                    summary="GraphCast is a learned weather simulator evaluated against operational numerical forecasting across thousands of targets, demonstrating a strong empirical prediction case without proving explicit law satisfaction.",
                    limitation="Weather forecasting evidence cannot be generalized to chemistry or semiconductor processes without new validation.",
                ),
            ),
            "04-physics-guided-foundation-model.md": (
                "Explicit conservation-guided approach",
                record(
                    title="Physics-Guided Foundation Model for Scientific Discovery",
                    url="https://arxiv.org/abs/2502.06084",
                    published="2025-02-10",
                    snapshot="baseline",
                    source_type="primary",
                    scope="Preprint abstract, coupled lake tasks, simulated pretraining and mass/energy consistency claim",
                    summary="The preprint combines learned and physics-based models for lake temperature and dissolved oxygen tasks while maintaining stated mass and energy consistency.",
                    limitation="Preprint and domain-specific evidence; peer-review and cross-domain generalization remain unknown.",
                ),
            ),
            "05-physics-foundation-model-preprint.md": (
                "Broad physics foundation claim",
                record(
                    title="Towards a Physics Foundation Model",
                    url="https://arxiv.org/abs/2509.13805",
                    published="2025-09-17",
                    snapshot="baseline",
                    source_type="primary",
                    scope="Preprint abstract, training scale, evaluated physics domains and zero-shot/rollout claims",
                    summary="GPhyT claims in-context governing-dynamics inference and transfer across several simulated physics domains, offering a broad foundation-model hypothesis that still requires independent reproduction.",
                    limitation="Preprint claims and simulation-only scope; no independent reproduction was verified in this fixture.",
                ),
            ),
        },
    },
}


DESCRIPTIONS = {
    "agentic-ai-change-radar": "T0와 T1을 비교해 new, strengthened, revised, contradicted, stale와 unknown을 재현한다.",
    "fab-logistics-digital-twin": "SEMI 공개 개념, 물류 twin 구성요소와 Object-Link-Action 연결을 가설 수준에서 검증한다.",
    "scientific-foundation-model-knowledge": "법칙 반영 방식, prediction evidence, 반례, 재현 상태와 장기 review cadence를 분리한다.",
}


def expected(case_id: str, case: dict) -> tuple[dict, str]:
    files = []
    rows = []
    for index, (name, (description, content)) in enumerate(sorted(case["files"].items()), 1):
        data = content.encode("utf-8")
        files.append({
            "path": f"sources/{name}",
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
            "synthetic": False,
            "source_record": True,
        })
        rows.append(f"| {index} | [{name}](sources/{name}) | {description} |")
    manifest = {
        "schema": SCHEMA,
        "case_id": case_id,
        "fixture_id": case["fixture_id"],
        "fixed_at": FIXED_AT,
        "synthetic": False,
        "fixture_policy": "public-only",
        "source_count": len(files),
        "required_media": case["required_media"],
        "files": files,
    }
    source_pack = f'''# Deterministic public source-record pack — {case_id}

Fixture ID: `{case["fixture_id"]}`

각 파일은 공개 1차 자료의 URL, 확인 범위, 접근 제한과 짧은 검증 요약을 고정합니다. 원문 전체를 복제하지 않으며 실제 적용 판단 전에는 원문을 다시 엽니다.

| # | source record | 검증 목적 |
|---:|---|---|
{chr(10).join(rows)}

## Case-specific method

{DESCRIPTIONS[case_id]}

유료 전문, 비공개 자료, SK하이닉스 내부 운영 조건은 포함하지 않습니다. 원문에 접근하지 못한 내용을 읽었다고 주장하지 않습니다.
'''
    return manifest, source_pack


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    repo = Path(args.root).resolve()
    errors: list[str] = []
    total_sources = 0
    for relative, case in CASE_FIXTURES.items():
        case_root = repo / relative
        case_id = case_root.name
        manifest, source_pack = expected(case_id, case)
        manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
        total_sources += len(case["files"])
        expected_files = {
            case_root / "fixtures" / "manifest.json": manifest_text.encode("utf-8"),
            case_root / "fixtures" / "source-pack.md": source_pack.encode("utf-8"),
            **{
                case_root / "fixtures" / "sources" / name: content.encode("utf-8")
                for name, (_, content) in case["files"].items()
            },
        }
        for path, payload in expected_files.items():
            if args.check:
                if not path.is_file() or path.read_bytes() != payload:
                    errors.append(f"{case_id}: fixture mismatch {path.relative_to(case_root).as_posix()}")
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
    result = {
        "schema": "boi-local-reference-fixture-build-result/v1",
        "ok": not errors,
        "case_count": len(CASE_FIXTURES),
        "source_count": total_sources,
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
