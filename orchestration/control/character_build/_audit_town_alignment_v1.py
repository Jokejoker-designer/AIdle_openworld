# -*- coding: utf-8 -*-
"""Audit plot transforms vs grid_cell centers; report drifts/overlaps."""
from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

PLAN = Path(r"E:\AIdle_openworld\game\resources\town\town_grid_plan_v1.json")
OUT = Path(r"E:\AIdle_openworld\orchestration\receipts\town_grid_import_001\_alignment_audit_raw.json")


def main() -> int:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    cols = plan["grid"]["cols"]
    rows = plan["grid"]["rows"]
    cs = float(plan["grid"]["cell_size_units"])

    def cell_center(cell: str):
        col = "".join(c for c in cell if c.isalpha())
        row = int("".join(c for c in cell if c.isdigit()))
        ci = cols.index(col)
        ri = rows.index(row)
        f6 = (cols.index("F"), rows.index(6))
        g7 = (cols.index("G"), rows.index(7))
        mid_c = (f6[0] + g7[0]) / 2.0
        mid_r = (f6[1] + g7[1]) / 2.0
        x = (ci - mid_c) * cs
        z = (ri - mid_r) * cs
        return x, z

    drifts = []
    for p in plan["plots"]:
        cell = p.get("grid_cell", "")
        t = p["transform"]
        if not cell:
            continue
        cx, cz = cell_center(cell)
        dx = t["x"] - cx
        dz = t["z"] - cz
        dist = (dx * dx + dz * dz) ** 0.5
        drifts.append(
            {
                "plot_id": p["plot_id"],
                "role": p.get("role"),
                "grid_cell": cell,
                "plan_xz": [t["x"], t["z"]],
                "cell_center_xz": [cx, cz],
                "delta_xz": [dx, dz],
                "dist": dist,
                "rotation_deg": t.get("rotation_deg", 0),
                "scale": t.get("scale", 1),
            }
        )

    drifts_sorted = sorted(drifts, key=lambda d: -d["dist"])
    # Snap candidates: dist > 0.5m from cell center (intentional sub-cell offsets vs drift)
    near_cell = [d for d in drifts if d["dist"] <= 0.5]
    mid_offset = [d for d in drifts if 0.5 < d["dist"] <= 2.5]
    far_offset = [d for d in drifts if d["dist"] > 2.5]

    # rotation neatness: not multiple of 45
    odd_rot = [
        d
        for d in drifts
        if abs(d["rotation_deg"] % 45) > 0.01 and abs(d["rotation_deg"] % 45 - 45) > 0.01
    ]

    blds = [p for p in plan["plots"] if p.get("role") == "building"]
    close_pairs = []
    for a, b in combinations(blds, 2):
        dx = a["transform"]["x"] - b["transform"]["x"]
        dz = a["transform"]["z"] - b["transform"]["z"]
        dist = (dx * dx + dz * dz) ** 0.5
        if dist < 4.5:
            close_pairs.append(
                {
                    "a": a["plot_id"],
                    "b": b["plot_id"],
                    "dist": dist,
                    "a_xz": [a["transform"]["x"], a["transform"]["z"]],
                    "b_xz": [b["transform"]["x"], b["transform"]["z"]],
                }
            )

    report = {
        "cell_size": cs,
        "origin_model": "midpoint of F6 and G7 cell centers = (0,0)",
        "plots": len(drifts),
        "near_cell_center_le_0_5m": len(near_cell),
        "mid_offset_0_5_to_2_5m": len(mid_offset),
        "far_offset_gt_2_5m": len(far_offset),
        "top_drifts": drifts_sorted[:20],
        "far_offsets": far_offset,
        "odd_rotations_not_45_multiple": odd_rot[:25],
        "odd_rot_count": len(odd_rot),
        "building_pairs_dist_lt_4_5": close_pairs,
    }
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in report if k not in ("top_drifts", "far_offsets", "odd_rotations_not_45_multiple")}, indent=2))
    print("top 10 drifts:")
    for d in drifts_sorted[:10]:
        print(
            f"  {d['plot_id']:16} cell={d['grid_cell']:4} plan=({d['plan_xz'][0]:6.2f},{d['plan_xz'][1]:6.2f}) "
            f"cell=({d['cell_center_xz'][0]:6.2f},{d['cell_center_xz'][1]:6.2f}) dist={d['dist']:.2f} rot={d['rotation_deg']}"
        )
    print("far offsets:")
    for d in far_offset:
        print(f"  {d['plot_id']} dist={d['dist']:.2f}")
    print("close building pairs:")
    for p in close_pairs:
        print(f"  {p['a']} <-> {p['b']} dist={p['dist']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
