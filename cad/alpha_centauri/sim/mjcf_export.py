"""Alpha Centauri — MJCF generator: the simulation model comes OFF THE CAD.

    edu/.cadenv/bin/python cad/alpha_centauri/sim/mjcf_export.py

RUNS UNDER THE CAD INTERPRETER (edu/.cadenv), NEVER .venv. It needs build123d
to read the STEP solids; the simulation itself (crawl_sim.py) runs under .venv
with mujoco and reads only the XML + provenance JSON this file writes. That
two-stage split is the interpreter law (design log §3.6) applied to sim.

WHY GENERATED, NOT HAND-TYPED (design log §5.4)
--------------------------------------------
The CAD is parametric Python. Mass and inertia come straight off the solids and
the joint frames are already in interface_constants.py, so a hand-typed MJCF
would restate shared dimensions — the exact class of bug the interface block
exists to kill (a shared dimension assumed in two places is a latent bug; this
project has paid for that repeatedly). Everything here is either imported from
the constants / sibling ledgers or measured off a STEP at generation time.

MJCF and not URDF because URDF cannot express what comes next (the detents,
the rail as a joint); today the rail is exported as a MODE, not a joint:

    WALK  torso x = +37   the crawl-legal station
    WORK  torso x = +167  four-feet-down work station

Four XMLs: {walk,work} x {brain in chest (as drawn), brain aft (the pending
layout decision — exported as a VARIANT for A/B evidence, decided by nobody
here)}. The brain was a 300 g Jetson lump until REPLAN-2026-08-28; since
2026-09-22 it is the 215 g phone stack (balance.PHONE_ETC) and the A/B is
the same question with a lighter lump.

THE MASS MODEL — imported, never restated
-----------------------------------------
Printed parts are measured off their own STEP at PETG 0.953 g/cm3, the same
convention balance.py uses for everything (including the parts slated for
PC/PA-CF — noted as a limitation in SIM-NOTES.md). Cluster masses (torso
balance.TORSO_FULL, brain balance.PHONE_ETC, battery balance.BATTERY, arms
500 g, servo 74.5 g) come from balance.py / hand_load.py /
interface_constants.py — never restated here. This model comes out
~468 g heavier than balance.py's ledger total (both computed at export into
the provenance JSON, never restated here) — and that delta is NOT the
"~498 g of rail parts" it was once called. The waist-rail parts the ledger
predates (ways, rack, carriage, pawl, lever) sum 491.8 g off their STEPs,
but the model omits the spine_pawl solid that the ledger's SPINE cluster
includes, and the torso-remainder logic pins the torso cluster to
TORSO_FULL regardless of the measured chest/waist solids. Both totals and
the computed delta live in the provenance JSON, never silently reconciled.

L1 IS A DIAGONAL (law). The hip-pitch axis sits at (0, ±L1_LATERAL, +L1_VERTICAL)
from the abduction axis, IN THE FRAME THAT ROTATES WITH ABDUCTION. The MJCF
encodes exactly that: hip body at the abduction axis with a +X hinge, thigh
body at (0, ±0.0496, +0.0143) inside it with a +Y hinge.

THE SERVO IS A POSITION ACTUATOR AT 2.4516 N·m — the 25 kg·cm MEASURED figure
(hand_load.SERVO_MEASURED_KGCM), never the 50 kg·cm datasheet peak (law 6).
kp/kv/armature/damping are ASSUMPTIONS (recorded in provenance + SIM-NOTES);
the torque LIMIT is the measured number.

CONCURRENT-EDIT DISCIPLINE (task law 12): interface_constants may be edited
independently of this run. Every value used is snapshotted into
provenance.json at export time; crawl_sim.py treats THAT snapshot as the
authority for the XML it accompanies and warns if the live constants have
drifted since.
"""

import hashlib
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from build123d import Axis, Location, import_step

HERE = Path(__file__).parent          # cad/alpha_centauri/sim
CAD = HERE.parent                     # cad/alpha_centauri
sys.path.insert(0, str(CAD))

import assembly as A                  # noqa: E402  solve_leg — THE leg solve
import assembly_centaur as AC         # noqa: E402  TORSO_WALK/WORK, RAIL_MID
import balance as B                   # noqa: E402  the mass ledger
import hand_load as HL                # noqa: E402  measured servo figure, arms
import waist_rail as R                # noqa: E402  rail stations
import chassis as CH                  # noqa: E402  pack bays (seated boxes)
import spine_lock as SL               # noqa: E402  rack dims
from thigh import SEC_X as THIGH_SEC_X, SERVO_Z_LO as THIGH_SERVO_Z_LO  # noqa: E402
import interface_constants as IC      # noqa: E402

