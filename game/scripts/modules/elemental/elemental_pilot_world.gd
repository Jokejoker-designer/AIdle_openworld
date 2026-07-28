## WO-P1E-004 thin elemental pilot world (first-execution adapted DNA concepts).
## Deliberate choice: NOT wholesale import of godot_4_3/addons/aidle_elemental_physics
## (solvers, ElementalBody3D, full 170-module assumptions). Minimum for 5 modules only.
##
## Trust boundaries:
## - No durable write except via PersistModule.apply_mutation (offline confirmed).
## - Preview entities (preview_only) never simulate and never journal.
## - No collision/navigation authority changes.
## - No autoload; instantiate when pilot runs.
extends RefCounted

const MAP_PATH := "res://resources/elemental/pilot/aidle_module_id_map_pilot.json"
const PROFILES_PATH := "res://resources/elemental/pilot/pilot_profiles_subset.json"
const STATE_SCRIPT := "res://scripts/modules/elemental/elemental_state.gd"

var _map: Dictionary = {}
var _profiles: Dictionary = {}
var _entities: Dictionary = {}  # entity_id -> state RefCounted
var _positions: Dictionary = {}  # entity_id -> Vector3
var last_error: String = ""
var lod_profile_id: String = "sim_lod_pc_balanced_v1"


func load_pilot_catalogs() -> bool:
	last_error = ""
	if not FileAccess.file_exists(MAP_PATH) or not FileAccess.file_exists(PROFILES_PATH):
		last_error = "pilot_catalog_missing"
		return false
	var mf := FileAccess.open(MAP_PATH, FileAccess.READ)
	var pf := FileAccess.open(PROFILES_PATH, FileAccess.READ)
	var mj = JSON.parse_string(mf.get_as_text())
	var pj = JSON.parse_string(pf.get_as_text())
	if typeof(mj) != TYPE_DICTIONARY or typeof(pj) != TYPE_DICTIONARY:
		last_error = "pilot_catalog_parse"
		return false
	_map = mj
	_profiles = pj
	lod_profile_id = str(_map.get("simulation_lod_profile_id", lod_profile_id))
	return true


func binding_for_module(aidle_module_id: String) -> Dictionary:
	for b in _map.get("bindings", []):
		if str(b.get("aidle_module_id", "")) == aidle_module_id:
			return b
	return {}


func create_entity(
	entity_id: String,
	aidle_module_id: String,
	position: Vector3,
	preview_only: bool = false
) -> Dictionary:
	var b: Dictionary = binding_for_module(aidle_module_id)
	if b.is_empty():
		return {"ok": false, "error": "no_binding:%s" % aidle_module_id}
	var st = load(STATE_SCRIPT).new()
	st.entity_id = entity_id
	st.aidle_module_id = aidle_module_id
	st.dna_module_id = str(b.get("dna_module_id", ""))
	st.element_id = str(b.get("element_id", ""))
	st.physical_profile_id = str(b.get("physical_profile_id", ""))
	st.simulates = bool(b.get("simulates", false)) and not preview_only
	st.preview_only = preview_only
	st.last_sim_unix = Time.get_unix_time_from_system()
	if st.element_id == "element_water":
		st.wetness = 1.0
	_entities[entity_id] = st
	_positions[entity_id] = position
	return {"ok": true, "state": st.to_dict()}


func get_state(entity_id: String) -> Dictionary:
	if not _entities.has(entity_id):
		return {}
	return _entities[entity_id].to_dict()


func set_lod_tier(entity_id: String, tier: int) -> void:
	if not _entities.has(entity_id):
		return
	var st = _entities[entity_id]
	st.simulation_lod_tier = clampi(tier, 0, 3)


func list_entity_ids() -> PackedStringArray:
	var out := PackedStringArray()
	for k in _entities.keys():
		out.append(str(k))
	return out


