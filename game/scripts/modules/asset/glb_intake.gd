## Runtime GLB intake from Bridge quarantine OS paths.
## Uses GLTFDocument + GLTFState only — never copies into res://.
## Imported collision nodes are stripped; Blender collision_hint is advisory only.
## Note: no class_name — headless -s may miss global class cache for new scripts.
extends RefCounted

const _Package = preload("res://scripts/modules/asset/glb_intake_package.gd")

## Physics layer bit for durable world geometry (project.godot layer 1).
const COLLISION_LAYER_WORLD := 1
## Manifestation solid layer (project.godot layer 3 → bit 4) — only after complete.
const COLLISION_LAYER_MANIFESTATION := 4

var last_error: String = ""
var last_load_report: Dictionary = {}


## Load a single GLB from absolute OS path. Returns root Node3D or null.
## Strips any imported CollisionObject3D / CollisionShape3D so collision is never
## activated at import time.
func load_glb_absolute(abs_path: String, instance_id: String = "") -> Node3D:
	last_error = ""
	last_load_report = {"path": abs_path, "instance_id": instance_id, "ok": false}
	if abs_path.is_empty():
		last_error = "empty_glb_path"
		return null
	var normalized := abs_path.replace("\\", "/")
	if not FileAccess.file_exists(normalized):
		last_error = "glb_missing:%s" % normalized
		return null

	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	var err: Error = doc.append_from_file(normalized, state)
	if err != OK:
		last_error = "gltf_append_failed:%d:%s" % [int(err), normalized]
		last_load_report["append_error"] = int(err)
		return null

	var scene: Node = doc.generate_scene(state)
	if scene == null:
		last_error = "gltf_generate_null:%s" % normalized
		return null

	var root: Node3D
	if scene is Node3D:
		root = scene as Node3D
	else:
		root = Node3D.new()
		root.name = instance_id if not instance_id.is_empty() else normalized.get_file().get_basename()
		root.add_child(scene)

	if not instance_id.is_empty():
		root.name = instance_id

	var stripped := _strip_imported_collision(root)
	var meshes := _collect_mesh_instances(root)
	var materials_ok := _materials_resolve(meshes)
	var sockets := _collect_socket_markers(root)

	root.set_meta("glb_source_path", normalized)
	root.set_meta("glb_instance_id", instance_id)
	root.set_meta("glb_intake", true)
	root.set_meta("imported_collision_stripped", stripped)
	root.set_meta("mesh_count", meshes.size())
	root.set_meta("materials_resolve", materials_ok)
	root.set_meta("socket_markers", sockets)
	# Ensure MAT_* names survive for STATE_VARIANTS / world-profile selector (WO-P1E-006).
	_stamp_material_names(root)
	# Cache surface materials/AABB, then detach GLTF meshes under headless dummy so
	# MeshInstance3D free never calls RS mesh_get_surface_count with a null handle.
	_cache_mesh_presentation_state(root)
	_release_dummy_unsafe_meshes(root)

	last_load_report = {
		"path": normalized,
		"instance_id": instance_id,
		"ok": true,
		"mesh_count": meshes.size(),
		"materials_resolve": materials_ok,
		"socket_markers": sockets,
		"collision_stripped": stripped,
		"runtime_load": "OK",
		"headless_mesh_released": _is_headless_dummy(),
	}
	return root


