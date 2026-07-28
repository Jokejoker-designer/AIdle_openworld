import bpy
from mathutils import Vector
from pathlib import Path
base = Path(r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep")
bpy.ops.wm.open_mainfile(filepath=str(base / "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
for o in sorted(bpy.data.objects, key=lambda x: x.name):
    if o.type!="MESH": continue
    n=o.name.upper()
    if "RIGHT" in n or "WING" in n or "CONNECTOR" in n or n.startswith("GH_"):
        mats=[s.material.name if s.material else "?" for s in o.material_slots][:1]
        corners=[o.matrix_world @ Vector(c) for c in o.bound_box]
        minx=min(c.x for c in corners); maxx=max(c.x for c in corners)
        minz=min(c.z for c in corners); maxz=max(c.z for c in corners)
        print(f"{o.name:40s} mat={mats[0]:16s} x={minx:6.1f}..{maxx:6.1f} z={minz:5.1f}..{maxz:5.1f} dim={tuple(round(v,1) for v in o.dimensions)} hide={o.hide_render}")
