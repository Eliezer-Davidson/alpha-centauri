"""Alpha Centauri Mk1 — everything built so far, placed in robot coordinates.

    edu/.cadenv/bin/python cad/alpha_centauri/assembly.py

This is an ASSEMBLY VIEW, not a design. Its only job is to answer "does the whole
thing look right, and do any two parts want to occupy the same space". Nothing
here changes a part; every solid is loaded from its own STEP.

Robot frame: X fore-aft (+X forward), Y lateral, Z up. Origin at the CENTRE of
the chassis floor -- so the two chassis halves span -250..0 and 0..+250, and the
robot is symmetric about X=0. Ground is wherever the feet land, which the leg
solve below computes rather than assumes.

Honesty markers, carried into the filenames so the viewer shows them:
  * `_`-prefixed parts start HIDDEN. They are superseded or reference geometry.
  * The legs are SCHEMATIC struts on exact Dingo L1/L2/L3 axes. They are massing,
    not parts -- no servo, no bracket, no bearing. Their joint angles ARE solved
    correctly, so the stance, the footprint and the ride height are real numbers.
"""

import math
import shutil
import subprocess
import sys
from pathlib import Path

from build123d import (
    Align,
    Axis,
    Box,
    Cylinder,
    Location,
    Rotation,
    Sphere,
    Vector,
    export_stl,
    import_step,
)

from interface_constants import (
    CHASSIS_HEIGHT,
    FOOT_SPHERE_R,
    HIP_PITCH_AXIS_ABOVE_DATUM,
    L1_LATERAL,
    L1_VERTICAL,
    L2_THIGH,
    L3_CALF,
    LEG_FB,
    LEG_LR,
    STANCE_Z,
    extension_at,
)

HERE = Path(__file__).parent
OUT = HERE / "output"
ASM = OUT / "assembly"
TBOT = HERE.parent / "telescopebot" / "output"

from thigh import SEC_X as THIGH_SEC_X, SERVO_Z_LO as _SZL
from thigh import SERVO_BODY_LENGTH as _SBL, CL as _CL

THIGH_SERVO_MID = _SZL + (_SBL + 2 * _CL) / 2   # cover sits at the servo station

from chassis import HIP_Z             # abduction axis — single source (law 8)
STRUT_R = 11.0                        # schematic limb radius
TORSO_STROKE = 250.0                  # stowed -> extended
# Rear plane the old twin M8 rods occupied (chest_box.py: -BOX_DEPTH/2 +
# TOWER_DEPTH/2). The rack inherits it -- the chest towers are already there.
ROD_Y = -49.5


# --------------------------------------------------------------- leg solve
def solve_leg(stance_z):
    """Joint angles for a foot directly below the hip-pitch axis.

    Returns (thigh angle from vertical, knee bend from straight, extension), deg.

    The hip-pitch axis sits HIP_PITCH_AXIS_ABOVE_DATUM above the body datum, so
    hip-to-foot spans MORE than the body stands tall -- the correction that
    halved every knee-torque estimate in the plan (§1.6).
    """
    ext = stance_z + HIP_PITCH_AXIS_ABOVE_DATUM
    reach = L2_THIGH + L3_CALF
    if ext >= reach:
        raise ValueError(f"stance {stance_z} needs {ext:.2f} mm, reach is {reach:.2f}")
    # interior angle at the knee, law of cosines on the L2/L3/ext triangle
    ck = (L2_THIGH**2 + L3_CALF**2 - ext**2) / (2 * L2_THIGH * L3_CALF)
    knee_int = math.degrees(math.acos(max(-1.0, min(1.0, ck))))
    # thigh's angle off the (vertical) hip-to-foot line, sine rule
    sa = L3_CALF * math.sin(math.radians(knee_int)) / ext
    alpha = math.degrees(math.asin(max(-1.0, min(1.0, sa))))
    return alpha, 180.0 - knee_int, ext


