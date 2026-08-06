#!/usr/bin/env python3
"""Build deterministic 1760px synthetic AI chat screens for the user Wiki."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1760, 1120
BG = (246, 247, 250)
SIDEBAR = (239, 241, 245)
TEXT = (31, 35, 42)
MUTED = (93, 101, 114)
ACCENT = (23, 101, 214)
GREEN = (35, 134, 88)
AMBER = (176, 111, 20)
RED = (185, 47, 65)


def font(size: int, bold: bool = False):
    candidates = [
        Path("C:/Windows/Fonts/malgunbd.ttf" if bold else "C:/Windows/Fonts/malgun.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default(size=size)


def wrap(draw: ImageDraw.ImageDraw, text: str, width: int, size: int) -> list[str]:
    result: list[str] = []
    for paragraph in text.splitlines() or [""]:
        current = ""
        for token in paragraph.split(" "):
            proposal = f"{current} {token}".strip()
            if draw.textlength(proposal, font=font(size)) <= width:
                current = proposal
            else:
                if current:
                    result.append(current)
                current = token
        result.append(current)
    return result


def shell(title: str, subtitle: str = "합성 교육 화면 · Local Private"):
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 310, HEIGHT), fill=SIDEBAR)
    draw.text((125, 40), "BoI Wiki Local", fill=TEXT, font=font(28, True))
    draw.text((125, 86), "Harness & Skills", fill=MUTED, font=font(21))
    draw.rounded_rectangle((34, 150, 276, 204), radius=12, fill=(221, 229, 244))
    draw.text((56, 164), "새 대화", fill=ACCENT, font=font(20, True))
    draw.text((350, 38), title, fill=TEXT, font=font(31, True))
    draw.text((350, 86), subtitle, fill=MUTED, font=font(18))
    draw.line((330, 125, 1725, 125), fill=(216, 220, 228), width=2)
    return image, draw


def bubble(draw, y: int, label: str, text: str, *, agent: bool, height: int = 190):
    x1, x2 = (560, 1650) if not agent else (390, 1480)
    fill = (222, 232, 251) if not agent else (255, 255, 255)
    outline = (190, 205, 232) if not agent else (213, 218, 228)
    draw.text((x1, y - 36), label, fill=ACCENT if not agent else GREEN, font=font(18, True))
    draw.rounded_rectangle((x1, y, x2, y + height), radius=18, fill=fill, outline=outline, width=2)
    line_y = y + 28
    for line in wrap(draw, text, x2 - x1 - 56, 23):
        draw.text((x1 + 28, line_y), line, fill=TEXT, font=font(23))
        line_y += 36


def save(image: Image.Image, output: Path, name: str):
    output.mkdir(parents=True, exist_ok=True)
    image.save(output / name, "PNG")


def setup_request(output: Path):
    image, draw = shell("AI에게 BoI Wiki Local 설치 맡기기")
    bubble(draw, 205, "사용자", "이 저장소를 내 BoI Wiki Local Harness로 설정해줘. 먼저 BoI Wiki 호환 문서를 만들 수 있게 하고, Flagship Second Brain도 Local Private로 연결해줘. 원격 업로드는 하지 마.", agent=False, height=210)
    bubble(draw, 515, "AI", "Harness와 Skills, OKF 0.1·BoI Profile 계약을 확인했습니다. 필요한 질문은 최대 세 개입니다. 외부 창을 열거나 Python·Obsidian·MCP를 요구하지 않습니다.", agent=True, height=160)
    save(image, output, "28-agent-setup-request.png")


def preset_choice(output: Path):
    image, draw = shell("어떻게 정리할까요?")
    options = [
        ("1", "알아서 정리", "가치 있는 내용만 기존 지식과 비교해 반영", ACCENT),
        ("2", "정리 전 확인", "변경할 주제를 짧게 보여준 뒤 반영", GREEN),
        ("3", "요청할 때만", "기억해줘·정리해줘라고 말한 경우만 실행", AMBER),
    ]
    y = 215
    for number, title, body, color in options:
        draw.rounded_rectangle((420, y, 1600, y + 170), radius=20, fill="white", outline=color, width=4)
        draw.ellipse((458, y + 48, 526, y + 116), fill=color)
        draw.text((480, y + 60), number, fill="white", font=font(27, True), anchor="mm")
        draw.text((565, y + 34), title + ("  (권장)" if number == "1" else ""), fill=TEXT, font=font(29, True))
        draw.text((565, y + 92), body, fill=MUTED, font=font(22))
        y += 205
    save(image, output, "29-curation-presets.png")


def setup_complete(output: Path):
    image, draw = shell("설정 완료")
    draw.rounded_rectangle((410, 190, 1570, 880), radius=24, fill="white", outline=(208, 216, 226), width=2)
    draw.ellipse((475, 242, 555, 322), fill=GREEN)
    draw.text((515, 282), "OK", fill="white", font=font(24, True), anchor="mm")
    draw.text((590, 250), "Second Brain을 사용할 준비가 됐습니다", fill=TEXT, font=font(31, True))
    rows = [
        ("대화 관리", "가치 있는 내용만 자동 반영"),
        ("자료 폴더", r"C:\Users\0000000\Documents\BoI-Second-Brain-Inbox"),
        ("원본 보존", "켜짐"),
        ("원격 자동 업로드", "꺼짐"),
        ("Obsidian / MCP", "없어도 정상 동작"),
    ]
    y = 365
    for key, value in rows:
        draw.text((485, y), key, fill=MUTED, font=font(22, True))
        draw.text((790, y), value, fill=TEXT, font=font(22))
        draw.line((485, y + 42, 1495, y + 42), fill=(231, 234, 239), width=1)
        y += 82
    draw.rounded_rectangle((475, 800, 1495, 852), radius=12, fill=(232, 246, 239))
    draw.text((500, 814), "첫 사용: 오늘 논의한 결정 중 오래 쓸 내용은 Second Brain에 반영해줘.", fill=GREEN, font=font(20, True))
    save(image, output, "30-zero-ui-setup-complete.png")


def inbox_summary(output: Path):
    image, draw = shell("자료 폴더 정리 결과")
    stats = [
        ("기존 지식 보강", "12", ACCENT),
        ("새로운 주제 생성", "3", GREEN),
        ("이미 반영됨", "28", MUTED),
        ("내용 확인 필요", "2", AMBER),
        ("아직 처리 중", "47", (117, 82, 184)),
    ]
    y = 205
    for label, value, color in stats:
        draw.rounded_rectangle((430, y, 1530, y + 128), radius=18, fill="white", outline=(216, 220, 228), width=2)
        draw.rectangle((430, y, 445, y + 128), fill=color)
        draw.text((490, y + 35), label, fill=TEXT, font=font(27, True))
        draw.text((1450, y + 64), value, fill=color, font=font(37, True), anchor="mm")
        y += 145
    draw.text((430, 965), "원본은 이동·수정·삭제하지 않았고 Local Private로 유지했습니다.", fill=MUTED, font=font(21))
    save(image, output, "31-inbox-curation-summary.png")


def before_after(output: Path):
    image, draw = shell("기존 지식 보강 — 새 파일을 만들지 않음")
    draw.text((400, 165), "변경 전", fill=MUTED, font=font(23, True))
    draw.text((1080, 165), "변경 후", fill=GREEN, font=font(23, True))
    draw.rounded_rectangle((390, 210, 1010, 900), radius=18, fill="white", outline=(215, 220, 229), width=2)
    draw.rounded_rectangle((1050, 210, 1670, 900), radius=18, fill="white", outline=GREEN, width=3)
    left = ["# 주간 검토 원칙", "", "- 금요일에 열린 항목 확인", "- 결정과 근거를 함께 기록", "", "근거: 회의 메모 1건"]
    right = ["# 주간 검토 원칙", "", "- 금요일에 열린 항목 확인", "- 결정과 근거를 함께 기록", "- 보류 항목은 다음 검토일 지정", "", "근거: 회의 메모 2건", "", "변경 이력 보존"]
    for x, lines in ((430, left), (1090, right)):
        y = 260
        for line in lines:
            draw.text((x, y), line, fill=TEXT if line else MUTED, font=font(22, line.startswith("#")))
            y += 54
    draw.rounded_rectangle((1090, 670, 1625, 748), radius=12, fill=(232, 246, 239))
    draw.text((1115, 692), "기존 주제에 새 근거를 추가했습니다", fill=GREEN, font=font(21, True))
    save(image, output, "32-memory-before-after.png")


def duplicate(output: Path):
    image, draw = shell("중복 자료 처리")
    bubble(draw, 205, "AI", "02-weekly-review-copy.pdf는 기존 자료와 SHA256이 같습니다. 새 문서나 링크를 만들지 않았습니다.", agent=True, height=155)
    draw.rounded_rectangle((450, 485, 1510, 760), radius=22, fill="white", outline=(213, 218, 228), width=2)
    draw.text((500, 535), "처리 결과", fill=TEXT, font=font(28, True))
    draw.text((500, 600), "이미 반영됨", fill=ACCENT, font=font(34, True))
    draw.text((500, 670), "원본 유지 · 새 파일 0개 · 기존 지식 변경 0건", fill=MUTED, font=font(22))
    save(image, output, "33-duplicate-already-reflected.png")


def conflict(output: Path):
    image, draw = shell("내용 확인 필요")
    draw.rounded_rectangle((420, 190, 1600, 870), radius=22, fill="white", outline=(216, 220, 228), width=2)
    draw.rounded_rectangle((460, 235, 1560, 320), radius=14, fill=(255, 246, 226))
    draw.text((495, 260), "기존 결정과 새 자료가 충돌해 자동으로 덮어쓰지 않았습니다.", fill=AMBER, font=font(24, True))
    draw.text((470, 380), "기존 지식", fill=MUTED, font=font(21, True))
    draw.text((470, 425), "검토 주기는 매주 금요일", fill=TEXT, font=font(27))
    draw.text((470, 515), "새 자료", fill=MUTED, font=font(21, True))
    draw.text((470, 560), "검토 주기는 격주 목요일", fill=TEXT, font=font(27))
    draw.line((470, 630, 1540, 630), fill=(226, 230, 236), width=2)
    draw.text((470, 675), "다음 확인", fill=RED, font=font(22, True))
    draw.text((470, 725), "어느 결정이 최신인지 확인해 주세요. 확인 전에는 두 근거와 이전 이력을 모두 보존합니다.", fill=TEXT, font=font(22))
    save(image, output, "34-conflict-needs-review.png")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    output = Path(args.output_dir).resolve()
    setup_request(output)
    preset_choice(output)
    setup_complete(output)
    inbox_summary(output)
    before_after(output)
    duplicate(output)
    conflict(output)
    print(f"created seven synthetic AI chat training screens in {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
