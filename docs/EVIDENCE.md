# Evidence index

Every claim on the [README](../README.md) maps to a file in this repository, a
line of source, or a command that reproduces it. This page is that map.

The reproduction below was run **at publication time**, from a clean export
(see [PROVENANCE](../PROVENANCE)), using
`edu/.cadenv/bin/python` (3.11, build123d) and `.venv/bin/python` (3.12,
mujoco 3.12) with `MUJOCO_GL=glx` and a live `DISPLAY`. Whole chain: 348 s.

---

## Simulation results

| Claim | Value | Where it comes from |
|---|---|---|
| WALK crawl distance | 145.0 mm of 150 mm | `docs/evidence/sim_results.json` → `runs.walk_chest.crawl.distance_mm` |
| WALK cycles / falls | 3 / 0 | same → `completed: true`, `fall_t: null` |
| WALK min three-foot margin | 15.0 mm | same → `min_margin_3ft_mm` |
| WALK deficient contact | 0.0 s, 0.0 % | same → `deficient_contact_s`, `deficient_contact_pct` |
| IK↔FK closed-loop grid error | 1.67e-09 m | same → `runs.walk_chest.ik_grid_max_err_m` |
| Peak crawl torque at WALK | 1.41 N·m | same → `max(runs.walk_chest.crawl.tau_max)` = 1.4090 |
| Peak crawl torque at WORK | 2.00 N·m = 81 % of the limit | same → `max(runs.work_chest.crawl.tau_max)` = 1.9977 |
| Measured servo limit | 2.4516625 N·m (25 kg·cm) | same → `torque_limit_Nm`; the constant is `cad/alpha_centauri/hand_load.py:47` (`SERVO_MEASURED_KGCM = 25.0`) |
| 57 % of the limit | 1.4090 / 2.4516625 = 0.5747 | computed from the two rows above |
| No joint saturated at kp 60 | `saturated_joints_frac: {}` | same → all four runs |
| kp 280 sweep, margins | WALK 16.6 mm, WORK 2.4 mm, four knees saturated 0.1–0.2 % (`saturated_joints_frac` 0.0009–0.0017) | `sensitivity_kp280.{walk,work}_chest.crawl.min_margin_3ft_mm` |
| kp 280 sweep, deficient contact | WALK 0.0 %, WORK **4.5 %** (vs 16.9 % at kp 60) | `sensitivity_kp280.work_chest.crawl.deficient_contact_pct` |
| WORK min three-foot margin | 2.2 mm | `runs.work_chest.crawl.min_margin_3ft_mm` |
| WORK deficient contact | 3.9 s, 16.9 % | same → `deficient_contact_s` 3.86, `deficient_contact_pct` 16.9 |
| WORK recovery shift | 45.2 mm lateral | `runs.work_chest.work_failure_math.lateral_shift_for_walk_margin_mm` |
| WORK recovery extension | 263.98 mm = 98.4 % of reach, guard 260.09 mm | same → `extension_at_recovery_shift_mm`, `extension_pct_of_reach`, `extension_limit_mm` |
| Brain-aft A/B | WORK 2.2 → 9.4 mm, WALK 15.0 → 10.7 mm | `runs.work_aft.crawl` and `runs.walk_aft.crawl` |
| Model total mass | 4.9734 kg vs a ledger of about 4.505 kg, +468 g (the file rounds the ledger to 0 dp and takes the delta from the unrounded ledger, so 4973.4 − 4505.0 ≠ 468.0 exactly) | [`docs/evidence/provenance.json`](evidence/provenance.json) → `mass_reconciliation`, and `sim/mjcf_export.py` stdout |
| 20 STEP files snapshotted | `step_files_count: 20` | same file (count computed at export, never hard-coded) |
| Nominal (not STEP-measured) mass in the model | 2 517.6 g of 4 973.4 g: packs 2 × 300, servos 12 × 74.5, joint parts 4 × 9.3, arm halves 2 × 250, torso remainder 271.4, compute stack 215 (point mass) | same file → `links.*.parts` entries carrying `box_mm` or `_NOMINAL`, and `torso_chest.mass_kg − torso.mass_kg` |

