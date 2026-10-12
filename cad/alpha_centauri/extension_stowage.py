"""Alpha Centauri — where do the chest verticals GO when the chest is down?

    edu/.cadenv/bin/python cad/alpha_centauri/extension_stowage.py

THE QUESTION
------------
The author, 2026-08-02, looking at the condensed render: "in our current design when the
chest box is down where do the railings go? they are too long to be just inside
the waist and chest box, and i dont want them protruding from the top or bottom.
we could make the waist box taller, if its mostly hollow it wont change the
weight much. they could also go into the actual body but that means their path
needs to be clear when the waist box slides up and down the body."

He is right that they do not fit, and both of his suggestions are live. This
file works out what each one costs, because the answer is not obvious and one
of the two does not close on its own.

THE LAW THAT GOVERNS ALL OF IT
------------------------------
For a SINGLE-STAGE vertical fixed at one end, the stowed overhang is set by
arithmetic, not by design skill:

    rod_len       = stroke + engagement          (it must stay engaged at full
                                                  extension)
    covered       = chest_height - tower_height  (what the chest hides when down)
    protrusion    = rod_len - clearance - covered
                  = stroke + engagement - clearance - covered

Everything except `stroke` is small. So PROTRUSION IS THE STROKE, near enough,
and it cannot be designed away inside a single stage -- it can only be MOVED.
That is why "make the waist taller" and "run them into the body" are both
really the same move: find 250 mm of somewhere-else. The three real families:

    MOVE IT DOWN     spend permanent height/depth equal to the stroke
    SPLIT IT         multi-stage telescope: overhang falls as stroke/N
    SHRINK IT        less stroke, or less wasted engagement (see E -- free)

WHAT IS ACTUALLY FREE, AND IT IS NOT NOTHING
--------------------------------------------
ROD_LEN is currently STROKE + 90. The chest's bushing tower is only 48 mm tall
and starts at the chest floor, so at full extension the rod's top 37 mm stands
ABOVE the tower it is supposed to be engaged in, carrying nothing. Trimming to
the true requirement is free -- no mechanism, no height, no mass -- and it comes
off the overhang directly. Do it regardless of which option wins.

WHY OPTION C (INVERT: RODS ON THE CHEST, HANGING DOWN) IS WORSE, NOT BETTER
--------------------------------------------------------------------------
The instinct is that hanging them downward hides them in the body. It does not:
the SAME length has to go somewhere, and downward it runs out of robot. Hung
from the chest top the rod bottom lands below the chassis FLOOR when condensed,
which is the bottom protrusion the author explicitly refused, and the chassis floor is
a structural face rather than an open rim -- so it is a harder hole to cut than
the open well the upright arrangement drops into. Symmetric problem, worse site.

THE SWEEP CONSTRAINT IS REAL BUT CHEAPER THAN IT SOUNDS
-------------------------------------------------------
The author: "their path needs to be clear when the waist box slides." Two frames, and
mixing them up would cost a redesign:

    vs the CARRIAGE   the verticals do NOT move -- they ride the waist, which
                      rides the carriage. Plain holes, not slots.
    vs the CHASSIS    they sweep the full rail travel, TORSO_WALK..TORSO_WORK.
                      But the chassis well is an OPEN channel (the ledges are
                      its rim), so there is nothing to slot -- the question is
                      only what stands inside the well in that swath.

So this file measures the swept volume against the real chassis + rack solids
rather than reasoning about it, and reports the clearances it finds.
"""

import json
import math
from pathlib import Path

from build123d import Axis, Compound, Cylinder, Location, Align, import_step

import assembly_centaur as AC
import waist_rail as R
from interface_constants import CHASSIS_HEIGHT, CHASSIS_WIDTH

HERE = Path(__file__).parent
OUT = HERE / "output"

# ---------------------------------------------------------------- geometry in
# Everything imported or derived. Nothing here restates a dimension that
# another module owns (law 8); the few locals are this study's own knobs.
import marks as M

