## H1 asset — Dreamy Low-Poly Starter Realm.
## Dual path: Bridge quarantine GLB intake (runtime, no res:// copy) when package
## resolves; otherwise pure Godot primitives. Palette from ArtStyleManager.
## Skips meshes under headless/dummy for procedural path.
class_name StarterRealmBuilder
extends RefCounted

const GROUP_LANDMARKS := "starter_realm_landmarks"
const ROOT_NAME := "StarterRealm"
const _GlbRuntimeBuilder = preload("res://scripts/modules/asset/glb_intake_runtime_builder.gd")
const _GlbPackage = preload("res://scripts/modules/asset/glb_intake_package.gd")
const _MeshLifecycle = preload("res://scripts/modules/asset/mesh_presentation_lifecycle.gd")

## When true (default), prefer quarantine GLB intake if package is present.
## Set OS env AIDLE_STARTER_PROCEDURAL=1 to force pure procedural (regression path).
## Set AIDLE_GLB_PACKAGE to override quarantine package root.
static func prefer_glb_intake() -> bool:
	var force_proc := OS.get_environment("AIDLE_STARTER_PROCEDURAL")
	if force_proc == "1" or force_proc.to_lower() == "true":
		return false
	var force_glb := OS.get_environment("AIDLE_STARTER_GLB_INTAKE")
	if force_glb == "0" or force_glb.to_lower() == "false":
		return false
	return true


static func is_headless() -> bool:
	if AIdleConstants != null and AIdleConstants.has_method("is_headless_or_dummy_presentation"):
		return bool(AIdleConstants.is_headless_or_dummy_presentation())
	return OS.has_feature("headless") or DisplayServer.get_name() == "headless"


## Build or rebuild under PrivateReality. Returns root Node3D.
## options (optional 2nd arg via build_into_opts):
##   force_procedural, force_glb, package_path, enable_collision
##   attach_town_cadastre (bool, default false) — if true, also mounts
##   TownCadastre via town_grid_loader under the realm root (Directive 99).
##   Does NOT remove procedural/GLB realm content.
static func build_into(private_reality: Node3D) -> Node3D:
	return build_into_opts(private_reality, {})


static func build_into_opts(private_reality: Node3D, options: Dictionary = {}) -> Node3D:
	if private_reality == null:
		return null
	var existing := private_reality.get_node_or_null(ROOT_NAME)
	if existing != null:
		# Product headless-safe rebuild: detach presentation meshes before free
		# (dummy renderer mesh_get_surface_count null RID on MeshInstance3D free).
		_MeshLifecycle.safe_free(existing)

	var force_procedural := bool(options.get("force_procedural", false))
	var force_glb := bool(options.get("force_glb", false))
	var use_glb := (force_glb or prefer_glb_intake()) and not force_procedural
	var realm_root: Node3D = null
	if use_glb:
		var glb_root := _try_build_glb_intake(private_reality, options)
		if glb_root != null:
			realm_root = glb_root
	if realm_root == null:
		if use_glb:
			print("[StarterRealmBuilder] GLB intake unavailable — falling back to procedural primitives.")
		realm_root = _build_procedural(private_reality)
	## Optional cadastre attach — additive only (WO-TOWN-GRID-IMPORT-001). Default off;
	## main.gd mounts TownCadastre at world root so play sees the map without duplicating.
	if bool(options.get("attach_town_cadastre", false)) and realm_root != null:
		_try_attach_town_cadastre(realm_root)
	return realm_root


## Additive: child TownCadastre under an existing realm. Never deletes landmarks.
static func _try_attach_town_cadastre(realm_root: Node3D) -> void:
	if realm_root == null:
		return
	if realm_root.get_node_or_null("TownCadastre") != null:
		return
	var script_path := "res://scripts/modules/town/town_grid_loader.gd"
	if not ResourceLoader.exists(script_path):
		return
	var loader_script: Script = load(script_path) as Script
	if loader_script == null:
		return
	var cad: Node3D = loader_script.new() as Node3D
	if cad == null:
		return
	cad.name = "TownCadastre"
	realm_root.add_child(cad)
	if cad.has_method("build_cadastre"):
		cad.call("build_cadastre")
		print("[StarterRealmBuilder] TownCadastre attached under realm (flag attach_town_cadastre).")


## Product teardown for a Starter Realm (or any mesh-bearing subtree).
## Callers that free PrivateReality/world trees should use this path rather than
## raw free/queue_free so headless dummy never sees residual presentation meshes.
static func dispose_realm(realm: Node) -> void:
	_MeshLifecycle.safe_free(realm)


