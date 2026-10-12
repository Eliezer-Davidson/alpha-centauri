"""Alpha Centauri — quad chassis, FOUR printed quarters (build123d).

TWO PARTS, EACH PRINTED TWICE. Since 2026-09-22 (edu/REPLAN-2026-08-28.md
queue item 2) the 500 mm body is four 125 mm segments split on the planes
CHASSIS_SPLICE_X = (-125, 0, +125):

    INNER quarter   global x 0..125    the midline splice, the +/-40/80/120
                                       ledge pilots, the floor lightening hole
    OUTER quarter   global x 125..250  the 160 mm body: the pod SOCKETS and
                                       insert lands, the +/-160/200 ledge
                                       pilots, the hip-end wall, the two battery
                                       bays, the dock contact station
    ABDUCTION POD   bolt-on, x 180..250 the servo pocket, HIP_POD_FACE_Y recess,
    (x4, one STL)                      boss-side tongue, gussets, flange
                                       (since 2026-09-23 -- see BOLT-ON POD)

The rear pair is the SAME two objects rotated 180 deg about Z -- the placement
convention the H2C-era halves used and that waist_rail.way_run() now asserts
against (rear way segments rotated, every ledge bolt on the +/-40..+/-200 grid).
That is why everything on both parts is mirrored in Y and identical at both
ends of every splice face, and why nothing fore-aft-asymmetric is printed in:
anything that has to differ front from rear (populated battery bays, the dock
contacts, a torso mount) BOLTS ON. The front outer quarter therefore carries
two empty battery bays and an unpopulated contact face. That is the law, not a
waste: the front bays are a mounting station for the phone or the power board
later, or they stay empty.

Why four and not two (the H2C-era text is below, kept because it explains the
decisions made against it):
  * the ONLY printer is a Bambu A1 mini, 180 x 180 x 180. A 250 x 160 half fits
    it in no orientation (partcheck: "FAIL fits the A1 mini bed"). 125 x 160 x
    72 fits flat, floor down, which is the print pose the part is authored in;
  * a failed print costs one quarter (~200-300 g), not a half;
  * still only TWO geometries to verify.

H2C-ERA TEXT (2026-08, two 250 mm halves), superseded but not deleted:
  ONE PART, PRINTED TWICE. The front and rear halves are the same object; the
  second is rotated 180 deg about Z. That is why the split-face bolt pattern is
  mirrored in Y and why nothing fore-aft-asymmetric is modelled into the shell.
  Three reasons this beats one 500 mm monolith: it fits the H2C bed (250 x 160)
  with room to spare [RETRACTED 2026-08-28: the H2C is gone]; a failed print
  costs one half; one geometry to verify.

Frame: X = fore-aft, Y = lateral, Z = up from the chassis floor. Both parts
are authored IN THE ROBOT FRAME of the front copy (inner 0..125, outer
125..250) so that placement is identity for the front pair and
rotate(Axis.Z, 180) for the rear pair -- nothing else. The hip abduction axis
sits at (LEG_FB, +/-LEG_LR, CHASSIS_HEIGHT/2), pointing along X.

THE SPLICE JOINT (all three planes, one design)
-----------------------------------------------
Bolted splice with loose shear keys; the keys carry shear and register Y and
Z, the bolts only clamp. Two POSTS per splice face -- the side wall thickened
inboard to 14 mm (WALL + POST_T) for POST_L along the joint, floor to ledge --
carry everything. Per plane: 4 x M4 x 30 along X (two per post, z = 20 and
52), heads and nuts in identical slots that open into the cavity 12 mm from
the joint face (the carriage-joint pattern from waist_rail.py: one slot shape
takes either a 7.0 socket head or a 7.0 A/F nut, so both mating faces are the
SAME feature and no hermaphroditic layout is needed), hex key down the bolt's
own 4.4 mm bore; plus 2 loose keys, 5.7 x 11.7 x 11.6, in 6 x 12 x 6-deep
pockets in both faces.

WHY NOT THE OLD FULL-WIDTH BULKHEAD. The H2C-era midline bulkhead (5 mm, full
width, four M4 at y = +/-55) was measured against rail_rack.step placed at
assembly_centaur.RAIL_MID and INTERSECTS IT BY 1.887 cm3 -- the rack's foot
starts at global x = 2 and runs 200 mm through the well, straight across the
x = 0 AND x = 125 planes. A full bulkhead at +/-125 would cut the rack in two
places more. The posts leave |y| < 66 completely open at every splice, so the
rack channel (y -21..13, z 4..64) is free, and the build asserts rack-vs-
quarters = 0 (it was 1.887 before). The same open band matters for the CHEST
VERTICALS (y = +/-60, 8 mm rod, extension_stowage.py option B lowers them into
the well): the posts start at |y| = 66, 2 mm outboard of the rod band 56..64.
The old bulkhead's y = +/-55 bolts sat inside that band.

WHY LOOSE KEYS, NOT TABS. At x = 0 an inner quarter mates ITS OWN rotated
copy, so a male tab would meet a male tab. Loose keys in identical pockets
are rotation-proof (waist_rail.py reached the same conclusion for the ways),
and a pocket in a vertical end face prints unsupported while a horizontal tab
sticking out of it does not.

THE BATTERY BAYS (queue item 3, with the 2026-09-22 correction)
---------------------------------------------------------------
Two 3S 18650 packs, BOTH AFT, side by side in Y, holder centres at global
(x -190, y +/-31.5), on the rear outer quarter. Not one fore and one aft:
balance.py's counterweight is 600 g at X_BATTERY = -190, and splitting it
+/-190 would remove 300 g x 380 mm of aft moment (~+26 mm of whole-robot CoM
on ~4.4 kg) and erase the WALK crawl margin. Two 300 g packs at -190 keep
balance.py numerically true. REPLAN section 3's stability check assumed
exactly this ("removing one 300 g pack at x = -190").

Each bay is a tray pocket in the floor: locating ribs 8 mm tall around a
77 x 60 footprint (DECISION: holder envelope 75 x 58 x 24 -- a 3-slot 18650
holder is ~58 x 77 x 20 (3 x 18 mm cells side by side plus walls) with a 3S
BMS strapped on top, +1.0 mm running fit per side; the 24 includes the BMS).
The pack sits on the floor top (z = 4) and lifts STRAIGHT UP: the well is
open above it, the ledges start at |y| = 65 and the dovetail way heads at
|y| = 63, so the pack's outer edge (|y| = 60.5) has 2.5 mm to the way head and
4.5 mm to the ledge on the way out. Honest consequence: that is the swap
dock's capture budget on Y unless the pack goes to a narrower 2+1 (triangle)
cell layout, which is queue item 7's call. Robot-side latch: passive sprung,
roughed in as a MOUNTING INTERFACE ONLY -- a 16 x 16 x 14 boss per bay at the
bay's inboard end (x 132.5..148.5, y +/-33.5) with two M3 pilots on top. The extraction sweep (pack box
lifted 90 mm) is asserted against all four quarters and the rear way
segments.

TRIM RAILS RETIRED (RAIL_X0/RAIL_X1/RAIL_Y, BATTERY_RAIL_PITCH). The rails
existed so the battery could be moved to trim the standing CoM empirically.
Two packs at a FIXED station replace them, for two reasons: the swap dock
needs the pack where it always is, and the trim function has moved to the
torso rail (assembly_centaur.py: TORSO_WALK -> TORSO_WORK slides the CoM
0 -> +46 mm, continuously, under servo control -- a far larger and finer trim
than 15 mm bolt steps). BATTERY_RAIL_PITCH / BATTERY_RAIL_TRAVEL in
interface_constants are now consumed by nothing in CAD (sim/mjcf_export.py
still reads BATTERY_RAIL_TRAVEL); they are left for a later cleanup.

DOCK CONTACT STATION (queue item 7 draws the dock; this is only the robot-side
mounting interface). The hip-end wall's OUTER face at global x = -250 (rear
copy), |y| <= 30, z 10..60, backed on the inside by a 5 mm pad; four M3
pilots from the outside at (y +/-20, z 22) and (y +/-20, z 46). The front
copy carries the same face unpopulated (the law above).

RETRACTIONS, measured on the H2C-era half before this rework:
  * "leave floor, both side walls, and the far end wall. The split face (X=0)
    stays open" -- the CODE did the opposite: the hollowing box ran from x =
    WALL to x = 250, so the hip end was OPEN and the split face was closed by
    a 3 mm wall plus the bulkhead. Probed: material at (248.5, 0, 36) False,
    at (1.5, 0, 36) True. The buttressing story's "reason 3, the far end wall
    the pod abuts for free" therefore never existed. The outer quarter now
    HAS that wall (it is the contact-station face), so reason 3 is true for
    the first time.
  * the pod "cable pass-through into the body cavity" (r 5 bore at y = +/-90)
    exits the pod's inboard end into open air OUTBOARD of the side wall
    (|y| 85..95 vs the wall at 77..80); it never reaches the cavity. Left as
    drawn -- pod geometry is untouched by instruction -- flagged for the pod
    rework.

THE BOLT-ON POD (2026-09-23, design-log section 4 decision 7, the author's call)
----------------------------------------------------------------------
The pods made the outer quarter 125 x 208.3 x 72 -- no A1 mini orientation.
They are now a separate part, abduction_pod, and the outer quarter is the
160 mm body (125 x 160 x 72, fits flat). Both are CARVED from the legacy
fused solid (create_quarter_outer_fused, kept as the reference), so the
pocket, the HIP_POD_FACE_Y recess, the gussets and the hip station are the
same solids at the same place -- gate 6 proves it (0 mm3 of legacy pod
material lost, voids still empty, envelope corner delta 0).

  SOCKET (body side, THE interface -- fixed by SOCK_* only): a window
    through wall + boss, x 198..250, y 70..80, z 11..61 (symmetric about
    HIP_Z), with the end wall kept as a post at y 70..76, x 247..250.
  TONGUE (pod side): the legacy material inside the socket, shrunk
    TONGUE_FIT = 0.15 per bearing face. It bears on the sill/header (Z both
    ways, and the Mx couple), the x = 198 face (-X) and the x = 247 shoulder
    (+X). The servo pocket lives INSIDE the tongue, so the body carries no
    servo geometry and is no longer caliper-blocked; only the pod is.
  FLANGE: 4 mm on the wall face, x 180..250, z 0..72; six M3 x 10 socket
    heads into M3 x 5.7 brass heat-set inserts in the body (inboard land
    x 189 z 24/48; sill x 215/240 z 6; header x 215/240 z 66). Inserts, not
    printed pilots: the pod is the part that gets unbolted (servo service,
    decisions 3 and 4 redraws) and self-tapped PETG-CF threads wear; M3,
    not M4: the sill and header are 7 mm, and an M4 insert bore (~5.6)
    would leave ~1 mm webs. The bolts CLAMP; the tongue carries the load.
  LOAD PATH (printed by the build, all computed): one leg at half the
    robot's weight + the 2.4516 N.m measured stall gives Mx = 2.67 N.m at
    the joint plane; as a tongue couple across the 10 mm socket depth that
    is ~800 N, 3.3 MPa peak bearing on 48.7 x 10 mm faces; with the tongue
    ignored the worst M3 sees ~15 N tension.
  ONE STL, FOUR STATIONS: the pod is symmetric about z = HIP_Z (bolt
    pattern included), so the -Y pod is the +Y pod turned 180 deg about the
    X line through z = HIP_Z (POD_FLIP_AXIS), gated equal to the mirror.
    pods_placed(): front_left identity, front_right flip, rear pair = the
    front pair rotated 180 deg about Z -- the quarters' own law.
  HEADROOM for decisions 3/4 (pod redraw, body untouched): pocket may grow
    to z 12.35..59.65 (a 47.3 mm pocket; decision 3's servo-on-end pocket
    is 45.62 tall, POD_H 51.6 -> 2.0 mm tongue walls), start at x >= 199.35,
    reach inboard to y >= 77.35 (walls at HIP_POD_WALL_MIN 1.2); the pod
    OUTBOARD of the flange is unconstrained by the body except the six bolt
    heads (x 186.25..191.75 at z 21..51; z 3.25..8.75 and 63.25..68.75 at
    x 215/240) -- so a +7 mm 608 end-wall station can grow outboard of
    x = 250 or inboard to x ~192 without a body change.
  PRINT POSE: hip face (x = 250) down -- every wall vertical, the pocket a
    shaft open at the bed. The support partcheck reports is the gussets'
    bed-facing faces and the tongue shoulder step.

Every shared dimension comes from interface_constants. Nothing is re-derived
here -- that is the whole point of the interface block (the design log, D11).

PRINT-BLOCKED (LAW: unresolved servo height): the abduction servo pocket
(POCKET_H) derives from SERVO_BODY_HEIGHT, which is UNRESOLVED (35.00 nominal
vs 37.80 vendor STEP). The outer quarter is drawn parametrically and
gate-checked at BOTH candidate heights via interface_constants._check(); it
must not be printed until the caliper resolves the height. Since the pod
split that is the abduction_pod ONLY: the inner quarter and the outer body
carry no servo geometry (gate 6d) and are not blocked by this. The same block applies
to the thigh and the hip module.

TRANSITIONAL EXPORT: chassis_half.step/.stl is still written -- the inner
quarter, the outer body and the two front pods, bolted and FUSED into the old
0..250 half (the pod flanges add 11.2 cm3 per side over the pre-split half) --
so assembly*.py, marks.py,
hip_module.py, extension_stowage.py and sim/mjcf_export.py keep working until
they migrate to the quarters. It is a reference solid, not a printed part
(it does not fit the bed), so it gets no partcheck and no 3MF.

    edu/.cadenv/bin/python cad/alpha_centauri/chassis.py
"""

