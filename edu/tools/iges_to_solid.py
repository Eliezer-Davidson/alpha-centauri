#!/usr/bin/env python3
"""Convert HiWonder's IGES bracket SURFACES into watertight, correctly-oriented
STEP SOLIDS.

    edu/.cadenv/bin/python edu/tools/iges_to_solid.py \
        "$HIWONDER_CAD_DIR"/bracket/*/IGS/*.IGS -o "$HIWONDER_CAD_DIR"/solids

The IGS/DXF inputs are HiWonder's and are NOT redistributed in this public
copy -- see THIRD_PARTY_NOTICES.md. Point HIWONDER_CAD_DIR at your own copy.

WHY. HiWonder ships the aluminium frame parts as IGES, and IGES carries no
solids — measured: 0 solids, 0 shells, just 27-106 loose faces per file. The
CAD research called this "chain break #1" and assumed manual sewing in a GUI.
It is not manual: all 8 sew into CLOSED shells at 1e-3 tolerance, so the whole
conversion is scriptable.

THE TRAP THIS EXISTS TO CATCH. Two of the eight (一字支架, 斜U支架) sew into
closed shells with NEGATIVE volume — their face normals point inward, so the
"solid" is inside-out. OCCT will hand you that shape without complaint. Every
downstream boolean then does the opposite of what you meant: a cut adds
material, a fuse removes it. Nothing errors; the geometry is just quietly wrong.

So this tool measures the volume and reverses any solid that comes out negative,
then asserts the result is positive. A converter that did not check would look
identical on 6 of 8 parts and be silently broken on the other 2.
"""
import argparse
import os
import sys

from OCP.BRep import BRep_Tool
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeSolid, BRepBuilderAPI_Sewing
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.IFSelect import IFSelect_RetDone
from OCP.IGESControl import IGESControl_Reader
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
from OCP.TopAbs import TopAbs_SHELL
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS


def volume_cm3(shape):
    p = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, p)
    return p.Mass() / 1000.0


def convert(path, tol=1e-3):
    """IGES surfaces -> one watertight, positively-oriented solid."""
    reader = IGESControl_Reader()
    if reader.ReadFile(path) != IFSelect_RetDone:
        raise OSError(f"IGES read failed: {path}")
    reader.TransferRoots()

    sew = BRepBuilderAPI_Sewing(tol)
    sew.Add(reader.OneShape())
    sew.Perform()

    exp = TopExp_Explorer(sew.SewedShape(), TopAbs_SHELL)
    if not exp.More():
        raise ValueError(f"{os.path.basename(path)}: sewing produced no shell")
    shell = TopoDS.Shell_s(exp.Current())
    if not BRep_Tool.IsClosed_s(shell):
        raise ValueError(f"{os.path.basename(path)}: shell is NOT closed — "
                         f"cannot make a solid; raise --tol and retry")

    solid = BRepBuilderAPI_MakeSolid(shell).Solid()
    vol = volume_cm3(solid)
    flipped = vol < 0
    if flipped:
        solid.Reverse()                      # inward normals: turn it right-side out
        vol = volume_cm3(solid)
    if vol <= 0:
        raise ValueError(f"{os.path.basename(path)}: volume still {vol:.2f} cm3 "
                         f"after reversing — geometry is not a valid solid")
    return solid, vol, flipped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--tol", type=float, default=1e-3)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    ok = fixed = 0
    for path in sorted(args.paths):
        name = os.path.splitext(os.path.basename(path))[0]
        try:
            solid, vol, flipped = convert(path, args.tol)
        except Exception as exc:
            print(f"  FAIL  {name:16s} {exc}")
            continue
        dest = os.path.join(args.out, f"{name}.step")
        writer = STEPControl_Writer()
        writer.Transfer(solid, STEPControl_AsIs)
        writer.Write(dest)
        ok += 1
        fixed += flipped
        print(f"  ok    {name:16s} {vol:7.2f} cm3"
              f"{'   [REVERSED — normals were inward]' if flipped else ''}")

    print(f"\n  {ok}/{len(args.paths)} solids written to {args.out}"
          f"   ({fixed} needed reversing)")
    return 0 if ok == len(args.paths) else 1


if __name__ == "__main__":
    sys.exit(main())
