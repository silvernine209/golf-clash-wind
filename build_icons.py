#!/usr/bin/env python3
"""Generate PWA icons (192x192 and 512x512 PNG) plus an SVG source.
Design: dark green background, white golf ball with concentric rings."""
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).parent / "icons"
ROOT.mkdir(exist_ok=True)

GREEN = (15, 87, 53)         # bg
BALL  = (245, 245, 245)      # off-white
RING  = (220, 220, 220)      # ring strokes
BULL  = (231, 76, 60)        # bullseye dot
EDGE  = (40, 60, 50)         # outer edge


def render(size: int) -> Image.Image:
    img = Image.new("RGB", (size, size), GREEN)
    d = ImageDraw.Draw(img)
    pad = int(size * 0.05)
    # outer rounded square edge
    # (use circle for simplicity)
    d.ellipse([pad, pad, size - pad, size - pad], fill=BALL, outline=EDGE,
              width=max(2, size // 96))
    cx = cy = size // 2
    # 4 concentric rings + bullseye
    max_r = (size - 2 * pad) // 2 - max(4, size // 64)
    for i, frac in enumerate([0.85, 0.65, 0.45, 0.25]):
        r = int(max_r * frac)
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  outline=RING, width=max(2, size // 96))
    # red bullseye dot
    rb = max(3, size // 24)
    d.ellipse([cx - rb, cy - rb, cx + rb, cy + rb], fill=BULL)
    return img


for s in (192, 512):
    render(s).save(ROOT / f"icon-{s}.png", optimize=True)

# A tiny SVG source for browsers that prefer it
SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect width="512" height="512" fill="#0F5735"/>
  <circle cx="256" cy="256" r="216" fill="#F5F5F5" stroke="#28443C" stroke-width="6"/>
  <g fill="none" stroke="#DCDCDC" stroke-width="6">
    <circle cx="256" cy="256" r="184"/>
    <circle cx="256" cy="256" r="140"/>
    <circle cx="256" cy="256" r="96"/>
    <circle cx="256" cy="256" r="54"/>
  </g>
  <circle cx="256" cy="256" r="22" fill="#E74C3C"/>
</svg>
"""
(ROOT / "icon.svg").write_text(SVG)
print("Wrote icons/icon-192.png, icon-512.png, icon.svg")
