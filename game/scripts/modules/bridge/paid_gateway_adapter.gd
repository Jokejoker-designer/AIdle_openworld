## Paid AGM Gateway client adapter (G5-001 A2).
##
## Production path: Godot → trusted gateway only (credentials stay server-side).
## G5-001 test path: pure GDScript fixture gateway that mirrors services/agm_gateway
## GatewayService response shape — NO provider SDK, NO secrets, NO outbound internet.
##
## Same Snapshot/Decision contracts as Free Desktop Bridge; edition=api_paid.
## Gateway success returns an untrusted proposal; consent → executor → preview →
## World Commit remain mandatory. This adapter never commits durable state.
class_name PaidGatewayAdapter
extends Node

const BridgePaths = preload("res://scripts/modules/bridge/bridge_paths.gd")
const BridgeSnapshotBuilder = preload("res://scripts/modules/bridge/snapshot_builder.gd")
const BridgeDecisionImportGuard = preload("res://scripts/modules/bridge/decision_import_guard.gd")

const MODULE_ID := "paid_gateway"
const EDITION_API_PAID := "api_paid"
const SCHEMA_VERSION := "1.0.0"
const PROVIDER_MODE_FIXTURE := "fixture"
const PROVIDER_LABEL_FIXTURE := "fixture_provider"
const TRANSPORT_CHANNEL := "api_gateway"

## Local fixture (no secrets) — preferred res:// load for headless smoke.
const FIXTURE_DECISION_RES := "res://scripts/modules/bridge/exports/valid_decision_api_paid.json"
const FIXTURE_SNAPSHOT_RES := "res://scripts/modules/bridge/exports/valid_snapshot_api_paid.json"
## Repo-relative fallbacks (when running from full workspace checkout).
const FIXTURE_DECISION_REPO := "contracts/fixtures/agm/valid/valid_decision_api_paid.json"
const FIXTURE_SNAPSHOT_REPO := "contracts/fixtures/agm/valid/valid_snapshot_api_paid.json"

## Structured error categories (match services/agm_gateway/errors.py).
const CAT_VALIDATION := "validation"
const CAT_POLICY := "policy"
const CAT_BUDGET := "budget"
const CAT_TIMEOUT := "timeout"
const CAT_RETRY_EXHAUSTED := "retry_exhausted"
const CAT_PROVIDER_UNAVAILABLE := "provider_unavailable"

const ERROR_CATEGORIES := [
	CAT_VALIDATION,
	CAT_POLICY,
	CAT_BUDGET,
	CAT_TIMEOUT,
	CAT_RETRY_EXHAUSTED,
	CAT_PROVIDER_UNAVAILABLE,
]

## Deny-list aligned with Free Bridge + gateway redaction (never store values).
const SNAPSHOT_DENY_KEYS := [
	"api_key",
	"access_token",
	"password",
	"secret",
	"secrets",
	"credentials",
	"cookie",
	"cookies",
	"session_cookie",
	"auth_token",
	"raw_system_prompt",
	"system_prompt",
	"private_memory",
	"raw_prompt",
	"tts_audio",
	"voice_sample",
	"microphone_buffer",
	"provider_credentials",
]

const DECISION_DENY_EXTRA := [
	"script",
	"scripts",
	"code",
	"shader",
	"executable",
	"commit_request",
	"durable_mutation",
	"scene_tree_mutation",
	"direct_world_write",
]

signal snapshot_built(snapshot: Dictionary)
signal gateway_response(response: Dictionary)
signal decision_pending_consent(decision: Dictionary, summary: String)
signal decision_accepted(decision: Dictionary)
signal decision_rejected(reason: String, detail: String)
signal consent_cancelled(reason: String)

@export var show_consent_ui: bool = true
## G5-001: fixture only. Real provider selection is HITL_REQUIRED (gateway-side).
@export var provider_mode: String = PROVIDER_MODE_FIXTURE
@export var per_request_cap: float = 1000.0
@export var session_cap: float = 10000.0

var _builder: RefCounted
var _guard: RefCounted
var _live_snapshot: Dictionary = {}
var _live_snapshot_id: String = ""
var _pending_decision: Dictionary = {}
var _accepted_decision: Dictionary = {}
var _seen_decision_ids: Dictionary = {}
var _last_rejection: Dictionary = {}
var _last_gateway_response: Dictionary = {}
var _session_spent: float = 0.0
var _idempotency: Dictionary = {}  # request_id -> response
var _registered: bool = false
var _consent_dialog: Node = null
## Test hook: force error category before fixture provider (validation/budget/policy/timeout/…).
var _test_force_error: String = ""
## Production note flag (never enables real network from this module).
var _production_gateway_url_documented_only: bool = true