## Load every module GLB listed in a verified package. Does not parent or place them.
## Returns { ok, roots: {instance_id: Node3D}, errors: [], reports: [] }.
func load_package_modules(package: RefCounted) -> Dictionary:
	last_error = ""
	var roots: Dictionary = {}
	var errors: Array = []
	var reports: Array = []
	if package == null or not package.has_method("is_ready") or not bool(package.call("is_ready")):
		last_error = "package_not_ready"
		return {"ok": false, "roots": roots, "errors": [last_error], "reports": reports}

	var mods: Array = package.get("modules") as Array
	for m in mods:
		if not (m is Dictionary):
			errors.append("bad_module_entry")
			continue
		var entry: Dictionary = m
		var iid := str(entry.get("instance_id", ""))
		var abs_path := str(package.call("module_abs_path", entry))
		# Prefer per-module sha from manifest when present.
		var expected := str(entry.get("artifact_sha256", "")).to_lower()
		if not expected.is_empty():
			var actual := _Package.sha256_file(abs_path)
			if actual != expected:
				var msg := "module_sha_mismatch:%s" % iid
				errors.append(msg)
				reports.append({"instance_id": iid, "ok": false, "reason": msg, "expected": expected, "actual": actual})
				continue
		var node := load_glb_absolute(abs_path, iid)
		if node == null:
			errors.append("%s:%s" % [iid, last_error])
			reports.append(last_load_report.duplicate(true))
			continue
		node.set_meta("module_id", str(entry.get("module_id", "")))
		node.set_meta("content_phase", str(entry.get("content_phase", "")))
		node.set_meta("manifestation_order", int(entry.get("manifestation_order", 0)))
		node.set_meta("artifact_sha256", expected)
		roots[iid] = node
		reports.append(last_load_report.duplicate(true))

	var ok := errors.is_empty() and roots.size() == mods.size()
	if not ok and last_error.is_empty():
		last_error = "partial_module_load"
	return {"ok": ok, "roots": roots, "errors": errors, "reports": reports, "count": roots.size()}


## Blender Z-up meters → Godot Y-up: (x, y, z)_b → (x, z, -y)_g
static func blender_pos_to_godot(bx: float, by: float, bz: float) -> Vector3:
	return Vector3(bx, bz, -by)


## Apply Blender 4x4 row-major transform (16 floats) onto a Node3D in Godot space.
static func apply_blender_transform(node: Node3D, flat16: Array) -> void:
	if node == null or flat16 == null or flat16.size() < 16:
		return
	# Blender matrix rows; translation in last row (m30,m31,m32).
	var bx := float(flat16[12])
	var by := float(flat16[13])
	var bz := float(flat16[14])
	node.position = blender_pos_to_godot(bx, by, bz)

	# Basis columns from upper-left 3x3 (row-major storage).
	var b00 := float(flat16[0])
	var b01 := float(flat16[1])
	var b02 := float(flat16[2])
	var b10 := float(flat16[4])
	var b11 := float(flat16[5])
	var b12 := float(flat16[6])
	var b20 := float(flat16[8])
	var b21 := float(flat16[9])
	var b22 := float(flat16[10])
	# Map Blender basis axes into Godot: X' = X, Y' = Z, Z' = -Y
	# Godot basis column 0 (local X) = map(Blender col0 = (b00,b10,b20))
	var col0 := Vector3(b00, b20, -b10)
	var col1 := Vector3(b02, b22, -b12)  # Blender Z → Godot Y
	var col2 := Vector3(-b01, -b21, b11)  # Blender -Y → Godot Z
	# Orthonormalize gently if needed.
	if col0.length_squared() < 1e-8:
		col0 = Vector3.RIGHT
	if col1.length_squared() < 1e-8:
		col1 = Vector3.UP
	if col2.length_squared() < 1e-8:
		col2 = Vector3.BACK
	node.basis = Basis(col0.normalized(), col1.normalized(), col2.normalized())


## Axis-aligned bounds of all MeshInstance3D under node (local space of `node`).
## Always uses relative transforms — safe before entering the SceneTree.
## Under headless, meshes may be released; prefer cached intake_local_aabb meta.
static func compute_local_aabb(node: Node3D) -> AABB:
	var empty := true
	var acc := AABB()
	for mi in _collect_mesh_instances(node):
		var local_aabb := AABB()
		if mi.mesh != null:
			local_aabb = mi.mesh.get_aabb()
		elif mi.has_meta("intake_local_aabb"):
			local_aabb = mi.get_meta("intake_local_aabb") as AABB
		else:
			continue
		var xf: Transform3D = _relative_transform(node, mi)
		var corners := _aabb_corners(local_aabb)
		for c in corners:
			var p: Vector3 = xf * c
			if empty:
				acc = AABB(p, Vector3.ZERO)
				empty = false
			else:
				acc = acc.expand(p)
	if empty:
		return AABB(Vector3(-0.5, 0, -0.5), Vector3(1, 1, 1))
	return acc


