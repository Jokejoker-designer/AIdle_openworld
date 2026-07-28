## Town cadastre loader — WO-TOWN-GRID-IMPORT-001 / Directive 99 Tier-1.
## Places all named plots from town_grid_plan_v1.json:
##  - footprint outline + plot name label
##  - real GLB when production asset exists
##  - honest "concept — not yet authored" placeholder otherwise
## Presentation only; never World-Commits. Does not edit town_layout_10phase.json.
extends Node3D

const _CastPresenter := preload("res://scripts/modules/ucbv_001/cast_presenter.gd")
const _NpcTownRoamer := preload("res://scripts/modules/ucbv_001/npc_town_roamer.gd")
const _GlbIntake = preload("res://scripts/modules/asset/glb_intake.gd")

const PLAN_PATH := "res://resources/town/town_grid_plan_v1.json"
const CAST_ROSTER := "res://resources/ucbv_001/cast/cast_roster.json"
const MODULE_CATALOG := "res://resources/p1e_cozy/module_catalog.json"

## Design-id → catalog id when production still uses preview/anchor names.
## Prefer real cozy_greenhouse_A when present in catalog; alias is fallback only.
const MODULE_ALIASES := {
	"cozy_greenhouse_A": "cozy_greenhouse_A",
}

var _last_report: Dictionary = {}
var _plot_nodes: Array = []


func get_report() -> Dictionary:
	return _last_report.duplicate(true)


