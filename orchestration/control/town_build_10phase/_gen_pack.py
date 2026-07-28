# -*- coding: utf-8 -*-
"""Generate town_build_10phase package: subagents, 10 phases, town layout, contracts."""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MOCK = json.loads(
    Path(
        r"E:\AIdle_openworld\orchestration\control\visual_reference\mockup_ssot_v2\MOCKUP_SSOT_V2.json"
    ).read_text(encoding="utf-8")
)
GAME = Path(r"E:\AIdle_openworld\game")

char_by_id = {c["id"]: c for c in MOCK["characters"]}
bld_by_id = {b["id"]: b for b in MOCK["buildings"]}
prop_by_id = {p["id"]: p for p in MOCK["props"]}

# 10 phases: 1 cast + 1 building + 3 props — town-function order (not dump order)
PHASES_PLAN = [
    (1, "home_plot", "CCP-RH-001", "cozy_house_small_A",
     ["cozy_path_stone_A", "cozy_garden_lamp_A", "cozy_mailbox_A"], "Nơi ở + lối vào"),
    (2, "market_square", "CCP-NS-002", "cozy_market_stall_A",
     ["cozy_bench_A", "cozy_cart_A", "cozy_signpost_A"], "Quảng trường chợ"),
    (3, "workshop_row", "CCP-NW-003", "cozy_workshop_A",
     ["cozy_tool_rack_A", "cozy_crate_small_A", "cozy_barrel_A"], "Xưởng sửa chữa"),
    (4, "creature_garden", "CCP-CT-004", "cozy_gazebo_A",
     ["cozy_flower_cluster_A", "cozy_flower_bed_B", "cozy_bush_round_A"], "Vườn thư giãn"),
    (5, "pollinator_farm", "SPH-RH-011", "cozy_greenhouse_A",
     ["cozy_farm_plot_A", "cozy_crop_row_A", "cozy_scarecrow_A"], "Nông trại kính"),
    (6, "water_edge", "OA-RG-021", "cozy_well_house_A",
     ["cozy_pond_small_A", "cozy_water_pump_A", "cozy_birdbath_A"], "Khu nước"),
    (7, "craft_landmark", "AC-CO-015", "cozy_windmill_A",
     ["cozy_fence_section_A", "cozy_grass_tuft_A", "cozy_rock_cluster_A"], "Cối xay + rìa"),
    (8, "barn_yard", "TD-CT-028", "cozy_barn_small_A",
     ["cozy_tree_fruit_A", "cozy_rock_small_A", "cozy_rock_stacked_A"], "Sân kho"),
    (9, "spirit_bridge", "SV-NW-019", "cozy_bridge_arch_A",
     ["cozy_tree_willow_A", "cozy_tree_blossom_A", "cozy_rock_mossy_A"], "Cầu + đường tinh"),
    (10, "canopy_lookout", "SPH-NG-009", "cozy_watchtower_A",
     ["cozy_tree_landmark_A", "cozy_tree_pine_A", "cozy_tree_cluster_A"], "Tháp + tán cây"),
]

