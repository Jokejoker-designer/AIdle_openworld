## WO-TOWN-GRID-IMPORT-001 / Directive 99 — headed QA for town cadastre.
## Launches main (ENABLE_TOWN_GRID_CADASTRE=true), verifies 50 plots, captures
## overview + real-GLB close-ups, records art-style, writes evidence JSON.
##
## Run headed (required for screenshots):
##   tools/Godot_v4.3-stable_win64_console.exe --path game \
##     -s res://tests/town_grid_headed_qa_001.gd
## Run headless (structure only, no PNG):
##   ... --headless -s res://tests/town_grid_headed_qa_001.gd
## Marker: AIDLE_TOWN_GRID_HEADED_QA=PASS|FAIL|PARTIAL
extends SceneTree

const MAIN_SCENE := "res://scenes/main/main.tscn"
const PLAN_PATH := "res://resources/town/town_grid_plan_v1.json"
const EVIDENCE_ABS := "E:/AIdle_openworld/orchestration/evidence/town_grid_import_001"
const RECEIPT_DIR := "E:/AIdle_openworld/orchestration/receipts/town_grid_import_001"

var _headed: bool = false
var _failures: PackedStringArray = []
var _passed: int = 0
var _captures: Array = []
var _main: Node = null
var _cad: Node3D = null
var _report: Dictionary = {}
var _art_style_id: String = "unknown"
var _world_profile: String = "unknown"
var _error_lines: PackedStringArray = []
var _plot_summary: Array = []


func _initialize() -> void:
	print("[TOWN_GRID_HEADED_QA] start WO-TOWN-GRID-IMPORT-001 directive=99")
	_headed = DisplayServer.get_name() != "headless"
	print(
		"[TOWN_GRID_HEADED_QA] display=%s headed=%s evidence=%s"
		% [DisplayServer.get_name(), str(_headed), EVIDENCE_ABS]
	)
	DirAccess.make_dir_recursive_absolute(EVIDENCE_ABS)
	DirAccess.make_dir_recursive_absolute(RECEIPT_DIR)
	await _run()
	_finish()


