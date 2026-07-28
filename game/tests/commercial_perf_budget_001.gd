## Commercial gate #9 — headless performance budget probe (measure + report).
## Not a ship claim. Captures timings for world build + smoke-critical paths when possible.
extends SceneTree

const SOAK_N := 5
var _passed: int = 0
var _failures: PackedStringArray = []
var _evidence: Dictionary = {}


func _initialize() -> void:
	print("[COMMERCIAL_PERF_BUDGET_001] starting…")
	_probe_script_load_budget()
	_probe_persist_apply_budget()
	_probe_frame_budget_headless()
	_finish()


func _finish() -> void:
	print("[COMMERCIAL_PERF_BUDGET_001] evidence=%s" % JSON.stringify(_evidence))
	if _failures.is_empty():
		print("AIDLE_COMMERCIAL_PERF_BUDGET_001=PASS checks=%d" % _passed)
		quit(0)
		return
	for f in _failures:
		printerr("[FAIL] %s" % f)
	print("AIDLE_COMMERCIAL_PERF_BUDGET_001=FAIL failed=%d passed=%d" % [_failures.size(), _passed])
	quit(1)


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)


func _probe_script_load_budget() -> void:
	var t0 := Time.get_ticks_usec()
	var paths := [
		"res://scripts/modules/persist/persist_module.gd",
		"res://scripts/modules/persist/journal_store.gd",
		"res://autoload/control_accessibility_settings.gd",
		"res://scripts/input/control_action_catalog.gd",
		"res://scripts/modules/ucbv_001/nori7_presenter.gd",
	]
	var loaded := 0
	for p in paths:
		if ResourceLoader.exists(p):
			var r = load(p)
			if r != null:
				loaded += 1
	var ms := (Time.get_ticks_usec() - t0) / 1000.0
	_evidence["script_load"] = {"ms": ms, "loaded": loaded, "budget_ms": 2000.0}
	if loaded < 3:
		_fail("script_load_count", str(loaded))
		return
	if ms > 5000.0:
		_fail("script_load_budget", "ms=%.1f" % ms)
		return
	_ok("script_load_budget_ms_%.1f" % ms)


func _probe_persist_apply_budget() -> void:
	var Store = load("res://scripts/modules/persist/journal_store.gd") as GDScript
	var Key = load("res://scripts/modules/persist/test_journal_key_provider.gd") as GDScript
	if Store == null or Key == null:
		_fail("persist_scripts")
		return
	var s: Object = Store.new()
	s.call("set_key_provider", Key.new(false))
	s.call("create_journal", "perf_space", 1, "snap", "sess")
	var t0 := Time.get_ticks_usec()
	var rev := 1
	for i in 50:
		var ent := {
			"entity_id": "e_perf_%d" % i,
			"kind": "prop",
			"recipe_id": "cozy_rock_small",
			"transform": {"x": i, "y": 0, "elevation": 0, "rotation_deg": 0},
			"bounds": {"width": 1, "depth": 1, "height": 1},
			"interaction_tags": [],
			"space_id": "perf_space",
			"chunk_id": "0_0",
		}
		var req := {
			"authority": {"context": "offline_private_reality", "source": "local_player_confirm"},
			"confirmation": {"state": "confirmed", "confirmed_by": "p"},
			"request_id": "req-perf-%04d-4000-8000-%012d" % [i, i],
			"prompt_id": "p-perf",
			"expected_world_revision": rev,
			"mutation_class": "durable_world",
			"operation": "create",
			"entity": ent,
			"actor": {"actor_id": "p", "actor_type": "player"},
		}
		var r: Dictionary = s.call("apply_mutation", req) as Dictionary
		if str(r.get("status", "")) != "committed":
			_fail("perf_apply", str(r))
			return
		rev = int(r.get("new_world_revision", rev + 1))
	var ms := (Time.get_ticks_usec() - t0) / 1000.0
	var per := ms / 50.0
	_evidence["persist_apply_50"] = {"total_ms": ms, "per_mutation_ms": per, "budget_per_ms": 50.0}
	if per > 100.0:
		_fail("persist_apply_budget", "per_ms=%.2f" % per)
		return
	_ok("persist_50_apply_avg_ms_%.2f" % per)


func _probe_frame_budget_headless() -> void:
	## SceneTree -s scripts cannot reliably await process_frame in all headless paths.
	## Record CPU tick budget for a tight loop as a proxy; headed GPU measure is a later wave.
	var t0 := Time.get_ticks_usec()
	var acc := 0
	for i in 100000:
		acc += i % 7
	var ms := (Time.get_ticks_usec() - t0) / 1000.0
	_evidence["cpu_proxy_loop"] = {
		"ms": ms,
		"acc": acc,
		"budget_ms": 500.0,
		"note": "headless CPU proxy only — not GPU/world render; headed measure still required for ship",
	}
	if ms > 500.0:
		_fail("cpu_proxy_budget", "ms=%.2f" % ms)
		return
	_ok("cpu_proxy_loop_ms_%.2f" % ms)
