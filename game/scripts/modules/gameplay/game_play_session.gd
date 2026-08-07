## GamePlaySession — single mount point for the completed cozy gameplay loop.
## Mounts under Main in the scene tree; wires subsystems together and routes
## their events onto EventBus so other modules (companion, AGM, UI) can react.
##
## The loop it completes, per Master Blueprint v1.1:
## - NPC/Companion talk → relationship points + dialogue beats (level-gated)
## - Quest offer (opt-in) → accept → goal progress → complete → reward +
##   relationship points, with journal provenance per beat.
## - Builds keep cost-awareness: the economy ledger approves recipe costs
##   alongside the authority commit path (preview never spends).
## - Day/night + weather cycle publishes time-of-day ambient events.
extends Node

const _Economy = preload("res://scripts/modules/gameplay/game_economy.gd")
const _QuestSystem = preload("res://scripts/modules/gameplay/game_quest_system.gd")
const _Meter = preload("res://scripts/modules/gameplay/game_relationship_meter.gd")
const _DayNight = preload("res://scripts/modules/gameplay/game_day_night_weather.gd")
const _Npc = preload("res://scripts/modules/gameplay/game_npc_interaction.gd")
const _Journal = preload("res://scripts/modules/gameplay/game_day_journal.gd")
const _Ui = preload("res://scripts/modules/gameplay/game_ui_overlay.gd")

var economy: RefCounted
var quests: RefCounted
var meter: RefCounted
var npc: RefCounted
var journal: RefCounted
var _day_night: GameDayNightWeather
var _ui: GameUiOverlay

var _event_bus: Node = null

func _ready() -> void:
	name = "GamePlaySession"
	economy = _Economy.new()
	quests = _QuestSystem.new()
	meter = _Meter.new({"warmth": 0.6, "curiosity": 0.55, "calmness": 0.7, "humor": 0.5, "protectiveness": 0.55})
	npc = _Npc.new()
	journal = _Journal.new()
	npc.attach(quests, meter, economy)
	_day_night = _DayNight.new()
	add_child(_day_night)
	_ui = _Ui.new()
	add_child(_ui)
	_ui.configure(economy, quests, meter, _day_night, npc)
	_wire_bus()
	_seed_starter_content()
	print("[GamePlaySession] Cozy gameplay loop online: economy, quests, relationship, day/night, NPC society.")

func _wire_bus() -> void:
	_event_bus = get_tree().get_root().get_node_or_null("EventBus") as Node
	if _event_bus == null:
		return
	if _day_night.has_signal("time_of_day_changed"):
		_day_night.time_of_day_changed.connect(_on_time_of_day)
	if _day_night.has_signal("day_advanced"):
		_day_night.day_advanced.connect(_on_day_advanced)
	if _day_night.has_signal("weather_changed"):
		_day_night.weather_changed.connect(_on_weather)

func _on_time_of_day(hour: float, label: String, _light: float) -> void:
	if _event_bus == null:
		return
	var envelope := {
		"event_type": "ambient.time_of_day_hint",
		"summary": "%s — %s (ngày %d)" % [str(label), _hour_str(hour), _day_night.get_day()],
		"hour": hour,
	}
	_emit_gameplay_event("gameplay.time_of_day", envelope)

func _on_day_advanced(day: int) -> void:
	if _event_bus == null:
		return
	var envelope := {"event_type": "ambient.time_of_day_hint", "summary": "Một ngày mới bắt đầu — ngày %d." % day}
	_emit_gameplay_event("gameplay.day_advanced", envelope)

func _on_weather(weather: String, intensity: float) -> void:
	if _event_bus == null:
		return
	var envelope := {"event_type": "ambient.weather_hint", "summary": "Thời tiết chuyển sang %s." % str(weather), "weather": weather, "intensity": intensity}
	_emit_gameplay_event("gameplay.weather_changed", envelope)

func _emit_gameplay_event(event_id: String, payload: Dictionary) -> void:
	if _event_bus == null:
		return
	if _event_bus.has_method("emit_gameplay_event"):
		_event_bus.call("emit_gameplay_event", event_id, payload)
	else:
		print("[GamePlaySession] event bus event=%s payload=%s" % [event_id, str(payload.get("summary", ""))])

## Public API used by UI (HUD button) and console commands.
func talk_npc(npc_id: String) -> Dictionary:
	var res: Dictionary = npc.call("talk", npc_id) if npc.has_method("talk") else {"ok": false, "reason": "npc_unavailable"}
	if res.get("ok", false):
		journal.record(_day_night.get_day(), "npc_talk", str(res.get("line", "")))
	return res

func pet_npc() -> Dictionary:
	var res: Dictionary = npc.call("pet", "bui_mo") if npc.has_method("pet") else {"ok": false, "reason": "npc_unavailable"}
	if res.get("ok", false):
		journal.record(_day_night.get_day(), "npc_pet", str(res.get("line", "")))
	return res

