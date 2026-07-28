## Generic cast presenter — loads Foundry production GLB + plays AnimationPlayer clips.
## Fail-soft: missing clip does not crash; missing GLB fails closed for that instance.
## Optional NPC auto_schedule cycles all available clips (Bac Bap workshop schedule).
extends Node3D

const _GlbIntake = preload("res://scripts/modules/asset/glb_intake.gd")

signal build_failed(reason: String, detail: Dictionary)
signal anim_changed(clip_id: String)
signal schedule_advanced(clip_id: String, index: int)

var character_id: String = ""
var glb_res_path: String = ""
var expected_sha256: String = ""
var _built: bool = false
var _error: String = ""
var _anim: AnimationPlayer = null
var _glb_root: Node3D = null
var _clip_map: Dictionary = {}  # clip_id -> animation name
var _current: String = ""
## NPC auto schedule
var _auto_schedule: bool = false
var _schedule_order: Array = []  # clip_id strings present in GLB
var _schedule_i: int = 0
var _loop_hold_s: float = 3.5
var _hold_timer: float = 0.0
var _finished_hooked: bool = false
var _slug: String = ""


func configure(p_character_id: String, p_glb_res: String, p_sha: String = "") -> void:
	character_id = p_character_id
	glb_res_path = p_glb_res
	expected_sha256 = p_sha


func configure_from_roster_row(row: Dictionary) -> void:
	## Full roster row: path/sha + optional auto_schedule / schedule_order / loop_hold_s.
	character_id = str(row.get("character_id", character_id))
	glb_res_path = str(row.get("glb", glb_res_path))
	expected_sha256 = str(row.get("glb_sha256", expected_sha256))
	_slug = str(row.get("slug", ""))
	_loop_hold_s = float(row.get("loop_hold_s", _loop_hold_s))
	if bool(row.get("auto_schedule", false)) or bool(row.get("npc", false)):
		_auto_schedule = true
	var so: Variant = row.get("schedule_order", [])
	if so is Array:
		_schedule_order = (so as Array).duplicate()


func is_built() -> bool:
	return _built and _error.is_empty()


func get_error() -> String:
	return _error


func get_clip_ids() -> PackedStringArray:
	var out := PackedStringArray()
	for k in _clip_map.keys():
		out.append(str(k))
	return out


func build_from_assets() -> Dictionary:
	_clear()
	_built = false
	_error = ""
	if glb_res_path.is_empty():
		return _fail("glb_path_empty", {})
	var abs_path := glb_res_path
	if glb_res_path.begins_with("res://"):
		abs_path = ProjectSettings.globalize_path(glb_res_path)
	if not FileAccess.file_exists(abs_path) and not FileAccess.file_exists(glb_res_path):
		return _fail("glb_missing", {"path": glb_res_path, "abs": abs_path})
	if not FileAccess.file_exists(abs_path):
		abs_path = glb_res_path
	if not expected_sha256.is_empty():
		var actual := _sha256_file(abs_path)
		if not actual.is_empty() and actual != expected_sha256.to_lower():
			return _fail("glb_sha256_mismatch", {"expected": expected_sha256, "actual": actual})
	var intake: RefCounted = _GlbIntake.new()
	_glb_root = intake.call("load_glb_absolute", abs_path, character_id) as Node3D
	if _glb_root == null:
		return _fail("glb_intake_failed", {"err": str(intake.get("last_error"))})
	add_child(_glb_root)
	_anim = _find_anim(_glb_root)
	if _anim == null:
		return _fail("animation_player_missing", {})
	_index_clips()
	## Root-cause fix (town cadastre white_sphere_cast_presenter):
	## 1) re-bind multi-surface materials (skinned GLB can lose readable slots under lighting)
	## 2) ground-align feet to local Y=0 so silhouette is not buried in pad
	## 3) never apply prop-style material boost here (that washes cream → "white sphere")
	_ensure_multisurface_materials(_glb_root)
	if _slug == "bui_mo" or character_id == "CCP-CT-004":
		_apply_bushcat_cute_palette(_glb_root)
	_ground_align(_glb_root)
	_sanitize_zero_scale_keys()
	_ensure_loop_flags()
	_hook_animation_finished()
	_built = true
	if _auto_schedule:
		_rebuild_schedule_from_available()
		set_process(true)
		_start_schedule()
	elif _clip_map.has("idle"):
		play_clip("idle")
	elif not _clip_map.is_empty():
		play_clip(str(_clip_map.keys()[0]))
	return {
		"built": true,
		"character_id": character_id,
		"clips": get_clip_ids(),
		"clip_count": _clip_map.size(),
		"auto_schedule": _auto_schedule,
		"schedule_len": _schedule_order.size(),
		"error": "",
		"presentation_fix": "multisurface_materials+ground_align+cute_bushcat" if (_slug == "bui_mo" or character_id == "CCP-CT-004") else "multisurface_materials+ground_align",
	}


