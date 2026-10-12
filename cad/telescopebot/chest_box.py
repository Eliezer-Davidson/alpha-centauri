"""
TelescopeBot: Chest Box -- the moving carriage (build123d)

One printable part: an open-top box that rides up and down the two vertical
M8x1.25 spine rods. Two reinforced nut towers (fused into the rear wall)
carry side-loaded captive M8 hex nuts; the FS5103R-driven rods below (see
spine_base.py horn coupler) thread through those nuts to raise and lower the
whole chest 0..25 cm.

Payload provisions:
  * Jetson devkit standoffs on the floor (Orin Nano / Nano P3449 share one
    86 x 58 pattern -- switching Jetson models is a constants edit).
  * RealSense D435/D435i on a raised, chamfered boss row at the top front
    (2x M3 clearance at the 45 mm rear-hole spacing; screws driven from
    inside; 5.0 mm total stack so M3x8 hits the 3.0 mm max insertion).
  * LM2596 buck bay (2 diagonal bosses + edge rails, open ends for wires,
    trimpot faces up) on the right floor strip.
  * 40 mm exhaust fan on the rear wall (octagonal opening -- prints
    support-free), intake vent slots on the front wall.
  * MG996R shoulder pockets in both side walls, gable-topped (45 deg roofs,
    no bridges), with 6 mm of local wall for the flange self-tappers.
  * 10 mm grommet hole low on the rear wall for 12 V power entry.

PRINT ORIENTATION: exported exactly as printed -- floor on the bed, open
top up. Every overhang is vertical, 45 deg, or a small flat bridge (nut
slot ceilings 13.4 mm, vent slot tops 4 mm, octagon flat 15.8 mm). The one
knowing exception: the 10 mm round grommet hole (a rubber grommet needs a
round hole; a <=10 mm circular bridge prints acceptably).

ASSEMBLY: drop an M8 nut into each rear slot (flats gripped by the 13.4 mm
slot walls), then feed the rods up through the 8.5 mm floor+tower bores and
thread them through the nuts. With a rod through it a nut cannot translate
or rotate -- captive in use, no tools, no glue.
"""

from math import sqrt
from pathlib import Path

from build123d import (
    Align,
    Box,
    BuildPart,
    BuildSketch,
    Cylinder,
    Locations,
    Mode,
    Plane,
    Polygon,
    Rectangle,
    RegularPolygon,
    export_step,
    export_stl,
    extrude,
)

from hardware_constants import (
    D435_REAR_M3_MAX_INSERTION,
    D435_REAR_M3_SPACING,
    FAN40_HOLE_SPACING,
    FAN40_OPENING_DIA,
    LM2596_BOARD_LENGTH,
    LM2596_BOARD_WIDTH,
    LM2596_HOLE_SPACING_DX,
    LM2596_HOLE_SPACING_DY,
    M3_CLEAR,
    M3_PILOT,
    M8_NUT_AF,
    M8_NUT_POCKET_DEPTH,
    MG996R_BODY_LENGTH,
    MG996R_BODY_WIDTH,
    MG996R_HOLE_SPACING_LENGTH,
    MG996R_HOLE_SPACING_WIDTH,
    ORIN_NANO_BOSS_HEIGHT_MIN,
    ORIN_NANO_BOSS_OD_MAX,
    ORIN_NANO_HOLE_SPACING_X,
    ORIN_NANO_HOLE_SPACING_Y,
    SPINE_ROD_SPACING_MM,
    WALL_MM,
)

# ------------------------------------------------------------ box envelope
# X = width (rods at +-60), Y = depth (+Y = front / camera side), Z = up.
BOX_WIDTH = 150.0            # external; rods at +-60 leave 15 mm side walls
BOX_DEPTH = 130.0            # sized so the Jetson (100 long, mounted along Y)
                             # and the LM2596 bay coexist on the floor
BOX_HEIGHT = 85.0            # clears shoulder pocket gables + fan + camera row
FLOOR_T = 4.0                # floor; > WALL_MM so floor pilots keep 2 mm meat
WALL = WALL_MM               # every vertical wall (house minimum)
EMBED = 0.5                  # solid overlap where added bosses meet walls/floor
                             # (robust OCCT fuses, no coincident-face unions)
