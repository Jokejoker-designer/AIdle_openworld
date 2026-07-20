extends Node2D

@onready var player: Player = $Player
@onready var companion: Companion = $Companion
@onready var building_system: BuildingSystem = $BuildingSystem
@onready var chat_input: LineEdit = $UI/ChatPanel/ChatInput
@onready var chat_history: RichTextLabel = $UI/ChatPanel/ChatHistory
@onready var progress_bar: ProgressBar = $UI/ProgressBar
@onready var status_label: Label = $UI/StatusLabel

func _ready():
	chat_input.grab_focus()
	chat_input.text_submitted.connect(_on_chat_submitted)
	companion.build_requested.connect(_on_build_requested)
	building_system.progress_changed.connect(_on_progress_changed)
	building_system.build_finished.connect(_on_build_finished)
	
	_add_system_message("Chào mừng đến AIdle Openworld Prototype!")
	_add_system_message("Hãy nói chuyện với AIda. Thử gõ: xây nhà nhỏ")
	status_label.text = "Gõ tin nhắn rồi nhấn Enter"

func _on_chat_submitted(text: String):
	if text.strip_edges() == "":
		return
	
	_add_player_message(text)
	chat_input.text = ""
	
	var reply = companion.receive_message(text)
	_add_companion_message(reply)

func _on_build_requested(building_type: String):
	status_label.text = "AIda đang Manifestation..."
	building_system.start_build(building_type)
	progress_bar.value = 0
	progress_bar.visible = true

func _on_progress_changed(value: float):
	progress_bar.value = value * 100.0

func _on_build_finished():
	status_label.text = "Ngôi nhà đã hiện thực hóa hoàn toàn!"
	await get_tree().create_timer(2.5).timeout
	progress_bar.visible = false
	status_label.text = "Gõ tin nhắn rồi nhấn Enter"

func _add_player_message(text: String):
	chat_history.append_text("[color=#7FDBFF]Bạn:[/color] " + text + "\n")

func _add_companion_message(text: String):
	chat_history.append_text("[color=#FF9CEE]AIda:[/color] " + text + "\n")

func _add_system_message(text: String):
	chat_history.append_text("[color=#AAAAAA]" + text + "[/color]\n")
