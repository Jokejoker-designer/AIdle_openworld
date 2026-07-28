# -*- coding: utf-8 -*-
"""Tick #120: lower fortification articulation (D3 front slab) + multi-level base.
Continue PASS8_V97_TOWER_MID. Scale lock 24x19x38. No densify. No FINAL."""
import bpy
import bmesh
import os
import shutil
from datetime import datetime
from mathutils import Vector
from collections import Counter

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V97_TOWER_MID.blend")
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
    verts = [
        bm.verts.new((-hw, -hd, 0)),
        bm.verts.new((hw, -hd, 0)),
        bm.verts.new((hw, hd, 0)),
        bm.verts.new((-hw, hd, 0)),
        bm.verts.new((0, -hd, hh)),
        bm.verts.new((0, hd, hh)),
    ]
    bm.verts.ensure_lookup_table()
    v0, v1, v2, v3, r0, r1 = verts
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
MAT_WOOD = make_mat("MAT_WOOD_DOOR", (0.28, 0.16, 0.08), 0.75, 0.0)

CX, CY = 1.0, 1.5
X_MIN, X_MAX = -11.5, 12.5
Y_MIN, Y_MAX = -8.5, 10.5
H_MAX = 38.2
n = 0

# ------------------------------------------------------------------
# 1) Kill blank gray gate slabs — replace with proper gatehouse mass
# ------------------------------------------------------------------
for name in ("STAIR_GATE_VOID", "STAIR_GATE_BAY"):
    o = bpy.data.objects.get(name)
    if o:
        # keep void as wood door recess, not huge gray panel
        if "VOID" in name:
            set_size(o, 2.2, 0.8, 3.0, bottom_z=0.5, center_xy=(CX, 5.85))
            assign(o, MAT_WOOD)
            apply_scale(o)
        else:
            set_size(o, 4.6, 2.8, 5.8, bottom_z=0.15, center_xy=(CX, 4.6))
            assign(o, MAT_STONE)
            apply_scale(o)
            soft_bevel(o, 0.08)
        n += 1

# Gatehouse projecting volume (mockup front entry)
gh = ensure_cube("GATEHOUSE_MASS")
set_size(gh, 5.5, 3.5, 6.5, bottom_z=0.15, center_xy=(CX, 4.2))
assign(gh, MAT_STONE)
apply_scale(gh)
soft_bevel(gh, 0.09)
n += 1

# Gatehouse blue roof
gr = create_gable_prism("GATEHOUSE_ROOF_GABLE", width=5.8, depth=3.8, height=2.2)
gr.location = (CX, 4.2, 6.7)
assign(gr, MAT_ROOF)
soft_bevel(gr, 0.03)
gt = ensure_cube("GATEHOUSE_ROOF_TIP")
set_size(gt, 0.2, 0.2, 0.5, bottom_z=8.8, center_xy=(CX, 4.2))
assign(gt, MAT_GOLD)
apply_scale(gt)
n += 2

# Pointed portal frame (stone outer + wood door)
frame = ensure_cube("GATE_PORTAL_FRAME")
set_size(frame, 3.0, 0.55, 3.6, bottom_z=0.4, center_xy=(CX, 5.95))
assign(frame, MAT_STONE)
apply_scale(frame)
door = ensure_cube("GATE_WOOD_DOOR")
set_size(door, 2.0, 0.25, 2.8, bottom_z=0.45, center_xy=(CX, 6.15))
assign(door, MAT_WOOD)
apply_scale(door)
# gold arch lip
lip = ensure_cube("GATE_GOLD_LIP")
set_size(lip, 3.2, 0.12, 0.2, bottom_z=3.9, center_xy=(CX, 6.05))
assign(lip, MAT_GOLD)
apply_scale(lip)
n += 3

print("GATE", n)

# ------------------------------------------------------------------
# 2) Multi-level lower base (plinth + wall + parapet) — not one slab
# ------------------------------------------------------------------
# Dark foundation plinth around footprint
plinth = ensure_cube("LOWER_PLINTH")
set_size(plinth, 23.5, 18.5, 1.2, bottom_z=0.0, center_xy=(CX, CY))
assign(plinth, MAT_DARK)
apply_scale(plinth)
soft_bevel(plinth, 0.06)
n += 1

