"""Alpha Centauri — where the chest columns go, and what the current layout costs.

    edu/.cadenv/bin/python cad/alpha_centauri/chest_columns.py

THE OBSERVATION, AND MY FIRST ANSWER TO IT WAS WRONG
-----------------------------------------------------
The author, 2026-08-01: "the chest extension mechanism in both versions is only on 1
side ... it should be on both sides", then: "I meant on both sides of the robot
as in its left and right so that the chest box is supported on the left legs
side and the right legs side."

He meant LATERALLY, and he was right about an outright bug, not a preference.
The donor box frame and the robot frame are 90 degrees apart:

    donor +X / -X = LEFT and RIGHT   (both rod towers, both shoulder pilots)
    donor +Y      = FRONT            (RealSense holes, intake vents)
    robot +X      = FRONT,  robot +/-Y = LEFT and RIGHT

Both boxes were installed UNROTATED, so the donor's left-right axis landed on
the robot's fore-aft. Both guide rods straddled front-to-back, sat 49.5 mm off
to one side of the centreline, the camera faced sideways and the shoulders
pointed fore and aft. FIXED in marks.py: the boxes install rotated -90 about Z,
and the rods now straddle the left and right legs as the donor intended.

MY FIRST READING HAD THE AXES SWAPPED and described the offset as fore-aft. The
arithmetic below survives that -- a 49.5 mm offset costs the same whichever axis
it is on -- but the SHAPE of the fix changed, so the file is corrected rather
than quietly re-run.

WHAT IS STILL WRONG AFTER THAT FIX
----------------------------------
All three columns share one fore-aft station, hard against the chest's rear
wall, and the chest's mass sits ~49.5 mm forward of it. So the machine is now
properly braced left-to-right and still cantilevered front-to-back.

WHY IT MATTERS MORE THAN IT LOOKS
---------------------------------
The instinct is about stiffness. The real cost is FRICTION, and it is much
larger. A telescoping column whose drive point is offset from the load's centre
of mass carries a permanent overturning moment, and a linear bushing reacts a
moment as a COUPLE across its own length -- 48 mm here. That couple is a constant
normal force on the bushings, so it becomes constant drag on every single lift.

  M     = W * offset
  N     = 2 * M / tower_height        <- couple, both bushing ends
  drag  = mu * N

That drag lands directly on the number that was already the tightest in the
project: the Mk2 hand lift, at 72% of a measured servo per arm.

WHAT THE FIX IS
---------------
Two separate changes, and they fix different things:

  1. PUT THE DRIVE UNDER THE LOAD (y = 0 instead of -49.5). Kills the overturning
     moment at the source, so the drag goes away rather than being reacted more
     stiffly. This is the one that matters.
  2. RODS AT FOUR CORNERS instead of two in a line. A pitch moment applied to two
     rods that share a y has NO couple arm at all -- it can only bend them and
     take up bushing slop. Four corners give it a 99 mm arm.

The blocker on both is the same: the Jetson lies on the chest floor spanning
y = -43..+43, which is exactly where a central drive column and the inboard half
of any front tower want to be.

That blocker is already scheduled to disappear. balance.py wants the Jetson OUT
of the chest and into the rear chassis for fore-aft balance reasons that have
nothing to do with this. Moving it pays for itself twice.
"""

import math

# ---- geometry as drawn (from telescopebot/chest_box.py) --------------------
BOX_DEPTH = 130.0
ROD_X = 60.0
ROD_Y_NOW = -49.5              # = -BOX_DEPTH/2 + TOWER_DEPTH/2, hard at the rear
TOWER_H = 48.0                 # bushing engagement length
ROD_D = 8.0
BORE_D = 8.5                   # so 0.5 mm diametral slop per bushing
STROKE = 250.0

CHEST_N = 15.1                 # chest cluster weight, N
CHEST_COM_Y = 0.0              # mid-depth: Jetson on the floor, camera on the front
MU = 0.30                      # PETG bushing on steel rod, dry
E_STEEL = 200000.0
ARM_N = 8.17                   # one arm at 300 mm reach, from hand_load.py
SERVO_MEASURED_KGCM = 25.0
DETENT_N = 2.55                # spine pawl ride-over


