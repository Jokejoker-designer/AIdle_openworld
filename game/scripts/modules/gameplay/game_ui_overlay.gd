## Cozy gameplay HUD overlay — mounts into the existing UI tree next to HUD /
## cozy_homestead_panel / playable_action_bar. Follows the existing panel
## conventions (read-only snapshot API, toggle open/close, responsive layout).
##
## Shows: resource HUD (coin/wood/stone/food/spirit), day/time/weather strip,
## active quest tracker, relationship meter, and a small quest log panel.
## All data comes from the gameplay subsystem snapshots (never reads game
## state ad-hoc).
class_name GameUiOverlay
extends Control

const FONT_NORMAL := "res://fonts/DejaVuSans.ttf"

var _economy: RefCounted = null
var _quests: RefCounted = null
var _meter: RefCounted = null
var _weather: Node = null
var _npc: RefCounted = null
var _visible: bool = false

var _vbox: VBoxContainer = null
var _resource_bar: HBoxContainer = null
var _day_strip: Label = null
var _quest_strip: Label = null
var _relationship_strip: Label = null
var _mood_strip: Label = null

func configure(economy: RefCounted, quests: RefCounted, meter: RefCounted, weather: Node, npc: RefCounted) -> void:
	_economy = economy
	_quests = quests
	_meter = meter
	_weather = weather
	_npc = npc

func _ready() -> void:
	name = "GameUiOverlay"
	anchor_left = 0.0
	anchor_right = 1.0
	anchor_top = 0.0
	anchor_bottom = 0.0
	visible = false
	set_process(true)

func toggle_ui(enabled: bool) -> void:
	_visible = bool(enabled)
	visible = _visible
	if _visible and _vbox == null:
		_build_ui()

func _build_ui() -> void:
	if _vbox != null:
		return
	_vbox = VBoxContainer.new()
	_vbox.name = "GameHudVBox"
	_vbox.set_anchors_preset(Control.PRESET_TOP_WIDE)
	_vbox.add_theme_constant_override("separation", 4)
	add_child(_vbox)
	_resource_bar = HBoxContainer.new()
	_day_strip = Label.new()
	_quest_strip = Label.new()
	_relationship_strip = Label.new()
	_mood_strip = Label.new()
	for c in [_day_strip, _quest_strip, _relationship_strip, _mood_strip, _resource_bar]:
		_vbox.add_child(c)
	_apply_style()

func _apply_style() -> void:
	var color := Color(1.0, 0.95, 0.85, 0.92)
	for c in _vbox.get_children():
		if c is Label:
			(c as Label).add_theme_color_override("font_color", color)

func _process(_delta: float) -> void:
	if not _visible or _vbox == null:
		return
	_refresh()

func _refresh() -> void:
	if _economy != null:
		var snap: Dictionary = _economy.call("snapshot")
		var b: Dictionary = snap.get("balance", {})
		for child in _resource_bar.get_children():
			_resource_bar.remove_child(child)
			child.queue_free()
		for res in ["coin", "wood", "stone", "food", "spirit"]:
			var lbl := Label.new()
			lbl.text = "%s:%s" % [res, str(b.get(res, 0))]
			_resource_bar.add_child(lbl)
		_day_strip.text = "Ngày %d · %s · %s (%.0fh)" % [int(snap.get("day", 1)), str(snap.get("time_of_day", "")), _weather_label(), float(snap.get("hour", 6.0))]
	if _quests != null:
		var qs: Dictionary = _quests.call("snapshot")
		var active: Array = qs.get("quests", [])
		if active.is_empty():
			_quest_strip.text = "Không có nhiệm vụ đang thực hiện — nói chuyện với NPC hoặc Companion để nhận việc mới."
		else:
			var rec: Dictionary = active[0]
			_quest_strip.text = "Nhiệm vụ: %s — %s" % [str(rec.get("title", "")), str(rec.get("objective_summary", ""))]
	if _meter != null:
		var ms: Dictionary = _meter.call("snapshot")
		_relationship_strip.text = "Quan hệ: %s (lv.%d, %d điểm)" % [str(ms.get("level_name", "")), int(ms.get("level", 0)), int(ms.get("points", 0))]
		_mood_strip.text = "Tâm trạng Companion: %s" % str(ms.get("mood", "calm"))

func _weather_label() -> String:
	if _weather != null and _weather.has_method("get_weather"):
		return str(_weather.call("get_weather"))
	return "clear"
