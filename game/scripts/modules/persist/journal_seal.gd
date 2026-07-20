## Journal integrity seals — HMAC-SHA256 over aidle_journal_seal_material_v1.
## Local Offline Private Reality reconciliation evidence only — NOT server / Shared District authority.
## Built-in Godot Crypto + HashingContext only (no third-party crypto).
class_name AIdleJournalSeal
extends RefCounted

const _Canon = preload("res://scripts/modules/persist/canonical_json.gd")
const _Hasher = preload("res://scripts/modules/persist/entity_hasher.gd")

const SEAL_ALG := "hmac-sha256"
const SEAL_HEX_RE_LEN := 64
const SCHEMA_VERSION := "1.0.0"
const SPACE_TYPE := "private_reality"


static func hmac_sha256_hex(key: PackedByteArray, message_utf8: String) -> String:
	if key.is_empty():
		return ""
	var crypto := Crypto.new()
	var msg: PackedByteArray = message_utf8.to_utf8_buffer()
	var digest: PackedByteArray = crypto.hmac_digest(HashingContext.HASH_SHA256, key, msg)
	return _to_hex_lower(digest)


static func _to_hex_lower(bytes: PackedByteArray) -> String:
	var out := ""
	for b in bytes:
		out += "%02x" % b
	return out


static func is_valid_seal_hex(s: String) -> bool:
	if s.length() != SEAL_HEX_RE_LEN:
		return false
	for i in s.length():
		var c: String = s[i]
		var ok_c: bool = (c >= "0" and c <= "9") or (c >= "a" and c <= "f")
		if not ok_c:
			return false
	return true


## Constant-time-ish hex compare (length mismatch fails fast).
static func seals_equal(a: String, b: String) -> bool:
	if a.length() != b.length():
		return false
	var diff: int = 0
	for i in a.length():
		diff |= a.unicode_at(i) ^ b.unicode_at(i)
	return diff == 0


static func build_genesis_material(
	space_id: String,
	journal_id: String,
	base_world_revision: int,
	base_snapshot_id: String
) -> Dictionary:
	return {
		"kind": "journal_genesis",
		"schema_version": SCHEMA_VERSION,
		"space_type": SPACE_TYPE,
		"space_id": space_id,
		"journal_id": journal_id,
		"base_world_revision": base_world_revision,
		"base_snapshot_id": base_snapshot_id if base_snapshot_id != null else "",
	}


static func compute_genesis_prev_seal(
	key: PackedByteArray,
	space_id: String,
	journal_id: String,
	base_world_revision: int,
	base_snapshot_id: String
) -> String:
	var material: Dictionary = build_genesis_material(
		space_id, journal_id, base_world_revision, base_snapshot_id
	)
	var msg: String = _Canon.stringify(material)
	return hmac_sha256_hex(key, msg)


## Strip seal output fields before payload hash / seal material construction.
static func entry_without_seals(entry: Dictionary) -> Dictionary:
	var out: Dictionary = entry.duplicate(true)
	out.erase("seal")
	out.erase("seal_alg")
	# Keep sequence_index and prev_seal in body (they bind order); seal is the MAC output.
	return out


static func entry_payload_hash(entry: Dictionary) -> String:
	var body: Dictionary = entry_without_seals(entry)
	# Payload hash binds full entry body including sequence_index/prev_seal, excluding seal outputs.
	body.erase("seal")
	body.erase("seal_alg")
	return _Hasher.sha256_hex(_Canon.stringify(body))


