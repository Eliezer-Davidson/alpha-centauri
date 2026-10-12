"""Alpha Centauri — THE interface block. Single source of truth for every
dimension that more than one thing depends on.

Why this file exists
--------------------
the design log, D11: TonyPi's 116 action groups (2,375 keyframes, ~38,000 joint
values) are invalidated the moment a link length changes. The generalisation is
that a shared dimension assumed independently in two places is a latent bug, and
this project has already paid for that once -- cad/telescopebot/VERIFICATION.md
records a 0.30 mm ligament that existed because a servo horn's screw circle was
ASSUMED rather than measured.

So: the CAD imports these, the gait config imports these, and a test asserts the
two agree. Nothing re-derives a shared number locally.

Provenance discipline
---------------------
Every constant carries where it came from:

    VERIFIED   -- read out of a primary source (vendor drawing, donor repo's own
                  config, or a caliper on the actual part). Trustworthy.
    NOMINAL    -- a datasheet figure for a part not yet in hand. Good enough to
                  draw against, NOT good enough to print a mating pocket from.
    DERIVED    -- computed here from other constants in this file.
    DECISION   -- a design choice with no external authority; the rationale is
                  in the comment and in edu/ALPHA-CENTAURI-PLAN.md.

A NOMINAL servo dimension must be re-measured before the part that mates with it
is printed. That is the P0 caliper gate.

Units are millimetres, degrees, grams, and kg-cm for torque, matching
cad/telescopebot/hardware_constants.py.
"""

import math

# ---------------------------------------------------------------- provenance
VERIFIED = "VERIFIED"
NOMINAL = "NOMINAL"
DERIVED = "DERIVED"
DECISION = "DECISION"


# ============================================================================
# 1. DONOR LEG GEOMETRY -- Dingo, and it does not change
# ============================================================================
# Source: MonashRobotics/DingoQuadruped (MIT), read directly out of
#   dingo_ws/src/dingo_control/src/dingo_control/Config.py
# NOT quoted through any summary document -- an earlier draft of this project
# misread `default_z_ref` (a stance HEIGHT) as a stance WIDTH.
#
# Locked at k = 1.0. Scaling the links is the one change that makes servo
# torque unaffordable, and it also invalidates the donor's gait tuning.

L1_HIP_OFFSET = 51.62024721   # VERIFIED  Config.py self.L1 * 1000
L2_THIGH = 130.0              # VERIFIED  Config.py self.L2 * 1000
L3_CALF = 138.13664159        # VERIFIED  Config.py self.L3 * 1000

LEG_REACH_MAX = L2_THIGH + L3_CALF                      # DERIVED  268.14 mm

# L1 IS A DIAGONAL, NOT A LATERAL OFFSET. This is the single most-repeated
# mistake in this project. The abduction link runs from the abduction axis to
# the hip-pitch axis, and at zero abduction it goes 49.60 mm OUTBOARD and
# 14.30 mm UP at the same time:
#
#       hypot(49.60, 14.30) = 51.6202480  ==  Config.py self.L1 * 1000
#       atan2(49.60, 14.30) = 73.9173872  ==  Config.py self.phi (deg)
#
# 49.60 and 14.30 are the PRIMITIVES -- they are what the URDF stores
# (joint FL_theta2 origin xyz="0.0496 0.0144 0" in the link1 frame, whose x is
# base +Y and whose y is base +Z). L1 and phi are what Dingo derived from them.
# Independently confirmed by Dingo's own default stance: DINGO_DELTA_Y -
# DINGO_LEG_LR = 110.6 - 61.0 = 49.600, i.e. its default foot sits exactly under
# the hip-pitch axis at zero abduction (its IK returns theta_1 = 0.000).
#
# Consequences of using the 51.62 hypotenuse as if it were lateral:
#   * the foot is drawn 2.02 mm too far outboard per side (footprint 283.2 vs
#     the true 279.2 mm), and
#   * the hip-pitch axis is drawn at the abduction axis's height, which silently
#     turns a 235 mm stance into the 249.3 mm one this project rejected.
# Both of those were live in assembly.py until 2026-07-31.
L1_LATERAL = 49.60    # VERIFIED  dingo.urdf FL_theta2 origin, = DELTA_Y - LEG_LR
L1_VERTICAL = 14.30   # VERIFIED  dingo.urdf FL_theta2 origin
PHI_DEG = 73.91738698  # VERIFIED  Config.py self.phi, = atan2(L1_LATERAL, L1_VERTICAL)

# The vertical component, under the name the rest of the project already uses.
# In-plane leg extension is stance height PLUS this -- with the foot on the
# ground the leg spans MORE than the body stands tall. Getting this sign wrong
# halved every knee-torque estimate; it has now bitten the project twice.
HIP_PITCH_AXIS_ABOVE_DATUM = L1_VERTICAL   # DERIVED  14.30

