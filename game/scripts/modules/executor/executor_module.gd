## Agent-Executor module (G2-006): deterministic AGM Decision executor +
## World Prompt pipeline (preview → confirm → commit handoff stub).
##
## Invariants:
## - Allowlisted Decision Envelope actions only.
## - decision_id idempotency (replay returns prior receipt; no re-apply).
## - Builds never skip preview/confirm/commit contracts.
## - No paid provider SDKs; no direct SceneTree durable mutation.
## - World Commit service remains the sole durable mutator (stubbed handoff).
class_name ExecutorModule
extends Node

const MODULE_ID := "executor"
const _DecisionExec = preload("res://scripts/modules/executor/decision_executor.gd")
const _Pipeline = preload("res://scripts/modules/executor/prompt_pipeline.gd")
const _IExecutor = preload("res://scripts/modules/interfaces/i_executor_module.gd")

signal decision_executed(receipt: Dictionary)
signal prompt_submitted(prompt_id: String, stage: String)
signal prompt_confirmed(prompt_id: String, commit_request: Dictionary)
signal prompt_cancelled(prompt_id: String, reason: String)

var _decision_exec: RefCounted
var _pipeline: RefCounted
var _live_snapshot: Dictionary = {}
var _last_receipt: Dictionary = {}


func _ready() -> void:
	_decision_exec = _DecisionExec.new()
	_pipeline = _Pipeline.new()
	_try_register()
	var missing: PackedStringArray = _IExecutor.validate(self)
	if not missing.is_empty():
		push_error("[ExecutorModule] Missing API methods: %s" % str(missing))
	print("[ExecutorModule] Ready – AGM decision executor + preview/confirm/commit handoff stub.")


func is_stub() -> bool:
	return false


func get_status() -> String:
	var seen: PackedStringArray = _decision_exec.call("list_seen_decision_ids") as PackedStringArray
	var prompts: PackedStringArray = _pipeline.call("list_prompt_ids") as PackedStringArray
	return "Executor online | decisions=%d | prompts=%d | last=%s" % [
		seen.size(),
		prompts.size(),
		str(_last_receipt.get("status", "none")),
	]


func _try_register() -> void:
	var existing: Node = ModuleRegistry.get_module(MODULE_ID)
	if existing == null or existing == self or existing.has_method("is_stub"):
		ModuleRegistry.register_module(MODULE_ID, self)


# ─── IExecutorModule: World Prompt path ──────────────────────────────────────

## Companion/System → Executor. Enters preview only; never commits durable state.
func submit_prompt(structured_world_prompt: Dictionary) -> String:
	var result: Dictionary = _pipeline.call("submit", structured_world_prompt, "companion") as Dictionary
	if not bool(result.get("ok", false)):
		push_warning("[ExecutorModule] submit_prompt rejected: %s" % str(result.get("reason", "")))
		return ""
	var prompt_id := str(result.get("prompt_id", ""))
	_maybe_start_preview_manifestation(structured_world_prompt, prompt_id)
	prompt_submitted.emit(prompt_id, str(result.get("pipeline_stage", "preview")))
	return prompt_id


func cancel_prompt(prompt_id: String, reason: String = "cancel") -> void:
	var result: Dictionary = _pipeline.call("cancel", prompt_id, reason) as Dictionary
	if bool(result.get("ok", false)):
		_maybe_cancel_manifestation(prompt_id, reason)
		prompt_cancelled.emit(prompt_id, reason)


func get_prompt_status(prompt_id: String) -> Dictionary:
	return _pipeline.call("get_status", prompt_id) as Dictionary


# ─── AGM Decision execution (G2-006) ─────────────────────────────────────────

func set_live_snapshot(snapshot: Dictionary) -> void:
	_live_snapshot = snapshot.duplicate(true)
	if not _live_snapshot.is_empty():
		_decision_exec.call("configure_context", {
			"world_revision": int(_live_snapshot.get("world_revision", 0)),
			"space_id": str(_live_snapshot.get("space_id", "home_01")),
			"player_id": str(
				((_live_snapshot.get("player", {}) as Dictionary).get("player_id", "player_01"))
			),
			"companion_id": str(
				((_live_snapshot.get("companion", {}) as Dictionary).get("companion_id", "companion_lumi"))
			),
			"mood": float(((_live_snapshot.get("companion", {}) as Dictionary).get("mood", 0.5))),
			"relationship": float(
				((_live_snapshot.get("companion", {}) as Dictionary).get("relationship", 0.5))
			),
		})


