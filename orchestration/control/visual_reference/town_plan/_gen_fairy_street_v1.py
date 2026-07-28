# -*- coding: utf-8 -*-
"""TOWN_FAIRY_STREET_PLAN_V1 — thị trấn cổ tích thân thiện (design mockup).

Phương pháp lấy cảm hứng 3DStreet (https://github.com/3DStreet/3dstreet):
  - Đường phố = chuỗi segment modular (path / sidewalk / green strip / building face)
  - Kiến trúc lặp lại theo family + biến thể màu/mái/cửa (rhythm hài hòa)
  - Street furniture (đèn, ghế, hộp hoa) dọc vỉa hè

KHÔNG:
  - Clone asset/code AGPL 3DStreet
  - Claim IP Disney / replica franchise
  - Patch game/** (design parent only)

Fits ±12 cadastre. IDs từ MOCKUP_SSOT_V2.
"""
from __future__ import annotations

import hashlib
import json
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent
PLAN_ID = "TOWN_FAIRY_STREET_PLAN_V1"

COLS = list("ABCDEFGHIJKL")
ROWS = list(range(1, 13))
CELL = 2.0


def cell_center(col: str, row: int) -> tuple[float, float]:
    i = COLS.index(col)
    j = row - 1
    return (-11.0 + i * CELL, 11.0 - j * CELL)


def cell_id(col: str, row: int) -> str:
    return f"{col}{row}"


def multi_cells(col0: str, row0: int, w: int, h: int) -> list[str]:
    i0 = COLS.index(col0)
    out = []
    for di in range(w):
        for dj in range(h):
            out.append(cell_id(COLS[i0 + di], row0 + dj))
    return out


def footprint_center(cells: list[str]) -> tuple[float, float]:
    xs, zs = [], []
    for c in cells:
        col, row = c[0], int(c[1:])
        x, z = cell_center(col, row)
        xs.append(x)
        zs.append(z)
    return (sum(xs) / len(xs), sum(zs) / len(zs))


# ---------------------------------------------------------------------------
# Architecture families — same silhouette language, many instances/variants
# ---------------------------------------------------------------------------
# Inspired by 3DStreet "building variants along street edge" + fairy-tale
# storybook rhythm: same roof slope family, soft corners, pastel facades.

ARCH_FAMILIES = {
    "ARCH_COTTAGE": {
        "name_vi": "Nhà tranh cổ tích (cottage)",
        "name_en": "Storybook cottage",
        "silhouette": "steep_peak_roof_soft_corners",
        "height_tier": "1.5_story",
        "mood": "home_warm",
        "repeatable": True,
        "ssot_primary": "cozy_house_small_A",
        "palette_variants": ["cream_rose", "butter_peach", "mint_soft", "sky_lilac"],
        "roof_variants": ["terracotta_soft", "slate_blue", "moss_green"],
        "door_variants": ["arched_wood", "round_window_door"],
        "harmony_rules": [
            "Cùng độ dốc mái trong 1 dãy phố",
            "Đổi palette xen kẽ (không 2 nhà liền kề cùng màu)",
            "Cửa sổ tròn nhỏ + hộp hoa mặt tiền",
        ],
    },
    "ARCH_SHOP": {
        "name_vi": "Mặt phố cửa hàng",
        "name_en": "Friendly shop front",
        "silhouette": "flat_shop_awning_peak_accent",
        "height_tier": "1_story",
        "mood": "market_cheerful",
        "repeatable": True,
        "ssot_primary": "cozy_market_stall_A",
        "palette_variants": ["strawberry_awning", "honey_awning", "blueberry_awning"],
        "roof_variants": ["striped_awning"],
        "door_variants": ["open_stall", "half_door"],
        "harmony_rules": [
            "Nhịp 1 module / 2m mặt tiền dọc Storybook Lane",
            "Mái che cùng cao độ",
            "Biển hiệu cùng font silhouette (không neon)",
        ],
    },
    "ARCH_WORKSHOP": {
        "name_vi": "Xưởng thợ",
        "name_en": "Craft workshop",
        "silhouette": "boxy_chimney_soft",
        "height_tier": "1_story",
        "mood": "craft_warm",
        "repeatable": True,
        "ssot_primary": "cozy_workshop_A",
        "palette_variants": ["clay_umber", "warm_sand"],
        "roof_variants": ["dark_shingle"],
        "door_variants": ["wide_barn_door_soft"],
        "harmony_rules": ["Cùng chimney language với cottage", "Sân trước có rack props"],
    },
    "ARCH_GAZEBO": {
        "name_vi": "Chòi vườn",
        "name_en": "Garden gazebo",
        "silhouette": "open_hex_or_round_roof",
        "height_tier": "open",
        "mood": "rest_soft",
        "repeatable": False,
        "ssot_primary": "cozy_gazebo_A",
        "palette_variants": ["cream_wood"],
        "roof_variants": ["soft_cone"],
        "door_variants": ["open"],
        "harmony_rules": ["Tâm village green — landmark nhẹ, không che nhà"],
    },
    "ARCH_GREENHOUSE": {
        "name_vi": "Nhà kính",
        "name_en": "Glass greenhouse",
        "silhouette": "gable_glass",
        "height_tier": "1_story",
        "mood": "grow_fresh",
        "repeatable": True,
        "ssot_primary": "cozy_greenhouse_A",
        "palette_variants": ["mint_frame", "white_frame"],
        "roof_variants": ["glass_gable"],
        "door_variants": ["glass_door"],
        "harmony_rules": ["Khung mỏng, trong suốt — không tranh sáng cottage"],
    },
    "ARCH_WELL": {
        "name_vi": "Nhà giếng",
        "name_en": "Well house",
        "silhouette": "round_stone_peak_cap",
        "height_tier": "low",
        "mood": "water_calm",
        "repeatable": False,
        "ssot_primary": "cozy_well_house_A",
        "palette_variants": ["stone_warm"],
        "roof_variants": ["wood_cap"],
        "door_variants": ["arch_open"],
        "harmony_rules": ["Gần ao / path nước — scale nhỏ hơn cottage"],
    },
    "ARCH_WINDMILL": {
        "name_vi": "Cối xay gió",
        "name_en": "Windmill landmark",
        "silhouette": "tower_blades",
        "height_tier": "landmark_tall",
        "mood": "story_icon",
        "repeatable": False,
        "ssot_primary": "cozy_windmill_A",
        "palette_variants": ["cream_tower_blue_blades"],
        "roof_variants": ["cone_cap"],
        "door_variants": ["small_door"],
        "harmony_rules": ["1 landmark / map — neo tầm nhìn SW"],
    },
    "ARCH_BARN": {
        "name_vi": "Kho / chuồng",
        "name_en": "Soft barn",
        "silhouette": "wide_gable",
        "height_tier": "1.5_story",
        "mood": "farm_friendly",
        "repeatable": True,
        "ssot_primary": "cozy_barn_small_A",
        "palette_variants": ["soft_red", "soft_cream"],
        "roof_variants": ["dark_gable"],
        "door_variants": ["double_soft"],
        "harmony_rules": ["Mái gable cùng góc cottage nhưng rộng hơn"],
    },
    "ARCH_BRIDGE": {
        "name_vi": "Cầu vòm",
        "name_en": "Story arch bridge",
        "silhouette": "gentle_arch",
        "height_tier": "low_span",
        "mood": "journey",
        "repeatable": False,
        "ssot_primary": "cozy_bridge_arch_A",
        "palette_variants": ["stone_warm"],
        "roof_variants": ["none"],
        "door_variants": ["none"],
        "harmony_rules": ["Vòm mềm — bắc suối/path, không industrial"],
    },
    "ARCH_LOOKOUT": {
        "name_vi": "Tháp vọng",
        "name_en": "Lookout tower",
        "silhouette": "slim_round_tower",
        "height_tier": "landmark_mid",
        "mood": "wonder",
        "repeatable": False,
        "ssot_primary": "cozy_watchtower_A",
        "palette_variants": ["stone_ivy"],
        "roof_variants": ["cone_flag"],
        "door_variants": ["small_door"],
        "harmony_rules": ["1 tháp SE — complement windmill (không 2 tháp cạnh nhau)"],
    },
}

# ---------------------------------------------------------------------------
# Surface materials — flat paved stone + wooden decks/boardwalks
# ---------------------------------------------------------------------------
# User request: đường bằng phẳng lát đá + bệ gỗ trên bản đồ quy hoạch.
# All surfaces are FLAT (slope 0°) for walkability; soft fairy-tale texture only.

SURFACE_MATERIALS = {
    "STONE_PAVER_FLAT": {
        "name_vi": "Đá lát phẳng",
        "name_en": "Flat stone pavers",
        "kind": "paved_path",
        "flat": True,
        "slope_deg": 0.0,
        "module_hint": "cozy_path_stone_A",
        "finish": "rounded_flagstone_or_square_paver_soft",
        "edge": "grass_or_flower_soft_shoulder",
        "color_map": "stone_paver",
        "use_vi": "Trục chính, vành đai, hẻm chợ — đi êm, đọc rõ hướng",
        "harmony": [
            "Mặt phẳng 0° (không gồ ghề gameplay)",
            "Viền bo mềm + 1 hàng hoa/cỏ hai bên",
            "Khớp nối segment liên tục — không gãy giữa cell",
        ],
    },
    "STONE_RING_PLAZA": {
        "name_vi": "Vòng đá quảng trường",
        "name_en": "Plaza stone ring",
        "kind": "paved_plaza_ring",
        "flat": True,
        "slope_deg": 0.0,
        "module_hint": "cozy_path_stone_A",
        "finish": "concentric_flat_pavers",
        "edge": "lawn_inside_flower_outside",
        "color_map": "stone_paver_light",
        "use_vi": "Vòng quanh gazebo — lát đá phẳng trên nền cỏ",
    },
    "WOOD_DECK_FLAT": {
        "name_vi": "Bệ gỗ phẳng",
        "name_en": "Flat wood deck / platform",
        "kind": "wood_platform",
        "flat": True,
        "slope_deg": 0.0,
        "module_hint": "future_cozy_wood_deck_A | placeholder: wood plank plane",
        "finish": "soft_planks_parallel_to_long_edge",
        "edge": "rounded_beam_or_low_rail",
        "color_map": "wood_deck",
        "use_vi": "Sàn đứng trước nhà / shop / giếng / chân tháp — thân thiện, ấm",
        "harmony": [
            "Cao hơn path đá ~0.05–0.12 unit (gần như phẳng, có mép đọc được)",
            "Thớ gỗ song song trục dài bệ",
            "Góc bo tròn storybook — không pallet thô industrial",
        ],
    },
    "WOOD_BOARDWALK": {
        "name_vi": "Cầu ván / lối gỗ dài",
        "name_en": "Wood boardwalk",
        "kind": "wood_path",
        "flat": True,
        "slope_deg": 0.0,
        "module_hint": "future_cozy_boardwalk_A",
        "finish": "plank_run_along_path",
        "edge": "low_soft_rail_optional",
        "color_map": "wood_boardwalk",
        "use_vi": "Ven nước, tiếp cận cầu, đoạn trên cỏ ẩm — thay đá nơi cần cảm giác ấm",
    },
    "WOOD_BRIDGE_DECK": {
        "name_vi": "Mặt sàn gỗ cầu",
        "name_en": "Bridge wood decking",
        "kind": "wood_bridge_surface",
        "flat": True,
        "slope_deg": 0.0,
        "module_hint": "part_of cozy_bridge_arch_A",
        "finish": "planks_across_span",
        "edge": "soft_handrail",
        "color_map": "wood_deck_dark",
        "use_vi": "Mặt cầu vòm — phẳng an toàn, lan can mềm",
    },
}

