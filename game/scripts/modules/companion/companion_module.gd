## Agent-Companion module (G2-003 AGM rework): text-only + AGM Decision Envelope consumer.
## Produces schema-valid World Prompt proposals. NO commit / NO durable world mutation.
## AGM dialogue/proposals are untrusted until validated; Companion never invents world truth.
## Never calls Voxel. May hand proposals to Executor.submit_prompt when available
## (Executor owns pipeline; Companion does not commit).
class_name CompanionModule
extends Node3D

const MODULE_ID := "companion"

signal proposal_ready(proposal: Dictionary)
signal chat_message(role: String, text: String)
signal personality_control(action: String, detail: Dictionary)
signal agm_decision_applied(result: Dictionary)
signal agm_decision_rejected(errors: PackedStringArray, decision_id: String)

@export var companion_id: String = "companion_lumi"
@export var player_id: String = "player_01"
@export var follow_enabled: bool = true
@export var follow_distance: float = 2.2

var _personality: CompanionPersonalityProfile
var _builder: CompanionWorldPromptBuilder
var _agm: CompanionAgmDecisionApplier
var _mood: String = "calm"
var _player: Node3D
var _last_proposal: Dictionary = {}
var _proposals: Array = []
var _chat_log: Array = []
var _spawned: bool = false
var _last_agm_result: Dictionary = {}
var _quest_notes: Array = []
var _event_notes: Array = []
var _next_trigger: Dictionary = {}
var _live_snapshot_id: String = ""

## Visual placeholder (simple aura mesh) — expression only, not player diagnosis.
var _body: MeshInstance3D
var _aura: MeshInstance3D


func _ready() -> void:
	_ensure_logic_state()
	if not _personality.control_applied.is_connected(_on_personality_control):
		_personality.control_applied.connect(_on_personality_control)
	_ensure_visuals()
	var registry := _service("ModuleRegistry")
	if registry != null:
		var existing_mod: Node = registry.call("get_module", MODULE_ID) as Node
		if existing_mod == null or existing_mod == self or existing_mod.has_method("is_stub"):
			registry.call("register_module", MODULE_ID, self)
	print("[CompanionModule] Ready – AGM-driven text-only, proposal-only (no commit tool).")


func is_stub() -> bool:
	return false


func get_status() -> String:
	return "Companion online | mood=%s | proposals=%d | agm=%d | rev=%d" % [
		_mood,
		_proposals.size(),
		_agm.get_applied_ids().size() if _agm else 0,
		_personality.revision,
	]


# ─── ICompanionModule surface ────────────────────────────────────────────────

func spawn_companion(player: Node3D, mount: Node) -> void:
	_player = player
	if mount and get_parent() != mount:
		if get_parent():
			get_parent().remove_child(self)
		mount.add_child(self)
	if player and player is Node3D:
		global_position = player.global_position + Vector3(-follow_distance, 0.0, follow_distance)
	_spawned = true
	set_emotional_state("calm")
	_append_chat(
		"companion",
		"Xin chào — mình là companion text-only. Mình chỉ *đề xuất* World Prompt, không commit thế giới."
	)


func set_emotional_state(mood: String) -> void:
	_mood = mood.strip_edges().to_lower()
	if _mood.is_empty():
		_mood = "calm"
	_update_aura_color()
	var bus := _service("EventBus")
	if bus != null:
		bus.emit_signal("emotional_state_changed", companion_id, _mood, _aura_color_for(_mood))


func get_emotional_state() -> String:
	return _mood


## Natural language → SWP proposal only. Does NOT commit. Optionally forwards
## pending proposal to Executor.submit_prompt when Executor is registered.
func request_world_change(natural_language: String) -> void:
	_personality.begin_turn()
	_append_chat("player", natural_language)
	var proposal := propose_from_text(natural_language)
	if proposal.is_empty():
		var reply := _style_reply(
			"Mình chưa map được intent thành World Prompt. Thử: 'xây nhà', 'đèn vườn', hoặc 'sàn gạch'."
		)
		_append_chat("companion", reply)
		return
	var entity_info: Dictionary = proposal.get("entity", {}) as Dictionary
	var reply2 := _style_reply(
		"Đã tạo proposal pending (preview_required). prompt_id=%s recipe=%s — chờ confirm ngoài Companion."
		% [str(proposal.get("prompt_id", "")), str(entity_info.get("recipe_id", ""))]
	)
	_append_chat("companion", reply2)
	_hand_off_to_executor_if_present(proposal)


