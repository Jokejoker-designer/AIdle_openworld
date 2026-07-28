# -*- coding: utf-8 -*-
"""Author cast batch 001 — 9 Foundry characters (Nori already production).

Human WO-MOCKUP-CAST-PROPS-PRODUCTION-001: build mockup cast as real GLB+clips.
Blender 5.2 layered actions + NLA one-track-per-clip.
"""
from __future__ import annotations
import hashlib, json, math, shutil, sys
from pathlib import Path
import bpy
from mathutils import Vector, Euler

JOB = "BLD-CAST-BATCH-001"
FPS = 30
QUAR = Path(r"E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine\CAST_BATCH_001")
GAME_CAST = Path(r"E:\AIdle_openworld\game\assets\ucbv_001\cast")
QUAR.mkdir(parents=True, exist_ok=True)
GAME_CAST.mkdir(parents=True, exist_ok=True)

# bone layout shared (compatible with Nori robot set; creatures map mesh to same names)
BONES = [
    ("root", None, (0, 0, 0)),
    ("pelvis", "root", (0, 0, 0.18)),
    ("spine", "pelvis", (0, 0, 0.38)),
    ("chest", "spine", (0, 0, 0.62)),
    ("head", "chest", (0, 0, 0.95)),
    ("sprout_ctrl", "head", (0, 0, 1.18)),
    ("arm_L", "chest", (-0.28, 0, 0.72)),
    ("hand_L", "arm_L", (-0.42, 0.05, 0.52)),
    ("arm_R", "chest", (0.28, 0, 0.72)),
    ("hand_R", "arm_R", (0.42, 0.05, 0.52)),
    ("leg_L", "pelvis", (-0.10, 0, 0.10)),
    ("foot_L", "leg_L", (-0.10, 0.08, 0.02)),
    ("leg_R", "pelvis", (0.10, 0, 0.10)),
    ("foot_R", "leg_R", (0.10, 0.08, 0.02)),
]

CLIPS = [
    ("idle", 3.0, "idle"),
    ("walk", 0.8, "walk"),
    ("scan", 1.2, "scan"),
    ("happy", 1.0, "happy"),
    ("cancel", 0.6, "cancel"),
    ("turn_left", 0.5, "turn_l"),
    ("turn_right", 0.5, "turn_r"),
    ("build_place", 0.67, "build"),
    ("build_place_hold", 0.8, "hold"),
    ("confirm", 0.55, "confirm"),
]


def log(m):
    print(f"[CAST_BATCH] {m}")


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.armatures, bpy.data.actions):
        for b in list(coll):
            coll.remove(b)


