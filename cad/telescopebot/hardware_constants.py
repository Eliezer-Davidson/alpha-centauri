"""
TelescopeBot: hardware constants (single source of truth)

Every hardware dimension the TelescopeBot CAD scripts use. All values in
MILLIMETRES unless the name says otherwise (_CM, _G, _TEETH, _COUNT, _M).

Sources are named per group. Confidence below HIGH means the value came
from raster-measured drawings, community CAD, or clone-prone hardware --
those constants carry "# UNVERIFIED -- caliper before printing" and MUST
be verified against the shipped part before anything structural is
printed (house rule: MEASURE BEFORE TRUSTING).

Printer contract (Bambu Lab H2C, 0.4 mm nozzle, PETG): structural
walls >= WALL_MM, parts print support-free in export orientation,
self-tap pilots per M2_PILOT / M3_PILOT, clearance per M3_CLEAR.
CORRECTED 2026-08-01: this docstring previously named a FlashForge
Guider 3 Plus, which was never the house printer. Authoritative bed /
chamber / nozzle numbers live in
cad/alpha_centauri/interface_constants.py (330 x 320 x 325 mm, 65 C
chamber, 350 C nozzle); no telescopebot part exceeds the 325 mm Z.
SUPERSEDED 2026-09-07 (see edu/REPLAN-2026-08-28.md): the H2C above was
the H2C-era printer and is gone. Since 2026-08-28 the actual house
printer is a Bambu A1 mini — 180 x 180 x 180 mm bed, OPEN frame (no
heated chamber), 300 C nozzle max. interface_constants.py already
carries the A1 mini numbers; re-check any telescopebot part against
the 180 mm envelope before printing. The 2026-08-01 correction above
is kept as history, not as current fact.
"""

# ------------------------------------------------------- shared architecture
# TelescopeBot architecture + house printer rules (project-defined).
SPINE_ROD_SPACING_MM = 120.0     # center-to-center, the two vertical M8x1.25 rods
SPINE_TRAVEL_CM = 25.0           # chest-box vertical travel, 0..25 cm (NOTE: cm)
WALL_MM = 3.0                    # minimum structural wall
M2_PILOT = 1.8                   # self-tap pilot for M2
M3_PILOT = 2.7                   # self-tap pilot for M3
M3_CLEAR = 3.4                   # M3 clearance hole
M8_NUT_AF = 13.4                 # captive M8 hex-nut pocket, across flats
M8_NUT_POCKET_DEPTH = 7.0        # captive M8 hex-nut pocket depth

# Battery bay placeholder -- battery model unknown, envelope is a guess.
BATTERY_BAY_LENGTH = 110.0       # UNVERIFIED -- caliper before printing
BATTERY_BAY_WIDTH = 40.0         # UNVERIFIED -- caliper before printing
BATTERY_BAY_HEIGHT = 30.0        # UNVERIFIED -- caliper before printing

# ------------------------------------------- FS5103R continuous-rotation servo
# FEETECH FS5103R (spine drive). Official FEETECH FS5103B case drawing
# (Pololu PDF), corroborated by Adafruit #154. Confidence: HIGH.
# Add FS5103R_POCKET_CLEARANCE to body dims for printed pockets; horn
# coupler in spine_base.py already matches the 21.0 round horn.
FS5103R_BODY_LENGTH = 40.15
FS5103R_BODY_WIDTH = 20.15
FS5103R_BODY_HEIGHT = 37.2               # case bottom -> case top
FS5103R_HEIGHT_TO_SPLINE_TOP = 42.2      # case bottom -> spline top
FS5103R_FLANGE_LENGTH = 54.0             # flange plate overall, tab tip to tab tip
FS5103R_FLANGE_WIDTH = 18.8
FS5103R_HOLE_SPACING_LENGTH = 49.5       # 4x mount holes, lengthwise centers
FS5103R_HOLE_SPACING_WIDTH = 10.0        # across-width centers
FS5103R_HOLE_DIA = 4.5
FS5103R_HOLE_COUNT = 4
FS5103R_TAB_UNDERSIDE_HEIGHT = 25.9      # servo hangs this far below the mount plane
FS5103R_TAB_TOP_HEIGHT = 28.55           # case bottom -> tab top face
FS5103R_TAB_THICKNESS = 2.65
FS5103R_SHAFT_OFFSET_FROM_CENTER = 10.05  # shaft axis vs body lengthwise center
FS5103R_SHAFT_FROM_FRONT_FACE = 10.03
FS5103R_SHAFT_FROM_FRONT_HOLES = 14.7
FS5103R_SPLINE_TEETH = 25
FS5103R_SPLINE_DIA = 5.9
FS5103R_WIRE_LENGTH = 300.0
FS5103R_WEIGHT_G = 41.5
FS5103R_POCKET_CLEARANCE = 0.5           # add to body dims in printed pockets

