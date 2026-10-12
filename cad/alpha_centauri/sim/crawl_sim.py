"""Alpha Centauri — THE crawl experiment: both waist-rail stations, in MuJoCo.

    MUJOCO_GL=egl .venv/bin/python cad/alpha_centauri/sim/crawl_sim.py

Runs under .venv (mujoco), NEVER the CAD interpreter. Consumes ONLY what
mjcf_export.py wrote to output/sim/ — the XMLs and the provenance snapshot.
If interface_constants.py has drifted since the export, the SNAPSHOT wins
(the XML is baked from it); the drift is detected and reported, not hidden.

WHAT THIS TESTS (design log §5.4: "First simulation should be the crawl at both
rail positions. It is the single claim the whole layout rests on."):

  E1  static stand at both stations — torque per joint vs the 2.4516 N·m
      measured limit (25 kg·cm MEASURED; the 50 kg·cm datasheet peak is
      never used — law).
  E2  THE CRAWL at WALK (torso x=+37): statically stable one-foot-at-a-time
      crawl, 25.5 mm lateral shift, 25 mm stride half-amplitude. Metrics:
      distance over N cycles, falls, minimum support-polygon margin, peak
      torque per joint.
  E3  THE CRAWL at WORK (torso x=+167): EXPECTED TO FAIL — the CoM sits
      ~+46 mm forward, so a front-foot lift loses the support triangle.
      The failure is demonstrated and quantified; it is evidence the mode
      logic is right. If it crawls anyway, that gets reported too.
  E4  BRAIN PLACEMENT A/B — evidence for the pending layout decision
      (design log §6), decided by NOBODY here: baseline (brain in the chest, as
      drawn) vs variant (brain moved to the rear chassis — the lump moved
      aft from the highest mass). The lump was a 300 g Jetson until
      REPLAN-2026-08-28; it is the 215 g phone stack (balance.PHONE_ETC)
      since 2026-09-22. CoM shift and crawl-margin delta.

Support-polygon margin is computed against MEASURED CONTACT points and the
MEASURED whole-robot CoM every step — the polygon vertices are the foot
spheres' centre xy (a sphere on flat ground contacts straight below its
centre, so the centre's horizontal position IS the contact xy). The IK foot
SITE at L3 on the calf axis is NOT used: at crawl calf angles it sits ~5 mm
horizontally off the contact, the same direction on all four legs — a
flattering bias; interface_constants' own foot-sphere note ("the centre is
not the foot position") names exactly this trap. The planner's stance set
only says which feet to include. Samples where fewer than 3 planner-stance
feet actually touch are excluded from the min-margin figures and REPORTED
first-class as deficient-contact time (seconds and % of the crawl) next to
every min-margin number. Falls are detected on the measured root pose.

All renders are offscreen (EGL; no interactive viewer is ever launched).
"""

import json
import math
import os
import sys
from pathlib import Path

os.environ.setdefault("MUJOCO_GL", "egl")

import imageio.v2 as imageio          # noqa: E402
import matplotlib                     # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt       # noqa: E402
import mujoco                         # noqa: E402
import numpy as np                    # noqa: E402

HERE = Path(__file__).parent
CAD = HERE.parent
SIM_OUT = CAD / "output" / "sim"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(CAD))

import crawl_gait as G                # noqa: E402
from crawl_gait import LEGS, CrawlPlan, LegMap  # noqa: E402

# ---- chart tokens (validated palette) -------------------------------------
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
GRID = "#e7e6e2"
SERIES = {"fl": "#2a78d6", "fr": "#eb6834", "rl": "#1baf7a", "rr": "#eda100"}
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
RED_STATUS = "#e34948"                # reserved: the torque limit / falls

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "text.color": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "font.size": 9, "axes.titlesize": 10, "figure.dpi": 150,
    "axes.spines.top": False, "axes.spines.right": False,
})

CTRL_DT = 0.01          # 100 Hz — the donor's own control rate (Config.dt)
LOG_EVERY = 2           # log every 2nd physics step (250 Hz)


# --------------------------------------------------------------------------
def load_provenance():
    prov = json.loads((SIM_OUT / "provenance.json").read_text())
    snap = prov["constants_snapshot"]
    drift = {}
    try:
        import interface_constants as IC_live
        for k, v in snap.items():
            live = getattr(IC_live, k, None)
            if isinstance(live, (int, float)) and abs(live - v) > 1e-9:
                drift[k] = {"snapshot": v, "live": live}
    except Exception as e:                              # pragma: no cover
        drift["_import_error"] = str(e)
    if drift:
        print(f"WARNING: interface_constants drifted since export: {drift}\n"
              f"         the SNAPSHOT governs this run (the XML is baked).")
    return prov, snap, drift