OUT = CAD / "output"
TBOT = CAD.parent / "telescopebot" / "output"
SIM_OUT = OUT / "sim"

PETG = 0.953                          # g/cm3 — balance.py's convention, all parts

# The one measured torque figure, converted once. 25 kg·cm * 0.0980665 N·m/(kg·cm).
TORQUE_LIMIT_NM = HL.SERVO_MEASURED_KGCM * 0.0980665          # 2.45166

# Actuator/joint model ASSUMPTIONS — not measurements. Recorded in provenance.
KP = 60.0            # N·m/rad — 2.3 deg of droop at the torque limit
KV = 2.0             # N·m·s/rad
ARMATURE = 0.0194    # kg·m2 — DONOR-derived: Dingo SimulationConfig G^2*m*r^2
JOINT_DAMPING = 0.1  # N·m·s/rad — donor used 1.049 for its own servo model;
                     # scaled down because at crawl speeds 1.0 masked kp droop
FRICTION = 1.0       # foot–ground: donor sim used 1.5; 1.0 is the cautious pick

DENS_G_MM3 = PETG / 1000.0


# --------------------------------------------------------------------------
# mass properties: everything in link-frame mm / g, converted to SI at the end
# --------------------------------------------------------------------------
class LinkMass:
    """Accumulates solids (posed build123d shapes) and point/box masses."""

    def __init__(self, name):
        self.name = name
        self.m = 0.0                        # g
        self.S = np.zeros(3)                # g·mm   first moment
        self.I0 = np.zeros((3, 3))          # g·mm2  inertia about link origin
        self.parts = []                     # provenance rows

    def _accum(self, m, com, I_com):
        c = np.asarray(com, float)
        self.m += m
        self.S += m * c
        self.I0 += I_com + m * ((c @ c) * np.eye(3) - np.outer(c, c))

    def add_solid(self, tag, shape):
        m = shape.volume / 1000.0 * PETG
        com = tuple(shape.center())
        I_com = np.array(shape.matrix_of_inertia) * DENS_G_MM3
        self._accum(m, com, I_com)
        self.parts.append({"part": tag, "mass_g": round(m, 1),
                           "com_mm": [round(v, 1) for v in com]})
        return m

    def add_box(self, tag, m, com, dims):
        """Point mass with a rectangular-box inertia (dims in mm)."""
        a, b, c = dims
        I = m / 12.0 * np.diag([b * b + c * c, a * a + c * c, a * a + b * b])
        self._accum(m, com, I)
        self.parts.append({"part": tag, "mass_g": round(m, 1),
                           "com_mm": [round(v, 1) for v in com],
                           "box_mm": list(dims)})

    def finish(self):
        assert self.m > 0, f"{self.name}: empty link"
        com = self.S / self.m
        I_com = self.I0 - self.m * ((com @ com) * np.eye(3) - np.outer(com, com))
        w = np.linalg.eigvalsh(I_com)
        assert w.min() > 0, f"{self.name}: inertia not positive definite {w}"
        return {
            "mass_kg": self.m / 1000.0,
            "com_m": (com / 1000.0).tolist(),
            # kg·m2, MJCF fullinertia order: ixx iyy izz ixy ixz iyz
            "fullinertia": [I_com[0, 0] * 1e-9, I_com[1, 1] * 1e-9,
                            I_com[2, 2] * 1e-9, I_com[0, 1] * 1e-9,
                            I_com[0, 2] * 1e-9, I_com[1, 2] * 1e-9],
            "parts": self.parts,
        }


def step(name, base=OUT):
    p = base / f"{name}.step"
    assert p.exists(), f"missing STEP: {p}"
    return import_step(str(p))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:16]


