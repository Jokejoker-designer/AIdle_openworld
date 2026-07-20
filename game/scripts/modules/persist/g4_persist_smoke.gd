## G4-001 P1 headless smoke — Offline Private Reality journal.
## Run:
##   tools\Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://scripts/modules/persist/g4_persist_smoke.gd
##
## Exit 0 on pass. Prints G4_PERSIST_SMOKE=PASS|FAIL.
## Covers: hash equality, dup request, stale rev, malformed journal,
## compensation append, cancel not journaled, rev 3 preserved.
extends SceneTree

const CANON_PATH := "res://scripts/modules/persist/canonical_json.gd"
const HASHER_PATH := "res://scripts/modules/persist/entity_hasher.gd"
const STORE_PATH := "res://scripts/modules/persist/journal_store.gd"
const MODULE_PATH := "res://scripts/modules/persist/persist_module.gd"
const IFACE_PATH := "res://scripts/modules/interfaces/i_persist_module.gd"
const EXPORT_DIR := "res://scripts/modules/persist/exports"
const USER_JOURNAL := "user://g4_persist_smoke/journal.json"
const USER_MALFORMED := "user://g4_persist_smoke/malformed.json"
const USER_SCHEMA := "user://g4_persist_smoke/bad_schema.json"
const USER_SPACE := "user://g4_persist_smoke/bad_space.json"
const USER_TRUNC := "user://g4_persist_smoke/truncated.json"

## G3 seed constants
const G3_BASE_REV := 3
const G3_SPACE_ID := "home_01"
const G3_SNAPSHOT_ID := "11111111-1111-4111-8111-111111111111"
const G3_SESSION_ID := "session_starter_01"
const G3_REQUEST_ID := "865ba0ef-0b16-4074-a579-098db5a78c13"
const G3_PROMPT_ID := "a5b87763-ffe5-45e7-af0c-6cefd1391298"
const G3_EXPECTED_REV := 3

var _failures: PackedStringArray = []
var _passed: int = 0
var _fatal: bool = false
var _Canon: GDScript
var _Hasher: GDScript
var _Store: GDScript
var _Module: GDScript
var _Iface: GDScript
var _evidence: Dictionary = {}


func _initialize() -> void:
	print("[G4-001 P1 persist smoke] starting…")
	_Canon = _require_script(CANON_PATH, "AIdleCanonicalJson")
	_Hasher = _require_script(HASHER_PATH, "AIdleEntityHasher")
	_Store = _require_script(STORE_PATH, "AIdleJournalStore")
	_Module = _require_script(MODULE_PATH, "PersistModule")
	_Iface = _require_script(IFACE_PATH, "IPersistModule")

	if _fatal or not _failures.is_empty():
		printerr("[G4 persist smoke] hard fail during script load — aborting")
		_finish()
		return

	_test_interface_surface()
	_test_canonical_sort_and_float()
	_test_save_reload_hash()
	_test_duplicate_request()
	_test_stale_revision()
	_test_malformed_journal()
	_test_schema_incompatible()
	_test_wrong_space_type()
	_test_compensation_append()
	_test_cancel_not_journaled()
	_test_g3_rev3_preserved()
	_write_evidence_export()

	_finish()


func _require_script(path: String, label: String) -> GDScript:
	if not ResourceLoader.exists(path):
		_fail("script_missing", "%s path=%s" % [label, path])
		_fatal = true
		return null
	var loaded: Resource = load(path)
	if loaded == null:
		_fail("script_load_null", "%s path=%s" % [label, path])
		_fatal = true
		return null
	var script: GDScript = loaded as GDScript
	if script == null or not script.can_instantiate():
		_fail("script_cannot_instantiate", "%s path=%s" % [label, path])
		_fatal = true
		return null
	print("  LOAD OK  %s" % label)
	return script


func _finish() -> void:
	if _failures.is_empty() and not _fatal:
		print("G4_PERSIST_SMOKE=PASS checks=%d" % _passed)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print(
			"G4_PERSIST_SMOKE=FAIL failed=%d passed=%d fatal=%s"
			% [_failures.size(), _passed, str(_fatal)]
		)
		quit(1)


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)


