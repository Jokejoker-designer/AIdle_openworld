# -*- coding: utf-8 -*-
"""PASS 1D — PRIMARY MASSING REBUILD
ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01

Rejects narrow 24×19 tower-column layout. Rebuilds ~20–30 major architectural
masses for silhouette match to 6-view mockup. Clay only. No windows/doors/detail.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import bpy
from mathutils import Euler, Vector

JOB = "ROYAL_LIGHTKEEP_PASS1D"
ASSET = "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01"
OUT = Path(r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep")
BLEND = OUT / f"{ASSET}_PASS1D.blend"
RENDER = OUT / "renders_pass1d"
QUAR = Path(r"E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine") / JOB

# Overall complex — silhouette priority over mockup text 24×19
W = 44.0   # total width X
D = 30.0   # total depth Y
TOWER_H = 38.0
TERRACE_Z = 5.8
WALL_H = 6.2


def log(m: str) -> None:
    print(f"[{JOB}] {m}")


def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for coll in list(bpy.data.collections):
        if coll.name not in ("Collection", "Scene Collection"):
            bpy.data.collections.remove(coll)
    for db in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for b in list(db):
            db.remove(b)


def units():
    s = bpy.context.scene
    s.unit_settings.system = "METRIC"
    s.unit_settings.scale_length = 1.0
    s.render.resolution_x = 1400
    s.render.resolution_y = 1050
    s.render.resolution_percentage = 100
    s.render.film_transparent = False
    w = bpy.data.worlds.new("W_CLAY") if "W_CLAY" not in bpy.data.worlds else bpy.data.worlds["W_CLAY"]
    s.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.78, 0.80, 0.83, 1.0)
        bg.inputs[1].default_value = 1.0


def clay(name, rgb):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    n = m.node_tree.nodes.get("Principled BSDF")
    if n:
        n.inputs["Base Color"].default_value = (*rgb, 1.0)
        if "Roughness" in n.inputs:
            n.inputs["Roughness"].default_value = 0.9
        if "Metallic" in n.inputs:
            n.inputs["Metallic"].default_value = 0.0
    return m


def coll(name):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in [x.name for x in bpy.context.scene.collection.children]:
        bpy.context.scene.collection.children.link(c)
    return c


def mass(name, center, size, mat, c):
    """center XYZ, size full extents XYZ in meters."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    o = bpy.context.active_object
    o.name = name
    o.dimensions = Vector(size)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.location = Vector(center)
    if o.data.materials:
        o.data.materials[0] = mat
    else:
        o.data.materials.append(mat)
    for u in list(o.users_collection):
        u.objects.unlink(o)
    c.objects.link(o)
    return o


def hip_roof(name, center, footprint_xy, height, mat, c, rot_z=0.0):
    """Simple pitched roof as scaled cube (massing only)."""
    sx, sy = footprint_xy
    o = mass(name, (center[0], center[1], center[2]), (sx, sy, height), mat, c)
    if rot_z:
        o.rotation_euler.z = math.radians(rot_z)
    return o


def cone_roof(name, loc, r, h, mat, c):
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=r, radius2=0.08, depth=h, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.rotation_euler = Euler((0, 0, math.radians(45)), "XYZ")
    if o.data.materials:
        o.data.materials[0] = mat
    else:
        o.data.materials.append(mat)
    for u in list(o.users_collection):
        u.objects.unlink(o)
    c.objects.link(o)
    return o


