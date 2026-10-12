"""Alpha Centauri -- dock, pack sled, latch, contact probe (REPLAN item 7).

Stages S1 (self-docking recharge, hardware) and S2a (manual-swap interfaces)
of edu/REPLAN-2026-08-28.md section 3. Robot side: pack sled x2, latch x2,
contact probe x1. Floor side: funnel, two column segments, base with a brick
cradle, ArUco tag mast. Every number below is printed by `__main__` from the
geometry (run it; it exits 1 if any gate fails):

    edu/.cadenv/bin/python cad/alpha_centauri/dock.py      (from cad/alpha_centauri/)

chassis.py is IMPORTED, never edited: BAY_*, PACK_*, LATCH_*, CONTACT_PILOT_YZ,
quarters_placed(). Rear legs come from assembly_centaur.leg_at() at WALK
stance; rear ways from waist_rail.way_run(). Nothing is restated.

FRAME. Robot frame of chassis.py (X fore, Z up from the chassis floor), robot
DOCKED. Ground is the foot point from assembly_centaur: z = -199.0 (ride height
199.0 mm). Dock parts are authored where they stand when the robot is docked.

LAWS APPLIED
  * Things that move get swept, not posed: sled lift (+90), latch release
    (7 poses 0..8.5 deg), robot capture (20 poses, both sides).
  * Bed fit is judged on the MEASURED bbox in the PRINT pose, never at the
    nominal 245 diagonal (interface_constants BED_DIAGONAL_MAX): every part
    fits 180^3 square.
  * A flexure bends IN the layer plane: the latch prints lying on its side.
  * A latch that holds with a preloaded spring creeps; this one does not --
    the leaf is straight when engaged and only bends during insert/release.

1. PACK SLED (pack_sled, x2, one geometry for both bays)
   75.0 x 58.0 footprint = the chassis envelope exactly (bay fit 1.0/side is
   chassis.py's). DECISION: THE SLED IS THE CELL HOLDER. A commercial 3-slot
   18650 holder is ~77 long by chassis.py's own docstring -- it does not fit a
   75 envelope, let alone inside a carrier. The sled cradles a spot-welded 3S1P
   (three cells side by side, 18.7 pitch, grooves r 9.45 on a 6 mm floor) in a
   66.50 mm bay (65.2 cell + 2 x 0.15 nickel + 0.5). The BMS lies on the cells
   under z 24 on four M2 pilots in the end-wall tops. ABOVE the envelope: a
   T-handle (web 6 wide, cap 16 wide with 45 deg undersides, top at local z 40)
   the station grips, and the catch post (local x 28..37.5, top z 52) with the
   latch pocket (3.5 deep, 17 wide, hold-down face at local z 40.7). The pocket
   is 17 wide so the tooth, 2 mm outboard of the pack centre in either bay
   (LATCH_Y 33.5 vs BAY_Y 31.5), fits one sled -- no mirrored part.
   GATES: sled vs rear quarters 0; lift sweep of the sled's measured bbox
   (+90, to z 146) vs quarters 0 and vs rear way segments 0, sled edge |y| 60.5
   to way head 63.0 = 2.5 mm (the chassis figure, unchanged).

2. LATCH (pack_latch, x2) -- print-in-place flexure, PETG (not -CF: flexure)
   Base 16 x 16 x 4 on the boss top (z 18), two M3 x 10 SHCS into the chassis
   pilots (gate: holes coaxial). Leaf 1.2 x 12, L 30 (z 22..52), tooth at
   z 45..52 reaching 2.5 mm into the sled post (flat underside = hold-down,
   45 deg top = the sled cams it aside on the way in -- self-latching), and a
   45 deg release cam on top. The station pusher DESCENDS on the cam at x ~-146
   and walks the leaf +X: stroke ~4.8 mm (rigid-rotation estimate).
   Strain (cantilever, tooth at a = 23 of L = 30):
     insertion 2.50 mm at the tooth -> tip 3.81, 0.762 %, 13.0 MPa, SF 1.93
     release   3.40 mm at the tooth -> tip 5.18, 1.036 %, 17.6 MPa, SF 1.42
     (E 1700, allowable 25 MPa -- waist_rail.py's house figures); force 1.69 N.
   GATES: engaged latch vs sled 0; engaged latch INSIDE the lift sweep 97.5 mm3
   (it actually blocks the lift); release motion vs sled 0 at all 7 poses;
   released latch vs lift sweep 0; latch vs quarters 0 engaged and released.
   The released pose is a RIGID rotation about the leaf root -- a stand-in for
   the bent shape; the strain numbers use the real cantilever shape.

3. CONTACT PROBE (contact_probe, x1) + two purchased blades
   Flange 6 x 56 x 46 on the four M3 contact pilots (M3 x 10, 2 mm counterbores)
   carrying a 28 x 28 beam aft to a nose at x -345 (nose tapers to 12 x 12 over
   8 mm). WHY A PROBE AND NOT A FLAT BLOCK: the funnel must stay aft of the
   chassis end (x -250) -- the pods and legs own everything forward of it -- so
   the funnel can only be as deep as the probe is long. A 22 mm block allowed a
   ~20 mm funnel; the 95 mm probe allows a 98 mm funnel.
   Blades: phosphor bronze C51000 strip 0.25 x 8, free length 23, clamped by an
   M2 at x -334, angled out to |y| 18.5 free; the throat (|y| 15) compresses
   them 3.50 mm -> 273 MPa (< 0.8 x 500 handbook yield), 0.99 N per blade. They
   ride on brass strips 0.5 x 10 x 42 flush in the throat walls; the blade tip
   meets the strip 13.4 mm before seating = the WIPE. Blades are trailing
   (root aft, tip forward) so the throat cannot snag them. +Y = +, -Y = -.

4. DOCK (floor station)
   dock_funnel: rectangular V -- throat +/-15 x z 19..49 (1 mm running fit on
   the beam), mouth +/-54 x z 2..66 at x -255 (5 mm short of the chassis end),
   V half-angles 44.3 deg (y) and 23.0 deg (z), backstop 8 thick at the nose.
   Prints standing on the backstop, mouth up: every wall leans <= 45 deg.
   GEOMETRIC CAPTURE: y +/-48.0 mm, z +/-26.0 mm = mouth inner half-width minus
   the nose half-width (54 - 6; 32 - 6). Wu et al. 2012 reported +/-8 mm from
   their passive funnel; ours is geometry only -- see NOT DONE.
   Legs are NOT the limit here: docked, leg inner |y| to funnel outer = 54.4 mm.
   GATES: docked, rear quarters + ways + legs vs every dock part 0, probe body
   vs dock 0; capture sweep 20 poses (entry offset +/-47.5 at the mouth, walked
   to 0 as the V allows, both sides) robot vs dock 0.
   dock_column_lower / _upper: 40 x 40 tube, 60 x 60 flanges, 4 x M4, 24 x 24
   cable bore; 45 deg skirt under the top flange (prints without a bridge).
   dock_base: 175 x 160 x 5 plate, nut recesses under the column bolts, four
   floor-screw holes, and a cradle 52 x 92 x 18 for a 12.6 V CC/CV brick with
   strap slots. dock_tag_mast: 4 mm plate + rib, M3 x 2 into the backstop, a
   100 x 100 face for a 90 mm ArUco tag centred at z 152 (351 above ground),
   printed face-down.
   Tag sightline: the phone is NOT in CAD; ASSUMED at the waist-box rim at the
   WALK station (x 37, z 152). The ray to the tag's bottom edge crosses the
   chassis end at z 118.9, above the deck (84). Docked distance 390 mm. The
   robot backs in and the phone's FRONT (selfie) camera looks aft -- DECISION,
   so no 180 deg turn is needed at the dock.

PARTS (print pose, PETG, partcheck): printed by __main__ as PART TABLE.

REJECTED
  * Commercial 3-slot holder screwed into a sled: 77 > 75 envelope (above).
  * Floor-level V-rail catching the feet (Roomba literal): the feet step,
    they do not slide; the rear end is the only part that arrives continuously.
  * Funnel walls around the chassis body: pods at |y| 104.2 and knees at
    |y| >= 112.4 leave no room forward of x -250.
  * Horizontal latch leaf pushed DOWN to release: pushing a hook down drives
    it deeper. The vertical leaf + 45 deg cam turns a downward push into +X.
  * Separate metal leaf for the latch: an extra part for a 1.7 N spring the
    printed leaf delivers at SF 1.42.

NOT DONE
  * S2b motorized station (rack-pinion pusher + gripper); only its interfaces
    (T-handle, release cam at z 52..59) exist.
  * Charge electronics and wiring: robot CC/CV + 3S balance BMS board, ideal
    diodes, timer cutoff, blade leads (M2 ring terminals, no wire channel is
    modelled in the probe), brick-to-strip leads up the column bore.
  * PACK-TO-BUS CONNECTION IN THE BAY: a swapped pack needs a blind-mate
    connector (bay floor contacts or a floating XT30) -- not designed, and
    S2 cannot work without it.
  * The capture tolerance is GEOMETRIC. The feet resist lateral correction;
    whether the funnel can walk the robot 48 mm sideways, or the gait must do
    it from the ArUco pose, is what the S1 gate (5/5 from ~1 m) measures.
    Yaw error was not swept. Leg SWING during the back-in was not swept.
  * Cell/brick dimensions are class values (18650 max 18.6 x 65.2; brick
    cradle for a 50 x 90 class brick): caliper the purchased parts first.
  * Dock tipping under the robot's push: base has floor-screw holes; no
    weighting computed. Run it on a fireproof tile (REPLAN S1 stack).
"""