def strut(p0, p1, r=STRUT_R):
    """A capsule from p0 to p1, for any direction.

    The previous version special-cased two directions: a pure-Y branch for the
    L1 link and an XZ branch for the thigh and calf. That was only ever right
    because L1 was being drawn as a pure lateral offset -- which was the bug.
    L1 actually runs 49.60 mm outboard AND 14.30 mm up, so it is neither case,
    and the special-cased version would have drawn it at the correct LENGTH
    pointing at the wrong PLACE. General axis-angle, no branches.
    """
    d = Vector(*(p1[i] - p0[i] for i in range(3)))
    length = d.length
    body = Cylinder(radius=r, height=length,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))
    body += Sphere(radius=r) + Sphere(radius=r).moved(Location((0, 0, length)))
    # Rotate +Z onto d about their common perpendicular. When d is already along
    # +/-Z the cross product vanishes, so fall back to an explicit axis.
    z = Vector(0, 0, 1)
    axis = z.cross(d)
    angle = math.degrees(math.acos(max(-1.0, min(1.0, z.dot(d) / length))))
    if axis.length < 1e-9:
        axis = Vector(1, 0, 0)
    body = body.rotate(Axis((0, 0, 0), axis.normalized().to_tuple()), angle)
    return body.moved(Location(p0))


def _aim(shape, p0, p1):
    """Place `shape` (authored along its own +Z) so +Z runs from p0 to p1.

    Every link here lies in a plane containing Z with its joint axis along Y, so
    a single rotation about Y suffices -- and unlike the schematic strut helper,
    the angle is derived rather than branched on.
    """
    dx, dz = p1[0] - p0[0], p1[2] - p0[2]
    return shape.rotate(Axis.Y, math.degrees(math.atan2(dx, dz))).moved(
        Location(p0))


def build_real_leg(sx, sy, alpha, knee, parts):
    """The actual printed leg, posed. Returns {name: solid} keyed for the viewer.

    The parts are NON-HANDED, so left and right load the identical STEP -- that
    claim is only worth making if the assembly actually demonstrates it, which
    is why nothing here mirrors anything.
    """
    hip_ab = (sx * LEG_FB, sy * LEG_LR, HIP_Z)
    hip_pitch = (sx * LEG_FB, sy * (LEG_LR + L1_LATERAL), HIP_Z + L1_VERTICAL)
    a = math.radians(alpha)
    knee_pt = (hip_pitch[0] - L2_THIGH * math.sin(a), hip_pitch[1],
               hip_pitch[2] - L2_THIGH * math.cos(a))
    foot_pt = (hip_pitch[0], hip_pitch[1], hip_pitch[2] - extension_at(STANCE_Z))

    out = {}
    if "thigh_shell" in parts:
        out["thigh"] = _aim(parts["thigh_shell"], hip_pitch, knee_pt)
    if "thigh_cover" in parts:
        # cover rides on the thigh's +X face, at the servo station
        cov = parts["thigh_cover"].moved(Location((THIGH_SEC_X / 2 + 1.5, 0,
                                                   THIGH_SERVO_MID)))
        out["cover"] = _aim(cov, hip_pitch, knee_pt)
    if "calf" in parts:
        out["calf"] = _aim(parts["calf"], knee_pt, foot_pt)
    return out, foot_pt


def build_leg(sx, sy, alpha, knee):
    """One schematic leg. sx = +1 front / -1 rear, sy = +1 left / -1 right.

    L1 IS A DIAGONAL. The hip-pitch axis sits L1_LATERAL outboard AND L1_VERTICAL
    UP from the abduction axis; those two are the primitives and 51.62 is their
    hypotenuse. Drawing the full 51.62 laterally at the same height -- which this
    function did until 2026-07-31 -- put the foot 2.02 mm too far out per side
    AND dropped the whole robot 14.30 mm, silently turning the 235 mm stance into
    the 249.30 mm one this project rejected as un-crawlable.
    """
    hip_ab = (sx * LEG_FB, sy * LEG_LR, HIP_Z)
    hip_pitch = (sx * LEG_FB,
                 sy * (LEG_LR + L1_LATERAL),
                 HIP_Z + L1_VERTICAL)

    a = math.radians(alpha)
    # knee trails aft of the hip; foot ends up directly below the hip-pitch axis
    knee_pt = (hip_pitch[0] - L2_THIGH * math.sin(a),
               hip_pitch[1],
               hip_pitch[2] - L2_THIGH * math.cos(a))
    # extension_at() owns the +L1_VERTICAL rule; do not restate it here.
    foot_pt = (hip_pitch[0], hip_pitch[1], hip_pitch[2] - extension_at(STANCE_Z))

    leg = strut(hip_ab, hip_pitch, r=STRUT_R * 0.85)     # L1 abduction offset
    leg += strut(hip_pitch, knee_pt)                      # thigh  L2
    leg += strut(knee_pt, foot_pt, r=STRUT_R * 0.8)       # calf   L3

    # Foot sphere centred FOOT_SPHERE_R back up the calf, so its surface touches
    # down exactly at foot_pt -- the point the IK actually solved for. Centring
    # it AT foot_pt instead would put the contact 15 mm lower and quietly turn a
    # 235 mm stance into the 250 mm one this project rejected.
    u = [(foot_pt[i] - knee_pt[i]) / L3_CALF for i in range(3)]
    centre = tuple(foot_pt[i] - u[i] * FOOT_SPHERE_R for i in range(3))
    leg += Sphere(radius=FOOT_SPHERE_R).moved(Location(centre))
    return leg, foot_pt