# Street segment types (3DStreet method → fairy-tale soft road + surface finish)
STREET_SEGMENTS = {
    "seg_plaza_green": {
        "width_m": 4.0,
        "layers": ["soft_lawn", "flower_ring", "path_stone_ring"],
        "surface": "STONE_RING_PLAZA",
        "surface_secondary": "WOOD_DECK_FLAT",
        "feel": "village_heart",
        "vi": "Quảng trường cỏ + vòng đá phẳng + bệ gỗ dưới gazebo",
    },
    "seg_storybook_lane": {
        "width_m": 3.0,
        "layers": [
            "building_face_L",
            "sidewalk_L_1.0",
            "path_center_stone_flat_1.0",
            "sidewalk_R_1.0",
            "building_face_R",
            "wood_deck_shopfront",
        ],
        "surface": "STONE_PAVER_FLAT",
        "surface_secondary": "WOOD_DECK_FLAT",
        "feel": "main_street_friendly",
        "vi": "Phố chính — lòng đường đá lát phẳng + bệ gỗ trước shop",
    },
    "seg_cottage_row": {
        "width_m": 2.5,
        "layers": ["garden_strip_0.5", "path_stone_flat_1.0", "wood_porch_deck", "cottage_face"],
        "surface": "STONE_PAVER_FLAT",
        "surface_secondary": "WOOD_DECK_FLAT",
        "feel": "residential_soft",
        "vi": "Lối đá phẳng dọc cottage + bệ gỗ hiên nhà",
    },
    "seg_craft_alley": {
        "width_m": 2.0,
        "layers": ["path_stone_flat_1.2", "wood_work_pad", "prop_strip"],
        "surface": "STONE_PAVER_FLAT",
        "surface_secondary": "WOOD_DECK_FLAT",
        "feel": "workshop_cozy",
        "vi": "Hẻm xưởng — đá phẳng + bệ gỗ để dụng cụ",
    },
    "seg_orchard_lane": {
        "width_m": 2.0,
        "layers": ["tree_edge", "path_stone_soft", "fence_soft"],
        "surface": "STONE_PAVER_FLAT",
        "feel": "nature_walk",
        "vi": "Lối vườn — đá lát phẳng hẹp",
    },
    "seg_water_path": {
        "width_m": 2.0,
        "layers": ["water_edge", "wood_boardwalk", "bench_nook"],
        "surface": "WOOD_BOARDWALK",
        "surface_secondary": "STONE_PAVER_FLAT",
        "feel": "calm_water",
        "vi": "Ven nước: ván gỗ boardwalk + đoạn đá nối plaza",
    },
    "seg_mill_road": {
        "width_m": 2.0,
        "layers": ["path_stone_flat", "grass_shoulder"],
        "surface": "STONE_PAVER_FLAT",
        "feel": "landmark_approach",
        "vi": "Đường đá phẳng tới cối xay / tháp",
    },
    "seg_bridge_approach": {
        "width_m": 2.0,
        "layers": ["path_stone_to_arch", "wood_bridge_deck", "rail_soft"],
        "surface": "STONE_PAVER_FLAT",
        "surface_secondary": "WOOD_BRIDGE_DECK",
        "feel": "crossing",
        "vi": "Tiếp cận đá phẳng + mặt sàn gỗ trên cầu",
    },
}

# Soft palette (fairy-tale friendly — not corporate neon)
PALETTE = {
    "sky": "#c9e4f5",
    "lawn": "#9fd4a3",
    "lawn_deep": "#72A96B",
    "path": "#e8d5b5",
    "path_edge": "#d4c4a0",
    "stone_paver": "#c5b8a4",
    "stone_paver_light": "#d8cfc0",
    "stone_joint": "#a89880",
    "wood_deck": "#c4a574",
    "wood_boardwalk": "#b8956a",
    "wood_deck_dark": "#9a7a52",
    "wood_plank_line": "#8a6a42",
    "water": "#9ED7E5",
    "plaza": "#b8e0b0",
    "cottage": "#f5c451",
    "shop": "#e88b7a",
    "workshop": "#c98a5e",
    "garden": "#7fc98f",
    "greenhouse": "#8fd4b0",
    "well": "#7eb8c9",
    "windmill": "#6b8cae",
    "barn": "#c47a6a",
    "bridge": "#a89f90",
    "lookout": "#b08d57",
    "ring": "#dcc9a8",
    "ink": "#3d3a36",
    "paper": "#fbf6ee",
    "accent_rose": "#f2a7b0",
    "accent_lilac": "#c4b0e0",
    "accent_butter": "#f6e27a",
}

DISTRICTS = [
    {
        "district_id": "PLAZA",
        "name": "Quảng trường Cỏ Làng",
        "name_en": "Village Green",
        "function_vi": "Tâm xã hội — gazebo + vòng hoa + chỗ tụ họp",
        "color": PALETTE["plaza"],
        "center": {"x": 0.0, "z": 0.0},
        "street_segment": "seg_plaza_green",
        "arch_primary": "ARCH_GAZEBO",
    },
    {
        "district_id": "HOME",
        "name": "Dãy Cottage",
        "name_en": "Cottage Row",
        "function_vi": "Cư trú — nhiều nhà cùng family ARCH_COTTAGE, palette xen kẽ",
        "color": PALETTE["cottage"],
        "center": {"x": 0.0, "z": 6.0},
        "street_segment": "seg_cottage_row",
        "arch_primary": "ARCH_COTTAGE",
    },
    {
        "district_id": "MARKET",
        "name": "Phố Chợ Storybook",
        "name_en": "Storybook Lane Market",
        "function_vi": "Thương mại thân thiện — shop front lặp nhịp",
        "color": PALETTE["shop"],
        "center": {"x": 7.0, "z": 2.0},
        "street_segment": "seg_storybook_lane",
        "arch_primary": "ARCH_SHOP",
    },
    {
        "district_id": "WORKSHOP",
        "name": "Hẻm Xưởng",
        "name_en": "Craft Alley",
        "function_vi": "Thủ công — workshop + prop rack",
        "color": PALETTE["workshop"],
        "center": {"x": 7.0, "z": -4.0},
        "street_segment": "seg_craft_alley",
        "arch_primary": "ARCH_WORKSHOP",
    },
    {
        "district_id": "GARDEN",
        "name": "Vườn Nghỉ",
        "name_en": "Rest Garden",
        "function_vi": "Hoa + bụi + ghế — đệm giữa cottage và chợ",
        "color": PALETTE["garden"],
        "center": {"x": 4.0, "z": 7.0},
        "street_segment": "seg_orchard_lane",
        "arch_primary": "ARCH_GAZEBO",
    },
    {
        "district_id": "GREENHOUSE",
        "name": "Khu Kính Xanh",
        "name_en": "Glass Garden",
        "function_vi": "Nhà kính + luống — nhịp farm thân thiện",
        "color": PALETTE["greenhouse"],
        "center": {"x": -7.0, "z": 6.0},
        "street_segment": "seg_orchard_lane",
        "arch_primary": "ARCH_GREENHOUSE",
    },
    {
        "district_id": "WELL",
        "name": "Góc Nước",
        "name_en": "Water Nook",
        "function_vi": "Giếng + ao nhỏ + chim tắm",
        "color": PALETTE["well"],
        "center": {"x": -7.0, "z": 0.0},
        "street_segment": "seg_water_path",
        "arch_primary": "ARCH_WELL",
    },
    {
        "district_id": "WINDMILL",
        "name": "Đồi Cối Xay",
        "name_en": "Windmill Knoll",
        "function_vi": "Landmark SW — silhouette cổ tích",
        "color": PALETTE["windmill"],
        "center": {"x": -7.0, "z": -7.0},
        "street_segment": "seg_mill_road",
        "arch_primary": "ARCH_WINDMILL",
    },
    {
        "district_id": "BARN",
        "name": "Sân Kho Mềm",
        "name_en": "Soft Barn Yard",
        "function_vi": "Barn + cây ăn quả — farm edge",
        "color": PALETTE["barn"],
        "center": {"x": 0.0, "z": -7.0},
        "street_segment": "seg_orchard_lane",
        "arch_primary": "ARCH_BARN",
    },
    {
        "district_id": "BRIDGE",
        "name": "Cầu Vòm",
        "name_en": "Arch Crossing",
        "function_vi": "Cầu + cây liễu — hành trình vào làng",
        "color": PALETTE["bridge"],
        "center": {"x": 2.0, "z": -9.0},
        "street_segment": "seg_bridge_approach",
        "arch_primary": "ARCH_BRIDGE",
    },
    {
        "district_id": "LOOKOUT",
        "name": "Tháp Vọng",
        "name_en": "Wonder Lookout",
        "function_vi": "Tháp SE — nhìn ra map",
        "color": PALETTE["lookout"],
        "center": {"x": 8.0, "z": -8.0},
        "street_segment": "seg_mill_road",
        "arch_primary": "ARCH_LOOKOUT",
    },
]


# Plots: 10 buildings + 30 props + 10 characters = 50
# Layout = fairy street: plaza core, cottage row N, market E, craft SE,
# water W, mill SW, barn S, bridge S, lookout SE, greenhouse NW

def make_plot(
    plot_id: str,
    role: str,
    object_id: str,
    district: str,
    cells: list[str],
    rot: float = 0.0,
    arch_family: str | None = None,
    palette_variant: str | None = None,
    instance_of: str | None = None,
    street_face: str | None = None,
    notes_vi: str = "",
) -> dict:
    cx, cz = footprint_center(cells)
    p = {
        "plot_id": plot_id,
        "role": role,
        "object_id": object_id,
        "district": district,
        "cells": cells,
        "position": {"x": round(cx, 2), "y": 0.0, "z": round(cz, 2)},
        "rotation_deg": rot,
        "occupancy_cells": cells,
        "notes_vi": notes_vi,
    }
    if arch_family:
        p["arch_family"] = arch_family
        p["architecture"] = {
            "family": arch_family,
            "palette_variant": palette_variant,
            "instance_of": instance_of or arch_family,
            "street_face": street_face,
            "modular_repeat": ARCH_FAMILIES.get(arch_family, {}).get("repeatable", False),
        }
    return p


