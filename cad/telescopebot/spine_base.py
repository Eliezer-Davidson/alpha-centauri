"""
TelescopeBot: Spine Horn Coupler (build123d)

Generates two 3D-printable parts:

1. ``horn_coupler`` -- adapter that screws onto the round 25T plastic servo
   horn of an FS5103R (continuous rotation) on one end and swallows an M8
   threaded rod on the other, locked by two opposed M3 set screws that
   self-tap into the printed wall.

2. ``bore_coupon`` -- a bore-fit test ladder (5 holes, 7.6..8.4 mm) so the
   real M8 rod fit can be measured on THIS printer/material before trusting
   ROD_BORE_DIAMETER. Notch count on the edge identifies each bore
   (1 notch = 7.6, 5 notches = 8.4). An undersized bore that the rod can
   self-thread into gives free axial retention; pick the tightest bore you
   can still drive the rod into by hand.

Both parts are exported ALREADY IN PRINT ORIENTATION -- print as exported,
no rotation in the slicer:

* Coupler prints rod-socket-end DOWN: full 28 mm disc on the bed, the only
  bridge is the 8.2 mm socket ceiling, and the horn recess + M2 pilot holes
  open upward so they print clean.  In assembly the part is flipped (horn
  below, rod above).

MEASURE BEFORE TRUSTING: HORN_DIAMETER and HORN_SCREW_PITCH_CIRCLE are for
a nominal 21 mm Futaba-style round horn. Caliper the actual horn shipped
with the FS5103R and update both constants (bore = measured + 0.25 fit
tolerance) before printing a second copy.
"""

from pathlib import Path

from build123d import (
    Align,
    Axis,
    BuildPart,
    Box,
    Cylinder,
    Locations,
    Mode,
    export_step,
    export_stl,
)
from math import cos, sin, radians

# ----------------------------------------------------------------- hardware
ROD_BORE_DIAMETER = 8.2      # M8 rod (7.8-8.0 actual) + FDM tolerance; refine via coupon
ROD_INSERT_DEPTH = 25.0
HORN_DIAMETER = 21.0         # round plastic horn on the FS5103R -- MEASURE IT
HORN_FIT_TOL = 0.3           # radial slop so the horn drops into its recess
HORN_RECESS_DEPTH = 3.0      # horn plate thickness + a little
HORN_SCREW_PITCH_CIRCLE = 14.0   # dia of the horn's screw-hole circle -- MEASURE IT
HORN_SCREW_PILOT = 1.8       # pilot for the M2 self-tappers that come with the horn
HORN_SCREW_COUNT = 4
HUB_CLEARANCE_DIAMETER = 10.0    # pocket over the horn hub / retaining-screw head
HUB_CLEARANCE_DEPTH = 2.5
SET_SCREW_PILOT = 2.7        # M3 set screw self-taps into this (9.9 mm wall engagement)
WEB_THICKNESS = 6.0          # solid wall between rod socket and horn recess
COUPLER_OUTER_DIAMETER = 28.0    # leaves 3.4 mm wall around the horn recess

TOTAL_HEIGHT = ROD_INSERT_DEPTH + WEB_THICKNESS + HORN_RECESS_DEPTH

# ------------------------------------------------------------- test coupon
COUPON_BORES = (7.6, 7.8, 8.0, 8.2, 8.4)
COUPON_THICKNESS = 6.0
COUPON_PITCH = 13.0          # bore-to-bore spacing
COUPON_WIDTH = 14.0


def create_horn_coupler():
    """Coupler in print orientation: rod socket opening at Z=0, horn recess at the top."""
    with BuildPart() as coupler:
        Cylinder(
            radius=COUPLER_OUTER_DIAMETER / 2,
            height=TOTAL_HEIGHT,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )

        # Rod socket: blind bore opening at the bottom (bed) face.
        Cylinder(
            radius=ROD_BORE_DIAMETER / 2,
            height=ROD_INSERT_DEPTH,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
            mode=Mode.SUBTRACT,
        )

        # Horn recess: opens at the top face.
        with Locations((0, 0, TOTAL_HEIGHT - HORN_RECESS_DEPTH)):
            Cylinder(
                radius=(HORN_DIAMETER + HORN_FIT_TOL) / 2,
                height=HORN_RECESS_DEPTH,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )

        # Clearance over the horn hub / retaining-screw head, under the recess.
        with Locations(
            (0, 0, TOTAL_HEIGHT - HORN_RECESS_DEPTH - HUB_CLEARANCE_DEPTH)
        ):
            Cylinder(
                radius=HUB_CLEARANCE_DIAMETER / 2,
                height=HUB_CLEARANCE_DEPTH,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )

        # Pilot holes for the horn's M2 self-tapping screws, drilled from the
        # top face into the web. Stop 1 mm short of the rod-socket ceiling.
        pilot_depth = HORN_RECESS_DEPTH + WEB_THICKNESS - 1.0
        pcr = HORN_SCREW_PITCH_CIRCLE / 2
        angles = [i * 360 / HORN_SCREW_COUNT for i in range(HORN_SCREW_COUNT)]
        with Locations(
            *[
                (pcr * cos(radians(a)), pcr * sin(radians(a)), TOTAL_HEIGHT - pilot_depth)
                for a in angles
            ]
        ):
            Cylinder(
                radius=HORN_SCREW_PILOT / 2,
                height=pilot_depth,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )

        # One through-hole across the rod socket at mid-depth = two opposed
        # M3 set-screw positions. M3 x 12 self-taps through the 9.9 mm wall.
        with Locations((0, 0, ROD_INSERT_DEPTH / 2)):
            Cylinder(
                radius=SET_SCREW_PILOT / 2,
                height=COUPLER_OUTER_DIAMETER,
                rotation=(90, 0, 0),
                mode=Mode.SUBTRACT,
            )

    return coupler.part


def create_bore_coupon():
    """Bore-fit ladder: five bores, edge notches count up from the smallest."""
    length = COUPON_PITCH * len(COUPON_BORES)
    with BuildPart() as coupon:
        Box(
            length,
            COUPON_WIDTH,
            COUPON_THICKNESS,
            align=(Align.MIN, Align.CENTER, Align.MIN),
        )
        for i, bore in enumerate(COUPON_BORES):
            x = COUPON_PITCH / 2 + i * COUPON_PITCH
            with Locations((x, 0, 0)):
                Cylinder(
                    radius=bore / 2,
                    height=COUPON_THICKNESS,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                    mode=Mode.SUBTRACT,
                )
            # i+1 identification notches on the +Y edge beside each bore
            for n in range(i + 1):
                nx = x - (i * 2.0) / 2 + n * 2.0
                with Locations((nx, COUPON_WIDTH / 2, COUPON_THICKNESS - 1.0)):
                    Box(
                        1.0,
                        3.0,
                        1.0,
                        align=(Align.CENTER, Align.CENTER, Align.MIN),
                        mode=Mode.SUBTRACT,
                    )
    return coupon.part


if __name__ == "__main__":
    out = Path(__file__).parent / "output"
    out.mkdir(exist_ok=True)

    coupler = create_horn_coupler()
    coupon = create_bore_coupon()

    for name, part in (("horn_coupler", coupler), ("bore_coupon", coupon)):
        export_stl(part, str(out / f"{name}.stl"))
        export_step(part, str(out / f"{name}.step"))
        bb = part.bounding_box()
        print(
            f"{name}: {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm, "
            f"volume {part.volume / 1000:.1f} cm^3 -> {name}.stl / .step"
        )
