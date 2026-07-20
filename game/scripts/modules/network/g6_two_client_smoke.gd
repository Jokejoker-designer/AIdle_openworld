## G6-001 M2 headless two-client authority POC smoke.
## Run:
##   tools\Godot_v4.3-stable_win64_console.exe --headless --path game \
##     -s res://scripts/modules/network/g6_two_client_smoke.gd
##
## Pure GDScript in-process dual-client simulator (mirrors M1 rules).
## LOCAL POC only — not Nakama, not Colyseus, no HTTP listen, no outbound internet.
## Exit 0 on pass. Prints G6_TWO_CLIENT_SMOKE=PASS|FAIL.
extends SceneTree

const SERVER_PATH := "res://scripts/modules/network/world_authority_local.gd"
const CLIENT_PATH := "res://scripts/modules/network/authority_client.gd"

const SPACE_ID := "home_01"
const CLIENT_A_ID := "client_a"
const CLIENT_B_ID := "client_b"
const ACTOR_A := "player_a"
const ACTOR_B := "player_b"

## Deterministic fixture UUIDs (valid create path)
const PROMPT_ID := "550e8400-e29b-41d4-a716-446655440000"
const REQUEST_ID := "bd5a8351-2b09-4acd-9520-19875098c928"
const FORGE_REQUEST_ID := "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"
const FORGE_PROMPT_ID := "ffffffff-1111-4222-8333-444444444444"
## Confirm-bypass exploit fixtures (client-supplied confirmation.state=confirmed on submit)
const BYPASS_REQUEST_ID := "cccccccc-dddd-4eee-8fff-000000000001"
const BYPASS_PROMPT_ID := "cccccccc-dddd-4eee-8fff-000000000002"

var _failures: PackedStringArray = []
var _passed: int = 0
var _fatal: bool = false
var _ServerScript: GDScript
var _ClientScript: GDScript


func _initialize() -> void:
	print("[G6-001 M2 two-client smoke] starting…")
	print("  POC_CLASS=LOCAL_IN_PROCESS (not Nakama, not Colyseus)")
	print("  TRANSPORT=in-process direct method calls (no HTTP, no sockets)")
	print("  client_ids: %s, %s" % [CLIENT_A_ID, CLIENT_B_ID])

	_ServerScript = _require_script(SERVER_PATH, "WorldAuthorityLocal")
	_ClientScript = _require_script(CLIENT_PATH, "AuthorityClient")
	if _fatal or not _failures.is_empty():
		printerr("[G6 two-client smoke] hard fail during script load — aborting")
		_finish()
		return

	_run_matrix()
	_finish()


func _require_script(path: String, label: String) -> GDScript:
	if not ResourceLoader.exists(path):
		_fail("script_missing", "%s path=%s" % [label, path])
		_fatal = true
		return null
	var loaded: Resource = load(path)
	if loaded == null:
		_fail("script_load_null", "%s path=%s" % [label, path])
		_fatal = true
		return null
	var script: GDScript = loaded as GDScript
	if script == null or not script.can_instantiate():
		_fail("script_cannot_instantiate", "%s path=%s" % [label, path])
		_fatal = true
		return null
	print("  LOAD OK  %s" % label)
	return script