func _ready() -> void:
	_ensure_helpers()
	if not ModuleRegistry.has_module(MODULE_ID):
		ModuleRegistry.register_module(MODULE_ID, self)
		_registered = true
	print("[PaidGatewayAdapter] Ready – fixture/local path only (no provider SDK, no secrets).")


func _exit_tree() -> void:
	if _registered and ModuleRegistry.has_module(MODULE_ID):
		if ModuleRegistry.get_module(MODULE_ID) == self:
			ModuleRegistry.unregister_module(MODULE_ID)


func _ensure_helpers() -> void:
	if _builder == null:
		_builder = BridgeSnapshotBuilder.new() as RefCounted
	if _guard == null:
		_guard = BridgeDecisionImportGuard.new() as RefCounted


func is_stub() -> bool:
	return false


func get_status() -> String:
	var pending := "yes" if has_pending_consent() else "no"
	return "PaidGateway fixture | edition=%s | live=%s | pending=%s | session_spent=%.1f" % [
		EDITION_API_PAID,
		_live_snapshot_id if not _live_snapshot_id.is_empty() else "-",
		pending,
		_session_spent,
	]


func get_edition() -> String:
	return EDITION_API_PAID


func get_provider_mode() -> String:
	return provider_mode


## Fixture/test adapter never opens sockets. Production still would only call a
## trusted local/remote gateway — never a provider SDK from Godot.
func uses_network() -> bool:
	return false


## Godot client never holds provider secrets (ARCHITECTURE_LOCK).
func holds_provider_secrets() -> bool:
	return false


func list_error_categories() -> PackedStringArray:
	return PackedStringArray(ERROR_CATEGORIES)


func get_session_spent() -> float:
	return _session_spent


func get_last_gateway_response() -> Dictionary:
	return _last_gateway_response.duplicate(true)


# ─── Snapshot (api_paid) ─────────────────────────────────────────────────────

## Build World State Snapshot with edition=api_paid and transport.api_gateway.
## Reuses Free Bridge builder core then rebinds edition/transport for identity parity.
func build_snapshot(context: Dictionary = {}) -> Dictionary:
	_ensure_helpers()
	var ctx: Dictionary = context.duplicate(true)
	ctx["channel"] = BridgePaths.CHANNEL_FILE  # builder only knows free channels; rebind below
	var snap: Dictionary = _builder.call("build", ctx) as Dictionary
	snap = snap.duplicate(true)
	snap["edition"] = EDITION_API_PAID
	snap["transport"] = {
		"channel": TRANSPORT_CHANNEL,
		"bridge_path_hint": str(ctx.get("bridge_path_hint", "gateway://trusted/agm")),
	}
	# Hard strip deny-list at top level (deep walk also used on request path).
	_strip_deny_keys_inplace(snap, SNAPSHOT_DENY_KEYS)

	var errs := _validate_snapshot_structure(snap)
	if not errs.is_empty():
		push_warning("[PaidGatewayAdapter] snapshot structure issues: %s" % ", ".join(errs))

	_live_snapshot = snap.duplicate(true)
	_live_snapshot_id = str(snap.get("snapshot_id", ""))
	snapshot_built.emit(snap)
	return snap.duplicate(true)


func get_live_snapshot() -> Dictionary:
	return _live_snapshot.duplicate(true)


func get_live_snapshot_id() -> String:
	return _live_snapshot_id


func set_live_snapshot_for_tests(snapshot_id: String, snapshot: Dictionary = {}) -> void:
	_live_snapshot_id = snapshot_id
	if not snapshot.is_empty():
		_live_snapshot = snapshot.duplicate(true)
	else:
		_live_snapshot = {
			"snapshot_id": snapshot_id,
			"schema_version": SCHEMA_VERSION,
			"edition": EDITION_API_PAID,
		}


func mark_decision_seen_for_tests(decision_id: String) -> void:
	_seen_decision_ids[decision_id] = true


func set_test_force_error(category: String) -> void:
	_test_force_error = category


func clear_test_force_error() -> void:
	_test_force_error = ""


func reset_session_budget_for_tests(spent: float = 0.0) -> void:
	_session_spent = maxf(0.0, spent)
	_idempotency.clear()


# ─── Gateway request (fixture mirror of GatewayService.handle_request) ───────

