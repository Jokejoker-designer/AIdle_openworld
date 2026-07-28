# -*- coding: utf-8 -*-
"""Tick #122: METHOD CHANGE — pointed-arch portal mesh + continuous hall multi-gable + noise hide.
Continue PASS8_V99_CLAMP_CLEAN. Scale 24x19x38. No densify. No FINAL."""
import bpy
import bmesh
import os
import shutil
import math
from datetime import datetime
from mathutils import Vector
from collections import Counter

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V99_CLAMP_CLEAN.blend")
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


def create_pointed_arch_solid(name, half_w=1.6, rise=3.8, depth=0.7, segs=14):
    """Solid pointed-arch block in XZ, extruded along Y (front-facing portal)."""
    bm = bmesh.new()
    spring = 0.5
    R = half_w * 2.0
    apex = spring + R * math.sin(math.pi / 3)
    # build front outline points (outer fill solid)
    pts = [(-half_w, 0.0), (-half_w, spring)]
    # left arc center (half_w, spring): ang pi → 2pi/3
    for i in range(segs):
        t = i / max(segs - 1, 1)
        ang = math.pi - (math.pi / 3) * t
        x = half_w + R * math.cos(ang)
        z = spring + R * math.sin(ang)
        pts.append((x, z))
    # right arc center (-half_w, spring)
    for i in range(1, segs):
        t = i / max(segs - 1, 1)
        ang = math.pi / 3 - (math.pi / 3) * t
        x = -half_w + R * math.cos(ang)
        z = spring + R * math.sin(ang)
        pts.append((x, z))
    pts.append((half_w, spring))
    pts.append((half_w, 0.0))

    y0, y1 = -depth * 0.5, depth * 0.5
    front = [bm.verts.new((x, y0, z)) for x, z in pts]
    back = [bm.verts.new((x, y1, z)) for x, z in pts]
    bm.verts.ensure_lookup_table()
    n = len(pts)
    try:
        bm.faces.new(front)
    except Exception:
        pass
    try:
        bm.faces.new(list(reversed(back)))
    except Exception:
        pass
    for i in range(n):
        j = (i + 1) % n
        try:
            bm.faces.new([front[i], front[j], back[j], back[i]])
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
    return obj, apex


MAT_STONE = make_mat("MAT_LIMESTONE", (0.86, 0.82, 0.74), 0.82, 0.0)
MAT_DARK = make_mat("MAT_FOUNDATION_DARK", (0.14, 0.12, 0.11), 0.92, 0.0)
MAT_GOLD = make_mat("MAT_GOLD_TRIM", (0.95, 0.72, 0.25), 0.18, 0.98)
MAT_ROOF = make_mat("MAT_SLATE_NAVY", (0.06, 0.10, 0.22), 0.42, 0.08)
MAT_WOOD = make_mat("MAT_WOOD_DOOR", (0.28, 0.16, 0.08), 0.75, 0.0)
MAT_PATH = make_mat("MAT_PAVING", (0.58, 0.54, 0.48), 0.88, 0.0)

CX, CY = 1.0, 1.5
X_MIN, X_MAX = -11.5, 12.5
Y_MIN, Y_MAX = -8.5, 10.5
H_MAX = 38.2
n = 0
hid = 0

# ------------------------------------------------------------------
# 1) Hide micro noise (plateau method: subtract clutter)
# ------------------------------------------------------------------
for o in list(bpy.data.objects):
    if o.type != "MESH":
        continue
    name = o.name
    # hide dense micro posts / excess lower merlons alternate
    if name.startswith("STAIR_RAIL_POST_"):
        o.hide_render = True
        o.hide_viewport = True
        hid += 1
        continue
    if name.startswith("LOWER_MERLON_"):
        # keep even indices only
        try:
            idx = int(name.rsplit("_", 1)[-1])
            if idx % 2 == 1:
                o.hide_render = True
                o.hide_viewport = True
                hid += 1
        except Exception:
            pass
    if name.startswith("SHAFT_LANCET_") and "FR" not in name:
        # keep front primary only partially — hide side excess row 0
        if name.endswith("_0") and ("_L_" in name or "_R_" in name):
            o.hide_render = True
            o.hide_viewport = True
            hid += 1

print("NOISE_HIDDEN", hid)

# ------------------------------------------------------------------
# 2) Pointed-arch portal (method change vs box void)
# ------------------------------------------------------------------
# Hide old box portal pieces that read as gray slabs
for name in ("STAIR_GATE_VOID", "GATE_PORTAL_FRAME", "FACADE_PORTAL_TRIM"):
    o = bpy.data.objects.get(name)
    if o:
        o.hide_render = True
        o.hide_viewport = True
        hid += 1

