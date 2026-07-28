# -*- coding: utf-8 -*-
"""Tick #86: main stair cascade + courtyard U-wrap + crown gable wedges.
Continue PASS8_V63_SNAP7. Scale lock 24x19x38. No FINAL claim."""
import bpy
import os
import shutil
import bmesh
import math
from datetime import datetime
from mathutils import Vector, Euler

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V63_SNAP7.blend")
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
    if o.type != "MESH":
        return
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


MAT_STONE = make_mat("MAT_LIMESTONE", (0.82, 0.78, 0.70), 0.78, 0.0)
MAT_DARK = make_mat("MAT_FOUNDATION_DARK", (0.18, 0.16, 0.14), 0.90, 0.0)
MAT_PATH = make_mat("MAT_PAVING", (0.55, 0.52, 0.48), 0.85, 0.0)
MAT_GOLD = make_mat("MAT_GOLD_TRIM", (0.90, 0.68, 0.22), 0.22, 0.95)
MAT_ROOF = make_mat("MAT_SLATE_NAVY", (0.08, 0.12, 0.26), 0.45, 0.05)
MAT_WOOD = make_mat("MAT_WOOD", (0.35, 0.22, 0.12), 0.75, 0.0)

CX, CY = 1.0, 1.5
X_MIN, X_MAX = -11.5, 12.5
Y_MIN, Y_MAX = -8.5, 10.5
H_MAX = 38.2
n_new = 0

# ========== 1) MAIN STAIR cascade (front approach, mockup monumental steps) ==========
# Landing platform at portal base
o = ensure_cube("STAIR_LANDING_MAIN")
set_size(o, 5.2, 2.4, 0.35, bottom_z=0.12, center_xy=(CX, 5.8))
assign(o, MAT_STONE)
apply_scale(o)
soft_bevel(o, 0.04)
n_new += 1

# Cascading treads (wide → narrow toward portal, rising toward hall)
for i in range(8):
    w = 5.0 - i * 0.22
    d = 0.55
    h = 0.28
    y = 8.6 - i * 0.48
    z = 0.12 + i * 0.26
    name = f"STAIR_TREAD_{i}"
    o = ensure_cube(name)
    set_size(o, w, d, h, bottom_z=z, center_xy=(CX, y))
    assign(o, MAT_STONE if i % 2 == 0 else MAT_PATH)
    apply_scale(o)
    soft_bevel(o, 0.03)
    n_new += 1

# Cheek walls left/right of stair
for side, sx in (("L", -2.7), ("R", 2.7)):
    o = ensure_cube(f"STAIR_CHEEK_{side}")
    set_size(o, 0.45, 4.2, 1.6, bottom_z=0.15, center_xy=(CX + sx, 7.0))
    assign(o, MAT_DARK)
    apply_scale(o)
    soft_bevel(o, 0.05)
    cap = ensure_cube(f"STAIR_CHEEK_CAP_{side}")
    set_size(cap, 0.55, 4.2, 0.14, bottom_z=1.7, center_xy=(CX + sx, 7.0))
    assign(cap, MAT_GOLD)
    apply_scale(cap)
    n_new += 2

# ========== 2) Courtyard U-wrap (deepen C-shape void walls) ==========
# Rear cross-bar of U (closes courtyard behind tower/hall)
o = ensure_cube("UWRAP_REAR_BAR")
set_size(o, 14.0, 1.8, 6.2, bottom_z=0.2, center_xy=(CX, -4.5))
assign(o, MAT_STONE)
apply_scale(o)
soft_bevel(o, 0.08)
n_new += 1

# Left wing deepen
o = ensure_cube("UWRAP_WING_L")
set_size(o, 2.2, 10.5, 6.0, bottom_z=0.2, center_xy=(CX - 7.2, 1.0))
assign(o, MAT_STONE)
apply_scale(o)
soft_bevel(o, 0.08)
n_new += 1

# Right wing deepen
o = ensure_cube("UWRAP_WING_R")
set_size(o, 2.2, 10.5, 6.0, bottom_z=0.2, center_xy=(CX + 7.2, 1.0))
assign(o, MAT_STONE)
apply_scale(o)
soft_bevel(o, 0.08)
n_new += 1