func build_cadastre() -> Dictionary:
	_clear()
	var plan: Variant = _load_json(PLAN_PATH)
	if plan == null or not (plan is Dictionary):
		_last_report = {"ok": false, "error": "plan_missing", "path": PLAN_PATH}
		print("AIDLE_TOWN_GRID_IMPORT=FAIL plan_missing")
		return _last_report

	var plots: Array = plan.get("plots", []) as Array
	var cell_size := 2.0
	var grid: Dictionary = plan.get("grid", {}) as Dictionary
	if grid.has("cell_size_units"):
		cell_size = float(grid.get("cell_size_units", 2.0))

	var cast_by_id: Dictionary = _index_cast()
	var mod_by_id: Dictionary = _index_modules()
	var intake: RefCounted = _GlbIntake.new()

	var total := 0
	var real_glb := 0
	var placeholders := 0
	var cast_built := 0
	var idle_play := 0
	var missing: Array = []
	var failed: Array = []
	var coords_ok := true
	var max_abs := 0.0

	for p in plots:
		if not (p is Dictionary):
			continue
		total += 1
		var plot_id := str(p.get("plot_id", "PLOT_%d" % total))
		var role := str(p.get("role", "prop"))
		var object_id := str(p.get("object_id", ""))
		var xf: Dictionary = p.get("transform", {}) as Dictionary
		var x := float(xf.get("x", 0.0))
		var y := float(xf.get("y", 0.0))
		var z := float(xf.get("z", 0.0))
		var rot := float(xf.get("rotation_deg", 0.0))
		var sc := float(xf.get("scale", 1.0))
		max_abs = maxf(max_abs, maxf(absf(x), absf(z)))
		if absf(x) > 12.0 or absf(z) > 12.0:
			coords_ok = false
			failed.append({"plot_id": plot_id, "error": "outside_pm12", "x": x, "z": z})

		## TOWN_ALIGNMENT_V1: root stays axis-aligned (neat pads/labels).
		## Plan yaw applies only to content (module/char) — no remesh, plan transform SSOT.
		var root := Node3D.new()
		root.name = "Plot_%s" % plot_id.replace(".", "_")
		root.position = Vector3(x, y, z)
		root.rotation_degrees = Vector3(0.0, 0.0, 0.0)
		add_child(root)
		_plot_nodes.append(root)

		var content := Node3D.new()
		content.name = "Content"
		content.rotation_degrees = Vector3(0.0, rot, 0.0)
		root.add_child(content)

		var fp: Array = p.get("footprint_units", [cell_size, cell_size]) as Array
		var fpx := float(fp[0]) if fp.size() > 0 else cell_size
		var fpz := float(fp[1]) if fp.size() > 1 else cell_size
		if role == "character_spawn":
			fpx = minf(fpx, 1.2)
			fpz = minf(fpz, 1.2)
		elif role == "prop" and fpx > 3.0:
			fpx = 2.0
			fpz = 2.0

		## Axis-aligned pad under content for "đều và ngay ngắn" grid read
		_add_footprint(root, fpx, fpz, role)
		var label_text := "%s\n%s" % [plot_id, object_id]
		_add_label(root, label_text, role)

		var placed := false
		if role == "character_spawn":
			var cres: Dictionary = _try_place_character(content, object_id, cast_by_id, sc)
			if bool(cres.get("ok", false)):
				cast_built += 1
				real_glb += 1
				placed = true
				if bool(cres.get("idle", false)):
					idle_play += 1
			else:
				missing.append({"plot_id": plot_id, "object_id": object_id, "role": role, "reason": cres.get("error", "no_cast")})
		else:
			var mres: Dictionary = _try_place_module(content, object_id, mod_by_id, intake, sc)
			if bool(mres.get("ok", false)):
				real_glb += 1
				placed = true
			else:
				missing.append({"plot_id": plot_id, "object_id": object_id, "role": role, "reason": mres.get("error", "no_glb")})

		if not placed:
			_add_honest_placeholder(content, plot_id, object_id, role, fpx, fpz)
			placeholders += 1

	var ok := total == 50 and coords_ok and failed.is_empty()
	_last_report = {
		"ok": ok,
		"directive_id": 99,
		"work_order": "WO-TOWN-GRID-IMPORT-001",
		"town_id": str(plan.get("town_id", "")),
		"plots_total": total,
		"real_glb": real_glb,
		"placeholders": placeholders,
		"cast_built": cast_built,
		"idle_play": idle_play,
		"missing": missing,
		"failed": failed,
		"coords_within_pm12": coords_ok,
		"max_abs_xz": max_abs,
		"art_style": "cozy_cyber_pixel",
		"world_profile": str(plan.get("world_profile", "cozy_cyber_pixel")),
		"accepted": false,
		"self_accept": false,
		"honesty": "unauthored plots use labeled concept placeholders; no fake GLB",
	}
	print(
		"[TownGrid] plots=%s real_glb=%s placeholders=%s cast=%s idle=%s max_abs=%.2f ok=%s"
		% [total, real_glb, placeholders, cast_built, idle_play, max_abs, ok]
	)
	if ok:
		print("AIDLE_TOWN_GRID_IMPORT=PASS")
	else:
		print("AIDLE_TOWN_GRID_IMPORT=FAIL")
	return _last_report


