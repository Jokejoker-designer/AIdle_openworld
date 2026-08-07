## Append-only day journal — blueprint provenance invariant:
## "append-only lineage; corrections append a new record".
##
## Records daily beats (quests completed, gifts accepted, weather moods,
## relationship milestones) as an append-only log per in-game day. Used by the
## AGM snapshot (bounded recent memory) and by the day-end summary UI.
## RefCounted, headless-safe.
class_name GameDayJournal
extends RefCounted

var _entries: Array = []
var _sequence: int = 0

func record(day: int, category: String, summary: String, meta: Dictionary = {}) -> Dictionary:
	_sequence += 1
	var entry := {
		"seq": _sequence,
		"day": int(day),
		"category": str(category),
		"summary": str(summary),
		"meta": meta.duplicate(true),
		"at": _now_iso(),
	}
	_entries.append(entry)
	return {"ok": true, "seq": _sequence}

func entries_for_day(day: int) -> Array:
	var out: Array = []
	for e in _entries:
		if int(e.get("day", 0)) == int(day):
			out.append(e.duplicate(true))
	return out

## Bounded recent memory for the AGM snapshot (blueprint: snapshots contain
## bounded recent conversation and summaries, not unrestricted history).
func recent_memories(max_entries: int = 20) -> Array:
	var out: Array = []
	for e in _entries.slice(max(-1, _entries.size() - max_entries)):
		out.append(e.duplicate(true))
	return out

## User privacy: inspect/delete history entries (blueprint memory controls).
func delete_entries(since_seq: int) -> Dictionary:
	var removed := 0
	for i in range(_entries.size() - 1, -1, -1):
		if int(_entries[i].get("seq", 0)) >= int(since_seq):
			_entries.remove_at(i)
			removed += 1
	return {"ok": true, "removed": removed}

func size() -> int:
	return _entries.size()

func _now_iso() -> String:
	return Time.get_datetime_string_from_system(true)
