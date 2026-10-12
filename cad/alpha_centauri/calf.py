"""Alpha Centauri — calf (L3), slender closed section, non-handed (build123d).

    edu/.cadenv/bin/python cad/alpha_centauri/calf.py

WHY THIS PART IS SLENDER AND THE THIGH IS NOT
---------------------------------------------
Put the foot contact ON the calf axis -- which the spherical foot does by
construction -- and a lateral foot force has ZERO moment arm about that axis.
The calf therefore carries no torsion at all, while the thigh carries all of it.
That single fact is why the thigh must be a fat closed box and the calf can be a
thin one.

And the calf is where mass actually costs something. Swing inertia goes as r^2,
and the calf sits 7-8x further from the hip-pitch axis than the thigh's own
centroid: it is 45-75% of the leg's swing inertia in every variant modelled.
A gram saved here is worth roughly seven saved on the thigh, which is the whole
reason the analysis said to stop optimising the thigh and start optimising this.

Bending requirement is 306 mm^3 of section modulus. The section below delivers
about 680 -- 2.2x -- at 2.5 mm walls. Do not add material; it is not free here.

THE FORK IS ON THE CALF
-----------------------
The calf straddles the thigh, not the other way round: two lugs outside the
thigh's cheeks. Both lugs are identical -- same seat bore, same depth -- so this
part is non-handed like the thigh. Handedness lives in which side gets the horn
adapter and which gets the bearing.

THE FOOT IS A SEPARATE PART
---------------------------
Contradicting an earlier plan note that wanted the TPU pad printed integral.
Three reasons it should not be: TPU bonds well to PETG and poorly to the PC/PA-CF
this part may end up in; the pad is the only wear item on the robot and the only
one P3 needs in two durometers; and a TPU stringing failure at hour 9 of a
structural print scraps the calf. So the calf ends in a spherical BOSS and the
foot clamps onto it.

The boss centre sits at FOOT_CENTRE_FROM_KNEE, not at L3. That is not an
adjustment -- it is what makes the contact point land at exactly L3 for every
calf angle across the 38.5 deg working swing. Centre it at L3 instead and the
contact wanders up to 4 mm, which is more than the entire reach headroom.

PRINT ORIENTATION -- ON ITS SIDE, NOT UPRIGHT
---------------------------------------------
Opposite of the thigh, and for one reason: THE BEARING SEATS.

Printed upright (calf axis along Z) the part is a 137 mm tower whose two 22 mm
seats are horizontal holes. A horizontal hole that size droops at the crown, and
a drooped bearing seat is a loose knee -- the one joint where slop turns
straight into foot-placement error. Teardropping it would fix the printing and
ruin the fit, because a teardrop is not a circle.

Laid on its side (seat axis vertical) the seats print as VERTICAL holes, which
is the only kind an FDM machine makes round. The footprint becomes 34 x 137 mm
instead of a tangent line, and the part is 54 mm tall instead of 137 -- low,
wide and stable. The cost is one bridge across the hollow shaft, about 15 mm,
which PETG spans without complaint.

The thigh goes the other way because its cavity is large and its bores are
clearance, not fits. Same reasoning, opposite answer.

Geometry below is authored in the ROBOT frame (knee at origin, calf down +Z).
PRINT_ROT is applied only on export and for the printability check.
"""

import math
from pathlib import Path
import subprocess
import sys

from build123d import (
    Align,
    Axis,
    BuildPart,
    Box,
    Cylinder,
    Location,
    Locations,
    Mode,
    Plane,
    Solid,
    Wire,
    add,
    export_step,
    export_stl,
)

from interface_constants import (
    FOOT_CENTRE_FROM_KNEE,
    FOOT_SPHERE_R,
    L2_THIGH,
    L3_CALF,
)
from thigh import (
    JOURNAL_D,
    END_OVER as THIGH_END_OVER,
    SEC_X as THIGH_SEC_X,
    SEC_Y as THIGH_SEC_Y,
)

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "edu/tools"))

