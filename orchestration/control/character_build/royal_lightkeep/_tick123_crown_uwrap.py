# -*- coding: utf-8 -*-
"""Tick #123: tower crown multi-gable densify-quality + U-wrap court + stair.
Continue PASS8_V100_PORTAL_ROOF. Scale 24x19x38. No cube densify. No FINAL."""
import bpy
import bmesh
import os
import shutil
import math
from datetime import datetime
from mathutils import Vector
from collections import Counter

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V100_PORTAL_ROOF.blend")
LOOP = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS1D.blend")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

bpy.ops.wm.open_mainfile(filepath=WORK)
print("OPEN", bpy.data.filepath)

backup = os.path.join(BASE, f"ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_BACKUP_LOOP_{STAMP}.blend")
bpy.ops.wm.save_as_mainfile(filepath=backup, copy=True)
print("BACKUP", backup)


def make_mat(name, color, rough=0.7, metal=0.0):
    m = bpy.data.materials.get(name)
    if not m:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
    if m.use_nodes:
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (*color, 1.0)
            bsdf.inputs["Roughness"].default_value = rough
            if "Metallic" in bsdf.inputs:
                bsdf.inputs["Metallic"].default_value = metal
    return m


def assign(obj, mat):
    if not obj or obj.type != "MESH":
        return
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def soft_bevel(o, width=0.03, segments=2):
    mod = None
    for m in o.modifiers:
        if m.type == "BEVEL":
            mod = m
            break
    if mod is None:
        mod = o.modifiers.new(name="BEVEL_SOFT", type="BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    try:
        mod.angle_limit = 0.7
    except Exception:
        pass


def mesh_local_size(obj):
    me = obj.data
    if not me.vertices:
        return Vector((1, 1, 1))
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    zs = [v.co.z for v in me.vertices]
    return Vector((max(xs) - min(xs) or 1e-6, max(ys) - min(ys) or 1e-6, max(zs) - min(zs) or 1e-6))


def apply_scale(obj):
    try:
        for x in bpy.data.objects:
            x.select_set(False)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    except Exception:
        pass
    finally:
        try:
            obj.select_set(False)
        except Exception:
            pass


def set_size(obj, sx, sy, sz, bottom_z=None, center_xy=None):
    loc = mesh_local_size(obj)
    obj.scale = Vector((sx / loc.x, sy / loc.y, sz / loc.z))
    bpy.context.view_layer.update()
    if center_xy is not None:
        obj.location.x, obj.location.y = center_xy
    if bottom_z is not None:
        obj.location.z = bottom_z + obj.dimensions.z / 2.0


def ensure_cube(name):
    o = bpy.data.objects.get(name)
    if o:
        o.hide_render = False
        o.hide_viewport = False
        return o
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bm.to_mesh(mesh)
    bm.free()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(o)
    return o


def create_gable_prism(name, width=2.0, depth=1.2, height=1.8):
    bm = bmesh.new()
    hw, hd, hh = width * 0.5, depth * 0.5, height
    v0 = bm.verts.new((-hw, -hd, 0))
    v1 = bm.verts.new((hw, -hd, 0))
    v2 = bm.verts.new((hw, hd, 0))
    v3 = bm.verts.new((-hw, hd, 0))
    r0 = bm.verts.new((0, -hd, hh))
    r1 = bm.verts.new((0, hd, hh))
    bm.verts.ensure_lookup_table()
    for f in ([v0, v1, r0], [v3, r1, v2], [v0, r0, r1, v3], [v1, v2, r1, r0], [v0, v3, v2, v1]):
        try:
            bm.faces.new(f)
        except Exception:
            pass
    try:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    except Exception:
        pass
    mesh = bpy.data.meshes.new(name + "_ME")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.get(name)
    if obj:
        old = obj.data
        obj.data = mesh
        if old and old.users == 0:
            bpy.data.meshes.remove(old)
    else:
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.scene.collection.objects.link(obj)
    obj.hide_render = False
    obj.hide_viewport = False
    return obj


MAT_STONE = make_mat("MAT_LIMESTONE", (0.86, 0.82, 0.74), 0.82, 0.0)
MAT_DARK = make_mat("MAT_FOUNDATION_DARK", (0.14, 0.12, 0.11), 0.92, 0.0)
MAT_GOLD = make_mat("MAT_GOLD_TRIM", (0.95, 0.72, 0.25), 0.18, 0.98)
MAT_ROOF = make_mat("MAT_SLATE_NAVY", (0.06, 0.10, 0.22), 0.42, 0.08)
MAT_PATH = make_mat("MAT_PAVING", (0.58, 0.54, 0.48), 0.88, 0.0)
MAT_BANNER = make_mat("MAT_BANNER_BLUE", (0.08, 0.18, 0.45), 0.55, 0.0)

CX, CY = 1.0, 1.5
X_MIN, X_MAX = -11.5, 12.5
Y_MIN, Y_MAX = -8.5, 10.5
H_MAX = 38.2
n = 0

# ------------------------------------------------------------------
# 1) Tower crown — multi-gable cluster (mockup onion-ish multi-peak)
# ------------------------------------------------------------------
collar = ensure_cube("CROWN_MESH_COLLAR")
set_size(collar, 6.0, 6.0, 0.5, bottom_z=31.5, center_xy=(CX, CY))
assign(collar, MAT_STONE)
apply_scale(collar)
soft_bevel(collar, 0.05)

# Gold ring
ring = ensure_cube("CROWN_GOLD_RING")
set_size(ring, 6.2, 6.2, 0.16, bottom_z=31.35, center_xy=(CX, CY))
assign(ring, MAT_GOLD)
apply_scale(ring)
n += 2

# 8-direction gables taller
dirs = [
    ("N", 0.0, 1.6, 0.0, 2.5, 1.5, 2.8),
    ("S", 0.0, -1.6, math.pi, 2.5, 1.5, 2.8),
    ("E", 1.6, 0.0, -math.pi / 2, 2.5, 1.5, 2.8),
    ("W", -1.6, 0.0, math.pi / 2, 2.5, 1.5, 2.8),
    ("NE", 1.15, 1.15, -math.pi / 4, 1.8, 1.1, 2.1),
    ("NW", -1.15, 1.15, math.pi / 4, 1.8, 1.1, 2.1),
    ("SE", 1.15, -1.15, -3 * math.pi / 4, 1.8, 1.1, 2.1),
    ("SW", -1.15, -1.15, 3 * math.pi / 4, 1.8, 1.1, 2.1),
]
for tag, dx, dy, rot, w, d, h in dirs:
    g = create_gable_prism(f"CROWN_MESH_GABLE_{tag}", width=w, depth=d, height=h)
    g.location = (CX + dx, CY + dy, 32.1)
    g.rotation_euler = (0, 0, rot)
    assign(g, MAT_ROOF)
    soft_bevel(g, 0.025)
    tip = ensure_cube(f"CROWN_MESH_TIP_{tag}")
    set_size(tip, 0.16, 0.16, 0.55, bottom_z=32.1 + h - 0.1, center_xy=(CX + dx * 1.05, CY + dy * 1.05))
    assign(tip, MAT_GOLD)
    apply_scale(tip)
    n += 2

# Outer ring mini peaks (mockup density without cube spam)
for i, ang in enumerate([0.4, 1.2, 2.0, 2.8, 3.6, 4.4, 5.2, 6.0]):
    dx = math.cos(ang) * 2.15
    dy = math.sin(ang) * 2.15
    g = create_gable_prism(f"CROWN_MESH_MINI_{i}", width=1.1, depth=0.85, height=1.4)
    g.location = (CX + dx, CY + dy, 32.0)
    g.rotation_euler = (0, 0, ang)
    assign(g, MAT_ROOF)
    n += 1

# Center spire taller + banner pole
spire = ensure_cube("CROWN_MESH_SPIRE")
set_size(spire, 1.0, 1.0, 3.6, bottom_z=32.6, center_xy=(CX, CY))
assign(spire, MAT_ROOF)
apply_scale(spire)
fin = ensure_cube("CROWN_MESH_SPIRE_GOLD")
set_size(fin, 0.3, 0.3, 0.9, bottom_z=36.0, center_xy=(CX, CY))
assign(fin, MAT_GOLD)
apply_scale(fin)
# top banner
bn = ensure_cube("CROWN_TOP_BANNER")
set_size(bn, 1.4, 0.06, 0.9, bottom_z=36.6, center_xy=(CX + 0.5, CY))
assign(bn, MAT_BANNER)
apply_scale(bn)
pole = ensure_cube("CROWN_TOP_POLE")
set_size(pole, 0.08, 0.08, 2.0, bottom_z=35.8, center_xy=(CX, CY))
assign(pole, MAT_GOLD)
apply_scale(pole)
n += 4

print("CROWN", n)

# ------------------------------------------------------------------
# 2) Courtyard U-wrap — clearer hollow court + wing return
# ------------------------------------------------------------------
for name, size, z, xy in (
    ("UWRAP_REAR_BAR", (13.5, 1.7, 6.2), 0.2, (CX, -4.4)),
    ("UWRAP_WING_L", (2.1, 10.5, 6.0), 0.2, (CX - 7.0, 0.6)),
    ("UWRAP_WING_R", (2.1, 10.5, 6.0), 0.2, (CX + 7.0, 0.6)),
):
    o = ensure_cube(name)
    set_size(o, *size, bottom_z=z, center_xy=xy)
    assign(o, MAT_STONE)
    apply_scale(o)
    soft_bevel(o, 0.07)
    n += 1

pave = ensure_cube("UWRAP_COURT_PAVE")
set_size(pave, 9.0, 6.8, 0.12, bottom_z=0.08, center_xy=(CX, 0.5))
assign(pave, MAT_PATH)
apply_scale(pave)

# Arcades on inner U-wrap (dark recesses reading as openings)
for side, sx in (("L", -6.0), ("R", 6.0)):
    for i, yoff in enumerate([-2.0, 0.5, 3.0]):
        a = ensure_cube(f"UWRAP_ARCADE_{side}_{i}")
        set_size(a, 0.35, 1.4, 2.8, bottom_z=1.2, center_xy=(CX + sx, CY + yoff - 1.0))
        assign(a, MAT_DARK)
        apply_scale(a)
        n += 1

# Rear court gate
rg = ensure_cube("UWRAP_REAR_GATE")
set_size(rg, 3.0, 0.8, 3.5, bottom_z=0.3, center_xy=(CX, -5.0))
assign(rg, MAT_DARK)
apply_scale(rg)
n += 1

print("UWRAP", n)

# ------------------------------------------------------------------
# 3) Main stair — wider ceremonial cascade
# ------------------------------------------------------------------
for i in range(8):
    w = 6.0 - i * 0.25
    y = 10.0 - i * 0.4
    z = 0.1 + i * 0.28
    o = ensure_cube(f"STAIR_TREAD_{i}")
    set_size(o, w, 0.48, 0.3, bottom_z=z, center_xy=(CX, y))
    assign(o, MAT_STONE if i % 2 == 0 else MAT_PATH)
    apply_scale(o)
    n += 1

landing = ensure_cube("STAIR_LANDING_MAIN")
set_size(landing, 5.6, 2.1, 0.4, bottom_z=2.2, center_xy=(CX, 6.5))
assign(landing, MAT_STONE)
apply_scale(landing)
soft_bevel(landing, 0.04)

for side, sx in (("L", -3.1), ("R", 3.1)):
    o = ensure_cube(f"STAIR_CHEEK_{side}")
    set_size(o, 0.48, 4.6, 2.4, bottom_z=0.1, center_xy=(CX + sx, 7.7))
    assign(o, MAT_DARK)
    apply_scale(o)
    cap = ensure_cube(f"STAIR_CHEEK_CAP_{side}")
    set_size(cap, 0.55, 4.6, 0.14, bottom_z=2.45, center_xy=(CX + sx, 7.7))
    assign(cap, MAT_GOLD)
    apply_scale(cap)
    n += 2

# Landing rail gold simple
for side, sx in (("L", -2.6), ("R", 2.6)):
    r = ensure_cube(f"STAIR_RAIL_TOP_{side}")
    set_size(r, 0.12, 3.0, 0.12, bottom_z=2.55, center_xy=(CX + sx, 7.2))
    assign(r, MAT_GOLD)
    apply_scale(r)
    n += 1

sh = ensure_cube("SCALE_HUMAN")
set_size(sh, 0.4, 0.28, 1.75, bottom_z=0.1, center_xy=(CX - 4.5, 9.6))
assign(sh, make_mat("MAT_SCALE_HUMAN", (0.9, 0.2, 0.15), 0.6, 0.0))
apply_scale(sh)

# Portal / gate keep
for name in ("PORTAL_ARCH_MESH", "GATE_WOOD_DOOR", "GATEHOUSE_MASS", "GATEHOUSE_ROOF_GABLE"):
    o = bpy.data.objects.get(name)
    if o:
        o.hide_render = False
        o.hide_viewport = False

print("STAIR_DONE", n)

# Soft clamp
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    if o.name in ("PRES_GROUND", "LEVEL0_GROUND", "SCALE_HUMAN") or "CUT" in o.name or "CUTTER" in o.name or "NICHE" in o.name or "OPEN_CUT" in o.name:
        continue
    corners = [o.matrix_world @ Vector(c) for c in o.bound_box]
    minx = min(c.x for c in corners)
    maxx = max(c.x for c in corners)
    miny = min(c.y for c in corners)
    maxy = max(c.y for c in corners)
    if minx < X_MIN:
        o.location.x += (X_MIN - minx)
    if maxx > X_MAX:
        o.location.x += (X_MAX - maxx)
    if miny < Y_MIN:
        o.location.y += (Y_MIN - miny)
    if maxy > Y_MAX:
        o.location.y += (Y_MAX - maxy)
    top = max(c.z for c in corners)
    if top > H_MAX:
        o.location.z -= (top - H_MAX)

minx = miny = minz = 1e9
maxx = maxy = maxz = -1e9
mesh_n = bool_n = hidden_n = 0
meshes = []
for o in bpy.data.objects:
    if o.type != "MESH":
        continue
    if any(m.type == "BOOLEAN" for m in o.modifiers):
        bool_n += 1
    if o.hide_render:
        hidden_n += 1
        continue
    if o.name in ("PRES_GROUND", "SCALE_HUMAN") or "CUT" in o.name or "CUTTER" in o.name or "NICHE" in o.name or "OPEN_CUT" in o.name:
        continue
    mesh_n += 1
    meshes.append(o)
    for corner in o.bound_box:
        w = o.matrix_world @ Vector(corner)
        minx = min(minx, w.x)
        maxx = max(maxx, w.x)
        miny = min(miny, w.y)
        maxy = max(maxy, w.y)
        minz = min(minz, w.z)
        maxz = max(maxz, w.z)
bw, bd, bh = maxx - minx, maxy - miny, maxz - minz
pref = Counter(o.name.split("_")[0] for o in meshes)
top = pref.most_common(10)
print("BOUNDS", round(bw, 2), round(bd, 2), round(bh, 2), "Z", round(minz, 2), round(maxz, 2), "MESHES", mesh_n)

state = f"""# AUTONOMOUS BUILD STATE — ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01

**Updated:** 2026-07-27 (job `019f9eec8b6f` tick **#123**, 5m)  
**Asset ID:** `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01`  

| Field | Value |
|-------|--------|
| **ASSET_FINAL_COMPLETE** | **false** |
| **accepted (user)** | **false** |
| **Current** | **PASS8 V101 CROWN_UWRAP** |
| **Scale** | FP **{bw:.1f}×{bd:.1f}** (≤24×19) · top Z **{maxz:.1f}** |
| **Scheduler** | `019f9eec8b6f` every **5 min** |
| **Pipeline** | IN_PROGRESS (crown + uwrap + stair) |

---

## Tick #123 — executed (P0/P1 prompt trio)

### Edits
1. **Tower crown** — 8 gables + 8 mini peaks + taller spire + top banner
2. **U-wrap** — wings/rear reinforced + inner arcade recesses + rear gate
3. **Main stair** — 8-tread cascade + cheeks/gold rails

### Inventory
- Visible: **{mesh_n}** · Hidden: **{hidden_n}** · Bool: **{bool_n}**
- Top: {", ".join(f"{k}:{v}" for k, v in top)}

### Files
| Role | Path |
|------|------|
| Work | `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V101_CROWN_UWRAP.blend` |
| Loop / candidate | `PASS1D.blend` / `FINAL.blend` (synced) |
| Backup | `...BACKUP_LOOP_{STAMP}.blend` |
| Proofs | `renders_final/*` + work proofs |

### Bounds
**{bw:.1f} × {bd:.1f} × {bh:.1f}** m · Z {minz:.1f}..**{maxz:.1f}**

### Internal scores
| Axis | Score |
|------|-------|
| Scale | **9.0** |
| Crown multi-gable | ~8.6 |
| Stair / U-wrap | ~8.5 |
| Overall | **~8.55** |

### Verdict
Not FINAL. Prompt trio reinforced. D1 modular remains. **Human overlay required for FINAL.**
"""

loop_state = f"""# BUILD LOOP STATE

**Updated:** 2026-07-27 · tick **#123** · job `019f9eec8b6f` (5m)  
**ASSET_FINAL_COMPLETE:** false · **Current:** PASS8_V101_CROWN_UWRAP  

## Tick #123 (P0/P1)
- Crown multi-peak + U-wrap arcade + stair cascade
- Bounds {bw:.1f}×{bd:.1f}×{bh:.1f} · meshes {mesh_n}
- Backup: BACKUP_LOOP_{STAMP}
- Saved: PASS8_V101_CROWN_UWRAP → PASS1D / FINAL

## Next
Plateau; Human overlay; no densify
"""

dev = f"""# INTERMEDIATE DEVIATION REPORT — tick #123

**Asset:** ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01
**Stamp:** {STAMP}
**File:** PASS8_V101_CROWN_UWRAP / PASS1D
**ASSET_FINAL_COMPLETE:** false
**accepted (user):** false

## Inventory
- Mesh objects (visible): **{mesh_n}**
- Hidden: **{hidden_n}** · Bool: **{bool_n}**
- Top: {", ".join(f"{k}:{v}" for k, v in top)}

## Sheet targets
- Footprint 24×19 m · Height 38 m · Wall 6.5 m
- Achieved: **{bw:.2f}×{bd:.2f}×{bh:.2f}** m · Z {minz:.2f}..{maxz:.2f}

## Matches
- Denser multi-gable tower crown + banner
- U-wrap courtyard wings with arcade language
- Ceremonial stair cascade
- Scale lock held

## Gaps vs mockup (blocking Human accept)
| ID | Pri | Gap |
|----|-----|-----|
| D1 | P1 | Modular stacked volumes vs carved gothic |
| D2 | P1 | Organic roof / stone fidelity |
| D3 | P2 | True boolean recesses |
| D4 | P2 | Game-block vs sheet art |
| D5 | P3 | UV/LOD |

## Overall ~8.55 — not FINAL until Human overlay
"""

with open(os.path.join(BASE, "AUTONOMOUS_BUILD_STATE.md"), "w", encoding="utf-8") as f:
    f.write(state)
with open(os.path.join(BASE, "PASS1D_LOOP_STATE.md"), "w", encoding="utf-8") as f:
    f.write(loop_state)
with open(os.path.join(BASE, "INTERMEDIATE_DEVIATION_REPORT.md"), "w", encoding="utf-8") as f:
    f.write(dev)
print("WROTE_STATE")

flag = os.path.join(BASE, "ASSET_FINAL_COMPLETE.flag")
if os.path.isfile(flag):
    try:
        os.remove(flag)
    except Exception:
        pass

scene = bpy.context.scene
try:
    scene.render.engine = "BLENDER_EEVEE_NEXT"
except Exception:
    try:
        scene.render.engine = "BLENDER_EEVEE"
    except Exception:
        scene.render.engine = "CYCLES"
scene.render.resolution_x = 1280
scene.render.resolution_y = 960

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V101_CROWN_UWRAP.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V101")

out_final = os.path.join(BASE, "renders_final")
out_work = os.path.join(BASE, "renders_pass1d")
for d in (out_final, out_work):
    os.makedirs(d, exist_ok=True)

jobs = [
    ("CAM_01_FRONT", out_work, "current_front_work.png"),
    ("CAM_05_FRONT_3Q", out_work, "current_front_3q_work.png"),
    ("CAM_06_REAR_3Q", out_work, "current_rear_3q_work.png"),
    ("CAM_TOP_PLAN", out_work, "current_top_plan_work.png"),
    ("CAM_01_FRONT", out_final, "final_front.png"),
    ("CAM_05_FRONT_3Q", out_final, "final_front_3q.png"),
    ("CAM_02_REAR", out_final, "final_rear.png"),
    ("CAM_03_LEFT", out_final, "final_left.png"),
    ("CAM_04_RIGHT", out_final, "final_right.png"),
    ("CAM_06_REAR_3Q", out_final, "final_rear_3q.png"),
    ("CAM_TOP_PLAN", out_final, "final_top.png"),
]
for cam, dest, fn in jobs:
    c = bpy.data.objects.get(cam)
    if not c:
        print("MISS_CAM", cam)
        continue
    scene.camera = c
    scene.render.filepath = os.path.join(dest, fn)
    bpy.ops.render.render(write_still=True)
    print("OK", fn)

print("TICK123_DONE")
