## Cozy Starter Town — 10-phase layout placer.
## Spawns district entities from town_layout_10phase.json using cast roster + P1E catalog.
## Presentation only: never World-Commits. Honest missing-asset reporting.
extends Node3D

const _CastPresenter := preload("res://scripts/modules/ucbv_001/cast_presenter.gd")
const _GlbIntake = preload("res://scripts/modules/asset/glb_intake.gd")

const LAYOUT_PATH := "res://resources/town/town_layout_10phase.json"
const CAST_ROSTER := "res://resources/ucbv_001/cast/cast_roster.json"
const MODULE_CATALOG := "res://resources/p1e_cozy/module_catalog.json"

## Alias mockup building IDs → currently catalogued module_ids when not 1:1 yet.
const MODULE_ALIASES := {
	"cozy_greenhouse_A": "cozy_greenhouse_preview_anchor_A",
}

var _last_report: Dictionary = {}
var _char_nodes: Array = []
var _module_nodes: Array = []


func get_report() -> Dictionary:
	return _last_report.duplicate(true)


func build_town(max_phase: int = -1) -> Dictionary:
	_clear()
	var layout: Variant = _load_json(LAYOUT_PATH)
	if layout == null or not (layout is Dictionary):
		_last_report = {"ok": false, "error": "layout_missing", "path": LAYOUT_PATH}
		return _last_report
	var roster: Variant = _load_json(CAST_ROSTER)
	var catalog: Variant = _load_json(MODULE_CATALOG)
	var cast_by_id: Dictionary = {}
	if roster is Dictionary:
		for c in roster.get("characters", []):
			if c is Dictionary:
				cast_by_id[str(c.get("character_id", ""))] = c
	var mod_by_id: Dictionary = {}
	if catalog is Dictionary:
		for m in catalog.get("modules", []):
			if m is Dictionary:
				mod_by_id[str(m.get("module_id", ""))] = m

	var active: Array = layout.get("active_phases", []) as Array
	var phases: Array = layout.get("phases", []) as Array
	var intake: RefCounted = _GlbIntake.new()

	var phases_built := 0
	var chars_built := 0
	var modules_built := 0
	var idle_play := 0
	var missing: Array = []
	var failed: Array = []

	for ph in phases:
		if not (ph is Dictionary):
			continue
		var pnum := int(ph.get("phase", 0))
		if max_phase > 0 and pnum > max_phase:
			continue
		if not active.is_empty() and not active.has(pnum) and not active.has(float(pnum)):
			# Still allow explicit max_phase override for progressive unlock tests.
			if max_phase < 0:
				continue
		var district := str(ph.get("district_id", "d%d" % pnum))
		var root := Node3D.new()
		root.name = "District_%02d_%s" % [pnum, district]
		add_child(root)

		# --- Character ---
		var ch: Dictionary = ph.get("character", {}) as Dictionary
		var cid := str(ch.get("character_id", ""))
		var cspawn: Dictionary = ch.get("spawn", {}) as Dictionary
		if cast_by_id.has(cid):
			var crow: Dictionary = cast_by_id[cid]
			var presenter: Node3D = _CastPresenter.new() as Node3D
			presenter.name = "Char_%s" % cid.replace("-", "_")
			root.add_child(presenter)
			_apply_spawn(presenter, cspawn)
			if presenter.has_method("configure"):
				presenter.call(
					"configure",
					cid,
					str(crow.get("glb", "")),
					str(crow.get("glb_sha256", ""))
				)
			var st: Dictionary = presenter.call("build_from_assets") as Dictionary
			_char_nodes.append(presenter)
			if bool(st.get("built", false)):
				chars_built += 1
				if presenter.has_method("play_clip") and bool(presenter.call("play_clip", "idle")):
					idle_play += 1
			else:
				failed.append({"phase": pnum, "kind": "character", "id": cid, "error": st.get("error", "build_failed")})
		else:
			missing.append({"phase": pnum, "kind": "character", "id": cid, "error": "not_in_cast_roster"})

		# --- Building ---
		var bld: Dictionary = ph.get("building", {}) as Dictionary
		var bmid := str(bld.get("module_id", ""))
		var bspawn: Dictionary = bld.get("spawn", {}) as Dictionary
		var bres: Dictionary = _spawn_module(root, bmid, bspawn, mod_by_id, intake, pnum, "building")
		if bool(bres.get("ok", false)):
			modules_built += 1
		elif str(bres.get("error", "")) == "missing":
			missing.append(bres)
		else:
			failed.append(bres)

		# --- Props ---
		for prop in ph.get("props", []):
			if not (prop is Dictionary):
				continue
			var pmid := str(prop.get("module_id", ""))
			var pspawn: Dictionary = prop.get("spawn", {}) as Dictionary
			var pres: Dictionary = _spawn_module(root, pmid, pspawn, mod_by_id, intake, pnum, "prop")
			if bool(pres.get("ok", false)):
				modules_built += 1
			elif str(pres.get("error", "")) == "missing":
				missing.append(pres)
			else:
				failed.append(pres)

		phases_built += 1

	var parity_ok := failed.is_empty() and missing.is_empty() and phases_built > 0 and chars_built > 0
	## Runtime can still be playable while parity is incomplete (honest missing list).
	var runtime_usable := phases_built > 0 and chars_built > 0 and modules_built >= 3 and idle_play >= 1
	_last_report = {
		"ok": parity_ok,
		"parity_ok": parity_ok,
		"runtime_usable": runtime_usable,
		"phases_built": phases_built,
		"chars_built": chars_built,
		"modules_built": modules_built,
		"idle_play": idle_play,
		"missing": missing,
		"failed": failed,
		"town_id": str(layout.get("town_id", "")),
		"mockup_ssot": str(layout.get("mockup_ssot", "")),
		"honesty": "missing modules fail MOCKUP_PARITY_100; no fake pass",
	}
	print(
		"[Town] phases=%s chars=%s modules=%s idle=%s missing=%s failed=%s parity=%s runtime=%s"
		% [
			phases_built,
			chars_built,
			modules_built,
			idle_play,
			missing.size(),
			failed.size(),
			parity_ok,
			runtime_usable,
		]
	)
	if parity_ok:
		print("AIDLE_TOWN_PHASE_LAYOUT=PASS")
	elif runtime_usable:
		print("AIDLE_TOWN_PHASE_LAYOUT=RUNTIME_OK_PARITY_PENDING missing=%s" % missing.size())
	else:
		print("AIDLE_TOWN_PHASE_LAYOUT=FAIL missing=%s failed=%s" % [missing.size(), failed.size()])
	return _last_report