func enable_auto_schedule(enabled: bool = true, loop_hold_s: float = -1.0) -> void:
	_auto_schedule = enabled
	if loop_hold_s > 0.0:
		_loop_hold_s = loop_hold_s
	if not _built:
		return
	if enabled:
		_rebuild_schedule_from_available()
		_hook_animation_finished()
		set_process(true)
		_start_schedule()
	else:
		set_process(false)


func disable_auto_schedule_for_roam() -> void:
	## Town roam controller owns actions — stop gallery-style clip cycle.
	_auto_schedule = false
	set_process(false)


func get_animation_player() -> AnimationPlayer:
	return _anim


func get_current_clip() -> String:
	return _current


func play_clip(clip_id: String) -> bool:
	if _anim == null:
		return false
	var name := str(_clip_map.get(clip_id, ""))
	if name.is_empty():
		# fuzzy match
		for k in _clip_map.keys():
			if str(k).to_lower() == clip_id.to_lower():
				name = str(_clip_map[k])
				break
	if name.is_empty() or not _anim.has_animation(name):
		return false
	## Ensure locomotion loops (walk/trot/run) even if GLB import left LOOP_NONE.
	var base_id := clip_id.to_lower()
	if base_id in ["walk", "trot", "run", "idle", "leaf_sway", "sniff", "hammer_loop", "carry_crate"]:
		var anim: Animation = _anim.get_animation(name)
		if anim != null and anim.loop_mode == Animation.LOOP_NONE:
			anim.loop_mode = Animation.LOOP_LINEAR
	_anim.speed_scale = 1.0
	## Force restart from frame 0 so walk always re-triggers (no silent keep of prior clip).
	if _anim.current_animation == name and _anim.is_playing():
		_anim.seek(0.0, true)
	else:
		_anim.play(name)
		_anim.seek(0.0, true)
	_current = clip_id
	_hold_timer = 0.0
	anim_changed.emit(clip_id)
	return true


func _process(delta: float) -> void:
	if not _auto_schedule or not _built or _anim == null:
		return
	if _is_clip_looping(_current):
		_hold_timer += delta
		if _hold_timer >= _loop_hold_s:
			_advance_schedule()


func _start_schedule() -> void:
	_schedule_i = 0
	_hold_timer = 0.0
	if _schedule_order.is_empty():
		if _clip_map.has("idle"):
			play_clip("idle")
		return
	var first := str(_schedule_order[0])
	play_clip(first)
	schedule_advanced.emit(first, 0)


func _advance_schedule() -> void:
	if _schedule_order.is_empty():
		return
	_schedule_i = (_schedule_i + 1) % _schedule_order.size()
	var clip_id := str(_schedule_order[_schedule_i])
	# Skip missing (should not happen after rebuild).
	var tries := 0
	while tries < _schedule_order.size() and not play_clip(clip_id):
		_schedule_i = (_schedule_i + 1) % _schedule_order.size()
		clip_id = str(_schedule_order[_schedule_i])
		tries += 1
	schedule_advanced.emit(clip_id, _schedule_i)


func _on_anim_finished(_anim_name: StringName) -> void:
	if not _auto_schedule or not _built:
		return
	# One-shots finish → next. Looping clips are held by _process timer.
	if _is_clip_looping(_current):
		return
	_advance_schedule()


func _hook_animation_finished() -> void:
	if _anim == null or _finished_hooked:
		return
	if not _anim.animation_finished.is_connected(_on_anim_finished):
		_anim.animation_finished.connect(_on_anim_finished)
	_finished_hooked = true


