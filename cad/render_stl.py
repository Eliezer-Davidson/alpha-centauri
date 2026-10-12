"""Headless STL renderer (numpy + PIL only -- no matplotlib in these venvs).

Flat-shaded painter's-algorithm isometric renders, composed into one labeled
montage PNG. Usage:

    python render_stl.py out.png "Label A" a.stl "Label B" b.stl ...
"""

import struct
import sys

import numpy as np
from PIL import Image, ImageDraw


def load_stl(path):
    """Return (n, 3, 3) float array of triangles from a binary or ASCII STL."""
    with open(path, "rb") as f:
        data = f.read()
    if data[:5] == b"solid" and b"facet" in data[:300]:
        tris = []
        cur = []
        for line in data.decode(errors="ignore").splitlines():
            parts = line.split()
            if parts[:1] == ["vertex"]:
                cur.append([float(v) for v in parts[1:4]])
                if len(cur) == 3:
                    tris.append(cur)
                    cur = []
        return np.array(tris)
    n = struct.unpack("<I", data[80:84])[0]
    body = np.frombuffer(data[84 : 84 + n * 50], dtype=np.uint8).reshape(n, 50)
    floats = body[:, :48].copy().view("<f4").reshape(n, 12)
    return floats[:, 3:12].reshape(n, 3, 3).astype(np.float64)


def render(tris, size=560, elev_deg=28.0, azim_deg=-50.0, bg=(250, 250, 252)):
    az, el = np.radians(azim_deg), np.radians(elev_deg)
    rz = np.array(
        [[np.cos(az), -np.sin(az), 0], [np.sin(az), np.cos(az), 0], [0, 0, 1]]
    )
    rx = np.array(
        [[1, 0, 0], [0, np.cos(el), -np.sin(el)], [0, np.sin(el), np.cos(el)]]
    )
    pts = tris.reshape(-1, 3) @ rz.T @ rx.T
    v = pts.reshape(-1, 3, 3)

    lo, hi = pts.min(axis=0), pts.max(axis=0)
    span = max(hi[0] - lo[0], hi[2] - lo[2]) or 1.0
    margin = 0.12 * size
    scale = (size - 2 * margin) / span
    cx, cz = (lo[0] + hi[0]) / 2, (lo[2] + hi[2]) / 2

    def to_px(p):
        return (
            size / 2 + (p[0] - cx) * scale,
            size / 2 - (p[2] - cz) * scale,
        )

    # painter's sort: farthest (smallest y) first
    order = np.argsort(v[:, :, 1].mean(axis=1))
    normals = np.cross(v[:, 1] - v[:, 0], v[:, 2] - v[:, 0])
    norms = np.linalg.norm(normals, axis=1)
    norms[norms == 0] = 1
    normals = normals / norms[:, None]
    light = np.array([0.3, -0.8, 0.52])
    light = light / np.linalg.norm(light)
    lam = np.abs(normals @ light)

    img = Image.new("RGB", (size, size), bg)
    dr = ImageDraw.Draw(img)
    base = np.array([70, 110, 170])
    for i in order:
        c = tuple((base * (0.35 + 0.65 * lam[i])).astype(int))
        dr.polygon([to_px(p) for p in v[i]], fill=c)
    return img


def main():
    out = sys.argv[1]
    pairs = list(zip(sys.argv[2::2], sys.argv[3::2]))
    tiles = []
    for label, path in pairs:
        img = render(load_stl(path))
        dr = ImageDraw.Draw(img)
        dr.rectangle([0, img.height - 26, img.width, img.height], fill=(30, 30, 34))
        dr.text((10, img.height - 21), label, fill=(240, 240, 245))
        tiles.append(img)
    w = sum(t.width for t in tiles)
    h = max(t.height for t in tiles)
    sheet = Image.new("RGB", (w, h), (250, 250, 252))
    x = 0
    for t in tiles:
        sheet.paste(t, (x, 0))
        x += t.width
    sheet.save(out)
    print(f"wrote {out} ({w}x{h}, {len(tiles)} tiles)")


if __name__ == "__main__":
    main()
