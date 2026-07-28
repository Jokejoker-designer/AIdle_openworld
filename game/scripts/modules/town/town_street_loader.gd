## WO-TOWN-STREET-IMPORT-001 Phase A — fairy-street stone path network.
## Tiles cozy_path_stone_A.glb along TOWN_FAIRY_STREET_PLAN_V1 stone_path_network[].
## Presentation only; never World-Commits. Does NOT edit town_grid_loader or grid plan.
## Phase B wood_platforms: primitive plank overlay when no production deck GLB.
## STREET_V2c MultiMesh stone + TOWN_ALIGNMENT_V1 wood overlay.
extends Node3D

const _GlbIntake = preload("res://scripts/modules/asset/glb_intake.gd")

const PLAN_PATH := "res://resources/town/town_fairy_street_plan_v1.json"
const MODULE_CATALOG := "res://resources/p1e_cozy/module_catalog.json"
const PATH_MODULE_ID := "cozy_path_stone_A"

## Dense enough for continuous ribbon; MultiMesh keeps GPU cost flat.
const TILE_STEP := 0.58
const TILE_CROSS_STEP := 0.58
const TILE_SCALE := 1.12
const TILE_YAW_JITTER_DEG := 18.0
const ELLIPSE_SAMPLES := 40
const ELLIPSE_RADIAL_BANDS := 2

var _last_report: Dictionary = {}
var _segment_nodes: Array = []
var _path_template: Node3D = null
## [{ "mesh": Mesh, "materials": Array[Material], "local_xform": Transform3D }]
var _path_mesh_parts: Array = []


func get_report() -> Dictionary:
	return _last_report.duplicate(true)


