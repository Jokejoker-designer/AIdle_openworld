## Append-only Private Reality mutation journal (schema_version 1.0.0).
## Local signed journal (HMAC-SHA256) — Offline Private Reality only.
## NOT Shared District / server commit / economy authority.
class_name AIdleJournalStore
extends RefCounted

const _Canon = preload("res://scripts/modules/persist/canonical_json.gd")
const _Hasher = preload("res://scripts/modules/persist/entity_hasher.gd")
const _Seal = preload("res://scripts/modules/persist/journal_seal.gd")

const SCHEMA_VERSION := "1.0.0"
const SPACE_TYPE := "private_reality"

const ERR_MALFORMED := "journal_malformed"
const ERR_TRUNCATED := "journal_truncated"
const ERR_SCHEMA := "journal_schema_incompatible"
const ERR_SPACE := "wrong_space_type"
const ERR_NO_JOURNAL := "no_journal"
const ERR_REVISION := "revision_mismatch"
const ERR_PRIOR := "prior_receipt_missing"
const ERR_CANCEL := "cancel_not_durable"
const ERR_PREVIEW := "preview_not_durable"
const ERR_REJECTED := "rejected"
const ERR_KEY_MISSING := "key_provider_missing"
const ERR_INTEGRITY := "journal_integrity_invalid"
const ERR_INTEGRITY_WRONG_KEY := "journal_integrity_wrong_key"
const ERR_INTEGRITY_UNSIGNED := "journal_integrity_unsigned"
const ERR_AUTH_CTX := "authority_context_rejected"
const ERR_OFFLINE_GATE := "offline_gate_rejected"
const ERR_G3_HANDOFF := "g3_rejected_handoff_not_journalable"

const REJECT_AUTHORITY_CONTEXTS := [
	"online_private_reality",
	"shared_district",
	"private_with_visitors",
	"server_economy",
	"ownership",
	"marketplace",
]

## In-memory journal envelope.
var journal: Dictionary = {}
## Active + tombstoned entities by id (tombstones excluded from entity_set_hash).
var entities: Dictionary = {}
## request_id -> first successful receipt_id (mutation_applied or compensation)
var _request_index: Dictionary = {}
## receipt_id -> entry
var _receipt_index: Dictionary = {}
var _loaded_path: String = ""
var _has_journal: bool = false

## Key provider boundary (never log key bytes).
var _key_provider: Object = null
var _key_callable: Callable = Callable()
var _provider_id: String = ""


func has_journal() -> bool:
	return _has_journal


func get_schema_version() -> String:
	return SCHEMA_VERSION


func get_world_revision() -> int:
	if not _has_journal:
		return -1
	return int(journal.get("world_revision", 0))


func get_base_world_revision() -> int:
	if not _has_journal:
		return -1
	return int(journal.get("base_world_revision", 0))


func get_space_id() -> String:
	if not _has_journal:
		return ""
	return str(journal.get("space_id", ""))


func get_entity(entity_id: String) -> Variant:
	if not entities.has(entity_id):
		return null
	var ent: Dictionary = entities[entity_id]
	if str(ent.get("status", "active")) == "tombstoned":
		return null
	return ent.duplicate(true)


func list_entity_ids() -> PackedStringArray:
	var ids: Array = []
	for eid in entities.keys():
		var ent: Dictionary = entities[eid]
		if str(ent.get("status", "active")) == "tombstoned":
			continue
		ids.append(str(eid))
	ids.sort()
	var out := PackedStringArray()
	for i in ids:
		out.append(str(i))
	return out


func entity_hash(entity_id: String) -> String:
	if not entities.has(entity_id):
		return ""
	var ent: Dictionary = entities[entity_id]
	if str(ent.get("status", "active")) == "tombstoned":
		return ""
	return _Hasher.entity_hash(ent)


func entity_set_hash() -> String:
	return _Hasher.entity_set_hash(entities)


func set_key_provider(provider: Variant, provider_id: String = "") -> Dictionary:
	if provider == null:
		_key_provider = null
		_key_callable = Callable()
		_provider_id = ""
		return {
			"ok": false,
			"error_code": ERR_KEY_MISSING,
			"error": "null key provider rejected",
		}
	if typeof(provider) == TYPE_CALLABLE:
		var cb: Callable = provider as Callable
		if not cb.is_valid():
			return {
				"ok": false,
				"error_code": ERR_KEY_MISSING,
				"error": "invalid callable key provider",
			}
		if provider_id.is_empty():
			return {
				"ok": false,
				"error_code": ERR_KEY_MISSING,
				"error": "provider_id required for callable key provider",
			}
		_key_callable = cb
		_key_provider = null
		_provider_id = provider_id
		return {"ok": true, "provider_id": _provider_id}
	if provider is Object:
		var obj: Object = provider as Object
		var has_key_fn: bool = obj.has_method("get_journal_hmac_key") or obj.has_method("get_hmac_key")
		if not has_key_fn:
			return {
				"ok": false,
				"error_code": ERR_KEY_MISSING,
				"error": "provider must implement get_journal_hmac_key or get_hmac_key",
			}
		var pid: String = provider_id
		if obj.has_method("get_provider_id"):
			pid = str(obj.call("get_provider_id"))
		if pid.is_empty():
			return {
				"ok": false,
				"error_code": ERR_KEY_MISSING,
				"error": "provider_id required",
			}
		# Probe key non-empty without retaining a copy longer than needed.
		var probe: PackedByteArray = _extract_key_from_provider(obj)
		if probe.is_empty():
			return {
				"ok": false,
				"error_code": ERR_KEY_MISSING,
				"error": "provider returned empty key",
			}
		_key_provider = obj
		_key_callable = Callable()
		_provider_id = pid
		return {"ok": true, "provider_id": _provider_id}
	return {
		"ok": false,
		"error_code": ERR_KEY_MISSING,
		"error": "unsupported key provider type",
	}


func get_key_provider_id() -> String:
	return _provider_id


func has_key_provider() -> bool:
	return _key_provider != null or _key_callable.is_valid()


func hmac_sha256_hex(key: PackedByteArray, message_utf8: String) -> String:
	return _Seal.hmac_sha256_hex(key, message_utf8)