# ------------------------------------------------- DS5160 60 kg-cm large servo
# DSSERVO/ANNIMOS DS5160 (large scale class, NOT standard 40x20). Official
# datasheet + raster-measured drawing (est +/-0.3 mm). Confidence: MEDIUM.
# The 75.0 is HOLE-CENTER spacing, not overall length; hole centers sit
# 5.1 OUTSIDE each body end face, so cradles need bosses beyond the body.
DS5160_BODY_LENGTH = 65.0                # UNVERIFIED -- caliper before printing
DS5160_BODY_WIDTH = 30.0                 # UNVERIFIED -- caliper before printing
DS5160_BODY_HEIGHT = 48.0                # UNVERIFIED -- caliper before printing
DS5160_HEIGHT_TO_SPLINE_TOP = 51.8       # UNVERIFIED -- caliper before printing
DS5160_OVERALL_HEIGHT_WITH_HORN = 56.8   # UNVERIFIED -- caliper before printing
DS5160_OVERALL_LENGTH_OVER_TABS = 82.0   # UNVERIFIED -- caliper before printing
DS5160_HOLE_SPACING_LENGTH = 75.0        # UNVERIFIED -- caliper before printing
DS5160_HOLE_SPACING_WIDTH = 17.0         # UNVERIFIED -- caliper before printing
DS5160_HOLE_DIA = 5.5                    # UNVERIFIED -- caliper before printing
DS5160_HOLE_COUNT = 4
DS5160_HOLE_BEYOND_BODY_FACE = 5.1       # UNVERIFIED -- caliper before printing
DS5160_TAB_THICKNESS = 4.0               # UNVERIFIED -- caliper before printing
DS5160_TAB_UNDERSIDE_HEIGHT = 31.0       # UNVERIFIED -- caliper before printing
DS5160_SHAFT_FROM_FRONT_FACE = 12.8      # UNVERIFIED -- caliper before printing
DS5160_SHAFT_FROM_FRONT_HOLES = 17.9     # UNVERIFIED -- caliper before printing
DS5160_SPLINE_TEETH = 25                 # UNVERIFIED -- caliper before printing (CONTESTED: 18T variant exists)
DS5160_WIRE_LENGTH = 300.0               # UNVERIFIED -- caliper before printing
DS5160_WEIGHT_G = 158.0                  # UNVERIFIED -- caliper before printing

# ----------------------------------------------- ST3215 30 kg-cm serial servo
# Waveshare ST3215 (= FEETECH STS3215). Measured from the vendor STEP
# (SO-ARM100 STS3215_03a.step) with build123d; matches the official
# 45.22 x 35 x 24.72 spec. Confidence: HIGH.
# No flanges: clamp between a face bracket (top 9.9 sq pattern, in the
# boss) and a bottom bracket (idler 9.9 sq pattern). SHORT screws only --
# holes are ~2.5 deep and long screws hit internals (Waveshare FAQ).
ST3215_BODY_LENGTH = 45.4
ST3215_BODY_WIDTH = 24.8
ST3215_BODY_HEIGHT_PLATES = 32.1         # case plate to case plate
ST3215_HEIGHT_BOSS_TO_BOSS = 36.4        # top boss face -> bottom boss face
ST3215_OVERALL_HEIGHT = 39.6             # incl spline + connector skirt
ST3215_SHAFT_FROM_FRONT_FACE = 10.2      # output axis, centered in width
ST3215_TOP_HOLE_SQUARE = 9.9             # 4x holes, square pattern about the axis
ST3215_TOP_HOLE_DIA = 2.5
ST3215_TOP_HOLE_DEPTH = 2.5              # blind -- short screws only
ST3215_BOSS_DIA = 20.0                   # raised output boss
ST3215_BOSS_PROTRUSION = 2.5
ST3215_BOTTOM_HOLE_SQUARE = 9.9          # identical pattern about the idler
ST3215_IDLER_SHAFT_DIA = 6.0
ST3215_IDLER_CENTER_HOLE_DIA = 2.5
ST3215_REAR_GROOVE_DIA = 4.0             # 2x half-cylinder locating grooves, full height
ST3215_REAR_GROOVE_INSET = 2.0           # groove axis from rear/side faces
ST3215_REAR_TOP_HOLE_DIA = 3.5           # 2x shallow holes, top rear corners
ST3215_CASE_SCREW_CBORE_DIA = 4.2        # keep-out: 4x counterbored case screws
ST3215_SPLINE_TEETH = 25
ST3215_SPLINE_DIA = 5.9
ST3215_HORN_SCREW_M = 3
ST3215_WEIGHT_G = 60.0

