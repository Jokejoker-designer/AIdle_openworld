## Free Desktop Bridge (G2-005): clipboard + local inbox/outbox transport.
## - Export redacted World State Snapshot (schema-shaped).
## - Import Decision Envelope only after structural/policy checks.
## - Manual visible consent required — no auto-apply of decisions.
## - Reject malformed JSON, stale source_snapshot_id, replayed decision_id.
## - No network/API SDK. Bridge never mutates durable world state (G2-006 executes).
class_name DesktopBridgeModule
extends Node

const MODULE_ID := "desktop_bridge"

signal snapshot_exported(snapshot: Dictionary, channel: String, path: String)
signal decision_pending_consent(decision: Dictionary, summary: String)
signal decision_accepted(decision: Dictionary)
signal decision_rejected(reason: String, detail: String)
signal consent_cancelled(reason: String)

@export var show_consent_ui: bool = true
@export var edition: String = BridgePaths.EDITION_DESKTOP_BRIDGE_FREE

var _builder: BridgeSnapshotBuilder
var _guard: BridgeDecisionImportGuard
var _live_snapshot: Dictionary = {}
var _live_snapshot_id: String = ""
var _pending_decision: Dictionary = {}
var _accepted_decision: Dictionary = {}
var _seen_decision_ids: Dictionary = {}  # decision_id -> true
var _last_rejection: Dictionary = {}
var _consent_dialog: Control
var _registered: bool = false


func _ready() -> void:
	_builder = BridgeSnapshotBuilder.new()
	_guard = BridgeDecisionImportGuard.new()
	BridgePaths.ensure_bridge_dirs()
	if not ModuleRegistry.has_module(MODULE_ID):
		ModuleRegistry.register_module(MODULE_ID, self)
		_registered = true
	print("[DesktopBridgeModule] Ready – Free Desktop Bridge (no network).")


func _exit_tree() -> void:
	if _registered and ModuleRegistry.has_module(MODULE_ID):
		if ModuleRegistry.get_module(MODULE_ID) == self:
			ModuleRegistry.unregister_module(MODULE_ID)


func is_stub() -> bool:
	return false


func get_status() -> String:
	var pending := "yes" if has_pending_consent() else "no"
	return "DesktopBridge free | live=%s | pending_consent=%s | seen=%d" % [
		_live_snapshot_id if not _live_snapshot_id.is_empty() else "-",
		pending,
		_seen_decision_ids.size(),
	]


func uses_network() -> bool:
	return false


# ─── Snapshot export ─────────────────────────────────────────────────────────

func build_snapshot(context: Dictionary = {}) -> Dictionary:
	var ctx := context.duplicate(true)
	if not ctx.has("edition"):
		ctx["edition"] = edition
	var snap := _builder.build(ctx)
	var errs := _builder.validate_structure(snap)
	if not errs.is_empty():
		push_warning("[DesktopBridgeModule] snapshot structure issues: %s" % ", ".join(errs))
	_live_snapshot = snap.duplicate(true)
	_live_snapshot_id = str(snap.get("snapshot_id", ""))
	return snap.duplicate(true)


func get_live_snapshot() -> Dictionary:
	return _live_snapshot.duplicate(true)


func get_live_snapshot_id() -> String:
	return _live_snapshot_id


func export_snapshot_to_clipboard(context: Dictionary = {}) -> Dictionary:
	var ctx := context.duplicate(true)
	ctx["channel"] = BridgePaths.CHANNEL_CLIPBOARD
	var snap := build_snapshot(ctx)
	var payload := _builder.clipboard_payload(snap)
	DisplayServer.clipboard_set(payload)
	snapshot_exported.emit(snap, BridgePaths.CHANNEL_CLIPBOARD, "")
	return {
		"ok": true,
		"channel": BridgePaths.CHANNEL_CLIPBOARD,
		"snapshot_id": _live_snapshot_id,
		"path": "",
		"bytes": payload.length(),
	}


