"""
TelescopeBot: Waist Box -- lower torso (build123d)

Generates two 3D-printable parts, both exported ALREADY IN PRINT
ORIENTATION (print as exported, no slicer rotation):

1. ``waist_box`` -- open-top rectangular box, printed floor-down.
   Carries: ST3215 waist-yaw pocket in the floor center (shaft DOWN
   through the floor), four SCS15 hip bays on the side walls (simplified
   draft pockets: horn window + M2 clearance holes + locating recess),
   a battery tray low at the rear, deck-support ribs + M3 pilots on the
   side-wall rims, four M3-pilot lid posts, and vent slots.

2. ``spine_servo_deck`` -- flat plate that bolts onto the side-wall rims
   and carries the two FS5103R spine servos, output shafts straight UP,
   shaft axes exactly SPINE_ROD_SPACING_MM apart, symmetric about the
   box center. Servos drop into flange cutouts from above and bolt down
   with M3 screws + nuts at the researched 49.5 x 10.0 hole pattern
   BEFORE the deck is screwed into the box.

WIDTH CHOICE (required statement): the waist telescopes OVER the chest --
interior width = CHEST_EXT_WIDTH_MM + 2 x CHEST_SIDE_CLEARANCE_MM =
156 mm, wider than the ~150 mm chest box, so the chest can descend INTO
the open waist mouth. The alternative (chest outside the waist) is
IMPOSSIBLE at SPINE_ROD_SPACING_MM = 120: chest internal ~144 mm caps
the waist interior half-width at ~68 mm, but an FS5103R body centered
10.05 mm outboard of a shaft at x = +/-60 reaches x = 70.4 mm. In the
current stack the chest actually bottoms out on the horn-coupler tops
(above the rim), but the mouth is sized so nothing in the waist ever
constrains the stroke.

WHY THE DECK IS A SEPARATE PART: an integrated mid-height shelf would be
a ~156 mm unsupported horizontal bridge over the battery/hip volume --
unprintable support-free floor-down. A flat bolt-on plate prints
support-free on its own, and M3 pilots drilled straight down into the
rim (backed by full-height internal ribs) give deep vertical thread
engagement with zero overhangs.

HIP BAY LAYOUT (draft deviation, deliberate): all four SCS15 bays sit on
the SIDE walls with shafts out +/-X, paired toward the FRONT bottom
corners (y = +22 and +44). The rear floor is owned by the 110 x 40
battery tray -- a rear-corner servo pocket cannot coexist with it in a
156 mm interior. The per-leg roll DOF hangs off an external bracket on
the outboard horn in a later part.

Clearances verified in this draft (see asserts): spine servos hang
25.9 mm below the deck top and clear the battery, the ST3215, and both
hip bays; a 32-dia x 48-tall column above each spine flange is open sky
for the 28 dia x 34 mm horn coupler from spine_base.py.

MEASURE BEFORE TRUSTING: battery envelope and every UNVERIFIED constant
in hardware_constants.py; caliper before printing this much PETG.
"""

from pathlib import Path

from build123d import (
    Align,
    BuildPart,
    Box,
    Cylinder,
    Locations,
    Mode,
    export_step,
    export_stl,
)

from hardware_constants import (
    BATTERY_BAY_HEIGHT,
    BATTERY_BAY_LENGTH,
    BATTERY_BAY_WIDTH,
    FS5103R_BODY_LENGTH,
    FS5103R_BODY_WIDTH,
    FS5103R_FLANGE_LENGTH,
    FS5103R_HOLE_SPACING_LENGTH,
    FS5103R_HOLE_SPACING_WIDTH,
    FS5103R_POCKET_CLEARANCE,
    FS5103R_SHAFT_OFFSET_FROM_CENTER,
    FS5103R_TAB_UNDERSIDE_HEIGHT,
    M3_CLEAR,
    M3_PILOT,
    SCS15_BODY_LENGTH,
    SCS15_BODY_WIDTH,
    SCS15_ROUND_HORN_DIA,
    SCS15_SHAFT_FROM_FRONT_FACE,
    SCS15_TOP_CENTER_HOLE_BEHIND_AXIS,
    SCS15_TOP_COLS_BEHIND_AXIS,
    SCS15_TOP_FAR_CENTER_HOLE_BEHIND_AXIS,
    SCS15_TOP_ROW_SPACING,
    SPINE_ROD_SPACING_MM,
    ST3215_BODY_LENGTH,
    ST3215_BODY_WIDTH,
    ST3215_BOSS_DIA,
    ST3215_BOSS_PROTRUSION,
    ST3215_TOP_HOLE_SQUARE,
    WALL_MM,
)

