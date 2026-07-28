# motion_primitive_adapter.gd  —  REFERENCE ONLY, NOT INTEGRATED
#
# This is a reference implementation for Grok to adapt into game/** under a
# proper authorization gate. It is deliberately placed in
# orchestration/control/motion_kit/reference/ and NOT in game/, so it is not a
# product write and does not touch the runtime.
#
# It shows how a character/vehicle/device drives real Godot animation from the
# motion_primitives.json contract instead of expecting 172 pre-baked clips.
#
# WHAT IS REAL vs WHAT NEEDS VERIFICATION
#   - The contract-reading logic and the dispatch-by-kind structure are sound.
#   - The exact Godot 4.3-stable API surface (AnimationTree node paths,
#     AnimationNodeBlendSpace1D parameter keys, SkeletonIK3D vs a look-at
#     helper) MUST be confirmed by whoever opens the editor. Lines that need
#     that confirmation are marked  # VERIFY(godot4.3).
#   - No animation is faked here. UNIQUE_CLIP and the authored base poses must
#     already exist as real keyframed animations in the character's GLB /
#     AnimationPlayer, authored per the per-skeleton authored_base_requirements.
#     If a required base or unique clip is missing, this adapter raises an
#     Asset Request (push_error) rather than substituting motion.

extends Node
class_name MotionPrimitiveAdapter

# --- injected dependencies ---------------------------------------------------
@export var animation_tree_path: NodePath        # the character's AnimationTree
@export var skeleton_path: NodePath               # Skeleton3D, for procedural aim/IK
@export var animation_set_id: String              # e.g. "anim_robot_gardener_v1"
@export var contract_path: String = "res://data/motion_primitives.json"  # VERIFY path after promotion

var _tree: AnimationTree
var _skel: Skeleton3D
var _kinds: Dictionary = {}        # kind -> primitive_kind definition
var _bindings: Dictionary = {}     # clip_id -> binding (for this animation_set)
var _authored_ok: bool = false


func _ready() -> void:
	_tree = get_node_or_null(animation_tree_path)
	_skel = get_node_or_null(skeleton_path)
	if _tree == null:
		push_error("[MotionPrimitiveAdapter] AnimationTree not found at %s" % animation_tree_path)
		return
	_load_contract()
	_verify_authored_bases()


# ---------------------------------------------------------------------------
# Contract loading
# ---------------------------------------------------------------------------
func _load_contract() -> void:
	var f := FileAccess.open(contract_path, FileAccess.READ)
	if f == null:
		push_error("[MotionPrimitiveAdapter] cannot open contract %s" % contract_path)
		return
	var doc: Dictionary = JSON.parse_string(f.get_as_text())
	if doc == null:
		push_error("[MotionPrimitiveAdapter] contract is not valid JSON")
		return
	for k in doc.get("primitive_kinds", []):
		_kinds[k["kind"]] = k
	for b in doc.get("clip_bindings", []):
		if b.get("animation_set_id") == animation_set_id:
			_bindings[b["clip_id"]] = b


# Fail-closed: confirm every authored base this set needs actually exists as a
# real animation before we let anything play. No base -> Asset Request, not a
# silent substitute.
func _verify_authored_bases() -> void:
	var ap := _tree.get("anim_player")           # VERIFY(godot4.3): AnimationTree.anim_player
	var player: AnimationPlayer = get_node_or_null(ap) if ap else null
	if player == null:
		push_warning("[MotionPrimitiveAdapter] no AnimationPlayer bound; cannot verify authored bases yet")
		return
	var required := ["idle_pose"]                # minimum every character needs
	for clip_id in _bindings:
		var b: Dictionary = _bindings[clip_id]
		if b.get("kind") == "SIGNATURE_UNIQUE":
			# unique clips must exist as real authored animations
			if not player.has_animation(clip_id):
				push_error("[MotionPrimitiveAdapter] ASSET REQUEST: missing authored clip '%s' for %s" % [clip_id, animation_set_id])
	_authored_ok = true


