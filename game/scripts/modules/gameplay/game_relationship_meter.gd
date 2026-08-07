## Relationship & adaptation meter — Companion Personality and Voice spec (Blueprint 07).
##
## Implements bounded adaptation: relationship levels unlock dialogue/story
## beats and NEVER economic pressure or authority. Adaptive deltas are EMA-based
## with per-turn/per-day caps and clamp radius around base traits (values taken
## from the blueprint's recommended initial caps, marked as hypotheses until
## play-tested).
##
## RefCounted, headless-safe; a Node wrapper publishes signals when mounted.
class_name GameRelationshipMeter
extends RefCounted

const TRAITS := ["warmth", "curiosity", "calmness", "humor", "protectiveness"]

const PER_TURN_CAP := 0.005
const PER_DAY_CAP := 0.03
const RADIUS_FROM_BASELINE := 0.25
const HALF_LIFE_DAYS := 30.0

const LEVEL_NAMES := ["acquaintance", "friend", "close_friend", "kindred_spirit", "soul_companion"]
const LEVEL_THRESHOLDS := [0, 10, 25, 45, 70]

var _base_traits: Dictionary = {}
var _current_traits: Dictionary = {}
var _level: int = 0
var _points: int = 0
var _mood: String = "calm"
var _day_change: Dictionary = {}
var _history: Array = []

func _init(base_traits: Dictionary = {}) -> void:
	for t in TRAITS:
		var v := float(base_traits.get(t, 0.5))
		v = clampf(v, 0.0, 1.0)
		_base_traits[t] = v
		_current_traits[t] = v

func get_traits() -> Dictionary:
	return _current_traits.duplicate(true)

func get_base_traits() -> Dictionary:
	return _base_traits.duplicate(true)

func get_mood() -> String:
	return _mood

## Relationship progression from accepted Companion quests / proposals.
## Level thresholds unlock dialogue beats only (blueprint §Relationship Context).
func add_points(amount: int, reason: String = "interaction") -> Dictionary:
	if amount <= 0:
		return {"ok": false, "reason": "points must be positive"}
	_points += int(amount)
	var new_level := _level_for(_points)
	var leveled_up := new_level > _level
	_level = new_level
	_history.append({"type": "points", "amount": amount, "reason": reason, "level": _level, "at": _now_iso()})
	var beats := []
	if leveled_up:
		beats = ["level_%d_%s" % [_level, LEVEL_NAMES[_level]]]
	return {"ok": true, "points": _points, "level": _level, "level_name": LEVEL_NAMES[_level], "leveled_up": leveled_up, "beats": beats}

func remove_points(amount: int, reason: String = "rejection") -> Dictionary:
	if amount <= 0:
		return {"ok": false, "reason": "amount must be positive"}
	_points = maxi(0, _points - int(amount))
	_level = _level_for(_points)
	_history.append({"type": "points", "amount": -amount, "reason": reason, "level": _level, "at": _now_iso()})
	return {"ok": true, "points": _points, "level": _level, "level_name": LEVEL_NAMES[_level]}

func _level_for(pts: int) -> int:
	var lvl := 0
	for i in range(LEVEL_THRESHOLDS.size()):
		if pts >= LEVEL_THRESHOLDS[i]:
			lvl = i
	return lvl

## Bounded adaptive drift (blueprint drift algorithm):
## - ema per turn capped at PER_TURN_CAP,
## - daily total capped at PER_DAY_CAP,
## - clamped within RADIUS_FROM_BASELINE of base traits.
func adapt(trait_name: String, delta: float, evidence: Dictionary = {}) -> Dictionary:
	if trait_name not in TRAITS:
		return {"ok": false, "reason": "unknown_trait"}
	delta = float(delta)
	delta = clampf(delta, -PER_TURN_CAP, PER_TURN_CAP)
	var day_total := float(_day_change.get(trait_name, 0.0))
	if absf(day_total + delta) > PER_DAY_CAP:
		delta = signf(delta) * (PER_DAY_CAP - absf(day_total))
		if absf(delta) < 1e-6:
			return {"ok": false, "reason": "daily_cap_reached", "trait": trait_name}
	var base := float(_base_traits[trait_name])
	var cur := float(_current_traits[trait_name])
	var candidate := cur + delta
	candidate = clampf(candidate, base - RADIUS_FROM_BASELINE, base + RADIUS_FROM_BASELINE)
	_current_traits[trait_name] = candidate
	_day_change[trait_name] = day_total + (candidate - cur)
	_history.append({"type": "adapt", "trait": trait_name, "delta": candidate - cur, "evidence": evidence, "at": _now_iso()})
	return {"ok": true, "trait": trait_name, "value": candidate}

## New day: reset daily drift accumulator + decay weak adaptations toward
## baseline (half-life HALF_LIFE_DAYS, decay factor per day).
func advance_day() -> void:
	_day_change = {}
	var decay_factor := pow(0.5, 1.0 / HALF_LIFE_DAYS)
	for t in TRAITS:
		var base := float(_base_traits[t])
		var cur := float(_current_traits[t])
		_current_traits[t] = base + (cur - base) * decay_factor

## Mood is the situational expression layer (short-lived, not durable unless
## the player consents to storing it).
func set_mood(mood: String) -> Dictionary:
	_mood = str(mood).strip_edges()
	return {"ok": true, "mood": _mood}

## Dialogue unlock gate: relationship level must reach at least
## `required_level` (0-based) to expose a dialogue beat.
func can_unlock_beat(required_level: int) -> bool:
	return _level >= int(required_level)

func snapshot() -> Dictionary:
	return {
		"level": _level,
		"level_name": LEVEL_NAMES[_level],
		"points": _points,
		"mood": _mood,
		"traits": _current_traits.duplicate(true),
		"base_traits": _base_traits.duplicate(true),
		"history_size": _history.size(),
	}

func reset_to_base_traits() -> void:
	for t in TRAITS:
		_current_traits[t] = float(_base_traits[t])
	_day_change = {}

func _now_iso() -> String:
	return Time.get_datetime_string_from_system(true)
