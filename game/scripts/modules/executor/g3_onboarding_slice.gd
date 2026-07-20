## G3-001 W2: deterministic AGM onboarding vertical-slice coordinator.
## Owns transaction order only; reuses companion / asset / manifestation / core UI APIs.
## World Commit remains a handoff stub (durable_mutation_applied always false).
## Text-only, 2.5D, no external AI / credentials.
class_name G3OnboardingSlice
extends Node

const SLICE_ID := "g3_onboarding_vertical"
const SCHEMA_VERSION := "g3_slice/1.0.0"
const RECIPE_ID := "cozy_house_small"

const EXPORT_DIR_RES := "res://scripts/modules/executor/exports"
const COMPLETE_EXPORT := "res://scripts/modules/executor/exports/g3_complete_receipt.json"
const CANCEL_EXPORT := "res://scripts/modules/executor/exports/g3_cancel_receipt.json"
const UNDO_EXPORT := "res://scripts/modules/executor/exports/g3_undo_receipt.json"

const SNAPSHOT_FIXTURE_REL := "contracts/fixtures/agm/valid/valid_snapshot_desktop_bridge.json"
const DECISION_ONBOARD_REL := "contracts/fixtures/agm/valid/valid_decision_desktop_bridge.json"
const DECISION_BUILD_REL := "contracts/fixtures/agm/valid/valid_decision_with_build_proposal.json"

## Paths only — load() at bootstrap so class_name deps resolve (avoid preload cycles).
const EXECUTOR_PATH := "res://scripts/modules/executor/executor_module.gd"
const COMPANION_PATH := "res://scripts/modules/companion/companion_module.gd"
const COMPANION_PERSONALITY_PATH := "res://scripts/modules/companion/personality_profile.gd"
const COMPANION_BUILDER_PATH := "res://scripts/modules/companion/world_prompt_builder.gd"
const COMPANION_APPLIER_PATH := "res://scripts/modules/companion/agm_decision_applier.gd"
const COMPANION_PRESENTER_PATH := "res://scripts/modules/companion/g3_onboarding_presenter.gd"
const REALM_PATH := "res://scripts/modules/g3_ui/starter_realm_controller.gd"
const RESOLVER_PATH := "res://scripts/modules/asset/house_recipe_resolver.gd"
const BRIDGE_PATH := "res://scripts/modules/manifestation/g3_preview_bridge.gd"
const SNAPSHOT_BUILDER_PATH := "res://scripts/modules/bridge/snapshot_builder.gd"
const STAGES_PATH := "res://scripts/modules/manifestation/manifestation_stages.gd"
const INSTANCE_PATH := "res://scripts/modules/manifestation/manifestation_instance.gd"
const MANIFEST_MODULE_PATH := "res://scripts/modules/manifestation/manifestation_module.gd"

var _executor: Node = null
var _companion: Node = null
var _realm: Node = null
var _resolver: RefCounted = null
var _preview_bridge: RefCounted = null
## Dedicated parent so G3PreviewBridge does not bind this coordinator
## (we also expose start_house_preview for the transaction API).
var _manifestation_host: Node = null
## Fallback when CompanionModule script fails to compile under -s load order.
var _presenter: RefCounted = null
var _applier: RefCounted = null
var _wp_builder: RefCounted = null
var _use_companion_module: bool = false

var _snapshot: Dictionary = {}
var _onboarding_presentation: Dictionary = {}
var _build_presentation: Dictionary = {}
var _recipe_bundle: Dictionary = {}
var _world_prompt: Dictionary = {}
var _prompt_id: String = ""
var _request_id: String = ""
var _decision_id_onboard: String = ""
var _decision_id_build: String = ""
var _trace_id: String = ""
var _last_preview: Dictionary = {}
var _last_confirm: Dictionary = {}
var _last_cancel: Dictionary = {}
var _last_complete_receipt: Dictionary = {}
var _bootstrapped: bool = false


func is_bootstrapped() -> bool:
	return _bootstrapped


func get_snapshot() -> Dictionary:
	return _snapshot.duplicate(true)


func get_world_prompt() -> Dictionary:
	return _world_prompt.duplicate(true)


func get_prompt_id() -> String:
	return _prompt_id


func get_last_complete_receipt() -> Dictionary:
	return _last_complete_receipt.duplicate(true)


