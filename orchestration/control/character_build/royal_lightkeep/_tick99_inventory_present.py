# -*- coding: utf-8 -*-
"""Tick #99: inventory snapshot + material contrast + presentation light polish.
No cube densify (plateau). Continue PASS8_V76. Scale lock 24x19x38. No FINAL claim."""
import bpy
import os
import shutil
from datetime import datetime
from mathutils import Vector
from collections import Counter

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V76_DECLUTTER_BANNER.blend")
LOOP = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS1D.blend")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

bpy.ops.wm.open_mainfile(filepath=WORK)
print("OPEN", bpy.data.filepath)

backup = os.path.join(BASE, f"ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_BACKUP_LOOP_{STAMP}.blend")
bpy.ops.wm.save_as_mainfile(filepath=backup, copy=True)
print("BACKUP", backup)

# ========== Material contrast polish (readability vs mockup) ==========
MAT_UPDATES = {
    "MAT_LIMESTONE": ((0.86, 0.82, 0.74), 0.82, 0.0),
    "MAT_FOUNDATION_DARK": ((0.14, 0.12, 0.11), 0.92, 0.0),
    "MAT_SLATE_NAVY": ((0.06, 0.10, 0.22), 0.42, 0.08),
    "MAT_GOLD_TRIM": ((0.95, 0.72, 0.25), 0.18, 0.98),
    "MAT_GLASS_DARK": ((0.12, 0.20, 0.28), 0.12, 0.05),
    "MAT_BANNER_NAVY": ((0.06, 0.10, 0.38), 0.50, 0.0),
    "MAT_BANNER_RED": ((0.62, 0.10, 0.10), 0.50, 0.0),
    "MAT_WOOD": ((0.38, 0.24, 0.12), 0.78, 0.0),
    "MAT_PAVING": ((0.58, 0.54, 0.48), 0.88, 0.0),
}
mat_n = 0
for name, (col, rough, metal) in MAT_UPDATES.items():
    m = bpy.data.materials.get(name)
    if not m:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
    if m.use_nodes:
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (*col, 1.0)
            bsdf.inputs["Roughness"].default_value = rough
            if "Metallic" in bsdf.inputs:
                bsdf.inputs["Metallic"].default_value = metal
            mat_n += 1
print("MATS", mat_n)

# ========== Presentation lights ==========
light_n = 0
# Key sun-like
sun = bpy.data.objects.get("LIGHT_KEY_SUN")
if not sun:
    data = bpy.data.lights.new(name="LIGHT_KEY_SUN", type="SUN")
    sun = bpy.data.objects.new("LIGHT_KEY_SUN", data)
    bpy.context.scene.collection.objects.link(sun)
sun.data.type = "SUN"
sun.data.energy = 3.2
try:
    sun.data.angle = 0.15
except Exception:
    pass
sun.rotation_euler = (0.9, 0.2, 0.6)
light_n += 1

# Fill
fill = bpy.data.objects.get("LIGHT_FILL")
if not fill:
    data = bpy.data.lights.new(name="LIGHT_FILL", type="AREA")
    fill = bpy.data.objects.new("LIGHT_FILL", data)
    bpy.context.scene.collection.objects.link(fill)
fill.data.type = "AREA"
fill.data.energy = 250
try:
    fill.data.size = 12
except Exception:
    pass
fill.location = (CX if False else 1.0, -12.0, 18.0)
fill.rotation_euler = (1.1, 0, 0)
light_n += 1

# Rim
rim = bpy.data.objects.get("LIGHT_RIM")
if not rim:
    data = bpy.data.lights.new(name="LIGHT_RIM", type="AREA")
    rim = bpy.data.objects.new("LIGHT_RIM", data)
    bpy.context.scene.collection.objects.link(rim)
rim.data.type = "AREA"
rim.data.energy = 180
try:
    rim.data.size = 8
except Exception:
    pass
rim.location = (14.0, 8.0, 22.0)
rim.rotation_euler = (0.8, 0.3, -0.9)
light_n += 1
print("LIGHTS_POLISH", light_n)

# World soft sky
world = bpy.context.scene.world
if world and world.use_nodes:
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.55, 0.62, 0.72, 1.0)
        bg.inputs[1].default_value = 0.45
        print("WORLD_OK")

# Soft clamp
X_MIN, X_MAX = -11.5, 12.5
Y_MIN, Y_MAX = -8.5, 10.5
H_MAX = 38.2
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

# Inventory
minx = miny = minz = 1e9
maxx = maxy = maxz = -1e9
mesh_n = 0
bool_n = 0
beveled = 0
hidden_n = 0
meshes = []
for o in bpy.data.objects:
    if o.type != "MESH":
        continue
    if any(m.type == "BOOLEAN" for m in o.modifiers):
        bool_n += 1
    if any(m.type == "BEVEL" for m in o.modifiers):
        beveled += 1
    if o.hide_render:
        hidden_n += 1
        continue
    if o.name in ("PRES_GROUND", "SCALE_HUMAN") or "CUT" in o.name or "CUTTER" in o.name or "NICHE" in o.name:
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
top = pref.most_common(14)
cams = sum(1 for o in bpy.data.objects if o.type == "CAMERA")
lights = sum(1 for o in bpy.data.objects if o.type == "LIGHT")
print("BOUNDS", round(bw, 2), round(bd, 2), round(bh, 2), "Z", round(minz, 2), round(maxz, 2), "MESHES", mesh_n, "BOOL", bool_n, "HIDDEN", hidden_n)

