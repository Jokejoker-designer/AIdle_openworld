## Control 1B closed action catalog + context allow-lists (fail-closed).
## Source of truth for foundation action IDs matching Control/CONTROL_1B_ACCEPTANCE_CONTRACT.md §2.2.
## Runtime gameplay must use InputMap action names from this catalog — never invent IDs.
extends RefCounted

const CONTRACT_VERSION := "1.0.0"
const CONTEXT_HUD_MAX_ACTIONS := 4

const CONTEXTS: PackedStringArray = [
	"exploration",
	"companion",
	"build",
	"inspect",
	"world_tool",
]

## Safety classes for proposal-boundary actions.
const SAFETY_BENIGN := "benign"
const SAFETY_UI_NAV := "ui_nav"
const SAFETY_SYSTEM := "system"
const SAFETY_PREVIEW_ONLY := "preview_only"
const SAFETY_PROPOSAL_ONLY := "proposal_only"
const SAFETY_COMPENSATION_REQUEST := "compensation_request"
const SAFETY_CONFIRM_GATED := "confirm_gated"

## Closed foundation action IDs (existing locomotion IDs preserved).
const ACTION_IDS: PackedStringArray = [
	# Locomotion / camera / system (stable)
	"move_forward",
	"move_back",
	"move_left",
	"move_right",
	"sprint",
	"jump",
	"camera_zoom_in",
	"camera_zoom_out",
	"rotate_camera_left",
	"rotate_camera_right",
	"pause_menu",
	"toggle_debug",
	"interact",
	# Required new / renamed foundation
	"interact_primary",
	"interact_secondary",
	"companion_call",
	"prompt_quick_open",
	"prompt_send",
	"prompt_newline",
	"build_mode_toggle",
	"world_ability",
	"world_panel",
	"inspect_entity",
	"map_open",
	"camera_reset",
	"cancel_action",
	"confirm_action",
	"request_undo",
	"request_redo",
	"delete_proposal",
	"build_place",
	"build_cancel",
	"build_rotate_left",
	"build_rotate_right",
	"build_elevation_up",
	"build_elevation_down",
	"build_scale_up",
	"build_scale_down",
	"build_snap_toggle",
	"build_grid_toggle",
	"build_duplicate",
	"build_validate_collision",
	"build_validate_navigation",
	"build_link",
	# P2E-001 playable module picker (remappable; Build context only)
	"build_module_prev",
	"build_module_next",
	# Cozy aliases (named aliases only)
	"cozy_helper_pulse",
	"cozy_homestead_panel",
]


static func is_known_context(context_id: String) -> bool:
	return context_id in CONTEXTS


static func is_known_action(action_id: String) -> bool:
	return action_id in ACTION_IDS


static func resolve_alias(action_id: String) -> String:
	## Named aliases only — free-form IDs fail closed at is_known_action.
	match action_id:
		"cozy_helper_pulse":
			return "world_ability"
		"cozy_homestead_panel":
			return "world_panel"
		"interact":
			# Legacy synonym of interact_primary for migration.
			return "interact_primary"
		_:
			return action_id


static func get_safety_class(action_id: String) -> String:
	var canonical := resolve_alias(action_id)
	match canonical:
		"delete_proposal", "prompt_send":
			return SAFETY_PROPOSAL_ONLY
		"request_undo", "request_redo":
			return SAFETY_COMPENSATION_REQUEST
		"build_place", "build_rotate_left", "build_rotate_right", "build_elevation_up", "build_elevation_down", "build_scale_up", "build_scale_down", "build_snap_toggle", "build_duplicate", "build_validate_collision", "build_validate_navigation", "build_link", "build_module_prev", "build_module_next", "world_ability":
			return SAFETY_PREVIEW_ONLY
		"confirm_action":
			return SAFETY_CONFIRM_GATED
		"pause_menu", "toggle_debug":
			return SAFETY_SYSTEM
		"companion_call", "prompt_quick_open", "prompt_newline", "build_mode_toggle", "world_panel", "map_open", "cancel_action", "build_cancel", "build_grid_toggle":
			return SAFETY_UI_NAV
		_:
			return SAFETY_BENIGN


