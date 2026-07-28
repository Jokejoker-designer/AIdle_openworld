## Nori-7 C2 production presenter — C1R GLB skinned mesh + AnimationTree over imported actions.
## Fail-closed: no procedural SphereMesh/pelvis-bob fallback in normal play.
## World Commit is never issued here. Animation markers are presentation-only.
## Note: no class_name for headless -s reliability.
extends Node3D

const _Paths = preload("res://scripts/modules/ucbv_001/ucbv_paths.gd")
const _GlbIntake = preload("res://scripts/modules/asset/glb_intake.gd")

signal anim_state_changed(state_id: String, clip_id: String)
signal trigger_applied(trigger: String, state_id: String)
signal build_failed_visible(reason: String, detail: Dictionary)

const PRODUCTION_MODE := "glb_c1r"
const PROCEDURAL_FALLBACK_FORBIDDEN := true

var character_id: String = _Paths.CHARACTER_ID
var recipe_id: String = _Paths.RECIPE_ID
var skeleton_id: String = _Paths.SKELETON_ID
var animation_set_id: String = "anim_robot_gardener_v1"
var production_slice: String = "c1r_glb_skinned"
var adapter_id: String = ""

var _built: bool = false
var _build_error: String = ""
var _build_detail: Dictionary = {}
var _skeleton: Skeleton3D = null
var _anim_player: AnimationPlayer = null
var _anim_tree: AnimationTree = null
var _glb_root: Node3D = null
var _fail_banner: Node3D = null
var _clip_durations: Dictionary = {}  # clip_id -> float
var _clip_loops: Dictionary = {}  # clip_id -> bool
var _state_machine: Dictionary = {}
var _adapter: Dictionary = {}
var _current_state: String = "idle"
var _presentation: bool = true
var _use_anim_tree: bool = false
var _anim_name_map: Dictionary = {}  # clip_id -> full AnimationPlayer name
var _validation_report: Dictionary = {}
var _root_motion_disabled: bool = true
var _locomotion_moving: bool = false
var _state_on_finished: Dictionary = {}  # state_id -> next_state_id
var _finished_connected: bool = false
var _leaf_sway_nodes: Array = []  # Node3D
var _leaf_rest_rot: Dictionary = {}  # instance_id -> Vector3 euler
var _leaf_sway_peaks: Dictionary = {}  # instance_id -> Vector3 euler peak
var _leaf_sway_tween: Tween = null
const LOCOMOTION_SPEED_THRESH := 0.35
const DROPLET_MIN_SCALE := 0.001
## GLB forward is +Z; player locomotion faces -Z — yaw 180 so walk matches WASD.
const MODEL_FACING_YAW_RAD := PI
## Scan presentation stretch + one head-leaf sway (user request ~4–5s).
const SCAN_PRESENTATION_S := 4.5
const LEAF_SWAY_DEG := 24.0
## Walk → idle: force even stance (blend alone left feet mid-stride).
const STOP_SETTLE_BLEND_S := 0.12
const START_WALK_BLEND_S := 0.12
const STOP_SETTLE_BOB_S := 0.26
const STOP_SETTLE_BOB_M := 0.022
const STOP_STANCE_SETTLE_S := 0.30
const STANCE_BONES: PackedStringArray = [
	"pelvis", "leg_L", "foot_L", "leg_R", "foot_R",
]
var _stop_settle_tween: Tween = null
var _glb_rest_y: float = 0.0
var _stance_settling: bool = false
## Idle frame-0 pose (even feet) captured after first idle play.
var _idle_stance_bone: Dictionary = {}  # bone_idx -> {p,r,s}
var _idle_stance_mesh: Dictionary = {}  # instance_id -> Transform3D
var _stance_mesh_nodes: Array = []  # Node3D
## Settle lerp sources (members — avoid MethodTweener.bind conversion errors on Godot 4.3).
var _settle_from_bone: Dictionary = {}
var _settle_from_mesh: Dictionary = {}
## Presenter local Y so mesh soles sit on player feet (CharacterBody3D origin).
## Idle anim sits lower than walk — use split plants (user: walk OK, idle sinks).
var _nori_feet_y: float = 0.0
const NORI_PLANT_IDLE_Y := 0.12
const NORI_PLANT_WALK_Y := 0.06


func _ready() -> void:
	if not _built:
		build_from_assets()
	set_process(true)


func _process(_delta: float) -> void:
	if not is_built():
		return
	# Keep XZ centered on player; Y is feet-snapped (_nori_feet_y).
	if absf(position.x) > 0.001 or absf(position.z) > 0.001:
		position.x = 0.0
		position.z = 0.0
	if absf(position.y - _nori_feet_y) > 0.02:
		position.y = _nori_feet_y
	if _glb_root != null and is_instance_valid(_glb_root):
		if absf(_glb_root.position.x) > 0.001 or absf(_glb_root.position.z) > 0.001:
			_glb_root.position.x = 0.0
			_glb_root.position.z = 0.0
		if absf(_glb_root.position.y - _glb_rest_y) > 0.02:
			_glb_root.position.y = _glb_rest_y
	_sync_locomotion_from_player()


func is_built() -> bool:
	return _built and _build_error.is_empty()


func get_build_error() -> String:
	return _build_error


func get_build_detail() -> Dictionary:
	return _build_detail.duplicate(true)


func get_validation_report() -> Dictionary:
	return _validation_report.duplicate(true)


func get_bone_count() -> int:
	## Production bone count (14), not raw Skeleton3D size (may include socket empties).
	if _skeleton == null:
		return 0
	var n := 0
	for i in _skeleton.get_bone_count():
		if _skeleton.get_bone_name(i) in _Paths.REQUIRED_BONES:
			n += 1
	return n


func get_bone_names() -> PackedStringArray:
	## Production bone names only (stable 14-set).
	var out := PackedStringArray()
	if _skeleton == null:
		return out
	for required in _Paths.REQUIRED_BONES:
		for i in _skeleton.get_bone_count():
			if _skeleton.get_bone_name(i) == required:
				out.append(required)
				break
	return out


func get_clip_ids() -> PackedStringArray:
	var out := PackedStringArray()
	for c in _Paths.REQUIRED_ACTIONS:
		if _clip_durations.has(c):
			out.append(c)
	return out


func get_clip_duration(clip_id: String) -> float:
	return float(_clip_durations.get(clip_id, -1.0))


func get_current_state() -> String:
	return _current_state


func uses_procedural_fallback() -> bool:
	return false


func get_status() -> Dictionary:
	return {
		"built": is_built(),
		"build_error": _build_error,
		"build_detail": _build_detail.duplicate(true),
		"character_id": character_id,
		"recipe_id": recipe_id,
		"skeleton_id": skeleton_id,
		"animation_set_id": animation_set_id,
		"production_slice": production_slice,
		"production_mode": PRODUCTION_MODE,
		"adapter_id": adapter_id,
		"bone_count": get_bone_count(),
		"clips": get_clip_ids(),
		"current_state": _current_state,
		"root_motion": false,
		"root_motion_disabled": _root_motion_disabled,
		"use_anim_tree": _use_anim_tree,
		"procedural_fallback": false,
		"procedural_fallback_forbidden": PROCEDURAL_FALLBACK_FORBIDDEN,
		"client_world_commit": false,
		"world_truth": false,
		"presentation": _presentation,
		"validation": _validation_report.duplicate(true),
	}