## Detach presentation meshes under headless so later free/queue_free is clean
## even when the caller does not go through dispose_realm (e.g. parent free).
static func ensure_headless_free_safe(realm: Node) -> int:
	return _MeshLifecycle.ensure_headless_free_safe(realm)


static func _try_build_glb_intake(private_reality: Node3D, options: Dictionary) -> Node3D:
	var package_path := str(options.get("package_path", _GlbPackage.default_package_path()))
	if not DirAccess.dir_exists_absolute(package_path.replace("\\", "/")):
		return null
	var builder = _GlbRuntimeBuilder.new()
	var enable_col := bool(options.get("enable_collision", true))
	var res: Dictionary = builder.call(
		"build_realm",
		package_path,
		{
			"parent": private_reality,
			"enable_collision": enable_col,
			"bake_navigation": bool(options.get("bake_navigation", true)),
			"collision_layer": int(options.get("collision_layer", 1)),
		}
	) as Dictionary
	if not bool(res.get("ok", false)):
		print("[StarterRealmBuilder] GLB intake failed: %s" % str(res.get("reason", "?")))
		return null
	var root: Node3D = res.get("root", null) as Node3D
	if root == null:
		return null
	# Procedural fillers: keep UX-002 fence rails always (regression).
	# Skip flowers/stones/extra lamps when P1E-003 density kit is present (35+ modules).
	var palette := _palette()
	_build_ground_variation(root, palette)
	_build_fence(root, palette)
	var kit_dense := int(res.get("module_count", 0)) >= 30
	if not kit_dense:
		_build_stones(root, palette)
		_build_flowers(root, palette)
		if root.get_node_or_null("Lamps") == null:
			_build_lamps(root, palette)
	_annotate_intake(root, res)
	# WO-P1E-006: STATE_VARIANTS-style world-profile visual selector (after GLB attach).
	var variant_report := _apply_world_profile_variant(root, options)
	# Procedural fillers may add meshes on headed; under headless ensure free-safe tree
	# (GLB path already detaches intake + NavSourcePlane inside runtime builder).
	var detached := _MeshLifecycle.ensure_headless_free_safe(root)
	root.set_meta("headless_presentation_detached", detached)
	print(
		"[StarterRealmBuilder] Built via GLB intake | job=%s modules=%s collision=%s headless=%s profile=%s"
		% [
			str(res.get("job_id", "")),
			str(res.get("module_count", 0)),
			str(res.get("collision_enabled", false)),
			str(is_headless()),
			str(variant_report.get("world_profile", "")),
		]
	)
	return root


static func _apply_world_profile_variant(root: Node3D, options: Dictionary = {}) -> Dictionary:
	var sel = load("res://scripts/modules/asset/world_profile_variant_selector.gd").new()
	if sel == null:
		return {"ok": false, "error": "selector_load"}
	var profile := str(options.get("world_profile", ""))
	return sel.call("apply_to_node", root, profile) as Dictionary


static func _build_procedural(private_reality: Node3D) -> Node3D:
	var root := Node3D.new()
	root.name = ROOT_NAME
	root.add_to_group(GROUP_LANDMARKS)
	root.set_meta("starter_realm", true)
	root.set_meta("glb_intake_realm", false)
	private_reality.add_child(root)

	var palette := _palette()
	# Always create collision-bearing landmarks; mesh only when presentation allowed.
	_build_ground_variation(root, palette)
	_build_house(root, palette)
	_build_path(root, palette)
	_build_farm(root, palette)
	_build_trees(root, palette)
	_build_fence(root, palette)
	_build_pond(root, palette)
	_build_stones(root, palette)
	_build_lamps(root, palette)
	_build_flowers(root, palette)
	_apply_world_profile_variant(root, {})
	_annotate(root)
	# Procedural path skips mesh create under headless; still mark free-safe for consistency.
	var detached := _MeshLifecycle.ensure_headless_free_safe(root)
	root.set_meta("headless_presentation_detached", detached)
	print(
		"[StarterRealmBuilder] Built landmarks under PrivateReality | headless_meshes=%s style_ground=%s"
		% [str(is_headless()), str(palette.get("ground", Color.GRAY))]
	)
	return root


static func _annotate_intake(root: Node3D, res: Dictionary) -> void:
	root.set_meta("landmark_count", landmark_names().size())
	root.set_meta("prop_groups", ["Trees", "Fence", "Pond", "Stones", "Lamps", "Flowers"])
	root.set_meta("has_house", root.get_node_or_null("House") != null)
	root.set_meta("has_farm", root.get_node_or_null("FarmPlots") != null)
	root.set_meta("has_path", root.get_node_or_null("Path") != null)
	root.set_meta("intake_job_id", str(res.get("job_id", "")))
	root.set_meta("intake_module_count", int(res.get("module_count", 0)))
	root.set_meta("navigation_baked", bool(res.get("navigation_bake_ok", false)))


