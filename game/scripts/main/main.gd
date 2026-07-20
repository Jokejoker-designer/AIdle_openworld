## Main playable 2.5D shell – wires player, fixed-angle camera, world, UI.
extends Node3D

@onready var world_root: WorldRoot = $WorldRoot
@onready var player: CharacterBody3D = $Player
@onready var camera_rig: CozyCamera = $CozyCamera


func _ready() -> void:
	if camera_rig and player:
		camera_rig.set_target(player)
	if player and camera_rig and player is PlayerController:
		(player as PlayerController).set_camera_rig(camera_rig)

	# Acceptance trace for G2-001 headless smoke.
	if camera_rig and camera_rig.has_method("is_fixed_angle") and camera_rig.is_fixed_angle():
		print("[Main] Camera mode=fixed-angle 2.5D (pitch locked, no free orbit/FPS).")
	if player:
		print("[Main] Player ready: CharacterBody3D XZ locomotion on ground plane.")

	GameManager.enter_world(world_root, player)

	# Notify private reality occupancy (client space).
	if world_root and world_root.private_reality is RealitySpace:
		(world_root.private_reality as RealitySpace).notify_player_entered(player)

	# Mount lightweight stubs so ModuleRegistry is non-empty and agents see slots.
	_spawn_module_stubs()

	if SettingsManager.get_value(SettingsManager.SECTION_DEBUG, "verbose_logs", true):
		print("[Main] Entered Private Reality | style=%s" % ArtStyleManager.get_active_style_id())


func _spawn_module_stubs() -> void:
	var stub_defs := [
		[AIdleConstants.MODULE_VOXEL, "Agent-Voxel"],
		[AIdleConstants.MODULE_COMPANION, "Agent-Companion"],
		[AIdleConstants.MODULE_EXECUTOR, "Agent-Executor"],
		[AIdleConstants.MODULE_NETWORK, "Agent-Network"],
		[AIdleConstants.MODULE_SCHEMA, "Agent-Schema"],
		[AIdleConstants.MODULE_ASSET, "Agent-Asset"],
		[AIdleConstants.MODULE_PERSIST, "Agent-Persist"],
	]
	for def in stub_defs:
		var mid: String = def[0]
		var aname: String = def[1]
		if ModuleRegistry.has_module(mid) and not (ModuleRegistry.get_module(mid) is ModuleStub):
			continue
		var stub := ModuleStub.new()
		stub.module_id = mid
		stub.agent_name = aname
		stub.name = "%sStub" % aname.replace("-", "")
		stub.status_message = "Stub – %s not integrated yet" % aname
		if not ModuleRegistry.attach_to_mount(mid, stub):
			# Fallback: parent under world mounts if bind raced.
			add_child(stub)
		else:
			pass
		if not ModuleRegistry.has_module(mid):
			ModuleRegistry.register_module(mid, stub)
