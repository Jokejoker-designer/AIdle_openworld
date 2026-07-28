## P2E-001 Block Assembly controller — select, snap, preview, cancel, confirm via World Commit.
## Client never claims commit success; only WorldAuthorityLocal issues receipts.
## Preview is non-durable; undo is compensation through authority, not SceneTree delete.
class_name BlockAssemblyController
extends Node

const _C = preload("res://scripts/modules/block_assembly/block_assembly_constants.gd")
const _Gate = preload("res://scripts/modules/block_assembly/block_catalog_gate.gd")
const _Sockets = preload("res://scripts/modules/block_assembly/block_socket_rules.gd")
const _Math = preload("res://scripts/modules/block_assembly/block_placement_math.gd")
const _Preview = preload("res://scripts/modules/block_assembly/block_preview_entity.gd")
const _Builder = preload("res://scripts/modules/block_assembly/block_world_prompt_builder.gd")
const _AuthServer = preload("res://scripts/modules/network/world_authority_local.gd")
const _AuthClient = preload("res://scripts/modules/network/authority_client.gd")
const _Canon = preload("res://scripts/modules/persist/canonical_json.gd")

signal preview_changed(state: Dictionary)
signal commit_result(receipt: Dictionary)
signal status_message(text: String)
signal picker_changed(state: Dictionary)
signal hud_state_changed(state: Dictionary)
## U5 presentation-only: Nori-7 / character clips. Never issues World Commit.
signal character_anim_trigger(trigger: String)

var space_id: String = _C.SPACE_ID_DEFAULT
var player_id: String = "player_01"
var actor_type: String = "player"
var world_profile: String = "cozy_cyber_pixel"
var client_id: String = "block_assembly_client"

var _gate: RefCounted
var _sockets: RefCounted
var _server: RefCounted
var _client: RefCounted
var _counter: int = 0

var _active: bool = false
var _module_id: String = ""
var _material_slot: String = "structure"
var _p1e_material: String = "MAT_CozyStoneWarm"
var _raw_x: float = 0.0
var _raw_y: float = 0.0
var _raw_elev: float = 0.0
var _raw_rot: float = 0.0
var _snap_enabled: bool = true
var _placement: Dictionary = {}
var _stage: String = "wireframe"
var _request_id: String = ""
var _prompt_id: String = ""
var _idempotency_key: String = ""
var _payload_fp: String = ""
var _payload: Dictionary = {}
var _preview: Node3D = null
var _proposal_submitted: bool = false
var _last_receipt: Dictionary = {}
var _last_entity_id: String = ""
var _committed_entities: Array = []  # {entity_id, request_id, node}
var _last_status: String = ""
var _last_reject: Dictionary = {}
var _session_ready: bool = false

## Local idempotency: bind fingerprint only after successful authority COMMIT (not intermediate submit).
## Pending/invalid attempts never freeze a key against a later corrected payload (F06).
var _local_idem: Dictionary = {}  # key -> fingerprint (committed only)
var _committed_keys: Dictionary = {}  # key -> true after durable commit
var _hold_idempotency_key: bool = false  # test/attack helper: do not remint key on next submit

## Player-facing allowlisted module picker (F03) — cycled via InputMap actions, not API injection.
var _picker_ids: PackedStringArray = PackedStringArray()
var _picker_index: int = 0
var _picker_open: bool = false

## Manual Build cursor-led placement (H1-HUMAN-BUILD-01) — preview only, never canonical.
var _manual_build: bool = false
var _cursor_follow: bool = false
var _cursor_hit_valid: bool = false
var _cursor_raw_x: float = 0.0
var _cursor_raw_y: float = 0.0
var _last_screen_pos: Vector2 = Vector2.ZERO
var _awaiting_place_click: bool = false
## H1-CODEX-MB-F06: Manual Build confirm requires one intentional valid LMB/place first.
var _intentional_place_done: bool = false

## C2: categorized catalog + Delete red-X mode (authority compensation only).
const _UcbvKit = preload("res://scripts/modules/ucbv_001/ucbv_block_kit_loader.gd")
var _kit: RefCounted = null
var _category_filter: String = ""  # empty = all
var _last_rotate_result: Dictionary = {}
var _last_elevate_result: Dictionary = {}
var _delete_mode: bool = false
var _delete_target_entity_id: String = ""
var _delete_target_index: int = -1
var _delete_pending_confirm: bool = false
var _delete_cursor_label: String = ""


func _init() -> void:
	_ensure_catalogs()


func _ready() -> void:
	_ensure_catalogs()
	_ensure_picker_list()


func _exit_tree() -> void:
	## F02: release preview resources before tree teardown (avoid RendererRD RID leaks).
	dispose_all_previews()


func _ensure_catalogs() -> void:
	if _gate == null:
		_gate = _Gate.new()
	if _sockets == null:
		_sockets = _Sockets.new()
	if _gate.has_method("ensure_loaded"):
		_gate.call("ensure_loaded")
	if _sockets.has_method("ensure_loaded"):
		_sockets.call("ensure_loaded")


func _ensure_picker_list() -> void:
	_ensure_catalogs()
	if _picker_ids.is_empty() and _gate != null and _gate.has_method("get_allowlisted_module_ids"):
		_picker_ids = _gate.call("get_allowlisted_module_ids") as PackedStringArray
	if _picker_index < 0 or _picker_index >= _picker_ids.size():
		_picker_index = 0


func bind_local_authority(seed_revision: int = 0) -> Dictionary:
	_ensure_catalogs()
	_server = _AuthServer.new(space_id, seed_revision)
	_client = _AuthClient.new(client_id, _server)
	var conn: Dictionary = _client.call("connect_client", player_id, actor_type) as Dictionary
	_session_ready = bool(conn.get("ok", false))
	return conn


func is_session_ready() -> bool:
	return _session_ready and _client != null


func get_world_revision() -> int:
	if _server == null:
		return -1
	return int(_server.call("world_revision"))


func get_active_state() -> Dictionary:
	return {
		"active": _active,
		"module_id": _module_id,
		"stage": _stage,
		"placement": _placement.duplicate(true),
		"request_id": _request_id,
		"prompt_id": _prompt_id,
		"snap_enabled": _snap_enabled,
		"collision": _preview != null and _preview.has_method("has_collision") and bool(_preview.call("has_collision")),
		"navigation": _preview != null and _preview.has_method("has_navigation") and bool(_preview.call("has_navigation")),
		"proposal_submitted": _proposal_submitted,
		"last_entity_id": _last_entity_id,
		"committed_count": _committed_entities.size(),
		"validity": get_validity(),
		"picker": get_picker_state(),
		"hud": get_hud_state(),
		"confirm_enabled": can_confirm(),
		"cancel_enabled": can_cancel(),
		"manual_build": _manual_build,
		"manual_cursor_follow": _cursor_follow,
		"cursor_hit_valid": _cursor_hit_valid,
		"cursor_raw": {"x": _cursor_raw_x, "y": _cursor_raw_y},
		"intentional_place_done": _intentional_place_done,
		"delete_mode": _delete_mode,
		"delete_target_entity_id": _delete_target_entity_id,
		"delete_cursor": "red_x" if _delete_mode else "",
		"preview_only": true,
		"client_world_commit": false,
	}


func get_picker_state() -> Dictionary:
	_ensure_picker_list()
	var mid := ""
	if _picker_ids.size() > 0:
		mid = _picker_ids[_picker_index]
	var display := mid
	var category := ""
	_ensure_kit()
	if _kit != null:
		if _kit.has_method("get_display_name"):
			display = str(_kit.call("get_display_name", mid))
		if _kit.has_method("get_category"):
			category = str(_kit.call("get_category", mid))
	return {
		"open": _picker_open or _is_build_context(),
		"index": _picker_index,
		"count": _picker_ids.size(),
		"highlighted_module_id": mid,
		"highlighted_display_name": display,
		"highlighted_category": category,
		"category_filter": _category_filter,
		"active_module_id": _module_id,
		"source": "inputmap_categorized_catalog_picker",
		"catalog_full_28": _picker_ids.size() >= 28,
	}


func _ensure_kit() -> void:
	if _kit == null:
		_kit = _UcbvKit.new()
		if _kit.has_method("ensure_loaded"):
			_kit.call("ensure_loaded")