# ------------------------------------------------------------------- section
# Slender: bending only, no torsion. 2.5 mm walls give 2.2x on section modulus.
WALL_C = 2.5
SEC_X = 20.0            # fore-aft -- the bending depth, where it matters
SEC_Y = 14.0            # lateral -- only needs to not buckle

# --------------------------------------------------------------------- lugs
LUG_T = 6.0             # lug thickness; sets the journal bearing width
LUG_GAP = THIGH_SEC_Y + 1.0        # inner span, 1 mm of running clearance
LUG_SPAN = LUG_GAP + 2 * LUG_T     # outer span
LUG_R = 19.0            # lug outline radius about the knee axis
# Retaining bolt circle, OUTSIDE the seat. Both lugs get it, which is what keeps
# the part non-handed: on the driven side these three bolts pull in the horn
# adapter, on the idle side a bearing retainer. Same holes, different insert.
RETAIN_PCD = 27.0
RETAIN_N = 3
M3_CLEAR = 3.4
# The lugs are the part's first layer, and a full circle touches the bed on a
# TANGENT LINE -- partcheck measured 51 mm2 of bed contact for a 140 mm tall
# part, which will shear off the plate. Chopping the lugs to a D gives a real
# footprint, removes mass from the leg's outer end where r^2 is worst, and
# costs nothing structurally: the load runs through the seat, not the rim.
LUG_FLAT_Z = -(LUG_R - 3.0)        # 3 mm of meat below the 22 mm seat

# WHERE THE FORK IS ALLOWED TO CLOSE. The thigh sweeps a cylinder about the knee
# axis of radius sqrt((THIGH_SEC_X/2)^2 + THIGH_END_OVER^2) = 22.3 mm. Anything
# the calf puts inside that radius, between the lugs, is a collision -- and the
# first version's web did exactly that. Converge below it, with margin.
THIGH_SWEEP_R = math.hypot(THIGH_SEC_X / 2, THIGH_END_OVER)
CONVERGE_Z = THIGH_SWEEP_R + 2.5
TAPER_H = 22.0          # loft from the fork span down to the shaft section
SEAT_D = JOURNAL_D      # 22.0 -- same seat as the thigh, takes a 608ZZ
SEAT_DEPTH = 7.0        # 608ZZ width

# ---------------------------------------------------------------- foot boss
BOSS_D = 16.0           # spigot the foot clamps onto
BOSS_L = 14.0
M3_PILOT = 2.6


