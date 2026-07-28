## Nori-7 multi-frame capture for animated GIF proof (gardener clips + idle/walk).
## Read-only: plays existing clips; does NOT re-key GLB.
## Captures every FRAME_DT seconds across real clip duration from presenter.
##
## Run headed:
##   tools/Godot_v4.3-stable_win64_console.exe --path game \
##     -s res://tests/nori7_anim_gif_frames_qa_001.gd
## Marker: AIDLE_NORI7_ANIM_GIF_FRAMES=PASS|FAIL
extends SceneTree

const _Nori := preload("res://scripts/modules/ucbv_001/nori7_presenter.gd")

const EVIDENCE_ABS := "E:/AIdle_openworld/orchestration/evidence/nori7_anim_15clip_001"
const FRAMES_DIR := "E:/AIdle_openworld/orchestration/evidence/nori7_anim_15clip_001/gif_frames"
const RECEIPT_DIR := "E:/AIdle_openworld/orchestration/receipts/nori7_anim_15clip_001"

## Sample interval seconds (Human: ~0.1s)
const FRAME_DT := 0.1

## idle + walk for context, then 5 gardener clips
const GIF_CLIPS: PackedStringArray = [
	"idle", "walk",
	"water", "plant_seed", "harvest", "charge", "low_energy",
]

var _headed: bool = false
var _nori: Node3D = null
var _manifest: Array = []
var _failures: PackedStringArray = []


func _initialize() -> void:
	print("[NORI7_GIF_FRAMES] start multi-frame capture for GIF proof")
	_headed = DisplayServer.get_name() != "headless"
	if not _headed:
		printerr("[NORI7_GIF_FRAMES] FAIL headed required for frames")
		print("AIDLE_NORI7_ANIM_GIF_FRAMES=FAIL headed=false")
		quit(1)
		return
	DirAccess.make_dir_recursive_absolute(EVIDENCE_ABS)
	DirAccess.make_dir_recursive_absolute(FRAMES_DIR)
	DirAccess.make_dir_recursive_absolute(RECEIPT_DIR)
	await _run()
	_finish()


func _finish() -> void:
	var path := RECEIPT_DIR.path_join("nori7_anim_gif_frames_manifest.json")
	var out := {
		"schema_version": "nori7_anim_gif_frames/0.1",
		"work_order": "WO-OBJECT-DNA-NORI7-ANIM-VERTICAL-SLICE-001",
		"directive_id": 99,
		"frame_dt_s": FRAME_DT,
		"clips": _manifest,
		"failures": Array(_failures),
		"accepted": false,
		"self_accept": false,
	}
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(out, "\t"))
		f.close()
		print("[NORI7_GIF_FRAMES] manifest=%s" % path)
	if _failures.is_empty() and not _manifest.is_empty():
		var total_frames := 0
		for m in _manifest:
			total_frames += int(m.get("frame_count", 0))
		print(
			"AIDLE_NORI7_ANIM_GIF_FRAMES=PASS clips=%d total_frames=%d frame_dt=%.2f"
			% [_manifest.size(), total_frames, FRAME_DT]
		)
		quit(0)
	else:
		for e in _failures:
			printerr("[FAIL] %s" % e)
		print("AIDLE_NORI7_ANIM_GIF_FRAMES=FAIL")
		quit(1)


func _run() -> void:
	DisplayServer.window_set_size(Vector2i(640, 480))
	await _frames(2)

	var world := Node3D.new()
	world.name = "NoriGifWorld"
	get_root().add_child(world)

	var light := DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-45, 35, 0)
	light.light_energy = 1.25
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
	cam.current = true
	cam.fov = 40.0
	world.add_child(cam)
	cam.global_position = Vector3(1.6, 1.35, 2.4)
	cam.look_at(Vector3(0.0, 0.65, 0.0), Vector3.UP)

	var ground := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(8, 8)
	ground.mesh = plane
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.45, 0.62, 0.42)
	ground.material_override = mat
	world.add_child(ground)

	_nori = _Nori.new() as Node3D
	world.add_child(_nori)
	await _frames(3)
	var st: Dictionary = _nori.call("build_from_assets", 1) as Dictionary
	print("[NORI7_GIF_FRAMES] build=", JSON.stringify(st))
	if not bool(st.get("built", false)):
		_failures.append("nori_build_failed:%s" % str(st.get("build_error", st)))
		return

	for clip_id in GIF_CLIPS:
		await _capture_clip_sequence(clip_id)


func _capture_clip_sequence(clip_id: String) -> void:
	var clip_dir := FRAMES_DIR.path_join(clip_id)
	DirAccess.make_dir_recursive_absolute(clip_dir)

	var res: Dictionary = _nori.call("apply_trigger", clip_id) as Dictionary
	if not bool(res.get("ok", false)):
		res = _nori.call("play_clip_direct", clip_id) as Dictionary
	var dur: float = float(_nori.call("get_clip_duration", clip_id))
	if not bool(res.get("ok", false)) or dur <= 0.0:
		_failures.append("play_failed:%s res=%s dur=%s" % [clip_id, str(res), str(dur)])
		return

	## Frame count from real duration / FRAME_DT (at least 2 frames so GIF can animate)
	var n_frames: int = maxi(2, int(ceil(dur / FRAME_DT)) + 1)
	var paths: Array = []
	print(
		"[NORI7_GIF_FRAMES] clip=%s duration_s=%.3f frames=%d dt=%.2f"
		% [clip_id, dur, n_frames, FRAME_DT]
	)

	## Restart clip at t=0 for clean sequence
	res = _nori.call("play_clip_direct", clip_id) as Dictionary
	await _frames(2)

	for fi in range(n_frames):
		var t_target: float = minf(float(fi) * FRAME_DT, dur)
		## Advance by waiting real time from previous sample
		if fi == 0:
			await _frames(3)
		else:
			await _seconds(FRAME_DT)
		## For looped clips past duration, keep playing; for one-shots hold last pose
		if t_target >= dur - 0.001 and fi > 0:
			## re-trigger loopers so motion continues through full sample window
			var loopish := clip_id in ["idle", "walk", "charge", "low_energy", "build_place_hold"]
			if loopish and fi % maxi(1, int(ceil(dur / FRAME_DT))) == 0:
				_nori.call("play_clip_direct", clip_id)

		var fname := "%03d.png" % fi
		var fpath := clip_dir.path_join(fname)
		DisplayServer.window_set_size(Vector2i(640, 480))
		await _frames(2)
		var img: Image = get_root().get_texture().get_image()
		if img == null:
			_failures.append("null_image:%s/%s" % [clip_id, fname])
			continue
		## Downscale for GIF size
		if img.get_width() > 480:
			img.resize(480, 360, Image.INTERPOLATE_BILINEAR)
		var err := img.save_png(fpath)
		if err != OK:
			_failures.append("save_fail:%s err=%s" % [fpath, str(err)])
		else:
			paths.append(fpath)
			print("[NORI7_GIF_FRAMES]   frame %s t=%.2f" % [fname, t_target])

	_manifest.append({
		"clip_id": clip_id,
		"duration_s": dur,
		"frame_dt_s": FRAME_DT,
		"frame_count": paths.size(),
		"frame_paths": paths,
		"clip_dir": clip_dir,
		"play_result": res,
	})


func _frames(n: int) -> void:
	for i in range(n):
		await process_frame


func _seconds(s: float) -> void:
	var t0 := Time.get_ticks_msec()
	while Time.get_ticks_msec() - t0 < int(s * 1000.0):
		await process_frame