def build():
    M = {
        "base": clay("CLAY_BASE", (0.52, 0.52, 0.54)),
        "terr": clay("CLAY_TERR", (0.56, 0.56, 0.58)),
        "tower": clay("CLAY_TOWER", (0.60, 0.60, 0.62)),
        "bar": clay("CLAY_BAR", (0.55, 0.55, 0.57)),
        "gate": clay("CLAY_GATE", (0.53, 0.53, 0.56)),
        "roof": clay("CLAY_ROOF", (0.38, 0.42, 0.50)),
        "stair": clay("CLAY_STAIR", (0.48, 0.48, 0.50)),
        "ground": clay("CLAY_GND", (0.68, 0.70, 0.66)),
        "void": clay("CLAY_VOID", (0.72, 0.74, 0.70)),
        "human": clay("CLAY_HUMAN", (0.2, 0.2, 0.22)),
    }
    c_base = coll("FORTIFIED_BASE")
    c_tower = coll("WATCHTOWER_MAIN")
    c_bar = coll("BARRACKS_LEFT")
    c_right = coll("RIGHT_WING_GATE")
    c_court = coll("COURTYARD")
    c_stair = coll("CIRCULATION")
    c_tur = coll("MAJOR_TURRETS")
    c_roof = coll("ROOF_MASS")
    c_cam = coll("CAMERAS_6")
    c_ref = coll("SCALE_REF")

    # Ground
    mass("LEVEL0_GROUND", (0, 0, -0.4), (70, 55, 0.8), M["ground"], c_base)

    # ---- LEVEL 1 lower fortification (3–4 m) with corner projections ----
    mass("LEVEL1_CORE", (0, 0, 1.8), (W - 2, D - 2, 3.6), M["base"], c_base)
    mass("LEVEL1_CORNER_FL", (-W * 0.42, D * 0.38, 2.0), (6, 5, 4.0), M["base"], c_base)
    mass("LEVEL1_CORNER_FR", (W * 0.40, D * 0.36, 2.0), (5.5, 5, 4.0), M["base"], c_base)
    mass("LEVEL1_CORNER_RL", (-W * 0.40, -D * 0.38, 2.0), (6, 5, 4.0), M["base"], c_base)
    mass("LEVEL1_CORNER_RR", (W * 0.38, -D * 0.36, 2.0), (5.5, 5, 4.0), M["base"], c_base)

    # ---- LEVEL 2 main terrace (5.5–7 m), non-rectangular ----
    # Front terrace wider
    mass("TERRACE_FRONT", (0, 8.5, TERRACE_Z * 0.5), (36, 10, TERRACE_Z), M["terr"], c_base)
    mass("TERRACE_LEFT", (-12, 0, TERRACE_Z * 0.5), (16, 22, TERRACE_Z), M["terr"], c_base)
    mass("TERRACE_RIGHT", (12, -1, TERRACE_Z * 0.5), (14, 20, TERRACE_Z), M["terr"], c_base)
    mass("TERRACE_REAR_BAND", (0, -10, TERRACE_Z * 0.45), (34, 8, TERRACE_Z * 0.9), M["terr"], c_base)
    # Parapet rim (perimeter mass, stepped)
    mass("PARAPET_FRONT", (0, 13.2, TERRACE_Z + 0.7), (38, 1.0, 1.4), M["base"], c_base)
    mass("PARAPET_LEFT", (-20.5, 0, TERRACE_Z + 0.7), (1.0, 26, 1.4), M["base"], c_base)
    mass("PARAPET_RIGHT", (20.0, 0, TERRACE_Z + 0.7), (1.0, 24, 1.4), M["base"], c_base)
    mass("PARAPET_REAR", (0, -14.0, TERRACE_Z + 0.7), (36, 1.0, 1.4), M["base"], c_base)

    # ---- COURTYARD VOID (true open pad, not filled by buildings) ----
    # Courtyard sits in U: tower front-center, barracks left, gate right-rear
    court_cx, court_cy = 3.0, -2.0
    court_w, court_d = 13.0, 11.0
    mass(
        "COURTYARD_VOID_GUIDE",
        (court_cx, court_cy, TERRACE_Z + 0.15),
        (court_w, court_d, 0.3),
        M["void"],
        c_court,
    )

    # ============================================================
    # TOWER — continuous 4 parts (NOT thin column)
    # ============================================================
    # Gatehouse base: 10×9×12 on terrace
    tw_x, tw_y = 1.5, 5.0  # slightly right, front-biased on terrace
    gh_w, gh_d, gh_h = 10.2, 9.2, 12.0
    gh_z = TERRACE_Z + gh_h * 0.5
    mass("TOWER_GATEHOUSE_BASE", (tw_x, tw_y, gh_z), (gh_w, gh_d, gh_h), M["tower"], c_tower)
    # Portal shoulder proxy (wider front face)
    mass(
        "TOWER_PORTAL_SHOULDER",
        (tw_x, tw_y + gh_d * 0.42, TERRACE_Z + 4.5),
        (7.5, 2.2, 9.0),
        M["tower"],
        c_tower,
    )
    # Connectors to wings
    mass("CONNECTOR_TO_BARRACKS", (tw_x - 7.5, tw_y - 1.0, TERRACE_Z + 5.0), (6.0, 6.0, 10.0), M["bar"], c_bar)
    mass("CONNECTOR_TO_RIGHT", (tw_x + 7.0, tw_y - 2.0, TERRACE_Z + 4.5), (5.0, 5.5, 9.0), M["gate"], c_right)

    # Shaft 8×8×19 continuous on gatehouse
    sh_w = 8.0
    sh_h = 19.5
    sh_z = TERRACE_Z + gh_h + sh_h * 0.5
    mass("TOWER_SHAFT", (tw_x, tw_y, sh_z), (sh_w, sh_w, sh_h), M["tower"], c_tower)

    # Observation wider 15–30%
    obs_w = sh_w * 1.22
    obs_h = 5.0
    obs_z = TERRACE_Z + gh_h + sh_h + obs_h * 0.5
    mass("TOWER_OBSERVATION_BLOCK", (tw_x, tw_y, obs_z), (obs_w, obs_w, obs_h), M["tower"], c_tower)
    # Corner projections on observation
    for i, (dx, dy) in enumerate([(-1, -1), (-1, 1), (1, -1), (1, 1)]):
        mass(
            f"TOWER_OBS_CORNER_{i}",
            (tw_x + dx * obs_w * 0.42, tw_y + dy * obs_w * 0.42, obs_z),
            (2.4, 2.4, obs_h + 0.8),
            M["tower"],
            c_tur,
        )

    # Roof crown continuous — single hip block + peak, 4 corner spires attached
    roof_h = 6.0
    roof_z = TERRACE_Z + gh_h + sh_h + obs_h + roof_h * 0.35
    mass(
        "TOWER_ROOF_BLOCK",
        (tw_x, tw_y, roof_z),
        (obs_w * 1.15, obs_w * 1.15, roof_h * 0.7),
        M["roof"],
        c_roof,
    )
    cone_roof(
        "TOWER_ROOF_PEAK",
        (tw_x, tw_y, roof_z + roof_h * 0.55),
        obs_w * 0.72,
        roof_h * 0.95,
        M["roof"],
        c_roof,
    )
    for i, (dx, dy) in enumerate([(-1, -1), (-1, 1), (1, -1), (1, 1)]):
        px = tw_x + dx * obs_w * 0.48
        py = tw_y + dy * obs_w * 0.48
        mass(f"TOWER_SPIRE_BASE_{i}", (px, py, obs_z + 1.2), (1.6, 1.6, 3.5), M["tower"], c_tur)
        cone_roof(f"TOWER_SPIRE_{i}", (px, py, obs_z + 4.2), 1.1, 3.5, M["roof"], c_roof)

    # Flag
    flag_z = TERRACE_Z + gh_h + sh_h + obs_h + roof_h + 0.5
    mass("TOWER_FLAG_MAST", (tw_x, tw_y, flag_z), (0.25, 0.25, 2.8), M["tower"], c_tower)
    mass("TOWER_FLAG", (tw_x + 1.0, tw_y, flag_z + 0.6), (2.0, 0.1, 1.0), M["roof"], c_tower)

    # ============================================================
    # LEFT BARRACKS — long horizontal mass (dominant left)
    # ============================================================
    # Length 22m, depth 11m, eave ~9m above terrace
    bar_len, bar_dep = 22.0, 11.0
    bar_eave = 9.0
    bar_cx = -12.0  # left of tower
    bar_cy = 1.0
    bar_z = TERRACE_Z + bar_eave * 0.5
    mass("BARRACKS_LEFT_MAIN", (bar_cx, bar_cy, bar_z), (bar_len, bar_dep, bar_eave), M["bar"], c_bar)
    # Front gable projection
    mass(
        "BARRACKS_LEFT_GABLE_BLOCK",
        (bar_cx - 2.0, bar_cy + bar_dep * 0.42, TERRACE_Z + 7.5),
        (6.5, 3.2, 15.0),
        M["bar"],
        c_bar,
    )
    # Roof ridge long — pitched mass (tall thin roof volume)
    ridge_h = 5.5
    mass(
        "BARRACKS_LEFT_ROOF",
        (bar_cx, bar_cy, TERRACE_Z + bar_eave + ridge_h * 0.45),
        (bar_len + 1.2, bar_dep + 1.0, ridge_h),
        M["roof"],
        c_roof,
    )
    mass(
        "BARRACKS_GABLE_ROOF",
        (bar_cx - 2.0, bar_cy + bar_dep * 0.42, TERRACE_Z + 16.0),
        (7.0, 4.0, 5.0),
        M["roof"],
        c_roof,
    )
    # Barracks corner turrets (1–2 major)
    mass("BAR_TURRET_FRONT_L", (bar_cx - bar_len * 0.42, bar_cy + bar_dep * 0.42, TERRACE_Z + 8), (3.0, 3.0, 12.0), M["tower"], c_tur)
    cone_roof("BAR_TURRET_FRONT_L_ROOF", (bar_cx - bar_len * 0.42, bar_cy + bar_dep * 0.42, TERRACE_Z + 15.5), 1.9, 4.0, M["roof"], c_roof)
    mass("BAR_TURRET_REAR_L", (bar_cx - bar_len * 0.40, bar_cy - bar_dep * 0.40, TERRACE_Z + 7), (2.8, 2.8, 10.5), M["tower"], c_tur)
    cone_roof("BAR_TURRET_REAR_L_ROOF", (bar_cx - bar_len * 0.40, bar_cy - bar_dep * 0.40, TERRACE_Z + 13.5), 1.7, 3.5, M["roof"], c_roof)

    # ============================================================
    # RIGHT WING + GATEHOUSE
    # ============================================================
    rw_len, rw_dep = 13.0, 10.0
    rw_eave = 8.0
    rw_cx, rw_cy = 13.0, -1.5
    mass("RIGHT_WING_MAIN", (rw_cx, rw_cy, TERRACE_Z + rw_eave * 0.5), (rw_len, rw_dep, rw_eave), M["gate"], c_right)
    mass(
        "RIGHT_WING_ROOF",
        (rw_cx, rw_cy, TERRACE_Z + rw_eave + 2.2),
        (rw_len + 0.8, rw_dep + 0.8, 4.5),
        M["roof"],
        c_roof,
    )
    # Gatehouse with tunnel depth (arch proxy = lower center notch via two side walls + top)
    ghx, ghy = 12.5, -8.5
    mass("RIGHT_GATEHOUSE", (ghx, ghy, TERRACE_Z + 5.0), (8.0, 7.0, 10.0), M["gate"], c_right)
    mass("RIGHT_GATE_TUNNEL_TOP", (ghx, ghy - 0.5, TERRACE_Z + 7.5), (5.0, 4.5, 3.5), M["gate"], c_right)
    mass("RIGHT_GATE_SIDE_L", (ghx - 2.8, ghy - 0.5, TERRACE_Z + 4.0), (1.8, 4.5, 8.0), M["gate"], c_right)
    mass("RIGHT_GATE_SIDE_R", (ghx + 2.8, ghy - 0.5, TERRACE_Z + 4.0), (1.8, 4.5, 8.0), M["gate"], c_right)
    mass("RIGHT_GATE_ROOF", (ghx, ghy, TERRACE_Z + 11.5), (8.5, 7.5, 3.8), M["roof"], c_roof)
    mass("RIGHT_TURRET_A", (rw_cx + 5.0, rw_cy + 4.0, TERRACE_Z + 7), (2.6, 2.6, 11.0), M["tower"], c_tur)
    cone_roof("RIGHT_TURRET_A_ROOF", (rw_cx + 5.0, rw_cy + 4.0, TERRACE_Z + 14), 1.6, 3.2, M["roof"], c_roof)
    mass("RIGHT_TURRET_B", (ghx + 3.5, ghy - 2.5, TERRACE_Z + 6.5), (2.5, 2.5, 10.0), M["tower"], c_tur)
    cone_roof("RIGHT_TURRET_B_ROOF", (ghx + 3.5, ghy - 2.5, TERRACE_Z + 13), 1.5, 3.0, M["roof"], c_roof)

    # ============================================================
    # MAIN STAIR — wide leading line to tower gate
    # ============================================================
    stair_w = 6.2
    n_steps = 16
    for i in range(n_steps):
        t = i / (n_steps - 1)
        z = 0.2 + t * TERRACE_Z
        y = 16.5 - t * 6.5
        mass(f"MAIN_STAIR_{i:02d}", (tw_x, y, z), (stair_w * (1.0 - 0.15 * t), 1.15, 0.4), M["stair"], c_stair)
    mass("MAIN_STAIR_LANDING", (tw_x, 11.5, TERRACE_Z * 0.55), (6.0, 2.2, 0.5), M["stair"], c_stair)
    mass("MAIN_STAIR_RAIL_L", (tw_x - stair_w * 0.55, 13.5, TERRACE_Z * 0.45), (0.6, 8.0, TERRACE_Z * 0.7), M["base"], c_stair)
    mass("MAIN_STAIR_RAIL_R", (tw_x + stair_w * 0.55, 13.5, TERRACE_Z * 0.45), (0.6, 8.0, TERRACE_Z * 0.7), M["base"], c_stair)

    # Side ramp/stair diagonal (left front) — strong diagonal silhouette
    for i in range(12):
        t = i / 11.0
        z = 0.25 + t * TERRACE_Z
        x = -20.0 + t * 6.0
        y = 12.0 - t * 5.5
        mass(f"SIDE_RAMP_{i:02d}", (x, y, z), (2.8, 1.6, 0.4), M["stair"], c_stair)
    mass("SIDE_RAMP_RAIL_OUT", (-18.5, 9.5, TERRACE_Z * 0.4), (0.7, 10.0, TERRACE_Z * 0.65), M["base"], c_stair)
    mass("SIDE_RAMP_RAIL_IN", (-16.0, 9.0, TERRACE_Z * 0.4), (0.7, 9.0, TERRACE_Z * 0.65), M["base"], c_stair)

    # Rear stair to gatehouse
    for i in range(10):
        t = i / 9.0
        z = 0.25 + t * (TERRACE_Z * 0.85)
        y = -16.5 + t * 4.5
        mass(f"REAR_STAIR_{i:02d}", (ghx, y, z), (4.5, 1.3, 0.4), M["stair"], c_stair)

    # Human scale at stair base
    bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=1.8, location=(tw_x, 17.2, 0.9))
    h = bpy.context.active_object
    h.name = "SCALE_HUMAN_1M8"
    if h.data.materials:
        h.data.materials[0] = M["human"]
    else:
        h.data.materials.append(M["human"])
    for u in list(h.users_collection):
        u.objects.unlink(h)
    c_ref.objects.link(h)

    dims = {
        "total_width_m": W,
        "total_depth_m": D,
        "total_height_m": TOWER_H,
        "terrace_height_m": TERRACE_Z,
        "tower_gatehouse": {"w": gh_w, "d": gh_d, "h": gh_h, "center": [tw_x, tw_y]},
        "tower_shaft": {"w": sh_w, "h": sh_h},
        "tower_obs": {"w": obs_w, "h": obs_h},
        "barracks": {"length": bar_len, "depth": bar_dep, "eave_h": bar_eave, "center": [bar_cx, bar_cy]},
        "right_wing": {"length": rw_len, "depth": rw_dep, "eave_h": rw_eave},
        "courtyard": {"w": court_w, "d": court_d, "center": [court_cx, court_cy]},
        "main_stair_width_m": stair_w,
        "note": "Silhouette-priority footprint; mockup text 24x19 not used for overall complex",
    }
    return dims