import copy
from pathlib import Path
import sys

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
    Plane,
    Solid,
    Vector,
    Wire,
    add,
    export_step,
    export_stl,
    import_step,
)

from interface_constants import (
    CHASSIS_HEIGHT,
    CHASSIS_LENGTH,
    CHASSIS_SEGMENT_LENGTH,
    CHASSIS_SPLICE_X,
    CHASSIS_WIDTH,
    HIP_POD_FACE_Y,
    HIP_POD_WALL_MIN,
    HIP_STACK,
    LEG_FB,
    LEG_LR,
    SERVO_BODY_HEIGHT,
    SERVO_BODY_LENGTH,
    SERVO_BODY_WIDTH,
    SERVO_POCKET_CLEARANCE,
    WALL,
)

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "edu/tools"))

# ------------------------------------------------------------------ fasteners
M4_CLEAR = 4.4          # through-hole for an M4 machine screw
M4_PILOT = 3.6          # self-tap into printed wall
M3_CLEAR = 3.4
M3_PILOT = 2.6

# ------------------------------------------------------------------ the shell
SEG_L = CHASSIS_SEGMENT_LENGTH        # 125; CHASSIS_HALF_LENGTH is no longer
                                      # imported anywhere -- the alias can die
INNER_X0, INNER_X1 = 0.0, SEG_L                 # 0..125
OUTER_X0, OUTER_X1 = SEG_L, 2 * SEG_L           # 125..250
assert OUTER_X1 == LEG_FB == CHASSIS_LENGTH / 2
W = CHASSIS_WIDTH                     # 160
H = CHASSIS_HEIGHT                    # 72
FLOOR_T = 4.0                         # floor is thicker than the walls: it
                                      # carries the battery bays

# Top ledge: an inward lip along each side wall that the torso, the electronics
# deck and any cover bolt down to. The 3 mm wall top is too narrow to take a
# hole, so the ledge is what makes the open-top box mountable.
LEDGE_W = 12.0
LEDGE_T = 4.0
LEDGE_Y = W / 2 - WALL - LEDGE_W / 2  # 71.0 -- waist_rail.LEDGE_Y restates it

# THE LEDGE PILOT GRID, global x, per half: 40, 80, 120, 160, 200 (and their
# negatives on the rotated rear pair). waist_rail.way_run() asserts every way
# bolt lands on exactly this set, so it is stated ONCE here and each quarter
# takes the stations that fall inside its span. The 40 mm pitch does not
# divide 125, which is why the inner gets three pilots and the outer two.
LEDGE_PILOT_PITCH = 40.0
LEDGE_PILOT_X = tuple(float(x) for x in range(40, int(2 * SEG_L) - 20, 40))
assert LEDGE_PILOT_X == (40.0, 80.0, 120.0, 160.0, 200.0)

# --------------------------------------------------------------- splice posts
# H2C-era BULK_T = 5.0, BULK_HOLE_Y = (-55, 55), BULK_HOLE_Z = (18, 52):
# RETIRED (see module docstring -- it cut the rail rack and sat in the chest
# rod band). Replaced by two side-wall posts per face.
POST_T = 11.0                         # inboard of the 3 mm wall: 14 mm section
POST_L = 20.0                         # run along X from the joint face
POST_Y = W / 2 - WALL - POST_T / 2    # 71.5, bolt and key centreline
POST_Y_IN = W / 2 - WALL - POST_T     # 66.0, the post's cavity face
JBOLT_Z = (20.0, 52.0)                # two M4 per post, straddling the key
JBOLT_HEAD_X = 12.0                   # slot starts 12 mm from the joint face
                                      # -> 24 mm grip across the joint, M4 x 30
