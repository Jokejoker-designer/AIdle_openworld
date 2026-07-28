# -*- coding: utf-8 -*-
"""PASS 1B — fix six cameras for full silhouette (PASS1 massing already built)."""
from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Vector

BLEND = Path(r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep\ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS1.blend")
RENDER_DIR = Path(r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep\renders_pass1")
QUAR = Path(r"E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine\ROYAL_LIGHTKEEP_PASS1_MASSING")


def look_at(obj, target: Vector):
    direction = target - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def main():
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    target = Vector((0.0, 0.0, 16.0))

    # Farther + higher so full 38m tower fits frame
    specs = {
        "CAM_01_FRONT": ((0.0, 72.0, 28.0), 40),
        "CAM_02_REAR": ((0.0, -72.0, 28.0), 40),
        "CAM_03_LEFT": ((-72.0, 2.0, 28.0), 40),
        "CAM_04_RIGHT": ((72.0, 2.0, 28.0), 40),
        "CAM_05_FRONT_3Q": ((48.0, 56.0, 32.0), 42),
        "CAM_06_REAR_3Q": ((-48.0, -56.0, 32.0), 42),
    }

    for name, (loc, lens) in specs.items():
        cam = bpy.data.objects.get(name)
        if cam is None:
            data = bpy.data.cameras.new(name)
            cam = bpy.data.objects.new(name, data)
            bpy.context.scene.collection.objects.link(cam)
        cam.location = loc
        cam.data.lens = lens
        cam.data.clip_end = 500
        look_at(cam, target)

    # Soft sun
    sun = bpy.data.objects.get("SUN_CLAY")
    if sun and sun.type == "LIGHT":
        sun.data.energy = 2.5

    scene = bpy.context.scene
    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"):
        try:
            scene.render.engine = eng
            break
        except Exception:
            continue
    scene.render.image_settings.file_format = "PNG"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.film_transparent = False

    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    QUAR.mkdir(parents=True, exist_ok=True)
    import shutil

    for name in specs:
        cam = bpy.data.objects[name]
        scene.camera = cam
        fp = RENDER_DIR / f"{name}.png"
        scene.render.filepath = str(fp)
        bpy.ops.render.render(write_still=True)
        shutil.copy2(fp, QUAR / fp.name)
        print(f"[PASS1B] rendered {fp}")

    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    print("[PASS1B] saved", BLEND)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
