# Designing a Lighter/Longer TonyPi Frame — Decision Document

## 1. THE ANSWER

**You do not scan anything, and you do not need a mechanical engineer.** HiWonder's own CAD is already on your disk: `LX-824HV.STEP` is a genuine AP203 B-rep solid of the servo-plus-bracket assembly, and all eight aluminium frame parts ship as IGES surfaces + 1:1 DXF drawings. Spend **one evening in FreeCAD** sewing those IGES files to solids and reading the M3 hole grid off the DXFs into a Python constants file. Then **re-author the frame in build123d** — Python, Apache-2.0, native Linux, real B-rep, STEP export — where `THIGH_LEN` and `SHANK_LEN` are module constants and `python frame.py` emits every part. Software cost: **$0**. Hardware cost: **$30 of calipers** to verify HiWonder's numbers against your actual robot.

The route is: *vendor CAD → measure once → parametric code → sweep the length variable → print.* Capture, scan, mesh-repair and reverse-engineering are all deleted from the chain.

---

## 2. THE FOUR ROUTES

### Route 1 — Vendor CAD → build123d parametric code ★ RECOMMENDED

| | |
|---|---|
| **Cost** | $0 software + ~$30 calipers + ~$70/kg PA6-CF |
| **Time to first printed part** | 3–5 evenings (1 FreeCAD session, 1 constants file, 1 coupon print) |
| **Time to fluency** | ~1 week of evenings in build123d |
| **Skill required** | Python. That is the whole prerequisite. |

Files downloaded from HiWonder and verified (vendor property — **not redistributed in this
public copy**; see [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) for where to obtain each):

- `LX-824HV.STEP` — 4.6 MB, ISO-10303-21 AP203, SolidWorks 2018, mm. 11 × `MANIFOLD_SOLID_BREP`, 1086 `ADVANCED_FACE`. Real solid, not a mesh. Internal name `224or824`, so LX-224 CAD found anywhere is valid too.
- `bracket/支架图/IGS/*.IGS` — the eight frame parts: `L架` (L bracket), `U梁` (U beam), `一字支架` (straight), `多功能支架` (multi-function), `斜U支架` (oblique U), `短U支架` (short U), `长U支架` (long U), `脚板` (foot plate).
- `bracket/支架图/DXF/*.DXF` — same eight, 1:1.
- `LFD-01.stp` (head servo, AP214), `LX-824HV.dwg`, `LX-824HV_manual.pdf`.

**The entire TonyPi frame is those eight parts repeated.** Redesigning the robot means redesigning that set — nothing more.

Hole vocabulary, measured directly from DXF `CIRCLE` entities: **3.0–3.1 mm = M3 clearance** (the universal fastener), **7.9–8.2 mm = servo horn boss**, **3.8–3.9 mm secondary**, **15.75 mm** foot-plate lightening holes.

**Where it breaks — three real places:**

1. **The IGES files are surfaces, not solids.** Zero type-186 entities; they are type-144 trimmed-surface collections. You must **sew** them in FreeCAD (Part → Shape builder → Sewing) before any boolean or thickening. Simple sheet-like parts usually close cleanly; budget an evening for gap-chasing. Note: **Plasticity Indie ($175) cannot open IGES at all** — that is Studio-tier ($299) only.
2. **The DXFs are A3 multi-view drawing sheets, not part outlines.** Raw bbox parses to ~426 × 304 mm because it's the sheet. Hole *diameters* are reliable; hole *pitches* are contaminated by cross-view pairs and must be read by a human in FreeCAD's TechDraw or LibreCAD. Recurring **9.19 mm and 13.0 mm** spacings appear in every file and are probably the real grid — **UNVERIFIED** until you open them. One hour, once.
3. **Fillet selectors under parameter sweeps.** In build123d you don't fillet "that edge", you fillet a query result. Change `THIGH_LEN` and the query can match a different edge set, or OCCT throws on a compound edge and kills the build. Assert on face/edge counts after each fillet; keep radii well under local wall thickness. Expect more time here than on the frame geometry itself.

**Licence caveat, and it is not small.** `github.com/Hiwonder/TonyPi` has **no LICENSE file** (`/license` API → 404). The Drive materials carry no terms of any kind. Default is **all rights reserved**. Fine for a personal build; **get written permission before selling anything derived from HiWonder's bracket geometry.**

---

### Route 2 — Vendor CAD → FreeCAD GUI, no Python

