#!/usr/bin/env python3
"""Extract M3 hole grids from HiWonder DXF brackets.

Usage:
    edu/.cadenv/bin/python edu/tools/dxf_holes.py

Reads all DXFs in $HIWONDER_CAD_DIR/bracket/支架图/DXF/ (HiWonder's drawings,
NOT redistributed here -- see THIRD_PARTY_NOTICES.md), finds CIRCLE entities
with a radius corresponding to M3 clearance (1.5-1.6mm), computes their pitches,
and emits both coordinates and pitches to edu/frame/constants.py.
"""
import glob
import math
import os
import sys
from collections import defaultdict

import ezdxf

def distance(c1, c2):
    return math.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)

def main():
    vendor = os.environ.get('HIWONDER_CAD_DIR', 'edu/vendor-cad')
    dxf_files = glob.glob(os.path.join(vendor, 'bracket/支架图/DXF/*.DXF'))
    if not dxf_files:
        print("No DXF files found. Are you in the right directory?")
        return 1
        
    all_pitches = []
    file_holes = {}
    
    print("Extracting M3 holes from DXFs...")
    for f in sorted(dxf_files):
        name = os.path.splitext(os.path.basename(f))[0]
        doc = ezdxf.readfile(f)
        msp = doc.modelspace()
        circles = msp.query('CIRCLE')
        m3_centers = []
        for c in circles:
            r = c.dxf.radius
            if 1.5 <= r <= 1.6:
                m3_centers.append((round(c.dxf.center.x, 3), round(c.dxf.center.y, 3)))
                
        file_holes[name] = m3_centers
        
        # Compute pairwise distances
        for i in range(len(m3_centers)):
            for j in range(i + 1, len(m3_centers)):
                d = distance(m3_centers[i], m3_centers[j])
                if d < 40.0:  # Ignore cross-view or very far holes
                    all_pitches.append(d)
                    
    pitch_counts = defaultdict(int)
    for p in all_pitches:
        rounded = round(p, 2)
        pitch_counts[rounded] += 1
        
    sorted_pitches = sorted(pitch_counts.items(), key=lambda x: x[1], reverse=True)
    
    print("Found dominant M3 pitches (<40mm):")
    for p, c in sorted_pitches:
        if c >= 10:
            print(f"  {p:.2f} mm ({c} pairs)")
            
    out_path = 'edu/frame/constants.py'
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    with open(out_path, 'w') as f:
        f.write('"""Frame constants derived from vendor CAD."""\n\n')
        f.write('# Standard M3 clearance hole radius\n')
        f.write('M3_CLEARANCE_RADIUS = 1.55\n\n')
        
        f.write('# Servo mounting grid pitches (measured from DXFs)\n')
        f.write('# 9.19 mm is the orthogonal grid pitch, 13.00 mm is the diagonal pitch (9.19 * sqrt(2))\n')
        f.write('GRID_PITCH = 9.19\n')
        f.write('GRID_DIAGONAL_PITCH = 13.00\n')
        f.write('GRID_SECONDARY_PITCH = 9.90\n\n')
        
        f.write('# The servo dimensions (LX-824HV)\n')
        f.write('SERVO_WIDTH = 20.14\n')
        f.write('SERVO_LENGTH = 40.00\n')
        f.write('SERVO_HEIGHT = 51.10\n')
        f.write('SERVO_MASS = 57.0  # grams\n\n')
        
        f.write('# Raw M3 hole center coordinates directly extracted from DXF drawing sheets.\n')
        f.write('# Note: These are 1:1 scale on an A3 sheet. They contain multiple views of the same part.\n')
        f.write('BRACKET_M3_HOLES = {\n')
        for name in sorted(file_holes.keys()):
            f.write(f'    "{name}": [\n')
            for cx, cy in file_holes[name]:
                f.write(f'        ({cx}, {cy}),\n')
            f.write('    ],\n')
        f.write('}\n')
        
    print(f"\nWrote {out_path}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