## One simulation step. Preview entities skipped. Tier 3 uses wall-clock delta.
func simulate_step(now_unix: float = -1.0) -> Dictionary:
	if now_unix < 0.0:
		now_unix = Time.get_unix_time_from_system()
	var advanced: Array = []
	# 1) Water sources emit wetness to nearby soil
	for eid in _entities.keys():
		var st = _entities[eid]
		if st.preview_only or not st.simulates:
			continue
		if st.element_id != "element_water":
			continue
		var pos: Vector3 = _positions.get(eid, Vector3.ZERO)
		var emit_r := 8.0
		var emit_rate := 0.12
		var prof: Dictionary = _profiles.get("physical_profiles", {}).get("phys_water_v1", {})
		if prof.has("wetness_emit_radius_m"):
			emit_r = float(prof["wetness_emit_radius_m"])
		if prof.has("wetness_emit_rate"):
			emit_rate = float(prof["wetness_emit_rate"])
		for oid in _entities.keys():
			var other = _entities[oid]
			if other.preview_only or not other.simulates:
				continue
			if other.element_id != "element_soil":
				continue
			var op: Vector3 = _positions.get(oid, Vector3.ZERO)
			var d := pos.distance_to(op)
			if d <= emit_r:
				var dt := _dt_for(other, now_unix)
				other.wetness = clampf(other.wetness + emit_rate * dt * (1.0 - d / emit_r), 0.0, 1.0)

	# 2) Soil growth scales with wetness
	for eid in _entities.keys():
		var st = _entities[eid]
		if st.preview_only or not st.simulates:
			continue
		if st.element_id != "element_soil":
			continue
		var dt := _dt_for(st, now_unix)
		var growth_rate: float = 0.05 + 0.35 * float(st.wetness)
		# Scale by LOD: tier3 uses full wall dt already; near tiers step-sized
		st.growth = clampf(float(st.growth) + growth_rate * dt, 0.0, 1.0)
		st.last_sim_unix = now_unix
		advanced.append(st.to_dict())

	# Mark water last_sim
	for eid in _entities.keys():
		var st = _entities[eid]
		if st.simulates and not st.preview_only and st.element_id == "element_water":
			st.last_sim_unix = now_unix

	return {"ok": true, "advanced": advanced, "now": now_unix}


func _dt_for(st, now_unix: float) -> float:
	var last: float = float(st.last_sim_unix)
	if last <= 0.0:
		last = now_unix
	var wall := maxf(0.0, now_unix - last)
	# Tier 3: full wall-clock time-delta (idle unload reconstruction)
	if int(st.simulation_lod_tier) >= 3:
		return wall
	# Near tiers: clamp to short step so headless unit tests remain deterministic
	return minf(wall, 1.0) if wall > 0.0 else 0.016


## Build PersistModule mutation request for one entity (caller applies).
func build_durable_mutation(entity_id: String, request_id: String, expected_world_revision: int = 0) -> Dictionary:
	if not _entities.has(entity_id):
		return {"ok": false, "error": "missing_entity"}
	var st = _entities[entity_id]
	if st.preview_only:
		return {"ok": false, "error": "preview_not_durable"}
	var pos: Vector3 = _positions.get(entity_id, Vector3.ZERO)
	return {
		"ok": true,
		"request": {
			"schema_version": "1.0.0",
			"request_id": request_id,
			"mutation_class": "durable_world",
			"operation": "create",
			"expected_world_revision": expected_world_revision,
			"authority": {
				"context": "offline_private_reality",
				"source": "elemental_pilot_p1e004",
			},
			"confirmation": {"state": "confirmed"},
			"actor": {"actor_id": "player_01", "actor_type": "player"},
			"entity": {
				"entity_id": entity_id,
				"kind": "elemental_prop",
				"recipe_id": st.aidle_module_id,
				"transform": {
					"x": pos.x,
					"y": pos.z,
					"elevation": pos.y,
					"rotation_deg": 0,
				},
				"bounds": {"width": 2, "depth": 2, "height": 1},
				"interaction_tags": Array(st.to_interaction_tags()),
				"space_id": "private_reality",
				"chunk_id": "pilot_0_0",
			},
		},
	}


## Unload chunk: strip runtime, keep only durable-capable state snapshot for Tier-3.
func unload_chunk_snapshot() -> Dictionary:
	var snap: Dictionary = {}
	for eid in _entities.keys():
		var st = _entities[eid]
		if st.preview_only:
			continue
		snap[eid] = {
			"state": st.to_dict(),
			"position": {
				"x": _positions[eid].x,
				"y": _positions[eid].y,
				"z": _positions[eid].z,
			},
		}
	_entities.clear()
	_positions.clear()
	return snap


func reload_chunk_from_snapshot(snap: Dictionary, now_unix: float) -> Dictionary:
	_entities.clear()
	_positions.clear()
	for eid in snap.keys():
		var entry: Dictionary = snap[eid]
		var sd: Dictionary = entry.get("state", {})
		var st = load(STATE_SCRIPT).new()
		st.entity_id = str(eid)
		st.aidle_module_id = str(sd.get("aidle_module_id", ""))
		st.dna_module_id = str(sd.get("dna_module_id", ""))
		st.element_id = str(sd.get("element_id", ""))
		st.physical_profile_id = str(sd.get("physical_profile_id", ""))
		st.wetness = float(sd.get("wetness", 0))
		st.growth = float(sd.get("growth", 0))
		st.temperature = float(sd.get("temperature", 0.5))
		st.integrity = float(sd.get("integrity", 1))
		st.simulates = bool(sd.get("simulates", false))
		st.simulation_lod_tier = 3  # reloaded far chunk starts at tier3
		st.last_sim_unix = float(sd.get("last_sim_unix", now_unix))
		st.preview_only = false
		_entities[eid] = st
		var p: Dictionary = entry.get("position", {})
		_positions[eid] = Vector3(float(p.get("x", 0)), float(p.get("y", 0)), float(p.get("z", 0)))
	# Advance time-delta for unloaded period
	return simulate_step(now_unix)
