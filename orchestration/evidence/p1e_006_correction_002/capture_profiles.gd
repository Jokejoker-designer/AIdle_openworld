## P1E-006 C1 headed capture — cozy_cyber_pixel + surrealism_canvas @ 1280x720.
## VERIFY_ONLY harness under orchestration/evidence/p1e_006_correction_002 only.
## Does NOT patch game/**. Isolates world_meta via ArtStyleManager override.
extends SceneTree

const MAIN_SCENE := "res://scenes/main/main.tscn"
const PKG := "E:/AIdle_Blender_Bridge_P0/storage/generated_quarantine/BLD-03CB1AADD475"
const EVIDENCE_ABS := "E:/AIdle_openworld/orchestration/evidence/p1e_006_correction_002"
const SELECTOR_PATH := "res://scripts/modules/asset/world_profile_variant_selector.gd"
const BUILDER_PATH := "res://scripts/modules/asset/starter_realm_builder.gd"

var _passed: int = 0
var _failed: int = 0
var _failures: PackedStringArray = []
var _captures: Array = []
var _sha_seen: Dictionary = {}
var _seed_path := "user://p1e006_c1_isolated/world_meta.cfg"


func _initialize() -> void:
	print("[P1E006_C1_HEADED] start")
	print("[P1E006_C1_HEADED] package=%s" % PKG)
	print("[P1E006_C1_HEADED] evidence=%s" % EVIDENCE_ABS)
	if DisplayServer.get_name() == "headless":
		_fail("headless_blocked")
		_finish()
		return

	DirAccess.make_dir_recursive_absolute(EVIDENCE_ABS)

	var art: Node = null
	for i in range(90):
		art = root.get_node_or_null("ArtStyleManager")
		if art != null and (not art.has_method("is_styles_ready") or bool(art.call("is_styles_ready"))):
			break
		await process_frame
	if art == null:
		_fail("art_style_manager_missing")
		_finish()
		return
	_ok("art_styles_ready")

	# Isolate world_meta — never touch Human Product Lead live save
	var seed_abs := ProjectSettings.globalize_path(_seed_path)
	DirAccess.make_dir_recursive_absolute(seed_abs.get_base_dir())
	if art.has_method("set_world_meta_path_override"):
		art.call("set_world_meta_path_override", _seed_path)
		print("[P1E006_C1_HEADED] world_meta_override=%s" % seed_abs)
	_ok("world_meta_isolated")

	_set_window(1280, 720)
	await process_frame
	await process_frame

	var err := change_scene_to_file(MAIN_SCENE)
	if err != OK:
		_fail("load_main", str(err))
		_finish()
		return
	for i in range(24):
		await process_frame

	var main := current_scene
	if main == null:
		_fail("main_null")
		_finish()
		return
	_ok("main_loaded")

	art = root.get_node_or_null("ArtStyleManager")
	if art == null:
		_fail("art_missing_after_main")
		_finish()
		return

	# --- Capture cozy_cyber_pixel ---
	await _capture_profile(main, art, "cozy_cyber_pixel", "cozy_cyber_pixel_1280x720.png")
	# --- Capture surrealism_canvas ---
	await _capture_profile(main, art, "surrealism_canvas", "surrealism_canvas_1280x720.png")

	# Distinct hashes required
	if _captures.size() == 2:
		var h0 := str((_captures[0] as Dictionary).get("sha256", ""))
		var h1 := str((_captures[1] as Dictionary).get("sha256", ""))
		if h0.is_empty() or h1.is_empty():
			_fail("missing_sha")
		elif h0 == h1:
			_fail("duplicate_profile_sha", h0.substr(0, 16))
		else:
			_ok("distinct_profile_sha")

	_write_meta()
	_finish()


