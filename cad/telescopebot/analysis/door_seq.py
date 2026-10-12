"""Alpha Centauri -- door sequence feasibility arithmetic.

Every number printed here is derived in-line. Sources for externally-cited
values are named in the comment above each constant. Run with:
    edu/.cadenv/bin/python cad/telescopebot/analysis/door_seq.py
"""
import math

G = 9.81
KGCM_PER_NM = 1.0 / 0.0980665   # 1 N.m = 10.1972 kg.cm
def nm2kgcm(t): return t * KGCM_PER_NM
def kgcm2nm(t): return t / KGCM_PER_NM

L = []
def p(s=""): L.append(s); print(s)
def h(s): p(); p("=" * 78); p(s); p("=" * 78)

# ============================================================ MASS BUDGET
h("0. MASS BUDGET -- RE-DERIVED FOR SHORT ARMS")

# Old torso, from the workstream brief (2-full-arm design)
old_torso = dict(chest_print=341, waist_mast_print=340, jetson_orin=176,
                 realsense_d435=72, arms_2x_soarm101=1408,
                 spine_hardware=358, misc=137)
OLD_TORSO = sum(old_torso.values())
p(f"OLD torso items: {old_torso}")
p(f"OLD torso total = {OLD_TORSO} g  (brief says 2.83 kg -> "
  f"{'MATCH' if abs(OLD_TORSO-2830) < 15 else 'MISMATCH'})")

OLD_TOTAL = 5780.0          # brief: total robot at k=1.0
BASE = OLD_TOTAL - OLD_TORSO
p(f"=> quadruped base+battery+legs = {OLD_TOTAL} - {OLD_TORSO} = {BASE:.0f} g")

# Independent cross-check of the base mass (built up, not back-solved)
base_check = dict(sts3250_x12=12*74.5, printed_legs_4x=4*180, body_print=500,
                  lipo_3s_5000=400, bec_wiring=50, fasteners_bus=250)
p(f"  cross-check build-up: {base_check}")
p(f"  cross-check total = {sum(base_check.values()):.0f} g "
  f"(vs back-solved {BASE:.0f} g, delta {sum(base_check.values())-BASE:+.0f} g)")

# SHORT ARM derivation
p()
p("SHORT ARM (target ~30 cm reach, 5 DOF, mostly owned servos):")
# servo masses from the owned-inventory table in the brief
arm_servos = dict(shoulder_pitch_MG996R=55, shoulder_roll_MG996R=55,
                  elbow_MG996R=55, wrist_pitch_MG996R=55, gripper_MG90S=13.4)
ARM_SERVO = sum(arm_servos.values())
p(f"  servos {arm_servos} = {ARM_SERVO:.1f} g")
# SO-ARM101 non-servo mass: 704 g total - 6x STS3215 @ 60 g
SOARM_NONSERVO = 704 - 6*60
p(f"  SO-ARM101 non-servo mass = 704 - 6x60 = {SOARM_NONSERVO} g for 6 joints / 44 cm")
# scale: 5 joint housings, links at 30/44
housings = 5 * (SOARM_NONSERVO * 0.70 / 6)     # ~70% of non-servo mass is housings
links    = (SOARM_NONSERVO * 0.30) * (30.0/44.0)
ARM_PRINT_NOM = housings + links
p(f"  housings 5 x (0.70*{SOARM_NONSERVO}/6) = {housings:.0f} g")
p(f"  links    0.30*{SOARM_NONSERVO} * 30/44  = {links:.0f} g")
p(f"  => print+fasteners nominal {ARM_PRINT_NOM:.0f} g")
ARM_NOM = ARM_SERVO + ARM_PRINT_NOM
ARM_LO, ARM_HI = ARM_SERVO + 165, ARM_SERVO + 285
p(f"  SHORT ARM: nominal {ARM_NOM:.0f} g   range {ARM_LO:.0f}-{ARM_HI:.0f} g")
p(f"  vs SO-ARM101 704 g -> saving {704-ARM_NOM:.0f} g/arm, {2*(704-ARM_NOM):.0f} g/pair")

# height recovery: 14 cm of reach lost (44 -> 30 cm)
p()
p("HEIGHT RECOVERY for the 14 cm of reach lost (decision #6):")
riser_vol = 2*(150+120) * 3.0 * 140            # mm^3, 3 mm walls, 140 mm tall box
riser_g   = riser_vol/1000.0 * 1.27 * 0.95
p(f"  option A printed riser 150x120x140, 3 mm walls: {riser_vol/1000:.0f} cm^3 "
  f"x 1.27 g/cm^3 x 0.95 = {riser_g:.0f} g")
rod_g = 2 * 0.14 * 320                          # 2 rods, 0.14 m, M8 thread ~320 g/m
p(f"  option B longer M8 rods: 2 x 0.14 m x 320 g/m = {rod_g:.0f} g  <-- 3.5x lighter")
HEIGHT_RECOVERY = 150.0                         # rods + taller nut towers + guides
p(f"  budgeted (rods + taller towers + guides): {HEIGHT_RECOVERY:.0f} g")

