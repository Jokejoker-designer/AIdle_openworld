## Local in-process World Authority server (G6-001 M2 POC).
## Pure GDScript mirror of services/world_authority_poc rules — NOT Nakama/Colyseus.
## No HTTP listen, no sockets, no outbound internet, no secrets.
## Clients propose; only this service mutates canonical world state.
class_name WorldAuthorityLocal
extends RefCounted

const Hasher = preload("res://scripts/modules/persist/entity_hasher.gd")
const Canon = preload("res://scripts/modules/persist/canonical_json.gd")

const DEFAULT_SPACE_ID := "home_01"
const POC_NOTE := "LOCAL authoritative World Commit simulator — not production multiplayer, not Nakama, not Colyseus."

var space_id: String = DEFAULT_SPACE_ID
var _world_revision: int = 0
## entity_id -> entity Dictionary (owner_id for ownership; not in set hash)
var _entities: Dictionary = {}
## session_token -> {client_id, actor_id, actor_type, session_id}
var _sessions: Dictionary = {}
## client_id -> session_token
var _client_tokens: Dictionary = {}
## request_id -> proposal record
var _proposals: Dictionary = {}
## request_id -> {fingerprint, receipt}
var _idempotency: Dictionary = {}
## ordered outbox of event envelopes
var _outbox: Array = []
## event_id registry (server-issued only)
var _event_ids: Dictionary = {}
## receipt_id -> receipt
var _receipts: Dictionary = {}
var _uuid_counter: int = 0


func _init(p_space_id: String = DEFAULT_SPACE_ID, seed_world_revision: int = 0) -> void:
	space_id = p_space_id
	_world_revision = seed_world_revision


# ------------------------------------------------------------------ API

func connect_client(
	client_id: String,
	actor_id: String,
	actor_type: String = "player",
	include_snapshot: bool = true
) -> Dictionary:
	if client_id.is_empty() or actor_id.is_empty():
		return {"ok": false, "error": "client_id and actor_id required"}
	if actor_type not in ["player", "companion", "system"]:
		return {"ok": false, "error": "invalid actor_type"}

	var old: Variant = _client_tokens.get(client_id, null)
	if old != null and _sessions.has(str(old)):
		_sessions.erase(str(old))

	var token := "tok_%s_%s" % [client_id, _hex_token(8)]
	var session_id := "sess_%s" % client_id
	_sessions[token] = {
		"client_id": client_id,
		"actor_id": actor_id,
		"actor_type": actor_type,
		"session_id": session_id,
	}
	_client_tokens[client_id] = token

	var result: Dictionary = {
		"ok": true,
		"session_token": token,
		"client_id": client_id,
		"actor_id": actor_id,
		"session_id": session_id,
		"world_revision": _world_revision,
		"entity_set_hash": entity_set_hash(),
		"space_id": space_id,
		"poc_note": POC_NOTE,
	}
	if include_snapshot:
		result["snapshot"] = _build_snapshot()
	return result


