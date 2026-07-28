# -*- coding: utf-8 -*-
"""cozy_house_small_A mockup v6 — solid gable + front scallops only (no join distortion)."""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Vector

JOB = "COZY_HOUSE_MOCKUP_V9"
MODULE_ID = "cozy_house_small_A"
QUAR = Path(r"E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine") / JOB
GAME_GLB = Path(r"E:\AIdle_openworld\game\assets\p1e_cozy\modules") / f"{MODULE_ID}.glb"
CATALOG = Path(r"E:\AIdle_openworld\game\resources\p1e_cozy\module_catalog.json")
RENDER_DIR = Path(
    r"E:\AIdle_openworld\orchestration\control\visual_reference\mockup_cast_props_001\gen"
)
QUAR.mkdir(parents=True, exist_ok=True)
RENDER_DIR.mkdir(parents=True, exist_ok=True)

COL = {
    "wall": (0.99, 0.94, 0.88),
    "roof_a": (0.99, 0.70, 0.32),
    "roof_b": (1.00, 0.86, 0.35),
    "roof_c": (0.99, 0.78, 0.45),
    "ridge": (0.99, 0.95, 0.86),
    "door": (0.82, 0.52, 0.32),
    "frame": (0.92, 0.70, 0.50),
    "knob": (1.0, 0.92, 0.50),
    "base": (0.76, 0.66, 0.92),
    "emit": (1.0, 0.76, 0.30),
    "emit2": (1.0, 0.90, 0.55),
    "curtain": (0.80, 0.50, 0.88),
    "pot": (0.90, 0.58, 0.38),
    "lav": (0.74, 0.50, 0.92),
    "leaf": (0.50, 0.80, 0.50),
    "stem": (0.40, 0.58, 0.35),
    "mail": (0.65, 0.52, 0.90),
    "stone": (0.94, 0.90, 0.84),
    "smoke": (0.80, 0.58, 0.94),
    "chimney": (0.98, 0.94, 0.90),
    "dark": (0.40, 0.24, 0.16),
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


def mat(name, rgb, rough=0.55, emit=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.diffuse_color = (*rgb, 1.0)
    bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = rough
        if emit > 0:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = (*rgb, 1.0)
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emit
    return m


def setm(o, m):
    o.data.materials.clear()
    o.data.materials.append(m)


def fin(o, m, bevel=0.0):
    setm(o, m)
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    if bevel > 0:
        try:
            bpy.ops.object.modifier_add(type="BEVEL")
            md = o.modifiers[-1]
            md.width = bevel
            md.segments = 3
            md.limit_method = "ANGLE"
            bpy.ops.object.modifier_apply(modifier=md.name)
        except Exception:
            pass
    try:
        bpy.ops.object.shade_smooth()
    except Exception:
        pass
    o.select_set(False)
    return o


def cube(name, loc, sc, m, bevel=0.05):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = sc
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return fin(o, m, bevel)


def sph(name, loc, r, m, sc=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=14, ring_count=10)
    o = bpy.context.active_object
    o.name = name
    o.scale = sc
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return fin(o, m, 0.0)


def cyl(name, loc, r, d, m, rot=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, vertices=14)
    o = bpy.context.active_object
    o.name = name
    if rot:
        o.rotation_euler = Euler(rot, "XYZ")
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    return fin(o, m, 0.0)


def build():
    M = {k: mat(f"M_{k}", v) for k, v in COL.items()}
    M["emit"] = mat("M_emit", COL["emit"], 0.35, 5.5)
    M["emit2"] = mat("M_emit2", COL["emit2"], 0.3, 4.5)
    M["smoke"] = mat("M_smoke", COL["smoke"], 1.0, 0.2)
    M["knob"] = mat("M_knob", COL["knob"], 0.25, 0.5)

    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = f"MOD_{MODULE_ID}"

    # Base
    cube("Base", (0, 0, 0.05), (1.9, 1.7, 0.10), M["base"], 0.13)

    # Body solid
    cube("Body", (0, 0, 0.68), (1.28, 1.12, 1.15), M["wall"], 0.16)
    cube("Attic", (0, 0, 1.30), (1.30, 1.10, 0.35), M["wall"], 0.10)
    cube("Front", (0, 0.50, 0.55), (1.05, 0.22, 0.95), M["wall"], 0.12)

    # Solid gable roof (triangular mass via two thick slopes) — cream base
    for sign, nm in ((1, "GableF"), (-1, "GableB")):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, sign * 0.30, 1.50))
        o = bpy.context.active_object
        o.name = nm
        o.scale = (1.48, 0.90, 0.12)
        o.rotation_euler = Euler((sign * math.radians(32), 0, 0), "XYZ")
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        fin(o, M["ridge"], 0.04)

    # Roof ends (gable triangles approximated by cubes)
        
    # FRONT scallop tiles only (camera-facing) — no join, no back wild tiles
    mats_r = [M["roof_a"], M["roof_b"], M["roof_c"]]
    for row in range(8):
        t = row / 7.0
        y = 0.55 - t * 0.55
        z = 1.22 + t * 0.68
        n_col = 10
        for col in range(n_col):
            x = (col - (n_col - 1) / 2) * 0.16
            if row % 2:
                x += 0.08
            if abs(x) > 0.78:
                continue
            m = mats_r[(row + col) % 3]
            o = sph(f"Tile{row}_{col}", (x, y, z), 0.12, m, (1.55, 1.35, 0.28))
            o.rotation_euler = Euler((math.radians(-32), 0, 0), "XYZ")
            # keep rotation as object transform (export_apply will bake)

    # Ridge beads
    for i, x in enumerate([-0.45, -0.22, 0, 0.22, 0.45]):
        sph(f"Ridge{i}", (x, 0.02, 1.88), 0.085, M["ridge"], (1.15, 1.0, 0.7))

    # Chimney
    cube("Chimney", (0.36, -0.10, 1.95), (0.20, 0.20, 0.40), M["chimney"], 0.04)
    cube("ChimCap", (0.36, -0.10, 2.16), (0.26, 0.26, 0.07), M["chimney"], 0.03)
    for i, (dx, dy, dz, s) in enumerate([
        (0.0, 0.0, 0.10, 0.075),
        (0.05, 0.04, 0.20, 0.095),
        (0.10, 0.08, 0.30, 0.08),
        (0.16, 0.12, 0.38, 0.06),
        (0.22, 0.16, 0.44, 0.045),
    ]):
        sph(f"Smoke{i}", (0.36 + dx, -0.10 + dy, 2.22 + dz), s, M["smoke"])

    # Door — solid fill, no black cavity
    cube("DoorWall", (0, 0.48, 0.50), (0.55, 0.18, 0.90), M["wall"], 0.06)
    cube("DoorFrame", (0, 0.58, 0.52), (0.46, 0.06, 0.86), M["frame"], 0.05)
    cube("Door", (0, 0.62, 0.50), (0.34, 0.05, 0.68), M["door"], 0.05)
    sph("DoorArch", (0, 0.64, 0.92), 0.20, M["frame"], (1.0, 0.35, 0.55))
    sph("Knob", (0.11, 0.68, 0.48), 0.04, M["knob"])
    cube("Step1", (0, 0.76, 0.10), (0.38, 0.16, 0.07), M["frame"], 0.03)
    cube("Step2", (0, 0.88, 0.05), (0.30, 0.12, 0.05), M["frame"], 0.02)

    # Windows
    for nm, x, z, rr in [
        ("W1", -0.36, 0.68, 0.095),
        ("W2", 0.36, 0.46, 0.085),
        ("W3", -0.26, 1.00, 0.09),
        ("W4", 0.0, 1.24, 0.10),
    ]:
        cyl(f"{nm}f", (x, 0.60, z), rr + 0.02, 0.04, M["frame"], rot=(math.pi / 2, 0, 0))
        sph(f"{nm}g", (x, 0.64, z), rr, M["emit"] if nm != "W4" else M["emit2"])

    # Side window with interior
    cube("SideFill", (0.60, 0.0, 0.74), (0.12, 0.50, 0.42), M["dark"], 0.02)
    cube("SideFrame", (0.66, 0.0, 0.74), (0.07, 0.54, 0.46), M["frame"], 0.03)
    cube("SideGlow", (0.70, 0.0, 0.74), (0.04, 0.46, 0.38), M["emit"], 0.01)
    cube("CurtL", (0.64, -0.16, 0.78), (0.04, 0.07, 0.34), M["curtain"], 0.02)
    cube("CurtR", (0.64, 0.18, 0.78), (0.04, 0.07, 0.34), M["curtain"], 0.02)
    cyl("Lamp", (0.52, 0.08, 0.58), 0.03, 0.08, M["pot"])
    sph("LampG", (0.52, 0.08, 0.66), 0.06, M["emit2"], (1, 1, 0.7))
    cyl("InPot", (0.52, -0.08, 0.55), 0.035, 0.05, M["pot"])
    sph("InLeaf", (0.52, -0.08, 0.62), 0.045, M["leaf"])

    # Mail + pots + stones
    cyl("MailPost", (0.28, 0.76, 0.15), 0.022, 0.18, M["mail"])
    cube("MailBox", (0.28, 0.76, 0.28), (0.14, 0.10, 0.11), M["mail"], 0.03)
    cube("MailFlag", (0.36, 0.76, 0.32), (0.03, 0.02, 0.07), M["lav"], 0.01)

    cyl("PotBig", (-0.66, 0.68, 0.15), 0.10, 0.15, M["pot"])
    for i, a in enumerate([0, 1.25, 2.5, 3.8, 5.0]):
        x = -0.66 + 0.04 * math.cos(a)
        y = 0.68 + 0.04 * math.sin(a)
        cyl(f"Stem{i}", (x, y, 0.30), 0.011, 0.20, M["stem"])
        sph(f"Bloom{i}", (x, y, 0.44), 0.045, M["lav"], (0.7, 0.7, 1.3))
    cyl("PotS1", (0.48, 0.76, 0.12), 0.05, 0.09, M["pot"])
    sph("PlS1", (0.48, 0.76, 0.22), 0.055, M["leaf"])
    cyl("PotS2", (0.60, 0.68, 0.11), 0.045, 0.08, M["pot"])
    sph("PlS2", (0.60, 0.68, 0.20), 0.045, M["lav"])

    for i, (x, y, s) in enumerate([(-0.10, 1.10, 0.12), (0.08, 1.28, 0.10), (-0.02, 1.45, 0.09)]):
        sph(f"Stone{i}", (x, y, 0.03), s, M["stone"], (1.3, 1.0, 0.22))

    # sockets
    for nm, loc in [
        (f"MOD_{MODULE_ID}_SOCKET_DOOR_FRONT", (0, 0.95, 0.15)),
        (f"MOD_{MODULE_ID}_SOCKET_PATH_FRONT", (0, 1.4, 0)),
        (f"MOD_{MODULE_ID}_SOCKET_PROP_LEFT", (-0.95, 0.5, 0.1)),
    ]:
        bpy.ops.object.empty_add(type="PLAIN_AXES", location=loc)
        e = bpy.context.active_object
        e.name = nm
        e.parent = root

    # Parent meshes to root (parent at origin)
    for o in list(bpy.data.objects):
        if o != root and o.type == "MESH" and o.parent is None:
            o.parent = root
            o.matrix_parent_inverse.identity()

    log(f"meshes={sum(1 for o in bpy.data.objects if o.type=='MESH')}")
    return root


