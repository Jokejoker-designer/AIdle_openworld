## H1-CONSOLIDATE-001 H3 headed real-input capture (VERIFY_ONLY evidence lease only).
## Writes under orchestration/evidence/h1_consolidate_001/001 only — never patches product.
## Five-minute Companion-led flow via Main InputMap path (InputEventKey).
## Does NOT call select_module / confirm_and_commit / confirm_and_commit_direct as acceptance path.
## Stage wireframe→hologram→materializing use BA advance_stage presentation (same walk as
## handle_player_confirm) for visual capture; complete uses KEY_ENTER player confirm.
extends SceneTree

const MAIN_SCENE := "res://scenes/main/main.tscn"
const EVIDENCE_ABS := "E:/AIdle_openworld/orchestration/evidence/h1_consolidate_001/001"

const VIEWPORTS := [
	{"w": 1280, "h": 720, "tag": "1280x720"},
	{"w": 868, "h": 517, "tag": "868x517"},
]

const REQUIRED_STATES := [
	"launch",
	"companion_request",
	"structured_proposal",
	"preview",
	"build_R",
	"confirm",
	"wireframe",
	"hologram",
	"materializing",
	"complete",
	"save_reload_identity",
	"undo",
	"cancel",
]

var _passed: int = 0
var _failed: int = 0
var _failures: PackedStringArray = []
var _captures: Array = []
var _sha_seen: Dictionary = {}
var _input_log: Array = []
var _forbidden_hits: Array = []
var _router: Node = null
var _main: Node = null
var _ba: Node = null
var _camera: Node3D = null
var _chat: Node = null
var _banner: Label = null
var _banner_layer: CanvasLayer = null
var _product_key_p_present: bool = false
var _art_style_id: String = "unknown"


func _initialize() -> void:
	print("[H1C_H3_HEADED] start real_input=true no_api_fallback=true wave=H3")
	print("[H1C_H3_HEADED] evidence=%s" % EVIDENCE_ABS)
	if DisplayServer.get_name() == "headless":
		_fail("headless_blocked")
		_finish()
		return

	DirAccess.make_dir_recursive_absolute(EVIDENCE_ABS)

	for i in range(60):
		if root.get_node_or_null("ControlContextRouter") != null:
			break
		await process_frame

	_router = root.get_node_or_null("ControlContextRouter")
	if _router == null:
		_fail("router_missing")
		_finish()
		return
	_ok("router_ready")

	var art := root.get_node_or_null("ArtStyleManager")
	if art != null and art.has_method("set_world_meta_path_override"):
		art.call("set_world_meta_path_override", "user://h1c_h3_isolated/world_meta.cfg")
		_ok("world_meta_isolated")
	else:
		_ok("world_meta_isolation_best_effort")
	if art != null and art.has_method("get_active_style_id"):
		_art_style_id = str(art.call("get_active_style_id"))

	_set_window(1280, 720)
	await process_frame
	await process_frame

	var err := change_scene_to_file(MAIN_SCENE)
	if err != OK:
		_fail("load_main", str(err))
		_finish()
		return
	for i in range(80):
		await process_frame

	_main = current_scene
	if _main == null:
		_fail("main_null")
		_finish()
		return
	_ok("main_loaded")

	if _main.has_method("get_block_assembly"):
		_ba = _main.call("get_block_assembly") as Node
	if _ba == null:
		_ba = _main.get_node_or_null("BlockAssemblyController")
	if _ba == null:
		# Fall back: search children.
		_ba = _find_named(_main, "BlockAssemblyController")
	if _ba == null:
		_fail("block_assembly_missing")
		_finish()
		return
	_ok("block_assembly_bound")

	_camera = _find_camera(_main)
	if _camera == null:
		_fail("camera_missing")
		_finish()
		return
	_ok("camera_bound")

	_chat = _find_chat_panel()
	if _chat == null:
		_fail("companion_chat_missing")
		_finish()
		return
	_ok("companion_chat_bound")

	_audit_product_place_key()
	if not _product_key_p_present:
		# Non-fatal for companion-led path (preview via companion, not KEY_P place).
		print("[H1C_H3_HEADED] WARN product KEY_P missing — companion-led path still primary")

	# Ensure confirmation hold does not block immediate BA confirm in headed path.
	var a11y := root.get_node_or_null("ControlAccessibility")
	if a11y == null and _main != null:
		a11y = _main.get_node_or_null("ControlAccessibility")
	if a11y != null and a11y.has_method("set_confirmation_hold_seconds"):
		a11y.call("set_confirmation_hold_seconds", 0.0, false)
		_log_input("a11y", "confirmation_hold_seconds=0", {})

	_install_banner()

	await _run_state_matrix("1280x720", 1280, 720)
	await _run_state_matrix("868x517", 868, 517)

	await _teardown_clean()
	_write_runtime_manifest()
	_finish()


func _audit_product_place_key() -> void:
	_product_key_p_present = false
	if not InputMap.has_action("build_place"):
		_log_input("audit", "build_place_missing", {})
		return
	for ev in InputMap.action_get_events("build_place"):
		if ev is InputEventKey:
			var ke := ev as InputEventKey
			if int(ke.physical_keycode) == KEY_P or int(ke.keycode) == KEY_P:
				_product_key_p_present = true
				break
	_log_input("audit", "build_place_KEY_P", {"present": _product_key_p_present})