func submit_proposal(session_token: String, world_prompt: Dictionary) -> Dictionary:
	var session: Variant = _auth(session_token)
	if session == null:
		return _error_envelope("auth_failed", "invalid or missing session_token")
	var sess: Dictionary = session

	var v: Dictionary = _validate_world_prompt_min(world_prompt)
	if not v.get("ok", false):
		return {
			"ok": false,
			"status": "rejected",
			"code": "schema_invalid",
			"errors": v.get("errors", []),
			"world_revision": _world_revision,
			"entity_set_hash": entity_set_hash(),
		}

	var prompt: Dictionary = world_prompt.duplicate(true)
	var request_id := str(prompt["request_id"])
	var actor_player := str((prompt.get("actor", {}) as Dictionary).get("player_id", ""))

	if str(sess["actor_type"]) == "player" and actor_player != str(sess["actor_id"]):
		return {
			"ok": false,
			"status": "rejected",
			"code": "client_forged",
			"reason": "world_prompt.actor.player_id does not match session actor",
			"world_revision": _world_revision,
			"entity_set_hash": entity_set_hash(),
		}

	var conf: Dictionary = prompt.get("confirmation", {}) as Dictionary
	if conf.get("preview_required") != true:
		return {
			"ok": false,
			"status": "rejected",
			"code": "schema_invalid",
			"reason": "preview_required must be true",
			"world_revision": _world_revision,
			"entity_set_hash": entity_set_hash(),
		}

	# INV-CONFIRM-SERVER-TRANSITION: never admit client-supplied confirmed on submit.
	# Fail closed BEFORE proposal registration / revision / entity / outbox / receipt.
	# Only confirm_proposal may transition pending → confirmed.
	if str(conf.get("state", "")) == "confirmed":
		return {
			"ok": false,
			"status": "rejected",
			"code": "client_forged",
			"reason": "confirmation.state=confirmed is not accepted on submit; only confirm_proposal may confirm",
			"retryable": false,
			"world_revision": _world_revision,
			"entity_set_hash": entity_set_hash(),
		}

	# Force pending on every valid admission path (omit / pending / other non-confirmed).
	if not prompt.has("confirmation"):
		prompt["confirmation"] = {}
	var conf2: Dictionary = prompt["confirmation"]
	conf2["state"] = "pending"
	prompt["confirmation"] = conf2
	var state: String = "pending"

	var space := str((prompt.get("target", {}) as Dictionary).get("space_id", ""))
	if space != space_id:
		return {
			"ok": false,
			"status": "rejected",
			"code": "policy",
			"reason": "space_id mismatch: expected %s" % space_id,
			"world_revision": _world_revision,
			"entity_set_hash": entity_set_hash(),
		}

	if _proposals.has(request_id):
		var existing: Dictionary = _proposals[request_id]
		if Canon.stringify(existing["prompt"]) != Canon.stringify(prompt):
			return {
				"ok": false,
				"status": "rejected",
				"code": "policy",
				"reason": "duplicate request_id with different proposal body",
				"world_revision": _world_revision,
				"entity_set_hash": entity_set_hash(),
			}
		return {
			"ok": true,
			"request_id": request_id,
			"status": existing["state"],
			"world_revision": _world_revision,
			"entity_set_hash": entity_set_hash(),
		}

	_proposals[request_id] = {
		"prompt": prompt,
		"state": state,
		"client_id": sess["client_id"],
		"actor_id": sess["actor_id"],
		"submitted_at": _utcnow_iso(),
	}
	return {
		"ok": true,
		"request_id": request_id,
		"status": state,
		"world_revision": _world_revision,
		"entity_set_hash": entity_set_hash(),
	}


func confirm_proposal(session_token: String, request_id: String, confirmed_by: String) -> Dictionary:
	var session: Variant = _auth(session_token)
	if session == null:
		return _error_envelope("auth_failed", "invalid or missing session_token")
	var sess: Dictionary = session

	if not _proposals.has(request_id):
		return {
			"ok": false,
			"status": "rejected",
			"code": "policy",
			"reason": "unknown request_id",
			"world_revision": _world_revision,
			"entity_set_hash": entity_set_hash(),
		}

	var prop: Dictionary = _proposals[request_id]
	if str(prop["client_id"]) != str(sess["client_id"]):
		return {
			"ok": false,
			"status": "rejected",
			"code": "client_forged",
			"reason": "proposal owned by another client",
			"world_revision": _world_revision,
			"entity_set_hash": entity_set_hash(),
		}
	if confirmed_by != str(sess["actor_id"]):
		return {
			"ok": false,
			"status": "rejected",
			"code": "client_forged",
			"reason": "confirmed_by does not match session actor",
			"world_revision": _world_revision,
			"entity_set_hash": entity_set_hash(),
		}

	if str(prop["state"]) == "confirmed":
		return {
			"ok": true,
			"request_id": request_id,
			"confirmation_state": "confirmed",
			"world_revision": _world_revision,
			"entity_set_hash": entity_set_hash(),
		}

	var prompt: Dictionary = prop["prompt"]
	if not prompt.has("confirmation"):
		prompt["confirmation"] = {}
	var conf: Dictionary = prompt["confirmation"]
	conf["state"] = "confirmed"
	conf["confirmed_by"] = confirmed_by
	prompt["confirmation"] = conf
	if not prompt.has("target"):
		prompt["target"] = {}
	var target: Dictionary = prompt["target"]
	target["expected_world_revision"] = _world_revision
	prompt["target"] = target
	prop["prompt"] = prompt
	prop["state"] = "confirmed"
	prop["confirmed_at"] = _utcnow_iso()
	_proposals[request_id] = prop

	return {
		"ok": true,
		"request_id": request_id,
		"confirmation_state": "confirmed",
		"world_revision": _world_revision,
		"entity_set_hash": entity_set_hash(),
	}


