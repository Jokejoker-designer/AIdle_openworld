from pathlib import Path
src = list(Path(r"E:/AIdle_openworld/orchestration/control/character_build").glob("*house*v7*.py"))[0]
t = src.read_text(encoding="utf-8")
t = t.replace("COZY_HOUSE_MOCKUP_V7","COZY_HOUSE_MOCKUP_V8").replace("mockup_match_v7","mockup_match_v8").replace("_preview_v7","_preview_v8")
# flatter fish-scale tiles (mockup scallops are flat ovals)
t = t.replace("o = sph(f\"Tile{row}_{col}\", (x, y, z), 0.108, m, (1.35, 1.15, 0.40))",
              "o = sph(f\"Tile{row}_{col}\", (x, y, z), 0.12, m, (1.55, 1.35, 0.28))")
# slightly larger spacing step for scale look
t = t.replace("* 0.155","* 0.16")
# kill black cavities: solid front face thicker, no arch hole
t = t.replace('cube("Front", (0, 0.48, 0.52), (0.90, 0.16, 0.80), M["wall"], 0.10)',
              'cube("Front", (0, 0.50, 0.55), (1.05, 0.22, 0.95), M["wall"], 0.12)')
# door arch as solid frame only (no open cavity) — replace arch with half sphere decoration
t = t.replace(
    'cyl("DoorArch", (0, 0.62, 0.90), 0.20, 0.05, M["frame"], rot=(math.pi / 2, 0, 0))',
    'sph("DoorArch", (0, 0.64, 0.92), 0.20, M["frame"], (1.0, 0.35, 0.55))'
)
out = Path(r"E:/AIdle_openworld/orchestration/control/character_build/author_cozy_house_mockup_v8.py")
out.write_text(t, encoding="utf-8")
print("wrote", out)
