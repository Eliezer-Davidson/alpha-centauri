#!/usr/bin/env python3
"""Generate OrcaSlicer presets for a FlashForge Guider 3 Plus.

OrcaSlicer ships FlashForge profiles for the Guider 2s and the Guider 3 Ultra
but NOT the Guider 3 Plus, and FlashForge's own preset repo has the same gap.
The Ultra is the wrong thing to substitute: it is a Klipper machine
(gcode_flavor=klipper, accel 20000), whereas the Plus runs FlashForge's own
firmware. Its gcode uses G161/G162/M132/M6/M7/M651/M652, which Klipper output
would not produce.

Every value below is sourced, not guessed:

  * bed / temps        FlashForge published specs -- 350x350x600, 320 C nozzle,
                       120 C bed
  * PLA parameters     FlashPrint 5.8.7's own profile.dat, section
                       "FlashForge Guider 3 Plus-0.4/PLA-1.75/Standard"
  * start / end gcode  a real .gx sliced by ffslicer for
                       ";machine_type: Guider 3 Plus", cross-checked against
                       OrcaSlicer's shipped Guider 2s override (identical
                       command sequence)
  * center origin      the .gx emits negative X/Y, so 0,0 is bed centre

The process preset deliberately departs from FlashForge's defaults where the
goal is a load-bearing bracket rather than a display print; each departure is
commented.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

BED = 350          # mm, square
HEIGHT = 600       # mm
HALF = BED // 2

# The GUI preset derives from this shipped, registered FlashForge model.
# It is chosen only because it is installed and already has the right 600 mm
# Z; its Klipper flavour and 20000 accel are both overridden.
GUI_PARENT = "Flashforge Guider 3 Ultra 0.4 Nozzle"
GUI_PARENT_MODEL = "Flashforge Guider 3 Ultra"

# REQUIRED for the GUI. Without a "version" key OrcaSlicer silently discards
# the user preset and reselects another printer -- it reverted to the Guider
# 3 Ultra every restart until this was added. No error is shown anywhere.
PRESET_VERSION = "2.3.0.0"

MACHINE_NAME = "FlashForge Guider 3 Plus 0.4 nozzle"
PROCESS_NAME = "0.20mm Structural @Guider3Plus 0.4"
FILAMENT_NAME = "Generic PLA @Guider3Plus"

# Verbatim from the Guider 2s override, with the purge line moved to this
# machine's front edge (Y -175 + FlashPrint's preExtrudeMargin of 8).
START_GCODE = "\n".join([
    "M118 X10 Y10 Z10",
    "M140 S[bed_temperature_initial_layer_single]; set initial bed temp",
    "M104 S[nozzle_temperature_initial_layer] T0; set initial extruder temp",
    "M107; disable cooling fan",
    "G90; absolute positioning",
    "G28; home axes",
    "M132 X Y A B; recall home offsets from EPROM",
    "G1 Z50.0 F420; adjust Z",
    "G161 X Y F3300",
    "M7; wait for bed to stabilize",
    "M6 T0; wait for extruder to stabilize",
    "M651 S255; start case fan",
    "G1 Z0.3 F3600; move down to purge",
    "G92 E0; zero extruder",
    f"G1 X-100 Y-{HALF - 8} F5000; move to purge start",
    f"G1 X100 Y-{HALF - 8} E20 F2000; purge line along the front edge",
    f"G1 X120 Y-{HALF - 8} F180; dwell to let ooze settle",
    f"G1 X140 Y-{HALF - 8} F5000; fast wipe",
    "G1 Z1 F100; lift",
    "G92 E0; zero extruder again",
    "G1 E-1.0000 F1800; initial retract",
])

END_GCODE = "\n".join([
    "M104 S0 T0; cool down extruder",
    "M140 S0 T0; cool down bed",
    "G162 Z F1800",
    "G28 X Y; home axes",
    "M132 X Y A B; recall home offsets from EPROM",
    "M652; turn off rear fan",
    "G91; relative positioning",
    "M18; disable stepper motors",
])


def machine() -> dict:
    return {
        "type": "machine",
        "name": MACHINE_NAME,
        "from": "User",
        "is_custom_defined": "1",
        "instantiation": "true",
        "inherits": "",
        "printer_technology": "FFF",
        "printer_model": "FlashForge Guider 3 Plus",
        "printer_variant": "0.4",
        "printer_settings_id": MACHINE_NAME,
        "printer_structure": "i3",

        # 0,0 is bed centre -- the reference .gx emits negative X/Y.
        "printable_area": [f"-{HALF}x-{HALF}", f"{HALF}x-{HALF}",
                           f"{HALF}x{HALF}", f"-{HALF}x{HALF}"],
        "printable_height": str(HEIGHT),
        "bed_exclude_area": ["0x0"],

        "nozzle_diameter": ["0.4"],
        "nozzle_type": "hardened_steel",
        "nozzle_volume": "0",
        "extruder_type": ["Direct Drive"],
        "single_extruder_multi_material": "0",
        "extruder_colour": ["#FCE94F"],
        "extruder_offset": ["0x0"],

        # FlashForge dialect: G161/G162/M132/M6/M7/M651/M652 are emitted from
        # the custom blocks; 'marlin' is the closest base Orca can generate.
        "gcode_flavor": "marlin",
        "machine_start_gcode": START_GCODE,
        "machine_end_gcode": END_GCODE,
        "machine_pause_gcode": "M25",
        "layer_change_gcode": "",
        "before_layer_change_gcode": "",
        "change_filament_gcode": "",
        "use_relative_e_distances": "0",

        # FlashPrint: accelerationGeneral 2000, accelerationTravel 4000.
        "machine_max_acceleration_x": ["2000", "2000"],
        "machine_max_acceleration_y": ["2000", "2000"],
        "machine_max_acceleration_z": ["500", "500"],
        "machine_max_acceleration_e": ["2000", "2000"],
        "machine_max_acceleration_extruding": ["2000", "2000"],
        "machine_max_acceleration_retracting": ["2000", "2000"],
        "machine_max_acceleration_travel": ["4000", "4000"],
        "machine_max_speed_x": ["300", "300"],
        "machine_max_speed_y": ["300", "300"],
        "machine_max_speed_z": ["20", "20"],
        "machine_max_speed_e": ["100", "100"],
        "machine_max_jerk_x": ["9", "9"],
        "machine_max_jerk_y": ["9", "9"],
        "machine_max_jerk_z": ["3", "3"],
        "machine_max_jerk_e": ["2.5", "2.5"],
        "machine_min_extruding_rate": ["0", "0"],
        "machine_min_travel_rate": ["0", "0"],

        # FlashPrint: retractLen0 0.8 mm @ 30 mm/s -- direct drive.
        "retraction_length": ["0.8"],
        "retraction_speed": ["30"],
        "deretraction_speed": ["30"],
        "retract_restart_extra": ["0"],
        "retraction_minimum_travel": ["1"],
        "retract_when_changing_layer": ["1"],
        "retract_before_wipe": ["70%"],
        "wipe": ["1"],
        "wipe_distance": ["2"],
        "z_hop": ["0.2"],                 # FlashPrint zHopHeight 0.2
        "z_hop_types": ["Normal Lift"],
        "retract_length_toolchange": ["2"],
        "retract_restart_extra_toolchange": ["0"],

        "max_layer_height": ["0.32"],     # 80% of a 0.4 nozzle
        "min_layer_height": ["0.08"],
        "silent_mode": "0",
        "scan_first_layer": "0",
        "auxiliary_fan": "1",             # the Plus has a case/side fan (M651)
        "support_chamber_temp_control": "1",
        "default_print_profile": PROCESS_NAME,
        "default_filament_profile": [FILAMENT_NAME],
    }


def process() -> dict:
    return {
        "type": "process",
        "name": PROCESS_NAME,
        "from": "User",
        "is_custom_defined": "1",
        "instantiation": "true",
        "inherits": "",
        "print_settings_id": PROCESS_NAME,
        # Must name the machine preset EXACTLY. An empty list does not
        # mean "any printer" on the CLI path -- it fails the compat check
        # just as hard as a wrong name.
        "compatible_printers": [MACHINE_NAME],
        "compatible_printers_condition": "",

        "layer_height": "0.2",
        "initial_layer_print_height": "0.25",
        "line_width": "0.42",
        "initial_layer_line_width": "0.5",
        "inner_wall_line_width": "0.45",
        "outer_wall_line_width": "0.42",
        "sparse_infill_line_width": "0.45",
        "internal_solid_infill_line_width": "0.42",
        "top_surface_line_width": "0.42",
        "support_line_width": "0.36",

        # DEPARTURE from FlashForge (shellCnt 2). On a part this small the
        # walls, not the infill, carry the load -- 4 perimeters at 0.45 mm is
        # 1.8 mm of solid shell per face.
        "wall_loops": "4",
        "top_shell_layers": "5",
        "top_shell_thickness": "1",
        "bottom_shell_layers": "4",
        "bottom_shell_thickness": "0.8",

        # DEPARTURE from FlashForge (0.15 hexagon). Gyroid is near-isotropic,
        # which matters when the load direction is not known up front.
        "sparse_infill_density": "40%",
        "sparse_infill_pattern": "gyroid",
        "infill_direction": "45",
        "minimum_sparse_infill_area": "15",
        "infill_combination": "0",
        "ensure_vertical_shell_thickness": "ensure_all",

        # FlashPrint speeds, kept as-is: they are tuned for this frame.
        "outer_wall_speed": "50",
        "inner_wall_speed": "80",
        "sparse_infill_speed": "100",
        "internal_solid_infill_speed": "80",
        "top_surface_speed": "40",
        "initial_layer_speed": "10",
        "initial_layer_infill_speed": "30",
        "travel_speed": "120",
        "bridge_speed": "25",
        "gap_infill_speed": "40",
        "overhang_1_4_speed": "40",
        "overhang_2_4_speed": "30",
        "overhang_3_4_speed": "20",
        "overhang_4_4_speed": "15",

        "default_acceleration": "2000",
        "outer_wall_acceleration": "2000",
        "inner_wall_acceleration": "2000",
        "initial_layer_acceleration": "500",
        "travel_acceleration": "4000",

        # Brim beats FlashForge's default raft here: same warp protection,
        # far less wasted filament and no raft scar on the mating face.
        "brim_type": "outer_only",
        "brim_width": "3",
        "brim_object_gap": "0.1",
        "skirt_loops": "0",
        "raft_layers": "0",

        "enable_support": "1",
        "support_type": "normal(auto)",
        "support_threshold_angle": "45",
        "support_top_z_distance": "0.2",
        "support_bottom_z_distance": "0.2",
        "support_base_pattern": "rectilinear",
        "support_base_pattern_spacing": "2.5",
        "support_interface_top_layers": "2",
        "support_interface_bottom_layers": "2",
        "support_on_build_plate_only": "0",

        "detect_thin_wall": "1",
        "detect_overhang_wall": "1",
        "reduce_crossing_wall": "1",
        "seam_position": "aligned",
        "wall_infill_order": "inner wall/outer wall/infill",
        "ironing_type": "no ironing",
        "fuzzy_skin": "none",
        "elefant_foot_compensation": "0.15",
        "xy_hole_compensation": "0",       # keep M3 holes at nominal
        "xy_contour_compensation": "0",
    }


def filament() -> dict:
    return {
        "type": "filament",
        "name": FILAMENT_NAME,
        "from": "User",
        "is_custom_defined": "1",
        "instantiation": "true",
        "inherits": "",
        "filament_id": "GFL99",
        "filament_settings_id": [FILAMENT_NAME],
        "filament_type": ["PLA"],
        "filament_vendor": ["Generic"],
        "compatible_printers": [MACHINE_NAME],
        "compatible_printers_condition": "",

        "filament_diameter": ["1.75"],
        "filament_density": ["1.24"],
        "filament_cost": ["20"],

        # DEPARTURE from FlashForge (205 C). Interlayer adhesion is the
        # failure mode for a structural PLA part, and it improves with melt
        # temperature; 320 C is the machine's ceiling so 215 is well inside it.
        "nozzle_temperature": ["215"],
        "nozzle_temperature_initial_layer": ["215"],
        "nozzle_temperature_range_low": ["190"],
        "nozzle_temperature_range_high": ["240"],
        # OrcaSlicer picks the bed temperature by PLATE TYPE, not from a
        # single field. Defining only hot_plate_temp silently emits the
        # cool-plate default instead (M140 S35 -- verified in the sliced
        # gcode), so all four are set to FlashPrint's PLA value of 45.
        "cool_plate_temp": ["45"],
        "cool_plate_temp_initial_layer": ["50"],
        "eng_plate_temp": ["45"],
        "eng_plate_temp_initial_layer": ["50"],
        "hot_plate_temp": ["45"],
        "hot_plate_temp_initial_layer": ["50"],
        "textured_plate_temp": ["45"],
        "textured_plate_temp_initial_layer": ["50"],
        "chamber_temperature": ["40"],     # FlashPrint chamberTemp for PLA

        # DEPARTURE from FlashForge (fanSpeed 100). Aggressive cooling is what
        # makes PLA layers peel; trading some overhang quality for bond
        # strength is the right call on a bracket.
        "fan_min_speed": ["40"],
        "fan_max_speed": ["70"],
        "fan_cooling_layer_time": ["20"],
        "slow_down_layer_time": ["8"],
        "slow_down_min_speed": ["10"],
        "overhang_fan_speed": ["90"],
        "overhang_fan_threshold": ["25%"],
        "close_fan_the_first_x_layers": ["2"],
        "reduce_fan_stop_start_freq": ["1"],

        "filament_flow_ratio": ["0.92"],   # FlashPrint extrusionRatio
        "filament_max_volumetric_speed": ["12"],
        "filament_retraction_length": ["nil"],
        "temperature_vitrification": ["60"],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config-dir", type=Path,
                    default=Path.home() / ".config" / "OrcaSlicer")
    ap.add_argument("--cli-dir", type=Path,
                    default=Path(__file__).resolve().parents[1]
                    / "print_files" / "orca_presets_cli")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    gui_root = args.config_dir / "user" / "default"
    parts = [("machine", MACHINE_NAME, machine()),
             ("process", PROCESS_NAME, process()),
             ("filament", FILAMENT_NAME, filament())]

    for kind, name, data in parts:
        # GUI copy. A standalone machine preset whose printer_model names an
        # UNREGISTERED model is silently dropped by the GUI, which then falls
        # back to another printer -- observed here selecting the Guider 3
        # Ultra, the Klipper machine, which is the one substitution that must
        # not happen. Deriving from an installed FlashForge model keeps the
        # preset visible; every functional value is still overridden below.
        gui_data = dict(data)
        gui_data["version"] = PRESET_VERSION
        if kind == "machine":
            gui_data["inherits"] = GUI_PARENT
            gui_data["printer_model"] = GUI_PARENT_MODEL
        gui = gui_root / kind / f"{name}.json"
        # CLI copy: OrcaSlicer 2.3.0's --load-settings REJECTS from="User"
        # with "process not compatible with printer" -- verified against the
        # shipped Guider 2s profile too, so it is the CLI path, not this
        # preset. from="system" is the only value it will slice with.
        cli_data = dict(data)
        cli_data["from"] = "system"
        cli_data.pop("is_custom_defined", None)
        cli = args.cli_dir / kind / f"{name}.json"

        for path, payload in ((gui, gui_data), (cli, cli_data)):
            if args.dry_run:
                print(f"[dry-run] would write {path}")
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(payload, indent=4, ensure_ascii=False) + "\n")
            print(f"wrote {path}  ({len(payload)} keys)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
