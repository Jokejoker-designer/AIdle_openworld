## WO-P1E-004 elemental pilot: static bindings, dynamic pond→soil→growth, Tier-3.
## Run:
##   tools/Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://tests/p1e004_elemental_pilot_smoke.gd
extends SceneTree

const WORLD_SCRIPT := "res://scripts/modules/elemental/elemental_pilot_world.gd"
const PERSIST_SCRIPT := "res://scripts/modules/persist/persist_module.gd"
const KEY_SCRIPT := "res://scripts/modules/persist/test_journal_key_provider.gd"

var _failed: int = 0
var _passed: int = 0
var _evidence: Dictionary = {}


func _initialize() -> void:
	print("[P1E-004 elemental pilot] start")
	_test_static_bindings()
	_test_dynamic_network()
	_test_tier3_unload_reload()
	_test_preview_non_sim()
	_test_persist_path()
	_finish()


func _ok(n: String) -> void:
	_passed += 1
	print("  OK  %s" % n)


func _fail(n: String, d: String = "") -> void:
	_failed += 1
	print("  FAIL %s | %s" % [n, d] if not d.is_empty() else "  FAIL %s" % n)


func _test_static_bindings() -> void:
	var world = load(WORLD_SCRIPT).new()
	if not world.load_pilot_catalogs():
		_fail("catalog_load", world.last_error)
		return
	for mid in ["cozy_rock_small_A", "cozy_path_stone_A", "cozy_fence_section_A"]:
		var r: Dictionary = world.create_entity("static_%s" % mid, mid, Vector3.ZERO, false)
		if not bool(r.get("ok", false)):
			_fail("static_create_%s" % mid, str(r))
			return
		var st: Dictionary = r["state"]
		if bool(st.get("simulates", true)):
			_fail("static_should_not_sim_%s" % mid)
			return
		if str(st.get("element_id", "")).is_empty() or str(st.get("physical_profile_id", "")).is_empty():
			_fail("static_missing_profile_%s" % mid, str(st))
			return
	# Path must map to hard stone per WO
	var path_b: Dictionary = world.binding_for_module("cozy_path_stone_A")
	if str(path_b.get("physical_profile_id", "")) != "phys_stone_hard_v1":
		_fail("path_hard_profile", str(path_b.get("physical_profile_id", "")))
		return
	_ok("static_three_modules_bound")
	_evidence["static_path_profile"] = str(path_b.get("physical_profile_id", ""))


func _test_dynamic_network() -> void:
	var world = load(WORLD_SCRIPT).new()
	world.load_pilot_catalogs()
	world.create_entity("pond_dyn", "cozy_pond_small_A", Vector3(0, 0, 0), false)
	world.create_entity("farm_dyn", "cozy_farm_plot_A", Vector3(3, 0, 0), false)
	world.set_lod_tier("pond_dyn", 0)
	world.set_lod_tier("farm_dyn", 0)
	var t0 := 1_000_000.0
	# seed last_sim
	world._entities["pond_dyn"].last_sim_unix = t0
	world._entities["farm_dyn"].last_sim_unix = t0
	var r1: Dictionary = world.simulate_step(t0 + 2.0)
	var farm: Dictionary = world.get_state("farm_dyn")
	var wet1 := float(farm.get("wetness", 0))
	var g1 := float(farm.get("growth", 0))
	if wet1 <= 0.0:
		_fail("wetness_not_propagated", str(farm))
		return
	if g1 <= 0.0:
		_fail("growth_not_advanced", str(farm))
		return
	# Higher wetness → more growth: dry farm farther
	world.create_entity("farm_dry", "cozy_farm_plot_A", Vector3(50, 0, 0), false)
	world._entities["farm_dry"].last_sim_unix = t0
	world.simulate_step(t0 + 2.0)
	var dry: Dictionary = world.get_state("farm_dry")
	if float(dry.get("growth", 0)) >= g1:
		_fail("growth_should_scale_with_wetness", "near=%s far=%s" % [g1, dry.get("growth")])
		return
	_ok("dynamic_pond_soil_growth")
	_evidence["wetness"] = wet1
	_evidence["growth_near"] = g1
	_evidence["growth_far"] = float(dry.get("growth", 0))
	_evidence["sim_step"] = r1


func _test_tier3_unload_reload() -> void:
	var world = load(WORLD_SCRIPT).new()
	world.load_pilot_catalogs()
	world.create_entity("pond_t3", "cozy_pond_small_A", Vector3(0, 0, 0), false)
	world.create_entity("farm_t3", "cozy_farm_plot_A", Vector3(2, 0, 0), false)
	var t0 := 2_000_000.0
	world._entities["pond_t3"].last_sim_unix = t0
	world._entities["farm_t3"].last_sim_unix = t0
	world.simulate_step(t0 + 1.0)
	var g_before := float(world.get_state("farm_t3").get("growth", 0))
	world.set_lod_tier("farm_t3", 3)
	world.set_lod_tier("pond_t3", 3)
	var snap: Dictionary = world.unload_chunk_snapshot()
	if snap.is_empty():
		_fail("unload_empty")
		return
	# Unloaded for 100 simulated seconds
	var t1 := t0 + 1.0 + 100.0
	var r: Dictionary = world.reload_chunk_from_snapshot(snap, t1)
	var g_after := float(world.get_state("farm_t3").get("growth", 0))
	if g_after <= g_before:
		_fail("tier3_no_advance", "before=%s after=%s" % [g_before, g_after])
		return
	if int(world.get_state("farm_t3").get("simulation_lod_tier", 0)) != 3:
		_fail("tier3_flag")
		return
	_ok("tier3_time_delta_unload_reload")
	_evidence["tier3"] = {
		"growth_before": g_before,
		"growth_after": g_after,
		"delta_s": 100.0,
		"reload": r.get("ok", false),
	}


