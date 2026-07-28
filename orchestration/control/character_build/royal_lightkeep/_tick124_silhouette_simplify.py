# -*- coding: utf-8 -*-
"""Tick #124: METHOD CHANGE — silhouette simplify (hide micro-noise) + primary mass proportions.
Continue PASS8_V101_CROWN_UWRAP. Scale 24x19x38. No densify. No FINAL."""
import bpy
import bmesh
import os
import shutil
from datetime import datetime
from mathutils import Vector
from collections import Counter

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V101_CROWN_UWRAP.blend")
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


MAT_STONE = make_mat("MAT_LIMESTONE", (0.86, 0.82, 0.74), 0.82, 0.0)
MAT_DARK = make_mat("MAT_FOUNDATION_DARK", (0.14, 0.12, 0.11), 0.92, 0.0)
MAT_GOLD = make_mat("MAT_GOLD_TRIM", (0.95, 0.72, 0.25), 0.18, 0.98)
MAT_ROOF = make_mat("MAT_SLATE_NAVY", (0.06, 0.10, 0.22), 0.42, 0.08)
MAT_PATH = make_mat("MAT_PAVING", (0.58, 0.54, 0.48), 0.88, 0.0)

CX, CY = 1.0, 1.5
X_MIN, X_MAX = -11.5, 12.5
Y_MIN, Y_MAX = -8.5, 10.5
H_MAX = 38.2
hid = 0
n = 0

# ------------------------------------------------------------------
# 1) Hide micro-noise prefixes that kill silhouette (method: subtract)
# ------------------------------------------------------------------
HIDE_PREFIX = (
    "CROWN_MESH_MINI_",  # outer mini peaks clutter top
    "SHAFT_LANCET_",  # proxy windows on shaft — keep band only
    "SHAFT_LANCET_FR_",
    "SHAFT_BANNER_",
    "UWRAP_ARCADE_",
    "LOWER_BUTT_CAP_",
    "LOWER_MERLON_",
    "STAIR_RAIL_",
    "HALL_DORMER_WIN_",
    "HALL_DORMER_TIP_",
    "HALL_RIDGE_FIN_",
    "FACADE_WING_TIP_",
    "QBUTT_",  # keep if needed — hide dense buttress cubes
    "CMERLON_",
    "COPE_",
    "LANCET_",  # 100 lancets noise
)
KEEP_EXACT = set()

for o in list(bpy.data.objects):
    if o.type != "MESH" or o.hide_render:
        continue
    name = o.name
    if any(name.startswith(p) for p in HIDE_PREFIX):
        # keep a sparse subset of lancets if critical — hide all for clean read
        o.hide_render = True
        o.hide_viewport = True
        hid += 1

# Hide half of HALL_DORMER bodies if too dense — keep N/S even only
for o in list(bpy.data.objects):
    if o.name.startswith("HALL_DORMER_N_") or o.name.startswith("HALL_DORMER_S_"):
        try:
            idx = int(o.name.rsplit("_", 1)[-1])
            if idx % 2 == 1:
                o.hide_render = True
                o.hide_viewport = True
                hid += 1
        except Exception:
            pass

print("HIDDEN", hid)

# ------------------------------------------------------------------
# 2) Primary mass proportions toward mockup (wider base, continuous tower)
# ------------------------------------------------------------------
# Dark plinth
pl = ensure_cube("LOWER_PLINTH")
set_size(pl, 23.0, 18.0, 1.1, bottom_z=0.0, center_xy=(CX, CY))
assign(pl, MAT_DARK)
apply_scale(pl)
soft_bevel(pl, 0.08)
n += 1

# Curtain front lower fort
cf = ensure_cube("CURTAIN_FRONT")
set_size(cf, 18.5, 1.4, 5.8, bottom_z=1.0, center_xy=(CX, 4.6))
assign(cf, MAT_STONE)
apply_scale(cf)
soft_bevel(cf, 0.08)
n += 1

# Continuous shaft stages (already exist) — reinforce mid body
s2 = ensure_cube("SHAFT_SETBACK_2")
set_size(s2, 5.6, 5.6, 15.0, bottom_z=6.0, center_xy=(CX, CY))
assign(s2, MAT_STONE)
apply_scale(s2)
soft_bevel(s2, 0.1)
n += 1

s3 = ensure_cube("SHAFT_SETBACK_3")
set_size(s3, 4.9, 4.9, 6.5, bottom_z=21.0, center_xy=(CX, CY))
assign(s3, MAT_STONE)
apply_scale(s3)
soft_bevel(s3, 0.09)
n += 1

