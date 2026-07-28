## Playable action bar — two-row compact layout at 868x517 (Directive 23).
extends CanvasLayer

signal companion_toggled
signal bridge_export_pressed
signal bridge_import_pressed
signal demo_build_pressed
signal confirm_pressed
signal cancel_pressed
## Nori-7 Object DNA gardener package (presentation-only triggers).
signal gardener_action_pressed(action_id: String)

const INK := Color("263238")
const CREAM := Color("FFF1C7")
const MUTED := Color(0.35, 0.38, 0.42, 0.9)
const MIN_BTN_H := 32
const MIN_BTN_W_COMPACT := 100
const MIN_BTN_W := 108

@onready var root: Control = $Root
@onready var margin: MarginContainer = $Root/Margin
@onready var rows: VBoxContainer = $Root/Margin/Rows
@onready var row1: HBoxContainer = $Root/Margin/Rows/Row1
@onready var row2: HBoxContainer = $Root/Margin/Rows/Row2
@onready var edition_label: Label = %EditionLabel
@onready var btn_companion: Button = %BtnCompanion
@onready var btn_export: Button = %BtnExport
@onready var btn_import: Button = %BtnImport
@onready var btn_demo: Button = %BtnDemoBuild
@onready var btn_confirm: Button = %BtnConfirm
@onready var btn_cancel: Button = %BtnCancel

var row3: HBoxContainer = null
var btn_water: Button = null
var btn_plant: Button = null
var btn_harvest: Button = null
var btn_charge: Button = null
var btn_low_energy: Button = null
var btn_scan: Button = null

var _flow_state: String = "idle"


func _ready() -> void:
	layer = 14
	process_mode = Node.PROCESS_MODE_ALWAYS
	_ensure_two_rows()
	_ensure_gardener_row()
	_style_all_buttons()
	_apply_responsive_layout()
	get_viewport().size_changed.connect(_apply_responsive_layout)
	if btn_companion:
		btn_companion.pressed.connect(func(): companion_toggled.emit())
	if btn_export:
		btn_export.pressed.connect(func(): bridge_export_pressed.emit())
	if btn_import:
		btn_import.pressed.connect(func(): bridge_import_pressed.emit())
	if btn_demo:
		btn_demo.pressed.connect(func(): demo_build_pressed.emit())
	if btn_confirm:
		btn_confirm.pressed.connect(func(): confirm_pressed.emit())
	if btn_cancel:
		btn_cancel.pressed.connect(func(): cancel_pressed.emit())
	_wire_gardener_buttons()
	_refresh_edition()
	set_flow_state("idle")
	EventBus.art_style_changed.connect(func(_s): _refresh_edition())


func _ensure_two_rows() -> void:
	## Support old single HBox layout by wrapping into Rows if needed.
	if rows != null and row1 != null and row2 != null:
		return
	var old_bar := get_node_or_null("Root/Margin/Bar") as HBoxContainer
	if margin == null or old_bar == null:
		return
	rows = VBoxContainer.new()
	rows.name = "Rows"
	rows.add_theme_constant_override("separation", 4)
	margin.remove_child(old_bar)
	margin.add_child(rows)
	row1 = HBoxContainer.new()
	row1.name = "Row1"
	row1.alignment = BoxContainer.ALIGNMENT_CENTER
	row1.add_theme_constant_override("separation", 6)
	row2 = HBoxContainer.new()
	row2.name = "Row2"
	row2.alignment = BoxContainer.ALIGNMENT_CENTER
	row2.add_theme_constant_override("separation", 6)
	rows.add_child(row1)
	rows.add_child(row2)
	# Reparent children: companion, export, import → row1; demo, confirm, cancel → row2
	for c in old_bar.get_children():
		old_bar.remove_child(c)
		var n := str(c.name)
		if n.begins_with("BtnDemo") or n.begins_with("BtnConfirm") or n.begins_with("BtnCancel"):
			row2.add_child(c)
		elif n == "HintLabel":
			c.queue_free()
		else:
			row1.add_child(c)
	old_bar.queue_free()
	btn_companion = %BtnCompanion if has_node("%BtnCompanion") else row1.get_node_or_null("BtnCompanion") as Button
	btn_export = %BtnExport if has_node("%BtnExport") else row1.get_node_or_null("BtnExport") as Button
	btn_import = %BtnImport if has_node("%BtnImport") else row1.get_node_or_null("BtnImport") as Button
	btn_demo = %BtnDemoBuild if has_node("%BtnDemoBuild") else row2.get_node_or_null("BtnDemoBuild") as Button
	btn_confirm = %BtnConfirm if has_node("%BtnConfirm") else row2.get_node_or_null("BtnConfirm") as Button
	btn_cancel = %BtnCancel if has_node("%BtnCancel") else row2.get_node_or_null("BtnCancel") as Button