OVERSHOOT = 0.5              # cutters run past faces so booleans never leave skins

# --------------------------------------------------------------- nut towers
# Rear-corner blocks fused through the rear wall; the rods live at the back
# of the chest so the floor center stays free for the Jetson.
ROD_X = SPINE_ROD_SPACING_MM / 2         # +-60 from center
ROD_CLEARANCE_DIA = 8.5                  # task-specified rod clearance bore
TOWER_BORE_INNER_WALL = 14.0             # bore axis -> tower inboard face
TOWER_WIDTH = BOX_WIDTH / 2 - ROD_X + TOWER_BORE_INNER_WALL   # 29: reaches side wall
TOWER_DEPTH = 31.0                       # rear exterior face -> tower front face
TOWER_HEIGHT = 48.0                      # long bore = rod bushing against pitch
ROD_Y = -BOX_DEPTH / 2 + TOWER_DEPTH / 2                      # -49.5 (bore axis)
TOWER_CX = BOX_WIDTH / 2 - TOWER_WIDTH / 2                    # +-60.5 (block center)
# Side-load nut slot: opens through the rear wall, 13.4 across flats grips the
# nut against rotation, rod traps it. Slot runs just past the nut's
# corner-to-corner half-diagonal so the nut centers on the bore.
NUT_SLOT_BOTTOM_Z = 20.0
NUT_SLOT_END_Y = ROD_Y + M8_NUT_AF / sqrt(3) + 0.5            # -41.26

# ------------------------------------------------- Jetson devkit standoffs
# One 86 x 58 pattern serves Orin Nano AND original Nano devkits (verified
# identical in hardware_constants). Board LENGTH (100/86 side) runs along Y.
# NOTE: the devkit holes are 2.75 mm -- M3 will NOT pass (researched
# constants), so the standoffs take M2.5 self-tappers, not the M3 the
# original spec guessed. Swapping Jetson models = edit these 4 lines.
JETSON_SPAN_Y = ORIN_NANO_HOLE_SPACING_X          # 86, board length direction
JETSON_SPAN_X = ORIN_NANO_HOLE_SPACING_Y          # 58, board width direction
JETSON_PATTERN_CX = 2.0      # shifts board so the I/O edge faces -X with
                             # 28 mm of connector room to the left wall
JETSON_PILOT = 2.2           # M2.5 self-tap pilot (M2.5 because 2.75 mm holes)
JETSON_BOSS_OD = ORIN_NANO_BOSS_OD_MAX            # 8.0 official keep-out
JETSON_BOSS_H = ORIN_NANO_BOSS_HEIGHT_MIN + 1.0   # 6.0 clears 4.3 underside parts

# --------------------------------------------------- RealSense D435 boss row
# Camera hangs on the front wall exterior, top edge ~4.5 above the box rim
# for a clear forward FOV. Screws (M3 clearance) drive from inside: 3 wall
# + 2 proud boss = 5.0 stack, so M3x8 protrudes exactly the 3.0 max insertion.
REALSENSE_HOLE_Z = 77.0
REALSENSE_STRIP_HALF_H = 6.0             # boss row 71..83 tall
REALSENSE_STRIP_PROUD = 2.0              # stand-off from the wall face
REALSENSE_STRIP_LEN = 60.0               # spans the 45 mm hole pair + margin
REALSENSE_SCREW_STACK = WALL + REALSENSE_STRIP_PROUD          # doc: 5.0
assert REALSENSE_SCREW_STACK + D435_REAR_M3_MAX_INSERTION == 8.0  # M3x8

# ------------------------------------------------------------- LM2596 bay
# Right floor strip (beside the Jetson, under the right shoulder servo --
# 2.8 mm clear of the servo body). Board length along Y; two diagonal
# bosses match the DX x DY corner holes; side rails retain the board edges,
# ends stay open for wiring; trimpot faces the open top.
LM_BAY_CX = 56.0
LM_BAY_CY = 25.0
LM_BOSS_OD = 7.0
LM_BOSS_H = 4.0              # board floats above floor wiring
LM_RAIL_T = 3.0              # house wall minimum
LM_RAIL_CLEAR = 0.2          # per side, board drop-in fit
LM_RAIL_TOP_Z = 12.0         # retains 4 mm of board edge above the bosses
LM_RAIL_LEN = LM2596_BOARD_LENGTH + 4.0
LM_RAIL_DX = LM2596_BOARD_WIDTH / 2 + LM_RAIL_CLEAR + LM_RAIL_T / 2