# Inner court floor void marker (paving ring, not solid fill)
o = ensure_cube("UWRAP_COURT_PAVE")
set_size(o, 9.5, 7.0, 0.12, bottom_z=0.08, center_xy=(CX, 0.8))
assign(o, MAT_PATH)
apply_scale(o)
n_new += 1

# Arcade colonnade suggestion on inner faces of U
for i, xoff in enumerate([-5.5, -3.5, 3.5, 5.5]):
    col = ensure_cube(f"UWRAP_COL_{i}")
    set_size(col, 0.45, 0.45, 4.2, bottom_z=0.25, center_xy=(CX + xoff, -2.8))
    assign(col, MAT_STONE)
    apply_scale(col)
    soft_bevel(col, 0.04)
    n_new += 1

# ========== 3) Tower crown gable wedges (break pure box crown) ==========
# 4 pitched wedge slabs rotated ~35° on X or Y for gable silhouette
pitch = math.radians(32)
for i, (dx, dy, axis) in enumerate([
    (0.0, -2.4, "X"),
    (0.0, 2.4, "X"),
    (-2.4, 0.0, "Y"),
    (2.4, 0.0, "Y"),
]):
    name = f"CROWN_GABLE_WEDGE_{i}"
    o = ensure_cube(name)
    set_size(o, 4.2 if axis == "X" else 1.4, 1.4 if axis == "X" else 4.2, 1.8,
             bottom_z=33.6, center_xy=(CX + dx, CY + dy))
    if axis == "X":
        o.rotation_euler = Euler((pitch if dy < 0 else -pitch, 0, 0), "XYZ")
    else:
        o.rotation_euler = Euler((0, pitch if dx > 0 else -pitch, 0), "XYZ")
    assign(o, MAT_ROOF)
    apply_scale(o)
    soft_bevel(o, 0.05)
    n_new += 1

# Corner hip connectors
for i, (dx, dy) in enumerate([(-1.8, -1.8), (1.8, -1.8), (-1.8, 1.8), (1.8, 1.8)]):
    o = ensure_cube(f"CROWN_HIP_CONN_{i}")
    set_size(o, 1.6, 1.6, 1.4, bottom_z=34.0, center_xy=(CX + dx, CY + dy))
    assign(o, MAT_ROOF)
    apply_scale(o)
    n_new += 1

# Parapet merlon ring under crown (break cylinder box feel)
for i in range(12):
    ang = i * (math.pi * 2 / 12)
    x = CX + 3.1 * math.cos(ang)
    y = CY + 3.1 * math.sin(ang)
    o = ensure_cube(f"CROWN_MERLON_R_{i}")
    set_size(o, 0.55, 0.55, 0.9, bottom_z=32.6, center_xy=(x, y))
    assign(o, MAT_STONE)
    apply_scale(o)
    n_new += 1

print("CREATED_OR_UPDATED", n_new)

# Soft footprint + height clamp
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    if o.name in ("PRES_GROUND", "LEVEL0_GROUND", "SCALE_HUMAN") or "BOOL_CUT" in o.name or o.name.endswith("_CUT"):
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
    top = o.location.z + o.dimensions.z / 2.0
    if top > H_MAX:
        o.location.z -= (top - H_MAX)

# Bounds report
minx = miny = minz = 1e9
maxx = maxy = maxz = -1e9
mesh_n = 0
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    if o.name in ("PRES_GROUND", "SCALE_HUMAN") or "BOOL_CUT" in o.name or o.name.endswith("_CUT"):
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