def polygon_margin(feet_xy, p):
    """Signed distance (m) from point p to the support polygon boundary:
    positive inside, negative outside. Vertices get sorted CCW about their
    centroid (3 or 4 stance feet, always convex here). NaN when fewer than
    3 planner-stance feet are actually touching (unload/touchdown
    transients, or the robot rocking onto 2 feet) — those samples are
    excluded from every min, and the excluded TIME is reported first-class
    (seconds and %) beside every min-margin figure, never hidden."""
    pts = np.asarray(feet_xy)
    if len(pts) < 3:
        return np.nan
    c = pts.mean(axis=0)
    order = np.argsort(np.arctan2(pts[:, 1] - c[1], pts[:, 0] - c[0]))
    pts = pts[order]
    d = []
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        e = b - a
        d.append(np.cross(e, p - a) / np.linalg.norm(e))
    d = np.array(d)
    return d.min()      # CCW ordering makes inward positive


class Runner:
    def __init__(self, variant, snap, kp=None, kv=None):
        self.variant = variant
        self.snap = snap
        self.model = mujoco.MjModel.from_xml_path(
            str(SIM_OUT / f"alpha_centauri_{variant}.xml"))
        if kp is not None:      # servo-stiffness sensitivity: override gains
            self.model.actuator_gainprm[:, 0] = kp
            self.model.actuator_biasprm[:, 1] = -kp
            self.model.actuator_biasprm[:, 2] = -(kv if kv else 2.0)
        self.data = mujoco.MjData(self.model)
        self.ride = float(self.model.body("chassis").pos[2])
        self.chassis_id = self.model.body("chassis").id
        self.map = LegMap(snap, self.model, mujoco.MjData(self.model), mujoco)
        self.floor_id = self.model.geom("floor").id
        self.foot_geom = {leg: self.model.geom(f"foot_{leg}").id
                          for leg in LEGS}
        self.act_idx = {}
        for i, leg in enumerate(LEGS):
            for j, jn in enumerate(("abd", "hip", "knee")):
                self.act_idx[(leg, jn)] = self.model.actuator(
                    f"{jn}_{leg}").id
        self.tau_names = [f"{j}_{leg}" for leg in LEGS
                          for j in ("abd", "hip", "knee")]

    def ctrl_from_plan(self, plan, t):
        body, feet3, stance, label = plan.targets(t)
        ctrl = np.zeros(self.model.nu)
        abd_z = self.snap["HIP_Z"] / 1000.0 + self.ride   # abduction plane, world
        for leg in LEGS:
            o = self.map.origins[leg]
            r = np.array([feet3[leg][0] - (body[0] + o[0]),
                          feet3[leg][1] - (body[1] + o[1]),
                          feet3[leg][2] - abd_z])
            q = self.map.solve(leg, r)
            for j, jn in enumerate(("abd", "hip", "knee")):
                ctrl[self.act_idx[(leg, jn)]] = q[j]
        return ctrl, stance, label

    def init_pose(self, plan):
        d = self.data
        mujoco.mj_resetData(self.model, d)
        ctrl, _, _ = self.ctrl_from_plan(plan, 0.0)
        d.qpos[:] = 0
        d.qpos[2] = self.ride + 0.002
        d.qpos[3] = 1.0
        for leg in LEGS:
            for j, jn in enumerate(("abd", "hip", "knee")):
                adr = self.model.joint(f"{jn}_{leg}").qposadr[0]
                d.qpos[adr] = ctrl[self.act_idx[(leg, jn)]]
        d.ctrl[:] = ctrl
        mujoco.mj_forward(self.model, d)

    def feet_contact(self):
        touching = {leg: False for leg in LEGS}
        for i in range(self.data.ncon):
            c = self.data.contact[i]
            pair = {c.geom1, c.geom2}
            if self.floor_id in pair:
                for leg, gid in self.foot_geom.items():
                    if gid in pair:
                        touching[leg] = True
        return touching

    def run(self, plan, tag, frames_at=(), frame_cam="iso",
            frame_size=(600, 800), video=None, video_fps=25,
            video_size=(480, 640), periodic_frames=None):
        m, d = self.model, self.data
        self.init_pose(plan)
        renderer = mujoco.Renderer(m, *frame_size)
        vrend = mujoco.Renderer(m, *video_size) if video else None
        vwriter = imageio.get_writer(video, fps=video_fps) if video else None

        log = {k: [] for k in ("t", "com", "rootz", "rpy", "tau", "margin",
                               "label", "stance_n")}
        frames, periodic = [], []
        frames_due = sorted(frames_at)
        fi = 0
        next_ctrl = 0.0
        next_video = 0.0
        next_periodic = 0.0
        fall_t = None
        stance = {leg: True for leg in LEGS}
        label = "settle"
        t_end = plan.total
        step = 0

        while d.time < t_end:
            if d.time >= next_ctrl:
                ctrl, stance, label = self.ctrl_from_plan(plan, d.time)
                d.ctrl[:] = ctrl
                next_ctrl += CTRL_DT
            mujoco.mj_step(m, d)
            step += 1

            if step % LOG_EVERY == 0:
                com = d.subtree_com[self.chassis_id].copy()
                quat = d.qpos[3:7]
                # roll/pitch from quaternion
                w, x, y, z = quat
                roll = math.atan2(2 * (w * x + y * z),
                                  1 - 2 * (x * x + y * y))
                pitch = math.asin(max(-1, min(1, 2 * (w * y - z * x))))
                touching = self.feet_contact()
                stance_feet = [leg for leg in LEGS
                               if stance[leg] and touching[leg]]
                # polygon vertices = CONTACT xy: the foot-sphere CENTRE's
                # horizontal position (a sphere on flat ground contacts
                # straight below its centre). NOT the IK foot site at L3 on
                # the calf axis — at ~21° of calf tilt that site sits
                # ~5.4 mm horizontally off the contact, the same direction
                # on all four legs, a flattering bias the metric must not
                # have (interface_constants' foot-sphere note names this
                # trap: "the centre is not the foot position").
                feet_xy = [d.geom_xpos[self.foot_geom[leg]][:2].copy()
                           for leg in stance_feet]
                margin = polygon_margin(feet_xy, com[:2])
                log["t"].append(d.time)
                log["com"].append(com)
                log["rootz"].append(d.qpos[2])
                log["rpy"].append((roll, pitch))
                log["tau"].append(d.actuator_force.copy())
                log["margin"].append(margin)
                log["label"].append(label)
                log["stance_n"].append(len(stance_feet))

                if fall_t is None and (abs(roll) > 0.35 or abs(pitch) > 0.35
                                       or d.qpos[2] < 0.55 * self.ride):
                    fall_t = d.time
                    t_end = min(t_end, d.time + 0.8)   # capture the fall, stop

            if fi < len(frames_due) and d.time >= frames_due[fi]:
                renderer.update_scene(d, camera=frame_cam)
                frames.append((d.time, label, renderer.render().copy()))
                fi += 1
            if periodic_frames and d.time >= next_periodic:
                renderer.update_scene(d, camera=frame_cam)
                periodic.append((d.time, label, renderer.render().copy()))
                next_periodic += periodic_frames
            if vwriter and d.time >= next_video:
                vrend.update_scene(d, camera=frame_cam)
                vwriter.append_data(vrend.render())
                next_video += 1.0 / video_fps

        if vwriter:
            vwriter.close()
            vrend.close()
        renderer.close()

        for k in ("t", "com", "rootz", "rpy", "tau", "margin", "stance_n"):
            log[k] = np.array(log[k])

        t = log["t"]
        stand_w = (t >= plan.stand_window[0]) & (t <= plan.stand_window[1])
        crawl_w = t >= plan.crawl_start
        if fall_t is not None:
            crawl_w &= t <= fall_t
        tau = np.abs(log["tau"])
        x0 = log["com"][stand_w][:, 0].mean() if stand_w.any() else np.nan
        res = {
            "variant": self.variant, "tag": tag,
            "fall_t": fall_t,
            "fall_label": (log["label"][int(np.searchsorted(t, fall_t))]
                           if fall_t is not None else None),
            "stand": {
                "com_mm": (log["com"][stand_w].mean(0) * 1000).round(2).tolist(),
                "root_z_mm": round(float(log["rootz"][stand_w].mean()) * 1000, 1),
                "tau_mean": tau[stand_w].mean(0).round(4).tolist(),
                "tau_max": tau[stand_w].max(0).round(4).tolist(),
            },
            "crawl": None,
        }
        if crawl_w.any():
            labels = np.array(log["label"], dtype=object)
            mg = log["margin"]
            m3 = mg[crawl_w & (log["stance_n"] == 3)]
            limit = self.snap["TORQUE_LIMIT_NM"]
            sat = {}
            for j, name in enumerate(self.tau_names):
                f = float((tau[crawl_w][:, j] >= 0.99 * limit).mean())
                if f > 0:
                    sat[name] = round(f, 4)
            swing_min = {}
            for leg in LEGS:
                mask = crawl_w & (labels == f"swing {leg}")
                vals = mg[mask]
                vals = vals[np.isfinite(vals)]
                if len(vals):
                    swing_min[leg] = round(float(vals.min()) * 1000, 1)
            fin = mg[crawl_w]
            fin = fin[np.isfinite(fin)]
            # Deficient-contact time: samples where <3 planner-stance feet
            # touch. Excluded from every min above — so it is REPORTED as a
            # first-class result (s and % of the crawl), never hidden in a
            # raw counter.
            n_crawl = int(crawl_w.sum())
            n_def = int(np.isnan(mg[crawl_w]).sum())
            log_dt = self.model.opt.timestep * LOG_EVERY
            res["crawl"] = {
                "distance_mm": round((log["com"][crawl_w][-1, 0]
                                      - log["com"][crawl_w][0, 0]) * 1000, 1),
                "expected_mm": round(plan.expected_advance * 1000, 1),
                "min_margin_mm": (round(float(fin.min()) * 1000, 1)
                                  if len(fin) else None),
                "min_margin_3ft_mm": (round(float(np.nanmin(m3)) * 1000, 1)
                                      if np.isfinite(m3).any() else None),
                "min_margin_per_swing_mm": swing_min,
                "deficient_contact_samples": n_def,
                "deficient_contact_s": round(n_def * log_dt, 2),
                "deficient_contact_pct": (round(100.0 * n_def / n_crawl, 1)
                                          if n_crawl else None),
                "tau_max": tau[crawl_w].max(0).round(4).tolist(),
                "saturated_joints_frac": sat,
                "completed": fall_t is None,
            }
        return res, log, frames, periodic


