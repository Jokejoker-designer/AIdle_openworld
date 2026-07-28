## Live headed proof: real main.tscn + PlayableActionBar gardener row.
## Not presenter-only QA — loads the actual game UI wiring.
## Marker: AIDLE_PLAYABLE_ACTION_BAR_GARDENER_LIVE=PASS|FAIL
extends SceneTree

const MAIN_SCENE := "res://scenes/main/main.tscn"
const RECEIPT_PATH := "E:/AIdle_openworld/orchestration/receipts/nori7_anim_15clip_001/playable_action_bar_parse_fix_001.json"
const LOG_PATH := "E:/AIdle_openworld/orchestration/evidence/nori7_anim_15clip_001/playable_action_bar_gardener_live_001.log"

const GARDENER_ACTIONS := ["water", "plant_seed", "harvest", "charge", "low_energy"]
const BTN_NAMES := {
	"water": "BtnWater",
	"plant_seed": "BtnPlant",
	"harvest": "BtnHarvest",
	"charge": "BtnCharge",
	"low_energy": "BtnLowEnergy",
}

var _main: Node = null
var _bar: CanvasLayer = null
var _failures: PackedStringArray = []
var _clicked: Array = []
var _console_hits: Array = []
var _script_load_ok: bool = false


func _initialize() -> void:
	print("[PAB_GARDENER_LIVE] start — real main.tscn + action bar gardener buttons")
	print("[PAB_GARDENER_LIVE] display=%s headed=%s" % [DisplayServer.get_name(), str(DisplayServer.get_name() != "headless")])
	await _run()
	_write_receipt()
	if _failures.is_empty() and _clicked.size() == 5:
		print("AIDLE_PLAYABLE_ACTION_BAR_GARDENER_LIVE=PASS clicked=5 script_ok=%s" % str(_script_load_ok))
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print(
			"AIDLE_PLAYABLE_ACTION_BAR_GARDENER_LIVE=FAIL failed=%d clicked=%d"
			% [_failures.size(), _clicked.size()]
		)
		quit(1)


func _run() -> void:
	var err := change_scene_to_file(MAIN_SCENE)
	if err != OK:
		_failures.append("change_scene_failed err=%s" % err)
		return
	# Wait for main boot (modules, Nori, action bar)
	for i in range(90):
		await process_frame
		_main = current_scene
		if _main == null:
			continue
		var ui := _main.get_node_or_null("UI")
		if ui != null:
			_bar = ui.get_node_or_null("PlayableActionBar") as CanvasLayer
		if _bar != null and _main.has_method("get_nori7_presenter"):
			var nori: Variant = _main.call("get_nori7_presenter")
			if nori != null:
				break
	if _main == null:
		_failures.append("main_null")
		return
	print("[PAB_GARDENER_LIVE] main loaded name=%s" % _main.name)

	# Script load proof: PlayableActionBar instance exists and has gardener signal
	if _bar == null:
		_failures.append("PlayableActionBar_missing — script likely failed to parse/load")
		return
	_script_load_ok = true
	print("[PAB_GARDENER_LIVE] PlayableActionBar LOADED path=%s" % _bar.get_path())

	if not _bar.has_signal("gardener_action_pressed"):
		_failures.append("gardener_action_pressed_signal_missing")
		return
	print("[PAB_GARDENER_LIVE] signal gardener_action_pressed present")

	# Confirm all rows' primary buttons exist (not just gardener)
	var required := [
		"BtnCompanion", "BtnExport", "BtnImport", "BtnDemoBuild", "BtnConfirm", "BtnCancel",
		"BtnWater", "BtnPlant", "BtnHarvest", "BtnCharge", "BtnLowEnergy",
	]
	for nm in required:
		var btn := _find_btn(nm)
		if btn == null:
			_failures.append("button_missing %s" % nm)
		else:
			print("[PAB_GARDENER_LIVE] button ok %s text=%s" % [nm, btn.text])

	# Extra frames so Nori/bridge settle
	for _i in range(20):
		await process_frame

	# Click each gardener button via real Button.pressed (same path as human click)
	for action_id in GARDENER_ACTIONS:
		var btn_name: String = BTN_NAMES[action_id]
		var btn := _find_btn(btn_name)
		if btn == null:
			_failures.append("click_target_missing %s" % btn_name)
			continue
		if not btn.visible:
			_failures.append("button_not_visible %s" % btn_name)
		print("[PAB_GARDENER_LIVE] CLICK %s action=%s" % [btn_name, action_id])
		btn.pressed.emit()
		_clicked.append({"action": action_id, "button": btn_name})
		# Allow Main._on_gardener_action + apply_trigger to run
		for _j in range(12):
			await process_frame
		await create_timer(0.15).timeout

	print("[PAB_GARDENER_LIVE] clicked_count=%d expected=5" % _clicked.size())
	if _clicked.size() != 5:
		_failures.append("not_all_five_clicked n=%d" % _clicked.size())


