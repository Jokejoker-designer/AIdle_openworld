## Nori-7 Object DNA anim vertical slice — 15-clip play-through QA.
## Headed preferred (screenshots). Headless still validates structure + play triggers.
##
## Run headed:
##   tools/Godot_v4.3-stable_win64_console.exe --path game \
##     -s res://tests/nori7_anim_15clip_headed_qa_001.gd
## Headless:
##   ... --headless -s res://tests/nori7_anim_15clip_headed_qa_001.gd
## Marker: AIDLE_NORI7_ANIM_15CLIP_QA=PASS|FAIL|PARTIAL
extends SceneTree

const _Nori := preload("res://scripts/modules/ucbv_001/nori7_presenter.gd")
const _Paths := preload("res://scripts/modules/ucbv_001/ucbv_paths.gd")

const EVIDENCE_ABS := "E:/AIdle_openworld/orchestration/evidence/nori7_anim_15clip_001"
const RECEIPT_DIR := "E:/AIdle_openworld/orchestration/receipts/nori7_anim_15clip_001"

const REQUIRED_CLIPS: PackedStringArray = [
	"idle", "walk", "scan", "happy", "cancel",
	"turn_left", "turn_right", "build_place", "build_place_hold", "confirm",
	"water", "plant_seed", "harvest", "charge", "low_energy",
]

var _headed: bool = false
var _passed: int = 0
var _failures: PackedStringArray = []
var _captures: Array = []
var _clip_results: Array = []
var _nori: Node3D = null
var _report: Dictionary = {}


func _initialize() -> void:
	print("[NORI7_ANIM_15CLIP_QA] start WO-OBJECT-DNA-NORI7-ANIM-VERTICAL-SLICE-001 directive=99")
	_headed = DisplayServer.get_name() != "headless"
	print(
		"[NORI7_ANIM_15CLIP_QA] display=%s headed=%s"
		% [DisplayServer.get_name(), str(_headed)]
	)
	DirAccess.make_dir_recursive_absolute(EVIDENCE_ABS)
	DirAccess.make_dir_recursive_absolute(RECEIPT_DIR)
	await _run()
	_finish()


