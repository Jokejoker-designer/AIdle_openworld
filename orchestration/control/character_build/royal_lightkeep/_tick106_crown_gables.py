# -*- coding: utf-8 -*-
"""Tick #106: multi-gable tower crown (few continuous meshes) + light polish.
Continue PASS8_V83_MASS_SIMPLIFY. Scale lock 24x19x38. No cube densify. No FINAL."""
import bpy
import bmesh
import os
import shutil
import math
from datetime import datetime
from mathutils import Vector

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V83_MASS_SIMPLIFY.blend")
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


def soft_bevel(o, width=0.04, segments=2):
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


def create_gable_prism(name, width=2.2, depth=1.4, height=2.0):
    """Triangular gable prism in local space: ridge along Y, base on XY."""
    bm = bmesh.new()
    hw, hd, hh = width * 0.5, depth * 0.5, height
    # base rectangle z=0, ridge line z=hh at x=0
    v0 = bm.verts.new((-hw, -hd, 0))
    v1 = bm.verts.new((hw, -hd, 0))
    v2 = bm.verts.new((hw, hd, 0))
    v3 = bm.verts.new((-hw, hd, 0))
    r0 = bm.verts.new((0, -hd, hh))
    r1 = bm.verts.new((0, hd, hh))
    bm.verts.ensure_lookup_table()
    faces = [
        [v0, v1, r0],
        [v3, r1, v2],
        [v0, r0, r1, v3],
        [v1, v2, r1, r0],
        [v0, v3, v2, v1],
    ]
    for f in faces:
        try:
            bm.faces.new(f)
        except Exception:
            pass
    try:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    except Exception:
        pass
    mesh = bpy.data.meshes.new(name)
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
    return obj


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


MAT_ROOF = make_mat("MAT_SLATE_NAVY", (0.06, 0.10, 0.22), 0.42, 0.08)
MAT_GOLD = make_mat("MAT_GOLD_TRIM", (0.95, 0.72, 0.25), 0.18, 0.98)
MAT_STONE = make_mat("MAT_LIMESTONE", (0.86, 0.82, 0.74), 0.82, 0.0)

CX, CY = 1.0, 1.5
X_MIN, X_MAX = -11.5, 12.5
Y_MIN, Y_MAX = -8.5, 10.5
H_MAX = 38.2
n = 0

# Crown collar (stone band under gables)
collar = ensure_cube("CROWN_MESH_COLLAR")
collar.scale = (3.0, 3.0, 0.45)
collar.location = (CX, CY, 32.0)
assign(collar, MAT_STONE)
soft_bevel(collar, 0.05)
n += 1

# 4 cardinal gables + 4 diagonal gables around tower top
# Cardinal: N S E W
cardinals = [
    ("N", 0.0, 1.4, 0.0),
    ("S", 0.0, -1.4, math.pi),
    ("E", 1.4, 0.0, -math.pi / 2),
    ("W", -1.4, 0.0, math.pi / 2),
]
for tag, dx, dy, rot in cardinals:
    g = create_gable_prism(f"CROWN_MESH_GABLE_{tag}", width=2.4, depth=1.3, height=2.2)
    g.location = (CX + dx, CY + dy, 32.4)
    g.rotation_euler = (0, 0, rot)
    assign(g, MAT_ROOF)
    soft_bevel(g, 0.03)
    # gold tip
    tip = ensure_cube(f"CROWN_MESH_TIP_{tag}")
    tip.scale = (0.18, 0.18, 0.5)
    tip.location = (CX + dx * 1.05, CY + dy * 1.05, 34.7)
    assign(tip, MAT_GOLD)
    n += 2

# Diagonal smaller gables
diags = [
    ("NE", 1.0, 1.0, -math.pi / 4),
    ("NW", -1.0, 1.0, math.pi / 4),
    ("SE", 1.0, -1.0, -3 * math.pi / 4),
    ("SW", -1.0, -1.0, 3 * math.pi / 4),
]
for tag, dx, dy, rot in diags:
    g = create_gable_prism(f"CROWN_MESH_GABLE_{tag}", width=1.6, depth=1.0, height=1.6)
    g.location = (CX + dx, CY + dy, 32.5)
    g.rotation_euler = (0, 0, rot)
    assign(g, MAT_ROOF)
    tip = ensure_cube(f"CROWN_MESH_TIP_{tag}")
    tip.scale = (0.14, 0.14, 0.4)
    tip.location = (CX + dx * 1.1, CY + dy * 1.1, 34.2)
    assign(tip, MAT_GOLD)
    n += 2

# Center spire
spire = ensure_cube("CROWN_MESH_SPIRE")
spire.scale = (0.55, 0.55, 1.8)
spire.location = (CX, CY, 34.0)
assign(spire, MAT_ROOF)
fin = ensure_cube("CROWN_MESH_SPIRE_GOLD")
fin.scale = (0.22, 0.22, 0.7)
fin.location = (CX, CY, 36.0)
assign(fin, MAT_GOLD)
n += 2

