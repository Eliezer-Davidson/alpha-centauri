# TonyPi TALL — first print run (one of each, measure, adjust)

> **Note for the public copy of this repository.** The plates below reference STL
> files derived from HiWonder's own frame geometry. Those derived meshes are **not
> redistributed here** — see [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md)
> for what was removed and how to regenerate it. `fit_gauge.stl` and
> `mohawk_crest.stl` are this repository's own geometry, built from primitives
> with no vendor solid as input, and do ship.

Machine: ~~Bambu Lab H2C~~ **[STALE — see `edu/REPLAN-2026-08-28.md`: the H2C is
gone; the only printer is a Bambu A1 mini, 180 × 180 × 180 mm]**, 0.4 hardened
nozzle (what is physically installed), 0.20 mm layer, **PLA** (what is on the
shelf). Chamber OFF, no drying needed.
Files: `edu/print_files_tall/stl/`. Rationale: `edu/TONYPI-TALL-DESIGN.md`.

> **Changing the nozzle in the slicer is a declaration, not an action.** It
> swaps no hardware. Leave it at 0.4 unless you physically fit a 0.6 hotend.
> `NOZZLE_D` in `tall_constants.py` re-derives every wall from it — and 0.4 is
> the *better* nozzle for this design: 短U servo clearance 0.54 → **0.75 mm/side**.

## ⚠️ What run 1 in PLA can and cannot answer

| | |
|---|---|
| **ANSWERED** | every dimension — hole sizes, wall thickness, shrinkage, servo slot fit, whether brackets bolt up. PLA is the *best* fit-test material: dimensionally stable, no chamber, no drying. |
| **NOT ANSWERED** | whether a printed bracket survives standing on the robot. PLA is stiff (~3.5 GPa, above PETG) but **creeps** under sustained load and is brittle. A PLA leg feels right on the bench and sags over days. |

So run 1 = **fit + tolerance only**. Do not leave it holding the robot up.
COMPARE 1 ("does plastic hold?") waits for real filament — it needs PET-CF and
a 0.6 hardened nozzle. Run 1 answers COMPARE 2 ("does the redesign fit?").

**Total one-of-each: 208 cm³ ≈ 90 g of PLA.** Under a tenth of a spool.

---

## Plate 0 — print this ALONE, first

| file | vol | why |
|---|---|---|
| `fit_gauge.stl` | 37 cm³ | ~20 min. Resolves every tolerance unknown at once, without touching the robot. |

Slot ladder is now 21.04 / 21.44 / **21.64 (notched = design)** / 22.04 mm.
The gauge decides whether the leg links need a CAD change *before* you spend
four of them.

## Plate 1 — everything else, PLA, one of each

| file | vol | orientation |
|---|---|---|
| `脚板_platform.stl` | 112 cm³ | **sole down**, ~15% infill, zero support — the top plate is smaller than the sole, so it is a stepped shrink |
| `mohawk_crest.stl` | 27 cm³ | fin flat; the saddle arch needs support |
| `U梁_tall.stl` | 18.9 cm³ | pass-through |
| `长U支架_tall.stl` | 16.8 cm³ | on an **arm face** — keeps layers out of the bending path |
| `短U支架_tall_closed.stl` | 8.1 cm³ | the closed concept |
| `短U支架_tall.stl` | 6.0 cm³ | **same part, unclosed — the control.** Print both. |
| `斜U支架_tall.stl` | 6.7 cm³ | pass-through |
| `多功能支架_tall.stl` | 5.7 cm³ | pass-through |
| `L架_tall.stl` | 2.6 cm³ | pass-through |
| `一字支架_tall.stl` | 3.1 cm³ | flat |

The five unchanged pass-throughs are not waste — they are the golden baseline
(`renders/test_matrix.png`). 短U closed **and** unclosed on one plate is the
cleanest single-variable comparison in the set.

⚠️ The crest **will not fit the head yet**. `HEAD_W=55` / `HEAD_R=45` are
placeholders — there is no head-shell CAD. Print it as a shape check only.

---

# What to send back

This is the whole ask. Five items, and the design updates itself from them.

### 1. The gauge — six numbers

| measure | nominal | yours |
|---|---|---|
| plate length | 110.00 mm | |
| plate width | 56.00 mm | |
| plate thickness | 5.00 mm | |
| thick wall (free-standing) | 2.52 mm | |
| thin wall (free-standing) | 1.68 mm | |
| **lowest slot the LX-824HV slides into** | slot 3 = 21.64 (notched) | slot __ |

Slots run **narrowest → widest**; the notched one is the design value. If the
servo only goes into slot 4, `REINF_WALL` comes down. If it drops into slot 1,
there is margin to spend on a thicker, stiffer wall.

### 2. The gauge — four holes

| hole | nominal | yours | what it gates |
|---|---|---|---|
| | 3.10 mm | | M3 clearance through the foot plate |
| | 3.90 mm | | the loose M3 holes |
| | 7.00 mm | | boot screw-access bores |
| | 8.20 mm | | the servo hub — does the boss/bearing seat? |

Printed holes come out undersize. The delta here is the compensation every hole
in the design needs.

### 3. Head measurements — unblocks the crest

Width across the head where a saddle would sit, and the front-to-back radius of
its crown. Two caliper readings; the saddle regenerates to fit.

### 4. Bracket quantities — count them on the robot

The repo has **no BOM** and the Tony Pi PDF is a quick-start with no exploded
views. The robot is 18-DOF (read from the `.d6a` SQLite schema: `Servo1`…
`Servo18`). Known: 脚板 ×2, and the height math needs exactly 2 × 长U支架 per
leg. Everything else is a count with the robot in front of you.

### 5. ~~One ruling~~ — ANSWERED 2026-07-31

> *"there are no wires or plugs on the tonypi's footplates."*

The vendor plate has 25 holes: 16 M3-size and **9 large** (Ø8.0, Ø8.1, Ø15.8).
Nothing passes through the large ones, so they are lightening holes and sealing
them costs nothing functionally.

**→ Print `脚板_platform.stl`** (112.2 cm³, large holes blind). It gives a
continuous, stronger sole with no edges to catch on the floor.

`脚板_platform_open.stl` (98.2 cm³, bored through) stays in the folder as a
spare — the only reason to switch is if a lighter foot ever matters more than
sole integrity (foot mass sits at the end of the swing leg), but at 15% infill
the difference is a few grams.

*(The nozzle question is settled: 0.4 hardened, confirmed installed. Walls
re-derived — `WEB_WALL` 2.52 unchanged, `REINF_WALL` 1.89 → 1.68.)*

---

## What happens with the answers

`cad/tonypi_tall/tall_constants.py` holds every number this design uses. Hole
compensation, wall thickness and saddle fit are all single-line changes there;
`build_all.py` regenerates all 11 parts in about a minute. Nothing is
hand-modelled, so nothing has to be re-modelled.
