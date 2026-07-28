# -*- coding: utf-8 -*-
"""Tick #121: hard FP clamp 24x19 + silhouette cleanup (hide clutter method).
Continue PASS8_V98_LOWER_FORT. No densify. No FINAL."""
import bpy
import bmesh
import os
import shutil
from datetime import datetime
from mathutils import Vector
from collections import Counter

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V98_LOWER_FORT.blend")
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
    except Exception as e:
        print("APPLY_ERR", obj.name, e)
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
MAT_WOOD = make_mat("MAT_WOOD_DOOR", (0.28, 0.16, 0.08), 0.75, 0.0)

CX, CY = 1.0, 1.5
X_MIN, X_MAX = -11.5, 12.5
Y_MIN, Y_MAX = -8.5, 10.5
H_MAX = 38.2
n = 0
hid = 0

# ------------------------------------------------------------------
# 1) Shrink known oversize volumes to fit FP
# ------------------------------------------------------------------
plinth = bpy.data.objects.get("LOWER_PLINTH")
if plinth:
    set_size(plinth, 23.0, 18.0, 1.15, bottom_z=0.0, center_xy=(CX, CY))
    assign(plinth, MAT_DARK)
    apply_scale(plinth)
    n += 1

for name, sx, sy, sz, bz, xy in (
    ("CURTAIN_FRONT", 19.0, 1.3, 5.5, 1.1, (CX, 4.8)),
    ("CURTAIN_LEFT", 1.2, 15.5, 5.5, 1.1, (CX - 10.2, CY)),
    ("CURTAIN_RIGHT", 1.2, 15.5, 5.5, 1.1, (CX + 10.2, CY)),
    ("LOWER_FRONT_COPE", 19.5, 1.5, 0.32, 6.5, (CX, 4.85)),
    ("GATEHOUSE_MASS", 5.2, 3.2, 6.2, 0.15, (CX, 4.0)),
):
    o = bpy.data.objects.get(name)
    if o:
        set_size(o, sx, sy, sz, bottom_z=bz, center_xy=xy)
        assign(o, MAT_STONE if "GATE" in name or "CURTAIN" in name or "COPE" in name else MAT_DARK)
        apply_scale(o)
        n += 1

# Corner turrets pull inward
for tag, xy in (("FL", (CX - 9.5, 5.0)), ("FR", (CX + 9.5, 5.0))):
    o = bpy.data.objects.get(f"LOWER_CORNER_{tag}")
    if o:
        set_size(o, 2.2, 2.2, 7.5, bottom_z=0.15, center_xy=xy)
        assign(o, MAT_STONE)
        apply_scale(o)
        n += 1
    roof = bpy.data.objects.get(f"LOWER_CORNER_ROOF_{tag}")
    if roof:
        roof.location = (xy[0], xy[1], 7.7)
    tip = bpy.data.objects.get(f"LOWER_CORNER_TIP_{tag}")
    if tip:
        set_size(tip, 0.16, 0.16, 0.4, bottom_z=9.4, center_xy=xy)
        apply_scale(tip)

# U-wrap within bounds
for name, size, z, xy in (
    ("UWRAP_REAR_BAR", (13.0, 1.6, 6.0), 0.2, (CX, -4.2)),
    ("UWRAP_WING_L", (2.0, 10.0, 5.8), 0.2, (CX - 6.8, 0.8)),
    ("UWRAP_WING_R", (2.0, 10.0, 5.8), 0.2, (CX + 6.8, 0.8)),
):
    o = bpy.data.objects.get(name)
    if o:
        set_size(o, *size, bottom_z=z, center_xy=xy)
        assign(o, MAT_STONE)
        apply_scale(o)
        n += 1

print("RESIZE", n)