static func is_proposal_only(action_id: String) -> bool:
	return get_safety_class(action_id) == SAFETY_PROPOSAL_ONLY


static func is_compensation_request(action_id: String) -> bool:
	return get_safety_class(action_id) == SAFETY_COMPENSATION_REQUEST


static func is_direct_durable_forbidden(action_id: String) -> bool:
	## C1B-SAFE-01/02/03: delete and undo never mutate durable state on keydown.
	var sc := get_safety_class(action_id)
	return sc == SAFETY_PROPOSAL_ONLY or sc == SAFETY_COMPENSATION_REQUEST


static func get_context_allowed_actions(context_id: String) -> PackedStringArray:
	## Fail-closed: unknown context → empty allow-list.
	match context_id:
		"exploration":
			return PackedStringArray([
				"move_forward", "move_back", "move_left", "move_right",
				"sprint", "jump",
				"camera_zoom_in", "camera_zoom_out",
				"rotate_camera_left", "rotate_camera_right",
				"pause_menu", "toggle_debug",
				"interact", "interact_primary", "interact_secondary",
				"companion_call", "prompt_quick_open", "build_mode_toggle",
				"world_ability", "world_panel", "cozy_helper_pulse", "cozy_homestead_panel",
				"inspect_entity", "map_open", "camera_reset", "cancel_action",
			])
		"companion":
			return PackedStringArray([
				"companion_call", "prompt_quick_open", "prompt_send", "prompt_newline",
				"confirm_action", "cancel_action", "delete_proposal", "request_undo",
			])
		"build":
			return PackedStringArray([
				"move_forward", "move_back", "move_left", "move_right", "sprint",
				"camera_zoom_in", "camera_zoom_out",
				"build_mode_toggle", "build_place", "build_cancel",
				"build_rotate_left", "build_rotate_right",
				"build_elevation_up", "build_elevation_down",
				"build_scale_up", "build_scale_down",
				"build_snap_toggle", "build_grid_toggle", "build_duplicate",
				"build_validate_collision", "build_validate_navigation", "build_link",
				"build_module_prev", "build_module_next",
				"confirm_action", "cancel_action",
				"delete_proposal", "request_undo", "request_redo",
				"prompt_quick_open", "companion_call",
			])
		"inspect":
			return PackedStringArray([
				"move_forward", "move_back", "move_left", "move_right",
				"camera_zoom_in", "camera_zoom_out",
				"inspect_entity", "interact", "interact_primary",
				"cancel_action", "confirm_action",
				"delete_proposal", "request_undo",
			])
		"world_tool":
			return PackedStringArray([
				"move_forward", "move_back", "move_left", "move_right",
				"sprint", "jump",
				"camera_zoom_in", "camera_zoom_out",
				"world_ability", "world_panel",
				"cozy_helper_pulse", "cozy_homestead_panel",
				"interact", "interact_primary", "interact_secondary",
				"cancel_action", "confirm_action",
			])
		_:
			return PackedStringArray()


static func get_context_hud_actions(context_id: String) -> PackedStringArray:
	## Always ≤ CONTEXT_HUD_MAX_ACTIONS (C1B-HUD-01).
	var raw: PackedStringArray
	match context_id:
		"exploration":
			raw = PackedStringArray([
				"interact_primary", "interact_secondary", "world_ability", "build_mode_toggle",
			])
		"companion":
			raw = PackedStringArray([
				"prompt_send", "confirm_action", "cancel_action", "companion_call",
			])
		"build":
			raw = PackedStringArray([
				"build_place", "build_module_next", "build_rotate_right", "cancel_action",
			])
		"inspect":
			raw = PackedStringArray([
				"inspect_entity", "interact_primary", "delete_proposal", "cancel_action",
			])
		"world_tool":
			raw = PackedStringArray([
				"world_ability", "world_panel", "interact_secondary", "cancel_action",
			])
		_:
			raw = PackedStringArray()
	if raw.size() > CONTEXT_HUD_MAX_ACTIONS:
		return raw.slice(0, CONTEXT_HUD_MAX_ACTIONS)
	return raw