import copy
import math
from pathlib import Path
import sys

from build123d import (
    Align,
    Axis,
    Box,
    Compound,
    Cylinder,
    Face,
    Location,
    Solid,
    Vector,
    Wire,
    export_step,
    export_stl,
    import_step,
)

import chassis as C                      # IMPORT ONLY -- never edited from here
import waist_rail as R
from interface_constants import BED_X, BED_Y, BED_Z, STANCE_Z

HERE = Path(__file__).parent
OUT = HERE / "output" / "dock"
EVID = HERE.parent.parent / "docs" / "evidence"
sys.path.insert(0, str(HERE.parent.parent / "edu/tools"))

M2_PILOT = 1.6
M4_CLEAR, M4_PILOT = C.M4_CLEAR, C.M4_PILOT
M3_CLEAR, M3_PILOT = C.M3_CLEAR, C.M3_PILOT

# ------------------------------------------------------------ material house
E_PETG, SIGMA_PETG = R.E_PETG, R.SIGMA_PETG          # 1700 MPa, 25 MPa allowable
E_PB = 110000.0          # MPa  phosphor bronze C51000 (handbook class value)
SIGMA_PB_YIELD = 500.0   # MPa  C51000 spring temper, handbook class value (INPUT)

# ------------------------------------------------------------ robot frame
GROUND_Z = None          # filled from assembly geometry in _legs()
BAY_XS = -C.BAY_X                        # -190, the rear (populated) bays
LATCH_XC = -C.LATCH_X                    # -140.5, rear boss centre
BOSS_X0 = LATCH_XC - C.LATCH_BOSS / 2    # -148.5, boss face toward the bay
BOSS_TOP = C.FLOOR_T + C.LATCH_BOSS_H    # 18
PACK_X_IN = BAY_XS + C.PACK_L / 2        # -152.5, the sled's inboard face
REAR_FACE_X = -C.OUTER_X1                # -250, contact face


def box(x0, x1, y0, y1, z0, z1):
    return Box(x1 - x0, y1 - y0, z1 - z0, align=Align.MIN).moved(Location((x0, y0, z0)))


def xz_prism(pts, y0, y1):
    """Polygon in the X-Z plane, extruded along +Y from y0 to y1."""
    w = Wire.make_polygon([Vector(x, y0, z) for x, z in pts], close=True)
    return Solid.extrude(Face(w), Vector(0, y1 - y0, 0))


def yz_prism(pts, x0, x1):
    w = Wire.make_polygon([Vector(x0, y, z) for y, z in pts], close=True)
    return Solid.extrude(Face(w), Vector(x1 - x0, 0, 0))


