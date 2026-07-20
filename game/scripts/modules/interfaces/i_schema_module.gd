## Interface contract for Agent-Schema.
class_name ISchemaModule
extends RefCounted

## Expected methods:
## func validate_prompt(data: Dictionary) -> Dictionary
##   returns { "ok": bool, "errors": PackedStringArray, "normalized": Dictionary }
## func get_schema_version() -> String

const REQUIRED_METHODS := ["validate_prompt", "get_schema_version"]


static func validate(module: Object) -> PackedStringArray:
	var missing: PackedStringArray = []
	for m in REQUIRED_METHODS:
		if not module.has_method(m):
			missing.append(m)
	return missing
