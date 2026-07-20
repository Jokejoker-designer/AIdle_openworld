## Minimal text chat + proposal / personality controls panel (no voice/mic/TTS).
## Lives under Companion module scripts; scene may be placed under scenes/ui.
extends Control

@onready var log_label: RichTextLabel = %ChatLog
@onready var input_line: LineEdit = %ChatInput
@onready var proposal_label: Label = %ProposalStatus
@onready var personality_label: Label = %PersonalityStatus

var _companion: CompanionModule


func _ready() -> void:
	visible = true
	if input_line:
		input_line.text_submitted.connect(_on_text_submitted)
		input_line.placeholder_text = "Text only — try: xây nhà · /inspect · /lock warmth · /reset · /delete · /tools · /agm"
	_bind_companion()
	_refresh_personality()
	if log_label:
		log_label.append_text(
			"[i]Companion text panel (no STT/TTS). AGM dialogue + pending proposals only; no commit.[/i]\n"
		)


func _bind_companion() -> void:
	if ModuleRegistry.has_module(AIdleConstants.MODULE_COMPANION):
		var m := ModuleRegistry.get_module(AIdleConstants.MODULE_COMPANION)
		if m is CompanionModule:
			_companion = m as CompanionModule
	if _companion == null:
		# Late bind: wait for module_registered.
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


func _on_text_submitted(text: String) -> void:
	if input_line:
		input_line.text = ""
	if _companion == null:
		_bind_companion()
	if _companion == null:
		_append_local("system", "Companion module not registered yet.")
		return
	_companion.receive_message(text)
	_refresh_personality()


func _on_chat_message(role: String, text: String) -> void:
	_append_local(role, text)


func _on_proposal_ready(proposal: Dictionary) -> void:
	if proposal_label == null:
		return
	var pid := str(proposal.get("prompt_id", "?"))
	var entity_info: Dictionary = proposal.get("entity", {}) as Dictionary
	var conf_info: Dictionary = proposal.get("confirmation", {}) as Dictionary
	var recipe := str(entity_info.get("recipe_id", "?"))
	var state := str(conf_info.get("state", "?"))
	proposal_label.text = "Proposal: %s | %s | state=%s (pending only)" % [recipe, pid.substr(0, 8), state]


func _on_personality_control(_action: String, _detail: Dictionary) -> void:
	_refresh_personality()


func _refresh_personality() -> void:
	if personality_label == null:
		return
	if _companion == null:
		personality_label.text = "Personality: (no companion)"
		return
	var p := _companion.get_personality()
	if p == null:
		return
	personality_label.text = "Personality rev=%d adapt=%s privacy=%s" % [
		p.revision,
		"on" if bool(p.adaptation_policy.get("enabled", false)) else "off",
		p.privacy_mode,
	]


func _append_local(role: String, text: String) -> void:
	if log_label == null:
		return
	var color := "#9ad" if role == "companion" else ("#ccc" if role == "player" else "#888")
	log_label.append_text("[color=%s][b]%s[/b][/color]: %s\n" % [color, role, text])


func _on_inspect_pressed() -> void:
	if _companion:
		_companion.receive_message("/inspect")
		_refresh_personality()


func _on_reset_pressed() -> void:
	if _companion:
		_companion.receive_message("/reset")
		_refresh_personality()


func _on_delete_pressed() -> void:
	if _companion:
		_companion.receive_message("/delete")
		_refresh_personality()