# Dingo's own stance, kept only as the reference we are deviating from.
DINGO_LEG_FB = 111.65     # VERIFIED  half the fore-aft hip spacing
DINGO_LEG_LR = 61.0       # VERIFIED  half the lateral hip spacing
DINGO_DELTA_X = 117.0     # VERIFIED  default foot fore-aft position
DINGO_DELTA_Y = 110.6     # VERIFIED  default foot lateral position
DINGO_STANCE_Z = 250.0    # VERIFIED  -default_z_ref * 1000
DINGO_REAR_X_SHIFT = -40.0  # VERIFIED  rear feet sit back, mass is rear-biased


# ============================================================================
# 2. ALPHA CENTAURI DEVIATIONS -- the body grows, the legs do not
# ============================================================================
# Spreading the hips changes the support polygon, NOT the per-leg torque: each
# leg still carries its share through the same links at the same stance height.
# So footprint is the cheapest stability there is -- it costs filament.
# Both of these are runtime parameters in Dingo's config, so widening the robot
# is a number change rather than a fork of its kinematics.

LEG_FB = 250.0   # DECISION  half the 500 mm fore-aft hip span (the author, 2026-07-31)
LEG_LR = 90.0    # DECISION  half the 180 mm lateral hip span. Dingo's 122 mm
                 #           span would look like a plank under a 500 mm body,
                 #           and lateral margin is free for the same reason
                 #           fore-aft margin is.

HIP_SPAN_FB = LEG_FB * 2   # DERIVED  500.0
HIP_SPAN_LR = LEG_LR * 2   # DERIVED  180.0

# TOTAL MACHINE HEIGHT, ground to the highest point, spine extended -- including
# a head. The author, 2026-08-01, resolving an ambiguity: the plan's §2.0 row this
# number descends from ("+173 mm riser -> 854 extended") was written as TOP OF
# CHEST, which made the gap look 140 mm worse than it is. A head sits above the
# chest and counts.
TARGET_TOTAL_HEIGHT = 850.0   # DECISION  total, extended, including the head

# Stance height. NOT Dingo's 250 mm: at 250 the leg sits at 98.6% of full reach
# with 3.79 mm left, and a statically stable crawl needs to shift the body
# ~25 mm laterally to put the CoM inside the support triangle. There is not
# enough reach left to do that, so 250 mm cannot crawl at all.
# 235 mm keeps the leg near-straight (cheap to hold) while leaving the headroom
# a crawl needs.
STANCE_Z = 235.0   # DECISION  see edu/ALPHA-CENTAURI-PLAN.md 1.6

# Dingo's Kinematics.py clips an over-extended IK request to 0.8*(L2+L3) and
# does NOT raise -- an unreachable command silently slams the foot ~35-50 mm
# instead of erroring. Our layer must refuse before it gets there.
LEG_EXTENSION_LIMIT_FRAC = 0.97   # DECISION  refuse commands beyond this
LEG_EXTENSION_LIMIT = LEG_REACH_MAX * LEG_EXTENSION_LIMIT_FRAC   # DERIVED

# THE FOOT IS A SPHERE, AND ITS CENTRE IS NOT THE FOOT POSITION.
# The calf swings through roughly 38.5 deg across the working envelope. On a
# FLAT pad the contact point migrates to the rim as the calf tilts -- at 20 deg
# on a 12 mm pad it lands 4.10 mm further from the knee than L3, which is more
# than the entire reach headroom at Dingo's own 250 mm stance. On a sphere
# centred ON the calf axis the contact stays exactly L3 from the knee at every
# angle. That is not a refinement, it is the difference between the IK's foot
# and the real one.
#
# So: centre the sphere at (L3 - FOOT_SPHERE_R) along the calf, and the contact
# point lands at L3. Ground level is then the IK's own foot point, with nothing
# added. Modelling the sphere centred AT the foot instead put the ground 15 mm
# low and silently made the drawn robot stand at 250 mm -- the forbidden stance.
FOOT_SPHERE_R = 15.0   # DECISION  hemisphere covers the 38.5 deg calf swing
FOOT_CENTRE_FROM_KNEE = L3_CALF - FOOT_SPHERE_R   # DERIVED  123.14


# ============================================================================
# 3. LEG SERVO -- pocket geometry. NOMINAL until one is in hand.
# ============================================================================
# FEETECH STS3250, serial bus, 12 V. Chosen because with the corrected torque
# figures it passes on CONTINUOUS rating (worst joint 11.67 kg-cm standing
# against 16 rated = 1.37x) as well as on peak (27.40 against 50 stall = 1.82x).
#
# !!! Every dimension in this block is a DATASHEET NOMINAL for a part we do not
# !!! physically have. Do NOT print a mating pocket from these. The repo's
# !!! measured ST3215 differs from its own nominal by up to 4.3 mm on height.
# VENDOR CROSS-CHECK, 2026-08-01. Pulled the checksum-verified ST3215 STEP from
# the step.parts catalog (cad/vendor/waveshare_feetech_st3215_servo.step) and
# measured its bounding box: 45.22 x 37.80 x 24.72 mm.
#
# Two of the three NOMINALs below reproduce EXACTLY (45.22, 24.72) -- the STS
# series shares a body footprint, so those are trustworthy. The third does not:
# vendor 37.80 against our 35.00, a 2.80 mm shortfall on the axis that sets pod
# height and the thigh's clevis span. The vendor solid includes the output boss
# and may include the horn, so this is not proof our 35.00 is wrong -- it is
# proof the number is UNRESOLVED and must not be printed against.
#
# Design consequence, already live: chassis.py's pod outboard face sits 34.04 mm
# clear of the leg plane. At 35.00 a hip-pitch servo interferes by ~1 mm; at
# 37.80 by ~3.8 mm. Either way the pod needs the recess the hip analysis wants.
SERVO_VENDOR_REF = "cad/vendor/waveshare_feetech_st3215_servo.step"
SERVO_VENDOR_BBOX = (45.22, 37.80, 24.72)   # VERIFIED  measured off the STEP

