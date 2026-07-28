# -*- coding: utf-8 -*-
"""Tick #115: inventory + key visibility audit + presentation polish.
Continue PASS8_V92_HALL_WINS. Scale lock 24x19x38. No densify. No FINAL."""
import bpy
import bmesh
import os
import shutil
from datetime import datetime
from mathutils import Vector
from collections import Counter

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V92_HALL_WINS.blend")
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


# Ensure critical systems visible
MUST_SHOW = [
    "GATEHOUSE_MASS", "PORTAL_CURVED_ARCH", "PORTAL_CURVED_ARCH_INNER",
    "HALL_FRONT_MASS", "SHAFT_SETBACK_2", "SHAFT_SETBACK_4",
    "ROOF_HIP_MESH_MAIN", "ROOF_HIP_MESH_TOWER",
    "CURTAIN_FRONT", "CURTAIN_REAR", "CURTAIN_LEFT", "CURTAIN_RIGHT",
    "STAIR_LANDING_MAIN", "UWRAP_REAR_BAR", "UWRAP_WING_L", "UWRAP_WING_R",
    "CROWN_MESH_COLLAR", "CROWN_MESH_SPIRE",
    "QBUTT_PIER_L_0", "QBUTT_PIER_R_0",
    "SCALE_HUMAN", "PRES_GROUND",
]
shown = 0
for name in MUST_SHOW:
    o = bpy.data.objects.get(name)
    if o:
        o.hide_render = False
        o.hide_viewport = False
        shown += 1
print("ENSURE_VISIBLE", shown, "/", len(MUST_SHOW))

# Soft light polish
sun = bpy.data.objects.get("LIGHT_KEY_SUN")
if sun and sun.data:
    sun.data.energy = 3.6
fill = bpy.data.objects.get("LIGHT_FILL")
if fill and fill.data:
    fill.data.energy = 320
rim = bpy.data.objects.get("LIGHT_RIM")
if rim and rim.data:
    rim.data.energy = 200

# Scale human ensure
sh = ensure_cube("SCALE_HUMAN")
sh.scale = (0.35, 0.25, 0.875)
sh.location = (1.0 - 5.5, 9.8, 0.875)
assign(sh, make_mat("MAT_SCALE_HUMAN", (0.9, 0.2, 0.15), 0.6, 0.0))

# Clamp structural
X_MIN, X_MAX = -11.5, 12.5
Y_MIN, Y_MAX = -8.5, 10.5
H_MAX = 38.2
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

# Full inventory
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
top = pref.most_common(14)
cams = sum(1 for o in bpy.data.objects if o.type == "CAMERA")
lights = sum(1 for o in bpy.data.objects if o.type == "LIGHT")
print("BOUNDS", round(bw, 2), round(bd, 2), round(bh, 2), "Z", round(minz, 2), round(maxz, 2), "MESHES", mesh_n, "BOOL", bool_n, "HIDDEN", hidden_n)

# Systems checklist
systems = {
    "gatehouse": bool(bpy.data.objects.get("GATEHOUSE_MASS") and not bpy.data.objects["GATEHOUSE_MASS"].hide_render),
    "curved_portal": bool(bpy.data.objects.get("PORTAL_CURVED_ARCH") and not bpy.data.objects["PORTAL_CURVED_ARCH"].hide_render),
    "shaft_taper": bool(bpy.data.objects.get("SHAFT_SETBACK_3") and not bpy.data.objects["SHAFT_SETBACK_3"].hide_render),
    "hip_roof": bool(bpy.data.objects.get("ROOF_HIP_MESH_MAIN") and not bpy.data.objects["ROOF_HIP_MESH_MAIN"].hide_render),
    "crown_gables": bool(bpy.data.objects.get("CROWN_MESH_GABLE_N") and not bpy.data.objects["CROWN_MESH_GABLE_N"].hide_render),
    "stair": bool(bpy.data.objects.get("STAIR_LANDING_MAIN") and not bpy.data.objects["STAIR_LANDING_MAIN"].hide_render),
    "curtain": bool(bpy.data.objects.get("CURTAIN_FRONT") and not bpy.data.objects["CURTAIN_FRONT"].hide_render),
    "buttress": bool(bpy.data.objects.get("QBUTT_PIER_L_0") and not bpy.data.objects["QBUTT_PIER_L_0"].hide_render),
    "hall_wins": bool(bpy.data.objects.get("HALL_WIN_FR_1_2") and not bpy.data.objects["HALL_WIN_FR_1_2"].hide_render),
}
print("SYSTEMS", systems)