# Town world positions (meters). Plaza center (0,0). Readable for fixed 2.5D camera.
# Min building spacing ~6m; props orbit building; characters offset for silhouette.
LAYOUT = {
    1: {"building": (0, 0, 0), "character": (1.6, 0, 1.4),
        "props": [(-1.4, 0, 1.6), (1.2, 0, -1.1), (0.9, 0, 1.8)], "facing_deg": -35},
    2: {"building": (9, 0, 0), "character": (7.8, 0, 1.6),
        "props": [(7.2, 0, -1.4), (10.4, 0, 1.2), (9.0, 0, -2.2)], "facing_deg": 0},
    3: {"building": (9, 0, 9), "character": (7.4, 0, 9.2),
        "props": [(10.6, 0, 7.8), (11.0, 0, 9.8), (7.6, 0, 10.6)], "facing_deg": -90},
    4: {"building": (0, 0, 11), "character": (1.7, 0, 9.8),
        "props": [(-1.7, 0, 9.8), (1.4, 0, 12.4), (-0.6, 0, 12.6)], "facing_deg": 180},
    5: {"building": (-9, 0, 9), "character": (-7.4, 0, 8.2),
        "props": [(-10.6, 0, 7.6), (-11.0, 0, 10.0), (-7.6, 0, 10.8)], "facing_deg": 90},
    6: {"building": (-11, 0, 0), "character": (-9.2, 0, 1.2),
        "props": [(-12.6, 0, 1.6), (-9.8, 0, -1.6), (-12.0, 0, -1.2)], "facing_deg": 45},
    7: {"building": (-9, 0, -9), "character": (-7.2, 0, -7.8),
        "props": [(-10.6, 0, -7.2), (-7.6, 0, -10.6), (-10.8, 0, -10.0)], "facing_deg": 135},
    8: {"building": (0, 0, -11), "character": (1.4, 0, -9.4),
        "props": [(-1.7, 0, -9.8), (1.6, 0, -12.4), (-0.9, 0, -12.6)], "facing_deg": 0},
    9: {"building": (9, 0, -9), "character": (7.6, 0, -7.4),
        "props": [(10.6, 0, -7.6), (11.0, 0, -10.0), (7.4, 0, -10.4)], "facing_deg": -45},
    10: {"building": (13.5, 0, 4.5), "character": (12.0, 0, 5.6),
         "props": [(13.5, 0, 2.6), (15.0, 0, 4.8), (15.2, 0, 2.8)], "facing_deg": -20},
}


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.lstrip("\n") if content.startswith("\n") else content, encoding="utf-8")
    if not content.endswith("\n"):
        path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")


def build_phases() -> list:
    phases = []
    for ph, district, cid, bid, pids, role in PHASES_PLAN:
        c = char_by_id[cid]
        b = bld_by_id[bid]
        ps = [prop_by_id[pid] for pid in pids]
        coords = LAYOUT[ph]
        clips = list(c["clips"])
        phases.append(
            {
                "phase": ph,
                "phase_id": f"TOWN_PHASE_{ph:02d}",
                "district_id": district,
                "district_role_vi": role,
                "status": "READY" if ph == 1 else "BLOCKED_UNTIL_PREV_PARITY_100",
                "mockup_ssot": "MOCKUP_SSOT_V2",
                "parity_gate": "MOCKUP_PARITY_100",
                "character": {
                    "character_id": c["id"],
                    "slug": c["slug"],
                    "name": c["name"],
                    "class": c["class"],
                    "form": c["form"],
                    "clips": clips,
                    "motion": c["motion"],
                    "signature": c["signature"],
                    "mockup_img": "orchestration/control/visual_reference/mockup_ssot_v2/" + c["img"],
                    "mockup_video": (
                        "orchestration/control/visual_reference/mockup_ssot_v2/" + c["video"]
                        if c.get("video")
                        else None
                    ),
                    "prod_hint": c.get("prod"),
                    "spawn": {
                        "x": coords["character"][0],
                        "y": coords["character"][1],
                        "z": coords["character"][2],
                        "rotation_deg": coords["facing_deg"],
                    },
                },
                "building": {
                    "module_id": b["id"],
                    "name": b["name"],
                    "cat": b["cat"],
                    "anim": b["anim"],
                    "mockup_img": (
                        "orchestration/control/visual_reference/mockup_ssot_v2/" + b["img"]
                        if b.get("img")
                        else None
                    ),
                    "spawn": {
                        "x": coords["building"][0],
                        "y": coords["building"][1],
                        "z": coords["building"][2],
                        "rotation_deg": coords["facing_deg"],
                    },
                },
                "props": [
                    {
                        "module_id": p["id"],
                        "name": p["name"],
                        "cat": p["cat"],
                        "anim": p["anim"],
                        "mockup_img": (
                            "orchestration/control/visual_reference/mockup_ssot_v2/" + p["img"]
                            if p.get("img")
                            else None
                        ),
                        "spawn": {
                            "x": coords["props"][i][0],
                            "y": coords["props"][i][1],
                            "z": coords["props"][i][2],
                            "rotation_deg": coords["facing_deg"] + (i - 1) * 12,
                        },
                    }
                    for i, p in enumerate(ps)
                ],
                "acceptance": {
                    "rule": "Do NOT mark complete until MOCKUP_PARITY_100 passes for this phase",
                    "mockup_delta_max": 0.0,
                    "require_idle_play": True,
                    "require_clips": clips if c["id"] == "CCP-RH-001" else ["idle", "walk", "scan", "happy", "cancel"],
                    "require_building_load": True,
                    "require_props_load": 3,
                    "require_town_no_overlap": True,
                    "require_district_role_readable": True,
                    "self_accept": False,
                    "human_accept_required": True,
                },
                "subagent_pipeline": [
                    "town-orchestrator",
                    "mockup-parity-guardian",
                    "character-animation-designer",
                    "building-module-designer",
                    "prop-set-designer",
                    "town-layout-planner",
                    "godot-runtime-integrator",
                    "red-mockup-delta-reviewer",
                    "purple-parity-gate",
                ],
            }
        )
    used_p = [p["module_id"] for ph in phases for p in ph["props"]]
    assert len(used_p) == 30 and len(set(used_p)) == 30, set(prop_by_id) - set(used_p)
    assert len({ph["building"]["module_id"] for ph in phases}) == 10
    assert len({ph["character"]["character_id"] for ph in phases}) == 10
    return phases


