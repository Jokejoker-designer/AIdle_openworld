import bpy
from mathutils import Vector
from pathlib import Path
base = Path(r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep")
bpy.ops.wm.open_mainfile(filepath=str(base / "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
# everything whose AABB intersects region x=5..14, z=8..22, y=0..12
for o in sorted(bpy.data.objects, key=lambda x: x.name):
    if o.type!="MESH" or o.hide_render: continue
    corners=[o.matrix_world @ Vector(c) for c in o.bound_box]
    minx=min(c.x for c in corners); maxx=max(c.x for c in corners)
    miny=min(c.y for c in corners); maxy=max(c.y for c in corners)
    minz=min(c.z for c in corners); maxz=max(c.z for c in corners)
    if maxx < 5 or minx > 14: continue
    if maxz < 8 or minz > 22: continue
    if maxy < 0 or miny > 12: continue
    mats=[s.material.name if s.material else "?" for s in o.material_slots][:1]
    print(f"{o.name:35s} {mats[0]:16s} x={minx:5.1f}..{maxx:5.1f} y={miny:5.1f}..{maxy:5.1f} z={minz:5.1f}..{maxz:5.1f}")
