"""Alpha Centauri — where can the torso actually sit? (fore-aft balance)

    edu/.cadenv/bin/python cad/alpha_centauri/balance.py

THE QUESTION
------------
The author, 2026-08-01: "why are the waist and chest box in the middle of the body and
not at the front end? like a real centaur." Correct instinct. This file works out
what it costs, because the answer is not free and is not obvious.

THE CONSTRAINT NOBODY GUESSES
-----------------------------
It is not tipping. A four-footed stand is stable with the CoM anywhere in the
footprint. What binds is the CRAWL: to lift one foot the CoM must be inside the
triangle of the other three, and when the front-left lifts, the binding edge runs
FR -> RL. That edge crosses the centreline at

    x = (x_front_hip + x_rear_hip) / 2

so with symmetric hips at +/-250 the limit is x = 0 and a centred CoM is ALREADY
on the boundary -- which is exactly where the 25.5 mm lateral shift comes from.
Push the CoM 50 mm forward and the shift needed to recover grows to 53 mm, which
needs 99.2% of leg reach. The robot simply stops being able to walk.

RETRACTED, 2026-08-01: ASYMMETRIC HIPS DO NOTHING
-------------------------------------------------
An earlier version of this file recommended moving the front hips to +300 and
the rear to -200. The author looked at the render and said it seemed like nothing had
changed but the length of one half. He was right.

The mistake was arithmetic, not conceptual: the solver held the battery at a
FIXED x = -190 in every configuration while the rear body shrank from 250 mm
long to 200 mm. In the symmetric layout the battery could have sat at -240 and
was never allowed to. That handed the asymmetric layout a better counterweight
position and then credited the hip geometry for it.

Measured properly -- battery at the rear EDGE in both cases -- the counterweight
lever about the wheelbase midpoint is 190.0 mm either way. Same wheelbase, same
lever, same robot. Sliding the hip stations along a fixed-length wheelbase only
relabels the origin.

WHAT ACTUALLY CONSTRAINS IT
---------------------------
Lifting a FRONT foot, the CoM must be AFT of the wheelbase midpoint.
Lifting a REAR foot, it must be FORWARD of it.
So the CoM has to sit essentially AT the midpoint, and the lateral lean does the
rest. There is no geometric trick; only three real levers exist:

  1. counterweight mass x lever arm  (costs mass, unless it is mass you carry
     anyway -- battery, Jetson, power board)
  2. body length AFT of the rear legs (a tail), which buys lever arm without
     touching the wheelbase
  3. MOVING THE TORSO ITSELF -- the author's rail idea. This is the only one that turns
     a fixed compromise into a mode: sit aft to walk, slide forward to work.
"""

import math
from pathlib import Path

from build123d import import_step

from interface_constants import (
    L1_LATERAL,
    LEG_LR,
    LEG_REACH_MAX,
    LEG_EXTENSION_LIMIT,
    STANCE_Z,
    SERVO_MASS_G,
    extension_at,
)

OUT = Path(__file__).parent / "output"
PETG = 0.953
HALF_TRACK = LEG_LR + L1_LATERAL
CRAWL_MARGIN = 25.0        # how far inside the triangle edge we insist on sitting
LAT_SHIFT = 25.5


def g(name):
    p = OUT / f"{name}.step"
    return import_step(str(p)).volume / 1000.0 * PETG if p.exists() else 0.0


# ------------------------------------------------------------- the ledger
PRINTED_LEG = g("thigh_shell") + g("thigh_cover") + g("calf") \
    + g("horn_adapter") + g("bearing_retainer") + g("bearing_carrier")
LEG_TOTAL = PRINTED_LEG + 3 * SERVO_MASS_G      # 3 servos per leg
# every printed chassis part (4 quarters, 4 pods, 6 keys) -- chassis.py owns
# the list; was 2 x chassis_half until 2026-09-23
CHASSIS = 2 * g("chassis_quarter_inner") + 2 * g("chassis_quarter_outer") \
    + 4 * g("abduction_pod") + 6 * g("chassis_splice_key")
SPINE = g("spine_rack") + g("spine_pawl")

# Cluster masses. The torso figure is the one the height analysis used.
#
# THE BRAIN IS A PHONE (REPLAN-2026-08-28 section 2, applied 2026-09-22): an
# old Android phone over USB-OTG to an FE-URT-1 bus adapter, plus a 5 V
# buck -- ~215 g NOMINAL. It replaces the 300 g Jetson + heatsink + power
# board the 2026-08-01 height analysis carried inside TORSO_FULL = 1538 g.
# TORSO_FULL is therefore DERIVED now, not restated: the H2C-era cluster
# minus the Jetson plus the phone. The brain stays MOVEABLE aft -- the E4
# placement A/B in the sim is the same question with a lighter lump.
TORSO_FULL_H2C_ERA = 1538.0   # chest box + Jetson 300 + camera + two arms
JETSON_ETC_H2C_ERA = 300.0    # provenance only -- nothing may consume this
PHONE_ETC = 215.0             # NOMINAL  phone + OTG bus adapter + 5 V buck
TORSO_FULL = TORSO_FULL_H2C_ERA - JETSON_ETC_H2C_ERA + PHONE_ETC   # 1453
# BATTERY (REPLAN-2026-08-28 section 3; bays drawn 2026-09-22 in chassis.py):
# TWO 3S 18650 swap packs, side by side, BOTH at the rear station. The old
# 600 g "6S-class" single pack (bay 110x40x30) is H2C-era provenance -- a 6S
# pack can never feed the 12 V-max servo bus (interface_constants, bus
# voltage law). Both packs sit at the same x, so the counterweight moment
# this file computes is unchanged: 2 x 300 g at -190 == 600 g at -190.
# Pulling ONE pack for a swap costs 300 g x 190 mm of aft moment -- the
# REPLAN's own stability check (+12..15 mm CoM shift, parked) covers it.
PACK_G = 300.0             # NOMINAL  one 3S pack + holder + BMS
N_PACKS = 2                # DECISION  the swap pair
BATTERY = N_PACKS * PACK_G # DERIVED  600, same total as the H2C-era pack