new_torso = dict(old_torso)
new_torso['arms_2x_soarm101'] = 2*ARM_NOM
new_torso['height_recovery'] = HEIGHT_RECOVERY
NEW_TORSO = sum(new_torso.values())
p()
p(f"NEW torso = {NEW_TORSO:.0f} g  (was {OLD_TORSO} g, delta {NEW_TORSO-OLD_TORSO:+.0f} g)")
M_TOT = (NEW_TORSO + BASE)/1000.0
W = M_TOT * G
p(f"NEW TOTAL ROBOT = {NEW_TORSO:.0f} + {BASE:.0f} = {NEW_TORSO+BASE:.0f} g = {M_TOT:.2f} kg")
p(f"WEIGHT W = {M_TOT:.3f} kg x 9.81 = {W:.1f} N")
p(f"(brief expected 500-900 g removed; ACTUAL net torso saving is "
  f"{OLD_TORSO-NEW_TORSO:.0f} g because height recovery adds {HEIGHT_RECOVERY:.0f} g back)")

# ============================================================ TIPPING MODEL
h("0b. TIPPING BUDGET -- RESCALED FROM THE BRIEF'S k=1.0 MARGINS")
# Brief's margins were derived at 5.78 kg. x measured forward-positive from the
# FRONT-FOOT contact line; negative = CG behind the line = stable.
x_both_old   = -0.006     # both arms forward, no crouch
x_crouch_old = -0.057     # + ~13 deg aft pitch
x_onearm_old = -0.034     # one arm reaching, other stowed, no crouch
p(f"brief @5.78 kg: both-fwd {x_both_old*1000:.0f} mm, crouch {x_crouch_old*1000:.0f} mm,"
  f" one-arm {x_onearm_old*1000:.0f} mm")
p(f"  brief's '3.3 N.m budget' reconciles as 5.78*9.81*0.057 = "
  f"{5.78*G*0.057:.2f} N.m  -> it is the CROUCHED case. CONFIRMED.")

X_ARM = +0.070      # arm CG when extended: shoulder 50 mm behind front feet + 120 mm out
X_MAST = -0.050     # mast/rod line, over the front third
dm_arm = (2*704 - 2*ARM_NOM)/1000.0
mom_old = 5.780 * x_both_old
mom_new = mom_old - dm_arm*X_ARM + (HEIGHT_RECOVERY/1000.0)*X_MAST
x_both = mom_new / M_TOT
p()
p(f"remove {dm_arm*1000:.0f} g of arm at x=+{X_ARM*1000:.0f} mm, add "
  f"{HEIGHT_RECOVERY:.0f} g at x={X_MAST*1000:.0f} mm:")
p(f"  moment {5.780}*{x_both_old} = {mom_old:.5f} kg.m")
p(f"  -> {mom_new:.5f} kg.m / {M_TOT:.3f} kg = x_both = {x_both*1000:.1f} mm")

d_crouch = x_crouch_old - x_both_old                       # -51 mm
scale_1arm = (ARM_NOM/704.0) * (5.780/M_TOT)
d_onearm = (x_onearm_old - x_both_old) * scale_1arm
x_crouch  = x_both + d_crouch
x_onearm  = x_both + d_onearm
x_1a_cr   = x_both + d_onearm + d_crouch
p(f"  crouch shift {d_crouch*1000:.0f} mm; one-arm shift {d_onearm*1000:.1f} mm "
  f"(scaled by {scale_1arm:.3f})")

CASES = {
    "both arms fwd, no crouch": x_both,
    "one arm fwd, no crouch":   x_onearm,
    "both arms fwd + crouch":   x_crouch,
    "one arm fwd + crouch":     x_1a_cr,
}
p()
p(f"{'stance':<28}{'margin mm':>11}{'budget N.m':>13}")
BUDGET = {}
for k, v in CASES.items():
    BUDGET[k] = W * abs(v)
    p(f"{k:<28}{abs(v)*1000:>11.1f}{BUDGET[k]:>13.2f}")
B_WORK = BUDGET["one arm fwd + crouch"]      # the door-task stance
p(f"\nWORKING TIPPING BUDGET (door stance = one arm fwd + crouch) = {B_WORK:.2f} N.m")

# ============================================================ (a) LEVER TURN
h("(a) LEVER TURN")
T_CODE = 28 * 0.1129848        # 28 in-lbf, ANSI/BHMA A156.2 + ICC A117.1 (2017) max
p(f"code ceiling  ANSI/BHMA A156.2 / ICC A117.1: 28 in-lbf = {T_CODE:.3f} N.m")
p( "               ICC A117.1 states the same as 315 N.cm = 3.15 N.m -- agrees")
p( "ADA 309.4 (via 404.2.7): operable parts <= 5 lbf = 22.2 N")
LEVERS = {"light residential (est, UNVERIFIED)": 0.8,
          "typical residential (est, UNVERIFIED)": 1.5,
          "stiff/worn (est, UNVERIFIED)": 2.5,
          "ANSI/ICC code MAXIMUM": T_CODE}
L_TIP, L_MID = 0.110, 0.070    # m from spindle axis: lever tip vs mid-lever
p()
p(f"{'lever':<38}{'T N.m':>8}{'F@110mm':>10}{'F@70mm':>9}")
for k, t in LEVERS.items():
    p(f"{k:<38}{t:>8.2f}{t/L_TIP:>10.1f}{t/L_MID:>9.1f}")
