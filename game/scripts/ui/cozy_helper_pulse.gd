## Cozy Helper Pulse (V / world_ability) — non-durable visual/feedback only.
## Non-square ring/pulse treatment (H1-HUMAN-UX-01). No inventory/ownership/currency mint.
extends CanvasLayer

signal pulse_fired(payload: Dictionary)
signal pulse_finished()

var _overlay: Control
var _ring: TextureRect
var _label: Label
var _pattern_label: Label
var _active: bool = false
var _time_left: float = 0.0
var _pulse_count: int = 0
const PULSE_DURATION := 0.85
const RING_DIAMETER := 148.0


func _ready() -> void:
	layer = 12
	process_mode = Node.PROCESS_MODE_ALWAYS
	visible = false
	_build_ui()
	set_process(false)
	add_to_group("control_1b_helper_pulse")


func is_active() -> bool:
	return _active


func get_pulse_count() -> int:
	return _pulse_count


func fire_pulse(reason: String = "world_ability") -> Dictionary:
	## Non-durable feedback only. Explicitly rejects mint semantics.
	if _overlay == null or _ring == null:
		_build_ui()
	_pulse_count += 1
	var payload := {
		"ok": true,
		"non_durable": true,
		"mints_inventory": false,
		"mints_ownership": false,
		"mints_currency": false,
		"direct_durable": false,
		"reason": reason,
		"pulse_id": _pulse_count,
		"feedback_only": true,
		"presentation": "ring_pulse",
		"is_square": false,
	}
	_active = true
	_time_left = PULSE_DURATION
	visible = true
	set_process(true)
	if _label:
		_label.text = "✦ Helper Pulse  ·  feedback only"
	if _pattern_label:
		_pattern_label.text = "pattern: soft ring · no mint · pulse #%d" % _pulse_count
	_apply_reduced_motion_visual()
	pulse_fired.emit(payload)
	print("[CozyHelperPulse] fire non_durable=%s id=%d reason=%s shape=ring" % [
		str(payload["non_durable"]), _pulse_count, reason
	])
	return payload


func _apply_reduced_motion_visual() -> void:
	var reduced := false
	var a11y := _get_a11y()
	if a11y != null:
		reduced = bool(a11y.get("reduced_motion")) if "reduced_motion" in a11y else false
		if a11y.has_method("get_snapshot"):
			var snap: Dictionary = a11y.call("get_snapshot") as Dictionary
			reduced = bool(snap.get("reduced_motion", reduced))
	if _ring:
		_ring.modulate = Color(1, 1, 1, 0.5 if reduced else 0.9)
	if reduced:
		_time_left = minf(_time_left, 0.35)


func _get_a11y() -> Node:
	if not is_inside_tree():
		return null
	var r := get_tree().root
	var n := r.get_node_or_null("ControlAccessibilitySettings")
	if n != null:
		return n
	for c in r.get_children():
		if str(c.name) == "ControlAccessibilitySettings":
			return c
	return null


func _process(delta: float) -> void:
	if not _active:
		set_process(false)
		return
	_time_left -= delta
	var t := 1.0 - clampf(_time_left / PULSE_DURATION, 0.0, 1.0)
	if _ring:
		# Expanding ring + fade — pattern motion, not color-only cue.
		var s := 0.55 + t * 1.55
		_ring.scale = Vector2(s, s)
		_ring.modulate.a = 0.75 * (1.0 - t)
	if _time_left <= 0.0:
		_active = false
		visible = false
		set_process(false)
		pulse_finished.emit()


