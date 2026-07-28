## Town NPC roam controller — multi-profile (Bac Bap workshop · Bui Mo garden cat).
## Cycle: idle home → pick anchor → walk → context action → talk/return.
## Interrupt: player nearby → finish beat safely → face player → wave/talk/pet.
## Ground-locked: reparent free under TownCadastre, Y always = plant height.
## Never World-Commits. No class_name (headless -s safe).
extends Node

const WALK_SPEED_WORKSHOP := 1.55
const WALK_SPEED_CAT := 1.85
const ARRIVE_DIST := 0.40
const PLAYER_INTERRUPT_DIST := 2.8
## Garden cat: don't freeze for player every second — allow full roam loops.
const CAT_INTERRUPT_DIST := 1.6
const CAT_INTERRUPT_COOLDOWN_S := 14.0
const CAT_MIN_WALK_DIST := 2.2
const FACE_SPEED := 8.0
const GROUND_Y := 0.0
## Hard plant defaults (pivot mid-mesh; tuned with headed QA).
const BAC_BAP_PLANT_Y := -0.72
const GARDEN_CAT_PLANT_Y := -0.18
const KILN_WORKER_PLANT_Y := -0.55

## Workshop context weights: craft 35 · inspect 20 · carry 15 · talk 15 · rest 15
const W_CRAFT := 0.35
const W_INSPECT := 0.20
const W_CARRY := 0.15
const W_TALK := 0.15
const W_REST := 0.15
## Garden cat: bias locomotion/play so user sees walk (leg cycle) + pounce.
const C_ROAM := 0.42
const C_SNIFF := 0.18
const C_PLAY := 0.28
const C_REST := 0.06
const C_EAT := 0.06
## Kiln worker (Cinder): forge 32 · stoke 22 · carry 18 · talk 14 · rest 14
const K_FORGE := 0.32
const K_STOKE := 0.22
const K_CARRY := 0.18
const K_TALK := 0.14
const K_REST := 0.14

enum Phase {
	IDLE_WORKSHOP,
	CHOOSE_DEST,
	WALKING,
	CONTEXT_ACTION,
	CHAT_OR_RETURN,
	PLAYER_INTERRUPT,
}

var _presenter: Node3D = null
var _phase: int = Phase.IDLE_WORKSHOP
var _phase_timer: float = 0.0
var _idle_hold: float = 3.0
var _action_hold: float = 3.0
var _dest: Vector3 = Vector3.ZERO
var _dest_id: String = "workshop"
var _intent: String = "craft"
var _home: Vector3 = Vector3.ZERO
var _ground_y: float = GROUND_Y
var _anchors: Dictionary = {}
## Model faces +Z in many GLBs; player uses atan2(x,z). PI = walk face-forward.
var _facing_yaw_offset: float = PI
var _player: Node3D = null
var _interrupt_pending: bool = false
var _rng := RandomNumberGenerator.new()
var _reparented: bool = false
## Extra Y so mesh feet (not pivot) rest on ground_y.
var _feet_lift: float = 0.0
## Profile: "workshop" (Bac Bap) | "garden_cat" (Bui Mo) | "kiln_worker" (Cinder)
var _profile: String = "workshop"
var _world_scale: float = 1.0
var _walk_speed: float = WALK_SPEED_WORKSHOP
var _character_id: String = ""
var _slug: String = ""
## After player greets, block re-interrupt so cat can walk away and roam.
var _interrupt_cooldown: float = 0.0
var _chain_walks: int = 0