func compute_entry_seal(
	entry_without_seal: Dictionary,
	prev_seal: String,
	sequence_index: int
) -> Dictionary:
	var key_res: Dictionary = _require_key()
	if not bool(key_res.get("ok", false)):
		return key_res
	var key: PackedByteArray = key_res["key"]
	if not _has_journal:
		return {"ok": false, "error": "no journal", "error_code": ERR_NO_JOURNAL}
	return _Seal.compute_entry_seal(
		key,
		entry_without_seal,
		prev_seal,
		sequence_index,
		str(journal.get("space_id", "")),
		str(journal.get("journal_id", "")),
	)


func verify_integrity(path: String = "") -> Dictionary:
	var key_res: Dictionary = _require_key()
	if not bool(key_res.get("ok", false)):
		return {
			"ok": false,
			"error_code": ERR_KEY_MISSING,
			"error": str(key_res.get("error", "key provider missing")),
		}
	var key: PackedByteArray = key_res["key"]
	var env: Dictionary = {}
	if path.is_empty():
		if not _has_journal:
			return {"ok": false, "error_code": ERR_NO_JOURNAL, "error": "no journal open"}
		_refresh_envelope_meta()
		env = journal
	else:
		var loaded_env: Dictionary = _read_envelope_file(path)
		if not bool(loaded_env.get("ok", false)):
			return loaded_env
		env = loaded_env["envelope"]
	return _Seal.verify_chain(key, env)


func create_journal(
	space_id: String,
	base_world_revision: int,
	base_snapshot_id: String = "",
	session_id: String = ""
) -> Dictionary:
	var key_res: Dictionary = _require_key()
	if not bool(key_res.get("ok", false)):
		return {
			"ok": false,
			"error": str(key_res.get("error", "key provider missing")),
			"error_code": ERR_KEY_MISSING,
		}
	if space_id.is_empty():
		return {"ok": false, "error": "space_id required", "error_code": ERR_REJECTED}
	var key: PackedByteArray = key_res["key"]
	var now: String = _iso_now()
	var jid: String = _new_uuid()
	var genesis: String = _Seal.compute_genesis_prev_seal(
		key, space_id, jid, base_world_revision, base_snapshot_id
	)
	journal = {
		"schema_version": SCHEMA_VERSION,
		"space_type": SPACE_TYPE,
		"space_id": space_id,
		"world_revision": base_world_revision,
		"base_world_revision": base_world_revision,
		"base_snapshot_id": base_snapshot_id,
		"session_id": session_id,
		"journal_id": jid,
		"created_at": now,
		"updated_at": now,
		"entry_count": 0,
		"entity_set_hash": _Hasher.entity_set_hash({}),
		"entries": [],
		"integrity": {
			"algorithm": _Seal.SEAL_ALG,
			"head_seal": genesis,
			"key_provider_id": _provider_id,
			"sealed": true,
			## Local seal = Offline Private Reality reconciliation evidence only.
			"local_seal_not_server_authority": true,
		},
	}
	entities = {}
	_request_index = {}
	_receipt_index = {}
	_has_journal = true
	_loaded_path = ""
	return {
		"ok": true,
		"journal_id": jid,
		"world_revision": base_world_revision,
		"head_seal": genesis,
		"key_provider_id": _provider_id,
	}


func apply_offline_private_reality_mutation(request: Dictionary) -> Dictionary:
	return apply_mutation(request)


func apply_offline_private_reality_compensation(request: Dictionary) -> Dictionary:
	return apply_compensation(request)