### Reproduction, and what drifted

Re-running the full chain reproduced the committed `docs/evidence/sim_results.json`
**exactly** for every headline number: all four `min_margin_3ft_mm`
(15.0 / 2.2 / 10.7 / 9.4), all four `deficient_contact_pct`
(0.0 / 16.9 / 0.1 / 1.8), the WALK distances (145.0, 144.6), the torque limit,
and the `work_failure_math` block bar two of its eight fields.

Twenty values moved in their last digit. They are listed here rather than
rounded away:

| field | committed | fresh |
|---|---:|---:|
| `runs.work_chest.crawl.distance_mm` | 92.0 | 92.1 |
| `runs.work_chest.crawl.min_margin_per_swing_mm.fl` | 3.2 | 3.4 |
| `runs.work_chest.crawl.deficient_contact_samples` | 966 | 968 |
| `runs.work_chest.crawl.deficient_contact_s` | 3.86 | 3.87 |
| `runs.work_chest.work_failure_math.measured_stand_com_x_mm` | 35.25 | 35.22 |
| `runs.work_chest.work_failure_math.extension_at_recovery_shift_mm` | 263.98 | 263.97 |
| `runs.walk_aft.crawl.deficient_contact_samples` | 6 | 5 |
| `sensitivity_kp280.walk_chest.crawl.min_margin_mm` (×3 fields) | 16.6 | 16.7 |
| `sensitivity_kp280.work_chest.crawl.distance_mm` | 99.7 | 99.6 |
| `sensitivity_kp280.work_chest.crawl.min_margin_mm` (×3 fields) | 2.4 | 2.5 |
| `sensitivity_kp280.work_chest.crawl.deficient_contact_samples` | 259 | 256 |
| `sensitivity_kp280.work_chest.crawl.deficient_contact_s` | 1.04 | 1.02 |
| `com_heights_mm` (×4) | 269.5 / 269.48 / 262.71 / 262.71 | 269.47 / 269.45 / 262.68 / 262.68 |

That is contact-solver noise at the reporting precision, not a change in any
conclusion. **The README quotes the committed values everywhere**, including the
two places it previously quoted the fresh run: the kp-280 margins are given as
16.6 / 2.4 mm and the WORK recovery extension as 263.98 mm. A re-run moves both in
their last digit, which is what this table is for.

### The one confound in the kp-280 sweep

The sweep runs `n_cycles=2` (`cad/alpha_centauri/sim/crawl_sim.py:706`, with the
confound written out at `:696`). The WORK baseline is also 2 cycles, so **the WORK
pair is a like-for-like comparison**. The WALK baseline is 3 cycles
(`crawl_sim.py:620`), so **the WALK pair is not**: a minimum taken over two
cycles has fewer chances to find a low margin than one
taken over three, and part of WALK's 15.0 → 16.6 mm is the shorter run rather than
the stiffer gain. Raising the sweep to 3 cycles would change the committed
`sensitivity_kp280` block, so the confound is recorded instead — in this file, in
the README, and in a comment at the line that causes it.

### The provenance file, and the two fields changed in it

[`docs/evidence/provenance.json`](evidence/provenance.json) is the export snapshot
from the publication run: 20 STEP hashes, every constant the exporter used, the
assumptions it did **not** measure, and the mass reconciliation. Two fields were
rewritten for publication and nothing else was touched — `interpreter` held an
absolute path under the author's home directory, and `git_rev` held the working
repository's revision id. The file says so in its own `_public_copy` key.

Its `generated` timestamp is `2026-09-23T13:50:38Z`, about two minutes later than
the `provenance_generated` recorded inside `sim_results.json`
(`2026-09-23T13:48:10Z`): the exporter was re-run after the crawl. The numbers
quoted from it above are the ones in the file that ships.

---

## Geometry, measured at build time