func build_streets() -> Dictionary:
	_clear()
	var plan: Variant = _load_json(PLAN_PATH)
	if plan == null or not (plan is Dictionary):
		_last_report = {
			"ok": false,
			"error": "plan_missing",
			"path": PLAN_PATH,
			"work_order": "WO-TOWN-STREET-IMPORT-001",
			"accepted": false,
			"self_accept": false,
		}
		print("AIDLE_TOWN_STREET_IMPORT=FAIL plan_missing")
		return _last_report

	var network: Array = plan.get("stone_path_network", []) as Array
	var mod_by_id: Dictionary = _index_modules()
	var intake: RefCounted = _GlbIntake.new()

	var segments_total := 0
	var segments_ok := 0
	var tiles_placed := 0
	var failed: Array = []
	var segment_reports: Array = []
	var max_abs := 0.0
	var coords_ok := true

	if not mod_by_id.has(PATH_MODULE_ID):
		_last_report = {
			"ok": false,
			"error": "path_module_not_in_catalog",
			"module_id": PATH_MODULE_ID,
			"work_order": "WO-TOWN-STREET-IMPORT-001",
			"accepted": false,
			"self_accept": false,
		}
		print("AIDLE_TOWN_STREET_IMPORT=FAIL path_module_not_in_catalog")
		return _last_report

	var glb_row: Dictionary = mod_by_id[PATH_MODULE_ID]
	var glb := str(glb_row.get("glb", ""))
	var abs_path := ProjectSettings.globalize_path(glb) if glb.begins_with("res://") else glb
	if not FileAccess.file_exists(abs_path):
		_last_report = {
			"ok": false,
			"error": "path_glb_missing",
			"glb": glb,
			"work_order": "WO-TOWN-STREET-IMPORT-001",
			"accepted": false,
			"self_accept": false,
		}
		print("AIDLE_TOWN_STREET_IMPORT=FAIL path_glb_missing")
		return _last_report

	if _path_template != null and is_instance_valid(_path_template):
		_path_template.queue_free()
	_path_template = intake.call("load_glb_absolute", abs_path, "path_stone_template") as Node3D
	if _path_template == null:
		_last_report = {
			"ok": false,
			"error": "path_template_load_failed",
			"glb": glb,
			"work_order": "WO-TOWN-STREET-IMPORT-001",
			"accepted": false,
			"self_accept": false,
		}
		print("AIDLE_TOWN_STREET_IMPORT=FAIL path_template_load_failed")
		return _last_report
	_boost_path_materials(_path_template)
	_path_mesh_parts = _extract_mesh_parts(_path_template)
	_path_template.visible = false
	add_child(_path_template)
	if _path_mesh_parts.is_empty():
		_last_report = {
			"ok": false,
			"error": "path_template_no_mesh",
			"glb": glb,
			"work_order": "WO-TOWN-STREET-IMPORT-001",
			"accepted": false,
			"self_accept": false,
		}
		print("AIDLE_TOWN_STREET_IMPORT=FAIL path_template_no_mesh")
		return _last_report

	for seg in network:
		if not (seg is Dictionary):
			continue
		segments_total += 1
		var sid := str(seg.get("id", "SP_%d" % segments_total))
		var geom := str(seg.get("geometry", "axis_aligned"))
		var width_m := float(seg.get("width_m", 2.0))
		var root := Node3D.new()
		root.name = "StreetSeg_%s" % sid.replace("-", "_")
		add_child(root)
		_segment_nodes.append(root)

		var label_text := "%s\n%s" % [sid, str(seg.get("name_vi", "stone_path"))]
		_add_label(root, label_text)

		var xforms: Array = []  ## Array of Transform3D in parent-local space
		var err := ""
		if geom == "axis_aligned" or geom == "":
			var res: Dictionary = _collect_axis_aligned(root, seg)
			xforms = res.get("xforms", []) as Array
			err = str(res.get("error", ""))
			max_abs = maxf(max_abs, float(res.get("max_abs", 0.0)))
			if not bool(res.get("coords_ok", true)):
				coords_ok = false
		elif geom == "ring_rect":
			var res2: Dictionary = _collect_ring_rect(root, seg)
			xforms = res2.get("xforms", []) as Array
			err = str(res2.get("error", ""))
			max_abs = maxf(max_abs, float(res2.get("max_abs", 0.0)))
		elif geom == "ring_ellipse":
			var res3: Dictionary = _collect_ring_ellipse(root, seg)
			xforms = res3.get("xforms", []) as Array
			err = str(res3.get("error", ""))
			max_abs = maxf(max_abs, float(res3.get("max_abs", 0.0)))
		else:
			err = "unknown_geometry_%s" % geom
			_add_honest_placeholder(root, sid, "unknown_geometry")

		var placed := 0
		if err.is_empty() and not xforms.is_empty():
			placed = _commit_multimesh(root, xforms)

		if placed > 0 and err.is_empty():
			segments_ok += 1
			tiles_placed += placed
			segment_reports.append({
				"id": sid,
				"geometry": geom,
				"width_m": width_m,
				"tiles": placed,
				"status": "real_glb_multimesh",
				"module_id": PATH_MODULE_ID,
			})
		else:
			if placed == 0 and err.is_empty():
				err = "zero_tiles"
			failed.append({"id": sid, "error": err if not err.is_empty() else "place_failed"})
			if placed == 0:
				_add_honest_placeholder(root, sid, err if not err.is_empty() else "unresolved")
			segment_reports.append({
				"id": sid,
				"geometry": geom,
				"tiles": placed,
				"status": "partial_or_failed" if placed > 0 else "honest_placeholder",
				"error": err,
			})
			if placed > 0:
				tiles_placed += placed
				segments_ok += 1

	## TOWN_ALIGNMENT_V1: wood platform overlay (presentation primitives — not cozy_wood_deck_A GLB).
	## Plan geometry only; does not claim production module identity.
	var wood: Array = plan.get("wood_platforms", []) as Array
	var wood_reports: Array = []
	var wood_ok := 0
	var wood_flags: Array = []
	for wp in wood:
		if not (wp is Dictionary):
			continue
		var wr: Dictionary = _place_wood_platform(wp)
		wood_reports.append(wr)
		if bool(wr.get("ok", false)):
			wood_ok += 1
		if wr.has("design_flag"):
			wood_flags.append(wr.get("design_flag"))

	var ok := segments_total == 13 and failed.is_empty() and coords_ok
	_last_report = {
		"ok": ok,
		"work_order": "WO-TOWN-STREET-IMPORT-001",
		"directive": "TOWN_ALIGNMENT_V1_STONE_PLUS_WOOD_OVERLAY",
		"loader_pass": "STREET_V2C_MULTIMESH_PLUS_WOOD_PRIMS",
		"tile_step_m": TILE_STEP,
		"tile_scale": TILE_SCALE,
		"plan_id": str(plan.get("plan_id", "TOWN_FAIRY_STREET_PLAN_V1")),
		"segments_total": segments_total,
		"segments_ok": segments_ok,
		"tiles_placed": tiles_placed,
		"path_module_id": PATH_MODULE_ID,
		"failed": failed,
		"segment_reports": segment_reports,
		"phase_b_wood_platforms": {
			"skipped": false,
			"implementation": "presentation_boxmesh_planks_not_production_glb",
			"count_in_plan": wood.size(),
			"placed": wood_ok,
			"reports": wood_reports,
			"design_flags": wood_flags,
			"reason": "no cozy_wood_deck_A GLB — honest primitive decks from plan rects (overlay only)",
		},
		"coords_within_pm12": coords_ok and max_abs <= 12.0,
		"max_abs_xz": max_abs,
		"accepted": false,
		"self_accept": false,
		"honesty": "Stone MultiMesh real GLB; wood = labeled primitive overlay not production deck module",
	}
	print(
		"[TownStreet] ALIGN_V1 segments=%s ok=%s tiles=%s wood=%s/%s step=%.2f max_abs=%.2f"
		% [segments_total, segments_ok, tiles_placed, wood_ok, wood.size(), TILE_STEP, max_abs]
	)
	if ok:
		print("AIDLE_TOWN_STREET_IMPORT=PASS")
	else:
		print("AIDLE_TOWN_STREET_IMPORT=FAIL failed=%s" % failed.size())
	return _last_report