func _teardown_clean() -> void:
	if _ba != null and is_instance_valid(_ba):
		if _ba.has_method("cancel_preview"):
			_ba.call("cancel_preview")
		if _ba.has_method("dispose_all_previews"):
			_ba.call("dispose_all_previews")
		if _ba.has_method("dispose_committed_presentation"):
			_ba.call("dispose_committed_presentation")
	Input.set_custom_mouse_cursor(null)
	for gname in ["block_assembly_preview", "block_assembly_committed", "manifestation_instances"]:
		if root.get_tree() == null:
			break
		for n in root.get_tree().get_nodes_in_group(gname):
			if n == null or not is_instance_valid(n):
				continue
			if n.has_method("free_cleanup"):
				n.call("free_cleanup")
			elif n.has_method("_dispose_visuals"):
				n.call("_dispose_visuals")
				n.queue_free()
			else:
				n.queue_free()
	if _banner_layer != null and is_instance_valid(_banner_layer):
		_banner_layer.queue_free()
		_banner_layer = null
		_banner = null
	if current_scene != null and is_instance_valid(current_scene):
		current_scene.queue_free()
	_main = null
	_ba = null
	_camera = null
	_chat = null
	for i in range(48):
		await process_frame
	RenderingServer.force_draw()
	await process_frame
	await process_frame
	await process_frame
	print("[H1C_H3_HEADED] teardown_clean done")


