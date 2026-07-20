## Interface contract for Agent-Network.
class_name INetworkModule
extends RefCounted

## Expected methods:
## func start_session(mode: String) -> void  # offline | listen | client
## func sync_manifestation_progress(prompt_id: String, progress: float, stage: String) -> void
## func sync_emotional_aura(companion_id: String, mood: String, color: Color) -> void
##
## Authority:
## - private_reality: client-authoritative (optional invite sync)
## - shared_district / doppelganger_city: server-authoritative
## - spacecraft / exoplanet: owner-authoritative + grants

const REQUIRED_METHODS := [
	"start_session",
	"sync_manifestation_progress",
]


static func validate(module: Object) -> PackedStringArray:
	var missing: PackedStringArray = []
	for m in REQUIRED_METHODS:
		if not module.has_method(m):
			missing.append(m)
	return missing