# --------------------------------------------------------------------------
# figures
# --------------------------------------------------------------------------
def contact_sheet_times(plan, cycle=1):
    """Mid-phase capture times across one full cycle: start, both shifts,
    all four swings, end — 8 frames."""
    marks = [p for p in plan.phases if p["kind"] == "mark"]
    ph = [p for p in plan.phases
          if marks[cycle]["t0"] <= p["t0"]
          and p["t0"] < (marks[cycle + 1]["t0"] if cycle + 1 < len(marks)
                         else plan.total)]
    times = [marks[cycle]["t0"] + 0.02]
    for p in ph:
        if p["kind"] in ("shift", "swing"):
            times.append(0.5 * (p["t0"] + p["t1"]))
    times.append(ph[-1]["t1"] - 0.02)
    return times[:8]


def save_sheet(frames, path, title, ncols=4):
    n = len(frames)
    nrows = math.ceil(n / ncols)
    fig, axes = plt.subplots(nrows, ncols,
                             figsize=(3.1 * ncols, 2.5 * nrows + 0.4))
    for ax, (t, label, img) in zip(np.ravel(axes), frames):
        ax.imshow(img)
        ax.set_title(f"t={t:.1f}s  {label}", fontsize=8, color=INK2)
        ax.axis("off")
    for ax in np.ravel(axes)[n:]:
        ax.axis("off")
    fig.suptitle(title, fontsize=11, color=INK)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  wrote {path.name}")


