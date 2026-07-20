## Headless smoke for G2-005 Free Desktop Bridge.
## Run:
##   tools\Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://scripts/modules/bridge/desktop_bridge_smoke.gd
##
## Exit 0 on pass. Prints G2-005_GODOT_SMOKE=PASS|FAIL.
## Uses load() (not only class_name) so concurrent broken modules cannot block.
extends SceneTree

const PATHS_PATH := "res://scripts/modules/bridge/bridge_paths.gd"
const BUILDER_PATH := "res://scripts/modules/bridge/snapshot_builder.gd"
const GUARD_PATH := "res://scripts/modules/bridge/decision_import_guard.gd"
const MODULE_PATH := "res://scripts/modules/bridge/desktop_bridge_module.gd"
const IFACE_PATH := "res://scripts/modules/interfaces/i_desktop_bridge_module.gd"

const FIXTURE_DECISION := "res://../contracts/fixtures/agm/valid/valid_decision_desktop_bridge.json"
const FIXTURE_STALE := "res://../contracts/fixtures/agm/policy/stale_snapshot_rejection.json"
const FIXTURE_REPLAY := "res://../contracts/fixtures/agm/policy/replay_decision_pair.json"
const FIXTURE_BAD_SCRIPT := "res://../contracts/fixtures/agm/invalid/invalid_decision_with_script_code.json"
const FIXTURE_MISSING := "res://../contracts/fixtures/agm/invalid/invalid_decision_missing_required.json"

var _failures: PackedStringArray = []
var _passed: int = 0
var _Builder: GDScript
var _Guard: GDScript
var _Module: GDScript
var _Iface: GDScript
var _Paths: GDScript


func _initialize() -> void:
	print("[G2-005 smoke] starting…")
	_Paths = load(PATHS_PATH) as GDScript
	_Builder = load(BUILDER_PATH) as GDScript
	_Guard = load(GUARD_PATH) as GDScript
	_Module = load(MODULE_PATH) as GDScript
	_Iface = load(IFACE_PATH) as GDScript

	if _Builder == null or _Guard == null or _Module == null:
		_fail("load_scripts", "builder/guard/module load failed")
		_finish()
		return

	_test_snapshot_export_structure()
	_test_export_file_roundtrip()
	_test_import_valid_requires_consent()
	_test_confirm_accepts()
	_test_reject_malformed()
	_test_reject_forbidden_script()
	_test_reject_stale()
	_test_reject_replay()
	_test_no_network()
	_test_interface_surface()

	_finish()


func _finish() -> void:
	if _failures.is_empty():
		print("G2-005_GODOT_SMOKE=PASS checks=%d" % _passed)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print("G2-005_GODOT_SMOKE=FAIL failed=%d passed=%d" % [_failures.size(), _passed])
		quit(1)


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)


func _new_module() -> Node:
	var mod: Node = _Module.new() as Node
	mod.set("show_consent_ui", false)
	# Attach so Node lifecycle is valid; ModuleRegistry may register on _ready.
	root.add_child(mod)
	return mod


func _read_project_json(rel_from_game: String) -> Variant:
	# game/ is project root for --path game; contracts sit one level up.
	var path := ProjectSettings.globalize_path("res://").path_join("..").path_join(
		rel_from_game.trim_prefix("res://../")
	) if rel_from_game.begins_with("res://../") else ProjectSettings.globalize_path(rel_from_game)
	# Normalize: prefer absolute path from known workspace layout.
	if rel_from_game.begins_with("res://../"):
		var game_root := ProjectSettings.globalize_path("res://")
		path = game_root.path_join("..").path_join(rel_from_game.substr(len("res://../")))
		path = path.simplify_path()
	if not FileAccess.file_exists(path):
		# Fallback absolute relative to this script location is unreliable; try user fixtures copy.
		return null
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return null
	var text := f.get_as_text()
	f.close()
	var json := JSON.new()
	if json.parse(text) != OK:
		return null
	return json.data


func _test_snapshot_export_structure() -> void:
	var builder = _Builder.new()
	var snap: Dictionary = builder.build({
		"snapshot_id": "11111111-1111-4111-8111-111111111111",
		"session_id": "session_starter_01",
	})
	var errs: PackedStringArray = builder.validate_structure(snap)
	if not errs.is_empty():
		_fail("snapshot_structure", ", ".join(errs))
		return
	if str(snap.get("edition", "")) != "desktop_bridge_free":
		_fail("snapshot_edition")
		return
	if str(snap.get("schema_version", "")) != "1.0.0":
		_fail("snapshot_schema_version")
		return
	for bad in ["api_key", "credentials", "tts_audio", "system_prompt"]:
		if snap.has(bad):
			_fail("snapshot_forbidden", bad)
			return
	_ok("snapshot_export_structure")