def drag(drive_y, n_rods, rod_y):
    """Bushing drag from the overturning moment, N.

    drive_y is where the vertical load is REACTED (nut or pawl); rod_y is where
    the guides are. They are separate: the moment is set by the drive offset,
    the arm that reacts it is set by the rod layout.
    """
    offset = abs(CHEST_COM_Y - drive_y)
    m = CHEST_N * offset / 1000.0            # N.m
    # A single line of rods reacts the moment inside each bushing, over its own
    # length. Rods at two different y react it as a couple between GROUPS, over
    # their separation -- a far longer arm.
    arm = TOWER_H if n_rods <= 2 else 2 * abs(rod_y)
    n = 2 * (m * 1000.0) / arm
    return MU * n, m, arm


def sway(n_rods, rod_y):
    """Chest-top movement under one arm: rod bending + bushing slop."""
    i_one = math.pi * ROD_D ** 4 / 64.0
    bend = ARM_N * STROKE ** 3 / (3 * E_STEEL * n_rods * i_one)
    # slop tilts about the bushing length for an in-line pair, about the rod
    # separation for a four-corner set
    arm = TOWER_H if n_rods <= 2 else 2 * abs(rod_y)
    tilt = (BORE_D - ROD_D) / arm
    return bend + tilt * STROKE, bend, math.degrees(tilt)


def lift_pct(extra_n):
    """Percent of one measured servo, per arm, at 200 mm reach."""
    per_arm = (CHEST_N + DETENT_N + extra_n) / 2.0
    kgcm = per_arm * 20.0 / 9.81
    return 100 * kgcm / SERVO_MEASURED_KGCM


OPTIONS = [
    ("A  2 rods at the rear  (as drawn)", 2, ROD_Y_NOW, ROD_Y_NOW),
    ("B  2 rods at mid-depth", 2, 0.0, 0.0),
    ("C  4 rods at the corners, rear drive", 4, 49.5, ROD_Y_NOW),
    ("D  4 rods at the corners, centre drive", 4, 49.5, 0.0),
]

if __name__ == "__main__":
    print(f"chest {CHEST_N:.1f} N, CoM at y = {CHEST_COM_Y:.0f}, "
          f"bushing {TOWER_H:.0f} mm long, mu {MU}\n")
    print(f"{'layout':<40s} {'drag N':>7s} {'lift/arm':>9s} {'sway mm':>8s}")
    print("-" * 68)
    for name, n, ry, dy in OPTIONS:
        d, m, arm = drag(dy, n, ry)
        s, bend, tilt = sway(n, ry)
        pct = lift_pct(d)
        flag = "OK" if pct < 75 else "OVER"
        print(f"{name:<40s} {d:7.1f} {pct:8.0f}% {s:8.2f}   {flag}")

    print()
    d_a, m_a, arm_a = drag(ROD_Y_NOW, 2, ROD_Y_NOW)
    print(f"A in detail -- this is what is drawn today:")
    print(f"  overturning moment  {m_a:.2f} N.m "
          f"({CHEST_N:.1f} N acting {abs(ROD_Y_NOW):.1f} mm forward of the drive)")
    print(f"  reacted over        {arm_a:.0f} mm -- the bushing's OWN length, "
          f"because both rods share a y")
    print(f"  bushing normal load {2 * m_a * 1000 / arm_a:.1f} N, constant, "
          f"every lift")
    print(f"  drag                {d_a:.1f} N = {100 * d_a / CHEST_N:.0f}% of the "
          f"chest's own weight")
    print(f"  hand lift goes      {lift_pct(0):.0f}% -> {lift_pct(d_a):.0f}% "
          f"of a measured servo per arm")
    print()
    print(f"So the author's read is right, and the reason is not the one it looks like.")
    print(f"The stiffness loss is real but small ({sway(2, ROD_Y_NOW)[0]:.1f} mm "
          f"vs {sway(4, 49.5)[0]:.1f} mm at the chest top).")
    print(f"The FRICTION is what kills it: layout A puts the Mk2 hand lift OVER "
          f"a stall it was already at 72% of.")
    print()
    print(f"RECOMMEND D. Drive under the load kills the drag; four corners give "
          f"the pitch a real arm.")
    print(f"Both need the Jetson out of the chest -- which balance.py wants "
          f"anyway, for fore-aft balance.")
