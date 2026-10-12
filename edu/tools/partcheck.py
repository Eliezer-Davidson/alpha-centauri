#!/usr/bin/env python3
"""Physical feedback for a printed part — the numbers, before the printer.

    edu/.cadenv/bin/python edu/tools/partcheck.py part.step [--mat PETG] [--3mf]

Or from a part script, which is the point:

    from partcheck import check
    check(solid, "chassis_half", out_dir)

WHY
---
Two ideas from the AI-CAD literature survive contact with this project, and both
are about closing a loop rather than generating geometry:

  * Zoo/Zookeeper's PHYSICAL FEEDBACK -- the agent gets mass, volume and centre
    of mass back after every edit, so a claim about a part can be checked
    instead of asserted. This project needs CoM specifically: standing CoM
    position is worth ~27% of knee-torque demand, and it was being ASSUMED
    centred.
  * PrintMakerAI's PRE-GENERATION CONSTRAINT VALIDATION -- minimum wall and
    unsupported overhang, checked before committing. We had neither; overhangs
    were being eyeballed.

Everything else in that survey (B-Rep diffusion, graph nets, the datasets and
benchmarks) is about TRAINING a model to emit CAD. It does not apply to using
build123d well.

WHAT THIS DELIBERATELY DOES NOT DO
----------------------------------
It does not slice, and it does not predict print time or adhesion. The overhang
map is a geometric fact; whether a given overhang actually fails depends on
cooling, material and speed, which only a slicer knows. Treat a support-area
number as "look here", not as a verdict.

THE FIRST-LAYER TRAP
--------------------
A naive overhang test flags the part's own footprint -- the bottom face points
straight down and is 100% "unsupported". On the chassis that alone was 18.5% of
surface area and turned a real 4.8% support requirement into a meaningless
23.4%. Facets within FIRST_LAYER of the minimum Z are therefore excluded: they
rest on the build plate.
"""

import argparse
import math
import os
from collections import Counter

import numpy as np
import trimesh

# g/cm3 -- the three materials interface_constants names
DENSITY = {"PETG": 0.953, "PC": 1.20, "PA-CF": 1.10, "TPU": 1.21, "PLA": 1.24}

NOZZLE = 0.4            # A1 mini stock (H2C-era value was the same 0.4);
                        # two extrusions is the printable floor
FIRST_LAYER = 0.15      # facets this close to z_min are bed contact, not overhang
OVERHANG_DEG = 45.0     # steeper than this off vertical needs support
# UPDATED 2026-09-07 (edu/REPLAN-2026-08-28.md): the only printer is a Bambu
# A1 mini. H2C-era bed was (330, 320, 325) -- parts graded before this date
# were gated against THAT bed; re-grade before printing anything old. Narrow
# parts can lie diagonally to ~245 mm, which this axis-aligned check does not
# model -- a False here for a long thin part may still print diagonally.
BED = (180.0, 180.0, 180.0)
# A cylinder resting on the plate touches along a TANGENT LINE, so a part can be
# geometrically perfect and still have almost no first layer. Rule of thumb: a
# tall slender part wants a couple of hundred mm2 or it shears off mid-print.
BED_CONTACT_MIN = 150.0


def _mesh_of(shape, tol=0.05):
    """Tessellate a build123d solid to a trimesh, without touching disk.

    MUST weld vertices. OCCT tessellates each B-Rep face independently, so the
    raw output is N disconnected islands sharing no vertices -- which reports as
    "not watertight, 106 bodies" on a part that is demonstrably one closed solid
    when the same geometry is round-tripped through STL. Welding restores the
    shared edges, and without it every integrity check is measuring the
    tessellator rather than the part.
    """
    verts, faces = shape.tessellate(tolerance=tol)
    m = trimesh.Trimesh(
        vertices=np.array([(v.X, v.Y, v.Z) for v in verts], dtype=float),
        faces=np.array(faces, dtype=np.int64),
        process=True,
    )
    m.merge_vertices()
    m.remove_degenerate_faces() if hasattr(m, "remove_degenerate_faces") else None
    return m


