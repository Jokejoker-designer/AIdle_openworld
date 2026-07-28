## Control 1B fail-closed Input Context router (kernel).
## Exactly one primary context; unknown context/action IDs rejected with state unchanged.
## Esc priority: cancel stack before pause (contract §5).
## R: build_rotate_right only in build; exploration does not dual-fire camera+build rotate.
## delete_proposal / request_undo emit proposal/compensation events only — no durable erase.
extends Node

const CatalogScript = preload("res://scripts/input/control_action_catalog.gd")

signal context_changed(previous_context: String, new_context: String)
signal action_rejected(action_id: String, reason: String, context_id: String)
signal cancel_resolved(target: String, action_id: String)
signal pause_requested()
signal delete_proposal_requested(payload: Dictionary)
signal undo_compensation_requested(payload: Dictionary)
signal redo_compensation_requested(payload: Dictionary)
signal build_rotate_requested(direction: int)  # -1 left, +1 right
signal action_dispatched(action_id: String, context_id: String)

const DEFAULT_CONTEXT := "exploration"

## Overlay cancel targets (ordered; first applicable wins).
const ESC_ORDER: PackedStringArray = [
	"pending_confirmation",
	"preview_hologram",
	"prompt_composer_or_dialogue",
	"inspect_panel",
	"world_tool_panel",
	"build_mode_idle_exit",
	"pause_menu",
]

var _primary_context: String = DEFAULT_CONTEXT
var _cancel_targets: Dictionary = {
	"pending_confirmation": false,
	"preview_hologram": false,
	"prompt_composer_or_dialogue": false,
	"inspect_panel": false,
	"world_tool_panel": false,
}
## Optional: when true, idle Esc in build may exit build (step 6). Default false — Tab primary.
var allow_esc_exit_build_when_idle: bool = false

var _last_reject_reason: String = ""
var _dispatch_log: Array = []  # recent dispatches for tests (capped)
## P2E-CODEX-ESC-DOUBLE-01: one resolve_escape per process frame (key-repeat / dual callers).
var _escape_resolve_frame: int = -1
var _escape_resolve_count: int = 0
var _last_escape_result: Dictionary = {}


func _ready() -> void:
	CatalogScript.ensure_input_map_actions()
	_primary_context = DEFAULT_CONTEXT
	print("[ControlContextRouter] Ready — primary=%s catalog_v=%s" % [
		_primary_context, CatalogScript.CONTRACT_VERSION
	])


func get_primary_context() -> String:
	return _primary_context


func get_last_reject_reason() -> String:
	return _last_reject_reason


func get_hud_actions() -> PackedStringArray:
	return CatalogScript.get_context_hud_actions(_primary_context)


func set_cancel_target(target: String, active: bool) -> bool:
	if not _cancel_targets.has(target):
		_last_reject_reason = "unknown_cancel_target"
		return false
	_cancel_targets[target] = active
	return true


func get_cancel_targets() -> Dictionary:
	return _cancel_targets.duplicate()


func has_any_cancel_target() -> bool:
	for k in _cancel_targets.keys():
		if bool(_cancel_targets[k]):
			return true
	return false


func request_context(context_id: String) -> Dictionary:
	## Transition primary context. Unknown ID → reject, state unchanged (C1B-CTX-02).
	if not CatalogScript.is_known_context(context_id):
		_last_reject_reason = "unknown_context_id"
		return {
			"ok": false,
			"error": "unknown_context_id",
			"context_id": context_id,
			"primary": _primary_context,
			"unchanged": true,
		}
	if context_id == _primary_context:
		return {
			"ok": true,
			"context_id": context_id,
			"primary": _primary_context,
			"unchanged": true,
		}
	var previous := _primary_context
	_primary_context = context_id
	# Sync inspect / world_tool cancel flags loosely with context for kernel defaults.
	if context_id == "inspect":
		_cancel_targets["inspect_panel"] = true
	elif previous == "inspect":
		_cancel_targets["inspect_panel"] = false
	if context_id == "world_tool":
		_cancel_targets["world_tool_panel"] = true
	elif previous == "world_tool":
		_cancel_targets["world_tool_panel"] = false
	if context_id == "companion":
		_cancel_targets["prompt_composer_or_dialogue"] = true
	elif previous == "companion":
		_cancel_targets["prompt_composer_or_dialogue"] = false
	context_changed.emit(previous, _primary_context)
	return {
		"ok": true,
		"previous": previous,
		"primary": _primary_context,
		"unchanged": false,
		"hud_actions": get_hud_actions(),
	}


func toggle_build_mode() -> Dictionary:
	if _primary_context == "build":
		return request_context(DEFAULT_CONTEXT)
	return request_context("build")


