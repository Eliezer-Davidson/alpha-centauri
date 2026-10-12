#!/usr/bin/env python3
"""Score build orientations for the TonyPi frame parts and render the result.

The vendor STEP files are exported in their assembly pose, which is not the
pose you want on a print bed -- a bracket that sits vertically in the robot
exports 123 mm tall and 2 mm thick, and slicing it as-exported gives a part
that is both slow and delaminates along the load axis.

For each part this enumerates the 24 axis-aligned orientations, scores them on
support burden / build height / bed adhesion, and renders as-exported against
the recommendation so the call is visible rather than asserted.

Run with the CAD venv:  edu/.cadenv/bin/python edu/tools/print_orientation.py
"""
from __future__ import annotations

import argparse
import itertools
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.patches import Patch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

REPO = Path(__file__).resolve().parents[2]
STL_DIR = REPO / "edu" / "print_files" / "stl"
OUT_DIR = REPO / "edu" / "print_files" / "orientation"

OVERHANG_LIMIT_DEG = 45.0     # steeper than this needs support
NOZZLE = 0.4
DEFAULT_LAYER = 0.20

# Readable names for the vendor's Chinese filenames.
NAMES = {
    "L架": "L bracket",
    "U梁": "U beam",
    "一字支架": "straight bracket",
    "多功能支架": "multi-function bracket",
    "斜U支架": "angled U bracket",
    "短U支架": "short U bracket",
    "脚板": "foot plate",
    "长U支架": "long U bracket",
}


def axis_aligned_rotations() -> list[tuple[str, np.ndarray]]:
    """The 24 proper rotations of the cube, as (label, 3x3 matrix)."""
    out: list[tuple[str, np.ndarray]] = []
    seen: set[bytes] = set()
    for ax_x, ax_y, ax_z in itertools.permutations(range(3)):
        for sx, sy, sz in itertools.product((1, -1), repeat=3):
            m = np.zeros((3, 3))
            m[0, ax_x] = sx
            m[1, ax_y] = sy
            m[2, ax_z] = sz
            if not math.isclose(np.linalg.det(m), 1.0, abs_tol=1e-9):
                continue           # reflection, not a rotation
            key = m.astype(np.int8).tobytes()
            if key in seen:
                continue
            seen.add(key)
            out.append((_describe(m), m))
    return out


def _describe(m: np.ndarray) -> str:
    """Name a rotation by where the original +Z axis ends up."""
    z_img = m @ np.array([0.0, 0.0, 1.0])
    lbl = {
        (0, 0, 1): "as-exported",
        (0, 0, -1): "flipped (Z down)",
        (1, 0, 0): "Z->+X  (tipped)",
        (-1, 0, 0): "Z->-X  (tipped)",
        (0, 1, 0): "Z->+Y  (laid down)",
        (0, -1, 0): "Z->-Y  (laid down)",
    }
    return lbl.get(tuple(int(round(v)) for v in z_img), "rotated")


def evaluate(mesh: trimesh.Trimesh, rot: np.ndarray) -> dict:
    """Metrics for one orientation, all in mm / mm^2."""
    m = mesh.copy()
    T = np.eye(4)
    T[:3, :3] = rot
    m.apply_transform(T)
    m.apply_translation(-m.bounds[0])          # drop onto the bed

    nz = m.face_normals[:, 2]
    area = m.area_faces
    zmin = m.vertices[:, 2].min()

    cos_lim = -math.cos(math.radians(90 - OVERHANG_LIMIT_DEG))
    # A downward face resting on the bed is not an overhang.
    face_z = m.vertices[m.faces][:, :, 2].max(axis=1)
    on_bed = face_z < zmin + 1e-6
    overhang = float(area[(nz < cos_lim) & ~on_bed].sum())
    contact = float(area[on_bed].sum())

    ext = m.extents
    return {
        "height": float(ext[2]),
        "footprint": float(ext[0] * ext[1]),
        "extents": ext,
        "overhang_mm2": overhang,
        "contact_mm2": contact,
        "layers": int(math.ceil(ext[2] / DEFAULT_LAYER)),
        "mesh": m,
    }


