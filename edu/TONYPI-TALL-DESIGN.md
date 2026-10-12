# TonyPi TALL — printed-frame design (v1, for review)

> **Note for the public copy of this repository.** Several artefacts this file
> points at are renders *of* HiWonder's geometry, or are regenerated from it, and
> are **not redistributed here**: `renders/review_sheet.png`,
> `renders/hero/stock_vs_tall.png`, `renders/hero/new_pieces.png` and
> `build_report.json`. See [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) for
> what was removed and how to regenerate it. `renders/height_comparison.png`,
> `renders/test_matrix.png` and the two own-geometry hero renders do ship.
>
> **Superseded numbers, left standing.** This file is the 0.6-nozzle era. The
> shipped design is the **0.4** nozzle, and
> [`edu/print_files_tall/PRINT-PLATE.md`](print_files_tall/PRINT-PLATE.md)
> supersedes it: `REINF_WALL` **1.89 → 1.68 mm**, servo-channel clearance
> **21.22 → 21.64 mm**, per-side margin **0.54 → 0.75 mm/side**. `WEB_WALL` is
> 2.52 mm either way. `cad/tonypi_tall/tall_constants.py:111` re-derives all of
> it from `NOZZLE_D`; `cad/tonypi_tall/fit_gauge.py` prints the shipped values.
> As everywhere in this project, the original text below is annotated, not
> rewritten.

**Status: DESIGN FOR REVIEW — nothing printed, nothing committed.**
Regenerate everything: `edu/.cadenv/bin/python cad/tonypi_tall/build_all.py`
Outputs: `edu/print_files_tall/` (step/, stl/, renders/, build_report.json)
Visual review: `edu/print_files_tall/renders/review_sheet.png` (not shipped — regenerate, see banner) ·
height budget: `edu/print_files_tall/renders/height_comparison.png`

Shaded renders (`edu/print_files_tall/renders/hero/`), orange = added material:
- `stock_vs_tall.png` — each pair at ONE shared scale, on a common floor (not shipped — regenerate, see banner)
- `new_pieces.png` — the five changed parts, 4 views each (not shipped — regenerate, see banner)
- regenerate: `edu/.cadenv/bin/python cad/tonypi_tall/hero_sheet.py` then
  `… compare_sheet.py`. Renderer: `edu/tools/hero_render.py` (software
  rasteriser — no GPU on this machine).

## 1. What the variant is

A copy of the eight `edu/print_files` structural parts, parametrically edited
(build123d, all numbers in `cad/tonypi_tall/tall_constants.py`) into a taller,
printed TonyPi, plus one new part. The height move is honest about where the
safe ceiling is — the analysis in `edu/CAD-DECISION.md` §4 sets it, and it is
lower than intuition wants.

| Part | Stock | Tall v1 | Change |
|---|---|---|---|
| 长U支架 leg/arm link | 56 × 64.5 × 25, 8.15 cm³ | 56 × **78.5** × 25, 16.76 cm³ | **+14 mm** stretch through the hole-free arm band (station y=23.5, section exactly 100 mm²), plus a **closed box section** over y[6.0, 33.5] — the 31.6 mm of channel the stretch opens up *below the servo*. See §2b: v1 closed the extension zone instead and fouled the servo |
| 脚板 foot plate | 63 × 123 × 2 | **82 × 132 × 12** | **platform boot**: 10 mm sole, rounded 82×132 footprint, original plate kept 1:1 as top skin, 16 screw-access bores (Ø7) under every M3 hole, chamfered rim |
| 一字支架 strap | 63 × 25 × 2 | **73** × 25 × 2 | +10 mm stretch at a hole-free band (x=19) |
| mohawk_crest | — | 60 × 85 × 110, 27.4 cm³ | **NEW**: clip-on spartan crest — saddle arc + zip-tie skirt tabs, 7-spike fin, ~+40 mm apparent height |
| 短U支架 short U | unchanged | pass-through + `_tall_closed` **concept**, 8.34 cm³ | closure mid-span at **1.89 mm** wall (3 extrusions — see §2b/§4b); leaves 0.54 mm/side on the servo. **Test-fit a real LX-824HV before printing** |
| 斜U / 多功能 / L架 / U梁 | unchanged | pass-through | see §3 — no assembly data proves added webs clear |

All 10 outputs: single valid solids, watertight STLs (verified with trimesh),
volume deltas exact against section-area × extension arithmetic.

## 2. Why +38 mm and not more ("as tall as safely possible")

Height gain: legs 2 × 14 = **+28**, sole **+10** → **380 → 418 mm (+10%)**;
mohawk adds ~40 mm of looks on top. The ceiling argument (CAD-DECISION §4):

