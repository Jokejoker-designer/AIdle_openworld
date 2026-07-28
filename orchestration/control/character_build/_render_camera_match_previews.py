import sys
from pathlib import Path
sys.path.insert(0, r"E:\AIdle_openworld\orchestration\control\character_build")
import bpy
from cozy_camera_match_lib import place_cozy_camera, load_mockup_for_module, auto_frame_distance, render_camera_match_preview, ensure_addons

# Import V11 builders by loading the author module functions via exec of builders only is heavy;
# instead import glb + camera overlay for evidence.
GAME = Path(r"E:\AIdle_openworld\game\assets\p1e_cozy\modules")
EVID = Path(r"E:\AIdle_openworld\orchestration\evidence\town_grid_import_001\camera_match_v11")
EVID.mkdir(parents=True, exist_ok=True)
MODULES = [
    "cozy_market_stall_A","cozy_gazebo_A","cozy_well_house_A",
    "cozy_windmill_A","cozy_bridge_arch_A","cozy_watchtower_A",
]
ensure_addons()
for mid in MODULES:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    glb = GAME / f"{mid}.glb"
    bpy.ops.import_scene.gltf(filepath=str(glb))
    cam = place_cozy_camera()
    load_mockup_for_module(mid, cam)
    auto_frame_distance(cam)
    out = EVID / f"{mid}_camera_match_preview.png"
    try:
        render_camera_match_preview(out)
        print("OK", mid, out.exists(), out.stat().st_size if out.exists() else 0)
    except Exception as e:
        print("FAIL", mid, e)
print("PREVIEWS_DONE")
