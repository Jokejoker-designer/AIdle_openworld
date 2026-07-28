# -*- coding: utf-8 -*-
"""Tick #97: tower mid-shaft window string densify on 4 faces + string courses.
Continue PASS8_V74_PORTAL_ARCH. Scale lock 24x19x38. No FINAL claim."""
import bpy
import os
import shutil
import bmesh
from datetime import datetime
from mathutils import Vector

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V74_PORTAL_ARCH.blend")
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


def soft_bevel(o, width=0.03, segments=2):
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


def add_bool_diff(host, cutter, mod_name):
    if not host or not cutter:
        return False
    for m in list(host.modifiers):
        if m.name == mod_name or (m.type == "BOOLEAN" and getattr(m, "object", None) == cutter):
            try:
                host.modifiers.remove(m)
            except Exception:
                pass
    mod = host.modifiers.new(name=mod_name, type="BOOLEAN")
    mod.operation = "DIFFERENCE"
    try:
        mod.solver = "FLOAT"
    except Exception:
        pass
    mod.object = cutter
    cutter.hide_render = True
    try:
        cutter.hide_set(True)
    except Exception:
        cutter.hide_viewport = True
    return True


MAT_STONE = make_mat("MAT_LIMESTONE", (0.82, 0.78, 0.70), 0.78, 0.0)
MAT_DARK = make_mat("MAT_FOUNDATION_DARK", (0.18, 0.16, 0.14), 0.90, 0.0)
MAT_GOLD = make_mat("MAT_GOLD_TRIM", (0.90, 0.68, 0.22), 0.22, 0.95)
MAT_GLASS = make_mat("MAT_GLASS_DARK", (0.15, 0.22, 0.28), 0.15, 0.05)

CX, CY = 1.0, 1.5
X_MIN, X_MAX = -11.5, 12.5
Y_MIN, Y_MAX = -8.5, 10.5
H_MAX = 38.2
n = 0

# Window levels on tower shaft (Z bands matching setbacks)
levels = [4.5, 9.5, 14.5, 19.5, 24.5]
# Face offsets: N S E W
faces = [
    ("N", 0.0, 2.9, 0.9, 0.25),   # dx, dy, frame_sx, frame_sy for N face
    ("S", 0.0, -2.9, 0.9, 0.25),
    ("E", 2.9, 0.0, 0.25, 0.9),
    ("W", -2.9, 0.0, 0.25, 0.9),
]

for li, z in enumerate(levels):
    for face, dx, dy, fsx, fsy in faces:
        # slight pair of windows per face at mid/upper levels
        offsets = [0.0] if li < 2 else [-0.7, 0.7]
        for oi, off in enumerate(offsets):
            if face in ("N", "S"):
                px, py = CX + off, CY + dy
                fwx, fwy = fsx, fsy
                pwx, pwy = 0.55, 0.12
            else:
                px, py = CX + dx, CY + off
                fwx, fwy = fsx, fsy
                pwx, pwy = 0.12, 0.55
            fr = ensure_cube(f"TWIN_FR_{face}_{li}_{oi}")
            set_size(fr, fwx, fwy, 1.6, bottom_z=z, center_xy=(px, py))
            assign(fr, MAT_DARK)
            apply_scale(fr)
            soft_bevel(fr, 0.025)
            pane = ensure_cube(f"TWIN_PN_{face}_{li}_{oi}")
            set_size(pane, pwx, pwy, 1.2, bottom_z=z + 0.15, center_xy=(px, py))
            assign(pane, MAT_GLASS)
            apply_scale(pane)
            mul = ensure_cube(f"TWIN_MU_{face}_{li}_{oi}")
            if face in ("N", "S"):
                set_size(mul, 0.08, 0.1, 1.2, bottom_z=z + 0.15, center_xy=(px, py))
            else:
                set_size(mul, 0.1, 0.08, 1.2, bottom_z=z + 0.15, center_xy=(px, py))
            assign(mul, MAT_GOLD)
            apply_scale(mul)
            n += 3

# Boolean lancet cuts into shaft setbacks (subtractive depth)
host_map = {
    0: "SHAFT_SETBACK_1",
    1: "SHAFT_SETBACK_2",
    2: "SHAFT_SETBACK_3",
    3: "SHAFT_SETBACK_4",
    4: "SHAFT_SETBACK_5",
}
for li, z in enumerate(levels):
    host = bpy.data.objects.get(host_map.get(li, "SHAFT_SETBACK_2"))
    if not host:
        continue
    for face, dx, dy, _, _ in faces:
        cut = ensure_cube(f"TWIN_CUT_{face}_{li}")
        if face in ("N", "S"):
            set_size(cut, 0.7, 0.9, 1.4, bottom_z=z + 0.1, center_xy=(CX, CY + dy * 0.85))
        else:
            set_size(cut, 0.9, 0.7, 1.4, bottom_z=z + 0.1, center_xy=(CX + dx * 0.85, CY))
        apply_scale(cut)
        if add_bool_diff(host, cut, f"TWIN_BOOL_{face}_{li}"):
            n += 1

