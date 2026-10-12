"""Alpha Centauri — leg-angle mapping + the static-crawl sequencer.

Runs under .venv. Two things live here, and their provenance differs — that
distinction is the point of this docstring (SIM-NOTES.md carries the table):

DONOR-DERIVED (MonashRobotics DingoQuadruped, MIT)
--------------------------------------------------
* The IK itself — dingo_ik.py, a faithful port (see its docstring for the
  three marked deviations).
* The triangular swing-height profile — SwingController.swing_height().
* The idea of a contact-phase schedule and of moving the body by moving the
  planted feet in the body frame — Gaits.py / StanceController.py.

NEW (purpose-written for this robot; the donor has no statically stable gait)
-----------------------------------------------------------------------------
* The crawl SEQUENCE itself. The donor ships a trot (contact_phases lifts two
  feet at once) which a 4.8 kg centaur with 25 kg·cm servos and a torso on a
  rail has no business attempting first. This sequencer lifts ONE foot at a
  time and keeps the CoM inside the three-foot support triangle by shifting
  the body laterally first — CRAWL_SHIFT_CENTRED (25.5 mm) and
  CRAWL_STRIDE_HALF (25 mm) straight from interface_constants (via the
  provenance snapshot), which is where the whole 235 mm stance argument was
  fought out.
* The donor->MJCF joint mapping (LegMap). The donor's servo angle convention
  (angle_corrector offsets) is mapped to the exported model's hinge angles by
  a per-joint affine map q = s*theta + c, s in {+1,-1}. The map is CALIBRATED
  against the in-plane leg solve the CAD itself uses (assembly.solve_leg's
  law-of-cosines triangle, whose alpha/knee values ride in the provenance
  snapshot) and then VERIFIED closed-loop: donor IK -> map -> MuJoCo forward
  kinematics must reproduce the commanded foot point over a random grid to
  micron level, or the constructor raises. The donor's own forward_kinematics
  is not used as the oracle because it is internally inconsistent with its IK
  by 0.037 deg (see dingo_ik.py).

THE CYCLE (one full crawl cycle, feet advance 2*CRAWL_STRIDE_HALF each)
-----------------------------------------------------------------------
    shift LEFT + advance      body CoM over the left feet, creep forward
    swing RR, swing FR        the unloaded right side steps, rear first
    shift RIGHT + advance
    swing RL, swing FL
A priming half-cycle (shift right, half-steps for RL/FL) precedes cycle 1 so
the steady-state stride stays inside +/-CRAWL_STRIDE_HALF of neutral — without
it the first left-side stance excursion is 2x the stride and trips the 97%
reach guard, which is exactly the class of bug the guard exists to catch.
"""

import math

import numpy as np

import dingo_ik as DK

LEGS = ("fl", "fr", "rl", "rr")               # actuator/XML order
DONOR_IDX = {"fl": 1, "fr": 0, "rl": 3, "rr": 2}
SIDE = {"fl": +1, "fr": -1, "rl": +1, "rr": -1}       # sy
FORE = {"fl": +1, "fr": +1, "rl": -1, "rr": -1}       # sx


