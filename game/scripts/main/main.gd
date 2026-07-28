## Main playable 2.5D shell – wires player, fixed-angle camera, world, UI.
## H1-CONSOLIDATE-001: Companion-led five-minute flow; product chrome (no diagnostic wall).
## CTRL-1B-002 B1: ControlContextRouter integration, context HUD, Cozy V/B, Esc priority.
extends Node3D

## G3 Starter Realm UI shell (W1 core). Preload path avoids class_name DB under -s.
const _StarterRealmController := preload("res://scripts/modules/g3_ui/starter_realm_controller.gd")
## G4-001 CORRECTION R2: real PersistModule for ModuleRegistry persist slot.
const _PersistModule := preload("res://scripts/modules/persist/persist_module.gd")
const _StarterRealmBuilder := preload("res://scripts/modules/asset/starter_realm_builder.gd")
const _DesktopBridge := preload("res://scripts/modules/bridge/desktop_bridge_module.gd")
const _HeadedDemoFlow := preload("res://scripts/modules/executor/headed_demo_flow.gd")
const _ActionBarScene := preload("res://scenes/ui/playable_action_bar.tscn")
const _ChatPanelScene := preload("res://scenes/ui/companion_chat_panel.tscn")
const _ContextHudScene := preload("res://scenes/ui/context_action_hud.tscn")
const _ControlSettingsScene := preload("res://scenes/ui/control_settings_panel.tscn")
const _HomesteadScene := preload("res://scenes/ui/cozy_homestead_panel.tscn")
const _HelperPulseScript := preload("res://scripts/ui/cozy_helper_pulse.gd")
const _InspectPanelScript := preload("res://scripts/ui/control_1b_inspect_panel.gd")
const _ProposalCardScript := preload("res://scripts/ui/control_1b_proposal_card.gd")
const _CursorLabelScript := preload("res://scripts/ui/control_1b_cursor_label.gd")
## P2E-001 Block Assembly preview controller (local World Commit only).
const _BlockAssemblyCtrl := preload("res://scripts/modules/block_assembly/block_assembly_controller.gd")
const _BlockAssemblyHud := preload("res://scripts/modules/block_assembly/block_assembly_hud.gd")
## UCBV-001 U5: Nori-7 procedural presenter + BA anim bridge (presentation only).
const _Nori7Presenter := preload("res://scripts/modules/ucbv_001/nori7_presenter.gd")
const _CastRosterLoader := preload("res://scripts/modules/ucbv_001/cast_roster_loader.gd")
const _P1eModuleKit := preload("res://scripts/modules/p1e_cozy/p1e_module_kit.gd")
const _RoyalLightkeepSpawner := preload("res://scripts/modules/p1e_cozy/royal_lightkeep_spawner.gd")
const _UcbvBaAnimBridge := preload("res://scripts/modules/ucbv_001/ucbv_ba_anim_bridge.gd")
## Town 10-phase mockup-parity layout (presentation spawn only).
## SUPERSEDED as live cadastre by town_grid_loader (WO-TOWN-GRID-IMPORT-001 / D99).
## Kept for optional legacy smoke; default off so plots use the named grid plan.
const _TownLayoutLoader := preload("res://scripts/modules/town/town_layout_loader.gd")
const _TownGridLoader := preload("res://scripts/modules/town/town_grid_loader.gd")
const _TownStreetLoader := preload("res://scripts/modules/town/town_street_loader.gd")
## Directive 99 Tier-1: named-plot cadastre (50 plots). Default ON.
const ENABLE_TOWN_GRID_CADASTRE := true
## WO-TOWN-STREET-IMPORT-001 Phase A: stone_path_network only (Phase B wood decks skipped).
const ENABLE_TOWN_STREET_PATHS := true
## Prior 10-phase ring dump — default OFF (superseded; file not deleted).
const ENABLE_TOWN_10PHASE_LEGACY := false
## Royal Lightkeep landmark (PASS5 materials GLB) — presentation spawn outside town ring.
const ENABLE_ROYAL_LIGHTKEEP_LANDMARK := true

@onready var world_root: WorldRoot = $WorldRoot
@onready var player: CharacterBody3D = $Player
@onready var camera_rig: CozyCamera = $CozyCamera

var _action_bar: CanvasLayer
var _chat_panel: Control
var _chat_visible: bool = false
## R-C5H1-03: restore this ControlContext when Companion closes (e.g. "build").
var _companion_return_context: String = "exploration"
var _demo_flow: Node
var _bridge: Node
var _block_assembly: Node = null
var _block_assembly_hud: CanvasLayer = null
var _nori7_presenter: Node3D = null
var _ucbv_anim_bridge: Node = null
## P2E-CODEX-ESC-DOUBLE-01: while true, cancel_resolved signal must not re-handle Esc.
var _esc_dispatch_guard: bool = false
var _esc_resolve_count: int = 0
var _esc_cancel_apply_count: int = 0

# Control 1B B1/C0 UI
var _context_hud: CanvasLayer
var _control_settings: CanvasLayer
var _homestead: CanvasLayer
var _helper_pulse: CanvasLayer
var _inspect_panel: CanvasLayer
var _proposal_card: CanvasLayer
var _cursor_label: CanvasLayer
var _delete_proposal_ui_visible: bool = false
var _last_delete_proposal: Dictionary = {}
var _last_undo_request: Dictionary = {}
var _last_confirm_result: Dictionary = {}
var _confirm_hold_accum: float = 0.0
var _confirm_holding: bool = false
var _confirm_hold_need: float = 0.0
var _significant_confirm_pending: bool = false
## H1 product chrome: normal runtime hides QA labels / evidence counters / diagnostic wall.
var _product_chrome_mode: bool = true
var _last_companion_proposal: Dictionary = {}
var _flow_stage: String = "launch"


func _ready() -> void:
	if camera_rig and player:
		camera_rig.set_target(player)
	if player and camera_rig and player is PlayerController:
		(player as PlayerController).set_camera_rig(camera_rig)

	# Acceptance trace for G2-001 headless smoke.
	if camera_rig and camera_rig.has_method("is_fixed_angle") and camera_rig.is_fixed_angle():
		print("[Main] Camera mode=fixed-angle 2.5D (pitch locked, no free orbit/FPS).")
	if player:
		print("[Main] Player ready: CharacterBody3D XZ locomotion on ground plane.")

	GameManager.enter_world(world_root, player)

	# Notify private reality occupancy (client space).
	if world_root and world_root.private_reality is RealitySpace:
		(world_root.private_reality as RealitySpace).notify_player_entered(player)

	_spawn_module_stubs()
	_mount_desktop_bridge()
	_mount_starter_realm_controller()
	# Prefer Cozy presentation for first readable alpha view when style is missing.
	if ArtStyleManager and not ArtStyleManager.has_chosen_style():
		ArtStyleManager.set_active_style(AIdleConstants.DEFAULT_ART_STYLE, false)
	_build_starter_realm()
	_spawn_companion_near_player()
	_mount_playable_ui()
	_mount_control_1b_ui()
	_wire_control_1b_signals()
	_mount_headed_demo_flow()
	_mount_block_assembly()
	_mount_ucbv_nori7_and_bridge()
	_mount_mockup_cast_and_props_production()
	if ENABLE_TOWN_GRID_CADASTRE:
		_mount_town_grid_cadastre()
	if ENABLE_TOWN_STREET_PATHS:
		_mount_town_street_paths()
	if ENABLE_TOWN_10PHASE_LEGACY:
		_mount_cozy_town_10phase()
	if ENABLE_ROYAL_LIGHTKEEP_LANDMARK:
		_mount_royal_lightkeep_landmark()
	_apply_product_chrome()
	_flow_stage = "ready"
	_set_realm_status("Talk to Companion (E) to begin")

	if SettingsManager.get_value(SettingsManager.SECTION_DEBUG, "verbose_logs", false):
		print("[Main] Entered Private Reality | style=%s" % ArtStyleManager.get_active_style_id())
	print(
		"[Main] Product shell ready | companion-led | style=%s | product_chrome=%s"
		% [ArtStyleManager.get_active_style_id(), str(_product_chrome_mode)]
	)


func _process(delta: float) -> void:
	# Manual Build: snapped hologram follows cursor while Build owns placement.
	_update_manual_build_cursor()
	# Confirmation hold for significant confirms (C1B-A11Y-12 / H-19) — not demo-only.
	if not _confirm_holding:
		return
	if not _has_significant_confirm_target():
		_confirm_holding = false
		_confirm_hold_accum = 0.0
		_set_pending_confirmation_target(false)
		return
	_confirm_hold_accum += delta
	if _confirm_hold_accum + 0.0001 >= _confirm_hold_need:
		_confirm_holding = false
		_confirm_hold_accum = 0.0
		_set_pending_confirmation_target(false)
		_on_confirm()


func _update_manual_build_cursor() -> void:
	if _block_assembly == null or not is_instance_valid(_block_assembly):
		return
	if not _block_assembly.has_method("is_manual_cursor_follow"):
		return
	if not bool(_block_assembly.call("is_manual_cursor_follow")):
		return
	if not _block_assembly.has_method("update_cursor_screen"):
		return
	var cam := _active_camera3d()
	if cam == null:
		return
	var screen := get_viewport().get_mouse_position()
	_block_assembly.call("update_cursor_screen", screen, cam)


func _active_camera3d() -> Camera3D:
	if camera_rig != null and camera_rig.has_method("get_camera"):
		var c: Variant = camera_rig.call("get_camera")
		if c is Camera3D:
			return c as Camera3D
	if camera_rig != null:
		var n := camera_rig.get_node_or_null("Camera3D")
		if n is Camera3D:
			return n as Camera3D
	var vp := get_viewport()
	if vp != null:
		return vp.get_camera_3d()
	return null


