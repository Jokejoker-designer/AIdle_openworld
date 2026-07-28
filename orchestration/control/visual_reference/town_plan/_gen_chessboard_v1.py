# -*- coding: utf-8 -*-
"""TOWN_CHESSBOARD_PLAN_V1 — quy hoạch thị trấn dạng bàn cờ (design mockup).

Orthogonal city grid like a real planned town: streets, blocks, parcels.
Fits ±12 cadastre / content ±11.5. IDs from MOCKUP_SSOT_V2 only.
"""
from __future__ import annotations

import hashlib
import json
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent

# Chessboard: 12×12 cells of 2m. Cell A1 = NW corner.
# center_x = -11 + col_i * 2
# center_z = 11 - row_j * 2  (row 1 = north)
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
    """w cols east, h rows south from anchor (col0,row0)."""
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


# --- City structure (chessboard blocks) ---
#   N (z+)
# W +----+----+----+ E
#   |AGRI|PARK|MKT |
#   +----+----+----+
#   |WTR |HOME|CRFT|
#   +----+----+----+
#   |MILL|BRG |VIEW|
#   S (z-)

DISTRICTS = [
    {
        "district_id": "HOME",
        "name": "Khu nhà (tâm)",
        "block": "E5–H8",
        "function_vi": "Trung tâm cư trú / Private Reality hub",
        "color": "#f5c451",
        "center": {"x": 0.0, "z": 0.0},
    },
    {
        "district_id": "MARKET",
        "name": "Khu chợ",
        "block": "I3–L6",
        "function_vi": "Thương mại / tụ họp",
        "color": "#e07a5f",
        "center": {"x": 7.0, "z": 5.0},
    },
    {
        "district_id": "WORKSHOP",
        "name": "Khu xưởng",
        "block": "I7–L10",
        "function_vi": "Thủ công / sửa chữa",
        "color": "#c98a5e",
        "center": {"x": 7.0, "z": -3.0},
    },
    {
        "district_id": "GARDEN",
        "name": "Công viên",
        "block": "E1–H4",
        "function_vi": "Cảnh quan / nghỉ",
        "color": "#72A96B",
        "center": {"x": 0.0, "z": 7.0},
    },
    {
        "district_id": "GREENHOUSE",
        "name": "Khu canh tác",
        "block": "A1–D4",
        "function_vi": "Nông nghiệp kính + luống",
        "color": "#7fc98f",
        "center": {"x": -7.0, "z": 7.0},
    },
    {
        "district_id": "WELL",
        "name": "Khu nước",
        "block": "A5–D8",
        "function_vi": "Giếng / ao / tiện ích nước",
        "color": "#9ED7E5",
        "center": {"x": -7.0, "z": 0.0},
    },
    {
        "district_id": "WINDMILL",
        "name": "Khu cối xay",
        "block": "A9–D12",
        "function_vi": "Cơ khí / landmark tây-nam",
        "color": "#6b8cae",
        "center": {"x": -7.0, "z": -7.0},
    },
    {
        "district_id": "BARN",
        "name": "Khu kho",
        "block": "E9–H12",
        "function_vi": "Kho / sân bãi",
        "color": "#a67c52",
        "center": {"x": 0.0, "z": -7.0},
    },
    {
        "district_id": "BRIDGE",
        "name": "Khu cầu",
        "block": "E11–H12 + trục nam",
        "function_vi": "Cầu vòm / lối cảnh quan",
        "color": "#8a8378",
        "center": {"x": 0.0, "z": -9.0},
    },
    {
        "district_id": "LOOKOUT",
        "name": "Khu vọng",
        "block": "I11–L12",
        "function_vi": "Tháp canh / nhìn ra",
        "color": "#b08d57",
        "center": {"x": 7.0, "z": -9.0},
    },
]