# --------------------------------------------------------------------------
# link property computation — poses copied from assembly_centaur.py / marks.py
# --------------------------------------------------------------------------
def build_links():
    files = {}

    def rec(name, base=OUT):
        p = base / f"{name}.step"
        files[str(p.relative_to(CAD.parent.parent))] = {
            "sha256_16": sha(p), "mtime": p.stat().st_mtime}
        return step(name, base)

    # ---- chassis: printed structure that does NOT slide -------------------
    ch = LinkMass("chassis")
    # 4 quarters + 4 bolt-on pods + 6 keys, placed by chassis.chassis_placed()
    for n in ("chassis_quarter_inner", "chassis_quarter_outer",
              "abduction_pod", "chassis_splice_key"):
        rec(n)                                   # provenance hashes
    for n, s in CH.chassis_placed(OUT).items():
        ch.add_solid(f"chassis_{n}", s)
    # rail ways: 8 x 125 mm segments + 6 loose keys since 2026-09-07 (A1
    # mini). Placement is owned by waist_rail.way_run()/keys_placed() (rear
    # segments rotated 180 like the rear chassis half, every bolt asserted
    # on the ledge grid) -- never restated here.
    for s in R.way_run(rec("rail_way_inner"), rec("rail_way_outer")):
        ch.add_solid("rail_way_segment", s)
    for k in R.keys_placed(rec("rail_way_key")):
        ch.add_solid("rail_way_key", k)
    ch.add_solid("rail_rack", rec("rail_rack").moved(
        Location((AC.RAIL_MID, 0, 0))))
    # batteries: TWO 3S packs (balance.PACK_G each), seated in the rear bays
    # exactly where chassis.pack_seated() puts them -- never restated here.
    # (Until 2026-09-22: one NOMINAL 600 g box 110x40x30 at X_BATTERY.)
    for i, pk in enumerate(CH.pack_seated(rear=True)):
        ch.add_box(f"pack_{i}_NOMINAL", B.PACK_G, tuple(pk.center()),
                   (CH.PACK_L, CH.PACK_W, CH.PACK_H))
    # four abduction servos: stators live in the chassis pods.
    for sx in (1, -1):
        for sy in (1, -1):
            ch.add_box("abduction_servo", IC.SERVO_MASS_G,
                       (sx * IC.LEG_FB, sy * IC.LEG_LR, AC.HIP_Z),
                       (IC.SERVO_BODY_LENGTH, IC.SERVO_BODY_WIDTH,
                        IC.SERVO_BODY_HEIGHT))

    # ---- the brain, as a separable lump (the A/B) -------------------------
    # chest-floor pose is TORSO-local; aft pose is CHASSIS-local.
    # REPLAN-2026-08-28: phone + FE-URT-1 + buck, balance.PHONE_ETC (215 g),
    # replaces the 300 g Jetson lump that was modelled as 100 x 80 x 30.
    # Envelope is a DECISION, nominal: a ~150 x 72 x 8 phone stacked on the
    # adapter and the buck -> 150 x 75 x 20 box, resting on the floor.
    brain_dims = (150, 75, 20)
    chest_z0 = R.CAR_Z0 + R.CAR_T + 60.0 + 5.0      # retracted chest floor
    brain_chest = {"m": B.PHONE_ETC, "com": (0.0, 0.0, chest_z0 + 4 + 10),
                   "dims": brain_dims}
    brain_aft = {"m": B.PHONE_ETC, "com": (B.X_ELECTRONICS, 0.0, 4.0 + 10.0),
                 "dims": brain_dims}

    # ---- torso: everything that rides the carriage ------------------------
    # Boxes install rotated -90 about Z (marks.py §1.4 — a real bug, fixed).
    # Spine retracted for the crawl: the chest sits at the bottom of stroke.
    to = LinkMass("torso")
    to.add_solid("rail_carriage", rec("rail_carriage").moved(
        Location((0, 0, R.CAR_Z0))))
    to.add_solid("rail_pawl", rec("rail_pawl").moved(
        Location((0, R.PAWL_Y_SEAT, R.PAWL_ROOT_Z))))
    to.add_solid("rail_lever", rec("rail_lever").moved(
        Location((0, R.PAWL_Y_SEAT - R.LEAF_T, R.PAWL_ROOT_Z - R.LEAF_L))))
    z_deck = R.CAR_Z0 + R.CAR_T
    waist_g = to.add_solid("waist_box", rec("waist_box", TBOT)
                           .rotate(Axis.Z, -90).moved(Location((0, 0, z_deck))))
    rim = z_deck + 60.0
    to.add_solid("spine_rack", rec("spine_rack").moved(
        Location((-SL.RACK_W / 2, AC.ROD_Y - SL.RACK_T / 2, rim))))
    chest_g = to.add_solid("chest_box_RETRACTED", rec("chest_box", TBOT)
                           .rotate(Axis.Z, -90).moved(Location((0, 0, rim + 5.0))))

    # The TORSO_FULL cluster (balance.py: "chest box + brain + camera + two
    # arms", DERIVED from the 1538 g H2C-era figure minus Jetson plus phone).
    # Printed chest + waist measured above; brain and arms are ledger point
    # masses; whatever remains is camera + wiring + fasteners and sits on the
    # chest front wall. If the remainder went negative the ledger and the
    # solids would disagree — assert instead of hiding it.
    misc = B.TORSO_FULL - chest_g - waist_g - B.PHONE_ETC - HL.ARMS_G
    assert misc > 0, (
        f"torso ledger broken: TORSO_FULL {B.TORSO_FULL} < solids+points "
        f"({chest_g:.0f}+{waist_g:.0f}+{B.PHONE_ETC}+{HL.ARMS_G})")
    for sy in (1, -1):
        to.add_box("arm_HALF_NOMINAL", HL.ARMS_G / 2,
                   (0.0, sy * 95.0, rim + 5 + 40), (40, 40, 160))
    to.add_box("camera_misc_remainder", misc, (55.0, 0.0, rim + 5 + 60),
               (30, 90, 30))

    # ---- leg links (non-handed parts: one computation serves all 4) -------
    # Thigh STEP is authored +Z hip->knee (assembly._aim); the sim thigh frame
    # is z-UP with the link hanging on -Z at q=0, i.e. the STEP rotated 180
    # about Y. Same for the calf.
    th = LinkMass("thigh")
    th.add_solid("thigh_shell", rec("thigh_shell").rotate(Axis.Y, 180))
    cover = rec("thigh_cover").moved(
        Location((THIGH_SEC_X / 2 + 1.5, 0,
                  THIGH_SERVO_Z_LO + (IC.SERVO_BODY_LENGTH + 0.4) / 2)))
    th.add_solid("thigh_cover", cover.rotate(Axis.Y, 180))
    th.add_box("knee_servo", IC.SERVO_MASS_G,
               (0.0, 0.0, -(THIGH_SERVO_Z_LO + IC.SERVO_BODY_LENGTH / 2)),
               (IC.SERVO_BODY_WIDTH, IC.SERVO_BODY_HEIGHT,
                IC.SERVO_BODY_LENGTH))

    ca = LinkMass("calf")
    ca.add_solid("calf", rec("calf").rotate(Axis.Y, 180))

    # hip module: not yet drawn (design log §5.1) — hip-pitch servo + the three
    # joint parts, all carried at the hip-pitch station. sy handled per side.
    def hip_link(sy):
        h = LinkMass("hip")
        hp = (0.0, sy * IC.L1_LATERAL, IC.L1_VERTICAL)
        h.add_box("hip_pitch_servo", IC.SERVO_MASS_G, hp,
                  (IC.SERVO_BODY_LENGTH, IC.SERVO_BODY_HEIGHT,
                   IC.SERVO_BODY_WIDTH))
        jp = sum(step(n).volume / 1000 * PETG
                 for n in ("horn_adapter", "bearing_retainer", "bearing_carrier"))
        h.add_box("joint_parts", jp, hp, (36, 36, 20))
        return h.finish()

    for n in ("horn_adapter", "bearing_retainer", "bearing_carrier"):
        rec(n)

    return {
        "files": files,
        "chassis": ch.finish(),
        "torso": to.finish(),
        "thigh": th.finish(),
        "calf": ca.finish(),
        "hip_left": hip_link(+1),
        "hip_right": hip_link(-1),
        "brain_chest": brain_chest,
        "brain_aft": brain_aft,
        "chest_z0": chest_z0,
        "rim": rim,
    }


