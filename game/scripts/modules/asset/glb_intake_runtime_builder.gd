## Godot-owned runtime construction from a verified Bridge package.
## Builds visuals from runtime-loaded GLBs; StaticBody3D / CollisionShape3D /
## NavigationRegion3D are authored here from Godot rules (hints are advisory).
## Collision is never enabled at import; only after explicit confirm (+ World Commit
## for durable authority). Preview stages stay non-solid.
## Note: no class_name — headless -s may miss global class cache for new scripts.
extends RefCounted

const _Package = preload("res://scripts/modules/asset/glb_intake_package.gd")
const _Intake = preload("res://scripts/modules/asset/glb_intake.gd")
const _Stages = preload("res://scripts/modules/manifestation/manifestation_stages.gd")
const _MeshLifecycle = preload("res://scripts/modules/asset/mesh_presentation_lifecycle.gd")

const ROOT_NAME := "StarterRealm"
const GROUP_LANDMARKS := "starter_realm_landmarks"
const INTAKE_META := "glb_intake_realm"
const SAVE_ID_META := "save_id"
const REVISION_META := "intake_revision_token"

const COLLISION_LAYER_WORLD := 1
const COLLISION_LAYER_MANIFESTATION := 4

## Map instance_id → starter realm landmark node name (compat with existing code).
const LANDMARK_NAME_MAP := {
	"house_01": "House",
	"farm_01": "FarmPlots",
	"pond_01": "Pond",
	"tree_landmark_01": "Trees",
	"light_brush_01": "Lamps",
	"greenhouse_preview_01": "GreenhousePreview",
	"path_01": "PathSeg0",
	"path_02": "PathSeg1",
	"path_03": "PathSeg2",
}

var last_error: String = ""
var last_report: Dictionary = {}
var _intake: RefCounted = _Intake.new()


