# -*- coding: utf-8 -*-
"""Hard-snap tower observation+roof onto shaft; re-render."""
from pathlib import Path
import bpy
from mathutils import Vector

BLEND = Path(
    r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep\ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS1D.blend"
)
RENDER = Path(r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep\renders_pass1d")


def world_z_minmax(obj):
    corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    zs = [c.z for c in corners]
    return min(zs), max(zs)


def set_bottom_at(obj, z_bottom):
    z0, z1 = world_z_minmax(obj)
    h = z1 - z0
    # set location so world bottom = z_bottom
    # current world bottom z0, need delta
    obj.location.z += z_bottom - z0
    bpy.context.view_layer.update()
    return world_z_minmax(obj)


def main():
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    shaft = bpy.data.objects["TOWER_SHAFT"]
    obs = bpy.data.objects["TOWER_OBSERVATION_BLOCK"]
    roof = bpy.data.objects["TOWER_ROOF_BLOCK"]
    peak = bpy.data.objects.get("TOWER_ROOF_PEAK")
    _, shaft_top = world_z_minmax(shaft)
    print("shaft_top", shaft_top)

    # Overlap slightly so no visual gap
    z0, z1 = set_bottom_at(obs, shaft_top - 0.15)
    print("obs", z0, z1)
    _, obs_top = world_z_minmax(obs)

    set_bottom_at(roof, obs_top - 0.2)
    if peak:
        _, rt = world_z_minmax(roof)
        peak.location.z = rt - 0.5

    for i in range(4):
        oc = bpy.data.objects.get(f"TOWER_OBS_CORNER_{i}")
        if oc:
            set_bottom_at(oc, shaft_top - 0.1)
        sb = bpy.data.objects.get(f"TOWER_SPIRE_BASE_{i}")
        if sb:
            set_bottom_at(sb, obs_top - 0.5)
        sp = bpy.data.objects.get(f"TOWER_SPIRE_{i}")
        if sp and sb:
            _, sbt = world_z_minmax(sb)
            sp.location.z = sbt + 1.2

    mast = bpy.data.objects.get("TOWER_FLAG_MAST")
    flag = bpy.data.objects.get("TOWER_FLAG")
    _, rt = world_z_minmax(roof)
    if mast:
        mast.location.z = rt + 1.0
    if flag:
        flag.location.z = rt + 1.8

    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))

    scene = bpy.context.scene
    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"):
        try:
            scene.render.engine = eng
            break
        except Exception:
            continue
    scene.render.image_settings.file_format = "PNG"
    for name in [
        "CAM_01_FRONT",
        "CAM_02_REAR",
        "CAM_03_LEFT",
        "CAM_04_RIGHT",
        "CAM_05_FRONT_3Q",
        "CAM_06_REAR_3Q",
    ]:
        cam = bpy.data.objects.get(name)
        if not cam:
            continue
        scene.camera = cam
        fp = RENDER / f"{name}.png"
        scene.render.filepath = str(fp)
        bpy.ops.render.render(write_still=True)
        print("rendered", name)

    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    print("snap done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