def mat(name, rgba, rough=0.55, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = rough
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metal
    return m


def sphere(name, loc, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if o.data.materials:
        o.data.materials[0] = material
    else:
        o.data.materials.append(material)
    return o


def cyl(name, loc, r, depth, material, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=r, depth=depth, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.rotation_euler = Euler(rot)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    if o.data.materials:
        o.data.materials[0] = material
    else:
        o.data.materials.append(material)
    return o


def join(parts, name):
    bpy.ops.object.select_all(action="DESELECT")
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    o = bpy.context.active_object
    o.name = name
    return o


def armature():
    data = bpy.data.armatures.new("skel_cast_v1")
    obj = bpy.data.objects.new("CastArmature", data)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    created = {}
    for name, parent, head in BONES:
        b = data.edit_bones.new(name)
        hx, hy, hz = head
        b.head = Vector((hx, hy, hz))
        b.tail = Vector((hx, hy, hz + 0.08))
        if parent:
            b.parent = created[parent]
            b.use_connect = False
        created[name] = b
    bpy.ops.object.mode_set(mode="OBJECT")
    return obj


def count_fcurves(act):
    if act is None:
        return 0
    if hasattr(act, "fcurves") and act.fcurves is not None:
        try:
            return len(act.fcurves)
        except Exception:
            pass
    n = 0
    try:
        for layer in act.layers:
            for strip in layer.strips:
                if hasattr(strip, "channelbags"):
                    for bag in strip.channelbags:
                        if hasattr(bag, "fcurves"):
                            n += len(bag.fcurves)
    except Exception:
        pass
    return n


def key(pb, frame, loc=None, euler=None):
    if pb is None:
        return
    if loc is not None:
        pb.location = Vector(loc)
        pb.keyframe_insert("location", frame=frame)
    if euler is not None:
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = Euler(euler)
        pb.keyframe_insert("rotation_euler", frame=frame)


def author_clips(arm):
    arm.animation_data_create()
    report = {}
    for clip_name, dur, kind in CLIPS:
        act = bpy.data.actions.new(clip_name)
        arm.animation_data.action = act
        n = max(2, int(round(dur * FPS)))
        pelvis = arm.pose.bones.get("pelvis")
        head = arm.pose.bones.get("head")
        arm_l = arm.pose.bones.get("arm_L")
        arm_r = arm.pose.bones.get("arm_R")
        leg_l = arm.pose.bones.get("leg_L")
        leg_r = arm.pose.bones.get("leg_R")
        sprout = arm.pose.bones.get("sprout_ctrl")
        if kind == "idle":
            for f, y in ((1, 0.0), (n // 2, -0.012), (n, 0.0)):
                key(pelvis, f, loc=(0, 0, y))
                key(sprout, f, euler=(0, 0, 0.03 if f == n // 2 else 0))
        elif kind == "walk":
            for f in (1, n // 4, n // 2, 3 * n // 4, n):
                t = (f - 1) / max(1, n - 1)
                ph = math.sin(t * math.pi * 2)
                key(leg_l, f, euler=(ph * 0.28, 0, 0))
                key(leg_r, f, euler=(-ph * 0.28, 0, 0))
                key(arm_l, f, euler=(-ph * 0.15, 0, 0.1))
                key(arm_r, f, euler=(ph * 0.15, 0, -0.1))
                key(pelvis, f, loc=(0, 0, abs(ph) * 0.01))
        elif kind == "scan":
            key(head, 1, euler=(0, 0, 0))
            key(head, n // 3, euler=(0, 0.25, 0.1))
            key(head, 2 * n // 3, euler=(0, -0.25, -0.1))
            key(head, n, euler=(0, 0, 0))
        elif kind == "happy":
            key(arm_l, n // 2, euler=(-0.5, 0, 0.3))
            key(arm_r, n // 2, euler=(-0.5, 0, -0.3))
            key(arm_l, n, euler=(0, 0, 0))
            key(arm_r, n, euler=(0, 0, 0))
            key(sprout, n // 2, euler=(0.2, 0, 0.2))
            key(sprout, n, euler=(0, 0, 0))
        elif kind == "cancel":
            key(head, n // 2, euler=(0.2, 0, 0))
            key(head, n, euler=(0, 0, 0))
        elif kind == "turn_l":
            key(pelvis, n // 2, euler=(0, 0, 0.5))
            key(pelvis, n, euler=(0, 0, 0))
        elif kind == "turn_r":
            key(pelvis, n // 2, euler=(0, 0, -0.5))
            key(pelvis, n, euler=(0, 0, 0))
        elif kind in ("build", "hold"):
            key(arm_r, 1, euler=(-0.5 if kind == "hold" else 0, 0, -0.1))
            key(arm_r, n // 2, euler=(-0.9, 0, -0.15))
            key(arm_r, n, euler=(-0.5 if kind == "hold" else 0, 0, -0.1))
        elif kind == "confirm":
            key(arm_r, n // 3, euler=(-1.0, 0, -0.1))
            key(arm_r, n, euler=(0, 0, 0))
        fc = count_fcurves(act)
        report[clip_name] = {"duration_s": dur, "fcurve_count": fc, "real_keys": fc > 0}
        track = arm.animation_data.nla_tracks.new()
        track.name = clip_name
        try:
            track.strips.new(clip_name, 1, act)
        except Exception as e:
            log(f"nla warn {clip_name}: {e}")
    if bpy.data.actions.get("idle"):
        arm.animation_data.action = bpy.data.actions["idle"]
    return report


# ---- character mesh builders (distinct silhouettes) ----

def body_robot_helper(parts, mats, accent=(0.5, 0.79, 0.56, 1)):
    cream, shade, leaf, glass, metal = mats["cream"], mats["shade"], mats["leaf"], mats["glass"], mats["metal"]
    # override leaf with accent for variants
    parts += [
        sphere("body", (0, 0.02, 0.4), (0.28, 0.26, 0.28), cream),
        sphere("head", (0, 0.04, 0.78), (0.26, 0.24, 0.26), shade),
        sphere("eyeL", (-0.08, 0.22, 0.82), (0.05, 0.03, 0.05), glass),
        sphere("eyeR", (0.08, 0.22, 0.82), (0.05, 0.03, 0.05), glass),
        cyl("armL", (-0.28, 0, 0.6), 0.04, 0.2, cream, (0, 0, 0.3)),
        cyl("armR", (0.28, 0, 0.6), 0.04, 0.2, cream, (0, 0, -0.3)),
        sphere("handL", (-0.4, 0.04, 0.48), (0.05, 0.05, 0.05), leaf),
        sphere("handR", (0.4, 0.04, 0.48), (0.05, 0.05, 0.05), leaf),
        cyl("legL", (-0.09, 0, 0.12), 0.045, 0.16, cream),
        cyl("legR", (0.09, 0, 0.12), 0.045, 0.16, cream),
        sphere("footL", (-0.09, 0.05, 0.03), (0.06, 0.08, 0.035), metal),
        sphere("footR", (0.09, 0.05, 0.03), (0.06, 0.08, 0.035), metal),
        sphere("sprout", (0, 0, 1.1), (0.07, 0.05, 0.05), leaf),
    ]
    return parts


def body_humanoid(parts, mats, stocky=False):
    cream, shade, wood, leaf = mats["cream"], mats["shade"], mats["wood"], mats["leaf"]
    s = 1.15 if stocky else 1.0
    parts += [
        sphere("torso", (0, 0.02, 0.55 * s), (0.22 * s, 0.16 * s, 0.28 * s), cream),
        sphere("head", (0, 0.05, 0.95 * s), (0.16, 0.15, 0.16), shade),
        sphere("hairL", (-0.1, -0.02, 1.05 * s), (0.08, 0.08, 0.08), wood),
        sphere("hairR", (0.1, -0.02, 1.05 * s), (0.08, 0.08, 0.08), wood),
        cyl("armL", (-0.26 * s, 0, 0.6 * s), 0.035, 0.22, cream, (0, 0, 0.25)),
        cyl("armR", (0.26 * s, 0, 0.6 * s), 0.035, 0.22, cream, (0, 0, -0.25)),
        sphere("handL", (-0.36 * s, 0.04, 0.46 * s), (0.04, 0.04, 0.04), leaf),
        sphere("handR", (0.36 * s, 0.04, 0.46 * s), (0.04, 0.04, 0.04), leaf),
        cyl("legL", (-0.08, 0, 0.18), 0.04, 0.22, shade),
        cyl("legR", (0.08, 0, 0.18), 0.04, 0.22, shade),
        sphere("footL", (-0.08, 0.06, 0.03), (0.06, 0.09, 0.03), wood),
        sphere("footR", (0.08, 0.06, 0.03), (0.06, 0.09, 0.03), wood),
    ]
    return parts


def body_quad(parts, mats, leaves=True):
    cream, shade, leaf, wood = mats["cream"], mats["shade"], mats["leaf"], mats["wood"]
    parts += [
        sphere("body", (0, 0.05, 0.28), (0.28, 0.2, 0.2), cream),
        sphere("head", (0, 0.22, 0.32), (0.14, 0.12, 0.12), shade),
        sphere("earL", (-0.08, 0.22, 0.42), (0.04, 0.03, 0.05), leaf),
        sphere("earR", (0.08, 0.22, 0.42), (0.04, 0.03, 0.05), leaf),
        cyl("legFL", (-0.12, 0.1, 0.1), 0.03, 0.14, wood),
        cyl("legFR", (0.12, 0.1, 0.1), 0.03, 0.14, wood),
        cyl("legBL", (-0.12, -0.08, 0.1), 0.03, 0.14, wood),
        cyl("legBR", (0.12, -0.08, 0.1), 0.03, 0.14, wood),
        sphere("tail", (0, -0.22, 0.3), (0.05, 0.12, 0.05), wood),
    ]
    if leaves:
        parts += [
            sphere("leaf1", (-0.05, 0, 0.48), (0.08, 0.04, 0.03), leaf),
            sphere("leaf2", (0.05, 0, 0.5), (0.07, 0.04, 0.03), leaf),
            sphere("leaf3", (0, -0.02, 0.52), (0.06, 0.03, 0.03), leaf),
        ]
    return parts


def body_construct(parts, mats):
    cream, metal, wood, glass = mats["cream"], mats["metal"], mats["wood"], mats["glass"]
    parts += [
        sphere("core", (0, 0, 0.5), (0.24, 0.2, 0.28), metal),
        sphere("head", (0, 0.02, 0.9), (0.18, 0.16, 0.16), cream),
        sphere("ember", (0, 0.16, 0.55), (0.08, 0.04, 0.08), glass),
        cyl("armL", (-0.3, 0, 0.55), 0.05, 0.24, metal, (0, 0, 0.2)),
        cyl("armR", (0.3, 0, 0.55), 0.05, 0.24, metal, (0, 0, -0.2)),
        cyl("legL", (-0.1, 0, 0.16), 0.06, 0.2, wood),
        cyl("legR", (0.1, 0, 0.16), 0.06, 0.2, wood),
    ]
    return parts


CHARACTERS = [
    # Nori skipped — already in game
    {"id": "CCP-NS-002", "slug": "may_mach", "form": "humanoid", "stocky": False,
     "colors": {"cream": (0.99, 0.92, 0.55, 1), "shade": (0.95, 0.85, 0.45, 1), "leaf": (0.5, 0.79, 0.56, 1), "wood": (0.45, 0.65, 0.8, 1), "glass": (0.66, 0.86, 0.93, 1), "metal": (0.7, 0.72, 0.74, 1)}},
    {"id": "CCP-NW-003", "slug": "bac_bap", "form": "humanoid", "stocky": True,
     "colors": {"cream": (0.9, 0.55, 0.35, 1), "shade": (0.55, 0.5, 0.35, 1), "leaf": (0.45, 0.55, 0.3, 1), "wood": (0.55, 0.4, 0.25, 1), "glass": (0.7, 0.8, 0.85, 1), "metal": (0.6, 0.62, 0.65, 1)}},
    {"id": "CCP-CT-004", "slug": "bui_mo", "form": "quad", "leaves": True,
     "colors": {"cream": (0.99, 0.95, 0.88, 1), "shade": (0.94, 0.88, 0.78, 1), "leaf": (0.5, 0.79, 0.56, 1), "wood": (0.55, 0.4, 0.28, 1), "glass": (0.3, 0.25, 0.2, 1), "metal": (0.5, 0.5, 0.5, 1)}},
    {"id": "SPH-RH-011", "slug": "kito", "form": "robot",
     "colors": {"cream": (0.99, 0.95, 0.88, 1), "shade": (0.94, 0.88, 0.78, 1), "leaf": (0.55, 0.85, 0.45, 1), "wood": (0.85, 0.75, 0.35, 1), "glass": (0.66, 0.9, 0.5, 1), "metal": (0.75, 0.78, 0.5, 1)}},
    {"id": "OA-RG-021", "slug": "nereu", "form": "robot",
     "colors": {"cream": (0.85, 0.93, 0.95, 1), "shade": (0.55, 0.75, 0.85, 1), "leaf": (0.3, 0.7, 0.75, 1), "wood": (0.4, 0.55, 0.6, 1), "glass": (0.4, 0.85, 0.95, 1), "metal": (0.55, 0.65, 0.7, 1)}},
    {"id": "AC-CO-015", "slug": "cinder", "form": "construct",
     "colors": {"cream": (0.85, 0.75, 0.55, 1), "shade": (0.65, 0.5, 0.35, 1), "leaf": (0.9, 0.45, 0.2, 1), "wood": (0.45, 0.3, 0.2, 1), "glass": (1.0, 0.55, 0.25, 1), "metal": (0.7, 0.55, 0.35, 1)}},
    {"id": "TD-CT-028", "slug": "patch", "form": "quad", "leaves": False,
     "colors": {"cream": (0.92, 0.78, 0.62, 1), "shade": (0.75, 0.55, 0.4, 1), "leaf": (0.55, 0.7, 0.45, 1), "wood": (0.55, 0.4, 0.3, 1), "glass": (0.2, 0.2, 0.25, 1), "metal": (0.5, 0.5, 0.55, 1)}},
    {"id": "SV-NW-019", "slug": "truc_nhi", "form": "humanoid", "stocky": False,
     "colors": {"cream": (0.95, 0.92, 0.85, 1), "shade": (0.75, 0.85, 0.7, 1), "leaf": (0.45, 0.7, 0.4, 1), "wood": (0.55, 0.45, 0.3, 1), "glass": (0.6, 0.8, 0.7, 1), "metal": (0.6, 0.6, 0.55, 1)}},
    {"id": "SPH-NG-009", "slug": "luma", "form": "humanoid", "stocky": False,
     "colors": {"cream": (0.99, 0.95, 0.85, 1), "shade": (0.95, 0.85, 0.5, 1), "leaf": (0.45, 0.75, 0.45, 1), "wood": (0.85, 0.7, 0.3, 1), "glass": (0.7, 0.9, 0.95, 1), "metal": (0.8, 0.75, 0.4, 1)}},
]


def build_one(spec):
    clear()
    bpy.context.scene.render.fps = FPS
    cols = spec["colors"]
    mats = {
        "cream": mat("MAT_Body", cols["cream"]),
        "shade": mat("MAT_Shade", cols["shade"]),
        "leaf": mat("MAT_Leaf", cols["leaf"]),
        "wood": mat("MAT_Wood", cols["wood"]),
        "glass": mat("MAT_Glass", cols["glass"], 0.25, 0.05),
        "metal": mat("MAT_Metal", cols["metal"], 0.35, 0.5),
    }
    parts = []
    form = spec["form"]
    if form == "robot":
        parts = body_robot_helper(parts, mats)
    elif form == "humanoid":
        parts = body_humanoid(parts, mats, stocky=bool(spec.get("stocky")))
    elif form == "quad":
        parts = body_quad(parts, mats, leaves=bool(spec.get("leaves", True)))
    elif form == "construct":
        parts = body_construct(parts, mats)
    mesh = join(parts, f"{spec['slug']}_Mesh")
    arm = armature()
    mesh.select_set(True)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    mesh.parent = arm
    root = bpy.data.objects.new(spec["id"], None)
    bpy.context.collection.objects.link(root)
    arm.parent = root
    clip_report = author_clips(arm)

    out_dir = GAME_CAST / spec["slug"] / "export"
    out_dir.mkdir(parents=True, exist_ok=True)
    glb = out_dir / f"{spec['slug']}_rigged.glb"
    blend = out_dir / f"{spec['slug']}_rigged.blend"
    qdir = QUAR / spec["slug"]
    qdir.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(qdir / f"{spec['slug']}_rigged.blend"))
    bpy.ops.export_scene.gltf(
        filepath=str(glb),
        export_format="GLB",
        use_selection=False,
        export_animations=True,
        export_skins=True,
        export_yup=True,
    )
    shutil.copy2(glb, qdir / glb.name)
    if Path(qdir / f"{spec['slug']}_rigged.blend").exists():
        shutil.copy2(qdir / f"{spec['slug']}_rigged.blend", blend)

    glb_hash = sha(glb)
    meta = {
        "character_id": spec["id"],
        "slug": spec["slug"],
        "form": form,
        "glb": str(glb).replace("\\", "/"),
        "glb_sha256": glb_hash,
        "glb_bytes": glb.stat().st_size,
        "clips": clip_report,
        "bones": 14,
        "job_id": JOB,
        "accepted": False,
        "self_accept": False,
    }
    (out_dir / "validation.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (qdir / "validation.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    log(f"OK {spec['id']} {spec['slug']} sha={glb_hash[:12]}… clips={len(clip_report)}")
    return meta


def main():
    results = []
    for spec in CHARACTERS:
        try:
            results.append(build_one(spec))
        except Exception as e:
            log(f"FAIL {spec['id']}: {e}")
            import traceback
            traceback.print_exc()
            results.append({"character_id": spec["id"], "error": str(e), "ok": False})
    # Nori pointer
    nori = Path(r"E:\AIdle_openworld\game\assets\ucbv_001\character\nori7\export\nori7_rigged.glb")
    nori_meta = {
        "character_id": "CCP-RH-001",
        "slug": "nori7",
        "form": "robot",
        "glb": "game/assets/ucbv_001/character/nori7/export/nori7_rigged.glb",
        "glb_sha256": sha(nori) if nori.exists() else "",
        "existing_production": True,
        "job_id": "NORI7_EXISTING",
    }
    results.insert(0, nori_meta)
    summary = {"job_id": JOB, "count": len(results), "characters": results, "accepted": False, "self_accept": False}
    (QUAR / "cast_batch_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (GAME_CAST / "cast_batch_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    log(f"DONE authored={len([r for r in results if r.get('glb_sha256')])}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        log(f"FATAL {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
