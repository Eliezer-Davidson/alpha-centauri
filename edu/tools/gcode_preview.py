import re, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

path, out = sys.argv[1], sys.argv[2]
x=y=z=0.0; e=0.0; rel_e=False; abs_pos=True
segs=[]   # (x0,y0,x1,y1,z, extruding)
for ln in open(path, errors='replace'):
    ln=ln.split(';')[0].strip()
    if not ln: continue
    if ln.startswith('M83'): rel_e=True; continue
    if ln.startswith('M82'): rel_e=False; continue
    if ln.startswith('G90'): abs_pos=True; continue
    if ln.startswith('G91'): abs_pos=False; continue
    if ln.startswith('G92'):
        m=re.search(r'E(-?[\d.]+)', ln)
        if m: e=float(m.group(1))
        continue
    if not re.match(r'G[01]\b', ln): continue
    nx,ny,nz,ne = x,y,z,None
    for ax,val in re.findall(r'([XYZE])(-?[\d.]+)', ln):
        v=float(val)
        if ax=='X': nx = v if abs_pos else x+v
        elif ax=='Y': ny = v if abs_pos else y+v
        elif ax=='Z': nz = v if abs_pos else z+v
        elif ax=='E': ne = v
    extruding=False
    if ne is not None:
        de = ne if rel_e else (ne-e)
        extruding = de > 1e-6
        e = ne if not rel_e else e
    if nx!=x or ny!=y:
        segs.append((x,y,nx,ny,nz,extruding))
    x,y,z = nx,ny,nz

segs=np.array([(a,b,c,d,zz,f) for a,b,c,d,zz,f in segs], dtype=float)
print(f"{len(segs)} moves, z range {segs[:,4].min():.2f}..{segs[:,4].max():.2f}")

ext=segs[segs[:,5]>0]
zs=np.unique(np.round(ext[:,4],3))
first_z=zs[0]
# Include everything up to 0.35 mm: the part's first layer is at 0.25 but
# the start-gcode purge line runs at z=0.30 and must be shown too.
fl=ext[ext[:,4] <= 0.35]
print(f"first layer z={first_z}, {len(fl)} extruding moves below z=0.35")

fig,(ax1,ax2)=plt.subplots(1,2,figsize=(15,7.4))

# --- first layer on the bed ---
ax1.add_patch(plt.Rectangle((-175,-175),350,350,fc="#eeeeee",ec="#888",lw=1.2,zorder=0))
for x0,y0,x1,y1,_,_ in fl:
    ax1.plot([x0,x1],[y0,y1],color="#c0392b",lw=0.9,solid_capstyle="round",zorder=3)
ax1.set_xlim(-190,190); ax1.set_ylim(-190,190); ax1.set_aspect("equal")
ax1.set_title(f"First layer on the 350x350 bed (z={first_z} mm)\n"
              "grey = printable area, red = extrusion",fontsize=11,fontweight="bold")
ax1.set_xlabel("X mm"); ax1.set_ylabel("Y mm"); ax1.grid(alpha=.25)
ax1.axhline(0,color="#999",lw=.6); ax1.axvline(0,color="#999",lw=.6)
ax1.plot(0,0,'k+',ms=10)
ax1.annotate("purge line (z=0.30, Y=-167)", xy=(0,-167), xytext=(-155,-186),
             fontsize=8, color="#c0392b",
             arrowprops=dict(arrowstyle="->",color="#c0392b",lw=.8))

# --- zoom on the part ---
px0,px1=fl[:,[0,2]].min(),fl[:,[0,2]].max()
py0,py1=fl[:,[1,3]].min(),fl[:,[1,3]].max()
part=fl[(fl[:,1]>-160)]
for x0,y0,x1,y1,_,_ in part:
    ax2.plot([x0,x1],[y0,y1],color="#2c6e49",lw=1.3,solid_capstyle="round")
if len(part):
    cx0,cx1=part[:,[0,2]].min(),part[:,[0,2]].max()
    cy0,cy1=part[:,[1,3]].min(),part[:,[1,3]].max()
    m=6
    ax2.set_xlim(cx0-m,cx1+m); ax2.set_ylim(cy0-m,cy1+m)
    ax2.set_title(f"First layer detail — part footprint "
                  f"{cx1-cx0:.1f} x {cy1-cy0:.1f} mm\n"
                  "outer ring = 3 mm brim",fontsize=11,fontweight="bold")
ax2.set_aspect("equal"); ax2.grid(alpha=.25)
ax2.set_xlabel("X mm"); ax2.set_ylabel("Y mm")

title = sys.argv[3] if len(sys.argv) > 3 else "FlashForge Guider 3 Plus profile"
fig.suptitle(f"OrcaSlicer 2.3.0 output — {title}",
             fontsize=13,fontweight="bold")
fig.tight_layout(rect=(0,0,1,0.96))
fig.savefig(out,dpi=110)
print("->",out)
