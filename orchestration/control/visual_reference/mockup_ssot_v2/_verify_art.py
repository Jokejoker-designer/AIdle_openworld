from pathlib import Path
import json

p = Path(__file__).resolve().parent
d = json.loads((p / "MOCKUP_SSOT_V2.json").read_text(encoding="utf-8"))
missb = [x["id"] for x in d["buildings"] if not (p / x["img"]).exists()]
missp = [x["id"] for x in d["props"] if not (p / x["img"]).exists()]
print("bld", len(d["buildings"]), "miss", missb)
print("prop", len(d["props"]), "miss", missp)
h = (p / "MOCKUP_SSOT_V2.html").read_text(encoding="utf-8")
print("has_svg_ico", 'class="ico"' in h)
print("has_bld03", "bld_03_barn" in h)
print("has_pine", "prop_tree_pine" in h)
print("has_campfire", "prop_campfire" in h)
print("html_bytes", len(h.encode("utf-8")))