# ------------------------------------------------------------- architecture
WALL = 4.0                   # box wall (>= WALL_MM house minimum)
FLOOR_T = 4.0                # box floor thickness
CHEST_EXT_WIDTH_MM = 150.0   # chest box external width -- ASSUMED, see docstring
CHEST_SIDE_CLEARANCE_MM = 3.0  # per-side slop so the chest drops into the mouth
INNER_W = CHEST_EXT_WIDTH_MM + 2 * CHEST_SIDE_CLEARANCE_MM   # 156.0 (X)
INNER_D = 114.0              # interior depth (Y): sized so the rear battery
                             # tray clears the ST3215 pad (asserted below)
RIM_Z = 60.0                 # wall top / deck seat height above the bed
OUTER_W = INNER_W + 2 * WALL                                 # 164.0
OUTER_D = INNER_D + 2 * WALL                                 # 122.0

# Spine deck (separate flat part that seats on the side-wall rims)
DECK_T = 5.0                 # deck plate thickness; mount plane = RIM_Z + DECK_T
DECK_Y_MIN = -44.0           # deck covers the FS5103R flanges (-37.05..+16.95)
DECK_Y_MAX = 24.0
DECK_SCREW_X = INNER_W / 2   # screw line straddles wall (4) + backing rib (4)
DECK_SCREW_YS = (-40.0, -10.0, 6.0)   # 3 M3 self-tappers per side rim
DECK_RIB_W = 6.0             # full-height rib backing each rim pilot (Y size)
DECK_RIB_D = 4.0             # rib protrusion inward from the wall (X size)

# Spine servo placement (FS5103R long axis along Y, shaft toward +Y front)
SPINE_SHAFT_X = SPINE_ROD_SPACING_MM / 2         # +/-60.0, symmetric
SPINE_BODY_CENTER_Y = -FS5103R_SHAFT_OFFSET_FROM_CENTER   # shaft axis at y=0
COUPLER_CLEAR_DIA = 32.0     # 28 dia coupler + 2/side (checked open, not cut)
COUPLER_CLEAR_H = 48.0       # 34 tall coupler + spline stack + margin

# Hip bays (4x SCS15, side walls, body vertical, shaft out +/-X)
HIP_BAY_YS = (22.0, 44.0)    # shaft-axis Y per side: front-corner pair
HIP_LIFT = 2.0               # servo bottom face sits this far above the floor
HIP_AXIS_Z = FLOOR_T + HIP_LIFT + SCS15_SHAFT_FROM_FRONT_FACE   # 16.15
HIP_FIT = 0.5                # locating-recess slop on the servo top face
HIP_RECESS_DEPTH = 0.6       # shallow outline recess in the wall inner face
HORN_CLEAR_DIA = SCS15_ROUND_HORN_DIA + 2.05     # 22.0 window for the horn
M2_CLEAR = 2.4               # clearance for M2 self-tappers -- ASSUMED (house
                             # constants only define the 1.8 pilot)

# Battery tray (rear floor; battery 110 long lies along X against rear wall)
BAT_CLR = 0.5                # per-side slop around the battery envelope
BAT_RIB_T = 3.0              # retaining rib thickness
BAT_RIB_H = 10.0             # rib height above the floor top
BAT_FRONT_Y = -INNER_D / 2 + BATTERY_BAY_WIDTH + BAT_CLR     # -16.5 front face

# ST3215 waist-yaw pocket (floor center, shaft DOWN through the floor)
ST_FIT = 0.5                 # pocket slop around the body
ST_PAD_WALL = 3.0            # pocket wall thickness
ST_POCKET_DEPTH = 12.0       # body capture depth; pad top = FLOOR_T + 12
ST_CENTER_HOLE_DIA = 12.0    # spline + horn-hub pass-through -- ASSUMED
ST_SCREW_CLEAR = M3_CLEAR    # boss holes are M3-class (ST3215_TOP_HOLE_DIA=2.5 tap,
                             # ST3215_HORN_SCREW_M=3): M3 screws from below need
                             # 3.4 clearance, not M2's 2.4