| | |
|---|---|
| **Cost** | $0 (FreeCAD 1.1.3, LGPL-2.1, AppImage) |
| **Time to first printed part** | Similar, 3–5 evenings |
| **Time to fluency** | 15–30 hours, front-loaded and painful |
| **Skill required** | Sketch constraints, datum strategy, Body/Part containers |

FreeCAD is the keystone tool either way — it is the only free thing that imports STEP *and* IGES *and* DXF, sews surfaces, and exports STEP. The question is whether you also *design* in it.

**Where it breaks:** the topological naming problem is **mitigated, not eliminated**. FreeCAD's own wiki still carries a live `Topological_naming_problem` page and issue #17041 is a post-1.0 regression report. A deep Part Design tree on a bracket you re-parameterise thirty times will break, and you will repair it. Model defensively: sketch on datum planes not model faces, keep trees shallow, split into many small bodies.

**Why not this route for you:** "make every femur 15 mm longer and regenerate all 20 parts" is a for-loop in build123d and a manual re-drive of a fragile feature tree in the GUI. Section 5 of this document *requires* you to sweep limb length against torque. Parametric-by-code is not a preference here; it is the correct architecture. **Use FreeCAD as the import/sew/FEM tool, author in build123d.**

---

### Route 3 — Clean-room calipers, no vendor files

| | |
|---|---|
| **Cost** | ~$30 calipers + ~$15 pin gauges |
| **Time to first printed part** | +1 day vs Route 1 |
| **Skill required** | Reading a caliper; knowing that a designer meant 20.00 when you measure 19.87 |

The route if the licence question comes back badly, or for parts the vendor set doesn't cover. Six to ten numbers per interface: servo body 40.00 × 20.14 × 51.10 mm, mounting hole pitch X and Y, horn spline diameter and screw circle, plate thickness, shaft-to-mounting-face offset. Write them into `servo_lx824hv.py` and every part imports the same module.

This is not a downgrade. **For sheet-metal brackets whose entire function is a hole pattern, calipers beat every scanner on cost, time, Linux compatibility, and accuracy** — because manufactured parts are designed on round numbers and a scan destroys exactly that information.

---

### Route 4 — Scan, reverse-engineer, re-model ✗ DO NOT DO THIS

Costed so you can rule it out deliberately rather than rediscover it after a wasted month.

| | |
|---|---|
| **Cost** | $829 Revopoint MINI 2 + $39 AESUB Blue + a Windows machine you don't own |
| **Real cost if you want automation** | Geomagic Design X, ~$1,900/yr entry, **Windows-only** |
| **Time to first printed part** | Weeks |

Six independent reasons, any one nearly fatal:

1. **Worst-case optics.** Anodized aluminium, 30–60 mm, thin, shiny, featureless. Photogrammetry needs texture to match; there is none. Structured light reflects instead of scattering. Fixable only with matting spray and cross-polarization, and bare metal depolarizes.
2. **No absolute scale.** Meshroom/COLMAP/KIRI output is dimensionless. A 0.5–1% residual on a 45 mm part is 0.22–0.45 mm — already over budget.
3. **Optical scanning is worst at holes,** and holes are the entire functional content of a bracket. Standard practice is to re-measure bores by contact anyway.
4. **Tolerance math.** M2.5 four-bolt patterns want ±0.15 mm. Phone LiDAR: ±1 cm, two orders out. Photogrammetry on a sprayed small part: 0.1–0.3 mm plus scale error. Only blue-light structured light clears the bar.
5. **Linux is a hard gate on exactly that qualifying class.** Revo Scan: iOS/macOS/Android/Windows, **no Linux**. Creality Scan: no Linux. EXStar: Windows. RealityCapture: Windows, officially. The one WINE datapoint is a thread about USB failing — this is live isochronous USB from proprietary firmware, not a port-it-yourself problem.
6. **You want lighter and longer. A scan reproduces the part you are throwing away.** The scan contributes ~5% of the information and 95% of the effort.

And the chain-killer sits downstream regardless: **there is no free Linux tool that turns a scan mesh into an editable parametric solid.** FreeCAD's Reverse Engineering workbench is a documented stub. Fusion's Convert Mesh errors out above 50,000 facets and a real scan is 200k–2,000k. Design X does it and costs five figures on the wrong OS.

---

### Route 5 — AI-generate ✗ DOES NOT WORK HERE (but here is what it IS for)