SERVO_MODEL = "FEETECH STS3250"
SERVO_BODY_LENGTH = 45.22     # NOMINAL  <- matches vendor ST3215 exactly
SERVO_BODY_WIDTH = 24.72      # NOMINAL  <- matches vendor ST3215 exactly
SERVO_BODY_HEIGHT = 35.0      # NOMINAL
SERVO_MASS_G = 74.5           # NOMINAL
SERVO_STALL_KGCM = 50.0       # NOMINAL  peak, at 12 V
SERVO_RATED_KGCM = 16.0       # NOMINAL  continuous -- THIS is the design number
SERVO_STALL_A = 4.2           # NOMINAL  at 12 V
SERVO_SPLINE_TEETH = 25       # NOMINAL  same family as the owned ST3215

# Clearance around the servo body in a printed pocket. Generous on purpose:
# the dimensions above are unverified, and a pocket that is 0.3 mm tight is a
# reprint while a pocket 0.3 mm loose is a shim.
SERVO_POCKET_CLEARANCE = 0.4   # DECISION

# BUS VOLTAGE LAW (2026-08-28, edu/REPLAN-2026-08-28.md 0): STS/ST bus
# servos are 12 V-MAX -- "2S or 3S lithium" per FEETECH/Waveshare. The servo
# rail is 3S li-ion from here on; the old 600 g "6S-class" pack in balance.py
# (25.2 V) can NEVER feed the servo bus. The DS3235SG arm servos are
# 8.4 V-max and get their own ~7.4 V buck rail -- they must never see the 3S
# rail directly.
SERVO_BUS_CELLS = 3         # DECISION  2x 3S 18650 swap packs, common bus
SERVO_BUS_V_MAX = SERVO_BUS_CELLS * 4.2   # DERIVED  12.6 V at full charge


# ============================================================================
# 4. CHASSIS -- printed, split, and deliberately trimmable
# ============================================================================
CHASSIS_LENGTH = HIP_SPAN_FB          # DERIVED  hip axis to hip axis
CHASSIS_WIDTH = 160.0                 # DECISION  narrower than the hip span;
                                      #           the abduction servos hang
                                      #           outboard of the body walls
CHASSIS_HEIGHT = 72.0                 # DECISION  battery + wiring depth
WALL = 3.0                            # DECISION  matches the telescopebot parts

# REPLANNED 2026-08-28 (edu/REPLAN-2026-08-28.md): printed in FOUR quarters
# for the A1 mini's 180 mm bed. H2C-era: two 250 mm halves bolted at the
# midline. Splice planes land at x = 0 and +/-125 -- away from the hip pods
# (+/-250) and the rack well -- and every joint gets a bolted splice with
# shear keys. A split body still means a crash at hour N costs one segment,
# not the whole chassis; now it also means no segment outgrows the bed.
CHASSIS_SPLIT_COUNT = 4               # DECISION  2026-08-28, was 2
CHASSIS_SEGMENT_LENGTH = CHASSIS_LENGTH / CHASSIS_SPLIT_COUNT  # DERIVED  125.0
CHASSIS_SPLICE_X = tuple(
    -CHASSIS_LENGTH / 2 + i * CHASSIS_SEGMENT_LENGTH
    for i in range(1, CHASSIS_SPLIT_COUNT)
)                                     # DERIVED  (-125.0, 0.0, 125.0); ways in
                                      # waist_rail.py segment on THESE planes
# LEGACY -- chassis.py still builds 250 mm halves against this alias; it
# migrates to CHASSIS_SEGMENT_LENGTH in the quarters rework, then this dies.
CHASSIS_HALF_LENGTH = CHASSIS_LENGTH / 2   # DERIVED  250.0 (H2C-era geometry)

