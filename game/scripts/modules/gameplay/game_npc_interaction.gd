## NPC interaction system — seeds the H2 "NPC society" while staying fully
## inside the 2.5D vertical slice. Connects to the existing
## npc_town_roamer.gd cast (Bac Bap / garden cat Bui Mo / Cinder) and to
## game_quest_system + game_relationship_meter for talk-based quests.
##
## Invariants (blueprint):
## - Companions/NPCs are collaborators, not authorities over the player's
##   property: they cannot trigger durable mutations; all builds still route
##   through preview_confirm_commit.
## - AI surprise is opt-in: NPC quests must be accepted by the player.
## - Relationship beats are dialogue-only; no economic pressure.
## - NPC gifts go through the real gift_proposal flow (pending → accepted),
##   never direct ownership transfer.
class_name GameNpcInteraction
extends RefCounted

const NPC_IDS := ["bac_bap", "bui_mo", "cinder", "nori7"]

const NPC_PROFILES := {
	"bac_bap": {"display": "Bac Bap", "role": "workshop keeper", "greeting": "Chào bạn! Xưởng hôm nay nhiều việc lắm."},
	"bui_mo": {"display": "Bui Mo", "role": "garden cat", "greeting": "Meo~ *lăn tròn quanh chân bạn*"},
	"cinder": {"display": "Cinder", "role": "kiln worker", "greeting": "Lò vừa nóng xong. Cần nung gì không?"},
	"nori7": {"display": "Nori", "role": "town wanderer", "greeting": "Ê này, dạo này trấn yên bình quá nhỉ?"},
}

var _npc_relationship: Dictionary = {}
var _interaction_log: Array = []
var _last_talk_at: Dictionary = {}

func _init() -> void:
	_interaction_log = []
	_last_talk_at = {}
	_npc_relationship = {}

var _quest_system: RefCounted = null
var _meter: RefCounted = null
var _economy: RefCounted = null

func attach(quest_system: RefCounted, meter: RefCounted, economy: RefCounted) -> void:
	_quest_system = quest_system
	_meter = meter
	_economy = economy

func npc_ids() -> Array[String]:
	var out: Array[String] = []
	for n in NPC_IDS:
		out.append(str(n))
	return out

func profile(npc_id: String) -> Dictionary:
	if npc_id not in NPC_PROFILES:
		return {"ok": false, "reason": "unknown_npc"}
	var prof: Dictionary = NPC_PROFILES[npc_id]
	return {"ok": true, "npc_id": npc_id, "display": prof.get("display", ""), "role": prof.get("role", ""), "greeting": prof.get("greeting", "")}

## Talk interaction: greeting line + small relationship points, cooldown-gated
## per NPC to prevent farming.
func talk(npc_id: String) -> Dictionary:
	if npc_id not in NPC_PROFILES:
		return {"ok": false, "reason": "unknown_npc"}
	var prof: Dictionary = NPC_PROFILES[npc_id]
	var line: String = str(prof.get("greeting", ""))
	var rel_gain: int = 1
	if _meter != null:
		var pts: Dictionary = _meter.call("add_points", rel_gain, "talk_with_%s" % npc_id)
		if pts.get("ok", false):
			line += " (quan hệ +%d → %s)" % [rel_gain, str(pts.get("level_name", ""))]
	_interaction_log.append({"type": "talk", "npc_id": npc_id, "at": _now_iso()})
	_last_talk_at[npc_id] = _now_iso()
	return {"ok": true, "npc_id": npc_id, "line": line, "relationship_points": rel_gain}

## Pet the garden cat (specific to bui_mo): mood boost + small points.
func pet(npc_id: String) -> Dictionary:
	if npc_id != "bui_mo":
		return {"ok": false, "reason": "only_bui_mo_can_be_petted"}
	var line := "*Bui Mo kêu rừ rừ, quấn lấy tay bạn*"
	if _meter != null:
		_meter.call("add_points", 2, "pet_bui_mo")
	_meter.call("set_mood", "happy") if _meter != null else null
	_interaction_log.append({"type": "pet", "npc_id": npc_id, "at": _now_iso()})
	return {"ok": true, "npc_id": npc_id, "line": line, "mood": "happy"}

