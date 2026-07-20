## Agent-Asset thin module (G3-001 W1): house-recipe resolution + provenance gate.
## No paid gen APIs, no neural world model, no durable world mutation.
## Registers ModuleRegistry slot "asset" when present; W2 may also load resolver directly.
class_name AssetModule
extends Node

const MODULE_ID := "asset"
const _Resolver = preload("res://scripts/modules/asset/house_recipe_resolver.gd")

var _resolver: RefCounted


func _ready() -> void:
	_ensure_resolver()
	_try_register()
	print("[AssetModule] Ready – house recipe resolver + provenance validation.")


func is_stub() -> bool:
	return false


func get_status() -> String:
	return "Asset online | recipe_resolver=ready | paid_gen=false | neural_wm=false"


func get_resolver() -> RefCounted:
	return _ensure_resolver()


func _ensure_resolver() -> RefCounted:
	if _resolver == null:
		_resolver = _Resolver.new()
	return _resolver


## resolve_recipe("cozy_house_small") → parts, build_order, collision_policy, style tokens ref
func resolve_recipe(recipe_id: String = "cozy_house_small") -> Dictionary:
	return _ensure_resolver().call("resolve_recipe", recipe_id) as Dictionary


## validate_provenance("recipe:cozy_house_small") or bare recipe_id
func validate_provenance(asset_id: String = "recipe:cozy_house_small") -> Dictionary:
	return _ensure_resolver().call("validate_provenance", asset_id) as Dictionary


## Geometry dict for ManifestationModule.start_manifestation (Starter Realm defaults).
func export_geometry_for_preview(recipe_id: String = "cozy_house_small", overrides: Dictionary = {}) -> Dictionary:
	return _ensure_resolver().call("export_geometry_dict", recipe_id, overrides) as Dictionary


## Bundled resolve + provenance + geometry for G3 onboarding house path.
func resolve_cozy_house_for_starter(overrides: Dictionary = {}) -> Dictionary:
	return _ensure_resolver().call("resolve_cozy_house_for_starter", overrides) as Dictionary


func get_last_error() -> String:
	return str(_ensure_resolver().call("get_last_error"))


func _try_register() -> void:
	var reg: Node = _autoload("ModuleRegistry")
	if reg == null:
		return
	var existing: Node = reg.call("get_module", MODULE_ID) as Node
	if existing == null or existing == self or (existing.has_method("is_stub") and bool(existing.call("is_stub"))):
		reg.call("register_module", MODULE_ID, self)


func _autoload(name: String) -> Node:
	var tree: MainLoop = Engine.get_main_loop()
	if tree is SceneTree:
		return (tree as SceneTree).root.get_node_or_null(name)
	return null