def rect_x(x, y0, y1, z0, z1):
    return Wire.make_polygon([Vector(x, y0, z0), Vector(x, y1, z0),
                              Vector(x, y1, z1), Vector(x, y0, z1)], close=True)


def cyl_x(r, x0, x1, y, z):
    return Cylinder(r, x1 - x0, rotation=(0, 90, 0)).moved(
        Location(((x0 + x1) / 2, y, z)))


def cyl_y(r, y0, y1, x, z):
    return Cylinder(r, y1 - y0, rotation=(90, 0, 0)).moved(
        Location((x, (y0 + y1) / 2, z)))


def cyl_z(r, z0, z1, x, y):
    return Cylinder(r, z1 - z0).moved(Location((x, y, (z0 + z1) / 2)))


def _vol(a, b):
    ba, bb = a.bounding_box(), b.bounding_box()
    if (ba.max.X < bb.min.X or bb.max.X < ba.min.X or ba.max.Y < bb.min.Y
            or bb.max.Y < ba.min.Y or ba.max.Z < bb.min.Z or bb.max.Z < ba.min.Z):
        return 0.0
    hit = a & b
    return 0.0 if hit is None else abs(hit.volume)


# =============================================================== 1. PACK SLED
# Local frame: origin at the bay centre on the floor top; +X = INBOARD (toward
# the latch boss) for BOTH rear bays -- the rear quarter is rotated 180, so the
# bay's inboard end is global +X. Placement is a pure translation.
CELL_D = 18.6            # 18650 max diameter incl. wrap (INPUT, class value)
CELL_L = 65.2            # 18650 max length (INPUT, class value)
CELL_PITCH = 18.7
CELL_ZC = 2.0 + CELL_D / 2          # 2 mm under the groove bottom -> 11.3
SLED_FLOOR = 6.0
SLED_H = C.PACK_H                   # 24 -- the envelope, BMS included
END_T = 4.25                        # inner length 66.5 for a welded 3S1P
INNER_HALF = C.PACK_L / 2 - END_T   # 33.25
POST_X0 = 28.0                      # catch post thickens inboard ABOVE the cells
POST_HALF_Y = 11.0
POST_TOP = 52.0
POCKET_DEPTH = 3.5                  # into the post from the +X face
POCKET_HALF_Y = 8.5                 # tooth 12 wide at +/-2 either bay -> one sled
POCKET_Z0, POCKET_Z1 = 40.7, 48.5   # local; hold-down face is POCKET_Z0
WEB_HALF, CAP_HALF = 3.0, 8.0
CAP_Z0, CAP_Z1 = 32.0, 40.0         # 45 deg underside 32..37, flat 37..40


def create_sled():
    L2, W2 = C.PACK_L / 2, C.PACK_W / 2
    s = box(-L2, L2, -W2, W2, 0, SLED_FLOOR)
    s += box(-L2, -INNER_HALF, -W2, W2, 0, SLED_H)
    s += box(INNER_HALF, L2, -W2, W2, 0, SLED_H)
    s += box(POST_X0, L2, -POST_HALF_Y, POST_HALF_Y, SLED_H, POST_TOP)
    s += box(-L2, POST_X0, -WEB_HALF, WEB_HALF, SLED_H, CAP_Z0 + 1)
    cap = [(-WEB_HALF, CAP_Z0), (WEB_HALF, CAP_Z0), (CAP_HALF, CAP_Z0 + 5),
           (CAP_HALF, CAP_Z1), (-CAP_HALF, CAP_Z1), (-CAP_HALF, CAP_Z0 + 5)]
    s += yz_prism(cap, -L2, POST_X0)
    for yc in (-CELL_PITCH, 0.0, CELL_PITCH):
        s -= cyl_x(CELL_D / 2 + 0.15, -INNER_HALF, INNER_HALF, yc, CELL_ZC)
    s -= box(L2 - POCKET_DEPTH, L2 + 1, -POCKET_HALF_Y, POCKET_HALF_Y,
             POCKET_Z0, POCKET_Z1)
    for x in (-(L2 - END_T / 2), L2 - END_T / 2):            # BMS carrier, 4 x M2
        for y in (-22.0, 22.0):
            s -= cyl_z(M2_PILOT / 2, SLED_H - 5, SLED_H + 0.1, x, y)
    return s


def sled_placed(sled, by):
    return copy.copy(sled).moved(Location((BAY_XS, by, C.BAY_Z0)))


# ================================================================ 2. LATCH
LEAF_T, LEAF_B = 1.2, 12.0
LEAF_Z0, LEAF_Z1 = BOSS_TOP + 4.0, 52.0          # 22 .. 52 -> L = 30
LEAF_L = LEAF_Z1 - LEAF_Z0
TOOTH_Z0 = 45.0                                   # flat underside = hold-down
TOOTH_TIP_X = BOSS_X0 - (BOSS_X0 - PACK_X_IN) - 2.5   # 2.5 into the sled -> -155
RELEASE_CLEAR = 0.9                               # tooth tip past the sled face
LATCH_BOLT = "M3 x 10 SHCS"


def create_latch(ly):
    """Robot frame, bay at y = ly (sign picks the bay). One part: base + leaf
    + tooth + cam. Returns (whole, moving) -- moving is what the flexure
    carries, used for the release sweep."""
    base = box(BOSS_X0, BOSS_X0 + C.LATCH_BOSS, ly - 8, ly + 8, BOSS_TOP, LEAF_Z0)
    for dy in (-C.LATCH_PILOT_DY, C.LATCH_PILOT_DY):
        base -= cyl_z(M3_CLEAR / 2, BOSS_TOP - 0.1, LEAF_Z0 + 0.1, LATCH_XC, ly + dy)
    y0, y1 = ly - LEAF_B / 2, ly + LEAF_B / 2
    leaf = box(BOSS_X0, BOSS_X0 + LEAF_T, y0, y1, LEAF_Z0, LEAF_Z1)
    tooth = xz_prism([(BOSS_X0, TOOTH_Z0), (TOOTH_TIP_X, TOOTH_Z0),
                      (TOOTH_TIP_X, TOOTH_Z0 + 2), (TOOTH_TIP_X + 5, LEAF_Z1),
                      (BOSS_X0, LEAF_Z1)], y0, y1)
    cam = xz_prism([(BOSS_X0, LEAF_Z1), (BOSS_X0 + 7, LEAF_Z1),
                    (BOSS_X0 + 7, LEAF_Z1 + 7)], y0, y1)
    moving = leaf + tooth + cam
    return base + moving, moving


