# TelescopeBot CAD Files

This directory holds all parametric CAD (build123d) and 3D-printable exports
(STL/STEP) for the TelescopeBot mid-sized humanoid.

## Environment

Run every script here with the CAD interpreter, `edu/.cadenv/bin/python`, from
the repository root — stage 2 of [BUILD.md](../../BUILD.md); the root README's
Quick start sets that interpreter up. It is NOT the simulation `.venv`.

```bash
edu/.cadenv/bin/python cad/telescopebot/spine_base.py      # regenerate coupler + coupon
edu/.cadenv/bin/python cad/render_stl.py out.png "label" part.stl   # proof render
```

## Print chain (FlashForge Guider 3 Plus)

CLI presets live in `edu/print_files/orca_presets_cli/` (machine / process /
filament). Use the **NoSupport** process for TelescopeBot parts — they are
designed support-free, and the plain "Structural" profile will pack support
into blind bores where it can never be removed:

```bash
$HOME/Applications/orcaslicer --debug 1 --slice 0 --arrange 1 --orient 0 \
  --load-settings "edu/print_files/orca_presets_cli/machine/FlashForge Guider 3 Plus 0.4 nozzle.json;edu/print_files/orca_presets_cli/process/0.20mm Structural NoSupport @Guider3Plus 0.4.json" \
  --load-filaments "edu/print_files/orca_presets_cli/filament/Generic PETG @Guider3Plus.json" \
  --outputdir OUT part1.stl part2.stl
```

Structural frame pieces print in PETG (creep + warm-servo softening rule
from `edu/MID_SIZE_HUMANOID_FEASIBILITY.md`); a PLA preset exists for
non-structural fit tests.

## Parts status

| Part | Script | State |
|---|---|---|
| Spine horn coupler + bore coupon | `spine_base.py` | Sliced (PLA + PETG gcode in `output/`), awaiting first print / fit test |
| Waist Box + servo deck | `waist_box.py` | Draft, adversarially verified (PASS_WITH_ISSUES — see `VERIFICATION.md`) |
| Chest Box | `chest_box.py` | Draft, adversarially verified (PASS_WITH_ISSUES — see `VERIFICATION.md`) |
| Thigh + Calf links | `leg_linkage.py` | Draft, adversarially verified (PASS_WITH_ISSUES — see `VERIFICATION.md`) |
| Hardware dimensions | `hardware_constants.py` | Researched (12 components); 54 UNVERIFIED constants need calipers |

Do NOT print the boxes/legs yet: `VERIFICATION.md` lists three open design
decisions (chest/waist nesting contradiction, hip DOF layout, MG996R slotted
holes) and every UNVERIFIED constant must be calipered first. The coupler +
coupon plate is the only print-ready job.

## First print: the fit test

1. Print `output/gcode_petg/plate_1.gcode` (coupler + bore coupon, ~1 h 39 m).
2. Thread the M8 rod into each coupon bore, smallest first (notch count:
   1 notch = 7.6 mm … 5 notches = 8.4 mm). The right bore is the tightest
   one the rod still threads into by hand — self-threading gives free axial
   retention.
3. Caliper the FS5103R round horn (diameter + screw hole circle) and press
   it into the coupler recess.
4. Update `ROD_BORE_DIAMETER`, `HORN_DIAMETER`, `HORN_SCREW_PITCH_CIRCLE`
   in `spine_base.py` from what you measured, regenerate, reprint the
   coupler only.

## Architecture Modules
1. **Lower Body (`leg_linkage.py`)**: Thigh, calf, ankle brackets with anchor points for surgical tubing (gravity compensation).
2. **Base Box (`waist_box.py`)**: Houses the hip servos and the base of the telescoping spine (2x FS5103R pointing up).
3. **Upper Box (`chest_box.py`)**: The moving carriage. Captive M8 nuts, Jetson compute, RealSense, shoulder joints.
4. **Arms**: Standard 5-DOF MG996R-driven arms and MG90s grippers (not started).
5. **Spine (`spine_base.py`)**: FS5103R horn-to-M8-rod coupler; twin M8x1.25 rods at 120 mm spacing.

## Open design risk — spine sync drift

The two FS5103R servos are continuous-rotation with NO position feedback.
Driven open-loop, left/right screws WILL desynchronize over cycles; because
the parallel rods are also the anti-rotation guide, differential advance
racks the chest carriage until it binds. Mitigations, in order of
preference:
1. **Mechanical sync**: one servo driving both screws via GT2 belt loop —
   eliminates the failure mode entirely, frees one servo.
2. Bottom hard-stop homing at every power-up + periodic re-home (software).
3. Upgrade to T8x8 lead screws (8 mm lead): 6.4x faster (31 s vs 200 s full
   travel) and printer-standard anti-backlash nuts; same coupler, one
   constant change (`SPINE_LEAD_MM_PER_REV = 8.0` in the robot runtime's
   telescopebot module, which lives outside this repository).