func _finish() -> void:
	_write_receipt()
	var ok := _failures.is_empty() and int(_report.get("clips_ok", 0)) == REQUIRED_CLIPS.size()
	var has_shots := not _captures.is_empty() and _headed
	if ok and has_shots:
		print(
			"AIDLE_NORI7_ANIM_15CLIP_QA=PASS clips=%d captures=%d"
			% [REQUIRED_CLIPS.size(), _captures.size()]
		)
		quit(0)
	elif ok and not _headed:
		print(
			"AIDLE_NORI7_ANIM_15CLIP_QA=PARTIAL structure_ok headed=false clips=%d"
			% REQUIRED_CLIPS.size()
		)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print(
			"AIDLE_NORI7_ANIM_15CLIP_QA=FAIL failed=%d passed=%d"
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
		_set_window(1280, 720)
		await _frames(2)

	var world := Node3D.new()
	world.name = "NoriQAWorld"
	get_root().add_child(world)

	# Lighting + camera for headed shots
	var light := DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-45, 35, 0)
	light.light_energy = 1.2
	world.add_child(light)
	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_COLOR
	e.background_color = Color(0.55, 0.72, 0.88)
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Color(0.85, 0.88, 0.9)
	e.ambient_light_energy = 0.55
	env.environment = e
	world.add_child(env)

	var cam := Camera3D.new()
	cam.name = "QACam"
	cam.current = true
	cam.fov = 40.0
	world.add_child(cam)
	cam.global_position = Vector3(1.6, 1.35, 2.4)
	cam.look_at(Vector3(0.0, 0.65, 0.0), Vector3.UP)

	# Ground plane for silhouette
	var ground := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(8, 8)
	ground.mesh = plane
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.45, 0.62, 0.42)
	ground.material_override = mat
	ground.position = Vector3(0, 0, 0)
	world.add_child(ground)

	_nori = _Nori.new() as Node3D
	_nori.name = "Nori7Presenter"
	world.add_child(_nori)
	await _frames(3)

	var st: Dictionary = _nori.call("build_from_assets", 1) as Dictionary
	print("  build_status=", JSON.stringify(st))
	if not bool(st.get("built", false)):
		_fail("nori_build", str(st.get("build_error", st)))
		_report = {"clips_ok": 0, "build": st}
		return
	_ok("nori_built")

	var bone_n: int = int(_nori.call("get_bone_count"))
	if bone_n == 14:
		_ok("bones_14")
	else:
		_fail("bones_count", str(bone_n))

	var clips_present: PackedStringArray = _nori.call("get_clip_ids") as PackedStringArray
	var missing: PackedStringArray = []
	for c in REQUIRED_CLIPS:
		if not clips_present.has(c) and float(_nori.call("get_clip_duration", c)) <= 0.0:
			missing.append(c)
	if missing.is_empty():
		_ok("all_15_clips_indexed")
	else:
		_fail("clips_missing", ",".join(missing))

	# Overview capture
	if _headed:
		await _capture("00_overview_idle", 1280, 720)

	var clips_ok := 0
	for i in range(REQUIRED_CLIPS.size()):
		var clip_id := REQUIRED_CLIPS[i]
		var res: Dictionary = _nori.call("apply_trigger", clip_id) as Dictionary
		# Some clips only via play_clip_direct if not transition-mapped
		if not bool(res.get("ok", false)):
			res = _nori.call("play_clip_direct", clip_id) as Dictionary
		var dur: float = float(_nori.call("get_clip_duration", clip_id))
		var ok_play := bool(res.get("ok", false)) and dur > 0.0
		var entry := {
			"clip_id": clip_id,
			"ok": ok_play,
			"duration_s": dur,
			"result": res,
		}
		_clip_results.append(entry)
		if ok_play:
			clips_ok += 1
			_ok("play_%s_d=%.2f" % [clip_id, dur])
		else:
			_fail("play_%s" % clip_id, str(res))
		# Wait a fraction of clip for pose to settle (cap 0.45s for QA speed)
		var wait_s: float = clampf(dur * 0.35, 0.12, 0.45)
		await _seconds(wait_s)
		if _headed:
			var fname := "%02d_%s" % [i + 1, clip_id]
			await _capture(fname, 1280, 720)

	# Return idle
	_nori.call("apply_trigger", "move_stop")
	await _frames(4)
	if _headed:
		await _capture("99_return_idle", 1280, 720)

	_report = {
		"clips_ok": clips_ok,
		"clips_required": REQUIRED_CLIPS.size(),
		"bone_count": bone_n,
		"built": true,
		"glb_sha_expected": _Paths.NORI_GLB_SHA256_EXPECTED,
		"captures": _captures.size(),
		"headed": _headed,
	}


func _set_window(w: int, h: int) -> void:
	DisplayServer.window_set_size(Vector2i(w, h))


func _frames(n: int) -> void:
	for i in range(n):
		await process_frame


func _seconds(s: float) -> void:
	var t0 := Time.get_ticks_msec()
	while Time.get_ticks_msec() - t0 < int(s * 1000.0):
		await process_frame


func _capture(name: String, w: int, h: int) -> void:
	if not _headed:
		return
	_set_window(w, h)
	await _frames(6)
	var fname := "%s_%dx%d.png" % [name, w, h]
	var path := EVIDENCE_ABS.path_join(fname)
	var img: Image = get_root().get_texture().get_image()
	if img == null:
		print("[NORI7_ANIM_15CLIP_QA] capture_skip null_image %s" % fname)
		return
	var err := img.save_png(path)
	var entry := {"file": fname, "path": path, "ok": err == OK, "state": name}
	_captures.append(entry)
	print("[NORI7_ANIM_15CLIP_QA] capture %s err=%s" % [fname, str(err)])


func _write_receipt() -> void:
	var receipt := {
		"schema_version": "nori7_anim_15clip_qa/0.1",
		"work_order": "WO-OBJECT-DNA-NORI7-ANIM-VERTICAL-SLICE-001",
		"directive_id": 99,
		"headed": _headed,
		"passed_checks": _passed,
		"failures": Array(_failures),
		"clip_results": _clip_results,
		"captures": _captures,
		"report": _report,
		"accepted": false,
		"self_accept": false,
	}
	var path := RECEIPT_DIR.path_join("nori7_anim_15clip_qa_receipt.json")
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(receipt, "\t"))
		f.close()
		print("[NORI7_ANIM_15CLIP_QA] receipt=%s" % path)