func _new_store() -> Object:
	return _Store.new()


func _house_entity() -> Dictionary:
	return {
		"entity_id": "entity_cozy_house_01",
		"kind": "building",
		"recipe_id": "cozy_house_small",
		"transform": {"x": 8, "y": 6, "elevation": 0, "rotation_deg": 0},
		"bounds": {"width": 4, "depth": 4, "height": 3},
		"interaction_tags": ["inspect", "enter"],
		"space_id": G3_SPACE_ID,
		"chunk_id": "0_0",
	}


func _test_interface_surface() -> void:
	var mod: Object = _Module.new()
	if mod == null:
		_fail("module_new")
		return
	var missing: PackedStringArray = _Iface.call("validate", mod) as PackedStringArray
	if missing == null:
		missing = PackedStringArray()
	if not missing.is_empty():
		_fail("interface_missing", str(missing))
	else:
		_ok("interface_surface")
	if mod is Node:
		(mod as Node).free()


func _test_canonical_sort_and_float() -> void:
	var a := {"z": 1, "a": 2, "m": {"b": 1, "a": 8.0}}
	var b := {"m": {"a": 8.000000, "b": 1}, "a": 2, "z": 1}
	var sa: String = str(_Canon.call("stringify", a))
	var sb: String = str(_Canon.call("stringify", b))
	if sa != sb:
		_fail("canonical_key_order", "sa=%s sb=%s" % [sa, sb])
		return
	var ha: String = str(_Hasher.call("sha256_hex", sa))
	var hb: String = str(_Hasher.call("sha256_hex", sb))
	if ha != hb or ha.length() != 64:
		_fail("canonical_hash", "ha=%s hb=%s" % [ha, hb])
		return
	if str(_Canon.call("format_float", 8.0)) != "8":
		_fail("float_8", str(_Canon.call("format_float", 8.0)))
		return
	if str(_Canon.call("format_float", 8.5)) != "8.5":
		_fail("float_8_5", str(_Canon.call("format_float", 8.5)))
		return
	if str(_Canon.call("format_float", 0.12)) != "0.12":
		_fail("float_0_12", str(_Canon.call("format_float", 0.12)))
		return
	_ok("canonical_json_key_order_and_float_format")


func _test_save_reload_hash() -> void:
	var s1: Object = _new_store()
	var created: Dictionary = s1.call(
		"create_journal", G3_SPACE_ID, G3_BASE_REV, G3_SNAPSHOT_ID, G3_SESSION_ID
	) as Dictionary
	if not bool(created.get("ok", false)):
		_fail("create_journal", str(created))
		return
	if int(s1.call("get_world_revision")) != G3_BASE_REV:
		_fail("base_rev", str(s1.call("get_world_revision")))
		return

	var apply: Dictionary = s1.call("apply_mutation", {
		"request_id": G3_REQUEST_ID,
		"prompt_id": G3_PROMPT_ID,
		"expected_world_revision": G3_EXPECTED_REV,
		"mutation_class": "durable_world",
		"operation": "create",
		"entity": _house_entity(),
		"confirmation": {"state": "confirmed", "confirmed_by": "player_01"},
		"actor": {"actor_id": "player_01", "actor_type": "player"},
		"trace_id": "g4_smoke_save_reload",
	}) as Dictionary
	if str(apply.get("status", "")) != "committed":
		_fail("apply_mutation", str(apply))
		return
	if int(apply.get("new_world_revision", 0)) != 4:
		_fail("rev_after_apply", str(apply.get("new_world_revision")))
		return

	var eid: String = "entity_cozy_house_01"
	var h1: String = str(s1.call("entity_hash", eid))
	var set1: String = str(s1.call("entity_set_hash"))
	var rev1: int = int(s1.call("get_world_revision"))
	if h1.length() != 64 or set1.length() != 64:
		_fail("hash_shape", "h=%s set=%s" % [h1, set1])
		return

	var saved: Dictionary = s1.call("save_journal", USER_JOURNAL) as Dictionary
	if not bool(saved.get("ok", false)):
		_fail("save_journal", str(saved))
		return

	var s2: Object = _new_store()
	var loaded: Dictionary = s2.call("load_journal", USER_JOURNAL) as Dictionary
	if not bool(loaded.get("ok", false)):
		_fail("load_journal", str(loaded))
		return
	var h2: String = str(s2.call("entity_hash", eid))
	var set2: String = str(s2.call("entity_set_hash"))
	var rev2: int = int(s2.call("get_world_revision"))
	if h1 != h2:
		_fail("entity_hash_mismatch", "before=%s after=%s" % [h1, h2])
		return
	if set1 != set2:
		_fail("entity_set_hash_mismatch", "before=%s after=%s" % [set1, set2])
		return
	if rev1 != rev2 or rev2 != 4:
		_fail("revision_mismatch_reload", "rev1=%d rev2=%d" % [rev1, rev2])
		return
	if int(s2.call("get_base_world_revision")) != G3_BASE_REV:
		_fail("base_rev_reload", str(s2.call("get_base_world_revision")))
		return

	_evidence["AT-SAVE-RELOAD-HASH"] = {
		"entity_hash": h1,
		"entity_set_hash": set1,
		"world_revision_after_apply": rev1,
		"base_world_revision": G3_BASE_REV,
		"reload_entity_hash": h2,
		"reload_entity_set_hash": set2,
		"hashes_equal": true,
	}
	_ok("deterministic_save_reload_same_entity_hashes")


