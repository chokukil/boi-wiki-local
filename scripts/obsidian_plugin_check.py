#!/usr/bin/env python3
"""Select reviewed optional plugin versions compatible with an Obsidian app version."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path


def version_tuple(value: str) -> tuple[int, ...]:
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)", value)
    if not match:
        raise ValueError(f"invalid semantic version: {value}")
    return tuple(int(part) for part in match.groups())


def detect_windows_runtime_version(appdata: Path | None = None) -> dict[str, object]:
    """Detect the Electron runtime ASAR version, which may be newer than Obsidian.exe."""
    root = appdata or (Path(os.environ["APPDATA"]) if os.environ.get("APPDATA") else None)
    if root is None:
        return {"detected": False, "version": "", "source": "not-windows-or-appdata-missing"}
    obsidian_data = root / "obsidian"
    candidates: list[tuple[tuple[int, ...], str, Path]] = []
    for path in obsidian_data.glob("obsidian-*.asar") if obsidian_data.exists() else []:
        match = re.fullmatch(r"obsidian-(\d+\.\d+\.\d+)\.asar", path.name)
        if match:
            candidates.append((version_tuple(match.group(1)), match.group(1), path))
    if not candidates:
        return {"detected": False, "version": "", "source": "runtime-asar-not-found"}
    _, version, path = max(candidates)
    return {"detected": True, "version": version, "source": "appdata-runtime-asar", "path": str(path)}


def resolve_app_version(snapshot: dict, requested: str) -> dict[str, object]:
    if requested and requested.lower() != "auto":
        version_tuple(requested)
        return {"detected": True, "version": requested, "source": "explicit-argument"}
    override = os.environ.get("OBSIDIAN_APP_VERSION", "").strip()
    if override:
        version_tuple(override)
        return {"detected": True, "version": override, "source": "OBSIDIAN_APP_VERSION"}
    detected = detect_windows_runtime_version()
    if detected["detected"]:
        return detected
    reference = str(snapshot.get("reference_app_version") or "")
    version_tuple(reference)
    return {
        "detected": False,
        "version": reference,
        "source": "reviewed-reference-no-installed-runtime",
        "detection_detail": detected["source"],
    }


def evaluate(snapshot: dict, app_version: str, *, app_version_source: str = "explicit-argument", installed_detected: bool = True) -> dict[str, object]:
    installed = version_tuple(app_version)
    results = []
    for plugin in snapshot.get("plugins", []):
        selected = None
        for candidate in plugin.get("candidates", []):
            if installed >= version_tuple(str(candidate["min_app_version"])):
                selected = candidate
                break
        policy = str(plugin.get("distribution_policy") or "optional-manual-install")
        compatible_status = (
            "deferred-until-core-search-gap"
            if policy == "deferred-until-core-search-gap"
            else "compatible-reviewed-candidate"
        )
        results.append(
            {
                "id": plugin.get("id"),
                "name": plugin.get("name"),
                "optional": True,
                "status": compatible_status if selected else "skip-no-reviewed-compatible-candidate",
                "distribution_policy": policy,
                "selected": selected,
                "latest": plugin.get("candidates", [None])[0],
                "required_settings": plugin.get("required_settings", {}),
                "requires_user_install_confirmation": True,
                "sources": plugin.get("sources", []),
            }
        )
    return {
        "ok": all(
            item["status"]
            in {
                "compatible-reviewed-candidate",
                "deferred-until-core-search-gap",
                "skip-no-reviewed-compatible-candidate",
            }
            for item in results
        ),
        "schema": snapshot.get("schema"),
        "snapshot_verified_at": snapshot.get("verified_at"),
        "app_version": app_version,
        "app_version_source": app_version_source,
        "installed_app_detected": installed_detected,
        "plugins": results,
        "plugins_required_for_local_second_brain": False,
        "plugins_installed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--app-version", default="auto", help="Semantic version or 'auto' (default)")
    args = parser.parse_args()
    path = Path(args.root).resolve() / "research" / "obsidian-plugin-compatibility.json"
    try:
        snapshot = json.loads(path.read_text(encoding="utf-8"))
        resolved = resolve_app_version(snapshot, args.app_version)
        payload = evaluate(
            snapshot,
            str(resolved["version"]),
            app_version_source=str(resolved["source"]),
            installed_detected=bool(resolved["detected"]),
        )
        payload["app_version_detection"] = resolved
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        payload = {"ok": False, "error": str(exc)}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
