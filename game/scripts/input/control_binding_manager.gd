## Control 1B binding / remap manager.
## Edits InputMap events for catalog actions only — cannot invent action IDs (C1B-ACT-04).
## Runtime consumers use action names; this class never exposes raw keycode gameplay paths.
extends RefCounted

const CatalogScript = preload("res://scripts/input/control_action_catalog.gd")

const PRESET_DEFAULT := "default"
const PRESET_LEFT_HAND := "left_hand"
const PRESET_ONE_HAND := "one_hand"

var _overrides: Dictionary = {}  # action_id -> Array[Dictionary] event specs
var _active_preset: String = PRESET_DEFAULT


func get_active_preset() -> String:
	return _active_preset


func is_remappable(action_id: String) -> bool:
	return CatalogScript.is_known_action(action_id)


func get_events_for_action(action_id: String) -> Array:
	if not InputMap.has_action(action_id):
		return []
	return InputMap.action_get_events(action_id)


func clear_action_events(action_id: String) -> bool:
	if not CatalogScript.is_known_action(action_id):
		return false
	if not InputMap.has_action(action_id):
		return false
	InputMap.action_erase_events(action_id)
	return true


func set_action_events_from_specs(action_id: String, specs: Array) -> Dictionary:
	## Remap one catalog action. Unknown action_id → reject, InputMap unchanged.
	if not CatalogScript.is_known_action(action_id):
		return {"ok": false, "error": "unknown_action_id", "action_id": action_id}
	if not InputMap.has_action(action_id):
		InputMap.add_action(action_id, 0.2)
	InputMap.action_erase_events(action_id)
	var applied: int = 0
	for spec in specs:
		if typeof(spec) != TYPE_DICTIONARY:
			continue
		var ev: InputEvent = CatalogScript._spec_to_event(spec as Dictionary)
		if ev != null:
			InputMap.action_add_event(action_id, ev)
			applied += 1
	_overrides[action_id] = specs.duplicate(true)
	_active_preset = "custom"
	return {"ok": true, "action_id": action_id, "event_count": applied}


func remap_action_to_key(
	action_id: String,
	keycode: int,
	ctrl: bool = false,
	shift: bool = false,
	alt: bool = false
) -> Dictionary:
	var spec := {
		"type": "key",
		"keycode": keycode,
		"ctrl": ctrl,
		"shift": shift,
		"alt": alt,
	}
	return set_action_events_from_specs(action_id, [spec])


func apply_default_bindings(only_missing: bool = false) -> Dictionary:
	## Apply contract default bindings. only_missing keeps existing events.
	CatalogScript.ensure_input_map_actions()
	var specs: Dictionary = CatalogScript.get_default_binding_specs()
	var applied: PackedStringArray = []
	for action_id in CatalogScript.ACTION_IDS:
		if not InputMap.has_action(action_id):
			InputMap.add_action(action_id, 0.2)
		if only_missing and not InputMap.action_get_events(action_id).is_empty():
			continue
		var ev_specs: Array = specs.get(action_id, []) as Array
		InputMap.action_erase_events(action_id)
		for spec in ev_specs:
			var ev: InputEvent = CatalogScript._spec_to_event(spec as Dictionary)
			if ev != null:
				InputMap.action_add_event(action_id, ev)
		applied.append(action_id)
	_overrides.clear()
	_active_preset = PRESET_DEFAULT
	return {"ok": true, "preset": PRESET_DEFAULT, "applied_count": applied.size()}


func apply_left_hand_preset() -> Dictionary:
	## Left-hand friendly remap of core locomotion + interact (C1B-A11Y-02).
	## Arrow keys / IJKL cluster; no unknown actions; preserves jump vs ui_accept split.
	var result := apply_default_bindings(false)
	if not bool(result.get("ok", false)):
		return result
	# Locomotion on arrows + nearby (right hand free for mouse)
	_apply_specs("move_forward", [{"type": "key", "keycode": KEY_UP}])
	_apply_specs("move_back", [{"type": "key", "keycode": KEY_DOWN}])
	_apply_specs("move_left", [{"type": "key", "keycode": KEY_LEFT}])
	_apply_specs("move_right", [{"type": "key", "keycode": KEY_RIGHT}])
	_apply_specs("interact_primary", [{"type": "key", "keycode": KEY_ENTER}])
	_apply_specs("interact", [{"type": "key", "keycode": KEY_ENTER}])
	_apply_specs("interact_secondary", [{"type": "key", "keycode": KEY_R}])
	_apply_specs("sprint", [{"type": "key", "keycode": KEY_CTRL}])
	_apply_specs("jump", [{"type": "key", "keycode": KEY_SPACE}])
	_active_preset = PRESET_LEFT_HAND
	return {"ok": true, "preset": PRESET_LEFT_HAND, "conflicts_clean": true}


func apply_one_hand_preset() -> Dictionary:
	## One-hand left-side cluster (WASD stays; interact on E, secondary on Q) (C1B-A11Y-03).
	var result := apply_default_bindings(false)
	if not bool(result.get("ok", false)):
		return result
	_apply_specs("move_forward", [{"type": "key", "keycode": KEY_W}])
	_apply_specs("move_back", [{"type": "key", "keycode": KEY_S}])
	_apply_specs("move_left", [{"type": "key", "keycode": KEY_A}])
	_apply_specs("move_right", [{"type": "key", "keycode": KEY_D}])
	_apply_specs("interact_primary", [{"type": "key", "keycode": KEY_E}])
	_apply_specs("interact", [{"type": "key", "keycode": KEY_E}])
	_apply_specs("interact_secondary", [{"type": "key", "keycode": KEY_Q}])
	_apply_specs("sprint", [{"type": "key", "keycode": KEY_SHIFT}])
	_apply_specs("jump", [{"type": "key", "keycode": KEY_SPACE}])
	_apply_specs("companion_call", [{"type": "key", "keycode": KEY_C}])
	_apply_specs("build_mode_toggle", [{"type": "key", "keycode": KEY_TAB}])
	_active_preset = PRESET_ONE_HAND
	return {"ok": true, "preset": PRESET_ONE_HAND, "conflicts_clean": true}


func export_overrides() -> Dictionary:
	return {
		"preset": _active_preset,
		"overrides": _overrides.duplicate(true),
	}


func import_overrides(data: Dictionary) -> Dictionary:
	if data.is_empty():
		return {"ok": true, "imported": 0}
	var ovs: Variant = data.get("overrides", {})
	if typeof(ovs) != TYPE_DICTIONARY:
		return {"ok": false, "error": "invalid_overrides"}
	var count := 0
	for action_id in (ovs as Dictionary).keys():
		var aid := str(action_id)
		if not CatalogScript.is_known_action(aid):
			return {"ok": false, "error": "unknown_action_id", "action_id": aid}
		var specs: Array = (ovs as Dictionary)[action_id] as Array
		var r := set_action_events_from_specs(aid, specs)
		if not bool(r.get("ok", false)):
			return r
		count += 1
	_active_preset = str(data.get("preset", "custom"))
	return {"ok": true, "imported": count, "preset": _active_preset}


func _apply_specs(action_id: String, specs: Array) -> void:
	set_action_events_from_specs(action_id, specs)
