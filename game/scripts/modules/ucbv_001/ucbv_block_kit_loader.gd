## UCBV-001 block family loader — mesh descriptors + full 28-module runtime catalog.
## Offline procedural MeshInstance3D trees from meshdesc JSON when present.
## Modules without meshdesc get categorized synthetic mass previews (not world truth).
## Note: no class_name for headless -s reliability.
extends RefCounted

const _Paths = preload("res://scripts/modules/ucbv_001/ucbv_paths.gd")
const _Mat = preload("res://scripts/modules/ucbv_001/ucbv_mat_palette.gd")

## Category taxonomy for the accepted 28-module Manual Build catalog.
const CATEGORY_ORDER: PackedStringArray = [
	"Primitive",
	"Architecture",
	"Terrain",
	"Cluster",
	"Prop",
	"Character",
]

const MODULE_CATEGORY := {
	"block_cube_round": "Primitive",
	"block_cylinder_round": "Primitive",
	"block_sphere_segment": "Primitive",
	"block_wedge": "Primitive",
	"block_arch": "Primitive",
	"block_dome": "Primitive",
	"block_ring": "Primitive",
	"block_beam": "Primitive",
	"block_panel": "Primitive",
	"block_pipe_straight": "Primitive",
	"block_platform": "Primitive",
	"block_ramp": "Primitive",
	"terrain_flat_8m": "Terrain",
	"terrain_flat_16m": "Terrain",
	"terrain_slope_8m": "Terrain",
	"arch_floor_round_4m": "Architecture",
	"arch_wall_door_4m": "Architecture",
	"arch_wall_window_4m": "Architecture",
	"arch_roof_dome_4m": "Architecture",
	"arch_door_round": "Architecture",
	"arch_window_frame_simple": "Architecture",
	"cluster_cozy_house_small_A": "Cluster",
	"cluster_cozy_greenhouse_droplet_A": "Cluster",
	"cluster_cozy_farm_A": "Cluster",
	"prop_bench_simple": "Prop",
	"prop_lamp_post": "Prop",
	"prop_crate_small": "Prop",
	"char_nori7_base": "Character",
}

const MODULE_DISPLAY_NAME := {
	"block_cube_round": "Cube Round",
	"block_cylinder_round": "Cylinder Round",
	"block_sphere_segment": "Sphere Segment",
	"block_wedge": "Wedge",
	"block_arch": "Arch Primitive",
	"block_dome": "Dome Primitive",
	"block_ring": "Ring",
	"block_beam": "Beam",
	"block_panel": "Panel",
	"block_pipe_straight": "Pipe Straight",
	"block_platform": "Platform",
	"block_ramp": "Ramp",
	"terrain_flat_8m": "Terrain Flat 8m",
	"terrain_flat_16m": "Terrain Flat 16m",
	"terrain_slope_8m": "Terrain Slope 8m",
	"arch_floor_round_4m": "Floor Round 4m",
	"arch_wall_door_4m": "Wall Door 4m",
	"arch_wall_window_4m": "Wall Window 4m",
	"arch_roof_dome_4m": "Roof Dome 4m",
	"arch_door_round": "Door Round",
	"arch_window_frame_simple": "Window Frame",
	"cluster_cozy_house_small_A": "Cozy House Small",
	"cluster_cozy_greenhouse_droplet_A": "Cozy Greenhouse",
	"cluster_cozy_farm_A": "Cozy Farm",
	"prop_bench_simple": "Bench",
	"prop_lamp_post": "Lamp Post",
	"prop_crate_small": "Crate Small",
	"char_nori7_base": "Nori-7 Base",
}

