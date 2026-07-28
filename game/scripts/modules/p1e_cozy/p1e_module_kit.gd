## Loads promoted P1E cozy modules from game/assets/p1e_cozy/modules.
extends Node3D

const _GlbIntake = preload("res://scripts/modules/asset/glb_intake.gd")
const CATALOG := "res://resources/p1e_cozy/module_catalog.json"

var _instances: Array = []
var _last_report: Dictionary = {}


func get_report() -> Dictionary:
	return _last_report.duplicate(true)


func build_gallery(spacing: float = 2.2) -> Dictionary:
	_clear()
	var cat: Variant = _load_json(CATALOG)
	if cat == null or not (cat is Dictionary):
		_last_report = {"ok": false, "error": "catalog_missing"}
		return _last_report
	var modules: Array = cat.get("modules", []) as Array
	var intake: RefCounted = _GlbIntake.new()
	var loaded := 0
	var failed: Array = []
	var i := 0
	for m in modules:
		if not (m is Dictionary):
			continue
		var mid := str(m.get("module_id", "mod_%d" % i))
		var glb := str(m.get("glb", ""))
		var abs_path := ProjectSettings.globalize_path(glb) if glb.begins_with("res://") else glb
		if not FileAccess.file_exists(abs_path):
			failed.append({"id": mid, "error": "missing", "path": glb})
			i += 1
			continue
		var node: Node3D = intake.call("load_glb_absolute", abs_path, mid) as Node3D
		if node == null:
			failed.append({"id": mid, "error": "intake_failed"})
			i += 1
			continue
		node.name = mid
		node.position = Vector3(float(i) * spacing, 0.0, 0.0)
		# Hero scale for redesign target house (mockup card cozy_house_small_A).
		if mid == "cozy_house_small_A":
			node.scale = Vector3(1.35, 1.35, 1.35)
		add_child(node)
		_instances.append(node)
		loaded += 1
		i += 1
	# Showcase clone near gallery origin offset for playtest focus.
	var house_src: Node3D = null
	for n in _instances:
		if n is Node3D and str((n as Node3D).name) == "cozy_house_small_A":
			house_src = n as Node3D
			break
	if house_src != null:
		var show: Node3D = house_src.duplicate() as Node3D
		if show != null:
			show.name = "cozy_house_small_A_SHOWCASE"
			show.position = Vector3(-4.5, 0.0, 2.5)
			show.scale = Vector3(1.8, 1.8, 1.8)
			show.rotation_degrees = Vector3(0.0, 35.0, 0.0)
			add_child(show)
			_instances.append(show)
	_last_report = {
		"ok": failed.is_empty(),
		"loaded": loaded,
		"failed": failed,
		"total": modules.size(),
		"showcase": house_src != null,
	}
	return _last_report


func _clear() -> void:
	for n in _instances:
		if is_instance_valid(n):
			n.queue_free()
	_instances.clear()


func _load_json(path: String) -> Variant:
	if not FileAccess.file_exists(path):
		return null
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return null
	var t := f.get_as_text()
	f.close()
	return JSON.parse_string(t)
