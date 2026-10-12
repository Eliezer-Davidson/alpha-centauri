# BUILD — the order that actually works

Nothing in this repository is a package you import; every module is a script that
reads STEP files off disk and writes STEP files back. That makes the dependency
graph a *file* graph, and running it out of order does not produce a helpful
error — it produces a `FileNotFoundError`, or worse, a **silently different
number**. This file is the graph.

Two interpreters, never mixed:

| lane | python | packages |
|---|---|---|
| CAD | 3.11 (`edu/.cadenv`) | build123d, trimesh, rtree, numpy, matplotlib, pillow |
| simulation | 3.12 (`.venv`) | mujoco >= 3.12, numpy < 2.4, imageio\[ffmpeg\], matplotlib |

Everything below is run from the repository root. `CADPY=edu/.cadenv/bin/python`,
`SIMPY=.venv/bin/python`.

---

## Stage 1 — the parts

`chassis`, `thigh`, `calf`, `joint_parts`, `hip_module`, `waist_rail`,
`spine_lock` and `foot` are independent of each other. Each runs its gates and
refuses to write its STEP if a gate fails, so a non-zero exit from one of those
is a real result.

**`dock.py` is the exception and must run last.** It draws the docked-robot
evidence view, so it imports `waist_rail.py`'s two rail ways and `thigh.py`,
`calf.py` and `foot.py`'s solids off disk. Run it on an empty `output/` and it
exits 1 with the list of modules to run first. The loop below is in the right
order.

```bash
for m in chassis thigh calf joint_parts hip_module waist_rail spine_lock foot dock; do
  $CADPY cad/alpha_centauri/$m.py || break
done
```

Typical wall-clock on a laptop: ~13–35 s per module, about 2½ minutes for the set.

> **Two gate lines print `FAIL` in a passing run, and that is expected.**
> `foot.py` prints `FAIL watertight` for both foot solids and still ends
> `ALL GATES GREEN` with exit 0. `partcheck`'s watertight probe cannot pass a
> sphere — the pole fan leaves zero-length edges — so `foot.py` proves closure
> independently (`assert_closed`, `foot.py:537` and `:748`) and prints
> `closure: … verified independently (… the known sphere artifact)` for each
> part. `chassis.py` likewise prints `WARN bed contact (136 mm², want ≥ 150)`
> on the 0.7 g splice key while its bed gate reports OK.

## Stage 2 — the donor torso

`cad/telescopebot/` is a separate part set, and both the assembly views **and the
MJCF exporter** read its output.

```bash
for m in waist_box chest_box spine_base leg_linkage; do
  $CADPY cad/telescopebot/$m.py || break
done
```

> **This stage is not optional, and skipping it fails quietly in one place.**
> `sim/mjcf_export.py` raises `FileNotFoundError: cad/telescopebot/output/waist_box.step`
> — loud, fine. But `assembly.py` *succeeds* without the chest box and falls back
> to a lower reference plane, printing `STANDING HEIGHT ... 331 mm` instead of the
> real **671 mm**. Run stage 2 before you read any height number off stage 3.

## Stage 3 — assemblies and the interactive pages

```bash
$CADPY cad/alpha_centauri/assembly.py           # quadruped, swept-interference asserts
$CADPY cad/alpha_centauri/assembly_centaur.py   # + torso, WALK/WORK stations
$CADPY cad/alpha_centauri/build_report.py       # needs assembly_centaur's output
$CADPY cad/alpha_centauri/marks.py work         # pose page, chest up
$CADPY cad/alpha_centauri/marks.py work_condensed
$CADPY cad/alpha_centauri/extension_stowage.py  # stowage study
```

Both of these fail on an empty `output/`, which is correct behaviour rather than a
bug — verified by deleting the directory and re-running:

```
$ marks.py work        -> FileNotFoundError: .../output/thigh_shell.step
$ build_report.py      -> run assembly.py first
```

`marks.py` wants stage 1's part STEPs. `build_report.py` actually scans
`output/centaur/*.stl`, which **`assembly_centaur.py`** writes — its message names
`assembly.py`, which is not quite right; run both assemblies and it succeeds.

The HTML pages land in `cad/alpha_centauri/output/` and carry pose sliders: drag
the chest up and down, slide the waist between WALK and WORK, drag individual
parts. Press `N` in the page to hide the notes.

## Stage 4 — the simulation

```bash
$CADPY cad/alpha_centauri/sim/mjcf_export.py            # CAD -> 4 MJCFs + provenance.json
MUJOCO_GL=glx $SIMPY cad/alpha_centauri/sim/crawl_sim.py
```

`mjcf_export.py` needs stages 1 and 2 (20 STEP files). `crawl_sim.py` needs
`cad/alpha_centauri/output/sim/provenance.json` and refuses to run without it;
it also compares the snapshotted constants against the live ones and warns on
drift.

Rendering needs a GL context. `MUJOCO_GL=glx` with a live `DISPLAY` is the tested
path on the laptop these results were measured on; `egl` fails there.
`xvfb-run -a` is the headless fallback.

Wall clock: export 3-9 s, crawl 26-45 s (cold cache is the slow end). The whole
chain above measured 348 s end to end on a laptop.

---

## The whole chain, in one block

```bash
CADPY=edu/.cadenv/bin/python
SIMPY=.venv/bin/python
set -e
for m in chassis thigh calf joint_parts hip_module waist_rail spine_lock foot dock; do
  $CADPY cad/alpha_centauri/$m.py; done
for m in waist_box chest_box spine_base leg_linkage; do
  $CADPY cad/telescopebot/$m.py; done
$CADPY cad/alpha_centauri/assembly.py
$CADPY cad/alpha_centauri/assembly_centaur.py
$CADPY cad/alpha_centauri/build_report.py
$CADPY cad/alpha_centauri/sim/mjcf_export.py
MUJOCO_GL=glx $SIMPY cad/alpha_centauri/sim/crawl_sim.py
```

About four minutes of CAD plus a minute of simulation. The end state is
`cad/alpha_centauri/output/sim/results.json`, which should match
`docs/evidence/sim_results.json` — see [docs/EVIDENCE.md](docs/EVIDENCE.md) for
exactly which values are bit-stable and which drift in their last digit.

## Not part of the chain

`cad/tonypi_tall/` reads HiWonder's own CAD, which is not redistributed in this
public copy. Point `TONYPI_STOCK_STEP_DIR` and `HIWONDER_CAD_DIR` at your own
download first; `cad/tonypi_tall/vendor_paths.py` reads both and fails with a
message naming [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) when they are
absent. `fit_gauge.py` is the exception — it builds from primitives and runs with
no vendor input at all.

## What is deliberately not committed

`cad/*/output/` and `cad/*/assembly/` — about 200 MB per rebuild of STEP, STL,
3MF and HTML. The design is the Python. The curated proof set is
`docs/evidence/`, and the README's figures are `docs/media/`.
