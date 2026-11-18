"""Adds formulas to a Kahoot illustration, or creates a formula image.

Without --base: PNG with a transparent background, 1200 x 675.
With --base: the image is kept and the formulas are placed on a white
band at the bottom, to stay readable whatever its content.

Examples:
  python formula_card.py --out q4.png --line "E = P · Δt"
  python formula_card.py --out q5.png --line "I = I_1 + I_2" --line "1 kWh = 3,6 · 10^{6} J"
  python formula_card.py --base console.jpg --out q4.png --line "E = P · Δt"
"""
import argparse
from PIL import Image, ImageDraw, ImageFont

from circuit_schema import centered, with_halo

W, H = 1200, 675
INK = (30, 30, 46, 255)
FONTS = ("C:/Windows/Fonts/cambria.ttc", "C:/Windows/Fonts/arial.ttf", "DejaVuSans.ttf")


def load_font(size):
    for path in FONTS:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default(size)


def fit_font(draw, lines, max_w, start):
    """Shrinks the font until the widest line fits."""
    size = start
    while size > 20:
        font = load_font(size)
        if max(draw.textlength(line, font=font) for line in lines) <= max_w:
            return font, size
        size -= 4
    return load_font(size), size


def draw_lines(draw, lines, font, size, top, width):
    gap = int(size * 1.35)
    for i, line in enumerate(lines):
        centered(draw, (width / 2, top + i * gap + size / 2), line, font, INK, load_font)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--line", action="append", required=True, help="one formula line (repeatable)")
    parser.add_argument("--out", required=True, help="output PNG file")
    parser.add_argument("--base", help="image to complete; without it, transparent background")
    args = parser.parse_args()

    if args.base:
        image = Image.open(args.base).convert("RGBA")
        image.thumbnail((W, H))
        canvas = Image.new("RGBA", (W, H), (255, 255, 255, 255))
        canvas.alpha_composite(image, ((W - image.width) // 2, (H - image.height) // 2))
        draw = ImageDraw.Draw(canvas)
        font, size = fit_font(draw, args.line, W - 120, 64)
        band = int(len(args.line) * size * 1.35) + 40
        draw.rectangle([0, H - band, W, H], fill=(255, 255, 255, 235))
        draw_lines(draw, args.line, font, size, H - band + 20, W)
    else:
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)
        font, size = fit_font(draw, args.line, W - 120, 110)
        total = int(len(args.line) * size * 1.35)
        draw_lines(draw, args.line, font, size, (H - total) // 2, W)
        canvas = with_halo(canvas)

    canvas.save(args.out)
    print(args.out)


if __name__ == "__main__":
    main()
