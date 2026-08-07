## Quest system for the AIdle cozy 2.5D vertical slice.
## Implements the AGM decision `quest_operations` allowlist (Blueprint 08):
##   offer | update_objective | mark_ready | complete | fail | cancel
## while extending the executor's soft state with a real FSM, goal conditions,
## rewards and a player-facing acceptance flow.
##
## Contract invariants:
## - Quest operations never perform direct durable mutations (build proposals
##   stay on the preview_confirm_commit path).
## - Relationship level unlocks dialogue/story beats, never economic pressure.
##   Rewards therefore carry story/dialogue beats and optional resources, but
##   resources are granted through the economy module, never silently.
## - The player must explicitly accept an offer (opt-in surprise).
class_name GameQuestSystem
extends RefCounted

const STATE_ORDER := ["offered", "accepted", "in_progress", "completed", "failed", "cancelled"]
const ALLOWED_TRANSITIONS := {
	"offered": ["accepted", "cancelled"],
	"accepted": ["in_progress", "cancelled"],
	"in_progress": ["completed", "failed", "cancelled"],
}

const DEFAULT_GOAL_KINDS := ["collect", "build", "talk", "visit", "wait", "spend"]

var _quests: Dictionary = {}
var _active_ids: Array[String] = []
var _pending_acceptance: Array[String] = []

func quest_ids() -> Array[String]:
	var out: Array[String] = []
	for qid in _quests.keys():
		out.append(str(qid))
	return out

func list_quests() -> Array:
	var out: Array = []
	for qid in quest_ids():
		out.append(quest_summary(str(qid)))
	return out

func quest_summary(quest_id: String) -> Dictionary:
	var q: Variant = _quests.get(quest_id, null)
	if q == null:
		return {"ok": false, "code": "unknown_quest"}
	var rec: Dictionary = q
	return {
		"ok": true,
		"quest_id": quest_id,
		"state": rec.get("state", "unknown"),
		"title": rec.get("title", ""),
		"objective_summary": rec.get("objective_summary", ""),
		"goals": rec.get("goals", []),
		"accepted": bool(rec.get("accepted", false)),
		"progress": rec.get("progress", {}),
		"relationship_gain": int(rec.get("relationship_gain", 0)),
		"reward": rec.get("reward", {}),
		"offered_at": rec.get("offered_at", ""),
		"updated_at": rec.get("updated_at", ""),
	}

## AGM-style op dispatcher. Mirrors decision_executor._apply_quest_op but adds
## the missing mechanics: acceptance, goal tracking, rewards.
func apply_op(op: Dictionary) -> Dictionary:
	var op_name := str(op.get("op", "")).strip_edges()
	match op_name:
		"offer":
			return offer_quest(op)
		"update_objective":
			return update_objective(op)
		"mark_ready":
			return mark_ready(op)
		"accept":
			return accept_quest(op)
		"complete":
			return complete_quest(op)
		"fail":
			return fail_quest(op)
		"cancel":
			return cancel_quest(op)
		"advance_goal":
			return advance_goal(op)
		"force_complete":
			return force_complete(op)
	return {"ok": false, "reason": "unknown_action: quest op %s" % op_name}

## `offer` — quest enters soft state, awaits player acceptance (opt-in).
func offer_quest(op: Dictionary) -> Dictionary:
	var quest_id := str(op.get("quest_id", "")).strip_edges()
	if quest_id.is_empty():
		return {"ok": false, "reason": "quest_id required"}
	if _quests.has(quest_id):
		var existing: Dictionary = _quests[quest_id]
		if str(existing.get("state", "")) not in ["completed", "failed", "cancelled"]:
			return {"ok": false, "reason": "quest %s is still active (state=%s)" % [quest_id, existing.get("state", "")]}
	var title := str(op.get("title", "")).strip_edges()
	var objective_summary := str(op.get("objective_summary", "")).strip_edges()
	if title.is_empty() or objective_summary.is_empty():
		return {"ok": false, "reason": "offer requires title and objective_summary"}
	var goals := _normalize_goals(op.get("goals", []))
	_quests[quest_id] = {
		"state": "offered",
		"quest_id": quest_id,
		"title": title,
		"objective_summary": objective_summary,
		"goals": goals,
		"accepted": false,
		"progress": _empty_progress(goals),
		"reward": op.get("reward", {}).duplicate(true) if op.get("reward") is Dictionary else {},
		"relationship_gain": int(op.get("relationship_gain", 1)),
		"offered_at": _now_iso(),
		"updated_at": _now_iso(),
	}
	_pending_acceptance.append(quest_id)
	return {"ok": true, "state": "offered", "quest_id": quest_id, "awaiting_acceptance": true}