# The heavy things must be MOVABLE. Static tipping margin is measured, not
# modelled (P4 puts a bathroom scale under each foot), so the battery rides a
# rail with multiple bolt positions and the CoM gets trimmed empirically
# instead of being predicted. Centring the standing CoM on the wheelbase is
# worth ~27% of knee demand -- the single highest-value free change available.
# RETIRED 2026-09-22 (chassis.py, REPLAN item 2): the trim rail is gone. The
# two 3S swap packs sit at a FIXED station (chassis.BAY_X = 190, aft) because
# the dock and the self-swap need a fixed target, and CoM trim now comes from
# the torso rail (TORSO_WALK -> TORSO_WORK sweeps the CoM 0 -> +46 mm,
# continuously). The two values stay as provenance; nothing in CAD reads them.
BATTERY_RAIL_PITCH = 15.0             # RETIRED  was: bolt positions along the rail
BATTERY_RAIL_TRAVEL = 180.0           # RETIRED  was: +/- 90 mm of CoM trim


# ============================================================================
# 5. PRINTER -- Bambu A1 mini (the ONLY printer since 2026-08-28)
# ============================================================================
# REPLANNED 2026-08-28 (edu/REPLAN-2026-08-28.md). The H2C is gone. H2C-era
# provenance, kept because it explains decisions made against it and must
# never be drawn against again: bed 330 x 320 x 325 (VERIFIED
# bambulab.com/en/h2c/specs), chamber 65 C actively heated, nozzle 350 C.
# cad/telescopebot/hardware_constants.py still names a FlashForge Guider 3
# Plus; that entry is WRONG and must be fixed there too.
PRINTER_MODEL = "Bambu A1 mini"
BED_X = 180.0    # VERIFIED  Bambu wiki/store, checked 2026-08-27
BED_Y = 180.0    # VERIFIED
BED_Z = 180.0    # VERIFIED
BED_DIAGONAL_MAX = 245.0   # NOMINAL  narrow parts laid diagonally reach ~245;
                           #          leave margin, never design AT this number
BED_MAX_C = 80.0     # VERIFIED
NOZZLE_MAX_C = 300.0   # VERIFIED  stock hotend; hardened-steel 0.4 for CF
CHAMBER_MAX_C = None   # OPEN FRAME -- no chamber. Bambu explicitly does not
                       # recommend ABS/ASA/PC/PA/PET-CF on the A1 series.

# The H2C-era logic ("heated chamber unlocks PC / PA-CF") is void on an open
# frame. PETG-CF is the A1-mini-printable structural pick: HDT ~68 C, Vicat
# ~85 C, ~2x PETG notched impact, low-warp formulation; needs the
# hardened-steel 0.4 hotend (~$14 swap unit). Second thermal defense the H2C
# plan never had: bus servos have a WRITABLE over-temperature cutoff (stock
# ~70 C) -- set it to ~55-60 C so the servo protects itself before any
# printed pocket creeps. PLA only for jigs and fit tests (creep ceiling
# ~35-40 C under sustained load).
MATERIAL_STRUCTURAL = "PETG-CF"       # DECISION  2026-08-28  servo pockets,
                                      #           knee brackets
MATERIAL_BULK = "PETG"                # DECISION  shells, covers, non-load parts
MATERIAL_GRIP = "TPU"                 # DECISION  95A, foot treads. EXTERNAL
                                      #           spool only (AMS lite cannot
                                      #           feed TPU); now a SEPARATE
                                      #           part -- the A1 mini has no
                                      #           second nozzle to co-print


# ============================================================================
# 6. SELF-CHECKS -- these run at import, so a bad edit fails loudly
# ============================================================================
def extension_at(stance_z, lateral_shift=0.0, fore_aft=0.0):
    """In-plane hip-to-foot distance, in mm. THE reach function -- nothing else
    in this project may restate it.

    At zero shift this is just stance + L1_VERTICAL: the hip-pitch axis sits
    ABOVE the body datum, so with the foot on the ground the leg spans MORE than
    the body stands tall. Hence +, not -. Getting that sign backwards flatters
    the reach budget and halved every knee-torque estimate in this project.

    `lateral_shift` is how far the body moves sideways to put the CoM inside a
    three-foot support triangle; `fore_aft` is the stride half-amplitude. The
    foot stays planted while the body moves, so DO NOT model either as a plain
    hypot against the vertical -- that is wrong, and wrong in the FLATTERING
    direction. The leg plane sits at a CONSTANT perpendicular offset L1_LATERAL
    from the abduction axis (Kinematics.py's a_2 = asin(sin(phi)*L1/len_A)
    constraint), so a lateral shift is absorbed by swinging the whole plane, and
    only what is left over after that costs reach.

    Cross-checked against a faithful port of the donor's own IK: agreement is
    1.6e-7 mm, which is the residual between L1 and hypot(L1_LATERAL,
    L1_VERTICAL). The out-of-plane residual is 0.000 at every shift, so the leg
    plane really does pass through the foot.

        shift  0.0 mm -> 249.300 mm (92.97% of reach)
        shift 25.5 mm -> 255.971 mm (95.46%)   CoM centred first
        shift 44.4 mm -> 262.495 mm (97.90%)   CoM not centred -- FAILS the guard
    """
    y = L1_LATERAL + lateral_shift
    return math.hypot(fore_aft,
                      L1_VERTICAL + math.sqrt(y * y + stance_z * stance_z
                                              - L1_LATERAL * L1_LATERAL))


