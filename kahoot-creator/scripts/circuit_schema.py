"""Draws a circuit diagram with a transparent background for Kahoot (PNG 1200 x 675).

Components: L (lamp), R (resistor), M (motor), D (LED), followed by an optional label.
In labels and formulas, _ makes a subscript and ^ a superscript (U_1, 10^{6}).
--top alone gives a series circuit; --top and --mid give two branches in
parallel. Several components on one branch are in series with each other.
--nodes places two labels on the left and right nodes.

Examples:
  python circuit_schema.py --top "L:L_1 L:L_2" --out serie.png
  python circuit_schema.py --top "L R" --mid "M" --out mixte.png
  python circuit_schema.py --top "R:R_1" --mid "R:R_2" --nodes A,B --out noeuds.png
  python circuit_schema.py --top "L:L_1" --mid "L:L_2" --formula "I = I_1 + I_2" --out q.png
"""
import argparse
import re
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1200, 675
INK = (30, 30, 46, 255)
RED = (200, 30, 30, 255)
LW = 12
LEFT, RIGHT, TOP, MID, BOTTOM = 220, 980, 110, 310, 560
HALF = {"L": 66, "M": 66, "R": 85, "D": 60}


def font(size):
    return ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", size)


def segments(text):
    """Splits U_1 or 10^{6} into normal, subscript and superscript parts."""
    parts = []
    pos = 0
    for m in re.finditer(r"([_^])(\{[^}]*\}|.)", text):
        parts.append((text[pos:m.start()], ""))
        parts.append((m.group(2).strip("{}"), m.group(1)))
        pos = m.end()
    parts.append((text[pos:], ""))
    return [p for p in parts if p[0]]


def centered(g, xy, text, f, fill=INK, loader=None):
    """Writes centered text; _ makes a subscript and ^ a superscript."""
    loader = loader or font
    small = loader(int(f.size * 0.65))
    parts = segments(text)
    width = sum(g.textlength(t, font=small if k else f) for t, k in parts)
    x = xy[0] - width / 2
    baseline = xy[1] + f.size * 0.36
    shift = {"": 0, "_": f.size * 0.2, "^": -f.size * 0.42}
    for t, k in parts:
        current = small if k else f
        g.text((x, baseline + shift[k]), t, fill=fill, font=current, anchor="ls")
        x += g.textlength(t, font=current)


def component(g, kind, x, y):
    if kind == "L":
        r = HALF["L"]
        k = int(r * 0.7)
        g.ellipse([x - r, y - r, x + r, y + r], outline=INK, width=LW)
        g.line([(x - k, y - k), (x + k, y + k)], fill=INK, width=LW)
        g.line([(x - k, y + k), (x + k, y - k)], fill=INK, width=LW)
    elif kind == "M":
        r = HALF["M"]
        g.ellipse([x - r, y - r, x + r, y + r], outline=INK, width=LW)
        centered(g, (x, y), "M", font(72))
    elif kind == "D":
        g.line([(x - 60, y), (x - 40, y)], fill=INK, width=LW)
        g.line([(x + 40, y), (x + 60, y)], fill=INK, width=LW)
        g.polygon([(x - 40, y - 48), (x - 40, y + 48), (x + 40, y)], outline=INK, width=LW)
        g.line([(x + 40, y - 52), (x + 40, y + 52)], fill=INK, width=LW)
        for dx in (0, 34):
            g.line([(x + dx - 14, y - 58), (x + dx + 20, y - 92)], fill=INK, width=7)
            g.polygon([(x + dx + 28, y - 100), (x + dx + 6, y - 94), (x + dx + 22, y - 78)], fill=INK)
    else:
        g.rectangle([x - HALF["R"], y - 36, x + HALF["R"], y + 36], outline=INK, width=LW)


def branch(g, y, comps):
    """Spreads the components along a horizontal wire, with no wire through them."""
    parsed = [c.split(":") for c in comps]
    n = len(parsed)
    step = (RIGHT - LEFT) / (n + 1)
    x0 = LEFT
    for i, item in enumerate(parsed):
        kind = item[0]
        x = int(LEFT + step * (i + 1))
        g.line([(x0, y), (x - HALF[kind], y)], fill=INK, width=LW)
        component(g, kind, x, y)
        if len(item) > 1:
            label = font(48)
            width = g.textlength(item[1].replace("_", ""), font=label)
            if n >= 3:
                centered(g, (x, y + HALF[kind] + 40), item[1], label)
            else:
                centered(g, (x + HALF[kind] + 16 + width / 2, y - 42), item[1], label)
        x0 = x + HALF[kind]
    g.line([(x0, y), (RIGHT, y)], fill=INK, width=LW)


def generator(g):
    cx = (LEFT + RIGHT) // 2
    g.line([(LEFT, BOTTOM), (cx - 30, BOTTOM)], fill=INK, width=LW)
    g.line([(cx + 30, BOTTOM), (RIGHT, BOTTOM)], fill=INK, width=LW)
    g.line([(cx + 30, BOTTOM - 85), (cx + 30, BOTTOM + 85)], fill=RED, width=14)
    g.line([(cx - 30, BOTTOM - 42), (cx - 30, BOTTOM + 42)], fill=INK, width=14)
    centered(g, (cx + 72, BOTTOM - 62), "+", font(64), RED)
    centered(g, (cx - 72, BOTTOM - 62), "−", font(64))


def with_halo(image, size=17):
    """Adds a white outline: outside the light panel, the Kahoot background is purple."""
    alpha = image.getchannel("A").filter(ImageFilter.MaxFilter(size))
    halo = Image.new("RGBA", image.size, (255, 255, 255, 255))
    halo.putalpha(alpha)
    halo.alpha_composite(image)
    return halo


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--top", required=True, help='components of the top branch, e.g. "L:L1 R"')
    parser.add_argument("--mid", help="components of the second branch (parallel circuit)")
    parser.add_argument("--nodes", help="labels of the left and right nodes, e.g. A,B")
    parser.add_argument("--formula", help="general relation shown in the circuit")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    image = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(image)
    g.line([(LEFT, TOP), (LEFT, BOTTOM)], fill=INK, width=LW)
    g.line([(RIGHT, TOP), (RIGHT, BOTTOM)], fill=INK, width=LW)
    branch(g, TOP, args.top.split())
    if args.mid:
        branch(g, MID, args.mid.split())
        for x in (LEFT, RIGHT):
            g.ellipse([x - 16, MID - 16, x + 16, MID + 16], fill=INK)
    generator(g)
    if args.nodes:
        a, b = args.nodes.split(",")
        centered(g, (LEFT - 55, MID), a, font(60))
        centered(g, (RIGHT + 55, MID), b, font(60))
    if args.formula:
        xy = (395, 435) if args.mid else ((LEFT + RIGHT) // 2, 335)
        centered(g, xy, args.formula, font(60 if args.mid else 70))
    with_halo(image).save(args.out)
    print(args.out)


if __name__ == "__main__":
    main()
