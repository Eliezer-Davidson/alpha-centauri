#!/usr/bin/env python3
"""A fit gauge for the dimensions THIS design actually depends on.

    edu/.cadenv/bin/python cad/tonypi_tall/fit_gauge.py

Printing one of each part tells you what fits. This tells you BY HOW MUCH, and
in which direction, which is the part that lets the CAD be corrected instead of
guessed at. ~20 minutes and a few grams.

Four things it measures:
  1. servo channel — a ladder of clear widths straddling DESIGN_CLEAR, which is
     derived below from REINF_WALL rather than written down (21.64 mm at the
     current wall). Whichever slot the LX-824HV first slides into is the real
     minimum, and the difference from DESIGN_CLEAR is the compensation
     REINF_WALL needs.
  2. holes — the four diameters the design relies on, printed through 5 mm.
  3. walls — free-standing 2.52 and 1.89 mm walls to caliper. Slicers hit wall
     thickness well; printers do not always agree.
  4. shrinkage — the plate is exactly 110.00 x 56.00 x 5.00 mm. Caliper it.

Print it in the SAME material and nozzle as the real parts. Tolerance is a
property of the material+machine+orientation, not of the machine alone.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

from build123d import (  # noqa: E402
    Axis, Box, Cylinder, Plane, Pos, export_step, export_stl,
)
import tall_constants as C  # noqa: E402

SERVO_W = 20.14          # measured from the vendor CAD, servo_envelope.py
DESIGN_CLEAR = 25.00 - 2 * C.REINF_WALL      # what 短U actually offers

PLATE = (110.0, 56.0, 5.0)
CH_H, CH_Y0, CH_Y1 = 18.0, -28.0, 2.0        # channel block: full-depth slots
RIB = 3.0

# ladder straddling the design value, so the answer is bracketed either way
WIDTHS = [round(DESIGN_CLEAR - 0.6, 2), round(DESIGN_CLEAR - 0.2, 2),
          round(DESIGN_CLEAR, 2), round(DESIGN_CLEAR + 0.4, 2)]
HOLES = [3.10, 3.90, 7.00, 8.20]             # M3 clear, M3 loose, access, hub

px, py, pz = PLATE
g = Pos(0, 0, pz / 2) * Box(px, py, pz)

# ---- channel block with the width ladder -----------------------------------
span = sum(WIDTHS) + RIB * (len(WIDTHS) + 1)
blk_x0 = -span / 2
blk = Pos(blk_x0 + span / 2, (CH_Y0 + CH_Y1) / 2, pz + CH_H / 2) * Box(
    span, CH_Y1 - CH_Y0, CH_H)
g = g + blk

x = blk_x0 + RIB
slots = []
for w in WIDTHS:
    cut = Pos(x + w / 2, (CH_Y0 + CH_Y1) / 2, pz + CH_H / 2 + 1) * Box(
        w, (CH_Y1 - CH_Y0) + 4, CH_H + 4)          # through, open top+both ends
    g = g - cut
    slots.append((round(x + w / 2, 2), w))
    x += w + RIB

# ---- hole strip ------------------------------------------------------------
hx = -46.0
hole_pos = []
for d in HOLES:
    g = g - Pos(hx, 15.0, pz / 2) * Cylinder(d / 2, pz + 4)
    hole_pos.append((hx, d))
    hx += max(14.0, d + 9.0)

# ---- free-standing wall witnesses ------------------------------------------
walls = [(C.WEB_WALL, 26.0), (C.REINF_WALL, 40.0)]
for t, wx in walls:
    g = g + Pos(wx, 15.0, pz + 7.5) * Box(t, 22.0, 15.0)

# a single asymmetric notch marks the DESIGN slot (3rd), so the ladder can
# never be read backwards off the printed part
g = g - Pos(slots[2][0], CH_Y1 - 1.0, pz + CH_H) * Box(4.0, 3.0, 3.0)

g = g.clean()
bb = g.bounding_box()

DST = os.path.join(REPO, "edu/print_files_tall")
step = os.path.join(DST, "step", "fit_gauge.step")
stl = os.path.join(DST, "stl", "fit_gauge.stl")
export_step(g, step)
export_stl(g, stl, tolerance=0.01)

print(f"fit_gauge  {bb.size.X:.2f} x {bb.size.Y:.2f} x {bb.size.Z:.2f} mm   "
      f"{g.volume/1000:.2f} cm3   solids {len(g.solids())}")
print(f"  plate reference: {px:.2f} x {py:.2f} x {pz:.2f} mm (caliper all three)")
print(f"  servo is {SERVO_W:.2f} mm wide; slot ladder (notch = design value):")
for i, (cx, w) in enumerate(slots, 1):
    tag = "  <- DESIGN (notched)" if abs(w - DESIGN_CLEAR) < 1e-6 else ""
    print(f"    slot {i}  clear {w:6.2f}   margin {(w-SERVO_W)/2:+.2f} mm/side{tag}")
print(f"  holes: {', '.join(f'Ø{d:.2f}' for d in HOLES)}")
print(f"  walls: {C.WEB_WALL} mm and {C.REINF_WALL} mm free-standing")
print(f"  -> {step}\n  -> {stl}")