PLOTS: list[dict] = []

# --- BUILDINGS (10) — each maps MOCKUP_SSOT; cottages/shops emphasize modularity ---
PLOTS.append(
    make_plot(
        "P-B01",
        "building",
        "cozy_house_small_A",
        "HOME",
        multi_cells("F", 4, 2, 2),
        rot=0,
        arch_family="ARCH_COTTAGE",
        palette_variant="cream_rose",
        street_face="south_to_plaza",
        notes_vi="Cottage hub — prototype family ARCH_COTTAGE (có thể lặp dọc hàng F–H).",
    )
)
PLOTS.append(
    make_plot(
        "P-B02",
        "building",
        "cozy_workshop_A",
        "WORKSHOP",
        multi_cells("J", 8, 2, 2),
        rot=270,
        arch_family="ARCH_WORKSHOP",
        palette_variant="clay_umber",
        street_face="west_to_craft_alley",
        notes_vi="Xưởng thợ — cùng chimney language cottage.",
    )
)
PLOTS.append(
    make_plot(
        "P-B03",
        "building",
        "cozy_market_stall_A",
        "MARKET",
        multi_cells("J", 5, 2, 2),
        rot=270,
        arch_family="ARCH_SHOP",
        palette_variant="strawberry_awning",
        street_face="west_to_storybook_lane",
        notes_vi="Shop module — nhịp lặp dọc Storybook Lane (awning cùng cao độ).",
    )
)
PLOTS.append(
    make_plot(
        "P-B04",
        "building",
        "cozy_gazebo_A",
        "PLAZA",
        multi_cells("F", 6, 2, 2),
        rot=0,
        arch_family="ARCH_GAZEBO",
        palette_variant="cream_wood",
        street_face="center",
        notes_vi="Tâm Village Green — chòi mở, không che sightline.",
    )
)
PLOTS.append(
    make_plot(
        "P-B05",
        "building",
        "cozy_greenhouse_A",
        "GREENHOUSE",
        multi_cells("B", 3, 2, 2),
        rot=0,
        arch_family="ARCH_GREENHOUSE",
        palette_variant="mint_frame",
        street_face="south",
        notes_vi="Nhà kính NW — khung mỏng, lặp được nếu farm mở rộng.",
    )
)
PLOTS.append(
    make_plot(
        "P-B06",
        "building",
        "cozy_well_house_A",
        "WELL",
        multi_cells("B", 6, 2, 2),
        rot=90,
        arch_family="ARCH_WELL",
        palette_variant="stone_warm",
        street_face="east_to_plaza",
        notes_vi="Nhà giếng — scale thấp hơn cottage.",
    )
)
PLOTS.append(
    make_plot(
        "P-B07",
        "building",
        "cozy_windmill_A",
        "WINDMILL",
        multi_cells("B", 10, 2, 2),
        rot=0,
        arch_family="ARCH_WINDMILL",
        palette_variant="cream_tower_blue_blades",
        street_face="east",
        notes_vi="Landmark duy nhất SW — silhouette cổ tích.",
    )
)
PLOTS.append(
    make_plot(
        "P-B08",
        "building",
        "cozy_barn_small_A",
        "BARN",
        multi_cells("F", 10, 2, 2),
        rot=0,
        arch_family="ARCH_BARN",
        palette_variant="soft_red",
        street_face="north",
        notes_vi="Barn S — gable rộng, cùng góc mái cottage.",
    )
)
PLOTS.append(
    make_plot(
        "P-B09",
        "building",
        "cozy_bridge_arch_A",
        "BRIDGE",
        multi_cells("F", 12, 2, 1),
        rot=90,
        arch_family="ARCH_BRIDGE",
        palette_variant="stone_warm",
        street_face="span_ew",
        notes_vi="Cầu vòm nam — tách barn/lookout, không overlap.",
    )
)
PLOTS.append(
    make_plot(
        "P-B10",
        "building",
        "cozy_watchtower_A",
        "LOOKOUT",
        multi_cells("K", 11, 2, 2),
        rot=0,
        arch_family="ARCH_LOOKOUT",
        palette_variant="stone_ivy",
        street_face="west",
        notes_vi="Tháp vọng SE — complement windmill, không cạnh nhau.",
    )
)

# --- PROPS (30) — street furniture rhythm like 3DStreet sidewalk objects ---
PROP_SPECS = [
    # HOME / cottage front
    ("P-P01", "cozy_path_stone_A", "HOME", "F", 6, 0, "Lối đá ra plaza"),
    ("P-P02", "cozy_garden_lamp_A", "HOME", "E", 5, 0, "Đèn vườn — nhịp 4–6m"),
    ("P-P03", "cozy_mailbox_A", "HOME", "E", 4, 0, "Hộp thư cottage"),
    # WORKSHOP
    ("P-P04", "cozy_tool_rack_A", "WORKSHOP", "I", 8, 270, "Giá dụng cụ mặt hẻm"),
    ("P-P05", "cozy_crate_small_A", "WORKSHOP", "I", 9, 0, "Thùng gỗ"),
    ("P-P06", "cozy_barrel_A", "WORKSHOP", "J", 10, 0, "Thùng tròn"),
    # MARKET / storybook lane furniture
    ("P-P07", "cozy_bench_A", "MARKET", "I", 5, 270, "Ghế vỉa hè chợ"),
    ("P-P08", "cozy_cart_A", "MARKET", "I", 6, 0, "Xe kéo chợ"),
    ("P-P09", "cozy_signpost_A", "MARKET", "I", 4, 0, "Biển chỉ đường thân thiện"),
    # GARDEN
    ("P-P10", "cozy_flower_cluster_A", "GARDEN", "H", 3, 0, "Cụm hoa — soft color"),
    ("P-P11", "cozy_flower_bed_B", "GARDEN", "G", 3, 0, "Luống hoa"),
    ("P-P12", "cozy_bush_round_A", "GARDEN", "H", 4, 0, "Bụi tròn"),
    # GREENHOUSE
    ("P-P13", "cozy_farm_plot_A", "GREENHOUSE", "A", 3, 0, "Luống canh tác"),
    ("P-P14", "cozy_crop_row_A", "GREENHOUSE", "A", 4, 0, "Hàng rau"),
    ("P-P15", "cozy_scarecrow_A", "GREENHOUSE", "C", 2, 0, "Bù nhìn dễ thương"),
    # WELL
    ("P-P16", "cozy_pond_small_A", "WELL", "A", 6, 0, "Ao nhỏ"),
    ("P-P17", "cozy_water_pump_A", "WELL", "A", 7, 0, "Bơm nước"),
    ("P-P18", "cozy_birdbath_A", "WELL", "C", 6, 0, "Bồn tắm chim"),
    # WINDMILL
    ("P-P19", "cozy_fence_section_A", "WINDMILL", "A", 10, 0, "Hàng rào mềm"),
    ("P-P20", "cozy_grass_tuft_A", "WINDMILL", "C", 10, 0, "Cỏ trang trí"),
    ("P-P21", "cozy_rock_cluster_A", "WINDMILL", "C", 11, 0, "Đá chân tháp cối"),
    # BARN
    ("P-P22", "cozy_tree_fruit_A", "BARN", "E", 10, 0, "Cây ăn quả"),
    ("P-P23", "cozy_rock_small_A", "BARN", "H", 10, 0, "Đá nhỏ"),
    ("P-P24", "cozy_rock_stacked_A", "BARN", "H", 11, 0, "Đá xếp"),
    # BRIDGE
    ("P-P25", "cozy_tree_willow_A", "BRIDGE", "E", 12, 0, "Liễu bên cầu"),
    ("P-P26", "cozy_tree_blossom_A", "BRIDGE", "H", 12, 0, "Cây hoa — fairy soft"),
    ("P-P27", "cozy_fence_section_A", "BRIDGE", "G", 11, 90, "Lan can mềm tiếp cận cầu"),
    # LOOKOUT + PLAZA extras for street rhythm
    ("P-P28", "cozy_garden_lamp_A", "LOOKOUT", "J", 11, 0, "Đèn tháp vọng"),
    ("P-P29", "cozy_bench_A", "PLAZA", "E", 7, 90, "Ghế quảng trường"),
    ("P-P30", "cozy_flower_cluster_A", "PLAZA", "H", 7, 0, "Vòng hoa plaza"),
]

for pid, oid, dist, col, row, rot, note in PROP_SPECS:
    PLOTS.append(
        make_plot(pid, "prop", oid, dist, [cell_id(col, row)], rot=rot, notes_vi=note)
    )

# --- CHARACTERS (10) — friendly storybook cast spawns ---
CHAR_SPECS = [
    ("P-C01", "CCP-RH-001", "HOME", "G", 5, "Nori / home hub"),
    ("P-C02", "CCP-NW-003", "WORKSHOP", "I", 7, "Thợ xưởng"),
    ("P-C03", "CCP-NS-002", "MARKET", "J", 4, "Người bán chợ"),
    ("P-C04", "CCP-CT-004", "PLAZA", "G", 7, "Bạn ở gazebo"),
    ("P-C05", "SPH-RH-011", "GREENHOUSE", "C", 4, "Người làm vườn"),
    ("P-C06", "OA-RG-021", "WELL", "C", 7, "Gác giếng"),
    ("P-C07", "AC-CO-015", "WINDMILL", "C", 9, "Gác cối xay"),
    ("P-C08", "TD-CT-028", "BARN", "G", 9, "Chăm barn"),
    ("P-C09", "SV-NW-019", "BRIDGE", "G", 12, "Cạnh cầu"),
    ("P-C10", "CCP-RH-001", "LOOKOUT", "J", 10, "Nhìn từ tháp (instance B)"),
]
# Fix C10 if duplicate cast id — use lookout-adjacent cast from grid plan
# Keep as listed; build maps real cast IDs from MOCKUP_SSOT_V2 later.

for pid, oid, dist, col, row, note in CHAR_SPECS:
    PLOTS.append(
        make_plot(
            pid, "character_spawn", oid, dist, [cell_id(col, row)], notes_vi=note
        )
    )

assert len([p for p in PLOTS if p["role"] == "building"]) == 10
assert len([p for p in PLOTS if p["role"] == "prop"]) == 30
assert len([p for p in PLOTS if p["role"] == "character_spawn"]) == 10
assert len(PLOTS) == 50