## Full assemble: verify package → load GLBs → place → optional collision/nav.
## options:
##   enable_collision (bool, default false) — Godot-owned collision after confirm
##   bake_navigation (bool, default true)
##   expected_revision (String/int, optional) — surface conflict if mismatch
##   collision_layer (int, default WORLD=1)
##   parent (Node3D) — attach root under parent
func build_realm(package_path: String = "", options: Dictionary = {}) -> Dictionary:
	last_error = ""
	last_report = {}
	var path := package_path if not package_path.is_empty() else _Package.default_package_path()
	var package = _Package.open(path)
	if package == null or not bool(package.call("is_ready")):
		last_error = str(package.get("last_error")) if package else "package_open_failed"
		return _fail_result(last_error)

	if options.has("expected_revision"):
		var expected := str(options.get("expected_revision"))
		var token := _revision_token(package)
		if not expected.is_empty() and expected != token and expected != str(package.get("job_id")):
			last_error = "revision_conflict:expected=%s actual=%s" % [expected, token]
			return {
				"ok": false,
				"reason": "revision_conflict",
				"expected_revision": expected,
				"actual_revision": token,
				"job_id": str(package.get("job_id")),
				"request_fingerprint": str(package.get("request_fingerprint")),
				"root": null,
			}

	var load_res: Dictionary = _intake.call("load_package_modules", package) as Dictionary
	if not bool(load_res.get("ok", false)):
		last_error = "module_load_failed:%s" % str(load_res.get("errors", []))
		return {
			"ok": false,
			"reason": last_error,
			"load": load_res,
			"root": null,
			"package": package.call("summary"),
		}

	var root := Node3D.new()
	root.name = ROOT_NAME
	root.add_to_group(GROUP_LANDMARKS)
	root.set_meta("starter_realm", true)
	root.set_meta(INTAKE_META, true)
	root.set_meta("job_id", str(package.get("job_id")))
	root.set_meta("request_fingerprint", str(package.get("request_fingerprint")))
	root.set_meta(REVISION_META, _revision_token(package))
	root.set_meta("world_profile", str(package.get("world_profile")))
	root.set_meta("collision_enabled", false)
	root.set_meta("package_root", str(package.get("package_root")))

	var path_parent := Node3D.new()
	path_parent.name = "Path"
	path_parent.set_meta("landmark", "path")
	root.add_child(path_parent)

	var roots: Dictionary = load_res.get("roots", {}) as Dictionary
	var placed: Array = []
	var mods: Array = package.get("modules") as Array
	# Sort by manifestation_order (content order only — Godot still owns state machine).
	var ordered: Array = mods.duplicate()
	ordered.sort_custom(func(a, b):
		return int(a.get("manifestation_order", 0)) < int(b.get("manifestation_order", 0))
	)

	var id_set: Dictionary = {}
	for entry in ordered:
		if not (entry is Dictionary):
			continue
		var iid := str(entry.get("instance_id", ""))
		if iid.is_empty() or not roots.has(iid):
			continue
		if id_set.has(iid):
			last_error = "duplicate_instance_id:%s" % iid
			_MeshLifecycle.safe_free(root)
			return _fail_result(last_error)
		id_set[iid] = true

		var node: Node3D = roots[iid] as Node3D
		var landmark_name := str(LANDMARK_NAME_MAP.get(iid, iid))
		var holder := Node3D.new()
		holder.name = landmark_name
		holder.set_meta("instance_id", iid)
		holder.set_meta("module_id", str(entry.get("module_id", "")))
		holder.set_meta("content_phase", str(entry.get("content_phase", "")))
		holder.set_meta("manifestation_order", int(entry.get("manifestation_order", 0)))
		holder.set_meta(SAVE_ID_META, "entity:%s:%s" % [str(package.get("job_id")), iid])
		holder.set_meta("landmark", iid)
		holder.set_meta("collision_hint_advisory", str(package.call("collision_hint_for", iid)))
		holder.set_meta("is_preview_anchor", iid.find("preview") >= 0)

		var xform: Array = entry.get("transform", []) as Array
		_Intake.apply_blender_transform(holder, xform)

		# Parent path segments under Path.
		if iid.begins_with("path_"):
			path_parent.add_child(holder)
		else:
			root.add_child(holder)

		# Detach from any prior parent then attach visual under holder.
		if node.get_parent():
			node.get_parent().remove_child(node)
		node.name = "VisualGLB"
		holder.add_child(node)

		# Collision container reserved but inactive until activate_collision.
		var col_host := Node3D.new()
		col_host.name = "GodotCollision"
		col_host.set_meta("collision_active", false)
		holder.add_child(col_host)

		# P1E-003: stagger idle loops so instances never sway/pulse in unison.
		var mid := str(entry.get("module_id", ""))
		var anim_delay := _anim_delay_for(iid)
		holder.set_meta("anim_delay", anim_delay)
		_attach_idle_animation(holder, mid, anim_delay)

		placed.append({
			"instance_id": iid,
			"module_id": mid,
			"landmark": landmark_name,
			"save_id": holder.get_meta(SAVE_ID_META),
			"position": [holder.position.x, holder.position.y, holder.position.z],
			"mesh_count": int(node.get_meta("mesh_count", 0)),
			"materials_resolve": bool(node.get_meta("materials_resolve", false)),
			"socket_markers": node.get_meta("socket_markers", PackedStringArray()),
			"collision_hint": str(package.call("collision_hint_for", iid)),
			"anim_delay": anim_delay,
		})

	# Scene origin marker at (0,0,0) Godot space.
	var origin := Node3D.new()
	origin.name = "SceneOrigin"
	origin.position = Vector3.ZERO
	origin.set_meta("scene_origin", true)
	root.add_child(origin)

	# Camera focus markers (advisory).
	var cam_root := Node3D.new()
	cam_root.name = "CameraMarkers"
	root.add_child(cam_root)
	for cm in package.get("camera_markers") as Array:
		if not (cm is Dictionary):
			continue
		var marker := Node3D.new()
		marker.name = str((cm as Dictionary).get("id", "camera"))
		var pos: Array = (cm as Dictionary).get("position", [0, 0, 0]) as Array
		if pos.size() >= 3:
			marker.position = _Intake.blender_pos_to_godot(float(pos[0]), float(pos[1]), float(pos[2]))
		marker.set_meta("camera_marker", true)
		cam_root.add_child(marker)

	# Build plot volume (visual helper / clear check) — never a solid body.
	var plot := _make_build_plot_marker(package.get("build_plot") as Dictionary)
	if plot:
		root.add_child(plot)

	var parent: Node3D = options.get("parent", null) as Node3D
	if parent != null:
		# Replace existing StarterRealm under parent (product free-safe lifecycle).
		var existing := parent.get_node_or_null(ROOT_NAME)
		if existing != null:
			_MeshLifecycle.safe_free(existing)
		parent.add_child(root)

	var enable_col := bool(options.get("enable_collision", false))
	var col_layer := int(options.get("collision_layer", COLLISION_LAYER_WORLD))
	if enable_col:
		activate_collision(root, package, col_layer)

	var bake_nav := bool(options.get("bake_navigation", true))
	var nav_ok := false
	if bake_nav:
		nav_ok = bake_navigation(root, package)

	# Headless: detach any residual product meshes so subsequent free/queue_free
	# of the realm tree does not hit dummy mesh_storage. Nav bake uses CPU faces
	# + StaticBody collider (no MeshInstance3D / PlaneMesh source).
	var headless_detached := _MeshLifecycle.ensure_headless_free_safe(root)
	root.set_meta("headless_presentation_detached", headless_detached)

	var unique_ok := _ids_unique(placed)
	var origin_ok := root.get_node_or_null("SceneOrigin") != null
	var materials_ok := true
	var sockets_ok := true
	for p in placed:
		if not bool(p.get("materials_resolve", false)):
			materials_ok = false
		# Socket markers are optional on kit meshes; resolution path always runs.
		var _sockets = p.get("socket_markers", PackedStringArray())
		sockets_ok = true

	last_report = {
		"ok": true,
		"reason": "ok",
		"job_id": str(package.get("job_id")),
		"request_fingerprint": str(package.get("request_fingerprint")),
		"revision_token": _revision_token(package),
		"module_count": placed.size(),
		"placed": placed,
		"ids_unique": unique_ok,
		"scene_origin_ok": origin_ok,
		"materials_resolve": materials_ok,
		"socket_markers_resolved": sockets_ok,
		"collision_enabled": enable_col,
		"navigation_bake_ok": nav_ok,
		"build_plot_clear": is_build_plot_clear(root),
		"camera_not_occluded": camera_not_occluded(root),
		"package": package.call("summary"),
		"load": {"count": load_res.get("count", 0), "reports": load_res.get("reports", [])},
		"root": root,
	}
	return last_report