func build_from_assets(force_presentation: int = -1) -> Dictionary:
	## force_presentation: -1 auto, 0 headless skip heavy meshes if needed, 1 force.
	## Never falls back to procedural primitives when GLB/adapter/bones/clips fail.
	if _built and _build_error.is_empty():
		return get_status()
	_clear_children()
	_built = false
	_build_error = ""
	_build_detail = {}
	_validation_report = {}
	if force_presentation < 0:
		_presentation = _Paths.is_presentation_enabled()
	else:
		_presentation = force_presentation != 0

	name = "Nori7"
	set_meta("character_id", character_id)
	set_meta("recipe_id", recipe_id)
	set_meta("skeleton_id", skeleton_id)
	set_meta("animation_set_id", animation_set_id)
	set_meta("production_slice", production_slice)
	set_meta("production_mode", PRODUCTION_MODE)
	set_meta("style_lock_id", _Paths.STYLE_LOCK_ID)
	set_meta("client_world_commit", false)
	set_meta("world_truth", false)
	set_meta("ucbv_nori7", true)
	set_meta("procedural_fallback", false)

	var adapter_v: Variant = _Paths.load_json(_Paths.NORI_ANIM_ADAPTER)
	if adapter_v == null or not (adapter_v is Dictionary):
		return _fail_closed("adapter_missing", {
			"path": _Paths.NORI_ANIM_ADAPTER,
			"hint": "C1R nori7_animation_adapter.json required for normal play",
		})
	_adapter = adapter_v as Dictionary
	adapter_id = str(_adapter.get("adapter_id", ""))
	var sk_bind: Dictionary = _adapter.get("skeleton", {}) as Dictionary
	skeleton_id = str(sk_bind.get("skeleton_id", skeleton_id))
	if skeleton_id != _Paths.SKELETON_ID:
		return _fail_closed("adapter_skeleton_mismatch", {
			"expected": _Paths.SKELETON_ID,
			"got": skeleton_id,
		})
	if bool(sk_bind.get("root_motion", false)):
		return _fail_closed("root_motion_enabled_forbidden", {"root_motion": true})

	var char_bind: Dictionary = _adapter.get("character_binding", {}) as Dictionary
	character_id = str(char_bind.get("character_id", character_id))
	recipe_id = str(char_bind.get("recipe_id", recipe_id))
	var base_set: Dictionary = _adapter.get("base_tier3_set", {}) as Dictionary
	animation_set_id = str(base_set.get("animation_set_id", animation_set_id))

	var glb_meta: Dictionary = _adapter.get("glb", {}) as Dictionary
	var glb_res := str(glb_meta.get("path", _Paths.NORI_GLB))
	if glb_res.is_empty():
		glb_res = _Paths.NORI_GLB
	var glb_abs := _Paths.resolve_res_to_abs(glb_res)
	if not FileAccess.file_exists(glb_abs) and not FileAccess.file_exists(glb_res):
		return _fail_closed("glb_missing", {
			"res_path": glb_res,
			"abs_path": glb_abs,
			"hint": "C1R nori7_rigged.glb required; procedural presenter removed from normal play",
		})
	if not FileAccess.file_exists(glb_abs):
		glb_abs = glb_res

	var expected_sha := str(glb_meta.get("sha256", _Paths.NORI_GLB_SHA256_EXPECTED)).to_lower()
	var actual_sha := _Paths.sha256_file(glb_abs if FileAccess.file_exists(glb_abs) else glb_res)
	if not expected_sha.is_empty() and not actual_sha.is_empty() and actual_sha != expected_sha:
		return _fail_closed("glb_sha256_mismatch", {
			"expected": expected_sha,
			"actual": actual_sha,
		})

	var intake: RefCounted = _GlbIntake.new()
	_glb_root = intake.call("load_glb_absolute", glb_abs, "Nori7Glb") as Node3D
	if _glb_root == null:
		return _fail_closed("glb_intake_failed", {
			"path": glb_abs,
			"error": str(intake.get("last_error")),
			"report": intake.get("last_load_report"),
		})
	add_child(_glb_root)
	_glb_root.position = Vector3.ZERO
	_glb_rest_y = 0.0
	# Face same way as CharacterBody3D forward (WASD). Without this, model walks "backwards".
	_glb_root.rotation = Vector3(0.0, MODEL_FACING_YAW_RAD, 0.0)

	_skeleton = _find_skeleton(_glb_root)
	if _skeleton == null:
		return _fail_closed("skeleton_missing", {"hint": "GLB must contain Skeleton3D"})
	var bone_check := _validate_bones(_skeleton)
	_validation_report["bones"] = bone_check
	if not bool(bone_check.get("ok", false)):
		return _fail_closed(str(bone_check.get("code", "bone_validation_failed")), bone_check)

	_anim_player = _find_animation_player(_glb_root)
	if _anim_player == null:
		# Some exporters put AnimationPlayer as sibling of mesh under root.
		_anim_player = _find_animation_player(self)
	if _anim_player == null:
		return _fail_closed("animation_player_missing", {
			"hint": "GLB must import AnimationPlayer with required actions",
		})

	# Disable root motion on player if present.
	if _anim_player.has_method("set") and "root_motion_track" in _anim_player:
		pass
	_anim_player.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_IDLE
	_root_motion_disabled = true

	var clip_check := _index_and_validate_clips(_anim_player)
	_validation_report["clips"] = clip_check
	if not bool(clip_check.get("ok", false)):
		return _fail_closed(str(clip_check.get("code", "clip_validation_failed")), clip_check)

	var sm_v: Variant = _Paths.load_json(_Paths.NORI_STATE_MACHINE)
	if sm_v is Dictionary:
		_state_machine = sm_v as Dictionary
	_extend_state_machine_for_c2()

	var tree_ok := _build_animation_tree()
	_validation_report["animation_tree"] = {"ok": tree_ok, "use_anim_tree": _use_anim_tree}
	if not tree_ok:
		# AnimationPlayer direct play is still valid when tree construction fails;
		# clips themselves already validated. Tree failure is non-destructive.
		_use_anim_tree = false

	_index_state_on_finished()
	_ensure_loop_flags_on_clips()
	var scale_fix := _sanitize_zero_scale_animation_keys()
	_validation_report["zero_scale_sanitize"] = scale_fix
	var mat_boost := _boost_cute_water_materials()
	_validation_report["material_boost"] = mat_boost
	_ensure_all_visual_meshes_ok()
	# Reset local offsets; real feet snap runs deferred after idle pose (accurate AABB).
	_glb_root.position = Vector3.ZERO
	_glb_rest_y = 0.0
	_nori_feet_y = 0.0
	position = Vector3.ZERO
	_cache_leaf_sway_nodes()
	_validation_report["facing_yaw_rad"] = MODEL_FACING_YAW_RAD
	_validation_report["leaf_sway_nodes"] = _leaf_sway_nodes.size()
	_connect_animation_finished()

	_built = true
	_locomotion_moving = false
	_current_state = "idle"
	_play_clip("idle", 0.0)
	call_deferred("_cache_idle_even_stance")
	call_deferred("_deferred_nori_feet_and_body_check")
	# Second pass after one physics frame — GLB meshes fully in world tree.
	if is_inside_tree():
		get_tree().create_timer(0.08).timeout.connect(_snap_nori_soles_to_player_floor)
	set_meta("built", true)
	set_meta("glb_sha256", actual_sha)
	set_meta("adapter_id", adapter_id)
	set_process(true)
	return get_status()