static func _relative_transform(ancestor: Node, descendant: Node) -> Transform3D:
	var xform := Transform3D.IDENTITY
	var n: Node = descendant
	var guard := 0
	while n != null and n != ancestor and guard < 64:
		if n is Node3D:
			xform = (n as Node3D).transform * xform
		n = n.get_parent()
		guard += 1
	return xform


static func _aabb_corners(a: AABB) -> Array:
	var p := a.position
	var e := a.end
	return [
		Vector3(p.x, p.y, p.z),
		Vector3(e.x, p.y, p.z),
		Vector3(p.x, e.y, p.z),
		Vector3(e.x, e.y, p.z),
		Vector3(p.x, p.y, e.z),
		Vector3(e.x, p.y, e.z),
		Vector3(p.x, e.y, e.z),
		Vector3(e.x, e.y, e.z),
	]


static func _strip_imported_collision(root: Node) -> int:
	var removed := 0
	var to_free: Array = []
	_walk_collect_collision(root, to_free)
	for n in to_free:
		if n is Node and is_instance_valid(n):
			var parent: Node = (n as Node).get_parent()
			if parent:
				parent.remove_child(n)
			(n as Node).free()
			removed += 1
	return removed


static func _walk_collect_collision(n: Node, out: Array) -> void:
	if n is CollisionObject3D or n is CollisionShape3D:
		out.append(n)
	for c in n.get_children():
		_walk_collect_collision(c, out)


static func _collect_mesh_instances(root: Node) -> Array:
	var out: Array = []
	_walk_meshes(root, out)
	return out


static func _walk_meshes(n: Node, out: Array) -> void:
	if n is MeshInstance3D:
		out.append(n)
	for c in n.get_children():
		_walk_meshes(c, out)


static func _stamp_material_names(root: Node) -> void:
	## GLTF materials often have empty resource_name; stamp from known MAT_ prefix if present.
	for mi in _collect_mesh_instances(root):
		if mi.material_override != null:
			_stamp_one(mi.material_override)
		var surfaces: int = _safe_surface_count(mi)
		for s in range(surfaces):
			var surf: Material = _surface_material_at(mi, s)
			if surf != null:
				_stamp_one(surf)


static func _stamp_one(mat: Material) -> void:
	if mat == null:
		return
	var nm := str(mat.resource_name)
	if not nm.is_empty():
		return
	# Some importers put name only in to_string(); keep empty — selector uses cache.


static func _materials_resolve(meshes: Array) -> bool:
	## Presence gate only. Color integrity is enforced by p1e004 material check
	## (GLB baseColorFactor + rendered ROI). Do NOT treat bare geometry / default
	## white as pass — that hid pure-white pond failure after emission wash.
	if meshes.is_empty():
		return false
	for mi in meshes:
		var m: MeshInstance3D = mi
		if m.material_override != null:
			continue
		if m.mesh == null and not m.has_meta("intake_surface_materials"):
			return false
		var surfaces: int = _safe_surface_count(m)
		if surfaces <= 0 and m.mesh == null:
			return false
		if surfaces <= 0:
			return false
		var any_mat := false
		for s in range(surfaces):
			if _surface_material_at(m, s) != null:
				any_mat = true
				break
		if not any_mat:
			return false
	return true


## Resource-side surface count — never call Mesh.get_surface_count() on types that
## may route through RenderingServer dummy mesh_storage (Parameter "m" is null).
static func _safe_mesh_surface_count(mesh: Mesh) -> int:
	if mesh == null:
		return 0
	if mesh is ArrayMesh:
		return (mesh as ArrayMesh).get_surface_count()
	if mesh is PrimitiveMesh:
		return 1
	return 0