| Claim | Value | Command that prints it |
|---|---|---|
| Chassis bed gate, all four parts | inner quarter 125.0 × 160.0 × 72.0 mm / 180.2 g / 3.4 % support; outer quarter same envelope / 229.4 g / 3.0 %; splice key 11.6 × 11.7 × 5.7 mm (print pose; 5.7 × 11.7 × 11.6 on the render) / 0.7 g; abduction pod 72.0 × 34.2 × 70.0 mm / 43.9 g / 6.8 % | `cad/alpha_centauri/chassis.py` → "BED GATE (measured bbox in print pose vs A1 mini 180 × 180 × 180)" |
| Outer quarter with pods printed in | 125 × 208.3 × 72 mm, fits in no orientation | `cad/alpha_centauri/chassis.py:139`, `interface_constants.py:479` |
| Abduction pod, thigh and hip module PRINT-BLOCKED | servo height 35.00 vs 37.80 mm | `chassis.py` final line; `thigh.py:282`; `hip_module.py:566` |
| Thigh known defect | upper cover-bolt pair cut in air at z = 149.40 vs part top 146.00; cover bolts only at the lower pair | `thigh.py:285` → "KNOWN DEFECT" |
| Spine pawl leaf spring cannot deflect | the leaf is fused to the carrier over its whole 40 mm length; every sweep is a rigid translation of the pawl; a relief pocket is needed before the ratchet can work | `spine_lock.py` docstring, "FOLLOWUPS FOUND WHILE FIXING" |
| Spine rack monolith height | 288 mm (24 teeth × 12 mm pitch) | `cad/alpha_centauri/spine_lock.py:58` |
| Rack split, stroke preserved | split 12+12 at z = 144, stroke 250 mm | `spine_lock.py` → "ALL GATES GREEN" line |
| Seam parity vs the monolith | 0.0000 mm³ in the tooth band; pawl at full seat on teeth 5/11/12/18 → 0.000 mm³ assembled *and* monolithic; 49-pose deflected sweep 0.0000 mm³; 21×49-pose release sweep 0.0000 mm³ | `spine_lock.py` → "seam gates" block |
| Foot, two materials | core 8.9 cm³ PETG (8.5 g) + tread 3.6 cm³ TPU (4.4 g) = 12.8 g per foot, 51.4 g ×4 | `cad/alpha_centauri/foot.py` |
| Foot retention | 0.8 mm bead into a 57–74° groove; 1.0 mm pull-off → 10.4 mm³ solid interference | `foot.py` → "retention:" line |
| Foot swept clearance | 0–54.4° over 8 azimuths (37.94 swing + 11.48 patch + 5.0 margin), min TPU-to-PETG ground clearance 2.71 mm at 55° tilt | `foot.py` → "swept" line |
| Dock, 8 parts | largest 178.0 × 100.0 × 8.0 mm, heaviest 141.9 g, worst support 5.4 % | `cad/alpha_centauri/dock.py` → "PART TABLE" then "ALL GATES PASS" |
| Stowage swept interference | 0.0 mm³ free, 1856.1 mm³ full **as committed** — the full case does not reproduce, see below | `docs/evidence/stowage_summary.json` |
| Chest verticals not stowed | 250 mm proud as drawn; 1.00 mm vertical-to-way overlap over a 12 mm z band (`way_clearance_mm: -1.0`); 77 mm of overhang left after trimming the 37 mm dead rod and running them into the body, bought back with +77 mm of permanent waist height (`waist_growth_needed: 77.0`) | `cad/alpha_centauri/extension_stowage.py` → "[B] RUN THEM INTO THE BODY", "THE ONE OBSTRUCTION", "RECOMMENDATION"; the same numbers in `docs/evidence/stowage_summary.json` |
| Ride height / footprint / leg extension | 199.0 mm / 500 × 279.2 mm / 249.30 mm = 93.0 % of 268.14 mm reach | `cad/alpha_centauri/assembly.py` |
| Standing height | 671 mm extended vs an 850 mm target, 179 mm short | `assembly.py` → "STANDING HEIGHT ... EXTENDED" (**requires stage 2 first** — see BUILD.md) |
| Mk1 / Mk2 envelope | 590.3 × 414.4 × 692.0 mm, 2556.25 vs 2615.45 cm³ | on-canvas captions of `docs/evidence/mk1_work.png` and `mk2_work.png` |

