## Resource ledger for the AIdle cozy 2.5D vertical slice.
## Implements the "Cost Validate" stage of the blueprint core loop:
## `Speak -> ... -> Policy/Cost/Schema Validate -> Preview -> Human Confirm -> ...`
##
## Contract invariants (binding with Master Blueprint v1.1):
## - Preview stages never create economy/ownership effect (costs are only
##   checked/deducted on confirmed commits, never on previews).
## - Balance checks are atomic with the mutation: a commit only succeeds if the
##   ledger approved the cost in the same call; no "built but unpaid" state.
## - Ledger history is an append-only provenance log (corrections append, never
##   delete) and is exported by the snapshot API for the AGM.
## - AI surprise is opt-in and never spends for the player: only explicit
##   earn/spend paths exist; no auto-deduction.
##
## RefCounted + standalone (headless-safe). A Node wrapper mounts it into the
## scene tree and wires UI signals when present.
class_name GameEconomy
extends RefCounted

const RESOURCES := {
	"coin": 0,
	"wood": 0,
	"stone": 0,
	"food": 0,
	"spirit": 0,
}

const RECIPE_COSTS := {
	"cozy_house_small_A": {"coin": 120, "wood": 40, "stone": 20},
	"cozy_greenhouse_preview_anchor_A": {"coin": 60, "wood": 25, "stone": 5},
	"cozy_pond_small_A": {"coin": 40, "wood": 10, "stone": 8},
	"cozy_fence_section_A": {"coin": 8, "wood": 6, "stone": 2},
	"cozy_garden_lamp": {"coin": 15, "wood": 4, "stone": 3},
	"cozy_tile_layer_A": {"coin": 5, "wood": 2, "stone": 4},
}

const DAILY_INCOME := {"coin": 10, "food": 2}
const MAX_SPIRIT := 100
const SPIRIT_REGEN_PER_HOUR := 8.0

var _balance: Dictionary = {}
var _spirit: float = 50.0
var _day: int = 1
var _hour: float = 6.0
var _log: Array = []
var _sequence: int = 0

func _init(initial: Dictionary = {}) -> void:
	for res in RESOURCES.keys():
		_balance[res] = int(initial.get(res, RESOURCES[res]))
	_spirit = float(clampf(initial.get("spirit", 50.0), 0.0, MAX_SPIRIT))

func get_balance() -> Dictionary:
	return _balance.duplicate(true)

func get_spirit() -> float:
	return _spirit

func get_balance_of(resource: String) -> int:
	if not _balance.has(resource):
		return 0
	return _balance[resource]

func can_afford(cost: Dictionary) -> Dictionary:
	if not (cost is Dictionary) or cost.is_empty():
		return {"ok": true, "code": "free_action", "details": cost}
	for res in cost:
		var amount := int(cost[res])
		if not _balance.has(str(res)):
			return {"ok": false, "code": "unknown_resource", "resource": str(res)}
		if amount < 0:
			return {"ok": false, "code": "negative_cost", "resource": str(res)}
		if _balance[str(res)] < amount:
			return {"ok": false, "code": "insufficient", "resource": str(res), "have": _balance[str(res)], "need": amount}
	return {"ok": true, "code": "affordable", "details": cost}

## Atomic cost check-then-deduct. Returns the ledger entry id when approved.
## No partial deduction ever occurs: if any resource is insufficient, the
## whole transaction fails and balances remain untouched.
func approve_spend(cost: Dictionary, spend_reason: String = "commit") -> Dictionary:
	if not (cost is Dictionary):
		return {"ok": false, "code": "cost_not_a_dictionary"}
	var check := can_afford(cost)
	if not check.get("ok", false):
		return check
	_sequence += 1
	for res in cost:
		_balance[str(res)] -= int(cost[res])
	var entry := {
		"seq": _sequence,
		"type": "spend",
		"reason": spend_reason,
		"amounts": cost.duplicate(true),
		"balances_after": _balance.duplicate(true),
		"at": _utcnow_iso(),
	}
	_log.append(entry)
	return {"ok": true, "code": "approved", "entry": entry}

func grant_income(amounts: Dictionary, earn_reason: String = "income") -> Dictionary:
	if not (amounts is Dictionary) or amounts.is_empty():
		return {"ok": false, "code": "empty_income"}
	for res in amounts:
		if not _balance.has(str(res)):
			return {"ok": false, "code": "unknown_resource", "resource": str(res)}
		var amount := int(amounts[res])
		if amount <= 0:
			return {"ok": false, "code": "non_positive_income"}
		_balance[str(res)] += amount
	_sequence += 1
	var entry := {
		"seq": _sequence,
		"type": "earn",
		"reason": earn_reason,
		"amounts": amounts.duplicate(true),
		"balances_after": _balance.duplicate(true),
		"at": _utcnow_iso(),
	}
	_log.append(entry)
	return {"ok": true, "code": "granted", "entry": entry}