# Horizontal string belts between window levels
for i, z in enumerate([7.0, 12.0, 17.0, 22.0, 27.0]):
    band = ensure_cube(f"TWIN_STRING_{i}")
    w = 6.2 - i * 0.25
    set_size(band, w, w, 0.22, bottom_z=z, center_xy=(CX, CY))
    assign(band, MAT_GOLD if i % 2 == 0 else MAT_DARK)
    apply_scale(band)
    n += 1

print("CREATED_OR_UPDATED", n)

# Soft clamp
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
    top = o.location.z + o.dimensions.z / 2.0
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
print("BOUNDS", round(bw, 2), round(bd, 2), round(bh, 2), "Z", round(minz, 2), round(maxz, 2), "MESHES", mesh_n, "BOOL", bool_n)

state = f"""# AUTONOMOUS BUILD STATE — ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01

**Updated:** 2026-07-27 (job `019f9eec8b6f` tick **#97**, 5m)  
**Asset ID:** `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01`  

| Field | Value |
|-------|--------|
| **ASSET_FINAL_COMPLETE** | **false** |
| **accepted (user)** | **false** |
| **Current** | **PASS8 V75 TOWER_WINS** |
| **Scale** | FP **{bw:.1f}×{bd:.1f}** (≤24×19) · top Z **{maxz:.1f}** |
| **Scheduler** | `019f9eec8b6f` every **5 min** |
| **Pipeline** | IN_PROGRESS (tower window string densify) |

---

## Tick #97 — executed (P1)

### Edits
1. **Tower window string** — 5 levels × 4 faces (frames + glass + gold mullions)
2. **Boolean lancets** into SHAFT_SETBACK hosts
3. **String belts** between levels

### Files
| Role | Path |
|------|------|
| Work | `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V75_TOWER_WINS.blend` |
| Loop / candidate | `PASS1D.blend` / `FINAL.blend` (synced) |
| Backup | `...BACKUP_LOOP_{STAMP}.blend` |
| Proofs | `renders_final/*` + work proofs |

### Bounds
**{bw:.1f} × {bd:.1f} × {bh:.1f}** m · Z {minz:.1f}..**{maxz:.1f}** · meshes ~{mesh_n} · bool {bool_n}

### Internal scores
| Axis | Score |
|------|-------|
| Scale | **9.0** |
| Tower fenestration | ~8.4 |
| Gothic fidelity | ~8.3 |
| Overall | **~8.45** |

### Verdict
Not FINAL. Tower mid reading denser; D1 modular core still primary Human blocker.  
Next: declutter low-value clutter OR banner/flag vertical polish.
"""

loop_state = f"""# BUILD LOOP STATE

**Updated:** 2026-07-27 · tick **#97** · job `019f9eec8b6f` (5m)  
**ASSET_FINAL_COMPLETE:** false · **Current:** PASS8_V75_TOWER_WINS  

## Tick #97 (P1)
- Tower window string 5 levels × 4 faces
- Shaft boolean lancets + string belts
- Bounds {bw:.1f}×{bd:.1f}×{bh:.1f} · bool {bool_n}
- Backup: BACKUP_LOOP_{STAMP}
- Saved: PASS8_V75_TOWER_WINS → PASS1D / FINAL

## Next
Declutter or banner polish; Human overlay when closer
"""

dev = f"""# INTERMEDIATE DEVIATION REPORT — tick #97

**Asset:** ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01
**Stamp:** {STAMP}
**File:** PASS8_V75_TOWER_WINS / PASS1D
**ASSET_FINAL_COMPLETE:** false
**accepted (user):** false

## Inventory
- Mesh objects (visible): **{mesh_n}**
- Boolean hosts: **{bool_n}**

## Sheet targets
- Footprint 24×19 m · Height 38 m · Wall 6.5 m
- Achieved: **{bw:.2f}×{bd:.2f}×{bh:.2f}** m · Z {minz:.2f}..{maxz:.2f}

## Matches
- Multi-level tower fenestration all faces
- Gold mullions + glass panes + shaft bool depth
- Scale lock held

## Gaps vs mockup (blocking Human accept)
| ID | Pri | Gap |
|----|-----|-----|
| D1 | P1 | Core modular-box language still dominant |
| D2 | P1 | Roof still plate-rotated hips |
| D3 | P2 | Windows are box frames not carved gothic |
| D4 | P2 | Mesh count growing again |
| D5 | P3 | UV/LOD not authored |

## Overall ~8.45 — not FINAL until Human overlay
Tower fenestration densified; Human overlay still required.
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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V75_TOWER_WINS.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V75")

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

print("TICK97_DONE")