# ------------------------------------------------------------------- build
def main():
    if ASM.exists():
        shutil.rmtree(ASM)
    ASM.mkdir(parents=True)

    alpha, knee, ext = solve_leg(STANCE_Z)
    reach = L2_THIGH + L3_CALF
    print(f"leg solve @ stance {STANCE_Z:.0f} mm:")
    print(f"  hip->foot {ext:.2f} mm = {100 * ext / reach:.1f}% of {reach:.2f} reach")
    print(f"  thigh {alpha:.2f} deg off vertical, knee bent {knee:.2f} deg\n")

    saved = []

    def emit(name, shape):
        p = ASM / f"{name}.stl"
        export_stl(shape, str(p))
        saved.append(p)
        return p

    # --- chassis: ONE part, placed twice, the rear copy spun 180 about Z ------
    # 4 quarters + 4 bolt-on pods + 6 keys since 2026-09-23; placement owned
    # by chassis.chassis_placed() -- never restated here.
    import chassis as CH
    for n, s in CH.chassis_placed(OUT).items():
        emit(f"01_chassis_{n}", s)

    # --- legs -----------------------------------------------------------------
    # Real printed parts if they exist; schematic struts only as a fallback, so
    # the view never silently shows massing when geometry is available.
    parts = {}
    for nm in ("thigh_shell", "thigh_cover", "calf"):
        p = OUT / f"{nm}.step"
        if p.exists():
            parts[nm] = import_step(str(p)).solids()[0]
    real = len(parts) == 3
    print(f"legs: {'REAL printed parts' if real else 'SCHEMATIC struts'}\n")

    feet = []
    for sx, tag_x in ((1, "front"), (-1, "rear")):
        for sy, tag_y in ((1, "left"), (-1, "right")):
            if real:
                bits, foot = build_real_leg(sx, sy, alpha, knee, parts)
                for k, v in bits.items():
                    emit(f"03_{k}_{tag_x}_{tag_y}", v)
            else:
                leg, foot = build_leg(sx, sy, alpha, knee)
                emit(f"03_leg_{tag_x}_{tag_y}_SCHEMATIC", leg)
            feet.append(foot)

    # Ground IS the IK's foot point -- the sphere is centred back up the calf so
    # its surface lands there. Nothing is subtracted; see FOOT_SPHERE_R.
    ground_z = feet[0][2]
    emit("00_ground", Box(760, 480, 3, align=(Align.CENTER, Align.CENTER, Align.MAX))
         .moved(Location((0, 0, ground_z))))

    # --- torso: HAND-DRIVEN spine ---------------------------------------------
    # §1.4 killed the twin open-loop SCREW drive (0.585 deg of tilt jams the
    # 8.5 mm bore). The BOXES survive that finding; only the DRIVE changed.
    # The author's call, 2026-08-01: the arms press the chest up a ratcheted rail
    # instead of two servos winding it up two screws.
    #
    # So the FS5103R servo deck is SUPERSEDED and is shown hidden -- it belongs
    # to the drive that was replaced, and leaving it visible would misrepresent
    # the build. The rack and pawl below are what is actually current.
    z = CHASSIS_HEIGHT
    if (TBOT / "waist_box.step").exists():
        emit("04_waist_box", import_step(str(TBOT / "waist_box.step"))
             .moved(Location((0, 0, z))))
    rim = z + 60.0                      # waist rim: the rack's mounting face

    if (TBOT / "spine_servo_deck.step").exists():
        emit("_spine_servo_deck_SUPERSEDED",
             import_step(str(TBOT / "spine_servo_deck.step"))
             .moved(Location((0, 0, rim))))

    # rack on the centreline, in the rear plane the old rods occupied
    rack_p = OUT / "spine_rack.step"
    if rack_p.exists():
        import spine_lock as SL
        off = Location((-SL.RACK_W / 2, ROD_Y - SL.RACK_T / 2, rim))
        emit("05_spine_rack", import_step(str(rack_p)).moved(off))
        pawl_p = OUT / "spine_pawl.step"
        if pawl_p.exists():
            # seated on the tooth nearest the extended chest floor.
            # The seat offset comes from spine_lock.pawl_engaged_location():
            # this file used to restate it WITHOUT CARRIER_T, burying the pawl
            # 10 mm inside the rack (9617 mm3 measured, 2026-09-07). Never
            # restate the seat arithmetic locally again.
            n = int((rim + TORSO_STROKE - SL.RAMP_H - rim) // SL.PITCH)
            emit("05_spine_pawl_ENGAGED",
                 import_step(str(pawl_p)).moved(
                     off * SL.pawl_engaged_location(n)))

    if (TBOT / "chest_box.step").exists():
        chest_z = rim + 5.0 + TORSO_STROKE
        emit("06_chest_box_EXTENDED",
             import_step(str(TBOT / "chest_box.step")).moved(Location((0, 0, chest_z))))
        top = chest_z + 85.0
    else:
        top = rim

    # --- superseded / reference, hidden by default ---------------------------
    # leg_linkage.py is NOT the Dingo leg (§1.6). Placed at the hip so the size
    # difference is visible, but it must not read as current.
    for f, nm in (("thigh_link.step", "_thigh_link_SUPERSEDED"),
                  ("calf_link.step", "_calf_link_SUPERSEDED")):
        if (TBOT / f).exists():
            emit(nm, import_step(str(TBOT / f))
                 .moved(Location((LEG_FB, LEG_LR + L1_LATERAL + 90, HIP_Z))))

    # --- the numbers this view exists to produce -----------------------------
    print(f"ground plane      z = {ground_z:8.1f}")
    print(f"chassis floor     z = {0:8.1f}   ride height {-ground_z:.1f} mm")
    print(f"chassis top       z = {CHASSIS_HEIGHT:8.1f}")
    print(f"torso top (ext)   z = {top:8.1f}")
    print(f"\nSTANDING HEIGHT, ground to torso top, EXTENDED: {top - ground_z:.0f} mm")
    print(f"                                       target:  850 mm")
    print(f"                                        short:  {850 - (top - ground_z):.0f} mm")
    # The foot sits L1_LATERAL (49.60) outboard of its abduction axis, not the
    # full L1 hypotenuse (51.62). Quoting the hypotenuse overstated the track by
    # 4.04 mm and was the visible symptom of the placement bug above.
    print(f"footprint (foot centres): {2 * LEG_FB:.0f} x "
          f"{2 * (LEG_LR + L1_LATERAL):.1f} mm")
    print(f"hip span:                 {2 * LEG_FB:.0f} x {2 * LEG_LR:.0f} mm")

    # The check the drawing exists to make: does the model stand at the stance
    # the project decided on? Assert it rather than print it -- this is exactly
    # the number that was silently 14.30 mm wrong.
    datum_to_foot = HIP_Z - feet[0][2]
    assert abs(datum_to_foot - STANCE_Z) < 1e-6, (
        f"assembly stands at {datum_to_foot:.3f} mm, not STANCE_Z {STANCE_Z}"
    )
    print(f"\nstance check: abduction datum to foot = {datum_to_foot:.3f} mm "
          f"== STANCE_Z  OK")

    # --- viewer ---------------------------------------------------------------
    html = OUT / "alpha_centauri_mk1.html"
    cmd = [sys.executable, str(HERE.parent.parent / "edu/tools/stl_viewer.py"),
           *[str(p) for p in sorted(saved)], "-o", str(html),
           "-t", "Alpha Centauri Mk1 — assembly to date"]
    print()
    subprocess.run(cmd, check=True)
    return html


if __name__ == "__main__":
    main()