func commit(
	session_token: String,
	commit_request: Dictionary,
	claimed_client_id: String = ""
) -> Dictionary:
	var session: Variant = _auth(session_token)
	if session == null:
		return _make_receipt_rejected(
			commit_request,
			"auth_failed",
			"invalid or missing session_token"
		)
	var sess: Dictionary = session

	if not claimed_client_id.is_empty() and claimed_client_id != str(sess["client_id"]):
		return _make_receipt_rejected(
			commit_request,
			"client_forged",
			"claimed client_id=%s does not match session client_id" % claimed_client_id,
			_world_revision
		)

	var v: Dictionary = _validate_commit_request_min(commit_request)
	if not v.get("ok", false):
		return _make_receipt_rejected(
			commit_request,
			"schema_invalid",
			str(v.get("reason", "schema_invalid")),
			_world_revision
		)

	var req: Dictionary = commit_request.duplicate(true)
	var request_id := str(req["request_id"])
	var prompt_id := str(req["prompt_id"])
	var req_space := str(req["space_id"])
	var expected_rev := int(req["expected_world_revision"])
	var actor_id := str((req.get("actor", {}) as Dictionary).get("actor_id", ""))
	var confirmed_by := str((req.get("confirmation", {}) as Dictionary).get("confirmed_by", ""))
	var mutation_class := str(req["mutation_class"])
	var source := str((req.get("authority", {}) as Dictionary).get("source", ""))

	if source != "server_authoritative":
		return _make_receipt_rejected(
			req,
			"policy",
			"authority.source=%s not allowed in G6 POC (server_authoritative only)" % source,
			_world_revision
		)

	if actor_id != str(sess["actor_id"]):
		return _make_receipt_rejected(
			req, "client_forged", "actor.actor_id does not match session actor", _world_revision
		)
	if confirmed_by != str(sess["actor_id"]):
		return _make_receipt_rejected(
			req,
			"client_forged",
			"confirmation.confirmed_by does not match session actor",
			_world_revision
		)
	if str((req.get("actor", {}) as Dictionary).get("actor_type", "")) != str(sess["actor_type"]):
		return _make_receipt_rejected(
			req, "client_forged", "actor.actor_type does not match session", _world_revision
		)
	if req_space != space_id:
		return _make_receipt_rejected(
			req, "policy", "space_id mismatch: expected %s" % space_id, _world_revision
		)

	if not _proposals.has(request_id):
		return _make_receipt_rejected(
			req, "confirmation_missing", "no registered proposal for request_id", _world_revision
		)
	var prop: Dictionary = _proposals[request_id]
	if str(prop["state"]) != "confirmed":
		return _make_receipt_rejected(
			req, "confirmation_missing", "proposal not confirmed", _world_revision
		)
	var prompt: Dictionary = prop["prompt"]
	if str(prompt.get("prompt_id", "")) != prompt_id:
		return _make_receipt_rejected(
			req, "policy", "prompt_id does not match registered proposal", _world_revision
		)
	if str((prompt.get("target", {}) as Dictionary).get("space_id", "")) != req_space:
		return _make_receipt_rejected(
			req, "policy", "space_id does not match proposal target", _world_revision
		)
	if str(prop["actor_id"]) != str(sess["actor_id"]) or str(prop["client_id"]) != str(sess["client_id"]):
		return _make_receipt_rejected(
			req, "client_forged", "proposal/session actor or client mismatch", _world_revision
		)

	var fingerprint := _fingerprint(req, prompt)

	# Idempotency before revision check
	if _idempotency.has(request_id):
		var entry: Dictionary = _idempotency[request_id]
		if str(entry["fingerprint"]) == fingerprint:
			var prior: Dictionary = (entry["receipt"] as Dictionary).duplicate(true)
			prior["status"] = "idempotent_replay"
			prior["occurred_at"] = _utcnow_iso()
			prior["idempotency"] = {
				"duplicate_of_request_id": request_id,
				"prior_receipt_id": prior["receipt_id"],
				"replayed": true,
			}
			prior.erase("rejection")
			prior.erase("conflict")
			return prior
		return _make_receipt_rejected(
			req,
			"policy",
			"idempotency payload mismatch for request_id",
			_world_revision
		)

	var op := str(prompt.get("operation", "create"))
	var ownership_err := _check_ownership(op, prompt, str(sess["actor_id"]))
	if not ownership_err.is_empty():
		return _make_receipt_rejected(req, "ownership", ownership_err, _world_revision)

	if expected_rev != _world_revision:
		return _make_receipt_conflicted(req, expected_rev, _world_revision)

	var old_rev := _world_revision
	var apply_res: Dictionary = _apply_mutation(op, prompt, str(sess["actor_id"]), request_id)
	if apply_res.has("error"):
		return _make_receipt_rejected(req, "policy", str(apply_res["error"]), _world_revision)

	var entity_ids: Array = apply_res.get("entity_ids", [])
	_world_revision = old_rev + 1
	var new_rev := _world_revision
	var set_hash := entity_set_hash()

	var receipt_id := _new_uuid()
	var artifact_hashes: Array = []
	for eid in entity_ids:
		if _entities.has(str(eid)):
			artifact_hashes.append({
				"role": "entity_snapshot",
				"algorithm": "sha256",
				"hash": Hasher.entity_hash(_entities[str(eid)]),
			})
	artifact_hashes.append({
		"role": "entity_set",
		"algorithm": "sha256",
		"hash": set_hash,
	})

	var receipt: Dictionary = {
		"schema_version": "1.0.0",
		"receipt_id": receipt_id,
		"request_id": request_id,
		"status": "committed",
		"occurred_at": _utcnow_iso(),
		"space_id": space_id,
		"authority": {
			"commit_path": "world_commit_service",
			"issuer": "world_commit_service",
		},
		"old_world_revision": old_rev,
		"new_world_revision": new_rev,
		"entity_ids": entity_ids.duplicate(),
		"artifact_hashes": artifact_hashes,
		"trace_id": str(req.get("trace_id", "trace-%s" % request_id.substr(0, mini(8, request_id.length())))),
	}
	_receipts[receipt_id] = receipt.duplicate(true)
	_idempotency[request_id] = {
		"fingerprint": fingerprint,
		"receipt": receipt.duplicate(true),
	}

	var event: Dictionary = _append_outbox_event(
		request_id,
		str(sess["actor_id"]),
		new_rev,
		receipt,
		set_hash,
		str(receipt["trace_id"])
	)
	var receipt_out: Dictionary = receipt.duplicate(true)
	receipt_out["_event_id"] = event["event_id"]
	receipt_out["_entity_set_hash"] = set_hash
	return receipt_out