def com_support_figure(log, plan, res, path):
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11, 4.6),
                                  gridspec_kw={"width_ratios": [1, 1.35]})
    t = log["t"]
    crawl = t >= plan.crawl_start
    com = log["com"][crawl] * 1000

    # support triangles at each swing mid-phase (all cycles, light fills)
    for p in plan.phases:
        if p["kind"] != "swing":
            continue
        tm = 0.5 * (p["t0"] + p["t1"])
        body, feet3, stance, _ = plan.targets(tm)
        pts = np.array([feet3[leg][:2] for leg in LEGS if stance[leg]]) * 1000
        c = pts.mean(0)
        order = np.argsort(np.arctan2(*(pts - c).T[::-1]))
        col = SERIES[p["leg"]]
        ax.fill(pts[order, 0], pts[order, 1], color=col, alpha=0.10,
                ec=col, lw=0.7, zorder=1)
    ax.plot(com[:, 0], com[:, 1], color=INK, lw=1.8, zorder=5)
    ax.plot(com[0, 0], com[0, 1], "o", color=INK, ms=5, zorder=6)
    ax.annotate("CoM start", (com[0, 0], com[0, 1]),
                textcoords="offset points", xytext=(-14, 14), fontsize=8)
    ax.annotate("end", (com[-1, 0], com[-1, 1]),
                textcoords="offset points", xytext=(6, -10), fontsize=8)
    for leg in LEGS:
        o = np.array([G.FORE[leg] * plan_leg_x(plan), G.SIDE[leg] *
                      plan_leg_y(plan)]) * 1000
        ax.plot(*o, "s", color=SERIES[leg], ms=7, zorder=4)
        ax.annotate(leg.upper(), o, textcoords="offset points",
                    xytext=(6, 4), fontsize=8, color=INK)
    ax.axvline(0, color=GRID, lw=0.8)
    ax.set_xlabel("x fore-aft (mm)")
    ax.set_ylabel("y lateral (mm)")
    ax.set_title("CoM path over support triangles (top view)")
    ax.set_aspect("equal")

    mg = log["margin"] * 1000
    ax2.plot(t[crawl], mg[crawl], color=BLUE, lw=1.6)
    ax2.axhline(0, color=RED_STATUS, lw=1.0, ls="--")
    ax2.annotate("tip boundary", (t[crawl][0], 0),
                 textcoords="offset points", xytext=(4, 4),
                 fontsize=8, color=RED_STATUS)
    three = crawl & (log["stance_n"] == 3)
    if three.any():
        i = np.argmin(np.where(three, mg, np.inf))
        ax2.plot(t[i], mg[i], "o", color=BLUE, ms=5)
        ax2.annotate(f"min 3-foot margin {mg[i]:.1f} mm",
                     (t[i], mg[i]), textcoords="offset points",
                     xytext=(8, -12), fontsize=8)
    ax2.set_xlabel("time (s)")
    ax2.set_ylabel("support-polygon margin (mm)")
    d = res["crawl"]
    ax2.set_title(f"margin vs time — distance {d['distance_mm']:.0f} mm "
                  f"(scripted {d['expected_mm']:.0f}), falls: "
                  f"{0 if d['completed'] else 1}\n"
                  f"deficient-contact (excluded from min): "
                  f"{d['deficient_contact_s']:.1f} s "
                  f"({d['deficient_contact_pct']:.1f}% of crawl)")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  wrote {path.name}")