### The one geometry number that does NOT reproduce

`swept_interference_full_mm3: 1856.1203262780346` in the committed
`docs/evidence/stowage_summary.json` **is not reproducible from this checkout.**
Rebuilding the whole chain and re-running `extension_stowage.py` returns
**0.0 mm³** for that field. It is 0.0 at 8 sweep samples (what `main()` uses),
and still 0.0 at 14 and 28, so it is not a sampling artifact. It is the **only**
field that moves: the other 13 in that file reproduce exactly, including the two
this page and the README quote as open costs (`way_clearance_mm: -1.0`,
`waist_growth_needed: 77.0`).

`swept_depth_probe()` intersects the four verticals against exactly two solids —
the chassis halves and the rail rack — so one of those two has moved since the
study was last run. Neither is committed here, because generated CAD is not
committed, so the 1856.1 cannot be re-derived against the geometry that produced
it. It can only be reported as not reproducing.

**The evidence file is left byte-for-byte as it was recorded, and the claim is
corrected instead.** Overwriting the JSON with a fresh 0.0 would make the page
agree with itself by editing the evidence, which is the one move this project
does not make. Whether to re-run the study and re-commit the file is the
author's call, not a fix that belongs in a documentation pass.

One more thing that sweep does not do: the dovetail ways are **not** in its
obstacle set. The 1.00 mm vertical-to-way overlap is computed analytically by
`way_clash()` from `LEDGE_Y`, `WAY_HEAD_W`, `ROD_HALF_SPAN` and `ROD_D`, and a
0.0 mm³ sweep result never contradicted it.

## Laws, and the mistake each one cost

| Claim | Where |
|---|---|
| Carriage read 24.1 % support until graded in its print pose; flipped, 0.5 %; bed contact 4 000 → 24 511 mm² | `cad/alpha_centauri/build_report.py:206-211` |
| First-layer facets turned a real 4.8 % chassis support requirement into 23.4 % | `edu/tools/partcheck.py`, "THE FIRST-LAYER TRAP" (line 36) |
| A calf sat 1.62 cm³ inside a thigh and passed every single-part check | `cad/alpha_centauri/calf.py:158,280`; `waist_rail.py:831` |
| `L1` is a diagonal: 49.60 outboard **and** 14.30 up; hypot = 51.62024721 | `cad/alpha_centauri/interface_constants.py:55-84`, `assembly.py:164-165,317` |
| 25 kg·cm measured, 50 kg·cm datasheet peak never used | `cad/alpha_centauri/hand_load.py:47-48` |

## Scale

These four numbers are re-derived by running the command beside each one after **any** edit to a
`.py` file.

| Claim | Value | Command |
|---|---|---|
| Lines of Python | 17 586 | `find . -name '*.py' -print0 \| xargs -0 wc -l \| tail -1` |
| Modules | 54 | `find . -name '*.py' \| wc -l` |
| `assert` statements, whole repo | 181 | `grep -rh '^\s*assert ' --include='*.py' . \| wc -l` |
| `assert` statements, `cad/alpha_centauri/` | 167 | `grep -rhc '^\s*assert ' cad/alpha_centauri --include='*.py' \| paste -sd+ \| bc` |
| Fit gauge volume | 36.98 cm³, 110.0 × 56.0 × 23.0 mm | `trimesh.load('edu/print_files_tall/stl/fit_gauge.stl').volume` |
| Mohawk crest volume | 27.43 cm³, 60.0 × 84.9 × 110.0 mm | same, on `mohawk_crest.stl` |

## Figures

`docs/media/` holds only the images the README inlines. `docs/evidence/` is the
full proof set — 36 PNGs and three JSON files — and every one of them is
regenerated by the code that makes the claim it illustrates. All are CAD renders,
matplotlib charts or MuJoCo screenshots; there are no photographs in this
repository.

