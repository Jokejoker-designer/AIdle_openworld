## Global EventBus – Common Contracts §2.
## All world-related events should carry prompt_id + provenance when available.
## Agents MUST use this bus instead of ad-hoc signal spaghetti across modules.
extends Node

# ─── Progressive Manifestation ───────────────────────────────────────────────
signal manifestation_started(prompt_id: String, target_space: String, provenance: Dictionary)
signal manifestation_progress_updated(prompt_id: String, progress: float, stage: String)
signal manifestation_completed(prompt_id: String, provenance: Dictionary)
signal manifestation_cancelled(prompt_id: String, reason: String)

# ─── Companion / emotion ─────────────────────────────────────────────────────
signal random_alchemist_gift(prompt_id: String, companion_id: String, provenance: Dictionary)
signal emotional_state_changed(companion_id: String, mood: String, aura_color: Color)

# ─── Spaces / social ─────────────────────────────────────────────────────────
signal player_entered_space(space_id: String, instance_key: String, player: Node)
signal visit_requested(from_player_id: String, to_space_id: String)
signal visit_accepted(from_player_id: String, to_space_id: String)

# ─── Art style ───────────────────────────────────────────────────────────────
signal art_style_changed(style_id: String)

# ─── Game lifecycle ──────────────────────────────────────────────────────────
signal game_booted()
signal world_ready(world_root: Node)
signal game_paused(is_paused: bool)
signal debug_toggled(visible: bool)

# ─── Module hot-plug ─────────────────────────────────────────────────────────
## Fired when an Agent module registers/unregisters via ModuleRegistry.
signal module_registered(module_id: String, module: Node)
signal module_unregistered(module_id: String)

# ─── Settings ────────────────────────────────────────────────────────────────
signal settings_changed(section: String, key: String, value: Variant)


func _ready() -> void:
	print("[EventBus] Ready – Common Contracts event hub online.")
