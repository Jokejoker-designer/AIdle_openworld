## Product-owned headless-safe mesh presentation lifecycle.
## Under Godot 4.3 --headless dummy renderer, freeing a MeshInstance3D that still
## holds a presentation mesh (GLTF ArrayMesh, PlaneMesh, BoxMesh, …) triggers
## ERROR Parameter "m" is null at mesh_get_surface_count (mesh_storage.h).
## Production teardown/rebuild must detach presentation meshes BEFORE free/queue_free.
## Note: no class_name — headless -s may miss global class cache for new scripts.
extends RefCounted

const META_SURFACE_MATERIALS := "intake_surface_materials"
const META_SURFACE_COUNT := "intake_surface_count"
const META_HEADLESS_CLEARED := "intake_headless_mesh_cleared"
const META_HAS_OVERRIDE := "intake_has_material_override"
const META_LOCAL_AABB := "intake_local_aabb"


static func is_headless_dummy() -> bool:
	if OS.has_feature("headless"):
		return true
	if DisplayServer.get_name() == "headless":
		return true
	return false


## Walk subtree; for every MeshInstance3D with a non-null mesh, cache materials
## (if not already) and set mi.mesh = null. Safe on headed and headless.
## Returns number of meshes detached.
static func detach_presentation_meshes(root: Node) -> int:
	if root == null or not is_instance_valid(root):
		return 0
	var n := 0
	for mi in _collect_mesh_instances(root):
		if mi == null or not is_instance_valid(mi):
			continue
		if mi.mesh == null:
			continue
		_cache_if_needed(mi)
		# material_override survives mesh=null; surface_override slots do not.
		if mi.material_override == null and mi.has_meta(META_SURFACE_MATERIALS):
			var mats: Array = mi.get_meta(META_SURFACE_MATERIALS) as Array
			if mats.size() == 1 and mats[0] != null:
				mi.material_override = mats[0] as Material
		mi.mesh = null
		mi.set_meta(META_HEADLESS_CLEARED, true)
		n += 1
	return n


## Alias used by rebuild/teardown call sites — always detach before free.
static func prepare_subtree_for_free(root: Node) -> int:
	return detach_presentation_meshes(root)


## Detach presentation meshes under headless only (live trees remain free-safe
## when tests/callers free via Node.free/queue_free without this helper).
## On headed presentation, leaves meshes attached for rendering.
static func ensure_headless_free_safe(root: Node) -> int:
	if not is_headless_dummy():
		return 0
	return detach_presentation_meshes(root)


## Prepare then free immediately (product rebuild / cancel path).
static func safe_free(node: Node) -> void:
	if node == null or not is_instance_valid(node):
		return
	prepare_subtree_for_free(node)
	var p: Node = node.get_parent()
	if p != null:
		p.remove_child(node)
	node.free()


## Prepare then queue_free (deferred teardown).
static func safe_queue_free(node: Node) -> void:
	if node == null or not is_instance_valid(node):
		return
	prepare_subtree_for_free(node)
	node.queue_free()


static func _cache_if_needed(mi: MeshInstance3D) -> void:
	if mi == null or mi.mesh == null:
		return
	if not mi.has_meta(META_LOCAL_AABB):
		mi.set_meta(META_LOCAL_AABB, mi.mesh.get_aabb())
	if mi.material_override != null:
		mi.set_meta(META_HAS_OVERRIDE, true)
	if mi.has_meta(META_SURFACE_MATERIALS):
		return
	var surfaces: Array = []
	var count := 0
	if mi.mesh is ArrayMesh:
		count = (mi.mesh as ArrayMesh).get_surface_count()
	elif mi.mesh is PrimitiveMesh:
		count = 1
	else:
		# Avoid RS surface queries on unknown mesh types under dummy.
		count = mi.get_surface_override_material_count()
	for s in range(max(count, 0)):
		var surf: Material = null
		if s < mi.get_surface_override_material_count():
			surf = mi.get_surface_override_material(s)
		if surf == null and mi.mesh is ArrayMesh:
			surf = (mi.mesh as ArrayMesh).surface_get_material(s)
		if surf == null and mi.material_override != null and s == 0:
			surf = mi.material_override
		surfaces.append(surf)
	mi.set_meta(META_SURFACE_MATERIALS, surfaces)
	mi.set_meta(META_SURFACE_COUNT, surfaces.size())


static func _collect_mesh_instances(root: Node) -> Array:
	var out: Array = []
	_walk_meshes(root, out)
	return out


static func _walk_meshes(n: Node, out: Array) -> void:
	if n is MeshInstance3D:
		out.append(n)
	for c in n.get_children():
		_walk_meshes(c, out)