**Mesh generators — Meshy, Tripo, Rodin, Hunyuan3D, TRELLIS, Spectral — cannot produce a printable structural servo bracket. Full stop.** They emit decorative meshes: no hole tolerances, no flatness, no datums, no feature tree, frequently non-manifold. Fine for a head shell. Never for a load path.

**Zoo (zoo.dev)** is the only one in a different class — genuine B-rep via KCL, and Design Studio does ship for Linux. Reject it anyway: the geometry kernel is closed-source and runs on Zoo's servers, the Linux app is a thin client streaming *video* back for the 3D view (no internet, no CAD), and Zoo's FAQ states it may train on free-plan data with no opt-out. This may become a product. Do not put the product's geometry on someone else's kernel behind an AI credit meter.

The architectural reason none of it works: **your part is defined by constraints from an existing assembly** — hole positions, servo envelope, mating brackets, joint axes — and **no current text-to-CAD system accepts that assembly as input.** Every vendor's showcase example is a standalone simple part. That is itself the finding.

**Where AI genuinely helps you, today: writing the build123d Python.** "Write a parameterised `ServoBracket` class taking these eight dimensions" is a task LLMs are very good at, and the output is code you can read, test, version and fix. A real 3–5× speedup, playing directly to your strengths. **Use AI as a code generator, not a geometry generator.** (Note this also makes AdamCAD redundant — it wraps an LLM writing CadQuery, which you can do free in your own editor with better control.)

---

## 3. THE RECOMMENDED ROUTE

**Route 1: FreeCAD 1.1.3 for import/sew/FEM, build123d v0.11.1 for authoring, OrcaSlicer for output. $0, native Linux, Apache-2.0 + LGPL, zero commercial restrictions.**

Why this one, for you specifically:

- **The author is a programmer, not an ME.** build123d is the single tool in this whole survey where that is an *advantage*. A servo bracket parameterised by servo dimensions is ~60 lines of Python. Git works. Tests work. Diffs work.
- **You asked for limb length as a variable.** That is not a stretch goal for code-CAD — it is the entire point of it. One dataclass (`femur_len`, `tibia_len`, `wall_t`, `servo=LX824HV`) drives all 20 parts, and you can sweep in a for-loop and print a comparison set. Nothing else here gives you that for free.
- **Section 5 forces the sweep.** You cannot pick a limb length by taste; you have to trade it against torque and deflection numerically. That makes parametric-by-code load-bearing, not stylistic.
- **STEP export matters twice:** no machine shop will quote an aluminium version from an STL, and STEP is the input to the FEA that this project cannot skip.
- **Add `ocp_vscode`** (Apache-2.0 VS Code extension). Code-CAD without a live viewer is miserable and nobody says so up front — you need to *see* which edge your selector grabbed. Pin your Python env before installing; its Quickstart button installs into whichever interpreter VS Code has selected.
- **Keep OpenSCAD installed** for 20-minute "does this clearance even work" throwaways. Do not build the frame in it: no STEP export, no fillet operation, and the newest *stable* tag is 2021.01 — everyone doing real work runs a nightly.

