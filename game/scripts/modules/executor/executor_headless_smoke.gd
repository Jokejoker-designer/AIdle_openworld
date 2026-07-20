## Headless smoke for G2-006 deterministic AGM Decision executor.
## Run:
##   tools\Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://scripts/modules/executor/executor_headless_smoke.gd
##
## Exit 0 on pass, 1 on failure. Prints G2-006_GODOT_SMOKE=PASS|FAIL.
## Uses load() so concurrent broken modules cannot block pure executor checks.
extends SceneTree

const DECISION_PATH := "res://scripts/modules/executor/decision_executor.gd"
const PIPELINE_PATH := "res://scripts/modules/executor/prompt_pipeline.gd"
const MODULE_PATH := "res://scripts/modules/executor/executor_module.gd"
const I_EXEC_PATH := "res://scripts/modules/interfaces/i_executor_module.gd"

var _failures: PackedStringArray = []
var _passed: int = 0
var _Decision: GDScript
var _Pipeline: GDScript
var _Module: GDScript
var _IExec: GDScript


func _initialize() -> void:
	print("[G2-006 smoke] starting…")
	_Decision = load(DECISION_PATH) as GDScript
	_Pipeline = load(PIPELINE_PATH) as GDScript
	_Module = load(MODULE_PATH) as GDScript
	_IExec = load(I_EXEC_PATH) as GDScript

	if _Decision == null or _Pipeline == null or _Module == null:
		_fail("load_scripts", "could not load executor scripts")
		_finish()
		return

	_test_interface_surface()
	_test_unknown_action_rejected()
	_test_forbidden_field_rejected()
	_test_stale_snapshot_rejected()
	_test_decision_id_idempotency()
	_test_build_routes_preview_confirm_commit()
	_test_build_bypass_rejected()
	_test_mood_cap_rejected()
	_test_valid_soft_decision()
	_test_pipeline_no_durable_on_confirm()
	await _test_module_execute_and_submit()

	_finish()


func _finish() -> void:
	if _failures.is_empty():
		print("G2-006_GODOT_SMOKE=PASS checks=%d" % _passed)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print("G2-006_GODOT_SMOKE=FAIL failed=%d passed=%d" % [_failures.size(), _passed])
		quit(1)


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)


func _base_decision(overrides: Dictionary = {}) -> Dictionary:
	var d := {
		"schema_version": "1.0.0",
		"decision_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
		"source_snapshot_id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
		"created_at": "2026-07-20T16:00:05Z",
		"edition": "desktop_bridge_free",
		"session_id": "session_smoke_01",
		"dialogue": {
			"lines": [{"speaker": "companion", "text": "Smoke dialogue line."}],
			"companion_expression": "warm",
		},
		"quest_operations": [],
		"build_proposals": [],
		"event_proposals": [],
		"mood_delta": {"delta": 0.01, "reason": "smoke"},
		"relationship_delta": {"delta": 0.0},
		"next_trigger": {"kind": "player_action"},
		"trace": {"trace_id": "trace_smoke", "model_receipt_ref": "bridge:smoke"},
	}
	for k in overrides.keys():
		d[k] = overrides[k]
	return d


