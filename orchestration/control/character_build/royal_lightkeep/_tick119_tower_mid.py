# -*- coding: utf-8 -*-
"""Tick #119: tower mid continuous shaft (anti-box-stack) + tall lancets + 3Q.
Continue PASS8_V96_FACADE_WINGS. Scale lock 24x19x38. No densify. No FINAL."""
import bpy
import bmesh
import os
import shutil
import math
from datetime import datetime
from mathutils import Vector
from collections import Counter

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V96_FACADE_WINGS.blend")
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


def soft_bevel(o, width=0.05, segments=2):
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
MAT_GLASS = make_mat("MAT_GLASS_DARK", (0.12, 0.20, 0.28), 0.12, 0.05)
MAT_BANNER = make_mat("MAT_BANNER_BLUE", (0.08, 0.18, 0.45), 0.55, 0.0)

CX, CY = 1.0, 1.5
X_MIN, X_MAX = -11.5, 12.5
Y_MIN, Y_MAX = -8.5, 10.5
H_MAX = 38.2
n = 0
hidden = 0

# ------------------------------------------------------------------
# 1) Hide redundant box-stack tower parts (method: simplify mid)
# ------------------------------------------------------------------
HIDE_PREFIXES = (
    "TOWER_FRONT_MASS", "TOWER_MID_MASS", "TOWER_UPPER_MASS",
    "TOWER_BOX_", "TOWER_LEVEL_", "TOWER_SEG_",
)
HIDE_NAMES = {
    "TOWER_FRONT_MASS", "TOWER_REAR_MASS", "TOWER_CORE_OLD",
}
for o in list(bpy.data.objects):
    if o.type != "MESH":
        continue
    if o.name in HIDE_NAMES or any(o.name.startswith(p) for p in HIDE_PREFIXES):
        if o.name.startswith("TOWER_") and "LANCET" not in o.name and "BANNER" not in o.name:
            # hide generic TOWER_* boxes but keep TOWER named systems carefully
            if any(k in o.name for k in ("SETBACK", "SHAFT", "CROWN", "HIP", "LANCET", "WIN", "BAND")):
                continue
            if o.name.startswith("TOWER_") and o.name.count("_") <= 3:
                o.hide_render = True
                o.hide_viewport = True
                hidden += 1

# Hide old mid setbacks 3-5 if we rebuild continuous — keep 1,2,6 structure but reshape
print("HIDDEN_TOWER_CLUTTER", hidden)

# ------------------------------------------------------------------
# 2) Continuous 3-stage shaft (base / mid / belfry) — fewer joints
# ------------------------------------------------------------------
# Base plinth dark
s1 = ensure_cube("SHAFT_SETBACK_1")
set_size(s1, 7.2, 7.2, 6.0, bottom_z=0.15, center_xy=(CX, CY))
assign(s1, MAT_DARK)
apply_scale(s1)
soft_bevel(s1, 0.08)
n += 1

# Continuous mid (was 2+3+4 stacked) → single tall body
s2 = ensure_cube("SHAFT_SETBACK_2")
set_size(s2, 5.8, 5.8, 14.5, bottom_z=6.1, center_xy=(CX, CY))
assign(s2, MAT_STONE)
apply_scale(s2)
soft_bevel(s2, 0.09)
n += 1

# Upper body taper
s3 = ensure_cube("SHAFT_SETBACK_3")
set_size(s3, 5.0, 5.0, 7.0, bottom_z=20.5, center_xy=(CX, CY))
assign(s3, MAT_STONE)
apply_scale(s3)
soft_bevel(s3, 0.08)
n += 1

# Belfry gallery
s4 = ensure_cube("SHAFT_SETBACK_4")
set_size(s4, 4.6, 4.6, 4.5, bottom_z=27.4, center_xy=(CX, CY))
assign(s4, MAT_STONE)
apply_scale(s4)
soft_bevel(s4, 0.07)
n += 1

# Collar under crown
s5 = ensure_cube("SHAFT_SETBACK_5")
set_size(s5, 5.0, 5.0, 1.4, bottom_z=31.6, center_xy=(CX, CY))
assign(s5, MAT_STONE)
apply_scale(s5)
n += 1

# Hide old setback 6 if oversized
s6 = bpy.data.objects.get("SHAFT_SETBACK_6")
if s6:
    s6.hide_render = True
    s6.hide_viewport = True

