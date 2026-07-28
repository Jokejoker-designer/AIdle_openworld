## Companion text panel — primary creative guide for five-minute first session.
## CTRL-1B B1/C0: `/` focus, Ctrl+Enter send, Shift+Enter newline (never send).
## No World Commit tool. Proposals route preview → confirm → World Commit only.
extends Control

signal companion_proposal_ready(proposal: Dictionary)

@onready var log_label: RichTextLabel = %ChatLog
@onready var input_line: LineEdit = %ChatInput
@onready var proposal_label: Label = %ProposalStatus
@onready var personality_label: Label = %PersonalityStatus
@onready var panel: PanelContainer = $Panel
@onready var title_label: Label = $Panel/VBox/Title

var _companion: CompanionModule
## Smoke/runtime counters (H-03): prompt_send vs prompt_newline never-send.
var _send_count: int = 0
var _newline_count: int = 0
var _last_send_text: String = ""
var _last_understanding: String = ""
var _last_proposal: Dictionary = {}

const MIN_INPUT_H := 28
const ACTION_BAR_CLEARANCE := 96.0


func _ready() -> void:
	_apply_panel_theme()
	if input_line:
		# Contract: plain Enter is NOT the sole send path (Ctrl+Enter = prompt_send).
		if input_line.text_submitted.is_connected(_on_text_submitted):
			input_line.text_submitted.disconnect(_on_text_submitted)
		# Keep connection for legacy callers but route through guarded path.
		if not input_line.text_submitted.is_connected(_on_plain_enter_guarded):
			input_line.text_submitted.connect(_on_plain_enter_guarded)
		input_line.placeholder_text = "Ask Companion… Ctrl+Enter send · try: xây nhà"
		input_line.custom_minimum_size = Vector2(0, MIN_INPUT_H)
	_apply_responsive_anchors()
	get_viewport().size_changed.connect(_apply_responsive_anchors)
	_bind_companion()
	_refresh_personality()
	if log_label:
		log_label.append_text(
			"[i]Companion is your guide. Ctrl+Enter sends · Shift+Enter newline. No World Commit here.[/i]\n"
		)
	if proposal_label:
		proposal_label.text = "Proposal: none"
	add_to_group("control_1b_companion_composer")
	add_to_group("h1_product_companion")


func _apply_panel_theme() -> void:
	if panel:
		var sb := StyleBoxFlat.new()
		sb.bg_color = Color(0.1, 0.12, 0.16, 0.96)
		sb.set_corner_radius_all(10)
		sb.content_margin_left = 10
		sb.content_margin_right = 10
		sb.content_margin_top = 8
		sb.content_margin_bottom = 8
		sb.border_width_left = 2
		sb.border_width_top = 2
		sb.border_width_right = 2
		sb.border_width_bottom = 2
		sb.border_color = Color("62E6FF").darkened(0.2)
		panel.add_theme_stylebox_override("panel", sb)
	if title_label:
		title_label.text = "Companion"
		title_label.add_theme_color_override("font_color", Color("FFB86B"))
		title_label.add_theme_font_size_override("font_size", 13)
	for bname in ["InspectBtn", "ResetBtn", "DeleteBtn"]:
		var b := get_node_or_null("Panel/VBox/Controls/%s" % bname) as Button
		if b:
			b.custom_minimum_size = Vector2(70, 28)
			b.add_theme_font_size_override("font_size", 12)


func _apply_responsive_anchors() -> void:
	var vp := get_viewport().get_visible_rect().size
	var compact := vp.x < 1000.0 or vp.y < 600.0
	# Bottom-left, clear of two-row action bar + context HUD (compact needs more lift).
	anchor_left = 0.0
	anchor_top = 1.0
	anchor_right = 0.0
	anchor_bottom = 1.0
	var clearance := 108.0 if compact else ACTION_BAR_CLEARANCE
	var width := minf(vp.x * 0.46, 320.0 if compact else 380.0)
	var height := minf(vp.y * 0.32, 170.0 if compact else 220.0)
	offset_left = 8.0
	offset_right = 8.0 + width
	offset_bottom = -clearance
	offset_top = -clearance - height
	grow_vertical = Control.GROW_DIRECTION_BEGIN
	if log_label:
		log_label.custom_minimum_size = Vector2(0, 56 if compact else 100)
	if input_line:
		input_line.custom_minimum_size = Vector2(0, MIN_INPUT_H)
		input_line.visible = true


func get_panel_global_rect() -> Rect2:
	return get_global_rect()


