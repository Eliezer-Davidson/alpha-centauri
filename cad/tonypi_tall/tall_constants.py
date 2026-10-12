"""TonyPi TALL variant — the one file that defines the whole design.

Every part script imports these. Change a number, re-run the part scripts,
and the entire variant regenerates. Safety rationale for each number is in
the comment beside it; the source analysis is edu/CAD-DECISION.md §4.

Stock reference numbers (measured from the sewn vendor STEP solids):
    长U支架 (leg/arm link)   56.0 x 64.5 x 25.0 mm   8.15 cm3
    短U支架 (short U joint)  56.0 x 42.5 x 25.0 mm   5.98 cm3
    斜U支架 (oblique U)      56.0 x 41.0 x 46.3 mm   6.66 cm3
    U梁   (U beam)           90.0 x 30.0 x 44.0 mm  18.88 cm3
    一字支架 (straight strap) 63.0 x 25.0 x  2.0 mm   2.55 cm3
    多功能支架 (multi-func)   58.3 x 25.5 x 37.0 mm   5.71 cm3
    L架   (L bracket)        25.0 x 37.0 x 30.0 mm   2.64 cm3
    脚板  (foot plate)       63.0 x 123.0 x 2.0 mm  12.38 cm3
    LX-824HV servo           40.0 x 52.5 x 20.1 mm, 57 g, 17 kg·cm stall,
                             ~5.1 kg·cm continuous thermal budget
"""

# ------------------------------------------------------------------ scale
# Chosen k for leg links: joint-to-joint ~80 mm -> ~94 mm  (k = 1.175).
# WHY NOT MORE: at k = 1.30 the worst standing pose (knee, 30 deg flexion,
# single support) costs 184% of the servo's continuous thermal budget and
# frame deflection grows 43x on PLA slabs (CAD-DECISION §4a/§4d). At
# k = 1.175 the same pose is ~166% before mass savings, ~155% after
# (~ -7% torque from lighter printed structure) vs 141% stock — a modest
# increase that keyframe gaits tolerate IF timings are rescaled (below).
LEG_LINK_EXT = 14.0     # 长U支架: 64.5 -> 78.5 mm along the arm axis
K_JOINT = (80.0 + LEG_LINK_EXT) / 80.0   # ~1.175  (L_thigh 80 mm UNVERIFIED
#                                          — measure the real robot, §4 note)

# MANDATORY companion change (free fix, CAD-DECISION §4b): rescale every
# .d6a keyframe duration by K_JOINT so dynamic torque returns to stock.
D6A_TIME_SCALE = K_JOINT

STRAP_EXT = 10.0        # 一字支架: 63 -> 73 mm
BEAM_EXT = 20.0         # U梁: only if the assembly check confirms it is a
#                         VERTICAL torso member; horizontal use -> keep stock.

# ------------------------------------------------------------------ feet
# "Platform boots". CAD-DECISION §4d: scaling the feet is the highest
# value-per-gram change in the project — it buys back the tipping budget
# that the added height spends. Width scales MORE than k (1.30 > 1.175) so
# net static margin improves ~16% despite the higher CoM.
FOOT_W = 82.0           # 63 -> 82 mm  (x1.30)
FOOT_L = 132.0          # 123 -> 132 mm (x1.07 — length gains kept small so
#                         swing-phase toe clearance is not disturbed)
SOLE_H = 10.0           # platform sole height under the original plate.
#                         Model SOLID; the slicer's 15% infill makes it light
#                         (~30 g/foot in PETG). Original 2 mm plate remains
#                         the top skin with its hole pattern 1:1.
SOLE_ACCESS_D = 7.0     # through-bores under every original M3 hole so
#                         screws stay reachable from below.

