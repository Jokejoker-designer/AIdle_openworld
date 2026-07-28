## Control 1B runtime consumer for cursor_size_scale + action_label_near_cursor (H-28, A3-F10).
## H1-HUMAN-UX-02: normal OS mouse pointer by default — no forced square cursor proxy in
## Exploration / ordinary UI. Near-cursor action label is optional and a11y-gated.
## Enlarged a11y cursor (scale > 1.0) may show a non-square pointer tip affordance only.
extends CanvasLayer

const BASE_CURSOR_PX := 18.0

var _label: Label
var _cursor_proxy: Control
var _cursor_draw: TextureRect
var _enabled_label: bool = false
var _cursor_scale: float = 1.0
var _action_text: String = "Interact"
var _a11y: Node = null
var _last_applied_scale: float = -1.0
var _custom_cursor_active: bool = false
## H1-CODEX-MB-F06: optional a11y force_custom_cursor (non-square tip). Default false = OS pointer.
var _force_custom_cursor: bool = false


func _ready() -> void:
	layer = 30
	process_mode = Node.PROCESS_MODE_ALWAYS
	_build_ui()
	_resolve_a11y()
	_sync_from_a11y()
	set_process(true)
	add_to_group("control_1b_cursor_label")
	print("[Control1BCursor] runtime consumer ready scale=%.2f label=%s force_custom=%s proxy_default=off" % [
		_cursor_scale, str(_enabled_label), str(_force_custom_cursor)
	])


func _exit_tree() -> void:
	## Always restore OS pointer on teardown (no lingering custom texture RID).
	_clear_custom_cursor()


func _resolve_a11y() -> void:
	if not is_inside_tree():
		return
	var r := get_tree().root
	_a11y = r.get_node_or_null("ControlAccessibilitySettings")
	if _a11y == null:
		for c in r.get_children():
			if str(c.name) == "ControlAccessibilitySettings":
				_a11y = c
				break
	if _a11y != null and _a11y.has_signal("accessibility_changed"):
		if not _a11y.accessibility_changed.is_connected(_on_a11y_changed):
			_a11y.accessibility_changed.connect(_on_a11y_changed)


func _on_a11y_changed(key: String, _value: Variant) -> void:
	if key in ["cursor_size_scale", "action_label_near_cursor", "force_custom_cursor"]:
		_sync_from_a11y()


func _sync_from_a11y() -> void:
	_resolve_a11y()
	if _a11y == null:
		_enabled_label = false
		_cursor_scale = 1.0
		_force_custom_cursor = false
		_apply_cursor_scale()
		_update_proxy_visibility()
		return
	if "cursor_size_scale" in _a11y:
		_cursor_scale = clampf(float(_a11y.cursor_size_scale), 0.75, 2.0)
	if "action_label_near_cursor" in _a11y:
		_enabled_label = bool(_a11y.action_label_near_cursor)
	if "force_custom_cursor" in _a11y:
		_force_custom_cursor = bool(_a11y.force_custom_cursor)
	_apply_cursor_scale()
	_update_proxy_visibility()


func _wants_custom_pointer() -> bool:
	## Non-square a11y tip when scale enlarged OR force_custom_cursor explicitly on.
	## Default (scale≈1 and force=false) keeps normal OS pointer (H1-HUMAN-UX-02).
	return _cursor_scale > 1.01 or _force_custom_cursor


func _wants_enlarged_proxy() -> bool:
	## Backward-compatible name: any custom non-square pointer path.
	return _wants_custom_pointer()


func _update_proxy_visibility() -> void:
	if _cursor_proxy:
		_cursor_proxy.visible = _wants_custom_pointer()
	if _label:
		_label.visible = _enabled_label
	if not _wants_custom_pointer():
		_clear_custom_cursor()


func _build_ui() -> void:
	if _cursor_proxy != null and is_instance_valid(_cursor_proxy):
		return
	var root := Control.new()
	root.name = "Root"
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)

	_cursor_proxy = Control.new()
	_cursor_proxy.name = "CursorProxy"
	_cursor_proxy.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_cursor_proxy.visible = false
	root.add_child(_cursor_proxy)

	# Arrow tip texture (not a solid square ColorRect) — only shown for a11y enlarged scale.
	_cursor_draw = TextureRect.new()
	_cursor_draw.name = "CursorTip"
	_cursor_draw.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_cursor_draw.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_cursor_draw.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_cursor_proxy.add_child(_cursor_draw)

	_label = Label.new()
	_label.name = "ActionLabel"
	_label.text = _action_text
	_label.visible = false
	_label.add_theme_font_size_override("font_size", 13)
	_label.add_theme_color_override("font_color", Color("FFF8E7"))
	_label.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.85))
	_label.add_theme_constant_override("outline_size", 4)
	_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(_label)

	_apply_cursor_scale()
	_update_proxy_visibility()