func get_snapshot(session_token: String, p_space_id: String = "") -> Dictionary:
	var session: Variant = _auth(session_token)
	if session == null:
		return _error_envelope("auth_failed", "invalid or missing session_token")
	if not p_space_id.is_empty() and p_space_id != space_id:
		return {"ok": false, "code": "policy", "reason": "unknown space_id %s" % p_space_id}
	var snap: Dictionary = _build_snapshot()
	snap["ok"] = true
	return snap


func poll_events(
	session_token: String,
	after_world_revision: int,
	after_event_id: String = ""
) -> Dictionary:
	var session: Variant = _auth(session_token)
	if session == null:
		return _error_envelope("auth_failed", "invalid or missing session_token")

	var events: Array = []
	var started := after_event_id.is_empty()
	for ev_any in _outbox:
		var ev: Dictionary = ev_any
		var rev := int(ev["world_revision"])
		if rev <= after_world_revision:
			continue
		if not after_event_id.is_empty() and not started:
			if str(ev["event_id"]) == after_event_id:
				started = true
			continue
		events.append(ev.duplicate(true))

	return {
		"ok": true,
		"events": events,
		"head_world_revision": _world_revision,
		"head_entity_set_hash": entity_set_hash(),
	}


func get_head(session_token: String) -> Dictionary:
	var session: Variant = _auth(session_token)
	if session == null:
		return _error_envelope("auth_failed", "invalid or missing session_token")
	return {
		"ok": true,
		"world_revision": _world_revision,
		"entity_set_hash": entity_set_hash(),
	}


# ---- Forbidden durable APIs (fail closed) ----

func client_write_entity(_a: Variant = null, _b: Variant = null) -> Dictionary:
	return {
		"ok": false,
		"status": "rejected",
		"code": "client_forged",
		"reason": "direct client entity write is forbidden; use preview→confirm→commit",
		"world_revision": _world_revision,
		"entity_set_hash": entity_set_hash(),
		"mutation": false,
	}


