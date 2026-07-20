## AIdle Openworld – global constants (Master Blueprint v1.0).
## Registered as Autoload `AIdleConstants` so all scripts (including other autoloads) can reference it.
extends Node

const SCHEMA_VERSION := "1.0"
const PROJECT_CODE_NAME := "AIdle Openworld"
const CORE_VERSION := "0.1.0-core"
## Client runtime pin (must match project.godot config/features + tools binary).
const GODOT_PIN := "4.3"
const PRESENTATION_MODE := "2.5D_fixed_angle"

## True when Godot runs headless / dummy renderer (no real GPU presentation).
## Callers must skip Mesh/Material construction only — never swallow real errors.
func is_headless_or_dummy_presentation() -> bool:
	if OS.has_feature("headless"):
		return true
	# --headless sets DisplayServer name to "headless" (Godot 4.x).
	if DisplayServer.get_name() == "headless":
		return true
	return false

## Reality Hierarchy – locked names (scene nodes + target_space enum mapping).
const SPACE_PRIVATE_REALITY := "private_reality"
const SPACE_SHARED_DISTRICT := "shared_district"
const SPACE_DOPPELGANGER_CITY := "doppelganger_city"
const SPACE_SPACECRAFT := "spacecraft"
const SPACE_EXOPLANET := "exoplanet"
const SPACE_OPEN_CONTINUUM := "open_continuum"

## Scene node names under WorldRoot (must match Master Blueprint hierarchy).
const NODE_PRIVATE_REALITY := "PrivateReality"
const NODE_SHARED_DISTRICTS := "SharedDistricts"
const NODE_DOPPELGANGER_CITIES := "DoppelgangerCities"
const NODE_ORBITAL := "Orbital"
const NODE_EXOPLANETS := "Exoplanets"

## Art styles (Visual Concept Pillars).
const ART_COZY_CYBER_PIXEL := "cozy_cyber_pixel"
const ART_SURREALISM_CANVAS := "surrealism_canvas"
const ART_CYBERPUNK_DENSE := "cyberpunk_dense"
const ART_PASTORAL_FANTASY := "pastoral_fantasy"
const ART_CUSTOM := "custom"

const DEFAULT_ART_STYLE := ART_COZY_CYBER_PIXEL

## AGM edition modes (transport only — identical snapshot/decision schemas).
## Blueprint: 08_AI_Game_Master_and_Edition_Modes.md + contracts/agm/*.schema.json
const EDITION_DESKTOP_BRIDGE_FREE := "desktop_bridge_free"
const EDITION_API_PAID := "api_paid"
## Free Desktop Bridge is the safe first-run default (no gateway, no secrets).
const DEFAULT_EDITION := EDITION_DESKTOP_BRIDGE_FREE
const AGM_EDITIONS: PackedStringArray = [
	EDITION_DESKTOP_BRIDGE_FREE,
	EDITION_API_PAID,
]

## Manifestation stages (Progressive Construction).
const STAGE_WIREFRAME := "wireframe"
const STAGE_HOLOGRAM := "hologram"
const STAGE_MATERIALIZING := "materializing"
const STAGE_COMPLETE := "complete"

## Settings / user data paths (user://).
const SETTINGS_PATH := "user://settings.cfg"
const WORLD_META_PATH := "user://world_meta.cfg"
const PROVENANCE_LOG_PATH := "user://logs/provenance.log"

## Physics layers (must match project.godot layer_names).
const LAYER_WORLD := 1
const LAYER_PLAYER := 2
const LAYER_MANIFESTATION := 3
const LAYER_COMPANION := 4
const LAYER_INTERACTABLE := 5

## Module slot ids used by ModuleRegistry.
const MODULE_VOXEL := "voxel"
const MODULE_COMPANION := "companion"
const MODULE_EXECUTOR := "executor"
const MODULE_NETWORK := "network"
const MODULE_SCHEMA := "schema"
const MODULE_ASSET := "asset"
const MODULE_PERSIST := "persist"
