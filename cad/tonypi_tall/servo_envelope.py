#!/usr/bin/env python3
"""Locate the LX-824HV's output shaft, then place it in the U and measure.

    edu/.cadenv/bin/python cad/tonypi_tall/servo_envelope.py

The first clearance pass used "longest servo axis points down the U", which is
a bound, not a measurement — it can only ever say COLLIDES. This finds the real
shaft axis in the vendor CAD, registers the servo to the bracket's hub hole,
and reports the two clearances that actually decide the design:

  along the U   — does the closure band sit inside the servo's footprint?
  across the U  — does the servo body fit between the two closing plates?
"""
import os
import sys

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import tall_constants as C  # noqa: E402
import vendor_paths  # noqa: E402

from build123d import export_stl, import_step  # noqa: E402
AX = "xyz"


def mesh_of(path, tol=0.15):
    tmp = f"/tmp/_env_{os.path.basename(path)}.stl"
    export_stl(import_step(path), tmp, tolerance=tol)
    return trimesh.load(tmp, force="mesh")


def round_loops(m, axis, coord, dmin=4.0, dmax=14.0, round_tol=0.30):
    """Round-ish section loops at a station — bosses, shafts, bores."""
    n = [0, 0, 0]; n[axis] = 1
    o = [0, 0, 0]; o[axis] = coord
    sec = m.section(plane_origin=o, plane_normal=n)
    if sec is None:
        return []
    planar, to3d = sec.to_2D()
    out = []
    for loop in planar.discrete:
        w = np.ptp(loop[:, 0]); h = np.ptp(loop[:, 1])
        d = (w + h) / 2
        if not (dmin <= d <= dmax) or abs(w - h) > round_tol * d:
            continue
        c3 = trimesh.transform_points(
            [[loop[:, 0].mean(), loop[:, 1].mean(), 0]], to3d)[0]
        out.append((d, c3))
    return out


print("=" * 78)
servo = mesh_of(vendor_paths.servo_step())
slo, shi = servo.bounds
ssz = shi - slo
print(f"LX-824HV  bbox {ssz[0]:.2f} x {ssz[1]:.2f} x {ssz[2]:.2f} mm")

# the output spline is the round boss standing proud at one end of some axis
best = None
for ax in range(3):
    for end, coord in (("max", shi[ax] - 1.0), ("min", slo[ax] + 1.0)):
        for d, c in round_loops(servo, ax, coord):
            depth = (shi[ax] - coord) if end == "max" else (coord - slo[ax])
            if best is None or d < best[0]:
                best = (d, ax, end, c, depth)
if best is None:
    print("no round boss found — cannot register the servo"); sys.exit(1)
d, sax, send, sc, _ = best
print(f"output boss: dia {d:.2f} mm on the {AX[sax]} axis ({send} end), "
      f"centre {AX[(sax+1)%3]}={sc[(sax+1)%3]:.2f} "
      f"{AX[(sax+2)%3]}={sc[(sax+2)%3]:.2f}")

# the two axes that are NOT the shaft: one runs along the U, one across it
oth = [a for a in range(3) if a != sax]
spans = {a: (slo[a], shi[a], ssz[a]) for a in oth}
long_ax = max(oth, key=lambda a: ssz[a])
thin_ax = min(oth, key=lambda a: ssz[a])
shaft_pos_long = sc[long_ax]
reach_web = shaft_pos_long - spans[long_ax][0]
reach_top = spans[long_ax][1] - shaft_pos_long
print(f"long axis  {AX[long_ax]}: {ssz[long_ax]:.2f} mm — shaft sits "
      f"{reach_top:.2f} from one end, {reach_web:.2f} from the other")
print(f"thin axis  {AX[thin_ax]}: {ssz[thin_ax]:.2f} mm  <- this is what must "
      f"fit BETWEEN the closing plates")

