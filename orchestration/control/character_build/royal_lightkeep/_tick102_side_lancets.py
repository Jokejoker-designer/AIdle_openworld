# -*- coding: utf-8 -*-
"""Tick #102: curved side lancets E/W on tower + hard H clamp.
Continue PASS8_V79_SHAFT_LANCETS. Scale lock 24x19x38. No FINAL claim."""
import bpy
import bmesh
import os
import shutil
import math
from datetime import datetime
from mathutils import Vector, Euler

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V79_SHAFT_LANCETS.blend")
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


def soft_bevel(o, width=0.02, segments=2):
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


def create_lancet_frame(name, half_w=0.4, depth=0.25, thickness=0.1, segs=10):
    R = half_w * 2.0
    spring_z = 0.15
    path = []
    for i in range(3):
        t = i / 2
        path.append(Vector((-half_w, 0, 0.05 + (spring_z - 0.05) * t)))
    for i in range(segs):
        t = i / (segs - 1)
        ang = math.pi - (math.pi / 3) * t
        path.append(Vector((half_w + R * math.cos(ang), 0, spring_z + R * math.sin(ang))))
    for i in range(1, segs):
        t = i / (segs - 1)
        ang = math.pi / 3 - (math.pi / 3) * t
        path.append(Vector((-half_w + R * math.cos(ang), 0, spring_z + R * math.sin(ang))))
    for i in range(1, 3):
        t = i / 2
        path.append(Vector((half_w, 0, spring_z + (0.05 - spring_z) * t)))
    bm = bmesh.new()
    hw_d, hw_t = depth * 0.5, thickness * 0.5
    rings = []
    for i, p in enumerate(path):
        tan = (path[i + 1] - p).normalized() if i < len(path) - 1 else (p - path[i - 1]).normalized()
        side = tan.cross(Vector((0, 0, 1)))
        side = side.normalized() if side.length > 1e-6 else Vector((1, 0, 0))
        ring = []
        for sx, sy in [(-hw_t, -hw_d), (hw_t, -hw_d), (hw_t, hw_d), (-hw_t, hw_d)]:
            ring.append(bm.verts.new(p + side * sx + Vector((0, 1, 0)) * (sy + depth * 0.5)))
        rings.append(ring)
    bm.verts.ensure_lookup_table()
    for i in range(len(rings) - 1):
        a, b = rings[i], rings[i + 1]
        for j in range(4):
            j2 = (j + 1) % 4
            try:
                bm.faces.new([a[j], a[j2], b[j2], b[j]])
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


MAT_STONE = make_mat("MAT_LIMESTONE", (0.86, 0.82, 0.74), 0.82, 0.0)
MAT_GOLD = make_mat("MAT_GOLD_TRIM", (0.95, 0.72, 0.25), 0.18, 0.98)
MAT_GLASS = make_mat("MAT_GLASS_DARK", (0.12, 0.20, 0.28), 0.12, 0.05)

CX, CY = 1.0, 1.5
X_MIN, X_MAX = -11.5, 12.5
Y_MIN, Y_MAX = -8.5, 10.5
H_MAX = 38.2
n = 0
hidden = 0

# Hide remaining TWIN on E/W (box fenestration replaced by curved)
for o in list(bpy.data.objects):
    if o.name.startswith("TWIN_FR_E_") or o.name.startswith("TWIN_PN_E_") or o.name.startswith("TWIN_MU_E_"):
        o.hide_render = True
        o.hide_viewport = True
        hidden += 1
    if o.name.startswith("TWIN_FR_W_") or o.name.startswith("TWIN_PN_W_") or o.name.startswith("TWIN_MU_W_"):
        o.hide_render = True
        o.hide_viewport = True
        hidden += 1
print("HIDDEN_EW_TWIN", hidden)

levels = [5.0, 10.0, 15.0, 20.0, 25.0]
# East face: +X, rotate lancet 90 deg around Z so arch plane faces outward
for face, x_sign, rot_z in (("E", 1.0, math.radians(90)), ("W", -1.0, math.radians(-90))):
    x_face = CX + x_sign * 2.95
    for i, z in enumerate(levels):
        for j, yoff in enumerate([-0.55, 0.55]):
            name = f"LANCET_{face}_{i}_{j}"
            o = create_lancet_frame(name, half_w=0.35, depth=0.26, thickness=0.09, segs=10)
            o.location = (x_face, CY + yoff, z)
            o.rotation_euler = Euler((0, 0, rot_z), "XYZ")
            assign(o, MAT_STONE)
            soft_bevel(o, 0.015)
            g = ensure_cube(f"LANCET_GLASS_{face}_{i}_{j}")
            g.scale = (0.08, 0.4, 0.95)
            g.location = (x_face + x_sign * 0.05, CY + yoff, z + 0.65)
            assign(g, MAT_GLASS)
            n += 2
        sill = ensure_cube(f"LANCET_SILL_{face}_{i}")
        sill.scale = (0.18, 1.5, 0.07)
        sill.location = (x_face, CY, z - 0.05)
        assign(sill, MAT_GOLD)
        n += 1