func play_all_idle() -> int:
	var n := 0
	for p in _char_nodes:
		if is_instance_valid(p) and p.has_method("play_clip"):
			if bool(p.call("play_clip", "idle")):
				n += 1
	return n


func _spawn_module(
	parent: Node3D,
	module_id: String,
	spawn: Dictionary,
	mod_by_id: Dictionary,
	intake: RefCounted,
	phase: int,
	kind: String
) -> Dictionary:
	var resolved := module_id
	if not mod_by_id.has(resolved) and MODULE_ALIASES.has(module_id):
		resolved = str(MODULE_ALIASES[module_id])
	if not mod_by_id.has(resolved):
		return {"ok": false, "error": "missing", "phase": phase, "kind": kind, "id": module_id}
	var row: Dictionary = mod_by_id[resolved]
	var glb := str(row.get("glb", ""))
	var abs_path := ProjectSettings.globalize_path(glb) if glb.begins_with("res://") else glb
	if not FileAccess.file_exists(abs_path):
		return {"ok": false, "error": "missing_file", "phase": phase, "kind": kind, "id": module_id, "path": glb}
	var node: Node3D = intake.call("load_glb_absolute", abs_path, module_id) as Node3D
	if node == null:
		return {"ok": false, "error": "intake_failed", "phase": phase, "kind": kind, "id": module_id}
	node.name = "%s_%s" % [kind, module_id]
	parent.add_child(node)
	_apply_spawn(node, spawn)
	if module_id == "cozy_house_small_A" or resolved == "cozy_house_small_A":
		node.scale = Vector3(1.25, 1.25, 1.25)
	_module_nodes.append(node)
	return {"ok": true, "phase": phase, "kind": kind, "id": module_id, "resolved": resolved}


func _apply_spawn(node: Node3D, spawn: Dictionary) -> void:
	node.position = Vector3(
		float(spawn.get("x", 0.0)),
		float(spawn.get("y", 0.0)),
		float(spawn.get("z", 0.0))
	)
	node.rotation_degrees = Vector3(0.0, float(spawn.get("rotation_deg", 0.0)), 0.0)


func _clear() -> void:
	for n in _char_nodes:
		if is_instance_valid(n):
			n.queue_free()
	for n in _module_nodes:
		if is_instance_valid(n):
			n.queue_free()
	_char_nodes.clear()
	_module_nodes.clear()
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
