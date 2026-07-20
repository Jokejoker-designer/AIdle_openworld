## G3 text-only onboarding presenter (W1 companion).
## Converts AGM Decision Envelopes into presentable dialogue / quest / mood state.
## Does NOT commit. Does NOT mutate durable world state. No TTS/STT/voice/mic.
## World Commit remains outside Companion; build proposals stay pending elsewhere.
class_name CompanionG3OnboardingPresenter
extends RefCounted

const PRESENTER_ID := "g3_onboarding_presenter"
const TEXT_ONLY := true

## Optional shared applier (validation + replay policy when bound).
var _applier: CompanionAgmDecisionApplier

## Session presentation board (soft UI state only — not world truth).
var _dialogue_lines: Array = []
var _quest_board: Dictionary = {} ## quest_id -> summary dict
var _quest_summaries: Array = []
var _mood_delta: float = 0.0
var _mood_reason: String = ""
var _relationship_delta: float = 0.0
var _expression: String = "neutral"
var _last_decision_id: String = ""
var _last_presentation: Dictionary = {}
var _event_notes: Array = []
var _next_trigger: Dictionary = {}


func _init(applier: CompanionAgmDecisionApplier = null) -> void:
	_applier = applier


func set_applier(applier: CompanionAgmDecisionApplier) -> void:
	_applier = applier


func get_applier() -> CompanionAgmDecisionApplier:
	return _applier


func set_live_snapshot_id(snapshot_id: String) -> void:
	if _applier != null:
		_applier.set_live_snapshot_id(snapshot_id)


func clear_presentation() -> void:
	_dialogue_lines.clear()
	_quest_board.clear()
	_quest_summaries.clear()
	_mood_delta = 0.0
	_mood_reason = ""
	_relationship_delta = 0.0
	_expression = "neutral"
	_last_decision_id = ""
	_last_presentation = {}
	_event_notes.clear()
	_next_trigger = {}