Most of `docs/media/` is a web-sized copy or crop of the `docs/evidence/` render
of the same subject, so the code in the table below regenerates its source. Four
`docs/media/` images are not copies of anything in `docs/evidence/`; they get
their own table after this one.

Two conventions run through the table below. The **sim charts** are drawn
directly by `cad/alpha_centauri/sim/crawl_sim.py`. The **part renders** are
tessellated out of a STEP solid that the named part module writes into its
`output/` directory, and drawn headless by `edu/tools/render_step.py` (four views,
shared scale, measured bounding box in the caption) or `edu/tools/hero_render.py`
(shaded, single subject). No GPU and no viewer are involved in either.

| file | what it shows | written by |
|---|---|---|
| `com_support_walk.png` | CoM path over the support triangles, and support margin vs time, for the WALK crawl | `sim/crawl_sim.py` |
| `crawl_walk_contactsheet.png` | eight mid-phase MuJoCo frames of cycle 2 of 3 (the shifts, the four swings and the end pause), each titled with its time and phase; the support triangles and CoM path are in `com_support_walk.png`, not on these frames | `sim/crawl_sim.py` |
| `work_failure_strip.png` | the WORK station at its worst margin, beside both stations' margin traces | `sim/crawl_sim.py` |
| `torque_vs_limit.png` | peak joint torque at the static stand and over the WALK crawl, against the measured servo limit | `sim/crawl_sim.py` |
| `brain_ab.png` | the phone/compute placement A/B — CoM by station and brain location, and the resulting crawl margins | `sim/crawl_sim.py` |
| `chassis_quarters_assembly.png` | the four chassis quarters assembled into the 500 mm chassis | `chassis.py` |
| `chassis_quarters_splice_key.png` | the splice joint exploded: bolt bores, head and nut slots, loose registration keys | `chassis.py` |
| `chassis_quarters_outer_bay.png` | the outer quarter's battery bay and contact face | `chassis.py` |
| `chassis_pod_bolted.png` | the abduction pod bolted on rather than printed in — the fix for the 208.3 mm bed failure | `chassis.py` |
| `chassis_pod_joint.png` | the pod-to-quarter joint in detail | `chassis.py` |
| `chassis_pod_print_pose.png` | the pod in the orientation it is graded and printed in | `chassis.py` |
| `hip_module_hero.png` | the hip module, shaded | `hip_module.py` |
| `hip_leg_chain_hero.png` | chassis half + hip module + thigh + calf as one chain, with the measured envelope | `assembly.py` |
| `foot_hero.png` | the assembled two-material foot | `foot.py` |
| `foot_on_calf_hero.png` | the foot seated on the calf | `foot.py` |
| `foot_split_core.png` | the PETG core alone | `foot.py` |
| `foot_split_tread.png` | the TPU tread alone | `foot.py` |
| `foot_split_section.png` | section through the snap: the 0.8 mm bead seated in the dome groove | `foot.py` |
| `spine_rack_upper_hero.png` | the upper half of the split ratchet rack | `spine_lock.py` |
| `spine_rack_lower_hero.png` | the lower half | `spine_lock.py` |
| `spine_rack_seam_engaged_hero.png` | the pawl engaged across the 12+12 seam — the parity claim's picture | `spine_lock.py` |
| `spine_pawl_tab_fix.png` | the pawl fully seated on tooth 12 (0.000 mm³, engagement 3.700 mm), release ears outside the rack width — the figures on its own canvas | `spine_lock.py` |
| `waist_rail_segmented_ways.png` | the segmented rail ways | `waist_rail.py` |
| `waist_rail_carriage_halves.png` | the carriage split into printable halves | `waist_rail.py` |
| `waist_rail_joint_key.png` | the rail-way joint key | `waist_rail.py` |
| `dock_parts_print.png` | all eight dock parts laid out in their print poses | `dock.py` |
| `dock_sled_in_bay.png` | the sprung pack sled in its bay | `dock.py` |
| `dock_latch_engaged.png` / `dock_latch_released.png` | the latch in both states | `dock.py` |
| `dock_robot_docked.png` | the robot on the dock | `dock.py` |
| `mk1_work.png` / `mk2_work.png` | each variant at the WORK station, envelope captioned on the canvas | `marks.py work` |
| `mk1_work_condensed.png` / `mk2_work_condensed.png` | the same two variants in the condensed four-view layout | `marks.py work_condensed` |
| `mk1_drive_closeup.png` / `mk2_drive_closeup.png` | the drive modules that are the only difference between the variants | `marks.py` |

