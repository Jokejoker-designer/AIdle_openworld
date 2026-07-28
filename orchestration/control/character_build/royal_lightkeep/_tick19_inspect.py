import bpy
from pathlib import Path
base = Path(r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep")
bpy.ops.wm.open_mainfile(filepath=str(base / "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS5_V01.blend"))
print("OBJECTS", len(bpy.data.objects))
for o in sorted(bpy.data.objects, key=lambda x: x.name):
    if o.type == 'MESH':
        mats = [s.material.name if s.material else None for s in o.material_slots]
        print(f"MESH {o.name} mats={mats} loc={tuple(round(v,2) for v in o.location)} dim={tuple(round(v,2) for v in o.dimensions)}")
    else:
        print(f"{o.type} {o.name}")
print("---MATERIALS---")
for m in bpy.data.materials:
    print(m.name)
print("---CAMERAS---")
for o in bpy.data.objects:
    if o.type=='CAMERA':
        print(o.name, tuple(round(v,2) for v in o.location))
print("---LIGHTS---")
for o in bpy.data.objects:
    if o.type=='LIGHT':
        print(o.name, o.data.type, o.data.energy)
