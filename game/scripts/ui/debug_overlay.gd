## F3 toggles via GameManager / SettingsManager.
extends CanvasLayer

@onready var label: Label = $Panel/Margin/Label


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	visible = SettingsManager.is_debug_overlay_enabled()
	EventBus.debug_toggled.connect(_on_debug_toggled)
	EventBus.settings_changed.connect(_on_settings)


func _process(_delta: float) -> void:
	if not visible:
		return
	var snap: Dictionary = GameManager.get_debug_snapshot()
	var modules: PackedStringArray = snap.get("modules", PackedStringArray())
	var lines: PackedStringArray = PackedStringArray([
		"AIdle Openworld – Debug",
		"Core: %s | FPS: %s" % [snap.get("core_version", "?"), snap.get("fps", 0)],
		"State: %s | Space: %s" % [snap.get("state", "?"), snap.get("space", "?")],
		"Art Style: %s" % snap.get("art_style", "?"),
		"Modules: %s" % (", ".join(modules) if modules.size() else "(none)"),
		"Voxel mount empty: %s" % ModuleRegistry.is_mount_empty(AIdleConstants.MODULE_VOXEL),
		"Companion mount empty: %s" % ModuleRegistry.is_mount_empty(AIdleConstants.MODULE_COMPANION),
		"Provenance recent: %d" % ProvenanceLogger.get_recent(5).size(),
		"",
		"WASD move | Shift sprint | Q/R orbit | Wheel zoom",
		"Esc pause | F3 debug",
	])
	label.text = "\n".join(lines)


func _on_debug_toggled(is_visible: bool) -> void:
	visible = is_visible


func _on_settings(section: String, key: String, value: Variant) -> void:
	if section == SettingsManager.SECTION_DEBUG and key == "show_overlay":
		visible = bool(value)
