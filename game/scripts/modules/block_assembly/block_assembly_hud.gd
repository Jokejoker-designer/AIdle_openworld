## P2E-001 / UCBV C2 plain-language Block Assembly HUD.
## Categorized 28-module catalog selector (name + preview meta), elevation labels,
## Delete red-X status. Responsive at 1280x720 and 868x517 — no diagnostic wall.
class_name BlockAssemblyHud
extends CanvasLayer

const MAX_LINES := 10

var _root: Control
var _panel: PanelContainer
var _title: Label
var _body: RichTextLabel
var _catalog: RichTextLabel
var _hint: Label
var _controller: Node = null
var _visible_build: bool = false
var _category_buttons: HBoxContainer = null


func _ready() -> void:
	layer = 12
	process_mode = Node.PROCESS_MODE_ALWAYS
	_build_ui()
	if get_viewport() != null and not get_viewport().size_changed.is_connected(_apply_responsive):
		get_viewport().size_changed.connect(_apply_responsive)
	_apply_responsive()
	add_to_group("block_assembly_hud")
	visible = false


func bind_controller(ctrl: Node) -> void:
	_controller = ctrl
	if _controller != null and _controller.has_signal("hud_state_changed"):
		if not _controller.hud_state_changed.is_connected(_on_hud_state):
			_controller.hud_state_changed.connect(_on_hud_state)
	if _controller != null and _controller.has_signal("preview_changed"):
		if not _controller.preview_changed.is_connected(_on_preview):
			_controller.preview_changed.connect(_on_preview)
	if _controller != null and _controller.has_signal("picker_changed"):
		if not _controller.picker_changed.is_connected(_on_picker):
			_controller.picker_changed.connect(_on_picker)
	refresh()


func set_build_visible(is_build: bool) -> void:
	_visible_build = is_build
	visible = is_build
	if is_build:
		refresh()


func refresh() -> void:
	if _controller == null or not _controller.has_method("get_hud_state"):
		return
	var st: Dictionary = _controller.call("get_hud_state") as Dictionary
	_apply_state(st)
	_refresh_catalog()


func _on_hud_state(st: Dictionary) -> void:
	_apply_state(st)
	_refresh_catalog()


func _on_preview(_st: Dictionary) -> void:
	refresh()


func _on_picker(_st: Dictionary) -> void:
	_refresh_catalog()


