## Interface contract for Agent-Executor (World Engine).
class_name IExecutorModule
extends RefCounted

## Expected methods:
## func submit_prompt(structured_world_prompt: Dictionary) -> String  # returns prompt_id or ""
## func cancel_prompt(prompt_id: String, reason: String) -> void
## func get_prompt_status(prompt_id: String) -> Dictionary
##
## Flow: Companion/System → Schema.validate → Executor → Voxel (+ Asset)
## Authority must be respected per RealitySpace.

const REQUIRED_METHODS := [
	"submit_prompt",
	"cancel_prompt",
	"get_prompt_status",
]


static func validate(module: Object) -> PackedStringArray:
	var missing: PackedStringArray = []
	for m in REQUIRED_METHODS:
		if not module.has_method(m):
			missing.append(m)
	return missing