func _test_export_file_roundtrip() -> void:
	var mod := _new_module()
	var result: Dictionary = mod.call("export_snapshot_to_file", {
		"snapshot_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
	})
	if not bool(result.get("ok", false)):
		_fail("export_file", str(result))
		mod.queue_free()
		return
	var path := str(result.get("path", ""))
	if not FileAccess.file_exists(path):
		_fail("export_file_missing", path)
		mod.queue_free()
		return
	var live_id: String = mod.call("get_live_snapshot_id")
	if live_id != "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa":
		_fail("live_snapshot_id", live_id)
		mod.queue_free()
		return
	# Structural re-read
	var f := FileAccess.open(path, FileAccess.READ)
	var text := f.get_as_text()
	f.close()
	var json := JSON.new()
	if json.parse(text) != OK:
		_fail("export_file_parse")
		mod.queue_free()
		return
	if typeof(json.data) != TYPE_DICTIONARY:
		_fail("export_file_not_object")
		mod.queue_free()
		return
	_ok("export_file_roundtrip")
	mod.queue_free()


func _test_import_valid_requires_consent() -> void:
	var mod := _new_module()
	mod.call("export_snapshot_to_file", {
		"snapshot_id": "11111111-1111-4111-8111-111111111111",
	})
	var decision := {
		"schema_version": "1.0.0",
		"decision_id": "22222222-2222-4222-8222-222222222222",
		"source_snapshot_id": "11111111-1111-4111-8111-111111111111",
		"created_at": "2026-07-20T16:00:05Z",
		"edition": "desktop_bridge_free",
		"session_id": "session_starter_01",
		"dialogue": {
			"lines": [{"speaker": "companion", "text": "Hello from smoke."}],
			"companion_expression": "warm",
		},
		"quest_operations": [],
		"build_proposals": [],
		"event_proposals": [],
		"mood_delta": {"delta": 0.02},
		"relationship_delta": {"delta": 0.01},
		"next_trigger": {"kind": "player_action"},
		"trace": {"trace_id": "t1", "model_receipt_ref": "bridge:smoke:1"},
	}
	var raw := JSON.stringify(decision)
	var result: Dictionary = mod.call("import_decision_from_text", raw, false)
	if not bool(result.get("ok", false)):
		_fail("import_valid", str(result))
		mod.queue_free()
		return
	if str(result.get("status", "")) != "awaiting_consent":
		_fail("awaiting_consent", str(result.get("status", "")))
		mod.queue_free()
		return
	if not bool(mod.call("has_pending_consent")):
		_fail("has_pending_consent")
		mod.queue_free()
		return
	# Must NOT be accepted yet without confirm.
	var accepted: Dictionary = mod.call("get_accepted_decision")
	if not accepted.is_empty():
		_fail("auto_applied_without_consent")
		mod.queue_free()
		return
	_ok("import_valid_requires_consent")
	mod.queue_free()


func _test_confirm_accepts() -> void:
	var mod := _new_module()
	mod.call("export_snapshot_to_file", {
		"snapshot_id": "11111111-1111-4111-8111-111111111111",
	})
	var decision := {
		"schema_version": "1.0.0",
		"decision_id": "33333333-3333-4333-8333-333333333333",
		"source_snapshot_id": "11111111-1111-4111-8111-111111111111",
		"created_at": "2026-07-20T16:00:05Z",
		"edition": "desktop_bridge_free",
		"session_id": "session_starter_01",
		"dialogue": {"lines": [{"speaker": "companion", "text": "Confirm me."}]},
		"quest_operations": [],
		"build_proposals": [],
		"event_proposals": [],
		"mood_delta": {"delta": 0.0},
		"relationship_delta": {"delta": 0.0},
		"next_trigger": {"kind": "none"},
		"trace": {"trace_id": "t2", "model_receipt_ref": "bridge:smoke:2"},
	}
	mod.call("import_decision_from_text", JSON.stringify(decision), false)
	var conf: Dictionary = mod.call("confirm_pending_decision")
	if not bool(conf.get("ok", false)) or not bool(conf.get("accepted", false)):
		_fail("confirm_accepts", str(conf))
		mod.queue_free()
		return
	if bool(conf.get("executed", true)):
		_fail("bridge_must_not_execute")
		mod.queue_free()
		return
	var seen: PackedStringArray = mod.call("list_seen_decision_ids")
	if not seen.has("33333333-3333-4333-8333-333333333333"):
		_fail("seen_decision_ids")
		mod.queue_free()
		return
	_ok("confirm_accepts_no_execute")
	mod.queue_free()


func _test_reject_malformed() -> void:
	var mod := _new_module()
	mod.call("set_live_snapshot_for_tests", "11111111-1111-4111-8111-111111111111")
	var result: Dictionary = mod.call("import_decision_from_text", "this is not json {{{", false)
	if bool(result.get("ok", true)):
		_fail("malformed_should_reject")
		mod.queue_free()
		return
	if str(result.get("reason", "")) != "malformed_json" and str(result.get("reason", "")) != "empty_input":
		# parse may yield malformed_json
		if str(result.get("reason", "")) == "":
			_fail("malformed_reason_empty")
			mod.queue_free()
			return
	_ok("reject_malformed")
	mod.queue_free()