func _finish() -> void:
	_write_machine_report()
	var ok_struct := _failures.is_empty() and int(_report.get("plots_total", 0)) == 50
	var has_shots := not _captures.is_empty() and _headed
	if ok_struct and has_shots:
		print(
			"AIDLE_TOWN_GRID_HEADED_QA=PASS checks=%d captures=%d plots=%s real_glb=%s placeholders=%s art=%s"
			% [
				_passed,
				_captures.size(),
				str(_report.get("plots_total", 0)),
				str(_report.get("real_glb", 0)),
				str(_report.get("placeholders", 0)),
				_art_style_id,
			]
		)
		quit(0)
	elif ok_struct and not _headed:
		print(
			"AIDLE_TOWN_GRID_HEADED_QA=PARTIAL structure_ok headed=false (no screenshots) plots=%s"
			% str(_report.get("plots_total", 0))
		)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print(
			"AIDLE_TOWN_GRID_HEADED_QA=FAIL failed=%d passed=%d"
			% [_failures.size(), _passed]
		)
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

	# Art style / world profile
	var art := root.get_node_or_null("ArtStyleManager")
	if art == null and _main != null:
		art = _main.get_node_or_null("ArtStyleManager")
	if art != null and art.has_method("get_active_style_id"):
		_art_style_id = str(art.call("get_active_style_id"))
	if art != null and art.has_method("get_active_world_profile"):
		_world_profile = str(art.call("get_active_world_profile"))
	elif art != null and art.has_method("get_world_profile_id"):
		_world_profile = str(art.call("get_world_profile_id"))
	print(
		"[TOWN_GRID_HEADED_QA] art_style_id=%s world_profile=%s"
		% [_art_style_id, _world_profile]
	)
	_ok("art_style_recorded art=%s profile=%s" % [_art_style_id, _world_profile])

	# Find cadastre
	_cad = _main.get_node_or_null("TownCadastre") as Node3D
	if _cad == null:
		_cad = _main.find_child("TownCadastre", true, false) as Node3D
	if _cad == null:
		_fail("town_cadastre_missing", "ENABLE_TOWN_GRID_CADASTRE should mount TownCadastre")
		return
	_ok("town_cadastre_found")

	if _cad.has_method("get_report"):
		_report = _cad.call("get_report") as Dictionary
	print("[TOWN_GRID_HEADED_QA] report=%s" % JSON.stringify(_report))

	var total := int(_report.get("plots_total", 0))
	var real_glb := int(_report.get("real_glb", 0))
	var placeholders := int(_report.get("placeholders", 0))
	var coords_ok := bool(_report.get("coords_within_pm12", false))
	var max_abs := float(_report.get("max_abs_xz", 99.0))
	if total != 50:
		_fail("plots_not_50", str(total))
	else:
		_ok("plots_50")
	if not coords_ok or max_abs > 12.0:
		_fail("coords_out_of_bounds", "max_abs=%.2f" % max_abs)
	else:
		_ok("coords_within_pm12 max_abs=%.2f" % max_abs)
	if real_glb + placeholders != 50:
		_fail("real_plus_placeholder_not_50", "real=%s ph=%s" % [real_glb, placeholders])
	else:
		_ok("real_glb=%s placeholders=%s honesty_sum=50" % [real_glb, placeholders])
	if real_glb < 1:
		_fail("no_real_glb_placed")
	else:
		_ok("real_glb_present n=%s" % real_glb)

	# Enumerate plot children for labels/footprints
	var plot_nodes := 0
	var labeled := 0
	for c in _cad.get_children():
		if str(c.name).begins_with("Plot_"):
			plot_nodes += 1
			if _has_label3d(c):
				labeled += 1
	if plot_nodes != 50:
		_fail("plot_nodes_not_50", str(plot_nodes))
	else:
		_ok("plot_nodes_50")
	if labeled < 40:
		_fail("labels_sparse", "labeled=%s" % labeled)
	else:
		_ok("labels_present labeled=%s" % labeled)

	# Free Camera3D (not player CozyCamera — that rewrites transform each frame).
	var free_cam := Camera3D.new()
	free_cam.name = "TownGridQACamera"
	free_cam.current = true
	free_cam.fov = 50.0
	_main.add_child(free_cam)
	# Disable existing cameras so free_cam wins
	for n in _main.find_children("*", "Camera3D", true, false):
		if n != free_cam and n is Camera3D:
			(n as Camera3D).current = false
	_position_overview_camera(free_cam)
	await _frames(8)
	_ok("camera_overview_positioned free_cam")

	if _headed:
		await _capture_state("town_cadastre_overview_50", 1600, 900)
		## TOWN_ALIGNMENT_V1 — extra top-down for neatness/path overlay verification
		free_cam.global_position = Vector3(0.0, 42.0, 0.05)
		free_cam.look_at(Vector3(0.0, 0.0, 0.0), Vector3.FORWARD)
		await _frames(8)
		await _capture_state("town_alignment_topdown_v1", 1600, 900)
		free_cam.global_position = Vector3(14.0, 18.0, 14.0)
		free_cam.look_at(Vector3(0.0, 0.0, 0.0), Vector3.UP)
		await _frames(6)
		await _capture_state("town_cadastre_iso_view", 1600, 900)
		for cluster in [
			# Door on Blender −Y → Godot +Z: approach from +Z for front door prominence
			{"name": "close_home", "pos": Vector3(1.2, 2.8, 4.5), "look": Vector3(0.0, 0.7, 0.0)},
			# Door at X≈−0.28 (left of HOME.CHAR at x=1.6) — approach from −X to clear occlusion
			{"name": "close_home_door", "pos": Vector3(-1.4, 1.5, 2.6), "look": Vector3(-0.28, 0.5, -0.3)},
			# Side interior window (+X) for SSOT curtains/lamp/pot
			{"name": "close_home_side", "pos": Vector3(3.2, 1.8, 1.0), "look": Vector3(0.6, 0.7, 0.0)},
			{"name": "close_home_char", "pos": Vector3(2.5, 1.8, 2.6), "look": Vector3(1.6, 0.75, 1.4)},
			{"name": "close_home_mailbox", "pos": Vector3(2.2, 2.2, -0.5), "look": Vector3(1.0, 0.5, -2.2)},
			{"name": "close_farm", "pos": Vector3(-3.0, 2.5, 10.0), "look": Vector3(-5.5, 0.3, 8.5)},
			{"name": "close_greenhouse", "pos": Vector3(-2.0, 4.5, 12.5), "look": Vector3(-5.0, 0.9, 9.0)},
			{"name": "close_greenhouse_char", "pos": Vector3(-2.5, 2.2, 8.3), "look": Vector3(-4.2, 0.7, 7.56)},
			# WORKSHOP.CHAR CCP-NW-003 @ (8.4, 0)
			{"name": "close_workshop_char", "pos": Vector3(10.2, 2.0, 1.8), "look": Vector3(8.4, 0.7, 0.0)},
			# MARKET.CHAR CCP-NS-002 @ (6.72, 5.04)
			{"name": "close_market_char", "pos": Vector3(8.5, 2.0, 6.8), "look": Vector3(6.72, 0.7, 5.04)},
			{"name": "close_lookout", "pos": Vector3(10.5, 6.0, -7.5), "look": Vector3(8.0, 0.8, -10.0)},
			{"name": "close_fence", "pos": Vector3(-9.5, 3.5, 1.0), "look": Vector3(-11.4, 0.4, -1.2)},
			# HOME.P2 lamp @ (2.4, 1.4)
			{"name": "close_lamp", "pos": Vector3(3.8, 2.2, 2.6), "look": Vector3(2.4, 0.9, 1.4)},
			# HOME.P1 path stones
			{"name": "close_path", "pos": Vector3(-0.5, 1.8, 2.2), "look": Vector3(-1.2, 0.1, 1.2)},
			# WELL.P1 pond @ (-11.4, 4.8)
			{"name": "close_pond", "pos": Vector3(-9.5, 2.0, 6.2), "look": Vector3(-11.4, 0.15, 4.8)},
			# LOOKOUT.P1 tree @ (5.6, -4.2) — plan coords
			{"name": "close_tree", "pos": Vector3(7.5, 3.2, -2.5), "look": Vector3(5.6, 1.0, -4.2)},
			# GARDEN.P1 flower @ (-0.4, 11.5)
			{"name": "close_flower", "pos": Vector3(1.2, 1.8, 12.8), "look": Vector3(-0.4, 0.3, 11.5)},
			# BARN.P2 rock @ (-2.6, -7.6)
			{"name": "close_rock", "pos": Vector3(-1.0, 1.6, -6.0), "look": Vector3(-2.6, 0.2, -7.6)},
			# BUILDINGS_WAVE1_V1 — freecam per new building at cadastre transform
			{"name": "close_workshop_bld", "pos": Vector3(12.5, 3.2, 2.5), "look": Vector3(10.0, 0.9, 0.0)},
			{"name": "close_market_bld", "pos": Vector3(10.5, 3.0, 8.5), "look": Vector3(8.0, 0.8, 6.0)},
			{"name": "close_gazebo_bld", "pos": Vector3(4.5, 3.0, 12.5), "look": Vector3(2.0, 0.9, 10.0)},
			{"name": "close_well_bld", "pos": Vector3(-6.5, 2.8, 5.0), "look": Vector3(-9.0, 0.8, 3.0)},
			{"name": "close_windmill_bld", "pos": Vector3(-6.0, 3.5, -0.5), "look": Vector3(-9.0, 1.2, -3.0)},
			{"name": "close_barn_bld", "pos": Vector3(-2.0, 3.2, -6.5), "look": Vector3(-5.0, 0.9, -9.0)},
			{"name": "close_bridge_bld", "pos": Vector3(4.5, 2.5, -7.5), "look": Vector3(2.0, 0.5, -10.0)},
			{"name": "close_watchtower_bld", "pos": Vector3(10.5, 4.5, -3.5), "look": Vector3(8.0, 1.5, -6.0)},
		]:
			free_cam.global_position = cluster["pos"]
			free_cam.look_at(cluster["look"], Vector3.UP)
			free_cam.current = true
			await _frames(6)
			await _capture_state(str(cluster["name"]), 1280, 720)
		_ok("headed_captures_done n=%d" % _captures.size())
	else:
		print("[TOWN_GRID_HEADED_QA] skip captures (headless)")

	# Build plot inventory for fidelity table (from plan + report missing list)
	_build_plot_inventory()
	print(
		"[TOWN_GRID_HEADED_QA] inventory real=%s placeholder=%s"
		% [real_glb, placeholders]
	)