func export_snapshot_to_file(context: Dictionary = {}, path: String = "") -> Dictionary:
	BridgePaths.ensure_bridge_dirs()
	var ctx := context.duplicate(true)
	ctx["channel"] = BridgePaths.CHANNEL_FILE
	if path.is_empty():
		path = BridgePaths.outbox_snapshot_path()
	ctx["bridge_path_hint"] = path
	var snap := build_snapshot(ctx)
	var text := _builder.to_pretty_json(snap)
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		return {
			"ok": false,
			"channel": BridgePaths.CHANNEL_FILE,
			"snapshot_id": _live_snapshot_id,
			"path": path,
			"error": "open_failed:%s" % FileAccess.get_open_error(),
		}
	file.store_string(text)
	file.close()
	snapshot_exported.emit(snap, BridgePaths.CHANNEL_FILE, path)
	return {
		"ok": true,
		"channel": BridgePaths.CHANNEL_FILE,
		"snapshot_id": _live_snapshot_id,
		"path": path,
		"bytes": text.length(),
	}


## Convenience: export to both clipboard and outbox file.
func export_snapshot_both(context: Dictionary = {}) -> Dictionary:
	var file_result := export_snapshot_to_file(context)
	# Re-export clipboard using the same live snapshot (do not rebuild id).
	if not _live_snapshot.is_empty():
		var payload := _builder.clipboard_payload(_live_snapshot)
		DisplayServer.clipboard_set(payload)
		snapshot_exported.emit(_live_snapshot, BridgePaths.CHANNEL_CLIPBOARD, "")
	return {
		"ok": bool(file_result.get("ok", false)),
		"file": file_result,
		"clipboard": true,
		"snapshot_id": _live_snapshot_id,
	}


# ─── Decision import (validate → pending consent → confirm) ──────────────────

## Import raw text. Never auto-applies unless auto_consent=true (smoke/tests only).
## Production UI always leaves auto_consent=false and shows consent dialog.
func import_decision_from_text(raw_text: String, auto_consent: bool = false) -> Dictionary:
	var result := _guard.evaluate(raw_text, _live_snapshot_id, _seen_decision_ids)
	if not bool(result.get("ok", false)):
		_record_rejection(str(result.get("reason", "")), str(result.get("detail", "")))
		return {
			"ok": false,
			"status": "rejected",
			"reason": result.get("reason", ""),
			"detail": result.get("detail", ""),
			"pending": false,
			"accepted": false,
		}

	var decision: Dictionary = result.get("decision", {}) as Dictionary
	_pending_decision = decision.duplicate(true)
	var summary := _summarize_decision(decision)
	decision_pending_consent.emit(decision, summary)

	if show_consent_ui and not auto_consent:
		_open_consent_dialog(decision, summary)

	if auto_consent:
		# Headless smoke path only — still goes through confirm API.
		return confirm_pending_decision()

	return {
		"ok": true,
		"status": "awaiting_consent",
		"reason": "",
		"detail": summary,
		"pending": true,
		"accepted": false,
		"decision_id": str(decision.get("decision_id", "")),
		"source_snapshot_id": str(decision.get("source_snapshot_id", "")),
	}


func import_decision_from_clipboard(auto_consent: bool = false) -> Dictionary:
	var text := DisplayServer.clipboard_get()
	return import_decision_from_text(text, auto_consent)


func import_decision_from_file(path: String = "", auto_consent: bool = false) -> Dictionary:
	if path.is_empty():
		path = BridgePaths.inbox_decision_path()
	if not FileAccess.file_exists(path):
		_record_rejection(BridgePaths.REJECT_EMPTY_INPUT, "inbox file missing: %s" % path)
		return {
			"ok": false,
			"status": "rejected",
			"reason": BridgePaths.REJECT_EMPTY_INPUT,
			"detail": "inbox file missing: %s" % path,
			"pending": false,
			"accepted": false,
		}
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		_record_rejection(BridgePaths.REJECT_EMPTY_INPUT, "cannot open: %s" % path)
		return {
			"ok": false,
			"status": "rejected",
			"reason": BridgePaths.REJECT_EMPTY_INPUT,
			"detail": "cannot open: %s" % path,
			"pending": false,
			"accepted": false,
		}
	var text := file.get_as_text()
	file.close()
	return import_decision_from_text(text, auto_consent)


func has_pending_consent() -> bool:
	return not _pending_decision.is_empty()


func get_pending_decision() -> Dictionary:
	return _pending_decision.duplicate(true)


## Explicit player confirm — sole path from pending → accepted.
## Bridge does not execute; G2-006 consumes accepted decisions.
func confirm_pending_decision() -> Dictionary:
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

	# Re-check stale/replay at confirm time (live snapshot may have advanced).
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
		# Handoff marker for G2-006 — bridge does not apply effects.
		"routes_to": "agm_decision_executor",
		"executed": false,
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