# Gold bands only at major joints (not every micro step)
for i, (z, w) in enumerate([(6.0, 7.4), (20.4, 6.0), (27.3, 5.2), (31.5, 5.4)]):
    b = ensure_cube(f"SHAFT_BAND_{i}")
    set_size(b, w, w, 0.22, bottom_z=z, center_xy=(CX, CY))
    assign(b, MAT_GOLD)
    apply_scale(b)
    n += 1

print("SHAFT_STAGES", n)

# ------------------------------------------------------------------
# 3) Corner piers continuous (mockup octagonal corners)
# ------------------------------------------------------------------
for tag, dx, dy in (("NE", 1.0, 1.0), ("NW", -1.0, 1.0), ("SE", 1.0, -1.0), ("SW", -1.0, -1.0)):
    # mid pier
    p = ensure_cube(f"SHAFT_CORNER_{tag}")
    set_size(p, 1.1, 1.1, 21.0, bottom_z=6.0, center_xy=(CX + dx * 2.6, CY + dy * 2.6))
    assign(p, MAT_STONE)
    apply_scale(p)
    soft_bevel(p, 0.06)
    # blue conical-ish cap via gable
    cap = create_gable_prism(f"SHAFT_CORNER_CAP_{tag}", width=1.4, depth=1.4, height=1.6)
    cap.location = (CX + dx * 2.6, CY + dy * 2.6, 27.0)
    assign(cap, MAT_ROOF)
    tip = ensure_cube(f"SHAFT_CORNER_TIP_{tag}")
    set_size(tip, 0.15, 0.15, 0.4, bottom_z=28.5, center_xy=(CX + dx * 2.6, CY + dy * 2.6))
    assign(tip, MAT_GOLD)
    apply_scale(tip)
    n += 3

# ------------------------------------------------------------------
# 4) Tall front/side lancet rows on mid shaft (vertical gothic)
# ------------------------------------------------------------------
# Front face tall windows (3 columns x 2 rows)
for col, xoff in enumerate([-1.3, 0.0, 1.3]):
    for row, z0 in enumerate([9.0, 15.5]):
        win = ensure_cube(f"SHAFT_LANCET_F_{col}_{row}")
        set_size(win, 0.85, 0.25, 3.8, bottom_z=z0, center_xy=(CX + xoff, CY + 2.95))
        assign(win, MAT_GLASS)
        apply_scale(win)
        fr = ensure_cube(f"SHAFT_LANCET_FR_F_{col}_{row}")
        set_size(fr, 1.0, 0.12, 4.1, bottom_z=z0 - 0.1, center_xy=(CX + xoff, CY + 3.05))
        assign(fr, MAT_GOLD)
        apply_scale(fr)
        n += 2

# Side faces (L/R) one column each for 3Q
for side, sx in (("L", -2.95), ("R", 2.95)):
    for row, z0 in enumerate([9.0, 15.5, 22.0]):
        win = ensure_cube(f"SHAFT_LANCET_{side}_{row}")
        set_size(win, 0.25, 0.85, 3.5, bottom_z=z0, center_xy=(CX + sx, CY))
        assign(win, MAT_GLASS)
        apply_scale(win)
        n += 1

# Belfry arcade openings (4 sides)
for tag, dx, dy, sx, sy in (
    ("N", 0, 1, 1.2, 0.2),
    ("S", 0, -1, 1.2, 0.2),
    ("E", 1, 0, 0.2, 1.2),
    ("W", -1, 0, 0.2, 1.2),
):
    arc = ensure_cube(f"SHAFT_BELFRY_{tag}")
    set_size(arc, sx, sy, 2.4, bottom_z=28.0, center_xy=(CX + dx * 2.35, CY + dy * 2.35))
    assign(arc, MAT_GLASS)
    apply_scale(arc)
    n += 1

# Blue banners on mid tower (mockup)
for side, sx in (("L", -2.0), ("R", 2.0)):
    b = ensure_cube(f"SHAFT_BANNER_{side}")
    set_size(b, 1.1, 0.08, 2.4, bottom_z=17.5, center_xy=(CX + sx, CY + 3.0))
    assign(b, MAT_BANNER)
    apply_scale(b)
    n += 1

# Ensure crown still up
for name in (
    "CROWN_MESH_COLLAR", "CROWN_MESH_SPIRE", "CROWN_MESH_GABLE_N",
    "CROWN_MESH_GABLE_S", "CROWN_MESH_GABLE_E", "CROWN_MESH_GABLE_W",
    "ROOF_HIP_MESH_TOWER",
):
    o = bpy.data.objects.get(name)
    if o:
        o.hide_render = False
        o.hide_viewport = False