func _place_wood_platform(wp: Dictionary) -> Dictionary:
	var wid := str(wp.get("id", "WD_?"))
	var x0 := float(wp.get("x0", 0.0))
	var x1 := float(wp.get("x1", 0.0))
	var z0 := float(wp.get("z0", 0.0))
	var z1 := float(wp.get("z1", 0.0))
	var min_x := minf(x0, x1)
	var max_x := maxf(x0, x1)
	var min_z := minf(z0, z1)
	var max_z := maxf(z0, z1)
	var cx := (min_x + max_x) * 0.5
	var cz := (min_z + max_z) * 0.5
	var sx := maxf(0.2, max_x - min_x)
	var sz := maxf(0.2, max_z - min_z)
	var h := float(wp.get("height_above_path_m", 0.08))
	var root := Node3D.new()
	root.name = "WoodPlat_%s" % wid.replace("-", "_")
	root.position = Vector3(cx, 0.0, cz)
	add_child(root)

	## Deck slab
	var mi := MeshInstance3D.new()
	mi.name = "Deck"
	var box := BoxMesh.new()
	box.size = Vector3(sx, 0.06, sz)
	mi.mesh = box
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.72, 0.52, 0.32, 1.0)
	mat.roughness = 0.75
	mi.material_override = mat
	mi.position = Vector3(0.0, h + 0.03, 0.0)
	root.add_child(mi)

	## Plank lines (visual only)
	var axis := str(wp.get("plank_axis", "x"))
	var n_plank := maxi(2, int(ceil((sx if axis == "x" else sz) / 0.35)))
	for i in range(n_plank + 1):
		var line := MeshInstance3D.new()
		line.name = "PlankLine_%d" % i
		var lb := BoxMesh.new()
		if axis == "x":
			var t := float(i) / float(n_plank) if n_plank > 0 else 0.5
			lb.size = Vector3(0.03, 0.02, sz * 0.98)
			line.position = Vector3(-sx * 0.5 + t * sx, h + 0.07, 0.0)
		else:
			var t2 := float(i) / float(n_plank) if n_plank > 0 else 0.5
			lb.size = Vector3(sx * 0.98, 0.02, 0.03)
			line.position = Vector3(0.0, h + 0.07, -sz * 0.5 + t2 * sz)
		line.mesh = lb
		var lm := StandardMaterial3D.new()
		lm.albedo_color = Color(0.55, 0.38, 0.22, 1.0)
		line.material_override = lm
		root.add_child(line)

	var lab := Label3D.new()
	lab.name = "WoodLabel"
	lab.text = "%s\noverlay deck — plan" % wid
	lab.font_size = 20
	lab.outline_size = 4
	lab.modulate = Color(0.85, 0.70, 0.45, 0.95)
	lab.position = Vector3(0.0, h + 0.55, 0.0)
	lab.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	root.add_child(lab)

	var out := {
		"ok": true,
		"id": wid,
		"serves": str(wp.get("serves", "")),
		"center": [cx, cz],
		"size": [sx, sz],
		"implementation": "primitive_plank_overlay",
	}
	## WD-GAZEBO: Human ruled deck moves to GARDEN.BLD H12 (not plaza origin / HOME.BLD).
	## Residual safety: if plan still places deck at plaza origin, re-flag conflict.
	if wid == "WD-GAZEBO":
		if absf(cx) < 2.0 and absf(cz) < 2.0:
			out["design_flag"] = {
				"id": "CONFLICT_WD_GAZEBO_VS_HOME_BLD",
				"status": "REOPENED_PLAN_STILL_AT_ORIGIN",
				"wood_platform": "WD-GAZEBO",
				"wood_rect_xz": [min_x, max_x, min_z, max_z],
				"wood_serves_plan": str(wp.get("serves", "")),
				"conflicts_with_plot": "HOME.BLD",
				"home_transform_xz": [0.0, 0.0],
				"gazebo_plot_transform_xz": [2.0, 10.0],
				"note": "Plan still centers WD-GAZEBO at plaza origin after HUMAN_RULED_MOVE_DECK — fix fairy-street rect.",
			}
		elif absf(cx - 2.0) < 0.5 and absf(cz - 10.0) < 0.5:
			out["design_flag"] = {
				"id": "CONFLICT_WD_GAZEBO_VS_HOME_BLD",
				"status": "RESOLVED",
				"decision": "HUMAN_RULED_MOVE_DECK",
				"decided_at": "2026-07-24T12:07:00+07:00",
				"wood_platform": "WD-GAZEBO",
				"wood_rect_xz": [min_x, max_x, min_z, max_z],
				"center_xz": [cx, cz],
				"aligned_to_plot": "GARDEN.BLD",
				"gazebo_plot_transform_xz": [2.0, 10.0],
				"grid_cell": "H12",
				"note": "Deck recentered on cadastre GARDEN.BLD (2,10) H12; no longer under HOME.BLD.",
			}
	return out


