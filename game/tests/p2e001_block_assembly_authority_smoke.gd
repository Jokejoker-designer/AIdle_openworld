## WO-P2E-001 — authority commit / idempotency / stale / undo / cancel-after-confirm.
## Run:
##   tools/Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://tests/p2e001_block_assembly_authority_smoke.gd
## Exit 0 + AIDLE_P2E001_AUTHORITY_SMOKE=PASS.
extends SceneTree

const CtrlScript = preload("res://scripts/modules/block_assembly/block_assembly_controller.gd")

var _failures: PackedStringArray = []
var _passed: int = 0
var _ctrl: Node = null


func _initialize() -> void:
	print("[P2E-001 authority smoke] starting…")
	_ctrl = CtrlScript.new() as Node
	root.add_child(_ctrl)
	var conn: Dictionary = _ctrl.call("bind_local_authority", 0) as Dictionary
	if not bool(conn.get("ok", false)):
		_fail("bind", str(conn))
		_finish()
		return

	_test_confirm_commit_one_entity()
	_test_idempotent_replay_no_duplicate()
	_test_changed_payload_same_key_reject()
	_test_stale_revision_reject()
	_test_client_authored_success_reject()
	_test_cancel_after_earlier_confirm()
	_test_undo_compensation_not_scene_tree()
	_test_preview_submit_no_mutation()
	_finish()


func _finish() -> void:
	if _failures.is_empty():
		print("AIDLE_P2E001_AUTHORITY_SMOKE=PASS checks=%d" % _passed)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print(
			"AIDLE_P2E001_AUTHORITY_SMOKE=FAIL failed=%d passed=%d"
			% [_failures.size(), _passed]
		)
		quit(1)


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)


func _fresh_ctrl(seed_rev: int = 0) -> Node:
	if _ctrl != null and is_instance_valid(_ctrl):
		_ctrl.queue_free()
	_ctrl = CtrlScript.new() as Node
	root.add_child(_ctrl)
	var conn: Dictionary = _ctrl.call("bind_local_authority", seed_rev) as Dictionary
	if not bool(conn.get("ok", false)):
		_fail("fresh_bind", str(conn))
	return _ctrl


func _test_confirm_commit_one_entity() -> void:
	_fresh_ctrl(0)
	var s: Dictionary = _ctrl.call(
		"select_module", "block_cube_round", "structure", "", 0.0, 0.0, 0.0, 0.0
	) as Dictionary
	if not bool(s.get("ok", false)):
		_fail("commit_select", str(s))
		return
	_ctrl.call("advance_stage", "hologram")
	_ctrl.call("advance_stage", "materializing")
	var r: Dictionary = _ctrl.call("confirm_and_commit", true) as Dictionary
	if not bool(r.get("ok", false)):
		_fail("confirm_commit", str(r))
		return
	var receipt: Dictionary = r.get("receipt", {}) as Dictionary
	if str(receipt.get("status", "")) != "committed":
		_fail("commit_status", str(receipt))
		return
	if str((receipt.get("authority", {}) as Dictionary).get("issuer", "")) != "world_commit_service":
		_fail("issuer", str(receipt.get("authority")))
		return
	var eids: Array = receipt.get("entity_ids", []) as Array
	if eids.size() != 1:
		_fail("one_entity", "count=%d" % eids.size())
		return
	if not bool(r.get("collision", false)) or not bool(r.get("navigation", false)):
		_fail("post_commit_phys", str(r))
		return
	if int(_ctrl.call("get_world_revision")) != 1:
		_fail("rev_bump", str(_ctrl.call("get_world_revision")))
		return
	if int(_ctrl.call("get_committed_count")) != 1:
		_fail("committed_count", str(_ctrl.call("get_committed_count")))
		return
	_ok("confirm_commit_one_entity_receipt")


