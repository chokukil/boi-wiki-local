#!/usr/bin/env python3
"""Build annotated WebP screenshots and their deterministic guide manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

GUIDE_RELEASE = "3.2.0"
MAX_WIDTH = 1760
MAX_BYTES = 600 * 1024

SPECS = [
    ("01", "explorer-repository", "File Explorer에서 Windows boi-wiki-local 저장소와 setup.cmd를 확인하는 화면", "File Explorer", "Windows 11", "10-install-repository.md", (0.13, 0.12, 0.50, 0.91)),
    ("02", "notepad-markdown", "Windows 메모장에서 OKF 0.1과 BoI Profile 0.1-local Markdown을 여는 화면", "Notepad", "Windows 11", "26-no-obsidian.md", (0.01, 0.12, 0.58, 0.92)),
    ("03", "vault-manager", "Obsidian Vault Manager에서 0000000 Local Private 경로를 확인하는 화면", "Obsidian", "1.13.4", "30-obsidian-install-and-vault.md", (0.01, 0.04, 0.35, 0.49)),
    ("05", "obsidian-properties", "Obsidian Properties에서 OKF 0.1과 BoI Profile 0.1-local을 확인하는 화면", "Obsidian", "1.13.4", "21-okf-and-boi-profile.md", (0.36, 0.16, 0.96, 0.96)),
    ("06", "immutable-capture", "잠긴 Local capture의 source_sha256과 source_immutability를 확인하는 화면", "Obsidian", "1.13.4", "23-capture-distill-review.md", (0.36, 0.50, 0.96, 0.82)),
    ("07", "distilled-provenance", "정제 지식에서 generated_from과 구조화된 source_refs를 확인하는 화면", "Obsidian", "1.13.4", "23-capture-distill-review.md", (0.36, 0.45, 0.96, 0.72)),
    ("09", "backlinks-outgoing", "정제 지식의 Backlinks 패널과 연결된 원문을 확인하는 화면", "Obsidian", "1.13.4", "31-obsidian-core-settings.md", (0.72, 0.05, 0.99, 0.52)),
    ("10", "filtered-graph", "Obsidian Graph의 필터 패널과 Local Wiki 연결 구조를 확인하는 화면", "Obsidian", "1.13.4", "31-obsidian-core-settings.md", (0.34, 0.04, 0.71, 0.96)),
    ("11", "properties-bases", "Obsidian Bases가 Markdown Properties를 목록으로 보여주는 화면", "Obsidian", "1.13.4", "31-obsidian-core-settings.md", (0.34, 0.05, 0.71, 0.97)),
    ("12", "core-plugins", "Obsidian 설정에서 Core plugins 목록을 확인하는 화면", "Obsidian", "1.13.4", "31-obsidian-core-settings.md", (0.01, 0.05, 0.25, 0.97)),
    ("13", "mode-matrix", "Obsidian과 MCP 구성에 따른 가능 작업과 금지 작업 표를 보는 화면", "Obsidian", "1.13.4", "52-mode-matrix.md", (0.35, 0.35, 0.70, 0.99)),
    ("14", "team-promotion-preview", "Team promotion preview에서 scope reviewer hash와 미승인 상태를 확인하는 화면", "Obsidian", "1.13.4", "51-promotion-package.md", (0.35, 0.04, 0.70, 0.96)),
    ("15", "organization-knowledge-loop", "Local capture에서 검토와 승인 후 조직 지식으로 이어지는 운영 루프 화면", "Obsidian", "1.13.4", "53-organization-knowledge-loop.md", (0.35, 0.25, 0.70, 0.98)),
    ("35", "golden-journey-home", "Obsidian 1.13.4에서 sanitized Agentic AI Golden Journey 홈과 공개 파일 트리를 보는 화면", "Obsidian", "1.13.4", ["00-start-here.md", "32-obsidian-golden-journey.md"], (0.02, 0.05, 0.98, 0.96)),
    ("36", "t0-t1-query-compare", "동일 Query의 T0 기준 답변과 T1 업데이트 후보 답변을 Obsidian 분할 화면에서 비교하는 화면", "Obsidian", "1.13.4", "32-obsidian-golden-journey.md", (0.02, 0.05, 0.98, 0.96)),
    ("37", "query-diff-review-queue", "query diff와 사람 검토가 필요한 review queue를 함께 보는 Obsidian 화면", "Obsidian", "1.13.4", "32-obsidian-golden-journey.md", (0.02, 0.05, 0.98, 0.96)),
    ("38", "bases-canvas-local-graph", "공개 Golden Journey의 Canvas, Bases와 Graph 탐색 결과를 모은 실제 Obsidian 화면", "Obsidian", "1.13.4", "32-obsidian-golden-journey.md", (0.01, 0.02, 0.99, 0.98)),
    ("39", "quickadd-common-source-preview", "QuickAdd와 Web Clipper가 같은 공통 source folder를 쓰는 설치 preview를 Obsidian에서 보는 화면", "Obsidian", "1.13.4", "32-obsidian-golden-journey.md", (0.17, 0.07, 0.98, 0.92)),
    ("40", "web-clip-raw-candidate", "공개 합성 Web Clipper 원문과 OKF 0.1 + BoI Profile 0.1-local 후보를 분리해 보는 Obsidian 화면", "Obsidian", "1.13.4", "32-obsidian-golden-journey.md", (0.01, 0.05, 0.99, 0.97)),
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
        original_width = None
        original_height = None
        if source.exists():
            with Image.open(source) as original:
                original_width, original_height = original.size
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
        capture_method = "windows-graphics-capture"
        capture_source = "Windows application window composite" if number == "38" else "Windows application window"
        old_item = old_items.get(f"screen-{number}", {})
        item = {
            "id": f"screen-{number}",
            "file": destination.name,
            "alt": alt,
            "app": app,
            "app_version": app_version,
            "captured_at": captured_at,
            "capture_method": capture_method,
            "capture_source": capture_source,
            "target_pages": page if isinstance(page, list) else [page],
            "sha256": digest,
            "bytes": byte_count,
            "width": width,
            "height": height,
            "synthetic_data": True,
            "synthetic_ui": False,
            "readability_verified": True,
            "contains_sensitive": False,
            "local_private_included": False,
        }
        if original_width is None or original_height is None:
            original_width = old_item.get("original_width")
            original_height = old_item.get("original_height")
        if original_width is not None and original_height is not None:
            item["original_width"] = original_width
            item["original_height"] = original_height
        items.append(item)
    manifest = {"schema": "boi-local-guide-media/v1", "guide_release": GUIDE_RELEASE, "items": items}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"ok": True, "output_dir": str(output_dir), "items": len(items)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