STROKE = M.STROKE                 # 250.0, chest travel
ROD_LEN = M.ROD_LEN               # 340.0 as drawn = STROKE + 90
ROD_D = M.ROD_D                   # 8.0
ROD_HALF_SPAN = M.ROD_HALF_SPAN   # 60.0, y of the verticals
TOWER_BACK = M.TOWER_BACK         # -49.5
TOWER_FRONT = M.TOWER_FRONT       # +49.5

TBOT = HERE.parent / "telescopebot" / "output"
CHEST_H = 85.0        # chest_box.py BOX_HEIGHT -- the box is a vendor-frame
TOWER_H = 48.0        # chest_box.py TOWER_HEIGHT: the bushing bore length
CHEST_GAP = 5.0       # marks.py: chest floor sits rim + 5 when condensed

# The Z stack, rebuilt exactly as marks.py builds it, so this study and the
# assembly cannot disagree about where anything is.
WAIST_BASE_Z = R.CAR_Z0 + R.CAR_T          # 92.0, waist box floor outside
WAIST_H = 60.0                             # waist_box.py RIM_Z
WAIST_FLOOR_T = 4.0                        # waist_box.py FLOOR_T
RIM_Z = WAIST_BASE_Z + WAIST_H             # 152.0, where the verticals stand
WAIST_INNER_Z = WAIST_BASE_Z + WAIST_FLOOR_T   # 96.0, inside the waist floor

# Waist interior occupants (waist_box.py): the battery bay stands on the floor
# and the spine servo hangs from the deck. Both are on the CENTRELINE, which is
# what makes the corner stations interesting.
BAT_BAY_H = 30.0
SPINE_SERVO_BOTTOM_Z = WAIST_BASE_Z + 39.1     # waist_box.py _spine_bottom_z

CHASSIS_FLOOR_T = 4.0                      # chassis.py FLOOR_T
WELL_FLOOR_Z = CHASSIS_FLOOR_T             # 4.0, inside the chassis floor
WELL_RIM_Z = CHASSIS_HEIGHT                # 72.0, the ledge plane


def rod_len_required(stroke=STROKE, chest_gap=CHEST_GAP, tower_h=TOWER_H):
    """The honest minimum length of a single-stage vertical.

    It must still be inside the bushing tower's TOP at full extension:

        chest floor, extended = rim + chest_gap + stroke
        tower top             = that + tower_h
        rod top must reach    = tower top

    Anything above the tower top at full extension is carrying nothing. As
    drawn ROD_LEN is 340 and this returns 303 -- 37 mm of dead steel that is
    also 37 mm of overhang.
    """
    return chest_gap + stroke + tower_h


def protrusion(rod_len, anchor_z=RIM_Z, chest_h=CHEST_H, chest_gap=CHEST_GAP):
    """How far the vertical stands above the closed chest's top face."""
    chest_top = RIM_Z + chest_gap + chest_h
    return max(0.0, (anchor_z + rod_len) - chest_top)


def _verticals(x_torso, rod_len, anchor_z=RIM_Z):
    """The four corner verticals as solids, in the robot frame."""
    out = []
    for sx in (TOWER_BACK, TOWER_FRONT):
        for sy in (1, -1):
            out.append(
                Cylinder(radius=ROD_D / 2, height=rod_len,
                         align=(Align.CENTER, Align.CENTER, Align.MIN))
                .moved(Location((x_torso + sx, sy * ROD_HALF_SPAN, anchor_z))))
    return out


