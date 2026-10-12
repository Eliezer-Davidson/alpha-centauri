#!/usr/bin/env python3
"""Turn STL files into ONE self-contained HTML page with a live 3D viewer.

    edu/.cadenv/bin/python edu/tools/stl_viewer.py part.stl [more.stl ...] -o view.html

Why this exists: OrcaSlicer's newer AppImages need GLIBC 2.38 and this box is
Ubuntu 22.04 (2.35), and a slicer is the wrong tool for "let me look at the
part" anyway. The output here is a single .html with the mesh embedded -- it
opens in any browser, works offline, survives being emailed, and has no
dependency that can go stale.

Hand-written WebGL1, no three.js, no CDN (an Artifact's CSP blocks external
hosts, and a viewer that needs the network is not a viewer you can trust).

Mesh payload is quantised to int16 per axis, which is ~1/50 mm on a 250 mm part
-- far below layer height, so it costs nothing visible and cuts the page to a
third of what raw float32 would.

MOTION-GROUP MANIFESTS (kinematically moveable pages). Pass a manifest with
--manifest pose.json -- or simply place it next to the output, named
<out with .html replaced by _manifest.json>, and it is AUTO-DETECTED. That
naming rule is a contract: cad/alpha_centauri/marks.py writes
<mark page>_manifest.json beside each HTML it asks this tool to build, and the
pose panel appears with zero new flags on marks.py's side. The manifest maps
each emitted STL basename to translation groups (see load_manifest for the
shape); the page then grows one slider per group (detent buttons included)
that slides every member part by (slider - as_built_value) * axis, composing
across groups, plus ctrl/M-drag free movement of a picked part. Everything
pose-related is injected through placeholders that collapse to the empty
string in plain mode, so WITHOUT a manifest the page is BYTE-FOR-BYTE what
this tool always produced -- other projects (telescopebot) share this tool
and their pages must not change. --no-manifest forces plain mode even when a
manifest file sits beside -o.
"""
import argparse
import base64
import json
import os
import struct
import sys

# ---------------------------------------------------------------- STL reading


def read_stl(path):
    """Return a flat list of triangle vertices [x,y,z, x,y,z, ...] in mm.

    Handles binary and ASCII. Face normals in the file are ignored -- they are
    routinely wrong in exported STLs, and a cross product in the loader is both
    free and correct.
    """
    with open(path, "rb") as f:
        raw = f.read()

    # ASCII STLs start with "solid", but so do some binary ones written by
    # sloppy exporters -- so verify against the declared triangle count.
    is_binary = True
    if raw[:5].lower() == b"solid" and len(raw) >= 84:
        n = struct.unpack_from("<I", raw, 80)[0]
        if 84 + n * 50 != len(raw):
            is_binary = False
    elif raw[:5].lower() == b"solid":
        is_binary = False

    verts = []
    if is_binary:
        n = struct.unpack_from("<I", raw, 80)[0]
        off = 84
        for _ in range(n):
            # skip the stored normal (12 bytes), take the 9 vertex floats
            vals = struct.unpack_from("<9f", raw, off + 12)
            verts.extend(vals)
            off += 50
    else:
        for line in raw.decode("utf-8", "replace").splitlines():
            s = line.strip()
            if s.startswith("vertex"):
                verts.extend(float(v) for v in s.split()[1:4])

    if not verts:
        raise ValueError(f"{path}: no triangles found")
    return verts


def quantise(verts):
    """int16-encode vertices, returning (base64, origin, scale).

    Decode in JS as: v = origin + q * scale
    """
    xs, ys, zs = verts[0::3], verts[1::3], verts[2::3]
    lo = [min(xs), min(ys), min(zs)]
    hi = [max(xs), max(ys), max(zs)]
    # one shared scale for all three axes so the part is not silently distorted
    span = max(hi[i] - lo[i] for i in range(3)) or 1.0
    scale = span / 65534.0

    buf = bytearray()
    for i in range(0, len(verts), 3):
        for a in range(3):
            q = int(round((verts[i + a] - lo[a]) / scale)) - 32767
            buf += struct.pack("<h", max(-32767, min(32767, q)))
    return base64.b64encode(bytes(buf)).decode("ascii"), lo, scale, hi


# ------------------------------------------------------------------- the page

