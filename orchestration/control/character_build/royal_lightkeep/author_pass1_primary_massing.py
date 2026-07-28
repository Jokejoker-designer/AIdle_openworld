# -*- coding: utf-8 -*-
"""PASS 1 — PRIMARY MASSING
ASSET: ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01
Watchtower + Barracks Complex — Royal Lightkeep

Clay blockout only: footprint ~24×19 m, tower ~38 m, walls ~6.5 m.
Six orthographic-ish / hero cameras matching mockup views 1–6.
No materials ornament. No foliage detail. No interior.
"""
from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Euler, Vector

JOB = "ROYAL_LIGHTKEEP_PASS1_MASSING"
ASSET_ID = "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01"
OUT = Path(r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep")
BLEND = OUT / "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS1.blend"
RENDER_DIR = OUT / "renders_pass1"
QUAR = Path(r"E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine") / JOB

# Scale (meters)
FOOT_X = 24.0  # left-right extent
FOOT_Y = 19.0  # front-back depth
TOWER_H = 38.0
WALL_H = 6.5
HUMAN = 1.8


def log(m: str) -> None:
    print(f"[{JOB}] {m}")


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in list(bpy.data.meshes):
        bpy.data.meshes.remove(block)
    for block in list(bpy.data.materials):
        bpy.data.materials.remove(block)
    for block in list(bpy.data.cameras):
        bpy.data.cameras.remove(block)
    for block in list(bpy.data.lights):
        bpy.data.lights.remove(block)
    for block in list(bpy.data.collections):
        if block.name not in ("Collection", "Scene Collection"):
            bpy.data.collections.remove(block)


def setup_units() -> None:
    s = bpy.context.scene
    s.unit_settings.system = "METRIC"
    s.unit_settings.scale_length = 1.0
    s.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in dir(bpy.types.RenderSettings) else "BLENDER_EEVEE"
    try:
        s.render.engine = "CYCLES"
    except Exception:
        pass
    s.render.resolution_x = 1280
    s.render.resolution_y = 960
    s.render.resolution_percentage = 100
    s.render.film_transparent = False
    world = bpy.data.worlds.new("World_Clay") if "World_Clay" not in bpy.data.worlds else bpy.data.worlds["World_Clay"]
    s.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.82, 0.84, 0.86, 1.0)
        bg.inputs[1].default_value = 1.0


def mat_clay(name: str, rgba=(0.55, 0.55, 0.55, 1.0)) -> bpy.types.Material:
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = 0.85
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = 0.0
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = 0.1
        elif "Specular" in bsdf.inputs:
            bsdf.inputs["Specular"].default_value = 0.1
    return m