## Apply an AGM Decision Envelope into presentable text state.
## Returns { dialogue_lines, quest_summaries, mood_delta, ... }.
## Never commits. Never builds durable world mutations.
## When a shared applier is bound, validate() is used (replay/stale policy).
## Presentation does not call project() so it will not elevate build proposals
## or mark decision_id applied — companion_module.apply_agm_decision owns that.
func apply_decision(decision_dict: Dictionary) -> Dictionary:
	if decision_dict.is_empty():
		return _reject("decision empty", "")

	var decision_id := str(decision_dict.get("decision_id", ""))

	# Full policy validate when applier bound and decision not yet project()'d.
	# Already-applied decisions may re-present (idempotent UI) without replay fail.
	if _applier != null and not decision_id.is_empty() and not _applier.was_applied(decision_id):
		var check := _applier.validate(decision_dict)
		if not bool(check.get("ok", false)):
			var errs: PackedStringArray = check.get("errors", PackedStringArray()) as PackedStringArray
			var first := str(errs[0]) if errs.size() > 0 else "validation failed"
			return _reject(first, decision_id, errs)
	elif decision_id.is_empty():
		return _reject("decision_id empty", "")

	# Shape-level extract (trusted only after validate when applier bound).
	var dialogue_lines := _extract_dialogue_lines(decision_dict)
	var quest_ops: Array = []
	var quests_raw: Variant = decision_dict.get("quest_operations", [])
	if typeof(quests_raw) == TYPE_ARRAY:
		for q in quests_raw:
			if typeof(q) == TYPE_DICTIONARY:
				quest_ops.append(q)

	var quest_summaries := _apply_quest_operations(quest_ops)

	var mood_delta := 0.0
	var mood_reason := ""
	var mood_v: Variant = decision_dict.get("mood_delta", {})
	if typeof(mood_v) == TYPE_DICTIONARY:
		mood_delta = float((mood_v as Dictionary).get("delta", 0.0))
		mood_reason = str((mood_v as Dictionary).get("reason", ""))

	var rel_delta := 0.0
	var rel_v: Variant = decision_dict.get("relationship_delta", {})
	if typeof(rel_v) == TYPE_DICTIONARY:
		rel_delta = float((rel_v as Dictionary).get("delta", 0.0))

	var expression := "neutral"
	var dialogue_v: Variant = decision_dict.get("dialogue", {})
	if typeof(dialogue_v) == TYPE_DICTIONARY:
		expression = str((dialogue_v as Dictionary).get("companion_expression", "neutral"))
		if expression.is_empty():
			expression = "neutral"

	var events: Array = []
	var events_raw: Variant = decision_dict.get("event_proposals", [])
	if typeof(events_raw) == TYPE_ARRAY:
		for e in events_raw:
			if typeof(e) == TYPE_DICTIONARY:
				events.append((e as Dictionary).duplicate(true))

	var next_trigger: Dictionary = {}
	if decision_dict.get("next_trigger") is Dictionary:
		next_trigger = (decision_dict["next_trigger"] as Dictionary).duplicate(true)

	_dialogue_lines = dialogue_lines
	_quest_summaries = quest_summaries
	_mood_delta = mood_delta
	_mood_reason = mood_reason
	_relationship_delta = rel_delta
	_expression = expression
	_last_decision_id = decision_id
	_event_notes = events
	_next_trigger = next_trigger

	var presentation := {
		"ok": true,
		"errors": PackedStringArray(),
		"presenter_id": PRESENTER_ID,
		"text_only": true,
		"committed": false,
		"durable_mutation": false,
		"decision_id": decision_id,
		"source_snapshot_id": str(decision_dict.get("source_snapshot_id", "")),
		"session_id": str(decision_dict.get("session_id", "")),
		"edition": str(decision_dict.get("edition", "")),
		"dialogue_lines": dialogue_lines.duplicate(true),
		"quest_summaries": quest_summaries.duplicate(true),
		"mood_delta": mood_delta,
		"mood_reason": mood_reason,
		"relationship_delta": rel_delta,
		"expression": expression,
		"emotional_mood": CompanionAgmDecisionApplier.expression_to_mood(expression),
		"event_notes": events.duplicate(true),
		"next_trigger": next_trigger.duplicate(true),
		"onboarding_quest_id": _primary_onboarding_quest_id(quest_summaries),
		"status_banner": _build_status_banner(dialogue_lines, quest_summaries),
	}
	_last_presentation = presentation.duplicate(true)
	return presentation.duplicate(true)


## Format presentation from an already-projected AGM result (no re-validate).
## Used after CompanionModule.apply_agm_decision so replay mark is already set.
func format_from_projected(projected: Dictionary) -> Dictionary:
	if projected.is_empty() or not bool(projected.get("ok", false)):
		var errs: PackedStringArray = projected.get("errors", PackedStringArray()) as PackedStringArray
		var did := str(projected.get("decision_id", ""))
		return _reject(
			str(errs[0]) if errs.size() > 0 else "projected not ok",
			did,
			errs
		)

	var dialogue_lines: Array = []
	for line_v in projected.get("dialogue_lines", []):
		if typeof(line_v) == TYPE_DICTIONARY:
			dialogue_lines.append((line_v as Dictionary).duplicate(true))

	var quest_ops: Array = []
	for q in projected.get("quest_operations", []):
		if typeof(q) == TYPE_DICTIONARY:
			quest_ops.append(q)
	var quest_summaries := _apply_quest_operations(quest_ops)

	var mood_delta := float(projected.get("mood_delta", 0.0))
	var mood_reason := str(projected.get("mood_reason", ""))
	var rel_delta := float(projected.get("relationship_delta", 0.0))
	var expression := str(projected.get("expression", "neutral"))
	if expression.is_empty():
		expression = "neutral"

	var events: Array = []
	for e in projected.get("event_proposals", []):
		if typeof(e) == TYPE_DICTIONARY:
			events.append((e as Dictionary).duplicate(true))

	var next_trigger: Dictionary = {}
	if projected.get("next_trigger") is Dictionary:
		next_trigger = (projected["next_trigger"] as Dictionary).duplicate(true)

	var decision_id := str(projected.get("decision_id", ""))

	_dialogue_lines = dialogue_lines
	_quest_summaries = quest_summaries
	_mood_delta = mood_delta
	_mood_reason = mood_reason
	_relationship_delta = rel_delta
	_expression = expression
	_last_decision_id = decision_id
	_event_notes = events
	_next_trigger = next_trigger

	var presentation := {
		"ok": true,
		"errors": PackedStringArray(),
		"presenter_id": PRESENTER_ID,
		"text_only": true,
		"committed": false,
		"durable_mutation": false,
		"decision_id": decision_id,
		"source_snapshot_id": str(projected.get("source_snapshot_id", "")),
		"session_id": str(projected.get("session_id", "")),
		"edition": str(projected.get("edition", "")),
		"dialogue_lines": dialogue_lines.duplicate(true),
		"quest_summaries": quest_summaries.duplicate(true),
		"mood_delta": mood_delta,
		"mood_reason": mood_reason,
		"relationship_delta": rel_delta,
		"expression": expression,
		"emotional_mood": CompanionAgmDecisionApplier.expression_to_mood(expression),
		"event_notes": events.duplicate(true),
		"next_trigger": next_trigger.duplicate(true),
		"onboarding_quest_id": _primary_onboarding_quest_id(quest_summaries),
		"status_banner": _build_status_banner(dialogue_lines, quest_summaries),
		"from_projected": true,
	}
	_last_presentation = presentation.duplicate(true)
	return presentation.duplicate(true)


