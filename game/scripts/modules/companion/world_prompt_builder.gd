## Builds Structured World Prompt *proposals* only.
## Never commits, never mutates SceneTree durable entities, never calls Voxel.
## Confirmation always starts as pending + preview_required=true.
class_name CompanionWorldPromptBuilder
extends RefCounted

const SCHEMA_VERSION := "1.1.0"
const MANIFESTATION_STAGES: Array = ["wireframe", "hologram", "materializing", "complete"]

## Recipe catalog for MVP text intents (no LLM required for deterministic export).
const RECIPES := {
	"cozy_house_small": {
		"kind": "modular_structure_2_5d",
		"operation": "create",
		"bounds": {"width": 8.0, "depth": 6.0, "height": 5.0},
		"interaction_tags": ["enterable", "lightable"],
		"max_compute_units": 200,
		"max_entities": 32,
		"presentation_duration_seconds": 12.0,
	},
	"garden_lamp": {
		"kind": "prop_2_5d",
		"operation": "create",
		"bounds": {"width": 1.0, "depth": 1.0, "height": 2.0},
		"interaction_tags": ["lightable", "pickable"],
		"max_compute_units": 40,
		"max_entities": 4,
		"presentation_duration_seconds": 6.0,
	},
	"tile_layer_floor": {
		"kind": "tile_layer",
		"operation": "create",
		"bounds": {"width": 4.0, "depth": 4.0, "height": 0.25},
		"interaction_tags": ["walkable"],
		"max_compute_units": 60,
		"max_entities": 8,
		"presentation_duration_seconds": 8.0,
	},
}


var player_id: String = "player_01"
var companion_id: String = "companion_lumi"
var session_id: String = "session_companion_01"
var space_type: String = "private_reality"
var space_id: String = "home_01"
var chunk_id: String = "0_0"
var expected_world_revision: int = 0
var style_profile_id: String = "cozy_default"
var style_profile_version: String = "1.0.0"
var base_concept: String = "cozy_cyber_pixel_2_5d"
var surrealism_budget: float = 0.15


func configure_context(ctx: Dictionary) -> void:
	if ctx.has("player_id"):
		player_id = str(ctx["player_id"])
	if ctx.has("companion_id"):
		companion_id = str(ctx["companion_id"])
	if ctx.has("session_id"):
		session_id = str(ctx["session_id"])
	if ctx.has("space_type"):
		space_type = str(ctx["space_type"])
	if ctx.has("space_id"):
		space_id = str(ctx["space_id"])
	if ctx.has("chunk_id"):
		chunk_id = str(ctx["chunk_id"])
	if ctx.has("expected_world_revision"):
		expected_world_revision = maxi(0, int(ctx["expected_world_revision"]))
	if ctx.has("style_profile_id"):
		style_profile_id = str(ctx["style_profile_id"])
	if ctx.has("base_concept"):
		base_concept = str(ctx["base_concept"])
	if ctx.has("surrealism_budget"):
		surrealism_budget = clampf(float(ctx["surrealism_budget"]), 0.0, 1.0)


## Map natural language (VI/EN MVP keywords) → recipe_id or "".
func detect_recipe(natural_language: String) -> String:
	var text := natural_language.strip_edges().to_lower()
	if text.is_empty():
		return ""
	if (
		"xây nhà" in text
		or "ngôi nhà" in text
		or "làm nhà" in text
		or "build house" in text
		or "cozy house" in text
		or "house" in text
	):
		return "cozy_house_small"
	if "đèn" in text or "lamp" in text or "garden lamp" in text:
		return "garden_lamp"
	if "sàn" in text or "floor" in text or "tile" in text:
		return "tile_layer_floor"
	return ""


