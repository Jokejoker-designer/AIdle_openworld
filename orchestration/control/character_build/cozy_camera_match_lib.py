# -*- coding: utf-8 -*-
"""Shared CozyCamera-match helpers for Blender authoring (artist-side only).

Mirrors game/scripts/camera/cozy_camera.gd locked values (READ-ONLY reference):
  pitch_degrees = 42.0
  fov           = 42.0  (perspective)
  distance      = 10.0  (default)
  follow_offset = (0, 1.1, 0)  — pivot lift; for standalone props we use (0,0.9,0)

Godot is Y-up; Blender is Z-up. Conversion applied in place_cozy_camera().
Nothing here ships in game/** or GLB — camera/background only.
"""
from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Vector, Euler

# Locked values from cozy_camera.gd — DO NOT change game code
PITCH_DEGREES = 42.0
FOV_DEGREES = 42.0
DEFAULT_DISTANCE = 10.0
# Three-quarter yaw: mockup cards face slightly from front-right
DEFAULT_YAW_DEGREES = 35.0
# Pivot height for building-centric framing (slightly below follow_offset character)
DEFAULT_PIVOT = Vector((0.0, 0.0, 0.85))

MOCKUP_DIR = Path(r"E:\AIdle_openworld\orchestration\control\visual_reference\mockup_ssot_v2\buildings")
MOCKUP_MAP = {
    "cozy_market_stall_A": "bld_05_market.jpg",
    "cozy_gazebo_A": "bld_10_gazebo.jpg",
    "cozy_well_house_A": "bld_07_well.jpg",
    "cozy_windmill_A": "bld_06_windmill.jpg",
    "cozy_bridge_arch_A": "bld_09_bridge.jpg",
    "cozy_watchtower_A": "bld_08_watchtower.jpg",
}


def ensure_addons():
    """Enable authorized artist tools if present (no-op if missing)."""
    import addon_utils
    for name in ("fspy_blender", "real_scale_references"):
        try:
            addon_utils.enable(name, default_set=True, persistent=True)
        except Exception as e:
            print(f"[cozy_camera_match] addon enable skip {name}: {e}")