HTML = r"""<title>__TITLE__</title>
<style>
  :root{--bg:#17161a;--ink:#f0ebe2;--dim:#a49c8e;--accent:#E0913F;--panel:#201f24;}
  @media (prefers-color-scheme:light){:root{--bg:#eeece7;--ink:#22201d;--dim:#6b655c;--panel:#dedbd4;}}
  :root[data-theme=dark]{--bg:#17161a;--ink:#f0ebe2;--dim:#a49c8e;--panel:#201f24;}
  :root[data-theme=light]{--bg:#eeece7;--ink:#22201d;--dim:#6b655c;--panel:#dedbd4;}
  html,body{height:100%;margin:0;background:var(--bg);color:var(--ink);
    font:14px/1.45 ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
    overflow:hidden;}
  canvas{display:block;width:100vw;height:100vh;cursor:grab;touch-action:none;}
  canvas.drag{cursor:grabbing;}
  #hud{position:fixed;left:14px;top:12px;pointer-events:none;max-width:min(46ch,60vw);}
  #hud h1{margin:0;font-size:15px;font-weight:650;letter-spacing:.01em;}
  #hud p{margin:3px 0 0;font-size:12.5px;color:var(--dim);
    font-family:ui-monospace,SFMono-Regular,Menlo,monospace;}
  #panel{position:fixed;right:14px;top:12px;background:var(--panel);
    border-radius:9px;padding:9px 11px;font-size:12.5px;max-height:80vh;overflow-y:auto;}
  #panel label{display:flex;align-items:center;gap:7px;padding:2px 0;cursor:pointer;
    white-space:nowrap;}
  #panel .sw{width:11px;height:11px;border-radius:2.5px;flex:none;}
  #panel hr{border:0;border-top:1px solid var(--dim);opacity:.3;margin:8px 0;}
  #panel button{font:inherit;background:none;border:1px solid var(--dim);
    color:var(--ink);border-radius:5px;padding:3px 9px;cursor:pointer;width:100%;}
  #panel button:hover{border-color:var(--accent);color:var(--accent);}
  #keys{position:fixed;left:14px;bottom:11px;font-size:12px;color:var(--dim);
    pointer-events:none;}
  kbd{font:inherit;color:var(--ink);}
  /* Notes ride WITH the geometry. A render and its numbers separated into two
     files drift apart; kept in one page they cannot. */
  #notes{position:fixed;left:14px;top:58px;background:var(--panel);
    border-radius:9px;padding:13px 16px;font-size:12.5px;
    max-width:min(58ch,42vw);max-height:calc(100vh - 104px);overflow-y:auto;}
  #notes.hide{display:none;}
  #notes h2{margin:14px 0 5px;font-size:12px;letter-spacing:.06em;
    text-transform:uppercase;color:var(--accent);font-weight:650;}
  #notes h2:first-child{margin-top:0;}
  #notes p{margin:4px 0;color:var(--dim);}
  #notes b{color:var(--ink);font-weight:600;}
  #notes table{border-collapse:collapse;width:100%;
    font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:11.5px;}
  #notes td,#notes th{padding:1.5px 0;text-align:left;white-space:nowrap;}
  #notes th{color:var(--dim);font-weight:500;border-bottom:1px solid var(--dim);}
  #notes td.n,#notes th.n{text-align:right;padding-left:12px;}
  #notes tr.tot td{border-top:1px solid var(--dim);color:var(--accent);
    font-weight:650;padding-top:3px;}
  #notes ul{margin:4px 0;padding-left:16px;color:var(--dim);}
  #notes li{margin:2px 0;}
  #notes .ok{color:#7fb069;} #notes .warn{color:var(--accent);}
__POSECSS__</style>
<canvas id=c></canvas>
<div id=hud><h1>__TITLE__</h1><p id=sub></p></div>
<div id=panel></div>
<div id=notes>__NOTES__</div>
<div id=keys><kbd>drag</kbd> orbit &nbsp;·&nbsp; <kbd>shift+drag</kbd> pan
  &nbsp;·&nbsp; <kbd>scroll</kbd> zoom &nbsp;·&nbsp; <kbd>W</kbd> wireframe
  &nbsp;·&nbsp; <kbd>R</kbd> reset &nbsp;·&nbsp; <kbd>N</kbd> notes</div>
<script>
const PARTS = __PARTS__;__POSEBOOT__

// ---- decode -----------------------------------------------------------
function decode(p){
  const bin = atob(p.b64), n = bin.length/2;
  const q = new Int16Array(n);
  for(let i=0;i<n;i++) q[i] = (bin.charCodeAt(2*i) | (bin.charCodeAt(2*i+1)<<8)) << 16 >> 16;
  const pos = new Float32Array(n);
  for(let i=0;i<n;i+=3){
    pos[i]   = p.origin[0] + (q[i]  +32767)*p.scale;
    pos[i+1] = p.origin[1] + (q[i+1]+32767)*p.scale;
    pos[i+2] = p.origin[2] + (q[i+2]+32767)*p.scale;
  }
  // flat face normals from the cross product -- never trust STL's stored ones
  const nor = new Float32Array(n);
  for(let t=0;t<n;t+=9){
    const ax=pos[t+3]-pos[t], ay=pos[t+4]-pos[t+1], az=pos[t+5]-pos[t+2];
    const bx=pos[t+6]-pos[t], by=pos[t+7]-pos[t+1], bz=pos[t+8]-pos[t+2];
    let nx=ay*bz-az*by, ny=az*bx-ax*bz, nz=ax*by-ay*bx;
    const L=Math.hypot(nx,ny,nz)||1; nx/=L; ny/=L; nz/=L;
    for(let k=0;k<9;k+=3){ nor[t+k]=nx; nor[t+k+1]=ny; nor[t+k+2]=nz; }
  }
  return {pos,nor,tris:n/9};
}

// ---- gl ---------------------------------------------------------------
const cv = document.getElementById('c');
const gl = cv.getContext('webgl',{antialias:true,alpha:false});
if(!gl){ document.body.innerHTML='<p style="padding:2rem">WebGL unavailable.</p>'; }

const VS=`attribute vec3 aP,aN;uniform mat4 uMVP,uM;varying vec3 vN,vP;
void main(){vN=mat3(uM)*aN;vP=(uM*vec4(aP,1.)).xyz;gl_Position=uMVP*vec4(aP,1.);}`;
const FS=`precision highp float;varying vec3 vN,vP;uniform vec3 uC,uEye;uniform float uFlat;
void main(){
  vec3 N=normalize(vN), V=normalize(uEye-vP);
  if(!gl_FrontFacing) N=-N;
  float key=max(dot(N,normalize(vec3(.45,.65,.75))),0.);
  float fil=max(dot(N,normalize(vec3(-.6,-.2,.35))),0.)*.28;
  float rim=pow(1.-max(dot(N,V),0.),2.6)*.42;
  vec3 col=uC*(.20+key*.86+fil)+vec3(.95,.82,.62)*rim;
  float spec=pow(max(dot(reflect(-normalize(vec3(.45,.65,.75)),N),V),0.),34.)*.30;
  col+=vec3(spec);
  gl_FragColor=vec4(mix(col,uC,uFlat),1.);
}`;
function sh(t,s){const o=gl.createShader(t);gl.shaderSource(o,s);gl.compileShader(o);
  if(!gl.getShaderParameter(o,gl.COMPILE_STATUS))throw gl.getShaderInfoLog(o);return o;}
const prog=gl.createProgram();
gl.attachShader(prog,sh(gl.VERTEX_SHADER,VS));
gl.attachShader(prog,sh(gl.FRAGMENT_SHADER,FS));
gl.bindAttribLocation(prog,0,'aP');gl.bindAttribLocation(prog,1,'aN');
gl.linkProgram(prog);gl.useProgram(prog);
const U={};for(const k of ['uMVP','uM','uC','uEye','uFlat'])U[k]=gl.getUniformLocation(prog,k);

// ---- upload -----------------------------------------------------------
let lo=[1e9,1e9,1e9], hi=[-1e9,-1e9,-1e9];
const objs = PARTS.map(p=>{
  const m=decode(p);
  const bp=gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER,bp);
  gl.bufferData(gl.ARRAY_BUFFER,m.pos,gl.STATIC_DRAW);
  const bn=gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER,bn);
  gl.bufferData(gl.ARRAY_BUFFER,m.nor,gl.STATIC_DRAW);
  for(let a=0;a<3;a++){ lo[a]=Math.min(lo[a],p.origin[a]); hi[a]=Math.max(hi[a],p.hi[a]); }
  return {...p, bp, bn, count:m.pos.length/3, tris:m.tris, on:p.on!==false};
});
const ctr=[0,1,2].map(a=>(lo[a]+hi[a])/2);
const span=Math.max(...[0,1,2].map(a=>hi[a]-lo[a]))||1;

// ---- matrices ---------------------------------------------------------
const mul=(a,b)=>{const o=new Float32Array(16);
  for(let i=0;i<4;i++)for(let j=0;j<4;j++){let s=0;
    for(let k=0;k<4;k++)s+=a[k*4+j]*b[i*4+k];o[i*4+j]=s;}return o;};
function persp(fov,ar,n,f){const t=1/Math.tan(fov/2);return new Float32Array(
  [t/ar,0,0,0, 0,t,0,0, 0,0,(f+n)/(n-f),-1, 0,0,2*f*n/(n-f),0]);}
function look(e,c,up){
  let z=[e[0]-c[0],e[1]-c[1],e[2]-c[2]];let L=Math.hypot(...z);z=z.map(v=>v/L);
  let x=[up[1]*z[2]-up[2]*z[1],up[2]*z[0]-up[0]*z[2],up[0]*z[1]-up[1]*z[0]];
  L=Math.hypot(...x)||1;x=x.map(v=>v/L);
  const y=[z[1]*x[2]-z[2]*x[1],z[2]*x[0]-z[0]*x[2],z[0]*x[1]-z[1]*x[0]];
  return new Float32Array([x[0],y[0],z[0],0, x[1],y[1],z[1],0, x[2],y[2],z[2],0,
    -(x[0]*e[0]+x[1]*e[1]+x[2]*e[2]), -(y[0]*e[0]+y[1]*e[1]+y[2]*e[2]),
    -(z[0]*e[0]+z[1]*e[1]+z[2]*e[2]), 1]);}

// ---- camera / interaction --------------------------------------------
const HOME={th:-0.85,ph:1.15,d:span*2.3,px:0,py:0};
let cam={...HOME}, wire=false;
function reset(){cam={...HOME};draw();}

let drag=null;
cv.addEventListener('pointerdown',e=>{drag={x:e.clientX,y:e.clientY,pan:e.shiftKey||e.button===2};
  cv.setPointerCapture(e.pointerId);cv.classList.add('drag');});
cv.addEventListener('pointerup',e=>{drag=null;cv.classList.remove('drag');});
cv.addEventListener('pointermove',e=>{
  if(!drag)return;
  const dx=e.clientX-drag.x, dy=e.clientY-drag.y;
  drag.x=e.clientX; drag.y=e.clientY;
  if(drag.pan){ cam.px-=dx*cam.d/900; cam.py+=dy*cam.d/900; }
  else{ cam.th-=dx*0.009; cam.ph=Math.max(0.02,Math.min(Math.PI-0.02,cam.ph-dy*0.009)); }
  draw();});
cv.addEventListener('contextmenu',e=>e.preventDefault());
cv.addEventListener('wheel',e=>{e.preventDefault();
  cam.d=Math.max(span*0.25,Math.min(span*14,cam.d*Math.exp(e.deltaY*0.0011)));draw();},
  {passive:false});
addEventListener('keydown',e=>{
  const k=e.key.toLowerCase();
  if(k==='r')reset(); else if(k==='w'){wire=!wire;draw();}
  else if(k==='n'){const n=document.getElementById('notes');
    if(n)n.classList.toggle('hide');}});
{const n=document.getElementById('notes');
 if(n&&!n.innerHTML.trim())n.classList.add('hide');}

// ---- panel ------------------------------------------------------------
const panel=document.getElementById('panel');
if(objs.length>1){
  objs.forEach((o,i)=>{
    const l=document.createElement('label');
    l.innerHTML=`<input type=checkbox ${o.on?'checked':''}><span class=sw style="background:rgb(${
      o.color.map(v=>Math.round(v*255)).join(',')})"></span>${o.name}`;
    l.querySelector('input').onchange=e=>{o.on=e.target.checked;draw();};
    panel.appendChild(l);});
  panel.appendChild(document.createElement('hr'));
}
const rb=document.createElement('button');rb.textContent='reset view';rb.onclick=reset;
panel.appendChild(rb);

document.getElementById('sub').textContent =
  `${(hi[0]-lo[0]).toFixed(1)} x ${(hi[1]-lo[1]).toFixed(1)} x ${(hi[2]-lo[2]).toFixed(1)} mm` +
  `   ·   ${objs.reduce((s,o)=>s+o.tris,0).toLocaleString()} tri` +
  (objs.length>1?`   ·   ${objs.length} parts`:'');

// ---- draw -------------------------------------------------------------
function draw(){
  const dpr=Math.min(devicePixelRatio||1,2);
  const w=Math.round(innerWidth*dpr), h=Math.round(innerHeight*dpr);
  if(cv.width!==w||cv.height!==h){cv.width=w;cv.height=h;}
  gl.viewport(0,0,w,h);
  const bg=getComputedStyle(document.documentElement).getPropertyValue('--bg').trim();
  const m=/^#(\w\w)(\w\w)(\w\w)$/.exec(bg);
  gl.clearColor(...(m?[1,2,3].map(i=>parseInt(m[i],16)/255):[0.09,0.086,0.10]),1);
  gl.enable(gl.DEPTH_TEST); gl.enable(gl.CULL_FACE); gl.cullFace(gl.BACK);
  gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);

  const sp=Math.sin(cam.ph), eye=[
    ctr[0]+cam.px + cam.d*sp*Math.cos(cam.th),
    ctr[1]      + cam.d*sp*Math.sin(cam.th),
    ctr[2]+cam.py + cam.d*Math.cos(cam.ph)];
  const tgt=[ctr[0]+cam.px, ctr[1], ctr[2]+cam.py];
  const V=look(eye,tgt,[0,0,1]);
  const P=persp(0.62,w/h,span*0.02,span*40);
  const MVP=mul(P,V);
  const I=new Float32Array([1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]);
  gl.uniformMatrix4fv(U.uMVP,false,MVP);
  gl.uniformMatrix4fv(U.uM,false,I);
  gl.uniform3fv(U.uEye,new Float32Array(eye));
  gl.uniform1f(U.uFlat,0);
  gl.enableVertexAttribArray(0); gl.enableVertexAttribArray(1);

  for(const o of objs){
    if(!o.on) continue;
__POSELOOP__    gl.uniform3fv(U.uC,new Float32Array(o.color));
    gl.bindBuffer(gl.ARRAY_BUFFER,o.bp); gl.vertexAttribPointer(0,3,gl.FLOAT,false,0,0);
    gl.bindBuffer(gl.ARRAY_BUFFER,o.bn); gl.vertexAttribPointer(1,3,gl.FLOAT,false,0,0);
    gl.drawArrays(wire?gl.LINES:gl.TRIANGLES,0,o.count);
  }
}
addEventListener('resize',draw);
matchMedia('(prefers-color-scheme:dark)').addEventListener('change',draw);
new MutationObserver(draw).observe(document.documentElement,{attributes:true,
  attributeFilter:['data-theme']});
__POSEUI__draw();
</script>
"""