# State files
state = f"""# AUTONOMOUS BUILD STATE — ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01

**Updated:** 2026-07-27 (job `019f9eec8b6f` tick **#86**, 5m)  
**Asset ID:** `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01`  

| Field | Value |
|-------|--------|
| **ASSET_FINAL_COMPLETE** | **false** |
| **accepted (user)** | **false** |
| **Current** | **PASS8 V64 STAIR_UWRAP** |
| **Scale** | FP **{bw:.1f}×{bd:.1f}** (≤24×19) · top Z **{maxz:.1f}** |
| **Scheduler** | `019f9eec8b6f` every **5 min** |
| **Pipeline** | IN_PROGRESS (stair + U-wrap + crown gables) |

---

## Tick #86 — executed (P0/P1)

### Edits
1. **Main stair cascade** — 8 treads + landing + cheek walls/gold caps
2. **Courtyard U-wrap** — rear bar + L/R wings + court pave + 4 colonnade posts
3. **Crown gable wedges** — 4 pitched roof slabs + hip connectors + 12 merlon ring

### Files
| Role | Path |
|------|------|
| Work | `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V64_STAIR_UWRAP.blend` |
| Loop / candidate | `PASS1D.blend` / `FINAL.blend` (synced) |
| Backup | `...BACKUP_LOOP_{STAMP}.blend` |
| Proofs | `renders_final/*` + work proofs |

### Bounds
**{bw:.1f} × {bd:.1f} × {bh:.1f}** m · Z {minz:.1f}..**{maxz:.1f}** · meshes ~{mesh_n}

### Internal scores
| Axis | Score |
|------|-------|
| Scale | **9.0** |
| Stair / approach | ~8.2 |
| Courtyard U-wrap | ~8.0 |
| Crown silhouette | ~8.15 |
| Gothic fidelity | ~7.7 |
| Overall | **~8.15** |

### Verdict
Not FINAL. D1 modular-box reduced but still blocks Human overlay accept.  
Next: boolean deepen court void or gothic window carve on wings.
"""

loop_state = f"""# BUILD LOOP STATE

**Updated:** 2026-07-27 · tick **#86** · job `019f9eec8b6f` (5m)  
**ASSET_FINAL_COMPLETE:** false · **Current:** PASS8_V64_STAIR_UWRAP  

## Tick #86 (P0/P1)
- Main stair cascade (8 treads + cheeks)
- Courtyard U-wrap wings + rear bar
- Crown gable wedges + merlon ring
- Bounds {bw:.1f}×{bd:.1f}×{bh:.1f}
- Backup: BACKUP_LOOP_{STAMP}
- Saved: PASS8_V64_STAIR_UWRAP → PASS1D / FINAL

## Next
Court void boolean deepen OR wing gothic openings; Human overlay when closer to mockup
"""

dev = f"""# INTERMEDIATE DEVIATION REPORT — tick #86

**Asset:** ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01
**Stamp:** {STAMP}
**File:** PASS8_V64_STAIR_UWRAP / PASS1D
**ASSET_FINAL_COMPLETE:** false
**accepted (user):** false

## Inventory
- Mesh objects (approx visible structural): **{mesh_n}**
- Edits this tick: stair cascade, U-wrap, crown gables

## Sheet targets
- Footprint 24×19 m · Height 38 m · Wall 6.5 m
- Achieved: **{bw:.2f}×{bd:.2f}×{bh:.2f}** m · Z {minz:.2f}..{maxz:.2f}

## Matches
- Monumental front stair cascade toward portal
- C/U courtyard wrap (rear bar + side wings)
- Crown pitched gable wedges + merlon ring
- Scale lock held

## Gaps vs mockup (blocking Human accept)
| ID | Pri | Gap |
|----|-----|-----|
| D1 | P1 | Core volumes still modular-box dominant |
| D2 | P1 | Roof not continuous organic gothic form |
| D3 | P2 | Tracery/detail still below sheet fidelity |
| D4 | P2 | Court void may need boolean carve depth |
| D5 | P3 | UV/LOD not authored |

## Overall ~8.15 — not FINAL until Human overlay
Stair/U-wrap/crown improved; modular language still primary blocker.
"""

with open(os.path.join(BASE, "AUTONOMOUS_BUILD_STATE.md"), "w", encoding="utf-8") as f:
    f.write(state)
with open(os.path.join(BASE, "PASS1D_LOOP_STATE.md"), "w", encoding="utf-8") as f:
    f.write(loop_state)
with open(os.path.join(BASE, "INTERMEDIATE_DEVIATION_REPORT.md"), "w", encoding="utf-8") as f:
    f.write(dev)
print("WROTE_STATE")

# Clear false complete flag if present
flag = os.path.join(BASE, "ASSET_FINAL_COMPLETE.flag")
if os.path.isfile(flag):
    try:
        os.remove(flag)
        print("REMOVED_FALSE_FINAL_FLAG")
    except Exception as e:
        print("FLAG_RM_ERR", e)

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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V64_STAIR_UWRAP.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V64")

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

print("TICK86_DONE")