- **Servo thermal duty, not stall torque, is the wall.** Worst standing pose
  (knee, 30° flexion, single support) already costs 141% of the LX-824HV's
  continuous budget on the stock robot. At k=1.30 it becomes 184% → mid-stride
  cutout risk. At our k≈1.175 it is ~166%, and the lighter printed structure
  claws back roughly 7% → **~155%**. That spends real margin; it is the
  furthest defensible point, not a free lunch. The "plastic is lighter" leeway
  is real but small: servos are 52% of robot mass and are not printed.
- **Mandatory companion:** rescale every `.d6a` keyframe duration by
  K_JOINT = 1.175 (`D6A_TIME_SCALE`), which returns dynamic torque to stock
  for free. Without it, dynamic torque rises k² = +38%.
- **Feet outscale the height on purpose.** Width 63 → 82 (×1.30) grows the
  support polygon faster than the CoM rises (×~1.12), so static tipping
  margin **improves ~16%** despite the extra height.
- **Stiffness was the honest weak spot — the H2C shrinks it.** A closed-box
  *PETG* link is torsionally sound but lands at roughly **4–8× stock
  deflection** (aluminium E is ~33× PETG's; the box buys most of that back, the
  1.22³ length factor spends some). The H2C's 65 °C heated chamber makes
  **PET-CF** printable, at 2.7× PETG's modulus → roughly **1.5–3×**. See §4b;
  it also fixes a heat problem the 155% duty figure above implies.
  **No PLA anywhere structural** (creep).

## 2b. The servo-envelope correction (v1 was wrong here)

v1 closed the sides over the *extension zone*, justified as "new material is
guaranteed servo-free". **That justification was false.** `find_stretch_station`
proves a band is **hole-free**; hole-free is not empty. On these brackets the
servo body sits *inside* the U.

Measured (`cad/tonypi_tall/servo_envelope.py`, registering the vendor
`LX-824HV.STEP` to each bracket's Ø8.20 hub hole):

| | |
|---|---|
| LX-824HV | 40.04 × 52.54 × 20.14 mm, output boss Ø5.04 |
| shaft position | 30.02 mm from the body's far end, 10.02 from the near end |
| 长U支架_tall hub | y = 64.00 → **servo body occupies y [33.97, 74.01]** |
| v1 closure band | y [22.50, 38.50] → **overlapped the servo by 4.53 mm** |
| across the channel | 25.00 − 2×2.5 = 20.00 clear vs a 20.14 servo → **−0.14 mm** |

So v1 fouled the servo two different ways. The fix is not a compromise — the
stretch *opens* 31.6 mm of channel below the servo (floor y≈0.35, servo starts
y=33.97), so closing **y [6.0, 33.5]** gives full-thickness walls, 0.47 mm of
clearance, and roughly **twice the closed length** v1 had. Volume 13.71 →
16.76 cm³. (The band starts at 6.0, not 1.85, to clear a servo horn disc up to
~5.6 mm thick on the web — the one dimension the manual cannot settle.)

短U支架 has no such luck: its servo spans y [−2.02, 38.02] inside a y[−2, 40.5]
bracket — **end to end, no servo-free span exists**. Closure is only possible by
thinning the wall: at 1.89 mm (3 extrusions, §4b) that is 21.22 clear vs 20.14
→ **0.54 mm/side**. Still inside FDM tolerance, which is why it stays a CONCEPT
part and why the check is a test-fit, not just the swing check §3 originally
called for.

Re-run the check any time: `edu/.cadenv/bin/python cad/tonypi_tall/servo_envelope.py`

## 3. What is deferred, and exactly why

- **Torso raise (+20 mm)**: the Tony Pi.pdf turned out to be a quick-start
  manual — no exploded views, no dimensions. U梁's orientation is unverifiable
  from it; stretching a *horizontal* beam widens instead of heightens. One
  look at the actual robot resolves it; the constant (`BEAM_EXT`) is wired in
  and ready.
- **Closed sides on 短U/斜U joint brackets**: measured in §2b — 短U's servo
  fills the bracket end to end, so the concept part runs 1.89 mm walls with
  0.54 mm/side. Test-fit a real LX-824HV *and* check the swing envelope before
  printing. 斜U has not been measured (its hub is not on a principal axis).
- **Head**: **we do not have the head shell CAD** — `LFD-01.stp` is the head
  *servo*. The mohawk is therefore a standalone clip-on with `HEAD_W=55` /
  `HEAD_R=45` as placeholder guesses. Caliper the head (or find/scan the
  shell) and the saddle regenerates to fit.
- **Unverified inputs inherited from CAD-DECISION**: stock height 380, link
  length 80 joint-to-joint, bracket hole pitches. Measure once, re-run.

## 4. Staged bring-up (one variable at a time, A/B vs golden baseline)

0. **Test-fit coupon first** — §2b's clearances (0.47 mm along the U, 0.54 mm
   per side on 短U) are inside FDM tolerance. Print the closure band alone and
   slide a real LX-824HV into it before committing to a full set.