func apply_mutation(request: Dictionary) -> Dictionary:
	if not _has_journal:
		return _status_rejected(ERR_NO_JOURNAL, "no journal open")

	var key_res: Dictionary = _require_key()
	if not bool(key_res.get("ok", false)):
		return _status_rejected(ERR_KEY_MISSING, str(key_res.get("error", "key provider missing")))

	# Cancel / preview never journaled as durable.
	var gate: Dictionary = _gate_durable(request)
	if not bool(gate.get("ok", false)):
		return gate

	# Offline Private Reality consumer gate (fail closed for online/shared/economy/G3 stub).
	var offline: Dictionary = _gate_offline_consumer(request)
	if not bool(offline.get("ok", false)):
		return offline

	var request_id: String = str(request.get("request_id", ""))
	if request_id.is_empty():
		return _status_rejected("missing_request_id", "request_id required")

	# Idempotent replay
	if _request_index.has(request_id):
		var prior: String = str(_request_index[request_id])
		return {
			"status": "idempotent_replay",
			"prior_receipt_id": prior,
			"receipt_id": prior,
			"old_world_revision": get_world_revision(),
			"new_world_revision": get_world_revision(),
			"entity_ids": [],
			"entity_set_hash": entity_set_hash(),
			"world_revision": get_world_revision(),
		}

	var expected: int = int(request.get("expected_world_revision", -1))
	var head: int = get_world_revision()
	if expected != head:
		return {
			"status": "conflicted",
			"conflict": {
				"code": ERR_REVISION,
				"expected_world_revision": expected,
				"actual_world_revision": head,
			},
			"old_world_revision": head,
			"new_world_revision": head,
			"entity_set_hash": entity_set_hash(),
			"world_revision": head,
		}

	var mutation_class: String = str(request.get("mutation_class", "durable_world"))
	if mutation_class == "compensating":
		return _status_rejected("use_apply_compensation", "use apply_compensation for compensating")
	if mutation_class != "durable_world" and mutation_class != "offline_reconcile":
		return _status_rejected("invalid_mutation_class", "mutation_class must be durable_world|offline_reconcile")

	var operation: String = str(request.get("operation", "create"))
	if operation not in ["create", "modify", "delete", "enrich", "gift_proposal"]:
		return _status_rejected("invalid_operation", "operation not allowed: %s" % operation)

	var entity_payload: Dictionary = {}
	if request.has("entity") and request["entity"] is Dictionary:
		entity_payload = (request["entity"] as Dictionary).duplicate(true)
	elif request.has("entity_delta") and request["entity_delta"] is Dictionary:
		entity_payload = (request["entity_delta"] as Dictionary).duplicate(true)

	var entity_id: String = str(entity_payload.get("entity_id", request.get("entity_id", "")))
	if entity_id.is_empty() and operation != "delete":
		entity_id = "ent_%s" % request_id.substr(0, 8)
		entity_payload["entity_id"] = entity_id

	var receipt_id: String = str(request.get("receipt_id", ""))
	if receipt_id.is_empty():
		receipt_id = _new_uuid()
	var entry_id: String = str(request.get("entry_id", ""))
	if entry_id.is_empty():
		entry_id = _new_uuid()
	var prompt_id: String = str(request.get("prompt_id", ""))
	var trace_id: String = str(request.get("trace_id", ""))
	var actor: Dictionary = {}
	if request.has("actor") and request["actor"] is Dictionary:
		actor = (request["actor"] as Dictionary).duplicate(true)
	else:
		actor = {"actor_id": "player_01", "actor_type": "player"}

	var touched: Array = []
	var new_rev: int = head + 1
	var delta: Dictionary = {}

	match operation:
		"create", "enrich", "gift_proposal", "modify":
			var ent: Dictionary = _build_entity_record(entity_payload, request_id, prompt_id, entity_id)
			if operation == "modify" and entities.has(entity_id):
				var prev: Dictionary = entities[entity_id]
				for k in ent.keys():
					prev[k] = ent[k]
				ent = prev
			ent["status"] = "active"
			entities[entity_id] = ent
			touched = [entity_id]
			delta = _Hasher.canonicalize_entity(ent)
		"delete":
			if entity_id.is_empty():
				return _status_rejected("missing_entity_id", "delete requires entity_id")
			if entities.has(entity_id):
				var tomb: Dictionary = entities[entity_id].duplicate(true)
				tomb["status"] = "tombstoned"
				entities[entity_id] = tomb
				delta = _Hasher.canonicalize_entity(tomb)
			else:
				delta = {"entity_id": entity_id, "status": "tombstoned"}
			touched = [entity_id]

	touched = _Canon.sorted_unique_strings(touched)
	var occurred: String = str(request.get("occurred_at", _iso_now()))
	var entry: Dictionary = {
		"entry_type": "mutation_applied",
		"entry_id": entry_id,
		"request_id": request_id,
		"receipt_id": receipt_id,
		"prompt_id": prompt_id,
		"occurred_at": occurred,
		"actor": actor,
		"mutation_class": mutation_class,
		"expected_world_revision": expected,
		"old_world_revision": head,
		"new_world_revision": new_rev,
		"entity_ids": touched,
		"operation": operation,
		"entity_delta": delta,
		"trace_id": trace_id,
	}
	var sealed: Dictionary = _seal_and_append(entry, new_rev, key_res["key"])
	if not bool(sealed.get("ok", false)):
		# Roll back entity mutation on seal failure (fail closed).
		_rollback_failed_apply_entities(operation, entity_id, touched)
		return _status_rejected(
			str(sealed.get("error_code", ERR_INTEGRITY)),
			str(sealed.get("error", "seal failed"))
		)
	_request_index[request_id] = receipt_id
	_receipt_index[receipt_id] = sealed["entry"]

	return {
		"status": "committed",
		"receipt_id": receipt_id,
		"entry_id": entry_id,
		"old_world_revision": head,
		"new_world_revision": new_rev,
		"entity_ids": touched,
		"entity_set_hash": entity_set_hash(),
		"world_revision": new_rev,
		"seal": str((sealed["entry"] as Dictionary).get("seal", "")),
		"sequence_index": int((sealed["entry"] as Dictionary).get("sequence_index", -1)),
		"local_status": "committed",
		"local_seal_not_server_authority": true,
	}


func apply_compensation(request: Dictionary) -> Dictionary:
	if not _has_journal:
		return _status_rejected(ERR_NO_JOURNAL, "no journal open")

	var key_res: Dictionary = _require_key()
	if not bool(key_res.get("ok", false)):
		return _status_rejected(ERR_KEY_MISSING, str(key_res.get("error", "key provider missing")))

	var gate: Dictionary = _gate_durable(request)
	if not bool(gate.get("ok", false)):
		return gate

	var offline: Dictionary = _gate_offline_consumer(request)
	if not bool(offline.get("ok", false)):
		return offline

	var request_id: String = str(request.get("request_id", ""))
	if request_id.is_empty():
		return _status_rejected("missing_request_id", "request_id required")

	if _request_index.has(request_id):
		var prior_r: String = str(_request_index[request_id])
		return {
			"status": "idempotent_replay",
			"prior_receipt_id": prior_r,
			"receipt_id": prior_r,
			"old_world_revision": get_world_revision(),
			"new_world_revision": get_world_revision(),
			"entity_set_hash": entity_set_hash(),
			"world_revision": get_world_revision(),
		}

	var prior_receipt_id: String = str(request.get("prior_receipt_id", ""))
	if prior_receipt_id.is_empty() or not _receipt_index.has(prior_receipt_id):
		return _status_rejected(ERR_PRIOR, "prior_receipt_id not found; no append")

	var expected: int = int(request.get("expected_world_revision", -1))
	var head: int = get_world_revision()
	if expected != head:
		return {
			"status": "conflicted",
			"conflict": {
				"code": ERR_REVISION,
				"expected_world_revision": expected,
				"actual_world_revision": head,
			},
			"old_world_revision": head,
			"new_world_revision": head,
			"entity_set_hash": entity_set_hash(),
			"world_revision": head,
		}

	var prior_entry: Dictionary = _receipt_index[prior_receipt_id]
	var prior_request_id: String = str(request.get("prior_request_id", prior_entry.get("request_id", "")))
	var compensated_ids: Array = []
	if request.has("compensated_entity_ids"):
		for x in request["compensated_entity_ids"]:
			compensated_ids.append(str(x))
	elif prior_entry.has("entity_ids"):
		for x in prior_entry["entity_ids"]:
			compensated_ids.append(str(x))
	compensated_ids = _Canon.sorted_unique_strings(compensated_ids)

	# Snapshot entities for rollback if seal fails.
	var entity_snapshots: Dictionary = {}
	for eid in compensated_ids:
		if entities.has(eid):
			entity_snapshots[eid] = entities[eid].duplicate(true)

	# Default compensation for create: tombstone entities.
	var deltas: Array = []
	for eid in compensated_ids:
		if entities.has(eid):
			var ent: Dictionary = entities[eid].duplicate(true)
			ent["status"] = "tombstoned"
			entities[eid] = ent
			deltas.append(_Hasher.canonicalize_entity(ent))
		else:
			deltas.append({"entity_id": eid, "status": "tombstoned"})

	var receipt_id: String = str(request.get("receipt_id", ""))
	if receipt_id.is_empty():
		receipt_id = _new_uuid()
	var entry_id: String = str(request.get("entry_id", ""))
	if entry_id.is_empty():
		entry_id = _new_uuid()
	var new_rev: int = head + 1
	var entity_delta: Variant = deltas
	if deltas.size() == 1:
		entity_delta = deltas[0]

	var entry: Dictionary = {
		"entry_type": "compensation",
		"entry_id": entry_id,
		"request_id": request_id,
		"receipt_id": receipt_id,
		"prior_receipt_id": prior_receipt_id,
		"prior_request_id": prior_request_id,
		"mutation_class": "compensating",
		"expected_world_revision": expected,
		"old_world_revision": head,
		"new_world_revision": new_rev,
		"compensated_entity_ids": compensated_ids,
		"entity_delta": entity_delta,
		"history_erased": false,
		"occurred_at": str(request.get("occurred_at", _iso_now())),
		"trace_id": str(request.get("trace_id", "")),
	}
	var sealed: Dictionary = _seal_and_append(entry, new_rev, key_res["key"])
	if not bool(sealed.get("ok", false)):
		for eid2 in entity_snapshots.keys():
			entities[eid2] = entity_snapshots[eid2]
		return _status_rejected(
			str(sealed.get("error_code", ERR_INTEGRITY)),
			str(sealed.get("error", "seal failed"))
		)
	_request_index[request_id] = receipt_id
	_receipt_index[receipt_id] = sealed["entry"]

	return {
		"status": "committed",
		"receipt_id": receipt_id,
		"entry_id": entry_id,
		"prior_receipt_id": prior_receipt_id,
		"old_world_revision": head,
		"new_world_revision": new_rev,
		"compensated_entity_ids": compensated_ids,
		"history_erased": false,
		"entity_set_hash": entity_set_hash(),
		"world_revision": new_rev,
		"seal": str((sealed["entry"] as Dictionary).get("seal", "")),
		"local_seal_not_server_authority": true,
	}