func _build_plot_inventory() -> void:
	if not FileAccess.file_exists(PLAN_PATH):
		return
	var f := FileAccess.open(PLAN_PATH, FileAccess.READ)
	var plan: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if not (plan is Dictionary):
		return
	var missing_ids: Dictionary = {}
	var miss: Array = _report.get("missing", []) as Array
	for m in miss:
		if m is Dictionary:
			missing_ids[str(m.get("plot_id", ""))] = true
	for p in plan.get("plots", []) as Array:
		if not (p is Dictionary):
			continue
		var pid := str(p.get("plot_id", ""))
		var oid := str(p.get("object_id", ""))
		var role := str(p.get("role", ""))
		var is_real := not missing_ids.has(pid)
		# double-check: if report says real_glb count, inventory uses missing list
		_plot_summary.append(
			{
				"plot_id": pid,
				"object_id": oid,
				"role": role,
				"placement": "real_glb" if is_real else "honest_placeholder",
				"transform": p.get("transform", {}),
			}
		)


func _has_label3d(n: Node) -> bool:
	if n is Label3D:
		return true
	for c in n.get_children():
		if _has_label3d(c):
			return true
	return false


func _position_overview_camera(cam: Node3D) -> void:
	## High three-quarter view covering ±12 cadastre.
	cam.global_position = Vector3(0.0, 28.0, 22.0)
	cam.look_at(Vector3(0.0, 0.0, 0.0), Vector3.UP)
	if cam is Camera3D:
		var c3 := cam as Camera3D
		c3.current = true
		if c3.projection == Camera3D.PROJECTION_PERSPECTIVE:
			c3.fov = 55.0