def release_angle():
    """Rigid-rotation stand-in for the bent leaf: the angle that moves the
    tooth's lowest inner corner RELEASE_CLEAR past the sled face."""
    need = (PACK_X_IN - TOOTH_TIP_X) + RELEASE_CLEAR
    h = TOOTH_Z0 - LEAF_Z0
    return math.degrees(math.asin(need / h)), need, h


def leaf_axis():
    return Axis((BOSS_X0 + LEAF_T / 2, 0, LEAF_Z0), (0, 1, 0))


def leaf_strain(tooth_disp):
    """Cantilever, tip load at L; deflection at the tooth height a is
    y(a) = y(L) * a^2 (3L - a) / (2 L^3). Returns (tip deflection, strain,
    stress, release force)."""
    a, L = TOOTH_Z0 - LEAF_Z0, LEAF_L
    tip = tooth_disp / (a * a * (3 * L - a) / (2 * L ** 3))
    eps = 3 * LEAF_T * tip / (2 * L * L)
    I = LEAF_B * LEAF_T ** 3 / 12
    return tip, eps, eps * E_PETG, 3 * E_PETG * I * tip / L ** 3


# ================================================== 3. ROBOT-SIDE CONTACT PROBE
PROBE_FLANGE = (REAR_FACE_X - 6.0, REAR_FACE_X)      # x -256..-250
PROBE_HALF_Y, PROBE_Z = 14.0, (20.0, 48.0)
NOSE_X = -345.0                                      # nose tip, seated
NOSE_L, NOSE_HALF_Y, NOSE_Z = 8.0, 6.0, (28.0, 40.0)
BLADE_T, BLADE_W, BLADE_L = 0.25, 8.0, 23.0          # phosphor bronze strip
BLADE_ROOT_X = -332.0                                # M2 clamp at x -334
BLADE_FREE_Y = 18.5                                  # tip outer face, free
BLADE_Z = 34.0


def create_probe():
    p = box(*PROBE_FLANGE, -28, 28, 12, 58)
    p += box(NOSE_X + NOSE_L, PROBE_FLANGE[0], -PROBE_HALF_Y, PROBE_HALF_Y, *PROBE_Z)
    p += Solid.make_loft([rect_x(NOSE_X + NOSE_L, -PROBE_HALF_Y, PROBE_HALF_Y, *PROBE_Z),
                          rect_x(NOSE_X, -NOSE_HALF_Y, NOSE_HALF_Y, *NOSE_Z)], ruled=True)
    for y, z in C.CONTACT_PILOT_YZ:
        p -= cyl_x(M3_CLEAR / 2, PROBE_FLANGE[0] - 0.1, REAR_FACE_X + 0.1, y, z)
        p -= cyl_x(3.0, PROBE_FLANGE[0] - 0.1, PROBE_FLANGE[0] + 2.0, y, z)
    for s in (-1, 1):                     # blade clamp, M2 x 6 into a pilot
        p -= cyl_y(M2_PILOT / 2, *sorted((s * (PROBE_HALF_Y - 5), s * (PROBE_HALF_Y + 0.1))),
                   BLADE_ROOT_X - 2.0, BLADE_Z)
    return p


def blades():
    """The two purchased blades, FREE shape (undeflected), for render and
    the preload number -- excluded from interference gates on purpose."""
    phi = math.asin((BLADE_FREE_Y - PROBE_HALF_Y - BLADE_T) / BLADE_L)
    out = []
    for s in (-1, 1):
        b = box(0, BLADE_L, -BLADE_T if s > 0 else 0, 0 if s > 0 else BLADE_T,
                -BLADE_W / 2, BLADE_W / 2)
        b = b.rotate(Axis.Z, s * math.degrees(phi)).moved(
            Location((BLADE_ROOT_X, s * (PROBE_HALF_Y + BLADE_T), BLADE_Z)))
        out.append(b)
    tip_x = BLADE_ROOT_X + BLADE_L * math.cos(phi)
    return out, tip_x, phi


# ============================================================ 4. DOCK (floor)
BACK_X0 = NOSE_X - 8.0                   # backstop x -353..-345
THROAT_X1 = -295.0                       # straight throat -345..-295
MOUTH_X = REAR_FACE_X - 5.0              # -255: 5 mm short of the chassis end
T_HALF, T_Z = PROBE_HALF_Y + 1.0, (PROBE_Z[0] - 1.0, PROBE_Z[1] + 1.0)   # 15, 19..49
M_HALF, M_Z = 54.0, (2.0, 66.0)          # mouth, inner
WALL_T = 4.0
STRIP = dict(x=(-338.0, -296.0), z=(BLADE_Z - 5, BLADE_Z + 5), t=0.5)
COL_XC = -323.0
COL_HALF, COL_WALL, FL_HALF, FL_T, FL_BOLT = 20.0, 4.0, 30.0, 5.0, 25.0
PAD_Z = (5.0, 15.0)
COL_SPLIT_Z = -94.0
TAG_ZC, TAG_SIZE, TAG_PLATE = 152.0, 90.0, 100.0
MAST_X = (BACK_X0 - 4.0, BACK_X0)        # -357..-353
BRICK = (52.0, 92.0)                     # cradle inner, X x Y (brick 50 x 90 class)


def w_inner(x):
    if x <= THROAT_X1:
        return T_HALF
    if x <= MOUTH_X:
        return T_HALF + (x - THROAT_X1) / (MOUTH_X - THROAT_X1) * (M_HALF - T_HALF)
    return float("inf")


