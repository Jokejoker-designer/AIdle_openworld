# -*- coding: utf-8 -*-
"""cozy_house_small_A mockup v4 — join solid clay cottage, no floating parts.

Fix: no reparent matrix bugs; join by part; dense scallop roof only;
smoke near chimney; Workbench+Cycles QA.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Vector

JOB = "COZY_HOUSE_MOCKUP_V4"
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
    "roof_a": (0.99, 0.78, 0.45),
    "roof_b": (1.00, 0.90, 0.48),
    "roof_c": (0.98, 0.82, 0.55),
    "ridge": (0.99, 0.95, 0.86),
    "door": (0.84, 0.55, 0.35),
    "frame": (0.92, 0.70, 0.50),
    "knob": (1.0, 0.92, 0.50),
    "base": (0.76, 0.66, 0.92),
    "emit": (1.0, 0.78, 0.32),
    "emit2": (1.0, 0.90, 0.58),
    "curtain": (0.80, 0.50, 0.88),
    "pot": (0.90, 0.58, 0.38),
    "lav": (0.74, 0.50, 0.92),
    "leaf": (0.50, 0.80, 0.50),
    "stem": (0.40, 0.58, 0.35),
    "mail": (0.65, 0.52, 0.90),
    "stone": (0.94, 0.90, 0.84),
    "smoke": (0.80, 0.58, 0.94),
    "chimney": (0.98, 0.94, 0.90),
    "dark": (0.38, 0.22, 0.14),
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


def set_mat(o, m):
    o.data.materials.clear()
    o.data.materials.append(m)


def fin(o, m, bevel=0.0):
    set_mat(o, m)
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
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=16, ring_count=10)
    o = bpy.context.active_object
    o.name = name
    o.scale = sc
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return fin(o, m, 0.0)


def cyl(name, loc, r, d, m, rot=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, vertices=16)
    o = bpy.context.active_object
    o.name = name
    if rot:
        o.rotation_euler = Euler(rot, "XYZ")
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    return fin(o, m, 0.0)


def join_named(name, objects, m):
    objs = [o for o in objects if o is not None and o.name in bpy.data.objects]
    if not objs:
        return None
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    if len(objs) > 1:
        bpy.ops.object.join()
    o = bpy.context.active_object
    o.name = name
    set_mat(o, m)
    o.select_set(False)
    return o


def build():
    M = {k: mat(f"M_{k}", v) for k, v in COL.items()}
    M["emit"] = mat("M_emit", COL["emit"], 0.35, 5.0)
    M["emit2"] = mat("M_emit2", COL["emit2"], 0.3, 4.0)
    M["smoke"] = mat("M_smoke", COL["smoke"], 1.0, 0.15)
    M["knob"] = mat("M_knob", COL["knob"], 0.25, 0.4)

    # --- BASE ---
    base_parts = [
        cube("b1", (0, 0, 0.05), (1.9, 1.7, 0.10), M["base"], 0.12),
        cube("b2", (0, 0.05, 0.01), (1.95, 1.75, 0.03), M["base"], 0.08),
    ]
    base = join_named("PART_Base", base_parts, M["base"])

    # --- BODY ---
    body_parts = [
        cube("body", (0, 0, 0.70), (1.28, 1.12, 1.18), M["wall"], 0.16),
        cube("front", (0, 0.48, 0.55), (0.92, 0.16, 0.82), M["wall"], 0.10),
        cube("attic", (0, 0, 1.32), (1.32, 1.14, 0.28), M["wall"], 0.10),
    ]
    body = join_named("PART_Body", body_parts, M["wall"])

    # --- ROOF tiles only (no floating slabs) ---
    # Build continuous scallop on two slopes as individual spheres then join by color
    roof_a, roof_b, roof_c = [], [], []
    buckets = [roof_a, roof_b, roof_c]
    mats_r = [M["roof_a"], M["roof_b"], M["roof_c"]]

    # Front slope: parametric plane
    # ridge at y=0, z=1.85; eave at y=0.62, z=1.22
    for row in range(8):
        t = row / 7.0
        y = 0.58 - t * 0.62
        z = 1.20 + t * 0.72
        n_col = 10
        for col in range(n_col):
            x = (col - (n_col - 1) / 2) * 0.155
            if row % 2:
                x += 0.07
            if abs(x) > 0.82:
                continue
            bi = (row + col) % 3
            o = sph(f"tf{row}_{col}", (x, y, z), 0.105, mats_r[bi], (1.4, 1.15, 0.38))
            o.rotation_euler = Euler((math.radians(-33), 0, 0), "XYZ")
            buckets[bi].append(o)

    # Back slope
    for row in range(6):
        t = row / 5.0
        y = -0.10 - t * 0.50
        z = 1.28 + t * 0.55
        for col in range(8):
            x = (col - 3.5) * 0.18
            if row % 2:
                x += 0.07
            if abs(x) > 0.78:
                continue
            bi = (row + col + 1) % 3
            o = sph(f"tb{row}_{col}", (x, y, z), 0.10, mats_r[bi], (1.3, 1.05, 0.36))
            o.rotation_euler = Euler((math.radians(33), 0, 0), "XYZ")
            buckets[bi].append(o)

    # Ridge soft cream beads
    ridge_parts = []
    for i, x in enumerate([-0.5, -0.25, 0, 0.25, 0.5]):
        ridge_parts.append(sph(f"rd{i}", (x, 0.0, 1.90), 0.09, M["ridge"], (1.2, 1.0, 0.65)))
    # small eave lips attached (short, not bars)
    ridge_parts.append(cube("eaveF", (0, 0.62, 1.18), (1.55, 0.10, 0.06), M["ridge"], 0.03))
    ridge_parts.append(cube("eaveB", (0, -0.55, 1.22), (1.50, 0.10, 0.06), M["ridge"], 0.03))
    roof_parts = []
    for bi, bucket in enumerate(buckets):
        j = join_named(f"PART_Roof{bi}", bucket, mats_r[bi])
        if j:
            roof_parts.append(j)
    ridge = join_named("PART_Ridge", ridge_parts, M["ridge"])
    if ridge:
        roof_parts.append(ridge)

    # --- CHIMNEY + SMOKE (tight cluster) ---
    chim_parts = [
        cube("ch", (0.38, -0.12, 1.98), (0.20, 0.20, 0.42), M["chimney"], 0.04),
        cube("chcap", (0.38, -0.12, 2.20), (0.26, 0.26, 0.07), M["chimney"], 0.03),
    ]
    chim = join_named("PART_Chimney", chim_parts, M["chimney"])
    smoke_parts = []
    for i, (dx, dy, dz, s) in enumerate([
        (0.0, 0.0, 0.12, 0.08),
        (0.06, 0.04, 0.24, 0.10),
        (0.12, 0.08, 0.34, 0.09),
        (0.18, 0.12, 0.42, 0.07),
        (0.24, 0.15, 0.48, 0.05),
    ]):
        smoke_parts.append(sph(f"sm{i}", (0.38 + dx, -0.12 + dy, 2.28 + dz), s, M["smoke"]))
    smoke = join_named("PART_Smoke", smoke_parts, M["smoke"])

    # --- DOOR ---
    door_parts = [
        cube("df", (0, 0.58, 0.52), (0.48, 0.06, 0.88), M["frame"], 0.05),
        cube("dd", (0, 0.62, 0.50), (0.36, 0.05, 0.70), M["door"], 0.05),
        cyl("da", (0, 0.62, 0.92), 0.22, 0.055, M["frame"], rot=(math.pi / 2, 0, 0)),
        sph("kn", (0.12, 0.68, 0.48), 0.042, M["knob"]),
        cube("s1", (0, 0.76, 0.10), (0.40, 0.16, 0.07), M["frame"], 0.03),
        cube("s2", (0, 0.88, 0.05), (0.32, 0.12, 0.05), M["frame"], 0.02),
    ]
    # door uses multi-materials after join - join frame and door separately
    door_frame = join_named("PART_DoorFrame", [door_parts[0], door_parts[2], door_parts[4], door_parts[5]], M["frame"])
    door_leaf = join_named("PART_Door", [door_parts[1], door_parts[3]], M["door"])

    # --- WINDOWS emit ---
    win_parts = []
    for nm, x, z, rr in [
        ("w1", -0.38, 0.68, 0.095),
        ("w2", 0.38, 0.45, 0.085),
        ("w3", -0.28, 1.00, 0.095),
        ("w4", 0.0, 1.26, 0.105),
    ]:
        win_parts.append(sph(f"{nm}g", (x, 0.64, z), rr, M["emit"] if nm != "w4" else M["emit2"]))
        win_parts.append(cyl(f"{nm}f", (x, 0.60, z), rr + 0.022, 0.045, M["frame"], rot=(math.pi / 2, 0, 0)))
    # side window
    win_parts.append(cube("sf", (0.66, 0.0, 0.74), (0.07, 0.55, 0.48), M["frame"], 0.03))
    win_parts.append(cube("sg", (0.70, 0.0, 0.74), (0.04, 0.48, 0.40), M["emit"], 0.01))
    win_parts.append(cube("sr", (0.48, 0.0, 0.74), (0.25, 0.45, 0.38), M["dark"], 0.02))
    win_parts.append(cube("cl", (0.64, -0.18, 0.78), (0.04, 0.08, 0.36), M["curtain"], 0.02))
    win_parts.append(cube("cr", (0.64, 0.20, 0.78), (0.04, 0.08, 0.36), M["curtain"], 0.02))
    # multi mat - keep separate join by material groups roughly as emit+frame mix: leave as separate objects under root
    # Join only pure emit glows
    glows = [o for o in win_parts if o.name.endswith("g") or o.name in ("sg",)]
    frames_w = [o for o in win_parts if o not in glows]
    win_glow = join_named("PART_WinGlow", glows, M["emit"])
    win_frame = join_named("PART_WinFrame", frames_w, M["frame"])

    # --- PROPS ---
    prop_parts = [
        cyl("mp", (0.28, 0.76, 0.15), 0.022, 0.18, M["mail"]),
        cube("mb", (0.28, 0.76, 0.28), (0.14, 0.10, 0.11), M["mail"], 0.03),
        cube("mf", (0.36, 0.76, 0.32), (0.035, 0.02, 0.07), M["lav"], 0.01),
        cyl("pb", (-0.66, 0.68, 0.15), 0.10, 0.15, M["pot"]),
    ]
    for i, a in enumerate([0, 1.25, 2.5, 3.8, 5.0]):
        x = -0.66 + 0.04 * math.cos(a)
        y = 0.68 + 0.04 * math.sin(a)
        prop_parts.append(cyl(f"st{i}", (x, y, 0.30), 0.011, 0.20, M["stem"]))
        prop_parts.append(sph(f"bl{i}", (x, y, 0.45), 0.045, M["lav"], (0.7, 0.7, 1.3)))
    prop_parts += [
        cyl("ps1", (0.48, 0.76, 0.12), 0.05, 0.09, M["pot"]),
        sph("pl1", (0.48, 0.76, 0.22), 0.055, M["leaf"]),
        cyl("ps2", (0.60, 0.68, 0.11), 0.045, 0.08, M["pot"]),
        sph("pl2", (0.60, 0.68, 0.20), 0.045, M["lav"]),
        sph("st0", (-0.10, 1.10, 0.03), 0.12, M["stone"], (1.3, 1.0, 0.22)),
        sph("st1", (0.08, 1.28, 0.03), 0.10, M["stone"], (1.3, 1.0, 0.22)),
        sph("st2", (-0.02, 1.45, 0.03), 0.09, M["stone"], (1.3, 1.0, 0.22)),
    ]
    # keep props separate by mat - join all non-critical as PART_Props with first mat (lossy colors)
    # Better: leave prop meshes as-is (many objects ok for GLB)
    props = prop_parts  # no join

    # Root empty + sockets
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = f"MOD_{MODULE_ID}"
    root.empty_display_size = 0.12
    for nm, loc in [
        (f"MOD_{MODULE_ID}_SOCKET_DOOR_FRONT", (0, 0.95, 0.15)),
        (f"MOD_{MODULE_ID}_SOCKET_PATH_FRONT", (0, 1.4, 0)),
        (f"MOD_{MODULE_ID}_SOCKET_PROP_LEFT", (-0.95, 0.5, 0.1)),
    ]:
        bpy.ops.object.empty_add(type="PLAIN_AXES", location=loc)
        e = bpy.context.active_object
        e.name = nm
        e.empty_display_size = 0.08
        e.parent = root

    # Parent all mesh parts under root WITHOUT changing world (objects already in world space)
    for o in list(bpy.data.objects):
        if o.type == "MESH" and o.parent is None:
            o.parent = root
            # clear parent inverse so local = world at origin hierarchy
            o.matrix_parent_inverse.identity()

    # Fix: after parent with identity inverse, if object was at world pos it stays
    # Actually parenting with identity inverse keeps local = previous world if parent at origin.
    # Parent at 0,0,0 so OK.

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

    bpy.ops.object.camera_add(location=(2.9, 3.3, 2.35))
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
    fill.data.energy = 45
    fill.data.size = 4

    sc = bpy.context.scene
    sc.render.resolution_x = 900
    sc.render.resolution_y = 900
    sc.render.image_settings.file_format = "PNG"

    sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"
    sc.display.shading.color_type = "MATERIAL"
    sc.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    log(f"wb {path.exists()}")

    beauty = path.with_name(path.stem + "_cycles.png")
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 40
    sc.cycles.use_denoising = True
    sc.render.filepath = str(beauty)
    bpy.ops.render.render(write_still=True)
    log(f"cy {beauty.exists()}")


def update_catalog(glb: Path):
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    d = sha(glb)
    n = glb.stat().st_size
    for m in data.get("modules", []):
        if m.get("module_id") == MODULE_ID:
            m["glb_sha256"] = d
            m["bytes"] = n
            m["source"] = JOB
            m["visual"] = "mockup_match_v4"
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
    preview = RENDER_DIR / f"{MODULE_ID}_blender_preview_v4.png"
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
