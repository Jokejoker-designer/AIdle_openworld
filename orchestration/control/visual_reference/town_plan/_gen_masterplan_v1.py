# -*- coding: utf-8 -*-
"""Generate TOWN_MASTERPLAN_MOCKUP_V1 — detailed planning mockup (design only)."""
from __future__ import annotations

import hashlib
import json
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent
SRC = OUT / "TOWN_GRID_PLAN_V1.json"

DIST_COLOR = {
    "HOME": "#f5c451",
    "WORKSHOP": "#c98a5e",
    "MARKET": "#e07a5f",
    "GARDEN": "#72A96B",
    "GREENHOUSE": "#7fc98f",
    "WELL": "#9ED7E5",
    "WINDMILL": "#6b8cae",
    "BARN": "#a67c52",
    "BRIDGE": "#8a8378",
    "LOOKOUT": "#b08d57",
}

BLD_IMG = {
    "cozy_house_small_A": "../mockup_ssot_v2/buildings/bld_01_house.jpg",
    "cozy_greenhouse_A": "../mockup_ssot_v2/buildings/bld_02_greenhouse.jpg",
    "cozy_barn_small_A": "../mockup_ssot_v2/buildings/bld_03_barn.jpg",
    "cozy_workshop_A": "../mockup_ssot_v2/buildings/bld_04_workshop.jpg",
    "cozy_market_stall_A": "../mockup_ssot_v2/buildings/bld_05_market.jpg",
    "cozy_windmill_A": "../mockup_ssot_v2/buildings/bld_06_windmill.jpg",
    "cozy_well_house_A": "../mockup_ssot_v2/buildings/bld_07_well.jpg",
    "cozy_watchtower_A": "../mockup_ssot_v2/buildings/bld_08_watchtower.jpg",
    "cozy_bridge_arch_A": "../mockup_ssot_v2/buildings/bld_09_bridge.jpg",
    "cozy_gazebo_A": "../mockup_ssot_v2/buildings/bld_10_gazebo.jpg",
}
CHAR_IMG = {
    "CCP-RH-001": "../mockup_ssot_v2/chars/char_01_nori7.jpg",
    "CCP-NS-002": "../mockup_ssot_v2/chars/char_02_maymach.jpg",
    "CCP-NW-003": "../mockup_ssot_v2/chars/char_03_bacbap.jpg",
    "CCP-CT-004": "../mockup_ssot_v2/chars/char_04_buimo.jpg",
    "SPH-RH-011": "../mockup_ssot_v2/chars/char_05_kito.jpg",
    "OA-RG-021": "../mockup_ssot_v2/chars/char_06_nereu.jpg",
    "AC-CO-015": "../mockup_ssot_v2/chars/char_07_cinder.jpg",
    "TD-CT-028": "../mockup_ssot_v2/chars/char_08_patch.jpg",
    "SV-NW-019": "../mockup_ssot_v2/chars/char_09_truc.jpg",
    "SPH-NG-009": "../mockup_ssot_v2/chars/char_10_luma.jpg",
}
PROP_IMG = {
    "cozy_path_stone_A": "prop_path_stone.jpg",
    "cozy_garden_lamp_A": "prop_garden_lamp.jpg",
    "cozy_mailbox_A": "prop_mailbox.jpg",
    "cozy_pond_small_A": "prop_pond.jpg",
    "cozy_fence_section_A": "prop_fence.jpg",
    "cozy_tree_landmark_A": "prop_tree_landmark.jpg",
    "cozy_farm_plot_A": "prop_farm_plot.jpg",
    "cozy_flower_cluster_A": "prop_flower_cluster.jpg",
    "cozy_rock_small_A": "prop_rock_small.jpg",
    "cozy_tree_pine_A": "prop_tree_pine.jpg",
    "cozy_tree_cluster_A": "prop_tree_cluster.jpg",
    "cozy_tree_blossom_A": "prop_tree_blossom.jpg",
    "cozy_tree_fruit_A": "prop_tree_fruit.jpg",
    "cozy_tree_willow_A": "prop_tree_willow.jpg",
    "cozy_rock_mossy_A": "prop_rock_mossy.jpg",
    "cozy_rock_stacked_A": "prop_rock_stacked.jpg",
    "cozy_rock_cluster_A": "prop_rock_cluster.jpg",
    "cozy_flower_bed_B": "prop_flower_bed.jpg",
    "cozy_bush_round_A": "prop_bush_round.jpg",
    "cozy_grass_tuft_A": "prop_grass_tuft.jpg",
    "cozy_crop_row_A": "prop_crop_row.jpg",
    "cozy_bench_A": "prop_bench.jpg",
    "cozy_crate_small_A": "prop_crate.jpg",
    "cozy_barrel_A": "prop_barrel.jpg",
    "cozy_signpost_A": "prop_signpost.jpg",
    "cozy_water_pump_A": "prop_water_pump.jpg",
    "cozy_scarecrow_A": "prop_scarecrow.jpg",
    "cozy_cart_A": "prop_cart.jpg",
    "cozy_tool_rack_A": "prop_tool_rack.jpg",
    "cozy_birdbath_A": "prop_birdbath.jpg",
}


