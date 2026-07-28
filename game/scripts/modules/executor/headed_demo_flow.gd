## Headed demo flow — stages + measurable cancel proof (Directive 24).
## CTRL-1B B1: preview cancel target, build rotate on active hologram, non-authority flags.
class_name HeadedDemoFlow
extends Node

signal flow_status(text: String)
signal preview_started(prompt_id: String)
signal flow_confirmed(prompt_id: String, result: Dictionary)
signal flow_cancelled(prompt_id: String)
signal stage_changed(stage: String)

var _pending_prompt_id: String = ""
var _active: bool = false
var _last_stage: String = ""
var _cancel_mode: bool = false  # distinct transform for cancel proof
var _preview_yaw_degrees: float = 0.0


func is_active() -> bool:
	return _active


func get_pending_prompt_id() -> String:
	return _pending_prompt_id


func get_last_runtime_stage() -> String:
	return _last_stage


func get_preview_count() -> int:
	var man := _manifestation()
	if man == null:
		return 0
	if man.has_method("get_active_prompt_ids"):
		return (man.call("get_active_prompt_ids") as PackedStringArray).size()
	return 0


func start_demo_build(cancel_mode: bool = false) -> Dictionary:
	var executor := _executor()
	if executor == null:
		flow_status.emit("Demo Build failed: Executor not ready")
		return {"ok": false, "reason": "executor_missing"}
	if _active:
		return {"ok": false, "reason": "already_active", "prompt_id": _pending_prompt_id}

	_cancel_mode = cancel_mode
	var rev := 3
	var snap := {}
	if executor.has_method("get_live_snapshot"):
		snap = executor.call("get_live_snapshot") as Dictionary
		if not snap.is_empty():
			rev = int(snap.get("world_revision", rev))
	if snap.is_empty() and executor.has_method("set_live_snapshot"):
		snap = {
			"snapshot_id": "11111111-1111-4111-8111-111111111111",
			"session_id": "session_headed_demo",
			"space_id": "home_01",
			"world_revision": rev,
			"player": {"player_id": "player_01"},
			"companion": {"companion_id": "companion_lumi"},
			"world": {"space_type": "private_reality"},
		}
		executor.call("set_live_snapshot", snap)

	var prompt := _demo_world_prompt(rev, cancel_mode)
	var prompt_id := ""
	if executor.has_method("submit_prompt"):
		prompt_id = str(executor.call("submit_prompt", prompt))
	if prompt_id.is_empty():
		flow_status.emit("Demo Build rejected")
		return {"ok": false, "reason": "submit_failed"}

	_pending_prompt_id = prompt_id
	_active = true
	_preview_yaw_degrees = 0.0
	_emit_stage("wireframe", 0.08)
	_set_router_preview_target(true)
	preview_started.emit(prompt_id)
	print(
		"[CANCEL_PROOF] preview_started id=%s count=%d cancel_mode=%s"
		% [prompt_id.substr(0, 16), get_preview_count(), str(cancel_mode)]
	)
	return {
		"ok": true,
		"prompt_id": prompt_id,
		"pipeline_stage": "preview",
		"cancel_mode": cancel_mode,
		"preview_owns_ownership": false,
		"preview_owns_collision": false,
	}


func advance_to_stage(stage: String) -> bool:
	if not _active or _pending_prompt_id.is_empty():
		return false
	var progress := 0.08
	match stage:
		"wireframe":
			progress = 0.12
		"hologram":
			progress = 0.38
		"materializing":
			progress = 0.72
		"complete":
			progress = 1.0
		_:
			return false
	_advance_manifestation(_pending_prompt_id, progress)
	_last_stage = stage
	stage_changed.emit(stage)
	_banner(stage)
	flow_status.emit("Preview: %s" % stage)
	print("[HeadedDemoFlow] runtime_stage=%s prompt=%s" % [stage, _pending_prompt_id.substr(0, 12)])
	return true