F_LEV_CODE = T_CODE / L_TIP
p(f"\n=> worst case at the TIP: {F_LEV_CODE:.1f} N downward")
p(f"   pressing at mid-lever instead costs {T_CODE/L_MID - F_LEV_CODE:+.1f} N "
  f"({(L_TIP/L_MID-1)*100:.0f}% more). DESIGN DEMAND: contact the lever TIP.")

# Can the ARM apply it by shoulder torque?
p()
p("CAN A ~450 g SHORT ARM PUSH IT WITH SHOULDER TORQUE?")
REACH = 0.300
p(f"  shoulder torque needed = F x reach = {F_LEV_CODE:.1f} N x {REACH} m "
  f"= {F_LEV_CODE*REACH:.2f} N.m = {nm2kgcm(F_LEV_CODE*REACH):.0f} kg.cm")
SERVOS = {"MG996R (owned x22)": 10, "SCS15 (owned x4)": 17,
          "STS3215 (owned x1)": 30, "STS3250 (leg servo)": 50,
          "DS5160 (owned x2)": 60}
need_kgcm = nm2kgcm(F_LEV_CODE*REACH)
for k, v in SERVOS.items():
    p(f"    {k:<24}{v:>4} kg.cm stall -> {v/need_kgcm:>5.2f}x of requirement "
      f"{'PASS' if v/need_kgcm >= 1.5 else 'FAIL'}")
p("  VERDICT: NO servo in the plausible set passes, let alone at 1.5x.")
p("  => the arm must be a RIGID STRUT against a printed hard stop; the force")
p("     comes from spine descent or a body-height drop, not from shoulder torque.")

# spine as the force source
p()
p("SPINE AS THE FORCE SOURCE (M8x1.25, FS5103R ~3 kg.cm each):")
pitch, dm8, mu_s = 0.00125, 0.007188, 0.15
lam = math.atan(pitch/(math.pi*dm8)); phi = math.atan(mu_s)
eta = math.tan(lam)/math.tan(lam+phi)
T_FS = kgcm2nm(3.0)
F_screw = 2*math.pi*T_FS*eta/pitch
p(f"  lead angle lam = atan({pitch*1000} / (pi*{dm8*1000:.3f})) = {math.degrees(lam):.2f} deg")
p(f"  friction angle phi = atan({mu_s}) = {math.degrees(phi):.2f} deg -> "
  f"self-locking ({math.degrees(lam):.2f} < {math.degrees(phi):.2f}) CONFIRMED")
p(f"  efficiency eta = tan(lam)/tan(lam+phi) = {eta:.3f}")
p(f"  axial force per screw = 2*pi*T*eta/p = 2*pi*{T_FS:.3f}*{eta:.3f}/{pitch} "
  f"= {F_screw:.0f} N; two screws = {2*F_screw:.0f} N")
p(f"  => spine can source {2*F_screw:.0f} N, needs {F_LEV_CODE:.1f} N. "
  f"Margin {2*F_screw/F_LEV_CODE:.0f}x. NOT the constraint.")
p(f"  reverse check: to hold {F_LEV_CODE:.1f} N each servo needs "
  f"{nm2kgcm(F_LEV_CODE/2*pitch/(2*math.pi*eta)):.3f} kg.cm of 3.0 available.")

# reaction moment on the robot
p()
p("REACTION MOMENT ON THE ROBOT (press down at the lever):")
HANDLE_PROJ = 0.065     # lever projects this far from the door face toward the robot
for standoff in (0.150, 0.185, 0.250):
    d_f = standoff - HANDLE_PROJ
    p(f"  front feet {standoff*1000:.0f} mm from the door face -> press point "
      f"{d_f*1000:.0f} mm FORWARD of the front-foot line")
    for k, t in LEVERS.items():
        Fd = t/L_TIP; M = Fd*d_f
        p(f"     {k:<38} F={Fd:5.1f} N  M_tip={M:5.2f} N.m  vs budget "
          f"{B_WORK:.2f} -> {'PASS' if M <= B_WORK/1.5 else ('MARGINAL' if M <= B_WORK else 'TIPS')}")
D_F = 0.185 - HANDLE_PROJ
T_LEV_MAX = B_WORK/D_F*L_TIP
p(f"\n  at the 185 mm standoff (d_f={D_F*1000:.0f} mm): break-even lever torque")
p(f"    T_max = budget/d_f*L_tip = {B_WORK:.2f}/{D_F:.3f}*{L_TIP} = {T_LEV_MAX:.2f} N.m")
p(f"    with 1.5x margin: {T_LEV_MAX/1.5:.2f} N.m")
p(f"    => the code ceiling {T_CODE:.2f} N.m TIPS THE ROBOT at this standoff.")

