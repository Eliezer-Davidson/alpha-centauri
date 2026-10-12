"""
TelescopeBot: Leg Linkage -- Thigh + Calf structural links (build123d)

Generates the two structural links for ONE leg (exported as separate solids):

1. ``thigh_link`` -- open-box (U-channel) beam from the hip to the knee.
   * Hip end: flat disc interface, 4x M3 clearance holes on a bolt circle,
     bolts flat against the waist-box SC15/SCS15 round horn (horn presses on
     the flat bed-side face; screw heads accessible from the open channel).
   * Knee end: pocketed bracket for a DS5160 60 kg-cm servo. The servo drops
     in from the open top and hangs from its flange tabs on two full-height
     ledge columns (M4 self-tap pilots at the researched 75.0 x 17.0 hole
     pattern). Spline up = knee axis. A boss on the web carries an M3
     self-tap pilot coaxial with the spline: the far-side idler pivot.

2. ``calf_link`` -- clevis + U-channel beam from the knee to the ankle.
   * Knee end: two parallel lug walls straddle the thigh. The outboard lug
     bolts to the DS5160 round horn (4x M3 clearance on an ASSUMED 17.0 PCD,
     teardrop center clearance). The inboard lug pivots on an M3 screw
     (IDLER CHOICE: M3 x 12 pan/button head + washer, self-tapped into the
     thigh's web+boss, 7.5 mm engagement. Chosen over a ball bearing seat:
     loads are modest, no unverified bearing dims enter the build, and
     preload is adjustable. Upgrade path: bore the lug to 8.0 and press a
     693ZZ if slop develops.)
   * Ankle end: side-loading pocket for an MG996R. The servo slides in from
     the outboard face, flange bears on that face, 4x M3 self-tap pilots at
     the researched (clone-variant!) 48.3 x 10.2 hole pattern.

Gravity-compensation anchors: two 6 dia x 8 grooved posts per link on the
FRONT face (thigh near hip, calf near ankle) to hook surgical-tubing
tendons spanning the knee. Thigh posts are horizontal in print orientation
and carry a 45-deg under-wedge so they print support-free; calf posts are
vertical in print orientation (trivially support-free).

Both parts export ALREADY IN PRINT ORIENTATION -- print as exported:
* thigh_link prints on its inboard face (knee axis vertical). Channel and
  servo pocket open upward; all holes are vertical; posts have under-wedges.
* calf_link prints on its back face (front face up). Lugs are vertical
  walls; the only horizontal holes are small (M3) plus one teardropped
  10 mm horn clearance (45-deg roof).

HANDEDNESS: as modeled this is ONE leg (fronts: thigh -Y, calf +Z). The
other leg is a MIRROR -- print a second set mirrored in the slicer.

Knee ROM: crossbar clears the thigh tip (R26 about the knee axis, 3 mm
running gap) for roughly +/-85 deg from straight before the crossbar meets
the tapered thigh flank. Ankle wire and knee wire route through the open
channels.

MEASURE BEFORE TRUSTING: every DS5160/MG996R constant is UNVERIFIED in
hardware_constants.py (caliper before printing). Horn bolt circles
(HIP_BOLT_PCD, KNEE_HORN_PCD) are ASSUMED -- measure the shipped horns.
"""

from math import cos, radians, sin, sqrt
from pathlib import Path

from build123d import (
    Align,
    Box,
    BuildPart,
    BuildSketch,
    Circle,
    Cone,
    Cylinder,
    Locations,
    Mode,
    Plane,
    Polygon,
    Rectangle,
    export_step,
    export_stl,
    extrude,
)