func is_chat_input_visible() -> bool:
	return input_line != null and input_line.visible and input_line.get_global_rect().size.y >= MIN_INPUT_H - 1


func _bind_companion() -> void:
	if ModuleRegistry.has_module(AIdleConstants.MODULE_COMPANION):
		var m := ModuleRegistry.get_module(AIdleConstants.MODULE_COMPANION)
		if m is CompanionModule:
			_companion = m as CompanionModule
	if _companion == null:
		if not EventBus.module_registered.is_connected(_on_module_registered):
			EventBus.module_registered.connect(_on_module_registered)
		return
	_wire_companion_signals()


func _on_module_registered(module_id: String, module: Node) -> void:
	if module_id != AIdleConstants.MODULE_COMPANION:
		return
	if module is CompanionModule:
		_companion = module as CompanionModule
		_wire_companion_signals()


func _wire_companion_signals() -> void:
	if _companion == null:
		return
	if not _companion.chat_message.is_connected(_on_chat_message):
		_companion.chat_message.connect(_on_chat_message)
	if not _companion.proposal_ready.is_connected(_on_proposal_ready):
		_companion.proposal_ready.connect(_on_proposal_ready)
	if not _companion.personality_control.is_connected(_on_personality_control):
		_companion.personality_control.connect(_on_personality_control)


func _on_plain_enter_guarded(_text: String) -> void:
	## Plain Enter must NOT send when Control 1B policy requires Ctrl+Enter (H-03 / C1B-HK-02).
	# Ignore — send only via send_current_input (prompt_send).
	pass


func _on_text_submitted(text: String) -> void:
	## Explicit send path (prompt_send / Ctrl+Enter only).
	_perform_send(text)


func _perform_send(text: String) -> void:
	var cleaned := text.strip_edges()
	if cleaned.is_empty():
		return
	if input_line:
		input_line.text = ""
	_send_count += 1
	_last_send_text = cleaned
	_last_understanding = "Player said: %s" % cleaned
	if _companion == null:
		_bind_companion()
	if _companion == null:
		_append_local("system", "Companion is not ready yet.")
		# Still surface a local Proposal Card scaffold so H-17 path is observable offline.
		_emit_local_proposal_scaffold(cleaned)
		return
	_companion.receive_message(cleaned)
	_refresh_personality()


func _emit_local_proposal_scaffold(text: String) -> void:
	var recipe := "build"
	var lower := text.to_lower()
	if "nhà" in lower or "house" in lower or "xây" in lower:
		recipe = "cozy_house"
	elif "cây" in lower or "tree" in lower:
		recipe = "tree"
	var proposal := {
		"prompt_id": "local-scaffold",
		"recipe_id": recipe,
		"understanding": "Companion understood intent from: %s" % text,
		"entity": {"recipe_id": recipe},
		"mutation_class": "proposal_only",
		"direct_durable": false,
		"state": "pending_confirm",
		"routes_through": "preview_confirm_commit",
	}
	_on_proposal_ready(proposal)


func _on_chat_message(role: String, text: String) -> void:
	_append_local(role, text)
	if role == "companion":
		_last_understanding = text


func _on_proposal_ready(proposal: Dictionary) -> void:
	_last_proposal = proposal.duplicate(true) if proposal is Dictionary else {}
	var entity_info: Dictionary = {}
	if proposal.get("entity", {}) is Dictionary:
		entity_info = proposal.get("entity", {}) as Dictionary
	var recipe := str(entity_info.get("recipe_id", proposal.get("recipe_id", "build")))
	if proposal_label:
		proposal_label.text = "Proposal: %s · preview then confirm" % recipe
	var understanding := _last_understanding
	if understanding.is_empty():
		understanding = str(proposal.get("understanding", "Companion prepared a proposal for %s" % recipe))
	# Surface structured Proposal Card (H-17) — never direct mutation / no World Commit tool.
	var card := _find_proposal_card()
	if card != null and card.has_method("present_proposal"):
		card.call("present_proposal", proposal, understanding)
	companion_proposal_ready.emit(_last_proposal)
	print(
		"[CompanionChat] proposal_card recipe=%s mutation_class=proposal_only direct_durable=false"
		% recipe
	)


func get_last_proposal() -> Dictionary:
	return _last_proposal.duplicate(true)


func has_world_commit_tool() -> bool:
	## Invariant: Companion never exposes a World Commit control.
	return false


func _on_personality_control(_action: String, _detail: Dictionary) -> void:
	_refresh_personality()


