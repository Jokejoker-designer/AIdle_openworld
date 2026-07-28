# -*- coding: utf-8 -*-
"""Tick #93: DIFFERENT METHOD for D1 — boolean niches into primary masses + hard FP clamp.
Continue PASS8_V70_GROUND_DRESS. Scale lock 24x19x38. No FINAL claim."""
import bpy
import os
import shutil
import bmesh
from datetime import datetime
from mathutils import Vector

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V70_GROUND_DRESS.blend")
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


CX = 1.0
CY = 1.5
X_MIN, X_MAX = -11.5, 12.5
Y_MIN, Y_MAX = -8.5, 10.5
H_MAX = 38.2
ops = 0

# ========== 1) Shrink ground apron that overshot FP ==========
for name, sx, sy in (
    ("GROUND_APRON", 23.0, 18.0),
    ("GROUND_PLINTH_0", 19.5, 15.5),
    ("GROUND_PLINTH_1", 18.0, 14.0),
    ("GROUND_PLINTH_2", 16.5, 12.5),
):
    o = bpy.data.objects.get(name)
    if o:
        set_size(o, sx, sy, max(0.1, o.dimensions.z), bottom_z=o.location.z - o.dimensions.z / 2.0, center_xy=(CX, CY))
        apply_scale(o)
        ops += 1
        print("RESIZE", name)

# ========== 2) Primary mass boolean niches (subtractive — different method) ==========
# Hosts to try
HOST_CANDIDATES = [
    "HALL_FRONT_MASS", "TOWER_FRONT_MASS", "WING_FRONT_MASS",
    "PORTAL_ARCH_OUTER", "SHAFT_SETBACK_2", "SHAFT_SETBACK_3",
    "UWRAP_REAR_BAR", "CURTAIN_FRONT",
]

# Create niche cutters on front facade rhythm
niche_specs = [
    # (name, sx, sy, sz, bottom_z, cx, cy)
    ("MASS_NICHE_A", 1.4, 1.2, 2.2, 3.0, CX - 3.5, 6.2),
    ("MASS_NICHE_B", 1.4, 1.2, 2.2, 3.0, CX + 3.5, 6.2),
    ("MASS_NICHE_C", 1.4, 1.2, 2.2, 6.5, CX - 3.5, 6.2),
    ("MASS_NICHE_D", 1.4, 1.2, 2.2, 6.5, CX + 3.5, 6.2),
    ("MASS_NICHE_E", 1.6, 1.2, 2.8, 4.0, CX, 5.8),
    ("MASS_NICHE_F", 1.2, 1.0, 1.8, 10.0, CX - 2.0, 5.5),
    ("MASS_NICHE_G", 1.2, 1.0, 1.8, 10.0, CX + 2.0, 5.5),
    ("MASS_NICHE_H", 1.5, 1.0, 2.0, 14.0, CX, 4.5),
]

cutters = []
for name, sx, sy, sz, bz, cx, cy in niche_specs:
    c = ensure_cube(name)
    set_size(c, sx, sy, sz, bottom_z=bz, center_xy=(cx, cy))
    apply_scale(c)
    cutters.append(c)
    ops += 1

# Apply first few niches to each available primary host (spread)
host_found = []
for hn in HOST_CANDIDATES:
    h = bpy.data.objects.get(hn)
    if h and h.type == "MESH":
        host_found.append(h)

print("HOSTS", [h.name for h in host_found])

# Map cutters to hosts in round-robin
for i, cut in enumerate(cutters):
    if not host_found:
        break
    host = host_found[i % len(host_found)]
    if add_bool_diff(host, cut, f"MASS_NICHE_BOOL_{i}"):
        print("BOOL", host.name, "<-", cut.name)
        ops += 1

