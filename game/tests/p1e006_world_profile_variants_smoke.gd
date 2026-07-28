## WO-P1E-006 — world-profile visual variants (STATE_VARIANTS selector).
## Run:
##   tools/Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://tests/p1e006_world_profile_variants_smoke.gd
extends SceneTree

const PKG := "E:/AIdle_Blender_Bridge_P0/storage/generated_quarantine/BLD-03CB1AADD475"
const BUILDER := "res://scripts/modules/asset/glb_intake_runtime_builder.gd"
const SELECTOR := "res://scripts/modules/asset/world_profile_variant_selector.gd"

var _failed := 0
var _passed := 0
var _evidence: Dictionary = {}


func _initialize() -> void:
	print("[P1E-006 variants smoke] start")
	_test_catalog_and_map()
	_test_cozy_identity_and_surrealism_switch()
	_finish()


func _ok(n: String) -> void:
	_passed += 1
	print("  OK  %s" % n)


func _fail(n: String, d: String = "") -> void:
	_failed += 1
	print("  FAIL %s | %s" % [n, d] if not d.is_empty() else "  FAIL %s" % n)


func _test_catalog_and_map() -> void:
	var sel = load(SELECTOR).new()
	if not bool(sel.call("load_catalog")):
		_fail("catalog", str(sel.get("last_error")))
		return
	if str(sel.call("art_style_to_world_profile", "cozy_cyber_pixel")) != "cozy_cyber_pixel":
		_fail("map_cozy")
		return
	if str(sel.call("art_style_to_world_profile", "surrealism_canvas")) != "surrealism_canvas":
		_fail("map_surreal")
		return
	if str(sel.call("art_style_to_world_profile", "pastoral_fantasy")) != "cozy_cyber_pixel":
		_fail("map_pastoral_nearest")
		return
	if str(sel.call("art_style_to_world_profile", "cyberpunk_dense")) != "cozy_cyber_pixel":
		_fail("map_cyber_nearest")
		return
	_ok("catalog_and_art_style_map")


func _test_cozy_identity_and_surrealism_switch() -> void:
	var builder = load(BUILDER).new()
	# bake_navigation false: variants smoke does not need nav; avoids NavSourcePlane
	# residual under headless (still disposed via _dispose_tree_root).
	var res: Dictionary = builder.call(
		"build_realm",
		PKG,
		{"enable_collision": true, "bake_navigation": false}
	) as Dictionary
	if not bool(res.get("ok", false)):
		_fail("build_realm", str(res.get("reason", res)))
		return
	var root: Node3D = res.get("root") as Node3D
	if root == null:
		_fail("root_null")
		return
	root_node_add(root)

	var mats_before := _sample_water_albedo(root)
	_evidence["cozy_water_albedo_before"] = mats_before

	var sel = load(SELECTOR).new()
	sel.call("load_catalog")
	var r_cozy: Dictionary = sel.call("apply_to_node", root, "cozy_cyber_pixel") as Dictionary
	if not bool(r_cozy.get("ok", false)):
		_fail("apply_cozy", str(r_cozy))
		return
	if str(r_cozy.get("mode", "")) != "identity_register":
		_fail("cozy_mode", str(r_cozy.get("mode", "")))
		return
	var mats_cozy := _sample_water_albedo(root)
	_evidence["cozy_water_albedo_after_identity"] = mats_cozy
	# Cozy identity should not invent white wash
	if mats_cozy.size() > 0:
		var c: Color = mats_cozy[0]
		if c.r > 0.95 and c.g > 0.95 and c.b > 0.95:
			_fail("cozy_water_white", str(c))
			return
	_ok("cozy_identity_no_white")

	var r_sur: Dictionary = sel.call("apply_to_node", root, "surrealism_canvas") as Dictionary
	if not bool(r_sur.get("ok", false)):
		_fail("apply_surreal", str(r_sur))
		return
	if int(r_sur.get("materials_rewritten", 0)) <= 0:
		# May fail if MAT names empty — record and fail clearly
		_fail("surreal_zero_rewrite", "names may be empty on GLTF mats: %s" % str(_list_mat_names(root)))
		return
	var mats_sur := _sample_water_albedo(root)
	_evidence["surreal_water_albedo"] = mats_sur
	_evidence["surreal_rewritten"] = r_sur.get("materials_rewritten")
	if mats_sur.is_empty():
		_fail("no_water_after_surreal")
		return
	var cs: Color = mats_sur[0]
	# Must not be achromatic white/grey
	var mx := maxf(cs.r, maxf(cs.g, cs.b))
	var mn := minf(cs.r, minf(cs.g, cs.b))
	var sat := 0.0 if mx < 0.001 else (mx - mn) / mx
	if sat < 0.12:
		_fail("surreal_water_achromatic", "sat=%s color=%s" % [sat, cs])
		return
	# Prefer blue/purple channel not all equal white
	if cs.r > 0.92 and cs.g > 0.92 and cs.b > 0.92:
		_fail("surreal_water_white", str(cs))
		return
	_ok("surrealism_recolor_chromatic")

	# Switch back to cozy without rebuild
	var r_back: Dictionary = sel.call("apply_to_node", root, "cozy_cyber_pixel") as Dictionary
	var mats_back := _sample_water_albedo(root)
	_evidence["cozy_water_after_switch_back"] = mats_back
	if mats_before.size() > 0 and mats_back.size() > 0:
		var a: Color = mats_before[0]
		var b: Color = mats_back[0]
		if absf(a.r - b.r) > 0.08 or absf(a.g - b.g) > 0.08 or absf(a.b - b.b) > 0.08:
			_fail("switch_back_regression", "before=%s after=%s" % [a, b])
			return
	_ok("switch_back_to_cozy_no_reload")

	# Package modules still present after variant apply (fence rails added by full starter builder)
	var pond := root.get_node_or_null("Pond")
	var house := root.get_node_or_null("House")
	if pond == null or house == null:
		_fail("landmarks_missing", "pond=%s house=%s" % [pond, house])
	else:
		_ok("landmarks_present_after_variant")

	_dispose_tree_root(root)


