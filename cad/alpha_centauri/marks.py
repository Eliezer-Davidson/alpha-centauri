"""Alpha Centauri — Mk1 (servo-rich) and Mk2 (servo-cheap), built side by side.

    edu/.cadenv/bin/python cad/alpha_centauri/marks.py

The author named them on 2026-08-01: Mk1 IS the servo-rich build, Mk2 IS the
servo-cheap one. They are not two robots. Chassis, legs, ways, carriage, guide
rods and boxes are identical; only the DRIVE MODULES differ, and every one of
them bolts to a pattern the other variant also has.

                            Mk1  servo-rich          Mk2  servo-cheap
    chest lift        T8 lead screw + 1 servo    ratchet rack + sprung pawl
    waist slide       pinion + 1 servo           two-way detent + release lever
    chest yaw         1 servo on the slew        indexed ring + pull pin
    servos            15                         12
    verticals         4: 2 rods + 2 screws on    6: 4 corner rods +
                      the 4 corners, diagonals   2 centreline racks

WHY THE GUIDE RODS ARE BACK -- the author, 2026-08-01
----------------------------------------------
"why is the rail to extend the chest box only on 1 side?"

Because a drive got swapped for a lock and the guide was never put back. The
donor chest box has TWO 8.5 mm tower bores at x = +/-60, y = -49.5: it was always
meant to ride two rods. Replacing the twin screws with one hand-driven ratchet
left a single central column doing both jobs, and those two bores ORPHANED.

A single column cannot guide this. Measured, not asserted:

    one printed rack column   J = 5904 mm4, k = 14.8 N.m/rad
                              -> 9.5 deg of yaw under one arm = 50 mm at the hand
    two 8 mm steel rods       2.64 mm tip deflection
                              -> 2.5 deg = 13 mm at the hand, 4x better

So the split is the same one the rail already uses, and the same one every
machine tool uses: RODS GUIDE, THE CENTRE COLUMN DRIVES. It also disposes of the
twin-screw jam from S1.4 -- two SMOOTH rods cannot fight each other, because the
jam came from differential drive, never from having two of something.

The centre column is at y = -49.5 rather than the middle of the box because the
chest interior is full: Jetson on the floor, camera strip on the front wall. The
rear wall is the only free face, which is why the donor put its towers there.

MK1: FOUR VERTICALS, NOT SIX -- the author, 2026-08-02
-----------------------------------------------
The chest extension does not need six vertical members. On Mk1 the two
centreline lead screws MOVE OUT to two diagonal corner stations, replacing the
guide rods that stood there -- drive and guide in one member, the middle
column empty:

    rear-left    guide rod            front-left   T8 lead screw
    front-right  guide rod            rear-right   T8 lead screw

Net 4 verticals: 2 rods + 2 screws on the same corner grid (x_torso +/- TOWER,
y = +/- ROD_HALF_SPAN) the chest towers are already bored for. The lift servo
stays SINGLE, placed beside the front-left screw; one belt gangs both screws
across the hypot(99, 120) = 155.6 mm diagonal to the rear-right screw -- the
belt is not drawn. Mk2 is UNCHANGED: 4 corner rods guide, 2 centreline ratchet
racks drive.

THE HONEST CONSEQUENCE, flagged for the drive-tower design: a lead screw
standing at a guide station must also GUIDE. The side load an 8 mm rod in a
bushing simply carried is now reacted through the T8 nut fit (a drive fit, not
a bearing fit -- nut backlash becomes chest sway) and by the screw itself,
which at 340 mm free length will whip under side loads a smooth rod shrugs
off. The drive tower must budget for this: an anti-backlash nut that doubles
as a bushing, or a plain guide bush around the screw's unthreaded shank.
Flagged, not solved.

CONDENSED MODE IS DRAWN HONESTLY -- the verticals poke out, on purpose
----------------------------------------------------------------------
build(mark, mode) accepts "work" / "walk" (chest EXTENDED at rim + 5 + STROKE)
and "work_condensed" / "walk_condensed" (chest DOWN at rim + 5, extension 0).
The verticals are fixed to the WAIST and are ROD_LEN = STROKE + 90 = 340 mm
long, so with the chest down they protrude ~250 mm through the open chest
top. The condensed builds DO NOT hide that -- the honest picture is the
design input. The author will not accept rods protruding top or bottom. Options on
the table, neither drawn: (a) a taller, mostly-hollow waist box that swallows
the rods; (b) verticals descending into the chassis body, legal only if their
path stays clear of the chassis internals while the waist box slides the full
rail travel (TORSO_WALK +37 .. TORSO_WORK +167, 130 mm).
"""

