from pathlib import Path
src = list(Path(r"E:/AIdle_openworld/orchestration/control/character_build").glob("*house*v6*.py"))[0]
t = src.read_text(encoding="utf-8")
t = t.replace("COZY_HOUSE_MOCKUP_V6","COZY_HOUSE_MOCKUP_V7").replace("mockup_match_v6","mockup_match_v7").replace("_preview_v6","_preview_v7")
# stronger roof colors
t = t.replace('"roof_a": (0.99, 0.76, 0.40)','"roof_a": (0.99, 0.70, 0.32)')
t = t.replace('"roof_b": (1.00, 0.88, 0.42)','"roof_b": (1.00, 0.86, 0.35)')
t = t.replace('"roof_c": (0.98, 0.80, 0.52)','"roof_c": (0.99, 0.78, 0.45)')
# denser front tiles
t = t.replace("for row in range(7):","for row in range(8):")
t = t.replace("t = row / 6.0","t = row / 7.0")
t = t.replace("n_col = 9","n_col = 10")
t = t.replace("0.165","0.155")
# bigger door wall fill
t = t.replace('cube("DoorWall", (0, 0.50, 0.50), (0.44, 0.12, 0.78), M["wall"], 0.05)',
              'cube("DoorWall", (0, 0.48, 0.50), (0.55, 0.18, 0.90), M["wall"], 0.06)')
# thinner gable slabs so tiles dominate
t = t.replace("o.scale = (1.50, 0.92, 0.18)","o.scale = (1.48, 0.90, 0.12)")
out = Path(r"E:/AIdle_openworld/orchestration/control/character_build/author_cozy_house_mockup_v7.py")
out.write_text(t, encoding="utf-8")
print("ok", out)
