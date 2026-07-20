## Headless smoke for G2-005 Free Desktop Bridge.
## Run:
##   tools\Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://scripts/modules/bridge/desktop_bridge_smoke.gd
##
## Exit 0 on pass. Prints G2-005_GODOT_SMOKE=PASS|FAIL.
## Any required-script load/parse/instantiate failure is a hard FAIL (no PASS beside errors).
extends SceneTree

const PATHS_PATH := "res://scripts/modules/bridge/bridge_paths.gd"
const BUILDER_PATH := "res://scripts/modules/bridge/snapshot_builder.gd"
const GUARD_PATH := "res://scripts/modules/bridge/decision_import_guard.gd"
const MODULE_PATH := "res://scripts/modules/bridge/desktop_bridge_module.gd"
const IFACE_PATH := "res://scripts/modules/interfaces/i_desktop_bridge_module.gd"
const CONSENT_SCENE := "res://scenes/ui/bridge_consent_dialog.tscn"
const CONSENT_SCRIPT := "res://scripts/modules/bridge/bridge_consent_dialog.gd"

var _failures: PackedStringArray = []
var _passed: int = 0
var _fatal: bool = false
var _Builder: GDScript
var _Guard: GDScript
var _Module: GDScript
var _Iface: GDScript
var _Paths: GDScript
var _ConsentScript: GDScript


func _initialize() -> void:
	print("[G2-005 smoke] starting…")

	_Paths = _require_script(PATHS_PATH, "BridgePaths")
	_Builder = _require_script(BUILDER_PATH, "BridgeSnapshotBuilder")
	_Guard = _require_script(GUARD_PATH, "BridgeDecisionImportGuard")
	_Module = _require_script(MODULE_PATH, "DesktopBridgeModule")
	_Iface = _require_script(IFACE_PATH, "IDesktopBridgeModule")
	_ConsentScript = _require_script(CONSENT_SCRIPT, "bridge_consent_dialog")

	if not ResourceLoader.exists(CONSENT_SCENE):
		_fail("consent_scene_missing", CONSENT_SCENE)
		_fatal = true

	if _fatal or not _failures.is_empty():
		printerr("[G2-005 smoke] hard fail during script load — aborting tests")
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
	_test_consent_scene_loads()

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
	if script == null:
		_fail("script_not_gdscript", "%s path=%s" % [label, path])
		_fatal = true
		return null
	# Parse/compile failures leave a GDScript that cannot instantiate.
	if not script.can_instantiate():
		_fail("script_cannot_instantiate", "%s path=%s (parse/compile error)" % [label, path])
		_fatal = true
		return null
	print("  LOAD OK  %s" % label)
	return script


func _finish() -> void:
	# Fail-closed: any recorded failure → FAIL (never PASS beside errors).
	if _failures.is_empty() and not _fatal:
		print("G2-005_GODOT_SMOKE=PASS checks=%d" % _passed)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print(
			"G2-005_GODOT_SMOKE=FAIL failed=%d passed=%d fatal=%s"
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


func _new_module() -> Node:
	if _Module == null or not _Module.can_instantiate():
		_fail("module_script_unavailable")
		return null
	var instance: Object = _Module.new()
	if instance == null:
		_fail("module_new_null")
		return null
	var mod: Node = instance as Node
	if mod == null:
		_fail("module_not_node")
		return null
	mod.set("show_consent_ui", false)
	root.add_child(mod)
	return mod


func _test_snapshot_export_structure() -> void:
	if _Builder == null or not _Builder.can_instantiate():
		_fail("builder_unavailable")
		return
	var builder: Object = _Builder.new()
	if builder == null:
		_fail("builder_new_null")
		return
	var snap_v: Variant = builder.call("build", {
		"snapshot_id": "11111111-1111-4111-8111-111111111111",
		"session_id": "session_starter_01",
	})
	if typeof(snap_v) != TYPE_DICTIONARY:
		_fail("snapshot_not_dict")
		return
	var snap: Dictionary = snap_v
	var errs_v: Variant = builder.call("validate_structure", snap)
	var errs: PackedStringArray = errs_v as PackedStringArray
	if errs == null:
		# Fallback if typed array boxing differs
		if typeof(errs_v) == TYPE_PACKED_STRING_ARRAY:
			errs = errs_v
		else:
			_fail("validate_structure_type")
			return
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
	if mod == null:
		return
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
	var live_id: String = str(mod.call("get_live_snapshot_id"))
	if live_id != "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa":
		_fail("live_snapshot_id", live_id)
		mod.queue_free()
		return
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		_fail("export_file_open")
		mod.queue_free()
		return
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
	if mod == null:
		return
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
	var accepted: Dictionary = mod.call("get_accepted_decision")
	if not accepted.is_empty():
		_fail("auto_applied_without_consent")
		mod.queue_free()
		return
	_ok("import_valid_requires_consent")
	mod.queue_free()


func _test_confirm_accepts() -> void:
	var mod := _new_module()
	if mod == null:
		return
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
	if mod == null:
		return
	mod.call("set_live_snapshot_for_tests", "11111111-1111-4111-8111-111111111111")
	var result: Dictionary = mod.call("import_decision_from_text", "this is not json {{{", false)
	if bool(result.get("ok", true)):
		_fail("malformed_should_reject")
		mod.queue_free()
		return
	var reason := str(result.get("reason", ""))
	if reason.is_empty():
		_fail("malformed_reason_empty")
		mod.queue_free()
		return
	_ok("reject_malformed")
	mod.queue_free()


func _test_reject_forbidden_script() -> void:
	var mod := _new_module()
	if mod == null:
		return
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
	if mod == null:
		return
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
	if mod == null:
		return
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
	if mod == null:
		return
	if bool(mod.call("uses_network")):
		_fail("uses_network_true")
		mod.queue_free()
		return
	_ok("no_network")
	mod.queue_free()


func _test_interface_surface() -> void:
	if _Iface == null or not _Iface.can_instantiate():
		_fail("iface_unavailable")
		return
	var mod := _new_module()
	if mod == null:
		return
	var missing: PackedStringArray = _Iface.call("validate", mod) as PackedStringArray
	if missing == null:
		_fail("iface_validate_type")
		mod.queue_free()
		return
	if not missing.is_empty():
		_fail("iface_methods", ", ".join(missing))
		mod.queue_free()
		return
	var net_issues: PackedStringArray = _Iface.call("audit_no_network", mod) as PackedStringArray
	if net_issues == null:
		_fail("iface_audit_type")
		mod.queue_free()
		return
	if not net_issues.is_empty():
		_fail("iface_network", ", ".join(net_issues))
		mod.queue_free()
		return
	_ok("interface_surface")
	mod.queue_free()


func _test_consent_scene_loads() -> void:
	if not ResourceLoader.exists(CONSENT_SCENE):
		_fail("consent_scene_missing")
		return
	var scene: PackedScene = load(CONSENT_SCENE) as PackedScene
	if scene == null:
		_fail("consent_scene_load_null")
		return
	var node: Node = scene.instantiate() as Node
	if node == null:
		_fail("consent_scene_instantiate_null")
		return
	if not node.has_method("bind") or not node.has_method("open_dialog"):
		_fail("consent_scene_methods")
		node.queue_free()
		return
	node.queue_free()
	_ok("consent_scene_loads")