func confirm_pending() -> Dictionary:
	## Confirm emits validated commit handoff only (H-20). No client World Commit authority.
	if not _active or _pending_prompt_id.is_empty():
		return {"ok": false, "reason": "no_pending", "client_world_commit": false}
	var executor := _executor()
	if executor == null or not executor.has_method("confirm_prompt"):
		return {
			"ok": false,
			"reason": "executor_missing",
			"client_world_commit": false,
			"durable_mutation_applied": false,
		}
	var pid := _pending_prompt_id
	# Existing validated commit handoff path only — never simulate canonical World Commit.
	var result: Dictionary = executor.call("confirm_prompt", pid, "player_01") as Dictionary
	var handoff_ok := bool(result.get("ok", false))
	# Local presentation may advance to complete after handoff; collision only at complete.
	# durable_mutation_applied remains false on client (World Commit owns canonical durable).
	if handoff_ok:
		advance_to_stage("complete")
		var inst := _find_active_instance()
		if inst != null and inst.has_method("finalize_complete"):
			inst.call("finalize_complete")
		elif inst != null and inst.has_method("set_stage"):
			inst.call("set_stage", "complete")
		var man := _manifestation()
		if man != null and man.has_method("finalize_manifestation"):
			# Presentation finalize only — executor already marked handoff-only.
			man.call("finalize_manifestation", pid)
		_last_stage = "complete"
		stage_changed.emit("complete")
		flow_status.emit("Confirmed — commit handoff only (no client World Commit)")
		_banner("complete")
		flow_confirmed.emit(pid, result)
	var out := result.duplicate(true) if result is Dictionary else {}
	out["ok"] = handoff_ok
	out["prompt_id"] = pid
	out["client_world_commit"] = false
	out["durable_mutation_applied"] = false
	out["handoff_only"] = true
	out["pipeline_stage"] = str(result.get("pipeline_stage", "commit_handoff_stubbed"))
	if not out.has("commit_request"):
		out["commit_request"] = result.get("commit_request", {})
	var coll := false
	var inst2 := _find_active_instance()
	if inst2 != null and inst2.has_method("has_durable_collision"):
		coll = bool(inst2.call("has_durable_collision"))
	out["local_complete_collision"] = coll
	out["collision_only_at_complete"] = true
	_set_router_preview_target(false)
	_active = false
	_pending_prompt_id = ""
	print(
		"[HeadedDemoFlow] confirm handoff_only=true client_world_commit=false durable_mutation_applied=false collision=%s"
		% str(coll)
	)
	return out


func rotate_active_preview(degrees: float) -> bool:
	## Build-only R path — rotates hologram; no durable ownership (C1B-HK-09 / SAFE-04).
	if not _active or _pending_prompt_id.is_empty():
		return false
	var inst: Node = _find_active_instance()
	if inst == null or not inst.has_method("rotate_preview"):
		return false
	var ok := bool(inst.call("rotate_preview", degrees))
	if ok:
		_preview_yaw_degrees += degrees
		flow_status.emit("Preview rotate %.0f° (non-authority)" % degrees)
		print("[HeadedDemoFlow] rotate_preview deg=%.1f total=%.1f id=%s" % [
			degrees, _preview_yaw_degrees, _pending_prompt_id.substr(0, 12)
		])
	return ok


func _find_active_instance() -> Node:
	var tree := get_tree()
	if tree:
		for n in tree.get_nodes_in_group("manifestation_instances"):
			if n == null:
				continue
			var pid := str(n.get("prompt_id")) if "prompt_id" in n else ""
			if pid.is_empty() and n.has_meta("prompt_id"):
				pid = str(n.get_meta("prompt_id"))
			if pid == _pending_prompt_id:
				return n
		# Any non-finalized preview if id match failed (single active demo).
		for n in tree.get_nodes_in_group("manifestation_instances"):
			if n != null and n.has_method("is_finalized") and not bool(n.call("is_finalized")):
				if n.has_method("is_cancelled") and bool(n.call("is_cancelled")):
					continue
				return n
	return null


func get_preview_yaw_degrees() -> float:
	return _preview_yaw_degrees


func cancel_pending() -> Dictionary:
	if not _active or _pending_prompt_id.is_empty():
		return {"ok": false, "reason": "no_pending"}
	var executor := _executor()
	var pid := _pending_prompt_id
	var before := get_preview_count()
	var had_collision := false
	var man := _manifestation()
	if man != null and man.has_method("has_durable_collision"):
		had_collision = bool(man.call("has_durable_collision", pid))
	print(
		"[CANCEL_PROOF] before cancel id=%s preview_count=%d durable_collision=%s"
		% [pid.substr(0, 16), before, str(had_collision)]
	)
	if executor != null and executor.has_method("cancel_prompt"):
		executor.call("cancel_prompt", pid, "player_cancel")
	# Ensure manifestation free even if executor path missed
	if man != null and man.has_method("cancel_manifestation"):
		if man.has_method("get_active_prompt_ids"):
			var ids: PackedStringArray = man.call("get_active_prompt_ids") as PackedStringArray
			if ids.has(pid):
				man.call("cancel_manifestation", pid, "player_cancel")
	var after := get_preview_count()
	var still_has := false
	if man != null and man.has_method("get_manifestation_stage"):
		still_has = not str(man.call("get_manifestation_stage", pid)).is_empty()
	# Entity for THIS cancel id must be gone; a prior confirmed object may remain (count can be >0).
	var entity_absent := not still_has
	print(
		"[CANCEL_PROOF] after cancel id=%s preview_count=%d entity_absent=%s collision_before=%s"
		% [pid.substr(0, 16), after, str(entity_absent), str(had_collision)]
	)
	if not entity_absent:
		print("[CANCEL_PROOF] FAIL residual_cancel_entity")
	else:
		print("[CANCEL_PROOF] PASS cancel_entity_cleared count_after=%d" % after)
	_last_stage = "cancelled"
	stage_changed.emit("cancelled")
	flow_status.emit("Cancelled — preview cleared")
	flow_cancelled.emit(pid)
	_banner("")
	_set_router_preview_target(false)
	_active = false
	_pending_prompt_id = ""
	# Post-cancel: no durable entity / collision residual for this prompt (H-20).
	var residual_collision := false
	if man != null and man.has_method("has_durable_collision"):
		residual_collision = bool(man.call("has_durable_collision", pid))
	var inst_left := _find_active_instance()
	if inst_left != null and str(inst_left.get("prompt_id")) == pid:
		if inst_left.has_method("has_durable_collision"):
			residual_collision = residual_collision or bool(inst_left.call("has_durable_collision"))
	return {
		"ok": true,
		"prompt_id": pid,
		"cancelled": true,
		"preview_count_before": before,
		"preview_count_after": after,
		"entity_absent": entity_absent,
		"orphan_safe": entity_absent and not residual_collision,
		"preview_owns_ownership": false,
		"preview_owns_collision": false,
		"durable_entity_left": not entity_absent,
		"durable_collision_left": residual_collision,
		"client_world_commit": false,
	}


