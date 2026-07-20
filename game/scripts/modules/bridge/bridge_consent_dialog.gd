## Minimal visible consent dialog for Free Desktop Bridge decision import (G2-005).
## Player must explicitly Accept or Reject — no auto-apply.
extends CanvasLayer

signal consent_accepted
signal consent_rejected

var _bridge: Node
var _summary: String = ""

@onready var _title: Label = $Center/Panel/VBox/Title
@onready var _body: Label = $Center/Panel/VBox/Body
@onready var _detail: Label = $Center/Panel/VBox/Detail
@onready var _accept_btn: Button = $Center/Panel/VBox/Buttons/Accept
@onready var _reject_btn: Button = $Center/Panel/VBox/Buttons/Reject


func _ready() -> void:
	layer = 60
	process_mode = Node.PROCESS_MODE_ALWAYS
	visible = false
	if _accept_btn:
		_accept_btn.pressed.connect(_on_accept)
	if _reject_btn:
		_reject_btn.pressed.connect(_on_reject)


func bind(bridge: Node, decision: Dictionary, summary: String) -> void:
	_bridge = bridge
	_summary = summary
	if _title:
		_title.text = "Import AGM Decision?"
	if _body:
		_body.text = (
			"A Decision Envelope arrived via Desktop Bridge (clipboard/file).\n"
			+ "Nothing is applied until you confirm.\n"
			+ "Build proposals still require preview → confirm → World Commit."
		)
	if _detail:
		_detail.text = summary if not summary.is_empty() else str(decision.get("decision_id", ""))


func open_dialog() -> void:
	visible = true
	if _accept_btn:
		_accept_btn.grab_focus()


func _on_accept() -> void:
	consent_accepted.emit()
	if _bridge and _bridge.has_method("confirm_pending_decision"):
		_bridge.call("confirm_pending_decision")
	visible = false


func _on_reject() -> void:
	consent_rejected.emit()
	if _bridge and _bridge.has_method("reject_pending_decision"):
		_bridge.call("reject_pending_decision", "player_rejected")
	visible = false
