## aidle_canonical_json_v1 — deterministic UTF-8 JSON for hashing and durable material.
## Godot JSON.stringify does NOT sort keys; this pure GDScript path is the sole hash input.
## Rules: sorted object keys, stable entity_id order (caller), compact (no pretty),
## fixed float format (max 6 fractional digits, strip trailing zeros).
class_name AIdleCanonicalJson
extends RefCounted

const SCHEMA_NAME := "aidle_canonical_json_v1"
const FLOAT_FRAC_DIGITS := 6


## Compact canonical JSON string. Same logical value => identical bytes.
static func stringify(value: Variant) -> String:
	return _stringify(value)


static func _stringify(value: Variant) -> String:
	var t: int = typeof(value)
	match t:
		TYPE_NIL:
			return "null"
		TYPE_BOOL:
			return "true" if value else "false"
		TYPE_INT:
			return str(value as int)
		TYPE_FLOAT:
			return format_float(value as float)
		TYPE_STRING:
			return "\"%s\"" % escape_string(value as String)
		TYPE_ARRAY, TYPE_PACKED_STRING_ARRAY, TYPE_PACKED_INT32_ARRAY, TYPE_PACKED_FLOAT32_ARRAY:
			return _stringify_array(value)
		TYPE_DICTIONARY:
			return _stringify_object(value as Dictionary)
		_:
			# Fail closed for non-JSON Godot types in durable material.
			push_error("[AIdleCanonicalJson] unsupported type %s" % t)
			return "null"


static func _stringify_array(value: Variant) -> String:
	var parts: PackedStringArray = PackedStringArray()
	for item in value:
		parts.append(_stringify(item))
	return "[" + ",".join(parts) + "]"


static func _stringify_object(obj: Dictionary) -> String:
	var keys: Array = obj.keys()
	keys.sort_custom(func(a: Variant, b: Variant) -> bool:
		return str(a) < str(b)
	)
	var parts: PackedStringArray = PackedStringArray()
	for k in keys:
		var key_s: String = str(k)
		parts.append("\"%s\":%s" % [escape_string(key_s), _stringify(obj[k])])
	return "{" + ",".join(parts) + "}"


## Floats: max 6 fractional digits, strip trailing zeros and trailing decimal point.
## Examples: 8.0 -> "8"; 8.500000 -> "8.5"; 0.12 -> "0.12". Reject non-finite as "null".
static func format_float(f: float) -> String:
	if is_nan(f) or is_inf(f):
		push_error("[AIdleCanonicalJson] non-finite float rejected")
		return "null"
	# Normalize -0.0 to 0
	if f == 0.0:
		return "0"
	var negative: bool = f < 0.0
	var abs_f: float = absf(f)
	var scale: float = pow(10.0, float(FLOAT_FRAC_DIGITS))
	var scaled: float = round(abs_f * scale)
	var whole: int = int(scaled / scale)
	var frac_i: int = int(scaled) % int(scale)
	var out: String
	if frac_i == 0:
		out = str(whole)
	else:
		var frac_s: String = str(frac_i).pad_zeros(FLOAT_FRAC_DIGITS)
		# Strip trailing zeros
		while frac_s.length() > 0 and frac_s[frac_s.length() - 1] == "0":
			frac_s = frac_s.substr(0, frac_s.length() - 1)
		out = "%d.%s" % [whole, frac_s]
	if negative:
		return "-" + out
	return out


static func escape_string(s: String) -> String:
	var out := ""
	for i in s.length():
		var ch: String = s[i]
		var code: int = s.unicode_at(i)
		match ch:
			"\\":
				out += "\\\\"
			"\"":
				out += "\\\""
			"\b":
				out += "\\b"
			"\f":
				out += "\\f"
			"\n":
				out += "\\n"
			"\r":
				out += "\\r"
			"\t":
				out += "\\t"
			_:
				if code < 0x20:
					out += "\\u%04x" % code
				else:
					out += ch
	return out


## Sort unique string list ascending (for interaction_tags, entity_ids hash material).
static func sorted_unique_strings(items: Array) -> Array:
	var seen: Dictionary = {}
	var out: Array = []
	for item in items:
		var s: String = str(item)
		if seen.has(s):
			continue
		seen[s] = true
		out.append(s)
	out.sort()
	return out
