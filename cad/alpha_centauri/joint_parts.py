"""Alpha Centauri — the small parts that carry ALL the handedness (build123d).

    edu/.cadenv/bin/python cad/alpha_centauri/joint_parts.py

Three inserts, ~8 g between them, and they are why the thigh and the calf are
each one part number instead of two:

  horn_adapter      driven side. Seats in the calf lug, bolts to the servo horn.
  bearing_retainer  idle side. Same seat, same three bolts, holds a 608ZZ in.
  bearing_carrier   plugs the THIGH's bore and presents an 8 mm stub for the
                    608's inner race.

Swap which lug gets the adapter and which gets the retainer, and the leg changes
hand. Nothing printed at leg scale has to change. Dingo ships separate left and
right links; this is the alternative.

WHY AN ADAPTER EXISTS AT ALL
----------------------------
A servo horn's bolt circle is ~14-17 mm PCD. Any bearing worth using is 22 mm+
across. So the bolts land INSIDE the bearing's footprint and no single plate can
both bolt to a horn and seat a bearing concentrically -- the first version of
the thigh cut a 17 mm PCD inside a 26 mm bore and removed literally nothing.
The adapter is the piece that spans that gap: horn PCD on its inner face,
retaining PCD on its flange.

THE 608ZZ IS A REAL PART
------------------------
8 x 22 x 7 mm, in the step.parts catalog, a few pence each. The seat diameter
everywhere in this project is 22.0 for exactly that reason -- it is the cheapest
bearing in the world and it sets the interface.
"""

import math
from pathlib import Path
import subprocess
import sys

from build123d import (
    Align,
    BuildPart,
    Box,
    Cylinder,
    Locations,
    Mode,
    export_step,
    export_stl,
)

from thigh import HORN_BOLT, HORN_PCD, JOURNAL_D, WALL
from calf import LUG_T, RETAIN_N, RETAIN_PCD

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "edu/tools"))

# 608ZZ, the interface everything keys off
BRG_ID, BRG_OD, BRG_W = 8.0, 22.0, 7.0

SEAT_D = JOURNAL_D                 # 22.0
PRESS = 0.15                       # printed-into-printed: light, not structural
FLANGE_D = RETAIN_PCD + 9.0        # 36.0, enough meat round each bolt
FLANGE_T = 3.0
M3_PILOT = 2.6
HUB_RELIEF_D = 12.0                # clears the servo's output hub / screw head


def _retain_holes(part_builder, dia, depth, z0=0.0):
    """The three-bolt circle every insert shares."""
    for i in range(RETAIN_N):
        th = math.radians(90 + 360 * i / RETAIN_N)
        with Locations((RETAIN_PCD / 2 * math.cos(th),
                        RETAIN_PCD / 2 * math.sin(th), z0)):
            Cylinder(radius=dia / 2, height=depth,
                     align=(Align.CENTER, Align.CENTER, Align.MIN),
                     mode=Mode.SUBTRACT)