def plan_leg_x(plan):
    return abs(plan.phases[0]["feet0"]["fl"][0])


def plan_leg_y(plan):
    return abs(plan.phases[0]["feet0"]["fl"][1])


def torque_figure(res_walk, res_work, tau_names, limit, path):
    x = np.arange(len(tau_names))
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(10, 6.2), sharex=True)
    w = 0.38
    ax.bar(x - w / 2, res_walk["stand"]["tau_max"], w, color=BLUE,
           label="stand @ WALK (torso x=+37)")
    ax.bar(x + w / 2, res_work["stand"]["tau_max"], w, color=ORANGE,
           label="stand @ WORK (torso x=+167)")
    ax.axhline(limit, color=RED_STATUS, lw=1.2, ls="--")
    ax.annotate(f"measured servo limit {limit:.3f} N·m (25 kg·cm)",
                (0, limit), textcoords="offset points", xytext=(2, 4),
                fontsize=8, color=RED_STATUS)
    ax.set_ylabel("|torque| (N·m)")
    ax.set_title("E1 — static stand, peak joint torque over the 2 s window")
    ax.legend(frameon=False, fontsize=8)
    ax.set_ylim(0, limit * 1.15)

    cw = res_walk["crawl"]["tau_max"]
    ax2.bar(x, cw, 0.55, color=BLUE)
    for xi, v in zip(x, cw):
        ax2.annotate(f"{v:.2f}", (xi, v), ha="center",
                     textcoords="offset points", xytext=(0, 2), fontsize=7,
                     color=INK2)
    ax2.axhline(limit, color=RED_STATUS, lw=1.2, ls="--")
    ax2.set_ylabel("|torque| (N·m)")
    ax2.set_title("E2 — crawl @ WALK, peak joint torque over 3 cycles")
    ax2.set_xticks(x, [n.replace("_", "\n") for n in tau_names], fontsize=7)
    ax2.set_ylim(0, limit * 1.15)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  wrote {path.name}")