# what the press does to the front knees
p()
p("FRONT-KNEE LOAD DURING THE PRESS:")
WB = 0.223      # Dingo hip footprint fore-aft = stance wheelbase, k=1.0
L3 = 0.1381     # Dingo shank
Fd = F_LEV_CODE
R_front_static = W * (WB - abs(x_1a_cr)) / WB
R_front_extra  = Fd * (D_F + WB)/WB
R_rear_static  = W - R_front_static
R_rear_delta   = R_front_extra - Fd
p(f"  static (one-arm+crouch, CG {abs(x_1a_cr)*1000:.1f} mm behind front feet):")
p(f"    R_front = W*(WB-|x|)/WB = {W:.1f}*({WB}-{abs(x_1a_cr):.4f})/{WB} = {R_front_static:.1f} N")
p(f"    R_rear  = {R_rear_static:.1f} N")
p(f"  press of {Fd:.1f} N at {D_F*1000:.0f} mm ahead of the front feet:")
p(f"    dR_front = F*(d_f+WB)/WB = {Fd:.1f}*({D_F}+{WB})/{WB} = +{R_front_extra:.1f} N")
p(f"    dR_rear  = F - dR_front = {-R_rear_delta:.1f} N")
p(f"    R_rear_final = {R_rear_static:.1f} - {R_rear_delta:.1f} = "
  f"{R_rear_static-R_rear_delta:.1f} N "
  f"{'-> REAR FEET LIFT, TIPS' if R_rear_static-R_rear_delta < 0 else '-> stays down'}")
Ff = (R_front_static + R_front_extra)/2
p(f"    per front foot = {Ff:.1f} N")
p()
p(f"  knee torque model tau = F_v * L3 * sin(theta), L3={L3*1000:.1f} mm:")
p(f"  {'theta':<8}{'tau N.m':>10}{'kg.cm':>9}{'vs 25 sust':>12}{'vs 48 peak':>12}")
for th in (20, 30, 40):
    tau = Ff*L3*math.sin(math.radians(th))
    p(f"  {th:<8}{tau:>10.2f}{nm2kgcm(tau):>9.1f}{nm2kgcm(tau)/25:>11.2f}x{nm2kgcm(tau)/48:>11.2f}x")
p("  STS3250 measured (robonine bench): 48 kg.cm peak, 25 kg.cm SUSTAINED before")
p("  the 70 C protection cuts torque. 50 kg.cm is the datasheet stall, not usable.")
p("  => DESIGN DEMAND: press with the front legs NEAR-STRAIGHT (theta <= 20 deg).")

# calibration: what the project's own '22-27 kg.cm at k=1.0' implies
tau_trot40 = (W/2)*L3*math.sin(math.radians(40))
p(f"\n  sanity: trot, half the robot on one diagonal pair -> {W/2:.1f} N per foot;")
p(f"    theta=40 deg -> {nm2kgcm(tau_trot40):.1f} kg.cm, which reproduces the")
p(f"    project's quoted '~22-27 kg.cm at k=1.0'. Model CALIBRATED.")

# ============================================================ (b) CRACK
h("(b) CRACK -- force to open an unsprung interior door from rest")
DOOR_W, DOOR_H = 0.813, 2.032          # 32 x 80 in US interior door
HANDLE_ARM = DOOR_W - 0.065            # handle 65 mm in from the leading edge
A_DOOR = DOOR_W*DOOR_H
p(f"door 813 x 2032 mm, area {A_DOOR:.3f} m^2, handle lever arm {HANDLE_ARM:.3f} m")
p(f"hollow-core 13.6 kg (<30 lb, sourced) / solid-core 35 kg")

def hinge_terms(mass):
    Wd = mass*G
    mu_h, r_thrust, r_pin, h_sp = 0.30, 0.005, 0.0032, 1.5
    T_ax = mu_h*Wd*r_thrust                                  # weight on knuckle thrust faces
    F_rad = Wd*(DOOR_W/2)/h_sp                               # overturning couple per hinge
    T_rad = mu_h*F_rad*r_pin*2
    return T_ax, T_rad, T_ax+T_rad

p()
p(f"{'term':<44}{'hollow N':>10}{'solid N':>10}   (at the handle, /0.748 m)")
rows = {}
for name, mass in (("hollow", 13.6), ("solid", 35.0)):
    Ta, Tr, Tt = hinge_terms(mass)
    rows[name] = dict(hinge=Tt/HANDLE_ARM)
p(f"{'1. hinge friction (mu=0.30, r_thrust 5 mm, r_pin 3.2 mm)':<44}"
  f"{rows['hollow']['hinge']:>10.2f}{rows['solid']['hinge']:>10.2f}")

for name, mass in (("hollow", 13.6), ("solid", 35.0)):
    for a in (0.5, 1.0, 2.0, 3.0):
        T = mass*G*(DOOR_W/2)*math.sin(math.radians(a))
        rows[name][f"slope{a}"] = T/HANDLE_ARM
for a in (0.5, 1.0, 2.0, 3.0):
    p(f"{f'2. hinge axis {a} deg out of plumb (self-close)':<44}"
      f"{rows['hollow'][f'slope{a}']:>10.2f}{rows['solid'][f'slope{a}']:>10.2f}")

for dp in (3, 5, 25):
    T = dp*A_DOOR*(DOOR_W/2)
    p(f"{f'3. draught / HVAC dP = {dp} Pa (breakaway only)':<44}"
      f"{T/HANDLE_ARM:>10.2f}{T/HANDLE_ARM:>10.2f}")
    rows['hollow'][f'dp{dp}'] = T/HANDLE_ARM
