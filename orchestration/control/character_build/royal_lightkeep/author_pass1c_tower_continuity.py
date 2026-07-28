# -*- coding: utf-8 -*-
"""PASS 1C — fix floating tower roof: snap roof/obs/pinnacles into continuous mass."""
from __future__ import annotations

from pathlib import Path
import bpy
from mathutils import Vector

BLEND = Path(
    r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep\ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS1.blend"
)
RENDER_DIR = Path(
    r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep\renders_pass1"
)


def bbox(obj):
    return [obj.matrix_world @ Vector(c) for c in obj.bound_box]


def z_range(obj):
    cs = bbox(obj)
    zs = [c.z for c in cs]
    return min(zs), max(zs)


def main():
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))

    shaft = bpy.data.objects.get("TOWER_SHAFT")
    obs = bpy.data.objects.get("TOWER_OBS")
    roof = bpy.data.objects.get("TOWER_ROOF_CORE")
    peak = bpy.data.objects.get("TOWER_ROOF_PEAK")
    mast = bpy.data.objects.get("TOWER_FLAG_MAST")
    flag = bpy.data.objects.get("TOWER_FLAG")

    if not all([shaft, obs, roof, peak]):
        print("[PASS1C] missing tower parts")
        return 2

    # Ensure observation sits on shaft top
    s_z0, s_z1 = z_range(shaft)
    o_z0, o_z1 = z_range(obs)
    gap_so = s_z1 - o_z0
    if abs(gap_so) > 0.05:
        obs.location.z += gap_so
        print(f"[PASS1C] moved OBS by {gap_so:.3f}")

    o_z0, o_z1 = z_range(obs)
    r_z0, r_z1 = z_range(roof)
    gap_or = o_z1 - r_z0
    if abs(gap_or) > 0.05:
        roof.location.z += gap_or
        print(f"[PASS1C] moved ROOF_CORE by {gap_or:.3f}")

    r_z0, r_z1 = z_range(roof)
    # Peak: sit so base ~ roof mid-top
    peak.location.z = r_z1 - 0.5
    # Pinnacles
    for i in range(4):
        p = bpy.data.objects.get(f"TOWER_PINNACLE_{i}")
        pr = bpy.data.objects.get(f"TOWER_PINNACLE_ROOF_{i}")
        if p:
            # align base to obs top
            pz0, pz1 = z_range(p)
            p.location.z += o_z1 - pz0
            if pr:
                pr.location.z = z_range(p)[1] + 0.8
    if mast:
        mast.location.z = r_z1 + 1.2
    if flag:
        flag.location.z = r_z1 + 2.2

    # Also lower arcade if floating
    for n in ("TOWER_OBS_ARCADE_F", "TOWER_OBS_ARCADE_B"):
        a = bpy.data.objects.get(n)
        if a:
            a.location.z = obs.location.z

    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))

    # Re-render six cams
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
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
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
        fp = RENDER_DIR / f"{name}.png"
        scene.render.filepath = str(fp)
        bpy.ops.render.render(write_still=True)
        print("[PASS1C] rendered", fp)

    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    print("[PASS1C] done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