func _test_idempotent_replay_no_duplicate() -> void:
	## Fresh commit then same request_id/fingerprint → idempotent_replay, no second entity.
	_fresh_ctrl(0)
	_ctrl.call("select_module", "prop_crate_small", "wood", "MAT_CozyWood", 0.5, 0.5, 0.0, 0.0)
	var st_before: Dictionary = _ctrl.call("get_active_state") as Dictionary
	var req_id := str(st_before.get("request_id", ""))
	var prompt_id := str(st_before.get("prompt_id", ""))
	var c1: Dictionary = _ctrl.call("confirm_and_commit", true) as Dictionary
	if not bool(c1.get("ok", false)):
		_fail("idem_setup_commit", str(c1))
		return
	var rec1: Dictionary = c1.get("receipt", {}) as Dictionary
	if str(rec1.get("status", "")) != "committed":
		_fail("idem_setup_status", str(rec1))
		return
	if req_id.is_empty():
		req_id = str(rec1.get("request_id", ""))
	if prompt_id.is_empty():
		var server0: RefCounted = _ctrl.call("get_server") as RefCounted
		var client0: RefCounted = _ctrl.call("get_client") as RefCounted
		var snap0: Dictionary = server0.call("get_snapshot", str(client0.get("session_token")), "") as Dictionary
		prompt_id = _extract_prompt_id(snap0)
	if req_id.is_empty() or prompt_id.is_empty():
		_fail("idem_ids_missing", "req=%s prompt=%s" % [req_id, prompt_id])
		return
	var server: RefCounted = _ctrl.call("get_server") as RefCounted
	var client: RefCounted = _ctrl.call("get_client") as RefCounted
	var replay_req := {
		"schema_version": "1.0.0",
		"request_id": req_id,
		"prompt_id": prompt_id,
		"space_id": "home_01",
		"expected_world_revision": 0,
		"mutation_class": "world_prompt_commit",
		"actor": {"actor_id": "player_01", "actor_type": "player"},
		"authority": {
			"commit_path": "world_commit_service",
			"source": "server_authoritative",
		},
		"confirmation": {"state": "confirmed", "confirmed_by": "player_01"},
		"trace_id": "trace-idem-replay",
	}
	var rec2: Dictionary = client.call("commit", replay_req) as Dictionary
	if str(rec2.get("status", "")) != "idempotent_replay":
		_fail("idempotent_status", str(rec2))
		return
	if int(server.call("world_revision")) != 1:
		_fail("idem_no_extra_rev", str(server.call("world_revision")))
		return
	if int(server.call("entity_count")) != 1:
		_fail("idem_no_duplicate_entity", str(server.call("entity_count")))
		return
	_ok("idempotent_replay_no_duplicate")


func _extract_prompt_id(snap: Dictionary) -> String:
	var ents_v: Variant = snap.get("entities", null)
	if ents_v is Array:
		for e in ents_v:
			if e is Dictionary and (e as Dictionary).has("origin_prompt_id"):
				return str((e as Dictionary)["origin_prompt_id"])
	elif ents_v is Dictionary:
		for k in (ents_v as Dictionary).keys():
			var e: Variant = (ents_v as Dictionary)[k]
			if e is Dictionary and (e as Dictionary).has("origin_prompt_id"):
				return str((e as Dictionary)["origin_prompt_id"])
	return ""


func _test_changed_payload_same_key_reject() -> void:
	## F06: after durable commit, same key + changed payload rejects; rev stays at post-commit.
	_fresh_ctrl(0)
	var s: Dictionary = _ctrl.call(
		"select_module", "block_beam", "structure", "", 0.0, 0.0, 0.0, 0.0
	) as Dictionary
	if not bool(s.get("ok", false)):
		_fail("changed_select", str(s))
		return
	var r: Dictionary = _ctrl.call("attempt_changed_payload_same_key") as Dictionary
	if bool(r.get("ok", false)):
		_fail("changed_payload_should_reject", str(r))
		return
	if str(r.get("code", "")) != "idempotency_payload_mismatch":
		_fail("changed_payload_code", str(r))
		return
	# One successful commit happened inside attempt_*; reject must not advance further.
	if int(_ctrl.call("get_world_revision")) != 1:
		_fail("changed_rev_after_commit_only", str(_ctrl.call("get_world_revision")))
		return
	_ok("changed_payload_same_key_reject")


func _test_stale_revision_reject() -> void:
	_fresh_ctrl(0)
	# Advance world by one commit, then try stale on new preview.
	_ctrl.call("select_module", "block_ring", "structure", "", 0.0, 0.0, 0.0, 0.0)
	var c1: Dictionary = _ctrl.call("confirm_and_commit", true) as Dictionary
	if not bool(c1.get("ok", false)):
		_fail("stale_setup", str(c1))
		return
	# New placement at current rev; force stale expected_rev=0
	_ctrl.call("select_module", "block_dome", "structure", "", 1.0, 0.0, 0.0, 0.0)
	var r: Dictionary = _ctrl.call("attempt_stale_revision_commit", 0) as Dictionary
	var receipt: Dictionary = r.get("receipt", {}) as Dictionary
	var status := str(receipt.get("status", r.get("status", "")))
	if status != "conflicted" and status != "rejected":
		_fail("stale_status", str(receipt))
		return
	# World should remain at 1 (only first commit).
	if int(_ctrl.call("get_world_revision")) != 1:
		_fail("stale_rev_unchanged", str(_ctrl.call("get_world_revision")))
		return
	_ok("stale_revision_reject")


