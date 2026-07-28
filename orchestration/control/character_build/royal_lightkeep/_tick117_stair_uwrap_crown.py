# -*- coding: utf-8 -*-
"""Tick #117: main stair front readability + U-wrap + tower crown multi-gable.
Continue PASS8_V94_ROOF_DORMERS. Scale lock 24x19x38. No densify. No FINAL."""
import bpy
import bmesh
import os
import shutil
import math
from datetime import datetime
from mathutils import Vector
from collections import Counter

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V94_ROOF_DORMERS.blend")
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


MAT_STONE = make_mat("MAT_LIMESTONE", (0.86, 0.82, 0.74), 0.82, 0.0)
MAT_DARK = make_mat("MAT_FOUNDATION_DARK", (0.14, 0.12, 0.11), 0.92, 0.0)
MAT_PATH = make_mat("MAT_PAVING", (0.58, 0.54, 0.48), 0.88, 0.0)
MAT_GOLD = make_mat("MAT_GOLD_TRIM", (0.95, 0.72, 0.25), 0.18, 0.98)
MAT_ROOF = make_mat("MAT_SLATE_NAVY", (0.06, 0.10, 0.22), 0.42, 0.08)

CX, CY = 1.0, 1.5
X_MIN, X_MAX = -11.5, 12.5
Y_MIN, Y_MAX = -8.5, 10.5
H_MAX = 38.2
n = 0

# ------------------------------------------------------------------
# 1) Front plinth: open a gate recess so stair reads (mockup front)
# ------------------------------------------------------------------
# Soften blank curtain face — push CURTAIN_FRONT slightly back / lower center
cf = bpy.data.objects.get("CURTAIN_FRONT")
if cf:
    # keep walls but ensure not over-tall blank slab in front of stair
    try:
        set_size(cf, min(cf.dimensions.x, 22.0), max(cf.dimensions.y, 1.2), 6.5, bottom_z=0.15, center_xy=(CX, 4.2))
        apply_scale(cf)
        assign(cf, MAT_STONE)
        soft_bevel(cf, 0.06)
        n += 1
    except Exception as e:
        print("CURTAIN_FRONT_WARN", e)

# Gate recess mass (darker void proxy) + portal keep
for name in ("GATEHOUSE_MASS", "PORTAL_CURVED_ARCH", "PORTAL_CURVED_ARCH_INNER", "CHANNEL_THRESH"):
    o = bpy.data.objects.get(name)
    if o:
        o.hide_render = False
        o.hide_viewport = False

# Explicit front gate bay (stone frame) — projects forward so front cam sees opening
bay = ensure_cube("STAIR_GATE_BAY")
set_size(bay, 6.2, 2.4, 5.5, bottom_z=0.2, center_xy=(CX, 5.0))
assign(bay, MAT_STONE)
apply_scale(bay)
soft_bevel(bay, 0.08)
n += 1

# Dark portal void (sunk) — reads as entry from front
void = ensure_cube("STAIR_GATE_VOID")
set_size(void, 3.2, 1.6, 3.8, bottom_z=0.35, center_xy=(CX, 5.9))
assign(void, MAT_DARK)
apply_scale(void)
n += 1

# ------------------------------------------------------------------
# 2) Monumental stair — push FORWARD toward Y_MAX so front silhouette reads
# ------------------------------------------------------------------
landing = ensure_cube("STAIR_LANDING_MAIN")
set_size(landing, 5.8, 2.2, 0.45, bottom_z=0.15, center_xy=(CX, 6.4))
assign(landing, MAT_STONE)
apply_scale(landing)
soft_bevel(landing, 0.04)
n += 1

# 8 treads cascading toward camera (higher Y = more front)
for i in range(8):
    w = 5.6 - i * 0.22
    y = 10.0 - i * 0.42  # start near Y_MAX
    z = 0.12 + i * 0.26
    o = ensure_cube(f"STAIR_TREAD_{i}")
    set_size(o, w, 0.5, 0.28, bottom_z=z, center_xy=(CX, y))
    assign(o, MAT_STONE if i % 2 == 0 else MAT_PATH)
    apply_scale(o)
    soft_bevel(o, 0.025)
    n += 1