## Full gateway request. Shape matches A0/A1 contract:
## { request_id, snapshot, budget_context?, provider_mode?, gateway_request_id? }
## Returns success envelope { ok, untrusted, decision, ... } or error envelope.
func handle_request(gateway_request: Dictionary) -> Dictionary:
	_ensure_helpers()
	var request_id := str(gateway_request.get("request_id", "")).strip_edges()
	var gateway_request_id := str(gateway_request.get("gateway_request_id", request_id)).strip_edges()
	var trace_id := ""

	if request_id.is_empty():
		var env := _error_envelope(
			CAT_VALIDATION, "request_id_missing", "request_id is required",
			request_id, trace_id, false, {}
		)
		_last_gateway_response = env
		gateway_response.emit(env)
		return env

	if _idempotency.has(request_id):
		var prior: Dictionary = (_idempotency[request_id] as Dictionary).duplicate(true)
		_last_gateway_response = prior
		gateway_response.emit(prior)
		return prior

	# Test force-error hook (deterministic smoke paths).
	if not _test_force_error.is_empty():
		var forced := _forced_error(_test_force_error, request_id, trace_id)
		_store_idempotent_terminal(request_id, forced)
		_last_gateway_response = forced
		gateway_response.emit(forced)
		return forced

	var snapshot_raw: Variant = gateway_request.get("snapshot", null)
	if snapshot_raw == null or typeof(snapshot_raw) != TYPE_DICTIONARY:
		var env2 := _error_envelope(
			CAT_VALIDATION, "snapshot_missing", "snapshot is required and must be an object",
			request_id, trace_id, false, {}
		)
		_store_idempotent_terminal(request_id, env2)
		_last_gateway_response = env2
		gateway_response.emit(env2)
		return env2

	var snapshot: Dictionary = (snapshot_raw as Dictionary).duplicate(true)
	trace_id = str(snapshot.get("trace_id", ""))

	# Deny-list on snapshot body → fail closed (validation). Never log values.
	var inbound_deny := _collect_deny_keys(snapshot, SNAPSHOT_DENY_KEYS)
	_strip_deny_keys_inplace(snapshot, SNAPSHOT_DENY_KEYS)
	if not inbound_deny.is_empty():
		var env3 := _error_envelope(
			CAT_VALIDATION,
			"snapshot_deny_list_rejected",
			"Inbound snapshot contained forbidden secret or credential fields",
			request_id,
			trace_id,
			false,
			{"fields_stripped": inbound_deny},
		)
		_store_idempotent_terminal(request_id, env3)
		_last_gateway_response = env3
		gateway_response.emit(env3)
		return env3

	var snap_errs := _validate_snapshot_structure(snapshot)
	if not snap_errs.is_empty():
		var env4 := _error_envelope(
			CAT_VALIDATION,
			"snapshot_schema_invalid",
			"World State Snapshot failed structural validation",
			request_id,
			trace_id,
			false,
			{"errors": Array(snap_errs).slice(0, 12)},
		)
		_store_idempotent_terminal(request_id, env4)
		_last_gateway_response = env4
		gateway_response.emit(env4)
		return env4

	if str(snapshot.get("edition", "")) != EDITION_API_PAID:
		var env5 := _error_envelope(
			CAT_POLICY,
			"edition_not_api_paid",
			"Paid gateway path requires edition=api_paid",
			request_id,
			trace_id,
			false,
			{"edition": str(snapshot.get("edition", ""))},
		)
		_store_idempotent_terminal(request_id, env5)
		_last_gateway_response = env5
		gateway_response.emit(env5)
		return env5

	var mode := str(gateway_request.get("provider_mode", provider_mode)).strip_edges()
	if mode == "fixture_provider":
		mode = PROVIDER_MODE_FIXTURE
	if mode != PROVIDER_MODE_FIXTURE:
		# Real provider selection is HITL_REQUIRED — denied by default from client.
		var env6 := _error_envelope(
			CAT_POLICY,
			"provider_mode_denied",
			"Real provider selection is HITL_REQUIRED; only fixture mode allowed in G5-001",
			request_id,
			trace_id,
			false,
			{"provider_mode": mode},
		)
		_store_idempotent_terminal(request_id, env6)
		_last_gateway_response = env6
		gateway_response.emit(env6)
		return env6

	# Budget precheck
	var budget_context: Dictionary = {}
	var bc: Variant = gateway_request.get("budget_context", {})
	if typeof(bc) == TYPE_DICTIONARY:
		budget_context = bc
	var pr_cap := float(budget_context.get("per_request_cap", per_request_cap))
	var s_cap := float(budget_context.get("session_cap", session_cap))
	if budget_context.has("session_spent") and _session_spent == 0.0:
		var requested_spent := float(budget_context.get("session_spent", 0.0))
		if requested_spent < 0.0:
			var env_neg := _error_envelope(
				CAT_BUDGET, "budget_negative_balance", "session_spent must be non-negative",
				request_id, trace_id, false, {}
			)
			_store_idempotent_terminal(request_id, env_neg)
			_last_gateway_response = env_neg
			gateway_response.emit(env_neg)
			return env_neg
		_session_spent = requested_spent

	var estimate := _estimate_budget(snapshot)
	if estimate > pr_cap:
		var env7 := _error_envelope(
			CAT_BUDGET,
			"budget_per_request_exceeded",
			"estimate exceeds per_request_cap",
			request_id,
			trace_id,
			false,
			{"estimate": estimate, "per_request_cap": pr_cap},
		)
		_store_idempotent_terminal(request_id, env7)
		_last_gateway_response = env7
		gateway_response.emit(env7)
		return env7
	if _session_spent + estimate > s_cap:
		var env8 := _error_envelope(
			CAT_BUDGET,
			"budget_session_exceeded",
			"session_spent + estimate exceeds session_cap",
			request_id,
			trace_id,
			false,
			{
				"estimate": estimate,
				"session_spent": _session_spent,
				"session_cap": s_cap,
			},
		)
		_store_idempotent_terminal(request_id, env8)
		_last_gateway_response = env8
		gateway_response.emit(env8)
		return env8

	# Fixture provider: load decision, rebind to snapshot (no network).
	var load_result := _load_fixture_decision()
	if not bool(load_result.get("ok", false)):
		var env9 := _error_envelope(
			CAT_PROVIDER_UNAVAILABLE,
			"fixture_load_failed",
			"Could not load fixture decision (local file path only)",
			request_id,
			trace_id,
			true,
			{"detail": str(load_result.get("reason", ""))},
		)
		# provider_unavailable is retryable; do not cache as terminal unless exhausted
		_last_gateway_response = env9
		gateway_response.emit(env9)
		return env9

	var decision: Dictionary = (load_result.get("data", {}) as Dictionary).duplicate(true)
	decision = _rebind_decision(decision, snapshot, {
		"request_id": request_id,
		"gateway_request_id": gateway_request_id,
	})

	var dec_deny := _collect_deny_keys(decision, SNAPSHOT_DENY_KEYS + DECISION_DENY_EXTRA)
	if not dec_deny.is_empty():
		var env10 := _error_envelope(
			CAT_VALIDATION,
			"decision_deny_list_rejected",
			"Provider decision contained forbidden fields",
			request_id,
			trace_id,
			false,
			{"fields": dec_deny},
		)
		_store_idempotent_terminal(request_id, env10)
		_last_gateway_response = env10
		gateway_response.emit(env10)
		return env10

	var struct_errs: PackedStringArray = _guard.call("validate_structure", decision) as PackedStringArray
	if struct_errs == null:
		struct_errs = PackedStringArray()
	if not struct_errs.is_empty():
		var env11 := _error_envelope(
			CAT_VALIDATION,
			"decision_schema_invalid",
			"AGM Decision Envelope failed structural validation",
			request_id,
			trace_id,
			false,
			{"errors": Array(struct_errs).slice(0, 12)},
		)
		_store_idempotent_terminal(request_id, env11)
		_last_gateway_response = env11
		gateway_response.emit(env11)
		return env11

	if str(decision.get("source_snapshot_id", "")) != str(snapshot.get("snapshot_id", "")):
		var env12 := _error_envelope(
			CAT_VALIDATION,
			"source_snapshot_mismatch",
			"decision.source_snapshot_id must equal snapshot.snapshot_id",
			request_id,
			trace_id,
			false,
			{},
		)
		_store_idempotent_terminal(request_id, env12)
		_last_gateway_response = env12
		gateway_response.emit(env12)
		return env12

	# Track live snapshot for consent path
	_live_snapshot = snapshot.duplicate(true)
	_live_snapshot_id = str(snapshot.get("snapshot_id", ""))

	_session_spent += estimate
	var response := {
		"ok": true,
		"request_id": request_id,
		"gateway_request_id": gateway_request_id if not gateway_request_id.is_empty() else request_id,
		"decision": decision,
		"untrusted": true,
		"provider_label": PROVIDER_LABEL_FIXTURE,
		"budget": {
			"estimate": estimate,
			"session_spent_after": _session_spent,
			"per_request_cap": pr_cap,
			"session_cap": s_cap,
		},
		# Adapter never invokes World Commit
		"executed": false,
		"committed": false,
		"routes_to": "consent_then_agm_decision_executor",
	}
	_idempotency[request_id] = response.duplicate(true)
	if not gateway_request_id.is_empty() and gateway_request_id != request_id:
		_idempotency[gateway_request_id] = response.duplicate(true)
	_last_gateway_response = response.duplicate(true)
	gateway_response.emit(response)
	return response.duplicate(true)