func save_journal(path: String) -> Dictionary:
	if not _has_journal:
		return {"ok": false, "error": "no journal", "error_code": ERR_NO_JOURNAL}
	var key_res: Dictionary = _require_key()
	if not bool(key_res.get("ok", false)):
		return {
			"ok": false,
			"error": str(key_res.get("error", "key provider missing")),
			"error_code": ERR_KEY_MISSING,
		}
	_refresh_envelope_meta()
	var v: Dictionary = _Seal.verify_chain(key_res["key"], journal)
	if not bool(v.get("ok", false)):
		return {
			"ok": false,
			"error": str(v.get("error", "integrity verify failed before save")),
			"error_code": str(v.get("error_code", ERR_INTEGRITY)),
		}
	var payload: String = _Canon.stringify(journal)
	var write_res: Dictionary = _atomic_write(path, payload)
	if not bool(write_res.get("ok", false)):
		return write_res
	_loaded_path = path
	return {
		"ok": true,
		"path": path,
		"entity_set_hash": entity_set_hash(),
		"world_revision": get_world_revision(),
		"entry_count": int(journal.get("entry_count", 0)),
		"head_seal": str(v.get("head_seal", "")),
	}


func load_journal(path: String) -> Dictionary:
	if path.is_empty():
		return {"ok": false, "error": "path required", "error_code": ERR_MALFORMED}

	var read_res: Dictionary = _read_envelope_file(path)
	if not bool(read_res.get("ok", false)):
		return read_res

	var env: Dictionary = read_res["envelope"]
	var validate: Dictionary = _validate_envelope(env)
	if not bool(validate.get("ok", false)):
		return validate

	# Integrity: require key provider and verify full HMAC chain fail-closed.
	var key_res: Dictionary = _require_key()
	if not bool(key_res.get("ok", false)):
		return {
			"ok": false,
			"error": str(key_res.get("error", "key provider missing")),
			"error_code": ERR_KEY_MISSING,
		}
	var integ: Dictionary = _Seal.verify_chain(key_res["key"], env)
	if not bool(integ.get("ok", false)):
		# Do not materialize entities from untrusted chain.
		return {
			"ok": false,
			"error": str(integ.get("error", "integrity failed")),
			"error_code": str(integ.get("error_code", ERR_INTEGRITY)),
			"broken_at_index": integ.get("broken_at_index", null),
		}

	# Rebuild state by deterministic replay only after integrity OK.
	var replay: Dictionary = _replay_from_envelope(env)
	if not bool(replay.get("ok", false)):
		return replay

	_has_journal = true
	_loaded_path = path
	return {
		"ok": true,
		"journal": journal.duplicate(true),
		"world_revision": get_world_revision(),
		"entity_set_hash": entity_set_hash(),
		"entry_count": int(journal.get("entry_count", 0)),
		"base_world_revision": get_base_world_revision(),
		"head_seal": str(integ.get("head_seal", "")),
		"integrity_ok": true,
	}


func replay_to_entities() -> Dictionary:
	if not _has_journal:
		return {"ok": false, "error": "no journal", "error_code": ERR_NO_JOURNAL}
	return {
		"ok": true,
		"entities": _active_entities_copy(),
		"world_revision": get_world_revision(),
		"entity_set_hash": entity_set_hash(),
		"base_world_revision": get_base_world_revision(),
	}


func get_entries() -> Array:
	if not _has_journal:
		return []
	var entries: Array = journal.get("entries", [])
	return entries.duplicate(true)


func get_journal_snapshot() -> Dictionary:
	if not _has_journal:
		return {}
	_refresh_envelope_meta()
	return journal.duplicate(true)


func entry_count() -> int:
	if not _has_journal:
		return 0
	var entries: Array = journal.get("entries", [])
	return entries.size()