from hardware_constants import (
    DS5160_BODY_LENGTH,
    DS5160_BODY_WIDTH,
    DS5160_HOLE_SPACING_LENGTH,
    DS5160_HOLE_SPACING_WIDTH,
    DS5160_OVERALL_HEIGHT_WITH_HORN,
    DS5160_SHAFT_FROM_FRONT_FACE,
    DS5160_SHAFT_FROM_FRONT_HOLES,
    DS5160_TAB_UNDERSIDE_HEIGHT,
    M3_CLEAR,
    M3_PILOT,
    MG996R_BODY_LENGTH,
    MG996R_BODY_WIDTH,
    MG996R_FLANGE_SPAN,
    MG996R_FLANGE_UNDERSIDE_HEIGHT,
    MG996R_HOLE_SPACING_LENGTH,
    MG996R_HOLE_SPACING_WIDTH,
    MG996R_SHAFT_FROM_FLANGE_TIP,
    MG996R_SHAFT_FROM_FRONT_FACE,
    SCS15_ROUND_HORN_DIA,
    WALL_MM,
)

# ------------------------------------------------------------ architecture
HIP_TO_KNEE_MM = 90.0        # hip axis -> knee axis (sweepable)
KNEE_TO_ANKLE_MM = 90.0      # knee axis -> ankle axis (sweepable)

WEB_T = 4.0                  # channel web (back wall) thickness, >= WALL_MM
WALL_T = 4.0                 # channel side-wall thickness, >= WALL_MM
POCKET_CL = 0.5              # per-side servo pocket clearance (mirrors FS5103R value)
UNDER_BODY_GAP = 4.0         # air between web top and DS5160 case bottom

# ------------------------------------------------------------- thigh (hip end)
HIP_PLATE_R = 17.0           # hip disc radius; covers the 19.95 SCS15 round horn
HIP_PLATE_T = 6.0            # hip disc thickness
HIP_BOLT_PCD = 14.0          # ASSUMED horn screw circle -- MEASURE the horn
HIP_CENTER_CLEAR = 10.0      # ASSUMED hub / retaining-screw head clearance
LOW_WALL_H = 20.0            # channel wall height in the hip half

# ------------------------------------------------------------ thigh (knee end)
KNEE_TIP_R = 26.0            # knee-end outline radius about the knee axis
KNEE_BLOCK_X0 = 26.0         # x where full-height knee block begins
M4_PILOT = 3.6               # M4 self-tap pilot (0.9*d rule, matches M2/M3 house pilots)
M4_PILOT_DEPTH = 12.0
IDLER_BOSS_DIA = 12.0
NOTCH_HALF_W = 4.5           # wire channel / lightening notch half width
RIB_X = 21.5                 # transverse rib center (hip half)

# knee stack (derived; comments show values for the stock constants)
KNEE_LEDGE_Z = WEB_T + UNDER_BODY_GAP + DS5160_TAB_UNDERSIDE_HEIGHT   # 39.0
DS_BODY_BOTTOM_Z = WEB_T + UNDER_BODY_GAP                             # 8.0
KNEE_HORN_TOP_Z = DS_BODY_BOTTOM_Z + DS5160_OVERALL_HEIGHT_WITH_HORN  # 64.8
IDLER_BOSS_TOP = DS_BODY_BOTTOM_Z - 0.5                               # 7.5

DS_FRONT_FACE_X = HIP_TO_KNEE_MM + DS5160_SHAFT_FROM_FRONT_FACE       # 102.8
DS_CAV_X0 = DS_FRONT_FACE_X - DS5160_BODY_LENGTH - POCKET_CL          # 37.3
DS_CAV_X1 = DS_FRONT_FACE_X + POCKET_CL                               # 103.3
DS_FRONT_HOLES_X = HIP_TO_KNEE_MM + DS5160_SHAFT_FROM_FRONT_HOLES     # 107.9
DS_REAR_HOLES_X = DS_FRONT_HOLES_X - DS5160_HOLE_SPACING_LENGTH       # 32.9
DS_HOLES_HALF_W = DS5160_HOLE_SPACING_WIDTH / 2                       # 8.5

