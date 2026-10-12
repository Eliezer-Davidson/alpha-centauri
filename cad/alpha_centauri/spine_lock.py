"""Alpha Centauri — hand-driven spine: ratchet rack + sprung pawl (build123d).

    edu/.cadenv/bin/python cad/alpha_centauri/spine_lock.py

WHY THIS EXISTS
---------------
The chest is raised by the ARMS, not by a motor: the hands press down on the
waist and the chest walks itself up. That was the author's call on 2026-08-01, and the
arithmetic behind it is decisive -- a screw converts limited hand rotation
through a tiny lead, so 179 mm of rise on the M8 spine is 143 full turns, while
a rail uses the arm's stroke directly and needs one or two presses.

It also DELETES a problem rather than inheriting one. §1.4 found the twin
open-loop screw spine dead on paper: two independent screws jam the 8.5 mm bore
at 1.225 mm of differential. A rail has nothing to synchronise.

THE ACTUATOR IS DELIBERATELY NOT DECIDED HERE. The rack is the same part whether
a hand or a jack drives it, so it carries a motor-mount bolt pattern that starts
empty. If the arms disappoint, a jack bolts on and nothing else is redrawn.

WHY A RATCHET AND NOT DETENT PINS
---------------------------------
A ratchet needs no timing and no actuation to ENGAGE -- press, and it clicks.
Detents would need the pin driven home at the top of each stroke, which is a
second coordinated act by arms that are already busy holding the robot up.
Gravity only ever pulls the chest DOWN, so a one-way tooth is sufficient.

WHY THE LEAF SPRING DOES NOT CREEP
----------------------------------
The usual objection to a printed spring is sustained-load creep. It does not
apply here: seated in a notch the leaf is UNDEFLECTED and carries nothing. It
only bends while riding over a tooth, for a fraction of a second per stroke.
Peak fibre stress at full 4 mm deflection is

    sigma = 3*E*delta*t / (2*L^2) = 3*1700*4.0*2.0 / (2*40^2) = 12.75 MPa

against the 25 MPa PETG allowable this project uses -- SF 2.0 on an
intermittent load, and the detent force works out at ~2.5 N.

PRINT ORIENTATION
-----------------
Rack: UPRIGHT, long axis along print Z, teeth facing sideways. Every tooth face
is then either a horizontal top surface (the load-bearing ledge), a vertical
wall (the root), or a 63.4-degree ramp -- no supports anywhere, and the load
path down the rack runs along the extrusions rather than across layer lines.

Both SEGMENTS (below) keep exactly this orientation. The upper segment prints
SEAM-FACE-DOWN: its mortise opens at the bed (a vertical pocket, no supports)
and its roof is a 45-degree gable, so nothing overhangs. Flipping the upper
segment is FORBIDDEN -- upside down, every load ledge becomes a 90-degree
downface (12 flat bridges of 4 x 24 mm each). Its bed contact is the spine
section minus the mortise opening -- 152 mm2 measured (partcheck 2026-09-07),
right at partcheck's 150 mm2 shear-off floor for a 144 mm column -- so the
upper segment prints WITH A BRIM.

A1 MINI SPLIT -- TWO SEGMENTS ON A TOOTH-PITCH BOUNDARY (2026-09-07)
--------------------------------------------------------------------
REPLAN-2026-08-28 item 4. The monolithic rack is 288 mm tall (24 teeth x
12 mm: STROKE 250 + ENGAGE 40 -- the "~250 mm" in the REPLAN table was the
stroke, not the part). The A1 mini bed is 180^3; BED_DIAGONAL_MAX is 245
NOMINAL and 288 exceeds even that, so no orientation saves the monolith.

THE FALLBACK WAS MIS-SPECIFIED. The REPLAN table offers "trim the stroke to
245 and print diagonally", but rack height = STROKE + ENGAGE: a 245 mm PART
caps the stroke at 245 - 40 = 205, quantised to 17 teeth of travel = 204 mm,
AND sits exactly AT the nominal diagonal the constants say never to design
at. The fallback costs ~50 mm of stroke, not 5. The split costs zero stroke.
Rejected on arithmetic, not preference.

THE SEAM LAW: the joint plane sits ON a tooth-pitch boundary,
Z_SPLIT = SEG_TEETH * PITCH = 144.0 -- the root plane between tooth 11 and
tooth 12. Every tooth keeps its full profile on one side of the seam, so the
pawl's engagement at tooth 11 and tooth 12 is bit-identical to the monolith.
That claim is not asserted, it is MEASURED: the build gates below subtract
the assembled pair from a monolithic reference and require zero difference
anywhere in the tooth envelope, then seat and sweep the actual pawl across
the seam.

THE JOINT: a 14 x 6 x 16 tenon (key) on the lower segment registers the
upper's mortise; two M3 cross-screws (along X, through the mortise walls,
threading the tenon -- pilot 2.6, clearance 3.4) pin the seam shut in double
shear. Loads: the chest's weight crosses the seam in PURE COMPRESSION on the
24 x 10 butt faces; the tooth-offset load line adds a bending moment of
15.1 N x ~7 mm = 0.11 N-m = 0.27 MPa at the extreme fibre of the butt
section (S = 24*10^2/6 = 400 mm3) -- nothing. The screws are for handling,
assembly and pawl-snap shock, not for the standing load.

Y IS THE CRITICAL REGISTRATION AXIS: a Y-step at the seam eats directly into
the pawl's 0.3 mm depth clearance (PAWL_TOOTH_D = DEPTH - 0.3). The tenon's
Y-fit is therefore deliberately snug at 0.10/side (file to fit on the A1
mini; a loose fit here is NOT a shim, it is a mis-registered tooth), and a
module-level assert ties the worst-case step 2*SPLICE_CLEAR to that budget.
X and Z register on the tenon flanks and the butt faces respectively; Z is
what preserves the pitch across the seam and it is set by faces modelled at
the same coordinate, clamped by the screws.

The mortise's roof is a 45-degree GABLE, not a flat ceiling: printed
seam-face-down the pocket points up, and a flat roof would be a 14 x 6 mm
90-degree bridge partcheck would flag. The tenon is 0.6 mm shorter than the
pocket is deep, so the BUTT FACES meet, never the tenon tip.

DEFECTS FOUND WHILE SPLITTING (measured 2026-09-07, geometry probes)
--------------------------------------------------------------------
1. THE OLD ENGAGED VIEW WAS 10 mm DEEP INSIDE THE RACK. The 2026-08 viewer
   assembly placed the pawl at y = RACK_T + DEPTH + LEAF_T, omitting
   CARRIER_T: measured interpenetration 9617.147 mm3 -- the entire carrier
   inside the spine. The correct seat offset is
   RACK_T + DEPTH + LEAF_T + CARRIER_T, now owned by pawl_engaged_location()
   and used by every gate and view below. assembly.py (~line 281) restates
   the OLD offset for its own scene and is NOT fixed here (out of this
   file's scope) -- flagged for its owner.
2. THE RELEASE TAB CLIPS THE TEETH ABOVE THE SEAT. At full seat the tab
   (outer face 2 mm proud of the pawl tooth root, band y 12..14) crosses the
   ramps of teeth n+1 and n+2: 81.120 mm3 of interference, measured at every
   tooth of the MONOLITH too -- this is a pawl defect, not a seam defect.
   Bisected consequence: the resting pawl is held 2.000 mm out of full seat,
   so effective engagement depth is 1.700 mm, not the designed 3.7. The
   ledge still catches (the catch is in Z, and 1.7 mm of Y-overlap remain),
   but the "drops into the notch with clearance" figure above is optimistic
   by exactly the tab stand-off. Pawl geometry is UNTOUCHED here by
   assignment; the seam gates therefore assert PARITY with the monolith
   (identical intersection volumes) plus ZERO interference for the tab-free
   engaging portion of the pawl.

   RESOLVED 2026-09-23 (the entry above is kept as history, not deleted).
   The in-band tab is gone. It was not a tab at all: a 12 x 2 x 18 pad on
   the leaf's rack-side face, INSIDE the leaf's own footprint, so it neither
   stuck out of the chest nor could miss the teeth. Replaced by two RELEASE
   EARS at the leaf's free end, OUTSIDE the rack's X width (TAB_X_CLEAR 1.0
   mm off each rack side face, reaching TAB_PROUD 8.0 mm past the carrier
   side face, TAB_H 8.0 tall). Over the tooth band the ears are bridged only
   in the LEAF's y band, which is outboard of the tooth tips already; beyond
   the rack they drop as deep as the pawl tooth, so their rack-side face is
   flush with the tooth face and a finger (or the ganged carrier) pushes it
   toward the chest (+Y world) to lift the tooth out. Measured by the gates
   below: whole pawl vs rack at full seat 0.000 mm3 at teeth 5, 11, 12 and
   18 (assembled AND monolith); resting stand-off 0.0000 mm, effective
   engagement 3.700 mm = design; ears add 0.0000 mm to the ride-over
   deflection at every pose across the seam; pull-out + lowered-with-pawl-
   held-out release sweep worst 0.0000 mm3. The PARITY gates are replaced by
   ZERO gates; the monolith-vs-assembled rack gates (G2..G4) are untouched.

   OPTIONS MEASURED AND REJECTED (2026-09-23):
   a. SHORTEN THE TAB IN PLACE. Tooth n+1's ramp enters the tab's y band
      (world y 12..14) at seat + 7.5 mm, so a resting tab must stop 3.9 mm
      above the tooth. Worse, during ride-over the pawl deflects 4/7 mm per
      mm of climb while the ramp face above it also advances 4/7 mm per mm:
      a tab of height L over the tooth (2 mm shallower than it) leads the
      contact unless (L + 0.525) * 4/7 <= 2, i.e. L <= 2.975 mm. A 3 x 2 mm
      nub on the leaf face, between two teeth, is not something a finger
      can reach.
   b. MOVE IT UP / OUT IN Y. Outboard of the tooth tips (world y >= 14) is
      the leaf, then the carrier -- a tab there is inside the pawl; there is
      no free Y above the teeth's reach within the rack's X width.
   c. MOVE IT BELOW THE TOOTH. Tooth n (the seat ledge) sits directly under
      the pawl tooth in the same y band -- same clash, other end.
   CHOSEN: offset in X beyond the rack width -- the only placement that is
   clear in EVERY pose by construction (the pawl never moves in X), which is
   why P4 can gate it as a static clearance.

   PRINT POSE: carrier back face (pawl-local y = 0) on the bed. The ears
   were given full depth down to y = 0 outboard of the carrier precisely so
   they stand on the bed instead of cantilevering 10 mm up in the air.

   FOLLOWUPS FOUND WHILE FIXING (NOT fixed here -- outside this assignment):
   - THE LEAF IS NOT A CANTILEVER IN THE MODEL. The leaf box (local y
     10..12, z 22..62) is fused to the carrier's front face over its whole
     40 mm length -- there is no gap, so the "spring" cannot deflect toward
     the carrier at all. Every deflection in these gates is a RIGID
     translation of the whole pawl. The carrier needs a relief pocket (or
     the leaf a stand-off) behind the leaf before the ratchet can work.
   - The leaf's rack-side face sits EXACTLY on the tooth tips (world y 14.0
     both): zero running clearance along the tip lands.
   - At teeth 0 and 1 the CARRIER (not the ears) hits the base flange: the
     carrier hangs 22 mm below the seat. Measured ~1197 mm3 at tooth 0;
     the P4 gate proves the ears add nothing there.
"""