func _build_ui() -> void:
	if _overlay != null and is_instance_valid(_overlay):
		return
	_overlay = Control.new()
	_overlay.name = "Root"
	_overlay.set_anchors_preset(Control.PRESET_FULL_RECT)
	_overlay.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_overlay)

	# Annular ring texture (not a solid ColorRect square) — H1-HUMAN-UX-01.
	_ring = TextureRect.new()
	_ring.name = "PulseRing"
	_ring.texture = _make_ring_texture(int(RING_DIAMETER))
	_ring.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_ring.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_ring.custom_minimum_size = Vector2(RING_DIAMETER, RING_DIAMETER)
	_ring.set_anchors_preset(Control.PRESET_CENTER)
	_ring.anchor_left = 0.5
	_ring.anchor_right = 0.5
	_ring.anchor_top = 0.5
	_ring.anchor_bottom = 0.5
	var half := RING_DIAMETER * 0.5
	_ring.offset_left = -half
	_ring.offset_right = half
	_ring.offset_top = -half
	_ring.offset_bottom = half
	_ring.pivot_offset = Vector2(half, half)
	_ring.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_overlay.add_child(_ring)

	var vbox := VBoxContainer.new()
	vbox.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	vbox.anchor_left = 0.5
	vbox.anchor_right = 0.5
	vbox.anchor_top = 1.0
	vbox.anchor_bottom = 1.0
	vbox.offset_left = -180
	vbox.offset_right = 180
	vbox.offset_top = -160
	vbox.offset_bottom = -100
	vbox.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_overlay.add_child(vbox)

	_label = Label.new()
	_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_label.add_theme_font_size_override("font_size", 14)
	_label.add_theme_color_override("font_color", Color("FFF8E7"))
	_label.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.8))
	_label.add_theme_constant_override("outline_size", 3)
	_label.text = "✦ Helper Pulse"
	vbox.add_child(_label)

	_pattern_label = Label.new()
	_pattern_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_pattern_label.add_theme_font_size_override("font_size", 11)
	_pattern_label.add_theme_color_override("font_color", Color(0.9, 0.92, 0.95))
	_pattern_label.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.75))
	_pattern_label.add_theme_constant_override("outline_size", 2)
	_pattern_label.text = "pattern: soft ring · no mint"
	vbox.add_child(_pattern_label)


func _make_ring_texture(diameter: int) -> Texture2D:
	## Procedural soft rings — circular presentation, not a filled square.
	var s: int = maxi(diameter, 32)
	var img := Image.create(s, s, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))
	var c := Vector2((s - 1) * 0.5, (s - 1) * 0.5)
	var outer_r := s * 0.42
	var outer_w := s * 0.035
	var mid_r := s * 0.26
	var mid_w := s * 0.025
	var core_r := s * 0.06
	for y in range(s):
		for x in range(s):
			var d := Vector2(float(x), float(y)).distance_to(c)
			var col := Color(0, 0, 0, 0)
			if absf(d - outer_r) <= outer_w:
				var a := 1.0 - clampf(absf(d - outer_r) / outer_w, 0.0, 1.0)
				col = Color(0.45, 0.88, 1.0, 0.85 * a)
			elif absf(d - mid_r) <= mid_w:
				var a2 := 1.0 - clampf(absf(d - mid_r) / mid_w, 0.0, 1.0)
				col = Color(0.5, 0.9, 1.0, 0.45 * a2)
			elif d <= core_r:
				var a3 := 1.0 - (d / maxf(core_r, 0.001))
				col = Color(0.7, 0.95, 1.0, 0.28 * a3)
			if col.a > 0.01:
				img.set_pixel(x, y, col)
	return ImageTexture.create_from_image(img)


func get_safety_snapshot() -> Dictionary:
	return {
		"active": _active,
		"pulse_count": _pulse_count,
		"non_durable": true,
		"mints_inventory": false,
		"mints_ownership": false,
		"mints_currency": false,
		"direct_durable": false,
		"presentation": "ring_pulse",
		"is_square": false,
	}


func get_presentation_audit() -> Dictionary:
	## Headless assertion surface for H1-HUMAN-UX-01.
	if _overlay == null or _ring == null:
		_build_ui()
	var has_ring := _ring != null and is_instance_valid(_ring)
	var class_name_str := _ring.get_class() if has_ring else ""
	var uses_color_rect := class_name_str == "ColorRect"
	return {
		"is_square": false,
		"uses_color_rect_square": uses_color_rect,
		"presentation": "ring_pulse",
		"ring_node": str(_ring.name) if has_ring else "",
		"ring_class": class_name_str,
		"ring_is_texture_rect": class_name_str == "TextureRect",
		"pass_non_square": has_ring and not uses_color_rect,
	}
