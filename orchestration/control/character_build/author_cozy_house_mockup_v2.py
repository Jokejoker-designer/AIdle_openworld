# -*- coding: utf-8 -*-
"""cozy_house_small_A mockup-match v2 — cleaner clay cottage + reliable Cycles preview."""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Matrix, Vector

JOB = "COZY_HOUSE_MOCKUP_V2"
MODULE_ID = "cozy_house_small_A"
QUAR = Path(r"E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine") / JOB
GAME_GLB = Path(r"E:\AIdle_openworld\game\assets\p1e_cozy\modules") / f"{MODULE_ID}.glb"
CATALOG = Path(r"E:\AIdle_openworld\game\resources\p1e_cozy\module_catalog.json")
RENDER_DIR = Path(
    r"E:\AIdle_openworld\orchestration\control\visual_reference\mockup_cast_props_001\gen"
)
QUAR.mkdir(parents=True, exist_ok=True)
RENDER_DIR.mkdir(parents=True, exist_ok=True)

# Mockup palette
P = {
    "wall": (0.99, 0.94, 0.89, 1),
    "roof1": (0.99, 0.84, 0.52, 1),
    "roof2": (1.0, 0.92, 0.58, 1),
    "roof3": (0.98, 0.78, 0.55, 1),
    "ridge": (0.99, 0.95, 0.86, 1),
    "door": (0.88, 0.64, 0.44, 1),
    "frame": (0.93, 0.76, 0.58, 1),
    "knob": (1.0, 0.93, 0.55, 1),
    "base": (0.80, 0.72, 0.93, 1),
    "emit": (1.0, 0.80, 0.40, 1),
    "emit2": (1.0, 0.92, 0.62, 1),
    "curtain": (0.80, 0.55, 0.85, 1),
    "pot": (0.90, 0.62, 0.42, 1),
    "lav": (0.75, 0.55, 0.90, 1),
    "leaf": (0.55, 0.78, 0.52, 1),
    "stem": (0.42, 0.58, 0.38, 1),
    "mail": (0.70, 0.58, 0.90, 1),
    "stone": (0.94, 0.90, 0.85, 1),
    "smoke": (0.82, 0.65, 0.95, 1),
    "chimney": (0.98, 0.94, 0.90, 1),
    "dark": (0.42, 0.26, 0.16, 1),
}


def log(m):
    print(f"[{JOB}] {m}")


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def mat(name, rgba, rough=0.55, emit=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if not bsdf:
        return m
    bsdf.inputs["Base Color"].default_value = rgba
    if "Roughness" in bsdf.inputs:
        bsdf.inputs["Roughness"].default_value = rough
    if emit > 0:
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (rgba[0], rgba[1], rgba[2], 1)
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = emit
    return m


def finish(obj, material, bevel_w=0.0):
    if material and obj.data:
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    if bevel_w > 0:
        try:
            bpy.ops.object.modifier_add(type="BEVEL")
            mod = obj.modifiers[-1]
            mod.width = bevel_w
            mod.segments = 4
            mod.limit_method = "ANGLE"
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except Exception:
            pass
    try:
        bpy.ops.object.shade_smooth()
    except Exception:
        pass
    obj.select_set(False)
    return obj


def add_cube(name, loc, scale, material, bevel=0.05):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, material, bevel)


def add_sphere(name, loc, r, material, scale=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=20, ring_count=12)
    o = bpy.context.active_object
    o.name = name
    if scale:
        o.scale = scale
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, material, 0.0)


def add_cyl(name, loc, r, depth, material, rot=None, verts=20):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, vertices=verts)
    o = bpy.context.active_object
    o.name = name
    if rot:
        o.rotation_euler = Euler(rot, "XYZ")
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    return finish(o, material, 0.0)


def add_empty(name, loc):
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=loc)
    o = bpy.context.active_object
    o.name = name
    o.empty_display_size = 0.1
    return o


def parent_all_to(root):
    for o in list(bpy.data.objects):
        if o != root and o.parent is None and o.type in {"MESH", "EMPTY"}:
            # keep world transform
            mw = o.matrix_world.copy()
            o.parent = root
            o.matrix_world = mw