func _refresh_personality() -> void:
	if personality_label == null:
		return
	var mood := "calm"
	var privacy := "session"
	if _companion != null:
		if _companion.has_method("get_emotional_state"):
			mood = str(_companion.call("get_emotional_state"))
		var p = _companion.get_personality() if _companion.has_method("get_personality") else null
		if p != null and p.get("privacy_mode") != null:
			privacy = str(p.privacy_mode)
	personality_label.text = "Mood: %s · Privacy: %s" % [mood, privacy]


func _append_local(role: String, text: String) -> void:
	if log_label == null:
		return
	var color := "#FFB86B" if role == "companion" else ("#E8F4FF" if role == "player" else "#9aa")
	var who := "You" if role == "player" else ("Companion" if role == "companion" else role)
	log_label.append_text("[color=%s][b]%s[/b][/color]: %s\n" % [color, who, text])


func _on_inspect_pressed() -> void:
	if _companion:
		_companion.receive_message("/inspect")
		_refresh_personality()


func _on_reset_pressed() -> void:
	if _companion:
		_companion.receive_message("/reset")
		_refresh_personality()


func _on_delete_pressed() -> void:
	## Prefer Control 1B delete_proposal (proposal only) over free-form durable delete.
	var router := _resolve_control_router()
	if router != null and router.has_method("try_dispatch"):
		var r: Dictionary = router.call("try_dispatch", "delete_proposal", {
			"source": "companion_panel",
			"mutation_class": "proposal_only",
		}) as Dictionary
		if proposal_label:
			proposal_label.text = "Delete Proposal only · direct_durable=false"
		_append_local("system", "Delete Proposal requested (not durable).")
		print("[CompanionChat] delete_proposal → %s" % str(r.get("mutation_class", "")))
		return
	if _companion:
		_companion.receive_message("/delete")
		_refresh_personality()


func _resolve_control_router() -> Node:
	## SceneTree-root relative lookup — never absolute "/root/..." (H1-CODEX-F01).
	if not is_inside_tree():
		return null
	var tree := get_tree()
	if tree == null:
		return null
	var r := tree.root
	if r == null:
		return null
	var direct := r.get_node_or_null("ControlContextRouter")
	if direct != null:
		return direct
	for c in r.get_children():
		if str(c.name) == "ControlContextRouter":
			return c
	return null


## ─── Control 1B B1 composer API ──────────────────────────────────────────────

func open_and_focus() -> void:
	visible = true
	focus_input()


func focus_input() -> void:
	if input_line == null:
		return
	input_line.grab_focus()
	input_line.caret_column = input_line.text.length()


func release_focus_input() -> void:
	if input_line and input_line.has_focus():
		input_line.release_focus()


func send_current_input() -> Dictionary:
	## Ctrl+Enter / prompt_send path (C1B-HK-02 / H-03).
	if input_line == null:
		return {"ok": false, "reason": "no_input", "sent": false}
	var text := input_line.text
	if text.strip_edges().is_empty():
		return {"ok": false, "reason": "empty", "sent": false}
	_perform_send(text)
	return {
		"ok": true,
		"sent": true,
		"action": "prompt_send",
		"text": _last_send_text,
		"send_count": _send_count,
	}


func insert_newline() -> Dictionary:
	## Shift+Enter / prompt_newline — insert newline, NEVER send (H-03).
	if input_line == null:
		return {"ok": false, "reason": "no_input", "sent": false}
	var before := input_line.text
	var col := input_line.caret_column
	if col < 0 or col > before.length():
		col = before.length()
	var after := before.substr(0, col) + "\n" + before.substr(col)
	input_line.text = after
	input_line.caret_column = col + 1
	_newline_count += 1
	print("[CompanionChat] prompt_newline inserted (sent=false) count=%d" % _newline_count)
	return {
		"ok": true,
		"sent": false,
		"action": "prompt_newline",
		"newline_count": _newline_count,
		"text": input_line.text,
	}


func get_composer_metrics() -> Dictionary:
	return {
		"send_count": _send_count,
		"newline_count": _newline_count,
		"last_send_text": _last_send_text,
		"last_understanding": _last_understanding,
		"has_proposal": not _last_proposal.is_empty(),
		"input_text": input_line.text if input_line else "",
	}


func set_input_text_for_test(text: String) -> void:
	if input_line:
		input_line.text = text


func is_composer_focused() -> bool:
	return visible and input_line != null and input_line.has_focus()


func is_composer_open() -> bool:
	return visible


func _find_proposal_card() -> Node:
	if not is_inside_tree():
		return null
	var nodes := get_tree().get_nodes_in_group("control_1b_proposal_card")
	if not nodes.is_empty():
		return nodes[0]
	return null