## Convenience: build snapshot from context + handle_request in one call.
func request_decision(context: Dictionary = {}) -> Dictionary:
	_ensure_helpers()
	var snap: Dictionary
	if context.has("snapshot") and typeof(context["snapshot"]) == TYPE_DICTIONARY:
		snap = (context["snapshot"] as Dictionary).duplicate(true)
		if str(snap.get("edition", "")) != EDITION_API_PAID:
			snap["edition"] = EDITION_API_PAID
		_live_snapshot = snap.duplicate(true)
		_live_snapshot_id = str(snap.get("snapshot_id", ""))
	else:
		snap = build_snapshot(context)

	var request_id := str(context.get("request_id", _new_uuid()))
	var gateway_request := {
		"request_id": request_id,
		"gateway_request_id": str(context.get("gateway_request_id", request_id)),
		"snapshot": snap,
		"provider_mode": str(context.get("provider_mode", PROVIDER_MODE_FIXTURE)),
		"budget_context": context.get("budget_context", {
			"per_request_cap": per_request_cap,
			"session_cap": session_cap,
			"session_spent": _session_spent,
		}),
	}
	return handle_request(gateway_request)


# ─── Untrusted proposal → consent (same Free Bridge semantics) ───────────────

## Route a successful gateway response through import guard + visible consent.
## Never auto-commits. auto_consent is for headless smoke only.
func receive_untrusted_response(response: Dictionary, auto_consent: bool = false) -> Dictionary:
	_ensure_helpers()
	if not bool(response.get("ok", false)):
		var reason := str(response.get("category", "gateway_error"))
		var detail := str(response.get("code", "")) + ": " + str(response.get("message", ""))
		_record_rejection(reason, detail)
		return {
			"ok": false,
			"status": "rejected",
			"reason": reason,
			"detail": detail,
			"pending": false,
			"accepted": false,
			"untrusted": true,
		}

	if response.get("untrusted", null) != true:
		_record_rejection("not_marked_untrusted", "gateway success must set untrusted=true")
		return {
			"ok": false,
			"status": "rejected",
			"reason": "not_marked_untrusted",
			"detail": "gateway success must set untrusted=true",
			"pending": false,
			"accepted": false,
			"untrusted": true,
		}

	var decision_v: Variant = response.get("decision", null)
	if typeof(decision_v) != TYPE_DICTIONARY:
		_record_rejection("decision_missing", "success response lacks decision object")
		return {
			"ok": false,
			"status": "rejected",
			"reason": "decision_missing",
			"detail": "success response lacks decision object",
			"pending": false,
			"accepted": false,
			"untrusted": true,
		}

	var decision: Dictionary = decision_v
	var raw := JSON.stringify(decision)
	var result: Dictionary = _guard.call(
		"evaluate", raw, _live_snapshot_id, _seen_decision_ids
	) as Dictionary
	if not bool(result.get("ok", false)):
		_record_rejection(str(result.get("reason", "")), str(result.get("detail", "")))
		return {
			"ok": false,
			"status": "rejected",
			"reason": result.get("reason", ""),
			"detail": result.get("detail", ""),
			"pending": false,
			"accepted": false,
			"untrusted": true,
		}

	_pending_decision = (result.get("decision", {}) as Dictionary).duplicate(true)
	var summary := _summarize_decision(_pending_decision)
	decision_pending_consent.emit(_pending_decision, summary)

	if show_consent_ui and not auto_consent:
		_open_consent_dialog(_pending_decision, summary)

	if auto_consent:
		return confirm_pending_decision()

	return {
		"ok": true,
		"status": "awaiting_consent",
		"reason": "",
		"detail": summary,
		"pending": true,
		"accepted": false,
		"untrusted": true,
		"decision_id": str(_pending_decision.get("decision_id", "")),
		"source_snapshot_id": str(_pending_decision.get("source_snapshot_id", "")),
		"executed": false,
		"committed": false,
	}


