## G3-001 W2 headless E2E smoke — onboarding vertical slice.
## Paths: complete (preview→confirm handoff stub), cancel (no durable), undo (compensating stub).
##
## Run:
##   tools\Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://scripts/modules/executor/g3_e2e_smoke.gd
##
## Exit 0 on pass. Prints G3_E2E_SMOKE=PASS|FAIL.
## Clean log expected: no SCRIPT ERROR, Parse Error, Compile Error, ERROR:.
extends SceneTree

const SLICE_PATH := "res://scripts/modules/executor/g3_onboarding_slice.gd"
const COMPLETE_EXPORT := "res://scripts/modules/executor/exports/g3_complete_receipt.json"
const CANCEL_EXPORT := "res://scripts/modules/executor/exports/g3_cancel_receipt.json"
const UNDO_EXPORT := "res://scripts/modules/executor/exports/g3_undo_receipt.json"

var _failures: PackedStringArray = []
var _passed: int = 0
var _Slice: GDScript


func _initialize() -> void:
	print("[G3-001 W2 executor E2E] starting…")
	_Slice = load(SLICE_PATH) as GDScript
	if _Slice == null:
		_fail("load_slice", "could not load %s" % SLICE_PATH)
		_finish()
		return

	var host := Node.new()
	host.name = "G3E2EHost"
	root.add_child(host)

	var slice: Node = _Slice.new() as Node
	slice.name = "G3OnboardingSlice"
	host.add_child(slice)

	# Allow _ready on modules (executor/companion/realm).
	await process_frame
	await process_frame

	var boot: Dictionary = slice.call("bootstrap", host) as Dictionary
	if not bool(boot.get("ok", false)):
		_fail("bootstrap", str(boot))
		_finish()
		return
	if not bool(boot.get("preview_bridge", false)):
		_fail("bootstrap_preview_bridge", str(boot))
		_finish()
		return
	_ok("bootstrap")

	# Ensure group lookup works for Starter Realm controller.
	var realm_nodes := get_nodes_in_group("g3_starter_realm")
	if realm_nodes.is_empty():
		_fail("realm_group", "g3_starter_realm empty")
	else:
		_ok("realm_group")

	await process_frame

	# ── Complete path ────────────────────────────────────────────────────────
	var complete: Dictionary = slice.call("run_complete_path", true) as Dictionary
	if not bool(complete.get("ok", false)):
		_fail("complete_path", str(complete.get("step", "")) + " " + str(complete.get("detail", complete.get("reason", complete))))
	else:
		_ok("complete_path")
		var crec: Dictionary = complete.get("receipt", {}) as Dictionary
		_assert_common_receipt(crec, "complete")
		if str(crec.get("pipeline_stage", "")) != "commit_handoff_stubbed":
			_fail("complete_pipeline_stage", str(crec.get("pipeline_stage", "")))
		else:
			_ok("complete_pipeline_stage")
		var conf: Dictionary = crec.get("confirmation", {}) as Dictionary
		if str(conf.get("state", "")) != "confirmed" or conf.get("preview_required") != true:
			_fail("complete_confirmation", str(conf))
		else:
			_ok("complete_confirmation")
		var man: Dictionary = crec.get("manifestation", {}) as Dictionary
		var stages: Array = man.get("stages_observed", []) as Array
		if stages.size() < 4:
			_fail("complete_stages", str(stages))
		else:
			_ok("complete_stages")
		if str(man.get("final_stage", "")) != "complete":
			_fail("complete_final_stage", str(man.get("final_stage", "")))
		else:
			_ok("complete_final_stage")
		if crec.get("durable_mutation_applied") != false:
			_fail("complete_durable_flag")
		else:
			_ok("complete_durable_false")
		if crec.get("world_commit_invoked") != false:
			_fail("complete_world_commit_flag")
		else:
			_ok("complete_world_commit_false")
		var cr: Dictionary = crec.get("commit_request", {}) as Dictionary
		var auth: Dictionary = cr.get("authority", {}) as Dictionary
		if str(auth.get("commit_path", "")) != "world_commit_service":
			_fail("complete_commit_path", str(auth))
		else:
			_ok("complete_commit_path")
		if str(auth.get("source", "")) == "client_authoritative":
			_fail("complete_commit_source_client")
		else:
			_ok("complete_commit_source")
		var stub: Dictionary = crec.get("commit_receipt_stub", {}) as Dictionary
		if str(stub.get("status", "")) == "committed":
			_fail("complete_stub_committed")
		else:
			_ok("complete_stub_not_committed")
		if str(crec.get("entity_recipe_id", "")) != "cozy_house_small":
			_fail("complete_recipe_id", str(crec.get("entity_recipe_id", "")))
		else:
			_ok("complete_recipe_id")
		if not _file_exists(COMPLETE_EXPORT):
			_fail("complete_export_missing")
		else:
			_ok("complete_export_written")
		var exp_w: Dictionary = complete.get("export", {}) as Dictionary
		if not bool(exp_w.get("ok", false)):
			_fail("complete_export_ok", str(exp_w))
		else:
			_ok("complete_export_ok")

	await process_frame

	# ── Cancel path ──────────────────────────────────────────────────────────
	var cancel: Dictionary = slice.call("run_cancel_path", true) as Dictionary
	if not bool(cancel.get("ok", false)):
		_fail("cancel_path", str(cancel.get("step", "")) + " " + str(cancel.get("detail", cancel.get("reason", cancel))))
	else:
		_ok("cancel_path")
		var krec: Dictionary = cancel.get("receipt", {}) as Dictionary
		_assert_common_receipt(krec, "cancel")
		if str(krec.get("pipeline_stage", "")) != "cancelled":
			_fail("cancel_pipeline_stage", str(krec.get("pipeline_stage", "")))
		else:
			_ok("cancel_pipeline_stage")
		if str(krec.get("status", "")) != "cancelled":
			_fail("cancel_status", str(krec.get("status", "")))
		else:
			_ok("cancel_status")
		if krec.get("durable_mutation_applied") != false:
			_fail("cancel_durable_flag")
		else:
			_ok("cancel_durable_false")
		if krec.get("world_commit_invoked") != false:
			_fail("cancel_world_commit_flag")
		else:
			_ok("cancel_world_commit_false")
		if krec.get("world_revision_advanced") != false:
			_fail("cancel_revision_advanced")
		else:
			_ok("cancel_revision_not_advanced")
		var kman: Dictionary = krec.get("manifestation", {}) as Dictionary
		if kman.get("has_durable_collision") != false:
			_fail("cancel_collision")
		else:
			_ok("cancel_no_collision")
		if int(kman.get("orphan_collision_count", -1)) != 0:
			_fail("cancel_orphan_collision")
		else:
			_ok("cancel_orphan_zero")
		var during := str(krec.get("cancelled_during_stage", ""))
		if during.is_empty() or during == "complete":
			_fail("cancel_during_stage", during)
		else:
			_ok("cancel_during_stage")
		# Cancel is not compensating.
		if str(krec.get("mutation_class", "")) == "compensating":
			_fail("cancel_must_not_be_compensating")
		else:
			_ok("cancel_not_compensating")
		if bool(cancel.get("confirm_after_cancel_ok", true)):
			_fail("confirm_after_cancel_should_fail")
		else:
			_ok("confirm_after_cancel_rejected")
		if not _file_exists(CANCEL_EXPORT):
			_fail("cancel_export_missing")
		else:
			_ok("cancel_export_written")

	await process_frame

	# ── Undo path (compensating stub; history preserved) ─────────────────────
	var prior: Dictionary = {}
	if slice.has_method("get_last_complete_receipt"):
		prior = slice.call("get_last_complete_receipt") as Dictionary
	var undo: Dictionary = slice.call("run_undo_path", prior, true) as Dictionary
	if not bool(undo.get("ok", false)):
		_fail("undo_path", str(undo.get("reason", undo)))
	else:
		_ok("undo_path")
		var urec: Dictionary = undo.get("receipt", {}) as Dictionary
		_assert_common_receipt(urec, "undo")
		if str(urec.get("mutation_class", "")) != "compensating":
			_fail("undo_mutation_class", str(urec.get("mutation_class", "")))
		else:
			_ok("undo_mutation_class")
		if urec.get("history_erased") != false:
			_fail("undo_history_erased")
		else:
			_ok("undo_history_not_erased")
		if urec.get("history_preserved") != true:
			_fail("undo_history_preserved")
		else:
			_ok("undo_history_preserved")
		if urec.get("durable_mutation_applied") != false:
			_fail("undo_durable_flag")
		else:
			_ok("undo_durable_false")
		if urec.get("world_commit_invoked") != false:
			_fail("undo_world_commit_flag")
		else:
			_ok("undo_world_commit_false")
		var prior_rid := str(urec.get("prior_receipt_id", ""))
		var prior_req := str(urec.get("prior_request_id", ""))
		if prior_rid.is_empty() or prior_req.is_empty():
			_fail("undo_prior_links", "missing prior_receipt_id/request_id")
		else:
			_ok("undo_prior_links")
		if str(urec.get("request_id", "")) == prior_req:
			_fail("undo_request_id_collision")
		else:
			_ok("undo_new_request_id")
		if str(urec.get("receipt_id", "")) == prior_rid:
			_fail("undo_receipt_id_collision")
		else:
			_ok("undo_new_receipt_id")
		# Prior complete export still on disk (not erased).
		if not _file_exists(COMPLETE_EXPORT):
			_fail("undo_erased_complete_export")
		else:
			_ok("undo_complete_still_exists")
		if not _file_exists(UNDO_EXPORT):
			_fail("undo_export_missing")
		else:
			_ok("undo_export_written")
		if urec.get("prior_complete_receipt_still_exists") != true:
			_fail("undo_prior_exists_flag")
		else:
			_ok("undo_prior_exists_flag")

	# ── Realm session context sanity ─────────────────────────────────────────
	if not realm_nodes.is_empty():
		var realm: Node = realm_nodes[0]
		if realm.has_method("get_session_context"):
			var ctx: Dictionary = realm.call("get_session_context") as Dictionary
			if str(ctx.get("snapshot_id", "")).is_empty() and str(ctx.get("live_snapshot_id", "")).is_empty():
				_fail("realm_snapshot_context")
			else:
				_ok("realm_snapshot_context")
		if realm.has_method("get_quest_summary"):
			var qs := str(realm.call("get_quest_summary"))
			if qs.is_empty():
				# Cancel path may have left last quest text; still acceptable if set earlier.
				_ok("realm_quest_summary_optional")
			else:
				_ok("realm_quest_summary")

	_finish()


