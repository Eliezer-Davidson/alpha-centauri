"""Alpha Centauri — foot: PETG core + SEPARATE TPU tread. Four identical pairs.

    edu/.cadenv/bin/python cad/alpha_centauri/foot.py

THE CONTRACT THIS PART EXISTS TO KEEP
-------------------------------------
The foot presents a SPHERE of radius FOOT_SPHERE_R = 15 whose centre sits ON
the calf axis at FOOT_CENTRE_FROM_KNEE = L3 - R from the knee. The OUTER
surface of the TPU tread IS that sphere. Not "about", not "plus a pad": if the
tread added thickness outside R15 the contact point would drop below the IK's
ground plane and silently change the stance -- the same class of bug (sphere
centred AT the foot instead of ON the axis) already put the drawn robot at the
forbidden 250 mm stance once. So:

    PETG core outer radius = R15 - TREAD_T   (12.0, ground side)
    TPU tread outer radius = exactly R15, SAME centre

and the build asserts both on the finished solids: every tread vertex sits in
the 12..15 shell with the outer surface exactly at 15 (the one deliberate
exception, the retention bead, is confined and asserted -- see RETENTION
below), every core vertex on the ground side of the centre sits inside 12,
and the assembled contact radius stays 15.000 at every tilt in the swept
swing check below.

WHY THE TREAD IS A FULL HEMISPHERE ENDING ON THE COLLAR RIM
-----------------------------------------------------------
Required angular coverage is DERIVED, not guessed: the calf tilts up to
~37.9 deg from vertical across the working envelope (the ~38.5 deg swing the
constants comment records -- reproduced here from the leg geometry, see
calf_tilt_deg), plus the angular half-width of the squished contact patch,
plus margin -- about 54 deg. A cap of exactly that size was drawn first and
rejected for its EDGE: any free-floating tread edge is either a >45 deg
overhung ring (radial cut), a knife-edge TPU taper (chamfered cut), or a ring
bridging over air (horizontal cut). Making the clamp collar diameter EQUAL to
the sphere (COLLAR_D = 2*R15 = 30) dissolves the problem: the tread runs all
the way to the equator and its termination ring lands flat ON the collar's
own rim, supported by PETG, with zero overhang. The silhouette is a cylinder
blending into its own ball, and coverage is 90 deg against the ~54 needed.

The PETG collar rim circle lies exactly ON the R15 sphere at the equator --
which is fine, and checked: at the maximum swept tilt it still clears the
ground (gate 4 measures the number), and the sweep assert below keeps it
that way forever.

SPLIT FOR THE A1 MINI (2026-09-07, REPLAN-2026-08-28 items 1 & 5)
-----------------------------------------------------------------
This file originally CO-PRINTED the two bodies -- TPU deposited onto the PETG
dome mid-print by the H2C's second nozzle. The H2C is gone; the only printer
is a Bambu A1 mini with ONE nozzle, so the co-print object no longer exists
on any machine this project owns. The tread is now a SEPARATE TPU part that
snaps onto the finished core. Everything the co-print design got right (the
contract, the hemisphere-to-rim termination, the clamp) is unchanged;
what is new is mechanical retention plus an assembly law:

    ASSEMBLY LAW: the tread is retained by the circumferential bead/groove
    engagement below AND a flexible adhesive of the Shoe-Goo class wetting
    the 905 mm2 spherical interface + 254 mm2 rim ring. NEVER glue alone --
    an adhesive-only joint on a flexing TPU shell fails by peel at the rim,
    exactly the load the bead exists to anchor. (Wet assembly is also the
    lubricant that makes the snap easy.)

RETENTION -- INTERNAL BEAD INTO A DOME GROOVE (the DECISION)
------------------------------------------------------------
The tread carries an internal circumferential BEAD: a spherical-band ridge
BEAD_H = 0.8 mm proud of its R12 bore, spanning polar angle 58..73 deg from
the ground pole. The core's dome carries the matching circumferential GROOVE,
cut 57..74 deg (1 deg polar play per side, ~0.2 mm) with its floor at
R11.0 -- 0.2 mm BELOW the bead crest, deliberately: the tread's radial seat
must always be the R12 dome-on-bore contact, never the bead bottoming in a
shallow groove, because a bead that props the shell outward moves the outer
surface past R15 and silently violates the contract. The groove is cut
deeper than the bead can reach; adhesive fills the void.

Rejected alternatives, recorded so they are not redrawn:
  * TPU skirt over the collar with a bead into a collar-OD groove: any skirt
    material below the equator and outside the collar sits OUTSIDE the R15
    sphere -- it fails the contract's own vertex gate. The gate is right and
    the skirt is wrong: material out there widens the presented ball.
  * Spherical undercut at the equator (expose the R12 ball below its equator
    and let the shell wrap past it): the exposed neck necks down below
    R12.0, but the socket's box-pocket corner sweeps a 12.42 mm radius --
    the undercut breaches into the pocket. Negative wall, dead on arrival.
The chosen band sits entirely ABOVE the equator (groove floor ends 3.0 mm
above it -- clear of collar and socket by construction, asserted) and
entirely OUTSIDE the derived contact envelope (band starts at 58 deg against
the ~55 deg the envelope needs, asserted): no contact pose ever loads the
one ring where tread backing thickness differs, so contact compliance is
uniform over every reachable touchdown.

Mechanics, derived in-code and asserted: snap-on travel is ~1.4 mm with a
peak bead hoop strain of BEAD_H/BEAD_R_IN = 7.1% -- trivial for TPU 95A
(elongation at break ~450%). Pull-off is blocked by the groove's pole-side
shoulder after ~0.23 mm of polar play: gate 6 MOVES the tread 1.0 mm along
the pull-off axis and asserts real solid interference with the core, so the
retention is proven on the geometry, not asserted in prose. Spin about the
calf axis is the one motion the bead does not resist -- it is geometrically
harmless (the tread is a body of revolution; the contact sphere is invariant)
and the adhesive owns it.

HOW IT CLAMPS THE CALF -- AND WHY A THROUGH-BOLT, NOT A PINCH
-------------------------------------------------------------
The calf ends in a 16 mm x 14 mm boss -- but the boss and the calf's 20 x 14
box shaft END TOGETHER at the sphere centre, so the socket must swallow both:
the pocket is the union of the box section and the boss bore, cut SOCKET_CLEAR
loose. That is a feature, not a workaround: the box flats are anti-rotation
for free, and the boss end face bottoming on the pocket floor puts the sphere
centre at FOOT_CENTRE_FROM_KNEE by construction -- zero axial adjustment.

Retention is the calf's own M3 cross pilot, used as a THROUGH-BOLT in double
shear. A pinch clamp was rejected because its slit would cross the collar (and
the tread's seat ring), and because this project already learned on the yaw
lock that friction devices hold nothing worth holding: a positive pin cannot
cam out at any load. Both foot walls are M3 CLEARANCE, threads engage ONLY the
calf's 2.6 pilot -- a member that is clamped and threaded at once can never be
drawn tight (the thread phase sets the gap, not the head). M3 x 25 socket head,
3 mm counterbore. The pocket is 180-deg symmetric, so the bolt can enter from
either side and the part stays non-handed: one STL, printed four times.

PRINT ORIENTATION -- TWO PARTS, TWO POSES
-----------------------------------------
CORE (PETG): socket-down, ball-up, unchanged. The collar's flat top ring is
the ONLY flat face the part owns, ~400 mm2 of real first layer. Ball-down is
the exact trap partcheck exists to catch -- a sphere touches the plate at a
POINT. Upright, every surface behaves: collar walls vertical, the dome closes
as a dome. The one flagged region is the pocket ceiling: a single 16.3 mm
PETG bridge where the boss seats -- the calf already prints a 15 mm bridge
over its hollow shaft "without complaint", and a domed ceiling would gut the
core right where the contact load flows from the pole up into the boss seat.
Deliberate, kept. The groove adds one small steep ring (its pole-side
shoulder, a ~57 deg cone face 1 mm tall) -- stair-steps on a dome, fine.

TREAD (TPU 95A): SEAT-RING-DOWN -- the same orientation the co-print used,
now on its own plate. "Tread-down" (dome on the plate) was considered and is
the point-contact trap again: the working surface is convex everywhere and
owns no flat. The seat ring is the tread's only flat face (254 mm2), so it
beds; the dome closes upward like any ball top. The honest cost, and the one
thing that CHANGED meaning in the split: the concave inner cap (the last
~265 mm2 where the bore closes toward its pole) used to be graded "support
needed" as an ARTIFACT -- it deposited straight onto the PETG dome mid-print.
There is no dome under it any more. It is now a REAL support region: print
with light tree support reaching through the 24 mm bore opening, or accept
millimetre-scale droop -- which lands on the glued, TPU-compliant interface
where the dome presses it flat and the adhesive fills what is left. Either
is acceptable; the droop does NOT reach the outer surface (3 mm of tread
between them prints supported by its own perimeters). The bead prints as a
ridge on a near-vertical wall 3-6 mm up; its rim-side flank is a small steep
ring the grade counts honestly.

TPU IS EXTERNAL-SPOOL ONLY on the A1 mini: the AMS lite cannot feed
flexibles. Direct-drive extruder handles 95A fine. PETG-CF is NOT this part:
core is plain PETG (MATERIAL_BULK), tread is MATERIAL_GRIP.

The dual-material 3MF export and the fused-body partcheck grade are RETIRED
with the co-print (2026-09-07): the printer never builds that object. Each
part now exports its own STL/3MF in its own print pose, and gate 5 grades
BOTH parts in their own print orientations, as the project law demands.

THE WATERTIGHT FLAG CANNOT PASS A SPHERE -- CHECKED, NOT IGNORED
----------------------------------------------------------------
This is the project's first spherical part, and partcheck's watertight flag
fails on a PLAIN build123d Sphere: OCCT's pole fan leaves one or two
ZERO-LENGTH boundary edges exactly at the parametric pole -- a topological
artifact with zero measure, not a hole (partcheck's own docstring warns that
integrity checks can end up "measuring the tessellator rather than the
part", and this is that case; its vertex weld cannot merge an edge that has
no length to merge). partcheck is not edited; instead the build proves
closure independently: every boundary edge of the welded mesh must have zero
length AND sit on the sphere's polar axis, and the tessellated volume must
agree with the exact B-rep volume -- a cracked or leaking solid can satisfy
neither. A real hole anywhere fails loudly.

WHY THE TREAD IS TPU AND SEPARATE THICKNESS MATTERS
---------------------------------------------------
TREAD_T = 3.0: thick enough to be the only thing that ever touches ground
(wear item), thin enough that squish under a footfall stays small -- the sink
term below feeds the coverage requirement, so making the tread softer or
thicker WIDENS the patch and eats coverage margin; the assert closes the loop.
The 905 mm2 spherical interface + 254 mm2 collar ring that used to be a
co-print weld are now the ADHESIVE areas; the load across them is compression
+ shear, never peel -- and the bead anchors the rim against the peel that
assembly abuse or a scuffed edge could start. (calf.py records why the foot
was never printed integral with the calf.)

Geometry is authored in the ROBOT frame (knee at origin, calf down +Z), same
as calf.py. Each part's print pose is a pure Z translation of the authored
frame -- the parts are authored in their shared print ORIENTATION; only the
drop to the plate differs per part (the co-print's single shared transform is
retired with it).
"""