func get_catalog_ui_state() -> Dictionary:
	## C2: categorized selector payload (name + preview meta) for full 28-module catalog.
	_ensure_picker_list()
	_ensure_kit()
	var entries: Array = []
	if _kit != null and _kit.has_method("get_catalog_entries"):
		entries = _kit.call("get_catalog_entries") as Array
	else:
		for mid in _picker_ids:
			entries.append({"module_id": mid, "display_name": mid, "category": ""})
	var categories: PackedStringArray = PackedStringArray()
	if _kit != null and _kit.has_method("get_categories"):
		categories = _kit.call("get_categories") as PackedStringArray
	var filtered: Array = []
	for e in entries:
		if not (e is Dictionary):
			continue
		var ed: Dictionary = e
		if not _category_filter.is_empty() and str(ed.get("category", "")) != _category_filter:
			continue
		filtered.append(ed)
	var hi := ""
	if _picker_ids.size() > 0:
		hi = _picker_ids[_picker_index]
	return {
		"module_count": _picker_ids.size(),
		"categories": categories,
		"category_filter": _category_filter,
		"entries": filtered if not _category_filter.is_empty() else entries,
		"all_entries": entries,
		"highlighted_module_id": hi,
		"highlighted_index": _picker_index,
		"source": "categorized_runtime_catalog",
		"period_only_cycle": false,
		"single_module_only": false,
	}


func set_category_filter(category: String) -> Dictionary:
	_ensure_picker_list()
	_category_filter = category.strip_edges()
	if _category_filter.is_empty():
		hud_state_changed.emit(get_hud_state())
		return {"ok": true, "category_filter": "", "catalog": get_catalog_ui_state()}
	_ensure_kit()
	# Jump picker to first module in category.
	for i in _picker_ids.size():
		var mid := _picker_ids[i]
		var cat := ""
		if _kit != null and _kit.has_method("get_category"):
			cat = str(_kit.call("get_category", mid))
		if cat == _category_filter:
			_picker_index = i
			break
	picker_changed.emit(get_picker_state())
	hud_state_changed.emit(get_hud_state())
	return {"ok": true, "category_filter": _category_filter, "catalog": get_catalog_ui_state()}


func select_catalog_index(index: int) -> Dictionary:
	## Direct catalog row selection (UI) — still InputMap-driven place/confirm after.
	_ensure_picker_list()
	if index < 0 or index >= _picker_ids.size():
		return _reject("picker_index_oob", "catalog index out of range")
	_picker_index = index
	_picker_open = true
	var st := get_picker_state()
	picker_changed.emit(st)
	hud_state_changed.emit(get_hud_state())
	return {"ok": true, "picker": st, "via": "catalog_select"}


func select_catalog_module(module_id: String) -> Dictionary:
	_ensure_picker_list()
	var idx := _picker_ids.find(module_id)
	if idx < 0:
		return _reject("unknown_module", "module not in allowlisted catalog: %s" % module_id)
	return select_catalog_index(idx)


func get_hud_state() -> Dictionary:
	## Plain-language BA HUD surface (F05) — not a diagnostic wall.
	var validity := get_validity() if _active else {"ok": false, "reason": "Aim cursor, then LMB to place preview"}
	var reason := str(validity.get("reason", ""))
	if not bool(validity.get("ok", false)) and _last_reject.has("reason"):
		if not _active:
			reason = "Aim on ground · LMB places preview (never commits)"
		elif str(_last_reject.get("code", "")) != "":
			reason = _plain_reject_reason(_last_reject)
	if _manual_build and _active and not _cursor_hit_valid:
		reason = "Invalid surface — move cursor onto allowed build ground"
	if _delete_mode:
		reason = "Delete red-X · LMB select committed owned · Enter confirm · Esc/RMB exit"
		if not _delete_target_entity_id.is_empty():
			reason = "Delete target %s — Enter confirms World Commit compensation" % _delete_target_entity_id
	var rot := float(_placement.get("rotation_deg", 0.0)) if _active else 0.0
	var elev := float(_placement.get("elevation", 0.0)) if _active else 0.0
	var picker := get_picker_state()
	var mod_id := _module_id if not _module_id.is_empty() else str(picker.get("highlighted_module_id", "—"))
	var mod_display := str(picker.get("highlighted_display_name", mod_id))
	var mod_cat := str(picker.get("highlighted_category", ""))
	return {
		"context": "Delete" if _delete_mode else ("Build" if _is_build_context() else "Exploration"),
		"module": mod_id,
		"module_display_name": mod_display,
		"module_category": mod_cat,
		"highlighted": str(picker.get("highlighted_module_id", "—")),
		"highlighted_display_name": mod_display,
		"catalog_count": int(picker.get("count", 0)),
		"snap": "On (0.5 m / 0.25 m / 15°)" if _snap_enabled else "Off",
		"validity": "Ready" if bool(validity.get("ok", false)) and (_cursor_hit_valid or not _manual_build) else "Not ready",
		"validity_reason": reason,
		"rotation": "%d°" % int(round(rot)),
		"elevation": "%.2f m" % elev,
		"elevation_label": "Lift (PgUp/PgDn)",
		"elevation_action": "build_elevation_up/down",
		"rotation_label": "Rotate (Q/R)",
		"stage": _stage if _active else "—",
		"confirm_enabled": can_confirm() if not _delete_mode else _delete_pending_confirm and not _delete_target_entity_id.is_empty(),
		"cancel_enabled": can_cancel() or _delete_mode,
		"confirm_label": "Confirm delete" if _delete_mode else ("Confirm" if can_confirm() else "Confirm (disabled)"),
		"cancel_label": "Exit delete" if _delete_mode else ("Cancel preview" if can_cancel() else "Cancel (nothing active)"),
		"manual_build": _manual_build,
		"manual_cursor_follow": _cursor_follow,
		"cursor_hit_valid": _cursor_hit_valid,
		"intentional_place_done": _intentional_place_done,
		"delete_mode": _delete_mode,
		"delete_target_entity_id": _delete_target_entity_id,
		"delete_cursor": "red_x" if _delete_mode else "",
		"last_rotate_reason": str(_last_rotate_result.get("reason", "")),
		"last_elevate_reason": str(_last_elevate_result.get("reason", "")),
	}


func can_confirm() -> bool:
	if _delete_mode:
		return _session_ready and not _delete_target_entity_id.is_empty() and _delete_pending_confirm
	if not _active or not _session_ready:
		return false
	if _manual_build:
		# F06: origin auto-ghost is not enough — require intentional valid place first.
		if not _intentional_place_done:
			return false
		if not _cursor_hit_valid:
			return false
	return bool(get_validity().get("ok", false))


func can_cancel() -> bool:
	return _active or _delete_mode


func _plain_reject_reason(rej: Dictionary) -> String:
	var code := str(rej.get("code", ""))
	match code:
		"budget_fail":
			return "Too far from the build area"
		"unknown_module":
			return "That module is not available"
		"idempotency_payload_mismatch":
			return "This placement already committed with different details"
		"free_float_forbidden":
			return "Snap must stay on"
		"no_preview":
			return "No active preview"
		_:
			return str(rej.get("reason", "Cannot place yet"))


func _is_build_context() -> bool:
	if not is_inside_tree():
		return _picker_open
	var st := get_tree()
	if st == null:
		return _picker_open
	var router: Node = st.root.get_node_or_null("ControlContextRouter")
	if router != null and router.has_method("get_primary_context"):
		return str(router.call("get_primary_context")) == "build"
	return _picker_open


func open_picker() -> Dictionary:
	## Called when entering Build — player can cycle allowlisted modules.
	_ensure_picker_list()
	_picker_open = true
	_set_status("Pick a module, then Place")
	var st := get_picker_state()
	picker_changed.emit(st)
	hud_state_changed.emit(get_hud_state())
	return {"ok": true, "picker": st}


func close_picker() -> void:
	_picker_open = false
	picker_changed.emit(get_picker_state())
	hud_state_changed.emit(get_hud_state())


func cycle_module(direction: int = 1) -> Dictionary:
	## Player-facing module cycle via remappable InputMap actions (F03).
	_ensure_picker_list()
	if _picker_ids.is_empty():
		return _reject("picker_empty", "no allowlisted modules")
	_picker_open = true
	var n := _picker_ids.size()
	_picker_index = posmod(_picker_index + direction, n)
	_set_status("Module: %s" % _picker_ids[_picker_index])
	var st := get_picker_state()
	picker_changed.emit(st)
	hud_state_changed.emit(get_hud_state())
	preview_changed.emit(get_active_state())
	return {"ok": true, "picker": st, "via": "input_cycle"}