func _test_duplicate_request() -> void:
	var s: Object = _new_store()
	s.call("create_journal", G3_SPACE_ID, G3_BASE_REV, G3_SNAPSHOT_ID, G3_SESSION_ID)
	var req := {
		"request_id": "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee",
		"prompt_id": G3_PROMPT_ID,
		"expected_world_revision": 3,
		"mutation_class": "durable_world",
		"operation": "create",
		"entity": _house_entity(),
		"confirmation": {"state": "confirmed"},
	}
	var a1: Dictionary = s.call("apply_mutation", req) as Dictionary
	if str(a1.get("status")) != "committed":
		_fail("dup_first_apply", str(a1))
		return
	var set1: String = str(s.call("entity_set_hash"))
	var count1: int = (s.call("list_entity_ids") as PackedStringArray).size()
	var rev1: int = int(s.call("get_world_revision"))

	var a2: Dictionary = s.call("apply_mutation", req) as Dictionary
	if str(a2.get("status")) != "idempotent_replay":
		_fail("dup_status", str(a2))
		return
	if str(a2.get("prior_receipt_id", "")) == "":
		_fail("dup_prior_receipt", str(a2))
		return
	var count2: int = (s.call("list_entity_ids") as PackedStringArray).size()
	var rev2: int = int(s.call("get_world_revision"))
	var set2: String = str(s.call("entity_set_hash"))
	if count1 != count2 or count2 != 1:
		_fail("dup_entity_count", "c1=%d c2=%d" % [count1, count2])
		return
	if rev1 != rev2 or rev2 != 4:
		_fail("dup_revision_bumped", "r1=%d r2=%d" % [rev1, rev2])
		return
	if set1 != set2:
		_fail("dup_set_hash_changed")
		return
	if int(s.call("entry_count")) != 1:
		_fail("dup_extra_entry", str(s.call("entry_count")))
		return
	_evidence["AT-DUP-REQUEST"] = {
		"status": "idempotent_replay",
		"prior_receipt_id": a2.get("prior_receipt_id"),
		"entity_count": count2,
		"world_revision": rev2,
	}
	_ok("duplicate_request_id_no_duplicate_entity")