func is_action_allowed(action_id: String) -> bool:
	if not CatalogScript.is_known_action(action_id):
		return false
	return CatalogScript.is_action_allowed_in_context(_primary_context, action_id)


func is_action_just_pressed(action_id: String) -> bool:
	## Context-gated InputMap query — runtime foundation path (no raw keycodes).
	if not is_action_allowed(action_id):
		return false
	if not InputMap.has_action(action_id):
		return false
	return Input.is_action_just_pressed(action_id)


func is_action_pressed(action_id: String) -> bool:
	if not is_action_allowed(action_id):
		return false
	if not InputMap.has_action(action_id):
		return false
	return Input.is_action_pressed(action_id)


func try_dispatch(action_id: String, payload: Dictionary = {}) -> Dictionary:
	## Fail-closed dispatch. Unknown action or not allowed → reject, no side effects.
	if not CatalogScript.is_known_action(action_id):
		_last_reject_reason = "unknown_action_id"
		action_rejected.emit(action_id, "unknown_action_id", _primary_context)
		return {"ok": false, "error": "unknown_action_id", "action_id": action_id}

	var canonical := CatalogScript.resolve_alias(action_id)

	# Safety: proposal / compensation never become direct durable ops.
	if action_id == "delete_proposal" or canonical == "delete_proposal":
		if not is_action_allowed("delete_proposal"):
			_last_reject_reason = "action_not_allowed_in_context"
			action_rejected.emit("delete_proposal", _last_reject_reason, _primary_context)
			return {"ok": false, "error": _last_reject_reason, "action_id": "delete_proposal"}
		var del_payload := payload.duplicate()
		del_payload["mutation_class"] = "proposal_only"
		del_payload["direct_durable"] = false
		del_payload["context_id"] = _primary_context
		delete_proposal_requested.emit(del_payload)
		_record_dispatch("delete_proposal")
		action_dispatched.emit("delete_proposal", _primary_context)
		return {
			"ok": true,
			"action_id": "delete_proposal",
			"mutation_class": "proposal_only",
			"direct_durable": false,
		}

	if action_id == "request_undo" or canonical == "request_undo":
		if not is_action_allowed("request_undo"):
			_last_reject_reason = "action_not_allowed_in_context"
			action_rejected.emit("request_undo", _last_reject_reason, _primary_context)
			return {"ok": false, "error": _last_reject_reason, "action_id": "request_undo"}
		var undo_payload := payload.duplicate()
		undo_payload["mutation_class"] = "compensation_request"
		undo_payload["erases_history"] = false
		undo_payload["direct_durable"] = false
		undo_payload["context_id"] = _primary_context
		undo_compensation_requested.emit(undo_payload)
		_record_dispatch("request_undo")
		action_dispatched.emit("request_undo", _primary_context)
		return {
			"ok": true,
			"action_id": "request_undo",
			"mutation_class": "compensation_request",
			"erases_history": false,
			"direct_durable": false,
		}

	if action_id == "request_redo" or canonical == "request_redo":
		if not is_action_allowed("request_redo"):
			_last_reject_reason = "action_not_allowed_in_context"
			action_rejected.emit("request_redo", _last_reject_reason, _primary_context)
			return {"ok": false, "error": _last_reject_reason, "action_id": "request_redo"}
		var redo_payload := payload.duplicate()
		redo_payload["mutation_class"] = "compensation_request"
		redo_payload["erases_history"] = false
		redo_payload["context_id"] = _primary_context
		redo_compensation_requested.emit(redo_payload)
		_record_dispatch("request_redo")
		action_dispatched.emit("request_redo", _primary_context)
		return {
			"ok": true,
			"action_id": "request_redo",
			"mutation_class": "compensation_request",
			"erases_history": false,
		}

	# Build rotate: only in build (C1B-HK-09/10, C1B-ACT-05).
	if action_id == "build_rotate_right" or action_id == "build_rotate_left":
		if _primary_context != "build":
			_last_reject_reason = "build_rotate_not_in_build_context"
			action_rejected.emit(action_id, _last_reject_reason, _primary_context)
			return {"ok": false, "error": _last_reject_reason, "action_id": action_id}
		if not is_action_allowed(action_id):
			_last_reject_reason = "action_not_allowed_in_context"
			action_rejected.emit(action_id, _last_reject_reason, _primary_context)
			return {"ok": false, "error": _last_reject_reason, "action_id": action_id}
		var dir := 1 if action_id == "build_rotate_right" else -1
		build_rotate_requested.emit(dir)
		_record_dispatch(action_id)
		action_dispatched.emit(action_id, _primary_context)
		return {"ok": true, "action_id": action_id, "direction": dir}

	# Camera rotate right: not dual-fired with build rotate (exploration may omit it).
	if action_id == "rotate_camera_right":
		if _primary_context == "build":
			_last_reject_reason = "camera_rotate_suppressed_in_build"
			action_rejected.emit(action_id, _last_reject_reason, _primary_context)
			return {"ok": false, "error": _last_reject_reason, "action_id": action_id}
		if not is_action_allowed(action_id):
			_last_reject_reason = "action_not_allowed_in_context"
			action_rejected.emit(action_id, _last_reject_reason, _primary_context)
			return {"ok": false, "error": _last_reject_reason, "action_id": action_id}

	# Context enter helpers.
	if action_id == "build_mode_toggle":
		if not is_action_allowed(action_id) and _primary_context != "build" and _primary_context != "exploration":
			# Allow toggle only from exploration/build per catalog.
			if not CatalogScript.is_action_allowed_in_context(_primary_context, action_id):
				_last_reject_reason = "action_not_allowed_in_context"
				action_rejected.emit(action_id, _last_reject_reason, _primary_context)
				return {"ok": false, "error": _last_reject_reason, "action_id": action_id}
		var t := toggle_build_mode()
		_record_dispatch(action_id)
		action_dispatched.emit(action_id, _primary_context)
		return {"ok": true, "action_id": action_id, "context": t}

	if action_id == "companion_call" or action_id == "prompt_quick_open":
		if not is_action_allowed(action_id):
			_last_reject_reason = "action_not_allowed_in_context"
			action_rejected.emit(action_id, _last_reject_reason, _primary_context)
			return {"ok": false, "error": _last_reject_reason, "action_id": action_id}
		var c := request_context("companion")
		_record_dispatch(action_id)
		action_dispatched.emit(action_id, _primary_context)
		return {"ok": true, "action_id": action_id, "context": c}

	if action_id == "inspect_entity":
		if not is_action_allowed(action_id):
			_last_reject_reason = "action_not_allowed_in_context"
			action_rejected.emit(action_id, _last_reject_reason, _primary_context)
			return {"ok": false, "error": _last_reject_reason, "action_id": action_id}
		var i := request_context("inspect")
		_record_dispatch(action_id)
		action_dispatched.emit(action_id, _primary_context)
		return {"ok": true, "action_id": action_id, "context": i}

	if action_id == "world_ability" or action_id == "cozy_helper_pulse" \
			or action_id == "world_panel" or action_id == "cozy_homestead_panel":
		if not is_action_allowed(action_id):
			_last_reject_reason = "action_not_allowed_in_context"
			action_rejected.emit(action_id, _last_reject_reason, _primary_context)
			return {"ok": false, "error": _last_reject_reason, "action_id": action_id}
		# Enter world_tool when panel/ability used from exploration.
		if _primary_context == "exploration":
			request_context("world_tool")
		_record_dispatch(canonical if canonical != action_id else action_id)
		action_dispatched.emit(action_id, _primary_context)
		return {
			"ok": true,
			"action_id": action_id,
			"canonical": canonical,
			"context_id": _primary_context,
			"non_durable": true,
		}

	if action_id == "cancel_action":
		return resolve_escape()

	if action_id == "pause_menu":
		# Direct pause only when no higher cancel target (callers should prefer resolve_escape).
		if has_any_cancel_target():
			return resolve_escape()
		pause_requested.emit()
		_record_dispatch("pause_menu")
		action_dispatched.emit("pause_menu", _primary_context)
		return {"ok": true, "action_id": "pause_menu", "resolved": "pause_menu"}

	if not is_action_allowed(action_id):
		_last_reject_reason = "action_not_allowed_in_context"
		action_rejected.emit(action_id, _last_reject_reason, _primary_context)
		return {"ok": false, "error": _last_reject_reason, "action_id": action_id}

	_record_dispatch(action_id)
	action_dispatched.emit(action_id, _primary_context)
	return {"ok": true, "action_id": action_id, "context_id": _primary_context}