ST_PAD_X = ST3215_BODY_LENGTH + ST_FIT + 2 * ST_PAD_WALL     # 51.9
ST_PAD_Y = ST3215_BODY_WIDTH + ST_FIT + 2 * ST_PAD_WALL      # 31.3

# Vent slots (side walls only, per requirement)
VENT_W = 4.0                 # slot width (also the only bridge: 4 mm, flat)
VENT_H = 35.0
VENT_Z0 = 14.0               # keep 10 mm of solid wall above the floor
VENT_YS = (-34.0, -26.0, -18.0, 0.0)   # clear of hip bays, ribs, corner posts

# Lid posts (M3 pilots for a later cover; full-height, fused to walls)
LID_POST = 8.0
LID_POST_XYS = ((32.0, 53.0), (-32.0, 53.0), (74.0, -53.0), (-74.0, -53.0))
PILOT_DEPTH = 12.0           # M3 self-tap engagement, straight down

# --------------------------------------------------- derived + sanity checks
SPINE_CUT_X = FS5103R_BODY_WIDTH + FS5103R_POCKET_CLEARANCE    # 20.65
SPINE_CUT_Y = FS5103R_BODY_LENGTH + FS5103R_POCKET_CLEARANCE   # 40.65
_spine_body_max_x = SPINE_SHAFT_X + FS5103R_BODY_WIDTH / 2 \
    + FS5103R_POCKET_CLEARANCE / 2                             # 70.4 outboard face
_spine_body_max_y = SPINE_BODY_CENTER_Y + FS5103R_BODY_LENGTH / 2   # +10.03
_spine_bottom_z = RIM_Z + DECK_T - FS5103R_TAB_UNDERSIDE_HEIGHT     # 39.1
assert WALL >= WALL_MM and FLOOR_T >= WALL_MM
assert _spine_body_max_x < INNER_W / 2 - DECK_RIB_D, "spine servo hits deck ribs"
assert _spine_bottom_z > FLOOR_T + BATTERY_BAY_HEIGHT + 2.0, \
    "spine servo hangs into the battery"
assert min(HIP_BAY_YS) - (SCS15_BODY_WIDTH + HIP_FIT) / 2 > _spine_body_max_y, \
    "hip bay overlaps hanging spine servo"
assert min(HIP_BAY_YS) - (SCS15_BODY_WIDTH + HIP_FIT) / 2 > BAT_FRONT_Y + BAT_RIB_T, \
    "hip bay overlaps battery tray"
assert max(HIP_BAY_YS) + SCS15_BODY_WIDTH / 2 < INNER_D / 2, "hip bay exits box"
assert BATTERY_BAY_LENGTH + 2 * BAT_CLR + 2 * BAT_RIB_T < INNER_W, "battery too long"
assert INNER_W / 2 - SPINE_SHAFT_X >= COUPLER_CLEAR_DIA / 2 + 2.0, \
    "wall intrudes on coupler clearance column"
assert ST_PAD_Y / 2 < -BAT_FRONT_Y - BAT_CLR, \
    "ST3215 pad intrudes into the battery envelope"


