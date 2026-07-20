## Headless smoke for G2-003 AGM rework (Godot -s).
## Tests WorldPromptBuilder + PersonalityProfile + AGM Decision Applier (no commit).
extends SceneTree


func _initialize() -> void:
	var failures: PackedStringArray = []

	# ── NL builder still works ───────────────────────────────────────────────
	var builder := CompanionWorldPromptBuilder.new()
	builder.configure_context({
		"player_id": "player_01",
		"companion_id": "companion_lumi",
		"session_id": "session_companion_smoke",
	})
	var proposal := builder.build_from_natural_language("xây nhà cozy house")
	if proposal.is_empty():
		failures.append("proposal empty for house intent")
	else:
		if str(proposal.get("schema_version", "")) != "1.1.0":
			failures.append("schema_version")
		var conf: Dictionary = proposal.get("confirmation", {}) as Dictionary
		if str(conf.get("state", "")) != "pending":
			failures.append("confirmation not pending")
		if conf.get("preview_required") != true:
			failures.append("preview_required not true")
		var entity: Dictionary = proposal.get("entity", {}) as Dictionary
		if str(entity.get("recipe_id", "")) != "cozy_house_small":
			failures.append("recipe_id mismatch")
		if str(proposal.get("operation", "")) != "create":
			failures.append("operation not create")

	if CompanionWorldPromptBuilder.has_commit_tool():
		failures.append("has_commit_tool true")
	var saw_agm_tool := false
	for t in CompanionWorldPromptBuilder.list_tools():
		if typeof(t) != TYPE_DICTIONARY:
			continue
		var tool: Dictionary = t
		if bool(tool.get("commits", false)) or bool(tool.get("mutates_world", false)):
			failures.append("tool mutates: %s" % str(tool.get("name", "")))
		if str(tool.get("name", "")) == "apply_agm_decision":
			saw_agm_tool = true
	if not saw_agm_tool:
		failures.append("list_tools missing apply_agm_decision")

	# ── Personality caps / controls ──────────────────────────────────────────
	var personality := CompanionPersonalityProfile.new("companion_lumi")
	var d0 := personality.apply_observation("warmth", 1.0, 0.99, "too few obs", 1, 1)
	if not is_zero_approx(d0):
		failures.append("applied delta without min observations")
	var d1 := personality.apply_observation("warmth", 1.0, 0.99, "ok", 3, 3)
	if absf(d1) > CompanionPersonalityProfile.CAP_MAX_DELTA_PER_TURN + 0.000001:
		failures.append("turn cap exceeded: %s" % d1)
	personality.lock_trait("warmth")
	personality.begin_turn()
	var d2 := personality.apply_observation("warmth", 1.0, 0.99, "locked", 3, 3)
	if not is_zero_approx(d2):
		failures.append("locked trait still drifted")
	personality.reset_adaptive_to_base()
	personality.delete_adaptation_history()
	var report := personality.inspect_plain_language()
	if report.is_empty():
		failures.append("inspect empty")
	if "Caps:" not in report:
		failures.append("inspect missing caps section")

	# ── AGM Decision Envelope: dialogue + build proposal ─────────────────────
	var applier := CompanionAgmDecisionApplier.new()
	applier.set_live_snapshot_id("11111111-1111-4111-8111-111111111111")
	var envelope := _fixture_build_proposal_decision()
	var projected := applier.project(envelope, builder)
	if not bool(projected.get("ok", false)):
		var errs: PackedStringArray = projected.get("errors", PackedStringArray()) as PackedStringArray
		failures.append("AGM project failed: %s" % (str(errs[0]) if errs.size() > 0 else "unknown"))
	else:
		var lines: Array = projected.get("dialogue_lines", []) as Array
		if lines.is_empty():
			failures.append("AGM dialogue_lines empty")
		else:
			var line0: Dictionary = lines[0]
			if str(line0.get("speaker", "")) != "companion":
				failures.append("AGM dialogue speaker not companion")
			if str(line0.get("text", "")).is_empty():
				failures.append("AGM dialogue text empty")
		if str(projected.get("expression", "")) != "curious":
			failures.append("AGM expression expected curious")
		var prompts: Array = projected.get("world_prompts", []) as Array
		if prompts.is_empty():
			failures.append("AGM world_prompts empty")
		else:
			var wp: Dictionary = prompts[0]
			var wp_conf: Dictionary = wp.get("confirmation", {}) as Dictionary
			if str(wp_conf.get("state", "")) != "pending":
				failures.append("AGM SWP confirmation not pending")
			if wp_conf.get("preview_required") != true:
				failures.append("AGM SWP preview_required not true")
			var wp_ent: Dictionary = wp.get("entity", {}) as Dictionary
			if str(wp_ent.get("recipe_id", "")) != "cozy_house_small":
				failures.append("AGM SWP recipe mismatch")
			var prov: Dictionary = wp.get("provenance", {}) as Dictionary
			if str(prov.get("source_type", "")) != "companion_enrichment":
				failures.append("AGM SWP source_type not companion_enrichment")
			if str(prov.get("generated_by", "")) != "companion_lumi":
				failures.append("AGM SWP generated_by mismatch")

	# Replay rejection
	var replay := applier.project(envelope, builder)
	if bool(replay.get("ok", false)):
		failures.append("AGM replay should be rejected")
	else:
		var r_errs: PackedStringArray = replay.get("errors", PackedStringArray()) as PackedStringArray
		var joined := " ".join(r_errs)
		if "replay" not in joined.to_lower():
			failures.append("replay error missing replay keyword")

	# Forbidden TTS / durable fields rejected
	var bad_tts := _fixture_build_proposal_decision()
	bad_tts["decision_id"] = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
	bad_tts["tts_audio"] = "base64-not-allowed"
	var tts_check := applier.validate(bad_tts)
	if bool(tts_check.get("ok", false)):
		failures.append("tts_audio should fail validation")

	var bad_durable := _fixture_build_proposal_decision()
	bad_durable["decision_id"] = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
	bad_durable["durable_mutation"] = true
	var dur_check := applier.validate(bad_durable)
	if bool(dur_check.get("ok", false)):
		failures.append("durable_mutation should fail validation")

	# Stale snapshot rejection
	var stale := _fixture_build_proposal_decision()
	stale["decision_id"] = "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
	stale["source_snapshot_id"] = "99999999-9999-4999-8999-999999999999"
	var stale_check := applier.validate(stale)
	if bool(stale_check.get("ok", false)):
		failures.append("stale snapshot should fail validation")

	# Bypass preview rejected
	var bypass := _fixture_build_proposal_decision()
	bypass["decision_id"] = "dddddddd-dddd-4ddd-8ddd-dddddddddddd"
	var bp0: Dictionary = (bypass["build_proposals"] as Array)[0]
	bp0["preview_required"] = false
	bp0["confirmation_state"] = "confirmed"
	(bypass["build_proposals"] as Array)[0] = bp0
	var bypass_check := applier.validate(bypass)
	if bool(bypass_check.get("ok", false)):
		failures.append("preview bypass should fail validation")

	# Dialogue-only decision still ok
	applier.clear_applied_history()
	applier.set_live_snapshot_id("11111111-1111-4111-8111-111111111111")
	var dialogue_only := _fixture_dialogue_only_decision()
	var d_proj := applier.project(dialogue_only, builder)
	if not bool(d_proj.get("ok", false)):
		failures.append("dialogue-only AGM should apply")
	elif (d_proj.get("world_prompts", []) as Array).size() != 0:
		failures.append("dialogue-only should have zero world_prompts")
	elif (d_proj.get("dialogue_lines", []) as Array).is_empty():
		failures.append("dialogue-only lines empty")

	# Expression → mood map is text-only, no voice
	if CompanionAgmDecisionApplier.expression_to_mood("curious") != "focused":
		failures.append("expression_to_mood curious→focused")
	if CompanionAgmDecisionApplier.expression_to_mood("proud") != "happy":
		failures.append("expression_to_mood proud→happy")

	# ── CompanionModule end-to-end apply (optional Node path) ────────────────
	var mod := CompanionModule.new()
	mod.name = "CompanionSmoke"
	get_root().add_child(mod)
	# _ready runs; re-bind snapshot after ready
	mod.set_live_snapshot_id("11111111-1111-4111-8111-111111111111")
	var mod_env := _fixture_build_proposal_decision()
	mod_env["decision_id"] = "eeeeeeee-eeee-4eee-8eee-eeeeeeeeeeee"
	var mod_result := mod.apply_agm_decision(mod_env)
	if not bool(mod_result.get("ok", false)):
		var m_errs: PackedStringArray = mod_result.get("errors", PackedStringArray()) as PackedStringArray
		failures.append(
			"module apply_agm_decision failed: %s"
			% (str(m_errs[0]) if m_errs.size() > 0 else "unknown")
		)
	else:
		if mod.get_last_proposal().is_empty():
			failures.append("module last proposal empty after AGM")
		var chat := mod.get_chat_log()
		var has_companion_line := false
		for entry in chat:
			if typeof(entry) != TYPE_DICTIONARY:
				continue
			if str((entry as Dictionary).get("role", "")) == "companion":
				has_companion_line = true
				break
		if not has_companion_line:
			failures.append("module chat missing companion dialogue from AGM")
		if mod.has_commit_tool():
			failures.append("module has_commit_tool true")
		var missing := ICompanionModule.validate(mod)
		if not missing.is_empty():
			failures.append("interface missing: %s" % str(missing[0]))
		var commit_issues := ICompanionModule.audit_no_commit_tools(mod)
		if not commit_issues.is_empty():
			failures.append("commit audit: %s" % str(commit_issues[0]))
		# inspect/lock/reset/delete still work after AGM apply
		if mod.inspect_personality_text().is_empty():
			failures.append("inspect empty after AGM")
		if not mod.lock_trait("humor"):
			failures.append("lock_trait failed")
		mod.reset_personality()
		mod.delete_adaptation_history()

	if failures.is_empty():
		print("G2-003_GODOT_SMOKE=PASS")
		quit(0)
	else:
		print("G2-003_GODOT_SMOKE=FAIL")
		for f in failures:
			print(" - ", f)
		quit(1)