func client_set_world_revision(_a: Variant = null) -> Dictionary:
	return {
		"ok": false,
		"status": "rejected",
		"code": "client_forged",
		"reason": "clients may not set world_revision",
		"world_revision": _world_revision,
		"entity_set_hash": entity_set_hash(),
		"mutation": false,
	}


func client_issue_receipt(_a: Variant = null) -> Dictionary:
	return {
		"ok": false,
		"status": "rejected",
		"code": "client_forged",
		"reason": "only world_commit_service may issue receipts",
		"world_revision": _world_revision,
		"entity_set_hash": entity_set_hash(),
		"mutation": false,
	}


func client_publish_event(_a: Variant = null) -> Dictionary:
	return {
		"ok": false,
		"status": "rejected",
		"code": "client_forged",
		"reason": "only server outbox may publish authoritative events",
		"world_revision": _world_revision,
		"entity_set_hash": entity_set_hash(),
		"mutation": false,
	}


# ---- Introspection ----

func entity_set_hash() -> String:
	return Hasher.entity_set_hash(_entities)


func world_revision() -> int:
	return _world_revision


func entity_count() -> int:
	var n := 0
	for eid in _entities.keys():
		var e: Dictionary = _entities[eid]
		if str(e.get("status", "active")) != "tombstoned":
			n += 1
	return n


func get_entity(entity_id: String) -> Variant:
	if not _entities.has(entity_id):
		return null
	return (_entities[entity_id] as Dictionary).duplicate(true)


func get_receipt(receipt_id: String) -> Variant:
	if not _receipts.has(receipt_id):
		return null
	return (_receipts[receipt_id] as Dictionary).duplicate(true)


func is_server_event(event_id: String) -> bool:
	return _event_ids.has(event_id)


func outbox_len() -> int:
	return _outbox.size()


# ------------------------------------------------------------------ internals

func _auth(session_token: String) -> Variant:
	if session_token.is_empty():
		return null
	if not _sessions.has(session_token):
		return null
	return _sessions[session_token]


func _error_envelope(code: String, reason: String) -> Dictionary:
	return {
		"ok": false,
		"code": code,
		"reason": reason,
		"world_revision": _world_revision,
		"entity_set_hash": entity_set_hash(),
	}


func _build_snapshot() -> Dictionary:
	var entities: Dictionary = {}
	for eid in _entities.keys():
		var ent: Dictionary = _entities[eid]
		if str(ent.get("status", "active")) != "tombstoned":
			entities[str(eid)] = ent.duplicate(true)
	return {
		"world_revision": _world_revision,
		"entities": entities,
		"entity_set_hash": entity_set_hash(),
		"space_id": space_id,
	}


func _fingerprint(req: Dictionary, prompt: Dictionary) -> String:
	var material: Dictionary = {
		"v": "aidle_world_authority_fp_v1",
		"request_id": str(req["request_id"]),
		"prompt_id": str(req["prompt_id"]),
		"space_id": str(req["space_id"]),
		"mutation_class": str(req["mutation_class"]),
		"actor_id": str((req.get("actor", {}) as Dictionary).get("actor_id", "")),
		"confirmed_world_prompt": prompt,
	}
	return Hasher.sha256_hex(Canon.stringify(material))


func _check_ownership(op: String, prompt: Dictionary, actor_id: String) -> String:
	if op in ["create", "enrich", "gift_proposal"]:
		return ""
	if op in ["modify", "delete"]:
		var eid = (prompt.get("target", {}) as Dictionary).get("entity_id", null)
		if eid == null or str(eid).is_empty():
			return "modify/delete requires target.entity_id"
		if not _entities.has(str(eid)):
			return "entity not found: %s" % eid
		var ent: Dictionary = _entities[str(eid)]
		if str(ent.get("status", "active")) == "tombstoned":
			return "entity not found: %s" % eid
		var owner := str(ent.get("owner_id", ""))
		if owner != actor_id:
			return "actor %s does not own entity %s (owner=%s)" % [actor_id, eid, owner]
	return ""


