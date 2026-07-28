## P2E-001 C0 F03 — playable allowlisted module selection via InputMap/actions.
## Evidence path must NOT call select_module to create state.
## Run:
##   tools/Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://tests/p2e001_block_assembly_playable_select_smoke.gd
extends SceneTree

const CatalogScript = preload("res://scripts/input/control_action_catalog.gd")
const RouterScript = preload("res://autoload/control_context_router.gd")
const CtrlScript = preload("res://scripts/modules/block_assembly/block_assembly_controller.gd")
const HudScript = preload("res://scripts/modules/block_assembly/block_assembly_hud.gd")

var _failures: PackedStringArray = []
var _passed: int = 0
var _router: Node = null
var _ctrl: Node = null
var _hud: CanvasLayer = null


func _initialize() -> void:
	print("[P2E-001 playable select smoke] starting…")
	CatalogScript.ensure_input_map_actions()
	_router = _resolve_router()
	_ctrl = CtrlScript.new() as Node
	root.add_child(_ctrl)
	_ctrl.call("bind_local_authority", 0)
	_hud = HudScript.new() as CanvasLayer
	root.add_child(_hud)
	_hud.call("bind_controller", _ctrl)

	_test_catalog_has_picker_actions()
	_test_build_context_allows_cycle_and_place()
	_test_cycle_and_place_without_select_module_api()
	_test_hud_plain_language()
	_test_elevation_and_cancel_keep_committed()
	_finish()


func _finish() -> void:
	if _ctrl != null and _ctrl.has_method("dispose_all_previews"):
		_ctrl.call("dispose_all_previews")
	if _failures.is_empty():
		print("AIDLE_P2E001_PLAYABLE_SELECT_SMOKE=PASS checks=%d" % _passed)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print("AIDLE_P2E001_PLAYABLE_SELECT_SMOKE=FAIL failed=%d passed=%d" % [_failures.size(), _passed])
		quit(1)


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)


func _resolve_router() -> Node:
	var existing := root.get_node_or_null("ControlContextRouter")
	if existing != null:
		return existing
	var node: Node = RouterScript.new() as Node
	root.add_child(node)
	return node


func _test_catalog_has_picker_actions() -> void:
	if not CatalogScript.is_known_action("build_module_next"):
		_fail("known_build_module_next")
		return
	if not CatalogScript.is_known_action("build_module_prev"):
		_fail("known_build_module_prev")
		return
	if not InputMap.has_action("build_module_next") or not InputMap.has_action("build_module_prev"):
		_fail("inputmap_picker_actions")
		return
	_ok("catalog_inputmap_picker_actions")


func _test_build_context_allows_cycle_and_place() -> void:
	_router.call("request_context", "build")
	if not bool(_router.call("is_action_allowed", "build_module_next")):
		_fail("build_allows_module_next")
		return
	if not bool(_router.call("is_action_allowed", "build_place")):
		_fail("build_allows_place")
		return
	_router.call("request_context", "exploration")
	if bool(_router.call("is_action_allowed", "build_module_next")):
		_fail("exploration_must_block_module_next")
		return
	_ok("context_gates_picker_actions")


func _test_cycle_and_place_without_select_module_api() -> void:
	## Simulate player path: enter build → cycle → place (no select_module call).
	_router.call("request_context", "build")
	_ctrl.call("open_picker")
	var p0: Dictionary = _ctrl.call("get_picker_state") as Dictionary
	var h0 := str(p0.get("highlighted_module_id", ""))
	if h0.is_empty():
		_fail("picker_highlight_empty")
		return
	var cyc: Dictionary = _ctrl.call("cycle_module", 1) as Dictionary
	if not bool(cyc.get("ok", false)):
		_fail("cycle_module", str(cyc))
		return
	if str(cyc.get("via", "")) != "input_cycle":
		_fail("cycle_via_input", str(cyc.get("via")))
		return
	var h1 := str((cyc.get("picker", {}) as Dictionary).get("highlighted_module_id", ""))
	if h1.is_empty() or h1 == h0:
		# allow same if size 1
		if int(p0.get("count", 0)) > 1 and h1 == h0:
			_fail("cycle_did_not_advance", "h0=%s h1=%s" % [h0, h1])
			return
	# Place highlighted — playable path.
	var placed: Dictionary = _ctrl.call("place_highlighted_module") as Dictionary
	if not bool(placed.get("ok", false)):
		_fail("place_highlighted", str(placed))
		return
	if bool(placed.get("api_injected", true)):
		_fail("place_must_not_flag_api_injected")
		return
	if str(placed.get("via", "")) != "input_place_highlighted":
		_fail("place_via", str(placed.get("via")))
		return
	var st: Dictionary = _ctrl.call("get_active_state") as Dictionary
	if not bool(st.get("active", false)):
		_fail("preview_active_after_place")
		return
	if str(st.get("module_id", "")) != h1 and str(st.get("module_id", "")) != h0:
		# must match highlighted at place time
		var hi := h1 if not h1.is_empty() else h0
		if str(st.get("module_id", "")) != hi:
			_fail("module_matches_highlight", "active=%s hi=%s" % [st.get("module_id"), hi])
			return
	_ok("playable_cycle_and_place_no_select_module_api")


func _test_hud_plain_language() -> void:
	var hud: Dictionary = _ctrl.call("get_hud_state") as Dictionary
	for k in ["module", "context", "snap", "validity", "validity_reason", "rotation", "elevation", "confirm_enabled", "cancel_enabled"]:
		if not hud.has(k):
			_fail("hud_missing_key", k)
			return
	var reason := str(hud.get("validity_reason", ""))
	if reason.find("Dictionary") >= 0 or reason.find("{") >= 0:
		_fail("hud_not_plain", reason)
		return
	if not bool(hud.get("cancel_enabled", false)):
		_fail("cancel_enabled_when_active")
		return
	_hud.call("set_build_visible", true)
	_hud.call("refresh")
	_ok("hud_plain_language_fields")


func _test_elevation_and_cancel_keep_committed() -> void:
	_ctrl.call("elevate", 2)
	var st: Dictionary = _ctrl.call("get_active_state") as Dictionary
	var elev := float((st.get("placement", {}) as Dictionary).get("elevation", -1))
	if elev < 0.4:
		_fail("elevate_after_place", str(elev))
		return
	# Commit one, then new place, cancel — committed stays.
	var c1: Dictionary = _ctrl.call("confirm_and_commit", true) as Dictionary
	if not bool(c1.get("ok", false)):
		_fail("commit_for_cancel_test", str(c1))
		return
	var committed := int(_ctrl.call("get_committed_count"))
	_ctrl.call("place_highlighted_module")
	var can: Dictionary = _ctrl.call("cancel_preview") as Dictionary
	if not bool(can.get("committed_untouched", false)):
		_fail("cancel_committed_untouched")
		return
	if int(_ctrl.call("get_committed_count")) != committed:
		_fail("cancel_must_keep_committed")
		return
	_ok("elevation_and_cancel_keep_committed")