func _input(event: InputEvent) -> void:
	## Consume Esc early so GameManager pause only runs after cancel priority (C1B-ESC-01).
	## C2R: accept remappable InputEventAction as well as InputEventKey (InputMap player path).
	if event.is_echo():
		return
	# Manual Build mouse path (LMB place preview / RMB cancel once) — not key-only.
	if event is InputEventMouseButton and (event as InputEventMouseButton).pressed:
		if _handle_manual_build_mouse(event as InputEventMouseButton):
			return

	# Confirm hold early-release must observe key/action release (was dead under key-only filter).
	if event.is_action_released("confirm_action"):
		if _confirm_holding:
			# Early release before hold completes cannot confirm (H-19 / H-29).
			if _confirm_hold_need > 0.001 and _confirm_hold_accum + 0.0001 < _confirm_hold_need:
				print(
					"[Main] confirm hold aborted early accum=%.3f need=%.3f"
					% [_confirm_hold_accum, _confirm_hold_need]
				)
			_confirm_holding = false
			_confirm_hold_accum = 0.0
			_set_pending_confirmation_target(false)
		return

	# Press path: physical keys OR remappable InputEventAction (parse_input_event / InputMap).
	if not _is_remappable_action_press(event):
		return

	var router := _control_router()
	if router == null:
		return

	# Esc / cancel_action / pause_menu — single-dispatch only (P2E-CODEX-ESC-DOUBLE-01).
	# just_pressed blocks key-repeat; signal path is suppressed while _esc_dispatch_guard is true.
	var esc_hit := event.is_action_pressed("cancel_action") or event.is_action_pressed("pause_menu")
	if esc_hit:
		# Key-repeat: only the first just_pressed counts.
		if not Input.is_action_just_pressed("cancel_action") and not Input.is_action_just_pressed("pause_menu"):
			get_viewport().set_input_as_handled()
			return
		if GameManager.state == GameManager.GameState.PAUSED:
			return  # let GameManager unpause via unhandled
		if GameManager.state == GameManager.GameState.SETTINGS:
			return
		# Control settings panel owns Esc when open.
		if _control_settings != null and _control_settings.has_method("is_open") \
				and bool(_control_settings.call("is_open")):
			_control_settings.call("close_panel")
			get_viewport().set_input_as_handled()
			return
		# C5H1: open Companion dismisses on Esc before build-preview cancel priority.
		# Defined outcome with active preview: first Esc closes composer (releases locomotion);
		# second Esc keeps existing preview / build_esc_no_pause path unregressed.
		if _chat_visible:
			_close_companion_composer()
			get_viewport().set_input_as_handled()
			return
		# Exactly one resolve_escape + one _handle_cancel_resolved (not also via cancel_resolved).
		var ctx_esc := str(router.call("get_primary_context"))
		if (ctx_esc == "build" or _ba_preview_active()) and router.has_method("set_cancel_target") and _ba_preview_active():
			router.call("set_cancel_target", "preview_hologram", true)
		_esc_dispatch_guard = true
		var resolved: Dictionary = router.call("resolve_escape") as Dictionary
		if bool(resolved.get("pause", false)) and ctx_esc == "build":
			resolved["pause"] = false
			resolved["resolved"] = "build_esc_no_pause"
		_handle_cancel_resolved(resolved)
		_esc_dispatch_guard = false
		get_viewport().set_input_as_handled()
		return

	# Foundation hotkeys via router (no raw keycode gameplay paths).
	# C5H1: companion_call / prompt_quick_open toggle — close when already open (Human H1 deadlock).
	# Close path does not re-dispatch open; open path keeps try_dispatch + composer open.
	if event.is_action_pressed("prompt_quick_open"):
		if _chat_visible:
			_close_companion_composer()
			get_viewport().set_input_as_handled()
			return
		if router.call("is_action_allowed", "prompt_quick_open"):
			router.call("try_dispatch", "prompt_quick_open")
			_open_companion_composer(true)
			get_viewport().set_input_as_handled()
		return

	if event.is_action_pressed("companion_call"):
		if _chat_visible:
			_close_companion_composer()
			get_viewport().set_input_as_handled()
			return
		if router.call("is_action_allowed", "companion_call"):
			router.call("try_dispatch", "companion_call")
			_open_companion_composer(true)
			get_viewport().set_input_as_handled()
		return

	if event.is_action_pressed("build_mode_toggle"):
		if router.call("is_action_allowed", "build_mode_toggle") \
				or str(router.call("get_primary_context")) in ["exploration", "build"]:
			router.call("try_dispatch", "build_mode_toggle")
			get_viewport().set_input_as_handled()
		return

	if event.is_action_pressed("world_ability") or event.is_action_pressed("cozy_helper_pulse"):
		if router.call("is_action_allowed", "world_ability") \
				or router.call("is_action_allowed", "cozy_helper_pulse"):
			router.call("try_dispatch", "world_ability")
			_fire_helper_pulse("world_ability")
			get_viewport().set_input_as_handled()
		return

	if event.is_action_pressed("world_panel") or event.is_action_pressed("cozy_homestead_panel"):
		if router.call("is_action_allowed", "world_panel") \
				or router.call("is_action_allowed", "cozy_homestead_panel"):
			router.call("try_dispatch", "world_panel")
			_toggle_homestead()
			get_viewport().set_input_as_handled()
		return

	if event.is_action_pressed("inspect_entity"):
		if router.call("is_action_allowed", "inspect_entity"):
			router.call("try_dispatch", "inspect_entity")
			_open_inspect_panel()
			get_viewport().set_input_as_handled()
		return

	if event.is_action_pressed("delete_proposal"):
		if router.call("is_action_allowed", "delete_proposal"):
			router.call("try_dispatch", "delete_proposal", {"source": "main_input"})
			# C2: also arm delete mode when dispatch only emitted signal (already handled in _on_delete_proposal).
			get_viewport().set_input_as_handled()
		return

	if event.is_action_pressed("request_undo"):
		if router.call("is_action_allowed", "request_undo"):
			router.call("try_dispatch", "request_undo", {"source": "main_input"})
			get_viewport().set_input_as_handled()
		return

	if event.is_action_pressed("build_rotate_right") or event.is_action_pressed("build_rotate_left"):
		var aid := "build_rotate_right" if event.is_action_pressed("build_rotate_right") else "build_rotate_left"
		if router.call("is_action_allowed", aid):
			# F04: freeze camera yaw before build rotate so residual lerp cannot move yaw.
			_freeze_camera_yaw_for_build()
			router.call("try_dispatch", aid)
			get_viewport().set_input_as_handled()
		return

	# P2E playable module picker (F03) — remappable InputMap, never API injection in evidence path.
	if event.is_action_pressed("build_module_next") or event.is_action_pressed("build_module_prev"):
		var mdir := 1 if event.is_action_pressed("build_module_next") else -1
		var maid := "build_module_next" if mdir > 0 else "build_module_prev"
		if router.call("is_action_allowed", maid):
			router.call("try_dispatch", maid)
			if _block_assembly != null and _block_assembly.has_method("cycle_module"):
				_block_assembly.call("cycle_module", mdir)
			get_viewport().set_input_as_handled()
		return

	if event.is_action_pressed("build_place"):
		if router.call("is_action_allowed", "build_place"):
			router.call("try_dispatch", "build_place")
			# C2 delete mode: LMB/place selects delete target instead of placing.
			if _block_assembly != null and _block_assembly.has_method("is_delete_mode") \
					and bool(_block_assembly.call("is_delete_mode")):
				if _block_assembly.has_method("cycle_delete_target"):
					var dsel: Dictionary = _block_assembly.call("cycle_delete_target", 0) as Dictionary
					if not bool(dsel.get("ok", false)) and _block_assembly.has_method("select_delete_target_by_index"):
						dsel = _block_assembly.call("select_delete_target_by_index", 0) as Dictionary
					_set_realm_status(
						"Delete target %s" % str(dsel.get("entity_id", "(none)"))
						if bool(dsel.get("ok", false))
						else str(dsel.get("reason", "no committed target"))
					)
			else:
				_manual_build_place_from_input()
			get_viewport().set_input_as_handled()
		return

	if event.is_action_pressed("build_cancel"):
		if router.call("is_action_allowed", "build_cancel"):
			if _block_assembly != null and _block_assembly.has_method("is_delete_mode") \
					and bool(_block_assembly.call("is_delete_mode")):
				router.call("try_dispatch", "build_cancel")
				_block_assembly.call("exit_delete_mode", "rmb")
				_delete_proposal_ui_visible = false
				_set_realm_status("Delete mode exited (RMB) — no mutation")
				get_viewport().set_input_as_handled()
				return
			if _ba_preview_active():
				router.call("try_dispatch", "build_cancel")
				_on_cancel()
				get_viewport().set_input_as_handled()
		return

	if event.is_action_pressed("build_elevation_up") or event.is_action_pressed("build_elevation_down"):
		var eaid := "build_elevation_up" if event.is_action_pressed("build_elevation_up") else "build_elevation_down"
		if router.call("is_action_allowed", eaid):
			router.call("try_dispatch", eaid)
			if _block_assembly != null and _block_assembly.has_method("elevate"):
				var eres: Dictionary = _block_assembly.call(
					"elevate", 1 if eaid == "build_elevation_up" else -1
				) as Dictionary
				if bool(eres.get("ok", false)):
					_set_realm_status(
						"Lift: %.2f m (PgUp/PgDn)" % float(eres.get("elevation_m", 0.0))
					)
				else:
					_set_realm_status(str(eres.get("reason", "Lift unavailable")))
			get_viewport().set_input_as_handled()
		return

	# Prompt send (Ctrl+Enter) when composer open (H-03).
	if event.is_action_pressed("prompt_send"):
		if _chat_visible and _chat_panel != null:
			if router.call("is_action_allowed", "prompt_send") \
					or str(router.call("get_primary_context")) == "companion":
				if _chat_panel.has_method("send_current_input"):
					_chat_panel.call("send_current_input")
				get_viewport().set_input_as_handled()
		return

	# Prompt newline (Shift+Enter) — never send (H-03).
	if event.is_action_pressed("prompt_newline"):
		if _chat_visible and _chat_panel != null:
			if router.call("is_action_allowed", "prompt_newline") \
					or str(router.call("get_primary_context")) == "companion":
				if _chat_panel.has_method("insert_newline"):
					_chat_panel.call("insert_newline")
				get_viewport().set_input_as_handled()
		return

	# Confirm with configurable hold for significant targets (H-19).
	# P2E F03-R2: Block Assembly uses immediate player confirm (no hold residual / no API fallback).
	if event.is_action_pressed("confirm_action"):
		if _ba_can_confirm():
			_on_confirm()
			get_viewport().set_input_as_handled()
			return
		if _has_significant_confirm_target():
			_begin_confirm_hold()
			get_viewport().set_input_as_handled()
		return


func _is_remappable_action_press(event: InputEvent) -> bool:
	## True for pressed InputEventKey or pressed InputEventAction (InputMap remappable path).
	if event is InputEventKey:
		return (event as InputEventKey).pressed
	if event is InputEventAction:
		return (event as InputEventAction).pressed
	return false