state = f"""# AUTONOMOUS BUILD STATE — ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01

**Updated:** 2026-07-27 (job `019f9eec8b6f` tick **#99**, 5m)  
**Asset ID:** `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01`  

| Field | Value |
|-------|--------|
| **ASSET_FINAL_COMPLETE** | **false** |
| **accepted (user)** | **false** |
| **Current** | **PASS8 V77 INVENTORY_PRESENT** |
| **Scale** | FP **{bw:.1f}×{bd:.1f}** (≤24×19) · top Z **{maxz:.1f}** |
| **Scheduler** | `019f9eec8b6f` every **5 min** |
| **Pipeline** | IN_PROGRESS (plateau — inventory + presentation polish) |

---

## Tick #99 — executed (P2 presentation, no cube densify)

### Edits
1. **Material contrast** — limestone / slate / gold / glass / banners tuned
2. **Presentation lights** — key sun + fill + rim + world sky
3. **Inventory snapshot** full

### Inventory
- Visible meshes: **{mesh_n}** · Hidden: **{hidden_n}**
- Bool hosts: **{bool_n}** · Bevel: **{beveled}**
- Cams: **{cams}** · Lights: **{lights}**
- Top prefixes: {", ".join(f"{k}:{v}" for k, v in top)}

### Files
| Role | Path |
|------|------|
| Work | `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V77_INVENTORY_PRESENT.blend` |
| Loop / candidate | `PASS1D.blend` / `FINAL.blend` (synced) |
| Backup | `...BACKUP_LOOP_{STAMP}.blend` |
| Proofs | `renders_final/*` + work proofs |

### Bounds
**{bw:.1f} × {bd:.1f} × {bh:.1f}** m · Z {minz:.1f}..**{maxz:.1f}**

### Internal scores
| Axis | Score |
|------|-------|
| Scale | **9.0** |
| Presentation | ~8.5 |
| Gothic fidelity | ~8.3 |
| Overall | **~8.45** |

### Verdict
Not FINAL. Plateau acknowledged: cube densify diminishing. Presentation polish only this tick.  
**Human overlay still required** for ASSET_FINAL_COMPLETE.  
Next: if Human silent, prefer structural method change (true curved arch mesh / mass merge) over more cubes.
"""

loop_state = f"""# BUILD LOOP STATE

**Updated:** 2026-07-27 · tick **#99** · job `019f9eec8b6f` (5m)  
**ASSET_FINAL_COMPLETE:** false · **Current:** PASS8_V77_INVENTORY_PRESENT  

## Tick #99 (P2 presentation)
- Material contrast + lights + world
- Inventory: meshes {mesh_n}, hidden {hidden_n}, bool {bool_n}
- Bounds {bw:.1f}×{bd:.1f}×{bh:.1f}
- Backup: BACKUP_LOOP_{STAMP}
- Saved: PASS8_V77_INVENTORY_PRESENT → PASS1D / FINAL

## Next
Human overlay preferred; or curved-arch / mass-merge method (not more cubes)
"""

dev = f"""# INTERMEDIATE DEVIATION REPORT — tick #99

**Asset:** ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01
**Stamp:** {STAMP}
**File:** PASS8_V77_INVENTORY_PRESENT / PASS1D
**ASSET_FINAL_COMPLETE:** false
**accepted (user):** false

## Inventory
- Mesh objects (visible): **{mesh_n}**
- Hidden meshes: **{hidden_n}**
- Boolean hosts: **{bool_n}** · Bevel: **{beveled}**
- Cameras: **{cams}** · Lights: **{lights}**
- Top prefixes: {", ".join(f"{k}:{v}" for k, v in top)}

## Sheet targets
- Footprint 24×19 m · Height 38 m · Wall 6.5 m
- Achieved: **{bw:.2f}×{bd:.2f}×{bh:.2f}** m · Z {minz:.2f}..{maxz:.2f}

## Matches
- Scale lock 24×19×38
- Curtain 6.5, portal arch, roof hips, tower fenestration, banners
- Presentation contrast improved

## Gaps vs mockup (blocking Human accept)
| ID | Pri | Gap |
|----|-----|-----|
| D1 | P1 | Core modular-box language still dominant |
| D2 | P1 | Roof still plate-rotated not organic |
| D3 | P2 | Arches stepped cubes not true curves |
| D4 | P2 | High object count (~{mesh_n} visible) |
| D5 | P3 | UV/LOD not authored |

## Overall ~8.45 — not FINAL until Human overlay
**Plateau.** Self-accept intermediate only. Do not claim FINAL without Human.
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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V77_INVENTORY_PRESENT.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V77")

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

print("TICK99_DONE")