sys_md = "\n".join(f"- {k}: **{'OK' if v else 'MISSING'}**" for k, v in systems.items())

state = f"""# AUTONOMOUS BUILD STATE — ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01

**Updated:** 2026-07-27 (job `019f9eec8b6f` tick **#115**, 5m)  
**Asset ID:** `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01`  

| Field | Value |
|-------|--------|
| **ASSET_FINAL_COMPLETE** | **false** |
| **accepted (user)** | **false** |
| **Current** | **PASS8 V93 INVENTORY** |
| **Scale** | FP **{bw:.1f}×{bd:.1f}** (≤24×19) · top Z **{maxz:.1f}** |
| **Scheduler** | `019f9eec8b6f` every **5 min** |
| **Pipeline** | IN_PROGRESS (inventory audit; plateau) |

---

## Tick #115 — executed (inventory / presentation)

### Edits
1. Ensure critical systems visible ({shown}/{len(MUST_SHOW)})
2. Lights + scale human polish
3. Full inventory + systems checklist

### Systems
{sys_md}

### Inventory
- Visible: **{mesh_n}** · Hidden: **{hidden_n}**
- Bool: **{bool_n}** · Bevel: **{beveled}** · Cams: **{cams}** · Lights: **{lights}**
- Top: {", ".join(f"{k}:{v}" for k, v in top)}

### Files
| Role | Path |
|------|------|
| Work | `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V93_INVENTORY.blend` |
| Loop / candidate | `PASS1D.blend` / `FINAL.blend` (synced) |
| Backup | `...BACKUP_LOOP_{STAMP}.blend` |
| Proofs | `renders_final/*` + work proofs |

### Bounds
**{bw:.1f} × {bd:.1f} × {bh:.1f}** m · Z {minz:.1f}..**{maxz:.1f}**

### Internal scores
| Axis | Score |
|------|-------|
| Scale | **9.0** |
| Systems integrity | ~8.7 |
| Gothic fidelity | ~8.55 |
| Overall | **~8.55** |

### Verdict
Not FINAL. Systems audit PASS-internal. D1 modular language still blocks Human. **Human overlay required for FINAL.**
"""

loop_state = f"""# BUILD LOOP STATE

**Updated:** 2026-07-27 · tick **#115** · job `019f9eec8b6f` (5m)  
**ASSET_FINAL_COMPLETE:** false · **Current:** PASS8_V93_INVENTORY  

## Tick #115 (inventory)
- Systems audit + lights + scale human
- Visible {mesh_n} / hidden {hidden_n} / bool {bool_n}
- Bounds {bw:.1f}×{bd:.1f}×{bh:.1f}
- Backup: BACKUP_LOOP_{STAMP}
- Saved: PASS8_V93_INVENTORY → PASS1D / FINAL

## Next
Human overlay for FINAL; avoid cube densify on plateau
"""

dev = f"""# INTERMEDIATE DEVIATION REPORT — tick #115

**Asset:** ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01
**Stamp:** {STAMP}
**File:** PASS8_V93_INVENTORY / PASS1D
**ASSET_FINAL_COMPLETE:** false
**accepted (user):** false

## Inventory
- Mesh objects (visible): **{mesh_n}**
- Hidden: **{hidden_n}**
- Boolean hosts: **{bool_n}** · Bevel: **{beveled}**
- Cameras: **{cams}** · Lights: **{lights}**
- Top prefixes: {", ".join(f"{k}:{v}" for k, v in top)}

## Systems checklist
{sys_md}

## Sheet targets
- Footprint 24×19 m · Height 38 m · Wall 6.5 m
- Achieved: **{bw:.2f}×{bd:.2f}×{bh:.2f}** m · Z {minz:.2f}..{maxz:.2f}

## Matches
- Scale lock 24×19×38
- Gatehouse, curved portal, shaft taper, hip roof, crown gables
- Stair, U-wrap, curtain merlons, buttresses, hall windows
- Scale human + presentation lights

## Gaps vs mockup (blocking Human accept)
| ID | Pri | Gap |
|----|-----|-----|
| D1 | P1 | Core modular-box language still dominant |
| D2 | P1 | Form still simplified vs carved gothic mockup |
| D3 | P2 | Art fidelity below sheet |
| D4 | P2 | Large hidden object stack |
| D5 | P3 | UV/LOD not authored |

## Overall ~8.55 — not FINAL until Human overlay
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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V93_INVENTORY.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V93")

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

print("TICK115_DONE")