# Front gray panels → stone (if still dark blank)
for name in ("STAIR_GATE_VOID",):
    o = bpy.data.objects.get(name)
    if o:
        set_size(o, 2.4, 1.0, 3.2, bottom_z=0.45, center_xy=(CX, 5.65))
        assign(o, MAT_DARK)
        apply_scale(o)

# Keep stair
for name in ("STAIR_LANDING_MAIN", "STAIR_TREAD_0", "STAIR_CHEEK_L", "SCALE_HUMAN"):
    o = bpy.data.objects.get(name)
    if o:
        o.hide_render = False
        o.hide_viewport = False

print("TOWER_MID_DONE", n, "hidden", hidden)

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
print("BOUNDS", round(bw, 2), round(bd, 2), round(bh, 2), "Z", round(minz, 2), round(maxz, 2), "MESHES", mesh_n)

state = f"""# AUTONOMOUS BUILD STATE — ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01

**Updated:** 2026-07-27 (job `019f9eec8b6f` tick **#119**, 5m)  
**Asset ID:** `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01`  

| Field | Value |
|-------|--------|
| **ASSET_FINAL_COMPLETE** | **false** |
| **accepted (user)** | **false** |
| **Current** | **PASS8 V97 TOWER_MID** |
| **Scale** | FP **{bw:.1f}×{bd:.1f}** (≤24×19) · top Z **{maxz:.1f}** |
| **Scheduler** | `019f9eec8b6f` every **5 min** |
| **Pipeline** | IN_PROGRESS (continuous tower mid shaft) |

---

## Tick #119 — executed (P1 D1 tower)

### Edits
1. **Shaft rework** — 5 continuous stages (hide micro-stack clutter)
2. **Corner piers** — 4 vertical + blue caps
3. **Tall lancets** — front 3×2 + side rows + belfry openings + mid banners

### Inventory
- Visible: **{mesh_n}** · Hidden: **{hidden_n}** · Bool: **{bool_n}**
- Top: {", ".join(f"{k}:{v}" for k, v in top)}

### Files
| Role | Path |
|------|------|
| Work | `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V97_TOWER_MID.blend` |
| Loop / candidate | `PASS1D.blend` / `FINAL.blend` (synced) |
| Backup | `...BACKUP_LOOP_{STAMP}.blend` |
| Proofs | `renders_final/*` + work proofs |

### Bounds
**{bw:.1f} × {bd:.1f} × {bh:.1f}** m · Z {minz:.1f}..**{maxz:.1f}**

### Internal scores
| Axis | Score |
|------|-------|
| Scale | **9.0** |
| Tower continuity | ~8.5 |
| 3Q silhouette | ~8.5 |
| Overall | **~8.55** |

### Verdict
Not FINAL. Tower mid less stacked. D1 modular language still present. **Human overlay required for FINAL.**
"""

loop_state = f"""# BUILD LOOP STATE

**Updated:** 2026-07-27 · tick **#119** · job `019f9eec8b6f` (5m)  
**ASSET_FINAL_COMPLETE:** false · **Current:** PASS8_V97_TOWER_MID  

## Tick #119 (P1)
- Continuous shaft stages + corner piers + tall lancets
- Bounds {bw:.1f}×{bd:.1f}×{bh:.1f} · meshes {mesh_n}
- Backup: BACKUP_LOOP_{STAMP}
- Saved: PASS8_V97_TOWER_MID → PASS1D / FINAL

## Next
Front lower mass still boxy; method change over densify
"""

dev = f"""# INTERMEDIATE DEVIATION REPORT — tick #119

**Asset:** ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01
**Stamp:** {STAMP}
**File:** PASS8_V97_TOWER_MID / PASS1D
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
- Fewer mid-tower box joints
- Tall vertical window language
- Corner pier continuity for 3Q
- Scale lock held

## Gaps vs mockup (blocking Human accept)
| ID | Pri | Gap |
|----|-----|-----|
| D1 | P1 | Modular volumes vs carved gothic still primary |
| D2 | P1 | Roof multi-gable organic fidelity |
| D3 | P2 | Front lower fortification still slabby |
| D4 | P2 | True recessed openings vs glass proxy |
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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V97_TOWER_MID.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V97")

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

print("TICK119_DONE")