def cameras():
    target = Vector((0.0, 0.0, 16.0))
    specs = {
        "CAM_01_FRONT": ((0.0, 85.0, 32.0), 38),
        "CAM_02_REAR": ((0.0, -85.0, 32.0), 38),
        "CAM_03_LEFT": ((-85.0, 2.0, 32.0), 38),
        "CAM_04_RIGHT": ((85.0, 2.0, 32.0), 38),
        "CAM_05_FRONT_3Q": ((55.0, 68.0, 36.0), 40),
        "CAM_06_REAR_3Q": ((-55.0, -68.0, 36.0), 40),
    }
    cams = []
    for name, (loc, lens) in specs.items():
        data = bpy.data.cameras.new(name)
        data.lens = lens
        data.clip_end = 600
        obj = bpy.data.objects.new(name, data)
        obj.location = loc
        direction = target - obj.location
        obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        bpy.context.scene.collection.objects.link(obj)
        cams.append(obj)
    return cams


def lights():
    bpy.ops.object.light_add(type="SUN", location=(30, -20, 60))
    sun = bpy.context.active_object
    sun.name = "SUN"
    sun.data.energy = 2.8
    sun.rotation_euler = Euler((math.radians(48), math.radians(12), math.radians(-25)), "XYZ")


def render_all(cams):
    RENDER.mkdir(parents=True, exist_ok=True)
    QUAR.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"):
        try:
            scene.render.engine = eng
            break
        except Exception:
            continue
    scene.render.image_settings.file_format = "PNG"
    paths = []
    import shutil

    for cam in cams:
        scene.camera = cam
        fp = RENDER / f"{cam.name}.png"
        scene.render.filepath = str(fp)
        bpy.ops.render.render(write_still=True)
        paths.append(str(fp))
        shutil.copy2(fp, QUAR / fp.name)
        log(f"render {fp.name}")
    return paths


