"""Alpha Centauri — hip module: the L1 link, one per leg (build123d).

    edu/.cadenv/bin/python cad/alpha_centauri/hip_module.py

WHAT THIS PART IS
-----------------
The physical L1 link. It clamps to the abduction servo's horn at the pod's hip
face and carries the thigh on the hip-pitch axis EXACTLY L1_LATERAL = 49.60 mm
outboard and L1_VERTICAL = 14.30 mm up from the abduction axis. L1 IS A
DIAGONAL — the single most-repeated mistake in this project — so the built
geometry is asserted to reproduce hypot(49.60, 14.30) == L1_HIP_OFFSET at
import, not trusted.

WHERE THE HIP-PITCH SERVO LIVES, AND THE TWO PLACES IT CANNOT
-------------------------------------------------------------
OUTBOARD-facing is LOCKED (decided before this file existed). Three
architectures satisfy "output faces outboard"; two die on measured geometry:

  * Servo in the hip module, horn engaging the thigh's INBOARD cheek: the
    body then spans the full SERVO_BODY_HEIGHT inboard of y = 115.7, reaching
    y = 78–81. The abduction pocket's outboard edge is at y = 102.56 and
    cannot move (its servo is centred on the abduction axis), so no possible
    pod recess clears it. Dead on arrival, by ~25 mm.
  * Servo in the hip module with its nose poking through the inboard cheek to
    the thigh's mid-plane (the stack the original ~1 mm/~3.8 mm interference
    estimate implies): the nose then sits INSIDE a box that pitches ±25 deg
    about the servo's own axis. The interior channel subtends only ±22 deg at
    the nose's 34 mm corner radius. The thigh sweeps through the servo. Dead.
  * Servo in the THIGH's hip end — the knee pattern verbatim, one thigh
    carrying both servos. The thigh's own section was sized for exactly this:
    SEC_Y is SERVO_BODY_HEIGHT + clearance + walls ("lateral: clevis span"),
    and its docstring already promises "the SAME bolt circle at each end. The
    driven side takes a servo horn; the idle side takes a small bearing
    carrier." This is the only survivor, and it is also the best one: the
    servo rotates WITH the thigh, so nothing sweeps through anything, and the
    hip module becomes a pure fork — the calf's own lug pattern, reused.

So: hip-pitch servo in the thigh, output boss ON the hip-pitch axis, horn
facing OUTBOARD. The module's OUTBOARD lug takes the standard horn_adapter
(drive side); the thigh's inboard bore takes the standard bearing_carrier,
whose 8 mm stub rides a 608ZZ seated in the module's INBOARD lug (idle side).
joint_parts.py carries the handedness, unchanged, exactly as at the knee.

NOTE, LOUDLY: thigh.py does NOT yet cut the hip-end servo cavity (its one
cavity is at the knee end). That is a thigh.py change mirroring its existing
knee cavity + structural cover, owned by the thigh, not this file. This
module's geometry consumes only the thigh's bores and outer cheek faces,
which exist today — the sweeps below run against the thigh AS DRAWN.

WHY THE BRIDGE GOES OVER THE TOP
--------------------------------
The two lugs must join outside the thigh. The calf converges BELOW its joint
because the calf hangs down and moves with the swing; here the fork is the
STATIC side and the thigh shaft occupies everything below the hip: at even
10 deg of pitch the shaft strip passes 7.9 mm from a point directly under the
axis. Above, the thigh can never reach past its own hip-end corner radius
(hypot(SEC_X/2, END_OVER) = 22.32 mm), so the bridge crosses at
+THIGH_SWEEP_R + 2.5 — the same keep-out convention calf.py uses at the knee.

THE ABDUCTION ROOT, AND WHY IT HAS ITS OWN ADAPTER
--------------------------------------------------
The root boss is a ring on the abduction axis, fully OUTBOARD (in X) of the
pod's open hip face — everything at x > the hip station is free space, which
is what keeps the boss out of the pod at every roll angle (it is coaxial with
the roll, so it spins in place). It clamps to the abduction horn through
ABD_ADAPTER, a NEW insert rather than joint_parts.horn_adapter, for one
reason: assembly access. The knee adapter's retain screws drive from the
0.5 mm gap side, which works only because the calf is bolted up before the
joint is mated. At the abduction root the equivalent face is 6 mm from the
pod; no driver fits. ABD_ADAPTER flips the stack — flange against the horn,
spigot pointing outboard into the boss's seat, retain screws driven from the
boss's OPEN outboard face, horn bolts reached through the boss's own bore.
Assembly order: bolt adapter to horn (fully exposed), press module onto the
spigot, drive three screws from outboard. No blind fastener anywhere.

All shared dimensions are IMPORTED (thigh section, calf lug pattern,
joint_parts bearing/horn interface, interface_constants hip frame). The
constants file cannot import CAD modules, so where it restates a lug number
the equality is ASSERTED here at import — restatement is guarded, not
trusted.

PRINT ORIENTATION — OUTBOARD LUG DOWN, SEAT AXES VERTICAL
---------------------------------------------------------
Same reasoning as the calf, same answer: the 608 seat and both adapter seats
are the fits that matter, so they print as vertical holes — the only kind an
FDM machine makes round. The one seat that cannot (the abduction boss bore,
axis orthogonal to the lug axes) gets a teardrop crown: its insert is a
static clamped spigot, not a running fit, so a gabled crown costs nothing.

PRINT-BLOCKED (LAW: unresolved servo height): this part's geometry derives
from SERVO_BODY_HEIGHT through the thigh section it straddles. It is drawn
parametrically and gate-checked at BOTH candidate heights (35.00 / 37.80) via
interface_constants._check(); it must not be printed until the caliper
resolves the height. The same block applies to the chassis pods and thigh.
"""