# Modular repeat plan (how to place MANY same buildings harmoniously)
MODULAR_REPEAT = {
    "principle_vi": (
        "Một family kiến trúc = 1 skeleton + nhiều instance. "
        "Bố trí theo nhịp phố (3DStreet street-edge rhythm), không rải ngẫu nhiên. "
        "Xen palette / cửa / mái để thân thiện, không đơn điệu, không hỗn loạn."
    ),
    "cottage_row_example": {
        "family": "ARCH_COTTAGE",
        "ssot_module": "cozy_house_small_A",
        "pattern": "row_along_z_or_x",
        "spacing_cells": 2,
        "setback_from_path_m": 1.0,
        "palette_sequence": ["cream_rose", "butter_peach", "mint_soft", "sky_lilac"],
        "rule": "Không 2 palette giống nhau liền kề; cùng roof slope; cửa sổ tròn + flower box",
        "future_instances_beyond_mvp": [
            "HOME row west of F4 (cells D4–E5)",
            "HOME row east of G4 (cells H4–I5)",
        ],
        "mvp_instance_count": 1,
        "note": "MVP 10 building slots = 1 cottage prototype; wave sau nhân bản cùng GLB/family",
    },
    "shop_lane_example": {
        "family": "ARCH_SHOP",
        "ssot_module": "cozy_market_stall_A",
        "pattern": "frontage_along_storybook_lane",
        "spacing_cells": 2,
        "awning_height_lock_m": 2.2,
        "palette_sequence": ["strawberry_awning", "honey_awning", "blueberry_awning"],
        "mvp_instance_count": 1,
    },
    "street_furniture_rhythm": {
        "lamp": {"module": "cozy_garden_lamp_A", "every_m": 5.0, "side": "sidewalk"},
        "bench": {"module": "cozy_bench_A", "every_m": 8.0, "side": "plaza_and_market"},
        "flower": {"module": "cozy_flower_cluster_A", "cluster_every_m": 4.0},
        "method_source": "3DStreet sidewalk object density idea — original AIdle modules only",
    },
}

STREETS = {
    "Storybook_Lane": {
        "class": "main_street",
        "segment_type": "seg_storybook_lane",
        "surface": "STONE_PAVER_FLAT",
        "surface_secondary": "WOOD_DECK_FLAT",
        "width_m": 3.0,
        "flat": True,
        "axis": "z",
        "at_x": 5.0,
        "z0": -5.0,
        "z1": 7.0,
        "name": "Storybook Lane (phố chính — đá lát phẳng)",
        "feel": "friendly_shop_rhythm",
    },
    "Cottage_Walk": {
        "class": "residential",
        "segment_type": "seg_cottage_row",
        "surface": "STONE_PAVER_FLAT",
        "surface_secondary": "WOOD_DECK_FLAT",
        "width_m": 2.5,
        "flat": True,
        "axis": "x",
        "at_z": 5.0,
        "x0": -5.0,
        "x1": 5.0,
        "name": "Cottage Walk (đá phẳng + hiên gỗ)",
        "feel": "home_garden_front",
    },
    "Craft_Alley": {
        "class": "alley",
        "segment_type": "seg_craft_alley",
        "surface": "STONE_PAVER_FLAT",
        "surface_secondary": "WOOD_DECK_FLAT",
        "width_m": 2.0,
        "flat": True,
        "axis": "x",
        "at_z": -3.0,
        "x0": 3.0,
        "x1": 11.0,
        "name": "Craft Alley (đá + bệ gỗ xưởng)",
        "feel": "workshop_cozy",
    },
    "Water_Path": {
        "class": "path",
        "segment_type": "seg_water_path",
        "surface": "WOOD_BOARDWALK",
        "surface_secondary": "STONE_PAVER_FLAT",
        "width_m": 2.0,
        "flat": True,
        "axis": "z",
        "at_x": -5.0,
        "z0": -5.0,
        "z1": 5.0,
        "name": "Water Path (ván gỗ boardwalk)",
        "feel": "calm",
    },
    "Mill_Road": {
        "class": "path",
        "segment_type": "seg_mill_road",
        "surface": "STONE_PAVER_FLAT",
        "width_m": 2.0,
        "flat": True,
        "axis": "x",
        "at_z": -7.0,
        "x0": -11.0,
        "x1": 1.0,
        "name": "Mill Road (đá lát phẳng)",
        "feel": "landmark_approach",
    },
    "Bridge_Approach": {
        "class": "path",
        "segment_type": "seg_bridge_approach",
        "surface": "STONE_PAVER_FLAT",
        "surface_secondary": "WOOD_BRIDGE_DECK",
        "width_m": 2.0,
        "flat": True,
        "axis": "z",
        "at_x": 0.0,
        "z0": -11.0,
        "z1": -5.0,
        "name": "Bridge Approach (đá + sàn gỗ cầu)",
        "feel": "journey_in",
    },
    "Cross_Plaza_EW": {
        "class": "connector",
        "segment_type": "seg_storybook_lane",
        "surface": "STONE_PAVER_FLAT",
        "width_m": 2.5,
        "flat": True,
        "axis": "x",
        "at_z": 0.0,
        "x0": -5.0,
        "x1": 5.0,
        "name": "Trục đá ngang qua plaza",
        "feel": "plaza_cross",
    },
    "Cross_Plaza_NS": {
        "class": "connector",
        "segment_type": "seg_storybook_lane",
        "surface": "STONE_PAVER_FLAT",
        "width_m": 2.5,
        "flat": True,
        "axis": "z",
        "at_x": 0.0,
        "z0": -5.0,
        "z1": 5.0,
        "name": "Trục đá dọc qua plaza",
        "feel": "plaza_cross",
    },
    "Garden_Spur": {
        "class": "spur",
        "segment_type": "seg_orchard_lane",
        "surface": "STONE_PAVER_FLAT",
        "width_m": 1.5,
        "flat": True,
        "axis": "x",
        "at_z": 7.0,
        "x0": 0.0,
        "x1": 7.0,
        "name": "Nhánh đá tới vườn nghỉ",
        "feel": "garden_soft",
    },
    "Greenhouse_Spur": {
        "class": "spur",
        "segment_type": "seg_orchard_lane",
        "surface": "STONE_PAVER_FLAT",
        "width_m": 1.5,
        "flat": True,
        "axis": "x",
        "at_z": 6.0,
        "x0": -9.0,
        "x1": -5.0,
        "name": "Nhánh đá tới nhà kính",
        "feel": "farm_soft",
    },
    "Lookout_Spur": {
        "class": "spur",
        "segment_type": "seg_mill_road",
        "surface": "STONE_PAVER_FLAT",
        "width_m": 1.5,
        "flat": True,
        "axis": "x",
        "at_z": -8.0,
        "x0": 5.0,
        "x1": 10.0,
        "name": "Nhánh đá tới tháp vọng",
        "feel": "landmark_approach",
    },
    "Ring_Soft": {
        "class": "ring",
        "segment_type": "seg_orchard_lane",
        "surface": "STONE_PAVER_FLAT",
        "width_m": 1.8,
        "flat": True,
        "shape": "soft_rectangle",
        "bounds": {"min_x": -9, "max_x": 9, "min_z": -9, "max_z": 9},
        "name": "Vành đai đá phẳng (soft ring)",
        "feel": "connect_all_districts",
        "note": "Lát đá bằng phẳng bo góc — cảm giác làng cổ tích, không asphalt",
    },
}

# Explicit path segments for map geometry (stone flat arteries)
# Each: polyline or axis-aligned rect in world units, surface material, width
STONE_PATH_NETWORK = [
    {
        "id": "SP-01",
        "name_vi": "Storybook Lane — đá lát phẳng",
        "surface": "STONE_PAVER_FLAT",
        "width_m": 3.0,
        "flat": True,
        "geometry": "axis_aligned",
        "x0": 3.5, "x1": 6.5, "z0": -5.0, "z1": 7.0,
        "joins": ["SP-03", "SP-04", "WP-03"],
    },
    {
        "id": "SP-02",
        "name_vi": "Cottage Walk — đá lát phẳng",
        "surface": "STONE_PAVER_FLAT",
        "width_m": 2.5,
        "flat": True,
        "geometry": "axis_aligned",
        "x0": -5.0, "x1": 5.0, "z0": 3.75, "z1": 6.25,
        "joins": ["SP-04", "SP-08"],
    },
    {
        "id": "SP-03",
        "name_vi": "Craft Alley — đá lát phẳng",
        "surface": "STONE_PAVER_FLAT",
        "width_m": 2.0,
        "flat": True,
        "geometry": "axis_aligned",
        "x0": 3.0, "x1": 11.0, "z0": -4.0, "z1": -2.0,
        "joins": ["SP-01", "SP-11"],
    },
    {
        "id": "SP-04",
        "name_vi": "Trục đá ngang plaza (Đông–Tây)",
        "surface": "STONE_PAVER_FLAT",
        "width_m": 2.5,
        "flat": True,
        "geometry": "axis_aligned",
        "x0": -5.0, "x1": 5.0, "z0": -1.25, "z1": 1.25,
        "joins": ["SP-05", "SP-01", "SP-06", "SP-RING"],
    },
    {
        "id": "SP-05",
        "name_vi": "Trục đá dọc plaza (Bắc–Nam)",
        "surface": "STONE_PAVER_FLAT",
        "width_m": 2.5,
        "flat": True,
        "geometry": "axis_aligned",
        "x0": -1.25, "x1": 1.25, "z0": -5.0, "z1": 5.0,
        "joins": ["SP-04", "SP-02", "SP-07", "SP-09"],
    },
    {
        "id": "SP-06",
        "name_vi": "Nối đá plaza → boardwalk giếng",
        "surface": "STONE_PAVER_FLAT",
        "width_m": 1.8,
        "flat": True,
        "geometry": "axis_aligned",
        "x0": -7.0, "x1": -5.0, "z0": -1.0, "z1": 1.0,
        "joins": ["SP-04", "WB-01"],
    },
    {
        "id": "SP-07",
        "name_vi": "Mill Road — đá lát phẳng",
        "surface": "STONE_PAVER_FLAT",
        "width_m": 2.0,
        "flat": True,
        "geometry": "axis_aligned",
        "x0": -11.0, "x1": 1.0, "z0": -8.0, "z1": -6.0,
        "joins": ["SP-05", "SP-09", "SP-RING"],
    },
    {
        "id": "SP-08",
        "name_vi": "Nhánh đá vườn nghỉ",
        "surface": "STONE_PAVER_FLAT",
        "width_m": 1.5,
        "flat": True,
        "geometry": "axis_aligned",
        "x0": 0.0, "x1": 7.0, "z0": 6.25, "z1": 7.75,
        "joins": ["SP-02", "SP-01"],
    },
    {
        "id": "SP-09",
        "name_vi": "Bridge Approach — đá phẳng",
        "surface": "STONE_PAVER_FLAT",
        "width_m": 2.0,
        "flat": True,
        "geometry": "axis_aligned",
        "x0": -1.0, "x1": 1.0, "z0": -11.0, "z1": -5.0,
        "joins": ["SP-05", "SP-07", "WD-BRIDGE"],
    },
    {
        "id": "SP-10",
        "name_vi": "Nhánh đá nhà kính",
        "surface": "STONE_PAVER_FLAT",
        "width_m": 1.5,
        "flat": True,
        "geometry": "axis_aligned",
        "x0": -9.0, "x1": -5.0, "z0": 5.25, "z1": 6.75,
        "joins": ["SP-RING", "WB-01"],
    },
    {
        "id": "SP-11",
        "name_vi": "Nhánh đá tháp vọng",
        "surface": "STONE_PAVER_FLAT",
        "width_m": 1.5,
        "flat": True,
        "geometry": "axis_aligned",
        "x0": 5.0, "x1": 10.0, "z0": -8.75, "z1": -7.25,
        "joins": ["SP-01", "SP-03", "SP-RING"],
    },
    {
        "id": "SP-RING",
        "name_vi": "Vành đai đá phẳng (4 cạnh soft rect)",
        "surface": "STONE_PAVER_FLAT",
        "width_m": 1.8,
        "flat": True,
        "geometry": "ring_rect",
        "bounds": {"min_x": -9.0, "max_x": 9.0, "min_z": -9.0, "max_z": 9.0},
        "joins": ["SP-01", "SP-04", "SP-07", "SP-10", "SP-11"],
        "note": "Bo góc cảm giác làng — vẫn mặt phẳng 0°",
    },
    {
        "id": "SP-PLAZA-RING",
        "name_vi": "Vòng đá quanh gazebo",
        "surface": "STONE_RING_PLAZA",
        "width_m": 1.2,
        "flat": True,
        "geometry": "ring_ellipse",
        "center": {"x": 0.0, "z": 0.0},
        "rx": 3.2,
        "rz": 2.6,
        "joins": ["SP-04", "SP-05", "WD-GAZEBO"],
    },
]

