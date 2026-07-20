## Headless smoke for G5-001 Paid AGM Gateway client adapter (A2).
## Run:
##   tools\Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://scripts/modules/bridge/paid_gateway_smoke.gd
##
## Exit 0 on pass. Prints G5_PAID_ADAPTER_SMOKE=PASS|FAIL.
## Proves: no secret patterns, edition api_paid, untrusted proposal, no network/SDK.
extends SceneTree

const ADAPTER_PATH := "res://scripts/modules/bridge/paid_gateway_adapter.gd"
const IFACE_PATH := "res://scripts/modules/interfaces/i_paid_gateway_adapter.gd"
const BUILDER_PATH := "res://scripts/modules/bridge/snapshot_builder.gd"
const GUARD_PATH := "res://scripts/modules/bridge/decision_import_guard.gd"
const FIXTURE_DECISION := "res://scripts/modules/bridge/exports/valid_decision_api_paid.json"
const FIXTURE_SNAPSHOT := "res://scripts/modules/bridge/exports/valid_snapshot_api_paid.json"

## Built at runtime so source files never contain live-looking credential prefixes.

const NETWORK_SYMBOLS := [
	"HTTPRequest",
	"HTTPClient",
	"WebSocketPeer",
	"WebSocketClient",
	"PacketPeerUDP",
	"StreamPeerTCP",
]

var _failures: PackedStringArray = []
var _passed: int = 0
var _fatal: bool = false
var _Adapter: GDScript
var _Iface: GDScript


func _initialize() -> void:
	print("[G5-001 A2 smoke] starting…")

	_Adapter = _require_script(ADAPTER_PATH, "PaidGatewayAdapter")
	_Iface = _require_script(IFACE_PATH, "IPaidGatewayAdapter")
	_require_script(BUILDER_PATH, "BridgeSnapshotBuilder")
	_require_script(GUARD_PATH, "BridgeDecisionImportGuard")

	if not ResourceLoader.exists(FIXTURE_DECISION):
		_fail("fixture_decision_missing", FIXTURE_DECISION)
		_fatal = true
	if not ResourceLoader.exists(FIXTURE_SNAPSHOT):
		_fail("fixture_snapshot_missing", FIXTURE_SNAPSHOT)
		_fatal = true

	if _fatal or not _failures.is_empty():
		printerr("[G5-001 A2 smoke] hard fail during load — aborting")
		_finish()
		return

	_test_source_secret_scan()
	_test_source_no_network_symbols()
	_test_interface_surface()
	_test_snapshot_api_paid_identity()
	_test_happy_path_untrusted_proposal()
	_test_consent_required_no_commit()
	_test_confirm_no_execute()
	_test_validation_error_category()
	_test_budget_reject()
	_test_policy_provider_mode()
	_test_error_categories_list()
	_test_idempotency_replay()
	_test_fixture_files_no_secrets()
	_test_production_path_note()

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
	if not script.can_instantiate():
		_fail("script_cannot_instantiate", "%s path=%s (parse/compile error)" % [label, path])
		_fatal = true
		return null
	print("  LOAD OK  %s" % label)
	return script


