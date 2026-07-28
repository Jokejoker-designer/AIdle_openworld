## WO-P1E-002 — twelve intake tests from 06_GODOT_INTAKE_AND_RUNTIME_BOUNDARY.md
## Run:
##   tools\Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://tests/p1e002_glb_intake_tests.gd
##
## Exit 0 on pass, 1 on failure. Prints AIDLE_P1E002_TESTS=PASS|FAIL.
extends SceneTree

const PACKAGE_PATH := "E:/AIdle_Blender_Bridge_P0/storage/generated_quarantine/BLD-E6BCC14D117E"
const PKG_SCRIPT := "res://scripts/modules/asset/glb_intake_package.gd"
const INTAKE_SCRIPT := "res://scripts/modules/asset/glb_intake.gd"
const BUILDER_SCRIPT := "res://scripts/modules/asset/glb_intake_runtime_builder.gd"
const MANIFEST_INSTANCE := "res://scripts/modules/manifestation/manifestation_instance.gd"
const STARTER_BUILDER := "res://scripts/modules/asset/starter_realm_builder.gd"

var _failures: PackedStringArray = []
var _passed: int = 0
var _evidence: Dictionary = {}
var _Pkg: GDScript
var _Intake: GDScript
var _Builder: GDScript
var _Instance: GDScript


func _initialize() -> void:
	print("[P1E-002 tests] starting…")
	_Pkg = load(PKG_SCRIPT) as GDScript
	_Intake = load(INTAKE_SCRIPT) as GDScript
	_Builder = load(BUILDER_SCRIPT) as GDScript
	_Instance = load(MANIFEST_INSTANCE) as GDScript
	if _Pkg == null or _Intake == null or _Builder == null:
		_fail("load_scripts", "pkg/intake/builder")
		_finish()
		return

	await _test_01_all_glb_import()
	_test_02_object_ids_unique()
	_test_03_scene_origin_correct()
	_test_04_material_slots_resolve()
	_test_05_socket_markers_resolve()
	await _test_06_collision_hint_not_authoritative_before_commit()
	await _test_07_navigation_bake_succeeds()
	await _test_08_build_plot_clear()
	await _test_09_camera_not_occluded()
	await _test_10_cancel_hologram_no_orphan()
	await _test_11_save_reload_no_duplicate()
	_test_12_revision_conflict_surfaces()
	_test_tampered_package_refused()
	_test_runtime_load_flag()

	_finish()


func _finish() -> void:
	print("[P1E-002 tests] evidence=%s" % JSON.stringify(_evidence))
	if _failures.is_empty():
		print("AIDLE_P1E002_TESTS=PASS checks=%d" % _passed)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print("AIDLE_P1E002_TESTS=FAIL failed=%d passed=%d" % [_failures.size(), _passed])
		quit(1)


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)


func _open_pkg():
	return _Pkg.call("open", PACKAGE_PATH)


func _test_01_all_glb_import() -> void:
	var pkg = _open_pkg()
	if pkg == null or not bool(pkg.call("is_ready")):
		_fail("all_glb_import", "package not ready: %s" % str(pkg.get("last_error") if pkg else "null"))
		return
	var intake = _Intake.new()
	var res: Dictionary = intake.call("load_package_modules", pkg) as Dictionary
	_evidence["import"] = {
		"ok": res.get("ok"),
		"count": res.get("count"),
		"errors": res.get("errors"),
	}
	if not bool(res.get("ok", false)):
		_fail("all_glb_import", str(res.get("errors")))
		return
	var roots: Dictionary = res.get("roots", {})
	if roots.size() < 7:
		_fail("all_glb_import", "expected>=7 got=%d" % roots.size())
		# free loaded
		for k in roots.keys():
			var n: Node = roots[k]
			if n:
				_dispose_node(n)
		return
	for k in roots.keys():
		var n: Node = roots[k]
		if n:
			_dispose_node(n)
	_ok("all_glb_import")
	await process_frame


func _test_02_object_ids_unique() -> void:
	var builder = _Builder.new()
	var res: Dictionary = builder.call("build_realm", PACKAGE_PATH, {"enable_collision": false, "bake_navigation": false}) as Dictionary
	if not bool(res.get("ok", false)):
		_fail("object_ids_unique", str(res.get("reason")))
		return
	if not bool(res.get("ids_unique", false)):
		_fail("object_ids_unique", "duplicate ids")
		_free_root(res)
		return
	var placed: Array = res.get("placed", []) as Array
	var seen: Dictionary = {}
	for p in placed:
		var id := str(p.get("instance_id", ""))
		if seen.has(id):
			_fail("object_ids_unique", id)
			_free_root(res)
			return
		seen[id] = true
	_evidence["ids"] = seen.keys()
	_ok("object_ids_unique")
	_free_root(res)


