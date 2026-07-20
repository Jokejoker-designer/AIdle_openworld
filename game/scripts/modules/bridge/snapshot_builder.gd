## Builds redacted World State Snapshot dictionaries for Free Desktop Bridge.
## Shape matches contracts/agm/world_state_snapshot.schema.json (structural).
## Never includes secrets, credentials, raw system prompts, or TTS/voice.
class_name BridgeSnapshotBuilder
extends RefCounted

const SCHEMA_VERSION := "1.0.0"
const EDITION := "desktop_bridge_free"

## Top-level keys forbidden in any exported snapshot (propertyNames deny-list).
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
]


## Build a schema-shaped snapshot. `context` may override bounded fields.
func build(context: Dictionary = {}) -> Dictionary:
	var now := _iso_now()
	var snapshot_id := str(context.get("snapshot_id", _new_uuid()))
	var channel := str(context.get("channel", BridgePaths.CHANNEL_CLIPBOARD))
	if channel != BridgePaths.CHANNEL_CLIPBOARD and channel != BridgePaths.CHANNEL_FILE:
		channel = BridgePaths.CHANNEL_CLIPBOARD

	var player_loc: Dictionary = {
		"chunk_id": str(context.get("chunk_id", "0_0")),
		"x": float(context.get("player_x", 8.0)),
		"y": float(context.get("player_y", 6.0)),
		"elevation": float(context.get("elevation", 0.0)),
	}

	var last_receipt: Dictionary = context.get("last_execution_receipt", {
		"decision_id": null,
		"status": "none",
	}) as Dictionary

	var recent_turns: Array = context.get("recent_turns", [
		{"role": "system", "text": "Starter Realm loaded."},
		{"role": "companion", "text": "Welcome home. Shall we plant something first?"},
	]) as Array

	var snap := {
		"schema_version": SCHEMA_VERSION,
		"snapshot_id": snapshot_id,
		"created_at": str(context.get("created_at", now)),
		"edition": EDITION,
		"session_id": str(context.get("session_id", "session_starter_01")),
		"space_id": str(context.get("space_id", "home_01")),
		"world_revision": int(context.get("world_revision", 0)),
		"progression_phase": str(context.get("progression_phase", "onboarding")),
		"art_style": {
			"profile_id": str(context.get("art_profile_id", "cozy_default")),
			"base_concept": str(context.get("base_concept", "cozy_cyber_pixel_2_5d")),
			"profile_version": str(context.get("profile_version", "1.0.0")),
		},
		"player": {
			"player_id": str(context.get("player_id", "player_01")),
			"display_name": str(context.get("display_name", "Ava")),
			"location": player_loc,
		},
		"companion": {
			"companion_id": str(context.get("companion_id", "companion_aida")),
			"mood": float(context.get("companion_mood", 0.62)),
			"relationship": float(context.get("companion_relationship", 0.4)),
			"personality_revision": int(context.get("personality_revision", 0)),
			"recent_dialogue_summary": str(
				context.get("recent_dialogue_summary", "Welcomed player to Starter Realm.")
			),
		},
		"world": {
			"space_type": str(context.get("space_type", "private_reality")),
			"entity_count": int(context.get("entity_count", 12)),
			"known_entity_ids": context.get(
				"known_entity_ids",
				["house_placeholder", "farm_plot_01", "path_01", "lamp_01"]
			),
			"starter_realm": bool(context.get("starter_realm", true)),
		},
		"quests": {
			"active": context.get("active_quests", []),
			"completed_ids": context.get("completed_quest_ids", []),
		},
		"latest_player_action": {
			"action_type": str(context.get("action_type", "session_start")),
			"occurred_at": str(context.get("action_occurred_at", now)),
			"summary": str(
				context.get(
					"action_summary",
					"Player entered Starter Realm for the first time."
				)
			),
		},
		"last_execution_receipt": last_receipt.duplicate(true),
		"memory": {
			"recent_turns": recent_turns.duplicate(true) if recent_turns is Array else [],
			"summary": str(context.get("memory_summary", "Onboarding about to begin; no quests yet.")),
		},
		"trace_id": str(context.get("trace_id", "trace_bridge_%s" % snapshot_id.substr(0, 8))),
		"transport": {
			"channel": channel,
			"bridge_path_hint": str(
				context.get("bridge_path_hint", BridgePaths.OUTBOX_SNAPSHOT)
			),
		},
	}

	# Hard strip any accidental forbidden keys at top level.
	for bad in FORBIDDEN_KEYS:
		if snap.has(bad):
			snap.erase(bad)

	return snap


## Minimal structural check for exported snapshots (not full Draft 2020-12 engine).
func validate_structure(snapshot: Dictionary) -> PackedStringArray:
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
	if snapshot.get("schema_version", "") != SCHEMA_VERSION:
		errors.append("schema_version must be %s" % SCHEMA_VERSION)
	if snapshot.get("edition", "") != EDITION:
		errors.append("edition must be %s for Free Desktop Bridge" % EDITION)
	for bad in FORBIDDEN_KEYS:
		if snapshot.has(bad):
			errors.append("forbidden field: %s" % bad)
	if not _looks_like_uuid(str(snapshot.get("snapshot_id", ""))):
		errors.append("snapshot_id must look like uuid")
	return errors


func to_pretty_json(snapshot: Dictionary) -> String:
	return JSON.stringify(snapshot, "\t")


func clipboard_payload(snapshot: Dictionary) -> String:
	return BridgePaths.CLIPBOARD_INSTRUCTION_HEADER + to_pretty_json(snapshot)


static func _iso_now() -> String:
	var dt := Time.get_datetime_dict_from_system(true)
	return "%04d-%02d-%02dT%02d:%02d:%02dZ" % [
		int(dt.year), int(dt.month), int(dt.day),
		int(dt.hour), int(dt.minute), int(dt.second),
	]


static func _new_uuid() -> String:
	# UUID v4-ish; sufficient for local bridge idempotency keys.
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


static func _looks_like_uuid(value: String) -> bool:
	if value.length() != 36:
		return false
	var parts := value.split("-")
	if parts.size() != 5:
		return false
	if parts[0].length() != 8 or parts[1].length() != 4:
		return false
	if parts[2].length() != 4 or parts[3].length() != 4:
		return false
	if parts[4].length() != 12:
		return false
	return true