p(f"{'4. paint/seal stiction breakaway (ESTIMATE)':<44}{5.0:>10.2f}{5.0:>10.2f}")
p(f"{'5. door bottom dragging on carpet (ESTIMATE)':<44}{'5-30':>10}{'5-30':>10}")

F_NOM  = rows['hollow']['hinge'] + rows['hollow']['slope0.5'] + 2.0   # +2 N latch/strike drag floor
F_ANA  = rows['hollow']['hinge'] + rows['hollow']['slope1.0'] + rows['hollow']['dp5'] + 5.0
F_ANA_W= rows['solid'] ['hinge'] + rows['solid'] ['slope2.0'] + rows['hollow']['dp5'] + 5.0
F_WORST= 25.0     # CODE-ANCHORED design ceiling, see note below -- all checks use this
F_REAL = F_ANA
F_PATH = F_ANA_W + rows['hollow']['dp25']
p()
p(f"NOMINAL  (well-hung hollow, 0.5 deg, HVAC off, +2 N strike drag) = {F_NOM:5.1f} N "
  f"({F_NOM*HANDLE_ARM:5.2f} N.m at the door)")
p(f"ANALYTIC REALISTIC WORST (hollow, 1 deg, 5 Pa, stiction)        = {F_ANA:5.1f} N "
  f"({F_ANA*HANDLE_ARM:5.2f} N.m)")
p(f"ANALYTIC WORST (solid, 2 deg, 5 Pa, stiction)                   = {F_ANA_W:5.1f} N "
  f"({F_ANA_W*HANDLE_ARM:5.2f} N.m)")
p(f"PATHOLOGICAL  (+ 25 Pa HVAC imbalance)                          = {F_PATH:5.1f} N "
  f"-> OUT OF SCOPE, abort")
p()
p(f"reference ceilings: ADA 404.2.9 interior hinged door 22.2 N;")
p(f"                    BS 8300 25 N (0-30 deg) / 22 N (30-60 deg); AS1428 20 N.")
p(f">>> The analytic build-up ({F_ANA_W:.1f} N) UNDER-PREDICTS: it cannot model a")
p(f"    misaligned strike, a binding hinge, a painted stop or a dragging latch, and")
p(f"    those are exactly why accessibility codes had to legislate a ceiling at all.")
p(f"    ALL CHECKS BELOW THEREFORE USE THE CODE-ANCHORED DESIGN CEILING")
p(f"    F_door = {F_WORST:.0f} N (BS 8300 0-30 deg). Anything above it: ABORT, not push harder.")
p()
Iy = (1/3)*13.6*DOOR_W**2
p(f"door inertia (hollow) I = m*w^2/3 = {Iy:.2f} kg.m^2; at 0.2 rad/s^2 that is")
p(f"  {Iy*0.2:.2f} N.m = {Iy*0.2/HANDLE_ARM:.2f} N at the handle -- negligible IF SLOW.")

# ============================================================ (c) TRACTION
h("(c) TRACTION")
p(f"W = {W:.1f} N. Traction F = mu*W (independent of how many feet are down,")
p( "so long as no foot is unloaded to zero while the others slip).")
MU = {"bare PETG on hardwood (UNVERIFIED, est)": (0.25, 0.35),
      "TPU 95A pad on hardwood (sourced 0.70-0.90)": (0.70, 0.90),
      "rubber/TPU pad on low carpet (sourced 0.5-1.25)": (0.50, 1.25)}
p()
p(f"{'surface':<46}{'mu':>12}{'F_max N':>16}")
TRAC = {}
for k, (lo, hi) in MU.items():
    TRAC[k] = (lo*W, hi*W)
    p(f"{k:<46}{f'{lo}-{hi}':>12}{f'{lo*W:.1f}-{hi*W:.1f}':>16}")
p()
p(f"{'surface':<46}{f'vs {F_WORST:.0f} N design ceiling':>26}")
for k, (lo, hi) in TRAC.items():
    p(f"{k:<46}{f'{lo/F_WORST:.2f}x - {hi/F_WORST:.2f}x':>26}"
      f"  {'PASS@1.5x' if lo/F_WORST>=1.5 else ('marginal' if lo/F_WORST>=1.0 else 'FAILS')}")
p()
p("=> HARD DEMAND: TPU (or rubber) foot pads. Bare PETG feet cannot deliver the")
p("   design-worst door force on hardwood. Carpet's LOW end is also marginal.")

# ============================================================ (d) THE PRY
h("(d) THE PRY -- loads through a wedged front leg")
H_FOOT_TO_HIP = 0.240      # vertical foot->hip-roll axis in a standing pose
H_FOOT_TO_KNEE = L3*math.cos(math.radians(20))
p(f"foot->knee vertical (theta=20 deg) = {L3}*cos20 = {H_FOOT_TO_KNEE:.4f} m")
p(f"foot->hip vertical (standing)      = {H_FOOT_TO_HIP:.3f} m")
p()
p(f"{'F_pry N':>8}{'M_knee N.m':>12}{'kg.cm':>9}{'M_hip N.m':>11}{'kg.cm':>9}{'hip vs 25 sust':>16}")
for F in (5, 10, 16, 25, 40):
    Mk, Mh = F*H_FOOT_TO_KNEE, F*H_FOOT_TO_HIP
    p(f"{F:>8}{Mk:>12.2f}{nm2kgcm(Mk):>9.1f}{Mh:>11.2f}{nm2kgcm(Mh):>9.1f}"
      f"{nm2kgcm(Mh)/25:>15.2f}x")
