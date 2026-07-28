## WO-P1E-006 — STATE_VARIANTS-style selector for world-profile visual variants.
## Extends the DNA pattern: Godot selects a visual variant deterministically from
## a selector key. Here the key is world_profile (mapped from active art style).
## Does NOT invent a parallel STYLE_VARIANTS system — same apply path as state.
## Cozy variant mode=identity_register → no material rewrite (no regression).
extends RefCounted

const CATALOG_PATH := "res://resources/world_profiles/state_visual_variants.json"

var last_error: String = ""
var last_applied_profile: String = ""
var last_applied_mode: String = ""
var _catalog: Dictionary = {}


func load_catalog() -> bool:
	last_error = ""
	if not FileAccess.file_exists(CATALOG_PATH):
		last_error = "catalog_missing"
		return false
	var f := FileAccess.open(CATALOG_PATH, FileAccess.READ)
	if f == null:
		last_error = "catalog_open_failed"
		return false
	var parsed = JSON.parse_string(f.get_as_text())
	f.close()
	if typeof(parsed) != TYPE_DICTIONARY:
		last_error = "catalog_parse"
		return false
	_catalog = parsed
	return true


func art_style_to_world_profile(art_style_id: String) -> String:
	if _catalog.is_empty() and not load_catalog():
		return "cozy_cyber_pixel"
	var map: Dictionary = _catalog.get("art_style_to_world_profile", {}) as Dictionary
	if map.has(art_style_id):
		return str(map[art_style_id])
	return "cozy_cyber_pixel"


func resolve_active_world_profile() -> String:
	var style_id := "cozy_cyber_pixel"
	if ArtStyleManager != null and ArtStyleManager.has_method("get_active_style_id"):
		style_id = str(ArtStyleManager.get_active_style_id())
	return art_style_to_world_profile(style_id)


## Apply visual variant under root for the given world_profile (or active).
## Returns report dict with counts and profile used.
func apply_to_node(root: Node, world_profile: String = "") -> Dictionary:
	if _catalog.is_empty() and not load_catalog():
		return {"ok": false, "error": last_error}
	var profile := world_profile
	if profile.is_empty():
		profile = resolve_active_world_profile()
	var variants: Dictionary = _catalog.get("variants", {}) as Dictionary
	if not variants.has(profile):
		# No content kit for this profile — fall back to cozy identity
		profile = "cozy_cyber_pixel"
	var variant: Dictionary = variants[profile] as Dictionary
	var mode := str(variant.get("mode", "identity_register"))
	last_applied_profile = profile
	last_applied_mode = mode
	root.set_meta("world_profile_visual_variant", profile)
	root.set_meta("state_visual_variant_mode", mode)

	# Snapshot originals once so cozy identity can restore after surrealism recolor.
	_ensure_original_cache(root)

	if mode == "identity_register":
		var restored := _restore_originals(root)
		return {
			"ok": true,
			"world_profile": profile,
			"mode": mode,
			"materials_rewritten": restored,
			"note": "cozy identity — restore cached intake materials, no re-author",
		}

	var table: Dictionary = variant.get("materials", {}) as Dictionary
	var rewritten := _walk_apply(root, table)
	return {
		"ok": true,
		"world_profile": profile,
		"mode": mode,
		"materials_rewritten": rewritten,
	}


func _ensure_original_cache(root: Node) -> void:
	if bool(root.get_meta("state_variant_originals_cached", false)):
		return
	_walk_cache(root)
	root.set_meta("state_variant_originals_cached", true)


func _walk_cache(n: Node) -> void:
	if n is MeshInstance3D:
		var mi := n as MeshInstance3D
		if mi.material_override != null:
			mi.set_meta("sv_orig_override", mi.material_override.duplicate(true))
		elif mi.has_meta("intake_has_material_override") == false and bool(mi.get_meta("intake_headless_mesh_cleared", false)):
			# Headless may have promoted a surface mat to material_override; still cache it.
			pass
		var arr: Array = []
		var sc := _mesh_surface_count(mi)
		for s in range(sc):
			var surf: Material = _surface_material_at(mi, s)
			arr.append(surf.duplicate(true) if surf != null else null)
		if sc > 0 or mi.has_meta("intake_surface_materials"):
			mi.set_meta("sv_orig_surfaces", arr)
	for c in n.get_children():
		_walk_cache(c)


func _restore_originals(n: Node) -> int:
	var count := 0
	if n is MeshInstance3D:
		var mi := n as MeshInstance3D
		if mi.has_meta("sv_orig_override"):
			mi.material_override = mi.get_meta("sv_orig_override")
			count += 1
		elif bool(mi.get_meta("intake_headless_mesh_cleared", false)):
			# Clear surrealism material_override when originals had none.
			mi.material_override = null
		if mi.has_meta("sv_orig_surfaces"):
			var arr: Array = mi.get_meta("sv_orig_surfaces") as Array
			# Always keep meta in sync for headless mesh-cleared instances.
			mi.set_meta("intake_surface_materials", arr.duplicate())
			mi.set_meta("intake_surface_count", arr.size())
			if mi.mesh != null:
				for s in range(arr.size()):
					mi.set_surface_override_material(s, arr[s])
					count += 1
			else:
				# mesh=null: surface_override slots are gone; promote single-surface.
				if arr.size() == 1 and arr[0] != null and mi.material_override == null:
					mi.material_override = arr[0] as Material
				count += arr.size()
	for c in n.get_children():
		count += _restore_originals(c)
	return count


