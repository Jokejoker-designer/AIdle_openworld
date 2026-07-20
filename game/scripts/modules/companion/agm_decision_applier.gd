## Validates and projects AGM Decision Envelopes into Companion-facing effects.
## Consumes contracts/agm/decision_envelope.schema.json (schema-informed checks).
## Does NOT commit world state. Build proposals become pending World Prompts only.
## Text-only: rejects TTS/voice/mic/secrets/code/durable mutation fields.
class_name CompanionAgmDecisionApplier
extends RefCounted

const SCHEMA_VERSION := "1.0.0"
const ALLOWED_EDITIONS: PackedStringArray = ["desktop_bridge_free", "api_paid"]
const ALLOWED_SPEAKERS: PackedStringArray = ["companion", "narrator", "npc"]
const ALLOWED_EXPRESSIONS: PackedStringArray = [
	"neutral", "warm", "curious", "playful", "concerned", "proud", "tired"
]
const ALLOWED_BUILD_OPS: PackedStringArray = [
	"create", "modify", "delete", "enrich", "gift_proposal"
]
const ALLOWED_ENTITY_KINDS: PackedStringArray = [
	"tile_layer",
	"terrain_patch_2_5d",
	"modular_structure_2_5d",
	"prop_2_5d",
	"character_2_5d",
	"vehicle_2_5d",
]
const ALLOWED_EVENT_TYPES: PackedStringArray = [
	"pacing.slow_down",
	"pacing.speed_up",
	"ambient.weather_hint",
	"ambient.time_of_day_hint",
	"narrative.beat",
	"companion.attention",
	"quest.hint",
	"onboarding.nudge",
]
const ALLOWED_QUEST_OPS: PackedStringArray = [
	"offer", "update_objective", "mark_ready", "complete", "fail", "cancel"
]
const ALLOWED_TRIGGER_KINDS: PackedStringArray = [
	"player_action", "timer", "quest_progress", "location_enter", "manual_bridge", "none"
]