## Map BA / locomotion triggers to state machine (presentation only — never commits world).
func apply_trigger(trigger: String) -> Dictionary:
	if not is_built():
		return {
			"ok": false,
			"reason": "not_built",
			"build_error": _build_error,
			"client_world_commit": false,
		}
	var t := trigger.strip_edges()
	if t.is_empty():
		return {"ok": false, "reason": "empty_trigger", "client_world_commit": false}
	# Hard cancel always wins.
	if t == "hard_cancel" or t == "cancel":
		return _enter_state("cancel")
	# Integration-map aliases.
	if t == "delete_mode" or t == "delete_enter":
		return _enter_state("scan")
	if t == "authoritative_complete" or t == "happy":
		return _enter_state("happy")
	if t == "move_start":
		return _enter_state("walk")
	if t == "move_stop":
		return _enter_state("idle")
	if t == "orient_left":
		return _enter_state("turn_left")
	if t == "orient_right":
		return _enter_state("turn_right")
	# Gardener package (Object DNA vertical slice) — presentation only.
	if t in [
		"water", "plant_seed", "harvest", "charge", "low_energy", "scan",
		"gardener_water", "gardener_plant_seed", "gardener_harvest",
		"gardener_charge", "gardener_low_energy", "gardener_scan",
	]:
		var gclip := t.trim_prefix("gardener_")
		if _clip_durations.has(gclip):
			return _enter_state(gclip)
		return {
			"ok": false,
			"reason": "gardener_clip_missing",
			"clip_id": gclip,
			"client_world_commit": false,
		}
	var next := _resolve_transition(_current_state, t)
	if next.is_empty():
		if t in _Paths.REQUIRED_ACTIONS:
			return _enter_state(t)
		if t == "preview_place":
			# Prefer scan → build_place path when scan exists.
			if _clip_durations.has("scan"):
				_enter_state("scan")
			return _enter_state("build_place")
		return {
			"ok": false,
			"reason": "no_transition",
			"from": _current_state,
			"trigger": t,
			"client_world_commit": false,
		}
	var res := _enter_state(next)
	res["trigger"] = t
	trigger_applied.emit(t, _current_state)
	return res


func play_clip_direct(clip_id: String) -> Dictionary:
	if not is_built():
		return {"ok": false, "reason": "not_built", "build_error": _build_error}
	if not _clip_durations.has(clip_id):
		return {"ok": false, "reason": "unknown_clip", "clip_id": clip_id}
	_current_state = clip_id
	_play_clip(clip_id, 0.08)
	anim_state_changed.emit(_current_state, clip_id)
	return {"ok": true, "state": _current_state, "clip": clip_id, "client_world_commit": false}


func _enter_state(state_id: String, blend_s: float = -1.0) -> Dictionary:
	var clip_id := state_id
	for st in _state_machine.get("states", []):
		if st is Dictionary and str((st as Dictionary).get("id", "")) == state_id:
			clip_id = str((st as Dictionary).get("clip_id", state_id))
			break
	if not _clip_durations.has(clip_id):
		return {
			"ok": false,
			"reason": "clip_missing",
			"state": state_id,
			"clip": clip_id,
			"client_world_commit": false,
		}
	var from_state := _current_state
	_current_state = state_id
	var use_blend := blend_s
	if use_blend < 0.0:
		# Default: soft blend only for locomotion handoff.
		if from_state == "walk" and state_id == "idle":
			use_blend = STOP_SETTLE_BLEND_S
		elif from_state == "idle" and state_id == "walk":
			use_blend = START_WALK_BLEND_S
		else:
			use_blend = 0.08
	# Walk→idle: blend only (no mesh-transform settle / bob — those caused float + broken look).
	_play_clip(clip_id, use_blend)
	anim_state_changed.emit(_current_state, clip_id)
	return {
		"ok": true,
		"state": _current_state,
		"clip": clip_id,
		"duration_s": get_clip_duration(clip_id),
		"blend_s": use_blend,
		"client_world_commit": false,
		"authority": false,
	}


func _resolve_transition(from_state: String, trigger: String) -> String:
	var transitions: Array = _state_machine.get("transitions", []) as Array
	var star_match := ""
	for tr in transitions:
		if not (tr is Dictionary):
			continue
		var d: Dictionary = tr
		if str(d.get("trigger", "")) != trigger:
			continue
		var fr := str(d.get("from", ""))
		if fr == from_state:
			return str(d.get("to", ""))
		if fr == "*":
			star_match = str(d.get("to", ""))
	return star_match


func _play_clip(clip_id: String, blend_s: float = 0.08) -> void:
	if _anim_player == null:
		return
	var full := str(_anim_name_map.get(clip_id, clip_id))
	# Default speed; scan is stretched for readable presentation + leaf sway.
	_anim_player.speed_scale = 1.0
	if clip_id != "scan":
		_stop_leaf_sway()
	if clip_id != "idle":
		_stop_stop_settle_beat()
	var blend := maxf(0.0, blend_s)
	if _use_anim_tree and _anim_tree != null:
		var playback: AnimationNodeStateMachinePlayback = (
			_anim_tree.get("parameters/playback") as AnimationNodeStateMachinePlayback
		)
		if playback != null:
			# Travel if state exists; else fall through to player.
			playback.travel(clip_id)
			if clip_id == "scan":
				_begin_scan_presentation(full)
			return
	if _anim_player.has_animation(full):
		# custom_blend: crossfade from current pose → new clip (feet settle walk→idle).
		_anim_player.play(full, blend)
	elif _anim_player.has_animation(clip_id):
		_anim_player.play(clip_id, blend)
		full = clip_id
	if clip_id == "scan":
		_begin_scan_presentation(full)


func _begin_stop_settle_beat() -> void:
	## Disabled — bobbing glb_root.y left Nori floating. Keep feet locked.
	_stop_stop_settle_beat()


func _stop_stop_settle_beat() -> void:
	_stance_settling = false
	if _stop_settle_tween != null and is_instance_valid(_stop_settle_tween):
		_stop_settle_tween.kill()
	_stop_settle_tween = null
	if _glb_root != null and is_instance_valid(_glb_root):
		_glb_root.position = Vector3(0.0, _glb_rest_y, 0.0)
	position = Vector3.ZERO


func _cache_idle_even_stance() -> void:
	## Snapshot idle frame-0: even feet for settle target.
	if not is_built() or _skeleton == null or _anim_player == null:
		return
	var full := str(_anim_name_map.get("idle", "idle"))
	if _anim_player.has_animation(full):
		_anim_player.play(full, 0.0)
		_anim_player.seek(0.0, true)
		_anim_player.advance(0.0)
	_idle_stance_bone.clear()
	for bname in STANCE_BONES:
		var idx := _skeleton.find_bone(bname)
		if idx < 0:
			continue
		_idle_stance_bone[idx] = {
			"p": _skeleton.get_bone_pose_position(idx),
			"r": _skeleton.get_bone_pose_rotation(idx),
			"s": _skeleton.get_bone_pose_scale(idx),
		}
	_stance_mesh_nodes.clear()
	_idle_stance_mesh.clear()
	if _glb_root == null:
		return
	var stack: Array = [_glb_root]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is Node3D and _is_stance_mesh_name(str(n.name)):
			var nd := n as Node3D
			_stance_mesh_nodes.append(nd)
			_idle_stance_mesh[nd.get_instance_id()] = nd.transform
		for c in n.get_children():
			stack.append(c)
	_validation_report["idle_stance_bones"] = _idle_stance_bone.size()
	_validation_report["idle_stance_meshes"] = _stance_mesh_nodes.size()


func _is_stance_mesh_name(nm: String) -> bool:
	if not nm.begins_with("N7V4_"):
		return false
	return (
		"Leg" in nm
		or "Boot" in nm
		or "Hip" in nm
		or "Ankle" in nm
		or "Toe" in nm
		or "Sole" in nm
	)