func _unhandled_input(event: InputEvent) -> void:
	## Legacy interact still toggles companion when exploration allows (E / interact).
	if event.is_action_pressed("interact") or event.is_action_pressed("interact_primary"):
		var router := _control_router()
		if router != null:
			var ctx := str(router.call("get_primary_context"))
			if ctx == "companion":
				return  # composer owns E semantics when focused
			if not router.call("is_action_allowed", "interact_primary") \
					and not router.call("is_action_allowed", "interact"):
				return
		_toggle_companion_chat()
		get_viewport().set_input_as_handled()


func _control_router() -> Node:
	## SceneTree-root relative lookup — never absolute "/root/..." (H1-CODEX-F01).
	return _autoload_node("ControlContextRouter")


func _control_a11y() -> Node:
	## SceneTree-root relative lookup — never absolute "/root/..." (H1-CODEX-F01).
	return _autoload_node("ControlAccessibilitySettings")


func _autoload_node(node_name: String) -> Node:
	## Safe autoload resolve under SceneTree root (headless + headed; no absolute paths).
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


func _mount_control_1b_ui() -> void:
	var ui := get_node_or_null("UI")
	if ui == null:
		ui = Node.new()
		ui.name = "UI"
		add_child(ui)

	if ui.get_node_or_null("ContextActionHUD") == null:
		_context_hud = _ContextHudScene.instantiate() as CanvasLayer
		_context_hud.name = "ContextActionHUD"
		ui.add_child(_context_hud)
	else:
		_context_hud = ui.get_node("ContextActionHUD") as CanvasLayer

	if ui.get_node_or_null("ControlSettingsPanel") == null:
		_control_settings = _ControlSettingsScene.instantiate() as CanvasLayer
		_control_settings.name = "ControlSettingsPanel"
		ui.add_child(_control_settings)
	else:
		_control_settings = ui.get_node("ControlSettingsPanel") as CanvasLayer

	if ui.get_node_or_null("CozyHomesteadPanel") == null:
		_homestead = _HomesteadScene.instantiate() as CanvasLayer
		_homestead.name = "CozyHomesteadPanel"
		ui.add_child(_homestead)
	else:
		_homestead = ui.get_node("CozyHomesteadPanel") as CanvasLayer

	if ui.get_node_or_null("CozyHelperPulse") == null:
		_helper_pulse = _HelperPulseScript.new() as CanvasLayer
		_helper_pulse.name = "CozyHelperPulse"
		ui.add_child(_helper_pulse)
	else:
		_helper_pulse = ui.get_node("CozyHelperPulse") as CanvasLayer

	if ui.get_node_or_null("Control1BInspectPanel") == null:
		_inspect_panel = _InspectPanelScript.new() as CanvasLayer
		_inspect_panel.name = "Control1BInspectPanel"
		ui.add_child(_inspect_panel)
	else:
		_inspect_panel = ui.get_node("Control1BInspectPanel") as CanvasLayer

	if ui.get_node_or_null("Control1BProposalCard") == null:
		_proposal_card = _ProposalCardScript.new() as CanvasLayer
		_proposal_card.name = "Control1BProposalCard"
		ui.add_child(_proposal_card)
	else:
		_proposal_card = ui.get_node("Control1BProposalCard") as CanvasLayer
	if _proposal_card != null and _proposal_card.has_signal("confirm_requested"):
		if not _proposal_card.confirm_requested.is_connected(_on_proposal_card_confirm):
			_proposal_card.confirm_requested.connect(_on_proposal_card_confirm)

	if ui.get_node_or_null("Control1BCursorLabel") == null:
		_cursor_label = _CursorLabelScript.new() as CanvasLayer
		_cursor_label.name = "Control1BCursorLabel"
		ui.add_child(_cursor_label)
	else:
		_cursor_label = ui.get_node("Control1BCursorLabel") as CanvasLayer

	print(
		"[Main] Control 1B UI mounted (context HUD · settings · homestead · helper pulse · inspect · proposal · cursor)."
	)


func _wire_control_1b_signals() -> void:
	var router := _control_router()
	if router == null:
		push_warning("[Main] ControlContextRouter missing — control integration degraded")
		return
	if router.has_signal("pause_requested") and not router.pause_requested.is_connected(_on_router_pause):
		router.pause_requested.connect(_on_router_pause)
	if router.has_signal("cancel_resolved") and not router.cancel_resolved.is_connected(_on_router_cancel):
		router.cancel_resolved.connect(_on_router_cancel)
	if router.has_signal("delete_proposal_requested") \
			and not router.delete_proposal_requested.is_connected(_on_delete_proposal):
		router.delete_proposal_requested.connect(_on_delete_proposal)
	if router.has_signal("undo_compensation_requested") \
			and not router.undo_compensation_requested.is_connected(_on_undo_compensation):
		router.undo_compensation_requested.connect(_on_undo_compensation)
	if router.has_signal("build_rotate_requested") \
			and not router.build_rotate_requested.is_connected(_on_build_rotate):
		router.build_rotate_requested.connect(_on_build_rotate)
	if router.has_signal("context_changed") and not router.context_changed.is_connected(_on_context_changed):
		router.context_changed.connect(_on_context_changed)


func _on_router_pause() -> void:
	if GameManager.state == GameManager.GameState.IN_WORLD:
		GameManager.set_paused(true)


func _on_router_cancel(target: String, action_id: String) -> void:
	## When Main owns Esc via resolve_escape() return path, ignore signal to prevent double cancel.
	if _esc_dispatch_guard:
		return
	# Non-Esc callers (try_dispatch cancel without main return handling) still apply once.
	_handle_cancel_resolved({"resolved": target, "pause": false, "action_id": action_id})


func _handle_cancel_resolved(resolved: Dictionary) -> void:
	var target := str(resolved.get("resolved", ""))
	var do_pause := bool(resolved.get("pause", false))
	_esc_resolve_count += 1
	# C2: Esc exits Delete red-X without mutation (single-dispatch still applies).
	if _block_assembly != null and _block_assembly.has_method("is_delete_mode") \
			and bool(_block_assembly.call("is_delete_mode")):
		_block_assembly.call("exit_delete_mode", "esc")
		_delete_proposal_ui_visible = false
		_esc_cancel_apply_count += 1
		_set_realm_status("Delete mode exited (Esc) — no mutation")
		return
	match target:
		"pending_confirmation":
			_confirm_holding = false
			_confirm_hold_accum = 0.0
			_set_realm_status("Confirmation cancelled")
		"preview_hologram":
			if _block_assembly != null and _block_assembly.has_method("cancel_preview"):
				_block_assembly.call("cancel_preview")
				_esc_cancel_apply_count += 1
			if _demo_flow and _demo_flow.has_method("cancel_pending"):
				_demo_flow.call("cancel_pending")
			_set_realm_status("Preview cancelled (no orphan)")
		"prompt_composer_or_dialogue":
			_close_companion_composer()
			_set_realm_status("Composer closed")
		"inspect_panel":
			if _inspect_panel and _inspect_panel.has_method("close_panel"):
				_inspect_panel.call("close_panel")
			_set_realm_status("Inspect closed")
		"world_tool_panel":
			if _homestead and _homestead.has_method("close_panel"):
				_homestead.call("close_panel")
			_set_realm_status("Homestead closed")
		"build_mode_idle_exit", "build_esc_no_pause":
			_set_realm_status("Build Esc (no pause)")
		"pause_menu":
			do_pause = true
	if do_pause:
		_on_router_pause()
	print(
		"[Main] Esc resolved → %s pause=%s resolve_n=%d cancel_apply_n=%d"
		% [target, str(do_pause), _esc_resolve_count, _esc_cancel_apply_count]
	)


func get_esc_dispatch_counts() -> Dictionary:
	return {
		"resolve_count": _esc_resolve_count,
		"cancel_apply_count": _esc_cancel_apply_count,
	}


func reset_esc_dispatch_counts() -> void:
	_esc_resolve_count = 0
	_esc_cancel_apply_count = 0


func _on_delete_proposal(payload: Dictionary) -> void:
	## C2: enter Delete red-X mode on Block Assembly — never direct durable delete.
	_last_delete_proposal = payload.duplicate(true)
	_last_delete_proposal["ui"] = "delete_red_x_mode"
	_last_delete_proposal["mutation_class"] = "proposal_only"
	_last_delete_proposal["direct_durable"] = false
	_last_delete_proposal["direct_scene_tree_delete"] = false
	_delete_proposal_ui_visible = true
	if _block_assembly != null and _block_assembly.has_method("begin_delete_mode"):
		var dres: Dictionary = _block_assembly.call("begin_delete_mode") as Dictionary
		_last_delete_proposal["delete_mode"] = dres
		_last_delete_proposal["cursor"] = "red_x"
		if _block_assembly_hud != null and _block_assembly_hud.has_method("set_build_visible"):
			_block_assembly_hud.call("set_build_visible", true)
		_set_realm_status("Delete red-X · LMB select owned · Enter confirm · Esc/RMB exit")
	else:
		_set_realm_status("Delete Proposal (not durable) — confirm path required")
	print("[Main] DELETE_RED_X_MODE mutation_class=proposal_only direct_durable=false")


func _on_undo_compensation(payload: Dictionary) -> void:
	## Compensation request only — does not erase history (C1B-SAFE-03, HK-07).
	## P2E-001: route through Block Assembly authority path when present (not SceneTree delete).
	_last_undo_request = payload.duplicate(true)
	_last_undo_request["mutation_class"] = "compensation_request"
	_last_undo_request["erases_history"] = false
	_last_undo_request["direct_durable"] = false
	if _block_assembly != null and _block_assembly.has_method("request_undo_compensation"):
		var urec: Dictionary = _block_assembly.call("request_undo_compensation") as Dictionary
		_last_undo_request["authority_result"] = urec
		_last_undo_request["authority_path"] = true
		_last_undo_request["direct_scene_tree_delete"] = false
	_set_realm_status("Undo compensation requested (history retained)")
	print("[Main] UNDO_COMPENSATION_REQUEST erases_history=false direct_durable=false")


