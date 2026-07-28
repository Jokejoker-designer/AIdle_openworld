import bpy
from mathutils import Vector
from pathlib import Path
base = Path(r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep")
bpy.ops.wm.open_mainfile(filepath=str(base / "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
# List SLATE objects sorted by how "vertical wall like" they are (high Z, moderate X, near tower)
rows=[]
for o in bpy.data.objects:
    if o.type!="MESH" or o.hide_render: continue
    mats=[s.material.name if s.material else "" for s in o.material_slots]
    if not any("SLATE" in m or "BANNER" in m for m in mats):
        continue
    d=o.dimensions; loc=o.location
    # bounding box world
    corners=[o.matrix_world @ Vector(c) for c in o.bound_box]
    minx=min(c.x for c in corners); maxx=max(c.x for c in corners)
    miny=min(c.y for c in corners); maxy=max(c.y for c in corners)
    minz=min(c.z for c in corners); maxz=max(c.z for c in corners)
    # near tower right zone for front camera
    if maxx > 4 and minx < 20 and maxz > 12 and miny < 12:
        wallness = (maxz-minz) / max(maxx-minx, 0.1)
        rows.append((wallness, o.name, mats[0] if mats else "", 
            (round(minx,1),round(maxx,1)), (round(miny,1),round(maxy,1)), (round(minz,1),round(maxz,1)),
            tuple(round(v,1) for v in d)))
rows.sort(reverse=True)
for r in rows[:25]:
    print(r)
print("COUNT", len(rows))