func place_highlighted_module() -> Dictionary:
	## Activate highlighted allowlisted module as preview (build_place path — not evidence API).
	_ensure_picker_list()
	if _picker_ids.is_empty():
		return _reject("picker_empty", "no allowlisted modules")
	var mid := _picker_ids[_picker_index]
	# Manual Build uses last cursor world hit when available; otherwise origin (P2E keyboard path).
	var px := _cursor_raw_x if _manual_build else 0.0
	var py := _cursor_raw_y if _manual_build else 0.0
	var pe := _raw_elev if _active else 0.0
	var pr := _raw_rot if _active else 0.0
	var res: Dictionary = select_module(mid, "structure", "", px, py, pe, pr)
	if bool(res.get("ok", false)):
		res["via"] = "input_place_highlighted"
		res["api_injected"] = false
		res["preview_only"] = true
		res["client_world_commit"] = false
		_awaiting_place_click = false
		if _manual_build:
			_cursor_follow = true
			# Intentional place action (button/key) counts once surface is valid.
			if _cursor_hit_valid or not bool(res.get("cursor_required", false)):
				_intentional_place_done = true
			advance_stage("hologram")
	hud_state_changed.emit(get_hud_state())
	return res


func begin_manual_build() -> Dictionary:
	## Enter cursor-led Manual Build: snapped hologram follows cursor; LMB places preview only.
	_ensure_picker_list()
	_manual_build = true
	_cursor_follow = true
	_awaiting_place_click = false
	_intentional_place_done = false
	_picker_open = true
	# Reset cursor origin so a prior invalid far hit cannot block boot.
	_cursor_raw_x = 0.0
	_cursor_raw_y = 0.0
	_cursor_hit_valid = true
	_raw_elev = 0.0
	_raw_rot = 0.0
	_set_status("Manual Build · aim cursor · LMB preview · Confirm commits")
	# Soft hologram near origin; follow moves it under the cursor (confirm still gated on LMB).
	var mid := _picker_ids[_picker_index] if not _picker_ids.is_empty() else "block_cube_round"
	var res: Dictionary = select_module(mid, "structure", "", 0.0, 0.0, 0.0, 0.0)
	if bool(res.get("ok", false)):
		advance_stage("hologram")
		_cursor_hit_valid = true
		# Boot ghost is not an intentional LMB place — Confirm stays disabled until place.
		_intentional_place_done = false
		if _preview != null and _preview.has_method("set_validity_visual"):
			_preview.call("set_validity_visual", true)
	open_picker()
	hud_state_changed.emit(get_hud_state())
	return {
		"ok": bool(res.get("ok", false)),
		"via": "manual_build",
		"manual_build": true,
		"cursor_follow": _cursor_follow,
		"intentional_place_done": _intentional_place_done,
		"confirm_enabled": can_confirm(),
		"preview_only": true,
		"client_world_commit": false,
		"canonical": false,
		"module_id": _module_id,
		"state": get_active_state(),
		"detail": res,
	}


func is_manual_build_mode() -> bool:
	return _manual_build


func is_manual_cursor_follow() -> bool:
	return _cursor_follow and _manual_build


func end_manual_build_mode() -> void:
	_manual_build = false
	_cursor_follow = false
	_awaiting_place_click = false
	_intentional_place_done = false
	_picker_open = false


func project_screen_to_ground(camera: Camera3D, screen_pos: Vector2, ground_y: float = 0.0) -> Dictionary:
	## Screen-to-ground ray on the allowed horizontal build plane (preview math only).
	if camera == null or not is_instance_valid(camera):
		return {"ok": false, "code": "no_camera", "reason": "camera required for ray"}
	var origin := camera.project_ray_origin(screen_pos)
	var dir := camera.project_ray_normal(screen_pos)
	if absf(dir.y) < 0.00001:
		return {"ok": false, "code": "ray_parallel", "reason": "ray parallel to ground"}
	var t := (ground_y - origin.y) / dir.y
	if t < 0.0:
		return {"ok": false, "code": "ray_behind", "reason": "intersection behind camera"}
	var hit := origin + dir * t
	# World XZ → placement x/y (contract plane).
	return {
		"ok": true,
		"x": hit.x,
		"y": hit.z,
		"world": hit,
		"ground_y": ground_y,
		"t": t,
	}


func update_cursor_screen(screen_pos: Vector2, camera: Camera3D) -> Dictionary:
	## Move snapped hologram with cursor while Manual Build owns follow (preview only).
	if not _manual_build:
		return {"ok": false, "code": "not_manual_build"}
	_last_screen_pos = screen_pos
	var elev := _raw_elev if _active else 0.0
	var proj: Dictionary = project_screen_to_ground(camera, screen_pos, elev)
	if not bool(proj.get("ok", false)):
		_cursor_hit_valid = false
		_apply_preview_validity(false)
		hud_state_changed.emit(get_hud_state())
		return proj
	_cursor_raw_x = float(proj["x"])
	_cursor_raw_y = float(proj["y"])
	# Snap always — free-float forbidden.
	var place: Dictionary = _Math.apply_placement(
		_cursor_raw_x, _cursor_raw_y, elev, _raw_rot if _active else 0.0, true
	) as Dictionary
	if not bool(place.get("ok", false)):
		_cursor_hit_valid = false
		_apply_preview_validity(false)
		return place
	var budget: Dictionary = _gate.call(
		"validate_budget_transform",
		float(place["x"]),
		float(place["y"]),
		float(place["elevation"])
	) as Dictionary
	_cursor_hit_valid = bool(budget.get("ok", false))
	if not _active:
		# After cancel: wait for LMB — do not auto-respawn (single cancel semantics).
		if _awaiting_place_click:
			return {
				"ok": true,
				"awaiting_place_click": true,
				"cursor_hit_valid": _cursor_hit_valid,
				"snapped": {
					"x": float(place["x"]),
					"y": float(place["y"]),
					"elevation": float(place["elevation"]),
				},
				"preview_only": true,
			}
		# Soft ghost: spawn following hologram.
		_ensure_picker_list()
		if _picker_ids.is_empty():
			return _reject("picker_empty", "no allowlisted modules")
		var mid := _picker_ids[_picker_index]
		var boot: Dictionary = select_module(
			mid, "structure", "", float(place["x"]), float(place["y"]), elev, _raw_rot
		)
		if bool(boot.get("ok", false)):
			advance_stage("hologram")
		_apply_preview_validity(_cursor_hit_valid)
		return {
			"ok": bool(boot.get("ok", false)),
			"spawned": true,
			"cursor_hit_valid": _cursor_hit_valid,
			"placement": _placement.duplicate(true) if _active else {},
			"preview_only": true,
			"client_world_commit": false,
		}
	# Active preview follows cursor (move only — never commit).
	_raw_x = float(place["x"])
	_raw_y = float(place["y"])
	_raw_elev = float(place["elevation"])
	# Soft reapply: update transform even when budget invalid so player sees feedback.
	_placement = {
		"x": float(place["x"]),
		"y": float(place["y"]),
		"elevation": float(place["elevation"]),
		"rotation_deg": float(place["rotation_deg"]),
	}
	if _preview != null and is_instance_valid(_preview) and _preview.has_method("apply_placement"):
		_preview.call("apply_placement", _placement)
	if _proposal_submitted:
		_proposal_submitted = false
		_counter += 1
		_request_id = str(_Builder.make_request_uuid("ba_req", _counter))
		_prompt_id = str(_Builder.make_request_uuid("ba_prm", _counter))
	_refresh_payload_and_key(false)
	_apply_preview_validity(_cursor_hit_valid)
	preview_changed.emit(get_active_state())
	hud_state_changed.emit(get_hud_state())
	return {
		"ok": true,
		"cursor_hit_valid": _cursor_hit_valid,
		"placement": _placement.duplicate(true),
		"preview_only": true,
		"client_world_commit": false,
		"canonical": false,
		"budget": budget,
	}