func setup(presenter: Node3D, home_global: Vector3, opts: Dictionary = {}) -> void:
	_presenter = presenter
	_rng.randomize()
	_ground_y = GROUND_Y
	_feet_lift = 0.0
	## Backward-compat: third arg used to be anchors-only Dictionary with "pos" keys.
	## Now accepts {profile, plant_y, scale, anchors?, character_id, slug}.
	if opts.has("pos") or (not opts.is_empty() and opts.values()[0] is Dictionary and (opts.values()[0] as Dictionary).has("pos")):
		## Legacy pure-anchors map.
		_profile = "workshop"
		_feet_lift = BAC_BAP_PLANT_Y
		_world_scale = 1.0
		_anchors = opts.duplicate(true)
	else:
		_profile = str(opts.get("profile", "workshop")).to_lower()
		if _profile in ["bac_bap", "workshop_npc", ""]:
			_profile = "workshop"
		if _profile in ["bui_mo", "cat", "bushcat"]:
			_profile = "garden_cat"
		if _profile in ["cinder", "kiln", "ember", "forge"]:
			_profile = "kiln_worker"
		_character_id = str(opts.get("character_id", ""))
		_slug = str(opts.get("slug", ""))
		if opts.has("plant_y"):
			_feet_lift = float(opts.get("plant_y"))
		elif _profile == "garden_cat":
			_feet_lift = GARDEN_CAT_PLANT_Y
		elif _profile == "kiln_worker":
			_feet_lift = KILN_WORKER_PLANT_Y
		else:
			_feet_lift = BAC_BAP_PLANT_Y
		var default_sc := 0.52 if _profile == "garden_cat" else 1.0
		_world_scale = float(opts.get("scale", default_sc))
		if _world_scale <= 0.0:
			_world_scale = default_sc
		if opts.has("anchors") and opts["anchors"] is Dictionary:
			_anchors = (opts["anchors"] as Dictionary).duplicate(true)
		else:
			_anchors = {}
	_walk_speed = WALK_SPEED_CAT if _profile == "garden_cat" else WALK_SPEED_WORKSHOP
	_home = Vector3(home_global.x, _ground_y, home_global.z)
	if _anchors.is_empty():
		_anchors = _default_anchors(_home)
	else:
		for k in _anchors.keys():
			var row: Dictionary = _anchors[k]
			if row.has("pos"):
				var p: Vector3 = row["pos"]
				row["pos"] = Vector3(p.x, _ground_y, p.z)
	if _presenter != null and _presenter.has_method("disable_auto_schedule_for_roam"):
		_presenter.call("disable_auto_schedule_for_roam")
	# Free agent under TownCadastre so plot parent scale/offset cannot float the NPC.
	call_deferred("_reparent_free_and_start")


func _reparent_free_and_start() -> void:
	if _presenter == null or not is_instance_valid(_presenter):
		return
	var cad := _find_town_cadastre()
	if cad != null and _presenter.get_parent() != cad:
		var keep := _presenter.global_transform
		var old_parent := _presenter.get_parent()
		if old_parent != null:
			old_parent.remove_child(_presenter)
		cad.add_child(_presenter)
		_presenter.global_transform = keep
		_reparented = true
	## Preserve per-character town scale (Bui Mo 0.52; Bac stays ~1.0 after free).
	var sc := _world_scale
	if sc <= 0.0:
		sc = 1.0
	_presenter.scale = Vector3(sc, sc, sc)
	if _presenter.has_method("reground_visual"):
		_presenter.call("reground_visual")
	_home = Vector3(_home.x, _ground_y + _feet_lift, _home.z)
	_snap_to_ground(_home)
	set_process(true)
	call_deferred("_remeasure_feet_lift")
	## Active NPCs start walking immediately so first seconds show locomotion.
	if _profile in ["garden_cat", "kiln_worker"]:
		_chain_walks = 0
		_choose_destination()
	else:
		_enter_idle_home()
	print(
		"[NpcRoam] %s plant=%.2f pos=%s scale=%.2f profile=%s"
		% [_slug if not _slug.is_empty() else _profile, _feet_lift, str(_presenter.global_position), sc, _profile]
	)


func _remeasure_feet_lift() -> void:
	if _presenter == null or not is_instance_valid(_presenter):
		return
	var xz := _presenter.global_position
	# Hard plant only (AABB was under-sinking workshop NPCs).
	_home = Vector3(_home.x, _ground_y + _feet_lift, _home.z)
	_snap_to_ground(xz)
	print("[NpcRoam] feet HARD plant lift=%.3f pos=%s" % [_feet_lift, str(_presenter.global_position)])


func _find_town_cadastre() -> Node3D:
	var n: Node = _presenter
	while n != null:
		if str(n.name) == "TownCadastre":
			return n as Node3D
		n = n.get_parent()
	var tree := get_tree()
	if tree == null:
		return null
	var root := tree.current_scene
	if root == null:
		root = tree.root
	return root.get_node_or_null("TownCadastre") as Node3D


