#!/usr/bin/env python3
"""Shaded hero renders of CAD parts — no GPU, no GL, no viewer.

    edu/.cadenv/bin/python edu/tools/hero_render.py part.step -o out.png \
        --highlight "y:23.5:37.5"

render_step.py proves a part imported. This proves what it LOOKS like, and
paints the newly-added material a different colour so an edit is legible at a
glance instead of having to diff two bounding boxes.

Pipeline: OCCT tessellation -> orthographic projection -> painter's algorithm
with backface culling -> per-face Lambert + fill + rim + Blinn-Phong specular
-> crease/silhouette edges -> supersampled downsample. Pure numpy + PIL, so it
works headless and over SSH like everything else in this folder.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

BG = (0x14, 0x11, 0x0E)
INK = (0x33, 0x2B, 0x22)          # crease lines
BASE = np.array([0.815, 0.785, 0.730])   # carried-over vendor geometry
NEW = np.array([0.925, 0.575, 0.245])    # material this variant adds

# light rig, in CAMERA space -> every view is lit the same way
KEY = np.array([-0.35, 0.46, 0.82]);  KEY /= np.linalg.norm(KEY)
FILL = np.array([0.62, -0.38, 0.50]); FILL /= np.linalg.norm(FILL)
VIEW = np.array([0.0, 0.0, 1.0])          # orthographic eye direction
AMBIENT, K_KEY, K_FILL, K_RIM, K_SPEC, SHINE = 0.30, 0.66, 0.28, 0.18, 0.26, 26.0
K_HEMI = 0.26                              # sky/ground wrap — keeps shadow sides readable

VIEWS = [("iso", 24, -58), ("iso rear", 16, 128), ("front", 2, -90), ("side", 2, 0)]

# vendor part names are Chinese; DejaVu has no CJK, so labels need Noto or they
# come out as tofu boxes
FONTS = ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
         "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]


def font(size):
    from PIL import ImageFont
    for p in FONTS:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


# ------------------------------------------------------------------ geometry

def tessellate(path, tol=0.02):
    """STEP is exact B-rep; the rasteriser needs triangles."""
    from build123d import export_stl, import_step
    import trimesh
    shape = import_step(path)
    tmp = "/tmp/_hero_render.stl"
    export_stl(shape, tmp, tolerance=tol)
    return shape, trimesh.load(tmp, force="mesh")


def upright(mesh, up):
    """Rotate so the part's own up-axis is world +Z (the camera's up).

    Vendor brackets are axis-agnostic, but the crest is authored Y-up and the
    boot's sole is -Y: rendered against a Z-up camera they come out lying on
    their side, which reads as a modelling error when it is a framing one.
    """
    if not up or up.lower() == "z":
        return mesh
    R = {"y": np.array([[1., 0., 0.], [0., 0., -1.], [0., 1., 0.]]),
         "x": np.array([[0., 0., -1.], [0., 1., 0.], [1., 0., 0.]])}[up.lower()]
    m = mesh.copy()
    m.vertices = mesh.vertices @ R.T
    return m


def camera(elev_deg, azim_deg):
    """matplotlib mplot3d's elev/azim convention, so views match render_step."""
    e, a = np.radians(elev_deg), np.radians(azim_deg)
    eye = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    fwd = -eye / np.linalg.norm(eye)            # eye -> subject
    up_w = np.array([0.0, 0.0, 1.0])
    if abs(fwd @ up_w) > 0.999:
        up_w = np.array([0.0, 1.0, 0.0])
    right = np.cross(fwd, up_w); right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    return np.stack([right, up, fwd])           # rows: x_cam, y_cam, depth


def shade(n_cam, albedo):
    """Lambert key + fill + hemisphere wrap + rim + Blinn-Phong, per face.

    The hemisphere term is what keeps a shadow-side face legible instead of
    crushed to black — on a matte print that is where most of the geometry is.
    """
    lam = np.clip(n_cam @ KEY, 0, 1) * K_KEY + np.clip(n_cam @ FILL, 0, 1) * K_FILL
    hemi = (0.5 + 0.5 * n_cam[:, 1]) * K_HEMI
    rim = (1.0 - np.abs(n_cam @ VIEW)) ** 3 * K_RIM
    h = KEY + VIEW; h /= np.linalg.norm(h)
    spec = np.clip(n_cam @ h, 0, 1) ** SHINE * K_SPEC
    lit = albedo * (AMBIENT + lam + hemi + rim)[:, None] + spec[:, None]
    return np.clip(lit, 0, 1)


def crease_keys(mesh, angle_deg=26.0):
    """Edges where the surface actually turns — the lines worth drawing."""
    adj, ang = mesh.face_adjacency, mesh.face_adjacency_angles
    edges = mesh.face_adjacency_edges[ang > np.radians(angle_deg)]
    return {(min(a, b), max(a, b)) for a, b in edges}, adj, mesh.face_adjacency_edges