def main() -> None:
    phases = build_phases()
    for d in [
        ROOT / "agents",
        ROOT / "contracts",
        ROOT / "workflow",
        ROOT / "phases",
        ROOT / "town",
        ROOT / "receipts",
    ]:
        d.mkdir(parents=True, exist_ok=True)

    town = {
        "schema_version": "1.0.0",
        "town_id": "COZY_STARTER_TOWN_10PHASE",
        "mockup_ssot": "MOCKUP_SSOT_V2",
        "design_lock": "orchestration/control/visual_reference/mockup_ssot_v2/MOCKUP_DESIGN_LOCK.md",
        "world_profile": "cozy_cyber_pixel",
        "camera": "fixed_three_quarter",
        "units": "meters",
        "origin": {"note": "plaza center = home_plot building origin", "x": 0, "y": 0, "z": 0},
        "layout_rules": [
            "Districts form a ring around home_plot — not a random dump",
            "Market east of home; farm west/south-west; water further west; craft SW; barn south; bridge SE; lookout NE",
            "Min 6m between building centers",
            "Character always readable in 2.5D — offset in front of building",
            "Props support district function (lamp/path at home, cart/bench at market, tools at workshop…)",
            "No cyan as body/building fill",
            "No overlapping AABBs (require_town_no_overlap)",
        ],
        "paths": [
            {"id": "main_loop", "waypoints": [[0, 0], [9, 0], [9, 9], [0, 11], [-9, 9], [-11, 0], [-9, -9], [0, -11], [9, -9], [0, 0]]},
            {"id": "farm_spur", "waypoints": [[-9, 9], [-11, 0]]},
            {"id": "lookout_spur", "waypoints": [[9, 0], [13.5, 4.5]]},
        ],
        "phases": phases,
        "counts": {"phases": 10, "characters": 10, "buildings": 10, "props": 30},
        "accepted": False,
        "self_accept": False,
        "status": "SYSTEM_ACTIVE_PHASE1_READY",
    }
    (ROOT / "town" / "TOWN_LAYOUT_10PHASE.json").write_text(
        json.dumps(town, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (ROOT / "phases" / "ALL_PHASES.json").write_text(
        json.dumps({"phases": phases}, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    for ph in phases:
        n = ph["phase"]
        md = f"""# {ph['phase_id']} — {ph['district_id']}

**Status:** `{ph['status']}`  
**District role:** {ph['district_role_vi']}  
**Parity gate:** `MOCKUP_PARITY_100` — **không được dừng** khi còn lệch mockup.

## Bindings (SSOT mockup — exact IDs)

| Slot | ID | Name |
|------|-----|------|
| Character | `{ph['character']['character_id']}` | {ph['character']['name']} |
| Building | `{ph['building']['module_id']}` | {ph['building']['name']} |
| Prop 1 | `{ph['props'][0]['module_id']}` | {ph['props'][0]['name']} |
| Prop 2 | `{ph['props'][1]['module_id']}` | {ph['props'][1]['name']} |
| Prop 3 | `{ph['props'][2]['module_id']}` | {ph['props'][2]['name']} |

## Mockup references

- Character art: `{ph['character']['mockup_img']}`
- Character video: `{ph['character'].get('mockup_video')}`
- Building art: `{ph['building'].get('mockup_img')}`
- Prop arts: {', '.join('`'+p.get('mockup_img')+'`' for p in ph['props'])}

## Animation contract

Clips required: `{', '.join(ph['acceptance']['require_clips'])}`  
Motion class: `{ph['character']['motion']}` · Signature: `{ph['character']['signature']}`  
Building ambient: `{ph['building']['anim']}`  
Prop ambients: {', '.join(p['anim'] for p in ph['props'])}

## Town spawn (meters)

```json
{json.dumps({
  'character': ph['character']['spawn'],
  'building': ph['building']['spawn'],
  'props': [p['spawn'] for p in ph['props']],
}, ensure_ascii=False, indent=2)}
```

## Subagent order (mandatory)

1. `mockup-parity-guardian` — lock target pixels/IDs  
2. `character-animation-designer` — GLB + real clips  
3. `building-module-designer` — building GLB  
4. `prop-set-designer` — 3 prop GLBs  
5. `town-layout-planner` — verify spacing / district  
6. `godot-runtime-integrator` — load + idle play in town  
7. `red-mockup-delta-reviewer` — findings only  
8. `purple-parity-gate` — MOCKUP_PARITY_100 verify only  

## Definition of Done (phase)

- [ ] Character loads and **idle plays** with required clip names  
- [ ] Building loads at spawn  
- [ ] All 3 props load at spawn  
- [ ] No AABB overlap with other accepted phases  
- [ ] Visual delta vs mockup = **0 fail criteria** (see `contracts/mockup_parity_100.schema.json`)  
- [ ] Receipt written under `receipts/{ph['phase_id']}/`  
- [ ] **No self-accept** — Human ACCEPT required for product ship  

## Block rule

If previous phase is not `PARITY_100_VERIFIED` or `HUMAN_ACCEPTED`, this phase stays **BLOCKED**.
"""
        write(ROOT / "phases" / f"PHASE_{n:02d}.md", md)
        (ROOT / "phases" / f"PHASE_{n:02d}.json").write_text(
            json.dumps(ph, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # Contracts
    parity = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "aidle://town_build_10phase/mockup_parity_100",
        "title": "MOCKUP_PARITY_100 gate",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            "phase_id",
            "mockup_ssot",
            "character_id",
            "building_module_id",
            "prop_module_ids",
            "checks",
            "verdict",
            "self_accept",
        ],
        "properties": {
            "schema_version": {"const": "mockup_parity_100/1.0"},
            "phase_id": {"type": "string", "pattern": "^TOWN_PHASE_[0-9]{2}$"},
            "mockup_ssot": {"const": "MOCKUP_SSOT_V2"},
            "character_id": {"type": "string"},
            "building_module_id": {"type": "string"},
            "prop_module_ids": {"type": "array", "minItems": 3, "maxItems": 3, "items": {"type": "string"}},
            "checks": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "ids_match_mockup",
                    "clips_named_exact",
                    "idle_plays",
                    "building_loads",
                    "props_load_count",
                    "no_cyan_body",
                    "silhouette_readable_25d",
                    "town_no_overlap",
                    "district_role_intact",
                    "assets_hashed",
                ],
                "properties": {
                    "ids_match_mockup": {"type": "boolean"},
                    "clips_named_exact": {"type": "boolean"},
                    "idle_plays": {"type": "boolean"},
                    "building_loads": {"type": "boolean"},
                    "props_load_count": {"type": "integer", "minimum": 3},
                    "no_cyan_body": {"type": "boolean"},
                    "silhouette_readable_25d": {"type": "boolean"},
                    "town_no_overlap": {"type": "boolean"},
                    "district_role_intact": {"type": "boolean"},
                    "assets_hashed": {"type": "boolean"},
                },
            },
            "verdict": {"enum": ["FAIL", "PARITY_100_VERIFIED"]},
            "self_accept": {"const": False},
            "findings": {"type": "array", "items": {"type": "string"}},
            "evidence_paths": {"type": "array", "items": {"type": "string"}},
        },
    }
    (ROOT / "contracts" / "mockup_parity_100.schema.json").write_text(
        json.dumps(parity, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    handoff = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "aidle://town_build_10phase/agent_handoff",
        "title": "Town phase agent handoff",
        "type": "object",
        "additionalProperties": False,
        "required": ["schema_version", "from_agent", "to_agent", "phase_id", "payload_paths", "authority"],
        "properties": {
            "schema_version": {"const": "town_handoff/1.0"},
            "from_agent": {"type": "string"},
            "to_agent": {"type": "string"},
            "phase_id": {"type": "string"},
            "payload_paths": {"type": "array", "items": {"type": "string"}},
            "authority": {
                "enum": [
                    "READ_ONLY_AUDIT",
                    "PATCH_DRAFT",
                    "VERIFY_ONLY",
                    "REPORT_ONLY",
                    "HUMAN_APPROVAL_REQUIRED",
                ]
            },
            "notes": {"type": "string"},
        },
    }
    (ROOT / "contracts" / "agent_handoff.schema.json").write_text(
        json.dumps(handoff, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Agents
    agents = {
        "01_TOWN_ORCHESTRATOR.md": """# Town Orchestrator — 10 Phase Mockup Parity

## Identity
Bạn điều phối 10 phase dựng thị trấn Cozy bám **MOCKUP_SSOT_V2 100%**.
Không tự thiết kế mesh; không tự ACCEPT.

## Authority
`HUMAN_APPROVAL_REQUIRED` cho ship · work order / routing only.

## Truth
1. `../town/TOWN_LAYOUT_10PHASE.json`
2. `../../visual_reference/mockup_ssot_v2/MOCKUP_DESIGN_LOCK.md`
3. `../../visual_reference/mockup_ssot_v2/MOCKUP_SSOT_V2.html`
4. `E:/standards/maf/COMPLIANCE.md` + TrustLayer x16

## Rules
- Mỗi phase: **1 character + 1 building + 3 props** đúng ID mockup.
- Phase N blocked until phase N-1 `PARITY_100_VERIFIED`.
- Lệch mockup = CHANGES_REQUESTED — **không được dừng khi chưa 100%**.
- Runtime phải load + idle play; gallery lộn xộn bị cấm (dùng town layout).
- Red finds only; Purple verifies only; Blue patches only under WO.

## Pipeline per phase
`mockup-parity-guardian → character-animation-designer → building-module-designer → prop-set-designer → town-layout-planner → godot-runtime-integrator → red-mockup-delta-reviewer → purple-parity-gate → HUMAN`

## Output
Work order YAML + phase status update + handoffs.
""",
        "02_MOCKUP_PARITY_GUARDIAN.md": """# Mockup Parity Guardian

## Identity
Giữ khóa visual: mọi deliverable **y hệt mockup SSOT V2** (ID, silhouette, palette, clip names, motion class).

## Authority
`READ_ONLY_AUDIT` (+ report lock tables). Không patch product.

## Must
- Mở mockup HTML + JSON; trích exact IDs phase.
- Cyan chỉ manifestation.
- ≤3 palette families / character.
- Clip names exact — cấm alias missing→idle.
- Xuất `parity_target.json` cho phase (reference paths + acceptance).

## Stop condition
Không bao giờ “good enough”. Chỉ `PARITY_TARGET_LOCKED` hoặc `NEED_HUMAN`.
""",
        "03_CHARACTER_ANIMATION_DESIGNER.md": """# Character + Animation Designer (production)

## Identity
Tạo/cập nhật character **skinned GLB + real AnimationPlayer clips** khớp mockup art + timing bible.

## Authority
`PATCH_DRAFT` under WO lease only.

## Deliverables
- `.blend` offline + `.glb` under quarantine then promote path
- Skeleton family documented (Nori: 14-bone `skel_small_biped_robot_v1`)
- Clips keyed with exact names + durations > 0
- SHA-256 + validation JSON
- Idle must play in Godot presenter/town placer

## Rules
- Edit-chain from mockup concept — không regenerate lệch identity
- Root motion false unless WO says otherwise
- Animation never World-Commits
- Fail closed if bone/clip missing

## Gate
Smoke: load + play idle (+ required clips present). Visual side-by-side mockup.
""",
        "04_BUILDING_MODULE_DESIGNER.md": """# Building Module Designer

## Identity
Sản xuất building module GLB/catalog entry khớp mockup building art + ambient motion class.

## Authority
`PATCH_DRAFT` under WO.

## Deliverables
- module_id exact from phase
- GLB + material slots cream-first
- ambient anim class from mockup (`door_pulse`, `spin`, …)
- town spawn transform from layout JSON

## Rules
- Không invent module_id
- Godot owns collision after commit; Blender collision_hint advisory
- Warm door light / readability for 2.5D
""",
        "05_PROP_SET_DESIGNER.md": """# Prop Set Designer (3 per phase)

## Identity
Sản xuất đúng **3 props** của phase — không thêm, không bớt, không đổi ID.

## Authority
`PATCH_DRAFT` under WO.

## Deliverables
- 3× GLB + catalog rows
- ambient classes from mockup
- placements from town layout (orbit building, support district role)

## Rules
- Functional props for district (market gets cart/bench; home gets path/lamp/mailbox)
- No dump piles; spacing ≥0.8m between prop origins unless WO
""",
        "06_TOWN_LAYOUT_PLANNER.md": """# Town Layout Planner

## Identity
Giữ thị trấn **có trật tự**: districts, paths, spacing, camera readability.

## Authority
`READ_ONLY_AUDIT` / `PATCH_DRAFT` only on `town/*.json` under WO.

## Must verify
- Ring layout intact
- Min 6m building centers
- Character front-offset readable
- Path loop connects districts
- No overlap AABBs
- Phase does not break previous accepted districts

## Forbidden
Random scatter, overlapping stalls, props inside building volumes.
""",
        "07_GODOT_RUNTIME_INTEGRATOR.md": """# Godot Runtime Integrator

## Identity
Gắn phase vào runtime town placer: load GLB, play idle, position from layout.

## Authority
`PATCH_DRAFT` under WO on `game/scripts/modules/town/**` + resources.

## Deliverables
- Phase loads via `town_layout_loader`
- Marker `AIDLE_TOWN_PHASE_XX=PASS` on smoke
- No World Commit from presentation spawn

## Honesty
Document if asset still mockup-only (catalog missing) — then FAIL parity, not silent placeholder success.
""",
        "08_RED_MOCKUP_DELTA_REVIEWER.md": """# Red Team — Mockup Delta Reviewer

## Identity
Chỉ tìm lệch mockup / overlap / missing clips / wrong IDs.

## Authority
`READ_ONLY_AUDIT`. **Never patch.**

## Report
Finding register: severity, evidence path, mockup expected vs actual.
""",
        "09_PURPLE_PARITY_GATE.md": """# Purple — MOCKUP_PARITY_100 Gate

## Identity
Xác minh độc lập theo `contracts/mockup_parity_100.schema.json`.

## Authority
`VERIFY_ONLY`. Never patch product.

## Verdicts
- `PARITY_100_VERIFIED` only if every check true
- else `FAIL` + findings
- Never self-accept; Human still required for ship
""",
        "10_TOWN_QA_PLAYABILITY.md": """# Town QA / Playability

## Identity
Chơi thử camera 2.5D: đọc silhouette, path, district function, reduced-motion.

## Authority
`VERIFY_ONLY`.

## Checks
- Can walk plaza loop without clipping buildings
- Each district reads its role in one glance
- Idle animations loop cleanly
""",
    }
    for name, body in agents.items():
        write(ROOT / "agents" / name, body)

    write(
        ROOT / "00_README.md",
        """# AIdle Town Build — 10 Phase Mockup-Parity System

## Mục tiêu

Dựng **thị trấn Cozy** từ mockup SSOT V2 theo **10 phase**, mỗi phase:

- **1 nhân vật** (animation thật, clip contract)
- **1 building**
- **3 vật thể**

**Khóa:** bám mockup **100%** (`MOCKUP_PARITY_100`) — chưa đạt thì **không được dừng / không claim complete**.

## Nguồn sự thật

| Layer | Path |
|-------|------|
| Visual SSOT | `../visual_reference/mockup_ssot_v2/MOCKUP_SSOT_V2.html` |
| Design lock | `../visual_reference/mockup_ssot_v2/MOCKUP_DESIGN_LOCK.md` |
| Town layout | `town/TOWN_LAYOUT_10PHASE.json` |
| Phases | `phases/PHASE_01.md` … `PHASE_10.md` |
| Parity gate | `contracts/mockup_parity_100.schema.json` |

## Subagents

| # | Agent | Authority |
|---|-------|-----------|
| 01 | Town Orchestrator | HUMAN_APPROVAL_REQUIRED |
| 02 | Mockup Parity Guardian | READ_ONLY_AUDIT |
| 03 | Character Animation Designer | PATCH_DRAFT |
| 04 | Building Module Designer | PATCH_DRAFT |
| 05 | Prop Set Designer | PATCH_DRAFT |
| 06 | Town Layout Planner | PATCH_DRAFT (layout only) |
| 07 | Godot Runtime Integrator | PATCH_DRAFT |
| 08 | Red Mockup Delta Reviewer | READ_ONLY_AUDIT |
| 09 | Purple Parity Gate | VERIFY_ONLY |
| 10 | Town QA Playability | VERIFY_ONLY |

Aligns with TrustLayer x16 + MAF (`E:\\standards\\maf\\COMPLIANCE.md`).

## Workflow

`READY → CLAIMED → IN_PROGRESS → REVIEW_REQUESTED → PARITY_100_VERIFIED → HUMAN_ACCEPT`

Phase N+1 **BLOCKED** until phase N is `PARITY_100_VERIFIED` (or Human waived in writing).

## Town order (not inventory dump)

1 home_plot → 2 market_square → 3 workshop_row → 4 creature_garden → 5 pollinator_farm  
→ 6 water_edge → 7 craft_landmark → 8 barn_yard → 9 spirit_bridge → 10 canopy_lookout

## Runtime

Godot: `game/scripts/modules/town/town_layout_loader.gd` + resource  
`game/resources/town/town_layout_10phase.json`

## Honesty

- `accepted=false` / `self_accept=false` until Human Product Lead
- Missing production GLB for a slot = phase **FAIL** parity (no fake pass)
- Presentation spawn ≠ World Commit ownership
""",
    )

    write(
        ROOT / "01_MASTER_ORCHESTRATOR.md",
        (ROOT / "agents" / "01_TOWN_ORCHESTRATOR.md").read_text(encoding="utf-8"),
    )

    write(
        ROOT / "workflow" / "PHASE_WORKFLOW.md",
        """# Phase Workflow — MOCKUP_PARITY_100

## States

`READY → CLAIMED → IN_PROGRESS → REVIEW_REQUESTED → PARITY_100_VERIFIED → HUMAN_ACCEPT`

Error: `CHANGES_REQUESTED` → rework until parity 100.  
Three identical failure signatures → `NEED_HUMAN`.

## Hard stop (must not stop early)

Agents **must continue rework** while any parity check is false:

1. IDs match mockup  
2. Clips named exact + idle plays  
3. Building + 3 props load  
4. No cyan body  
5. Silhouette readable 2.5D  
6. Town no overlap  
7. District role intact  
8. Assets hashed  

“Looks fine” without evidence = protocol violation.

## Parallelism

Within a phase after parity target locked:

- Character anim ∥ Building module ∥ Prop set  
- Then layout verify → runtime integrate → Red → Purple  

## One writer

One writer lease per file. Red/Purple never patch product.
""",
    )

    write(
        ROOT / "MASTER_PLAN_10_PHASE.md",
        f"""# MASTER PLAN — Cozy Starter Town 10 Phase

**Status:** `SYSTEM_ACTIVE_PHASE1_READY`  
**Mockup:** MOCKUP_SSOT_V2  
**Gate:** MOCKUP_PARITY_100  

## Phase table

| Ph | District | Character | Building | Props (3) |
|---:|---|---|---|---|
"""
        + "\n".join(
            f"| {ph['phase']} | `{ph['district_id']}` | {ph['character']['name']} (`{ph['character']['character_id']}`) | `{ph['building']['module_id']}` | "
            + ", ".join(f"`{p['module_id']}`" for p in ph["props"])
            + " |"
            for ph in phases
        )
        + """

## Execution rule

Không chuyển phase khi phase trước chưa `PARITY_100_VERIFIED`.  
Không claim market-ready / ship khi Human chưa ACCEPT.

## Next action

Run **Phase 01 home_plot** subagent pipeline against existing Nori + house assets; fill gaps until parity 100.
""",
    )

    manifest = {
        "package": "aidle_town_build_10phase",
        "version": "1.0.0",
        "mockup_ssot": "MOCKUP_SSOT_V2",
        "phases": 10,
        "agents": 10,
        "status": "SYSTEM_ACTIVE_PHASE1_READY",
        "accepted": False,
        "self_accept": False,
    }
    (ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    # Copy layout into game resources for runtime
    game_town = GAME / "resources" / "town"
    game_town.mkdir(parents=True, exist_ok=True)
    runtime_layout = {
        "schema_version": "1.0.0",
        "town_id": town["town_id"],
        "mockup_ssot": "MOCKUP_SSOT_V2",
        "active_phases": [1],  # only phase 1 enabled until parity expands
        "phases": [
            {
                "phase": ph["phase"],
                "phase_id": ph["phase_id"],
                "district_id": ph["district_id"],
                "character": {
                    "character_id": ph["character"]["character_id"],
                    "slug": ph["character"]["slug"],
                    "spawn": ph["character"]["spawn"],
                    "clips_min": ph["acceptance"]["require_clips"],
                },
                "building": {
                    "module_id": ph["building"]["module_id"],
                    "spawn": ph["building"]["spawn"],
                },
                "props": [
                    {"module_id": p["module_id"], "spawn": p["spawn"]} for p in ph["props"]
                ],
            }
            for ph in phases
        ],
    }
    (game_town / "town_layout_10phase.json").write_text(
        json.dumps(runtime_layout, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("Generated", ROOT)
    print("Phases", len(phases))
    print("Game layout", game_town / "town_layout_10phase.json")


if __name__ == "__main__":
    main()