func _on_build_rotate(direction: int) -> void:
	## Build-only hologram rotate when preview active (C1B-HK-09 / P2E-001 / UCBV C2).
	## Camera yaw must remain exactly unchanged (F04).
	## When no preview: explain why Q/R cannot rotate (never silent rotated=false).
	_freeze_camera_yaw_for_build()
	var yaw_before := _camera_yaw_now()
	var degrees := 15.0 * float(direction)
	var rotated := false
	var rotate_reason := ""
	# Prefer P2E Block Assembly active preview (camera yaw never touched here).
	if _block_assembly != null and _block_assembly.has_method("rotate_preview_degrees"):
		var rres: Variant = _block_assembly.call("rotate_preview_degrees", degrees)
		if rres is Dictionary:
			var rd: Dictionary = rres
			rotated = bool(rd.get("rotated", rd.get("ok", false)))
			rotate_reason = str(rd.get("reason", rd.get("message", "")))
		else:
			rotated = bool(rres)
	if not rotated and _demo_flow != null and _demo_flow.has_method("rotate_active_preview"):
		rotated = bool(_demo_flow.call("rotate_active_preview", degrees))
	if not rotated and rotate_reason.is_empty():
		# Fallback: find any preview manifestation instance.
		for n in get_tree().get_nodes_in_group("manifestation_instances"):
			if n != null and n.has_method("rotate_preview") and n.has_method("is_finalized"):
				if not bool(n.call("is_finalized")) and not bool(n.call("is_cancelled")):
					n.call("rotate_preview", degrees)
					rotated = true
					break
	if not rotated and rotate_reason.is_empty():
		rotate_reason = "Q/R cannot rotate — no active preview. Place a module (LMB or P) first."
	_freeze_camera_yaw_for_build()
	var yaw_after := _camera_yaw_now()
	if rotated:
		_set_realm_status("Build rotate %s°" % str(int(degrees)))
	else:
		_set_realm_status(rotate_reason)
	print(
		"[Main] build_rotate dir=%d rotated=%s reason=%s camera_yaw_before=%.6f camera_yaw_after=%.6f unchanged=%s"
		% [
			direction,
			str(rotated),
			rotate_reason if not rotated else "ok",
			yaw_before,
			yaw_after,
			str(is_equal_approx(yaw_before, yaw_after)),
		]
	)


func _on_context_changed(prev: String, new_ctx: String) -> void:
	_set_realm_status("Context: %s → %s" % [prev, new_ctx])
	if player and player.has_method("set_locomotion_suppressed"):
		var suppress := new_ctx == "companion" and _chat_visible
		player.call("set_locomotion_suppressed", suppress)
	# P2E: BA HUD + camera freeze + picker open in Build; hide diagnostic clutter (F05-R2).
	if new_ctx == "build":
		_freeze_camera_yaw_for_build()
		if camera_rig != null:
			camera_rig.allow_yaw_snaps = false
		if _block_assembly != null and _block_assembly.has_method("open_picker"):
			_block_assembly.call("open_picker")
		if _block_assembly_hud != null and _block_assembly_hud.has_method("set_build_visible"):
			_block_assembly_hud.call("set_build_visible", true)
		if _context_hud != null and _context_hud.has_method("set_compact_build_mode"):
			_context_hud.call("set_compact_build_mode", true)
		_set_build_ui_declutter(true)
	else:
		if camera_rig != null:
			camera_rig.allow_yaw_snaps = true
		if _block_assembly != null and _block_assembly.has_method("close_picker"):
			_block_assembly.call("close_picker")
		if _block_assembly_hud != null and _block_assembly_hud.has_method("set_build_visible"):
			_block_assembly_hud.call("set_build_visible", false)
		if _context_hud != null and _context_hud.has_method("set_compact_build_mode"):
			_context_hud.call("set_compact_build_mode", false)
		_set_build_ui_declutter(false)


func _ba_preview_active() -> bool:
	if _block_assembly == null or not _block_assembly.has_method("get_active_state"):
		return false
	var st: Dictionary = _block_assembly.call("get_active_state") as Dictionary
	return bool(st.get("active", false))


func _ba_can_confirm() -> bool:
	if _block_assembly == null:
		return false
	if _block_assembly.has_method("can_confirm"):
		return bool(_block_assembly.call("can_confirm"))
	return _ba_preview_active()


func _set_build_ui_declutter(in_build: bool) -> void:
	## Hide diagnostic/debug surfaces so BA plain HUD is primary (F05-R2).
	## Cursor label layer stays mounted; internal proxy respects a11y (H1-HUMAN-UX-02).
	if _cursor_label != null:
		if in_build:
			_cursor_label.visible = false
		else:
			_apply_cursor_label_a11y_visibility()
	if _inspect_panel != null and in_build and _inspect_panel.has_method("close_panel"):
		_inspect_panel.call("close_panel")
	if _helper_pulse != null and in_build:
		_helper_pulse.visible = false
	elif _helper_pulse != null:
		_helper_pulse.visible = true
	# Always restore OS pointer when entering build / leaving custom cursor (F02-R2 / UX-02).
	Input.set_custom_mouse_cursor(null)
	if not in_build and _block_assembly != null and _block_assembly.has_method("end_manual_build_mode"):
		# Leaving Build context ends Manual Build follow (Exploration owns camera again).
		_block_assembly.call("end_manual_build_mode")
	var dbg := get_tree().get_first_node_in_group("debug_overlay") if get_tree() else null
	if dbg != null:
		dbg.visible = not in_build and bool(SettingsManager.is_debug_overlay_enabled()) if SettingsManager else not in_build


func _apply_cursor_label_a11y_visibility() -> void:
	## Default: no forced square proxy layer — only optional near-cursor label when a11y on.
	if _cursor_label == null:
		return
	var show_lbl := false
	var a11y := _control_a11y()
	if a11y != null and "action_label_near_cursor" in a11y:
		show_lbl = bool(a11y.action_label_near_cursor)
	# Layer can stay active for a11y scale consumers; product chrome defaults label off.
	_cursor_label.visible = show_lbl or (
		a11y != null and "cursor_size_scale" in a11y and float(a11y.cursor_size_scale) > 1.01
	)


func _handle_manual_build_mouse(event: InputEventMouseButton) -> bool:
	## Returns true when event consumed. LMB = preview place/move; RMB = cancel once.
	var router := _control_router()
	if router == null:
		return false
	var ctx := str(router.call("get_primary_context")) if router.has_method("get_primary_context") else ""
	if ctx != "build":
		return false
	if event.button_index == MOUSE_BUTTON_LEFT:
		if router.call("is_action_allowed", "build_place"):
			router.call("try_dispatch", "build_place")
			_manual_build_place_from_input()
			get_viewport().set_input_as_handled()
			return true
		return false
	if event.button_index == MOUSE_BUTTON_RIGHT:
		if _ba_preview_active() and (
			router.call("is_action_allowed", "build_cancel")
			or router.call("is_action_allowed", "cancel_action")
		):
			if router.has_method("try_dispatch"):
				router.call("try_dispatch", "build_cancel")
			_on_cancel()
			get_viewport().set_input_as_handled()
			return true
	return false


func _manual_build_place_from_input() -> void:
	if _block_assembly == null:
		return
	var cam := _active_camera3d()
	var screen := get_viewport().get_mouse_position()
	if _block_assembly.has_method("place_at_cursor") and cam != null:
		var placed: Dictionary = _block_assembly.call("place_at_cursor", screen, cam) as Dictionary
		_set_preview_buttons(bool(placed.get("ok", false)) or _ba_preview_active())
		_significant_confirm_pending = _ba_can_confirm()
		_set_realm_status(
			"Preview %s · confirm to commit"
			% str((placed.get("state", {}) as Dictionary).get("module_id", placed.get("via", "placed")))
		)
		return
	if _block_assembly.has_method("place_highlighted_module"):
		var placed2: Dictionary = _block_assembly.call("place_highlighted_module") as Dictionary
		_set_realm_status(
			"Place %s" % str((placed2.get("state", {}) as Dictionary).get("module_id", placed2.get("ok", false)))
		)


func _freeze_camera_yaw_for_build() -> void:
	if camera_rig == null:
		return
	if camera_rig.has_method("freeze_yaw_now"):
		camera_rig.call("freeze_yaw_now")
	elif camera_rig.has_method("get_yaw"):
		# Direct property sync if freeze helper unavailable.
		var y := float(camera_rig.call("get_yaw"))
		if "_yaw" in camera_rig:
			camera_rig._yaw = y
		if "_target_yaw" in camera_rig:
			camera_rig._target_yaw = y


func _camera_yaw_now() -> float:
	if camera_rig != null and camera_rig.has_method("get_yaw"):
		return float(camera_rig.call("get_yaw"))
	return 0.0


func _fire_helper_pulse(reason: String) -> void:
	if _helper_pulse and _helper_pulse.has_method("fire_pulse"):
		var res: Dictionary = _helper_pulse.call("fire_pulse", reason) as Dictionary
		_set_realm_status("Helper Pulse (non-durable)")
		print("[Main] Helper Pulse → %s" % str(res.get("non_durable", false)))


func _toggle_homestead() -> void:
	if _homestead and _homestead.has_method("toggle_panel"):
		_homestead.call("toggle_panel")


func _open_companion_composer(focus_input: bool = true) -> void:
	_chat_visible = true
	if _chat_panel:
		_chat_panel.visible = true
		if focus_input and _chat_panel.has_method("focus_input"):
			_chat_panel.call("focus_input")
		elif focus_input and _chat_panel.has_method("open_and_focus"):
			_chat_panel.call("open_and_focus")
	var router := _control_router()
	if router != null:
		# R-C5H1-03: remember prior context (build) so close restores it.
		if router.has_method("get_primary_context"):
			var prior := str(router.call("get_primary_context"))
			if prior != "companion" and not prior.is_empty():
				_companion_return_context = prior
			elif _ba_preview_active() or prior == "build":
				_companion_return_context = "build"
		if router.has_method("set_cancel_target"):
			router.call("set_cancel_target", "prompt_composer_or_dialogue", true)
		if router.has_method("request_context"):
			router.call("request_context", "companion")
	if player and player.has_method("set_locomotion_suppressed"):
		player.call("set_locomotion_suppressed", true)
	print("[Main] Companion composer open focus=%s return_ctx=%s" % [str(focus_input), _companion_return_context])
	_set_realm_status("Companion composer open (text-only)")