func _run_matrix() -> void:
	# ---- Setup: one local server, two clients ----
	var server: RefCounted = _ServerScript.new(SPACE_ID, 0)
	var client_a: RefCounted = _ClientScript.new(CLIENT_A_ID, server)
	var client_b: RefCounted = _ClientScript.new(CLIENT_B_ID, server)

	var ca: Dictionary = client_a.call("connect_client", ACTOR_A, "player")
	var cb: Dictionary = client_b.call("connect_client", ACTOR_B, "player")
	if not ca.get("ok", false) or not cb.get("ok", false):
		_fail("connect", "client_a.ok=%s client_b.ok=%s" % [ca.get("ok"), cb.get("ok")])
		return
	_ok("connect_both clients=%s,%s" % [CLIENT_A_ID, CLIENT_B_ID])

	var head0: Dictionary = server.call("get_head", str(ca["session_token"]))
	var r0 := int(head0.get("world_revision", -1))
	var h0 := str(head0.get("entity_set_hash", ""))
	if r0 != 0:
		_fail("seed_revision", "expected 0 got %d" % r0)
		return
	_ok("seed world_revision=0 entity_set_hash=%s" % h0.substr(0, 12))

	# ---- TM-VALID-COMMIT-CONVERGE: preview → confirm → commit ----
	var prompt: Dictionary = _make_create_prompt(REQUEST_ID, PROMPT_ID, ACTOR_A, r0)
	var sub: Dictionary = client_a.call("submit_and_preview", prompt)
	if not sub.get("ok", false):
		_fail("submit_proposal", str(sub))
		return
	if int(server.call("world_revision")) != r0:
		_fail("submit_no_mutation", "revision advanced on submit")
		return
	if not (sub.get("preview", {}) as Dictionary).get("shown", false):
		_fail("preview", "preview not shown")
		return
	_ok("submit_and_preview request_id=%s status=%s" % [sub.get("request_id"), sub.get("status")])

	var conf: Dictionary = client_a.call("confirm", REQUEST_ID, ACTOR_A)
	if not conf.get("ok", false) or str(conf.get("confirmation_state", "")) != "confirmed":
		_fail("confirm", str(conf))
		return
	if int(server.call("world_revision")) != r0:
		_fail("confirm_no_mutation", "revision advanced on confirm")
		return
	_ok("confirm confirmation_state=confirmed")

	var commit_req: Dictionary = _make_commit_request(
		REQUEST_ID, PROMPT_ID, ACTOR_A, "player", r0
	)
	var receipt: Dictionary = client_a.call("commit", commit_req)
	if str(receipt.get("status", "")) != "committed":
		_fail("valid_commit", "status=%s receipt=%s" % [receipt.get("status"), receipt])
		return
	if str((receipt.get("authority", {}) as Dictionary).get("issuer", "")) != "world_commit_service":
		_fail("issuer", "expected world_commit_service")
		return
	var r1 := int(receipt.get("new_world_revision", -1))
	if r1 != r0 + 1:
		_fail("revision_bump", "expected %d got %d" % [r0 + 1, r1])
		return
	_ok("valid_commit status=committed new_world_revision=%d" % r1)

	# Client A sync (events)
	var sync_a: Dictionary = client_a.call("sync", false)
	if not sync_a.get("ok", false):
		_fail("sync_a", str(sync_a))
		return
	# Client B converge via poll/replay
	var sync_b: Dictionary = client_b.call("sync", false)
	if not sync_b.get("ok", false):
		_fail("sync_b", str(sync_b))
		return

	var head_a: Dictionary = client_a.call("get_mirror_head")
	var head_b: Dictionary = client_b.call("get_mirror_head")
	var head_s: Dictionary = server.call("get_head", str(ca["session_token"]))
	var sa_rev := int(head_a.get("world_revision", -1))
	var sb_rev := int(head_b.get("world_revision", -1))
	var ss_rev := int(head_s.get("world_revision", -1))
	var sa_hash := str(head_a.get("entity_set_hash", ""))
	var sb_hash := str(head_b.get("entity_set_hash", ""))
	var ss_hash := str(head_s.get("entity_set_hash", ""))

	if not (sa_rev == sb_rev and sb_rev == ss_rev and sa_rev == r1):
		_fail(
			"converge_revision",
			"A=%d B=%d S=%d expected=%d" % [sa_rev, sb_rev, ss_rev, r1]
		)
		return
	if not (sa_hash == sb_hash and sb_hash == ss_hash and not sa_hash.is_empty()):
		_fail(
			"converge_hash",
			"A=%s B=%s S=%s" % [sa_hash.substr(0, 12), sb_hash.substr(0, 12), ss_hash.substr(0, 12)]
		)
		return
	var entity_ids_a: Array = head_a.get("entity_ids", [])
	if entity_ids_a.size() != 1:
		_fail("entity_count", "expected 1 got %d" % entity_ids_a.size())
		return
	_ok(
		"TM-VALID-COMMIT-CONVERGE rev=%d hash=%s entities=%s"
		% [sa_rev, sa_hash.substr(0, 16), entity_ids_a]
	)

	# ---- TM-FORGED-ACTOR-REJECT + TM-FORGED-LEAVES-PEER-UNCHANGED ----
	var pre_forge_rev := int(server.call("world_revision"))
	var pre_forge_hash := str(server.call("entity_set_hash"))

	# New pending proposal owned by A, then commit with forged actor_id player_b
	var forge_prompt: Dictionary = _make_create_prompt(
		FORGE_REQUEST_ID, FORGE_PROMPT_ID, ACTOR_A, pre_forge_rev
	)
	# Slightly different entity so it is a distinct proposal
	var forge_ent: Dictionary = forge_prompt["entity"]
	forge_ent["recipe_id"] = "cozy_house_forged_attempt"
	forge_prompt["entity"] = forge_ent
	var fsub: Dictionary = client_a.call("submit_and_preview", forge_prompt)
	if not fsub.get("ok", false):
		_fail("forge_setup_submit", str(fsub))
		return
	var fconf: Dictionary = client_a.call("confirm", FORGE_REQUEST_ID, ACTOR_A)
	if not fconf.get("ok", false):
		_fail("forge_setup_confirm", str(fconf))
		return

	var forged_req: Dictionary = _make_commit_request(
		FORGE_REQUEST_ID, FORGE_PROMPT_ID, ACTOR_B, "player", pre_forge_rev
	)
	# Use actor_id player_b while session is player_a
	var forged_receipt: Dictionary = client_a.call("attempt_forged_commit", forged_req)
	if str(forged_receipt.get("status", "")) != "rejected":
		_fail("forged_status", "expected rejected got %s" % forged_receipt.get("status"))
		return
	var rej_code := str((forged_receipt.get("rejection", {}) as Dictionary).get("code", ""))
	if rej_code not in ["client_forged", "auth_failed", "ownership"]:
		_fail("forged_code", "unexpected code=%s" % rej_code)
		return
	if int(server.call("world_revision")) != pre_forge_rev:
		_fail("forged_revision_changed", "server revision mutated after forge")
		return
	if str(server.call("entity_set_hash")) != pre_forge_hash:
		_fail("forged_hash_changed", "entity_set_hash mutated after forge")
		return
	_ok("TM-FORGED-ACTOR-REJECT code=%s" % rej_code)

	# Peer B unchanged after forge
	var sync_b2: Dictionary = client_b.call("sync", false)
	if not sync_b2.get("ok", false):
		_fail("forge_peer_sync", str(sync_b2))
		return
	var head_b2: Dictionary = client_b.call("get_mirror_head")
	if int(head_b2.get("world_revision", -1)) != pre_forge_rev:
		_fail("peer_revision_after_forge", "B diverged after forge reject")
		return
	if str(head_b2.get("entity_set_hash", "")) != pre_forge_hash:
		_fail("peer_hash_after_forge", "B hash diverged after forge reject")
		return
	_ok("TM-FORGED-LEAVES-PEER-UNCHANGED rev=%d" % pre_forge_rev)

	# Direct write reject
	var dw: Dictionary = client_a.call("attempt_direct_write")
	if dw.get("mutation", true) != false or str(dw.get("status", "")) != "rejected":
		_fail("direct_write", str(dw))
		return
	if int(server.call("world_revision")) != pre_forge_rev:
		_fail("direct_write_mutation", "revision changed")
		return
	_ok("TM-DIRECT-WRITE-REJECT")

	# ---- AT-G6-CONFIRM-BYPASS-REJECT ----
	# Client must NOT skip confirm_proposal by submitting state=confirmed.
	# Reject before registration; revision/hash/entity/outbox unchanged; commit fails.
	var pre_bypass_rev := int(server.call("world_revision"))
	var pre_bypass_hash := str(server.call("entity_set_hash"))
	var pre_bypass_entities := int(server.call("entity_count"))
	var pre_bypass_outbox := int(server.call("outbox_len"))

	var bypass_prompt: Dictionary = _make_create_prompt(
		BYPASS_REQUEST_ID, BYPASS_PROMPT_ID, ACTOR_A, pre_bypass_rev
	)
	var bypass_ent: Dictionary = bypass_prompt["entity"]
	bypass_ent["recipe_id"] = "cozy_house_confirm_bypass_attempt"
	bypass_prompt["entity"] = bypass_ent
	var bypass_conf: Dictionary = bypass_prompt["confirmation"]
	bypass_conf["state"] = "confirmed"
	bypass_conf["confirmed_by"] = ACTOR_A
	bypass_prompt["confirmation"] = bypass_conf

	var bypass_sub: Dictionary = client_a.call("submit_and_preview", bypass_prompt)
	if bypass_sub.get("ok", true) != false:
		_fail("confirm_bypass_ok", "expected ok=false got %s" % bypass_sub)
		return
	if str(bypass_sub.get("status", "")) != "rejected":
		_fail("confirm_bypass_status", "expected rejected got %s" % bypass_sub.get("status"))
		return
	if str(bypass_sub.get("code", "")) != "client_forged":
		_fail("confirm_bypass_code", "expected client_forged got %s" % bypass_sub.get("code"))
		return
	if bypass_sub.get("retryable", false) == true:
		_fail("confirm_bypass_retryable", "expected non-retryable reject")
		return
	var bypass_reason := str(bypass_sub.get("reason", ""))
	if bypass_reason.find("not accepted on submit") < 0 and bypass_reason.find("confirm_proposal") < 0:
		_fail("confirm_bypass_reason", "unexpected reason=%s" % bypass_reason)
		return

	# Follow-on commit without registered confirmed proposal → confirmation_missing
	var bypass_commit: Dictionary = _make_commit_request(
		BYPASS_REQUEST_ID, BYPASS_PROMPT_ID, ACTOR_A, "player", pre_bypass_rev
	)
	var bypass_receipt: Dictionary = client_a.call("commit", bypass_commit)
	if str(bypass_receipt.get("status", "")) != "rejected":
		_fail(
			"confirm_bypass_commit_status",
			"expected rejected got %s" % bypass_receipt.get("status")
		)
		return
	var bypass_rej := str(
		(bypass_receipt.get("rejection", {}) as Dictionary).get("code", "")
	)
	if bypass_rej != "confirmation_missing":
		_fail("confirm_bypass_commit_code", "expected confirmation_missing got %s" % bypass_rej)
		return

	if int(server.call("world_revision")) != pre_bypass_rev:
		_fail("confirm_bypass_revision", "revision mutated after bypass attempt")
		return
	if str(server.call("entity_set_hash")) != pre_bypass_hash:
		_fail("confirm_bypass_hash", "entity_set_hash mutated after bypass attempt")
		return
	if int(server.call("entity_count")) != pre_bypass_entities:
		_fail("confirm_bypass_entities", "entity_count mutated after bypass attempt")
		return
	if int(server.call("outbox_len")) != pre_bypass_outbox:
		_fail("confirm_bypass_outbox", "outbox mutated after bypass attempt")
		return
	_ok(
		"AT-G6-CONFIRM-BYPASS-REJECT code=client_forged commit=confirmation_missing rev=%d"
		% pre_bypass_rev
	)

	# ---- TM-RECONNECT-REPLAY ----
	# Disconnect B conceptually: clear session; A already committed once.
	# B reconnects with last_ack and replays.
	# Simulate: B holds last_ack at r1 (already synced). Force disconnect by
	# reconnecting; ensure no double apply and same head.
	var before_reconnect: Dictionary = client_b.call("get_mirror_head")
	var br_rev := int(before_reconnect.get("world_revision", -1))
	var br_hash := str(before_reconnect.get("entity_set_hash", ""))
	var br_entities: Array = (before_reconnect.get("entity_ids", []) as Array).duplicate()

	var recon: Dictionary = client_b.call("reconnect", "replay")
	if not recon.get("ok", false):
		_fail("reconnect", str(recon))
		return
	var after_reconnect: Dictionary = client_b.call("get_mirror_head")
	if int(after_reconnect.get("world_revision", -1)) != br_rev:
		_fail(
			"reconnect_revision",
			"before=%d after=%d" % [br_rev, int(after_reconnect.get("world_revision", -1))]
		)
		return
	if str(after_reconnect.get("entity_set_hash", "")) != br_hash:
		_fail("reconnect_hash", "hash changed on reconnect replay")
		return
	var ar_entities: Array = after_reconnect.get("entity_ids", [])
	if ar_entities.size() != br_entities.size():
		_fail(
			"reconnect_double_apply",
			"entity count before=%d after=%d" % [br_entities.size(), ar_entities.size()]
		)
		return
	_ok(
		"TM-RECONNECT-REPLAY mode=%s rev=%d entities=%d"
		% [recon.get("mode", "replay"), br_rev, ar_entities.size()]
	)

	# Snapshot resync path also converges
	var recon_snap: Dictionary = client_b.call("reconnect", "snapshot")
	if not recon_snap.get("ok", false):
		_fail("reconnect_snapshot", str(recon_snap))
		return
	var after_snap: Dictionary = client_b.call("get_mirror_head")
	if int(after_snap.get("world_revision", -1)) != int(server.call("world_revision")):
		_fail("snapshot_rev", "B not at server head after snapshot")
		return
	if str(after_snap.get("entity_set_hash", "")) != str(server.call("entity_set_hash")):
		_fail("snapshot_hash", "B hash != server after snapshot")
		return
	_ok("TM-RECONNECT-SNAPSHOT-RESYNC rev=%d" % int(after_snap.get("world_revision", -1)))

	# Final both-clients equal
	var final_a: Dictionary = client_a.call("sync", true)
	var final_b: Dictionary = client_b.call("get_mirror_head")
	var final_ah: Dictionary = client_a.call("get_mirror_head")
	if int(final_ah["world_revision"]) != int(final_b["world_revision"]):
		_fail("final_rev", "A/B diverge")
		return
	if str(final_ah["entity_set_hash"]) != str(final_b["entity_set_hash"]):
		_fail("final_hash", "A/B hash diverge")
		return
	_ok(
		"TM-TWO-CLIENT-HEADLESS-SMOKE final rev=%d hash=%s"
		% [int(final_ah["world_revision"]), str(final_ah["entity_set_hash"]).substr(0, 16)]
	)

	print("  SUMMARY clients=%s,%s committed_once=true converge=true forged_rejected=true reconnect_ok=true"
		% [CLIENT_A_ID, CLIENT_B_ID])
	print("  NOTE %s" % str(server.get("POC_NOTE")))