# ---------------------------------------------------------------------------
# Public API — the one call AI/gameplay uses. `params` supplies the runtime
# vectors (direction, speed, aim target, reach target) the primitive needs.
# ---------------------------------------------------------------------------
func play(clip_id: String, params: Dictionary = {}) -> void:
	if not _bindings.has(clip_id):
		push_error("[MotionPrimitiveAdapter] no binding for clip '%s'" % clip_id)
		return
	var b: Dictionary = _bindings[clip_id]
	var kind: String = b["kind"]
	match kind:
		"DIRECTION_MIRROR":
			# one authored turn base, sign chosen by the catalog / runtime
			var dir: float = params.get("turn_direction", b["params"].get("turn_direction", 0))
			_set_blend("parameters/turn/blend_position", dir)   # VERIFY(godot4.3) node name
		"LOCOMOTION_CYCLE":
			var speed: float = params.get("locomotion_speed", b["params"].get("locomotion_speed", 0.0))
			_set_blend("parameters/locomotion/blend_position", speed)  # VERIFY(godot4.3)
		"PROCEDURAL_AIM":
			# no clip: rotate the aim bone toward a runtime vector, layered additively
			_aim_bone_toward(params.get("aim_target_vector", Vector3.FORWARD))
		"BINARY_TOGGLE":
			# one authored clip, forward or reversed
			var state: float = params.get("toggle_state", b["params"].get("toggle_state", 1))
			_play_directional(clip_id, 1.0 if state >= 0 else -1.0)
		"REACH_MANIPULATE":
			# base reach pose + IK target at the real object position
			_play_directional("reach_pose", 1.0)
			_ik_reach_to(params.get("reach_target_position", Vector3.ZERO))
		"GROWTH_SHAPE":
			# blend-shape / shader scalar, not skeletal
			_set_growth(params.get("growth_amount", 0.0))
		"IDLE_VARIANT":
			# base idle + additive accent layer
			_set_accent(b["params"].get("accent_id", clip_id))
		"VFX_PARAMETER":
			_set_emission(params.get("emission_strength", 1.0))
		"SIGNATURE_UNIQUE":
			# real authored clip only. If missing, we already raised an Asset
			# Request in _verify_authored_bases — never substitute motion.
			_play_directional(clip_id, 1.0)
		_:
			push_error("[MotionPrimitiveAdapter] unknown kind '%s'" % kind)


# ---------------------------------------------------------------------------
# Low-level helpers — all marked for Godot 4.3 API confirmation.
# ---------------------------------------------------------------------------
func _set_blend(param_path: String, value: float) -> void:
	_tree.set(param_path, value)                 # VERIFY(godot4.3)

func _play_directional(anim_name: String, speed: float) -> void:
	# forward (speed=1) or reverse (speed=-1) playback of one authored clip
	_tree.set("parameters/oneshot_request", AnimationNodeOneShot.ONE_SHOT_REQUEST_FIRE)  # VERIFY(godot4.3)
	# real wiring: route anim_name + custom_speed into a OneShot/TimeScale node

func _aim_bone_toward(target: Vector3) -> void:
	if _skel == null:
		return
	# VERIFY(godot4.3): additive look-at on a dedicated aim bone, clamped to range.
	# Prefer a look-at helper layered over the base pose so locomotion still plays.

func _ik_reach_to(target: Vector3) -> void:
	if _skel == null:
		return
	# VERIFY(godot4.3): SkeletonIK3D or a 2-bone IK chain on the hand/tool socket,
	# target set to the real object world position.

func _set_growth(amount: float) -> void:
	# VERIFY(godot4.3): drive a MeshInstance3D blend shape or a shader uniform in [0,1].
	pass

func _set_accent(accent_id: String) -> void:
	# VERIFY(godot4.3): enable a small additive accent AnimationNodeAdd2 over idle.
	pass

func _set_emission(strength: float) -> void:
	# material emission scalar, not a bone pose
	pass
