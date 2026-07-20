## Interface contract for Agent-Companion (G2-003 AGM-driven, text-only MVP).
class_name ICompanionModule
extends RefCounted

## Expected methods:
## func spawn_companion(player: Node3D, mount: Node) -> void
## func set_emotional_state(mood: String) -> void
## func get_emotional_state() -> String
## func request_world_change(natural_language: String) -> void  # builds SWP proposal only
##
## AGM Decision Envelope (G2-003 rework):
## func apply_agm_decision(envelope: Dictionary) -> Dictionary
##   - Consumes validated AGM dialogue + build_proposals (pending World Prompts only).
##   - Rejects replayed decision_id, forbidden fields (TTS/voice/secrets/code/commit).
##   - Never commits durable world state.
##
## Proposal / personality (G2-003):
## func propose_from_text(natural_language: String) -> Dictionary
## func propose_world_prompt(recipe_id: String, transform: Dictionary = {}) -> Dictionary
## func get_last_proposal() -> Dictionary
## func list_tools() -> Array  # must not include commit/durable-mutate
## func has_commit_tool() -> bool  # must return false
## func inspect_personality() -> Dictionary
## func inspect_personality_text() -> String
## func lock_trait(trait_name: String) -> bool
## func reset_personality() -> void
## func delete_adaptation_history() -> void
##
## Rules:
## - Companion NEVER calls Voxel directly (Blueprint coordination).
## - Companion may hand proposals to Executor.submit_prompt; never commits durable state.
## - AGM is untrusted until validated; Companion projects dialogue + pending proposals only.
## - No STT / TTS / mic / voice models on MVP critical path.
## - Emit emotional_state_changed + random_alchemist_gift on EventBus.

const REQUIRED_METHODS := [
	"spawn_companion",
	"set_emotional_state",
	"get_emotional_state",
	"request_world_change",
	"apply_agm_decision",
	"propose_from_text",
	"list_tools",
	"has_commit_tool",
	"inspect_personality",
	"lock_trait",
	"reset_personality",
	"delete_adaptation_history",
]

const FORBIDDEN_TOOL_NAME_FRAGMENTS := [
	"commit",
	"durable_mutate",
	"mutate_world",
	"write_world",
	"scene_tree_mutate",
]


static func validate(module: Object) -> PackedStringArray:
	var missing: PackedStringArray = []
	for m in REQUIRED_METHODS:
		if not module.has_method(m):
			missing.append(m)
	return missing


## Audit tool surface: any tool marked commits/mutates_world or named like commit fails.
static func audit_no_commit_tools(module: Object) -> PackedStringArray:
	var issues: PackedStringArray = []
	if module.has_method("has_commit_tool") and bool(module.call("has_commit_tool")):
		issues.append("has_commit_tool() returned true")
	if not module.has_method("list_tools"):
		issues.append("list_tools missing")
		return issues
	var tools: Variant = module.call("list_tools")
	if typeof(tools) != TYPE_ARRAY:
		issues.append("list_tools did not return Array")
		return issues
	for t in tools:
		if typeof(t) != TYPE_DICTIONARY:
			continue
		var d: Dictionary = t
		var name := str(d.get("name", "")).to_lower()
		if bool(d.get("commits", false)):
			issues.append("tool commits=true: %s" % name)
		if bool(d.get("mutates_world", false)):
			issues.append("tool mutates_world=true: %s" % name)
		for frag in FORBIDDEN_TOOL_NAME_FRAGMENTS:
			if frag in name:
				issues.append("forbidden tool name fragment '%s' in %s" % [frag, name])
	return issues