F_LEG_SUST = kgcm2nm(25)/H_FOOT_TO_HIP
F_LEG_PEAK = kgcm2nm(48)/H_FOOT_TO_HIP
p()
p(f"break-even on the HIP servo (the binding joint, not the knee):")
p(f"  at 25 kg.cm sustained: F = {kgcm2nm(25):.2f}/{H_FOOT_TO_HIP} = {F_LEG_SUST:.1f} N")
p(f"  at 48 kg.cm peak     : F = {F_LEG_PEAK:.1f} N")
p(f"  with the project's 1.5x rule on sustained: F = {F_LEG_SUST/1.5:.1f} N")
p(f"  => a leg can pry {F_LEG_SUST:.1f} N. NOMINAL door ({F_NOM:.1f} N) PASSES;")
p(f"     REALISTIC WORST ({F_REAL:.1f} N) and DESIGN WORST ({F_WORST:.1f} N) FAIL.")

p()
p("PRINTED SHANK IN BENDING (calf_link.py: 34 x 30 box, 4 mm walls):")
b,d,bi,di = 34.,30.,26.,22.
I1 = (b*d**3 - bi*di**3)/12; Z1 = I1/(d/2)
I2 = (d*b**3 - di*bi**3)/12; Z2 = I2/(b/2)
p(f"  I (bend in the 30 mm direction) = (34*30^3 - 26*22^3)/12 = {I1:.0f} mm^4, Z = {Z1:.0f} mm^3")
p(f"  I (bend in the 34 mm direction) = (30*34^3 - 22*26^3)/12 = {I2:.0f} mm^4, Z = {Z2:.0f} mm^3")
for F in (25, 100):
    M = F*H_FOOT_TO_KNEE*1000
    p(f"  F={F:>3} N -> M_knee = {M:.0f} N.mm, sigma = M/Z = {M/Z1:.2f} MPa")
    p(f"        vs PETG flexural XY 78.9 MPa -> SF {78.9/(M/Z1):.0f}x")
    p(f"        vs PETG Z-direction tensile 13.4 MPa (layer adhesion, the weakest")
    p(f"        published number) -> SF {13.4/(M/Z1):.1f}x")
Epetg = 1700.
dfl = 25*L3**3*1e9/(3*Epetg*I1)
p(f"  tip deflection at 25 N: F L^3/(3 E I) = 25*{L3*1000:.1f}^3/(3*{Epetg:.0f}*{I1:.0f})"
  f" = {dfl:.2f} mm -- negligible")
p("  => THE PRINTED SHANK IS NOT THE PROBLEM. It is ~15x over-strength even on the")
p("     worst published PETG number. The failure is 100% in the SERVOS.")

p()
p("SERVO HORN -> PRINTED HIP DISC (the real mechanical risk):")
PCD = 0.017
for F in (10, 25):
    Mh = F*H_FOOT_TO_HIP
    Fs = Mh/(4*PCD/2)
    p(f"  F_pry={F:>3} N -> M_hip {Mh:.2f} N.m -> {Fs:.0f} N per M3 screw at "
      f"{PCD*1000:.0f} mm PCD")
    p(f"      bearing on 6 mm of PETG: {Fs:.0f}/(3*6) = {Fs/18:.1f} MPa "
      f"(PETG bearing ~50 MPa, SF {50/(Fs/18):.1f}x) -- but this CREEPS and the")
    p(f"      holes elongate under repeated load. VERIFICATION.md already flags a")
    p(f"      0.30 mm ligament in exactly this disc.")

p()
p("ALTERNATIVE: LOW CHASSIS HOOK instead of a leg")
p(f"  hook at height h; pull F; overturning M = F*h about the FRONT-foot line")
p(f"  {'h mm':>6}{'F=10':>9}{'F=16':>9}{'F=25':>9}{'F=40':>9}   (M in N.m; budget "
  f"{B_WORK:.2f})")
for hh in (0.05, 0.10, 0.20, 0.40, 1.05):
    row = "".join(f"{F*hh:>9.2f}" for F in (10, 16, 25, 40))
    p(f"{hh*1000:>6.0f}{row}")
p(f"  break-even height at the DESIGN WORST {F_WORST:.1f} N: h = {B_WORK:.2f}/{F_WORST:.1f} "
  f"= {B_WORK/F_WORST*1000:.0f} mm")
p(f"  with 1.5x margin:                                   h = {B_WORK/1.5/F_WORST*1000:.0f} mm")
p(f"  => DESIGN RULE: the door-pulling feature must sit BELOW "
  f"{B_WORK/1.5/F_WORST*1000:.0f} mm above the floor.")
p(f"  a hook at 100 mm carries {B_WORK/0.10:.0f} N before tipping -- "
  f"{B_WORK/0.10/F_LEG_SUST:.1f}x better than the leg pry, and the load path is")
p(f"  chassis->legs-in-compression, the direction the legs were designed for.")