func _capture_state(name: String, w: int, h: int) -> void:
	if not _headed:
		return
	_set_window(w, h)
	await _frames(5)
	var fname := "%s_%dx%d.png" % [name, w, h]
	var path := EVIDENCE_ABS.path_join(fname)
	var img: Image = get_root().get_texture().get_image()
	if img == null:
		print("[TOWN_GRID_HEADED_QA] capture_skip null_image %s" % fname)
		_error_lines.append("capture_null:%s" % fname)
		return
	var err := img.save_png(path)
	var entry := {
		"file": fname,
		"path": path,
		"w": w,
		"h": h,
		"state": name,
		"ok": err == OK,
		"art_style_id": _art_style_id,
	}
	_captures.append(entry)
	print("[TOWN_GRID_HEADED_QA] capture %s err=%s bytes_path=%s" % [fname, str(err), path])


func _write_machine_report() -> void:
	var path := EVIDENCE_ABS.path_join("headed_qa_machine_report.json")
	var body := {
		"schema_version": "town_grid_headed_qa_machine/1.0",
		"work_order": "WO-TOWN-GRID-IMPORT-001",
		"directive_id": 99,
		"headed": _headed,
		"display_server": DisplayServer.get_name(),
		"art_style_id": _art_style_id,
		"world_profile": _world_profile,
		"cadastre_report": _report,
		"checks_passed": _passed,
		"failures": Array(_failures),
		"captures": _captures,
		"plot_inventory": _plot_summary,
		"plot_inventory_count": _plot_summary.size(),
		"error_notes": Array(_error_lines),
		"accepted": false,
		"self_accept": false,
	}
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f != null:
		f.store_string(JSON.stringify(body, "\t"))
		f.close()
		print("[TOWN_GRID_HEADED_QA] wrote %s" % path)


func _frames(n: int) -> void:
	for i in range(n):
		await process_frame


func _set_window(w: int, h: int) -> void:
	if DisplayServer.get_name() == "headless":
		return
	DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
	DisplayServer.window_set_size(Vector2i(w, h))
	get_root().size = Vector2i(w, h)


func _find_camera(from: Node) -> Node3D:
	if from == null:
		return null
	if from.has_node("CozyCamera"):
		return from.get_node("CozyCamera") as Node3D
	var cam := from.find_child("Camera3D", true, false)
	if cam is Camera3D:
		return cam as Node3D
	cam = from.find_child("CozyCamera", true, false)
	if cam is Node3D:
		return cam as Node3D
	return null