PALETTE = [
    (0.62, 0.66, 0.72), (0.88, 0.57, 0.25), (0.45, 0.68, 0.60),
    (0.72, 0.52, 0.66), (0.55, 0.62, 0.80), (0.80, 0.72, 0.42),
    (0.52, 0.74, 0.78), (0.85, 0.45, 0.42), (0.60, 0.75, 0.45),
    (0.70, 0.63, 0.55),
]

# ------------------------------------------------- pose injection (manifest)
# Everything below is spliced into the page ONLY when a manifest is given.
# The four __POSE*__ placeholders collapse to "" otherwise, which is what
# keeps the plain page byte-for-byte identical to what this tool has always
# emitted (telescopebot and friends share it).

POSE_CSS = r"""  /* pose panel -- present only on manifest-built pages */
  #pose{position:fixed;right:14px;bottom:11px;background:var(--panel);
    border-radius:9px;padding:9px 11px;font-size:12.5px;width:30ch;
    max-height:60vh;overflow-y:auto;}
  #pose .pgh{display:flex;justify-content:space-between;gap:10px;}
  #pose .pv{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;
    color:var(--accent);}
  #pose input[type=range]{width:100%;margin:2px 0 1px;}
  #pose .pd{display:flex;gap:5px;margin:1px 0 9px;flex-wrap:wrap;}
  #pose button{font:inherit;font-size:11.5px;background:none;
    border:1px solid var(--dim);color:var(--ink);border-radius:5px;
    padding:1px 7px;cursor:pointer;}
  #pose button:hover{border-color:var(--accent);color:var(--accent);}
  #pose select{font:inherit;background:var(--bg);color:var(--ink);
    border:1px solid var(--dim);border-radius:5px;max-width:20ch;}
  #pose .hint{color:var(--dim);font-size:11.5px;margin:3px 0 6px;}
  #pose #fmreset{margin-top:2px;width:100%;}
"""

