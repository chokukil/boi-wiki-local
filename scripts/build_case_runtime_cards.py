#!/usr/bin/env python3
"""Build progressive-disclosure role cards and runtime dispatch contracts.

The generated files are plain Markdown/JSON consumed by Codex, Claude, or a
single-agent fallback. Python is maintainer/CI tooling, not an employee runtime
dependency.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_reference_case_docs import CASES


ROOT = Path(__file__).resolve().parents[1]

FLAGSHIP_PATH = "cases/flagship/second-brain"
FLAGSHIP_ROLES = [
    (
        "source-curator",
        "원본 bytes와 provenance를 보존한 deterministic source inventory를 만든다.",
        "지정 source subset과 fixture manifest",
        "intermediate/source-inventory.json",
        "모든 지정 source가 정확히 한 상태이며 before hash가 manifest와 일치한다.",
        "source 변경, 누락 source를 읽었다고 주장, 확장자만으로 도메인 의미 추론",
    ),
    (
        "memory-maintainer",
        "새 문서를 만들기 전에 기존 topic, history owner, processing checkpoint를 찾는다.",
        "seed vault, Local indexes, source inventory",
        "intermediate/knowledge-inventory.json",
        "source마다 기존 owner 또는 no-suitable-owner의 검색 근거가 있다.",
        "검색 없는 신규 생성, archive/history 삭제, 완료 source 재생성",
    ),
    (
        "knowledge-distiller",
        "evidence 복사본을 늘리지 않고 기존 지식을 보강·교정·검토 보류한다.",
        "source inventory, knowledge inventory, user prompt",
        "intermediate/consolidation-plan.json과 OKF Local pages",
        "모든 operation에 source hash와 reason이 있고 schema lint가 통과한다.",
        "raw transcript 저장, 충돌 자동 덮어쓰기, 누락 evidence 생성, blocked type promotion",
    ),
    (
        "grounded-query-analyst",
        "compiled Wiki에서 시작해 출처·반증·미확인·다음 확인을 포함한 답을 만든다.",
        "reviewed pages와 명시적 source_refs",
        "grounded-answer.md 또는 promotion input knowledge",
        "material claim citation coverage 100%이거나 근거 부족을 명시한다.",
        "모델 기억으로 빈칸 보충, remote/local citation 혼합, reviewer 없는 확정 표현",
    ),
    (
        "privacy-reviewer",
        "생성자와 독립적으로 source·history·projection·사용자 요약을 역추적한다.",
        "manifest, intermediate, Local outputs, answer/projection",
        "reviewer-report.json과 assertion evidence",
        "모든 assertion에 evidence locator가 있고 누락 evidence는 fail이다.",
        "자기 결과 승인, hard failure 점수 보정, projection leak 또는 remote mutation 묵인",
    ),
]


def encoded_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def card(case_id: str, role: tuple[str, str, str, str, str, str], reviewer: bool) -> bytes:
    name, purpose, inputs, output, exit_criteria, hard_fail = role
    reviewer_rules = (
        "- 생성자의 결론 요약을 먼저 읽지 않고 manifest → source → intermediate → final 순서로 확인한다.\n"
        "- 작성 runtime과 다른 reviewer/evaluator ID를 기록한다.\n"
        "- 누락 evidence는 fail이며 점수로 보정하지 않는다."
        if reviewer
        else
        "- 자신의 산출물을 최종 승인하지 않는다.\n- reviewer에게 결론 대신 source locator와 검증 질문을 전달한다."
    )
    return f'''---
name: {name}
description: "{purpose}"
case_id: {case_id}
runtime_contract: boi-local-case-runtime/v1
independent_reviewer: {str(reviewer).lower()}
---

# {name}

## 목적

{purpose}

## 허용 입력

- {inputs}
- 현재 run이 잠근 user prompt, fixture/seed manifest, 허용 source subset만 읽는다.
- Local Private source를 원격 도구에 보내지 않는다.

## 산출물 계약

- 주 산출물: `{output}`
- 모든 파일은 path·bytes·SHA256과 함께 handoff에 기록한다.
- Profile 문서라면 OKF 0.1 + BoI Profile 0.1-local을 사용한다.
- 사실, 추론, 반증, 미확인, 사람의 판정을 섞지 않는다.

## Handoff protocol

`boi-local-case-handoff/v1`으로 다음을 전달한다.

- input source ref와 exact SHA256
- output path·bytes·SHA256
- unknowns, blockers, 다음 역할의 review questions
- source manifest before/after SHA256와 changed source files 0건

경로: [공통 handoff schema](../../../_schema/handoff.schema.json)

## Exit criteria

{exit_criteria}

## Hard fail

{hard_fail}

## 독립성 규칙

{reviewer_rules}

## Scale behavior

- Full: 이 카드만 로드한 독립 specialist가 실행한다.
- Reduced: creator가 이 역할을 겸할 수 있지만 reviewer 역할은 겸하지 않는다.
- Single-agent: 이 역할의 입력·산출물·exit를 별도 pass로 유지한다.
- No-team fallback: 같은 파일과 handoff schema를 사용하고 agent-team 기능을 요구하지 않는다.
'''.encode("utf-8")


def dispatch(case: dict) -> bytes:
    case_id = case["case_id"]
    role_links = "\n".join(f"- [{role}](../roles/{role}.md)" for role in case["logical_roles"])
    return f'''# Runtime dispatch — {case['title']}

Contract: `boi-local-case-runtime/v1`

이 문서는 Codex·Claude·Single-agent가 같은 Case 산출물 계약을 실행하기 위한 얇은 adapter입니다. 별도 도메인 Skill이나 OKF schema를 만들지 않습니다.

## Load order

1. [Case manifest](../case.yaml)와 [orchestrator DAG](../orchestrator.md)
2. 선택한 scale mode에서 필요한 역할 카드만
3. [domain method](../references/method.md)와 [output contract](../expected/OUTPUT-CONTRACT.md)
4. [fixture manifest](../fixtures/manifest.json)와 해당 source subset
5. 실제 평가일 때만 [frozen protocol](../evals/PROTOCOL.md)

## Role cards

{role_links}

Reviewer: **{case['reviewer_role']}**

## Runtime mapping

- **Codex Full:** DAG에서 독립적인 역할만 병렬 agent로 보내고, 모든 handoff 파일이 완성된 뒤 reviewer를 실행한다.
- **Claude Full:** 같은 역할 카드와 DAG를 사용한다. Team 기능이 없으면 Reduced 또는 Single-agent로 자동 축소한다.
- **Reduced:** creator 1명과 독립 reviewer 1명으로 실행한다.
- **Single-agent/No-team:** 역할별 pass를 순차 수행하고 reviewer pass에서는 source부터 다시 읽는다.

어떤 runtime도 입력·산출물 schema, hard fail, Local/Remote 경계, reviewer exit criteria를 줄일 수 없다.

## Handoff envelope

모든 역할 전환은 [boi-local-case-handoff/v1](../../../_schema/handoff.schema.json)을 사용한다. 단순 채팅 요약만으로 다음 역할을 시작하지 않는다. output file hash와 source-integrity hash가 없으면 해당 handoff는 실패다.

## Stop conditions

- source hash drift 또는 허용 source 밖 접근
- 누락 evidence를 사실처럼 채움
- reviewer와 creator 독립성 상실
- Local path·식별자·raw bytes가 remote projection에 포함됨
- 승인 없는 MCP write 또는 remote submit

중단 시 완료를 주장하지 않고 blocker와 안전한 resume point를 Local에 남긴다.
'''.encode("utf-8")


def runtime_manifest(case: dict) -> bytes:
    return encoded_json(
        {
            "schema": "boi-local-case-runtime/v1",
            "case_id": case["case_id"],
            "orchestrator": "../orchestrator.md",
            "handoff_schema": "../../../_schema/handoff.schema.json",
            "reviewer_role": case["reviewer_role"],
            "role_cards": [
                {
                    "role": role,
                    "path": f"../roles/{role}.md",
                    "independent_reviewer": role == case["reviewer_role"],
                }
                for role in case["logical_roles"]
            ],
            "scale_modes": case["scale_modes"],
            "remote_mutation_default": False,
        }
    )


def expected_cases() -> list[tuple[Path, dict, list[tuple[str, str, str, str, str, str]]]]:
    result: list[tuple[Path, dict, list[tuple[str, str, str, str, str, str]]]] = []
    flagship_root = ROOT / FLAGSHIP_PATH
    flagship = json.loads((flagship_root / "case.yaml").read_text(encoding="utf-8"))
    result.append((flagship_root, flagship, FLAGSHIP_ROLES))
    for relative, spec in CASES.items():
        case_root = ROOT / relative
        case = json.loads((case_root / "case.yaml").read_text(encoding="utf-8"))
        result.append((case_root, case, list(spec["roles"])))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    mismatches: list[str] = []
    written = 0
    for case_root, case, roles in expected_cases():
        outputs: dict[Path, bytes] = {
            case_root / "runtime" / "dispatch.md": dispatch(case),
            case_root / "runtime" / "runtime.yaml": runtime_manifest(case),
        }
        reviewer = case["reviewer_role"]
        if {role[0] for role in roles} != set(case["logical_roles"]):
            raise ValueError(f"role source and manifest differ: {case['case_id']}")
        for role in roles:
            outputs[case_root / "roles" / f"{role[0]}.md"] = card(
                case["case_id"], role, role[0] == reviewer
            )
        for target, payload in outputs.items():
            if args.check:
                if not target.is_file() or target.read_bytes() != payload:
                    mismatches.append(target.relative_to(ROOT).as_posix())
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.is_file() or target.read_bytes() != payload:
                    target.write_bytes(payload)
                    written += 1
    if mismatches:
        print(json.dumps({"ok": False, "mismatches": mismatches}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"ok": True, "mode": "check" if args.check else "write", "written": written}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