### The four `docs/media/` images the table above does not cover

Three of these are **not** redrawn by any code in this export. They are named
here rather than left to be discovered, because "every figure regenerates" would
otherwise be a claim this page contradicts. (`crawl_walk.gif`, below, is a fifth
image with no counterpart — but the run does write its source.)

| file | what it actually is | redrawn by this export? |
|---|---|---|
| `tall_test_matrix.png` | the print-test 2×2 argument diagram | **yes.** `cad/tonypi_tall/test_matrix.py` writes `edu/print_files_tall/renders/test_matrix.png`, byte-identical to this copy. It is pure matplotlib and reads no vendor CAD, so it is the one module in `cad/tonypi_tall/` that runs from this checkout alone. |
| `shortarm_spec_v1.png` (byte-identical to `cad/shortarm/shortarm_spec_v1.png`) | the six-panel v1 arm sizing sheet | **no.** A static figure, authored once by analysis code that is not part of this export; nothing in this repository draws it, and `cad/shortarm/` holds that one PNG and nothing else. It is a sizing sheet rather than a result — the README lists the arm under "Does not" partly for this reason. |
| `shortarm_press_and_mass.png` | panels (e) and (f) of that sheet | **no.** An exact crop of `shortarm_spec_v1.png` — 1188 × 515 px taken at offset (593, 615) — so it inherits the line above. |
| `hero_mk1_mk2.png` | the two variants side by side, at the top of the README | **no.** A hand-composited pair of `docs/evidence/mk1_work.png` and `mk2_work.png` (both written by `marks.py work`, both in the table above), with the titles, the envelope line and the "nothing here has been printed" caption added on the canvas. The two source renders regenerate; the composite is not written by any code here. |

`docs/media/crawl_walk.gif` is one crawl cycle of three at the WALK station, sped
up, cut from `cad/alpha_centauri/output/sim/crawl_walk.mp4`. The mp4 itself is
**not committed** — `crawl_sim.py` writes it on every run, 34.1 s at 25 fps for
the full three cycles.

`work_failure_strip.png` was regenerated during the pre-publication review, after
its title was shortened and its station labels moved into a legend (they had been
overprinting the traces, and the title was clipping at the canvas edge). Every
number printed on the regenerated figure — 15.0 and 2.2 mm, 0.0 s, 3.9 s, 16.9 % —
is identical to the committed `sim_results.json`; the traces are that re-run's.

---

## What this repository does NOT evidence

Stated plainly, because the absence is the honest result:

- **Nothing has been printed, assembled, or powered.** There is no photograph, no
  telemetry log, no hardware run, and no motor has turned.
- The crawl exists only in MuJoCo, under a static-stability planner, with a
  contact model and an assumed servo `kp` — one of which (`kp`) is swept and
  reported, and one of which (contact) is not.
- There is **no unit-test suite**. The gates are the tests.
- `edu/ALPHA-CENTAURI-PLAN.md` describes PASS criteria for hardware milestones
  (P0–P5). **None of them has been run.** They are a plan, and the document says
  so.
- `cad/alpha_centauri/sim/SIM-NOTES.md` is a chronological working notebook. Its
  earlier tables are deliberately left standing and are superseded; the file
  carries a banner saying which section agrees with `sim_results.json`.
- **One committed number does not reproduce**, and it is named rather than
  regenerated: `swept_interference_full_mm3: 1856.1` in
  `docs/evidence/stowage_summary.json` comes back 0.0 mm³ against the rebuilt
  chassis. See "The one geometry number that does NOT reproduce" above.
- Three of the README's images are **not redrawn by any code here** — the hero
  composite and the two arm-spec images. See the second table under Figures.