func get_live_snapshot() -> Dictionary:
	return _live_snapshot.duplicate(true)


## Execute allowlisted Decision Envelope actions. Returns execution receipt.
func execute_decision(decision: Dictionary, live_snapshot: Dictionary = {}) -> Dictionary:
	var snap := live_snapshot if not live_snapshot.is_empty() else _live_snapshot
	if not live_snapshot.is_empty():
		set_live_snapshot(live_snapshot)

	var receipt: Dictionary = _decision_exec.call("execute", decision, snap) as Dictionary
	_last_receipt = receipt.duplicate(true)

	var status := str(receipt.get("status", ""))
	# Idempotent replay / hard rejects: do not re-apply soft effects or re-submit builds.
	if status in ["replayed", "rejected", "stale_snapshot"]:
		decision_executed.emit(receipt)
		return receipt.duplicate(true)

	# Soft dialogue → companion chat when module present (text-only).
	_deliver_dialogue_to_companion(receipt)

	# Soft mood → companion expression when present.
	_apply_mood_to_companion(receipt)

	# Build handoffs → prompt pipeline (preview stage only; never durable).
	if receipt.has("build_handoffs") and receipt["build_handoffs"] is Array:
		var updated_handoffs: Array = []
		for h in receipt["build_handoffs"]:
			if typeof(h) != TYPE_DICTIONARY:
				continue
			var handoff: Dictionary = (h as Dictionary).duplicate(true)
			var wp: Dictionary = handoff.get("world_prompt", {}) as Dictionary
			if not wp.is_empty():
				var sub: Dictionary = _pipeline.call("submit", wp, "agm_decision") as Dictionary
				if bool(sub.get("ok", false)):
					var pid := str(sub.get("prompt_id", ""))
					handoff["pipeline_stage"] = "preview"
					handoff["prompt_id"] = pid
					_maybe_start_preview_manifestation(wp, pid)
					prompt_submitted.emit(pid, "preview")
			updated_handoffs.append(handoff)
		receipt["build_handoffs"] = updated_handoffs
		_last_receipt = receipt.duplicate(true)

	decision_executed.emit(receipt)
	return receipt.duplicate(true)


func get_execution_receipt(decision_id: String) -> Dictionary:
	return _decision_exec.call("get_receipt", decision_id) as Dictionary


func get_last_execution_receipt() -> Dictionary:
	return _last_receipt.duplicate(true)


## Projection for World State Snapshot.last_execution_receipt.
func get_snapshot_execution_receipt(decision_id: String = "") -> Dictionary:
	var full: Dictionary
	if decision_id.is_empty():
		full = _last_receipt
	else:
		full = get_execution_receipt(decision_id)
	return _decision_exec.call("to_snapshot_receipt", full) as Dictionary


func has_seen_decision(decision_id: String) -> bool:
	return bool(_decision_exec.call("has_seen_decision", decision_id))


func list_allowlisted_event_types() -> PackedStringArray:
	return _DecisionExec.list_allowlisted_event_types()


func list_allowlisted_quest_ops() -> PackedStringArray:
	return _DecisionExec.list_allowlisted_quest_ops()


func get_soft_state() -> Dictionary:
	return _decision_exec.call("get_soft_state") as Dictionary


## Player confirms a previewed prompt → commit_request handoff stub.
func confirm_prompt(prompt_id: String, confirmed_by: String = "player_01") -> Dictionary:
	var rev := 0
	if not _live_snapshot.is_empty():
		rev = int(_live_snapshot.get("world_revision", 0))
	var result: Dictionary = _pipeline.call("confirm", prompt_id, confirmed_by, rev) as Dictionary
	if bool(result.get("ok", false)):
		var cr: Dictionary = result.get("commit_request", {}) as Dictionary
		prompt_confirmed.emit(prompt_id, cr)
		# Intentionally do NOT finalize manifestation to durable collision.
		# World Commit service owns durable mutation; this is handoff only.
	return result


