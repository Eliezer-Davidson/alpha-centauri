"""Alpha Centauri — what the servo- build actually asks of the arms.

    edu/.cadenv/bin/python cad/alpha_centauri/hand_load.py

THE QUESTION
------------
The author, 2026-08-01: "relying so much on the hands to do everything is dangerous and
will put a lot of strain on the hand servos. on the other [hand] the less servo
build has its own merits, less cost, less weight, smarter in a way. we'll have to
see whats what."

This is the "see what's what". Three jobs are hand-driven in the servo- build --
raise the chest, slide the waist, turn the chest -- and they do NOT come out the
same. Two are comfortable and one is not, which is a more useful answer than a
verdict on the whole philosophy.

THE ONE MEASURED NUMBER
-----------------------
25 kg.cm. It is the only bench figure in this project and everything here is
quoted against it. The ST3215 datasheet says 50 kg.cm peak at 12 V; that number
is NOMINAL and is not used, because a stall rating is not a duty rating and the
measured figure already came in at half of it.

WHY LEVER ARM IS THE WHOLE STORY
--------------------------------
A servo makes TORQUE. What the hand can push is torque / reach, so the same arm
is a strong arm folded and a weak one extended. Every row below therefore
carries the reach it assumes; changing that assumption changes the verdict, and
the arms are not designed yet. Treat this as the SPEC the arm must meet, not a
measurement of an arm that exists.

WHAT IT DECIDES
---------------
  spine lift      hand-drivable, but it is the heavy one -- 62% of stall per arm
                  at 200 mm reach. Fold the elbow and it drops to 46%.
  waist slide     hand-drivable ONLY with the release lever. Without it the
                  detent alone is 97% of stall and the arms simply will not move
                  the torso. With it, 12%. A 6.6 g part is the difference.
  chest yaw       the arms CAN turn it -- 2.8x margin over slew friction -- but
                  friction can never hold it. The holding job is 10x what the
                  arms can even generate, so the yaw lock has to be a POSITIVE
                  PIN, not a detent. That is the one place a spring is wrong.
"""

import math

SERVO_MEASURED_KGCM = 25.0        # MEASURED. The only one. Everything divides by it.
SERVO_NOMINAL_KGCM = 50.0         # NOMINAL, datasheet peak at 12 V -- NOT used
G = 9.81

TORSO_G = 1538.0                  # CONSERVATIVE load figure: the H2C-era
                                  # torso (chest box + 300 g Jetson + camera
                                  # + two arms). Since the phone replan the
                                  # ledger torso is balance.TORSO_FULL = 1453 g
                                  # (2026-09-22); the loads below deliberately
                                  # keep the heavier figure -- 85 g of margin,
                                  # not a restatement. Never lower it to match.
ARMS_G = 500.0                    # the pair; they cannot lift themselves by proxy
MU_SLIDE = 0.25                   # PETG on PETG, dry, printed finish
MU_SLEW = 0.25

# from spine_lock.py and waist_rail.py, both computed not assumed
SPINE_DETENT_N = 2.55
RAIL_DETENT_N = 27.8
RAIL_FRICTION_N = TORSO_G / 1000.0 * G * MU_SLIDE

YAW_RING_R = 60.0                 # mean slew radius, mm
YAW_PUSH_R = 80.0                 # where a hand can reach the waist rim, mm


def kgcm(force_n, lever_mm):
    """Torque one arm must make to apply force_n at lever_mm."""
    return force_n * (lever_mm / 10.0) / G


def row(job, total_n, arms, reach_mm, note=""):
    per = total_n / arms
    t = kgcm(per, reach_mm)
    pct = 100 * t / SERVO_MEASURED_KGCM
    flag = "OK" if pct < 40 else ("HEAVY" if pct < 75 else "NO")
    print(f"{job:<26s} {total_n:7.1f} {per:7.1f} {reach_mm:7.0f} {t:8.1f} "
          f"{pct:6.0f}%  {flag:5s} {note}")


if __name__ == "__main__":
    print(f"every % below is against the MEASURED {SERVO_MEASURED_KGCM:.0f} kg.cm, "
          f"not the {SERVO_NOMINAL_KGCM:.0f} kg.cm datasheet peak\n")
    print(f"{'job':<26s} {'total N':>7s} {'per arm':>7s} {'reach':>7s} "
          f"{'kg.cm':>8s} {'of 25':>6s}  verdict")
    print("-" * 84)

    # ---- 1. raise the chest -------------------------------------------------
    # The arms press DOWN on the waist deck and the chest walks up the rack. The
    # load is everything above the waist -- INCLUDING the arms, because they are
    # mounted on the chest and go up with it.
    lift = TORSO_G / 1000.0 * G + SPINE_DETENT_N
    row("spine lift, arm extended", lift, 2, 200, "one press per 175 mm")
    row("spine lift, elbow folded", lift, 2, 150, "same load, better geometry")

    # ---- 2. slide the waist -------------------------------------------------
    row("waist slide, no release", RAIL_DETENT_N + RAIL_FRICTION_N, 2, 150,
        "detent fights the whole way")
    row("waist slide, lever first", RAIL_FRICTION_N, 2, 150,
        "pawl unseated -> friction only")

    # ---- 3. turn the chest --------------------------------------------------
    # An arm mounted ON the chest can still rotate it, by pushing tangentially
    # against the WAIST -- an internal torque pair, which is legal. What it
    # cannot do is hold that rotation against its own manipulation reaction.
    slew_fric_nm = TORSO_G / 1000.0 * G * MU_SLEW * (YAW_RING_R / 1000.0)
    need_n = slew_fric_nm / (YAW_PUSH_R / 1000.0)
    row("chest yaw, unlocked", need_n, 1, YAW_PUSH_R, "one arm on the waist rim")

    print()
    # ---- what the yaw LOCK has to survive -----------------------------------
    arm_force_n = SERVO_MEASURED_KGCM * G / (300.0 / 10.0)     # at 300 mm reach
    worst_nm = arm_force_n * 0.300
    print(f"yaw LOCK sizing -- the disturbance is the robot's OWN arm:")
    print(f"  one arm at 300 mm makes {arm_force_n:.1f} N -> {worst_nm:.2f} N.m "
          f"about the yaw axis")
    print(f"  slew friction holds only {slew_fric_nm:.3f} N.m "
          f"({100 * slew_fric_nm / worst_nm:.0f}% of it)")
    print(f"  a detent would need {worst_nm * 1.5 / (YAW_RING_R / 1000.0):.0f} N "
          f"tangential -- far past a printed leaf")
    pin_d = 5.0
    shear = 2 * math.pi * pin_d ** 2 / 4 * 25.0                 # double shear, PETG
    pin_need = worst_nm * 1.5 / (0.070)
    print(f"  a {pin_d:.0f} mm PIN in double shear holds {shear:.0f} N vs "
          f"{pin_need:.0f} N needed -- SF {shear / pin_need:.1f}")
    print(f"  => the yaw lock is a PIN INTO AN INDEXED RING, not a spring detent.")
    print(f"     24 stations gives 15 deg resolution and cannot cam out at all.")

    print(f"\nthe seam, stated plainly:")
    print(f"  servo-  works for spine and waist. Needs the 6.6 g release lever,")
    print(f"          and needs the yaw pin. Saves 3 servos ~ 224 g and 3 channels.")
    print(f"  servo+  costs 3 servos and makes all three jobs a command instead")
    print(f"          of a gesture -- but STILL needs the detent and the pin,")
    print(f"          because every one of these drives is back-drivable.")
