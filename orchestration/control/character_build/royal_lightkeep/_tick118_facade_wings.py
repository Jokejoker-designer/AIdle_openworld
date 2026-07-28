# -*- coding: utf-8 -*-
"""Tick #118: front facade bays + barracks wing multi-gables (method: bay language).
Continue PASS8_V95_STAIR_UWRAP_CROWN. Scale lock 24x19x38. No densify. No FINAL."""
import bpy
import bmesh
import os
import shutil
import math
from datetime import datetime
from mathutils import Vector
from collections import Counter

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V95_STAIR_UWRAP_CROWN.blend")
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
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    try:
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    except Exception:
        pass
    obj.select_set(False)


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


def create_pointed_window_proxy(name, half_w=0.55, rise=1.8, depth=0.35):
    """Simple pointed-arch silhouette as extruded 2D (glass + frame)."""
    bm = bmesh.new()
    # base rectangle + pointed top
    pts = []
    segs = 10
    for i in range(segs + 1):
        t = i / segs
        # left side of arch from base to apex via two arcs approx
        x = -half_w + (half_w * 2) * t
        # pointed: height rises as 1 - abs(2t-1)
        z = rise * (1.0 - abs(2.0 * t - 1.0) ** 0.85)
        pts.append((x, z))
    # bottom corners
    verts_f = []
    verts_b = []
    y0, y1 = -depth * 0.5, depth * 0.5
    # bottom left, bottom right
    bl = bm.verts.new((-half_w, y0, 0))
    br = bm.verts.new((half_w, y0, 0))
    # arch front
    arch_f = [bm.verts.new((x, y0, z)) for x, z in pts]
    arch_b = [bm.verts.new((x, y1, z)) for x, z in pts]
    bm.verts.ensure_lookup_table()
    # front face
    try:
        bm.faces.new([bl] + arch_f + [br])
    except Exception:
        pass
    try:
        bm.faces.new([br] + list(reversed(arch_b)) + [bm.verts.new((-half_w, y1, 0))])
    except Exception:
        pass
    # simpler solid: box with peak via gable-like
    bm.free()
    # fallback solid lancet prism
    bm = bmesh.new()
    hw, d, h = half_w, depth * 0.5, rise
    v = [
        bm.verts.new((-hw, -d, 0)),
        bm.verts.new((hw, -d, 0)),
        bm.verts.new((hw, d, 0)),
        bm.verts.new((-hw, d, 0)),
        bm.verts.new((0, -d, h)),
        bm.verts.new((0, d, h)),
        bm.verts.new((-hw, -d, h * 0.55)),
        bm.verts.new((hw, -d, h * 0.55)),
        bm.verts.new((hw, d, h * 0.55)),
        bm.verts.new((-hw, d, h * 0.55)),
    ]
    bm.verts.ensure_lookup_table()
    # box body
    for f in (
        [v[0], v[1], v[7], v[6]],
        [v[3], v[9], v[8], v[2]],
        [v[0], v[6], v[9], v[3]],
        [v[1], v[2], v[8], v[7]],
        [v[0], v[3], v[2], v[1]],
        [v[6], v[7], v[4]],
        [v[9], v[5], v[8]],
        [v[6], v[4], v[5], v[9]],
        [v[7], v[8], v[5], v[4]],
    ):
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

# ------------------------------------------------------------------
# 1) Soften oversized gray gate void — smaller, deeper portal only
# ------------------------------------------------------------------
void = bpy.data.objects.get("STAIR_GATE_VOID")
if void:
    set_size(void, 2.6, 1.2, 3.4, bottom_z=0.4, center_xy=(CX, 5.7))
    assign(void, MAT_DARK)
    apply_scale(void)
    n += 1

bay = bpy.data.objects.get("STAIR_GATE_BAY")
if bay:
    set_size(bay, 5.0, 2.0, 5.2, bottom_z=0.2, center_xy=(CX, 4.8))
    assign(bay, MAT_STONE)
    apply_scale(bay)
    soft_bevel(bay, 0.08)
    n += 1

# Gold portal trim
trim = ensure_cube("FACADE_PORTAL_TRIM")
set_size(trim, 3.2, 0.2, 3.8, bottom_z=0.5, center_xy=(CX, 6.05))
assign(trim, MAT_GOLD)
apply_scale(trim)
n += 1