func has_pending_consent() -> bool:
	return not _pending_decision.is_empty()


func get_pending_decision() -> Dictionary:
	return _pending_decision.duplicate(true)


## Explicit player confirm — sole path pending → accepted. Does not execute.
func confirm_pending_decision() -> Dictionary:
	_ensure_helpers()
	if _pending_decision.is_empty():
		_record_rejection(BridgePaths.REJECT_NO_PENDING, "nothing to confirm")
		return {
			"ok": false,
			"status": "rejected",
			"reason": BridgePaths.REJECT_NO_PENDING,
			"detail": "nothing to confirm",
			"pending": false,
			"accepted": false,
		}

	var decision_id := str(_pending_decision.get("decision_id", ""))
	var source_id := str(_pending_decision.get("source_snapshot_id", ""))
	if source_id != _live_snapshot_id:
		var detail := "source_snapshot_id=%s live=%s" % [source_id, _live_snapshot_id]
		_pending_decision = {}
		_close_consent_dialog()
		_record_rejection(BridgePaths.REJECT_STALE_SNAPSHOT, detail)
		return {
			"ok": false,
			"status": "rejected",
			"reason": BridgePaths.REJECT_STALE_SNAPSHOT,
			"detail": detail,
			"pending": false,
			"accepted": false,
		}
	if _seen_decision_ids.has(decision_id):
		_pending_decision = {}
		_close_consent_dialog()
		_record_rejection(BridgePaths.REJECT_REPLAYED_DECISION, decision_id)
		return {
			"ok": false,
			"status": "rejected",
			"reason": BridgePaths.REJECT_REPLAYED_DECISION,
			"detail": decision_id,
			"pending": false,
			"accepted": false,
		}

	_seen_decision_ids[decision_id] = true
	_accepted_decision = _pending_decision.duplicate(true)
	_pending_decision = {}
	_close_consent_dialog()
	_last_rejection = {}
	decision_accepted.emit(_accepted_decision)
	return {
		"ok": true,
		"status": "accepted",
		"reason": "",
		"detail": "player_confirmed",
		"pending": false,
		"accepted": true,
		"decision_id": decision_id,
		"source_snapshot_id": source_id,
		"routes_to": "agm_decision_executor",
		"executed": false,
		"committed": false,
		"untrusted_was": true,
	}