## Build a schema-shaped proposal Dictionary. Always confirmation.state=pending.
func build_proposal(
	recipe_id: String,
	source_type: String = "player_request",
	transform: Dictionary = {},
	overrides: Dictionary = {}
) -> Dictionary:
	if not RECIPES.has(recipe_id):
		return {}
	var recipe: Dictionary = RECIPES[recipe_id]
	var op: String = str(overrides.get("operation", recipe.get("operation", "create")))
	var xform := {
		"x": float(transform.get("x", 8.0)),
		"y": float(transform.get("y", 6.0)),
		"elevation": float(transform.get("elevation", 0.0)),
		"rotation_deg": fposmod(float(transform.get("rotation_deg", 0.0)), 360.0),
	}
	# exclusiveMaximum 360 — keep away from 360.
	if is_equal_approx(xform["rotation_deg"], 360.0):
		xform["rotation_deg"] = 0.0

	var prompt_id := _new_uuid()
	var request_id := _new_uuid()
	var created_at := Time.get_datetime_string_from_system(true, true)
	# Prefer RFC3339 Z suffix for schema date-time fixtures.
	if not created_at.ends_with("Z") and "+" not in created_at:
		created_at = created_at.replace(" ", "T")
		if not created_at.ends_with("Z"):
			created_at += "Z"

	var bounds: Dictionary = (recipe["bounds"] as Dictionary).duplicate(true)
	if overrides.has("bounds") and overrides["bounds"] is Dictionary:
		bounds = (overrides["bounds"] as Dictionary).duplicate(true)

	var tags: Array = []
	for t in recipe.get("interaction_tags", []):
		tags.append(str(t))

	var proposal := {
		"schema_version": SCHEMA_VERSION,
		"prompt_id": prompt_id,
		"request_id": request_id,
		"session_id": session_id,
		"actor": {"player_id": player_id, "companion_id": companion_id},
		"operation": op,
		"target": {
			"space_type": space_type,
			"space_id": space_id,
			"chunk_id": chunk_id,
			"expected_world_revision": expected_world_revision,
		},
		"style_profile": {
			"profile_id": style_profile_id,
			"profile_version": style_profile_version,
			"base_concept": base_concept,
			"surrealism_budget": surrealism_budget,
		},
		"entity": {
			"kind": str(recipe["kind"]),
			"recipe_id": recipe_id,
			"transform": xform,
			"bounds": {
				"width": float(bounds.get("width", 1.0)),
				"depth": float(bounds.get("depth", 1.0)),
				"height": float(bounds.get("height", 1.0)),
			},
			"interaction_tags": tags,
		},
		"manifestation": {
			"stages": MANIFESTATION_STAGES.duplicate(),
			"presentation_duration_seconds": float(
				recipe.get("presentation_duration_seconds", 12.0)
			),
		},
		"budget": {
			"max_compute_units": int(recipe.get("max_compute_units", 100)),
			"max_entities": int(recipe.get("max_entities", 16)),
			"paid_compute_allowed": false,
		},
		"provenance": {
			"source_type": source_type,
			"requested_by": player_id if source_type == "player_request" else companion_id,
			"generated_by": companion_id,
			"created_at": created_at,
		},
		"confirmation": {
			"preview_required": true,
			"state": "pending",
			"rollback_window_seconds": 3600,
		},
	}

	if overrides.has("entity_id"):
		proposal["target"]["entity_id"] = str(overrides["entity_id"])
	if overrides.has("parent_prompt_id"):
		proposal["provenance"]["parent_prompt_id"] = str(overrides["parent_prompt_id"])

	return proposal


func build_from_natural_language(natural_language: String) -> Dictionary:
	var recipe_id := detect_recipe(natural_language)
	if recipe_id.is_empty():
		return {}
	return build_proposal(recipe_id, "player_request")


## Gift proposal (companion enrichment / alchemist) — still pending, never committed here.
func build_gift_proposal(recipe_id: String = "garden_lamp") -> Dictionary:
	if not RECIPES.has(recipe_id):
		recipe_id = "garden_lamp"
	var p := build_proposal(recipe_id, "random_alchemist", {"x": 10.0, "y": 8.0})
	if p.is_empty():
		return p
	p["operation"] = "gift_proposal"
	p["provenance"]["source_type"] = "random_alchemist"
	p["provenance"]["requested_by"] = companion_id
	return p


