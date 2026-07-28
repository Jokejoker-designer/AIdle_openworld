## WO-P1E-004 thin pilot state — adapted from DNA elemental_state.gd (first-execution).
## NOT a wholesale import of aidle_elemental_physics. No class_name (headless -s safe).
## Durable fields encode into interaction_tags for existing PersistModule path.
extends RefCounted

var entity_id: String = ""
var aidle_module_id: String = ""
var dna_module_id: String = ""
var element_id: String = ""
var physical_profile_id: String = ""
var temperature: float = 0.5
var wetness: float = 0.0
var integrity: float = 1.0
var growth: float = 0.0
var simulates: bool = false
## 0 near … 3 far / unloaded time-delta
var simulation_lod_tier: int = 0
## Wall-clock seconds last simulated (for Tier-3 reconstruction)
var last_sim_unix: float = 0.0
var preview_only: bool = false


func clamp_values() -> void:
	temperature = clampf(temperature, 0.0, 1.0)
	wetness = clampf(wetness, 0.0, 1.0)
	integrity = clampf(integrity, 0.0, 1.0)
	growth = clampf(growth, 0.0, 1.0)
	simulation_lod_tier = clampi(simulation_lod_tier, 0, 3)


## Encode into PersistModule-safe interaction_tags (entity hasher drops unknown keys).
func to_interaction_tags() -> PackedStringArray:
	clamp_values()
	var tags: PackedStringArray = PackedStringArray()
	tags.append("elemental_pilot_v1")
	tags.append("aidle:%s" % aidle_module_id)
	tags.append("dna:%s" % dna_module_id)
	tags.append("element:%s" % element_id)
	tags.append("profile:%s" % physical_profile_id)
	tags.append("wetness:%.4f" % wetness)
	tags.append("growth:%.4f" % growth)
	tags.append("temp:%.4f" % temperature)
	tags.append("integrity:%.4f" % integrity)
	tags.append("sim:%s" % ("1" if simulates else "0"))
	tags.append("lod:%d" % simulation_lod_tier)
	tags.append("last_sim:%.3f" % last_sim_unix)
	if preview_only:
		tags.append("preview_only")
	return tags


static func from_interaction_tags(entity_id_in: String, tags: Array) -> RefCounted:
	var st = load("res://scripts/modules/elemental/elemental_state.gd").new()
	st.entity_id = entity_id_in
	for t in tags:
		var s := str(t)
		if s.begins_with("aidle:"):
			st.aidle_module_id = s.substr(6)
		elif s.begins_with("dna:"):
			st.dna_module_id = s.substr(4)
		elif s.begins_with("element:"):
			st.element_id = s.substr(8)
		elif s.begins_with("profile:"):
			st.physical_profile_id = s.substr(8)
		elif s.begins_with("wetness:"):
			st.wetness = float(s.substr(8))
		elif s.begins_with("growth:"):
			st.growth = float(s.substr(7))
		elif s.begins_with("temp:"):
			st.temperature = float(s.substr(5))
		elif s.begins_with("integrity:"):
			st.integrity = float(s.substr(10))
		elif s.begins_with("sim:"):
			st.simulates = s.substr(4) == "1"
		elif s.begins_with("lod:"):
			st.simulation_lod_tier = int(s.substr(4))
		elif s.begins_with("last_sim:"):
			st.last_sim_unix = float(s.substr(9))
		elif s == "preview_only":
			st.preview_only = true
	st.clamp_values()
	return st


func to_dict() -> Dictionary:
	clamp_values()
	return {
		"entity_id": entity_id,
		"aidle_module_id": aidle_module_id,
		"dna_module_id": dna_module_id,
		"element_id": element_id,
		"physical_profile_id": physical_profile_id,
		"temperature": temperature,
		"wetness": wetness,
		"integrity": integrity,
		"growth": growth,
		"simulates": simulates,
		"simulation_lod_tier": simulation_lod_tier,
		"last_sim_unix": last_sim_unix,
		"preview_only": preview_only,
	}