func _make_create_prompt(
	request_id: String,
	prompt_id: String,
	player_id: String,
	expected_rev: int
) -> Dictionary:
	return {
		"schema_version": "1.1.0",
		"prompt_id": prompt_id,
		"request_id": request_id,
		"session_id": "session_g6_poc",
		"actor": {"player_id": player_id, "companion_id": "companion_lumi"},
		"operation": "create",
		"target": {
			"space_type": "private_reality",
			"space_id": SPACE_ID,
			"chunk_id": "0_0",
			"expected_world_revision": expected_rev,
		},
		"style_profile": {
			"profile_id": "cozy_default",
			"profile_version": "1.0.0",
			"base_concept": "cozy_cyber_pixel_2_5d",
			"surrealism_budget": 0.15,
		},
		"entity": {
			"kind": "modular_structure_2_5d",
			"recipe_id": "cozy_house_small",
			"transform": {"x": 8, "y": 6, "elevation": 0, "rotation_deg": 0},
			"bounds": {"width": 8, "depth": 6, "height": 5},
			"interaction_tags": ["enterable", "lightable"],
		},
		"manifestation": {
			"stages": ["wireframe", "hologram", "materializing", "complete"],
			"presentation_duration_seconds": 12,
		},
		"budget": {
			"max_compute_units": 200,
			"max_entities": 32,
			"paid_compute_allowed": false,
		},
		"provenance": {
			"source_type": "player_request",
			"requested_by": player_id,
			"generated_by": "companion_lumi",
			"created_at": "2026-07-21T00:00:00Z",
		},
		"confirmation": {
			"preview_required": true,
			"state": "pending",
			"rollback_window_seconds": 3600,
		},
	}


