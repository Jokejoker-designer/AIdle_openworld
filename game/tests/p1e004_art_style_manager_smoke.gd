## WO-P1E-004 W1a — ArtStyleManager clean-log proof (BEFORE DNA work).
## Proves get_active_style never throws SCRIPT ERROR on cozy_cyber_pixel path.
## Instantiates the autoload script as a Node (headless -s has no autoload globals).
## Run:
##   tools/Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://tests/p1e004_art_style_manager_smoke.gd
extends SceneTree

const ASM_SCRIPT := "res://autoload/art_style_manager.gd"
const DEFAULT_ID := "cozy_cyber_pixel"

var _failed: int = 0
var _passed: int = 0


func _initialize() -> void:
	print("[P1E-004 ASM smoke] start")
	var scr: Script = load(ASM_SCRIPT) as Script
	if scr == null:
		_fail("load_asm_script")
		_finish()
		return
	var asm: Node = scr.new() as Node
	if asm == null:
		_fail("instantiate_asm")
		_finish()
		return
	root.add_child(asm)

	# --- Crash window: empty _styles + active = cozy_cyber_pixel (DEFAULT) ---
	# Previously: _styles.get(id, _styles[DEFAULT]) eagerly indexed empty dict → SCRIPT ERROR
	asm.set("_styles", {})
	asm.set("_active_style_id", DEFAULT_ID)
	var style: Dictionary = asm.call("get_active_style") as Dictionary
	if style.is_empty():
		_fail("empty_style_after_get")
	elif str(style.get("id", "")) != DEFAULT_ID:
		_fail("wrong_style_id", str(style.get("id", "")))
	else:
		_ok("get_active_style_before_ready")

	# Builtins must now contain cozy_cyber_pixel (real entry, not missing)
	var styles_dict: Dictionary = asm.get("_styles") as Dictionary
	if not styles_dict.has(DEFAULT_ID):
		_fail("builtin_missing_cozy")
	else:
		_ok("builtin_cozy_present")

	# set_active + query path
	var set_ok: bool = bool(asm.call("set_active_style", DEFAULT_ID, false))
	if not set_ok:
		_fail("set_active_style")
	else:
		_ok("set_active_style")

	var s2: Dictionary = asm.call("get_active_style") as Dictionary
	if str(s2.get("id", "")) != DEFAULT_ID:
		_fail("active_cozy", str(s2.get("id", "")))
	else:
		_ok("active_cozy_cyber_pixel")

	var s3: Dictionary = asm.call("query_art_style_for_generation") as Dictionary
	if s3.is_empty() or not s3.has("palette"):
		_fail("query_empty")
	else:
		_ok("query_art_style_for_generation")

	# Second empty-dict call after clear — still must not throw
	asm.set("_styles", {})
	var s4: Dictionary = asm.call("get_active_style") as Dictionary
	if str(s4.get("id", "")) != DEFAULT_ID:
		_fail("second_empty_call", str(s4.get("id", "")))
	else:
		_ok("idempotent_register_on_get")

	asm.queue_free()
	_finish()


func _ok(name: String) -> void:
	_passed += 1
	print("  OK  %s" % name)


func _fail(name: String, detail: String = "") -> void:
	_failed += 1
	if detail.is_empty():
		print("  FAIL %s" % name)
	else:
		print("  FAIL %s | %s" % [name, detail])


func _finish() -> void:
	if _failed == 0:
		print("AIDLE_P1E004_ASM_SMOKE=PASS checks=%d" % _passed)
		print("SCRIPT_ERROR_ART_STYLE=0")
	else:
		print("AIDLE_P1E004_ASM_SMOKE=FAIL failed=%d passed=%d" % [_failed, _passed])
	quit(0 if _failed == 0 else 1)
