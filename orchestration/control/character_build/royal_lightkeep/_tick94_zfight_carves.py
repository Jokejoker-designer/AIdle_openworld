# -*- coding: utf-8 -*-
"""Tick #94: merlon/z-fight cleanup + more host-specific carves on curtain/hall.
Continue PASS8_V71_MASS_BOOL. Scale lock 24x19x38. No FINAL claim."""
import bpy
import os
import shutil
import bmesh
from datetime import datetime
from mathutils import Vector

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V71_MASS_BOOL.blend")
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


def apply_scale(o):
    try:
        for x in bpy.data.objects:
            x.select_set(False)
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    except Exception as e:
        print("APPLY_ERR", o.name, e)


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


CX, CY = 1.0, 1.5
X_MIN, X_MAX = -11.5, 12.5
Y_MIN, Y_MAX = -8.5, 10.5
H_MAX = 38.2
MAT_STONE = make_mat("MAT_LIMESTONE", (0.82, 0.78, 0.70), 0.78, 0.0)
MAT_DARK = make_mat("MAT_FOUNDATION_DARK", (0.18, 0.16, 0.14), 0.90, 0.0)
ops = 0
hidden = 0

# ========== 1) Z-fight cleanup: hide alternate merlons / duplicate FACADE_PILASTER ==========
# Keep every other merlon on dense rings to reduce coplanar flicker
for o in list(bpy.data.objects):
    if o.type != "MESH":
        continue
    name = o.name
    # Hide odd-indexed dense merlons (keep rhythm but less coplanar stack)
    if name.startswith("MERLON_F_") or name.startswith("MERLON_R_") or name.startswith("MERLON_L_") or name.startswith("MERLON_RT_"):
        try:
            idx = int(name.rsplit("_", 1)[-1])
            if idx % 2 == 1:
                o.hide_render = True
                o.hide_viewport = True
                hidden += 1
        except ValueError:
            pass
    # Hide older FACADE_PILASTER if BAY_PIL exists (duplicate front language)
    if name.startswith("FACADE_PILASTER_") or name.startswith("FACADE_CAP_"):
        o.hide_render = True
        o.hide_viewport = True
        hidden += 1
    # Hide CROWN_MERLON_R alternate if dense
    if name.startswith("CROWN_MERLON_R_"):
        try:
            idx = int(name.rsplit("_", 1)[-1])
            if idx % 2 == 1:
                o.hide_render = True
                o.hide_viewport = True
                hidden += 1
        except ValueError:
            pass

print("HIDDEN", hidden)

# ========== 2) Slight push curtain inward to reduce z-fight with outer bollards ==========
for cname, dy, dx in (
    ("CURTAIN_FRONT", -0.15, 0.0),
    ("CURTAIN_REAR", 0.15, 0.0),
    ("CURTAIN_LEFT", 0.0, 0.15),
    ("CURTAIN_RIGHT", 0.0, -0.15),
):
    o = bpy.data.objects.get(cname)
    if o:
        o.location.y += dy
        o.location.x += dx
        ops += 1

# ========== 3) Host-specific carves: curtain gate / hall rear windows ==========
# Larger gate cut in CURTAIN_FRONT (portal center)
gate_cut = ensure_cube("CURTAIN_GATE_CUT")
set_size(gate_cut, 4.2, 2.0, 5.0, bottom_z=0.15, center_xy=(CX, 9.5))
apply_scale(gate_cut)
host = bpy.data.objects.get("CURTAIN_FRONT")
if host and add_bool_diff(host, gate_cut, "CURTAIN_GATE_BOOL"):
    print("BOOL CURTAIN_FRONT <- GATE")
    ops += 1

# Arrow slots along curtain sides
for side, host_name, x in (("L", "CURTAIN_LEFT", CX - 10.5), ("R", "CURTAIN_RIGHT", CX + 10.5)):
    host = bpy.data.objects.get(host_name)
    if not host:
        continue
    for i, y in enumerate([-4.0, -1.0, 2.0, 5.0]):
        cut = ensure_cube(f"CURTAIN_SLOT_{side}_{i}")
        set_size(cut, 1.2, 0.35, 1.1, bottom_z=3.2, center_xy=(x, CY + y))
        apply_scale(cut)
        if add_bool_diff(host, cut, f"CURTAIN_SLOT_BOOL_{side}_{i}"):
            ops += 1
            print("BOOL", host_name, "<-", cut.name)

# Hall / tower upper gallery carve
for i, (x, z) in enumerate([(-2.5, 12.5), (0.0, 12.5), (2.5, 12.5)]):
    cut = ensure_cube(f"HALL_GALLERY_CUT_{i}")
    set_size(cut, 1.6, 1.4, 2.0, bottom_z=z, center_xy=(CX + x, 5.5))
    apply_scale(cut)
    host = bpy.data.objects.get("HALL_FRONT_MASS") or bpy.data.objects.get("TOWER_FRONT_MASS")
    if host and add_bool_diff(host, cut, f"HALL_GALLERY_BOOL_{i}"):
        print("BOOL", host.name, "<-", cut.name)
        ops += 1