func _rebuild_schedule_from_available() -> void:
	## Keep preferred order when present; append any leftover clips so nothing is wasted.
	var preferred: Array = _schedule_order.duplicate() if not _schedule_order.is_empty() else []
	if preferred.is_empty():
		preferred = [
			"idle", "wave", "talk_A", "hammer_loop", "inspect_blueprint", "walk",
			"saw_loop", "talk_B", "sweep_loop", "repair_kneel", "pick_up", "carry_crate",
			"sit", "stand", "tired_idle", "happy", "scan", "handshake",
			"build_place", "build_place_hold", "confirm", "turn_left", "turn_right", "cancel",
		]
	var have: Dictionary = {}
	var ordered: Array = []
	for c in preferred:
		var key := str(c)
		if _has_clip(key) and not have.has(key.to_lower()):
			ordered.append(key)
			have[key.to_lower()] = true
	# Append remaining unique base clip names from GLB.
	for k in _clip_map.keys():
		var base := str(k)
		# skip lowercase duplicates we already indexed
		if base != base.to_lower() and base.find("/") < 0:
			if _has_clip(base) and not have.has(base.to_lower()):
				ordered.append(base)
				have[base.to_lower()] = true
	_schedule_order = ordered


func _has_clip(clip_id: String) -> bool:
	if _clip_map.has(clip_id):
		return true
	if _clip_map.has(clip_id.to_lower()):
		return true
	return false


func _is_clip_looping(clip_id: String) -> bool:
	var id := clip_id.to_lower()
	if id.ends_with("_loop") or id in [
		"idle", "walk", "trot", "run", "tired_idle", "build_place_hold", "sit",
		"leaf_sway", "sniff", "carry_crate", "hammer_loop",
	]:
		return true
	var full := str(_clip_map.get(clip_id, _clip_map.get(id, "")))
	if full.is_empty() or _anim == null or not _anim.has_animation(full):
		return false
	var anim: Animation = _anim.get_animation(full)
	if anim == null:
		return false
	return anim.loop_mode != Animation.LOOP_NONE


func _ensure_loop_flags() -> void:
	if _anim == null:
		return
	for k in _clip_map.keys():
		var base := str(k).to_lower()
		if base != str(k):
			continue
		var full := str(_clip_map[k])
		if not _anim.has_animation(full):
			continue
		var anim: Animation = _anim.get_animation(full)
		if anim == null:
			continue
		if _is_clip_looping(str(k)) and anim.loop_mode == Animation.LOOP_NONE:
			anim.loop_mode = Animation.LOOP_LINEAR


func _sanitize_zero_scale_keys() -> void:
	## Clamp scale 0 tracks / rest scales so Godot does not spam Basis→Quaternion errors.
	const EPS := 0.001
	if _anim != null:
		for anim_name in _anim.get_animation_list():
			var anim: Animation = _anim.get_animation(anim_name)
			if anim == null:
				continue
			for ti in anim.get_track_count():
				var ttype := anim.track_get_type(ti)
				if ttype != Animation.TYPE_SCALE_3D and ttype != Animation.TYPE_VALUE:
					continue
				for ki in anim.track_get_key_count(ti):
					var raw: Variant = anim.track_get_key_value(ti, ki)
					if not (raw is Vector3):
						continue
					var v: Vector3 = raw
					if v.x > 0.0 and v.y > 0.0 and v.z > 0.0:
						continue
					anim.track_set_key_value(
						ti,
						ki,
						Vector3(maxf(v.x, EPS), maxf(v.y, EPS), maxf(v.z, EPS))
					)
	if _glb_root == null:
		return
	var stack: Array = [_glb_root]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is Node3D:
			var nd := n as Node3D
			var s := nd.scale
			if s.x <= 0.0 or s.y <= 0.0 or s.z <= 0.0:
				nd.scale = Vector3(maxf(s.x, EPS), maxf(s.y, EPS), maxf(s.z, EPS))
		for c in n.get_children():
			stack.append(c)


func _index_clips() -> void:
	_clip_map.clear()
	if _anim == null:
		return
	var list: PackedStringArray = _anim.get_animation_list()
	for full in list:
		var base := str(full)
		if "/" in base:
			base = base.get_file()
		# strip library prefix patterns
		var key := base.to_lower()
		for suffix in ["", "-action", "_action"]:
			pass
		_clip_map[base] = full
		_clip_map[key] = full
		# also map without prefixes
		if base.begins_with("Anim_"):
			_clip_map[base.substr(5)] = full


func _find_anim(n: Node) -> AnimationPlayer:
	if n is AnimationPlayer:
		return n as AnimationPlayer
	for c in n.get_children():
		var f := _find_anim(c)
		if f != null:
			return f
	return null