## Default overall sizes for catalog modules without meshdesc (presentation only).
const MODULE_DEFAULT_SIZE := {
	"block_cube_round": Vector3(1.0, 1.0, 1.0),
	"block_cylinder_round": Vector3(1.0, 1.2, 1.0),
	"block_sphere_segment": Vector3(1.2, 0.8, 1.2),
	"block_wedge": Vector3(1.0, 1.0, 1.0),
	"block_arch": Vector3(2.0, 2.0, 0.6),
	"block_dome": Vector3(2.0, 1.2, 2.0),
	"block_ring": Vector3(1.6, 0.3, 1.6),
	"block_beam": Vector3(2.0, 0.25, 0.25),
	"block_panel": Vector3(1.5, 1.5, 0.12),
	"block_pipe_straight": Vector3(1.5, 0.3, 0.3),
	"block_platform": Vector3(2.0, 0.2, 2.0),
	"block_ramp": Vector3(2.0, 1.0, 1.0),
	"terrain_flat_8m": Vector3(8.0, 0.15, 8.0),
	"terrain_flat_16m": Vector3(16.0, 0.15, 16.0),
	"terrain_slope_8m": Vector3(8.0, 2.0, 8.0),
	"arch_floor_round_4m": Vector3(4.0, 0.2, 4.0),
	"arch_wall_door_4m": Vector3(4.0, 3.0, 0.3),
	"arch_wall_window_4m": Vector3(4.0, 3.0, 0.3),
	"arch_roof_dome_4m": Vector3(4.0, 2.0, 4.0),
	"arch_door_round": Vector3(1.2, 2.2, 0.2),
	"arch_window_frame_simple": Vector3(1.2, 1.2, 0.15),
	"cluster_cozy_house_small_A": Vector3(4.0, 3.5, 4.0),
	"cluster_cozy_greenhouse_droplet_A": Vector3(3.0, 3.0, 3.0),
	"cluster_cozy_farm_A": Vector3(6.0, 2.0, 6.0),
	"prop_bench_simple": Vector3(1.2, 0.5, 0.45),
	"prop_lamp_post": Vector3(0.3, 2.2, 0.3),
	"prop_crate_small": Vector3(0.6, 0.6, 0.6),
	"char_nori7_base": Vector3(0.8, 1.4, 0.6),
}

var _loaded: bool = false
var _load_error: String = ""
var _family: Dictionary = {}
var _module_ids: PackedStringArray = PackedStringArray()
var _descriptors: Dictionary = {}  # module_id -> meshdesc dict
var _roles: Dictionary = {}  # module_id -> role
var _definitions: Dictionary = {}  # module_id -> module def
var _categories: Dictionary = {}  # module_id -> category
var _display_names: Dictionary = {}  # module_id -> display


func ensure_loaded() -> bool:
	if _loaded:
		return _load_error.is_empty()
	_loaded = true
	_load_error = ""
	# Prefer accepted runtime catalog (28 modules) as the player-facing source of truth.
	var cat: Variant = _Paths.load_json(_Paths.RUNTIME_CATALOG)
	if cat is Dictionary and (cat as Dictionary).has("module_ids"):
		for m in (cat as Dictionary).get("module_ids", []):
			var mid := str(m)
			if mid.is_empty():
				continue
			_module_ids.append(mid)
			_categories[mid] = str(MODULE_CATEGORY.get(mid, _infer_category(mid)))
			_display_names[mid] = str(MODULE_DISPLAY_NAME.get(mid, _pretty_name(mid)))
	var idx: Variant = _Paths.load_json(_Paths.KIT_RUNTIME_INDEX)
	var fam: Variant = _Paths.load_json(_Paths.FAMILY_MANIFEST)
	if fam is Dictionary:
		_family = fam as Dictionary
		for mod in _family.get("modules", []):
			if not (mod is Dictionary):
				continue
			var md: Dictionary = mod
			var mid2 := str(md.get("module_id", ""))
			if mid2.is_empty():
				continue
			if not _module_ids.has(mid2):
				_module_ids.append(mid2)
			_roles[mid2] = str(md.get("role", ""))
			if md.has("category"):
				_categories[mid2] = str(md.get("category"))
			if md.has("display_name"):
				_display_names[mid2] = str(md.get("display_name"))
			var rel_desc := str(md.get("mesh_descriptor_path", "mesh_descriptors/%s.meshdesc.json" % mid2))
			var desc_path := "%s/%s" % [_Paths.BLOCKS_ROOT, rel_desc]
			var desc: Variant = _Paths.load_json(desc_path)
			if desc is Dictionary:
				_descriptors[mid2] = desc
			var rel_def := str(md.get("definition_path", "modules/%s.json" % mid2))
			var def_path := "%s/%s" % [_Paths.BLOCKS_ROOT, rel_def]
			var defn: Variant = _Paths.load_json(def_path)
			if defn is Dictionary:
				_definitions[mid2] = defn
	# Also load any standalone meshdesc files for catalog modules not in family.
	for mid3 in _module_ids:
		if _descriptors.has(mid3):
			continue
		var solo := "%s/mesh_descriptors/%s.meshdesc.json" % [_Paths.BLOCKS_ROOT, mid3]
		var d2: Variant = _Paths.load_json(solo)
		if d2 is Dictionary:
			_descriptors[mid3] = d2
		if not _categories.has(mid3):
			_categories[mid3] = str(MODULE_CATEGORY.get(mid3, _infer_category(mid3)))
		if not _display_names.has(mid3):
			_display_names[mid3] = str(MODULE_DISPLAY_NAME.get(mid3, _pretty_name(mid3)))
		if not _roles.has(mid3):
			_roles[mid3] = _category_to_role(str(_categories[mid3]))
	# If runtime catalog missing, fall back to kit index only.
	if _module_ids.is_empty() and idx is Dictionary:
		for m in (idx as Dictionary).get("module_ids", []):
			_module_ids.append(str(m))
	if _module_ids.is_empty():
		_load_error = "no_modules"
		return false
	# Ensure category/display for every id.
	for mid4 in _module_ids:
		if not _categories.has(mid4):
			_categories[mid4] = str(MODULE_CATEGORY.get(mid4, _infer_category(mid4)))
		if not _display_names.has(mid4):
			_display_names[mid4] = str(MODULE_DISPLAY_NAME.get(mid4, _pretty_name(mid4)))
	return true


