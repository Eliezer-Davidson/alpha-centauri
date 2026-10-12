"""Alpha Centauri — the fore-aft waist rail: torso slides along the body.

    edu/.cadenv/bin/python cad/alpha_centauri/waist_rail.py

WHY THIS IS Mk1 AND NOT Mk2
---------------------------
The author, 2026-08-01. It is not a luxury -- it is the only thing that makes a FORWARD
torso possible at all. balance.py retracted the asymmetric-hip idea: with a fixed
wheelbase, moving the hip stations only relabels the origin. What actually binds
is the crawl. Lifting a FRONT foot puts the centre of mass aft of the wheelbase
midpoint; lifting a REAR foot puts it forward. Both directions squeeze, so a
FIXED torso has to sit essentially at the middle, and you get the centred look
the author rejected.

The torso is 1538 g of a 4370 g robot -- 35.2%. Sliding it d mm moves the CoM
0.352*d. So 150 mm of travel is 53 mm of CoM authority, against a crawl boundary
that is tight to about 25 mm. It is the largest single lever on the machine.

Used BACKWARDS from the obvious: slide AFT to walk, FORWARD to work. It is not a
better fixed compromise, it is a mode switch.

THE VARIANT SEAM RUNS THROUGH THIS FILE
---------------------------------------
The author, 2026-08-01: "this could be a split between the servo+ version and the
servo- version." It is, and cleanly:

    SHARED     rail_way x4, rail_rack x1, rail_carriage x1
               (2026-09-07: the shared row is now rail_way_inner x4 +
               rail_way_outer x4 + rail_way_key x6, and the carriage is two
               bolted halves -- see SEGMENTED FOR THE A1 MINI below. The seam
               itself is unchanged: both modules still bolt to the same four
               holes at the same station.)
    servo+     rail_pinion + rail_drive_tower  (ST3215 stands in the waist box,
               shaft DOWN through the carriage, involute pinion on the rack)
    servo-     rail_pawl                       (sprung two-way detent on the same
               rack, same four carriage bolts, pushed by the arms)

Both modules bolt to the SAME four holes on the carriage at the SAME station.
You can build one robot and swap which module is fitted, which is the only
honest way to answer "we will have to see what these two versions end up being."

WHY THE RACK LIVES DOWN IN THE CHASSIS WELL
-------------------------------------------
Three layouts were tried on paper and two died:

  teeth UP, pinion above    -- the pinion radius forces its axis ~20 mm over the
                               rack, which lands inside the waist box floor.
  teeth SIDEWAYS at deck    -- the rack then passes THROUGH the carriage plate
                               for its full length, and a slot open at both ends
                               cuts the carriage into two unconnected rails.
  teeth SIDEWAYS, low  <--   the rack sits entirely below the ledges (z 4..64),
                               the carriage is an UNBROKEN plate with one 24 mm
                               hole, and the drive module reaches down through it.

The third also makes the two variants interchangeable, because both modules are
things that hang down through that one hole.

WHY A TWO-WAY DETENT AND NOT A RATCHET
--------------------------------------
The spine gets away with a one-way tooth because gravity only ever pulls the
chest DOWN. Here it is walking inertia, which throws the torso fore AND aft, so
a one-way pawl would let the waist creep forward one tooth per step until it ran
out of rail. Both flanks have to hold.

The rack's own 20-degree pressure-angle flanks do that for free. A flank 20 deg
off the lift direction is 70 deg off the travel direction, so a detent preload P
resists P*tan(70) = 2.75*P of push before it cams out. Steep flanks hold; that is
why a gear rack makes a better detent track than a purpose-drawn vee.

WHY THE RELEASE LEVER IS NOT OPTIONAL ON THE servo- BUILD
---------------------------------------------------------
This is the finding the author predicted -- "relying so much on the hands is dangerous
and will put a lot of strain on the hand servos." Run the numbers and he is
right, but only for one of the three hand-driven jobs. See hand_load.py: shoving
1538 g against a detent stiff enough to survive walking needs ~29 N, which is
88% of what two arms can stall out. Pulling the pawl FIRST drops it to friction
alone, about 5 N. So the servo- rail is comfortable WITH a release lever and
marginal without one. The lever costs 6 g.

SEGMENTED FOR THE A1 MINI (2026-09-07, edu/REPLAN-2026-08-28.md item 3)
-----------------------------------------------------------------------
The H2C is gone; the only printer is a Bambu A1 mini (180^3). The 250 mm ways
and the 200 x 170 carriage were the two casualties in this file.

WAYS. Segmented at 125 mm, joints ON the chassis splice planes
(CHASSIS_SPLICE_X = -125, 0, +125), per the REPLAN. Two findings from doing it:

  * THE 40 mm LEDGE GRID DOES NOT DIVIDE 125. The chassis ledge pilots sit at
    40..200 mm from each half's split face (chassis.py:221, range(40, 230, 40)),
    i.e. global +/-40..+/-200. A 125 mm segment boundary is incommensurable with
    that grid, so ONE segment drawing cannot serve every station -- there are
    TWO variants: inner (splice-to-splice, holes at local 40, 80) and outer
    (splice-to-pod, holes at local 35, 75). Tiled, they land on +/-40, +/-80,
    +/-160, +/-200 -- a subset of the ledge grid. The +/-120 pilots go unused:
    local 120 on a 125 mm part is 5 mm from the joint face, inside the 20 mm
    end margin the 250 mm way already enforced. Bolt count per 250 mm run drops
    5 -> 4; flagged in the report, not hidden.
  * THE OLD REAR WAYS NEVER MATCHED THEIR LEDGE. assembly_centaur.py places the
    rear chassis half ROTATED 180 (pilots at -40..-200) but the rear ways only
    TRANSLATED (bolts at -210..-50). Every rear rail bolt missed its pilot by
    10 mm and nothing ever checked. The segmented run is placed the same way
    the chassis is -- rear segments rotated 180 -- and way_run() now ASSERTS
    every bolt lands on the ledge grid, so the mistake cannot come back.

The joint is a square butt with a LOOSE KEY (6 x 2.5 x 9.6, pockets in BOTH end
faces of BOTH variants). Loose key rather than tab-and-pocket because the rear
segments are the front segments rotated 180: a male end would meet a male end
at x = 0. The key registers Y and Z across the joint so the dovetail running
surfaces line up; the ledge bolts, 40 mm away on each side, do the clamping.
The key sits in the BASE (z 1.25..3.75), below the shoe's swept envelope by
0.9 mm -- the sweep assert covers it anyway.

CARRIAGE. Split at x = 0 -- the mirror plane -- into two 100 x 170 halves,
dowelled and bolted (REPLAN: "two bolted mirror halves, dowelled").
create_carriage() still builds the monolith as the reference, the halves are
cut FROM it, and main() asserts (a) the assembled halves' bounding box equals
the monolith's and (b) probe volumes around each dovetail channel are
IDENTICAL between monolith and assembly -- because the rail slide envelope is
load-bearing for the extension-stowage study.

RETRACTION FOUND BY THE NEW SWEEP, same date: the female dovetail channel was
drawn INVERTED (wide at the bottom in the robot frame, mirroring nothing) and
the carriage as previously committed interfered with its own ways by 2884 mm3
per shoe-way pair -- it could never have been assembled. No carriage-vs-way
swept assert existed, so nothing caught it; the sweep added for the
segmentation caught it on its first run. The channel now mirrors the male way
at SHOE_CLEAR per face (see the retraction comment in create_carriage). What
the stowage study consumed -- way position LEDGE_Y, head width, the z 72..84
band, the carriage ENVELOPE -- is exactly as it was; the correction is inside
the shoes. way_clearance -1.0 mm and the 2 mm shift question are untouched.

Joint hardware, and why it is where it is:
  * 4 steel dowels (3 mm, in-plate at z=+4, y = -75, -30, +45, +75): the +/-75
    pair sits directly over each shoe so the female channels register across
    the joint; the bores stop 2.3 mm above the channel roof.
  * 2 M4 x 30 cross-bolts in bosses UNDER the plate at y = +/-50, hanging 6 mm
    into the z 78..84 band. That band is empty at |y| <= 56: the ways start at
    y = 63, the ledges top out at z = 72, the rack at z = 64, and the chest
    verticals (y = +/-60, the stowage study's 1 mm clash) live at x = +/-49.5
    in the carriage frame while the bosses stay inside |x| <= 17.5. Head
    pockets and nut slots alternate direction (+y bolt heads aft, -y heads
    fwd), all opening DOWNWARD so the plate's top face stays flush for the
    waist box. In the print pose (plate-top on the bed) they open upward and
    print unsupported.
  * The halves are NOT interchangeable prints: the drive hole at y = +24.66
    breaks every symmetry that could have made one STL serve both. Two parts.

STIFFNESS CONSEQUENCES OF SEGMENTING -- flagged, not solved:
  * A butt+key joint carries shear but ZERO bending moment. Way bending
    continuity across a joint now comes from the ledge it bolts to -- and the
    chassis itself splices at the SAME x planes (that co-location is the
    REPLAN's own choice, for print logistics), so the rail's softest sections
    sit exactly on the chassis's softest sections. The 200 mm shoe always
    bridges at least one joint, which helps, but nobody has measured the
    stack's compliance.
  * Each 125 mm segment is held by TWO bolts, not five-per-250; a segment is
    a shorter lever against its own bolts, but the run as a whole lost 2 of
    10 anchors per side.
  * The carriage joint at x = 0 passes through the drive hole and severs the
    lightening cross-rib at the highest-load station. The waist box floor
    (4 bolts at x = +/-45) and the drive module (4 bolts at x = +/-13.4)
    both bridge the joint in service, but the bare two-half plate is torsion-
    softer than the monolith was.
  * Square butt seams on the running surface every 125 mm: the shoe crosses a
    seam whose step height is whatever the key + printing tolerance leave.
    If it clicks, the fix is a hand-chamfer on the seam edges, not a redesign.

SCOPE GUARD, same date: extension_stowage.py measured the chest verticals
(y = +/-60) overlapping the way heads by exactly 1.00 mm in z 72..84 and
recommends a 2 mm inboard shift of the RODS. That recommendation is AWAITING
the author's approval and is deliberately NOT implemented here: the ways stand where
they stood, at LEDGE_Y with a 16 mm head, and the carriage gains no rod holes.
"""