func place_at_cursor(screen_pos: Vector2, camera: Camera3D) -> Dictionary:
	## Left click: create or move preview at snapped cursor — never canonical World Commit.
	## H1-CODEX-MB-F06: fail closed outside Build context — never silently enable Manual Build.
	if not _is_build_context():
		# Even if a prior Manual Build flag lingered, never place outside Build.
		return _reject(
			"not_build_context",
			"place_at_cursor requires Build context; Manual Build not silently enabled"
		)
	if not _manual_build:
		# Enter Manual Build only when already in Build context (explicit product path).
		_manual_build = true
		_cursor_follow = true
		_intentional_place_done = false
	_awaiting_place_click = false
	_cursor_follow = true
	var upd: Dictionary = update_cursor_screen(screen_pos, camera)
	if not _active:
		_ensure_picker_list()
		if _picker_ids.is_empty():
			return _reject("picker_empty", "no allowlisted modules")
		var mid := _picker_ids[_picker_index]
		var res: Dictionary = select_module(
			mid, "structure", "", _cursor_raw_x, _cursor_raw_y, _raw_elev, _raw_rot
		)
		if bool(res.get("ok", false)):
			advance_stage("hologram")
			_apply_preview_validity(_cursor_hit_valid)
			if _cursor_hit_valid:
				_intentional_place_done = true
		res["via"] = "cursor_place"
		res["preview_only"] = true
		res["client_world_commit"] = false
		res["canonical"] = false
		res["intentional_place_done"] = _intentional_place_done
		hud_state_changed.emit(get_hud_state())
		return res
	# Move existing preview to cursor snap.
	var moved: Dictionary = {
		"ok": true,
		"via": "cursor_place_move",
		"preview_only": true,
		"client_world_commit": false,
		"canonical": false,
		"cursor_hit_valid": _cursor_hit_valid,
		"placement": _placement.duplicate(true),
		"state": get_active_state(),
		"update": upd,
	}
	if not _cursor_hit_valid:
		moved["ok"] = false
		moved["code"] = "invalid_surface"
		moved["reason"] = "cursor not on allowed build surface"
	else:
		# Intentional valid LMB place — unlock confirm for Manual Build.
		_intentional_place_done = true
	moved["intentional_place_done"] = _intentional_place_done
	_set_status(
		"Preview at snap (%.1f, %.1f) · %s"
		% [
			float(_placement.get("x", 0.0)),
			float(_placement.get("y", 0.0)),
			"valid" if _cursor_hit_valid else "invalid",
		]
	)
	hud_state_changed.emit(get_hud_state())
	return moved


func get_cursor_placement_state() -> Dictionary:
	return {
		"manual_build": _manual_build,
		"cursor_follow": _cursor_follow,
		"cursor_hit_valid": _cursor_hit_valid,
		"raw_x": _cursor_raw_x,
		"raw_y": _cursor_raw_y,
		"screen": _last_screen_pos,
		"placement": _placement.duplicate(true) if _active else {},
		"awaiting_place_click": _awaiting_place_click,
		"intentional_place_done": _intentional_place_done,
		"preview_only": true,
		"client_world_commit": false,
	}


func force_cursor_world_for_test(raw_x: float, raw_y: float) -> Dictionary:
	## Headless helper: apply snapped cursor world without a Camera3D ray.
	## Does NOT count as intentional LMB and does NOT enable Manual Build outside mode.
	if not _manual_build:
		return {
			"ok": false,
			"code": "not_manual_build",
			"reason": "force_cursor_world_for_test requires Manual Build mode already active",
			"preview_only": true,
		}
	_cursor_raw_x = raw_x
	_cursor_raw_y = raw_y
	var elev := _raw_elev if _active else 0.0
	var place: Dictionary = _Math.apply_placement(raw_x, raw_y, elev, _raw_rot if _active else 0.0, true) as Dictionary
	if not bool(place.get("ok", false)):
		_cursor_hit_valid = false
		_apply_preview_validity(false)
		return place
	var budget: Dictionary = _gate.call(
		"validate_budget_transform",
		float(place["x"]),
		float(place["y"]),
		float(place["elevation"])
	) as Dictionary
	_cursor_hit_valid = bool(budget.get("ok", false))
	if _active:
		_raw_x = float(place["x"])
		_raw_y = float(place["y"])
		_placement = {
			"x": float(place["x"]),
			"y": float(place["y"]),
			"elevation": float(place["elevation"]),
			"rotation_deg": float(place["rotation_deg"]),
		}
		if _preview != null and is_instance_valid(_preview) and _preview.has_method("apply_placement"):
			_preview.call("apply_placement", _placement)
		_apply_preview_validity(_cursor_hit_valid)
		preview_changed.emit(get_active_state())
		hud_state_changed.emit(get_hud_state())
	return {
		"ok": true,
		"cursor_hit_valid": _cursor_hit_valid,
		"placement": _placement.duplicate(true) if _active else {
			"x": float(place["x"]),
			"y": float(place["y"]),
			"elevation": float(place["elevation"]),
		},
		"budget": budget,
		"preview_only": true,
	}


func _apply_preview_validity(valid: bool) -> void:
	if _preview != null and is_instance_valid(_preview) and _preview.has_method("set_validity_visual"):
		_preview.call("set_validity_visual", valid)


func dispose_all_previews() -> void:
	if _preview != null and is_instance_valid(_preview):
		if _preview.has_method("free_cleanup"):
			_preview.call("free_cleanup")
		else:
			_preview.queue_free()
	_preview = null
	_active = false
	_proposal_submitted = false
	_set_router_preview_flag(false)
	# Also clear any orphan previews in groups (F02-R2).
	if is_inside_tree():
		for n in get_tree().get_nodes_in_group(_C.PREVIEW_GROUP):
			if n == null or not is_instance_valid(n):
				continue
			if n.has_method("free_cleanup"):
				n.call("free_cleanup")
			else:
				n.queue_free()
	# Do not free committed entities here — only preview.


func dispose_committed_presentation() -> void:
	## Optional presentation cleanup for committed visuals before process exit (not authority undo).
	var keep: Array = []
	for ent in _committed_entities:
		if not (ent is Dictionary):
			continue
		var node: Variant = (ent as Dictionary).get("node", null)
		if node != null and is_instance_valid(node):
			if (node as Node).has_method("free_cleanup"):
				(node as Node).call("free_cleanup")
			else:
				(node as Node).queue_free()
		keep.append(ent)
	_committed_entities.clear()


func get_validity() -> Dictionary:
	if not _active:
		return {"ok": false, "code": "no_preview", "reason": "no active preview"}
	var budget: Dictionary = _gate.call("validate_budget_transform",
		float(_placement.get("x", 0.0)),
		float(_placement.get("y", 0.0)),
		float(_placement.get("elevation", 0.0))
	) as Dictionary
	if not bool(budget.get("ok", false)):
		return budget
	var mod: Dictionary = _gate.call("validate_module_selection", _module_id) as Dictionary
	if not bool(mod.get("ok", false)):
		return mod
	var mat: Dictionary = _gate.call("validate_material_pair", _material_slot, _p1e_material) as Dictionary
	if not bool(mat.get("ok", false)):
		return mat
	return {"ok": true, "reason": "valid snapped placement"}


func get_last_status() -> String:
	return _last_status


func get_last_reject() -> Dictionary:
	return _last_reject.duplicate(true)


func get_last_receipt() -> Dictionary:
	return _last_receipt.duplicate(true)


func get_preview_node() -> Node3D:
	return _preview