func _test_reject_forbidden_script() -> void:
	var mod := _new_module()
	mod.call("set_live_snapshot_for_tests", "11111111-1111-4111-8111-111111111111")
	var bad := {
		"schema_version": "1.0.0",
		"decision_id": "22222222-2222-4222-8222-222222222222",
		"source_snapshot_id": "11111111-1111-4111-8111-111111111111",
		"created_at": "2026-07-20T16:00:05Z",
		"edition": "desktop_bridge_free",
		"session_id": "session_starter_01",
		"dialogue": {"lines": []},
		"quest_operations": [],
		"build_proposals": [],
		"event_proposals": [],
		"mood_delta": {"delta": 0.0},
		"relationship_delta": {"delta": 0.0},
		"next_trigger": {"kind": "none"},
		"trace": {"trace_id": "t", "model_receipt_ref": "x"},
		"script": "print('no')",
		"code": "func _ready(): pass",
	}
	var result: Dictionary = mod.call("import_decision_from_text", JSON.stringify(bad), false)
	if bool(result.get("ok", true)):
		_fail("forbidden_script_accepted")
		mod.queue_free()
		return
	var reason := str(result.get("reason", ""))
	if reason != "forbidden_field" and reason != "schema_invalid":
		_fail("forbidden_reason", reason)
		mod.queue_free()
		return
	_ok("reject_forbidden_script")
	mod.queue_free()


func _test_reject_stale() -> void:
	var mod := _new_module()
	# Live snapshot is bbbb…; decision points at 1111… → stale.
	mod.call("set_live_snapshot_for_tests", "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb")
	var stale := {
		"schema_version": "1.0.0",
		"decision_id": "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
		"source_snapshot_id": "11111111-1111-4111-8111-111111111111",
		"created_at": "2026-07-20T16:00:05Z",
		"edition": "desktop_bridge_free",
		"session_id": "session_starter_01",
		"dialogue": {"lines": [{"speaker": "companion", "text": "stale"}]},
		"quest_operations": [],
		"build_proposals": [],
		"event_proposals": [],
		"mood_delta": {"delta": 0.0},
		"relationship_delta": {"delta": 0.0},
		"next_trigger": {"kind": "none"},
		"trace": {"trace_id": "trace_stale", "model_receipt_ref": "bridge:decision:stale"},
	}
	var result: Dictionary = mod.call("import_decision_from_text", JSON.stringify(stale), false)
	if bool(result.get("ok", true)):
		_fail("stale_accepted")
		mod.queue_free()
		return
	if str(result.get("reason", "")) != "stale_snapshot":
		_fail("stale_reason", str(result.get("reason", "")))
		mod.queue_free()
		return
	_ok("reject_stale_snapshot")
	mod.queue_free()


func _test_reject_replay() -> void:
	var mod := _new_module()
	mod.call("set_live_snapshot_for_tests", "11111111-1111-4111-8111-111111111111")
	var decision_id := "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
	mod.call("mark_decision_seen_for_tests", decision_id)
	var replay := {
		"schema_version": "1.0.0",
		"decision_id": decision_id,
		"source_snapshot_id": "11111111-1111-4111-8111-111111111111",
		"created_at": "2026-07-20T16:00:06Z",
		"edition": "desktop_bridge_free",
		"session_id": "session_starter_01",
		"dialogue": {"lines": [{"speaker": "companion", "text": "replay"}]},
		"quest_operations": [],
		"build_proposals": [],
		"event_proposals": [],
		"mood_delta": {"delta": 0.05},
		"relationship_delta": {"delta": 0.02},
		"next_trigger": {"kind": "none"},
		"trace": {"trace_id": "trace_replay_demo", "model_receipt_ref": "bridge:decision:replay"},
	}
	var result: Dictionary = mod.call("import_decision_from_text", JSON.stringify(replay), false)
	if bool(result.get("ok", true)):
		_fail("replay_accepted")
		mod.queue_free()
		return
	if str(result.get("reason", "")) != "replayed_decision":
		_fail("replay_reason", str(result.get("reason", "")))
		mod.queue_free()
		return
	_ok("reject_replayed_decision")
	mod.queue_free()


func _test_no_network() -> void:
	var mod := _new_module()
	if bool(mod.call("uses_network")):
		_fail("uses_network_true")
		mod.queue_free()
		return
	_ok("no_network")
	mod.queue_free()


func _test_interface_surface() -> void:
	if _Iface == null:
		_fail("iface_load")
		return
	var mod := _new_module()
	var missing: PackedStringArray = _Iface.validate(mod)
	if not missing.is_empty():
		_fail("iface_methods", ", ".join(missing))
		mod.queue_free()
		return
	var net_issues: PackedStringArray = _Iface.audit_no_network(mod)
	if not net_issues.is_empty():
		_fail("iface_network", ", ".join(net_issues))
		mod.queue_free()
		return
	_ok("interface_surface")
	mod.queue_free()