# Wooden platforms / decks / boardwalks (bệ gỗ)
WOOD_PLATFORMS = [
    {
        "id": "WD-GAZEBO",
        "name_vi": "Bệ gỗ dưới gazebo (plaza)",
        "surface": "WOOD_DECK_FLAT",
        "flat": True,
        "geometry": "rect",
        "x0": -1.6, "x1": 1.6, "z0": -1.6, "z1": 1.6,
        "plank_axis": "x",
        "height_above_path_m": 0.08,
        "district": "PLAZA",
        "serves": "cozy_gazebo_A",
    },
    {
        "id": "WD-COTTAGE",
        "name_vi": "Bệ gỗ hiên cottage",
        "surface": "WOOD_DECK_FLAT",
        "flat": True,
        "geometry": "rect",
        "x0": -1.2, "x1": 1.2, "z0": 3.2, "z1": 4.4,
        "plank_axis": "x",
        "height_above_path_m": 0.1,
        "district": "HOME",
        "serves": "cozy_house_small_A",
    },
    {
        "id": "WD-SHOP",
        "name_vi": "Bệ gỗ mặt tiền chợ",
        "surface": "WOOD_DECK_FLAT",
        "flat": True,
        "geometry": "rect",
        "x0": 6.6, "x1": 8.4, "z0": 3.4, "z1": 6.6,
        "plank_axis": "z",
        "height_above_path_m": 0.08,
        "district": "MARKET",
        "serves": "cozy_market_stall_A",
    },
    {
        "id": "WD-WORKSHOP",
        "name_vi": "Bệ gỗ sân xưởng",
        "surface": "WOOD_DECK_FLAT",
        "flat": True,
        "geometry": "rect",
        "x0": 7.6, "x1": 10.4, "z0": -4.8, "z1": -3.2,
        "plank_axis": "x",
        "height_above_path_m": 0.1,
        "district": "WORKSHOP",
        "serves": "cozy_workshop_A",
    },
    {
        "id": "WD-WELL",
        "name_vi": "Bệ gỗ quanh nhà giếng",
        "surface": "WOOD_DECK_FLAT",
        "flat": True,
        "geometry": "rect",
        "x0": -8.2, "x1": -5.8, "z0": -1.2, "z1": 1.2,
        "plank_axis": "z",
        "height_above_path_m": 0.08,
        "district": "WELL",
        "serves": "cozy_well_house_A",
    },
    {
        "id": "WB-01",
        "name_vi": "Boardwalk gỗ ven nước (N–S)",
        "surface": "WOOD_BOARDWALK",
        "flat": True,
        "geometry": "rect",
        "x0": -6.0, "x1": -4.0, "z0": -5.0, "z1": 5.0,
        "plank_axis": "x",
        "height_above_path_m": 0.06,
        "district": "WELL",
        "serves": "water_edge_walk",
    },
    {
        "id": "WD-GREENHOUSE",
        "name_vi": "Bệ gỗ cửa nhà kính",
        "surface": "WOOD_DECK_FLAT",
        "flat": True,
        "geometry": "rect",
        "x0": -8.4, "x1": -5.6, "z0": 4.0, "z1": 5.2,
        "plank_axis": "x",
        "height_above_path_m": 0.08,
        "district": "GREENHOUSE",
        "serves": "cozy_greenhouse_A",
    },
    {
        "id": "WD-WINDMILL",
        "name_vi": "Bệ gỗ chân cối xay",
        "surface": "WOOD_DECK_FLAT",
        "flat": True,
        "geometry": "rect",
        "x0": -9.2, "x1": -6.8, "z0": -8.2, "z1": -6.0,
        "plank_axis": "x",
        "height_above_path_m": 0.1,
        "district": "WINDMILL",
        "serves": "cozy_windmill_A",
    },
    {
        "id": "WD-BARN",
        "name_vi": "Bệ gỗ sân barn",
        "surface": "WOOD_DECK_FLAT",
        "flat": True,
        "geometry": "rect",
        "x0": -1.4, "x1": 1.4, "z0": -8.4, "z1": -7.0,
        "plank_axis": "x",
        "height_above_path_m": 0.1,
        "district": "BARN",
        "serves": "cozy_barn_small_A",
    },
    {
        "id": "WD-BRIDGE",
        "name_vi": "Mặt sàn gỗ cầu vòm",
        "surface": "WOOD_BRIDGE_DECK",
        "flat": True,
        "geometry": "rect",
        "x0": -1.4, "x1": 1.4, "z0": -11.2, "z1": -9.6,
        "plank_axis": "x",
        "height_above_path_m": 0.12,
        "district": "BRIDGE",
        "serves": "cozy_bridge_arch_A",
    },
    {
        "id": "WD-LOOKOUT",
        "name_vi": "Bệ gỗ chân tháp vọng",
        "surface": "WOOD_DECK_FLAT",
        "flat": True,
        "geometry": "rect",
        "x0": 8.0, "x1": 10.4, "z0": -9.4, "z1": -7.2,
        "plank_axis": "z",
        "height_above_path_m": 0.1,
        "district": "LOOKOUT",
        "serves": "cozy_watchtower_A",
    },
    {
        "id": "WD-GARDEN",
        "name_vi": "Bệ gỗ góc vườn nghỉ",
        "surface": "WOOD_DECK_FLAT",
        "flat": True,
        "geometry": "rect",
        "x0": 3.0, "x1": 5.0, "z0": 6.2, "z1": 7.8,
        "plank_axis": "x",
        "height_above_path_m": 0.08,
        "district": "GARDEN",
        "serves": "bench_nook",
    },
]

SURFACE_LAYERING = {
    "order_bottom_to_top": [
        "terrain_lawn",
        "STONE_PAVER_FLAT / STONE_RING_PLAZA",
        "WOOD_BOARDWALK / WOOD_DECK_FLAT",
        "WOOD_BRIDGE_DECK",
        "props_and_furniture",
        "buildings",
    ],
    "rule_vi": (
        "Đá lát luôn mặt phẳng 0° làm lớp đi chính. "
        "Bệ gỗ nằm trên / sát path, cao thêm chút để đọc mép, vẫn coi là walkable flat. "
        "Boardwalk ven nước thay đá ở đoạn WELL. "
        "Junction: đá–gỗ dùng mép bo tròn, không bậc cao."
    ),
    "ssot_modules": {
        "stone": "cozy_path_stone_A (+ future path strip variants)",
        "wood_deck": "design: cozy_wood_deck_A (chưa có GLB — design slot)",
        "boardwalk": "design: cozy_boardwalk_A (chưa có GLB — design slot)",
        "bridge_wood": "part of cozy_bridge_arch_A mesh",
    },
}

HARMONY = {
    "title_vi": "Quy tắc bố trí hài hòa & thân thiện",
    "rules": [
        {
            "id": "H1",
            "vi": "Cùng family → cùng silhouette mái / tỉ lệ cửa sổ — chỉ đổi màu & chi tiết nhỏ",
        },
        {
            "id": "H2",
            "vi": "Nhịp mặt phố: building–gap–building đều (2m cell) — không dồn cụm rồi để trống",
        },
        {
            "id": "H3",
            "vi": "Vỉa hè + cây/đèn/hoa tạo “đệm thân thiện” giữa path và tường nhà",
        },
        {
            "id": "H4",
            "vi": "Landmark (cối xay, tháp) đối xứng góc — không cạnh nhau che tầm nhìn",
        },
        {
            "id": "H5",
            "vi": "Tâm plaza mở — gazebo thấp, sightline xuyên 4 hướng",
        },
        {
            "id": "H6",
            "vi": "Palette pastel ấm; tránh neon / harsh cyber trên facade (cyber chỉ accent nhỏ)",
        },
        {
            "id": "H7",
            "vi": "Scale trẻ em/storybook: cửa cao ~1.1–1.3 unit relative, không brutalist",
        },
        {
            "id": "H8",
            "vi": "Lặp module có chủ đích (production-friendly) nhưng cảm giác “ngôi làng sống”, không clone cứng",
        },
        {
            "id": "H9",
            "vi": "Mọi đường đi = mặt phẳng 0°; trục chính/vành đai/hẻm = đá lát; bệ gỗ trước cửa & boardwalk ven nước — mép bo, không bậc cao",
        },
        {
            "id": "H10",
            "vi": "Đá–gỗ nối liền mạch (junction soft); thớ gỗ song song cạnh dài bệ; paver không gồ gameplay",
        },
    ],
    "disney_feel_without_ip": [
        "Storybook proportions (mái dốc, cửa sổ tròn, chimney soft)",
        "Village green + main street + cottage row archetypes (public domain urban form)",
        "Warm friendly lighting mood",
        "KHÔNG: logo, nhân vật, tên phim, castle replica Disney",
    ],
}