import json
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
    Cylinder,
    Location,
    export_step,
    export_stl,
    import_step,
)

import assembly as A
import assembly_centaur as AC
import waist_rail as R
from build123d import Plane
from chassis import HIP_Z
from interface_constants import (
    L1_VERTICAL,
    LEG_PLANE_Y,
    SERVO_MASS_G,
    STANCE_Z,
)

HERE = Path(__file__).parent
OUT = HERE / "output"
TBOT = HERE.parent / "telescopebot" / "output"
VENDOR = HERE.parent / "vendor"
PETG = 0.953
TPU = 1.21          # foot tread only -- matches foot.py's density table
_RHO = {"foot_tread": TPU}   # parts not printed in PETG

# THE BOXES INSTALL ROTATED -90 ABOUT Z. Not a style choice -- the donor frame
# and the robot frame are 90 degrees apart, and installing them unrotated was a
# real bug that the author caught off the render:
#
#   donor  +X / -X  = LEFT and RIGHT   (both rod towers, both shoulder pilots)
#   donor  +Y       = FRONT            (RealSense holes, intake vents)
#   donor  -Y       = REAR             (fan, 12 V grommet, rod towers sit here)
#   robot  +X       = FRONT,  robot +/-Y = LEFT and RIGHT
#
# Unrotated, the donor's left-right axis landed on the robot's fore-aft: both
# guide rods straddled FRONT-TO-BACK and sat 49.5 mm off to one side, the
# camera faced sideways, and the shoulders pointed fore and aft.
#
#   (x, y) rotated -90 about Z -> (y, -x)
#   camera (0, +65)   -> (+65, 0)          front           OK
#   rods   (+/-60, -49.5) -> (-49.5, -/+60) rear, left AND right   OK
#   arms   (+/-75, 0) -> (0, -/+75)         left and right  OK
BOX_ROT = -90.0
ROD_HALF_SPAN = 60.0    # robot Y: the rods straddle the left and right legs

# TWO COLUMN STATIONS, not one. The author, 2026-08-01: "the side opposite of where the
# rail is should also have a rail and extending mechanism."
#
# Rotating the boxes square fixed ROLL -- the rods straddle left and right. It
# did nothing for PITCH, because every column still shared one fore-aft station
# against the chest's rear wall while the box ran 132 mm forward of it:
#
#     chest box   X 102 .. 234        guide rods   X 113.5 .. 121.5
#                                     spine rack   X 110.5 .. 144.5
#
# 90 mm of the box hung past its last support. Duplicating the group at the
# opposite edge braces pitch on a 99 mm arm and, because the drive is duplicated
# too, the chest's weight is carried EITHER SIDE of its own centre of mass --
# so the overturning moment is not merely reacted better, it stops existing:
#
#     one station, reacted inside the bushing   31.1 N normal, 9.3 N drag
#     two stations 99 mm apart, one drive       15.1 N normal, 4.5 N drag
#     two stations, drive duplicated             0.0 N normal, 0.0 N drag
#
# THE TWO DRIVES MUST BE GANGED. Two pawls that seat one tooth apart across the
# 99 mm span cock the chest 6.9 deg. Mk2 carries both pawls on ONE printed
# carrier so they cannot index independently; Mk1 turns both screws from a
# single servo through a belt. That is also what disposes of the S1.4 twin-screw
# jam -- that jam was two INDEPENDENT open-loop screws, never two of something.
TOWER_BACK = -49.5      # robot X: rear tower station, as the donor drilled it
TOWER_FRONT = 49.5      # robot X: its mirror at the chest's front wall
STATIONS = ((TOWER_BACK, "rear"), (TOWER_FRONT, "front"))

# The DRIVE stations are pulled in to +/-44, NOT +/-49.5 like the rods. The rack
# base flange is 34 deep, so a drive at +/-49.5 puts its flange at 100.5 and
# 233.5 while the waist box only spans 106..228 -- both flanges overhang by
# 5.5 mm. At +/-44 they land on 106..140 and 194..228, flush at both ends.
# The rods keep +/-49.5 because those are drilled into the chest towers.
DRIVE_BACK, DRIVE_FRONT = -44.0, 44.0
DRIVES = ((DRIVE_BACK, "rear"), (DRIVE_FRONT, "front"))
ROD_D = 8.0             # smooth steel, h6; 8.5 bore in the chest towers
STROKE = 250.0
ROD_LEN = STROKE + 90.0
SCREW_LEAD = 8.0        # T8, 4-start. M8 coarse is 1.25 and needs 200 turns.

