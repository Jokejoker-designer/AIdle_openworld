## World Prompt pipeline: preview → confirm → commit handoff stub (G2-006).
## Never mutates durable world revision itself. Commit is prepared as a
## schema-shaped request for the World Commit service (sole mutator).
## Preview may start manifestation wireframe (non-durable collision).
class_name ExecutorPromptPipeline
extends RefCounted

const PIPELINE_PREVIEW := "preview"
const PIPELINE_CONFIRMED := "confirmed"
const PIPELINE_COMMIT_STUBBED := "commit_handoff_stubbed"
const PIPELINE_CANCELLED := "cancelled"

## prompt_id -> pipeline record
var _prompts: Dictionary = {}


func has_prompt(prompt_id: String) -> bool:
	return _prompts.has(prompt_id)


func get_record(prompt_id: String) -> Dictionary:
	if not _prompts.has(prompt_id):
		return {}
	return (_prompts[prompt_id] as Dictionary).duplicate(true)


func list_prompt_ids() -> PackedStringArray:
	return PackedStringArray(_prompts.keys())


func get_status(prompt_id: String) -> Dictionary:
	var rec := get_record(prompt_id)
	if rec.is_empty():
		return {"prompt_id": prompt_id, "found": false, "stage": "", "status": "unknown"}
	return {
		"prompt_id": prompt_id,
		"found": true,
		"stage": str(rec.get("pipeline_stage", "")),
		"status": str(rec.get("status", "")),
		"confirmation_state": str(
			((rec.get("world_prompt", {}) as Dictionary).get("confirmation", {}) as Dictionary).get("state", "")
		),
		"preview_required": (
			((rec.get("world_prompt", {}) as Dictionary).get("confirmation", {}) as Dictionary).get("preview_required", true)
		),
		"durable_mutation_applied": bool(rec.get("durable_mutation_applied", false)),
		"commit_handoff_ready": rec.get("commit_request") != null,
	}


## Accept a Structured World Prompt into the pipeline at preview stage.
## Forces preview_required=true and confirmation pending unless already confirmed
## by a later confirm_prompt call (never auto-confirms on submit).
func submit(world_prompt: Dictionary, source: String = "companion") -> Dictionary:
	if world_prompt.is_empty():
		return {"ok": false, "reason": "empty world_prompt", "prompt_id": ""}

	var prompt_id := str(world_prompt.get("prompt_id", "")).strip_edges()
	if prompt_id.is_empty():
		return {"ok": false, "reason": "missing prompt_id", "prompt_id": ""}

	if _prompts.has(prompt_id):
		var existing: Dictionary = _prompts[prompt_id]
		return {
			"ok": true,
			"prompt_id": prompt_id,
			"idempotent": true,
			"pipeline_stage": str(existing.get("pipeline_stage", PIPELINE_PREVIEW)),
			"record": existing.duplicate(true),
		}

	var wp := world_prompt.duplicate(true)
	# Defense in depth: AGM/companion submits always enter as pending preview.
	if not wp.has("confirmation") or typeof(wp["confirmation"]) != TYPE_DICTIONARY:
		wp["confirmation"] = {
			"preview_required": true,
			"state": "pending",
			"rollback_window_seconds": 3600,
		}
	var conf: Dictionary = (wp["confirmation"] as Dictionary).duplicate(true)
	# Never accept client pre-confirmed durable path on submit.
	if conf.get("preview_required") != true:
		return {
			"ok": false,
			"reason": "preview_required must be true (build cannot skip preview)",
			"prompt_id": prompt_id,
		}
	if str(conf.get("state", "")) == "confirmed":
		return {
			"ok": false,
			"reason": "cannot submit pre-confirmed prompt; use confirm_prompt after preview",
			"prompt_id": prompt_id,
		}
	conf["preview_required"] = true
	conf["state"] = "pending"
	conf.erase("confirmed_by")
	wp["confirmation"] = conf

	var record := {
		"prompt_id": prompt_id,
		"request_id": str(wp.get("request_id", "")),
		"source": source,
		"pipeline_stage": PIPELINE_PREVIEW,
		"status": "preview_pending",
		"world_prompt": wp,
		"commit_request": null,
		"commit_receipt_stub": null,
		"durable_mutation_applied": false,
		"submitted_at": _now_iso(),
		"confirmed_at": null,
		"cancelled_at": null,
	}
	_prompts[prompt_id] = record
	return {
		"ok": true,
		"prompt_id": prompt_id,
		"idempotent": false,
		"pipeline_stage": PIPELINE_PREVIEW,
		"record": record.duplicate(true),
	}


