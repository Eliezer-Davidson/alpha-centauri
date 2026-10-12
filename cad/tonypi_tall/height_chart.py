#!/usr/bin/env python3
"""Height-budget comparison chart: stock TonyPi vs TALL variant.

    edu/.cadenv/bin/python cad/tonypi_tall/height_chart.py

Stacked composition bars from tall_constants.py — nothing hardcoded.
Palette: dataviz reference categorical (dark mode), adjacent-order validated.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tall_constants as C  # noqa: E402

SURFACE = "#1a1a19"
TEXT_1 = "#ffffff"
TEXT_2 = "#c3c2b7"
SERIES = {  # dataviz reference palette, dark column, fixed slot order
    "platform sole": "#3987e5",
    "shank link": "#d95926",
    "thigh link": "#199e70",
    "torso + hip": "#c98500",
    "head": "#d55181",
}
VIOLET = "#9085e9"  # decorative crest (hatched, not counted in height)

LINK = 80.0                      # stock joint-to-joint (UNVERIFIED, CAD-DECISION)
TORSO = C.STOCK_HEIGHT - 2 * LINK - 40.0   # remainder block
STOCK = [0.0, LINK, LINK, TORSO, 40.0]
TALL = [C.SOLE_H, LINK + C.LEG_LINK_EXT, LINK + C.LEG_LINK_EXT, TORSO, 40.0]

fig, ax = plt.subplots(figsize=(8.6, 7.2), facecolor=SURFACE)
ax.set_facecolor(SURFACE)
xs, labels = [0, 1], ["STOCK", "TALL variant"]
for x, segs in zip(xs, [STOCK, TALL]):
    y = 0.0
    for (name, color), h in zip(SERIES.items(), segs):
        if h <= 0:
            y += h
            continue
        ax.bar(x, h, bottom=y, width=0.46, color=color,
               edgecolor=SURFACE, linewidth=2, zorder=3)
        if h >= 8:
            ax.text(x, y + h / 2, f"{h:.0f}", ha="center", va="center",
                    color=TEXT_1, fontsize=10, family="monospace", zorder=4)
        y += h
    total = sum(segs)
    # TALL bar carries hatched extras above it — lift its total clear of them
    dy = 26 if x == 0 else C.BEAM_EXT + C.CREST_H + 32
    ax.text(x, y + dy, f"{total:.0f} mm", ha="center", color=TEXT_1,
            fontsize=15, weight="bold", family="monospace")

# deferred torso raise: hatched extension on the TALL bar
y_tall = sum(TALL)
ax.bar(1, C.BEAM_EXT, bottom=y_tall, width=0.46, facecolor="none",
       edgecolor=SERIES["torso + hip"], linewidth=1.4, hatch="//", zorder=3)
ax.text(1.30, y_tall + C.BEAM_EXT / 2, f"+{C.BEAM_EXT:.0f} torso raise\n(DEFERRED)",
        va="center", color=TEXT_2, fontsize=9, family="monospace")
# mohawk: decorative, drawn distinct and not counted
ax.bar(1, C.CREST_H, bottom=y_tall + C.BEAM_EXT + 6, width=0.2,
       facecolor="none", edgecolor=VIOLET, linewidth=1.4, hatch="xx", zorder=3)
ax.text(1.30, y_tall + C.BEAM_EXT + 6 + C.CREST_H / 2,
        f"+{C.CREST_H:.0f} mohawk crest\n(decorative)",
        va="center", color=VIOLET, fontsize=9, family="monospace")

gain = sum(TALL) - sum(STOCK)
ax.annotate("", xy=(0.62, sum(TALL)), xytext=(0.62, sum(STOCK)),
            arrowprops=dict(arrowstyle="<->", color=TEXT_2, lw=1.2))
ax.text(0.56, (sum(TALL) + sum(STOCK)) / 2, f"+{gain:.0f} mm\nconfirmed",
        ha="right", va="center", color=TEXT_1, fontsize=10, family="monospace")

for x, w in zip(xs, [63, C.FOOT_W]):
    ax.text(x, -34, f"foot width {w:.0f} mm", ha="center", color=TEXT_2,
            fontsize=9, family="monospace")

ax.set_xticks(xs)
ax.set_xticklabels(labels, color=TEXT_1, fontsize=12, family="monospace")
ax.set_xlim(-0.55, 1.95)
ax.set_ylim(-50, 560)
ax.set_ylabel("height (mm)", color=TEXT_2, family="monospace")
ax.tick_params(colors=TEXT_2)
for s in ax.spines.values():
    s.set_visible(False)
ax.grid(axis="y", color="#383835", linewidth=0.6, zorder=0)
ax.set_axisbelow(True)

handles = [Patch(facecolor=c, label=n) for n, c in SERIES.items()]
handles += [Patch(facecolor="none", edgecolor=SERIES["torso + hip"], hatch="//",
                  label="deferred (needs check)"),
            Patch(facecolor="none", edgecolor=VIOLET, hatch="xx",
                  label="decorative crest")]
leg = ax.legend(handles=handles, loc="upper left", frameon=False, fontsize=9)
for t in leg.get_texts():
    t.set_color(TEXT_2)
    t.set_family("monospace")

ax.set_title("TonyPi height budget — stock vs TALL "
             "(stock 380 mm & link 80 mm are UNVERIFIED: measure the robot)",
             color=TEXT_1, fontsize=10.5, family="monospace", pad=14)
out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "../../edu/print_files_tall/renders/height_comparison.png")
fig.tight_layout()
fig.savefig(out, dpi=150, facecolor=SURFACE, bbox_inches="tight")
print(f"wrote {os.path.abspath(out)}")