def create_horn_adapter():
    """Driven side. Flange outside the lug, spigot into the seat.

    Built about +Z: the flange sits at z 0..FLANGE_T against the lug's OUTER
    face, and the spigot reaches inward. Print flange-down, no supports.
    """
    with BuildPart() as part:
        Cylinder(radius=FLANGE_D / 2, height=FLANGE_T,
                 align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, 0, FLANGE_T)):
            Cylinder(radius=(SEAT_D - PRESS) / 2, height=LUG_T,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
        # horn bolt circle, through the spigot into the servo horn
        for i in range(4):
            th = math.radians(45 + 90 * i)
            with Locations((HORN_PCD / 2 * math.cos(th),
                            HORN_PCD / 2 * math.sin(th), 0)):
                Cylinder(radius=HORN_BOLT / 2, height=FLANGE_T + LUG_T + 2,
                         align=(Align.CENTER, Align.CENTER, Align.MIN),
                         mode=Mode.SUBTRACT)
        # relief so the horn's own hub and retaining screw are not fouled
        with Locations((0, 0, FLANGE_T + LUG_T - 3.5)):
            Cylinder(radius=HUB_RELIEF_D / 2, height=4.0,
                     align=(Align.CENTER, Align.CENTER, Align.MIN),
                     mode=Mode.SUBTRACT)
        _retain_holes(part, M3_PILOT, FLANGE_T * 2)
    return part.part


def create_bearing_retainer():
    """Idle side. A ring that traps the 608ZZ in the lug seat.

    Deliberately a RING, not a disc: the shaft has to pass through it.
    """
    with BuildPart() as part:
        Cylinder(radius=FLANGE_D / 2, height=FLANGE_T,
                 align=(Align.CENTER, Align.CENTER, Align.MIN))
        # a shallow lip that bears on the bearing's OUTER race only -- never
        # the inner race, or the bearing is preloaded and stops turning
        with Locations((0, 0, FLANGE_T)):
            Cylinder(radius=(SEAT_D - PRESS) / 2, height=1.2,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, 0, FLANGE_T)):
            Cylinder(radius=(BRG_OD - 3.0) / 2, height=4.0,
                     align=(Align.CENTER, Align.CENTER, Align.MIN),
                     mode=Mode.SUBTRACT)
        Cylinder(radius=(BRG_ID + 1.6) / 2, height=FLANGE_T * 3,
                 align=(Align.CENTER, Align.CENTER, Align.MIN),
                 mode=Mode.SUBTRACT)
        _retain_holes(part, M3_PILOT, FLANGE_T * 2)
    return part.part


def create_bearing_carrier():
    """Plugs the thigh's bore and presents the 8 mm stub the 608 rides on.

    This is the whole handedness story in 4 grams: it goes in whichever thigh
    cheek is NOT carrying the servo.
    """
    stub_l = LUG_T + BRG_W + 1.0
    with BuildPart() as part:
        Cylinder(radius=(SEAT_D - PRESS) / 2, height=WALL + 2.0,
                 align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, 0, WALL + 2.0)):
            Cylinder(radius=BRG_ID / 2 - 0.05, height=stub_l,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
        # axial screw pulls the whole knee stack together
        Cylinder(radius=M3_PILOT / 2, height=WALL + 2.0 + stub_l,
                 align=(Align.CENTER, Align.CENTER, Align.MIN),
                 mode=Mode.SUBTRACT)
        # flats so it can be driven home and does not spin in its bore
        for sx in (-1, 1):
            with Locations((sx * (SEAT_D / 2 - 0.6), 0, 0)):
                Box(3.0, SEAT_D, WALL + 2.0,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    mode=Mode.SUBTRACT)
    return part.part


if __name__ == "__main__":
    from partcheck import check

    out = Path(__file__).parent / "output"
    out.mkdir(exist_ok=True)

    parts = [
        ("horn_adapter", create_horn_adapter()),
        ("bearing_retainer", create_bearing_retainer()),
        ("bearing_carrier", create_bearing_carrier()),
    ]
    print(f"608ZZ interface: {BRG_ID:.0f} x {BRG_OD:.0f} x {BRG_W:.0f} mm")
    print(f"seat {SEAT_D:.1f}, retain {RETAIN_N}x M3 at PCD {RETAIN_PCD:.0f}, "
          f"horn 4x at PCD {HORN_PCD:.0f}\n")

    total = 0.0
    for nm, sh in parts:
        export_stl(sh, str(out / f"{nm}.stl"))
        export_step(sh, str(out / f"{nm}.step"))
        total += sh.volume / 1000 * 0.953
    for nm, sh in parts:
        check(sh, nm, out_dir=str(out), material="PETG")
    print(f"\nthree inserts, {total:.1f} g total -- and they carry the entire "
          f"left/right distinction")

    html = out / "joint_parts.html"
    subprocess.run([sys.executable,
                    str(Path(__file__).parent.parent.parent / "edu/tools/stl_viewer.py"),
                    *[str(out / f"{nm}.stl") for nm, _ in parts],
                    "-o", str(html), "-t", "Alpha Centauri — knee inserts"],
                   check=True)