# --------------------------------------------------------- MG996R shoulders
# Through-pockets in both side walls, servo body vertical (shaft on X,
# pointing out), flange on the wall exterior. 45 deg gable roof instead of a
# 41 mm bridge. Interior pads thicken the wall 3 -> 6 mm so the flange
# self-tappers (M3 + washers per constants: clone holes are 4.0-4.3) bite.
SERVO_POCKET_CLEAR = 0.5     # per side around the MG996R body
SHOULDER_CY = 30.0           # forward of the towers, clear of the nut slots
SHOULDER_CZ = 50.0           # body bottom clears Jetson I/O + LM2596 parts
POCKET_W = MG996R_BODY_WIDTH + 2 * SERVO_POCKET_CLEAR         # 21.0 along Y
POCKET_H = MG996R_BODY_LENGTH + 2 * SERVO_POCKET_CLEAR        # 41.3 along Z
SHOULDER_PAD_T = 3.0         # interior thickening (total wall 6.0)
SHOULDER_PAD_W = 36.0        # pad spans pocket + pilots + margin (Y 12..48)
SHOULDER_PAD_Z0 = 17.0       # pad up to the box rim

# ------------------------------------------------------- rear wall: fan + power
# Octagonal fan opening (apothem = the 38.2 opening radius): 45 deg diagonals
# and a 15.8 mm flat top bridge = support-free in a vertical wall.
FAN_CZ = 42.0
GROMMET_DIA = 10.0           # task-specified 12 V wire entry
GROMMET_X = 35.0             # rod side of the wall, near the LM2596 bay
GROMMET_Z = 12.0             # "low": hole bottom 3 mm above the floor top

# --------------------------------------------------------- front wall vents
VENT_COUNT = 6
VENT_W = 4.0                 # slot top is a 4 mm bridge -- prints clean
VENT_H = 25.0
VENT_PITCH = 10.0
VENT_CZ = 27.5               # slots span Z 15..40, below the camera row