import copy
import math
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
)

from interface_constants import (
    BED_X,
    BED_Y,
    BED_Z,
    CHASSIS_HEIGHT,
    CHASSIS_SEGMENT_LENGTH,
    CHASSIS_SPLICE_X,
    CHASSIS_WIDTH,
)

# ------------------------------------------------------------------ fasteners
M4_CLEAR, M4_PILOT = 4.4, 3.6
M3_CLEAR, M3_PILOT = 3.4, 2.6

# --------------------------------------------------------------- the stations
# All Z here are ABOVE THE CHASSIS FLOOR TOP (chassis floor is 4 mm thick, so
# chassis-local z = 4 is the well floor and z = 72 is the ledge top plane).
CHASSIS_FLOOR_T = 4.0
LEDGE_TOP = CHASSIS_HEIGHT               # 72.0, where the ways bolt down
LEDGE_W = 12.0                           # matches chassis.py
LEDGE_Y = CHASSIS_WIDTH / 2 - 3.0 - LEDGE_W / 2      # 71.0, ledge centreline

TRAVEL = 150.0                           # DECISION  aft (walk) -> forward (work)

# ------------------------------------------------------------------- the ways
# Dovetail, wide at the TOP. Printed lying on its base the flare is a 45 deg
# self-supporting slope, and the female channel in the carriage is the same
# slope inverted -- so neither part needs support anywhere. That is the whole
# reason this is a dovetail and not a tee.
#
# H2C-era WAY_L was 250.0 -- one chassis half, 4 identical parts. RETIRED
# 2026-09-07: 250 does not fit the A1 mini in any orientation. Segments are
# CHASSIS_SEGMENT_LENGTH so every joint lands ON a chassis splice plane.
WAY_SEG_L = CHASSIS_SEGMENT_LENGTH       # 125.0; joints on CHASSIS_SPLICE_X
WAY_BASE_W = LEDGE_W                     # 12.0, sits exactly on the ledge
WAY_BASE_H = 5.0
WAY_NECK_W = 8.0
WAY_HEAD_W = 16.0
WAY_FLARE_H = (WAY_HEAD_W - WAY_NECK_W) / 2.0        # 4.0 at 45 deg
WAY_LAND_H = 3.0
WAY_H = WAY_BASE_H + WAY_FLARE_H + WAY_LAND_H        # 12.0
WAY_BOLT_PITCH = 40.0                    # matches the chassis ledge hole pattern
# Ledge pilots sit at local 40..200 from each chassis half's split face
# (chassis.py:221, range(40, half_l - 20, 40)) -- restated here because chassis
# exposes no constant for it; way_run() asserts every tiled bolt lands on that
# grid, so the restatement is guarded, not trusted. The 40 grid does not divide
# 125, hence TWO variants (see module docstring):
WAY_BOLT_XS_INNER = (40.0, 80.0)         # splice-to-splice segment
WAY_BOLT_XS_OUTER = (35.0, 75.0)         # splice-to-pod segment -> global 160, 200
WAY_END_MARGIN = 20.0                    # the 250 mm way's own rule, kept

# Loose alignment key across each butt joint, seated in the base. Loose (a
# separate part, pockets in BOTH end faces) because rear segments are front
# segments rotated 180 -- a male tab would meet a male tab at x = 0.
KEY_POCKET_D = 5.0                       # pocket depth into each end face
KEY_W = 6.0                              # of a 12.0 base: 3.0 walls each side
KEY_H = 2.5                              # of a 5.0 base: 1.25 floor + roof
KEY_Z0 = 1.25                            # pocket floor above the ledge plane
KEY_FIT = 0.3                            # lateral/vertical clearance, total
KEY_L = 2 * KEY_POCKET_D - 0.4           # 9.6 axial in a 10.0 pocket pair

# --------------------------------------------------------------- the carriage
CAR_L = 200.0                            # X
# The plate has to COVER its own shoes or the outboard hook lands beyond the
# plate edge and prints as a loose sliver. Ledge centreline is at y = 71 and the
# shoe is 26.7 wide, so the plate must reach 84.4 -- it follows the waist box's
# 164 mm footprint, not the 160 mm chassis. Caught by a solids count of 3.
CAR_W = 170.0                            # Y
CAR_T = 8.0                              # plate thickness
CAR_Z0 = LEDGE_TOP + WAY_H               # 84.0, carriage underside
SHOE_CLEAR = 0.35                        # per-face running clearance on the dovetail
SHOE_WALL = 5.0                          # meat outboard of the female channel
DRIVE_HOLE_D = 24.0                      # the one hole; both modules pass through
DRIVE_BOLT_PCD = 38.0                    # four M4 that BOTH modules share
DRIVE_BOLT_N = 4

# Carriage split joint (2026-09-07, A1 mini). Split plane x = 0 -- the plate's
# own mirror plane, and the chassis mid-splice. All hardware opens DOWNWARD so
# the plate top stays flush under the waist box; in the print pose (plate-top
# on the bed) downward is upward and everything prints unsupported.
CAR_JB_Y = 50.0        # +/- bolt-boss stations. The z 78..84 band under the
                       # plate is empty at |y| <= 56: ways start at y = 63,
                       # ledge tops at z = 72, rack top z = 64, and the chest
                       # verticals (y = +/-60) sit at x = +/-49.5 while the
                       # boss stays inside |x| <= 17.5.