func _collect_axis_aligned(parent: Node3D, seg: Dictionary) -> Dictionary:
	var x0 := float(seg.get("x0", 0.0))
	var x1 := float(seg.get("x1", 0.0))
	var z0 := float(seg.get("z0", 0.0))
	var z1 := float(seg.get("z1", 0.0))
	var min_x := minf(x0, x1)
	var max_x := maxf(x0, x1)
	var min_z := minf(z0, z1)
	var max_z := maxf(z0, z1)
	var max_abs := maxf(maxf(absf(min_x), absf(max_x)), maxf(absf(min_z), absf(max_z)))
	parent.position = Vector3((min_x + max_x) * 0.5, 0.0, (min_z + max_z) * 0.5)
	var xforms := _rect_xforms(parent, min_x, max_x, min_z, max_z)
	return {"xforms": xforms, "max_abs": max_abs, "coords_ok": max_abs <= 12.0, "error": ""}


func _collect_ring_rect(parent: Node3D, seg: Dictionary) -> Dictionary:
	var b: Dictionary = seg.get("bounds", {}) as Dictionary
	var min_x := float(b.get("min_x", -9.0))
	var max_x := float(b.get("max_x", 9.0))
	var min_z := float(b.get("min_z", -9.0))
	var max_z := float(b.get("max_z", 9.0))
	var width_m := float(seg.get("width_m", 1.8))
	parent.position = Vector3(0.0, 0.0, 0.0)
	var max_abs := maxf(maxf(absf(min_x), absf(max_x)), maxf(absf(min_z), absf(max_z)))
	var half_w := width_m * 0.5
	var xforms: Array = []
	xforms.append_array(_rect_xforms(parent, min_x, max_x, max_z - half_w, max_z + half_w))
	xforms.append_array(_rect_xforms(parent, min_x, max_x, min_z - half_w, min_z + half_w))
	xforms.append_array(_rect_xforms(parent, max_x - half_w, max_x + half_w, min_z + half_w, max_z - half_w))
	xforms.append_array(_rect_xforms(parent, min_x - half_w, min_x + half_w, min_z + half_w, max_z - half_w))
	return {"xforms": xforms, "max_abs": max_abs, "coords_ok": max_abs <= 12.0, "error": ""}