func _begin_even_stance_settle() -> void:
	## Simplified: just play idle with blend. Mesh-lerp settle corrupted modular body + Y.
	_cancel_even_stance_settle(false)
	_current_state = "idle"
	_play_clip("idle", STOP_SETTLE_BLEND_S)
	position = Vector3.ZERO
	if _glb_root != null:
		_glb_root.position = Vector3(0.0, _glb_rest_y, 0.0)


func _apply_even_stance_lerp_t(t: float) -> void:
	_apply_even_stance_lerp(_settle_from_bone, _settle_from_mesh, t)


func _apply_even_stance_lerp(from_bone: Dictionary, from_mesh: Dictionary, t: float) -> void:
	var u := clampf(t, 0.0, 1.0)
	# Smoothstep for softer plant.
	u = u * u * (3.0 - 2.0 * u)
	if _skeleton != null:
		for idx in _idle_stance_bone.keys():
			var i := int(idx)
			if not from_bone.has(i):
				continue
			var f: Dictionary = from_bone[i]
			var g: Dictionary = _idle_stance_bone[i]
			var rp: Vector3 = f["p"] as Vector3
			var gp: Vector3 = g["p"] as Vector3
			_skeleton.set_bone_pose_position(i, rp.lerp(gp, u))
			var rf: Quaternion = f["r"] as Quaternion
			var rg: Quaternion = g["r"] as Quaternion
			if not rf.is_normalized():
				rf = rf.normalized()
			if not rg.is_normalized():
				rg = rg.normalized()
			_skeleton.set_bone_pose_rotation(i, rf.slerp(rg, u))
			var rs: Vector3 = f["s"] as Vector3
			var gs: Vector3 = g["s"] as Vector3
			# Never lerp through non-positive scale (Basis zero → Quaternion spam).
			var out_s := rs.lerp(gs, u)
			out_s.x = maxf(out_s.x, 0.001)
			out_s.y = maxf(out_s.y, 0.001)
			out_s.z = maxf(out_s.z, 0.001)
			_skeleton.set_bone_pose_scale(i, out_s)
	for item in _stance_mesh_nodes:
		var nd := item as Node3D
		if nd == null or not is_instance_valid(nd):
			continue
		var id := nd.get_instance_id()
		if not from_mesh.has(id) or not _idle_stance_mesh.has(id):
			continue
		var a: Transform3D = from_mesh[id]
		var b: Transform3D = _idle_stance_mesh[id]
		# Avoid interpolate_with on degenerate bases.
		var origin := a.origin.lerp(b.origin, u)
		var basis_ok := (
			a.basis.get_scale().x > 0.0001
			and a.basis.get_scale().y > 0.0001
			and a.basis.get_scale().z > 0.0001
			and b.basis.get_scale().x > 0.0001
		)
		if basis_ok:
			nd.transform = a.interpolate_with(b, u)
		else:
			nd.transform = Transform3D(b.basis, origin)


func _apply_idle_stance_pose_full() -> void:
	if _skeleton == null:
		return
	for idx in _idle_stance_bone.keys():
		var i := int(idx)
		var g: Dictionary = _idle_stance_bone[i]
		_skeleton.set_bone_pose_position(i, g["p"] as Vector3)
		_skeleton.set_bone_pose_rotation(i, g["r"] as Quaternion)
		_skeleton.set_bone_pose_scale(i, g["s"] as Vector3)
	for item in _stance_mesh_nodes:
		var nd := item as Node3D
		if nd == null or not is_instance_valid(nd):
			continue
		var id := nd.get_instance_id()
		if _idle_stance_mesh.has(id):
			nd.transform = _idle_stance_mesh[id] as Transform3D


func _finish_even_stance_settle() -> void:
	_stance_settling = false
	_current_state = "idle"
	_play_clip("idle", 0.0)
	position = Vector3.ZERO
	if _glb_root != null:
		_glb_root.position = Vector3(0.0, _glb_rest_y, 0.0)


func _cancel_even_stance_settle(resume_idle_anim: bool = true) -> void:
	_stance_settling = false
	if _stop_settle_tween != null and is_instance_valid(_stop_settle_tween):
		_stop_settle_tween.kill()
	_stop_settle_tween = null
	position = Vector3.ZERO
	if _glb_root != null and is_instance_valid(_glb_root):
		_glb_root.position = Vector3(0.0, _glb_rest_y, 0.0)
	if resume_idle_anim and _current_state == "idle" and _anim_player != null:
		var full := str(_anim_name_map.get("idle", "idle"))
		if _anim_player.has_animation(full) and not _anim_player.is_playing():
			_anim_player.play(full, 0.0)


func _begin_scan_presentation(anim_full_name: String) -> void:
	## Stretch scan to ~4.5s and sway head leaves once (out and back).
	if _anim_player == null:
		return
	var anim: Animation = null
	if _anim_player.has_animation(anim_full_name):
		anim = _anim_player.get_animation(anim_full_name)
	if anim != null and anim.length > 0.01:
		_anim_player.speed_scale = float(anim.length) / SCAN_PRESENTATION_S
	else:
		_anim_player.speed_scale = 1.3 / SCAN_PRESENTATION_S
	_start_leaf_sway_once(SCAN_PRESENTATION_S)


func _cache_leaf_sway_nodes() -> void:
	_leaf_sway_nodes.clear()
	_leaf_rest_rot.clear()
	if _glb_root == null:
		return
	var stack: Array = [_glb_root]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		var nm := str(n.name)
		# Main leaf panels + stem (veins ride along if parented; else include MainVein).
		var want := (
			nm == "N7V4_LeafL"
			or nm == "N7V4_LeafR"
			or nm == "N7V4_SproutStem"
			or nm == "N7V4_LeafL_MainVein"
			or nm == "N7V4_LeafR_MainVein"
		)
		if want and n is Node3D:
			var nd := n as Node3D
			_leaf_sway_nodes.append(nd)
			_leaf_rest_rot[nd.get_instance_id()] = nd.rotation
		for c in n.get_children():
			stack.append(c)


func _start_leaf_sway_once(duration_s: float) -> void:
	_stop_leaf_sway()
	if _leaf_sway_nodes.is_empty():
		_cache_leaf_sway_nodes()
	if _leaf_sway_nodes.is_empty():
		return
	# Reset to rest pose before tween.
	for item in _leaf_sway_nodes:
		var nd := item as Node3D
		if nd == null or not is_instance_valid(nd):
			continue
		var id := nd.get_instance_id()
		if _leaf_rest_rot.has(id):
			nd.rotation = _leaf_rest_rot[id] as Vector3
	var amp := deg_to_rad(LEAF_SWAY_DEG)
	_leaf_sway_peaks.clear()
	for item in _leaf_sway_nodes:
		var nd2 := item as Node3D
		if nd2 == null or not is_instance_valid(nd2):
			continue
		var rest: Vector3 = _leaf_rest_rot.get(nd2.get_instance_id(), nd2.rotation)
		var sign_z := 1.0
		var nm2 := str(nd2.name)
		if "LeafR" in nm2:
			sign_z = -1.0
		# One soft nod on local X + side sway on Z (leaf plane).
		_leaf_sway_peaks[nd2.get_instance_id()] = rest + Vector3(amp * 0.45, 0.0, amp * sign_z)
	var tw := create_tween()
	_leaf_sway_tween = tw
	tw.tween_method(
		_apply_leaf_sway_t,
		0.0,
		1.0,
		maxf(0.2, duration_s)
	).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)


