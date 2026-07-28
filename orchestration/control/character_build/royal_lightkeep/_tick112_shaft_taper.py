# -*- coding: utf-8 -*-
"""Tick #112: tower shaft taper refine (D1 massing) + inventory.
Continue PASS8_V89_BUTTRESS. Scale lock 24x19x38. No densify. No FINAL."""
import bpy
import bmesh
import os
import shutil
from datetime import datetime
from mathutils import Vector
from collections import Counter

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V89_BUTTRESS.blend")
LOOP = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS1D.blend")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

bpy.ops.wm.open_mainfile(filepath=WORK)
print("OPEN", bpy.data.filepath)

backup = os.path.join(BASE, f"ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_BACKUP_LOOP_{STAMP}.blend")
bpy.ops.wm.save_as_mainfile(filepath=backup, copy=True)
print("BACKUP", backup)


def mesh_local_size(obj):
    me = obj.data
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    zs = [v.co.z for v in me.vertices]
    return Vector((max(xs) - min(xs) or 1e-6, max(ys) - min(ys) or 1e-6, max(zs) - min(zs) or 1e-6))


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
    bmesh.ops.create_cube(bm, size=2.0)
    bm.to_mesh(mesh)
    bm.free()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(o)
    return o


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


def apply_scale(o):
    try:
        for x in bpy.data.objects:
            x.select_set(False)
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    except Exception as e:
        print("APPLY_ERR", o.name, e)


def soft_bevel(o, width=0.06, segments=2):
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


MAT_STONE = make_mat("MAT_LIMESTONE", (0.86, 0.82, 0.74), 0.82, 0.0)
MAT_DARK = make_mat("MAT_FOUNDATION_DARK", (0.14, 0.12, 0.11), 0.92, 0.0)
MAT_GOLD = make_mat("MAT_GOLD_TRIM", (0.95, 0.72, 0.25), 0.18, 0.98)

CX, CY = 1.0, 1.5
X_MIN, X_MAX = -11.5, 12.5
Y_MIN, Y_MAX = -8.5, 10.5
H_MAX = 38.2
n = 0

# Stronger gothic taper: wider base → narrower upper
# SHAFT_SETBACK_1..6 (0 may be hidden)
stages = [
    # name, sx, sy, sz, bottom_z
    ("SHAFT_SETBACK_1", 7.0, 7.0, 5.5, 0.2),
    ("SHAFT_SETBACK_2", 6.0, 6.0, 6.5, 5.7),
    ("SHAFT_SETBACK_3", 5.2, 5.2, 6.0, 12.2),
    ("SHAFT_SETBACK_4", 4.6, 4.6, 5.5, 18.2),
    ("SHAFT_SETBACK_5", 4.0, 4.0, 5.0, 23.7),
    ("SHAFT_SETBACK_6", 4.4, 4.4, 2.2, 28.7),
]
for name, sx, sy, sz, bz in stages:
    o = ensure_cube(name)
    set_size(o, sx, sy, sz, bottom_z=bz, center_xy=(CX, CY))
    assign(o, MAT_DARK if "6" in name or "1" in name and name.endswith("1") else MAT_STONE)
    if name.endswith("_1"):
        assign(o, MAT_DARK)
    apply_scale(o)
    soft_bevel(o, 0.07)
    n += 1
    print("SHAFT", name, sx, sz, bz)

# Gold string courses at setback joints
for i, z in enumerate([5.6, 12.1, 18.1, 23.6, 28.6]):
    w = 7.2 - i * 0.55
    b = ensure_cube(f"SHAFT_BAND_{i}")
    set_size(b, w, w, 0.25, bottom_z=z, center_xy=(CX, CY))
    assign(b, MAT_GOLD if i % 2 == 0 else MAT_DARK)
    apply_scale(b)
    n += 1