# ─── AGM Decision Envelope (validated dialogue + pending proposals only) ─────

## Bind live World State Snapshot id so stale AGM decisions are rejected.
func set_live_snapshot_id(snapshot_id: String) -> void:
	_live_snapshot_id = snapshot_id
	_ensure_logic_state()
	_agm.set_live_snapshot_id(snapshot_id)


## Apply a provider-neutral AGM Decision Envelope after schema-informed validation.
## Returns application result. Never commits durable world state.
func apply_agm_decision(envelope: Dictionary) -> Dictionary:
	_ensure_logic_state()
	_personality.begin_turn()

	var projected := _agm.project(envelope, _builder)
	if not bool(projected.get("ok", false)):
		var errs: PackedStringArray = projected.get("errors", PackedStringArray()) as PackedStringArray
		var did := str(projected.get("decision_id", ""))
		agm_decision_rejected.emit(errs, did)
		var err_text := "AGM decision rejected"
		if errs.size() > 0:
			err_text = "AGM decision rejected: %s" % str(errs[0])
		_append_chat("system", err_text)
		_last_agm_result = projected
		return projected.duplicate(true)

	# Dialogue (text-only).
	for line_v in projected.get("dialogue_lines", []):
		if typeof(line_v) != TYPE_DICTIONARY:
			continue
		var line: Dictionary = line_v
		var speaker := str(line.get("speaker", "companion"))
		var text := str(line.get("text", ""))
		if text.is_empty():
			continue
		if speaker == "companion":
			_append_chat("companion", _style_reply(text))
		elif speaker == "narrator":
			_append_chat("narrator", text)
		else:
			var npc_id := str(line.get("npc_id", "npc"))
			_append_chat("npc:%s" % npc_id, text)

	# Expression → temporary emotional aura (not diagnosis).
	var expression := str(projected.get("expression", "neutral"))
	set_emotional_state(CompanionAgmDecisionApplier.expression_to_mood(expression))

	# Build proposals → schema-valid pending World Prompts only.
	var stored_prompts: Array = []
	for prompt_v in projected.get("world_prompts", []):
		if typeof(prompt_v) != TYPE_DICTIONARY:
			continue
		var prompt: Dictionary = prompt_v
		var stored := _store_proposal(prompt)
		if not stored.is_empty():
			stored_prompts.append(stored)
			_hand_off_to_executor_if_present(stored)

	# Soft personality drift from bounded AGM deltas (still capped by profile policy).
	_apply_agm_personality_deltas(
		float(projected.get("mood_delta", 0.0)),
		float(projected.get("relationship_delta", 0.0)),
		str(projected.get("mood_reason", "")),
		str(projected.get("relationship_reason", ""))
	)

	# Quest / event notes (non-mutating bookkeeping for UI / later executor).
	for q in projected.get("quest_operations", []):
		if typeof(q) == TYPE_DICTIONARY:
			_quest_notes.append((q as Dictionary).duplicate(true))
	for e in projected.get("event_proposals", []):
		if typeof(e) == TYPE_DICTIONARY:
			_event_notes.append((e as Dictionary).duplicate(true))
	if projected.get("next_trigger") is Dictionary:
		_next_trigger = (projected["next_trigger"] as Dictionary).duplicate(true)

	projected["world_prompts"] = stored_prompts
	projected["applied_by"] = companion_id
	projected["text_only"] = true
	projected["committed"] = false
	_last_agm_result = projected.duplicate(true)
	agm_decision_applied.emit(_last_agm_result)

	if stored_prompts.size() > 0:
		var first: Dictionary = stored_prompts[0]
		var entity_info: Dictionary = first.get("entity", {}) as Dictionary
		_append_chat(
			"system",
			"AGM build proposal projected as pending World Prompt (preview_required). recipe=%s prompt_id=%s"
			% [str(entity_info.get("recipe_id", "")), str(first.get("prompt_id", ""))]
		)
	return _last_agm_result.duplicate(true)