func _finish() -> void:
	if _failures.is_empty() and not _fatal:
		print("G5_PAID_ADAPTER_SMOKE=PASS checks=%d" % _passed)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print(
			"G5_PAID_ADAPTER_SMOKE=FAIL failed=%d passed=%d fatal=%s"
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


func _new_adapter() -> Node:
	if _Adapter == null or not _Adapter.can_instantiate():
		_fail("adapter_script_unavailable")
		return null
	var instance: Object = _Adapter.new()
	if instance == null:
		_fail("adapter_new_null")
		return null
	var mod: Node = instance as Node
	if mod == null:
		_fail("adapter_not_node")
		return null
	mod.set("show_consent_ui", false)
	root.add_child(mod)
	return mod


func _read_text(path: String) -> String:
	var open_path := path
	if path.begins_with("res://"):
		if not FileAccess.file_exists(path):
			open_path = ProjectSettings.globalize_path(path)
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		f = FileAccess.open(open_path, FileAccess.READ)
	if f == null:
		return ""
	var t := f.get_as_text()
	f.close()
	return t


func _live_secret_value_markers() -> PackedStringArray:
	# Construct markers without embedding vendor key prefixes as contiguous source literals.
	var markers: PackedStringArray = PackedStringArray()
	markers.append("sk" + "-" + "proj" + "-")
	markers.append("sk" + "-" + "ant" + "-")
	markers.append("-----BEGIN " + "PRIVATE KEY-----")
	markers.append("-----BEGIN " + "RSA PRIVATE KEY-----")
	return markers


func _test_source_secret_scan() -> void:
	var paths := [ADAPTER_PATH, IFACE_PATH, FIXTURE_DECISION, FIXTURE_SNAPSHOT]
	var markers := _live_secret_value_markers()
	for path in paths:
		var text := _read_text(path)
		if text.is_empty() and path.begins_with("res://scripts"):
			_fail("source_unreadable", path)
			return
		for pat in markers:
			if pat in text:
				_fail("live_secret_value", "%s contains live-looking token" % path)
				return
		# JSON fixtures must not carry deny-list payload keys
		if path.ends_with(".json"):
			for bad_key in ["\"api_key\"", "\"access_token\"", "\"password\"", "\"credentials\"", "\"provider_credentials\""]:
				if bad_key in text:
					_fail("fixture_deny_key", "%s has %s" % [path, bad_key])
					return
	_ok("source_secret_scan")


func _test_source_no_network_symbols() -> void:
	var text := _read_text(ADAPTER_PATH)
	if text.is_empty():
		_fail("adapter_source_empty")
		return
	for sym in NETWORK_SYMBOLS:
		# Allow listing in comments/constants as forbidden symbols only
		if sym in text:
			# Check it's only in a comment or string list of forbidden items
			var lines := text.split("\n")
			for line in lines:
				if sym in line and not line.strip_edges().begins_with("#") and "FORBIDDEN" not in line and "NETWORK" not in line:
					# actual usage like HTTPRequest.new() would fail
					if ".new(" in line or "extends " + sym in line or ":" + sym in line or " = " + sym in line:
						_fail("network_symbol_used", line.strip_edges())
						return
	_ok("source_no_network_symbols")


func _test_interface_surface() -> void:
	if _Iface == null or not _Iface.can_instantiate():
		_fail("iface_unavailable")
		return
	var mod := _new_adapter()
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
	if net_issues == null or not net_issues.is_empty():
		_fail("iface_network", "" if net_issues == null else ", ".join(net_issues))
		mod.queue_free()
		return
	var sec_issues: PackedStringArray = _Iface.call("audit_no_secrets", mod) as PackedStringArray
	if sec_issues == null or not sec_issues.is_empty():
		_fail("iface_secrets", "" if sec_issues == null else ", ".join(sec_issues))
		mod.queue_free()
		return
	if bool(mod.call("uses_network")):
		_fail("uses_network_true")
		mod.queue_free()
		return
	if bool(mod.call("holds_provider_secrets")):
		_fail("holds_provider_secrets_true")
		mod.queue_free()
		return
	if str(mod.call("get_edition")) != "api_paid":
		_fail("edition_identity", str(mod.call("get_edition")))
		mod.queue_free()
		return
	if str(mod.call("get_provider_mode")) != "fixture":
		_fail("provider_mode", str(mod.call("get_provider_mode")))
		mod.queue_free()
		return
	_ok("interface_surface")
	mod.queue_free()


func _test_snapshot_api_paid_identity() -> void:
	var mod := _new_adapter()
	if mod == null:
		return
	var snap: Dictionary = mod.call("build_snapshot", {
		"snapshot_id": "11111111-1111-4111-8111-111111111111",
		"session_id": "session_starter_01",
	})
	if str(snap.get("edition", "")) != "api_paid":
		_fail("snapshot_edition", str(snap.get("edition", "")))
		mod.queue_free()
		return
	if str(snap.get("schema_version", "")) != "1.0.0":
		_fail("snapshot_schema_version")
		mod.queue_free()
		return
	var transport: Variant = snap.get("transport", {})
	if typeof(transport) != TYPE_DICTIONARY:
		_fail("snapshot_transport_type")
		mod.queue_free()
		return
	if str((transport as Dictionary).get("channel", "")) != "api_gateway":
		_fail("snapshot_transport_channel", str((transport as Dictionary).get("channel", "")))
		mod.queue_free()
		return
	for bad in ["api_key", "credentials", "tts_audio", "system_prompt", "provider_credentials"]:
		if snap.has(bad):
			_fail("snapshot_forbidden", bad)
			mod.queue_free()
			return
	_ok("snapshot_api_paid_identity")
	mod.queue_free()


func _test_happy_path_untrusted_proposal() -> void:
	var mod := _new_adapter()
	if mod == null:
		return
	var resp: Dictionary = mod.call("request_decision", {
		"snapshot_id": "11111111-1111-4111-8111-111111111111",
		"session_id": "session_starter_01",
		"request_id": "req-smoke-happy-0001",
	})
	if not bool(resp.get("ok", false)):
		_fail("happy_path_ok", str(resp))
		mod.queue_free()
		return
	if resp.get("untrusted", null) != true:
		_fail("untrusted_flag", str(resp.get("untrusted", null)))
		mod.queue_free()
		return
	if bool(resp.get("executed", true)):
		_fail("executed_must_be_false")
		mod.queue_free()
		return
	if bool(resp.get("committed", true)):
		_fail("committed_must_be_false")
		mod.queue_free()
		return
	var decision: Variant = resp.get("decision", null)
	if typeof(decision) != TYPE_DICTIONARY:
		_fail("decision_missing")
		mod.queue_free()
		return
	var dec: Dictionary = decision
	if str(dec.get("edition", "")) != "api_paid":
		_fail("decision_edition", str(dec.get("edition", "")))
		mod.queue_free()
		return
	if str(dec.get("source_snapshot_id", "")) != "11111111-1111-4111-8111-111111111111":
		_fail("source_snapshot_bind", str(dec.get("source_snapshot_id", "")))
		mod.queue_free()
		return
	if str(resp.get("provider_label", "")) != "fixture_provider":
		_fail("provider_label", str(resp.get("provider_label", "")))
		mod.queue_free()
		return
	_ok("happy_path_untrusted_proposal")
	mod.queue_free()


func _test_consent_required_no_commit() -> void:
	var mod := _new_adapter()
	if mod == null:
		return
	var resp: Dictionary = mod.call("request_decision", {
		"snapshot_id": "11111111-1111-4111-8111-111111111111",
		"request_id": "req-smoke-consent-0001",
	})
	if not bool(resp.get("ok", false)):
		_fail("consent_gateway", str(resp))
		mod.queue_free()
		return
	var recv: Dictionary = mod.call("receive_untrusted_response", resp, false)
	if not bool(recv.get("ok", false)):
		_fail("consent_receive", str(recv))
		mod.queue_free()
		return
	if str(recv.get("status", "")) != "awaiting_consent":
		_fail("awaiting_consent", str(recv.get("status", "")))
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
	if bool(recv.get("executed", false)) or bool(recv.get("committed", false)):
		_fail("consent_path_must_not_commit")
		mod.queue_free()
		return
	_ok("consent_required_no_commit")
	mod.queue_free()


func _test_confirm_no_execute() -> void:
	var mod := _new_adapter()
	if mod == null:
		return
	var resp: Dictionary = mod.call("request_decision", {
		"snapshot_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
		"request_id": "req-smoke-confirm-0001",
	})
	mod.call("receive_untrusted_response", resp, false)
	var conf: Dictionary = mod.call("confirm_pending_decision")
	if not bool(conf.get("ok", false)) or not bool(conf.get("accepted", false)):
		_fail("confirm_accepts", str(conf))
		mod.queue_free()
		return
	if bool(conf.get("executed", true)):
		_fail("confirm_must_not_execute")
		mod.queue_free()
		return
	if bool(conf.get("committed", true)):
		_fail("confirm_must_not_commit")
		mod.queue_free()
		return
	if str(conf.get("routes_to", "")) != "agm_decision_executor":
		_fail("routes_to_executor", str(conf.get("routes_to", "")))
		mod.queue_free()
		return
	_ok("confirm_no_execute")
	mod.queue_free()


func _test_validation_error_category() -> void:
	var mod := _new_adapter()
	if mod == null:
		return
	var bad_req := {
		"request_id": "req-smoke-val-0001",
		"snapshot": {
			"schema_version": "1.0.0",
			# missing most required fields
			"edition": "api_paid",
		},
		"provider_mode": "fixture",
	}
	var resp: Dictionary = mod.call("handle_request", bad_req)
	if bool(resp.get("ok", true)):
		_fail("validation_should_fail")
		mod.queue_free()
		return
	if str(resp.get("category", "")) != "validation":
		_fail("validation_category", str(resp.get("category", "")))
		mod.queue_free()
		return
	if bool(resp.get("retryable", true)):
		_fail("validation_not_retryable")
		mod.queue_free()
		return
	# Deny-list smuggling (value is a marker, not a live credential)
	var smuggle := {
		"request_id": "req-smoke-deny-0001",
		"snapshot": mod.call("build_snapshot", {
			"snapshot_id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
		}),
		"provider_mode": "fixture",
	}
	var smuggle_marker := "REDACT_MARKER_NOT_A_CREDENTIAL"
	(smuggle["snapshot"] as Dictionary)["api_key"] = smuggle_marker
	var resp2: Dictionary = mod.call("handle_request", smuggle)
	if bool(resp2.get("ok", true)):
		_fail("deny_list_should_reject")
		mod.queue_free()
		return
	if str(resp2.get("category", "")) != "validation":
		_fail("deny_list_category", str(resp2.get("category", "")))
		mod.queue_free()
		return
	# Ensure smuggled value is not echoed in error message
	var msg := str(resp2.get("message", "")) + str(resp2.get("details", {}))
	if smuggle_marker in msg:
		_fail("secret_leaked_in_error")
		mod.queue_free()
		return
	_ok("validation_error_category")
	mod.queue_free()


func _test_budget_reject() -> void:
	var mod := _new_adapter()
	if mod == null:
		return
	var snap: Dictionary = mod.call("build_snapshot", {
		"snapshot_id": "cccccccc-cccc-4ccc-8ccc-cccccccccccc",
	})
	var resp: Dictionary = mod.call("handle_request", {
		"request_id": "req-smoke-budget-0001",
		"snapshot": snap,
		"provider_mode": "fixture",
		"budget_context": {
			"per_request_cap": 0.01,
			"session_cap": 10000.0,
			"session_spent": 0.0,
		},
	})
	if bool(resp.get("ok", true)):
		_fail("budget_should_reject", str(resp))
		mod.queue_free()
		return
	if str(resp.get("category", "")) != "budget":
		_fail("budget_category", str(resp.get("category", "")))
		mod.queue_free()
		return
	if str(resp.get("code", "")) != "budget_per_request_exceeded":
		_fail("budget_code", str(resp.get("code", "")))
		mod.queue_free()
		return
	_ok("budget_reject")
	mod.queue_free()


func _test_policy_provider_mode() -> void:
	var mod := _new_adapter()
	if mod == null:
		return
	var snap: Dictionary = mod.call("build_snapshot", {
		"snapshot_id": "dddddddd-dddd-4ddd-8ddd-dddddddddddd",
	})
	var resp: Dictionary = mod.call("handle_request", {
		"request_id": "req-smoke-policy-0001",
		"snapshot": snap,
		"provider_mode": "openai_live",
	})
	if bool(resp.get("ok", true)):
		_fail("policy_should_deny_real_provider")
		mod.queue_free()
		return
	if str(resp.get("category", "")) != "policy":
		_fail("policy_category", str(resp.get("category", "")))
		mod.queue_free()
		return
	_ok("policy_provider_mode")
	mod.queue_free()


func _test_error_categories_list() -> void:
	var mod := _new_adapter()
	if mod == null:
		return
	var cats: PackedStringArray = mod.call("list_error_categories") as PackedStringArray
	if cats == null:
		_fail("error_categories_type")
		mod.queue_free()
		return
	var required := [
		"validation", "policy", "budget", "timeout", "retry_exhausted", "provider_unavailable",
	]
	for c in required:
		if not cats.has(c):
			_fail("missing_error_category", c)
			mod.queue_free()
			return
	# Force each category once
	for c in required:
		mod.call("set_test_force_error", c)
		var r: Dictionary = mod.call("handle_request", {
			"request_id": "req-force-%s" % c,
			"snapshot": mod.call("build_snapshot", {
				"snapshot_id": "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee",
			}),
			"provider_mode": "fixture",
		})
		if str(r.get("category", "")) != c:
			_fail("force_category", "expected %s got %s" % [c, str(r.get("category", ""))])
			mod.queue_free()
			return
	mod.call("clear_test_force_error")
	_ok("error_categories_list")
	mod.queue_free()


func _test_idempotency_replay() -> void:
	var mod := _new_adapter()
	if mod == null:
		return
	var snap: Dictionary = mod.call("build_snapshot", {
		"snapshot_id": "ffffffff-ffff-4fff-8fff-ffffffffffff",
	})
	var req := {
		"request_id": "req-smoke-idem-0001",
		"snapshot": snap,
		"provider_mode": "fixture",
	}
	var r1: Dictionary = mod.call("handle_request", req)
	var r2: Dictionary = mod.call("handle_request", req)
	if not bool(r1.get("ok", false)) or not bool(r2.get("ok", false)):
		_fail("idempotency_ok", "r1=%s r2=%s" % [str(r1.get("ok")), str(r2.get("ok"))])
		mod.queue_free()
		return
	var d1 := str((r1.get("decision", {}) as Dictionary).get("decision_id", ""))
	var d2 := str((r2.get("decision", {}) as Dictionary).get("decision_id", ""))
	if d1.is_empty() or d1 != d2:
		_fail("idempotency_decision_id", "%s vs %s" % [d1, d2])
		mod.queue_free()
		return
	_ok("idempotency_replay")
	mod.queue_free()


func _test_fixture_files_no_secrets() -> void:
	for path in [FIXTURE_DECISION, FIXTURE_SNAPSHOT]:
		var text := _read_text(path)
		if text.is_empty():
			_fail("fixture_empty", path)
			return
		for bad in ["api_key", "access_token", "password", "Bearer ", "sk-proj", "credentials"]:
			# structural absence: key names with values
			if "\"%s\"" % bad in text or bad + ":" in text:
				# "credentials" alone shouldn't appear
				_fail("fixture_secret_field", "%s has %s" % [path, bad])
				return
	_ok("fixture_files_no_secrets")


func _test_production_path_note() -> void:
	var mod := _new_adapter()
	if mod == null:
		return
	var note: String = str(mod.call("production_path_note"))
	if note.find("HITL") < 0 and note.find("trusted gateway") < 0:
		_fail("production_note_missing")
		mod.queue_free()
		return
	if note.find("untrusted") < 0 and note.find("consent") < 0:
		_fail("production_note_consent")
		mod.queue_free()
		return
	_ok("production_path_note")
	mod.queue_free()
