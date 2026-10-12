#!/usr/bin/env python3
"""Why the UNCHANGED vendor parts are in the print test.

    edu/.cadenv/bin/python cad/tonypi_tall/test_matrix.py

Two independent things changed between the robot on the bench and the robot on
the screen: the MATERIAL (aluminium -> printed polymer) and the GEOMETRY (the
TALL edits). Print only the modified parts and a failure cannot be attributed
to either one. The pass-throughs are the missing cell.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
from matplotlib.patches import Rectangle, FancyArrowPatch  # noqa: E402

SURFACE, T1, T2 = "#1a1a19", "#ffffff", "#c3c2b7"
BLUE, ORANGE, AQUA, MUTED = "#3987e5", "#d95926", "#199e70", "#4a4642"

# English names on purpose: matplotlib has no CJK face here, and the vendor
# names add nothing to the argument the diagram is making
CELLS = [
    # col, row, colour, title, body
    (0, 1, AQUA, "THE ROBOT TODAY",
     "vendor geometry\nin ALUMINIUM\n\nworks — this is\nthe golden baseline"),
    (0, 0, BLUE, "PLATE 1  pass-throughs",
     "vendor geometry\nPRINTED\n\nshort-U · oblique-U\nmulti-mount · L · U-beam"
     "\n\ntests MATERIAL alone"),
    (1, 0, ORANGE, "PLATE 1-2  changed",
     "TALL geometry\nPRINTED\n\nlong-U · short-U closed\nstrap · boot · crest"
     "\n\ntests GEOMETRY"),
    (1, 1, None, "never built",
     "TALL geometry\nin aluminium\n\nnot interesting —\nwe are not machining"),
]

fig, ax = plt.subplots(figsize=(10.4, 6.6), facecolor=SURFACE)
ax.set_facecolor(SURFACE)
W, H, GAP = 4.0, 2.6, 0.45

for col, row, colour, title, body in CELLS:
    x, y = col * (W + GAP), row * (H + GAP)
    filled = colour is not None
    ax.add_patch(Rectangle((x, y), W, H, facecolor=SURFACE,
                           edgecolor=colour or MUTED, linewidth=2.4,
                           linestyle="-" if filled else (0, (5, 4)), zorder=3))
    if filled:
        ax.add_patch(Rectangle((x, y + H - 0.42), W, 0.42, facecolor=colour,
                               edgecolor="none", zorder=4))
    ax.text(x + W / 2, y + H - 0.21, title, ha="center", va="center",
            color=SURFACE if filled else T2, fontsize=11.5, weight="bold",
            family="monospace", zorder=5)
    ax.text(x + W / 2, y + (H - 0.42) / 2, body, ha="center", va="center",
            color=T1 if filled else MUTED, fontsize=10, family="monospace",
            linespacing=1.55, zorder=5)

# the two comparisons the test actually buys. Both arrows are drawn in the
# clear gap between cells; labels go OUTSIDE the grid so nothing overlaps.
ax.add_patch(FancyArrowPatch((W * 0.72, H + GAP - 0.06), (W * 0.72, H + 0.06),
                             arrowstyle="-|>,head_width=5,head_length=9",
                             color=AQUA, lw=2.6, zorder=7))
ax.text(W * 0.78, H + GAP / 2, "  COMPARE 1 — does PLASTIC hold?",
        ha="left", va="center", color=AQUA, fontsize=10.5, weight="bold",
        family="monospace", zorder=7)
ax.add_patch(FancyArrowPatch((W + 0.06, H * 0.5), (W + GAP - 0.06, H * 0.5),
                             arrowstyle="-|>,head_width=5,head_length=9",
                             color=ORANGE, lw=2.6, zorder=7))
ax.text(W + GAP / 2, -0.92, "COMPARE 2 — does the REDESIGN fit?",
        ha="center", va="center", color=ORANGE, fontsize=10.5, weight="bold",
        family="monospace", zorder=7)

ax.text(-0.35, H + GAP + H / 2, "ALUMINIUM", rotation=90, ha="center",
        va="center", color=T2, fontsize=11, family="monospace")
ax.text(-0.35, H / 2, "PRINTED", rotation=90, ha="center", va="center",
        color=T2, fontsize=11, family="monospace")
ax.text(W / 2, -0.5, "vendor geometry", ha="center", color=T2, fontsize=11,
        family="monospace")
ax.text(W + GAP + W / 2, -0.5, "TALL geometry", ha="center", color=T2,
        fontsize=11, family="monospace")

ax.set_title("Why the print test includes the UNMODIFIED vendor parts\n"
             "two variables changed at once — the pass-throughs separate them",
             color=T1, fontsize=13, family="monospace", pad=18)
ax.set_xlim(-1.0, 2 * W + GAP + 0.4)
ax.set_ylim(-1.45, 2 * H + GAP + 0.3)
ax.set_aspect("equal")
ax.axis("off")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "../../edu/print_files_tall/renders/test_matrix.png")
fig.savefig(out, dpi=150, facecolor=SURFACE, bbox_inches="tight")
print(f"wrote {os.path.abspath(out)}")