func _collect_ring_ellipse(parent: Node3D, seg: Dictionary) -> Dictionary:
	var c: Dictionary = seg.get("center", {}) as Dictionary
	var cx := float(c.get("x", 0.0))
	var cz := float(c.get("z", 0.0))
	var rx := float(seg.get("rx", 3.2))
	var rz := float(seg.get("rz", 2.6))
	var width_m := float(seg.get("width_m", 1.2))
	parent.position = Vector3(cx, 0.0, cz)
	var half_w := width_m * 0.5
	var xforms: Array = []
	var idx := 0
	for ri in range(ELLIPSE_RADIAL_BANDS + 1):
		var rt := float(ri) / float(ELLIPSE_RADIAL_BANDS) if ELLIPSE_RADIAL_BANDS > 0 else 0.5
		var r_scale := 1.0 + (rt - 0.5) * (half_w * 2.0) / maxf(minf(rx, rz), 0.5)
		for i in range(ELLIPSE_SAMPLES):
			var ang := TAU * float(i) / float(ELLIPSE_SAMPLES)
			var x := rx * r_scale * cos(ang)
			var z := rz * r_scale * sin(ang)
			xforms.append(_make_tile_xform(x, z, idx))
			idx += 1
	var max_abs := maxf(absf(cx) + rx + half_w, absf(cz) + rz + half_w)
	return {"xforms": xforms, "max_abs": max_abs, "coords_ok": max_abs <= 12.0, "error": ""}


func _rect_xforms(
	parent: Node3D, min_x: float, max_x: float, min_z: float, max_z: float
) -> Array:
	var dx := max_x - min_x
	var dz := max_z - min_z
	var out: Array = []
	var nx := maxi(0, int(ceil(dx / TILE_STEP))) if dx > 0.02 else 0
	var nz := maxi(0, int(ceil(dz / TILE_CROSS_STEP))) if dz > 0.02 else 0
	var idx := 0
	if dx <= 0.02 and dz <= 0.02:
		out.append(_make_tile_xform(min_x - parent.position.x, min_z - parent.position.z, idx))
		return out
	for iz in range(nz + 1):
		var tz := 0.5 if nz == 0 else float(iz) / float(nz)
		var z := min_z + tz * dz
		for ix in range(nx + 1):
			var tx := 0.5 if nx == 0 else float(ix) / float(nx)
			var x := min_x + tx * dx
			out.append(_make_tile_xform(x - parent.position.x, z - parent.position.z, idx))
			idx += 1
	return out


func _make_tile_xform(local_x: float, local_z: float, idx: int) -> Transform3D:
	var yaw_deg := fmod(float(idx * 37), TILE_YAW_JITTER_DEG * 2.0) - TILE_YAW_JITTER_DEG
	var basis := Basis(Vector3.UP, deg_to_rad(yaw_deg)).scaled(Vector3(TILE_SCALE, TILE_SCALE, TILE_SCALE))
	return Transform3D(basis, Vector3(local_x, 0.02, local_z))


func _extract_mesh_parts(root: Node) -> Array:
	var parts: Array = []
	var stack: Array = [root]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is MeshInstance3D:
			var mi := n as MeshInstance3D
			if mi.mesh != null:
				var mats: Array = []
				for s in range(mi.mesh.get_surface_count()):
					var mat: Material = mi.get_active_material(s)
					if mat == null and mi.mesh is ArrayMesh:
						mat = (mi.mesh as ArrayMesh).surface_get_material(s)
					mats.append(mat)
				parts.append({
					"mesh": mi.mesh,
					"materials": mats,
					"local_xform": mi.transform,
				})
		for c in n.get_children():
			stack.append(c)
	return parts