## Mount domain modules under this node (or parent). Headless-safe.
func bootstrap(host: Node = null) -> Dictionary:
	var parent: Node = host if host != null else self
	if parent != self and self.get_parent() == null and host != null:
		host.add_child(self)

	# Warm class_name / dependency scripts before constructing modules.
	_warm_script(COMPANION_PERSONALITY_PATH)
	_warm_script(COMPANION_BUILDER_PATH)
	_warm_script(COMPANION_APPLIER_PATH)
	_warm_script(COMPANION_PRESENTER_PATH)
	_warm_script(STAGES_PATH)
	_warm_script(INSTANCE_PATH)
	_warm_script(MANIFEST_MODULE_PATH)

	var ExecutorScript: GDScript = load(EXECUTOR_PATH) as GDScript
	var RealmScript: GDScript = load(REALM_PATH) as GDScript
	var ResolverScript: GDScript = load(RESOLVER_PATH) as GDScript
	var BridgeScript: GDScript = load(BRIDGE_PATH) as GDScript
	if ExecutorScript == null or RealmScript == null or ResolverScript == null or BridgeScript == null:
		return {
			"ok": false,
			"reason": "failed_to_load_core_scripts",
			"executor_script": ExecutorScript != null,
			"realm_script": RealmScript != null,
			"resolver_script": ResolverScript != null,
			"bridge_script": BridgeScript != null,
		}

	if _executor == null or not is_instance_valid(_executor):
		_executor = ExecutorScript.new() as Node
		_executor.name = "ExecutorModule"
		parent.add_child(_executor)

	# CompanionModule may fail under partial class DB; fall back to presenter/applier.
	_use_companion_module = false
	var CompanionScript: GDScript = load(COMPANION_PATH) as GDScript
	if CompanionScript != null and CompanionScript.can_instantiate():
		var cnode: Variant = CompanionScript.new()
		if cnode is Node:
			_companion = cnode as Node
			_companion.name = "CompanionModule"
			_companion.set("companion_id", "companion_aida")
			_companion.set("player_id", "player_01")
			parent.add_child(_companion)
			_use_companion_module = true
	if not _use_companion_module:
		var ApplierScript: GDScript = load(COMPANION_APPLIER_PATH) as GDScript
		var PresenterScript: GDScript = load(COMPANION_PRESENTER_PATH) as GDScript
		var BuilderScript: GDScript = load(COMPANION_BUILDER_PATH) as GDScript
		if ApplierScript == null or not ApplierScript.can_instantiate():
			return {"ok": false, "reason": "companion_applier_unavailable"}
		if PresenterScript == null or not PresenterScript.can_instantiate():
			return {"ok": false, "reason": "companion_presenter_unavailable"}
		if BuilderScript == null or not BuilderScript.can_instantiate():
			return {"ok": false, "reason": "companion_builder_unavailable"}
		_applier = ApplierScript.new() as RefCounted
		_wp_builder = BuilderScript.new() as RefCounted
		_wp_builder.call("configure_context", {
			"player_id": "player_01",
			"companion_id": "companion_aida",
			"session_id": "session_starter_01",
			"space_type": "private_reality",
			"space_id": "home_01",
			"chunk_id": "0_0",
			"expected_world_revision": 3,
		})
		_presenter = PresenterScript.new() as RefCounted
		if _presenter != null and _presenter.has_method("set_applier"):
			_presenter.call("set_applier", _applier)

	if _realm == null or not is_instance_valid(_realm):
		_realm = RealmScript.new() as Node
		_realm.name = "StarterRealmController"
		parent.add_child(_realm)

	if _resolver == null:
		_resolver = ResolverScript.new() as RefCounted

	if _manifestation_host == null or not is_instance_valid(_manifestation_host):
		_manifestation_host = Node.new()
		_manifestation_host.name = "G3ManifestationHost"
		parent.add_child(_manifestation_host)

	if _preview_bridge == null:
		_preview_bridge = BridgeScript.new() as RefCounted
	# Bind manifestation ONLY under dedicated host (not coordinator — name clash).
	# Prefer explicit ManifestationModule bind over registry walk.
	var ManScript: GDScript = load(MANIFEST_MODULE_PATH) as GDScript
	if ManScript != null and ManScript.can_instantiate():
		var man: Node = ManScript.new() as Node
		man.name = "ManifestationModule"
		_manifestation_host.add_child(man)
		_preview_bridge.call("bind", man)
	else:
		_preview_bridge.call("resolve", _manifestation_host, true)

	_bootstrapped = (
		_executor != null
		and _realm != null
		and _resolver != null
		and bool(_preview_bridge.call("is_bound"))
		and (_use_companion_module or _presenter != null)
	)
	return {
		"ok": _bootstrapped,
		"executor": _executor != null,
		"companion": _use_companion_module,
		"companion_fallback_presenter": (not _use_companion_module) and _presenter != null,
		"realm": _realm != null,
		"resolver": _resolver != null,
		"preview_bridge": bool(_preview_bridge.call("is_bound")),
	}


func _warm_script(path: String) -> void:
	var s: Variant = load(path)
	if s == null:
		push_warning("[G3OnboardingSlice] warm load failed: %s" % path)


func reset_soft_state() -> void:
	_snapshot = {}
	_onboarding_presentation = {}
	_build_presentation = {}
	_recipe_bundle = {}
	_world_prompt = {}
	_prompt_id = ""
	_request_id = ""
	_decision_id_onboard = ""
	_decision_id_build = ""
	_trace_id = ""
	_last_preview = {}
	_last_confirm = {}
	_last_cancel = {}
	# Keep _last_complete_receipt for undo linkage until cleared by caller.
	# Allow replaying fixture decision_ids across complete/cancel smoke paths.
	_clear_companion_replay_history()


func _clear_companion_replay_history() -> void:
	if _use_companion_module and _companion != null and is_instance_valid(_companion):
		if _companion.has_method("get_agm_applier"):
			var applier: Variant = _companion.call("get_agm_applier")
			if applier != null and applier.has_method("clear_applied_history"):
				applier.call("clear_applied_history")
		if _companion.has_method("get_g3_onboarding_presenter"):
			var presenter: Variant = _companion.call("get_g3_onboarding_presenter")
			if presenter != null and presenter.has_method("clear_presentation"):
				presenter.call("clear_presentation")
		return
	if _applier != null and _applier.has_method("clear_applied_history"):
		_applier.call("clear_applied_history")
	if _presenter != null and _presenter.has_method("clear_presentation"):
		_presenter.call("clear_presentation")


func clear_complete_receipt_cache() -> void:
	_last_complete_receipt = {}


# ─── Step 1: World State Snapshot ────────────────────────────────────────────

