#!/usr/bin/env python3
"""Convert STEP solids into 3D printable STL files with high resolution.

Usage:
    edu/.cadenv/bin/python edu/tools/generate_print_files.py
"""
import os
import glob
import shutil
from build123d import import_step, export_stl

def main():
    # Vendor solids are not redistributed in this public copy; point
    # HIWONDER_CAD_DIR at your own download. See THIRD_PARTY_NOTICES.md.
    solids_dir = os.path.join(
        os.environ.get("HIWONDER_CAD_DIR", "edu/vendor-cad"), "solids")
    out_dir = "edu/print_files"
    stl_dir = os.path.join(out_dir, "stl")
    step_dir = os.path.join(out_dir, "step")
    
    os.makedirs(stl_dir, exist_ok=True)
    os.makedirs(step_dir, exist_ok=True)
    
    step_files = glob.glob(os.path.join(solids_dir, "*.step"))
    if not step_files:
        print(f"No STEP files found in {solids_dir}!")
        return 1
        
    print("Preparing 3D printable files...")
    for step_path in sorted(step_files):
        base_name = os.path.basename(step_path)
        part_name = os.path.splitext(base_name)[0]
        
        # 1. Copy the high-quality STEP solid directly
        dest_step = os.path.join(step_dir, base_name)
        shutil.copy2(step_path, dest_step)
        print(f"  [STEP] Copied {base_name} to step/")
        
        # 2. Tessellate and export as STL for slicers that don't support STEP
        dest_stl = os.path.join(stl_dir, f"{part_name}.stl")
        try:
            shape = import_step(step_path)
            # Use a tight tolerance (0.01mm) for round M3 holes and smooth fillets
            export_stl(shape, dest_stl, tolerance=0.01)
            print(f"  [STL ] Exported {part_name}.stl with high tolerance")
        except Exception as e:
            print(f"  [FAIL] Failed to convert {base_name} to STL: {e}")
            
    print(f"\nAll parts organized under: {out_dir}")
    print("  - step/ (Contains raw STEP files; recommended for modern slicers)")
    print("  - stl/  (Contains high-resolution STL meshes)")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