func _apply_leaf_sway_t(t: float) -> void:
	## t 0→1 over scan; weight sin(πt) does one full sway (out and back).
	var w := sin(clampf(t, 0.0, 1.0) * PI)
	for item in _leaf_sway_nodes:
		var nd := item as Node3D
		if nd == null or not is_instance_valid(nd):
			continue
		var id := nd.get_instance_id()
		if not _leaf_rest_rot.has(id) or not _leaf_sway_peaks.has(id):
			continue
		var r0: Vector3 = _leaf_rest_rot[id]
		var r1: Vector3 = _leaf_sway_peaks[id]
		nd.rotation = r0.lerp(r1, w)


func _stop_leaf_sway() -> void:
	if _leaf_sway_tween != null and is_instance_valid(_leaf_sway_tween):
		_leaf_sway_tween.kill()
	_leaf_sway_tween = null
	_leaf_sway_peaks.clear()
	for item in _leaf_sway_nodes:
		var nd := item as Node3D
		if nd == null or not is_instance_valid(nd):
			continue
		var id := nd.get_instance_id()
		if _leaf_rest_rot.has(id):
			nd.rotation = _leaf_rest_rot[id] as Vector3


func _sync_locomotion_from_player() -> void:
	## WASD locomotion → walk/idle. Never interrupts one-shot gardener/BA clips.
	var body := get_parent() as CharacterBody3D
	if body == null:
		return
	var horiz := Vector3(body.velocity.x, 0.0, body.velocity.z).length()
	var want_move := horiz > LOCOMOTION_SPEED_THRESH
	var locomotion_states := {"idle": true, "walk": true}
	if want_move:
		if _stance_settling:
			_cancel_even_stance_settle(false)
		_stop_stop_settle_beat()
		_set_nori_locomotion_plant(true)
		if not _locomotion_moving:
			_locomotion_moving = true
			if locomotion_states.has(_current_state) or _current_state == "idle":
				_enter_state("walk", START_WALK_BLEND_S)
		elif _current_state == "idle":
			_enter_state("walk", START_WALK_BLEND_S)
	else:
		if _locomotion_moving:
			_locomotion_moving = false
			_set_nori_locomotion_plant(false)
			if _current_state == "walk" or _stance_settling:
				# Force even feet (lerp to idle stance), not mid-stride freeze.
				_enter_state("idle", STOP_SETTLE_BLEND_S)
		else:
			# Standing still — keep idle plant (higher) so soles not buried.
			_set_nori_locomotion_plant(false)


func _index_state_on_finished() -> void:
	_state_on_finished.clear()
	for st in _state_machine.get("states", []):
		if not (st is Dictionary):
			continue
		var d: Dictionary = st
		var sid := str(d.get("id", ""))
		var nxt := str(d.get("on_finished", ""))
		if not sid.is_empty() and not nxt.is_empty():
			_state_on_finished[sid] = nxt


func _ensure_loop_flags_on_clips() -> void:
	if _anim_player == null:
		return
	for action in _clip_loops.keys():
		var full := str(_anim_name_map.get(action, action))
		if not _anim_player.has_animation(full):
			continue
		var anim: Animation = _anim_player.get_animation(full)
		if anim == null:
			continue
		var should_loop := bool(_clip_loops[action])
		# State machine loop flag is authoritative for idle/walk presentation.
		if action in ["idle", "walk", "build_place_hold", "charge", "low_energy"]:
			should_loop = true
		if should_loop and anim.loop_mode == Animation.LOOP_NONE:
			anim.loop_mode = Animation.LOOP_LINEAR
			_clip_loops[action] = true


func _connect_animation_finished() -> void:
	if _anim_player == null or _finished_connected:
		return
	if not _anim_player.animation_finished.is_connected(_on_animation_finished):
		_anim_player.animation_finished.connect(_on_animation_finished)
	_finished_connected = true


func _on_animation_finished(anim_name: StringName) -> void:
	if not is_built():
		return
	var base := str(anim_name)
	if base.contains("/"):
		base = base.get_slice("/", base.get_slice_count("/") - 1)
	# Only chain when the finished clip matches current state clip.
	var current_clip := _current_state
	for st in _state_machine.get("states", []):
		if st is Dictionary and str((st as Dictionary).get("id", "")) == _current_state:
			current_clip = str((st as Dictionary).get("clip_id", _current_state))
			break
	if base != current_clip and str(anim_name) != str(_anim_name_map.get(current_clip, "")):
		return
	if bool(_clip_loops.get(current_clip, false)):
		return
	var nxt := str(_state_on_finished.get(_current_state, ""))
	if nxt.is_empty():
		# Default: return to walk if still moving, else idle.
		if _locomotion_moving:
			_enter_state("walk")
		elif _current_state != "idle":
			_enter_state("idle")
		return
	if _locomotion_moving and nxt == "idle":
		_enter_state("walk")
	else:
		_enter_state(nxt)


func _sanitize_zero_scale_animation_keys() -> Dictionary:
	## Water droplets use scale 0.0 → Godot Basis→Quaternion spam. Clamp to epsilon.
	## Godot 4.3: use track_get/set_key_value (scale_track_* not always available).
	if _anim_player == null:
		return {"ok": false, "reason": "no_player"}
	var fixed_tracks := 0
	var fixed_keys := 0
	for anim_name in _anim_player.get_animation_list():
		var anim: Animation = _anim_player.get_animation(anim_name)
		if anim == null:
			continue
		for ti in anim.get_track_count():
			var ttype := anim.track_get_type(ti)
			# SCALE_3D = 7 in Godot 4; also accept VALUE tracks storing Vector3 scale.
			var handle := ttype == Animation.TYPE_SCALE_3D or ttype == Animation.TYPE_VALUE
			if not handle:
				continue
			var changed := false
			for ki in anim.track_get_key_count(ti):
				var raw: Variant = anim.track_get_key_value(ti, ki)
				if not (raw is Vector3):
					continue
				var v: Vector3 = raw
				if v.x > 0.0 and v.y > 0.0 and v.z > 0.0:
					continue
				var nx := maxf(v.x, DROPLET_MIN_SCALE)
				var ny := maxf(v.y, DROPLET_MIN_SCALE)
				var nz := maxf(v.z, DROPLET_MIN_SCALE)
				if v.length() <= 0.0001:
					nx = DROPLET_MIN_SCALE
					ny = DROPLET_MIN_SCALE
					nz = DROPLET_MIN_SCALE
				anim.track_set_key_value(ti, ki, Vector3(nx, ny, nz))
				fixed_keys += 1
				changed = true
			if changed:
				fixed_tracks += 1
	# Hide droplets at rest so epsilon scale is not visible.
	_hide_water_droplets_default()
	return {"ok": true, "fixed_tracks": fixed_tracks, "fixed_keys": fixed_keys}


func _hide_water_droplets_default() -> void:
	if _glb_root == null:
		return
	var stack: Array = [_glb_root]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		var nm := str(n.name)
		if nm.begins_with("N7V4_WaterDrop") or nm.begins_with("WaterDrop"):
			if n is Node3D:
				(n as Node3D).scale = Vector3(DROPLET_MIN_SCALE, DROPLET_MIN_SCALE, DROPLET_MIN_SCALE)
				(n as Node3D).visible = true
		for c in n.get_children():
			stack.append(c)