func select_module(
	module_id: String,
	material_slot: String = "structure",
	p1e_material_id: String = "",
	raw_x: float = 0.0,
	raw_y: float = 0.0,
	raw_elev: float = 0.0,
	raw_rot: float = 0.0
) -> Dictionary:
	_ensure_catalogs()
	var mod: Dictionary = _gate.call("validate_module_selection", module_id) as Dictionary
	if not bool(mod.get("ok", false)):
		# Missing/unknown → Asset Request proposal only (no code/network/fs).
		if str(mod.get("code", "")) == "unknown_module":
			var ar: Dictionary = _gate.call("missing_asset_request", module_id, "unknown_or_missing_module") as Dictionary
			_last_reject = mod
			_set_status("Asset request only for %s" % module_id)
			return {"ok": false, "code": "unknown_module", "asset_request": ar, "reason": mod.get("reason", "")}
		_last_reject = mod
		return mod

	var slot := material_slot
	var mat_id := p1e_material_id
	if mat_id.is_empty():
		mat_id = str(_gate.call("resolve_material_for_slot", slot))
	var mat: Dictionary = _gate.call("validate_material_pair", slot, mat_id) as Dictionary
	if not bool(mat.get("ok", false)):
		_last_reject = mat
		return mat

	if _active:
		cancel_preview()

	_module_id = module_id
	_material_slot = slot
	_p1e_material = mat_id
	_raw_x = raw_x
	_raw_y = raw_y
	_raw_elev = raw_elev
	_raw_rot = raw_rot
	_snap_enabled = true
	_stage = "wireframe"
	_proposal_submitted = false
	_last_receipt = {}
	_last_entity_id = ""

	var place: Dictionary = _Math.apply_placement(_raw_x, _raw_y, _raw_elev, _raw_rot, true)
	if not bool(place.get("ok", false)):
		_last_reject = place
		return place
	_placement = {
		"x": float(place["x"]),
		"y": float(place["y"]),
		"elevation": float(place["elevation"]),
		"rotation_deg": float(place["rotation_deg"]),
	}

	var budget: Dictionary = _gate.call(
		"validate_budget_transform",
		float(_placement["x"]),
		float(_placement["y"]),
		float(_placement["elevation"])
	) as Dictionary
	if not bool(budget.get("ok", false)):
		_last_reject = budget
		_active = false
		return budget

	_counter += 1
	_request_id = str(_Builder.make_request_uuid("ba_req", _counter))
	_prompt_id = str(_Builder.make_request_uuid("ba_prm", _counter))
	_refresh_payload_and_key(false)

	_preview = _Preview.new() as Node3D
	_preview.name = "BlockPreview_%s" % _module_id
	# U5: set module_id before enter-tree so _ready kit path can resolve meshdesc.
	if "module_id" in _preview:
		_preview.set("module_id", _module_id)
	add_child(_preview)
	if _preview.has_method("configure"):
		_preview.call("configure", _module_id, _request_id, _prompt_id, _placement)
	if _preview.has_method("set_stage"):
		_preview.call("set_stage", "wireframe")

	_active = true
	_set_router_preview_flag(true)
	_set_status("Selected %s (wireframe, no collision)" % _module_id)
	var st := get_active_state()
	preview_changed.emit(st)
	hud_state_changed.emit(get_hud_state())
	# U5: presentation place pose — not durable, not authority.
	character_anim_trigger.emit("preview_place")
	return {"ok": true, "state": st, "api_injected": false, "client_world_commit": false}


func elevate(delta_steps: int = 1) -> Dictionary:
	## Labelled Lift action (build_elevation_up/down / PgUp/PgDn) — preview only.
	if _delete_mode:
		_last_elevate_result = {
			"ok": false,
			"elevated": false,
			"code": "delete_mode_active",
			"reason": "Lift unavailable in Delete red-X mode — exit delete first (Esc/RMB)",
			"elevation_label": "Lift (PgUp/PgDn)",
		}
		_set_status(str(_last_elevate_result["reason"]))
		hud_state_changed.emit(get_hud_state())
		return _last_elevate_result
	if not _active:
		_last_elevate_result = {
			"ok": false,
			"elevated": false,
			"code": "no_preview",
			"reason": "Lift needs an active preview — place a module first (LMB or P)",
			"elevation_label": "Lift (PgUp/PgDn)",
		}
		_set_status(str(_last_elevate_result["reason"]))
		hud_state_changed.emit(get_hud_state())
		return _last_elevate_result
	_raw_elev += float(delta_steps) * _C.ELEVATION_SNAP_M
	var r := _reapply_placement()
	r["elevated"] = bool(r.get("ok", false))
	r["elevation_label"] = "Lift (PgUp/PgDn)"
	r["elevation_m"] = float(_placement.get("elevation", _raw_elev))
	r["delta_steps"] = delta_steps
	if bool(r.get("ok", false)):
		r["reason"] = "Lift %.2f m" % float(r["elevation_m"])
		_set_status("Lift: %.2f m (PgUp/PgDn)" % float(r["elevation_m"]))
	_last_elevate_result = r
	hud_state_changed.emit(get_hud_state())
	return r


func rotate_steps(direction: int = 1) -> Dictionary:
	## direction: -1 left, +1 right. 15° contract snap.
	if _delete_mode:
		_last_rotate_result = {
			"ok": false,
			"rotated": false,
			"code": "delete_mode_active",
			"reason": "Q/R rotate unavailable in Delete red-X mode — exit delete first",
		}
		_set_status(str(_last_rotate_result["reason"]))
		hud_state_changed.emit(get_hud_state())
		return _last_rotate_result
	if not _active:
		_last_rotate_result = {
			"ok": false,
			"rotated": false,
			"code": "no_preview",
			"reason": "Q/R cannot rotate — no active preview. Place a module (LMB or P) first.",
			"message": "Q/R cannot rotate — no active preview. Place a module (LMB or P) first.",
		}
		_set_status(str(_last_rotate_result["reason"]))
		hud_state_changed.emit(get_hud_state())
		status_message.emit(str(_last_rotate_result["reason"]))
		return _last_rotate_result
	_raw_rot += float(direction) * _C.ROTATION_SNAP_DEG
	var r := _reapply_placement()
	r["rotated"] = bool(r.get("ok", false))
	r["rotation_deg"] = float(_placement.get("rotation_deg", _raw_rot))
	r["direction"] = direction
	if bool(r.get("ok", false)):
		r["reason"] = "Rotated to %d°" % int(round(float(r["rotation_deg"])))
	_last_rotate_result = r
	return r


func rotate_preview_degrees(degrees: float) -> Dictionary:
	## Called from Main build_rotate path — preview only.
	## Returns detail dict (never silent rotated=false without reason).
	if _delete_mode:
		_last_rotate_result = {
			"ok": false,
			"rotated": false,
			"code": "delete_mode_active",
			"reason": "Q/R rotate unavailable in Delete red-X mode — exit delete first",
			"message": "Q/R rotate unavailable in Delete red-X mode — exit delete first",
		}
		_set_status(str(_last_rotate_result["reason"]))
		hud_state_changed.emit(get_hud_state())
		status_message.emit(str(_last_rotate_result["reason"]))
		return _last_rotate_result
	if not _active or _preview == null:
		_last_rotate_result = {
			"ok": false,
			"rotated": false,
			"code": "no_preview",
			"reason": "Q/R cannot rotate — no active preview. Place a module (LMB or P) first.",
			"message": "Q/R cannot rotate — no active preview. Place a module (LMB or P) first.",
			"degrees_requested": degrees,
		}
		_set_status(str(_last_rotate_result["reason"]))
		hud_state_changed.emit(get_hud_state())
		status_message.emit(str(_last_rotate_result["reason"]))
		return _last_rotate_result
	var steps := int(round(degrees / _C.ROTATION_SNAP_DEG))
	if steps == 0 and absf(degrees) > 0.001:
		steps = 1 if degrees > 0.0 else -1
	var r := rotate_steps(steps)
	r["degrees_requested"] = degrees
	_last_rotate_result = r
	return r


func get_last_rotate_result() -> Dictionary:
	return _last_rotate_result.duplicate(true)


func get_last_elevate_result() -> Dictionary:
	return _last_elevate_result.duplicate(true)


func nudge_grid(dx_steps: int, dy_steps: int) -> Dictionary:
	if not _active:
		return _reject("no_preview", "no active preview")
	_raw_x += float(dx_steps) * _C.GRID_SNAP_M
	_raw_y += float(dy_steps) * _C.GRID_SNAP_M
	return _reapply_placement()


func set_snap_enabled(enabled: bool) -> Dictionary:
	## Snap off is rejected for placement (free float forbidden).
	if not enabled:
		return _reject("free_float_forbidden", "grid/socket snap required by contract")
	_snap_enabled = true
	return _reapply_placement()


func advance_stage(stage: String) -> Dictionary:
	if not _active:
		return _reject("no_preview", "no active preview")
	if stage not in _C.MANIFESTATION_STAGES:
		return _reject("bad_stage", "unknown stage %s" % stage)
	_stage = stage
	if _preview != null and _preview.has_method("set_stage"):
		_preview.call("set_stage", stage)
	# Collision/nav remain disabled until authority receipt.
	_set_status("Stage %s (collision=off nav=off)" % stage)
	var st := get_active_state()
	preview_changed.emit(st)
	return {"ok": true, "stage": _stage, "collision": false, "navigation": false, "state": st}


func validate_socket_edge(edge: Dictionary) -> Dictionary:
	_ensure_catalogs()
	return _sockets.call("validate_edge", edge) as Dictionary