func get_load_error() -> String:
	ensure_loaded()
	return _load_error


func get_family_id() -> String:
	ensure_loaded()
	return str(_family.get("family_id", _Paths.FAMILY_ID))


func get_module_ids() -> PackedStringArray:
	ensure_loaded()
	return _module_ids.duplicate()


func module_count() -> int:
	ensure_loaded()
	return _module_ids.size()


func has_module(module_id: String) -> bool:
	ensure_loaded()
	return module_id in _module_ids or _descriptors.has(module_id)


func get_descriptor(module_id: String) -> Dictionary:
	ensure_loaded()
	if not _descriptors.has(module_id):
		return {}
	return (_descriptors[module_id] as Dictionary).duplicate(true)


func get_role(module_id: String) -> String:
	ensure_loaded()
	return str(_roles.get(module_id, _category_to_role(get_category(module_id))))


func get_category(module_id: String) -> String:
	ensure_loaded()
	return str(_categories.get(module_id, _infer_category(module_id)))


func get_display_name(module_id: String) -> String:
	ensure_loaded()
	return str(_display_names.get(module_id, _pretty_name(module_id)))


func get_categories() -> PackedStringArray:
	ensure_loaded()
	var present := {}
	for mid in _module_ids:
		present[get_category(mid)] = true
	var out := PackedStringArray()
	for c in CATEGORY_ORDER:
		if present.has(c):
			out.append(c)
	for c2 in present.keys():
		if not out.has(str(c2)):
			out.append(str(c2))
	return out


func get_modules_in_category(category: String) -> PackedStringArray:
	ensure_loaded()
	var out := PackedStringArray()
	for mid in _module_ids:
		if get_category(mid) == category:
			out.append(mid)
	return out


func get_catalog_entries() -> Array:
	## Full categorized catalog for Manual Build selector UI.
	ensure_loaded()
	var items: Array = []
	for mid in _module_ids:
		items.append({
			"module_id": mid,
			"display_name": get_display_name(mid),
			"category": get_category(mid),
			"role": get_role(mid),
			"has_descriptor": _descriptors.has(mid),
			"has_definition": _definitions.has(mid),
			"preview_size": {
				"x": get_overall_size(mid).x,
				"y": get_overall_size(mid).y,
				"z": get_overall_size(mid).z,
			},
		})
	return items


func get_catalog_summary() -> Dictionary:
	ensure_loaded()
	var items: Array = get_catalog_entries()
	var by_cat := {}
	for c in get_categories():
		by_cat[c] = get_modules_in_category(c)
	return {
		"ok": _load_error.is_empty(),
		"family_id": get_family_id(),
		"style_lock_id": str(_family.get("style_lock_id", _Paths.STYLE_LOCK_ID)),
		"module_count": _module_ids.size(),
		"descriptor_count": _descriptors.size(),
		"categories": get_categories(),
		"by_category": by_cat,
		"modules": items,
		"load_error": _load_error,
		"runtime_catalog_full": _module_ids.size() >= 28,
	}


