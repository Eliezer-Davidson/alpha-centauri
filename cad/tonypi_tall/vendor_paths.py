#!/usr/bin/env python3
"""Where HiWonder's own CAD lives — configured, never assumed.

HiWonder's TonyPi frame STEPs and the LX-824HV servo solid are vendor
property. This public copy of the repository does not redistribute them
(see THIRD_PARTY_NOTICES.md for what was removed and where to get it), so
every module that reads them asks here instead of hard-coding a path.

Set either variable to the directory holding your own download:

    export TONYPI_STOCK_STEP_DIR=/path/to/tonypi/step   # the 8 frame parts
    export HIWONDER_CAD_DIR=/path/to/hiwonder-cad       # LX-824HV.STEP etc.

Both default to the in-repo locations they used to live at, so a private
working copy that still has the vendor files keeps running unchanged.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

_NOTICE = (
    "\n  Set {var} to a directory containing your own copy.\n"
    "  See THIRD_PARTY_NOTICES.md -- this public repository deliberately does\n"
    "  not redistribute HiWonder's CAD."
)


def _resolve(var, default_rel, what, required):
    path = os.environ.get(var) or os.path.join(REPO, default_rel)
    if required and not os.path.exists(path):
        raise SystemExit(
            f"{what} not found at: {path}" + _NOTICE.format(var=var))
    return path


def stock_step_dir(required=True):
    """Directory of HiWonder's eight original frame STEP files."""
    return _resolve("TONYPI_STOCK_STEP_DIR", "edu/print_files/step",
                    "HiWonder stock frame STEPs", required)


def stock_stl_dir(required=True):
    """Directory of HiWonder's eight original frame STL files."""
    return _resolve("TONYPI_STOCK_STL_DIR", "edu/print_files/stl",
                    "HiWonder stock frame STLs", required)


def vendor_cad_dir(required=True):
    """Directory of HiWonder's servo/bracket CAD (LX-824HV.STEP, ...)."""
    return _resolve("HIWONDER_CAD_DIR", "edu/vendor-cad",
                    "HiWonder vendor CAD", required)


def servo_step(required=True):
    """The LX-824HV servo solid."""
    path = os.path.join(vendor_cad_dir(required=False), "LX-824HV.STEP")
    if required and not os.path.exists(path):
        raise SystemExit(
            f"LX-824HV.STEP not found at: {path}"
            + _NOTICE.format(var="HIWONDER_CAD_DIR"))
    return path