import copy
import math
import sys
from pathlib import Path

from build123d import (
    Align,
    Axis,
    BuildPart,
    Box,
    Compound,
    Cylinder,
    Face,
    Location,
    Locations,
    Mode,
    Solid,
    Vector,
    Wire,
    add,
    export_step,
    export_stl,
    import_step,
)

from interface_constants import (
    HIP_ABDUCTION_RANGE_DEG,
    HIP_LUG_CLEAR,
    HIP_LUG_R,
    HIP_LUG_T,
    HIP_PITCH_RANGE_DEG,
    HIP_POD_FACE_Y,
    HIP_POD_GAP,
    L1_HIP_OFFSET,
    L1_LATERAL,
    L1_VERTICAL,
    L2_THIGH,
    LEG_FB,
    LEG_PLANE_Y,
    SERVO_BODY_HEIGHT,
    STANCE_Z,
    extension_at,
    hip_thigh_sec_y,
)
from thigh import HORN_BOLT, HORN_PCD, JOURNAL_D, SEC_Y as THIGH_SEC_Y
from calf import (
    LUG_GAP,
    LUG_R,
    LUG_T,
    RETAIN_N,
    RETAIN_PCD,
    SEAT_D,
    SEAT_DEPTH,
    THIGH_SWEEP_R,
)
from joint_parts import BRG_OD, FLANGE_D, FLANGE_T, HUB_RELIEF_D, PRESS

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "edu/tools"))

HERE = Path(__file__).parent
OUT = HERE / "output"

# ---------------------------------------------------------------- fasteners
# HORN_BOLT is imported from thigh above (law 8) — joint_parts.py's pattern.
M3_CLEAR, M3_PILOT = 3.4, 2.6      # ISO M3 clearance/pilot, standard sizes