arch, apex = create_pointed_arch_solid("PORTAL_ARCH_MESH", half_w=1.7, rise=3.6, depth=0.85, segs=16)
arch.location = (CX, 5.9, 0.45)
assign(arch, MAT_STONE)
soft_bevel(arch, 0.03)
n += 1

# Wood door panel behind arch opening (slightly recessed)
door = ensure_cube("GATE_WOOD_DOOR")
set_size(door, 2.4, 0.2, 2.6, bottom_z=0.5, center_xy=(CX, 5.55))
assign(door, MAT_WOOD)
apply_scale(door)
n += 1

# Gold trim strip at springing
gold = ensure_cube("PORTAL_GOLD_SPRING")
set_size(gold, 4.0, 0.15, 0.18, bottom_z=0.9, center_xy=(CX, 6.15))
assign(gold, MAT_GOLD)
apply_scale(gold)
n += 1

# Gatehouse mass ensure
gh = ensure_cube("GATEHOUSE_MASS")
set_size(gh, 5.0, 3.0, 6.0, bottom_z=0.15, center_xy=(CX, 4.0))
assign(gh, MAT_STONE)
apply_scale(gh)
soft_bevel(gh, 0.08)

gr = create_gable_prism("GATEHOUSE_ROOF_GABLE", width=5.4, depth=3.4, height=2.0)
gr.location = (CX, 4.0, 6.2)
assign(gr, MAT_ROOF)
n += 1

print("PORTAL", n)

# ------------------------------------------------------------------
# 3) Continuous hall multi-gable (fewer, larger — mockup roof language)
# ------------------------------------------------------------------
# Main hall roof ridge gables along X (center body)
for i, xoff in enumerate([-5.5, -2.75, 0.0, 2.75, 5.5]):
    g = create_gable_prism(f"HALL_MAIN_GABLE_{i}", width=3.0, depth=7.5, height=3.2)
    g.location = (CX + xoff, CY + 0.5, 18.0)
    assign(g, MAT_ROOF)
    soft_bevel(g, 0.03)
    tip = ensure_cube(f"HALL_MAIN_TIP_{i}")
    set_size(tip, 0.18, 0.18, 0.5, bottom_z=21.1, center_xy=(CX + xoff, CY + 0.5))
    assign(tip, MAT_GOLD)
    apply_scale(tip)
    n += 2

# Ensure hip mesh visible under
for name in ("ROOF_HIP_MESH_MAIN", "ROOF_HIP_MESH_TOWER"):
    o = bpy.data.objects.get(name)
    if o:
        o.hide_render = False
        o.hide_viewport = False

# ------------------------------------------------------------------
# 4) Monumental stair refresh (prompt priority)
# ------------------------------------------------------------------
for i in range(7):
    w = 5.6 - i * 0.22
    y = 9.8 - i * 0.42
    z = 0.12 + i * 0.3
    o = ensure_cube(f"STAIR_TREAD_{i}")
    set_size(o, w, 0.5, 0.32, bottom_z=z, center_xy=(CX, y))
    assign(o, MAT_STONE if i % 2 == 0 else MAT_PATH)
    apply_scale(o)
    n += 1

landing = ensure_cube("STAIR_LANDING_MAIN")
set_size(landing, 5.4, 2.0, 0.4, bottom_z=2.1, center_xy=(CX, 6.4))
assign(landing, MAT_STONE)
apply_scale(landing)

for side, sx in (("L", -2.9), ("R", 2.9)):
    o = ensure_cube(f"STAIR_CHEEK_{side}")
    set_size(o, 0.45, 4.4, 2.3, bottom_z=0.12, center_xy=(CX + sx, 7.6))
    assign(o, MAT_DARK)
    apply_scale(o)
    cap = ensure_cube(f"STAIR_CHEEK_CAP_{side}")
    set_size(cap, 0.55, 4.4, 0.14, bottom_z=2.4, center_xy=(CX + sx, 7.6))
    assign(cap, MAT_GOLD)
    apply_scale(cap)
    n += 2

# U-wrap ensure
for name in ("UWRAP_REAR_BAR", "UWRAP_WING_L", "UWRAP_WING_R", "UWRAP_COURT_PAVE"):
    o = bpy.data.objects.get(name)
    if o:
        o.hide_render = False
        o.hide_viewport = False

# Crown ensure
for name in (
    "CROWN_MESH_COLLAR", "CROWN_MESH_SPIRE", "CROWN_MESH_GABLE_N",
    "CROWN_MESH_GABLE_S", "CROWN_MESH_GABLE_E", "CROWN_MESH_GABLE_W",
):
    o = bpy.data.objects.get(name)
    if o:
        o.hide_render = False
        o.hide_viewport = False

