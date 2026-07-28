## Headless smoke — WO-TOWN-GRID-IMPORT-001 / Directive 99.
## Validates 50 plots load, coords within ±12, honest placeholders, no crash.
extends SceneTree

const _TownGridLoader := preload("res://scripts/modules/town/town_grid_loader.gd")
const PLAN_PATH := "res://resources/town/town_grid_plan_v1.json"


func _init() -> void:
	# Round-trip resource exists
	if not FileAccess.file_exists(PLAN_PATH):
		print("AIDLE_TOWN_GRID_IMPORT_SMOKE=FAIL plan_missing")
		quit(1)
		return
	var f := FileAccess.open(PLAN_PATH, FileAccess.READ)
	var plan: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if not (plan is Dictionary) or int((plan as Dictionary).get("plots", []).size()) != 50:
		print("AIDLE_TOWN_GRID_IMPORT_SMOKE=FAIL plan_plots_not_50")
		quit(1)
		return

	var root := _TownGridLoader.new() as Node3D
	root.name = "TownGridSmoke"
	get_root().add_child(root)
	var report: Dictionary = root.call("build_cadastre") as Dictionary
	var total := int(report.get("plots_total", 0))
	var real_glb := int(report.get("real_glb", 0))
	var placeholders := int(report.get("placeholders", 0))
	var coords_ok := bool(report.get("coords_within_pm12", false))
	var max_abs := float(report.get("max_abs_xz", 99.0))
	print(
		"AIDLE_TOWN_GRID_IMPORT_SMOKE plots=%s real_glb=%s placeholders=%s cast=%s idle=%s max_abs=%.2f coords_ok=%s"
		% [
			total,
			real_glb,
			placeholders,
			str(report.get("cast_built", 0)),
			str(report.get("idle_play", 0)),
			max_abs,
			coords_ok,
		]
	)
	# Cadastre import success: all 50 plots present + in bounds. Placeholders expected.
	var pass_ok := (
		total == 50
		and coords_ok
		and max_abs <= 12.0
		and (real_glb + placeholders) == 50
		and bool(report.get("ok", false))
	)
	if pass_ok:
		print("AIDLE_TOWN_GRID_IMPORT_SMOKE=PASS")
		print(
			"AIDLE_TOWN_GRID_HONESTY real_glb=%s placeholders=%s (concept not authored is expected)"
			% [real_glb, placeholders]
		)
		quit(0)
	else:
		print("AIDLE_TOWN_GRID_IMPORT_SMOKE=FAIL")
		print(JSON.stringify(report))
		quit(1)