## Project an AGM Decision Envelope build_proposal item into a pending World Prompt.
## Never confirms or commits. Always preview_required + state=pending.
## provenance.source_type uses companion_enrichment (AGM is Companion brain; not durable).
func build_from_agm_build_proposal(agm_item: Dictionary, meta: Dictionary = {}) -> Dictionary:
	if agm_item.is_empty():
		return {}
	# Hard authority: AGM cannot pre-confirm or bypass preview.
	if agm_item.get("preview_required") != true:
		return {}
	if str(agm_item.get("confirmation_state", "")) != "pending":
		return {}
	if str(agm_item.get("routes_through", "")) != "preview_confirm_commit":
		return {}

	var recipe_id := str(agm_item.get("recipe_id", "")).strip_edges()
	if recipe_id.is_empty():
		return {}

	var transform: Dictionary = {}
	if agm_item.get("transform") is Dictionary:
		transform = (agm_item["transform"] as Dictionary).duplicate(true)

	# Prefer space/chunk from AGM item when present.
	var prev_space := space_id
	var prev_chunk := chunk_id
	var prev_session := session_id
	if agm_item.has("space_id") and str(agm_item["space_id"]).strip_edges() != "":
		space_id = str(agm_item["space_id"])
	if agm_item.has("chunk_id") and str(agm_item["chunk_id"]).strip_edges() != "":
		chunk_id = str(agm_item["chunk_id"])
	if meta.has("session_id") and str(meta["session_id"]).strip_edges() != "":
		session_id = str(meta["session_id"])

	var op := str(agm_item.get("operation", "create"))
	var overrides := {"operation": op}
	# If recipe is known, use catalog bounds/kind; else synthesize from entity_kind.
	var proposal: Dictionary
	if RECIPES.has(recipe_id):
		proposal = build_proposal(recipe_id, "companion_enrichment", transform, overrides)
	else:
		proposal = _build_unknown_recipe_from_agm(recipe_id, agm_item, transform, op)

	# Restore context (per-call overrides must not leak).
	space_id = prev_space
	chunk_id = prev_chunk
	session_id = prev_session

	if proposal.is_empty():
		return {}

	# Force pending confirmation (never trust AGM confirmation_state beyond gate above).
	proposal["confirmation"] = {
		"preview_required": true,
		"state": "pending",
		"rollback_window_seconds": 3600,
	}
	proposal["operation"] = op
	proposal["provenance"]["source_type"] = "companion_enrichment"
	proposal["provenance"]["requested_by"] = companion_id
	proposal["provenance"]["generated_by"] = companion_id
	if meta.has("model_receipt_ref") and str(meta["model_receipt_ref"]).strip_edges() != "":
		proposal["provenance"]["model_receipt_ref"] = str(meta["model_receipt_ref"])

	# Align entity.kind with AGM when provided and valid.
	var entity_kind := str(agm_item.get("entity_kind", ""))
	if entity_kind != "" and proposal.has("entity") and proposal["entity"] is Dictionary:
		# Only override if AGM kind is allowlisted-ish (builder catalog may already match).
		proposal["entity"]["kind"] = entity_kind
		proposal["entity"]["recipe_id"] = recipe_id

	return proposal