POSE_BOOT = r"""
const MANIFEST = __MANIFEST__;
// live pose: group -> slider value. Starts at the value the STLs were BUILT
// with, so the page opens showing exactly the as-built assembly (zero offset).
const POSE = {}; for(const g in MANIFEST.groups) POSE[g]=MANIFEST.groups[g].value;"""

POSE_LOOP = r"""    // kinematic pose: this part rides its motion groups (+ any free drag)
    const T=poseMatrix(o);
    gl.uniformMatrix4fv(U.uMVP,false,mul(MVP,T));
    gl.uniformMatrix4fv(U.uM,false,T);
"""

POSE_UI = r"""
// ---- pose panel (manifest mode only; injected by stl_viewer) -----------
// A part's offset = sum over its groups of (slider - group.value) * axis,
// composing across groups -- e.g. the chest box rides waist AND chest.
// group.value is the pose the STLs were BUILT in, so zero offset = truth.
function poseMatrix(o){
  const off=[0,0,0];
  for(const gn of (MANIFEST.parts[o.key]||[])){
    const g=MANIFEST.groups[gn]; if(!g) continue;
    const d=POSE[gn]-g.value;
    for(let a=0;a<3;a++) off[a]+=d*g.axis[a];
  }
  if(o.freeOff) for(let a=0;a<3;a++) off[a]+=o.freeOff[a];
  return new Float32Array([1,0,0,0, 0,1,0,0, 0,0,1,0,
    off[0],off[1],off[2],1]);
}
const pose=document.createElement('div'); pose.id='pose';
document.body.appendChild(pose);
for(const gn in MANIFEST.groups){
  const g=MANIFEST.groups[gn];
  const head=document.createElement('div'); head.className='pgh';
  const lab=document.createElement('span'); lab.textContent=g.label||gn;
  const val=document.createElement('span'); val.className='pv';
  head.appendChild(lab); head.appendChild(val); pose.appendChild(head);
  const s=document.createElement('input');
  s.type='range'; s.min=g.min; s.max=g.max; s.step='any'; s.value=g.value;
  s.setAttribute('list','dl_'+gn); s.dataset.g=gn;
  // tick marks: every detent plus the as-built value, so "where it was
  // drawn" stays visible while the slider wanders
  const dl=document.createElement('datalist'); dl.id='dl_'+gn;
  const ticks=Object.assign({},g.detents||{}); ticks['BUILT']=g.value;
  for(const t in ticks){const op=document.createElement('option');
    op.value=ticks[t]; op.label=t; dl.appendChild(op);}
  const show=v=>{val.textContent=(+v).toFixed(1)+' mm'
    +(Math.abs(v-g.value)<1e-9?' (as built)':'');};
  const set=v=>{v=Math.max(g.min,Math.min(g.max,+v));
    s.value=v; POSE[gn]=v; show(v); draw();};
  s.addEventListener('input',()=>set(s.value)); show(g.value);
  pose.appendChild(s); pose.appendChild(dl);
  const dd=document.createElement('div'); dd.className='pd';
  for(const dn in (g.detents||{})){
    const b=document.createElement('button'); b.textContent=dn;
    b.onclick=()=>set(g.detents[dn]); dd.appendChild(b);}
  const hb=document.createElement('button'); hb.textContent='as built';
  hb.onclick=()=>set(g.value); dd.appendChild(hb);
  pose.appendChild(dd);
}
// ---- free move: pick a part, ctrl+drag (or hold M) slides it in the
// camera plane. A visual what-if only -- "reset pose" restores truth.
let fmPart=null,fmDrag=null,fmKey=false;
{
  const row=document.createElement('div');
  row.appendChild(document.createTextNode('free move: '));
  const sel=document.createElement('select');
  const n0=document.createElement('option');
  n0.value=-1; n0.textContent='(none)'; sel.appendChild(n0);
  objs.forEach((o,i)=>{const op=document.createElement('option');
    op.value=i; op.textContent=o.name; sel.appendChild(op);});
  sel.onchange=()=>{fmPart=sel.value<0?null:objs[sel.value];};
  row.appendChild(sel); pose.appendChild(row);
  const hint=document.createElement('div'); hint.className='hint';
  hint.textContent='ctrl+drag (or hold M) slides the picked part';
  pose.appendChild(hint);
  const rs=document.createElement('button'); rs.id='fmreset';
  rs.textContent='reset pose';
  rs.onclick=()=>{
    document.querySelectorAll('#pose input[type=range]').forEach(i=>{
      i.value=MANIFEST.groups[i.dataset.g].value;
      i.dispatchEvent(new Event('input'));});
    for(const o of objs) o.freeOff=null;
    draw();};
  pose.appendChild(rs);
}
addEventListener('keydown',e=>{if(e.key.toLowerCase()==='m')fmKey=true;});
addEventListener('keyup',e=>{if(e.key.toLowerCase()==='m')fmKey=false;});
// Registered AFTER the orbit handler, so nulling `drag` here vetoes the
// orbit that handler just started -- the same gesture becomes a part move.
cv.addEventListener('pointerdown',e=>{
  if(fmPart&&(e.ctrlKey||fmKey)){drag=null;fmDrag={x:e.clientX,y:e.clientY};}});
cv.addEventListener('pointermove',e=>{
  if(!fmDrag||!fmPart)return;
  const dx=e.clientX-fmDrag.x,dy=e.clientY-fmDrag.y;
  fmDrag.x=e.clientX;fmDrag.y=e.clientY;
  // world mm per CSS px at the orbit target's depth (fov 0.62, see persp)
  const k=2*cam.d*Math.tan(0.31)/innerHeight;
  const sp=Math.sin(cam.ph),
    z=[sp*Math.cos(cam.th),sp*Math.sin(cam.th),Math.cos(cam.ph)],
    R=[-Math.sin(cam.th),Math.cos(cam.th),0],
    up=[z[1]*R[2]-z[2]*R[1],z[2]*R[0]-z[0]*R[2],z[0]*R[1]-z[1]*R[0]];
  if(!fmPart.freeOff)fmPart.freeOff=[0,0,0];
  for(let a=0;a<3;a++)fmPart.freeOff[a]+=R[a]*dx*k-up[a]*dy*k;
  draw();});
addEventListener('pointerup',()=>{fmDrag=null;});
"""


