#!/usr/bin/env python3
"""Shared, dependency-free helpers for BoI Wiki Local commands."""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

KST = timezone(timedelta(hours=9))
EMPLOYEE_ID_RE = re.compile(r"[0-9]{7}")
RESERVED_NAMES = {"index.md", "log.md"}
SOURCE_START = "<!-- boi-source:start -->"
SOURCE_END = "<!-- boi-source:end -->"
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")

REQUIRED_LOCAL_FIELDS = (
    "okf_version",
    "boi_profile_version",
    "type",
    "title",
    "description",
    "timestamp",
    "boi_id",
    "visibility",
    "classification",
    "owner",
    "employee_id",
    "local_owner_ref",
    "local_only",
    "promotion_status",
    "retention_class",
    "archive_status",
    "artifact_visibility",
    "lifecycle_state",
    "memory_candidate",
    "cleanup_policy",
    "review_after",
    "contains_sensitive",
    "source_refs",
)


def now_kst() -> datetime:
    return datetime.now(KST)


def normalize_text(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n").strip()


def sha256_text(value: str) -> str:
    return hashlib.sha256(normalize_text(value).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9가-힣._-]+", "-", value.strip().lower()).strip("-")
    return slug[:80] or "local-document"


def dotenv_value(root: Path, key: str) -> str:
    path = root / ".env"
    if not path.is_file():
        return ""
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        if name.strip() != key:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        return value.strip()
    return ""


def workspace_employee_id(
    root: Path,
    raw: str | None = None,
    *,
    allow_template: bool = True,
) -> tuple[str, str]:
    """Resolve one Local Profile without printing or persisting its identifier."""
    root = root.resolve()
    explicit = (raw or "").strip()
    environment = os.getenv("BOI_LOCAL_EMPLOYEE_ID", "").strip()
    configured = dotenv_value(root, "BOI_LOCAL_EMPLOYEE_ID")
    source = ""
    employee_id = ""
    if explicit:
        employee_id, source = explicit, "argument"
    else:
        if environment and not EMPLOYEE_ID_RE.fullmatch(environment):
            raise ValueError("BOI_LOCAL_EMPLOYEE_ID must be a numeric 7-digit employee ID")
        if configured and not EMPLOYEE_ID_RE.fullmatch(configured):
            raise ValueError(".env BOI_LOCAL_EMPLOYEE_ID must be a numeric 7-digit employee ID")
        if (
            environment not in {"", "0000000"}
            and configured not in {"", "0000000"}
            and environment != configured
        ):
            raise ValueError(
                "environment and .env select different Local Private profiles; choose one explicitly"
            )

        if environment and environment != "0000000":
            employee_id, source = environment, "environment"
        elif configured and configured != "0000000":
            employee_id, source = configured, "dotenv"
        else:
            private = root / "data" / "boi" / "private"
            profiles = sorted(
                path.name
                for path in private.iterdir()
                if path.is_dir() and EMPLOYEE_ID_RE.fullmatch(path.name) and path.name != "0000000"
            ) if private.is_dir() else []
            if len(profiles) > 1:
                raise ValueError("multiple Local Private profiles found; set BOI_LOCAL_EMPLOYEE_ID explicitly")
            if len(profiles) == 1:
                employee_id, source = profiles[0], "profile-directory"
            elif configured:
                employee_id, source = configured, "dotenv-template"
            elif environment:
                employee_id, source = environment, "environment-template"
            else:
                employee_id, source = "0000000", "template-default"
    if not EMPLOYEE_ID_RE.fullmatch(employee_id):
        raise ValueError("BOI_LOCAL_EMPLOYEE_ID must be a numeric 7-digit employee ID")
    if employee_id == "0000000" and not allow_template:
        raise ValueError("0000000 is the template ID; provide your real 7-digit employee ID")
    return employee_id, source


def private_root(root: Path, employee_id: str) -> Path:
    return root / "data" / "boi" / "private" / employee_id


def relative_to_root(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def require_private_path(root: Path, employee_id: str, path: Path) -> Path:
    resolved = path.resolve()
    resolved.relative_to(private_root(root.resolve(), employee_id).resolve())
    return resolved


def split_frontmatter(text: str) -> tuple[str, str]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    # Windows PowerShell 5.1 writes UTF-8 with a BOM.  Treat a single leading
    # BOM as an encoding marker so otherwise canonical OKF/BoI frontmatter is
    # portable across Windows-native agents and editors.
    if normalized.startswith("\ufeff"):
        normalized = normalized[1:]
    if not normalized.startswith("---\n"):
        return "", normalized
    end = normalized.find("\n---\n", 4)
    if end < 0:
        return "", normalized
    return normalized[4:end], normalized[end + 5 :]


def parse_frontmatter(text: str) -> dict[str, str]:
    header, _ = split_frontmatter(text)
    result: dict[str, str] = {}
    for line in header.splitlines():
        if not line or line[0].isspace() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        result[key.strip()] = value
    return result


def parse_frontmatter_list(text: str, field: str) -> list[dict[str, str]]:
    """Parse the small list-of-mappings subset used by OKF source_refs.

    The Local profile intentionally stays dependency-free. This parser does not
    pretend to be a general YAML implementation; it accepts only the canonical
    list shape emitted by ``local_frontmatter``.
    """
    header, _ = split_frontmatter(text)
    lines = header.splitlines()
    start = next((index for index, line in enumerate(lines) if line.startswith(f"{field}:")), -1)
    if start < 0 or lines[start].strip().endswith("[]"):
        return []
    items: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in lines[start + 1 :]:
        if line and not line[0].isspace():
            break
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- "):
            if current:
                items.append(current)
            current = {}
            stripped = stripped[2:].strip()
        if current is None or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        current[key.strip()] = value
    if current:
        items.append(current)
    return items


def yaml_scalar(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return '""'
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def append_frontmatter_items(lines: list[str], field: str, items: list[dict[str, Any]]) -> None:
    lines.append(f"{field}:")
    if not items:
        lines[-1] = f"{field}: []"
        return
    for item in items:
        first = True
        for key, value in item.items():
            prefix = "  - " if first else "    "
            lines.append(f"{prefix}{key}: {yaml_scalar(value)}")
            first = False


def replace_frontmatter_list(text: str, field: str, items: list[dict[str, str]]) -> str:
    """Replace one canonical frontmatter list while preserving all other text."""
    header, body = split_frontmatter(text)
    if not header:
        raise ValueError("missing YAML frontmatter")
    lines = header.splitlines()
    start = next((index for index, line in enumerate(lines) if line.startswith(f"{field}:")), -1)
    if start < 0:
        raise ValueError(f"missing frontmatter field: {field}")
    end = start + 1
    while end < len(lines) and (not lines[end] or lines[end][0].isspace()):
        end += 1
    rendered = [f"{field}:"]
    if not items:
        rendered[0] = f"{field}: []"
    else:
        for item in items:
            first = True
            for key, value in item.items():
                rendered.append(f"{'  - ' if first else '    '}{key}: {yaml_scalar(value)}")
                first = False
    new_header = "\n".join(lines[:start] + rendered + lines[end:])
    return f"---\n{new_header}\n---\n{body}"


def local_frontmatter(
    *,
    employee_id: str,
    doc_type: str,
    title: str,
    description: str,
    boi_id: str,
    tags: list[str],
    source_refs: list[dict[str, str]],
    timestamp: datetime | None = None,
    promotion_status: str = "local_only",
    retention_class: str = "working",
    artifact_visibility: str = "working",
    lifecycle_state: str = "working",
    memory_candidate: bool = False,
    review_after_days: int = 30,
    contains_sensitive: str = "unknown",
    generated_from: list[dict[str, Any]] | None = None,
    extra: dict[str, Any] | None = None,
) -> str:
    current = timestamp or now_kst()
    lines = [
        "---",
        'okf_version: "0.1"',
        'boi_profile_version: "0.1-local"',
        f"type: {doc_type}",
        f"title: {yaml_scalar(title)}",
        f"description: {yaml_scalar(description)}",
        "tags: [" + ", ".join(tags) + "]",
        f"timestamp: {current.isoformat()}",
        f"boi_id: {boi_id}",
        "visibility: local-private",
        "classification: internal",
        f'owner: "{employee_id}"',
        f'employee_id: "{employee_id}"',
        f"local_owner_ref: local-private:{employee_id}",
        "local_only: true",
        f"promotion_status: {promotion_status}",
        f"retention_class: {retention_class}",
        'retention_until: ""',
        "archive_status: active",
        f"artifact_visibility: {artifact_visibility}",
        f"lifecycle_state: {lifecycle_state}",
        f"memory_candidate: {'true' if memory_candidate else 'false'}",
        "cleanup_policy: keep",
        f"review_after: {(current + timedelta(days=review_after_days)).date().isoformat()}",
        f"contains_sensitive: {contains_sensitive}",
    ]
    if extra:
        lines.extend(f"{key}: {yaml_scalar(value)}" for key, value in extra.items())
    append_frontmatter_items(lines, "source_refs", source_refs)
    if generated_from is not None:
        append_frontmatter_items(lines, "generated_from", generated_from)
    lines.append("---")
    return "\n".join(lines) + "\n"


def captured_source(body: str) -> str | None:
    normalized = body.replace("\r\n", "\n").replace("\r", "\n")
    start = normalized.find(SOURCE_START)
    end = normalized.find(SOURCE_END)
    if start < 0 or end < 0 or end <= start:
        return None
    return normalize_text(normalized[start + len(SOURCE_START) : end])


def verify_locked_source(text: str, metadata: dict[str, str] | None = None) -> tuple[bool, str]:
    meta = metadata or parse_frontmatter(text)
    if meta.get("source_immutability") != "locked":
        return True, "not_locked"
    _, body = split_frontmatter(text)
    source = captured_source(body)
    if source is None:
        return False, "locked source markers are missing"
    expected = meta.get("source_sha256", "")
    actual = sha256_text(source)
    if not expected:
        return False, "source_sha256 is missing"
    if actual != expected:
        return False, f"source hash mismatch: expected {expected}, got {actual}"
    return True, "verified"


def atomic_write(path: Path, content: str, *, overwrite: bool = False) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    temporary.replace(path)


def append_log(root: Path, message: str) -> None:
    path = root / "data" / "boi" / "log.md"
    today = now_kst().date().isoformat()
    text = path.read_text(encoding="utf-8") if path.exists() else "# Local BoI Log\n"
    heading = f"## {today}"
    if heading not in text:
        text = text.rstrip() + f"\n\n{heading}\n"
    text = text.rstrip() + f"\n\n- {message}\n"
    atomic_write(path, text, overwrite=True)


def append_index_link(index_path: Path, title: str, relative_link: str) -> None:
    line = f"* [{title}]({relative_link})"
    text = index_path.read_text(encoding="utf-8") if index_path.exists() else "# Index\n"
    if line not in text:
        text = text.rstrip() + "\n\n" + line + "\n"
        atomic_write(index_path, text, overwrite=True)