## Load fixture snapshot, or build via BridgeSnapshotBuilder when fixture missing.
func load_world_state_snapshot(snapshot: Dictionary = {}) -> Dictionary:
	if not _bootstrapped:
		return {"ok": false, "reason": "not_bootstrapped"}

	if not snapshot.is_empty():
		_snapshot = snapshot.duplicate(true)
	else:
		var loaded := _load_json_fixture(SNAPSHOT_FIXTURE_REL)
		if bool(loaded.get("ok", false)):
			_snapshot = loaded.get("data", {}) as Dictionary
		else:
			# Fallback: builder produces schema-shaped Free Desktop Bridge snapshot.
			var BuilderScript: GDScript = load(SNAPSHOT_BUILDER_PATH) as GDScript
			if BuilderScript != null:
				var builder: RefCounted = BuilderScript.new() as RefCounted
				_snapshot = builder.call("build", {
					"snapshot_id": "11111111-1111-4111-8111-111111111111",
					"session_id": "session_starter_01",
					"space_id": "home_01",
					"world_revision": 3,
					"progression_phase": "onboarding",
					"player_id": "player_01",
					"companion_id": "companion_aida",
					"trace_id": "trace_snap_desktop_01",
				}) as Dictionary
			else:
				_snapshot = {
					"schema_version": "1.0.0",
					"snapshot_id": "11111111-1111-4111-8111-111111111111",
					"session_id": "session_starter_01",
					"space_id": "home_01",
					"world_revision": 3,
					"progression_phase": "onboarding",
					"edition": "desktop_bridge_free",
					"player": {"player_id": "player_01", "location": {"chunk_id": "0_0", "x": 8.0, "y": 6.0}},
					"companion": {"companion_id": "companion_aida", "mood": 0.62, "relationship": 0.4},
					"world": {"space_type": "private_reality", "starter_realm": true},
					"trace_id": "trace_snap_desktop_01",
				}

	if _snapshot.is_empty() or str(_snapshot.get("snapshot_id", "")).is_empty():
		return {"ok": false, "reason": "snapshot_missing_id"}

	_trace_id = str(_snapshot.get("trace_id", "trace_g3_slice"))
	_executor.call("set_live_snapshot", _snapshot)
	var snap_id := str(_snapshot.get("snapshot_id", ""))
	if _use_companion_module and _companion != null:
		_companion.call("set_live_snapshot_id", snap_id)
	elif _applier != null:
		_applier.call("set_live_snapshot_id", snap_id)
		if _presenter != null and _presenter.has_method("set_live_snapshot_id"):
			_presenter.call("set_live_snapshot_id", snap_id)
	if _wp_builder != null:
		_wp_builder.call("configure_context", {
			"player_id": str((_snapshot.get("player", {}) as Dictionary).get("player_id", "player_01")),
			"companion_id": str((_snapshot.get("companion", {}) as Dictionary).get("companion_id", "companion_aida")),
			"session_id": str(_snapshot.get("session_id", "session_starter_01")),
			"space_type": str((_snapshot.get("world", {}) as Dictionary).get("space_type", "private_reality")),
			"space_id": str(_snapshot.get("space_id", "home_01")),
			"chunk_id": str(((_snapshot.get("player", {}) as Dictionary).get("location", {}) as Dictionary).get("chunk_id", "0_0")),
			"expected_world_revision": int(_snapshot.get("world_revision", 0)),
		})
	if _realm.has_method("apply_snapshot_context"):
		_realm.call("apply_snapshot_context", _snapshot)
	if _realm.has_method("set_status"):
		_realm.call("set_status", "Snapshot loaded | revision=%s" % str(_snapshot.get("world_revision", 0)))

	return {
		"ok": true,
		"snapshot_id": str(_snapshot.get("snapshot_id", "")),
		"session_id": str(_snapshot.get("session_id", "")),
		"space_id": str(_snapshot.get("space_id", "")),
		"world_revision": int(_snapshot.get("world_revision", 0)),
		"source": "fixture_or_builder",
	}


# ─── Step 2–3: Companion onboarding + quest UI ───────────────────────────────

func present_onboarding_decision(decision: Dictionary = {}) -> Dictionary:
	if not _bootstrapped:
		return {"ok": false, "reason": "not_bootstrapped"}
	var env := decision
	if env.is_empty():
		var loaded := _load_json_fixture(DECISION_ONBOARD_REL)
		if not bool(loaded.get("ok", false)):
			return {"ok": false, "reason": "onboarding_decision_fixture_missing"}
		env = loaded.get("data", {}) as Dictionary

	var presentation := _present_g3_decision(env)
	_onboarding_presentation = presentation.duplicate(true)
	_decision_id_onboard = str(presentation.get("decision_id", env.get("decision_id", "")))

	_drive_realm_from_presentation(presentation, "Onboarding quest presented (soft UI only)")
	return presentation


func present_build_proposal_decision(decision: Dictionary = {}) -> Dictionary:
	if not _bootstrapped:
		return {"ok": false, "reason": "not_bootstrapped"}
	var env := decision
	if env.is_empty():
		var loaded := _load_json_fixture(DECISION_BUILD_REL)
		if not bool(loaded.get("ok", false)):
			return {"ok": false, "reason": "build_decision_fixture_missing"}
		env = loaded.get("data", {}) as Dictionary

	var presentation := _present_g3_decision(env)
	_build_presentation = presentation.duplicate(true)
	_decision_id_build = str(presentation.get("decision_id", env.get("decision_id", "")))

	# Extract pending world prompt (companion elevates build proposals).
	var agm: Dictionary = presentation.get("agm_result", {}) as Dictionary
	var prompts: Array = agm.get("world_prompts", []) as Array
	if prompts.is_empty() and presentation.has("world_prompts"):
		prompts = presentation.get("world_prompts", []) as Array
	if not prompts.is_empty() and typeof(prompts[0]) == TYPE_DICTIONARY:
		_world_prompt = (prompts[0] as Dictionary).duplicate(true)
		_prompt_id = str(_world_prompt.get("prompt_id", ""))
		_request_id = str(_world_prompt.get("request_id", ""))

	_drive_realm_from_presentation(presentation, "Build proposal pending preview (no durable mutation)")
	return presentation


