#!/usr/bin/env python3
"""Pin and consume the shared BoI Wiki HarnessPackage without extra dependencies."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PACKAGE_RUNTIME_FIELDS = {
    "checksum", "signature", "signature_algorithm", "signature_status",
    "readiness", "warnings",
}
MANAGED_MARKER = "<!-- boi-harness-bootstrap:managed -->"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def checksum(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tree_digest(root: Path) -> str:
    if not root.exists():
        return hashlib.sha256(b"").hexdigest()
    rows = [
        {"path": str(path.relative_to(root)), "sha256": file_digest(path), "bytes": path.stat().st_size}
        for path in sorted(item for item in root.rglob("*") if item.is_file())
    ]
    return checksum(rows)


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            stream.write(value.rstrip() + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class HarnessClient:
    def __init__(self, base_url: str, employee_id: str, token: str, timeout: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.employee_id = employee_id
        self.token = token
        self.timeout = timeout

    def request(self, method: str, path: str, payload: Any | None = None) -> Any:
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        elif self.employee_id:
            headers["x-employee-id"] = self.employee_id
        data = None
        if payload is not None:
            data = canonical_bytes(payload)
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(f"{self.base_url}{path}", data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Harness API {method} {path} failed: HTTP {exc.code} {body}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Harness API unavailable: {exc.reason}") from exc

    def get(self, path: str) -> Any:
        return self.request("GET", path)

    def post(self, path: str, payload: Any) -> Any:
        return self.request("POST", path, payload)


def package_checksum(package: dict[str, Any]) -> str:
    return checksum({key: value for key, value in package.items() if key not in PACKAGE_RUNTIME_FIELDS})


def validate_package(package: dict[str, Any], lock: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    required = {"release", "package_schema", "checksum", "signature", "signature_algorithm", "capability_catalog", "ontology_schema_registry", "domain_catalogs", "policies"}
    missing = sorted(required - set(package))
    if missing:
        failures.append(f"package_missing:{','.join(missing)}")
    if package_checksum(package) != str(package.get("checksum") or ""):
        failures.append("package_checksum_mismatch")
    for key in ("release", "checksum", "signature", "signature_algorithm"):
        if str(lock.get(key) or "") != str(package.get(key) or ""):
            failures.append(f"lock_{key}_mismatch")
    if str(lock.get("schema") or "") != "boi-harness-lock/v1":
        failures.append("lock_schema_invalid")
    return failures


def managed_bootstrap(client: str, package: dict[str, Any], bootstrap: dict[str, Any]) -> str:
    title = "Codex" if client == "codex" else "Claude"
    instructions = "\n".join(f"- {item}" for item in bootstrap.get("instructions") or [])
    skill_location = (
        "Load project Skills from `.claude/skills/`. " if client == "claude" else ""
    )
    return f"""{MANAGED_MARKER}
# {title} Bootstrap for BoI Wiki Local

This file is a thin client bootstrap generated from the pinned BoI Wiki HarnessPackage.
It is not the canonical policy source.

- Harness release: `{package['release']}`
- Harness checksum: `{package['checksum']}`
- Canonical snapshot: `.boi-harness/package.json`
- Local lock: `harness.lock`

Before using shared BoI capabilities, read the pinned package contracts. If an optional
validation runtime is available, run `scripts/harness_sync.py verify`; otherwise compare the
embedded release, canonical checksum, signature, and signature algorithm in the lock and snapshot
and label the reduced check. The canonical package checksum is not the raw `package.json` file
SHA256; never compare those two values. If the shared endpoint is unavailable, continue with the
pinned offline snapshot and Local Private files only.

{instructions}

Local Private source text under `data/boi/private/` must never be published to BoI Wiki, MCP,
Team, or Public scope without an explicit user-approved preview. A user-selected AI runtime may
process selected content under the approved provider and company policy; record that separately
from BoI remote activity and never claim false zero-byte processing. Shared execution must inherit
the authenticated principal ACL, use expected revision and idempotency, and follow preview then confirmation.

## Local Second Brain session check

When a real Local Profile contains `.boi-local/second-brain-preferences.json`, use the
`boi-second-brain` Skill. Check the configured source folder at session start only when
`agent_session_check` is true. In `suggest` mode, show a grouped preview before knowledge writes.
In `explicit-only` mode, do not inspect the folder or retain conversation knowledge automatically;
act only after an explicit natural-language request. Never copy raw chat transcripts. This check
must not require Python, open an external window, run without the agent, or upload Local Private content.

## Meta Harness and Case Harnesses