func _default_anchors(home: Vector3) -> Dictionary:
	if _profile == "garden_cat":
		## Wider garden circuit so walks are long enough to read (not micro-shuffles).
		return {
			"garden_home": {"pos": Vector3(home.x, _ground_y, home.z), "kinds": ["rest", "sniff"]},
			"gazebo": {"pos": Vector3(0.0, _ground_y, 11.0), "kinds": ["rest", "eat", "sniff", "roam"]},
			"crop_row": {"pos": Vector3(-2.4, _ground_y, 9.0), "kinds": ["sniff", "eat", "roam"]},
			"lamp_path": {"pos": Vector3(3.2, _ground_y, 7.2), "kinds": ["roam", "play"]},
			"leaf_patch": {"pos": Vector3(4.4, _ground_y, 10.6), "kinds": ["play", "sniff", "roam"]},
			"plaza_edge": {"pos": Vector3(0.2, _ground_y, 5.0), "kinds": ["roam", "play"]},
			"north_path": {"pos": Vector3(-1.0, _ground_y, 12.4), "kinds": ["roam", "play", "sniff"]},
			"east_nook": {"pos": Vector3(5.2, _ground_y, 8.6), "kinds": ["play", "roam", "eat"]},
			"shade_rest": {"pos": Vector3(1.7, _ground_y, 11.6), "kinds": ["rest"]},
			"water_bowl": {"pos": Vector3(-1.4, _ground_y, 10.6), "kinds": ["eat", "sniff"]},
			"south_loop": {"pos": Vector3(2.0, _ground_y, 4.2), "kinds": ["roam", "play"]},
		}
	if _profile == "kiln_worker":
		## WINDMILL / craft landmark circuit around Cinder home.
		return {
			"kiln_home": {"pos": Vector3(home.x, _ground_y, home.z), "kinds": ["forge", "rest", "talk", "stoke"]},
			"windmill": {"pos": Vector3(-9.0, _ground_y, -9.0), "kinds": ["stoke", "forge", "rest"]},
			"anvil": {"pos": Vector3(-6.2, _ground_y, -4.0), "kinds": ["forge", "talk"]},
			"ember_pit": {"pos": Vector3(-8.4, _ground_y, -5.2), "kinds": ["stoke", "forge"]},
			"crate_yard": {"pos": Vector3(-5.0, _ground_y, -1.6), "kinds": ["carry", "forge"]},
			"wood_stack": {"pos": Vector3(-10.6, _ground_y, -6.4), "kinds": ["carry", "stoke"]},
			"doorway": {"pos": Vector3(-7.0, _ground_y, -0.8), "kinds": ["talk", "rest"]},
			"path_loop": {"pos": Vector3(-4.2, _ground_y, -3.2), "kinds": ["carry", "talk", "rest"]},
			"cool_bench": {"pos": Vector3(-9.6, _ground_y, -2.0), "kinds": ["rest", "talk"]},
		}
	return {
		"workshop": {"pos": Vector3(home.x, _ground_y, home.z), "kinds": ["craft", "rest", "talk"]},
		"workbench": {"pos": Vector3(7.6, _ground_y, 1.8), "kinds": ["craft", "inspect"]},
		"furnace": {"pos": Vector3(11.0, _ground_y, -2.4), "kinds": ["craft"]},
		"crate_stack": {"pos": Vector3(11.5, _ground_y, 1.4), "kinds": ["carry", "craft"]},
		"blueprint_table": {"pos": Vector3(10.0, _ground_y, 0.6), "kinds": ["inspect", "craft"]},
		"doorway": {"pos": Vector3(7.0, _ground_y, 0.0), "kinds": ["talk", "rest"]},
		"home_plaza": {"pos": Vector3(0.0, _ground_y, 1.6), "kinds": ["talk", "rest"]},
		"market_delivery": {"pos": Vector3(10.4, _ground_y, 7.4), "kinds": ["carry", "talk"]},
		"barn_storage": {"pos": Vector3(-4.2, _ground_y, -7.6), "kinds": ["carry", "rest"]},
		"path_rest": {"pos": Vector3(2.0, _ground_y, 5.0), "kinds": ["rest", "talk"]},
	}