## Preferred: CompanionModule.present_g3_onboarding_decision.
## Fallback: AGM applier.project + presenter.format_from_projected (same soft effects).
func _present_g3_decision(envelope: Dictionary) -> Dictionary:
	if _use_companion_module and _companion != null and _companion.has_method("present_g3_onboarding_decision"):
		return _companion.call("present_g3_onboarding_decision", envelope) as Dictionary

	if _applier == null or _presenter == null or _wp_builder == null:
		return {"ok": false, "reason": "companion_path_unavailable", "dialogue_lines": [], "quest_summaries": [], "mood_delta": 0.0}

	var projected: Dictionary = _applier.call("project", envelope, _wp_builder) as Dictionary
	if not bool(projected.get("ok", false)):
		return {
			"ok": false,
			"errors": projected.get("errors", PackedStringArray()),
			"dialogue_lines": [],
			"quest_summaries": [],
			"mood_delta": 0.0,
			"text_only": true,
			"committed": false,
			"durable_mutation": false,
			"decision_id": str(projected.get("decision_id", envelope.get("decision_id", ""))),
			"agm_result": projected,
		}
	var presentation: Dictionary = _presenter.call("format_from_projected", projected) as Dictionary
	if presentation.is_empty():
		presentation = _presenter.call("apply_decision", envelope) as Dictionary
	presentation = presentation.duplicate(true)
	presentation["agm_result"] = projected
	presentation["world_prompt_count"] = (projected.get("world_prompts", []) as Array).size()
	if not presentation.has("ok"):
		presentation["ok"] = true
	return presentation


# ─── Step 4: House recipe resolution ─────────────────────────────────────────

func resolve_house_recipe(recipe_id: String = RECIPE_ID) -> Dictionary:
	if not _bootstrapped or _resolver == null:
		return {"ok": false, "reason": "not_bootstrapped"}
	var bundle: Dictionary = _resolver.call("resolve_cozy_house_for_starter", {}) as Dictionary
	if recipe_id != RECIPE_ID and recipe_id != "":
		# Primary path is cozy_house_small; still allow resolve_recipe for other ids.
		var resolved: Dictionary = _resolver.call("resolve_recipe", recipe_id) as Dictionary
		if not bool(resolved.get("ok", false)):
			return resolved
		var prov: Dictionary = _resolver.call("validate_provenance", "recipe:%s" % recipe_id) as Dictionary
		var geo: Dictionary = _resolver.call("export_geometry_dict", recipe_id, {}) as Dictionary
		bundle = {
			"ok": bool(resolved.get("ok", false)) and bool(prov.get("ok", false)) and bool(geo.get("ok", false)),
			"recipe_id": recipe_id,
			"resolved": resolved,
			"provenance": prov,
			"geometry": geo,
		}
	_recipe_bundle = bundle.duplicate(true)
	if _realm != null and _realm.has_method("set_status"):
		_realm.call(
			"set_status",
			"Recipe resolved: %s parts=%s" % [
				str(bundle.get("recipe_id", recipe_id)),
				str(((bundle.get("resolved", {}) as Dictionary).get("part_count", "?"))),
			]
		)
	return bundle


# ─── Step 5: Preview via G3PreviewBridge ─────────────────────────────────────

## Ensure world_prompt is in executor pipeline (preview stage), then run stages.
## options: stop_at_stage, skip_animation, auto_advance (forwarded to bridge).
func start_house_preview(options: Dictionary = {}) -> Dictionary:
	if not _bootstrapped:
		return {"ok": false, "reason": "not_bootstrapped"}
	if _world_prompt.is_empty():
		return {"ok": false, "reason": "no_world_prompt"}
	if _prompt_id.is_empty():
		_prompt_id = str(_world_prompt.get("prompt_id", ""))
	if _request_id.is_empty():
		_request_id = str(_world_prompt.get("request_id", ""))

	# Submit into executor pipeline if not already present (companion may have handed off).
	var status: Dictionary = _executor.call("get_prompt_status", _prompt_id) as Dictionary
	if not bool(status.get("found", false)):
		var submitted := str(_executor.call("submit_prompt", _world_prompt))
		if submitted.is_empty():
			return {"ok": false, "reason": "submit_prompt_failed", "prompt_id": _prompt_id}
		_prompt_id = submitted

	# Cancel any auto-started wireframe so start_house_preview can own lifecycle.
	if bool(_preview_bridge.call("is_bound")):
		var stage_now := str(_preview_bridge.call("get_stage", _prompt_id))
		if not stage_now.is_empty():
			_preview_bridge.call("cancel_preview", _prompt_id, "restart_for_g3_stages")

	var preview_opts := options.duplicate(true)
	if not preview_opts.has("auto_advance"):
		preview_opts["auto_advance"] = true

	var preview: Dictionary = _preview_bridge.call("start_house_preview", _world_prompt, preview_opts) as Dictionary
	_last_preview = preview.duplicate(true)

	var stages: Array = preview.get("stages_observed", []) as Array
	if _realm != null and _realm.has_method("show_preview_banner"):
		var banner_stage := str(preview.get("stage", ""))
		if not stages.is_empty():
			# For complete path show final; for stop_at show last observed.
			banner_stage = str(stages[stages.size() - 1])
		_realm.call("show_preview_banner", banner_stage)
	if _realm != null and _realm.has_method("set_status"):
		_realm.call(
			"set_status",
			"Preview %s | durable_collision=%s" % [
				str(preview.get("stage", "")),
				str(preview.get("has_durable_collision", false)),
			]
		)
	return preview