def overhangs(mesh):
    """Area needing support, first layer excluded. Returns (mm2, fraction, detail)."""
    n, a, c = mesh.face_normals, mesh.area_faces, mesh.triangles_center
    zmin = mesh.bounds[0][2]
    # angle of the normal BELOW horizontal: 90 = facing straight down
    down = np.degrees(np.arcsin(np.clip(-n[:, 2], -1, 1)))
    on_bed = (c[:, 2] < zmin + FIRST_LAYER) & (down > 80)
    bad = (down >= OVERHANG_DEG) & ~on_bed
    total = a.sum()
    detail = {
        "bed_contact_mm2": float(a[on_bed].sum()),
        "bridge_mm2": float(a[(down >= 80) & ~on_bed].sum()),
        "steep_mm2": float(a[(down >= OVERHANG_DEG) & (down < 80) & ~on_bed].sum()),
    }
    if bad.any():
        detail["z_range"] = (float(c[bad][:, 2].min()), float(c[bad][:, 2].max()))
    return float(a[bad].sum()), float(a[bad].sum() / total), detail


def thickness(mesh, n_samples=20000, seed=0):
    """Local wall thickness by casting each sampled point's normal INWARD.

    Sampling rather than per-facet because a tessellated part has tens of
    thousands of facets and the distribution is what matters, not each triangle.
    The eps step is needed or every ray re-hits its own origin facet.
    """
    rng = np.random.default_rng(seed)
    pts, fid = trimesh.sample.sample_surface(mesh, n_samples, seed=int(rng.integers(1 << 30)))
    nrm = mesh.face_normals[fid]
    origins = pts - nrm * 1e-3
    loc, idx, _ = mesh.ray.intersects_location(origins, -nrm, multiple_hits=False)
    if len(loc) == 0:
        return None
    return np.linalg.norm(loc - origins[idx], axis=1), pts[idx]


def _cluster_extent(pts, link=3.0, cap=4000):
    """Group thin points into connected clusters; return (count, biggest extent).

    Single-link at `link` mm: two thin samples belong together only if they are
    within a few nozzle widths. That separates "one continuous thin wall" from
    "several unrelated sharp corners", which a global bounding box cannot.
    """
    from scipy.cluster.hierarchy import fcluster, linkage

    p = pts if len(pts) <= cap else pts[np.random.default_rng(0).choice(
        len(pts), cap, replace=False)]
    if len(p) < 2:
        return 1, np.zeros(3)
    lab = fcluster(linkage(p, method="single"), t=link, criterion="distance")
    best = np.zeros(3)
    for c in np.unique(lab):
        e = np.ptp(p[lab == c], axis=0)
        if e.prod() > best.prod() or best.sum() == 0:
            best = e
    return int(len(np.unique(lab))), best


def check(shape, name, out_dir=None, material="PETG", wall_nominal=None,
          write_3mf=True, verbose=True):
    """Run every check on a build123d solid. Returns a dict; prints a report."""
    mesh = _mesh_of(shape)
    rho = DENSITY.get(material, 0.953)
    bb = shape.bounding_box()
    com = shape.center()
    size = (bb.size.X, bb.size.Y, bb.size.Z)

    r = {
        "name": name,
        "size_mm": size,
        "volume_cm3": shape.volume / 1000.0,
        "mass_g": shape.volume / 1000.0 * rho,
        "material": material,
        "com_mm": (com.X, com.Y, com.Z),
        "solids": len(shape.solids()),
        "faces": len(shape.faces()),
        "surface_types": dict(Counter(str(f.geom_type).split(".")[-1]
                                      for f in shape.faces())),
        "watertight": bool(mesh.is_watertight),
        "winding_ok": bool(mesh.is_winding_consistent),
        "bodies": int(mesh.body_count),
        "fits_bed": all(s <= b for s, b in zip(sorted(size), sorted(BED))),
    }
    area, frac, detail = overhangs(mesh)
    r["support_mm2"], r["support_frac"], r["overhang_detail"] = area, frac, detail

    tr = thickness(mesh)
    if tr is not None:
        t, where = tr
        floor = 2 * NOZZLE
        thin = t < floor
        r["thickness_min_mm"] = float(t.min())
        r["thickness_p1_mm"] = float(np.percentile(t, 1))
        r["below_two_extrusions_frac"] = float(thin.mean())
        # A bare minimum is not actionable: EVERY convex edge tapers to zero, so
        # a sharp corner and a genuinely thin wall both report ~0.00 mm.
        #
        # Nor is the bounding box of all thin points. Two specks 110 mm apart
        # produce a huge box and read as one broad defect -- which is exactly
        # what this reported on the calf, where the truth was 25 samples in two
        # sharp corners. CLUSTER them and judge the biggest cluster alone.
        if thin.any():
            pts_thin = np.asarray(where[thin])
            r["thin_count"] = int(thin.sum())
            r["thin_clusters"], big = _cluster_extent(pts_thin)
            r["thin_extent_mm"] = tuple(float(v) for v in big)
            # a cluster thin in one direction only is an edge; thin in all
            # three is a speck; broad in two is a genuine thin wall
            r["thin_is_edge_sliver"] = bool(sorted(big)[1] < 3.0)

    if out_dir and write_3mf:
        os.makedirs(out_dir, exist_ok=True)
        p = os.path.join(out_dir, f"{name}.3mf")
        mesh.export(p)
        r["mf3"] = p

    if verbose:
        _print(r)
    return r