# MK1 ONLY (the author, 2026-08-02): FOUR verticals, not six. The two centreline lead
# screws move OUT to two diagonal corner stations, replacing the guide rods
# there -- drive and guide in one member, the middle column empty. The rods
# keep the other diagonal. All four members stand on the SAME corner grid the
# chest towers are bored for: x_torso +/- TOWER, y = +/- ROD_HALF_SPAN. The
# screws do NOT use the +/-44 DRIVE stations -- that pull-in exists because the
# Mk2 rack has a 34 mm flange to keep flush with the waist box; a plain screw
# has no flange to overhang.
# CONSEQUENCE (flagged for the drive-tower design): a screw at a guide station
# must also guide -- the T8 nut fit and 340 mm of screw whip now take the side
# load an 8 mm rod in a bushing simply carried. See the module docstring.
# Mk2 is UNCHANGED: 4 corner rods + 2 centreline racks.
MK1_ROD_CORNERS = (((TOWER_BACK, 1), ("rear", "left")),
                   ((TOWER_FRONT, -1), ("front", "right")))
MK1_SCREW_CORNERS = (((TOWER_FRONT, 1), ("front", "left")),
                     ((TOWER_BACK, -1), ("rear", "right")))
# The two diagonals must be disjoint and cover all four corners -- a rod and a
# screw sharing a corner would be two members fighting for one 8.5 mm bore.
_MK1_RODS = {c for c, _ in MK1_ROD_CORNERS}
_MK1_SCREWS = {c for c, _ in MK1_SCREW_CORNERS}
assert _MK1_RODS.isdisjoint(_MK1_SCREWS), "rod and screw share a corner"
assert len(_MK1_RODS | _MK1_SCREWS) == 4, "the four corners are not all manned"

MARKS = {
    "mk1": dict(
        title="Mk1 — servo-rich",
        lift="T8 lead screw, 1 servo",
        slide="pinion, 1 servo",
        yaw="1 servo on the slew ring",
        servos=15,
    ),
    "mk2": dict(
        title="Mk2 — servo-cheap",
        lift="ratchet rack + sprung pawl, arm-driven",
        slide="two-way detent + release lever, arm-driven",
        yaw="indexed ring + pull pin, arm-driven",
        servos=12,
    ),
}


def _g(name, folder=OUT):
    p = folder / f"{name}.step"
    rho = _RHO.get(name, PETG)
    return import_step(str(p)).volume / 1000.0 * rho if p.exists() else 0.0


