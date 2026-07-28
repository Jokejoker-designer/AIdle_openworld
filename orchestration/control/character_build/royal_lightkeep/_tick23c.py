import bpy
from mathutils import Vector
from pathlib import Path
base = Path(r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep")
bpy.ops.wm.open_mainfile(filepath=str(base / "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
rows=[]
for o in bpy.data.objects:
    if o.type!="MESH" or o.hide_render: continue
    if o.name in ("PRES_GROUND","LEVEL0_GROUND","SCALE_HUMAN"): continue
    corners=[o.matrix_world @ Vector(c) for c in o.bound_box]
    minx=min(c.x for c in corners); maxx=max(c.x for c in corners)
    miny=min(c.y for c in corners); maxy=max(c.y for c in corners)
    minz=min(c.z for c in corners); maxz=max(c.z for c in corners)
    # zone right of tower shaft, front half, tall
    if minx < 14 and maxx > 5.5 and maxz > 14 and minz < 20 and maxy > 0:
        hz = maxz-minz
        if hz > 4:
            mats=[s.material.name if s.material else "?" for s in o.material_slots][:1]
            rows.append((hz, o.name, mats, (round(minx,1),round(maxx,1)), (round(miny,1),round(maxy,1)), (round(minz,1),round(maxz,1))))
rows.sort(reverse=True)
for r in rows[:30]:
    print(r)
print("N", len(rows))
