# -*- coding: utf-8 -*-
"""Author cozy_house_small_A to match mockup prop_house_small.jpg / card Image #1.

Clay-pastel isometric cottage: scalloped roof, warm windows, lilac base,
mailbox, pots, stepping stones, purple smoke. Blender 5.2 → GLB.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Vector

JOB = "COZY_HOUSE_MOCKUP_V1"
MODULE_ID = "cozy_house_small_A"
QUAR = Path(r"E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine") / JOB
GAME_GLB = Path(r"E:\AIdle_openworld\game\assets\p1e_cozy\modules") / f"{MODULE_ID}.glb"
CATALOG = Path(r"E:\AIdle_openworld\game\resources\p1e_cozy\module_catalog.json")
RENDER_DIR = Path(
    r"E:\AIdle_openworld\orchestration\control\visual_reference\mockup_cast_props_001\gen"
)
QUAR.mkdir(parents=True, exist_ok=True)
RENDER_DIR.mkdir(parents=True, exist_ok=True)

# Style lock palette (cozy mockup)
C_WALL = (0.98, 0.93, 0.88, 1.0)  # warm cream stucco
C_WALL_SOFT = (0.96, 0.90, 0.86, 1.0)
C_ROOF_A = (0.98, 0.82, 0.55, 1.0)  # peach-yellow
C_ROOF_B = (0.99, 0.90, 0.62, 1.0)  # light yellow
C_ROOF_C = (0.97, 0.78, 0.58, 1.0)  # peach
C_ROOF_RIDGE = (0.99, 0.94, 0.82, 1.0)
C_DOOR = (0.86, 0.62, 0.42, 1.0)
C_DOOR_FRAME = (0.92, 0.74, 0.55, 1.0)
C_KNOB = (0.98, 0.92, 0.55, 1.0)
C_BASE = (0.78, 0.70, 0.92, 1.0)  # lilac
C_BASE_EDGE = (0.72, 0.64, 0.88, 1.0)
C_EMIT = (1.0, 0.82, 0.45, 1.0)
C_EMIT_CORE = (1.0, 0.92, 0.65, 1.0)
C_GLASS = (0.95, 0.75, 0.35, 0.55)
C_CURTAIN = (0.78, 0.55, 0.82, 1.0)
C_POT = (0.90, 0.62, 0.42, 1.0)
C_LAVENDER = (0.72, 0.55, 0.88, 1.0)
C_LEAF = (0.55, 0.78, 0.55, 1.0)
C_STEM = (0.45, 0.62, 0.40, 1.0)
C_MAIL = (0.68, 0.58, 0.88, 1.0)
C_STONE = (0.93, 0.88, 0.82, 1.0)
C_SMOKE = (0.78, 0.62, 0.92, 0.85)
C_CHIMNEY = (0.97, 0.93, 0.88, 1.0)
C_INTERIOR = (0.45, 0.28, 0.18, 1.0)
C_LAMP = (0.98, 0.88, 0.45, 1.0)


def log(m: str) -> None:
    print(f"[{JOB}] {m}")


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for coll in (
        bpy.data.meshes,
        bpy.data.materials,
        bpy.data.lights,
        bpy.data.cameras,
        bpy.data.images,
    ):
        for b in list(coll):
            coll.remove(b)


def mat(name: str, rgba, rough=0.55, metal=0.0, emit=0.0) -> bpy.types.Material:
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = rough
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metal
        # Blender 4+/5 emission
        for key in ("Emission Color", "Emission"):
            if key in bsdf.inputs and emit > 0:
                if "Color" in key or key == "Emission":
                    try:
                        bsdf.inputs[key].default_value = (
                            rgba[0],
                            rgba[1],
                            rgba[2],
                            1.0,
                        )
                    except Exception:
                        pass
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = emit
        if rgba[3] < 0.99:
            m.blend_method = "BLEND"
            if "Alpha" in bsdf.inputs:
                bsdf.inputs["Alpha"].default_value = rgba[3]
    return m


def link(obj: bpy.types.Object, parent: bpy.types.Object | None = None) -> bpy.types.Object:
    if parent:
        obj.parent = parent
    return obj


def apply_mat(obj: bpy.types.Object, material: bpy.types.Material) -> None:
    if obj.data and hasattr(obj.data, "materials"):
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)


def bevel_obj(obj: bpy.types.Object, width=0.04, segments=3) -> None:
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    try:
        bpy.ops.object.modifier_add(type="BEVEL")
        mod = obj.modifiers[-1]
        mod.width = width
        mod.segments = segments
        mod.limit_method = "ANGLE"
        bpy.ops.object.modifier_apply(modifier=mod.name)
    except Exception as e:
        log(f"bevel skip {obj.name}: {e}")
    obj.select_set(False)


def shade_smooth(obj: bpy.types.Object) -> None:
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.shade_smooth()
        obj.select_set(False)
    except Exception:
        pass


def cube(name, loc, scale, material, parent=None, bevel=0.05, smooth=True):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_mat(obj, material)
    if bevel > 0:
        bevel_obj(obj, width=bevel, segments=4)
    if smooth:
        shade_smooth(obj)
    return link(obj, parent)


def sphere(name, loc, radius, material, parent=None, scale=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=loc, segments=24, ring_count=16)
    obj = bpy.context.active_object
    obj.name = name
    if scale:
        obj.scale = scale
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    apply_mat(obj, material)
    shade_smooth(obj)
    return link(obj, parent)


def cylinder(name, loc, radius, depth, material, parent=None, vertices=24, rot=None):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius, depth=depth, location=loc, vertices=vertices
    )
    obj = bpy.context.active_object
    obj.name = name
    if rot:
        obj.rotation_euler = Euler(rot, "XYZ")
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    apply_mat(obj, material)
    shade_smooth(obj)
    return link(obj, parent)


def empty(name, loc, parent=None):
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.empty_display_size = 0.12
    return link(obj, parent)


def build_house() -> bpy.types.Object:
    mats = {
        "wall": mat("MAT_CozyWall", C_WALL, rough=0.72),
        "wall2": mat("MAT_CozyWallSoft", C_WALL_SOFT, rough=0.75),
        "roof_a": mat("MAT_CozyRoofA", C_ROOF_A, rough=0.48),
        "roof_b": mat("MAT_CozyRoofB", C_ROOF_B, rough=0.48),
        "roof_c": mat("MAT_CozyRoofC", C_ROOF_C, rough=0.50),
        "ridge": mat("MAT_CozyRidge", C_ROOF_RIDGE, rough=0.55),
        "door": mat("MAT_CozyDoor", C_DOOR, rough=0.55),
        "frame": mat("MAT_CozyDoorFrame", C_DOOR_FRAME, rough=0.5),
        "knob": mat("MAT_CozyKnob", C_KNOB, rough=0.25, metal=0.15, emit=0.15),
        "base": mat("MAT_CozyBase", C_BASE, rough=0.65),
        "emit": mat("MAT_CozyLampWarm", C_EMIT, rough=0.35, emit=4.5),
        "emit_core": mat("MAT_CozyEmitCore", C_EMIT_CORE, rough=0.3, emit=6.0),
        "glass": mat("MAT_CozyGlass", C_GLASS, rough=0.2, emit=1.2),
        "curtain": mat("MAT_CozyCurtain", C_CURTAIN, rough=0.7),
        "pot": mat("MAT_CozyPot", C_POT, rough=0.6),
        "lav": mat("MAT_CozyLavender", C_LAVENDER, rough=0.55),
        "leaf": mat("MAT_CozyLeaf", C_LEAF, rough=0.6),
        "stem": mat("MAT_CozyStem", C_STEM, rough=0.65),
        "mail": mat("MAT_CozyMail", C_MAIL, rough=0.45),
        "stone": mat("MAT_CozyStone", C_STONE, rough=0.7),
        "smoke": mat("MAT_CozySmoke", C_SMOKE, rough=1.0, emit=0.05),
        "chimney": mat("MAT_CozyChimney", C_CHIMNEY, rough=0.7),
        "interior": mat("MAT_CozyInterior", C_INTERIOR, rough=0.8),
        "lamp": mat("MAT_CozyTableLamp", C_LAMP, rough=0.4, emit=2.5),
    }

    root = empty(f"MOD_{MODULE_ID}", (0, 0, 0))
    # --- base platform (rounded lilac pad) ---
    base = cube(
        "BasePad",
        (0, 0, 0.06),
        (1.85, 1.55, 0.12),
        mats["base"],
        root,
        bevel=0.12,
    )
    # slightly soft under-lip
    cube("BaseLip", (0, 0, 0.01), (1.92, 1.62, 0.03), mats["base"], root, bevel=0.08)

    # --- main body (soft cream stucco) ---
    body = cube(
        "Body",
        (0, 0, 0.72),
        (1.45, 1.15, 1.15),
        mats["wall"],
        root,
        bevel=0.14,
    )
    # front porch bulge
    cube(
        "FrontBulge",
        (0, 0.52, 0.55),
        (0.95, 0.22, 0.85),
        mats["wall2"],
        root,
        bevel=0.1,
    )

    # --- gable roof mass (under tiles) ---
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 1.48))
    roof_mass = bpy.context.active_object
    roof_mass.name = "RoofMass"
    roof_mass.scale = (1.65, 1.35, 0.55)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    # shape as prism via edit - simple: scale top by collapsing via lattice-ish: use cone-like by two wedges
    apply_mat(roof_mass, mats["ridge"])
    bevel_obj(roof_mass, 0.06, 3)
    shade_smooth(roof_mass)
    link(roof_mass, root)

    # roof gable sides (triangular look via rotated boxes)
    for sign, name in ((-1, "RoofSlopeL"), (1, "RoofSlopeR")):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, sign * 0.15, 1.55))
        sl = bpy.context.active_object
        sl.name = name
        sl.scale = (1.7, 0.95, 0.18)
        sl.rotation_euler = Euler((sign * 0.55, 0, 0), "XYZ")
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        apply_mat(sl, mats["ridge"])
        shade_smooth(sl)
        link(sl, root)

    # --- scalloped roof tiles (mockup signature) ---
    tile_mats = [mats["roof_a"], mats["roof_b"], mats["roof_c"]]
    rows = 5
    cols = 7
    for r in range(rows):
        for c in range(cols):
            # stagger like fish scales
            x = (c - (cols - 1) / 2) * 0.22 + (0.08 if r % 2 else 0.0)
            # map onto roof: y back-to-front, z rises toward ridge
            t = r / max(rows - 1, 1)
            y = 0.55 - t * 1.15
            z = 1.22 + t * 0.55 + abs(y) * 0.08
            # skip extreme corners for soft silhouette
            if abs(x) > 0.78 and r < 1:
                continue
            m = tile_mats[(r + c) % 3]
            # tile = flattened sphere (scale shape)
            tile = sphere(
                f"Tile_{r}_{c}",
                (x, y, z),
                0.12,
                m,
                root,
                scale=(1.15, 0.95, 0.42),
            )
            # slight tilt following slope
            tile.rotation_euler = Euler((-0.35 + t * 0.15, 0.0, 0.0), "XYZ")

    # ridge cap beads
    for i, x in enumerate([-0.55, -0.28, 0.0, 0.28, 0.55]):
        sphere(f"RidgeCap_{i}", (x, -0.05, 1.78), 0.09, mats["ridge"], root, scale=(1.1, 1.0, 0.7))

    # eaves / overhang lip
    cube("EaveFront", (0, 0.62, 1.28), (1.7, 0.12, 0.08), mats["ridge"], root, bevel=0.04)
    cube("EaveBack", (0, -0.62, 1.28), (1.7, 0.12, 0.08), mats["ridge"], root, bevel=0.04)

    # --- chimney ---
    cube("Chimney", (0.42, -0.22, 1.95), (0.22, 0.22, 0.42), mats["chimney"], root, bevel=0.04)
    cube("ChimneyTop", (0.42, -0.22, 2.18), (0.26, 0.26, 0.08), mats["chimney"], root, bevel=0.03)
    # purple smoke blobs (pixel-soft cubes + spheres)
    smoke_pts = [
        (0.42, -0.22, 2.35, 0.08),
        (0.50, -0.18, 2.50, 0.11),
        (0.58, -0.12, 2.62, 0.09),
        (0.68, -0.05, 2.72, 0.07),
        (0.78, 0.02, 2.80, 0.05),
        (0.55, -0.08, 2.55, 0.06),
    ]
    for i, (sx, sy, sz, sr) in enumerate(smoke_pts):
        if i % 2 == 0:
            sphere(f"Smoke_{i}", (sx, sy, sz), sr, mats["smoke"], root)
        else:
            cube(f"SmokeC_{i}", (sx, sy, sz), (sr * 1.6, sr * 1.6, sr * 1.6), mats["smoke"], root, bevel=0.02)

    # --- door (arched look: door plate + arch top) ---
    door = cube("Door", (0.0, 0.68, 0.55), (0.38, 0.06, 0.72), mats["door"], root, bevel=0.05)
    cube("DoorFrame", (0.0, 0.66, 0.58), (0.46, 0.04, 0.82), mats["frame"], root, bevel=0.04)
    # arch top
    cylinder("DoorArch", (0.0, 0.68, 0.95), 0.22, 0.07, mats["frame"], root, rot=(math.pi / 2, 0, 0))
    # knob
    sphere("DoorKnob", (0.14, 0.74, 0.52), 0.045, mats["knob"], root)
    # door steps
    cube("Step1", (0.0, 0.78, 0.14), (0.42, 0.18, 0.08), mats["frame"], root, bevel=0.03)
    cube("Step2", (0.0, 0.88, 0.08), (0.36, 0.14, 0.06), mats["frame"], root, bevel=0.03)

    # --- small front arched windows with warm glow ---
    for name, x, z in (("WinFL", -0.42, 0.72), ("WinFR", 0.42, 0.48), ("WinFU", -0.35, 1.05)):
        # frame ring
        cylinder(f"{name}_frame", (x, 0.70, z), 0.11, 0.05, mats["frame"], root, rot=(math.pi / 2, 0, 0))
        sphere(f"{name}_glow", (x, 0.72, z), 0.09, mats["emit"], root)

    # upper gable circular window
    cylinder("WinGable_frame", (0.0, 0.55, 1.35), 0.12, 0.05, mats["frame"], root, rot=(math.pi / 2, 0, 0))
    sphere("WinGable_glow", (0.0, 0.57, 1.35), 0.10, mats["emit_core"], root)

    # --- large side window (mockup right face) with interior scene ---
    # opening on +X face
    cube("SideWinFrame", (0.74, 0.05, 0.78), (0.08, 0.55, 0.48), mats["frame"], root, bevel=0.03)
    # warm glass plane
    cube("SideWinGlass", (0.76, 0.05, 0.78), (0.03, 0.48, 0.40), mats["emit"], root, bevel=0.01)
    # interior box darker
    cube("SideInterior", (0.55, 0.05, 0.78), (0.25, 0.45, 0.38), mats["interior"], root, bevel=0.02)
    # curtains (left/right)
    cube("CurtainL", (0.68, -0.18, 0.82), (0.04, 0.08, 0.36), mats["curtain"], root, bevel=0.02)
    cube("CurtainR", (0.68, 0.28, 0.82), (0.04, 0.08, 0.36), mats["curtain"], root, bevel=0.02)
    # curtain dots
    for i, dy in enumerate([-0.18, -0.18, 0.28, 0.28]):
        sphere(f"CurtainDot_{i}", (0.71, dy, 0.70 + (i % 2) * 0.18), 0.02, mats["lav"], root)
    # lamp + plant inside
    cylinder("TableLampBody", (0.58, 0.12, 0.62), 0.04, 0.12, mats["pot"], root)
    sphere("TableLampShade", (0.58, 0.12, 0.72), 0.07, mats["lamp"], root, scale=(1.0, 1.0, 0.7))
    sphere("TableLampGlow", (0.58, 0.12, 0.72), 0.05, mats["emit_core"], root)
    cylinder("WinPlantPot", (0.58, -0.08, 0.58), 0.04, 0.06, mats["pot"], root)
    sphere("WinPlant", (0.58, -0.08, 0.66), 0.05, mats["leaf"], root)

    # --- mailbox purple ---
    cube("MailboxBody", (0.28, 0.82, 0.32), (0.14, 0.10, 0.12), mats["mail"], root, bevel=0.03)
    cube("MailboxFlag", (0.36, 0.82, 0.36), (0.04, 0.02, 0.08), mats["lav"], root, bevel=0.01)
    cylinder("MailboxPost", (0.28, 0.82, 0.18), 0.025, 0.2, mats["mail"], root)

    # --- plant pots ---
    # large lavender left
    cylinder("PotL", (-0.72, 0.72, 0.18), 0.10, 0.14, mats["pot"], root)
    for i, ang in enumerate([0, 1.2, 2.4, 3.5, 4.8]):
        sx = -0.72 + 0.04 * math.cos(ang)
        sy = 0.72 + 0.04 * math.sin(ang)
        cylinder(f"LavStem_{i}", (sx, sy, 0.32), 0.012, 0.22, mats["stem"], root)
        sphere(f"LavBloom_{i}", (sx, sy, 0.46), 0.045, mats["lav"], root, scale=(0.7, 0.7, 1.3))
    # small pots right of door
    for i, (px, py) in enumerate([(0.48, 0.78), (0.62, 0.72)]):
        cylinder(f"PotS_{i}", (px, py, 0.14), 0.06, 0.10, mats["pot"], root)
        sphere(f"PlantS_{i}", (px, py, 0.24), 0.06, mats["leaf"] if i == 0 else mats["lav"], root)

    # --- stepping stones ---
    for i, (px, py, s) in enumerate([(-0.15, 1.15, 0.14), (0.05, 1.32, 0.12), (-0.05, 1.48, 0.11)]):
        sphere(f"Stone_{i}", (px, py, 0.04), s, mats["stone"], root, scale=(1.3, 1.0, 0.25))

    # sockets (keep catalog compatibility)
    empty(f"MOD_{MODULE_ID}_SOCKET_DOOR_FRONT", (0.0, 0.95, 0.2), root)
    empty(f"MOD_{MODULE_ID}_SOCKET_PATH_FRONT", (0.0, 1.35, 0.0), root)
    empty(f"MOD_{MODULE_ID}_SOCKET_PROP_LEFT", (-0.9, 0.5, 0.1), root)

    return root


def export_glb(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # select hierarchy
    bpy.ops.object.select_all(action="DESELECT")
    root = bpy.data.objects.get(f"MOD_{MODULE_ID}")
    if root is None:
        raise RuntimeError("root missing")
    # select all mesh children
    for obj in bpy.data.objects:
        if obj.type in {"MESH", "EMPTY"}:
            obj.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_extras=False,
        export_cameras=False,
        export_lights=False,
    )
    log(f"exported {path} bytes={path.stat().st_size}")


def setup_render_camera() -> None:
    # isometric-ish matching mockup card angle
    bpy.ops.object.camera_add(location=(3.6, 3.8, 2.8))
    cam = bpy.context.active_object
    cam.name = "PreviewCam"
    cam.rotation_euler = Euler((math.radians(58), 0, math.radians(48)), "XYZ")
    cam.data.lens = 50
    bpy.context.scene.camera = cam
    # lights
    bpy.ops.object.light_add(type="AREA", location=(2.5, 1.5, 4.0))
    key = bpy.context.active_object
    key.data.energy = 80
    key.data.size = 3.0
    bpy.ops.object.light_add(type="AREA", location=(-2.0, -1.0, 2.5))
    fill = bpy.context.active_object
    fill.data.energy = 25
    fill.data.size = 2.5
    # soft purple rim
    bpy.ops.object.light_add(type="AREA", location=(0.5, -2.5, 2.0))
    rim = bpy.context.active_object
    rim.data.energy = 15
    rim.data.size = 2.0
    rim.data.color = (0.85, 0.75, 1.0)
    # world
    world = bpy.data.worlds.new("CozyWorld")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.93, 0.88, 0.95, 1.0)
        bg.inputs[1].default_value = 0.8


def render_preview(path: Path) -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in dir(bpy.types) else "BLENDER_EEVEE"
    # try eevee next then eevee
    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"):
        try:
            scene.render.engine = eng
            break
        except Exception:
            continue
    scene.render.resolution_x = 768
    scene.render.resolution_y = 768
    scene.render.filepath = str(path)
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    bpy.ops.render.render(write_still=True)
    log(f"render {path}")


def update_catalog(glb: Path) -> None:
    if not CATALOG.exists():
        log("catalog missing — skip")
        return
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    digest = sha256(glb)
    size = glb.stat().st_size
    for m in data.get("modules", []):
        if m.get("module_id") == MODULE_ID:
            m["glb_sha256"] = digest
            m["bytes"] = size
            m["source"] = JOB
            m["visual"] = "mockup_match_v1"
            break
    data["house_mockup_revision"] = JOB
    CATALOG.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log(f"catalog updated sha={digest[:12]}… bytes={size}")


def main() -> int:
    log("start Blender author")
    clear_scene()
    build_house()
    quar_glb = QUAR / f"{MODULE_ID}.glb"
    export_glb(quar_glb)
    # promote to game path (exact leased module)
    GAME_GLB.parent.mkdir(parents=True, exist_ok=True)
    GAME_GLB.write_bytes(quar_glb.read_bytes())
    log(f"promoted → {GAME_GLB}")
    update_catalog(GAME_GLB)
    # preview render for visual QA loop
    setup_render_camera()
    preview = RENDER_DIR / f"{MODULE_ID}_blender_preview_v1.png"
    try:
        render_preview(preview)
    except Exception as e:
        log(f"render failed (non-fatal): {e}")
    meta = {
        "job": JOB,
        "module_id": MODULE_ID,
        "glb": str(GAME_GLB),
        "sha256": sha256(GAME_GLB),
        "bytes": GAME_GLB.stat().st_size,
        "preview": str(preview) if preview.exists() else None,
        "accepted": False,
    }
    (QUAR / "result.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    log("DONE " + json.dumps(meta))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        log(f"FATAL {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