def assign(obj, mat):
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def box(name: str, loc, size, mat, coll=None) -> bpy.types.Object:
    """loc = center; size = full extents XYZ meters."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = (size[0], size[1], size[2])
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # after apply, cube is unit; re-scale to size
    # Actually with size=1 and scale applied, dimensions = scale. Fix:
    # Better: create then set dimensions
    o.dimensions = Vector(size)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.location = Vector(loc)
    assign(o, mat)
    if coll:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        coll.objects.link(o)
    return o


def ensure_collection(name: str) -> bpy.types.Collection:
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c


def add_human_ref(coll, mat) -> None:
    # 1.8 m human silhouette proxy at front stairs
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=1.8, location=(0.0, 11.5, 0.9))
    o = bpy.context.active_object
    o.name = "SCALE_REF_HUMAN_1M8"
    assign(o, mat)
    for c in list(o.users_collection):
        c.objects.unlink(o)
    coll.objects.link(o)


def build_massing() -> dict:
    mats = {
        "base": mat_clay("CLAY_BASE", (0.50, 0.50, 0.52, 1)),
        "tower": mat_clay("CLAY_TOWER", (0.58, 0.58, 0.60, 1)),
        "barracks": mat_clay("CLAY_BARRACKS", (0.54, 0.54, 0.56, 1)),
        "gate": mat_clay("CLAY_GATE", (0.52, 0.52, 0.55, 1)),
        "roof": mat_clay("CLAY_ROOF", (0.35, 0.40, 0.48, 1)),  # slightly cooler grey for roofs (still clay, no color polish)
        "wall": mat_clay("CLAY_WALL", (0.48, 0.48, 0.50, 1)),
        "stair": mat_clay("CLAY_STAIR", (0.45, 0.45, 0.47, 1)),
        "ground": mat_clay("CLAY_GROUND", (0.62, 0.64, 0.60, 1)),
        "human": mat_clay("CLAY_HUMAN", (0.25, 0.25, 0.28, 1)),
    }

    root = ensure_collection("ROYAL_LIGHTKEEP_ROOT")
    c_base = ensure_collection("LOWER_FORTIFIED_BASE")
    c_tower = ensure_collection("WATCHTOWER_MAIN")
    c_bar = ensure_collection("BARRACKS_LEFT_WING")
    c_gate = ensure_collection("SERVICE_GATE_RIGHT_WING")
    c_court = ensure_collection("CENTRAL_COURTYARD")
    c_stair = ensure_collection("STAIRS")
    c_roof = ensure_collection("ROOF_BLOCKOUT")
    c_turret = ensure_collection("CORNER_TURRETS")
    c_cam = ensure_collection("CAMERAS_MOCKUP_6")
    c_ref = ensure_collection("SCALE_REF")

    for c in (c_base, c_tower, c_bar, c_gate, c_court, c_stair, c_roof, c_turret, c_cam, c_ref):
        if c.name not in [x.name for x in root.children]:
            root.children.link(c)

    # Coordinate: origin ground center of footprint
    # Footprint X [-12, 12], Y [-9.5, 9.5]
    # +Y = front

    # --- Ground plane ---
    box("LEVEL_00_GROUND", (0, 0, -0.25), (40, 36, 0.5), mats["ground"], c_base)

    # --- Lower fortified base / plinth (LEVEL_01) ~6.5m walls on outer ---
    # Main podium under whole complex
    box("BASE_PODIUM", (0, 0, 1.0), (23.5, 18.5, 2.0), mats["base"], c_base)

    # Outer low walls (parapet mass)
    # Front wall segments (split for gate/stair openings later)
    box("WALL_FRONT_L", (-7.5, 9.0, WALL_H * 0.5), (7.0, 1.2, WALL_H), mats["wall"], c_base)
    box("WALL_FRONT_R", (8.0, 9.0, WALL_H * 0.5), (5.5, 1.2, WALL_H), mats["wall"], c_base)
    box("WALL_REAR", (0, -9.0, WALL_H * 0.5), (22.0, 1.2, WALL_H), mats["wall"], c_base)
    box("WALL_LEFT", (-11.5, 0.0, WALL_H * 0.5), (1.2, 17.0, WALL_H), mats["wall"], c_base)
    box("WALL_RIGHT", (11.5, 0.5, WALL_H * 0.5), (1.2, 16.0, WALL_H), mats["wall"], c_base)

    # Terrace LEVEL_02
    box("TERRACE_MAIN", (0, 1.0, 2.6), (20.0, 14.0, 0.6), mats["base"], c_base)

    # --- CENTRAL COURTYARD (void approximation: lower courtyard pad) ---
    box("COURTYARD_PAD", (2.5, -1.0, 2.15), (8.0, 7.0, 0.3), mats["ground"], c_court)

    # =========================================================
    # WATCHTOWER_MAIN — slightly right of center, front-biased
    # =========================================================
    # Tower footprint ~6.5 x 6.5, base at terrace
    tw_x, tw_y = 2.2, 1.5  # center of tower
    tw_w, tw_d = 6.8, 6.8

    # 5.1 Tower base (includes grand portal mass)
    box("TOWER_BASE", (tw_x, tw_y, 4.0), (tw_w + 1.2, tw_d + 0.8, 5.0), mats["tower"], c_tower)
    # Portal frame extrusion front
    box("TOWER_PORTAL_FRAME", (tw_x, tw_y + tw_d * 0.5 + 0.4, 4.5), (3.6, 1.4, 5.5), mats["tower"], c_tower)

    # 5.2 Tower shaft
    shaft_h = 16.0
    shaft_z = 4.0 + 2.5 + shaft_h * 0.5
    box("TOWER_SHAFT", (tw_x, tw_y, shaft_z), (tw_w * 0.92, tw_d * 0.92, shaft_h), mats["tower"], c_tower)

    # Banner plane (clay mass)
    box("TOWER_BANNER_FRONT", (tw_x, tw_y + tw_d * 0.46, 18.0), (2.2, 0.15, 5.5), mats["roof"], c_tower)

    # 5.3 Observation level (slightly wider)
    obs_h = 5.5
    obs_z = 4.0 + 2.5 + shaft_h + obs_h * 0.5
    box("TOWER_OBS", (tw_x, tw_y, obs_z), (tw_w * 1.15, tw_d * 1.15, obs_h), mats["tower"], c_tower)
    # Arcade hint (four side shelves)
    box("TOWER_OBS_ARCADE_F", (tw_x, tw_y + tw_d * 0.55, obs_z), (tw_w * 1.05, 0.6, obs_h * 0.7), mats["tower"], c_tower)
    box("TOWER_OBS_ARCADE_B", (tw_x, tw_y - tw_d * 0.55, obs_z), (tw_w * 1.05, 0.6, obs_h * 0.7), mats["tower"], c_tower)

    # 5.4 Tower roof mass (steep pavilion)
    roof_h = 9.0
    roof_z = obs_z + obs_h * 0.5 + roof_h * 0.45
    box("TOWER_ROOF_CORE", (tw_x, tw_y, roof_z), (tw_w * 1.25, tw_d * 1.25, roof_h * 0.55), mats["roof"], c_roof)
    # Peak
    bpy.ops.mesh.primitive_cone_add(
        vertices=4,
        radius1=tw_w * 0.75,
        radius2=0.15,
        depth=roof_h * 0.85,
        location=(tw_x, tw_y, roof_z + roof_h * 0.25),
    )
    peak = bpy.context.active_object
    peak.name = "TOWER_ROOF_PEAK"
    peak.rotation_euler = Euler((0, 0, math.radians(45)), "XYZ")
    assign(peak, mats["roof"])
    for c in list(peak.users_collection):
        c.objects.unlink(peak)
    c_roof.objects.link(peak)

    # Corner pinnacles on tower roof
    for i, (dx, dy) in enumerate([(-1, -1), (-1, 1), (1, -1), (1, 1)]):
        px = tw_x + dx * tw_w * 0.55
        py = tw_y + dy * tw_d * 0.55
        box(f"TOWER_PINNACLE_{i}", (px, py, roof_z + 1.5), (1.1, 1.1, 4.5), mats["tower"], c_turret)
        bpy.ops.mesh.primitive_cone_add(
            vertices=4, radius1=0.7, radius2=0.05, depth=2.2,
            location=(px, py, roof_z + 4.2),
        )
        cone = bpy.context.active_object
        cone.name = f"TOWER_PINNACLE_ROOF_{i}"
        cone.rotation_euler = Euler((0, 0, math.radians(45)), "XYZ")
        assign(cone, mats["roof"])
        for c in list(cone.users_collection):
            c.objects.unlink(cone)
        c_roof.objects.link(cone)

    # Flag mast
    box("TOWER_FLAG_MAST", (tw_x, tw_y, TOWER_H - 1.5), (0.2, 0.2, 3.0), mats["tower"], c_tower)
    box("TOWER_FLAG", (tw_x + 0.9, tw_y, TOWER_H - 0.3), (1.8, 0.08, 0.9), mats["roof"], c_tower)

    # =========================================================
    # BARRACKS_LEFT_WING  (-X)
    # =========================================================
    # Wing roughly X from -11.5 to +0.5, Y from -6 to +7
    bar_cx, bar_cy = -5.5, 0.5
    bar_sx, bar_sy = 11.0, 11.5
    bar_h = 11.5  # ~2 storeys + base

    box("BARRACKS_MASS", (bar_cx, bar_cy, 2.0 + bar_h * 0.5), (bar_sx, bar_sy, bar_h), mats["barracks"], c_bar)
    # Front gable mass (taller section)
    box("BARRACKS_GABLE_FRONT", (bar_cx - 1.0, bar_cy + bar_sy * 0.35, 2.0 + 7.5), (5.5, 3.5, 15.0), mats["barracks"], c_bar)
    # Roof long block
    box("BARRACKS_ROOF", (bar_cx, bar_cy, 2.0 + bar_h + 2.2), (bar_sx + 0.8, bar_sy + 0.6, 4.5), mats["roof"], c_roof)
    # Gable roof peak
    box("BARRACKS_GABLE_ROOF", (bar_cx - 1.0, bar_cy + bar_sy * 0.35, 18.5), (6.0, 4.0, 5.0), mats["roof"], c_roof)

    # Left corner turrets on barracks
    for i, (lx, ly, h) in enumerate([
        (-10.5, 6.5, 14.0),
        (-10.5, -5.0, 12.0),
        (-1.5, 6.8, 13.0),
    ]):
        box(f"BAR_TURRET_{i}", (lx, ly, 2.0 + h * 0.45), (2.2, 2.2, h * 0.9), mats["tower"], c_turret)
        bpy.ops.mesh.primitive_cone_add(
            vertices=4, radius1=1.3, radius2=0.08, depth=3.2,
            location=(lx, ly, 2.0 + h * 0.9 + 1.2),
        )
        cone = bpy.context.active_object
        cone.name = f"BAR_TURRET_ROOF_{i}"
        cone.rotation_euler = Euler((0, 0, math.radians(45)), "XYZ")
        assign(cone, mats["roof"])
        for c in list(cone.users_collection):
            c.objects.unlink(cone)
        c_roof.objects.link(cone)

    # =========================================================
    # SERVICE_GATE_RIGHT_WING (+X)
    # =========================================================
    gate_cx, gate_cy = 7.5, -0.5
    gate_sx, gate_sy = 7.0, 9.0
    gate_h = 9.0

    box("GATE_WING_MASS", (gate_cx, gate_cy, 2.0 + gate_h * 0.5), (gate_sx, gate_sy, gate_h), mats["gate"], c_gate)
    box("GATE_ROOF", (gate_cx, gate_cy, 2.0 + gate_h + 1.8), (gate_sx + 0.6, gate_sy + 0.5, 3.6), mats["roof"], c_roof)
    # Gate arch mass (rear-ish / side)
    box("GATE_ARCH_TUNNEL", (gate_cx + 0.5, gate_cy - 3.5, 4.5), (4.0, 3.5, 5.5), mats["gate"], c_gate)
    # Small turrets
    for i, (lx, ly, h) in enumerate([
        (10.2, 4.0, 12.0),
        (10.0, -5.5, 11.0),
        (5.5, -5.8, 10.5),
    ]):
        box(f"GATE_TURRET_{i}", (lx, ly, 2.0 + h * 0.4), (1.9, 1.9, h * 0.85), mats["tower"], c_turret)
        bpy.ops.mesh.primitive_cone_add(
            vertices=4, radius1=1.1, radius2=0.06, depth=2.6,
            location=(lx, ly, 2.0 + h * 0.85 + 0.9),
        )
        cone = bpy.context.active_object
        cone.name = f"GATE_TURRET_ROOF_{i}"
        cone.rotation_euler = Euler((0, 0, math.radians(45)), "XYZ")
        assign(cone, mats["roof"])
        for c in list(cone.users_collection):
            c.objects.unlink(cone)
        c_roof.objects.link(cone)

    # Connecting wall between tower and wings
    box("LINK_BARRACKS_TOWER", (-0.5, 1.5, 8.0), (3.5, 5.0, 8.0), mats["barracks"], c_bar)
    box("LINK_GATE_TOWER", (5.5, 1.0, 7.0), (2.8, 4.5, 7.0), mats["gate"], c_gate)

    # =========================================================
    # STAIRS
    # =========================================================
    # Main front stair to tower portal (+Y)
    for i in range(14):
        t = i / 13.0
        z = 0.15 + t * 5.5
        y = 11.2 - t * 3.2
        depth = 1.1
        box(f"STAIR_MAIN_{i:02d}", (tw_x, y, z), (5.5 - t * 0.8, depth, 0.35), mats["stair"], c_stair)
    # Landing
    box("STAIR_MAIN_LANDING", (tw_x, 8.2, 5.7), (5.0, 1.8, 0.4), mats["stair"], c_stair)

    # Left side diagonal stair / ramp mass (visible left view)
    for i in range(10):
        t = i / 9.0
        z = 0.2 + t * 5.8
        x = -11.0 + t * 2.5
        y = 8.5 - t * 4.0
        box(f"STAIR_LEFT_{i:02d}", (x, y, z), (2.2, 1.4, 0.35), mats["stair"], c_stair)

    # Rear side stair
    for i in range(8):
        t = i / 7.0
        z = 0.2 + t * 4.5
        y = -10.5 + t * 2.5
        box(f"STAIR_REAR_{i:02d}", (6.5, y, z), (3.0, 1.2, 0.35), mats["stair"], c_stair)

    # Human scale
    add_human_ref(c_ref, mats["human"])

    # Empty root marker
    empty = bpy.data.objects.new("ASSET_ROOT_ROYAL_LIGHTKEEP", None)
    empty.empty_display_type = "PLAIN_AXES"
    empty.empty_display_size = 2.0
    empty.location = (0, 0, 0)
    root.objects.link(empty)

    dims = {
        "footprint_m": [FOOT_X, FOOT_Y],
        "tower_height_m": TOWER_H,
        "wall_height_m": WALL_H,
        "tower_center_xy": [tw_x, tw_y],
        "barracks_center_xy": [bar_cx, bar_cy],
        "gate_center_xy": [gate_cx, gate_cy],
        "human_ref_m": HUMAN,
    }
    return dims


def setup_cameras() -> list:
    """Six cameras matching mockup panels. +Y front."""
    cams = []
    # Target look-at roughly building center mass
    target = Vector((0.0, 0.0, 14.0))

    def make_cam(name, loc, lens=50):
        data = bpy.data.cameras.new(name)
        data.lens = lens
        data.clip_end = 500
        obj = bpy.data.objects.new(name, data)
        obj.location = loc
        # look at target
        direction = target - obj.location
        obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        bpy.context.scene.collection.objects.link(obj)
        # move to camera collection
        for c in bpy.data.collections:
            if c.name == "CAMERAS_MOCKUP_6":
                for uc in list(obj.users_collection):
                    uc.objects.unlink(obj)
                c.objects.link(obj)
                break
        cams.append(obj)
        return obj

    # 1 FRONT — looking from +Y toward origin
    make_cam("CAM_01_FRONT", (0.0, 42.0, 18.0), 45)
    # 2 REAR — from -Y
    make_cam("CAM_02_REAR", (0.0, -42.0, 18.0), 45)
    # 3 LEFT SIDE — from -X
    make_cam("CAM_03_LEFT", (-42.0, 0.0, 18.0), 45)
    # 4 RIGHT SIDE — from +X
    make_cam("CAM_04_RIGHT", (42.0, 0.0, 18.0), 45)
    # 5 FRONT 3/4
    make_cam("CAM_05_FRONT_3Q", (28.0, 34.0, 20.0), 48)
    # 6 REAR 3/4
    make_cam("CAM_06_REAR_3Q", (-28.0, -34.0, 20.0), 48)

    # Fix look-at more carefully
    for cam in cams:
        direction = target - cam.location
        rot_quat = direction.to_track_quat("-Z", "Y")
        cam.rotation_euler = rot_quat.to_euler()

    return cams


def setup_light() -> None:
    bpy.ops.object.light_add(type="SUN", location=(20, -15, 50))
    sun = bpy.context.active_object
    sun.name = "SUN_CLAY"
    sun.data.energy = 3.0
    sun.rotation_euler = Euler((math.radians(45), math.radians(15), math.radians(-30)), "XYZ")
    bpy.ops.object.light_add(type="AREA", location=(-15, 20, 25))
    fill = bpy.context.active_object
    fill.name = "FILL_CLAY"
    fill.data.energy = 400
    fill.data.size = 30


def render_views(cams: list) -> list:
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    QUAR.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    # Prefer EEVEE for speed
    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"):
        try:
            scene.render.engine = eng
            break
        except Exception:
            continue
    scene.render.image_settings.file_format = "PNG"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    paths = []
    for cam in cams:
        scene.camera = cam
        fp = RENDER_DIR / f"{cam.name}.png"
        scene.render.filepath = str(fp)
        bpy.ops.render.render(write_still=True)
        paths.append(str(fp))
        log(f"rendered {fp.name}")
        # copy quarantine
        try:
            import shutil
            shutil.copy2(fp, QUAR / fp.name)
        except Exception:
            pass
    return paths


def main() -> int:
    log("PASS 1 PRIMARY MASSING start")
    OUT.mkdir(parents=True, exist_ok=True)
    clear_scene()
    setup_units()
    dims = build_massing()
    cams = setup_cameras()
    setup_light()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    log(f"saved blend {BLEND}")
    paths = render_views(cams)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))

    report = {
        "pass": "PASS_1_PRIMARY_MASSING",
        "asset_id": ASSET_ID,
        "blend": str(BLEND),
        "renders": paths,
        "dimensions": dims,
        "objects_created_count": len([o for o in bpy.data.objects if o.type == "MESH"]),
        "cameras": [c.name for c in cams],
        "materials": "CLAY_ONLY",
        "accepted": False,
        "self_accept": False,
        "note": "Blockout only — no ornament, no final materials, six-view clay proof",
    }
    import json
    (OUT / "PASS1_REPORT.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    log(f"objects={report['objects_created_count']}")
    log("PASS 1 done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