func _snap_to_ground(xz: Vector3) -> void:
	if _presenter == null:
		return
	_presenter.global_position = Vector3(xz.x, _ground_y + _feet_lift, xz.z)


func _process(delta: float) -> void:
	if _presenter == null or not is_instance_valid(_presenter):
		return
	if _presenter.has_method("is_built") and not bool(_presenter.call("is_built")):
		return
	if _interrupt_cooldown > 0.0:
		_interrupt_cooldown = maxf(0.0, _interrupt_cooldown - delta)
	# Lock Y to measured plant height.
	var gp := _presenter.global_position
	var want_y := _ground_y + _feet_lift
	if absf(gp.y - want_y) > 0.001:
		_presenter.global_position = Vector3(gp.x, want_y, gp.z)
	_player = _find_player()
	if _phase != Phase.PLAYER_INTERRUPT and _should_player_interrupt():
		if _phase == Phase.WALKING:
			## Cat finishes the walk first (visible locomotion); workshop can soft-pend.
			if _profile != "garden_cat":
				_interrupt_pending = true
		else:
			_begin_player_interrupt()
			return
	match _phase:
		Phase.IDLE_WORKSHOP:
			_phase_timer -= delta
			if _phase_timer <= 0.0:
				_phase = Phase.CHOOSE_DEST
				_choose_destination()
		Phase.CHOOSE_DEST:
			pass
		Phase.WALKING:
			_tick_walk(delta)
		Phase.CONTEXT_ACTION:
			_phase_timer -= delta
			if _phase_timer <= 0.0:
				_phase = Phase.CHAT_OR_RETURN
				_chat_or_return()
		Phase.CHAT_OR_RETURN:
			_phase_timer -= delta
			if _phase_timer <= 0.0:
				if _profile in ["garden_cat", "kiln_worker"]:
					## Chain another walk often — avoid long idle loops.
					if _chain_walks < 4 and _rng.randf() < 0.78:
						_chain_walks += 1
						_choose_destination()
					else:
						_chain_walks = 0
						_enter_idle_home()
				elif _is_home_dest() or _intent in ["rest", "sleep"]:
					_enter_idle_home()
				else:
					_intent = "rest"
					_dest_id = _home_dest_id()
					_dest = _home
					_start_walk_to(_dest, false)
		Phase.PLAYER_INTERRUPT:
			_phase_timer -= delta
			if _player != null:
				_face_toward(_player.global_position, delta)
			if _phase_timer <= 0.0:
				if _profile in ["garden_cat", "kiln_worker"]:
					## After greeting, walk away so user sees motion again.
					_interrupt_cooldown = CAT_INTERRUPT_COOLDOWN_S
					_chain_walks = 0
					_choose_destination()
				else:
					_enter_idle_home()


func _should_player_interrupt() -> bool:
	if _interrupt_cooldown > 0.0:
		return false
	if _player == null or not is_instance_valid(_player):
		return false
	var a := _presenter.global_position
	var b := _player.global_position
	a.y = 0.0
	b.y = 0.0
	var dist := a.distance_to(b)
	if _profile == "garden_cat":
		## Only greet when very close + not mid-walk (walks must complete).
		if _phase == Phase.WALKING:
			return false
		return dist <= CAT_INTERRUPT_DIST
	return dist <= PLAYER_INTERRUPT_DIST


func _home_dest_id() -> String:
	if _profile == "garden_cat":
		return "garden_home"
	if _profile == "kiln_worker":
		return "kiln_home"
	return "workshop"


func _is_home_dest() -> bool:
	return _dest_id in ["workshop", "garden_home", "kiln_home", "home"]