def swept_depth_probe(depth, samples=14):
    """Sweep the four verticals' DOWNWARD extension through the full rail
    travel and intersect against the real chassis + rack solids.

    `depth` is how far below RIM_Z the verticals are asked to descend. Returns
    (interference_mm3, min_clearance_to_ways_mm).

    This is the measurement the author's constraint actually asks for, and it is done
    against imported geometry rather than against a mental model of it.
    """
    chassis = import_step(str(OUT / "chassis_half.step"))
    body = Compound(children=[chassis, chassis.rotate(Axis.Z, 180)])
    obstacles = [body]
    rack = OUT / "rail_rack.step"
    if rack.exists():
        obstacles.append(
            import_step(str(rack)).moved(Location((AC.RAIL_MID, 0, 0))))

    hit = 0.0
    for i in range(samples):
        t = i / (samples - 1)
        x_torso = AC.TORSO_WALK + t * (AC.TORSO_WORK - AC.TORSO_WALK)
        # only the part BELOW the rim matters for stowage
        for sx in (TOWER_BACK, TOWER_FRONT):
            for sy in (1, -1):
                stub = (Cylinder(radius=ROD_D / 2, height=depth,
                                 align=(Align.CENTER, Align.CENTER, Align.MAX))
                        .moved(Location((x_torso + sx, sy * ROD_HALF_SPAN,
                                         RIM_Z))))
                for ob in obstacles:
                    inter = stub & ob
                    if inter.volume > 1e-6:
                        hit += inter.volume
    # lateral clearance to the dovetail ways, which stand on the ledges at
    # LEDGE_Y and are the nearest thing to the rod line.
    way_inner_y = R.LEDGE_Y - R.WAY_HEAD_W / 2.0
    gap = way_inner_y - (ROD_HALF_SPAN + ROD_D / 2)
    return hit, gap


def available_depth():
    """How far a vertical can descend below the rim before it exits the robot.

    Reported as a stack so every millimetre is attributable, and so the
    occupied ones are visible rather than assumed away.
    """
    rows = [
        ("waist interior (rim -> inside waist floor)",
         RIM_Z - WAIST_INNER_Z, "FREE. clear at the CORNERS; battery + spine "
         "servo are both on the centreline"),
        ("waist floor + carriage plate",
         WAIST_INNER_Z - R.CAR_Z0,
         "FREE. solid, needs 4 clearance holes -- but the verticals do not "
         "move relative to the carriage, so holes, not slots"),
        ("the dovetail-way band",
         0.0, "BLOCKED by 1.00 mm -- see way_clash(); costs a 2 mm shift"),
        ("chassis well (ledge plane -> inside chassis floor)",
         WELL_RIM_Z - WELL_FLOOR_Z,
         "OPEN channel, no lid to slot; rack is on the centreline"),
    ]
    free = RIM_Z - (R.LEDGE_TOP + R.WAY_H)      # 68.0, reachable TODAY
    return rows, free, sum(r[1] for r in rows)


def way_clash():
    """The one obstruction on the way down, measured rather than assumed.

    The verticals stand at y = +/-ROD_HALF_SPAN because that is where the DONOR
    chest box was bored. The dovetail ways stand on the ledges at LEDGE_Y. In
    the 12 mm band the ways occupy, the two overlap by 1.00 mm -- so the
    descent is free to the carriage underside and then stops dead.

    A swept probe that stops above the band measures 0.0000 cm3, which is what
    makes this a 2 mm problem instead of a redesign: shift the verticals (and
    the chest tower bores) 2 mm inboard, or relieve the way head locally.
    """
    way_inner = R.LEDGE_Y - R.WAY_HEAD_W / 2.0
    rod_outer = ROD_HALF_SPAN + ROD_D / 2.0
    return dict(way_inner_y=way_inner, rod_outer_y=rod_outer,
                overlap=rod_outer - way_inner,
                band_z=(R.LEDGE_TOP, R.LEDGE_TOP + R.WAY_H),
                shift_to_clear=rod_outer - way_inner + 1.0)


def telescope(stages, stroke=STROKE, overlap=40.0):
    """Stowed length of an N-stage telescoping vertical.

    Each sliding joint carries stroke/N, and each stage must keep `overlap` of
    engagement when extended. Stowed length is one stage's travel plus the
    engagement, because the stages nest.
    """
    return stroke / stages + overlap