def add_point_to_link(link, pt):
    """Fold a point/box mass (mm/g dict) into an already-finished link dict."""
    lm = LinkMass("tmp")
    m0 = link["mass_kg"] * 1000.0
    c0 = np.array(link["com_m"]) * 1000.0
    ix, iy, iz, ixy, ixz, iyz = [v * 1e9 for v in link["fullinertia"]]
    I0 = np.array([[ix, ixy, ixz], [ixy, iy, iyz], [ixz, iyz, iz]])
    lm._accum(m0, c0, I0)
    lm.add_box("brain", pt["m"], pt["com"], pt["dims"])
    out = lm.finish()
    out["parts"] = link["parts"] + lm.parts[1:]
    return out


# --------------------------------------------------------------------------
# MJCF emission
# --------------------------------------------------------------------------
def fmt(v):
    if isinstance(v, (list, tuple, np.ndarray)):
        return " ".join(f"{x:.8g}" for x in v)
    return f"{v:.8g}"


def inertial(parent, link):
    ET.SubElement(parent, "inertial", pos=fmt(link["com_m"]),
                  mass=fmt(link["mass_kg"]),
                  fullinertia=fmt(link["fullinertia"]))


def build_xml(links, station_x_mm, brain_where, model_name):
    mm = 1e-3
    # Chassis origin height above ground — assembly.py's own stance identity:
    # the abduction datum (z = HIP_Z chassis-local) sits STANCE_Z above the
    # feet, so the chassis origin rides at STANCE_Z - HIP_Z = 199.0 mm.
    ride = (IC.STANCE_Z - AC.HIP_Z) * mm

    root = ET.Element("mujoco", model=model_name)
    ET.SubElement(root, "compiler", angle="radian", autolimits="true")
    ET.SubElement(root, "option", timestep="0.002", integrator="implicitfast",
                  gravity="0 0 -9.81")
    vis = ET.SubElement(root, "visual")
    ET.SubElement(vis, "global", offwidth="1280", offheight="960")
    ET.SubElement(vis, "headlight", ambient="0.35 0.35 0.35",
                  diffuse="0.7 0.7 0.7", specular="0.2 0.2 0.2")
    ET.SubElement(vis, "quality", shadowsize="4096")

    asset = ET.SubElement(root, "asset")
    ET.SubElement(asset, "texture", type="skybox", builtin="gradient",
                  rgb1="0.85 0.89 0.93", rgb2="0.55 0.62 0.70",
                  width="256", height="256")
    ET.SubElement(asset, "texture", name="grid", type="2d", builtin="checker",
                  rgb1="0.85 0.85 0.87", rgb2="0.72 0.74 0.78",
                  width="512", height="512")
    ET.SubElement(asset, "material", name="grid", texture="grid",
                  texrepeat="8 8", reflectance="0.05")

    dflt = ET.SubElement(root, "default")
    ET.SubElement(dflt, "joint", damping=fmt(JOINT_DAMPING),
                  armature=fmt(ARMATURE))
    ET.SubElement(dflt, "geom", contype="0", conaffinity="0", group="1")
    dcol = ET.SubElement(dflt, "default", {"class": "collide"})
    ET.SubElement(dcol, "geom", contype="1", conaffinity="2", group="0",
                  friction=f"{FRICTION} 0.005 0.0001", condim="3")
    ET.SubElement(dflt, "position", kp=fmt(KP), kv=fmt(KV),
                  forcerange=f"-{TORQUE_LIMIT_NM:.6f} {TORQUE_LIMIT_NM:.6f}")

    wb = ET.SubElement(root, "worldbody")
    ET.SubElement(wb, "light", pos="1 -1 2.5", dir="-0.4 0.4 -1",
                  diffuse="0.8 0.8 0.8")
    ET.SubElement(wb, "geom", name="floor", type="plane", size="3 3 0.05",
                  material="grid", contype="2", conaffinity="1",
                  friction=f"{FRICTION} 0.005 0.0001", group="0")
    ET.SubElement(wb, "camera", name="iso", mode="targetbodycom",
                  target="chassis", pos="0.95 -0.85 0.55")
    ET.SubElement(wb, "camera", name="side", mode="targetbodycom",
                  target="chassis", pos="0.05 -1.35 0.30")
    ET.SubElement(wb, "camera", name="front", mode="targetbodycom",
                  target="chassis", pos="1.35 0.0 0.35")

    chassis = ET.SubElement(wb, "body", name="chassis", pos=f"0 0 {ride:.6f}")
    ET.SubElement(chassis, "freejoint", name="root")
    ch_link = links["chassis_aft" if brain_where == "aft" else "chassis"]
    inertial(chassis, ch_link)
    ET.SubElement(chassis, "site", name="body_origin", size="0.005")
    ET.SubElement(chassis, "geom", type="box", name="chassis_box",
                  size=fmt([IC.CHASSIS_LENGTH / 2 * mm, IC.CHASSIS_WIDTH / 2 * mm,
                            IC.CHASSIS_HEIGHT / 2 * mm]),
                  pos=fmt([0, 0, IC.CHASSIS_HEIGHT / 2 * mm]),
                  rgba="0.55 0.57 0.60 1", **{"class": "collide"})
    for i, pk in enumerate(CH.pack_seated(rear=True)):
        ET.SubElement(chassis, "geom", type="box", name=f"pack_{i}",
                      size=fmt(np.array([CH.PACK_L, CH.PACK_W, CH.PACK_H]) * mm / 2),
                      pos=fmt(np.array(tuple(pk.center())) * mm),
                      rgba="0.20 0.25 0.55 1")
    if brain_where == "aft":
        ET.SubElement(chassis, "geom", type="box", name="brain",
                      size=fmt(np.array(links["brain_aft"]["dims"]) * mm / 2),
                      pos=fmt(np.array(links["brain_aft"]["com"]) * mm),
                      rgba="0.15 0.55 0.25 1")

    # ---- torso at its station --------------------------------------------
    torso = ET.SubElement(chassis, "body", name="torso",
                          pos=fmt([station_x_mm * mm, 0, 0]))
    t_link = links["torso_chest" if brain_where == "chest" else "torso"]
    inertial(torso, t_link)
    ET.SubElement(torso, "geom", type="box", name="carriage",
                  size=fmt([0.1, 0.085, 0.008]),
                  pos=fmt([0, 0, (R.CAR_Z0 + R.CAR_T / 2) * mm]),
                  rgba="0.75 0.45 0.15 1")
    ET.SubElement(torso, "geom", type="box", name="waist_box",
                  size=fmt([0.061, 0.082, 0.030]),
                  pos=fmt([0, 0, (R.CAR_Z0 + R.CAR_T + 30) * mm]),
                  rgba="0.25 0.35 0.60 1", **{"class": "collide"})
    ET.SubElement(torso, "geom", type="box", name="chest_box",
                  size=fmt([0.066, 0.075, 0.0425]),
                  pos=fmt([0, 0, (links["rim"] + 5 + 42.5) * mm]),
                  rgba="0.30 0.42 0.68 1", **{"class": "collide"})
    if brain_where == "chest":
        ET.SubElement(torso, "geom", type="box", name="brain",
                      size=fmt(np.array(links["brain_chest"]["dims"]) * mm / 2),
                      pos=fmt(np.array(links["brain_chest"]["com"]) * mm),
                      rgba="0.15 0.55 0.25 1")
    for sy in (1, -1):
        ET.SubElement(torso, "geom", type="box",
                      name=f"arm_{'l' if sy > 0 else 'r'}",
                      size="0.02 0.02 0.08",
                      pos=fmt([0, sy * 0.095, (links["rim"] + 45) * mm]),
                      rgba="0.35 0.35 0.38 1")

    # ---- legs -------------------------------------------------------------
    for tag, sx, sy in (("fl", 1, 1), ("fr", 1, -1), ("rl", -1, 1), ("rr", -1, -1)):
        hip = ET.SubElement(chassis, "body", name=f"hip_{tag}",
                            pos=fmt([sx * IC.LEG_FB * mm, sy * IC.LEG_LR * mm,
                                     AC.HIP_Z * mm]))
        ET.SubElement(hip, "joint", name=f"abd_{tag}", axis="1 0 0",
                      range="-0.9 0.9")
        inertial(hip, links["hip_left" if sy > 0 else "hip_right"])
        ET.SubElement(hip, "geom", type="box", name=f"hipm_{tag}",
                      size="0.023 0.018 0.013",
                      pos=fmt([0, sy * IC.L1_LATERAL * mm, IC.L1_VERTICAL * mm]),
                      rgba="0.80 0.30 0.15 1")
        thigh = ET.SubElement(hip, "body", name=f"thigh_{tag}",
                              pos=fmt([0, sy * IC.L1_LATERAL * mm,
                                       IC.L1_VERTICAL * mm]))
        ET.SubElement(thigh, "joint", name=f"hip_{tag}", axis="0 1 0",
                      range="-1.6 1.6")
        inertial(thigh, links["thigh"])
        ET.SubElement(thigh, "geom", type="capsule", name=f"thigh_g_{tag}",
                      fromto=fmt([0, 0, 0, 0, 0, -IC.L2_THIGH * mm]),
                      size="0.014", rgba="0.85 0.55 0.20 1")
        calf = ET.SubElement(thigh, "body", name=f"calf_{tag}",
                             pos=fmt([0, 0, -IC.L2_THIGH * mm]))
        ET.SubElement(calf, "joint", name=f"knee_{tag}", axis="0 1 0",
                      range="-2.2 0.6")
        inertial(calf, links["calf"])
        ET.SubElement(calf, "geom", type="capsule", name=f"calf_g_{tag}",
                      fromto=fmt([0, 0, 0, 0, 0, -IC.FOOT_CENTRE_FROM_KNEE * mm]),
                      size="0.010", rgba="0.30 0.30 0.33 1")
        # THE FOOT IS A SPHERE CENTRED ON THE CALF AXIS AT L3 - R, so contact
        # lands at exactly L3 for every calf angle (interface_constants).
        ET.SubElement(calf, "geom", type="sphere", name=f"foot_{tag}",
                      size=fmt(IC.FOOT_SPHERE_R * mm),
                      pos=fmt([0, 0, -IC.FOOT_CENTRE_FROM_KNEE * mm]),
                      rgba="0.12 0.12 0.12 1", **{"class": "collide"})
        ET.SubElement(calf, "site", name=f"foot_site_{tag}",
                      pos=fmt([0, 0, -IC.L3_CALF * mm]), size="0.004")

    act = ET.SubElement(root, "actuator")
    for tag in ("fl", "fr", "rl", "rr"):
        for j in ("abd", "hip", "knee"):
            ET.SubElement(act, "position", name=f"{j}_{tag}",
                          joint=f"{j}_{tag}",
                          ctrlrange="-2.2 2.2")

    sens = ET.SubElement(root, "sensor")
    for tag in ("fl", "fr", "rl", "rr"):
        for j in ("abd", "hip", "knee"):
            ET.SubElement(sens, "actuatorfrc", name=f"tau_{j}_{tag}",
                          actuator=f"{j}_{tag}")

    ET.indent(root)
    return ET.tostring(root, encoding="unicode")