## Build a presentation Node3D for module (multi MeshInstance3D parts). Collision separate.
## stage: wireframe|hologram|materializing|complete. presentation=false → empty root (headless).
func build_module_visual(
	module_id: String,
	stage: String = "complete",
	placement_valid: bool = true,
	presentation: bool = true
) -> Node3D:
	ensure_loaded()
	var root := Node3D.new()
	root.name = "UcbvModule_%s" % module_id
	root.set_meta("ucbv_module_id", module_id)
	root.set_meta("ucbv_family_id", get_family_id())
	root.set_meta("ucbv_kit", true)
	root.set_meta("ucbv_category", get_category(module_id))
	root.set_meta("ucbv_display_name", get_display_name(module_id))
	root.set_meta("world_truth", false)
	root.set_meta("client_world_commit", false)
	if not has_module(module_id):
		root.set_meta("ucbv_build_ok", false)
		root.set_meta("ucbv_error", "unknown_module")
		return root
	var size := get_overall_size(module_id)
	root.set_meta("overall_size", {"x": size.x, "y": size.y, "z": size.z})
	root.set_meta("ucbv_role", get_role(module_id))
	if not presentation:
		root.set_meta("ucbv_build_ok", true)
		return root
	if _descriptors.has(module_id):
		var desc: Dictionary = _descriptors[module_id]
		root.set_meta("ucbv_asset_id", str(desc.get("asset_id", "")))
		var slot_to_mat := _slot_map_from_desc(desc)
		var parts: Array = desc.get("parts", []) as Array
		if parts.is_empty():
			parts = [{
				"part_id": "primary",
				"primitive": str(desc.get("primary_primitive", "BoxMesh")),
				"size": [size.x, size.y, size.z],
				"offset": [0.0, size.y * 0.5, 0.0],
				"material_slot": "body",
			}]
		for p in parts:
			if not (p is Dictionary):
				continue
			var mi := _build_part_mesh(p as Dictionary, slot_to_mat, stage, placement_valid)
			if mi != null:
				root.add_child(mi)
	else:
		# Synthetic categorized mass for catalog modules without meshdesc.
		var part := {
			"part_id": "primary",
			"primitive": _default_primitive(module_id),
			"size": [size.x, size.y, size.z],
			"offset": [0.0, size.y * 0.5, 0.0],
			"material_slot": "structure",
		}
		var mi2 := _build_part_mesh(part, {}, stage, placement_valid)
		if mi2 != null:
			root.add_child(mi2)
		root.set_meta("ucbv_synthetic_preview", true)
	root.set_meta("ucbv_build_ok", true)
	root.set_meta("ucbv_part_count", root.get_child_count())
	return root


func get_overall_size(module_id: String) -> Vector3:
	ensure_loaded()
	if _descriptors.has(module_id):
		var desc: Dictionary = _descriptors[module_id]
		var osz: Dictionary = desc.get("overall_size_m", {}) as Dictionary
		return Vector3(
			float(osz.get("x", 1.0)),
			float(osz.get("y", 1.0)),
			float(osz.get("z", 1.0))
		)
	if MODULE_DEFAULT_SIZE.has(module_id):
		return MODULE_DEFAULT_SIZE[module_id] as Vector3
	return Vector3.ONE


func apply_stage_to_visual(root: Node3D, stage: String, placement_valid: bool = true) -> void:
	if root == null or not is_instance_valid(root):
		return
	var mid := str(root.get_meta("ucbv_module_id", ""))
	if mid.is_empty() or not has_module(mid):
		return
	var slot_to_mat := {}
	if _descriptors.has(mid):
		slot_to_mat = _slot_map_from_desc(_descriptors[mid] as Dictionary)
	for child in root.get_children():
		if not (child is MeshInstance3D):
			continue
		var mi := child as MeshInstance3D
		var slot := str(mi.get_meta("material_slot", "body"))
		var mat_id := str(slot_to_mat.get(slot, _Mat.mat_for_slot(slot)))
		if mi.has_meta("mat_id"):
			mat_id = str(mi.get_meta("mat_id"))
		mi.material_override = _Mat.make_stage_material(mat_id, stage, placement_valid)