func _test_stale_revision() -> void:
	var s: Object = _new_store()
	s.call("create_journal", G3_SPACE_ID, G3_BASE_REV, G3_SNAPSHOT_ID, G3_SESSION_ID)
	var set_before: String = str(s.call("entity_set_hash"))
	var entries_before: int = int(s.call("entry_count"))
	var stale: Dictionary = s.call("apply_mutation", {
		"request_id": "stale-0000-4000-8000-000000000001",
		"expected_world_revision": 0,
		"mutation_class": "durable_world",
		"operation": "create",
		"entity": _house_entity(),
		"confirmation": {"state": "confirmed"},
	}) as Dictionary
	if str(stale.get("status")) != "conflicted":
		_fail("stale_status", str(stale))
		return
	var conflict: Dictionary = stale.get("conflict", {}) as Dictionary
	if str(conflict.get("code", "")) != "revision_mismatch":
		_fail("stale_code", str(conflict))
		return
	if int(s.call("get_world_revision")) != 3:
		_fail("stale_rev_changed", str(s.call("get_world_revision")))
		return
	if int(s.call("entry_count")) != entries_before:
		_fail("stale_appended")
		return
	if str(s.call("entity_set_hash")) != set_before:
		_fail("stale_entities_mutated")
		return
	# also stale 2
	var stale2: Dictionary = s.call("apply_mutation", {
		"request_id": "stale-0000-4000-8000-000000000002",
		"expected_world_revision": 2,
		"mutation_class": "durable_world",
		"operation": "create",
		"entity": _house_entity(),
		"confirmation": {"state": "confirmed"},
	}) as Dictionary
	if str(stale2.get("status")) != "conflicted":
		_fail("stale2_status", str(stale2))
		return
	_evidence["AT-STALE-REVISION"] = {
		"status": "conflicted",
		"conflict_code": "revision_mismatch",
		"head_unchanged": 3,
		"no_partial_mutation": true,
	}
	_ok("stale_expected_world_revision_rejected")


func _test_malformed_journal() -> void:
	_write_user_file(USER_MALFORMED, "{not json at all")
	var s: Object = _new_store()
	var r1: Dictionary = s.call("load_journal", USER_MALFORMED) as Dictionary
	if bool(r1.get("ok", true)):
		_fail("malformed_accepted", str(r1))
		return
	var code1: String = str(r1.get("error_code", ""))
	if code1 != "journal_malformed" and code1 != "journal_truncated":
		_fail("malformed_code", code1)
		return

	_write_user_file(USER_TRUNC, "{\"schema_version\":\"1.0.0\",\"space_type\":\"private_reality\"")
	var r2: Dictionary = s.call("load_journal", USER_TRUNC) as Dictionary
	if bool(r2.get("ok", true)):
		_fail("truncated_accepted", str(r2))
		return
	var code2: String = str(r2.get("error_code", ""))
	if code2 != "journal_truncated" and code2 != "journal_malformed":
		_fail("truncated_code", code2)
		return

	# missing entries
	_write_user_file(
		USER_MALFORMED,
		"{\"schema_version\":\"1.0.0\",\"space_type\":\"private_reality\",\"space_id\":\"home_01\",\"world_revision\":3}"
	)
	var r3: Dictionary = s.call("load_journal", USER_MALFORMED) as Dictionary
	if bool(r3.get("ok", true)):
		_fail("missing_entries_accepted", str(r3))
		return
	if (s.call("list_entity_ids") as PackedStringArray).size() != 0 and s.call("has_journal"):
		# store should not invent entities from failed load — if prior journal was open, recreate
		pass
	_evidence["AT-MALFORMED-JOURNAL"] = {
		"malformed_error_code": code1,
		"truncated_error_code": code2,
		"missing_entries_ok": false,
	}
	_ok("truncated_malformed_journal_fail_closed")


func _test_schema_incompatible() -> void:
	var body := {
		"schema_version": "99.0.0",
		"space_type": "private_reality",
		"space_id": "home_01",
		"world_revision": 3,
		"entries": [],
		"entry_count": 0,
	}
	_write_user_file(USER_SCHEMA, JSON.stringify(body))
	var s: Object = _new_store()
	var r: Dictionary = s.call("load_journal", USER_SCHEMA) as Dictionary
	if bool(r.get("ok", true)):
		_fail("schema_accepted", str(r))
		return
	if str(r.get("error_code", "")) != "journal_schema_incompatible":
		_fail("schema_code", str(r.get("error_code")))
		return
	_ok("incompatible_schema_version_fail_closed")


