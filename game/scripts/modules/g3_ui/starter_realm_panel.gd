## Starter Realm HUD panel — presentation only for G3 vertical slice.
## Text-only surface: quest title, status, preview stage banner, companion placeholder.
## No TTS/STT. No commit controls. No camera mutation (2.5D fixed-angle stays intact).
extends CanvasLayer

@onready var snapshot_label: Label = %SnapshotLabel
@onready var session_label: Label = %SessionLabel
@onready var quest_label: Label = %QuestLabel
@onready var status_label: Label = %StatusLabel
@onready var banner_panel: PanelContainer = %PreviewBanner
@onready var banner_label: Label = %PreviewBannerLabel
@onready var companion_label: Label = %CompanionPlaceholder


func _ready() -> void:
	layer = 12
	visible = true
	if banner_panel:
		banner_panel.visible = false
	if quest_label and quest_label.text.is_empty():
		quest_label.text = "Quest: (none)"
	if status_label and status_label.text.is_empty():
		status_label.text = "Status: —"
	if companion_label and companion_label.text.is_empty():
		companion_label.text = "Companion: (awaiting text)"


func set_session_display(
	snapshot_id: String,
	session_id: String,
	space_id: String,
	world_revision: int,
	progression_phase: String,
	edition: String
) -> void:
	var snap_short := snapshot_id
	if snap_short.length() > 13:
		snap_short = snap_short.substr(0, 8) + "…"
	if snapshot_label:
		snapshot_label.text = "Snapshot: %s" % (snap_short if not snap_short.is_empty() else "(none)")
	if session_label:
		session_label.text = "Session: %s | %s | rev=%d | %s | %s" % [
			session_id if not session_id.is_empty() else "—",
			space_id if not space_id.is_empty() else "—",
			world_revision,
			progression_phase if not progression_phase.is_empty() else "—",
			edition if not edition.is_empty() else "—",
		]


func set_quest_summary(text: String) -> void:
	if quest_label == null:
		return
	if text.is_empty():
		quest_label.text = "Quest: (none)"
	else:
		quest_label.text = "Quest: %s" % text


func set_status(text: String) -> void:
	if status_label == null:
		return
	if text.is_empty():
		status_label.text = "Status: —"
	else:
		status_label.text = "Status: %s" % text


func set_preview_banner(stage: String) -> void:
	if banner_panel == null or banner_label == null:
		return
	if stage.is_empty():
		banner_panel.visible = false
		banner_label.text = ""
		return
	banner_panel.visible = true
	banner_label.text = "Preview: %s" % stage
	# Soft tint by stage (presentation only).
	var style := StyleBoxFlat.new()
	style.bg_color = _banner_color(stage)
	style.set_corner_radius_all(6)
	style.content_margin_left = 10
	style.content_margin_right = 10
	style.content_margin_top = 6
	style.content_margin_bottom = 6
	banner_panel.add_theme_stylebox_override("panel", style)


func set_companion_placeholder(text: String) -> void:
	if companion_label == null:
		return
	if text.is_empty():
		companion_label.text = "Companion: (awaiting text)"
	else:
		companion_label.text = "Companion: %s" % text


func _banner_color(stage: String) -> Color:
	match stage:
		"wireframe":
			return Color(0.25, 0.45, 0.65, 0.85)
		"hologram":
			return Color(0.25, 0.55, 0.75, 0.9)
		"materializing":
			return Color(0.45, 0.4, 0.7, 0.9)
		"complete":
			return Color(0.25, 0.55, 0.35, 0.9)
		_:
			return Color(0.3, 0.3, 0.35, 0.85)
