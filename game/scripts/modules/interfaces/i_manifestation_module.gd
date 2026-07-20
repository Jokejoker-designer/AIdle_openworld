## Interface contract for Agent-Manifestation (2.5D progressive construction).
## Preferred surface for G2-002+; mirrors legacy IVoxelModule methods for mount
## compatibility while making stage/collision invariants explicit.
##
## Duck-typed. Register with ModuleRegistry using MODULE_VOXEL mount until a
## dedicated manifestation mount exists in WorldRoot.
class_name IManifestationModule
extends RefCounted

## Suggested signatures:
##
## func start_manifestation(prompt_id: String, art_style: String, geometry: Dictionary) -> bool
## func update_construction_progress(prompt_id: String, progress: float) -> void
## func finalize_manifestation(prompt_id: String) -> void
## func cancel_manifestation(prompt_id: String, reason: String) -> void
## func get_manifestation_stage(prompt_id: String) -> String
## func has_durable_collision(prompt_id: String) -> bool
## func set_skip_animation(enabled: bool) -> void
##
## Ordered stages (locked): wireframe → hologram → materializing → complete
## Preview / pre-complete stages MUST NOT enable durable collision.
## Cancel / abort MUST remove preview geometry and leave no collision.
##
## Emit via EventBus:
##   manifestation_started / progress_updated / completed / cancelled

const REQUIRED_METHODS := [
	"start_manifestation",
	"update_construction_progress",
	"finalize_manifestation",
	"cancel_manifestation",
	"get_manifestation_stage",
	"has_durable_collision",
]


static func validate(module: Object) -> PackedStringArray:
	var missing: PackedStringArray = []
	for m in REQUIRED_METHODS:
		if not module.has_method(m):
			missing.append(m)
	return missing
