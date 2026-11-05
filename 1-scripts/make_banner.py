#!/usr/bin/env python3
"""Render a Model Releases banner: hill-climb mark, gradient title, and chips or a subtitle.

Usage:
  python 1-scripts/make_banner.py --title "Model Releases" --chips Select Optimize Scale --out .github/images/banner.png
  python 1-scripts/make_banner.py --title "MAI-Transcribe-2" --subtitle "Speaker-aware transcription" --out .github/images/banners/mai-transcribe-2.png
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
LOGO = ROOT / ".github/images/logo.png"
FONTS = ROOT / "1-scripts/fonts"
S = 2  # supersample factor for smooth edges
NAVY, INDIGO, BLUE, PURPLE = (32, 24, 91), (79, 70, 229), (33, 150, 243), (124, 58, 237)


def white_to_alpha(img: Image.Image) -> Image.Image:
    arr = np.array(img.convert("RGBA")).astype(float)
    rgb, alpha = arr[..., :3], arr[..., 3] / 255
    new_alpha = np.clip((255 - rgb.min(axis=2)) / 255, 0, 1) * alpha
    safe = np.where(new_alpha > 0, new_alpha, 1)[..., None]
    rgb = np.clip((rgb - 255 * (1 - safe)) / safe, 0, 255)
    return Image.fromarray(np.dstack([rgb, new_alpha * 255]).astype("uint8"), "RGBA")


def lerp(c0, c1, t):
    return tuple(round(a + (b - a) * t) for a, b in zip(c0, c1))


def gradient(w, h, stops):
    xs = np.linspace(0, 1, w)
    out = np.zeros((h, w, 3))
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        m = (xs >= p0) & (xs <= p1)
        t = ((xs[m] - p0) / (p1 - p0))[None, :, None]
        out[:, m] = np.array(c0) * (1 - t) + np.array(c1) * t
    return Image.fromarray(out.astype("uint8"), "RGB")


def fit_font(draw, text, name, size, max_w):
    while size > 20 * S:
        font = ImageFont.truetype(str(FONTS / name), size)
        if draw.textlength(text, font=font) <= max_w:
            return font
        size -= 4 * S
    return ImageFont.truetype(str(FONTS / name), size)


def render(title: str, chips: list[str], subtitle: str, height: int) -> Image.Image:
    W, H = 1600 * S, height * S
    yy, xx = np.mgrid[0:H, 0:W]
    t = np.clip((xx / W) * 0.75 + (yy / H) * 0.25, 0, 1)[..., None]
    bg = np.array([252, 252, 255]) * (1 - t) + np.array([236, 232, 255]) * t
    bg = bg * (1 - t * 0.4) + np.array([226, 240, 255]) * (t * 0.4)
    banner = Image.fromarray(bg.astype("uint8"), "RGB").convert("RGBA")

    # Contour lines and a dot grid hint at terrain to climb.
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for k in range(9):
        pts = [
            (x, H * (1.08 - 0.08 * k) - H * 0.55 * ((x / W) ** 1.6) + 18 * S * math.sin(x / W * 7 + k * 0.6))
            for x in range(0, W + 1, 8 * S)
        ]
        d.line(pts, fill=lerp(BLUE, PURPLE, k / 8) + (34,), width=2 * S)
    for gx in range(W // 2, W, 34 * S):
        for gy in range(20 * S, H, 34 * S):
            a = int(40 * (gx - W / 2) / (W / 2))
            d.ellipse((gx - 2 * S, gy - 2 * S, gx + 2 * S, gy + 2 * S), fill=INDIGO + (a,))

    # The climb: each kept step goes up.
    steps = [(0.875, 0.82), (0.900, 0.70), (0.920, 0.73), (0.940, 0.56), (0.958, 0.47), (0.972, 0.31), (0.985, 0.18)]
    pts = [(u * W, v * H) for u, v in steps]
    d.line(pts, fill=PURPLE + (110,), width=4 * S, joint="curve")
    for i, (px, py) in enumerate(pts):
        r = (7 if i == len(pts) - 1 else 5) * S
        d.ellipse((px - r, py - r, px + r, py + r), fill=lerp(BLUE, PURPLE, i / (len(pts) - 1)) + (200,),
                  outline=(255, 255, 255, 230), width=2 * S)
    banner.alpha_composite(layer)

    mark = white_to_alpha(Image.open(LOGO).crop((52, 52, 575, 473)))
    mark_h = H - 90 * S
    mark = mark.resize((round(mark.width * mark_h / mark.height), mark_h), Image.LANCZOS)
    mx, my = 80 * S, (H - mark_h) // 2
    glow = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    ImageDraw.Draw(glow).ellipse((mx - 10 * S, my + 10 * S, mx + mark.width + 10 * S, my + mark_h + 10 * S),
                                 fill=(255, 255, 255, 230))
    banner.alpha_composite(glow.filter(ImageFilter.GaussianBlur(40 * S)))
    banner.alpha_composite(mark, (mx, my))

    d = ImageDraw.Draw(banner)
    text_x = mx + mark.width + 64 * S
    max_w = int(0.86 * W) - text_x
    title_font = fit_font(d, title, "Poppins-Bold.ttf", (108 if height >= 340 else 92) * S, max_w)
    tb = d.textbbox((0, 0), title, font=title_font)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    second_h = 70 * S
    title_y = (H - th - 34 * S - second_h) // 2
    tmask = Image.new("L", (tw, th), 0)
    ImageDraw.Draw(tmask).text((-tb[0], -tb[1]), title, font=title_font, fill=255)
    banner.paste(gradient(tw, th, [(0, NAVY), (0.55, INDIGO), (1, PURPLE)]), (text_x, title_y), tmask)

    line_y = title_y + th + 34 * S
    if chips:
        chip_font = ImageFont.truetype(str(FONTS / "Poppins-SemiBold.ttf"), 34 * S)
        colors = [BLUE, INDIGO, PURPLE]
        cx = text_x
        for i, word in enumerate(chips):
            col = colors[i % len(colors)]
            wb = d.textbbox((0, 0), word, font=chip_font)
            cw, ch = wb[2] - wb[0] + 44 * S, wb[3] - wb[1] + 28 * S
            chip = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(chip).rounded_rectangle((cx, line_y, cx + cw, line_y + ch), radius=ch // 2,
                                                   fill=(255, 255, 255, 215), outline=col + (255,), width=3 * S)
            banner.alpha_composite(chip)
            d.text((cx + 22 * S - wb[0], line_y + 14 * S - wb[1]), word, font=chip_font, fill=col)
            cx += cw
            if i < len(chips) - 1:
                ay = line_y + ch // 2
                d.line((cx + 14 * S, ay, cx + 46 * S, ay), fill=(150, 140, 200), width=3 * S)
                d.polygon([(cx + 46 * S, ay - 9 * S), (cx + 60 * S, ay), (cx + 46 * S, ay + 9 * S)], fill=(150, 140, 200))
                cx += 74 * S
    elif subtitle:
        sub_font = fit_font(d, subtitle, "Poppins-Medium.ttf", 40 * S, max_w)
        sb = d.textbbox((0, 0), subtitle, font=sub_font)
        d.text((text_x - sb[0], line_y - sb[1] + 8 * S), subtitle, font=sub_font, fill=(88, 80, 140))

    bar_h = 10 * S
    banner.paste(gradient(W, bar_h, [(0, BLUE), (0.5, INDIGO), (1, PURPLE)]), (0, H - bar_h))
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, W - 1, H - 1), 32 * S, fill=255)
    banner.putalpha(mask)
    return banner.resize((W // S, H // S), Image.LANCZOS)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--title", required=True)
    ap.add_argument("--chips", nargs="*", default=[], help="Short words shown as linked chips")
    ap.add_argument("--subtitle", default="", help="One line under the title (ignored when --chips is set)")
    ap.add_argument("--height", type=int, default=300, help="360 for the README, 300 for notebooks")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    render(args.title, args.chips, args.subtitle, args.height).save(out, optimize=True)
    print(out.relative_to(ROOT))


if __name__ == "__main__":
    main()