# ---------------------------------------------------------------------- calf
PIVOT_WASHER_GAP = 0.5       # running gap at the idler side of the clevis
CLEVIS_HALF = (KNEE_HORN_TOP_Z + PIVOT_WASHER_GAP) / 2                # 32.65
LUG_T = 5.0                  # clevis lug wall thickness
LUG_R = 15.0                 # lug tip radius about the knee axis
CROSSBAR_CLEAR = 3.0         # crossbar to thigh-tip running gap
CB_X0 = KNEE_TIP_R + CROSSBAR_CLEAR                                   # 29.0
CB_X1 = CB_X0 + 8.0                                                   # 37.0
TAPER_X = 55.0               # crossbar-width -> beam-width taper ends here
BEAM_HALF_W = 17.0           # ankle beam half width (34 total)
CALF_DEPTH = 30.0            # front-back depth of the calf (print Z)
KNEE_AXIS_Z = CALF_DEPTH / 2                                          # 15.0
CALF_END_X = 114.0
POCKET_END_X = CALF_END_X - WALL_T                                    # 110.0
KNEE_HORN_PCD = 17.0         # ASSUMED DS5160 round-horn screw circle -- MEASURE
KNEE_HORN_CENTER_CLEAR = 10.0  # ASSUMED horn hub / screw-head clearance
BLK_Y0 = 8.0                 # ankle flange block inner face

MG_SHAFT_X = KNEE_TO_ANKLE_MM                                         # 90.0
MG_CAV_X0 = MG_SHAFT_X + MG996R_SHAFT_FROM_FRONT_FACE - MG996R_BODY_LENGTH - POCKET_CL  # 59.2
MG_CAV_X1 = MG_SHAFT_X + MG996R_SHAFT_FROM_FRONT_FACE + POCKET_CL     # 100.5
MG_CAV_Z0 = (CALF_DEPTH - MG996R_BODY_WIDTH - 2 * 0.25) / 2           # 4.75
MG_FLANGE_CENTER_X = MG_SHAFT_X + MG996R_SHAFT_FROM_FLANGE_TIP - MG996R_FLANGE_SPAN / 2  # 80.0
MG_HOLE_XS = (
    MG_FLANGE_CENTER_X - MG996R_HOLE_SPACING_LENGTH / 2,              # 55.85
    MG_FLANGE_CENTER_X + MG996R_HOLE_SPACING_LENGTH / 2,              # 104.15
)
MG_HOLE_ZS = (
    KNEE_AXIS_Z - MG996R_HOLE_SPACING_WIDTH / 2,                      # 9.9
    KNEE_AXIS_Z + MG996R_HOLE_SPACING_WIDTH / 2,                      # 20.1
)

# --------------------------------------------------- gravity-comp tendon posts
POST_DIA = 6.0
POST_LEN = 8.0               # exposed length
POST_GROOVE_DIA = 4.4
POST_GROOVE_W = 1.6
POST_BASE_LEN = POST_LEN - POST_GROOVE_W - 1.6                        # 4.8 shank
THIGH_POST_XS = (18.0, 28.0)   # near hip, on the front (-Y) wall
THIGH_POST_Z = 14.0
CALF_POST_XS = (55.0, 104.5)   # ankle-ward, on the front (+Z) face
CALF_POST_Y = 12.5

assert WEB_T >= WALL_MM and WALL_T >= WALL_MM
assert 2 * HIP_PLATE_R >= SCS15_ROUND_HORN_DIA + 2.0  # disc covers the horn


def _thigh_half_width(x):
    """Half width of the thigh hull at station x (hip disc -> knee circle)."""
    return HIP_PLATE_R + (KNEE_TIP_R - HIP_PLATE_R) * x / HIP_TO_KNEE_MM


def _thigh_outline():
    """Hull: hip circle + knee circle + connecting quad (call inside a sketch)."""
    Circle(HIP_PLATE_R)
    with Locations((HIP_TO_KNEE_MM, 0)):
        Circle(KNEE_TIP_R)
    Polygon(
        (0, HIP_PLATE_R),
        (HIP_TO_KNEE_MM, KNEE_TIP_R),
        (HIP_TO_KNEE_MM, -KNEE_TIP_R),
        (0, -HIP_PLATE_R),
        align=None,
    )