func _assert_common_receipt(rec: Dictionary, kind: String) -> void:
	if str(rec.get("receipt_kind", "")) != kind:
		_fail("%s_receipt_kind" % kind, str(rec.get("receipt_kind", "")))
	else:
		_ok("%s_receipt_kind" % kind)
	if str(rec.get("schema_version", "")).is_empty():
		_fail("%s_schema_version" % kind)
	else:
		_ok("%s_schema_version" % kind)
	if str(rec.get("receipt_id", "")).is_empty():
		_fail("%s_receipt_id" % kind)
	else:
		_ok("%s_receipt_id" % kind)
	if str(rec.get("request_id", "")).is_empty():
		_fail("%s_request_id" % kind)
	else:
		_ok("%s_request_id" % kind)
	if str(rec.get("prompt_id", "")).is_empty():
		_fail("%s_prompt_id" % kind)
	else:
		_ok("%s_prompt_id" % kind)
	if str(rec.get("space_id", "")).is_empty():
		_fail("%s_space_id" % kind)
	else:
		_ok("%s_space_id" % kind)
	if str(rec.get("slice", "")) != "g3_onboarding_vertical":
		_fail("%s_slice" % kind, str(rec.get("slice", "")))
	else:
		_ok("%s_slice" % kind)


func _file_exists(res_path: String) -> bool:
	if FileAccess.file_exists(res_path):
		return true
	var abs_path := ProjectSettings.globalize_path(res_path)
	return FileAccess.file_exists(abs_path)


func _finish() -> void:
	if _failures.is_empty():
		print("G3_E2E_SMOKE=PASS checks=%d" % _passed)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print("G3_E2E_SMOKE=FAIL failed=%d passed=%d" % [_failures.size(), _passed])
		quit(1)


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)