func reject_pending_decision(reason: String = "player_rejected") -> Dictionary:
	if _pending_decision.is_empty():
		return {
			"ok": false,
			"status": "rejected",
			"reason": BridgePaths.REJECT_NO_PENDING,
			"detail": "nothing to reject",
			"pending": false,
			"accepted": false,
		}
	var decision_id := str(_pending_decision.get("decision_id", ""))
	_pending_decision = {}
	_close_consent_dialog()
	consent_cancelled.emit(reason)
	return {
		"ok": true,
		"status": "cancelled",
		"reason": reason,
		"detail": decision_id,
		"pending": false,
		"accepted": false,
	}


func get_accepted_decision() -> Dictionary:
	return _accepted_decision.duplicate(true)


func list_seen_decision_ids() -> PackedStringArray:
	return PackedStringArray(_seen_decision_ids.keys())


func get_last_rejection() -> Dictionary:
	return _last_rejection.duplicate(true)


func clear_accepted_handoff() -> void:
	_accepted_decision = {}


## Production documentation helper — never enables network or stores secrets.
func production_path_note() -> String:
	return (
		"Production Paid AGM path: Godot PaidGatewayAdapter builds redacted "
		+ "api_paid snapshots and calls a trusted gateway only (server-side credentials). "
		+ "Real provider selection is HITL_REQUIRED. G5-001 uses fixture provider only. "
		+ "Decision remains untrusted: consent → executor soft effects → world_prompt "
		+ "preview → player confirm → World Commit."
	)


# ─── Internals ───────────────────────────────────────────────────────────────

func _validate_snapshot_structure(snapshot: Dictionary) -> PackedStringArray:
	var errors: PackedStringArray = []
	var required := [
		"schema_version", "snapshot_id", "created_at", "edition", "session_id",
		"space_id", "world_revision", "progression_phase", "art_style", "player",
		"companion", "world", "quests", "latest_player_action",
		"last_execution_receipt", "memory", "trace_id",
	]
	for key in required:
		if not snapshot.has(key):
			errors.append("missing required: %s" % key)
	if str(snapshot.get("schema_version", "")) != SCHEMA_VERSION:
		errors.append("schema_version must be %s" % SCHEMA_VERSION)
	if str(snapshot.get("edition", "")) != EDITION_API_PAID:
		errors.append("edition must be %s for Paid gateway adapter" % EDITION_API_PAID)
	for bad in SNAPSHOT_DENY_KEYS:
		if snapshot.has(bad):
			errors.append("forbidden field: %s" % bad)
	if not BridgeSnapshotBuilder._looks_like_uuid(str(snapshot.get("snapshot_id", ""))):
		errors.append("snapshot_id must look like uuid")
	return errors


func _estimate_budget(snapshot: Dictionary) -> float:
	# Deterministic size-based units (mirrors gateway budget estimate intent).
	var text := JSON.stringify(snapshot)
	var units := 1.0 + float(text.length()) / 500.0
	return snappedf(units, 0.01)