{skill_location}Use `boi-harness-builder` when a user wants to turn a recurring work description into a
reusable BoI Harness, or to package, evaluate, register, or evolve that repeatable pattern.
Do not use it for ordinary one-off document authoring or merely running an existing Case.
When a user asks to run a previously configured personal Harness, search the active Local Profile's
`notes/harnesses/` directory, load the matching profiled Harness card, and execute its declared DAG
and output contract. Invoke the builder again only to audit or evolve that card. Reuse existing generic
BoI Skills before proposing a new Skill. Case-specific domain knowledge
belongs under `cases/`; it must not silently create a new OKF schema or global domain Skill.
Never call a Case `reference` or `production-ready` unless its stored cross-runtime benchmark,
hard safety assertions, blind review, non-developer acceptance, and actual BoI Wiki contract
evidence satisfy the production gates.
"""


def workspace_paths(root: Path) -> dict[str, Path]:
    return {
        "private": root / "data" / "boi" / "private",
        "lock": root / "harness.lock",
        "package": root / ".boi-harness" / "package.json",
        "state": root / ".boi-harness" / "sync-state.json",
        "bootstrap_codex": root / ".boi-harness" / "bootstrap" / "codex.json",
        "bootstrap_claude": root / ".boi-harness" / "bootstrap" / "claude.json",
        "bootstrap_custom": root / ".boi-harness" / "bootstrap" / "custom.json",
        "agents": root / "AGENTS.md",
        "claude": root / "CLAUDE.md",
    }


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return value


def sync(args: argparse.Namespace) -> dict[str, Any]:
    target = workspace_paths(Path(args.root).resolve())
    private_before = tree_digest(target["private"])
    client = HarnessClient(args.base_url, args.employee_id, args.token, args.timeout)
    package = client.get("/api/v2/harness/current")
    lock_response = client.get("/api/v2/harness/local-lock")
    lock = dict(lock_response.get("harness_lock") or lock_response)
    bootstraps = {name: client.get(f"/api/v2/harness/bootstrap/{name}") for name in ("codex", "claude", "custom")}
    failures = validate_package(package, lock)
    for name, bootstrap in bootstraps.items():
        if str(bootstrap.get("generated_from_checksum") or "") != package.get("checksum"):
            failures.append(f"bootstrap_{name}_checksum_mismatch")
    online = client.post("/api/v2/harness/local/offline/verify", {"harness_lock": lock, "expected_checksum": package.get("checksum")})
    if not online.get("lock_valid") or not online.get("signature_valid"):
        failures.append("server_signature_or_lock_verification_failed")
    if failures:
        raise RuntimeError("Harness sync rejected: " + ", ".join(sorted(set(failures))))

    atomic_json(target["package"], package)
    atomic_json(target["lock"], lock)
    for name, bootstrap in bootstraps.items():
        atomic_json(target[f"bootstrap_{name}"], bootstrap)
    atomic_text(target["agents"], managed_bootstrap("codex", package, bootstraps["codex"]))
    atomic_text(target["claude"], managed_bootstrap("claude", package, bootstraps["claude"]))
    private_after = tree_digest(target["private"])
    if private_after != private_before:
        raise RuntimeError("Local Private tree changed during Harness sync")
    state = {
        "schema": "boi-local-harness-state/v1",
        "release": package["release"], "checksum": package["checksum"],
        "signature": package["signature"], "signature_algorithm": package["signature_algorithm"],
        "online_signature_verified": True,
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "source_identity": args.base_url.rstrip("/"),
        "private_tree_digest_before": private_before, "private_tree_digest_after": private_after,
        "private_files_overwritten": False, "token_persisted": False,
    }
    atomic_json(target["state"], state)
    return {
        "status": "synced", "release": package["release"], "checksum": package["checksum"],
        "signature_status": package.get("signature_status"), "online_signature_verified": True,
        "offline_snapshot_ready": True, "private_files_overwritten": False, "network_accessed": True,
        "paths": {"lock": str(target["lock"]), "package": str(target["package"])},
    }


def verify(args: argparse.Namespace) -> dict[str, Any]:
    target = workspace_paths(Path(args.root).resolve())
    package, lock, state = read_json(target["package"]), read_json(target["lock"]), read_json(target["state"])
    failures = validate_package(package, lock)
    if state.get("checksum") != package.get("checksum"):
        failures.append("sync_state_checksum_mismatch")
    if not state.get("online_signature_verified"):
        failures.append("signature_online_attestation_missing")
    for path_key in ("agents", "claude"):
        path = target[path_key]
        body = path.read_text(encoding="utf-8") if path.exists() else ""
        if MANAGED_MARKER not in body or str(package.get("checksum") or "") not in body:
            failures.append(f"{path_key}_bootstrap_not_bound")
    return {
        "status": "valid" if not failures else "invalid", "lock_valid": not failures,
        "offline_snapshot_consumed": not failures, "release": package.get("release", ""),
        "checksum": package.get("checksum", ""),
        "signature_pinned": bool(package.get("signature")) and package.get("signature") == lock.get("signature"),
        "signature_validation": "online_attestation_pinned", "network_accessed": False,
        "private_files_overwritten": False, "failures": sorted(set(failures)),
    }


def preview(args: argparse.Namespace) -> dict[str, Any]:
    target = workspace_paths(Path(args.root).resolve())
    current_lock = read_json(target["lock"])
    private_before = tree_digest(target["private"])
    client = HarnessClient(args.base_url, args.employee_id, args.token, args.timeout)
    package = client.get("/api/v2/harness/current")
    result = client.post("/api/v2/harness/local/update/preview", {"current_lock": current_lock, "target_release": package.get("release")})
    if private_before != tree_digest(target["private"]):
        raise RuntimeError("Local Private tree changed during update preview")
    return {**result, "target_signature_status": package.get("signature_status"), "network_accessed": True, "private_files_overwritten": False}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("sync", "preview", "verify"))
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--base-url", default=os.environ.get("BOI_WIKI_BASE_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--employee-id", default=os.environ.get("BOI_LOCAL_EMPLOYEE_ID", ""))
    parser.add_argument("--token", default=os.environ.get("BOI_WIKI_PAT", ""), help=argparse.SUPPRESS)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--report-path", default="", help="Optional JSON audit report path")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = {"sync": sync, "preview": preview, "verify": verify}[args.command](args)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        result = {"status": "failed", "error": str(exc)}
        if args.report_path:
            atomic_json(Path(args.report_path).resolve(), result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1
    if args.report_path:
        atomic_json(Path(args.report_path).resolve(), result)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("status") not in {"failed", "invalid"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