func cancel_preview() -> Dictionary:
	## Cancel removes only current preview — never committed objects. Exactly-once semantics at caller.
	var had := _active
	var rid := _request_id
	var committed_before := _committed_entities.size()
	if _preview != null and is_instance_valid(_preview):
		if _preview.has_method("free_cleanup"):
			_preview.call("free_cleanup")
		elif is_instance_valid(_preview):
			_preview.queue_free()
	_preview = null
	_active = false
	_proposal_submitted = false
	_stage = "wireframe"
	# After cancel: do not auto-respawn ghost until LMB (single cancel).
	_awaiting_place_click = true
	_intentional_place_done = false
	_cursor_follow = _manual_build
	_set_router_preview_flag(false)
	_set_status("Preview cancelled (no receipt, no collision)")
	preview_changed.emit(get_active_state())
	hud_state_changed.emit(get_hud_state())
	# U5: cancel clip presentation only (Esc single-cancel still owns cancel_preview once).
	if had:
		character_anim_trigger.emit("cancel")
	return {
		"ok": true,
		"cancelled": had,
		"request_id": rid,
		"receipt": null,
		"collision": false,
		"navigation": false,
		"committed_untouched": true,
		"committed_count": committed_before,
		"awaiting_place_click": _awaiting_place_click,
		"single_cancel": true,
		"client_world_commit": false,
	}


func submit_preview_proposal() -> Dictionary:
	## Registers pending proposal on local World Commit authority (no durable mutation).
	## F06: invalid/intermediate does NOT freeze idempotency key; only committed keys bind.
	if not _active:
		return _reject("no_preview", "no active preview")
	if not _session_ready:
		return _reject("no_session", "bind_local_authority required")
	var validity := get_validity()
	if not bool(validity.get("ok", false)):
		_last_reject = validity
		# Do not bind key on invalid.
		return validity

	# Recompute payload fingerprint. Key tracks payload unless attacker forces a committed key.
	_refresh_payload_and_key(_hold_idempotency_key)
	_hold_idempotency_key = false

	# After a durable commit, same key + changed payload rejects.
	if _committed_keys.has(_idempotency_key):
		var prior_fp := str(_local_idem.get(_idempotency_key, ""))
		if not prior_fp.is_empty() and prior_fp != _payload_fp:
			var rej := {
				"ok": false,
				"code": "idempotency_payload_mismatch",
				"reason": "same idempotency key with changed payload after commit",
				"idempotency_key": _idempotency_key,
			}
			_last_reject = rej
			return rej

	var rev := get_world_revision()
	var prompt: Dictionary = _Builder.build_create_prompt(
		_request_id,
		_prompt_id,
		player_id,
		space_id,
		rev,
		_module_id,
		_placement,
		_material_slot,
		_p1e_material,
		world_profile,
		_idempotency_key,
		_payload_fp
	) as Dictionary

	var sub: Dictionary = _client.call("submit_and_preview", prompt) as Dictionary
	if not bool(sub.get("ok", false)):
		_last_reject = sub
		# Invalid authority submit: release any provisional binding (none for uncommitted).
		_set_status("Proposal rejected: %s" % str(sub.get("code", sub.get("reason", "fail"))))
		hud_state_changed.emit(get_hud_state())
		return sub
	_proposal_submitted = true
	# Intentionally do NOT write _local_idem / _committed_keys here (only after commit success).
	_set_status("Proposal pending (preview only)")
	hud_state_changed.emit(get_hud_state())
	return {"ok": true, "submit": sub, "world_revision": get_world_revision(), "mutated": false}


func confirm_and_commit(explicit: bool = true) -> Dictionary:
	## Requires explicit player confirm; schema-valid commit via WorldAuthorityLocal only.
	if not explicit:
		return _reject("confirm_not_explicit", "confirm requires explicit player input")
	if not _active:
		return _reject("no_preview", "no active preview")
	if not _session_ready:
		return _reject("no_session", "bind_local_authority required")
	var validity := get_validity()
	if not bool(validity.get("ok", false)):
		_last_reject = validity
		return validity
	if not _proposal_submitted:
		var sub := submit_preview_proposal()
		if not bool(sub.get("ok", false)):
			return sub

	var rev := get_world_revision()
	var conf: Dictionary = _client.call("confirm", _request_id, player_id) as Dictionary
	if not bool(conf.get("ok", false)):
		_last_reject = conf
		return conf

	var commit_req: Dictionary = _Builder.build_commit_request(
		_request_id, _prompt_id, player_id, actor_type, space_id, rev
	) as Dictionary
	var receipt: Dictionary = _client.call("commit", commit_req) as Dictionary
	_last_receipt = receipt.duplicate(true)
	commit_result.emit(receipt)

	var status := str(receipt.get("status", ""))
	if status == "committed" or status == "idempotent_replay":
		var eids: Array = receipt.get("entity_ids", []) as Array
		if eids.is_empty() and status == "idempotent_replay":
			# Prior entity already recorded.
			pass
		elif not eids.is_empty():
			_last_entity_id = str(eids[0])
		# F06: bind key only after successful authority commit (stable replay ok; changed payload rejects).
		if not _idempotency_key.is_empty():
			_local_idem[_idempotency_key] = _payload_fp
			_committed_keys[_idempotency_key] = true
		if status == "committed" and _preview != null and is_instance_valid(_preview):
			if _preview.has_method("enable_post_commit_physics"):
				_preview.call("enable_post_commit_physics")
			_committed_entities.append({
				"entity_id": _last_entity_id,
				"request_id": _request_id,
				"module_id": _module_id,
				"node": _preview,
			})
			_preview = null
			_active = false
			_proposal_submitted = false
			_set_router_preview_flag(false)
		_client.call("sync", false)
		_set_status("Committed entity=%s status=%s" % [_last_entity_id, status])
		hud_state_changed.emit(get_hud_state())
		# U5: confirm clip after authority receipt only (anim never commits).
		character_anim_trigger.emit("confirm")
		return {
			"ok": true,
			"receipt": receipt,
			"entity_id": _last_entity_id,
			"collision": true,
			"navigation": true,
			"issuer": str((receipt.get("authority", {}) as Dictionary).get("issuer", "")),
			"client_world_commit": false,
		}

	_last_reject = receipt
	_set_status("Commit rejected status=%s" % status)
	hud_state_changed.emit(get_hud_state())
	return {"ok": false, "receipt": receipt, "code": status}


func reject_client_authored_success(forged: Dictionary) -> Dictionary:
	## Client-authored success claims are never accepted as authority.
	return {
		"ok": false,
		"code": "client_forged",
		"reason": "client-authored success claim rejected; only world_commit_service may issue receipts",
		"accepted": false,
		"forged_status": str(forged.get("status", "")),
		"authority_required": "world_commit_service",
	}


func attempt_stale_revision_commit(stale_rev: int) -> Dictionary:
	if not _active or not _session_ready:
		return _reject("no_preview", "need active session+preview")
	if not _proposal_submitted:
		var sub := submit_preview_proposal()
		if not bool(sub.get("ok", false)):
			return sub
	_client.call("confirm", _request_id, player_id)
	var commit_req: Dictionary = _Builder.build_commit_request(
		_request_id, _prompt_id, player_id, actor_type, space_id, stale_rev
	) as Dictionary
	var receipt: Dictionary = _client.call("commit", commit_req) as Dictionary
	_last_receipt = receipt.duplicate(true)
	return {
		"ok": false,
		"receipt": receipt,
		"status": str(receipt.get("status", "")),
		"code": str((receipt.get("conflict", {}) as Dictionary).get("code", receipt.get("status", ""))),
	}


func attempt_changed_payload_same_key() -> Dictionary:
	## After durable commit, same key with mutated placement → REJECT (F06).
	## Intermediate invalid/pending must NOT poison a later corrected key.
	# Ensure active preview then commit to bind key.
	if not _active:
		var boot: Dictionary = select_module("block_cube_round", "structure", "", 0.0, 0.0, 0.0, 0.0)
		if not bool(boot.get("ok", false)):
			return boot
	var first := confirm_and_commit(true)
	if not bool(first.get("ok", false)):
		return first
	var frozen_key := str(_idempotency_key)
	var frozen_fp := str(_payload_fp)
	# New preview with different placement.
	var s2: Dictionary = select_module("block_cube_round", "structure", "", 1.0, 0.0, 0.0, 0.0)
	if not bool(s2.get("ok", false)):
		return s2
	# Force reuse of committed key with the new payload fingerprint (attack).
	_idempotency_key = frozen_key
	_hold_idempotency_key = true
	_payload = _Builder.placement_payload(
		_module_id, _placement, _material_slot, _p1e_material, world_profile
	) as Dictionary
	_payload_fp = str(_Builder.payload_fingerprint(_payload))
	if _payload_fp == frozen_fp:
		_raw_x += _C.GRID_SNAP_M
		_reapply_placement()
		_hold_idempotency_key = true
		_idempotency_key = frozen_key
	var second := submit_preview_proposal()
	return second