JSLOT_L = 4.4                         # X: socket head 4.0 / nut 3.2 + fit
JSLOT_W = 7.3                         # Z: nut 7.0 A/F + fit; head 7.0 dia fits
JSLOT_DEPTH_Y = 10.5                  # from the cavity face outward: 66..76.5,
                                      # 0.5 mm of post + the wall behind it
# Loose shear keys, waist_rail.py's convention: pocket = KEY_W x KEY_H, key =
# that minus KEY_FIT, length 0.4 short of the pocket pair.
KEY_W = 6.0                           # Y, of an 11 mm post
KEY_H = 12.0                          # Z
KEY_POCKET_D = 6.0                    # into each face
KEY_FIT = 0.3
KEY_L = 2 * KEY_POCKET_D - 0.4        # 11.6
KEY_Z = 36.0                          # mid-height, between the two bolts

# ------------------------------------------------------------- abduction pods
# The servo lies along X with its output on the hip axis. Its body reaches
# INBOARD from the hip station, so the pod never overhangs the end of the robot.
POD_WALL = 3.0
POCKET_L = SERVO_BODY_LENGTH + SERVO_POCKET_CLEARANCE
POCKET_W = SERVO_BODY_WIDTH + SERVO_POCKET_CLEARANCE
POCKET_H = SERVO_BODY_HEIGHT + SERVO_POCKET_CLEARANCE
POD_L = POCKET_L + POD_WALL           # closed inboard, open at the hip face
POD_H = POCKET_H + 2 * POD_WALL
HIP_Z = H / 2.0                       # abduction axis at mid-height
HORN_BORE = 22.0                      # clearance for the output horn / hip disc

# THE POD IS RECESSED BY HIP_STACK (interface_constants section 7). The hip
# module's fork lug hangs inboard of the thigh cheek and rolls with the leg;
# swept through the abduction working range it comes inside the old outboard
# face's running clearance at the 37.80 vendor servo height. The abduction
# pocket cannot move (its servo is centred on the abduction axis), so the
# recess comes entirely out of the outboard wall: the pod is now ASYMMETRIC
# about the hip station -- full POD_WALL inboard, POD_WALL - HIP_STACK
# outboard. The inboard face, the boss and the gussets all key off the same
# derived extents as before, so the buttressing story survives unchanged.
POD_Y_OUT = HIP_POD_FACE_Y            # outboard face, recessed (was LEG_LR
                                      # + POD_W/2 = HIP_POD_FACE_NOMINAL)
POD_Y_IN = LEG_LR - (POCKET_W / 2 + POD_WALL)   # inboard face, unchanged
POD_W = POD_Y_OUT - POD_Y_IN          # asymmetric width, 31.12 - HIP_STACK
POD_CY = (POD_Y_OUT + POD_Y_IN) / 2.0  # pod centreline, HIP_STACK/2 inboard
                                       # of the abduction axis

# The recess must leave a printable outboard wall over the pocket. This is
# also asserted at import by interface_constants._check(); repeating it here
# ties the failure to the part that would actually be misprinted.
_POD_WALL_OUT = POD_Y_OUT - (LEG_LR + POCKET_W / 2)
assert _POD_WALL_OUT >= HIP_POD_WALL_MIN, (
    f"pod recess leaves {_POD_WALL_OUT:.2f} mm outboard wall, under the "
    f"{HIP_POD_WALL_MIN} printable floor"
)

# Derived pod extents -- everything the buttressing keys off.
POD_Z0 = HIP_Z - POD_H / 2.0
POD_Z1 = HIP_Z + POD_H / 2.0
POD_X0 = LEG_FB - POD_L               # inboard end of the pod

# The pod is a CANTILEVER: it hangs outboard of a 3 mm wall and carries a whole
# leg. Bare, it overlaps that wall by only (POD_Y_OUT - POD_W) ~ 5.6 mm, which is
# the weakest joint in the part. Three things fix it, in order of effect:
#   1. BOSS  -- thicken the wall locally to ~10 mm over the pod's span, on the
#      INSIDE where there is free cavity, so the shear goes into a real section.
#   2. GUSSET -- triangular buttresses above and below the pod tying its outboard
#      corner back to the wall, converting cantilever bending into web shear.
#   3. the end wall at X = LEG_FB, which the pod abuts. (It did not exist on
#      the H2C-era half -- see RETRACTIONS; the outer quarter now has it.)
BOSS_T = 7.0                          # 3 mm wall + 7 = 10 mm through the pod span
BOSS_RUN = 12.0                       # boss overruns the pod aft, easing the step
GUSSET_T = 4.0                        # web thickness, ~1.3x wall so it is stiffer

# ------------------------------------------------ the BOLT-ON pod interface
# (2026-09-23, design-log section 4 decision 7, the author: the pod becomes a separate
# bolt-on part.) Everything here is the INTERFACE -- the body side is fixed
# by these numbers and nothing else, so the pod can be redrawn for decisions
# 3 and 4 without touching the body. See the module docstring, BOLT-ON POD.
SOCK_X0 = 198.0                       # socket inboard end face (bears -X)
SOCK_SHOULDER_X = OUTER_X1 - WALL     # 247: end-wall post face (bears +X)
SOCK_Y_IN = W / 2 - WALL - BOSS_T     # 70: through wall + boss to the cavity
SOCK_Y_OUT = W / 2                    # 80: the wall's outer face, the joint plane
SOCK_SHOULDER_Y = 76.0                # end-wall post is y 70..76; outboard of
                                      # it the socket runs out through x = 250
SOCK_Z0, SOCK_Z1 = 11.0, 61.0         # sill and header faces (bear -Z / +Z);
                                      # symmetric about HIP_Z = 36
TONGUE_FIT = 0.15                     # per bearing face -- KEY_FIT's 0.3 split
FLANGE_T = 4.0                        # on the wall face, y 80..84
FLANGE_X0 = 180.0                     # flange runs x 180..250, z 0..72
BODY_BOSS_X0 = 180.0                  # body boss run forward from 189.38 to
                                      # back the inboard bolt pair
# Six M3 x 10 socket-head screws per pod, heads on the flange, into brass
# heat-set inserts in the body (wall + boss = 10 mm deep). Symmetric about
# z = HIP_Z so the flipped pod lands on the same inserts.
POD_BOLT_XZ = ((189.0, 24.0), (189.0, 48.0),      # inboard land, x 180..198
               (215.0, 6.0), (240.0, 6.0),        # sill, z 4..11 (+ floor)
               (215.0, 66.0), (240.0, 66.0))      # header, z 61..68
INSERT_HOLE_D = 4.0                   # M3 x 5.7 short heat-set insert
INSERT_HOLE_DEPTH = 6.5
M3_TENSILE_AREA = 5.03                # mm2, ISO 898 stress area of M3
assert all(abs(z - (2 * HIP_Z - z2)) < 1e-9 for (x, z), (x2, z2)
           in zip(POD_BOLT_XZ, (POD_BOLT_XZ[1], POD_BOLT_XZ[0], POD_BOLT_XZ[4],
                                POD_BOLT_XZ[5], POD_BOLT_XZ[2], POD_BOLT_XZ[3])))
assert abs((SOCK_Z0 + SOCK_Z1) / 2 - HIP_Z) < 1e-9, "socket not symmetric about HIP_Z"


def _tongue_walls(h):
    """Tongue wall left around the servo pocket at servo height h, per face:
    (sill/header, inboard end, back skin behind the shoulder)."""
    ph = h + SERVO_POCKET_CLEARANCE
    zw = min(HIP_Z - ph / 2 - (SOCK_Z0 + TONGUE_FIT),
             (SOCK_Z1 - TONGUE_FIT) - (HIP_Z + ph / 2))
    xw = (LEG_FB - POCKET_L) - (SOCK_X0 + TONGUE_FIT)
    yw = (LEG_LR - POCKET_W / 2) - (SOCK_SHOULDER_Y + TONGUE_FIT)
    return zw, xw, yw


for _h in (35.0, 37.8):   # = SERVO_BODY_HEIGHT_CANDIDATES; both must print
    _w = _tongue_walls(_h)
    assert min(_w) >= HIP_POD_WALL_MIN, (
        f"socket too tight for the pocket at servo height {_h}: walls {_w}")

# ------------------------------------------------------------- battery bays
# Outer-quarter local x (= robot x of the FRONT copy); the rear copy lands the
# bay centre at global x = -BAY_X by the 180 deg rotation.
PACK_L, PACK_W, PACK_H = 75.0, 58.0, 24.0   # DECISION  3S 18650 holder + BMS
BAY_FIT = 1.0                               # running fit per side, X and Y
BAY_L = PACK_L + 2 * BAY_FIT                # 77
BAY_W = PACK_W + 2 * BAY_FIT                # 60
BAY_X = 190.0                               # DECISION  the aft station;
                                            # balance.X_BATTERY DERIVES from
                                            # this (never the other way)