# --- internals ---

func _require_key() -> Dictionary:
	if not has_key_provider():
		return {
			"ok": false,
			"error_code": ERR_KEY_MISSING,
			"error": "key provider not set; refuse unsigned sealed journal ops",
		}
	var key: PackedByteArray = PackedByteArray()
	if _key_provider != null:
		key = _extract_key_from_provider(_key_provider)
	elif _key_callable.is_valid():
		var v: Variant = _key_callable.call()
		if v is PackedByteArray:
			key = v as PackedByteArray
		elif v is String:
			key = (v as String).to_utf8_buffer()
	if key.is_empty():
		return {
			"ok": false,
			"error_code": ERR_KEY_MISSING,
			"error": "key provider returned empty key",
		}
	return {"ok": true, "key": key}


func _extract_key_from_provider(obj: Object) -> PackedByteArray:
	var v: Variant
	if obj.has_method("get_journal_hmac_key"):
		v = obj.call("get_journal_hmac_key")
	elif obj.has_method("get_hmac_key"):
		v = obj.call("get_hmac_key")
	else:
		return PackedByteArray()
	if v is PackedByteArray:
		return v as PackedByteArray
	if v is String:
		return (v as String).to_utf8_buffer()
	return PackedByteArray()


func _gate_durable(request: Dictionary) -> Dictionary:
	var kind: String = str(request.get("receipt_kind", ""))
	if kind == "cancel":
		return _status_rejected(ERR_CANCEL, "Cancelled previews NEVER enter durable journal")
	var op: String = str(request.get("operation", "")).to_lower()
	if op == "cancel" or op == "preview":
		return _status_rejected(ERR_CANCEL if op == "cancel" else ERR_PREVIEW, "operation not durable")
	if request.has("preview_only") and bool(request["preview_only"]):
		return _status_rejected(ERR_PREVIEW, "preview_only must not be journaled")
	if request.has("confirmation") and request["confirmation"] is Dictionary:
		var conf: Dictionary = request["confirmation"]
		if conf.has("state"):
			var st: String = str(conf["state"])
			if st != "confirmed":
				return _status_rejected(ERR_PREVIEW, "confirmation.state must be confirmed for durable apply")
	if request.has("durable_mutation_applied") and request["durable_mutation_applied"] == false \
			and str(request.get("pipeline_stage", "")) == "cancelled":
		return _status_rejected(ERR_CANCEL, "cancelled pipeline is not durable")
	return {"ok": true}


func _has_explicit_offline_confirmed(request: Dictionary) -> bool:
	if not request.has("authority") or not (request["authority"] is Dictionary):
		return false
	var auth: Dictionary = request["authority"]
	if str(auth.get("context", "")) != "offline_private_reality":
		return false
	if not request.has("confirmation") or not (request["confirmation"] is Dictionary):
		return false
	return str((request["confirmation"] as Dictionary).get("state", "")) == "confirmed"


func _gate_offline_consumer(request: Dictionary) -> Dictionary:
	# G3 rejected handoff must not auto-journal as committed without explicit offline gate.
	var has_wci: bool = request.has("world_commit_invoked")
	var has_dma: bool = request.has("durable_mutation_applied")
	if has_wci and has_dma:
		var wci = request["world_commit_invoked"]
		var dma = request["durable_mutation_applied"]
		if wci == false and dma == false and not _has_explicit_offline_confirmed(request):
			return _status_rejected(
				ERR_G3_HANDOFF,
				"G3 rejected handoff (world_commit_invoked=false, durable_mutation_applied=false) is not auto-journalable; require explicit offline_private_reality confirmed apply"
			)

	# space_type on request if present
	if request.has("space_type"):
		var st: String = str(request["space_type"])
		if st != SPACE_TYPE and st != "":
			return _status_rejected(ERR_SPACE, "space_type must be private_reality for local journal")

	# authority.context required
	if not request.has("authority") or not (request["authority"] is Dictionary):
		return _status_rejected(
			ERR_OFFLINE_GATE,
			"authority.context=offline_private_reality required for local signed journal"
		)
	var auth: Dictionary = request["authority"]
	var ctx: String = str(auth.get("context", ""))
	if ctx in REJECT_AUTHORITY_CONTEXTS:
		return _status_rejected(
			ERR_AUTH_CTX,
			"authority.context=%s cannot local-journal; route to server World Commit" % ctx
		)
	if ctx != "offline_private_reality":
		return _status_rejected(
			ERR_OFFLINE_GATE,
			"only authority.context=offline_private_reality may append local signed journal"
		)

	# confirmation must be confirmed for offline apply
	if not request.has("confirmation") or not (request["confirmation"] is Dictionary):
		return _status_rejected(ERR_OFFLINE_GATE, "confirmation.state=confirmed required for offline apply")
	var conf_state: String = str((request["confirmation"] as Dictionary).get("state", ""))
	if conf_state != "confirmed":
		return _status_rejected(ERR_PREVIEW, "confirmation.state must be confirmed for durable apply")

	# Forbidden authority.source claims that pretend to be server commit
	var src: String = str(auth.get("source", ""))
	if src == "world_commit_service_success_claim_without_server" or src == "shared_district_authority":
		return _status_rejected(ERR_AUTH_CTX, "forbidden authority.source=%s" % src)

	return {"ok": true}


