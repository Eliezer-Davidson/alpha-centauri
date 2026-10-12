"""Alpha Centauri — CENTAUR layout Mk1: symmetric hips, torso on a fore-aft rail.

    edu/.cadenv/bin/python cad/alpha_centauri/assembly_centaur.py

WHAT THIS FILE USED TO SAY, AND WHY IT WAS WRONG
------------------------------------------------
It used to build hips at +300/-200 and claim that moving them bought a forward
torso for free. The author looked at the render and said it seemed like nothing had
changed except that one half got longer. He was right.

With the wheelbase length fixed, sliding the hip stations only relabels the
origin: the counterweight lever about the midpoint came out 190.0 mm either way.
The apparent gain was an arithmetic artifact -- the solver pinned the battery at
x = -190 in every configuration while the rear body shrank from 250 to 200, so
the symmetric layout was never allowed the x = -240 it could have had.

Hips are back to +/-250, which also restores "one chassis part, printed twice".

WHAT REPLACES IT
----------------
The rail. The torso is 35.2% of the robot's mass, so moving it IS the lever that
moving the hips only pretended to be:

    WALK MODE   torso aft at x = +37   -> CoM at 0, dead on the crawl boundary
    WORK MODE   torso fwd at x = +167  -> CoM at +46, over the front legs

Backwards from the obvious, and that is the point: it is a mode switch, not a
better fixed compromise. Standing on four feet the CoM may sit anywhere inside
the footprint, so WORK mode is stable; it is only the three-footed crawl that
demands a centred CoM, and that is exactly when the torso is aft.
"""

import math
import shutil
import subprocess
import sys
from pathlib import Path

from build123d import (
    Align,
    Axis,
    Box,
    Compound,
    Location,
    export_step,
    export_stl,
    import_step,
)

import assembly as A
import waist_rail as R
from interface_constants import (
    L1_LATERAL,
    L1_VERTICAL,
    L2_THIGH,
    LEG_LR,
    STANCE_Z,
    extension_at,
)

HERE = Path(__file__).parent
OUT = HERE / "output"
ASM = OUT / "centaur"
TBOT = HERE.parent / "telescopebot" / "output"

X_FRONT, X_REAR = 250.0, -250.0          # SYMMETRIC. One part, printed twice.
RAIL_MID = 102.0                         # rail centre; travel is +/-75 about it
TORSO_WALK = 37.0                        # CoM = 0, the crawl boundary
TORSO_WORK = 167.0                       # CoM = +46, torso over the front legs
TORSO_STROKE = 250.0                     # chest extension, unrelated to the rail
ROD_Y = -49.5
from chassis import HIP_Z  # abduction axis — single source (law 8)

# Torso mass fraction for the CoM readout below -- taken from the ledger,
# never restated. (Until 2026-09-22 this line restated 1538 / 4370 g; the
# phone replan moved the ledger to 1453 g torso and the restatement was
# silently stale.)
import balance as _B
TORSO_FRAC = _B.TORSO_FULL / (_B.CHASSIS + 4 * _B.LEG_TOTAL + _B.TORSO_FULL
                              + _B.SPINE + _B.BATTERY)


def leg_at(x_hip, sy, alpha, parts):
    hip_pitch = (x_hip, sy * (LEG_LR + L1_LATERAL), HIP_Z + L1_VERTICAL)
    a = math.radians(alpha)
    knee = (hip_pitch[0] - L2_THIGH * math.sin(a), hip_pitch[1],
            hip_pitch[2] - L2_THIGH * math.cos(a))
    foot = (hip_pitch[0], hip_pitch[1], hip_pitch[2] - extension_at(STANCE_Z))
    bits = {"thigh": A._aim(parts["thigh_shell"], hip_pitch, knee),
            "calf": A._aim(parts["calf"], knee, foot)}
    # The foot's STEPs are authored in the calf frame (foot.py: "robot frame,
    # assembly"), so the calf's own aim transform places them exactly; the
    # tread's R15 contact then lands on the IK foot point by construction.
    for fp in ("foot_core", "foot_tread"):
        if fp in parts:
            bits[fp] = A._aim(parts[fp], knee, foot)
    return (bits, foot)