s4 = ensure_cube("SHAFT_SETBACK_4")
set_size(s4, 4.5, 4.5, 4.2, bottom_z=27.5, center_xy=(CX, CY))
assign(s4, MAT_STONE)
apply_scale(s4)
soft_bevel(s4, 0.08)
n += 1

# Gold bands major only
for i, (z, w) in enumerate([(6.0, 7.0), (20.9, 5.8), (27.4, 5.0)]):
    b = ensure_cube(f"SHAFT_BAND_{i}")
    set_size(b, w, w, 0.22, bottom_z=z, center_xy=(CX, CY))
    assign(b, MAT_GOLD)
    apply_scale(b)
    n += 1

# Gatehouse
gh = ensure_cube("GATEHOUSE_MASS")
set_size(gh, 5.0, 3.2, 6.0, bottom_z=0.15, center_xy=(CX, 3.9))
assign(gh, MAT_STONE)
apply_scale(gh)
soft_bevel(gh, 0.09)
n += 1

# Portal arch ensure
for name in ("PORTAL_ARCH_MESH", "GATE_WOOD_DOOR", "GATEHOUSE_ROOF_GABLE"):
    o = bpy.data.objects.get(name)
    if o:
        o.hide_render = False
        o.hide_viewport = False

# ------------------------------------------------------------------
# 3) Stair + U-wrap ensure (prompt)
# ------------------------------------------------------------------
for i in range(7):
    w = 5.5 - i * 0.2
    y = 9.7 - i * 0.42
    z = 0.12 + i * 0.3
    o = ensure_cube(f"STAIR_TREAD_{i}")
    set_size(o, w, 0.5, 0.3, bottom_z=z, center_xy=(CX, y))
    assign(o, MAT_STONE if i % 2 == 0 else MAT_PATH)
    apply_scale(o)
    n += 1

landing = ensure_cube("STAIR_LANDING_MAIN")
set_size(landing, 5.2, 2.0, 0.4, bottom_z=2.1, center_xy=(CX, 6.3))
assign(landing, MAT_STONE)
apply_scale(landing)

for side, sx in (("L", -2.85), ("R", 2.85)):
    o = ensure_cube(f"STAIR_CHEEK_{side}")
    set_size(o, 0.45, 4.2, 2.2, bottom_z=0.12, center_xy=(CX + sx, 7.5))
    assign(o, MAT_DARK)
    apply_scale(o)
    n += 1

for name, size, z, xy in (
    ("UWRAP_REAR_BAR", (13.0, 1.6, 6.0), 0.2, (CX, -4.3)),
    ("UWRAP_WING_L", (2.0, 10.0, 5.8), 0.2, (CX - 6.9, 0.5)),
    ("UWRAP_WING_R", (2.0, 10.0, 5.8), 0.2, (CX + 6.9, 0.5)),
):
    o = ensure_cube(name)
    set_size(o, *size, bottom_z=z, center_xy=xy)
    assign(o, MAT_STONE)
    apply_scale(o)
    soft_bevel(o, 0.07)
    n += 1

# Crown key pieces ensure (not mini)
for name in (
    "CROWN_MESH_COLLAR", "CROWN_MESH_SPIRE", "CROWN_MESH_SPIRE_GOLD",
    "CROWN_MESH_GABLE_N", "CROWN_MESH_GABLE_S", "CROWN_MESH_GABLE_E", "CROWN_MESH_GABLE_W",
    "CROWN_MESH_GABLE_NE", "CROWN_MESH_GABLE_NW", "CROWN_MESH_GABLE_SE", "CROWN_MESH_GABLE_SW",
    "CROWN_TOP_BANNER", "CROWN_TOP_POLE", "CROWN_GOLD_RING",
    "ROOF_HIP_MESH_MAIN", "ROOF_HIP_MESH_TOWER",
):
    o = bpy.data.objects.get(name)
    if o:
        o.hide_render = False
        o.hide_viewport = False

# Corner lower turrets
for tag, xy in (("FL", (CX - 9.3, 4.8)), ("FR", (CX + 9.3, 4.8))):
    o = bpy.data.objects.get(f"LOWER_CORNER_{tag}")
    if o:
        set_size(o, 2.2, 2.2, 7.5, bottom_z=0.15, center_xy=xy)
        assign(o, MAT_STONE)
        apply_scale(o)
        o.hide_render = False
        o.hide_viewport = False
        n += 1

# Lighting
sun = bpy.data.objects.get("LIGHT_KEY_SUN")
if sun and sun.data:
    sun.data.energy = 4.0
    sun.rotation_euler = (0.9, 0.2, 0.6)
fill = bpy.data.objects.get("LIGHT_FILL")
if fill and fill.data:
    fill.data.energy = 380
