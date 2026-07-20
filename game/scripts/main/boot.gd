## Boot: edition gate → art style → main.
## Headless / CI smoke auto-picks defaults without persisting first-run choices.
extends Control


func _ready() -> void:
	GameManager.notify_booted()
	# Small delay so autoloads finish first-frame setup.
	await get_tree().process_frame

	# ── G2-007: AGM edition must be chosen before world entry ───────────────
	if not SettingsManager.has_chosen_edition():
		if _is_headless_smoke():
			# Ephemeral default — leave interactive first-run intact on user://.
			SettingsManager.set_edition(AIdleConstants.DEFAULT_EDITION, false, false)
			print("[Boot] Headless smoke → default AGM edition (not persisted).")
		else:
			get_tree().change_scene_to_file("res://scenes/ui/edition_select.tscn")
			return
	print(
		"[Boot] AGM edition=%s same_contracts=%s no_client_secrets=%s"
		% [
			SettingsManager.get_edition(),
			SettingsManager.uses_same_agm_contracts(),
			SettingsManager.has_no_client_secrets(),
		]
	)

	if ArtStyleManager.has_chosen_style():
		get_tree().change_scene_to_file("res://scenes/main/main.tscn")
		return
	if _is_headless_smoke():
		# Do not persist headless default into user:// (leave first interactive pick intact).
		ArtStyleManager.set_active_style(AIdleConstants.DEFAULT_ART_STYLE, false)
		print("[Boot] Headless smoke → main with default art style.")
		get_tree().change_scene_to_file("res://scenes/main/main.tscn")
		return
	get_tree().change_scene_to_file("res://scenes/ui/art_style_select.tscn")


func _is_headless_smoke() -> bool:
	if DisplayServer.get_name() == "headless":
		return true
	if OS.has_feature("headless"):
		return true
	# Godot CLI often passes --headless before project args.
	for arg in OS.get_cmdline_user_args():
		if arg == "--headless" or arg == "--quit-after":
			return true
	for arg in OS.get_cmdline_args():
		if arg == "--headless":
			return true
	return false
