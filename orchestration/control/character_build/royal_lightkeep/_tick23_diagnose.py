import bpy
from pathlib import Path
from mathutils import Vector
base = Path(r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep")
bpy.ops.wm.open_mainfile(filepath=str(base / "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
# Find blue/roof mats near tower (+X side, mid height) that could be the vertical slab
suspects = []
for o in bpy.data.objects:
    if o.type != "MESH" or o.hide_render:
        continue
    mats = [s.material.name if s.material else "" for s in o.material_slots]
    is_roof = any("SLATE" in m or "ROOF" in m or "CLAY_ROOF" in m for m in mats) or any(k in o.name.upper() for k in ("ROOF","GABLE","HIP","SPIRE","PAVILION"))
    d = o.dimensions
    loc = o.location
    # right of tower center, tall-ish, not main left wing
    if loc.x > 5 and loc.z > 8 and (d.z > 6 or (d.y < 3 and d.z > 4) or (max(d) > 10 and min(d) < 4)):
        suspects.append((o.name, tuple(round(v,2) for v in loc), tuple(round(v,2) for v in d), mats[:1]))
    elif is_roof and loc.x > 4:
        suspects.append((o.name, tuple(round(v,2) for v in loc), tuple(round(v,2) for v in d), mats[:1]))
print("SUSPECTS", len(suspects))
for s in sorted(suspects, key=lambda x: -x[2][2])[:40]:
    print(s)
# also list any object with x in 6..12 and large Z
print("---NEAR_TOWER_RIGHT---")
for o in sorted(bpy.data.objects, key=lambda x: x.name):
    if o.type!="MESH" or o.hide_render: continue
    if 5 < o.location.x < 20 and o.location.z > 10:
        print(o.name, tuple(round(v,2) for v in o.location), tuple(round(v,2) for v in o.dimensions))