static func is_action_allowed_in_context(context_id: String, action_id: String) -> bool:
	if not is_known_context(context_id):
		return false
	if not is_known_action(action_id):
		return false
	var allowed := get_context_allowed_actions(context_id)
	if action_id in allowed:
		return true
	# Accept canonical alias target if listed (e.g. cozy → world_ability).
	var canonical := resolve_alias(action_id)
	return canonical != action_id and canonical in allowed


static func get_default_binding_specs() -> Dictionary:
	## Physical defaults for binding manager / project.godot alignment.
	## Values: Array of {type, keycode|button, ctrl?, shift?, alt?}
	return {
		"move_forward": [{"type": "key", "keycode": KEY_W}, {"type": "key", "keycode": KEY_UP}],
		"move_back": [{"type": "key", "keycode": KEY_S}, {"type": "key", "keycode": KEY_DOWN}],
		"move_left": [{"type": "key", "keycode": KEY_A}, {"type": "key", "keycode": KEY_LEFT}],
		"move_right": [{"type": "key", "keycode": KEY_D}, {"type": "key", "keycode": KEY_RIGHT}],
		"sprint": [{"type": "key", "keycode": KEY_SHIFT}],
		"jump": [{"type": "key", "keycode": KEY_SPACE}],
		"camera_zoom_in": [{"type": "mouse_button", "button": MOUSE_BUTTON_WHEEL_UP}],
		"camera_zoom_out": [{"type": "mouse_button", "button": MOUSE_BUTTON_WHEEL_DOWN}],
		"rotate_camera_left": [{"type": "key", "keycode": KEY_Q}],
		"rotate_camera_right": [{"type": "key", "keycode": KEY_R}],
		"pause_menu": [{"type": "key", "keycode": KEY_ESCAPE}],
		"toggle_debug": [{"type": "key", "keycode": KEY_F3}],
		"interact": [{"type": "key", "keycode": KEY_E}],
		"interact_primary": [{"type": "key", "keycode": KEY_E}],
		"interact_secondary": [{"type": "key", "keycode": KEY_F}],
		"companion_call": [{"type": "key", "keycode": KEY_C}],
		"prompt_quick_open": [{"type": "key", "keycode": KEY_SLASH}],
		"prompt_send": [{"type": "key", "keycode": KEY_ENTER, "ctrl": true}],
		"prompt_newline": [{"type": "key", "keycode": KEY_ENTER, "shift": true}],
		"build_mode_toggle": [{"type": "key", "keycode": KEY_TAB}],
		"world_ability": [{"type": "key", "keycode": KEY_V}],
		"world_panel": [{"type": "key", "keycode": KEY_B}],
		"inspect_entity": [{"type": "key", "keycode": KEY_I}],
		"map_open": [{"type": "key", "keycode": KEY_M}],
		"camera_reset": [{"type": "key", "keycode": KEY_HOME}],
		"cancel_action": [{"type": "key", "keycode": KEY_ESCAPE}],
		"confirm_action": [{"type": "key", "keycode": KEY_ENTER}],
		"request_undo": [{"type": "key", "keycode": KEY_Z, "ctrl": true}],
		"request_redo": [{"type": "key", "keycode": KEY_Y, "ctrl": true}],
		"delete_proposal": [{"type": "key", "keycode": KEY_DELETE}],
		# KEY_P enables full keyboard player path (F03-R2); LMB remains place alias.
		"build_place": [
			{"type": "mouse_button", "button": MOUSE_BUTTON_LEFT},
			{"type": "key", "keycode": KEY_P},
		],
		"build_cancel": [{"type": "mouse_button", "button": MOUSE_BUTTON_RIGHT}],
		"build_rotate_left": [{"type": "key", "keycode": KEY_Q}],
		"build_rotate_right": [{"type": "key", "keycode": KEY_R}],
		"build_elevation_up": [{"type": "key", "keycode": KEY_PAGEUP}],
		"build_elevation_down": [{"type": "key", "keycode": KEY_PAGEDOWN}],
		"build_scale_up": [],
		"build_scale_down": [],
		"build_snap_toggle": [{"type": "key", "keycode": KEY_X}],
		"build_grid_toggle": [{"type": "key", "keycode": KEY_G}],
		"build_duplicate": [{"type": "key", "keycode": KEY_D, "ctrl": true}],
		"build_validate_collision": [{"type": "key", "keycode": KEY_K}],
		"build_validate_navigation": [{"type": "key", "keycode": KEY_N}],
		"build_link": [{"type": "key", "keycode": KEY_L}],
		"build_module_prev": [{"type": "key", "keycode": KEY_COMMA}],
		"build_module_next": [{"type": "key", "keycode": KEY_PERIOD}],
		"cozy_helper_pulse": [{"type": "key", "keycode": KEY_V}],
		"cozy_homestead_panel": [{"type": "key", "keycode": KEY_B}],
	}