func _ensure_gardener_row() -> void:
	## Row3: Nori gardener package — Water / Plant / Harvest / Charge / Low energy.
	if rows == null:
		return
	row3 = rows.get_node_or_null("Row3") as HBoxContainer
	if row3 == null:
		row3 = HBoxContainer.new()
		row3.name = "Row3"
		row3.alignment = BoxContainer.ALIGNMENT_CENTER
		row3.add_theme_constant_override("separation", 6)
		rows.add_child(row3)
	btn_water = _ensure_gardener_btn(row3, "BtnWater", "💧 Water")
	btn_plant = _ensure_gardener_btn(row3, "BtnPlant", "🌱 Plant")
	btn_harvest = _ensure_gardener_btn(row3, "BtnHarvest", "🧺 Harvest")
	btn_charge = _ensure_gardener_btn(row3, "BtnCharge", "⚡ Charge")
	btn_low_energy = _ensure_gardener_btn(row3, "BtnLowEnergy", "😴 Rest")
	btn_scan = _ensure_gardener_btn(row3, "BtnScan", "🔍 Scan")


func _ensure_gardener_btn(parent: HBoxContainer, node_name: String, label: String) -> Button:
	var existing := parent.get_node_or_null(node_name) as Button
	if existing != null:
		return existing
	var b := Button.new()
	b.name = node_name
	b.text = label
	b.focus_mode = Control.FOCUS_NONE
	b.custom_minimum_size = Vector2(MIN_BTN_W_COMPACT, MIN_BTN_H)
	parent.add_child(b)
	return b


func _wire_gardener_buttons() -> void:
	_connect_gardener(btn_water, "water")
	_connect_gardener(btn_plant, "plant_seed")
	_connect_gardener(btn_harvest, "harvest")
	_connect_gardener(btn_charge, "charge")
	_connect_gardener(btn_low_energy, "low_energy")
	_connect_gardener(btn_scan, "scan")


func _connect_gardener(b: Button, action_id: String) -> void:
	if b == null:
		return
	# Fresh Callable each connect; guard with meta so re-wire is safe.
	var meta_key := "gardener_wired_%s" % action_id
	if bool(b.get_meta(meta_key, false)):
		return
	b.pressed.connect(func(): gardener_action_pressed.emit(action_id))
	b.set_meta(meta_key, true)


func _style_all_buttons() -> void:
	# Mouse-driven action bar (WO-G8-UX-001): never steal keyboard focus for
	# WASD/arrows after a click. Keyboard a11y later can re-enable FOCUS_ALL
	# only if every pressed handler also calls release_focus().
	var all_btns: Array = [
		btn_companion, btn_export, btn_import, btn_demo, btn_confirm, btn_cancel,
		btn_water, btn_plant, btn_harvest, btn_charge, btn_low_energy, btn_scan,
	]
	for b in all_btns:
		if b == null:
			continue
		b.focus_mode = Control.FOCUS_NONE
		_apply_btn_style(b, false)


func _apply_btn_style(b: Button, primary: bool) -> void:
	var normal := StyleBoxFlat.new()
	normal.bg_color = CREAM if primary else Color(0.12, 0.14, 0.18, 0.94)
	normal.set_corner_radius_all(6)
	normal.content_margin_left = 10
	normal.content_margin_right = 10
	normal.content_margin_top = 6
	normal.content_margin_bottom = 6
	var hover := normal.duplicate() as StyleBoxFlat
	hover.bg_color = (CREAM if primary else Color(0.18, 0.2, 0.26, 0.96)).lightened(0.06)
	var pressed := normal.duplicate() as StyleBoxFlat
	pressed.bg_color = (CREAM if primary else Color(0.1, 0.11, 0.14, 0.96)).darkened(0.06)
	var disabled := normal.duplicate() as StyleBoxFlat
	disabled.bg_color = MUTED
	b.add_theme_stylebox_override("normal", normal)
	b.add_theme_stylebox_override("hover", hover)
	b.add_theme_stylebox_override("pressed", pressed)
	b.add_theme_stylebox_override("disabled", disabled)
	b.add_theme_color_override("font_color", INK if primary else Color(0.96, 0.97, 0.98))
	b.add_theme_color_override("font_disabled_color", Color(0.72, 0.74, 0.76, 0.7))
	b.add_theme_font_size_override("font_size", 12)