# ------------------------------------------------------------------ webs
# Torsion is the printed frame's scarcest stiffness resource; a closed box
# section is what makes a PETG link viable at all (open PETG arms alone:
# ~19.7x the deflection of aluminium at equal section).
#
# CORRECTION (measured, cad/tonypi_tall/servo_envelope.py): v1 closed the
# *extension zone* on the claim that new material is "guaranteed servo-free".
# That claim was FALSE. Hole-free is not the same as empty. Registering the
# real LX-824HV (40.04 x 52.54 x 20.14 mm, output boss Ø5.04, shaft 30.02 mm
# from the body's far end) to the bracket's Ø8.20 hub hole shows:
#
#   长U支架_tall  hub y=64.00  ->  servo body occupies y [33.97, 74.01]
#                 v1 band [22.50, 38.50] overlapped it by 4.53 mm, and the
#                 plates left 25.00 - 2x2.5 = 20.00 mm clear vs a 20.14 mm
#                 servo: -0.14 mm, an interference fit.
#
# The stretch does not just move the hub up — it OPENS 31.6 mm of channel
# below the servo. Closing that instead is strictly better: full-thickness
# walls, zero interference, and ~2x the closed length v1 had.
# Wall thicknesses are snapped to whole multiples of the extrusion width
# (see MACHINE below) so every wall prints as pure perimeters — no gap fill,
# no under-filled seam down the middle of the part's only stiffness member.
LEG_CLOSE_LO = 6.0      # channel floor measured at y=0.35; +6 clears a servo
#                         horn disc up to ~5.6 mm thick on the web (the one
#                         part of this the manual cannot settle)
LEG_CLOSE_HI = 33.5     # servo body starts at y=33.97 — 0.47 mm below it

# ------------------------------------------------------------------ machine
# Bambu Lab H2C (corrected 2026-07-31 — the repo's orca_presets_cli are for a
# FlashForge Guider 3 Plus and DO NOT APPLY).
# STALE — H2C era (annotated 2026-09-07, see edu/REPLAN-2026-08-28.md).
# The H2C is gone; the actual printer since 2026-08-28 is a Bambu A1 mini
# (180 x 180 x 180 mm, OPEN frame — no chamber, 300 C nozzle max). TonyPi
# TALL is PARKED; values below are left unchanged as H2C-era record so
# nothing downstream shifts silently. Do NOT plan PET-CF/PAHT-CF prints on
# the strength of CHAMBER_MAX_C/NOZZLE_MAX_C below — neither is available
# on the A1 mini. If this project un-parks, re-derive from
# cad/alpha_centauri/interface_constants.py.
PRINTER = "Bambu Lab H2C"              # STALE — H2C era, see note above
BUILD_VOLUME = (330.0, 320.0, 325.0)   # mm; largest part here is 132 mm — STALE, A1 mini is 180^3
NOZZLE_MAX_C = 350                     # STALE — A1 mini max is 300 C
BED_MAX_C = 120
CHAMBER_MAX_C = 65      # ACTIVELY heated — this is what unlocks PET-CF/PAHT-CF
#                         STALE — A1 mini is open-frame; no heated chamber exists

# NOZZLE_D is the PHYSICALLY INSTALLED nozzle. Changing it in the slicer is a
# declaration, not an action — it swaps no hardware. Set this to what is in the
# machine; the walls below re-derive from it.
NOZZLE_D = 0.4          # standard hardened 0.4, currently installed
LINE_W = round(NOZZLE_D * 1.05, 3)     # 0.42 at 0.4 nozzle, 0.63 at 0.6

# ------------------------------------------------------------------ webs (2)
# Walls are whole multiples of LINE_W so they print as pure perimeters — no gap
# fill down the middle of the part's only stiffness member.
_FINE = NOZZLE_D <= 0.5
WEB_WALL = round(LINE_W * (6 if _FINE else 4), 3)     # 2.52 EITHER WAY
REINF_WALL = round(LINE_W * (4 if _FINE else 3), 3)   # 1.68 at 0.4, 1.89 at 0.6
# REINF_WALL is what buys 短U's servo clearance — its servo fills the bracket
# end to end (y [-2.02, 38.02] in a y[-2, 40.5] part) so no servo-free span
# exists and the wall is the only lever:
#     0.4 nozzle -> 1.68 mm -> 25.00 - 3.36 = 21.64 clear vs 20.14 -> 0.75/side
#     0.6 nozzle -> 1.89 mm -> 25.00 - 3.78 = 21.22 clear vs 20.14 -> 0.54/side
# The 0.4 nozzle is the BETTER one here. Still a CONCEPT part either way:
# test-fit a real LX-824HV before printing a set.