# chest push (the push-door case)
p()
p("CHEST PUSH (push-door case; moment is about the REAR-foot line):")
B_REAR = W*(WB - abs(x_onearm))
p(f"  rear-tip budget = W*(WB - |x_cg|) = {W:.1f}*({WB} - {abs(x_onearm):.4f}) "
  f"= {B_REAR:.2f} N.m")
for hh in (0.20, 0.30):
    for F in (6, 16, 25.5):
        p(f"  push {F:>5.1f} N at h={hh*1000:.0f} mm -> M {F*hh:.2f} N.m, "
          f"margin {B_REAR/(F*hh):.1f}x")

# ============================================================ (e) SPINE
h("(e) SPINE POSITION DURING THE PRY")
p("CLAIM AS WRITTEN ('spine must be DOWN so the load path goes through the")
p("chassis') is CONFIRMED -- but the usual reason given for it is WRONG.")
p()
p("1. STATIC tipping is INDEPENDENT of CG height.")
p("   Overturning = F*h_force. Restoring = W*d. Neither contains z_cg.")
p("   (CAD-DECISION.md sec 4(f) says the same thing for the humanoid.)")
p("   => 'spine up raises the CG so it tips more' is FALSE for a static pull.")
p()
p("2. What DOES change, #1: THE HEIGHT AT WHICH THE FORCE IS APPLIED.")
for hh, lbl in ((0.10, "chassis hook, spine down"), (1.05, "arm at the lever, spine up")):
    p(f"   {lbl:<32} h={hh:.2f} m  M = {F_WORST:.1f}*{hh:.2f} = "
      f"{F_WORST*hh:6.2f} N.m  vs budget {B_WORK:.2f} -> "
      f"{'PASS' if F_WORST*hh<=B_WORK/1.5 else 'TIPS'}")
p(f"   ratio = {1.05/0.10:.1f}x. THIS is the quantified difference, and it is")
p(f"   {F_WORST*1.05/B_WORK:.1f}x over the budget at the top. Not marginal -- catastrophic.")
p()
p("3. What DOES change, #2: INERTIAL overturning when the door breaks free.")
m_move = (341+176+72+2*ARM_NOM+60)/1000.0
m_fix  = M_TOT - m_move
z_fix  = 0.18
p("   Model it as an ELASTIC RELEASE, not a constant-force acceleration: the leg")
p("   servos are POSITION-controlled, so when the door lets go the only stored")
p("   energy is the elastic + backlash deflection accumulated at F_WORST.")
d_bend = 25*L3**3*1e9/(3*Epetg*I1) if False else 0.24    # mm, from (d)
d_lash = math.radians(0.43)*H_FOOT_TO_HIP*1000            # STS3250 measured backlash 0.43 deg
s_tot  = (d_bend + d_lash)/1000.0
E_st   = 0.5*F_WORST*s_tot
v_snap = math.sqrt(2*E_st/M_TOT)
a_snap = v_snap**2/(2*s_tot)
p(f"   shank bending at {F_WORST:.0f} N = {d_bend:.2f} mm; hip backlash 0.43 deg "
  f"(robonine measured) x {H_FOOT_TO_HIP} m = {d_lash:.2f} mm -> s = {s_tot*1000:.2f} mm")
p(f"   E = 0.5*F*s = {E_st*1000:.1f} mJ -> v = sqrt(2E/m) = {v_snap:.3f} m/s -> "
  f"a = v^2/(2s) = {a_snap:.2f} m/s^2")
for z_move, lbl in ((0.20, "spine DOWN"), (0.45, "spine UP 250 mm")):
    z_cg = (m_move*z_move + m_fix*z_fix)/M_TOT
    p(f"   {lbl:<16} moving {m_move:.2f} kg at z={z_move:.2f}, fixed {m_fix:.2f} kg at "
      f"z={z_fix:.2f} -> z_cg = {z_cg:.3f} m")
    p(f"   {'':16} M_inertial = m*a*z_cg = {M_TOT*a_snap*z_cg:.2f} N.m vs budget "
      f"{B_WORK:.2f} -> {'PASS' if M_TOT*a_snap*z_cg<=B_WORK/1.5 else ('MARGINAL' if M_TOT*a_snap*z_cg<=B_WORK else 'TIPS')}")
z_dn = (m_move*0.20 + m_fix*z_fix)/M_TOT
z_up = (m_move*0.45 + m_fix*z_fix)/M_TOT
p(f"   spine up is {z_up/z_dn:.2f}x worse inertially ({(z_up/z_dn-1)*100:.0f}%).")
p(f"   The snap is survivable BECAUSE the actuators are stiff position sources with")
p(f"   almost no stored energy. It stops being survivable the moment anything")
p(f"   compliant is added to the load path (a spring-loaded paw, a soft hook mount,")
p(f"   a long TPU pad). DESIGN RULE: the door-pull load path must be STIFF.")
p()
p("4. What DOES change, #3: MAST BENDING. Two M8x1.25 rods, 120 mm apart,")
p("   bending in the SAGITTAL plane -> each rod bends about its OWN axis;")
p("   the 120 mm spacing buys nothing for fore-aft loads.")
d_min = 6.647   # M8x1.25 minor diameter
I_rod = math.pi*d_min**4/64; Z_rod = math.pi*d_min**3/32
p(f"   M8x1.25 minor dia {d_min} mm -> I = pi*d^4/64 = {I_rod:.1f} mm^4/rod, "
  f"Z = {Z_rod:.1f} mm^3")