def build(mark, mode="work"):
    """One mark, posed. Returns (stl paths, headline numbers).

    mode:  "work" / "walk"                        chest EXTENDED, rim+5+STROKE
           "work_condensed" / "walk_condensed"    chest DOWN, rim+5, ext 0 --
    the 340 mm verticals then poke ~250 mm out of the open chest top, drawn
    HONESTLY on purpose. See the module docstring.

    Also writes output/<mark>_manifest.json -- the motion-group manifest the
    HTML viewer uses to make parts moveable. Written here, in the same
    function that emits the STLs, so the two cannot drift.
    """
    spec = MARKS[mark]
    assert mode in ("work", "walk", "work_condensed", "walk_condensed"), mode
    x_torso = AC.TORSO_WORK if mode.startswith("work") else AC.TORSO_WALK
    ext = 0.0 if mode.endswith("_condensed") else STROKE
    asm = OUT / mark
    if asm.exists():
        shutil.rmtree(asm)
    asm.mkdir(parents=True)
    saved, solids, part_groups = [], [], {}

    # groups: () = chassis-fixed; ("waist",) = rides the rail;
    # ("waist", "chest") = chest-fixed. The viewer translates each part by
    # sum over its groups of (slider - group.value) * group.axis.
    def emit(name, shape, groups=()):
        p = asm / f"{name}.stl"
        export_stl(shape, str(p))
        saved.append(p)
        part_groups[name] = list(groups)
        if "ground" not in name:
            solids.append(shape)

    alpha, _, _ = A.solve_leg(STANCE_Z)
    parts = {n: import_step(str(OUT / f"{n}.step")).solids()[0]
             for n in ("thigh_shell", "calf")}
    # Feet (foot.py, 2026-08-01): authored in the calf frame, so leg_at can
    # pose them with the calf's own aim transform. Optional so marks.py still
    # builds if foot.py has not been run yet.
    for n in ("foot_core", "foot_tread"):
        if (OUT / f"{n}.step").exists():
            parts[n] = import_step(str(OUT / f"{n}.step")).solids()[0]

    # ---------------------------------------------- shared: body and legs
    import chassis as CH
    for n, s in CH.chassis_placed(OUT).items():
        emit(f"01_chassis_{n}", s)

    feet = []
    for x_hip, tag in ((AC.X_FRONT, "front"), (AC.X_REAR, "rear")):
        for sy, side in ((1, "left"), (-1, "right")):
            bits, foot = AC.leg_at(x_hip, sy, alpha, parts)
            feet.append(foot)
            for k, v in bits.items():
                emit(f"02_{k}_{tag}_{side}", v)

    # --- hip modules: ONE drawn part (front-left chirality), the right side
    # is its XZ mirror -- printed by mirroring the same STL in the slicer --
    # and the rear stations are the same two spun 180 about Z, exactly the
    # trick the chassis halves already use. Module STEP is authored with the
    # hip-pitch axis at its origin, so placement is pure translate+orient.
    hp = OUT / "hip_module.step"
    if hp.exists():
        hm = import_step(str(hp))
        hip_axis_z = HIP_Z + L1_VERTICAL   # chassis.py's own hip station (law 8)
        for x_hip, tag in ((AC.X_FRONT, "front"), (AC.X_REAR, "rear")):
            for sy, side in ((1, "left"), (-1, "right")):
                m = hm if sy > 0 else hm.mirror(Plane.XZ)
                if x_hip < 0:
                    m = m.rotate(Axis.Z, 180)
                emit(f"02_hip_{tag}_{side}",
                     m.moved(Location((x_hip, sy * LEG_PLANE_Y, hip_axis_z))))
    ground_z = feet[0][2]
    emit("00_ground", Box(900, 480, 3,
                          align=(Align.CENTER, Align.CENTER, Align.MAX))
         .moved(Location((0, 0, ground_z))))

    # ---------------------------------------------- shared: the waist rail
    # 8 x 125 mm way segments + 6 keys since 2026-09-07 (A1 mini). Placement
    # is owned by waist_rail.way_run()/keys_placed(), which asserts every
    # bolt on the chassis ledge grid -- see assembly_centaur.py for the
    # 10 mm rear-way mistake that restating it here caused.
    for i, s in enumerate(R.way_run(
            import_step(str(OUT / "rail_way_inner.step")),
            import_step(str(OUT / "rail_way_outer.step")))):
        emit(f"03_rail_way_{i}", s)
    for i, k in enumerate(R.keys_placed(
            import_step(str(OUT / "rail_way_key.step")))):
        emit(f"03_rail_way_key_{i}", k)
    emit("04_rail_rack", import_step(str(OUT / "rail_rack.step"))
         .moved(Location((AC.RAIL_MID, 0, 0))))
    emit("05_rail_carriage", import_step(str(OUT / "rail_carriage.step"))
         .moved(Location((x_torso, 0, R.CAR_Z0))), groups=("waist",))

    # ---------------------------------------------- the rail DRIVE MODULE
    if mark == "mk2":
        emit("06_rail_pawl", import_step(str(OUT / "rail_pawl.step"))
             .moved(Location((x_torso, R.PAWL_Y_SEAT, R.PAWL_ROOT_Z))),
             groups=("waist",))
        emit("06_rail_lever", import_step(str(OUT / "rail_lever.step"))
             .moved(Location((x_torso, R.PAWL_Y_SEAT - R.LEAF_T,
                              R.PAWL_ROOT_Z - R.LEAF_L))), groups=("waist",))
    else:
        z_mid = R.RACK_FACE_Z0 + R.RACK_FACE_H / 2.0
        emit("06_rail_pinion", import_step(str(OUT / "rail_pinion.step"))
             .rotate(Axis.Z, 6.92)
             .moved(Location((x_torso, R.PINION_AXIS_Y, z_mid))),
             groups=("waist",))
        emit("06_rail_driveshaft",
             Cylinder(radius=4.0, height=R.CAR_Z0 + 40.0 - z_mid,
                      align=(Align.CENTER, Align.CENTER, Align.MIN))
             .moved(Location((x_torso, R.PINION_AXIS_Y, z_mid))),
             groups=("waist",))
        sv = VENDOR / "waveshare_feetech_st3215_servo.step"
        if sv.exists():
            emit("06_rail_servo", import_step(str(sv))
                 .rotate(Axis.X, 90)
                 .moved(Location((x_torso, R.PINION_AXIS_Y,
                                  R.CAR_Z0 + R.CAR_T + 46.0))),
                 groups=("waist",))

    # ---------------------------------------------- shared: waist box
    z = R.CAR_Z0 + R.CAR_T
    if (TBOT / "waist_box.step").exists():
        emit("07_waist_box", import_step(str(TBOT / "waist_box.step"))
             .rotate(Axis.Z, BOX_ROT).moved(Location((x_torso, 0, z))),
             groups=("waist",))
    rim = z + 60.0

    # ------------------------------------- shared: the smooth guide rods
    # The author, 2026-08-01: "it should be on both sides ... supported on the left
    # legs side and the right legs side." Which is where the donor always put
    # them -- it was the 90 degree install error that moved them.
    # Mk2 mans all four corners with rods. Mk1 (the author, 2026-08-02) keeps rods on
    # ONE diagonal only -- rear-left + front-right -- because the other
    # diagonal's corners are taken by the lead screws below.
    rod_at = (MK1_ROD_CORNERS if mark == "mk1"
              else tuple(((sx, sy), (end, side))
                         for sx, end in STATIONS
                         for sy, side in ((1, "left"), (-1, "right"))))
    for (sx, sy), (end, side) in rod_at:
        emit(f"08_guide_rod_{end}_{side}",
             Cylinder(radius=ROD_D / 2, height=ROD_LEN,
                      align=(Align.CENTER, Align.CENTER, Align.MIN))
             .moved(Location((x_torso + sx, sy * ROD_HALF_SPAN, rim))),
             groups=("waist",))

    # ------------------------------------- the lift DRIVE, at BOTH stations
    # Duplicated front and rear so the chest's weight is carried either side of
    # its own centre of mass. Ganged -- see the note on STATIONS.
    if mark == "mk2":
        for sx, end in DRIVES:
            # The FRONT rack is MIRRORED: +180 so its teeth face inward, toward
            # the rear rack, instead of out over the nose. Placed at the same
            # rotation as the rear one it points the wrong way and its pawl
            # would have to reach around the outside of the box.
            r = (import_step(str(OUT / "spine_rack.step"))
                 .rotate(Axis.Z, BOX_ROT + (180.0 if end == "front" else 0.0)))
            bb = r.bounding_box()
            # Seat it by its own bounding box rather than by a hand-derived
            # offset, so mirroring cannot shift it: centred on the station in X,
            # on the centreline in Y, sitting on the rim in Z.
            r = r.moved(Location((x_torso + sx - (bb.min.X + bb.max.X) / 2,
                                  -(bb.min.Y + bb.max.Y) / 2,
                                  rim - bb.min.Z)))
            emit(f"09_spine_rack_{end}", r, groups=("waist",))
    else:
        # Mk1 (the author, 2026-08-02): the screws stand at the OTHER diagonal's
        # corners -- front-left + rear-right, on the tower grid, NOT the
        # +/-44 centreline DRIVE stations. Drive and guide in one member;
        # the centreline is empty. See MK1_SCREW_CORNERS for the honest
        # cost: a screw at a guide station must also guide.
        for (sx, sy), (end, side) in MK1_SCREW_CORNERS:
            emit(f"09_lead_screw_{end}_{side}",
                 Cylinder(radius=ROD_D / 2, height=ROD_LEN,
                          align=(Align.CENTER, Align.CENTER, Align.MIN))
                 .moved(Location((x_torso + sx, sy * ROD_HALF_SPAN, rim))),
                 groups=("waist",))
        # ONE servo drives BOTH screws through a belt -- two independent
        # open-loop screws is exactly what jammed in S1.4. It stands beside
        # the FRONT-LEFT screw; the (undrawn) belt spans the 155.6 mm
        # diagonal to the rear-right screw.
        sv = VENDOR / "waveshare_feetech_st3215_servo.step"
        if sv.exists():
            emit("09_lift_servo", import_step(str(sv)).rotate(Axis.Z, BOX_ROT)
                 .moved(Location((x_torso + TOWER_FRONT - 25.0,
                                  ROD_HALF_SPAN - 25.0, rim - 30.0))),
                 groups=("waist",))

    # ---------------------------------------------- shared: chest
    # Extended: rim + 5 + STROKE. Condensed: rim + 5, and the verticals poke
    # through the open top -- drawn honestly, never hidden.
    top, chest_top = rim, None
    if (TBOT / "chest_box.step").exists():
        cz = rim + 5.0 + ext
        pose = "EXTENDED" if ext else "CONDENSED"
        chest = (import_step(str(TBOT / "chest_box.step"))
                 .rotate(Axis.Z, BOX_ROT).moved(Location((x_torso, 0, cz))))
        emit(f"10_chest_box_{pose}", chest, groups=("waist", "chest"))
        top = cz + 85.0
        chest_top = chest.bounding_box().max.Z

    export_step(Compound(children=solids), str(OUT / f"{mark}_{mode}.step"))

    # ------------------------------------------ the motion-group manifest
    # Same build() that emits the STLs, so it cannot drift. value = the pose
    # THIS build was drawn in; the viewer translates each part by
    # sum over its groups of (slider - value) * axis.
    manifest = dict(
        groups=dict(
            waist=dict(label="waist station (rail)", axis=[1, 0, 0],
                       min=AC.TORSO_WALK, max=AC.TORSO_WORK, value=x_torso,
                       detents=dict(WALK=AC.TORSO_WALK, WORK=AC.TORSO_WORK)),
            chest=dict(label="chest extension", axis=[0, 0, 1],
                       min=0.0, max=STROKE, value=ext,
                       detents=dict(DOWN=0.0, UP=STROKE)),
        ),
        parts=part_groups,
    )
    assert set(part_groups) == {p.stem for p in saved}, "manifest drifted"
    # NAMED FOR THE PAGE, NOT FOR THE MARK. stl_viewer auto-detects
    # "<output html without .html>_manifest.json"; writing "{mark}_manifest.json"
    # instead produced a valid manifest that the viewer never found, so the
    # pages built silently WITHOUT the pose panel and nothing failed. The
    # manifest belongs to the page it poses, so it takes the page's name.
    (OUT / f"alpha_centauri_{mark}_manifest.json").write_text(
        json.dumps(manifest, indent=1))

    rod_top = rim + ROD_LEN
    protrusion = max(0.0, rod_top - chest_top) if chest_top else 0.0
    nums = dict(ground_z=ground_z, top=top, x_torso=x_torso,
                height=top - ground_z, mode=mode, ext=ext,
                rod_top=rod_top, protrusion=protrusion, **spec)
    return saved, nums