# --------------------------------------------------------------------------
def main():
    SIM_OUT.mkdir(parents=True, exist_ok=True)
    links = build_links()

    # brain variants folded into finished links
    links["torso_chest"] = add_point_to_link(links["torso"],
                                             links["brain_chest"])
    links["chassis_aft"] = add_point_to_link(links["chassis"],
                                             links["brain_aft"])

    # ---- analytic CoM cross-check per variant (mm, chassis frame) ---------
    # This cross-check verifies MASS BOOKKEEPING at qpos=0 — legs straight —
    # where the analytic sum is comparable to MuJoCo's subtree CoM of the
    # loaded XML (e.g. work_chest: +45.89 analytic vs +45.77 in MuJoCo). It
    # is NOT the stance-pose CoM the crawl actually runs at: posed at stance
    # that measures ~+40.5, and ~+39.5 once settled under servo droop —
    # crawl_sim.py measures that live, every step.
    def com_x(station, where):
        ch = links["chassis_aft" if where == "aft" else "chassis"]
        to = links["torso_chest" if where == "chest" else "torso"]
        legs_m = 4 * (links["thigh"]["mass_kg"] + links["calf"]["mass_kg"]
                      + links["hip_left"]["mass_kg"])
        m = ch["mass_kg"] + to["mass_kg"] + legs_m
        x = (ch["mass_kg"] * ch["com_m"][0]
             + to["mass_kg"] * (to["com_m"][0] + station / 1000.0)) / m
        return x * 1000.0, m

    variants = {}
    for st_name, st_x in (("walk", AC.TORSO_WALK), ("work", AC.TORSO_WORK)):
        for where in ("chest", "aft"):
            name = f"alpha_centauri_{st_name}_{where}"
            xml = build_xml(links, st_x, where, name)
            (SIM_OUT / f"{name}.xml").write_text(xml)
            cx, m = com_x(st_x, where)
            variants[name] = {"station": st_name, "torso_x_mm": st_x,
                              "brain": where,
                              "com_x_mm_analytic": round(cx, 2),
                              "total_mass_kg": round(m, 4)}
            print(f"wrote {name}.xml   CoM_x {cx:+7.2f} mm   "
                  f"total {m:.3f} kg")

    alpha, knee, ext = A.solve_leg(IC.STANCE_Z)
    ledger_total_g = (B.CHASSIS + 4 * B.LEG_TOTAL + B.TORSO_FULL
                      + B.SPINE + B.BATTERY)
    # Mass reconciliation — COMPUTED, never narrated from memory. The delta
    # is not "the rail parts": the model omits the spine_pawl solid that the
    # ledger's SPINE cluster includes, and the torso-remainder logic pins the
    # torso cluster to TORSO_FULL regardless of the measured solids.
    model_total_g = (variants["alpha_centauri_walk_chest"]["total_mass_kg"]
                     * 1000.0)
    rail_parts_g = sum(p["mass_g"]
                       for ln in ("chassis", "torso")
                       for p in links[ln]["parts"]
                       if p["part"].startswith("rail_"))
    n_steps = len(links["files"])          # computed — never hard-code this

    prov = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "generator": "cad/alpha_centauri/sim/mjcf_export.py",
        # Identify the interpreter WITHOUT leaking a developer home path:
        # provenance is committed evidence, and an absolute path is a leak.
        "interpreter": "%s %d.%d.%d" % (
            os.path.basename(sys.executable), *sys.version_info[:3]),
        "git_rev": subprocess.run(["git", "rev-parse", "HEAD"],
                                  capture_output=True, text=True,
                                  cwd=CAD).stdout.strip(),
        "constants_snapshot": {
            "L1_LATERAL": IC.L1_LATERAL, "L1_VERTICAL": IC.L1_VERTICAL,
            "L1_HIP_OFFSET": IC.L1_HIP_OFFSET, "PHI_DEG": IC.PHI_DEG,
            "L2_THIGH": IC.L2_THIGH, "L3_CALF": IC.L3_CALF,
            "LEG_FB": IC.LEG_FB, "LEG_LR": IC.LEG_LR,
            "STANCE_Z": IC.STANCE_Z,
            "LEG_EXTENSION_LIMIT": IC.LEG_EXTENSION_LIMIT,
            "LEG_EXTENSION_LIMIT_FRAC": IC.LEG_EXTENSION_LIMIT_FRAC,
            "LEG_REACH_MAX": IC.LEG_REACH_MAX,
            "CRAWL_SHIFT_CENTRED": IC.CRAWL_SHIFT_CENTRED,
            "CRAWL_STRIDE_HALF": IC.CRAWL_STRIDE_HALF,
            "FOOT_SPHERE_R": IC.FOOT_SPHERE_R,
            "FOOT_CENTRE_FROM_KNEE": IC.FOOT_CENTRE_FROM_KNEE,
            "HIP_Z": AC.HIP_Z, "TORSO_WALK": AC.TORSO_WALK,
            "TORSO_WORK": AC.TORSO_WORK, "RAIL_MID": AC.RAIL_MID,
            "RAIL_TRAVEL": R.TRAVEL,
            "SERVO_MEASURED_KGCM": HL.SERVO_MEASURED_KGCM,
            "TORQUE_LIMIT_NM": TORQUE_LIMIT_NM,
            "SERVO_MASS_G": IC.SERVO_MASS_G,
            "X_BATTERY": B.X_BATTERY, "X_ELECTRONICS": B.X_ELECTRONICS,
            "BATTERY_G": B.BATTERY, "PACK_G": B.PACK_G, "N_PACKS": B.N_PACKS,
            "BAY_X": CH.BAY_X, "BAY_Y": list(CH.BAY_Y),
            "PHONE_ETC_G": B.PHONE_ETC,
            "TORSO_FULL_H2C_ERA_G": B.TORSO_FULL_H2C_ERA,
            "TORSO_FULL_G": B.TORSO_FULL, "ARMS_G": HL.ARMS_G,
            "BATTERY_RAIL_TRAVEL_RETIRED": IC.BATTERY_RAIL_TRAVEL,
            "solve_leg_alpha_deg": alpha, "solve_leg_knee_deg": knee,
            "solve_leg_ext_mm": ext,
        },
        "assumptions_NOT_measured": {
            "kp_Nm_per_rad": KP, "kv_Nms_per_rad": KV,
            "armature_kgm2_DONOR": ARMATURE,
            "joint_damping_Nms": JOINT_DAMPING,
            "foot_friction_mu": FRICTION,
            "petg_density_g_cm3_ALL_PARTS": PETG,
            "servo_box_uses_UNRESOLVED_height_35mm": True,
        },
        "step_files": links["files"],
        "links": {k: links[k] for k in ("chassis", "chassis_aft", "torso",
                                        "torso_chest", "thigh", "calf",
                                        "hip_left", "hip_right")},
        "variants": variants,
        "step_files_count": n_steps,
        "mass_reconciliation": {
            "balance_py_ledger_total_g": round(ledger_total_g, 0),
            "model_total_g": round(model_total_g, 1),
            "model_minus_ledger_g": round(model_total_g - ledger_total_g, 1),
            "rail_parts_sum_g": round(rail_parts_g, 1),
            "note": "the delta is NOT the rail-part sum: the ledger predates "
                    f"the waist-rail parts ({rail_parts_g:.1f} g off their "
                    "STEPs) but this model omits the spine_pawl solid that "
                    "the ledger's SPINE cluster includes, and the "
                    "torso-remainder logic pins the torso cluster to "
                    "TORSO_FULL regardless of the measured chest/waist "
                    "solids",
        },
    }
    (SIM_OUT / "provenance.json").write_text(json.dumps(prov, indent=1))
    print(f"\nprovenance.json written — ledger {ledger_total_g:.0f} g, "
          f"model {model_total_g:.0f} g (delta "
          f"{model_total_g - ledger_total_g:+.1f} g), "
          f"all {n_steps} STEP files snapshotted (count computed)")
    print(f"leg solve: thigh {alpha:.2f} deg off vertical, knee {knee:.2f} deg, "
          f"extension {ext:.2f} mm")


if __name__ == "__main__":
    main()