static func build_seal_material(
	entry: Dictionary,
	prev_seal: String,
	sequence_index: int,
	space_id: String,
	journal_id: String
) -> Dictionary:
	var et: String = str(entry.get("entry_type", ""))
	var material: Dictionary = {
		"schema_version": SCHEMA_VERSION,
		"space_type": SPACE_TYPE,
		"space_id": space_id,
		"journal_id": journal_id,
		"sequence_index": sequence_index,
		"prev_seal": prev_seal,
		"world_revision": int(entry.get("new_world_revision", 0)),
		"old_world_revision": int(entry.get("old_world_revision", 0)),
		"entry_type": et,
		"entry_id": str(entry.get("entry_id", "")),
		"request_id": str(entry.get("request_id", "")),
		"receipt_id": str(entry.get("receipt_id", "")),
		"mutation_class": str(entry.get("mutation_class", "")),
		"entry_payload_hash": entry_payload_hash(entry),
	}
	if et == "mutation_applied":
		var eids: Array = []
		if entry.has("entity_ids"):
			for x in entry["entity_ids"]:
				eids.append(str(x))
		eids = _Canon.sorted_unique_strings(eids)
		material["operation"] = str(entry.get("operation", ""))
		material["entity_ids"] = eids
		material["entity_delta"] = entry.get("entity_delta", {})
	elif et == "compensation":
		var cids: Array = []
		if entry.has("compensated_entity_ids"):
			for x in entry["compensated_entity_ids"]:
				cids.append(str(x))
		cids = _Canon.sorted_unique_strings(cids)
		material["prior_receipt_id"] = str(entry.get("prior_receipt_id", ""))
		material["prior_request_id"] = str(entry.get("prior_request_id", ""))
		material["compensated_entity_ids"] = cids
		material["entity_delta"] = entry.get("entity_delta", {})
		material["history_erased"] = false
	return material


static func compute_entry_seal(
	key: PackedByteArray,
	entry_without_seal: Dictionary,
	prev_seal: String,
	sequence_index: int,
	space_id: String,
	journal_id: String
) -> Dictionary:
	if key.is_empty():
		return {"ok": false, "error": "empty key", "error_code": "key_provider_missing"}
	if prev_seal.is_empty() or not is_valid_seal_hex(prev_seal):
		return {"ok": false, "error": "invalid prev_seal", "error_code": "journal_integrity_invalid"}
	var material: Dictionary = build_seal_material(
		entry_without_seal, prev_seal, sequence_index, space_id, journal_id
	)
	var msg: String = _Canon.stringify(material)
	var seal: String = hmac_sha256_hex(key, msg)
	if not is_valid_seal_hex(seal):
		return {"ok": false, "error": "seal compute failed", "error_code": "journal_integrity_invalid"}
	return {
		"ok": true,
		"seal": seal,
		"prev_seal": prev_seal,
		"sequence_index": sequence_index,
		"seal_alg": SEAL_ALG,
		"seal_material": material,
	}