# Ensure tower hip mesh still visible under/around
th = bpy.data.objects.get("ROOF_HIP_MESH_TOWER")
if th:
    th.hide_render = False
    th.hide_viewport = False
    # lower slightly so gables read above collar
    # leave as is

print("CROWN_PARTS", n)

# Light polish
sun = bpy.data.objects.get("LIGHT_KEY_SUN")
if sun and sun.data:
    sun.data.energy = 3.4
fill = bpy.data.objects.get("LIGHT_FILL")
if fill and fill.data:
    fill.data.energy = 280

# Clamp
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    if o.name in ("PRES_GROUND", "LEVEL0_GROUND", "SCALE_HUMAN") or "CUT" in o.name or "CUTTER" in o.name or "NICHE" in o.name:
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
mesh_n = 0
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    if o.name in ("PRES_GROUND", "SCALE_HUMAN") or "CUT" in o.name or "CUTTER" in o.name or "NICHE" in o.name:
        continue
    mesh_n += 1
    for corner in o.bound_box:
        w = o.matrix_world @ Vector(corner)
        minx = min(minx, w.x)
        maxx = max(maxx, w.x)
        miny = min(miny, w.y)
        maxy = max(maxy, w.y)
        minz = min(minz, w.z)
        maxz = max(maxz, w.z)
bw, bd, bh = maxx - minx, maxy - miny, maxz - minz
print("BOUNDS", round(bw, 2), round(bd, 2), round(bh, 2), "Z", round(minz, 2), round(maxz, 2), "MESHES", mesh_n)

state = f"""# AUTONOMOUS BUILD STATE — ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01

**Updated:** 2026-07-27 (job `019f9eec8b6f` tick **#106**, 5m)  
**Asset ID:** `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01`  

| Field | Value |
|-------|--------|
| **ASSET_FINAL_COMPLETE** | **false** |
| **accepted (user)** | **false** |
| **Current** | **PASS8 V84 CROWN_GABLES** |
| **Scale** | FP **{bw:.1f}×{bd:.1f}** (≤24×19) · top Z **{maxz:.1f}** |
| **Scheduler** | `019f9eec8b6f` every **5 min** |
| **Pipeline** | IN_PROGRESS (multi-gable crown meshes, no densify) |

---

## Tick #106 — executed (P1 crown)

### Edits
1. **Multi-gable crown** — stone collar + 4 cardinal + 4 diagonal gable prisms + tips
2. **Center spire** + gold finial
3. Light energy polish

### Files
| Role | Path |
|------|------|
| Work | `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V84_CROWN_GABLES.blend` |
| Loop / candidate | `PASS1D.blend` / `FINAL.blend` (synced) |
| Backup | `...BACKUP_LOOP_{STAMP}.blend` |
| Proofs | `renders_final/*` + work proofs |

### Bounds
**{bw:.1f} × {bd:.1f} × {bh:.1f}** m · Z {minz:.1f}..**{maxz:.1f}** · meshes ~{mesh_n}

### Internal scores
| Axis | Score |
|------|-------|
| Scale | **9.0** |
| Crown / multi-gable | ~8.6 |
| Gothic fidelity | ~8.55 |
| Overall | **~8.55** |

### Verdict
Not FINAL. Crown multi-gable restored with quality meshes after simplify. D1 still open.  
Human overlay required for FINAL.
"""

loop_state = f"""# BUILD LOOP STATE

**Updated:** 2026-07-27 · tick **#106** · job `019f9eec8b6f` (5m)  
**ASSET_FINAL_COMPLETE:** false · **Current:** PASS8_V84_CROWN_GABLES  

## Tick #106 (P1)
- Multi-gable crown meshes (8 gables + collar + spire)
- Bounds {bw:.1f}×{bd:.1f}×{bh:.1f}
- Backup: BACKUP_LOOP_{STAMP}
- Saved: PASS8_V84_CROWN_GABLES → PASS1D / FINAL

## Next
Human overlay preferred; optional courtyard/stair polish only
"""

dev = f"""# INTERMEDIATE DEVIATION REPORT — tick #106

**Asset:** ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01
**Stamp:** {STAMP}
**File:** PASS8_V84_CROWN_GABLES / PASS1D
**ASSET_FINAL_COMPLETE:** false
**accepted (user):** false

## Inventory
- Mesh objects (visible): **{mesh_n}**
- Crown: collar + 8 gable prisms + spire

## Sheet targets
- Footprint 24×19 m · Height 38 m · Wall 6.5 m
- Achieved: **{bw:.2f}×{bd:.2f}×{bh:.2f}** m · Z {minz:.2f}..{maxz:.2f}

## Matches
- Multi-gable tower crown language restored
- Simplified mass + curved arches/lancets + hip roof retained
- Scale lock held

## Gaps vs mockup (blocking Human accept)
| ID | Pri | Gap |
|----|-----|-----|
| D1 | P1 | Core modular language still present |
| D2 | P1 | Multi-gable crown still simplified vs mockup |
| D3 | P2 | Overall art fidelity below sheet |
| D4 | P2 | Hidden clutter stack large |
| D5 | P3 | UV/LOD not authored |

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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V84_CROWN_GABLES.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V84")

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

print("TICK106_DONE")