func _apply_responsive_layout() -> void:
	if root == null:
		return
	var vp := get_viewport().get_visible_rect().size
	var compact := vp.x < 1000.0 or vp.y < 600.0
	var min_w := MIN_BTN_W_COMPACT if compact else MIN_BTN_W
	if margin:
		# Three rows (incl. gardener) need more bottom chrome height.
		margin.offset_top = -112.0 if compact else -104.0
	if rows:
		rows.add_theme_constant_override("separation", 4 if compact else 6)
	var all_btns: Array = [
		btn_companion, btn_export, btn_import, btn_demo, btn_confirm, btn_cancel,
		btn_water, btn_plant, btn_harvest, btn_charge, btn_low_energy, btn_scan,
	]
	for b in all_btns:
		if b == null:
			continue
		var is_garden: bool = (b == btn_water or b == btn_plant or b == btn_harvest or b == btn_charge or b == btn_low_energy)
		var bw := minf(float(min_w), 96.0) if is_garden else float(min_w)
		b.custom_minimum_size = Vector2(bw, MIN_BTN_H)
		b.add_theme_font_size_override("font_size", 11 if compact else 12)
	if btn_export:
		# Secondary bridge path — not primary creative chrome.
		btn_export.text = "Share file"
	if btn_import:
		btn_import.text = "Open file"
	if btn_companion:
		btn_companion.text = "Companion (E)"
	if btn_demo:
		# Cursor-led Manual Build shortcut (H1-HUMAN-BUILD-01); Companion flow remains primary.
		btn_demo.text = "Manual Build"
	if btn_confirm:
		btn_confirm.text = "✓ Confirm"
	if btn_cancel:
		btn_cancel.text = "✕ Cancel"
	if edition_label:
		edition_label.visible = not compact
		edition_label.add_theme_font_size_override("font_size", 11)


func _refresh_edition() -> void:
	if edition_label == null:
		return
	# Product chrome: normal first-session edition chip only (H1-CODEX-F03).
	var ed := "Free Bridge (manual)"
	if SettingsManager != null and SettingsManager.has_method("get_edition"):
		var raw := str(SettingsManager.get_edition())
		if raw.find("free") >= 0 or raw.find("desktop") >= 0:
			ed = "Free Bridge (manual)"
		elif raw.find("api") >= 0 or raw.find("paid") >= 0:
			ed = "API Gateway"
		else:
			ed = "Private Reality"
	var art := ArtStyleManager.get_active_style_id() if ArtStyleManager else "—"
	edition_label.text = "%s · %s" % [ed, art]


func set_preview_active(active: bool) -> void:
	set_flow_state("confirmable" if active else "idle")


func set_flow_state(state: String) -> void:
	_flow_state = state
	match state:
		"previewing", "confirmable":
			if btn_confirm:
				btn_confirm.disabled = false
				_apply_btn_style(btn_confirm, true)
			if btn_cancel:
				btn_cancel.disabled = false
				_apply_btn_style(btn_cancel, false)
			if btn_demo:
				btn_demo.disabled = true
				_apply_btn_style(btn_demo, false)
		_:
			if btn_confirm:
				btn_confirm.disabled = true
				_apply_btn_style(btn_confirm, false)
			if btn_cancel:
				btn_cancel.disabled = true
				_apply_btn_style(btn_cancel, false)
			if btn_demo:
				btn_demo.disabled = false
				_apply_btn_style(btn_demo, true)


## Geometry helpers for headed harness.
func get_action_bar_global_rect() -> Rect2:
	if margin:
		return margin.get_global_rect()
	if root:
		return root.get_global_rect()
	return Rect2()