func _apply_state(st: Dictionary) -> void:
	if _body == null:
		return
	var mod := str(st.get("module", "—"))
	var mod_name := str(st.get("module_display_name", st.get("highlighted_display_name", mod)))
	var mod_cat := str(st.get("module_category", ""))
	var hi := str(st.get("highlighted", mod))
	var ctx := str(st.get("context", "—"))
	var snap := str(st.get("snap", "—"))
	var valid := str(st.get("validity", "—"))
	var reason := str(st.get("validity_reason", ""))
	var rot := str(st.get("rotation", "—"))
	var elev := str(st.get("elevation", "—"))
	var elev_label := str(st.get("elevation_label", "Lift (PgUp/PgDn)"))
	var rot_label := str(st.get("rotation_label", "Rotate (Q/R)"))
	var conf := bool(st.get("confirm_enabled", false))
	var can := bool(st.get("cancel_enabled", false))
	var stage := str(st.get("stage", "—"))
	var catalog_count := int(st.get("catalog_count", 0))
	var delete_mode := bool(st.get("delete_mode", false))
	var delete_target := str(st.get("delete_target_entity_id", ""))
	var cursor_mode := bool(st.get("manual_cursor_follow", false)) or bool(st.get("manual_build", false))
	var cursor_hit_present: bool = st.has("cursor_hit_valid")
	var cursor_valid: bool = bool(st.get("cursor_hit_valid", false))
	var rotate_reason := str(st.get("last_rotate_reason", ""))
	var stage_label := stage
	match stage:
		"wireframe":
			stage_label = "▢ Wireframe · outline"
		"hologram":
			stage_label = "◈ Hologram · glow"
		"materializing":
			stage_label = "▣ Materializing · solidifying"
		"complete":
			stage_label = "■ Complete · solid"
		"—", "":
			stage_label = "— choose a module"
	if delete_mode:
		_title.text = "Delete · red-X"
		_title.add_theme_color_override("font_color", Color(1.0, 0.35, 0.3))
	else:
		_title.text = "Manual Build · %s" % ctx if cursor_mode else "Build · %s" % ctx
		_title.add_theme_color_override("font_color", Color(1, 0.97, 0.9))
	var mod_line := "Module: %s" % mod_name
	if not mod_cat.is_empty():
		mod_line = "Module: %s [%s]" % [mod_name, mod_cat]
	if mod_name != mod and not mod.is_empty() and mod != "—":
		mod_line += " (%s)" % mod
	var lines := PackedStringArray([
		mod_line,
		"Catalog: %d modules · Highlighted: %s" % [catalog_count if catalog_count > 0 else 28, hi],
		"Stage: %s" % stage_label,
		"Snap: %s" % snap,
		"%s: %s · %s: %s" % [rot_label, rot, elev_label, elev],
		"Status: %s — %s" % [valid, reason],
		"Confirm [✓]: %s · Cancel [✕]: %s" % [
			"ready" if conf else "disabled",
			"ready" if can else "disabled",
		],
	])
	if delete_mode:
		lines.append(
			"Delete target: %s · cursor=red X · World Commit only" % (
				delete_target if not delete_target.is_empty() else "(LMB select committed)"
			)
		)
	if cursor_mode and not delete_mode:
		var cv := "—"
		if cursor_hit_present:
			cv = "valid surface" if cursor_valid else "invalid surface"
		lines.append("Cursor: %s · LMB preview only" % cv)
	if not rotate_reason.is_empty() and not bool(st.get("confirm_enabled", false)):
		if "cannot rotate" in rotate_reason or "unavailable" in rotate_reason:
			lines.append(rotate_reason)
	_body.text = "\n".join(lines)
	if delete_mode:
		_hint.text = "Delete red-X · LMB select owned · Enter confirm compensation · Esc/RMB exit · Undo restores"
	else:
		_hint.text = "Catalog · LMB/P place · Q/R rotate · Lift PgUp/PgDn · Enter confirm · Del erase · Esc cancel"
	if _visible_build or delete_mode:
		visible = true


func _refresh_catalog() -> void:
	if _catalog == null or _controller == null:
		return
	if not _controller.has_method("get_catalog_ui_state"):
		_catalog.text = "(catalog state unavailable)"
		return
	var cat: Dictionary = _controller.call("get_catalog_ui_state") as Dictionary
	var entries: Array = cat.get("all_entries", cat.get("entries", [])) as Array
	var hi := str(cat.get("highlighted_module_id", ""))
	var filter := str(cat.get("category_filter", ""))
	var by_cat: Dictionary = {}
	for e in entries:
		if not (e is Dictionary):
			continue
		var ed: Dictionary = e
		var cname := str(ed.get("category", "Other"))
		if not filter.is_empty() and cname != filter:
			continue
		if not by_cat.has(cname):
			by_cat[cname] = []
		(by_cat[cname] as Array).append(ed)
	var lines := PackedStringArray()
	lines.append("Module catalog (%d)" % int(cat.get("module_count", entries.size())))
	var order: PackedStringArray = PackedStringArray([
		"Primitive", "Architecture", "Terrain", "Cluster", "Prop", "Character"
	])
	var seen := {}
	for c in order:
		if not by_cat.has(c):
			continue
		seen[c] = true
		lines.append("· %s" % c)
		for ed2 in by_cat[c]:
			var mid := str((ed2 as Dictionary).get("module_id", ""))
			var dname := str((ed2 as Dictionary).get("display_name", mid))
			var mark := "►" if mid == hi else " "
			var preview := "preview"
			if bool((ed2 as Dictionary).get("has_descriptor", false)):
				preview = "mesh"
			lines.append("  %s %s · %s" % [mark, dname, preview])
	for c2 in by_cat.keys():
		if seen.has(c2):
			continue
		lines.append("· %s" % str(c2))
		for ed3 in by_cat[c2]:
			var mid2 := str((ed3 as Dictionary).get("module_id", ""))
			var dname2 := str((ed3 as Dictionary).get("display_name", mid2))
			var mark2 := "►" if mid2 == hi else " "
			lines.append("  %s %s" % [mark2, dname2])
	_catalog.text = "\n".join(lines)


