from pathlib import Path
src = list(Path(r"E:/AIdle_openworld/orchestration/control/character_build").glob("*house*v8*.py"))[0]
t = src.read_text(encoding="utf-8")
t = t.replace("COZY_HOUSE_MOCKUP_V8","COZY_HOUSE_MOCKUP_V9").replace("mockup_match_v8","mockup_match_v9").replace("_preview_v8","_preview_v9")
# remove black X gable ends
t = t.replace('cube("GableEndL", (-0.68, 0, 1.45), (0.12, 0.95, 0.55), M["wall"], 0.06)\n', '')
t = t.replace('cube("GableEndR", (0.68, 0, 1.45), (0.12, 0.95, 0.55), M["wall"], 0.06)\n', '')
# thicker attic under roof
if 'cube("Attic"' not in t:
    t = t.replace(
        'cube("Body", (0, 0, 0.68), (1.28, 1.12, 1.15), M["wall"], 0.16)',
        'cube("Body", (0, 0, 0.68), (1.28, 1.12, 1.15), M["wall"], 0.16)\n    cube("Attic", (0, 0, 1.30), (1.30, 1.10, 0.35), M["wall"], 0.10)'
    )
out = Path(r"E:/AIdle_openworld/orchestration/control/character_build/author_cozy_house_mockup_v9.py")
out.write_text(t, encoding="utf-8")
print("ok")