# ------------------------------------------------- guarded restatements
# interface_constants cannot import the CAD modules (they import it), so its
# hip-frame numbers restate the calf/thigh lug pattern. If any of these fire,
# someone changed one copy without the other — the exact failure D11 exists
# to prevent.
assert LUG_T == HIP_LUG_T, f"calf LUG_T {LUG_T} != HIP_LUG_T {HIP_LUG_T}"
assert LUG_R == HIP_LUG_R, f"calf LUG_R {LUG_R} != HIP_LUG_R {HIP_LUG_R}"
assert abs((LUG_GAP - THIGH_SEC_Y) / 2 - HIP_LUG_CLEAR) < 1e-9, (
    f"calf lug clearance {(LUG_GAP - THIGH_SEC_Y) / 2} != HIP_LUG_CLEAR "
    f"{HIP_LUG_CLEAR}"
)
assert abs(THIGH_SEC_Y - hip_thigh_sec_y(SERVO_BODY_HEIGHT)) < 1e-9, (
    f"thigh SEC_Y {THIGH_SEC_Y} != hip_thigh_sec_y({SERVO_BODY_HEIGHT})"
)
assert SEAT_D == JOURNAL_D == BRG_OD, "22 mm 608ZZ interface broken"
# The L1 diagonal, rebuilt from the primitives this module places.
assert abs(math.hypot(L1_LATERAL, L1_VERTICAL) - L1_HIP_OFFSET) < 1e-5

# ---------------------------------------------------------------- the frame
# Module-local frame: ROBOT-ALIGNED axes, origin ON THE HIP-PITCH AXIS at the
# leg plane. +X is the abduction-horn side (robot-forward for the front-left
# leg this file authors), +Y outboard, +Z up. The abduction axis runs along X
# through (0, -L1_LATERAL, -L1_VERTICAL) — the L1 diagonal, stated once.
ABD_Y, ABD_Z = -L1_LATERAL, -L1_VERTICAL

# Fork stations, straight off the thigh section (SERVO_BODY_HEIGHT-dependent).
LUG_IN = THIGH_SEC_Y / 2 + HIP_LUG_CLEAR        # lug INNER face |y|, 21.20
LUG_OUT = LUG_IN + LUG_T                        # lug OUTER face |y|, 27.20

# Over-bridge: crosses ABOVE the thigh's swept envelope (see docstring).
BRIDGE_Z0 = THIGH_SWEEP_R + 2.5                 # 24.82 -> underside at 24.82
BRIDGE_Z1 = BRIDGE_Z0 + 8.0                     # 8 mm deep in bending
ARM_W = 24.0                                    # arm/bridge width in X
ARM_Z0 = 8.0                                    # arms leave the lug rims here

# Abduction root. The horn arm's outer face sits ABD_HORN_STANDOFF proud of
# the pod's hip face (output boss + horn hub, NOMINAL — the vendor STEP's
# 2.80 mm height excess is exactly the boss, see interface_constants §3).
# Everything about the root lives at x >= +ABD_HORN_STANDOFF, which is
# OUTBOARD (in X) of the pod's open face — free space at every roll angle.
ABD_HORN_STANDOFF = 6.0        # NOMINAL  P0 caliper gate, like HORN_PCD
ABD_FLANGE_T = FLANGE_T        # 3.0, adapter flange against the horn
ABD_BOSS_X0 = ABD_HORN_STANDOFF + ABD_FLANGE_T  # boss inboard face, +9
ABD_BOSS_T = 10.0              # seat (6) + open counterbore (4)
ABD_BOSS_R = FLANGE_D / 2      # 18.0 — same meat around the bolts as the
                               # knee inserts carry
ABD_CBORE_D = 24.0             # driver access to the horn bolts

# Inboard-lug tab + web that carry the fork loads down to the boss. The web
# is PROUD of the lug's outer face, so it must stay outside the r=18 flange
# zone (the bearing retainer needs that face flat) — its closest corner sits
# at hypot(9, 20) = 21.9 from the axis. The tab is IN-PLANE with the lug
# (flush faces), so it may cross the flange zone freely: coplanar material
# under the flange is support, not obstruction.
TAB_X0, TAB_X1 = 2.0, 19.0
TAB_Z0, TAB_Z1 = -34.0, -12.0
WEB_X0, WEB_X1 = ABD_BOSS_X0, ABD_BOSS_X0 + ABD_BOSS_T   # +9 .. +19
WEB_Z0, WEB_Z1 = -34.0, -20.0
assert math.hypot(WEB_X0, abs(WEB_Z1)) > LUG_R + 1.0, (
    "web encroaches the lug's flange zone — the retainer needs that face"
)

