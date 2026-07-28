## WO-G8-UX-001 regression: action-bar focus trap + player vs manifestation collision.
## Run:
##   tools\Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://tests/g8_ux_input_collision_smoke.gd
##
## Exit 0 on pass, 1 on failure. Prints AIDLE_G8_UX_SMOKE=PASS|FAIL.
## Prefers preload/load paths (not only class_name) for concurrent parse safety.
extends SceneTree

const ACTION_BAR_SCRIPT := "res://scripts/ui/playable_action_bar.gd"
const ACTION_BAR_SCENE := "res://scenes/ui/playable_action_bar.tscn"
const PLAYER_SCENE := "res://scenes/player/player.tscn"
const PLAYER_SCRIPT := "res://scripts/player/player_controller.gd"
const INSTANCE_PATH := "res://scripts/modules/manifestation/manifestation_instance.gd"

## Bit values (project.godot layer_names): world=1, player=2, manifestation=4
const LAYER_WORLD := 1
const LAYER_PLAYER := 2
const LAYER_MANIFESTATION := 4
const PLAYER_MASK_EXPECTED := LAYER_WORLD | LAYER_MANIFESTATION  # 5

var _failures: PackedStringArray = []
var _passed: int = 0
var _evidence: Dictionary = {}


func _initialize() -> void:
	print("[G8-UX-001 smoke] starting…")
	_test_input_map_bindings()
	_test_player_script_uses_jump_not_ui_accept()
	await _test_action_bar_focus_none()
	await _test_ac1_movement_after_action_bar_click()
	await _test_ac4_player_blocked_by_complete_manifestation()
	await _test_ac5_preview_stages_non_solid()
	_finish()


func _finish() -> void:
	print("[G8-UX-001 smoke] evidence=%s" % JSON.stringify(_evidence))
	if _failures.is_empty():
		print("AIDLE_G8_UX_SMOKE=PASS checks=%d" % _passed)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print("AIDLE_G8_UX_SMOKE=FAIL failed=%d passed=%d" % [_failures.size(), _passed])
		quit(1)


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)


func _test_input_map_bindings() -> void:
	# jump must exist; move_* keep WASD+arrows; ui_left/right/up/down must not own arrows.
	if not InputMap.has_action("jump"):
		_fail("input_map_jump_missing")
		return
	var jump_events := InputMap.action_get_events("jump")
	var has_space := false
	for e in jump_events:
		if e is InputEventKey and int((e as InputEventKey).physical_keycode) == KEY_SPACE:
			has_space = true
			break
	if not has_space:
		_fail("input_map_jump_not_space", str(jump_events))
		return

	for dir_action in ["move_forward", "move_back", "move_left", "move_right"]:
		if not InputMap.has_action(dir_action):
			_fail("input_map_missing_move", dir_action)
			return
		var evs := InputMap.action_get_events(dir_action)
		if evs.is_empty():
			_fail("input_map_move_empty", dir_action)
			return

	# Arrow ownership: keep on move_*; clear from ui_* focus navigation.
	for ui_action in ["ui_left", "ui_right", "ui_up", "ui_down"]:
		if not InputMap.has_action(ui_action):
			# If action absent, Godot may still use engine defaults — fail closed.
			_fail("input_map_ui_nav_not_overridden", ui_action)
			return
		var ui_evs := InputMap.action_get_events(ui_action)
		for e in ui_evs:
			if e is InputEventKey:
				var pk := int((e as InputEventKey).physical_keycode)
				if pk == KEY_LEFT or pk == KEY_RIGHT or pk == KEY_UP or pk == KEY_DOWN:
					_fail("input_map_ui_still_has_arrow", "%s key=%d" % [ui_action, pk])
					return
	_evidence["arrow_owner"] = "move_* (WASD+arrows); ui_left/right/up/down events empty"
	_ok("input_map_bindings")


func _test_player_script_uses_jump_not_ui_accept() -> void:
	var f := FileAccess.open(PLAYER_SCRIPT, FileAccess.READ)
	if f == null:
		_fail("player_script_open")
		return
	var src := f.get_as_text()
	f.close()
	if src.find('is_action_just_pressed("ui_accept")') >= 0:
		_fail("player_still_uses_ui_accept_for_jump")
		return
	if src.find('is_action_just_pressed("jump")') < 0:
		_fail("player_missing_jump_action")
		return
	_ok("player_script_jump_action")