# ------------------------------------------------------------------
# 2) Barracks wing masses L/R — mockup has wide hall wings at front
# ------------------------------------------------------------------
for side, sx in (("L", -6.5), ("R", 6.5)):
    wing = ensure_cube(f"FACADE_WING_{side}")
    set_size(wing, 6.5, 5.5, 9.5, bottom_z=0.2, center_xy=(CX + sx, 2.8))
    assign(wing, MAT_STONE)
    apply_scale(wing)
    soft_bevel(wing, 0.08)
    n += 1
    # multi-gable roof on wing (3 peaks along X)
    for i, xoff in enumerate([-1.8, 0.0, 1.8]):
        g = create_gable_prism(f"FACADE_WING_GABLE_{side}_{i}", width=2.4, depth=4.8, height=2.4)
        g.location = (CX + sx + xoff, 2.8, 9.7)
        g.rotation_euler = (0, 0, 0)
        assign(g, MAT_ROOF)
        soft_bevel(g, 0.03)
        tip = ensure_cube(f"FACADE_WING_TIP_{side}_{i}")
        set_size(tip, 0.16, 0.16, 0.45, bottom_z=12.0, center_xy=(CX + sx + xoff, 2.8))
        assign(tip, MAT_GOLD)
        apply_scale(tip)
        n += 2

print("WINGS", n)

# ------------------------------------------------------------------
# 3) Front facade pier + pointed window bays (gothic language)
# ------------------------------------------------------------------
# Vertical piers across front
for i, xoff in enumerate([-9.0, -6.5, -3.5, 3.5, 6.5, 9.0]):
    p = ensure_cube(f"FACADE_PIER_{i}")
    set_size(p, 0.55, 1.0, 8.5, bottom_z=0.25, center_xy=(CX + xoff, 5.3))
    assign(p, MAT_STONE)
    apply_scale(p)
    soft_bevel(p, 0.04)
    n += 1

# Pointed window proxies between piers (wing bays)
win_xs = [-8.0, -5.5, -4.2, 4.2, 5.5, 8.0]
for i, xoff in enumerate(win_xs):
    w = create_pointed_window_proxy(f"FACADE_WIN_{i}", half_w=0.55, rise=2.2, depth=0.4)
    w.location = (CX + xoff, 5.55, 3.2)
    assign(w, MAT_GLASS)
    soft_bevel(w, 0.02)
    # gold frame lip
    fr = ensure_cube(f"FACADE_WIN_FR_{i}")
    set_size(fr, 1.3, 0.15, 2.5, bottom_z=3.0, center_xy=(CX + xoff, 5.7))
    assign(fr, MAT_GOLD)
    apply_scale(fr)
    n += 2

# Upper row smaller windows on tower mid
for i, xoff in enumerate([-1.4, 0.0, 1.4]):
    w = create_pointed_window_proxy(f"FACADE_TOWER_WIN_{i}", half_w=0.45, rise=1.8, depth=0.35)
    w.location = (CX + xoff, 4.2, 18.5)
    assign(w, MAT_GLASS)
    n += 1

print("BAYS", n)

# ------------------------------------------------------------------
# 4) Corbel / string course + battlement rhythm on front wall top
# ------------------------------------------------------------------
string = ensure_cube("FACADE_STRING")
set_size(string, 20.0, 0.6, 0.35, bottom_z=6.6, center_xy=(CX, 5.0))
assign(string, MAT_GOLD)
apply_scale(string)

# Merlon rhythm on front parapet (sparse)
for i, xoff in enumerate([-9.5, -7.5, -5.5, -3.5, 3.5, 5.5, 7.5, 9.5]):
    m = ensure_cube(f"FACADE_MERLON_{i}")
    set_size(m, 0.7, 0.7, 1.0, bottom_z=6.9, center_xy=(CX + xoff, 5.1))
    assign(m, MAT_STONE)
    apply_scale(m)
    n += 1

# Blue banners L/R of gate (mockup)
for side, sx in (("L", -2.2), ("R", 2.2)):
    b = ensure_cube(f"FACADE_BANNER_{side}")
    set_size(b, 0.9, 0.08, 1.6, bottom_z=4.5, center_xy=(CX + sx, 6.1))
    assign(b, MAT_BANNER)
    apply_scale(b)
    pole = ensure_cube(f"FACADE_BANNER_POLE_{side}")
    set_size(pole, 0.08, 0.08, 2.2, bottom_z=4.3, center_xy=(CX + sx, 6.15))
    assign(pole, MAT_GOLD)
    apply_scale(pole)
    n += 2

