#!/usr/bin/env python3
"""Stock vs TALL, side by side at ONE shared scale.

    edu/.cadenv/bin/python cad/tonypi_tall/compare_sheet.py

The per-part hero sheets auto-fit each part to its tile, which is exactly what
hides the change: a 63 mm strap and a 73 mm strap fill the frame identically.
Here both members of a pair share a mm-per-pixel and sit on a common floor, so
the growth is the thing you see rather than something you read in a caption.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "edu/tools"))
sys.path.insert(0, HERE)

from PIL import Image, ImageDraw  # noqa: E402
import hero_render as H  # noqa: E402
import tall_constants as C  # noqa: E402
import vendor_paths  # noqa: E402

STEP_T = os.path.join(REPO, "edu/print_files_tall/step")
STEP_S = vendor_paths.stock_step_dir()
OUT = os.path.join(REPO, "edu/print_files_tall/renders/hero")

ISO = ("iso", 24, -58)
LEG_ST, STRAP_ST, SHORTU_MID, HALF = 23.5, 19.0, 19.25, 6.0

PAIRS = [
    dict(stock="长U支架", tall="长U支架_tall", up="y", view=ISO,
         title="长U支架 — leg / arm link",
         delta=f"64.5 → 78.5 mm   (+{C.LEG_LINK_EXT:.0f} mm, ×2 per leg = "
               f"+{2*C.LEG_LINK_EXT:.0f} mm of robot)   8.15 → 16.70 cm³",
         hl=[f"y:{C.LEG_CLOSE_LO}:{C.LEG_CLOSE_HI}", f"y:{LEG_ST}:{LEG_ST+C.LEG_LINK_EXT}"]),
    dict(stock="脚板", tall="脚板_platform", up="y", view=("iso", 30, -58),
         title="脚板 — foot plate → platform boot",
         delta=f"63×123×2 → {C.FOOT_W:.0f}×{C.FOOT_L:.0f}×12 mm   "
               f"(width ×1.30, the support polygon grows faster than the CoM)"
               f"   12.38 → 112.21 cm³",
         hl=["y:-10:0"]),
    dict(stock="一字支架", tall="一字支架_tall", up="z", view=ISO,
         title="一字支架 — flat strap",
         delta=f"63 → {63+C.STRAP_EXT:.0f} mm   (+{C.STRAP_EXT:.0f} mm)   "
               f"2.55 → 3.05 cm³",
         hl=[f"x:{STRAP_ST}:{STRAP_ST+C.STRAP_EXT}"]),
    dict(stock="短U支架", tall="短U支架_tall_closed", up="y", view=ISO,
         title="短U支架 — joint bracket → closed sides  (CONCEPT)",
         delta=f"same envelope, open U → closed box   5.98 → 8.34 cm³ at {C.REINF_WALL:.2f} mm wall   · 0.54 mm/side on the servo — TEST-FIT FIRST",
         hl=[f"y:{SHORTU_MID-HALF}:{SHORTU_MID+HALF},z:10:12.5",
             f"y:{SHORTU_MID-HALF}:{SHORTU_MID+HALF},z:-12.5:-10"]),
]

PX, SS, PAD = 620, 3, 20
rows = []
for p in PAIRS:
    a = H.Part(os.path.join(STEP_S, f"{p['stock']}.step"), [], p["up"], 0.015)
    b = H.Part(os.path.join(STEP_T, f"{p['tall']}.step"), p["hl"], p["up"], 0.015)
    ex = max(a.extents([p["view"]])[0], b.extents([p["view"]])[0]) * 1.12
    ey = max(a.extents([p["view"]])[1], b.extents([p["view"]])[1]) * 1.16
    mm2px = PX / ex                       # ONE scale for both members
    th = max(150, int(round(ey * mm2px)))
    _, elev, azim = p["view"]
    tiles = [a.shot(elev, azim, PX, th, SS, mm2px, anchor="bottom"),
             b.shot(elev, azim, PX, th, SS, mm2px, anchor="bottom")]
    rows.append((p, tiles, th))
    print(f"  {p['stock']:10s} vs {p['tall']:20s}  scale {mm2px:.2f} px/mm")

W = PAD + 2 * (PX + PAD)
head = 92
Ht = head + sum(th + 82 for _, _, th in rows) + PAD
sheet = Image.new("RGB", (W, Ht), H.BG)
d = ImageDraw.Draw(sheet)
d.text((PAD, 24), "TonyPi TALL — stock (left) vs redesigned (right)",
       fill="#f0ebe2", font=H.font(30))
d.text((PAD, 60), "each pair drawn at ONE shared scale, sitting on a common "
                  "floor · orange = material added",
       fill="#a49c8e", font=H.font(15))
y = head
for p, tiles, th in rows:
    for i, t in enumerate(tiles):
        sheet.paste(t, (PAD + i * (PX + PAD), y))
    d.line([(PAD + PX + PAD // 2, y + 6), (PAD + PX + PAD // 2, y + th - 6)],
           fill="#3a332a", width=2)
    d.text((PAD + 4, y + th + 8), p["title"], fill="#f0ebe2", font=H.font(20))
    d.text((PAD + 4, y + th + 36), p["delta"], fill="#a49c8e", font=H.font(14))
    d.text((PAD + PX // 2, y + 4), "STOCK", fill="#8d8578", font=H.font(14),
           anchor="ma")
    d.text((PAD + PX + PAD + PX // 2, y + 4), "TALL", fill="#E0913F",
           font=H.font(14), anchor="ma")
    y += th + 82
out = os.path.join(OUT, "stock_vs_tall.png")
sheet.save(out)
print(f"\n-> {out}  ({sheet.width}x{sheet.height})")
