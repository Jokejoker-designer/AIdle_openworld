## Bounded companion personality (contracts/personality_profile.schema.json).
## Slow drift caps: max_delta_per_turn / max_delta_per_day / max_distance_from_base.
## Player controls: inspect, lock, reset, delete. Text-only MVP — no voice.
class_name CompanionPersonalityProfile
extends RefCounted

const SCHEMA_VERSION := "1.0.0"
const TRAIT_KEYS: PackedStringArray = [
	"warmth",
	"curiosity",
	"calmness",
	"humor",
	"supportive_guardianship",
	"precision",
	"brevity",
	"initiative",
]

## Schema caps (hard ceilings from personality_profile.schema.json).
const CAP_MAX_DELTA_PER_TURN := 0.005
const CAP_MAX_DELTA_PER_DAY := 0.03
const CAP_MAX_DISTANCE_FROM_BASE := 0.25
const CAP_SUPPORTIVE_GUARDIANSHIP_MAX := 0.7

signal profile_changed(reason: String)
signal adaptation_applied(trait_name: String, before: float, after: float, evidence: Dictionary)
signal control_applied(action: String, detail: Dictionary)

var companion_id: String = "companion_lumi"
var privacy_mode: String = "session_only"
var revision: int = 0

var base_traits: Dictionary = {}
var adaptive_traits: Dictionary = {}
var adaptation_policy: Dictionary = {}

## Per-session bookkeeping for turn/day caps.
var _turn_deltas: Dictionary = {}
var _day_deltas: Dictionary = {}
var _day_key: String = ""
var _delta_log: Array = []
var _suppressed_inferences: PackedStringArray = []


func _init(p_companion_id: String = "companion_lumi") -> void:
	companion_id = p_companion_id
	reset_to_defaults()


func reset_to_defaults() -> void:
	base_traits = _default_base_traits()
	adaptive_traits = base_traits.duplicate(true)
	adaptation_policy = {
		"enabled": true,
		"max_delta_per_turn": CAP_MAX_DELTA_PER_TURN,
		"max_delta_per_day": CAP_MAX_DELTA_PER_DAY,
		"max_distance_from_base": CAP_MAX_DISTANCE_FROM_BASE,
		"minimum_observations": 3,
		"minimum_independent_sessions": 3,
		"minimum_confidence": 0.65,
		"locked_traits": [],
	}
	_turn_deltas.clear()
	_day_deltas.clear()
	_day_key = _today_key()
	revision = 0
	profile_changed.emit("reset_to_defaults")


## Full profile dict matching personality_profile.schema.json.
func to_dict() -> Dictionary:
	return {
		"schema_version": SCHEMA_VERSION,
		"companion_id": companion_id,
		"base_traits": base_traits.duplicate(true),
		"adaptive_traits": adaptive_traits.duplicate(true),
		"adaptation_policy": adaptation_policy.duplicate(true),
		"privacy_mode": privacy_mode,
		"revision": revision,
	}


func from_dict(data: Dictionary) -> PackedStringArray:
	var errors: PackedStringArray = []
	if str(data.get("schema_version", "")) != SCHEMA_VERSION:
		errors.append("schema_version must be %s" % SCHEMA_VERSION)
	if data.has("companion_id"):
		companion_id = str(data["companion_id"])
	if data.has("privacy_mode"):
		var pm := str(data["privacy_mode"])
		if pm in ["session_only", "local_durable", "account_sync"]:
			privacy_mode = pm
		else:
			errors.append("invalid privacy_mode")
	if data.has("base_traits") and data["base_traits"] is Dictionary:
		base_traits = _sanitize_traits(data["base_traits"] as Dictionary, true)
	if data.has("adaptive_traits") and data["adaptive_traits"] is Dictionary:
		adaptive_traits = _sanitize_traits(data["adaptive_traits"] as Dictionary, false)
		_clamp_adaptive_to_base()
	if data.has("adaptation_policy") and data["adaptation_policy"] is Dictionary:
		_merge_policy(data["adaptation_policy"] as Dictionary)
	if data.has("revision"):
		revision = maxi(0, int(data["revision"]))
	return errors