def create_funnel():
    k = (MOUTH_X - THROAT_X1)
    o_lo, o_hi = T_Z[0] - WALL_T, T_Z[1] + WALL_T
    outer = box(BACK_X0, THROAT_X1, -T_HALF - WALL_T, T_HALF + WALL_T, o_lo, o_hi)
    outer += Solid.make_loft([
        rect_x(THROAT_X1, -T_HALF - WALL_T, T_HALF + WALL_T, o_lo, o_hi),
        rect_x(MOUTH_X, -M_HALF - WALL_T, M_HALF + WALL_T, M_Z[0] - WALL_T,
               M_Z[1] + WALL_T)], ruled=True)
    outer += box(BACK_X0, BACK_X0 + 2 * FL_HALF, -FL_HALF, FL_HALF, PAD_Z[0], o_lo)
    # square collar at the mouth: without it the sloped walls end in a knife
    # edge (partcheck found 163 samples < 0.8 mm, all on the x = -255 rim)
    outer += box(MOUTH_X - 3.0, MOUTH_X, -M_HALF - WALL_T, M_HALF + WALL_T,
                 M_Z[0] - WALL_T, M_Z[1] + WALL_T)
    ext = 1.0 / k
    inner = box(NOSE_X, THROAT_X1, -T_HALF, T_HALF, *T_Z)
    inner += Solid.make_loft([
        rect_x(THROAT_X1, -T_HALF, T_HALF, *T_Z),
        rect_x(MOUTH_X + 1.0, -(M_HALF + (M_HALF - T_HALF) * ext),
               M_HALF + (M_HALF - T_HALF) * ext,
               M_Z[0] - (T_Z[0] - M_Z[0]) * ext, M_Z[1] + (M_Z[1] - T_Z[1]) * ext)],
        ruled=True)
    f = outer - inner
    for s in (-1, 1):                    # contact-strip recess + 2 x M3 through
        f -= box(*STRIP["x"], *sorted((s * T_HALF, s * (T_HALF + STRIP["t"]))), *STRIP["z"])
        for x in (STRIP["x"][0] + 6, STRIP["x"][1] - 6):
            f -= cyl_y(M3_CLEAR / 2, *sorted((s * (T_HALF - 0.1), s * (T_HALF + WALL_T + 0.1))),
                       x, BLADE_Z)
    for sx in (-1, 1):                   # column bolts, M4 pilots from below
        for sy in (-1, 1):
            f -= cyl_z(M4_PILOT / 2, PAD_Z[0] - 0.1, PAD_Z[0] + 8, COL_XC + sx * FL_BOLT,
                       sy * FL_BOLT)
    for y in (-9.0, 9.0):                # tag mast, M3 pilots into the backstop
        f -= cyl_x(M3_PILOT / 2, BACK_X0 - 0.1, BACK_X0 + 7, y, 37.0)
    return f


def strips():
    return [box(*STRIP["x"], *sorted((s * T_HALF, s * (T_HALF + STRIP["t"]))), *STRIP["z"])
            for s in (-1, 1)]


def _flange(z0):
    f = box(COL_XC - FL_HALF, COL_XC + FL_HALF, -FL_HALF, FL_HALF, z0, z0 + FL_T)
    for sx in (-1, 1):
        for sy in (-1, 1):
            f -= cyl_z(M4_CLEAR / 2, z0 - 0.1, z0 + FL_T + 0.1, COL_XC + sx * FL_BOLT,
                       sy * FL_BOLT)
    return f


def create_column(z0, z1):
    c = _flange(z0) + _flange(z1 - FL_T)
    c += box(COL_XC - COL_HALF, COL_XC + COL_HALF, -COL_HALF, COL_HALF, z0 + FL_T, z1 - FL_T)
    # 45 deg skirt under the TOP flange so it prints without a 10 mm bridge
    zc = z1 - FL_T
    c += Solid.make_loft([
        Wire.make_polygon([Vector(COL_XC + sx * COL_HALF, sy * COL_HALF, zc - (FL_HALF - COL_HALF))
                           for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], close=True),
        Wire.make_polygon([Vector(COL_XC + sx * FL_HALF, sy * FL_HALF, zc)
                           for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], close=True)],
        ruled=True)
    h = COL_HALF - COL_WALL
    c -= box(COL_XC - h, COL_XC + h, -h, h, z0 - 0.1, z1 + 0.1)   # cable bore
    return c


def create_base(gz):
    b = box(-420.0, -245.0, -80.0, 80.0, gz, gz + 5.0)
    cx0 = -420.0
    b += box(cx0, cx0 + BRICK[0] + 6, -BRICK[1] / 2 - 3, BRICK[1] / 2 + 3, gz + 5, gz + 23)
    b -= box(cx0 + 3, cx0 + 3 + BRICK[0], -BRICK[1] / 2, BRICK[1] / 2, gz + 5, gz + 24)
    b -= box(cx0 + 3 + 10, cx0 + 3 + 40, -BRICK[1] / 2 - 4, BRICK[1] / 2 + 4,
             gz + 8, gz + 14)                                  # strap slots
    h = COL_HALF - COL_WALL
    b -= box(COL_XC - h, COL_XC + h, -h, h, gz - 0.1, gz + 5.1)
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = COL_XC + sx * FL_BOLT, sy * FL_BOLT
            b -= cyl_z(M4_CLEAR / 2, gz - 0.1, gz + 5.1, x, y)
            b -= cyl_z(4.1, gz - 0.1, gz + 3.2, x, y)          # nut recess, below
    for x, y in ((-265.0, 70.0), (-265.0, -70.0), (-350.0, 70.0), (-350.0, -70.0)):
        b -= cyl_z(2.3, gz - 0.1, gz + 5.1, x, y)              # floor screws
    return b


def create_tag_mast():
    x0, x1 = MAST_X
    m = box(x0, x1, -15, 15, 24.0, TAG_ZC - TAG_PLATE / 2 + 2)
    m += box(x0, x1, -TAG_PLATE / 2, TAG_PLATE / 2, TAG_ZC - TAG_PLATE / 2,
             TAG_ZC + TAG_PLATE / 2)
    m += box(x0 - 4, x0, -3, 3, 24.0, TAG_ZC - TAG_PLATE / 2)
    for y in (-9.0, 9.0):
        m -= cyl_x(M3_CLEAR / 2, x0 - 0.1, x1 + 0.1, y, 37.0)
    return m


