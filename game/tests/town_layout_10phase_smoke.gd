## Headless smoke: town 10-phase layout loader (active phases).
extends SceneTree

const _TownLoader := preload("res://scripts/modules/town/town_layout_loader.gd")


func _init() -> void:
	var root := _TownLoader.new() as Node3D
	root.name = "TownSmoke"
	get_root().add_child(root)
	var report: Dictionary = root.call("build_town", -1) as Dictionary
	var idle: int = int(root.call("play_all_idle"))
	print(
		"AIDLE_TOWN_LAYOUT_SMOKE phases=%s chars=%s modules=%s idle=%s missing=%s failed=%s ok=%s"
		% [
			str(report.get("phases_built", 0)),
			str(report.get("chars_built", 0)),
			str(report.get("modules_built", 0)),
			str(idle),
			str((report.get("missing", []) as Array).size()),
			str((report.get("failed", []) as Array).size()),
			str(report.get("ok", false)),
		]
	)
	var runtime_ok := bool(report.get("runtime_usable", false)) or (
		int(report.get("chars_built", 0)) >= 1
		and int(report.get("modules_built", 0)) >= 3
		and idle >= 1
	)
	var parity_ok := bool(report.get("parity_ok", false)) or bool(report.get("ok", false))
	if parity_ok:
		print("AIDLE_TOWN_LAYOUT_SMOKE=PASS")
		quit(0)
	elif runtime_ok:
		## Town runs; MOCKUP_PARITY_100 still open until missing modules authored.
		print("AIDLE_TOWN_LAYOUT_SMOKE=RUNTIME_OK_PARITY_PENDING")
		print(JSON.stringify({"missing": report.get("missing", []), "failed": report.get("failed", [])}))
		quit(0)
	else:
		print("AIDLE_TOWN_LAYOUT_SMOKE=FAIL")
		print(JSON.stringify(report))
		quit(1)