func _commit_multimesh(parent: Node3D, xforms: Array) -> int:
	## One MultiMeshInstance3D per source mesh part; instances share mesh + materials.
	if xforms.is_empty() or _path_mesh_parts.is_empty():
		return 0
	var count := xforms.size()
	var part_i := 0
	for part in _path_mesh_parts:
		if not (part is Dictionary):
			continue
		var mesh: Mesh = part.get("mesh") as Mesh
		if mesh == null:
			continue
		var mmi := MultiMeshInstance3D.new()
		mmi.name = "PathMultiMesh_%d" % part_i
		var mm := MultiMesh.new()
		mm.transform_format = MultiMesh.TRANSFORM_3D
		mm.mesh = mesh
		mm.instance_count = count
		var part_local: Transform3D = part.get("local_xform", Transform3D.IDENTITY)
		for i in range(count):
			var t: Transform3D = xforms[i] as Transform3D
			## Bake GLB mesh-local offset into each instance transform
			mm.set_instance_transform(i, t * part_local)
		mmi.multimesh = mm
		var mats: Array = part.get("materials", []) as Array
		if mats.size() == 1 and mats[0] is Material:
			mmi.material_override = mats[0] as Material
		elif mats.size() > 1:
			## Prefer first opaque surface as override; multi-surface stays on mesh
			if mats[0] is Material:
				mmi.material_override = mats[0] as Material
		parent.add_child(mmi)
		part_i += 1
	return count


func _boost_path_materials(root: Node) -> void:
	var stack: Array = [root]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is MeshInstance3D:
			var mi := n as MeshInstance3D
			if mi.mesh == null:
				continue
			for s in range(mi.mesh.get_surface_count()):
				var mat: Material = mi.get_active_material(s)
				if mat == null and mi.mesh is ArrayMesh:
					mat = (mi.mesh as ArrayMesh).surface_get_material(s)
				if mat == null or not (mat is StandardMaterial3D):
					continue
				var sm := (mat as StandardMaterial3D).duplicate() as StandardMaterial3D
				var c := sm.albedo_color
				var nm := str(sm.resource_name).to_lower()
				if "moss" in nm or (c.g > c.r + 0.05 and c.g > c.b):
					sm.albedo_color = Color(0.40, 0.65, 0.35, c.a)
				elif "stone" in nm or c.r > 0.7:
					sm.albedo_color = Color(0.78, 0.72, 0.64, c.a)
				sm.roughness = clampf(sm.roughness, 0.55, 0.9)
				mi.set_surface_override_material(s, sm)
		for c in n.get_children():
			stack.append(c)


func _add_label(parent: Node3D, text: String) -> void:
	var lab := Label3D.new()
	lab.name = "SegLabel"
	lab.text = text
	lab.font_size = 28
	lab.outline_size = 6
	lab.modulate = Color(0.95, 0.92, 0.85, 0.95)
	lab.position = Vector3(0.0, 0.85, 0.0)
	lab.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	parent.add_child(lab)


func _add_honest_placeholder(parent: Node3D, sid: String, reason: String) -> void:
	var mi := MeshInstance3D.new()
	mi.name = "HonestPlaceholder"
	var box := BoxMesh.new()
	box.size = Vector3(1.2, 0.08, 1.2)
	mi.mesh = box
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.55, 0.45, 0.35, 0.45)
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	mi.material_override = mat
	mi.position = Vector3(0.0, 0.04, 0.0)
	parent.add_child(mi)
	var lab := Label3D.new()
	lab.text = "%s\nconcept — %s" % [sid, reason]
	lab.font_size = 22
	lab.position = Vector3(0.0, 0.5, 0.0)
	lab.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	lab.modulate = Color(0.95, 0.7, 0.4, 1.0)
	parent.add_child(lab)


func _index_modules() -> Dictionary:
	var out := {}
	var data: Variant = _load_json(MODULE_CATALOG)
	if data == null or not (data is Dictionary):
		return out
	for m in (data as Dictionary).get("modules", []) as Array:
		if m is Dictionary:
			out[str(m.get("module_id", ""))] = m
	return out


func _load_json(path: String) -> Variant:
	if not FileAccess.file_exists(path):
		return null
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return null
	var text := f.get_as_text()
	f.close()
	return JSON.parse_string(text)


func _clear() -> void:
	for c in get_children():
		c.queue_free()
	_segment_nodes.clear()
	_path_template = null
	_path_mesh_parts.clear()
	_last_report.clear()