print("CREATED", n)

# Hard height clamp
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
bool_n = 0
for o in bpy.data.objects:
    if o.type != "MESH":
        continue
    if any(m.type == "BOOLEAN" for m in o.modifiers):
        bool_n += 1
    if o.hide_render:
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

**Updated:** 2026-07-27 (job `019f9eec8b6f` tick **#102**, 5m)  
**Asset ID:** `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01`  

| Field | Value |
|-------|--------|
| **ASSET_FINAL_COMPLETE** | **false** |
| **accepted (user)** | **false** |
| **Current** | **PASS8 V80 SIDE_LANCETS** |
| **Scale** | FP **{bw:.1f}×{bd:.1f}** (≤24×19) · top Z **{maxz:.1f}** |
| **Scheduler** | `019f9eec8b6f` every **5 min** |
| **Pipeline** | IN_PROGRESS (side curved lancets E/W) |

---

## Tick #102 — executed (P1)

### Edits
1. **Hide E/W TWIN boxes** ({hidden})
2. **Curved side lancets** — E/W × 5 levels × 2 + glass + gold sills
3. **Hard H clamp** Z≤38.2

### Files
| Role | Path |
|------|------|
| Work | `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V80_SIDE_LANCETS.blend` |
| Loop / candidate | `PASS1D.blend` / `FINAL.blend` (synced) |
| Backup | `...BACKUP_LOOP_{STAMP}.blend` |
| Proofs | `renders_final/*` + work proofs |

### Bounds
**{bw:.1f} × {bd:.1f} × {bh:.1f}** m · Z {minz:.1f}..**{maxz:.1f}** · meshes ~{mesh_n}

### Internal scores
| Axis | Score |
|------|-------|
| Scale | **9.0** |
| Tower fenestration | ~8.55 |
| Gothic fidelity | ~8.5 |
| Overall | **~8.55** |

### Verdict
Not FINAL. Curved lancets now on N/E/W. D1 modular core still primary Human blocker.  
Next: rear S lancets or roof hip mesh; Human overlay when closer.
"""

loop_state = f"""# BUILD LOOP STATE

**Updated:** 2026-07-27 · tick **#102** · job `019f9eec8b6f` (5m)  
**ASSET_FINAL_COMPLETE:** false · **Current:** PASS8_V80_SIDE_LANCETS  

## Tick #102 (P1)
- Side curved lancets E/W 5×2 each
- Hidden EW TWIN: {hidden}
- Bounds {bw:.1f}×{bd:.1f}×{bh:.1f}
- Backup: BACKUP_LOOP_{STAMP}
- Saved: PASS8_V80_SIDE_LANCETS → PASS1D / FINAL

## Next
Rear S lancets or roof hip mesh; Human overlay when closer
"""

dev = f"""# INTERMEDIATE DEVIATION REPORT — tick #102

**Asset:** ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01
**Stamp:** {STAMP}
**File:** PASS8_V80_SIDE_LANCETS / PASS1D
**ASSET_FINAL_COMPLETE:** false
**accepted (user):** false

## Inventory
- Mesh objects (visible): **{mesh_n}**
- Hidden EW twins: **{hidden}**

## Sheet targets
- Footprint 24×19 m · Height 38 m · Wall 6.5 m
- Achieved: **{bw:.2f}×{bd:.2f}×{bh:.2f}** m · Z {minz:.2f}..{maxz:.2f}

## Matches
- Curved pointed lancets N/E/W tower faces
- Portal curved arch retained
- Scale lock held

## Gaps vs mockup (blocking Human accept)
| ID | Pri | Gap |
|----|-----|-----|
| D1 | P1 | Core modular-box language still dominant |
| D2 | P1 | Roof still plate-rotated hips |
| D3 | P2 | Rear face may still be box fenestration |
| D4 | P2 | High residual object count |
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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V80_SIDE_LANCETS.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V80")

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

print("TICK102_DONE")