func _sha256_file(path: String) -> String:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return ""
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	var buf := f.get_buffer(f.get_length())
	ctx.update(buf)
	f.close()
	return ctx.finish().hex_encode()


func _fail(code: String, detail: Dictionary) -> Dictionary:
	_error = code
	_built = false
	build_failed.emit(code, detail)
	return {"built": false, "error": code, "detail": detail, "character_id": character_id}


func _clear() -> void:
	for c in get_children():
		c.queue_free()
	_glb_root = null
	_anim = null
	_clip_map.clear()


## Re-bind each ArrayMesh surface material onto surface_override so multi-material
## cast skins (cream body + leaf + cyan eye) remain distinct under realm lighting.
## Root cause of white_sphere_cast_presenter was cream albedo washing to pure white
## under bright realm light + missing accent emission — fix once for all 10 cast.
func _ensure_multisurface_materials(root: Node) -> void:
	var stack: Array = [root]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is MeshInstance3D:
			var mi := n as MeshInstance3D
			if mi.mesh != null:
				var sc := mi.mesh.get_surface_count()
				for s in range(sc):
					var mat: Material = null
					if mi.mesh is ArrayMesh:
						mat = (mi.mesh as ArrayMesh).surface_get_material(s)
					if mat == null:
						mat = mi.get_active_material(s)
					if mat == null:
						continue
					## Duplicate so per-instance overrides don't share resources.
					var dup := mat.duplicate() as Material
					if dup is StandardMaterial3D:
						var sm := dup as StandardMaterial3D
						var c := sm.albedo_color
						var nm := str(sm.resource_name).to_lower()
						if nm.is_empty():
							nm = str(mi.name).to_lower()
						var maxc: float = maxf(c.r, maxf(c.g, c.b))
						var minc: float = minf(c.r, minf(c.g, c.b))
						var sat: float = 0.0 if maxc < 0.001 else (maxc - minc) / maxc
						## Near-white / low-sat cream body → warm readable beige (not pure white).
						if maxc > 0.88 and sat < 0.18:
							sm.albedo_color = Color(0.94, 0.86, 0.68, c.a)
						## Leaf / green accents — punch up + slight emission.
						elif c.g > c.r + 0.08 and c.g > c.b + 0.05:
							sm.albedo_color = Color(
								clampf(c.r * 0.85, 0.15, 0.55),
								clampf(c.g * 1.05, 0.45, 0.88),
								clampf(c.b * 0.85, 0.15, 0.50),
								c.a
							)
							sm.emission_enabled = true
							sm.emission = sm.albedo_color
							sm.emission_energy_multiplier = 0.35
						## Cyan / teal eyes & glass — strong emission for SSOT readability.
						elif c.b > 0.55 and c.g > 0.45 and c.b >= c.r:
							sm.albedo_color = Color(
								clampf(c.r * 0.7, 0.05, 0.45),
								clampf(c.g, 0.55, 0.95),
								clampf(c.b, 0.70, 1.0),
								c.a
							)
							sm.emission_enabled = true
							sm.emission = sm.albedo_color
							sm.emission_energy_multiplier = 2.0
						## Orange / warm humanoid (May Mach / Bac Bap) — keep saturation.
						elif c.r > c.g + 0.05 and c.r > c.b + 0.1 and sat > 0.15:
							sm.albedo_color = Color(
								clampf(c.r, 0.75, 1.0),
								clampf(c.g * 0.95, 0.35, 0.85),
								clampf(c.b * 0.9, 0.15, 0.55),
								c.a
							)
						## Metal / grey construct — slightly darker for silhouette.
						## Skip cream/fur/face (bushcat Bui Mo must stay soft cute, not grey monster).
						elif sat < 0.12 and maxc > 0.45 and maxc < 0.85:
							if not ("cream" in nm or "fur" in nm or "shade" in nm or "blush" in nm or "paw" in nm):
								sm.albedo_color = Color(c.r * 0.85, c.g * 0.85, c.b * 0.85, c.a)
						## Name-based boosts (Blender material names from CAST_SSOT).
						if "glass" in nm or "eye" in nm or "cyan" in nm or "emit" in nm:
							sm.emission_enabled = true
							if not sm.emission_enabled or sm.emission_energy_multiplier < 1.2:
								sm.emission = sm.albedo_color
								sm.emission_energy_multiplier = maxf(sm.emission_energy_multiplier, 1.8)
						if "leaf" in nm or "plant" in nm or "sprout" in nm or "accent" in nm:
							if c.g >= c.r:
								## Bright lime canopy (not murky forest green).
								sm.albedo_color = Color(0.42, 0.82, 0.38, c.a)
								sm.emission_enabled = true
								sm.emission = sm.albedo_color
								sm.emission_energy_multiplier = maxf(sm.emission_energy_multiplier, 0.55)
						if "wood" in nm or "hair" in nm:
							sm.albedo_color = Color(0.52, 0.36, 0.22, c.a)
						if "metal" in nm:
							sm.albedo_color = Color(0.48, 0.50, 0.52, c.a)
							sm.metallic = maxf(sm.metallic, 0.35)
						sm.roughness = clampf(sm.roughness, 0.40, 0.78)
						## Godot 4: lower metallic default keeps pastels matte under sun.
						if sm.metallic > 0.6 and "metal" not in nm:
							sm.metallic = 0.0
					mi.set_surface_override_material(s, dup)
		for c in n.get_children():
			stack.append(c)