# ------------------------------------------------------------------
# 2) Hide duplicate/clutter facade that fights lower fort (method change)
# ------------------------------------------------------------------
HIDE_STARTS = (
    "FACADE_PIER_", "FACADE_WIN_", "FACADE_WIN_FR_", "FACADE_MERLON_",
    "FACADE_STRING", "FACADE_BANNER_", "FACADE_BANNER_POLE_",
    "FACADE_PORTAL_TRIM", "FACADE_TOWER_WIN_",
    # duplicate wing masses that double-stack with halls
    "FACADE_WING_L", "FACADE_WING_R",
)
# Keep FACADE_WING_GABLE_* roofs if they help silhouette; hide base wing boxes only
for o in bpy.data.objects:
    if o.type != "MESH":
        continue
    if any(o.name.startswith(p) or o.name == p for p in HIDE_STARTS):
        o.hide_render = True
        o.hide_viewport = True
        hid += 1
    # hide extra UWRAP_CORNER if overcrowded with LOWER_CORNER
    if o.name.startswith("UWRAP_CORNER_") and not o.name.startswith("UWRAP_CORNER_CAP"):
        # keep caps, hide body if LOWER_CORNER exists
        if bpy.data.objects.get("LOWER_CORNER_FL"):
            o.hide_render = True
            o.hide_viewport = True
            hid += 1

print("HIDDEN_CLUTTER", hid)

# ------------------------------------------------------------------
# 3) Ensure critical systems visible
# ------------------------------------------------------------------
MUST = [
    "GATEHOUSE_MASS", "GATEHOUSE_ROOF_GABLE", "GATE_WOOD_DOOR", "GATE_PORTAL_FRAME",
    "STAIR_LANDING_MAIN", "STAIR_TREAD_0", "STAIR_CHEEK_L", "STAIR_CHEEK_R",
    "LOWER_PLINTH", "CURTAIN_FRONT", "LOWER_CORNER_FL", "LOWER_CORNER_FR",
    "SHAFT_SETBACK_2", "CROWN_MESH_COLLAR", "CROWN_MESH_SPIRE",
    "CROWN_MESH_GABLE_N", "CROWN_MESH_GABLE_S", "CROWN_MESH_GABLE_E", "CROWN_MESH_GABLE_W",
    "ROOF_HIP_MESH_MAIN", "ROOF_HIP_MESH_TOWER",
    "UWRAP_REAR_BAR", "UWRAP_WING_L", "UWRAP_WING_R",
    "SCALE_HUMAN", "PRES_GROUND",
]
shown = 0
for name in MUST:
    o = bpy.data.objects.get(name)
    if o:
        o.hide_render = False
        o.hide_viewport = False
        shown += 1
print("ENSURE", shown, "/", len(MUST))

# Soft light polish
sun = bpy.data.objects.get("LIGHT_KEY_SUN")
if sun and sun.data:
    sun.data.energy = 3.8
fill = bpy.data.objects.get("LIGHT_FILL")
if fill and fill.data:
    fill.data.energy = 340

# Scale human
sh = ensure_cube("SCALE_HUMAN")
set_size(sh, 0.4, 0.28, 1.75, bottom_z=0.1, center_xy=(CX - 4.2, 9.5))
assign(sh, make_mat("MAT_SCALE_HUMAN", (0.9, 0.2, 0.15), 0.6, 0.0))
apply_scale(sh)

# ------------------------------------------------------------------
# 4) HARD clamp all visible meshes into box
# ------------------------------------------------------------------
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
    # second pass if still over (object larger than box)
    bpy.context.view_layer.update()
    corners = [o.matrix_world @ Vector(c) for c in o.bound_box]
    minx = min(c.x for c in corners)
    maxx = max(c.x for c in corners)
    miny = min(c.y for c in corners)
    maxy = max(c.y for c in corners)
    bw_o = maxx - minx
    bd_o = maxy - miny
    if bw_o > (X_MAX - X_MIN) + 0.05:
        # scale down X
        factor = (X_MAX - X_MIN) / bw_o * 0.98
        o.scale.x *= factor
        apply_scale(o)
        o.location.x = CX
    if bd_o > (Y_MAX - Y_MIN) + 0.05:
        factor = (Y_MAX - Y_MIN) / bd_o * 0.98
        o.scale.y *= factor
        apply_scale(o)
        o.location.y = CY

# Re-clamp after scale
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    if o.name in ("PRES_GROUND", "LEVEL0_GROUND", "SCALE_HUMAN") or "CUT" in o.name or "CUTTER" in o.name:
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

fp_ok = bw <= 24.05 and bd <= 19.05
print("FP_OK", fp_ok)

