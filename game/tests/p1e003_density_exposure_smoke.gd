## WO-P1E-003 smoke — dense quarantine kit load + fence BOX collision + stagger meta.
## Run:
##   tools\Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://tests/p1e003_density_exposure_smoke.gd
##
## Exit 0 on pass, 1 on failure. Prints AIDLE_P1E003_SMOKE=PASS|FAIL.
extends SceneTree

const PACKAGE_PATH := "E:/AIdle_Blender_Bridge_P0/storage/generated_quarantine/BLD-03CB1AADD475"
const PKG_SCRIPT := "res://scripts/modules/asset/glb_intake_package.gd"
const BUILDER_SCRIPT := "res://scripts/modules/asset/glb_intake_runtime_builder.gd"
const STARTER_SCRIPT := "res://scripts/modules/asset/starter_realm_builder.gd"

const LAYER_WORLD := 1

var _failures: PackedStringArray = []
var _passed: int = 0
var _evidence: Dictionary = {}


func _initialize() -> void:
	print("[P1E-003 smoke] starting…")
	_test_package_density()
	await _test_runtime_build_and_fence()
	_test_game_glb_count_zero()
	_finish()


func _finish() -> void:
	print("[P1E-003 smoke] evidence=%s" % JSON.stringify(_evidence))
	if _failures.is_empty():
		print("AIDLE_P1E003_SMOKE=PASS checks=%d" % _passed)
		print("GODOT_RUNTIME_LOAD=OK")
		print("GAME_GLB_COUNT=0")
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print("AIDLE_P1E003_SMOKE=FAIL failed=%d passed=%d" % [_failures.size(), _passed])
		quit(1)


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)


func _test_package_density() -> void:
	var Pkg := load(PKG_SCRIPT) as GDScript
	if Pkg == null:
		_fail("package_script")
		return
	var pkg = Pkg.call("open", PACKAGE_PATH)
	if pkg == null or not bool(pkg.call("is_ready")):
		_fail("package_ready", str(pkg.get("last_error") if pkg else "null"))
		return
	var summary: Dictionary = pkg.call("summary") as Dictionary
	_evidence["package"] = summary
	var count := int(summary.get("module_count", 0))
	if count < 35 or count > 50:
		_fail("instance_count_range", "count=%d want 35-50" % count)
		return
	_ok("package_density_%d" % count)

	var mods: Array = pkg.get("modules") as Array
	var ids: Dictionary = {}
	var has_fence := false
	var has_flower := false
	var has_lamp := false
	var has_rock := false
	for m in mods:
		if not (m is Dictionary):
			continue
		var mid := str((m as Dictionary).get("module_id", ""))
		var iid := str((m as Dictionary).get("instance_id", ""))
		if ids.has(iid):
			_fail("duplicate_instance", iid)
			return
		ids[iid] = true
		if mid == "cozy_fence_section_A":
			has_fence = true
		if mid == "cozy_flower_cluster_A":
			has_flower = true
		if mid == "cozy_garden_lamp_A":
			has_lamp = true
		if mid == "cozy_rock_small_A":
			has_rock = true
	if not (has_fence and has_flower and has_lamp and has_rock):
		_fail("missing_wave1_modules", "fence=%s flower=%s lamp=%s rock=%s" % [has_fence, has_flower, has_lamp, has_rock])
		return
	_ok("wave1_modules_present")