def score(ev: dict) -> float:
    """Lower is better.

    Adhesion is a *threshold*, not a reward. Scoring it linearly makes the
    solver trade real build height for bed contact it does not need -- it
    wanted to print the U brackets 2.6x taller to gain grip on a part that
    already sticks fine. So: penalise too-little contact, but never pay for
    surplus contact.
    """
    need = min(max(150.0, 0.10 * ev["footprint"]), 600.0)
    adhesion = 400.0 * max(0.0, 1.0 - ev["contact_mm2"] / need)

    # Tall and narrow parts get knocked over by the nozzle.
    slenderness = ev["height"] / math.sqrt(max(ev["footprint"], 1.0))
    tipping = 300.0 if slenderness > 3.5 else 0.0

    return (ev["overhang_mm2"] * 1.0      # support: time, material, scarring
            + ev["height"] * 4.0          # proxy for print time
            + adhesion
            + tipping)


# Two orientations within this fraction of each other are not meaningfully
# distinguishable by this heuristic; say so rather than pick one and imply
# confidence.
CLOSE_CALL = 0.15


def render(ax, m: trimesh.Trimesh, title: str, subtitle: str, colour: str):
    tris = m.vertices[m.faces]
    # Painter's algorithm: draw far triangles first.
    order = np.argsort(tris[:, :, 1].mean(axis=1))
    tris = tris[order]
    normals = m.face_normals[order]

    light = np.array([0.4, -0.7, 0.6])
    light /= np.linalg.norm(light)
    shade = np.clip(normals @ light, 0.0, 1.0) * 0.65 + 0.35
    base = np.array(matplotlib.colors.to_rgb(colour))
    facecolors = np.clip(shade[:, None] * base[None, :], 0, 1)

    ax.add_collection3d(Poly3DCollection(
        tris, facecolors=facecolors, edgecolors="none", linewidths=0))

    ext = m.extents
    span = max(ext) * 0.55
    ctr = m.bounds.mean(axis=0)
    ax.set_xlim(ctr[0] - span, ctr[0] + span)
    ax.set_ylim(ctr[1] - span, ctr[1] + span)
    ax.set_zlim(0, span * 2)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=22, azim=-58)
    ax.set_axis_off()

    # The bed, so build height reads at a glance.
    bx = np.array([ctr[0] - span, ctr[0] + span])
    by = np.array([ctr[1] - span, ctr[1] + span])
    xx, yy = np.meshgrid(bx, by)
    ax.plot_surface(xx, yy, np.zeros_like(xx), color="0.85",
                    alpha=0.45, shade=False, zorder=-10)

    # Both labels live inside the axes so each one visually binds to its own
    # render -- set_title() on a 3D axes floats up into the row above.
    ax.text2D(0.5, 0.94, title, transform=ax.transAxes,
              ha="center", va="top", fontsize=10, fontweight="bold")
    ax.text2D(0.5, 0.06, subtitle, transform=ax.transAxes,
              ha="center", va="bottom", fontsize=8, color="0.25")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stl-dir", type=Path, default=STL_DIR)
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    rotations = axis_aligned_rotations()
    stls = sorted(args.stl_dir.glob("*.stl"))
    if not stls:
        print(f"no STLs under {args.stl_dir}")
        return 1

    rows = []
    fig = plt.figure(figsize=(12, 2.7 * len(stls)))
    fig.suptitle("TonyPi frame parts — build orientation\n"
                 f"left: as exported   ·   right: recommended   ·   "
                 f"overhang limit {OVERHANG_LIMIT_DEG:.0f}°, "
                 f"layer {DEFAULT_LAYER} mm",
                 fontsize=12, fontweight="bold", y=0.997)

    for i, p in enumerate(stls):
        mesh = trimesh.load(p, process=True)
        stem = p.stem
        label = NAMES.get(stem, stem)

        evs = [(lbl, evaluate(mesh, r)) for lbl, r in rotations]
        as_is = evaluate(mesh, np.eye(3))
        ranked = sorted(evs, key=lambda kv: score(kv[1]))
        best_lbl, best = ranked[0]
        changed = score(best) < score(as_is) - 1e-6

        # Is the runner-up (in a genuinely different pose) basically as good?
        runner = next(
            ((l, e) for l, e in ranked[1:]
             if abs(e["height"] - best["height"]) > 0.5
             or abs(e["overhang_mm2"] - best["overhang_mm2"]) > 1.0),
            None)
        close = bool(
            runner and score(best) > 0
            and (score(runner[1]) - score(best)) / abs(score(best)) < CLOSE_CALL)

        rows.append({
            "part": label, "file": stem,
            "as_h": as_is["height"], "as_ovh": as_is["overhang_mm2"],
            "as_lay": as_is["layers"],
            "bs_h": best["height"], "bs_ovh": best["overhang_mm2"],
            "bs_lay": best["layers"], "rot": best_lbl,
            "changed": changed,
            "watertight": mesh.is_watertight,
            "thin": float(min(mesh.extents)),
            "close": close,
            "alt": (f"{runner[0]} (h {runner[1]['height']:.0f} mm, "
                    f"overhang {runner[1]['overhang_mm2']:.0f} mm²)"
                    if close and runner else ""),
        })

        axl = fig.add_subplot(len(stls), 2, 2 * i + 1, projection="3d")
        render(axl, as_is["mesh"], f"{label} — as exported",
               f"h {as_is['height']:.0f} mm · {as_is['layers']} layers · "
               f"overhang {as_is['overhang_mm2']:.0f} mm²",
               "#b0453a" if changed else "#4a7c59")

        axr = fig.add_subplot(len(stls), 2, 2 * i + 2, projection="3d")
        render(axr, best["mesh"],
               f"{label} — {'ROTATE: ' + best_lbl if changed else 'keep as-is'}",
               f"h {best['height']:.0f} mm · {best['layers']} layers · "
               f"overhang {best['overhang_mm2']:.0f} mm²",
               "#4a7c59")

    fig.legend(handles=[
        Patch(facecolor="#b0453a", label="needs reorienting before slicing"),
        Patch(facecolor="#4a7c59", label="good orientation"),
    ], loc="lower center", ncol=2, frameon=False, fontsize=9)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.965, bottom=0.028,
                        wspace=0.02, hspace=0.05)
    out = args.out_dir / "orientation_sheet.png"
    fig.savefig(out, dpi=115)
    plt.close(fig)

    w = max(len(r["part"]) for r in rows)
    print(f"\n{'part':<{w}} {'wt':>3} {'thin':>6} "
          f"{'as-exp h':>9} {'ovh':>7} {'lay':>5}   "
          f"{'best h':>7} {'ovh':>7} {'lay':>5}  action")
    print("-" * (w + 74))
    for r in rows:
        act = f"ROTATE {r['rot']}" if r["changed"] else "keep"
        if r["close"]:
            act += "  [CLOSE CALL]"
        print(f"{r['part']:<{w}} {'Y' if r['watertight'] else 'N':>3} "
              f"{r['thin']:>6.1f} "
              f"{r['as_h']:>9.1f} {r['as_ovh']:>7.0f} {r['as_lay']:>5} "
              f"  {r['bs_h']:>7.1f} {r['bs_ovh']:>7.0f} {r['bs_lay']:>5}  {act}")

    for r in rows:
        if r["close"]:
            print(f"\n  close call -- {r['part']}: the runner-up is within "
                  f"{CLOSE_CALL:.0%}.\n    alternative: {r['alt']}")

    print("\nNOTE: this scores PRINTABILITY only -- support burden, build "
          "height, bed adhesion,\n      tipping. It does NOT model strength. "
          "Layer planes are the weak direction,\n      so for a part whose "
          "load path you know, override the recommendation to keep\n"
          "      tensile load in-plane rather than peeling layers apart.")
    print(f"\nsheet -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
