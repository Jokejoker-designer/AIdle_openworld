import bpy
from pathlib import Path
base = Path(r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep")
bpy.ops.wm.open_mainfile(filepath=str(base / "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V01.blend"))
keys = ("ROOF","SPIRE","HIP","GABLE","CROWN","BARRACKS","BAR_","RIGHT_","STAIR","PEAK","FINIAL","PAVILION","CORNER")
for o in sorted(bpy.data.objects, key=lambda x: x.name):
    if o.type != "MESH":
        continue
    n = o.name.upper()
    if any(k in n for k in keys):
        print(f"{o.name} loc={tuple(round(v,2) for v in o.location)} dim={tuple(round(v,2) for v in o.dimensions)}")
print("TOTAL", len([o for o in bpy.data.objects if o.type=="MESH"]))
