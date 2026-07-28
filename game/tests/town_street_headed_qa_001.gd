## WO-TOWN-STREET-IMPORT-001 Phase A — headed QA for stone path network.
## Verifies TownStreet mount, 13 segments, tile placement, freecam captures vs plan.
extends SceneTree

const MAIN_SCENE := "res://scenes/main/main.tscn"
const PLAN_PATH := "res://resources/town/town_fairy_street_plan_v1.json"
const EVIDENCE_ABS := "E:/AIdle_openworld/orchestration/evidence/town_street_import_001"
const RECEIPT_DIR := "E:/AIdle_openworld/orchestration/receipts/town_street_import_001"

var _headed: bool = false
var _failures: PackedStringArray = []
var _passed: int = 0
var _captures: Array = []
var _main: Node = null
var _street: Node3D = null
var _report: Dictionary = {}


func _initialize() -> void:
	print("[TOWN_STREET_HEADED_QA] start WO-TOWN-STREET-IMPORT-001 Phase A")
	_headed = DisplayServer.get_name() != "headless"
	DirAccess.make_dir_recursive_absolute(EVIDENCE_ABS)
	DirAccess.make_dir_recursive_absolute(RECEIPT_DIR)
	await _run()
	_finish()


func _finish() -> void:
	_write_report()
	var ok := _failures.is_empty() and int(_report.get("segments_total", 0)) == 13
	var has_shots := not _captures.is_empty() and _headed
	if ok and has_shots:
		print(
			"AIDLE_TOWN_STREET_HEADED_QA=PASS checks=%d captures=%d segments=%s tiles=%s"
			% [_passed, _captures.size(), str(_report.get("segments_total", 0)), str(_report.get("tiles_placed", 0))]
		)
		quit(0)
	elif ok and not _headed:
		print("AIDLE_TOWN_STREET_HEADED_QA=PARTIAL structure_ok headed=false")
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print("AIDLE_TOWN_STREET_HEADED_QA=FAIL failed=%d" % _failures.size())
		quit(1)


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)