import copy
import math
import subprocess
import sys
from pathlib import Path

import numpy as np

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    Compound,
    Cone,
    Cylinder,
    Location,
    Locations,
    Mode,
    Sphere,
    export_step,
    export_stl,
)

from interface_constants import (
    BED_X,
    BED_Y,
    BED_Z,
    CRAWL_SHIFT_CENTRED,
    CRAWL_STRIDE_HALF,
    FOOT_CENTRE_FROM_KNEE,
    FOOT_SPHERE_R,
    L1_LATERAL,
    L1_VERTICAL,
    L2_THIGH,
    L3_CALF,
    LEG_EXTENSION_LIMIT,
    STANCE_Z,
    extension_at,
)
from calf import (  # single source for everything the foot mates with
    BOSS_D,
    BOSS_L,
    M3_CLEAR,
    M3_PILOT,
    SEC_X as CALF_SEC_X,
    SEC_Y as CALF_SEC_Y,
    create_calf,
)

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "edu/tools"))

# ------------------------------------------------------------------- stations
ZC = FOOT_CENTRE_FROM_KNEE            # DERIVED  123.14, sphere centre, ON axis
TOP_Z = ZC - BOSS_L                   # DERIVED  109.14, socket opening plane
BOLT_Z = ZC - BOSS_L / 2              # DERIVED  116.14 -- the same expression
                                      #          calf.py uses to place its pilot,
                                      #          so they can never drift apart