for Lm in (0.250,):
    M = F_WORST*Lm
    sig = (M/2)*1000/Z_rod
    dfl = F_WORST*(Lm*1000)**3/(3*200000*2*I_rod)
    p(f"   cantilever L={Lm*1000:.0f} mm, F={F_WORST:.1f} N -> M_base {M:.2f} N.m")
    p(f"     stress/rod = {sig:.0f} MPa (grade 4.8 rod yield ~320 MPa, SF "
      f"{320/sig:.1f}x -- but every thread root is a notch)")
    p(f"     sway = F L^3/(3 E I_total) = {dfl:.2f} mm at the chest")
p("   spine DOWN: mast bending = 0. Force goes straight into the chassis.")
p()
_sway = F_WORST*(250.0)**3/(3*200000*2*I_rod)
p("VERDICT: CONFIRMED, restated. The rule is not 'spine down because the CG is")
p("lower'. The rule is: THE PULLING FORCE MUST BE APPLIED LOW AND THROUGH THE")
p(f"CHASSIS. Spine-down is a consequence of that, plus it deletes {_sway:.1f} mm of mast")
p(f"sway and {(z_up/z_dn-1)*100:.0f}% of the inertial overturning.")

# ============================================================ P(success)
h("PROBABILITY OF SUCCESS -- FIRST ATTEMPT")
STAGES_FULL = {"lever actually turns (needs T<=2.7 N.m + press pose holds)": 0.50,
               "door cracks and stays cracked (latch timing)": 0.55,
               "paw enters a 10-20 mm gap, blind, arm still on the lever": 0.35,
               "leg pry without slip / tip / servo cutout (F<=10 N)": 0.40}
STAGES_HOOK = {"lever actually turns": 0.50,
               "door cracks and stays cracked": 0.55,
               "chassis hook catches the door edge": 0.55,
               "hook pry without slip / tip (F<=30 N)": 0.70}
for name, st in (("FULL SEQUENCE AS SPECIFIED (leg pry)", STAGES_FULL),
                 ("WITH A CHASSIS HOOK SUBSTITUTED", STAGES_HOOK)):
    pr = 1.0
    p(f"\n{name}")
    for k, v in st.items():
        pr *= v
        p(f"  {k:<58}{v:.2f}")
    p(f"  {'independent product':<58}{pr:.3f} = {pr*100:.1f}%")
    p(f"  {'with positive correlation (a good door helps every stage)':<58}"
      f"~{pr*100*1.8:.0f}%")

p("\nFALLBACK -- 'PUSH-DOOR TOUCH-AND-THROUGH' (near certain):")
p(f"  unlatched (taped/wedged) unsprung door that opens AWAY; spine down;")
p(f"  walk forward, push with the TPU chassis bumper, walk through.")
p(f"  force needed {F_NOM:.1f} N; traction available "
  f"{TRAC['TPU 95A pad on hardwood (sourced 0.70-0.90)'][0]:.1f} N "
  f"-> {TRAC['TPU 95A pad on hardwood (sourced 0.70-0.90)'][0]/F_NOM:.0f}x")
p(f"  tipping: {F_NOM:.1f} N at h=0.20 m -> {F_NOM*0.20:.2f} N.m vs rear budget "
  f"{B_REAR:.2f} -> {B_REAR/(F_NOM*0.20):.0f}x")
p(f"  no arm, no lever, no gap, no pry, no servo over 25 kg.cm. P ~ 90-95%.")

p("\nINTERMEDIATE (recommended target) -- 'LEVER PRESS + PUSH THROUGH':")
p("  1 look/find lever  2 spine up, arm pad on the lever TIP, press (crouched,")
p("  one arm)  3 quadruped steps forward 30 mm -> crack  4 arm retracts+stows")
p("  5 spine down  6 chest bumper pushes the door open  7 walk through.")
p("  Deletes the two lowest-probability stages by choosing a PUSH door.")
p("  P ~ 50-60%. Demonstrates everything the full sequence claims except the pry.")

import json, pathlib
out = pathlib.Path(__file__).parent
(out/"door_seq_log.txt").write_text("\n".join(L))
NUM = dict(M_TOT=M_TOT, W=W, ARM_NOM=ARM_NOM, NEW_TORSO=NEW_TORSO,
           B_WORK=B_WORK, B_REAR=B_REAR, T_CODE=T_CODE, F_LEV_CODE=F_LEV_CODE,
           T_LEV_MAX=T_LEV_MAX, F_NOM=F_NOM, F_REAL=F_REAL, F_WORST=F_WORST,
           F_PATH=F_PATH, F_LEG_SUST=F_LEG_SUST, TRAC={k: v for k, v in TRAC.items()},
           x_both=x_both, x_onearm=x_onearm, x_crouch=x_crouch, x_1a_cr=x_1a_cr,
           hook_h_max=B_WORK/1.5/F_WORST, Ff=Ff, z_dn=z_dn, z_up=z_up)
(out/"door_seq_numbers.json").write_text(json.dumps(NUM, indent=2, default=str))
print(f"\n[wrote {out}/door_seq_log.txt and door_seq_numbers.json]")
