## Validates inbound AGM Decision Envelope JSON for Free Desktop Bridge (G2-005).
## Rejects: malformed JSON, structural schema failures, forbidden fields,
## stale source_snapshot_id, and replayed decision_id.
## Does NOT execute decisions (G2-006). Does NOT auto-consent.
class_name BridgeDecisionImportGuard
extends RefCounted

const SCHEMA_VERSION := "1.0.0"
const EXPECTED_EDITION := "desktop_bridge_free"

const REQUIRED_TOP := [
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

const FORBIDDEN_TOP := [
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
	"tts_audio",
	"voice_sample",
	"microphone_buffer",
	"provider_credentials",
	"script",
	"code",
	"executable",
	"shader_code",
	"gdscript",
	"direct_world_mutation",
	"scene_tree_ops",
	"durable_mutation",
]

## Allowlisted top-level keys (additionalProperties: false).
const ALLOWED_TOP := {
	"schema_version": true,
	"decision_id": true,
	"source_snapshot_id": true,
	"created_at": true,
	"edition": true,
	"session_id": true,
	"dialogue": true,
	"quest_operations": true,
	"build_proposals": true,
	"event_proposals": true,
	"mood_delta": true,
	"relationship_delta": true,
	"next_trigger": true,
	"pacing_hint": true,
	"trace": true,
}


## Parse + validate. Returns:
## { ok: bool, decision: Dictionary, reason: String, detail: String }
func evaluate(
	raw_text: String,
	live_snapshot_id: String,
	seen_decision_ids: Dictionary
) -> Dictionary:
	if raw_text.strip_edges().is_empty():
		return _fail(BridgePaths.REJECT_EMPTY_INPUT, "input empty")

	var extracted := extract_json_object(raw_text)
	if extracted.is_empty():
		return _fail(BridgePaths.REJECT_MALFORMED_JSON, "no JSON object found")

	var json := JSON.new()
	var err := json.parse(extracted)
	if err != OK:
		return _fail(
			BridgePaths.REJECT_MALFORMED_JSON,
			"JSON.parse error: %s" % json.get_error_message()
		)

	var data: Variant = json.data
	if typeof(data) != TYPE_DICTIONARY:
		return _fail(BridgePaths.REJECT_NOT_OBJECT, "root is not an object")

	var decision: Dictionary = data
	var structural := validate_structure(decision)
	if not structural.is_empty():
		var first := structural[0]
		if first.begins_with("forbidden field"):
			return _fail(BridgePaths.REJECT_FORBIDDEN_FIELD, first)
		if first.begins_with("unknown field"):
			return _fail(BridgePaths.REJECT_FORBIDDEN_FIELD, first)
		return _fail(BridgePaths.REJECT_SCHEMA_INVALID, first)

	if live_snapshot_id.strip_edges().is_empty():
		return _fail(BridgePaths.REJECT_NO_LIVE_SNAPSHOT, "export a snapshot first")

	var source_id := str(decision.get("source_snapshot_id", ""))
	if source_id != live_snapshot_id:
		return _fail(
			BridgePaths.REJECT_STALE_SNAPSHOT,
			"source_snapshot_id=%s live=%s" % [source_id, live_snapshot_id]
		)

	var decision_id := str(decision.get("decision_id", ""))
	if seen_decision_ids.has(decision_id):
		return _fail(
			BridgePaths.REJECT_REPLAYED_DECISION,
			"decision_id already accepted: %s" % decision_id
		)

	return {
		"ok": true,
		"decision": decision.duplicate(true),
		"reason": "",
		"detail": "",
	}


func validate_structure(decision: Dictionary) -> PackedStringArray:
	var errors: PackedStringArray = []
	for key in decision.keys():
		var k := str(key)
		if FORBIDDEN_TOP.has(k) or not ALLOWED_TOP.has(k):
			# Unknown or explicitly forbidden — both rejected (additionalProperties false).
			if FORBIDDEN_TOP.has(k):
				errors.append("forbidden field: %s" % k)
			else:
				errors.append("unknown field: %s" % k)

	for key in REQUIRED_TOP:
		if not decision.has(key):
			errors.append("missing required: %s" % key)

	if str(decision.get("schema_version", "")) != SCHEMA_VERSION:
		errors.append("schema_version must be %s" % SCHEMA_VERSION)

	var edition := str(decision.get("edition", ""))
	if edition != EXPECTED_EDITION and edition != "api_paid":
		errors.append("edition invalid: %s" % edition)
	# Free bridge transport still accepts schema-valid envelopes; edition mismatch
	# for paid-only payloads is soft-warned but allowed for identity semantics.
	# Stale/replay remain hard rejects.

	if not BridgeSnapshotBuilder._looks_like_uuid(str(decision.get("decision_id", ""))):
		errors.append("decision_id must look like uuid")
	if not BridgeSnapshotBuilder._looks_like_uuid(str(decision.get("source_snapshot_id", ""))):
		errors.append("source_snapshot_id must look like uuid")

	var dialogue: Variant = decision.get("dialogue", null)
	if typeof(dialogue) != TYPE_DICTIONARY:
		errors.append("dialogue must be object")
	elif not (dialogue as Dictionary).has("lines"):
		errors.append("dialogue.lines required")

	for arr_key in ["quest_operations", "build_proposals", "event_proposals"]:
		if typeof(decision.get(arr_key, null)) != TYPE_ARRAY:
			errors.append("%s must be array" % arr_key)

	var mood: Variant = decision.get("mood_delta", null)
	if typeof(mood) != TYPE_DICTIONARY or not (mood as Dictionary).has("delta"):
		errors.append("mood_delta.delta required")
	else:
		var md := float((mood as Dictionary).get("delta", 0.0))
		if md < -0.1 or md > 0.1:
			errors.append("mood_delta.delta out of bounds")

	var rel: Variant = decision.get("relationship_delta", null)
	if typeof(rel) != TYPE_DICTIONARY or not (rel as Dictionary).has("delta"):
		errors.append("relationship_delta.delta required")
	else:
		var rd := float((rel as Dictionary).get("delta", 0.0))
		if rd < -0.05 or rd > 0.05:
			errors.append("relationship_delta.delta out of bounds")

	var next_trigger: Variant = decision.get("next_trigger", null)
	if typeof(next_trigger) != TYPE_DICTIONARY or not (next_trigger as Dictionary).has("kind"):
		errors.append("next_trigger.kind required")

	var trace: Variant = decision.get("trace", null)
	if typeof(trace) != TYPE_DICTIONARY:
		errors.append("trace must be object")
	else:
		var t: Dictionary = trace
		if str(t.get("trace_id", "")).is_empty():
			errors.append("trace.trace_id required")
		if str(t.get("model_receipt_ref", "")).is_empty():
			errors.append("trace.model_receipt_ref required")

	# Build proposals must keep preview/confirm/commit path if present.
	var builds: Variant = decision.get("build_proposals", [])
	if typeof(builds) == TYPE_ARRAY:
		for item in builds:
			if typeof(item) != TYPE_DICTIONARY:
				errors.append("build_proposals item not object")
				continue
			var bp: Dictionary = item
			if bp.get("preview_required", null) != true:
				errors.append("build_proposals.preview_required must be true")
			if str(bp.get("confirmation_state", "")) != "pending":
				errors.append("build_proposals.confirmation_state must be pending")
			if str(bp.get("routes_through", "")) != "preview_confirm_commit":
				errors.append("build_proposals.routes_through must be preview_confirm_commit")

	return errors


## Pull first top-level `{...}` from free-form AI Desktop paste (fenced or raw).
func extract_json_object(raw_text: String) -> String:
	var text := raw_text.strip_edges()
	# Strip markdown fences if present.
	if "```" in text:
		var fence_start := text.find("```")
		var after := text.substr(fence_start + 3)
		# optional language tag
		var nl := after.find("\n")
		if nl >= 0:
			after = after.substr(nl + 1)
		var fence_end := after.find("```")
		if fence_end >= 0:
			after = after.substr(0, fence_end)
		text = after.strip_edges()

	var start := text.find("{")
	if start < 0:
		return ""
	var depth := 0
	var in_string := false
	var escape := false
	for i in range(start, text.length()):
		var ch := text[i]
		if in_string:
			if escape:
				escape = false
			elif ch == "\\":
				escape = true
			elif ch == "\"":
				in_string = false
			continue
		if ch == "\"":
			in_string = true
			continue
		if ch == "{":
			depth += 1
		elif ch == "}":
			depth -= 1
			if depth == 0:
				return text.substr(start, i - start + 1)
	return ""


func _fail(reason: String, detail: String) -> Dictionary:
	return {
		"ok": false,
		"decision": {},
		"reason": reason,
		"detail": detail,
	}