def highlight_mask(mesh, spec):
    """--highlight 'axis:lo:hi[,axis:lo:hi]' -> per-face new-material mask.

    Multiple clauses AND together (a face must satisfy all), so a band can be
    intersected with a surface shell. Prefix an axis with '~' to invert.
    """
    cen = mesh.triangles.mean(axis=1)
    if not spec or spec == "all":
        return np.ones(len(mesh.faces), bool) if spec == "all" else np.zeros(len(mesh.faces), bool)
    mask = np.ones(len(mesh.faces), bool)
    for clause in spec.split(","):
        parts = clause.split(":")
        ax, lo, hi = parts[0], float(parts[1]), float(parts[2])
        inv = ax.startswith("~")
        i = "xyz".index(ax.lstrip("~").lower())
        band = (cen[:, i] >= lo - 1e-6) & (cen[:, i] <= hi + 1e-6)
        mask &= ~band if inv else band
    return mask


def highlight_or(mesh, specs):
    """OR together several --highlight expressions (e.g. two opposite webs)."""
    out = np.zeros(len(mesh.faces), bool)
    for s in specs:
        out |= highlight_mask(mesh, s)
    return out


# ------------------------------------------------------------------ raster

def render_view(mesh, new_mask, elev, azim, tw, th, ss, mm2px, center, creases,
                edges_lut, edge_w, anchor=None):
    M = camera(elev, azim)
    V = (mesh.vertices - center) @ M.T                  # (V,3) camera space
    # centre each view on its own projected bbox; scale stays shared so the
    # tiles remain directly comparable
    V[:, 0] -= (V[:, 0].min() + V[:, 0].max()) / 2
    if anchor == "bottom":
        # sit both members of a pair on a common floor, so extra height reads
        # as growth upward instead of as a centred rescale
        V[:, 1] -= V[:, 1].min() + (th / mm2px) / 2 - 4.0
    else:
        V[:, 1] -= (V[:, 1].min() + V[:, 1].max()) / 2
    N = mesh.face_normals @ M.T                          # (F,3)
    front = N[:, 2] < 0                                  # outward normal toward eye
    tri = mesh.faces[front]
    if len(tri) == 0:
        return Image.new("RGB", (tw, th), BG)
    Nf = N[front]
    Nf = Nf * -np.sign(Nf[:, 2:3])                       # face the camera

    col = np.where(new_mask[front][:, None], NEW, BASE)
    rgb = (shade(Nf, col) * 255).astype(np.uint8)

    W, H = tw * ss, th * ss
    s = mm2px * ss
    sx = V[:, 0] * s + W / 2.0
    sy = H / 2.0 - V[:, 1] * s                           # image y grows down

    depth = V[tri, 2].mean(axis=1)
    order = np.argsort(-depth)                           # far -> near

    img = Image.new("RGB", (W, H), BG)
    dr = ImageDraw.Draw(img)
    lw = max(1, int(round(edge_w * ss)))

    # silhouette = crease set + edges whose two faces disagree about facing
    sil = set()
    if edges_lut is not None:
        adj, adj_edges = edges_lut
        flip = front[adj[:, 0]] != front[adj[:, 1]]
        for a, b in adj_edges[flip]:
            sil.add((min(a, b), max(a, b)))
    draw_set = creases | sil

    fidx = np.nonzero(front)[0]
    for k in order:
        f = tri[k]
        pts = [(sx[f[0]], sy[f[0]]), (sx[f[1]], sy[f[1]]), (sx[f[2]], sy[f[2]])]
        c = tuple(int(v) for v in rgb[k])
        dr.polygon(pts, fill=c)
        if draw_set:
            for u, v in ((0, 1), (1, 2), (2, 0)):
                key = (min(f[u], f[v]), max(f[u], f[v]))
                if key in draw_set:
                    dr.line([pts[u], pts[v]], fill=INK, width=lw)
    _ = fidx
    return img.resize((tw, th), Image.LANCZOS)


class Part:
    """A tessellated, masked, upright part — ready to shoot from any angle.

    Split out from render() so two parts can be drawn at ONE shared scale.
    Auto-fitting each part to its own tile is what makes a stock/tall pair look
    identical in size, which is the exact thing the pair exists to show.
    """

    def __init__(self, path, highlights=(), up="z", tol=0.02):
        self.shape, mesh = tessellate(path, tol)
        self.n_tri = len(mesh.faces)
        if highlights and highlights != ["all"]:
            edge = max(0.8, float(np.abs(mesh.bounds[1] - mesh.bounds[0]).max()) / 60.0)
            mesh = mesh.subdivide_to_size(max_edge=edge)
        self.mask = (highlight_or(mesh, highlights) if highlights
                     else np.zeros(len(mesh.faces), bool))
        self.size = np.abs(mesh.bounds[1] - mesh.bounds[0])
        self.mesh = upright(mesh, up)
        self.creases, self.adj, self.adj_edges = crease_keys(self.mesh)
        self.center = self.mesh.bounds.mean(axis=0)

    def extents(self, views):
        """Projected width/height in mm over the given views."""
        ex = ey = 0.0
        for _, e, a in views:
            P = (self.mesh.vertices - self.center) @ camera(e, a).T
            ex, ey = max(ex, np.ptp(P[:, 0])), max(ey, np.ptp(P[:, 1]))
        return ex, ey

    def shot(self, elev, azim, tw, th, ss, mm2px, edge_w=0.9, anchor=None):
        return render_view(self.mesh, self.mask, elev, azim, tw, th, ss, mm2px,
                           self.center, self.creases,
                           (self.adj, self.adj_edges), edge_w, anchor)