def place_cozy_camera(
    name: str = "CozyCameraMatch",
    pitch_deg: float = PITCH_DEGREES,
    fov_deg: float = FOV_DEGREES,
    distance: float = DEFAULT_DISTANCE,
    yaw_deg: float = DEFAULT_YAW_DEGREES,
    pivot: Vector | None = None,
) -> bpy.types.Object:
    """Place a perspective camera matching cozy_camera.gd spherical offset.

    Godot (Y-up):
      offset = (sin(yaw)*cos(pitch), sin(pitch), cos(yaw)*cos(pitch)) * distance
      look_at(pivot)

    Blender (Z-up): map Godot (x,y,z) -> Blender (x, -z, y)
    """
    if pivot is None:
        pivot = DEFAULT_PIVOT.copy()
    pitch = math.radians(pitch_deg)
    yaw = math.radians(yaw_deg)
    # Godot Y-up offset
    gx = math.sin(yaw) * math.cos(pitch) * distance
    gy = math.sin(pitch) * distance
    gz = math.cos(yaw) * math.cos(pitch) * distance
    # -> Blender Z-up
    loc = Vector((gx, -gz, gy)) + Vector((pivot.x, pivot.y, pivot.z))

    # remove existing
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
    cam_data = bpy.data.cameras.new(name)
    cam_data.type = "PERSP"
    cam_data.lens_unit = "FOV"
    cam_data.angle = math.radians(fov_deg)
    cam_obj = bpy.data.objects.new(name, cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    cam_obj.location = loc

    # look at pivot (Blender track)
    direction = Vector((pivot.x, pivot.y, pivot.z)) - loc
    rot_quat = direction.to_track_quat("-Z", "Y")
    cam_obj.rotation_euler = rot_quat.to_euler()

    bpy.context.scene.camera = cam_obj
    # store custom props for receipts
    cam_obj["cozy_pitch_degrees"] = pitch_deg
    cam_obj["cozy_fov_degrees"] = fov_deg
    cam_obj["cozy_distance"] = distance
    cam_obj["cozy_yaw_degrees"] = yaw_deg
    cam_obj["cozy_source"] = "cozy_camera.gd read-only lock"
    return cam_obj


def set_camera_background(cam_obj: bpy.types.Object, image_path: Path, alpha: float = 0.55) -> bool:
    """Attach mockup image as camera background (artist overlay)."""
    image_path = Path(image_path)
    if not image_path.is_file():
        print(f"[cozy_camera_match] missing bg {image_path}")
        return False
    img = bpy.data.images.load(str(image_path), check_existing=True)
    cam = cam_obj.data
    # clear existing
    while cam.background_images:
        cam.background_images.remove(cam.background_images[0])
    bg = cam.background_images.new()
    bg.image = img
    bg.alpha = alpha
    bg.display_depth = "BACK"
    bg.frame_method = "FIT"
    cam.show_background_images = True
    return True


def load_mockup_for_module(module_id: str, cam_obj: bpy.types.Object | None = None) -> dict:
    fname = MOCKUP_MAP.get(module_id)
    if not fname:
        return {"ok": False, "error": "no mockup map"}
    path = MOCKUP_DIR / fname
    cam = cam_obj or bpy.context.scene.camera
    if cam is None:
        cam = place_cozy_camera()
    ok = set_camera_background(cam, path)
    return {
        "ok": ok,
        "module_id": module_id,
        "mockup_path": str(path),
        "mockup_file": fname,
        "camera": cam.name if cam else None,
        "pitch": PITCH_DEGREES,
        "fov": FOV_DEGREES,
    }


def mesh_world_bounds(objects=None) -> tuple[Vector, Vector] | None:
    """Axis-aligned world bounds of mesh objects."""
    if objects is None:
        objects = [o for o in bpy.data.objects if o.type == "MESH"]
    mins = Vector((1e9, 1e9, 1e9))
    maxs = Vector((-1e9, -1e9, -1e9))
    any_m = False
    for o in objects:
        if o.type != "MESH":
            continue
        for corner in o.bound_box:
            w = o.matrix_world @ Vector(corner)
            mins.x = min(mins.x, w.x)
            mins.y = min(mins.y, w.y)
            mins.z = min(mins.z, w.z)
            maxs.x = max(maxs.x, w.x)
            maxs.y = max(maxs.y, w.y)
            maxs.z = max(maxs.z, w.z)
            any_m = True
    if not any_m:
        return None
    return mins, maxs


def auto_frame_distance(cam_obj: bpy.types.Object, margin: float = 1.35) -> float:
    """Adjust camera distance so mesh roughly fills FOV (keeps pitch/yaw/fov locked)."""
    bb = mesh_world_bounds()
    if not bb:
        return float(cam_obj.get("cozy_distance", DEFAULT_DISTANCE))
    mins, maxs = bb
    size = maxs - mins
    # characteristic size
    char = max(size.x, size.y, size.z, 0.5)
    # FOV half-angle
    half = math.radians(FOV_DEGREES) * 0.5
    # distance so char fills ~frame with margin
    dist = (char * 0.5 * margin) / max(math.tan(half), 1e-4)
    dist = max(4.0, min(16.0, dist))
    pitch = math.radians(PITCH_DEGREES)
    yaw = math.radians(float(cam_obj.get("cozy_yaw_degrees", DEFAULT_YAW_DEGREES)))
    pivot = (mins + maxs) * 0.5
    pivot.z = mins.z + size.z * 0.35  # slightly low pivot like mockup card
    gx = math.sin(yaw) * math.cos(pitch) * dist
    gy = math.sin(pitch) * dist
    gz = math.cos(yaw) * math.cos(pitch) * dist
    loc = Vector((gx, -gz, gy)) + pivot
    cam_obj.location = loc
    direction = pivot - loc
    cam_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam_obj["cozy_distance"] = dist
    return dist


def render_camera_match_preview(out_path: Path, res_x: int = 960, res_y: int = 960) -> Path:
    """Render current scene from cozy match camera (for silhouette compare)."""
    sc = bpy.context.scene
    # Blender 5.2: EEVEE (not EEVEE_NEXT)
    for eng in ("BLENDER_EEVEE", "BLENDER_WORKBENCH", "CYCLES"):
        try:
            sc.render.engine = eng
            break
        except Exception:
            continue
    sc.render.resolution_x = res_x
    sc.render.resolution_y = res_y
    sc.render.resolution_percentage = 100
    sc.render.filepath = str(out_path)
    sc.render.image_settings.file_format = "PNG"
    # bright studio-ish world for soft-clay readability
    world = bpy.data.worlds.new("MatchWorld") if "MatchWorld" not in bpy.data.worlds else bpy.data.worlds["MatchWorld"]
    sc.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.92, 0.90, 0.95, 1.0)
        bg.inputs[1].default_value = 1.0
    bpy.ops.render.render(write_still=True)
    return out_path


def camera_match_meta() -> dict:
    return {
        "pitch_degrees": PITCH_DEGREES,
        "fov_degrees": FOV_DEGREES,
        "default_distance": DEFAULT_DISTANCE,
        "default_yaw_degrees": DEFAULT_YAW_DEGREES,
        "source_script": "game/scripts/camera/cozy_camera.gd",
        "source_lock": "MOCKUP_DESIGN_LOCK.md section 2 (three-quarter / isometric)",
        "addons": ["fspy_blender", "real_scale_references"],
        "addons_ship_in_game": False,
        "addons_in_glb": False,
    }