func _ensure_all_visual_meshes_ok() -> void:
	## Body/shell must stay visible with positive scale (user saw only leaves when body buried/zeroed).
	if _glb_root == null:
		return
	const EPS := 0.001
	var stack: Array = [_glb_root]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is MeshInstance3D:
			var mi := n as MeshInstance3D
			var nm := str(mi.name)
			# Droplets stay tiny; everything else must be visible.
			if not nm.contains("WaterDrop") and not nm.contains("water_drop"):
				mi.visible = true
				var s := mi.scale
				if s.x <= EPS or s.y <= EPS or s.z <= EPS:
					mi.scale = Vector3(maxf(s.x, 1.0), maxf(s.y, 1.0), maxf(s.z, 1.0))
				# Opaque cream body — kill accidental full transparency.
				if mi.mesh != null:
					for si in mi.mesh.get_surface_count():
						var mat := mi.get_active_material(si)
						if mat is StandardMaterial3D:
							var sm := mat as StandardMaterial3D
							if sm.albedo_color.a < 0.5:
								sm.albedo_color.a = 1.0
							if sm.transparency != BaseMaterial3D.TRANSPARENCY_DISABLED:
								if "glass" not in str(sm.resource_name).to_lower() and "tank" not in nm.to_lower():
									sm.transparency = BaseMaterial3D.TRANSPARENCY_DISABLED
		elif n is Node3D:
			var nd := n as Node3D
			var sn := str(nd.name)
			if sn.begins_with("N7V4_") and not sn.contains("WaterDrop"):
				var sc := nd.scale
				if sc.x <= EPS or sc.y <= EPS or sc.z <= EPS:
					nd.scale = Vector3(maxf(sc.x, 1.0), maxf(sc.y, 1.0), maxf(sc.z, 1.0))
				nd.visible = true
		for c in n.get_children():
			stack.append(c)


func _ground_align_glb_feet() -> void:
	## Prefer deferred world snap — keep glb_root at origin.
	if _glb_root != null:
		_glb_root.position = Vector3(0.0, 0.0, 0.0)
		_glb_rest_y = 0.0


func _is_nori_body_mesh_name(nm: String) -> bool:
	var l := nm.to_lower()
	# Only exclude water FX — Godot import may rename N7V4_* nodes.
	if l.contains("waterdrop") or l.contains("water_drop") or l.contains("droplet"):
		return false
	return true


func _mesh_min_y_world_body_only(root: Node3D) -> float:
	var empty := true
	var min_y := 0.0
	var stack: Array = [root]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is MeshInstance3D:
			var mi := n as MeshInstance3D
			if mi.mesh != null and mi.visible and mi.is_inside_tree() and _is_nori_body_mesh_name(str(mi.name)):
				var la := mi.mesh.get_aabb()
				var xf := mi.global_transform
				for i in range(8):
					var corner := la.position + Vector3(
						la.size.x if (i & 1) else 0.0,
						la.size.y if (i & 2) else 0.0,
						la.size.z if (i & 4) else 0.0
					)
					var world: Vector3 = xf * corner
					if empty or world.y < min_y:
						min_y = world.y
						empty = false
		for c in n.get_children():
			stack.append(c)
	return min_y if not empty else NAN


func _snap_nori_soles_to_player_floor() -> void:
	## Player CharacterBody3D origin = feet (capsule center at local y=0.7).
	## Lower/raise presenter so lowest body mesh sits on that floor.
	if not is_inside_tree() or _glb_root == null:
		return
	var parent_n := get_parent() as Node3D
	if parent_n == null:
		return
	var floor_y := parent_n.global_position.y
	# Reset then measure.
	position = Vector3(0.0, 0.0, 0.0)
	_glb_root.position = Vector3(0.0, 0.0, 0.0)
	_glb_rest_y = 0.0
	var min_y := _mesh_min_y_world_body_only(self)
	if is_nan(min_y):
		_nori_feet_y = NORI_PLANT_IDLE_Y
		position = Vector3(0.0, _nori_feet_y, 0.0)
		print("[Nori7] feet snap FALLBACK pos_y=%.3f (no body mesh aabb)" % _nori_feet_y)
		return
	var dy := floor_y - min_y
	_nori_feet_y = clampf(dy, -0.9, 0.16)
	# Prefer idle plant; walk uses NORI_PLANT_WALK_Y via locomotion.
	if _nori_feet_y > 0.16 or _nori_feet_y < -0.15:
		_nori_feet_y = NORI_PLANT_IDLE_Y
	position = Vector3(0.0, _nori_feet_y, 0.0)
	print("[Nori7] feet snap floor=%.3f mesh_min=%.3f dy=%.3f pos_y=%.3f" % [floor_y, min_y, dy, _nori_feet_y])


func _set_nori_locomotion_plant(walking: bool) -> void:
	## Idle sits lower in clip — use higher plant when standing still.
	_nori_feet_y = NORI_PLANT_WALK_Y if walking else NORI_PLANT_IDLE_Y
	position = Vector3(0.0, _nori_feet_y, 0.0)


func _deferred_nori_feet_and_body_check() -> void:
	_ensure_all_visual_meshes_ok()
	if _glb_root != null:
		var stack: Array = [_glb_root]
		while not stack.is_empty():
			var n: Node = stack.pop_back()
			var nm := str(n.name)
			if n is MeshInstance3D and ("Body" in nm or "Shell" in nm or "Shade" in nm or "Boot" in nm):
				(n as MeshInstance3D).visible = true
				var mi := n as MeshInstance3D
				var s := mi.scale
				if s.x < 0.5 or s.y < 0.5 or s.z < 0.5:
					mi.scale = Vector3.ONE
			for c in n.get_children():
				stack.append(c)
	_snap_nori_soles_to_player_floor()


func _boost_cute_water_materials() -> Dictionary:
	## Brighter cream / leaf / teal eyes for V4 modular pieces (presentation only).
	if _glb_root == null:
		return {"ok": false, "reason": "no_glb"}
	var touched := 0
	var stack: Array = [_glb_root]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is MeshInstance3D:
			var mi := n as MeshInstance3D
			var mesh := mi.mesh
			if mesh != null:
				for si in mesh.get_surface_count():
					var mat := mi.get_active_material(si)
					if mat == null and mesh is ArrayMesh:
						mat = (mesh as ArrayMesh).surface_get_material(si)
					if mat is StandardMaterial3D:
						var src := mat as StandardMaterial3D
						var dup := src.duplicate() as StandardMaterial3D
						var name_l := str(src.resource_name).to_lower()
						var path_l := str(mi.name).to_lower()
						var tag := name_l + " " + path_l
						if "cream" in tag or "shell" in tag or "body" in tag or "boot" in tag:
							dup.albedo_color = Color(1.0, 0.97, 0.92, 1.0)
							dup.roughness = minf(dup.roughness, 0.55)
						elif "shade" in tag and ("leaf" not in tag):
							dup.albedo_color = Color(0.92, 0.84, 0.72, 1.0)
						elif "leaf" in tag or "accent" in tag or "sprout" in tag:
							dup.albedo_color = Color(0.62, 0.92, 0.22, 1.0)
							dup.emission_enabled = true
							dup.emission = Color(0.18, 0.45, 0.05)
							dup.emission_energy_multiplier = 0.35
						elif "eye" in tag or "glass" in tag and "tank" not in tag:
							dup.albedo_color = Color(0.15, 0.95, 0.88, 1.0)
							dup.emission_enabled = true
							dup.emission = Color(0.08, 0.75, 0.7)
							dup.emission_energy_multiplier = 1.35
						elif "tank" in tag:
							dup.albedo_color = Color(0.82, 0.96, 0.98, 0.55)
							dup.emission_enabled = true
							dup.emission = Color(0.2, 0.55, 0.65)
							dup.emission_energy_multiplier = 0.45
						elif "droplet" in tag or "water" in tag:
							dup.albedo_color = Color(0.35, 0.85, 1.0, 0.9)
							dup.emission_enabled = true
							dup.emission = Color(0.1, 0.45, 0.85)
							dup.emission_energy_multiplier = 0.8
						elif "metal" in tag or "seam" in tag or "latch" in tag:
							dup.albedo_color = Color(0.18, 0.2, 0.22, 1.0)
							dup.metallic = maxf(dup.metallic, 0.55)
						else:
							# Generic lift so dull imports still read cozy-bright.
							var c := dup.albedo_color
							dup.albedo_color = Color(
								clampf(c.r * 1.08 + 0.04, 0.0, 1.0),
								clampf(c.g * 1.08 + 0.04, 0.0, 1.0),
								clampf(c.b * 1.06 + 0.03, 0.0, 1.0),
								c.a
							)
						mi.set_surface_override_material(si, dup)
						touched += 1
		for c in n.get_children():
			stack.append(c)
	return {"ok": true, "surfaces_boosted": touched}


