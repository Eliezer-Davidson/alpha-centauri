"""Shared B-rep operations for the TonyPi TALL variant.

Every part edit in this folder goes through these four operations so the
whole variant stays parametric: change a delta in tall_constants.py and
re-run the part script.

Run with: edu/.cadenv/bin/python (build123d 0.11.1 + trimesh).
"""
from build123d import (
    Axis, Box, Pos,
    export_step, export_stl, extrude,
)

BIG = 500.0  # larger than any part dimension, for half-space booleans


# ---------------------------------------------------------------- probing

def section_profile(part, axis: Axis, n=120):
    """Cross-section area at n stations along axis. Returns [(coord, area)].

    A station is a safe stretch site when its neighbourhood has constant
    area (prismatic, no holes, no fillet transitions).
    """
    bb = part.bounding_box()
    lo, hi = {
        Axis.X: (bb.min.X, bb.max.X),
        Axis.Y: (bb.min.Y, bb.max.Y),
        Axis.Z: (bb.min.Z, bb.max.Z),
    }[axis]
    out = []
    for i in range(1, n):
        c = lo + (hi - lo) * i / n
        faces = _section_faces(part, axis, c)
        out.append((round(c, 3), round(sum(f.area for f in faces), 3)))
    return out


def find_stretch_station(part, axis: Axis, lo_frac=0.15, hi_frac=0.85,
                         band_mm=4.0, tol=0.5):
    """Find the coordinate of the widest constant-area band along axis.

    Scans the profile between lo_frac..hi_frac of the length and returns the
    centre of the longest run whose area varies < tol mm^2. Raises if no run
    at least band_mm wide exists (part has no prismatic zone -> needs a
    hand-picked station).
    """
    prof = section_profile(part, axis)
    m = len(prof)
    prof = prof[int(m * lo_frac):int(m * hi_frac)]
    runs, start = [], 0
    for i in range(1, len(prof) + 1):
        if i == len(prof) or abs(prof[i][1] - prof[start][1]) > tol:
            runs.append((prof[start][0], prof[i - 1][0], prof[start][1]))
            start = i
    best = max(runs, key=lambda r: r[1] - r[0])
    if best[1] - best[0] < band_mm:
        raise ValueError(
            f"no prismatic band >= {band_mm} mm (best {best[1]-best[0]:.1f} mm); "
            f"profile runs: {runs}")
    return (best[0] + best[1]) / 2


def _section_faces(part, axis: Axis, coord):
    """Planar faces of the cut cross-section at coord along axis."""
    half = _half_space(axis, coord, below=True)
    lower = part & half
    return [f for f in lower.faces()
            if abs(_face_coord(f, axis) - coord) < 1e-3
            and abs(abs(f.normal_at(None).dot(axis.direction)) - 1) < 1e-3]


def _axis_name(axis: Axis):
    return {(1, 0, 0): 0, (0, 1, 0): 1, (0, 0, 1): 2}[
        tuple(round(v) for v in axis.direction.to_tuple())]


def _face_coord(face, axis: Axis):
    c = face.center()
    return [c.X, c.Y, c.Z][_axis_name(axis)]


def _half_space(axis: Axis, coord, below: bool):
    i = _axis_name(axis)
    size = [BIG * 2] * 3
    center = [0.0, 0.0, 0.0]
    center[i] = coord - BIG if below else coord + BIG
    return Pos(*center) * Box(*size)


# ---------------------------------------------------------------- stretch

def stretch(part, axis: Axis, delta: float, station: float = None):
    """Lengthen part by delta along axis at a prismatic station.

    Cuts at the station, translates the upper half by +delta, and bridges
    with an extrusion of the cut faces. Volume grows by exactly
    section_area * delta; everything on both sides (holes, bosses, the web)
    is preserved untouched.
    """
    if station is None:
        station = find_stretch_station(part, axis)
    i = _axis_name(axis)
    lower = part & _half_space(axis, station, below=True)
    upper = part & _half_space(axis, station, below=False)
    faces = [f for f in lower.faces()
             if abs(_face_coord(f, axis) - station) < 1e-3
             and abs(abs(f.normal_at(None).dot(axis.direction)) - 1) < 1e-3]
    if not faces:
        raise ValueError(f"no cut faces found at station {station}")
    vec = [0.0, 0.0, 0.0]
    vec[i] = delta
    bridges = [extrude(f, amount=delta, dir=axis.direction) for f in faces]
    out = lower
    for b in bridges:
        out = out + b
    out = out + upper.translate(vec)
    return out.clean(), station, sum(f.area for f in faces)


# ---------------------------------------------------------------- closure

def close_span(part, axis: Axis, span_lo: float, span_hi: float,
               close_axis: Axis, wall: float = 2.5, both: bool = True,
               inset: float = 0.0):
    """Add closing web plates over [span_lo, span_hi] along axis.

    Bridges the open side(s) of a U section: plates at the close_axis
    extremes of the part bbox, spanning the full third axis. `inset` pulls
    the plates inward from the bbox extreme (0 = flush with outer surface).
    Used on the stretch bridge zone to turn the open U into a closed box —
    torsional stiffness is the printed frame's scarcest resource.
    """
    bb = part.bounding_box()
    i = _axis_name(axis)          # span axis
    k = _axis_name(close_axis)    # closing axis
    j = 3 - i - k                 # remaining axis
    mins = [bb.min.X, bb.min.Y, bb.min.Z]
    maxs = [bb.max.X, bb.max.Y, bb.max.Z]

    def plate(at_max: bool):
        size = [0.0, 0.0, 0.0]
        size[i] = span_hi - span_lo
        size[j] = maxs[j] - mins[j]
        size[k] = wall
        center = [0.0, 0.0, 0.0]
        center[i] = (span_lo + span_hi) / 2
        center[j] = (mins[j] + maxs[j]) / 2
        center[k] = (maxs[k] - inset - wall / 2) if at_max else (mins[k] + inset + wall / 2)
        return Pos(*center) * Box(*size)

    out = part + plate(True)
    if both:
        out = out + plate(False)
    return out.clean()


# ---------------------------------------------------------------- report

def report(part, path_step: str, path_stl: str, label: str):
    """Export STEP + STL and return a measurement dict for verification."""
    export_step(part, path_step)
    export_stl(part, path_stl, tolerance=0.01)
    bb = part.bounding_box()
    return {
        "label": label,
        "bbox_mm": [round(bb.size.X, 3), round(bb.size.Y, 3), round(bb.size.Z, 3)],
        "volume_cm3": round(part.volume / 1000, 3),
        "n_solids": len(part.solids()),
        "n_faces": len(part.faces()),
        "step": path_step,
        "stl": path_stl,
    }