func _enter_idle_home() -> void:
	_phase = Phase.IDLE_WORKSHOP
	if _profile == "garden_cat":
		## Short pause only — then resume roam circuit.
		_idle_hold = _rng.randf_range(0.6, 1.6)
		_phase_timer = _idle_hold
		_interrupt_pending = false
		_play(_pick_random(["sniff", "happy", "scan", "idle", "sit"]))
		## Idle in place (current pos), not forced teleport home every cycle.
		_snap_to_ground(_presenter.global_position if _presenter else _home)
	elif _profile == "kiln_worker":
		_idle_hold = _rng.randf_range(1.0, 2.4)
		_phase_timer = _idle_hold
		_interrupt_pending = false
		_play(_pick_random(["idle", "cooldown", "scan", "wake_up"]))
		_snap_to_ground(_presenter.global_position if _presenter else _home)
	else:
		_idle_hold = _rng.randf_range(2.0, 5.5)
		_phase_timer = _idle_hold
		_interrupt_pending = false
		_play("idle")
		_snap_to_ground(_home)


func _choose_destination() -> void:
	_intent = _roll_intent()
	var here := _presenter.global_position if _presenter else _home
	here.y = 0.0
	var far_candidates: Array = []
	var any_candidates: Array = []
	for id in _anchors.keys():
		var row: Dictionary = _anchors[id]
		var kinds: Array = row.get("kinds", []) as Array
		## Do not always inject home — that caused zero-length walks + leaf_sway spam.
		if _intent in kinds:
			var p: Vector3 = row.get("pos", _home) as Vector3
			var d := Vector2(p.x - here.x, p.z - here.z).length()
			any_candidates.append(id)
			if d >= CAT_MIN_WALK_DIST or _profile != "garden_cat":
				far_candidates.append(id)
	var pool: Array = far_candidates if not far_candidates.is_empty() else any_candidates
	if pool.is_empty():
		pool = _anchors.keys()
	## Prefer a different anchor than last dest.
	if pool.size() > 1:
		var filtered: Array = []
		for id2 in pool:
			if str(id2) != _dest_id:
				filtered.append(id2)
		if not filtered.is_empty():
			pool = filtered
	_dest_id = str(pool[_rng.randi() % pool.size()])
	var row2: Dictionary = _anchors.get(_dest_id, {}) as Dictionary
	var p2: Vector3 = row2.get("pos", _home) as Vector3
	_dest = Vector3(p2.x, _ground_y, p2.z)
	## If still too close (edge case), nudge a random far offset for cat.
	if _profile == "garden_cat":
		var d2 := Vector2(_dest.x - here.x, _dest.z - here.z).length()
		if d2 < CAT_MIN_WALK_DIST:
			var ang := _rng.randf() * TAU
			var rad := _rng.randf_range(2.8, 4.5)
			_dest = Vector3(here.x + cos(ang) * rad, _ground_y, here.z + sin(ang) * rad)
			_dest_id = "wander_%d" % _rng.randi_range(1, 99)
	_start_walk_to(_dest, _intent == "carry")


func _roll_intent() -> String:
	var r := _rng.randf()
	var acc := 0.0
	if _profile == "garden_cat":
		acc += C_ROAM
		if r < acc:
			return "roam"
		acc += C_SNIFF
		if r < acc:
			return "sniff"
		acc += C_PLAY
		if r < acc:
			return "play"
		acc += C_REST
		if r < acc:
			return "rest"
		return "eat"
	if _profile == "kiln_worker":
		acc += K_FORGE
		if r < acc:
			return "forge"
		acc += K_STOKE
		if r < acc:
			return "stoke"
		acc += K_CARRY
		if r < acc:
			return "carry"
		acc += K_TALK
		if r < acc:
			return "talk"
		return "rest"
	acc += W_CRAFT
	if r < acc:
		return "craft"
	acc += W_INSPECT
	if r < acc:
		return "inspect"
	acc += W_CARRY
	if r < acc:
		return "carry"
	acc += W_TALK
	if r < acc:
		return "talk"
	return "rest"