# ------------------------------------------------- SCS15 serial bus servo
# FEETECH SCS15 / Waveshare SC15. Official FEETECH SCS15-C022 spec sheet
# outline drawing (p.6); printed numbers, not the stretched raster.
# Confidence: HIGH.
# Boxy double-shaft case, face-mounted via 1.6 pilot holes for ~M2
# self-tappers. Column positions are along the length relative to the
# output/idler axis (positive toward the rear).
SCS15_BODY_LENGTH = 40.2
SCS15_BODY_WIDTH = 20.2
SCS15_BODY_HEIGHT = 40.0
SCS15_OVERALL_HEIGHT = 51.3              # incl spline + idler boss
SCS15_SPLINE_PROTRUSION = 5.7
SCS15_IDLER_BOSS_PROTRUSION = 5.6
SCS15_SHAFT_FROM_FRONT_FACE = 10.15      # output axis, centered in width
SCS15_MOUNT_HOLE_DIA = 1.6               # self-tap pilot, ~M2 screws
SCS15_MOUNT_HOLE_DEPTH = 4.0
SCS15_BOTTOM_ROW_SPACING = 15.0          # 2 rows x 3 cols, rows +/-7.5 off center
SCS15_BOTTOM_COLS_FROM_AXIS = (-7.5, 12.5, 27.5)
SCS15_TOP_ROW_SPACING = 14.0             # 4-hole rectangle rows, +/-7 off center
SCS15_TOP_COLS_BEHIND_AXIS = (20.15, 23.15)
SCS15_TOP_CENTER_HOLE_BEHIND_AXIS = 10.0
SCS15_TOP_FAR_CENTER_HOLE_BEHIND_AXIS = 27.15
SCS15_IDLER_SHAFT_DIA = 6.0
SCS15_IDLER_CENTER_HOLE_DIA = 2.5
SCS15_SPLINE_TEETH = 25
SCS15_SPLINE_DIA = 5.9
SCS15_ROUND_HORN_DIA = 19.95
SCS15_WEIGHT_G = 58.2

# --------------------------------------------------- MG996R standard servo
# TowerPro MG996R. Body dims from the TowerPro/Handsontec drawing; hole
# pattern from three measured community STEP models (no official pattern
# drawing exists) -- clones vary. Confidence: MEDIUM.
# DESIGN WITH SLOTTED HOLES (4.3 x 6 slots at the nominal spacing) and
# M3/M4 screws with washers.
MG996R_BODY_LENGTH = 40.3                # UNVERIFIED -- caliper before printing
MG996R_BODY_WIDTH = 20.0                 # UNVERIFIED -- caliper before printing
MG996R_FLANGE_SPAN = 54.0                # UNVERIFIED -- caliper before printing (53.6-54.6 across sources)
MG996R_FLANGE_UNDERSIDE_HEIGHT = 26.7    # UNVERIFIED -- caliper before printing
MG996R_FLANGE_THICKNESS = 2.4            # UNVERIFIED -- caliper before printing
MG996R_HEIGHT_TO_CASE_TOP = 36.6         # UNVERIFIED -- caliper before printing
MG996R_OVERALL_HEIGHT_WITH_HORN = 47.6   # UNVERIFIED -- caliper before printing
MG996R_HOLE_SPACING_LENGTH = 48.3        # UNVERIFIED -- caliper before printing (48.0-48.6 across clones)
MG996R_HOLE_SPACING_WIDTH = 10.2         # UNVERIFIED -- caliper before printing (10.0-10.4 across clones)
MG996R_HOLE_DIA = 4.2                    # UNVERIFIED -- caliper before printing (4.0-4.3 across clones)
MG996R_HOLE_SLOT_LENGTH = 6.0            # recommended slot length at HOLE_DIA width
MG996R_HOLE_COUNT = 4
MG996R_SHAFT_FROM_FRONT_FACE = 10.0      # UNVERIFIED -- caliper before printing
MG996R_SHAFT_FROM_FLANGE_TIP = 17.0      # UNVERIFIED -- caliper before printing
MG996R_SPLINE_TEETH = 25
MG996R_SPLINE_DIA = 5.9
MG996R_WEIGHT_G = 55.0                   # UNVERIFIED -- caliper before printing

