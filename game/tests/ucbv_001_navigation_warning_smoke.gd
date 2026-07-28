## UCBV-001 C3-F01 — navigation bake source + voxel-alignment smoke (offline).
## Asserts collision/procedural CPU source (no MeshInstance3D/PlaneMesh) and
## exact cell/agent integral ratios. Does not fake or filter engine warnings.
## Run:
##   tools/Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://tests/ucbv_001_navigation_warning_smoke.gd
extends SceneTree

const _Builder = preload("res://scripts/modules/asset/glb_intake_runtime_builder.gd")

const CELL_SIZE := 0.2
const CELL_HEIGHT := 0.2
const AGENT_RADIUS := 0.4
const AGENT_HEIGHT := 1.6

var _failures: PackedStringArray = []
var _passed: int = 0


func _initialize() -> void:
	print("[UCBV-001 C3F01 nav warning smoke] starting…")
	_run()
	_finish()


func _run() -> void:
	var builder = _Builder.new()
	# Parent in-tree so map voxel align path exercises product runtime order.
	var host := Node3D.new()
	host.name = "NavSmokeHost"
	root.add_child(host)

	var realm := Node3D.new()
	realm.name = "StarterRealm"
	host.add_child(realm)

	var ok := bool(builder.call("bake_navigation", realm, null))
	if not ok:
		_fail("bake_navigation", "returned false")
		return
	_ok("bake_navigation_true")

	var region := realm.get_node_or_null("NavigationRegion") as NavigationRegion3D
	if region == null:
		_fail("NavigationRegion", "missing under realm")
		return
	_ok("NavigationRegion_present")

	# No legacy MeshInstance3D + PlaneMesh source.
	if region.get_node_or_null("NavSourcePlane") != null:
		_fail("no_MeshInstance_source", "NavSourcePlane still present")
	else:
		_ok("no_NavSourcePlane_MeshInstance")

	for c in region.get_children():
		if c is MeshInstance3D:
			_fail("no_MeshInstance_source", "MeshInstance3D child under NavigationRegion: %s" % c.name)
			return
	_ok("no_MeshInstance3D_under_region")

	# Collision-shape source contract.
	var collider := region.get_node_or_null("NavSourceCollider") as StaticBody3D
	if collider == null:
		_fail("NavSourceCollider", "missing StaticBody3D source")
		return
	var shape_ok := false
	for c in collider.get_children():
		if c is CollisionShape3D and (c as CollisionShape3D).shape is BoxShape3D:
			shape_ok = true
			break
	if not shape_ok:
		_fail("NavSourceCollider", "missing CollisionShape3D+BoxShape3D")
		return
	_ok("collision_shape_source_present")

	var nm := region.navigation_mesh
	if nm == null:
		_fail("navigation_mesh", "null after bake")
		return

	if nm.geometry_parsed_geometry_type != NavigationMesh.PARSED_GEOMETRY_STATIC_COLLIDERS:
		_fail(
			"parsed_geometry_type",
			"expected STATIC_COLLIDERS got %s" % str(nm.geometry_parsed_geometry_type)
		)
	else:
		_ok("parsed_geometry_static_colliders")

	if not is_equal_approx(nm.cell_size, CELL_SIZE):
		_fail("cell_size", "got %s want %s" % [str(nm.cell_size), str(CELL_SIZE)])
	else:
		_ok("cell_size_0_2")

	if not is_equal_approx(nm.cell_height, CELL_HEIGHT):
		_fail("cell_height", "got %s want %s" % [str(nm.cell_height), str(CELL_HEIGHT)])
	else:
		_ok("cell_height_0_2")

	if not is_equal_approx(nm.agent_radius, AGENT_RADIUS):
		_fail("agent_radius", "got %s want %s" % [str(nm.agent_radius), str(AGENT_RADIUS)])
	else:
		_ok("agent_radius_0_4")

	if not is_equal_approx(nm.agent_height, AGENT_HEIGHT):
		_fail("agent_height", "got %s want %s" % [str(nm.agent_height), str(AGENT_HEIGHT)])
	else:
		_ok("agent_height_1_6")

	# Integral voxel ratios (precision-loss condition that triggers engine warnings).
	var radius_voxels := nm.agent_radius / nm.cell_size
	var height_voxels := nm.agent_height / nm.cell_height
	if not is_equal_approx(radius_voxels, roundf(radius_voxels)):
		_fail("agent_radius_voxel_integral", "radius/cell_size=%s" % str(radius_voxels))
	else:
		_ok("agent_radius_voxel_integral")
	if not is_equal_approx(height_voxels, roundf(height_voxels)):
		_fail("agent_height_voxel_integral", "height/cell_height=%s" % str(height_voxels))
	else:
		_ok("agent_height_voxel_integral")

	if region.has_meta("nav_source_type"):
		var st := str(region.get_meta("nav_source_type"))
		if st != "procedural_cpu_faces":
			_fail("nav_source_type", "got %s" % st)
		else:
			_ok("nav_source_type_procedural_cpu_faces")
	else:
		_fail("nav_source_type", "meta missing")

	if nm.get_polygon_count() <= 0:
		_fail("bake_polygons", "polygon_count=0")
	else:
		_ok("bake_polygons_gt_0")

	# 48m coverage intent: source box spans ±24m.
	var covered := false
	for c in collider.get_children():
		if c is CollisionShape3D and (c as CollisionShape3D).shape is BoxShape3D:
			var b := (c as CollisionShape3D).shape as BoxShape3D
			if b.size.x >= 47.9 and b.size.z >= 47.9:
				covered = true
	if not covered:
		_fail("ground_48m", "collider footprint < 48m")
	else:
		_ok("ground_48m_coverage")

	if bool(realm.get_meta("navigation_baked", false)):
		_ok("navigation_baked_meta")
	else:
		_fail("navigation_baked_meta", "false")

	if is_instance_valid(host):
		host.queue_free()


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	var msg := label if detail.is_empty() else "%s: %s" % [label, detail]
	_failures.append(msg)
	printerr("[FAIL] %s" % msg)


func _finish() -> void:
	if _failures.is_empty():
		print("AIDLE_UCBV001_NAVIGATION_WARNING_SMOKE=PASS checks=%d" % _passed)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print(
			"AIDLE_UCBV001_NAVIGATION_WARNING_SMOKE=FAIL failed=%d passed=%d"
			% [_failures.size(), _passed]
		)
		quit(1)
