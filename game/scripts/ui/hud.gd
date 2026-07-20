extends CanvasLayer

@onready var art_label: Label = $Root/TopBar/ArtStyleLabel
@onready var space_label: Label = $Root/TopBar/SpaceLabel
@onready var hint_label: Label = $Root/HintLabel


func _ready() -> void:
	_refresh()
	EventBus.art_style_changed.connect(func(_s): _refresh())
	EventBus.player_entered_space.connect(func(space_id, _inst, _p): space_label.text = "Space: %s" % space_id)


func _refresh() -> void:
	var style := ArtStyleManager.get_active_style()
	art_label.text = "Art: %s" % str(style.get("display_name", ArtStyleManager.get_active_style_id()))
	space_label.text = "Space: %s" % GameManager.current_space_id
	hint_label.text = "Esc Pause · F3 Debug · WASD Move · Q/R Camera"