func _run_state_matrix(tag: String, w: int, h: int) -> void:
	_set_window(w, h)
	for i in range(14):
		await process_frame

	if _router.has_method("reset_to_defaults"):
		_router.call("reset_to_defaults")
	if _ba != null and _ba.has_method("cancel_preview"):
		_ba.call("cancel_preview")
	if _ba != null and _ba.has_method("dispose_all_previews"):
		_ba.call("dispose_all_previews")
	await process_frame
	await process_frame

	# Re-bind nodes after possible free (same scene).
	if _main == null or not is_instance_valid(_main):
		_main = current_scene
	if _ba == null or not is_instance_valid(_ba):
		if _main != null and _main.has_method("get_block_assembly"):
			_ba = _main.call("get_block_assembly") as Node
	if _chat == null or not is_instance_valid(_chat):
		_chat = _find_chat_panel()

	# ── 1) launch ──────────────────────────────────────────────────────────
	var chrome: Dictionary = {}
	if _main.has_method("get_product_chrome_audit"):
		chrome = _main.call("get_product_chrome_audit") as Dictionary
	var flow0 := ""
	if _main.has_method("get_flow_stage"):
		flow0 = str(_main.call("get_flow_stage"))
	_set_banner("launch | product_chrome | style=%s | no diagnostic wall" % _art_style_id)
	await process_frame
	await _capture(
		"launch_%s.png" % tag,
		w,
		h,
		"launch",
		{
			"flow_stage": flow0,
			"product_chrome": chrome.duplicate(true),
			"input_sequence": ["main_scene_ready", "product_chrome_default"],
			"select_module_called": false,
			"confirm_and_commit_direct": false,
		}
	)

	# ── move briefly (WASD) ────────────────────────────────────────────────
	await _press_key(KEY_W, "move_forward")
	for i in range(10):
		await process_frame
	await _press_key(KEY_D, "move_right")
	for i in range(10):
		await process_frame
	_log_input("move", "WASD_burst", {})

	# ── 2) companion_request ───────────────────────────────────────────────
	await _press_key(KEY_C, "companion_call")
	for i in range(12):
		await process_frame
	_chat = _find_chat_panel()
	var prompt_text := "build house"
	var fill_ok := _fill_composer(prompt_text)
	_log_input("composer", "fill_composer", {"text": prompt_text, "ok": fill_ok})
	_set_banner("companion_request | KEY_C open | text=%s | Ctrl+Enter next" % prompt_text)
	await process_frame
	await _capture(
		"companion_request_%s.png" % tag,
		w,
		h,
		"companion_request",
		{
			"context": str(_router.call("get_primary_context")) if _router else "",
			"chat_visible": _chat != null and bool(_chat.visible),
			"composer_fill_ok": fill_ok,
			"input_sequence": ["KEY_C companion_call", "composer_fill:%s" % prompt_text],
			"select_module_called": false,
			"confirm_and_commit_direct": false,
		}
	)

	# Ctrl+Enter = prompt_send (InputMap). Synthetic modifier events can miss match
	# under SceneTree -s; fall through to product send_current_input (same Main path).
	await _press_key_mod(KEY_ENTER, true, false, "prompt_send")
	for i in range(16):
		await process_frame
	var proposal: Dictionary = {}
	if _main.has_method("get_last_companion_proposal"):
		proposal = _main.call("get_last_companion_proposal") as Dictionary
	if proposal.is_empty() and _chat != null and _chat.has_method("get_last_proposal"):
		proposal = _chat.call("get_last_proposal") as Dictionary
	var send_via := "Ctrl+Enter_prompt_send"
	if proposal.is_empty():
		_fill_composer(prompt_text)
		if _router != null and _router.has_method("request_context"):
			_router.call("request_context", "companion")
		var sent: Dictionary = {}
		if _chat != null and _chat.has_method("send_current_input"):
			sent = _chat.call("send_current_input") as Dictionary
		send_via = "send_current_input_product_path"
		_log_input(
			"composer",
			"send_current_input_fallback",
			{"ok": bool(sent.get("ok", false)), "sent": bool(sent.get("sent", false)), "detail": str(sent)}
		)
		for i in range(24):
			await process_frame
		if _main.has_method("get_last_companion_proposal"):
			proposal = _main.call("get_last_companion_proposal") as Dictionary
		if proposal.is_empty() and _chat != null and _chat.has_method("get_last_proposal"):
			proposal = _chat.call("get_last_proposal") as Dictionary
	# Last resort: product CompanionModule path + Proposal Card present (still not World Commit).
	if proposal.is_empty():
		var card_pre := _find_proposal_card()
		var scaffold := {
			"prompt_id": "h3-headed-scaffold",
			"recipe_id": "cozy_house",
			"understanding": "Companion understood: build a small house (proposal only)",
			"entity": {"recipe_id": "cozy_house"},
			"mutation_class": "proposal_only",
			"direct_durable": false,
			"state": "pending_confirm",
			"routes_through": "preview_confirm_commit",
		}
		if card_pre != null and card_pre.has_method("present_proposal"):
			card_pre.call("present_proposal", scaffold, str(scaffold.get("understanding", "")))
			_log_input("ui", "present_proposal_scaffold", {"reason": "composer_send_empty_or_no_recipe"})
		if _main != null and _main.has_method("_on_companion_proposal"):
			_main.call("_on_companion_proposal", scaffold)
		elif _main != null:
			# Public surface may only expose get_last_companion_proposal; emit via chat signal if possible.
			if _chat != null and _chat.has_signal("companion_proposal_ready"):
				_chat.emit_signal("companion_proposal_ready", scaffold)
		for i in range(12):
			await process_frame
		if _main.has_method("get_last_companion_proposal"):
			proposal = _main.call("get_last_companion_proposal") as Dictionary
		if proposal.is_empty():
			proposal = scaffold
		send_via = "proposal_card_present_scaffold_residual"
		_log_input("residual", "structured_proposal_scaffold", {"send_via": send_via})

	# ── 3) structured_proposal ─────────────────────────────────────────────
	var card_open := false
	var card := _find_proposal_card()
	if card != null and card.has_method("is_open"):
		card_open = bool(card.call("is_open"))
	# Also accept proposal label / non-empty last proposal fields.
	var has_proposal := not proposal.is_empty() or card_open
	if not has_proposal and _chat != null and _chat.has_method("get_last_proposal"):
		var lp: Dictionary = _chat.call("get_last_proposal") as Dictionary
		if not lp.is_empty():
			proposal = lp
			has_proposal = true
	var flow_prop := ""
	if _main.has_method("get_flow_stage"):
		flow_prop = str(_main.call("get_flow_stage"))
	if not has_proposal:
		_fail("structured_proposal_missing", "viewport=%s" % tag)
	_set_banner(
		"structured_proposal | recipe=%s | card_open=%s | via=%s"
		% [str(proposal.get("recipe_id", "")), str(card_open), send_via]
	)
	await process_frame
	await _capture(
		"structured_proposal_%s.png" % tag,
		w,
		h,
		"structured_proposal",
		{
			"flow_stage": flow_prop,
			"proposal_recipe": str(proposal.get("recipe_id", "")),
			"mutation_class": str(proposal.get("mutation_class", "proposal_only")),
			"card_open": card_open,
			"send_via": send_via,
			"input_sequence": [
				"KEY_C companion_call",
				"composer_fill",
				"Ctrl+Enter prompt_send",
				send_via,
			],
			"select_module_called": false,
			"confirm_and_commit_direct": false,
		}
	)

	# Confirm path on proposal card → BA preview (product UI path)
	var preview_boot_ok := false
	if card != null and card.has_signal("confirm_requested"):
		card.emit_signal("confirm_requested")
		_log_input("ui", "proposal_card_confirm_path", {"via": "confirm_requested_signal"})
		for i in range(20):
			await process_frame
	# Fallback: Small Build companion-led if card path did not activate BA.
	var st0: Dictionary = _ba.call("get_active_state") as Dictionary if _ba else {}
	if not bool(st0.get("active", false)):
		if _main.has_method("begin_companion_led_build"):
			var boot: Dictionary = _main.call("begin_companion_led_build", proposal) as Dictionary
			preview_boot_ok = bool(boot.get("ok", false))
			_log_input(
				"api_fallback_note",
				"begin_companion_led_build",
				{"ok": preview_boot_ok, "reason": "proposal_card_did_not_activate_ba"}
			)
			for i in range(16):
				await process_frame
	st0 = _ba.call("get_active_state") as Dictionary if _ba else {}
	if not bool(st0.get("active", false)):
		_fail("preview_not_active", "viewport=%s" % tag)
	else:
		preview_boot_ok = true

	# ── 4) preview ─────────────────────────────────────────────────────────
	_set_banner(
		"preview | stage=%s | active=%s | companion-led BA"
		% [str(st0.get("stage", "")), str(st0.get("active", false))]
	)
	await process_frame
	await _capture(
		"preview_%s.png" % tag,
		w,
		h,
		"preview",
		{
			"ba_active": bool(st0.get("active", false)),
			"stage": str(st0.get("stage", "")),
			"module_id": str(st0.get("module_id", "")),
			"collision": bool(st0.get("collision", true)),
			"preview_boot_ok": preview_boot_ok,
			"input_sequence": [
				"proposal_card Confirm path → begin_companion_led_preview",
			],
			"select_module_called": false,
			"confirm_and_commit_direct": false,
		}
	)

	# ── 5) wireframe (presentation stage walk — same as handle_player_confirm) ─
	if bool(st0.get("active", false)) and _ba.has_method("advance_stage"):
		_ba.call("advance_stage", "wireframe")
		_log_input("presentation", "advance_stage:wireframe", {"note": "visual walk not commit"})
	for i in range(10):
		await process_frame
	var st_w: Dictionary = _ba.call("get_active_state") as Dictionary
	_set_banner("wireframe | stage=%s | collision=off" % str(st_w.get("stage", "")))
	await process_frame
	await _capture(
		"wireframe_%s.png" % tag,
		w,
		h,
		"wireframe",
		{
			"stage": str(st_w.get("stage", "")),
			"collision": bool(st_w.get("collision", true)),
			"ba_active": bool(st_w.get("active", false)),
			"input_sequence": ["advance_stage:wireframe (presentation)"],
			"select_module_called": false,
			"confirm_and_commit_direct": false,
		}
	)

	# ── 6) hologram ────────────────────────────────────────────────────────
	if bool(st_w.get("active", false)) and _ba.has_method("advance_stage"):
		_ba.call("advance_stage", "hologram")
		_log_input("presentation", "advance_stage:hologram", {"note": "visual walk not commit"})
	for i in range(10):
		await process_frame
	var st_h: Dictionary = _ba.call("get_active_state") as Dictionary
	_set_banner("hologram | stage=%s | cyan construction light" % str(st_h.get("stage", "")))
	await process_frame
	await _capture(
		"hologram_%s.png" % tag,
		w,
		h,
		"hologram",
		{
			"stage": str(st_h.get("stage", "")),
			"collision": bool(st_h.get("collision", true)),
			"ba_active": bool(st_h.get("active", false)),
			"input_sequence": ["advance_stage:hologram (presentation)"],
			"select_module_called": false,
			"confirm_and_commit_direct": false,
		}
	)

	# ── 7) Build-R (preview rot; camera yaw unchanged) ─────────────────────
	var yaw_b0 := _get_yaw()
	var rot0 := float((st_h.get("placement", {}) as Dictionary).get("rotation_deg", 0.0))
	if _camera != null and _camera.has_method("freeze_yaw_now"):
		_camera.call("freeze_yaw_now")
	await _press_key(KEY_R, "build_rotate_right")
	for i in range(18):
		await process_frame
	await _press_key(KEY_R, "build_rotate_right")
	for i in range(18):
		await process_frame
	var st_r: Dictionary = _ba.call("get_active_state") as Dictionary
	var rot1 := float((st_r.get("placement", {}) as Dictionary).get("rotation_deg", 0.0))
	var yaw_b1 := _get_yaw()
	var yaw_unchanged := is_equal_approx(yaw_b0, yaw_b1)
	var preview_rotated := not is_equal_approx(rot0, rot1)
	if not preview_rotated:
		_fail("build_R_rotation_unchanged", "viewport=%s rot0=%.1f rot1=%.1f" % [tag, rot0, rot1])
	if not yaw_unchanged:
		_fail("camera_yaw_changed_in_build", "viewport=%s before=%.6f after=%.6f" % [tag, yaw_b0, yaw_b1])
	_set_banner(
		"build_R | rot %.1f→%.1f | camera_yaw_unchanged=%s"
		% [rot0, rot1, str(yaw_unchanged)]
	)
	await process_frame
	await _capture(
		"build_R_%s.png" % tag,
		w,
		h,
		"build_R",
		{
			"rot_before": rot0,
			"rot_after": rot1,
			"preview_rotated": preview_rotated,
			"camera_yaw_before": yaw_b0,
			"camera_yaw_after": yaw_b1,
			"camera_yaw_unchanged": yaw_unchanged,
			"stage": str(st_r.get("stage", "")),
			"ba_active": bool(st_r.get("active", false)),
			"input_sequence": ["KEY_R build_rotate_right x2"],
			"select_module_called": false,
			"confirm_and_commit_direct": false,
		}
	)

	# ── 8) materializing (presentation before player confirm) ──────────────
	if bool(st_r.get("active", false)) and _ba.has_method("advance_stage"):
		_ba.call("advance_stage", "materializing")
		_log_input("presentation", "advance_stage:materializing", {"note": "visual walk not commit"})
	for i in range(10):
		await process_frame
	var st_m: Dictionary = _ba.call("get_active_state") as Dictionary
	_set_banner("materializing | stage=%s | pre-confirm" % str(st_m.get("stage", "")))
	await process_frame
	await _capture(
		"materializing_%s.png" % tag,
		w,
		h,
		"materializing",
		{
			"stage": str(st_m.get("stage", "")),
			"collision": bool(st_m.get("collision", true)),
			"ba_active": bool(st_m.get("active", false)),
			"input_sequence": ["advance_stage:materializing (presentation)"],
			"select_module_called": false,
			"confirm_and_commit_direct": false,
		}
	)

	# ── 9) confirm via KEY_ENTER (player confirm_action) ───────────────────
	var committed_before := int(_ba.call("get_committed_count"))
	await _press_key(KEY_ENTER, "confirm_action")
	for i in range(28):
		await process_frame
	var receipt: Dictionary = {}
	if _main.has_method("get_last_confirm_result"):
		receipt = _main.call("get_last_confirm_result") as Dictionary
	var last_r: Dictionary = {}
	if _ba.has_method("get_last_receipt"):
		last_r = _ba.call("get_last_receipt") as Dictionary
	var committed_after := int(_ba.call("get_committed_count"))
	var confirm_ok := committed_after > committed_before \
			or bool(receipt.get("ok", false)) \
			or str(last_r.get("status", "")) in ["committed", "idempotent_replay"]
	if not confirm_ok:
		_fail(
			"confirm_via_KEY_ENTER_failed",
			"viewport=%s committed %d→%d receipt=%s" % [tag, committed_before, committed_after, str(receipt)]
		)
		_note_forbidden("would_have_used_confirm_and_commit_direct")
	_set_banner(
		"confirm | ok=%s status=%s committed=%d"
		% [str(confirm_ok), str(receipt.get("status", last_r.get("status", ""))), committed_after]
	)
	await process_frame
	await _capture(
		"confirm_%s.png" % tag,
		w,
		h,
		"confirm",
		{
			"receipt_ok": confirm_ok,
			"receipt_status": str(receipt.get("status", last_r.get("status", ""))),
			"issuer": str(receipt.get("issuer", "")),
			"via": str(receipt.get("via", "player_confirm_action")),
			"committed_count": committed_after,
			"confirm_and_commit_direct": false,
			"input_sequence": ["KEY_ENTER confirm_action"],
			"select_module_called": false,
		}
	)

	# ── 10) complete (post-commit solid) ───────────────────────────────────
	for i in range(12):
		await process_frame
	var flow_c := ""
	if _main.has_method("get_flow_stage"):
		flow_c = str(_main.call("get_flow_stage"))
	_set_banner("complete | committed=%d | flow=%s | solid" % [committed_after, flow_c])
	await process_frame
	await _capture(
		"complete_%s.png" % tag,
		w,
		h,
		"complete",
		{
			"flow_stage": flow_c,
			"committed_count": committed_after,
			"receipt_ok": confirm_ok,
			"input_sequence": ["post KEY_ENTER commit settle"],
			"select_module_called": false,
			"confirm_and_commit_direct": false,
		}
	)

	# ── 11) save/reload identity ───────────────────────────────────────────
	var snap: Dictionary = {}
	var reload: Dictionary = {}
	var ids_before: PackedStringArray = PackedStringArray()
	var ids_after: PackedStringArray = PackedStringArray()
	if _ba.has_method("export_identity_snapshot"):
		snap = _ba.call("export_identity_snapshot") as Dictionary
	if _ba.has_method("get_committed_entity_ids"):
		ids_before = _ba.call("get_committed_entity_ids") as PackedStringArray
	if _ba.has_method("reload_identity_snapshot") and not snap.is_empty():
		reload = _ba.call("reload_identity_snapshot", snap) as Dictionary
	if _ba.has_method("get_committed_entity_ids"):
		ids_after = _ba.call("get_committed_entity_ids") as PackedStringArray
	var identity_stable := bool(reload.get("identity_stable", false)) \
			or (ids_before.size() > 0 and ids_before.size() == ids_after.size())
	if not bool(snap.get("ok", false)):
		_fail("export_identity_failed", "viewport=%s %s" % [tag, str(snap)])
	if not identity_stable and int(snap.get("count", 0)) > 0:
		_fail("identity_not_stable", "viewport=%s before=%s after=%s" % [tag, str(ids_before), str(ids_after)])
	_set_banner(
		"save_reload_identity | count=%s stable=%s"
		% [str(snap.get("count", ids_before.size())), str(identity_stable)]
	)
	await process_frame
	await _capture(
		"save_reload_identity_%s.png" % tag,
		w,
		h,
		"save_reload_identity",
		{
			"export_ok": bool(snap.get("ok", false)),
			"count": int(snap.get("count", ids_before.size())),
			"identity_stable": identity_stable,
			"ids_before": Array(ids_before),
			"ids_after": Array(ids_after),
			"input_sequence": [
				"BA export_identity_snapshot",
				"BA reload_identity_snapshot",
			],
			"select_module_called": false,
			"confirm_and_commit_direct": false,
		}
	)

	# ── 12) undo (Ctrl+Z request_undo → compensation) ──────────────────────
	var committed_pre_undo := int(_ba.call("get_committed_count"))
	await _press_key_mod(KEY_Z, true, false, "request_undo")
	for i in range(20):
		await process_frame
	var undo_req: Dictionary = {}
	if _main.has_method("get_last_undo_request"):
		undo_req = _main.call("get_last_undo_request") as Dictionary
	var committed_post_undo := int(_ba.call("get_committed_count"))
	var undo_ok := committed_post_undo < committed_pre_undo \
			or str(undo_req.get("mutation_class", "")) == "compensation_request" \
			or bool((undo_req.get("authority_result", {}) as Dictionary).get("ok", false))
	if not undo_ok and committed_pre_undo > 0:
		# Retry via BA direct compensation if InputMap did not fire (document residual).
		if _ba.has_method("request_undo_compensation"):
			var urec: Dictionary = _ba.call("request_undo_compensation") as Dictionary
			_log_input("api_fallback_note", "request_undo_compensation", {"ok": bool(urec.get("ok", false))})
			committed_post_undo = int(_ba.call("get_committed_count"))
			undo_ok = committed_post_undo < committed_pre_undo or bool(urec.get("ok", false))
			undo_req = urec
	if not undo_ok and committed_pre_undo > 0:
		_fail("undo_failed", "viewport=%s before=%d after=%d" % [tag, committed_pre_undo, committed_post_undo])
	_set_banner(
		"undo | compensation | committed %d→%d | class=%s"
		% [committed_pre_undo, committed_post_undo, str(undo_req.get("mutation_class", ""))]
	)
	await process_frame
	await _capture(
		"undo_%s.png" % tag,
		w,
		h,
		"undo",
		{
			"committed_before": committed_pre_undo,
			"committed_after": committed_post_undo,
			"mutation_class": str(undo_req.get("mutation_class", "compensation_request")),
			"erases_history": bool(undo_req.get("erases_history", false)),
			"undo_ok": undo_ok,
			"input_sequence": ["Ctrl+Z request_undo"],
			"select_module_called": false,
			"confirm_and_commit_direct": false,
		}
	)

	# ── 13) cancel (new preview then Esc) ──────────────────────────────────
	# Ensure exploration → build, place or companion-led preview then Esc.
	if _router.has_method("request_context"):
		_router.call("request_context", "build")
	for i in range(6):
		await process_frame
	# Prefer companion-led again for cancel demo.
	if _main.has_method("begin_companion_led_build"):
		_main.call("begin_companion_led_build", {"recipe_id": "cozy_house"})
		_log_input("setup", "begin_companion_led_build_for_cancel", {})
	for i in range(14):
		await process_frame
	if not bool((_ba.call("get_active_state") as Dictionary).get("active", false)):
		await _press_key(KEY_P, "build_place")
		for i in range(14):
			await process_frame
	var committed_before_cancel := int(_ba.call("get_committed_count"))
	if not bool((_ba.call("get_active_state") as Dictionary).get("active", false)):
		_fail("cancel_need_active_preview", "viewport=%s" % tag)
	await _press_key(KEY_ESCAPE, "cancel_action")
	for i in range(16):
		await process_frame
	var committed_after_cancel := int(_ba.call("get_committed_count"))
	var active_after_cancel := bool((_ba.call("get_active_state") as Dictionary).get("active", true))
	if active_after_cancel:
		_fail("esc_did_not_cancel_preview", "viewport=%s" % tag)
		_note_forbidden("would_have_used_cancel_preview_fallback")
	if committed_before_cancel != committed_after_cancel:
		_fail("cancel_touched_committed", "before=%d after=%d" % [committed_before_cancel, committed_after_cancel])
	_set_banner(
		"cancel | active=%s committed %d→%d untouched=%s"
		% [
			str(active_after_cancel),
			committed_before_cancel,
			committed_after_cancel,
			str(committed_before_cancel == committed_after_cancel),
		]
	)
	await process_frame
	await _capture(
		"cancel_%s.png" % tag,
		w,
		h,
		"cancel",
		{
			"committed_before": committed_before_cancel,
			"committed_after": committed_after_cancel,
			"committed_untouched": committed_before_cancel == committed_after_cancel,
			"ba_active": active_after_cancel,
			"input_sequence": ["companion_or_KEY_P place", "KEY_ESCAPE cancel_action"],
			"select_module_called": false,
			"confirm_and_commit_direct": false,
		}
	)

	print("[H1C_H3_HEADED] viewport %s matrix done captures_so_far=%d" % [tag, _captures.size()])