func _try_place_character(parent: Node3D, character_id: String, cast_by_id: Dictionary, sc: float) -> Dictionary:
	if not cast_by_id.has(character_id):
		return {"ok": false, "error": "not_in_cast_roster"}
	var row: Dictionary = cast_by_id[character_id]
	var glb := str(row.get("glb", ""))
	var sha := str(row.get("glb_sha256", ""))
	var abs_path := ProjectSettings.globalize_path(glb) if glb.begins_with("res://") else glb
	if glb.is_empty() or not FileAccess.file_exists(abs_path):
		return {"ok": false, "error": "cast_glb_missing"}
	var presenter: Node3D = _CastPresenter.new() as Node3D
	presenter.name = "Char_%s" % character_id.replace("-", "_")
	parent.add_child(presenter)
	## Cadastre readability + mockup scale (chibi ~1 unit height → boost for town view).
	## Default 1.65 keeps pear/robot silhouettes readable. Roster town_scale overrides
	## (Bac Bap 1.0 free-agent, Bui Mo 0.52 cute pet — not house-sized canopy).
	var town_mul := 1.65
	if row.has("town_scale"):
		town_mul = float(row.get("town_scale"))
	if town_mul <= 0.0:
		town_mul = 1.65
	var cast_sc := town_mul * sc
	presenter.scale = Vector3(cast_sc, cast_sc, cast_sc)
	## Prefer full roster row so NPC flags (auto_schedule, schedule_order) apply — Bac Bap V3.
	if presenter.has_method("configure_from_roster_row"):
		presenter.call("configure_from_roster_row", row)
	elif presenter.has_method("configure"):
		presenter.call("configure", character_id, glb, sha)
	var st: Dictionary = presenter.call("build_from_assets") as Dictionary
	if not bool(st.get("built", false)):
		presenter.queue_free()
		return {"ok": false, "error": str(st.get("error", "cast_build_failed"))}
	## Do NOT run prop material boost on cast — it washes multi-surface cream/leaf/cyan
	## into a single white-sphere look (root cause white_sphere_cast_presenter).
	## cast_presenter.gd now rebinds multisurface materials + ground-aligns feet.
	var idle := false
	var auto_sched := bool(st.get("auto_schedule", false))
	var auto_roam := bool(row.get("auto_roam", false)) or character_id == "CCP-NW-003"
	if auto_roam:
		## Town roaming schedule (replaces in-place clip gallery cycle).
		if presenter.has_method("disable_auto_schedule_for_roam"):
			presenter.call("disable_auto_schedule_for_roam")
		var roamer: Node = _NpcTownRoamer.new() as Node
		roamer.name = "NpcTownRoamer"
		presenter.add_child(roamer)
		## Plot content is under cadastre at plan XZ — home = current global.
		var home := presenter.global_position
		var default_profile := "workshop"
		var default_plant := -0.72
		if character_id == "CCP-CT-004" or str(row.get("slug", "")) == "bui_mo":
			default_profile = "garden_cat"
			default_plant = -0.18
		elif character_id == "AC-CO-015" or str(row.get("slug", "")) == "cinder":
			default_profile = "kiln_worker"
			default_plant = -0.55
		elif character_id == "CCP-NW-003":
			default_profile = "workshop"
			default_plant = -0.72
		var roam_opts := {
			"profile": str(row.get("roam_profile", default_profile)),
			"plant_y": float(row.get("plant_y", default_plant)),
			"scale": cast_sc,
			"character_id": character_id,
			"slug": str(row.get("slug", "")),
		}
		if roamer.has_method("setup"):
			roamer.call("setup", presenter, home, roam_opts)
		idle = true
		auto_sched = false
	elif auto_sched:
		idle = true  # schedule starts itself (includes idle)
	elif presenter.has_method("play_clip"):
		idle = bool(presenter.call("play_clip", "idle"))
	return {
		"ok": true,
		"idle": idle,
		"auto_schedule": auto_sched,
		"auto_roam": auto_roam,
		"town_scale": cast_sc,
		"schedule_len": int(st.get("schedule_len", 0)),
		"clip_count": int(st.get("clip_count", 0)),
		"presentation_fix": str(st.get("presentation_fix", "")),
	}


func _try_place_module(
	parent: Node3D, module_id: String, mod_by_id: Dictionary, intake: RefCounted, sc: float
) -> Dictionary:
	var resolved := module_id
	if not mod_by_id.has(resolved) and MODULE_ALIASES.has(module_id):
		resolved = str(MODULE_ALIASES[module_id])
	# Also honor plan import aliases if present in resource
	if not mod_by_id.has(resolved):
		return {"ok": false, "error": "not_in_catalog"}
	var row: Dictionary = mod_by_id[resolved]
	var glb := str(row.get("glb", ""))
	var abs_path := ProjectSettings.globalize_path(glb) if glb.begins_with("res://") else glb
	if not FileAccess.file_exists(abs_path):
		return {"ok": false, "error": "glb_file_missing"}
	var node: Node3D = intake.call("load_glb_absolute", abs_path, module_id) as Node3D
	if node == null:
		return {"ok": false, "error": "intake_failed"}
	node.name = "Mod_%s" % module_id
	if sc != 1.0:
		node.scale = Vector3(sc, sc, sc)
	if module_id == "cozy_house_small_A" or resolved == "cozy_house_small_A":
		node.scale = Vector3(1.15, 1.15, 1.15)
	## Royal Lightkeep full mesh is ~24×19×38 m — town plots pass scale via transform (0.14).
	if (
		module_id == "royal_lightkeep_watchtower_barracks_01"
		or resolved == "royal_lightkeep_watchtower_barracks_01"
	):
		if sc < 0.01:
			node.scale = Vector3(0.14, 0.14, 0.14)
	## Fidelity law: GLB cream/pastels wash under realm lighting — boost readability.
	_boost_mockup_materials(node)
	parent.add_child(node)
	return {"ok": true, "resolved": resolved}


