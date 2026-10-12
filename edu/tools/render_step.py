#!/usr/bin/env python3
"""Render a STEP/IGES part to a labelled PNG montage — no GPU, no GL, no viewer.

    edu/.cadenv/bin/python edu/tools/render_step.py path/to/part.step

Exists because "the CAD imported fine" is a claim, and this project's rule is
that a claim ships with a picture. Tessellates through build123d/OCCT, then
draws the triangles with matplotlib's 3D backend so it works headless and over
SSH. Four views, a shared scale, and the measured bounding box in the caption.
"""
import argparse
import os
import sys

import matplotlib
matplotlib.use("Agg")                       # headless: no display needed
import matplotlib.pyplot as plt             # noqa: E402
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

from build123d import Mesher, import_step   # noqa: E402

VIEWS = [("iso", 22, -60), ("front", 0, -90), ("side", 0, 0), ("top", 89, -90)]


def load(path):
    if path.lower().endswith((".step", ".stp")):
        return import_step(path)
    from build123d import import_brep
    return import_brep(path)


def tessellate(shape, tmp="/tmp/_render_step.stl", tol=0.08):
    """STEP is exact B-rep; matplotlib needs triangles. Go through STL."""
    Mesher().add_shape(shape, linear_deflection=tol)
    Mesher().write(tmp) if False else None
    from build123d import export_stl
    export_stl(shape, tmp, tolerance=tol)
    import trimesh
    return trimesh.load(tmp, force="mesh")


def render(path, out, tol=0.08):
    shape = load(path)
    bb = shape.bounding_box()
    mesh = tessellate(shape, tol=tol)
    tris = mesh.vertices[mesh.faces]

    fig = plt.figure(figsize=(13, 3.4), facecolor="#14110e")
    span = max(bb.size.X, bb.size.Y, bb.size.Z) * 0.62
    cx, cy, cz = (bb.min.X + bb.max.X) / 2, (bb.min.Y + bb.max.Y) / 2, (bb.min.Z + bb.max.Z) / 2

    for i, (name, elev, azim) in enumerate(VIEWS, 1):
        ax = fig.add_subplot(1, len(VIEWS), i, projection="3d")
        ax.add_collection3d(Poly3DCollection(
            tris, facecolor="#c8c2b8", edgecolor="#4a4038", linewidths=0.06, alpha=1.0))
        ax.set_xlim(cx - span, cx + span)
        ax.set_ylim(cy - span, cy + span)
        ax.set_zlim(cz - span, cz + span)
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(elev=elev, azim=azim)
        ax.set_facecolor("#14110e")
        ax.set_axis_off()
        ax.set_title(name, color="#E0913F", fontsize=10,
                     family="monospace", pad=-2)

    fig.suptitle(
        f"{os.path.basename(path)}   "
        f"{bb.size.X:.2f} x {bb.size.Y:.2f} x {bb.size.Z:.2f} mm   "
        f"{shape.volume/1000:.2f} cm3   {len(mesh.faces)} triangles",
        color="#e8e2d9", fontsize=10, family="monospace", y=0.06)
    fig.tight_layout()
    fig.savefig(out, dpi=135, facecolor="#14110e", bbox_inches="tight")
    print(f"  {os.path.basename(path)}  ->  {out}")
    print(f"  {bb.size.X:.2f} x {bb.size.Y:.2f} x {bb.size.Z:.2f} mm, "
          f"{shape.volume/1000:.2f} cm3, {len(mesh.faces)} triangles")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("path")
    p.add_argument("-o", "--out", default=None)
    p.add_argument("--tol", type=float, default=0.08)
    a = p.parse_args()
    out = a.out or os.path.splitext(os.path.basename(a.path))[0] + ".png"
    sys.exit(render(a.path, out, a.tol))