REF_3DSTREET = {
    "repo": "https://github.com/3DStreet/3dstreet",
    "license_note": "AGPL-3.0 codebase; assets often CC-BY-NC — do NOT vendor into AIdle commercial tree without counsel",
    "methods_adopted": [
        "Street as layered segments (path / sidewalk / edge objects)",
        "Building variants along street edge",
        "Modular street furniture density",
        "Rapid layout from plan JSON → 3D instances",
    ],
    "methods_NOT_copied": [
        "A-Frame components / source",
        "3DStreet GLB/texture assets",
        "Streetmix JSON import pipeline",
    ],
    "aidle_mapping": {
        "street_segments": "game town path modules + future street_segment schema",
        "building_variants": "arch_family + palette_variant on plot",
        "runtime": "Godot P1E cozy modules / Foundry IDs — not A-Frame",
    },
}


def build_json() -> dict:
    role_counts = {
        "building": sum(1 for p in PLOTS if p["role"] == "building"),
        "prop": sum(1 for p in PLOTS if p["role"] == "prop"),
        "character_spawn": sum(1 for p in PLOTS if p["role"] == "character_spawn"),
    }
    doc = {
        "schema_version": "town_fairy_street_plan/1.1",
        "plan_id": PLAN_ID,
        "title": "Thị trấn Cổ tích Thân thiện — Storybook Street Town",
        "title_en": "Friendly Fairy-Tale Street Town (flat stone paths + wood decks)",
        "status": "DESIGN_FAIRY_STREET_ACTIVE",
        "accepted": False,
        "self_accept": False,
        "authority": "REPORT_ONLY | design parent — no game/** patch",
        "mockup_ssot": "MOCKUP_SSOT_V2",
        "world_profile": "cozy_cyber_pixel",
        "planning_style": "modular_fairy_street_with_flat_stone_and_wood_surfaces",
        "planning_style_vi": (
            "Phố cổ tích modular + mạng đường đá lát phẳng 0° + bệ/ván gỗ trước cửa & ven nước. "
            "Segment 3DStreet-style · family kiến trúc lặp · palette xen kẽ · plaza mềm."
        ),
        "revision_note": "v1.1: add STONE_PATH_NETWORK + WOOD_PLATFORMS + surface materials (user request flat paved stone + wood decks)",
        "coordinate_convention": "game_godot: x=east, z=north, y=up; rotation_deg about y",
        "fits_map": {
            "content_bounds": {
                "min": {"x": -11.5, "z": -11.5},
                "max": {"x": 11.5, "z": 11.5},
            },
            "cadastre_bounds": {
                "min": {"x": -12, "z": -12},
                "max": {"x": 12, "z": 12},
            },
            "note": "Fits current starter realm ±12.",
        },
        "grid": {
            "pattern": "soft_grid_with_street_segments",
            "cell_size_units": 2.0,
            "cols": COLS,
            "rows": ROWS,
            "origin": "A1 = NW (-11,+11); L12 = SE (+11,-11)",
            "label_format": "COLROW e.g. G7",
        },
        "reference_3dstreet": REF_3DSTREET,
        "architecture_families": ARCH_FAMILIES,
        "surface_materials": SURFACE_MATERIALS,
        "surface_layering": SURFACE_LAYERING,
        "street_segments": STREET_SEGMENTS,
        "streets": STREETS,
        "stone_path_network": STONE_PATH_NETWORK,
        "wood_platforms": WOOD_PLATFORMS,
        "modular_repeat": MODULAR_REPEAT,
        "harmony": HARMONY,
        "palette": PALETTE,
        "districts": DISTRICTS,
        "counts": {
            **role_counts,
            "stone_path_segments": len(STONE_PATH_NETWORK),
            "wood_platforms": len(WOOD_PLATFORMS),
        },
        "plots": PLOTS,
        "relation_to_prior_plans": {
            "TOWN_GRID_PLAN_V1": "legal cadastre 50 plots — still SSOT for cells if Human keeps",
            "TOWN_MASTERPLAN_MOCKUP_V1": "district illustration on grid",
            "TOWN_CHESSBOARD_PLAN_V1": "orthogonal city — harsher; this plan is softer storybook",
            "TOWN_FAIRY_STREET_PLAN_V1": "recommended design direction for friendly fairy-tale town",
        },
        "html": f"{PLAN_ID}.html",
        "svg": f"{PLAN_ID}.svg",
        "readme": f"{PLAN_ID}_README.md",
    }
    raw = json.dumps(doc, sort_keys=True, ensure_ascii=False)
    doc["content_sha256"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return doc


def svg_map(doc: dict) -> str:
    # map world ±12 → SVG 40..860
    def W(x: float) -> float:
        return 40 + (x + 12) * (800 / 24)

    def H(z: float) -> float:
        # z+ north → top
        return 40 + (12 - z) * (800 / 24)

    def rect_wz(x0: float, z0: float, x1: float, z1: float) -> tuple[float, float, float, float]:
        """World AABB → SVG x,y,w,h (z+ north = top)."""
        sx0, sx1 = W(min(x0, x1)), W(max(x0, x1))
        # SVG y increases down; H(z+) is smaller
        sy_top, sy_bot = H(max(z0, z1)), H(min(z0, z1))
        return sx0, sy_top, sx1 - sx0, sy_bot - sy_top

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 980" font-family="Segoe UI, system-ui, sans-serif">',
        f'<rect width="900" height="980" fill="{PALETTE["paper"]}"/>',
        f'<text x="450" y="26" text-anchor="middle" font-size="18" font-weight="700" fill="{PALETTE["ink"]}">AIdle · Thị trấn Cổ tích — đường đá phẳng + bệ gỗ</text>',
        f'<text x="450" y="44" text-anchor="middle" font-size="11" fill="#666">{PLAN_ID} · flat stone pavers · wood decks/boardwalk · design only</text>',
        # patterns
        f'''<defs>
  <pattern id="paver" width="8" height="8" patternUnits="userSpaceOnUse">
    <rect width="8" height="8" fill="{PALETTE["stone_paver"]}"/>
    <path d="M0 0H8M0 8H8M0 0V8M8 0V8" stroke="{PALETTE["stone_joint"]}" stroke-width="0.6" opacity="0.55"/>
  </pattern>
  <pattern id="woodX" width="6" height="10" patternUnits="userSpaceOnUse">
    <rect width="6" height="10" fill="{PALETTE["wood_deck"]}"/>
    <line x1="0" y1="0" x2="0" y2="10" stroke="{PALETTE["wood_plank_line"]}" stroke-width="0.9" opacity="0.5"/>
  </pattern>
  <pattern id="woodZ" width="10" height="6" patternUnits="userSpaceOnUse">
    <rect width="10" height="6" fill="{PALETTE["wood_boardwalk"]}"/>
    <line x1="0" y1="0" x2="10" y2="0" stroke="{PALETTE["wood_plank_line"]}" stroke-width="0.9" opacity="0.5"/>
  </pattern>
</defs>''',
    ]

    # chessboard cells faint (under surfaces)
    for col in COLS:
        for row in ROWS:
            x, z = cell_center(col, row)
            tone = "#f0e6d6" if (COLS.index(col) + row) % 2 == 0 else "#e8dcc8"
            parts.append(
                f'<rect x="{W(x-1):.1f}" y="{H(z+1):.1f}" width="{W(x+1)-W(x-1):.1f}" '
                f'height="{H(z-1)-H(z+1):.1f}" fill="{tone}" opacity="0.28"/>'
            )

    # plaza lawn under
    parts.append(
        f'<ellipse cx="{W(0):.1f}" cy="{H(0):.1f}" rx="78" ry="64" fill="{PALETTE["plaza"]}" opacity="0.75"/>'
    )

    # --- STONE PATH NETWORK (flat pavers) ---
    parts.append('<g id="stone-paths">')
    for sp in STONE_PATH_NETWORK:
        geom = sp.get("geometry")
        if geom == "axis_aligned":
            x, y, w, h = rect_wz(sp["x0"], sp["z0"], sp["x1"], sp["z1"])
            parts.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
                f'rx="4" fill="url(#paver)" stroke="{PALETTE["stone_joint"]}" stroke-width="1" opacity="0.95"/>'
            )
            # id label at center
            cx = (sp["x0"] + sp["x1"]) / 2
            cz = (sp["z0"] + sp["z1"]) / 2
            parts.append(
                f'<text x="{W(cx):.1f}" y="{H(cz):.1f}" text-anchor="middle" font-size="7" '
                f'fill="#5a5040" opacity="0.75">{escape(sp["id"])}</text>'
            )
        elif geom == "ring_rect":
            b = sp["bounds"]
            # 4 strips as stroke-rect
            parts.append(
                f'<rect x="{W(b["min_x"]):.1f}" y="{H(b["max_z"]):.1f}" '
                f'width="{W(b["max_x"])-W(b["min_x"]):.1f}" height="{H(b["min_z"])-H(b["max_z"]):.1f}" '
                f'rx="40" fill="none" stroke="url(#paver)" stroke-width="14" opacity="0.9"/>'
            )
            parts.append(
                f'<rect x="{W(b["min_x"]):.1f}" y="{H(b["max_z"]):.1f}" '
                f'width="{W(b["max_x"])-W(b["min_x"]):.1f}" height="{H(b["min_z"])-H(b["max_z"]):.1f}" '
                f'rx="40" fill="none" stroke="{PALETTE["stone_joint"]}" stroke-width="1.2" opacity="0.5"/>'
            )
        elif geom == "ring_ellipse":
            c = sp["center"]
            rx = abs(W(c["x"] + sp["rx"]) - W(c["x"]))
            rz = abs(H(c["z"] - sp["rz"]) - H(c["z"]))
            parts.append(
                f'<ellipse cx="{W(c["x"]):.1f}" cy="{H(c["z"]):.1f}" rx="{rx:.1f}" ry="{rz:.1f}" '
                f'fill="none" stroke="url(#paver)" stroke-width="12" opacity="0.95"/>'
            )
    parts.append("</g>")

    # --- WOOD PLATFORMS ---
    parts.append('<g id="wood-platforms">')
    for wd in WOOD_PLATFORMS:
        x, y, w, h = rect_wz(wd["x0"], wd["z0"], wd["x1"], wd["z1"])
        fill = "url(#woodX)" if wd.get("plank_axis") == "x" else "url(#woodZ)"
        if wd["surface"] == "WOOD_BRIDGE_DECK":
            stroke = PALETTE["wood_deck_dark"]
        elif wd["surface"] == "WOOD_BOARDWALK":
            stroke = PALETTE["wood_plank_line"]
        else:
            stroke = PALETTE["wood_plank_line"]
        parts.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="3" fill="{fill}" stroke="{stroke}" stroke-width="1.2" opacity="0.92"/>'
        )
        cx = (wd["x0"] + wd["x1"]) / 2
        cz = (wd["z0"] + wd["z1"]) / 2
        parts.append(
            f'<text x="{W(cx):.1f}" y="{H(cz)+3:.1f}" text-anchor="middle" font-size="6.5" '
            f'fill="#4a3820" font-weight="600">{escape(wd["id"])}</text>'
        )
    parts.append("</g>")

    # district name labels (light)
    for d in DISTRICTS:
        cx, cz = d["center"]["x"], d["center"]["z"]
        parts.append(
            f'<text x="{W(cx):.1f}" y="{H(cz)-36:.1f}" text-anchor="middle" font-size="9" '
            f'font-weight="600" fill="{PALETTE["ink"]}" opacity="0.7">{escape(d["name"])}</text>'
        )

    # plots on top
    for p in PLOTS:
        x, z = p["position"]["x"], p["position"]["z"]
        role = p["role"]
        if role == "building":
            fam = p.get("arch_family", "")
            col = {
                "ARCH_COTTAGE": PALETTE["cottage"],
                "ARCH_SHOP": PALETTE["shop"],
                "ARCH_WORKSHOP": PALETTE["workshop"],
                "ARCH_GAZEBO": "#e8d48a",
                "ARCH_GREENHOUSE": PALETTE["greenhouse"],
                "ARCH_WELL": PALETTE["well"],
                "ARCH_WINDMILL": PALETTE["windmill"],
                "ARCH_BARN": PALETTE["barn"],
                "ARCH_BRIDGE": PALETTE["bridge"],
                "ARCH_LOOKOUT": PALETTE["lookout"],
            }.get(fam, "#ccc")
            px, py = W(x), H(z)
            parts.append(
                f'<g transform="translate({px:.1f},{py:.1f})">'
                f'<polygon points="0,-16 -12,-3 12,-3" fill="{col}" stroke="{PALETTE["ink"]}" stroke-width="1"/>'
                f'<rect x="-10" y="-3" width="20" height="14" rx="3" fill="{col}" stroke="{PALETTE["ink"]}" stroke-width="1"/>'
                f'<rect x="-2.5" y="2" width="5" height="9" fill="#5c4033" opacity="0.85"/>'
                f'<text y="24" text-anchor="middle" font-size="7.5" fill="{PALETTE["ink"]}">{escape(p["plot_id"])}</text>'
                f"</g>"
            )
        elif role == "prop":
            parts.append(
                f'<circle cx="{W(x):.1f}" cy="{H(z):.1f}" r="4.5" fill="{PALETTE["accent_butter"]}" stroke="#b89b3a" stroke-width="0.8"/>'
            )
        else:
            parts.append(
                f'<circle cx="{W(x):.1f}" cy="{H(z):.1f}" r="5.5" fill="{PALETTE["accent_lilac"]}" stroke="#6a5a8a" stroke-width="1"/>'
            )

    # legend
    ly = 900
    parts.append(f'<text x="40" y="{ly}" font-size="11" font-weight="700" fill="{PALETTE["ink"]}">Chú giải bề mặt & đối tượng</text>')
    parts.append(f'<rect x="40" y="{ly+10}" width="36" height="14" rx="3" fill="url(#paver)" stroke="{PALETTE["stone_joint"]}"/>')
    parts.append(f'<text x="82" y="{ly+21}" font-size="10" fill="#444">Đá lát phẳng (STONE path)</text>')
    parts.append(f'<rect x="230" y="{ly+10}" width="36" height="14" rx="3" fill="url(#woodX)" stroke="{PALETTE["wood_plank_line"]}"/>')
    parts.append(f'<text x="272" y="{ly+21}" font-size="10" fill="#444">Bệ / ván gỗ (WOOD deck)</text>')
    parts.append(f'<polygon points="430,{ly+10} 418,{ly+24} 442,{ly+24}" fill="{PALETTE["cottage"]}"/>')
    parts.append(f'<text x="450" y="{ly+21}" font-size="10" fill="#444">Building</text>')
    parts.append(f'<circle cx="530" cy="{ly+17}" r="5" fill="{PALETTE["accent_butter"]}"/>')
    parts.append(f'<text x="542" y="{ly+21}" font-size="10" fill="#444">Prop</text>')
    parts.append(f'<circle cx="600" cy="{ly+17}" r="5.5" fill="{PALETTE["accent_lilac"]}"/>')
    parts.append(f'<text x="612" y="{ly+21}" font-size="10" fill="#444">Cast</text>')
    parts.append(
        f'<text x="450" y="950" text-anchor="middle" font-size="10" fill="#666">'
        f'{len(STONE_PATH_NETWORK)} stone segments · {len(WOOD_PLATFORMS)} wood platforms · slope 0° · accepted=false</text>'
    )
    parts.append(
        f'<text x="450" y="968" text-anchor="middle" font-size="9" fill="#999">'
        f'Design Parent · no game/** · 3DStreet method only (no AGPL assets)</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts)


def html_page(doc: dict) -> str:
    dist_cards = []
    for d in DISTRICTS:
        dist_cards.append(
            f"""<article class="card" style="border-color:{d['color']}">
  <h3>{escape(d['name'])}</h3>
  <p class="muted">{escape(d.get('name_en',''))}</p>
  <p>{escape(d['function_vi'])}</p>
  <p class="tag">segment: {escape(d['street_segment'])}</p>
  <p class="tag">arch: {escape(d['arch_primary'])}</p>
</article>"""
        )

    arch_rows = []
    for fid, f in ARCH_FAMILIES.items():
        arch_rows.append(
            f"<tr><td><code>{escape(fid)}</code></td><td>{escape(f['name_vi'])}</td>"
            f"<td><code>{escape(f['ssot_primary'])}</code></td>"
            f"<td>{'✓ lặp' if f['repeatable'] else 'landmark'}</td>"
            f"<td>{escape(', '.join(f['palette_variants'][:3]))}</td></tr>"
        )

    plot_rows = []
    for p in PLOTS:
        arch = p.get("arch_family", "—")
        plot_rows.append(
            f"<tr data-role=\"{p['role']}\"><td>{escape(p['plot_id'])}</td>"
            f"<td>{escape(p['role'])}</td><td><code>{escape(p['object_id'])}</code></td>"
            f"<td>{escape(p['district'])}</td><td>{escape(str(arch))}</td>"
            f"<td>({p['position']['x']}, {p['position']['z']})</td>"
            f"<td>{escape(p.get('notes_vi',''))}</td></tr>"
        )

    harmony_li = "".join(f"<li><strong>{escape(r['id'])}</strong> — {escape(r['vi'])}</li>" for r in HARMONY["rules"])

    mat_rows = []
    for mid, m in SURFACE_MATERIALS.items():
        mat_rows.append(
            f"<tr><td><code>{escape(mid)}</code></td><td>{escape(m['name_vi'])}</td>"
            f"<td>{'✓ phẳng 0°' if m.get('flat') else '—'}</td>"
            f"<td><code>{escape(str(m.get('module_hint','')))}</code></td>"
            f"<td>{escape(m.get('use_vi',''))}</td></tr>"
        )

    stone_rows = []
    for sp in STONE_PATH_NETWORK:
        stone_rows.append(
            f"<tr><td><code>{escape(sp['id'])}</code></td><td>{escape(sp['name_vi'])}</td>"
            f"<td>{sp.get('width_m','—')}</td><td>{escape(sp.get('geometry',''))}</td>"
            f"<td>{'✓' if sp.get('flat') else '—'}</td></tr>"
        )

    wood_rows = []
    for wd in WOOD_PLATFORMS:
        wood_rows.append(
            f"<tr><td><code>{escape(wd['id'])}</code></td><td>{escape(wd['name_vi'])}</td>"
            f"<td>{escape(wd['surface'])}</td><td>{escape(wd.get('district',''))}</td>"
            f"<td>{escape(str(wd.get('serves','')))}</td>"
            f"<td>+{wd.get('height_above_path_m',0)}m</td></tr>"
        )

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{PLAN_ID} — Thị trấn Cổ tích Thân thiện</title>
<style>
  :root {{
    --paper: {PALETTE['paper']};
    --ink: {PALETTE['ink']};
    --path: {PALETTE['path']};
    --plaza: {PALETTE['plaza']};
    --rose: {PALETTE['accent_rose']};
    --lilac: {PALETTE['accent_lilac']};
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; font-family: "Segoe UI", system-ui, sans-serif;
    background: linear-gradient(165deg, #e8f4fc 0%, var(--paper) 40%, #f7ebe0 100%);
    color: var(--ink); line-height: 1.5;
  }}
  header {{
    padding: 1.5rem 1.25rem 1rem; text-align: center;
    background: radial-gradient(ellipse at 50% 0%, #fff8e8 0%, transparent 60%);
  }}
  h1 {{ margin: 0 0 .35rem; font-size: 1.65rem; letter-spacing: -0.02em; }}
  .sub {{ color: #5a5550; max-width: 48rem; margin: 0 auto; }}
  .badge {{
    display: inline-block; margin: .5rem .25rem; padding: .2rem .6rem;
    border-radius: 999px; background: #fff; border: 1px solid #e0d5c4;
    font-size: .75rem;
  }}
  .badge.warn {{ background: #fff3cd; border-color: #e0c36a; }}
  main {{ max-width: 1100px; margin: 0 auto; padding: 0 1rem 3rem; }}
  section {{
    background: rgba(255,255,255,.72); border: 1px solid #eadfce;
    border-radius: 16px; padding: 1.1rem 1.25rem; margin: 1rem 0;
    box-shadow: 0 8px 24px rgba(80,60,40,.06);
  }}
  h2 {{ margin: 0 0 .75rem; font-size: 1.15rem; }}
  .map-wrap {{
    background: #fff; border-radius: 12px; overflow: auto;
    border: 1px solid #e5d9c6; max-height: 70vh;
  }}
  .map-wrap img {{ width: 100%; height: auto; display: block; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: .75rem; }}
  .card {{
    background: #fff; border-radius: 12px; padding: .75rem .9rem;
    border: 2px solid #ddd;
  }}
  .card h3 {{ margin: 0 0 .25rem; font-size: .95rem; }}
  .muted {{ color: #777; font-size: .8rem; margin: 0 0 .4rem; }}
  .tag {{
    display: inline-block; font-size: .72rem; background: #f3ebe0;
    padding: .1rem .4rem; border-radius: 6px; margin: .15rem .15rem 0 0;
  }}
  table {{ width: 100%; border-collapse: collapse; font-size: .82rem; }}
  th, td {{ border-bottom: 1px solid #efe6d8; padding: .4rem .35rem; text-align: left; vertical-align: top; }}
  th {{ background: #f7f0e6; position: sticky; top: 0; }}
  code {{ font-size: .78rem; background: #f0ebe3; padding: .05rem .25rem; border-radius: 4px; }}
  .filters button {{
    margin: 0 .25rem .5rem 0; padding: .35rem .7rem; border-radius: 999px;
    border: 1px solid #d8cbb8; background: #fff; cursor: pointer; font-size: .8rem;
  }}
  .filters button.active {{ background: #3d3a36; color: #fff; }}
  ul.rules {{ padding-left: 1.1rem; }}
  ul.rules li {{ margin: .35rem 0; }}
  footer {{ text-align: center; color: #888; font-size: .8rem; padding: 1rem; }}
  a {{ color: #3a6d8c; }}
  .callout {{
    background: linear-gradient(90deg, #fff5f7, #f5f0ff);
    border-left: 4px solid var(--rose);
    padding: .75rem 1rem; border-radius: 0 12px 12px 0; margin: .5rem 0;
  }}
</style>
</head>
<body>
<header>
  <h1>🏡 Thị trấn Cổ tích Thân thiện</h1>
  <p class="sub">Quy hoạch <strong>storybook street town</strong> + <strong>đường đá lát phẳng</strong> +
  <strong>bệ / ván gỗ</strong> — modular (ý 3DStreet), kiến trúc lặp hài hòa, plaza mềm.
  Cảm giác cổ tích thân thiện <em>không dùng IP Disney</em>.</p>
  <span class="badge">{PLAN_ID}</span>
  <span class="badge">MOCKUP_SSOT_V2 · 50 plots</span>
  <span class="badge">{len(STONE_PATH_NETWORK)} stone · {len(WOOD_PLATFORMS)} wood</span>
  <span class="badge warn">accepted=false · design only</span>
</header>
<main>
  <section>
    <h2>Bản đồ (đá + gỗ hiển thị rõ)</h2>
    <div class="map-wrap">
      <img src="{PLAN_ID}.svg" alt="Fairy street town map with stone paths and wood decks"/>
    </div>
    <p style="font-size:.85rem;color:#666">
      <a href="{PLAN_ID}.svg" target="_blank">SVG</a> ·
      <a href="{PLAN_ID}.json" target="_blank">JSON</a> ·
      <a href="{PLAN_ID}_README.md" target="_blank">README</a>
    </p>
  </section>

  <section>
    <h2>Bề mặt đi — đá lát phẳng &amp; bệ gỗ</h2>
    <div class="callout">
      <strong>Mọi path = slope 0° (bằng phẳng).</strong>
      Trục chính / vành đai / hẻm = <em>đá lát</em> (paver soft).
      Trước cửa nhà, shop, giếng, tháp = <em>bệ gỗ</em>.
      Ven nước = <em>boardwalk ván gỗ</em>. Cầu = mặt sàn gỗ trên đá tiếp cận.
    </div>
    <p class="muted">{escape(SURFACE_LAYERING['rule_vi'])}</p>
    <h3 style="font-size:1rem;margin:1rem 0 .5rem">Vật liệu</h3>
    <div style="overflow:auto">
    <table>
      <thead><tr><th>ID</th><th>Tên</th><th>Phẳng?</th><th>Module hint</th><th>Dùng</th></tr></thead>
      <tbody>{''.join(mat_rows)}</tbody>
    </table>
    </div>
    <h3 style="font-size:1rem;margin:1rem 0 .5rem">Mạng đường đá ({len(STONE_PATH_NETWORK)} segment)</h3>
    <div style="overflow:auto;max-height:280px">
    <table>
      <thead><tr><th>ID</th><th>Tên</th><th>Rộng (m)</th><th>Geometry</th><th>Flat</th></tr></thead>
      <tbody>{''.join(stone_rows)}</tbody>
    </table>
    </div>
    <h3 style="font-size:1rem;margin:1rem 0 .5rem">Bệ / ván gỗ ({len(WOOD_PLATFORMS)})</h3>
    <div style="overflow:auto;max-height:280px">
    <table>
      <thead><tr><th>ID</th><th>Tên</th><th>Surface</th><th>District</th><th>Phục vụ</th><th>Cao hơn path</th></tr></thead>
      <tbody>{''.join(wood_rows)}</tbody>
    </table>
    </div>
  </section>

  <section>
    <h2>Ý tưởng cốt lõi</h2>
    <div class="callout">
      <strong>3DStreet:</strong> phố = lớp segment. <strong>AIdle:</strong> đá phẳng + bệ gỗ + family kiến trúc lặp.
    </div>
    <ul class="rules">{harmony_li}</ul>
  </section>

  <section>
    <h2>Districts (làng cổ tích)</h2>
    <div class="grid">{''.join(dist_cards)}</div>
  </section>

  <section>
    <h2>Architecture families — lặp giống nhau, hài hòa</h2>
    <p class="muted">Cùng skeleton / silhouette; đổi palette, mái, cửa. MVP gắn 10 building SSOT; wave sau nhân bản cottage/shop.</p>
    <div style="overflow:auto">
    <table>
      <thead><tr><th>Family</th><th>Tên</th><th>SSOT module</th><th>Lặp?</th><th>Palette</th></tr></thead>
      <tbody>{''.join(arch_rows)}</tbody>
    </table>
    </div>
  </section>

  <section>
    <h2>Plots (50)</h2>
    <div class="filters" id="filters">
      <button type="button" class="active" data-f="all">Tất cả</button>
      <button type="button" data-f="building">Building</button>
      <button type="button" data-f="prop">Prop</button>
      <button type="button" data-f="character_spawn">Cast</button>
    </div>
    <div style="overflow:auto;max-height:420px">
    <table id="plots">
      <thead><tr><th>Plot</th><th>Role</th><th>Object</th><th>District</th><th>Arch</th><th>XZ</th><th>Ghi chú</th></tr></thead>
      <tbody>{''.join(plot_rows)}</tbody>
    </table>
    </div>
  </section>

  <section>
    <h2>Modular repeat (nhiều nhà giống nhau)</h2>
    <p>{escape(MODULAR_REPEAT['principle_vi'])}</p>
    <p><strong>Cottage row:</strong> spacing 2 cells · setback 1m · palette sequence
      <code>cream_rose → butter_peach → mint_soft → sky_lilac</code></p>
    <p><strong>Shop lane:</strong> awning height lock · frontage dọc Storybook Lane</p>
    <p><strong>Street furniture:</strong> đèn ~5m · ghế ~8m · hoa ~4m (ý tưởng density 3DStreet, module AIdle)</p>
  </section>
</main>
<footer>
  {PLAN_ID} · Design Parent · không patch game/** · Human accept trước khi import runtime
</footer>
<script>
document.getElementById('filters').addEventListener('click', (e) => {{
  const b = e.target.closest('button');
  if (!b) return;
  const f = b.dataset.f;
  document.querySelectorAll('#filters button').forEach(x => x.classList.toggle('active', x === b));
  document.querySelectorAll('#plots tbody tr').forEach(tr => {{
    tr.style.display = (f === 'all' || tr.dataset.role === f) ? '' : 'none';
  }});
}});
</script>
</body>
</html>
"""


def readme(doc: dict) -> str:
    stone_list = "\n".join(f"- `{s['id']}` — {s['name_vi']} ({s.get('width_m','?')}m, flat)" for s in STONE_PATH_NETWORK)
    wood_list = "\n".join(f"- `{w['id']}` — {w['name_vi']} → {w.get('serves','')}" for w in WOOD_PLATFORMS)
    return f"""# {PLAN_ID} — Thị trấn Cổ tích Thân thiện (+ đường đá & bệ gỗ)

**Có.** Quy hoạch **storybook street town** với:

- **Đường bằng phẳng lát đá** (`STONE_PAVER_FLAT`, slope 0°)
- **Bệ / ván gỗ** (`WOOD_DECK_FLAT`, `WOOD_BOARDWALK`, `WOOD_BRIDGE_DECK`)
- Phương pháp segment [3DStreet](https://github.com/3DStreet/3dstreet) — **không** clone AGPL assets
- Kiến trúc lặp family + palette xen kẽ
- 50 plots MOCKUP_SSOT_V2 · bounds ±12

## Mở

| File | Mô tả |
|------|--------|
| `{PLAN_ID}.html` | Mockup (có bảng stone/wood) |
| `{PLAN_ID}.svg` | Bản đồ — paver pattern + wood plank |
| `{PLAN_ID}.json` | `stone_path_network` + `wood_platforms` + materials |
| `_gen_fairy_street_v1.py` | Generator |

## Bề mặt (v1.1)

### Vật liệu

| Material | Vai trò |
|----------|---------|
| `STONE_PAVER_FLAT` | Lòng đường / vành đai / hẻm — đá lát phẳng |
| `STONE_RING_PLAZA` | Vòng đá quanh gazebo |
| `WOOD_DECK_FLAT` | Bệ gỗ trước cửa, shop, tháp, barn… |
| `WOOD_BOARDWALK` | Lối ván ven nước (WELL) |
| `WOOD_BRIDGE_DECK` | Mặt sàn gỗ cầu vòm |

**Layer:** lawn → stone → wood deck/boardwalk → props → buildings.  
Gỗ cao hơn path ~0.06–0.12m (mép đọc được, vẫn walkable flat). Junction đá–gỗ bo tròn, không bậc cao.

### Mạng đá ({len(STONE_PATH_NETWORK)} segment)

{stone_list}

### Bệ gỗ ({len(WOOD_PLATFORMS)})

{wood_list}

### Module production

| Surface | Module |
|---------|--------|
| Đá | `cozy_path_stone_A` (+ strip variants sau) |
| Bệ gỗ | design slot `cozy_wood_deck_A` (chưa GLB) |
| Boardwalk | design slot `cozy_boardwalk_A` (chưa GLB) |
| Cầu | part of `cozy_bridge_arch_A` |

## Architecture families

Cottage / Shop / Workshop / Gazebo / Greenhouse / Well / Windmill / Barn / Bridge / Lookout (`cozy_watchtower_A`).

## Status

**accepted=false** — design only. Không patch `game/**`. Human + wave packet trước import runtime.

## Regenerate

```text
python orchestration/control/visual_reference/town_plan/_gen_fairy_street_v1.py
```
"""


def main() -> None:
    doc = build_json()
    (OUT / f"{PLAN_ID}.json").write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (OUT / f"{PLAN_ID}.svg").write_text(svg_map(doc), encoding="utf-8")
    (OUT / f"{PLAN_ID}.html").write_text(html_page(doc), encoding="utf-8")
    (OUT / f"{PLAN_ID}_README.md").write_text(readme(doc), encoding="utf-8")
    print(f"OK {PLAN_ID}: 50 plots, sha={doc.get('content_sha256')}")
    print(f"  → {OUT / f'{PLAN_ID}.html'}")


if __name__ == "__main__":
    main()