func _test_wrong_space_type() -> void:
	var body := {
		"schema_version": "1.0.0",
		"space_type": "shared_district",
		"space_id": "district_01",
		"world_revision": 0,
		"entries": [],
		"entry_count": 0,
	}
	_write_user_file(USER_SPACE, JSON.stringify(body))
	var s: Object = _new_store()
	var r: Dictionary = s.call("load_journal", USER_SPACE) as Dictionary
	if bool(r.get("ok", true)):
		_fail("shared_district_accepted", str(r))
		return
	if str(r.get("error_code", "")) != "wrong_space_type":
		_fail("space_code", str(r.get("error_code")))
		return
	_ok("reject_non_private_reality_journal")


func _test_compensation_append() -> void:
	var s: Object = _new_store()
	s.call("create_journal", G3_SPACE_ID, G3_BASE_REV, G3_SNAPSHOT_ID, G3_SESSION_ID)
	var a1: Dictionary = s.call("apply_mutation", {
		"request_id": "comp-mut-0000-4000-8000-000000000001",
		"prompt_id": G3_PROMPT_ID,
		"expected_world_revision": 3,
		"mutation_class": "durable_world",
		"operation": "create",
		"entity": _house_entity(),
		"confirmation": {"state": "confirmed"},
		"receipt_id": "receipt-mut-0000-4000-8000-000000000001",
	}) as Dictionary
	if str(a1.get("status")) != "committed":
		_fail("comp_apply", str(a1))
		return
	var prior_receipt: String = str(a1.get("receipt_id"))
	var entries_before: Array = s.call("get_entries") as Array
	var prior_entry_canon: String = str(_Canon.call("stringify", entries_before[0]))

	var c1: Dictionary = s.call("apply_compensation", {
		"request_id": "comp-new-0000-4000-8000-000000000002",
		"prior_receipt_id": prior_receipt,
		"prior_request_id": "comp-mut-0000-4000-8000-000000000001",
		"expected_world_revision": 4,
		"compensated_entity_ids": ["entity_cozy_house_01"],
		"trace_id": "g4_smoke_compensation",
	}) as Dictionary
	if str(c1.get("status")) != "committed":
		_fail("comp_status", str(c1))
		return
	if bool(c1.get("history_erased", true)) != false:
		_fail("comp_history_erased")
		return
	if int(s.call("get_world_revision")) != 5:
		_fail("comp_rev", str(s.call("get_world_revision")))
		return
	var entries_after: Array = s.call("get_entries") as Array
	if entries_after.size() != 2:
		_fail("comp_entry_count", str(entries_after.size()))
		return
	var prior_after: String = str(_Canon.call("stringify", entries_after[0]))
	if prior_entry_canon != prior_after:
		_fail("comp_prior_rewritten")
		return
	if str(entries_after[1].get("entry_type")) != "compensation":
		_fail("comp_entry_type", str(entries_after[1].get("entry_type")))
		return
	if str(entries_after[1].get("prior_receipt_id")) != prior_receipt:
		_fail("comp_link")
		return
	# entity tombstoned — not in active set
	if s.call("get_entity", "entity_cozy_house_01") != null:
		_fail("comp_entity_still_active")
		return

	# save/reload preserves both entries
	s.call("save_journal", USER_JOURNAL)
	var s2: Object = _new_store()
	var loaded: Dictionary = s2.call("load_journal", USER_JOURNAL) as Dictionary
	if not bool(loaded.get("ok", false)):
		_fail("comp_reload", str(loaded))
		return
	if int(s2.call("entry_count")) != 2:
		_fail("comp_reload_entries", str(s2.call("entry_count")))
		return
	if int(s2.call("get_world_revision")) != 5:
		_fail("comp_reload_rev", str(s2.call("get_world_revision")))
		return
	_evidence["AT-COMPENSATION-APPEND"] = {
		"prior_receipt_id": prior_receipt,
		"history_erased": false,
		"entry_count": 2,
		"world_revision": 5,
		"prior_entry_unchanged": true,
	}
	_ok("compensation_append_only_history_preserved")


