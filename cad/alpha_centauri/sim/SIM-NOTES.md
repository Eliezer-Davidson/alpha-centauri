# Alpha Centauri — simulation lane notes (2026-08-01 → 2026-09-23)

> **Read this first.** This file is a working notebook kept in chronological order,
> not a summary. Numbers move as the model changes, and the *earlier* tables
> below are deliberately left standing so the movement is visible.
>
> **The authority is `docs/evidence/sim_results.json`, and for the model itself
> `docs/evidence/provenance.json`.** The last section of this file ("2026-09-23
> addendum") agrees with the results file on every margin; every table above that
> disagrees with it is superseded, including the −0.1 mm WORK margin and the
> "hip_fr SATURATED" line in the 2026-08-01 table — both were true of an earlier
> mass model and are not true of the model this repository ships.
>
> **Two more figures in this file are superseded and are not corrected in place.**
> Every *model total mass* quoted below — 4.913 kg in the 2026-09-22 section, and
> 4.969 kg in the 2026-09-23 addendum's own heading — is earlier than the model
> that shipped: the exported model is **4.9734 kg** against a 4.505 kg ledger,
> +468.0 g. Likewise every *STEP-file count* below (15, then 17) is superseded:
> the shipped export snapshots **20**. Both shipped figures are in
> `docs/evidence/provenance.json` (`mass_reconciliation`, `step_files_count`),
> which is the file that produced them.

MuJoCo simulation of the crawl at both waist-rail stations — the single claim
the whole layout rests on (design log §5.4). Everything lives in
`cad/alpha_centauri/sim/`, artifacts in `output/sim/`.

## How to run

```
# stage 1 — CAD interpreter ONLY (reads STEPs, writes MJCF + provenance):
edu/.cadenv/bin/python cad/alpha_centauri/sim/mjcf_export.py

# stage 2 — sim interpreter ONLY (mujoco; reads XML + provenance):
MUJOCO_GL=glx .venv/bin/python cad/alpha_centauri/sim/crawl_sim.py
```

The two stages never share an interpreter (project law). The exporter
snapshots every constant it uses — and every STEP file it reads (count
computed at export, never hard-coded) — into
`output/sim/provenance.json`; `crawl_sim.py` treats that snapshot as
authority and *warns* if `interface_constants.py` has drifted since export (the
constants file is edited independently of this run). Constants were unchanged
during the run (drift check: clean).

## The support-margin metric — two corrections (2026-08-01 adversarial audit)

An adversarial verification of the previous run found the physics sound and
everything reproducible, but the SUPPORT-MARGIN METRIC defective in two ways.
Both are fixed; the headline numbers below are the corrected ones.

* **Polygon vertices are now the CONTACT points, not the IK foot sites.**
  The margin polygon is built from each stance foot's sphere-centre xy
  (`foot_<leg>` geom): a sphere on flat ground contacts straight below its
  centre, so the centre's horizontal position IS the contact xy. The earlier
  revision used the IK foot SITES (on the calf axis at L3); at ~21° calf tilt
  every site sits 5.36 mm horizontally off its contact, the same direction on
  all four legs — a flattering bias at WORK (front-lift margin reported
  4.2 mm; true value ≈ 0 — the audit's replay measured 0.0 on the audited
  model, the fresh export lands at −0.1) and a pessimistic one at WALK
  (13.8 reported, 15.2 true). `interface_constants.py`'s own foot-sphere
  docstring names exactly this trap ("the centre is not the foot position");
  the physics honoured it, the metric didn't — now it does.
* **Deficient-contact time is a first-class result.** When fewer than 3
  planner-stance feet actually touch, no support polygon exists; those
  samples are excluded from every min-margin figure. The previous revision
  hid that exclusion in a raw sample counter. It is now reported per run as
  seconds and % of the crawl (`deficient_contact_s` / `deficient_contact_pct`
  in results.json, in the run summary, and beside every min-margin number
  here and in the figures). It matters: **WORK/chest spends 3.5 s = 15.4% of
  its crawl rocking on 2 feet**; WALK/chest spends 0.0 s.

## Results (numbers are from `output/sim/results.json`)

| run | stand CoM x | stand peak τ | crawl | distance | min 3-ft margin | deficient contact | crawl peak τ |
|---|---:|---:|---|---:|---:|---:|---:|
| WALK, Jetson chest | −11.0 mm | 0.544 N·m | OK, 0 falls | 145/150 mm | **15.2 mm** | 0.0 s (0.0%) | 1.367 N·m (56%) |
| WORK, Jetson chest | +39.5 mm | 0.629 N·m | completes, ON the boundary | 91/100 mm | **−0.1 mm** | **3.5 s (15.4%)** | **2.452 N·m — SATURATED (hip_fr)** |
| WALK, Jetson aft | −22.7 mm | 0.570 N·m | OK | 144/150 mm | 9.0 mm | 0.1 s (0.3%) | 1.443 N·m |
| WORK, Jetson aft | +19.7 mm | 0.586 N·m | OK | 95/100 mm | 10.2 mm | 0.3 s (1.5%) | 1.443 N·m |

Torque limit everywhere: **2.4517 N·m = 25 kg·cm MEASURED** (from
`hand_load.SERVO_MEASURED_KGCM`; the 50 kg·cm datasheet peak is never used).

* **E1 stand:** both stations stand with the worst joint at 26% of the
  measured limit (knee_fr, WORK). Hip-pitch torques are near zero standing —
  the feet sit directly under the hip-pitch axes; abduction carries the L1
  lateral offset moment (~0.6 N·m), knees carry the bent-knee moment.
* **E2 crawl @ WALK:** works as designed. 145 mm covered of 150 scripted
  (3 cycles), zero falls, **15.2 mm** minimum three-foot margin, zero
  deficient-contact time, no joint above 56% of the measured limit. The
  binding lifts are the REAR feet (rl 15.2 / rr 19.3 mm vs fl 27.8 /
  fr 26.3 mm) because the settled CoM sits ~11 mm aft of the wheelbase
  midpoint — servo droop plus the model's ledger deltas. The battery rail
  (±90 mm of trim, `BATTERY_RAIL_TRAVEL`) exists to zero exactly this.
* **E3 crawl @ WORK — the honest surprise, sharpened by the metric fix.**
  The brief predicted a fall. What the sim shows is *boundary-riding, not a
  clean topple* — and measured at the true contacts the margin is exactly
  the boundary: **−0.1 mm** minimum during the front lifts (fr −0.1, fl 1.4).
  The CoM grazes the edge of the support triangle, and the robot spends
  **3.5 s = 15.4% of the crawl** with only 2 planner-stance feet touching
  (rocking; those samples define no polygon and are excluded from the min —
  reported, not hidden). It still staggers through at 91/100 mm, with
  **hip_fr pinned at the measured torque limit**. The previously-reported
  +4.2 mm margin was the site-vertex bias, not a real margin. Quantified
  recovery: holding WALK's working margin at WORK would need a 47.6 mm
  lateral shift → `extension_at(235, 47.6, 25)` = 264.9 mm = 98.8% of reach,
  **past the 97% guard** — i.e. the legs cannot buy back what the forward
  CoM spends. The mode logic (crawl only at WALK) is supported: WORK
  crawling sits ON the static boundary, drops to 2-foot support for a
  seventh of the run, AND saturates a servo.
* **E4 Jetson A/B (evidence only — the decision is the author's, design log §6):**
  moving the Jetson (300 g) from the chest to the rear chassis moves the
  standing CoM −11.7 mm and drops it 9.7 mm lower. At the CURRENT WALK
  station that *costs* crawl margin (15.2 → 9.0 mm) because the CoM is
  already aft of the midpoint — but the rail exists to re-trim (sliding the
  torso ~+13 mm re-centres; not tested here). At WORK it is a clean win:
  margin −0.1 → 10.2 mm, deficient-contact time collapses 3.5 → 0.3 s, and
  the servo saturation disappears. Net: aft helps exactly the station that
  is in trouble, and the WALK cost is a trim, not a wall.
* **E5 sensitivity:** WALK conclusions are gain-robust (15.2 → 16.8 mm at
  kp 280) — with one caveat to carry next to that number: the kp 280 WALK
  run **transiently saturates all four knees** (frac ~0.001–0.0014 of crawl
  samples) where the kp 60 run saturates nothing. At WORK the corrected
  metric changes the story: kp 60 gives −0.1 mm and kp 280 gives 0.0 mm
  (kp 280 spends 3.4 s = 14.8% of the run on <3 stance feet, same caveat as
  kp 60's 15.4%) — **boundary-zero at BOTH gains**. The previously-reported +4.2 → −4.2 mm
  gain swing was largely the site-vertex bias moving with calf angle, not a
  real gain sensitivity. The conclusion stands, stronger: WORK is ON the
  boundary, and no crawl should be scheduled there.

## What is donor-derived vs new

| piece | provenance |
|---|---|
| leg IK (`dingo_ik.py`) | **faithful port** of DingoQuadruped `Kinematics.py` (MIT). Three marked deviations: rospy removed; the silent 0.8-reach clip is now a hard `ReachError` at the 0.97 guard (interface_constants law); `np.matrix`→`ndarray`. |
| triangular swing height | donor `SwingController.swing_height` |
| body-shift-as-foot-motion idea, 100 Hz control rate | donor `StanceController` / `Config.dt` |
| joint `armature` 0.0194 kg·m² | donor `SimulationConfig` (G²·m·r²) — the DONOR's servo, not a measured ST3215 value |
| crawl sequencer (`crawl_gait.CrawlPlan`) | **new** — the donor only ships a trot (two feet airborne); a statically stable one-foot-at-a-time crawl with lateral shift 25.5 mm / stride half 25 mm (both from `interface_constants`) is purpose-written, incl. the priming half-cycle that keeps stride excursions inside the 97% reach guard |
| donor→MJCF angle map (`crawl_gait.LegMap`) | **new**, calibrated against `assembly.solve_leg`'s triangle and **verified closed-loop**: donor IK → map → MuJoCo FK reproduces commanded foot points to 1.7e-9 m over 40 random targets per leg (asserted at every run) |
| donor `forward_kinematics` | **NOT used** — its hard-coded (403π)/4500 disagrees with its own φ by 0.037°; MuJoCo FK of the exported model is the oracle instead |

## The mass model

Generated from the CAD, never hand-typed: printed parts measured off their own
STEPs at PETG 0.953 g/cm³ (balance.py's convention — including parts slated
for PC/PA-CF, a deliberate consistency-over-realism choice), posed exactly as
`assembly_centaur.py`/`marks.py` pose them (boxes rotated −90°, the §1.4 fix).
Cluster masses imported from `balance.py`/`hand_load.py`: torso 1538 g,
Jetson 300 g, battery 600 g NOMINAL, arms 500 g, servo 74.5 g each.

Model total **4.833 kg** vs the balance.py ledger's 4.357 kg — a delta of
**+476 g** (all three numbers computed into `provenance.json`, never
reconciled silently). The delta is **not** the "~498 g of rail parts" an
earlier revision of this file called it: the waist-rail parts the ledger
predates (ways+rack+carriage+pawl+lever) do sum 497.7 g off their STEPs, but
the sim torso **omits the spine_pawl solid** that balance.py's SPINE ledger
includes, and the torso-remainder logic **pins the torso cluster to
TORSO_FULL** regardless of the measured chest/waist solids — which is why the
delta lands ~21 g short of the rail sum.

The exporter's analytic CoM cross-check (WORK/chest: **+45.89 analytic vs
+45.77 in MuJoCo**) verifies **mass bookkeeping at qpos=0 (legs straight)** —
it is NOT the stance-pose CoM the crawl runs at, which measures **+40.5 posed
and +39.5 settled** under servo droop. crawl_sim measures the stance CoM
live, every step; the qpos=0 agreement only proves the two mass pipelines
agree.

L1 is modelled as the diagonal it is: hip-pitch hinge at (0, ±49.60, +14.30)
mm inside the abduction-rotating frame.

## What sim CANNOT see — be straight about this

* **Links are rigid.** Printed-part flex is invisible — the 9.5° single-column
  chest yaw that `marks.py` measured would never have shown up here.
* **No backlash, no detent feel.** The rail is exported as two fixed STATIONS
  (walk/work XMLs), not as a sliding joint with detents — MJCF could express
  the joint, but the detent/lever behaviour is exactly the part a rigid-body
  position actuator would misrepresent. Mode-switching mid-sim is not
  modelled.
* **Servo heat, current limits, voltage sag** — none modelled. The 2.4517 N·m
  clamp is the only servo reality in the loop. A joint pinned at the clamp
  (WORK: hip_fr) would be COOKING a real ST3215.
* **Assumed, not measured:** kp 60 (kv 2), armature (donor's), joint damping
  0.1, foot µ 1.0. Sensitivity to kp is measured (E5); the others are not.
* **Geometry gaps:** feet, hip modules, head and arms are undrawn — they
  enter as ledger point masses (arms 500 g) or not at all (feet, head),
  matching the ledger. Collision geoms are primitives (boxes/capsules/
  spheres), so limb-limb interference is NOT checked here — the CAD lane's
  swept asserts (calf.py) remain the authority on that.
* `SERVO_BODY_HEIGHT` is UNRESOLVED (35.0 vs vendor 37.8) — it only enters
  the sim as servo-box inertia dimensions, where 2.8 mm is negligible; the
  print-blocking consequences live in the CAD lane, unaffected by this sim.

## Artifacts (all in `cad/alpha_centauri/output/sim/`)

* `alpha_centauri_{walk,work}_{chest,aft}.xml` + `provenance.json`
* `crawl_walk_contactsheet.png` — one full cycle at WALK, 8 frames
* `work_failure_strip.png` — worst front-lift instant + margin traces of both
  stations, deficient-contact time in the title
* `com_support_walk.png` — CoM path over the support triangles + margin
  timeline, deficient-contact time in the title
* `torque_vs_limit.png` — stand (both stations) and crawl peaks vs the
  measured limit
* `brain_ab.png` (named `jetson_ab.png` when this section was written) — the
  A/B: CoM by variant + margin by station, with
  deficient-contact seconds on each bar
* `crawl_walk.mp4`, `crawl_work.mp4` — full runs
* `results.json` — every number above, incl. per-run `deficient_contact_s`
  and `deficient_contact_pct`

## RE-RUN 2026-09-22 — phone brain, two 3S packs, four-quarter chassis

REPLAN-2026-08-28 items 2 and 6 applied to the mass model and the E-series
re-run (export against git rev `993abdf`, drift check clean):

* **Brain**: the 300 g Jetson lump is a 215 g phone stack
  (`balance.PHONE_ETC`, box 150 × 75 × 20). `TORSO_FULL` is derived
  (1538 − 300 + 215 = **1453 g**). The E4 A/B keeps its meaning with the
  lighter lump; the figure is now `brain_ab.png` (was `jetson_ab.png`).
* **Battery**: two 300 g packs (`balance.PACK_G` × `N_PACKS`) seated where
  `chassis.pack_seated()` puts them — x −190, y ±31.5, z 16, 75 × 58 × 24
  each — never restated in the exporter. Same total and same x as the old
  600 g lump, so the aft moment is unchanged by construction.
* **Chassis**: `chassis_half.step` is now the transitional fuse of the inner
  and outer quarters (posts, end walls, contact pads, bay trays): **939 g**
  for four quarters vs ~768 g for the H2C-era halves. The 17 STEP files are
  snapshotted; model **4.913 kg** vs ledger 4.443 kg, delta +470 g (the same
  bookkeeping delta as before — spine_pawl omitted, torso pinned).

| run | stand CoM x | stand peak τ | crawl | min 3-ft margin | deficient | crawl peak τ |
|---|---:|---:|---|---:|---:|---:|
| WALK, brain chest | −11.6 mm | 0.555 N·m | OK, 145/150 mm | **15.0 mm** (was 15.2) | 0.0 s | 1.391 N·m (57%) |
| WORK, brain chest | +35.7 mm | 0.631 N·m | 92/100 mm | **2.0 mm** (was −0.1) | **3.8 s (16.6%)** | 2.065 N·m — **no saturation** (was hip_fr pinned) |
| WALK, brain aft | −19.8 mm | 0.573 N·m | OK, 145/150 | 10.6 mm (was 9.0) | 0.0 s | 1.422 N·m |
| WORK, brain aft | +21.7 mm | 0.601 N·m | 94/100 | 9.2 mm (was 10.2) | 0.4 s (1.9%) | 1.477 N·m |

E5 (kp 280): WALK 16.6 mm, WORK 2.2 mm with 1.2 s deficient — same shape as
before, knees transiently saturate at the high gain as before.

Reading: the 85 g the phone saves off the top of the torso moves every
station's CoM aft by ~2–4 mm, which is why WORK/chest crosses from −0.1 to
+2.0 mm and stops saturating. **The conclusion does not change**: WORK still
spends a sixth of its crawl on two feet, and 2.0 mm is not a working
margin. Crawl at WALK only. Brain-aft remains the only configuration where
WORK has a real margin (9.2 mm) — see design log §4 decision 6. Recovery at
WORK/chest now needs a 45.4 mm lateral shift (was 47.6), still past the
97% reach guard.

Not in this model: the pack sled / latch / dock (undrawn), the pod rework the
chassis bed gate is waiting on (does not change mass), the arms as drawn on
the 2026-08-12 deck (this run used the 2026-08-01 nominal arm boxes because
`marks.py`'s deck furniture is not yet in the exporter — the 2026-08-12 re-run
on the other branch is not merged here).

**2026-09-23 addendum — bolt-on pods (+56 g of flanges, chassis 995 g, model
4.969 kg):** WALK/chest 15.0 mm, WORK/chest 2.2 mm (16.9% deficient, no
saturation), WALK/aft 10.7, WORK/aft 9.4. Within 0.2 mm of the table above;
conclusions unchanged.