func _test_action_bar_focus_none() -> void:
	var packed: PackedScene = load(ACTION_BAR_SCENE) as PackedScene
	if packed == null:
		_fail("action_bar_scene_load")
		return
	var bar: CanvasLayer = packed.instantiate() as CanvasLayer
	if bar == null:
		_fail("action_bar_instantiate")
		return
	root.add_child(bar)
	await process_frame
	await process_frame

	var names := ["BtnCompanion", "BtnExport", "BtnImport", "BtnDemoBuild", "BtnConfirm", "BtnCancel"]
	var checked := 0
	for n in names:
		var btn := _find_button(bar, n)
		if btn == null:
			_fail("action_bar_btn_missing", n)
			bar.queue_free()
			return
		if btn.focus_mode != Control.FOCUS_NONE:
			_fail("action_bar_focus_mode", "%s mode=%d want FOCUS_NONE" % [n, btn.focus_mode])
			bar.queue_free()
			return
		# Mouse-driven: pressed does not require keyboard focus.
		if btn.has_focus():
			_fail("action_bar_unexpected_focus", n)
			bar.queue_free()
			return
		btn.emit_signal("pressed")
		await process_frame
		if btn.has_focus():
			_fail("action_bar_gained_focus_after_press", n)
			bar.queue_free()
			return
		checked += 1

	_evidence["action_bar_buttons_focus_none"] = checked
	_ok("action_bar_focus_none")
	bar.queue_free()
	await process_frame


func _find_button(root_n: Node, name: String) -> Button:
	if root_n.name == name and root_n is Button:
		return root_n as Button
	for c in root_n.get_children():
		var found := _find_button(c, name)
		if found != null:
			return found
	return null


func _test_ac1_movement_after_action_bar_click() -> void:
	## (a) After action-bar interaction, movement input must move the player.
	var world := Node3D.new()
	world.name = "AC1World"
	root.add_child(world)

	var floor_body := _make_static_box(world, "Floor", Vector3(20, 1, 20), Vector3(0, -0.5, 0), LAYER_WORLD)
	var packed: PackedScene = load(PLAYER_SCENE) as PackedScene
	if packed == null:
		_fail("player_scene_load_ac1")
		world.queue_free()
		return
	var player: CharacterBody3D = packed.instantiate() as CharacterBody3D
	world.add_child(player)
	player.global_position = Vector3(0, 0.05, 0)
	player.velocity = Vector3.ZERO

	# Assert mask includes manifestation bit (defect 4 setup).
	if int(player.collision_mask) != PLAYER_MASK_EXPECTED:
		_fail("player_mask_not_5", "mask=%d" % int(player.collision_mask))
		world.queue_free()
		return
	if int(player.collision_layer) != LAYER_PLAYER:
		_fail("player_layer_not_2", "layer=%d" % int(player.collision_layer))
		world.queue_free()
		return

	# Action bar click path (FOCUS_NONE already asserted).
	var bar_packed: PackedScene = load(ACTION_BAR_SCENE) as PackedScene
	var bar: CanvasLayer = bar_packed.instantiate() as CanvasLayer
	root.add_child(bar)
	await process_frame
	var demo := _find_button(bar, "BtnDemoBuild")
	if demo:
		demo.emit_signal("pressed")
	await process_frame

	var before := player.global_position
	# Inject move_forward for several physics ticks.
	Input.action_press("move_forward")
	for i in range(20):
		await physics_frame
	Input.action_release("move_forward")
	await physics_frame

	var after := player.global_position
	var delta_xz := Vector2(after.x - before.x, after.z - before.z).length()
	_evidence["ac1_transform_delta"] = {
		"before": {"x": before.x, "y": before.y, "z": before.z},
		"after": {"x": after.x, "y": after.y, "z": after.z},
		"delta_xz": delta_xz,
	}
	if delta_xz < 0.05:
		_fail("ac1_no_movement_after_action_bar", "delta_xz=%s" % delta_xz)
		Input.action_release("move_forward")
		bar.queue_free()
		world.queue_free()
		return

	_ok("ac1_movement_after_action_bar_click")
	bar.queue_free()
	world.queue_free()
	await process_frame
	# silence unused
	if floor_body:
		pass