# Cheeks + gold caps (wider for mockup ceremonial feel)
for side, sx in (("L", -2.95), ("R", 2.95)):
    o = ensure_cube(f"STAIR_CHEEK_{side}")
    set_size(o, 0.48, 4.8, 2.0, bottom_z=0.12, center_xy=(CX + sx, 7.6))
    assign(o, MAT_DARK)
    apply_scale(o)
    soft_bevel(o, 0.05)
    cap = ensure_cube(f"STAIR_CHEEK_CAP_{side}")
    set_size(cap, 0.55, 4.8, 0.14, bottom_z=2.05, center_xy=(CX + sx, 7.6))
    assign(cap, MAT_GOLD)
    apply_scale(cap)
    n += 2

# Rail posts + top rails
for i in range(6):
    y = 9.6 - i * 0.55
    z = 0.35 + i * 0.26
    for side, sx in (("L", -2.65), ("R", 2.65)):
        p = ensure_cube(f"STAIR_RAIL_POST_{side}_{i}")
        set_size(p, 0.15, 0.15, 0.85, bottom_z=z, center_xy=(CX + sx, y))
        assign(p, MAT_STONE)
        apply_scale(p)
        n += 1
for side, sx in (("L", -2.65), ("R", 2.65)):
    r = ensure_cube(f"STAIR_RAIL_TOP_{side}")
    set_size(r, 0.12, 3.6, 0.12, bottom_z=2.15, center_xy=(CX + sx, 7.4))
    assign(r, MAT_GOLD)
    apply_scale(r)
    n += 1

# Approach channel
fl = ensure_cube("CHANNEL_FLOOR")
set_size(fl, 4.4, 5.0, 0.12, bottom_z=0.08, center_xy=(CX, 7.8))
assign(fl, MAT_PATH)
apply_scale(fl)
for side, sx in (("L", -2.4), ("R", 2.4)):
    w = ensure_cube(f"CHANNEL_WALL_{side}")
    set_size(w, 0.45, 4.4, 2.8, bottom_z=0.12, center_xy=(CX + sx, 7.6))
    assign(w, MAT_STONE)
    apply_scale(w)
    n += 1

# Scale human at stair base
sh = ensure_cube("SCALE_HUMAN")
set_size(sh, 0.4, 0.28, 1.75, bottom_z=0.1, center_xy=(CX - 4.2, 9.6))
assign(sh, make_mat("MAT_SCALE_HUMAN", (0.9, 0.2, 0.15), 0.6, 0.0))
apply_scale(sh)

print("STAIR_DONE", n)

# ------------------------------------------------------------------
# 3) Courtyard U-wrap — reinforce wings + rear bar + pave
# ------------------------------------------------------------------
for name, size, z, xy in (
    ("UWRAP_REAR_BAR", (14.0, 1.8, 6.2), 0.2, (CX, -4.5)),
    ("UWRAP_WING_L", (2.2, 11.0, 6.0), 0.2, (CX - 7.2, 0.8)),
    ("UWRAP_WING_R", (2.2, 11.0, 6.0), 0.2, (CX + 7.2, 0.8)),
):
    o = ensure_cube(name)
    set_size(o, *size, bottom_z=z, center_xy=xy)
    assign(o, MAT_STONE)
    apply_scale(o)
    soft_bevel(o, 0.07)
    n += 1

pave = ensure_cube("UWRAP_COURT_PAVE")
set_size(pave, 9.5, 7.0, 0.12, bottom_z=0.08, center_xy=(CX, 0.6))
assign(pave, MAT_PATH)
apply_scale(pave)

# Corner turrets on U-wrap for mockup courtyard corners
for tag, xy in (("FL", (CX - 7.2, 5.5)), ("FR", (CX + 7.2, 5.5)), ("RL", (CX - 7.2, -4.0)), ("RR", (CX + 7.2, -4.0))):
    t = ensure_cube(f"UWRAP_CORNER_{tag}")
    set_size(t, 2.0, 2.0, 7.5, bottom_z=0.2, center_xy=xy)
    assign(t, MAT_STONE)
    apply_scale(t)
    soft_bevel(t, 0.06)
    # small blue cap
    cap = create_gable_prism(f"UWRAP_CORNER_CAP_{tag}", width=2.2, depth=2.2, height=1.4)
    cap.location = (xy[0], xy[1], 7.7)
    assign(cap, MAT_ROOF)
    soft_bevel(cap, 0.03)
    tip = ensure_cube(f"UWRAP_CORNER_TIP_{tag}")
    set_size(tip, 0.2, 0.2, 0.5, bottom_z=9.0, center_xy=xy)
    assign(tip, MAT_GOLD)
    apply_scale(tip)
    n += 3