func _test_03_scene_origin_correct() -> void:
	var builder = _Builder.new()
	var res: Dictionary = builder.call("build_realm", PACKAGE_PATH, {"enable_collision": false, "bake_navigation": false}) as Dictionary
	if not bool(res.get("ok", false)):
		_fail("scene_origin_correct", str(res.get("reason")))
		return
	var root: Node3D = res.get("root") as Node3D
	var origin := root.get_node_or_null("SceneOrigin") as Node3D
	if origin == null:
		_fail("scene_origin_correct", "missing SceneOrigin")
		_free_root(res)
		return
	if origin.position != Vector3.ZERO:
		_fail("scene_origin_correct", str(origin.position))
		_free_root(res)
		return
	# House should not sit on origin if kit transform is non-zero.
	var house := root.get_node_or_null("House") as Node3D
	if house != null and house.position.is_equal_approx(Vector3.ZERO):
		_fail("scene_origin_correct", "house unexpectedly at origin")
		_free_root(res)
		return
	_ok("scene_origin_correct")
	_free_root(res)


func _test_04_material_slots_resolve() -> void:
	var builder = _Builder.new()
	var res: Dictionary = builder.call("build_realm", PACKAGE_PATH, {"enable_collision": false, "bake_navigation": false}) as Dictionary
	if not bool(res.get("ok", false)):
		_fail("material_slots_resolve", str(res.get("reason")))
		return
	if not bool(res.get("materials_resolve", false)):
		_fail("material_slots_resolve", "materials_resolve=false")
		_free_root(res)
		return
	_ok("material_slots_resolve")
	_free_root(res)


func _test_05_socket_markers_resolve() -> void:
	# Resolution path always runs; empty sockets is valid for this kit wave.
	var builder = _Builder.new()
	var res: Dictionary = builder.call("build_realm", PACKAGE_PATH, {"enable_collision": false, "bake_navigation": false}) as Dictionary
	if not bool(res.get("ok", false)):
		_fail("socket_markers_resolve", str(res.get("reason")))
		return
	if not bool(res.get("socket_markers_resolved", false)):
		_fail("socket_markers_resolve", "resolver failed")
		_free_root(res)
		return
	_evidence["sockets_note"] = "optional on P1E kit; resolver executed"
	_ok("socket_markers_resolve")
	_free_root(res)


func _test_06_collision_hint_not_authoritative_before_commit() -> void:
	var builder = _Builder.new()
	var res: Dictionary = builder.call(
		"build_realm",
		PACKAGE_PATH,
		{"enable_collision": false, "bake_navigation": false}
	) as Dictionary
	if not bool(res.get("ok", false)):
		_fail("collision_hint_not_authoritative", str(res.get("reason")))
		return
	var root: Node3D = res.get("root") as Node3D
	var solid := _count_solid_static(root)
	_evidence["collision_before_commit"] = solid
	if solid != 0:
		_fail("collision_hint_not_authoritative", "solid_bodies=%d before commit" % solid)
		_free_root(res)
		return
	# After explicit activate (confirm path), Godot-owned collision appears.
	var activated: int = int(builder.call("activate_collision", root, null, 1))
	var solid_after := _count_solid_static(root)
	_evidence["collision_after_confirm"] = {"activated": activated, "solid": solid_after}
	if activated <= 0 or solid_after <= 0:
		_fail("collision_hint_not_authoritative", "activate produced no solid collision")
		_free_root(res)
		return
	# Preview anchor greenhouse must still be non-solid.
	var gh := root.get_node_or_null("GreenhousePreview") as Node3D
	if gh != null and bool(gh.get_meta("has_godot_collision", false)):
		_fail("collision_hint_not_authoritative", "preview anchor gained collision")
		_free_root(res)
		return
	_ok("collision_hint_not_authoritative_before_commit")
	_free_root(res)
	await process_frame


func _test_07_navigation_bake_succeeds() -> void:
	var builder = _Builder.new()
	var res: Dictionary = builder.call(
		"build_realm",
		PACKAGE_PATH,
		{"enable_collision": false, "bake_navigation": true}
	) as Dictionary
	if not bool(res.get("ok", false)):
		_fail("navigation_bake", str(res.get("reason")))
		return
	if not bool(res.get("navigation_bake_ok", false)):
		_fail("navigation_bake", "bake flag false")
		_free_root(res)
		return
	var root: Node3D = res.get("root") as Node3D
	var nav := root.get_node_or_null("NavigationRegion")
	if nav == null:
		_fail("navigation_bake", "NavigationRegion missing")
		_free_root(res)
		return
	_ok("navigation_bake_succeeds")
	_free_root(res)
	await process_frame