# Streets: orthogonal chessboard avenues (world units along cell edges)
# Vertical avenues (constant x): between col bands
STREETS = {
    "Ave_W": {"axis": "z", "at_x": -5.0, "z0": -11.0, "z1": 11.0, "class": "avenue", "name": "Đại lộ Tây"},
    "Ave_C": {"axis": "z", "at_x": 0.0, "z0": -11.0, "z1": 11.0, "class": "avenue", "name": "Trục Trung tâm (N–S)"},
    "Ave_E": {"axis": "z", "at_x": 5.0, "z0": -11.0, "z1": 11.0, "class": "avenue", "name": "Đại lộ Đông"},
    "St_N": {"axis": "x", "at_z": 5.0, "x0": -11.0, "x1": 11.0, "class": "street", "name": "Phố Bắc"},
    "St_C": {"axis": "x", "at_z": 0.0, "x0": -11.0, "x1": 11.0, "class": "street", "name": "Phố Trung (Đ–T)"},
    "St_S": {"axis": "x", "at_z": -5.0, "x0": -11.0, "x1": 11.0, "class": "street", "name": "Phố Nam"},
    "Ring": {
        "axis": "ring",
        "class": "ring",
        "name": "Vành đai ngoài",
        "waypoints": [
            [-11, 11],
            [11, 11],
            [11, -11],
            [-11, -11],
            [-11, 11],
        ],
    },
}

# Building parcels (chessboard multi-cell), then char offset, then 3 props on street frontage
# Format: district, building_id, anchor_col, anchor_row, w, h, rot, char_id, char_name, props[(id, col, row, rot)]
PARCELS = [
    (
        "HOME",
        "cozy_house_small_A",
        "F",
        6,
        3,
        2,
        0.0,
        "CCP-RH-001",
        "Nori-7",
        [
            ("cozy_path_stone_A", "E", 7, 0.0),
            ("cozy_garden_lamp_A", "I", 6, 0.0),
            ("cozy_mailbox_A", "G", 8, 0.0),
        ],
    ),
    (
        "MARKET",
        "cozy_market_stall_A",
        "J",
        4,
        3,
        2,
        180.0,
        "CCP-NS-002",
        "Mây Mạch",
        [
            ("cozy_bench_A", "I", 4, 90.0),
            ("cozy_cart_A", "L", 5, 0.0),
            ("cozy_signpost_A", "J", 3, 0.0),
        ],
    ),
    (
        "WORKSHOP",
        "cozy_workshop_A",
        "J",
        8,
        2,
        2,
        270.0,
        "CCP-NW-003",
        "Bác Bắp",
        [
            ("cozy_tool_rack_A", "I", 8, 0.0),
            ("cozy_crate_small_A", "L", 8, 0.0),
            ("cozy_barrel_A", "L", 10, 0.0),
        ],
    ),
    (
        "GARDEN",
        "cozy_gazebo_A",
        "F",
        2,
        2,
        2,
        0.0,
        "CCP-CT-004",
        "Bụi Mơ",
        [
            ("cozy_flower_cluster_A", "E", 2, 0.0),
            ("cozy_flower_bed_B", "H", 2, 0.0),
            ("cozy_bush_round_A", "G", 4, 0.0),
        ],
    ),
    (
        "GREENHOUSE",
        "cozy_greenhouse_A",
        "B",
        2,
        3,
        2,
        0.0,
        "SPH-RH-011",
        "Kito Thụ Phấn",
        [
            ("cozy_farm_plot_A", "A", 2, 0.0),
            ("cozy_crop_row_A", "A", 4, 0.0),
            ("cozy_scarecrow_A", "D", 4, 0.0),
        ],
    ),
    (
        "WELL",
        "cozy_well_house_A",
        "B",
        6,
        2,
        2,
        90.0,
        "OA-RG-021",
        "Nereu-5",
        [
            ("cozy_pond_small_A", "A", 6, 0.0),
            ("cozy_water_pump_A", "D", 6, 0.0),
            ("cozy_birdbath_A", "D", 8, 0.0),
        ],
    ),
    (
        "WINDMILL",
        "cozy_windmill_A",
        "B",
        10,
        2,
        2,
        0.0,
        "AC-CO-015",
        "Cinder-04",
        [
            ("cozy_fence_section_A", "A", 10, 0.0),
            ("cozy_grass_tuft_A", "D", 10, 0.0),
            ("cozy_rock_cluster_A", "D", 12, 0.0),
        ],
    ),
    (
        "BARN",
        "cozy_barn_small_A",
        "F",
        9,
        3,
        2,
        0.0,
        "TD-CT-028",
        "Patch Gấu Nút",
        [
            ("cozy_tree_fruit_A", "E", 9, 0.0),
            ("cozy_rock_small_A", "I", 9, 0.0),
            ("cozy_rock_stacked_A", "I", 10, 0.0),
        ],
    ),
    (
        "BRIDGE",
        "cozy_bridge_arch_A",
        "F",
        11,
        3,
        2,
        90.0,
        "SV-NW-019",
        "Trúc Nhi",
        [
            ("cozy_tree_willow_A", "E", 11, 0.0),
            ("cozy_tree_blossom_A", "I", 11, 0.0),
            ("cozy_rock_mossy_A", "G", 12, 0.0),
        ],
    ),
    (
        "LOOKOUT",
        "cozy_watchtower_A",
        "J",
        11,
        2,
        2,
        180.0,
        "SPH-NG-009",
        "Luma Tán Lá",
        [
            ("cozy_tree_landmark_A", "I", 12, 0.0),
            ("cozy_tree_pine_A", "L", 11, 0.0),
            ("cozy_tree_cluster_A", "L", 12, 0.0),
        ],
    ),
]