# ---------------------------------------------------------------------- tread
TREAD_T = 3.0                         # DECISION  wear allowance vs squish; see
                                      #           docstring -- feeds TREAD_SINK
R_CORE = FOOT_SPHERE_R - TREAD_T      # DERIVED   12.0, the PETG/TPU interface
THETA_COV_DEG = 90.0                  # DERIVED   tread runs to the equator and
                                      #           seats on the collar rim

# ------------------------------------------------- retention (A1 mini split)
# See RETENTION in the docstring for the full decision record.
BEAD_H = 0.8              # DECISION  radial protrusion of the bead below R_CORE:
                          #           2 extrusion widths -- printable as a ridge,
                          #           deep enough for a real shoulder
BEAD_TH = (58.0, 73.0)    # DECISION  polar band, deg from the ground pole.
                          #           Starts ABOVE the ~55 deg contact need
                          #           (asserted), ends 17 deg short of the rim
GROOVE_CLR_DEG = 1.0      # DECISION  polar play per side, ~0.2 mm of arc
GROOVE_EXTRA_DEPTH = 0.2  # DECISION  groove floor sits below the bead crest so
                          #           the DOME, never the bead, sets the tread's
                          #           radial seat -- a bead that bottoms first
                          #           props the outer surface past R15 (the LAW)
BEAD_R_IN = R_CORE - BEAD_H                  # DERIVED  11.2, bead crest radius
GROOVE_R_IN = BEAD_R_IN - GROOVE_EXTRA_DEPTH  # DERIVED  11.0, groove floor
RETENTION_TEST_PULL = 1.0  # DECISION  pull-off displacement gate 6 tests at

# ---------------------------------------------------------------------- clamp
COLLAR_D = 2 * FOOT_SPHERE_R          # DERIVED   30.0 -- equal to the sphere BY
                                      #           CONSTRUCTION; this is what lets
                                      #           the tread end on the rim
SOCKET_CLEAR = 0.3                    # DECISION  total per dimension (0.15/side).
                                      #           Both parts print on the same
                                      #           machine from the same constants,
                                      #           so this is a light push fit, not
                                      #           the 0.4 of an unverified vendor
                                      #           pocket. A loose foot wobbles the
                                      #           contact point.
CB_D, CB_DEPTH = 6.2, 3.0             # DECISION  M3 socket head (5.5 x 3) recess

# ------------------------------------------------- working envelope, for cover
# Contact poses: stance from STANCE_Z down to a CROUCH_DROP body drop, body
# shifted up to the crawl's lateral shift, striding up to its half-amplitude.
# CROUCH_DROP mirrors the crawl's own 25 mm scale -- and at exactly this drop
# the derived swing reproduces the ~38.5 deg the constants comment and
# build_report already quote, which is the number this tread was specced
# against. Candidate for promotion to interface_constants.py.
CROUCH_DROP = 25.0                    # DECISION  see above
TREAD_SINK = 0.3                      # DECISION  radial squish of the loaded
                                      #           tread; ~21 N/foot on 3 mm of
                                      #           ~95A TPU estimates 0.16 mm --
                                      #           0.3 is that with headroom
TREAD_MARGIN_DEG = 5.0                # DECISION  beyond swing + patch
DOC_SWING_DEG = 38.5                  # the figure the repo already quotes; the
                                      # derivation below must land on it


def calf_tilt_deg(stance_z, lateral_shift=0.0, fore_aft=0.0):
    """Angle between the calf axis and world vertical, in a contact pose.

    This is what decides where on the sphere the ground lands. In the leg
    plane: the hip-to-foot line tilts atan2(stride, V) off vertical, and the
    calf sits a law-of-cosines angle off that line (knee bend). Worst case
    they add. Out of plane: a lateral body shift swings the whole leg plane
    (Kinematics.py's constant-offset constraint, same geometry extension_at
    encodes), and the two tilts combine as acos(cos*cos). The V term repeats
    extension_at's own construction -- L1_VERTICAL PLUS the in-plane drop --
    because that sign error has already bitten this project twice.
    """
    y = L1_LATERAL + lateral_shift
    v = L1_VERTICAL + math.sqrt(y * y + stance_z * stance_z - L1_LATERAL ** 2)
    d = math.hypot(fore_aft, v)
    beta = math.acos((d * d + L3_CALF ** 2 - L2_THIGH ** 2) / (2 * d * L3_CALF))
    alpha = math.atan2(abs(fore_aft), v)
    in_plane = beta + alpha
    lam = math.atan2(y, stance_z) - math.asin(L1_LATERAL / math.hypot(y, stance_z))
    return math.degrees(math.acos(math.cos(in_plane) * math.cos(lam)))