## Forbidden top-level keys (mirror decision_envelope propertyNames ban list).
const FORBIDDEN_KEYS: PackedStringArray = [
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

const REQUIRED_TOP: PackedStringArray = [
	"schema_version",
	"decision_id",
	"source_snapshot_id",
	"created_at",
	"edition",
	"session_id",
	"dialogue",
	"quest_operations",
	"build_proposals",
	"event_proposals",
	"mood_delta",
	"relationship_delta",
	"next_trigger",
	"trace",
]

## Schema caps for deltas.
const MOOD_DELTA_MIN := -0.1
const MOOD_DELTA_MAX := 0.1
const REL_DELTA_MIN := -0.05
const REL_DELTA_MAX := 0.05

## decision_id → application receipt (replay rejection).
var _applied: Dictionary = {}
var live_snapshot_id: String = ""


func set_live_snapshot_id(snapshot_id: String) -> void:
	live_snapshot_id = snapshot_id.strip_edges()


func clear_applied_history() -> void:
	_applied.clear()


func was_applied(decision_id: String) -> bool:
	return _applied.has(decision_id)


func get_applied_ids() -> PackedStringArray:
	var out: PackedStringArray = []
	for k in _applied.keys():
		out.append(str(k))
	return out


## Validate envelope shape + policy (stale snapshot, replay, forbidden fields).
## Returns { "ok": bool, "errors": PackedStringArray }.
func validate(envelope: Dictionary) -> Dictionary:
	var errors: PackedStringArray = []
	if envelope.is_empty():
		errors.append("envelope empty")
		return {"ok": false, "errors": errors}

	for key in FORBIDDEN_KEYS:
		if envelope.has(key):
			errors.append("forbidden field: %s" % key)

	for req in REQUIRED_TOP:
		if not envelope.has(req):
			errors.append("missing required: %s" % req)

	if str(envelope.get("schema_version", "")) != SCHEMA_VERSION:
		errors.append("schema_version must be %s" % SCHEMA_VERSION)

	var edition := str(envelope.get("edition", ""))
	if edition not in ALLOWED_EDITIONS:
		errors.append("invalid edition: %s" % edition)

	var decision_id := str(envelope.get("decision_id", ""))
	if decision_id.is_empty():
		errors.append("decision_id empty")
	elif _applied.has(decision_id):
		errors.append("replay rejected: decision_id already applied")

	var source_snap := str(envelope.get("source_snapshot_id", ""))
	if not live_snapshot_id.is_empty() and source_snap != live_snapshot_id:
		errors.append(
			"stale snapshot: source_snapshot_id=%s live=%s" % [source_snap, live_snapshot_id]
		)

	# Dialogue
	var dialogue: Variant = envelope.get("dialogue", null)
	if typeof(dialogue) != TYPE_DICTIONARY:
		errors.append("dialogue must be object")
	else:
		var d: Dictionary = dialogue
		if not d.has("lines") or typeof(d["lines"]) != TYPE_ARRAY:
			errors.append("dialogue.lines must be array")
		else:
			var lines: Array = d["lines"]
			if lines.size() > 12:
				errors.append("dialogue.lines maxItems 12")
			for i in lines.size():
				var line_v: Variant = lines[i]
				if typeof(line_v) != TYPE_DICTIONARY:
					errors.append("dialogue.lines[%d] not object" % i)
					continue
				var line: Dictionary = line_v
				var speaker := str(line.get("speaker", ""))
				if speaker not in ALLOWED_SPEAKERS:
					errors.append("dialogue.lines[%d] bad speaker" % i)
				var text := str(line.get("text", ""))
				if text.is_empty() or text.length() > 480:
					errors.append("dialogue.lines[%d] text length" % i)
				if speaker == "npc" and str(line.get("npc_id", "")).is_empty():
					errors.append("dialogue.lines[%d] npc requires npc_id" % i)
		if d.has("companion_expression"):
			var expr := str(d["companion_expression"])
			if expr not in ALLOWED_EXPRESSIONS:
				errors.append("invalid companion_expression: %s" % expr)

	# Build proposals — must stay pending + preview_confirm_commit
	var builds_v: Variant = envelope.get("build_proposals", null)
	if typeof(builds_v) != TYPE_ARRAY:
		errors.append("build_proposals must be array")
	else:
		var builds: Array = builds_v
		if builds.size() > 4:
			errors.append("build_proposals maxItems 4")
		for i in builds.size():
			_validate_build_item(builds[i], i, errors)

	# Event proposals allowlist
	var events_v: Variant = envelope.get("event_proposals", null)
	if typeof(events_v) != TYPE_ARRAY:
		errors.append("event_proposals must be array")
	else:
		var events: Array = events_v
		if events.size() > 8:
			errors.append("event_proposals maxItems 8")
		for i in events.size():
			if typeof(events[i]) != TYPE_DICTIONARY:
				errors.append("event_proposals[%d] not object" % i)
				continue
			var ev: Dictionary = events[i]
			var et := str(ev.get("event_type", ""))
			if et not in ALLOWED_EVENT_TYPES:
				errors.append("unknown event_type: %s" % et)
			if str(ev.get("summary", "")).is_empty():
				errors.append("event_proposals[%d] summary empty" % i)

	# Quest ops
	var quests_v: Variant = envelope.get("quest_operations", null)
	if typeof(quests_v) != TYPE_ARRAY:
		errors.append("quest_operations must be array")
	else:
		var quests: Array = quests_v
		if quests.size() > 8:
			errors.append("quest_operations maxItems 8")
		for i in quests.size():
			if typeof(quests[i]) != TYPE_DICTIONARY:
				errors.append("quest_operations[%d] not object" % i)
				continue
			var q: Dictionary = quests[i]
			var op := str(q.get("op", ""))
			if op not in ALLOWED_QUEST_OPS:
				errors.append("bad quest op: %s" % op)
			if str(q.get("quest_id", "")).is_empty():
				errors.append("quest_operations[%d] quest_id empty" % i)
			if op == "offer":
				if str(q.get("title", "")).is_empty() or str(q.get("objective_summary", "")).is_empty():
					errors.append("quest offer requires title + objective_summary")

	# Deltas
	_validate_delta(envelope.get("mood_delta", null), "mood_delta", MOOD_DELTA_MIN, MOOD_DELTA_MAX, errors)
	_validate_delta(
		envelope.get("relationship_delta", null),
		"relationship_delta",
		REL_DELTA_MIN,
		REL_DELTA_MAX,
		errors
	)

	# next_trigger
	var nt_v: Variant = envelope.get("next_trigger", null)
	if typeof(nt_v) != TYPE_DICTIONARY:
		errors.append("next_trigger must be object")
	else:
		var nt: Dictionary = nt_v
		var kind := str(nt.get("kind", ""))
		if kind not in ALLOWED_TRIGGER_KINDS:
			errors.append("bad next_trigger.kind: %s" % kind)
		if kind == "timer" and not nt.has("timer_seconds"):
			errors.append("timer trigger requires timer_seconds")

	# trace
	var tr_v: Variant = envelope.get("trace", null)
	if typeof(tr_v) != TYPE_DICTIONARY:
		errors.append("trace must be object")
	else:
		var tr: Dictionary = tr_v
		if str(tr.get("trace_id", "")).is_empty():
			errors.append("trace.trace_id empty")
		if str(tr.get("model_receipt_ref", "")).is_empty():
			errors.append("trace.model_receipt_ref empty")
		# Never treat receipt as credential; reject obvious key-like values.
		var receipt := str(tr.get("model_receipt_ref", "")).to_lower()
		for bad in ["sk-", "api_key=", "bearer ", "password="]:
			if bad in receipt:
				errors.append("trace.model_receipt_ref looks like a secret")

	return {"ok": errors.is_empty(), "errors": errors}


## Project a validated envelope into structured Companion effects (no commit).
## Returns application result dict. Marks decision_id applied on success.
func project(
	envelope: Dictionary,
	builder: CompanionWorldPromptBuilder
) -> Dictionary:
	var check := validate(envelope)
	if not bool(check.get("ok", false)):
		return {
			"ok": false,
			"errors": check.get("errors", []),
			"decision_id": str(envelope.get("decision_id", "")),
			"dialogue_lines": [],
			"world_prompts": [],
			"quest_operations": [],
			"event_proposals": [],
			"mood_delta": 0.0,
			"relationship_delta": 0.0,
			"expression": "neutral",
			"next_trigger": {},
			"trace": {},
		}

	var dialogue: Dictionary = envelope.get("dialogue", {}) as Dictionary
	var lines_out: Array = []
	for line_v in dialogue.get("lines", []):
		if typeof(line_v) != TYPE_DICTIONARY:
			continue
		var line: Dictionary = line_v
		var entry := {
			"speaker": str(line.get("speaker", "companion")),
			"text": str(line.get("text", "")),
		}
		if line.has("npc_id"):
			entry["npc_id"] = str(line["npc_id"])
		lines_out.append(entry)

	var expression := str(dialogue.get("companion_expression", "neutral"))
	if expression.is_empty() or expression not in ALLOWED_EXPRESSIONS:
		expression = "neutral"

	var world_prompts: Array = []
	var builds: Array = envelope.get("build_proposals", []) as Array
	var model_receipt := ""
	var tr: Dictionary = envelope.get("trace", {}) as Dictionary
	if tr.has("model_receipt_ref"):
		model_receipt = str(tr["model_receipt_ref"])

	for bp_v in builds:
		if typeof(bp_v) != TYPE_DICTIONARY:
			continue
		var bp: Dictionary = bp_v
		if builder == null:
			continue
		var prompt := builder.build_from_agm_build_proposal(
			bp,
			{
				"session_id": str(envelope.get("session_id", "")),
				"decision_id": str(envelope.get("decision_id", "")),
				"model_receipt_ref": model_receipt,
				"source_snapshot_id": str(envelope.get("source_snapshot_id", "")),
			}
		)
		if not prompt.is_empty():
			world_prompts.append(prompt)

	var mood_d: Dictionary = envelope.get("mood_delta", {}) as Dictionary
	var rel_d: Dictionary = envelope.get("relationship_delta", {}) as Dictionary
	var mood_delta := float(mood_d.get("delta", 0.0))
	var rel_delta := float(rel_d.get("delta", 0.0))

	var quests: Array = []
	for q in envelope.get("quest_operations", []):
		if typeof(q) == TYPE_DICTIONARY:
			quests.append((q as Dictionary).duplicate(true))

	var events: Array = []
	for e in envelope.get("event_proposals", []):
		if typeof(e) == TYPE_DICTIONARY:
			events.append((e as Dictionary).duplicate(true))

	var next_trigger: Dictionary = {}
	if envelope.get("next_trigger") is Dictionary:
		next_trigger = (envelope["next_trigger"] as Dictionary).duplicate(true)

	var decision_id := str(envelope.get("decision_id", ""))
	var result := {
		"ok": true,
		"errors": PackedStringArray(),
		"decision_id": decision_id,
		"source_snapshot_id": str(envelope.get("source_snapshot_id", "")),
		"edition": str(envelope.get("edition", "")),
		"session_id": str(envelope.get("session_id", "")),
		"dialogue_lines": lines_out,
		"world_prompts": world_prompts,
		"quest_operations": quests,
		"event_proposals": events,
		"mood_delta": mood_delta,
		"relationship_delta": rel_delta,
		"mood_reason": str(mood_d.get("reason", "")),
		"relationship_reason": str(rel_d.get("reason", "")),
		"expression": expression,
		"next_trigger": next_trigger,
		"trace": tr.duplicate(true),
		"pacing_hint": (
			(envelope["pacing_hint"] as Dictionary).duplicate(true)
			if envelope.get("pacing_hint") is Dictionary
			else {}
		),
	}
	_applied[decision_id] = {
		"applied_at": Time.get_datetime_string_from_system(true, true),
		"world_prompt_count": world_prompts.size(),
		"dialogue_count": lines_out.size(),
	}
	return result


## Map AGM companion_expression → temporary emotional mood string.
static func expression_to_mood(expression: String) -> String:
	match expression:
		"warm":
			return "soft"
		"curious":
			return "focused"
		"playful":
			return "playful"
		"concerned":
			return "empathetic"
		"proud":
			return "happy"
		"tired":
			return "calm"
		_:
			return "calm"


func _validate_build_item(item: Variant, index: int, errors: PackedStringArray) -> void:
	if typeof(item) != TYPE_DICTIONARY:
		errors.append("build_proposals[%d] not object" % index)
		return
	var bp: Dictionary = item
	for req in [
		"proposal_id",
		"operation",
		"recipe_id",
		"entity_kind",
		"routes_through",
		"preview_required",
		"confirmation_state",
	]:
		if not bp.has(req):
			errors.append("build_proposals[%d] missing %s" % [index, req])
	if str(bp.get("routes_through", "")) != "preview_confirm_commit":
		errors.append("build_proposals[%d] routes_through must be preview_confirm_commit" % index)
	if bp.get("preview_required") != true:
		errors.append("build_proposals[%d] preview_required must be true" % index)
	if str(bp.get("confirmation_state", "")) != "pending":
		errors.append("build_proposals[%d] confirmation_state must be pending" % index)
	var op := str(bp.get("operation", ""))
	if op != "" and op not in ALLOWED_BUILD_OPS:
		errors.append("build_proposals[%d] bad operation" % index)
	var kind := str(bp.get("entity_kind", ""))
	if kind != "" and kind not in ALLOWED_ENTITY_KINDS:
		errors.append("build_proposals[%d] bad entity_kind" % index)
	if str(bp.get("recipe_id", "")).is_empty():
		errors.append("build_proposals[%d] recipe_id empty" % index)


func _validate_delta(
	raw: Variant,
	label: String,
	min_v: float,
	max_v: float,
	errors: PackedStringArray
) -> void:
	if typeof(raw) != TYPE_DICTIONARY:
		errors.append("%s must be object" % label)
		return
	var d: Dictionary = raw
	if not d.has("delta"):
		errors.append("%s.delta missing" % label)
		return
	var v := float(d["delta"])
	if v < min_v or v > max_v:
		errors.append("%s.delta out of bounds: %s" % [label, str(v)])