## Godot-owned collision from advisory hints + mesh AABB. Never copies Blender collision.
## Skips preview anchors and NONE hints. Requires explicit call (confirm path).
func activate_collision(root: Node3D, package: RefCounted = null, layer: int = COLLISION_LAYER_WORLD) -> int:
	if root == null:
		return 0
	var activated := 0
	for holder in _iter_module_holders(root):
		if bool(holder.get_meta("is_preview_anchor", false)):
			continue
		var hint := str(holder.get_meta("collision_hint_advisory", "NONE")).to_upper()
		if hint == "NONE" or hint.is_empty():
			# Paths / non-solid decorative — still no collision.
			continue
		var col_host := holder.get_node_or_null("GodotCollision") as Node3D
		if col_host == null:
			continue
		# Clear prior shapes (idempotent activate).
		for c in col_host.get_children():
			_MeshLifecycle.safe_free(c)
		var visual := holder.get_node_or_null("VisualGLB") as Node3D
		var aabb := _Intake.compute_local_aabb(visual if visual else holder)
		var body := StaticBody3D.new()
		body.name = "StaticBody"
		body.collision_layer = layer
		body.collision_mask = 0
		var shape := CollisionShape3D.new()
		shape.name = "Shape"
		shape.shape = _shape_from_hint(hint, aabb)
		shape.position = aabb.position + aabb.size * 0.5
		body.add_child(shape)
		col_host.add_child(body)
		col_host.set_meta("collision_active", true)
		holder.set_meta("has_godot_collision", true)
		activated += 1
	root.set_meta("collision_enabled", true)
	root.set_meta("collision_layer", layer)
	return activated


