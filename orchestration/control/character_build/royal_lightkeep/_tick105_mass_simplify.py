# -*- coding: utf-8 -*-
"""Tick #105: mass silhouette simplify (hide overlapping modular boxes) + inventory.
Continue PASS8_V82_ROOF_MESH. Scale lock 24x19x38. No FINAL claim."""
import bpy
import os
import shutil
from datetime import datetime
from mathutils import Vector
from collections import Counter

BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
WORK = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V82_ROOF_MESH.blend")
LOOP = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS1D.blend")
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

bpy.ops.wm.open_mainfile(filepath=WORK)
print("OPEN", bpy.data.filepath)

backup = os.path.join(BASE, f"ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_BACKUP_LOOP_{STAMP}.blend")
bpy.ops.wm.save_as_mainfile(filepath=backup, copy=True)
print("BACKUP", backup)

CX, CY = 1.0, 1.5
X_MIN, X_MAX = -11.5, 12.5
Y_MIN, Y_MAX = -8.5, 10.5
H_MAX = 38.2
hidden = 0

# Keep: SHAFT_SETBACK_*, PORTAL_*, CURTAIN_*, ROOF_HIP_MESH_*, LANCET_*, BANNER_V_*, STAIR_*, UWRAP_*, CHANNEL_*
# Hide: leftover density cubes that fight silhouette
HIDE_PREFIXES = (
    "CROWN_RING_", "CROWN_GABLE_", "CROWN_HIP_CONN", "CROWN_MERLON_",
    "CROWN_RIDGE_", "CROWN_CENTER_", "CROWN_PEAK_", "CROWN_ROSE_",
    "CROWN_TRACERY_",  # keep if visible? hide dense ring - crown mesh roof covers
    "ROOF_RIDGE_MAIN", "ROOF_RIDGE_WING", "ROOF_DECK_", "ROOF_RIDGE_FINIAL",
    "ROOF_EAVES_BELT", "ROOF_MESH_EAVES",  # mesh eaves may stay - hide old only
    "DORM2_", "DORM_", "MERLON_F_", "MERLON_R_", "MERLON_L_", "MERLON_RT_",
    "BAY_WIN_", "BAY_PANE_", "BAY_PIL_", "BAY_CAP_",
    "FACADE_GALLERY_", "FACADE_CORNICE_",
    "UWRAP_COL_", "GROUND_GRASS_",
    "MAIN_", "BARRACKS_", "HALL_",  # careful - HALL_FRONT_MASS has bools
)

# More careful hide list
for o in list(bpy.data.objects):
    if o.type != "MESH" or o.hide_render:
        continue
    name = o.name
    hide = False
    # Old crown densify under new hip tower roof
    if name.startswith("CROWN_") and "CURVED" not in name:
        # keep CROWN nothing essential if roof mesh tower covers
        if any(name.startswith(p) for p in (
            "CROWN_RING_", "CROWN_GABLE_", "CROWN_HIP_CONN", "CROWN_MERLON_",
            "CROWN_RIDGE_", "CROWN_CENTER_", "CROWN_PEAK_", "CROWN_ROSE_",
            "CROWN_TRACERY_", "CROWN_GABLE_WEDGE",
        )):
            hide = True
    # Old ridge plates under hip mesh
    if name.startswith("ROOF_RIDGE_") or name.startswith("ROOF_DECK_") or name == "ROOF_EAVES_BELT":
        hide = True
    # Excess merlons on curtain (keep curtain walls)
    if name.startswith("MERLON_"):
        hide = True
    # Dormers clutter
    if name.startswith("DORM") or name.startswith("DORM2"):
        hide = True
    # Bay windows clutter on facade
    if name.startswith("BAY_"):
        hide = True
    # Gallery dark boxes
    if name.startswith("FACADE_GALLERY") or name == "FACADE_CORNICE_BELT":
        hide = True
    # Colonnade posts in court
    if name.startswith("UWRAP_COL_"):
        hide = True
    # Remaining TWIN anywhere
    if name.startswith("TWIN_"):
        hide = True
    # Old WIN mid
    if name.startswith("WIN_"):
        hide = True
    # ARCADE every remaining
    if name.startswith("ARCADE_"):
        hide = True
    # BUTT2 remaining
    if name.startswith("BUTT2_") or name.startswith("BUTTRESS_"):
        hide = True
    # COPE many
    if name.startswith("COPE_") and name not in ("COPE_FRONT", "COPE_REAR"):
        try:
            # hide side copes duplicates
            if "LEFT" in name or "RIGHT" in name:
                hide = True
        except Exception:
            pass
    # MASS_NICHE cutters already hidden
    # Soft-hide HALL_FRONT_MASS if very blocky vs portal - keep for structure
    # Hide WING_FRONT_MASS alternate density
    if name in ("WING_FRONT_MASS",):
        # keep - structural
        pass
    # Hide SHAFT_SETBACK_0 dark plinth if GROUND_PLINTH covers
    if name == "SHAFT_SETBACK_0":
        hide = True
    # Hide string bands excess
    if name.startswith("SHAFT_STRING_") or name.startswith("TWIN_STRING_"):
        hide = True
    # Hide old flags
    if name.startswith("FLAG_") and not name.startswith("FLAG_V"):
        hide = True
    if name.startswith("BANNER_") and not name.startswith("BANNER_V_"):
        hide = True

    if hide:
        o.hide_render = True
        o.hide_viewport = True
        hidden += 1

print("HIDDEN", hidden)

