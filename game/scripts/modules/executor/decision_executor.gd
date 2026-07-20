## Deterministic AGM Decision Envelope executor (G2-006).
## Allowlisted soft effects only; builds become pending World Prompts that must
## route through preview → confirm → World Commit (never direct durable mutation).
## decision_id is the idempotency key: replay returns prior receipt, no re-apply.
## Pure RefCounted logic — no SceneTree durable writes.
class_name AgmDecisionExecutor
extends RefCounted

const SCHEMA_VERSION := "1.0.0"
const RECEIPT_SCHEMA_VERSION := "1.0.0"

## Top-level Decision Envelope fields (schema additionalProperties:false mirror).
const ALLOWED_DECISION_KEYS := [
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
	"pacing_hint",
	"trace",
]

## Forbidden payload names (schema propertyNames banlist subset + durable bypasses).
const FORBIDDEN_KEYS := [
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

const ALLOWED_QUEST_OPS := [
	"offer",
	"update_objective",
	"mark_ready",
	"complete",
	"fail",
	"cancel",
]

const ALLOWED_EVENT_TYPES := [
	"pacing.slow_down",
	"pacing.speed_up",
	"ambient.weather_hint",
	"ambient.time_of_day_hint",
	"narrative.beat",
	"companion.attention",
	"quest.hint",
	"onboarding.nudge",
]

const ALLOWED_BUILD_OPS := ["create", "modify", "delete", "enrich", "gift_proposal"]

const ALLOWED_ENTITY_KINDS := [
	"tile_layer",
	"terrain_patch_2_5d",
	"modular_structure_2_5d",
	"prop_2_5d",
	"character_2_5d",
	"vehicle_2_5d",
]

const ALLOWED_SPEAKERS := ["companion", "narrator", "npc"]
const ALLOWED_EDITIONS := ["desktop_bridge_free", "api_paid"]

const MOOD_DELTA_MIN := -0.1
const MOOD_DELTA_MAX := 0.1
const RELATIONSHIP_DELTA_MIN := -0.05
const RELATIONSHIP_DELTA_MAX := 0.05

## Recipe defaults used when elevating a build_proposal → world_prompt.
const RECIPE_DEFAULTS := {
	"cozy_house_small": {
		"kind": "modular_structure_2_5d",
		"bounds": {"width": 8.0, "depth": 6.0, "height": 5.0},
		"interaction_tags": ["enterable", "lightable"],
		"max_compute_units": 200,
		"max_entities": 32,
		"presentation_duration_seconds": 12.0,
	},
	"garden_lamp": {
		"kind": "prop_2_5d",
		"bounds": {"width": 1.0, "depth": 1.0, "height": 2.0},
		"interaction_tags": ["lightable", "pickable"],
		"max_compute_units": 40,
		"max_entities": 4,
		"presentation_duration_seconds": 6.0,
	},
	"tile_layer_floor": {
		"kind": "tile_layer",
		"bounds": {"width": 4.0, "depth": 4.0, "height": 0.25},
		"interaction_tags": ["walkable"],
		"max_compute_units": 60,
		"max_entities": 8,
		"presentation_duration_seconds": 8.0,
	},
}

## decision_id -> original execution receipt (idempotency store).
var _seen: Dictionary = {}
## Local soft state applied by decisions (not durable world truth).
var _soft_quests: Dictionary = {}
var _soft_events: Array = []
var _mood: float = 0.5
var _relationship: float = 0.5
var _dialogue_log: Array = []
var _player_id: String = "player_01"
var _companion_id: String = "companion_lumi"
var _space_type: String = "private_reality"
var _space_id: String = "home_01"
var _chunk_id: String = "0_0"
var _world_revision: int = 0
var _style_profile_id: String = "cozy_default"
var _style_profile_version: String = "1.0.0"
var _base_concept: String = "cozy_cyber_pixel_2_5d"


func configure_context(ctx: Dictionary) -> void:
	if ctx.has("player_id"):
		_player_id = str(ctx["player_id"])
	if ctx.has("companion_id"):
		_companion_id = str(ctx["companion_id"])
	if ctx.has("space_type"):
		_space_type = str(ctx["space_type"])
	if ctx.has("space_id"):
		_space_id = str(ctx["space_id"])
	if ctx.has("chunk_id"):
		_chunk_id = str(ctx["chunk_id"])
	if ctx.has("expected_world_revision"):
		_world_revision = maxi(0, int(ctx["expected_world_revision"]))
	if ctx.has("world_revision"):
		_world_revision = maxi(0, int(ctx["world_revision"]))
	if ctx.has("style_profile_id"):
		_style_profile_id = str(ctx["style_profile_id"])
	if ctx.has("base_concept"):
		_base_concept = str(ctx["base_concept"])
	if ctx.has("mood"):
		_mood = clampf(float(ctx["mood"]), 0.0, 1.0)
	if ctx.has("relationship"):
		_relationship = clampf(float(ctx["relationship"]), 0.0, 1.0)


func has_seen_decision(decision_id: String) -> bool:
	return _seen.has(decision_id)


func get_receipt(decision_id: String) -> Dictionary:
	if not _seen.has(decision_id):
		return {}
	return (_seen[decision_id] as Dictionary).duplicate(true)


func list_seen_decision_ids() -> PackedStringArray:
	return PackedStringArray(_seen.keys())


func get_soft_state() -> Dictionary:
	return {
		"mood": _mood,
		"relationship": _relationship,
		"quests": _soft_quests.duplicate(true),
		"events": _soft_events.duplicate(true),
		"dialogue_log": _dialogue_log.duplicate(true),
	}


static func list_allowlisted_event_types() -> PackedStringArray:
	return PackedStringArray(ALLOWED_EVENT_TYPES)


static func list_allowlisted_quest_ops() -> PackedStringArray:
	return PackedStringArray(ALLOWED_QUEST_OPS)


## Execute a Decision Envelope against the live snapshot.
## Returns an execution receipt suitable for the next World State Snapshot.
func execute(decision: Dictionary, live_snapshot: Dictionary = {}) -> Dictionary:
	if decision.is_empty():
		return _reject_receipt("", "", "schema_invalid", "empty decision envelope")

	# Forbidden keys / unknown top-level fields (untrusted AGM input).
	var key_issue := _check_keys(decision)
	if not key_issue.is_empty():
		return _reject_receipt(
			str(decision.get("decision_id", "")),
			str(decision.get("source_snapshot_id", "")),
			"forbidden_or_unknown_field",
			key_issue
		)

	var decision_id := str(decision.get("decision_id", "")).strip_edges()
	if decision_id.is_empty():
		return _reject_receipt("", str(decision.get("source_snapshot_id", "")), "schema_invalid", "missing decision_id")

	# Idempotency: replay returns prior receipt without re-applying effects.
	if _seen.has(decision_id):
		return _replay_receipt(decision_id)

	var source_snapshot_id := str(decision.get("source_snapshot_id", "")).strip_edges()
	if source_snapshot_id.is_empty():
		return _store_reject(decision_id, "", "schema_invalid", "missing source_snapshot_id")

	# Stale snapshot policy.
	if not live_snapshot.is_empty():
		var live_id := str(live_snapshot.get("snapshot_id", "")).strip_edges()
		if live_id.is_empty():
			return _store_reject(decision_id, source_snapshot_id, "stale_snapshot", "live snapshot missing snapshot_id")
		if live_id != source_snapshot_id:
			var stale := _make_receipt_base(decision_id, source_snapshot_id, "stale_snapshot")
			stale["notes"] = "source_snapshot_id does not match live snapshot_id"
			stale["rejection"] = {
				"code": "stale_snapshot",
				"reason": "source=%s live=%s" % [source_snapshot_id, live_id],
			}
			stale["live_snapshot_id"] = live_id
			_seen[decision_id] = stale.duplicate(true)
			return stale.duplicate(true)
		# Pull context from live snapshot when present.
		_hydrate_from_snapshot(live_snapshot)

	# Required field presence (lightweight; full schema is G1-003 contracts).
	var required_issue := _check_required(decision)
	if not required_issue.is_empty():
		return _store_reject(decision_id, source_snapshot_id, "schema_invalid", required_issue)

	if str(decision.get("schema_version", "")) != SCHEMA_VERSION:
		return _store_reject(decision_id, source_snapshot_id, "schema_invalid", "schema_version must be 1.0.0")

	var edition := str(decision.get("edition", ""))
	if edition not in ALLOWED_EDITIONS:
		return _store_reject(decision_id, source_snapshot_id, "unknown_action", "unknown edition: %s" % edition)

	# ── Apply allowlisted actions ────────────────────────────────────────────
	var actions_applied: Array = []
	var actions_rejected: Array = []
	var dialogue_delivered: Array = []
	var quest_ops_applied: Array = []
	var events_applied: Array = []
	var build_handoffs: Array = []

	# Dialogue (soft → companion / UI).
	var dialogue_result := _apply_dialogue(decision.get("dialogue", {}))
	if bool(dialogue_result.get("ok", false)):
		dialogue_delivered = dialogue_result.get("lines", []) as Array
		if not dialogue_delivered.is_empty():
			actions_applied.append("dialogue")
	else:
		actions_rejected.append({"action": "dialogue", "reason": str(dialogue_result.get("reason", ""))})

	# Quest operations (soft UI state only).
	var quests_raw: Variant = decision.get("quest_operations", [])
	if typeof(quests_raw) == TYPE_ARRAY:
		for q in quests_raw:
			if typeof(q) != TYPE_DICTIONARY:
				actions_rejected.append({"action": "quest_operation", "reason": "not an object"})
				continue
			var qres := _apply_quest_op(q as Dictionary)
			if bool(qres.get("ok", false)):
				quest_ops_applied.append(qres.get("applied", {}))
				actions_applied.append("quest:%s" % str((q as Dictionary).get("op", "")))
			else:
				actions_rejected.append({
					"action": "quest_operation",
					"reason": str(qres.get("reason", "")),
					"op": str((q as Dictionary).get("op", "")),
				})
	else:
		actions_rejected.append({"action": "quest_operations", "reason": "must be array"})

	# Event proposals (allowlist only; soft narrative/pacing).
	var events_raw: Variant = decision.get("event_proposals", [])
	if typeof(events_raw) == TYPE_ARRAY:
		for e in events_raw:
			if typeof(e) != TYPE_DICTIONARY:
				actions_rejected.append({"action": "event_proposal", "reason": "not an object"})
				continue
			var eres := _apply_event(e as Dictionary)
			if bool(eres.get("ok", false)):
				events_applied.append(eres.get("applied", {}))
				actions_applied.append("event:%s" % str((e as Dictionary).get("event_type", "")))
			else:
				actions_rejected.append({
					"action": "event_proposal",
					"reason": str(eres.get("reason", "")),
					"event_type": str((e as Dictionary).get("event_type", "")),
				})
	else:
		actions_rejected.append({"action": "event_proposals", "reason": "must be array"})

	# Mood / relationship (capped soft deltas).
	var mood_applied := 0.0
	var rel_applied := 0.0
	var mood_res := _apply_mood_delta(decision.get("mood_delta", {}))
	if bool(mood_res.get("ok", false)):
		mood_applied = float(mood_res.get("applied", 0.0))
		if not is_zero_approx(mood_applied):
			actions_applied.append("mood_delta")
	else:
		actions_rejected.append({"action": "mood_delta", "reason": str(mood_res.get("reason", ""))})

	var rel_res := _apply_relationship_delta(decision.get("relationship_delta", {}))
	if bool(rel_res.get("ok", false)):
		rel_applied = float(rel_res.get("applied", 0.0))
		if not is_zero_approx(rel_applied):
			actions_applied.append("relationship_delta")
	else:
		actions_rejected.append({"action": "relationship_delta", "reason": str(rel_res.get("reason", ""))})

	# Build proposals → world_prompt handoffs (preview_confirm_commit only).
	var builds_raw: Variant = decision.get("build_proposals", [])
	if typeof(builds_raw) == TYPE_ARRAY:
		for b in builds_raw:
			if typeof(b) != TYPE_DICTIONARY:
				actions_rejected.append({"action": "build_proposal", "reason": "not an object"})
				continue
			var bres := _elevate_build_proposal(b as Dictionary, decision)
			if bool(bres.get("ok", false)):
				build_handoffs.append(bres.get("handoff", {}))
				actions_applied.append("build_preview:%s" % str((b as Dictionary).get("proposal_id", "")))
			else:
				actions_rejected.append({
					"action": "build_proposal",
					"reason": str(bres.get("reason", "")),
					"proposal_id": str((b as Dictionary).get("proposal_id", "")),
				})
	else:
		actions_rejected.append({"action": "build_proposals", "reason": "must be array"})

	# Unknown / unsupported action surface: reject if any hard failures on builds with no soft success.
	# Hard reject when every action failed and there was work to do, or unknown quest/event.
	var hard_unknown := false
	for rej in actions_rejected:
		if typeof(rej) != TYPE_DICTIONARY:
			continue
		var reason := str((rej as Dictionary).get("reason", ""))
		if reason.begins_with("unknown_") or reason.begins_with("forbidden_"):
			hard_unknown = true

	var status := "applied"
	if hard_unknown and actions_applied.is_empty():
		status = "rejected"
	elif not build_handoffs.is_empty():
		status = "awaiting_player"
	elif not actions_rejected.is_empty() and not actions_applied.is_empty():
		status = "partial"
	elif not actions_rejected.is_empty() and actions_applied.is_empty():
		# Empty dialogue/quests/builds with only zero deltas still counts as applied soft no-op.
		var has_work := (
			not dialogue_delivered.is_empty()
			or not quest_ops_applied.is_empty()
			or not events_applied.is_empty()
			or not build_handoffs.is_empty()
			or not is_zero_approx(mood_applied)
			or not is_zero_approx(rel_applied)
		)
		if has_work or hard_unknown:
			status = "rejected"
		else:
			status = "applied"

	# Zero-work valid decision (empty arrays, zero deltas) is a successful no-op apply.
	if (
		actions_applied.is_empty()
		and actions_rejected.is_empty()
		and dialogue_delivered.is_empty()
		and quest_ops_applied.is_empty()
		and events_applied.is_empty()
		and build_handoffs.is_empty()
	):
		status = "applied"

	var receipt := _make_receipt_base(decision_id, source_snapshot_id, status)
	receipt["session_id"] = str(decision.get("session_id", ""))
	receipt["edition"] = edition
	receipt["notes"] = _status_notes(status, build_handoffs.size(), actions_rejected.size())
	receipt["actions_applied"] = actions_applied
	receipt["actions_rejected"] = actions_rejected
	receipt["dialogue_delivered"] = dialogue_delivered
	receipt["quest_ops_applied"] = quest_ops_applied
	receipt["event_proposals_applied"] = events_applied
	receipt["build_handoffs"] = build_handoffs
	receipt["mood_delta_applied"] = mood_applied
	receipt["relationship_delta_applied"] = rel_applied
	receipt["mood_after"] = _mood
	receipt["relationship_after"] = _relationship
	receipt["next_trigger"] = (decision.get("next_trigger", {"kind": "none"}) as Dictionary).duplicate(true)
	if decision.has("pacing_hint") and decision["pacing_hint"] is Dictionary:
		receipt["pacing_hint"] = (decision["pacing_hint"] as Dictionary).duplicate(true)
	if decision.has("trace") and decision["trace"] is Dictionary:
		receipt["trace"] = (decision["trace"] as Dictionary).duplicate(true)
	if status == "rejected":
		receipt["rejection"] = {
			"code": "unknown_action" if hard_unknown else "policy",
			"reason": receipt["notes"],
		}

	_seen[decision_id] = receipt.duplicate(true)
	return receipt.duplicate(true)


## Snapshot-compatible last_execution_receipt projection.
func to_snapshot_receipt(full_receipt: Dictionary) -> Dictionary:
	if full_receipt.is_empty():
		return {"decision_id": null, "status": "none"}
	var out := {
		"decision_id": full_receipt.get("decision_id", null),
		"status": str(full_receipt.get("status", "none")),
	}
	if full_receipt.has("executed_at"):
		out["executed_at"] = full_receipt["executed_at"]
	if full_receipt.has("notes"):
		out["notes"] = str(full_receipt["notes"]).substr(0, 256)
	return out


# ─── Internals ───────────────────────────────────────────────────────────────

func _hydrate_from_snapshot(snap: Dictionary) -> void:
	if snap.has("world_revision"):
		_world_revision = maxi(0, int(snap["world_revision"]))
	if snap.has("space_id"):
		_space_id = str(snap["space_id"])
	var player: Variant = snap.get("player", {})
	if player is Dictionary:
		if (player as Dictionary).has("player_id"):
			_player_id = str((player as Dictionary)["player_id"])
		var loc: Variant = (player as Dictionary).get("location", {})
		if loc is Dictionary and (loc as Dictionary).has("chunk_id"):
			_chunk_id = str((loc as Dictionary)["chunk_id"])
	var companion: Variant = snap.get("companion", {})
	if companion is Dictionary:
		if (companion as Dictionary).has("companion_id"):
			_companion_id = str((companion as Dictionary)["companion_id"])
		if (companion as Dictionary).has("mood"):
			_mood = clampf(float((companion as Dictionary)["mood"]), 0.0, 1.0)
		if (companion as Dictionary).has("relationship"):
			_relationship = clampf(float((companion as Dictionary)["relationship"]), 0.0, 1.0)
	var world: Variant = snap.get("world", {})
	if world is Dictionary and (world as Dictionary).has("space_type"):
		_space_type = str((world as Dictionary)["space_type"])
	var art: Variant = snap.get("art_style", {})
	if art is Dictionary:
		if (art as Dictionary).has("profile_id"):
			_style_profile_id = str((art as Dictionary)["profile_id"])
		if (art as Dictionary).has("base_concept"):
			_base_concept = str((art as Dictionary)["base_concept"])


func _check_keys(decision: Dictionary) -> String:
	for k in decision.keys():
		var key := str(k)
		if key in FORBIDDEN_KEYS:
			return "forbidden field: %s" % key
		if key not in ALLOWED_DECISION_KEYS:
			return "unknown field: %s" % key
	return ""


func _check_required(decision: Dictionary) -> String:
	for req in [
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
	]:
		if not decision.has(req):
			return "missing required field: %s" % req
	return ""


func _apply_dialogue(dialogue: Variant) -> Dictionary:
	if typeof(dialogue) != TYPE_DICTIONARY:
		return {"ok": false, "reason": "dialogue must be object"}
	var d: Dictionary = dialogue
	var lines_raw: Variant = d.get("lines", [])
	if typeof(lines_raw) != TYPE_ARRAY:
		return {"ok": false, "reason": "dialogue.lines must be array"}
	var out: Array = []
	for line in lines_raw:
		if typeof(line) != TYPE_DICTIONARY:
			return {"ok": false, "reason": "unknown_action: dialogue line not object"}
		var L: Dictionary = line
		var speaker := str(L.get("speaker", ""))
		if speaker not in ALLOWED_SPEAKERS:
			return {"ok": false, "reason": "unknown_action: speaker %s" % speaker}
		var text := str(L.get("text", "")).strip_edges()
		if text.is_empty():
			return {"ok": false, "reason": "dialogue text empty"}
		if text.length() > 480:
			text = text.substr(0, 480)
		var entry := {"speaker": speaker, "text": text}
		if speaker == "npc":
			var npc_id := str(L.get("npc_id", "")).strip_edges()
			if npc_id.is_empty():
				return {"ok": false, "reason": "npc line missing npc_id"}
			entry["npc_id"] = npc_id
		out.append(entry)
		_dialogue_log.append(entry.duplicate(true))
	if d.has("companion_expression"):
		# Expression is advisory soft metadata only (text-only MVP; no TTS).
		pass
	return {"ok": true, "lines": out}


func _apply_quest_op(op: Dictionary) -> Dictionary:
	var op_name := str(op.get("op", ""))
	if op_name not in ALLOWED_QUEST_OPS:
		return {"ok": false, "reason": "unknown_action: quest op %s" % op_name}
	var quest_id := str(op.get("quest_id", "")).strip_edges()
	if quest_id.is_empty():
		return {"ok": false, "reason": "quest_id required"}
	if op_name == "offer":
		if str(op.get("title", "")).is_empty() or str(op.get("objective_summary", "")).is_empty():
			return {"ok": false, "reason": "offer requires title and objective_summary"}
	var record := {
		"op": op_name,
		"quest_id": quest_id,
		"title": str(op.get("title", "")),
		"objective_summary": str(op.get("objective_summary", "")),
		"reason": str(op.get("reason", "")),
		"applied_at": _now_iso(),
	}
	_soft_quests[quest_id] = record.duplicate(true)
	return {"ok": true, "applied": record}


func _apply_event(ev: Dictionary) -> Dictionary:
	var et := str(ev.get("event_type", ""))
	if et not in ALLOWED_EVENT_TYPES:
		return {"ok": false, "reason": "unknown_action: event_type %s" % et}
	var summary := str(ev.get("summary", "")).strip_edges()
	if summary.is_empty():
		return {"ok": false, "reason": "event summary required"}
	var intensity := clampf(float(ev.get("intensity", 0.5)), 0.0, 1.0)
	var record := {
		"event_type": et,
		"summary": summary.substr(0, 256),
		"intensity": intensity,
		"applied_at": _now_iso(),
	}
	_soft_events.append(record.duplicate(true))
	return {"ok": true, "applied": record}


func _apply_mood_delta(md: Variant) -> Dictionary:
	if typeof(md) != TYPE_DICTIONARY:
		return {"ok": false, "reason": "mood_delta must be object"}
	if not (md as Dictionary).has("delta"):
		return {"ok": false, "reason": "mood_delta.delta required"}
	var delta := float((md as Dictionary)["delta"])
	if delta < MOOD_DELTA_MIN - 0.000001 or delta > MOOD_DELTA_MAX + 0.000001:
		return {"ok": false, "reason": "forbidden_excessive_mood_delta: %s" % delta}
	_mood = clampf(_mood + delta, 0.0, 1.0)
	return {"ok": true, "applied": delta}


func _apply_relationship_delta(rd: Variant) -> Dictionary:
	if typeof(rd) != TYPE_DICTIONARY:
		return {"ok": false, "reason": "relationship_delta must be object"}
	if not (rd as Dictionary).has("delta"):
		return {"ok": false, "reason": "relationship_delta.delta required"}
	var delta := float((rd as Dictionary)["delta"])
	if delta < RELATIONSHIP_DELTA_MIN - 0.000001 or delta > RELATIONSHIP_DELTA_MAX + 0.000001:
		return {"ok": false, "reason": "forbidden_excessive_relationship_delta: %s" % delta}
	_relationship = clampf(_relationship + delta, 0.0, 1.0)
	return {"ok": true, "applied": delta}


func _elevate_build_proposal(bp: Dictionary, decision: Dictionary) -> Dictionary:
	# Hard invariants — builds never skip preview/confirm/commit.
	var routes := str(bp.get("routes_through", ""))
	if routes != "preview_confirm_commit":
		return {"ok": false, "reason": "forbidden_build_bypass: routes_through must be preview_confirm_commit"}
	if bp.get("preview_required") != true:
		return {"ok": false, "reason": "forbidden_build_bypass: preview_required must be true"}
	if str(bp.get("confirmation_state", "")) != "pending":
		return {"ok": false, "reason": "forbidden_build_bypass: confirmation_state must be pending"}

	var operation := str(bp.get("operation", ""))
	if operation not in ALLOWED_BUILD_OPS:
		return {"ok": false, "reason": "unknown_action: build operation %s" % operation}

	var entity_kind := str(bp.get("entity_kind", ""))
	if entity_kind not in ALLOWED_ENTITY_KINDS:
		return {"ok": false, "reason": "unknown_action: entity_kind %s" % entity_kind}

	var recipe_id := str(bp.get("recipe_id", "")).strip_edges()
	if recipe_id.is_empty():
		return {"ok": false, "reason": "recipe_id required"}

	var proposal_id := str(bp.get("proposal_id", "")).strip_edges()
	if proposal_id.is_empty():
		proposal_id = _new_uuid()

	var world_prompt := build_world_prompt_from_proposal(bp, decision)
	if world_prompt.is_empty():
		return {"ok": false, "reason": "failed to construct world_prompt"}

	# Force invariants on constructed prompt (defense in depth).
	var conf: Dictionary = world_prompt.get("confirmation", {}) as Dictionary
	conf["preview_required"] = true
	conf["state"] = "pending"
	conf.erase("confirmed_by")
	world_prompt["confirmation"] = conf

	var handoff := {
		"proposal_id": proposal_id,
		"prompt_id": str(world_prompt.get("prompt_id", "")),
		"request_id": str(world_prompt.get("request_id", "")),
		"recipe_id": recipe_id,
		"entity_kind": entity_kind,
		"operation": operation,
		"routes_through": "preview_confirm_commit",
		"preview_required": true,
		"confirmation_state": "pending",
		"pipeline_stage": "preview",
		"world_prompt": world_prompt,
		"commit_request": null,
		"commit_receipt": null,
		"durable_mutation_applied": false,
	}
	return {"ok": true, "handoff": handoff}


## Construct a schema-shaped Structured World Prompt from an AGM build proposal.
func build_world_prompt_from_proposal(bp: Dictionary, decision: Dictionary = {}) -> Dictionary:
	var recipe_id := str(bp.get("recipe_id", "")).strip_edges()
	var entity_kind := str(bp.get("entity_kind", "modular_structure_2_5d"))
	var operation := str(bp.get("operation", "create"))
	var defaults: Dictionary = RECIPE_DEFAULTS.get(recipe_id, {
		"kind": entity_kind,
		"bounds": {"width": 2.0, "depth": 2.0, "height": 2.0},
		"interaction_tags": ["enterable"],
		"max_compute_units": 100,
		"max_entities": 16,
		"presentation_duration_seconds": 10.0,
	}) as Dictionary

	var space_id := str(bp.get("space_id", _space_id))
	var chunk_id := str(bp.get("chunk_id", _chunk_id))
	var xform_in: Dictionary = bp.get("transform", {}) as Dictionary
	var xform := {
		"x": float(xform_in.get("x", 8.0)),
		"y": float(xform_in.get("y", 6.0)),
		"elevation": float(xform_in.get("elevation", 0.0)),
		"rotation_deg": fposmod(float(xform_in.get("rotation_deg", 0.0)), 360.0),
	}
	if is_equal_approx(float(xform["rotation_deg"]), 360.0):
		xform["rotation_deg"] = 0.0

	var bounds: Dictionary = (defaults.get("bounds", {}) as Dictionary).duplicate(true)
	var tags: Array = []
	for t in defaults.get("interaction_tags", []):
		tags.append(str(t))

	var created_at := _now_iso()
	var session_id := str(decision.get("session_id", "session_executor_01"))
	var kind := str(defaults.get("kind", entity_kind))
	if entity_kind in ALLOWED_ENTITY_KINDS:
		kind = entity_kind

	return {
		"schema_version": "1.1.0",
		"prompt_id": _new_uuid(),
		"request_id": _new_uuid(),
		"session_id": session_id,
		"actor": {"player_id": _player_id, "companion_id": _companion_id},
		"operation": operation,
		"target": {
			"space_type": _space_type,
			"space_id": space_id,
			"chunk_id": chunk_id,
			"expected_world_revision": _world_revision,
		},
		"style_profile": {
			"profile_id": _style_profile_id,
			"profile_version": _style_profile_version,
			"base_concept": _base_concept,
			"surrealism_budget": 0.15,
		},
		"entity": {
			"kind": kind,
			"recipe_id": recipe_id,
			"transform": xform,
			"bounds": {
				"width": float(bounds.get("width", 2.0)),
				"depth": float(bounds.get("depth", 2.0)),
				"height": float(bounds.get("height", 2.0)),
			},
			"interaction_tags": tags,
		},
		"manifestation": {
			"stages": ["wireframe", "hologram", "materializing", "complete"],
			"presentation_duration_seconds": float(defaults.get("presentation_duration_seconds", 10.0)),
		},
		"budget": {
			"max_compute_units": int(defaults.get("max_compute_units", 100)),
			"max_entities": int(defaults.get("max_entities", 16)),
			"paid_compute_allowed": false,
		},
		"provenance": {
			"source_type": "system",
			"requested_by": _companion_id,
			"generated_by": "agm_decision_executor",
			"created_at": created_at,
		},
		"confirmation": {
			"preview_required": true,
			"state": "pending",
			"rollback_window_seconds": 3600,
		},
	}


func _replay_receipt(decision_id: String) -> Dictionary:
	var prior: Dictionary = (_seen[decision_id] as Dictionary).duplicate(true)
	var replay := prior.duplicate(true)
	replay["status"] = "replayed"
	replay["executed_at"] = _now_iso()
	replay["notes"] = "idempotent replay; effects not re-applied"
	replay["idempotency"] = {
		"replayed": true,
		"prior_receipt_id": str(prior.get("receipt_id", "")),
		"duplicate_of_decision_id": decision_id,
	}
	# Preserve prior soft/build outcomes for caller inspection without re-apply.
	replay["prior_status"] = str(prior.get("status", ""))
	return replay


func _store_reject(decision_id: String, source_snapshot_id: String, code: String, reason: String) -> Dictionary:
	var r := _reject_receipt(decision_id, source_snapshot_id, code, reason)
	if not decision_id.is_empty():
		_seen[decision_id] = r.duplicate(true)
	return r


func _reject_receipt(decision_id: String, source_snapshot_id: String, code: String, reason: String) -> Dictionary:
	var status := "rejected"
	if code == "stale_snapshot":
		status = "stale_snapshot"
	var r := _make_receipt_base(decision_id, source_snapshot_id, status)
	r["notes"] = reason.substr(0, 256)
	r["rejection"] = {"code": code, "reason": reason.substr(0, 512)}
	r["actions_applied"] = []
	r["actions_rejected"] = [{"action": "decision", "reason": reason}]
	r["dialogue_delivered"] = []
	r["quest_ops_applied"] = []
	r["event_proposals_applied"] = []
	r["build_handoffs"] = []
	r["mood_delta_applied"] = 0.0
	r["relationship_delta_applied"] = 0.0
	r["durable_mutation_applied"] = false
	return r


func _make_receipt_base(decision_id: String, source_snapshot_id: String, status: String) -> Dictionary:
	return {
		"schema_version": RECEIPT_SCHEMA_VERSION,
		"receipt_id": _new_uuid(),
		"decision_id": decision_id if not decision_id.is_empty() else null,
		"source_snapshot_id": source_snapshot_id if not source_snapshot_id.is_empty() else null,
		"status": status,
		"executed_at": _now_iso(),
		"durable_mutation_applied": false,
	}


func _status_notes(status: String, build_count: int, reject_count: int) -> String:
	match status:
		"awaiting_player":
			return "soft effects applied; %d build(s) awaiting preview/confirm/commit" % build_count
		"partial":
			return "partial apply; %d action rejection(s)" % reject_count
		"rejected":
			return "decision rejected; %d action rejection(s)" % reject_count
		"applied":
			return "allowlisted soft effects applied; no durable mutation"
		_:
			return status


func _now_iso() -> String:
	var created_at := Time.get_datetime_string_from_system(true, true)
	if not created_at.ends_with("Z") and "+" not in created_at:
		created_at = created_at.replace(" ", "T")
		if not created_at.ends_with("Z"):
			created_at += "Z"
	return created_at


func _new_uuid() -> String:
	var b := PackedByteArray()
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