# ------------------------------------------------------ MG90S micro servo
# TowerPro MG90S. Body dims from the TowerPro/Electronicos Caldas drawing;
# hole spacing/diameter and shaft offset from a community STEP model.
# Confidence: MEDIUM. Slot the holes to 2.8 x 3.5 (sources vary 2.2-2.8)
# and make the clamp height adjustable (flange underside varies 17.3-18.5).
MG90S_BODY_LENGTH = 22.8                 # UNVERIFIED -- caliper before printing (22.5-23.0)
MG90S_BODY_WIDTH = 12.2                  # UNVERIFIED -- caliper before printing (12.0-12.5)
MG90S_FLANGE_SPAN = 32.5                 # UNVERIFIED -- caliper before printing
MG90S_FLANGE_UNDERSIDE_HEIGHT = 18.0     # UNVERIFIED -- caliper before printing (17.3-18.5)
MG90S_FLANGE_THICKNESS = 2.3             # UNVERIFIED -- caliper before printing
MG90S_HEIGHT_TO_CASE_TOP = 24.1          # UNVERIFIED -- caliper before printing
MG90S_OVERALL_HEIGHT = 28.5              # UNVERIFIED -- caliper before printing (to output boss)
MG90S_OVERALL_HEIGHT_WITH_HORN = 35.5    # UNVERIFIED -- caliper before printing
MG90S_HOLE_SPACING = 27.8                # UNVERIFIED -- caliper before printing (2 holes, width centerline)
MG90S_HOLE_DIA = 2.7                     # UNVERIFIED -- caliper before printing (2.2-2.8 across sources)
MG90S_HOLE_COUNT = 2
MG90S_SHAFT_FROM_FRONT_FACE = 6.25       # UNVERIFIED -- caliper before printing
MG90S_GEAR_TOWER_DIA = 12.5              # UNVERIFIED -- caliper before printing
MG90S_SPLINE_TEETH = 21                  # SG90-compatible horns
MG90S_SPLINE_DIA = 4.8
MG90S_WEIGHT_G = 13.4                    # UNVERIFIED -- caliper before printing

# ------------------------------------- Jetson Orin Nano Developer Kit (P3768)
# Official carrier spec SP-11324-001 v1.3; hole positions measured from
# the to-scale Fig 4-1 (~+/-0.2 mm) and they reproduce the officially
# dimensioned P3449 Nano pattern exactly. Confidence: HIGH.
# Use M2.5 screws (M3 will NOT pass) and M3_CLEAR-sized slop in the print
# to absorb the residual uncertainty; check against the physical board.
ORIN_NANO_BOARD_LENGTH = 100.0
ORIN_NANO_BOARD_WIDTH = 79.0
ORIN_NANO_PCB_THICKNESS = 1.57
ORIN_NANO_HOLE_SPACING_X = 86.0
ORIN_NANO_HOLE_SPACING_Y = 58.0
ORIN_NANO_HOLE_FROM_LEFT_EDGE = 4.0      # datum hole
ORIN_NANO_HOLE_FROM_BOTTOM_EDGE = 17.0   # bottom = I/O edge
ORIN_NANO_HOLE_DIA = 2.75                # M2.5 screws; M3 will NOT pass
ORIN_NANO_ALT_HOLE_PAIR_X = 95.9         # second equivalent pair, 4.1 from right edge
ORIN_NANO_BOSS_OD_MAX = 8.0              # official keep-out around each hole
ORIN_NANO_BOSS_HEIGHT_MIN = 5.0          # clears 4.3 underside components
ORIN_NANO_UNDERSIDE_COMPONENT_MAX = 4.3
ORIN_NANO_TOPSIDE_COMPONENT_MAX = 16.7   # carrier only, no devkit base
ORIN_NANO_KIT_LENGTH = 103.0             # envelope with stock base + fan
ORIN_NANO_KIT_WIDTH = 90.5
ORIN_NANO_KIT_HEIGHT = 34.77