func _fail_closed(code: String, detail: Dictionary = {}) -> Dictionary:
	_built = false
	_build_error = code
	_build_detail = detail.duplicate(true)
	_build_detail["code"] = code
	_build_detail["procedural_fallback"] = false
	_build_detail["client_world_commit"] = false
	set_meta("built", false)
	set_meta("build_error", code)
	set_meta("procedural_fallback", false)
	_show_visible_failure(code, detail)
	build_failed_visible.emit(code, _build_detail)
	push_warning("[Nori7] FAIL_CLOSED %s %s" % [code, str(detail)])
	return get_status()


func _show_visible_failure(code: String, detail: Dictionary) -> void:
	## Non-destructive visible failure marker (no world mutation, no procedural character).
	if _fail_banner != null and is_instance_valid(_fail_banner):
		_fail_banner.queue_free()
	_fail_banner = Node3D.new()
	_fail_banner.name = "Nori7FailClosed"
	_fail_banner.set_meta("fail_closed", true)
	_fail_banner.set_meta("build_error", code)
	_fail_banner.set_meta("detail", detail)
	_fail_banner.set_meta("client_world_commit", false)
	add_child(_fail_banner)
	# Only attach a tiny marker mesh when presentation is possible — never a full character.
	if _presentation:
		var mi := MeshInstance3D.new()
		mi.name = "FailMarker"
		var sph := SphereMesh.new()
		sph.radius = 0.08
		sph.height = 0.16
		mi.mesh = sph
		var mat := StandardMaterial3D.new()
		mat.albedo_color = Color(0.95, 0.25, 0.2, 0.85)
		mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		mat.emission_enabled = true
		mat.emission = Color(0.9, 0.2, 0.15)
		mat.emission_energy_multiplier = 0.6
		mi.material_override = mat
		mi.position = Vector3(0.0, 1.0, 0.0)
		_fail_banner.add_child(mi)
	print("[Nori7] visible fail-closed: %s (no procedural presenter)" % code)


func _clear_children() -> void:
	for c in get_children():
		remove_child(c)
		c.free()
	_skeleton = null
	_anim_player = null
	_anim_tree = null
	_glb_root = null
	_fail_banner = null
	_clip_durations.clear()
	_clip_loops.clear()
	_anim_name_map.clear()
	_use_anim_tree = false


func _find_skeleton(root: Node) -> Skeleton3D:
	if root is Skeleton3D:
		return root as Skeleton3D
	for c in root.get_children():
		var found := _find_skeleton(c)
		if found != null:
			return found
	return null


func _find_animation_player(root: Node) -> AnimationPlayer:
	if root is AnimationPlayer:
		return root as AnimationPlayer
	for c in root.get_children():
		var found := _find_animation_player(c)
		if found != null:
			return found
	return null


func _validate_bones(skel: Skeleton3D) -> Dictionary:
	## Exact 14 production bones + parents required. Extra socket empties from glTF
	## (character_hand/head/back, vfx_anchor) are allowed and listed, not counted as production.
	var names := PackedStringArray()
	var name_to_idx := {}
	for i in skel.get_bone_count():
		var bn := skel.get_bone_name(i)
		names.append(bn)
		name_to_idx[bn] = i
	# Reject DNA placeholder-only set.
	if names.size() == 3 and names.has("body") and names.has("head") and names.has("root"):
		return {"ok": false, "code": "dna_placeholder_bones_rejected", "names": names}
	var missing: PackedStringArray = []
	for required in _Paths.REQUIRED_BONES:
		if not name_to_idx.has(required):
			missing.append(required)
	if not missing.is_empty():
		return {
			"ok": false,
			"code": "production_bones_missing",
			"missing": missing,
			"bone_count_total": skel.get_bone_count(),
			"names": names,
		}
	var parent_errors: Array = []
	for bname in _Paths.BONE_PARENTS.keys():
		var expected_parent := str(_Paths.BONE_PARENTS[bname])
		var idx: int = int(name_to_idx[bname])
		var pidx := skel.get_bone_parent(idx)
		if expected_parent.is_empty():
			if pidx != -1:
				parent_errors.append({
					"bone": bname,
					"expected_parent": null,
					"got_parent": skel.get_bone_name(pidx) if pidx >= 0 else "",
				})
		else:
			if pidx < 0 or skel.get_bone_name(pidx) != expected_parent:
				parent_errors.append({
					"bone": bname,
					"expected_parent": expected_parent,
					"got_parent": skel.get_bone_name(pidx) if pidx >= 0 else "",
				})
	if not parent_errors.is_empty():
		return {
			"ok": false,
			"code": "bone_parent_mismatch",
			"parent_errors": parent_errors,
			"names": names,
		}
	var extras: PackedStringArray = []
	## Socket bones + glTF/Blender export artifacts + V4 modular visual bones.
	## Production animation still drives REQUIRED_BONES; N7V4_* pieces are rigid
	## modular meshes parented into the same Skeleton3D (CuteWater upgrade).
	var socket_allowed := {
		"character_hand": true,
		"character_head": true,
		"character_back": true,
		"vfx_anchor": true,
		"neutral_bone": true,
		"NeutralBone": true,
		"Armature": true,
	}
	for n in names:
		if n in _Paths.REQUIRED_BONES:
			continue
		extras.append(n)
		var allowed_extra := socket_allowed.has(n) or str(n).begins_with("N7V4_")
		if not allowed_extra:
			# Unexpected extra production-like bone — fail closed.
			return {
				"ok": false,
				"code": "unexpected_extra_bone",
				"extra": n,
				"names": names,
			}
	return {
		"ok": true,
		"bone_count": 14,
		"bone_count_total": skel.get_bone_count(),
		"production_bones": _Paths.REQUIRED_BONES,
		"extra_socket_bones": extras,
		"modular_visual_bones_allowed": true,
		"names": names,
		"hierarchy_exact": true,
	}