static func landmark_names() -> PackedStringArray:
	return PackedStringArray([
		"House", "Path", "FarmPlots", "Trees", "Fence", "Pond", "Stones", "Lamps", "Flowers",
	])


static func count_landmarks(private_reality: Node3D) -> int:
	if private_reality == null:
		return 0
	var root := private_reality.get_node_or_null(ROOT_NAME)
	if root == null:
		return 0
	var n := 0
	for name in landmark_names():
		if root.get_node_or_null(name) != null:
			n += 1
	return n


static func _palette() -> Dictionary:
	## Prefer DESIGN.md Cozy tokens for landmark readability. Surrealism may tint sky
	## via WorldEnvironment but must not flatten landmarks into one purple field.
	var style: Dictionary = {}
	var style_id := ""
	if ArtStyleManager != null:
		style = ArtStyleManager.get_active_style()
		style_id = str(ArtStyleManager.get_active_style_id())
	var p: Dictionary = style.get("palette", {}) as Dictionary
	var cozy_ground := Color("C9B98A")
	var cozy_sky := Color("9ED7E5")
	var cozy_leaf := Color("72A96B")
	# When surrealism is active, keep warm ground/path/leaf so landmarks stay readable.
	var surreal := style_id == "surrealism_canvas"
	return {
		"primary": _c(p.get("primary", p.get("surface_primary", Color("F7B267")))),
		"secondary": _c(p.get("secondary", p.get("surface_secondary", Color("E8D5B5")))),
		"accent": _c(p.get("accent", Color("E07A5F"))),
		"ground": cozy_ground if surreal else _c(p.get("ground", cozy_ground)),
		"ground_alt": Color("B8C97A") if not surreal else Color("A89BC8"),
		"sky": cozy_sky if surreal else _c(p.get("sky", cozy_sky)),
		"leaf": cozy_leaf if surreal else _c(p.get("leaf", cozy_leaf)),
		"ink": _c(p.get("ink", Color("263238"))),
		"cream": _c(p.get("cream_light", Color("FFF1C7"))),
		"water": Color("4A90A4"),
		"soil": Color("6B4F2A"),
		"path": Color("C4A574"),
		"wood": Color("8B5A2B"),
		"stone": Color("8A8F98"),
		"flower": Color("E07A9A"),
		"lamp": Color("FFE08A"),
		"style_id": style_id,
	}


static func _build_ground_variation(root: Node3D, p: Dictionary) -> void:
	## Breaks single-color ground: soft patches of grass / soil islands (DESIGN.md rhythm).
	var patches := Node3D.new()
	patches.name = "GroundVariation"
	root.add_child(patches)
	var spots := [
		[Vector3(0, 0.01, 0), Vector3(10, 0.02, 10), p["ground"]],
		[Vector3(4, 0.015, 3), Vector3(5, 0.02, 4), p["ground_alt"]],
		[Vector3(-5, 0.015, -3), Vector3(4, 0.02, 5), p["ground_alt"]],
		[Vector3(2, 0.012, -6), Vector3(3.5, 0.02, 3), p.get("leaf", Color("72A96B")).darkened(0.15)],
	]
	var i := 0
	for s in spots:
		_box(patches, "Patch%d" % i, s[1], s[0], s[2], false)
		i += 1



static func _c(v: Variant) -> Color:
	if v is Color:
		return v
	return Color(str(v))


static func _mat(color: Color, roughness: float = 0.85, emission: float = 0.0) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.roughness = roughness
	if emission > 0.0:
		m.emission_enabled = true
		m.emission = color
		m.emission_energy_multiplier = emission
	return m


static func _box(parent: Node3D, name: String, size: Vector3, pos: Vector3, color: Color, with_collision: bool = true) -> Node3D:
	var holder := Node3D.new()
	holder.name = name
	holder.position = pos
	parent.add_child(holder)
	if not is_headless():
		var mi := MeshInstance3D.new()
		var mesh := BoxMesh.new()
		mesh.size = size
		mi.mesh = mesh
		mi.material_override = _mat(color)
		holder.add_child(mi)
	if with_collision:
		var body := StaticBody3D.new()
		body.collision_layer = 1
		body.collision_mask = 0
		var shape := CollisionShape3D.new()
		var box := BoxShape3D.new()
		box.size = size
		shape.shape = box
		body.add_child(shape)
		holder.add_child(body)
	return holder