def create_chest_box():
    """Chest box in print orientation: floor on the bed (Z=0), open top up."""
    with BuildPart() as chest:
        # ---------------------------------------------------------- shell
        Box(BOX_WIDTH, BOX_DEPTH, BOX_HEIGHT,
            align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((0, 0, FLOOR_T)):
            Box(BOX_WIDTH - 2 * WALL, BOX_DEPTH - 2 * WALL,
                BOX_HEIGHT - FLOOR_T,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT)

        # ------------------------------------------------------ nut towers
        with Locations((TOWER_CX, ROD_Y, 0), (-TOWER_CX, ROD_Y, 0)):
            Box(TOWER_WIDTH, TOWER_DEPTH, TOWER_HEIGHT,
                align=(Align.CENTER, Align.CENTER, Align.MIN))

        # ------------------------------------------- shoulder pads (walls 3->6)
        for side in (1, -1):
            pad_cx = side * (BOX_WIDTH / 2 - WALL - SHOULDER_PAD_T / 2 + EMBED / 2)
            with Locations((pad_cx, SHOULDER_CY, SHOULDER_PAD_Z0)):
                Box(SHOULDER_PAD_T + EMBED, SHOULDER_PAD_W,
                    BOX_HEIGHT - SHOULDER_PAD_Z0,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))

        # ------------------------------------------------- Jetson standoffs
        jetson_holes = [
            (JETSON_PATTERN_CX + sx * JETSON_SPAN_X / 2, sy * JETSON_SPAN_Y / 2)
            for sx in (1, -1) for sy in (1, -1)
        ]
        with Locations(*[(x, y, FLOOR_T - EMBED) for x, y in jetson_holes]):
            Cylinder(JETSON_BOSS_OD / 2, JETSON_BOSS_H + EMBED,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))

        # ------------------------------------------- RealSense boss row (front)
        # Chamfered underside (45 deg) so the 2 mm proud row prints clean.
        y_wall = BOX_DEPTH / 2
        y_face = y_wall + REALSENSE_STRIP_PROUD
        z_bot = REALSENSE_HOLE_Z - REALSENSE_STRIP_HALF_H
        z_top = REALSENSE_HOLE_Z + REALSENSE_STRIP_HALF_H
        with BuildSketch(Plane.YZ.offset(-REALSENSE_STRIP_LEN / 2)):
            Polygon(
                (y_wall - EMBED, z_bot - REALSENSE_STRIP_PROUD - EMBED),
                (y_face, z_bot),
                (y_face, z_top),
                (y_wall - EMBED, z_top),
                align=None,
            )
        extrude(amount=REALSENSE_STRIP_LEN)

        # ------------------------------------------------------- LM2596 bay
        lm_holes = [
            (LM_BAY_CX - LM2596_HOLE_SPACING_DY / 2,
             LM_BAY_CY - LM2596_HOLE_SPACING_DX / 2),
            (LM_BAY_CX + LM2596_HOLE_SPACING_DY / 2,
             LM_BAY_CY + LM2596_HOLE_SPACING_DX / 2),
        ]
        with Locations(*[(x, y, FLOOR_T - EMBED) for x, y in lm_holes]):
            Cylinder(LM_BOSS_OD / 2, LM_BOSS_H + EMBED,
                     align=(Align.CENTER, Align.CENTER, Align.MIN))
        with Locations((LM_BAY_CX - LM_RAIL_DX, LM_BAY_CY, FLOOR_T - EMBED),
                       (LM_BAY_CX + LM_RAIL_DX, LM_BAY_CY, FLOOR_T - EMBED)):
            Box(LM_RAIL_T, LM_RAIL_LEN, LM_RAIL_TOP_Z - FLOOR_T + EMBED,
                align=(Align.CENTER, Align.CENTER, Align.MIN))

        # ========================================================== cuts ==
        # Rod clearance bores: through tower AND floor, full height.
        with Locations((ROD_X, ROD_Y, -OVERSHOOT), (-ROD_X, ROD_Y, -OVERSHOOT)):
            Cylinder(ROD_CLEARANCE_DIA / 2, TOWER_HEIGHT + 2 * OVERSHOOT,
                     align=(Align.CENTER, Align.CENTER, Align.MIN),
                     mode=Mode.SUBTRACT)

        # Captive nut slots: side-load from the rear, 13.4 flats, 7.0 tall.
        slot_y0 = -BOX_DEPTH / 2 - OVERSHOOT
        with Locations((ROD_X, slot_y0, NUT_SLOT_BOTTOM_Z),
                       (-ROD_X, slot_y0, NUT_SLOT_BOTTOM_Z)):
            Box(M8_NUT_AF, NUT_SLOT_END_Y - slot_y0, M8_NUT_POCKET_DEPTH,
                align=(Align.CENTER, Align.MIN, Align.MIN),
                mode=Mode.SUBTRACT)

        # Shoulder pockets: rectangle + 45-rotated square = gable roof.
        for side in (1, -1):
            inner_x = BOX_WIDTH / 2 - WALL - SHOULDER_PAD_T   # 69
            with BuildSketch(Plane.YZ.offset(side * inner_x)):
                with Locations((SHOULDER_CY, SHOULDER_CZ)):
                    Rectangle(POCKET_W, POCKET_H)
                with Locations((SHOULDER_CY, SHOULDER_CZ + POCKET_H / 2)):
                    Rectangle(POCKET_W / sqrt(2), POCKET_W / sqrt(2),
                              rotation=45)
            extrude(amount=side * (WALL + SHOULDER_PAD_T + OVERSHOOT),
                    mode=Mode.SUBTRACT)

        # Shoulder flange pilots: 4 per side through wall + pad (6 mm bite).
        pilot_len = WALL + SHOULDER_PAD_T + 2 * OVERSHOOT
        pilot_cx = BOX_WIDTH / 2 - (WALL + SHOULDER_PAD_T) / 2
        shoulder_pilots = [
            (side * pilot_cx,
             SHOULDER_CY + sy * MG996R_HOLE_SPACING_WIDTH / 2,
             SHOULDER_CZ + sz * MG996R_HOLE_SPACING_LENGTH / 2)
            for side in (1, -1) for sy in (1, -1) for sz in (1, -1)
        ]
        with Locations(*shoulder_pilots):
            Cylinder(M3_PILOT / 2, pilot_len, rotation=(0, 90, 0),
                     mode=Mode.SUBTRACT)

        # Fan opening: octagon, flats up/down (rotation=22.5), rear wall.
        with BuildSketch(Plane.XZ.offset(BOX_DEPTH / 2 - WALL - OVERSHOOT)):
            with Locations((0, FAN_CZ)):
                RegularPolygon(FAN40_OPENING_DIA / 2, 8,
                               major_radius=False, rotation=22.5)
        extrude(amount=WALL + 2 * OVERSHOOT, mode=Mode.SUBTRACT)

        # Fan mount pilots (M3 self-tap, standard 32 mm square).
        y_rear_mid = -(BOX_DEPTH - WALL) / 2
        fan_pilots = [
            (sx * FAN40_HOLE_SPACING / 2, y_rear_mid,
             FAN_CZ + sz * FAN40_HOLE_SPACING / 2)
            for sx in (1, -1) for sz in (1, -1)
        ]
        with Locations(*fan_pilots):
            Cylinder(M3_PILOT / 2, WALL + 2 * OVERSHOOT,
                     rotation=(90, 0, 0), mode=Mode.SUBTRACT)

        # 12 V grommet hole, low on the rear wall.
        with Locations((GROMMET_X, y_rear_mid, GROMMET_Z)):
            Cylinder(GROMMET_DIA / 2, WALL + 2 * OVERSHOOT,
                     rotation=(90, 0, 0), mode=Mode.SUBTRACT)

        # Front intake vent slots.
        vent_x0 = -VENT_PITCH * (VENT_COUNT - 1) / 2
        y_front_mid = (BOX_DEPTH - WALL) / 2
        with Locations(*[(vent_x0 + i * VENT_PITCH, y_front_mid, VENT_CZ)
                         for i in range(VENT_COUNT)]):
            Box(VENT_W, WALL + 2 * OVERSHOOT, VENT_H, mode=Mode.SUBTRACT)

        # RealSense M3 clearance holes through wall + boss row.
        rs_len = WALL + REALSENSE_STRIP_PROUD + 2 * OVERSHOOT
        rs_cy = BOX_DEPTH / 2 + (REALSENSE_STRIP_PROUD - WALL) / 2
        with Locations((D435_REAR_M3_SPACING / 2, rs_cy, REALSENSE_HOLE_Z),
                       (-D435_REAR_M3_SPACING / 2, rs_cy, REALSENSE_HOLE_Z)):
            Cylinder(M3_CLEAR / 2, rs_len, rotation=(90, 0, 0),
                     mode=Mode.SUBTRACT)

        # Jetson standoff pilots (M2.5 self-tap; 8 deep, 2 mm off the bed).
        with Locations(*[(x, y, FLOOR_T + JETSON_BOSS_H) for x, y in jetson_holes]):
            Cylinder(JETSON_PILOT / 2, 8.0,
                     align=(Align.CENTER, Align.CENTER, Align.MAX),
                     mode=Mode.SUBTRACT)

        # LM2596 pilots (M3 self-tap through the board's 3.0 corner holes).
        with Locations(*[(x, y, FLOOR_T + LM_BOSS_H) for x, y in lm_holes]):
            Cylinder(M3_PILOT / 2, 6.0,
                     align=(Align.CENTER, Align.CENTER, Align.MAX),
                     mode=Mode.SUBTRACT)

    return chest.part


if __name__ == "__main__":
    out = Path(__file__).parent / "output"
    out.mkdir(exist_ok=True)

    box = create_chest_box()
    assert len(box.solids()) == 1, f"expected 1 solid, got {len(box.solids())}"

    for name, part in (("chest_box", box),):
        export_stl(part, str(out / f"{name}.stl"))
        export_step(part, str(out / f"{name}.step"))
        bb = part.bounding_box()
        print(
            f"{name}: {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm, "
            f"volume {part.volume / 1000:.1f} cm^3 -> {name}.stl / .step"
        )