# The bridge must actually clear the thigh's swept corner.
assert BRIDGE_Z0 - THIGH_SWEEP_R >= 2.5 - 1e-9


def _teardrop_x(dia, length, apex=45.0):
    """A bore along +X with a gabled crown toward -Y.

    Same technique as thigh._teardrop, rotated for this part's print
    orientation: printed outboard-lug-down the +Y axis points DOWN, so the
    crown that needs the gable faces -Y. The abduction seat is the one bore
    in this part whose axis cannot print vertical; its insert is a clamped
    static spigot, so a non-circular crown is affordable where it never
    would be on the 608 seat.
    """
    r = dia / 2.0
    a = math.radians(apex)
    tip = r / math.sin(a)
    pts, n = [], 48
    for i in range(n + 1):
        th = math.radians(90 + apex) + math.radians(360 - 2 * apex) * i / n
        # profile in the YZ plane; crown apex toward -Y
        pts.append(Vector(0, -r * math.sin(th), r * math.cos(th)))
    pts.append(Vector(0, -tip, 0))
    face = Face(Wire.make_polygon(pts, close=True))
    return Solid.extrude(face, Vector(length, 0, 0))


def create_hip_module():
    """The fork + root, authored in the module-local frame (front-left)."""
    with BuildPart() as part:
        # --- the two lugs: the calf's own pattern, one per cheek -----------
        for sy in (-1, 1):
            with Locations((0, sy * (LUG_IN + LUG_T / 2), 0)):
                Cylinder(radius=LUG_R, height=LUG_T,
                         rotation=(90, 0, 0), align=Align.CENTER)
            # arm up the lug plane to the bridge
            with Locations((0, sy * (LUG_IN + LUG_T / 2),
                            (ARM_Z0 + BRIDGE_Z1) / 2)):
                Box(ARM_W, LUG_T, BRIDGE_Z1 - ARM_Z0, align=Align.CENTER)

        # --- over-bridge, above the thigh's swept corner -------------------
        with Locations((0, 0, (BRIDGE_Z0 + BRIDGE_Z1) / 2)):
            Box(ARM_W, 2 * LUG_OUT, BRIDGE_Z1 - BRIDGE_Z0, align=Align.CENTER)

        # --- inboard-lug tab (in-plane) + web down to the boss -------------
        with Locations(((TAB_X0 + TAB_X1) / 2, -(LUG_IN + LUG_T / 2),
                        (TAB_Z0 + TAB_Z1) / 2)):
            Box(TAB_X1 - TAB_X0, LUG_T, TAB_Z1 - TAB_Z0, align=Align.CENTER)
        web_y0, web_y1 = -33.0, -LUG_IN          # flush with lug inner plane
        with Locations(((WEB_X0 + WEB_X1) / 2, (web_y0 + web_y1) / 2,
                        (WEB_Z0 + WEB_Z1) / 2)):
            Box(WEB_X1 - WEB_X0, web_y1 - web_y0, WEB_Z1 - WEB_Z0,
                align=Align.CENTER)

        # --- abduction root boss, coaxial with the roll --------------------
        with Locations((ABD_BOSS_X0 + ABD_BOSS_T / 2, ABD_Y, ABD_Z)):
            Cylinder(radius=ABD_BOSS_R, height=ABD_BOSS_T,
                     rotation=(0, 90, 0), align=Align.CENTER)

        # --- SUBTRACT, all of it after all the adds ------------------------
        # lug seats: 608ZZ / horn-adapter spigot, opening at the OUTER faces,
        # 1 mm proud toward the thigh exactly as the calf seats its bearings
        for sy in (-1, 1):
            with Locations((0, sy * (LUG_IN + LUG_T - SEAT_DEPTH / 2), 0)):
                Cylinder(radius=SEAT_D / 2, height=SEAT_DEPTH,
                         rotation=(90, 0, 0), align=Align.CENTER,
                         mode=Mode.SUBTRACT)
        # through-hole for the carrier stub / horn boss
        Cylinder(radius=4.6, height=2 * LUG_OUT + 4,
                 rotation=(90, 0, 0), mode=Mode.SUBTRACT)
        # retain circles, both lugs, both the same — handedness by insert
        for sy in (-1, 1):
            for i in range(RETAIN_N):
                th = math.radians(90 + 360 * i / RETAIN_N)
                with Locations((RETAIN_PCD / 2 * math.cos(th),
                                sy * (LUG_IN + LUG_T / 2),
                                RETAIN_PCD / 2 * math.sin(th))):
                    Cylinder(radius=M3_CLEAR / 2, height=LUG_T * 3,
                             rotation=(90, 0, 0), mode=Mode.SUBTRACT)

        # abduction seat: adapter spigot, teardropped (see _teardrop_x),
        # then the open counterbore that gives the horn bolts their driver
        add(_teardrop_x(SEAT_D, SEAT_DEPTH - 1.0)
            .moved(Location((ABD_BOSS_X0, ABD_Y, ABD_Z))), mode=Mode.SUBTRACT)
        # counterbore starts EXACTLY at the spigot's end: the horn-bolt heads
        # stand proud there (r up to ~11.25 on an M3 head) and would rub a
        # 22 mm seat wall (r 11.0) — they need the 24 mm bore from +0 up
        with Locations((ABD_BOSS_X0 + (SEAT_DEPTH - 1.0)
                        + (ABD_BOSS_T - (SEAT_DEPTH - 1.0) + 0.2) / 2,
                        ABD_Y, ABD_Z)):
            Cylinder(radius=ABD_CBORE_D / 2,
                     height=ABD_BOSS_T - (SEAT_DEPTH - 1.0) + 0.2,
                     rotation=(0, 90, 0), align=Align.CENTER,
                     mode=Mode.SUBTRACT)
        # abduction retain screws: driven from the OPEN outboard face,
        # through the boss, into the adapter flange's pilots
        for i in range(RETAIN_N):
            th = math.radians(90 + 360 * i / RETAIN_N)
            with Locations((ABD_BOSS_X0 + ABD_BOSS_T / 2,
                            ABD_Y + RETAIN_PCD / 2 * math.cos(th),
                            ABD_Z + RETAIN_PCD / 2 * math.sin(th))):
                Cylinder(radius=M3_CLEAR / 2, height=ABD_BOSS_T * 2,
                         rotation=(0, 90, 0), mode=Mode.SUBTRACT)

    return part.part