# Aft stations. The battery station is OWNED by chassis.py (the bays are
# geometry); this file used to restate -190 and chassis.py used to restate
# it back -- now one direction only.
from chassis import BAY_X as _BAY_X   # noqa: E402
X_BATTERY = -_BAY_X        # DERIVED  -190.0
X_ELECTRONICS = -150.0


def com_x(xf, xr, x_torso, torso_mass, aft_extra_mass, x_aft):
    """Fore-aft centre of mass, mm. Chassis is symmetric so contributes 0."""
    m = [(CHASSIS, 0.0),
         (2 * LEG_TOTAL, xf), (2 * LEG_TOTAL, xr),
         (torso_mass, x_torso), (SPINE, x_torso),
         (BATTERY, X_BATTERY), (aft_extra_mass, x_aft)]
    tot = sum(a for a, _ in m)
    return sum(a * b for a, b in m) / tot, tot


def max_torso_x(xf, xr, torso_mass, aft_extra, x_aft):
    """Furthest forward the torso can sit and still leave the CoM legal."""
    limit = (xf + xr) / 2 - CRAWL_MARGIN
    lo, hi = -400.0, 600.0
    for _ in range(80):
        mid = (lo + hi) / 2
        c, _ = com_x(xf, xr, mid, torso_mass, aft_extra, x_aft)
        lo, hi = (mid, hi) if c < limit else (lo, mid)
    return lo


if __name__ == "__main__":
    print(f"printed leg {PRINTED_LEG:.0f} g + 3 servos = {LEG_TOTAL:.0f} g each")
    print(f"chassis {CHASSIS:.0f} g   spine {SPINE:.0f} g   "
          f"torso {TORSO_FULL:.0f} g   battery {BATTERY:.0f} g "
          f"({N_PACKS} x {PACK_G:.0f} g packs at x = {X_BATTERY:.0f})\n")

    e = extension_at(STANCE_Z, LAT_SHIFT)
    print(f"crawl reach is {100*e/LEG_REACH_MAX:.1f}% in EVERY row below -- moving "
          f"the hips does not change it.\n")

    print("A) battery aft only, electronics stay in the chest")
    print(f"{'x_front':>8s} {'x_rear':>8s} {'CoM limit':>10s} "
          f"{'torso max x':>12s} {'total kg':>9s}")
    for xf, xr in ((250, -250), (280, -220), (300, -200), (320, -180), (350, -150)):
        xt = max_torso_x(xf, xr, TORSO_FULL, 0.0, X_ELECTRONICS)
        _, tot = com_x(xf, xr, xt, TORSO_FULL, 0.0, X_ELECTRONICS)
        print(f"{xf:8.0f} {xr:8.0f} {(xf+xr)/2 - CRAWL_MARGIN:10.1f} "
              f"{xt:12.1f} {tot/1000:9.2f}")

    print("\nB) battery aft AND phone/power moved out of the chest into the "
          "rear chassis")
    print(f"{'x_front':>8s} {'x_rear':>8s} {'CoM limit':>10s} "
          f"{'torso max x':>12s} {'total kg':>9s}")
    best = None
    for xf, xr in ((250, -250), (280, -220), (300, -200), (320, -180), (350, -150)):
        xt = max_torso_x(xf, xr, TORSO_FULL - PHONE_ETC, PHONE_ETC, X_ELECTRONICS)
        _, tot = com_x(xf, xr, xt, TORSO_FULL - PHONE_ETC, PHONE_ETC,
                       X_ELECTRONICS)
        print(f"{xf:8.0f} {xr:8.0f} {(xf+xr)/2 - CRAWL_MARGIN:10.1f} "
              f"{xt:12.1f} {tot/1000:9.2f}")
        if xf == 320:
            best = (xf, xr, xt, tot)

    print("\nC) what pure ballast would buy, at symmetric hips (the expensive way)")
    print(f"{'ballast g':>10s} {'torso max x':>12s} {'total kg':>9s}")
    for bal in (0, 250, 500, 1000, 1500):
        xt = max_torso_x(250, -250, TORSO_FULL, bal, X_BATTERY)
        _, tot = com_x(250, -250, xt, TORSO_FULL, bal, X_BATTERY)
        print(f"{bal:10.0f} {xt:12.1f} {tot/1000:9.2f}")

    xf, xr, xt, tot = best
    print(f"\nRECOMMENDATION: hips {xf:+.0f}/{xr:+.0f}, torso at x = {xt:.0f} mm,")
    print(f"battery and phone aft. Total {tot/1000:.2f} kg, no ballast at all.")
    print(f"The chest then spans roughly x {xt-75:.0f}..{xt+75:.0f} on a body that")
    print(f"ends at {xf+40:.0f} -- it sits OVER the front legs, which is the look.")