def _print(r):
    w, f = r["size_mm"], r
    print(f"\n{'='*66}\n  {r['name']}\n{'='*66}")
    print(f"  {w[0]:.1f} x {w[1]:.1f} x {w[2]:.1f} mm     "
          f"{f['volume_cm3']:.1f} cm3     {f['material']} ~{f['mass_g']:.0f} g")
    c = f["com_mm"]
    print(f"  centre of mass  ({c[0]:.2f}, {c[1]:.2f}, {c[2]:.2f}) mm")
    print(f"  B-Rep           {f['solids']} solid, {f['faces']} faces  "
          f"{f['surface_types']}")

    def flag(ok):
        return "OK  " if ok else "FAIL"

    print(f"\n  {flag(f['solids'] == 1)} single solid            ({f['solids']})")
    print(f"  {flag(f['watertight'])} watertight")
    print(f"  {flag(f['winding_ok'])} winding consistent")
    print(f"  {flag(f['bodies'] == 1)} one body                ({f['bodies']})")
    print(f"  {flag(f['fits_bed'])} fits the A1 mini bed    "
          f"({BED[0]:.0f}x{BED[1]:.0f}x{BED[2]:.0f})")
    if "thickness_min_mm" in f:
        frac = f["below_two_extrusions_frac"]
        sliver = f.get("thin_is_edge_sliver", False)
        ok = frac == 0.0
        print(f"  {'OK  ' if ok else 'WARN'} wall >= 2 extrusions    "
              f"(min {f['thickness_min_mm']:.2f} mm, floor {2*NOZZLE:.1f})")
        if not ok:
            e = f["thin_extent_mm"]
            print(f"       {f['thin_count']} thin samples ({100*frac:.2f}%) in "
                  f"{f['thin_clusters']} cluster(s); biggest "
                  f"{e[0]:.1f}x{e[1]:.1f}x{e[2]:.1f} mm"
                  + ("  <- sharp corner, not a thin wall"
                     if sliver else "  <- REAL thin wall"))

    bed = f["overhang_detail"]["bed_contact_mm2"]
    bed_ok = bed >= BED_CONTACT_MIN
    print(f"  {'OK  ' if bed_ok else 'WARN'} bed contact             "
          f"({bed:.0f} mm2, want >= {BED_CONTACT_MIN:.0f})"
          + ("" if bed_ok else "  <- tall part on a tangent line will shear off"))
    d = f["overhang_detail"]
    print(f"\n  support needed  {f['support_mm2']:.0f} mm2 = {100*f['support_frac']:.1f}% "
          f"of surface")
    print(f"    bridge >80 deg   {d['bridge_mm2']:8.0f} mm2")
    print(f"    steep 45-80      {d['steep_mm2']:8.0f} mm2")
    print(f"    (bed contact     {d['bed_contact_mm2']:8.0f} mm2, free)")
    if "z_range" in d:
        print(f"    at Z {d['z_range'][0]:.1f} .. {d['z_range'][1]:.1f} mm")
    if "mf3" in f:
        print(f"\n  3MF -> {f['mf3']}")


if __name__ == "__main__":
    from build123d import import_step

    ap = argparse.ArgumentParser()
    ap.add_argument("step")
    ap.add_argument("--mat", default="PETG", choices=sorted(DENSITY))
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    shape = import_step(a.step)
    check(shape, os.path.splitext(os.path.basename(a.step))[0],
          out_dir=a.out or os.path.dirname(a.step), material=a.mat)
