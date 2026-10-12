# Third-party notices

Everything in this repository was written for this repository (see
[LICENSE](LICENSE)) **except** the items listed here, which belong to their
respective owners and are included only as build inputs and reference. Nothing
below is claimed as this repository's own.

---

## What was REMOVED for this public copy, and how to get it

The private working copy of this project carried vendor files whose
redistribution terms are unverified. A private working copy is not the same
permission as publication, so every one of them has been taken out of this
repository. Each row below says where the original is published; nothing here
is secret, it simply is not this repository's to redistribute.

| Removed | Owner | Where to obtain it | What stops working without it |
|---|---|---|---|
| `cad/vendor/waveshare_feetech_st3215_servo.step` | Waveshare / FEETECH | The [step.parts](https://step.parts) catalogue, by part name (checksum-verified when it was obtained) | Nothing. `cad/alpha_centauri/marks.py` guards it with `.exists()` (lines 343, 412) and simply omits the servo visual from the pose pages. The whole `cad/alpha_centauri` chain was re-run without it. |
| `edu/vendor-cad/` — `LX-824HV.STEP`, `LX-824HV.dwg`, `LX-824HV_manual.pdf`, `LFD-01.stp`, `Bracket.rar`, 8 `.IGS` solids, 8 `.DXF` drawings | HiWonder | HiWonder's TonyPi product pages and official CAD download folders. `edu/CAD-DECISION.md` records the exact provenance and file identities. | `cad/tonypi_tall/check_servo_clearance.py`, `servo_envelope.py`, and `edu/tools/{iges_to_solid,dxf_holes,generate_print_files}.py`. Set `HIWONDER_CAD_DIR` to your own download. |
| `edu/datasheets/*.pdf` (6 files) — TonyPi, Mini Hexa, Mech Dog, AI Quadruped, RosPug, SO-ARM101/LeRobot guide | HiWonder (5) and the SO-ARM101/LeRobot project (1) | HiWonder product pages; the SO-ARM101 guide is a customised PDF derived from the Apache-2.0 upstream project | Nothing. Reference reading only. |
| `edu/print_files/step/*.step`, `edu/print_files/stl/*.stl` (8 + 8) — HiWonder's original printable frame parts | HiWonder | HiWonder's TonyPi print-file download | `cad/tonypi_tall/build_all.py`, `compare_sheet.py`, `hero_sheet.py`. Set `TONYPI_STOCK_STEP_DIR` / `TONYPI_STOCK_STL_DIR`. |
| `edu/print_files_tall/{step,stl}/*` and `RUN1/plate1_parts/*` — the TALL bracket variants, **except** `fit_gauge` and `mohawk_crest` | HiWonder (base geometry) + this repository (the modification) | Regenerate them by running `cad/tonypi_tall/build_all.py` against your own copy of the vendor STEPs | Nothing that is not already covered above. |
| `edu/print_files_tall/renders/*_before.png`, `*_after.png`, `hero/*_stock.png`, `hero/stock_vs_tall.png`, `hero/new_pieces.png`, `renders/review_sheet.png`, `edu/print_files/orientation/orientation_sheet.png` | renders **of** HiWonder's geometry | Regenerate with `cad/tonypi_tall/hero_sheet.py` / `compare_sheet.py` / `montage.py` once the vendor CAD is in place | Nothing. |

`cad/tonypi_tall/vendor_paths.py` is the single place those environment
variables are read; every consumer asks it, and it fails with a message naming
this file when the directory is absent.

**Kept, because they are this repository's own geometry, built from primitives
with no vendor solid as input:** `edu/print_files_tall/step/fit_gauge.step` and
`mohawk_crest.step` (and their STLs and hero renders). `build_all.py`'s own
docstring calls `mohawk_crest` a new clip-on part, and `fit_gauge.py` builds its
gauge entirely from boxes and cylinders.

**Still open, and recorded as open:** `edu/CAD-DECISION.md` and
`edu/TONYPI-TALL-DESIGN.md` both note that the clean commercial answer for the
TALL variant is a direct question to HiWonder about modifying, printing and
selling derived parts. That question has not been answered, which is exactly why
no derived geometry ships here.

---

## Derived geometry

| What | Source | Licence | How it is used |
|---|---|---|---|
| Quadruped leg kinematics — `L1`/`L2`/`L3`, `phi`, the IK and its gait config | [MonashRobotics/DingoQuadruped](https://github.com/MonashRobotics/DingoQuadruped) — Copyright (c) Monash Robotics, MIT licence | MIT | Link lengths and the IK are read from the donor's own `Config.py` / `Kinematics.py` and re-derived in `cad/alpha_centauri/interface_constants.py`. The simulation ports the donor IK faithfully (`cad/alpha_centauri/sim/dingo_ik.py`) with its deviations marked in-file. **Alpha Centauri deviates from the donor** by driving the knee directly instead of through the donor's hip-mounted four-bar. MIT permits redistribution of derived work with attribution; this row is that attribution. |

## Measured from vendor drawings

| What | Note |
|---|---|
| `edu/frame/constants.py` | Hole pitches, hole diameters and the servo envelope, read off HiWonder's DXF drawings with `edu/tools/dxf_holes.py`. It contains **numbers, not vendor geometry** — dimensions are facts, not expression — and no vendor file is included. |

## Slicer presets

`edu/tools/make_guider3plus_profile.py` generates the OrcaSlicer presets under
`edu/print_files/orca_presets_cli/`. The generator and the structural process
overrides were written for this project; two inputs it writes out were not, and
are itemised here because the generator's own docstring names their origin.

| What | Source | Licence | How it is used |
|---|---|---|---|
| The machine start/end G-code sequence in `edu/print_files/orca_presets_cli/machine/*.json` | [OrcaSlicer](https://github.com/OrcaSlicer/OrcaSlicer) | AGPL-3.0 | Taken **verbatim** from OrcaSlicer's shipped FlashForge Guider 2s override, with the purge line relocated to this machine's front edge. `make_guider3plus_profile.py` says so at its `START_GCODE` definition, and that comment is the derivation record. |
| The PLA temperature and speed parameters in `edu/print_files/orca_presets_cli/filament/Generic PLA @Guider3Plus.json` | FlashForge / FlashPrint 5.8.7 | proprietary software; the values are **numbers, not expression** | Read off the vendor's own `profile.dat`, section "FlashForge Guider 3 Plus-0.4/PLA-1.75/Standard". No FlashForge file is included here. |

What **is** this repository's own in those presets: the 350 × 350 × 600 mm bed envelope
and centre origin derived from a real sliced `.gx`, the structural process
overrides (wall count, infill, the deliberate departures from FlashForge's
display-print defaults, each commented in the generator), and the generator
itself.

These files carry `"from": "system"`. That is **not** a claim that FlashForge or
OrcaSlicer shipped them: it is a functional workaround, recorded at
`make_guider3plus_profile.py:361-364` — OrcaSlicer 2.3.0's `--load-settings`
rejects `from="User"` with "process not compatible with printer", verified
against the shipped Guider 2s profile too. The GUI copies the same generator
writes do carry `"from": "User"`, and are not committed here.

## Tooling depended on, not vendored

| What | Licence |
|---|---|
| [build123d](https://github.com/gumyr/build123d) (and OCCT beneath it) | Apache-2.0 / LGPL — installed into a venv, never committed here |
| [MuJoCo](https://github.com/google-deepmind/mujoco) — Google DeepMind | Apache-2.0 — used by `cad/alpha_centauri/sim/`, installed separately |
| [trimesh](https://github.com/mikedh/trimesh), [rtree](https://github.com/Toblerity/rtree) | MIT — used by `edu/tools/partcheck.py` and `cad/tonypi_tall/` |
| numpy, matplotlib, imageio, pillow | BSD / PSF / BSD / MIT-CMU |

## Named for comparison only

`cad/shortarm/shortarm_spec_v1.png` plots the SO-ARM101 arm as a scale and mass
reference. No SO-ARM101 geometry, code or documentation is included.

## Everything else

Everything else was written for this repository: all of `cad/alpha_centauri/`
(chassis, thigh, calf, foot, hip module, waist rail, spine lock, dock, marks, the
analyses, and the MJCF export and crawl simulation), `cad/telescopebot/`,
`cad/tonypi_tall/` (the code), `cad/shortarm/`, `edu/tools/`, `edu/frame/`, and
every design document.

The slicer presets under `edu/print_files/orca_presets_cli/` are **mixed** and are
itemised under "Slicer presets" above: the bed envelope, the structural process
overrides and the generator are this repository's own; the machine G-code
sequence and the PLA numbers are not.