## Player explicitly accepts. Relationship level can unlock the offer but the
## offer itself is never forced on the player.
func accept_quest(op: Dictionary) -> Dictionary:
	var quest_id := str(op.get("quest_id", "")).strip_edges()
	if quest_id.is_empty():
		return {"ok": false, "reason": "quest_id required"}
	var q: Variant = _quests.get(quest_id, null)
	if q == null:
		return {"ok": false, "reason": "unknown quest %s" % quest_id}
	var rec: Dictionary = q
	if rec.get("state") != "offered":
		return {"ok": false, "reason": "cannot accept quest in state %s" % str(rec.get("state", ""))}
	if not bool(_pending_acceptance.has(quest_id)):
		return {"ok": false, "reason": "quest %s not pending acceptance" % quest_id}
	rec["state"] = "accepted"
	rec["accepted"] = true
	rec["updated_at"] = _now_iso()
	if not _active_ids.has(quest_id):
		_active_ids.append(quest_id)
	_pending_acceptance.erase(quest_id)
	return {"ok": true, "state": "accepted", "quest_id": quest_id}

func update_objective(op: Dictionary) -> Dictionary:
	var quest_id := str(op.get("quest_id", "")).strip_edges()
	var new_summary := str(op.get("objective_summary", "")).strip_edges()
	if quest_id.is_empty() or new_summary.is_empty():
		return {"ok": false, "reason": "update_objective requires quest_id and objective_summary"}
	var q: Variant = _quests.get(quest_id, null)
	if q == null:
		return {"ok": false, "reason": "unknown quest %s" % quest_id}
	var rec: Dictionary = q
	if str(rec.get("state", "")) in ["completed", "failed", "cancelled"]:
		return {"ok": false, "reason": "quest is terminal (state=%s)" % str(rec.get("state", ""))}
	rec["objective_summary"] = new_summary
	if op.get("goals") is Array:
		rec["goals"] = _normalize_goals(op.get("goals"))
		rec["progress"] = _empty_progress(rec["goals"])
	rec["updated_at"] = _now_iso()
	return {"ok": true, "state": rec.get("state"), "quest_id": quest_id}

func mark_ready(op: Dictionary) -> Dictionary:
	## Convenience: player signals they are acting on the quest now.
	var quest_id := str(op.get("quest_id", "")).strip_edges()
	var q: Variant = _quests.get(quest_id, null)
	if q == null:
		return {"ok": false, "reason": "unknown quest %s" % quest_id}
	var rec: Dictionary = q
	if str(rec.get("state", "")) == "offered":
		var accept_res := accept_quest({"op": "accept", "quest_id": quest_id})
		if not accept_res.get("ok", false):
			return accept_res
		rec = _quests[quest_id]
	if rec.get("state") != "accepted":
		return {"ok": false, "reason": "cannot mark ready in state %s" % str(rec.get("state", ""))}
	rec["state"] = "in_progress"
	rec["updated_at"] = _now_iso()
	return {"ok": true, "state": "in_progress", "quest_id": quest_id}