func get_last_presentation() -> Dictionary:
	return _last_presentation.duplicate(true)


func get_dialogue_lines() -> Array:
	return _dialogue_lines.duplicate(true)


func get_quest_summaries() -> Array:
	return _quest_summaries.duplicate(true)


func get_mood_delta() -> float:
	return _mood_delta


func get_expression() -> String:
	return _expression


func get_quest_board() -> Dictionary:
	return _quest_board.duplicate(true)


## Plain-language multi-line dump for text HUD / smoke / /onboarding command.
func inspect_presentation_text() -> String:
	var lines: PackedStringArray = []
	lines.append("G3 Onboarding Presenter (text-only, no commit)")
	lines.append("decision_id=%s expression=%s mood_delta=%s" % [
		_last_decision_id if not _last_decision_id.is_empty() else "(none)",
		_expression,
		str(_mood_delta),
	])
	if _dialogue_lines.is_empty():
		lines.append("Dialogue: (none)")
	else:
		lines.append("Dialogue:")
		for line_v in _dialogue_lines:
			if typeof(line_v) != TYPE_DICTIONARY:
				continue
			var line: Dictionary = line_v
			lines.append("  [%s] %s" % [str(line.get("speaker", "?")), str(line.get("text", ""))])
	if _quest_summaries.is_empty():
		lines.append("Quests: (none)")
	else:
		lines.append("Quests:")
		for qs in _quest_summaries:
			if typeof(qs) != TYPE_DICTIONARY:
				continue
			var q: Dictionary = qs
			lines.append(
				"  - %s [%s] %s" % [
					str(q.get("quest_id", "")),
					str(q.get("display_status", "")),
					str(q.get("status_text", "")),
				]
			)
	lines.append("committed=false durable_mutation=false")
	return "\n".join(lines)


# ─── Internals ───────────────────────────────────────────────────────────────

func _extract_dialogue_lines(decision_dict: Dictionary) -> Array:
	var out: Array = []
	var dialogue_v: Variant = decision_dict.get("dialogue", null)
	if typeof(dialogue_v) != TYPE_DICTIONARY:
		return out
	var dialogue: Dictionary = dialogue_v
	var lines_v: Variant = dialogue.get("lines", [])
	if typeof(lines_v) != TYPE_ARRAY:
		return out
	for line_v in lines_v:
		if typeof(line_v) != TYPE_DICTIONARY:
			continue
		var line: Dictionary = line_v
		var entry := {
			"speaker": str(line.get("speaker", "companion")),
			"text": str(line.get("text", "")),
		}
		if line.has("npc_id"):
			entry["npc_id"] = str(line["npc_id"])
		if str(entry["text"]).is_empty():
			continue
		out.append(entry)
	return out


