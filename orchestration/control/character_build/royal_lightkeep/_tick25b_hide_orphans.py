import bpy, os, shutil
from mathutils import Vector
BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
path = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_V03_SILHOUETTE.blend")
bpy.ops.wm.open_mainfile(filepath=path)

# Keep list: names we want visible for front silhouette
KEEP_PREFIX = (
    "TOWER_SHAFT", "TOWER_PORTAL", "TOWER_BASE", "TOWER_OBSERVATION", "TOWER_MID_BELT",
    "TOWER_HIP_BASE", "TOWER_ROOF_BLOCK", "TOWER_ROOF_PEAK", "TOWER_CORNER_MASS",
    "TOWER_SPIRE_", "TOWER_SHOULDER", "TOWER_WIN_F", "WIN_FRAME_F",
    "GOLD_SPIRE", "GOLD_FINIAL", "FINIAL_MAIN", "GOLD_EAVES",
    "BANNER_PANEL", "EMBLEM_PLATE", "MAIN_PORTAL",
    "MAIN_STAIR_STEP_", "MAIN_STAIR_WALL_", "STAIR_RAIL_L", "STAIR_RAIL_R",
    "BARRACKS_LEFT_MAIN", "BARRACKS_LEFT_ROOF", "BARRACKS_GABLE", "BARRACKS_ROOF_GABLE",
    "BARRACKS_GABLE_CAP", "BAR_TURRET_FRONT_L",
    "RIGHT_WING_MAIN", "RIGHT_WING_ROOF", "RIGHT_ROOF_GABLE_0", "RIGHT_ROOF_GABLE_1",
    "RIGHT_ROOF_GABLE_2", "RIGHT_PAVILION", "RIGHT_CORNER_TURRET",
    "LEVEL0_GROUND", "OUTER_WALL_FRONT", "BASTION_FL", "BASTION_FR",
    "CONNECTOR_TO_BARRACKS", "CONNECTOR_ROOF",
    "PRES_GROUND", "SCALE_HUMAN", "CAM_", "KEY_LIGHT", "FILL_LIGHT", "RIM_LIGHT", "SUN",
    "MAT_", # not objects
)

def keep(name):
    n = name.upper()
    # cameras lights
    o = bpy.data.objects.get(name)
    if o and o.type in ("CAMERA", "LIGHT", "EMPTY"):
        return True
    for p in KEEP_PREFIX:
        if name.startswith(p) or name.upper().startswith(p.upper()):
            return True
    # materials not objects
    return False

hidden = 0
for o in list(bpy.data.objects):
    if o.type != "MESH":
        continue
    if keep(o.name):
        o.hide_render = False
        o.hide_viewport = False
        continue
    # hide everything else mesh
    o.hide_render = True
    o.hide_viewport = True
    hidden += 1
print("HIDDEN", hidden)

# Also hide old MAIN_STAIR_00 style if present
for o in bpy.data.objects:
    if o.type != "MESH":
        continue
    n = o.name.upper()
    if n.startswith("MAIN_STAIR_") and not n.startswith("MAIN_STAIR_STEP_") and not n.startswith("MAIN_STAIR_WALL_"):
        o.hide_render = True
        o.hide_viewport = True
        print("HIDE_OLD_STAIR", o.name)

# Fix camera look-at roughly center
import math
from mathutils import Euler
for cname, loc in [
    ("CAM_01_FRONT", (0, 90, 26)),
    ("CAM_05_FRONT_3Q", (50, 65, 30)),
]:
    c = bpy.data.objects.get(cname)
    if not c:
        continue
    c.location = Vector(loc)
    # point to origin tower
    direction = Vector((0, 4, 18)) - c.location
    c.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

scene = bpy.context.scene
try:
    scene.render.engine = "BLENDER_EEVEE_NEXT"
except Exception:
    scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 960
out = os.path.join(BASE, "renders_final")
work = os.path.join(BASE, "renders_pass1d")
for cam, dest, fn in [
    ("CAM_01_FRONT", out, "final_front.png"),
    ("CAM_05_FRONT_3Q", out, "final_front_3q.png"),
    ("CAM_01_FRONT", work, "current_front_work.png"),
    ("CAM_05_FRONT_3Q", work, "current_front_3q_work.png"),
]:
    scene.camera = bpy.data.objects.get(cam)
    scene.render.filepath = os.path.join(dest, fn)
    bpy.ops.render.render(write_still=True)
    print("OK", fn)

bpy.ops.wm.save_as_mainfile(filepath=path)
shutil.copy2(path, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend"))
shutil.copy2(path, os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS1D.blend"))
print("SAVED clean")