func _ensure_logic_state() -> void:
	if _personality == null:
		_personality = CompanionPersonalityProfile.new(companion_id)
	if _builder == null:
		_builder = CompanionWorldPromptBuilder.new()
		_builder.configure_context({
			"player_id": player_id,
			"companion_id": companion_id,
			"session_id": "session_companion_01",
			"space_type": "private_reality",
			"space_id": "home_01",
			"chunk_id": "0_0",
			"expected_world_revision": 0,
		})
	if _agm == null:
		_agm = CompanionAgmDecisionApplier.new()
	if not _live_snapshot_id.is_empty():
		_agm.set_live_snapshot_id(_live_snapshot_id)


func get_last_agm_result() -> Dictionary:
	return _last_agm_result.duplicate(true)


func get_quest_notes() -> Array:
	return _quest_notes.duplicate(true)


func get_event_notes() -> Array:
	return _event_notes.duplicate(true)


func get_next_trigger() -> Dictionary:
	return _next_trigger.duplicate(true)


func get_agm_applier() -> CompanionAgmDecisionApplier:
	return _agm


# ─── Proposal API (acceptance: schema-valid, no commit tool) ─────────────────

func propose_from_text(natural_language: String) -> Dictionary:
	var proposal := _builder.build_from_natural_language(natural_language)
	return _store_proposal(proposal)


func propose_world_prompt(recipe_id: String, transform: Dictionary = {}) -> Dictionary:
	var proposal := _builder.build_proposal(recipe_id, "player_request", transform)
	return _store_proposal(proposal)


func propose_gift(recipe_id: String = "garden_lamp") -> Dictionary:
	var proposal := _builder.build_gift_proposal(recipe_id)
	if not proposal.is_empty():
		var bus := _service("EventBus")
		if bus != null:
			bus.emit_signal(
				"random_alchemist_gift",
				str(proposal.get("prompt_id", "")),
				companion_id,
				proposal.get("provenance", {}) as Dictionary
			)
		set_emotional_state("playful")
	return _store_proposal(proposal)


func get_last_proposal() -> Dictionary:
	return _last_proposal.duplicate(true)


func get_proposals() -> Array:
	return _proposals.duplicate(true)


## Export last proposal as JSON string (for fixtures / receipts).
func export_last_proposal_json() -> String:
	if _last_proposal.is_empty():
		return "{}"
	return JSON.stringify(_last_proposal, "\t")


func list_tools() -> Array:
	return CompanionWorldPromptBuilder.list_tools()


func has_commit_tool() -> bool:
	return CompanionWorldPromptBuilder.has_commit_tool()


# ─── Personality controls (inspect / lock / reset / delete) ──────────────────

func get_personality() -> CompanionPersonalityProfile:
	return _personality


func inspect_personality() -> Dictionary:
	return _personality.inspect()


func inspect_personality_text() -> String:
	return _personality.inspect_plain_language()


func lock_trait(trait_name: String) -> bool:
	return _personality.lock_trait(trait_name)


func unlock_trait(trait_name: String) -> bool:
	return _personality.unlock_trait(trait_name)


func set_adaptation_enabled(enabled: bool) -> void:
	_personality.set_adaptation_enabled(enabled)


func reset_personality() -> void:
	_personality.reset_adaptive_to_base()


func delete_adaptation_history() -> void:
	_personality.delete_adaptation_history()


func apply_personality_observation(
	trait_name: String,
	signed_evidence: float,
	confidence: float,
	reason: String = "",
	observation_count: int = 3,
	independent_sessions: int = 3
) -> float:
	return _personality.apply_observation(
		trait_name, signed_evidence, confidence, reason, observation_count, independent_sessions
	)