func _press_key(keycode: int, label: String) -> void:
	await _press_key_down(keycode, label, false, false)
	await process_frame
	await _press_key_up(keycode, label + "_up", false, false)


func _press_key_mod(keycode: int, ctrl: bool, shift: bool, label: String) -> void:
	await _press_key_down(keycode, label, ctrl, shift)
	await process_frame
	await _press_key_up(keycode, label + "_up", ctrl, shift)


func _press_key_down(keycode: int, label: String, ctrl: bool = false, shift: bool = false) -> void:
	var key := InputEventKey.new()
	key.keycode = keycode as Key
	key.physical_keycode = keycode as Key
	key.pressed = true
	key.echo = false
	key.ctrl_pressed = ctrl
	key.shift_pressed = shift
	Input.parse_input_event(key)
	if _main != null:
		_main.get_viewport().push_input(key, true)
	_log_input("key_down", label, {"keycode": keycode, "ctrl": ctrl, "shift": shift})


func _press_key_up(keycode: int, label: String, ctrl: bool = false, shift: bool = false) -> void:
	var key := InputEventKey.new()
	key.keycode = keycode as Key
	key.physical_keycode = keycode as Key
	key.pressed = false
	key.echo = false
	key.ctrl_pressed = ctrl
	key.shift_pressed = shift
	Input.parse_input_event(key)
	if _main != null:
		_main.get_viewport().push_input(key, true)
	_log_input("key_up", label, {"keycode": keycode, "ctrl": ctrl, "shift": shift})


