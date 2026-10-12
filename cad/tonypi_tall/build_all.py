#!/usr/bin/env python3
"""Build every part of the TonyPi TALL variant. One command, whole variant:

    edu/.cadenv/bin/python cad/tonypi_tall/build_all.py

Decisions encoded here (rationale in tall_constants.py + TONYPI-TALL-DESIGN.md):
  长U支架  +14 mm stretch, closed-box bridge   (leg/arm link — the height move)
  一字支架 +10 mm stretch if a hole-free band exists, else pass-through
  脚板     platform boot: 82x132 sole, 10 mm, screw-access bores
  短U支架  pass-through + a _closed concept variant (needs swing check on robot)
  斜U/多功能/L架/U梁  pass-through v1 (no assembly data proves webs clear;
                      U梁 torso raise DEFERRED — orientation unverified)
  mohawk_crest  new clip-on part (head dims UNVERIFIED — calipers pending)
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)

from build123d import (  # noqa: E402
    Axis, Box, Cylinder, Plane, Pos, RectangleRounded, chamfer,
    extrude, import_step, make_face, Polyline,
)
import ops  # noqa: E402
import tall_constants as C  # noqa: E402
import vendor_paths  # noqa: E402

# HiWonder's own STEPs. Not redistributed here -- see THIRD_PARTY_NOTICES.md
# and set TONYPI_STOCK_STEP_DIR. build_all.py cannot run without them.
SRC = vendor_paths.stock_step_dir()
DST = os.path.join(REPO, "edu/print_files_tall")
reports = []


def out_paths(name):
    return (os.path.join(DST, "step", f"{name}.step"),
            os.path.join(DST, "stl", f"{name}.stl"))


def render(step_path, png_name):
    png = os.path.join(DST, "renders", png_name)
    rc = os.system(
        f'cd {REPO} && edu/.cadenv/bin/python edu/tools/render_step.py '
        f'"{step_path}" -o "{png}" >/dev/null 2>&1')
    return png if rc == 0 else None


def emit(part, name, note, src_file=None, render_before=True, copy_src=None):
    step, stl = out_paths(name)
    if copy_src:
        # pass-through: byte-identical copy beats a re-export (zero drift),
        # and OCCT refuses export_step on some re-imported compounds anyway
        import shutil
        from build123d import export_stl
        shutil.copy(os.path.join(SRC, copy_src), step)
        export_stl(part, stl, tolerance=0.01)
        bb = part.bounding_box()
        r = {"label": name,
             "bbox_mm": [round(bb.size.X, 3), round(bb.size.Y, 3), round(bb.size.Z, 3)],
             "volume_cm3": round(part.volume / 1000, 3),
             "n_solids": len(part.solids()), "n_faces": len(part.faces()),
             "step": step, "stl": stl}
    else:
        r = ops.report(part, step, stl, name)
    r["notes"] = note
    if src_file and render_before:
        r["render_before"] = render(os.path.join(SRC, src_file), f"{name}_before.png")
    r["render_after"] = render(step, f"{name}_after.png")
    # The report is COMMITTED evidence, so it must never carry an absolute
    # path off this machine: every path it records is relative to the repo.
    for k in ("step", "stl", "render_before", "render_after"):
        if r.get(k):
            r[k] = os.path.relpath(r[k], REPO)
    reports.append(r)
    print(f"  {name}: bbox {r['bbox_mm']} vol {r['volume_cm3']} cm3 "
          f"solids {r['n_solids']} — {note}")
    return r


# ------------------------------------------------------------ 1. leg link
print("长U支架 +14 closed box …")
p = import_step(os.path.join(SRC, "长U支架.step"))
tall, st, area = ops.stretch(p, Axis.Y, C.LEG_LINK_EXT)
# Close the SERVO-FREE channel the stretch opens up, not the extension zone:
# the servo body sits at y [33.97, 74.01] and the v1 band ran into it. See the
# webs section of tall_constants.py; verify with servo_envelope.py.
tall = ops.close_span(tall, Axis.Y, C.LEG_CLOSE_LO, C.LEG_CLOSE_HI,
                      Axis.Z, wall=C.WEB_WALL)
emit(tall, "长U支架_tall",
     f"+{C.LEG_LINK_EXT} mm at y={st:.1f}, closed box y="
     f"[{C.LEG_CLOSE_LO},{C.LEG_CLOSE_HI}] (below the servo, measured)",
     "长U支架.step")

# ------------------------------------------------------------ 2. strap
print("一字支架 +10 …")
p = import_step(os.path.join(SRC, "一字支架.step"))
try:
    tall, st, area = ops.stretch(p, Axis.X, C.STRAP_EXT)
    emit(tall, "一字支架_tall", f"+{C.STRAP_EXT} mm at x={st:.1f}", "一字支架.step")
except ValueError as e:
    emit(p, "一字支架_tall", f"PASS-THROUGH — no hole-free band ({e})", "一字支架.step")

# ------------------------------------------------------------ 3. foot
print("脚板 platform boot …")
import trimesh  # noqa: E402
orig_stl = trimesh.load(os.path.join(vendor_paths.stock_stl_dir(), "脚板.stl"),
                        force="mesh")
sec = orig_stl.section(plane_origin=[0, 1.0, 0], plane_normal=[0, 1, 0])
planar, to3d = sec.to_2D()
# loops without shapely: the largest-extent loop is the outline, rest are holes
loops = planar.discrete
extent = [max(l[:, 0].max() - l[:, 0].min(), l[:, 1].max() - l[:, 1].min())
          for l in loops]
outline_i = extent.index(max(extent))
holes = []                            # (x, z, diameter) in plate coords
for k, loop in enumerate(loops):
    if k == outline_i:
        continue
    cx2, cy2 = loop[:, 0].mean(), loop[:, 1].mean()
    c3 = trimesh.transform_points([[cx2, cy2, 0]], to3d)[0]
    holes.append((round(float(c3[0]), 2), round(float(c3[2]), 2),
                  round(float(extent[k]), 2)))
m3 = [h for h in holes if 2.6 <= h[2] <= 4.6]
print(f"  holes found: {len(holes)} total, {len(m3)} M3-size: {m3}")

plate = import_step(os.path.join(SRC, "脚板.step"))
bb = plate.bounding_box()
cx, cz = (bb.min.X + bb.max.X) / 2, (bb.min.Z + bb.max.Z) / 2
sole_plane = Plane(origin=(cx, bb.min.Y, cz), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
sole_sk = sole_plane * RectangleRounded(C.FOOT_W, C.FOOT_L, 8.0)
sole = extrude(sole_sk, amount=C.SOLE_H)
bottom_edges = [e for e in sole.edges()
                if abs(e.center().Y - (bb.min.Y - C.SOLE_H)) < 0.1]
try:
    sole = chamfer(bottom_edges, 2.5)
except Exception as exc:
    print(f"  chamfer skipped: {exc}")
boot = (plate + sole).clean()
for (hx, hz, hd) in m3:
    bore = Pos(hx, bb.min.Y - C.SOLE_H / 2, hz) * Cylinder(
        C.SOLE_ACCESS_D / 2, C.SOLE_H + 2, rotation=(90, 0, 0))
    boot = boot - bore
boot = boot.clean()
emit(boot, "脚板_platform",
     f"sole {C.FOOT_W}x{C.FOOT_L}x{C.SOLE_H}, {len(m3)} access bores; "
     f"solid model — print at ~15% infill", "脚板.step")

# Second variant: also bore the LARGE holes through the sole. The vendor plate
# has 6 of them and the boot turns them into blind pockets. Which is correct
# depends on whether anything (cable, sensor, foot pad) passes through them —
# an assembly fact the manual does not carry. Ship both so the answer is a
# choice on the bench, not a rebuild.
big = [h for h in holes if h[2] > 4.6]
boot_open = boot
for (hx, hz, hd) in big:
    bore = Pos(hx, bb.min.Y - C.SOLE_H / 2, hz) * Cylinder(
        (hd + 0.6) / 2, C.SOLE_H + 2, rotation=(90, 0, 0))
    boot_open = boot_open - bore
boot_open = boot_open.clean()
emit(boot_open, "脚板_platform_open",
     f"ALTERNATIVE — same boot with the {len(big)} large vendor holes bored "
     f"through the sole too (dia {sorted({round(h[2],1) for h in big})} +0.6 "
     f"clearance). Use this one IF anything passes through them.",
     None, render_before=False)

# ------------------------------------------------------------ 4. mohawk
print("mohawk_crest …")
R_out = C.HEAD_W / 2 + 2.5
R_in = C.HEAD_W / 2
SADDLE_L = 60.0
# saddle axis = Z (front-back over the head); keep the upper half-arc only
shell = (Cylinder(R_out, SADDLE_L)
         - Cylinder(R_in, SADDLE_L + 2)
         - Pos(0, -R_out, 0) * Box(2 * R_out + 2, 2 * R_out, SADDLE_L + 2))
# skirt tabs with zip-tie slots, both sides
for sx in (-1, 1):
    tab = Pos(sx * (R_in + 1.25), -9, 0) * Box(2.5, 18, 14)
    slot = Pos(sx * (R_in + 1.25), -12, 0) * Box(
        3.0, C.STRAP_SLOT[1], C.STRAP_SLOT[0])
    shell = shell + tab - slot
# crest fin: spiked profile in the YZ plane, extruded CREST_T in X
n = C.CREST_N_SPIKES
half = C.CREST_L / 2
base_y = R_out - 3.0
pts = [(-half, base_y)]
for k in range(n):
    z0 = -half + (2 * k) * half / n
    z1 = -half + (2 * k + 1) * half / n
    z2 = -half + (2 * k + 2) * half / n
    env = math.cos(math.pi * ((z0 + z1) / 2) / (2.6 * half))
    peak = base_y + 12 + (C.CREST_H - 12) * env
    pts += [(z1, peak), (z2, base_y + 8)]
pts += [(half, base_y), (-half, base_y)]
# plane maps sketch (z, y) -> global (Z, +Y): y_dir = z_dir x x_dir = +Y
fin_sk = Plane((0, 0, 0), x_dir=(0, 0, 1), z_dir=(-1, 0, 0)) * make_face(
    Polyline(*[(z, y) for z, y in pts]))
fin = extrude(fin_sk, amount=C.CREST_T / 2, both=True)
crest = (shell + fin).clean()
emit(crest, "mohawk_crest",
     f"clip-on: saddle W={C.HEAD_W} UNVERIFIED, fin {C.CREST_L}x{C.CREST_H}, "
     f"{n} spikes, zip-tie slots", None, render_before=False)

# ------------------------------------------------------------ 5. pass-throughs
PASS = {
    "短U支架": "joint bracket — servo swings between arms; closure needs a "
              "swing check on the robot (see _closed concept)",
    "斜U支架": "oblique joint bracket — same swing concern, pass-through v1",
    "多功能支架": "complex mount — no proven-clear web zone, pass-through v1",
    "L架": "corner bracket — pass-through v1",
    "U梁": "TORSO RAISE DEFERRED — orientation unverified by the manual; "
           "stretching a horizontal beam would widen, not heighten",
}
for name, why in PASS.items():
    p = import_step(os.path.join(SRC, f"{name}.step"))
    emit(p, f"{name}_tall", f"PASS-THROUGH — {why}", f"{name}.step",
         copy_src=f"{name}.step")

# 短U closed-sides CONCEPT (clearly marked, not for blind printing)
p = import_step(os.path.join(SRC, "短U支架.step"))
bb = p.bounding_box()
mid = (bb.min.Y + bb.max.Y) / 2
concept = ops.close_span(p, Axis.Y, mid - 6, mid + 6, Axis.Z, wall=C.REINF_WALL)
SERVO_W = 20.14                      # measured, servo_envelope.py
_per_side = ((bb.max.Z - bb.min.Z) - 2 * C.REINF_WALL - SERVO_W) / 2
emit(concept, "短U支架_tall_closed",
     f"CONCEPT ONLY — servo fills this bracket end to end (y[-2.02,38.02] in "
     f"a y[-2,40.5] part), so no servo-free span exists; {C.REINF_WALL} mm "
     f"walls leave {_per_side:.2f} mm/side. Test-fit a real LX-824HV before "
     f"printing", None, render_before=False)

with open(os.path.join(DST, "build_report.json"), "w") as fh:
    json.dump(reports, fh, indent=2, ensure_ascii=False)
print(f"\n{len(reports)} parts -> {DST}/build_report.json")

# ------------------------------------------------------------ plate fit
# Cheap, but it is the one check that turns a design into a print job.
bv = C.BUILD_VOLUME
over = [r for r in reports
        if any(d > v for d, v in zip(sorted(r["bbox_mm"], reverse=True),
                                     sorted(bv, reverse=True)))]
biggest = max(reports, key=lambda r: max(r["bbox_mm"]))
print(f"{C.PRINTER} plate {bv[0]:.0f}x{bv[1]:.0f}x{bv[2]:.0f} mm — "
      f"largest part {biggest['label']} at {max(biggest['bbox_mm']):.0f} mm: "
      + ("ALL FIT" if not over else f"OVERSIZE: {[r['label'] for r in over]}"))