import copy
import math
import sys
from pathlib import Path

from build123d import (
    Align,
    BuildPart,
    Box,
    Compound,
    Cylinder,
    Face,
    Location,
    Locations,
    Mode,
    Rotation,
    Solid,
    Vector,
    Wire,
    add,
    export_step,
    export_stl,
)

from interface_constants import BED_X, BED_Y, BED_Z, PRINTER_MODEL

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "edu/tools"))

# ------------------------------------------------------------------ the stroke
STROKE = 250.0          # DECISION  stowed -> extended, as the telescope design
ENGAGE = 40.0           # rack still captured by the pawl at full extension

# ------------------------------------------------------------- tooth geometry
# One period: ramp up-and-out, then a horizontal ledge back in, then a vertical
# root face to the start of the next ramp. The pawl rides the ramp on the way
# up, snaps into the notch, and on the way down sits on the LEDGE -- so the
# locking face is horizontal and in pure compression, never a printed hook.
PITCH = 12.0            # lost height if the chest settles one tooth
RAMP_H = 8.0            # rise of the ride-over ramp
NOTCH_H = PITCH - RAMP_H                    # 4.0, the pawl tooth's seat
DEPTH = 4.0             # how far a tooth stands off the rack spine
TIP_LAND = 1.0          # flat at the tooth tip -- see below
RAMP_DEG = math.degrees(math.atan2(RAMP_H - TIP_LAND, DEPTH))   # 60.3 from horizontal