## Bui Mo (bushcat) — force cute bright palette so dark leaves + grey face don't read as monster.
func _apply_bushcat_cute_palette(root: Node) -> void:
	var stack: Array = [root]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is MeshInstance3D:
			var mi := n as MeshInstance3D
			if mi.mesh != null:
				var sc := mi.mesh.get_surface_count()
				for s in range(sc):
					var mat: Material = mi.get_surface_override_material(s)
					if mat == null:
						if mi.mesh is ArrayMesh:
							mat = (mi.mesh as ArrayMesh).surface_get_material(s)
						if mat == null:
							mat = mi.get_active_material(s)
					if mat == null or not (mat is StandardMaterial3D):
						continue
					var sm := (mat as StandardMaterial3D).duplicate() as StandardMaterial3D
					var nm := str(sm.resource_name).to_lower()
					if nm.is_empty():
						nm = str(mi.name).to_lower()
					var c := sm.albedo_color
					## Bright sage / lime canopy leaves.
					if "dark_leaf" in nm or ("dark" in nm and "leaf" in nm):
						sm.albedo_color = Color(0.34, 0.72, 0.36, c.a)
						sm.emission_enabled = true
						sm.emission = Color(0.28, 0.62, 0.30)
						sm.emission_energy_multiplier = 0.45
					elif "sage" in nm or "leaf" in nm or "canopy" in nm or "mane" in nm:
						sm.albedo_color = Color(0.48, 0.86, 0.42, c.a)
						sm.emission_enabled = true
						sm.emission = Color(0.40, 0.78, 0.36)
						sm.emission_energy_multiplier = 0.60
					## Soft cream face/body — never grey/monster.
					elif "cream" in nm or "fur" in nm:
						sm.albedo_color = Color(0.99, 0.93, 0.78, c.a)
						sm.emission_enabled = true
						sm.emission = Color(0.98, 0.90, 0.72)
						sm.emission_energy_multiplier = 0.22
					elif "shade" in nm:
						sm.albedo_color = Color(0.92, 0.78, 0.58, c.a)
					## Peach tips + blush for cuteness.
					elif "peach" in nm or "tip" in nm:
						sm.albedo_color = Color(1.0, 0.72, 0.55, c.a)
						sm.emission_enabled = true
						sm.emission = Color(0.95, 0.62, 0.48)
						sm.emission_energy_multiplier = 0.35
					elif "blush" in nm:
						sm.albedo_color = Color(1.0, 0.62, 0.55, c.a)
						sm.emission_enabled = true
						sm.emission = Color(0.98, 0.55, 0.50)
						sm.emission_energy_multiplier = 0.40
					elif "eye" in nm and "highlight" in nm:
						sm.albedo_color = Color(1.0, 0.99, 0.95, c.a)
						sm.emission_enabled = true
						sm.emission = Color(1.0, 0.98, 0.92)
						sm.emission_energy_multiplier = 1.2
					elif "eye" in nm:
						sm.albedo_color = Color(0.28, 0.14, 0.08, c.a)
					elif "nose" in nm:
						sm.albedo_color = Color(0.42, 0.22, 0.18, c.a)
					elif "branch" in nm or "wood" in nm:
						sm.albedo_color = Color(0.58, 0.40, 0.26, c.a)
					sm.metallic = 0.0
					sm.roughness = clampf(sm.roughness, 0.45, 0.82)
					mi.set_surface_override_material(s, sm)
		for ch in n.get_children():
			stack.append(ch)