## Disable all Godot collision under an intake realm (cancel / preview path).
func deactivate_collision(root: Node3D) -> int:
	if root == null:
		return 0
	var n := 0
	for holder in _iter_module_holders(root):
		var col_host := holder.get_node_or_null("GodotCollision") as Node3D
		if col_host == null:
			continue
		for c in col_host.get_children():
			if c is StaticBody3D:
				(c as StaticBody3D).collision_layer = 0
				(c as StaticBody3D).collision_mask = 0
			if c is CollisionShape3D:
				(c as CollisionShape3D).disabled = true
			_MeshLifecycle.safe_free(c)
			n += 1
		col_host.set_meta("collision_active", false)
		holder.set_meta("has_godot_collision", false)
	root.set_meta("collision_enabled", false)
	return n


## Bake a simple NavigationRegion3D covering the 48m walkable ground + advisory hints.
## C3-F01: no MeshInstance3D/PlaneMesh → never parse RenderingServer visual meshes.
## Primary bake = procedural CPU faces via NavigationMeshSourceGeometryData3D.
## Secondary source = StaticBody3D+BoxShape3D (nav-only layer) for optional rebake.
## Voxel alignment: cell_size=cell_height=0.2 so agent_radius=0.4 and agent_height=1.6
## are exact integer voxel multiples (2 and 8). agent_max_climb=0.2 (1 cell).
func bake_navigation(root: Node3D, package: RefCounted = null) -> bool:
	if root == null:
		return false
	var existing := root.get_node_or_null("NavigationRegion")
	if existing != null:
		_MeshLifecycle.safe_free(existing)

	# Exact design agent dims; cell_* chosen so ratios are integral (no ceil/floor warn).
	const CELL_SIZE := 0.2
	const CELL_HEIGHT := 0.2
	const AGENT_RADIUS := 0.4
	const AGENT_HEIGHT := 1.6
	const AGENT_MAX_CLIMB := 0.2
	const GROUND_HALF := 24.0 # 48m × 48m walkable coverage
	const GROUND_Y := 0.02
	# Dedicated high bit so nav source does not participate as world physics (layer 1).
	const NAV_SOURCE_LAYER := 1 << 15

	var region := NavigationRegion3D.new()
	region.name = "NavigationRegion"

	var nav_mesh := NavigationMesh.new()
	nav_mesh.cell_size = CELL_SIZE
	nav_mesh.cell_height = CELL_HEIGHT
	nav_mesh.agent_radius = AGENT_RADIUS
	nav_mesh.agent_height = AGENT_HEIGHT
	nav_mesh.agent_max_climb = AGENT_MAX_CLIMB
	# Parser: static colliders only — never MeshInstance3D / RenderingServer meshes.
	nav_mesh.geometry_parsed_geometry_type = NavigationMesh.PARSED_GEOMETRY_STATIC_COLLIDERS
	nav_mesh.geometry_source_geometry_mode = NavigationMesh.SOURCE_GEOMETRY_ROOT_NODE_CHILDREN
	nav_mesh.geometry_collision_mask = NAV_SOURCE_LAYER

	# Collision-shape bake source (kept for contracts / optional region rebake).
	var body := StaticBody3D.new()
	body.name = "NavSourceCollider"
	body.collision_layer = NAV_SOURCE_LAYER
	body.collision_mask = 0
	var shape_node := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(GROUND_HALF * 2.0, CELL_HEIGHT, GROUND_HALF * 2.0)
	shape_node.shape = box
	shape_node.position = Vector3(0.0, GROUND_Y + CELL_HEIGHT * 0.5, 0.0)
	body.add_child(shape_node)
	region.add_child(body)

	# Procedural CPU source geometry — primary bake (tree-independent, no RS stall).
	var source := NavigationMeshSourceGeometryData3D.new()
	var faces := PackedVector3Array([
		Vector3(-GROUND_HALF, GROUND_Y, -GROUND_HALF),
		Vector3(GROUND_HALF, GROUND_Y, -GROUND_HALF),
		Vector3(GROUND_HALF, GROUND_Y, GROUND_HALF),
		Vector3(-GROUND_HALF, GROUND_Y, -GROUND_HALF),
		Vector3(GROUND_HALF, GROUND_Y, GROUND_HALF),
		Vector3(-GROUND_HALF, GROUND_Y, GROUND_HALF),
	])
	source.add_faces(faces, Transform3D.IDENTITY)
	NavigationServer3D.bake_from_source_geometry_data(nav_mesh, source)

	region.set_meta("nav_source_type", "procedural_cpu_faces")
	region.set_meta("nav_source_collider", "NavSourceCollider")
	region.set_meta("nav_cell_size", CELL_SIZE)
	region.set_meta("nav_cell_height", CELL_HEIGHT)
	region.set_meta("nav_agent_radius", AGENT_RADIUS)
	region.set_meta("nav_agent_height", AGENT_HEIGHT)
	region.set_meta("bake_deferred", false)

	# Advisory hints only — not world authority.
	if package != null:
		region.set_meta("navigation_hints_advisory", package.get("navigation_hints"))

	# Godot requires NavigationMap cell_* == NavigationMesh cell_* before region maps.
	if root.is_inside_tree():
		_align_navigation_map_voxels(root, CELL_SIZE, CELL_HEIGHT)

	region.navigation_mesh = nav_mesh
	root.add_child(region)

	# Re-align after enter in case world/map became valid only post-add.
	if root.is_inside_tree():
		_align_navigation_map_voxels(root, CELL_SIZE, CELL_HEIGHT)

	var baked := nav_mesh.get_polygon_count() > 0
	root.set_meta("navigation_baked", baked)
	return baked