func _build_ui() -> void:
	_root = Control.new()
	_root.name = "Root"
	_root.set_anchors_preset(Control.PRESET_FULL_RECT)
	_root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_root)

	_panel = PanelContainer.new()
	_panel.name = "BaPanel"
	_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.06, 0.08, 0.11, 0.88)
	sb.set_corner_radius_all(10)
	sb.content_margin_left = 12
	sb.content_margin_right = 12
	sb.content_margin_top = 8
	sb.content_margin_bottom = 8
	sb.border_width_left = 1
	sb.border_width_top = 1
	sb.border_width_right = 1
	sb.border_width_bottom = 1
	sb.border_color = Color(0.95, 0.9, 0.7, 0.55)
	_panel.add_theme_stylebox_override("panel", sb)
	_root.add_child(_panel)

	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 4)
	_panel.add_child(v)

	_title = Label.new()
	_title.text = "Build"
	_title.add_theme_font_size_override("font_size", 14)
	_title.add_theme_color_override("font_color", Color(1, 0.97, 0.9))
	v.add_child(_title)

	_body = RichTextLabel.new()
	_body.bbcode_enabled = false
	_body.fit_content = true
	_body.scroll_active = false
	_body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_body.custom_minimum_size = Vector2(280, 110)
	_body.add_theme_font_size_override("normal_font_size", 12)
	_body.add_theme_color_override("default_color", Color(0.95, 0.95, 0.92))
	v.add_child(_body)

	_catalog = RichTextLabel.new()
	_catalog.name = "CatalogList"
	_catalog.bbcode_enabled = false
	_catalog.fit_content = false
	_catalog.scroll_active = true
	_catalog.autowrap_mode = TextServer.AUTOWRAP_OFF
	_catalog.custom_minimum_size = Vector2(280, 120)
	_catalog.add_theme_font_size_override("normal_font_size", 11)
	_catalog.add_theme_color_override("default_color", Color(0.88, 0.9, 0.85))
	v.add_child(_catalog)

	_hint = Label.new()
	_hint.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_hint.add_theme_font_size_override("font_size", 11)
	_hint.add_theme_color_override("font_color", Color(0.85, 0.88, 0.8))
	_hint.text = "Catalog · Place · Rotate · Lift · Confirm · Delete · Cancel"
	v.add_child(_hint)


func _apply_responsive() -> void:
	if _panel == null or get_viewport() == null:
		return
	var sz := get_viewport().get_visible_rect().size
	# Top-left card; compact on 868x517 so bottom context HUD never overlaps (F05-R2).
	var margin := 8.0 if sz.y < 560.0 else 12.0
	var width := mini(320.0, maxf(220.0, sz.x * 0.30)) if sz.y < 560.0 else mini(360.0, maxf(260.0, sz.x * 0.34))
	var height := 220.0 if sz.y < 560.0 else 320.0
	_panel.anchor_left = 0.0
	_panel.anchor_top = 0.0
	_panel.anchor_right = 0.0
	_panel.anchor_bottom = 0.0
	_panel.offset_left = margin
	_panel.offset_top = margin + 4.0
	_panel.offset_right = margin + width
	_panel.offset_bottom = margin + 4.0 + height
	# Keep fully inside viewport.
	if _panel.offset_right > sz.x - margin:
		_panel.offset_right = sz.x - margin
		_panel.offset_left = maxf(margin, _panel.offset_right - width)
	if _panel.offset_bottom > sz.y - 72.0:
		_panel.offset_bottom = sz.y - 72.0
		_panel.offset_top = maxf(margin, _panel.offset_bottom - height)
	if _body != null:
		_body.custom_minimum_size = Vector2(width - 24.0, 72.0 if sz.y < 560.0 else 100.0)
	if _catalog != null:
		_catalog.custom_minimum_size = Vector2(width - 24.0, 80.0 if sz.y < 560.0 else 140.0)
		_catalog.visible = sz.y >= 480.0
	if _hint != null:
		_hint.visible = sz.y >= 540.0
	if _title != null:
		_title.add_theme_font_size_override("font_size", 12 if sz.y < 560.0 else 14)