func _live_snap(snapshot_id: String = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb") -> Dictionary:
	return {
		"schema_version": "1.0.0",
		"snapshot_id": snapshot_id,
		"created_at": "2026-07-20T18:00:00Z",
		"edition": "desktop_bridge_free",
		"session_id": "session_smoke_01",
		"space_id": "home_01",
		"world_revision": 3,
		"player": {"player_id": "player_01", "location": {"chunk_id": "0_0", "x": 1.0, "y": 1.0}},
		"companion": {"companion_id": "companion_lumi", "mood": 0.5, "relationship": 0.5},
		"world": {"space_type": "private_reality", "entity_count": 1, "known_entity_ids": []},
		"art_style": {"profile_id": "cozy_default", "base_concept": "cozy_cyber_pixel_2_5d"},
	}


func _test_interface_surface() -> void:
	if _IExec == null:
		_fail("interface_load")
		return
	var mod: Node = _Module.new() as Node
	# validate before tree enter is fine for method presence
	var missing: PackedStringArray = _IExec.call("validate", mod) as PackedStringArray
	mod.free()
	if not missing.is_empty():
		_fail("interface_surface", "missing %s" % str(missing))
		return
	_ok("interface_surface")


func _test_unknown_action_rejected() -> void:
	var ex: RefCounted = _Decision.new() as RefCounted
	var d := _base_decision({
		"decision_id": "11111111-1111-4111-8111-111111111101",
		"event_proposals": [
			{"event_type": "economy.spawn_currency", "summary": "not allowlisted"},
		],
		"mood_delta": {"delta": 0.0},
	})
	var receipt: Dictionary = ex.call("execute", d, _live_snap()) as Dictionary
	var rejected: Array = receipt.get("actions_rejected", []) as Array
	var found := false
	for r in rejected:
		if typeof(r) == TYPE_DICTIONARY and "unknown_action" in str((r as Dictionary).get("reason", "")):
			found = true
	if not found and str(receipt.get("status", "")) not in ["rejected", "partial"]:
		_fail("unknown_action", "status=%s rejected=%s" % [receipt.get("status"), str(rejected)])
		return
	if not found:
		_fail("unknown_action", "no unknown_action rejection recorded")
		return
	_ok("unknown_action_rejected")


func _test_forbidden_field_rejected() -> void:
	var ex: RefCounted = _Decision.new() as RefCounted
	var d := _base_decision({
		"decision_id": "11111111-1111-4111-8111-111111111102",
		"durable_mutation": {"entity": "hack"},
	})
	var receipt: Dictionary = ex.call("execute", d, _live_snap()) as Dictionary
	if str(receipt.get("status", "")) != "rejected":
		_fail("forbidden_field", "status=%s" % receipt.get("status"))
		return
	_ok("forbidden_field_rejected")


func _test_stale_snapshot_rejected() -> void:
	var ex: RefCounted = _Decision.new() as RefCounted
	var d := _base_decision({
		"decision_id": "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
		"source_snapshot_id": "11111111-1111-4111-8111-111111111111",
	})
	var live := _live_snap("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb")
	var receipt: Dictionary = ex.call("execute", d, live) as Dictionary
	if str(receipt.get("status", "")) != "stale_snapshot":
		_fail("stale_snapshot", "status=%s" % receipt.get("status"))
		return
	_ok("stale_snapshot_rejected")


func _test_decision_id_idempotency() -> void:
	var ex: RefCounted = _Decision.new() as RefCounted
	var d := _base_decision({
		"decision_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
		"quest_operations": [
			{
				"op": "offer",
				"quest_id": "q_smoke_once",
				"title": "Once",
				"objective_summary": "Should not double-apply",
			}
		],
		"mood_delta": {"delta": 0.05},
	})
	var live := _live_snap()
	var r1: Dictionary = ex.call("execute", d, live) as Dictionary
	var soft1: Dictionary = ex.call("get_soft_state") as Dictionary
	var mood1 := float(soft1.get("mood", 0.0))
	var quests1: Dictionary = soft1.get("quests", {}) as Dictionary

	var d2 := d.duplicate(true)
	d2["mood_delta"] = {"delta": 0.05}
	d2["quest_operations"] = [
		{
			"op": "offer",
			"quest_id": "q_should_not_reoffer",
			"title": "Replay Trap",
			"objective_summary": "Must be ignored",
		}
	]
	var r2: Dictionary = ex.call("execute", d2, live) as Dictionary
	if str(r2.get("status", "")) != "replayed":
		_fail("idempotency_status", "status=%s" % r2.get("status"))
		return
	if not bool((r2.get("idempotency", {}) as Dictionary).get("replayed", false)):
		_fail("idempotency_flag")
		return
	var soft2: Dictionary = ex.call("get_soft_state") as Dictionary
	var mood2 := float(soft2.get("mood", 0.0))
	if not is_equal_approx(mood1, mood2):
		_fail("idempotency_mood", "mood re-applied %s → %s" % [mood1, mood2])
		return
	var quests2: Dictionary = soft2.get("quests", {}) as Dictionary
	if quests2.has("q_should_not_reoffer"):
		_fail("idempotency_quest", "replay re-applied quest")
		return
	if not quests1.has("q_smoke_once"):
		_fail("idempotency_original_quest")
		return
	if str(r1.get("receipt_id", "")) == "":
		_fail("idempotency_prior_receipt")
		return
	_ok("decision_id_idempotency")


func _test_build_routes_preview_confirm_commit() -> void:
	var ex: RefCounted = _Decision.new() as RefCounted
	var pipe: RefCounted = _Pipeline.new() as RefCounted
	var d := _base_decision({
		"decision_id": "33333333-3333-4333-8333-333333333333",
		"build_proposals": [
			{
				"proposal_id": "44444444-4444-4444-8444-444444444444",
				"operation": "create",
				"recipe_id": "cozy_house_small",
				"entity_kind": "modular_structure_2_5d",
				"routes_through": "preview_confirm_commit",
				"preview_required": true,
				"confirmation_state": "pending",
				"space_id": "home_01",
				"chunk_id": "0_0",
				"transform": {"x": 8.0, "y": 6.0, "elevation": 0.0, "rotation_deg": 0.0},
			}
		],
		"mood_delta": {"delta": 0.0},
	})
	var receipt: Dictionary = ex.call("execute", d, _live_snap()) as Dictionary
	if str(receipt.get("status", "")) != "awaiting_player":
		_fail("build_status", "status=%s" % receipt.get("status"))
		return
	var handoffs: Array = receipt.get("build_handoffs", []) as Array
	if handoffs.is_empty():
		_fail("build_handoffs_empty")
		return
	var h: Dictionary = handoffs[0]
	if str(h.get("routes_through", "")) != "preview_confirm_commit":
		_fail("build_routes")
		return
	if h.get("preview_required") != true:
		_fail("build_preview_required")
		return
	if str(h.get("confirmation_state", "")) != "pending":
		_fail("build_confirmation_pending")
		return
	if bool(h.get("durable_mutation_applied", true)):
		_fail("build_durable_flag")
		return
	var wp: Dictionary = h.get("world_prompt", {}) as Dictionary
	if wp.is_empty() or str(wp.get("schema_version", "")) != "1.1.0":
		_fail("build_world_prompt")
		return
	var conf: Dictionary = wp.get("confirmation", {}) as Dictionary
	if conf.get("preview_required") != true or str(conf.get("state", "")) != "pending":
		_fail("build_wp_confirmation")
		return

	var sub: Dictionary = pipe.call("submit", wp, "agm") as Dictionary
	if not bool(sub.get("ok", false)):
		_fail("pipeline_submit", str(sub.get("reason", "")))
		return
	var pid := str(sub.get("prompt_id", ""))
	var conf_res: Dictionary = pipe.call("confirm", pid, "player_01", 3) as Dictionary
	if not bool(conf_res.get("ok", false)):
		_fail("pipeline_confirm", str(conf_res.get("reason", "")))
		return
	if str(conf_res.get("pipeline_stage", "")) != "commit_handoff_stubbed":
		_fail("pipeline_stage", str(conf_res.get("pipeline_stage", "")))
		return
	if bool(conf_res.get("durable_mutation_applied", true)):
		_fail("confirm_durable")
		return
	var cr: Dictionary = conf_res.get("commit_request", {}) as Dictionary
	var authority: Dictionary = cr.get("authority", {}) as Dictionary
	if str(authority.get("commit_path", "")) != "world_commit_service":
		_fail("commit_path")
		return
	if str(authority.get("source", "")) != "server_authoritative":
		_fail("commit_source")
		return
	if authority.get("durable_mutation") != true:
		_fail("commit_durable_flag")
		return
	_ok("build_routes_preview_confirm_commit")


func _test_build_bypass_rejected() -> void:
	var ex: RefCounted = _Decision.new() as RefCounted
	var d := _base_decision({
		"decision_id": "55555555-5555-4555-8555-555555555501",
		"build_proposals": [
			{
				"proposal_id": "44444444-4444-4444-8444-444444444401",
				"operation": "create",
				"recipe_id": "cozy_house_small",
				"entity_kind": "modular_structure_2_5d",
				"routes_through": "preview_confirm_commit",
				"preview_required": false,
				"confirmation_state": "confirmed",
				"space_id": "home_01",
				"chunk_id": "0_0",
				"transform": {"x": 1.0, "y": 1.0, "elevation": 0.0, "rotation_deg": 0.0},
			}
		],
		"mood_delta": {"delta": 0.0},
	})
	var receipt: Dictionary = ex.call("execute", d, _live_snap()) as Dictionary
	var rejected: Array = receipt.get("actions_rejected", []) as Array
	var found := false
	for r in rejected:
		if typeof(r) == TYPE_DICTIONARY and "forbidden_build_bypass" in str((r as Dictionary).get("reason", "")):
			found = true
	if not found:
		_fail("build_bypass", str(rejected))
		return
	var handoffs: Array = receipt.get("build_handoffs", []) as Array
	if not handoffs.is_empty():
		_fail("build_bypass_handoff", "handoff should be empty")
		return
	_ok("build_bypass_rejected")


func _test_mood_cap_rejected() -> void:
	var ex: RefCounted = _Decision.new() as RefCounted
	var d := _base_decision({
		"decision_id": "55555555-5555-4555-8555-555555555502",
		"mood_delta": {"delta": 0.5},
		"dialogue": {"lines": []},
	})
	var receipt: Dictionary = ex.call("execute", d, _live_snap()) as Dictionary
	var rejected: Array = receipt.get("actions_rejected", []) as Array
	var found := false
	for r in rejected:
		if typeof(r) == TYPE_DICTIONARY and "mood" in str((r as Dictionary).get("action", "")):
			found = true
	if not found:
		_fail("mood_cap", str(receipt))
		return
	_ok("mood_cap_rejected")


func _test_valid_soft_decision() -> void:
	var ex: RefCounted = _Decision.new() as RefCounted
	var d := _base_decision({
		"decision_id": "22222222-2222-4222-8222-222222222222",
		"quest_operations": [
			{
				"op": "complete",
				"quest_id": "onboarding_first_home",
				"reason": "smoke complete",
			}
		],
		"event_proposals": [
			{"event_type": "narrative.beat", "summary": "soft beat", "intensity": 0.4}
		],
		"mood_delta": {"delta": 0.04},
		"relationship_delta": {"delta": 0.03},
	})
	var receipt: Dictionary = ex.call("execute", d, _live_snap()) as Dictionary
	if str(receipt.get("status", "")) != "applied":
		_fail("valid_soft_status", "status=%s" % receipt.get("status"))
		return
	if bool(receipt.get("durable_mutation_applied", true)):
		_fail("valid_soft_durable")
		return
	var snap_r: Dictionary = ex.call("to_snapshot_receipt", receipt) as Dictionary
	if str(snap_r.get("status", "")) != "applied":
		_fail("snapshot_receipt")
		return
	if snap_r.get("decision_id") == null:
		_fail("snapshot_decision_id")
		return
	_ok("valid_soft_decision")


func _test_pipeline_no_durable_on_confirm() -> void:
	var pipe: RefCounted = _Pipeline.new() as RefCounted
	var wp := {
		"schema_version": "1.1.0",
		"prompt_id": "550e8400-e29b-41d4-a716-446655440099",
		"request_id": "bd5a8351-2b09-4acd-9520-19875098c999",
		"session_id": "session_smoke_01",
		"actor": {"player_id": "player_01", "companion_id": "companion_lumi"},
		"operation": "create",
		"target": {
			"space_type": "private_reality",
			"space_id": "home_01",
			"chunk_id": "0_0",
			"expected_world_revision": 0,
		},
		"style_profile": {
			"profile_id": "cozy_default",
			"profile_version": "1.0.0",
			"base_concept": "cozy_cyber_pixel_2_5d",
			"surrealism_budget": 0.15,
		},
		"entity": {
			"kind": "modular_structure_2_5d",
			"recipe_id": "cozy_house_small",
			"transform": {"x": 8, "y": 6, "elevation": 0, "rotation_deg": 0},
			"bounds": {"width": 8, "depth": 6, "height": 5},
			"interaction_tags": ["enterable"],
		},
		"manifestation": {
			"stages": ["wireframe", "hologram", "materializing", "complete"],
			"presentation_duration_seconds": 12,
		},
		"budget": {"max_compute_units": 200, "max_entities": 32, "paid_compute_allowed": false},
		"provenance": {
			"source_type": "system",
			"requested_by": "companion_lumi",
			"generated_by": "agm_decision_executor",
			"created_at": "2026-07-20T15:00:00Z",
		},
		"confirmation": {"preview_required": true, "state": "pending", "rollback_window_seconds": 3600},
	}
	# Pre-confirmed submit must fail.
	var bad := wp.duplicate(true)
	bad["confirmation"] = {"preview_required": true, "state": "confirmed", "confirmed_by": "hacker"}
	var bad_sub: Dictionary = pipe.call("submit", bad, "test") as Dictionary
	if bool(bad_sub.get("ok", true)):
		_fail("preconfirm_submit_allowed")
		return
	var sub: Dictionary = pipe.call("submit", wp, "test") as Dictionary
	if not bool(sub.get("ok", false)):
		_fail("pipeline_submit_ok")
		return
	var conf: Dictionary = pipe.call("confirm", str(wp["prompt_id"]), "player_01", 0) as Dictionary
	if bool(conf.get("durable_mutation_applied", true)):
		_fail("pipeline_confirm_mutated")
		return
	var status: Dictionary = pipe.call("get_status", str(wp["prompt_id"])) as Dictionary
	if bool(status.get("durable_mutation_applied", true)):
		_fail("pipeline_status_durable")
		return
	if not bool(status.get("commit_handoff_ready", false)):
		_fail("pipeline_handoff_ready")
		return
	_ok("pipeline_no_durable_on_confirm")


func _test_module_execute_and_submit() -> void:
	var mod: Node = _Module.new() as Node
	root.add_child(mod)
	# Force ready
	await process_frame
	if not mod.has_method("execute_decision"):
		_fail("module_methods")
		mod.queue_free()
		return
	var d := _base_decision({
		"decision_id": "99999999-9999-4999-8999-999999999999",
		"event_proposals": [
			{"event_type": "onboarding.nudge", "summary": "nudge", "intensity": 0.2}
		],
	})
	mod.call("set_live_snapshot", _live_snap())
	var receipt: Dictionary = mod.call("execute_decision", d) as Dictionary
	if str(receipt.get("status", "")) != "applied":
		_fail("module_execute", "status=%s" % receipt.get("status"))
		mod.queue_free()
		return
	if not bool(mod.call("has_seen_decision", "99999999-9999-4999-8999-999999999999")):
		_fail("module_seen")
		mod.queue_free()
		return
	# submit_prompt path
	var wp: Dictionary = _Decision.new().call(
		"build_world_prompt_from_proposal",
		{
			"proposal_id": "44444444-4444-4444-8444-444444444402",
			"operation": "create",
			"recipe_id": "cozy_house_small",
			"entity_kind": "modular_structure_2_5d",
			"routes_through": "preview_confirm_commit",
			"preview_required": true,
			"confirmation_state": "pending",
			"space_id": "home_01",
			"chunk_id": "0_0",
			"transform": {"x": 2.0, "y": 2.0, "elevation": 0.0, "rotation_deg": 0.0},
		},
		d
	) as Dictionary
	var pid := str(mod.call("submit_prompt", wp))
	if pid.is_empty():
		_fail("module_submit_prompt")
		mod.queue_free()
		return
	var conf: Dictionary = mod.call("confirm_prompt", pid, "player_01") as Dictionary
	if not bool(conf.get("ok", false)):
		_fail("module_confirm")
		mod.queue_free()
		return
	if bool(conf.get("durable_mutation_applied", true)):
		_fail("module_confirm_durable")
		mod.queue_free()
		return
	mod.queue_free()
	_ok("module_execute_and_submit")