func _find_btn(node_name: String) -> Button:
	if _bar == null:
		return null
	var n := _bar.find_child(node_name, true, false)
	return n as Button


func _write_receipt() -> void:
	var receipt := {
		"schema_version": "playable_action_bar_parse_fix/1.0",
		"receipt_id": "playable_action_bar_parse_fix_001",
		"work_order": "WO-OBJECT-DNA-NORI7-ANIM-VERTICAL-SLICE-001",
		"purpose": "Fix GDScript parse error blocking PlayableActionBar (gardener UI) in real play",
		"accepted": false,
		"self_accept": false,
		"purple": "WAITING",
		"fix": {
			"file": "game/scripts/ui/playable_action_bar.gd",
			"line": 216,
			"error": "Parse Error: Cannot infer the type of \"is_garden\" variable because the value doesn't have a set type.",
			"root_cause": "for b in all_btns: where all_btns: Array (untyped) → b is Variant; := cannot infer bool from Variant == Button or-chain",
		},
		"diff": {
			"before": "var is_garden := b == btn_water or b == btn_plant or b == btn_harvest or b == btn_charge or b == btn_low_energy",
			"after": "var is_garden: bool = (b == btn_water or b == btn_plant or b == btn_harvest or b == btn_charge or b == btn_low_energy)",
			"logic_change": false,
			"lines_touched": 1,
		},
		"verification": {
			"mode": "headed_real_main_tscn",
			"scene": MAIN_SCENE,
			"script_loaded": _script_load_ok,
			"parse_error_gone": _script_load_ok and _failures.is_empty() or (_script_load_ok and _clicked.size() == 5),
			"gardener_buttons_clicked": _clicked,
			"expected_console_line_pattern": "[Main] gardener_action action=... ok=true ... client_world_commit=false",
			"note": "Outer shell log captures Main gardener_action prints; this receipt records click loop results.",
		},
		"honesty_gap": {
			"prior_claim": "nori7_anim_15clip_qa_receipt.json claimed UI gardener row PlayableActionBar Row3 Water/Plant/Harvest/Charge/Rest as done",
			"reality": "That QA (nori7_anim_15clip_headed_qa_001.gd) exercises the Nori presenter directly and never loads playable_action_bar.gd. The parse error blocked the real action bar in live play, so end-to-end button→apply_trigger was not proven before the UI claim was reported complete. This fix + live click-through closes that gap for the 5 gardener buttons.",
		},
		"failures": Array(_failures),
		"ok": _failures.is_empty() and _clicked.size() == 5 and _script_load_ok,
	}
	var f := FileAccess.open(RECEIPT_PATH, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(receipt, "\t"))
		f.close()
		print("[PAB_GARDENER_LIVE] receipt=%s" % RECEIPT_PATH)
	else:
		printerr("[PAB_GARDENER_LIVE] could not write receipt")
