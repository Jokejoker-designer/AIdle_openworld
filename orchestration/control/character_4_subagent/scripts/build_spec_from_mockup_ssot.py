# -*- coding: utf-8 -*-
"""Build character_spec.json from MOCKUP_SSOT_V2 + Object DNA / Nori contracts.

Does not invent mockup pixels. Paths are absolute AIdle paths.
accepted=false, self_accept=false.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

BRIDGE = Path(__file__).resolve().parents[1] / "aidle_bridge.json"


def load_bridge() -> dict:
    return json.loads(BRIDGE.read_text(encoding="utf-8"))


def find_character(ssot: dict, character_id: str) -> dict:
    for c in ssot.get("characters", []):
        if c.get("id") == character_id or c.get("slug") == character_id:
            return c
    raise SystemExit(f"character not found in MOCKUP_SSOT: {character_id}")


def load_nori_bones(bridge: dict) -> dict:
    path = Path(bridge["paths"]["nori7_hierarchy"])
    if not path.exists():
        return {"bone_count": None, "bones": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    names = [b["name"] for b in data.get("bones", [])]
    return {
        "bone_count": data.get("bone_count_production"),
        "skeleton_id": data.get("skeleton_id"),
        "bones": names,
        "hierarchy_ref": str(path),
    }


def load_adapter_clips(bridge: dict) -> list:
    path = Path(bridge["paths"]["nori7_adapter"])
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data.get("required_actions_all") or [])


def build_spec(character_id: str) -> dict:
    bridge = load_bridge()
    ssot_path = Path(bridge["paths"]["mockup_ssot_json"])
    chars_dir = Path(bridge["paths"]["mockup_chars_dir"])
    ssot = json.loads(ssot_path.read_text(encoding="utf-8"))
    ch = find_character(ssot, character_id)

    img_rel = ch.get("img") or ""
    img_abs = str((chars_dir.parent / img_rel).resolve()) if img_rel else ""
    concept = chars_dir / img_rel.replace(".jpg", "_concept.jpg").split("/")[-1]
    refs = [img_abs]
    if concept.exists():
        refs.append(str(concept.resolve()))

    # Clips: prefer production adapter for Nori; else SSOT list
    clips = ch.get("clips") or []
    if ch.get("id") == "CCP-RH-001":
        adapter_clips = load_adapter_clips(bridge)
        if adapter_clips:
            clips = adapter_clips

    bones = load_nori_bones(bridge) if ch.get("id") == "CCP-RH-001" else {}

    skeleton_family = "robot_biped_small_v1" if ch.get("form") == "robot" else "humanoid_standard_v1"
    if ch.get("id") == "CCP-RH-001":
        skeleton_family = "robot_biped_small_v1"
        skeleton_alias = "skel_small_biped_robot_v1"
    else:
        skeleton_alias = None

    # Robot Nori: S1 owns face display / sprout; S2 owns body tank limbs
    if ch.get("form") == "robot":
        part_ownership = {
            "S1": ["head", "face_socket", "eyes", "sprout", "face_details"],
            "S2": ["torso", "arms", "hands", "legs", "feet", "water_tank", "nozzle", "body_accessories"],
            "S3": ["retopo", "uv", "materials", "armature", "weights", "animations", "export"],
            "S4": ["read_only_visual_qa", "technical_qa", "change_requests"],
        }
        forbidden = [
            "white golf-ball single sphere body",
            "cyan body fill (cyan eye ring only)",
            "missing mechanical sprout rear identifier",
            "placeholder capsule limbs without tank/nozzle readability",
            "material or lighting used to hide form errors",
            "alias missing clip to idle",
            "self_accept",
        ]
        proportions = {
            "character_heads_tall": 2.0,
            "body_height_m": 1.2,
            "form": "cream_teardrop_robot",
            "signature": ch.get("signature"),
        }
        palette = {
            "dominant_families_max": 3,
            "swatches": [
                {"token": "cream", "hex": "#fdf3e2"},
                {"token": "leaf", "hex": "#7fc98f"},
                {"token": "iris_cyan_eye_only", "hex": "#a8dced"},
            ],
            "forbidden_primary_colors": ["full_body_cyan"],
            "emission_allowed": False,
        }
        technical_budget = {
            "triangle_max": 12000,
            "bone_max": 14,
            "texture_max_px": 1024,
            "mobile_target": True,
            "production_bones": bones.get("bones") or [],
            "skeleton_id": bones.get("skeleton_id") or skeleton_alias,
        }
    else:
        part_ownership = {
            "S1": ["head", "ears", "eyes", "hair_clouds", "bangs", "face_details"],
            "S2": ["torso", "inner_cloth", "outer_cloth", "arms", "hands", "legs", "boots", "body_accessories"],
            "S3": ["retopo", "uv", "materials", "armature", "weights", "animations", "export"],
            "S4": ["read_only_visual_qa", "technical_qa", "change_requests"],
        }
        forbidden = [
            "near-identical sphere hair clouds",
            "bead-chain bangs",
            "placeholder sphere hands",
            "placeholder capsule boots",
            "material or lighting used to hide form errors",
            "alias missing clip to idle",
            "self_accept",
        ]
        proportions = {
            "character_heads_tall": 2.5,
            "form": ch.get("form"),
            "signature": ch.get("signature"),
        }
        palette = {
            "dominant_families_max": 3,
            "swatches": [],
            "forbidden_primary_colors": ["cyan_as_body"],
            "emission_allowed": False,
        }
        technical_budget = {
            "triangle_max": 15000,
            "bone_max": 42,
            "texture_max_px": 1024,
            "mobile_target": True,
        }

    spec = {
        "spec_version": "1.0.0",
        "character_id": ch["id"],
        "display_name": ch.get("name") or ch.get("slug"),
        "class": ch.get("class"),
        "slug": ch.get("slug"),
        "mockup_ssot": {
            "id": "MOCKUP_SSOT_V2",
            "catalog_path": str(ssot_path),
            "reference_images": refs,
            "mockup_img_rel": img_rel,
            "video": ch.get("video"),
            "approved_delta_work_order": None,
        },
        "target": {
            "match_mode": "CAMERA_LOCKED_MATCH",
            "style": "Cozy Cyber-Pixel / Dreamy Low-Poly 2.5D",
            "camera_priority": "PRIMARY_3Q_ISOMETRIC",
            "world_profile": ch.get("world") or "cozy_cyber_pixel",
            "notes": [
                "Clay proof first; no material pass until FORM_LOCKED",
                "Primary camera similarity is the main visual gate",
                "Vision lock §12: mockup fidelity law — in-game must match mockup 100% when shipped",
                "Do not claim 3D geometry fidelity for unseen angles",
            ],
        },
        "camera_lock": {
            "primary": {
                "projection": "PERSPECTIVE",
                "resolution": [1024, 1024],
                "transform": {
                    "location": [2.2, -2.8, 1.6],
                    "rotation_euler_deg": [62.0, 0.0, 38.0],
                    "fov_deg": 40.0,
                    "look_at": [0.0, 0.0, 0.7],
                },
            },
            "secondary_views": ["FRONT", "LEFT", "BACK", "TURN_45_RIGHT"],
        },
        "proportions": proportions,
        "landmarks": [
            {"id": "ground", "hint": "feet contact"},
            {"id": "head_top", "hint": "sprout tip or hair crown"},
            {"id": "face_center", "hint": "eye cluster center"},
        ],
        "palette": palette,
        "part_ownership": part_ownership,
        "skeleton_family": skeleton_family,
        "skeleton_alias": skeleton_alias,
        "object_dna_family_ref": "orchestration/control/object_dna_card_system/registries/skeleton_family_categories_v1.json",
        "clips": clips,
        "technical_budget": technical_budget,
        "gates": {
            "silhouette_iou_min": 0.94,
            "landmark_rmse_max": 0.018,
            "bbox_delta_max": 0.02,
            "palette_delta_e00_max": 6.0,
            "require_rear_identifier": True,
        },
        "forbidden_patterns": forbidden,
        "production_binding": {
            "existing_glb": bridge["paths"]["nori7_glb"] if ch.get("id") == "CCP-RH-001" else None,
            "adapter": bridge["paths"]["nori7_adapter"] if ch.get("id") == "CCP-RH-001" else None,
            "quarantine_root": bridge["paths"]["quarantine_root"],
            "promote_to_game_requires_human": True,
        },
        "four_subagent_system": {
            "upstream": bridge["upstream_root"],
            "state_machine": "workflow/state_machine.json",
            "collection_contract": "blender/BLENDER_COLLECTION_CONTRACT.md",
        },
        "human_acceptance_required": True,
        "accepted": False,
        "self_accept": False,
    }
    return spec


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--character-id", default="CCP-RH-001")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    spec = build_spec(args.character_id)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(args.out), "character_id": spec["character_id"], "clips": len(spec["clips"]), "accepted": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