class LegMap:
    """Donor IK -> exported-model joint angles, calibrated then FK-verified."""

    def __init__(self, snap, model, data, mujoco, tol=1e-8, n_grid=40,
                 rng_seed=7):
        self.snap = snap
        self.cfg = DK.DingoConfig(snap)
        self.mm = 1e-3
        self.L1L = snap["L1_LATERAL"] * self.mm
        self.stance = snap["STANCE_Z"] * self.mm
        self.origins = {
            leg: np.array([FORE[leg] * snap["LEG_FB"] * self.mm,
                           SIDE[leg] * snap["LEG_LR"] * self.mm,
                           0.0])
            for leg in LEGS}
        self._calibrate(snap)
        self.max_grid_err = self._verify(model, data, mujoco, tol, n_grid,
                                         rng_seed)

    # ---- calibration anchors: the CAD's own in-plane leg solve ------------
    @staticmethod
    def _planar(px, pz, L2, L3):
        """In-plane 2-link, knee-aft branch — the same law-of-cosines triangle
        as assembly.solve_leg, expressed as MJCF hinge angles. Calibration
        scaffolding only; the donor IK is the solver of record."""
        r2 = px * px + pz * pz
        c3 = (r2 - L2 * L2 - L3 * L3) / (2 * L2 * L3)
        q3 = -math.acos(max(-1.0, min(1.0, c3)))          # knee bends forward
        bend = -q3
        gamma = math.atan2(L3 * math.sin(bend), L2 + L3 * math.cos(bend))
        q2 = math.atan2(-px, -pz) + gamma
        return q2, q3

    def _calibrate(self, snap):
        L2 = snap["L2_THIGH"] * self.mm
        L3 = snap["L3_CALF"] * self.mm
        alpha = math.radians(snap["solve_leg_alpha_deg"])
        knee = math.radians(snap["solve_leg_knee_deg"])

        self.maps = {}
        for leg in LEGS:
            sy = SIDE[leg]
            # anchor A: foot directly below the hip-pitch axis at stance
            tA = np.array([0.0, sy * self.L1L, -self.stance])
            # anchor B: 30 mm forward, same plane
            tB = np.array([0.030, sy * self.L1L, -self.stance])
            thA = DK.leg_explicit_inverse_kinematics(tA, DONOR_IDX[leg],
                                                     self.cfg)
            thB = DK.leg_explicit_inverse_kinematics(tB, DONOR_IDX[leg],
                                                     self.cfg)
            qA = (0.0, alpha, -knee)
            # cross-check anchor A against the planar solve — same triangle
            q2A, q3A = self._planar(0.0, -(self.stance
                                           + snap["L1_VERTICAL"] * self.mm),
                                    L2, L3)
            assert abs(q2A - alpha) < 1e-9 and abs(q3A + knee) < 1e-9, (
                "planar scaffolding disagrees with solve_leg anchor")
            q2B, q3B = self._planar(0.030, -(self.stance
                                             + snap["L1_VERTICAL"] * self.mm),
                                    L2, L3)
            qB = (None, q2B, q3B)

            m = {}
            for j, (qa, qb) in ((1, (qA[1], qB[1])), (2, (qA[2], qB[2]))):
                s = (qb - qa) / (thB[j] - thA[j])
                assert abs(abs(s) - 1.0) < 1e-6, (
                    f"{leg} joint {j}: donor angle is not an affine image, "
                    f"s={s}")
                s = round(s)
                m[j] = (s, qa - s * thA[j])
            # abduction sign resolved by the FK verifier (both tried there)
            m[0] = (None, -thA[0])       # offset assuming s=+1; fixed in verify
            self.maps[leg] = m

    def q_from_theta(self, leg, th):
        m = self.maps[leg]
        s0, c0 = m[0]
        return np.array([s0 * th[0] + c0,
                         m[1][0] * th[1] + m[1][1],
                         m[2][0] * th[2] + m[2][1]])

    def solve(self, leg, r_leg_frame):
        """Foot target relative to the leg's abduction origin (m) -> q(3)."""
        th = DK.leg_explicit_inverse_kinematics(np.asarray(r_leg_frame),
                                                DONOR_IDX[leg], self.cfg)
        return self.q_from_theta(leg, th)

    # ---- closed-loop verification against the exported model --------------
    def _verify(self, model, data, mujoco, tol, n_grid, rng_seed):
        ride = float(model.body("chassis").pos[2])
        assert ride > 0.1, f"chassis ride height {ride} m looks wrong"
        root = np.array([0, 0, ride, 1, 0, 0, 0])

        def fk_err(leg, target, q):
            data.qpos[:] = 0
            data.qpos[0:7] = root
            adr = [model.joint(f"{j}_{leg}").qposadr[0]
                   for j in ("abd", "hip", "knee")]
            for a, v in zip(adr, q):
                data.qpos[a] = v
            mujoco.mj_kinematics(model, data)
            site = data.site(f"foot_site_{leg}").xpos
            world = root[:3] + self.origins[leg] + \
                np.array([0, 0, self.snap["HIP_Z"] * self.mm]) + target
            return np.linalg.norm(site - world)

        rng = np.random.default_rng(rng_seed)
        worst = 0.0
        for leg in LEGS:
            sy = SIDE[leg]
            tA = np.array([0.0, sy * self.L1L, -self.stance])
            thA = DK.leg_explicit_inverse_kinematics(tA, DONOR_IDX[leg],
                                                     self.cfg)
            # resolve the abduction sign on a laterally shifted probe
            tC = tA + np.array([0.0, 0.02, 0.0])
            best = None
            for s0 in (+1, -1):
                self.maps[leg][0] = (s0, -s0 * thA[0])
                e = fk_err(leg, tC, self.solve(leg, tC))
                if best is None or e < best[1]:
                    best = (s0, e)
            self.maps[leg][0] = (best[0], -best[0] * thA[0])
            assert best[1] < tol, (
                f"{leg}: abduction sign unresolved, best err {best[1]:.2e} m")

            n_ok = 0
            while n_ok < n_grid:
                t = tA + rng.uniform((-0.045, -0.045, -0.020),
                                     (0.045, 0.045, 0.020))
                try:
                    q = self.solve(leg, t)
                except DK.ReachError:
                    continue
                e = fk_err(leg, t, q)
                worst = max(worst, e)
                assert e < tol, (f"{leg}: FK closure {e:.3e} m at {t} — "
                                 f"mapping or model frame is wrong")
                n_ok += 1
        return worst


