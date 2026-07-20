## Interface contract for Agent-Companion.
class_name ICompanionModule
extends RefCounted

## Expected methods:
## func spawn_companion(player: Node3D, mount: Node) -> void
## func set_emotional_state(mood: String) -> void
## func get_emotional_state() -> String
## func request_world_change(natural_language: String) -> void  # builds SWP → Executor only
##
## Rules:
## - Companion NEVER calls Voxel directly (Blueprint coordination).
## - Companion may only call Executor for world changes.
## - Emit emotional_state_changed + random_alchemist_gift on EventBus.

const REQUIRED_METHODS := [
	"spawn_companion",
	"set_emotional_state",
	"get_emotional_state",
]


static func validate(module: Object) -> PackedStringArray:
	var missing: PackedStringArray = []
	for m in REQUIRED_METHODS:
		if not module.has_method(m):
			missing.append(m)
	return missing