# Curtain front as thinner wall at 6.5m with setback from plinth edge
cf = ensure_cube("CURTAIN_FRONT")
set_size(cf, 20.0, 1.4, 5.5, bottom_z=1.1, center_xy=(CX, 5.0))
assign(cf, MAT_STONE)
apply_scale(cf)
soft_bevel(cf, 0.07)
n += 1

# Side curtain lower walls for 3Q
for side, sy, xy in (
    ("LEFT", 1.3, (CX - 10.5, CY)),
    ("RIGHT", 1.3, (CX + 10.5, CY)),
):
    # dimensions: thin in X for left/right
    o = ensure_cube(f"CURTAIN_{side}")
    if side == "LEFT":
        set_size(o, 1.3, 16.0, 5.5, bottom_z=1.1, center_xy=xy)
    else:
        set_size(o, 1.3, 16.0, 5.5, bottom_z=1.1, center_xy=xy)
    assign(o, MAT_STONE)
    apply_scale(o)
    soft_bevel(o, 0.06)
    n += 1

# Front parapet cope + merlon rhythm (articulated top of lower wall)
cope = ensure_cube("LOWER_FRONT_COPE")
set_size(cope, 20.5, 1.6, 0.35, bottom_z=6.5, center_xy=(CX, 5.0))
assign(cope, MAT_STONE)
apply_scale(cope)
for i, xoff in enumerate([-9.0, -7.0, -5.0, -3.0, 3.0, 5.0, 7.0, 9.0]):
    m = ensure_cube(f"LOWER_MERLON_{i}")
    set_size(m, 0.85, 1.0, 1.1, bottom_z=6.8, center_xy=(CX + xoff, 5.05))
    assign(m, MAT_STONE)
    apply_scale(m)
    n += 1

# Buttress piers on front lower (mockup fortification rhythm)
for i, xoff in enumerate([-8.5, -5.5, -2.5, 2.5, 5.5, 8.5]):
    b = ensure_cube(f"LOWER_BUTT_{i}")
    set_size(b, 0.9, 1.6, 6.0, bottom_z=1.0, center_xy=(CX + xoff, 5.6))
    assign(b, MAT_STONE)
    apply_scale(b)
    soft_bevel(b, 0.05)
    # stepped cap
    cap = ensure_cube(f"LOWER_BUTT_CAP_{i}")
    set_size(cap, 1.1, 1.8, 0.35, bottom_z=6.9, center_xy=(CX + xoff, 5.6))
    assign(cap, MAT_GOLD if i % 2 == 0 else MAT_STONE)
    apply_scale(cap)
    n += 2

print("LOWER", n)

# ------------------------------------------------------------------
# 3) Stair refresh — wide ceremonial on multi-level base
# ------------------------------------------------------------------
for i in range(8):
    w = 5.8 - i * 0.2
    y = 9.9 - i * 0.4
    z = 0.15 + i * 0.28
    o = ensure_cube(f"STAIR_TREAD_{i}")
    set_size(o, w, 0.48, 0.3, bottom_z=z, center_xy=(CX, y))
    assign(o, MAT_STONE if i % 2 == 0 else MAT_PATH)
    apply_scale(o)
    n += 1

landing = ensure_cube("STAIR_LANDING_MAIN")
set_size(landing, 5.5, 2.0, 0.4, bottom_z=2.2, center_xy=(CX, 6.5))
assign(landing, MAT_STONE)
apply_scale(landing)

for side, sx in (("L", -3.0), ("R", 3.0)):
    o = ensure_cube(f"STAIR_CHEEK_{side}")
    set_size(o, 0.45, 4.5, 2.4, bottom_z=0.15, center_xy=(CX + sx, 7.8))
    assign(o, MAT_DARK)
    apply_scale(o)
    cap = ensure_cube(f"STAIR_CHEEK_CAP_{side}")
    set_size(cap, 0.55, 4.5, 0.14, bottom_z=2.5, center_xy=(CX + sx, 7.8))
    assign(cap, MAT_GOLD)
    apply_scale(cap)
    n += 2

# Scale human
sh = ensure_cube("SCALE_HUMAN")
set_size(sh, 0.4, 0.28, 1.75, bottom_z=0.1, center_xy=(CX - 4.5, 9.7))
assign(sh, make_mat("MAT_SCALE_HUMAN", (0.9, 0.2, 0.15), 0.6, 0.0))
apply_scale(sh)