# ------------------------------------------------------------ print poses
def to_bed(s):
    b = s.bounding_box()
    return s.moved(Location((-(b.min.X + b.max.X) / 2, -(b.min.Y + b.max.Y) / 2, -b.min.Z)))


def _legs():
    """Rear legs at WALK stance, from assembly_centaur's own placer."""
    import assembly as A
    import assembly_centaur as AC
    alpha, _, _ = A.solve_leg(STANCE_Z)
    parts = {n: import_step(str(AC.OUT / f"{n}.step")).solids()[0]
             for n in ("thigh_shell", "calf", "foot_core", "foot_tread")
             if (AC.OUT / f"{n}.step").exists()}
    legs, feet = [], []
    for sy in (1, -1):
        bits, foot = AC.leg_at(AC.X_REAR, sy, alpha, parts)
        legs += list(bits.values())
        feet.append(foot)
    return legs, feet[0][2], sorted(parts)


PREREQ_STEPS = (
    ("output/rail_way_inner.step", "waist_rail.py"),
    ("output/rail_way_outer.step", "waist_rail.py"),
    ("output/thigh_shell.step", "thigh.py"),
    ("output/calf.step", "calf.py"),
    ("output/foot_core.step", "foot.py"),
    ("output/foot_tread.step", "foot.py"),
)


def _require_prereqs():
    """dock.py is the ONE part module that is not independent.

    It draws the docked-robot evidence view, so it consumes other modules'
    STEPs. Without this check the failures are a bare FileNotFoundError on a
    rail way and, past that, a KeyError on 'thigh_shell' -- neither of which
    names the module to run. BUILD.md stage 1 orders them correctly.
    """
    missing = sorted({mod for rel, mod in PREREQ_STEPS
                      if not (HERE / rel).exists()})
    if missing:
        raise SystemExit(
            "dock.py needs other part modules' STEPs and they are not in "
            "output/.\n  run first: "
            + "  ".join(missing)
            + "\n  (see BUILD.md stage 1 -- dock.py runs last)")