func _make_commit_request(
	request_id: String,
	prompt_id: String,
	actor_id: String,
	p_actor_type: String,
	expected_rev: int
) -> Dictionary:
	return {
		"schema_version": "1.0.0",
		"request_id": request_id,
		"prompt_id": prompt_id,
		"space_id": SPACE_ID,
		"expected_world_revision": expected_rev,
		"mutation_class": "world_prompt_commit",
		"actor": {"actor_id": actor_id, "actor_type": p_actor_type},
		"authority": {
			"commit_path": "world_commit_service",
			"source": "server_authoritative",
		},
		"confirmation": {
			"state": "confirmed",
			"confirmed_by": actor_id,
		},
		"trace_id": "trace-g6-m2-%s" % request_id.substr(0, mini(8, request_id.length())),
	}


func _ok(label: String) -> void:
	_passed += 1
	print("  OK  %s" % label)


func _fail(label: String, detail: String = "") -> void:
	var msg := label if detail.is_empty() else "%s — %s" % [label, detail]
	_failures.append(msg)
	printerr("  FAIL %s" % msg)


func _finish() -> void:
	if _failures.is_empty() and not _fatal:
		print("G6_TWO_CLIENT_SMOKE=PASS checks=%d" % _passed)
		quit(0)
	else:
		for f in _failures:
			printerr("[FAIL] %s" % f)
		print(
			"G6_TWO_CLIENT_SMOKE=FAIL failed=%d passed=%d fatal=%s"
			% [_failures.size(), _passed, str(_fatal)]
		)
		quit(1)
