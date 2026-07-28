# -*- coding: utf-8 -*-
"""cozy_house_small_A mockup-match v3 — saturated clay colors + dense scallop roof.

Target: prop_house_small.jpg card — peach/yellow fish-scale roof, cream body,
warm windows, lilac pad, mailbox, pots, purple smoke.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Vector

JOB = "COZY_HOUSE_MOCKUP_V3"
MODULE_ID = "cozy_house_small_A"
QUAR = Path(r"E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine") / JOB
GAME_GLB = Path(r"E:\AIdle_openworld\game\assets\p1e_cozy\modules") / f"{MODULE_ID}.glb"
CATALOG = Path(r"E:\AIdle_openworld\game\resources\p1e_cozy\module_catalog.json")
RENDER_DIR = Path(
    r"E:\AIdle_openworld\orchestration\control\visual_reference\mockup_cast_props_001\gen"
)
QUAR.mkdir(parents=True, exist_ok=True)
RENDER_DIR.mkdir(parents=True, exist_ok=True)

# Strong clay palette (sRGB 0-1) matching mockup
COL = {
    "wall": (0.99, 0.93, 0.86),
    "roof_peach": (0.98, 0.72, 0.42),
    "roof_yellow": (0.99, 0.86, 0.40),
    "roof_cream": (0.99, 0.90, 0.70),
    "ridge": (0.99, 0.94, 0.82),
    "door": (0.82, 0.52, 0.32),
    "frame": (0.90, 0.68, 0.48),
    "knob": (1.0, 0.90, 0.45),
    "base": (0.72, 0.62, 0.90),
    "emit": (1.0, 0.75, 0.28),
    "emit_soft": (1.0, 0.88, 0.55),
    "curtain": (0.78, 0.48, 0.85),
    "pot": (0.88, 0.55, 0.35),
    "lav": (0.72, 0.48, 0.90),
    "leaf": (0.48, 0.78, 0.48),
    "stem": (0.38, 0.55, 0.32),
    "mail": (0.62, 0.50, 0.88),
    "stone": (0.93, 0.88, 0.80),
    "smoke": (0.78, 0.55, 0.92),
    "chimney": (0.97, 0.92, 0.86),
    "dark": (0.35, 0.20, 0.12),
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


def make_mat(name: str, rgb, rough=0.55, emit=0.0) -> bpy.types.Material:
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    # Viewport solid color (Workbench)
    m.diffuse_color = (rgb[0], rgb[1], rgb[2], 1.0)
    nt = m.node_tree
    bsdf = None
    for n in nt.nodes:
        if n.type == "BSDF_PRINCIPLED":
            bsdf = n
            break
    if bsdf is None:
        bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
        out = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None)
        if out:
            nt.links.new(bsdf.outputs[0], out.inputs[0])
    # Color
    if "Base Color" in bsdf.inputs:
        bsdf.inputs["Base Color"].default_value = (rgb[0], rgb[1], rgb[2], 1.0)
    if "Roughness" in bsdf.inputs:
        bsdf.inputs["Roughness"].default_value = rough
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = 0.0
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.15
    if emit > 0:
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (rgb[0], rgb[1], rgb[2], 1.0)
        elif "Emission" in bsdf.inputs:
            try:
                bsdf.inputs["Emission"].default_value = (rgb[0], rgb[1], rgb[2], 1.0)
            except Exception:
                pass
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = emit
    return m


def assign(obj, mat):
    if obj.data is None:
        return
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def bevel_smooth(obj, w=0.05):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    if w > 0:
        try:
            bpy.ops.object.modifier_add(type="BEVEL")
            mod = obj.modifiers[-1]
            mod.width = w
            mod.segments = 3
            mod.limit_method = "ANGLE"
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except Exception:
            pass
    try:
        bpy.ops.object.shade_smooth()
    except Exception:
        pass
    obj.select_set(False)


def cube(name, loc, scale, mat, bevel=0.05):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = Vector(scale)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(o, mat)
    bevel_smooth(o, bevel)
    return o


def sphere(name, loc, r, mat, sx=1.0, sy=1.0, sz=1.0):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=18, ring_count=12)
    o = bpy.context.active_object
    o.name = name
    o.scale = Vector((sx, sy, sz))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign(o, mat)
    bevel_smooth(o, 0.0)
    return o


def cyl(name, loc, r, depth, mat, rot=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, vertices=18)
    o = bpy.context.active_object
    o.name = name
    if rot:
        o.rotation_euler = Euler(rot, "XYZ")
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    assign(o, mat)
    bevel_smooth(o, 0.0)
    return o


def empty(name, loc):
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=loc)
    o = bpy.context.active_object
    o.name = name
    o.empty_display_size = 0.08
    return o


def build():
    M = {k: make_mat(f"M_{k}", v) for k, v in COL.items()}
    M["emit"] = make_mat("M_emit", COL["emit"], rough=0.35, emit=5.5)
    M["emit_soft"] = make_mat("M_emit_soft", COL["emit_soft"], rough=0.3, emit=4.0)
    M["smoke"] = make_mat("M_smoke", COL["smoke"], rough=1.0, emit=0.2)
    M["knob"] = make_mat("M_knob", COL["knob"], rough=0.25, emit=0.5)
    M["roof_peach"] = make_mat("M_roof_peach", COL["roof_peach"], rough=0.45)
    M["roof_yellow"] = make_mat("M_roof_yellow", COL["roof_yellow"], rough=0.45)
    M["roof_cream"] = make_mat("M_roof_cream", COL["roof_cream"], rough=0.48)

    root = empty(f"MOD_{MODULE_ID}", (0, 0, 0))
    meshes = []

    def keep(o):
        meshes.append(o)
        return o

    # Base pad
    keep(cube("Base", (0, 0.05, 0.06), (1.95, 1.75, 0.12), M["base"], 0.14))
    keep(cube("BaseEdge", (0, 0.05, 0.01), (2.0, 1.8, 0.03), M["base"], 0.08))

    # Body
    keep(cube("Body", (0, 0.0, 0.68), (1.30, 1.15, 1.15), M["wall"], 0.15))
    keep(cube("FrontFace", (0, 0.48, 0.55), (0.95, 0.18, 0.85), M["wall"], 0.10))

    # Gable roof mass (cream under-tiles)
    # Front slope slab
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.28, 1.52))
    fr = bpy.context.active_object
    fr.name = "RoofFrontSlab"
    fr.scale = (1.55, 0.95, 0.10)
    fr.rotation_euler = Euler((math.radians(34), 0, 0), "XYZ")
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    assign(fr, M["ridge"])
    bevel_smooth(fr, 0.03)
    keep(fr)
    # Back slope
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.28, 1.52))
    bk = bpy.context.active_object
    bk.name = "RoofBackSlab"
    bk.scale = (1.55, 0.95, 0.10)
    bk.rotation_euler = Euler((math.radians(-34), 0, 0), "XYZ")
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    assign(bk, M["ridge"])
    bevel_smooth(bk, 0.03)
    keep(bk)

    # Dense fish-scale tiles on front slope (mockup read)
    roof_ms = [M["roof_peach"], M["roof_yellow"], M["roof_cream"]]
    for row in range(7):
        n_col = 9 if row < 6 else 7
        for col in range(n_col):
            # parametric on front slope plane
            # slope: y from 0.65 (eave) to 0.0 (ridge), z from 1.22 to 1.85
            t = row / 6.0
            y = 0.62 - t * 0.68
            z = 1.22 + t * 0.68
            x = (col - (n_col - 1) / 2.0) * 0.175
            if row % 2:
                x += 0.08
            if abs(x) > 0.78 and row == 0:
                continue
            m = roof_ms[(row + col) % 3]
            t_obj = sphere(f"TileF{row}_{col}", (x, y, z), 0.11, m, sx=1.35, sy=1.1, sz=0.36)
            t_obj.rotation_euler = Euler((math.radians(-34), 0, 0), "XYZ")
            keep(t_obj)

    # Back tiles (sparser but colored)
    for row in range(5):
        for col in range(7):
            t = row / 4.0
            y = -0.15 - t * 0.50
            z = 1.30 + t * 0.55
            x = (col - 3) * 0.20
            if row % 2:
                x += 0.08
            m = roof_ms[(row + col + 1) % 3]
            t_obj = sphere(f"TileB{row}_{col}", (x, y, z), 0.10, m, sx=1.25, sy=1.0, sz=0.34)
            t_obj.rotation_euler = Euler((math.radians(34), 0, 0), "XYZ")
            keep(t_obj)

    # Ridge line
    for i, x in enumerate([-0.55, -0.28, 0.0, 0.28, 0.55]):
        keep(sphere(f"Ridge{i}", (x, 0.0, 1.88), 0.085, M["ridge"], sx=1.15, sy=1.0, sz=0.7))

    # Eaves
    keep(cube("EaveF", (0, 0.68, 1.22), (1.65, 0.12, 0.07), M["ridge"], 0.03))
    keep(cube("EaveB", (0, -0.68, 1.22), (1.65, 0.12, 0.07), M["ridge"], 0.03))

    # Chimney + smoke
    keep(cube("Chimney", (0.40, -0.15, 1.98), (0.22, 0.22, 0.48), M["chimney"], 0.04))
    keep(cube("ChimTop", (0.40, -0.15, 2.24), (0.28, 0.28, 0.08), M["chimney"], 0.03))
    for i, (dx, dy, dz, s) in enumerate([
        (0.02, 0.0, 0.15, 0.09),
        (0.10, 0.06, 0.30, 0.12),
        (0.18, 0.12, 0.42, 0.10),
        (0.28, 0.18, 0.52, 0.08),
        (0.38, 0.24, 0.60, 0.06),
        (0.12, 0.08, 0.35, 0.07),
        (0.22, 0.14, 0.48, 0.05),
    ]):
        keep(sphere(f"Smoke{i}", (0.40 + dx, -0.15 + dy, 2.30 + dz), s, M["smoke"]))

    # Door
    keep(cube("DoorFrame", (0, 0.60, 0.52), (0.50, 0.07, 0.90), M["frame"], 0.05))
    keep(cube("Door", (0, 0.64, 0.50), (0.38, 0.05, 0.72), M["door"], 0.05))
    keep(cyl("DoorArch", (0, 0.64, 0.95), 0.23, 0.06, M["frame"], rot=(math.pi / 2, 0, 0)))
    keep(sphere("Knob", (0.13, 0.70, 0.48), 0.045, M["knob"]))
    keep(cube("Step1", (0, 0.78, 0.11), (0.42, 0.18, 0.08), M["frame"], 0.03))
    keep(cube("Step2", (0, 0.90, 0.055), (0.34, 0.14, 0.05), M["frame"], 0.02))

    # Front windows glow
    for nm, x, z, rr in [
        ("W1", -0.40, 0.70, 0.10),
        ("W2", 0.40, 0.46, 0.09),
        ("W3", -0.30, 1.02, 0.10),
        ("W4", 0.0, 1.28, 0.11),
    ]:
        keep(cyl(f"{nm}f", (x, 0.62, z), rr + 0.025, 0.05, M["frame"], rot=(math.pi / 2, 0, 0)))
        keep(sphere(f"{nm}g", (x, 0.66, z), rr, M["emit"] if nm != "W4" else M["emit_soft"]))

    # Side big window
    keep(cube("SideFrame", (0.68, 0.0, 0.75), (0.08, 0.58, 0.50), M["frame"], 0.03))
    keep(cube("SideGlow", (0.72, 0.0, 0.75), (0.04, 0.50, 0.42), M["emit"], 0.01))
    keep(cube("SideRoom", (0.50, 0.0, 0.75), (0.28, 0.48, 0.40), M["dark"], 0.02))
    keep(cube("CurtL", (0.66, -0.20, 0.80), (0.04, 0.09, 0.38), M["curtain"], 0.02))
    keep(cube("CurtR", (0.66, 0.22, 0.80), (0.04, 0.09, 0.38), M["curtain"], 0.02))
    for i, (y, z) in enumerate([(-0.20, 0.68), (-0.20, 0.88), (0.22, 0.68), (0.22, 0.88)]):
        keep(sphere(f"CDot{i}", (0.69, y, z), 0.022, M["lav"]))
    keep(cyl("LampStem", (0.52, 0.10, 0.58), 0.035, 0.10, M["pot"]))
    keep(sphere("LampShade", (0.52, 0.10, 0.68), 0.07, M["emit_soft"], sx=1, sy=1, sz=0.75))
    keep(cyl("InPot", (0.52, -0.10, 0.55), 0.04, 0.06, M["pot"]))
    keep(sphere("InPlant", (0.52, -0.10, 0.63), 0.05, M["leaf"]))

    # Mailbox
    keep(cyl("MailPost", (0.30, 0.78, 0.16), 0.025, 0.20, M["mail"]))
    keep(cube("MailBox", (0.30, 0.78, 0.30), (0.16, 0.12, 0.12), M["mail"], 0.03))
    keep(cube("MailFlag", (0.38, 0.78, 0.34), (0.04, 0.02, 0.08), M["lav"], 0.01))

    # Plants
    keep(cyl("PotBig", (-0.68, 0.70, 0.16), 0.11, 0.16, M["pot"]))
    for i, a in enumerate([0, 1.2, 2.4, 3.6, 4.8]):
        x = -0.68 + 0.045 * math.cos(a)
        y = 0.70 + 0.045 * math.sin(a)
        keep(cyl(f"Stem{i}", (x, y, 0.32), 0.012, 0.22, M["stem"]))
        keep(sphere(f"Bloom{i}", (x, y, 0.48), 0.05, M["lav"], sx=0.7, sy=0.7, sz=1.35))
    keep(cyl("PotS1", (0.48, 0.78, 0.13), 0.055, 0.10, M["pot"]))
    keep(sphere("PlS1", (0.48, 0.78, 0.23), 0.06, M["leaf"]))
    keep(cyl("PotS2", (0.62, 0.70, 0.12), 0.05, 0.09, M["pot"]))
    keep(sphere("PlS2", (0.62, 0.70, 0.21), 0.05, M["lav"]))

    # Stones
    for i, (x, y, s) in enumerate([(-0.12, 1.12, 0.13), (0.08, 1.30, 0.11), (-0.02, 1.48, 0.10)]):
        keep(sphere(f"Stone{i}", (x, y, 0.03), s, M["stone"], sx=1.35, sy=1.05, sz=0.22))

    empty(f"MOD_{MODULE_ID}_SOCKET_DOOR_FRONT", (0, 0.95, 0.15))
    empty(f"MOD_{MODULE_ID}_SOCKET_PATH_FRONT", (0, 1.4, 0))
    empty(f"MOD_{MODULE_ID}_SOCKET_PROP_LEFT", (-0.95, 0.5, 0.1))

    # Parent meshes to root preserving world
    for o in bpy.data.objects:
        if o == root:
            continue
        if o.type in {"MESH", "EMPTY"} and o.parent is None:
            mw = o.matrix_world.copy()
            o.parent = root
            o.matrix_world = mw

    log(f"mesh_count={sum(1 for o in bpy.data.objects if o.type=='MESH')}")
    return root


def export_glb(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Ensure materials travel: join not required
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=False,
        export_apply=True,
        export_cameras=False,
        export_lights=False,
        export_materials="EXPORT",
        export_image_format="AUTO",
    )
    log(f"export {path} size={path.stat().st_size}")


def render_preview(path: Path):
    # Soft lilac world
    w = bpy.data.worlds.new("CozyW")
    bpy.context.scene.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.93, 0.88, 0.95, 1)
    bg.inputs[1].default_value = 1.0

    bpy.ops.object.camera_add(location=(3.0, 3.4, 2.5))
    cam = bpy.context.active_object
    direction = Vector((0.0, 0.1, 0.9)) - Vector(cam.location)
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 50
    bpy.context.scene.camera = cam

    bpy.ops.object.light_add(type="SUN", location=(4, 3, 7))
    sun = bpy.context.active_object
    sun.data.energy = 3.0
    sun.rotation_euler = Euler((math.radians(50), math.radians(10), math.radians(25)), "XYZ")
    bpy.ops.object.light_add(type="AREA", location=(-2.5, 2, 3.5))
    fill = bpy.context.active_object
    fill.data.energy = 50
    fill.data.size = 5
    fill.data.color = (1.0, 0.95, 0.9)

    scene = bpy.context.scene
    # Workbench first for true material diffuse colors
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.render.resolution_x = 900
    scene.render.resolution_y = 900
    scene.render.filepath = str(path)
    scene.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    log(f"workbench render {path} exists={path.exists()}")

    # Also Cycles for beauty
    beauty = path.with_name(path.stem + "_cycles.png")
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 48
    scene.cycles.use_denoising = True
    scene.render.filepath = str(beauty)
    bpy.ops.render.render(write_still=True)
    log(f"cycles render {beauty} exists={beauty.exists()}")


def update_catalog(glb: Path):
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    d = sha(glb)
    n = glb.stat().st_size
    for m in data.get("modules", []):
        if m.get("module_id") == MODULE_ID:
            m["glb_sha256"] = d
            m["bytes"] = n
            m["source"] = JOB
            m["visual"] = "mockup_match_v3"
            break
    data["house_mockup_revision"] = JOB
    CATALOG.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log(f"catalog sha={d[:16]} bytes={n}")


def main():
    log("start")
    clear()
    build()
    quar = QUAR / f"{MODULE_ID}.glb"
    export_glb(quar)
    GAME_GLB.parent.mkdir(parents=True, exist_ok=True)
    GAME_GLB.write_bytes(quar.read_bytes())
    log(f"promoted {GAME_GLB}")
    update_catalog(GAME_GLB)
    preview = RENDER_DIR / f"{MODULE_ID}_blender_preview_v3.png"
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