func _apply_mutation(op: String, prompt: Dictionary, actor_id: String, request_id: String) -> Dictionary:
	var target: Dictionary = prompt.get("target", {}) as Dictionary
	var entity_body: Dictionary = prompt.get("entity", {}) as Dictionary
	var ent_space := str(target.get("space_id", space_id))
	var chunk_id := str(target.get("chunk_id", "0_0"))
	var prompt_id := str(prompt.get("prompt_id", ""))

	if op == "create":
		var compact := request_id.replace("-", "")
		var eid := "ent_%s" % compact.substr(0, mini(12, compact.length()))
		if _entities.has(eid) and str((_entities[eid] as Dictionary).get("status", "active")) != "tombstoned":
			return {"error": "entity id collision: %s" % eid}
		var ent: Dictionary = {
			"entity_id": eid,
			"kind": entity_body.get("kind", ""),
			"recipe_id": entity_body.get("recipe_id", ""),
			"transform": (entity_body.get("transform", {}) as Dictionary).duplicate(true),
			"bounds": (entity_body.get("bounds", {}) as Dictionary).duplicate(true),
			"interaction_tags": (entity_body.get("interaction_tags", []) as Array).duplicate(),
			"space_id": ent_space,
			"chunk_id": chunk_id,
			"status": "active",
			"origin_request_id": request_id,
			"origin_prompt_id": prompt_id,
			"owner_id": actor_id,
		}
		_entities[eid] = ent
		return {"entity_ids": [eid]}

	if op == "modify":
		var eid2 := str(target.get("entity_id", ""))
		var ent2: Dictionary = _entities[eid2]
		if entity_body.has("kind"):
			ent2["kind"] = entity_body["kind"]
		if entity_body.has("recipe_id"):
			ent2["recipe_id"] = entity_body["recipe_id"]
		if entity_body.has("transform"):
			ent2["transform"] = (entity_body["transform"] as Dictionary).duplicate(true)
		if entity_body.has("bounds"):
			ent2["bounds"] = (entity_body["bounds"] as Dictionary).duplicate(true)
		if entity_body.has("interaction_tags"):
			ent2["interaction_tags"] = (entity_body["interaction_tags"] as Array).duplicate()
		_entities[eid2] = ent2
		return {"entity_ids": [eid2]}

	if op == "delete":
		var eid3 := str(target.get("entity_id", ""))
		var ent3: Dictionary = _entities[eid3]
		ent3["status"] = "tombstoned"
		_entities[eid3] = ent3
		return {"entity_ids": [eid3]}

	if op in ["enrich", "gift_proposal"]:
		var eid4 = target.get("entity_id", null)
		if eid4 != null and _entities.has(str(eid4)):
			return {"entity_ids": [str(eid4)]}
		return {"entity_ids": []}

	return {"error": "unsupported operation: %s" % op}


func _append_outbox_event(
	request_id: String,
	actor_id: String,
	p_world_revision: int,
	receipt: Dictionary,
	p_entity_set_hash: String,
	trace_id: String
) -> Dictionary:
	var event_id := _new_uuid()
	var event: Dictionary = {
		"event_id": event_id,
		"event_type": "world.mutation_committed",
		"event_version": "1.0.0",
		"occurred_at": receipt["occurred_at"],
		"request_id": request_id,
		"space_id": space_id,
		"world_revision": p_world_revision,
		"actor_id": actor_id,
		"payload": {
			"receipt_id": receipt["receipt_id"],
			"entity_ids": (receipt.get("entity_ids", []) as Array).duplicate(),
			"old_world_revision": receipt["old_world_revision"],
			"new_world_revision": receipt["new_world_revision"],
			"entity_set_hash": p_entity_set_hash,
		},
		"trace_id": trace_id,
	}
	_outbox.append(event)
	_event_ids[event_id] = true
	return event


func _make_receipt_rejected(
	req: Dictionary,
	code: String,
	reason: String,
	old_revision: int = -1
) -> Dictionary:
	var request_id := str(req.get("request_id", "00000000-0000-4000-8000-000000000000"))
	if not _looks_like_uuid(request_id):
		request_id = "00000000-0000-4000-8000-000000000000"
	var receipt: Dictionary = {
		"schema_version": "1.0.0",
		"receipt_id": _new_uuid(),
		"request_id": request_id,
		"status": "rejected",
		"occurred_at": _utcnow_iso(),
		"space_id": str(req.get("space_id", space_id)),
		"authority": {
			"commit_path": "world_commit_service",
			"issuer": "world_commit_service",
		},
		"rejection": {"code": code, "reason": reason.substr(0, mini(512, reason.length()))},
	}
	if old_revision >= 0:
		receipt["old_world_revision"] = old_revision
	if req.has("trace_id"):
		receipt["trace_id"] = str(req["trace_id"])
	return receipt


