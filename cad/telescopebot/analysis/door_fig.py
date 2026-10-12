"""Proof figure for the Alpha Centauri door-sequence analysis (house law:
every geometry/engineering claim ships with a rendered image)."""
import json, math, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, FancyArrow

HERE = pathlib.Path(__file__).parent
N = json.loads((HERE/"door_seq_numbers.json").read_text())
W, B_WORK, B_REAR = N["W"], N["B_WORK"], N["B_REAR"]
F_WORST, F_REAL, F_NOM = N["F_WORST"], N["F_REAL"], N["F_NOM"]
F_LEG = N["F_LEG_SUST"]

fig = plt.figure(figsize=(17, 11.0))
fig.suptitle("Alpha Centauri — door sequence: what the numbers say\n"
             f"robot {N['M_TOT']:.2f} kg / {W:.1f} N (short arms, re-derived) · "
             f"door-stance tipping budget {B_WORK:.2f} N·m · "
             f"design-ceiling door force {F_WORST:.0f} N",
             fontsize=13.5, fontweight="bold")
gs = fig.add_gridspec(2, 3, hspace=0.42, wspace=0.30,
                      left=0.055, right=0.975, top=0.865, bottom=0.065)

RED, AMB, GRN, GRY = "#c0392b", "#e08a1e", "#1e8449", "#7f8c8d"
def col(ratio):  # ratio = capability / demand
    return GRN if ratio >= 1.5 else (AMB if ratio >= 1.0 else RED)

# ---------------------------------------------------------------- panel 1
ax = fig.add_subplot(gs[0, 0])
levers = ["light\n0.8", "typical\n1.5", "stiff/worn\n2.5", "ANSI/ICC max\n3.16"]
T = np.array([0.8, 1.5, 2.5, 3.164])
standoffs = [(0.150, "150 mm standoff"), (0.185, "185 mm"), (0.250, "250 mm")]
x = np.arange(len(T)); wdt = 0.26
for i, (so, lbl) in enumerate(standoffs):
    d_f = so - 0.065
    M = T/0.110*d_f
    b = ax.bar(x + (i-1)*wdt, M, wdt, label=lbl,
               color=[col(B_WORK/m) for m in M], edgecolor="k", linewidth=0.6,
               hatch=["", "//", "xx"][i])
ax.axhline(B_WORK, color="k", lw=2, label=f"tipping budget {B_WORK:.2f} N·m")
ax.axhline(B_WORK/1.5, color="k", lw=1.2, ls="--", label="budget / 1.5× margin")
ax.set_xticks(x); ax.set_xticklabels(levers, fontsize=8.5)
ax.set_ylabel("forward tipping moment  (N·m)")
ax.set_title("(a-i) LEVER PRESS — reaction moment\nstanding CLOSE is the whole game",
             fontsize=10.5, fontweight="bold")
ax.legend(fontsize=7.2, loc="upper left"); ax.grid(axis="y", alpha=0.3)
ax.text(0.98, 0.03, "break-even lever torque\nat 185 mm: "
        f"{N['T_LEV_MAX']:.2f} N·m", transform=ax.transAxes, ha="right",
        fontsize=8, bbox=dict(fc="#fff3cd", ec="k", lw=0.5))

# ---------------------------------------------------------------- panel 2
ax = fig.add_subplot(gs[0, 1])
servos = ["MG996R\n(x22 owned)", "SCS15\n(x4 owned)", "STS3215\n(x1 owned)",
          "STS3250\n(leg servo)", "DS5160\n(x2 owned)"]
cap = np.array([10, 17, 30, 50, 60], float)
need = 28.8*0.300*10.1972            # N·m -> kg·cm
bars = ax.barh(servos, cap, color=[col(c/need) for c in cap],
               edgecolor="k", linewidth=0.6)
ax.axvline(need, color="k", lw=2)
ax.text(need*1.02, 4.35, f"required\n{need:.0f} kg·cm", fontsize=8.5, va="top")
ax.axvline(need*1.5, color="k", lw=1.2, ls="--")
ax.text(need*1.52, 0.0, "×1.5", fontsize=8)
for b, c in zip(bars, cap):
    ax.text(c+1.5, b.get_y()+b.get_height()/2, f"{c:.0f}", va="center", fontsize=8.5)
