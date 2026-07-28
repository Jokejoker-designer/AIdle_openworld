## Pure stage machine for progressive 2.5D manifestation.
## Stages are monotonic and locked to world_prompt.schema.json:
##   wireframe → hologram → materializing → complete
## No scene-tree dependency — safe for headless unit/smoke tests.
class_name ManifestationStages
extends RefCounted

const ORDERED_STAGES: PackedStringArray = [
	"wireframe",
	"hologram",
	"materializing",
	"complete",
]

## Progress bands mapped to stages (inclusive lower bound).
## 0.00–0.25 wireframe | 0.25–0.50 hologram | 0.50–0.90 materializing | 0.90–1.0 complete
const STAGE_THRESHOLDS := {
	"wireframe": 0.0,
	"hologram": 0.25,
	"materializing": 0.5,
	"complete": 0.9,
}


static func is_valid_stage(stage: String) -> bool:
	return ORDERED_STAGES.has(stage)


static func stage_index(stage: String) -> int:
	return ORDERED_STAGES.find(stage)


static func stage_at_or_before(a: String, b: String) -> bool:
	## True if stage a is the same as or earlier than stage b in ORDERED_STAGES.
	var ia := stage_index(a)
	var ib := stage_index(b)
	if ia < 0 or ib < 0:
		return false
	return ia <= ib


static func can_advance(from_stage: String, to_stage: String) -> bool:
	## Progress is monotonic: only equal or later stages allowed.
	var from_i := stage_index(from_stage)
	var to_i := stage_index(to_stage)
	if from_i < 0 or to_i < 0:
		return false
	return to_i >= from_i


static func next_stage(current: String) -> String:
	var i := stage_index(current)
	if i < 0:
		return ORDERED_STAGES[0]
	if i >= ORDERED_STAGES.size() - 1:
		return ORDERED_STAGES[ORDERED_STAGES.size() - 1]
	return ORDERED_STAGES[i + 1]


static func stage_for_progress(progress: float) -> String:
	var p := clampf(progress, 0.0, 1.0)
	if p >= float(STAGE_THRESHOLDS["complete"]):
		return "complete"
	if p >= float(STAGE_THRESHOLDS["materializing"]):
		return "materializing"
	if p >= float(STAGE_THRESHOLDS["hologram"]):
		return "hologram"
	return "wireframe"


static func progress_for_stage(stage: String) -> float:
	## Representative progress at stage entry (for EventBus reporting).
	match stage:
		"wireframe":
			return 0.0
		"hologram":
			return 0.25
		"materializing":
			return 0.5
		"complete":
			return 1.0
		_:
			return 0.0


static func allows_durable_collision(stage: String) -> bool:
	## Preview stages never create durable collision authority.
	return stage == "complete"


static func visual_opacity(stage: String) -> float:
	## Headed stages must be object-distinct (U4 UI skill correction).
	match stage:
		"wireframe":
			return 0.18
		"hologram":
			return 0.5
		"materializing":
			return 0.82
		"complete":
			return 1.0
		_:
			return 0.18


static func visual_emission_energy(stage: String) -> float:
	match stage:
		"wireframe":
			return 0.7
		"hologram":
			return 1.8
		"materializing":
			return 0.55
		"complete":
			return 0.0
		_:
			return 0.7


static func stage_display_label(stage: String) -> String:
	## Plain-language stage name + non-color pattern cue (never color alone).
	match stage:
		"wireframe":
			return "Wireframe · outline"
		"hologram":
			return "Hologram · glow"
		"materializing":
			return "Materializing · solidifying"
		"complete":
			return "Complete · solid"
		_:
			return "Building · %s" % stage


static func stage_pattern_glyph(stage: String) -> String:
	## Distinct glyph per stage so state is readable without color.
	match stage:
		"wireframe":
			return "▢"
		"hologram":
			return "◈"
		"materializing":
			return "▣"
		"complete":
			return "■"
		_:
			return "·"


static func is_ordered_sequence(stages: PackedStringArray) -> bool:
	## True when stages appear in monotonic ORDERED_STAGES order (subset allowed).
	var last_i := -1
	for s in stages:
		var i := stage_index(str(s))
		if i < 0:
			return false
		if i < last_i:
			return false
		last_i = i
	return stages.size() > 0


static func enforce_monotonic(current: String, requested: String) -> String:
	## Clamp requested stage so it never regresses.
	if not is_valid_stage(requested):
		return current if is_valid_stage(current) else ORDERED_STAGES[0]
	if not is_valid_stage(current):
		return requested
	if can_advance(current, requested):
		return requested
	return current