func _build_unknown_recipe_from_agm(
	recipe_id: String,
	agm_item: Dictionary,
	transform: Dictionary,
	op: String
) -> Dictionary:
	# Minimal SWP for recipes not in local catalog — still pending, no commit.
	var kind := str(agm_item.get("entity_kind", "prop_2_5d"))
	var xform := {
		"x": float(transform.get("x", 8.0)),
		"y": float(transform.get("y", 6.0)),
		"elevation": float(transform.get("elevation", 0.0)),
		"rotation_deg": fposmod(float(transform.get("rotation_deg", 0.0)), 360.0),
	}
	if is_equal_approx(float(xform["rotation_deg"]), 360.0):
		xform["rotation_deg"] = 0.0
	var created_at := Time.get_datetime_string_from_system(true, true)
	if not created_at.ends_with("Z") and "+" not in created_at:
		created_at = created_at.replace(" ", "T")
		if not created_at.ends_with("Z"):
			created_at += "Z"
	return {
		"schema_version": SCHEMA_VERSION,
		"prompt_id": _new_uuid(),
		"request_id": _new_uuid(),
		"session_id": session_id,
		"actor": {"player_id": player_id, "companion_id": companion_id},
		"operation": op,
		"target": {
			"space_type": space_type,
			"space_id": space_id,
			"chunk_id": chunk_id,
			"expected_world_revision": expected_world_revision,
		},
		"style_profile": {
			"profile_id": style_profile_id,
			"profile_version": style_profile_version,
			"base_concept": base_concept,
			"surrealism_budget": surrealism_budget,
		},
		"entity": {
			"kind": kind,
			"recipe_id": recipe_id,
			"transform": xform,
			"bounds": {"width": 1.0, "depth": 1.0, "height": 1.0},
			"interaction_tags": [],
		},
		"manifestation": {
			"stages": MANIFESTATION_STAGES.duplicate(),
			"presentation_duration_seconds": 10.0,
		},
		"budget": {
			"max_compute_units": 100,
			"max_entities": 16,
			"paid_compute_allowed": false,
		},
		"provenance": {
			"source_type": "companion_enrichment",
			"requested_by": companion_id,
			"generated_by": companion_id,
			"created_at": created_at,
		},
		"confirmation": {
			"preview_required": true,
			"state": "pending",
			"rollback_window_seconds": 3600,
		},
	}


## Tool surface enumeration for audits: proposal-only, no commit/mutate.
static func list_tools() -> Array:
	return [
		{
			"name": "propose_world_prompt",
			"description": "Build a schema-valid World Prompt proposal (pending confirmation).",
			"mutates_world": false,
			"commits": false,
		},
		{
			"name": "propose_from_text",
			"description": "Map player text intent to a pending World Prompt proposal.",
			"mutates_world": false,
			"commits": false,
		},
		{
			"name": "propose_gift",
			"description": "Build a random_alchemist gift_proposal (still pending).",
			"mutates_world": false,
			"commits": false,
		},
		{
			"name": "apply_agm_decision",
			"description": "Consume validated AGM Decision Envelope dialogue + pending build proposals.",
			"mutates_world": false,
			"commits": false,
		},
		{
			"name": "inspect_personality",
			"description": "Show how adaptive traits drift (plain language + caps).",
			"mutates_world": false,
			"commits": false,
		},
		{
			"name": "lock_trait",
			"description": "Lock a personality trait against adaptation.",
			"mutates_world": false,
			"commits": false,
		},
		{
			"name": "reset_personality",
			"description": "Reset adaptive traits to base.",
			"mutates_world": false,
			"commits": false,
		},
		{
			"name": "delete_adaptation_history",
			"description": "Delete adaptation history and inferred prefs.",
			"mutates_world": false,
			"commits": false,
		},
	]


static func has_commit_tool() -> bool:
	for t in list_tools():
		if bool(t.get("commits", false)) or bool(t.get("mutates_world", false)):
			return true
		var n := str(t.get("name", "")).to_lower()
		if "commit" in n or "mutate" in n or "durable" in n:
			return true
	return false


func _new_uuid() -> String:
	# RFC4122-ish v4 from RNG (good enough for local proposals; not crypto).
	var b := PackedByteArray()
	b.resize(16)
	for i in 16:
		b[i] = randi() % 256
	b[6] = (b[6] & 0x0f) | 0x40
	b[8] = (b[8] & 0x3f) | 0x80
	var hex := b.hex_encode()
	return "%s-%s-%s-%s-%s" % [
		hex.substr(0, 8),
		hex.substr(8, 4),
		hex.substr(12, 4),
		hex.substr(16, 4),
		hex.substr(20, 12),
	]