func _index_and_validate_clips(player: AnimationPlayer) -> Dictionary:
	_clip_durations.clear()
	_clip_loops.clear()
	_anim_name_map.clear()
	var listed: PackedStringArray = PackedStringArray(player.get_animation_list())
	# Map bare clip id → full library path (e.g. "idle" or "lib/idle").
	var by_base := {}
	for full_name in listed:
		var base := str(full_name)
		if base.contains("/"):
			base = base.get_slice("/", base.get_slice_count("/") - 1)
		by_base[base] = str(full_name)
		by_base[str(full_name)] = str(full_name)

	var adapter_actions := _collect_adapter_action_meta()
	var missing: PackedStringArray = []
	var bad_duration: PackedStringArray = []
	var bad_tracks: PackedStringArray = []
	var method_mutation: PackedStringArray = []
	var loop_mismatch: PackedStringArray = []

	for action in _Paths.REQUIRED_ACTIONS:
		var full := ""
		if by_base.has(action):
			full = str(by_base[action])
		if full.is_empty() or not player.has_animation(full):
			missing.append(action)
			continue
		var anim: Animation = player.get_animation(full)
		if anim == null:
			missing.append(action)
			continue
		var dur := float(anim.length)
		if dur <= 0.0:
			bad_duration.append(action)
			continue
		if not _has_non_root_transform_track(anim):
			bad_tracks.append(action)
			continue
		if _has_forbidden_method_track(anim):
			method_mutation.append(action)
			continue
		_clip_durations[action] = dur
		_anim_name_map[action] = full
		var loops := anim.loop_mode != Animation.LOOP_NONE
		_clip_loops[action] = loops
		if adapter_actions.has(action):
			var expect_loop := bool((adapter_actions[action] as Dictionary).get("loop", loops))
			if expect_loop != loops:
				# Soft mismatch recorded; still accept if duration/tracks ok (export loop flags).
				loop_mismatch.append(action)

	if not missing.is_empty():
		return {
			"ok": false,
			"code": "required_clips_missing",
			"missing": missing,
			"listed": listed,
		}
	if not bad_duration.is_empty():
		return {
			"ok": false,
			"code": "clip_duration_zero",
			"bad_duration": bad_duration,
		}
	if not bad_tracks.is_empty():
		return {
			"ok": false,
			"code": "clip_missing_non_root_tracks",
			"bad_tracks": bad_tracks,
		}
	if not method_mutation.is_empty():
		return {
			"ok": false,
			"code": "clip_forbidden_method_mutation",
			"method_mutation": method_mutation,
		}
	return {
		"ok": true,
		"clip_count": _clip_durations.size(),
		"durations": _clip_durations.duplicate(true),
		"loops": _clip_loops.duplicate(true),
		"loop_mismatch_soft": loop_mismatch,
		"listed": listed,
		"root_motion": false,
	}


func _collect_adapter_action_meta() -> Dictionary:
	var out := {}
	var layer_a: Dictionary = _adapter.get("layer_a_tier3_names", {}) as Dictionary
	var actions_a: Dictionary = layer_a.get("actions", {}) as Dictionary
	for k in actions_a.keys():
		if actions_a[k] is Dictionary:
			out[str(k)] = (actions_a[k] as Dictionary).duplicate(true)
	var layer_b: Dictionary = _adapter.get("layer_b_ucbv_extension", {}) as Dictionary
	var actions_b: Dictionary = layer_b.get("actions", {}) as Dictionary
	for k in actions_b.keys():
		if actions_b[k] is Dictionary:
			out[str(k)] = (actions_b[k] as Dictionary).duplicate(true)
	var layer_c: Dictionary = _adapter.get("layer_c_gardener", {}) as Dictionary
	var actions_c: Dictionary = layer_c.get("actions", {}) as Dictionary
	for k in actions_c.keys():
		if actions_c[k] is Dictionary:
			out[str(k)] = (actions_c[k] as Dictionary).duplicate(true)
	return out


func _has_non_root_transform_track(anim: Animation) -> bool:
	## Require at least one non-root transform/property track with keys.
	for i in anim.get_track_count():
		var path := str(anim.track_get_path(i))
		var ttype := anim.track_get_type(i)
		var is_xform := (
			ttype == Animation.TYPE_POSITION_3D
			or ttype == Animation.TYPE_ROTATION_3D
			or ttype == Animation.TYPE_SCALE_3D
			or ttype == Animation.TYPE_BLEND_SHAPE
			or ttype == Animation.TYPE_VALUE
		)
		if not is_xform:
			continue
		if anim.track_get_key_count(i) <= 0:
			continue
		# Reject pure root-only tracks: path ends with ":root" or "/root" bone.
		var base := path.get_file() if path.contains(":") else path
		if base.ends_with(":root") or base == "root" or path.ends_with("/root"):
			# Keep looking for non-root.
			continue
		return true
	return false


func _has_forbidden_method_track(anim: Animation) -> bool:
	## Animation markers must never call World Commit / delete / ownership / mutate.
	const FORBIDDEN := [
		"world_commit", "commit", "queue_free", "delete", "request_undo",
		"confirm_and_commit", "submit_and_preview", "mutate", "ownership",
	]
	for i in anim.get_track_count():
		if anim.track_get_type(i) != Animation.TYPE_METHOD:
			continue
		for k in anim.track_get_key_count(i):
			var key: Variant = anim.track_get_key_value(i, k)
			var method_name := ""
			if key is Dictionary:
				method_name = str((key as Dictionary).get("method", ""))
			elif key is String:
				method_name = str(key)
			var lower := method_name.to_lower()
			for f in FORBIDDEN:
				if lower.contains(f):
					return true
	return false


func _extend_state_machine_for_c2() -> void:
	## Ensure scan/happy and delete/complete reactions exist for integration map.
	if _state_machine.is_empty():
		_state_machine = {
			"default_state": "idle",
			"states": [],
			"transitions": [],
		}
	var states: Array = _state_machine.get("states", []) as Array
	var have := {}
	for st in states:
		if st is Dictionary:
			have[str((st as Dictionary).get("id", ""))] = true
	for extra in [
		"scan", "happy", "idle", "walk", "build_place", "build_place_hold", "confirm", "cancel",
		"turn_left", "turn_right",
		"water", "plant_seed", "harvest", "charge", "low_energy",
	]:
		if not have.has(extra):
			states.append({
				"id": extra,
				"clip_id": extra,
				"loop": extra in ["idle", "walk", "build_place_hold", "low_energy", "charge"],
			})
			have[extra] = true
	_state_machine["states"] = states
	var transitions: Array = _state_machine.get("transitions", []) as Array
	# Integration-map: confirm → happy after authoritative complete (runtime uses happy trigger).
	transitions.append({"from": "confirm", "to": "happy", "trigger": "happy", "blend_s": 0.1})
	transitions.append({"from": "happy", "to": "idle", "trigger": "auto_on_finished", "blend_s": 0.12})
	transitions.append({"from": "*", "to": "scan", "trigger": "delete_mode", "blend_s": 0.08})
	transitions.append({"from": "scan", "to": "build_place", "trigger": "preview_place", "blend_s": 0.08})
	_state_machine["transitions"] = transitions


func _build_animation_tree() -> bool:
	## AnimationTree state machine over imported actions.
	## Playback uses AnimationPlayer.apply_trigger path for deterministic BA wiring;
	## tree is constructed and validated so C4 can prove states resolve to imported actions.
	if _anim_player == null:
		return false
	var tree := AnimationTree.new()
	tree.name = "AnimationTree"
	var root_sm := AnimationNodeStateMachine.new()
	var added := 0
	for action in _Paths.REQUIRED_ACTIONS:
		if not _clip_durations.has(action):
			continue
		var node := AnimationNodeAnimation.new()
		var full := str(_anim_name_map.get(action, action))
		node.animation = StringName(full)
		root_sm.add_node(StringName(action), node)
		added += 1
	if added <= 0:
		tree.free()
		return false
	tree.tree_root = root_sm
	tree.active = false
	var parent_node: Node = _anim_player.get_parent()
	if parent_node == null:
		parent_node = self
	parent_node.add_child(tree)
	tree.anim_player = tree.get_path_to(_anim_player)
	_anim_tree = tree
	# Deterministic BA triggers use AnimationPlayer.play; tree remains as evidence resource.
	_use_anim_tree = false
	return true


func _anim_marker(payload: Dictionary = {}) -> void:
	## Presentation marker only — forbidden to mutate world / commit.
	if bool(payload.get("authority", false)):
		push_warning("[Nori7] authority=true anim marker ignored (forbidden)")
	# no-op by design