func _apply_quest_operations(quest_ops: Array) -> Array:
	## Fold ops into board; return ordered board values as quest_summaries.
	for q_v in quest_ops:
		if typeof(q_v) != TYPE_DICTIONARY:
			continue
		var q: Dictionary = q_v
		var summary := CompanionAgmDecisionApplier.summarize_quest_operation(q)
		var qid := str(summary.get("quest_id", ""))
		if qid.is_empty():
			continue
		var prior: Dictionary = {}
		if _quest_board.has(qid) and typeof(_quest_board[qid]) == TYPE_DICTIONARY:
			prior = _quest_board[qid] as Dictionary
		# Preserve title/objective when later ops omit them.
		if str(summary.get("title", "")).is_empty() and prior.has("title"):
			summary["title"] = prior["title"]
		if str(summary.get("objective_summary", "")).is_empty() and prior.has("objective_summary"):
			summary["objective_summary"] = prior["objective_summary"]
		# Rebuild status_text if we filled title/objective from prior.
		summary["status_text"] = CompanionAgmDecisionApplier.quest_status_text(summary)
		_quest_board[qid] = summary

	var ordered: Array = []
	# Prefer ops order, then remaining board keys.
	var seen: Dictionary = {}
	for q_v in quest_ops:
		if typeof(q_v) != TYPE_DICTIONARY:
			continue
		var qid2 := str((q_v as Dictionary).get("quest_id", ""))
		if qid2.is_empty() or seen.has(qid2):
			continue
		seen[qid2] = true
		if _quest_board.has(qid2):
			ordered.append((_quest_board[qid2] as Dictionary).duplicate(true))
	for k in _quest_board.keys():
		var qid3 := str(k)
		if seen.has(qid3):
			continue
		ordered.append((_quest_board[qid3] as Dictionary).duplicate(true))
	return ordered


func _primary_onboarding_quest_id(summaries: Array) -> String:
	for s in summaries:
		if typeof(s) != TYPE_DICTIONARY:
			continue
		var qid := str((s as Dictionary).get("quest_id", ""))
		if qid.begins_with("onboarding") or qid == "onboarding_first_home":
			return qid
	if summaries.size() > 0 and typeof(summaries[0]) == TYPE_DICTIONARY:
		return str((summaries[0] as Dictionary).get("quest_id", ""))
	return ""


func _build_status_banner(dialogue_lines: Array, quest_summaries: Array) -> String:
	var parts: PackedStringArray = []
	if dialogue_lines.size() > 0 and typeof(dialogue_lines[0]) == TYPE_DICTIONARY:
		var t := str((dialogue_lines[0] as Dictionary).get("text", ""))
		if not t.is_empty():
			parts.append(t)
	if quest_summaries.size() > 0 and typeof(quest_summaries[0]) == TYPE_DICTIONARY:
		var st := str((quest_summaries[0] as Dictionary).get("status_text", ""))
		if not st.is_empty():
			parts.append(st)
	if parts.is_empty():
		return "Onboarding idle (text-only)."
	return " | ".join(parts)


func _reject(reason: String, decision_id: String, errors: PackedStringArray = PackedStringArray()) -> Dictionary:
	var errs := errors
	if errs.is_empty():
		errs = PackedStringArray([reason])
	return {
		"ok": false,
		"errors": errs,
		"presenter_id": PRESENTER_ID,
		"text_only": true,
		"committed": false,
		"durable_mutation": false,
		"decision_id": decision_id,
		"dialogue_lines": [],
		"quest_summaries": [],
		"mood_delta": 0.0,
		"mood_reason": "",
		"relationship_delta": 0.0,
		"expression": "neutral",
		"emotional_mood": "calm",
		"event_notes": [],
		"next_trigger": {},
		"onboarding_quest_id": "",
		"status_banner": "Onboarding rejected: %s" % reason,
	}