func quest_from_npc(npc_id: String, quest_id: String, title: String, objective: String, goals: Array = [], reward: Dictionary = {}) -> Dictionary:
	var res: Dictionary = npc.call("npc_quest", npc_id, quest_id, title, objective, goals, reward) if npc.has_method("npc_quest") else {"ok": false, "reason": "npc_unavailable"}
	if res.get("ok", false):
		journal.record(_day_night.get_day(), "quest_offered", "%s: %s" % [str(title), str(objective)])
	return res

func accept_quest(quest_id: String) -> Dictionary:
	return quests.call("apply_op", {"op": "accept", "quest_id": quest_id})

func advance_goal(quest_id: String, goal_kind: String, target: String = "", count: int = 1) -> Dictionary:
	var res: Dictionary = quests.call("apply_op", {"op": "advance_goal", "quest_id": quest_id, "goal_kind": goal_kind, "target": target, "count": count})
	if res.get("ok", false) and bool(res.get("goals_met", false)):
		_handle_quest_completion(quest_id, res)
		journal.record(_day_night.get_day(), "quest_completed", "Quest %s hoàn thành!" % quest_id)
	return res

func _handle_quest_completion(quest_id: String, res: Dictionary) -> void:
	var reward: Dictionary = res.get("reward", {})
	if not reward.is_empty() and economy != null:
		var grant: Dictionary = economy.call("grant_income", reward, "quest_reward_%s" % quest_id)
		print("[GamePlaySession] quest reward granted=%s" % str(grant.get("code", "")))
	var rel_gain: int = int(res.get("relationship_gain", 0))
	if rel_gain > 0 and meter != null:
		meter.call("add_points", rel_gain, "quest_completed_%s" % quest_id)
	if meter != null:
		var snap: Dictionary = meter.call("snapshot")
		if bool(snap.get("leveled_up", false)):
			journal.record(_day_night.get_day(), "relationship_level_up", "Quan hệ tăng lên %s!" % str(snap.get("level_name", "")))

func npc_gift(npc_id: String, recipe_id: String) -> Dictionary:
	var res: Dictionary = npc.call("offer_npc_gift", npc_id, recipe_id)
	if res.get("ok", false):
		journal.record(_day_night.get_day(), "npc_gift_offered", "%s tặng %s" % [npc_id, recipe_id])
	return res

## Cost-aware build helper: approve cost then return the economic part of a
## commit. Actual world mutation still goes through world_authority_local
## preview→confirm→commit; this only guarantees no "built but unpaid" state.
func pay_for_build(recipe_id: String, reason: String = "build_commit") -> Dictionary:
	var cost: Dictionary = economy.call("cost_for", recipe_id) as Dictionary
	if cost.is_empty():
		return {"ok": true, "code": "free_recipe", "cost": cost}
	var approved: Dictionary = economy.call("approve_spend", cost, reason)
	if approved.get("ok", false):
		return approved
	journal.record(_day_night.get_day(), "build_cost_paid", "%s: %s" % [recipe_id, str(cost)])
	return {"ok": true, "code": "cost_approved", "cost": cost, "entry": approved.get("entry", {})}

func spend_spirit(amount: float) -> Dictionary:
	var res: Dictionary = economy.call("spend_spirit", amount)
	if res.get("ok", false):
		return res
	journal.record(_day_night.get_day(), "spirit_spent", str(amount))
	return res

## Presentation-only helper: set weather for demo/pacing (still emits events).
func set_weather(weather: String) -> Dictionary:
	return _day_night.set_weather(weather)

func toggle_ui() -> void:
	_ui.toggle_ui(not _ui.visible)

func snapshot() -> Dictionary:
	return {
		"economy": economy.call("snapshot"),
		"quests": quests.call("snapshot"),
		"relationship": meter.call("snapshot"),
		"day_night": _day_night.snapshot(),
		"npcs": npc.call("snapshot"),
		"journal_recent": journal.recent_memories(8),
	}

func _seed_starter_content() -> void:
	# Starter quest from Bac Bap so new players immediately see the loop.
	var starter: Dictionary = npc.call("npc_quest", "bac_bap", "q_starter_garden", "Vườn rau đầu tiên", "Trồng 3 luống rau với Bac Bap", [{"kind": "collect", "target": "vegetable_bed", "need": 3}], {"coin": 25, "food": 3})
	if starter.get("ok", false):
		print("[GamePlaySession] Starter quest offered: q_starter_garden")

func _hour_str(hour: float) -> String:
	var h := int(floor(float(hour))) % 24
	var m := int(fmod(float(hour), 1.0) * 60)
	return "%02d:%02d" % [h, m]