func attempt_invalid_then_corrected_submit() -> Dictionary:
	## F06 proof: invalid attempt must not freeze key against later corrected payload.
	if not _session_ready:
		return _reject("no_session", "bind_local_authority required")
	# Invalid: budget fail selection (no active bind).
	var bad: Dictionary = select_module("block_platform", "structure", "", 200.0, 0.0, 0.0, 0.0)
	if bool(bad.get("ok", false)):
		return {"ok": false, "code": "expected_budget_fail", "reason": "budget should fail"}
	# Corrected valid placement must succeed (key not poisoned).
	var good: Dictionary = select_module("block_cube_round", "structure", "", 0.0, 0.0, 0.0, 0.0)
	if not bool(good.get("ok", false)):
		return good
	# Intermediate: nudge then submit, then nudge again and re-submit — must not freeze.
	elevate(1)
	var sub1 := submit_preview_proposal()
	if not bool(sub1.get("ok", false)):
		return sub1
	# Correct placement again (new request after reapply clears proposal).
	elevate(1)
	var sub2 := submit_preview_proposal()
	if not bool(sub2.get("ok", false)):
		return {
			"ok": false,
			"code": "corrected_submit_blocked",
			"reason": "invalid/intermediate poisoned key",
			"detail": sub2,
		}
	var c := confirm_and_commit(true)
	return {
		"ok": bool(c.get("ok", false)),
		"invalid_first": bad,
		"corrected_submit": sub2,
		"commit": c,
		"key_poisoned": false,
	}


func request_undo_compensation() -> Dictionary:
	## Compensation via authority delete path — not direct SceneTree deletion of committed.
	if _committed_entities.is_empty():
		return _reject("nothing_to_undo", "no committed entity")
	if not _session_ready:
		return _reject("no_session", "bind_local_authority required")
	var last: Dictionary = _committed_entities[_committed_entities.size() - 1]
	var entity_id := str(last.get("entity_id", ""))
	if entity_id.is_empty():
		return _reject("missing_entity", "committed entity_id empty")
	return _authority_delete_entity(entity_id, "undo_compensation")


## --- C2 Delete red-X mode (explicit erase; World Commit compensation only) ---

func is_delete_mode() -> bool:
	return _delete_mode


func get_delete_mode_state() -> Dictionary:
	return {
		"active": _delete_mode,
		"cursor": "red_x" if _delete_mode else "",
		"target_entity_id": _delete_target_entity_id,
		"target_index": _delete_target_index,
		"pending_confirm": _delete_pending_confirm,
		"committed_count": _committed_entities.size(),
		"player_owned_only": true,
		"direct_scene_tree_delete": false,
		"client_world_commit": false,
		"mutation_class": "proposal_only" if _delete_mode and not _delete_pending_confirm else (
			"compensation_request" if _delete_pending_confirm else ""
		),
	}


func begin_delete_mode() -> Dictionary:
	## Enter explicit erase mode: red X cursor; only committed player-owned entities selectable.
	if not _session_ready:
		return _reject("no_session", "bind_local_authority required for delete mode")
	# Cancel non-durable preview without mutating committed.
	if _active:
		cancel_preview()
	_delete_mode = true
	_delete_target_entity_id = ""
	_delete_target_index = -1
	_delete_pending_confirm = false
	_delete_cursor_label = "red_x"
	_manual_build = false
	_cursor_follow = false
	character_anim_trigger.emit("delete_mode")
	_set_status("Delete red-X · LMB select committed owned · Enter confirm · Esc/RMB exit")
	hud_state_changed.emit(get_hud_state())
	preview_changed.emit(get_active_state())
	return {
		"ok": true,
		"delete_mode": true,
		"cursor": "red_x",
		"committed_count": _committed_entities.size(),
		"direct_scene_tree_delete": false,
		"client_world_commit": false,
		"mutation_class": "proposal_only",
	}


func exit_delete_mode(via: String = "esc_or_rmb") -> Dictionary:
	## Esc/RMB exits without mutation.
	var had := _delete_mode
	var had_target := _delete_target_entity_id
	_delete_mode = false
	_delete_target_entity_id = ""
	_delete_target_index = -1
	_delete_pending_confirm = false
	_delete_cursor_label = ""
	_clear_delete_highlights()
	_set_status("Delete mode exited (%s) — no mutation" % via)
	hud_state_changed.emit(get_hud_state())
	return {
		"ok": true,
		"exited": had,
		"via": via,
		"mutated": false,
		"prior_target": had_target,
		"direct_scene_tree_delete": false,
		"client_world_commit": false,
	}


func select_delete_target_by_index(index: int) -> Dictionary:
	## LMB path: select a committed player-owned/unlocked entity by list index.
	if not _delete_mode:
		return _reject("not_delete_mode", "enter delete mode first")
	if index < 0 or index >= _committed_entities.size():
		return _reject("delete_target_oob", "no committed entity at index")
	var ent: Dictionary = _committed_entities[index]
	var eid := str(ent.get("entity_id", ""))
	if eid.is_empty():
		return _reject("missing_entity", "committed entity_id empty")
	# Ownership gate: only player-owned session commits (this controller's list).
	_delete_target_entity_id = eid
	_delete_target_index = index
	_delete_pending_confirm = true
	_apply_delete_highlight(index)
	_set_status("Delete target selected: %s — Enter confirms compensation" % eid)
	hud_state_changed.emit(get_hud_state())
	return {
		"ok": true,
		"entity_id": eid,
		"index": index,
		"module_id": str(ent.get("module_id", "")),
		"pending_confirm": true,
		"cursor": "red_x",
		"direct_scene_tree_delete": false,
		"client_world_commit": false,
		"mutation_class": "proposal_only",
	}


func select_delete_target_entity(entity_id: String) -> Dictionary:
	if not _delete_mode:
		return _reject("not_delete_mode", "enter delete mode first")
	for i in _committed_entities.size():
		var ent: Dictionary = _committed_entities[i]
		if str(ent.get("entity_id", "")) == entity_id:
			return select_delete_target_by_index(i)
	return _reject("delete_target_not_owned", "entity not in player-owned committed list")


func cycle_delete_target(direction: int = 1) -> Dictionary:
	## When multiple committed entities exist, cycle selection under red-X.
	if not _delete_mode:
		return _reject("not_delete_mode", "enter delete mode first")
	if _committed_entities.is_empty():
		return _reject("nothing_to_delete", "no committed player-owned entities")
	var n := _committed_entities.size()
	var idx := _delete_target_index
	if idx < 0:
		idx = 0 if direction >= 0 else n - 1
	else:
		idx = posmod(idx + direction, n)
	return select_delete_target_by_index(idx)


func confirm_delete_target() -> Dictionary:
	## Confirmation → World Commit compensation-delete proposal. No queue_free as mutation.
	if not _delete_mode:
		return _reject("not_delete_mode", "enter delete mode first")
	if _delete_target_entity_id.is_empty():
		return _reject("no_delete_target", "LMB select a committed owned entity first")
	if not _delete_pending_confirm:
		return _reject("delete_not_pending", "delete confirmation not armed")
	var eid := _delete_target_entity_id
	var res := _authority_delete_entity(eid, "delete_red_x")
	if bool(res.get("ok", false)):
		character_anim_trigger.emit("confirm")
		_delete_target_entity_id = ""
		_delete_target_index = -1
		_delete_pending_confirm = false
		_clear_delete_highlights()
		# Stay in delete mode for multi-erase; player exits via Esc/RMB.
		hud_state_changed.emit(get_hud_state())
		# Happy reaction after authoritative result observed.
		character_anim_trigger.emit("happy")
	return res


func handle_player_confirm() -> Dictionary:
	## Player confirm path (confirm_action InputMap) — not evidence API injection.
	if _delete_mode:
		return confirm_delete_target()
	## Walk ordered manifestation stages before authority commit (preview stays non-solid).
	if not can_confirm():
		return _reject("confirm_disabled", "preview not ready to confirm")
	for s in ["wireframe", "hologram", "materializing"]:
		advance_stage(s)
	# complete applied post-receipt via enable_post_commit_physics on the committed node.
	return confirm_and_commit(true)