func _close_companion_composer() -> void:
	_chat_visible = false
	if _chat_panel:
		_chat_panel.visible = false
		if _chat_panel.has_method("release_focus_input"):
			_chat_panel.call("release_focus_input")
	var router := _control_router()
	if router != null:
		if router.has_method("set_cancel_target"):
			router.call("set_cancel_target", "prompt_composer_or_dialogue", false)
		if router.has_method("get_primary_context") and str(router.call("get_primary_context")) == "companion":
			# R-C5H1-03: restore build (or last non-companion) instead of always exploration.
			var restore := _companion_return_context
			if restore.is_empty() or restore == "companion":
				restore = "exploration"
			# If preview still active, force build return.
			if _ba_preview_active():
				restore = "build"
			if router.has_method("request_context"):
				router.call("request_context", restore)
	if player and player.has_method("set_locomotion_suppressed"):
		player.call("set_locomotion_suppressed", false)
	print("[Main] Companion composer closed restore_ctx=%s" % _companion_return_context)


func _spawn_module_stubs() -> void:
	# G4-001 CORRECTION R2: register real PersistModule before remaining stubs.
	_mount_persist_module()

	var stub_defs := [
		[AIdleConstants.MODULE_VOXEL, "Agent-Voxel"],
		[AIdleConstants.MODULE_COMPANION, "Agent-Companion"],
		[AIdleConstants.MODULE_EXECUTOR, "Agent-Executor"],
		[AIdleConstants.MODULE_NETWORK, "Agent-Network"],
		[AIdleConstants.MODULE_SCHEMA, "Agent-Schema"],
		[AIdleConstants.MODULE_ASSET, "Agent-Asset"],
	]
	for def in stub_defs:
		var mid: String = def[0]
		var aname: String = def[1]
		if ModuleRegistry.has_module(mid) and not (ModuleRegistry.get_module(mid) is ModuleStub):
			continue
		var stub := ModuleStub.new()
		stub.module_id = mid
		stub.agent_name = aname
		stub.name = "%sStub" % aname.replace("-", "")
		stub.status_message = "Stub – %s not integrated yet" % aname
		if not ModuleRegistry.attach_to_mount(mid, stub):
			add_child(stub)
		if not ModuleRegistry.has_module(mid):
			ModuleRegistry.register_module(mid, stub)


func _mount_persist_module() -> void:
	var mid: String = AIdleConstants.MODULE_PERSIST
	if ModuleRegistry.has_module(mid):
		var existing: Node = ModuleRegistry.get_module(mid)
		if existing != null and is_instance_valid(existing) and not (existing is ModuleStub):
			print("[Main] PersistModule mounted (real, not AgentPersistStub).")
			return
		if existing != null and is_instance_valid(existing):
			ModuleRegistry.unregister_module(mid)
			existing.queue_free()

	var persist: Node = _PersistModule.new() as Node
	persist.name = "PersistModule"
	if not ModuleRegistry.attach_to_mount(mid, persist):
		add_child(persist)
	if not ModuleRegistry.has_module(mid):
		ModuleRegistry.register_module(mid, persist)
	print("[Main] PersistModule mounted (real, not AgentPersistStub).")


func _mount_desktop_bridge() -> void:
	if ModuleRegistry.has_module("desktop_bridge"):
		var existing: Node = ModuleRegistry.get_module("desktop_bridge")
		if existing != null and not existing.has_method("is_stub"):
			_bridge = existing
			return
		if existing != null and existing.has_method("is_stub") and not bool(existing.call("is_stub")):
			_bridge = existing
			return
	_bridge = _DesktopBridge.new()
	_bridge.name = "DesktopBridgeModule"
	add_child(_bridge)
	print("[Main] DesktopBridgeModule mounted (Free Desktop Bridge, no network).")


func _mount_block_assembly() -> void:
	## P2E-001: offline Block Assembly preview + local World Commit bridge + plain HUD.
	if get_node_or_null("BlockAssemblyController") != null:
		_block_assembly = get_node("BlockAssemblyController")
	else:
		_block_assembly = _BlockAssemblyCtrl.new() as Node
		_block_assembly.name = "BlockAssemblyController"
		add_child(_block_assembly)
	if _block_assembly.has_method("bind_local_authority"):
		var conn: Dictionary = _block_assembly.call("bind_local_authority", 0) as Dictionary
		print(
			"[Main] BlockAssemblyController mounted bind_ok=%s (local World Commit only)."
			% str(conn.get("ok", false))
		)
	else:
		print("[Main] BlockAssemblyController mounted.")

	var ui := get_node_or_null("UI")
	if ui == null:
		ui = Node.new()
		ui.name = "UI"
		add_child(ui)
	if ui.get_node_or_null("BlockAssemblyHUD") == null:
		_block_assembly_hud = _BlockAssemblyHud.new() as CanvasLayer
		_block_assembly_hud.name = "BlockAssemblyHUD"
		ui.add_child(_block_assembly_hud)
	else:
		_block_assembly_hud = ui.get_node("BlockAssemblyHUD") as CanvasLayer
	if _block_assembly_hud != null and _block_assembly_hud.has_method("bind_controller"):
		_block_assembly_hud.call("bind_controller", _block_assembly)
	print("[Main] BlockAssemblyHUD mounted (plain-language Build surface).")


func _mount_ucbv_nori7_and_bridge() -> void:
	## UCBV-001 U5: replace placeholder player capsule visual with Nori-7 production_slice_v1.
	## Locomotion CharacterBody3D / collision unchanged. Anim never World-Commits.
	if player == null or not is_instance_valid(player):
		print("[Main] UCBV Nori-7 skipped — no player.")
		return
	var existing := player.get_node_or_null("Nori7Presenter")
	if existing != null:
		_nori7_presenter = existing as Node3D
	else:
		# Hide legacy capsule presentation mesh only (collision stays).
		var legacy := player.get_node_or_null("MeshInstance3D") as MeshInstance3D
		if legacy != null:
			legacy.visible = false
			legacy.mesh = null
		_nori7_presenter = _Nori7Presenter.new() as Node3D
		_nori7_presenter.name = "Nori7Presenter"
		player.add_child(_nori7_presenter)
	if _nori7_presenter != null and _nori7_presenter.has_method("build_from_assets"):
		var st: Dictionary = _nori7_presenter.call("build_from_assets") as Dictionary
		var built_ok := bool(st.get("built", false))
		print(
			"[Main] Nori-7 presenter built=%s bones=%s character_id=%s slice=%s mode=%s procedural=%s"
			% [
				str(built_ok),
				str(st.get("bone_count", 0)),
				str(st.get("character_id", "")),
				str(st.get("production_slice", "")),
				str(st.get("production_mode", "")),
				str(st.get("procedural_fallback", false)),
			]
		)
		if not built_ok:
			var err := str(st.get("build_error", "unknown"))
			_set_realm_status("Nori-7 fail-closed: %s (no procedural presenter)" % err)
			print("[Main] Nori-7 FAIL_CLOSED %s detail=%s" % [err, str(st.get("build_detail", {}))])
	if get_node_or_null("UcbvBaAnimBridge") != null:
		_ucbv_anim_bridge = get_node("UcbvBaAnimBridge")
	else:
		_ucbv_anim_bridge = _UcbvBaAnimBridge.new() as Node
		_ucbv_anim_bridge.name = "UcbvBaAnimBridge"
		add_child(_ucbv_anim_bridge)
	if (
		_ucbv_anim_bridge != null
		and _ucbv_anim_bridge.has_method("bind_controller")
		and _block_assembly != null
		and _nori7_presenter != null
	):
		var br: Dictionary = _ucbv_anim_bridge.call(
			"bind_controller", _block_assembly, _nori7_presenter
		) as Dictionary
		print("[Main] UCBV BA anim bridge bound=%s (presentation only)." % str(br.get("ok", false)))


func get_block_assembly() -> Node:
	return _block_assembly


func get_block_assembly_hud() -> Node:
	return _block_assembly_hud


func get_nori7_presenter() -> Node:
	return _nori7_presenter


func get_ucbv_anim_bridge() -> Node:
	return _ucbv_anim_bridge


func _on_gardener_action(action_id: String) -> void:
	## Playable action bar gardener row → Nori-7 presentation clips only.
	## Never World Commit / inventory / economy.
	var aid := action_id.strip_edges()
	if aid.is_empty():
		return
	var res: Dictionary = {}
	if _ucbv_anim_bridge != null and _ucbv_anim_bridge.has_method("apply_trigger"):
		res = _ucbv_anim_bridge.call("apply_trigger", aid) as Dictionary
	elif _nori7_presenter != null and _nori7_presenter.has_method("apply_trigger"):
		res = _nori7_presenter.call("apply_trigger", aid) as Dictionary
	else:
		print("[Main] gardener_action ignored — no Nori presenter: %s" % aid)
		return
	print(
		"[Main] gardener_action action=%s ok=%s state=%s client_world_commit=false"
		% [aid, str(res.get("ok", false)), str(res.get("state", res.get("clip", "")))]
	)


func _mount_mockup_cast_and_props_production() -> void:
	## WO-MOCKUP-CAST-PROPS-PRODUCTION-001: 10 Foundry cast GLBs + 10 P1E props in-world.
	## Presentation gallery offset from player; never World-Commits.
	## Kept far from CozyTown so inventory dump does not mix into the town ring.
	var cast_root := get_node_or_null("MockupCastGallery") as Node3D
	if cast_root == null:
		cast_root = _CastRosterLoader.new() as Node3D
		cast_root.name = "MockupCastGallery"
		add_child(cast_root)
	cast_root.global_position = Vector3(28.0, 0.0, -18.0)
	if cast_root.has_method("build_gallery"):
		var cr: Dictionary = cast_root.call("build_gallery", 1.7) as Dictionary
		print(
			"[Main] Mockup cast gallery built=%s total=%s failed=%s"
			% [str(cr.get("built", 0)), str(cr.get("total", 0)), str((cr.get("failed", []) as Array).size())]
		)
		if cast_root.has_method("play_all"):
			cast_root.call("play_all", "idle")
	var prop_root := get_node_or_null("MockupPropGallery") as Node3D
	if prop_root == null:
		prop_root = _P1eModuleKit.new() as Node3D
		prop_root.name = "MockupPropGallery"
		add_child(prop_root)
	prop_root.global_position = Vector3(28.0, 0.0, -8.0)
	if prop_root.has_method("build_gallery"):
		var pr: Dictionary = prop_root.call("build_gallery", 2.4) as Dictionary
		print(
			"[Main] Mockup prop gallery loaded=%s total=%s"
			% [str(pr.get("loaded", 0)), str(pr.get("total", 0))]
		)