func _test_08_build_plot_clear() -> void:
	var builder = _Builder.new()
	var res: Dictionary = builder.call(
		"build_realm",
		PACKAGE_PATH,
		{"enable_collision": true, "bake_navigation": false}
	) as Dictionary
	if not bool(res.get("ok", false)):
		_fail("build_plot_clear", str(res.get("reason")))
		return
	if not bool(res.get("build_plot_clear", false)):
		_fail("build_plot_clear", "plot not clear after activate")
		_free_root(res)
		return
	_ok("build_plot_clear")
	_free_root(res)
	await process_frame


func _test_09_camera_not_occluded() -> void:
	var builder = _Builder.new()
	var res: Dictionary = builder.call(
		"build_realm",
		PACKAGE_PATH,
		{"enable_collision": false, "bake_navigation": false}
	) as Dictionary
	if not bool(res.get("ok", false)):
		_fail("camera_not_occluded", str(res.get("reason")))
		return
	if not bool(res.get("camera_not_occluded", false)):
		_fail("camera_not_occluded", "marker height check failed")
		_free_root(res)
		return
	_ok("camera_not_occluded")
	_free_root(res)
	await process_frame


func _test_10_cancel_hologram_no_orphan() -> void:
	if _Instance == null:
		_fail("cancel_hologram_no_orphan", "instance script missing")
		return
	var world := Node3D.new()
	world.name = "CancelWorld"
	root.add_child(world)

	var intake = _Intake.new()
	var glb_path := PACKAGE_PATH.path_join("modules/house_01.glb")
	var glb: Node3D = intake.call("load_glb_absolute", glb_path, "house_preview") as Node3D
	if glb == null:
		_fail("cancel_hologram_no_orphan", "glb load failed")
		_dispose_node(world)
		return

	var inst: Node3D = _Instance.new() as Node3D
	inst.name = "Manifestation_preview"
	world.add_child(inst)
	inst.call("configure", "p1e002_preview_house", "cozy_cyber_pixel", {
		"size": Vector3(2, 2, 2),
		"position": Vector3(1, 0, 1),
		"target_space": "private_reality",
	})
	inst.call("set_stage", "hologram")
	# Preview must be non-solid.
	if bool(inst.call("has_durable_collision")):
		_fail("cancel_hologram_no_orphan", "hologram has durable collision")
		_dispose_node(world)
		return
	var attached: bool = bool(inst.call("attach_external_visual", glb))
	if not attached:
		_fail("cancel_hologram_no_orphan", "attach_external_visual failed")
		_dispose_node(world)
		return
	# Layer still 0 on preview.
	if bool(inst.call("has_durable_collision")):
		_fail("cancel_hologram_no_orphan", "external visual made hologram solid")
		_dispose_node(world)
		return

	var builder = _Builder.new()
	var cancel_res: Dictionary = builder.call("cancel_preview_instance", inst) as Dictionary
	await process_frame
	await process_frame

	var orphan := int(cancel_res.get("orphan_collision_count", -1))
	var still := world.get_node_or_null("Manifestation_preview")
	# queue_free may leave node one frame; force check free_cleanup path
	if still != null and is_instance_valid(still):
		# After free_cleanup + queue_free, may still be valid until flush.
		_clear_presentation_meshes(still)
	_evidence["cancel"] = cancel_res
	if orphan != 0:
		_fail("cancel_hologram_no_orphan", "orphan_collision_count=%d" % orphan)
		_dispose_node(world)
		return
	# Residual note: prior confirmed building remaining after later cancel is G8 residual — not fixed here.
	_evidence["g8_residual_note"] = "prior confirmed building after later cancel is out of scope (WO residual)"
	_ok("cancel_hologram_no_orphan")
	_dispose_node(world)
	await process_frame


func _test_11_save_reload_no_duplicate() -> void:
	var parent := Node3D.new()
	parent.name = "SaveReloadParent"
	root.add_child(parent)
	var builder = _Builder.new()
	var res1: Dictionary = builder.call(
		"build_realm",
		PACKAGE_PATH,
		{"parent": parent, "enable_collision": true, "bake_navigation": false}
	) as Dictionary
	if not bool(res1.get("ok", false)):
		_fail("save_reload_no_duplicate", str(res1.get("reason")))
		_dispose_node(parent)
		return
	var root1: Node3D = res1.get("root") as Node3D
	var ids1: PackedStringArray = builder.call("collect_save_ids", root1) as PackedStringArray
	# Rebuild (save/reload simulation) into same parent — must replace, not duplicate.
	var res2: Dictionary = builder.call(
		"build_realm",
		PACKAGE_PATH,
		{"parent": parent, "enable_collision": true, "bake_navigation": false}
	) as Dictionary
	if not bool(res2.get("ok", false)):
		_fail("save_reload_no_duplicate", "second build failed")
		_dispose_node(parent)
		return
	var realm_count := 0
	for c in parent.get_children():
		if c.name == "StarterRealm":
			realm_count += 1
	var root2: Node3D = res2.get("root") as Node3D
	var ids2: PackedStringArray = builder.call("collect_save_ids", root2) as PackedStringArray
	_evidence["save_reload"] = {
		"realm_count": realm_count,
		"ids1": ids1.size(),
		"ids2": ids2.size(),
	}
	if realm_count != 1:
		_fail("save_reload_no_duplicate", "StarterRealm count=%d" % realm_count)
		_dispose_node(parent)
		return
	if ids1.size() != ids2.size() or ids1.size() == 0:
		_fail("save_reload_no_duplicate", "id count mismatch")
		_dispose_node(parent)
		return
	# Ensure unique within second build.
	var seen: Dictionary = {}
	for id in ids2:
		if seen.has(id):
			_fail("save_reload_no_duplicate", "dup id %s" % id)
			_dispose_node(parent)
			return
		seen[id] = true
	_ok("save_reload_no_duplicate")
	_dispose_node(parent)
	await process_frame