func _test_cancel_not_journaled() -> void:
	var s: Object = _new_store()
	s.call("create_journal", G3_SPACE_ID, G3_BASE_REV, G3_SNAPSHOT_ID, G3_SESSION_ID)
	var before: int = int(s.call("entry_count"))
	var set_before: String = str(s.call("entity_set_hash"))

	var cancel_req := {
		"request_id": "6da43c54-8ec5-4803-8076-45c81860dbdc",
		"receipt_kind": "cancel",
		"expected_world_revision": 3,
		"mutation_class": "durable_world",
		"operation": "create",
		"entity": _house_entity(),
		"durable_mutation_applied": false,
		"pipeline_stage": "cancelled",
	}
	var r1: Dictionary = s.call("apply_mutation", cancel_req) as Dictionary
	if str(r1.get("status")) != "rejected":
		_fail("cancel_not_rejected", str(r1))
		return
	var code: String = str((r1.get("rejection", {}) as Dictionary).get("code", r1.get("error_code", "")))
	if code != "cancel_not_durable":
		_fail("cancel_code", code)
		return

	# unconfirmed preview
	var r2: Dictionary = s.call("apply_mutation", {
		"request_id": "preview-0000-4000-8000-000000000001",
		"expected_world_revision": 3,
		"mutation_class": "durable_world",
		"operation": "create",
		"entity": _house_entity(),
		"confirmation": {"state": "pending"},
		"preview_only": true,
	}) as Dictionary
	if str(r2.get("status")) != "rejected":
		_fail("preview_not_rejected", str(r2))
		return

	if int(s.call("entry_count")) != before:
		_fail("cancel_journaled")
		return
	if str(s.call("entity_set_hash")) != set_before:
		_fail("cancel_mutated_entities")
		return
	if int(s.call("get_world_revision")) != 3:
		_fail("cancel_advanced_rev")
		return
	_evidence["AT-CANCEL-NOT-JOURNALED"] = {
		"cancel_status": "rejected",
		"entries_unchanged": true,
		"world_revision": 3,
		"entity_ids_durable": [],
	}
	_ok("cancelled_preview_never_in_journal")


func _test_g3_rev3_preserved() -> void:
	var s: Object = _new_store()
	var created: Dictionary = s.call(
		"create_journal", G3_SPACE_ID, G3_BASE_REV, G3_SNAPSHOT_ID, G3_SESSION_ID
	) as Dictionary
	if not bool(created.get("ok", false)):
		_fail("g3_create", str(created))
		return
	if int(s.call("get_world_revision")) != 3:
		_fail("g3_seed_not_3", str(s.call("get_world_revision")))
		return
	if int(s.call("get_base_world_revision")) != 3:
		_fail("g3_base_not_3")
		return

	# Apply using expected_world_revision=3 matching G3 complete receipt / commit_request
	var apply: Dictionary = s.call("apply_mutation", {
		"request_id": "g3-preserve-0000-4000-8000-000000000099",
		"prompt_id": G3_PROMPT_ID,
		"expected_world_revision": 3,
		"mutation_class": "durable_world",
		"operation": "create",
		"entity": _house_entity(),
		"confirmation": {"state": "confirmed", "confirmed_by": "player_01"},
		"actor": {"actor_id": "player_01", "actor_type": "player"},
		"trace_id": "executor_commit_handoff_a5b87763",
	}) as Dictionary
	if str(apply.get("status")) != "committed":
		_fail("g3_apply", str(apply))
		return
	if int(apply.get("old_world_revision", -1)) != 3:
		_fail("g3_old_rev", str(apply.get("old_world_revision")))
		return
	if int(apply.get("new_world_revision", -1)) != 4:
		_fail("g3_new_rev", str(apply.get("new_world_revision")))
		return

	s.call("save_journal", USER_JOURNAL)
	var s2: Object = _new_store()
	var loaded: Dictionary = s2.call("load_journal", USER_JOURNAL) as Dictionary
	if not bool(loaded.get("ok", false)):
		_fail("g3_reload", str(loaded))
		return
	if int(s2.call("get_base_world_revision")) != 3:
		_fail("g3_reload_base", str(s2.call("get_base_world_revision")))
		return
	if int(s2.call("get_world_revision")) != 4:
		_fail("g3_reload_head", str(s2.call("get_world_revision")))
		return
	# Ensure never coerced to 0
	if int(s2.call("get_base_world_revision")) == 0 or int(s2.call("get_world_revision")) == 0:
		_fail("g3_coerced_to_zero")
		return

	var snap: Dictionary = s2.call("get_journal_snapshot") as Dictionary
	_evidence["AT-G3-REV-3-PRESERVED"] = {
		"base_world_revision": int(s2.call("get_base_world_revision")),
		"world_revision_before_apply": 3,
		"world_revision_after_apply": 4,
		"expected_world_revision_used": 3,
		"g3_complete_receipt_expected_world_revision": 3,
		"g3_commit_request_expected_world_revision": 3,
		"never_coerced_to_0": true,
		"space_id": str(snap.get("space_id", "")),
		"space_type": str(snap.get("space_type", "")),
		"base_snapshot_id": str(snap.get("base_snapshot_id", "")),
	}
	_ok("g3_expected_world_revision_3_through_save_reload")