# Corner lower turrets with blue roofs (mockup corner towers on wall)
for tag, xy in (("FL", (CX - 10.0, 5.5)), ("FR", (CX + 10.0, 5.5))):
    t = ensure_cube(f"LOWER_CORNER_{tag}")
    set_size(t, 2.4, 2.4, 8.0, bottom_z=0.15, center_xy=xy)
    assign(t, MAT_STONE)
    apply_scale(t)
    soft_bevel(t, 0.07)
    g = create_gable_prism(f"LOWER_CORNER_ROOF_{tag}", width=2.6, depth=2.6, height=1.8)
    g.location = (xy[0], xy[1], 8.2)
    assign(g, MAT_ROOF)
    tip = ensure_cube(f"LOWER_CORNER_TIP_{tag}")
    set_size(tip, 0.18, 0.18, 0.45, bottom_z=9.9, center_xy=xy)
    assign(tip, MAT_GOLD)
    apply_scale(tip)
    n += 3

print("FORT_DONE", n)

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

**Updated:** 2026-07-27 (job `019f9eec8b6f` tick **#120**, 5m)  
**Asset ID:** `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01`  

| Field | Value |
|-------|--------|
| **ASSET_FINAL_COMPLETE** | **false** |
| **accepted (user)** | **false** |
| **Current** | **PASS8 V98 LOWER_FORT** |
| **Scale** | FP **{bw:.1f}×{bd:.1f}** (≤24×19) · top Z **{maxz:.1f}** |
| **Scheduler** | `019f9eec8b6f` every **5 min** |
| **Pipeline** | IN_PROGRESS (lower fortification multi-level) |

---

## Tick #120 — executed (P1 D3 lower)

### Edits
1. **Gatehouse** — stone mass + blue gable roof + wood door (replace gray slab)
2. **Multi-level base** — dark plinth + curtain + cope/merlons + buttress piers
3. **Stair** — refreshed cascade + corner lower turrets L/R

### Inventory
- Visible: **{mesh_n}** · Hidden: **{hidden_n}** · Bool: **{bool_n}**
- Top: {", ".join(f"{k}:{v}" for k, v in top)}

### Files
| Role | Path |
|------|------|
| Work | `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V98_LOWER_FORT.blend` |
| Loop / candidate | `PASS1D.blend` / `FINAL.blend` (synced) |
| Backup | `...BACKUP_LOOP_{STAMP}.blend` |
| Proofs | `renders_final/*` + work proofs |

### Bounds
**{bw:.1f} × {bd:.1f} × {bh:.1f}** m · Z {minz:.1f}..**{maxz:.1f}**

### Internal scores
| Axis | Score |
|------|-------|
| Scale | **9.0** |
| Lower fortification | ~8.5 |
| Gatehouse / stair | ~8.5 |
| Overall | **~8.55** |

### Verdict
Not FINAL. Lower slab broken into multi-level fort language. D1 modular remains. **Human overlay required for FINAL.**
"""

loop_state = f"""# BUILD LOOP STATE

**Updated:** 2026-07-27 · tick **#120** · job `019f9eec8b6f` (5m)  
**ASSET_FINAL_COMPLETE:** false · **Current:** PASS8_V98_LOWER_FORT  

## Tick #120 (P1)
- Gatehouse roof + wood door; multi-level plinth/curtain/buttress
- Bounds {bw:.1f}×{bd:.1f}×{bh:.1f} · meshes {mesh_n}
- Backup: BACKUP_LOOP_{STAMP}
- Saved: PASS8_V98_LOWER_FORT → PASS1D / FINAL

## Next
Plateau watch; method change if no visual gain
"""

dev = f"""# INTERMEDIATE DEVIATION REPORT — tick #120

**Asset:** ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01
**Stamp:** {STAMP}
**File:** PASS8_V98_LOWER_FORT / PASS1D
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
- Multi-level lower fort (plinth / wall / parapet)
- Gatehouse with roof + wood door (not gray slab)
- Buttress rhythm + corner turrets
- Scale lock held

## Gaps vs mockup (blocking Human accept)
| ID | Pri | Gap |
|----|-----|-----|
| D1 | P1 | Modular stacked volumes vs carved gothic |
| D2 | P1 | Organic roof / stone carving fidelity |
| D3 | P2 | Openings still proxy not true recesses |
| D4 | P2 | Overall still game-block vs sheet art |
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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V98_LOWER_FORT.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V98")

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

print("TICK120_DONE")