def swing_max_deg():
    """Max calf tilt over the contact envelope corners (worst is the crouch
    at full stride, zero shift -- shifting EXTENDS the leg and straightens it)."""
    worst = 0.0
    for stance in (STANCE_Z, STANCE_Z - CROUCH_DROP):
        for shift in (0.0, CRAWL_SHIFT_CENTRED):
            for stride in (0.0, CRAWL_STRIDE_HALF):
                assert extension_at(stance, shift, stride) < LEG_EXTENSION_LIMIT, (
                    f"envelope corner ({stance}, {shift}, {stride}) is not "
                    f"even reachable -- fix the envelope, not the tread")
                worst = max(worst, calf_tilt_deg(stance, shift, stride))
    return worst


# Contact patch half-angle: pressing a sphere TREAD_SINK deep widens the
# contact from a point to a disc of radius sqrt(2*R*sink - sink^2).
PATCH_HALF_DEG = math.degrees(math.asin(
    math.sqrt(2 * FOOT_SPHERE_R * TREAD_SINK - TREAD_SINK ** 2) / FOOT_SPHERE_R))


def band_volume(r_in, r_out, th1_deg, th2_deg):
    """Exact volume of a spherical-shell sector: radii r_in..r_out, polar
    th1..th2 about the axis. V = (2*pi/3)(r_out^3 - r_in^3)(cos th1 - cos th2).
    This closed form is why the bead/groove are spherical bands with conical
    flanks and not a torus: gate 1's exact-volume assert survives the split."""
    return (2 * math.pi / 3) * (r_out ** 3 - r_in ** 3) * (
        math.cos(math.radians(th1_deg)) - math.cos(math.radians(th2_deg)))


def _check():
    # The reason the sphere centre is where it is. If this fails, someone
    # changed L3 or R without the other and the contact no longer lands at L3.
    assert abs(ZC + FOOT_SPHERE_R - L3_CALF) < 1e-9, (
        f"contact point {ZC + FOOT_SPHERE_R} != L3 {L3_CALF}")

    # COVERAGE IS DERIVED, NOT ASSERTED. Swing from the leg geometry, patch
    # from the tread squish, margin on top -- the tread must cover it all.
    swing = swing_max_deg()
    need = swing + PATCH_HALF_DEG + TREAD_MARGIN_DEG
    assert THETA_COV_DEG >= need, (
        f"tread covers {THETA_COV_DEG} deg but the envelope needs "
        f"{swing:.2f} swing + {PATCH_HALF_DEG:.2f} patch + "
        f"{TREAD_MARGIN_DEG:.1f} margin = {need:.2f} deg")

    # ... and the derivation must land on the figure the repo already quotes.
    # If these diverge, either the envelope here or every document citing
    # 38.5 deg is wrong -- find out which before printing.
    assert abs(swing - DOC_SWING_DEG) <= 1.0, (
        f"derived swing {swing:.2f} deg does not reproduce the documented "
        f"~{DOC_SWING_DEG} deg -- the envelope definition has drifted")

    # ---- retention band (A1 mini split) -------------------------------------
    th1, th2 = BEAD_TH
    assert 0.0 < th1 < th2 < THETA_COV_DEG, "bead band must live on the tread"
    # The bead must sit OUTSIDE every reachable contact direction, with margin:
    # the one ring where tread backing differs must never be what touches down.
    assert th1 >= need + 2.0, (
        f"bead band starts at {th1} deg, inside the contact envelope's "
        f"{need:.2f} deg (+2 margin) -- contact would ride the bead")
    # Groove stays ABOVE the equator: clear of the collar rim seat and the
    # socket (both live at z <= ZC) by construction.
    groove_z_min = GROOVE_R_IN * math.cos(math.radians(th2 + GROOVE_CLR_DEG))
    assert groove_z_min > 1.0, (
        f"groove reaches to {groove_z_min:.2f} mm above the equator -- too "
        f"close to the collar rim seat")
    # Printable ridge, and shallow enough to snap: <= half the tread wall.
    assert 0.4 <= BEAD_H <= TREAD_T / 2, f"bead height {BEAD_H} out of range"
    assert GROOVE_EXTRA_DEPTH > 0, (
        "groove must be deeper than the bead: the dome, never the bead, "
        "sets the tread's radial seat (the R15 law)")
    assert GROOVE_CLR_DEG > 0
    # Assembly snap: peak hoop strain at the bead crest ring.
    hoop = BEAD_H / BEAD_R_IN
    assert hoop < 0.20, f"snap needs {hoop:.1%} hoop strain -- too much even for TPU"

    # The socket must actually clear the calf, wall by wall.
    assert SOCKET_CLEAR > 0
    # Collar wall at the pocket's worst corner (the box diagonal).
    corner_r = math.hypot((CALF_SEC_X + SOCKET_CLEAR) / 2,
                          (CALF_SEC_Y + SOCKET_CLEAR) / 2)
    assert COLLAR_D / 2 - corner_r >= 2.0, (
        f"collar wall {COLLAR_D / 2 - corner_r:.2f} mm at the pocket corner "
        f"-- below the 2.0 structural floor")
    # The pocket corner is also why the equator-undercut retention was
    # rejected: an exposed neck below R12.0 cannot clear a 12.42 mm corner.
    assert corner_r > R_CORE, "if this ever flips, revisit the undercut option"
    # The bore is bigger than the boss, the box pocket bigger than the shaft.
    assert BOSS_D + SOCKET_CLEAR > BOSS_D and CALF_SEC_X + SOCKET_CLEAR > CALF_SEC_X

    # Tread printable: at least 4 extrusion widths of TPU everywhere.
    assert TREAD_T >= 1.6, f"tread {TREAD_T} mm is thinner than 4 extrusions"

    # Counterbore must leave real wall for the clearance bore to steer in.
    assert COLLAR_D / 2 - CB_DEPTH - (BOSS_D + SOCKET_CLEAR) / 2 >= 3.0

    # Retention scheme: the screw must spin FREE in both foot walls and
    # thread ONLY in the calf's pilot -- that is what makes the joint tight.
    assert M3_PILOT < 3.0 < M3_CLEAR, (
        "an M3 must clear the foot walls and bite the calf pilot")

    assert 0 < CROUCH_DROP < STANCE_Z - 150  # sanity on the envelope itself