def work_evidence_figure(res_walk, log_walk, plan_walk,
                         res_work, log_work, plan_work, periodic, path):
    """THE WORK-station evidence: the worst front-foot-lift instant (render)
    beside the margin traces of both stations. If the run fell, the frame is
    the fall; if it survived, the frame is the near-zero-margin moment —
    either way the picture shows what the mode logic is protecting against."""
    t = log_work["t"]
    labels = np.array(log_work["label"], dtype=object)
    crawl = t >= plan_work.crawl_start
    mg = log_work["margin"] * 1000
    front = crawl & ((labels == "swing fl") | (labels == "swing fr")) \
        & np.isfinite(log_work["margin"])
    if res_work["fall_t"] is not None:
        t_pick = res_work["fall_t"] + 0.5
        pick_note = f"fall during '{res_work['fall_label']}'"
        m_worst = None
    else:
        i = int(np.argmin(np.where(front, mg, np.inf)))
        t_pick, m_worst = t[i], mg[i]
        pick_note = f"margin {m_worst:.1f} mm during '{labels[i]}'"
    frame = min(periodic, key=lambda f: abs(f[0] - t_pick))

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(11, 4.4),
                                  gridspec_kw={"width_ratios": [1, 1.25]})
    ax.imshow(frame[2])
    ax.axis("off")
    ax.set_title(f"WORK station, t={frame[0]:.1f}s — {pick_note}", fontsize=9)

    tw = log_walk["t"]
    cw = tw >= plan_walk.crawl_start
    (lw_walk,) = ax2.plot(tw[cw] - plan_walk.crawl_start,
                          log_walk["margin"][cw] * 1000, color=BLUE, lw=1.5)
    (lw_work,) = ax2.plot(t[crawl] - plan_work.crawl_start, mg[crawl],
                          color=ORANGE, lw=1.5)
    ax2.axhline(0, color=RED_STATUS, lw=1.0, ls="--")
    ax2.annotate("tip boundary", (0.995, 0.055), xycoords="axes fraction",
                 fontsize=8, color=RED_STATUS, ha="right", va="bottom")
    w3 = res_walk["crawl"]["min_margin_3ft_mm"]
    k3 = res_work["crawl"]["min_margin_3ft_mm"]
    wd = res_walk["crawl"]["deficient_contact_s"]
    kd = res_work["crawl"]["deficient_contact_s"]
    kdp = res_work["crawl"]["deficient_contact_pct"]
    sat = ", ".join(res_work["crawl"]["saturated_joints_frac"]) or "none"
    # Headroom first, THEN the legend: a label pinned into the data area
    # overprints the traces (it did, at 0.93 axes-fraction, straight through the
    # WORK plateau). Reserve the space instead of competing for it.
    lo, hi = ax2.get_ylim()
    ax2.set_ylim(lo, hi + 0.30 * (hi - lo))
    ax2.legend([lw_walk, lw_work],
               ["WALK station (torso x=+37) — no saturated servos",
                f"WORK station (torso x=+167) — saturated servos: {sat}"],
               loc="upper center", ncol=1, fontsize=8, frameon=True,
               framealpha=0.92, edgecolor="none", handlelength=1.6)
    ax2.set_title(f"min 3-foot margin: {w3} mm WALK vs {k3} mm WORK\n"
                  f"deficient contact excluded: WALK {wd:.1f} s, "
                  f"WORK {kd:.1f} s ({kdp:.1f} %)", fontsize=9)
    ax2.set_xlabel("time since crawl start (s)")
    ax2.set_ylabel("support-polygon margin (mm)")
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  wrote {path.name}")


def brain_figure(all_res, com_heights, path):
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.2))
    combos = [("walk_chest", "WALK / chest"), ("walk_aft", "WALK / aft"),
              ("work_chest", "WORK / chest"), ("work_aft", "WORK / aft")]
    ys = np.arange(len(combos))[::-1]
    for y, (v, lab) in zip(ys, combos):
        cx = all_res[v]["stand"]["com_mm"][0]
        col = BLUE if "chest" in v else ORANGE
        ax.plot([0, cx], [y, y], color=GRID, lw=2, zorder=1)
        ax.plot(cx, y, "o", color=col, ms=9, zorder=3)
        ax.annotate(f"{cx:+.1f} mm", (cx, y), textcoords="offset points",
                    xytext=(8, -3), fontsize=8, color=INK)
    ax.axvline(0, color=RED_STATUS, lw=1.0, ls="--")
    ax.annotate("crawl boundary\n(wheelbase midpoint)", (0, ys[-1] - 0.45),
                fontsize=7.5, color=RED_STATUS, ha="center")
    ax.set_yticks(ys, [lab for _, lab in combos])
    ax.set_xlabel("standing CoM x (mm, measured in sim)")
    ax.set_title("brain (phone) A/B — CoM by station and brain location")

    labels, vals, cols, sats, defs = [], [], [], [], []
    for v, lab in (("walk_chest", "WALK\nchest"), ("walk_aft", "WALK\naft"),
                   ("work_chest", "WORK\nchest"), ("work_aft", "WORK\naft")):
        c = all_res[v]["crawl"]
        labels.append(lab)
        vals.append(c["min_margin_3ft_mm"])
        cols.append(BLUE if "chest" in v else ORANGE)
        sats.append(bool(c["saturated_joints_frac"]))
        defs.append(c["deficient_contact_s"])
    b = ax2.bar(labels, vals, 0.55, color=cols)
    for rect, v, s, ds in zip(b, vals, sats, defs):
        note = f"{v:.1f} mm" + (f"\n{ds:.1f}s def." if ds else "") \
            + ("\nservo sat." if s else "")
        ax2.annotate(note, (rect.get_x() + rect.get_width() / 2, v),
                     ha="center", textcoords="offset points", xytext=(0, 3),
                     fontsize=8.5, color=INK)
    ax2.set_ylabel("min 3-foot crawl margin (mm)")
    ax2.axhline(0, color=RED_STATUS, lw=1.0, ls="--")
    ax2.set_ylim(min(0.0, min(vals) * 1.3) - 1.0, max(vals) * 1.3)
    dz = com_heights["walk_chest"] - com_heights["walk_aft"]
    ax2.set_title(f"crawl margin by station — brain aft: CoM {dz:.1f} mm "
                  f"lower", fontsize=9.5)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  wrote {path.name}")