# How far the body must move sideways to stand on three feet. Two values,
# because whether the CoM is centred first is what decides if the robot can
# step at all -- see the CRAWL assertion below.
CRAWL_SHIFT_CENTRED = 25.5     # DERIVED  CoM on the fore-aft mid-line
CRAWL_SHIFT_UNCENTRED = 44.4   # DERIVED  CoM where it lands if nothing is trimmed

# Swing-phase foot lift, read out of the donor's own gait config:
# DingoQuadruped Config.py `self.z_clearance = 0.07` (metres). This is the
# number that sets how far the knee folds mid-swing, and therefore the far end
# of the hip-pitch working range the hip module must sweep against.
DONOR_Z_CLEARANCE = 70.0       # VERIFIED  Config.py self.z_clearance * 1000


# ============================================================================
# 7. HIP MODULE -- the L1 link, and the pod recess it forces
# ============================================================================
# ARCHITECTURE (settled 2026-08-01, hip_module.py carries the full WHY):
# the hip-pitch servo lives in the THIGH's hip end, output boss ON the
# hip-pitch axis, FACING OUTBOARD -- the locked decision. The hip module is
# the mating FORK: two lugs in the calf's own lug pattern straddling the thigh
# (horn adapter in the outboard lug, 608ZZ in the inboard lug), an over-bridge
# clearing the thigh's swept envelope, and a root boss on the abduction axis
# that clamps to the abduction servo horn.
#
# THE POD RECESS. The fork's INBOARD lug hangs LUG_CLEAR + LUG_T inboard of
# the thigh's inboard cheek, and the whole fork rolls about the abduction axis
# with the leg. The pod's outboard face currently sits at
# HIP_POD_FACE_NOMINAL = 105.56, and the swept lug comes as close as
# 107.55 mm (h=35.0) / 106.16 mm (h=37.8) -- inside the HIP_POD_GAP running
# clearance either way. So the pod face must move inboard by HIP_STACK.
#
# Every term, outboard of the leg plane centre going inboard:
#   SEC_Y(h)/2      half the thigh box: servo half-height + pocket clearance
#                   half + one wall (thigh.py restates the same sum; the
#                   build-time assert in hip_module.py keeps them equal)
#   HIP_LUG_CLEAR   running gap between thigh cheek and fork lug (calf.py's
#                   own 0.5 mm convention, asserted equal at build)
#   HIP_LUG_T       the lug: carries the 608ZZ / horn-adapter seat, 22 x 6,
#                   straight from joint_parts.py (asserted equal at build)
#   sweep term      the lug's inboard excursion rolling +/-HIP_ABDUCTION_
#                   RANGE_DEG about the abduction axis: worst corner sits
#                   dy = lug_face - LEG_LR inboard and dz = L1_VERTICAL +
#                   HIP_LUG_R above the axis, so it swings in by
#                   dy*(1-cos t) + dz*sin t. CONSERVATIVE: the true corner
#                   leaves the pod's z-band as it rolls; the swept-solid
#                   asserts in hip_module.py are the exact gate.
#   HIP_POD_GAP     printed-part running clearance to the recessed face
#
# SERVO_BODY_HEIGHT is UNRESOLVED (35.00 nominal vs 37.80 vendor STEP), so
# everything here is a FUNCTION of h, HIP_STACK is evaluated at the WORST
# candidate, and _check() gates BOTH candidates -- only the print waits on
# the caliper, not the design.

SERVO_BODY_HEIGHT_CANDIDATES = (35.0, 37.8)   # NOMINAL vs vendor-STEP reading

LEG_PLANE_Y = LEG_LR + L1_LATERAL   # DERIVED  139.60, thigh centre plane

# Fork lug geometry. DECISION values that MIRROR calf.py/joint_parts.py; the
# constants file cannot import those modules (they import this one), so
# hip_module.py asserts equality at build time instead -- restatement is
# guarded, not trusted.
HIP_LUG_T = 6.0        # DECISION  == calf.LUG_T, seats a 608ZZ (22 x 7 - lip)
HIP_LUG_R = 19.0       # DECISION  == calf.LUG_R, lug outline about the axis
HIP_LUG_CLEAR = 0.5    # DECISION  == (calf.LUG_GAP - thigh.SEC_Y) / 2
HIP_POD_GAP = 2.0      # DECISION  moving-fork to static-pod running clearance

# Working ranges the swept asserts protect. NOT guesses:
#  * abduction: the crawl's own body shift (+/-CRAWL_SHIFT_CENTRED) needs
#    +/-6.27 deg through crawl_abduction_deg() below; 8.0 adds ~27% margin.
#  * hip pitch: the crawl posing envelope -- foot fore-aft +/-CRAWL_STRIDE_
#    HALF, lift 0..DONOR_Z_CLEARANCE -- spans +15.8..+57.5 deg aft of
#    vertical (hip_pitch_deg below); (10, 60) brackets it with margin.
HIP_ABDUCTION_RANGE_DEG = 8.0          # DECISION  see derivation above
HIP_PITCH_RANGE_DEG = (10.0, 60.0)     # DECISION  aft of vertical, see above