func get_pending_build_handoffs() -> Array:
	return _pipeline.call("list_pending_preview") as Array


func get_commit_handoffs() -> Array:
	return _pipeline.call("list_commit_handoffs") as Array


func configure_context(ctx: Dictionary) -> void:
	_decision_exec.call("configure_context", ctx)


# ─── Companion / manifestation soft bridges ──────────────────────────────────

func _deliver_dialogue_to_companion(receipt: Dictionary) -> void:
	if str(receipt.get("status", "")) in ["rejected", "stale_snapshot", "replayed"]:
		if str(receipt.get("status", "")) == "replayed":
			return
		return
	var lines: Variant = receipt.get("dialogue_delivered", [])
	if typeof(lines) != TYPE_ARRAY or (lines as Array).is_empty():
		return
	if not ModuleRegistry.has_module(AIdleConstants.MODULE_COMPANION):
		return
	var companion: Node = ModuleRegistry.get_module(AIdleConstants.MODULE_COMPANION)
	if companion == null:
		return
	for line in lines:
		if typeof(line) != TYPE_DICTIONARY:
			continue
		var L: Dictionary = line
		var speaker := str(L.get("speaker", "companion"))
		var text := str(L.get("text", ""))
		if text.is_empty():
			continue
		if companion.has_method("_append_chat"):
			var role := "companion" if speaker == "companion" else "system"
			companion.call("_append_chat", role, text)
		elif companion.has_signal("chat_message"):
			companion.emit_signal("chat_message", speaker, text)


func _apply_mood_to_companion(receipt: Dictionary) -> void:
	if str(receipt.get("status", "")) in ["rejected", "stale_snapshot", "replayed"]:
		return
	if not receipt.has("mood_after"):
		return
	if not ModuleRegistry.has_module(AIdleConstants.MODULE_COMPANION):
		return
	var companion: Node = ModuleRegistry.get_module(AIdleConstants.MODULE_COMPANION)
	if companion == null or not companion.has_method("set_emotional_state"):
		return
	var mood_val := float(receipt.get("mood_after", 0.5))
	var label := "calm"
	if mood_val >= 0.75:
		label = "joyful"
	elif mood_val >= 0.55:
		label = "warm"
	elif mood_val <= 0.25:
		label = "tired"
	elif mood_val <= 0.4:
		label = "concerned"
	companion.call("set_emotional_state", label)


func _maybe_start_preview_manifestation(world_prompt: Dictionary, prompt_id: String) -> void:
	if prompt_id.is_empty() or world_prompt.is_empty():
		return
	if not ModuleRegistry.has_module(AIdleConstants.MODULE_VOXEL):
		return
	var man: Node = ModuleRegistry.get_module(AIdleConstants.MODULE_VOXEL)
	if man == null or not man.has_method("start_manifestation"):
		return
	# Skip stubs that are not real manifestation modules.
	if man.has_method("is_stub") and bool(man.call("is_stub")):
		return
	var style := "cozy_cyber_pixel_2_5d"
	var sp: Variant = world_prompt.get("style_profile", {})
	if sp is Dictionary:
		style = str((sp as Dictionary).get("base_concept", style))
	var entity: Dictionary = world_prompt.get("entity", {}) as Dictionary
	var target: Dictionary = world_prompt.get("target", {}) as Dictionary
	var geometry := {
		"target_space": str(target.get("space_type", "private_reality")),
		"recipe_id": str(entity.get("recipe_id", "")),
		"transform": entity.get("transform", {}),
		"bounds": entity.get("bounds", {}),
		"provenance": world_prompt.get("provenance", {}),
		"preview_only": true,
	}
	man.call("start_manifestation", prompt_id, style, geometry)


func _maybe_cancel_manifestation(prompt_id: String, reason: String) -> void:
	if not ModuleRegistry.has_module(AIdleConstants.MODULE_VOXEL):
		return
	var man: Node = ModuleRegistry.get_module(AIdleConstants.MODULE_VOXEL)
	if man == null or not man.has_method("cancel_manifestation"):
		return
	if man.has_method("is_stub") and bool(man.call("is_stub")):
		return
	man.call("cancel_manifestation", prompt_id, reason)