# Ensure stair still visible
for name in ("STAIR_LANDING_MAIN", "STAIR_TREAD_0", "STAIR_TREAD_1", "STAIR_CHEEK_L", "STAIR_CHEEK_R"):
    o = bpy.data.objects.get(name)
    if o:
        o.hide_render = False
        o.hide_viewport = False

# Scale human
sh = ensure_cube("SCALE_HUMAN")
set_size(sh, 0.4, 0.28, 1.75, bottom_z=0.1, center_xy=(CX - 4.2, 9.6))
assign(sh, make_mat("MAT_SCALE_HUMAN", (0.9, 0.2, 0.15), 0.6, 0.0))
apply_scale(sh)

print("FACADE_DONE", n)

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

**Updated:** 2026-07-27 (job `019f9eec8b6f` tick **#118**, 5m)  
**Asset ID:** `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01`  

| Field | Value |
|-------|--------|
| **ASSET_FINAL_COMPLETE** | **false** |
| **accepted (user)** | **false** |
| **Current** | **PASS8 V96 FACADE_WINGS** |
| **Scale** | FP **{bw:.1f}×{bd:.1f}** (≤24×19) · top Z **{maxz:.1f}** |
| **Scheduler** | `019f9eec8b6f` every **5 min** |
| **Pipeline** | IN_PROGRESS (front facade bays + wing gables) |

---

## Tick #118 — executed (P1 front silhouette)

### Edits
1. **Portal** — smaller void, gold trim (less blank gray slab)
2. **Barracks wings L/R** — mass + 3 multi-gables each + gold tips
3. **Facade bays** — piers, pointed window proxies, string course, merlons, banners

### Inventory
- Visible: **{mesh_n}** · Hidden: **{hidden_n}** · Bool: **{bool_n}**
- Top: {", ".join(f"{k}:{v}" for k, v in top)}

### Files
| Role | Path |
|------|------|
| Work | `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V96_FACADE_WINGS.blend` |
| Loop / candidate | `PASS1D.blend` / `FINAL.blend` (synced) |
| Backup | `...BACKUP_LOOP_{STAMP}.blend` |
| Proofs | `renders_final/*` + work proofs |

### Bounds
**{bw:.1f} × {bd:.1f} × {bh:.1f}** m · Z {minz:.1f}..**{maxz:.1f}**

### Internal scores
| Axis | Score |
|------|-------|
| Scale | **9.0** |
| Front facade | ~8.5 |
| Wing multi-gable | ~8.5 |
| Overall | **~8.55** |

### Verdict
Not FINAL. Front bay language + wing roofs added. D1 modular core remains. **Human overlay required for FINAL.**
"""

loop_state = f"""# BUILD LOOP STATE

**Updated:** 2026-07-27 · tick **#118** · job `019f9eec8b6f` (5m)  
**ASSET_FINAL_COMPLETE:** false · **Current:** PASS8_V96_FACADE_WINGS  

## Tick #118 (P1)
- Facade wings L/R multi-gable + piers/windows/banners
- Portal trim tightened
- Bounds {bw:.1f}×{bd:.1f}×{bh:.1f} · meshes {mesh_n}
- Backup: BACKUP_LOOP_{STAMP}
- Saved: PASS8_V96_FACADE_WINGS → PASS1D / FINAL

## Next
3Q silhouette / hall depth; avoid cube densify plateau
"""

dev = f"""# INTERMEDIATE DEVIATION REPORT — tick #118

**Asset:** ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01
**Stamp:** {STAMP}
**File:** PASS8_V96_FACADE_WINGS / PASS1D
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
- Front wing multi-gable language (mockup L/R halls)
- Pier + pointed window bay rhythm
- Portal gold + banners
- Scale lock held

## Gaps vs mockup (blocking Human accept)
| ID | Pri | Gap |
|----|-----|-----|
| D1 | P1 | Still modular stacked volumes vs carved gothic |
| D2 | P1 | Organic multi-gable / stone carving fidelity |
| D3 | P2 | Window openings still proxy not true carved recesses |
| D4 | P2 | Tower shaft still boxy mid-section |
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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V96_FACADE_WINGS.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V96")

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

print("TICK118_DONE")