# --------------------------------------------------------------------------
def smooth(u):
    """Quintic ease 0->1, zero velocity and acceleration at both ends."""
    u = min(1.0, max(0.0, u))
    return u * u * u * (10.0 + u * (-15.0 + 6.0 * u))


def tri(u):
    """DONOR swing-height profile (SwingController.swing_height, triangular)."""
    return u / 0.5 if u < 0.5 else (1 - (u - 0.5) / 0.5)


class CrawlPlan:
    """Scripted statically-stable crawl. Each phase carries a SNAPSHOT of the
    body position and all four foot anchors at its start, taken while the plan
    is built — targets(t) only ever interpolates inside the active phase, so
    there is no replay logic to get subtly wrong."""

    T_SHIFT = 1.4
    T_SWING = 1.0
    T_PAUSE = 0.35
    LIFT = 0.025          # m; swing apex. Donor z_clearance is 0.07 for a trot
                          # at 250 stance — far more than a crawl wants here.

    def __init__(self, snap, n_cycles=3, settle=1.0, stand=2.0):
        mm = 1e-3
        self.shift = snap["CRAWL_SHIFT_CENTRED"] * mm     # 25.5 mm
        self.half = snap["CRAWL_STRIDE_HALF"] * mm        # 25 mm
        self.adv = self.half                              # per shift phase
        y_foot = (snap["LEG_LR"] + snap["L1_LATERAL"]) * mm
        x_foot = snap["LEG_FB"] * mm
        self.n_cycles = n_cycles

        feet = {leg: np.array([FORE[leg] * x_foot, SIDE[leg] * y_foot])
                for leg in LEGS}
        body = np.array([0.0, 0.0])
        self.phases = []
        t = 0.0

        def add(kind, dur, **kw):
            nonlocal t
            self.phases.append(dict(
                kind=kind, t0=t, t1=t + dur,
                body0=body.copy(),
                feet0={k: v.copy() for k, v in feet.items()}, **kw))
            t += dur

        def shift_to(dx, y_to):
            b1 = np.array([body[0] + dx, y_to])
            add("shift", self.T_SHIFT, b1=b1)
            body[:] = b1

        def swing(leg, step):
            f1 = feet[leg] + np.array([step, 0.0])
            add("swing", self.T_SWING, leg=leg, f1=f1)
            feet[leg][:] = f1
            add("pause", self.T_PAUSE)

        add("settle", settle)
        add("stand", stand)
        # priming half-cycle (see module docstring)
        shift_to(0.0, -self.shift)
        swing("rl", self.half)
        swing("fl", self.half)
        for i in range(n_cycles):
            add("mark", 0.0, cycle=i)
            shift_to(self.adv, +self.shift)
            swing("rr", 2 * self.half)
            swing("fr", 2 * self.half)
            shift_to(self.adv, -self.shift)
            swing("rl", 2 * self.half)
            swing("fl", 2 * self.half)
        shift_to(0.0, 0.0)
        add("stand", 1.0)

        self.total = t
        self.stand_window = (settle * 0.5, settle + stand)
        self.crawl_start = settle + stand
        self.expected_advance = n_cycles * 2 * self.adv

    def phase_at(self, t):
        for ph in self.phases:
            if t < ph["t1"] and ph["t1"] > ph["t0"]:
                return ph
        return self.phases[-1]

    def targets(self, t):
        """-> (body_xy, {leg: xyz world target}, {leg: in_stance}, label)"""
        ph = self.phase_at(t)
        u = (t - ph["t0"]) / (ph["t1"] - ph["t0"])
        body = ph["body0"].copy()
        feet3 = {leg: np.array([*ph["feet0"][leg], 0.0]) for leg in LEGS}
        stance = {leg: True for leg in LEGS}
        label = ph["kind"]
        if ph["kind"] == "shift":
            body = body + smooth(u) * (ph["b1"] - ph["body0"])
        elif ph["kind"] == "swing":
            leg = ph["leg"]
            label = f"swing {leg}"
            s = smooth(u)
            xy = ph["feet0"][leg] + s * (ph["f1"] - ph["feet0"][leg])
            feet3[leg] = np.array([*xy, self.LIFT * tri(u)])
            stance[leg] = False
        return body, feet3, stance, label