func get_escape_resolve_count() -> int:
	return _escape_resolve_count


func reset_escape_resolve_count() -> void:
	_escape_resolve_count = 0
	_escape_resolve_frame = -1
	_last_escape_result = {}


func resolve_escape() -> Dictionary:
	## Contract §5 ordered Esc priority. Stop at first applicable cancel target.
	## Count real resolutions (tests assert single physical Esc → one apply via Main guard).
	_escape_resolve_count += 1
	_escape_resolve_frame = Engine.get_process_frames()

	# 1 pending confirmation
	if bool(_cancel_targets.get("pending_confirmation", false)):
		_cancel_targets["pending_confirmation"] = false
		var r1 := {
			"ok": true,
			"resolved": "pending_confirmation",
			"action_id": "cancel_action",
			"pause": false,
		}
		_finish_escape(r1)
		return r1
	# 2 preview hologram
	if bool(_cancel_targets.get("preview_hologram", false)):
		_cancel_targets["preview_hologram"] = false
		var r2 := {
			"ok": true,
			"resolved": "preview_hologram",
			"action_id": "cancel_action",
			"pause": false,
			"orphan_safe": true,
		}
		_finish_escape(r2)
		return r2
	# 3 composer / dialogue
	if bool(_cancel_targets.get("prompt_composer_or_dialogue", false)):
		_cancel_targets["prompt_composer_or_dialogue"] = false
		if _primary_context == "companion":
			request_context(DEFAULT_CONTEXT)
		var r3 := {
			"ok": true,
			"resolved": "prompt_composer_or_dialogue",
			"action_id": "cancel_action",
			"pause": false,
		}
		_finish_escape(r3)
		return r3
	# 4 inspect
	if bool(_cancel_targets.get("inspect_panel", false)) or _primary_context == "inspect":
		_cancel_targets["inspect_panel"] = false
		if _primary_context == "inspect":
			request_context(DEFAULT_CONTEXT)
		var r4 := {
			"ok": true,
			"resolved": "inspect_panel",
			"action_id": "cancel_action",
			"pause": false,
		}
		_finish_escape(r4)
		return r4
	# 5 world tool panel
	if bool(_cancel_targets.get("world_tool_panel", false)) or _primary_context == "world_tool":
		_cancel_targets["world_tool_panel"] = false
		if _primary_context == "world_tool":
			request_context(DEFAULT_CONTEXT)
		var r5 := {
			"ok": true,
			"resolved": "world_tool_panel",
			"action_id": "cancel_action",
			"pause": false,
		}
		_finish_escape(r5)
		return r5
	# 6 optional idle build exit
	if allow_esc_exit_build_when_idle and _primary_context == "build":
		request_context(DEFAULT_CONTEXT)
		var r6 := {
			"ok": true,
			"resolved": "build_mode_idle_exit",
			"action_id": "build_mode_toggle",
			"pause": false,
		}
		_finish_escape(r6)
		return r6
	# 6b P2E F05-R2: while Build is primary, Esc must NEVER open Pause.
	if _primary_context == "build":
		var r6b := {
			"ok": true,
			"resolved": "build_esc_no_pause",
			"action_id": "cancel_action",
			"pause": false,
		}
		_finish_escape(r6b)
		return r6b
	# 7 pause only when nothing above applies and not in Build
	var r7 := {
		"ok": true,
		"resolved": "pause_menu",
		"action_id": "pause_menu",
		"pause": true,
	}
	_finish_escape(r7)
	if bool(r7.get("pause", false)):
		pause_requested.emit()
	return r7