static func _cyl(parent: Node3D, name: String, radius: float, height: float, pos: Vector3, color: Color, with_collision: bool = false) -> Node3D:
	var holder := Node3D.new()
	holder.name = name
	holder.position = pos
	parent.add_child(holder)
	if not is_headless():
		var mi := MeshInstance3D.new()
		var mesh := CylinderMesh.new()
		mesh.top_radius = radius
		mesh.bottom_radius = radius
		mesh.height = height
		mi.mesh = mesh
		mi.material_override = _mat(color)
		holder.add_child(mi)
	if with_collision:
		var body := StaticBody3D.new()
		body.collision_layer = 1
		var shape := CollisionShape3D.new()
		var cyl := CylinderShape3D.new()
		cyl.radius = radius
		cyl.height = height
		shape.shape = cyl
		body.add_child(shape)
		holder.add_child(body)
	return holder


static func _sphere(parent: Node3D, name: String, radius: float, pos: Vector3, color: Color) -> Node3D:
	var holder := Node3D.new()
	holder.name = name
	holder.position = pos
	parent.add_child(holder)
	if not is_headless():
		var mi := MeshInstance3D.new()
		var mesh := SphereMesh.new()
		mesh.radius = radius
		mesh.height = radius * 2.0
		mi.mesh = mesh
		mi.material_override = _mat(color)
		holder.add_child(mi)
	return holder


static func _build_house(root: Node3D, p: Dictionary) -> void:
	var house := Node3D.new()
	house.name = "House"
	house.position = Vector3(-4.0, 0.0, -6.0)
	root.add_child(house)
	# Body
	_box(house, "Body", Vector3(4.2, 2.4, 3.6), Vector3(0, 1.2, 0), p["cream"], true)
	# Roof (pyramid-ish via flat sloped box)
	_box(house, "Roof", Vector3(4.8, 0.55, 4.0), Vector3(0, 2.7, 0), p["accent"], false)
	# Door
	_box(house, "Door", Vector3(0.9, 1.5, 0.12), Vector3(0, 0.75, 1.85), p["wood"], false)
	# Windows
	_box(house, "WinL", Vector3(0.7, 0.7, 0.1), Vector3(-1.2, 1.4, 1.85), p["secondary"], false)
	_box(house, "WinR", Vector3(0.7, 0.7, 0.1), Vector3(1.2, 1.4, 1.85), p["secondary"], false)
	# Chimney
	_box(house, "Chimney", Vector3(0.45, 1.0, 0.45), Vector3(1.4, 3.2, -0.6), p["stone"], false)
	house.set_meta("landmark", "house")


static func _build_path(root: Node3D, p: Dictionary) -> void:
	var path := Node3D.new()
	path.name = "Path"
	root.add_child(path)
	# Spawn (0,0,2) → house (-4,-6) → farm (5,-2)
	var segments := [
		[Vector3(0.0, 0.03, 0.5), Vector3(1.4, 0.06, 3.0)],
		[Vector3(-1.5, 0.03, -2.0), Vector3(1.2, 0.06, 3.5)],
		[Vector3(-3.2, 0.03, -4.5), Vector3(1.2, 0.06, 2.5)],
		[Vector3(0.5, 0.03, -2.0), Vector3(4.0, 0.06, 1.0)],
		[Vector3(3.5, 0.03, -2.0), Vector3(2.5, 0.06, 1.0)],
	]
	var i := 0
	for seg in segments:
		_box(path, "Seg%d" % i, seg[1], seg[0], p["path"], false)
		i += 1
	path.set_meta("landmark", "path")


static func _build_farm(root: Node3D, p: Dictionary) -> void:
	var farm := Node3D.new()
	farm.name = "FarmPlots"
	farm.position = Vector3(5.0, 0.0, -2.0)
	root.add_child(farm)
	for r in range(2):
		for c in range(3):
			var soil_pos := Vector3((c - 1) * 1.6, 0.05, (r - 0.5) * 1.5)
			_box(farm, "Soil_%d_%d" % [r, c], Vector3(1.3, 0.12, 1.2), soil_pos, p["soil"], false)
			# Crop markers (taller green)
			_box(
				farm,
				"Crop_%d_%d" % [r, c],
				Vector3(0.25, 0.45 + float(c) * 0.08, 0.25),
				soil_pos + Vector3(0, 0.3, 0),
				p["leaf"],
				false
			)
	farm.set_meta("landmark", "farm")