# ============================================================== the pages
SHARED_BOM = [
    ("chassis_quarter_inner", 2), ("chassis_quarter_outer", 2),
    ("abduction_pod", 4), ("chassis_splice_key", 6), ("thigh_shell", 4), ("thigh_cover", 4), ("calf", 4),
    ("foot_core", 4), ("foot_tread", 4),
    ("hip_module", 4), ("abd_adapter", 4),
    ("horn_adapter", 4), ("bearing_retainer", 4), ("bearing_carrier", 4),
    ("rail_way_inner", 4), ("rail_way_outer", 4), ("rail_way_key", 6),
    ("rail_carriage_half_aft", 1), ("rail_carriage_half_fwd", 1),
    ("rail_rack", 1),
]
MARK_BOM = {
    "mk1": [("rail_pinion", 1)],
    "mk2": [("rail_pawl", 1), ("rail_lever", 1),
            ("spine_rack", 1), ("spine_pawl", 1)],
}


def notes(mark, nums, other):
    spec = MARKS[mark]
    rows, total = [], 0.0
    for name, qty in SHARED_BOM + MARK_BOM[mark]:
        g = _g(name)
        if not g:
            continue
        total += g * qty
        tag = "" if (name, qty) in SHARED_BOM else " <b>*</b>"
        rows.append(f"<tr><td>{name.replace('_',' ')}{tag}</td>"
                    f"<td class=n>{qty}</td><td class=n>{g:.1f}</td>"
                    f"<td class=n>{g*qty:.1f}</td></tr>")
    servo_g = spec["servos"] * SERVO_MASS_G
    rows.append(f"<tr><td>servos</td><td class=n>{spec['servos']}</td>"
                f"<td class=n>{SERVO_MASS_G:.1f}</td>"
                f"<td class=n>{servo_g:.1f}</td></tr>")
    rows.append(f"<tr class=tot><td>printed + servos</td><td class=n></td>"
                f"<td class=n></td><td class=n>{total + servo_g:.0f} g</td></tr>")

    o = MARKS[other]
    d_servo = (spec["servos"] - o["servos"]) * SERVO_MASS_G
    return f"""
<h2>{spec['title']}</h2>
<table>
<tr><th>job</th><th>this build</th><th>the other one</th></tr>
<tr><td>chest lift</td><td><b>{spec['lift']}</b></td><td>{o['lift']}</td></tr>
<tr><td>waist slide</td><td><b>{spec['slide']}</b></td><td>{o['slide']}</td></tr>
<tr><td>chest yaw</td><td><b>{spec['yaw']}</b></td><td>{o['yaw']}</td></tr>
<tr><td>servos</td><td class=n><b>{spec['servos']}</b></td>
    <td class=n>{o['servos']}</td></tr>
</table>
<p>Chassis, legs, ways, carriage, guide rods and boxes are the <b>same parts</b>.
Only the rows marked <b>*</b> below are specific to this mark, and each bolts to
a pattern the other build also carries &mdash; so one machine can be converted
without reprinting structure. Servo delta vs the other mark:
<b>{d_servo:+.0f}&nbsp;g</b>.</p>

<h2>Mass, measured off the STEP</h2>
<table>
<tr><th>part</th><th class=n>qty</th><th class=n>ea g</th><th class=n>total</th></tr>
{''.join(rows)}
</table>

<h2 class=warn>Fixed today: the boxes were installed 90&deg; out</h2>
<p>The author, off the render: <i>&ldquo;it should be on both sides of the robot, its
left and right, so the chest box is supported on the left legs side and the
right legs side.&rdquo;</i> A real bug, not a preference.</p>
<p>The donor box frame and the robot frame are 90&deg; apart &mdash; in the
donor, <b>&plusmn;X is left and right</b> (both rod towers, both shoulder
pilots) and <b>+Y is front</b> (RealSense holes, intake vents). Both boxes were
installed <b>unrotated</b>, so the donor's left-right axis landed on the robot's
fore-aft. The result: both guide rods straddled front-to-back, sat 49.5&nbsp;mm
off to <i>one side</i> of the centreline, the camera faced sideways and the
shoulders pointed fore and aft.</p>
<p>Boxes now install rotated &minus;90&deg; about&nbsp;Z. The rods straddle the
left and right legs, as the donor intended.</p>
<p>Two rods also matter on their own account &mdash; the twin-screw drive had
been swapped for a single hand ratchet, leaving one column doing both jobs and
<b>orphaning both 8.5&nbsp;mm tower bores</b>:</p>
<table>
<tr><th>guide</th><th class=n>yaw under one arm</th><th class=n>sway at the hand</th></tr>
<tr><td>one printed rack column</td><td class=n>9.5&deg;</td>
    <td class=n><span class=warn>50 mm</span></td></tr>
<tr><td>two 8 mm steel rods at &plusmn;60</td><td class=n>2.5&deg;</td>
    <td class=n><span class=ok>13 mm</span></td></tr>
</table>
<p>So the rule became <b>rods guide, columns drive</b> &mdash; which also
disposed of the twin-screw jam from &sect;1.4, since two <i>smooth</i> rods
cannot fight each other. That jam came from differential drive, not from
having two of something. (On Mk1 the 2026-08-02 rearrangement has since folded
drive and guide together at the corners &mdash; next section.)</p>

<h2>The drive/guide layout, this mark</h2>
<p>Both marks carry <b>two fore-aft column stations 99&nbsp;mm apart</b>, so
the chest's weight is carried either side of its own CoM and the one-station
overturning drag (31&nbsp;N of bushing normal load, 9.3&nbsp;N per lift, a
110% Mk2 hand lift) stopped existing rather than being reacted better. The two
drives are <b>ganged</b> &mdash; indexing one tooth apart across the span
would cock the chest 6.9&deg;.</p>
{"".join([
 "<p><b>Mk1 has four verticals, not six</b> (the author, 2026-08-02): the two "
 "centreline lead screws moved OUT to the front-left and rear-right corners, "
 "replacing the guide rods there &mdash; drive and guide in one member, the "
 "centreline empty. Rods keep the rear-left and front-right corners. All four "
 "stand on the corner grid the chest towers are bored for "
 "(&plusmn;49.5 fore-aft, &plusmn;60 across). The lift servo stays single, "
 "beside the front-left screw; one belt gangs both screws across the "
 "155.6&nbsp;mm diagonal (belt not drawn).</p>"
 "<p class=warn>The honest consequence: a lead screw at a guide station must "
 "also <b>guide</b>. Side load now passes through the T8 nut fit (a drive "
 "fit, not a bearing fit &mdash; nut backlash becomes chest sway) and through "
 "the screw itself, which at 340&nbsp;mm free length whips under loads a "
 "smooth rod simply carries. The drive-tower design must budget for it: an "
 "anti-backlash nut that doubles as a bushing, or a guide bush on the screw's "
 "plain shank. Flagged, not solved.</p>"
 ] if mark == "mk1" else [
 "<p><b>Mk2 keeps rods guide, columns drive:</b> four 8&nbsp;mm corner rods, "
 "and two ratchet racks at &plusmn;44 on the centreline &mdash; pulled in "
 "from the &plusmn;49.5 towers so their 34&nbsp;mm base flanges sit flush on "
 "the waist box, and both pawls ride one printed carrier so they cannot index "
 "independently.</p>"])}

<h2>Where this mark is strong and weak</h2>
{"".join([
 "<p><b>Mk1 buys speed and autonomy.</b> The waist slides in 1.3 s on 3% of a "
 "measured servo. The lift needs a bought <b>T8 lead screw</b> (8 mm lead, "
 "~28 s); on M8 coarse threaded rod the same move is 200 turns and about "
 "<b>3 minutes</b>, which is why the donor's screw spine was not kept as-is.</p>"
 "<p class=warn>It still needs the detent and the pin. Every one of these "
 "drives is back-drivable, so a stalled servo would otherwise be holding the "
 "torso against every footfall.</p>"
 ] if mark == "mk1" else [
 "<p><b>Mk2 buys cost, mass and simplicity</b> &mdash; 3 fewer servos, 3 fewer "
 "channels, and two presses instead of three minutes on the lift, where the "
 "hand genuinely beats the screw.</p>"
 "<p>The load on the arms is not uniform, and this is the finding worth "
 "keeping: <b>slide 12%</b> of a measured servo per arm, <b>yaw 9%</b>, but "
 "<b>lift 72%</b> at 200 mm reach (54% with the elbow folded). The lift is the "
 "expensive one, not the slide.</p>"
 "<p class=warn>The 6.6 g release lever is load-bearing on the whole concept: "
 "shoving the waist against a live detent is 97% of stall and simply will not "
 "move. Unseat first, then push.</p>"])}

{"".join([
 f"<h2 class=warn>Condensed: the verticals poke out the top, on purpose</h2>"
 f"<p>The chest is DOWN (extension 0) and the {ROD_LEN:.0f}&nbsp;mm verticals "
 f"(STROKE {STROKE:.0f} + 90 engagement), fixed to the waist, protrude "
 f"<b>{nums['protrusion']:.0f}&nbsp;mm</b> through the open chest top. The "
 f"render does not hide it &mdash; the honest picture is the design input, "
 f"and rods protruding top <i>or bottom</i> are not acceptable. Options on "
 f"the table, neither drawn: a taller, mostly-hollow waist box; or verticals "
 f"descending into the chassis body, legal only if their path stays clear "
 f"while the waist box slides the full 130&nbsp;mm of rail travel "
 f"(+37&nbsp;..&nbsp;+167).</p>"
 ] if not nums['ext'] else [])}
<h2>Stance, unchanged by the mark</h2>
<table>
<tr><td>torso now at</td><td class=n>x = {nums['x_torso']:+.0f} mm</td></tr>
<tr><td>ride height</td><td class=n>{-nums['ground_z']:.0f} mm</td></tr>
<tr><td>chest top, {'extended' if nums['ext'] else 'condensed'}</td>
    <td class=n>{nums['height']:.0f} mm</td></tr>
{f"<tr><td class=warn>verticals above the open chest top</td>"
 f"<td class=n>{nums['protrusion']:.0f} mm</td></tr>" if not nums['ext'] else ""}
<tr><td>footprint</td><td class=n>500 x 279 mm</td></tr>
</table>
<p class=warn>Still open in both: hips, feet, head, arms. The yaw ring is
specified (5 mm pin, double shear, SF 18.7, 24 stations) but not yet drawn.</p>
"""


def main(mode="work"):
    outs = []
    for mark, other in (("mk1", "mk2"), ("mk2", "mk1")):
        saved, nums = build(mark, mode)
        nt = OUT / f"_notes_{mark}.html"
        nt.write_text(notes(mark, nums, other))
        html = OUT / f"alpha_centauri_{mark}.html"
        subprocess.run(
            [sys.executable, str(HERE.parent.parent / "edu/tools/stl_viewer.py"),
             *[str(p) for p in sorted(saved)], "-o", str(html),
             "-t", f"Alpha Centauri {MARKS[mark]['title']} ({mode.upper()} mode)",
             "-n", str(nt)], check=True)
        poke = (f", verticals poke {nums['protrusion']:.0f} mm out the top"
                if not nums["ext"] else "")
        print(f"{mark}: {MARKS[mark]['servos']} servos, "
              f"{nums['height']:.0f} mm tall{poke} -> {html.name}")
        outs.append(html)
    return outs


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "work")