func _load_fixture_decision() -> Dictionary:
	var candidates: PackedStringArray = PackedStringArray()
	candidates.append(FIXTURE_DECISION_RES)
	var game_root := ProjectSettings.globalize_path("res://")
	candidates.append(game_root.path_join("..").path_join(FIXTURE_DECISION_REPO).simplify_path())
	candidates.append(game_root.path_join(FIXTURE_DECISION_REPO).simplify_path())
	candidates.append(ProjectSettings.globalize_path(FIXTURE_DECISION_RES))
	# Workspace absolute fallback for headless CI when res:// export missing
	candidates.append("E:/AIdle_openworld".path_join(FIXTURE_DECISION_REPO))

	for p in candidates:
		if p.is_empty():
			continue
		var open_path := p
		if not FileAccess.file_exists(open_path):
			# try globalize for res://
			if p.begins_with("res://"):
				open_path = ProjectSettings.globalize_path(p)
			if not FileAccess.file_exists(open_path):
				continue
		var f := FileAccess.open(open_path if FileAccess.file_exists(open_path) else p, FileAccess.READ)
		if f == null and p.begins_with("res://"):
			f = FileAccess.open(p, FileAccess.READ)
		if f == null:
			continue
		var text := f.get_as_text()
		f.close()
		var json := JSON.new()
		if json.parse(text) != OK:
			continue
		if typeof(json.data) != TYPE_DICTIONARY:
			continue
		return {"ok": true, "data": json.data, "path": p}
	return {"ok": false, "reason": "fixture decision not found"}


func _rebind_decision(decision: Dictionary, snapshot: Dictionary, context: Dictionary) -> Dictionary:
	var out: Dictionary = decision.duplicate(true)
	var snapshot_id := str(snapshot.get("snapshot_id", ""))
	var session_id := str(snapshot.get("session_id", ""))
	var trace_id := str(snapshot.get("trace_id", ""))

	out["source_snapshot_id"] = snapshot_id
	if not session_id.is_empty():
		out["session_id"] = session_id
	out["edition"] = EDITION_API_PAID
	out["created_at"] = _iso_now()
	# Fresh decision_id per request (gateway-layer idempotency is request_id).
	if not bool(context.get("reuse_decision_id", false)):
		out["decision_id"] = _new_uuid()

	var trace: Dictionary = {}
	if typeof(out.get("trace", null)) == TYPE_DICTIONARY:
		trace = (out["trace"] as Dictionary).duplicate(true)
	if not trace_id.is_empty():
		trace["trace_id"] = trace_id
	trace["provider_label"] = PROVIDER_LABEL_FIXTURE
	trace["model_receipt_ref"] = "fixture:paid_gateway:decision"
	out["trace"] = trace
	return out


func _error_envelope(
	category: String,
	code: String,
	message: String,
	request_id: String,
	trace_id: String,
	retryable: bool,
	details: Dictionary
) -> Dictionary:
	var envelope := {
		"ok": false,
		"error": true,
		"category": category,
		"code": code,
		"message": message,
		"request_id": request_id,
		"trace_id": trace_id,
		"retryable": retryable,
		"occurred_at": _iso_now(),
		"untrusted": true,
		"executed": false,
		"committed": false,
	}
	if not details.is_empty():
		envelope["details"] = details
	return envelope


func _forced_error(category: String, request_id: String, trace_id: String) -> Dictionary:
	match category:
		CAT_VALIDATION:
			return _error_envelope(
				CAT_VALIDATION, "forced_validation", "test forced validation error",
				request_id, trace_id, false, {}
			)
		CAT_POLICY:
			return _error_envelope(
				CAT_POLICY, "forced_policy", "test forced policy error",
				request_id, trace_id, false, {}
			)
		CAT_BUDGET:
			return _error_envelope(
				CAT_BUDGET, "forced_budget", "test forced budget error",
				request_id, trace_id, false, {}
			)
		CAT_TIMEOUT:
			return _error_envelope(
				CAT_TIMEOUT, "forced_timeout", "test forced timeout",
				request_id, trace_id, true, {}
			)
		CAT_RETRY_EXHAUSTED:
			return _error_envelope(
				CAT_RETRY_EXHAUSTED, "forced_retry_exhausted", "test forced retry exhausted",
				request_id, trace_id, false, {}
			)
		CAT_PROVIDER_UNAVAILABLE:
			return _error_envelope(
				CAT_PROVIDER_UNAVAILABLE, "forced_unavailable", "test forced provider unavailable",
				request_id, trace_id, true, {}
			)
		_:
			return _error_envelope(
				CAT_VALIDATION, "unknown_force", "unknown forced category",
				request_id, trace_id, false, {"category": category}
			)


