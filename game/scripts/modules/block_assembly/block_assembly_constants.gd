## P2E-001 Block Assembly — contract-aligned placement constants.
## Values mirror accepted BLOCK-DNA-ADAPT-001 catalog_allowlists.grid (read-only consume).
## No parallel grammar; no DNA package code import.
class_name BlockAssemblyConstants
extends RefCounted

const CONTRACT_ID := "block_dna_adapt_001"
const CONTRACT_VERSION := "1.0"
const SPACE_ID_DEFAULT := "home_01"

## Grid snap from catalog_allowlists.grid
const GRID_SNAP_M := 0.5
const ELEVATION_SNAP_M := 0.25
const ROTATION_SNAP_DEG := 15.0
const SCALE_DELTA_MAX := 0.25

const BOUNDS_MAX_WIDTH_M := 128.0
const BOUNDS_MAX_DEPTH_M := 128.0
const BOUNDS_MAX_HEIGHT_M := 64.0

const MANIFESTATION_STAGES: PackedStringArray = [
	"wireframe",
	"hologram",
	"materializing",
	"complete",
]

const RUNTIME_CATALOG_PATH := "res://resources/block_assembly/runtime_catalog.json"
const SOCKET_RULES_PATH := "res://resources/block_assembly/socket_rules.json"

const PREVIEW_GROUP := "block_assembly_previews"
const COMMITTED_GROUP := "block_assembly_committed"