## Advance a goal by (kind, target). `advance_goal {quest_id, goal_kind, target}`
func advance_goal(op: Dictionary) -> Dictionary:
	var quest_id := str(op.get("quest_id", "")).strip_edges()
	var kind := str(op.get("goal_kind", "")).strip_edges()
	var target := str(op.get("target", "")).strip_edges()
	var count := int(op.get("count", 1))
	if quest_id.is_empty() or kind.is_empty():
		return {"ok": false, "reason": "advance_goal requires quest_id and goal_kind"}
	var q: Variant = _quests.get(quest_id, null)
	if q == null:
		return {"ok": false, "reason": "unknown quest %s" % quest_id}
	var rec: Dictionary = q
	if str(rec.get("state", "")) not in ["in_progress", "accepted"]:
		# Cozy opt-in UX: advancing an accepted/accepted quest activates it.
		return {"ok": false, "reason": "quest not accepted yet (state=%s); player must accept first" % str(rec.get("state", ""))}
	if rec.get("state") == "accepted":
		# Auto-activate on first goal progress (mark_ready optional convenience).
		rec["state"] = "in_progress"
		rec["updated_at"] = _now_iso()
		if not _active_ids.has(quest_id):
			_active_ids.append(quest_id)
		_pending_acceptance.erase(quest_id)
	elif rec.get("state") != "in_progress":
		return {"ok": false, "reason": "quest not in_progress (state=%s)" % str(rec.get("state", ""))}
	var progress: Dictionary = rec.get("progress", {})
	var goals: Array = rec.get("goals", [])
	var matched := false
	for g in goals:
		var gd: Dictionary = g
		if str(gd.get("kind", "")) == kind and (target.is_empty() or str(gd.get("target", "")) == target):
			var key := "%s:%s" % [kind, target]
			var current := int(progress.get(key, 0))
			var need := int(gd.get("need", 1))
			progress[key] = mini(current + count, need)
			matched = true
			break
	if not matched:
		return {"ok": false, "reason": "no goal matches kind=%s target=%s" % [kind, target]}
	rec["progress"] = progress
	rec["updated_at"] = _now_iso()
	var goals_met := _goals_met(goals, progress)
	if goals_met:
		var complete_res := complete_quest({"op": "complete", "quest_id": quest_id})
		complete_res["goals_met"] = true
		return complete_res
	return {"ok": true, "state": "in_progress", "progress": progress.duplicate(true), "goals_met": false}

func complete_quest(op: Dictionary) -> Dictionary:
	var quest_id := str(op.get("quest_id", "")).strip_edges()
	var q: Variant = _quests.get(quest_id, null)
	if q == null:
		return {"ok": false, "reason": "unknown quest %s" % quest_id}
	var rec: Dictionary = q
	if rec.get("state") != "in_progress":
		if rec.get("state") == "completed":
			return {"ok": false, "reason": "quest already completed (idempotent-noop-for-display)"}
		return {"ok": false, "reason": "cannot complete quest in state %s" % str(rec.get("state", ""))}
	var goals: Array = rec.get("goals", [])
	if not _goals_met(goals, rec.get("progress", {})):
		return {"ok": false, "reason": "goals not met yet (cannot force from state=%s); use advance_goal" % str(rec.get("state", ""))}
	rec["state"] = "completed"
	rec["completed_at"] = _now_iso()
	rec["updated_at"] = _now_iso()
	_active_ids.erase(quest_id)
	var reward: Dictionary = rec.get("reward", {})
	var relationship_gain: int = int(rec.get("relationship_gain", 1))
	return {
		"ok": true,
		"state": "completed",
		"quest_id": quest_id,
		"reward": reward.duplicate(true),
		"relationship_gain": relationship_gain,
		"dialogue_beat": rec.get("dialogue_beat", ""),
	}