## Player confirmation after preview. Builds a commit_request handoff stub.
## Does NOT apply durable world mutation (World Commit service is sole mutator).
func confirm(prompt_id: String, confirmed_by: String, world_revision: int = 0) -> Dictionary:
	if prompt_id.is_empty() or not _prompts.has(prompt_id):
		return {"ok": false, "reason": "unknown prompt_id", "prompt_id": prompt_id}
	var rec: Dictionary = (_prompts[prompt_id] as Dictionary).duplicate(true)
	var stage := str(rec.get("pipeline_stage", ""))
	if stage == PIPELINE_CANCELLED:
		return {"ok": false, "reason": "prompt cancelled", "prompt_id": prompt_id}
	if stage == PIPELINE_COMMIT_STUBBED or stage == PIPELINE_CONFIRMED:
		# Idempotent confirm: return existing handoff.
		return {
			"ok": true,
			"prompt_id": prompt_id,
			"idempotent": true,
			"pipeline_stage": stage,
			"record": rec,
			"commit_request": rec.get("commit_request"),
		}

	if stage != PIPELINE_PREVIEW:
		return {"ok": false, "reason": "prompt not in preview stage: %s" % stage, "prompt_id": prompt_id}

	var who := confirmed_by.strip_edges()
	if who.is_empty():
		return {"ok": false, "reason": "confirmed_by required", "prompt_id": prompt_id}

	var wp: Dictionary = (rec.get("world_prompt", {}) as Dictionary).duplicate(true)
	var conf: Dictionary = (wp.get("confirmation", {}) as Dictionary).duplicate(true)
	if conf.get("preview_required") != true:
		return {"ok": false, "reason": "preview_required invariant broken", "prompt_id": prompt_id}
	conf["state"] = "confirmed"
	conf["confirmed_by"] = who
	wp["confirmation"] = conf

	var target: Dictionary = wp.get("target", {}) as Dictionary
	var expected_rev := world_revision
	if target.has("expected_world_revision"):
		expected_rev = int(target.get("expected_world_revision", world_revision))

	var commit_request := {
		"schema_version": "1.0.0",
		"request_id": str(wp.get("request_id", _new_uuid())),
		"prompt_id": prompt_id,
		"session_id": str(wp.get("session_id", "session_executor_01")),
		"space_id": str(target.get("space_id", "home_01")),
		"expected_world_revision": expected_rev,
		"actor": {
			"actor_id": who,
			"actor_type": "player",
		},
		"authority": {
			"commit_path": "world_commit_service",
			"source": "server_authoritative",
			"durable_mutation": true,
		},
		"confirmation": {
			"state": "confirmed",
			"confirmed_by": who,
		},
		"mutation_class": "durable_world",
		"trace_id": "executor_commit_handoff_%s" % prompt_id.substr(0, 8),
	}

	# Synthetic non-authoritative stub receipt: not a real commit.
	var commit_receipt_stub := {
		"schema_version": "1.0.0",
		"receipt_id": _new_uuid(),
		"request_id": str(commit_request["request_id"]),
		"status": "rejected",
		"occurred_at": _now_iso(),
		"space_id": str(commit_request["space_id"]),
		"authority": {
			"commit_path": "world_commit_service",
			"issuer": "world_commit_service",
		},
		"rejection": {
			"code": "policy",
			"reason": "G2-006 stub: commit handoff prepared; World Commit service not invoked (no durable mutation)",
		},
		"trace_id": str(commit_request["trace_id"]),
		"stub": true,
		"durable_mutation_applied": false,
	}

	rec["world_prompt"] = wp
	rec["pipeline_stage"] = PIPELINE_COMMIT_STUBBED
	rec["status"] = "commit_handoff_stubbed"
	rec["confirmed_at"] = _now_iso()
	rec["commit_request"] = commit_request
	rec["commit_receipt_stub"] = commit_receipt_stub
	rec["durable_mutation_applied"] = false
	_prompts[prompt_id] = rec

	return {
		"ok": true,
		"prompt_id": prompt_id,
		"idempotent": false,
		"pipeline_stage": PIPELINE_COMMIT_STUBBED,
		"record": rec.duplicate(true),
		"commit_request": commit_request.duplicate(true),
		"commit_receipt_stub": commit_receipt_stub.duplicate(true),
		"durable_mutation_applied": false,
	}