func _test_12_revision_conflict_surfaces() -> void:
	var builder = _Builder.new()
	var res: Dictionary = builder.call(
		"build_realm",
		PACKAGE_PATH,
		{
			"enable_collision": false,
			"bake_navigation": false,
			"expected_revision": "WRONG_REVISION_TOKEN_FOR_TEST",
		}
	) as Dictionary
	_evidence["revision_conflict"] = {
		"ok": res.get("ok"),
		"reason": res.get("reason"),
		"expected": res.get("expected_revision"),
		"actual": res.get("actual_revision"),
	}
	if bool(res.get("ok", false)):
		_fail("revision_conflict_surfaces", "expected failure on wrong revision")
		_free_root(res)
		return
	if str(res.get("reason", "")) != "revision_conflict":
		_fail("revision_conflict_surfaces", "reason=%s" % str(res.get("reason")))
		return
	# Positive path: matching job_id accepted.
	var pkg = _open_pkg()
	var job := str(pkg.get("job_id"))
	var res_ok: Dictionary = builder.call(
		"build_realm",
		PACKAGE_PATH,
		{"enable_collision": false, "bake_navigation": false, "expected_revision": job}
	) as Dictionary
	if not bool(res_ok.get("ok", false)):
		_fail("revision_conflict_surfaces", "matching revision rejected")
		return
	_ok("revision_conflict_surfaces")
	_free_root(res_ok)


func _test_tampered_package_refused() -> void:
	var pkg = _open_pkg()
	if pkg == null or not bool(pkg.call("is_ready")):
		_fail("tampered_package_refused", "package not ready")
		return
	pkg.call("inject_tampered_hash", "modules/house_01.glb", "0000000000000000000000000000000000000000000000000000000000000000")
	var ok: bool = bool(pkg.call("reverify_hashes"))
	_evidence["tamper"] = {"reverify_ok": ok, "refused": pkg.get("refused"), "error": pkg.get("last_error")}
	if ok or not bool(pkg.get("refused")):
		_fail("tampered_package_refused", "tamper not refused")
		return
	_ok("tampered_package_refused")


func _test_runtime_load_flag() -> void:
	var intake = _Intake.new()
	var node: Node3D = intake.call(
		"load_glb_absolute",
		PACKAGE_PATH.path_join("modules/tree_landmark_01.glb"),
		"tree_probe"
	) as Node3D
	var report: Dictionary = intake.get("last_load_report") as Dictionary
	_evidence["runtime_load"] = report
	if node == null or str(report.get("runtime_load", "")) != "OK":
		_fail("runtime_load", str(intake.get("last_error")))
		return
	print("GODOT_RUNTIME_LOAD=OK")
	_dispose_node(node)
	_ok("runtime_load_absolute_path")


func _count_solid_static(n: Node) -> int:
	var count := 0
	if n is StaticBody3D:
		var body := n as StaticBody3D
		if int(body.collision_layer) != 0:
			count += 1
	for c in n.get_children():
		count += _count_solid_static(c)
	return count


## Headless dummy: MeshInstance3D free with any mesh RID triggers
## ERROR Parameter "m" is null at mesh_get_surface_count. Clear meshes first.
## Semantic disposal — not stderr filtering.
func _clear_presentation_meshes(n: Node) -> void:
	if n == null or not is_instance_valid(n):
		return
	if n is MeshInstance3D:
		(n as MeshInstance3D).mesh = null
	for c in n.get_children():
		_clear_presentation_meshes(c)


func _dispose_node(n: Node) -> void:
	if n == null or not is_instance_valid(n):
		return
	_clear_presentation_meshes(n)
	var p: Node = n.get_parent()
	if p:
		p.remove_child(n)
	n.free()


func _free_root(res: Dictionary) -> void:
	var root = res.get("root", null)
	if root != null and is_instance_valid(root):
		_dispose_node(root as Node)