func _infer_category(module_id: String) -> String:
	if module_id.begins_with("terrain_"):
		return "Terrain"
	if module_id.begins_with("arch_"):
		return "Architecture"
	if module_id.begins_with("cluster_"):
		return "Cluster"
	if module_id.begins_with("prop_"):
		return "Prop"
	if module_id.begins_with("char_"):
		return "Character"
	if module_id.begins_with("block_"):
		return "Primitive"
	return "Primitive"


func _category_to_role(category: String) -> String:
	match category:
		"Terrain":
			return "terrain"
		"Architecture":
			return "structure"
		"Cluster":
			return "cluster"
		"Prop":
			return "prop"
		"Character":
			return "character"
		_:
			return "structure"


func _pretty_name(module_id: String) -> String:
	return module_id.replace("_", " ").capitalize()


func _default_primitive(module_id: String) -> String:
	if "sphere" in module_id or "dome" in module_id:
		return "SphereMesh"
	if "cylinder" in module_id or "pipe" in module_id or "lamp" in module_id:
		return "CylinderMesh"
	if "ramp" in module_id or "wedge" in module_id:
		return "BoxMesh"
	return "BoxMesh"


func _slot_map_from_desc(desc: Dictionary) -> Dictionary:
	var out := {}
	for s in desc.get("material_slots", []):
		if s is Dictionary:
			var name := str((s as Dictionary).get("name", ""))
			var mat := str((s as Dictionary).get("mat", ""))
			if not name.is_empty() and not mat.is_empty():
				out[name] = mat
	return out


func _build_part_mesh(
	part: Dictionary,
	slot_to_mat: Dictionary,
	stage: String,
	placement_valid: bool
) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var part_id := str(part.get("part_id", "part"))
	mi.name = part_id
	var slot := str(part.get("material_slot", "body"))
	var mat_id := str(part.get("mat", part.get("mat_id", "")))
	if mat_id.is_empty():
		mat_id = str(slot_to_mat.get(slot, _Mat.mat_for_slot(slot)))
	mi.set_meta("material_slot", slot)
	mi.set_meta("mat_id", mat_id)
	mi.mesh = _primitive_mesh(part)
	mi.material_override = _Mat.make_stage_material(mat_id, stage, placement_valid)
	var off: Array = part.get("offset", [0.0, 0.0, 0.0]) as Array
	if off.size() >= 3:
		mi.position = Vector3(float(off[0]), float(off[1]), float(off[2]))
	return mi


func _primitive_mesh(part: Dictionary) -> Mesh:
	var prim := str(part.get("primitive", "BoxMesh")).to_lower()
	var size: Array = part.get("size", []) as Array
	var sx := float(size[0]) if size.size() > 0 else 1.0
	var sy := float(size[1]) if size.size() > 1 else 1.0
	var sz := float(size[2]) if size.size() > 2 else 1.0
	if "sphere" in prim:
		var sph := SphereMesh.new()
		if part.has("radius"):
			var r := float(part.get("radius", 0.5))
			sph.radius = r
			sph.height = float(part.get("height", r * 2.0))
		else:
			sph.radius = maxf(sx, sz) * 0.5
			sph.height = sy if sy > 0.001 else sph.radius * 2.0
		if "hemisphere" in prim:
			sph.height = float(part.get("height", sph.height * 0.5))
			sph.is_hemisphere = true
		return sph
	if "capsule" in prim:
		var cap := CapsuleMesh.new()
		cap.radius = maxf(sx, sz) * 0.5
		cap.height = maxf(sy, cap.radius * 2.0 + 0.01)
		return cap
	if "cylinder" in prim:
		var cyl := CylinderMesh.new()
		cyl.top_radius = maxf(sx, sz) * 0.5
		cyl.bottom_radius = cyl.top_radius
		cyl.height = sy if sy > 0.001 else 0.5
		return cyl
	var box := BoxMesh.new()
	if "torus" in prim:
		box.size = Vector3(maxf(sx, 0.2), maxf(sy, 0.05), maxf(sz, 0.2))
	else:
		box.size = Vector3(maxf(sx, 0.05), maxf(sy, 0.05), maxf(sz, 0.05))
	return box