## Text chat entry (no speech/voice models). Commands for personality controls.
func receive_message(text: String) -> String:
	var raw := text.strip_edges()
	if raw.is_empty():
		return ""
	_personality.begin_turn()
	_append_chat("player", raw)
	var lower := raw.to_lower()

	# Personality control commands (text UI).
	if lower.begins_with("/inspect") or lower == "inspect personality" or "xem tính cách" in lower:
		var report := inspect_personality_text()
		_append_chat("companion", report)
		return report
	if lower.begins_with("/lock "):
		var lock_key := lower.substr(6).strip_edges()
		var ok_lock := lock_trait(lock_key)
		var msg_lock := ("Locked trait: %s" % lock_key) if ok_lock else ("Unknown trait: %s" % lock_key)
		_append_chat("companion", msg_lock)
		return msg_lock
	if lower.begins_with("/unlock "):
		var unlock_key := lower.substr(8).strip_edges()
		var ok_unlock := unlock_trait(unlock_key)
		var msg_unlock := ("Unlocked trait: %s" % unlock_key) if ok_unlock else ("Unknown trait: %s" % unlock_key)
		_append_chat("companion", msg_unlock)
		return msg_unlock
	if lower == "/reset" or lower == "reset personality" or "reset tính cách" in lower:
		reset_personality()
		var msg_r := "Adaptive traits reset to base."
		_append_chat("companion", msg_r)
		return msg_r
	if lower == "/delete" or lower == "delete history" or "xóa lịch sử" in lower:
		delete_adaptation_history()
		var msg_d := "Adaptation history deleted; adaptive traits restored to base."
		_append_chat("companion", msg_d)
		return msg_d
	if lower == "/tools":
		var names: PackedStringArray = []
		for t in list_tools():
			names.append(str(t.get("name", "")))
		var msg_t := "Tools (no commit): %s" % ", ".join(names)
		_append_chat("companion", msg_t)
		return msg_t
	if lower == "/agm" or lower == "/last_agm":
		if _last_agm_result.is_empty():
			var none_msg := "No AGM decision applied yet."
			_append_chat("companion", none_msg)
			return none_msg
		var agm_msg := "Last AGM decision_id=%s prompts=%d expression=%s committed=false" % [
			str(_last_agm_result.get("decision_id", "")),
			(_last_agm_result.get("world_prompts", []) as Array).size(),
			str(_last_agm_result.get("expression", "")),
		]
		_append_chat("companion", agm_msg)
		return agm_msg
	if lower.begins_with("/gift"):
		var gift_proposal := propose_gift()
		var msg_g := "Gift proposal pending: %s" % str(gift_proposal.get("prompt_id", "failed"))
		_append_chat("companion", msg_g)
		return msg_g

	# World proposal intents.
	var recipe := _builder.detect_recipe(raw)
	if not recipe.is_empty():
		request_world_change(raw)
		if _chat_log.is_empty():
			return ""
		var last_entry: Dictionary = _chat_log.back()
		return str(last_entry.get("text", ""))

	var fallback := _style_reply(
		"Mình nghe bạn đây (text-only, AGM-driven). Gõ ý định xây ('xây nhà'), /inspect, /lock warmth, /reset, /delete, /tools, /agm."
	)
	_append_chat("companion", fallback)
	return fallback


func get_chat_log() -> Array:
	return _chat_log.duplicate(true)


# ─── Follow / process ────────────────────────────────────────────────────────

func _process(delta: float) -> void:
	if not follow_enabled or _player == null or not is_instance_valid(_player):
		return
	if not (_player is Node3D):
		return
	var target: Vector3 = (_player as Node3D).global_position + Vector3(-follow_distance, 0.0, follow_distance)
	global_position = global_position.lerp(target, clampf(delta * 3.0, 0.0, 1.0))


# ─── Internals ───────────────────────────────────────────────────────────────

func _store_proposal(proposal: Dictionary) -> Dictionary:
	if proposal.is_empty():
		return {}
	# Invariant: companion proposals never leave pending confirmation here.
	if proposal.has("confirmation") and proposal["confirmation"] is Dictionary:
		var conf: Dictionary = proposal["confirmation"]
		conf["preview_required"] = true
		conf["state"] = "pending"
		conf.erase("confirmed_by")
		proposal["confirmation"] = conf
	else:
		proposal["confirmation"] = {
			"preview_required": true,
			"state": "pending",
			"rollback_window_seconds": 3600,
		}
	_last_proposal = proposal.duplicate(true)
	_proposals.append(_last_proposal.duplicate(true))
	proposal_ready.emit(_last_proposal)
	set_emotional_state("focused")
	return _last_proposal.duplicate(true)