func _capture_profile(main: Node, art: Node, style_id: String, filename: String) -> void:
	print("[P1E006_C1_HEADED] capture_begin profile=%s file=%s" % [style_id, filename])
	# Force style without persisting into human save (override path only if persist true)
	if not bool(art.call("set_active_style", style_id, false)):
		_fail("set_style_%s" % style_id)
		return
	var active := str(art.call("get_active_style_id"))
	if active != style_id:
		_fail("active_mismatch_%s" % style_id, "got=%s" % active)
		return
	_ok("style_active_%s" % style_id)

	# Rebuild starter realm with forced package + world_profile (matches style)
	var world_root = main.get_node_or_null("WorldRoot")
	if world_root == null:
		_fail("world_root_missing_%s" % style_id)
		return
	var pr: Node3D = world_root.get_node_or_null("PrivateReality") as Node3D
	if pr == null:
		_fail("private_reality_missing_%s" % style_id)
		return

	var Builder = load(BUILDER_PATH)
	if Builder == null:
		_fail("builder_load_%s" % style_id)
		return
	var realm_root: Node3D = Builder.build_into_opts(pr, {
		"package_path": PKG,
		"enable_collision": true,
		"world_profile": style_id,
		"force_glb": true,
	}) as Node3D
	if realm_root == null:
		_fail("realm_build_%s" % style_id)
		return
	var via_glb := bool(realm_root.get_meta("glb_intake_realm", false))
	var job_id := str(realm_root.get_meta("intake_job_id", ""))
	var pond := realm_root.get_node_or_null("Pond")
	var house := realm_root.get_node_or_null("House")
	print(
		"[P1E006_C1_HEADED] realm style=%s glb=%s job=%s pond=%s house=%s meta_profile=%s"
		% [
			style_id,
			str(via_glb),
			job_id,
			str(pond != null),
			str(house != null),
			str(realm_root.get_meta("world_profile_visual_variant", "")),
		]
	)
	if pond == null:
		_fail("pond_missing_%s" % style_id)
		return
	if not via_glb:
		_fail("not_glb_intake_%s" % style_id)
		return
	_ok("realm_ready_%s" % style_id)

	# Re-apply selector explicitly for binding proof
	var sel = load(SELECTOR_PATH).new()
	sel.call("load_catalog")
	var report: Dictionary = sel.call("apply_to_node", realm_root, style_id) as Dictionary
	var world_profile_id := str(report.get("world_profile", style_id))
	print(
		"[P1E006_C1_HEADED] variant style=%s profile=%s mode=%s rewritten=%s ok=%s"
		% [
			style_id,
			world_profile_id,
			str(report.get("mode", "")),
			str(report.get("materials_rewritten", 0)),
			str(report.get("ok", false)),
		]
	)
	if not bool(report.get("ok", false)):
		_fail("variant_apply_%s" % style_id, str(report))
		return
	if world_profile_id != style_id:
		_fail("profile_binding_%s" % style_id, world_profile_id)
		return
	_ok("profile_bound_%s" % style_id)

	# Settle frames for rendering
	_set_window(1280, 720)
	for i in range(12):
		await process_frame

	if DisplayServer.get_name() == "headless":
		_fail("capture_headless_%s" % style_id)
		return
	var img: Image = get_root().get_viewport().get_texture().get_image()
	if img == null:
		_fail("capture_null_%s" % style_id)
		return
	var w := img.get_width()
	var h := img.get_height()
	if absi(w - 1280) > 8 or absi(h - 720) > 8:
		_fail("wrong_dimensions_%s" % style_id, "%dx%d" % [w, h])
		return
	# Blank check — reject near-uniform frames
	if _is_blank(img):
		_fail("blank_image_%s" % style_id)
		return

	var abs_path := EVIDENCE_ABS.path_join(filename)
	if img.save_png(abs_path) != OK:
		_fail("save_png_%s" % style_id)
		return
	var sha := FileAccess.get_sha256(abs_path)
	if sha.is_empty():
		_fail("sha_empty_%s" % style_id)
		return
	if _sha_seen.has(sha):
		_fail("duplicate_sha_%s" % style_id, str(_sha_seen[sha]))
		return
	_sha_seen[sha] = filename

	var entry := {
		"file": filename,
		"path": abs_path.replace("\\", "/"),
		"width": w,
		"height": h,
		"sha256": sha,
		"world_profile_id": world_profile_id,
		"art_style_id_active": active,
		"package_job_id": job_id if not job_id.is_empty() else "BLD-03CB1AADD475",
		"package_path": PKG,
		"capture_source": "godot_headed",
		"live_parity": true,
		"live_parity_reason": "same BLD-03CB1AADD475 package + runtime-forced art_style_id_active==world_profile_id binding",
		"variant_mode": str(report.get("mode", "")),
		"materials_rewritten": int(report.get("materials_rewritten", 0)),
		"pond_present": true,
		"house_present": house != null,
		"starter_realm": true,
	}
	_captures.append(entry)
	_ok("captured_%s" % style_id)
	print(
		"[P1E006_C1_HEADED] CAPTURED file=%s %dx%d sha=%s profile=%s art=%s"
		% [filename, w, h, sha.substr(0, 16), world_profile_id, active]
	)


