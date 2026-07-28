# -*- coding: utf-8 -*-
"""PASS 1D fix: shorten tower shaft, ensure roof continuity, pull cameras for full silhouette."""
from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Vector

BLEND = Path(
    r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep\ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS1D.blend"
)
RENDER = Path(r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep\renders_pass1d")


def zr(obj):
    cs = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    zs = [c.z for c in cs]
    return min(zs), max(zs)


def main():
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))

    shaft = bpy.data.objects.get("TOWER_SHAFT")
    obs = bpy.data.objects.get("TOWER_OBSERVATION_BLOCK")
    roof = bpy.data.objects.get("TOWER_ROOF_BLOCK")
    peak = bpy.data.objects.get("TOWER_ROOF_PEAK")
    gh = bpy.data.objects.get("TOWER_GATEHOUSE_BASE")
    mast = bpy.data.objects.get("TOWER_FLAG_MAST")
    flag = bpy.data.objects.get("TOWER_FLAG")

    # Shorten shaft height visually: scale Z to ~0.72 and re-seat on gatehouse
    if shaft and gh:
        _, gh_top = zr(gh)
        # target shaft height ~14.5m
        target_h = 14.5
        cur_h = shaft.dimensions.z
        if cur_h > 0.1:
            shaft.dimensions.z = target_h
            bpy.context.view_layer.objects.active = shaft
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        # place shaft center so bottom sits on gh top
        shaft.location.z = gh_top + target_h * 0.5
        print(f"[1Dfix] shaft reseated h={target_h} z={shaft.location.z:.2f}")

    if shaft and obs:
        _, sh_top = zr(shaft)
        oh = obs.dimensions.z
        obs.location.z = sh_top + oh * 0.5
        # slightly widen obs
        obs.dimensions.x = max(obs.dimensions.x, 10.5)
        obs.dimensions.y = max(obs.dimensions.y, 10.5)
        bpy.context.view_layer.objects.active = obs
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        obs.location.z = sh_top + obs.dimensions.z * 0.5
        print(f"[1Dfix] obs on shaft top z={obs.location.z:.2f}")

    if obs and roof:
        _, ot = zr(obs)
        roof.location.z = ot + roof.dimensions.z * 0.35
        if peak:
            peak.location.z = ot + 3.5
        for i in range(4):
            sb = bpy.data.objects.get(f"TOWER_SPIRE_BASE_{i}")
            sp = bpy.data.objects.get(f"TOWER_SPIRE_{i}")
            oc = bpy.data.objects.get(f"TOWER_OBS_CORNER_{i}")
            if oc:
                oc.location.z = obs.location.z
            if sb:
                sb.location.z = ot + 1.5
            if sp:
                sp.location.z = ot + 4.0
        if mast:
            mast.location.z = ot + 6.5
        if flag:
            flag.location.z = ot + 7.5
        print("[1Dfix] roof/spires snapped to obs")

    # Widen barracks slightly for stronger horizontal front
    bar = bpy.data.objects.get("BARRACKS_LEFT_MAIN")
    if bar:
        bar.dimensions.x = max(bar.dimensions.x, 24.0)
        bpy.context.view_layer.objects.active = bar
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        # keep center roughly left
        bar.location.x = -12.5

    broof = bpy.data.objects.get("BARRACKS_LEFT_ROOF")
    if broof and bar:
        broof.dimensions.x = bar.dimensions.x + 1.2
        bpy.context.view_layer.objects.active = broof
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        broof.location.x = bar.location.x
        broof.location.z = zr(bar)[1] + broof.dimensions.z * 0.4

    # Cameras farther + lower angle so full 38m fits
    target = Vector((0.0, 0.0, 14.0))
    specs = {
        "CAM_01_FRONT": ((0.0, 105.0, 38.0), 35),
        "CAM_02_REAR": ((0.0, -105.0, 38.0), 35),
        "CAM_03_LEFT": ((-105.0, 2.0, 38.0), 35),
        "CAM_04_RIGHT": ((105.0, 2.0, 38.0), 35),
        "CAM_05_FRONT_3Q": ((68.0, 82.0, 42.0), 36),
        "CAM_06_REAR_3Q": ((-68.0, -82.0, 42.0), 36),
    }
    for name, (loc, lens) in specs.items():
        cam = bpy.data.objects.get(name)
        if not cam:
            continue
        cam.location = loc
        cam.data.lens = lens
        cam.data.clip_end = 800
        direction = target - cam.location
        cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))

    scene = bpy.context.scene
    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"):
        try:
            scene.render.engine = eng
            break
        except Exception:
            continue
    scene.render.image_settings.file_format = "PNG"
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 1050
    RENDER.mkdir(parents=True, exist_ok=True)
    for name in specs:
        cam = bpy.data.objects.get(name)
        if not cam:
            continue
        scene.camera = cam
        fp = RENDER / f"{name}.png"
        scene.render.filepath = str(fp)
        bpy.ops.render.render(write_still=True)
        print("[1Dfix] rendered", fp.name)

    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    print("[1Dfix] done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