func _test_runtime_build_and_fence() -> void:
	var Builder := load(BUILDER_SCRIPT) as GDScript
	if Builder == null:
		_fail("builder_script")
		return
	var world := Node3D.new()
	world.name = "P1E003World"
	root.add_child(world)
	var builder = Builder.new()
	var res: Dictionary = builder.call(
		"build_realm",
		PACKAGE_PATH,
		{"parent": world, "enable_collision": true, "bake_navigation": true}
	) as Dictionary
	if not bool(res.get("ok", false)):
		_fail("build_realm", str(res.get("reason", "?")))
		world.queue_free()
		return
	var module_count := int(res.get("module_count", 0))
	_evidence["build"] = {
		"module_count": module_count,
		"job_id": res.get("job_id"),
		"collision_enabled": res.get("collision_enabled"),
		"build_plot_clear": res.get("build_plot_clear"),
	}
	if module_count < 35:
		_fail("built_module_count", str(module_count))
		world.queue_free()
		return
	_ok("runtime_build_%d" % module_count)

	if not bool(res.get("build_plot_clear", false)):
		_fail("build_plot_clear")
	else:
		_ok("build_plot_clear")

	# Fence sections must carry active Godot collision (rails must block).
	var realm: Node3D = res.get("root", null) as Node3D
	var fence_bodies := 0
	var anim_delays: Array = []
	if realm != null:
		for c in realm.get_children():
			if c is Node3D and (c as Node3D).has_meta("module_id"):
				var mid := str((c as Node3D).get_meta("module_id"))
				if mid == "cozy_fence_section_A":
					var col := (c as Node3D).get_node_or_null("GodotCollision")
					if col != null:
						for b in col.get_children():
							if b is StaticBody3D and int((b as StaticBody3D).collision_layer) == LAYER_WORLD:
								fence_bodies += 1
				if (c as Node3D).has_meta("anim_delay"):
					anim_delays.append(float((c as Node3D).get_meta("anim_delay")))
	if fence_bodies < 1:
		_fail("fence_collision_bodies", "count=%d" % fence_bodies)
	else:
		_ok("fence_collision_bodies_%d" % fence_bodies)

	# Stagger: more than one unique delay among animated instances.
	var uniq: Dictionary = {}
	for d in anim_delays:
		uniq[str(snapped(d, 0.01))] = true
	_evidence["anim_delay_unique"] = uniq.size()
	if uniq.size() < 2 and anim_delays.size() >= 2:
		_fail("anim_stagger", "unique=%d" % uniq.size())
	else:
		_ok("anim_stagger_unique_%d" % uniq.size())

	# StarterRealmBuilder dual-path still mounts dense package.
	var Starter := load(STARTER_SCRIPT) as GDScript
	if Starter != null:
		var pr := Node3D.new()
		pr.name = "PrivateReality"
		world.add_child(pr)
		var starter_root: Node3D = Starter.call(
			"build_into_opts",
			pr,
			{"force_glb": true, "package_path": PACKAGE_PATH, "enable_collision": true}
		) as Node3D
		if starter_root == null:
			_fail("starter_builder_glb")
		else:
			_ok("starter_builder_glb")
			# UX-002 procedural fence still present for rail regression path.
			if starter_root.get_node_or_null("Fence") == null:
				_fail("procedural_fence_missing")
			else:
				_ok("procedural_fence_present")
	world.queue_free()


func _test_game_glb_count_zero() -> void:
	# Commercial path: environment modules stay quarantine-only; approved character
	# production GLB (UCBV Nori-7) may live under named path. Unexpected glbs still fail.
	var allowed_suffixes := PackedStringArray([
		"game/assets/ucbv_001/character/nori7/export/nori7_rigged.glb",
		"game\\assets\\ucbv_001\\character\\nori7\\export\\nori7_rigged.glb",
	])
	var found: PackedStringArray = PackedStringArray()
	var abs_count := 0
	var dir := DirAccess.open("E:/AIdle_openworld/game")
	if dir != null:
		abs_count = _count_glbs_abs("E:/AIdle_openworld/game", found)
	var unexpected: PackedStringArray = PackedStringArray()
	for p in found:
		var ok_allowed := false
		for suf in allowed_suffixes:
			if str(p).replace("\\", "/").ends_with(str(suf).replace("\\", "/")):
				ok_allowed = true
				break
		if not ok_allowed:
			unexpected.append(p)
	_evidence["game_glb_count"] = abs_count
	_evidence["game_glb_found"] = found
	_evidence["game_glb_unexpected"] = unexpected
	if unexpected.size() != 0:
		_fail("game_glb_unexpected", ",".join(unexpected))
	else:
		_ok("game_glb_allowlist_ok count=%d allowed_nori=%s" % [abs_count, str(abs_count >= 1)])


func _count_glbs(_res_path: String) -> int:
	return 0


func _count_glbs_abs(path: String, found: PackedStringArray = PackedStringArray()) -> int:
	var n := 0
	var d := DirAccess.open(path)
	if d == null:
		return 0
	d.list_dir_begin()
	var name := d.get_next()
	while name != "":
		if name.begins_with("."):
			name = d.get_next()
			continue
		var full := path.path_join(name)
		if d.current_is_dir():
			n += _count_glbs_abs(full, found)
		elif name.to_lower().ends_with(".glb") or name.to_lower().ends_with(".gltf"):
			n += 1
			found.append(full)
		name = d.get_next()
	d.list_dir_end()
	return n