def main(mode="work"):
    x_torso = TORSO_WORK if mode == "work" else TORSO_WALK
    if ASM.exists():
        shutil.rmtree(ASM)
    ASM.mkdir(parents=True)
    saved, solids = [], []

    def emit(name, shape):
        p = ASM / f"{name}.stl"
        export_stl(shape, str(p))
        saved.append(p)
        if "ground" not in name:
            solids.append(shape)

    alpha, _, _ = A.solve_leg(STANCE_Z)
    parts = {n: import_step(str(OUT / f"{n}.step")).solids()[0]
             for n in ("thigh_shell", "calf")}

    # --- chassis: ONE part, printed twice --------------------------------
    # --- chassis: 4 quarters + 4 bolt-on pods + 6 keys (chassis.py owns
    # the placement; the H2C-era "one half printed twice" is gone)
    import chassis as CH
    for n, s in CH.chassis_placed(OUT).items():
        emit(f"01_chassis_{n}", s)

    # --- legs -------------------------------------------------------------
    feet = []
    for x_hip, tag in ((X_FRONT, "front"), (X_REAR, "rear")):
        for sy, side in ((1, "left"), (-1, "right")):
            bits, foot = leg_at(x_hip, sy, alpha, parts)
            feet.append(foot)
            for k, v in bits.items():
                emit(f"02_{k}_{tag}_{side}", v)

    ground_z = feet[0][2]
    emit("00_ground", Box(900, 480, 3,
                          align=(Align.CENTER, Align.CENTER, Align.MAX))
         .moved(Location((0, 0, ground_z))))

    # --- THE RAIL ---------------------------------------------------------
    # Ways sit on the chassis ledges in the existing bolt pattern. The rack
    # stands in the well; the carriage rides above.
    # HISTORY: one 250 mm way per chassis half tiled the body -250..0..+250.
    # Placed off RAIL_MID instead, they ran to x = 452 and the robot's bounding
    # box came out 772 mm long on a 500 mm body -- which is how this was caught.
    # SINCE 2026-09-07 (A1 mini): 8 x 125 mm segments + 6 loose keys, and the
    # placement is OWNED by waist_rail.way_run() / keys_placed() -- it rotates
    # the rear segments 180 deg like the rear chassis half and ASSERTS every
    # ledge bolt on the chassis pilot grid. This file used to restate the
    # placement (translated, not rotated) and every rear bolt missed its
    # pilot by 10 mm for a month. Never restate it here again.
    run = R.way_run(import_step(str(OUT / "rail_way_inner.step")),
                    import_step(str(OUT / "rail_way_outer.step")))
    for i, s in enumerate(run):
        emit(f"03_rail_way_{i}", s)
    keys = R.keys_placed(import_step(str(OUT / "rail_way_key.step")))
    for i, k in enumerate(keys):
        emit(f"03_rail_way_key_{i}", k)

    emit("04_rail_rack",
         import_step(str(OUT / "rail_rack.step")).moved(Location((RAIL_MID, 0, 0))))
    emit("05_rail_carriage",
         import_step(str(OUT / "rail_carriage.step"))
         .moved(Location((x_torso, 0, R.CAR_Z0))))

    # servo- module, seated. The pinion is the alternative at the same station.
    pawl = import_step(str(OUT / "rail_pawl.step"))
    emit("06_rail_pawl_SERVOLESS",
         pawl.moved(Location((x_torso, R.PAWL_Y_SEAT, R.PAWL_ROOT_Z))))
    emit("06_rail_lever_SERVOLESS",
         import_step(str(OUT / "rail_lever.step"))
         .moved(Location((x_torso, R.PAWL_Y_SEAT - R.LEAF_T,
                          R.PAWL_ROOT_Z - R.LEAF_L))))

    # --- torso, riding the carriage ---------------------------------------
    z = R.CAR_Z0 + R.CAR_T
    if (TBOT / "waist_box.step").exists():
        emit("07_waist_box", import_step(str(TBOT / "waist_box.step"))
             .moved(Location((x_torso, 0, z))))
    rim = z + 60.0

    if (OUT / "spine_rack.step").exists():
        import spine_lock as SL
        emit("08_spine_rack", import_step(str(OUT / "spine_rack.step")).moved(
            Location((x_torso - SL.RACK_W / 2, ROD_Y - SL.RACK_T / 2, rim))))

    top = rim
    if (TBOT / "chest_box.step").exists():
        cz = rim + 5.0 + TORSO_STROKE
        emit("09_chest_box_EXTENDED", import_step(str(TBOT / "chest_box.step"))
             .moved(Location((x_torso, 0, cz))))
        top = cz + 85.0

    # --- the numbers -------------------------------------------------------
    com = lambda xt: TORSO_FRAC * (xt - TORSO_WALK)
    print(f"hips        {X_FRONT:+.0f} / {X_REAR:+.0f}   SYMMETRIC -- one chassis "
          f"part, printed twice")
    print(f"rail        {R.TRAVEL:.0f} mm travel centred at x = {RAIL_MID:+.0f}")
    print(f"  WALK      torso {TORSO_WALK:+.0f}  CoM {com(TORSO_WALK):+.1f} mm   "
          f"crawl-legal")
    print(f"  WORK      torso {TORSO_WORK:+.0f}  CoM {com(TORSO_WORK):+.1f} mm   "
          f"4-foot stance only")
    print(f"showing     {mode.upper()} mode, torso at {x_torso:+.0f}")
    print(f"ground      z = {ground_z:.1f}   ride height {-ground_z:.1f} mm")
    print(f"standing    {top - ground_z:.0f} mm to chest top, extended")
    print(f"footprint   {X_FRONT - X_REAR:.0f} x {2 * (LEG_LR + L1_LATERAL):.1f} mm")
    print(f"deck rose   {R.WAY_H + R.CAR_T:.0f} mm -- the rail sits under the "
          f"waist box, so the head budget shrinks by that much")

    # Compound STEP as well as the STLs: hero_render.py works off B-Rep, and a
    # shaded still is the only artefact that survives being pasted into a chat.
    export_step(Compound(children=solids), str(OUT / f"centaur_{mode}.step"))

    html = OUT / "alpha_centauri_centaur.html"
    subprocess.run([sys.executable, str(HERE.parent.parent / "edu/tools/stl_viewer.py"),
                    *[str(p) for p in sorted(saved)], "-o", str(html),
                    "-t", f"Alpha Centauri Mk1 — symmetric hips + waist rail "
                          f"({mode.upper()} mode)"],
                   check=True)
    return html


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "work")