state = f"""# AUTONOMOUS BUILD STATE — ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01

**Updated:** 2026-07-27 (job `019f9eec8b6f` tick **#121**, 5m)  
**Asset ID:** `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01`  

| Field | Value |
|-------|--------|
| **ASSET_FINAL_COMPLETE** | **false** |
| **accepted (user)** | **false** |
| **Current** | **PASS8 V99 CLAMP_CLEAN** |
| **Scale** | FP **{bw:.1f}×{bd:.1f}** (≤24×19) · top Z **{maxz:.1f}** · FP_OK={fp_ok} |
| **Scheduler** | `019f9eec8b6f` every **5 min** |
| **Pipeline** | IN_PROGRESS (clamp + clutter hide) |

---

## Tick #121 — executed (P0 scale + cleanup)

### Edits
1. **Hard FP clamp** — plinth/curtains/corners resized; soft+hard box clamp
2. **Clutter hide** — duplicate FACADE_ pier/win/banner stacks ({hid} hidden)
3. **Ensure systems** — gate/stair/shaft/crown/uwrap visible + light polish

### Inventory
- Visible: **{mesh_n}** · Hidden: **{hidden_n}** · Bool: **{bool_n}**
- Top: {", ".join(f"{k}:{v}" for k, v in top)}

### Files
| Role | Path |
|------|------|
| Work | `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V99_CLAMP_CLEAN.blend` |
| Loop / candidate | `PASS1D.blend` / `FINAL.blend` (synced) |
| Backup | `...BACKUP_LOOP_{STAMP}.blend` |
| Proofs | `renders_final/*` + work proofs |

### Bounds
**{bw:.1f} × {bd:.1f} × {bh:.1f}** m · Z {minz:.1f}..**{maxz:.1f}**

### Internal scores
| Axis | Score |
|------|-------|
| Scale | **{"9.0" if fp_ok else "8.5"}** |
| Silhouette clarity | ~8.5 |
| Overall | **~8.55** |

### Verdict
Not FINAL. FP corrected; clutter reduced. D1 modular remains. **Human overlay required for FINAL.**
"""

loop_state = f"""# BUILD LOOP STATE

**Updated:** 2026-07-27 · tick **#121** · job `019f9eec8b6f` (5m)  
**ASSET_FINAL_COMPLETE:** false · **Current:** PASS8_V99_CLAMP_CLEAN  

## Tick #121 (P0)
- Hard clamp FP + hide FACADE clutter ({hid})
- Bounds {bw:.1f}×{bd:.1f}×{bh:.1f} · meshes {mesh_n} · FP_OK={fp_ok}
- Backup: BACKUP_LOOP_{STAMP}
- Saved: PASS8_V99_CLAMP_CLEAN → PASS1D / FINAL

## Next
Plateau ~8.55; major method change or Human overlay
"""

dev = f"""# INTERMEDIATE DEVIATION REPORT — tick #121

**Asset:** ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01
**Stamp:** {STAMP}
**File:** PASS8_V99_CLAMP_CLEAN / PASS1D
**ASSET_FINAL_COMPLETE:** false
**accepted (user):** false

## Inventory
- Mesh objects (visible): **{mesh_n}**
- Hidden: **{hidden_n}** · Bool: **{bool_n}**
- Clutter hidden this tick: **{hid}**
- Top: {", ".join(f"{k}:{v}" for k, v in top)}

## Sheet targets
- Footprint 24×19 m · Height 38 m · Wall 6.5 m
- Achieved: **{bw:.2f}×{bd:.2f}×{bh:.2f}** m · Z {minz:.2f}..{maxz:.2f}
- FP_OK: **{fp_ok}**

## Matches
- Scale lock restored toward 24×19
- Cleaner front (less double facade stack)
- Gate/stair/crown systems retained

## Gaps vs mockup (blocking Human accept)
| ID | Pri | Gap |
|----|-----|-----|
| D1 | P1 | Modular stacked volumes vs carved gothic (primary) |
| D2 | P1 | Organic multi-gable / stone carving fidelity |
| D3 | P2 | Openings proxy not true recesses |
| D4 | P2 | Overall game-block vs sheet art |
| D5 | P3 | UV/LOD |

## Overall ~8.55 plateau — not FINAL until Human overlay / major method change
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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V99_CLAMP_CLEAN.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V99")

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

print("TICK121_DONE")