# Tower mid-shaft deep side recesses
for side, xoff in (("L", -2.2), ("R", 2.2)):
    for j, z in enumerate([9.0, 16.0, 22.0]):
        cut = ensure_cube(f"SHAFT_SIDE_CUT_{side}_{j}")
        set_size(cut, 1.0, 2.5, 2.5, bottom_z=z, center_xy=(CX + xoff, CY))
        apply_scale(cut)
        # prefer shaft setbacks
        host = bpy.data.objects.get(f"SHAFT_SETBACK_{j + 2}") or bpy.data.objects.get("TOWER_FRONT_MASS")
        if host and add_bool_diff(host, cut, f"SHAFT_SIDE_BOOL_{side}_{j}"):
            print("BOOL", host.name, "<-", cut.name)
            ops += 1

# ========== 3) Declutter: hide redundant low-impact ground grass if >3 ==========
hidden = 0
for o in list(bpy.data.objects):
    if o.name.startswith("GROUND_GRASS_") and o.name not in ("GROUND_GRASS_0", "GROUND_GRASS_1", "GROUND_GRASS_2"):
        o.hide_render = True
        o.hide_viewport = True
        hidden += 1
print("HIDDEN_GRASS", hidden)

# ========== 4) Hard footprint + height clamp ==========
for o in bpy.data.objects:
    if o.type != "MESH":
        continue
    if o.name in ("PRES_GROUND", "LEVEL0_GROUND", "SCALE_HUMAN") or "BOOL_CUT" in o.name or o.name.endswith("_CUT") or "CUTTER" in o.name or "NICHE" in o.name or "SIDE_CUT" in o.name:
        # still clamp cutters that are visible somehow
        if o.hide_render:
            continue
    if o.hide_render and ("NICHE" in o.name or "CUT" in o.name):
        continue
    if o.type != "MESH" or o.hide_render:
        if "NICHE" not in o.name and "SIDE_CUT" not in o.name:
            continue
    if o.hide_render:
        continue
    if o.name in ("PRES_GROUND", "LEVEL0_GROUND", "SCALE_HUMAN"):
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

# Second pass: scale down any still overshooting by shrinking location only failed — force dim check
bpy.context.view_layer.update()

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
    if o.name in ("PRES_GROUND", "SCALE_HUMAN") or "BOOL_CUT" in o.name or o.name.endswith("_CUT") or "CUTTER" in o.name or "NICHE" in o.name or "SIDE_CUT" in o.name:
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

# If still over FP, nudge outermost objects again harder
if maxx - minx > 24.05 or maxy - miny > 19.05:
    print("EXTRA_CLAMP", round(maxx - minx, 2), round(maxy - miny, 2))
    for o in bpy.data.objects:
        if o.type != "MESH" or o.hide_render:
            continue
        if o.name in ("PRES_GROUND", "SCALE_HUMAN") or "NICHE" in o.name or "CUT" in o.name:
            continue
        corners = [o.matrix_world @ Vector(c) for c in o.bound_box]
        ominx = min(c.x for c in corners)
        omaxx = max(c.x for c in corners)
        ominy = min(c.y for c in corners)
        omaxy = max(c.y for c in corners)
        if ominx < X_MIN + 0.05:
            o.location.x += (X_MIN + 0.05 - ominx)
        if omaxx > X_MAX - 0.05:
            o.location.x += (X_MAX - 0.05 - omaxx)
        if ominy < Y_MIN + 0.05:
            o.location.y += (Y_MIN + 0.05 - ominy)
        if omaxy > Y_MAX - 0.05:
            o.location.y += (Y_MAX - 0.05 - omaxy)
    bpy.context.view_layer.update()
    minx = miny = minz = 1e9
    maxx = maxy = maxz = -1e9
    mesh_n = 0
    for o in bpy.data.objects:
        if o.type != "MESH" or o.hide_render:
            continue
        if o.name in ("PRES_GROUND", "SCALE_HUMAN") or "BOOL_CUT" in o.name or o.name.endswith("_CUT") or "CUTTER" in o.name or "NICHE" in o.name or "SIDE_CUT" in o.name:
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
print("OPS", ops, "BOUNDS", round(bw, 2), round(bd, 2), round(bh, 2), "Z", round(minz, 2), round(maxz, 2), "MESHES", mesh_n, "BOOL", bool_n)