def main():
    print("=" * 74)
    print("ALPHA CENTAURI -- CHEST VERTICAL STOWAGE")
    print("=" * 74)

    chest_top_closed = RIM_Z + CHEST_GAP + CHEST_H
    print(f"\nthe closed stack (robot frame, ground at "
          f"{AC.GROUND_Z if hasattr(AC, 'GROUND_Z') else 'see marks'}):")
    print(f"  chassis well          {WELL_FLOOR_Z:7.1f} .. {WELL_RIM_Z:7.1f}")
    print(f"  carriage plate        {R.CAR_Z0:7.1f} .. "
          f"{R.CAR_Z0 + R.CAR_T:7.1f}")
    print(f"  waist box             {WAIST_BASE_Z:7.1f} .. {RIM_Z:7.1f}")
    print(f"  chest box, CLOSED     {RIM_Z + CHEST_GAP:7.1f} .. "
          f"{chest_top_closed:7.1f}")
    print(f"  vertical, as drawn    {RIM_Z:7.1f} .. {RIM_Z + ROD_LEN:7.1f}"
          f"   <- {protrusion(ROD_LEN):.0f} mm PROUD of the closed chest")

    # ---------------------------------------------------------------- option E
    need = rod_len_required()
    waste = ROD_LEN - need
    print(f"\n[E] TRIM THE DEAD LENGTH -- free, do it whatever else wins")
    print(f"    required = gap {CHEST_GAP} + stroke {STROKE} + tower "
          f"{TOWER_H} = {need:.0f} mm")
    print(f"    as drawn = {ROD_LEN:.0f} mm  ->  {waste:.0f} mm carries "
          f"nothing at full extension")
    print(f"    overhang {protrusion(ROD_LEN):.0f} -> "
          f"{protrusion(need):.0f} mm, for nothing")
    assert abs((STROKE + 90.0) - ROD_LEN) < 1e-9, "ROD_LEN convention moved"

    # ---------------------------------------------------------------- option B
    rows, depth_free, depth_total = available_depth()
    print(f"\n[B] RUN THEM INTO THE BODY -- the author's second idea, MEASURED")
    for label, mm, note in rows:
        print(f"    {label:<44} {mm:6.1f} mm   {note}")
    print(f"    {'reachable TODAY, nothing changed':<44} "
          f"{depth_free:6.1f} mm")
    print(f"    {'reachable AFTER the 2 mm shift':<44} "
          f"{depth_total:6.1f} mm")

    clash = way_clash()
    print(f"\n    THE ONE OBSTRUCTION, measured not assumed:")
    print(f"      dovetail ways stand y {clash['way_inner_y']:.1f}+ in the "
          f"z {clash['band_z'][0]:.0f}..{clash['band_z'][1]:.0f} band")
    print(f"      vertical's outer skin reaches y "
          f"{clash['rod_outer_y']:.1f}  ->  OVERLAP "
          f"{clash['overlap']:.2f} mm")
    print(f"      it is a {clash['band_z'][1] - clash['band_z'][0]:.0f} mm "
          f"band and a {clash['overlap']:.0f} mm interference, not a wall: "
          f"shift the")
    print(f"      verticals (and the chest tower bores) "
          f"{clash['shift_to_clear']:.0f} mm inboard, or relieve the way head.")

    hit_free, _ = swept_depth_probe(depth_free, samples=8)
    print(f"\n    swept probe over the full "
          f"{AC.TORSO_WORK - AC.TORSO_WALK:.0f} mm of rail travel:")
    print(f"      descending {depth_free:.0f} mm (to the carriage underside): "
          f"{hit_free / 1000.0:.4f} cm3   <- CLEAR TODAY")
    hit_all, _ = swept_depth_probe(depth_total, samples=8)
    print(f"      descending {depth_total:.0f} mm (into the well): "
          f"{hit_all / 1000.0:.4f} cm3   <- the way band, above")

    left = protrusion(need) - depth_total
    left_free = protrusion(need) - depth_free
    print(f"\n    overhang after E + B(today) = {protrusion(need):.0f} - "
          f"{depth_free:.0f} = {left_free:.0f} mm")
    print(f"    overhang after E + B(shifted) = {protrusion(need):.0f} - "
          f"{depth_total:.0f} = {left:.0f} mm   "
          f"{'STILL PROUD' if left > 0 else 'CLOSED'}")
    gap = -clash['overlap']

    # ---------------------------------------------------------------- option A
    print(f"\n[A] TALLER WAIST BOX -- the author's first idea")
    extra = max(0.0, left)
    print(f"    a taller waist raises the RIM, so it lifts the chest with it:")
    print(f"    the box must grow by exactly the overhang that is left over,")
    print(f"    and every millimetre is permanent height in BOTH poses.")
    print(f"    alone (no B):   waist {WAIST_H:.0f} -> "
          f"{WAIST_H + protrusion(need):.0f} mm, "
          f"+{protrusion(need):.0f} mm permanent")
    print(f"    after E + B:    waist {WAIST_H:.0f} -> "
          f"{WAIST_H + extra:.0f} mm, +{extra:.0f} mm permanent")

    # ---------------------------------------------------------------- option D
    print(f"\n[D] SPLIT IT -- telescoping stages (the only zero-height answer)")
    for n in (1, 2, 3):
        st = telescope(n)
        pr = max(0.0, st - (CHEST_GAP + CHEST_H))
        print(f"    {n}-stage: stowed {st:6.1f} mm -> overhang {pr:6.1f} mm"
              f"{'   <- closes with no added height' if pr <= 0 else ''}")
    print(f"    COST: a lead screw cannot telescope, so Mk1's drive must "
          f"change\n          (cable/chain-synchronised stages, or drive "
          f"stage 1 only).")
    print(f"          Mk2's ratchet racks have the same problem.")

    # ---------------------------------------------------------------- verdict
    print("\n" + "=" * 74)
    print("RECOMMENDATION")
    print("=" * 74)
    print(f"""
  Do [E] now -- {waste:.0f} mm of overhang for free, no mechanism, no mass.

  Then EITHER

    E + B + A   overhang {protrusion(need):.0f} -> {depth_total:.0f} into the
                body -> {extra:.0f} mm of extra waist. Both of the ideas quoted at the top of this file,
                and together they close it. Buys back nothing at all in
                mechanism risk: the verticals stay single, smooth and stiff.
                Costs {extra:.0f} mm of permanent height in the closed pose.

    E + D(3)    zero overhang, zero added height, chest stays {STROKE:.0f} mm
                of real travel -- but the drive is no longer a plain screw on
                either mark, and stage slop stacks at full extension.

  The first is cheap and boring and works. The second is the machine-tool
  answer and is a mechanism project. Given "feasible, properly functional,
  cheap", E + B + A is the recommendation, with D held for a Mk3 if the
  closed height ever becomes the binding constraint.
""")

    summary = dict(
        stroke=STROKE, rod_len_drawn=ROD_LEN, rod_len_required=need,
        dead_length=waste,
        overhang_drawn=protrusion(ROD_LEN), overhang_after_E=protrusion(need),
        body_depth_available=depth_total, overhang_after_E_B=left,
        waist_growth_needed=extra, swept_interference_free_mm3=hit_free,
        swept_interference_full_mm3=hit_all, depth_free_today=depth_free,
        way_clearance_mm=gap,
        telescope={n: telescope(n) for n in (1, 2, 3)},
    )
    (OUT / "stowage_summary.json").write_text(json.dumps(summary, indent=1))
    print(f"  -> {OUT / 'stowage_summary.json'}")
    return summary


if __name__ == "__main__":
    main()