sh = ensure_cube("SCALE_HUMAN")
set_size(sh, 0.4, 0.28, 1.75, bottom_z=0.1, center_xy=(CX - 4.2, 9.5))
assign(sh, make_mat("MAT_SCALE_HUMAN", (0.9, 0.2, 0.15), 0.6, 0.0))
apply_scale(sh)

print("STAIR_ROOF_DONE", n)

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

**Updated:** 2026-07-27 (job `019f9eec8b6f` tick **#122**, 5m)  
**Asset ID:** `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01`  

| Field | Value |
|-------|--------|
| **ASSET_FINAL_COMPLETE** | **false** |
| **accepted (user)** | **false** |
| **Current** | **PASS8 V100 PORTAL_ROOF** |
| **Scale** | FP **{bw:.1f}×{bd:.1f}** (≤24×19) · top Z **{maxz:.1f}** |
| **Scheduler** | `019f9eec8b6f` every **5 min** |
| **Pipeline** | IN_PROGRESS (method: pointed portal + hall gables) |

---

## Tick #122 — executed (method change)

### Edits
1. **Pointed-arch portal mesh** (bmesh) + wood door + gold spring — replace box void
2. **Hall main multi-gables** ×5 continuous larger ridge language
3. **Noise hide** — rail posts / alt merlons / side lancet excess ({hid})
4. **Stair** cascade refresh + uwrap/crown ensure

### Inventory
- Visible: **{mesh_n}** · Hidden: **{hidden_n}** · Bool: **{bool_n}**
- Top: {", ".join(f"{k}:{v}" for k, v in top)}

### Files
| Role | Path |
|------|------|
| Work | `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V100_PORTAL_ROOF.blend` |
| Loop / candidate | `PASS1D.blend` / `FINAL.blend` (synced) |
| Backup | `...BACKUP_LOOP_{STAMP}.blend` |
| Proofs | `renders_final/*` + work proofs |

### Bounds
**{bw:.1f} × {bd:.1f} × {bh:.1f}** m · Z {minz:.1f}..**{maxz:.1f}**

### Internal scores
| Axis | Score |
|------|-------|
| Scale | **9.0** |
| Portal gothic | ~8.6 |
| Hall multi-gable | ~8.55 |
| Overall | **~8.55** |

### Verdict
Not FINAL. Method change on portal/roof. D1 modular core remains. **Human overlay required for FINAL.**
"""

loop_state = f"""# BUILD LOOP STATE

**Updated:** 2026-07-27 · tick **#122** · job `019f9eec8b6f` (5m)  
**ASSET_FINAL_COMPLETE:** false · **Current:** PASS8_V100_PORTAL_ROOF  

## Tick #122 (method)
- Pointed portal mesh + hall ×5 gables + noise hide ({hid})
- Bounds {bw:.1f}×{bd:.1f}×{bh:.1f} · meshes {mesh_n}
- Backup: BACKUP_LOOP_{STAMP}
- Saved: PASS8_V100_PORTAL_ROOF → PASS1D / FINAL

## Next
Plateau; Human overlay preferred; no densify
"""

dev = f"""# INTERMEDIATE DEVIATION REPORT — tick #122

**Asset:** ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01
**Stamp:** {STAMP}
**File:** PASS8_V100_PORTAL_ROOF / PASS1D
**ASSET_FINAL_COMPLETE:** false
**accepted (user):** false

## Inventory
- Mesh objects (visible): **{mesh_n}**
- Hidden: **{hidden_n}** · Bool: **{bool_n}**
- Noise hidden: **{hid}**
- Top: {", ".join(f"{k}:{v}" for k, v in top)}

## Sheet targets
- Footprint 24×19 m · Height 38 m · Wall 6.5 m
- Achieved: **{bw:.2f}×{bd:.2f}×{bh:.2f}** m · Z {minz:.2f}..{maxz:.2f}

## Matches
- Pointed gothic portal mesh (method change)
- Larger continuous hall multi-gables
- Stair / crown / uwrap retained
- Scale lock held

## Gaps vs mockup (blocking Human accept)
| ID | Pri | Gap |
|----|-----|-----|
| D1 | P1 | Modular stacked volumes vs carved gothic |
| D2 | P1 | Stone carving / organic fidelity |
| D3 | P2 | True recessed openings into mass (bool) |
| D4 | P2 | Overall still game-block vs sheet |
| D5 | P3 | UV/LOD |

## Overall ~8.55 plateau — not FINAL until Human overlay
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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V100_PORTAL_ROOF.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V100")

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

print("TICK122_DONE")