static func _safe_surface_count(mi: MeshInstance3D) -> int:
	if mi == null:
		return 0
	if mi.has_meta("intake_surface_count"):
		return int(mi.get_meta("intake_surface_count"))
	if mi.has_meta("intake_surface_materials"):
		return (mi.get_meta("intake_surface_materials") as Array).size()
	var soc: int = mi.get_surface_override_material_count()
	if soc > 0:
		return soc
	return _safe_mesh_surface_count(mi.mesh)


static func _surface_material_at(mi: MeshInstance3D, s: int) -> Material:
	if mi == null or s < 0:
		return null
	# Prefer meta cache — never call get_active_material after headless mesh clear
	# (RS instance materials size 0 → ERROR spam).
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


## Snapshot surface materials + local AABB onto each MeshInstance3D so presentation
## logic can run after headless mesh clear without RS surface queries on GLTF RIDs.
static func _cache_mesh_presentation_state(root: Node) -> void:
	for mi in _collect_mesh_instances(root):
		if mi == null or not is_instance_valid(mi):
			continue
		var surfaces: Array = []
		var count := 0
		if mi.mesh != null:
			count = _safe_mesh_surface_count(mi.mesh)
			mi.set_meta("intake_local_aabb", mi.mesh.get_aabb())
			for s in range(count):
				var surf: Material = null
				# Resource-side only — avoid get_active_material (RS instance path).
				if s < mi.get_surface_override_material_count():
					surf = mi.get_surface_override_material(s)
				if surf == null and mi.mesh is ArrayMesh:
					surf = (mi.mesh as ArrayMesh).surface_get_material(s)
				surfaces.append(surf)
		else:
			count = mi.get_surface_override_material_count()
			for s in range(count):
				surfaces.append(mi.get_surface_override_material(s))
		if mi.material_override != null:
			mi.set_meta("intake_has_material_override", true)
		mi.set_meta("intake_surface_materials", surfaces)
		mi.set_meta("intake_surface_count", count if count > 0 else surfaces.size())


## GLTF MeshInstance3D free under dummy renderer errors (mesh_get_surface_count m=null).
## Headless only: promote cached materials onto material_override when needed, then
## clear mi.mesh BEFORE free. Clearing mesh is the only free-safe path; do not leave
## GLTF ArrayMesh attached, and do not rely on surface_override after mesh=null
## (Godot resizes surface_override_materials to 0 when mesh is cleared).
static func _release_dummy_unsafe_meshes(root: Node) -> void:
	if not _is_headless_dummy():
		return
	for mi in _collect_mesh_instances(root):
		if mi == null or not is_instance_valid(mi):
			continue
		if mi.mesh == null:
			continue
		var mats: Array = []
		if mi.has_meta("intake_surface_materials"):
			mats = mi.get_meta("intake_surface_materials") as Array
		# material_override survives mesh=null; surface_override slots do not.
		if mi.material_override == null and mats.size() >= 1 and mats[0] != null:
			# Single- or multi-surface: keep first as override for simple readers;
			# full per-surface list remains in intake_surface_materials meta.
			if mats.size() == 1:
				mi.material_override = mats[0] as Material
		mi.mesh = null
		mi.set_meta("intake_headless_mesh_cleared", true)


static func _is_headless_dummy() -> bool:
	if OS.has_feature("headless"):
		return true
	if DisplayServer.get_name() == "headless":
		return true
	return false


static func _collect_socket_markers(root: Node) -> PackedStringArray:
	var out := PackedStringArray()
	_walk_sockets(root, out)
	return out


static func _walk_sockets(n: Node, out: PackedStringArray) -> void:
	var nm := String(n.name).to_upper()
	if nm.begins_with("SOCKET") or nm.begins_with("SNAP") or nm.begins_with("MARKER_SOCKET"):
		out.append(String(n.name))
	if n.has_meta("socket") or n.has_meta("socket_id"):
		out.append(String(n.name))
	for c in n.get_children():
		_walk_sockets(c, out)