print("-" * 78)
# measure the parts the closure is actually ON. The stretch moves the hub up by
# the extension, so checking the stock bracket answers the wrong question.
TARGETS = [
    ("长U支架_tall", "edu/print_files_tall/step",
     C.LEG_CLOSE_LO, C.LEG_CLOSE_HI, C.WEB_WALL),
    ("短U支架_tall_closed", "edu/print_files_tall/step",
     19.25 - 6.0, 19.25 + 6.0, C.REINF_WALL),
]
for part, folder, band_lo, band_hi, wall in TARGETS:
    m = mesh_of(os.path.join(REPO, folder, f"{part}.step"))
    lo, hi = m.bounds
    hub = sorted(round_loops(m, 0, lo[0] + 1.0, dmin=6.0, dmax=12.0),
                 key=lambda t: -t[0])
    if not hub:
        print(f"{part}: no hub hole found"); continue
    hub_d, hub_c = hub[0]
    hub_y, hub_z = hub_c[1], hub_c[2]
    depth = hi[2] - lo[2]
    print(f"\n{part}   arms y[{lo[1]:.1f},{hi[1]:.1f}]  channel depth "
          f"{depth:.2f} mm   hub dia {hub_d:.2f} at y={hub_y:.2f} z={hub_z:.2f}")

    # servo hangs from the hub toward the web (the far end of the long axis)
    servo_lo = hub_y - reach_web
    servo_hi = hub_y + reach_top
    print(f"  servo body occupies y [{servo_lo:.2f}, {servo_hi:.2f}]"
          f"   (web end of the bracket is y={lo[1]:.2f})")
    olap = min(band_hi, servo_hi) - max(band_lo, servo_lo)
    gap = servo_lo - band_hi
    print(f"  closure band          y [{band_lo:.2f}, {band_hi:.2f}]"
          f"   overlap along the U = {max(0.0, olap):+.2f} mm"
          + (f"   (clear by {gap:.2f} mm)" if olap <= 0 else ""))

    clear = depth - 2 * wall
    marg = clear - ssz[thin_ax]
    # channel depth only decides anything where the plates and the servo share
    # Y-span; if the band sits clear along the U, this check does not apply
    if olap > 0:
        print(f"  ACROSS: channel {depth:.2f} - 2x{wall:.1f} wall = "
              f"{clear:.2f} clear   vs servo {ssz[thin_ax]:.2f}   "
              f"margin {marg:+.2f} mm  -> {'FITS' if marg > 0 else 'INTERFERES'}")
    else:
        print(f"  ACROSS: n/a — band shares no Y-span with the servo "
              f"(would have been {marg:+.2f} mm at {wall:.1f} mm wall)")

    # where does the channel floor start? the web is a full-width slab; above it
    # only the two arms remain, so the section area drops hard at the floor
    ys = np.linspace(lo[1] + 0.4, hi[1] - 0.4, 160)
    areas = []
    for yv in ys:
        sec = m.section(plane_origin=[0, yv, 0], plane_normal=[0, 1, 0])
        if sec is None:
            areas.append(0.0)
            continue
        planar, _ = sec.to_2D()
        areas.append(float(sum(p.area for p in planar.polygons_full)))
    areas = np.array(areas)
    # the web is a full slab; above the floor only the two arms remain
    solid = areas > 0.80 * areas.max()
    floor_y = float(ys[np.argmax(~solid)]) if (~solid).any() else lo[1]
    print(f"  channel floor (top of the web) y ≈ {floor_y:.2f}")

    free_lo, free_hi = floor_y + 1.5, servo_lo - 0.5
    if free_hi - free_lo > 4.0:
        print(f"  >> SERVO-FREE CHANNEL: y [{free_lo:.2f}, {free_hi:.2f}] = "
              f"{free_hi - free_lo:.1f} mm — closes at full {C.WEB_WALL} mm wall")
    if olap > 0:
        need = (depth - ssz[thin_ax] - 0.8) / 2      # 0.4 mm per side
        print(f"  FIX A: move band to y [{free_lo:.1f}, {free_hi:.1f}] "
              f"(full wall, zero interference)")
        print(f"  FIX B: keep the band, thin the wall to <= {need:.2f} mm "
              f"(0.40 mm/side — inside print tolerance, riskier)")
print("=" * 78)
