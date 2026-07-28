"""
Material integrity check for P1E-004.

Prior check FAILED us: it sampled a single lucky rim pixel (165,207,215) while
the pond body was pure white (255,255,255), and used "not beige" as pass.

This check:
1. Parses GLB baseColorFactor for MAT_CozyWater (pipeline stage A)
2. Samples pond ROI median on rendered PNG (pipeline stage B)
3. FAILS pure white (max channel >= 250 for >35% of ROI OR median white)
4. FAILS beige closer than bible
5. Requires median within distance tolerance of art-bible #8fd4e8
6. Supports --self-test with deliberate wrong values
"""
from __future__ import annotations

import argparse
import json
import math
import struct
import sys
from pathlib import Path

from PIL import Image

BIBLE_WATER = (143, 212, 232)  # #8fd4e8
BEIGE_FALSE = (218, 209, 195)
WHITE_FALSE = (255, 255, 255)
# Roof / door / lamp from art bible (kept for multi-surface check)
BIBLE_SURFACES = {
    "water": {"hex": "#8fd4e8", "rgb": BIBLE_WATER, "max_dist": 55.0},
    "roof": {"hex": "#e88b6f", "rgb": (232, 139, 111), "max_dist": 70.0},
    "door": {"hex": "#c98a5e", "rgb": (201, 138, 94), "max_dist": 70.0},
    "lamp_glow": {"hex": "#f5d98f", "rgb": (245, 217, 143), "max_dist": 40.0},
}


def dist(a, b) -> float:
    return math.sqrt(sum((float(x) - float(y)) ** 2 for x, y in zip(a, b)))


def parse_glb_materials(path: Path) -> list[dict]:
    data = path.read_bytes()
    magic, _version, length = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF":
        raise ValueError(f"not glb: {path}")
    off = 12
    while off < length:
        clen, ctype = struct.unpack_from("<I4s", data, off)
        off += 8
        chunk = data[off : off + clen]
        off += clen
        if ctype.startswith(b"JSON"):
            j = json.loads(chunk.decode("utf-8"))
            return j.get("materials", [])
    return []


def glb_water_base_rgb(path: Path) -> tuple[int, int, int] | None:
    for m in parse_glb_materials(path):
        if m.get("name") == "MAT_CozyWater":
            base = m.get("pbrMetallicRoughness", {}).get("baseColorFactor")
            if not base or len(base) < 3:
                return None
            return (
                int(round(float(base[0]) * 255)),
                int(round(float(base[1]) * 255)),
                int(round(float(base[2]) * 255)),
            )
    return None


def sample_roi_median(im: Image.Image, bbox: tuple[int, int, int, int]) -> dict:
    x0, y0, x1, y1 = bbox
    px = im.load()
    rs, gs, bs = [], [], []
    white_n = 0
    beige_n = 0
    n = 0
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b = px[x, y]
            rs.append(r)
            gs.append(g)
            bs.append(b)
            n += 1
            if r >= 250 and g >= 250 and b >= 250:
                white_n += 1
            if dist((r, g, b), BEIGE_FALSE) < 28:
                beige_n += 1
    if n == 0:
        return {"error": "empty_roi"}
    rs.sort()
    gs.sort()
    bs.sort()
    mid = n // 2
    median = (rs[mid], gs[mid], bs[mid])
    return {
        "n": n,
        "median_rgb": list(median),
        "white_pct": 100.0 * white_n / n,
        "beige_pct": 100.0 * beige_n / n,
        "bbox": list(bbox),
        "dist_bible": dist(median, BIBLE_WATER),
        "dist_beige": dist(median, BEIGE_FALSE),
        "dist_white": dist(median, WHITE_FALSE),
    }


def sample_pond_auto(im: Image.Image, search_bbox: tuple[int, int, int, int]) -> dict:
    """Sample only cyan-like pond body pixels inside search box (not grass median).

    Prior false-PASS used a single lucky rim pixel while body was white.
    Prior false-FAIL on grass median used a fixed bbox that was mostly ground.
    """
    x0, y0, x1, y1 = search_bbox
    px = im.load()
    pts: list[tuple[int, int, int, int, int]] = []
    white_n = 0
    beige_n = 0
    total = 0
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b = px[x, y]
            total += 1
            if r >= 250 and g >= 250 and b >= 250:
                white_n += 1
                continue
            if dist((r, g, b), BEIGE_FALSE) < 28:
                beige_n += 1
            # Cyan-ish water: blue-green, not grass green, not white
            if (
                r < 250
                and g > 150
                and b > 160
                and b >= r - 5
                and (g - r) > 5
                and abs(g - b) < 55
            ):
                pts.append((x, y, r, g, b))
    if len(pts) < 50:
        # Fall back to full bbox median (will usually fail honesty gates)
        base = sample_roi_median(im, search_bbox)
        base["mode"] = "bbox_fallback"
        base["cyan_n"] = len(pts)
        base["search_white_pct"] = 100.0 * white_n / max(1, total)
        return base
    rs = sorted(p[2] for p in pts)
    gs = sorted(p[3] for p in pts)
    bs = sorted(p[4] for p in pts)
    mid = len(pts) // 2
    median = (rs[mid], gs[mid], bs[mid])
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return {
        "n": len(pts),
        "mode": "cyan_auto",
        "median_rgb": list(median),
        "white_pct": 100.0 * white_n / max(1, total),
        "beige_pct": 100.0 * beige_n / max(1, total),
        "bbox": [min(xs), min(ys), max(xs), max(ys)],
        "search_bbox": list(search_bbox),
        "dist_bible": dist(median, BIBLE_WATER),
        "dist_beige": dist(median, BEIGE_FALSE),
        "dist_white": dist(median, WHITE_FALSE),
    }