def main() -> None:
    plan = json.loads(SRC.read_text(encoding="utf-8"))
    plots = plan["plots"]
    districts = plan["districts"]
    cell = float(plan["grid"]["cell_size_units"])
    cols = plan["grid"]["cols"]
    rows = plan["grid"]["rows"]

    roads = {
        "ring_road": {
            "name": "Vành đai làng",
            "class": "primary",
            "width_m": 1.6,
            "waypoints": [
                [0, 0],
                [8, 6],
                [2, 10],
                [-5, 9],
                [-9, 3],
                [-9, -3],
                [-5, -9],
                [2, -10],
                [8, -6],
                [10, 0],
                [0, 0],
            ],
            "function_vi": "Liên kết 10 district; người đi + xe kéo",
        },
        "home_spur": {
            "name": "Lối sân nhà",
            "class": "secondary",
            "width_m": 1.2,
            "waypoints": [[0, 0], [1.6, 1.4], [-2.4, 1.8], [1.0, -2.4]],
            "function_vi": "Path stone + mailbox + character approach",
        },
        "farm_water_link": {
            "name": "Đường nông–giếng",
            "class": "secondary",
            "width_m": 1.2,
            "waypoints": [[-5, 9], [-9, 3], [-9, -3]],
            "function_vi": "Nước tưới / hậu cần nông",
        },
        "market_workshop": {
            "name": "Phố thợ–chợ",
            "class": "secondary",
            "width_m": 1.4,
            "waypoints": [[10, 0], [8, 6]],
            "function_vi": "Hàng xưởng ra chợ",
        },
        "scenic_south": {
            "name": "Đường cảnh quan nam",
            "class": "tertiary",
            "width_m": 1.0,
            "waypoints": [[-5, -9], [2, -10], [8, -6]],
            "function_vi": "Kho–cầu–tháp ngắm",
        },
    }

    land_use = [
        {"zone_id": "LU_RESIDENTIAL", "name": "Ở / sân nhà", "districts": ["HOME"], "color": "#fff1c7"},
        {"zone_id": "LU_CRAFT", "name": "Thủ công / xưởng", "districts": ["WORKSHOP", "WINDMILL"], "color": "#efe0c8"},
        {"zone_id": "LU_COMMERCE", "name": "Thương mại", "districts": ["MARKET"], "color": "#fde8d8"},
        {"zone_id": "LU_AGRI", "name": "Nông nghiệp", "districts": ["GREENHOUSE", "BARN"], "color": "#e4f0d8"},
        {"zone_id": "LU_LEISURE", "name": "Cảnh quan / nghỉ", "districts": ["GARDEN", "LOOKOUT"], "color": "#e8f5e9"},
        {"zone_id": "LU_WATER", "name": "Nước / tiện ích", "districts": ["WELL", "BRIDGE"], "color": "#e3f4fa"},
    ]

    principles = [
        "Nhà (HOME) là tâm làng — mọi vành đai quay về đây.",
        "Chợ + xưởng nửa đông — trao đổi hàng hóa đường ngắn.",
        "Nông nghiệp + giếng nửa tây/bắc — nước và ruộng liền kề.",
        "Cối xay / kho / cầu nửa nam — hậu cần và cảnh quan.",
        "Mỗi district: 1 building + 1 character + 3 props (ID MOCKUP_SSOT_V2).",
        "Camera 2.5D: character offset trước building, không chìm trong footprint.",
        "Cyan không tô body building/prop — chỉ manifestation.",
        "Content ±11.5, cadastre ±12 — khớp starter realm hiện tại.",
        "Build priority: HOME → MARKET/WORKSHOP → agri/water → còn lại.",
        "Placeholder in-game phải ghi plot_id + “concept — not yet authored”.",
    ]

    enriched = []
    for p in plots:
        ep = dict(p)
        role = p["role"]
        oid = p["object_id"]
        did = p["district"]
        ep["display_name"] = p.get("character_name") or oid
        ep["planning"] = {
            "setback_m": 0.4 if role == "prop" else (0.8 if role == "building" else 0.3),
            "build_priority": (
                1
                if did == "HOME"
                else 2
                if did in ("MARKET", "WORKSHOP")
                else 3
                if did in ("GREENHOUSE", "WELL", "GARDEN")
                else 4
            ),
            "notes_vi": {
                "building": "Khối công trình chính district — occupancy cells bắt buộc.",
                "prop": "Vật thể chức năng/trang trí — không chiếm building footprint.",
                "character_spawn": "Điểm đứng helper — offset trước building cho 2.5D.",
            }.get(role, ""),
            "access_vi": "Tiếp cận từ đường district / vành đai gần nhất.",
        }
        if role == "building":
            ep["mockup_img"] = BLD_IMG.get(oid)
        elif role == "character_spawn":
            ep["mockup_img"] = CHAR_IMG.get(oid)
        else:
            fn = PROP_IMG.get(oid)
            ep["mockup_img"] = ("../mockup_ssot_v2/props/" + fn) if fn else None
        enriched.append(ep)

    master = {
        "schema_version": "town_masterplan_mockup/1.0",
        "plan_id": "TOWN_MASTERPLAN_MOCKUP_V1",
        "title": "AIdle Cozy Starter Town — Masterplan Mockup (quy hoạch chi tiết)",
        "status": "DESIGN_MASTERPLAN_ACTIVE",
        "accepted": False,
        "self_accept": False,
        "mockup_ssot": "MOCKUP_SSOT_V2",
        "source_cadastre": "TOWN_GRID_PLAN_V1.json",
        "world_profile": "cozy_cyber_pixel",
        "art_direction": {
            "style": "Cozy Cyber-Pixel / Dreamy Low-Poly 2.5D",
            "palette": {
                "cream": "#fdf3e2",
                "ink": "#263238",
                "sky": "#9ED7E5",
                "leaf": "#72A96B",
                "wood": "#c98a5e",
                "warm": "#f5c451",
                "cyan_manifest_only": "#62E6FF",
            },
            "camera_game": "fixed three-quarter / isometric",
            "camera_map": "top-down planning (this mockup)",
        },
        "coordinate_convention": plan["coordinate_convention"],
        "fits_map": plan["fits_map"],
        "grid": plan["grid"],
        "counts": plan["counts"],
        "districts": [
            {
                **d,
                "color": DIST_COLOR.get(d["district_id"], "#ccc"),
                "display_name": d["name"],
            }
            for d in districts
        ],
        "land_use_zones": land_use,
        "circulation": roads,
        "plots": enriched,
        "design_principles_vi": principles,
        "legend": {
            "building": "Ô công trình (footprint + occupancy cells)",
            "prop": "Ô vật thể",
            "character_spawn": "Ô nhân vật / helper",
            "road_primary": "Vành đai liên district",
            "road_secondary": "Lối phụ",
            "grid": "Lưới 2m — cột A–L, hàng 1–12",
        },
        "html": "TOWN_MASTERPLAN_MOCKUP_V1.html",
        "svg": "TOWN_MASTERPLAN_MOCKUP_V1.svg",
        "readme": "TOWN_MASTERPLAN_MOCKUP_V1_README.md",
    }
    body = json.dumps(master["plots"], sort_keys=True, separators=(",", ":")).encode()
    master["payload_fingerprint"] = hashlib.sha256(body).hexdigest()
    (OUT / "TOWN_MASTERPLAN_MOCKUP_V1.json").write_text(
        json.dumps(master, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    # SVG
    pad = 14.0
    scale = 28.0
    w = int(pad * 2 * scale)
    h = int(pad * 2 * scale)

    def wx(x: float) -> float:
        return (x + pad) * scale

    def wz(z: float) -> float:
        return (pad - z) * scale

    svg: list[str] = []
    svg.append(
        f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<title>AIdle Cozy Starter Town — Masterplan Mockup V1</title>
<defs>
  <pattern id="grid" width="{cell * scale}" height="{cell * scale}" patternUnits="userSpaceOnUse">
    <path d="M {cell * scale} 0 L 0 0 0 {cell * scale}" fill="none" stroke="#e8d9c0" stroke-width="0.8"/>
  </pattern>
  <filter id="soft"><feDropShadow dx="0" dy="1" stdDeviation="1.5" flood-opacity="0.15"/></filter>
</defs>
<rect width="100%" height="100%" fill="#f7f0e4"/>
<rect width="100%" height="100%" fill="url(#grid)" opacity="0.9"/>
'''
    )

    for d in districts:
        c = d["center"]
        col = DIST_COLOR.get(d["district_id"], "#ddd")
        svg.append(
            f'<circle cx="{wx(c["x"]):.1f}" cy="{wz(c["z"]):.1f}" r="{3.2 * scale}" fill="{col}" opacity="0.18"/>'
        )
        svg.append(
            f'<circle cx="{wx(c["x"]):.1f}" cy="{wz(c["z"]):.1f}" r="{3.2 * scale}" fill="none" stroke="{col}" stroke-width="2" stroke-dasharray="6 4" opacity="0.55"/>'
        )
        svg.append(
            f'<text x="{wx(c["x"]):.1f}" y="{wz(c["z"]) + 3.55 * scale:.1f}" text-anchor="middle" font-family="Segoe UI,sans-serif" font-size="13" font-weight="700" fill="#263238">{escape(d["name"])}</text>'
        )
        svg.append(
            f'<text x="{wx(c["x"]):.1f}" y="{wz(c["z"]) + 3.55 * scale + 14:.1f}" text-anchor="middle" font-family="Consolas,monospace" font-size="10" fill="#5a655c">{d["district_id"]}</text>'
        )

    for _rid, road in roads.items():
        pts = " ".join(f"{wx(x):.1f},{wz(z):.1f}" for x, z in road["waypoints"])
        ww = road["width_m"] * scale * 0.55
        stroke = "#c9b98a" if road["class"] == "primary" else "#d9cfc0"
        svg.append(
            f'<polyline points="{pts}" fill="none" stroke="{stroke}" stroke-width="{ww:.1f}" stroke-linecap="round" stroke-linejoin="round" opacity="0.85"/>'
        )
        svg.append(
            f'<polyline points="{pts}" fill="none" stroke="#f5efe3" stroke-width="{max(1.0, ww * 0.25):.1f}" stroke-linecap="round" stroke-dasharray="4 6" opacity="0.7"/>'
        )

    for i, coln in enumerate(cols):
        x = (i - 5.5) * cell
        svg.append(
            f'<text x="{wx(x):.1f}" y="{wz(pad - 0.35):.1f}" text-anchor="middle" font-size="11" font-family="Consolas" fill="#8a8378">{coln}</text>'
        )
        svg.append(
            f'<text x="{wx(x):.1f}" y="{wz(-pad + 0.55):.1f}" text-anchor="middle" font-size="11" font-family="Consolas" fill="#8a8378">{coln}</text>'
        )
    for row in rows:
        z = (6.5 - (row - 1)) * cell - cell / 2
        svg.append(
            f'<text x="{wx(-pad + 0.45):.1f}" y="{wz(z):.1f}" text-anchor="middle" font-size="11" font-family="Consolas" fill="#8a8378">{row}</text>'
        )

    for p in enriched:
        t = p["transform"]
        x, z = float(t["x"]), float(t["z"])
        rot = float(t.get("rotation_deg", 0))
        role = p["role"]
        did = p["district"]
        col = DIST_COLOR.get(did, "#999")
        cx, cy = wx(x), wz(z)
        if role == "building":
            fp = p.get("footprint_units", [4, 4])
            fw = float(fp[0]) * scale * 0.45
            fh = float(fp[1]) * scale * 0.45
            svg.append(f'<g transform="translate({cx:.1f},{cy:.1f}) rotate({-rot:.1f})">')
            svg.append(
                f'<rect x="{-fw / 2:.1f}" y="{-fh / 2:.1f}" width="{fw:.1f}" height="{fh:.1f}" rx="4" fill="{col}" opacity="0.55" stroke="#263238" stroke-width="1.5" filter="url(#soft)"/>'
            )
            svg.append(
                f'<rect x="{-fw / 2 + 3:.1f}" y="{-fh / 2 + 3:.1f}" width="{max(4, fw - 6):.1f}" height="{max(4, fh - 6):.1f}" rx="3" fill="#fdf3e2" opacity="0.35"/>'
            )
            svg.append("</g>")
            svg.append(
                f'<text x="{cx:.1f}" y="{cy + 4:.1f}" text-anchor="middle" font-size="9" font-weight="700" font-family="Segoe UI" fill="#263238">{escape(p["plot_id"])}</text>'
            )
            svg.append(
                f'<text x="{cx:.1f}" y="{cy + 15:.1f}" text-anchor="middle" font-size="8" font-family="Consolas" fill="#3d4a40">{escape(p["object_id"][:22])}</text>'
            )
        elif role == "character_spawn":
            svg.append(
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="10" fill="#72A96B" stroke="#263238" stroke-width="1.2" opacity="0.9"/>'
            )
            svg.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4" fill="#fdf3e2"/>')
            name = p.get("character_name") or p["object_id"]
            svg.append(
                f'<text x="{cx:.1f}" y="{cy + 22:.1f}" text-anchor="middle" font-size="8" font-family="Segoe UI" fill="#1b4332">{escape(str(name))}</text>'
            )
        else:
            svg.append(
                f'<rect x="{cx - 7:.1f}" y="{cy - 7:.1f}" width="14" height="14" rx="3" fill="#fdf3e2" stroke="{col}" stroke-width="1.4"/>'
            )
            tag = p["plot_id"].split(".")[-1]
            svg.append(
                f'<text x="{cx:.1f}" y="{cy + 3:.1f}" text-anchor="middle" font-size="7" font-family="Consolas" fill="#5a655c">{escape(tag)}</text>'
            )

    svg.append(
        f'''
<g transform="translate({w - 70},{80})">
  <polygon points="0,-28 10,10 -10,10" fill="#263238"/>
  <text x="0" y="28" text-anchor="middle" font-size="12" font-weight="700" fill="#263238">N (+Z)</text>
</g>
<text x="{w / 2}" y="28" text-anchor="middle" font-size="20" font-weight="700" font-family="Segoe UI" fill="#263238">AIdle Cozy Starter Town — Masterplan Mockup V1</text>
<text x="{w / 2}" y="48" text-anchor="middle" font-size="12" font-family="Segoe UI" fill="#5a655c">50 plots · 10 districts · lưới 2m · content ±11.5 · cadastre ±12 · MOCKUP_SSOT_V2</text>
<g transform="translate(24,{h - 160})">
  <rect width="240" height="145" rx="10" fill="#fffaf0" stroke="#e8d9c0"/>
  <text x="12" y="22" font-size="12" font-weight="700" fill="#263238">Chú giải</text>
  <rect x="12" y="34" width="18" height="14" rx="2" fill="#f5c451" opacity="0.7" stroke="#263238"/>
  <text x="36" y="45" font-size="11" fill="#263238">Building footprint</text>
  <circle cx="21" cy="64" r="7" fill="#72A96B" stroke="#263238"/>
  <text x="36" y="68" font-size="11" fill="#263238">Character spawn</text>
  <rect x="14" y="80" width="12" height="12" rx="2" fill="#fdf3e2" stroke="#c98a5e"/>
  <text x="36" y="90" font-size="11" fill="#263238">Prop plot</text>
  <line x1="12" y1="108" x2="40" y2="108" stroke="#c9b98a" stroke-width="5"/>
  <text x="48" y="112" font-size="11" fill="#263238">Đường vành đai / lối</text>
  <text x="12" y="132" font-size="10" fill="#5a655c">x=+Đông · z=+Bắc · y=lên · accepted=false</text>
</g>
</svg>
'''
    )
    (OUT / "TOWN_MASTERPLAN_MOCKUP_V1.svg").write_text("".join(svg), encoding="utf-8")

    # HTML
    js_plots = json.dumps(enriched, ensure_ascii=False)
    js_dist = json.dumps(master["districts"], ensure_ascii=False)
    js_pr = json.dumps(principles, ensure_ascii=False)
    js_roads = json.dumps(roads, ensure_ascii=False)
    js_lu = json.dumps(land_use, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>AIdle — Mockup Quy hoạch Thị trấn V1</title>
<style>
:root {{
  --cream:#fdf3e2; --ink:#263238; --leaf:#72A96B; --wood:#c98a5e;
  --border:#e8d9c0; --card:#fffaf0; --sub:#5a655c;
}}
* {{ box-sizing:border-box; }}
body {{ margin:0; font-family:"Segoe UI",system-ui,sans-serif; color:var(--ink);
  background: linear-gradient(180deg,#e8f4f8 0%,#f7f0e4 40%,#efe6d4 100%); }}
header {{ max-width:1440px; margin:0 auto; padding:24px 20px 8px; }}
h1 {{ margin:0 0 6px; font-size:1.55rem; }}
.sub {{ color:var(--sub); font-size:0.95rem; max-width:90ch; line-height:1.5; }}
.badge {{ display:inline-block; background:var(--cream); border:1px solid var(--border);
  border-radius:999px; padding:3px 10px; font-size:0.78rem; margin:4px 4px 0 0; }}
.badge.lock {{ background:#1b4332; color:#e8f5e9; }}
.badge.warn {{ background:#fff4d6; }}
.layout {{ max-width:1440px; margin:0 auto; padding:8px 20px 36px;
  display:grid; grid-template-columns:1.35fr 360px; gap:16px; }}
@media (max-width:1100px) {{ .layout {{ grid-template-columns:1fr; }} }}
.map-panel {{ background:var(--card); border:1px solid var(--border); border-radius:16px;
  overflow:hidden; box-shadow:0 10px 28px rgba(38,50,56,.08); }}
.map-toolbar {{ display:flex; flex-wrap:wrap; gap:8px; padding:10px 12px; border-bottom:1px solid var(--border);
  background:#faf6ee; align-items:center; }}
.map-toolbar select, .map-toolbar a {{ font-size:.8rem; padding:5px 10px; border-radius:8px;
  border:1px solid var(--border); background:#fff; text-decoration:none; color:var(--ink); }}
.map-wrap {{ overflow:auto; max-height:78vh; background:#f3ebe0; }}
.map-wrap img {{ display:block; width:100%; height:auto; }}
.hint {{ font-size:.75rem; color:var(--sub); padding:8px 12px 12px; margin:0; }}
.side {{ display:flex; flex-direction:column; gap:12px; }}
.card {{ background:var(--card); border:1px solid var(--border); border-radius:14px; padding:12px 14px; }}
.card h2 {{ margin:0 0 8px; font-size:1rem; border-left:3px solid var(--leaf); padding-left:8px; }}
.meta {{ font-size:.74rem; font-family:ui-monospace,Consolas,monospace; color:var(--sub); }}
.list {{ max-height:36vh; overflow:auto; display:flex; flex-direction:column; gap:6px; }}
.item {{ border:1px solid var(--border); border-radius:10px; padding:8px 10px; cursor:pointer; background:#fff; }}
.item:hover, .item.sel {{ background:#f0f7e8; border-color:#b7d4a8; }}
.item .pid {{ font-weight:700; font-size:.85rem; }}
.thumb {{ width:100%; border-radius:10px; border:1px solid var(--border); max-height:140px; object-fit:cover; background:#eee; }}
.row {{ display:grid; grid-template-columns:96px 1fr; gap:4px 8px; font-size:.82rem; margin:3px 0; }}
.k {{ color:var(--sub); }}
.principles {{ font-size:.82rem; line-height:1.45; padding-left:18px; margin:0; }}
.lu {{ display:flex; flex-wrap:wrap; gap:6px; }}
.lu span {{ font-size:.72rem; padding:3px 8px; border-radius:999px; border:1px solid var(--border); }}
footer {{ max-width:1440px; margin:0 auto; padding:0 20px 40px; font-size:.82rem; color:var(--sub); }}
</style>
</head>
<body>
<header>
  <h1>Mockup quy hoạch thị trấn Cozy — Masterplan V1</h1>
  <p class="sub">
    Bản đồ quy hoạch chi tiết: <strong>10 district</strong>, <strong>50 thửa</strong>
    (10 building + 30 prop + 10 character), lưới 2m, đường vành đai + lối phụ,
    vùng sử dụng đất, ưu tiên xây dựng, gắn art MOCKUP_SSOT_V2. Đây là
    <strong>design masterplan</strong> (chưa product-accept).
  </p>
  <span class="badge lock">DESIGN_MASTERPLAN_ACTIVE</span>
  <span class="badge">50 plots</span>
  <span class="badge">10 districts</span>
  <span class="badge">±11.5 content · ±12 cadastre</span>
  <span class="badge warn">accepted=false · self_accept=false</span>
</header>
<div class="layout">
  <div class="map-panel">
    <div class="map-toolbar">
      <label>District
        <select id="fDist"><option value="">Tất cả</option></select>
      </label>
      <label>Role
        <select id="fRole">
          <option value="">Tất cả</option>
          <option value="building">Building</option>
          <option value="prop">Prop</option>
          <option value="character_spawn">Character</option>
        </select>
      </label>
      <a href="TOWN_MASTERPLAN_MOCKUP_V1.svg" target="_blank">SVG full</a>
      <a href="TOWN_MASTERPLAN_MOCKUP_V1.json" target="_blank">JSON</a>
      <a href="TOWN_GRID_PLAN_V1.json" target="_blank">Cadastre source</a>
    </div>
    <div class="map-wrap"><img src="TOWN_MASTERPLAN_MOCKUP_V1.svg" alt="Town masterplan"/></div>
    <p class="hint">Top-down quy hoạch (x=+Đông, z=+Bắc). In-game: camera 2.5D three-quarter. Vòng = district · chữ nhật = building · chấm xanh = character · ô kem = prop · đường be = circulation.</p>
  </div>
  <div class="side">
    <div class="card">
      <h2>Vùng sử dụng đất</h2>
      <div class="lu" id="lu"></div>
    </div>
    <div class="card">
      <h2>District</h2>
      <div class="list" id="distList"></div>
    </div>
    <div class="card">
      <h2>Thửa / Plot (<span id="cnt">0</span>)</h2>
      <div class="list" id="plotList"></div>
    </div>
    <div class="card" id="detail">
      <h2>Chi tiết thửa</h2>
      <p class="meta">Chọn một plot…</p>
    </div>
    <div class="card">
      <h2>Đường / circulation</h2>
      <div class="list" id="roadList"></div>
    </div>
    <div class="card">
      <h2>Nguyên tắc quy hoạch</h2>
      <ol class="principles" id="principles"></ol>
    </div>
  </div>
</div>
<footer>
  <p>TOWN_MASTERPLAN_MOCKUP_V1 · source TOWN_GRID_PLAN_V1 · MOCKUP_SSOT_V2 · design parent masterplan</p>
  <p>Runtime cadastre: <code>game/resources/town/town_grid_plan_v1.json</code> (build parent). Masterplan này là mockup quy hoạch chi tiết để duyệt &amp; bám fidelity.</p>
</footer>
<script>
const PLOTS = {js_plots};
const DISTS = {js_dist};
const PRINCIPLES = {js_pr};
const ROADS = {js_roads};
const LU = {js_lu};
const fDist = document.getElementById('fDist');
const fRole = document.getElementById('fRole');
const plotList = document.getElementById('plotList');
const distList = document.getElementById('distList');
const detail = document.getElementById('detail');
const lu = document.getElementById('lu');
const roadList = document.getElementById('roadList');
LU.forEach(z => {{
  const s = document.createElement('span');
  s.style.background = z.color;
  s.textContent = z.name + ' · ' + z.districts.join('/');
  lu.appendChild(s);
}});
DISTS.forEach(d => {{
  const o = document.createElement('option');
  o.value = d.district_id;
  o.textContent = d.display_name + ' (' + d.district_id + ')';
  fDist.appendChild(o);
  const el = document.createElement('div');
  el.className = 'item';
  el.innerHTML = '<div class="pid" style="border-left:4px solid '+d.color+';padding-left:6px">'+d.display_name+'</div>'
    + '<div class="meta">'+d.district_id+' · center ('+d.center.x+', '+d.center.z+')</div>';
  el.onclick = () => {{ fDist.value = d.district_id; render(); }};
  distList.appendChild(el);
}});
Object.keys(ROADS).forEach(k => {{
  const r = ROADS[k];
  const el = document.createElement('div');
  el.className = 'item';
  el.innerHTML = '<div class="pid">'+r.name+'</div><div class="meta">'+r.class+' · w='+r.width_m+'m</div><div class="meta">'+r.function_vi+'</div>';
  roadList.appendChild(el);
}});
document.getElementById('principles').innerHTML = PRINCIPLES.map(p => '<li>'+p+'</li>').join('');
function filtered() {{
  return PLOTS.filter(p => {{
    if (fDist.value && p.district !== fDist.value) return false;
    if (fRole.value && p.role !== fRole.value) return false;
    return true;
  }});
}}
function show(p) {{
  const img = p.mockup_img
    ? '<img class="thumb" src="'+p.mockup_img+'" alt="" onerror="this.style.display=\\'none\\'"/>'
    : '';
  detail.innerHTML = '<h2>'+p.plot_id+'</h2>'+img
    + '<div class="row"><span class="k">Tên / ID</span><span>'+(p.display_name||p.object_id)+'<br><span class="meta">'+p.object_id+'</span></span></div>'
    + '<div class="row"><span class="k">Role</span><span>'+p.role+'</span></div>'
    + '<div class="row"><span class="k">District</span><span>'+p.district+'</span></div>'
    + '<div class="row"><span class="k">Grid</span><span class="meta">'+(p.grid_cell||'—')+' · occ '+((p.occupancy_cells||[]).join(', ')||'—')+'</span></div>'
    + '<div class="row"><span class="k">XYZ / rot</span><span class="meta">('+p.transform.x+', '+p.transform.y+', '+p.transform.z+') · '+p.transform.rotation_deg+'°</span></div>'
    + '<div class="row"><span class="k">Footprint</span><span class="meta">'+JSON.stringify(p.footprint_units||null)+'</span></div>'
    + '<div class="row"><span class="k">Priority</span><span>P'+(p.planning&&p.planning.build_priority)+' · setback '+(p.planning&&p.planning.setback_m)+'m</span></div>'
    + '<div class="row"><span class="k">Ghi chú</span><span>'+(p.planning&&p.planning.notes_vi||'')+'</span></div>';
}}
function render() {{
  const list = filtered();
  document.getElementById('cnt').textContent = list.length;
  plotList.innerHTML = '';
  list.forEach(p => {{
    const el = document.createElement('div');
    el.className = 'item';
    el.innerHTML = '<div class="pid">'+p.plot_id+'</div>'
      + '<div class="meta">'+p.role+' · '+p.object_id+'</div>'
      + '<div class="meta">('+p.transform.x+', '+p.transform.z+') · '+(p.grid_cell||'')+'</div>';
    el.onclick = () => {{
      document.querySelectorAll('.item.sel').forEach(x => x.classList.remove('sel'));
      el.classList.add('sel');
      show(p);
    }};
    plotList.appendChild(el);
  }});
}}
fDist.onchange = render;
fRole.onchange = render;
render();
</script>
</body>
</html>
"""
    (OUT / "TOWN_MASTERPLAN_MOCKUP_V1.html").write_text(html, encoding="utf-8")

    readme = """# TOWN MASTERPLAN MOCKUP V1

**Status:** `DESIGN_MASTERPLAN_ACTIVE` · **accepted=false** · **self_accept=false**

## Mở file

| File | Mục đích |
|------|----------|
| `TOWN_MASTERPLAN_MOCKUP_V1.html` | Mockup quy hoạch tương tác (duyệt district/plot/art) |
| `TOWN_MASTERPLAN_MOCKUP_V1.svg` | Bản đồ in / zoom full |
| `TOWN_MASTERPLAN_MOCKUP_V1.json` | Index máy (roads, land use, plots enriched) |
| `TOWN_GRID_PLAN_V1.json` | Cadastre pháp lý 50 plot (source cells/coords) |

## Nội dung chi tiết

- 10 district + màu + tâm
- 50 thửa: building / prop / character_spawn
- Lưới 2m A–L × 1–12
- Circulation: vành đai + 4 nhánh
- Land-use zones
- Ưu tiên xây P1–P4
- Link art MOCKUP_SSOT_V2
- Bounds content ±11.5 / cadastre ±12

## Quan hệ runtime

Build parent import: `game/resources/town/town_grid_plan_v1.json`.  
Masterplan này là **design mockup quy hoạch** — không tự claim ship / game patch.
"""
    (OUT / "TOWN_MASTERPLAN_MOCKUP_V1_README.md").write_text(readme, encoding="utf-8")
    print("OK", OUT)
    print("plots", len(enriched), "svg", w, "x", h)
    print("fingerprint", master["payload_fingerprint"][:16])


if __name__ == "__main__":
    main()