## Plain-language inspect for player controls ("how I adapt to you").
func inspect_plain_language() -> String:
	var lines: PackedStringArray = []
	lines.append("Companion: %s (rev %d, privacy=%s)" % [companion_id, revision, privacy_mode])
	var enabled: bool = bool(adaptation_policy.get("enabled", false))
	lines.append("Adaptation: %s" % ("on" if enabled else "off (locked by player)"))
	lines.append(
		"Caps: turn≤%.3f day≤%.3f distance≤%.2f"
		% [
			float(adaptation_policy.get("max_delta_per_turn", CAP_MAX_DELTA_PER_TURN)),
			float(adaptation_policy.get("max_delta_per_day", CAP_MAX_DELTA_PER_DAY)),
			float(adaptation_policy.get("max_distance_from_base", CAP_MAX_DISTANCE_FROM_BASE)),
		]
	)
	var locked: Array = adaptation_policy.get("locked_traits", []) as Array
	if locked.is_empty():
		lines.append("Locked traits: (none)")
	else:
		lines.append("Locked traits: %s" % ", ".join(PackedStringArray(locked)))
	lines.append("Traits (base → adaptive):")
	for key in TRAIT_KEYS:
		var b: float = float(base_traits.get(key, 0.0))
		var a: float = float(adaptive_traits.get(key, b))
		var delta: float = a - b
		lines.append("  %s: base=%.3f adaptive=%.3f (Δ%+.3f)" % [key, b, a, delta])
	if _delta_log.is_empty():
		lines.append("Recent accepted deltas: (none)")
	else:
		lines.append("Recent accepted deltas (up to 5):")
		var start: int = maxi(0, _delta_log.size() - 5)
		for i in range(start, _delta_log.size()):
			var e: Dictionary = _delta_log[i]
			lines.append(
				"  %s %s: %.3f→%.3f conf=%.2f (%s)"
				% [
					str(e.get("timestamp", "")),
					str(e.get("trait", "")),
					float(e.get("before", 0.0)),
					float(e.get("after", 0.0)),
					float(e.get("confidence", 0.0)),
					str(e.get("reason", "")),
				]
			)
	return "\n".join(lines)


func inspect() -> Dictionary:
	return {
		"profile": to_dict(),
		"plain_language": inspect_plain_language(),
		"turn_deltas_used": _turn_deltas.duplicate(true),
		"day_deltas_used": _day_deltas.duplicate(true),
		"day_key": _day_key,
		"delta_log_size": _delta_log.size(),
		"suppressed_inferences": Array(_suppressed_inferences),
	}


func lock_trait(trait_name: String) -> bool:
	if not _is_trait(trait_name):
		return false
	var locked: Array = adaptation_policy.get("locked_traits", []) as Array
	if trait_name not in locked:
		locked.append(trait_name)
		adaptation_policy["locked_traits"] = locked
		revision += 1
		control_applied.emit("lock", {"trait": trait_name})
		profile_changed.emit("lock_trait")
	return true


func unlock_trait(trait_name: String) -> bool:
	if not _is_trait(trait_name):
		return false
	var locked: Array = adaptation_policy.get("locked_traits", []) as Array
	if trait_name in locked:
		locked.erase(trait_name)
		adaptation_policy["locked_traits"] = locked
		revision += 1
		control_applied.emit("unlock", {"trait": trait_name})
		profile_changed.emit("unlock_trait")
	return true


func set_adaptation_enabled(enabled: bool) -> void:
	adaptation_policy["enabled"] = enabled
	revision += 1
	control_applied.emit("set_adaptation_enabled", {"enabled": enabled})
	profile_changed.emit("set_adaptation_enabled")


func reset_adaptive_to_base() -> void:
	adaptive_traits = base_traits.duplicate(true)
	_turn_deltas.clear()
	_day_deltas.clear()
	revision += 1
	control_applied.emit("reset", {"scope": "adaptive_to_base"})
	profile_changed.emit("reset_adaptive_to_base")