def create_calf():
    """Knee fork + slender shaft + foot boss, in print orientation.

    Knee axis at the origin, axis along Y. The calf runs down +Z; the foot
    contact point is at z = L3_CALF.
    """
    with BuildPart() as part:
        # --- the two lugs ---------------------------------------------------
        for sy in (-1, 1):
            with Locations((0, sy * (LUG_GAP + LUG_T) / 2, 0)):
                Cylinder(radius=LUG_R, height=LUG_T,
                         rotation=(90, 0, 0), align=Align.CENTER)

        # --- arms: the lugs run down as SEPARATE plates ---------------------
        # They must not join until they are clear of the thigh's swept envelope.
        # Joining them at the knee (which the first version did) put 1.62 cm3 of
        # solid material exactly where the thigh's end overhang lives -- at ZERO
        # knee bend, before any motion. See CONVERGE_Z.
        for sy in (-1, 1):
            with Locations((0, sy * (LUG_GAP + LUG_T) / 2, CONVERGE_Z / 2)):
                Box(SEC_X, LUG_T, CONVERGE_Z, align=Align.CENTER)

        # --- yoke: taper from the fork span down to the shaft section -------
        add(Solid.make_loft([
            Wire.make_rect(SEC_X, LUG_SPAN, Plane.XY.offset(CONVERGE_Z)),
            Wire.make_rect(SEC_X, SEC_Y, Plane.XY.offset(CONVERGE_Z + TAPER_H)),
        ]))

        # --- shaft: slender box down to the foot ----------------------------
        shaft_z0, shaft_z1 = CONVERGE_Z + TAPER_H - 2.0, FOOT_CENTRE_FROM_KNEE
        with Locations((0, 0, (shaft_z0 + shaft_z1) / 2)):
            Box(SEC_X, SEC_Y, shaft_z1 - shaft_z0, align=Align.CENTER)
        # hollow it, stopping short of both ends
        with Locations((0, 0, (shaft_z0 + shaft_z1) / 2)):
            Box(SEC_X - 2 * WALL_C, SEC_Y - 2 * WALL_C,
                shaft_z1 - shaft_z0 - 2 * WALL_C,
                align=Align.CENTER, mode=Mode.SUBTRACT)

        # OPEN THE UPPER WEB. Printed on its side this face is the cavity's
        # ceiling, and a sealed box would trap its own support forever -- there
        # is no way to reach inside a closed calf. Opening it is affordable here
        # and NOT on the thigh, for the same reason the section is slender at
        # all: the calf carries no torsion, so it does not need to be closed.
        #
        # And the face removed is a WEB, not a flange. Fore-aft bending puts its
        # extreme fibres at x = +/-SEC_X/2, which this cut does not touch. It
        # spans exactly the cavity width, so nothing bridges and nothing is
        # trapped: I falls 6802 -> ~6100 mm^4, still 2x the requirement.
        with Locations((0, SEC_Y / 2, (shaft_z0 + shaft_z1) / 2)):
            Box(SEC_X - 2 * WALL_C, SEC_Y, shaft_z1 - shaft_z0 - 2 * WALL_C,
                align=Align.CENTER, mode=Mode.SUBTRACT)

        # --- foot boss ------------------------------------------------------
        # A plain spigot on the calf axis. The FOOT part carries the sphere; the
        # boss only has to locate and retain it.
        with Locations((0, 0, FOOT_CENTRE_FROM_KNEE - BOSS_L / 2)):
            Cylinder(radius=BOSS_D / 2, height=BOSS_L, align=Align.CENTER)
        # cross pilot for the foot's retaining screw
        with Locations((0, 0, FOOT_CENTRE_FROM_KNEE - BOSS_L / 2)):
            Cylinder(radius=M3_PILOT / 2, height=BOSS_D * 2,
                     rotation=(90, 0, 0), mode=Mode.SUBTRACT)

        # --- flat off the lug bottoms so the part has a real first layer ----
        with Locations((0, 0, LUG_FLAT_Z)):
            Box(LUG_R * 4, LUG_SPAN * 2, LUG_R * 2,
                align=(Align.CENTER, Align.CENTER, Align.MAX),
                mode=Mode.SUBTRACT)

        # --- seats, cut last so nothing backfills them ----------------------
        for sy in (-1, 1):
            with Locations((0, sy * (LUG_GAP / 2 + LUG_T - SEAT_DEPTH / 2), 0)):
                Cylinder(radius=SEAT_D / 2, height=SEAT_DEPTH,
                         rotation=(90, 0, 0), align=Align.CENTER,
                         mode=Mode.SUBTRACT)
        # through-hole for the knee shaft
        with Locations((0, 0, 0)):
            Cylinder(radius=4.6, height=LUG_SPAN * 2,
                     rotation=(90, 0, 0), mode=Mode.SUBTRACT)

        # retaining bolts, both lugs, same pattern
        for sy in (-1, 1):
            for i in range(RETAIN_N):
                th = math.radians(90 + 360 * i / RETAIN_N)
                with Locations((RETAIN_PCD / 2 * math.cos(th),
                                sy * (LUG_GAP + LUG_T) / 2,
                                RETAIN_PCD / 2 * math.sin(th))):
                    Cylinder(radius=M3_CLEAR / 2, height=LUG_T * 3,
                             rotation=(90, 0, 0), mode=Mode.SUBTRACT)

        # --- lightening down the shaft --------------------------------------
        for z in (60.0, 85.0, 110.0):
            if z < FOOT_CENTRE_FROM_KNEE - BOSS_L - 6:
                with Locations((0, 0, z)):
                    Cylinder(radius=5.0, height=SEC_Y * 2,
                             rotation=(90, 0, 0), mode=Mode.SUBTRACT)

    return part.part