_check()


# ============================================================================
# solids
# ============================================================================
def _polar_band(r_in, r_out, th1_deg, th2_deg):
    """Spherical-shell sector about the calf axis, centred at the sphere
    centre C: radii r_in..r_out, polar angle th1..th2 from the ground pole
    (+Z). Volume is band_volume() EXACTLY -- sphere and cone are quadrics,
    so the boolean is closed-form and gate 1 keeps its 1e-3 assert."""
    h = 3.0 * FOOT_SPHERE_R
    at_c = Location((0, 0, ZC))
    shell = at_c * Sphere(r_out) - at_c * Sphere(r_in)
    outer_cone, inner_cone = (
        at_c * Cone(bottom_radius=0.0,
                    top_radius=h * math.tan(math.radians(th)),
                    height=h,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))
        for th in (th2_deg, th1_deg))
    return shell & outer_cone - inner_cone


def create_foot_core():
    """PETG: R12 sphere + clamp collar, socket cut for the calf's boss + shaft,
    retention groove cut into the dome.

    Robot frame, knee at origin, ground toward +Z. The socket opens toward -Z
    (the knee), which is also the print's bed face.
    """
    with BuildPart() as part:
        # the load-bearing ball -- outer radius R15 - TREAD_T, ON the axis
        with Locations((0, 0, ZC)):
            Sphere(R_CORE)
        # clamp collar, flush with the tread sphere's equator by construction
        with Locations((0, 0, (TOP_Z + ZC) / 2)):
            Cylinder(radius=COLLAR_D / 2, height=BOSS_L, align=Align.CENTER)

        # socket: the calf's box shaft AND boss end together at the sphere
        # centre, so the pocket is their union, cut loose by SOCKET_CLEAR.
        # Floor at exactly ZC: the boss bottoms out and the sphere centre
        # lands at FOOT_CENTRE_FROM_KNEE with no adjustment possible.
        pocket_h = BOSS_L + 6.0        # overshoots the top face; floor is what counts
        with Locations((0, 0, ZC - pocket_h / 2)):
            Box(CALF_SEC_X + SOCKET_CLEAR, CALF_SEC_Y + SOCKET_CLEAR, pocket_h,
                align=Align.CENTER, mode=Mode.SUBTRACT)
            Cylinder(radius=(BOSS_D + SOCKET_CLEAR) / 2, height=pocket_h,
                     align=Align.CENTER, mode=Mode.SUBTRACT)

        # retention: M3 through-bolt on the calf's own cross pilot. BOTH foot
        # walls are clearance -- threads engage only the calf (a clamped member
        # that is also threaded can never be drawn tight). M3 x 25 socket head.
        with Locations((0, 0, BOLT_Z)):
            Cylinder(radius=M3_CLEAR / 2, height=2 * COLLAR_D,
                     rotation=(90, 0, 0), mode=Mode.SUBTRACT)
        with Locations((0, -(COLLAR_D / 2 - CB_DEPTH + 4.0), BOLT_Z)):
            Cylinder(radius=CB_D / 2, height=8.0,
                     rotation=(90, 0, 0), mode=Mode.SUBTRACT)

    # tread-retention groove: the bead's band widened by the polar play,
    # floor GROOVE_EXTRA_DEPTH below the bead crest (dome seats, bead never
    # bottoms), cut radially past the dome surface so the boolean is robust.
    groove = _polar_band(GROOVE_R_IN, R_CORE + 1.0,
                         BEAD_TH[0] - GROOVE_CLR_DEG,
                         BEAD_TH[1] + GROOVE_CLR_DEG)
    return part.part - groove


def create_foot_tread():
    """TPU: hemispherical shell, R_CORE..R15, terminating on the collar rim,
    plus the internal retention bead.

    Outer surface = THE contact sphere of the whole robot. Nothing here may
    be clever: two concentric spheres, a half-space cut at the equator, and
    one spherical-band bead whose OUTER extent stops at the bore -- the bead
    is the one sanctioned excursion below R12, and gate 1 confines it.
    """
    with BuildPart() as part:
        with Locations((0, 0, ZC)):
            Sphere(FOOT_SPHERE_R)
            Sphere(R_CORE, mode=Mode.SUBTRACT)
        # keep the ground-side hemisphere only (z >= ZC)
        with Locations((0, 0, ZC + 2 * FOOT_SPHERE_R)):
            Box(6 * FOOT_SPHERE_R, 6 * FOOT_SPHERE_R, 4 * FOOT_SPHERE_R,
                align=Align.CENTER, mode=Mode.INTERSECT)
    # retention bead: crest at BEAD_R_IN, band BEAD_TH. Built radially past
    # R_CORE (the overlap is already shell material, adds no volume) so the
    # union never fuses two coincident spheres.
    bead = _polar_band(BEAD_R_IN, R_CORE + 1.0, *BEAD_TH)
    return part.part + bead


# ============================================================================
# checks that need the solids
# ============================================================================
def _verts(shape, tol):
    v, _ = shape.tessellate(tol)
    return np.array([(p.X, p.Y, p.Z) for p in v], dtype=float)