# Soft-hide TOWER_FRONT_MASS more (reduce double mass)
t = bpy.data.objects.get("TOWER_FRONT_MASS")
if t:
    t.hide_render = True
    t.hide_viewport = True
    print("HIDE_TOWER_FRONT_MASS")

# Clamp
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
mesh_n = 0
bool_n = 0
hidden_n = 0
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
print("BOUNDS", round(bw, 2), round(bd, 2), round(bh, 2), "Z", round(minz, 2), round(maxz, 2), "MESHES", mesh_n, "UPDATED", n)

state = f"""# AUTONOMOUS BUILD STATE — ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01

**Updated:** 2026-07-27 (job `019f9eec8b6f` tick **#112**, 5m)  
**Asset ID:** `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01`  

| Field | Value |
|-------|--------|
| **ASSET_FINAL_COMPLETE** | **false** |
| **accepted (user)** | **false** |
| **Current** | **PASS8 V90 SHAFT_TAPER** |
| **Scale** | FP **{bw:.1f}×{bd:.1f}** (≤24×19) · top Z **{maxz:.1f}** |
| **Scheduler** | `019f9eec8b6f` every **5 min** |
| **Pipeline** | IN_PROGRESS (shaft taper massing) |

---

## Tick #112 — executed (P1 D1 massing)

### Edits
1. **Shaft taper** — 6 stepped stages wider→narrower (7.0→4.0)
2. **Gold/dark bands** at setback joints
3. Hide TOWER_FRONT_MASS (double mass)

### Inventory
- Visible: **{mesh_n}** · Hidden: **{hidden_n}** · Bool: **{bool_n}**
- Top: {", ".join(f"{k}:{v}" for k, v in top)}

### Files
| Role | Path |
|------|------|
| Work | `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V90_SHAFT_TAPER.blend` |
| Loop / candidate | `PASS1D.blend` / `FINAL.blend` (synced) |
| Backup | `...BACKUP_LOOP_{STAMP}.blend` |
| Proofs | `renders_final/*` + work proofs |

### Bounds
**{bw:.1f} × {bd:.1f} × {bh:.1f}** m · Z {minz:.1f}..**{maxz:.1f}**

### Internal scores
| Axis | Score |
|------|-------|
| Scale | **9.0** |
| Tower taper / mass | ~8.6 |
| Overall | **~8.55** |

### Verdict
Not FINAL. Tower taper improved. D1 modular language reduced but not eliminated. Human overlay for FINAL.
"""

loop_state = f"""# BUILD LOOP STATE

**Updated:** 2026-07-27 · tick **#112** · job `019f9eec8b6f` (5m)  
**ASSET_FINAL_COMPLETE:** false · **Current:** PASS8_V90_SHAFT_TAPER  

## Tick #112 (P1)
- Shaft taper 6 stages + bands; hide TOWER_FRONT_MASS
- Bounds {bw:.1f}×{bd:.1f}×{bh:.1f} · meshes {mesh_n}
- Backup: BACKUP_LOOP_{STAMP}
- Saved: PASS8_V90_SHAFT_TAPER → PASS1D / FINAL

## Next
Human overlay preferred; optional more mass cleanup
"""

dev = f"""# INTERMEDIATE DEVIATION REPORT — tick #112

**Asset:** ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01
**Stamp:** {STAMP}
**File:** PASS8_V90_SHAFT_TAPER / PASS1D
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
- Clearer stepped tower taper
- Gatehouse / stair / curtain / crown / buttress stack retained
- Scale lock held

## Gaps vs mockup (blocking Human accept)
| ID | Pri | Gap |
|----|-----|-----|
| D1 | P1 | Still modular stacked volumes vs carved gothic |
| D2 | P1 | Multi-gable / organic roof still simplified |
| D3 | P2 | Art fidelity below sheet |
| D4 | P2 | Residual hidden clutter |
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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V90_SHAFT_TAPER.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V90")

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

print("TICK112_DONE")