static func ensure_input_map_actions() -> Dictionary:
	## Register any missing catalog actions on InputMap (idempotent; headless-safe).
	## Does not clear existing events. Returns {added: [], already: [], unknown_skipped: []}.
	var added: PackedStringArray = []
	var already: PackedStringArray = []
	var specs: Dictionary = get_default_binding_specs()
	for action_id in ACTION_IDS:
		if InputMap.has_action(action_id):
			already.append(action_id)
			continue
		InputMap.add_action(action_id, 0.2)
		var events: Array = specs.get(action_id, []) as Array
		for spec in events:
			var ev := _spec_to_event(spec as Dictionary)
			if ev != null:
				InputMap.action_add_event(action_id, ev)
		added.append(action_id)
	# P2E F03-R2: ensure KEY_P is bound to build_place even if action pre-existed with LMB only.
	_ensure_build_place_key_p()
	return {"added": added, "already": already}


static func _ensure_build_place_key_p() -> void:
	if not InputMap.has_action("build_place"):
		InputMap.add_action("build_place", 0.2)
	var has_p := false
	for ev in InputMap.action_get_events("build_place"):
		if ev is InputEventKey:
			var ke := ev as InputEventKey
			if int(ke.physical_keycode) == KEY_P or int(ke.keycode) == KEY_P:
				has_p = true
				break
	if not has_p:
		var ke2 := InputEventKey.new()
		ke2.physical_keycode = KEY_P
		ke2.keycode = KEY_P
		InputMap.action_add_event("build_place", ke2)


static func _spec_to_event(spec: Dictionary) -> InputEvent:
	var t := str(spec.get("type", "key"))
	if t == "key":
		var ke := InputEventKey.new()
		ke.physical_keycode = int(spec.get("keycode", 0)) as Key
		ke.ctrl_pressed = bool(spec.get("ctrl", false))
		ke.shift_pressed = bool(spec.get("shift", false))
		ke.alt_pressed = bool(spec.get("alt", false))
		ke.meta_pressed = bool(spec.get("meta", false))
		return ke
	if t == "mouse_button":
		var me := InputEventMouseButton.new()
		me.button_index = int(spec.get("button", 0)) as MouseButton
		me.ctrl_pressed = bool(spec.get("ctrl", false))
		me.shift_pressed = bool(spec.get("shift", false))
		me.alt_pressed = bool(spec.get("alt", false))
		return me
	return null


static func validate_catalog_cardinality() -> Dictionary:
	## C1B-CTX-06: exactly one of each closed context_id conceptually present.
	var missing: PackedStringArray = []
	for c in CONTEXTS:
		if get_context_allowed_actions(c).is_empty():
			missing.append(c)
	var dup_check: Dictionary = {}
	var dups: PackedStringArray = []
	for c in CONTEXTS:
		if dup_check.has(c):
			dups.append(c)
		else:
			dup_check[c] = true
	return {
		"ok": missing.is_empty() and dups.is_empty() and CONTEXTS.size() == 5,
		"context_count": CONTEXTS.size(),
		"missing": missing,
		"duplicates": dups,
	}