def render(path, out, highlights=(), px=760, ss=3, tol=0.02, tag=None,
           views=None, edge_w=0.9, up="z"):
    shape, mesh = tessellate(path, tol)
    n_tri = len(mesh.faces)                      # the STL's real triangle count
    if highlights and highlights != ["all"]:
        # OCCT's clean() merges added material back into the coplanar vendor
        # faces it touches, so after a stretch the new span is no longer its own
        # face — a whole 73 mm strap can be two triangles. Subdivide for the
        # render only, so a centroid band can resolve the boundary.
        edge = max(0.8, float(np.abs(mesh.bounds[1] - mesh.bounds[0]).max()) / 60.0)
        mesh = mesh.subdivide_to_size(max_edge=edge)
    # mask in the part's authoring frame (that is where the bands are defined),
    # then reorient — face order survives a vertex transform
    new_mask = highlight_or(mesh, highlights) if highlights else np.zeros(len(mesh.faces), bool)
    size = np.abs(mesh.bounds[1] - mesh.bounds[0])   # authoring frame, for the caption
    mesh = upright(mesh, up)
    creases, adj, adj_edges = crease_keys(mesh)
    bb = mesh.bounds
    center = bb.mean(axis=0)
    views = views or VIEWS
    # one shared scale, but tile aspect follows the part: a flat bracket should
    # not be framed in a square of empty background
    ext_x = ext_y = 0.0
    for _, e, a in views:
        P = (mesh.vertices - center) @ camera(e, a).T
        ext_x, ext_y = max(ext_x, np.ptp(P[:, 0])), max(ext_y, np.ptp(P[:, 1]))
    ext_x, ext_y = ext_x * 1.10, ext_y * 1.14
    mm2px = px / ext_x
    tw, th = px, max(110, int(round(ext_y * mm2px)))
    tiles = [render_view(mesh, new_mask, e, a, tw, th, ss, mm2px, center,
                         creases, (adj, adj_edges), edge_w, None)
             for _, e, a in views]

    pad, cap = 12, 58
    W = pad + len(tiles) * (tw + pad)
    sheet = Image.new("RGB", (W, th + pad * 2 + cap), BG)
    d = ImageDraw.Draw(sheet)
    fnt, fsm = font(19), font(15)
    for i, t in enumerate(tiles):
        x = pad + i * (tw + pad)
        sheet.paste(t, (x, pad))
        d.text((x + tw // 2, pad + 4), views[i][0], fill="#E0913F", font=fsm, anchor="ma")

    label = tag or os.path.splitext(os.path.basename(path))[0]
    ty = th + pad * 2
    d.text((pad + 6, ty - 2), label, fill="#f0ebe2", font=fnt)
    d.text((pad + 6, ty + 24),
           f"{size[0]:.1f} x {size[1]:.1f} x {size[2]:.1f} mm    "
           f"{shape.volume/1000:.2f} cm3    {n_tri} tri",
           fill="#a49c8e", font=fsm)
    if highlights:
        d.rectangle([W - 250, ty + 6, W - 234, ty + 22],
                    fill=tuple((NEW * 255).astype(int)))
        d.text((W - 226, ty + 5), "material added", fill="#a49c8e", font=fsm)
    sheet.save(out)
    print(f"  {label:28s} -> {out}  ({size[0]:.1f} x {size[1]:.1f} x {size[2]:.1f} mm, "
          f"{int(new_mask.sum())}/{len(mesh.faces)} tri highlighted)")
    return out


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("path")
    p.add_argument("-o", "--out", default=None)
    p.add_argument("--highlight", action="append", default=[],
                   help="axis:lo:hi[,axis:lo:hi] — repeatable (OR); 'all'")
    p.add_argument("--px", type=int, default=760)
    p.add_argument("--ss", type=int, default=3)
    p.add_argument("--tol", type=float, default=0.02)
    p.add_argument("--tag", default=None)
    p.add_argument("--up", default="z", choices=["x", "y", "z"],
                   help="which part axis points up in the render")
    a = p.parse_args()
    out = a.out or os.path.splitext(os.path.basename(a.path))[0] + "_hero.png"
    render(a.path, out, a.highlight, a.px, a.ss, a.tol, a.tag, up=a.up)
    sys.exit(0)