## Delete adaptation history / inferred prefs (keeps base traits).
func delete_adaptation_history() -> void:
	_delta_log.clear()
	_turn_deltas.clear()
	_day_deltas.clear()
	_suppressed_inferences.clear()
	adaptive_traits = base_traits.duplicate(true)
	revision += 1
	control_applied.emit("delete", {"scope": "adaptation_history"})
	profile_changed.emit("delete_adaptation_history")


func suppress_inference(tag: String) -> void:
	if tag.is_empty():
		return
	if tag not in _suppressed_inferences:
		_suppressed_inferences.append(tag)
		control_applied.emit("suppress_inference", {"tag": tag})


## Apply a signed evidence sample in [-1, 1] with confidence.
## Returns applied delta (0 if rejected by caps/policy).
func apply_observation(
	trait_name: String,
	signed_evidence: float,
	confidence: float,
	reason: String = "",
	observation_count: int = 1,
	independent_sessions: int = 1,
	inference_tag: String = ""
) -> float:
	_roll_day_if_needed()
	if not bool(adaptation_policy.get("enabled", false)):
		return 0.0
	if not _is_trait(trait_name):
		return 0.0
	var locked: Array = adaptation_policy.get("locked_traits", []) as Array
	if trait_name in locked:
		return 0.0
	if inference_tag != "" and inference_tag in _suppressed_inferences:
		return 0.0

	var min_obs: int = int(adaptation_policy.get("minimum_observations", 3))
	var min_sess: int = int(adaptation_policy.get("minimum_independent_sessions", 3))
	var min_conf: float = float(adaptation_policy.get("minimum_confidence", 0.65))
	if observation_count < min_obs or independent_sessions < min_sess:
		return 0.0
	if confidence < min_conf:
		return 0.0

	var evidence: float = clampf(signed_evidence, -1.0, 1.0)
	var conf: float = clampf(confidence, 0.0, 1.0)
	var max_turn: float = minf(
		float(adaptation_policy.get("max_delta_per_turn", CAP_MAX_DELTA_PER_TURN)),
		CAP_MAX_DELTA_PER_TURN
	)
	var max_day: float = minf(
		float(adaptation_policy.get("max_delta_per_day", CAP_MAX_DELTA_PER_DAY)),
		CAP_MAX_DELTA_PER_DAY
	)
	var max_dist: float = minf(
		float(adaptation_policy.get("max_distance_from_base", CAP_MAX_DISTANCE_FROM_BASE)),
		CAP_MAX_DISTANCE_FROM_BASE
	)

	# Desired raw step scaled by confidence, then hard-capped per turn.
	var desired: float = evidence * conf * max_turn
	var used_turn: float = float(_turn_deltas.get(trait_name, 0.0))
	var remain_turn: float = max_turn - absf(used_turn)
	if remain_turn <= 0.0:
		return 0.0
	var step: float = clampf(desired, -remain_turn, remain_turn)

	var used_day: float = float(_day_deltas.get(trait_name, 0.0))
	var remain_day: float = max_day - absf(used_day)
	if remain_day <= 0.0:
		return 0.0
	step = clampf(step, -remain_day, remain_day)

	var base_v: float = float(base_traits.get(trait_name, 0.5))
	var before: float = float(adaptive_traits.get(trait_name, base_v))
	var after: float = before + step
	# Clamp to [base - max_dist, base + max_dist] and trait range.
	after = clampf(after, base_v - max_dist, base_v + max_dist)
	after = _clamp_trait_value(trait_name, after)
	step = after - before
	if is_zero_approx(step):
		return 0.0

	adaptive_traits[trait_name] = after
	_turn_deltas[trait_name] = used_turn + step
	_day_deltas[trait_name] = used_day + step
	revision += 1

	var entry := {
		"trait": trait_name,
		"before": before,
		"after": after,
		"confidence": conf,
		"reason": reason,
		"timestamp": Time.get_datetime_string_from_system(true, true),
		"algorithm_version": "personality_drift_v1",
		"evidence_category": "player_feedback",
	}
	_delta_log.append(entry)
	adaptation_applied.emit(trait_name, before, after, entry)
	profile_changed.emit("adaptation")
	return step


