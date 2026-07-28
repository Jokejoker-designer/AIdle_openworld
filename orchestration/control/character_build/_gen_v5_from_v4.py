from pathlib import Path

src = Path(r"E:/AIdle_openworld/orchestration/control/character_build")
v4 = list(src.glob("*house*v4*.py"))[0]
text = v4.read_text(encoding="utf-8")
text = (
    text.replace("COZY_HOUSE_MOCKUP_V4", "COZY_HOUSE_MOCKUP_V5")
    .replace("mockup_match_v4", "mockup_match_v5")
    .replace("_preview_v4", "_preview_v5")
)

# Apply rotation after setting euler on front tiles
old = """            o = sph(f\"tf{row}_{col}\", (x, y, z), 0.105, mats_r[bi], (1.4, 1.15, 0.38))
            o.rotation_euler = Euler((math.radians(-33), 0, 0), \"XYZ\")
            buckets[bi].append(o)"""
new = """            o = sph(f\"tf{row}_{col}\", (x, y, z), 0.105, mats_r[bi], (1.4, 1.15, 0.38))
            o.rotation_euler = Euler((math.radians(-33), 0, 0), \"XYZ\")
            bpy.context.view_layer.objects.active = o
            o.select_set(True)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            o.select_set(False)
            buckets[bi].append(o)"""
if old not in text:
    raise SystemExit("front tile block missing")
text = text.replace(old, new)

old2 = """            o = sph(f\"tb{row}_{col}\", (x, y, z), 0.10, mats_r[bi], (1.3, 1.05, 0.36))
            o.rotation_euler = Euler((math.radians(33), 0, 0), \"XYZ\")
            buckets[bi].append(o)"""
new2 = """            o = sph(f\"tb{row}_{col}\", (x, y, z), 0.10, mats_r[bi], (1.3, 1.05, 0.36))
            o.rotation_euler = Euler((math.radians(33), 0, 0), \"XYZ\")
            bpy.context.view_layer.objects.active = o
            o.select_set(True)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
            o.select_set(False)
            buckets[bi].append(o)"""
if old2 not in text:
    raise SystemExit("back tile block missing")
text = text.replace(old2, new2)

# Fill door cavity with wall panel before door parts
needle = "    # --- DOOR ---"
fill = """    # --- DOOR ---
    cube(\"door_fill\", (0, 0.50, 0.50), (0.40, 0.10, 0.76), M[\"wall\"], 0.04)
"""
if needle not in text:
    raise SystemExit("door marker missing")
text = text.replace(needle, fill, 1)

# Don't parent with identity inverse incorrectly — keep simple parent at origin
# Reduce smoke float: lower smoke start
text = text.replace(
    "smoke_parts.append(sph(f\"sm{i}\", (0.38 + dx, -0.12 + dy, 2.28 + dz), s, M[\"smoke\"]))",
    "smoke_parts.append(sph(f\"sm{i}\", (0.38 + dx, -0.12 + dy, 2.22 + dz), s, M[\"smoke\"]))",
)

out = src / "author_cozy_house_mockup_v5.py"
out.write_text(text, encoding="utf-8")
print("wrote", out)