func _finish_escape(result: Dictionary) -> void:
	## Emit once per real resolve; Main suppresses signal re-apply while _esc_dispatch_guard is set.
	_last_escape_result = result.duplicate(true)
	var aid := str(result.get("action_id", "cancel_action"))
	_record_dispatch(aid)
	action_dispatched.emit(aid, _primary_context)
	cancel_resolved.emit(str(result.get("resolved", "")), aid)


func simulate_physical_r() -> Dictionary:
	## Conflict probe: R must not dual-fire camera + build rotate (C1B-CF-01 / ACT-05).
	var fired: PackedStringArray = []
	if is_action_allowed("build_rotate_right"):
		var br := try_dispatch("build_rotate_right")
		if bool(br.get("ok", false)):
			fired.append("build_rotate_right")
	if is_action_allowed("rotate_camera_right"):
		var cr := try_dispatch("rotate_camera_right")
		if bool(cr.get("ok", false)):
			fired.append("rotate_camera_right")
	var dual := fired.size() > 1
	return {
		"context": _primary_context,
		"fired": fired,
		"dual_fire": dual,
		"ok": not dual,
	}


func get_dispatch_log() -> Array:
	return _dispatch_log.duplicate()


func clear_dispatch_log() -> void:
	_dispatch_log.clear()


func reset_to_defaults() -> void:
	_primary_context = DEFAULT_CONTEXT
	for k in _cancel_targets.keys():
		_cancel_targets[k] = false
	_last_reject_reason = ""
	_dispatch_log.clear()
	allow_esc_exit_build_when_idle = false


func _record_dispatch(action_id: String) -> void:
	_dispatch_log.append({"action_id": action_id, "context": _primary_context})
	if _dispatch_log.size() > 64:
		_dispatch_log.pop_front()