# ─── Step 6: Explicit confirm → World Commit handoff stub ────────────────────

## Requires explicit player confirm. Never auto-confirms. No live World Commit.
func confirm_after_preview(confirmed_by: String = "player_01") -> Dictionary:
	if not _bootstrapped:
		return {"ok": false, "reason": "not_bootstrapped"}
	if _prompt_id.is_empty():
		return {"ok": false, "reason": "no_prompt_id"}
	var who := confirmed_by.strip_edges()
	if who.is_empty():
		return {"ok": false, "reason": "confirmed_by required"}

	# Guard: must not confirm without preview having run (defense in depth).
	if _last_preview.is_empty() or not bool(_last_preview.get("ok", false)):
		return {"ok": false, "reason": "preview_required_before_confirm", "prompt_id": _prompt_id}

	var result: Dictionary = _executor.call("confirm_prompt", _prompt_id, who) as Dictionary
	_last_confirm = result.duplicate(true)
	if _realm != null and _realm.has_method("set_status"):
		if bool(result.get("ok", false)):
			_realm.call("set_status", "Confirmed → commit handoff stub (world_commit not invoked)")
		else:
			_realm.call("set_status", "Confirm rejected: %s" % str(result.get("reason", "")))
	return result


func cancel_transaction(reason: String = "player_cancel") -> Dictionary:
	if not _bootstrapped:
		return {"ok": false, "reason": "not_bootstrapped"}
	if _prompt_id.is_empty():
		return {"ok": false, "reason": "no_prompt_id"}

	var man_cancel: Dictionary = {}
	if _preview_bridge != null and bool(_preview_bridge.call("is_bound")):
		man_cancel = _preview_bridge.call("cancel_preview", _prompt_id, reason) as Dictionary
	_executor.call("cancel_prompt", _prompt_id, reason)
	var pipe_status: Dictionary = _executor.call("get_prompt_status", _prompt_id) as Dictionary
	_last_cancel = {
		"ok": true,
		"prompt_id": _prompt_id,
		"manifestation": man_cancel,
		"pipeline": pipe_status,
		"cancel_reason": reason,
		"durable_mutation_applied": false,
		"world_commit_invoked": false,
	}
	if _realm != null:
		if _realm.has_method("show_preview_banner"):
			_realm.call("show_preview_banner", "none")
		if _realm.has_method("set_status"):
			_realm.call("set_status", "Cancelled | no durable mutation")
	return _last_cancel.duplicate(true)


# ─── Full transactions + receipt exports ─────────────────────────────────────

## Full happy path: snapshot → onboard → build → recipe → preview complete → confirm → export.
func run_complete_path(write_export: bool = true) -> Dictionary:
	reset_soft_state()
	var snap_res := load_world_state_snapshot()
	if not bool(snap_res.get("ok", false)):
		return {"ok": false, "step": "snapshot", "detail": snap_res}

	var onboard := present_onboarding_decision()
	if not bool(onboard.get("ok", false)):
		return {"ok": false, "step": "onboarding", "detail": onboard}

	var build := present_build_proposal_decision()
	if not bool(build.get("ok", false)):
		return {"ok": false, "step": "build_decision", "detail": build}
	if _world_prompt.is_empty():
		return {"ok": false, "step": "world_prompt", "reason": "no pending SWP from build decision"}

	var recipe := resolve_house_recipe(RECIPE_ID)
	if not bool(recipe.get("ok", false)):
		return {"ok": false, "step": "recipe", "detail": recipe}

	# Enrich geometry from recipe into prompt for manifestation bounds consistency.
	_merge_recipe_geometry_into_prompt()

	var preview := start_house_preview({"auto_advance": true})
	if not bool(preview.get("ok", false)):
		return {"ok": false, "step": "preview", "detail": preview}
	if str(preview.get("stage", "")) != "complete":
		return {"ok": false, "step": "preview_stage", "detail": preview}

	var conf := confirm_after_preview("player_01")
	if not bool(conf.get("ok", false)):
		return {"ok": false, "step": "confirm", "detail": conf}
	if bool(conf.get("durable_mutation_applied", true)):
		return {"ok": false, "step": "confirm_durable", "detail": conf}

	var receipt := build_complete_receipt(preview, conf)
	_last_complete_receipt = receipt.duplicate(true)
	var written := {"ok": true, "path": COMPLETE_EXPORT, "skipped": not write_export}
	if write_export:
		written = write_receipt_json(receipt, COMPLETE_EXPORT)
	return {
		"ok": true,
		"receipt_kind": "complete",
		"receipt": receipt,
		"export": written,
		"prompt_id": _prompt_id,
		"durable_mutation_applied": false,
		"world_commit_invoked": false,
	}


