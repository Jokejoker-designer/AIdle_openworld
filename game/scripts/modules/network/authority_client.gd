## AuthorityClient — Godot-side adapter for G6 local World Authority POC.
## Untrusted local mirror; updates only from server events or explicit snapshots.
## LOCAL POC only — not Nakama, not Colyseus, no public network transport.
class_name AuthorityClient
extends RefCounted

const Hasher = preload("res://scripts/modules/persist/entity_hasher.gd")
const WorldAuthorityLocalScript = preload("res://scripts/modules/network/world_authority_local.gd")

const POC_NOTE := "LOCAL in-process authority client — not production multiplayer (not Nakama/Colyseus)."

var client_id: String = ""
var actor_id: String = ""
var actor_type: String = "player"
var session_token: String = ""
var server: RefCounted = null

## LocalMirror fields
var world_revision: int = 0
var entities: Dictionary = {}
var entity_set_hash: String = ""
var applied_event_ids: Dictionary = {}
var last_ack_world_revision: int = 0
var last_ack_event_id: String = ""
var pending_receipts: Dictionary = {}


func _init(p_client_id: String = "", p_server: RefCounted = null) -> void:
	client_id = p_client_id
	server = p_server
	entity_set_hash = Hasher.entity_set_hash({})


## Connect to local server endpoint (in-process RefCounted; no URL/network).
func connect_client(p_actor_id: String, p_actor_type: String = "player") -> Dictionary:
	if server == null:
		return {"ok": false, "error": "no server bound"}
	actor_id = p_actor_id
	actor_type = p_actor_type
	var res: Dictionary = server.call("connect_client", client_id, p_actor_id, p_actor_type, true)
	if not res.get("ok", false):
		return res
	session_token = str(res["session_token"])
	var snap: Dictionary = res.get("snapshot", {}) as Dictionary
	_replace_from_snapshot_dict(snap)
	return res


func submit_and_preview(world_prompt: Dictionary) -> Dictionary:
	if session_token.is_empty():
		return {"ok": false, "error": "not connected"}
	# Preview is local-only; server only stores pending proposal (no mutation).
	var res: Dictionary = server.call("submit_proposal", session_token, world_prompt)
	if res.get("ok", false):
		res["preview"] = {
			"shown": true,
			"stages": ["wireframe", "hologram"],
			"durable_mutation": false,
		}
	return res


func confirm(request_id: String, confirmed_by: String) -> Dictionary:
	if session_token.is_empty():
		return {"ok": false, "error": "not connected"}
	return server.call("confirm_proposal", session_token, request_id, confirmed_by)


func commit(commit_request: Dictionary) -> Dictionary:
	if session_token.is_empty():
		return {"ok": false, "error": "not connected"}
	var receipt: Dictionary = server.call("commit", session_token, commit_request, "")
	# Receipt alone does not update durable mirror; sync via events/snapshot.
	if str(receipt.get("status", "")) in ["committed", "idempotent_replay"]:
		verify_receipt(receipt)
	return receipt


## Test helper: forged commit (wrong actor labels inside request body).
func attempt_forged_commit(forged_commit_request: Dictionary) -> Dictionary:
	if session_token.is_empty():
		return {"ok": false, "error": "not connected"}
	return server.call("commit", session_token, forged_commit_request, "")


## Test helper: claim another client_id while using own session.
func attempt_forged_client_claim(commit_request: Dictionary, claimed_client_id: String) -> Dictionary:
	if session_token.is_empty():
		return {"ok": false, "error": "not connected"}
	return server.call("commit", session_token, commit_request, claimed_client_id)


func attempt_direct_write() -> Dictionary:
	if server == null:
		return {"ok": false, "error": "no server"}
	return server.call("client_write_entity")