func _start_walk_to(dest: Vector3, carry: bool) -> void:
	_phase = Phase.WALKING
	_dest = Vector3(dest.x, _ground_y, dest.z)
	var played := false
	if carry and _has_clip("carry_crate"):
		played = _play_bool("carry_crate")
	elif _profile == "garden_cat":
		## HARD prefer walk (leg rotation cycle in GLB) — user reported walk never used.
		## trot only as rare spice; never idle/leaf_sway while pathing.
		if _intent == "play" and _rng.randf() < 0.25:
			played = _play_bool("trot") or _play_bool("walk") or _play_bool("run")
		else:
			played = _play_bool("walk") or _play_bool("trot") or _play_bool("run")
	elif _profile == "kiln_worker":
		if carry:
			played = _play_bool("carry_crate") or _play_bool("walk")
		else:
			played = _play_bool("walk") or _play_bool("run")
	else:
		played = _play_bool("walk")
	if not played:
		_play("idle")
	if _profile in ["garden_cat", "kiln_worker"]:
		print(
			"[NpcRoam] %s walk→%s intent=%s clip=%s ok=%s"
			% [_slug if not _slug.is_empty() else _profile, _dest_id, _intent, _current_clip_hint(), played]
		)


func _current_clip_hint() -> String:
	if _presenter != null and _presenter.has_method("get_current_clip"):
		return str(_presenter.call("get_current_clip"))
	return "?"


func _tick_walk(delta: float) -> void:
	var pos := _presenter.global_position
	var to := Vector3(_dest.x - pos.x, 0.0, _dest.z - pos.z)
	var dist := to.length()
	if dist <= ARRIVE_DIST:
		_snap_to_ground(_dest)
		if _interrupt_pending and _profile != "garden_cat":
			_begin_player_interrupt()
			return
		_begin_context_action()
		return
	var step := minf(_walk_speed * delta, dist)
	var dir := to.normalized()
	_snap_to_ground(pos + dir * step)
	_face_dir(dir, delta)


func _begin_context_action() -> void:
	_phase = Phase.CONTEXT_ACTION
	var clip := _pick_context_clip()
	_play(clip)
	if _profile == "garden_cat":
		## Short beats so next walk starts quickly.
		if _is_loop_name(clip):
			_action_hold = _rng.randf_range(1.2, 2.4)
		else:
			_action_hold = _rng.randf_range(1.0, 2.2)
	elif _profile == "kiln_worker":
		if _is_loop_name(clip):
			_action_hold = _rng.randf_range(2.4, 4.0)
		else:
			_action_hold = _rng.randf_range(1.6, 3.0)
	elif _is_loop_name(clip):
		_action_hold = _rng.randf_range(3.0, 5.0)
	else:
		_action_hold = _rng.randf_range(2.0, 4.0)
	_phase_timer = _action_hold


func _pick_context_clip() -> String:
	if _profile == "garden_cat":
		## Prefer readable actions; leaf_sway only rare spice (was the only visible motion).
		match _intent:
			"roam":
				return _pick_random(["sniff", "scan", "happy", "stand", "sniff"])
			"sniff":
				return _pick_random(["sniff", "scan", "eat_leaf", "sniff"])
			"play":
				return _pick_random(["pounce", "jump", "happy", "pounce", "stand"])
			"rest":
				return _pick_random(["sit", "lie_down", "idle", "sit"])
			"eat":
				return _pick_random(["eat_leaf", "drink", "sniff", "eat_leaf"])
			"sleep":
				return _pick_random(["sleep", "lie_down", "sit"])
			_:
				return _pick_random(["sniff", "happy", "scan"])
	if _profile == "kiln_worker":
		## Use pre-authored kiln clips from Cinder_Ember_Kiln_Upgrade_v1.
		match _intent:
			"forge":
				return _pick_random(["hammer_loop", "build_place", "charge_ember", "hammer_loop"])
			"stoke":
				return _pick_random(["stoke_fire", "charge_ember", "scan", "stoke_fire"])
			"carry":
				return _pick_random(["pick_up", "put_down", "carry_crate", "pick_up"])
			"talk":
				return _pick_random(["talk_A", "talk_B", "greet", "happy"])
			"rest":
				return _pick_random(["cooldown", "idle", "shutdown", "cooldown"])
			_:
				return _pick_random(["idle", "scan", "happy"])
	match _intent:
		"craft":
			return _pick_first(["hammer_loop", "saw_loop", "sweep_loop", "repair_kneel", "build_place"])
		"inspect":
			return _pick_first(["inspect_blueprint", "scan", "happy"])
		"carry":
			return _pick_first(["pick_up", "carry_crate", "stand"])
		"talk":
			return _pick_first(["talk_A", "talk_B", "wave", "handshake"])
		"rest":
			return _pick_first(["sit", "tired_idle", "idle"])
		_:
			return "idle"