def build():
    M = {k: mat(f"MAT_{k}", v, rough=0.55 if k != "emit" else 0.35,
                emit=(5.0 if k == "emit" else 7.0 if k == "emit2" else 0.08 if k == "smoke" else 0.0))
         for k, v in P.items()}
    # retune a few
    M["wall"] = mat("MAT_wall", P["wall"], 0.72)
    M["base"] = mat("MAT_base", P["base"], 0.65)
    M["door"] = mat("MAT_door", P["door"], 0.5)
    M["emit"] = mat("MAT_emit", P["emit"], 0.3, emit=6.0)
    M["emit2"] = mat("MAT_emit2", P["emit2"], 0.25, emit=8.0)
    M["smoke"] = mat("MAT_smoke", P["smoke"], 1.0, emit=0.15)
    M["knob"] = mat("MAT_knob", P["knob"], 0.2, emit=0.4)

    root = add_empty(f"MOD_{MODULE_ID}", (0, 0, 0))

    # Lilac rounded base (mockup pad)
    add_cube("Base", (0, 0, 0.07), (1.9, 1.7, 0.14), M["base"], bevel=0.14)
    add_cube("BaseSoft", (0, 0.05, 0.02), (1.95, 1.78, 0.04), M["base"], bevel=0.1)

    # Main soft body — slightly wider front face toward +Y
    add_cube("Body", (0, 0, 0.70), (1.35, 1.20, 1.20), M["wall"], bevel=0.16)
    # rounded roof eaves mass under tiles
    add_cube("Attic", (0, 0, 1.35), (1.40, 1.22, 0.35), M["wall"], bevel=0.12)

    # Proper gable roof core (two slopes via rotated slabs)
    for sign, nm in ((1, "SlopeF"), (-1, "SlopeB")):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, sign * 0.28, 1.58))
        o = bpy.context.active_object
        o.name = nm
        o.scale = (1.55, 0.95, 0.12)
        o.rotation_euler = Euler((sign * math.radians(32), 0, 0), "XYZ")
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        finish(o, M["ridge"], 0.04)

    # Scalloped tiles — cover front slope (+Y down) and back
    roof_mats = [M["roof1"], M["roof2"], M["roof3"]]
    # front slope tiles
    for r in range(6):
        cols = 8 if r < 5 else 6
        for c in range(cols):
            u = (c - (cols - 1) / 2) * 0.18
            v = 0.55 - r * 0.16  # y
            # height follows slope: higher toward ridge (y~0)
            z = 1.30 + (0.55 - abs(v)) * 0.85 + r * 0.02
            # place on front half primarily for mockup read
            y = v
            m = roof_mats[(r + c) % 3]
            t = add_sphere(f"T_f{r}_{c}", (u, y, z), 0.105, m, scale=(1.25, 1.05, 0.38))
            t.rotation_euler = Euler((math.radians(-28 + r * 2), 0, 0), "XYZ")
    # back slope fewer tiles
    for r in range(4):
        for c in range(6):
            u = (c - 2.5) * 0.20
            y = -0.25 - r * 0.14
            z = 1.35 + (0.5 - abs(y) * 0.3) * 0.7
            m = roof_mats[(r + c + 1) % 3]
            t = add_sphere(f"T_b{r}_{c}", (u, y, z), 0.10, m, scale=(1.2, 1.0, 0.36))
            t.rotation_euler = Euler((math.radians(28), 0, 0), "XYZ")

    # ridge beads
    for i, x in enumerate([-0.5, -0.25, 0, 0.25, 0.5]):
        add_sphere(f"Ridge{i}", (x, 0.02, 1.82), 0.08, M["ridge"], scale=(1.2, 1.0, 0.65))

    # Chimney (right-back of roof, mockup)
    add_cube("Chimney", (0.38, -0.18, 1.95), (0.22, 0.22, 0.45), M["chimney"], bevel=0.04)
    add_cube("ChimneyCap", (0.38, -0.18, 2.20), (0.28, 0.28, 0.08), M["chimney"], bevel=0.03)
    for i, (dx, dy, dz, s) in enumerate([
        (0.0, 0.0, 0.18, 0.09),
        (0.08, 0.05, 0.32, 0.12),
        (0.16, 0.10, 0.45, 0.10),
        (0.26, 0.16, 0.55, 0.08),
        (0.36, 0.22, 0.62, 0.06),
        (0.12, 0.08, 0.38, 0.07),
    ]):
        add_sphere(f"Smoke{i}", (0.38 + dx, -0.18 + dy, 2.25 + dz), s, M["smoke"])

    # Door center-front
    add_cube("DoorFrame", (0, 0.62, 0.55), (0.48, 0.06, 0.88), M["frame"], bevel=0.05)
    add_cube("Door", (0, 0.66, 0.52), (0.38, 0.05, 0.72), M["door"], bevel=0.05)
    add_cyl("DoorArch", (0, 0.66, 0.95), 0.22, 0.06, M["frame"], rot=(math.pi / 2, 0, 0))
    add_sphere("Knob", (0.13, 0.72, 0.50), 0.045, M["knob"])
    add_cube("StepA", (0, 0.78, 0.12), (0.42, 0.20, 0.08), M["frame"], bevel=0.03)
    add_cube("StepB", (0, 0.90, 0.06), (0.34, 0.14, 0.05), M["frame"], bevel=0.025)

    # Small glowing windows front
    for nm, x, z, r in [
        ("W1", -0.40, 0.72, 0.10),
        ("W2", 0.40, 0.48, 0.09),
        ("W3", -0.32, 1.05, 0.10),
        ("W4", 0.0, 1.32, 0.11),  # gable
    ]:
        add_cyl(f"{nm}_fr", (x, 0.64, z), r + 0.02, 0.05, M["frame"], rot=(math.pi / 2, 0, 0))
        add_sphere(f"{nm}_gl", (x, 0.68, z), r, M["emit"] if nm != "W4" else M["emit2"])

    # Large side window (+X) with cozy interior
    add_cube("SideFrame", (0.70, 0.02, 0.78), (0.08, 0.58, 0.50), M["frame"], bevel=0.03)
    add_cube("SideGlow", (0.74, 0.02, 0.78), (0.04, 0.50, 0.42), M["emit"], bevel=0.01)
    add_cube("SideRoom", (0.52, 0.02, 0.78), (0.28, 0.48, 0.40), M["dark"], bevel=0.02)
    add_cube("CurtL", (0.68, -0.20, 0.82), (0.04, 0.08, 0.38), M["curtain"], bevel=0.02)
    add_cube("CurtR", (0.68, 0.24, 0.82), (0.04, 0.08, 0.38), M["curtain"], bevel=0.02)
    for i, (y, z) in enumerate([(-0.20, 0.70), (-0.20, 0.90), (0.24, 0.70), (0.24, 0.90)]):
        add_sphere(f"Dot{i}", (0.71, y, z), 0.022, M["lav"])
    add_cyl("LampStem", (0.55, 0.12, 0.60), 0.035, 0.10, M["pot"])
    add_sphere("LampShade", (0.55, 0.12, 0.70), 0.07, M["emit2"], scale=(1, 1, 0.75))
    add_cyl("InPot", (0.55, -0.10, 0.58), 0.04, 0.06, M["pot"])
    add_sphere("InPlant", (0.55, -0.10, 0.66), 0.05, M["leaf"])

    # Mailbox
    add_cyl("MailPost", (0.32, 0.78, 0.18), 0.025, 0.22, M["mail"])
    add_cube("MailBox", (0.32, 0.78, 0.32), (0.16, 0.12, 0.12), M["mail"], bevel=0.03)
    add_cube("MailFlag", (0.40, 0.78, 0.36), (0.04, 0.02, 0.08), M["lav"], bevel=0.01)

    # Pots
    add_cyl("PotBig", (-0.70, 0.70, 0.18), 0.11, 0.16, M["pot"])
    for i, a in enumerate([0, 1.25, 2.5, 3.8, 5.0]):
        x = -0.70 + 0.045 * math.cos(a)
        y = 0.70 + 0.045 * math.sin(a)
        add_cyl(f"Stem{i}", (x, y, 0.34), 0.012, 0.24, M["stem"])
        add_sphere(f"Bloom{i}", (x, y, 0.50), 0.05, M["lav"], scale=(0.7, 0.7, 1.35))
    add_cyl("PotS1", (0.50, 0.78, 0.14), 0.055, 0.10, M["pot"])
    add_sphere("PlS1", (0.50, 0.78, 0.24), 0.06, M["leaf"])
    add_cyl("PotS2", (0.64, 0.70, 0.13), 0.05, 0.09, M["pot"])
    add_sphere("PlS2", (0.64, 0.70, 0.22), 0.05, M["lav"])

    # Stepping stones
    for i, (x, y, s) in enumerate([(-0.12, 1.12, 0.13), (0.08, 1.30, 0.11), (-0.02, 1.48, 0.10)]):
        add_sphere(f"Stone{i}", (x, y, 0.035), s, M["stone"], scale=(1.35, 1.05, 0.22))

    # sockets
    add_empty(f"MOD_{MODULE_ID}_SOCKET_DOOR_FRONT", (0, 0.95, 0.15))
    add_empty(f"MOD_{MODULE_ID}_SOCKET_PATH_FRONT", (0, 1.4, 0))
    add_empty(f"MOD_{MODULE_ID}_SOCKET_PROP_LEFT", (-0.95, 0.5, 0.1))

    parent_all_to(root)
    return root