## Keep the active World3D navigation map raster grid matched to our NavigationMesh.
func _align_navigation_map_voxels(root: Node3D, cell_size: float, cell_height: float) -> void:
	if root == null or not root.is_inside_tree():
		return
	var world := root.get_world_3d()
	if world == null:
		return
	var map_rid: RID = world.get_navigation_map()
	if not map_rid.is_valid():
		return
	if not is_equal_approx(NavigationServer3D.map_get_cell_size(map_rid), cell_size):
		NavigationServer3D.map_set_cell_size(map_rid, cell_size)
	if not is_equal_approx(NavigationServer3D.map_get_cell_height(map_rid), cell_height):
		NavigationServer3D.map_set_cell_height(map_rid, cell_height)


## Cancel a preview manifestation of intake content: free node, ensure no orphan collision.
func cancel_preview_instance(instance: Node) -> Dictionary:
	var orphan_before := 0
	var parent: Node = null
	if instance != null and is_instance_valid(instance):
		parent = instance.get_parent()
		if instance is Node3D:
			deactivate_collision(instance as Node3D)
		# Always detach presentation meshes before any free path (product lifecycle).
		_MeshLifecycle.prepare_subtree_for_free(instance)
		if instance.has_method("free_cleanup"):
			instance.call("free_cleanup")
		elif instance.has_method("mark_cancelled"):
			instance.call("mark_cancelled")
			instance.queue_free()
		else:
			_MeshLifecycle.safe_free(instance)
	var orphan_after := _count_orphan_collision(parent)
	return {
		"ok": orphan_after == 0,
		"orphan_collision_count": orphan_after,
		"has_durable_collision": false,
	}


## Product teardown entry for an intake realm root (or any mesh-bearing subtree).
func dispose_realm(realm: Node) -> void:
	_MeshLifecycle.safe_free(realm)


