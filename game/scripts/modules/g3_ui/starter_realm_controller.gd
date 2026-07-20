## G3-001 Starter Realm UI controller (W1 core).
## Holds live snapshot / session context for the vertical slice surface.
## Does NOT own Desktop Bridge, AGM network, or executor transaction logic.
## Executor (W2) drives: get_session_context / set_quest_summary / set_status / show_preview_banner.
## Snapshot context is applied only at call sites (fixture load or BridgeSnapshotBuilder output).
extends Node

const GROUP_NAME := "g3_starter_realm"
const PANEL_SCENE_PATH := "res://scenes/ui/starter_realm_panel.tscn"
const PANEL_SCRIPT_PATH := "res://scripts/modules/g3_ui/starter_realm_panel.gd"

## Ordered preview stages (aligned with manifestation / world_prompt schema).
const PREVIEW_STAGES: PackedStringArray = [
	"wireframe",
	"hologram",
	"materializing",
	"complete",
]

## Emitted when quest title/summary text changes (Companion text placeholder hook).
signal quest_summary_changed(text: String)
## Emitted for companion dialogue placeholder surface (text-only; no TTS).
signal companion_text_placeholder(text: String)
signal status_changed(text: String)
signal preview_banner_changed(stage: String)
signal session_context_changed(context: Dictionary)

## Live session keys used by executor / AGM slice (subset of World State Snapshot).
var _session_context: Dictionary = {}
var _quest_summary: String = ""
var _status_text: String = ""
var _preview_stage: String = ""
var _companion_placeholder: String = ""
var _panel: Node = null


func _ready() -> void:
	add_to_group(GROUP_NAME)
	_session_context = _default_session_context()
	_mount_panel()
	_push_all_to_panel()
	set_status("Starter Realm ready (awaiting AGM onboarding slice)")
	print(
		"[StarterRealmController] Mounted | snapshot_id=%s session_id=%s space=%s"
		% [
			str(_session_context.get("snapshot_id", "")),
			str(_session_context.get("session_id", "")),
			str(_session_context.get("space_id", "")),
		]
	)


# ─── Executor-facing API (W2 contract) ───────────────────────────────────────

## Full session context for snapshot/decision correlation (duplicate; safe to mutate).
func get_session_context() -> Dictionary:
	return _session_context.duplicate(true)


## Quest title / summary line for HUD + companion placeholder signal.
func set_quest_summary(text: String) -> void:
	_quest_summary = str(text)
	if _panel != null and _panel.has_method("set_quest_summary"):
		_panel.call("set_quest_summary", _quest_summary)
	quest_summary_changed.emit(_quest_summary)
	# Quest title doubles as the default companion text placeholder signal.
	companion_text_placeholder.emit(_quest_summary)


## Free-form status line (pipeline stage hints, errors, waiting messages).
func set_status(text: String) -> void:
	_status_text = str(text)
	if _panel != null and _panel.has_method("set_status"):
		_panel.call("set_status", _status_text)
	status_changed.emit(_status_text)


## Show manifestation preview stage banner (wireframe → hologram → materializing → complete).
## Empty / "none" / "idle" hides the banner. Unknown stages are still displayed as text.
func show_preview_banner(stage: String) -> void:
	var s := str(stage).strip_edges().to_lower()
	if s.is_empty() or s == "none" or s == "idle" or s == "hidden":
		_preview_stage = ""
	else:
		_preview_stage = s
	if _panel != null and _panel.has_method("set_preview_banner"):
		_panel.call("set_preview_banner", _preview_stage)
	preview_banner_changed.emit(_preview_stage)


# ─── Call-site helpers (fixture / builder output — not bridge ownership) ─────

## Merge a full or partial World State Snapshot into live session context.
## Call from executor smoke or any site that already holds fixture/builder output.
func apply_snapshot_context(snapshot: Dictionary) -> void:
	if snapshot.is_empty():
		return
	var next := _session_context.duplicate(true)
	if snapshot.has("snapshot_id"):
		next["snapshot_id"] = str(snapshot.get("snapshot_id"))
		next["live_snapshot_id"] = str(snapshot.get("snapshot_id"))
	if snapshot.has("session_id"):
		next["session_id"] = str(snapshot.get("session_id"))
	if snapshot.has("space_id"):
		next["space_id"] = str(snapshot.get("space_id"))
	if snapshot.has("world_revision"):
		next["world_revision"] = int(snapshot.get("world_revision"))
	if snapshot.has("progression_phase"):
		next["progression_phase"] = str(snapshot.get("progression_phase"))
	if snapshot.has("edition"):
		next["edition"] = str(snapshot.get("edition"))
	if snapshot.has("trace_id"):
		next["trace_id"] = str(snapshot.get("trace_id"))
	if snapshot.has("created_at"):
		next["created_at"] = str(snapshot.get("created_at"))
	var player: Variant = snapshot.get("player", null)
	if player is Dictionary:
		var pd: Dictionary = player
		if pd.has("player_id"):
			next["player_id"] = str(pd.get("player_id"))
		if pd.has("display_name"):
			next["display_name"] = str(pd.get("display_name"))
	var companion: Variant = snapshot.get("companion", null)
	if companion is Dictionary:
		var cd: Dictionary = companion
		if cd.has("companion_id"):
			next["companion_id"] = str(cd.get("companion_id"))
	var world: Variant = snapshot.get("world", null)
	if world is Dictionary:
		var wd: Dictionary = world
		if wd.has("starter_realm"):
			next["starter_realm"] = bool(wd.get("starter_realm"))
		if wd.has("space_type"):
			next["space_type"] = str(wd.get("space_type"))
	var quests: Variant = snapshot.get("quests", null)
	if quests is Dictionary:
		next["quests"] = (quests as Dictionary).duplicate(true)
	_session_context = next
	_push_session_to_panel()
	session_context_changed.emit(get_session_context())