ax.set_xlabel("stall torque  (kg·cm)"); ax.set_xlim(0, need*1.75)
ax.set_title("(a-ii) NO ARM SERVO CAN PRESS THE LEVER\n28.8 N × 0.30 m reach = 8.6 N·m at the shoulder",
             fontsize=10.5, fontweight="bold")
ax.grid(axis="x", alpha=0.3)
ax.text(0.98, 0.06, "⇒ the arm must be a RIGID STRUT\nagainst a printed hard stop;\n"
        "force comes from spine descent\nor a body-height drop",
        transform=ax.transAxes, ha="right", fontsize=8.2,
        bbox=dict(fc="#f8d7da", ec=RED, lw=1))

# ---------------------------------------------------------------- panel 3
ax = fig.add_subplot(gs[0, 2])
surf = ["bare PETG\non hardwood\n(UNVERIFIED)", "TPU 95A pad\non hardwood",
        "rubber pad\non low carpet"]
lo = np.array([0.25, 0.70, 0.50])*W
hi = np.array([0.35, 0.90, 1.25])*W
y = np.arange(3)
ax.barh(y, hi-lo, left=lo, height=0.45, color=[col(l/F_WORST) for l in lo],
        edgecolor="k", linewidth=0.6)
for i in range(3):
    ax.text(hi[i]+1.2, y[i], f"{lo[i]:.0f}–{hi[i]:.0f} N", va="center", fontsize=8.5)
ax.axvline(F_WORST, color="k", lw=2)
ax.axvline(F_WORST*1.5, color="k", lw=1.2, ls="--")
ax.text(F_WORST+0.8, 1.62, f"design\nceiling\n{F_WORST:.0f} N", fontsize=8.2, va="center")
ax.text(F_WORST*1.5+0.8, 1.62, "×1.5", fontsize=8, va="center", rotation=90)
ax.axvline(F_REAL, color=GRY, lw=1.2, ls=":")
ax.text(F_REAL-0.8, 1.62, f"analytic\nworst\n{F_REAL:.0f} N", fontsize=7.4,
        color=GRY, ha="right", va="center")
ax.set_yticks(y); ax.set_yticklabels(surf, fontsize=8.5)
ax.set_xlabel("horizontal force before slip,  F = μ·W  (N)"); ax.set_xlim(0, 78)
ax.set_title("(c) TRACTION vs DOOR FORCE\nTPU foot pads are NOT optional",
             fontsize=10.5, fontweight="bold"); ax.grid(axis="x", alpha=0.3)

# ---------------------------------------------------------------- panel 4
ax = fig.add_subplot(gs[1, 0])
F = np.linspace(0, 45, 300)
ax.plot(F, F*0.240*10.1972, lw=2.4, color=RED, label="hip roll/pitch servo (binding joint)")
ax.plot(F, F*0.1298*10.1972, lw=2.0, color=AMB, label="knee servo")
ax.axhline(25, color="k", lw=2, ls="-")
ax.axhline(48, color="k", lw=1.4, ls="--")
ax.text(45, 25.6, "STS3250 25 kg·cm SUSTAINED (measured)", fontsize=7.8, ha="right")
ax.text(45, 48.6, "48 kg·cm peak (measured)", fontsize=7.8, ha="right")
ax.axvline(F_LEG, color=RED, ls=":", lw=1.6)
ax.text(F_LEG+0.7, 78, f"leg limit\n{F_LEG:.1f} N", fontsize=8.5, color=RED,
        fontweight="bold", bbox=dict(fc="white", ec="none", alpha=0.85))
for v, lbl, c in ((F_NOM, f"nominal door\n{F_NOM:.0f} N", GRN),
                  (F_REAL, f"analytic worst\n{F_REAL:.0f} N", AMB),
                  (F_WORST, f"design ceiling\n{F_WORST:.0f} N", RED)):
    ax.axvline(v, color=c, ls="-", lw=1.0, alpha=0.55)
    ax.text(v, 4, lbl, fontsize=7.4, ha="center", color=c, va="bottom",
            bbox=dict(fc="white", ec="none", alpha=0.85))
ax.set_xlabel("pry force at the wedged paw  (N)")
ax.set_ylabel("servo torque demanded  (kg·cm)")
ax.set_ylim(0, 135); ax.set_xlim(0, 45)
ax.set_title("(d) THE LEG PRY FAILS AT THE HIP\nnot at the knee, and never in the printed part",
             fontsize=10.5, fontweight="bold")
ax.legend(fontsize=7.8, loc="upper left"); ax.grid(alpha=0.3)