func cancel(prompt_id: String, reason: String = "player_cancel") -> Dictionary:
	if prompt_id.is_empty() or not _prompts.has(prompt_id):
		return {"ok": false, "reason": "unknown prompt_id", "prompt_id": prompt_id}
	var rec: Dictionary = (_prompts[prompt_id] as Dictionary).duplicate(true)
	if str(rec.get("pipeline_stage", "")) == PIPELINE_CANCELLED:
		return {"ok": true, "prompt_id": prompt_id, "idempotent": true, "pipeline_stage": PIPELINE_CANCELLED}
	# Cannot cancel after a real durable commit — we never apply durable mutation here.
	rec["pipeline_stage"] = PIPELINE_CANCELLED
	rec["status"] = "cancelled"
	rec["cancelled_at"] = _now_iso()
	rec["cancel_reason"] = reason
	rec["durable_mutation_applied"] = false
	_prompts[prompt_id] = rec
	return {
		"ok": true,
		"prompt_id": prompt_id,
		"idempotent": false,
		"pipeline_stage": PIPELINE_CANCELLED,
		"record": rec.duplicate(true),
	}


func list_pending_preview() -> Array:
	var out: Array = []
	for pid in _prompts.keys():
		var rec: Dictionary = _prompts[pid]
		if str(rec.get("pipeline_stage", "")) == PIPELINE_PREVIEW:
			out.append(rec.duplicate(true))
	return out


func list_commit_handoffs() -> Array:
	var out: Array = []
	for pid in _prompts.keys():
		var rec: Dictionary = _prompts[pid]
		if str(rec.get("pipeline_stage", "")) == PIPELINE_COMMIT_STUBBED and rec.get("commit_request") != null:
			out.append({
				"prompt_id": pid,
				"commit_request": (rec.get("commit_request") as Dictionary).duplicate(true),
				"durable_mutation_applied": false,
			})
	return out


func _now_iso() -> String:
	var created_at := Time.get_datetime_string_from_system(true, true)
	if not created_at.ends_with("Z") and "+" not in created_at:
		created_at = created_at.replace(" ", "T")
		if not created_at.ends_with("Z"):
			created_at += "Z"
	return created_at


func _new_uuid() -> String:
	var b := PackedByteArray()
	b.resize(16)
	for i in 16:
		b[i] = randi() % 256
	b[6] = (b[6] & 0x0f) | 0x40
	b[8] = (b[8] & 0x3f) | 0x80
	var hex := b.hex_encode()
	return "%s-%s-%s-%s-%s" % [
		hex.substr(0, 8),
		hex.substr(8, 4),
		hex.substr(12, 4),
		hex.substr(16, 4),
		hex.substr(20, 12),
	]