## Saturate / recolor materials so MOCKUP_SSOT palette reads in-game (not pure white).
func _boost_mockup_materials(root: Node) -> void:
	var stack: Array = [root]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is MeshInstance3D:
			var mi := n as MeshInstance3D
			_boost_mi(mi)
		for c in n.get_children():
			stack.append(c)


func _boost_mi(mi: MeshInstance3D) -> void:
	if mi.mesh == null:
		return
	var sc := mi.mesh.get_surface_count()
	for s in range(sc):
		var mat: Material = mi.get_active_material(s)
		if mat == null and mi.mesh is ArrayMesh:
			mat = (mi.mesh as ArrayMesh).surface_get_material(s)
		if mat == null:
			continue
		var sm: StandardMaterial3D = null
		if mat is StandardMaterial3D:
			sm = (mat as StandardMaterial3D).duplicate() as StandardMaterial3D
		else:
			continue
		var nm := str(sm.resource_name).to_lower()
		if nm.is_empty():
			nm = str(mi.name).to_lower()
		var c := sm.albedo_color
		# Near-white cream → warmer readable cream
		if c.r > 0.92 and c.g > 0.88 and c.b > 0.82:
			sm.albedo_color = Color(0.98, 0.86, 0.68, c.a)
		# Soft lilac → stronger lilac pad (skip greens: g-dominant leaves/petals)
		if c.b > c.r and c.b > 0.75 and c.r > 0.55 and c.g < c.b * 0.95 and c.g < 0.72:
			sm.albedo_color = Color(0.72, 0.55, 0.92, c.a)
		# Name-based overrides (Blender MAT_ / M_ prefixes)
		# Preserve peach/yellow/cream fish-scale bands — do NOT collapse all roof tiles to one orange.
		if "roof_a" in nm or nm.ends_with("_a") and "roof" in nm:
			sm.albedo_color = Color(1.0, 0.78, 0.55, c.a)  # soft peach
		elif "roof_b" in nm:
			sm.albedo_color = Color(1.0, 0.90, 0.45, c.a)  # soft yellow
		elif "roof_c" in nm:
			sm.albedo_color = Color(0.99, 0.94, 0.78, c.a)  # soft cream
		elif ("roof" in nm or "tile" in nm) and "ridge" not in nm:
			# keep relative hue: if already peach-tinted stay peach; yellow stays yellow
			if c.g < 0.65:
				sm.albedo_color = Color(1.0, 0.55, 0.28, c.a)
			elif c.b < 0.35 and c.g > 0.75:
				sm.albedo_color = Color(1.0, 0.84, 0.22, c.a)
			elif c.r > 0.85 and c.g > 0.55:
				sm.albedo_color = Color(clampf(c.r, 0.9, 1.0), clampf(c.g, 0.55, 0.90), clampf(c.b, 0.20, 0.55), c.a)
		if "door" in nm and "frame" not in nm:
			sm.albedo_color = Color(0.78, 0.45, 0.22, c.a)
		if "mail" in nm:
			sm.albedo_color = Color(0.68, 0.42, 0.92, c.a)
		if "emit" in nm or "glow" in nm or "lamp" in nm:
			sm.emission_enabled = true
			sm.emission = Color(1.0, 0.78, 0.35)
			sm.emission_energy_multiplier = 2.2
			sm.albedo_color = Color(1.0, 0.85, 0.5, c.a)
		if "wood" in nm or "fence" in nm or "post" in nm and "mail" not in nm:
			if c.r < 0.9:
				sm.albedo_color = Color(0.72, 0.50, 0.32, c.a)
		if "leaf" in nm or "crop" in nm or "plant" in nm or "grass" in nm:
			sm.albedo_color = Color(0.38, 0.72, 0.35, c.a)
		if "lav" in nm or "bloom" in nm or "flower" in nm or "curtain" in nm:
			sm.albedo_color = Color(0.72, 0.42, 0.90, c.a)
		if "pot" in nm:
			sm.albedo_color = Color(0.88, 0.52, 0.32, c.a)
		# BUILDINGS_WAVE1 / V12 palette (do not collapse green roofs / fruit / awnings to peach)
		# Green gazebo petals + scale shells — must win over soft-lilac / near-white rules
		if "roof_g" in nm or "petal_g" in nm or "scale_g" in nm or "green_dome" in nm \
				or ("gazebo" in nm and "roof" in nm) or nm.begins_with("g1") or nm.begins_with("g2") \
				or nm.begins_with("g3") or nm == "g1" or nm == "g2" or nm == "g3":
			sm.albedo_color = Color(0.38, 0.82, 0.48, c.a)
			sm.roughness = 0.55
		if "awn_pink" in nm or nm.begins_with("awn_p") or ("awn" in nm and c.r > 0.85 and c.b > 0.7 and c.g < 0.85):
			sm.albedo_color = Color(0.96, 0.66, 0.78, c.a)
		if "awn_cream" in nm or nm.begins_with("awn_c"):
			sm.albedo_color = Color(0.99, 0.95, 0.88, c.a)
		# Watchtower / well wood shingles (NOT generic orange roof collapse)
		if "thatch" in nm or nm.begins_with("t1") or nm.begins_with("t2") or nm.begins_with("t3") \
				or "shingle" in nm or (nm.begins_with("sh") and "shadow" not in nm and "ship" not in nm):
			sm.albedo_color = Color(0.78, 0.48, 0.26, c.a)
			sm.roughness = 0.62
		# Soft clay body (windmill / tower cream) — warmer, not peach-collapse
		if "clay" in nm or "body_cream" in nm:
			sm.albedo_color = Color(0.98, 0.94, 0.88, c.a)
			sm.roughness = 0.68
		# Windmill pink-brown mushroom cap
		if "roof_pink" in nm or "cap_pink" in nm or ("roof" in nm and c.r > 0.85 and c.g < 0.65 and c.b < 0.55):
			sm.albedo_color = Color(0.92, 0.48, 0.42, c.a)
		# Bridge soft lavender-grey cobbles (mockup bld_09) — darker than pure white
		if "cobble" in nm or "bridge_s" in nm or "lavender_s" in nm:
			sm.albedo_color = Color(0.78, 0.74, 0.82, c.a)
			sm.roughness = 0.74
		# Cabin interior warm spill (lookout / windmill cutouts)
		if "cabin_emit" in nm or "win_emit" in nm or "interior_glow" in nm:
			sm.emission_enabled = true
			sm.emission = Color(1.0, 0.82, 0.40)
			sm.emission_energy_multiplier = 3.5
			sm.albedo_color = Color(1.0, 0.88, 0.55, c.a)
			sm.roughness = 0.35
		if "hay" in nm:
			sm.albedo_color = Color(0.95, 0.82, 0.28, c.a)
		if "apple" in nm or "fruit_r" in nm:
			sm.albedo_color = Color(0.92, 0.28, 0.28, c.a)
		if "lemon" in nm or "fruit_y" in nm:
			sm.albedo_color = Color(0.95, 0.88, 0.22, c.a)
		if ("orange" in nm and "roof" not in nm) or "fruit_o" in nm:
			sm.albedo_color = Color(0.98, 0.55, 0.15, c.a)
		if "yarn" in nm:
			if c.b > c.r and c.b > c.g:
				sm.albedo_color = Color(0.55, 0.55, 0.95, c.a)
			elif c.g > c.r:
				sm.albedo_color = Color(0.45, 0.85, 0.55, c.a)
			else:
				sm.albedo_color = Color(0.95, 0.45, 0.70, c.a)
		if "reg" in nm and "door" not in nm:
			sm.albedo_color = Color(0.55, 0.82, 0.65, c.a)
		if "blade" in nm or "hub" in nm:
			sm.albedo_color = Color(0.82, 0.58, 0.35, c.a)
		if "band" in nm and "roof" not in nm:
			sm.albedo_color = Color(0.82, 0.52, 0.35, c.a)
		if "stone" in nm or "rock" in nm:
			sm.albedo_color = Color(0.68, 0.62, 0.54, c.a)
		if "water" in nm or "pond" in nm:
			sm.albedo_color = Color(0.28, 0.62, 0.88, c.a)
			sm.emission_enabled = true
			sm.emission = Color(0.25, 0.55, 0.85)
			sm.emission_energy_multiplier = 0.6
			sm.roughness = 0.15
		if "lily" in nm:
			sm.albedo_color = Color(0.35, 0.72, 0.32, c.a)
		if "trunk" in nm:
			sm.albedo_color = Color(0.52, 0.34, 0.22, c.a)
		if "canopy" in nm or ("leaf" in nm and "water" not in nm):
			if c.g > c.r:
				sm.albedo_color = Color(0.32, 0.70, 0.30, c.a)
		if "soil" in nm:
			sm.albedo_color = Color(0.42, 0.30, 0.20, c.a)
		if "glass" in nm:
			sm.albedo_color = Color(0.30, 0.70, 0.95, 0.32)
			sm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			sm.emission_enabled = true
			sm.emission = Color(0.35, 0.72, 0.98)
			sm.emission_energy_multiplier = 0.55
			sm.roughness = 0.08
		# Mesh-name glass panes (when material name lost on glTF)
		var minm0 := str(mi.name).to_lower()
		if "glass" in minm0 or minm0.begins_with("glass"):
			sm.albedo_color = Color(0.30, 0.70, 0.95, 0.32)
			sm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			sm.emission_enabled = true
			sm.emission = Color(0.35, 0.72, 0.98)
			sm.emission_energy_multiplier = 0.55
			sm.roughness = 0.08
		if "frame" in nm and "door" not in nm:
			# greenhouse cream frame — keep warm, not pure white
			if c.r > 0.85:
				sm.albedo_color = Color(0.96, 0.88, 0.72, c.a)
		# Mesh-name fallbacks when glTF drops material names
		var minm := str(mi.name).to_lower()
		if "water" in minm or minm.begins_with("water"):
			sm.albedo_color = Color(0.28, 0.62, 0.88, c.a)
			sm.emission_enabled = true
			sm.emission = Color(0.25, 0.55, 0.85)
			sm.emission_energy_multiplier = 0.6
		sm.roughness = clampf(sm.roughness, 0.15 if "water" in nm or "water" in minm else 0.45, 0.85)
		mi.set_surface_override_material(s, sm)