def create_thigh():
    """Thigh in print orientation: inboard face on the bed, knee axis +Z."""
    with BuildPart() as thigh:
        # Web (channel back wall) across the whole hull.
        with BuildSketch():
            _thigh_outline()
        extrude(amount=WEB_T)

        # Perimeter wall ring, low height (hip half of the link).
        with BuildSketch():
            _thigh_outline()
            Circle(HIP_PLATE_R - WALL_T, mode=Mode.SUBTRACT)
            with Locations((HIP_TO_KNEE_MM, 0)):
                Circle(KNEE_TIP_R - WALL_T, mode=Mode.SUBTRACT)
            Polygon(
                (0, HIP_PLATE_R - WALL_T),
                (HIP_TO_KNEE_MM, KNEE_TIP_R - WALL_T),
                (HIP_TO_KNEE_MM, -(KNEE_TIP_R - WALL_T)),
                (0, -(HIP_PLATE_R - WALL_T)),
                align=None,
                mode=Mode.SUBTRACT,
            )
        extrude(amount=LOW_WALL_H)

        # Full-height knee block (becomes cavity walls + tab ledge columns).
        with BuildSketch():
            _thigh_outline()
            with Locations((KNEE_BLOCK_X0, 0)):
                Rectangle(
                    200, 120, align=(Align.MIN, Align.CENTER), mode=Mode.INTERSECT
                )
        extrude(amount=KNEE_LEDGE_Z)

        # Hip disc (SC15 horn bolts flat against its bed-side face).
        Cylinder(
            HIP_PLATE_R, HIP_PLATE_T, align=(Align.CENTER, Align.CENTER, Align.MIN)
        )

        # Transverse rib in the hip half (ends embed into the side walls).
        with Locations((RIB_X, 0, 0)):
            Box(3.0, 32.0, 10.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # DS5160 body cavity -- open top, servo hangs from its tabs.
        cav_w = DS5160_BODY_WIDTH + 2 * POCKET_CL
        with Locations(((DS_CAV_X0 + DS_CAV_X1) / 2, 0, WEB_T)):
            Box(
                DS_CAV_X1 - DS_CAV_X0,
                cav_w,
                KNEE_LEDGE_Z + 10,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )

        # Rear notch: wire drop-in channel between the rear pilot columns.
        with Locations((31.0, 0, WEB_T)):
            Box(
                14.0,
                2 * NOTCH_HALF_W,
                KNEE_LEDGE_Z + 10,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )
        # Front notch: lightening between the front pilot columns.
        with Locations((DS_CAV_X1, 0, WEB_T)):
            Box(
                8.2,
                2 * NOTCH_HALF_W,
                KNEE_LEDGE_Z + 10,
                align=(Align.MIN, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )

        # Idler boss + M3 pilot, coaxial with the knee (spline) axis.
        with Locations((HIP_TO_KNEE_MM, 0, WEB_T)):
            Cylinder(
                IDLER_BOSS_DIA / 2,
                IDLER_BOSS_TOP - WEB_T,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
        with Locations((HIP_TO_KNEE_MM, 0, -1)):
            Cylinder(
                M3_PILOT / 2,
                IDLER_BOSS_TOP + 1,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )

        # M4 self-tap pilots for the DS5160 flange screws (4x).
        pilot_pts = [
            (x, s * DS_HOLES_HALF_W, KNEE_LEDGE_Z - M4_PILOT_DEPTH)
            for x in (DS_REAR_HOLES_X, DS_FRONT_HOLES_X)
            for s in (-1, 1)
        ]
        with Locations(*pilot_pts):
            Cylinder(
                M4_PILOT / 2,
                M4_PILOT_DEPTH,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )

        # Hip interface holes: center hub clearance + 4x M3 clearance on PCD.
        with Locations((0, 0, -1)):
            Cylinder(
                HIP_CENTER_CLEAR / 2,
                HIP_PLATE_T + 2,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )
        pcr = HIP_BOLT_PCD / 2
        hip_pts = [
            (pcr * cos(radians(a)), pcr * sin(radians(a)), -1)
            for a in (0, 90, 180, 270)
        ]
        with Locations(*hip_pts):
            Cylinder(
                M3_CLEAR / 2,
                HIP_PLATE_T + 2,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )

        # Gravity-comp posts on the front (-Y) wall + 45-deg under-wedges.
        for px in THIGH_POST_XS:
            face_y = -_thigh_half_width(px)
            segs = (
                (POST_DIA / 2, face_y + 2.0, face_y - POST_BASE_LEN),
                (
                    POST_GROOVE_DIA / 2,
                    face_y - POST_BASE_LEN,
                    face_y - POST_BASE_LEN - POST_GROOVE_W,
                ),
                (POST_DIA / 2, face_y - POST_BASE_LEN - POST_GROOVE_W, face_y - POST_LEN),
            )
            for r, y0, y1 in segs:
                with Locations((px, (y0 + y1) / 2, THIGH_POST_Z)):
                    Cylinder(r, abs(y0 - y1), rotation=(90, 0, 0))
            # 45-deg wedge under the full post length (support-free print).
            zt = THIGH_POST_Z - POST_DIA / 2  # post bottom tangent
            with BuildSketch(Plane.YZ.offset(px - POST_DIA / 2)):
                Polygon(
                    (face_y + 1.0, zt),
                    (face_y - POST_LEN, zt),
                    (face_y + 1.0, zt - (POST_LEN + 1.0)),
                    align=None,
                )
            extrude(amount=POST_DIA)

    return thigh.part


def create_calf():
    """Calf in print orientation: back face on the bed, front face +Z."""
    lug_out = CLEVIS_HALF + LUG_T  # lug outer faces at +/- this y
    with BuildPart() as calf:
        # Beam + crossbar outline (plan view), full depth.
        with BuildSketch():
            Polygon(
                (CB_X0, lug_out),
                (CB_X1, lug_out),
                (TAPER_X, BEAM_HALF_W),
                (CALF_END_X, BEAM_HALF_W),
                (CALF_END_X, -BEAM_HALF_W),
                (TAPER_X, -BEAM_HALF_W),
                (CB_X1, -lug_out),
                (CB_X0, -lug_out),
                align=None,
            )
        extrude(amount=CALF_DEPTH)

        # Channel pocket (hand-offset inner outline, >= 4 mm walls everywhere).
        with BuildSketch(Plane.XY.offset(WEB_T)):
            Polygon(
                (CB_X0 + WALL_T, 32.5),
                (TAPER_X - 3.0, BEAM_HALF_W - WALL_T),
                (POCKET_END_X, BEAM_HALF_W - WALL_T),
                (POCKET_END_X, -(BEAM_HALF_W - WALL_T)),
                (TAPER_X - 3.0, -(BEAM_HALF_W - WALL_T)),
                (CB_X0 + WALL_T, -32.5),
                align=None,
            )
        extrude(amount=CALF_DEPTH - WEB_T + 1, mode=Mode.SUBTRACT)

        # Ankle flange blocks (trimmed flush by the servo cavity cut below).
        for bx0, bx1 in ((MG_HOLE_XS[0] - 5.0, MG_CAV_X0 + 1.0),
                         (MG_CAV_X1 - 1.0, MG_HOLE_XS[1] + 4.65)):
            with Locations((bx0, BLK_Y0, 0)):
                Box(
                    bx1 - bx0,
                    BEAM_HALF_W - BLK_Y0,
                    CALF_DEPTH,
                    align=(Align.MIN, Align.MIN, Align.MIN),
                )

        # MG996R cavity: opens on the outboard (+Y) face AND the front (+Z)
        # face -- no ceiling bridge; the servo side-loads, flange bears on
        # the +Y wall face, horn outboard.
        cav_y0 = BEAM_HALF_W - (MG996R_FLANGE_UNDERSIDE_HEIGHT + POCKET_CL)
        with Locations((MG_CAV_X0, cav_y0, MG_CAV_Z0)):
            Box(
                MG_CAV_X1 - MG_CAV_X0,
                40.0,
                CALF_DEPTH,
                align=(Align.MIN, Align.MIN, Align.MIN),
                mode=Mode.SUBTRACT,
            )

        # MG996R flange pilots: M3 self-tap, drilled inboard along -Y.
        mg_pts = [(hx, BLK_Y0 + 5.25, hz) for hx in MG_HOLE_XS for hz in MG_HOLE_ZS]
        with Locations(*mg_pts):
            Cylinder(
                M3_PILOT / 2, 9.5, rotation=(90, 0, 0), mode=Mode.SUBTRACT
            )

        # Clevis lugs: vertical walls in print, straddling the thigh.
        # Plane.XZ normal is -Y: offset(+d) puts the sketch at y=-d.
        for plane_off in (CLEVIS_HALF, -lug_out):
            with BuildSketch(Plane.XZ.offset(plane_off)):
                with Locations((0, KNEE_AXIS_Z)):
                    Circle(LUG_R)
                Polygon(
                    (0, 0),
                    (CB_X1, 0),
                    (CB_X1, CALF_DEPTH),
                    (0, CALF_DEPTH),
                    align=None,
                )
            extrude(amount=LUG_T)

        # Outboard (+Y) lug: teardropped horn hub clearance (45-deg roof,
        # prints support-free in a vertical wall) + 4x M3 on the horn PCD.
        r = KNEE_HORN_CENTER_CLEAR / 2
        t = r / sqrt(2)
        with BuildSketch(Plane.XZ.offset(-(lug_out + 1))):
            with Locations((0, KNEE_AXIS_Z)):
                Circle(r)
            Polygon(
                (-t, KNEE_AXIS_Z + t),
                (t, KNEE_AXIS_Z + t),
                (0, KNEE_AXIS_Z + r * sqrt(2)),
                align=None,
            )
        extrude(amount=LUG_T + 2, mode=Mode.SUBTRACT)

        pcr = KNEE_HORN_PCD / 2
        horn_pts = [
            (
                pcr * cos(radians(a)),
                CLEVIS_HALF + LUG_T / 2,
                KNEE_AXIS_Z + pcr * sin(radians(a)),
            )
            for a in (45, 135, 225, 315)
        ]
        with Locations(*horn_pts):
            Cylinder(
                M3_CLEAR / 2, LUG_T + 2, rotation=(90, 0, 0), mode=Mode.SUBTRACT
            )

        # Inboard (-Y) lug: M3 clearance for the idler pivot screw.
        with Locations((0, -(CLEVIS_HALF + LUG_T / 2), KNEE_AXIS_Z)):
            Cylinder(
                M3_CLEAR / 2, LUG_T + 2, rotation=(90, 0, 0), mode=Mode.SUBTRACT
            )

        # Gravity-comp posts on the front (+Z) face, vertical in print.
        for px in CALF_POST_XS:
            z = CALF_DEPTH
            with Locations((px, CALF_POST_Y, z)):
                Cylinder(
                    POST_DIA / 2,
                    POST_BASE_LEN,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            with Locations((px, CALF_POST_Y, z + POST_BASE_LEN)):
                Cylinder(
                    POST_GROOVE_DIA / 2,
                    POST_GROOVE_W,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            with Locations((px, CALF_POST_Y, z + POST_BASE_LEN + POST_GROOVE_W)):
                Cone(
                    bottom_radius=POST_GROOVE_DIA / 2,
                    top_radius=POST_DIA / 2,
                    height=0.8,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )
            with Locations((px, CALF_POST_Y, z + POST_BASE_LEN + POST_GROOVE_W + 0.8)):
                Cylinder(
                    POST_DIA / 2,
                    0.8,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )

    return calf.part


if __name__ == "__main__":
    out = Path(__file__).parent / "output"
    out.mkdir(exist_ok=True)

    thigh = create_thigh()
    calf = create_calf()

    for name, part in (("thigh_link", thigh), ("calf_link", calf)):
        export_stl(part, str(out / f"{name}.stl"))
        export_step(part, str(out / f"{name}.step"))
        bb = part.bounding_box()
        print(
            f"{name}: {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm, "
            f"volume {part.volume / 1000:.1f} cm^3 -> {name}.stl / .step"
        )