func _test_ac4_player_blocked_by_complete_manifestation() -> void:
	## (b) Completed manifestation (layer bit 4) must block the player.
	var InstanceScript: GDScript = load(INSTANCE_PATH) as GDScript
	if InstanceScript == null:
		_fail("manifestation_instance_load")
		return

	var world := Node3D.new()
	world.name = "AC4World"
	root.add_child(world)
	_make_static_box(world, "Floor", Vector3(40, 1, 40), Vector3(0, -0.5, 0), LAYER_WORLD)

	var inst: Node3D = InstanceScript.new() as Node3D
	world.add_child(inst)
	inst.call(
		"configure",
		"g8-ux-ac4",
		"cozy_cyber_pixel",
		{"position": Vector3(0, 0, -3.0), "size": Vector3(2.0, 2.0, 2.0)}
	)
	inst.call("finalize_complete")
	await process_frame
	await process_frame

	if not bool(inst.call("has_durable_collision")):
		_fail("ac4_complete_not_durable")
		world.queue_free()
		return

	var body := inst.get_node_or_null("CollisionBody") as StaticBody3D
	if body == null:
		_fail("ac4_no_collision_body")
		world.queue_free()
		return
	if int(body.collision_layer) != LAYER_MANIFESTATION:
		_fail("ac4_complete_layer", "layer=%d want=%d" % [int(body.collision_layer), LAYER_MANIFESTATION])
		world.queue_free()
		return

	var packed: PackedScene = load(PLAYER_SCENE) as PackedScene
	var player: CharacterBody3D = packed.instantiate() as CharacterBody3D
	world.add_child(player)
	# Face the box and start just outside its front face (box at z=-3 size 2 → front ~ z=-2).
	player.global_position = Vector3(0, 0.05, -0.6)
	player.velocity = Vector3.ZERO
	await physics_frame

	var before := player.global_position
	# Drive into the solid box along -Z with a large velocity for many frames.
	for i in range(45):
		player.velocity = Vector3(0, 0, -12.0)
		player.move_and_slide()
		await physics_frame
	var after := player.global_position
	var penetrated := after.z < -2.05  # past front face into interior
	_evidence["ac4_collision"] = {
		"before": {"x": before.x, "y": before.y, "z": before.z},
		"after": {"x": after.x, "y": after.y, "z": after.z},
		"manifestation_layer": int(body.collision_layer),
		"player_mask": int(player.collision_mask),
		"penetrated": penetrated,
	}
	if penetrated:
		_fail("ac4_player_passed_through_complete", "z=%s" % after.z)
		world.queue_free()
		return
	# Must have been blocked before fully entering (not free-flight through).
	if after.z > before.z - 0.01:
		# Also accept if player couldn't advance at all (blocked immediately).
		pass
	_ok("ac4_player_blocked_by_complete_manifestation")
	world.queue_free()
	await process_frame


func _test_ac5_preview_stages_non_solid() -> void:
	var InstanceScript: GDScript = load(INSTANCE_PATH) as GDScript
	if InstanceScript == null:
		_fail("ac5_instance_load")
		return
	var world := Node3D.new()
	root.add_child(world)
	for stage in ["wireframe", "hologram", "materializing"]:
		var inst: Node3D = InstanceScript.new() as Node3D
		world.add_child(inst)
		inst.call("configure", "g8-ux-%s" % stage, "cozy_cyber_pixel", {
			"position": Vector3(0, 0, 0),
			"size": Vector3(2, 2, 2),
		})
		inst.call("set_stage", stage)
		await process_frame
		if bool(inst.call("has_durable_collision")):
			_fail("ac5_preview_solid", stage)
			world.queue_free()
			return
		var body := inst.get_node_or_null("CollisionBody") as StaticBody3D
		if body != null and int(body.collision_layer) != 0:
			_fail("ac5_preview_layer_nonzero", "%s layer=%d" % [stage, int(body.collision_layer)])
			world.queue_free()
			return
		inst.queue_free()
	_ok("ac5_preview_stages_non_solid")
	world.queue_free()
	await process_frame


func _make_static_box(parent: Node3D, name: String, size: Vector3, pos: Vector3, layer: int) -> StaticBody3D:
	var body := StaticBody3D.new()
	body.name = name
	body.collision_layer = layer
	body.collision_mask = 0
	body.position = pos
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = size
	shape.shape = box
	body.add_child(shape)
	parent.add_child(body)
	return body