def load_manifest(path):
    """Parse and validate a motion-group manifest.

    Shape (the marks.py contract -- both lanes build to exactly this):
      {"groups": {"waist": {"label": str, "axis": [x,y,z], "min": f, "max": f,
                            "value": f, "detents": {"WALK": f, ...}}, ...},
       "parts":  {"<stl basename without .stl>": ["waist", ...] | [], ...}}
    Hard-fails on structural problems; soft mismatches (a part the page emits
    that the manifest does not name) only warn in build(), because a stale
    manifest should degrade to "that part stays put", not to no page.
    """
    with open(path) as f:
        m = json.load(f)
    if not isinstance(m.get("groups"), dict) or not isinstance(m.get("parts"), dict):
        raise ValueError(f"{path}: manifest needs 'groups' and 'parts' objects")
    for name, g in m["groups"].items():
        ax = g.get("axis")
        if (not isinstance(ax, list) or len(ax) != 3
                or not all(isinstance(v, (int, float)) for v in ax)):
            raise ValueError(f"{path}: group '{name}' axis must be [x,y,z]")
        for k in ("min", "max", "value"):
            if not isinstance(g.get(k), (int, float)):
                raise ValueError(f"{path}: group '{name}' needs numeric '{k}'")
        if g["min"] > g["max"]:
            raise ValueError(f"{path}: group '{name}' has min > max")
        if not g["min"] <= g["value"] <= g["max"]:
            print(f"  WARNING: group '{name}' value {g['value']} outside "
                  f"[{g['min']}, {g['max']}] -- slider will clamp")
    for pname, gs in m["parts"].items():
        if not isinstance(gs, list):
            raise ValueError(f"{path}: parts['{pname}'] must be a list")
    return m