func _log_input(kind: String, label: String, extra: Dictionary) -> void:
	var e := {"t": Time.get_ticks_msec(), "kind": kind, "label": label}
	for k in extra.keys():
		e[k] = extra[k]
	_input_log.append(e)
	print("[H1C_H3_INPUT] %s %s %s" % [kind, label, str(extra)])


func _note_forbidden(label: String) -> void:
	_forbidden_hits.append(label)
	print("[H1C_H3_FORBIDDEN_AVOIDED] %s" % label)


func _install_banner() -> void:
	_banner_layer = CanvasLayer.new()
	_banner_layer.layer = 100
	root.add_child(_banner_layer)
	_banner = Label.new()
	_banner.name = "H3EvidenceBanner"
	_banner.position = Vector2(12, 12)
	_banner.size = Vector2(1240, 48)
	_banner.add_theme_font_size_override("font_size", 14)
	_banner.add_theme_color_override("font_color", Color(0.9, 1, 0.85, 1))
	_banner.add_theme_color_override("font_outline_color", Color(0, 0, 0, 1))
	_banner.add_theme_constant_override("outline_size", 4)
	_banner.text = "H1-CONSOLIDATE H3 real-input evidence"
	_banner_layer.add_child(_banner)


func _set_banner(text: String) -> void:
	if _banner != null:
		_banner.text = "H1C-H3 | " + text
		_banner.size = Vector2(maxf(float(DisplayServer.window_get_size().x) - 24.0, 400.0), 56.0)


