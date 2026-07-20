## WorldRoot – Reality Hierarchy (Master Blueprint §3). LOCKED structure:
##   WorldRoot
##     PrivateReality
##     SharedDistricts
##     DoppelgangerCities
##     Orbital
##     Exoplanets
##     ModuleMounts (Voxel / Companion / Executor / Network / Schema / Asset / Persist)
##     Systems (lighting, env – core only)
##
## Agent-Voxel fills ManifestationHost under each space + VoxelMount.
## Do NOT rename hierarchy nodes without blueprint version bump.
class_name WorldRoot
extends Node3D

@onready var private_reality: Node3D = $PrivateReality
@onready var shared_districts: Node3D = $SharedDistricts
@onready var doppelganger_cities: Node3D = $DoppelgangerCities
@onready var orbital: Node3D = $Orbital
@onready var exoplanets: Node3D = $Exoplanets
@onready var module_mounts: Node3D = $ModuleMounts


func _ready() -> void:
	_configure_spaces()
	_bind_module_mounts()
	# Under headless/dummy: clear presentation meshes before any material write
	# (avoids dummy mesh_get_surface_count ERROR). Real logic/hierarchy stays.
	_disable_presentation_meshes_if_headless()
	_apply_art_style_environment()
	if not EventBus.art_style_changed.is_connected(_on_art_style_changed):
		EventBus.art_style_changed.connect(_on_art_style_changed)
	print("[WorldRoot] Hierarchy ready (Blueprint v1.0).")


func _configure_spaces() -> void:
	_setup_space(private_reality, AIdleConstants.SPACE_PRIVATE_REALITY, "Private Reality", "client")
	_setup_space(shared_districts, AIdleConstants.SPACE_SHARED_DISTRICT, "Shared Districts", "server")
	_setup_space(doppelganger_cities, AIdleConstants.SPACE_DOPPELGANGER_CITY, "Doppelgänger Cities", "server")
	_setup_space(orbital, AIdleConstants.SPACE_SPACECRAFT, "Orbital & Spacecraft", "owner")
	_setup_space(exoplanets, AIdleConstants.SPACE_EXOPLANET, "Exoplanets", "owner")


func _setup_space(node: Node3D, space_id: String, display: String, authority: String) -> void:
	if node == null:
		push_error("[WorldRoot] Missing hierarchy node for %s" % space_id)
		return
	if node is RealitySpace:
		var rs := node as RealitySpace
		rs.space_id = space_id
		rs.display_name = display
		rs.authority = authority
		rs.art_style = ArtStyleManager.get_active_style_id()
	else:
		# Fallback meta if script not attached yet.
		node.set_meta("space_id", space_id)
		node.set_meta("authority", authority)
	# Ensure progressive construction host exists (Agent-Voxel owns children).
	var host := node.get_node_or_null("ManifestationHost")
	if host == null:
		host = Node3D.new()
		host.name = "ManifestationHost"
		node.add_child(host)
	host.set_meta("awaiting_agent_voxel", true)
	host.set_meta("construction_progress_layer", true)


func _bind_module_mounts() -> void:
	if module_mounts == null:
		push_error("[WorldRoot] ModuleMounts missing.")
		return
	var pairs := {
		AIdleConstants.MODULE_VOXEL: "VoxelMount",
		AIdleConstants.MODULE_COMPANION: "CompanionMount",
		AIdleConstants.MODULE_EXECUTOR: "ExecutorMount",
		AIdleConstants.MODULE_NETWORK: "NetworkMount",
		AIdleConstants.MODULE_SCHEMA: "SchemaMount",
		AIdleConstants.MODULE_ASSET: "AssetMount",
		AIdleConstants.MODULE_PERSIST: "PersistMount",
	}
	for module_id in pairs.keys():
		var child_name: String = pairs[module_id]
		var mount := module_mounts.get_node_or_null(child_name)
		if mount == null:
			mount = Node3D.new()
			mount.name = child_name
			module_mounts.add_child(mount)
		ModuleRegistry.bind_mount(module_id, mount)


func get_space_node(space_id: String) -> Node3D:
	match space_id:
		AIdleConstants.SPACE_PRIVATE_REALITY:
			return private_reality
		AIdleConstants.SPACE_SHARED_DISTRICT:
			return shared_districts
		AIdleConstants.SPACE_DOPPELGANGER_CITY:
			return doppelganger_cities
		AIdleConstants.SPACE_SPACECRAFT:
			return orbital
		AIdleConstants.SPACE_EXOPLANET:
			return exoplanets
		_:
			return private_reality


func get_manifestation_host(space_id: String) -> Node3D:
	var space := get_space_node(space_id)
	if space == null:
		return null
	return space.get_node_or_null("ManifestationHost") as Node3D


func _on_art_style_changed(style_id: String) -> void:
	for n in get_tree().get_nodes_in_group("reality_spaces"):
		if n is RealitySpace:
			(n as RealitySpace).set_art_style(style_id)
	_apply_art_style_environment()


func _is_headless_presentation() -> bool:
	if AIdleConstants != null and AIdleConstants.has_method("is_headless_or_dummy_presentation"):
		return bool(AIdleConstants.is_headless_or_dummy_presentation())
	return OS.has_feature("headless") or DisplayServer.get_name() == "headless"


func _disable_presentation_meshes_if_headless() -> void:
	if not _is_headless_presentation():
		return
	var ground := get_node_or_null("Systems/Ground/MeshInstance3D") as MeshInstance3D
	if ground != null:
		ground.mesh = null
		ground.material_override = null
		ground.visible = false


func _apply_art_style_environment() -> void:
	var style := ArtStyleManager.get_active_style()
	var palette: Dictionary = style.get("palette", {})
	# Presentation-only material on ground mesh — skip under headless/dummy renderer.
	if not _is_headless_presentation():
		var ground := get_node_or_null("Systems/Ground/MeshInstance3D") as MeshInstance3D
		if ground and ground.mesh:
			var mat := StandardMaterial3D.new()
			mat.albedo_color = palette.get("ground", Color("8FBC8F"))
			mat.roughness = 0.85
			ground.material_override = mat
	var world_env := get_node_or_null("Systems/WorldEnvironment") as WorldEnvironment
	if world_env and world_env.environment:
		var sky_color: Color = palette.get("sky", Color("8EC5E8"))
		world_env.environment.background_mode = Environment.BG_COLOR
		world_env.environment.background_color = sky_color
		world_env.environment.ambient_light_color = sky_color.lightened(0.2)
		world_env.environment.ambient_light_energy = 0.55