## Cancel mid-preview (hologram): no durable mutation, no compensating class.
func run_cancel_path(write_export: bool = true) -> Dictionary:
	reset_soft_state()
	var snap_res := load_world_state_snapshot()
	if not bool(snap_res.get("ok", false)):
		return {"ok": false, "step": "snapshot", "detail": snap_res}

	var onboard := present_onboarding_decision()
	if not bool(onboard.get("ok", false)):
		return {"ok": false, "step": "onboarding", "detail": onboard}

	var build := present_build_proposal_decision()
	if not bool(build.get("ok", false)):
		return {"ok": false, "step": "build_decision", "detail": build}
	if _world_prompt.is_empty():
		return {"ok": false, "step": "world_prompt", "reason": "no pending SWP"}

	var recipe := resolve_house_recipe(RECIPE_ID)
	if not bool(recipe.get("ok", false)):
		return {"ok": false, "step": "recipe", "detail": recipe}
	_merge_recipe_geometry_into_prompt()

	var preview := start_house_preview({"auto_advance": true, "stop_at_stage": "hologram"})
	if not bool(preview.get("ok", false)):
		return {"ok": false, "step": "preview", "detail": preview}

	var cancelled := cancel_transaction("player_cancel")
	if not bool(cancelled.get("ok", false)):
		return {"ok": false, "step": "cancel", "detail": cancelled}

	# Confirm after cancel must fail.
	var conf_after: Dictionary = _executor.call("confirm_prompt", _prompt_id, "player_01") as Dictionary
	if bool(conf_after.get("ok", false)):
		return {"ok": false, "step": "confirm_after_cancel_should_fail", "detail": conf_after}

	# Idempotent re-cancel.
	var recancel := cancel_transaction("player_cancel")
	if not bool(recancel.get("ok", false)):
		return {"ok": false, "step": "recancel", "detail": recancel}

	var receipt := build_cancel_receipt(preview, cancelled)
	var written := {"ok": true, "path": CANCEL_EXPORT, "skipped": not write_export}
	if write_export:
		written = write_receipt_json(receipt, CANCEL_EXPORT)
	return {
		"ok": true,
		"receipt_kind": "cancel",
		"receipt": receipt,
		"export": written,
		"prompt_id": _prompt_id,
		"confirm_after_cancel_ok": bool(conf_after.get("ok", false)),
		"durable_mutation_applied": false,
		"world_commit_invoked": false,
	}


## Compensating undo stub after a complete-path receipt. Never erases history.
func run_undo_path(prior_complete: Dictionary = {}, write_export: bool = true) -> Dictionary:
	var prior := prior_complete if not prior_complete.is_empty() else _last_complete_receipt
	if prior.is_empty():
		# Try load from disk.
		var loaded := _load_json_res(COMPLETE_EXPORT)
		if bool(loaded.get("ok", false)):
			prior = loaded.get("data", {}) as Dictionary
	if prior.is_empty() or str(prior.get("receipt_kind", "")) != "complete":
		return {"ok": false, "reason": "prior_complete_receipt_required"}

	var receipt := build_undo_receipt(prior)
	var written := {"ok": true, "path": UNDO_EXPORT, "skipped": not write_export}
	if write_export:
		written = write_receipt_json(receipt, UNDO_EXPORT)

	# History preserved: complete export must still exist.
	var still_exists := FileAccess.file_exists(COMPLETE_EXPORT) or FileAccess.file_exists(
		ProjectSettings.globalize_path(COMPLETE_EXPORT)
	)
	receipt["prior_complete_receipt_still_exists"] = still_exists
	if write_export:
		# Re-write with existence flag.
		written = write_receipt_json(receipt, UNDO_EXPORT)

	if _realm != null and _realm.has_method("set_status"):
		_realm.call("set_status", "Undo compensating stub written (history preserved)")

	return {
		"ok": true,
		"receipt_kind": "undo",
		"receipt": receipt,
		"export": written,
		"history_preserved": true,
		"history_erased": false,
		"prior_complete_receipt_still_exists": still_exists,
		"durable_mutation_applied": false,
		"world_commit_invoked": false,
	}


# ─── Receipt builders (W0_persist field contract) ────────────────────────────