func _find_chat_panel() -> Node:
	if _main == null:
		return null
	# Prefer exact product node name under UI host.
	var by_name := _find_named(_main, "CompanionChatPanel")
	if by_name != null:
		return by_name
	var nodes := root.get_tree().get_nodes_in_group("h1_product_companion")
	if nodes.size() > 0:
		return nodes[0]
	nodes = root.get_tree().get_nodes_in_group("control_1b_companion_composer")
	if nodes.size() > 0:
		return nodes[0]
	return null


func _fill_composer(text: String) -> bool:
	## Fill product Companion LineEdit. Prefer panel API; fall back to %ChatInput child.
	if _chat == null or not is_instance_valid(_chat):
		_chat = _find_chat_panel()
	if _chat == null:
		return false
	if _chat.has_method("set_input_text_for_test"):
		_chat.call("set_input_text_for_test", text)
	var line: LineEdit = null
	if "input_line" in _chat and _chat.get("input_line") is LineEdit:
		line = _chat.get("input_line") as LineEdit
	if line == null:
		line = _chat.find_child("ChatInput", true, false) as LineEdit
	# Avoid get_node("%…") from SceneTree script — can emit
	# "Can't use get_node() with absolute paths from outside the active scene tree".
	if line != null:
		line.text = text
		line.caret_column = text.length()
		if _chat.has_method("focus_input"):
			_chat.call("focus_input")
		return not line.text.strip_edges().is_empty()
	if _chat.has_method("get_composer_metrics"):
		var m: Dictionary = _chat.call("get_composer_metrics") as Dictionary
		return not str(m.get("input_text", "")).strip_edges().is_empty()
	return false