func _mount_royal_lightkeep_landmark() -> void:
	## ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01 — full-scale landmark in AIdle Openworld.
	## Parent under PrivateReality ManifestationHost (not Main root). Town LOOKOUT uses
	## the same module_id at reduced scale via town_grid_plan_v1.json.
	## Presentation only — no World Commit.
	var host: Node3D = null
	if world_root != null and world_root.private_reality != null:
		host = world_root.private_reality.get_node_or_null("ManifestationHost") as Node3D
		if host == null:
			host = world_root.private_reality as Node3D
	if host == null:
		host = self

	var lk := host.get_node_or_null("RoyalLightkeepLandmark") as Node3D
	if lk == null:
		lk = _RoyalLightkeepSpawner.new() as Node3D
		lk.name = "RoyalLightkeepLandmark"
		host.add_child(lk)
	if lk.has_method("spawn_landmark"):
		# Full author scale (24×19×38 m) NE of starter realm — visible landmark.
		var lr: Dictionary = lk.call(
			"spawn_landmark", Vector3(-36.0, 0.0, 28.0), 25.0
		) as Dictionary
		print(
			"[Main] RoyalLightkeep WORLD ok=%s meshes=%s pos=(%.1f,%.1f,%.1f) parent=%s err=%s"
			% [
				str(lr.get("ok", false)),
				str(lr.get("mesh_count", 0)),
				float((lr.get("position", {}) as Dictionary).get("x", 0.0)),
				float((lr.get("position", {}) as Dictionary).get("y", 0.0)),
				float((lr.get("position", {}) as Dictionary).get("z", 0.0)),
				str(host.name),
				str(lr.get("error", "")),
			]
		)


func _mount_town_grid_cadastre() -> void:
	## WO-TOWN-GRID-IMPORT-001 / Directive 99: 50 named plots from town_grid_plan_v1.json.
	## Real GLB where authored; honest concept placeholders otherwise. No World Commit.
	var cad := get_node_or_null("TownCadastre") as Node3D
	if cad == null:
		cad = _TownGridLoader.new() as Node3D
		cad.name = "TownCadastre"
		add_child(cad)
	## Plan coords are world-centred (±12); keep at origin so cadastre = realm map.
	cad.global_position = Vector3(0.0, 0.0, 0.0)
	if cad.has_method("build_cadastre"):
		var tr: Dictionary = cad.call("build_cadastre") as Dictionary
		print(
			"[Main] TownCadastre plots=%s real_glb=%s placeholders=%s cast=%s max_abs=%.2f ok=%s"
			% [
				str(tr.get("plots_total", 0)),
				str(tr.get("real_glb", 0)),
				str(tr.get("placeholders", 0)),
				str(tr.get("cast_built", 0)),
				float(tr.get("max_abs_xz", 0.0)),
				str(tr.get("ok", false)),
			]
		)


func _mount_town_street_paths() -> void:
	## WO-TOWN-STREET-IMPORT-001 Phase A: tile stone paths from fairy street plan.
	## Additive; does not touch TownCadastre plots. Phase B wood platforms skipped.
	var street := get_node_or_null("TownStreet") as Node3D
	if street == null:
		street = _TownStreetLoader.new() as Node3D
		street.name = "TownStreet"
		add_child(street)
	street.global_position = Vector3(0.0, 0.0, 0.0)
	if street.has_method("build_streets"):
		var tr: Dictionary = street.call("build_streets") as Dictionary
		print(
			"[Main] TownStreet segments=%s ok=%s tiles=%s max_abs=%.2f ok=%s"
			% [
				str(tr.get("segments_total", 0)),
				str(tr.get("segments_ok", 0)),
				str(tr.get("tiles_placed", 0)),
				float(tr.get("max_abs_xz", 0.0)),
				str(tr.get("ok", false)),
			]
		)


func _mount_cozy_town_10phase() -> void:
	## LEGACY (superseded by TownCadastre). File town_layout_10phase.json not edited in place.
	## Enable only via ENABLE_TOWN_10PHASE_LEGACY for historical smoke.
	var town := get_node_or_null("CozyTown") as Node3D
	if town == null:
		town = _TownLayoutLoader.new() as Node3D
		town.name = "CozyTown"
		add_child(town)
	town.global_position = Vector3(-6.0, 0.0, 10.0)
	if town.has_method("build_town"):
		var tr: Dictionary = town.call("build_town", -1) as Dictionary
		print(
			"[Main] CozyTown(legacy) phases=%s chars=%s modules=%s idle=%s parity=%s runtime=%s missing=%s"
			% [
				str(tr.get("phases_built", 0)),
				str(tr.get("chars_built", 0)),
				str(tr.get("modules_built", 0)),
				str(tr.get("idle_play", 0)),
				str(tr.get("parity_ok", false)),
				str(tr.get("runtime_usable", false)),
				str((tr.get("missing", []) as Array).size()),
			]
		)


func _exit_tree() -> void:
	## F02-R2: release BA presentation + custom cursor textures before RenderingServer dies.
	Input.set_custom_mouse_cursor(null)
	if _block_assembly != null and is_instance_valid(_block_assembly):
		if _block_assembly.has_method("dispose_all_previews"):
			_block_assembly.call("dispose_all_previews")
		if _block_assembly.has_method("dispose_committed_presentation"):
			_block_assembly.call("dispose_committed_presentation")


func _mount_starter_realm_controller() -> void:
	var ui := get_node_or_null("UI")
	var parent: Node = ui if ui != null else self
	if parent.get_node_or_null("StarterRealmController") != null:
		return
	var ctrl: Node = _StarterRealmController.new()
	ctrl.name = "StarterRealmController"
	parent.add_child(ctrl)


func _build_starter_realm() -> void:
	if world_root == null or world_root.private_reality == null:
		return
	# Prefer Bridge quarantine GLB intake (runtime OS path) when package present.
	# Falls back to procedural primitives. No res:// promotion of generated assets.
	var root: Node3D = _StarterRealmBuilder.build_into(world_root.private_reality)
	var count := _StarterRealmBuilder.count_landmarks(world_root.private_reality)
	var via := "procedural"
	if root != null and bool(root.get_meta("glb_intake_realm", false)):
		via = "glb_intake:%s" % str(root.get_meta("intake_job_id", ""))
	print(
		"[Main] Starter Realm landmarks=%d root=%s via=%s"
		% [count, root.name if root else "null", via]
	)


func _spawn_companion_near_player() -> void:
	await get_tree().process_frame
	await get_tree().process_frame
	if player == null:
		return
	if not ModuleRegistry.has_module(AIdleConstants.MODULE_COMPANION):
		return
	var companion: Node = ModuleRegistry.get_module(AIdleConstants.MODULE_COMPANION)
	if companion == null or (companion.has_method("is_stub") and bool(companion.call("is_stub"))):
		return
	var mount: Node = null
	if world_root and world_root.module_mounts:
		mount = world_root.module_mounts.get_node_or_null("CompanionMount")
	if companion.has_method("spawn_companion"):
		companion.call("spawn_companion", player, mount if mount else companion.get_parent())
		print("[Main] Companion spawned near player (text-only).")


func _mount_playable_ui() -> void:
	var ui := get_node_or_null("UI")
	if ui == null:
		ui = Node.new()
		ui.name = "UI"
		add_child(ui)

	# Action bar
	if ui.get_node_or_null("PlayableActionBar") == null:
		_action_bar = _ActionBarScene.instantiate() as CanvasLayer
		_action_bar.name = "PlayableActionBar"
		ui.add_child(_action_bar)
		_wire_action_bar()
	else:
		_action_bar = ui.get_node("PlayableActionBar") as CanvasLayer
		_wire_action_bar()

	# Companion chat panel (hidden until E / button / prompt_quick_open)
	if ui.get_node_or_null("CompanionChatHost") == null:
		var host := CanvasLayer.new()
		host.name = "CompanionChatHost"
		host.layer = 13
		ui.add_child(host)
		_chat_panel = _ChatPanelScene.instantiate() as Control
		_chat_panel.name = "CompanionChatPanel"
		_chat_panel.visible = false
		host.add_child(_chat_panel)
	else:
		_chat_panel = ui.get_node_or_null("CompanionChatHost/CompanionChatPanel") as Control
	_chat_visible = false
	_wire_companion_panel()
	print("[Main] Playable UI mounted (action bar + companion chat panel).")


func _wire_action_bar() -> void:
	if _action_bar == null:
		return
	if _action_bar.has_signal("companion_toggled") and not _action_bar.companion_toggled.is_connected(_toggle_companion_chat):
		_action_bar.companion_toggled.connect(_toggle_companion_chat)
	if _action_bar.has_signal("bridge_export_pressed") and not _action_bar.bridge_export_pressed.is_connected(_on_bridge_export):
		_action_bar.bridge_export_pressed.connect(_on_bridge_export)
	if _action_bar.has_signal("bridge_import_pressed") and not _action_bar.bridge_import_pressed.is_connected(_on_bridge_import):
		_action_bar.bridge_import_pressed.connect(_on_bridge_import)
	if _action_bar.has_signal("demo_build_pressed") and not _action_bar.demo_build_pressed.is_connected(_on_demo_build):
		_action_bar.demo_build_pressed.connect(_on_demo_build)
	if _action_bar.has_signal("confirm_pressed") and not _action_bar.confirm_pressed.is_connected(_on_confirm):
		_action_bar.confirm_pressed.connect(_on_confirm)
	if _action_bar.has_signal("cancel_pressed") and not _action_bar.cancel_pressed.is_connected(_on_cancel):
		_action_bar.cancel_pressed.connect(_on_cancel)
	if _action_bar.has_signal("gardener_action_pressed") and not _action_bar.gardener_action_pressed.is_connected(_on_gardener_action):
		_action_bar.gardener_action_pressed.connect(_on_gardener_action)


func _mount_headed_demo_flow() -> void:
	if get_node_or_null("HeadedDemoFlow") != null:
		_demo_flow = get_node("HeadedDemoFlow")
		return
	_demo_flow = _HeadedDemoFlow.new()
	_demo_flow.name = "HeadedDemoFlow"
	add_child(_demo_flow)
	if _demo_flow.has_signal("flow_status"):
		_demo_flow.flow_status.connect(_on_flow_status)
	if _demo_flow.has_signal("preview_started"):
		_demo_flow.preview_started.connect(func(_pid):
			_set_preview_buttons(true)
			var router := _control_router()
			if router != null and router.has_method("set_cancel_target"):
				router.call("set_cancel_target", "preview_hologram", true)
		)
	if _demo_flow.has_signal("flow_confirmed"):
		_demo_flow.flow_confirmed.connect(func(_pid, _r):
			_set_preview_buttons(false)
			var router := _control_router()
			if router != null and router.has_method("set_cancel_target"):
				router.call("set_cancel_target", "preview_hologram", false)
		)
	if _demo_flow.has_signal("flow_cancelled"):
		_demo_flow.flow_cancelled.connect(func(_pid):
			_set_preview_buttons(false)
			var router := _control_router()
			if router != null and router.has_method("set_cancel_target"):
				router.call("set_cancel_target", "preview_hologram", false)
		)