func build_complete_receipt(preview: Dictionary, confirm: Dictionary) -> Dictionary:
	var now := _now_iso()
	var commit_request: Dictionary = confirm.get("commit_request", {}) as Dictionary
	if commit_request.is_empty():
		var rec: Dictionary = confirm.get("record", {}) as Dictionary
		commit_request = rec.get("commit_request", {}) as Dictionary
	var commit_stub: Dictionary = confirm.get("commit_receipt_stub", {}) as Dictionary
	if commit_stub.is_empty():
		var rec2: Dictionary = confirm.get("record", {}) as Dictionary
		commit_stub = rec2.get("commit_receipt_stub", {}) as Dictionary

	var stages: Array = preview.get("stages_observed", []) as Array
	if stages.is_empty():
		stages = ["wireframe", "hologram", "materializing", "complete"]

	var conf_block := {
		"preview_required": true,
		"state": "confirmed",
		"confirmed_by": "player_01",
	}
	if commit_request.has("confirmation") and commit_request["confirmation"] is Dictionary:
		var from_cr: Dictionary = (commit_request["confirmation"] as Dictionary).duplicate(true)
		for k in from_cr.keys():
			conf_block[k] = from_cr[k]
		# W0_persist complete smoke requires preview_required true after confirm.
		conf_block["preview_required"] = true
		if str(conf_block.get("state", "")) != "confirmed":
			conf_block["state"] = "confirmed"
		if str(conf_block.get("confirmed_by", "")).is_empty():
			conf_block["confirmed_by"] = "player_01"

	var receipt_id := _new_uuid()
	var request_id := str(commit_request.get("request_id", _request_id if not _request_id.is_empty() else _new_uuid()))
	var expected_rev := int(_snapshot.get("world_revision", 0))
	if commit_request.has("expected_world_revision"):
		expected_rev = int(commit_request.get("expected_world_revision", expected_rev))
	elif _world_prompt.has("target"):
		expected_rev = int((_world_prompt.get("target", {}) as Dictionary).get("expected_world_revision", expected_rev))

	return {
		"schema_version": SCHEMA_VERSION,
		"receipt_kind": "complete",
		"receipt_id": receipt_id,
		"request_id": request_id,
		"prompt_id": _prompt_id,
		"space_id": str(_snapshot.get("space_id", "home_01")),
		"occurred_at": now,
		"trace_id": _trace_id if not _trace_id.is_empty() else "trace_g3_complete",
		"durable_mutation_applied": false,
		"world_commit_invoked": false,
		"slice": SLICE_ID,
		"pipeline_stage": "commit_handoff_stubbed",
		"confirmation": conf_block,
		"manifestation": {
			"final_stage": "complete",
			"stages_observed": stages,
			"has_durable_collision": bool(preview.get("has_durable_collision", true)),
		},
		"commit_request": commit_request.duplicate(true) if not commit_request.is_empty() else {
			"schema_version": "1.0.0",
			"request_id": request_id,
			"prompt_id": _prompt_id,
			"authority": {
				"commit_path": "world_commit_service",
				"source": "server_authoritative",
			},
			"mutation_class": "durable_world",
		},
		"commit_receipt_stub": commit_stub.duplicate(true) if not commit_stub.is_empty() else {
			"status": "rejected",
			"authority": {"commit_path": "world_commit_service"},
			"rejection": {
				"code": "policy",
				"reason": "World Commit not invoked / policy handoff (G3 stub)",
			},
			"durable_mutation_applied": false,
			"stub": true,
		},
		"expected_world_revision": expected_rev,
		"entity_recipe_id": RECIPE_ID,
		"source_snapshot_id": str(_snapshot.get("snapshot_id", "")),
		"decision_id": _decision_id_build if not _decision_id_build.is_empty() else _decision_id_onboard,
		"onboarding_decision_id": _decision_id_onboard,
		"build_decision_id": _decision_id_build,
		"recipe_part_count": int(((_recipe_bundle.get("resolved", {}) as Dictionary).get("part_count", 0))),
		"text_only": true,
		"mvp_lock": "2.5D",
	}


func build_cancel_receipt(preview: Dictionary, cancelled: Dictionary) -> Dictionary:
	var now := _now_iso()
	var man: Dictionary = cancelled.get("manifestation", {}) as Dictionary
	var stages: Array = man.get("stages_observed", []) as Array
	if stages.is_empty():
		stages = preview.get("stages_observed", []) as Array
	var during := str(man.get("cancelled_during_stage", preview.get("stage", "hologram")))
	if during.is_empty():
		during = "hologram"

	return {
		"schema_version": SCHEMA_VERSION,
		"receipt_kind": "cancel",
		"receipt_id": _new_uuid(),
		"request_id": _request_id if not _request_id.is_empty() else _new_uuid(),
		"prompt_id": _prompt_id,
		"space_id": str(_snapshot.get("space_id", "home_01")),
		"occurred_at": now,
		"cancelled_at": now,
		"trace_id": _trace_id if not _trace_id.is_empty() else "trace_g3_cancel",
		"durable_mutation_applied": false,
		"world_commit_invoked": false,
		"slice": SLICE_ID,
		"pipeline_stage": "cancelled",
		"status": "cancelled",
		"cancel_reason": str(cancelled.get("cancel_reason", "player_cancel")),
		"cancelled_during_stage": during,
		"manifestation": {
			"final_stage": "cancelled",
			"has_durable_collision": false,
			"orphan_collision_count": 0,
			"stages_observed": stages,
		},
		"entity_ids_durable": [],
		"world_revision_advanced": false,
		"commit_receipt_status_if_any": "none",
		"source_snapshot_id": str(_snapshot.get("snapshot_id", "")),
		"decision_id": _decision_id_build if not _decision_id_build.is_empty() else _decision_id_onboard,
		"entity_recipe_id": RECIPE_ID,
		"note": "Cancel removes preview only; not a compensating mutation",
	}


func build_undo_receipt(prior_complete: Dictionary) -> Dictionary:
	var now := _now_iso()
	var prior_receipt_id := str(prior_complete.get("receipt_id", ""))
	var prior_request_id := str(prior_complete.get("request_id", ""))
	var prompt_id := str(prior_complete.get("prompt_id", _prompt_id))
	var new_request_id := _new_uuid()
	var new_receipt_id := _new_uuid()
	# Guaranteed distinct from prior ids.
	if new_request_id == prior_request_id:
		new_request_id = _new_uuid()
	if new_receipt_id == prior_receipt_id:
		new_receipt_id = _new_uuid()

	return {
		"schema_version": SCHEMA_VERSION,
		"receipt_kind": "undo",
		"receipt_id": new_receipt_id,
		"request_id": new_request_id,
		"prompt_id": prompt_id,
		"space_id": str(prior_complete.get("space_id", _snapshot.get("space_id", "home_01"))),
		"occurred_at": now,
		"trace_id": str(prior_complete.get("trace_id", _trace_id if not _trace_id.is_empty() else "trace_g3_undo")),
		"durable_mutation_applied": false,
		"world_commit_invoked": false,
		"slice": SLICE_ID,
		"mutation_class": "compensating",
		"status": "compensating_stub",
		"prior_receipt_id": prior_receipt_id,
		"prior_request_id": prior_request_id,
		"compensated_prompt_id": prompt_id,
		"compensated_entity_ids": [],
		"history_erased": false,
		"history_preserved": true,
		"prior_complete_receipt_still_exists": true,
		"world_revision_advanced": false,
		"entity_recipe_id": str(prior_complete.get("entity_recipe_id", RECIPE_ID)),
		"source_snapshot_id": str(prior_complete.get("source_snapshot_id", "")),
		"decision_id": str(prior_complete.get("decision_id", "")),
		"note": "G3 stub only — real compensation commit + revision bump is G4 / live World Commit",
		"compensating_commit_request_stub": {
			"schema_version": "1.0.0",
			"request_id": new_request_id,
			"prompt_id": prompt_id,
			"mutation_class": "compensating",
			"prior_receipt_id": prior_receipt_id,
			"prior_request_id": prior_request_id,
			"authority": {
				"commit_path": "world_commit_service",
				"source": "server_authoritative",
			},
			"stub": true,
			"durable_mutation_applied": false,
		},
	}