def create_abd_adapter():
    """Abduction horn adapter — joint_parts.horn_adapter with the stack
    flipped for driver access (see docstring). Flange toward the horn,
    spigot toward the boss, every fastener reachable from outboard.

    Built about +Z like the knee inserts: flange z 0..FLANGE_T against the
    horn's arm face, spigot reaching up into the boss seat. Prints
    flange-down, no supports.
    """
    with BuildPart() as part:
        Cylinder(radius=FLANGE_D / 2, height=ABD_FLANGE_T,
                 align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, 0, ABD_FLANGE_T)):
            Cylinder(radius=(SEAT_D - PRESS) / 2, height=SEAT_DEPTH - 1.0,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
        # horn hub + retaining-screw-head relief, on the HORN side. The
        # diameter is joint_parts' own HUB_RELIEF_D: the first cut here used
        # a restated 13.0 and partcheck flagged the 0.55 mm ligament it left
        # against the bolt holes — law 8 exists for exactly this.
        Cylinder(radius=HUB_RELIEF_D / 2, height=2.5,
                 align=(Align.CENTER, Align.CENTER, Align.MIN),
                 mode=Mode.SUBTRACT)
        # horn bolt circle: plain through-holes. NO head counterbores — a
        # 6.5 mm counterbore at the 17 mm PCD breaks through the 21.85 mm
        # spigot's side wall (r 8.5 + 3.25 > r 10.9), which partcheck flagged
        # as twelve thin-wall clusters. The heads stand proud of the spigot's
        # end face instead, inside the boss's 24 mm access counterbore, which
        # is 4 mm deep against a ~2.5 mm head.
        for i in range(4):
            th = math.radians(45 + 90 * i)
            x, y = (HORN_PCD / 2 * math.cos(th), HORN_PCD / 2 * math.sin(th))
            with Locations((x, y, 0)):
                Cylinder(radius=HORN_BOLT / 2,
                         height=ABD_FLANGE_T + SEAT_DEPTH + 2,
                         align=(Align.CENTER, Align.CENTER, Align.MIN),
                         mode=Mode.SUBTRACT)
        # retain pilots for the three screws driven from the boss side
        for i in range(RETAIN_N):
            th = math.radians(90 + 360 * i / RETAIN_N)
            with Locations((RETAIN_PCD / 2 * math.cos(th),
                            RETAIN_PCD / 2 * math.sin(th), 0)):
                Cylinder(radius=M3_PILOT / 2, height=ABD_FLANGE_T * 2,
                         align=(Align.CENTER, Align.CENTER, Align.MIN),
                         mode=Mode.SUBTRACT)
    return part.part


# ------------------------------------------------------------------ posing
def thigh_posed(thigh_solid, pitch_deg):
    """The thigh in module-local frame at a given pitch aft of vertical.

    thigh.py authors hip axis at origin, +Z running hip->knee; in the robot
    the knee hangs down-aft, so the aim direction is (-sin p, 0, -cos p) —
    the same atan2 convention assembly._aim uses.
    """
    p = math.radians(pitch_deg)
    ang = math.degrees(math.atan2(-math.sin(p), -math.cos(p)))
    return thigh_solid.rotate(Axis.Y, ang)


def rolled(solid, roll_deg):
    """Rotate about the ABDUCTION axis — the X line through (ABD_Y, ABD_Z)."""
    return solid.rotate(Axis((0, ABD_Y, ABD_Z), (1, 0, 0)), roll_deg)


def _vol(a, b):
    hit = a & b
    return 0.0 if hit is None else hit.volume


# --------------------------------------------------------------------- build
if __name__ == "__main__":
    from partcheck import check

    OUT.mkdir(exist_ok=True)

    mod = create_hip_module()
    abd = create_abd_adapter()
    bb = mod.bounding_box()

    print(f"hip module (module-local frame, front-left):")
    print(f"  bbox {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm, "
          f"{mod.volume / 1000:.1f} cm3, PETG ~{mod.volume / 1000 * 0.953:.1f} g")
    print(f"  abd adapter {abd.volume / 1000:.1f} cm3, "
          f"~{abd.volume / 1000 * 0.953:.1f} g")
    print(f"  lug faces |y| {LUG_IN:.2f}..{LUG_OUT:.2f}   bridge z "
          f"{BRIDGE_Z0:.2f}..{BRIDGE_Z1:.2f}   boss x {ABD_BOSS_X0:.1f}.."
          f"{ABD_BOSS_X0 + ABD_BOSS_T:.1f} on the L1 diagonal "
          f"({ABD_Y:.2f}, {ABD_Z:.2f})")

    # --- THE GEOMETRIC CONTRACT (law 7): the built hip-pitch axis sits on
    # the L1 diagonal from the built abduction axis. The module is authored
    # with the hip-pitch axis AT the origin and the abduction boss ON
    # (ABD_Y, ABD_Z); reproduce the diagonal from those placed values.
    built = math.hypot(-ABD_Y, -ABD_Z)
    assert abs(built - L1_HIP_OFFSET) < 1e-5, (
        f"built L1 {built:.6f} != {L1_HIP_OFFSET:.6f}"
    )
    print(f"\nL1 contract: hypot({-ABD_Y}, {-ABD_Z}) = {built:.5f} "
          f"== L1_HIP_OFFSET  OK")

    # --- exports, BEFORE the sweeps ----------------------------------------
    # (the sweeps only read; exporting first means a red sweep still leaves
    # inspectable artifacts on disk, and the first run of this file proved
    # that sharing solids with a Compound can poison a later export)
    export_step(mod, str(OUT / "hip_module.step"))       # module-local frame
    export_step(abd, str(OUT / "abd_adapter.step"))
    # print pose: outboard lug face on the bed, seat axes vertical. The sign
    # matters and partcheck caught it: +90 stands the part on the boss's
    # cylindrical rim — 45 mm2 of tangent-line bed contact on a 95 mm part,
    # which shears off mid-print. -90 puts the outboard lug flat down.
    printed = mod.rotate(Axis.X, -90)
    pbb = printed.bounding_box()
    printed = printed.moved(Location((0, 0, -pbb.min.Z)))
    export_stl(printed, str(OUT / "hip_module.stl"))
    export_stl(abd, str(OUT / "abd_adapter.stl"))

    # --- load neighbours for the interference sweeps -----------------------
    thigh_p = OUT / "thigh_shell.step"
    chassis_p = OUT / "chassis_half.step"
    assert thigh_p.exists() and chassis_p.exists(), (
        "run thigh.py and chassis.py first — the sweeps need their STEPs"
    )
    thigh_s = import_step(str(thigh_p)).solids()[0]
    # chassis -> module-local: hip station at (LEG_FB, LEG_PLANE_Y, HIP_Z +
    # L1_VERTICAL) in chassis coordinates. HIP_Z is chassis.py's own number
    # (law 8) — imported here, with the pod extents the probe below needs.
    from chassis import HIP_Z, POD_X0, POD_Z0, POD_Z1

    hip_z = HIP_Z
    chassis_s = import_step(str(chassis_p)).moved(
        Location((-LEG_FB, -LEG_PLANE_Y, -(hip_z + L1_VERTICAL))))

    # --- SWEEP (a): thigh through the FULL hip-pitch working range, at zero
    # roll, against the recessed pod/chassis AND against this module. LAW 5:
    # single-part checks are blind to this; the assert is permanent.
    lo, hi = HIP_PITCH_RANGE_DEG
    pitches = sorted({0.0, lo, 15.0, 22.3, 30.0, 40.0, 50.0, hi, hi + 5.0})
    print(f"\nsweep (a): thigh pitch {lo}..{hi} deg (+margin poses) "
          f"vs chassis + hip module")
    worst_a = 0.0
    for p in pitches:
        tp = thigh_posed(thigh_s, p)
        v1, v2 = _vol(tp, chassis_s), _vol(tp, mod)
        worst_a = max(worst_a, v1, v2)
        print(f"  pitch {p:5.1f} deg -> chassis {v1 / 1000:7.3f} cm3  "
              f"module {v2 / 1000:7.3f} cm3   "
              f"{'CLEAR' if max(v1, v2) < 1e-6 else 'COLLIDE'}")
    assert worst_a < 1e-6, (
        f"thigh sweeps into a neighbour: {worst_a / 1000:.3f} cm3"
    )

    # --- SWEEP (b): module + thigh through the FULL abduction range vs the
    # chassis. The thigh rides at both pitch extremes — the lug is roll's
    # worst case, the thigh shaft is pitch's; both must clear at once.
    rr = HIP_ABDUCTION_RANGE_DEG
    rolls = [-rr, -6.0, -rr / 2, -2.0, 0.0, 2.0, rr / 2, 6.0, rr]
    print(f"\nsweep (b): module+thigh roll +/-{rr} deg vs chassis")
    worst_b = 0.0
    for p in (lo, hi):
        tp = thigh_posed(thigh_s, p)
        # copies: Compound(children=...) re-parents its children's shapes,
        # which broke export_step(mod) downstream the first time this ran
        pair = Compound(children=[copy.copy(mod), copy.copy(tp)])
        for r in rolls:
            v = _vol(rolled(pair, r), chassis_s)
            worst_b = max(worst_b, v)
            print(f"  pitch {p:5.1f}  roll {r:+5.1f} deg -> "
                  f"{v / 1000:7.3f} cm3   {'CLEAR' if v < 1e-6 else 'COLLIDE'}")
    assert worst_b < 1e-6, (
        f"module/thigh sweeps into the chassis: {worst_b / 1000:.3f} cm3"
    )

    # The clearance the recess was derived for, measured off the real solids.
    # NOT a bare bbox: the first version of this check measured min-Y of the
    # whole cropped module and failed on the bridge's top corner — which does
    # roll 1.5 mm inside the pod face's PLANE, but 29 mm ABOVE the pod's top,
    # where there is no pod. The honest probe is the pod's own envelope
    # (imported from chassis.py, never restated) grown by HIP_POD_GAP on the
    # outboard side: any module material inside it at any roll angle means
    # the running clearance is broken. (POD_X0/POD_Z0/POD_Z1 and HIP_Z were
    # imported from chassis above, where the neighbours load.)
    hip_dz = hip_z + L1_VERTICAL
    probe = Box(LEG_FB - POD_X0, 60.0 + HIP_POD_GAP, POD_Z1 - POD_Z0,
                align=(Align.MAX, Align.MAX, Align.MIN)).moved(
        Location((0, HIP_POD_FACE_Y - LEG_PLANE_Y + HIP_POD_GAP,
                  POD_Z0 - hip_dz)))
    worst_probe, near = 0.0, None
    for r in rolls:
        rm = rolled(mod, r)
        worst_probe = max(worst_probe, _vol(rm, probe))
        band = rm & Box(LEG_FB - POD_X0, 400, POD_Z1 - POD_Z0,
                        align=(Align.MAX, Align.CENTER, Align.MIN)).moved(
            Location((0, 0, POD_Z0 - hip_dz)))
        if band is not None and band.volume > 1e-9:
            y = LEG_PLANE_Y + band.bounding_box().min.Y
            near = y if near is None else min(near, y)
    print(f"\nswept module, inside the pod's x/z band: closest lateral "
          f"approach y = {near:.2f} (robot), recessed pod face "
          f"{HIP_POD_FACE_Y:.2f} -> {near - HIP_POD_FACE_Y:.2f} mm running "
          f"gap; HIP_POD_GAP {HIP_POD_GAP}")
    assert worst_probe < 1e-6, (
        f"swept module enters the pod's {HIP_POD_GAP} mm clearance "
        f"envelope: {worst_probe / 1000:.3f} cm3"
    )

    check(printed, "hip_module", out_dir=str(OUT), material="PETG")
    check(abd, "abd_adapter", out_dir=str(OUT), material="PETG")

    # --- one full leg chain, posed at stance, for the hero render ----------
    # Chassis + recessed pod + hip module + thigh + calf, robot frame. The
    # calf pose reuses the same solve as assembly.py rather than restating.
    calf_p = OUT / "calf.step"
    if calf_p.exists():
        import assembly as A

        alpha, knee, ext = A.solve_leg(STANCE_Z)
        origin = Vector(LEG_FB, LEG_PLANE_Y, hip_z + L1_VERTICAL)
        hip_pt = tuple(origin)
        knee_pt = (hip_pt[0] - L2_THIGH * math.sin(math.radians(alpha)),
                   hip_pt[1],
                   hip_pt[2] - L2_THIGH * math.cos(math.radians(alpha)))
        foot_pt = (hip_pt[0], hip_pt[1], hip_pt[2] - extension_at(STANCE_Z))
        calf_s = import_step(str(calf_p)).solids()[0]
        chain = Compound(children=[
            import_step(str(chassis_p)),
            mod.moved(Location(hip_pt)),
            A._aim(thigh_s, hip_pt, knee_pt),
            A._aim(calf_s, knee_pt, foot_pt),
        ])
        export_step(chain, str(OUT / "hip_leg_chain.step"))
        print(f"\nleg chain at stance (alpha {alpha:.2f}, knee {knee:.2f}) "
              f"-> {OUT / 'hip_leg_chain.step'}")

    print("\nPRINT-BLOCKED: servo height unresolved (35.00 vs 37.80) — "
          "drawn parametrically, gated at both; do not print before the "
          "caliper.")