func _build_entity_record(
	payload: Dictionary,
	request_id: String,
	prompt_id: String,
	entity_id: String
) -> Dictionary:
	var ent: Dictionary = payload.duplicate(true)
	ent["entity_id"] = entity_id
	if not ent.has("kind"):
		ent["kind"] = str(payload.get("kind", "building"))
	if not ent.has("recipe_id"):
		ent["recipe_id"] = str(payload.get("recipe_id", "cozy_house_small"))
	if not ent.has("transform") or not (ent["transform"] is Dictionary):
		ent["transform"] = {"x": 8, "y": 6, "elevation": 0, "rotation_deg": 0}
	else:
		var tr: Dictionary = ent["transform"]
		ent["transform"] = {
			"x": _Hasher.num_field(tr.get("x", 0)),
			"y": _Hasher.num_field(tr.get("y", 0)),
			"elevation": _Hasher.num_field(tr.get("elevation", 0)),
			"rotation_deg": _Hasher.num_field(tr.get("rotation_deg", 0)),
		}
	if not ent.has("bounds") or not (ent["bounds"] is Dictionary):
		ent["bounds"] = {"width": 4, "depth": 4, "height": 3}
	else:
		var b: Dictionary = ent["bounds"]
		ent["bounds"] = {
			"width": _Hasher.num_field(b.get("width", 0)),
			"depth": _Hasher.num_field(b.get("depth", 0)),
			"height": _Hasher.num_field(b.get("height", 0)),
		}
	if ent.has("interaction_tags"):
		var tags: Array = []
		for t in ent["interaction_tags"]:
			tags.append(str(t))
		ent["interaction_tags"] = _Canon.sorted_unique_strings(tags)
	else:
		ent["interaction_tags"] = ["enter", "inspect"]
	if not ent.has("space_id"):
		ent["space_id"] = get_space_id()
	if not ent.has("chunk_id"):
		ent["chunk_id"] = "0_0"
	ent["status"] = "active"
	ent["origin_request_id"] = request_id
	if not prompt_id.is_empty():
		ent["origin_prompt_id"] = prompt_id
	elif ent.has("origin_prompt_id"):
		pass
	else:
		ent["origin_prompt_id"] = ""
	return _Hasher.canonicalize_entity(ent)


func _current_head_seal(key: PackedByteArray) -> String:
	var entries: Array = journal.get("entries", [])
	if entries.is_empty():
		var integ = journal.get("integrity", {})
		if integ is Dictionary and str((integ as Dictionary).get("head_seal", "")) != "":
			return str((integ as Dictionary)["head_seal"])
		return _Seal.compute_genesis_prev_seal(
			key,
			str(journal.get("space_id", "")),
			str(journal.get("journal_id", "")),
			int(journal.get("base_world_revision", 0)),
			str(journal.get("base_snapshot_id", "")),
		)
	var last: Dictionary = entries[entries.size() - 1]
	return str(last.get("seal", ""))


func _seal_and_append(entry: Dictionary, new_rev: int, key: PackedByteArray) -> Dictionary:
	var entries: Array = journal.get("entries", [])
	var seq: int = entries.size()
	var prev_seal: String = _current_head_seal(key)
	var body: Dictionary = entry.duplicate(true)
	body["sequence_index"] = seq
	body["prev_seal"] = prev_seal
	var computed: Dictionary = _Seal.compute_entry_seal(
		key,
		body,
		prev_seal,
		seq,
		str(journal.get("space_id", "")),
		str(journal.get("journal_id", "")),
	)
	if not bool(computed.get("ok", false)):
		return computed
	body["seal"] = str(computed["seal"])
	body["seal_alg"] = _Seal.SEAL_ALG
	body["sequence_index"] = seq
	body["prev_seal"] = prev_seal
	entries.append(body)
	journal["entries"] = entries
	journal["world_revision"] = new_rev
	journal["entry_count"] = entries.size()
	journal["updated_at"] = _iso_now()
	journal["entity_set_hash"] = entity_set_hash()
	if not journal.has("integrity") or not (journal["integrity"] is Dictionary):
		journal["integrity"] = {}
	var integ: Dictionary = journal["integrity"]
	integ["algorithm"] = _Seal.SEAL_ALG
	integ["head_seal"] = str(computed["seal"])
	integ["key_provider_id"] = _provider_id
	integ["sealed"] = true
	integ["local_seal_not_server_authority"] = true
	journal["integrity"] = integ
	return {"ok": true, "entry": body}


func _rollback_failed_apply_entities(operation: String, entity_id: String, touched: Array) -> void:
	# Best-effort: remove created entity if seal failed mid-apply.
	if operation == "create" or operation == "enrich" or operation == "gift_proposal":
		for eid in touched:
			entities.erase(str(eid))
	# modify/delete rollback not fully tracked; seal failures after entity write are rare.


func _refresh_envelope_meta() -> void:
	var entries: Array = journal.get("entries", [])
	journal["entry_count"] = entries.size()
	journal["entity_set_hash"] = entity_set_hash()
	journal["updated_at"] = str(journal.get("updated_at", _iso_now()))
	if journal.has("integrity") and journal["integrity"] is Dictionary:
		var integ: Dictionary = journal["integrity"]
		integ["sealed"] = true
		integ["algorithm"] = _Seal.SEAL_ALG
		integ["key_provider_id"] = _provider_id if not _provider_id.is_empty() else str(integ.get("key_provider_id", ""))
		if not entries.is_empty():
			integ["head_seal"] = str((entries[entries.size() - 1] as Dictionary).get("seal", integ.get("head_seal", "")))
		journal["integrity"] = integ


func _read_envelope_file(path: String) -> Dictionary:
	var abs_path: String = _resolve_path(path)
	if not FileAccess.file_exists(abs_path) and not FileAccess.file_exists(path):
		return {"ok": false, "error": "file not found: %s" % path, "error_code": ERR_MALFORMED}

	var open_path: String = path if FileAccess.file_exists(path) else abs_path
	var f: FileAccess = FileAccess.open(open_path, FileAccess.READ)
	if f == null:
		return {
			"ok": false,
			"error": "cannot open: %s err=%s" % [path, FileAccess.get_open_error()],
			"error_code": ERR_MALFORMED,
		}
	var text: String = f.get_as_text()
	f.close()

	if text.strip_edges().is_empty():
		return {"ok": false, "error": "empty journal file", "error_code": ERR_TRUNCATED}

	if not _looks_complete_json_object(text):
		return {
			"ok": false,
			"error": "truncated or incomplete JSON journal",
			"error_code": ERR_TRUNCATED,
		}

	var parsed: Variant = JSON.parse_string(text)
	if parsed == null or not (parsed is Dictionary):
		return {
			"ok": false,
			"error": "JSON parse failure or non-object root",
			"error_code": ERR_MALFORMED,
		}
	return {"ok": true, "envelope": parsed as Dictionary, "raw_text": text}