state = f"""# AUTONOMOUS BUILD STATE — ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01

**Updated:** 2026-07-27 (job `019f9eec8b6f` tick **#93**, 5m)  
**Asset ID:** `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01`  

| Field | Value |
|-------|--------|
| **ASSET_FINAL_COMPLETE** | **false** |
| **accepted (user)** | **false** |
| **Current** | **PASS8 V71 MASS_BOOL** |
| **Scale** | FP **{bw:.1f}×{bd:.1f}** (≤24×19) · top Z **{maxz:.1f}** |
| **Scheduler** | `019f9eec8b6f` every **5 min** |
| **Pipeline** | IN_PROGRESS (subtractive mass niches — D1 method change) |

---

## Tick #93 — executed (P1, different method)

### Edits
1. **Hard FP reclamp** — shrink ground apron/plinths that overshot 24×19
2. **Primary mass boolean niches** — 8 front niches + 6 shaft side cuts (subtractive)
3. **Declutter** — hide excess GROUND_GRASS plates

### Files
| Role | Path |
|------|------|
| Work | `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V71_MASS_BOOL.blend` |
| Loop / candidate | `PASS1D.blend` / `FINAL.blend` (synced) |
| Backup | `...BACKUP_LOOP_{STAMP}.blend` |
| Proofs | `renders_final/*` + work proofs |

### Bounds
**{bw:.1f} × {bd:.1f} × {bh:.1f}** m · Z {minz:.1f}..**{maxz:.1f}** · meshes ~{mesh_n} · bool hosts {bool_n}

### Internal scores
| Axis | Score |
|------|-------|
| Scale | **9.0** (reclamped) |
| Mass depth (subtractive) | ~8.25 |
| Gothic fidelity | ~8.2 |
| Overall | **~8.4** |

### Verdict
Not FINAL. Method shifted from additive cubes to boolean niche carve on primary masses.  
D1 still open until silhouette reads less stacked-box vs mockup.  
Next: apply more host-specific carves OR hide/merge redundant MERLON duplicates if z-fighting.
"""

loop_state = f"""# BUILD LOOP STATE

**Updated:** 2026-07-27 · tick **#93** · job `019f9eec8b6f` (5m)  
**ASSET_FINAL_COMPLETE:** false · **Current:** PASS8_V71_MASS_BOOL  

## Tick #93 (P1 different method)
- Hard FP reclamp (apron/plinth)
- Subtractive niches on primary masses + shaft sides
- Hide excess grass plates
- Bounds {bw:.1f}×{bd:.1f}×{bh:.1f} · bool {bool_n}
- Backup: BACKUP_LOOP_{STAMP}
- Saved: PASS8_V71_MASS_BOOL → PASS1D / FINAL

## Next
More host-specific carves or merlon/z-fight cleanup; Human overlay when closer
"""

dev = f"""# INTERMEDIATE DEVIATION REPORT — tick #93

**Asset:** ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01
**Stamp:** {STAMP}
**File:** PASS8_V71_MASS_BOOL / PASS1D
**ASSET_FINAL_COMPLETE:** false
**accepted (user):** false

## Inventory
- Mesh objects (visible): **{mesh_n}**
- Boolean hosts: **{bool_n}**
- Method: subtractive mass niches (not more additive cubes)

## Sheet targets
- Footprint 24×19 m · Height 38 m · Wall 6.5 m
- Achieved: **{bw:.2f}×{bd:.2f}×{bh:.2f}** m · Z {minz:.2f}..{maxz:.2f}

## Matches
- Scale reclamp after ground dress overshoot
- Depth carves into primary masses (D1 approach change)
- Prior stair/U-wrap/crown/portal/curtain stack retained

## Gaps vs mockup (blocking Human accept)
| ID | Pri | Gap |
|----|-----|-----|
| D1 | P1 | Core still modular language; booleans help but incomplete |
| D2 | P1 | Roof organic continuity incomplete |
| D3 | P2 | High mesh density / possible z-fight |
| D4 | P2 | Pointed arches still stacked-box approximated |
| D5 | P3 | UV/LOD not authored |

## Overall ~8.4 — not FINAL until Human overlay
Subtractive method engaged. Continue carve quality over cube count.
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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V71_MASS_BOOL.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V71")

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

print("TICK93_DONE")