func _add_footprint(parent: Node3D, fpx: float, fpz: float, role: String) -> void:
	var mi := MeshInstance3D.new()
	mi.name = "Footprint"
	var box := BoxMesh.new()
	box.size = Vector3(maxf(0.4, fpx), 0.04, maxf(0.4, fpz))
	mi.mesh = box
	var mat := StandardMaterial3D.new()
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	match role:
		"building":
			mat.albedo_color = Color(0.78, 0.54, 0.37, 0.28)  # wood
		"character_spawn":
			mat.albedo_color = Color(0.45, 0.72, 0.40, 0.32)  # leaf
		_:
			mat.albedo_color = Color(0.99, 0.95, 0.89, 0.22)  # cream
	mat.emission_enabled = true
	mat.emission = mat.albedo_color
	mat.emission_energy_multiplier = 0.15
	mi.material_override = mat
	mi.position = Vector3(0.0, 0.02, 0.0)
	parent.add_child(mi)
	# outline ring
	var ring := MeshInstance3D.new()
	ring.name = "FootprintEdge"
	var t := TorusMesh.new()
	t.inner_radius = maxf(0.15, minf(fpx, fpz) * 0.35)
	t.outer_radius = t.inner_radius + 0.05
	ring.mesh = t
	var em := StandardMaterial3D.new()
	em.albedo_color = Color(0.38, 0.55, 0.42, 0.55)
	em.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	ring.material_override = em
	ring.position = Vector3(0.0, 0.03, 0.0)
	ring.scale = Vector3(1.0, 0.2, 1.0)
	parent.add_child(ring)