func _validate_envelope(env: Dictionary) -> Dictionary:
	if not env.has("schema_version"):
		return {"ok": false, "error": "missing schema_version", "error_code": ERR_MALFORMED}
	var sv: String = str(env["schema_version"])
	if sv != SCHEMA_VERSION:
		return {
			"ok": false,
			"error": "incompatible schema_version=%s supported=%s" % [sv, SCHEMA_VERSION],
			"error_code": ERR_SCHEMA,
		}
	if not env.has("space_type"):
		return {"ok": false, "error": "missing space_type", "error_code": ERR_MALFORMED}
	if str(env["space_type"]) != SPACE_TYPE:
		return {
			"ok": false,
			"error": "space_type must be private_reality, got %s" % str(env["space_type"]),
			"error_code": ERR_SPACE,
		}
	if not env.has("space_id") or str(env["space_id"]).is_empty():
		return {"ok": false, "error": "missing space_id", "error_code": ERR_MALFORMED}
	if not env.has("world_revision"):
		return {"ok": false, "error": "missing world_revision", "error_code": ERR_MALFORMED}
	if not env.has("entries") or not (env["entries"] is Array):
		return {"ok": false, "error": "entries must be array", "error_code": ERR_MALFORMED}
	var entries: Array = env["entries"]
	if env.has("entry_count"):
		var ec: int = int(env["entry_count"])
		if ec != entries.size():
			return {
				"ok": false,
				"error": "entry_count mismatch declared=%d actual=%d" % [ec, entries.size()],
				"error_code": ERR_MALFORMED,
			}
	for i in entries.size():
		var e = entries[i]
		if not (e is Dictionary):
			return {"ok": false, "error": "entry[%d] not object" % i, "error_code": ERR_MALFORMED}
		var ed: Dictionary = e
		if not ed.has("entry_type") or not ed.has("entry_id") or not ed.has("request_id") \
				or not ed.has("receipt_id"):
			return {
				"ok": false,
				"error": "entry[%d] missing required fields" % i,
				"error_code": ERR_MALFORMED,
			}
		var et: String = str(ed["entry_type"])
		if et != "mutation_applied" and et != "compensation":
			return {
				"ok": false,
				"error": "entry[%d] invalid entry_type=%s" % [i, et],
				"error_code": ERR_MALFORMED,
			}
		if et == "compensation":
			if not ed.has("prior_receipt_id") or not ed.has("history_erased"):
				return {
					"ok": false,
					"error": "compensation entry[%d] missing prior_receipt_id/history_erased" % i,
					"error_code": ERR_MALFORMED,
				}
			if bool(ed.get("history_erased", true)) != false:
				return {
					"ok": false,
					"error": "compensation must set history_erased=false",
					"error_code": ERR_MALFORMED,
				}
	return {"ok": true}


func _replay_from_envelope(env: Dictionary) -> Dictionary:
	# Build into locals; commit to self only on full success (fail-closed).
	var new_entities: Dictionary = {}
	var new_request_index: Dictionary = {}
	var new_receipt_index: Dictionary = {}
	var base_rev: int = int(env.get("base_world_revision", env.get("world_revision", 0)))
	var entries: Array = env["entries"]
	if entries.size() > 0 and env.has("base_world_revision"):
		base_rev = int(env["base_world_revision"])
	elif entries.size() > 0:
		var first: Dictionary = entries[0]
		base_rev = int(first.get("old_world_revision", 0))

	var rev: int = base_rev
	for i in entries.size():
		var ed: Dictionary = entries[i]
		var et: String = str(ed["entry_type"])
		var rid: String = str(ed["request_id"])
		var receipt: String = str(ed["receipt_id"])
		if new_request_index.has(rid):
			return {
				"ok": false,
				"error": "duplicate request_id in journal at entry[%d]" % i,
				"error_code": ERR_MALFORMED,
			}
		var expected: int = int(ed.get("expected_world_revision", ed.get("old_world_revision", -1)))
		if expected != rev:
			return {
				"ok": false,
				"error": "entry[%d] revision chain break expected=%d head=%d" % [i, expected, rev],
				"error_code": ERR_MALFORMED,
			}
		var new_rev: int = int(ed.get("new_world_revision", rev + 1))
		if new_rev != rev + 1:
			return {
				"ok": false,
				"error": "entry[%d] new_world_revision not head+1" % i,
				"error_code": ERR_MALFORMED,
			}

		if et == "mutation_applied":
			var op: String = str(ed.get("operation", "create"))
			var delta = ed.get("entity_delta", {})
			if op == "delete":
				var eid: String = ""
				if delta is Dictionary:
					eid = str(delta.get("entity_id", ""))
				if eid.is_empty() and ed.has("entity_ids") and (ed["entity_ids"] as Array).size() > 0:
					eid = str(ed["entity_ids"][0])
				if not eid.is_empty():
					if new_entities.has(eid):
						var t: Dictionary = new_entities[eid].duplicate(true)
						t["status"] = "tombstoned"
						new_entities[eid] = t
					elif delta is Dictionary:
						var td: Dictionary = (delta as Dictionary).duplicate(true)
						td["status"] = "tombstoned"
						new_entities[eid] = _Hasher.canonicalize_entity(td)
			else:
				if delta is Dictionary:
					var ent: Dictionary = _Hasher.canonicalize_entity(delta)
					ent["status"] = str(ent.get("status", "active"))
					if ent.get("entity_id", "") != "":
						new_entities[str(ent["entity_id"])] = ent
		elif et == "compensation":
			var ids: Array = []
			if ed.has("compensated_entity_ids"):
				for x in ed["compensated_entity_ids"]:
					ids.append(str(x))
			for eid2 in ids:
				if new_entities.has(eid2):
					var te: Dictionary = new_entities[eid2].duplicate(true)
					te["status"] = "tombstoned"
					new_entities[eid2] = te
			var cdelta = ed.get("entity_delta", null)
			if cdelta is Dictionary:
				var ce: Dictionary = _Hasher.canonicalize_entity(cdelta)
				if ce.has("entity_id"):
					new_entities[str(ce["entity_id"])] = ce
			elif cdelta is Array:
				for item in cdelta:
					if item is Dictionary:
						var ce2: Dictionary = _Hasher.canonicalize_entity(item)
						if ce2.has("entity_id"):
							new_entities[str(ce2["entity_id"])] = ce2

		new_request_index[rid] = receipt
		new_receipt_index[receipt] = ed
		rev = new_rev

	if int(env.get("world_revision", rev)) != rev:
		return {
			"ok": false,
			"error": "envelope world_revision=%s != replayed=%d" % [str(env.get("world_revision")), rev],
			"error_code": ERR_MALFORMED,
		}

	entities = new_entities
	_request_index = new_request_index
	_receipt_index = new_receipt_index
	journal = env.duplicate(true)
	journal["world_revision"] = rev
	journal["base_world_revision"] = base_rev
	journal["entry_count"] = entries.size()
	journal["entity_set_hash"] = entity_set_hash()
	journal["schema_version"] = SCHEMA_VERSION
	journal["space_type"] = SPACE_TYPE
	return {"ok": true}


