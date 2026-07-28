## Builds schema-valid World Prompt proposals from validated Block Assembly placement.
## Adapter may only emit STRUCTURED_WORLD_PROMPT_PROPOSAL (pending, preview_required).
## Never confirms, commits, or claims client success.
class_name BlockWorldPromptBuilder
extends RefCounted

const _C = preload("res://scripts/modules/block_assembly/block_assembly_constants.gd")
const _Canon = preload("res://scripts/modules/persist/canonical_json.gd")
const _Hasher = preload("res://scripts/modules/persist/entity_hasher.gd")


static func payload_fingerprint(payload: Dictionary) -> String:
	return _Hasher.sha256_hex(_Canon.stringify(payload))


static func make_request_uuid(seed: String, counter: int) -> String:
	## Deterministic UUID-shaped id for offline POC (no crypto secrets).
	var h := _Hasher.sha256_hex("%s|%d" % [seed, counter])
	return "%s-%s-%s-%s-%s" % [
		h.substr(0, 8),
		h.substr(8, 4),
		"4" + h.substr(13, 3),
		"8" + h.substr(17, 3),
		h.substr(20, 12),
	]


static func build_create_prompt(
	request_id: String,
	prompt_id: String,
	player_id: String,
	space_id: String,
	expected_rev: int,
	module_id: String,
	placement: Dictionary,
	material_slot: String,
	p1e_material_id: String,
	world_profile: String,
	idempotency_key: String,
	payload_fp: String
) -> Dictionary:
	return {
		"schema_version": "1.1.0",
		"prompt_id": prompt_id,
		"request_id": request_id,
		"session_id": "session_block_assembly",
		"actor": {"player_id": player_id, "companion_id": "companion_lumi"},
		"operation": "create",
		"target": {
			"space_type": "private_reality",
			"space_id": space_id,
			"chunk_id": "0_0",
			"expected_world_revision": expected_rev,
		},
		"style_profile": {
			"profile_id": world_profile,
			"profile_version": "1.0.0",
			"base_concept": "block_assembly_2_5d",
			"surrealism_budget": 0.15,
		},
		"entity": {
			"kind": "modular_structure_2_5d",
			"recipe_id": "block:%s" % module_id,
			"transform": {
				"x": float(placement.get("x", 0.0)),
				"y": float(placement.get("y", 0.0)),
				"elevation": float(placement.get("elevation", 0.0)),
				"rotation_deg": float(placement.get("rotation_deg", 0.0)),
			},
			"bounds": {"width": 1.0, "depth": 1.0, "height": 1.0},
			"interaction_tags": ["block_assembly", "preview_gated"],
			"material_slot": material_slot,
			"p1e_material_id": p1e_material_id,
			"module_id": module_id,
		},
		"manifestation": {
			"stages": Array(_C.MANIFESTATION_STAGES),
			"presentation_duration_seconds": 8,
		},
		"budget": {
			"max_compute_units": 200,
			"max_entities": 32,
			"paid_compute_allowed": false,
		},
		"provenance": {
			"source_type": "player_request",
			"requested_by": player_id,
			"generated_by": "block_assembly_controller",
			"created_at": "2026-07-22T00:00:00Z",
			"contract_id": _C.CONTRACT_ID,
			"idempotency_key": idempotency_key,
			"payload_fingerprint": payload_fp,
		},
		"confirmation": {
			"preview_required": true,
			"state": "pending",
			"rollback_window_seconds": 3600,
		},
	}


static func build_commit_request(
	request_id: String,
	prompt_id: String,
	actor_id: String,
	actor_type: String,
	space_id: String,
	expected_rev: int
) -> Dictionary:
	return {
		"schema_version": "1.0.0",
		"request_id": request_id,
		"prompt_id": prompt_id,
		"space_id": space_id,
		"expected_world_revision": expected_rev,
		"mutation_class": "world_prompt_commit",
		"actor": {"actor_id": actor_id, "actor_type": actor_type},
		"authority": {
			"commit_path": "world_commit_service",
			"source": "server_authoritative",
		},
		"confirmation": {
			"state": "confirmed",
			"confirmed_by": actor_id,
		},
		"trace_id": "trace-p2e-%s" % request_id.substr(0, mini(8, request_id.length())),
	}


static func build_delete_compensation_prompt(
	request_id: String,
	prompt_id: String,
	player_id: String,
	space_id: String,
	expected_rev: int,
	entity_id: String
) -> Dictionary:
	## Undo = compensation through authority path (delete op), not SceneTree erase.
	return {
		"schema_version": "1.1.0",
		"prompt_id": prompt_id,
		"request_id": request_id,
		"session_id": "session_block_assembly",
		"actor": {"player_id": player_id, "companion_id": "companion_lumi"},
		"operation": "delete",
		"target": {
			"space_type": "private_reality",
			"space_id": space_id,
			"chunk_id": "0_0",
			"entity_id": entity_id,
			"expected_world_revision": expected_rev,
		},
		"style_profile": {
			"profile_id": "cozy_cyber_pixel",
			"profile_version": "1.0.0",
			"base_concept": "block_assembly_compensation",
			"surrealism_budget": 0.0,
		},
		"entity": {
			"kind": "modular_structure_2_5d",
			"recipe_id": "compensation_delete",
			"transform": {"x": 0, "y": 0, "elevation": 0, "rotation_deg": 0},
			"bounds": {"width": 1, "depth": 1, "height": 1},
			"interaction_tags": ["compensation"],
		},
		"manifestation": {
			"stages": Array(_C.MANIFESTATION_STAGES),
			"presentation_duration_seconds": 1,
		},
		"budget": {
			"max_compute_units": 50,
			"max_entities": 1,
			"paid_compute_allowed": false,
		},
		"provenance": {
			"source_type": "player_request",
			"requested_by": player_id,
			"generated_by": "block_assembly_undo_compensation",
			"created_at": "2026-07-22T00:00:00Z",
			"mutation_class": "compensation_request",
		},
		"confirmation": {
			"preview_required": true,
			"state": "pending",
			"rollback_window_seconds": 3600,
		},
	}


static func placement_payload(
	module_id: String,
	placement: Dictionary,
	material_slot: String,
	p1e_material_id: String,
	world_profile: String
) -> Dictionary:
	return {
		"module_id": module_id,
		"placement": {
			"x": float(placement.get("x", 0.0)),
			"y": float(placement.get("y", 0.0)),
			"elevation": float(placement.get("elevation", 0.0)),
			"rotation_deg": float(placement.get("rotation_deg", 0.0)),
		},
		"material_slot": material_slot,
		"p1e_material_id": p1e_material_id,
		"world_profile": world_profile,
	}
