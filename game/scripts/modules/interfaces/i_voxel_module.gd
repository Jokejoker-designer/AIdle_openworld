## Interface contract for Agent-Voxel (duck-typed).
## Implement these methods on your module root and register with ModuleRegistry.
class_name IVoxelModule
extends RefCounted

## Suggested method signatures (document only – GDScript duck typing):
##
## func start_manifestation(prompt_id: String, art_style: String, geometry: Dictionary) -> bool
## func update_construction_progress(prompt_id: String, progress: float) -> void
## func finalize_manifestation(prompt_id: String) -> void
## func cancel_manifestation(prompt_id: String, reason: String) -> void
##
## Mount: ModuleRegistry.attach_to_mount(AIdleConstants.MODULE_VOXEL, self)
## Host:  WorldRoot.get_manifestation_host(space_id)  # spawn progressive meshes here
##
## MUST emit via EventBus:
##   manifestation_started / progress_updated / completed / cancelled
## MUST NOT instant-spawn solid geometry (Blueprint hard constraint).

const REQUIRED_METHODS := [
	"start_manifestation",
	"update_construction_progress",
	"finalize_manifestation",
	"cancel_manifestation",
]


static func validate(module: Object) -> PackedStringArray:
	var missing: PackedStringArray = []
	for m in REQUIRED_METHODS:
		if not module.has_method(m):
			missing.append(m)
	return missing