func write_receipt_json(receipt: Dictionary, path: String) -> Dictionary:
	if path.is_empty():
		return {"ok": false, "reason": "empty path"}
	var text := JSON.stringify(receipt, "\t")
	var abs_path := path
	if path.begins_with("res://"):
		abs_path = ProjectSettings.globalize_path(path)
	var dir_path := abs_path.get_base_dir()
	DirAccess.make_dir_recursive_absolute(dir_path)
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		f = FileAccess.open(abs_path, FileAccess.WRITE)
	if f == null:
		return {"ok": false, "reason": "FileAccess.open failed for %s" % path, "abs_path": abs_path}
	f.store_string(text)
	f.close()
	return {"ok": true, "path": path, "abs_path": abs_path}


# ─── Internals ───────────────────────────────────────────────────────────────

func _drive_realm_from_presentation(presentation: Dictionary, status: String) -> void:
	if _realm == null:
		return
	var quest_summaries: Array = presentation.get("quest_summaries", []) as Array
	if not quest_summaries.is_empty() and typeof(quest_summaries[0]) == TYPE_DICTIONARY:
		var q0: Dictionary = quest_summaries[0]
		var summary := str(q0.get("status_text", ""))
		if summary.is_empty():
			summary = "%s: %s" % [str(q0.get("title", q0.get("quest_id", "quest"))), str(q0.get("objective_summary", ""))]
		if _realm.has_method("set_quest_summary"):
			_realm.call("set_quest_summary", summary)
	var lines: Array = presentation.get("dialogue_lines", []) as Array
	if not lines.is_empty() and typeof(lines[0]) == TYPE_DICTIONARY:
		var text := str((lines[0] as Dictionary).get("text", ""))
		if not text.is_empty() and _realm.has_method("set_companion_text_placeholder"):
			_realm.call("set_companion_text_placeholder", text)
	if _realm.has_method("set_status"):
		_realm.call("set_status", status)


func _merge_recipe_geometry_into_prompt() -> void:
	if _world_prompt.is_empty() or _recipe_bundle.is_empty():
		return
	var geo: Dictionary = _recipe_bundle.get("geometry", {}) as Dictionary
	if geo.is_empty():
		return
	var entity: Dictionary = (_world_prompt.get("entity", {}) as Dictionary).duplicate(true)
	if geo.has("bounds") and geo["bounds"] is Dictionary:
		entity["bounds"] = (geo["bounds"] as Dictionary).duplicate(true)
	if geo.has("transform") and geo["transform"] is Dictionary:
		entity["transform"] = (geo["transform"] as Dictionary).duplicate(true)
	entity["recipe_id"] = str(geo.get("recipe_id", RECIPE_ID))
	_world_prompt["entity"] = entity
	# Attach preview geometry hints used by manifestation normalize path.
	_world_prompt["geometry_preview"] = {
		"size": geo.get("size", {}),
		"position": geo.get("position", {}),
		"parts": geo.get("parts", []),
		"build_order": geo.get("build_order", []),
		"collision_policy": geo.get("collision_policy", {}),
		"preview_only": true,
	}


func _load_json_fixture(rel_from_repo: String) -> Dictionary:
	var candidates: PackedStringArray = PackedStringArray()
	var game_root := ProjectSettings.globalize_path("res://")
	candidates.append(game_root.path_join("..").path_join(rel_from_repo).simplify_path())
	candidates.append(game_root.path_join(rel_from_repo).simplify_path())
	# user-info workspace relative guesses
	candidates.append("E:/AIdle_openworld".path_join(rel_from_repo))
	for p in candidates:
		if p.is_empty():
			continue
		if not FileAccess.file_exists(p):
			continue
		var f := FileAccess.open(p, FileAccess.READ)
		if f == null:
			continue
		var text := f.get_as_text()
		f.close()
		var json := JSON.new()
		if json.parse(text) != OK:
			continue
		if typeof(json.data) != TYPE_DICTIONARY:
			continue
		return {"ok": true, "data": json.data, "path": p}
	return {"ok": false, "reason": "fixture not found: %s" % rel_from_repo}


func _load_json_res(path: String) -> Dictionary:
	var open_path := path
	if not FileAccess.file_exists(open_path):
		open_path = ProjectSettings.globalize_path(path)
	if not FileAccess.file_exists(open_path) and not FileAccess.file_exists(path):
		return {"ok": false, "reason": "missing %s" % path}
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		f = FileAccess.open(open_path, FileAccess.READ)
	if f == null:
		return {"ok": false, "reason": "open failed %s" % path}
	var text := f.get_as_text()
	f.close()
	var json := JSON.new()
	if json.parse(text) != OK:
		return {"ok": false, "reason": "parse failed"}
	if typeof(json.data) != TYPE_DICTIONARY:
		return {"ok": false, "reason": "not object"}
	return {"ok": true, "data": json.data}


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