if __name__ == "__main__":
    from partcheck import check
    _require_prereqs()
    OUT.mkdir(parents=True, exist_ok=True)
    fails = []

    def gate(ok, msg):
        print(("  PASS  " if ok else "  FAIL  ") + msg)
        if not ok:
            fails.append(msg)

    # --------------------------------------------------------------- robot
    q = C.quarters_placed(C.create_quarter_inner(), C.create_quarter_outer())
    rear_q = [q["rear_outer"], q["rear_inner"]]
    run = R.way_run(import_step(str(HERE / "output/rail_way_inner.step")),
                    import_step(str(HERE / "output/rail_way_outer.step")))
    rear_ways = [w for w in run if w.bounding_box().max.X <= 1e-6]
    wh = min(min(abs(w.bounding_box().min.Y), abs(w.bounding_box().max.Y)) for w in rear_ways)
    legs, gz, leg_parts = _legs()
    print(f"rear legs at WALK stance from {leg_parts}; ground z = {gz:.1f} "
          f"(ride height {-gz:.1f} mm under the chassis floor)")

    # ------------------------------------------------------------- 1. SLED
    print("\n== 1. PACK SLED")
    sled = create_sled()
    sb = sled.bounding_box()
    print(f"sled {sb.size.X:.1f} x {sb.size.Y:.1f} x {sb.size.Z:.1f} (envelope "
          f"{C.PACK_L:.0f} x {C.PACK_W:.0f} x {C.PACK_H:.0f} below z {C.PACK_H:.0f}; "
          f"handle + catch post above it)")
    gate(abs(sb.size.X - C.PACK_L) < 1e-6 and abs(sb.size.Y - C.PACK_W) < 1e-6,
         "sled footprint == pack envelope 75 x 58 (bay fit 1.0/side from chassis)")
    sleds = [sled_placed(sled, by) for by in C.BAY_Y]
    v = max(_vol(s, qq) for s in sleds for qq in rear_q)
    gate(v < 1e-6, f"sled seated vs rear quarters: {v:.2e} mm3")
    sweeps = []
    for s in sleds:
        b = s.bounding_box()
        sweeps.append(box(b.min.X, b.max.X, b.min.Y, b.max.Y, b.min.Z, b.max.Z + C.PACK_LIFT))
    v = max(_vol(sw, qq) for sw in sweeps for qq in rear_q)
    gate(v < 1e-6, f"sled lift sweep (+{C.PACK_LIFT:.0f}, to z {sweeps[0].bounding_box().max.Z:.0f}) "
                   f"vs rear quarters: {v:.2e} mm3")
    v = max(_vol(sw, w) for sw in sweeps for w in rear_ways)
    edge = max(abs(s.bounding_box().max.Y) for s in sleds)
    gate(v < 1e-6, f"sled lift sweep vs rear way segments: {v:.2e} mm3 "
                   f"(sled edge |y| {edge:.1f}, way heads |y| {wh:.1f} -> {wh - edge:.1f} mm)")
    # cell fit
    gate(2 * INNER_HALF >= CELL_L + 2 * 0.15 + 0.5,
         f"cell bay length {2 * INNER_HALF:.2f} >= 65.2 cell + 2 x 0.15 strip + 0.5")

    # ------------------------------------------------------------ 2. LATCH
    print("\n== 2. LATCH")
    latches = [create_latch(ly) for ly in C.LATCH_Y]
    for (lat, _), ly in zip(latches, C.LATCH_Y):
        for dy in (-C.LATCH_PILOT_DY, C.LATCH_PILOT_DY):
            probe_pt = cyl_z(0.2, BOSS_TOP + 1, BOSS_TOP + 3, LATCH_XC, ly + dy)
            assert _vol(probe_pt, lat) < 1e-9, "latch bolt hole not over the chassis pilot"
    gate(True, f"latch clearance holes coaxial with chassis pilots (x {LATCH_XC}, "
               f"y {C.LATCH_Y} +/- {C.LATCH_PILOT_DY})")
    v = max(_vol(lat, qq) for lat, _ in latches for qq in rear_q)
    gate(v < 1e-6, f"latch vs rear quarters (seated on the boss top): {v:.2e} mm3")
    v = max(_vol(lat, s) for lat, _ in latches for s in sleds)
    gate(v < 1e-6, f"latch ENGAGED vs sled seated: {v:.2e} mm3")
    v = min(_vol(lat, sw) for (lat, _), sw in zip(latches, sweeps))
    gate(v > 1.0, f"latch ENGAGED blocks the lift: tooth inside the lift sweep "
                  f"{v:.1f} mm3 (> 0 is the point)")
    th, need, h = release_angle()
    worst = 0.0
    for i in range(0, 7):
        a = th * i / 6
        for (lat, mv), s in zip(latches, sleds):
            worst = max(worst, _vol(mv.rotate(leaf_axis(), a), s))
    gate(worst < 1e-6, f"release MOTION 0..{th:.2f} deg (7 poses) vs seated sled: {worst:.2e} mm3")
    rel = [(lat - mv) + mv.rotate(leaf_axis(), th) for lat, mv in latches]
    v = max(_vol(r, sw) for r, sw in zip(rel, sweeps))
    gate(v < 1e-6, f"latch RELEASED vs sled lift sweep: {v:.2e} mm3")
    v = max(_vol(r, qq) for r in rel for qq in rear_q)
    gate(v < 1e-6, f"latch RELEASED vs rear quarters: {v:.2e} mm3")
    tip_r, eps_r, sig_r, f_r = leaf_strain(need)
    tip_i, eps_i, sig_i, f_i = leaf_strain(PACK_X_IN - TOOTH_TIP_X)
    print(f"  leaf {LEAF_T} x {LEAF_B} x L {LEAF_L:.0f} PETG, tooth at a = {h:.0f}; "
          f"insertion tooth {PACK_X_IN - TOOTH_TIP_X:.2f} mm -> tip {tip_i:.2f} mm, "
          f"release tooth {need:.2f} mm -> tip {tip_r:.2f} mm")
    gate(sig_r < SIGMA_PETG, f"leaf strain at release {eps_r * 100:.3f}% -> {sig_r:.1f} MPa "
                             f"< {SIGMA_PETG:.0f} (SF {SIGMA_PETG / sig_r:.2f}); force {f_r:.2f} N")
    gate(sig_i < SIGMA_PETG, f"leaf strain at insertion {eps_i * 100:.3f}% -> {sig_i:.1f} MPa "
                             f"(SF {SIGMA_PETG / sig_i:.2f}); force {f_i:.2f} N")
    cam_stroke = need * ((LEAF_Z1 + 2.5 - LEAF_Z0) / h)
    print(f"  pusher: descends on the 45 deg cam at x ~{BOSS_X0 + 2.5:.1f}, stroke ~{cam_stroke:.1f} mm "
          f"(rigid-rotation estimate); engaged leaf carries NO standing load")

    # ------------------------------------------------------------ 3. PROBE
    print("\n== 3. CONTACT PROBE")
    probe = create_probe()
    bl, tip_x, phi = blades()
    v = max(_vol(probe, qq) for qq in rear_q)
    gate(v < 1e-6, f"probe vs rear quarters: {v:.2e} mm3")
    for y, z in C.CONTACT_PILOT_YZ:
        pt = cyl_x(0.2, REAR_FACE_X - 5, REAR_FACE_X - 1, y, z)
        assert _vol(pt, probe) < 1e-9, "probe bolt hole off the contact pilot"
    gate(True, f"probe holes on the chassis contact pilots {C.CONTACT_PILOT_YZ}")
    delta = BLADE_FREE_Y - T_HALF
    I_b = BLADE_W * BLADE_T ** 3 / 12
    sig_b = 3 * E_PB * BLADE_T * delta / (2 * BLADE_L ** 2)
    F_b = 3 * E_PB * I_b * delta / BLADE_L ** 3
    wipe = STRIP["x"][1] - tip_x
    gate(sig_b < 0.8 * SIGMA_PB_YIELD, f"blade {BLADE_T} x {BLADE_W} x L {BLADE_L:.0f} PB, "
         f"preload deflection {delta:.2f} -> {sig_b:.0f} MPa < 0.8 x {SIGMA_PB_YIELD:.0f}; "
         f"contact force {F_b:.2f} N per blade")
    gate(wipe > 5.0, f"wipe on the strip: tip seated at x {tip_x:.1f}, strip starts "
                     f"{STRIP['x'][1]:.0f} -> {wipe:.1f} mm")

    # ------------------------------------------------------------- 4. DOCK
    print("\n== 4. DOCK")
    funnel = create_funnel()
    col_lo = create_column(gz + 5.0, COL_SPLIT_Z)
    col_hi = create_column(COL_SPLIT_Z, PAD_Z[0])
    base = create_base(gz)
    mast = create_tag_mast()
    dock = {"dock_funnel": funnel, "dock_column_lower": col_lo,
            "dock_column_upper": col_hi, "dock_base": base, "dock_tag_mast": mast}
    fb = funnel.bounding_box()
    mouth_in = w_inner(MOUTH_X)
    e_y = mouth_in - NOSE_HALF_Y
    e_z = min(NOSE_Z[0] - M_Z[0], M_Z[1] - NOSE_Z[1])
    print(f"funnel x {fb.min.X:.1f}..{fb.max.X:.1f}; mouth inner +/-{mouth_in:.1f} y, "
          f"z {M_Z[0]:.0f}..{M_Z[1]:.0f}; throat +/-{T_HALF:.0f} y, z {T_Z[0]:.0f}..{T_Z[1]:.0f}")
    print(f"V half-angles: y {math.degrees(math.atan((M_HALF - T_HALF) / (MOUTH_X - THROAT_X1))):.1f} deg, "
          f"z {math.degrees(math.atan((T_Z[0] - M_Z[0]) / (MOUTH_X - THROAT_X1))):.1f} deg (from the approach axis)")
    print(f"GEOMETRIC CAPTURE: y +/-{e_y:.1f} mm, z +/-{e_z:.1f} mm (nose tip +/-{NOSE_HALF_Y:.0f} "
          f"x {NOSE_Z[1] - NOSE_Z[0]:.0f} inside the mouth)")
    parts_all = list(dock.values())
    robot_rigid = rear_q + rear_ways + legs          # probe checked separately
    # docked
    v = max(_vol(r, d) for r in robot_rigid for d in parts_all)
    gate(v < 1e-6, f"DOCKED: rear quarters + ways + legs vs every dock part: {v:.2e} mm3")
    v = max(_vol(probe, d) for d in parts_all)
    gate(v < 1e-6, f"DOCKED: probe body vs dock: {v:.2e} mm3 (nose on the backstop face)")
    v = max(_vol(l, d) for l in legs for d in parts_all)
    gap_leg = min(min(abs(l.bounding_box().min.Y), abs(l.bounding_box().max.Y)) for l in legs) \
        - (M_HALF + WALL_T)
    gate(v < 1e-6, f"DOCKED: legs vs dock {v:.2e} mm3; leg inner |y| to funnel outer: {gap_leg:.1f} mm")
    # capture sweep: robot enters with offset e, the funnel walks it to centre
    worst, n = 0.0, 0
    for sgn in (1, -1):
        for dx in (90.0, 80.0, 70.0, 60.0, 50.0, 40.0, 30.0, 20.0, 10.0, 0.5):
            xn = NOSE_X + dx
            allow = min(w_inner(xn) - NOSE_HALF_Y, w_inner(xn + NOSE_L) - PROBE_HALF_Y) - 0.3
            dy = sgn * min(e_y - 0.5, max(allow, 0.0))
            loc = Location((dx, dy, 0))
            for r in robot_rigid + [probe]:
                rm = r.moved(loc)
                for d in parts_all:
                    worst = max(worst, _vol(rm, d))
            n += 1
    gate(worst < 1e-6, f"CAPTURE SWEEP: {n} poses, entry offset +/-{e_y - 0.5:.1f} walked to 0 "
                       f"through the V; robot (quarters, ways, legs, probe) vs dock: {worst:.2e} mm3")
    # sightline: phone ASSUMED at the waist-box rim, WALK torso station
    import assembly_centaur as AC
    ph = (AC.TORSO_WALK, R.CAR_Z0 + R.CAR_T + 60.0)
    zt = TAG_ZC - TAG_SIZE / 2
    z_at_end = ph[1] + (zt - ph[1]) * (ph[0] - REAR_FACE_X) / (ph[0] - MAST_X[1])
    gate(z_at_end > R.CAR_Z0, f"tag sightline (phone ASSUMED at x {ph[0]:.0f}, z {ph[1]:.0f}): "
         f"ray to tag bottom edge passes x {REAR_FACE_X:.0f} at z {z_at_end:.1f} > deck {R.CAR_Z0:.0f}")
    dist = ph[0] - MAST_X[1]
    print(f"  tag centre z {TAG_ZC:.0f} (chassis frame) = {TAG_ZC - gz:.0f} mm above ground; "
          f"docked phone-to-tag {dist:.0f} mm; 1 m approach -> ~{dist + 1000:.0f} mm")

    # ------------------------------------------------ exports + partcheck
    print("\n== PRINTED PARTS (print pose, A1 mini)")
    printed = {
        "pack_sled": (sled, sled, 2),
        "pack_latch": (latches[1][0], to_bed(latches[1][0].rotate(Axis.X, 90)), 2),
        "contact_probe": (probe, to_bed(probe.rotate(Axis.Y, 90)), 1),
        "dock_funnel": (funnel, to_bed(funnel.rotate(Axis.Y, -90)), 1),
        "dock_column_lower": (col_lo, to_bed(col_lo), 1),
        "dock_column_upper": (col_hi, to_bed(col_hi), 1),
        "dock_base": (base, to_bed(base), 1),
        "dock_tag_mast": (mast, to_bed(mast.rotate(Axis.Y, 90)), 1),
    }
    report = {}
    for nm, (auth, pp, qty) in printed.items():
        export_step(auth, str(OUT / f"{nm}.step"))
        export_stl(pp, str(OUT / f"{nm}.stl"))
        r = check(pp, nm, out_dir=str(OUT), material="PETG")
        report[nm] = (r, qty)
        bb = sorted(r["size_mm"])
        gate(r["solids"] == 1 and r["watertight"] and r["fits_bed"],
             f"{nm}: 1 solid, watertight, fits {BED_X:.0f}^3 on MEASURED bbox "
             f"{r['size_mm'][0]:.1f} x {r['size_mm'][1]:.1f} x {r['size_mm'][2]:.1f}")
    print("\nPART TABLE")
    for nm, (r, qty) in report.items():
        s = r["size_mm"]
        print(f"  {nm:18s} x{qty}  {s[0]:6.1f} x {s[1]:6.1f} x {s[2]:6.1f}  "
              f"{r['mass_g']:6.1f} g  support {100 * r['support_frac']:4.1f}%  "
              f"min wall {r.get('thickness_min_mm', float('nan')):.2f}"
              f"{'  thin-cluster ' + str(r['thin_extent_mm']) if 'thin_extent_mm' in r else ''}")

    # ------------------------------------------------------------ evidence
    ev = OUT
    export_step(Compound(children=[copy.copy(q["rear_outer"])] + sleds + [l for l, _ in latches]),
                str(ev / "ev_sled_in_bay.step"))
    clip = box(-172, -130, 12, 56, 0, 70)
    for tag, lat in (("engaged", latches[1][0]), ("released", rel[1])):
        export_step(Compound(children=[q["rear_outer"] & clip, sleds[1] & clip, lat]),
                    str(ev / f"ev_latch_{tag}.step"))
    export_step(Compound(children=rear_q + rear_ways + legs + [probe] + bl + strips()
                         + parts_all), str(ev / "ev_robot_docked.step"))
    xo, lay = 0.0, []
    for nm in dock:
        pp = printed[nm][1]
        b = pp.bounding_box()
        lay.append(pp.moved(Location((xo - b.min.X, 0, 0))))
        xo += b.size.X + 25
    export_step(Compound(children=lay), str(ev / "ev_dock_parts_print.step"))

    print(f"\n{len(fails)} gate(s) failed" if fails else "\nALL GATES PASS")
    sys.exit(1 if fails else 0)