BAY_Y = (-31.5, 31.5)                       # DECISION  side by side, 3 mm rib
BAY_RIB_T = 3.0
BAY_RIB_H = 8.0                             # above the floor top
BAY_Z0 = FLOOR_T                            # the pack sits on the floor top
LATCH_BOSS = 16.0                           # square, per bay, inboard end
LATCH_BOSS_H = 14.0
LATCH_Y = (-33.5, 33.5)                     # 2 mm outboard of the bay centre:
                                            # clear of the rack channel below
LATCH_PILOT_DY = 5.0                        # two M3, +/- about LATCH_Y
PACK_LIFT = 90.0                            # extraction sweep, past the ways
_TRAY_L = BAY_L + 2 * BAY_RIB_T             # 83
_TRAY_W = 2 * BAY_W + 3 * BAY_RIB_T         # 129 -> ribs out to |y| 64.5
assert _TRAY_W / 2 < LEDGE_Y - LEDGE_W / 2, "bay ribs run under the ledge"
assert BAY_X + _TRAY_L / 2 < OUTER_X1 - WALL, "bay tray hits the end wall"
LATCH_X = BAY_X - _TRAY_L / 2 - LATCH_BOSS / 2      # 140.5, abutting the rib

# THE FRONT COPY'S TRAY MEETS THE RAIL RACK. One part printed twice means the
# tray also stands at global +148..+232, and rail_rack.step at RAIL_MID runs
# x 2..202, y -20.9..13.1, z 4..64 (measured) -- first build of this file
# found 1.595 cm3 of divider rib and inboard end rib inside it. So the rack
# channel is cut out of the tray: no divider rib forward of RACK_X_END, and
# the inboard rib is notched over |y| < RACK_CHANNEL_HALF_W. The divider
# survives as a 26 mm stub at the rear end, which still locates the packs'
# inner edges. Restated rack numbers, guarded by gate 4 (rack vs quarters = 0).
RACK_CHANNEL_HALF_W = 24.0                  # rack y -20.9..13.1, symmetric + 3
RACK_X_END = 205.0                          # rack ends at 202 (front copy)
assert abs(LATCH_Y[1]) - LATCH_BOSS / 2 > RACK_CHANNEL_HALF_W, "latch boss in the rack channel"

# ----------------------------------------------------- dock contact station
PAD_T = 5.0                                 # inside the end wall
PAD_HALF_W = 30.0
PAD_Z0, PAD_Z1 = 4.0, 60.0
CONTACT_PILOT_YZ = tuple((y, z) for z in (22.0, 46.0) for y in (-20.0, 20.0))
CONTACT_PILOT_DEPTH = 8.0                   # through the 3 mm wall into the pad

# The torso rail carriage's bolt access and the bay hardware share the cavity
# with the splice posts; keep them apart in X.
assert LATCH_X - LATCH_BOSS / 2 > OUTER_X0 + POST_L or abs(BAY_Y[0]) + LATCH_BOSS / 2 < POST_Y_IN, (
    "latch boss overlaps a splice post")


def _gusset(x0, sgn, z_wall, z_pod):
    """Triangular web tying the pod's outboard corner back to the side wall.

    Right angle at the wall: one leg runs up (or down) the wall face from z_wall
    to z_pod, the other runs outboard along the pod face, and the hypotenuse
    closes them. That turns the pod's cantilever bending into shear in a web,
    which is the one thing an FDM part is genuinely good at -- the load stays in
    the XY plane of the print, never across the layer lines.

    Built from raw topology rather than BuildSketch/extrude so it carries no
    builder state -- it is a plain solid the caller adds wherever it likes.
    """
    yw = sgn * (W / 2)              # outer face of the side wall
    yo = sgn * POD_Y_OUT            # outboard face of the pod
    tri = Wire.make_polygon(
        [Vector(x0, yw, z_wall), Vector(x0, yw, z_pod), Vector(x0, yo, z_pod)],
        close=True,
    )
    return Solid.extrude(Face(tri), Vector(GUSSET_T, 0, 0))


def _splice_posts_add(x_face, d):
    """Two posts on the joint face at x_face; the part extends toward d*X.
    Call inside a BuildPart, in the ADD phase."""
    for sgn in (-1, 1):
        with Locations((min(x_face, x_face + d * POST_L), sgn * POST_Y, FLOOR_T)):
            Box(POST_L, POST_T, H - LEDGE_T - FLOOR_T,
                align=(Align.MIN, Align.CENTER, Align.MIN))


def _splice_posts_cut(x_face, d):
    """Bolt bores, head/nut slots and key pockets for the posts at x_face.
    Identical on every face of both parts -- that is what makes the rotated
    rear copies mate. Call inside a BuildPart, in the SUBTRACT phase."""
    for sgn in (-1, 1):
        for z in JBOLT_Z:
            # bore the full post length: bolt AND hex-key passage
            with Locations((x_face + d * POST_L / 2, sgn * POST_Y, z)):
                Cylinder(radius=M4_CLEAR / 2, height=POST_L + 2.0,
                         rotation=(0, 90, 0), mode=Mode.SUBTRACT)
            # one slot shape takes a socket head or a nut; open to the cavity
            with Locations((x_face + d * (JBOLT_HEAD_X + JSLOT_L / 2),
                            sgn * (POST_Y_IN + JSLOT_DEPTH_Y / 2), z)):
                Box(JSLOT_L, JSLOT_DEPTH_Y, JSLOT_W, align=Align.CENTER,
                    mode=Mode.SUBTRACT)
        with Locations((x_face + d * KEY_POCKET_D / 2, sgn * POST_Y, KEY_Z)):
            Box(KEY_POCKET_D, KEY_W, KEY_H, align=Align.CENTER,
                mode=Mode.SUBTRACT)


def _ledges(x0, x1):
    """Both top ledges over x0..x1 with the global-grid pilots that fall inside."""
    for sgn in (-1, 1):
        with Locations((x0, sgn * LEDGE_Y, H - LEDGE_T)):
            Box(x1 - x0, LEDGE_W, LEDGE_T,
                align=(Align.MIN, Align.CENTER, Align.MIN))


def _ledge_pilots(x0, x1):
    for sgn in (-1, 1):
        for x in LEDGE_PILOT_X:
            if x0 < x < x1:
                with Locations((x, sgn * LEDGE_Y, H - LEDGE_T)):
                    Cylinder(radius=M4_PILOT / 2, height=LEDGE_T * 2,
                             align=(Align.CENTER, Align.CENTER, Align.MIN),
                             mode=Mode.SUBTRACT)


def quarter_pilots(x0, x1):
    """Global ledge pilot stations inside a quarter's span -- what the gates
    and the report read; the same rule _ledge_pilots() cuts from."""
    return tuple(x for x in LEDGE_PILOT_X if x0 < x < x1)


