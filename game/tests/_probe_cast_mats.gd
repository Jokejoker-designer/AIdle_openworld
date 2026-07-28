extends SceneTree
func _initialize() -> void:
	await process_frame
	var intake = load("res://scripts/modules/asset/glb_intake.gd").new()
	var path = ProjectSettings.globalize_path("res://assets/ucbv_001/character/nori7/export/nori7_rigged.glb")
	var node = intake.call("load_glb_absolute", path, "nori_probe") as Node3D
	if node == null:
		print("CAST_PROBE_FAIL ", intake.get("last_error"))
		quit(1)
		return
	get_root().add_child(node)
	await process_frame
	var count = 0
	_walk(node)
	print("CAST_PROBE_DONE meshes_seen=", count)
	quit(0)
var count := 0
func _walk(n: Node) -> void:
	if n is MeshInstance3D:
		var mi := n as MeshInstance3D
		count += 1
		var aabb := AABB()
		if mi.mesh:
			aabb = mi.mesh.get_aabb()
		print("MESH name=", mi.name, " mesh=", mi.mesh != null, " surfaces=", (mi.mesh.get_surface_count() if mi.mesh else 0), " aabb=", aabb, " scale=", mi.global_transform.basis.get_scale())
		if mi.mesh:
			for s in range(mi.mesh.get_surface_count()):
				var mat = mi.get_active_material(s)
				if mat == null and mi.mesh is ArrayMesh:
					mat = (mi.mesh as ArrayMesh).surface_get_material(s)
				if mat is StandardMaterial3D:
					var sm = mat as StandardMaterial3D
					print("  surf", s, " albedo=", sm.albedo_color, " name=", sm.resource_name)
				elif mat:
					print("  surf", s, " class=", mat.get_class())
				else:
					print("  surf", s, " NULL_MAT")
	for c in n.get_children():
		_walk(c)