def _rot(axis_az_deg, tilt_deg):
    """Rodrigues rotation by tilt about a horizontal axis at azimuth az."""
    az, t = math.radians(axis_az_deg), math.radians(tilt_deg)
    u = np.array([math.cos(az), math.sin(az), 0.0])
    k = np.array([[0, -u[2], u[1]], [u[2], 0, -u[0]], [-u[1], u[0], 0]])
    return np.eye(3) + math.sin(t) * k + (1 - math.cos(t)) * (k @ k)


def assert_closed(shape, name):
    """Independent closure proof -- see 'THE WATERTIGHT FLAG' in the docstring.

    partcheck's watertight flag fails on ANY sphere (zero-length pole-fan
    boundary edges). This check accepts exactly that artifact and nothing
    else: every boundary edge of the welded mesh must have zero length and
    lie on the polar axis, and the meshed volume must agree with the exact
    B-rep volume. A real crack or hole fails both ways.
    """
    import collections

    from partcheck import _mesh_of

    m = _mesh_of(shape)
    cnt = collections.Counter(map(tuple, m.edges_sorted))
    open_e = [k for k, v in cnt.items() if v == 1]
    for a, b in open_e:
        length = float(np.linalg.norm(m.vertices[a] - m.vertices[b]))
        axis_r = float(np.linalg.norm(m.vertices[a][:2]))
        assert length < 1e-6 and axis_r < 1e-6, (
            f"{name}: REAL open edge, length {length:.4f} mm at "
            f"{axis_r:.2f} mm off-axis -- not the pole artifact")
    dv = abs(m.volume - shape.volume) / shape.volume
    assert dv < 0.005, f"{name}: mesh volume off B-rep by {dv:.2%}"
    return len(open_e)