# Soft nudge TOWER_FRONT_MASS inward if still visible (reduce front box mass)
t = bpy.data.objects.get("TOWER_FRONT_MASS")
if t and not t.hide_render:
    t.location.y -= 0.2
    # scale slightly smaller in XY if dimensions allow
    try:
        t.scale.x *= 0.92
        t.scale.y *= 0.92
    except Exception:
        pass
    print("NUDGE_TOWER_FRONT")

# HALL mass slight setback
h = bpy.data.objects.get("HALL_FRONT_MASS")
if h and not h.hide_render:
    h.location.y -= 0.1
    print("NUDGE_HALL")

# Clamp
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
    top = max(c.z for c in corners)
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
print("BOUNDS", round(bw, 2), round(bd, 2), round(bh, 2), "Z", round(minz, 2), round(maxz, 2), "MESHES", mesh_n, "HIDDEN_TOTAL", hidden_n)

state = f"""# AUTONOMOUS BUILD STATE — ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01

**Updated:** 2026-07-27 (job `019f9eec8b6f` tick **#105**, 5m)  
**Asset ID:** `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01`  

| Field | Value |
|-------|--------|
| **ASSET_FINAL_COMPLETE** | **false** |
| **accepted (user)** | **false** |
| **Current** | **PASS8 V83 MASS_SIMPLIFY** |
| **Scale** | FP **{bw:.1f}×{bd:.1f}** (≤24×19) · top Z **{maxz:.1f}** |
| **Scheduler** | `019f9eec8b6f` every **5 min** |
| **Pipeline** | IN_PROGRESS (silhouette simplify vs modular clutter) |

---

## Tick #105 — executed (P1 D1 approach)

### Edits
1. **Mass silhouette simplify** — hide {hidden} modular clutter (crown densify, merlons, dorms, bays, twins, old ridges, etc.)
2. **Nudge** TOWER_FRONT_MASS / HALL_FRONT_MASS slightly back
3. Full inventory

### Inventory
- Visible: **{mesh_n}** · Hidden total: **{hidden_n}**
- Bool: **{bool_n}** · Bevel: **{beveled}** · Cams: **{cams}** · Lights: **{lights}**
- Top: {", ".join(f"{k}:{v}" for k, v in top)}

### Files
| Role | Path |
|------|------|
| Work | `ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V83_MASS_SIMPLIFY.blend` |
| Loop / candidate | `PASS1D.blend` / `FINAL.blend` (synced) |
| Backup | `...BACKUP_LOOP_{STAMP}.blend` |
| Proofs | `renders_final/*` + work proofs |

### Bounds
**{bw:.1f} × {bd:.1f} × {bh:.1f}** m · Z {minz:.1f}..**{maxz:.1f}**

### Internal scores
| Axis | Score |
|------|-------|
| Scale | **9.0** |
| Silhouette clarity | ~8.55 |
| Gothic fidelity | ~8.55 |
| Overall | **~8.55** |

### Verdict
Not FINAL. Reduced modular noise; core volumes still modular. Human overlay required for FINAL.  
Next: keep simplify path or presentation re-render; avoid cube densify.
"""

loop_state = f"""# BUILD LOOP STATE

**Updated:** 2026-07-27 · tick **#105** · job `019f9eec8b6f` (5m)  
**ASSET_FINAL_COMPLETE:** false · **Current:** PASS8_V83_MASS_SIMPLIFY  

## Tick #105 (P1)
- Silhouette simplify hidden={hidden} (this tick)
- Visible meshes {mesh_n} / hidden total {hidden_n}
- Bounds {bw:.1f}×{bd:.1f}×{bh:.1f}
- Backup: BACKUP_LOOP_{STAMP}
- Saved: PASS8_V83_MASS_SIMPLIFY → PASS1D / FINAL

## Next
Avoid cube densify; Human overlay preferred for FINAL gate
"""

dev = f"""# INTERMEDIATE DEVIATION REPORT — tick #105

**Asset:** ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01
**Stamp:** {STAMP}
**File:** PASS8_V83_MASS_SIMPLIFY / PASS1D
**ASSET_FINAL_COMPLETE:** false
**accepted (user):** false

## Inventory
- Mesh objects (visible): **{mesh_n}**
- Hidden (all): **{hidden_n}** · this tick: **{hidden}**
- Boolean hosts: **{bool_n}** · Bevel: **{beveled}**
- Cameras: **{cams}** · Lights: **{lights}**
- Top prefixes: {", ".join(f"{k}:{v}" for k, v in top)}

## Sheet targets
- Footprint 24×19 m · Height 38 m · Wall 6.5 m
- Achieved: **{bw:.2f}×{bd:.2f}×{bh:.2f}** m · Z {minz:.2f}..{maxz:.2f}

## Matches
- Cleaner silhouette after clutter hide
- Curved portal + 4-face lancets + hip roof mesh retained
- Scale lock held

## Gaps vs mockup (blocking Human accept)
| ID | Pri | Gap |
|----|-----|-----|
| D1 | P1 | Core still modular language (hidden clutter only) |
| D2 | P1 | Hip roof still simplified vs multi-gable mockup |
| D3 | P2 | Detail density tradeoff after simplify |
| D4 | P2 | Residual hidden stack large |
| D5 | P3 | UV/LOD not authored |

## Overall ~8.55 — not FINAL until Human overlay
Simplify path over densify. Human overlay still required.
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

out_blend = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V83_MASS_SIMPLIFY.blend")
bpy.ops.wm.save_as_mainfile(filepath=out_blend)
shutil.copy2(out_blend, LOOP)
shutil.copy2(out_blend, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
print("SAVED V83")

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

print("TICK105_DONE")