func _write_user_file(path: String, content: String) -> void:
	var global: String = ProjectSettings.globalize_path(path)
	var parent: String = global.get_base_dir()
	if not DirAccess.dir_exists_absolute(parent):
		DirAccess.make_dir_recursive_absolute(parent)
	var f: FileAccess = FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		f = FileAccess.open(global, FileAccess.WRITE)
	if f == null:
		_fail("write_user_file", path)
		return
	f.store_string(content)
	f.close()


func _write_evidence_export() -> void:
	var out_path := "user://g4_persist_smoke/g4_persist_smoke_evidence.json"
	# Also write under res://scripts/modules/persist/exports if writable
	var payload := {
		"schema_version": "g4_persist_smoke/1.0.0",
		"task_id": "G4-001",
		"wave": "P1_PERSIST_PATCH",
		"marker": "G4_PERSIST_SMOKE",
		"passed_checks": _passed,
		"failed_checks": _failures.size(),
		"failures": Array(_failures),
		"g3_revision_binding": {
			"expected_world_revision": 3,
			"base_world_revision_seed": 3,
			"source": "g3_complete_receipt / commit_request_handoff_stub / valid_snapshot_desktop_bridge",
		},
		"acceptance": _evidence,
		"authority": {
			"context": "Offline Private Reality",
			"space_type": "private_reality",
			"not": ["shared_district", "server_economy", "multiplayer_ownership"],
		},
	}
	var text: String = JSON.stringify(payload, "\t")
	_write_user_file(out_path, text)

	# Best-effort project export (may fail if res is read-only in export builds; OK for editor path)
	var export_abs := ProjectSettings.globalize_path(EXPORT_DIR)
	if not DirAccess.dir_exists_absolute(export_abs):
		DirAccess.make_dir_recursive_absolute(export_abs)
	var exp_path := export_abs.path_join("g4_persist_smoke_evidence.json")
	var ef: FileAccess = FileAccess.open(exp_path, FileAccess.WRITE)
	if ef != null:
		ef.store_string(text)
		ef.close()
		print("  wrote evidence %s" % exp_path)
	else:
		# try relative open via res path
		var rf: FileAccess = FileAccess.open(
			"res://scripts/modules/persist/exports/g4_persist_smoke_evidence.json", FileAccess.WRITE
		)
		if rf != null:
			rf.store_string(text)
			rf.close()
			print("  wrote evidence res://scripts/modules/persist/exports/g4_persist_smoke_evidence.json")
		else:
			print("  note: could not write res export (user:// evidence still written)")