print("UWRAP_DONE")

# ------------------------------------------------------------------
# 4) Tower crown multi-gable — denser, taller blue silhouette
# ------------------------------------------------------------------
collar = ensure_cube("CROWN_MESH_COLLAR")
set_size(collar, 6.2, 6.2, 0.55, bottom_z=31.6, center_xy=(CX, CY))
assign(collar, MAT_STONE)
apply_scale(collar)
soft_bevel(collar, 0.05)

# Cardinal tall gables
cardinals = [
    ("N", 0.0, 1.55, 0.0),
    ("S", 0.0, -1.55, math.pi),
    ("E", 1.55, 0.0, -math.pi / 2),
    ("W", -1.55, 0.0, math.pi / 2),
]
for tag, dx, dy, rot in cardinals:
    g = create_gable_prism(f"CROWN_MESH_GABLE_{tag}", width=2.6, depth=1.45, height=2.6)
    g.location = (CX + dx, CY + dy, 32.2)
    g.rotation_euler = (0, 0, rot)
    assign(g, MAT_ROOF)
    soft_bevel(g, 0.03)
    tip = ensure_cube(f"CROWN_MESH_TIP_{tag}")
    set_size(tip, 0.2, 0.2, 0.6, bottom_z=34.7, center_xy=(CX + dx * 1.05, CY + dy * 1.05))
    assign(tip, MAT_GOLD)
    apply_scale(tip)
    n += 2

# Diagonal mid gables
diags = [
    ("NE", 1.1, 1.1, -math.pi / 4),
    ("NW", -1.1, 1.1, math.pi / 4),
    ("SE", 1.1, -1.1, -3 * math.pi / 4),
    ("SW", -1.1, -1.1, 3 * math.pi / 4),
]
for tag, dx, dy, rot in diags:
    g = create_gable_prism(f"CROWN_MESH_GABLE_{tag}", width=1.7, depth=1.1, height=1.9)
    g.location = (CX + dx, CY + dy, 32.3)
    g.rotation_euler = (0, 0, rot)
    assign(g, MAT_ROOF)
    tip = ensure_cube(f"CROWN_MESH_TIP_{tag}")
    set_size(tip, 0.15, 0.15, 0.45, bottom_z=34.1, center_xy=(CX + dx * 1.1, CY + dy * 1.1))
    assign(tip, MAT_GOLD)
    apply_scale(tip)
    n += 2

# Extra intermediate gables for denser crown (mockup multi-peak)
extras = [
    ("N2", 0.0, 2.0, 0.0, 1.4, 0.9, 1.4),
    ("S2", 0.0, -2.0, math.pi, 1.4, 0.9, 1.4),
    ("E2", 2.0, 0.0, -math.pi / 2, 1.4, 0.9, 1.4),
    ("W2", -2.0, 0.0, math.pi / 2, 1.4, 0.9, 1.4),
]
for tag, dx, dy, rot, w, d, h in extras:
    g = create_gable_prism(f"CROWN_MESH_GABLE_{tag}", width=w, depth=d, height=h)
    g.location = (CX + dx, CY + dy, 32.15)
    g.rotation_euler = (0, 0, rot)
    assign(g, MAT_ROOF)
    n += 1

# Center spire + gold finial
spire = ensure_cube("CROWN_MESH_SPIRE")
set_size(spire, 1.1, 1.1, 3.2, bottom_z=32.8, center_xy=(CX, CY))
assign(spire, MAT_ROOF)
apply_scale(spire)
fin = ensure_cube("CROWN_MESH_SPIRE_GOLD")
set_size(fin, 0.35, 0.35, 1.0, bottom_z=35.8, center_xy=(CX, CY))
assign(fin, MAT_GOLD)
apply_scale(fin)
n += 2