func _walk_apply(n: Node, table: Dictionary) -> int:
	var count := 0
	if n is MeshInstance3D:
		count += _apply_mesh_instance(n as MeshInstance3D, table)
	for c in n.get_children():
		count += _walk_apply(c, table)
	return count


## Safe surface count: prefer intake/sv caches. Never call Mesh.get_surface_count()
## when mesh is null (headless clear) or only a dummy RS handle remains.
func _mesh_surface_count(mi: MeshInstance3D) -> int:
	if mi == null:
		return 0
	if mi.has_meta("sv_orig_surfaces"):
		return (mi.get_meta("sv_orig_surfaces") as Array).size()
	if mi.has_meta("intake_surface_count"):
		return int(mi.get_meta("intake_surface_count"))
	if mi.has_meta("intake_surface_materials"):
		return (mi.get_meta("intake_surface_materials") as Array).size()
	if mi.mesh != null:
		var soc: int = mi.get_surface_override_material_count()
		if soc > 0:
			return soc
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


func _apply_mesh_instance(mi: MeshInstance3D, table: Dictionary) -> int:
	var n := 0
	# Prefer cached original for name resolution so we always map from Cozy MAT_* names.
	var name_src: Material = null
	if mi.has_meta("sv_orig_override"):
		name_src = mi.get_meta("sv_orig_override") as Material
	elif mi.material_override != null:
		name_src = mi.material_override
	if name_src != null:
		var mname := _mat_name(name_src)
		if table.has(mname):
			var built0 := _build_mat(table[mname], name_src)
			built0.resource_name = mname
			mi.material_override = built0
			n += 1
	var orig_surfs: Array = []
	if mi.has_meta("sv_orig_surfaces"):
		orig_surfs = mi.get_meta("sv_orig_surfaces") as Array
	var sc := _mesh_surface_count(mi)
	if sc <= 0 and orig_surfs.is_empty():
		return n
	if sc <= 0:
		sc = orig_surfs.size()
	var live_mats: Array = []
	if mi.has_meta("intake_surface_materials"):
		live_mats = (mi.get_meta("intake_surface_materials") as Array).duplicate()
	while live_mats.size() < sc:
		live_mats.append(null)
	for s in range(sc):
		var surf: Material = null
		if s < orig_surfs.size() and orig_surfs[s] != null:
			surf = orig_surfs[s] as Material
		else:
			surf = _surface_material_at(mi, s)
		if surf == null:
			continue
		var mname2 := _mat_name(surf)
		if not table.has(mname2):
			continue
		var built := _build_mat(table[mname2], surf)
		built.resource_name = mname2
		live_mats[s] = built
		if mi.mesh != null:
			mi.set_surface_override_material(s, built)
		n += 1
	if n > 0:
		mi.set_meta("intake_surface_materials", live_mats)
		mi.set_meta("intake_surface_count", live_mats.size())
		# Headless mesh-cleared: surface_override unavailable — use material_override
		# when a single surface was rewritten, or keep override from name_src path.
		if mi.mesh == null:
			if live_mats.size() == 1 and live_mats[0] != null:
				mi.material_override = live_mats[0] as Material
	return n


func _mat_name(mat: Material) -> String:
	if mat == null:
		return ""
	var nm := str(mat.resource_name)
	if nm.is_empty() and mat is Resource:
		nm = str((mat as Resource).resource_path.get_file())
	if nm.is_empty():
		# Godot GLTF often leaves name empty; try meta from importer
		if mat.has_meta("name"):
			nm = str(mat.get_meta("name"))
	return nm


func _build_mat(spec: Dictionary, _src: Material) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	var alb: Array = spec.get("albedo", [1, 1, 1, 1]) as Array
	m.albedo_color = Color(
		float(alb[0]) if alb.size() > 0 else 1.0,
		float(alb[1]) if alb.size() > 1 else 1.0,
		float(alb[2]) if alb.size() > 2 else 1.0,
		float(alb[3]) if alb.size() > 3 else 1.0
	)
	if spec.has("roughness"):
		m.roughness = float(spec["roughness"])
	if spec.has("metallic"):
		m.metallic = float(spec["metallic"])
	if spec.has("emission"):
		var em: Array = spec["emission"] as Array
		m.emission_enabled = true
		m.emission = Color(float(em[0]), float(em[1]), float(em[2]))
		m.emission_energy_multiplier = float(spec.get("emission_strength", 1.0))
	if m.albedo_color.a < 0.99:
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	return m


func get_hsl_targets(world_profile: String) -> Dictionary:
	if _catalog.is_empty() and not load_catalog():
		return {}
	var variants: Dictionary = _catalog.get("variants", {}) as Dictionary
	if not variants.has(world_profile):
		return {}
	return (variants[world_profile] as Dictionary).get("hsl_targets", {}) as Dictionary
