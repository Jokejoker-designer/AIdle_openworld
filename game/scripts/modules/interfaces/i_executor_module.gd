## Interface contract for Agent-Executor (World Engine + AGM Decision executor).
## G2-006: deterministic allowlisted Decision Envelope execution, decision_id
## idempotency, build proposals via preview → confirm → commit handoff stub.
class_name IExecutorModule
extends RefCounted

## World Prompt path (Companion / System):
## func submit_prompt(structured_world_prompt: Dictionary) -> String  # prompt_id or ""
## func cancel_prompt(prompt_id: String, reason: String) -> void
## func get_prompt_status(prompt_id: String) -> Dictionary
## func confirm_prompt(prompt_id: String, confirmed_by: String = "player_01") -> Dictionary
##
## AGM Decision path (G2-006):
## func execute_decision(decision: Dictionary, live_snapshot: Dictionary = {}) -> Dictionary
## func get_execution_receipt(decision_id: String) -> Dictionary
## func get_last_execution_receipt() -> Dictionary
## func get_snapshot_execution_receipt(decision_id: String = "") -> Dictionary
## func set_live_snapshot(snapshot: Dictionary) -> void
## func has_seen_decision(decision_id: String) -> bool
## func list_allowlisted_event_types() -> PackedStringArray
##
## Flow: AGM Decision → allowlist validate → soft effects + build preview handoffs
##       Companion SWP → submit_prompt → preview → confirm_prompt → commit stub
## Authority: World Commit service is sole durable mutator (handoff may be stubbed).

const REQUIRED_METHODS := [
	"submit_prompt",
	"cancel_prompt",
	"get_prompt_status",
	"execute_decision",
	"get_execution_receipt",
	"confirm_prompt",
	"has_seen_decision",
]


static func validate(module: Object) -> PackedStringArray:
	var missing: PackedStringArray = []
	for m in REQUIRED_METHODS:
		if not module.has_method(m):
			missing.append(m)
	return missing