func _fixture_build_proposal_decision() -> Dictionary:
	## Mirrors contracts/fixtures/agm/valid/valid_decision_with_build_proposal.json
	return {
		"schema_version": "1.0.0",
		"decision_id": "33333333-3333-4333-8333-333333333333",
		"source_snapshot_id": "11111111-1111-4111-8111-111111111111",
		"created_at": "2026-07-20T16:05:00Z",
		"edition": "desktop_bridge_free",
		"session_id": "session_starter_01",
		"dialogue": {
			"lines": [
				{
					"speaker": "companion",
					"text": "I can sketch a small cozy house here. You'll preview it before anything solid appears.",
				}
			],
			"companion_expression": "curious",
		},
		"quest_operations": [
			{
				"op": "update_objective",
				"quest_id": "onboarding_first_home",
				"objective_summary": "Preview and confirm the cozy house proposal.",
			}
		],
		"build_proposals": [
			{
				"proposal_id": "44444444-4444-4444-8444-444444444444",
				"operation": "create",
				"recipe_id": "cozy_house_small",
				"entity_kind": "modular_structure_2_5d",
				"routes_through": "preview_confirm_commit",
				"preview_required": true,
				"confirmation_state": "pending",
				"space_id": "home_01",
				"chunk_id": "0_0",
				"transform": {"x": 8.0, "y": 6.0, "elevation": 0.0, "rotation_deg": 0.0},
				"rationale": "Starter house for onboarding vertical slice.",
			}
		],
		"event_proposals": [
			{
				"event_type": "narrative.beat",
				"summary": "House sketch offered; wait for player confirm.",
				"intensity": 0.5,
			}
		],
		"mood_delta": {"delta": 0.03, "reason": "shared build excitement"},
		"relationship_delta": {"delta": 0.02, "reason": "collaborative proposal"},
		"next_trigger": {"kind": "player_action", "hint": "await preview confirm or cancel"},
		"trace": {
			"trace_id": "trace_build_proposal_01",
			"model_receipt_ref": "bridge:manual:decision:002",
			"provider_label": "desktop_bridge",
		},
	}


