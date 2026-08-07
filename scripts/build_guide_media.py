#!/usr/bin/env python3
"""Build annotated WebP screenshots and their deterministic guide manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

GUIDE_RELEASE = "3.1.0"
MAX_WIDTH = 1760
MAX_BYTES = 600 * 1024

SPECS = [
    ("01", "explorer-repository", "File Explorer에서 boi-wiki-local 저장소와 install.cmd를 확인하는 화면", "File Explorer", "Windows 11", "10-install-repository.md", (0.13, 0.12, 0.50, 0.91)),
    ("02", "notepad-markdown", "Windows 메모장에서 OKF 0.1과 BoI Profile 0.1-local Markdown을 여는 화면", "Notepad", "Windows 11", "26-no-obsidian.md", (0.01, 0.12, 0.58, 0.92)),
    ("03", "vault-manager", "Obsidian Vault Manager에서 0000000 Local Private 경로를 확인하는 화면", "Obsidian", "1.13.4", "30-obsidian-install-and-vault.md", (0.01, 0.04, 0.35, 0.49)),
    ("04", "obsidian-start-here", "Obsidian에서 BoI Wiki Local 시작 페이지와 다음 여정 링크를 보는 화면", "Obsidian", "1.13.4", "00-start-here.md", (0.35, 0.10, 0.97, 0.94)),
    ("05", "obsidian-properties", "Obsidian Properties에서 OKF 0.1과 BoI Profile 0.1-local을 확인하는 화면", "Obsidian", "1.13.4", "21-okf-and-boi-profile.md", (0.36, 0.16, 0.96, 0.96)),
    ("06", "immutable-capture", "잠긴 Local capture의 source_sha256과 source_immutability를 확인하는 화면", "Obsidian", "1.13.4", "23-capture-distill-review.md", (0.36, 0.50, 0.96, 0.82)),
    ("07", "distilled-provenance", "정제 지식에서 generated_from과 구조화된 source_refs를 확인하는 화면", "Obsidian", "1.13.4", "23-capture-distill-review.md", (0.36, 0.45, 0.96, 0.72)),
    ("08", "core-search", "Obsidian Core Search에서 합성 품질 지식을 다시 찾는 화면", "Obsidian", "1.13.4", "20-first-10-minutes.md", (0.05, 0.04, 0.33, 0.96)),
    ("09", "backlinks-outgoing", "정제 지식의 Backlinks 패널과 연결된 원문을 확인하는 화면", "Obsidian", "1.13.4", "31-obsidian-core-settings.md", (0.72, 0.05, 0.99, 0.52)),
    ("10", "filtered-graph", "Obsidian Graph의 필터 패널과 Local Wiki 연결 구조를 확인하는 화면", "Obsidian", "1.13.4", "31-obsidian-core-settings.md", (0.34, 0.04, 0.71, 0.96)),
    ("11", "properties-bases", "Obsidian Bases가 Markdown Properties를 목록으로 보여주는 화면", "Obsidian", "1.13.4", "31-obsidian-core-settings.md", (0.34, 0.05, 0.71, 0.97)),
    ("12", "core-plugins", "Obsidian 설정에서 Core plugins 목록을 확인하는 화면", "Obsidian", "1.13.4", "31-obsidian-core-settings.md", (0.01, 0.05, 0.25, 0.97)),
    ("13", "mode-matrix", "Obsidian과 MCP 구성에 따른 가능 작업과 금지 작업 표를 보는 화면", "Obsidian", "1.13.4", "52-mode-matrix.md", (0.35, 0.35, 0.70, 0.99)),
    ("14", "team-promotion-preview", "Team promotion preview에서 scope reviewer hash와 미승인 상태를 확인하는 화면", "Obsidian", "1.13.4", "51-promotion-package.md", (0.35, 0.04, 0.70, 0.96)),
    ("15", "organization-knowledge-loop", "Local capture에서 검토와 승인 후 조직 지식으로 이어지는 운영 루프 화면", "Obsidian", "1.13.4", "53-organization-knowledge-loop.md", (0.35, 0.25, 0.70, 0.98)),
    ("28", "agent-setup-request", "Codex·Claude에 한 문장으로 BoI Wiki 호환 Harness와 Local Private Second Brain 설정을 요청하는 합성 교육 화면", "Synthetic AI chat training mockup", "provider-neutral", "12-ai-assisted-setup.md", (0.20, 0.14, 0.95, 0.66)),
    ("29", "curation-presets", "알아서 정리·정리 전 확인·요청할 때만 세 가지 방식을 선택하는 합성 교육 화면", "Synthetic AI chat training mockup", "provider-neutral", "12-ai-assisted-setup.md", (0.22, 0.16, 0.93, 0.78)),
    ("30", "zero-ui-setup-complete", "외부 창 없이 완료된 대화 관리·자료 폴더·원본 보존·원격 업로드 차단 설정 요약", "Synthetic AI chat training mockup", "provider-neutral", "12-ai-assisted-setup.md", (0.23, 0.15, 0.91, 0.81)),
    ("31", "inbox-curation-summary", "대량 자료 폴더 정리 후 보강·신규·중복·확인 필요·처리 중 건수를 보는 합성 교육 화면", "Synthetic AI chat training mockup", "provider-neutral", "14-folder-auto-curation.md", (0.23, 0.16, 0.89, 0.89)),
    ("32", "memory-before-after", "같은 주제의 기존 지식에 새 근거와 변경 이력이 보강된 전후 비교 합성 화면", "Synthetic AI chat training mockup", "provider-neutral", "13-conversation-memory.md", (0.21, 0.15, 0.96, 0.82)),
    ("33", "duplicate-already-reflected", "같은 SHA256 자료를 이미 반영됨으로 처리하고 새 파일을 만들지 않은 합성 화면", "Synthetic AI chat training mockup", "provider-neutral", "14-folder-auto-curation.md", (0.24, 0.17, 0.88, 0.73)),
    ("34", "conflict-needs-review", "기존 결정과 새 자료의 충돌을 자동 덮어쓰지 않고 확인 필요로 둔 합성 화면", "Synthetic AI chat training mockup", "provider-neutral", "15-memory-review-and-correction.md", (0.23, 0.16, 0.92, 0.80)),
]


def annotate(source: Path, destination: Path, number: str, rect: tuple[float, float, float, float]) -> tuple[int, int, int, str]:
    image = Image.open(source).convert("RGB")
    if image.width > MAX_WIDTH:
        height = round(image.height * MAX_WIDTH / image.width)
        image = image.resize((MAX_WIDTH, height), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(image)
    x1, y1, x2, y2 = (round(rect[0] * image.width), round(rect[1] * image.height), round(rect[2] * image.width), round(rect[3] * image.height))
    width = max(3, round(image.width / 360))
    draw.rounded_rectangle((x1, y1, x2, y2), radius=10, outline=(225, 29, 72), width=width)
    badge_size = max(42, round(image.width / 19))
    draw.ellipse((12, 12, 12 + badge_size, 12 + badge_size), fill=(225, 29, 72), outline="white", width=2)
    font = ImageFont.load_default(size=max(18, badge_size // 2))
    box = draw.textbbox((0, 0), number, font=font)
    tx = 12 + (badge_size - (box[2] - box[0])) / 2
    ty = 12 + (badge_size - (box[3] - box[1])) / 2 - box[1]
    draw.text((tx, ty), number, fill="white", font=font)
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, "WEBP", quality=82, method=6)
    data = destination.read_bytes()
    if len(data) > MAX_BYTES:
        image.save(destination, "WEBP", quality=68, method=6)
        data = destination.read_bytes()
    if len(data) > MAX_BYTES:
        raise ValueError(f"{destination.name} exceeds {MAX_BYTES} bytes")
    return image.width, image.height, len(data), hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture-dir", required=True)
    parser.add_argument("--output-dir", default="templates/second-brain-guide/_media")
    parser.add_argument("--captured-at", default=datetime.now().astimezone().isoformat(timespec="seconds"))
    args = parser.parse_args()
    capture_dir = Path(args.capture_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    old_manifest_path = output_dir / "manifest.json"
    old_items = {}
    if old_manifest_path.exists():
        old_payload = json.loads(old_manifest_path.read_text(encoding="utf-8"))
        old_items = {item.get("id", ""): item for item in old_payload.get("items", [])}
    items = []
    for number, slug, alt, app, app_version, page, rect in SPECS:
        source = capture_dir / f"{number}-{slug}.png"
        destination = output_dir / f"{number}-{slug}.webp"
        if source.exists():
            width, height, byte_count, digest = annotate(source, destination, number, rect)
            captured_at = args.captured_at
        elif destination.exists():
            with Image.open(destination) as existing:
                width, height = existing.size
            data = destination.read_bytes()
            byte_count = len(data)
            digest = hashlib.sha256(data).hexdigest()
            captured_at = old_items.get(f"screen-{number}", {}).get("captured_at", args.captured_at)
        else:
            raise FileNotFoundError(source)
        synthetic = number in {"16", "17", "28", "29", "30", "31", "32", "33", "34"}
        capture_method = "synthetic-training-mockup" if synthetic else "windows-graphics-capture"
        capture_source = "generated synthetic training screen" if synthetic else "Windows application window"
        item = {
            "id": f"screen-{number}",
            "file": destination.name,
            "alt": alt,
            "app": app,
            "app_version": app_version,
            "captured_at": captured_at,
            "capture_method": capture_method,
            "capture_source": capture_source,
            "target_pages": [page],
            "sha256": digest,
            "bytes": byte_count,
            "width": width,
            "height": height,
            "synthetic_data": True,
            "contains_sensitive": False,
        }
        old_item = old_items.get(f"screen-{number}", {})
        if not source.exists() and old_item.get("requires_recapture_for_release") is True:
            item["requires_recapture_for_release"] = True
            item["recapture_reason"] = old_item.get("recapture_reason", "release recapture required")
        items.append(item)
    manifest = {"schema": "boi-local-guide-media/v1", "guide_release": GUIDE_RELEASE, "items": items}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"ok": True, "output_dir": str(output_dir), "items": len(items)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