# The pod's outboard face before any recess: abduction pocket half-width plus
# one pod wall. chassis.py's POD_WALL is the same 3.0 as WALL; chassis.py now
# imports HIP_POD_FACE_Y instead of re-deriving this.
HIP_POD_FACE_NOMINAL = LEG_LR + (SERVO_BODY_WIDTH + SERVO_POCKET_CLEARANCE) / 2 + WALL
# DERIVED  105.56


def crawl_abduction_deg(shift, stance_z=None):
    """Abduction angle that absorbs a lateral body shift, deg.

    The leg plane rides at a constant perpendicular offset L1_LATERAL from the
    abduction axis (the same constraint extension_at() documents), so the roll
    needed for a shift s at stance z is atan2(L1_LATERAL + s, z) minus the
    plane-offset angle asin(L1_LATERAL / hypot). Zero at zero shift -- the
    donor's own default stance solves theta_1 = 0.000 exactly.
    """
    z = STANCE_Z if stance_z is None else stance_z
    y = L1_LATERAL + shift
    return math.degrees(math.atan2(y, z) - math.asin(L1_LATERAL / math.hypot(y, z)))


def hip_pitch_deg(foot_x, lift=0.0, stance_z=None):
    """Thigh angle aft of vertical for a foot at fore-aft offset / lift, deg.

    Same law-of-cosines pose solve as assembly.solve_leg, with the foot moved
    fore-aft and lifted. Used only to DERIVE the working-range bracket; the
    per-pose solve in assembly.py remains the posing authority.
    """
    z = STANCE_Z if stance_z is None else stance_z
    drop = z + L1_VERTICAL - lift
    ext = math.hypot(foot_x, drop)
    ck = (L2_THIGH**2 + L3_CALF**2 - ext**2) / (2 * L2_THIGH * L3_CALF)
    knee_int = math.acos(max(-1.0, min(1.0, ck)))
    sa = L3_CALF * math.sin(knee_int) / ext
    alpha = math.degrees(math.asin(max(-1.0, min(1.0, sa))))
    return alpha - math.degrees(math.atan2(foot_x, drop))


def hip_thigh_sec_y(h):
    """Thigh lateral box width at servo height h -- thigh.py's SEC_Y."""
    return h + SERVO_POCKET_CLEARANCE + 2 * WALL


def hip_lug_inner_y(h):
    """Robot-Y of the fork's inboard lug INNER (pod-facing) face."""
    return LEG_PLANE_Y - hip_thigh_sec_y(h) / 2 - HIP_LUG_CLEAR - HIP_LUG_T


def hip_lug_swept_min_y(h, roll_deg=None):
    """Worst-case (most inboard) Y any lug corner reaches over the abduction
    roll. Conservative scalar -- the exact gate is the swept-solid assert."""
    t = math.radians(HIP_ABDUCTION_RANGE_DEG if roll_deg is None else roll_deg)
    dy = hip_lug_inner_y(h) - LEG_LR
    dz = L1_VERTICAL + HIP_LUG_R
    return LEG_LR + dy * math.cos(t) - dz * math.sin(t)


def hip_stack_at(h):
    """Pod recess needed at servo height h: how far HIP_POD_FACE_NOMINAL
    stands inside the swept lug's clearance envelope."""
    return max(0.0, HIP_POD_FACE_NOMINAL - (hip_lug_swept_min_y(h) - HIP_POD_GAP))


# THE recess. Evaluated at the WORST candidate height so the chassis geometry
# is safe whichever way the caliper lands; the per-height gates run in
# _check() below.  h = 35.0 -> 0.01 mm, h = 37.8 -> 1.40 mm.
HIP_STACK = max(hip_stack_at(h) for h in SERVO_BODY_HEIGHT_CANDIDATES)  # DERIVED
HIP_POD_FACE_Y = HIP_POD_FACE_NOMINAL - HIP_STACK                       # DERIVED

# RESOLVED 2026-09-23 (design-log section 4 decision 7, the author: bolt-on pods).
# Found 2026-09-22 by chassis.py's measured bed gate: with the pods printed
# in, the outer segment was 125 x 208.3 x 72 -- no A1 mini orientation. The
# pods are now a separate part (chassis.abduction_pod, x4, one STL), bolted
# into a socket in the side wall, so the PRINTED outer segment is the body,
# CHASSIS_WIDTH wide, and the segment gate in _check() below is the real
# pre-check again. The bolted span over the pods is unchanged (it is the
# hip geometry) and is kept as CHASSIS_OUTER_ASSEMBLED_WIDTH; chassis.py
# gates the built parts' measured print-pose boxes, and asserts the bolted
# body + pods envelope equals the old fused one.
CHASSIS_OUTER_SEGMENT_WIDTH = CHASSIS_WIDTH        # DERIVED  160 -- fits
CHASSIS_OUTER_ASSEMBLED_WIDTH = 2 * HIP_POD_FACE_Y  # DERIVED  208.3, pods bolted