def create_waist_box():
    """Box in print orientation: floor on the bed (z=0), open top at RIM_Z."""
    with BuildPart() as box:
        # Shell: outer block minus interior cavity (cavity overshoots the rim
        # by 1 so the top face is cleanly open).
        Box(OUTER_W, OUTER_D, RIM_Z, align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, 0, FLOOR_T)):
            Box(
                INNER_W,
                INNER_D,
                RIM_Z - FLOOR_T + 1.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )

        # Deck-support ribs: full-height strips on the side-wall inner faces.
        # Each backs a rim pilot so the M3 self-tapper lands in 8 mm of
        # material (4 wall + 4 rib) instead of a bare 4 mm wall.
        with Locations(
            *[
                (s * (INNER_W / 2 - DECK_RIB_D / 2), y, 0)
                for s in (1, -1)
                for y in DECK_SCREW_YS
            ]
        ):
            Box(DECK_RIB_D, DECK_RIB_W, RIM_Z,
                align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Lid posts: full-height square posts fused to the walls (front pair
        # inboard of the hip bays, rear pair in the true corners).
        with Locations(*[(x, y, 0) for x, y in LID_POST_XYS]):
            Box(LID_POST, LID_POST, RIM_Z,
                align=(Align.CENTER, Align.CENTER, Align.MIN))

        # ST3215 waist-yaw pad: raised pocket in the floor center; servo
        # drops in shaft-down, output boss seats in a floor recess, spline
        # exits below the floor for the pelvis-side horn.
        pad_top = FLOOR_T + ST_POCKET_DEPTH
        Box(ST_PAD_X, ST_PAD_Y, pad_top,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, 0, FLOOR_T)):
            Box(
                ST3215_BODY_LENGTH + ST_FIT,
                ST3215_BODY_WIDTH + ST_FIT,
                ST_POCKET_DEPTH + 1.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )
        # Cable notch in the +X pad wall.
        with Locations((ST_PAD_X / 2, 0, pad_top - 6.0)):
            Box(10.0, 10.0, 7.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT)
        # Output-boss recess (boss sinks into the floor)...
        with Locations((0, 0, FLOOR_T - ST3215_BOSS_PROTRUSION)):
            Cylinder(
                radius=(ST3215_BOSS_DIA + ST_FIT) / 2,
                height=ST3215_BOSS_PROTRUSION + 0.5,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )
        # ...spline/horn-hub pass-through, and M3 clearance holes (screws
        # come up from below the floor into the boss's 9.9-square pattern;
        # only ~1.5 mm of floor remains under the boss -- retention only,
        # the pocket walls take the yaw torque).
        sq = ST3215_TOP_HOLE_SQUARE / 2
        for cx, cy, r in [(0.0, 0.0, ST_CENTER_HOLE_DIA / 2)] + [
            (sx * sq, sy * sq, ST_SCREW_CLEAR / 2)
            for sx in (1, -1)
            for sy in (1, -1)
        ]:
            with Locations((cx, cy, -0.5)):
                Cylinder(radius=r, height=FLOOR_T + 1.0,
                         align=(Align.CENTER, Align.CENTER, Align.MIN),
                         mode=Mode.SUBTRACT)

        # Battery tray: rear floor, battery lies along X against the rear
        # wall, retained by two end ribs and two short front ribs (the gap
        # between the front ribs clears the ST3215 pad).
        bat_end_x = BATTERY_BAY_LENGTH / 2 + BAT_CLR + BAT_RIB_T / 2
        with Locations(*[(s * bat_end_x, -INNER_D / 2 + 15.0, 0) for s in (1, -1)]):
            Box(BAT_RIB_T, 25.0, FLOOR_T + BAT_RIB_H,
                align=(Align.CENTER, Align.MIN, Align.MIN))
        with Locations(*[(s * 40.0, BAT_FRONT_Y + BAT_RIB_T / 2, 0) for s in (1, -1)]):
            Box(20.0, BAT_RIB_T, FLOOR_T + BAT_RIB_H,
                align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Hip bays: per side wall, two SCS15 draft bays (body vertical,
        # bottom face HIP_LIFT above the floor, shaft out +/-X through the
        # wall). Features per bay: shallow locating recess outlining the
        # servo top face, horn clearance window, and six M2 clearance holes
        # at the researched SCS15 top-face pattern ("behind the axis" = up,
        # because the body hangs upward from the low shaft).
        recess_z_center = FLOOR_T + HIP_LIFT - HIP_FIT / 2 \
            + (SCS15_BODY_LENGTH + HIP_FIT) / 2
        for s in (1, -1):
            wall_mid_x = s * (INNER_W / 2 + WALL / 2)
            for bay_y in HIP_BAY_YS:
                with Locations((s * INNER_W / 2, bay_y, recess_z_center)):
                    Box(2 * HIP_RECESS_DEPTH, SCS15_BODY_WIDTH + HIP_FIT,
                        SCS15_BODY_LENGTH + HIP_FIT,
                        align=(Align.CENTER, Align.CENTER, Align.CENTER),
                        mode=Mode.SUBTRACT)
                holes = [(bay_y, HIP_AXIS_Z, HORN_CLEAR_DIA / 2)]
                for col in SCS15_TOP_COLS_BEHIND_AXIS:
                    for row in (1, -1):
                        holes.append((bay_y + row * SCS15_TOP_ROW_SPACING / 2,
                                      HIP_AXIS_Z + col, M2_CLEAR / 2))
                for c in (SCS15_TOP_CENTER_HOLE_BEHIND_AXIS,
                          SCS15_TOP_FAR_CENTER_HOLE_BEHIND_AXIS):
                    holes.append((bay_y, HIP_AXIS_Z + c, M2_CLEAR / 2))
                for hy, hz, hr in holes:
                    with Locations((wall_mid_x, hy, hz)):
                        Cylinder(radius=hr, height=WALL + 2.0,
                                 rotation=(0, 90, 0), mode=Mode.SUBTRACT)

        # Vent slots through both side walls (top edge is a 4 mm flat bridge).
        with Locations(
            *[
                (s * (INNER_W / 2 + WALL / 2), y, VENT_Z0)
                for s in (1, -1)
                for y in VENT_YS
            ]
        ):
            Box(WALL + 2.0, VENT_W, VENT_H,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT)

        # M3 pilots, all drilled straight down from z = RIM_Z: deck screws
        # into the rib-backed rim line, lid screws into the four posts.
        pilot_xy = [(s * DECK_SCREW_X, y) for s in (1, -1) for y in DECK_SCREW_YS]
        pilot_xy += list(LID_POST_XYS)
        with Locations(*[(x, y, RIM_Z - PILOT_DEPTH) for x, y in pilot_xy]):
            Cylinder(radius=M3_PILOT / 2, height=PILOT_DEPTH + 0.5,
                     align=(Align.CENTER, Align.CENTER, Align.MIN),
                     mode=Mode.SUBTRACT)

    return box.part


def create_spine_servo_deck():
    """Deck in print orientation: flat on the bed, mount plane at z = DECK_T.

    Assembly: bolt both FS5103R servos into the cutouts (M3 + nut at the
    researched 49.5 x 10.0 flange pattern), drop the deck onto the rims,
    drive six M3 self-tappers down into the rib-backed rim pilots. Shafts
    point straight up at (+/-SPINE_ROD_SPACING_MM/2, 0); everything above
    the flange is open sky for the 28 dia x 34 horn coupler.
    """
    deck_d = DECK_Y_MAX - DECK_Y_MIN
    deck_yc = (DECK_Y_MAX + DECK_Y_MIN) / 2
    with BuildPart() as deck:
        with Locations((0, deck_yc, 0)):
            Box(OUTER_W, deck_d, DECK_T,
                align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Flange drop-in cutouts: body + clearance; the 54 mm flange tabs
        # overhang the cutout ends by ~6.7 mm and seat on the deck top.
        assert FS5103R_FLANGE_LENGTH > SPINE_CUT_Y + 8.0
        with Locations(
            *[(s * SPINE_SHAFT_X, SPINE_BODY_CENTER_Y, -0.5) for s in (1, -1)]
        ):
            Box(SPINE_CUT_X, SPINE_CUT_Y, DECK_T + 1.0,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT)

        # M3 clearance holes at the researched flange pattern (4 per servo)
        # plus the six deck-to-rim screw holes.
        holes = [
            (s * SPINE_SHAFT_X + sx * FS5103R_HOLE_SPACING_WIDTH / 2,
             SPINE_BODY_CENTER_Y + sy * FS5103R_HOLE_SPACING_LENGTH / 2)
            for s in (1, -1)
            for sx in (1, -1)
            for sy in (1, -1)
        ]
        holes += [(s * DECK_SCREW_X, y) for s in (1, -1) for y in DECK_SCREW_YS]
        with Locations(*[(x, y, -0.5) for x, y in holes]):
            Cylinder(radius=M3_CLEAR / 2, height=DECK_T + 1.0,
                     align=(Align.CENTER, Align.CENTER, Align.MIN),
                     mode=Mode.SUBTRACT)

    return deck.part


if __name__ == "__main__":
    out = Path(__file__).parent / "output"
    out.mkdir(exist_ok=True)

    parts = (
        ("waist_box", create_waist_box()),
        ("spine_servo_deck", create_spine_servo_deck()),
    )
    for name, part in parts:
        export_stl(part, str(out / f"{name}.stl"))
        export_step(part, str(out / f"{name}.step"))
        bb = part.bounding_box()
        print(
            f"{name}: {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm, "
            f"volume {part.volume / 1000:.1f} cm^3 -> {name}.stl / .step"
        )