func _toggle_companion_chat() -> void:
	if _chat_visible:
		_close_companion_composer()
	else:
		_open_companion_composer(true)


func _on_bridge_export() -> void:
	if _bridge == null:
		_mount_desktop_bridge()
	if _bridge == null:
		_set_realm_status("Bridge missing")
		return
	# Free edition: schema-valid UUID snapshot (Directive 24 Bridge evidence).
	var uuid := "a1b2c3d4-e5f6-4789-a012-3456789abcde"
	var ctx := {
		"snapshot_id": uuid,
		"session_id": "session_headed",
		"space_id": "home_01",
		"world_revision": 3,
		"player_id": "player_01",
		"companion_id": "companion_lumi",
	}
	var res: Dictionary = {}
	if _bridge.has_method("export_snapshot_to_file"):
		res = _bridge.call("export_snapshot_to_file", ctx) as Dictionary
	elif _bridge.has_method("export_snapshot_both"):
		res = _bridge.call("export_snapshot_both", ctx) as Dictionary
	elif _bridge.has_method("export_snapshot_to_clipboard"):
		res = _bridge.call("export_snapshot_to_clipboard", ctx) as Dictionary
	var path := str(res.get("path", ""))
	var ok := bool(res.get("ok", false))
	var sid := str(res.get("snapshot_id", uuid))
	_set_realm_status("Bridge export %s · path=%s" % ["OK" if ok else "FAIL", path.get_file() if path else "—"])
	print(
		"[Main] Bridge export manual result ok=%s snapshot_id=%s path=%s bytes=%s"
		% [str(ok), sid, path, str(res.get("bytes", 0))]
	)
	print("[Main] BRIDGE_EVIDENCE_VISIBLE status=%s operation=export_snapshot_to_file" % ("success" if ok else "fail"))


func _on_bridge_import() -> void:
	if _bridge == null:
		_mount_desktop_bridge()
	if _bridge == null:
		return
	# Import from inbox file if present; consent UI required (auto_consent=false).
	if _bridge.has_method("import_decision_from_file"):
		_bridge.call("import_decision_from_file", "", false)
	elif _bridge.has_method("import_decision_from_clipboard"):
		_bridge.call("import_decision_from_clipboard", false)
	_set_realm_status("Import Decision (consent required — no auto-apply)")
	print("[Main] Bridge import requested (consent gate).")


func _on_demo_build() -> void:
	## Product "Manual Build" — cursor-led snapped hologram (H1-HUMAN-BUILD-01).
	## Preview-only until explicit Confirm → World Commit. Never client-canonical.
	var router := _control_router()
	if router != null and router.has_method("request_context"):
		router.call("request_context", "build")
	if _block_assembly != null and _block_assembly.has_method("begin_manual_build"):
		var boot: Dictionary = _block_assembly.call("begin_manual_build") as Dictionary
		if router != null and router.has_method("set_cancel_target"):
			router.call("set_cancel_target", "preview_hologram", true)
		_set_preview_buttons(bool(boot.get("ok", false)))
		_significant_confirm_pending = true
		_flow_stage = "preview"
		_set_preview_banner_stage("hologram")
		_set_realm_status("Manual Build · cursor place · LMB preview · Confirm commits")
		print(
			"[Main] Manual Build → cursor-led BA preview ok=%s preview_only=%s client_world_commit=false"
			% [str(boot.get("ok", false)), str(boot.get("preview_only", true))]
		)
		return
	# Fallback: companion-led BA preview if Manual Build API missing.
	var fallback: Dictionary = begin_companion_led_build({"recipe_id": "cozy_house"})
	if bool(fallback.get("ok", false)):
		print("[Main] Manual Build fallback → companion-led BA preview ok")
		return
	if _demo_flow and _demo_flow.has_method("start_demo_build"):
		var res: Dictionary = _demo_flow.call("start_demo_build") as Dictionary
		print("[Main] Manual Build fallback demo flow → %s" % str(res))
		if router != null and bool(res.get("ok", false)):
			if router.has_method("request_context"):
				router.call("request_context", "build")
			if router.has_method("set_cancel_target"):
				router.call("set_cancel_target", "preview_hologram", true)
			_significant_confirm_pending = true


func _on_confirm() -> void:
	## Significant confirm → World Commit authority only (H-20 / P2E-001). Never client-forged success.
	_confirm_holding = false
	_confirm_hold_accum = 0.0
	_set_pending_confirmation_target(false)
	# P2E Block Assembly: player confirm_action → handle_player_confirm only (no direct confirm_and_commit).
	if _block_assembly != null and _ba_can_confirm():
		_set_preview_banner_stage("materializing")
		var bres: Dictionary = {}
		if _block_assembly.has_method("handle_player_confirm"):
			bres = _block_assembly.call("handle_player_confirm") as Dictionary
		else:
			bres = {"ok": false, "reason": "handle_player_confirm_missing"}
		_last_confirm_result = bres.duplicate(true)
		_last_confirm_result["client_world_commit"] = false
		_last_confirm_result["authority_path"] = "world_commit_service"
		_last_confirm_result["handoff_only"] = false
		_last_confirm_result["via"] = "player_confirm_action"
		_significant_confirm_pending = false
		var status := str((bres.get("receipt", {}) as Dictionary).get("status", bres.get("ok", false)))
		if bool(bres.get("ok", false)):
			_flow_stage = "complete"
			_set_preview_banner_stage("complete")
			_set_preview_buttons(false)
			_set_realm_status("Committed · solid · undo available")
		else:
			_set_realm_status("Confirm status=%s" % status)
		print(
			"[Main] BlockAssembly confirm ok=%s issuer=%s via=player_confirm_action client_world_commit=false"
			% [str(bres.get("ok", false)), str(bres.get("issuer", ""))]
		)
		return
	if _demo_flow and _demo_flow.has_method("confirm_pending"):
		var res: Dictionary = _demo_flow.call("confirm_pending") as Dictionary
		_last_confirm_result = res.duplicate(true) if res is Dictionary else {}
		_last_confirm_result["client_world_commit"] = false
		_last_confirm_result["handoff_only"] = true
		_significant_confirm_pending = false
		_set_realm_status("Confirm handoff only (no client World Commit)")
		print(
			"[Main] Confirm → handoff_only=%s client_world_commit=false durable=%s"
			% [
				str(_last_confirm_result.get("handoff_only", true)),
				str(_last_confirm_result.get("durable_mutation_applied", false)),
			]
		)
		return
	_last_confirm_result = {
		"ok": false,
		"reason": "no_pending",
		"client_world_commit": false,
		"durable_mutation_applied": false,
		"handoff_only": true,
	}


func _on_cancel() -> void:
	_confirm_holding = false
	_confirm_hold_accum = 0.0
	_set_pending_confirmation_target(false)
	if _block_assembly != null and _block_assembly.has_method("is_delete_mode") \
			and bool(_block_assembly.call("is_delete_mode")):
		_block_assembly.call("exit_delete_mode", "cancel_action")
		_delete_proposal_ui_visible = false
		_set_realm_status("Delete mode exited — no mutation")
		return
	if _block_assembly != null and _block_assembly.has_method("cancel_preview"):
		var bcan: Dictionary = _block_assembly.call("cancel_preview") as Dictionary
		print("[Main] BlockAssembly cancel → %s" % str(bcan.get("cancelled", false)))
		_flow_stage = "cancel"
		_set_preview_banner_stage("")
		_set_preview_buttons(false)
		_set_realm_status("Preview cancelled")
	if _demo_flow and _demo_flow.has_method("cancel_pending"):
		var res: Dictionary = _demo_flow.call("cancel_pending") as Dictionary
		print("[Main] Cancel → %s" % str(res))
		var router := _control_router()
		if router != null and router.has_method("set_cancel_target"):
			router.call("set_cancel_target", "preview_hologram", false)
		_significant_confirm_pending = false


func _on_flow_status(text: String) -> void:
	_set_realm_status(text)


func _set_preview_buttons(active: bool) -> void:
	if _action_bar and _action_bar.has_method("set_preview_active"):
		_action_bar.call("set_preview_active", active)


func _set_realm_status(text: String) -> void:
	for n in get_tree().get_nodes_in_group("g3_starter_realm"):
		if n != null and n.has_method("set_status"):
			n.call("set_status", text)


## ─── B1 / C0 smoke accessors ─────────────────────────────────────────────────

func get_last_delete_proposal() -> Dictionary:
	return _last_delete_proposal.duplicate(true)


func get_last_undo_request() -> Dictionary:
	return _last_undo_request.duplicate(true)


func is_delete_proposal_ui_visible() -> bool:
	return _delete_proposal_ui_visible


func get_last_confirm_result() -> Dictionary:
	return _last_confirm_result.duplicate(true)


func is_confirm_holding() -> bool:
	return _confirm_holding


func get_confirm_hold_accum() -> float:
	return _confirm_hold_accum


func get_confirm_hold_need() -> float:
	return _confirm_hold_need


func begin_confirm_hold_for_test() -> Dictionary:
	return _begin_confirm_hold()


func tick_confirm_hold_for_test(delta: float) -> void:
	if not _confirm_holding:
		return
	_confirm_hold_accum += delta
	if _confirm_hold_accum + 0.0001 >= _confirm_hold_need:
		_confirm_holding = false
		_confirm_hold_accum = 0.0
		_set_pending_confirmation_target(false)
		_on_confirm()


func release_confirm_hold_for_test() -> void:
	_confirm_holding = false
	_confirm_hold_accum = 0.0
	_set_pending_confirmation_target(false)


func open_inspect_for_test(payload: Dictionary = {}) -> Dictionary:
	return _open_inspect_panel(payload)


