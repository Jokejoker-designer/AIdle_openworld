## UCBV-001 U5 bridge: Block Assembly state transitions → Nori-7 presentation clips.
## World Commit remains sole mutator. Animation events never commit.
## Note: no class_name for headless -s reliability.
extends Node

const _NoriScript = preload("res://scripts/modules/ucbv_001/nori7_presenter.gd")

signal bridge_event(kind: String, detail: Dictionary)

var _ba: Node = null
var _nori: Node = null
var _last_active: bool = false
var _last_stage: String = ""
var _bound: bool = false


func is_bound() -> bool:
	return _bound and _ba != null and is_instance_valid(_ba) and _nori != null and is_instance_valid(_nori)


func get_status() -> Dictionary:
	return {
		"bound": is_bound(),
		"ba_valid": _ba != null and is_instance_valid(_ba),
		"nori_valid": _nori != null and is_instance_valid(_nori),
		"last_active": _last_active,
		"last_stage": _last_stage,
		"client_world_commit": false,
		"anim_authority": false,
	}


func bind_controller(ba: Node, nori: Node) -> Dictionary:
	_unbind()
	_ba = ba
	_nori = nori
	if _ba == null or not is_instance_valid(_ba):
		return {"ok": false, "reason": "ba_missing"}
	if _nori == null or not is_instance_valid(_nori):
		return {"ok": false, "reason": "nori_missing"}
	if _ba.has_signal("preview_changed") and not _ba.preview_changed.is_connected(_on_preview_changed):
		_ba.preview_changed.connect(_on_preview_changed)
	if _ba.has_signal("commit_result") and not _ba.commit_result.is_connected(_on_commit_result):
		_ba.commit_result.connect(_on_commit_result)
	if _ba.has_signal("character_anim_trigger") and not _ba.character_anim_trigger.is_connected(_on_character_anim_trigger):
		_ba.character_anim_trigger.connect(_on_character_anim_trigger)
	_bound = true
	return {"ok": true, "bound": true, "client_world_commit": false}


func unbind() -> void:
	_unbind()


func _unbind() -> void:
	if _ba != null and is_instance_valid(_ba):
		if _ba.has_signal("preview_changed") and _ba.preview_changed.is_connected(_on_preview_changed):
			_ba.preview_changed.disconnect(_on_preview_changed)
		if _ba.has_signal("commit_result") and _ba.commit_result.is_connected(_on_commit_result):
			_ba.commit_result.disconnect(_on_commit_result)
		if _ba.has_signal("character_anim_trigger") and _ba.character_anim_trigger.is_connected(_on_character_anim_trigger):
			_ba.character_anim_trigger.disconnect(_on_character_anim_trigger)
	_ba = null
	_nori = null
	_bound = false
	_last_active = false
	_last_stage = ""


func apply_trigger(trigger: String) -> Dictionary:
	if _nori == null or not is_instance_valid(_nori):
		return {"ok": false, "reason": "nori_missing", "client_world_commit": false}
	if not _nori.has_method("apply_trigger"):
		return {"ok": false, "reason": "nori_no_apply_trigger"}
	var res: Dictionary = _nori.call("apply_trigger", trigger) as Dictionary
	res["client_world_commit"] = false
	res["via"] = "ucbv_ba_anim_bridge"
	bridge_event.emit("trigger", res)
	return res


func _on_character_anim_trigger(trigger: String) -> void:
	apply_trigger(trigger)


func _on_preview_changed(state: Dictionary) -> void:
	if not is_bound():
		return
	var active := bool(state.get("active", false))
	var stage := str(state.get("stage", ""))
	if active and not _last_active:
		# Entered preview / place — build_place path.
		apply_trigger("preview_place")
	elif not active and _last_active:
		# Left active without commit path handled here → cancel (commit uses commit_result).
		# If stage empty after cancel, play cancel.
		if str(state.get("last_entity_id", "")) == "" or not bool(state.get("proposal_submitted", false)):
			# cancel_preview clears active; commit also clears but fires commit_result first.
			pass
	_last_active = active
	_last_stage = stage
	bridge_event.emit("preview_changed", {
		"active": active,
		"stage": stage,
		"client_world_commit": false,
	})


func _on_commit_result(receipt: Dictionary) -> void:
	var status := str(receipt.get("status", ""))
	if status == "committed" or status == "idempotent_replay":
		apply_trigger("confirm")
		# Integration map: happy only after authoritative complete is observed.
		apply_trigger("happy")
	bridge_event.emit("commit_result", {
		"status": status,
		"client_world_commit": false,
		"issuer": str((receipt.get("authority", {}) as Dictionary).get("issuer", "")),
	})


## Explicit cancel path for Main / Esc single-dispatch (presentation only).
func notify_cancel() -> Dictionary:
	return apply_trigger("cancel")


## Explicit confirm path after World Commit success (optional double-safe).
func notify_confirm() -> Dictionary:
	return apply_trigger("confirm")


## Explicit preview place (Manual Build LMB / place_highlighted).
func notify_preview_place() -> Dictionary:
	return apply_trigger("preview_place")
