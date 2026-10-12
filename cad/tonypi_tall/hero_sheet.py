#!/usr/bin/env python3
"""Shaded hero renders of every part the TALL variant actually changes.

    edu/.cadenv/bin/python cad/tonypi_tall/hero_sheet.py

Writes edu/print_files_tall/renders/hero/. Each highlight band below is the
exact geometry the build op created — station+delta for a stretch, the sole
block for the boot, the web plates for a closure — so the orange is a claim
that can be checked against build_all.py, not a paint job.
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
os.makedirs(OUT, exist_ok=True)

LEG_ST = 23.5           # stretch station reported by build_all
STRAP_ST = 19.0
SHORTU_MID = 19.25      # (‑2 + 40.5)/2, the close_span centre
HALF = 6.0              # close_span half-width used for 短U

PARTS = [
    dict(name="长U支架_tall", src=STEP_T, up="y",
         tag="长U支架_tall  ·  leg / arm link  —  THE HEIGHT MOVE",
         sub=f"64.5 → 78.5 mm  (+{C.LEG_LINK_EXT:.0f} at the hole-free band) · box section over y[{C.LEG_CLOSE_LO:.0f},{C.LEG_CLOSE_HI:.0f}], the 31.6 mm the stretch opens BELOW the servo (measured, not assumed)",
         hl=[f"y:{C.LEG_CLOSE_LO}:{C.LEG_CLOSE_HI}", f"y:{LEG_ST}:{LEG_ST + C.LEG_LINK_EXT}"]),
    dict(name="脚板_platform", src=STEP_T, up="y",
         tag="脚板_platform  ·  the platform boot",
         sub=f"63×123×2 → {C.FOOT_W:.0f}×{C.FOOT_L:.0f}×12 mm  "
             f"({C.SOLE_H:.0f} mm sole, vendor plate kept 1:1 as the top skin, "
             f"16 screw-access bores)",
         hl=["y:-10:0"]),
    dict(name="mohawk_crest", src=STEP_T, up="y",
         tag="mohawk_crest  ·  NEW PART  —  spartan crest",
         sub=f"{C.CREST_N_SPIKES} spikes, {C.CREST_L:.0f} mm long, "
             f"{C.CREST_H:.0f} mm tall · clip-on saddle + zip-tie tabs · "
             f"saddle W={C.HEAD_W:.0f} is a PLACEHOLDER (no head CAD)",
         hl=["all"]),
    dict(name="一字支架_tall", src=STEP_T, up="z",
         tag="一字支架_tall  ·  flat strap",
         sub=f"63 → {63 + C.STRAP_EXT:.0f} mm (+{C.STRAP_EXT:.0f} at a "
             f"hole-free band)",
         hl=[f"x:{STRAP_ST}:{STRAP_ST + C.STRAP_EXT}"]),
    dict(name="短U支架_tall_closed", src=STEP_T, up="y",
         tag="短U支架_tall_closed  ·  CONCEPT — the \"add sides\" ask",
         sub=f"closed sides mid-span, 5.98 → 8.34 cm³ at {C.REINF_WALL:.2f} mm wall · the servo fills this bracket end to end, leaving 0.54 mm/side — TEST-FIT a real LX-824HV before printing",
         hl=[f"y:{SHORTU_MID - HALF}:{SHORTU_MID + HALF},z:10:12.5",
             f"y:{SHORTU_MID - HALF}:{SHORTU_MID + HALF},z:-12.5:-10"]),
]

STOCK = {"长U支架": "y", "脚板": "y", "一字支架": "z", "短U支架": "y"}

rows = []
for p in PARTS:
    png = os.path.join(OUT, f"{p['name']}_hero.png")
    H.render(os.path.join(p["src"], f"{p['name']}.step"), png,
             highlights=p["hl"], px=680, ss=3, tol=0.015, tag=p["tag"],
             up=p["up"])
    rows.append((png, p))

print("\nstock counterparts (no highlight, same scale rules):")
for stock, up in STOCK.items():
    H.render(os.path.join(STEP_S, f"{stock}.step"),
             os.path.join(OUT, f"{stock}_stock.png"),
             highlights=[], px=680, ss=3, tol=0.015, up=up,
             tag=f"{stock}  ·  vendor original (unmodified)")

# ------------------------------------------------------- contact sheet
pad = 22
imgs = [Image.open(png) for png, _ in rows]
subs = [p["sub"] for _, p in rows]
W = max(i.width for i in imgs) + pad * 2
head = 78
Ht = head + sum(i.height + 30 + pad for i in imgs) + pad
sheet = Image.new("RGB", (W, Ht), H.BG)
d = ImageDraw.Draw(sheet)
d.text((pad, 22), "TonyPi TALL — the five pieces that change",
       fill="#f0ebe2", font=H.font(30))
d.text((pad, 56), "orange = material this design adds · everything grey is "
                  "vendor geometry, translated but never scaled",
       fill="#a49c8e", font=H.font(15))
y = head
for img, sub in zip(imgs, subs):
    sheet.paste(img, (pad, y))
    d.text((pad + 6, y + img.height + 2), sub, fill="#8d8578", font=H.font(14))
    y += img.height + 30 + pad
out = os.path.join(OUT, "new_pieces.png")
sheet.save(out)
print(f"\ncontact sheet -> {out}  ({sheet.width}x{sheet.height})")