# --------------------------------------------------------------------------
def main():
    prov, snap, drift = load_provenance()
    import interface_constants as IC          # pure-math module, venv-safe
    limit = snap["TORQUE_LIMIT_NM"]
    all_res, com_heights = {}, {}
    figs = SIM_OUT

    # ---------------- E1 + E2: WALK, brain in chest (baseline) ------------
    print("== E2  crawl @ WALK (brain chest) ==")
    r = Runner("walk_chest", snap)
    print(f"  IK->FK closed-loop grid max err {r.map.max_grid_err:.2e} m")
    plan = CrawlPlan(snap, n_cycles=3)
    res, log, frames, _ = r.run(
        plan, "crawl", frames_at=contact_sheet_times(plan),
        video=str(figs / "crawl_walk.mp4"))
    res["ik_grid_max_err_m"] = r.map.max_grid_err
    all_res["walk_chest"] = res
    com_heights["walk_chest"] = res["stand"]["com_mm"][2]
    save_sheet(frames, figs / "crawl_walk_contactsheet.png",
               "Alpha Centauri — statically stable crawl at WALK "
               "(cycle 2 of 3, torso x=+37, one foot at a time)")
    com_support_figure(log, plan, res, figs / "com_support_walk.png")
    print(json.dumps(res["crawl"], indent=1))

    # ---------------- E3: WORK, expected to fail ---------------------------
    print("== E3  crawl @ WORK (brain chest) — failure expected ==")
    rw = Runner("work_chest", snap)
    planw = CrawlPlan(snap, n_cycles=2)
    resw, logw, _, periodic = rw.run(
        planw, "crawl", periodic_frames=0.20,
        video=str(figs / "crawl_work.mp4"))
    all_res["work_chest"] = resw
    com_heights["work_chest"] = resw["stand"]["com_mm"][2]
    # quantify: measured CoM x, boundary math, and the reach cost of fixing it.
    # Lifting a front foot, the binding diagonal crosses the centreline at the
    # wheelbase midpoint; a CoM x_com forward of it needs an EXTRA lateral
    # shift of x_com * (track/2) / (wheelbase/2) just to get BACK to zero
    # margin, on top of the CRAWL_SHIFT_CENTRED that buys the working margin.
    x_com = resw["stand"]["com_mm"][0]
    y_track = snap["LEG_LR"] + snap["L1_LATERAL"]
    shift_zero = x_com * y_track / snap["LEG_FB"]          # zero-margin shift
    shift_recover = shift_zero + snap["CRAWL_SHIFT_CENTRED"]
    ext_needed = IC.extension_at(snap["STANCE_Z"], shift_recover,
                                 snap["CRAWL_STRIDE_HALF"])
    resw["work_failure_math"] = {
        "measured_stand_com_x_mm": x_com,
        "shift_used_mm": snap["CRAWL_SHIFT_CENTRED"],
        "lateral_shift_for_zero_margin_mm": round(shift_zero, 1),
        "lateral_shift_for_walk_margin_mm": round(shift_recover, 1),
        "extension_at_recovery_shift_mm": round(ext_needed, 2),
        "extension_pct_of_reach": round(100 * ext_needed
                                        / snap["LEG_REACH_MAX"], 1),
        "extension_limit_mm": round(snap["LEG_EXTENSION_LIMIT"], 2),
        "recovery_exceeds_guard": bool(ext_needed
                                       > snap["LEG_EXTENSION_LIMIT"]),
    }
    print(json.dumps({k: resw[k] for k in ("fall_t", "fall_label",
                                           "work_failure_math")}, indent=1))
    work_evidence_figure(res, log, plan, resw, logw, planw, periodic,
                         figs / "work_failure_strip.png")

    # ---------------- E4: brain aft A/B ------------------------------------
    print("== E4  brain (phone) placement A/B ==")
    ra = Runner("walk_aft", snap)
    plana = CrawlPlan(snap, n_cycles=3)
    resa, loga, _, _ = ra.run(plana, "crawl")
    all_res["walk_aft"] = resa
    com_heights["walk_aft"] = resa["stand"]["com_mm"][2]
    print(json.dumps(resa["crawl"], indent=1))

    rwa = Runner("work_aft", snap)
    planwa = CrawlPlan(snap, n_cycles=2)
    reswa, _, _, _ = rwa.run(planwa, "crawl")
    all_res["work_aft"] = reswa
    com_heights["work_aft"] = reswa["stand"]["com_mm"][2]

    torque_figure(all_res["walk_chest"], all_res["work_chest"],
                  r.tau_names, limit, figs / "torque_vs_limit.png")
    brain_figure(all_res, com_heights, figs / "brain_ab.png")

    # ------- E5: servo-stiffness sensitivity — kp is an ASSUMPTION ---------
    # The WORK-station verdict rides on how far the body settles under servo
    # droop (softer servos let the CoM sag aft, flattering WORK). Re-run both
    # stations with a much stiffer position gain to see which conclusions are
    # gain-sensitive. kp=280 ~ full torque at 0.5 deg of error.
    print("== E5  servo-stiffness sensitivity (kp 280 vs assumed 60) ==")
    sens = {}
    # KNOWN CONFOUND, stated rather than hidden: this sweep runs 2 cycles to keep
    # it cheap. The WORK baseline above is also 2 cycles, so the WORK pair is
    # like-for-like; the WALK baseline is 3 cycles, so the WALK pair changes gain
    # AND run length together. A minimum over 2 cycles has fewer chances to find
    # a low margin than one over 3, so part of WALK's 15.0 -> 16.6 mm move is run
    # length, not gain. Read the WALK row as indicative and the WORK row as the
    # controlled comparison. Raising this to 3 would change the committed
    # sensitivity_kp280 numbers in docs/evidence/sim_results.json.
    for v in ("walk_chest", "work_chest"):
        rs = Runner(v, snap, kp=280.0, kv=6.0)
        resS, _, _, _ = rs.run(CrawlPlan(snap, n_cycles=2), "crawl_kp280")
        sens[v] = resS
        c = resS["crawl"]
        print(f"  {v} kp280: {'OK' if c['completed'] else 'FELL'} "
              f"dist {c['distance_mm']:.0f} mm, min 3ft margin "
              f"{c['min_margin_3ft_mm']} mm (deficient-contact "
              f"{c['deficient_contact_s']:.1f} s = "
              f"{c['deficient_contact_pct']:.1f}%), stand CoM x "
              f"{resS['stand']['com_mm'][0]:+.1f} mm, saturated: "
              f"{list(c['saturated_joints_frac']) or '-'}")

    # ---------------- results ----------------------------------------------
    def _san(o):
        if isinstance(o, dict):
            return {k: _san(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [_san(v) for v in o]
        if isinstance(o, float) and not math.isfinite(o):
            return None
        return o

    out = {
        "provenance_generated": prov["generated"],
        "constants_drift_since_export": drift,
        "torque_limit_Nm": limit,
        "tau_names": r.tau_names,
        "runs": all_res,
        "sensitivity_kp280": sens,
        "com_heights_mm": com_heights,
    }
    (figs / "results.json").write_text(json.dumps(_san(out), indent=1))
    print(f"\nresults.json written to {figs}")

    print("\n================ SUMMARY ================")
    for v in ("walk_chest", "work_chest", "walk_aft", "work_aft"):
        res = all_res[v]
        c = res["crawl"]
        stand_pk = max(res["stand"]["tau_max"])
        line = (f"{v:12s} stand CoM x {res['stand']['com_mm'][0]:+7.1f} mm, "
                f"peak stand tau {stand_pk:.3f} Nm")
        if c:
            line += (f" | crawl: {'OK' if c['completed'] else 'FELL'} "
                     f"dist {c['distance_mm']:.0f} mm, "
                     f"min 3ft margin {c['min_margin_3ft_mm']} mm, "
                     f"deficient-contact {c['deficient_contact_s']:.1f} s "
                     f"({c['deficient_contact_pct']:.1f}%), "
                     f"peak tau {max(c['tau_max']):.3f} Nm, "
                     f"saturated: {list(c['saturated_joints_frac']) or '-'}")
        print(line)


if __name__ == "__main__":
    main()
