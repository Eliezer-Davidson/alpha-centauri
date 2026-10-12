# Alpha Centauri — CAD tooling + donor-design research (2026-07-31)

The TelescopeBot pivots to a **centaur**: quadruped base + the already-designed
telescoping twin-screw torso. Robot name: **Alpha Centauri** (the author, 2026-07-31 —
see `CENTAUR-NAMES.md`). This document is the verified research behind the
build stack.

**Provenance.** Four research angles (31 tools/projects evaluated) plus one
stratified verification pass. Every license claim below was
verified from the GitHub registry API (`spdx_id` + the LICENSE blob itself)
or raw first-party page bytes — never README prose or summarizers. 22
verification checks: **21 CONFIRMED, 1 UNVERIFIABLE, 0 CONTRADICTED**. The raw
evidence pool behind those checks is not part of this public copy.

## The recommendation stack (all license-clean, all verified)

| Layer | Choice | License | Why |
|---|---|---|---|
| CAD authoring | **build123d 0.11.1** (unchanged) + AI writing the code | Apache-2.0 | Real local B-rep, STEP out, $0; already load-bearing in `cad/telescopebot/` |
| CAD viewer | **ocp-vscode v4.0.1** — INSTALLED 2026-07-31 into `cad/.venv` (now `edu/.cadenv`) | Apache-2.0 | Live build123d rendering in VSCode; was recommended in CAD-DECISION and never installed |
| Fasteners/threads | **bd_warehouse v0.3.0** — INSTALLED 2026-07-31 | Apache-2.0 | Parametric ISO threads/fasteners; directly useful for M8 spine + assembly interfaces |
| Import/sew/FEM | **FreeCAD 1.1.3** (unchanged) | LGPL-2.1 | Consumes the donor SolidWorks/STEP/FCStd sources below |
| Quadruped base donor | **Dingo Quadruped** | **MIT on BOTH code and CAD repos** | Real design source: 190 SolidWorks files + whole-robot STEP; designed to carry payload; biggest hobby-servo base surveyed |
| Arms donor | **SO-ARM101** (TheRobotStudio/SO-ARM100) | Apache-2.0 (single surface) | 36 per-part STEPs incl. `Base_SO101.step`; 6x FEETECH STS3215 per arm = the TTL bus family already on hand; guide PDF already in `edu/` |
| Gait controller | **CHAMP** (or Dingo's own MIT stack) | BSD-3-Clause | ROS quadruped controller, proven on SpotMicro-class bodies |

## Angle 1 — AI CAD generation: the standing decision SURVIVES

CAD-DECISION.md's rule — *AI as a code generator writing build123d, never a
geometry generator* — was re-tested against the 2026 field and comes out
strengthened:

- **Zoo (KittyCAD)** — the only genuine AI-to-B-rep product (KCL → STEP;
  Zookeeper conversational agent launched 2026-02-05). Still rejected on the
  same three re-verified grounds: closed **cloud-only kernel** (no internet =
  no CAD), metered agent ($0.0083/s past 20 free min/mo), and ToS training
  grant whose opt-out is **tier-gated** ("only if your subscription tier
  allows"; free plan explicitly trains on your data). Outputs are user-owned.
  Notably, Zookeeper's architecture (agent edits parametric code over B-rep)
  is exactly what we run locally for $0.
- **AdamCAD** — pivoted away from text-to-CAD entirely (now an "AI teammate"
  that drives Onshape/Fusion); its generator was open-sourced as **CADAM**
  (GPL-3.0), which is vendored **OpenSCAD-WASM** — CSG mesh, no B-rep, no
  STEP. Vindicates the original "redundant wrapper" call.
- **Backflip AI** — the one real mesh→B-rep tool (scan → STEP / Onshape
  feature tree). Waitlist beta, ToS unreadable (Notion JS wall — the single
  UNVERIFIABLE). Irrelevant here anyway: this project deleted the scanning
  step (vendor CAD on disk + calipers).
- **Meshy/Tripo-class image-to-3D** — confirmed mesh-only from the API format
  enums (no STEP). CSM was acquired by Google and shut (2026-01-24). Fine for
  aesthetic shells someday, not for engineering frames.

## Angle 2 — CAD editors: Route 1 reconfirmed from raw vendor bytes

- **Onshape Free**: "For non-commercial use only. All Onshape Documents are
  accessible to the public." Exit is $1,500/yr. Eliminated.
- **Fusion 360 Personal**: non-commercial cap, **no Linux client** (WINE
  installer archived 2026-02-21). Eliminated.
- **Plasticity**: $175/$299 direct modeler, no parametric history. Eliminated.
- **CadQuery** (Apache-2.0 — spdx NOASSERTION is a scanner artifact, LICENSE
  blob says Apache) and **OpenSCAD** (GPLv2 + CGAL exception; last stable
  release still 2021) remain viable-but-not-chosen.
- New since the decision: FreeCAD 1.1.3 current (2026-07-25), build123d
  v0.11.1 still latest, ocp-vscode had a major v4 rewrite. Assembly-level
  design (many mating parts) is where the toolbox was thinnest → ocp-vscode
  (visual cross-check) + bd_warehouse (shared fastener interfaces) added.

## Angle 3 — quadruped base donors, ranked

1. **Dingo Quadruped** (Ferguson & Calvert) — **MIT on both repos** (code +
   CAD, verified 2026; pushed 2026-03-27). 190 SolidWorks part/assembly files
   plus a whole-robot STEP. 12x CLS6336 35 kg·cm serial-bus servos; verified
   geometry from `Config.py`: L1=51.6 mm, L2=130 mm, L3=138.1 mm, ~250 mm
   stance, 223x122 mm hip footprint. Explicit design goal: carry extra
   actuators/sensors — i.e. a payload back, which is where our torso goes.
   Bearing-supported push-rod knee keeps servo mass proximal. **The base.**
2. **SpotMicroESP32** (Kubina remix) — GPL-3.0 covering the repo incl. CAD;
   **71 native FreeCAD .FCStd files** (opens in our exact toolchain), 58 STLs.
   Last pushed 2024-11-25. GPL is fine for a personal build; would bind
   derivative CAD if ever distributed. Backup / parts quarry.
3. **OpenQuadruped + Spot-Mini-Mini** (Elarabawy + Rahme) — 28 STEP + 64 STL;
   LICENSE is MIT text **plus an appended DMCA credit rider** (spdx
   NOASSERTION); spot_mini_mini itself clean MIT with RL training stack.
4. Lineage note: original **SpotMicro** (KDY0523) is CC-BY-4.0 (first-party
   Thingiverse JSON) but STL-only; **Nova SM3** MIT but effectively STL-only
   (232 STLs, 3 partial .f3d); **Mini Pupper** and **Petoi OpenCat/Bittle**
   publish no CAD at all despite open branding; **openDog** is the wrong
   actuator class (brushless + ODrive); **Pupper v3** GPL monorepo has no
   mechanical CAD; **CHAMP** (BSD-3) survives as the software layer.

## Angle 4 — torso/arms donors

**Winner: SO-ARM101** — single Apache-2.0 surface, pushed 2026-02-26, **36
STEP files** including `Base_SO101.step` and the STS3215 servo model. 6x
FEETECH STS3215 per follower arm (7.4V/16.5 kg·cm, 12V/30 kg·cm variant),
same TTL bus family as the owned ST3215/SC15. Flat-bottomed base + shipped
mounting-plate STEPs → bolts to the chest box top face via a printed adapter.
The build-guide PDF (`edu/SO-ARM101_LeRobot_KT_Guide-Custom.pdf`) was on hand in the working copy; it is not redistributed here (see THIRD_PARTY_NOTICES.md).
Verify the two-arms-side-by-side footprint against the 150 mm chest width
before committing; fallback is one stock arm + one custom shoulder.

Eliminated with verified cause: **InMoov** (CAD surface under a **non-commercial** Creative Commons
licence, STL-only, adult-scale); **Reachy** (no generation ships open hardware source;
Reachy Mini README: hardware is **non-commercial** share-alike); **Poppy** (CC-BY-SA
declared in prose, **no LICENSE file instantiated** — spdx null); **BCN3D
Moveo** (MIT but NEMA-stepper class, kg-scale arm); **Thor** (CC-BY-SA-4.0,
exemplary FreeCAD+STEP source — the runner-up if SO-ARM101 footprint fails);
**EEZYbotARM** (non-commercial Creative Commons). Centaur-form precedents (concept only, no reuse):
IIT **CENTAURO**, Bonn **Momaro** — both validate quadruped-base +
manipulation-torso as a serious research form factor.

## Carry-over from TelescopeBot → Alpha Centauri

Survives untouched: spine (coupler, rods, `spine_base.py`), chest box,
`hardware_constants.py`, and the spine math in the robot-runtime software (a
separate repository). Changes: waist box keeps its
shell/spine/battery core but its hip bays become four Dingo-style leg mounts
(the hip-DOF question from VERIFICATION.md is superseded); `leg_linkage.py`'s
DS5160 knee bracket informs the quad knee. New work: import Dingo CAD in
FreeCAD → re-author leg geometry in build123d sized to our servos; SO-ARM101
chest adapter plate; shoulder review.

## Next actions

1. Caliper session (54 UNVERIFIED constants) + print the coupler fit plate —
   unchanged, still gates everything.
2. Clone Dingo + SO-ARM100 repos; open the whole-robot STEP in FreeCAD 1.1.3;
   extract leg geometry + mount interfaces into `hardware_constants.py` as an
   INTERFACE section (one source of truth for mating parts).
3. Re-author Dingo-geometry legs in build123d against our servo pockets.
4. Decide: buy 8-12 more bus servos (STS3215-class unifies legs AND arms on
   one bus) vs mixed PWM fleet — electronics declared not-a-constraint, and
   one servo family simplifies everything.