func _add_label(parent: Node3D, text: String, role: String) -> void:
	var lab := Label3D.new()
	lab.name = "PlotLabel"
	lab.text = text
	lab.font_size = 28
	lab.outline_size = 6
	lab.modulate = Color(0.15, 0.2, 0.18, 1.0)
	lab.outline_modulate = Color(0.99, 0.95, 0.89, 0.9)
	lab.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	lab.position = Vector3(0.0, 1.35 if role == "building" else 0.85, 0.0)
	lab.no_depth_test = true
	parent.add_child(lab)


func _add_honest_placeholder(
	parent: Node3D, plot_id: String, object_id: String, role: String, fpx: float, fpz: float
) -> void:
	var mi := MeshInstance3D.new()
	mi.name = "PlaceholderConcept"
	var box := BoxMesh.new()
	var h := 0.55 if role == "prop" else (1.1 if role == "building" else 0.7)
	box.size = Vector3(maxf(0.35, fpx * 0.35), h, maxf(0.35, fpz * 0.35))
	mi.mesh = box
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.85, 0.82, 0.78, 0.55)
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	# dashed feel via emission pulse color (static)
	mat.emission_enabled = true
	mat.emission = Color(0.95, 0.75, 0.35, 1.0)
	mat.emission_energy_multiplier = 0.25
	mi.material_override = mat
	mi.position = Vector3(0.0, h * 0.5, 0.0)
	parent.add_child(mi)

	var lab := Label3D.new()
	lab.name = "PlaceholderLabel"
	lab.text = "%s\n%s\nconcept — not yet authored" % [plot_id, object_id]
	lab.font_size = 22
	lab.outline_size = 5
	lab.modulate = Color(0.55, 0.35, 0.12, 1.0)
	lab.outline_modulate = Color(1.0, 0.97, 0.9, 1.0)
	lab.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	lab.position = Vector3(0.0, h + 0.45, 0.0)
	lab.no_depth_test = true
	parent.add_child(lab)


func _index_cast() -> Dictionary:
	var out := {}
	var roster: Variant = _load_json(CAST_ROSTER)
	if roster is Dictionary:
		for c in roster.get("characters", []):
			if c is Dictionary:
				out[str(c.get("character_id", ""))] = c
	return out


func _index_modules() -> Dictionary:
	var out := {}
	var cat: Variant = _load_json(MODULE_CATALOG)
	if cat is Dictionary:
		for m in cat.get("modules", []):
			if m is Dictionary:
				out[str(m.get("module_id", ""))] = m
	return out


func _clear() -> void:
	for n in _plot_nodes:
		if is_instance_valid(n):
			n.queue_free()
	_plot_nodes.clear()
	for c in get_children():
		c.queue_free()


func _load_json(path: String) -> Variant:
	if not FileAccess.file_exists(path):
		return null
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return null
	var t := f.get_as_text()
	f.close()
	return JSON.parse_string(t)