## Map AGM mood/relationship deltas into personality observations.
## Caps remain those of personality_profile (turn/day/distance); AGM cannot force large drift.
func _apply_agm_personality_deltas(
	mood_delta: float,
	relationship_delta: float,
	mood_reason: String,
	relationship_reason: String
) -> void:
	if _personality == null:
		return
	# Evidence is signed in [-1,1]; scale small schema deltas into evidence units.
	if not is_zero_approx(mood_delta):
		var mood_evidence := clampf(mood_delta / 0.1, -1.0, 1.0)
		_personality.apply_observation(
			"warmth",
			mood_evidence,
			0.7,
			mood_reason if not mood_reason.is_empty() else "agm_mood_delta",
			3,
			3,
			"agm_mood"
		)
		_personality.apply_observation(
			"calmness",
			mood_evidence * 0.5,
			0.7,
			mood_reason if not mood_reason.is_empty() else "agm_mood_delta",
			3,
			3,
			"agm_mood"
		)
	if not is_zero_approx(relationship_delta):
		var rel_evidence := clampf(relationship_delta / 0.05, -1.0, 1.0)
		_personality.apply_observation(
			"supportive_guardianship",
			rel_evidence,
			0.7,
			relationship_reason if not relationship_reason.is_empty() else "agm_relationship_delta",
			3,
			3,
			"agm_relationship"
		)


func _hand_off_to_executor_if_present(proposal: Dictionary) -> void:
	if proposal.is_empty():
		return
	var registry := _service("ModuleRegistry")
	if registry == null or not bool(registry.call("has_module", "executor")):
		return
	var ex: Node = registry.call("get_module", "executor") as Node
	if ex == null or not ex.has_method("submit_prompt"):
		return
	# Executor owns validate→preview path. Companion still does not commit.
	ex.call("submit_prompt", proposal)


func _append_chat(role: String, text: String) -> void:
	_chat_log.append({"role": role, "text": text})
	chat_message.emit(role, text)


func _style_reply(base: String) -> String:
	var warmth := _personality.get_effective_trait("warmth")
	var brevity := _personality.get_effective_trait("brevity")
	var humor := _personality.get_effective_trait("humor")
	var out := base
	if warmth > 0.65:
		out = out + " ♥"
	if humor > 0.6 and brevity < 0.5:
		out = out + " (aura nhấp nháy vui vẻ.)"
	if brevity > 0.7 and out.length() > 120:
		out = out.substr(0, 117) + "..."
	return out


func _on_personality_control(action: String, detail: Dictionary) -> void:
	personality_control.emit(action, detail)


func _ensure_visuals() -> void:
	if _body != null:
		return
	if DisplayServer.get_name() == "headless":
		return
	_body = MeshInstance3D.new()
	_body.name = "Body"
	var sphere := SphereMesh.new()
	sphere.radius = 0.35
	sphere.height = 0.7
	_body.mesh = sphere
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.55, 0.75, 1.0, 1.0)
	mat.emission_enabled = true
	mat.emission = Color(0.2, 0.45, 0.9)
	mat.emission_energy_multiplier = 0.6
	_body.material_override = mat
	_body.position = Vector3(0, 0.9, 0)
	add_child(_body)

	_aura = MeshInstance3D.new()
	_aura.name = "Aura"
	var aura_mesh := SphereMesh.new()
	aura_mesh.radius = 0.55
	aura_mesh.height = 1.1
	_aura.mesh = aura_mesh
	var aura_mat := StandardMaterial3D.new()
	aura_mat.albedo_color = Color(0.3, 0.7, 1.0, 0.25)
	aura_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	aura_mat.emission_enabled = true
	aura_mat.emission = Color(0.2, 0.6, 1.0)
	aura_mat.emission_energy_multiplier = 0.4
	_aura.material_override = aura_mat
	_aura.position = Vector3(0, 0.9, 0)
	add_child(_aura)


func _service(service_name: String) -> Node:
	if not is_inside_tree() or get_tree() == null:
		return null
	return get_tree().root.get_node_or_null(service_name)


func _update_aura_color() -> void:
	if _aura == null or _aura.material_override == null:
		return
	var mat := _aura.material_override as StandardMaterial3D
	if mat == null:
		return
	var c := _aura_color_for(_mood)
	mat.albedo_color = Color(c.r, c.g, c.b, 0.28)
	mat.emission = c


func _aura_color_for(mood: String) -> Color:
	match mood:
		"happy", "playful":
			return Color(1.0, 0.85, 0.35)
		"excited", "focused":
			return Color(1.0, 0.45, 0.85)
		"empathetic", "soft":
			return Color(1.0, 0.55, 0.65)
		_:
			return Color(0.25, 0.65, 1.0)