## Correct a ledger mistake by appending a compensating entry. History is
## never erased (blueprint provenance invariant).
func compensate(entry_seq: int, amounts: Dictionary, reason: String = "compensation") -> Dictionary:
	var found := false
	for e in _log:
		if int(e.get("seq", -1)) == int(entry_seq):
			found = true
			break
	if not found:
		return {"ok": false, "code": "unknown_entry", "seq": entry_seq}
	var refund := {}
	for res in amounts:
		if not _balance.has(str(res)):
			return {"ok": false, "code": "unknown_resource", "resource": str(res)}
		refund[str(res)] = int(amounts[res])
		_balance[str(res)] += refund[str(res)]
	_sequence += 1
	_log.append({
		"seq": _sequence,
		"type": "compensation",
		"corrects": entry_seq,
		"reason": reason,
		"amounts": refund,
		"balances_after": _balance.duplicate(true),
		"at": _utcnow_iso(),
	})
	return {"ok": true, "code": "compensated", "balances_after": _balance.duplicate(true)}

## Per-day cycle hook: daily income + spirit regen. Idempotent per day number.
var _last_income_day: int = 0
func advance_day_income() -> Dictionary:
	if _day <= _last_income_day:
		return {"ok": false, "code": "day_already_credited", "day": _day}
	_last_income_day = _day
	var income := DAILY_INCOME.duplicate(true)
	var res := grant_income(income, "daily_income_day_%d" % _day)
	if not res.get("ok", false):
		return res
	_spirit = float(clampf(_spirit + SPIRIT_REGEN_PER_HOUR * 24.0, 0.0, MAX_SPIRIT))
	return res

func spend_spirit(amount: float) -> Dictionary:
	if amount < 0.0 or amount > MAX_SPIRIT:
		return {"ok": false, "code": "invalid_spirit_amount"}
	if _spirit < amount:
		return {"ok": false, "code": "insufficient_spirit", "have": _spirit, "need": amount}
	_spirit = float(clampf(_spirit - amount, 0.0, MAX_SPIRIT))
	return {"ok": true, "code": "spent", "spirit": _spirit}

func regen_spirit_for_hours(hours: float) -> void:
	_spirit = float(clampf(_spirit + SPIRIT_REGEN_PER_HOUR * float(hours), 0.0, MAX_SPIRIT))

## Time-of-day state. Hours: 0..24.
func set_hour(hour: float) -> void:
	_hour = float(clampf(hour, 0.0, 24.0))
	if _hour < 6.0:
		_day += 1
		_last_income_day = 0  # re-arm daily income for the new day (caller decides when to credit)

func get_hour() -> float:
	return _hour

func get_day() -> int:
	return _day

func time_of_day_label() -> String:
	if _hour >= 6.0 and _hour < 12.0:
		return "morning"
	if _hour >= 12.0 and _hour < 17.0:
		return "afternoon"
	if _hour >= 17.0 and _hour < 20.0:
		return "evening"
	return "night"

## Recipe lookup for build costs. Unknown recipes are free (preview-only
## modules) — never an error, but the caller may treat an empty cost as
## "informational only".
func cost_for(recipe_id: String) -> Dictionary:
	if RECIPE_COSTS.has(recipe_id):
		return RECIPE_COSTS[recipe_id].duplicate(true)
	return {}

## Snapshot for the AGM World State Snapshot (bounded, no secrets).
func snapshot() -> Dictionary:
	return {
		"day": _day,
		"hour": _hour,
		"time_of_day": time_of_day_label(),
		"balance": _balance.duplicate(true),
		"spirit": _spirit,
		"last_entry_seq": _sequence,
		"entries_since_day_start": _log.size() - _last_entry_day_index(),
	}

func _last_entry_day_index() -> int:
	var idx := 0
	for i in range(_log.size()):
		if str(_log[i].get("reason", "")).begins_with("daily_income_day_%d" % _day):
			idx = i
	return idx

func ledger_export(max_entries: int = 200) -> Array:
	var out: Array = []
	for e in _log.slice(max(-1, _log.size() - max_entries)):
		out.append(e.duplicate(true))
	return out

func _utcnow_iso() -> String:
	return Time.get_datetime_string_from_system(true)