func _store_idempotent_terminal(request_id: String, envelope: Dictionary) -> void:
	var cat := str(envelope.get("category", ""))
	if cat in [CAT_VALIDATION, CAT_POLICY, CAT_BUDGET, CAT_RETRY_EXHAUSTED]:
		_idempotency[request_id] = envelope.duplicate(true)


func _collect_deny_keys(obj: Variant, deny: Array, out: Array = []) -> Array:
	if typeof(obj) == TYPE_DICTIONARY:
		var d: Dictionary = obj
		for k in d.keys():
			var ks := str(k)
			if deny.has(ks) and not out.has(ks):
				out.append(ks)
			_collect_deny_keys(d[k], deny, out)
	elif typeof(obj) == TYPE_ARRAY:
		for item in obj:
			_collect_deny_keys(item, deny, out)
	return out


func _strip_deny_keys_inplace(obj: Variant, deny: Array) -> void:
	if typeof(obj) == TYPE_DICTIONARY:
		var d: Dictionary = obj
		for bad in deny:
			if d.has(bad):
				d.erase(bad)
		for k in d.keys():
			_strip_deny_keys_inplace(d[k], deny)
	elif typeof(obj) == TYPE_ARRAY:
		for item in obj:
			_strip_deny_keys_inplace(item, deny)


func _summarize_decision(decision: Dictionary) -> String:
	var did: String = str(decision.get("decision_id", "?"))
	var lines: Array = []
	var dialogue: Variant = decision.get("dialogue", {})
	if typeof(dialogue) == TYPE_DICTIONARY:
		var dl: Variant = (dialogue as Dictionary).get("lines", [])
		if typeof(dl) == TYPE_ARRAY:
			for line in dl:
				if typeof(line) == TYPE_DICTIONARY:
					lines.append(str((line as Dictionary).get("text", "")))
	var quests: Variant = decision.get("quest_operations", [])
	var builds: Variant = decision.get("build_proposals", [])
	var qn: int = quests.size() if typeof(quests) == TYPE_ARRAY else 0
	var bn: int = builds.size() if typeof(builds) == TYPE_ARRAY else 0
	var first_line: String = str(lines[0]) if lines.size() > 0 else "(no dialogue)"
	if first_line.length() > 120:
		first_line = first_line.substr(0, 117) + "..."
	return "decision_id=%s\nquests=%d builds=%d\n\"%s\"" % [did, qn, bn, first_line]


func _record_rejection(reason: String, detail: String) -> void:
	_last_rejection = {
		"reason": reason,
		"detail": detail,
		"at": Time.get_datetime_string_from_system(true),
	}
	decision_rejected.emit(reason, detail)
	print("[PaidGatewayAdapter] REJECT %s — %s" % [reason, detail])


func _open_consent_dialog(decision: Dictionary, summary: String) -> void:
	_close_consent_dialog()
	var scene: PackedScene = load("res://scenes/ui/bridge_consent_dialog.tscn") as PackedScene
	var dialog_node: Node = null
	if scene != null:
		dialog_node = scene.instantiate() as Node
	if dialog_node == null:
		return
	_consent_dialog = dialog_node
	if _consent_dialog.has_method("bind"):
		_consent_dialog.call("bind", self, decision, summary)
	var tree := get_tree()
	var host: Node = tree.root if tree != null else null
	if host != null:
		host.add_child(_consent_dialog)
	else:
		add_child(_consent_dialog)
	if _consent_dialog.has_method("open_dialog"):
		_consent_dialog.call("open_dialog")


func _close_consent_dialog() -> void:
	if _consent_dialog != null and is_instance_valid(_consent_dialog):
		_consent_dialog.queue_free()
	_consent_dialog = null


static func _iso_now() -> String:
	var dt := Time.get_datetime_dict_from_system(true)
	return "%04d-%02d-%02dT%02d:%02d:%02dZ" % [
		int(dt.year), int(dt.month), int(dt.day),
		int(dt.hour), int(dt.minute), int(dt.second),
	]


static func _new_uuid() -> String:
	var b: PackedByteArray = PackedByteArray()
	b.resize(16)
	for i in 16:
		b[i] = randi() % 256
	b[6] = (b[6] & 0x0f) | 0x40
	b[8] = (b[8] & 0x3f) | 0x80
	var hex := b.hex_encode()
	return "%s-%s-%s-%s-%s" % [
		hex.substr(0, 8),
		hex.substr(8, 4),
		hex.substr(12, 4),
		hex.substr(16, 4),
		hex.substr(20, 12),
	]