# What is left of the pod's outboard wall after the recess. The abduction
# pocket cannot move (its servo is centred on the abduction axis), so the
# recess comes entirely out of the 3.0 mm wall.
HIP_POD_WALL_MIN = 1.2   # DECISION  3 perimeters at the 0.4 nozzle

# Fore-aft half-amplitude of one crawl step. PROVISIONAL -- this is the number
# that sets the stance ceiling and nobody has measured it on this robot yet.
# Dingo's stock trot is far larger; a crawl is much gentler.
CRAWL_STRIDE_HALF = 25.0       # NOMINAL  see open question in §1.6


def _check():
    # L1 is a DIAGONAL. If this ever fails, someone has "fixed" one of the two
    # components without the other, and the leg geometry is silently wrong.
    assert abs(math.hypot(L1_LATERAL, L1_VERTICAL) - L1_HIP_OFFSET) < 1e-5, (
        f"L1 decomposition broken: hypot({L1_LATERAL}, {L1_VERTICAL}) = "
        f"{math.hypot(L1_LATERAL, L1_VERTICAL)} != L1 {L1_HIP_OFFSET}"
    )

    # The legs must actually reach the commanded stance. Call extension_at()
    # rather than restating its formula: the previous version of this check
    # restated it with the sign FLIPPED, so the assertion written to catch the
    # 250 mm stance would in fact have passed it (235.70 < 260.09), while the
    # true extension 264.30 exceeds the limit. The named failure mode reappeared
    # inside the guard written to catch it. Do not inline this arithmetic again.
    in_plane = extension_at(STANCE_Z)
    assert in_plane < LEG_EXTENSION_LIMIT, (
        f"stance {STANCE_Z} mm needs {in_plane:.2f} mm of in-plane leg "
        f"extension, past the {LEG_EXTENSION_LIMIT:.2f} mm limit "
        f"({LEG_REACH_MAX:.2f} mm max reach). Lower STANCE_Z."
    )

    # THE BINDING CHECK. A guard that only looks at STANDING will happily pass a
    # robot that cannot take a step -- standing at 235 mm uses 93.0% of reach and
    # looks roomy, while the pose it must actually hold mid-crawl uses 95.8%.
    # This assertion is what killed the proposal to raise the stance to 240 mm:
    # 240 stands fine and then needs 97.3% to shift its body, over the limit.
    #
    #   ceiling, 25.5 mm shift alone          : 239.24 mm
    #   ceiling, 25.5 mm shift + 25 mm stride : 238.00 mm
    #
    # So 235 has about 3 mm of headroom, not the 8 mm a standing-only check
    # implies. Centring the CoM is likewise a PRECONDITION, not an optimisation:
    # the uncentred 44.4 mm shift needs 97.9% and fails outright.
    crawl = extension_at(STANCE_Z, CRAWL_SHIFT_CENTRED, CRAWL_STRIDE_HALF)
    assert crawl < LEG_EXTENSION_LIMIT, (
        f"stance {STANCE_Z} mm cannot crawl: a {CRAWL_SHIFT_CENTRED} mm body "
        f"shift with a {CRAWL_STRIDE_HALF} mm stride needs {crawl:.2f} mm "
        f"({100 * crawl / LEG_REACH_MAX:.1f}% of reach), past the "
        f"{LEG_EXTENSION_LIMIT:.2f} mm limit. Lower STANCE_Z."
    )

    # Each printed chassis SEGMENT must fit the bed in some orientation.
    # (The legacy 250 mm half does NOT fit the A1 mini -- that is exactly why
    # CHASSIS_SPLIT_COUNT went to 4. Gate the segment, not the alias.)
    seg = sorted([CHASSIS_SEGMENT_LENGTH, CHASSIS_WIDTH, CHASSIS_HEIGHT])
    bed = sorted([BED_X, BED_Y, BED_Z])
    assert all(s <= b for s, b in zip(seg, bed)), (
        f"chassis segment {seg} does not fit bed {bed}"
    )
    # ...and the outer segment, which since the 2026-09-23 bolt-on pods is
    # the body alone (see CHASSIS_OUTER_SEGMENT_WIDTH). Asserted now; the
    # measured print-pose gate is still chassis.py's.
    _outer = sorted([CHASSIS_SEGMENT_LENGTH, CHASSIS_OUTER_SEGMENT_WIDTH,
                     CHASSIS_HEIGHT])
    assert all(s <= b for s, b in zip(_outer, bed)), (
        f"chassis outer segment {_outer} does not fit bed {bed}")
    # Splice planes must stay clear of the hip pods at the chassis ends.
    assert all(abs(abs(x) - LEG_FB) > 50.0 for x in CHASSIS_SPLICE_X), (
        f"a chassis splice plane in {CHASSIS_SPLICE_X} lands within 50 mm of "
        f"a hip pod station (+/-{LEG_FB})"
    )

    # Hips must sit outboard of the body walls or the servos intersect it.
    assert LEG_LR >= CHASSIS_WIDTH / 2, (
        f"LEG_LR {LEG_LR} is inboard of the chassis wall "
        f"({CHASSIS_WIDTH / 2}); abduction servos would clash with the body"
    )

    assert 0.0 < LEG_EXTENSION_LIMIT_FRAC < 1.0

    # ---- HIP MODULE gates, at BOTH candidate servo heights ------------------
    # SERVO_BODY_HEIGHT is unresolved (35.00 vs 37.80). The design must hold
    # at either resolution so that only the PRINT waits on the caliper. If one
    # of these ever fails, the hip geometry -- not the constant -- is wrong.
    assert SERVO_BODY_HEIGHT in SERVO_BODY_HEIGHT_CANDIDATES, (
        f"SERVO_BODY_HEIGHT {SERVO_BODY_HEIGHT} is not one of the tracked "
        f"candidates {SERVO_BODY_HEIGHT_CANDIDATES}; if the caliper resolved "
        f"it, update the candidates tuple to the single measured value"
    )
    for h in SERVO_BODY_HEIGHT_CANDIDATES:
        # the recessed pod face must clear the swept lug by the running gap
        clear = hip_lug_swept_min_y(h) - HIP_POD_FACE_Y
        assert clear >= HIP_POD_GAP - 1e-9, (
            f"hip fork lug at servo height {h}: swept lug reaches "
            f"{hip_lug_swept_min_y(h):.2f} mm, recessed pod face "
            f"{HIP_POD_FACE_Y:.2f} -- {clear:.2f} mm gap < {HIP_POD_GAP}"
        )
        # the recess must leave a printable outboard pod wall
        wall_left = WALL - hip_stack_at(h)
        assert wall_left >= HIP_POD_WALL_MIN, (
            f"pod recess at servo height {h} leaves a {wall_left:.2f} mm "
            f"outboard wall, under the {HIP_POD_WALL_MIN} printable floor"
        )
    # the declared working ranges must actually cover the crawl's own demands
    need_ab = max(abs(crawl_abduction_deg(CRAWL_SHIFT_CENTRED)),
                  abs(crawl_abduction_deg(-CRAWL_SHIFT_CENTRED)))
    assert HIP_ABDUCTION_RANGE_DEG >= need_ab, (
        f"abduction range {HIP_ABDUCTION_RANGE_DEG} deg < crawl demand "
        f"{need_ab:.2f} deg"
    )
    lo, hi = HIP_PITCH_RANGE_DEG
    for fx in (-CRAWL_STRIDE_HALF, 0.0, CRAWL_STRIDE_HALF):
        for lift in (0.0, DONOR_Z_CLEARANCE / 2, DONOR_Z_CLEARANCE):
            p = hip_pitch_deg(fx, lift)
            assert lo <= p <= hi, (
                f"hip pitch range {HIP_PITCH_RANGE_DEG} misses crawl pose "
                f"foot_x={fx} lift={lift}: {p:.2f} deg"
            )