func begin_turn() -> void:
	_turn_deltas.clear()
	_roll_day_if_needed()


func get_effective_trait(trait_name: String) -> float:
	if not _is_trait(trait_name):
		return 0.0
	return float(adaptive_traits.get(trait_name, base_traits.get(trait_name, 0.0)))


func _default_base_traits() -> Dictionary:
	return {
		"warmth": 0.72,
		"curiosity": 0.68,
		"calmness": 0.70,
		"humor": 0.45,
		"supportive_guardianship": 0.55,
		"precision": 0.60,
		"brevity": 0.40,
		"initiative": 0.50,
	}


func _is_trait(name: String) -> bool:
	return name in TRAIT_KEYS


func _clamp_trait_value(trait_name: String, value: float) -> float:
	if trait_name == "supportive_guardianship":
		return clampf(value, 0.0, CAP_SUPPORTIVE_GUARDIANSHIP_MAX)
	return clampf(value, 0.0, 1.0)


func _sanitize_traits(src: Dictionary, is_base: bool) -> Dictionary:
	var out := _default_base_traits() if is_base else base_traits.duplicate(true)
	for key in TRAIT_KEYS:
		if src.has(key):
			out[key] = _clamp_trait_value(key, float(src[key]))
	return out


func _clamp_adaptive_to_base() -> void:
	var max_dist: float = minf(
		float(adaptation_policy.get("max_distance_from_base", CAP_MAX_DISTANCE_FROM_BASE)),
		CAP_MAX_DISTANCE_FROM_BASE
	)
	for key in TRAIT_KEYS:
		var base_v: float = float(base_traits.get(key, 0.5))
		var a: float = float(adaptive_traits.get(key, base_v))
		a = clampf(a, base_v - max_dist, base_v + max_dist)
		adaptive_traits[key] = _clamp_trait_value(key, a)


func _merge_policy(src: Dictionary) -> void:
	if src.has("enabled"):
		adaptation_policy["enabled"] = bool(src["enabled"])
	if src.has("max_delta_per_turn"):
		adaptation_policy["max_delta_per_turn"] = clampf(
			float(src["max_delta_per_turn"]), 0.0, CAP_MAX_DELTA_PER_TURN
		)
	if src.has("max_delta_per_day"):
		adaptation_policy["max_delta_per_day"] = clampf(
			float(src["max_delta_per_day"]), 0.0, CAP_MAX_DELTA_PER_DAY
		)
	if src.has("max_distance_from_base"):
		adaptation_policy["max_distance_from_base"] = clampf(
			float(src["max_distance_from_base"]), 0.0, CAP_MAX_DISTANCE_FROM_BASE
		)
	if src.has("minimum_observations"):
		adaptation_policy["minimum_observations"] = clampi(int(src["minimum_observations"]), 3, 100)
	if src.has("minimum_independent_sessions"):
		adaptation_policy["minimum_independent_sessions"] = clampi(
			int(src["minimum_independent_sessions"]), 3, 30
		)
	if src.has("minimum_confidence"):
		adaptation_policy["minimum_confidence"] = clampf(float(src["minimum_confidence"]), 0.65, 1.0)
	if src.has("locked_traits") and src["locked_traits"] is Array:
		var cleaned: Array = []
		for t in src["locked_traits"]:
			var name := str(t)
			if _is_trait(name) and name not in cleaned:
				cleaned.append(name)
		adaptation_policy["locked_traits"] = cleaned


func _today_key() -> String:
	var dt := Time.get_datetime_dict_from_system(true)
	return "%04d-%02d-%02d" % [int(dt.year), int(dt.month), int(dt.day)]


func _roll_day_if_needed() -> void:
	var today := _today_key()
	if today != _day_key:
		_day_key = today
		_day_deltas.clear()
