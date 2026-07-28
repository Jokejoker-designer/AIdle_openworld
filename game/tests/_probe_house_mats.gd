extends SceneTree
func _init():
	var intake = load("res://scripts/modules/asset/glb_intake.gd").new()
	var path = ProjectSettings.globalize_path("res://assets/p1e_cozy/modules/cozy_house_small_A.glb")
	var node = intake.call("load_glb_absolute", path, "house_probe")
	if node == null:
		print("PROBE_FAIL ", intake.last_error)
		quit(1)
		return
	var n = 0
	_walk(node, n)
	print("PROBE_DONE")
	quit(0)
func _walk(n: Node, depth: int) -> void:
	if n is MeshInstance3D:
		var mi := n as MeshInstance3D
		if mi.mesh != null:
			for s in range(mi.mesh.get_surface_count()):
				var mat = mi.get_active_material(s)
				if mat == null:
					mat = mi.mesh.surface_get_material(s)
				if mat is StandardMaterial3D:
					var sm := mat as StandardMaterial3D
					print("MAT ", mi.name, " albedo=", sm.albedo_color, " emit=", sm.emission, " emit_en=", sm.emission_enabled)
				elif mat != null:
					print("MAT ", mi.name, " type=", mat.get_class(), " ", mat.resource_name)
				else:
					print("MAT ", mi.name, " NULL")
				break
	for c in n.get_children():
		_walk(c, depth+1)