def export_glb(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=False,
        export_apply=True,
        export_cameras=False,
        export_lights=False,
    )
    log(f"export {path} size={path.stat().st_size}")


def render_preview(path: Path):
    # World soft lilac
    world = bpy.data.worlds.new("W")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.94, 0.90, 0.96, 1)
    bg.inputs[1].default_value = 1.0

    # Camera — mockup isometric-ish (front-right elevated)
    bpy.ops.object.camera_add(location=(2.8, 3.2, 2.4))
    cam = bpy.context.active_object
    cam.name = "Cam"
    # aim at house center ~ (0,0.2,0.9)
    direction = Vector((0, 0.15, 0.85)) - Vector(cam.location)
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 55
    cam.data.clip_start = 0.05
    cam.data.clip_end = 100
    bpy.context.scene.camera = cam

    # Lights
    bpy.ops.object.light_add(type="SUN", location=(3, 2, 6))
    sun = bpy.context.active_object
    sun.data.energy = 2.5
    sun.rotation_euler = Euler((math.radians(45), math.radians(15), math.radians(30)), "XYZ")
    bpy.ops.object.light_add(type="AREA", location=(-2, 2, 3))
    fill = bpy.context.active_object
    fill.data.energy = 40
    fill.data.size = 4
    fill.data.color = (1, 0.95, 0.9)
    bpy.ops.object.light_add(type="AREA", location=(1, -2, 2))
    rim = bpy.context.active_object
    rim.data.energy = 20
    rim.data.size = 3
    rim.data.color = (0.85, 0.75, 1.0)

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 900
    scene.render.resolution_y = 900
    scene.render.filepath = str(path)
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    bpy.ops.render.render(write_still=True)
    log(f"render ok {path} exists={path.exists()}")