1. **Coupon**: print the servo hole-pattern plate, bolt a real LX-824HV to it.
2. **Stock-length closed-box 长U** (change material+section only): stock
   `.d6a` untouched. If stock gaits walk, the frame concept is proven.
3. **Tall legs** (+14/+14) + platform boots + `.d6a` retarget (×1.175 timing).
4. Torso raise + joint-bracket closures after their checks. Mohawk any time.

## 4b. Printing it on the Bambu Lab H2C

⚠️ `edu/print_files/orca_presets_cli` is for a **FlashForge Guider 3 Plus,
0.4 nozzle, PLA/PETG only** — it does not apply. Nothing in it is right for
this machine.

**Machine** (330 × 320 × 325 mm, 350 °C nozzles, 120 °C bed, **65 °C actively
heated chamber**, Vortek toolchanger 1+6 hotends, up to 4× AMS 2 Pro / 8× AMS
HT = 24 filaments). Largest part here is the boot at 132 mm — everything fits
with room for a full leg set on one plate (`build_all.py` asserts this).

**The chamber changes the material call, and that was the weak spot.** §2 said
plain PETG lands at ~4–8× stock deflection. Published bending moduli:

| | modulus | tensile | impact | HDT |
|---|---|---|---|---|
| PETG | ~2.0 GPa | — | — | ~70 °C |
| PETG-CF | 2.91 GPa | 70 MPa | 41.2 kJ/m² | 74 °C |
| PAHT-CF | 4.23 GPa | 125 MPa | **57.5** kJ/m² | — |
| **PET-CF** | **5.32 GPa** | 131 MPa | 36.0 kJ/m² | **205 °C** |
| Al 6061 (today) | 69 GPa | | | |

- **长U links + 短U concept → PET-CF.** 2.7× stiffer than plain PETG takes the
  closed-box link to roughly **1.5–3× stock deflection**. Second, independent
  reason: §2 has the knee at ~155% of the servo's *continuous* thermal budget,
  so the bracket clamping it runs hot — a 74 °C HDT is the wrong side of that
  line, 205 °C is not. Swap to **PAHT-CF** if falls rather than deflection turn
  out to be the failure mode (+60% impact, −21% stiffness).
- **脚板 boots → PETG / PETG-CF.** A 10 mm slab in compression; stiffness is not
  binding, toughness and grip are. ~15% infill. Chamber OFF for PETG.
- **mohawk → PLA.** Unloaded and decorative — the one part where colour is the
  point. No PLA anywhere structural (creep, CAD-DECISION §4d).

**Nozzle: 0.6 hardened steel** (Bambu's own recommendation for any CF/GF
filament; tungsten carbide also offered). Wall thicknesses are snapped to whole
multiples of the 0.63 mm extrusion width so walls print as pure perimeters with
no gap fill: `WEB_WALL = 2.52` (4 lines at 0.6, and exactly 6 at 0.4 — the one
value correct on both nozzles), `REINF_WALL = 1.89` (3 lines). That last one is
not cosmetic: it also widens the 短U servo clearance from 0.43 to **0.54 mm per
side**. On a 0.4 nozzle use 1.68 (4 lines) → 0.75 mm/side.

**Orientation** — the layer plane must not be the shear plane:
- boot: **sole down**, flat. The plate on top is smaller than the sole, so it is
  a stepped shrink — zero support, and the 16 access bores print as clean
  vertical holes.
- 长U link: lay it on an **arm face** so the closed box's axis is parallel to
  the bed. Web-down would stand the arms up and put layer adhesion directly in
  the bending path. Confirm in the slicer before committing.
- crest: fin flat on the bed; the saddle arch then needs a support interface —
  which is exactly what the AMS is for (a support-interface filament peels
  clean where PETG-on-PETG will not).

Dry PET-CF and PAHT-CF before printing; PAHT-CF absorbs moisture even at its
reduced rate.

## 5. Licence

HiWonder's CAD carries no licence (all rights reserved by default). Personal
build: fine. **Selling anything derived from these brackets needs their
written permission** (`support@hiwonder.com` — same email can return the
whole-robot STP and the head shell).