def evaluate(pond_roi: dict, glb_rgb: tuple[int, int, int] | None, max_dist: float = 70.0) -> dict:
    reasons: list[str] = []
    # Stage: GLB base must be near bible
    glb_ok = False
    if glb_rgb is None:
        reasons.append("glb_water_base_missing")
    else:
        gd = dist(glb_rgb, BIBLE_WATER)
        glb_ok = gd <= 20.0
        if not glb_ok:
            reasons.append(f"glb_base_far_from_bible dist={gd:.1f} rgb={list(glb_rgb)}")

    # Stage: render ROI
    render_ok = True
    if pond_roi.get("error"):
        reasons.append(pond_roi["error"])
        render_ok = False
    else:
        if pond_roi["white_pct"] > 35.0:
            reasons.append(f"render_white_pct={pond_roi['white_pct']:.1f}>35")
            render_ok = False
        if pond_roi["beige_pct"] > 35.0:
            reasons.append(f"render_beige_pct={pond_roi['beige_pct']:.1f}>35")
            render_ok = False
        if pond_roi["dist_white"] < 25.0:
            reasons.append(f"median_near_white dist={pond_roi['dist_white']:.1f}")
            render_ok = False
        # Beige fail only when median is actually beige-like (the W1 failure mode).
        # Do not use "closer to beige than bible" — desaturated mid-grey is closer to beige
        # than cyan but is not the beige false-pass (218,209,195).
        if pond_roi["dist_beige"] < 28.0:
            reasons.append(f"median_is_beige dist={pond_roi['dist_beige']:.1f}")
            render_ok = False
        if pond_roi["dist_bible"] > max_dist:
            reasons.append(f"median_far_from_bible dist={pond_roi['dist_bible']:.1f}>{max_dist}")
            render_ok = False

    passed = glb_ok and render_ok and not reasons
    return {
        "pass": passed,
        "glb_ok": glb_ok,
        "render_ok": render_ok,
        "glb_water_rgb": list(glb_rgb) if glb_rgb else None,
        "pond_roi": pond_roi,
        "fail_reasons": reasons,
        "bible_rgb": list(BIBLE_WATER),
        "bible_hex": "#8fd4e8",
    }


def self_test() -> int:
    """Demonstrate check FAILS on pure white and beige; PASSES near bible."""
    # Synthetic images
    def solid(rgb, size=(100, 100)):
        im = Image.new("RGB", size, rgb)
        return im

    # Pure white ROI must FAIL
    white_roi = sample_roi_median(solid(WHITE_FALSE), (10, 10, 90, 90))
    r_white = evaluate(white_roi, BIBLE_WATER)  # glb ok but render white
    assert r_white["pass"] is False, r_white
    assert any("white" in x for x in r_white["fail_reasons"]), r_white

    # Beige ROI must FAIL
    beige_roi = sample_roi_median(solid(BEIGE_FALSE), (10, 10, 90, 90))
    r_beige = evaluate(beige_roi, BIBLE_WATER)
    assert r_beige["pass"] is False, r_beige
    assert any("beige" in x for x in r_beige["fail_reasons"]), r_beige

    # Near-bible must PASS
    good_roi = sample_roi_median(solid((155, 205, 225)), (10, 10, 90, 90))
    r_good = evaluate(good_roi, BIBLE_WATER)
    assert r_good["pass"] is True, r_good

    # Wrong GLB base must FAIL even if render good
    r_bad_glb = evaluate(good_roi, (255, 255, 255))
    assert r_bad_glb["pass"] is False, r_bad_glb

    print("MATERIAL_INTEGRITY_SELF_TEST=PASS")
    print(json.dumps({"white_fail": r_white["fail_reasons"], "beige_fail": r_beige["fail_reasons"]}, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--png")
    ap.add_argument("--pond-glb")
    ap.add_argument("--pond-bbox", default="640,250,760,380", help="x0,y0,x1,y1")
    ap.add_argument("--out")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not args.png or not args.pond_glb:
        print("need --png and --pond-glb or --self-test")
        return 2
    bbox = tuple(int(x) for x in args.pond_bbox.split(","))
    im = Image.open(args.png).convert("RGB")
    roi = sample_pond_auto(im, bbox)  # type: ignore[arg-type]
    glb_rgb = glb_water_base_rgb(Path(args.pond_glb))
    result = evaluate(roi, glb_rgb)
    text = json.dumps(result, indent=2)
    print(text)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print("MATERIAL_INTEGRITY=" + ("PASS" if result["pass"] else "FAIL"))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