if __name__ == "__main__":
    from partcheck import check

    out = Path(__file__).parent / "output"
    out.mkdir(exist_ok=True)
    evid = Path(__file__).parent.parent.parent / "docs/evidence"
    evid.mkdir(parents=True, exist_ok=True)

    core = create_foot_core()
    tread = create_foot_tread()
    calf = create_calf()
    c = np.array([0.0, 0.0, ZC])

    def polar_deg(pts):
        rel = pts - c
        rr = np.maximum(np.linalg.norm(rel, axis=1), 1e-12)
        return np.degrees(np.arccos(np.clip(rel[:, 2] / rr, -1.0, 1.0)))

    # --- GATE 1: the contact-sphere contract, on the finished solids --------
    # Exact B-rep volume: a hemispherical 12..15 shell plus the bead band and
    # nothing else -- both terms closed-form.
    v_hemi = (4 * math.pi / 3) * (FOOT_SPHERE_R ** 3 - R_CORE ** 3) / 2
    v_exp = v_hemi + band_volume(BEAD_R_IN, R_CORE, *BEAD_TH)
    assert abs(tread.volume - v_exp) < 1e-3, (
        f"tread volume {tread.volume:.3f} != shell hemisphere + bead {v_exp:.3f}")

    # Tessellation vertices lie ON the B-rep faces: every tread vertex must
    # sit in the 12..15 shell about C, touching both bounds -- except the
    # bead, which may reach down to BEAD_R_IN but ONLY inside its own band.
    tv = _verts(tread, 0.005)
    r = np.linalg.norm(tv - c, axis=1)
    assert r.max() <= FOOT_SPHERE_R + 1e-6 and r.max() >= FOOT_SPHERE_R - 1e-6
    assert r.min() >= BEAD_R_IN - 1e-6, (
        f"tread reaches {r.min():.3f}, below the bead crest {BEAD_R_IN}")
    proud = r < R_CORE - 1e-6
    assert proud.any(), "the retention bead is missing from the tread"
    ppol = polar_deg(tv[proud])
    assert ppol.min() >= BEAD_TH[0] - 0.5 and ppol.max() <= BEAD_TH[1] + 0.5, (
        f"material below R12 outside the bead band: polar "
        f"{ppol.min():.1f}..{ppol.max():.1f} vs band {BEAD_TH}")
    # Directional support: the outer surface IS the R15 sphere for every
    # direction the swing can point the ground, patch and margin included.
    swing = swing_max_deg()
    for tilt in np.arange(0.0, swing + PATCH_HALF_DEG + TREAD_MARGIN_DEG + 1e-9, 5.0):
        for az in range(0, 360, 45):
            d = _rot(az, tilt)[:, 2]          # world-down mapped into part frame
            support = ((tv - c) @ d).max()
            assert support > FOOT_SPHERE_R - 0.02, (
                f"tread surface at tilt {tilt:.1f}/az {az} is "
                f"{support:.3f}, not {FOOT_SPHERE_R}")

    # The PETG core on the ground side of the centre stays INSIDE the tread:
    # outer radius R15 - TREAD_T, exactly as the contract demands. (The
    # groove only REMOVES material, so this bound is untouched by the split.)
    cv = _verts(core, 0.01)
    ground_side = cv[:, 2] > ZC + 1e-6
    cr = np.linalg.norm(cv[ground_side] - c, axis=1)
    assert cr.max() <= R_CORE + 1e-6, (
        f"PETG pokes to {cr.max():.3f} on the ground side (limit {R_CORE})")

    print(f"contact sphere:  R {FOOT_SPHERE_R:.2f} at {ZC:.2f} from the knee "
          f"-> contact at {ZC + FOOT_SPHERE_R:.2f} = L3 {L3_CALF:.2f}")
    print(f"tread volume     {tread.volume:8.2f} mm3 == hemisphere "
          f"{v_hemi:.2f} + bead {band_volume(BEAD_R_IN, R_CORE, *BEAD_TH):.2f} "
          f"(exact)")

    # --- GATE 2: coverage, derived --------------------------------------------
    need = swing + PATCH_HALF_DEG + TREAD_MARGIN_DEG
    print(f"\ncoverage: swing {swing:.2f} (documented ~{DOC_SWING_DEG}) "
          f"+ patch {PATCH_HALF_DEG:.2f} + margin {TREAD_MARGIN_DEG:.1f} "
          f"= {need:.2f} deg needed, tread covers {THETA_COV_DEG:.0f}; "
          f"bead band {BEAD_TH[0]:.0f}..{BEAD_TH[1]:.0f} stays outside it")

    # --- GATE 3: the clamp actually clears the calf ---------------------------
    for name, body in (("core", core), ("tread", tread)):
        hit = body & calf
        vol = 0.0 if hit is None else hit.volume
        assert vol < 1e-6, f"foot {name} intersects the calf: {vol:.3f} mm3"
    # ... and the seated tread engages the groove without interference: the
    # bead's band sits inside the groove's (parametric -- the surfaces are
    # tangent over 905 mm2, where a boolean would only measure OCCT noise).
    assert BEAD_TH[0] - GROOVE_CLR_DEG < BEAD_TH[0] and \
        BEAD_TH[1] + GROOVE_CLR_DEG > BEAD_TH[1] and \
        GROOVE_R_IN < BEAD_R_IN, "groove does not swallow the bead"
    print(f"\nclamp: pocket = calf section + {SOCKET_CLEAR / 2:.2f} mm/side, "
          f"boss bottoms on the floor at ZC; foot-vs-calf overlap 0.000 mm3")

    # --- GATE 4: swept ground contact -----------------------------------------
    # Tilt the assembled leg end about the sphere centre through the whole
    # swing (+patch +margin), every azimuth: the deepest point must ALWAYS be
    # TPU at exactly R15. Never the PETG rim, never the calf. partcheck can
    # not see this; only a sweep can (the calf/thigh lesson, again).
    kv = _verts(calf, 0.02)
    worst_gap, worst_pose = 1e9, None
    tilts = sorted(set(list(np.arange(0.0, need + 2.5, 2.5)) + [swing, need]))
    for tilt in tilts:
        for az in range(0, 360, 45):
            d = _rot(az, tilt)[:, 2]
            t_ext = ((tv - c) @ d).max()
            p_ext = max(((cv - c) @ d).max(), ((kv - c) @ d).max())
            assert t_ext > FOOT_SPHERE_R - 0.02      # contact still at R15
            gap = t_ext - p_ext
            if gap < worst_gap:
                worst_gap, worst_pose = gap, (tilt, az)
    assert worst_gap >= 1.0, (
        f"PETG/calf comes within {worst_gap:.2f} mm of the ground at "
        f"tilt {worst_pose[0]:.1f} deg az {worst_pose[1]}")
    print(f"swept 0..{need:.1f} deg x 8 azimuths: min TPU-to-PETG ground "
          f"clearance {worst_gap:.2f} mm at tilt {worst_pose[0]:.1f} deg "
          f"(only TPU ever touches down)")

    # --- GATE 6 (2026-09-07): retention is REAL, proven on the geometry -------
    # Pull the tread RETENTION_TEST_PULL along the pull-off axis (+Z, off the
    # ball toward the ground): the bead must collide with the groove's
    # pole-side shoulder -- solid interference, not friction, not glue. This
    # is the swept-interference law applied to the one relative motion the
    # split introduces. (Without the bead this displacement is entirely free:
    # two R12 spheres offset axially only ever move APART.)
    pulled = tread.moved(Location((0, 0, RETENTION_TEST_PULL))) & core
    v_pull = 0.0 if pulled is None else pulled.volume
    # Measured 10.4 mm3 at 1.0 mm pull (2026-09-07); the floor is set at a
    # fifth of that so tessellation/OCCT drift can never green a missing bead.
    assert v_pull > 2.0, (
        f"pull-off interference only {v_pull:.2f} mm3 -- the bead is not "
        f"engaging the groove shoulder")
    print(f"retention: bead {BEAD_H} mm proud at {BEAD_TH[0]:.0f}.."
          f"{BEAD_TH[1]:.0f} deg into groove {BEAD_TH[0]-GROOVE_CLR_DEG:.0f}.."
          f"{BEAD_TH[1]+GROOVE_CLR_DEG:.0f} deg (floor {GROOVE_R_IN}); "
          f"{RETENTION_TEST_PULL} mm pull-off -> {v_pull:.1f} mm3 of solid "
          f"interference. Assembly: mechanical snap + Shoe-Goo-class "
          f"adhesive, NEVER glue alone")

    # --- exports --------------------------------------------------------------
    # NB every Compound gets COPIES: build123d re-parents a child into the
    # newest compound it joins, so sharing solids between compounds silently
    # empties the earlier one -- the first foot-alone render came out as the
    # tread floating by itself, and only the caption volume gave it away.
    export_step(core, str(out / "foot_core.step"))     # robot frame, assembly
    export_step(tread, str(out / "foot_tread.step"))
    export_step(Compound(children=[copy.copy(core), copy.copy(tread)]),
                str(out / "foot.step"))
    export_step(Compound(children=[copy.copy(calf), copy.copy(core),
                                   copy.copy(tread)]),
                str(out / "foot_on_calf.step"))

    # print poses: authored ORIENTATION is the print orientation for both
    # parts (socket/seat-ring down, dome up -- see docstring); each part gets
    # its OWN drop to the plate. The co-print's single shared transform is
    # RETIRED (2026-09-07): the A1 mini has one nozzle, the parts print alone.
    printed_core = core.moved(Location((0, 0, -TOP_Z)))
    printed_tread = tread.moved(Location((0, 0, -ZC)))   # seat ring to the bed
    export_stl(printed_core, str(out / "foot_core.stl"))
    export_stl(printed_tread, str(out / "foot_tread.stl"))
    # The dual-material foot.3mf (Mesher, 2 bodies, shared pose) died with
    # the H2C: the printer never builds that object. partcheck below writes
    # one 3MF per part in its own print pose -- those are what get sliced.
    # TPU is EXTERNAL SPOOL only on the A1 mini (AMS lite cannot feed it).

    # --- masses (the claim the ledger needs) ----------------------------------
    m_core = core.volume / 1000.0 * 0.953              # PETG, g
    m_tread = tread.volume / 1000.0 * 1.21             # TPU, g
    print(f"\nmass: core {m_core:.1f} g PETG + tread {m_tread:.1f} g TPU "
          f"= {m_core + m_tread:.1f} g per foot, x4 = "
          f"{4 * (m_core + m_tread):.1f} g")

    # --- GATE 5: printability, EACH part in its OWN print orientation ---------
    rc = check(printed_core, "foot_core", out_dir=str(out), material="PETG")
    rt = check(printed_tread, "foot_tread", out_dir=str(out), material="TPU")
    # The fused core+tread grade is RETIRED with the co-print -- there is no
    # machine that builds the fused body, so grading it would be theatre.

    for tag, r_ in (("core", rc), ("tread", rt)):
        assert r_["solids"] == 1 and r_["bodies"] == 1 and r_["winding_ok"], (
            f"{tag} is not one consistent body")
        assert r_["fits_bed"]        # partcheck's own (stale H2C) bed gate...
        # ... and the REAL printer: partcheck.BED still says H2C 330x320x325
        # (REPLAN item 8's stale-text sweep owns that file); the A1 mini gate
        # lives here until partcheck migrates.
        assert all(s <= b for s, b in zip(sorted(r_["size_mm"]),
                                          sorted((BED_X, BED_Y, BED_Z)))), (
            f"{tag} does not fit the A1 mini bed {BED_X}x{BED_Y}x{BED_Z}")
    # partcheck's watertight flag cannot pass a sphere (see docstring);
    # closure is proven independently, artifact-and-nothing-else:
    for tag, body in (("core", printed_core), ("tread", printed_tread)):
        n_pole = assert_closed(body, tag)
        print(f"  closure: {tag} verified independently "
              f"({n_pole} zero-length pole edges, the known sphere artifact)")
    assert rc["overhang_detail"]["bed_contact_mm2"] >= 150.0
    # core support = the deliberate pocket-ceiling bridge + M3 crowns + the
    # groove's small pole-side shoulder ring (new with the split)
    assert rc["support_frac"] < 0.10, f"core support {rc['support_frac']:.1%}"
    # The tread's flagged region is its concave inner cap (the bore closing
    # toward the pole) plus the bead's rim-side flank. Under the co-print
    # this was an ARTIFACT (it deposited onto the PETG dome); printed alone
    # it is REAL: light tree support through the 24 mm bore opening, or
    # accept droop onto the glued interface -- see PRINT ORIENTATION in the
    # docstring. The bound stays, now guarding a real number.
    assert rt["support_frac"] < 0.15, f"tread support {rt['support_frac']:.1%}"
    assert rt["overhang_detail"]["bed_contact_mm2"] >= 150.0  # the seat ring
    # partcheck WARNs "REAL thin wall, 6.6x5.4x0.0" on the tread: probed
    # 2026-09-07, 100% of those samples sit ON the rim circle (r 14.97..15.00,
    # polar 89.9..90.0 deg, z 0..0.02) -- the convex sphere-meets-plane EDGE,
    # partcheck's own "every convex edge tapers to zero" case. A circular
    # edge is broad in TWO dims, so the sliver heuristic mislabels it; 0% of
    # the samples touch the bead. Not a wall, not gated -- recorded so nobody
    # chases it.

    # --- renders --------------------------------------------------------------
    hero = Path(__file__).parent.parent.parent / "edu/tools/hero_render.py"
    # assembled heroes (standing pose: ball down, knee up), as before
    for bodies, png, tag in (
        ([core, tread], "foot_hero.png",
         "Alpha Centauri — foot (PETG core + separate TPU tread)"),
        ([calf, core, tread], "foot_on_calf_hero.png",
         "Alpha Centauri — foot on calf"),
    ):
        src = Compound(children=[copy.copy(b) for b in bodies])  # see NB above
        view = src.rotate(Axis.X, 180)                 # robot +Z is DOWN; flip
        vstep = out / png.replace(".png", "_view.step")
        export_step(view, str(vstep))
        subprocess.run([sys.executable, str(hero), str(vstep),
                        "-o", str(out / png), "--tag", tag], check=True)

    # split evidence (docs/evidence, per the visual-proof law): core in print
    # pose (ball up -- groove visible), tread bowl-up (bead visible), and the
    # assembled axial section showing the bead seated in the groove.
    half = Box(200, 200, 400, align=(Align.CENTER, Align.MAX, Align.CENTER))
    section = Compound(children=[copy.copy(core & half),
                                 copy.copy(tread & half)]).rotate(Axis.X, 180)
    for solid, png, tag in (
        (copy.copy(core), "foot_split_core.png",
         "foot core, PETG — print pose; retention groove ring on the dome"),
        (copy.copy(tread).rotate(Axis.X, 180), "foot_split_tread.png",
         "foot tread, TPU 95A (external spool) — internal retention bead"),
        (section, "foot_split_section.png",
         "foot assembled, axial section — bead seated in the dome groove"),
    ):
        vstep = out / png.replace(".png", "_view.step")
        export_step(solid, str(vstep))
        subprocess.run([sys.executable, str(hero), str(vstep),
                        "-o", str(evid / png), "--tag", tag], check=True)

    print("\nALL GATES GREEN — foot: 2 SEPARATE parts (PETG core + external-"
          "spool TPU tread), 4 copies each; assembly = bead snap + flexible "
          "adhesive, never glue alone")