## Clear accepted-but-not-executed handoff (after executor consumes). Does not
## clear seen ids — replays remain rejected.
func clear_accepted_handoff() -> void:
	_accepted_decision = {}


## Test helper: seed live snapshot id without full export (policy unit tests).
func set_live_snapshot_for_tests(snapshot_id: String, snapshot: Dictionary = {}) -> void:
	_live_snapshot_id = snapshot_id
	if not snapshot.is_empty():
		_live_snapshot = snapshot.duplicate(true)
	else:
		_live_snapshot = {"snapshot_id": snapshot_id, "schema_version": "1.0.0"}


## Test helper: mark a decision_id as already accepted (replay suite).
func mark_decision_seen_for_tests(decision_id: String) -> void:
	_seen_decision_ids[decision_id] = true


# ─── Consent UI ──────────────────────────────────────────────────────────────

func _open_consent_dialog(decision: Dictionary, summary: String) -> void:
	_close_consent_dialog()
	var scene: PackedScene = load("res://scenes/ui/bridge_consent_dialog.tscn") as PackedScene
	if scene == null:
		# Fallback programmatic dialog if scene missing.
		_consent_dialog = _make_fallback_dialog(summary)
	else:
		_consent_dialog = scene.instantiate() as Control
	if _consent_dialog == null:
		push_warning("[DesktopBridgeModule] consent dialog failed to instantiate")
		return
	if _consent_dialog.has_method("bind"):
		_consent_dialog.call("bind", self, decision, summary)
	elif _consent_dialog.has_signal("confirmed"):
		# Generic AcceptDialog wiring
		if not _consent_dialog.is_connected("confirmed", Callable(self, "confirm_pending_decision")):
			_consent_dialog.connect("confirmed", Callable(self, "confirm_pending_decision"))
		if _consent_dialog.has_signal("canceled"):
			if not _consent_dialog.is_connected("canceled", Callable(self, "_on_dialog_canceled")):
				_consent_dialog.connect("canceled", Callable(self, "_on_dialog_canceled"))
	var host := get_tree().root if get_tree() else null
	if host:
		host.add_child(_consent_dialog)
	else:
		add_child(_consent_dialog)
	if _consent_dialog.has_method("open_dialog"):
		_consent_dialog.call("open_dialog")
	elif _consent_dialog is Window:
		(_consent_dialog as Window).popup_centered()
	elif _consent_dialog.has_method("popup_centered"):
		_consent_dialog.call("popup_centered")
	else:
		_consent_dialog.visible = true


func _make_fallback_dialog(summary: String) -> AcceptDialog:
	var dlg := AcceptDialog.new()
	dlg.name = "BridgeConsentFallback"
	dlg.title = "Import AGM Decision?"
	dlg.dialog_text = (
		"Desktop Bridge received a Decision Envelope.\n\n%s\n\n"
		+ "Accept only if you pasted this from your AI Desktop intentionally.\n"
		+ "Nothing is applied until you confirm. Builds still need preview."
	) % summary
	dlg.ok_button_text = "Accept decision"
	dlg.add_cancel_button("Reject")
	dlg.confirmed.connect(func() -> void: confirm_pending_decision())
	dlg.canceled.connect(func() -> void: reject_pending_decision("player_rejected"))
	return dlg


func _on_dialog_canceled() -> void:
	reject_pending_decision("player_rejected")


func _close_consent_dialog() -> void:
	if _consent_dialog != null and is_instance_valid(_consent_dialog):
		_consent_dialog.queue_free()
	_consent_dialog = null


func _summarize_decision(decision: Dictionary) -> String:
	var did := str(decision.get("decision_id", "?"))
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
	var qn := quests.size() if typeof(quests) == TYPE_ARRAY else 0
	var bn := builds.size() if typeof(builds) == TYPE_ARRAY else 0
	var first_line := lines[0] if lines.size() > 0 else "(no dialogue)"
	if str(first_line).length() > 120:
		first_line = str(first_line).substr(0, 117) + "..."
	return "decision_id=%s\nquests=%d builds=%d\n\"%s\"" % [did, qn, bn, first_line]


func _record_rejection(reason: String, detail: String) -> void:
	_last_rejection = {
		"reason": reason,
		"detail": detail,
		"at": Time.get_datetime_string_from_system(true),
	}
	decision_rejected.emit(reason, detail)
	print("[DesktopBridgeModule] REJECT %s — %s" % [reason, detail])