**Explicitly rejected:** Onshape free (non-commercial *and* every document is public and third-party-sublicensable — $1,500/yr is the only exit). Fusion (no Linux client; the cryinkfly WINE installer was **archived 2026-02-21** with open silent-failure bugs — a trap). Plasticity (direct modeller, no history: "make it 30% longer" is its single weakest operation, and Indie can't even open your IGES). **Fornjot (archived 2026-06-19) and CADmium (archived, no licence) are dead** and still rank well in "open source CAD 2026" listicles — ignore them.

---

## 4. THE UNWELCOME ENGINEERING TRUTHS

Corrected part number first: **TonyPi runs LX-824HV, not LX-15D.** 17 kg·cm @ 11.1 V, 57 g, 40.00 × 20.14 × 51.10 mm, 9–12.6 V. Different mass, different envelope, different voltage domain. Every number below uses the real part.

**(a) Torque scales linearly with length, and the margin is already gone.** τ = Σ m·g·d, so τ ∝ k. At k = 1.30 you pay **+30% static torque**. But the stall figure is not the usable figure: stall current is 1.7–2 A at 11.1 V = **19–22 W dissipated in a 57 g body**, so continuous safe holding is ~25–35% of stall ≈ **5.1 kg·cm**. A knee in single support at 30° flexion is already **7.20 kg·cm = 141% of continuous budget** on the stock robot; at +30% length it is **9.36 kg·cm = 184%**. TonyPi survives this today only because keyframe gaits pass through loaded poses quickly. **You are not spending torque margin — you are spending thermal duty cycle, and it is already negative in the worst pose.** The LX-824HV has documented overheat and stall protection: the failure mode is not graceful sag, it is *cutout*, mid-stride.

**(b) The dynamic penalty is worse, and it is the one free fix in this document.** Limb inertia J ≈ mL²/3, so at k = 1.3, **J → 1.69×**. Keep the stock keyframe timings and α is unchanged, so **τ_dyn scales as k² = +69%**. **Rescale every `.d6a` keyframe duration by k = 1.30** and α drops by 1/k², returning dynamic torque to stock — and because the step is also 30% longer, ground speed is roughly unchanged. This is nearly free and it is not optional.

**(c) "Lighter by printing" is largely a myth at this scale.** 16 servos × 57 g = 912 g of an 1800 g robot. **52% of your robot is servos you are not printing.** Total addressable structure is ~500 g. And at equal stiffness, PLA is **24% HEAVIER** than the aluminium it replaces (E/ρ: Al 25.5 vs PLA 2.8; at equal I you need 2.70× the thickness). At equal strength, PLA is 14% heavier. Only PA6-CF gets you a real 29% at equal strength. Realistic total saving from a genuine redesign — closed sections, part consolidation, deleting catalogue over-design — is **100–150 g = 6–8% of robot mass**. To hold torque constant at k = 1.30 you would need to remove **415 g: 83% of all structure, replaced by nothing.** Best case cancels about one third of the penalty. **Length dominates decisively and it is not close.**

**(d) Stiffness is the constraint that actually kills the naive version.** δ = FL³/3EI. Two penalties compound multiplicatively: material E_Al/E_PLA = **19.7×**, length 1.30³ = **2.20×**. **Same cross-section, PLA, 30% longer → 43× more deflection.** Referred into the angular error stack, frame flex goes from ~0.2° to **~8.6°**, which at z_c = 0.26 m is Δx = **39 mm against a ~22 mm lateral half-margin. It cannot stand.** Worse: the total budget is θ_tip × 0.3 = **1.46°**, and servo accuracy + gear backlash + horn slop alone consume ~**1.6°**. *The compliance budget at stock foot size is already negative.* **Scale the feet by the same k** — a flat printed plate, costs grams — and the budget rises to 1.90°, leaving the frame ~0.3°. That is the highest value-per-gram change in the entire project. Recovering 43× stiffness needs I up 43×, i.e. section depth up 3.5×: **impossible as a slab, achievable as a closed box section.** Where there is no envelope room — the servo-to-servo joint gaps, which is most of a small humanoid — **you cannot recover it, and that joint should stay aluminium.** Also: **do not use PLA for structure.** It creeps under sustained load, and a standing robot applies sustained load; your `.d6a` deviation table will drift out of calibration over hours.

**(e) The gait re-recording cost is the item most likely to sink this, and it is currently unbudgeted.** `.d6a` files in `/home/pi/TonyPi/ActionGroups` store **absolute joint angles** (0–1000 counts ↔ 0–240°). Joint space is meaningful only against a fixed kinematic chain. Grow thigh and shank by 24 mm each and **every stored pose becomes wrong simultaneously** — a 15°/30° pose now puts the foot 30–40 mm lower and differently fore-aft. And **nothing absorbs it for you**: stock walking is open-loop keyframe playback; the IMU serves posture and fall detection, not closed-loop balance. Static poses are cheap. Walking and turning are expensive — they encode a balance trajectory HiWonder tuned empirically for the stock mass distribution *and* stock link lengths, and you change both. Dynamic actions (kick, push-up, get-up) are most expensive and **you will lose several outright.** Hand-re-recording everything: **2–4 weeks, worse result.** Writing a retargeter (forward-kinematics the stock chain → recover Cartesian foot/CoM trajectories → IK onto the new chain → rescale timings by k → write back): **2–5 days**, plus 1–3 days per-gait tuning. This is the same shape of problem as retargeting captured motion onto a humanoid with different link lengths. **What retargeting does not fix:** printed limbs distribute mass differently than aluminium ones, so the ZMP trajectory is not preserved. Retargeting gets you ~80%; tuning finishes it.

**(f) One thing genuinely in your favour.** Time-to-fall T_c = √(z_c/g) rises from 0.143 s to 0.163 s (**+14%**) at k = 1.3. A taller robot falls more slowly, giving an open-loop keyframe walker more time to plant the swing foot. Static tipping margin, contrary to intuition, is **unchanged** by height — the tipping condition contains no height term. What is *not* in your favour is (d): angular error is amplified linearly by z_c, and that dominates.

---

## 5. FIRST THREE STEPS THIS WEEK

**1. Run `file ~/TonyPi/ActionGroups/*.d6a` and `sqlite3 <f> .schema`. Ten seconds, today.** HiWonder/LewanSoul `.d6a` files are widely reported to be SQLite3 databases with an action table of (index, time, servo1…servoN) — **UNVERIFIED against official docs**, and trivially checkable. This one command decides whether your gait plan is a weekend or a month. Do it before you buy filament.

**2. Email `support@hiwonder.com`.** Ask for the whole-robot TonyPi STP — their own product-page FAQ says *"We only provide STP file"*, but all 1,052 entries across their three official Drive folders were crawled and there is no robot-level STEP posted, so it means *on request*. In the same email, ask explicitly whether you may modify and 3D-print derived parts, and whether you may sell them. One email; it can delete the remaining geometry work and it is the only path to a clean commercial answer.

**3. One FreeCAD session, then print one coupon.** Install FreeCAD 1.1.3 AppImage (`freecad.org/downloads.php`). Import `LX-824HV.STEP` as your fixed obstacle. Sew the eight IGES brackets to solids. Open the eight DXFs and hand-record the M3 pitch grid into `servo_lx824hv.py` — that file is now the interface contract every part imports. Then **print a 3 mm plate carrying nothing but the servo hole pattern and bolt a real LX-824HV to it.** If it drops in, every downstream part inherits a verified interface. If it doesn't, you burned 10 g of filament instead of a redesign. **That coupon is worth more than any scan.**

---

### Two questions that could halve the project, and cost nothing to ask

- **Does "longer" mean longer *legs*, or a bigger *robot*?** If torso and neck will do, you get most of the reach and proportion goal with **zero leg-torque penalty, zero leg IK change, and every walking gait untouched** — you even keep the +14% T_c benefit. Only arm and head action groups need attention. Highest-leverage question in the whole project.
- **Print the frame at STOCK link lengths first.** One variable changed (material + section geometry), stock `.d6a` files untouched, stock kinematics. If the stock gaits still walk, your frame is stiff enough and you know it in a week. If they don't, you learned it before a month of retargeting. This is *one component change at a time, A/B'd against a golden baseline*, and it applies here verbatim.

---

**Sources:** [hiwonder.com/products/tonypi](https://www.hiwonder.com/products/tonypi) · [lx-824hv](https://www.hiwonder.com/products/lx-824hv) · [lfd-01m](https://www.hiwonder.com/products/lfd-01m) · [TonyPi Pro action-control docs](https://docs.hiwonder.com/projects/TonyPi_Pro/en/latest/docs/4_pc_software_action_control_courses.html) · [TonyPi Drive](https://drive.google.com/drive/folders/1EJppBKT0G0KF8uXjyMVlsAD1MwwAzq_2) · [github.com/Hiwonder/TonyPi](https://github.com/Hiwonder/TonyPi) (no LICENSE) · [github.com/Hiwonder/ainex](https://github.com/Hiwonder/ainex) (sibling URDF, 25 STLs — reference only, different servo family) · [freecad.org/downloads.php](https://www.freecad.org/downloads.php) · [github.com/gumyr/build123d](https://github.com/gumyr/build123d) · [github.com/bernhard-42/vscode-ocp-cad-viewer](https://github.com/bernhard-42/vscode-ocp-cad-viewer) · [onshape.com/en/pricing](https://www.onshape.com/en/pricing) · [plasticity.xyz/buy](https://www.plasticity.xyz/buy) · [zoo.dev/pricing](https://zoo.dev/pricing)

**UNVERIFIED and flagged:** `.d6a` = SQLite3 · bracket hole *pitches* (diameters verified from DXF entities; pitches need a human in CAD) · licence terms on every HiWonder CAD file — default all-rights-reserved · whether HiWonder actually supplies the robot-level STP on request · TonyPi link segment lengths (L_thigh 80 mm assumed throughout; **measure yours and re-run — the formulas hold, the constants won't**) · LX-824HV gear backlash ~1.0° (class-typical, not a published spec, and the largest single term in your error budget — measure it) · whether any 3D-printed HiWonder-pattern structural bracket has ever survived real use: **no such report exists anywhere. You would be first.**