func sync(force_snapshot: bool = false) -> Dictionary:
	if session_token.is_empty():
		return {"ok": false, "error": "not connected"}
	if force_snapshot:
		var snap: Dictionary = server.call("get_snapshot", session_token, "")
		if snap.has("code") and not snap.get("ok", true):
			return snap
		_replace_from_snapshot_dict(snap)
		return {
			"ok": true,
			"mode": "snapshot",
			"world_revision": world_revision,
			"entity_set_hash": entity_set_hash,
		}

	var polled: Dictionary = server.call(
		"poll_events", session_token, last_ack_world_revision, last_ack_event_id
	)
	if not polled.get("ok", false):
		return polled

	var events: Array = polled.get("events", [])
	if events.size() > 0:
		var first: Dictionary = events[0]
		var first_rev := int(first["world_revision"])
		if first_rev > last_ack_world_revision + 1:
			var gap_snap: Dictionary = server.call("get_snapshot", session_token, "")
			_replace_from_snapshot_dict(gap_snap)
			return {
				"ok": true,
				"mode": "snapshot",
				"reason": "gap_detected",
				"world_revision": world_revision,
				"entity_set_hash": entity_set_hash,
			}

	var applied_count := 0
	for ev_any in events:
		var ev: Dictionary = ev_any
		var apply_res: Dictionary = apply_event(ev)
		if not apply_res.get("ok", false):
			var fail_snap: Dictionary = server.call("get_snapshot", session_token, "")
			_replace_from_snapshot_dict(fail_snap)
			return {
				"ok": true,
				"mode": "snapshot",
				"reason": str(apply_res.get("code", "apply_failed")),
				"world_revision": world_revision,
				"entity_set_hash": entity_set_hash,
			}
		if not apply_res.get("replayed", false):
			applied_count += 1

	return {
		"ok": true,
		"mode": "replay",
		"world_revision": world_revision,
		"entity_set_hash": entity_set_hash,
		"events_applied": applied_count,
	}


func reconnect(mode: String = "replay") -> Dictionary:
	if actor_id.is_empty():
		return {"ok": false, "error": "never connected"}
	var include_snap := mode == "snapshot"
	var res: Dictionary = server.call("connect_client", client_id, actor_id, actor_type, include_snap)
	if not res.get("ok", false):
		return res
	session_token = str(res["session_token"])
	if mode == "snapshot":
		var snap: Dictionary = res.get("snapshot", {}) as Dictionary
		if snap.is_empty():
			snap = server.call("get_snapshot", session_token, "")
		_replace_from_snapshot_dict(snap)
		return {
			"ok": true,
			"mode": "snapshot",
			"world_revision": world_revision,
			"entity_set_hash": entity_set_hash,
		}
	return sync(false)


## EventApplier: apply one server event. Out-of-order / forged → structured failure.
func apply_event(event: Dictionary) -> Dictionary:
	if event.is_empty():
		return {"ok": false, "code": "schema_invalid", "reason": "event must be object"}

	var event_id := str(event.get("event_id", ""))
	if event_id.is_empty():
		return {"ok": false, "code": "schema_invalid", "reason": "missing event_id"}

	if not bool(server.call("is_server_event", event_id)):
		return {
			"ok": false,
			"code": "client_forged",
			"reason": "event_id not in server outbox registry",
			"mutation": false,
		}

	if applied_event_ids.has(event_id):
		return {"ok": true, "replayed": true, "event_id": event_id}

	var rev := int(event.get("world_revision", -1))
	var expected_next := last_ack_world_revision + 1
	if rev != expected_next:
		return {
			"ok": false,
			"code": "out_of_order",
			"reason": "expected world_revision %d, got %d" % [expected_next, rev],
			"action": "snapshot_resync_or_structured_failure",
			"mutation": false,
		}

	var payload: Dictionary = event.get("payload", {}) as Dictionary
	var entity_ids: Array = payload.get("entity_ids", [])
	var new_hash: String = str(payload.get("entity_set_hash", ""))

	if not session_token.is_empty():
		var snap: Dictionary = server.call("get_snapshot", session_token, "")
		var server_entities: Dictionary = snap.get("entities", {}) as Dictionary
		if int(snap.get("world_revision", -1)) == rev:
			entities = {}
			for k in server_entities.keys():
				entities[str(k)] = (server_entities[k] as Dictionary).duplicate(true)
		else:
			for eid in entity_ids:
				var es := str(eid)
				if server_entities.has(es):
					entities[es] = (server_entities[es] as Dictionary).duplicate(true)
				elif entities.has(es):
					entities.erase(es)

	world_revision = rev
	entity_set_hash = Hasher.entity_set_hash(entities)
	if not new_hash.is_empty() and entity_set_hash != new_hash:
		world_revision = last_ack_world_revision
		return {
			"ok": false,
			"code": "integrity_fail",
			"reason": "local entity_set_hash != event payload entity_set_hash",
			"mutation": false,
		}

	applied_event_ids[event_id] = true
	last_ack_world_revision = rev
	last_ack_event_id = event_id
	return {
		"ok": true,
		"event_id": event_id,
		"world_revision": world_revision,
		"entity_set_hash": entity_set_hash,
	}