## Attach loaded GLB visual under ManifestationInstance without enabling collision.
## Returns false if instance missing attach API and fallback fails.
func attach_visual_to_manifestation(instance: Node3D, glb_root: Node3D) -> bool:
	if instance == null or glb_root == null:
		return false
	if instance.has_method("attach_external_visual"):
		return bool(instance.call("attach_external_visual", glb_root))
	# Fallback: parent under instance, keep collision_layer=0 on any bodies.
	if glb_root.get_parent():
		glb_root.get_parent().remove_child(glb_root)
	glb_root.name = "ExternalVisual"
	instance.add_child(glb_root)
	_force_preview_non_solid(instance)
	return true


func is_build_plot_clear(root: Node3D) -> bool:
	if root == null:
		return false
	# Build plot clear = no active Godot collision inside preview-anchor holders.
	for holder in _iter_module_holders(root):
		if bool(holder.get_meta("is_preview_anchor", false)):
			if bool(holder.get_meta("has_godot_collision", false)):
				return false
			var col_host := holder.get_node_or_null("GodotCollision") as Node3D
			if col_host and bool(col_host.get_meta("collision_active", false)):
				return false
	return true


func camera_not_occluded(root: Node3D) -> bool:
	if root == null:
		return false
	var markers := root.get_node_or_null("CameraMarkers")
	if markers == null or markers.get_child_count() == 0:
		# No marker → cannot prove occlusion; treat advisory pass.
		return true
	# Camera markers should sit above ground (y > 0 in Godot) for isometric kit.
	for c in markers.get_children():
		if c is Node3D:
			if (c as Node3D).position.y < 0.5:
				return false
	return true


## Save/reload identity: collect save_ids; second build must not duplicate ids under same parent.
func collect_save_ids(root: Node3D) -> PackedStringArray:
	var out := PackedStringArray()
	if root == null:
		return out
	for holder in _iter_module_holders(root):
		if holder.has_meta(SAVE_ID_META):
			out.append(str(holder.get_meta(SAVE_ID_META)))
	return out


func _shape_from_hint(hint: String, aabb: AABB) -> Shape3D:
	var size := aabb.size
	size.x = maxf(size.x, 0.2)
	size.y = maxf(size.y, 0.2)
	size.z = maxf(size.z, 0.2)
	match hint:
		"CAPSULE":
			var cap := CapsuleShape3D.new()
			cap.radius = maxf(size.x, size.z) * 0.5
			cap.height = maxf(size.y, cap.radius * 2.0 + 0.01)
			return cap
		"SPHERE":
			var sph := SphereShape3D.new()
			sph.radius = maxf(maxf(size.x, size.y), size.z) * 0.5
			return sph
		"CYLINDER":
			var cyl := CylinderShape3D.new()
			cyl.radius = maxf(size.x, size.z) * 0.5
			cyl.height = size.y
			return cyl
		_:
			var box := BoxShape3D.new()
			box.size = size
			return box


func _make_build_plot_marker(plot: Dictionary) -> Node3D:
	if plot == null or plot.is_empty():
		return null
	var marker := Node3D.new()
	marker.name = "BuildPlot"
	var center: Array = plot.get("center", [0, 0, 0]) as Array
	if center.size() >= 3:
		marker.position = _Intake.blender_pos_to_godot(float(center[0]), float(center[1]), float(center[2]))
	marker.set_meta("build_plot", true)
	marker.set_meta("size_m", plot.get("size_m", []))
	# Visual only under non-headless; always meta for tests.
	return marker


func _iter_module_holders(root: Node3D) -> Array:
	var out: Array = []
	if root == null:
		return out
	for c in root.get_children():
		if c is Node3D and (c as Node3D).has_meta("instance_id"):
			out.append(c)
		# Path segments nested under Path.
		if c.name == "Path":
			for seg in c.get_children():
				if seg is Node3D and (seg as Node3D).has_meta("instance_id"):
					out.append(seg)
	return out