func _fixture_dialogue_only_decision() -> Dictionary:
	## Mirrors contracts/fixtures/agm/valid/valid_decision_desktop_bridge.json shape
	return {
		"schema_version": "1.0.0",
		"decision_id": "22222222-2222-4222-8222-222222222222",
		"source_snapshot_id": "11111111-1111-4111-8111-111111111111",
		"created_at": "2026-07-20T16:00:05Z",
		"edition": "desktop_bridge_free",
		"session_id": "session_starter_01",
		"dialogue": {
			"lines": [
				{
					"speaker": "companion",
					"text": "Let's start small — plant a seed on the farm plot and claim your first home light.",
				}
			],
			"companion_expression": "warm",
		},
		"quest_operations": [
			{
				"op": "offer",
				"quest_id": "onboarding_first_home",
				"title": "First Light at Home",
				"objective_summary": "Visit the farm plot and acknowledge the house placeholder.",
			}
		],
		"build_proposals": [],
		"event_proposals": [
			{
				"event_type": "onboarding.nudge",
				"summary": "Highlight farm plot and house silhouette.",
				"intensity": 0.4,
			}
		],
		"mood_delta": {"delta": 0.02, "reason": "friendly onboarding"},
		"relationship_delta": {"delta": 0.01, "reason": "first shared plan"},
		"next_trigger": {"kind": "player_action", "hint": "await interact on farm_plot_01"},
		"pacing_hint": {"tempo": "slow", "note": "gentle first minutes"},
		"trace": {
			"trace_id": "trace_snap_desktop_01",
			"model_receipt_ref": "bridge:manual:decision:001",
			"provider_label": "desktop_bridge",
		},
	}
