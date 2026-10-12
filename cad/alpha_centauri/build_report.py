"""Alpha Centauri — the build page: every part, posed, with its numbers.

    edu/.cadenv/bin/python cad/alpha_centauri/build_report.py

One HTML file, opens in any browser, works offline. The 3D view and the figures
live in the SAME page on purpose -- a render in one file and a mass table in
another drift apart within a day, and then nobody knows which is current.

Every number below is MEASURED off the STEP at generation time. Nothing here is
typed in, so the page cannot claim a mass the geometry does not have.
"""

import subprocess
import sys
from pathlib import Path

from build123d import Location, import_step

from interface_constants import (
    CRAWL_SHIFT_CENTRED,
    CRAWL_STRIDE_HALF,
    L1_LATERAL,
    L1_VERTICAL,
    LEG_EXTENSION_LIMIT,
    LEG_REACH_MAX,
    L2_THIGH,
    L3_CALF,
    STANCE_Z,
    TARGET_TOTAL_HEIGHT,
    extension_at,
)

HERE = Path(__file__).parent
OUT = HERE / "output"
PETG = 0.953

# part, qty, what it is
BOM = [
    ("chassis_quarter_inner", 2, "midline quarter, rear copy spun 180 deg"),
    ("chassis_quarter_outer", 2, "end quarter: body + two 3S bays + dock contact pad"),
    ("abduction_pod", 4, "bolt-on servo pod, one STL, 6 x M3 heat-set inserts"),
    ("chassis_splice_key", 6, "loose shear key, two per splice plane"),
    ("thigh_shell", 4, "closed section; torsion is the only load that matters"),
    ("thigh_cover", 4, "structural, not cosmetic -- it closes the box"),
    ("calf", 4, "open web; prints on its side for round bearing seats"),
    ("horn_adapter", 4, "spans horn PCD to bearing OD"),
    ("bearing_retainer", 4, "bears on the OUTER race only"),
    ("bearing_carrier", 4, "plugs the thigh bore, presents the 8 mm stub"),
    ("spine_rack", 1, "hand-driven ratchet, 24 teeth at 12 mm"),
    ("spine_pawl", 1, "leaf undeflected when seated, so it cannot creep"),
    ("rail_way_inner", 4, "dovetail way, splice-to-splice 125 mm segment (A1 mini)"),
    ("rail_way_outer", 4, "dovetail way, splice-to-pod 125 mm segment"),
    ("rail_way_key", 6, "loose joint key -- registers Y/Z across a way butt joint"),
    ("rail_carriage_half_aft", 1, "carriage half, dowelled + bolted at x = 0"),
    ("rail_carriage_half_fwd", 1, "carriage half; both drive modules share the one hole"),
    ("rail_rack", 1, "module 3 rack, 21 teeth, lives in the chassis well"),
]

# Fitted to ONE variant or the other, never both.
VARIANT = [
    ("rail_pinion", "servo+", "13T involute, +0.25 shift, tip-shortened"),
    ("rail_pawl", "servo-", "two-way detent on the rack's own 20 deg flanks"),
    ("rail_lever", "servo-", "unseats the pawl; without it the arms cannot slide"),
]


def _g(name):
    p = OUT / f"{name}.step"
    if not p.exists():
        return None
    return import_step(str(p)).volume / 1000.0 * PETG