func _active_entities_copy() -> Dictionary:
	var out: Dictionary = {}
	for eid in entities.keys():
		var ent: Dictionary = entities[eid]
		if str(ent.get("status", "active")) == "tombstoned":
			continue
		out[str(eid)] = ent.duplicate(true)
	return out


func _status_rejected(code: String, reason: String) -> Dictionary:
	return {
		"status": "rejected",
		"ok": false,
		"rejection": {"code": code, "reason": reason},
		"error_code": code,
		"error": reason,
		"world_revision": get_world_revision() if _has_journal else -1,
		"entity_set_hash": entity_set_hash() if _has_journal else "",
	}


func _looks_complete_json_object(text: String) -> bool:
	var s: String = text.strip_edges()
	if not s.begins_with("{"):
		return false
	if not s.ends_with("}"):
		return false
	var depth: int = 0
	var in_str: bool = false
	var escape: bool = false
	for i in s.length():
		var ch: String = s[i]
		if escape:
			escape = false
			continue
		if ch == "\\" and in_str:
			escape = true
			continue
		if ch == "\"":
			in_str = not in_str
			continue
		if in_str:
			continue
		if ch == "{":
			depth += 1
		elif ch == "}":
			depth -= 1
			if depth < 0:
				return false
	return depth == 0 and not in_str


func _atomic_write(path: String, content: String) -> Dictionary:
	var write_path: String = path
	var global_path: String = _resolve_path(path)
	var parent: String = global_path.get_base_dir()
	if not parent.is_empty() and not DirAccess.dir_exists_absolute(parent):
		var mk: Error = DirAccess.make_dir_recursive_absolute(parent)
		if mk != OK:
			return {"ok": false, "error": "cannot create dir %s err=%s" % [parent, mk], "error_code": "io_error"}

	var tmp_path: String = write_path + ".tmp"
	var tmp_global: String = global_path + ".tmp"

	var f: FileAccess = FileAccess.open(tmp_path, FileAccess.WRITE)
	if f == null:
		f = FileAccess.open(tmp_global, FileAccess.WRITE)
		if f == null:
			return {
				"ok": false,
				"error": "cannot write temp %s err=%s" % [tmp_path, FileAccess.get_open_error()],
				"error_code": "io_error",
			}
		tmp_path = tmp_global
		write_path = global_path

	f.store_string(content)
	f.flush()
	f.close()

	var target: String = write_path if write_path == global_path or FileAccess.file_exists(write_path + ".tmp") else global_path
	if FileAccess.file_exists(path + ".tmp"):
		tmp_path = path + ".tmp"
		target = path
	elif FileAccess.file_exists(tmp_global):
		tmp_path = tmp_global
		target = global_path

	if FileAccess.file_exists(target):
		DirAccess.remove_absolute(_resolve_path(target) if not target.begins_with("user://") else ProjectSettings.globalize_path(target))
		if target.begins_with("user://") or target.begins_with("res://"):
			var da := DirAccess.open(target.get_base_dir())
			if da:
				da.remove(target.get_file())

	var from_abs: String = _resolve_path(tmp_path) if tmp_path.begins_with("user://") or tmp_path.begins_with("res://") else tmp_path
	var to_abs: String = _resolve_path(target) if target.begins_with("user://") or target.begins_with("res://") else target
	var ren: Error = DirAccess.rename_absolute(from_abs, to_abs)
	if ren != OK:
		var tf: FileAccess = FileAccess.open(tmp_path, FileAccess.READ)
		if tf == null:
			tf = FileAccess.open(from_abs, FileAccess.READ)
		if tf == null:
			return {"ok": false, "error": "atomic rename failed err=%s" % ren, "error_code": "io_error"}
		var body: String = tf.get_as_text()
		tf.close()
		var outf: FileAccess = FileAccess.open(target, FileAccess.WRITE)
		if outf == null:
			outf = FileAccess.open(to_abs, FileAccess.WRITE)
		if outf == null:
			return {"ok": false, "error": "fallback write failed", "error_code": "io_error"}
		outf.store_string(body)
		outf.flush()
		outf.close()
		DirAccess.remove_absolute(from_abs)

	return {"ok": true}


func _resolve_path(path: String) -> String:
	if path.begins_with("user://") or path.begins_with("res://"):
		return ProjectSettings.globalize_path(path)
	return path


func _iso_now() -> String:
	var dt: Dictionary = Time.get_datetime_dict_from_system(true)
	return "%04d-%02d-%02dT%02d:%02d:%02dZ" % [
		int(dt.get("year", 1970)),
		int(dt.get("month", 1)),
		int(dt.get("day", 1)),
		int(dt.get("hour", 0)),
		int(dt.get("minute", 0)),
		int(dt.get("second", 0)),
	]


func _new_uuid() -> String:
	var rng := RandomNumberGenerator.new()
	rng.randomize()
	var b: PackedByteArray = PackedByteArray()
	for i in 16:
		b.append(rng.randi() % 256)
	b[6] = (b[6] & 0x0f) | 0x40
	b[8] = (b[8] & 0x3f) | 0x80
	return "%02x%02x%02x%02x-%02x%02x-%02x%02x-%02x%02x-%02x%02x%02x%02x%02x%02x" % [
		b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7],
		b[8], b[9], b[10], b[11], b[12], b[13], b[14], b[15],
	]