func _run() -> void:
	if _headed:
		_set_window(1600, 900)
		await _frames(2)
	var err := change_scene_to_file(MAIN_SCENE)
	if err != OK:
		_fail("load_main", str(err))
		return
	for i in range(120):
		await process_frame
	_main = current_scene
	if _main == null:
		_fail("main_null")
		return
	_ok("main_loaded")

	_street = _main.get_node_or_null("TownStreet") as Node3D
	if _street == null:
		_street = _main.find_child("TownStreet", true, false) as Node3D
	if _street == null:
		_fail("town_street_missing", "ENABLE_TOWN_STREET_PATHS should mount TownStreet")
		return
	_ok("town_street_found")

	if _street.has_method("get_report"):
		_report = _street.call("get_report") as Dictionary
	print("[TOWN_STREET_HEADED_QA] report=%s" % JSON.stringify(_report))

	var total := int(_report.get("segments_total", 0))
	var ok_segs := int(_report.get("segments_ok", 0))
	var tiles := int(_report.get("tiles_placed", 0))
	var coords_ok := bool(_report.get("coords_within_pm12", false))
	if total != 13:
		_fail("segments_not_13", str(total))
	else:
		_ok("segments_13")
	if ok_segs < 13:
		_fail("segments_ok_lt_13", str(ok_segs))
	else:
		_ok("segments_ok_13")
	if tiles < 13:
		_fail("tiles_sparse", str(tiles))
	else:
		_ok("tiles_placed n=%s" % tiles)
	if not coords_ok:
		_fail("coords_out_of_bounds", str(_report.get("max_abs_xz", 99)))
	else:
		_ok("coords_within_pm12")
	var pb: Variant = _report.get("phase_b_wood_platforms", {})
	if pb is Dictionary and bool(pb.get("skipped", false)):
		_ok("phase_b_honestly_skipped")
	else:
		_fail("phase_b_not_skipped")

	# Free cam overview + segment close-ups
	var free_cam := Camera3D.new()
	free_cam.name = "TownStreetQACamera"
	free_cam.current = true
	free_cam.fov = 55.0
	_main.add_child(free_cam)
	for n in _main.find_children("*", "Camera3D", true, false):
		if n != free_cam and n is Camera3D:
			(n as Camera3D).current = false

	if _headed:
		free_cam.global_position = Vector3(0.0, 32.0, 0.1)
		free_cam.look_at(Vector3(0.0, 0.0, 0.0), Vector3.FORWARD)
		await _frames(8)
		await _capture("street_overview_topdown", 1600, 900)
		free_cam.global_position = Vector3(14.0, 18.0, 14.0)
		free_cam.look_at(Vector3(0.0, 0.0, 0.0), Vector3.UP)
		await _frames(6)
		await _capture("street_overview_iso", 1600, 900)
		# Segment sample close-ups (plaza cross, ring, storybook lane)
		for cluster in [
			{"name": "street_plaza_cross", "pos": Vector3(4.0, 6.0, 4.0), "look": Vector3(0.0, 0.0, 0.0)},
			{"name": "street_storybook_lane", "pos": Vector3(8.0, 5.0, 2.0), "look": Vector3(5.0, 0.0, 1.0)},
			{"name": "street_ring_corner", "pos": Vector3(-7.0, 5.0, -7.0), "look": Vector3(-9.0, 0.0, -9.0)},
			{"name": "street_bridge_approach", "pos": Vector3(2.0, 5.0, -8.0), "look": Vector3(0.0, 0.0, -8.0)},
			{"name": "street_cottage_walk", "pos": Vector3(0.0, 5.0, 8.0), "look": Vector3(0.0, 0.0, 5.0)},
		]:
			free_cam.global_position = cluster["pos"]
			free_cam.look_at(cluster["look"], Vector3.UP)
			free_cam.current = true
			await _frames(5)
			await _capture(str(cluster["name"]), 1280, 720)
		_ok("headed_captures n=%d" % _captures.size())
	else:
		print("[TOWN_STREET_HEADED_QA] skip captures (headless)")


func _capture(name: String, w: int, h: int) -> void:
	if not _headed:
		return
	_set_window(w, h)
	await _frames(4)
	var fname := "%s_%dx%d.png" % [name, w, h]
	var path := EVIDENCE_ABS.path_join(fname)
	var img: Image = get_root().get_texture().get_image()
	if img == null:
		_error_skip(fname)
		return
	var err := img.save_png(path)
	_captures.append({"file": fname, "ok": err == OK, "path": path})
	print("[TOWN_STREET_HEADED_QA] capture %s err=%s" % [fname, str(err)])


func _error_skip(fname: String) -> void:
	print("[TOWN_STREET_HEADED_QA] capture_skip null_image %s" % fname)


func _write_report() -> void:
	var path := EVIDENCE_ABS.path_join("street_headed_qa_machine_report.json")
	var out := {
		"work_order": "WO-TOWN-STREET-IMPORT-001",
		"phase": "A_stone_path_only",
		"accepted": false,
		"self_accept": false,
		"purple": "WAITING",
		"report": _report,
		"captures": _captures,
		"checks_passed": _passed,
		"failures": Array(_failures),
	}
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(out, "\t"))
		f.close()
		print("[TOWN_STREET_HEADED_QA] wrote %s" % path)
	# also receipt
	var rpath := RECEIPT_DIR.path_join("STREET_PHASE_A_HEADED_QA.json")
	var f2 := FileAccess.open(rpath, FileAccess.WRITE)
	if f2:
		f2.store_string(JSON.stringify(out, "\t"))
		f2.close()


func _set_window(w: int, h: int) -> void:
	DisplayServer.window_set_size(Vector2i(w, h))


func _frames(n: int) -> void:
	for i in range(n):
		await process_frame