# ---------------------------------------------------------------- panel 5
ax = fig.add_subplot(gs[1, 1])
h = np.array([0.05, 0.10, 0.20, 0.30, 0.40, 0.60, 1.05])
M = F_WORST*h
bars = ax.bar(range(len(h)), M, color=[col(B_WORK/m) for m in M],
              edgecolor="k", linewidth=0.6)
ax.axhline(B_WORK, color="k", lw=2)
ax.axhline(B_WORK/1.5, color="k", lw=1.2, ls="--")
ax.text(0.05, B_WORK+0.7, f"tipping budget {B_WORK:.2f} N·m", fontsize=8.4)
ax.set_xticks(range(len(h)))
ax.set_xticklabels([f"{v*1000:.0f}" for v in h], fontsize=8.5)
ax.set_xlabel("height at which the pulling force is applied  (mm)")
ax.set_ylabel(f"overturning moment at {F_WORST:.0f} N  (N·m)")
ax.set_title("(e) IT IS THE FORCE HEIGHT, NOT THE CG HEIGHT\n"
             "static tipping contains no z_cg term at all",
             fontsize=10.5, fontweight="bold"); ax.grid(axis="y", alpha=0.3)
for i, (hh, mm) in enumerate(zip(h, M)):
    ax.text(i, mm+0.5, f"{mm:.1f}", ha="center", fontsize=7.8)
ax.annotate("chassis hook", (1, M[1]), (0.42, 0.42), textcoords="axes fraction",
            fontsize=8.5, color=GRN, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=GRN))
ax.annotate("arm at the lever\n(spine up, 105 cm)", (6, M[6]), (0.24, 0.78),
            textcoords="axes fraction", fontsize=8.5, color=RED, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color=RED))
ax.text(0.36, 0.03, f"max allowed height at {F_WORST:.0f} N, ×1.5 margin:\n"
        f"{N['hook_h_max']*1000:.0f} mm above the floor",
        transform=ax.transAxes, fontsize=8.4,
        bbox=dict(fc="#fff3cd", ec="k", lw=0.5))

# ---------------------------------------------------------------- panel 6
ax = fig.add_subplot(gs[1, 2]); ax.axis("off")
ax.set_title("PROBABILITY OF SUCCESS — FIRST ATTEMPT", fontsize=10.5, fontweight="bold")
plans = [
    ("FULL SEQUENCE AS SPECIFIED\nlever → crack → paw in gap → leg pry backwards",
     [("lever turns", .50), ("crack holds", .55), ("paw enters gap", .35),
      ("leg pry ≤10 N", .40)], 7, RED),
    ("WITH A LOW CHASSIS HOOK instead of the leg",
     [("lever turns", .50), ("crack holds", .55), ("hook catches", .55),
      ("hook pry ≤30 N", .70)], 19, AMB),
    ("RECOMMENDED: LEVER PRESS + PUSH THROUGH\n(choose a PUSH door — deletes gap + pry)",
     [("lever turns", .50), ("crack holds", .60), ("chest push through", .90),
      ("walk through", .95)], 55, "#2874a6"),
    ("FALLBACK: PUSH-DOOR TOUCH-AND-THROUGH\n(unlatched, opens away, no arm at all)",
     [("find door", .97), ("chest push 3 N vs 38 N traction", .97),
      ("walk through", .96)], 92, GRN),
]
yy = 0.955
for title, stages, pct, c in plans:
    ax.text(0.0, yy, title, fontsize=9.1, fontweight="bold", va="top", color=c)
    yy -= 0.075 if "\n" in title else 0.048
    for s, v in stages:
        ax.add_patch(Rectangle((0.03, yy-0.028), 0.42*v, 0.026, fc=c, alpha=0.55, ec="k", lw=0.4))
        ax.text(0.47, yy-0.015, f"{v:.2f}  {s}", fontsize=7.9, va="center")
        yy -= 0.036
    ax.add_patch(Rectangle((0.03, yy-0.040), 0.90*pct/100, 0.034, fc=c, ec="k", lw=0.8))
    ax.text(0.03+0.90*pct/100+0.02, yy-0.023, f"≈ {pct}%", fontsize=10.5,
            fontweight="bold", va="center", color=c)
    yy -= 0.085
ax.set_xlim(0, 1); ax.set_ylim(0, 1)

out = HERE/"alpha_centauri_door_analysis.png"
fig.savefig(out, dpi=125, facecolor="white")
print("wrote", out)