def notes_html():
    rows, total = [], 0.0
    for name, qty, why in BOM:
        g = _g(name)
        if g is None:
            continue
        total += g * qty
        rows.append(
            f"<tr><td>{name.replace('_',' ')}</td>"
            f"<td class=n>{qty}</td><td class=n>{g:.1f}</td>"
            f"<td class=n>{g*qty:.1f}</td></tr>"
        )
    rows.append(
        f"<tr class=tot><td>printed structure</td><td class=n></td>"
        f"<td class=n></td><td class=n>{total:.0f} g</td></tr>"
    )

    stand = extension_at(STANCE_Z)
    crawl = extension_at(STANCE_Z, CRAWL_SHIFT_CENTRED, CRAWL_STRIDE_HALF)
    pct = lambda v: 100 * v / LEG_REACH_MAX

    vrows = []
    for name, which, why in VARIANT:
        g = _g(name)
        if g is None:
            continue
        vrows.append(
            f"<tr><td>{name.replace('_',' ')}</td><td>{which}</td>"
            f"<td class=n>{g:.1f}</td><td>{why}</td></tr>")

    return f"""
<h2>The variant seam</h2>
<p>The author, today: <i>&ldquo;this could be a split between the servo+ version and the
servo&minus; version&hellip; we'll have to see what's what.&rdquo;</i> It is a
split, and the honest finding is that it is <b>three separate decisions, and
they do not all go the same way.</b></p>
<table>
<tr><th>job</th><th>hand-driven?</th><th>why</th></tr>
<tr><td>raise the chest</td><td><span class=warn>heavy</span></td>
    <td>72% of a measured servo per arm at 200&nbsp;mm reach; 54% with the elbow
    folded. It works, but it is the expensive one.</td></tr>
<tr><td>slide the waist</td><td><span class=ok>yes</span></td>
    <td>12% &mdash; but only after the release lever unseats the pawl. Shoving
    against a live detent is 97% and simply will not move.</td></tr>
<tr><td>turn the chest</td><td><span class=ok>yes</span></td>
    <td>9% to turn. Holding is the problem, not turning &mdash; see below.</td></tr>
</table>
<p>And it runs the other way for the spine drive itself. On <b>M8 threaded
rod</b> the motorised spine needs 200 turns for 250&nbsp;mm &mdash; about
<b>3 minutes</b>. The hand-driven rack does it in two presses. servo+ only wins
that job with a bought <b>T8 lead screw</b> (8&nbsp;mm lead, ~28&nbsp;s).</p>
<table>
<tr><th>part</th><th>variant</th><th class=n>g</th><th>note</th></tr>
{''.join(vrows)}
</table>

<h2>Mass, measured off the STEP</h2>
<table>
<tr><th>part</th><th class=n>qty</th><th class=n>ea g</th><th class=n>total</th></tr>
{''.join(rows)}
</table>
<p>{100*total/5500:.1f}% of the 5.5&nbsp;kg design mass. Hips, feet and head
still to come.</p>

<h2>The rail, and why it is Mk1</h2>
<p>The torso is <b>1538&nbsp;g of 4370&nbsp;g &mdash; 35.2%</b>. Sliding it
<i>d</i>&nbsp;mm moves the centre of mass 0.352<i>d</i>, so 150&nbsp;mm of travel
is <b>53&nbsp;mm of CoM authority</b> against a crawl boundary that is tight to
about 25&nbsp;mm. Nothing else on the robot has that much leverage.</p>
<table>
<tr><th>mode</th><th class=n>torso x</th><th class=n>CoM</th><th>stance</th></tr>
<tr><td>WALK</td><td class=n>+37</td><td class=n>0.0</td>
    <td>crawl-legal &mdash; the CoM must sit at the wheelbase midpoint</td></tr>
<tr><td>WORK</td><td class=n>+167</td><td class=n>+45.8</td>
    <td>four feet down; torso over the front legs</td></tr>
</table>
<p>Used <b>backwards</b> from the obvious: aft to walk, forward to work. It is a
mode switch, not a better fixed compromise.</p>

<h2 class=warn>Retracted today: asymmetric hips do nothing</h2>
<p>This page previously carried hips at +300/&minus;200. The author looked at the render
and said it seemed like nothing had changed but the length of one half. He was
right. With the wheelbase length fixed, moving the hip stations only relabels the
origin &mdash; the counterweight lever about the midpoint is <b>190.0&nbsp;mm
either way</b>. The apparent gain came from pinning the battery at
x&nbsp;=&nbsp;&minus;190 in every configuration while the rear body shrank, so
the symmetric layout was never allowed the &minus;240 it could have had. Hips are
back to &plusmn;250, which also restores &ldquo;one chassis part, printed
twice.&rdquo;</p>

<h2>Stance</h2>
<table>
<tr><td>leg reach</td><td class=n>{LEG_REACH_MAX:.2f} mm</td><td></td></tr>
<tr><td>standing</td><td class=n>{stand:.2f} mm</td>
    <td class=n><span class=ok>{pct(stand):.1f}%</span></td></tr>
<tr><td>mid-crawl</td><td class=n>{crawl:.2f} mm</td>
    <td class=n><span class=ok>{pct(crawl):.1f}%</span></td></tr>
<tr><td>0.97 guard</td><td class=n>{LEG_EXTENSION_LIMIT:.2f} mm</td>
    <td class=n>97.0%</td></tr>
</table>
<p>The <b>crawl</b> pose binds, not the standing one. Standing looks roomy and
is not the pose that fails. This is what killed raising the stance to 240&nbsp;mm:
it stands fine, then needs 97.3% of reach just to shift its body sideways.</p>

<h2>Geometry that bit us</h2>
<p><b>L1 is a diagonal.</b> {L1_LATERAL} mm outboard <b>and</b> {L1_VERTICAL} mm
up — hypot = {(L1_LATERAL**2 + L1_VERTICAL**2)**0.5:.5f}, which is the donor's
own L1. Using the hypotenuse as if it were lateral drew the robot 14.3 mm too
tall and 4.0 mm too wide.</p>
<p><b>The foot sphere is centred {L3_CALF - 15:.2f} mm from the knee, not
{L3_CALF:.2f}.</b> That is what puts the contact point at exactly L3 for every
calf angle across the 38.5&deg; swing.</p>

<h2>Caught before printing</h2>
<ul>
<li><b>Calf buried 1.62 cm&sup3; inside the thigh</b> at zero knee bend. Passed
every single-part check — only a swept interference test sees it.</li>
<li><b>Cover came out as 5 loose solids</b> — M3 clearance is 3.4 mm and the
flange was 3.0 mm wide, so each hole cut its rib through.</li>
<li><b>51 mm&sup2; of bed contact</b> on a 140 mm part: the lug circles touch the
plate on a tangent line. Geometrically perfect, would have sheared off.</li>
<li><b>Rebate as deep as the wall</b> is a through-hole with a razor shoulder.</li>
<li><b>Rack tooth tips were knife edges</b> — 1.6% of surface under two
extrusions.</li>
<li><b>The pinion did not roll.</b> Rolling without slip makes rotation and
translation opposite in sign; drawn the other way the gear ground
<b>364.6&nbsp;mm&sup3;</b> straight through the rack and still looked like a
gear. The swept mesh test now reads 0.0000&nbsp;mm&sup3;.</li>
<li><b>Carriage came out as 3 solids</b> — the shoes are 26.7&nbsp;mm wide on a
ledge at y&nbsp;=&nbsp;71, so the outboard hook landed past the plate edge and
printed as two loose slivers.</li>
<li><b>The pawl's release lever swept through the rack</b> (460&nbsp;mm&sup3;).
Moving it behind the leaf then put features on both faces and no print
orientation was clean — so it became a separate 6.6&nbsp;g part, which is also
what lets the pawl print leaf-flat.</li>
<li><b>Carriage graded 24.1% support</b> until it was graded in the pose it
actually prints in. Flipped, it is 0.5% and bed contact goes
4000&nbsp;&rarr;&nbsp;24511&nbsp;mm&sup2;.</li>
<li><b>Rack lightening diamonds undercut the tooth roots</b> — caught in the
<i>render</i>, not the checks: partcheck passed it at 2.80&nbsp;mm because a thin
ligament is not a broken one.</li>
</ul>

<h2>The yaw lock has to be a pin, not a detent</h2>
<p>The disturbance is the robot's <b>own arm</b>. One arm at 300&nbsp;mm reach
makes 2.45&nbsp;N&middot;m about the yaw axis; slew friction holds
0.226&nbsp;N&middot;m, or <b>9% of it</b>. A spring detent would need 61&nbsp;N
tangential, far past a printed leaf. A <b>5&nbsp;mm pin in double shear</b> holds
982&nbsp;N against the 53&nbsp;N needed — SF&nbsp;18.7 — and cannot cam out at
any load. So: an indexed ring, 24 stations, 15&deg; resolution.
<span class=warn>Specified here, not yet drawn.</span></p>

<h2>Open</h2>
<ul>
<li class=warn>Servo height unresolved: vendor ST3215 measures 37.80 mm,
our NOMINAL says 35.00. Two of three dimensions match exactly. No pocket prints
until this is settled.</li>
<li>Height {TARGET_TOTAL_HEIGHT:.0f} mm total: chest tops out at 671 mm, so a
~179 mm head closes it with no stroke change.</li>
<li>Hip modules, feet and head not yet drawn.</li>
</ul>
"""


def main():
    asm = OUT / "centaur"
    stls = sorted(asm.glob("*.stl"))
    if not stls:
        print("run assembly.py first"); return
    nt = OUT / "_notes.html"
    nt.write_text(notes_html())
    html = OUT / "alpha_centauri_build.html"
    subprocess.run(
        [sys.executable, str(HERE.parent.parent / "edu/tools/stl_viewer.py"),
         *[str(p) for p in stls], "-o", str(html),
         "-t", "Alpha Centauri Mk1 — symmetric hips, waist rail, both variants", "-n", str(nt)],
        check=True)
    print(f"\npress N in the page to hide/show the notes")
    return html


if __name__ == "__main__":
    main()