def export_glb(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=False,
        export_apply=True,
        export_cameras=False,
        export_lights=False,
        export_materials="EXPORT",
    )
    log(f"export {path} size={path.stat().st_size}")


def render_preview(path: Path):
    w = bpy.data.worlds.new("W")
    bpy.context.scene.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.94, 0.90, 0.96, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 1.0

    bpy.ops.object.camera_add(location=(2.85, 3.25, 2.30))
    cam = bpy.context.active_object
    d = Vector((0.0, 0.05, 0.95)) - Vector(cam.location)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 52
    bpy.context.scene.camera = cam

    bpy.ops.object.light_add(type="SUN", location=(3, 2, 6))
    sun = bpy.context.active_object
    sun.data.energy = 2.8
    sun.rotation_euler = Euler((math.radians(48), 0.2, 0.4), "XYZ")
    bpy.ops.object.light_add(type="AREA", location=(-2, 1.5, 3))
    fill = bpy.context.active_object
    fill.data.energy = 50
    fill.data.size = 4

    sc = bpy.context.scene
    sc.render.resolution_x = 900
    sc.render.resolution_y = 900
    sc.render.image_settings.file_format = "PNG"
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 48
    sc.cycles.use_denoising = True
    sc.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    log(f"render {path.exists()}")


def update_catalog(glb: Path):
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    d = sha(glb)
    n = glb.stat().st_size
    for m in data.get("modules", []):
        if m.get("module_id") == MODULE_ID:
            m["glb_sha256"] = d
            m["bytes"] = n
            m["source"] = JOB
            m["visual"] = "mockup_match_v9"
            break
    data["house_mockup_revision"] = JOB
    CATALOG.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    log(f"catalog {d[:16]} {n}")


def main():
    log("start")
    clear()
    build()
    quar = QUAR / f"{MODULE_ID}.glb"
    export_glb(quar)
    GAME_GLB.write_bytes(quar.read_bytes())
    log(f"promoted {GAME_GLB}")
    update_catalog(GAME_GLB)
    preview = RENDER_DIR / f"{MODULE_ID}_blender_preview_v9.png"
    try:
        render_preview(preview)
    except Exception as e:
        log(f"render fail {e}")
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