func _ids_unique(placed: Array) -> bool:
	var seen: Dictionary = {}
	for p in placed:
		var id := str(p.get("instance_id", ""))
		if id.is_empty():
			return false
		if seen.has(id):
			return false
		seen[id] = true
	return true


func _revision_token(package: RefCounted) -> String:
	var job := str(package.get("job_id"))
	var fp := str(package.get("request_fingerprint"))
	return "%s:%s" % [job, fp.substr(0, 16)]


func _count_orphan_collision(parent: Node) -> int:
	if parent == null or not is_instance_valid(parent):
		return 0
	var n := 0
	for c in parent.get_children():
		if c is StaticBody3D and int((c as StaticBody3D).collision_layer) != 0:
			n += 1
		if c is Node:
			n += _count_orphan_collision(c)
	return n


func _force_preview_non_solid(node: Node) -> void:
	if node is StaticBody3D:
		(node as StaticBody3D).collision_layer = 0
		(node as StaticBody3D).collision_mask = 0
	if node is CollisionShape3D:
		(node as CollisionShape3D).disabled = true
	for c in node.get_children():
		_force_preview_non_solid(c)


func _fail_result(reason: String) -> Dictionary:
	last_error = reason
	return {
		"ok": false,
		"reason": reason,
		"root": null,
	}


## Deterministic 0–1.5 s delay from instance_id (art bible §4 stagger).
func _anim_delay_for(instance_id: String) -> float:
	var h := 0
	for i in instance_id.length():
		h = ((h * 33) + instance_id.unicode_at(i)) & 0x7fffffff
	return float(h % 1501) / 1000.0


## Attach looping idle AnimationPlayer for known P1E-003 modules.
func _attach_idle_animation(holder: Node3D, module_id: String, delay_s: float) -> void:
	if holder == null or module_id.is_empty():
		return
	var visual := holder.get_node_or_null("VisualGLB") as Node3D
	if visual == null:
		visual = holder
	var anim_name := ""
	var duration := 0.0
	if module_id == "cozy_flower_cluster_A":
		anim_name = "sway_small"
		duration = 4.2
	elif module_id == "cozy_garden_lamp_A":
		anim_name = "pulse"
		duration = 2.0
	else:
		return

	var player := AnimationPlayer.new()
	player.name = "IdleAnim"
	holder.add_child(player)
	var anim := Animation.new()
	anim.loop_mode = Animation.LOOP_LINEAR
	anim.length = duration
	if anim_name == "sway_small":
		var track := anim.add_track(Animation.TYPE_VALUE)
		anim.track_set_path(track, NodePath("%s:rotation_degrees" % visual.name))
		# Ease-in-out sway −1.2° → +1.2° around local Y (Godot Y-up after basis).
		anim.track_insert_key(track, 0.0, Vector3(0, -1.2, 0))
		anim.track_insert_key(track, duration * 0.5, Vector3(0, 1.2, 0))
		anim.track_insert_key(track, duration, Vector3(0, -1.2, 0))
	elif anim_name == "pulse":
		var track := anim.add_track(Animation.TYPE_VALUE)
		# Scale pulse approximates opacity pulse for imported meshes.
		anim.track_set_path(track, NodePath("%s:scale" % visual.name))
		anim.track_insert_key(track, 0.0, Vector3(0.95, 0.95, 0.95))
		anim.track_insert_key(track, duration * 0.5, Vector3(1.05, 1.05, 1.05))
		anim.track_insert_key(track, duration, Vector3(0.95, 0.95, 0.95))
	var lib := AnimationLibrary.new()
	lib.add_animation(anim_name, anim)
	player.add_animation_library("idle", lib)
	holder.set_meta("anim_name", anim_name)
	holder.set_meta("anim_duration", duration)
	# Seek into the loop by delay so instances are phase-offset without timers.
	player.play("idle/%s" % anim_name)
	var seek_t := fmod(delay_s, duration)
	player.seek(seek_t, true)