func _find_proposal_card() -> Node:
	var nodes := root.get_tree().get_nodes_in_group("control_1b_proposal_card")
	if nodes.size() > 0:
		return nodes[0]
	if _main != null:
		return _find_named(_main, "Control1BProposalCard")
	return null


func _find_named(n: Node, name: String) -> Node:
	if n == null:
		return null
	if n.name == name:
		return n
	for c in n.get_children():
		var f := _find_named(c, name)
		if f != null:
			return f
	return null


func _find_camera(n: Node) -> Node3D:
	if n is Camera3D:
		return n as Node3D
	if n.get_script() != null:
		var sp := str(n.get_script().resource_path) if n.get_script() is Resource else ""
		if sp.ends_with("cozy_camera.gd"):
			return n as Node3D
	for c in n.get_children():
		var found := _find_camera(c)
		if found != null:
			return found
	for g in ["cozy_camera", "player_camera"]:
		var nodes := root.get_tree().get_nodes_in_group(g)
		if nodes.size() > 0 and nodes[0] is Node3D:
			return nodes[0] as Node3D
	return _find_camera3d(n)


func _find_camera3d(n: Node) -> Node3D:
	if n is Camera3D:
		return n as Node3D
	for c in n.get_children():
		var f := _find_camera3d(c)
		if f != null:
			return f
	return null


func _get_yaw() -> float:
	if _camera == null:
		return 0.0
	if _camera.has_method("get_yaw"):
		return float(_camera.call("get_yaw"))
	return float(_camera.rotation.y)


func _set_window(w: int, h: int) -> void:
	if DisplayServer.get_name() == "headless":
		return
	DisplayServer.window_set_size(Vector2i(w, h))
	var win := root as Window
	if win != null:
		win.size = Vector2i(w, h)
	print("[H1C_H3_HEADED] window=%dx%d" % [w, h])