def build_plots() -> list[dict]:
    plots = []
    for did, bid, ac, ar, bw, bh, brot, cid, cname, props in PARCELS:
        occ = multi_cells(ac, ar, bw, bh)
        bx, bz = footprint_center(occ)
        # clamp slight float
        bx, bz = round(bx, 2), round(bz, 2)
        plots.append(
            {
                "plot_id": f"{did}.BLD",
                "role": "building",
                "district": did,
                "object_id": bid,
                "grid_cell": cell_id(ac, ar),
                "occupancy_cells": occ,
                "footprint_units": [bw * CELL, bh * CELL],
                "chessboard": {"pattern": "city_block", "parcel": f"{ac}{ar}+{bw}x{bh}"},
                "transform": {
                    "x": bx,
                    "y": 0.0,
                    "z": bz,
                    "rotation_deg": brot,
                    "scale": 1.0,
                },
            }
        )
        # Character: one cell south or east of building front (readability 2.5D)
        # Place on cell just south of parcel center (higher row number)
        ci = COLS.index(ac) + max(0, bw // 2)
        cj = ar + bh  # south of parcel
        if cj > 12:
            cj = ar - 1
        if cj < 1:
            cj = 1
        col_c = COLS[min(ci, 11)]
        cx, cz = cell_center(col_c, cj)
        # nudge toward building
        cx = round((cx + bx) / 2, 2)
        cz = round((cz + bz) / 2, 2)
        plots.append(
            {
                "plot_id": f"{did}.CHAR",
                "role": "character_spawn",
                "district": did,
                "object_id": cid,
                "character_name": cname,
                "world_profile": "cozy_cyber_pixel",
                "resident_status": "native_or_visitor",
                "grid_cell": cell_id(col_c, cj),
                "chessboard": {"pattern": "frontage_cell"},
                "transform": {
                    "x": cx,
                    "y": 0.0,
                    "z": cz,
                    "rotation_deg": brot,
                    "scale": 1.0,
                },
            }
        )
        for i, (pid, pc, pr, prot) in enumerate(props, 1):
            px, pz = cell_center(pc, pr)
            plots.append(
                {
                    "plot_id": f"{did}.P{i}",
                    "role": "prop",
                    "district": did,
                    "object_id": pid,
                    "grid_cell": cell_id(pc, pr),
                    "footprint_units": [1.0, 1.0],
                    "chessboard": {"pattern": "single_cell"},
                    "transform": {
                        "x": round(px, 2),
                        "y": 0.0,
                        "z": round(pz, 2),
                        "rotation_deg": prot,
                        "scale": 1.0,
                    },
                }
            )
    return plots


def validate(plots: list[dict]) -> None:
    assert len(plots) == 50
    roles = {}
    for p in plots:
        roles[p["role"]] = roles.get(p["role"], 0) + 1
        t = p["transform"]
        assert abs(t["x"]) <= 11.5 and abs(t["z"]) <= 11.5, p["plot_id"]
    assert roles == {"building": 10, "prop": 30, "character_spawn": 10}
    # building occupancy no overlap
    occ = {}
    for p in plots:
        if p["role"] != "building":
            continue
        for c in p["occupancy_cells"]:
            assert c not in occ, (c, occ[c], p["plot_id"])
            occ[c] = p["plot_id"]
    # unique object ids for buildings and props
    bids = [p["object_id"] for p in plots if p["role"] == "building"]
    assert len(bids) == len(set(bids))
    pids = [p["object_id"] for p in plots if p["role"] == "prop"]
    assert len(pids) == len(set(pids)), pids


def write_svg(plots: list[dict], path: Path) -> None:
    pad = 14.0
    scale = 30.0
    w = int(pad * 2 * scale)
    h = int(pad * 2 * scale)

    def wx(x: float) -> float:
        return (x + pad) * scale

    def wz(z: float) -> float:
        return (pad - z) * scale

    dist_color = {d["district_id"]: d["color"] for d in DISTRICTS}
    parts = [
        f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<title>AIdle Cozy Town — Chessboard City Plan V1</title>
<defs>
  <pattern id="chess" width="{CELL * scale * 2}" height="{CELL * scale * 2}" patternUnits="userSpaceOnUse">
    <rect width="{CELL * scale}" height="{CELL * scale}" fill="#f3ebe0"/>
    <rect x="{CELL * scale}" width="{CELL * scale}" height="{CELL * scale}" fill="#e8dcc8"/>
    <rect y="{CELL * scale}" width="{CELL * scale}" height="{CELL * scale}" fill="#e8dcc8"/>
    <rect x="{CELL * scale}" y="{CELL * scale}" width="{CELL * scale}" height="{CELL * scale}" fill="#f3ebe0"/>
  </pattern>
</defs>
<rect width="100%" height="100%" fill="#dfe9e2"/>
<!-- chessboard field within ±12 -->
<rect x="{wx(-12):.1f}" y="{wz(12):.1f}" width="{24 * scale}" height="{24 * scale}" fill="url(#chess)" stroke="#263238" stroke-width="2"/>
'''
    ]

    # district block overlays (approx rectangles)
    blocks = {
        "HOME": ("E", 5, 4, 4),
        "MARKET": ("I", 3, 4, 4),
        "WORKSHOP": ("I", 7, 4, 4),
        "GARDEN": ("E", 1, 4, 4),
        "GREENHOUSE": ("A", 1, 4, 4),
        "WELL": ("A", 5, 4, 4),
        "WINDMILL": ("A", 9, 4, 4),
        "BARN": ("E", 9, 4, 2),
        "BRIDGE": ("E", 11, 4, 2),
        "LOOKOUT": ("I", 11, 4, 2),
    }
    for did, (c0, r0, bw, bh) in blocks.items():
        cells = multi_cells(c0, r0, bw, bh)
        xs = [cell_center(c[0], int(c[1:]))[0] for c in cells]
        zs = [cell_center(c[0], int(c[1:]))[1] for c in cells]
        minx, maxx = min(xs) - 1, max(xs) + 1
        minz, maxz = min(zs) - 1, max(zs) + 1
        col = dist_color[did]
        parts.append(
            f'<rect x="{wx(minx):.1f}" y="{wz(maxz):.1f}" width="{(maxx - minx) * scale:.1f}" height="{(maxz - minz) * scale:.1f}" fill="{col}" opacity="0.22" stroke="{col}" stroke-width="2" stroke-dasharray="5 3"/>'
        )
        name = next(d["name"] for d in DISTRICTS if d["district_id"] == did)
        parts.append(
            f'<text x="{wx((minx + maxx) / 2):.1f}" y="{wz((minz + maxz) / 2):.1f}" text-anchor="middle" font-size="12" font-weight="700" fill="#263238" opacity="0.85">{escape(name)}</text>'
        )

    # streets
    for _sid, s in STREETS.items():
        if s.get("axis") == "ring":
            pts = " ".join(f"{wx(x):.1f},{wz(z):.1f}" for x, z in s["waypoints"])
            parts.append(
                f'<polyline points="{pts}" fill="none" stroke="#b8a878" stroke-width="{1.4 * scale * 0.35:.1f}" opacity="0.75"/>'
            )
        elif s.get("axis") == "z":
            x = s["at_x"]
            parts.append(
                f'<line x1="{wx(x):.1f}" y1="{wz(s["z0"]):.1f}" x2="{wx(x):.1f}" y2="{wz(s["z1"]):.1f}" stroke="#c9b98a" stroke-width="{1.5 * scale * 0.4:.1f}" opacity="0.9"/>'
            )
        else:
            z = s["at_z"]
            parts.append(
                f'<line x1="{wx(s["x0"]):.1f}" y1="{wz(z):.1f}" x2="{wx(s["x1"]):.1f}" y2="{wz(z):.1f}" stroke="#c9b98a" stroke-width="{1.5 * scale * 0.4:.1f}" opacity="0.9"/>'
            )

    # cell labels light
    for i, col in enumerate(COLS):
        x = -11 + i * 2
        parts.append(
            f'<text x="{wx(x):.1f}" y="{wz(12.6):.1f}" text-anchor="middle" font-size="10" font-family="Consolas" fill="#5a655c">{col}</text>'
        )
    for row in ROWS:
        z = 11 - (row - 1) * 2
        parts.append(
            f'<text x="{wx(-12.7):.1f}" y="{wz(z):.1f}" text-anchor="middle" font-size="10" font-family="Consolas" fill="#5a655c">{row}</text>'
        )

    for p in plots:
        t = p["transform"]
        cx, cy = wx(t["x"]), wz(t["z"])
        col = dist_color.get(p["district"], "#999")
        if p["role"] == "building":
            fw = p["footprint_units"][0] * scale * 0.42
            fh = p["footprint_units"][1] * scale * 0.42
            rot = -t["rotation_deg"]
            parts.append(f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({rot:.1f})">')
            parts.append(
                f'<rect x="{-fw / 2:.1f}" y="{-fh / 2:.1f}" width="{fw:.1f}" height="{fh:.1f}" rx="3" fill="{col}" opacity="0.75" stroke="#263238" stroke-width="1.6"/>'
            )
            parts.append("</g>")
            parts.append(
                f'<text x="{cx:.1f}" y="{cy + 4:.1f}" text-anchor="middle" font-size="8" font-weight="700" fill="#263238">{escape(p["plot_id"])}</text>'
            )
        elif p["role"] == "character_spawn":
            parts.append(
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="9" fill="#72A96B" stroke="#263238" stroke-width="1.2"/>'
            )
            parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.5" fill="#fdf3e2"/>')
        else:
            parts.append(
                f'<rect x="{cx - 6:.1f}" y="{cy - 6:.1f}" width="12" height="12" rx="2" fill="#fdf3e2" stroke="{col}" stroke-width="1.3"/>'
            )

    parts.append(
        f'''
<text x="{w / 2}" y="26" text-anchor="middle" font-size="18" font-weight="700" fill="#263238">Thị trấn Cozy — Quy hoạch bàn cờ (Chessboard City Plan V1)</text>
<text x="{w / 2}" y="46" text-anchor="middle" font-size="11" fill="#5a655c">Lưới 12×12 · ô 2m · trục N–S / Đ–T · 10 block · 50 thửa · MOCKUP_SSOT_V2 · ±12</text>
<g transform="translate({w - 72},{90})">
  <polygon points="0,-26 9,10 -9,10" fill="#263238"/>
  <text x="0" y="26" text-anchor="middle" font-size="11" font-weight="700" fill="#263238">N (+Z)</text>
</g>
<g transform="translate(20,{h - 150})">
  <rect width="250" height="130" rx="10" fill="#fffaf0" stroke="#e8d9c0"/>
  <text x="12" y="20" font-size="12" font-weight="700" fill="#263238">Quy hoạch bàn cờ</text>
  <text x="12" y="40" font-size="10" fill="#263238">• Ô xen kẽ (chessboard) 2×2m</text>
  <text x="12" y="56" font-size="10" fill="#263238">• Đại lộ dọc + phố ngang (trục chữ thập)</text>
  <text x="12" y="72" font-size="10" fill="#263238">• 10 block = 10 district chức năng</text>
  <text x="12" y="88" font-size="10" fill="#263238">• Building = lô đa ô · Prop = 1 ô</text>
  <text x="12" y="104" font-size="10" fill="#263238">• Character = frontage (trước nhà)</text>
  <text x="12" y="120" font-size="10" fill="#5a655c">accepted=false · design mockup</text>
</g>
</svg>
'''
    )
    path.write_text("".join(parts), encoding="utf-8")


def write_html(plan: dict, path: Path) -> None:
    js_plots = json.dumps(plan["plots"], ensure_ascii=False)
    js_dist = json.dumps(plan["districts"], ensure_ascii=False)
    js_st = json.dumps(plan["streets"], ensure_ascii=False)
    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Thị trấn bàn cờ — Chessboard Plan V1</title>
<style>
:root {{ --ink:#263238; --cream:#fdf3e2; --border:#e8d9c0; --card:#fffaf0; --leaf:#72A96B; --sub:#5a655c; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; font-family:"Segoe UI",system-ui,sans-serif; color:var(--ink);
  background:linear-gradient(180deg,#e8f2ea,#f7f0e4 50%); }}
header {{ max-width:1400px; margin:0 auto; padding:22px 18px 8px; }}
h1 {{ margin:0 0 6px; font-size:1.5rem; }}
.sub {{ color:var(--sub); max-width:85ch; line-height:1.5; font-size:.95rem; }}
.badge {{ display:inline-block; border:1px solid var(--border); border-radius:999px; padding:3px 10px;
  font-size:.78rem; background:var(--cream); margin:4px 4px 0 0; }}
.badge.lock {{ background:#1b4332; color:#e8f5e9; }}
.layout {{ max-width:1400px; margin:0 auto; padding:8px 18px 36px; display:grid;
  grid-template-columns:1.3fr 340px; gap:14px; }}
@media(max-width:1000px){{ .layout {{ grid-template-columns:1fr; }} }}
.panel {{ background:var(--card); border:1px solid var(--border); border-radius:14px; overflow:hidden; }}
.toolbar {{ padding:10px; border-bottom:1px solid var(--border); display:flex; flex-wrap:wrap; gap:8px; background:#faf6ee; }}
.toolbar a, .toolbar select {{ font-size:.8rem; padding:5px 9px; border-radius:8px; border:1px solid var(--border); background:#fff; text-decoration:none; color:var(--ink); }}
.map {{ overflow:auto; max-height:78vh; background:#dfe9e2; }}
.map img {{ width:100%; display:block; }}
.side {{ display:flex; flex-direction:column; gap:10px; }}
.card {{ background:var(--card); border:1px solid var(--border); border-radius:12px; padding:12px; }}
.card h2 {{ margin:0 0 8px; font-size:.95rem; border-left:3px solid var(--leaf); padding-left:8px; }}
.list {{ max-height:32vh; overflow:auto; display:flex; flex-direction:column; gap:5px; }}
.item {{ border:1px solid var(--border); border-radius:8px; padding:7px 9px; cursor:pointer; background:#fff; font-size:.82rem; }}
.item:hover {{ background:#eef6ea; }}
.meta {{ font-family:Consolas,monospace; font-size:.72rem; color:var(--sub); }}
.row {{ display:grid; grid-template-columns:90px 1fr; gap:4px; font-size:.8rem; margin:3px 0; }}
.k {{ color:var(--sub); }}
footer {{ max-width:1400px; margin:0 auto; padding:0 18px 36px; font-size:.8rem; color:var(--sub); }}
ul {{ margin:0; padding-left:18px; font-size:.82rem; line-height:1.45; }}
</style>
</head>
<body>
<header>
  <h1>Thị trấn hình bàn cờ — quy hoạch đô thị V1</h1>
  <p class="sub">
    Lưới <strong>12×12 ô</strong> (mỗi ô 2m) như bàn cờ; <strong>trục chữ thập</strong> Bắc–Nam / Đông–Tây;
    <strong>10 block</strong> = 10 khu chức năng; 50 thửa bám MOCKUP_SSOT_V2.
    Giống quy hoạch thành phố nhỏ có thứ tự — không rải ngẫu nhiên.
  </p>
  <span class="badge lock">DESIGN_CHESSBOARD_ACTIVE</span>
  <span class="badge">12×12 · ô 2m</span>
  <span class="badge">10 blocks</span>
  <span class="badge">50 plots</span>
  <span class="badge">accepted=false</span>
</header>
<div class="layout">
  <div class="panel">
    <div class="toolbar">
      <select id="fDist"><option value="">Mọi district</option></select>
      <select id="fRole">
        <option value="">Mọi role</option>
        <option value="building">Building</option>
        <option value="prop">Prop</option>
        <option value="character_spawn">Character</option>
      </select>
      <a href="TOWN_CHESSBOARD_PLAN_V1.svg" target="_blank">SVG</a>
      <a href="TOWN_CHESSBOARD_PLAN_V1.json" target="_blank">JSON</a>
      <a href="TOWN_MASTERPLAN_MOCKUP_V1.html" target="_blank">Masterplan trước</a>
    </div>
    <div class="map"><img src="TOWN_CHESSBOARD_PLAN_V1.svg" alt="Chessboard city plan"/></div>
  </div>
  <div class="side">
    <div class="card">
      <h2>Cấu trúc đô thị</h2>
      <ul>
        <li>Lưới bàn cờ A1–L12</li>
        <li>Đại lộ Tây / Trung / Đông (N–S)</li>
        <li>Phố Bắc / Trung / Nam (Đ–T)</li>
        <li>Vành đai ngoài ±11</li>
        <li>Tâm HOME tại giao trục</li>
        <li>Chợ–Xưởng đông · Nông–Nước tây · Kho–Cầu–Vọng nam</li>
      </ul>
    </div>
    <div class="card"><h2>District / Block</h2><div class="list" id="dList"></div></div>
    <div class="card"><h2>Thửa (<span id="n">0</span>)</h2><div class="list" id="pList"></div></div>
    <div class="card" id="det"><h2>Chi tiết</h2><p class="meta">Chọn thửa…</p></div>
  </div>
</div>
<footer>
  TOWN_CHESSBOARD_PLAN_V1 · design only · MOCKUP_SSOT_V2 IDs · không tự patch game/** ·
  Import runtime cần wave build riêng (cadastre V2) nếu Human duyệt.
</footer>
<script>
const P={js_plots};
const D={js_dist};
const fd=document.getElementById('fDist'), fr=document.getElementById('fRole');
const pL=document.getElementById('pList'), dL=document.getElementById('dList'), det=document.getElementById('det');
D.forEach(d=>{{
  const o=document.createElement('option'); o.value=d.district_id; o.textContent=d.name; fd.appendChild(o);
  const el=document.createElement('div'); el.className='item';
  el.innerHTML='<b style="border-left:4px solid '+d.color+';padding-left:6px">'+d.name+'</b><div class="meta">'+d.district_id+' · '+d.block+'</div><div class="meta">'+d.function_vi+'</div>';
  el.onclick=()=>{{fd.value=d.district_id; ren();}};
  dL.appendChild(el);
}});
function fil(){{return P.filter(p=>{{
  if(fd.value&&p.district!==fd.value)return false;
  if(fr.value&&p.role!==fr.value)return false;
  return true;
}});}}
function show(p){{
  det.innerHTML='<h2>'+p.plot_id+'</h2>'
    +'<div class="row"><span class="k">Object</span><span>'+p.object_id+(p.character_name?(' · '+p.character_name):'')+'</span></div>'
    +'<div class="row"><span class="k">Role</span><span>'+p.role+'</span></div>'
    +'<div class="row"><span class="k">District</span><span>'+p.district+'</span></div>'
    +'<div class="row"><span class="k">Ô bàn cờ</span><span class="meta">'+(p.grid_cell||'')+' '+(p.occupancy_cells?('· '+p.occupancy_cells.join(',')):'')+'</span></div>'
    +'<div class="row"><span class="k">XYZ</span><span class="meta">('+p.transform.x+',0,'+p.transform.z+') rot '+p.transform.rotation_deg+'°</span></div>'
    +'<div class="row"><span class="k">Pattern</span><span class="meta">'+JSON.stringify(p.chessboard||{{}})+'</span></div>';
}}
function ren(){{
  const L=fil(); document.getElementById('n').textContent=L.length; pL.innerHTML='';
  L.forEach(p=>{{
    const el=document.createElement('div'); el.className='item';
    el.innerHTML='<div><b>'+p.plot_id+'</b></div><div class="meta">'+p.role+' · '+p.object_id+'</div><div class="meta">('+p.transform.x+', '+p.transform.z+') · '+(p.grid_cell||'')+'</div>';
    el.onclick=()=>show(p); pL.appendChild(el);
  }});
}}
fd.onchange=fr.onchange=ren; ren();
</script>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")


def main() -> None:
    plots = build_plots()
    validate(plots)
    plan = {
        "schema_version": "town_chessboard_plan/1.0",
        "plan_id": "TOWN_CHESSBOARD_PLAN_V1",
        "title": "Thị trấn Cozy — Quy hoạch bàn cờ (chessboard city)",
        "status": "DESIGN_CHESSBOARD_ACTIVE",
        "accepted": False,
        "self_accept": False,
        "mockup_ssot": "MOCKUP_SSOT_V2",
        "world_profile": "cozy_cyber_pixel",
        "planning_style": "orthogonal_chessboard_city_grid",
        "planning_style_vi": "Lưới bàn cờ + trục đô thị chữ thập + block chức năng — giống thành phố quy hoạch, không rải ngẫu nhiên.",
        "coordinate_convention": "game_godot: x=east, z=north, y=up; rotation_deg about y",
        "fits_map": {
            "content_bounds": {"min": {"x": -11.5, "z": -11.5}, "max": {"x": 11.5, "z": 11.5}},
            "cadastre_bounds": {"min": {"x": -12, "z": -12}, "max": {"x": 12, "z": 12}},
            "note": "Fits current starter realm ±12.",
        },
        "grid": {
            "pattern": "chessboard",
            "cell_size_units": 2.0,
            "cols": COLS,
            "rows": ROWS,
            "origin": "A1 = northwest cell center (-11,+11); L12 = southeast (+11,-11)",
            "label_format": "COLROW e.g. G7",
            "alternating_tone": "visual chessboard for planning readability",
        },
        "streets": STREETS,
        "districts": DISTRICTS,
        "counts": {"building": 10, "prop": 30, "character_spawn": 10, "plots": 50},
        "plots": plots,
        "design_principles_vi": [
            "Bàn cờ 12×12: mọi thửa gắn ô có tên — không plot ‘bay’ ngoài lưới.",
            "Trục chữ thập Ave_C + St_C cắt tại HOME (tâm thành phố).",
            "Ba đại lộ dọc (Tây/Trung/Đông) + ba phố ngang (Bắc/Trung/Nam).",
            "10 block 4×4 (hoặc 4×2 phía nam) = 10 district chức năng rõ.",
            "Building = lô đa ô; prop = đúng 1 ô; character = frontage trước nhà.",
            "ID object chỉ lấy từ MOCKUP_SSOT_V2 — không invent module_id.",
            "Cyan không dùng tô block màu quy hoạch (chỉ manifestation in-game).",
            "Import game/** chỉ sau wave build + Human batch-accept.",
        ],
        "relation_to_prior": {
            "TOWN_GRID_PLAN_V1": "radial/organic district placement — still legal cadastre source if Human keeps it",
            "TOWN_MASTERPLAN_MOCKUP_V1": "narrative masterplan on V1 coords",
            "TOWN_CHESSBOARD_PLAN_V1": "THIS — formal chessboard replan of same 50 SSOT objects",
        },
        "html": "TOWN_CHESSBOARD_PLAN_V1.html",
        "svg": "TOWN_CHESSBOARD_PLAN_V1.svg",
    }
    body = json.dumps(plots, sort_keys=True, separators=(",", ":")).encode()
    plan["payload_fingerprint"] = hashlib.sha256(body).hexdigest()

    (OUT / "TOWN_CHESSBOARD_PLAN_V1.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_svg(plots, OUT / "TOWN_CHESSBOARD_PLAN_V1.svg")
    write_html(plan, OUT / "TOWN_CHESSBOARD_PLAN_V1.html")
    (OUT / "TOWN_CHESSBOARD_PLAN_V1_README.md").write_text(
        """# TOWN_CHESSBOARD_PLAN_V1 — Thị trấn hình bàn cờ

**Có.** Đây là quy hoạch **dạng bàn cờ / lưới đô thị** bài bản:

- Ô xen kẽ 12×12 (2m/ô)
- Đại lộ dọc + phố ngang (trục chữ thập)
- 10 block chức năng như khu thành phố nhỏ
- 50 thửa = 10 building + 30 prop + 10 character (MOCKUP_SSOT_V2)

## Mở

- `TOWN_CHESSBOARD_PLAN_V1.html` — mockup tương tác  
- `TOWN_CHESSBOARD_PLAN_V1.svg` — bản đồ  
- `TOWN_CHESSBOARD_PLAN_V1.json` — machine plan  

## So với plan trước

| Plan | Kiểu |
|------|------|
| TOWN_GRID_PLAN_V1 | District vòng quanh nhà (hơi “làng”) |
| TOWN_MASTERPLAN_MOCKUP_V1 | Minh họa quy hoạch trên V1 |
| **TOWN_CHESSBOARD_PLAN_V1** | **Thành phố lưới bàn cờ** |

**accepted=false** — design only. Build parent import cần Human duyệt + wave riêng.
""",
        encoding="utf-8",
    )
    print("OK chessboard", len(plots), plan["payload_fingerprint"][:16])


if __name__ == "__main__":
    main()