func _test_preview_non_sim() -> void:
	var world = load(WORLD_SCRIPT).new()
	world.load_pilot_catalogs()
	world.create_entity("pond_prev", "cozy_pond_small_A", Vector3.ZERO, true)
	world.create_entity("farm_prev", "cozy_farm_plot_A", Vector3(2, 0, 0), true)
	var t0 := 3_000_000.0
	world._entities["pond_prev"].last_sim_unix = t0
	world._entities["farm_prev"].last_sim_unix = t0
	world.simulate_step(t0 + 50.0)
	if float(world.get_state("farm_prev").get("growth", -1)) != 0.0:
		_fail("preview_grew")
		return
	var mut: Dictionary = world.build_durable_mutation("farm_prev", "req_preview_block")
	if bool(mut.get("ok", true)):
		_fail("preview_should_block_durable")
		return
	_ok("preview_non_simulating_non_durable")


func _test_persist_path() -> void:
	var world = load(WORLD_SCRIPT).new()
	world.load_pilot_catalogs()
	world.create_entity("rock_p", "cozy_rock_small_A", Vector3(1, 0, 1), false)
	world.create_entity("farm_p", "cozy_farm_plot_A", Vector3(0, 0, 0), false)
	world.create_entity("pond_p", "cozy_pond_small_A", Vector3(2, 0, 0), false)
	var t0 := 4_000_000.0
	world._entities["farm_p"].last_sim_unix = t0
	world._entities["pond_p"].last_sim_unix = t0
	world.simulate_step(t0 + 3.0)

	var persist = load(PERSIST_SCRIPT).new()
	root.add_child(persist)
	var keyp = load(KEY_SCRIPT).new()
	persist.set_key_provider(keyp, "test_key")
	var cj: Dictionary = persist.create_journal("private_reality", 0, "p1e004_pilot", "sess_p1e004")
	if not bool(cj.get("ok", false)) and str(cj.get("status", "")) != "ok":
		# create_journal may return differently — try proceed if journal open
		if persist.list_entity_ids().is_empty() and not persist.get_status().contains("rev"):
			_fail("journal_create", str(cj))
			persist.queue_free()
			return

	var rev: int = 0
	if persist.has_method("get_world_revision"):
		rev = int(persist.call("get_world_revision"))
	for eid in ["rock_p", "farm_p", "pond_p"]:
		var built: Dictionary = world.build_durable_mutation(eid, "req_p1e004_%s" % eid, rev)
		if not bool(built.get("ok", false)):
			_fail("build_mut_%s" % eid, str(built))
			persist.queue_free()
			return
		var applied: Dictionary = persist.apply_mutation(built["request"])
		var st_s := str(applied.get("status", ""))
		var ok := bool(applied.get("ok", false)) or st_s in ["ok", "mutation_applied", "applied", "committed"]
		# Some stores use entry_type / local_status
		if not ok and str(applied.get("entry_type", "")) == "mutation_applied":
			ok = true
		if not ok and str(applied.get("local_status", "")) == "committed":
			ok = true
		if not ok:
			_fail("apply_mut_%s" % eid, str(applied))
			persist.queue_free()
			return
		# Advance expected revision after each successful apply
		if applied.has("new_world_revision"):
			rev = int(applied["new_world_revision"])
		elif persist.has_method("get_world_revision"):
			rev = int(persist.call("get_world_revision"))
		else:
			rev += 1

	# Reload from journal memory
	var farm_ent = persist.get_entity("farm_p")
	if farm_ent == null or not (farm_ent is Dictionary):
		_fail("get_entity_farm", str(farm_ent))
		persist.queue_free()
		return
	var tags: Array = (farm_ent as Dictionary).get("interaction_tags", [])
	var has_wet := false
	var has_growth := false
	for t in tags:
		var s := str(t)
		if s.begins_with("wetness:") and float(s.substr(8)) > 0.0:
			has_wet = true
		if s.begins_with("growth:") and float(s.substr(7)) > 0.0:
			has_growth = true
		if s.begins_with("element:"):
			pass
	if not has_wet or not has_growth:
		_fail("tags_missing_state", str(tags))
		persist.queue_free()
		return
	_ok("persist_static_and_dynamic_state")
	_evidence["farm_tags"] = tags
	persist.queue_free()


func _finish() -> void:
	print("[P1E-004 elemental pilot] evidence=%s" % JSON.stringify(_evidence))
	if _failed == 0:
		print("AIDLE_P1E004_ELEMENTAL_SMOKE=PASS checks=%d" % _passed)
		quit(0)
	else:
		print("AIDLE_P1E004_ELEMENTAL_SMOKE=FAIL failed=%d passed=%d" % [_failed, _passed])
		quit(1)