# ------------------------------------------------------------------ head
# NOTE: we do NOT have the head shell CAD. LFD-01.stp is the head SERVO,
# not the shell. The mohawk is therefore a standalone clip-on crest with a
# parametric saddle; the two numbers below are GUESSES to be replaced by
# caliper measurements of the real head (or a scan/vendor file).
HEAD_W = 55.0           # UNVERIFIED — saddle inner width across the head
HEAD_R = 45.0           # UNVERIFIED — saddle arc radius front-to-back
CREST_H = 40.0          # fin height above the saddle (visual +~40 mm)
CREST_L = 110.0         # crest length along the head midline
CREST_T = 6.0           # fin thickness at the base
CREST_N_SPIKES = 7      # spartan spikes along the top edge
STRAP_SLOT = (4.0, 2.0) # zip-tie slots (w, h) in the saddle skirt

# ------------------------------------------------------------------ height
STOCK_HEIGHT = 380.0    # mm, UNVERIFIED — assembly check confirms from PDF
HEIGHT_GAIN_LEGS = 2 * LEG_LINK_EXT          # thigh + shank per leg = +28
HEIGHT_GAIN_SOLE = SOLE_H                    # +10
HEIGHT_GAIN_TORSO = BEAM_EXT                 # +20 IF beam is vertical
# functional height: +38 mm confirmed, +58 mm with torso  (~+10..15%)
# apparent height with crest: ~ +98 mm at the mohawk tip

# ------------------------------------------------------------------ material
# REVISED for the H2C. The 65 C actively-heated chamber is not a nicety here,
# it changes which material the legs can be made of, and that was the design's
# stated weak spot. Bambu published bending moduli:
#     PETG      ~2.0 GPa (approx, grade-dependent)   HDT ~70 C
#     PETG-CF    2.91 GPa   tensile  70 MPa          HDT   74 C
#     PAHT-CF    4.23 GPa   tensile 125 MPa   impact 57.5 kJ/m^2
#     PET-CF     5.32 GPa   tensile 131 MPa   impact 36.0 kJ/m^2   HDT 205 C
#     Al 6061   69 GPa  (the metal these brackets are today)
# PET-CF is 2.7x stiffer than plain PETG, which takes the closed-box link from
# ~4-8x stock deflection to roughly ~1.5-3x. SECOND reason, from CAD-DECISION
# §4a: the knee runs at ~155% of the servo's CONTINUOUS thermal budget, so the
# bracket clamping it gets hot — a 74 C HDT (PETG/PETG-CF) is the wrong side of
# that line. PET-CF's 205 C is not.
MATERIAL_LEGS = "PET-CF"        # 长U links + 短U concept. Dry it; hardened 0.6;
#                                 chamber ON. PAHT-CF instead if falls (not
#                                 deflection) turn out to be the failure mode:
#                                 60% better impact, 21% less stiff.
MATERIAL_FEET = "PETG or PETG-CF"   # boots are a 10 mm slab in compression —
#                                     stiffness is not binding; toughness and
#                                     grip are. Chamber OFF for PETG.
MATERIAL_CREST = "PLA"          # decorative, unloaded — and the one part where
#                                 a colour is the whole point.
MATERIAL = MATERIAL_LEGS        # back-compat for anything reading MATERIAL
# NO PLA anywhere structural (creeps under standing load, CAD-DECISION §4d).

# ---- what is ACTUALLY on the shelf right now --------------------------------
# PLA only. That does not block the first run, but it narrows what the run can
# answer, and the narrowing must be stated rather than discovered later:
#   ANSWERED by a PLA print — every dimension. Hole sizes, wall thickness,
#     shrinkage, servo slot fit, whether brackets bolt up. PLA is in fact the
#     BEST fit-test material: dimensionally stable, no chamber, no drying.
#   NOT ANSWERED — whether a printed bracket survives standing on the robot.
#     PLA is stiff (~3.5 GPa, above PETG) but creeps under sustained load and
#     is brittle. A PLA leg will feel right on the bench and sag over days.
# So run 1 = FIT + TOLERANCE only. Leave it off a robot that has to stand.
MATERIAL_ON_HAND = "PLA"
RUN1_SCOPE = "fit and tolerance only — NOT strength, NOT durability"
PRINT_PROFILE = (f"Bambu Studio / OrcaSlicer, H2C {NOZZLE_D} hardened, "
                 f"0.20 mm layer, {MATERIAL_ON_HAND}")