func _make_receipt_conflicted(req: Dictionary, expected: int, actual: int) -> Dictionary:
	return {
		"schema_version": "1.0.0",
		"receipt_id": _new_uuid(),
		"request_id": str(req["request_id"]),
		"status": "conflicted",
		"occurred_at": _utcnow_iso(),
		"space_id": str(req.get("space_id", space_id)),
		"authority": {
			"commit_path": "world_commit_service",
			"issuer": "world_commit_service",
		},
		"old_world_revision": actual,
		"conflict": {
			"code": "revision_mismatch",
			"expected_world_revision": expected,
			"actual_world_revision": actual,
			"diff_ref": "conflict_diff://%s/rev_%d_vs_%d" % [space_id, expected, actual],
		},
		"trace_id": str(req.get("trace_id", "trace-conflict-%d" % expected)),
	}


func _validate_world_prompt_min(wp: Dictionary) -> Dictionary:
	var errors: Array = []
	for key in ["schema_version", "prompt_id", "request_id", "operation", "target", "entity", "confirmation"]:
		if not wp.has(key):
			errors.append("missing %s" % key)
	if wp.has("confirmation"):
		var conf: Dictionary = wp["confirmation"]
		if conf.get("preview_required") != true:
			errors.append("preview_required must be true")
	if errors.is_empty():
		return {"ok": true}
	return {"ok": false, "errors": errors}


func _validate_commit_request_min(cr: Dictionary) -> Dictionary:
	for key in [
		"schema_version",
		"request_id",
		"prompt_id",
		"space_id",
		"expected_world_revision",
		"actor",
		"mutation_class",
		"authority",
		"confirmation",
	]:
		if not cr.has(key):
			return {"ok": false, "reason": "missing %s" % key}
	var auth: Dictionary = cr["authority"]
	if str(auth.get("commit_path", "")) != "world_commit_service":
		return {"ok": false, "reason": "authority.commit_path must be world_commit_service"}
	var src := str(auth.get("source", ""))
	if src == "client_authoritative":
		return {"ok": false, "reason": "client_authoritative not allowed"}
	var conf: Dictionary = cr["confirmation"]
	if str(conf.get("state", "")) != "confirmed":
		return {"ok": false, "reason": "confirmation.state must be confirmed"}
	if not conf.has("confirmed_by"):
		return {"ok": false, "reason": "confirmation.confirmed_by required"}
	var actor: Dictionary = cr["actor"]
	if not actor.has("actor_id") or not actor.has("actor_type"):
		return {"ok": false, "reason": "actor.actor_id and actor_type required"}
	return {"ok": true}


func _new_uuid() -> String:
	_uuid_counter += 1
	# Deterministic-enough POC UUID (version-ish 4 shape, no crypto secrets)
	var a := "%08x" % (0x10000000 + (_uuid_counter * 17) % 0x0fffffff)
	var b := "%04x" % (0x4000 + (_uuid_counter * 3) % 0x0fff)
	var c := "%04x" % (0x8000 + (_uuid_counter * 7) % 0x3fff)
	var d := "%04x" % ((_uuid_counter * 11) % 0xffff)
	var e := "%012x" % ((_uuid_counter * 13 + Time.get_ticks_usec()) % 0xffffffffffff)
	return "%s-%s-%s-%s-%s" % [a, b, c, d, e]


func _hex_token(n_bytes: int) -> String:
	var out := ""
	for i in n_bytes:
		out += "%02x" % ((Time.get_ticks_usec() + _uuid_counter * 31 + i * 97) % 256)
		_uuid_counter += 1
	return out


func _utcnow_iso() -> String:
	var t := Time.get_datetime_dict_from_system(true)
	return "%04d-%02d-%02dT%02d:%02d:%02dZ" % [
		t["year"], t["month"], t["day"], t["hour"], t["minute"], t["second"]
	]


func _looks_like_uuid(s: String) -> bool:
	# Simple shape check: 8-4-4-4-12 hex with dashes
	if s.length() != 36:
		return false
	if s[8] != "-" or s[13] != "-" or s[18] != "-" or s[23] != "-":
		return false
	return true