func _autoload_node(node_name: String) -> Node:
	## SceneTree-root relative lookup — never absolute "/root/..." (H1-CODEX-F01).
	if not is_inside_tree():
		return null
	var tree := get_tree()
	if tree == null:
		return null
	var r := tree.root
	if r == null:
		return null
	var direct := r.get_node_or_null(node_name)
	if direct != null:
		return direct
	for c in r.get_children():
		if str(c.name) == node_name:
			return c
	return null


func _set_router_preview_target(active: bool) -> void:
	var router := _autoload_node("ControlContextRouter")
	if router != null and router.has_method("set_cancel_target"):
		router.call("set_cancel_target", "preview_hologram", active)


func _demo_world_prompt(expected_rev: int, cancel_mode: bool) -> Dictionary:
	# Distinct transform for cancel-proof captures so crop x=550..900 changes.
	var tx := 6.5 if cancel_mode else 1.5
	var ty := -1.0 if cancel_mode else -3.5
	var eid := "entity_cancel_preview_box" if cancel_mode else "entity_headed_demo_house"
	return {
		"schema_version": "1.0.0",
		"prompt_id": "headed-demo-%s" % str(Time.get_ticks_msec()),
		"intent": "build_structure",
		"source": "headed_demo_local",
		"player_id": "player_01",
		"companion_id": "companion_lumi",
		"session_id": "session_headed_demo",
		"target": {
			"space_type": "private_reality",
			"space_id": "home_01",
			"expected_world_revision": expected_rev,
		},
		"entity": {
			"entity_id": eid,
			"kind": "modular_structure_2_5d",
			"recipe_id": "cozy_house_small",
			"display_name": "Cancel Preview Box" if cancel_mode else "Demo Cozy House",
			"transform": {"x": tx, "y": ty, "elevation": 0.0, "yaw_deg": 0.0},
			"bounds": {"x": 3.5, "y": 3.0, "z": 3.5},
		},
		"transform": {"x": tx, "y": ty, "elevation": 0.0, "yaw_deg": 0.0},
		"geometry": {
			"size": {"x": 3.5, "y": 3.0, "z": 3.5},
			"recipe_id": "cozy_house_small",
			"position": {"x": tx, "y": 0.0, "z": ty},
		},
		"style_profile": {"base_concept": "cozy_cyber_pixel_2_5d"},
		"confirmation": {
			"preview_required": true,
			"stages": ["wireframe", "hologram", "materializing", "complete"],
		},
		"provenance": {
			"generator": "headed_demo_flow",
			"note": "local deterministic demo — not live LLM",
			"cancel_mode": cancel_mode,
		},
	}


func _executor() -> Node:
	if ModuleRegistry == null or not ModuleRegistry.has_module(AIdleConstants.MODULE_EXECUTOR):
		return null
	var m: Node = ModuleRegistry.get_module(AIdleConstants.MODULE_EXECUTOR)
	if m != null and m.has_method("is_stub") and bool(m.call("is_stub")):
		return null
	return m


func _manifestation() -> Node:
	if ModuleRegistry == null or not ModuleRegistry.has_module(AIdleConstants.MODULE_VOXEL):
		return null
	var m: Node = ModuleRegistry.get_module(AIdleConstants.MODULE_VOXEL)
	if m != null and m.has_method("is_stub") and bool(m.call("is_stub")):
		return null
	return m


func _advance_manifestation(prompt_id: String, progress: float) -> void:
	var man := _manifestation()
	if man == null:
		return
	if man.has_method("update_construction_progress"):
		man.call("update_construction_progress", prompt_id, progress)


func _emit_stage(stage: String, progress: float) -> void:
	_advance_manifestation(_pending_prompt_id, progress)
	_last_stage = stage
	stage_changed.emit(stage)
	_banner(stage)
	flow_status.emit("Preview: %s" % stage)
	print("[HeadedDemoFlow] runtime_stage=%s prompt=%s" % [stage, _pending_prompt_id.substr(0, 12)])


func _banner(stage: String) -> void:
	for n in get_tree().get_nodes_in_group("g3_starter_realm"):
		if n != null and n.has_method("show_preview_banner"):
			n.call("show_preview_banner", stage)
		if n != null and n.has_method("set_status") and not stage.is_empty():
			n.call("set_status", "Building: %s" % stage)