func root_node_add(n: Node) -> void:
	root.add_child(n)


## Headless dummy: free MeshInstance3D only after mesh=null (see glb_intake release).
func _clear_presentation_meshes(n: Node) -> void:
	if n == null or not is_instance_valid(n):
		return
	if n is MeshInstance3D:
		(n as MeshInstance3D).mesh = null
	for c in n.get_children():
		_clear_presentation_meshes(c)


func _dispose_tree_root(n: Node) -> void:
	if n == null or not is_instance_valid(n):
		return
	_clear_presentation_meshes(n)
	var p: Node = n.get_parent()
	if p:
		p.remove_child(n)
	n.free()


func _sample_water_albedo(root: Node) -> Array:
	var out: Array = []
	_walk_water(root, out)
	return out


func _walk_water(n: Node, out: Array) -> void:
	if n is MeshInstance3D:
		var mi := n as MeshInstance3D
		var mats: Array = []
		if mi.material_override != null:
			mats.append(mi.material_override)
		for s in range(_mesh_surface_count(mi)):
			var surf: Material = _surface_material_at(mi, s)
			if surf != null:
				mats.append(surf)
		for mat in mats:
			var nm := str(mat.resource_name)
			if nm.findn("Water") >= 0 or nm.findn("water") >= 0:
				if mat is BaseMaterial3D:
					out.append((mat as BaseMaterial3D).albedo_color)
			elif mat is BaseMaterial3D:
				# Fallback: pond holder named Pond
				var p := mi.get_parent()
				while p != null:
					if str(p.name).findn("Pond") >= 0 or str(p.name).findn("pond") >= 0:
						out.append((mat as BaseMaterial3D).albedo_color)
						break
					p = p.get_parent()
	for c in n.get_children():
		_walk_water(c, out)


func _list_mat_names(n: Node) -> Array:
	var names: Array = []
	_walk_names(n, names)
	return names


func _walk_names(n: Node, names: Array) -> void:
	if n is MeshInstance3D:
		var mi := n as MeshInstance3D
		for s in range(_mesh_surface_count(mi)):
			var surf: Material = _surface_material_at(mi, s)
			if surf != null:
				names.append(str(surf.resource_name))
	for c in n.get_children():
		_walk_names(c, names)


## Prefer intake/surface-override caches. Do not call Mesh.get_surface_count() when
## headless intake released the GLTF mesh (dummy RS handle would be null).
func _mesh_surface_count(mi: MeshInstance3D) -> int:
	if mi == null:
		return 0
	if mi.has_meta("intake_surface_count"):
		return int(mi.get_meta("intake_surface_count"))
	if mi.has_meta("intake_surface_materials"):
		return (mi.get_meta("intake_surface_materials") as Array).size()
	if mi.has_meta("sv_orig_surfaces"):
		return (mi.get_meta("sv_orig_surfaces") as Array).size()
	var soc: int = mi.get_surface_override_material_count()
	if soc > 0:
		return soc
	if mi.mesh == null:
		return 0
	if mi.mesh is ArrayMesh:
		return (mi.mesh as ArrayMesh).get_surface_count()
	if mi.mesh is PrimitiveMesh:
		return 1
	return 0


func _surface_material_at(mi: MeshInstance3D, s: int) -> Material:
	if mi == null or s < 0:
		return null
	if mi.has_meta("intake_surface_materials"):
		var arr: Array = mi.get_meta("intake_surface_materials") as Array
		if s < arr.size() and arr[s] != null:
			return arr[s] as Material
	if mi.mesh != null and s < mi.get_surface_override_material_count():
		var ov: Material = mi.get_surface_override_material(s)
		if ov != null:
			return ov
	if mi.material_override != null:
		return mi.material_override
	if mi.mesh != null and mi.mesh is ArrayMesh:
		return (mi.mesh as ArrayMesh).surface_get_material(s)
	return null


func _finish() -> void:
	print("[P1E-006 variants smoke] evidence=%s" % JSON.stringify(_evidence))
	if _failed == 0:
		print("AIDLE_P1E006_VARIANTS_SMOKE=PASS checks=%d" % _passed)
		quit(0)
	else:
		print("AIDLE_P1E006_VARIANTS_SMOKE=FAIL failed=%d passed=%d" % [_failed, _passed])
		quit(1)
