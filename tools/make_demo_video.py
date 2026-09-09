"""Build a ≤5 min silent slide demo. Contest allows slides + screen text."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "_frames"
W, H = 1920, 1080
BG = (2, 5, 8)
INK = (234, 247, 255)
CYAN = (67, 214, 255)
GREEN = (66, 255, 192)
AMBER = (255, 189, 84)
RED = (255, 107, 122)
MUTED = (134, 161, 179)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in (
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ):
        p = Path(name)
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def slide(path: Path, lines: list[tuple[str, str]]) -> None:
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 8), fill=CYAN)
    y = 120
    for kind, text in lines:
        if kind == "kicker":
            d.text((120, y), text.upper(), fill=CYAN, font=font(22, True))
            y += 56
        elif kind == "h":
            d.text((120, y), text, fill=INK, font=font(54, True))
            y += 88
        elif kind == "sub":
            d.text((120, y), text, fill=MUTED, font=font(28))
            y += 48
        elif kind == "ok":
            d.text((120, y), text, fill=GREEN, font=font(36, True))
            y += 56
        elif kind == "wait":
            d.text((120, y), text, fill=AMBER, font=font(36, True))
            y += 56
        elif kind == "no":
            d.text((120, y), text, fill=RED, font=font(36, True))
            y += 56
        elif kind == "body":
            d.text((120, y), text, fill=INK, font=font(30))
            y += 46
    d.text((120, 1000), "Hood Intelligence, Corp.  ·  patents pending  ·  production_certified = false", fill=MUTED, font=font(20))
    im.save(path)


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    slides = [
        [
            ("kicker", "Agents for Humans  ·  Professional Agents  ·  Strands SDK"),
            ("h", "HIOP Governed Operations Agent"),
            ("sub", "A clerk for commercial building permits."),
            ("sub", "Strands investigates. CRUSHIA decides. Only a fresh PERMIT issues."),
        ],
        [
            ("kicker", "Problem"),
            ("h", "Permit clerks repeat the same loop."),
            ("body", "Look up the application. Decide if this office can issue it."),
            ("body", "Stop when the fee exceeds auto-issue authority."),
            ("body", "Wait for a building official. Then issue — or refuse."),
            ("sub", "An agent that chats about permits is not enough."),
        ],
        [
            ("kicker", "Path 1  ·  $20 OTC wall sign"),
            ("h", "SGN-2026-01102 Harborline"),
            ("ok", "CRUSHIA  PERMIT"),
            ("ok", "Issued  NH-SGN-2026-01102"),
            ("sub", "Within the $25 auto-issue ceiling. Permission Δ = 0."),
        ],
        [
            ("kicker", "Path 2  ·  $7,600 commercial building"),
            ("h", "BLD-2026-08441  ·  1400 Industrial Way"),
            ("wait", "CRUSHIA  PERMIT_WITH_APPROVAL"),
            ("wait", "No permit printed. Approval is a fact, not a permit."),
            ("sub", "PERMIT_WITH_APPROVAL never dispatches."),
        ],
        [
            ("kicker", "Path 2 continued"),
            ("h", "Building official approves."),
            ("body", "Fresh CRUSHIA decision on the same application + amount."),
            ("ok", "CRUSHIA  PERMIT"),
            ("ok", "Issued  NH-BLD-2026-08441"),
        ],
        [
            ("kicker", "Path 3  ·  wrong jurisdiction"),
            ("h", "Riverside Holdings"),
            ("no", "CRUSHIA  DENY"),
            ("no", "No permit. State unchanged."),
        ],
        [
            ("kicker", "Binding  ·  the clerk cannot cheat"),
            ("h", "Tokens are bound to the request."),
            ("no", "Wrong application → refused"),
            ("no", "Replay → refused"),
            ("no", "Approval used as a permit → refused"),
            ("sub", "Every path Fossilized. Permission Δ stays 0."),
        ],
        [
            ("kicker", "Hood Intelligence, Corp."),
            ("h", "Kenneth Wyche"),
            ("body", "founder@hoodintelligence.ai"),
            ("body", "hoodintelligence.ai"),
            ("sub", "Apache-2.0  ·  patents pending"),
            ("sub", "New Strands app for this hackathon. HIOP engines disclosed pre-existing."),
            ("sub", "Not Studio Cinema Control. Not a second HIOP. production_certified = false."),
        ],
    ]
    for i, lines in enumerate(slides, 1):
        slide(OUT_DIR / f"s{i:02d}.png", lines)
    print("frames", len(slides), OUT_DIR)


if __name__ == "__main__":
    main()