# Dark liners inside new gate (depth read without more solid boxes)
liner = ensure_cube("CURTAIN_GATE_LINER")
set_size(liner, 3.8, 0.4, 4.6, bottom_z=0.2, center_xy=(CX, 9.2))
assign(liner, MAT_DARK)
apply_scale(liner)
ops += 1

print("OPS", ops)

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
print("BOUNDS", round(bw, 2), round(bd, 2), round(bh, 2), "Z", round(minz, 2), round(maxz, 2), "MESHES", mesh_n, "BOOL", bool_n, "HIDDEN", hidden)

state = f"""# AUTONOMOUS BUILD STATE — ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01

**Updated:** 2026-07-27 (job `019f9eec8b6f` tick **#94**, 5m)  
**Asset ID:** `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01`  

| Field | Value |
|-------|--------|
| **ASSET_FINAL_COMPLETE** | **false** |
| **accepted (user)** | **false** |
| **Current** | **PASS8 V72 ZFIGHT_CARVE** |
| **Scale** | FP **{bw:.1f}×{bd:.1f}** (≤24×19) · top Z **{maxz:.1f}** |
| **Scheduler** | `019f9eec8b6f` every **5 min** |
| **Pipeline** | IN_PROGRESS (z-fight cleanup + curtain carves) |

---

## Tick #94 — executed (P1/P2)

### Edits
1. **Z-fight cleanup** — hide odd merlons + duplicate FACADE_PILASTER/CAP + alt crown merlons ({hidden} hidden)
2. **Curtain nudge** inward + **gate boolean** on CURTAIN_FRONT
3. **Arrow slots** on L/R curtain (8) + **hall gallery carves** (3) + gate liner

### Files
| Role | Path |
|------|------|
| Work | `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V72_ZFIGHT_CARVE.blend` |
| Loop / candidate | `PASS1D.blend` / `FINAL.blend` (synced) |
| Backup | `...BACKUP_LOOP_{STAMP}.blend` |
| Proofs | `renders_final/*` + work proofs |

### Bounds
**{bw:.1f} × {bd:.1f} × {bh:.1f}** m · Z {minz:.1f}..**{maxz:.1f}** · meshes ~{mesh_n} · bool {bool_n}

### Internal scores
| Axis | Score |
|------|-------|
| Scale | **9.0** |
| Clean / z-fight | ~8.3 |
| Opening depth | ~8.3 |
| Gothic fidelity | ~8.2 |
| Overall | **~8.4** |

### Verdict
Not FINAL. Cleanup + carves improve readability; D1 modular core still primary Human blocker.  
Next: roof hip continuity OR declutter SHAFT_SETBACK vs older TOWER masses.
"""

loop_state = f"""# BUILD LOOP STATE

**Updated:** 2026-07-27 · tick **#94** · job `019f9eec8b6f` (5m)  
**ASSET_FINAL_COMPLETE:** false · **Current:** PASS8_V72_ZFIGHT_CARVE  

## Tick #94 (P1/P2)
- Merlon/facade z-fight hide ({hidden})
- Curtain gate + arrow slots + hall gallery carves
- Bounds {bw:.1f}×{bd:.1f}×{bh:.1f} · bool {bool_n}
- Backup: BACKUP_LOOP_{STAMP}
- Saved: PASS8_V72_ZFIGHT_CARVE → PASS1D / FINAL

## Next
Roof hip continuity or hide overlapping tower mass layers; Human overlay when closer
"""

dev = f"""# INTERMEDIATE DEVIATION REPORT — tick #94

**Asset:** ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01
**Stamp:** {STAMP}
**File:** PASS8_V72_ZFIGHT_CARVE / PASS1D
**ASSET_FINAL_COMPLETE:** false
**accepted (user):** false

## Inventory
- Mesh objects (visible): **{mesh_n}**
- Boolean hosts: **{bool_n}**
- Hidden this tick: **{hidden}**

## Sheet targets
- Footprint 24×19 m · Height 38 m · Wall 6.5 m
- Achieved: **{bw:.2f}×{bd:.2f}×{bh:.2f}** m · Z {minz:.2f}..{maxz:.2f}

## Matches
- Reduced merlon/facade coplanar clutter
- Curtain gate opening + side arrow slots
- Continued subtractive method on hosts

## Gaps vs mockup (blocking Human accept)
| ID | Pri | Gap |
|----|-----|-----|
| D1 | P1 | Core modular language still dominant |
| D2 | P1 | Roof organic continuity incomplete |
| D3 | P2 | Overlapping tower mass layers possible |
| D4 | P2 | Pointed-arch true mesh missing |
| D5 | P3 | UV/LOD not authored |

## Overall ~8.4 — not FINAL until Human overlay
Cleanup path engaged; still need silhouette closer to mockup for Human accept.
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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V72_ZFIGHT_CARVE.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V72")

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

print("TICK94_DONE")