## ReceiptIntegrity: reject altered receipts; do not treat as durable truth alone.
func verify_receipt(receipt: Dictionary) -> Dictionary:
	if receipt.is_empty():
		return {"ok": false, "code": "schema_invalid"}

	var status := str(receipt.get("status", ""))
	if status not in ["committed", "idempotent_replay", "rejected", "conflicted"]:
		return {"ok": false, "code": "schema_invalid", "reason": "unknown status"}

	if status in ["rejected", "conflicted"]:
		return {"ok": true, "status": status, "mirror_updated": false}

	var receipt_id := str(receipt.get("receipt_id", ""))
	if receipt_id.is_empty():
		return {"ok": false, "code": "integrity_fail", "reason": "missing receipt_id"}

	var server_receipt: Variant = server.call("get_receipt", receipt_id)
	if server_receipt == null:
		return {
			"ok": false,
			"code": "integrity_fail",
			"reason": "receipt_id not issued by server",
			"mirror_updated": false,
		}
	var sr: Dictionary = server_receipt

	for key in [
		"status",
		"request_id",
		"old_world_revision",
		"new_world_revision",
		"entity_ids",
		"space_id",
	]:
		if sr.has(key) and str(receipt.get(key, null)) != str(sr.get(key, null)):
			# Deep compare for arrays via canonical stringify
			if key == "entity_ids":
				var Canon = load("res://scripts/modules/persist/canonical_json.gd")
				if Canon.stringify(receipt.get(key, [])) != Canon.stringify(sr.get(key, [])):
					return {
						"ok": false,
						"code": "integrity_fail",
						"reason": "altered receipt field: %s" % key,
						"mirror_updated": false,
					}
			elif typeof(receipt.get(key, null)) != typeof(sr.get(key, null)) or receipt.get(key) != sr.get(key):
				return {
					"ok": false,
					"code": "integrity_fail",
					"reason": "altered receipt field: %s" % key,
					"mirror_updated": false,
				}

	var Canon2 = load("res://scripts/modules/persist/canonical_json.gd")
	if Canon2.stringify(receipt.get("artifact_hashes", [])) != Canon2.stringify(sr.get("artifact_hashes", [])):
		return {
			"ok": false,
			"code": "integrity_fail",
			"reason": "altered artifact_hashes",
			"mirror_updated": false,
		}

	pending_receipts[receipt_id] = receipt.duplicate(true)
	return {"ok": true, "status": status, "mirror_updated": false, "verified": true}


func attempt_mirror_update_from_receipt_alone(receipt: Dictionary) -> Dictionary:
	var check: Dictionary = verify_receipt(receipt)
	if not check.get("ok", false):
		return {
			"ok": false,
			"code": str(check.get("code", "integrity_fail")),
			"reason": str(check.get("reason", "receipt integrity failed")),
			"mirror_not_updated_from_altered_receipt": true,
			"world_revision": world_revision,
			"entity_set_hash": entity_set_hash,
		}
	return {
		"ok": true,
		"mirror_updated": false,
		"note": "verified receipt stored; durable mirror updates only via events/snapshot",
		"world_revision": world_revision,
		"entity_set_hash": entity_set_hash,
	}


func get_mirror_head() -> Dictionary:
	var ids: Array = []
	for eid in entities.keys():
		var ent: Dictionary = entities[eid]
		if str(ent.get("status", "active")) != "tombstoned":
			ids.append(str(eid))
	ids.sort()
	return {
		"world_revision": world_revision,
		"entity_set_hash": entity_set_hash,
		"entity_ids": ids,
		"client_id": client_id,
	}


func _replace_from_snapshot_dict(snap: Dictionary) -> void:
	world_revision = int(snap.get("world_revision", 0))
	var ents: Dictionary = snap.get("entities", {}) as Dictionary
	entities = {}
	for k in ents.keys():
		entities[str(k)] = (ents[k] as Dictionary).duplicate(true)
	var h: String = str(snap.get("entity_set_hash", ""))
	if h.is_empty():
		entity_set_hash = Hasher.entity_set_hash(entities)
	else:
		entity_set_hash = h
	last_ack_world_revision = world_revision
	last_ack_event_id = ""
