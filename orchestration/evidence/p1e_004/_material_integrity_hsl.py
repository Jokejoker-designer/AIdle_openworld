"""
P1E-004 CORRECTION — material integrity on HUE + SATURATION (not RGB channel distance).

Historical false-passes under RGB distance:
  beige  (218,209,195) — sat low, wrong hue
  white  (255,255,255) — sat 0
  grey   (185,195,189) — sat ~5%, achromatic (current false-PASS under RGB)

Target water #8fd4e8 (143,212,232): hue ~193°, sat ~38%.
"""
from __future__ import annotations

import argparse
import colorsys
import json
import math
import struct
import sys
from pathlib import Path

from PIL import Image

BIBLE = (143, 212, 232)
BEIGE = (218, 209, 195)
WHITE = (255, 255, 255)
GREY_WASH = (185, 195, 189)  # current false-pass under RGB distance


def rgb_to_hsv255(rgb: tuple[int, int, int]) -> dict:
    r, g, b = [c / 255.0 for c in rgb]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return {
        "rgb": list(rgb),
        "hue_deg": h * 360.0,
        "sat": s * 100.0,
        "val": v * 100.0,
        "rb_spread": int(rgb[2]) - int(rgb[0]),
    }


# Tolerances chosen so bible passes and all three historical failures fail.
HUE_TARGET = 193.0
HUE_TOL = 28.0  # cyan-blue band
SAT_MIN = 22.0  # achromatic grey/white/beige fail
VAL_MAX = 98.0  # pure white fail even if somehow saturated
RB_SPREAD_MIN = 25  # bible has ~89; grey has ~4


def evaluate_sample(rgb: tuple[int, int, int], label: str = "") -> dict:
    hsv = rgb_to_hsv255(rgb)
    reasons: list[str] = []
    hue = hsv["hue_deg"]
    sat = hsv["sat"]
    val = hsv["val"]
    spread = hsv["rb_spread"]

    # Hue wrap-safe distance
    dh = abs(hue - HUE_TARGET)
    if dh > 180:
        dh = 360 - dh
    if dh > HUE_TOL:
        reasons.append(f"hue_out_of_band hue={hue:.1f} target={HUE_TARGET}±{HUE_TOL}")
    if sat < SAT_MIN:
        reasons.append(f"sat_too_low sat={sat:.1f}% < {SAT_MIN}% (achromatic)")
    if val >= VAL_MAX and sat < 15.0:
        reasons.append(f"near_white val={val:.1f}% sat={sat:.1f}%")
    if spread < RB_SPREAD_MIN:
        reasons.append(f"rb_spread_too_low spread={spread} < {RB_SPREAD_MIN}")

    return {
        "label": label,
        "pass": len(reasons) == 0,
        "hsv": hsv,
        "hue_delta": dh,
        "fail_reasons": reasons,
    }


def four_value_demo() -> dict:
    rows = [
        evaluate_sample(BEIGE, "beige_218_209_195"),
        evaluate_sample(WHITE, "white_255_255_255"),
        evaluate_sample(GREY_WASH, "grey_185_195_189"),
        evaluate_sample(BIBLE, "bible_143_212_232"),
    ]
    expected = {
        "beige_218_209_195": False,
        "white_255_255_255": False,
        "grey_185_195_189": False,
        "bible_143_212_232": True,
    }
    ok = all(r["pass"] == expected[r["label"]] for r in rows)
    return {
        "demo": "four_value_hsl",
        "pass": ok,
        "results": rows,
        "expected": expected,
        "tolerances": {
            "hue_target_deg": HUE_TARGET,
            "hue_tol_deg": HUE_TOL,
            "sat_min_pct": SAT_MIN,
            "val_max_near_white": VAL_MAX,
            "rb_spread_min": RB_SPREAD_MIN,
        },
    }


def parse_glb_water(path: Path) -> tuple[int, int, int] | None:
    data = path.read_bytes()
    magic, _v, length = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF":
        return None
    off = 12
    while off < length:
        clen, ctype = struct.unpack_from("<I4s", data, off)
        off += 8
        chunk = data[off : off + clen]
        off += clen
        if ctype.startswith(b"JSON"):
            j = json.loads(chunk.decode("utf-8"))
            for m in j.get("materials", []):
                if m.get("name") == "MAT_CozyWater":
                    base = m.get("pbrMetallicRoughness", {}).get("baseColorFactor")
                    if base and len(base) >= 3:
                        return (
                            int(round(float(base[0]) * 255)),
                            int(round(float(base[1]) * 255)),
                            int(round(float(base[2]) * 255)),
                        )
    return None