CAR_JB_L = 35.0        # boss length in X (17.5 each side of the joint)
CAR_JB_W = 12.0        # boss width in Y
CAR_JB_H = 6.0         # boss depth below the plate underside
CAR_JBOLT_Z = -2.5     # M4 axis, below the plate underside
CAR_JBOLT_HEAD_D = 9.0     # socket head 7.0 + room
CAR_JBOLT_HEAD_X = 12.0    # head under-face plane |x| -> 23.7 mm grip, M4 x 30
CAR_JNUT_AF = 7.3          # M4 hex nut 7.0 A/F + fit
CAR_JNUT_T = 3.4           # 3.2 thick + fit
CAR_JNUT_X = 13.4          # nut slot centre |x|
CAR_DOWEL_D = 3.2          # 3 mm steel dowel, slip fit + glue
CAR_DOWEL_L = 20.0         # 10 mm into each half
CAR_DOWEL_Z = 4.0          # mid-plate; bores stop 2.3 mm above the channel roof
CAR_DOWEL_Y = (-75.0, -30.0, 45.0, 75.0)   # +/-75 register the shoe channels;
                       # 45 clears the drive bolt at y 35.9..40.3 by 3.1 mm and
                       # the nut slot at y 46.35..53.65 in Z (bore z 2.4..5.6
                       # vs slot top z = +1.0)