func _chat_or_return() -> void:
	if _profile == "garden_cat":
		## Rare brief flourish; usually immediately chain next walk via CHAT_OR_RETURN timer.
		if _rng.randf() < 0.18:
			_play(_pick_random(["happy", "sniff", "pet_reaction"]))
			_phase_timer = _rng.randf_range(0.8, 1.4)
		else:
			_phase_timer = 0.05
		_dest_id = "elsewhere"
		return
	if _profile == "kiln_worker":
		if _rng.randf() < 0.30 and _intent not in ["rest"]:
			_play(_pick_random(["talk_A", "talk_B", "greet", "happy"]))
			_phase_timer = _rng.randf_range(1.4, 2.6)
		else:
			_phase_timer = 0.05
		_dest_id = "elsewhere"
		return
	if _rng.randf() < 0.40 and _intent != "rest":
		_play(_pick_first(["talk_A", "talk_B", "wave", "happy"]))
		_phase_timer = _rng.randf_range(2.0, 3.5)
		_dest_id = "workshop"
	else:
		_phase_timer = 0.05
		_dest_id = "elsewhere"


func _begin_player_interrupt() -> void:
	_phase = Phase.PLAYER_INTERRUPT
	_interrupt_pending = false
	if _profile == "garden_cat":
		_play(_pick_random(["pet_reaction", "happy", "sniff", "pounce"]))
		_phase_timer = _rng.randf_range(1.6, 2.6)
	elif _profile == "kiln_worker":
		_play(_pick_random(["greet", "talk_A", "happy", "wave"]))
		_phase_timer = _rng.randf_range(2.0, 3.2)
	else:
		_play(_pick_first(["wave", "talk_A", "happy", "idle"]))
		_phase_timer = _rng.randf_range(2.5, 4.0)


func _play(clip_id: String) -> void:
	_play_bool(clip_id)


func _play_bool(clip_id: String) -> bool:
	if _presenter != null and _presenter.has_method("play_clip"):
		return bool(_presenter.call("play_clip", clip_id))
	return false


func _has_clip(clip_id: String) -> bool:
	if _presenter == null or not _presenter.has_method("get_clip_ids"):
		return true
	var ids: PackedStringArray = _presenter.call("get_clip_ids") as PackedStringArray
	for c in ids:
		if str(c).to_lower() == clip_id.to_lower():
			return true
	return false


func _pick_first(options: Array) -> String:
	for o in options:
		if _has_clip(str(o)):
			return str(o)
	return "idle"


func _pick_random(options: Array) -> String:
	var avail: Array = []
	for o in options:
		if _has_clip(str(o)):
			avail.append(str(o))
	if avail.is_empty():
		return "idle"
	return str(avail[_rng.randi() % avail.size()])


func _is_loop_name(clip_id: String) -> bool:
	var id := clip_id.to_lower()
	## leaf_sway / sniff are short beats for cat — not long "standing still" holds.
	return id.ends_with("_loop") or id in [
		"idle", "walk", "trot", "run", "tired_idle", "sit", "lie_down", "sleep",
		"carry_crate", "hammer_loop", "stoke_fire", "charge_ember",
	]


func _face_dir(dir: Vector3, delta: float) -> void:
	if dir.length_squared() < 0.0001:
		return
	var target := atan2(dir.x, dir.z) + _facing_yaw_offset
	_presenter.rotation.y = lerp_angle(
		_presenter.rotation.y, target, clampf(FACE_SPEED * delta, 0.0, 1.0)
	)


func _face_toward(world_pos: Vector3, delta: float) -> void:
	var dir := world_pos - _presenter.global_position
	dir.y = 0.0
	_face_dir(dir, delta)


func _find_player() -> Node3D:
	if _player != null and is_instance_valid(_player):
		return _player
	var tree := get_tree()
	if tree == null:
		return null
	return tree.get_first_node_in_group("player") as Node3D
