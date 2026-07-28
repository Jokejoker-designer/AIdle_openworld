## ART-G01 outline foundation load smoke (commercial gate 12 partial).
extends SceneTree

func _initialize() -> void:
	print("[COMMERCIAL_OUTLINE_FOUNDATION_001] starting…")
	var fails: PackedStringArray = []
	var okn := 0
	var sp := "res://shaders/cozy_silhouette_outline.gdshader"
	var mp := "res://shaders/cozy_silhouette_outline_mat.tres"
	var jp := "res://resources/art_styles/cozy_cyber_pixel_2_5d.json"
	if not ResourceLoader.exists(sp):
		fails.append("shader_missing")
	else:
		var sh = load(sp)
		if sh == null:
			fails.append("shader_load_null")
		else:
			okn += 1
			print("  OK  shader_load")
	if not ResourceLoader.exists(mp):
		fails.append("mat_missing")
	else:
		var mat = load(mp)
		if mat == null:
			fails.append("mat_load_null")
		else:
			okn += 1
			print("  OK  material_load")
	if not FileAccess.file_exists(jp):
		fails.append("style_json_missing")
	else:
		var f := FileAccess.open(jp, FileAccess.READ)
		var txt := f.get_as_text()
		f.close()
		var data = JSON.parse_string(txt)
		if data == null or not (data is Dictionary):
			fails.append("style_json_parse")
		else:
			var o: Dictionary = data.get("silhouette_outline", {}) as Dictionary
			if str(o.get("cream_body_ssot", "")) != "#fdf3e2":
				fails.append("cream_ssot")
			else:
				okn += 1
				print("  OK  style_outline_block_cream_ssot")
	if fails.is_empty():
		print("AIDLE_COMMERCIAL_OUTLINE_FOUNDATION_001=PASS checks=%d" % okn)
		quit(0)
		return
	for x in fails:
		printerr("[FAIL] %s" % x)
	print("AIDLE_COMMERCIAL_OUTLINE_FOUNDATION_001=FAIL failed=%d passed=%d" % [fails.size(), okn])
	quit(1)