def create_quarter_inner():
    """Global 0..125: floor, walls, ledges, splice posts at BOTH ends, the
    floor lightening hole. Print pose as authored: floor on the bed."""
    x0, x1 = INNER_X0, INNER_X1
    with BuildPart() as part:
        with Locations((x0, 0, 0)):
            Box(SEG_L, W, H, align=(Align.MIN, Align.CENTER, Align.MIN))
        # hollow: open through BOTH splice faces
        with Locations((x0 - 1.0, 0, FLOOR_T)):
            Box(SEG_L + 2.0, W - 2 * WALL, H - FLOOR_T,
                align=(Align.MIN, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        _ledges(x0, x1)
        _splice_posts_add(x0, +1)
        _splice_posts_add(x1, -1)

        _ledge_pilots(x0, x1)
        _splice_posts_cut(x0, +1)
        _splice_posts_cut(x1, -1)

        # floor lightening, away from the posts and the rack foot's flange
        # stations. Keeps the floor stiff in bending while removing mass from
        # the least-loaded region. (The H2C half also had one at 150; that
        # station is now under the outer quarter's battery bays and is gone.)
        with Locations((95.0, 0, 0)):
            Cylinder(radius=17.0, height=FLOOR_T * 2,
                     align=(Align.CENTER, Align.CENTER, Align.MIN),
                     mode=Mode.SUBTRACT)
    return part.part


def create_quarter_outer_fused(leg_fb=LEG_FB):
    """REFERENCE ONLY since 2026-09-23 -- the pre-split outer quarter with the
    pods PRINTED IN (125 x 208.3 x 72, fits the A1 mini in no orientation).
    Not a printed part. The printed body and the bolt-on pods are CARVED from
    this solid (see create_quarter_outer / create_abduction_pod), which is
    what lets the gates prove the pod geometry did not move.

    Global 125..250: the splice posts at 125, the pod and its buttressing at
    the hip station, the hip-end wall with the contact pad, the two battery
    bays. Floor on the bed."""
    x0, x1 = OUTER_X0, OUTER_X1
    pod_x0 = leg_fb - POD_L
    with BuildPart() as part:
        # --- outer shell, hollowed through the splice face only -------------
        with Locations((x0, 0, 0)):
            Box(SEG_L, W, H, align=(Align.MIN, Align.CENTER, Align.MIN))
        with Locations((x0 - 1.0, 0, FLOOR_T)):
            Box(SEG_L + 1.0 - WALL, W - 2 * WALL, H - FLOOR_T,
                align=(Align.MIN, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
        _ledges(x0, x1)
        _splice_posts_add(x0, +1)

        # --- abduction servo pods, then their buttressing --------------------
        # Outboard of the side walls, straddling the hip station. Body reaches
        # inboard so the pod itself never projects past the robot's footprint.
        # ADD everything first, SUBTRACT after, so no bore gets backfilled.
        for sgn in (-1, 1):
            # The pod box is centred on POD_CY, not the abduction axis: the
            # recess comes off the outboard face only (see POD_Y_OUT above).
            with Locations((leg_fb - POD_L / 2, sgn * POD_CY, HIP_Z)):
                Box(POD_L, POD_W, POD_H, align=Align.CENTER)

            # 1. local wall boss, on the inside where the cavity is free
            with Locations((pod_x0 - BOSS_RUN,
                            sgn * (W / 2 - WALL - BOSS_T / 2), FLOOR_T)):
                Box(x1 - pod_x0 + BOSS_RUN, BOSS_T, H - LEDGE_T - FLOOR_T,
                    align=(Align.MIN, Align.CENTER, Align.MIN))

            # 2. triangular webs above and below, two along the pod's length so
            #    the cantilever is supported at more than one station
            for gx in (pod_x0, pod_x0 + POD_L / 2):
                add(_gusset(gx, sgn, FLOOR_T, POD_Z0))          # below
                add(_gusset(gx, sgn, H - LEDGE_T, POD_Z1))      # above

        # --- dock contact pad, inside the end wall ---------------------------
        with Locations((x1 - WALL - PAD_T, 0, PAD_Z0)):
            Box(PAD_T, 2 * PAD_HALF_W, PAD_Z1 - PAD_Z0,
                align=(Align.MIN, Align.CENTER, Align.MIN))

        # --- battery bay tray: ribs around two pockets, then the latch bosses -
        with Locations((BAY_X, 0, BAY_Z0)):
            Box(_TRAY_L, _TRAY_W, BAY_RIB_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
        for y in LATCH_Y:
            with Locations((LATCH_X, y, FLOOR_T)):
                Box(LATCH_BOSS, LATCH_BOSS, LATCH_BOSS_H,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))

        # ===================== SUBTRACT phase ================================
        _ledge_pilots(x0, x1)
        _splice_posts_cut(x0, +1)

        for sgn in (-1, 1):
            pod_cy = sgn * LEG_LR
            # servo pocket, open at the hip face so the servo slides in
            with Locations((leg_fb - POCKET_L / 2 + 0.5, pod_cy, HIP_Z)):
                Box(POCKET_L + 1.0, POCKET_W, POCKET_H,
                    align=Align.CENTER, mode=Mode.SUBTRACT)
            # horn / hip-disc clearance through the outboard end face
            with Locations((leg_fb, pod_cy, HIP_Z)):
                Cylinder(radius=HORN_BORE / 2, height=POD_L,
                         rotation=(0, 90, 0), mode=Mode.SUBTRACT)
            # cable pass-through (see RETRACTIONS: it exits outboard of the
            # wall, not into the cavity; untouched here)
            with Locations((pod_x0 + 2, pod_cy, HIP_Z)):
                Cylinder(radius=5.0, height=40.0,
                         rotation=(0, 90, 0), mode=Mode.SUBTRACT)

        # bay pockets: the pack drops in from above and sits on the floor top
        for y in BAY_Y:
            with Locations((BAY_X, y, BAY_Z0)):
                Box(BAY_L, BAY_W, BAY_RIB_H + 1.0,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    mode=Mode.SUBTRACT)
        # latch mounting pilots, from the top of each boss
        for y in LATCH_Y:
            for dy in (-LATCH_PILOT_DY, LATCH_PILOT_DY):
                with Locations((LATCH_X, y + dy, FLOOR_T + LATCH_BOSS_H)):
                    Cylinder(radius=M3_PILOT / 2, height=8.0,
                             align=(Align.CENTER, Align.CENTER, Align.MAX),
                             mode=Mode.SUBTRACT)
        # the rail rack's channel through the FRONT copy's tray (see above)
        with Locations((x0 - 1.0, 0, BAY_Z0)):
            Box(RACK_X_END - x0 + 1.0, 2 * RACK_CHANNEL_HALF_W, BAY_RIB_H + 1.0,
                align=(Align.MIN, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # contact-station pilots, from the OUTER face of the end wall inward
        for y, z in CONTACT_PILOT_YZ:
            with Locations((x1 - CONTACT_PILOT_DEPTH / 2, y, z)):
                Cylinder(radius=M3_PILOT / 2, height=CONTACT_PILOT_DEPTH,
                         rotation=(0, 90, 0), mode=Mode.SUBTRACT)
    return part.part


def _pod_voids(sgn, leg_fb=LEG_FB):
    """The legacy pod subtractions as plain solids -- the SAME boxes and
    cylinders create_quarter_outer_fused() cuts (pocket open at the hip face,
    horn bore, cable pass-through). Re-cut through the new flange so it can
    never close the pocket, and read by the gates."""
    cy = sgn * LEG_LR
    return [
        Box(POCKET_L + 1.0, POCKET_W, POCKET_H, align=Align.CENTER)
        .moved(Location((leg_fb - POCKET_L / 2 + 0.5, cy, HIP_Z))),
        Cylinder(radius=HORN_BORE / 2, height=POD_L, rotation=(0, 90, 0))
        .moved(Location((leg_fb, cy, HIP_Z))),
        Cylinder(radius=5.0, height=40.0, rotation=(0, 90, 0))
        .moved(Location((leg_fb - POD_L + 2, cy, HIP_Z))),
    ]


def _box(x0, x1, y0, y1, z0, z1):
    return Box(x1 - x0, y1 - y0, z1 - z0,
               align=(Align.MIN, Align.MIN, Align.MIN)).moved(Location((x0, y0, z0)))


def _socket_boxes(fit=0.0):
    """The +Y socket as two boxes (the -Y one is its mirror). fit = 0 is the
    body's cut; fit = TONGUE_FIT is the pod's tongue, shrunk on every
    bearing face. Box A: the outboard layer y SOCK_SHOULDER_Y..80, open
    through the end wall at x = 250. Box B: the deep layer y 70..76, closed
    by the end-wall post at x = 247 -- the shoulder that takes +X."""
    f = fit
    a = _box(SOCK_X0 + f, OUTER_X1 + (0.0 if f else 1.0),
             SOCK_SHOULDER_Y + f, SOCK_Y_OUT, SOCK_Z0 + f, SOCK_Z1 - f)
    b = _box(SOCK_X0 + f, SOCK_SHOULDER_X - f,
             SOCK_Y_IN - 1.0, SOCK_SHOULDER_Y + f, SOCK_Z0 + f, SOCK_Z1 - f)
    return [a, b]


def _mirror_y(s):
    return s.mirror(Plane.XZ)


def create_quarter_outer():
    """THE PRINTED OUTER QUARTER since 2026-09-23: the 160 mm body, no pod.
    = the legacy fused quarter cut to |y| <= W/2, minus the two pod
    sockets, plus the boss run forward to BODY_BOSS_X0 (the land the pod's
    inboard bolts need), minus six heat-set insert holes per side.
    Carries NO servo geometry (gated): not print-blocked by the caliper.
    Print pose as authored: floor on the bed, 125 x 160 x 72."""
    legacy = create_quarter_outer_fused()
    body = legacy & _box(OUTER_X0 - 1, OUTER_X1 + 1, -W / 2, W / 2, -1, H + 1)
    for sgn in (1, -1):
        boss = _box(BODY_BOSS_X0, OUTER_X1 - WALL, W / 2 - WALL - BOSS_T, W / 2 - WALL,
                    FLOOR_T, H - LEDGE_T)
        body = body + (boss if sgn > 0 else _mirror_y(boss))
    for sgn in (1, -1):
        for s in _socket_boxes():
            body = body - (s if sgn > 0 else _mirror_y(s))
        for x, z in POD_BOLT_XZ:
            hole = Cylinder(radius=INSERT_HOLE_D / 2, height=INSERT_HOLE_DEPTH,
                            rotation=(90, 0, 0)).moved(
                Location((x, sgn * (W / 2 - INSERT_HOLE_DEPTH / 2), z)))
            body = body - hole
    assert len(body.solids()) == 1, "outer body is not one solid"
    return body


def create_abduction_pod():
    """THE BOLT-ON ABDUCTION POD, authored in the robot frame of the FRONT
    +Y (left) station. = the legacy fused quarter's material outboard of the
    wall face (pod box, pocket, HIP_POD_FACE_Y recess, gussets -- untouched),
    plus the tongue (legacy material inside the socket, shrunk TONGUE_FIT on
    every bearing face), plus the flange on the wall face, minus the legacy
    voids re-cut and six M3 clearance holes. Mirror-symmetric about z = HIP_Z,
    so ONE STL serves all four stations (pods_placed)."""
    legacy = create_quarter_outer_fused()
    region = _box(OUTER_X0 - 1, OUTER_X1 + 1, W / 2, 300, -1, H + 1)
    for s in _socket_boxes(TONGUE_FIT):
        region = region + s
    pod = legacy & region
    pod = pod + _box(FLANGE_X0, OUTER_X1, W / 2, W / 2 + FLANGE_T, 0.0, H)
    for v in _pod_voids(+1):
        pod = pod - v
    for x, z in POD_BOLT_XZ:
        pod = pod - Cylinder(radius=M3_CLEAR / 2, height=FLANGE_T + 2.0,
                             rotation=(90, 0, 0)).moved(
            Location((x, W / 2 + FLANGE_T / 2, z)))
    assert len(pod.solids()) == 1, "pod is not one solid"
    return pod


# The rotation that turns the +Y pod into the -Y pod: 180 deg about the X
# line through (y 0, z HIP_Z). Equal to the Y-mirror because the pod is
# symmetric about z = HIP_Z (gated), so one printed part serves both sides.
POD_FLIP_AXIS = Axis((0, 0, HIP_Z), (1, 0, 0))


def chassis_placed(out_dir=None):
    """EVERY printed chassis part, robot frame, read from the exported STEPs:
    4 quarters + 4 pods + 6 splice keys (name -> solid). The one call every
    consumer uses since 2026-09-23 -- the transitional fused chassis_half
    is for sweeps (hip_module, extension_stowage) only."""
    from build123d import import_step
    out = Path(out_dir) if out_dir else Path(__file__).parent / "output"
    ld = lambda n: import_step(str(out / f"{n}.step"))
    parts = dict(quarters_placed(ld("chassis_quarter_inner"),
                                 ld("chassis_quarter_outer")))
    parts.update(pods_placed(ld("abduction_pod")))
    for i, k in enumerate(keys_placed(ld("chassis_splice_key"))):
        parts[f"splice_key_{i}"] = k
    return parts


def pods_placed(pod):
    """The four pods in the robot frame (X fore, Y left, Z up). Front pair:
    front_left = identity, front_right = rotate(POD_FLIP_AXIS, 180). Rear
    pair: the front pair rotated 180 deg about Z, exactly as the outer
    quarters are (quarters_placed) -- so each pod rides its own quarter."""
    fl = copy.copy(pod)
    fr = pod.rotate(POD_FLIP_AXIS, 180)
    return {
        "pod_front_left": fl,
        "pod_front_right": fr,
        "pod_rear_right": fl.rotate(Axis.Z, 180),     # +Y pod -> y < 0, x < 0
        "pod_rear_left": fr.rotate(Axis.Z, 180),
    }


def pod_print_pose(pod):
    """Hip face (x = 250) down: flange, tongue and pod walls all stand
    vertical, the pocket is a vertical shaft open at the bed."""
    p = pod.rotate(Axis.Y, 90)
    bb = p.bounding_box()
    return p.moved(Location((-bb.min.X, -bb.min.Y, -bb.min.Z)))


def create_splice_key():
    """The loose shear key. Registers Y and Z across a splice; the post bolts
    do the clamping. Prints flat, as modelled (centred on the origin)."""
    with BuildPart() as part:
        Box(KEY_L, KEY_W - KEY_FIT, KEY_H - KEY_FIT, align=Align.CENTER)
    return part.part


def quarters_placed(inner, outer):
    """The four quarters in the robot frame. THE placement convention:
    front pair identity, rear pair rotate(Axis.Z, 180) -- exactly how the
    H2C-era rear half was placed and how waist_rail.way_run() places the
    rear way segments. Returns an ordered dict name -> solid."""
    return {
        "front_inner": copy.copy(inner),                 # x   0..125
        "front_outer": copy.copy(outer),                 # x 125..250
        "rear_inner": inner.rotate(Axis.Z, 180),         # x -125..0
        "rear_outer": outer.rotate(Axis.Z, 180),         # x -250..-125
    }


def keys_placed(key):
    """The six splice keys, robot frame: two per splice plane, in the posts."""
    return [copy.copy(key).moved(Location((xs, sgn * POST_Y, KEY_Z)))
            for xs in CHASSIS_SPLICE_X for sgn in (-1, 1)]


def pack_seated(rear=True):
    """A battery pack's envelope, seated in one bay, robot frame. Both bays of
    the rear copy by default (the populated ones)."""
    xs = -BAY_X if rear else BAY_X
    return [Box(PACK_L, PACK_W, PACK_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
            .moved(Location((xs, y, BAY_Z0))) for y in BAY_Y]


def pack_extraction_sweep(rear=True):
    """The volume a pack sweeps lifting straight up out of its bay by
    PACK_LIFT -- past the ledge plane (72) and the way heads (84)."""
    xs = -BAY_X if rear else BAY_X
    return [Box(PACK_L, PACK_W, PACK_H + PACK_LIFT,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
            .moved(Location((xs, y, BAY_Z0))) for y in BAY_Y]


def create_chassis_half():
    """TRANSITIONAL: the H2C-era 0..250 half, as inner + outer body + the
    two FRONT pods, bolted and FUSED. Kept so downstream placers that import
    chassis_half.step (hip_module.py's sweeps, assembly*.py, marks.py,
    extension_stowage.py, sim/mjcf_export.py) see the same pod at the same
    place until they migrate. Not a printed part."""
    pods = pods_placed(create_abduction_pod())
    half = create_quarter_inner() + create_quarter_outer() \
        + pods["pod_front_left"] + pods["pod_front_right"]
    assert len(half.solids()) == 1, "inner, outer and pods did not fuse into one solid"
    return half


def _vol(a, b):
    hit = a & b
    return 0.0 if hit is None else hit.volume


if __name__ == "__main__":
    import contextlib
    import io
    import math

    from partcheck import BED, check

    out = Path(__file__).parent / "output"
    out.mkdir(exist_ok=True)
    evidence = Path(__file__).parent.parent.parent / "docs" / "evidence"

    inner = create_quarter_inner()
    legacy = create_quarter_outer_fused()
    outer = create_quarter_outer()
    pod = create_abduction_pod()
    key = create_splice_key()
    pods = pods_placed(pod)

    # ---------------------------------------------------------------- exports
    for nm, s in (("chassis_quarter_inner", inner),
                  ("chassis_quarter_outer", outer),
                  ("chassis_splice_key", key),
                  ("abduction_pod", pod)):          # STEP: robot frame, front-left
        export_step(s, str(out / f"{nm}.step"))
        export_stl(s, str(out / f"{nm}.stl"))
    half = create_chassis_half()
    export_step(half, str(out / "chassis_half.step"))
    export_stl(half, str(out / "chassis_half.stl"))
    stale = out / "chassis_half.3mf"      # a print file for an unprintable part
    if stale.exists():
        stale.unlink()

    for nm, s in (("chassis_quarter_inner", inner), ("chassis_quarter_outer", outer),
                  ("abduction_pod", pod), ("(legacy fused outer)", legacy)):
        bb = s.bounding_box()
        print(f"{nm}: x {bb.min.X:.1f}..{bb.max.X:.1f}  "
              f"{bb.size.X:.1f} x {bb.size.Y:.2f} x {bb.size.Z:.1f} mm   "
              f"{s.volume / 1000:.1f} cm3  PETG ~{s.volume / 1000 * 0.953:.0f} g")
    tot = 2 * (inner.volume + outer.volume) + 4 * pod.volume
    print(f"four quarters + four pods PETG ~{tot / 1000 * 0.953:.0f} g "
          f"(fused-pod quarters were ~{2 * (inner.volume + legacy.volume) / 1000 * 0.953:.0f} g)")

    # ------------------------------------------------------ GATE 1: the grid
    pi, po = quarter_pilots(INNER_X0, INNER_X1), quarter_pilots(OUTER_X0, OUTER_X1)
    assert pi == (40.0, 80.0, 120.0) and po == (160.0, 200.0), (pi, po)
    assert set(pi) | set(po) == set(range(40, int(2 * SEG_L) - 20, 40)), (
        "ledge pilot grid no longer matches waist_rail.way_run()'s law")
    print(f"ledge pilots  inner {pi}  outer {po}  (global, +/- on the rear pair)")

    # ----------------------------------------- GATE 2: tiling and envelope
    placed = quarters_placed(inner, outer)
    spans = sorted((round(s.bounding_box().min.X, 6), round(s.bounding_box().max.X, 6))
                   for s in placed.values())
    joints = []
    for (a0, a1), (b0, b1) in zip(spans, spans[1:]):
        assert abs(a1 - b0) < 1e-6, f"quarters do not tile: {a1} vs {b0}"
        joints.append(a1)
    assert joints == sorted(CHASSIS_SPLICE_X), (joints, CHASSIS_SPLICE_X)
    assert (spans[0][0], spans[-1][1]) == (-2 * SEG_L, 2 * SEG_L)
    asm = Compound(children=[copy.copy(s) for s in placed.values()]
                   + [copy.copy(p) for p in pods.values()])
    ab = asm.bounding_box()
    ib, ob = inner.bounding_box(), outer.bounding_box()
    assert abs(ab.size.X - CHASSIS_LENGTH) < 1e-6 and abs(ab.size.Z - H) < 1e-6
    for b in (ib, ob):
        assert abs(b.size.Y - W) < 1e-6 and abs(b.size.Z - H) < 1e-6, b.size
    assert abs(ab.size.Y - 2 * POD_Y_OUT) < 1e-6, ab.size
    print(f"assembled     {ab.size.X:.1f} x {ab.size.Y:.2f} (pods; body {ob.size.Y:.0f}) "
          f"x {ab.size.Z:.1f} mm, splices on {joints}")

    # ---------------------------------- GATE 3: nothing interpenetrates
    keys = keys_placed(key)
    bodies = list(placed.items()) + list(pods.items()) \
        + [(f"key{i}", k) for i, k in enumerate(keys)]
    worst = 0.0
    for i, (na, a) in enumerate(bodies):
        for nb, b in bodies[i + 1:]:
            v = _vol(a, b)
            worst = max(worst, v)
            assert v < 1e-6, f"{na} x {nb} interpenetrate by {v / 1000:.4f} cm3"
    print(f"interpenetration, 4 quarters + 4 pods + 6 keys pairwise: max {worst:.2e} mm3")

    for k in keys:
        c = k.center()
        pocket = Box(2 * KEY_POCKET_D, KEY_W, KEY_H, align=Align.CENTER) \
            .moved(Location((c.X, c.Y, c.Z)))
        assert abs(_vol(k, pocket) - k.volume) < 1e-6, "key stands proud of its pocket"

    # -------------------- GATE 4: the rack channel is free at every splice
    rack_p = out / "rail_rack.step"
    if rack_p.exists():
        rack = import_step(str(rack_p)).moved(Location((102.0, 0, 0)))   # RAIL_MID
        rv = sum(_vol(rack, s) for s in placed.values())
        print(f"rail rack (at RAIL_MID) vs quarters: {rv / 1000:.4f} cm3 "
              f"(H2C-era bulkhead: 1.8867)")
        assert rv < 1e-6, "a splice post cuts the rail rack"
    else:
        print("GATE 4 SKIPPED: output/rail_rack.step missing (run waist_rail.py)")

    # ----------------- GATE 5: pack extraction sweep (LAW: it moves)
    sweep = pack_extraction_sweep(rear=True)
    for pk in pack_seated(rear=True):
        pb = pk.bounding_box()
        print(f"pack seated   x {pb.min.X:.1f}..{pb.max.X:.1f}  y {pb.min.Y:.1f}..{pb.max.Y:.1f}"
              f"  z {pb.min.Z:.1f}..{pb.max.Z:.1f}")
    worst = 0.0
    for sw in sweep:
        for nm, s in list(placed.items()) + list(pods.items()):
            worst = max(worst, _vol(sw, s))
    print(f"pack lift sweep (+{PACK_LIFT:.0f} mm) vs quarters + pods: max {worst / 1000:.4f} cm3")
    assert worst < 1e-6, "a pack cannot be lifted out of its bay"
    way_p = out / "rail_way_outer.step"
    if way_p.exists():
        wo = import_step(str(way_p))
        ways = [wo.rotate(Axis.Z, 180).moved(Location((-SEG_L, sy * LEDGE_Y, H)))
                for sy in (1, -1)]                     # way_run()'s rear placement
        wb = ways[0].bounding_box()
        wv = max(_vol(sw, w) for sw in sweep for w in ways)
        print(f"pack lift sweep vs rear way segments (heads at |y| >= "
              f"{min(abs(wb.min.Y), abs(wb.max.Y)):.1f}): max {wv / 1000:.4f} cm3")
        assert wv < 1e-6, "a pack cannot be lifted past the way heads"
        pv = max(_vol(w, p) for w in ways for p in pods.values())
        print(f"rear way segments vs pods: max {pv / 1000:.4f} cm3")
        assert pv < 1e-6, "a pod (flange/bolt land) hits a way segment"
        y_clear = min(abs(wb.min.Y), abs(wb.max.Y)) - (abs(BAY_Y[1]) + PACK_W / 2)
        print(f"  lateral clearance pack edge -> way head: {y_clear:.1f} mm; "
              f"-> ledge: {LEDGE_Y - LEDGE_W / 2 - (abs(BAY_Y[1]) + PACK_W / 2):.1f} mm")
    else:
        print("GATE 5b SKIPPED: output/rail_way_outer.step missing")

    # ------------------------- GATE 6: the bolt-on pod (decision 7, 2026-09-23)
    print("\nGATE 6 -- bolt-on pod")
    fl, fr = pods["pod_front_left"], pods["pod_front_right"]
    # (a) bolted envelope == the fused envelope it replaces
    bolted = Compound(children=[copy.copy(outer), copy.copy(fl), copy.copy(fr)])
    nb_, lb_ = bolted.bounding_box(), legacy.bounding_box()
    d_env = max(abs(a - b) for a, b in zip(
        (nb_.min.X, nb_.min.Y, nb_.min.Z, nb_.max.X, nb_.max.Y, nb_.max.Z),
        (lb_.min.X, lb_.min.Y, lb_.min.Z, lb_.max.X, lb_.max.Y, lb_.max.Z)))
    print(f"  bolted body+pods envelope {nb_.size.X:.2f} x {nb_.size.Y:.2f} x {nb_.size.Z:.2f}"
          f" vs fused {lb_.size.X:.2f} x {lb_.size.Y:.2f} x {lb_.size.Z:.2f}: max corner delta {d_env:.1e} mm")
    assert d_env < 1e-6, "bolted envelope differs from the fused outer quarter"
    # (b) body vs pod interpenetration when bolted (also inside gate 3)
    v_bp = max(_vol(outer, fl), _vol(outer, fr))
    print(f"  body x pod interpenetration, bolted: {v_bp:.2e} mm3")
    assert v_bp < 1e-6
    # (c) every mm3 of the legacy pod outboard of the wall face is in the pod
    far = _box(OUTER_X0 - 1, OUTER_X1 + 1, W / 2, 300, -1, H + 1)
    lost = []
    for sgn, p in ((1, fl), (-1, fr)):
        lp = legacy & (far if sgn > 0 else _mirror_y(far))
        lost.append((lp - p).volume if (lp - p) is not None else 0.0)
    print(f"  legacy pod material (|y| > {W / 2:.0f}) missing from the pods: "
          f"{max(lost):.2e} mm3")
    assert max(lost) < 1e-6, "the split lost pod geometry"
    # (d) the pocket, horn bore and cable bore are still empty in the bolted
    #     assembly, and the BODY carries no servo geometry at either height
    v_void = max(_vol(v, s) for sgn in (1, -1) for v in _pod_voids(sgn)
                 for s in (outer, fl, fr))
    print(f"  pocket/horn/cable voids vs body+pods: {v_void:.2e} mm3")
    assert v_void < 1e-6
    for hh in (35.0, 37.8):
        ph = hh + SERVO_POCKET_CLEARANCE
        env = _box(LEG_FB - POCKET_L, LEG_FB + 1, LEG_LR - POCKET_W / 2, 300,
                   HIP_Z - ph / 2, HIP_Z + ph / 2)
        vb = max(_vol(outer, env), _vol(outer, _mirror_y(env)))
        print(f"  body vs pocket envelope at servo height {hh}: {vb:.2e} mm3  "
              f"tongue walls (sill/header, end, back) "
              f"{', '.join(f'{w:.2f}' for w in _tongue_walls(hh))} mm")
        assert vb < 1e-6, "the body still carries servo geometry"
    # (e) hip station and recess unchanged
    pbb = fl.bounding_box()
    assert abs(pbb.max.Y - HIP_POD_FACE_Y) < 1e-6, pbb.max.Y
    print(f"  pod outboard face y = {pbb.max.Y:.4f} == HIP_POD_FACE_Y; hip station "
          f"({LEG_FB:.0f}, +/-{LEG_LR:.0f}, {HIP_Z:.0f}); POD_X0 {POD_X0:.2f} "
          f"POD_Z0..Z1 {POD_Z0:.2f}..{POD_Z1:.2f}")
    # (f) ONE part serves both sides: the flip equals the mirror
    mir = _mirror_y(pod)
    sd = (fr - mir).volume + (mir - fr).volume
    print(f"  flip(180 about X @ z {HIP_Z:.0f}) vs mirror(XZ): symmetric difference {sd:.2e} mm3")
    assert sd < 1e-3, "pod is not symmetric about HIP_Z; left/right need two parts"
    # (g) what the tongue fit shaves off the legacy material, reported
    sock = _socket_boxes()
    skin = sum(((legacy & s) - fl).volume for s in sock if (legacy & s) is not None)
    print(f"  tongue fit {TONGUE_FIT} mm/face shaves {skin:.1f} mm3 of legacy material "
          f"per pod; flange adds {(fl - legacy).volume / 1000:.2f} cm3")
    # (h) every pod rides its own quarter's span
    for nm, p in pods.items():
        b = p.bounding_box()
        lo, hi = sorted((abs(b.min.X), abs(b.max.X)))
        assert b.min.X * b.max.X > 0 and OUTER_X0 <= lo and abs(hi - OUTER_X1) < 1e-6, nm

    # --------------------------------------------- LOAD PATH (computed here)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            import balance as BAL
        m_tot = 4 * BAL.LEG_TOTAL + BAL.CHASSIS + BAL.SPINE + BAL.TORSO_FULL + BAL.BATTERY
        leg_g = BAL.LEG_TOTAL
    except Exception as e:                       # the mass model must not gate CAD
        print(f"  (balance.py unavailable: {e}; using 4400 g)")
        m_tot, leg_g = 4400.0, 336.0
    from interface_constants import L1_LATERAL, STANCE_Z
    g0 = 9.80665
    T_STALL = 2.4516                              # N.m, MEASURED (design log, item 2)
    fz = m_tot / 1000 * g0 / 2                    # one leg carrying HALF the robot
    arm = (LEG_LR - W / 2) / 1000                 # abduction axis -> joint plane
    mx = T_STALL + fz * arm                       # about X, at the joint plane
    L_t = SOCK_SHOULDER_X - SOCK_X0 - 2 * TONGUE_FIT       # tongue bearing length, X
    d_t = SOCK_Y_OUT - SOCK_Y_IN                           # socket depth, Y
    f_couple = mx / (d_t / 3 / 1000)             # two triangular blocks, arm d/3
    p_peak = 2 * f_couple / (L_t * d_t)          # MPa
    p_fz = fz / (L_t * d_t)
    zs = [z for _, z in POD_BOLT_XZ]
    # bolts-only path (no tongue): pivot on the flange's far edge, z = 0 or H
    t_bolt = mx * 1000 * max(zs) / sum(z * z for z in zs)
    fx = fz                                       # mu = 1 bound, no friction credit
    my = fx * (STANCE_Z + HIP_Z - FLOOR_T) / 1000  # foot to joint, about Y
    h_t = SOCK_Z1 - SOCK_Z0
    f_my = my / (L_t / 1000)                      # couple on sill+header over L_t
    print(f"\nLOAD PATH  robot {m_tot:.0f} g (leg {leg_g:.0f} g); one leg at half weight "
          f"Fz = {fz:.1f} N; stall {T_STALL} N.m (measured)")
    print(f"  Mx at joint plane = stall + Fz x {arm * 1000:.0f} mm = {mx:.3f} N.m")
    print(f"  tongue bearing, {L_t:.1f} x {d_t:.0f} mm sill/header: Mx couple {f_couple:.0f} N "
          f"(peak {p_peak:.2f} MPa); Fz alone {p_fz:.3f} MPa")
    print(f"  bolts-only fallback (tongue ignored): worst M3 tension {t_bolt:.0f} N = "
          f"{t_bolt / M3_TENSILE_AREA:.1f} MPa on the {M3_TENSILE_AREA} mm2 stress area")
    print(f"  Fx (mu = 1 bound) {fx:.1f} N bears on x = {SOCK_X0:.0f} (-X) or the "
          f"x = {SOCK_SHOULDER_X:.0f} shoulder (+X), {h_t:.0f} x {SOCK_SHOULDER_Y - SOCK_Y_IN:.0f} mm "
          f"= {fx / (h_t * (SOCK_SHOULDER_Y - SOCK_Y_IN)):.3f} MPa; My = {my:.2f} N.m -> "
          f"sill/header couple {f_my:.0f} N")

    # ---------------------------------------------------------- partcheck
    # LAW 4: grade in the PRINT orientation, and gate the bed on the MEASURED
    # bounding box OF THAT POSE (not "some orientation fits").
    printed_key = key.rotate(Axis.X, 90)
    printed_key = printed_key.moved(Location((0, 0, -printed_key.bounding_box().min.Z)))
    export_stl(printed_key, str(out / "chassis_splice_key.stl"))
    printed_pod = pod_print_pose(pod)
    export_stl(printed_pod, str(out / "abduction_pod.stl"))
    export_step(printed_pod, str(out / "abduction_pod_print.step"))
    results = []
    for s, nm in ((inner, "chassis_quarter_inner"), (outer, "chassis_quarter_outer"),
                  (printed_key, "chassis_splice_key"), (printed_pod, "abduction_pod")):
        r = check(s, nm, out_dir=str(out), material="PETG")
        assert r["solids"] == 1 and r["watertight"], r["name"]
        b = s.bounding_box()
        posed = (b.size.X, b.size.Y, b.size.Z)
        r["fits_pose"] = all(v <= lim + 1e-9 for v, lim in zip(posed, BED))
        results.append(r)
    print("\nBED GATE (measured bbox in print pose vs A1 mini "
          f"{BED[0]:.0f} x {BED[1]:.0f} x {BED[2]:.0f}):")
    unprintable = []
    for r in results:
        sz = r["size_mm"]
        d = r["overhang_detail"]
        print(f"  {'OK  ' if r['fits_pose'] else 'FAIL'} {r['name']:24s} "
              f"{sz[0]:6.1f} x {sz[1]:6.1f} x {sz[2]:6.1f}  {r['mass_g']:6.1f} g  "
              f"support {100 * r['support_frac']:.1f}%  bed {d['bed_contact_mm2']:.0f} mm2")
        if not r["fits_pose"]:
            unprintable.append(r)
            mf3 = out / f"{r['name']}.3mf"
            if mf3.exists():
                mf3.unlink()

    # ---------------------------------------------------------- evidence
    export_step(Compound(children=[copy.copy(s) for s in placed.values()]
                         + [copy.copy(p) for p in pods.values()]
                         + [copy.copy(k) for k in keys]),
                str(out / "chassis_quarters_assembly.step"))
    slab_in = inner & Box(25, 300, 100, align=(Align.MAX, Align.CENTER, Align.MIN)) \
        .moved(Location((SEG_L, 0, 0)))
    slab_out = outer & Box(25, 300, 100, align=(Align.MIN, Align.CENTER, Align.MIN)) \
        .moved(Location((SEG_L, 0, 0)))
    export_step(Compound(children=[
        slab_in,
        *[copy.copy(k).moved(Location((8.0, 0, 0))) for k in keys if abs(k.center().X - SEG_L) < 1e-6],
        slab_out.moved(Location((16.0, 0, 0))),
    ]), str(out / "chassis_splice_closeup.step"))
    # pod joint close-up: the +Y corner of the body and the pod pulled 25 mm
    # outboard, so the socket, shoulder, tongue and insert holes all show
    corner = outer & _box(170, 251, 40, W / 2, -1, H + 1)
    export_step(Compound(children=[corner, copy.copy(pod).moved(Location((0, 25.0, 0)))]),
                str(out / "chassis_pod_joint.step"))
    export_step(Compound(children=[copy.copy(outer), copy.copy(fl), copy.copy(fr)]),
                str(out / "chassis_pod_bolted.step"))
    print(f"\nevidence STEPs -> {out}/chassis_pod_bolted.step, chassis_pod_joint.step, "
          f"abduction_pod_print.step, chassis_quarters_assembly.step "
          f"(render with edu/tools/hero_render.py into {evidence}/chassis_pod_*.png)")

    print("\nPRINT-BLOCKED (abduction_pod only): servo height unresolved (35.00 vs "
          "37.80) -- the pocket derives from it; gated at both; do not print the "
          "pod before the caliper. The outer BODY now carries no servo geometry "
          "(gate 6d) and, like the inner quarter, is not caliper-blocked.")
    if unprintable:
        for r in unprintable:
            sz = r["size_mm"]
            print(f"\nBED GATE FAILED: {r['name']} is {sz[0]:.1f} x {sz[1]:.1f} x "
                  f"{sz[2]:.1f} mm in its print pose")
        sys.exit(1)