func _test_client_authored_success_reject() -> void:
	var forged := {
		"status": "committed",
		"receipt_id": "client-forged-receipt",
		"authority": {"issuer": "client"},
	}
	var r: Dictionary = _ctrl.call("reject_client_authored_success", forged) as Dictionary
	if bool(r.get("ok", false)) or bool(r.get("accepted", true)):
		_fail("client_success_should_reject")
		return
	if str(r.get("code", "")) != "client_forged":
		_fail("client_forged_code", str(r))
		return
	_ok("client_authored_success_reject")


func _test_cancel_after_earlier_confirm() -> void:
	_fresh_ctrl(0)
	_ctrl.call("select_module", "block_arch", "structure", "", 0.0, 0.0, 0.0, 0.0)
	var c1: Dictionary = _ctrl.call("confirm_and_commit", true) as Dictionary
	if not bool(c1.get("ok", false)):
		_fail("cancel_after_confirm_setup", str(c1))
		return
	var committed := int(_ctrl.call("get_committed_count"))
	if committed != 1:
		_fail("cancel_after_committed_count", str(committed))
		return
	# Start new preview and cancel — must not remove committed.
	_ctrl.call("select_module", "block_wedge", "structure", "", 2.0, 2.0, 0.0, 15.0)
	_ctrl.call("advance_stage", "hologram")
	var cancel: Dictionary = _ctrl.call("cancel_preview") as Dictionary
	if not bool(cancel.get("ok", false)):
		_fail("cancel_after_confirm_cancel", str(cancel))
		return
	if int(_ctrl.call("get_committed_count")) != 1:
		_fail("cancel_must_keep_committed", str(_ctrl.call("get_committed_count")))
		return
	if int(_ctrl.call("get_world_revision")) != 1:
		_fail("cancel_no_rev_change", str(_ctrl.call("get_world_revision")))
		return
	if not bool(cancel.get("committed_untouched", false)):
		_fail("committed_untouched_flag")
		return
	_ok("cancel_after_earlier_confirm")


func _test_undo_compensation_not_scene_tree() -> void:
	# Uses current controller which has 1 committed entity from previous test.
	if int(_ctrl.call("get_committed_count")) < 1:
		_ctrl.call("select_module", "block_pipe_straight", "metal", "MAT_CozyMetal", 0.0, 0.0, 0.0, 0.0)
		var c: Dictionary = _ctrl.call("confirm_and_commit", true) as Dictionary
		if not bool(c.get("ok", false)):
			_fail("undo_setup", str(c))
			return
	var before_rev := int(_ctrl.call("get_world_revision"))
	var u: Dictionary = _ctrl.call("request_undo_compensation") as Dictionary
	if not bool(u.get("ok", false)):
		_fail("undo_compensation", str(u))
		return
	if bool(u.get("direct_scene_tree_delete", true)):
		_fail("undo_not_direct_delete")
		return
	if not bool(u.get("authority_path", false)):
		_fail("undo_authority_path")
		return
	if str(u.get("mutation_class", "")) != "compensation_request":
		_fail("undo_mutation_class", str(u.get("mutation_class")))
		return
	var receipt: Dictionary = u.get("receipt", {}) as Dictionary
	if str(receipt.get("status", "")) != "committed":
		_fail("undo_receipt", str(receipt))
		return
	if int(_ctrl.call("get_world_revision")) != before_rev + 1:
		_fail("undo_rev_bump", str(_ctrl.call("get_world_revision")))
		return
	_ok("undo_compensation_authority_path")


func _test_preview_submit_no_mutation() -> void:
	_fresh_ctrl(0)
	_ctrl.call("select_module", "block_platform", "structure", "", 0.0, 0.0, 0.0, 0.0)
	var sub: Dictionary = _ctrl.call("submit_preview_proposal") as Dictionary
	if not bool(sub.get("ok", false)):
		_fail("preview_submit", str(sub))
		return
	if int(_ctrl.call("get_world_revision")) != 0:
		_fail("submit_no_mutation", str(_ctrl.call("get_world_revision")))
		return
	if bool(sub.get("mutated", true)):
		_fail("submit_mutated_flag")
		return
	# Explicit false confirm must fail.
	var bad: Dictionary = _ctrl.call("confirm_and_commit", false) as Dictionary
	if bool(bad.get("ok", false)):
		_fail("explicit_confirm_required")
		return
	_ok("preview_submit_no_mutation_explicit_confirm")
