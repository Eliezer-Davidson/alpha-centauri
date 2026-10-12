#!/usr/bin/env python3
"""360-degree turntable montage of a CAD part — no GPU, no GL, no viewer.

    edu/.cadenv/bin/python edu/tools/turntable.py part.stl -o out.png -n 12

hero_render.py shoots four fixed hero angles, which is right for "did this edit
land". A turntable is for "what IS this thing" — you cannot read a robot chassis
off one isometric, because every pocket, rail and bore faces a different way.

Reuses hero_render's Part (tessellate -> upright -> crease-keyed) and its light
rig, which is defined in CAMERA space, so every frame around the turn is lit
identically and the shape reads instead of the lighting.

Laid out as a grid rather than hero_render's single row: 12 tiles in one row is
9,000 px wide and unreadable in a terminal or a doc.
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hero_render import BG, NEW, Part, font  # noqa: E402

import numpy as np  # noqa: E402


def turntable(path, out, n=12, elev=22.0, cols=4, px=430, ss=2, tol=0.02,
              up="z", tag=None, highlights=()):
    part = Part(path, highlights=highlights, up=up, tol=tol)

    azims = [i * 360.0 / n for i in range(n)]
    views = [(f"{a:.0f}°", elev, a) for a in azims]

    # ONE shared scale across every frame — a turntable whose subject changes
    # size as it spins is worse than useless, it is misleading.
    ex, ey = part.extents(views)
    ex, ey = ex * 1.10, ey * 1.16
    mm2px = px / ex
    tw, th = px, max(90, int(round(ey * mm2px)))

    tiles = [part.shot(e, a, tw, th, ss, mm2px) for _, e, a in views]

    rows = (n + cols - 1) // cols
    pad, cap = 10, 60
    sheet_w = pad + cols * (tw + pad)
    sheet_h = pad + rows * (th + pad) + cap
    sheet = Image.new("RGB", (sheet_w, sheet_h), BG)
    d = ImageDraw.Draw(sheet)
    fnt, fsm = font(19), font(14)

    for i, tile in enumerate(tiles):
        r, c = divmod(i, cols)
        x = pad + c * (tw + pad)
        y = pad + r * (th + pad)
        sheet.paste(tile, (x, y))
        d.text((x + tw // 2, y + 3), views[i][0], fill="#E0913F", font=fsm,
               anchor="ma")

    label = tag or os.path.splitext(os.path.basename(path))[0]
    s = part.size
    ty = pad + rows * (th + pad)
    d.text((pad + 6, ty), label, fill="#f0ebe2", font=fnt)
    d.text((pad + 6, ty + 26),
           f"{s[0]:.1f} x {s[1]:.1f} x {s[2]:.1f} mm    "
           f"{part.shape.volume / 1000:.1f} cm3    "
           f"{part.n_tri} tri    elev {elev:.0f}°, {n} frames",
           fill="#a49c8e", font=fsm)
    if highlights:
        d.rectangle([sheet_w - 250, ty + 8, sheet_w - 234, ty + 24],
                    fill=tuple((NEW * 255).astype(int)))
        d.text((sheet_w - 226, ty + 7), "material added", fill="#a49c8e",
               font=fsm)

    sheet.save(out)
    print(f"  {label:26s} -> {out}  "
          f"({s[0]:.1f} x {s[1]:.1f} x {s[2]:.1f} mm, {n} frames)")
    return out


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("path")
    p.add_argument("-o", "--out", default=None)
    p.add_argument("-n", "--frames", type=int, default=12)
    p.add_argument("--elev", type=float, default=22.0)
    p.add_argument("--cols", type=int, default=4)
    p.add_argument("--px", type=int, default=430)
    p.add_argument("--ss", type=int, default=2)
    p.add_argument("--tol", type=float, default=0.02)
    p.add_argument("--up", default="z", choices=["x", "y", "z"])
    p.add_argument("--tag", default=None)
    p.add_argument("--highlight", action="append", default=[])
    a = p.parse_args()

    out = a.out or os.path.splitext(a.path)[0] + "_turntable.png"
    turntable(a.path, out, n=a.frames, elev=a.elev, cols=a.cols, px=a.px,
              ss=a.ss, tol=a.tol, up=a.up, tag=a.tag,
              highlights=tuple(a.highlight))