def update_catalog(glb: Path):
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    d = sha(glb)
    n = glb.stat().st_size
    for m in data.get("modules", []):
        if m.get("module_id") == MODULE_ID:
            m["glb_sha256"] = d
            m["bytes"] = n
            m["source"] = JOB
            m["visual"] = "mockup_match_v2"
            break
    data["house_mockup_revision"] = JOB
    CATALOG.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log(f"catalog sha={d[:16]}… bytes={n}")


def main():
    log("start")
    clear()
    build()
    # bounds sanity
    mins = Vector((1e9, 1e9, 1e9))
    maxs = Vector((-1e9, -1e9, -1e9))
    for o in bpy.data.objects:
        if o.type != "MESH":
            continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            mins = Vector((min(mins.x, w.x), min(mins.y, w.y), min(mins.z, w.z)))
            maxs = Vector((max(maxs.x, w.x), max(maxs.y, w.y), max(maxs.z, w.z)))
    log(f"bounds min={tuple(mins)} max={tuple(maxs)}")
    quar = QUAR / f"{MODULE_ID}.glb"
    export_glb(quar)
    GAME_GLB.write_bytes(quar.read_bytes())
    log(f"promoted {GAME_GLB}")
    update_catalog(GAME_GLB)
    preview = RENDER_DIR / f"{MODULE_ID}_blender_preview_v2.png"
    try:
        render_preview(preview)
    except Exception as e:
        log(f"render fail: {e}")
        import traceback
        traceback.print_exc()
    meta = {
        "job": JOB,
        "module_id": MODULE_ID,
        "glb": str(GAME_GLB),
        "sha256": sha(GAME_GLB),
        "bytes": GAME_GLB.stat().st_size,
        "preview": str(preview) if preview.exists() else None,
        "accepted": False,
    }
    (QUAR / "result.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    log("DONE " + json.dumps(meta))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        log(f"FATAL {e}")
        import traceback
        traceback.print_exc()
        raise SystemExit(1)
