## UCBV-001 path constants (C2 runtime). Relative res:// only — never absolute /root.
## Note: no class_name so headless -s always resolves via preload path.
extends RefCounted

const BLOCKS_ROOT := "res://assets/ucbv_001/blocks"
const FAMILY_MANIFEST := "res://assets/ucbv_001/blocks/family_manifest.json"
const MATERIAL_BINDINGS := "res://assets/ucbv_001/blocks/material_bindings.json"
const VISUAL_STATES := "res://assets/ucbv_001/blocks/visual_states.json"

const NORI_ROOT := "res://assets/ucbv_001/character/nori7"
const NORI_PACKAGE := "res://assets/ucbv_001/character/nori7/package_manifest.json"
const NORI_SLICE := "res://assets/ucbv_001/character/nori7/godot/nori7_procedural_slice_spec.json"
const NORI_HIERARCHY := "res://assets/ucbv_001/character/nori7/skeleton/skel_small_biped_robot_v1.hierarchy.json"
const NORI_MESH := "res://assets/ucbv_001/character/nori7/mesh/nori7_mesh_descriptor.json"
const NORI_TIMING := "res://assets/ucbv_001/character/nori7/animations/anim_robot_gardener_v1.timing_table.json"
const NORI_STATE_MACHINE := "res://assets/ucbv_001/character/nori7/animations/animation_state_machine.json"
const NORI_SOCKETS := "res://assets/ucbv_001/character/nori7/sockets/attachment_sockets.json"

## C2 production GLB + animation adapter (C1R input).
const NORI_GLB := "res://assets/ucbv_001/character/nori7/export/nori7_rigged.glb"
const NORI_ANIM_ADAPTER := "res://resources/ucbv_001/character/nori7_animation_adapter.json"
const NORI_GLB_SHA256_EXPECTED := "8af77c042f336b1377aaacfb746c7c0198fdbec022f808baed15dea309d65f2b"

const KIT_RUNTIME_INDEX := "res://resources/ucbv_001/kit_runtime_index.json"
const SHARED_TOKENS := "res://resources/art_styles/tokens/ucbv_001_shared_character_block_tokens.json"
const RUNTIME_CATALOG := "res://resources/block_assembly/runtime_catalog.json"

const ANIM_LIBRARY_NAME := "anim_robot_gardener_v1"
const CHARACTER_ID := "CCP-RH-001"
const RECIPE_ID := "recipe_nori7_v1"
const STYLE_LOCK_ID := "ucbv_001_style_lock_v1"
const FAMILY_ID := "ucbv_001_cozy_architecture_kit_v1"
const SKELETON_ID := "skel_small_biped_robot_v1"

## Exact 14-bone production hierarchy (parent by name; root parent null).
const REQUIRED_BONES: PackedStringArray = [
	"root", "pelvis", "spine", "chest", "head",
	"arm_L", "hand_L", "arm_R", "hand_R",
	"leg_L", "foot_L", "leg_R", "foot_R", "sprout_ctrl",
]

const BONE_PARENTS := {
	"root": "",
	"pelvis": "root",
	"spine": "pelvis",
	"chest": "spine",
	"head": "chest",
	"sprout_ctrl": "head",
	"arm_L": "chest",
	"hand_L": "arm_L",
	"arm_R": "chest",
	"hand_R": "arm_R",
	"leg_L": "pelvis",
	"foot_L": "leg_L",
	"leg_R": "pelvis",
	"foot_R": "leg_R",
}

const REQUIRED_ACTIONS: PackedStringArray = [
	"idle",
	"walk",
	"scan",
	"happy",
	"cancel",
	"turn_left",
	"turn_right",
	"build_place",
	"build_place_hold",
	"confirm",
	"water",
	"plant_seed",
	"harvest",
	"charge",
	"low_energy",
]


static func load_json(path: String) -> Variant:
	if path.is_empty() or not FileAccess.file_exists(path):
		return null
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return null
	var text := f.get_as_text()
	f.close()
	return JSON.parse_string(text)


static func is_presentation_enabled() -> bool:
	if OS.has_feature("headless"):
		return false
	if str(DisplayServer.get_name()) == "headless":
		return false
	return true


static func resolve_res_to_abs(res_path: String) -> String:
	## Convert res:// path to absolute OS path for offline GLTFDocument intake.
	if res_path.is_empty():
		return ""
	if res_path.begins_with("res://"):
		return ProjectSettings.globalize_path(res_path).replace("\\", "/")
	return res_path.replace("\\", "/")


static func sha256_file(path: String) -> String:
	var abs_path := resolve_res_to_abs(path) if path.begins_with("res://") else path.replace("\\", "/")
	if not FileAccess.file_exists(abs_path):
		return ""
	var f := FileAccess.open(abs_path, FileAccess.READ)
	if f == null:
		return ""
	var bytes := f.get_buffer(f.get_length())
	f.close()
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	ctx.update(bytes)
	return ctx.finish().hex_encode()