def label_of(path):
    """(display name, default-visible).

    A leading '_' means "show it in the list but start it hidden" -- that is how
    superseded or reference geometry appears without implying it is current.
    A leading 'NN_' orders the panel and is stripped for display.
    """
    n = os.path.splitext(os.path.basename(path))[0]
    on = not n.startswith("_")
    n = n.lstrip("_")
    if len(n) > 3 and n[:2].isdigit() and n[2] in "_-":
        n = n[3:]
    return n.replace("_", " "), on


def build(paths, out, title=None, notes="", manifest=None):
    """Emit the page. `manifest` is a load_manifest() dict or None.

    In manifest mode each part additionally carries `key` -- the RAW stl
    basename, NOT the prettied label_of() name -- because that is what the
    manifest's "parts" table is keyed by (the underscore-stripping display
    transform must never leak into the contract).
    """
    parts = []
    moving = 0
    for i, p in enumerate(paths):
        verts = read_stl(p)
        b64, origin, scale, hi = quantise(verts)
        name, on = label_of(p)
        key = os.path.splitext(os.path.basename(p))[0]
        keyfield = ""
        if manifest is not None:
            keyfield = ",key:%s" % json.dumps(key)
            groups = manifest["parts"].get(key)
            if groups is None:
                print(f"  WARNING: {key} not in manifest parts -- "
                      "treated as chassis-fixed")
            elif groups:
                moving += 1
        parts.append(
            '{name:"%s",on:%s,b64:"%s",origin:[%.6f,%.6f,%.6f],scale:%.9f,'
            'hi:[%.6f,%.6f,%.6f],color:[%.3f,%.3f,%.3f]%s}'
            % (name, "true" if on else "false", b64, *origin, scale, *hi,
               *PALETTE[i % len(PALETTE)], keyfield)
        )
        print(f"  {name:34s} {len(verts) // 9:>7,} tri"
              f"{'' if on else '   (hidden by default)'}")

    tl = title or (os.path.splitext(os.path.basename(paths[0]))[0]
                   if len(paths) == 1 else "assembly")
    # Pose placeholders are resolved FIRST so nothing a user puts in notes
    # (or a part name) can collide with them afterwards.
    if manifest is None:
        html = (HTML.replace("__POSECSS__", "").replace("__POSEBOOT__", "")
                    .replace("__POSELOOP__", "").replace("__POSEUI__", ""))
    else:
        for pname, gs in manifest["parts"].items():
            for g in gs:
                if g not in manifest["groups"]:
                    print(f"  WARNING: manifest part {pname} names unknown "
                          f"group '{g}'")
        # </ must not appear inside a <script> block, JSON or not
        mjson = (json.dumps(manifest, separators=(",", ":"))
                 .replace("</", "<\\/"))
        html = (HTML.replace("__POSECSS__", POSE_CSS)
                    .replace("__POSEBOOT__",
                             POSE_BOOT.replace("__MANIFEST__", mjson))
                    .replace("__POSELOOP__", POSE_LOOP)
                    .replace("__POSEUI__", POSE_UI))
        print(f"  pose panel: {len(manifest['groups'])} groups, "
              f"{moving} moving parts")
    html = (html.replace("__PARTS__", "[" + ",".join(parts) + "]")
                .replace("__NOTES__", notes)
                .replace("__TITLE__", tl))
    with open(out, "w") as f:
        f.write(html)
    print(f"\n  -> {out}  ({os.path.getsize(out) / 1e6:.2f} MB, opens in any browser)")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("-o", "--out", default=None)
    ap.add_argument("-t", "--title", default=None)
    ap.add_argument("-n", "--notes", default=None,
                    help="HTML fragment file shown in the notes panel (key N)")
    ap.add_argument("-m", "--manifest", default=None,
                    help="motion-group manifest JSON; when omitted, "
                         "<out minus .html>_manifest.json is auto-detected")
    ap.add_argument("--no-manifest", action="store_true",
                    help="force the plain static page even if a manifest "
                         "file sits beside -o")
    a = ap.parse_args()
    out = a.out or os.path.splitext(a.paths[0])[0] + "_view.html"
    nt = open(a.notes).read() if a.notes else ""
    manifest = None
    if not a.no_manifest:
        mpath = a.manifest
        if mpath is None and out.endswith(".html"):
            # The marks.py contract: a manifest written alongside the page,
            # named after it, lights the pose panel with no extra flag.
            cand = out[:-len(".html")] + "_manifest.json"
            if os.path.exists(cand):
                mpath = cand
                print(f"  pose manifest auto-detected: {cand}")
        if mpath:
            manifest = load_manifest(mpath)
    sys.exit(0 if build(a.paths, out, a.title, nt, manifest) else 1)