func _has_significant_confirm_target() -> bool:
	if _significant_confirm_pending:
		return true
	if _block_assembly != null and _block_assembly.has_method("get_active_state"):
		var bast: Dictionary = _block_assembly.call("get_active_state") as Dictionary
		if bool(bast.get("active", false)):
			return true
	if _demo_flow != null and _demo_flow.has_method("is_active") and bool(_demo_flow.call("is_active")):
		return true
	var router := _control_router()
	if router != null and router.has_method("get_cancel_targets"):
		var t: Dictionary = router.call("get_cancel_targets") as Dictionary
		if bool(t.get("preview_hologram", false)) or bool(t.get("pending_confirmation", false)):
			return true
	return false


func _begin_confirm_hold() -> Dictionary:
	_confirm_hold_need = 0.8
	var a11y := _control_a11y()
	if a11y != null and "confirmation_hold_seconds" in a11y:
		_confirm_hold_need = float(a11y.confirmation_hold_seconds)
	_confirm_hold_accum = 0.0
	_set_pending_confirmation_target(true)
	if _confirm_hold_need <= 0.001:
		# Hold 0 → immediate confirm (H-19 / H-29).
		_confirm_holding = false
		_set_pending_confirmation_target(false)
		_on_confirm()
		return {"immediate": true, "need": 0.0, "confirmed": true}
	_confirm_holding = true
	print("[Main] confirm hold started need=%.2fs (cannot confirm early)" % _confirm_hold_need)
	return {"immediate": false, "need": _confirm_hold_need, "confirmed": false, "holding": true}


func _set_pending_confirmation_target(active: bool) -> void:
	var router := _control_router()
	if router != null and router.has_method("set_cancel_target"):
		router.call("set_cancel_target", "pending_confirmation", active)


func _open_inspect_panel(payload: Dictionary = {}) -> Dictionary:
	## H-07: read-only provenance surface; no durable mutation.
	if _inspect_panel == null:
		return {"ok": false, "reason": "inspect_panel_missing", "durable_mutation": false}
	var data := payload.duplicate(true) if payload is Dictionary else {}
	if data.is_empty():
		data = _gather_inspect_payload()
	var result: Dictionary = {}
	if _inspect_panel.has_method("open_inspect"):
		result = _inspect_panel.call("open_inspect", data) as Dictionary
	_set_realm_status("Inspect open (read-only provenance)")
	return result


func _gather_inspect_payload() -> Dictionary:
	var payload := {
		"entity_id": "selected_or_nearest",
		"read_only": true,
		"durable_mutation": false,
	}
	for n in get_tree().get_nodes_in_group("manifestation_instances"):
		if n == null:
			continue
		payload["entity_id"] = str(n.get("prompt_id")) if "prompt_id" in n else str(n.name)
		payload["prompt_id"] = str(n.get("prompt_id")) if "prompt_id" in n else ""
		payload["recipe_id"] = str(n.get("recipe_id")) if "recipe_id" in n else ""
		payload["stage"] = str(n.call("get_stage")) if n.has_method("get_stage") else ""
		if n.has_method("has_durable_collision"):
			payload["has_durable_collision"] = bool(n.call("has_durable_collision"))
		if "provenance" in n and n.provenance is Dictionary:
			payload["provenance"] = (n.provenance as Dictionary).duplicate(true)
		else:
			payload["provenance"] = {
				"source": "runtime_inspect",
				"read_only": true,
				"prompt_id": payload.get("prompt_id", ""),
			}
		break
	if not payload.has("provenance"):
		payload["provenance"] = {
			"source": "runtime_inspect",
			"space": "private_reality",
			"read_only": true,
		}
	return payload


func _on_proposal_card_confirm() -> void:
	## Proposal Card "Confirm path" → open bounded Block Assembly preview (not World Commit yet).
	var prop := _last_companion_proposal
	if prop.is_empty() and _proposal_card != null and _proposal_card.has_method("get_last_proposal"):
		prop = _proposal_card.call("get_last_proposal") as Dictionary
	var boot: Dictionary = begin_companion_led_build(prop)
	if bool(boot.get("ok", false)):
		_flow_stage = "preview"
		_set_realm_status("Preview ready · cursor/LMB place · Q/R rotate · Enter confirm · Esc cancel")
		_set_preview_banner_stage("hologram")
		if _proposal_card != null and _proposal_card.has_method("close_card"):
			_proposal_card.call("close_card")
		return
	# Fallback: significant confirm hold if BA unavailable.
	_significant_confirm_pending = true
	_begin_confirm_hold()


func _wire_companion_panel() -> void:
	if _chat_panel == null:
		return
	if _chat_panel.has_signal("companion_proposal_ready"):
		if not _chat_panel.companion_proposal_ready.is_connected(_on_companion_proposal):
			_chat_panel.companion_proposal_ready.connect(_on_companion_proposal)


func _on_companion_proposal(proposal: Dictionary) -> void:
	_last_companion_proposal = proposal.duplicate(true) if proposal is Dictionary else {}
	_flow_stage = "structured_proposal"
	var recipe := str(_last_companion_proposal.get("recipe_id", "build"))
	var entity: Dictionary = {}
	if _last_companion_proposal.get("entity", {}) is Dictionary:
		entity = _last_companion_proposal.get("entity", {}) as Dictionary
		recipe = str(entity.get("recipe_id", recipe))
	_set_realm_status("Proposal ready: %s · confirm path for preview" % recipe)
	print("[Main] Companion proposal ready recipe=%s (no World Commit on Companion)" % recipe)


func begin_companion_led_build(proposal: Dictionary = {}) -> Dictionary:
	## Companion request → structured proposal → BA bounded preview surface.
	if _block_assembly == null:
		return {"ok": false, "reason": "block_assembly_missing"}
	var prop := proposal if not proposal.is_empty() else _last_companion_proposal
	var module_id := _module_for_recipe(prop)
	var res: Dictionary = {}
	if _block_assembly.has_method("begin_companion_led_preview"):
		res = _block_assembly.call("begin_companion_led_preview", module_id, 0.0, 0.0, 0.0, 0.0) as Dictionary
	else:
		res = _block_assembly.call("select_module", module_id, "structure", "", 0.0, 0.0, 0.0, 0.0) as Dictionary
	if not bool(res.get("ok", false)):
		return res
	var router := _control_router()
	if router != null:
		if router.has_method("request_context"):
			router.call("request_context", "build")
		if router.has_method("set_cancel_target"):
			router.call("set_cancel_target", "preview_hologram", true)
	_set_preview_buttons(true)
	_significant_confirm_pending = true
	_flow_stage = "preview"
	_set_preview_banner_stage(str(res.get("stage", "hologram")))
	return res


func _module_for_recipe(proposal: Dictionary) -> String:
	var recipe := "build"
	if proposal.get("entity", {}) is Dictionary:
		recipe = str((proposal.get("entity", {}) as Dictionary).get("recipe_id", proposal.get("recipe_id", "build")))
	else:
		recipe = str(proposal.get("recipe_id", "build"))
	var lower := recipe.to_lower()
	if "tree" in lower or "cây" in lower:
		return "block_cube_round"
	if "house" in lower or "nhà" in lower or "cozy" in lower:
		return "block_cube_round"
	return "block_cube_round"


func _apply_product_chrome() -> void:
	## Normal runtime: no QA labels, evidence counters, or diagnostic wall as primary chrome.
	_product_chrome_mode = true
	# Debug overlay only when player explicitly enables F3 (SettingsManager).
	var dbg := get_tree().get_first_node_in_group("debug_overlay") if get_tree() else null
	if dbg != null:
		var want_dbg := false
		if SettingsManager and SettingsManager.has_method("is_debug_overlay_enabled"):
			want_dbg = bool(SettingsManager.is_debug_overlay_enabled())
		dbg.visible = want_dbg
	# Cursor: normal OS pointer by default; label/proxy only when a11y opts in (H1-HUMAN-UX-02).
	Input.set_custom_mouse_cursor(null)
	_apply_cursor_label_a11y_visibility()
	# Starter Realm snapshot/session lines already gated by debug_toggled.
	for n in get_tree().get_nodes_in_group("g3_starter_realm"):
		if n != null and n.has_method("_set_debug_visible"):
			var on := false
			if SettingsManager and SettingsManager.has_method("is_debug_overlay_enabled"):
				on = bool(SettingsManager.is_debug_overlay_enabled())
			n.call("_set_debug_visible", on)
	print("[Main] product_chrome applied (debug_overlay=%s)" % str(
		SettingsManager.is_debug_overlay_enabled() if SettingsManager else false
	))


func is_product_chrome_mode() -> bool:
	return _product_chrome_mode


func get_flow_stage() -> String:
	return _flow_stage


func get_last_companion_proposal() -> Dictionary:
	return _last_companion_proposal.duplicate(true)


func get_product_chrome_audit() -> Dictionary:
	## Headless assertion surface: normal runtime must not present diagnostic wall.
	var dbg := get_tree().get_first_node_in_group("debug_overlay") if get_tree() else null
	var dbg_vis := dbg != null and bool(dbg.visible)
	var cursor_vis := _cursor_label != null and bool(_cursor_label.visible)
	var snap_vis := false
	var session_vis := false
	for n in get_tree().get_nodes_in_group("g3_starter_realm"):
		if n == null:
			continue
		var snap = n.get("snapshot_label") if "snapshot_label" in n else null
		var sess = n.get("session_label") if "session_label" in n else null
		if snap != null and snap is CanvasItem:
			snap_vis = snap_vis or bool((snap as CanvasItem).visible)
		if sess != null and sess is CanvasItem:
			session_vis = session_vis or bool((sess as CanvasItem).visible)
	var companion_has_commit := false
	if _chat_panel != null and _chat_panel.has_method("has_world_commit_tool"):
		companion_has_commit = bool(_chat_panel.call("has_world_commit_tool"))
	return {
		"product_chrome_mode": _product_chrome_mode,
		"debug_overlay_visible": dbg_vis,
		"cursor_label_visible": cursor_vis,
		"snapshot_label_visible": snap_vis,
		"session_label_visible": session_vis,
		"companion_has_world_commit_tool": companion_has_commit,
		"diagnostic_wall_primary": dbg_vis or snap_vis or session_vis,
		"pass_no_debug_chrome": (
			_product_chrome_mode
			and not dbg_vis
			and not snap_vis
			and not session_vis
			and not companion_has_commit
		),
	}


func _set_preview_banner_stage(stage: String) -> void:
	for n in get_tree().get_nodes_in_group("g3_starter_realm"):
		if n != null and n.has_method("set_preview_banner"):
			n.call("set_preview_banner", stage)
	_flow_stage = stage if stage in ["wireframe", "hologram", "materializing", "complete"] else _flow_stage