if __name__ == "__main__":
    from partcheck import check

    out = Path(__file__).parent / "output"
    out.mkdir(exist_ok=True)

    calf = create_calf()
    export_step(calf, str(out / "calf.step"))          # robot frame, for assembly
    # Lay it down: +Y (the seat axis) becomes +Z (the build axis).
    printed = calf.rotate(Axis.X, -90)
    bb = printed.bounding_box()
    printed = printed.moved(Location((0, 0, -bb.min.Z)))
    export_stl(printed, str(out / "calf.stl"))

    # --- the numbers this part exists to satisfy ---------------------------
    b, d, t = SEC_Y, SEC_X, WALL_C
    I = (b * d ** 3 - (b - 2 * t) * (d - 2 * t) ** 3) / 12.0
    Z = I / (d / 2)
    print(f"L3 = {L3_CALF:.5f} mm, section {SEC_X:.1f} x {SEC_Y:.1f}, "
          f"wall {WALL_C:.1f}")
    print(f"\nbending:")
    print(f"  section modulus  {Z:7.0f} mm3   required 306   "
          f"margin {Z/306:.2f}x")
    print(f"\ntorsion: ZERO by construction -- the foot contact lies ON the calf")
    print(f"  axis, so a lateral force has no moment arm about it.")
    print(f"\nfoot:")
    print(f"  sphere radius        {FOOT_SPHERE_R:6.2f} mm")
    print(f"  centre from knee     {FOOT_CENTRE_FROM_KNEE:6.2f} mm")
    print(f"  contact from knee    {FOOT_CENTRE_FROM_KNEE + FOOT_SPHERE_R:6.2f} mm"
          f"   = L3 {L3_CALF:.2f}  "
          f"{'OK' if abs(FOOT_CENTRE_FROM_KNEE + FOOT_SPHERE_R - L3_CALF) < 1e-9 else 'MISMATCH'}")
    print(f"\nfork:")
    print(f"  inner span {LUG_GAP:.1f} over a {THIGH_SEC_Y:.2f} thigh "
          f"({LUG_GAP - THIGH_SEC_Y:.1f} mm running clearance)")
    print(f"  seat {SEAT_D:.1f} x {SEAT_DEPTH:.1f} -- 608ZZ, both lugs identical")

    # --- INTERFERENCE SWEEP -------------------------------------------------
    # partcheck validates one part in isolation and can never catch this. The
    # first fork closed at the knee axis and buried 1.62 cm3 of the thigh at
    # ZERO bend -- it passed every single-part check cleanly. Any joint that
    # moves needs its range swept, not its rest pose spot-checked.
    thigh_step = out / "thigh_shell.step"
    if thigh_step.exists():
        from build123d import import_step
        base = import_step(str(thigh_step)).solids()[0].moved(
            Location((0, 0, -L2_THIGH)))
        print("\nthigh-vs-calf interference across the knee sweep:")
        worst = 0.0
        for bend in (0, 10, 20, 30, 43.23, 55, 70, 85):
            hit = calf & base.rotate(Axis.Y, bend)
            v = 0.0 if hit is None else hit.volume
            worst = max(worst, v)
            print(f"  bend {bend:6.2f} deg -> {v/1000:7.3f} cm3   "
                  f"{'CLEAR' if v < 1e-6 else 'COLLIDE'}")
        assert worst < 1e-6, f"calf hits the thigh: {worst/1000:.3f} cm3"

    # Check the PRINTED pose, not the robot pose -- overhangs and bed contact
    # are meaningless against an orientation the part is never built in.
    check(printed, "calf", out_dir=str(out), material="PETG")

    html = out / "calf.html"
    subprocess.run([sys.executable,
                    str(Path(__file__).parent.parent.parent / "edu/tools/stl_viewer.py"),
                    str(out / "calf.stl"), "-o", str(html),
                    "-t", "Alpha Centauri — calf (L3)"], check=True)