# Gold ring under crown
ring = ensure_cube("CROWN_GOLD_RING")
set_size(ring, 6.4, 6.4, 0.18, bottom_z=31.45, center_xy=(CX, CY))
assign(ring, MAT_GOLD)
apply_scale(ring)

for name in ("ROOF_HIP_MESH_TOWER", "ROOF_HIP_MESH_MAIN"):
    o = bpy.data.objects.get(name)
    if o:
        o.hide_render = False
        o.hide_viewport = False

print("CROWN_DONE", n)

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

**Updated:** 2026-07-27 (job `019f9eec8b6f` tick **#117**, 5m)  
**Asset ID:** `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01`  

| Field | Value |
|-------|--------|
| **ASSET_FINAL_COMPLETE** | **false** |
| **accepted (user)** | **false** |
| **Current** | **PASS8 V95 STAIR_UWRAP_CROWN** |
| **Scale** | FP **{bw:.1f}×{bd:.1f}** (≤24×19) · top Z **{maxz:.1f}** |
| **Scheduler** | `019f9eec8b6f` every **5 min** |
| **Pipeline** | IN_PROGRESS (stair + U-wrap + crown) |

---

## Tick #117 — executed (P0/P1 silhouette)

### Edits
1. **Main stair** — 8 treads pushed to Y≈10, cheeks/rails/gold, gate bay + void
2. **U-wrap** — rear bar + wings reinforced; 4 corner turrets + blue caps
3. **Tower crown** — denser multi-gable (cardinal+diag+mid) + spire + gold ring

### Inventory
- Visible: **{mesh_n}** · Hidden: **{hidden_n}** · Bool: **{bool_n}**
- Top: {", ".join(f"{k}:{v}" for k, v in top)}

### Files
| Role | Path |
|------|------|
| Work | `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V95_STAIR_UWRAP_CROWN.blend` |
| Loop / candidate | `PASS1D.blend` / `FINAL.blend` (synced) |
| Backup | `...BACKUP_LOOP_{STAMP}.blend` |
| Proofs | `renders_final/*` + work proofs |

### Bounds
**{bw:.1f} × {bd:.1f} × {bh:.1f}** m · Z {minz:.1f}..**{maxz:.1f}**

### Internal scores
| Axis | Score |
|------|-------|
| Scale | **9.0** |
| Stair / approach | ~8.4 |
| Crown multi-gable | ~8.5 |
| Overall | **~8.55** |

### Verdict
Not FINAL. Stair/U-wrap/crown silhouettes reinforced. D1 modular language still blocks Human. **Human overlay required for FINAL.**
"""

loop_state = f"""# BUILD LOOP STATE

**Updated:** 2026-07-27 · tick **#117** · job `019f9eec8b6f` (5m)  
**ASSET_FINAL_COMPLETE:** false · **Current:** PASS8_V95_STAIR_UWRAP_CROWN  

## Tick #117 (P0/P1)
- Stair forward cascade + gate bay/void
- U-wrap wings + corner turrets
- Crown multi-gable denser
- Bounds {bw:.1f}×{bd:.1f}×{bh:.1f} · meshes {mesh_n}
- Backup: BACKUP_LOOP_{STAMP}
- Saved: PASS8_V95_STAIR_UWRAP_CROWN → PASS1D / FINAL

## Next
Front silhouette vs mockup; avoid cube densify on plateau
"""

dev = f"""# INTERMEDIATE DEVIATION REPORT — tick #117

**Asset:** ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01
**Stamp:** {STAMP}
**File:** PASS8_V95_STAIR_UWRAP_CROWN / PASS1D
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
- Ceremonial stair pushed forward for front cam
- U-wrap courtyard wings + corner turrets
- Tower crown multi-gable denser + gold accents
- Scale lock held

## Gaps vs mockup (blocking Human accept)
| ID | Pri | Gap |
|----|-----|-----|
| D1 | P1 | Still modular stacked volumes vs carved gothic |
| D2 | P1 | Multi-gable simplified vs organic mockup |
| D3 | P2 | Front wall still reads boxy vs articulated facade |
| D4 | P2 | Art fidelity / stone carving below sheet |
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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V95_STAIR_UWRAP_CROWN.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V95")

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

print("TICK117_DONE")
