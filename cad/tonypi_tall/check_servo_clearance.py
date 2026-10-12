#!/usr/bin/env python3
"""Does the closed-box span actually clear the servo body?

    edu/.cadenv/bin/python cad/tonypi_tall/check_servo_clearance.py

close_span() was applied over a band proven to be *hole-free*. Hole-free is not
the same as empty: on HiWonder frames the servo body sits INSIDE the U, between
the two arms. This measures the real LX-824HV against the real bracket instead
of assuming, and prints the margin.
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


def mesh_of(path, tol=0.2):
    tmp = "/tmp/_clearance.stl"
    export_stl(import_step(path), tmp, tolerance=tol)
    return trimesh.load(tmp, force="mesh")


def circles_in_arm(m, x_side, r_min=3.5):
    """Find large through-holes in one arm: slice the arm, take loop centres."""
    sec = m.section(plane_origin=[x_side, 0, 0], plane_normal=[1, 0, 0])
    planar, to3d = sec.to_2D()
    out = []
    for loop in planar.discrete:
        w = loop[:, 0].max() - loop[:, 0].min()
        h = loop[:, 1].max() - loop[:, 1].min()
        d = (w + h) / 2
        if d < 2 * r_min or abs(w - h) > 0.35 * d:      # round-ish only
            continue
        c2 = [loop[:, 0].mean(), loop[:, 1].mean(), 0]
        c3 = trimesh.transform_points([c2], to3d)[0]
        out.append((round(float(c3[1]), 2), round(float(c3[2]), 2), round(d, 2)))
    return out


print("=" * 74)
servo = mesh_of(vendor_paths.servo_step())
lo, hi = servo.bounds
sz = hi - lo
print(f"LX-824HV servo   bbox {sz[0]:.2f} x {sz[1]:.2f} x {sz[2]:.2f} mm   "
      f"vol {servo.volume/1000:.1f} cm3")

stock = mesh_of(os.path.join(vendor_paths.stock_step_dir(), "长U支架.step"))
slo, shi = stock.bounds
print(f"长U支架 stock     bbox {shi[0]-slo[0]:.2f} x {shi[1]-slo[1]:.2f} x "
      f"{shi[2]-slo[2]:.2f} mm    y range [{slo[1]:.2f}, {shi[1]:.2f}]")

# the arms sit at the x extremes; slice just inside one of them
arm_x = slo[0] + 1.0
holes = sorted(circles_in_arm(stock, arm_x), key=lambda h: -h[2])
print(f"\nround features in the arm at x={arm_x:.1f} (y, z, dia):")
for h in holes[:6]:
    print(f"   y={h[0]:8.2f}  z={h[1]:7.2f}  dia={h[2]:6.2f}")

if holes:
    hub_y = holes[0][0]
    hub_d = holes[0][2]
    print(f"\nlargest = servo shaft/idler hub:  y = {hub_y:.2f}, dia {hub_d:.2f}")
else:
    hub_y = None

band_lo = 23.5 - 1.0
band_hi = 23.5 + C.LEG_LINK_EXT + 1.0
print(f"closure band (长U支架_tall):       y = [{band_lo:.2f}, {band_hi:.2f}]")

# A servo hangs from its hub toward the web end. Its reach past the hub axis is
# the body dimension measured from the shaft axis -- take the larger half-span.
reach = max(sz) / 2.0
print(f"\nservo half-span from shaft axis (worst case): {reach:.2f} mm")
if hub_y is not None:
    occupies_to = hub_y - reach
    margin = occupies_to - band_hi
    print(f"servo body would reach down to y = {occupies_to:.2f}")
    print(f"closure top is at            y = {band_hi:.2f}")
    verdict = "CLEARS" if margin > 0 else "COLLIDES"
    print(f"\n  -> {verdict}   margin = {margin:+.2f} mm")
    print("     (worst-case: assumes the servo's longest axis points down the U)")

# 短U support: same test on the concept part's band
sh = mesh_of(os.path.join(vendor_paths.stock_step_dir(), "短U支架.step"))
hlo, hhi = sh.bounds
mid = (hlo[1] + hhi[1]) / 2
print(f"\n短U支架 y range [{hlo[1]:.2f}, {hhi[1]:.2f}], closure band "
      f"[{mid-6:.2f}, {mid+6:.2f}]")
sholes = sorted(circles_in_arm(sh, hlo[0] + 1.0), key=lambda h: -h[2])
if sholes:
    print(f"largest hub y = {sholes[0][0]:.2f}, dia {sholes[0][2]:.2f} -> "
          f"servo reaches to y = {sholes[0][0]-reach:.2f}, band top "
          f"{mid+6:.2f}  -> "
          f"{'CLEARS' if sholes[0][0]-reach > mid+6 else 'COLLIDES'}")
print("=" * 74)