# ------------------------------- Jetson Nano Developer Kit (P3449, fallback)
# Original Nano devkit; official P3449 mechanical drawing (explicit
# dimension callouts). Confidence: HIGH. Identical 4-hole pattern to the
# Orin Nano devkit above -- one chest-box boss layout serves both boards.
JETSON_NANO_BOARD_LENGTH = 100.0
JETSON_NANO_BOARD_WIDTH = 79.0
JETSON_NANO_KIT_HEIGHT_WITH_HEATSINK = 29.0
JETSON_NANO_HOLE_SPACING_X = 86.0
JETSON_NANO_HOLE_SPACING_Y = 58.0
JETSON_NANO_HOLE_FROM_LEFT_EDGE = 4.0
JETSON_NANO_HOLE_FROM_BOTTOM_EDGE = 17.0
JETSON_NANO_HOLE_DIA = 2.75              # non-plated; M2.5 screws
JETSON_NANO_HOLE_KEEPOUT_OD = 8.0        # both sides of the board
JETSON_NANO_AUX_PTH_X = (12.2, 75.8)     # plated aux holes -- do NOT mount here

# ------------------------------------------ RealSense D435 / D435i camera
# Intel drawing MD0600012 rev V3, D400 datasheet 337029-005 p.106.
# Confidence: HIGH. Rear M3 screws must protrude <= 3.0 through the
# bracket or they bottom out. Keep the front face / FOV cones clear.
D435_BODY_LENGTH = 90.0
D435_BODY_HEIGHT = 25.0
D435_BODY_DEPTH = 25.05
D435_REAR_M3_SPACING = 45.0              # 2x M3x0.5, symmetric about body center
D435_REAR_M3_HEIGHT = 12.5               # mid-face line above bottom
D435_REAR_M3_MAX_INSERTION = 3.0
D435_TRIPOD_OFFSET_FROM_LEFT_IMAGER = 17.5   # 1/4-20 UNC boss, bottom face
D435_TRIPOD_FROM_ENDS = 45.0             # lengthwise center
D435_STEREO_BASELINE = 50.0

# ------------------------------------------------- RealSense D455 camera
# Intel drawing MD0665201 rev 02, D400 datasheet 337029-017 pp.148-150.
# Confidence: HIGH. Rear mounts are M4 (NOT M3 -- several aggregators are
# wrong), max insertion 4.0, max torque 0.4 Nm.
D455_BODY_LENGTH = 124.0
D455_BODY_HEIGHT = 26.0
D455_BODY_DEPTH = 29.0
D455_REAR_MOUNT_SPACING = 95.0           # 2x M4 on the mid-height line
D455_REAR_MOUNT_THREAD_M = 4             # M4, NOT M3
D455_REAR_MOUNT_MAX_INSERTION = 4.0
D455_REAR_MOUNT_HEIGHT = 13.0            # above bottom face
D455_TRIPOD_OFFSET_FROM_LEFT_IMAGER = 47.8   # 1/4-20 UNC boss, bottom face
D455_TRIPOD_FROM_ENDS = 62.0             # lengthwise center
D455_TRIPOD_MAX_INSERTION = 6.0
D455_STEREO_BASELINE = 95.0

# --------------------------------------------------- 40x40x10 mm axial fan
# Industry-standard 40 mm frame; ARCTIC official 1:1 mounting-hole drawing
# (rev 28-May-24), same pattern across Noctua/Sunon/etc. Confidence: HIGH.
# Grille/duct opening 38-38.5; M3_CLEAR holes + nuts or M3_PILOT self-taps.
FAN40_FRAME_SIDE = 40.0
FAN40_FRAME_THICKNESS = 10.0
FAN40_HOLE_SPACING = 32.0                # square pattern, holes 4.0 in from edges
FAN40_HOLE_DIA = 3.5
FAN40_OPENING_DIA = 38.2

# ------------------------------------------------ LM2596 buck converter
# Common D-SUN-style 43x21 board; Handsontec vendor drawing + pixel
# measurement. Confidence: MEDIUM -- clones vary (45x20 boards exist),
# use M3_CLEAR slots / oversized bosses and leave trimpot top access.
# Two holes on opposite corners (180-deg rotated), near IN+ and OUT-.
LM2596_BOARD_LENGTH = 43.18              # UNVERIFIED -- caliper before printing
LM2596_BOARD_WIDTH = 21.08               # UNVERIFIED -- caliper before printing
LM2596_HEIGHT = 14.0                     # UNVERIFIED -- caliper before printing (incl caps/inductor)
LM2596_HOLE_FROM_SHORT_EDGE = 6.6        # UNVERIFIED -- caliper before printing
LM2596_HOLE_FROM_LONG_EDGE = 2.54        # UNVERIFIED -- caliper before printing
LM2596_HOLE_SPACING_DX = 29.97           # UNVERIFIED -- caliper before printing
LM2596_HOLE_SPACING_DY = 16.0            # UNVERIFIED -- caliper before printing
LM2596_HOLE_DIA = 3.0                    # UNVERIFIED -- caliper before printing