_check()


def leg_extension_frac(stance_z):
    """Fraction of maximum reach used at a given stance height. Above ~0.97 a
    crawl gait cannot shift the body far enough to stay statically stable."""
    return extension_at(stance_z) / LEG_REACH_MAX


if __name__ == "__main__":
    print(f"Alpha Centauri interface constants -- all checks passed\n")
    print(f"  legs (Dingo, k=1.0)   L1 {L1_HIP_OFFSET:.2f}  L2 {L2_THIGH:.1f}  "
          f"L3 {L3_CALF:.2f} mm   max reach {LEG_REACH_MAX:.2f}")
    print(f"  hip span              {HIP_SPAN_FB:.0f} x {HIP_SPAN_LR:.0f} mm "
          f"(Dingo: {DINGO_LEG_FB * 2:.0f} x {DINGO_LEG_LR * 2:.0f})")
    print(f"  stance                {STANCE_Z:.0f} mm  -> in-plane "
          f"{extension_at(STANCE_Z):.2f} mm = {leg_extension_frac(STANCE_Z) * 100:.1f}% of reach")
    print(f"  Dingo's 250 mm would be {leg_extension_frac(DINGO_STANCE_Z) * 100:.1f}% "
          f"-- too extended to crawl")
    print(f"  chassis               {CHASSIS_LENGTH:.0f} x {CHASSIS_WIDTH:.0f} x "
          f"{CHASSIS_HEIGHT:.0f} mm, {CHASSIS_SPLIT_COUNT} segments of "
          f"{CHASSIS_SEGMENT_LENGTH:.0f} mm, splices at {CHASSIS_SPLICE_X}")
    print(f"  printer               {PRINTER_MODEL}  {BED_X:.0f} x {BED_Y:.0f} x {BED_Z:.0f}")
    print(f"  outer segment         {CHASSIS_OUTER_SEGMENT_WIDTH:.1f} mm wide printed "
          f"(pods bolt on); {CHASSIS_OUTER_ASSEMBLED_WIDTH:.1f} mm over the bolted pods")
