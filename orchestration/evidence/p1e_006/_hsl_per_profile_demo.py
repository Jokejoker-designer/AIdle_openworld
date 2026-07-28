"""Per-world-profile HSL targets + washed-out Surrealism fail demo (WO-P1E-006)."""
from __future__ import annotations

import colorsys
import json
import sys
from pathlib import Path

# Cozy water target (bible)
COZY_WATER = (143, 212, 232)
# Surrealism water target from catalog (readable purple-water)
SURREAL_WATER = (89, 82, 158)  # ~0.35,0.32,0.62 * 255
# Deliberately washed-out Surrealism (lavender white — the human failure mode)
WASHED_SURREAL = (200, 190, 210)


def hsv(rgb):
    r, g, b = [c / 255.0 for c in rgb]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return {
        "rgb": list(rgb),
        "hue_deg": h * 360.0,
        "sat": s * 100.0,
        "val": v * 100.0,
        "rb_spread": int(rgb[2]) - int(rgb[0]),
    }


def eval_cozy(rgb):
    h = hsv(rgb)
    reasons = []
    dh = abs(h["hue_deg"] - 193.0)
    if dh > 180:
        dh = 360 - dh
    if dh > 35:
        reasons.append(f"hue {h['hue_deg']:.1f}")
    if h["sat"] < 18:
        reasons.append(f"sat {h['sat']:.1f}")
    if h["rb_spread"] < 20:
        reasons.append(f"rb {h['rb_spread']}")
    if rgb[0] >= 250 and rgb[1] >= 250 and rgb[2] >= 250:
        reasons.append("white")
    return {"profile": "cozy_cyber_pixel", "pass": not reasons, "hsv": h, "fail_reasons": reasons}


def eval_surreal(rgb):
    h = hsv(rgb)
    reasons = []
    # Purple-blue water band ~220-300 or cool purple
    hue = h["hue_deg"]
    in_band = (200 <= hue <= 310) or (hue <= 20)  # purple-magenta range
    # Also accept high-blue chromatic water-like
    if h["sat"] < 18:
        reasons.append(f"sat_too_low {h['sat']:.1f} (washed)")
    if not in_band and h["sat"] >= 18:
        # allow if clearly chromatic and not beige/green-grey
        if hue < 150 or hue > 200:
            if not (220 <= hue <= 300):
                reasons.append(f"hue_out_of_water_band {hue:.1f}")
    if rgb[0] >= 250 and rgb[1] >= 250 and rgb[2] >= 250:
        reasons.append("white")
    # lavender wash: high val, low sat, near equal RGB
    if h["val"] > 75 and h["sat"] < 18:
        reasons.append("lavender_wash")
    return {"profile": "surrealism_canvas", "pass": not reasons, "hsv": h, "fail_reasons": reasons}


def main():
    rows = [
        ("cozy_bible", eval_cozy(COZY_WATER)),
        ("surreal_target", eval_surreal(SURREAL_WATER)),
        ("washed_surreal_deliberate", eval_surreal(WASHED_SURREAL)),
        ("beige", eval_cozy((218, 209, 195))),
        ("white", eval_cozy((255, 255, 255))),
        ("grey", eval_cozy((185, 195, 189))),
    ]
    # Expected: cozy_bible PASS, surreal_target PASS, washed FAIL, beige/white/grey FAIL under cozy
    expected = {
        "cozy_bible": True,
        "surreal_target": True,
        "washed_surreal_deliberate": False,
        "beige": False,
        "white": False,
        "grey": False,
    }
    out = {"demo": "p1e006_per_profile_hsl", "results": []}
    ok = True
    for name, r in rows:
        exp = expected[name]
        match = r["pass"] == exp
        if not match:
            ok = False
        out["results"].append({"label": name, "expected_pass": exp, "actual_pass": r["pass"], "match": match, **r})
    out["pass"] = ok
    print(json.dumps(out, indent=2))
    Path(r"E:/AIdle_openworld/orchestration/evidence/p1e_006/hsl_per_profile_demo.json").parent.mkdir(
        parents=True, exist_ok=True
    )
    Path(r"E:/AIdle_openworld/orchestration/evidence/p1e_006/hsl_per_profile_demo.json").write_text(
        json.dumps(out, indent=2) + "\n", encoding="utf-8"
    )
    print("P1E006_HSL_DEMO=" + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