## Replace or shallow-merge session keys from a partial context dictionary.
func set_session_context(context: Dictionary, replace: bool = false) -> void:
	if replace:
		_session_context = context.duplicate(true)
	else:
		for k in context.keys():
			_session_context[k] = context[k]
	if _session_context.has("snapshot_id"):
		_session_context["live_snapshot_id"] = str(_session_context.get("snapshot_id"))
	_push_session_to_panel()
	session_context_changed.emit(get_session_context())


func get_live_snapshot_id() -> String:
	return str(_session_context.get("live_snapshot_id", _session_context.get("snapshot_id", "")))


func get_quest_summary() -> String:
	return _quest_summary


func get_status() -> String:
	return _status_text


func get_preview_stage() -> String:
	return _preview_stage


## Explicit companion dialogue placeholder (text-only surface; no STT/TTS).
func set_companion_text_placeholder(text: String) -> void:
	_companion_placeholder = str(text)
	if _panel != null and _panel.has_method("set_companion_placeholder"):
		_panel.call("set_companion_placeholder", _companion_placeholder)
	companion_text_placeholder.emit(_companion_placeholder)


func get_companion_text_placeholder() -> String:
	return _companion_placeholder


## Static lookup for executor / smoke without hard scene paths.
static func find_in_tree(tree: SceneTree) -> Node:
	if tree == null:
		return null
	var nodes := tree.get_nodes_in_group(GROUP_NAME)
	if nodes.is_empty():
		return null
	return nodes[0]


# ─── Internal ────────────────────────────────────────────────────────────────

func _default_session_context() -> Dictionary:
	## Defaults mirror contracts/fixtures/agm/valid/valid_snapshot_desktop_bridge.json
	## (identity only — controller does not load bridge or fixtures itself).
	return {
		"snapshot_id": "",
		"live_snapshot_id": "",
		"session_id": "session_starter_01",
		"space_id": "home_01",
		"world_revision": 0,
		"progression_phase": "onboarding",
		"edition": "desktop_bridge_free",
		"player_id": "player_01",
		"display_name": "Ava",
		"companion_id": "companion_aida",
		"starter_realm": true,
		"space_type": "private_reality",
		"trace_id": "",
		"slice": "g3_onboarding_vertical",
	}


func _mount_panel() -> void:
	if _panel != null and is_instance_valid(_panel):
		return
	var scene: PackedScene = load(PANEL_SCENE_PATH) as PackedScene
	if scene != null:
		_panel = scene.instantiate()
	else:
		# Fallback: pure script panel if scene missing under headless pack quirks.
		var script: Script = load(PANEL_SCRIPT_PATH) as Script
		if script != null:
			_panel = CanvasLayer.new()
			_panel.set_script(script)
	if _panel == null:
		push_warning("[StarterRealmController] Panel scene/script unavailable; API-only mode.")
		return
	_panel.name = "StarterRealmPanel"
	add_child(_panel)


func _push_all_to_panel() -> void:
	_push_session_to_panel()
	if _panel == null:
		return
	if _panel.has_method("set_quest_summary"):
		_panel.call("set_quest_summary", _quest_summary)
	if _panel.has_method("set_status"):
		_panel.call("set_status", _status_text)
	if _panel.has_method("set_preview_banner"):
		_panel.call("set_preview_banner", _preview_stage)
	if _panel.has_method("set_companion_placeholder"):
		_panel.call("set_companion_placeholder", _companion_placeholder)


func _push_session_to_panel() -> void:
	if _panel == null:
		return
	if _panel.has_method("set_session_display"):
		_panel.call(
			"set_session_display",
			get_live_snapshot_id(),
			str(_session_context.get("session_id", "")),
			str(_session_context.get("space_id", "")),
			int(_session_context.get("world_revision", 0)),
			str(_session_context.get("progression_phase", "")),
			str(_session_context.get("edition", ""))
		)