## Shift character so lowest mesh AABB sits on local Y=0 (plot pad).
func _ground_align(root: Node3D) -> void:
	if root == null:
		return
	var min_y := _mesh_min_y_local(root)
	if not is_nan(min_y) and absf(min_y) > 0.001:
		root.position.y -= min_y


## World-space: move this presenter so lowest mesh vertex sits on ground_y.
## Returns lift applied to global_position.y (positive = raised).
func align_feet_to_world_ground(ground_y: float = 0.0) -> float:
	if not is_inside_tree():
		return 0.0
	# Start from exact plane then sink/lift using body meshes only.
	var gp := global_position
	global_position = Vector3(gp.x, ground_y, gp.z)
	var min_y := _mesh_min_y_world(self)
	if is_nan(min_y):
		return 0.0
	var dy := ground_y - min_y
	# Prefer sinking floaters (dy negative or small). Cap lift hard.
	dy = clampf(dy, -0.9, 0.05)
	if absf(dy) > 0.0005:
		global_position.y = ground_y + dy
	return dy


func get_mesh_min_y_world() -> float:
	return _mesh_min_y_world(self)


func reground_visual() -> void:
	## Call after external scale change — re-zero glb feet under presenter.
	if _glb_root == null:
		return
	_glb_root.position = Vector3.ZERO
	_ground_align(_glb_root)


func set_visual_y_bias(bias: float) -> void:
	## Extra local sink for NPC plant tuning (negative = lower mesh).
	if _glb_root == null:
		return
	_glb_root.position.y += bias


func _mesh_min_y_local(root: Node3D) -> float:
	var empty := true
	var min_y := 0.0
	var stack: Array = [root]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is MeshInstance3D:
			var mi := n as MeshInstance3D
			if mi.mesh != null and mi.visible:
				var aabb := mi.mesh.get_aabb()
				var xf := mi.global_transform if mi.is_inside_tree() else mi.transform
				for i in range(8):
					var corner := aabb.position + Vector3(
						aabb.size.x if (i & 1) else 0.0,
						aabb.size.y if (i & 2) else 0.0,
						aabb.size.z if (i & 4) else 0.0
					)
					var world: Vector3 = xf * corner
					var local: Vector3 = root.to_local(world) if root.is_inside_tree() else world
					if empty or local.y < min_y:
						min_y = local.y
						empty = false
		for c in n.get_children():
			stack.append(c)
	return min_y if not empty else NAN


func _mesh_min_y_world(root: Node3D) -> float:
	## Only body/feet silhouettes — NEVER prop tools (broom/hammer/crate at scale~0 or below soles)
	## or foot snap lifts the whole NPC into the air.
	var empty := true
	var min_y := 0.0
	var stack: Array = [root]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is MeshInstance3D:
			var mi := n as MeshInstance3D
			var nm := str(mi.name).to_lower()
			if _is_foot_snap_excluded_mesh(nm):
				pass
			elif mi.mesh != null and mi.visible and mi.is_inside_tree():
				var aabb := mi.mesh.get_aabb()
				var xf := mi.global_transform
				for i in range(8):
					var corner := aabb.position + Vector3(
						aabb.size.x if (i & 1) else 0.0,
						aabb.size.y if (i & 2) else 0.0,
						aabb.size.z if (i & 4) else 0.0
					)
					var world: Vector3 = xf * corner
					if empty or world.y < min_y:
						min_y = world.y
						empty = false
		for c in n.get_children():
			stack.append(c)
	return min_y if not empty else NAN


func _is_foot_snap_excluded_mesh(nm: String) -> bool:
	## Hidden/held props + unit primitives skew AABB min-Y and float characters.
	if nm.contains("waterdrop") or nm.contains("water_drop"):
		return true
	if nm.contains("hammer") or nm.contains("saw") or nm.contains("broom"):
		return true
	if nm.contains("crate") or nm.contains("blueprint") or nm.contains("brush"):
		return true
	if nm.contains("handle") and (nm.contains("hand") or nm.contains("bbv")):
		return true
	# BBV2 prop roots / tool bits
	if nm.begins_with("bbv2_") and not (
		nm.contains("body") or nm.contains("leg") or nm.contains("boot")
		or nm.contains("foot") or nm.contains("head") or nm.contains("torso")
		or nm.contains("arm") or nm.contains("hand")
	):
		return true
	return false