## Verify full chain. env is journal envelope dictionary. Does not mutate env.
## Returns { ok, head_seal?, entry_count?, world_revision?, error_code?, error?, broken_at_index? }
static func verify_chain(key: PackedByteArray, env: Dictionary) -> Dictionary:
	if key.is_empty():
		return {
			"ok": false,
			"error_code": "key_provider_missing",
			"error": "key provider missing or empty key",
		}
	if env.is_empty():
		return {"ok": false, "error_code": "no_journal", "error": "empty envelope"}

	var space_id: String = str(env.get("space_id", ""))
	var journal_id: String = str(env.get("journal_id", ""))
	var base_rev: int = int(env.get("base_world_revision", 0))
	var base_snap: String = str(env.get("base_snapshot_id", ""))
	var genesis: String = compute_genesis_prev_seal(key, space_id, journal_id, base_rev, base_snap)

	if not env.has("entries") or not (env["entries"] is Array):
		return {
			"ok": false,
			"error_code": "journal_integrity_invalid",
			"error": "entries missing",
		}

	var entries: Array = env["entries"]
	var integrity = env.get("integrity", null)
	var has_integrity_meta: bool = integrity is Dictionary and bool((integrity as Dictionary).get("sealed", false))

	if entries.is_empty():
		# Empty sealed journal: head must equal genesis when integrity present.
		if has_integrity_meta:
			var head0: String = str((integrity as Dictionary).get("head_seal", ""))
			if head0.is_empty() or not seals_equal(head0, genesis):
				return {
					"ok": false,
					"error_code": "journal_integrity_invalid",
					"error": "empty journal head_seal != genesis",
					"broken_at_index": -1,
				}
		elif not has_integrity_meta:
			# Unsigned empty: fail closed under enforcement.
			return {
				"ok": false,
				"error_code": "journal_integrity_unsigned",
				"error": "unsigned journal (no integrity meta)",
			}
		return {
			"ok": true,
			"head_seal": genesis,
			"entry_count": 0,
			"world_revision": int(env.get("world_revision", base_rev)),
		}

	# Non-empty: every entry must be sealed.
	var prev: String = genesis
	var last_seal: String = genesis
	for i in entries.size():
		var e = entries[i]
		if not (e is Dictionary):
			return {
				"ok": false,
				"error_code": "journal_integrity_invalid",
				"error": "entry[%d] not object" % i,
				"broken_at_index": i,
			}
		var ed: Dictionary = e
		if not ed.has("seal") or not ed.has("prev_seal") or not ed.has("sequence_index"):
			return {
				"ok": false,
				"error_code": "journal_integrity_unsigned",
				"error": "entry[%d] missing seal fields" % i,
				"broken_at_index": i,
			}
		var seal_alg: String = str(ed.get("seal_alg", ""))
		if seal_alg != SEAL_ALG:
			return {
				"ok": false,
				"error_code": "journal_integrity_invalid",
				"error": "entry[%d] seal_alg=%s" % [i, seal_alg],
				"broken_at_index": i,
			}
		var got_seal: String = str(ed.get("seal", ""))
		var got_prev: String = str(ed.get("prev_seal", ""))
		var seq: int = int(ed.get("sequence_index", -1))
		if seq != i:
			return {
				"ok": false,
				"error_code": "journal_integrity_invalid",
				"error": "entry[%d] sequence_index=%d" % [i, seq],
				"broken_at_index": i,
			}
		if not is_valid_seal_hex(got_seal) or not is_valid_seal_hex(got_prev):
			return {
				"ok": false,
				"error_code": "journal_integrity_invalid",
				"error": "entry[%d] invalid seal hex" % i,
				"broken_at_index": i,
			}
		if not seals_equal(got_prev, prev):
			return {
				"ok": false,
				"error_code": "journal_integrity_invalid",
				"error": "entry[%d] broken prev_seal chain" % i,
				"broken_at_index": i,
			}
		var body: Dictionary = entry_without_seals(ed)
		# Ensure body carries the claimed sequence/prev for payload hash consistency.
		body["sequence_index"] = seq
		body["prev_seal"] = got_prev
		var computed: Dictionary = compute_entry_seal(
			key, body, got_prev, seq, space_id, journal_id
		)
		if not bool(computed.get("ok", false)):
			return {
				"ok": false,
				"error_code": str(computed.get("error_code", "journal_integrity_invalid")),
				"error": "entry[%d] seal recompute failed: %s" % [i, str(computed.get("error", ""))],
				"broken_at_index": i,
			}
		var expect_seal: String = str(computed["seal"])
		if not seals_equal(got_seal, expect_seal):
			# Systematic mismatch at first entry often means wrong key; still fail closed.
			var code: String = "journal_integrity_invalid"
			if i == 0:
				code = "journal_integrity_wrong_key"
			return {
				"ok": false,
				"error_code": code,
				"error": "entry[%d] seal HMAC mismatch" % i,
				"broken_at_index": i,
			}
		prev = got_seal
		last_seal = got_seal

	if has_integrity_meta:
		var head: String = str((integrity as Dictionary).get("head_seal", ""))
		if not head.is_empty() and not seals_equal(head, last_seal):
			return {
				"ok": false,
				"error_code": "journal_integrity_invalid",
				"error": "integrity.head_seal mismatch",
				"broken_at_index": entries.size() - 1,
			}

	return {
		"ok": true,
		"head_seal": last_seal,
		"entry_count": entries.size(),
		"world_revision": int(env.get("world_revision", 0)),
	}