def sample_pond_median(im: Image.Image, search_bbox: tuple[int, int, int, int]) -> dict:
    """Sample pond body by highest-saturation cyan-band pixels (not grass median)."""
    x0, y0, x1, y1 = search_bbox
    px = im.load()
    scored: list[tuple[float, int, int, int]] = []
    white_n = total = 0
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b = px[x, y]
            total += 1
            if r >= 250 and g >= 250 and b >= 250:
                white_n += 1
                continue
            hsv = rgb_to_hsv255((r, g, b))
            # Cyan-blue band candidates
            if 150.0 <= hsv["hue_deg"] <= 220.0 and hsv["sat"] >= 8.0 and b > r:
                scored.append((hsv["sat"], r, g, b))
    if len(scored) < 30:
        # fallback: any pixel with B-R spread
        for y in range(y0, y1):
            for x in range(x0, x1):
                r, g, b = px[x, y]
                if b - r >= 20 and b > 140:
                    hsv = rgb_to_hsv255((r, g, b))
                    scored.append((hsv["sat"], r, g, b))
    if len(scored) < 20:
        return {"error": "too_few_pond_pixels", "n": len(scored)}
    scored.sort(key=lambda t: t[0], reverse=True)
    # Use top-half by saturation so rim/desat grass does not dominate
    top = scored[: max(20, len(scored) // 2)]
    rs = sorted(t[1] for t in top)
    gs = sorted(t[2] for t in top)
    bs = sorted(t[3] for t in top)
    m = len(top) // 2
    med = (rs[m], gs[m], bs[m])
    return {
        "n": len(top),
        "candidates": len(scored),
        "median_rgb": list(med),
        "white_pct": 100.0 * white_n / max(1, total),
        "hsv": rgb_to_hsv255(med),
        "eval": evaluate_sample(med, "pond_median"),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--four-value-demo", action="store_true")
    ap.add_argument("--png")
    ap.add_argument("--pond-glb")
    ap.add_argument("--pond-bbox", default="640,250,760,380")
    ap.add_argument("--out")
    args = ap.parse_args()

    if args.four_value_demo:
        demo = four_value_demo()
        text = json.dumps(demo, indent=2)
        print(text)
        if args.out:
            Path(args.out).write_text(text, encoding="utf-8")
        print("FOUR_VALUE_DEMO=" + ("PASS" if demo["pass"] else "FAIL"))
        return 0 if demo["pass"] else 1

    if not args.png or not args.pond_glb:
        print("need --four-value-demo or --png + --pond-glb")
        return 2

    bbox = tuple(int(x) for x in args.pond_bbox.split(","))
    im = Image.open(args.png).convert("RGB")
    pond = sample_pond_median(im, bbox)  # type: ignore[arg-type]
    glb = parse_glb_water(Path(args.pond_glb))
    glb_eval = evaluate_sample(glb, "glb_base") if glb else None

    reasons: list[str] = []
    if glb is None:
        reasons.append("glb_water_missing")
    elif not glb_eval["pass"]:
        reasons.extend(["glb:" + r for r in glb_eval["fail_reasons"]])
    if pond.get("error"):
        reasons.append(pond["error"])
    elif not pond["eval"]["pass"]:
        reasons.extend(["render:" + r for r in pond["eval"]["fail_reasons"]])

    result = {
        "pass": len(reasons) == 0,
        "method": "hsl_hue_sat_not_rgb_distance",
        "bible": rgb_to_hsv255(BIBLE),
        "glb_water_rgb": list(glb) if glb else None,
        "glb_eval": glb_eval,
        "pond": pond,
        "fail_reasons": reasons,
        "four_value_demo": four_value_demo(),
    }
    text = json.dumps(result, indent=2)
    print(text)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    print("MATERIAL_INTEGRITY_HSL=" + ("PASS" if result["pass"] else "FAIL"))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