# WHY THE TIP HAS A LAND. Ramp straight into ledge makes the tooth tip a 63-deg
# wedge that tapers to nothing, and partcheck measured 1.6% of the rack's
# surface thinner than two extrusions -- all of it within 0.4 mm of the tip. A
# knife edge there prints as a burr, wears, and does no work: the pawl seats in
# the NOTCH, never on the tip. A 1 mm vertical land costs nothing and makes both
# tip corners square.

RACK_T = 10.0           # spine thickness (Y), before teeth
RACK_W = 24.0           # rack width (X)
N_TEETH = int((STROKE + ENGAGE) // PITCH)
RACK_H = N_TEETH * PITCH

# ------------------------------------------------------------- base mounting
FOOT_T = 6.0            # flange thickness
FOOT_W = 56.0           # flange width (X), spans to the deck screw lines
FOOT_D = 34.0           # flange depth (Y)
FOOT_BOLT_DX = 20.0     # M4 pattern into the waist deck
FOOT_BOLT_DY = 10.0
M4_CLEAR = 4.4
M3_CLEAR = 3.4
M3_PILOT = 2.6

# The empty option. A jack bolts here if the arms cannot do the job; the holes
# cost nothing and cannot be added later without reprinting the rack.
JACK_BOLT_DX = 17.0
JACK_BOLT_DY = 17.0

# --------------------------------------------------------------- pawl carrier
LEAF_L = 40.0           # cantilever length -- sets both stress and detent force
LEAF_T = 2.0            # leaf thickness
LEAF_W = 12.0           # leaf width
PAWL_TOOTH_H = NOTCH_H - 0.4        # 3.6, drops into the notch with clearance
PAWL_TOOTH_D = DEPTH - 0.3          # 3.7, seats before bottoming on the root
CARRIER_W = 34.0
CARRIER_T = 10.0
CARRIER_H = LEAF_L + 22.0
RELEASE_TAB = 18.0      # RETIRED 2026-09-23 -- the old in-band 12 x 2 x 18 tab
                        # that clipped the teeth (docstring defect 2). Kept
                        # only so the history reads; create_pawl() no longer
                        # consumes it.

# Release EARS (2026-09-23, replaces RELEASE_TAB). Two wings at the pawl's free
# end, OUTSIDE the rack's X width, so no pose of the pawl can put them over a
# tooth. See docstring defect 2 for the options measured and rejected.
TAB_X_CLEAR = 1.0       # DECISION  ear inner edge beyond the rack side face
TAB_PROUD = 8.0         # DECISION  ear reach beyond the carrier's side face --
                        #           the finger / ganged-carrier press pad
TAB_H = 8.0             # DECISION  ear height (Z), from the leaf's free end
TAB_X_IN = RACK_W / 2 + TAB_X_CLEAR          # DERIVED 13.0 (pawl-local |x|)
TAB_X_OUT = CARRIER_W / 2 + TAB_PROUD        # DERIVED 25.0
assert TAB_X_IN > LEAF_W / 2, "ear must start outboard of the leaf"
assert TAB_X_OUT > TAB_X_IN + 4.0, "ear press pad too narrow for a finger"

# --------------------------------------- A1 mini split (2026-09-07, REPLAN 4)
SEG_TEETH = 12                       # DECISION  12 + 12: both segments equal,
                                     #           both far inside the 180 bed
Z_SPLIT = SEG_TEETH * PITCH          # DERIVED   144.0 -- ON a pitch boundary,
                                     #           THE seam law (docstring)
TENON_W = 14.0                       # DECISION  key width (X); 4.9 mm mortise
                                     #           walls remain each side
TENON_T = 6.0                        # DECISION  key thickness (Y); 1.9 mm
                                     #           spine walls remain -- Y is the
                                     #           critical registration axis
TENON_H = 16.0                       # DECISION  key engagement depth (Z)
SPLICE_CLEAR = 0.10                  # DECISION  per side, deliberately snug:
                                     #           file to fit; see docstring
MORTISE_HEADROOM = 0.6               # DECISION  butt faces meet, tenon never
                                     #           bottoms in the pocket
SPLICE_SCREW_DZ = (4.5, 11.5)        # DECISION  M3 cross-screw heights above
                                     #           the seam, inside the tenon

# G0: the seam law itself. If Z_SPLIT ever stops being a pitch multiple the
# pawl meets a partial tooth at the seam and the whole scheme is void.
assert N_TEETH == 2 * SEG_TEETH, (
    f"split {SEG_TEETH}+{SEG_TEETH} does not cover {N_TEETH} teeth")
assert abs(Z_SPLIT - round(Z_SPLIT / PITCH) * PITCH) < 1e-9, (
    f"seam at {Z_SPLIT} is not on a tooth-pitch boundary (pitch {PITCH})")

# G1: the Y-registration budget. Worst-case seam step (both fits at limit) must
# stay inside the pawl's own depth clearance or the pawl bottoms on the root
# short of the ledge on one side of the seam.
assert 2 * SPLICE_CLEAR < DEPTH - PAWL_TOOTH_D, (
    f"seam Y-step budget 2*{SPLICE_CLEAR} not inside pawl depth clearance "
    f"{DEPTH - PAWL_TOOTH_D:.2f}")

# Screws live inside the tenon with edge distance; walls stay printable.
assert max(SPLICE_SCREW_DZ) + M3_CLEAR / 2 < TENON_H - 1.0
assert min(SPLICE_SCREW_DZ) - M3_CLEAR / 2 > 1.0
assert (RACK_W - TENON_W) / 2 - SPLICE_CLEAR >= 2.0     # mortise X walls, 4.9
assert (RACK_T - TENON_T) / 2 - SPLICE_CLEAR >= 1.5     # spine Y walls, 1.9


def _tooth_profile():
    """One rack tooth as a closed polygon in the YZ plane, extruded along X.

    Traced upward from the root: ramp out to the tip, horizontal ledge back in,
    then vertically up the root to where the next ramp starts. Built from raw
    topology rather than a sketch builder so it carries no builder state.
    """
    y0, y1 = RACK_T, RACK_T + DEPTH
    pts = [
        Vector(0, y0, 0.0),                   # root, bottom of the ramp
        Vector(0, y1, RAMP_H - TIP_LAND),     # ramp reaches full depth
        Vector(0, y1, RAMP_H),                # vertical land -> square tip
        Vector(0, y0, RAMP_H),                # ledge -- load face, pointing UP
        Vector(0, y0, PITCH),                 # up the root to the next period
    ]
    return Solid.extrude(Face(Wire.make_polygon(pts, close=True)),
                         Vector(RACK_W, 0, 0))


def _mortise_gable():
    """The mortise's 45-degree roof, as an extruded wedge to SUBTRACT.

    Printed seam-face-down the pocket points up; a flat ceiling would be a
    14 x 6 mm 90-degree bridge. Two 45-degree planes meeting in a ridge along
    X print supportless (the ridge itself is a near-zero-width bridge).
    """
    mw = TENON_W + 2 * SPLICE_CLEAR
    y_lo = RACK_T / 2 - (TENON_T / 2 + SPLICE_CLEAR)
    y_hi = RACK_T / 2 + (TENON_T / 2 + SPLICE_CLEAR)
    z0 = TENON_H + MORTISE_HEADROOM
    apex = z0 + (y_hi - y_lo) / 2            # exactly 45 degrees
    x0 = RACK_W / 2 - mw / 2
    pts = [Vector(x0, y_lo, z0), Vector(x0, y_hi, z0),
           Vector(x0, (y_lo + y_hi) / 2, apex)]
    return Solid.extrude(Face(Wire.make_polygon(pts, close=True)),
                         Vector(mw, 0, 0))


def create_rack_lower():
    """Bottom segment: teeth 0..11, the base flange, and the tenon key.

    Bolts to the waist deck exactly as the monolith did. Prints upright on its
    own flange -- the print orientation the tooth geometry was designed for.
    """
    with BuildPart() as part:
        # spine, up to the seam
        Box(RACK_W, RACK_T, Z_SPLIT, align=(Align.MIN, Align.MIN, Align.MIN))

        # teeth 0..SEG_TEETH-1
        for n in range(SEG_TEETH):
            add(_tooth_profile().moved(Location((0, 0, n * PITCH))))

        # base flange
        with Locations((RACK_W / 2, RACK_T / 2, 0)):
            Box(FOOT_W, FOOT_D, FOOT_T, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # deck bolts, and the empty jack pattern beside them
        for dx, dy, dia in (
            (FOOT_BOLT_DX, FOOT_BOLT_DY, M4_CLEAR),
            (JACK_BOLT_DX, JACK_BOLT_DY, M3_CLEAR),
        ):
            for sx in (-1, 1):
                for sy in (-1, 1):
                    with Locations((RACK_W / 2 + sx * dx, RACK_T / 2 + sy * dy, 0)):
                        Cylinder(radius=dia / 2, height=FOOT_T * 3,
                                 align=(Align.CENTER, Align.CENTER, Align.MIN),
                                 mode=Mode.SUBTRACT)

        # the tenon key, centred in the spine section
        with Locations((RACK_W / 2, RACK_T / 2, Z_SPLIT)):
            Box(TENON_W, TENON_T, TENON_H,
                align=(Align.CENTER, Align.CENTER, Align.MIN))

        # cross-screw pilots (M3 self-tap threads the tenon)
        for dz in SPLICE_SCREW_DZ:
            with Locations((RACK_W / 2, RACK_T / 2, Z_SPLIT + dz)):
                Cylinder(radius=M3_PILOT / 2, height=RACK_W * 2,
                         rotation=(0, 90, 0), mode=Mode.SUBTRACT)

    return part.part


def create_rack_upper():
    """Top segment, in its own PRINT frame: z = 0 is the seam face AND the bed.

    Teeth 12..23 of the assembled rack. Mortise + gabled roof open at z = 0;
    M3 clearance holes cross both mortise walls. Place at z = Z_SPLIT to
    assemble. Prints seam-face-down WITH A BRIM (bed contact ~151 mm2 -- the
    spine section minus the mortise opening -- on a 144 mm column).
    """
    with BuildPart() as part:
        Box(RACK_W, RACK_T, RACK_H - Z_SPLIT,
            align=(Align.MIN, Align.MIN, Align.MIN))

        for n in range(N_TEETH - SEG_TEETH):
            add(_tooth_profile().moved(Location((0, 0, n * PITCH))))

        # mortise pocket
        with Locations((RACK_W / 2, RACK_T / 2, 0)):
            Box(TENON_W + 2 * SPLICE_CLEAR, TENON_T + 2 * SPLICE_CLEAR,
                TENON_H + MORTISE_HEADROOM,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT)
        add(_mortise_gable(), mode=Mode.SUBTRACT)

        # cross-screw clearance through both mortise walls
        for dz in SPLICE_SCREW_DZ:
            with Locations((RACK_W / 2, RACK_T / 2, dz)):
                Cylinder(radius=M3_CLEAR / 2, height=RACK_W * 2,
                         rotation=(0, 90, 0), mode=Mode.SUBTRACT)

    return part.part


def create_rack():
    """The assembled rack: both segments in place, fused. Drop-in for every
    downstream consumer of spine_rack.step (assembly, marks, balance, sim) --
    same envelope, same teeth, same flange; only the internal joint differs.
    NOT printable as one piece; print create_rack_lower / create_rack_upper.
    """
    return create_rack_lower() + create_rack_upper().moved(Location((0, 0, Z_SPLIT)))


def _create_rack_monolith():
    """The pre-split rack, kept as the GEOMETRIC REFERENCE the seam gates
    subtract against. 288 mm tall -- exceeds the A1 mini in every orientation.
    Never exported for print."""
    with BuildPart() as part:
        Box(RACK_W, RACK_T, RACK_H, align=(Align.MIN, Align.MIN, Align.MIN))
        for n in range(N_TEETH):
            add(_tooth_profile().moved(Location((0, 0, n * PITCH))))
        with Locations((RACK_W / 2, RACK_T / 2, 0)):
            Box(FOOT_W, FOOT_D, FOOT_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
        for dx, dy, dia in (
            (FOOT_BOLT_DX, FOOT_BOLT_DY, M4_CLEAR),
            (JACK_BOLT_DX, JACK_BOLT_DY, M3_CLEAR),
        ):
            for sx in (-1, 1):
                for sy in (-1, 1):
                    with Locations((RACK_W / 2 + sx * dx, RACK_T / 2 + sy * dy, 0)):
                        Cylinder(radius=dia / 2, height=FOOT_T * 3,
                                 align=(Align.CENTER, Align.CENTER, Align.MIN),
                                 mode=Mode.SUBTRACT)
    return part.part


def create_pawl(ears=True):
    """Sprung pawl. Bolts inside the chest rear wall, rides the rack.

    The leaf is horizontal in the print (its bending plane is the print's XY),
    so it flexes along extrusions rather than peeling layers apart -- the one
    orientation rule that matters for a printed spring.

    Print pose: carrier back face (pawl-local y = 0) on the bed -- see
    pawl_print_pose(). Every feature, the ears included, is an extrusion standing
    on that face or on the carrier, so nothing overhangs.

    ears=False gives the bare carrier + leaf + tooth: the gates use it as the
    reference that proves the ears never lead a contact.
    """
    with BuildPart() as part:
        # carrier block that bolts to the chest
        Box(CARRIER_W, CARRIER_T, CARRIER_H,
            align=(Align.CENTER, Align.MIN, Align.MIN))
        for sx in (-1, 1):
            with Locations((sx * 12.0, 0, CARRIER_H - 10.0)):
                Cylinder(radius=M3_CLEAR / 2, height=CARRIER_T * 3,
                         rotation=(90, 0, 0), mode=Mode.SUBTRACT)

        # cantilever leaf, rooted at the top of the carrier, reaching down
        with Locations((0, CARRIER_T, CARRIER_H - LEAF_L)):
            Box(LEAF_W, LEAF_T, LEAF_L,
                align=(Align.CENTER, Align.MIN, Align.MIN))

        # the tooth at the free end
        with Locations((0, CARRIER_T + LEAF_T, CARRIER_H - LEAF_L)):
            Box(LEAF_W, PAWL_TOOTH_D, PAWL_TOOTH_H,
                align=(Align.CENTER, Align.MIN, Align.MIN))

        # release ears -- press toward the chest (+Y world) to free it. Also
        # the grip for the future ganged carrier / a servo horn if the empty
        # jack option is ever populated. (The 2026-08 in-band tab that lived
        # here clipped teeth n+1 and n+2 -- docstring defect 2.)
        if ears:
            z0 = CARRIER_H - LEAF_L
            for sx in (-1, 1):
                # bridge over the tooth band: stays in the LEAF's y band, i.e.
                # outboard of the tooth tips, exactly where the leaf already is
                with Locations((sx * (LEAF_W / 2 + TAB_X_IN) / 2, CARRIER_T, z0)):
                    Box(TAB_X_IN - LEAF_W / 2, LEAF_T, TAB_H,
                        align=(Align.CENTER, Align.MIN, Align.MIN))
                # the ear: clear of the rack in X, so it may reach as deep as
                # the pawl tooth, and it stands on the bed (y = 0) in print
                with Locations((sx * (TAB_X_IN + TAB_X_OUT) / 2, 0, z0)):
                    Box(TAB_X_OUT - TAB_X_IN, CARRIER_T + LEAF_T + PAWL_TOOTH_D,
                        TAB_H, align=(Align.CENTER, Align.MIN, Align.MIN))

    return part.part


def pawl_print_pose(pawl):
    """The pawl as it prints: carrier back (local y = 0) down on the bed."""
    p = pawl.moved(Rotation(90, 0, 0))          # local +y -> print +z
    return p.moved(Location((0, 0, -p.bounding_box().min.Z)))


def pawl_engaged_location(n, deflect=0.0):
    """Location seating the pawl tooth in notch n; +deflect pushes it out (+Y).

    THE seat offset includes CARRIER_T. The 2026-08 engaged view omitted it
    and buried the pawl 10 mm inside the rack (9617.147 mm3, measured) --
    every gate and view now comes through here so the mistake cannot recur.
    """
    seat_z = n * PITCH + RAMP_H
    return (Location((RACK_W / 2,
                      RACK_T + DEPTH + LEAF_T + CARRIER_T + deflect,
                      seat_z - (CARRIER_H - LEAF_L)))
            * Rotation(0, 0, 180))


def _vol(shape):
    """Volume of a boolean result that may be None/empty."""
    if shape is None:
        return 0.0
    try:
        return shape.volume
    except Exception:
        return 0.0


def _report(name, shape, extra=""):
    bb = shape.bounding_box()
    print(f"{name:14s} {bb.size.X:6.1f} x {bb.size.Y:6.1f} x {bb.size.Z:6.1f} mm   "
          f"{shape.volume / 1000:7.1f} cm3   PETG ~{shape.volume / 1000 * 0.953:5.0f} g"
          f"   solids {len(shape.solids())}{extra}")


if __name__ == "__main__":
    from partcheck import check

    out = Path(__file__).parent / "output"
    out.mkdir(exist_ok=True)
    evidence = Path(__file__).parent.parent.parent / "docs/evidence"
    evidence.mkdir(parents=True, exist_ok=True)

    lower = create_rack_lower()
    upper = create_rack_upper()
    upper_placed = upper.moved(Location((0, 0, Z_SPLIT)))
    rack = lower + upper_placed          # the assembled, fused rack
    reference = _create_rack_monolith()
    pawl = create_pawl()

    # printable segments + the assembled rack downstream consumers import
    for nm, sh in (("rack_lower", lower), ("rack_upper", upper),
                   ("rack", rack), ("pawl", pawl)):
        export_stl(sh, str(out / f"spine_{nm}.stl"))
        export_step(sh, str(out / f"spine_{nm}.step"))

    print(f"stroke {STROKE:.0f} mm + {ENGAGE:.0f} engagement, "
          f"{N_TEETH} teeth at {PITCH:.0f} mm pitch, "
          f"split {SEG_TEETH}+{SEG_TEETH} at z = {Z_SPLIT:.0f}\n")
    _report("rack (asm)", rack)
    _report("rack_lower", lower)
    _report("rack_upper", upper)
    _report("pawl", pawl)

    # --- the numbers that decide whether this works ------------------------
    E = 1700.0                       # PETG, MPa
    I = LEAF_W * LEAF_T ** 3 / 12.0
    F = 3 * E * I * DEPTH / LEAF_L ** 3
    sigma = 3 * E * DEPTH * LEAF_T / (2 * LEAF_L ** 2)
    print(f"\nleaf spring at full {DEPTH:.1f} mm ride-over:")
    print(f"  detent force   {F:5.2f} N")
    print(f"  fibre stress   {sigma:5.2f} MPa   SF {25.0 / sigma:.2f} vs PETG 25")
    print(f"  ramp           {RAMP_DEG:.1f} deg from horizontal "
          f"({90 - RAMP_DEG:.1f} from vertical -- prints unsupported)")
    print(f"  worst settle   {PITCH:.0f} mm (one tooth)")
    print(f"\nchest cluster ~1.54 kg = 15.1 N; two arms -> 7.5 N each")
    print(f"press strokes for {STROKE:.0f} mm at a 175 mm arm stroke: "
          f"{STROKE / 175.0:.1f}")

    # The load path, which is the whole reason the ledge is horizontal: a flat
    # face generates no radial component, so the chest's weight cannot cam the
    # pawl out of its notch no matter how heavy the chest gets.
    bearing = PAWL_TOOTH_D * LEAF_W
    print(f"\npawl seated on a tooth ledge:")
    print(f"  bearing area   {bearing:.0f} mm2 -> {15.1 / bearing:.2f} MPa at 15.1 N")
    print(f"  cam-out force  0.00 N (ledge is horizontal, by design)")
    print(f"  holds          {25.0 * bearing / 1000 * 1000 / 9.81:.0f} kgf before "
          f"the tooth yields")

    # ========================== SEAM GATES =================================
    print(f"\n--- seam gates (joint at z = {Z_SPLIT:.0f} = tooth {SEG_TEETH} "
          f"root plane) ---")

    # G2: the segments never exceed the monolith's envelope -- nothing new
    # sticks out anywhere for the pawl (or the chest guide) to catch.
    excess = _vol(rack - reference)
    assert excess < 1e-3, f"segments exceed the monolith by {excess:.4f} mm3"
    print(f"  G2 envelope     union - monolith = {excess:.4f} mm3")

    # G3: nothing is MISSING in the tooth envelope. The joint's voids
    # (clearance shell, headroom, gable, screw holes) all live in the spine
    # core, y <= 8.1; the band the pawl touches must be bit-identical.
    missing = reference - rack
    tooth_zone = Box(1000, DEPTH + 2.5, 1000,
                     align=(Align.CENTER, Align.MIN, Align.CENTER)
                     ).moved(Location((0, RACK_T - 0.5, 0)))
    lost = _vol(missing & tooth_zone)
    assert lost < 1e-3, f"tooth envelope lost {lost:.4f} mm3 at the seam"
    print(f"  G3 teeth        monolith - union in tooth band = {lost:.4f} mm3 "
          f"(total joint void {_vol(missing):.0f} mm3, all in the spine core)")

    # G4: the butt faces actually meet -- a fuse of two touching solids is ONE
    # solid; two solids here means a modelled gap at the seam.
    assert len(rack.solids()) == 1, (
        f"assembled rack is {len(rack.solids())} solids -- seam gap")
    print(f"  G4 closure      assembled rack fuses to 1 solid")

    # G5/G6: seat the ACTUAL, WHOLE pawl (ears included) FULLY at the last
    # lower notch (11), the first upper notch (12) and two mid-segment notches
    # (5, 18). ZERO interference against BOTH the assembled rack and the
    # monolith. (Until 2026-09-23 these gates asserted PARITY, 81.120 ==
    # 81.120 mm3, because the old release tab clipped every tooth -- docstring
    # defect 2, now resolved; the gate is ZERO so it can never come back.)
    for n in (5, SEG_TEETH - 1, SEG_TEETH, N_TEETH - 6):
        p = pawl.moved(pawl_engaged_location(n))
        v_asm, v_ref = _vol(p & rack), _vol(p & reference)
        assert v_asm < 1e-3 and v_ref < 1e-3, (
            f"seated pawl hits the rack at tooth {n}: assembled {v_asm:.4f}, "
            f"monolith {v_ref:.4f} mm3 -- the tab clash is back")
        drop = _vol(p.moved(Location((0, 0, -1.0))) & rack)
        assert drop > 1.0, f"pawl does not catch tooth {n}: {drop:.4f} mm3"
        print(f"  G5/G6 tooth {n:2d}  whole pawl at full seat: assembled "
              f"{v_asm:.3f}, monolith {v_ref:.3f} mm3; 1 mm drop catches "
              f"({drop:.1f} mm3)")

    # G7: THE SWEPT-INTERFERENCE ASSERT for the moving pair. Ride the pawl,
    # deflected past its own tooth depth (+0.05 running clearance), across
    # two full pitches spanning the seam. Any protrusion at the joint --
    # a proud screw head boss, a swollen clearance shell, a mis-placed tenon
    # -- would strike here.
    steps = 49
    worst = 0.0
    for i in range(steps):
        dz = i * 0.5                                    # tooth 11 -> tooth 13
        p = (pawl.moved(pawl_engaged_location(SEG_TEETH - 1,
                                              deflect=PAWL_TOOTH_D + 0.05))
             .moved(Location((0, 0, dz))))
        v = _vol(p & rack)
        worst = max(worst, v)
        assert v < 1e-3, f"deflected pawl hits seam region at dz={dz}: {v:.4f}"
    print(f"  G7 sweep        deflected pawl x{steps} poses over 24 mm across "
          f"the seam: worst {worst:.4f} mm3")

    # ========================== PAWL / RELEASE-EAR GATES ====================
    # Docstring defect 2 (the tab clash) and its resolution. Every number here
    # is re-measured on every build.
    print(f"\n--- pawl gates (release ears, defect 2 resolution) ---")
    bare = create_pawl(ears=False)
    win = Box(1000, 1000, 64, align=(Align.CENTER, Align.CENTER, Align.MIN)
              ).moved(Location((0, 0, Z_SPLIT - 24.0)))
    rack_w = rack & win                  # local window: the sweeps stay fast

    def _pose(shape, n, deflect=0.0, dz=0.0):
        return shape.moved(pawl_engaged_location(n, deflect=deflect)
                           ).moved(Location((0, 0, dz)))

    def _min_clear_deflect(shape, n, dz, target):
        """Smallest +Y deflection at which `shape` clears `target` (bisection,
        18 halvings of 5 mm = 0.00002 mm)."""
        if _vol(_pose(shape, n, 0.0, dz) & target) < 1e-6:
            return 0.0
        lo, hi = 0.0, 5.0
        for _ in range(18):
            mid = (lo + hi) / 2
            if _vol(_pose(shape, n, mid, dz) & target) > 1e-6:
                lo = mid
            else:
                hi = mid
        return hi

    # P1: resting stand-off and EFFECTIVE ENGAGEMENT. Was 2.000 mm stand-off
    # -> 1.700 mm engagement with the old tab; must now be the design depth.
    hi = _min_clear_deflect(pawl, SEG_TEETH, 0.0, rack_w)
    eff = PAWL_TOOTH_D - hi
    assert hi < 1e-3 and abs(eff - PAWL_TOOTH_D) < 1e-3, (
        f"pawl rests {hi:.4f} mm out of seat -> engagement {eff:.3f} mm, "
        f"designed {PAWL_TOOTH_D} (docstring defect 2)")
    print(f"  P1 engagement   resting stand-off {hi:.4f} mm -> effective "
          f"engagement {eff:.3f} mm (designed {PAWL_TOOTH_D}; was 1.700)")

    # P2: through the ratchet stroke the EARS NEVER LEAD A CONTACT. Ride the
    # pawl up one full pitch across the seam (tooth 11 -> 12, 0.5 mm steps);
    # at every step the whole pawl needs exactly the deflection the bare
    # carrier+leaf+tooth needs -- i.e. the tooth alone decides the ride-over.
    worst_ride = 0.0
    for i in range(25):
        dz = i * 0.5
        d_whole = _min_clear_deflect(pawl, SEG_TEETH - 1, dz, rack_w)
        d_bare = _min_clear_deflect(bare, SEG_TEETH - 1, dz, rack_w)
        worst_ride = max(worst_ride, d_whole - d_bare)
        assert d_whole - d_bare < 1e-3, (
            f"ears lead the ride-over at dz={dz}: need {d_whole:.4f} vs "
            f"tooth-only {d_bare:.4f} mm")
    print(f"  P2 ride-over    x25 poses over one pitch across the seam: ears "
          f"add {worst_ride:.4f} mm to the needed deflection (tooth decides)")

    # P3: THE RELEASE MOTION. Pull straight out (+Y) from full seat at tooth
    # 12 to full release (tooth depth + 0.05), then lower the chest across the
    # seam two full pitches with the pawl held out. 0 mm3 at every pose.
    release = PAWL_TOOTH_D + 0.05
    worst_rel = 0.0
    for i in range(21):
        v = _vol(_pose(pawl, SEG_TEETH, release * i / 20) & rack_w)
        worst_rel = max(worst_rel, v)
        assert v < 1e-3, f"pull-out hits at deflect {release * i / 20:.3f}: {v:.4f}"
    for i in range(49):
        v = _vol(_pose(pawl, SEG_TEETH, release, -i * 0.5) & rack_w)
        worst_rel = max(worst_rel, v)
        assert v < 1e-3, f"released descent hits at dz={-i * 0.5}: {v:.4f}"
    print(f"  P3 release      pull-out x21 (0 -> {release:.2f} mm) + lowered "
          f"x49 over 24 mm across the seam: worst {worst_rel:.4f} mm3")

    # P4: the ears cannot see a tooth -- static X clearance to the rack side
    # faces, the same in every pose because the pawl never moves in X.
    ear_gap = TAB_X_IN - RACK_W / 2
    assert ear_gap >= 0.5, f"ear only {ear_gap:.2f} mm off the rack side face"
    # ... and the ears add nothing at the flange end of the stroke. (The
    # CARRIER itself hits the base flange at teeth 0 and 1 -- pre-existing,
    # reported, not an ear defect: see FOLLOWUPS in defect 2.)
    for n in (0, 1):
        dv = _vol(_pose(pawl, n) & rack) - _vol(_pose(bare, n) & rack)
        assert abs(dv) < 1e-3, f"ears add {dv:.3f} mm3 at tooth {n}"
    # reachability: the press face is the ears' rack-side face, world y =
    # RACK_T + (DEPTH - PAWL_TOOTH_D), i.e. flush with the pawl tooth face
    press_y = RACK_T + DEPTH - PAWL_TOOTH_D
    pad = (TAB_X_OUT - TAB_X_IN) * TAB_H
    pad_out = (TAB_X_OUT - CARRIER_W / 2) * TAB_H
    print(f"  P4 ears         {TAB_X_IN - RACK_W / 2:.1f} mm X-clear of each rack "
          f"side face; press face at world y = {press_y:.1f} (0.3 mm off the "
          f"spine plane), {pad:.0f} mm2 per ear, {pad_out:.0f} mm2 of it "
          f"outboard of the carrier; press +Y by {release:.2f} mm to release; "
          f"ears add 0.000 mm3 at teeth 0/1")

    # ========================== A1 MINI BED GATES ==========================
    # Gate against interface_constants' A1 mini bed, NOT partcheck's fits_bed
    # (partcheck still carries the H2C's 330x320x325 -- stale, flagged).
    # No diagonal placement needed for either segment, so BED_DIAGONAL_MAX
    # (245 NOMINAL, never design at it) is deliberately not consumed.
    bed = sorted((BED_X, BED_Y, BED_Z))
    print(f"\n--- {PRINTER_MODEL} bed gates ({BED_X:.0f} x {BED_Y:.0f} x "
          f"{BED_Z:.0f}) ---")
    for nm, sh in (("lower", lower), ("upper", upper)):
        bb = sh.bounding_box()
        dims = sorted((bb.size.X, bb.size.Y, bb.size.Z))
        assert all(d <= b for d, b in zip(dims, bed)), (
            f"spine_rack_{nm} {dims} does not fit the {PRINTER_MODEL} bed {bed}")
        print(f"  {nm:5s} {bb.size.X:5.1f} x {bb.size.Y:5.1f} x {bb.size.Z:5.1f}"
              f"  tallest-axis margin {bed[2] - dims[2]:5.1f} mm, axis-aligned, "
              f"upright")

    # ========================== PARTCHECK (print orientation) ==============
    # Both segments are AUTHORED in print orientation: upright, teeth
    # sideways; lower on its flange, upper seam-face-down (z=0 IS its bed).
    rl = check(lower, "spine_rack_lower", out_dir=str(out), material="PETG")
    ru = check(upper, "spine_rack_upper", out_dir=str(out), material="PETG")
    for nm, r in (("lower", rl), ("upper", ru)):
        assert r["solids"] == 1 and r["bodies"] == 1, f"{nm}: not one body"
        assert r["watertight"] and r["winding_ok"], f"{nm}: mesh integrity"
        # measured 2026-09-07: lower 0.0%, upper 0.0% support (gable + ramps
        # all steeper than 45); gate leaves headroom for tessellation noise
        assert r["support_frac"] < 0.02, (
            f"{nm}: support {r['support_frac']:.1%} -- a joint face went "
            f"unprintable")
        # thin samples are the known square-tip corner slivers, never a wall
        if r.get("below_two_extrusions_frac", 0) > 0:
            assert r["thin_is_edge_sliver"], f"{nm}: REAL thin wall appeared"
    # lower stands on its 56 x 34 flange
    assert rl["overhang_detail"]["bed_contact_mm2"] >= 150.0
    # upper: spine section minus mortise opening -- measured 152 mm2
    # (2026-09-07), i.e. AT partcheck's 150 shear-off floor. That is why
    # the docstring mandates a BRIM for this segment; the gate holds the
    # geometry to what was measured so it cannot silently shrink further.
    assert ru["overhang_detail"]["bed_contact_mm2"] >= 140.0, (
        "upper bed contact shrank below the measured ~150 mm2 -- reprofile "
        "the mortise or add tabs")

    # pawl, in its print pose (carrier back on the bed, ears standing on it)
    pawl_print = pawl_print_pose(pawl)
    export_step(pawl_print, str(out / "spine_pawl_print.step"))
    rp = check(pawl_print, "spine_pawl_print", out_dir=str(out), material="PETG")
    assert rp["solids"] == 1 and rp["bodies"] == 1, "pawl: not one body"
    assert rp["watertight"] and rp["winding_ok"], "pawl: mesh integrity"
    assert rp["support_frac"] < 0.02, (
        f"pawl: support {rp['support_frac']:.1%} -- an ear went unprintable")
    if rp.get("below_two_extrusions_frac", 0) > 0:
        assert rp["thin_is_edge_sliver"], "pawl: REAL thin wall appeared"
    pb = pawl_print.bounding_box()
    print(f"  pawl print      {pb.size.X:.1f} x {pb.size.Y:.1f} x {pb.size.Z:.1f}"
          f" carrier-back-down; support {rp['support_frac']:.1%}; bed "
          f"contact {rp['overhang_detail']['bed_contact_mm2']:.0f} mm2")

    # ========================== EVIDENCE RENDERS ===========================
    import subprocess
    hero = Path(__file__).parent.parent.parent / "edu/tools/hero_render.py"

    # segments, joint features highlighted
    for nm, sh, hl, tag in (
        ("spine_rack_lower", lower, f"z:{Z_SPLIT - 0.1:.1f}:{Z_SPLIT + TENON_H + 0.1:.1f}",
         "spine rack LOWER -- 12 teeth, flange, tenon key (A1 mini)"),
        ("spine_rack_upper", upper, f"y:0:8.2,z:-0.1:{TENON_H + MORTISE_HEADROOM + 3.3:.1f}",
         "spine rack UPPER -- 12 teeth, mortise + gable, seam face at z=0"),
    ):
        vstep = out / f"{nm}_hero_view.step"
        export_step(sh, str(vstep))
        subprocess.run([sys.executable, str(hero), str(vstep),
                        "-o", str(evidence / f"{nm}_hero.png"),
                        "--highlight", hl, "--tag", tag], check=True)

    # the claim that matters: pawl engaged on tooth 12, the first tooth ABOVE
    # the seam, at the measured resting deflection -- a window around the
    # joint so the seam is legible at render scale
    window = Box(1000, 1000, 58, align=(Align.CENTER, Align.CENTER, Align.MIN)
                 ).moved(Location((0, 0, Z_SPLIT - 26.0)))
    p_rest = pawl.moved(pawl_engaged_location(SEG_TEETH, deflect=hi))
    closeup = Compound(children=[copy.copy(rack & window),
                                 copy.copy(p_rest & window)])
    vstep = out / "spine_rack_seam_engaged_view.step"
    export_step(closeup, str(vstep))
    subprocess.run([sys.executable, str(hero), str(vstep),
                    "-o", str(evidence / "spine_rack_seam_engaged_hero.png"),
                    "--highlight", f"z:{Z_SPLIT - 3.0:.1f}:{Z_SPLIT + 3.0:.1f}",
                    "--tag", "seam closeup -- pawl engaged on tooth 12, "
                             "first tooth above the joint"], check=True)

    # the defect-2 fix: pawl at FULL seat (deflect 0) on tooth 12, ears lit
    fix = Compound(children=[copy.copy(rack & window),
                             copy.copy(pawl.moved(pawl_engaged_location(SEG_TEETH))
                                       & window)])
    vstep = out / "spine_pawl_tab_fix_view.step"
    export_step(fix, str(vstep))
    subprocess.run([sys.executable, str(hero), str(vstep),
                    "-o", str(evidence / "spine_pawl_tab_fix.png"),
                    "--highlight", "x:-30:-0.5,x:24.5:40",
                    "--tag", "pawl FULLY seated on tooth 12: 0.000 mm3, "
                             "engagement 3.700 -- release ears outside the "
                             "rack width"], check=True)

    # --- engaged view (interactive) ----------------------------------------
    import shutil
    asm = out / "spine_lock_asm"
    if asm.exists():
        shutil.rmtree(asm)
    asm.mkdir()
    export_stl(lower, str(asm / "01_rack_lower.stl"))
    export_stl(upper_placed, str(asm / "02_rack_upper.stl"))
    # seat the pawl half way up, at the measured resting deflection -- 0.000
    # since the 2026-09-23 ear fix (it was 2.000 under the old tab clash)
    export_stl(pawl.moved(pawl_engaged_location(SEG_TEETH, deflect=hi)),
               str(asm / "03_pawl_ENGAGED.stl"))
    html = out / "spine_lock.html"
    subprocess.run([sys.executable,
                    str(Path(__file__).parent.parent.parent / "edu/tools/stl_viewer.py"),
                    str(asm / "01_rack_lower.stl"), str(asm / "02_rack_upper.stl"),
                    str(asm / "03_pawl_ENGAGED.stl"),
                    "-o", str(html),
                    "-t", "Alpha Centauri — hand-driven spine lock (2 segments)"],
                   check=True)

    print("\nALL GATES GREEN -- spine rack split 12+12 at the tooth-12 root "
          "plane; seam adds nothing, removes nothing the pawl can feel; both "
          "segments upright on the A1 mini (upper WITH BRIM); stroke kept at "
          f"{STROKE:.0f} mm (the diagonal fallback would have cost ~50 mm)")