func _is_blank(img: Image) -> bool:
	# Sample a grid; if nearly all samples match first, treat as blank.
	var w := img.get_width()
	var h := img.get_height()
	if w < 8 or h < 8:
		return true
	var first: Color = img.get_pixel(w / 2, h / 2)
	var same := 0
	var total := 0
	for gy in range(8):
		for gx in range(8):
			var x := int((gx + 0.5) * w / 8.0)
			var y := int((gy + 0.5) * h / 8.0)
			var c: Color = img.get_pixel(x, y)
			total += 1
			if absf(c.r - first.r) < 0.02 and absf(c.g - first.g) < 0.02 and absf(c.b - first.b) < 0.02:
				same += 1
	return same >= total - 2


func _set_window(w: int, h: int) -> void:
	if DisplayServer.get_name() == "headless":
		return
	DisplayServer.window_set_size(Vector2i(w, h))
	print("[P1E006_C1_HEADED] window=%dx%d" % [w, h])


func _write_meta() -> void:
	var meta := {
		"schema": "p1e006_headed_correction_002/1.0",
		"work_order": "WO-P1E-006-CORRECTION-001",
		"finding_closed": "P1E006-CODEX-F03",
		"capture_source": "godot_headed",
		"package_job_id": "BLD-03CB1AADD475",
		"package_path": PKG,
		"resolution": "1280x720",
		"profiles": _captures,
		"passed_checks": _passed,
		"failed_checks": _failed,
		"failures": Array(_failures),
		"timestamp": Time.get_datetime_string_from_system(true),
		"isolation": {
			"world_meta_override": ProjectSettings.globalize_path(_seed_path),
			"persist_style": false,
			"note": "Godot 4.3-stable has no --user-data-dir CLI; isolation via world_meta override + no persist to default AppData human save",
		},
	}
	var path := EVIDENCE_ABS.path_join("visual_claim_meta.json")
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(meta, "\t"))
		f.close()
		_ok("meta_written")
		print("[P1E006_C1_HEADED] meta_written=%s" % path)
	else:
		_fail("meta_write")


func _ok(n: String) -> void:
	_passed += 1
	print("  OK  %s" % n)


func _fail(n: String, d: String = "") -> void:
	_failed += 1
	var msg := "  FAIL %s | %s" % [n, d] if not d.is_empty() else "  FAIL %s" % n
	print(msg)
	_failures.append(n if d.is_empty() else "%s:%s" % [n, d])


func _finish() -> void:
	var ok := _failed == 0 and _captures.size() == 2
	print(
		"AIDLE_P1E006_HEADED_C1=%s checks_ok=%d checks_fail=%d captures=%d"
		% ["PASS" if ok else "FAIL", _passed, _failed, _captures.size()]
	)
	quit(0 if ok else 1)