static func _build_trees(root: Node3D, p: Dictionary) -> void:
	var trees := Node3D.new()
	trees.name = "Trees"
	root.add_child(trees)
	var spots := [Vector3(7, 0, 3), Vector3(-7, 0, 1), Vector3(-6, 0, -9), Vector3(2, 0, -10)]
	var i := 0
	for s in spots:
		var t := Node3D.new()
		t.name = "Tree%d" % i
		t.position = s
		trees.add_child(t)
		_cyl(t, "Trunk", 0.22, 1.4, Vector3(0, 0.7, 0), p["wood"], true)
		_sphere(t, "Canopy", 0.95, Vector3(0, 1.9, 0), p["leaf"])
		i += 1
	trees.set_meta("landmark", "trees")


static func _build_fence(root: Node3D, p: Dictionary) -> void:
	var fence := Node3D.new()
	fence.name = "Fence"
	fence.position = Vector3(5.0, 0.0, 0.5)
	root.add_child(fence)
	for i in range(5):
		_box(fence, "Post%d" % i, Vector3(0.12, 0.9, 0.12), Vector3((i - 2) * 1.1, 0.45, 0), p["wood"], true)
		if i < 4:
			_box(fence, "Rail%d" % i, Vector3(1.0, 0.08, 0.06), Vector3((i - 1.5) * 1.1, 0.55, 0), p["wood"], true)
	fence.set_meta("landmark", "fence")


static func _build_pond(root: Node3D, p: Dictionary) -> void:
	var pond := Node3D.new()
	pond.name = "Pond"
	pond.position = Vector3(3.5, 0.02, 4.5)
	root.add_child(pond)
	_cyl(pond, "Water", 1.8, 0.08, Vector3(0, 0.04, 0), p["water"], false)
	_box(pond, "Rim", Vector3(4.0, 0.1, 4.0), Vector3(0, 0.02, 0), p["stone"], false)
	pond.set_meta("landmark", "pond")


static func _build_stones(root: Node3D, p: Dictionary) -> void:
	var stones := Node3D.new()
	stones.name = "Stones"
	root.add_child(stones)
	var spots := [Vector3(-2, 0.15, 3), Vector3(1.5, 0.12, -5), Vector3(-5, 0.18, 4)]
	var i := 0
	for s in spots:
		_box(stones, "Rock%d" % i, Vector3(0.5 + i * 0.1, 0.3, 0.4), s, p["stone"], true)
		i += 1
	stones.set_meta("landmark", "stones")


static func _build_lamps(root: Node3D, p: Dictionary) -> void:
	var lamps := Node3D.new()
	lamps.name = "Lamps"
	root.add_child(lamps)
	for i in range(2):
		var x := -1.0 if i == 0 else 1.0
		var L := Node3D.new()
		L.name = "Lamp%d" % i
		L.position = Vector3(x * 2.5, 0, 1.0)
		lamps.add_child(L)
		_cyl(L, "Pole", 0.08, 1.6, Vector3(0, 0.8, 0), p["ink"], true)
		_sphere(L, "Bulb", 0.22, Vector3(0, 1.7, 0), p["lamp"])
		if not is_headless():
			var light := OmniLight3D.new()
			light.light_color = p["lamp"]
			light.light_energy = 0.55
			light.omni_range = 4.0
			light.position = Vector3(0, 1.7, 0)
			L.add_child(light)
	lamps.set_meta("landmark", "lamps")


static func _build_flowers(root: Node3D, p: Dictionary) -> void:
	var flowers := Node3D.new()
	flowers.name = "Flowers"
	root.add_child(flowers)
	var spots := [
		Vector3(-3.5, 0.1, -3.5), Vector3(-2.8, 0.1, -3.2), Vector3(-3.2, 0.1, -2.8),
		Vector3(6.5, 0.1, -3.5), Vector3(6.8, 0.1, -3.0),
	]
	var i := 0
	for s in spots:
		_box(flowers, "Stem%d" % i, Vector3(0.06, 0.25, 0.06), s + Vector3(0, 0.12, 0), p["leaf"], false)
		_sphere(flowers, "Bloom%d" % i, 0.12, s + Vector3(0, 0.32, 0), p["flower"] if i % 2 == 0 else p["accent"])
		i += 1
	flowers.set_meta("landmark", "flowers")


static func _annotate(root: Node3D) -> void:
	root.set_meta("landmark_count", landmark_names().size())
	root.set_meta("prop_groups", ["Trees", "Fence", "Pond", "Stones", "Lamps", "Flowers"])
	root.set_meta("has_house", true)
	root.set_meta("has_farm", true)
	root.set_meta("has_path", true)