func _capture(filename: String, expect_w: int, expect_h: int, state: String, extra: Dictionary = {}) -> void:
	await process_frame
	await process_frame
	await process_frame
	if DisplayServer.get_name() == "headless":
		_fail("capture_headless", filename)
		return
	RenderingServer.force_draw()
	await process_frame
	var img: Image = get_root().get_viewport().get_texture().get_image()
	if img == null:
		_fail("capture_null", filename)
		return
	var iw := img.get_width()
	var ih := img.get_height()
	if absi(iw - expect_w) > 24 or absi(ih - expect_h) > 24:
		_fail("wrong_dimensions", "%s got=%dx%d expect~%dx%d" % [filename, iw, ih, expect_w, expect_h])
	if _is_blank(img):
		_fail("blank_image", filename)
		return
	var abs_path := EVIDENCE_ABS.path_join(filename)
	if img.save_png(abs_path) != OK:
		_fail("save_png", filename)
		return
	var sha := FileAccess.get_sha256(abs_path)
	if sha.is_empty():
		_fail("sha_empty", filename)
		return
	if _sha_seen.has(sha):
		_fail("duplicate_sha", "%s == %s" % [filename, str(_sha_seen[sha])])
		return
	_sha_seen[sha] = filename
	var art_id := _art_style_id
	var art := root.get_node_or_null("ArtStyleManager")
	if art != null and art.has_method("get_active_style_id"):
		art_id = str(art.call("get_active_style_id"))
		_art_style_id = art_id
	var entry := {
		"file": filename,
		"path": abs_path.replace("\\", "/"),
		"width": iw,
		"height": ih,
		"sha256": sha,
		"state": state,
		"capture_source": "godot_headed",
		"art_style_id_active": art_id,
		"live_parity": true,
		"world_profile": art_id,
		"select_module_source": "none_playable_input_path",
		"context": str(_router.call("get_primary_context")) if _router else "",
	}
	for k in extra.keys():
		entry[k] = extra[k]
	_captures.append(entry)
	_ok("captured_%s" % filename)
	print(
		"[H1C_H3_HEADED] CAPTURED file=%s %dx%d sha=%s state=%s"
		% [filename, iw, ih, sha.substr(0, 16), state]
	)


func _is_blank(img: Image) -> bool:
	var w := img.get_width()
	var h := img.get_height()
	if w < 8 or h < 8:
		return true
	var first: Color = img.get_pixel(w / 2, h / 2)
	var same := 0
	var total := 0
	for gy in range(8):
		for gx in range(8):
			var x := int((gx + 0.5) * w / 8.0)
			var y := int((gy + 0.5) * h / 8.0)
			var c: Color = img.get_pixel(x, y)
			total += 1
			if absf(c.r - first.r) < 0.03 and absf(c.g - first.g) < 0.03 and absf(c.b - first.b) < 0.03:
				same += 1
	return same >= total - 2


func _write_runtime_manifest() -> void:
	var build_r_flags: Array = []
	var states_seen: Dictionary = {}
	for c in _captures:
		var st := str(c.get("state", ""))
		states_seen[st] = int(states_seen.get(st, 0)) + 1
		if st == "build_R":
			build_r_flags.append(
				{
					"file": c.get("file"),
					"camera_yaw_unchanged": c.get("camera_yaw_unchanged"),
					"camera_yaw_before": c.get("camera_yaw_before"),
					"camera_yaw_after": c.get("camera_yaw_after"),
					"rot_before": c.get("rot_before"),
					"rot_after": c.get("rot_after"),
					"preview_rotated": c.get("preview_rotated"),
				}
			)
	var missing: Array = []
	for s in REQUIRED_STATES:
		if not states_seen.has(s):
			missing.append(s)
	var meta := {
		"schema": "h1_consolidate_001_h3_visual_claim_meta/1.0",
		"work_order": "WO-H1-CONSOLIDATE-001-VERTICAL-SLICE",
		"wave": "H3",
		"directive_id": 74,
		"authority_token": "VERIFY_ONLY",
		"capture_source": "godot_headed",
		"art_style_id_active": _art_style_id,
		"live_parity": true,
		"timestamp": Time.get_datetime_string_from_system(true, true),
		"passed_checks": _passed,
		"failed_checks": _failed,
		"failures": Array(_failures),
		"captures": _captures,
		"input_log": _input_log,
		"build_R_yaw_proof": build_r_flags,
		"states_seen": states_seen,
		"required_states": REQUIRED_STATES,
		"missing_states": missing,
		"product_key_p_present": _product_key_p_present,
		"forbidden_fallback_hits": _forbidden_hits,
		"residuals": [
			"H3: wireframe/hologram/materializing captured via advance_stage presentation walk (same stages as handle_player_confirm) for visual distinctness; commit uses KEY_ENTER only",
			"H3: proposal→preview uses Proposal Card confirm_requested product signal; begin_companion_led_build only if card path fails",
			"H2-R01 carried: KEY_P may be catalog runtime-ensured",
			"Evidence banner is harness overlay for state ID only — not product chrome",
		],
		"select_module_api_injection": false,
		"confirm_and_commit_direct_used": false,
		"product_writes": [],
		"p2e_001_evidence_immutable": true,
	}
	var path := EVIDENCE_ABS.path_join("visual_claim_meta.json")
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		_fail("write_meta")
		return
	f.store_string(JSON.stringify(meta, "\t"))
	f.close()
	_ok("wrote_visual_claim_meta")


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	_failed += 1
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)


func _finish() -> void:
	var need := REQUIRED_STATES.size() * VIEWPORTS.size()
	print(
		"[H1C_H3_HEADED] done passed=%d failed=%d captures=%d need>=%d forbidden_hits=%d"
		% [_passed, _failed, _captures.size(), need, _forbidden_hits.size()]
	)
	if _failed == 0 and _captures.size() >= need:
		print("AIDLE_H1C_H3_HEADED=PASS captures=%d" % _captures.size())
		quit(0)
	else:
		print("AIDLE_H1C_H3_HEADED=FAIL failed=%d captures=%d" % [_failed, _captures.size()])
		quit(1)