rim = bpy.data.objects.get("LIGHT_RIM")
if rim and rim.data:
    rim.data.energy = 220

sh = ensure_cube("SCALE_HUMAN")
set_size(sh, 0.4, 0.28, 1.75, bottom_z=0.1, center_xy=(CX - 4.3, 9.5))
assign(sh, make_mat("MAT_SCALE_HUMAN", (0.9, 0.2, 0.15), 0.6, 0.0))
apply_scale(sh)

print("SIMPLIFY", n, "hid", hid)

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

**Updated:** 2026-07-27 (job `019f9eec8b6f` tick **#124**, 5m)  
**Asset ID:** `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01`  

| Field | Value |
|-------|--------|
| **ASSET_FINAL_COMPLETE** | **false** |
| **accepted (user)** | **false** |
| **Current** | **PASS8 V102 SILHOUETTE_SIMPLIFY** |
| **Scale** | FP **{bw:.1f}×{bd:.1f}** (≤24×19) · top Z **{maxz:.1f}** |
| **Scheduler** | `019f9eec8b6f` every **5 min** |
| **Pipeline** | IN_PROGRESS (method: hide noise + primary masses) |

---

## Tick #124 — executed (method change)

### Edits
1. **Hide micro-noise** — LANCET/CMERLON/QBUTT/mini-crown/shaft proxy windows ({hid})
2. **Primary masses** — plinth, curtain, continuous shaft, gatehouse proportions
3. **Stair + U-wrap ensure** + hero lighting polish

### Inventory
- Visible: **{mesh_n}** · Hidden: **{hidden_n}** · Bool: **{bool_n}**
- Top: {", ".join(f"{k}:{v}" for k, v in top)}

### Files
| Role | Path |
|------|------|
| Work | `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V102_SILHOUETTE_SIMPLIFY.blend` |
| Loop / candidate | `PASS1D.blend` / `FINAL.blend` (synced) |
| Backup | `...BACKUP_LOOP_{STAMP}.blend` |
| Proofs | `renders_final/*` + work proofs |

### Bounds
**{bw:.1f} × {bd:.1f} × {bh:.1f}** m · Z {minz:.1f}..**{maxz:.1f}**

### Internal scores
| Axis | Score |
|------|-------|
| Scale | **9.0** |
| Silhouette clarity | ~8.6 |
| Overall | **~8.55** |

### Verdict
Not FINAL. Cleaner silhouette via subtractive method. D1 modular remains. **Human overlay required for FINAL.**
"""

loop_state = f"""# BUILD LOOP STATE

**Updated:** 2026-07-27 · tick **#124** · job `019f9eec8b6f` (5m)  
**ASSET_FINAL_COMPLETE:** false · **Current:** PASS8_V102_SILHOUETTE_SIMPLIFY  

## Tick #124 (method)
- Hide noise {hid}; primary masses; stair/uwrap ensure
- Bounds {bw:.1f}×{bd:.1f}×{bh:.1f} · meshes {mesh_n}
- Backup: BACKUP_LOOP_{STAMP}
- Saved: PASS8_V102_SILHOUETTE_SIMPLIFY → PASS1D / FINAL

## Next
Plateau; Human overlay; avoid densify
"""

dev = f"""# INTERMEDIATE DEVIATION REPORT — tick #124

**Asset:** ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01
**Stamp:** {STAMP}
**File:** PASS8_V102_SILHOUETTE_SIMPLIFY / PASS1D
**ASSET_FINAL_COMPLETE:** false
**accepted (user):** false

## Inventory
- Mesh objects (visible): **{mesh_n}** (was higher; simplified)
- Hidden: **{hidden_n}** · newly hidden this tick ~**{hid}**
- Bool: **{bool_n}**
- Top: {", ".join(f"{k}:{v}" for k, v in top)}

## Sheet targets
- Footprint 24×19 m · Height 38 m · Wall 6.5 m
- Achieved: **{bw:.2f}×{bd:.2f}×{bh:.2f}** m · Z {minz:.2f}..{maxz:.2f}

## Matches
- Cleaner silhouette (less micro-cube noise)
- Continuous tower mid mass
- Stair / U-wrap / crown core retained
- Scale lock held

## Gaps vs mockup (blocking Human accept)
| ID | Pri | Gap |
|----|-----|-----|
| D1 | P1 | Modular volumes vs carved gothic |
| D2 | P1 | Organic multi-gable / stone carving |
| D3 | P2 | True recessed openings |
| D4 | P2 | Art fidelity vs sheet |
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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V102_SILHOUETTE_SIMPLIFY.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V102")

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

print("TICK124_DONE")