def main():
    log("PASS 1D rebuild start")
    OUT.mkdir(parents=True, exist_ok=True)
    clear()
    units()
    dims = build()
    cams = cameras()
    lights()
    nmesh = len([o for o in bpy.data.objects if o.type == "MESH"])
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))
    paths = render_all(cams)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))

    masses = sorted([o.name for o in bpy.data.objects if o.type == "MESH"])
    report = {
        "pass": "PASS_1D_PRIMARY_MASSING_REBUILD",
        "asset_id": ASSET,
        "accepted": False,
        "self_accept": False,
        "dimensions": dims,
        "major_mass_count": nmesh,
        "major_masses": masses,
        "removed": "PASS1 narrow 24x19 layout discarded (backup PASS1_BACKUP.blend)",
        "blend": str(BLEND),
        "renders": paths,
        "six_view_match": {
            "front": "PENDING_VISUAL_REVIEW",
            "rear": "PENDING_VISUAL_REVIEW",
            "left": "PENDING_VISUAL_REVIEW",
            "right": "PENDING_VISUAL_REVIEW",
            "front_3q": "PENDING_VISUAL_REVIEW",
            "rear_3q": "PENDING_VISUAL_REVIEW",
        },
        "materials": "CLAY_ONLY",
        "no_windows_doors_ornament": True,
    }
    (OUT / "PASS1D_REPORT.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    log(f"meshes={nmesh} blend={BLEND}")
    log("PASS 1D done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