func _apply_cursor_scale() -> void:
	var px := BASE_CURSOR_PX * _cursor_scale
	if _cursor_draw:
		var h := px * 1.25
		_cursor_draw.custom_minimum_size = Vector2(px, h)
		_cursor_draw.size = Vector2(px, h)
		_cursor_draw.position = Vector2(0, 0)
		_cursor_draw.texture = _make_pointer_texture(int(px), int(h))
	if _label:
		_label.add_theme_font_size_override("font_size", int(round(12.0 + 4.0 * (_cursor_scale - 1.0))))
	# Re-apply whenever scale or force_custom_cursor path changes.
	var want_custom := _wants_custom_pointer()
	if not is_equal_approx(_last_applied_scale, _cursor_scale) or want_custom != _custom_cursor_active:
		_last_applied_scale = _cursor_scale
		if want_custom:
			_try_apply_display_cursor(px)
		else:
			_clear_custom_cursor()


func _make_pointer_texture(w: int, h: int) -> Texture2D:
	var ww: int = maxi(w, 8)
	var hh: int = maxi(h, 10)
	var img := Image.create(ww, hh, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))
	var core := Color(1, 0.97, 0.9, 1)
	var edge := Color(0.1, 0.12, 0.15, 1)
	for y in range(hh):
		for x in range(ww):
			var on := false
			if y < int(hh * 0.55):
				var half_w := int((float(y) / maxf(1.0, hh * 0.55)) * (ww * 0.45))
				if x <= half_w + 1:
					on = true
			elif x <= int(ww * 0.28) and y < int(hh * 0.92):
				on = true
			if on:
				var border := x == 0 or y == 0
				img.set_pixel(x, y, edge if border else core)
	return ImageTexture.create_from_image(img)


func _clear_custom_cursor() -> void:
	if not OS.has_feature("headless") and DisplayServer.get_name() != "headless":
		Input.set_custom_mouse_cursor(null)
	_custom_cursor_active = false


func _try_apply_display_cursor(px: float) -> void:
	## A11y custom/enlarged cursor — arrow-shaped bitmap, never a solid square.
	if OS.has_feature("headless") or DisplayServer.get_name() == "headless":
		return
	if not _wants_custom_pointer():
		_clear_custom_cursor()
		return
	var size_i := int(clampf(px, 16.0, 48.0))
	var h := int(clampf(px * 1.25, 18.0, 56.0))
	var tex := _make_pointer_texture(size_i, h)
	Input.set_custom_mouse_cursor(tex, Input.CURSOR_ARROW, Vector2(1, 1))
	_custom_cursor_active = true


func _process(_delta: float) -> void:
	if not is_inside_tree():
		return
	var pos := get_viewport().get_mouse_position()
	if _cursor_proxy:
		_cursor_proxy.position = pos
		_cursor_proxy.visible = _wants_custom_pointer()
	if _label:
		_label.visible = _enabled_label
		if _enabled_label:
			_label.text = _resolve_action_label()
			_label.position = pos + Vector2(14.0 * _cursor_scale, 10.0 * _cursor_scale)


func _autoload_node(node_name: String) -> Node:
	## SceneTree-root relative lookup — never absolute "/root/..." (H1-CODEX-F01).
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


func _control_router() -> Node:
	return _autoload_node("ControlContextRouter")


func _resolve_action_label() -> String:
	var router := _control_router()
	if router != null and router.has_method("get_hud_actions"):
		var acts: PackedStringArray = router.call("get_hud_actions") as PackedStringArray
		if not acts.is_empty():
			return str(acts[0]).replace("_", " ")
	return _action_text


func set_action_text(text: String) -> void:
	_action_text = text
	if _label and _enabled_label:
		_label.text = text


func get_runtime_snapshot() -> Dictionary:
	if _cursor_proxy == null or _label == null:
		_build_ui()
	return {
		"consumer": "control_1b_cursor_label",
		"cursor_size_scale": _cursor_scale,
		"action_label_near_cursor": _enabled_label,
		"force_custom_cursor": _force_custom_cursor,
		"cursor_proxy_visible": _cursor_proxy != null and _cursor_proxy.visible,
		"label_visible": _label != null and _label.visible,
		"proxy_px": BASE_CURSOR_PX * _cursor_scale,
		"readable_large": _cursor_scale >= 1.4,
		"os_pointer_default": not _force_custom_cursor and not _wants_custom_pointer() and not _custom_cursor_active,
		"forced_square_proxy": false,
		"custom_cursor_active": _custom_cursor_active,
		"custom_pointer_shape": "arrow_tip_non_square",
	}


func apply_scale_for_test(scale: float) -> void:
	if _cursor_proxy == null:
		_build_ui()
	_cursor_scale = clampf(scale, 0.75, 2.0)
	_apply_cursor_scale()
	_update_proxy_visibility()


func set_force_custom_cursor_for_test(enabled: bool) -> void:
	## Test helper for optional a11y force_custom_cursor wiring (default remains off).
	if _cursor_proxy == null:
		_build_ui()
	_force_custom_cursor = enabled
	_apply_cursor_scale()
	_update_proxy_visibility()


func set_label_enabled_for_test(enabled: bool) -> void:
	if _label == null:
		_build_ui()
	_enabled_label = enabled
	if _label:
		_label.visible = enabled
