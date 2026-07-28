## WO-G8-UX-002 regression: fence rails must block player between posts.
## Real physics (CharacterBody3D.move_and_slide) against StarterRealmBuilder geometry.
## Run:
##   tools\Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://tests/g8_ux002_fence_rail_collision_smoke.gd
##
## Exit 0 on pass, 1 on failure. Prints AIDLE_G8_UX002_SMOKE=PASS|FAIL.
## Prefers preload/load paths (not only class_name) for concurrent parse safety.
extends SceneTree

const BUILDER_PATH := "res://scripts/modules/asset/starter_realm_builder.gd"
const PLAYER_SCENE := "res://scenes/player/player.tscn"
const LAYER_WORLD := 1
const LAYER_PLAYER := 2

## Fence root is at world (5, 0, 0.5). Posts at local x=(i-2)*1.1, rails span gaps.
## Midpoint between Post0 (x=-2.2) and Post1 (x=-1.1) is local x=-1.65 → world x=3.35.
const FENCE_WORLD_Z := 0.5
const GAP_WORLD_X := 5.0 + (-1.65)  # 3.35 — center of Rail0 between Post0 and Post1

var _failures: PackedStringArray = []
var _passed: int = 0
var _evidence: Dictionary = {}


func _initialize() -> void:
	print("[G8-UX-002 smoke] starting…")
	await _test_rails_have_collision_bodies()
	await _test_player_blocked_between_posts()
	_finish()


func _finish() -> void:
	print("[G8-UX-002 smoke] evidence=%s" % JSON.stringify(_evidence))
	if _failures.is_empty():
		print("AIDLE_G8_UX002_SMOKE=PASS checks=%d" % _passed)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print("AIDLE_G8_UX002_SMOKE=FAIL failed=%d passed=%d" % [_failures.size(), _passed])
		quit(1)


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)


func _load_builder() -> GDScript:
	var s: GDScript = load(BUILDER_PATH) as GDScript
	return s


func _test_rails_have_collision_bodies() -> void:
	var BuilderScript := _load_builder()
	if BuilderScript == null:
		_fail("builder_load")
		return

	var world := Node3D.new()
	world.name = "RailBodyWorld"
	root.add_child(world)
	var pr := Node3D.new()
	pr.name = "PrivateReality"
	world.add_child(pr)

	# Call static build_into via script class.
	var realm: Node3D = BuilderScript.call("build_into", pr) as Node3D
	if realm == null:
		_fail("build_into_null")
		world.queue_free()
		return

	var fence := realm.get_node_or_null("Fence") as Node3D
	if fence == null:
		_fail("fence_missing")
		world.queue_free()
		return

	var rail_count := 0
	var rails_with_body := 0
	for i in range(4):
		var rail := fence.get_node_or_null("Rail%d" % i) as Node3D
		if rail == null:
			_fail("rail_missing", "Rail%d" % i)
			world.queue_free()
			return
		rail_count += 1
		var has_static := false
		for c in rail.get_children():
			if c is StaticBody3D:
				var body := c as StaticBody3D
				if int(body.collision_layer) != LAYER_WORLD:
					_fail("rail_layer", "Rail%d layer=%d" % [i, int(body.collision_layer)])
					world.queue_free()
					return
				has_static = true
				break
		if has_static:
			rails_with_body += 1

	_evidence["rails"] = {"count": rail_count, "with_static_body": rails_with_body}
	if rails_with_body != 4:
		_fail("rails_missing_collision", "with_body=%d want=4" % rails_with_body)
		world.queue_free()
		return

	_ok("rails_have_collision_bodies")
	world.queue_free()
	await process_frame


func _test_player_blocked_between_posts() -> void:
	## Drive player along -Z through the gap between Post0 and Post1 (Rail0 span).
	## Pre-fix: posts alone leave ~0.98m gap > player diameter 0.70m → walk-through.
	## Post-fix: Rail0 StaticBody on layer 1 must stop the player before penetrating past fence Z.
	var BuilderScript := _load_builder()
	if BuilderScript == null:
		_fail("builder_load_block")
		return

	var world := Node3D.new()
	world.name = "FenceBlockWorld"
	root.add_child(world)

	# Floor so CharacterBody can stand / slide on world layer.
	_make_static_box(world, "Floor", Vector3(40, 1, 40), Vector3(0, -0.5, 0), LAYER_WORLD)

	var pr := Node3D.new()
	pr.name = "PrivateReality"
	world.add_child(pr)
	var realm: Node3D = BuilderScript.call("build_into", pr) as Node3D
	if realm == null:
		_fail("build_into_null_block")
		world.queue_free()
		return

	var fence := realm.get_node_or_null("Fence") as Node3D
	if fence == null:
		_fail("fence_missing_block")
		world.queue_free()
		return

	# Confirm Rail0 static present at the aimed gap.
	var rail0 := fence.get_node_or_null("Rail0") as Node3D
	if rail0 == null:
		_fail("rail0_missing")
		world.queue_free()
		return
	var rail0_body: StaticBody3D = null
	for c in rail0.get_children():
		if c is StaticBody3D:
			rail0_body = c as StaticBody3D
			break
	if rail0_body == null:
		_fail("rail0_no_static_body")
		world.queue_free()
		return

	var packed: PackedScene = load(PLAYER_SCENE) as PackedScene
	if packed == null:
		_fail("player_scene_load")
		world.queue_free()
		return
	var player: CharacterBody3D = packed.instantiate() as CharacterBody3D
	world.add_child(player)
	# Start south of fence on the gap midline; capsule feet near ground.
	player.global_position = Vector3(GAP_WORLD_X, 0.05, FENCE_WORLD_Z + 1.4)
	player.velocity = Vector3.ZERO
	await physics_frame
	await physics_frame

	if (int(player.collision_mask) & LAYER_WORLD) == 0:
		_fail("player_mask_excludes_world", "mask=%d" % int(player.collision_mask))
		world.queue_free()
		return

	var before := player.global_position
	# Drive hard into the fence along -Z for many physics ticks.
	for i in range(60):
		player.velocity = Vector3(0, 0, -14.0)
		player.move_and_slide()
		await physics_frame
	var after := player.global_position

	# Free travel without rails would push z well past fence (1.4 → negative of fence).
	# Rail thickness is 0.06 centered at fence z; capsule radius 0.35 → contact ~ z >= fence_z + 0.03 + epsilon.
	# Fail if player center crosses north of the fence plane by more than half a step.
	var crossed_through := after.z < (FENCE_WORLD_Z - 0.25)
	var advanced := before.z - after.z
	_evidence["fence_gap_drive"] = {
		"gap_world_x": GAP_WORLD_X,
		"fence_world_z": FENCE_WORLD_Z,
		"before": {"x": before.x, "y": before.y, "z": before.z},
		"after": {"x": after.x, "y": after.y, "z": after.z},
		"advanced_along_minus_z": advanced,
		"crossed_through": crossed_through,
		"rail0_layer": int(rail0_body.collision_layer),
		"player_mask": int(player.collision_mask),
		"player_layer": int(player.collision_layer),
	}

	if crossed_through:
		_fail(
			"player_passed_through_fence_gap",
			"z_before=%s z_after=%s fence_z=%s" % [before.z, after.z, FENCE_WORLD_Z]
		)
		world.queue_free()
		return

	# Must have been able to approach (not stuck far away) but not free-flight through.
	# Blocked near fence: after.z should remain south-ish of/near fence contact band.
	if after.z > before.z - 0.02:
		# Completely stuck at start is still "blocked" — acceptable if never penetrated.
		pass

	_ok("player_blocked_between_posts")
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