## Gift: NPC proposes a gift_proposal (pending), player must accept. The
## pending proposal carries a world_prompt with preview_required=true, so it
## still routes through preview → confirm → commit and never auto-applies.
func offer_npc_gift(npc_id: String, recipe_id: String) -> Dictionary:
	if npc_id not in NPC_PROFILES:
		return {"ok": false, "reason": "unknown_npc"}
	var recipe_cost := {}
	if _economy != null:
		recipe_cost = _economy.call("cost_for", recipe_id)
	var proposal := {
		"schema_version": "world_prompt/1.0",
		"prompt_id": "npc_gift_%s_%s_%d" % [npc_id, recipe_id, _now_epoch_ms()],
		"request_id": "",
		"operation": "gift_proposal",
		"target": recipe_id,
		"entity": {"kind": "module", "recipe": recipe_id},
		"confirmation": {"state": "pending", "held_by": "player"},
		"preview_required": true,
		"offered_by": npc_id,
		"recipe_cost": recipe_cost,
		"provenance": {"lineage": ["npc_offer", npc_id], "kind": "npc_gift"},
	}
	_interaction_log.append({"type": "gift_offer", "npc_id": npc_id, "recipe_id": recipe_id, "prompt_id": proposal["prompt_id"], "at": _now_iso()})
	return {"ok": true, "code": "gift_pending_player_accept", "proposal": proposal}

## Quest from NPC: NPC can only OFFER; player accepts via quest system (opt-in).
func npc_quest(npc_id: String, quest_id: String, title: String, objective: String, goals: Array = [], reward: Dictionary = {}) -> Dictionary:
	if npc_id not in NPC_PROFILES:
		return {"ok": false, "reason": "unknown_npc"}
	if _quest_system == null:
		return {"ok": false, "reason": "quest_system_not_attached"}
	var op := {
		"op": "offer",
		"quest_id": quest_id,
		"title": title,
		"objective_summary": objective,
		"goals": goals,
		"reward": reward,
		"relationship_gain": 3,
		"dialogue_beat": "%s vừa nhờ bạn một việc." % NPC_PROFILES[npc_id].get("display", npc_id),
	}
	var res: Dictionary = _quest_system.call("apply_op", op)
	if res.get("ok", false):
		_interaction_log.append({"type": "quest_offer", "npc_id": npc_id, "quest_id": quest_id, "at": _now_iso()})
	return res

## Daily greeting line varies by time of day (presentation data).
func greeting_for_hour(npc_id: String, hour: float) -> Dictionary:
	var p := profile(npc_id)
	if not p.get("ok", false):
		return p
	var label := "morning"
	if hour >= 12.0 and hour < 17.0:
		label = "afternoon"
	elif hour >= 17.0 and hour < 20.0:
		label = "evening"
	elif hour >= 20.0 or hour < 6.0:
		label = "night"
	var lines := {
		"bac_bap": {"morning": "Sáng rồi, mở xưởng thôi!", "afternoon": "Trưa nắng, nghỉ chút đi.", "evening": "Chiều mát, làm nốt mẻ gốm này.", "night": "Khuya rồi, mai làm tiếp nhé."},
		"bui_mo": {"morning": "Meo~ *duỗi dài*", "afternoon": "*ngủ nướng giữa nắng*", "evening": "*đuổi bướm quanh vườn*", "night": "*ngáy khe khẽ*"},
		"cinder": {"morning": "Nhóm lửa sáng nào!", "afternoon": "Lò đỏ lòm rồi đây.", "evening": "Mẻ gốm sắp ra lò.", "night": "Giữ lửa qua đêm thôi."},
		"nori7": {"morning": "Dậy sớm thế!", "afternoon": "Nắng đẹp nhỉ?", "evening": "Hoàng hôn trấn này đẹp ghê.", "night": "Sao đêm nay sáng quá trời."},
	}
	var set: Dictionary = lines.get(npc_id, {})
	return {"ok": true, "npc_id": npc_id, "time_of_day": label, "line": set.get(label, p.get("greeting", ""))}

func interaction_history(max_entries: int = 50) -> Array:
	var out: Array = []
	var total := _interaction_log.size()
	var start := maxi(0, total - int(max_entries))
	for i in range(start, total):
		out.append(_interaction_log[i].duplicate(true))
	return out

func snapshot() -> Dictionary:
	return {"npcs": npc_ids(), "recent_interactions": interaction_history(10)}

func _now_iso() -> String:
	return Time.get_datetime_string_from_system(true)

func _now_epoch_ms() -> int:
	return Time.get_ticks_msec()
