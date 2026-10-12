"""Alpha Centauri — thigh (L2), closed-section, non-handed (build123d).

    edu/.cadenv/bin/python cad/alpha_centauri/thigh.py

THE ONE STRUCTURAL FACT THAT SETS THIS PART
-------------------------------------------
It is not strength. At full servo stall the worst fibre stress in this section
is ~1.3 MPa against a 25 MPa PETG allowable -- safety factor 19. Adding material
for strength here is wasted mass.

It is TORSION, and it discriminates by 130x. The same outline closed vs open:

    closed box  J = 4*Am^2*t/perimeter = 109,136 mm^4
    open channel J = sum(b*t^3)/3      =     836 mm^4

Under an ordinary walking side load the open section twists 14.6 degrees over
the thigh's length and swings the foot 63.7 mm. Closed: 0.11 deg, 0.33 mm. The
open section's STRESS is fine -- 7 MPa -- which is exactly why a strength check
would have passed it. The section must be CLOSED, and the servo opening must be
shut by a bolted cover that is treated as structural, not cosmetic.

WHY IT IS NON-HANDED
--------------------
Both cheeks carry the SAME large coaxial bore and the SAME bolt circle at each
end. The driven side takes a servo horn; the idle side takes a small bearing
carrier. Handedness lives in that 2 g carrier and in the servo calibration
table, not in this part -- so ONE printed thigh serves all four legs. Dingo
ships separate L/R links; we do not have to.

THE HORN NEVER TAKES A RADIAL LOAD
----------------------------------
A lateral foot force puts ~3.9 kN.mm of splay moment at the knee. Through a
straddle across the clevis that is a ~98 N journal reaction, 0.75 MPa on a
printed bore -- trivial. Through a single-shear horn it is 3.9 kN.mm of bending
on a ~6 mm output shaft. No hobby-class bus servo publishes a radial rating.
The horn transmits TORQUE ONLY; every transverse force goes to the journals.

FRAME AND PRINT ORIENTATION
---------------------------
Defined directly in PRINT orientation: hip-pitch axis at the origin, knee axis
at (0, 0, L2), both axes along Y, part built with the hip end on the bed.

Upright is the only orientation that yields a one-piece closed box with no
bridge: both cheeks become continuous vertical perimeters, the servo cavity is a
vertical pocket, and the two large bores are horizontal holes in vertical walls
-- so they are teardropped. Sagittal bending then runs along the extrusions
rather than across layer lines, though at SF 19 that is a bonus, not the reason.

PRINT-BLOCKED (LAW: unresolved servo height)
--------------------------------------------
SEC_Y derives from SERVO_BODY_HEIGHT, which is UNRESOLVED (35.00 nominal vs
37.80 vendor STEP), and this part will also carry the hip-pitch servo cavity
mirroring the knee one. It is drawn parametrically and gate-checked at BOTH
candidate heights via interface_constants._check(); it must not be printed
until the caliper resolves the height. Same block as the chassis pods and the
hip module.

KNOWN DEFECT (2026-08-01, verification-CONFIRMED, geometry left as-is)
----------------------------------------------------------------------
The UPPER structural-cover bolt pair is cut at z = 149.40 while the part ends
at Z1 = 146.00 -- both upper pilots are cut in air (annulus probe: 0.0 mm3 of
material around each, vs 47.8 mm3 at the lower pair), so the torsion-box cover
currently bolts only at its lower pair, and its top tab overhangs the shell by
10.40 mm. NO clean relocation exists: the only in-envelope band above the
opening is Z1 - (L2 + boss offset 12.0 + 2*CL) = 3.60 mm, and an M3 pilot
(2.6) centred there leaves 0.50 mm ligaments both sides -- the 1.0d
edge-distance floor needs a 5.2 mm band, 1.5d needs 7.8. Every in-part fix
changes the outer envelope (growing END_OVER moves THIGH_SWEEP_R = 22.32 and
cascades into calf CONVERGE_Z, hip BRIDGE_Z0 and the permanent sweep asserts),
so the correction is deferred to the hip-pitch-cavity rework of this part.
Until then the cover's top row must not be drilled or screwed.
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
)

from interface_constants import (
    L2_THIGH,
    SERVO_BODY_HEIGHT,
    SERVO_BODY_LENGTH,
    SERVO_BODY_WIDTH,
    SERVO_POCKET_CLEARANCE,
    WALL,
)

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "edu/tools"))

# ---------------------------------------------------------------- the section
CL = SERVO_POCKET_CLEARANCE / 2.0            # per side
SEC_Y = SERVO_BODY_HEIGHT + 2 * CL + 2 * WALL    # lateral: clevis span, 41.40
SEC_X = SERVO_BODY_WIDTH + 2 * CL + 2 * WALL     # fore-aft: bending depth, 31.12

# Ends run past each axis far enough to carry a journal bore plus wall.
# Seat for the horn adapter / bearing carrier. 22.0 matches the HORN_BORE
# convention already used in chassis.py, and takes a 608ZZ (8x22x7) directly --
# which the step.parts catalog carries, so it is a real orderable part.
JOURNAL_D = 22.0
JOURNAL_WALL = 5.0
END_OVER = JOURNAL_D / 2 + JOURNAL_WALL      # 16.0
Z0, Z1 = -END_OVER, L2_THIGH + END_OVER

HORN_PCD = 17.0        # NOMINAL -- P0 caliper gate. Dingo's own is 14.142.
HORN_BOLT = 2.9
M3_CLEAR, M3_PILOT = 3.4, 2.6

# ------------------------------------------------------------- servo + cover
# The knee servo lives in the thigh (direct drive). Its output is ON the knee
# axis; its body reaches UP the thigh from there.
SERVO_Z_LO = L2_THIGH - SERVO_BODY_LENGTH + 12.0     # boss offset from body end
POCKET_X = SERVO_BODY_WIDTH + 2 * CL
POCKET_Y = SERVO_BODY_HEIGHT + 2 * CL
COVER_T = WALL
TONGUE_D = 2.5         # how far the tongue reaches into the opening
COVER_TAB = 14.0       # cover runs past the opening top and bottom, to bolt
COVER_BOLT_DY = 13.0   # bolt line, well inside SEC_Y/2 = 20.7


def _teardrop(dia, length, apex=45.0):
    """A horizontal bore with a roof, so it prints without support.

    A plain horizontal circle needs a bridge across its crown. Adding a
    `apex`-degree gable turns the top into two self-supporting walls. Lifted
    verbatim from the technique in cad/telescopebot/leg_linkage.py, which is
    one of the few things in that superseded module worth keeping.
    """
    r = dia / 2.0
    a = math.radians(apex)
    tip = r / math.sin(a)
    pts, n = [], 48
    for i in range(n + 1):
        th = math.radians(90 + a) + (math.radians(360 - 2 * a)) * i / n
        pts.append(Vector(r * math.cos(th), 0, r * math.sin(th)))
    pts.append(Vector(0, 0, tip))
    face = Face(Wire.make_polygon(pts, close=True))
    return Solid.extrude(face, Vector(0, length, 0))


def create_thigh():
    """The shell: closed box, two coaxial ends, servo cavity open on +X."""
    with BuildPart() as part:
        # --- outer section --------------------------------------------------
        with Locations((0, 0, (Z0 + Z1) / 2)):
            Box(SEC_X, SEC_Y, Z1 - Z0, align=Align.CENTER)

        # --- hollow it, leaving both cheeks and both end caps ----------------
        with Locations((0, 0, (Z0 + Z1) / 2)):
            Box(SEC_X - 2 * WALL, SEC_Y - 2 * WALL, Z1 - Z0 - 2 * WALL,
                align=Align.CENTER, mode=Mode.SUBTRACT)

        # --- the two coaxial bores, one pair per end ------------------------
        # Same diameter both ends, both cheeks. That sameness IS the
        # non-handedness: one bore accepts a horn adapter, the other a bearing
        # carrier, and swapping them swaps the leg's hand.
        #
        # THERE IS NO BOLT CIRCLE HERE, deliberately. The first version cut a
        # HORN_PCD circle in these cheeks and it removed nothing -- a 17 mm PCD
        # puts bolts at r = 8.5, entirely inside an r = 11 bore. That is not a
        # typo, it is geometry: a servo horn's bolt circle is ALWAYS smaller
        # than a useful bearing OD, so no single plate can both bolt to a horn
        # and seat a bearing concentrically. The horn interface therefore lives
        # on a separate adapter disc that seats in this bore, which is also what
        # lets both cheeks stay identical.
        for z in (0.0, L2_THIGH):
            with Locations((0, 0, z)):
                Cylinder(radius=JOURNAL_D / 2, height=SEC_Y * 2,
                         rotation=(90, 0, 0), mode=Mode.SUBTRACT)

        # --- servo cavity, opened on the +X face only -----------------------
        # Split plane normal to X: the governing bending acts in the YZ plane,
        # so it lies IN the joint plane and the bolted seam carries no direct
        # tension from it -- only the 2.4 N/mm of torsional shear flow.
        srv_h = SERVO_BODY_LENGTH + 2 * CL
        with Locations((SEC_X / 2, 0, SERVO_Z_LO + srv_h / 2)):
            Box(SEC_X, POCKET_Y, srv_h, align=Align.CENTER, mode=Mode.SUBTRACT)

        # NO REBATE. The obvious move is to sink the cover flush in a rebate,
        # but the wall here is WALL thick and a rebate deep enough to swallow a
        # WALL-thick cover removes the entire wall -- it becomes a through-hole
        # with a razor shoulder, which is what partcheck flagged as a 0.7 mm
        # sliver on the first attempt. Instead the cover sits proud and its
        # TONGUE plugs the opening. The tongue is the shear key, and it carries
        # the 2.37 N/mm flow continuously where bolts would carry it at points.

        # Bolts go ABOVE and BELOW the opening, never in the side flanks. The
        # flank is only WALL thick between POCKET_Y and SEC_Y, so an M3 hole
        # there is wider than the material and severs it -- which is exactly
        # what partcheck reported as "5 solids, 0.07 mm wall" on the first
        # attempt. Above and below, the shell is solid across the full section.
        for zz in (SERVO_Z_LO - COVER_TAB / 2,
                   SERVO_Z_LO + srv_h + COVER_TAB / 2):
            for sy in (-1, 1):
                with Locations((SEC_X / 2, sy * COVER_BOLT_DY, zz)):
                    Cylinder(radius=M3_PILOT / 2, height=WALL * 3,
                             rotation=(0, 90, 0), mode=Mode.SUBTRACT)

        # --- cable route from the cavity up to the hip end -------------------
        with Locations((0, 0, SERVO_Z_LO - 6.0)):
            Cylinder(radius=4.0, height=20.0, mode=Mode.SUBTRACT)

    return part.part


def create_cover():
    """The closure plate. STRUCTURAL: it is what makes the section closed.

    One plate, no separate flanges. The first version bolted through 3 mm-wide
    ribs and partcheck caught it immediately -- an M3 clearance hole is 3.4 mm,
    so each rib was cut clean through and the "plate" came out as five loose
    solids. Bolt tabs now run past the opening in Z, where the plate is full
    width and there is real meat around every hole.
    """
    srv_h = SERVO_BODY_LENGTH + 2 * CL
    plate_z = srv_h + 2 * COVER_TAB
    with BuildPart() as part:
        # backing plate: sits ON the outer face, spanning the bolt tabs
        Box(COVER_T, SEC_Y, plate_z, align=Align.CENTER)
        # tongue: plugs the opening, 0.3 mm clearance all round for fit
        with Locations((-(COVER_T / 2 + TONGUE_D / 2), 0, 0)):
            Box(TONGUE_D, POCKET_Y - 0.3, srv_h - 0.3, align=Align.CENTER)
        for zz in (-(srv_h / 2 + COVER_TAB / 2), +(srv_h / 2 + COVER_TAB / 2)):
            for sy in (-1, 1):
                with Locations((0, sy * COVER_BOLT_DY, zz)):
                    Cylinder(radius=M3_CLEAR / 2, height=COVER_T * 4,
                             rotation=(0, 90, 0), mode=Mode.SUBTRACT)
    return part.part


if __name__ == "__main__":
    from partcheck import check

    out = Path(__file__).parent / "output"
    out.mkdir(exist_ok=True)

    shell, cover = create_thigh(), create_cover()
    for nm, sh in (("thigh_shell", shell), ("thigh_cover", cover)):
        export_stl(sh, str(out / f"{nm}.stl"))
        export_step(sh, str(out / f"{nm}.step"))

    # --- the torsion numbers this part exists to satisfy --------------------
    b, d, t = SEC_Y, SEC_X, WALL
    Am = (b - t) * (d - t)
    J_closed = 4 * Am ** 2 * t / (2 * ((b - t) + (d - t)))
    J_open = (2 * b * t ** 3 + d * t ** 3) / 3
    G = 1700 / 2.6
    T = 1073.0                      # N.mm, mu=0.3 walking side load
    th_c = T * L2_THIGH / (G * J_closed)
    th_o = T * L2_THIGH / (G * J_open)
    print(f"section {SEC_X:.2f} (fore-aft) x {SEC_Y:.2f} (lateral) x "
          f"{Z1-Z0:.1f} tall,  L2 = {L2_THIGH:.1f} mm")
    print(f"\ntorsion, the ONLY quantity that discriminates topology:")
    print(f"  J closed   {J_closed:10.0f} mm4   twist {math.degrees(th_c):6.3f} deg"
          f"   foot swing {math.degrees(th_c)*math.pi/180*249.3:6.2f} mm")
    print(f"  J open     {J_open:10.0f} mm4   twist {math.degrees(th_o):6.3f} deg"
          f"   foot swing {math.degrees(th_o)*math.pi/180*249.3:6.2f} mm")
    print(f"  ratio      {J_closed/J_open:10.0f}x  <- why the cover is structural")

    for nm, sh, mat in (("thigh_shell", shell, "PETG"),
                        ("thigh_cover", cover, "PETG")):
        check(sh, nm, out_dir=str(out), material=mat)

    print("\nPRINT-BLOCKED: servo height unresolved (35.00 vs 37.80) — "
          "SEC_Y derives from it; drawn parametrically, gated at both; "
          "do not print before the caliper.")
    print("KNOWN DEFECT (2026-08-01): upper cover-bolt pair cut in air at "
          f"z=149.40 vs part top {Z1:.2f} — cover bolts only at its lower "
          "pair; no in-envelope relocation exists (3.60 mm band vs 5.2 mm "
          "1.0d floor). Deferred to the hip-pitch-cavity rework; do not "
          "drill/screw the top row. See docstring.")

    html = out / "thigh.html"
    subprocess.run([sys.executable,
                    str(Path(__file__).parent.parent.parent / "edu/tools/stl_viewer.py"),
                    str(out / "thigh_shell.stl"), str(out / "thigh_cover.stl"),
                    "-o", str(html), "-t", "Alpha Centauri — thigh (L2)"],
                   check=True)