# ------------------------------------------------------------------- the rack
# Module 3, 20 deg pressure angle. Coarse enough that a 0.4 mm nozzle renders a
# 2.5 mm tooth tip in six lines, fine enough that one tooth of settle is 9.4 mm.
MOD = 3.0
PRESSURE_DEG = 20.0
RACK_PITCH = math.pi * MOD               # 9.4248
RACK_L = 200.0
RACK_N = int(RACK_L // RACK_PITCH)       # 21 teeth
RACK_WEB_Y0 = -8.0                       # web spans y -8.0 .. +0.25 (the root line)
RACK_PITCH_Y = 4.0                       # pitch line
RACK_ROOT_Y = RACK_PITCH_Y - 1.25 * MOD  # 0.25
RACK_TIP_Y = RACK_PITCH_Y + MOD          # 7.0
RACK_FACE_Z0 = 46.0                      # teeth occupy z 46..58, clear of the ledges
RACK_FACE_H = 12.0
RACK_FOOT_T = 5.0                        # flange bolting to the chassis floor
RACK_TOP_Z = RACK_FACE_Z0 + RACK_FACE_H + 6.0        # 64.0, below the ledge underside

# ------------------------------------------------------- the servo+ pinion
PINION_Z = 13                            # teeth
PINION_SHIFT = 0.25                      # profile shift; z=13 undercuts below 17
PINION_FACE = 12.0
PINION_BORE = 8.0                        # 608 stub shaft, as every other joint
# Rack-and-pinion centre distance grows by x*m when the pinion is shifted. A
# theoretically exact mesh has ZERO backlash, which on an FDM gear means it
# binds: opening the centre distance by d buys 2*d*tan(alpha) of backlash.
PINION_BACKLASH = 0.30
PINION_AXIS_Y = (RACK_PITCH_Y + MOD * PINION_Z / 2.0 + PINION_SHIFT * MOD
                 + PINION_BACKLASH / (2 * math.tan(math.radians(PRESSURE_DEG))))

# ---------------------------------------------------------- the servo- pawl
PAWL_ENGAGE = 3.0                        # how deep the stub sits in a tooth space
LEAF_T = 3.8
LEAF_W = 16.0
# The leaf length is NOT a free choice: the root block bolts to the carriage top
# and the stub has to land centred on the rack's 12 mm tooth face. Picking a
# round 50 mm instead puts a third of the stub hanging off the end of the rack.
PAWL_ROOT_Z = CAR_Z0 + CAR_T                         # 92.0
RACK_FACE_MID = RACK_FACE_Z0 + RACK_FACE_H / 2.0     # 52.0
LEAF_L = PAWL_ROOT_Z - RACK_FACE_MID + LEAF_W / 2.0  # 48.0
# Seating offset: the stub base plane must coincide with the rack tip line.
PAWL_Y_SEAT = RACK_TIP_Y + LEAF_T
# The lever is rooted at the LEAF TIP, 50 mm below the carriage, and has to
# finish clear ABOVE the deck where a hand can reach it -- so it is longer than
# the leaf by the grab height, not shorter.
PAWL_RELEASE_L = LEAF_L + 35.0           # the lever that makes this build viable

E_PETG = 1700.0                          # MPa
SIGMA_PETG = 25.0                        # MPa allowable, house figure


# ============================================================== tooth geometry
def _inv(a):
    return math.tan(a) - a


def _rack_tooth_poly():
    """One rack tooth as a closed polygon in the XY plane, extruded along Z.

    Straight flanks at the pressure angle -- the rack is the one member of a
    gear pair whose correct profile is a straight line, which is also the one
    profile an FDM printer renders without argument.
    """
    a = math.radians(PRESSURE_DEG)
    half_p = RACK_PITCH / 4.0
    tip = half_p - MOD * math.tan(a)
    root = half_p + 1.25 * MOD * math.tan(a)
    pts = [
        Vector(-root, RACK_ROOT_Y, 0),
        Vector(-tip, RACK_TIP_Y, 0),
        Vector(tip, RACK_TIP_Y, 0),
        Vector(root, RACK_ROOT_Y, 0),
    ]
    return Solid.extrude(Face(Wire.make_polygon(pts, close=True)),
                         Vector(0, 0, RACK_FACE_H))


def _pinion_tooth_poly(steps=14):
    """One involute tooth as a closed polygon in the XY plane, extruded in Z.

    Tip-shortened: the addendum stays at m even though the profile is shifted
    +0.25. Shifting without shortening would take the tip from 2.6 mm down to
    1.5 mm, which is four extrusions and a tooth that shears.
    """
    a = math.radians(PRESSURE_DEG)
    r = MOD * PINION_Z / 2.0
    rb = r * math.cos(a)
    ra = r + MOD                                     # tip-shortened
    rf = r - MOD * (1.25 - PINION_SHIFT)
    psi = math.pi / (2 * PINION_Z) + 2 * PINION_SHIFT * math.tan(a) / PINION_Z

    def phi(rr):
        return psi + _inv(a) - _inv(math.acos(min(1.0, rb / rr)))

    r0 = max(rf, rb)
    flank = [(r0 + (ra - r0) * i / steps) for i in range(steps + 1)]
    right = [Vector(rr * math.cos(phi(rr)), rr * math.sin(phi(rr)), 0)
             for rr in flank]
    left = [Vector(v.X, -v.Y, 0) for v in reversed(right)]

    # Below the base circle the involute does not exist; drop radially to the
    # root so the polygon closes on real geometry instead of an extrapolation.
    p0 = phi(r0)
    skirt = [Vector(rf * math.cos(p0), -rf * math.sin(p0), 0),
             Vector(rf * math.cos(p0), rf * math.sin(p0), 0)]

    return Solid.extrude(Face(Wire.make_polygon(skirt + right + left, close=True)),
                         Vector(0, 0, PINION_FACE))


# ================================================================ the parts
def create_way(bolt_xs):
    """One dovetail way SEGMENT, 125 mm. Two variants from this one code path
    (inner / outer), differing ONLY in where the ledge bolts fall -- the
    profile cannot diverge between them because it is never restated.

    Bolts to the chassis ledge's existing 40 mm M4 pilot pattern, so the rail is
    a retrofit: the ledge was drawn before the rail existed and does not change.
    Both end faces carry a key pocket; the joint key is a separate loose part.
    """
    for x in bolt_xs:
        assert WAY_END_MARGIN <= x <= WAY_SEG_L - WAY_END_MARGIN, (
            f"way bolt at local {x} is inside the {WAY_END_MARGIN} mm end margin")
    with BuildPart() as part:
        Box(WAY_SEG_L, WAY_BASE_W, WAY_BASE_H,
            align=(Align.MIN, Align.CENTER, Align.MIN))

        # neck -> flare -> land, as one swept trapezoid pair
        z = WAY_BASE_H
        Box(WAY_SEG_L, WAY_NECK_W, WAY_FLARE_H,
            align=(Align.MIN, Align.CENTER, Align.MIN)).locate(Location((0, 0, z)))
        with Locations((0, 0, z)):
            pts = [Vector(0, -WAY_NECK_W / 2, 0), Vector(0, WAY_NECK_W / 2, 0),
                   Vector(0, WAY_HEAD_W / 2, WAY_FLARE_H),
                   Vector(0, -WAY_HEAD_W / 2, WAY_FLARE_H)]
            add(Solid.extrude(Face(Wire.make_polygon(pts, close=True)),
                              Vector(WAY_SEG_L, 0, 0)))
        with Locations((0, 0, z + WAY_FLARE_H)):
            Box(WAY_SEG_L, WAY_HEAD_W, WAY_LAND_H,
                align=(Align.MIN, Align.CENTER, Align.MIN))

        # ledge bolts
        for x in bolt_xs:
            with Locations((x, 0, 0)):
                Cylinder(radius=M4_CLEAR / 2, height=WAY_H * 3,
                         align=(Align.CENTER, Align.CENTER, Align.MIN),
                         mode=Mode.SUBTRACT)
                # counterbore so the head cannot foul the shoe
                Cylinder(radius=8.0 / 2, height=WAY_BASE_H - 1.5,
                         align=(Align.CENTER, Align.CENTER, Align.MIN),
                         mode=Mode.SUBTRACT)

        # key pockets, BOTH end faces (rotation-proof; an unused pocket at the
        # rail's outer tip is 0.07 g of air)
        for x0 in (0.0, WAY_SEG_L - KEY_POCKET_D):
            with Locations((x0, 0, KEY_Z0)):
                Box(KEY_POCKET_D, KEY_W, KEY_H,
                    align=(Align.MIN, Align.CENTER, Align.MIN),
                    mode=Mode.SUBTRACT)
    return part.part


def create_way_key():
    """The loose joint key. Registers Y and Z across a way butt joint; the
    ledge bolts do the clamping. Prints flat, as modeled."""
    with BuildPart() as part:
        Box(KEY_L, KEY_W - KEY_FIT, KEY_H - KEY_FIT,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
    return part.part


def way_run(inner, outer):
    """The full segmented rail run, placed in robot coordinates: 4 segments per
    side, rear pair ROTATED 180 exactly like the rear chassis half they bolt to
    (the old translated placement missed every rear ledge pilot by 10 mm).

    Returns the 8 placed solids. Asserts, from MEASURED bounding boxes: the run
    tiles -250..+250 with interior joints exactly on CHASSIS_SPLICE_X, and
    every ledge bolt lands on the chassis pilot grid.
    """
    grid = set()
    for x in range(40, int(2 * WAY_SEG_L) - 20, 40):   # chassis.py:221's law
        grid.add(float(x))
        grid.add(float(-x))

    placed, holes = [], []
    for sy in (1, -1):
        y, z = sy * LEDGE_Y, LEDGE_TOP
        for seg, bolt_xs, x0, rot in (
                (inner, WAY_BOLT_XS_INNER, 0.0, False),
                (outer, WAY_BOLT_XS_OUTER, WAY_SEG_L, False),
                (inner, WAY_BOLT_XS_INNER, 0.0, True),
                (outer, WAY_BOLT_XS_OUTER, -WAY_SEG_L, True)):
            s = seg.rotate(Axis.Z, 180) if rot else copy.copy(seg)
            placed.append(s.moved(Location((x0, y, z))))
            holes += [x0 + (-bx if rot else bx) for bx in bolt_xs]

        # measured tiling: spans meet exactly on the splice planes
        spans = sorted((round(s.bounding_box().min.X, 6),
                        round(s.bounding_box().max.X, 6))
                       for s in placed[-4:])
        joints = []
        for (a0, a1), (b0, b1) in zip(spans, spans[1:]):
            assert abs(a1 - b0) < 1e-6, (
                f"way segments do not tile: gap/overlap {a1} vs {b0}")
            joints.append(a1)
        assert joints == sorted(CHASSIS_SPLICE_X), (
            f"way joints {joints} are not the chassis splice planes "
            f"{sorted(CHASSIS_SPLICE_X)}")
        assert (spans[0][0], spans[-1][1]) == (-2 * WAY_SEG_L, 2 * WAY_SEG_L)

    off_grid = [h for h in holes if h not in grid]
    assert not off_grid, (
        f"way bolts at {off_grid} miss the chassis ledge pilot grid "
        f"(+/-40..+/-200 step 40) -- the exact mistake the old rear ways had")
    return placed


def keys_placed(key):
    """The six joint keys, in robot coordinates, centred on each splice plane."""
    return [copy.copy(key).moved(Location((xj, sy * LEDGE_Y, LEDGE_TOP + KEY_Z0)))
            for sy in (1, -1) for xj in CHASSIS_SPLICE_X]


def create_carriage():
    """The plate the waist box bolts onto. Unbroken -- one hole, no slot.

    Both drive modules hang through the same hole on the same four bolts, which
    is what makes servo+ and servo- a fit choice rather than two robots.

    SINCE 2026-09-07 THIS IS THE REFERENCE MONOLITH, NOT A PRINTED PART: it
    does not fit the A1 mini. The printed parts are the two halves cut FROM it
    by create_carriage_halves(), and main() asserts the assembled halves match
    this reference's envelope and slide interface exactly. Keeping the monolith
    as the single geometry authority is what makes that assert meaningful.
    """
    ch_w = WAY_HEAD_W + 2 * SHOE_CLEAR
    ch_n = WAY_NECK_W + 2 * SHOE_CLEAR
    ch_h = WAY_FLARE_H + WAY_LAND_H + SHOE_CLEAR

    with BuildPart() as part:
        Box(CAR_L, CAR_W, CAR_T, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # shoe rails hanging down, one per way
        for sy in (-1, 1):
            with Locations((0, sy * LEDGE_Y, 0)):
                Box(CAR_L, ch_w + 2 * SHOE_WALL, ch_h,
                    align=(Align.CENTER, Align.CENTER, Align.MAX))

        # Female dovetail cut into each shoe. RETRACTION 2026-09-07: this cut
        # was originally drawn "wide at the BOTTOM ... prints unsupported" --
        # reasoning about the print pose in the ROBOT frame, when the carriage
        # prints FLIPPED. Drawn that way the void was wide where the way is
        # narrow and narrow where the way's 16 mm head is: the carriage
        # interfered with its own ways by 2884 mm3 PER SHOE-WAY PAIR (z
        # 79.1..84, the head band) and could never have been assembled, let
        # alone slid. Nothing caught it for a month because no carriage-vs-way
        # swept assert existed -- a dovetail that does not mate looks exactly
        # like one that does, same as the gear lesson at the top of the mesh
        # section. The sweep added with the A1-mini segmentation caught it at
        # its first run.
        #
        # The profile now MIRRORS the male way + SHOE_CLEAR per face:
        #   z -7.35..-7   relief, half 6.35 -- the shoe lip dips 0.35 below
        #                 the base top, so it must clear the 12 mm base
        #   z -7..-3      45 deg flank, half 4.35 -> 8.35 (male 4 -> 8, so a
        #                 constant 0.35 horizontal running clearance)
        #   z -3..+0.1    half 8.35 over the 16 mm land, cut 0.1 into the
        #                 plate exactly as before
        # The hook lip (y 4.35..6.35 under the flare) is what retains the
        # carriage. In the print pose (flipped) the flank overhangs at the
        # same 45 deg the way climbs and self-supports -- the claim the old
        # comment made, now true in the frame the printer sees.
        ch_b = WAY_BASE_W + 2 * SHOE_CLEAR
        z_lip = -(WAY_FLARE_H + WAY_LAND_H)          # -7.0, base top plane
        z_head = -WAY_LAND_H                         # -3.0, flare-top plane
        for sy in (-1, 1):
            y = sy * LEDGE_Y
            pts = [Vector(0, y - ch_b / 2, -ch_h), Vector(0, y + ch_b / 2, -ch_h),
                   Vector(0, y + ch_b / 2, z_lip), Vector(0, y + ch_n / 2, z_lip),
                   Vector(0, y + ch_w / 2, z_head), Vector(0, y + ch_w / 2, 0.1),
                   Vector(0, y - ch_w / 2, 0.1), Vector(0, y - ch_w / 2, z_head),
                   Vector(0, y - ch_n / 2, z_lip), Vector(0, y - ch_b / 2, z_lip)]
            with Locations((-CAR_L / 2, 0, 0)):
                add(Solid.extrude(Face(Wire.make_polygon(pts, close=True)),
                                  Vector(CAR_L, 0, 0)), mode=Mode.SUBTRACT)

        # the one hole, and the shared four-bolt module pattern around it
        with Locations((0, PINION_AXIS_Y, 0)):
            Cylinder(radius=DRIVE_HOLE_D / 2, height=CAR_T * 3,
                     align=(Align.CENTER, Align.CENTER, Align.MIN),
                     mode=Mode.SUBTRACT)
        for i in range(DRIVE_BOLT_N):
            th = 2 * math.pi * i / DRIVE_BOLT_N + math.pi / 4
            with Locations((DRIVE_BOLT_PCD / 2 * math.cos(th),
                            PINION_AXIS_Y + DRIVE_BOLT_PCD / 2 * math.sin(th), 0)):
                Cylinder(radius=M4_CLEAR / 2, height=CAR_T * 3,
                         align=(Align.CENTER, Align.CENTER, Align.MIN),
                         mode=Mode.SUBTRACT)

        # Waist-box bolt pattern, on the box's own deck screw lines. Installed
        # rotated -90 the box is 122 deep fore-aft and 164 wide across, so the
        # long pair runs in Y. Before that was understood these were at
        # (+/-70 X, +/-50 Y) -- 9 mm outside the box in X, thin air.
        for sx in (-1, 1):
            for sy in (-1, 1):
                with Locations((sx * 45.0, sy * 70.0, 0)):
                    Cylinder(radius=M4_CLEAR / 2, height=CAR_T * 3,
                             align=(Align.CENTER, Align.CENTER, Align.MIN),
                             mode=Mode.SUBTRACT)

        # Lightening windows. A solid 200x170x8 plate is 259 g -- half the whole
        # rail -- and it is doing almost nothing: the only job is carrying four
        # waist-box bolts into four shoe lines. Leave a 22 mm perimeter frame, a
        # spine over each shoe, and a cross rib through the drive station.
        for sx in (-1, 1):
            for sy in (-1, 1):
                with Locations((sx * 55.0, sy * 42.0, -1.0)):
                    Box(66.0, 34.0, CAR_T + 4.0,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                        mode=Mode.SUBTRACT)
    return part.part


def _joint_cyl(r, h, x, y, z):
    """A cylinder whose axis runs along X -- every cross-joint bore is one."""
    return Cylinder(radius=r, height=h, rotation=(0, 90, 0)).moved(
        Location((x, y, z)))


def create_carriage_halves():
    """The two printed carriage halves, cut FROM the reference monolith at the
    x = 0 mirror plane, then given the joint hardware. Returns (aft, fwd).

    They are two DISTINCT parts: the drive hole at y = +24.66 kills every
    symmetry that could let one STL print twice, and the head-pocket / nut-slot
    alternation differs between them anyway. Both are partchecked.

    Hardware (see the constants block for the WHY of every station):
      * two M4 x 30 in under-plate bosses at y = +/-CAR_JB_Y; +y bolt heads
        aft, -y heads fwd; nut drops into a downward-opening slot
      * four 3 mm dowels in-plate at CAR_DOWEL_Y, 10 mm into each face
    The joint adds NOTHING above the plate top and NOTHING below z = -6, so
    the slide envelope and the waist-box seat are untouched -- asserted in
    main(), not just claimed here.
    """
    full = create_carriage()
    halves = {}
    for side, tag in ((-1, "aft"), (1, "fwd")):
        keep = Box(CAR_L / 2 + 5.0, CAR_W + 20.0, 80.0,
                   align=(Align.MAX if side < 0 else Align.MIN,
                          Align.CENTER, Align.CENTER))
        h = full & keep

        # bolt bosses under the plate
        for sy in (-1, 1):
            h = h + Box(CAR_JB_L / 2.0, CAR_JB_W, CAR_JB_H,
                        align=(Align.MAX if side < 0 else Align.MIN,
                               Align.CENTER, Align.MAX)).moved(
                Location((0.0, sy * CAR_JB_Y, 0.0)))

        # cross-bolt bores + head pocket OR nut slot, alternating direction
        for sy in (-1, 1):
            yb = sy * CAR_JB_Y
            head_side = -1 if sy > 0 else 1
            h = h - _joint_cyl(M4_CLEAR / 2, 44.0, 0.0, yb, CAR_JBOLT_Z)
            if side == head_side:
                x0, x1 = CAR_JBOLT_HEAD_X, CAR_JB_L / 2.0 + 0.2
                h = h - _joint_cyl(CAR_JBOLT_HEAD_D / 2, x1 - x0,
                                   head_side * (x0 + x1) / 2.0, yb, CAR_JBOLT_Z)
            else:
                h = h - Box(CAR_JNUT_T, CAR_JNUT_AF, CAR_JB_H + 1.2,
                            align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(
                    Location((side * CAR_JNUT_X, yb, -CAR_JB_H - 0.2)))

        # dowel bores, both halves, 10 mm each side of the joint face
        for yd in CAR_DOWEL_Y:
            h = h - _joint_cyl(CAR_DOWEL_D / 2, CAR_DOWEL_L, 0.0, yd, CAR_DOWEL_Z)

        halves[tag] = h
    return halves["aft"], halves["fwd"]


def create_rack():
    """Fixed rack, standing in the chassis well on a full-length foot.

    Teeth face +Y so the drive module engages from the side; nothing about this
    part knows whether a pinion or a pawl is on the other side of it.
    """
    with BuildPart() as part:
        # web
        with Locations((0, (RACK_WEB_Y0 + RACK_ROOT_Y) / 2, CHASSIS_FLOOR_T)):
            Box(RACK_L, RACK_ROOT_Y - RACK_WEB_Y0, RACK_TOP_Z - CHASSIS_FLOOR_T,
                align=(Align.CENTER, Align.CENTER, Align.MIN))

        # teeth, centred on the rack so travel is symmetric about x = 0
        x0 = -(RACK_N - 1) * RACK_PITCH / 2.0
        for n in range(RACK_N):
            add(_rack_tooth_poly().moved(
                Location((x0 + n * RACK_PITCH, 0, RACK_FACE_Z0))))

        # foot flange down the centreline, between the chassis battery rails
        with Locations((0, (RACK_WEB_Y0 + RACK_ROOT_Y) / 2, CHASSIS_FLOOR_T)):
            Box(RACK_L, 34.0, RACK_FOOT_T,
                align=(Align.CENTER, Align.CENTER, Align.MIN))
        for sx in (-1, 1):
            for sy in (-1, 1):
                with Locations((sx * 80.0,
                                (RACK_WEB_Y0 + RACK_ROOT_Y) / 2 + sy * 12.0,
                                CHASSIS_FLOOR_T)):
                    Cylinder(radius=M4_CLEAR / 2, height=RACK_FOOT_T * 3,
                             align=(Align.CENTER, Align.CENTER, Align.MIN),
                             mode=Mode.SUBTRACT)

        # Lighten the web: it is a shear panel, so triangulate rather than
        # drill -- round holes in a shear web cut the diagonal load path.
        #
        # Sized off the RENDER, not the mass target: at 24 mm the diamonds'
        # top corners reached z = 46, which is the tooth root plane, leaving
        # the teeth standing on nothing. partcheck still passed it (min wall
        # 2.80 mm) because a thin ligament is not a broken one. Keep a real
        # 5 mm band of solid web under the tooth root.
        DIA = 22.0
        band_z = (CHASSIS_FLOOR_T + RACK_FACE_Z0) / 2.0
        assert band_z + DIA * math.sqrt(2) / 2 < RACK_FACE_Z0 - 5.0, (
            "lightening diamonds undercut the tooth roots")
        for n in range(-2, 3):
            with Locations((n * 40.0, 0, band_z)):
                Box(DIA, 40.0, DIA, rotation=(0, 45, 0), mode=Mode.SUBTRACT)
    return part.part


def create_pinion():
    """servo+ only. Involute spur, 13T module 3, +0.25 shift, tip-shortened."""
    r = MOD * PINION_Z / 2.0
    rf = r - MOD * (1.25 - PINION_SHIFT)
    with BuildPart() as part:
        Cylinder(radius=rf, height=PINION_FACE, align=(Align.CENTER,) * 3)
        for i in range(PINION_Z):
            add(_pinion_tooth_poly().moved(
                Location((0, 0, -PINION_FACE / 2))
            ).rotate(Axis.Z, 360.0 * i / PINION_Z))
        Cylinder(radius=PINION_BORE / 2, height=PINION_FACE * 3,
                 align=(Align.CENTER,) * 3, mode=Mode.SUBTRACT)
        # grub screw onto the shaft flat
        with Locations((0, 0, 0)):
            Cylinder(radius=M3_PILOT / 2, height=rf * 2,
                     rotation=(90, 0, 0), mode=Mode.SUBTRACT)
    return part.part


def create_pawl():
    """servo- only. Two-way detent on the rack's own 20 deg flanks.

    The leaf bends in Y. Printed flat, that bending happens ALONG extrusions
    rather than across layer lines -- the single orientation rule that decides
    whether a printed spring is a spring or a hinge that breaks once.

    The RELEASE LEVER is what makes the hand-driven rail viable at all. Without
    it the arms must overcome the full detent to slide; with it they unseat the
    pawl first and then push against friction only. See hand_load.py.
    """
    with BuildPart() as part:
        # root block, bolts to the carriage on the shared 4-bolt pattern
        Box(46.0, 14.0, CAR_T + 6.0, align=(Align.CENTER, Align.MAX, Align.MIN))
        for sx in (-1, 1):
            with Locations((sx * DRIVE_BOLT_PCD / 2 * math.cos(math.pi / 4), -7.0, 0)):
                Cylinder(radius=M4_CLEAR / 2, height=(CAR_T + 6.0) * 3,
                         align=(Align.CENTER, Align.CENTER, Align.MIN),
                         mode=Mode.SUBTRACT)

        # leaf reaching DOWN toward the rack
        with Locations((0, -LEAF_T, -LEAF_L)):
            Box(LEAF_W, LEAF_T, LEAF_L, align=(Align.CENTER, Align.MIN, Align.MIN))

        # Detent stub: sits in a tooth space, bears on both flanks. Its height
        # is the RACK'S face, not the leaf's width -- a stub taller than the
        # teeth it seats in overhangs the rack and lands on the web.
        a = math.radians(PRESSURE_DEG)
        half = RACK_PITCH / 4.0 - (MOD - PAWL_ENGAGE) * math.tan(a) - 0.25
        pts = [Vector(-half - PAWL_ENGAGE * math.tan(a), 0, 0),
               Vector(-half, -PAWL_ENGAGE, 0),
               Vector(half, -PAWL_ENGAGE, 0),
               Vector(half + PAWL_ENGAGE * math.tan(a), 0, 0)]
        with Locations((0, -LEAF_T, -LEAF_L + (LEAF_W - RACK_FACE_H) / 2.0)):
            add(Solid.extrude(Face(Wire.make_polygon(pts, close=True)),
                              Vector(0, 0, RACK_FACE_H)))

        # Anchor for the release lever, which is a SEPARATE part -- see
        # create_lever() for why. One M3 through the leaf tip.
        with Locations((0, -LEAF_T / 2, -LEAF_L + LEAF_W / 2)):
            Cylinder(radius=M3_CLEAR / 2, height=LEAF_T * 4,
                     rotation=(90, 0, 0), mode=Mode.SUBTRACT)
    return part.part


def create_lever():
    """The release lever -- a SEPARATE part, bolted to the leaf tip.

    Integral looked obvious and was wrong three ways. Rooted on the stub side it
    swept straight through the rack (460 mm3). Moved to the back of the leaf it
    put features on BOTH faces, and then no orientation prints cleanly: the pawl
    ends up standing on its leaf tip with 109 mm2 of bed contact, which shears
    off, or lying with the lever below the bed plane.

    Split out, the pawl becomes a flat L that prints leaf-down with 1412 mm2 of
    contact -- and that is the orientation the SPRING needs anyway, because the
    leaf's bending stress then runs along extrusions instead of across layers.

    Two more things fall out for free: the lever is the only part whose length
    depends on where the waist box finally sits, so the pawl stops being
    reprinted every time the box moves; and it is the only part a hand touches,
    so a different filament costs nothing.
    """
    with BuildPart() as part:
        # foot, clamping the back of the leaf tip
        Box(LEAF_W, 4.0, LEAF_W, align=(Align.CENTER, Align.MIN, Align.MIN))
        with Locations((0, 0, LEAF_W / 2)):
            Cylinder(radius=M3_CLEAR / 2, height=12.0, rotation=(90, 0, 0),
                     mode=Mode.SUBTRACT)
        # post up past the deck
        with Locations((0, 0, 0)):
            Box(LEAF_W, 4.0, PAWL_RELEASE_L, align=(Align.CENTER, Align.MIN, Align.MIN))
        # paddle -- extends SIDEWAYS, not rearward, so the whole part stays in
        # one 4 mm slab and prints flat with no overhang anywhere.
        with Locations((0, 0, PAWL_RELEASE_L - 3.0)):
            Box(LEAF_W + 22.0, 4.0, 12.0, align=(Align.CENTER, Align.MIN, Align.MIN))
    return part.part


# ============================================================ meshing, checked
# A gear that does not mesh looks exactly like a gear that does. The calf sat
# 1.62 cm3 inside the thigh and passed every single-part check; only a SWEPT
# interference test found it. Same discipline here: roll the pinion through a
# full tooth and measure the overlap at every step.
def mesh_check(rack, pinion, steps=9, offsets=24, verbose=True):
    """Roll the pinion one full tooth along the rack; return the worst overlap.

    A rack-and-pinion rolls without slip, so a rotation of dtheta MUST come with
    a translation of r*dtheta. Rotating without translating (or vice versa) is
    the classic way to draw a mesh that cannot turn.
    """
    r = MOD * PINION_Z / 2.0
    z_mid = RACK_FACE_Z0 + RACK_FACE_H / 2.0
    tooth_deg = 360.0 / PINION_Z

    def overlap(phase, phi0):
        # ROLLING WITHOUT SLIP: with the rack below the pinion centre, the
        # contact velocity is vx + omega*r, so vx = -omega*r. Translating +x
        # therefore needs a NEGATIVE rotation. Getting this sign backwards
        # grinds the teeth through each other and still looks like a gear --
        # it cost 364.6 mm3 of overlap before the sweep caught it.
        p = pinion.rotate(Axis.Z, phi0 - phase * tooth_deg).moved(
            Location((phase * RACK_PITCH, PINION_AXIS_Y, z_mid)))
        try:
            return (p & rack).volume
        except Exception:
            return float("inf")

    # Find a timing phase at which the teeth interleave. Scored over the WHOLE
    # sweep, not just at station 0 -- a phase can look clean at one station and
    # collide at the next.
    coarse = range(0, steps + 1, max(1, steps // 3))
    best, best_v = 0.0, float("inf")
    for i in range(offsets):
        phi0 = tooth_deg * i / offsets
        v = max(overlap(s / steps, phi0) for s in coarse)
        if v < best_v:
            best, best_v = phi0, v

    worst = max(overlap(s / steps, best) for s in range(steps + 1))
    if verbose:
        print(f"\nmesh sweep, {steps + 1} stations over one {tooth_deg:.2f} deg tooth:")
        print(f"  timing phase   {best:.2f} deg")
        print(f"  worst overlap  {worst:.4f} mm3   "
              f"{'OK' if worst < 1.0 else 'INTERFERES'}")
    return worst


def pawl_seated(pawl, x=None):
    """Place the pawl in a tooth SPACE, in robot coordinates."""
    if x is None:                       # centre of the space next to tooth 0
        x = -(RACK_N - 1) * RACK_PITCH / 2.0 + RACK_PITCH / 2.0
    return pawl.moved(Location((x, PAWL_Y_SEAT, PAWL_ROOT_Z)))


def pawl_check(rack, pawl, verbose=True):
    """Seated in a space the stub must touch NOTHING -- it is a detent, not a peg.

    The clearance is the whole point: 0.25 mm per flank means the stub finds its
    seat under spring load rather than being pressed into an interference fit
    that would need the arms to break it out.
    """
    seated = pawl_seated(pawl)
    try:
        cut = (seated & rack).volume
    except Exception:
        cut = float("inf")
    # Measure the STUB, not the part. The bounding box is dominated by the
    # release paddle, so reading reach off bb.min.Y reports the lever's tip and
    # calls a correct detent 13 mm deep.
    tip_y = PAWL_Y_SEAT - LEAF_T - PAWL_ENGAGE
    z0 = PAWL_ROOT_Z - LEAF_L + (LEAF_W - RACK_FACE_H) / 2.0
    depth = RACK_TIP_Y - tip_y
    z_ok = (RACK_FACE_Z0 - 0.01 <= z0
            and z0 + RACK_FACE_H <= RACK_FACE_Z0 + RACK_FACE_H + 0.01)
    if verbose:
        print(f"\npawl seated in a tooth space:")
        print(f"  stub tip       y = {tip_y:.2f}  (rack tips {RACK_TIP_Y:.2f}, "
              f"roots {RACK_ROOT_Y:.2f})")
        print(f"  engagement     {depth:.2f} mm deep  "
              f"{'OK' if 0.5 < depth <= MOD * 2.25 else 'WRONG'}")
        print(f"  stub z-span    {z0:.1f}..{z0 + RACK_FACE_H:.1f} vs rack face "
              f"{RACK_FACE_Z0:.0f}..{RACK_FACE_Z0 + RACK_FACE_H:.0f}  "
              f"{'OK' if z_ok else 'HANGS OFF THE RACK'}")
        print(f"  overlap        {cut:.3f} mm3  "
              f"{'OK -- seats on clearance' if cut < 1.0 else 'JAMMED'}")
    return cut


# ==================================================================== reporting
def _report(name, shape, extra=""):
    bb = shape.bounding_box()
    print(f"{name:16s} {bb.size.X:6.1f} x {bb.size.Y:6.1f} x {bb.size.Z:6.1f} mm  "
          f"{shape.volume / 1000:7.1f} cm3  PETG {shape.volume / 1000 * 0.953:6.1f} g"
          f"  solids {len(shape.solids())}{extra}")


def main():
    out = Path(__file__).parent / "output"
    out.mkdir(exist_ok=True)

    car_aft, car_fwd = create_carriage_halves()
    parts = {
        "rail_way_inner": create_way(WAY_BOLT_XS_INNER),
        "rail_way_outer": create_way(WAY_BOLT_XS_OUTER),
        "rail_way_key": create_way_key(),
        "rail_carriage_half_aft": car_aft,
        "rail_carriage_half_fwd": car_fwd,
        "rail_rack": create_rack(),
        "rail_pinion": create_pinion(),
        "rail_pawl": create_pawl(),
        "rail_lever": create_lever(),
    }
    # The assembled carriage (both halves fused, no hardware) keeps the old
    # rail_carriage.step name because assembly_centaur/marks/mjcf_export place
    # that file and its envelope is UNCHANGED. rail_way.step is gone -- the
    # 250 mm part is retired, and its consumers must move to the segmented run
    # (loud breakage beats silently assembling a part that no longer exists).
    car_asm = car_aft + car_fwd
    for stale in ("rail_way.step", "rail_way.stl", "rail_carriage_print.step"):
        p = out / stale
        if p.exists():
            p.unlink()
            print(f"removed stale {stale}")

    # Print orientation, where it differs from the robot frame. The STEP stays
    # in robot coordinates so the assembly can place it; the *_print.step is
    # what the slicer and partcheck see. Keeping both is the only way a
    # printability grade means anything -- graded in the wrong pose the carriage
    # reads 24% support and the pawl reads 109 mm2 of bed contact.
    PRINT_ROT = {
        "rail_carriage_half_aft": (Axis.X, 180.0),  # plate on the bed, shoes
                                            # and joint bosses UP: the female
                                            # dovetail opens upward at 45 deg
                                            # and self-supports; nut slots and
                                            # head pockets open upward too
        "rail_carriage_half_fwd": (Axis.X, 180.0),
        "rail_pawl": (Axis.X, -90.0),       # leaf FLAT: bending stress runs
                                            # along extrusions, not across layers
        "rail_lever": (Axis.X, -90.0),      # it is a 4 mm slab; stood on edge it
                                            # balances on 64 mm2
    }
    for n, s in parts.items():
        export_step(s, str(out / f"{n}.step"))
        p = s
        if n in PRINT_ROT:
            ax, deg = PRINT_ROT[n]
            p = s.rotate(ax, deg)
            bb = p.bounding_box()
            p = p.moved(Location((0, 0, -bb.min.Z)))
            export_step(p, str(out / f"{n}_print.step"))
        export_stl(p, str(out / f"{n}.stl"))
    export_step(car_asm, str(out / "rail_carriage.step"))
    export_stl(car_asm, str(out / "rail_carriage.stl"))

    qty = {"rail_way_inner": 4, "rail_way_outer": 4, "rail_way_key": 6,
           "rail_carriage_half_aft": 1, "rail_carriage_half_fwd": 1,
           "rail_rack": 1, "rail_pinion": 1, "rail_pawl": 1, "rail_lever": 1}
    print(f"travel {TRAVEL:.0f} mm   rack {RACK_N} teeth at module {MOD:.0f} "
          f"({RACK_PITCH:.3f} mm pitch)\n")
    for n, s in parts.items():
        _report(n, s, f"  x{qty[n]}")
        assert len(s.solids()) == 1, f"{n} is {len(s.solids())} solids, not 1"

    # ------------------------- A1 mini bed gate, in PRINT orientation
    # partcheck.py's own fits_bed still checks the H2C's 330x320x325 (stale);
    # this gate is the one that binds. Footprint = the print pose's X x Y;
    # a footprint too long for the 180 square may still go DIAGONALLY (the
    # 200 mm rack does, at ~165 mm across corners) -- but the 245 diagonal is
    # NOMINAL, so a diagonal placement must clear the bed by 5 mm, never
    # design AT the number.
    def fits_a1(sx, sy, sz):
        if sz > BED_Z:
            return False
        if (sx <= BED_X and sy <= BED_Y) or (sx <= BED_Y and sy <= BED_X):
            return True
        for deg in range(1, 90):
            t = math.radians(deg)
            if (sx * math.cos(t) + sy * math.sin(t) <= BED_X - 5.0
                    and sx * math.sin(t) + sy * math.cos(t) <= BED_Y - 5.0):
                return True
        return False

    for n in parts:
        s = parts[n]
        if n in PRINT_ROT:
            s = s.rotate(*PRINT_ROT[n])
        bb = s.bounding_box()
        assert fits_a1(bb.size.X, bb.size.Y, bb.size.Z), (
            f"{n} does not fit the A1 mini bed in its print pose: "
            f"{bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f}")

    shared = sum(parts[n].volume / 1000 * 0.953 * qty[n]
                 for n in ("rail_way_inner", "rail_way_outer", "rail_way_key",
                           "rail_carriage_half_aft", "rail_carriage_half_fwd",
                           "rail_rack"))
    g = lambda n: parts[n].volume / 1000 * 0.953
    print(f"\nshared structure   {shared:6.1f} g")
    print(f"  + servo+ module  {g('rail_pinion'):6.1f} g printed + 74.5 g servo "
          f"= {shared + g('rail_pinion') + 74.5:.1f} g")
    print(f"  + servo- module  {g('rail_pawl'):6.1f} g printed, no servo "
          f"+ {g('rail_lever'):.1f} g lever = {shared + g('rail_pawl') + g('rail_lever'):.1f} g")

    # --------------------- does the split carriage EQUAL the monolith?
    # The slide envelope is load-bearing for the extension-stowage study, so
    # "the interface geometry is identical" is asserted, not claimed. Probe
    # boxes around each dovetail channel: the joint hardware lives at
    # |y| <= 56 and z >= +2.4, so inside the probes the two solids must agree
    # to the last cubic micron.
    ref = create_carriage()
    assert (car_aft & car_fwd).volume < 1e-9, "carriage halves overlap each other"
    bb_r, bb_a = ref.bounding_box(), car_asm.bounding_box()
    for a, b in ((bb_r.min, bb_a.min), (bb_r.max, bb_a.max)):
        assert max(abs(a.X - b.X), abs(a.Y - b.Y), abs(a.Z - b.Z)) < 1e-6, (
            f"assembled carriage envelope moved: {a} vs {b}")
    print(f"\nsplit carriage vs reference monolith:")
    for sy in (-1, 1):
        probe = Box(CAR_L + 4.0, 26.0, 8.0,
                    align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(
            Location((0, sy * LEDGE_Y, -7.5)))
        v_ref = (ref & probe).volume
        v_asm = (car_asm & probe).volume
        print(f"  shoe channel y={sy * LEDGE_Y:+.0f}: monolith {v_ref:.3f} vs "
              f"halves {v_asm:.3f} mm3  d={abs(v_ref - v_asm):.2e}")
        assert abs(v_ref - v_asm) < 1e-3, (
            "the split changed the slide interface -- forbidden, the stowage "
            "study depends on it")
    d_vol = car_asm.volume - ref.volume
    print(f"  volume delta   {d_vol / 1000:+.2f} cm3 (bosses minus joint cuts)")

    # ------------- does the carriage SWEEP the segmented run cleanly?
    # The ways gained six butt joints and the carriage gained under-plate
    # bosses; the shoe crosses every joint and the bosses fly over the well.
    # Same discipline as the gear mesh: sweep it and MEASURE, in robot frame.
    run = way_run(parts["rail_way_inner"], parts["rail_way_outer"])
    run += keys_placed(parts["rail_way_key"])
    obstacle = run[0]
    for s in run[1:]:
        obstacle = obstacle + s
    worst_x, worst_v = 0.0, 0.0
    for xt in (-75.0, -50.0, -25.0, 0.0, 25.0, 50.0, 75.0,
               100.0, 125.0, 150.0, 167.0, 180.0):
        placed = copy.copy(car_asm).moved(Location((xt, 0, CAR_Z0)))
        v = (placed & obstacle).volume
        if v > worst_v:
            worst_x, worst_v = xt, v
    print(f"\ncarriage swept over segmented ways + keys, 12 stations "
          f"x = -75..180:")
    print(f"  worst overlap  {worst_v:.4f} mm3 at x = {worst_x:.0f}   "
          f"{'OK' if worst_v < 1e-3 else 'INTERFERES'}")
    assert worst_v < 1e-3, (
        f"carriage fouls the segmented way run: {worst_v:.3f} mm3 at "
        f"x = {worst_x}")

    # -------------------------------------------- does either module MESH?
    worst = mesh_check(parts["rail_rack"], parts["rail_pinion"])
    assert worst < 1.0, f"pinion does not roll on the rack: {worst:.1f} mm3 overlap"
    jam = pawl_check(parts["rail_rack"], parts["rail_pawl"])
    assert jam < 1.0, f"pawl jams in the tooth space: {jam:.1f} mm3 overlap"

    # ------------------------------------------------ does the spring work?
    I = LEAF_W * LEAF_T ** 3 / 12.0
    P = 3 * E_PETG * I * PAWL_ENGAGE / LEAF_L ** 3
    sigma = 3 * E_PETG * PAWL_ENGAGE * LEAF_T / (2 * LEAF_L ** 2)
    beta = math.radians(90 - PRESSURE_DEG)
    hold = P * math.tan(beta)
    print(f"\ntwo-way detent, riding {PAWL_ENGAGE:.1f} mm out of a tooth space:")
    print(f"  preload        {P:5.1f} N")
    print(f"  fibre stress   {sigma:5.1f} MPa   SF {SIGMA_PETG / sigma:.2f}")
    print(f"  flank          {90 - PRESSURE_DEG:.0f} deg off travel -> holds "
          f"{math.tan(beta):.2f}x preload = {hold:.1f} N both ways")
    print(f"  one tooth      {RACK_PITCH:.2f} mm of creep if it ever slips")

    # walking inertia is the load it exists to resist
    m_torso = 1.538
    for acc in (1.0, 2.0, 3.0):
        print(f"  torso at {acc:.0f} m/s2 -> {m_torso * acc:5.1f} N  "
              f"{'HELD' if m_torso * acc < hold else 'SLIPS'}")

    # ------------------------------------------------ does the servo+ work?
    r_pitch = MOD * PINION_Z / 2.0
    per_rev = 2 * math.pi * r_pitch
    mu = 0.25
    f_fric = m_torso * 9.81 * mu
    kgcm = f_fric * (r_pitch / 10.0) / 9.81      # N x cm -> kgf.cm
    print(f"\nservo+ pinion, {PINION_Z}T module {MOD:.0f}:")
    print(f"  pitch dia      {2 * r_pitch:.1f} mm -> {per_rev:.1f} mm per turn")
    print(f"  full travel    {TRAVEL / per_rev:.2f} turns "
          f"({60 * TRAVEL / per_rev / 55:.1f} s at 55 rpm)")
    print(f"  torque needed  {kgcm:.2f} kg.cm against {f_fric:.1f} N of friction, "
          f"{100 * kgcm / 25.0:.0f}% of the MEASURED 25 kg.cm")
    print(f"  back-drivable  YES -- so the servo+ build still needs the detent, "
          f"or a stalled servo holds the torso against every step")

    # ------------------------------------------- evidence scenes (renders)
    # _scene_* files are NOT parts; they exist so hero_render can show the
    # claims: joints on the splice planes, keys in their pockets, the halves'
    # joint faces. Children are fresh moved copies -- Compound RE-PARENTS
    # shared children (the project already paid for that one).
    export_step(Compound(children=[copy.copy(s) for s in run]),
                str(out / "_scene_way_run.step"))
    export_step(Compound(children=[
        copy.copy(car_aft).moved(Location((-14.0, 0, 0))),
        copy.copy(car_fwd).moved(Location((14.0, 0, 0))),
    ]), str(out / "_scene_carriage_halves.step"))
    export_step(Compound(children=[
        copy.copy(parts["rail_way_inner"]),
        copy.copy(parts["rail_way_outer"]).moved(Location((WAY_SEG_L + 8.0, 0, 0))),
        copy.copy(parts["rail_way_key"]).moved(
            Location((WAY_SEG_L + 4.0, 0, KEY_Z0 + 16.0))),   # floated so the
                                            # render shows it; seated it hides
                                            # between the exploded end faces
    ]), str(out / "_scene_joint_key.step"))
    return parts


if __name__ == "__main__":
    main()