## Player may force-complete an in-progress quest (cozy design: quests never
## punish), but force-completes grant reduced relationship gain.
func force_complete(op: Dictionary) -> Dictionary:
	var quest_id := str(op.get("quest_id", "")).strip_edges()
	var q: Variant = _quests.get(quest_id, null)
	if q == null:
		return {"ok": false, "reason": "unknown quest %s" % quest_id}
	var rec: Dictionary = q
	if rec.get("state") == "accepted":
		rec["state"] = "in_progress"
		rec["updated_at"] = _now_iso()
	elif rec.get("state") != "in_progress":
		return {"ok": false, "reason": "force_complete only valid for accepted/in_progress"}
	rec["state"] = "completed"
	rec["completed_at"] = _now_iso()
	rec["updated_at"] = _now_iso()
	_active_ids.erase(quest_id)
	var rel := int(rec.get("relationship_gain", 1))
	rel = maxi(0, rel / 2)
	return {"ok": true, "state": "completed", "quest_id": quest_id, "relationship_gain": rel, "force": true}

func fail_quest(op: Dictionary) -> Dictionary:
	var quest_id := str(op.get("quest_id", "")).strip_edges()
	var q: Variant = _quests.get(quest_id, null)
	if q == null:
		return {"ok": false, "reason": "unknown quest %s" % quest_id}
	var rec: Dictionary = q
	if rec.get("state") == "accepted":
		rec["state"] = "in_progress"
		rec["updated_at"] = _now_iso()
	elif rec.get("state") != "in_progress":
		return {"ok": false, "reason": "cannot fail quest in state %s" % str(rec.get("state", ""))}
	rec["state"] = "failed"
	rec["updated_at"] = _now_iso()
	_active_ids.erase(quest_id)
	return {"ok": true, "state": "failed", "quest_id": quest_id}

func cancel_quest(op: Dictionary) -> Dictionary:
	var quest_id := str(op.get("quest_id", "")).strip_edges()
	var q: Variant = _quests.get(quest_id, null)
	if q == null:
		return {"ok": false, "reason": "unknown quest %s" % quest_id}
	var rec: Dictionary = q
	if str(rec.get("state", "")) not in ["offered", "accepted", "in_progress"]:
		return {"ok": false, "reason": "cannot cancel quest in state %s" % str(rec.get("state", ""))}
	rec["state"] = "cancelled"
	rec["updated_at"] = _now_iso()
	_pending_acceptance.erase(quest_id)
	_active_ids.erase(quest_id)
	return {"ok": true, "state": "cancelled", "quest_id": quest_id}

## Pending offers the UI should surface for player opt-in.
func pending_acceptance_ids() -> Array[String]:
	var out: Array[String] = []
	for qid in _pending_acceptance:
		out.append(str(qid))
	return out

func active_quest_ids() -> Array[String]:
	var out: Array[String] = []
	for qid in _active_ids:
		out.append(str(qid))
	return out

## Snapshot slice for the AGM World State Snapshot.
func snapshot(max_active: int = 12) -> Dictionary:
	var active: Array = []
	for qid in active_quest_ids():
		active.append(quest_summary(qid))
		if active.size() >= max_active:
			break
	return {"quests": active, "pending_acceptance": pending_acceptance_ids()}

func _normalize_goals(goals: Variant) -> Array:
	var out: Array = []
	if not (goals is Array):
		return out
	for g in goals:
		if not (g is Dictionary):
			continue
		var kind := str(g.get("kind", "")).strip_edges()
		if kind not in DEFAULT_GOAL_KINDS:
			kind = "collect"
		out.append({
			"kind": kind,
			"target": str(g.get("target", "")),
			"need": maxi(1, int(g.get("need", 1))),
		})
	return out

func _empty_progress(goals: Array) -> Dictionary:
	var progress := {}
	for g in goals:
		var gd: Dictionary = g
		var key := "%s:%s" % [str(gd.get("kind", "")), str(gd.get("target", ""))]
		progress[key] = 0
	return progress

func _goals_met(goals: Array, progress: Dictionary) -> bool:
	if goals.is_empty():
		return true
	for g in goals:
		var gd: Dictionary = g
		var key := "%s:%s" % [str(gd.get("kind", "")), str(gd.get("target", ""))]
		if int(progress.get(key, 0)) < int(gd.get("need", 1)):
			return false
	return true

func _now_iso() -> String:
	return Time.get_datetime_string_from_system(true)