func _authority_delete_entity(entity_id: String, via: String) -> Dictionary:
	if not _session_ready:
		return _reject("no_session", "bind_local_authority required")
	var idx := -1
	var ent: Dictionary = {}
	for i in _committed_entities.size():
		var e: Dictionary = _committed_entities[i]
		if str(e.get("entity_id", "")) == entity_id:
			idx = i
			ent = e
			break
	if idx < 0:
		return _reject("delete_target_not_owned", "entity not player-owned/unlocked in session")

	_counter += 1
	var ureq := str(_Builder.make_request_uuid("ba_del", _counter))
	var uprm := str(_Builder.make_request_uuid("ba_delp", _counter))
	var rev := get_world_revision()
	var prompt: Dictionary = _Builder.build_delete_compensation_prompt(
		ureq, uprm, player_id, space_id, rev, entity_id
	) as Dictionary
	var sub: Dictionary = _client.call("submit_and_preview", prompt) as Dictionary
	if not bool(sub.get("ok", false)):
		return sub
	var conf: Dictionary = _client.call("confirm", ureq, player_id) as Dictionary
	if not bool(conf.get("ok", false)):
		return conf
	var commit_req: Dictionary = _Builder.build_commit_request(
		ureq, uprm, player_id, actor_type, space_id, rev
	) as Dictionary
	var receipt: Dictionary = _client.call("commit", commit_req) as Dictionary
	_last_receipt = receipt.duplicate(true)
	commit_result.emit(receipt)
	if str(receipt.get("status", "")) == "committed":
		# Authority path succeeded — then presentation cleanup (not the mutation source).
		var node: Variant = ent.get("node", null)
		if node != null and is_instance_valid(node):
			(node as Node).queue_free()
		_committed_entities.remove_at(idx)
		_client.call("sync", false)
		_set_status("Delete compensation committed for %s via=%s" % [entity_id, via])
		return {
			"ok": true,
			"mutation_class": "compensation_request",
			"direct_scene_tree_delete": false,
			"authority_path": true,
			"entity_id": entity_id,
			"via": via,
			"receipt": receipt,
			"client_world_commit": false,
		}
	return {"ok": false, "receipt": receipt, "via": via}


func _apply_delete_highlight(index: int) -> void:
	_clear_delete_highlights()
	if index < 0 or index >= _committed_entities.size():
		return
	var ent: Dictionary = _committed_entities[index]
	var node: Variant = ent.get("node", null)
	if node != null and is_instance_valid(node):
		(node as Node).set_meta("delete_highlight", true)
		if (node as Node).has_method("set_validity_visual"):
			(node as Node).call("set_validity_visual", false)


func _clear_delete_highlights() -> void:
	for ent in _committed_entities:
		if not (ent is Dictionary):
			continue
		var node: Variant = (ent as Dictionary).get("node", null)
		if node != null and is_instance_valid(node):
			(node as Node).set_meta("delete_highlight", false)
			if (node as Node).has_method("set_validity_visual"):
				(node as Node).call("set_validity_visual", true)


func get_committed_count() -> int:
	return _committed_entities.size()


func get_committed_entity_ids() -> PackedStringArray:
	var ids := PackedStringArray()
	for ent in _committed_entities:
		if ent is Dictionary:
			var eid := str((ent as Dictionary).get("entity_id", ""))
			if not eid.is_empty():
				ids.append(eid)
	return ids


func export_identity_snapshot() -> Dictionary:
	## Local identity snapshot for save/reload continuity (not network).
	var entities: Array = []
	for ent in _committed_entities:
		if not (ent is Dictionary):
			continue
		var d: Dictionary = ent as Dictionary
		entities.append({
			"entity_id": str(d.get("entity_id", "")),
			"request_id": str(d.get("request_id", "")),
			"module_id": str(d.get("module_id", "")),
		})
	return {
		"ok": true,
		"world_revision": get_world_revision(),
		"space_id": space_id,
		"entities": entities,
		"count": entities.size(),
		"client_world_commit": false,
	}


func reload_identity_snapshot(snap: Dictionary) -> Dictionary:
	## Restore committed identity records after a local save/reload (presentation optional).
	if snap == null or not (snap is Dictionary):
		return {"ok": false, "reason": "invalid_snapshot"}
	var entities: Array = snap.get("entities", []) as Array
	var restored: Array = []
	for ent in entities:
		if not (ent is Dictionary):
			continue
		var d: Dictionary = (ent as Dictionary).duplicate(true)
		var eid := str(d.get("entity_id", ""))
		if eid.is_empty():
			continue
		# Presentation node is not reconstructed here — identity is authority record only.
		d["node"] = null
		restored.append(d)
	_committed_entities = restored
	if not restored.is_empty():
		_last_entity_id = str((restored[restored.size() - 1] as Dictionary).get("entity_id", ""))
	return {
		"ok": true,
		"count": _committed_entities.size(),
		"entity_ids": get_committed_entity_ids(),
		"world_revision_at_snapshot": int(snap.get("world_revision", -1)),
		"identity_stable": true,
	}


func begin_companion_led_preview(
	module_id: String = "block_cube_round",
	raw_x: float = 0.0,
	raw_y: float = 0.0,
	raw_elev: float = 0.0,
	raw_rot: float = 0.0
) -> Dictionary:
	## Companion-led bounded surface: structured proposal → BA preview (not World Commit).
	var mid := module_id if not module_id.is_empty() else "block_cube_round"
	var sel: Dictionary = select_module(mid, "structure", "", raw_x, raw_y, raw_elev, raw_rot)
	if not bool(sel.get("ok", false)):
		return sel
	# Product preview reads as hologram construction light after wireframe spawn.
	advance_stage("hologram")
	open_picker()
	return {
		"ok": true,
		"via": "companion_led_preview",
		"module_id": _module_id,
		"stage": _stage,
		"preview": true,
		"client_world_commit": false,
		"mutation_class": "proposal_only",
		"state": get_active_state(),
	}


func get_server() -> RefCounted:
	return _server


func get_client() -> RefCounted:
	return _client


func _reapply_placement() -> Dictionary:
	var place: Dictionary = _Math.apply_placement(
		_raw_x, _raw_y, _raw_elev, _raw_rot, _snap_enabled
	) as Dictionary
	if not bool(place.get("ok", false)):
		_last_reject = place
		return place
	_placement = {
		"x": float(place["x"]),
		"y": float(place["y"]),
		"elevation": float(place["elevation"]),
		"rotation_deg": float(place["rotation_deg"]),
	}
	var budget: Dictionary = _gate.call(
		"validate_budget_transform",
		float(_placement["x"]),
		float(_placement["y"]),
		float(_placement["elevation"])
	) as Dictionary
	if not bool(budget.get("ok", false)):
		_last_reject = budget
		return budget
	if _preview != null and is_instance_valid(_preview) and _preview.has_method("apply_placement"):
		_preview.call("apply_placement", _placement)
	# Placement change after submit invalidates proposal (must re-submit) and refreshes key.
	if _proposal_submitted:
		_proposal_submitted = false
		_counter += 1
		_request_id = str(_Builder.make_request_uuid("ba_req", _counter))
		_prompt_id = str(_Builder.make_request_uuid("ba_prm", _counter))
	_refresh_payload_and_key(false)
	preview_changed.emit(get_active_state())
	hud_state_changed.emit(get_hud_state())
	return {"ok": true, "placement": _placement.duplicate(true)}


func _refresh_payload_and_key(force_keep_key: bool = false) -> void:
	## Recompute fingerprint from current placement. Until commit, key tracks payload (F06).
	_payload = _Builder.placement_payload(
		_module_id, _placement, _material_slot, _p1e_material, world_profile
	) as Dictionary
	_payload_fp = str(_Builder.payload_fingerprint(_payload))
	if force_keep_key:
		return
	if _committed_keys.has(_idempotency_key):
		var prior := str(_local_idem.get(_idempotency_key, ""))
		if prior == _payload_fp:
			return  # stable committed payload
		# New work after a prior commit → mint a fresh key for the new payload.
		_idempotency_key = "idem_%s" % _payload_fp.substr(0, 16)
		return
	# Uncommitted (or empty key): always follow current payload — never freeze on invalid.
	_idempotency_key = "idem_%s" % _payload_fp.substr(0, 16)


func _reject(code: String, reason: String) -> Dictionary:
	var d := {"ok": false, "code": code, "reason": reason}
	_last_reject = d
	hud_state_changed.emit(get_hud_state())
	return d


func _set_status(text: String) -> void:
	_last_status = text
	status_message.emit(text)
	hud_state_changed.emit(get_hud_state())


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


func _set_router_preview_flag(active: bool) -> void:
	## SceneTree-root relative only — no absolute /root (H1-CODEX-F01).
	var router := _autoload_node("ControlContextRouter")
	if router != null and router.has_method("set_cancel_target"):
		router.call("set_cancel_target", "preview_hologram", active)
