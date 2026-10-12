# Alpha Centauri — Gated Execution Plan

**Status:** DRAFT, awaiting the author's sign-off. Written 2026-07-31.
**Target:** one filmed demo run. **Date:** 2026-08-22 (a self-set date — movable, see §7).

---

> **2026-09-07 SUPERSESSION — read `edu/REPLAN-2026-08-28.md` first** (mirrors the
> block in the replan). Two classes of facts below date from the previous laptop
> and are DEAD:
> **(1) Printer.** The H2C (and §0.5's correction to it) is gone; the only
> printer is a **Bambu A1 mini** — 180×180×180 mm, open frame, no heated
> chamber, 300 °C nozzle. **(2) Servos.** Every claim that a Waveshare ST3215
> is "owned" / "on the shelf" is STALE: the only servos on hand are **six
> DS3235SG**. The ST3215 + STS3250 bench pair would need to be **purchased**
> (the fleet buy is bench-gated on that ~$80 unblocking order). Inline
> `[STALE — see REPLAN-2026-08-28]` markers flag each such claim. The original
> text is kept readable below — this project annotates, it does not rewrite.
>
> **Note for the public copy.** References below to "the design log" point to the
> author's working design record, which is not part of this public copy. The
> decisions they cite (D4, D8, D11, §5.4 and so on) are summarised at the point
> of use.

## 0. Read this first — evidence quality

Every number below came out of a single derivation pass on 2026-07-31. **The adversarial
verification pass never ran.** So:

- The numbers are **single-derivation, sourced but unchecked**. Each carries its own confidence
  flag from the derivation that produced it. Nothing here has been through a second pair of eyes.
- Where two workstreams derived the same quantity independently and agreed, that is noted — those
  are the strongest claims in the document.
- **Where they disagreed, the disagreement is preserved, not resolved.** See §2.

Treat this as a plan built on the best available arithmetic, not on verified fact. The whole point
of the P0 gate is to replace the load-bearing estimates with measurements before anything expensive
is committed.

---

## 0.5 The printer is a Bambu Lab H2C, not a Guider 3 Plus

Corrected 2026-07-31. This invalidates several numbers below and improves almost all of them.

| | Guider 3 Plus (assumed) | **Bambu Lab H2C (actual)** |
|---|---|---|
| Build volume | 350 × 350 × **600** mm | 330 × 320 × **325** mm |
| Nozzle max | 240–260 °C class | **350 °C** |
| Chamber | Enclosed, passive | **65 °C actively heated** |
| Bed | 120 °C | 120 °C |
| Materials | PLA / PETG / ABS | **+ PC, PA-CF, PETG-CF, PPS, TPU** |
| Hotends | 1 | **6 swappable (Vortek) + AMS multi-material** |
| Throughput | 13.38 cm³/h (measured) | ~3–4× that — **needs re-slicing to confirm** |

**Four consequences, three of them large:**

1. **The PETG-softens-before-the-servo-trips failure (risk 1.1) is fixable by material.** PETG's loaded
   limit is ~65 °C against the servo's 70 °C trip. **PC** (Tg ~147 °C, HDT ~130 °C) and **PA-CF** hold
   form far above anything a servo case will reach. Print the 12 servo pockets and the knee brackets in
   PC or PA-CF and the compound failure — permanent mount deformation — goes away. The servo still
   overheats; the robot no longer deforms while it does. Cost is small because these are *small* parts:
   ~200–300 g of engineering filament, roughly $20–25, against PETG for everything else.
2. **The strength problem shrinks too.** Risk 11 found a 4 mm PETG knee web at 49.7 MPa against a 25 MPa
   XY allowable. PA-CF and PC are several times stronger, so those sections either pass as drawn or get
   *thinner and lighter* — which feeds straight back into the torque budget.
3. **TPU pads become integral, not glued.** The door analysis made TPU feet a hard requirement (13.6–19.0 N
   of traction bare vs 25 N needed; 38–48 N with TPU). With AMS the pad prints directly onto the foot as
   one part. No adhesion failure mode, no dovetail retention feature, no separate part. Same for chest
   bumpers and any gripper surface.
4. **Print time stops being the critical path.** The 155–311 h estimate was calibrated on the Guider
   profile. At a conservative 3× it is ~52–104 h — days, not weeks. **Re-slice the existing STLs in
   Bambu Studio and measure it** rather than trusting the 3× (P0 item).

**The one loss: Z drops from 600 mm to 325 mm.** Checked against every part currently designed — chest
box 85 mm, waist box ~65 mm, riser ≤173 mm, legs ≤138 mm, chassis low-profile — and **nothing needs more
than 325 mm.** The spine rods are 307 mm of *steel*, not printed. The 600 mm was never being used, so the
loss is theoretical. XY 350 → 330/320 is likewise clear: the widest part is the chassis at ~223 mm.

---

## 1. What changed — five findings that move standing decisions

### 1.1 The leg servo margin ~~does not close~~ — VERDICT WITHDRAWN, see §1.6

> **⚠️ SUPERSEDED 2026-07-31.** The "FAIL" conclusion below rests on a 22–27 kg·cm knee requirement
> that was later found to be **~2× overstated** — it used body stance height as the leg's in-plane
> extension. Corrected, the worst continuous joint load is 11.67 kg·cm (abduction, standing) against
> the STS3250's 16 kg·cm rated, a **1.37× pass**. §1.6 has the corrected arithmetic and the current
> verdict. What survives from this section is the *thermal reasoning* — servos fail by overheating,
> continuous rating is what matters, and PETG softens below the servo's trip point — all of which still
> shapes the design. The numbers do not.

The locked choice of FEETECH STS3250 was made on its **50 kg·cm peak stall** figure, giving an
apparent 1.85× margin over the 22–27 kg·cm knee requirement. Both a spec-sheet review and an
independent bench review say that is the wrong number to design against:

| Source | Figure | Margin at 27 kg·cm |
|---|---|---|
| Vendor headline (goodservo, Evelta, AIFITLAB) | 50 kg·cm peak stall @12 V | 1.85× |
| Vendor spec table, **rated/continuous** (Evelta + AIFITLAB, 2 independent) | **16 kg·cm @12 V** | **0.59× — FAIL** |
| robonine independent bench, sustained before 70 °C trip | **~25 kg·cm** | **0.93× — FAIL** |
| At 3S nominal 11.1 V rather than 12 V, peak | 44.4 kg·cm | 1.64× |

The two "honest" figures disagree with each other (16 vs 25), but **both fail the requirement**, and
neither is close to 1.85×. This is a *duty-cycle* problem, not a torque problem: the servo can hit
the pose, it cannot hold it. Derived hold times at a 200 mm stance:

- Trot, knee at 25.1 kg·cm → **70 °C cutout in ~7 minutes** continuous, ~14 min at 50% stance duty.
- Standing front-biased, 17.5 kg·cm → ~14 minutes.
- Near-straight leg (h ≥ 250 mm), 9.5 kg·cm → ~49 minutes, effectively safe.

The safe pose is the tall one, which is also the tippiest one. **A static reach pose has a stopwatch
on it**, and a Gemini look→reason→act round trip is 30–60 s of that budget.

Compounding it: PETG's loaded service limit is ~65 °C but the servo doesn't protect until 70 °C —
**the printed mount goes soft before the servo saves itself**, and that deformation is permanent.

**What this forces:** a per-servo thermal gate in software (the bus gives `Present Temperature` free),
2–3 mm standoff ribs so the servo case never touches a structural wall, and an LLM loop designed to
*extend → act → retract* rather than hold. It may also force a geared knee or gravity compensation.
**P0 resolves it for $0 on hardware already owned.**

### 1.2 Harvesting is dead for the legs ❌ RESOLVED — buy

You asked to harvest from TonyPi and MiniHexa. The MiniHexa audit completed and the answer is
unambiguous:

- MiniHexa's 18 servos are **HiWonder HPD-0127, 1.8 kg·cm** — and that figure is a *clutch trigger*,
  not a motor limit, so it does not scale with voltage. Running them at 12 V buys nothing and is 43%
  over their rated max. They are **~20× short** of the leg requirement. Not marginal — wrong category
  of machine (18 of them weigh 198 g and are sized to walk a 580 g robot).
- Their protocol is plain 3-wire hobby PWM behind an ESP32, with **zero** FEETECH STS/SCS
  compatibility and no feedback of any kind. A bus driver board cannot drive them at all.
- Stripping the MiniHexa would destroy a working, already-integrated robot (first live BLE motion
  2026-07-23, 5 test files) in exchange for parts that cannot be used.

The TonyPi audit was cut short, but the partial finding is that its LX-824HV class is
~17–20 kg·cm at HV and speaks HiWonder's own protocol, not FEETECH — so it is *also* short, and on the
wrong bus. **Leg servos must be bought.** Harvest is still fine for the arms (see §2.3).

### 1.3 The 105 cm door handle is not reachable as designed ⚠️ BLOCKING

Two workstreams derived this independently and agreed:

- **Height workstream:** extended shoulder at 656 mm; a 300 mm arm at 85% extension and 60° elevation
  reaches **877 mm**. Short of 1050 mm by **173 mm**.
- **Software workstream:** short by **84–154 mm** even at full spine extension with the crouch engaged.

Two roads to the missing height, and they trade differently than expected:

| Option | Mass | Cost |
|---|---|---|
| Printed riser, ~140–173 mm | +274 to +398 g | No travel penalty |
| Longer M8 spine rods, +140 mm | **+90 g** (4.5× lighter) | Full travel goes 200 s → **312 s** |

**But there is a third option that may delete the problem entirely.** The US residential lever standard
is **914 mm**, not 1050 mm. At 914 mm the riser requirement collapses to **37 mm** — and moving the arms
from the chest side-wall pockets to the chest *top face* supplies 25 mm of that for free. At the ADA
floor of 865 mm it is already reachable today with nothing added.

**Measuring your actual door is worth 136 mm of structure and possibly the entire riser.** It takes
five minutes with a tape measure and it is the highest-leverage measurement in this whole document.

Related: the tallest point of the condensed robot is **not** the chest at 431 mm — it is the two bare
M8 rods at **628 mm**, which are always at full length because only the chest moves. Any static riser
above ~72 mm ends under-table access at a 700 mm apron.

### 1.4 The twin open-loop spine is dead on paper ⚠️ BLOCKING

`chest_box.py` bores 8.5 mm through 49 mm of tower for an 8.0 mm rod. Maximum carriage tilt before
the bore binds on the rod is asin(0.5/49) = 0.585°; across the 120 mm rod spacing that is **1.225 mm
of differential advance between the two screws — 0.49% of a 250 mm stroke, or 0.98 of one M8
revolution.**

Two FS5103R continuous-rotation servos have no position feedback, no matched deadband, and different
loads. They will not hold 0.5%. `cad/telescopebot/README.md` already flagged sync drift as an open
risk; this is the first time the jam threshold has been quantified, and it is far tighter than the
mitigation discussion assumed.

**Fixes, in order of preference:**
1. **One servo driving both screws through a GT2 belt loop** — deletes the failure mode entirely and
   frees a servo. Cheapest, most reliable.
2. Replace the FS5103R pair with position-feedback bus servos in multi-turn mode (+$52 net). 1.225 mm
   is ±0.5 rev on an M8 — trivially held by a 4096-count encoder, and it also kills the open-loop
   height-drift problem and gives the spine real telemetry.
3. One screw + a separate linear rail.

Recommend **1 + 2 together**: belt-synced *and* closed-loop. The spine is the one subsystem described
as "already designed," and it is the one most likely to waste a print.

### 1.5 The short-arm saving is real but half what was assumed

I told you two short arms beat two full SO-ARM101s on mass and symmetry. That still holds, but the
number was optimistic. Three independent re-derivations: **249 g**, **399 g** (pair, before height
recovery), **520 g**. Not the 500–900 g I quoted. Reason: recovering the 14 cm of lost reach adds mass
back, and the nominal short arm comes out at 504 g against the 400–500 g target.

Separately, printed mass across the whole robot was over-estimated by 24% — actual slicing on your own
Guider 3 Plus profile gives **0.953 g per cm³ of solid model volume**, not 1.27. Chest drops 341 → 258 g,
waist 340 → 260 g. That is a genuine, free saving that partly offsets the above.

**Whole robot re-derives to 5.4–5.6 kg** on a Dingo base whose stock design payload is 0.5 kg. The
torso alone is 3.3× the rated payload. Every printed member inherits a ~1.54× stress increase over
stock, and net knee margin is ~18% *worse* than a stock Dingo even after the servo upgrade.

---

## 1.6 The build: stock Dingo legs, direct drive, stretched body

The author's priorities, restated 2026-07-31: **feasible · properly functional when built · relatively big and
impressive · cheap.** Decided 2026-07-31 after the reduction analysis: **no gearboxes.** Stock Dingo
legs, servos driven directly, body stretched, torso on top. If that needs different or more servos,
buy them.

### Why the gearbox path was closed

A limited-rotation servo geared R:1 gains torque by R and *loses travel* by R — the product is
invariant. An MG996R has ~180° of travel; the knee needs ~52° of joint swing to walk, capping R at
~3.5:1, at which point torque is still short by ~2.9×. **There is no ratio that works** — more gearing
buys force by removing the very travel the knee needs to take a step. The finding survived every
optimistic assumption tested (higher continuous rating, pushed travel, no dynamic factor, lighter
robot, shorter stride). Closed as a dead end, not deferred.

### Four geometry corrections that came out of that analysis and still stand

These were derived by re-implementing Dingo's own IK from `Config.py` / `Kinematics.py` and verifying
FK inverts it to 1e-12 m. They **supersede the torque figures used earlier in this document**, including
in §1.1.

1. **Knee torques quoted earlier were ~2× too high.** The error: 250 mm is the *body* stance height, but
   the hip-pitch joint sits 14.30 mm above the body datum, so in-plane hip-to-foot extension is
   264.35 mm. That gives α = 9.64°, not 21.19°, and an exact knee moment arm of **25.18 mm** rather
   than `L3·sin α` = 49.94 mm.
2. **Abduction is the most loaded joint when standing, not the least.** Per newton of vertical load the
   moment arms are **abduction 49.60 mm, knee 25.18 mm, hip pitch 5.35 mm** — abduction carries ~2× the
   knee and ~9× the hip. It is also the only joint with a 250 mm arm against lateral force, so any side
   load or slope dominates it. Earlier drafts of this plan ignored abduction entirely.
3. **Stance height must be ~235 mm, not 250 mm.** At 250 mm the leg is at **98.59% of full reach** with
   3.79 mm left, which makes a statically stable crawl kinematically impossible — the body cannot shift
   far enough to get the CoM inside the support triangle. The "never crouch, hold 250 mm" rule as
   written was broken. Corrected rule: **hold ~235 mm** — still near-straight and thermally cheap, but
   with the reach headroom a crawl needs.
4. **`Kinematics.py` fails silently on over-extension.** Line 86 clips `len_B` to `0.8*(L2+L3)` rather
   than raising, which on an unreachable command would slam the foot ~35–50 mm. This must be guarded in
   our code, not trusted.

**Corrected torque table** (5.5 kg robot, W = 53.94 N, h = 235 mm, CoM centred):

| Case | Abduction | Hip pitch | Knee |
|---|---|---|---|
| 4-foot standing (continuous) | **11.67** | 0.74 | 7.15 kg·cm |
| 3-foot crawl support | ~18 | ~4.3 | ~16 kg·cm |
| Worst transient (1.5× dynamic) | **27.40** | 6.50 | 24.25 kg·cm |

> **⚠️ FLAGGED 2026-08-01 (do not quote this section without reading this):**
> two defects in §1.6 as written, recorded rather than silently rewritten.
> **(1) Prose/table stance mismatch.** Correction #1's worked numbers
> (264.35 mm extension, α = 9.64°, 25.18 mm knee arm) are evaluated at the
> **250 mm** stance this same section rejects; the torque table header says
> **h = 235 mm**. The table is the governing artifact and it reproduces at 235
> only with an additional **μ = 0.15 lateral-scrub friction term that is not
> documented anywhere in this file**. At 235 mm the in-plane extension is
> 249.30 mm (`interface_constants.extension_at(235)`), not 264.35.
> **(2) The 3-foot crawl row (~18 / ~4.3 / ~16 kg·cm) is UNREPRODUCIBLE** —
> the "~" values do not fall out of the documented model. Treat that row as
> indicative only; the MJCF crawl simulation (cad/alpha_centauri/sim/) is the
> replacement evidence for crawl-phase torques.

### Recorded deviation from the donor: the knee is direct-drive

Dingo drives its lower leg through a **hip-mounted four-bar linkage** — both
leg servos sit at the hip and the calf is actuated remotely through the
linkage. Alpha Centauri instead mounts the knee servo **in the thigh, driving
the calf directly** (thigh.py + joint_parts.py: horn adapter in the calf lug,
608ZZ on the idle side). This was decided implicitly when the thigh was drawn
and is recorded here explicitly as a deviation, 2026-08-01. What it changes:

- **Distal mass.** The donor's gait tuning assumes near-zero servo mass below
  the hip; we carry ~74.5 g (NOMINAL) at the knee per leg. Swing dynamics
  differ from the donor's; the MJCF model takes mass placement off the solids,
  so the crawl simulation — not the donor's tuning — is the evidence that this
  is fine.
- **Transmission.** A four-bar's effective ratio varies over the swing; direct
  drive removes that nonlinearity. Knee torque figures in this plan already
  assume direct drive.
- **Cabling.** The knee servo's bus cable must cross the hip-pitch joint into
  a moving thigh — a routing item for the electronics phase.

### What this does to the servo choice — it vindicates the original one

§1.1 declared the STS3250 a failure on continuous torque (16 kg·cm rated against a "22–27 kg·cm"
requirement, 0.59×). **That requirement figure was the 2×-overstated one.** Against the corrected
numbers:

- **Continuous / standing:** worst joint is abduction at 11.67 kg·cm against 16 rated → **1.37×. Passes.**
- **Peak transient:** 27.40 kg·cm against 50 stall → **1.82×. Passes.**
- 3-foot crawl support at ~18 kg·cm slightly exceeds the continuous rating, but that is an intermittent
  per-leg condition during a step, not a held pose.

So direct-drive STS3250 closes, and §1.1's FAIL verdict is **withdrawn** — it was arithmetic downstream
of the moment-arm error, not a property of the servo.

### Two free changes worth more than any component swap

- **Centre the CoM fore-aft.** Move the telescoping torso back until the standing CoM sits at the
  wheelbase centre. This cuts the required lateral body shift from 44.4 to 25.5 mm, drops the 3-foot
  peak load from 3.04 to 2.57 kgf, and cuts knee demand ~27%. It costs nothing but placement.
- **Stretch the body and spread the hips.** Per-leg torque is unchanged by hip spacing; what changes is
  the support polygon. Going from Dingo's 274 mm foot pattern to ~500 mm is the tipping fix, and it is
  paid for in filament. `LEG_FB` and `delta_x` are runtime parameters in Dingo's config, so this is a
  number change rather than a rewrite.

### Two repo contradictions this analysis surfaced

- **`cad/telescopebot/leg_linkage.py` is NOT the Dingo leg.** It must not be treated as a starting point
  for the Dingo-geometry legs.
- **`hardware_constants.py` names the wrong printer** (Guider 3 Plus). See §0.5 — it is a Bambu H2C.

---

## 2. Decisions I need from you

The door and servo-purchase questions below are **parked** per your steer of 2026-07-31 — kept because
the plan depends on them eventually, not because they block now. The live question is 2.0.

### 2.0 How big is "relatively big"? ← the only thing blocking CAD right now

"Big and impressive" needs one number before the chassis and riser can be drawn, because they are the
two parts that supply it. The stack today, at k = 1.0 legs:

| | Condensed | Extended |
|---|---|---|
| Camera / eye line | 423 mm | 673 mm |
| Top of chest | 431 mm | 681 mm |
| + 173 mm riser | 604 mm | **854 mm** |
| Fingertip reach, 300 mm arm | — | **~1,050 mm** |

So the machine as planned is roughly **85 cm at the shoulder, 105 cm at the fingertip, on a body that
can be 320 mm long** — dog-sized-plus, and it grows a quarter-metre on camera when the spine extends,
which is the single most impressive thing it does. Going meaningfully taller than this is cheap
(spine + riser, no torque cost); going meaningfully *longer or wider* is also cheap (printed chassis)
and buys stability at the same time. Going taller in the **legs** is the only expensive direction.

Tell me the target — "as tall as the spine will go", a number, or "make the body as long as the H2C can
print" — and I will size the chassis and riser to it.

### 2.1 Is the demo door a PUSH door or a PULL door? *(parked)*

The entire crack-wedge-pry sub-problem exists only because pull was assumed. Your scope said "lever
handles, unsprung interior doors" — it never said pull. The difference is enormous:

| Route | First-attempt success (derived) |
|---|---|
| Pull door, leg-pry as specified | **~7%** |
| Pull door, low chassis hook instead of leg-pry | ~19% |
| **Push door, chest push** | **~55%** |
| Unlatched push-through | ~92% |

The pull route fails three independent ways: no servo in the plausible arm set can press a
code-maximum lever by shoulder torque (needs 8.63 N·m, best owned servo gives 5.88 N·m); the leg pry
binds at the **hip** servo at 10.2 N against a 25 N code ceiling; and bare PETG feet give 13.6–19.0 N
of traction against 25 N needed. A chest push against a push door is structurally sound with **2.0×
margin** and needs none of that machinery.

If a push door is acceptable for the demo, it deletes the two lowest-probability stages outright.

### 2.2 Approve the servo spend *(parked — and the number just dropped)*

Per §1.6 the recommended part changed from STS3250 to **STS3215-12V at a tall stance**: ~$312 for twelve
instead of $700–1,056. That is the largest single cost reduction available and it comes from a pose
change, not a compromise. The note below is retained for when this un-parks.

**Servo lead time is the true critical path and it may already exceed the calendar.** Every US
reseller checked was sold out or backordered. Alibaba plus customs is routinely 2–6 weeks. Nothing in
P2 or P3 can be validated without them.

- 12 leg servos: **$573** (Alibaba, 2–99 tier, no quoted lead time) to **$1,056** (US retail)
- Recommended split: buy **ONE** from the fastest US source (~$84 delivered, ~1 week) so the P0/P2
  torque and thermal gate can run a week early, and the other 11 from the cheapest source in parallel.
- Plus ~$60 for two shoulder servos (§2.3), a 3S pack rated ≥20 A continuous, 16–18 AWG distribution
  wire, an IR thermometer, and a clamp meter.

Tier totals: **MUST-BUY $1,723 · MUST+SHOULD $2,263 · full build $2,960 · cheapest credible
walking-and-reaching build $1,408.**

**Do not order the 11 until the P0 thermal bench runs** — a bad result there cancels the order and
saves $573–1,056. But order the *one* today; it is the gating item.

### 2.3 The shoulder servo does not exist in your inventory

A 30 cm arm holding 200 g needs 10.8–12.0 kg·cm at the shoulder. An MG996R is 10 kg·cm **stall** and
~3.5 kg·cm continuous — the requirement is 108–120% of stall and 310–343% of continuous. Even unloaded
it is 138% of continuous. So "built mostly from servos already owned" needs an explicit exception.

Options, cheapest first: (1) surgical-tubing gravity compensation across the shoulder —
`leg_linkage.py` already prints the 6 mm gravity posts with retention grooves; (2) two MG996R in
parallel, inventory allows it; (3) **buy 2× STS3215-12V (~$30 each)** — which is what SO-ARM101 itself
uses, and which puts the arms on the same bus and the same telemetry as the legs. Recommend (3), with
(1) as a free addition.

---

## 3. Critical path

```
git push (5 min)  ←── nothing else has value if this doesn't happen
   │
   ├─→ order ONE servo fast (10 min) ──→ [7 days] ──┐
   ├─→ order 11 servos cheap (10 min) ─→ [7–42 days] ─┐
   │                                                   │
   ├─→ CALIPER SESSION (2 h, $0) ──→ unblocks ALL CAD  │
   │      │                                            │
   │      └─→ leg CAD from Dingo STEP (2–3 d) ──→ print one leg (11 h) ──┤
   │                                                                      │
   └─→ THERMAL BENCH on owned ST3215 (90 min, $0) ──→ can CANCEL the order│  <!-- [STALE — see REPLAN-2026-08-28: no ST3215 owned; must be purchased] -->
                                                                          ▼
                                                            P2 leg GO/NO-GO
```

Three consequences:

1. **The `git push` is not housekeeping.** It is the only action that preserves any value at all if
   the servo branch runs long. 48 uncommitted paths, zero of them anywhere but this disk.
2. **The caliper session is now the longest pole, because printing stopped being one.** On the Guider
   the print BOM was 155–311 h — 30–59% of the calendar. On the H2C it is plausibly a third of that
   (§0.5), which takes the printer off the critical path entirely and puts **CAD readiness** on it
   instead. Every part still consumes at least one of the 54 `UNVERIFIED` constants, so nothing can be
   printed until the calipers come out. Two hours, zero dollars, day 0. Do it first.
3. **The thermal bench is no longer a proxy — it tests the exact recommended part.** §1.6's tall-stance
   argument names the STS3215, and you own one. Run it this week: it now decides a ~$312 purchase
   directly rather than standing in for a $700–1,056 one.

---

## 4. The gates

Each gate lists what PASS requires as *photographable evidence*, and what kills the phase.

### P0 — Measure + fit · 2 days · $0 (+1 servo ordered)

**Do:** git push. Caliper session over all 54 `UNVERIFIED` constants. Print the existing bore-fit
coupon (g-code already sliced, 1 h 39 m) and hand-thread the M8 rod through the 7.6–8.4 mm ladder.
Caliper every servo horn PCD. Measure your actual door: lever height, lever operating torque (fish
scale + tape measure, 3 doors), door breakaway force, and whether it pushes or pulls. Measure µ for
PETG and TPU coupons on your actual floor.

**PASS requires:**
1. Photo of the M8 rod threaded by hand into the chosen coupon bore, notch count legible in frame.
2. `hardware_constants.py` diff showing ≥40 of the 54 `UNVERIFIED` markers replaced with calipered
   values, each dated.
3. Caliper photo of the actual servo horn against a scale, measured PCD written into a new INTERFACE
   section.
4. Rendered PNG of the hip disc regenerated at the **measured** PCD, plus a passing `ligament_check.py`
   asserting every ligament ≥ 0.84 mm (two extrusions).
5. `git push` output showing `origin/feat/hiwonder-robots` at the new commit.
6. A number for your door's lever height and operating torque, written into the INTERFACE section.

**KILL if:** no coupon bore accepts the rod by hand (printer hole tolerance worse than ±0.4 mm —
recalibrate before any structural print) · the measured horn PCD leaves the hip-disc ligament below
0.84 mm at every feasible PCD (abandon the direct horn-bolt interface for a printed spline hub or
clamp collar).

> Known defect this gate must fix: `leg_linkage.py`'s hip disc currently has a **0.303 mm ligament** —
> 0.36 of one extrusion width. It will print as ragged slivers. Cause: an *assumed* 14.0 mm horn PCD.

### P1 — Torso bench rig · 3 days · ~$60

**Do:** Fix the spine sync (belt loop and/or bus servos, §1.4). Bench the twin screw off-robot with the
real torso mass. Wire a real voltage read.

**PASS requires:**
1. Video of the spine driving bottom-hard-stop to full extension and back, tape measure and wall clock
   in frame.
2. CSV of commanded vs measured height over 10 cycles, with maximum inter-nut differential measured by
   dial indicator. **PASS at ≤ 1.0 mm** (against the 1.225 mm jam threshold).
3. A robot-runtime transcript showing look → reason → `set_spine_height` → look, where the model chose
   the height from the image.
4. Photo of the carriage at full extension carrying the Jetson, the D435 and a 2 kg dummy, no visible rack.
5. IR reading of the spine servos after three full cycles.
6. Measured full-travel time within **15%** of the `SPINE_LEAD_MM_PER_REV` model — if it isn't, every
   duration the LLM plans is wrong.

**KILL if:** two FS5103R at identical command diverge by more than 1.225 mm equivalent over one
250 mm stroke — *expect this to fire*, and it means belt-sync or encoders are mandatory, not optional ·
the carriage descends >2 mm in 60 s unpowered on a T8 screw (T8 rejected, accept M8's 200–312 s) ·
no software-readable pack voltage exists anywhere in the chosen electronics.

### P2 — Quad chassis, one leg · 4 days · ~$700 (the 11 servos)

**Do:** Re-author the Dingo leg in build123d at k=1.0 against a **calipered STS3250 pocket** (not the
ST3215 pocket — 45.22×24.72×35 nominal vs the repo's measured 45.4×24.8×36.4 is close but not equal).
[STALE — see REPLAN-2026-08-28: the "repo's measured" ST3215 belonged to the previous laptop's era; none is on hand now.]
Print one leg. Load it. Heat it.

**PASS requires:**
1. Photo of one complete printed leg on a test stand with 2.75 kg hanging at the foot.
2. **Plot of knee servo case temperature vs time over 10 minutes at h = 200 mm. PASS at ≤ 65 °C.**
3. Same plot for the PETG mount surface. **PASS at ≤ 55 °C** (10 °C of headroom under PETG's limit).
4. Dial-indicator foot deflection under load. PASS at ≤ 2 mm.
5. 3-point-bend load-to-failure on a sacrificial thigh, with a photo of the fracture surface
   identifying interlayer vs in-plane failure. PASS at ≥ 2× the computed peak moment.
6. Measured STS3250 stall torque **at 11.1 V, not 12 V**, from a lever and a scale. PASS at ≥ 40 kg·cm.

**Item 2 is the gate that can kill the project**, and it has a zero-purchase proxy that should run in
P0 (see §5).

**KILL if:** the knee servo passes 70 °C or the PETG mount passes 65 °C within 5 minutes at h = 200 mm
(the k=1.0 + STS3250 + static-crouch-reach architecture cannot do the mission — needs a geared knee or
active cooling) · measured stall at 11.1 V is below 35 kg·cm · a printed thigh fails below 2× the peak
moment (PETG is the wrong material for the load path).

### P3 — Walking base · 4 days · $0

**Do:** Port Dingo's parametric gait generator (verified MIT — 847 lines, only 208 with real ROS
coupling, written for this exact leg). **Reconfigure trot → crawl, which is a config-only change** —
`Gaits.py` is 71 lines with zero imports and reads its contact table from config. A crawl also makes
host-death survivable: FEETECH goal positions latch forever with no bus watchdog, so a wedged host
mid-trot drops two feet and falls, while mid-crawl three feet are down and it just stands there.

Write the bus link with **SYNC WRITE / SYNC READ, never a per-servo loop** — 133 Hz vs 29 Hz at 24
servos. 1 Mbps is mandatory; at 115200 the 12-servo sync write alone is 80% of a 100 Hz tick.

**PASS requires:**
1. Uncut video of a 10 m walk carrying a 2.6 kg dummy at the real torso CG height, on hard floor **and**
   on low carpet.
2. Plotted time series from the servos' **own registers** (Present Temperature, Voltage, Load) for all
   12 legs across the walk. This is free telemetry and the only honest thermal evidence.
3. Logged pack-current trace.
4. Minimum pack voltage under trot transients.

**Numeric PASS:** 10 m in ≤ 90 s · max servo temp ≤ 65 °C · min pack voltage ≥ 10.2 V · zero brownouts ·
measured control rate ≥ 50 Hz.

**KILL if:** after two rounds of tuning it cannot walk 10 m carrying 2.6 kg without a servo hitting
70 °C · pack sags below 10.0 V on any transient, or static crouch current exceeds 12 A · **it cannot
walk on low carpet at all** — the mission names carpet, and a carpet failure at P3 is far cheaper to
admit than at P5.

### P4 — Integration · 3 days · $0

**PASS requires:**
1. Video of the robot standing, extending the spine, touching the lever at your measured door height,
   **holding for 60 s** (a realistic Gemini round trip).
2. Top-down photo with the support polygon marked and the CG **measured, not modelled** — one bathroom
   scale under each foot, solve for the centroid.
3. The same at the 75 cm tabletop.
4. Servo temperature log across the full 60 s hold.
5. A repeat with a deliberate lateral impulse sized to move the CG 20 mm.

**Numeric PASS:** measured static margin **≥ 20 mm** with both arms forward · the 60 s hold completes
with no servo above 65 °C · the impulse does not tip it.

**KILL if:** margin is below 20 mm — the derived 6 mm for both arms forward is inside the measurement
noise of a hand-built robot, and 20 mm is the minimum that survives a carpet edge. Fall back to
**one-arm reach as the only reach mode** (34 mm margin). · It cannot hold the pose for 60 s within
thermal budget — a reach that expires before the model answers cannot be driven by an LLM at all.

The four-scale CG measurement is the item that turns "we computed 6 mm of margin" into evidence.

### P5 — The demo · 3 days · $0

**PASS requires** a single **uncut** take from a fixed camera showing, in order: the prompt typed · the
`look()` frame · the model's reasoning text on screen · the walk to the door · the spine extending ·
the arm pressing the lever · the door opening. Alongside it: the full robot-runtime transcript and
the 12-servo telemetry log for the same wall-clock window, timestamps aligned to the video.

**Numeric PASS:** 3 of 5 attempts succeed end-to-end with no human touch · zero falls · no servo above
70 °C.

An edited video, or a video without the aligned telemetry log, does not close this gate.

**KILL the door task** if three consecutive attempts fail to rotate the lever, or the robot tips even
once. Fall back immediately to the **75 cm tabletop demo**, which is thermally and geometrically far
easier and still proves the entire look→reason→act chain. Do not iterate on the door under deadline:
the lever force cannot come from a shoulder servo, it must come from the spine or body weight, and if
that mechanism has not been proven by P4 it will not be invented in the last week.

---

## 5. The one experiment to run this week

**The crouch-hold thermal and brownout bench.** 90 minutes, on the ONE Waveshare ST3215 already on the
shelf, zero purchases, with a negative control.
[STALE — see REPLAN-2026-08-28: no ST3215 is on the shelf. Only six DS3235SG are on hand; this bench
now requires the 1× ST3215 + 1× STS3250 unblocking order first — it is no longer $0.]

Bolt the ST3215 to a rigid board. Print a 100 mm lever arm and a 4 mm PETG contact coupon in one
20-minute job. Hang **1.65 kg at 100 mm = 16.5 kg·cm = 55% of the ST3215's 30 kg·cm stall** — the same
fraction of peak that an STS3250 knee sees at a 200 mm trot (25.1/44.4 = 56%). Command position hold.
Log Present Temperature / Voltage / Load / Position at 1 Hz from the servo's own registers; log the
clamped PETG coupon's surface temperature with an IR thermometer.

Record: time to 65 °C on the PETG, 70 °C on the servo, the overload cutout, any position sag over 2°.
In the same rig, clamp-meter the current and caliper the conductor gauge of the stock 3-pin lead.

**Negative control:** repeat at 20% of stall (0.6 kg at 100 mm — the near-straight-leg standing case)
and confirm it reaches equilibrium below 50 °C. Without the control, a hot result can be blamed on the rig.

**Why this one:** it resolves the #2 risk (servo thermal duty) and the #6 risk (PETG mount HDT)
simultaneously, on the chosen servo family, at k=1.0 geometry, at the exact load fraction the design
will see. It resolves half of the #4 risk by producing a measured amps-per-kg·cm figure and the real
conductor gauge. It validates or refutes the thermal model that every duty-cycle policy, every P2–P4
gate criterion, and the whole door scenario rest on. Its output is a plot, which satisfies the house
visual-proof law. And **if it fails badly — cutout inside five minutes at 55% load — the whole
architecture is dead before $573–1,056 of servos is ordered.**

---

## 6. Power — three things that will otherwise burn something

1. **Do not daisy-chain servo power.** Three STS3250 on one factory 24 AWG 15 cm pigtail is 12.6 A →
   0.32 V drop and **4.0 W dissipated in the wire**. Twelve servos in a static 200 mm crouch draw
   ~10.6 A through a first link rated 3.5 A — a 3.0× overload before any transient, 4.8× on a
   four-servo simultaneous stall. Daisy-chain **signal only**; star-wire power from a distribution
   block, 16 AWG branches, 12 AWG trunk. Budget ≥20 A continuous, ≥40 A peak.
2. **3S full charge is 12.60 V and the STS3250 is rated 6–12 V** — 5% over. Either charge to 4.15 V/cell
   or bench-verify one servo on a full pack before trusting it. (The ST3215 is rated to 12.6 V and is fine.)
   [STALE — see REPLAN-2026-08-28: any "bench on hand" reading is wrong — no ST3215 is owned; the bench pair must be purchased.]
3. **The LM2596 already dimensioned in `hardware_constants.py` cannot power a Jetson Orin Nano.** It is a
   2–3 A part; the Orin Nano devkit pulls 5 A at 5 V in 25 W mode. The CAD is currently designing a boss
   for a brownout. Substitute a 5 V 8 A buck (~$14) or a Pololu D24V90F5, and delete or annotate that
   constants block.

---

## 7. About the date

2026-08-22 is 22 days out and it is **your** scheduling, not an external cutoff — you do the wipe and
you decide in the moment what is preserved. I am not planning scope cuts around it.

What I will say plainly: the servo lead time (7–42 days) and the print time (155–311 h) are both
comparable to the whole remaining calendar, and they are *serial* with each other for the leg. If the
servos take three weeks, the P2 leg GO/NO-GO lands on or after the 22nd. That is a schedule collision
worth knowing about now, and moving the date is a legitimate response to it — as is deciding that the
repo surviving in good shape matters more than a running machine existing on the 21st. Those two goals
imply different orderings, and that is your call, not mine.

Either way: **the git push costs five minutes and removes the only truly irreversible risk here.**

---

## 8. Still unverified — the honest list

Load-bearing things nobody has checked:

- **Every number in this document** — the adversarial verification pass never ran (§0).
- **The H2C's real throughput on these parts.** The "~3–4×" in §0.5 is an inference from nozzle class,
  not a measurement. Re-slice the existing STLs in Bambu Studio and read the number off. Five minutes,
  and it is the difference between printing being a non-issue and printing being a week.
- **The ST3215's rated (continuous) torque** — unpublished by both Waveshare and FEETECH. Inferred at
  ~9.6 kg·cm from the STS3250's 16/50 ratio. **The entire §1.6 cost saving rests on this**, and the
  free bench on the owned unit settles it. [STALE — see REPLAN-2026-08-28: no owned unit; the bench
  needs the purchased ST3215+STS3250 pair, so it is gated on that order, not free.]
- **Whether PC or PA-CF servo pockets actually solve the mount problem**, or just move the failure to
  the fastener bearing surface. PA-CF is also strongly hygroscopic — it needs drying discipline that
  PETG does not, on a robot whose parts may sit half-built for weeks.
- **The STS3250's real continuous torque.** 16 kg·cm (spec table) vs ~25 kg·cm (bench review) is a 56%
  disagreement. Now less load-bearing than it was, since §1.6 moves the recommendation off that part —
  but it still settles what the expensive option would have bought.
- **Whether 12 STS3250 can be delivered before the 22nd.** No supplier quoted a lead time anywhere.
- **Your door**: push or pull, lever height, lever torque, breakaway force. Five minutes, changes everything.
- **The actual Dingo link lengths**, read from its own `Config.py` in the cloned repo rather than quoted
  through `CENTAUR-RESEARCH.md`. Every torque number rests on L2 = 130 and L3 = 138.1 mm.
- **Whether the waist box survives the centaur pivot at all.** If the battery migrates into the quad
  body it may shrink to a mast-base plate — which would delete 16.5 h of printing *and* the unresolved
  chest/waist nesting contradiction (chest `BOX_DEPTH` 130 exceeds the waist's 114 mm interior, and the
  chest rod line sits at its rear, so the chest can never descend into the waist mouth as drawn).
- **Whether digital calipers are actually on hand.** Every P0 item assumes them and nothing confirms it.
- **The SO-ARM101 baseline** (704 g, 44 cm reach) — carried forward from the brief, never confirmed from
  a primary source. The whole short-arm saving is measured against it.
- **Contradiction to resolve by measurement:** the height workstream says a 75 cm tabletop is *not*
  top-down graspable (94 mm above the extended shoulder, 21.6° upward angle — you can slide an object to
  the edge, not grasp it); the software workstream calls the same tabletop "comfortably reachable with
  171 of 250 mm of spine travel." Both can be true — *reachable* is not *graspable* — but the tabletop
  demo is the P5 fallback, so which one it is matters.

Two D-series dead ends from the design log transfer directly and must be defended against:

- **D8 (inverted normals).** Two of eight HiWonder brackets came out of sewing as closed shells with
  *negative* volume, and OCCT accepted them silently — a 25% hit rate. Dingo ships 190 SolidWorks files
  plus a whole-robot STEP. Any importer must assert positive volume and render a proof PNG per solid.
- **D11 (hard-coded link lengths).** TonyPi's 116 action groups broke because a link length changed.
  k=1.0 defuses this, but it re-arms the moment the build123d legs hard-code a length that Dingo's
  `Config.py` also owns. One INTERFACE block, imported by both the CAD and the gait config, with a test
  asserting they agree.

---

## 9. Software shape (for when the hardware is real)

Briefly, since you said hardware first:

- **One adapter, not three.** A stop that halts the gait but leaves the spine screwing upward is not a
  stop, so gait, spine and arms become subsystem objects held by a single adapter with one
  stop-everything entry point — rather than three peers that each have to be stopped separately.
- **A real battery gate at last.** FEETECH STS servos report input voltage per servo (datasheet §7-10),
  so this robot escapes the dead end of a servo bus that reports no battery state at all. Read the
  **minimum** across the 12 leg servos, not the mean, and label it *servo-rail* voltage — it is
  measured after the wiring drop, which makes it better than a pack-terminal reading for brownout
  detection and useless as a fuel gauge. This is the ROSPug lesson: that robot brownout-rebooted while
  resting voltage still read 11.8 V.
- **The safety layer needs a per-servo thermal gate alongside its battery gate.** Heat, not volts, is
  the top-ranked physical risk on this robot, and the bus hands you `Present Temperature` free on the
  same register read.
- **Validate the tilt guard against the crouch it must permit.** The reach posture is ~13° aft pitch; a
  naive symmetric guard would abort the robot's own required stance. This is a rule learned the hard
  way on an earlier project: validate every guard against the reference motion it must permit.
- **Do not build a MuJoCo/PyBullet sim.** It would answer statics questions with guessed inertias. Build
  the kinematic visualiser and known-answer test tables instead.
