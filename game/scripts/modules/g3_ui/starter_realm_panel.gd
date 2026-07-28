## Starter Realm status — high-contrast pill, min 12px (Directive 24 C003).
extends CanvasLayer

@onready var snapshot_label: Label = %SnapshotLabel
@onready var session_label: Label = %SessionLabel
@onready var quest_label: Label = %QuestLabel
@onready var status_label: Label = %StatusLabel
@onready var banner_panel: PanelContainer = %PreviewBanner
@onready var banner_label: Label = %PreviewBannerLabel
@onready var companion_label: Label = %CompanionPlaceholder
@onready var top_right: Control = $Root/TopRight
@onready var title_label: Label = $Root/TopRight/Title

var status_pill: PanelContainer = null
var _debug_visible: bool = false
const MIN_PLAYER_FONT := 12


func _ready() -> void:
	layer = 12
	visible = true
	_ensure_status_pill()
	_apply_responsive()
	get_viewport().size_changed.connect(_apply_responsive)
	if banner_panel:
		banner_panel.visible = false
	# Product default: snapshot/session QA counters off unless F3 debug overlay is on.
	_set_debug_visible(SettingsManager.is_debug_overlay_enabled() if SettingsManager else false)
	if not EventBus.debug_toggled.is_connected(_on_debug_toggled):
		EventBus.debug_toggled.connect(_on_debug_toggled)
	if quest_label and (quest_label.text.is_empty() or quest_label.text == "Quest: (none)"):
		quest_label.text = "Talk to Companion · request a small build"
	if status_label and (status_label.text.is_empty() or status_label.text.begins_with("Status:")):
		status_label.text = "Ready"
	if companion_label:
		companion_label.text = "Companion: press C to chat"
	if title_label:
		title_label.text = "Starter Realm"
	add_to_group("h1_product_realm_panel")


func _ensure_status_pill() -> void:
	var root := get_node_or_null("Root") as Control
	if root == null:
		return
	status_pill = root.get_node_or_null("StatusPill") as PanelContainer
	if status_pill != null:
		return
	if top_right == null:
		top_right = root.get_node_or_null("TopRight") as Control
	if top_right == null:
		return
	status_pill = PanelContainer.new()
	status_pill.name = "StatusPill"
	status_pill.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	status_pill.offset_left = -280
	status_pill.offset_top = 40
	status_pill.offset_right = -10
	status_pill.offset_bottom = 180
	var parent := top_right.get_parent()
	if parent:
		parent.remove_child(top_right)
	root.add_child(status_pill)
	status_pill.add_child(top_right)
	top_right.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


func _on_debug_toggled(on: bool) -> void:
	_set_debug_visible(on)


func _set_debug_visible(on: bool) -> void:
	_debug_visible = on
	if snapshot_label:
		snapshot_label.visible = on
	if session_label:
		session_label.visible = on


func _apply_responsive() -> void:
	var vp := get_viewport().get_visible_rect().size
	var compact := vp.x < 1000.0 or vp.y < 600.0
	var fs := MIN_PLAYER_FONT  # never below 12px (WO C003)
	if status_pill:
		var sb := StyleBoxFlat.new()
		sb.bg_color = Color(0.07, 0.09, 0.12, 0.92)
		sb.set_corner_radius_all(10)
		sb.content_margin_left = 12
		sb.content_margin_right = 12
		sb.content_margin_top = 8
		sb.content_margin_bottom = 8
		sb.border_width_left = 1
		sb.border_width_top = 1
		sb.border_width_right = 1
		sb.border_width_bottom = 1
		sb.border_color = Color("FFF1C7").darkened(0.15)
		status_pill.add_theme_stylebox_override("panel", sb)
		status_pill.offset_left = -minf(vp.x * 0.42, 300.0 if not compact else 260.0)
		status_pill.offset_right = -10.0
		status_pill.offset_top = 40.0 if compact else 48.0
		status_pill.offset_bottom = 190.0 if compact else 210.0
	if top_right:
		top_right.offset_left = 0
		top_right.offset_right = 0
		top_right.offset_top = 0
		top_right.offset_bottom = 0
	for child in (top_right.get_children() if top_right else []):
		if child is Label:
			var lbl := child as Label
			lbl.add_theme_font_size_override("font_size", fs)
			lbl.add_theme_color_override("font_color", Color("FFF8E7"))
			lbl.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.8))
			lbl.add_theme_constant_override("outline_size", 2)
			lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART


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
		quest_label.text = "Quest: explore your Starter Realm"
	else:
		quest_label.text = "Quest: %s" % text


func set_status(text: String) -> void:
	if status_label == null:
		return
	if text.is_empty():
		status_label.text = "Ready"
	else:
		var t := text
		if t.length() > 72:
			t = t.substr(0, 69) + "…"
		status_label.text = t


func set_preview_banner(stage: String) -> void:
	if banner_panel == null or banner_label == null:
		return
	if stage.is_empty():
		banner_panel.visible = false
		banner_label.text = ""
		return
	banner_panel.visible = true
	# Text + glyph (not color alone) for ordered manifestation stages.
	var glyph := "·"
	var label := stage
	match stage:
		"wireframe":
			glyph = "▢"
			label = "Wireframe · outline"
		"hologram":
			glyph = "◈"
			label = "Hologram · glow"
		"materializing":
			glyph = "▣"
			label = "Materializing · solidifying"
		"complete":
			glyph = "■"
			label = "Complete · solid"
		"preview":
			glyph = "◈"
			label = "Preview (not committed)"
	banner_label.text = "%s Building: %s" % [glyph, label]
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
		companion_label.text = "Companion: press C to chat (text-only)"
	else:
		companion_label.text = "Companion: %s" % text


func _banner_color(stage: String) -> Color:
	match stage:
		"wireframe":
			return Color(0.15, 0.45, 0.55, 0.92)
		"hologram":
			return Color(0.1, 0.55, 0.75, 0.94)
		"materializing":
			return Color(0.35, 0.45, 0.55, 0.94)
		"complete":
			return Color(0.25, 0.55, 0.35, 0.94)
		_:
			return Color(0.25, 0.28, 0.32, 0.9)
