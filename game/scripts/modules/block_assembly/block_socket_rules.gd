## Socket mutual-compatibility + pair-bound normalization enforcement.
## Semantics from accepted socket_catalog.contract.json (embedded runtime snapshot).
## Peer-launder / one-way compatibility / unknown sockets REJECT.
class_name BlockSocketRules
extends RefCounted

const _C = preload("res://scripts/modules/block_assembly/block_assembly_constants.gd")

var _loaded: bool = false
var _load_error: String = ""
## socket_type -> {default_polarity, compatible_with: PackedStringArray}
var _types: Dictionary = {}
## normalization_id -> {pair: Array, orientations: Array}
var _norms: Dictionary = {}
## unordered pair key "a|b" (sorted) -> Array of norm records that cover it
var _pair_to_norms: Dictionary = {}


func ensure_loaded() -> bool:
	if _loaded:
		return _load_error.is_empty()
	_loaded = true
	if not FileAccess.file_exists(_C.SOCKET_RULES_PATH):
		_load_error = "socket_rules_missing"
		return false
	var f := FileAccess.open(_C.SOCKET_RULES_PATH, FileAccess.READ)
	if f == null:
		_load_error = "socket_rules_unreadable"
		return false
	var parsed: Variant = JSON.parse_string(f.get_as_text())
	f.close()
	if not (parsed is Dictionary):
		_load_error = "socket_rules_parse"
		return false
	var root: Dictionary = parsed
	for st in root.get("socket_types", []):
		if not (st is Dictionary):
			continue
		var d: Dictionary = st
		var sid := str(d.get("socket_type", ""))
		if sid.is_empty():
			continue
		var compat: PackedStringArray = PackedStringArray()
		for c in d.get("compatible_with", []):
			compat.append(str(c))
		_types[sid] = {
			"default_polarity": str(d.get("default_polarity", "peer")),
			"compatible_with": compat,
		}
	for n in root.get("adapter_normalizations", []):
		if not (n is Dictionary):
			continue
		var nd: Dictionary = n
		var nid := str(nd.get("normalization_id", ""))
		if nid.is_empty():
			continue
		var pair: Array = nd.get("pair", []) as Array
		var orients: Array = nd.get("allowed_orientations", []) as Array
		_norms[nid] = {"pair": pair.duplicate(), "orientations": orients.duplicate(true)}
		if pair.size() == 2:
			var pk := _pair_key(str(pair[0]), str(pair[1]))
			if not _pair_to_norms.has(pk):
				_pair_to_norms[pk] = []
			(_pair_to_norms[pk] as Array).append(nid)
	return true


func get_load_error() -> String:
	ensure_loaded()
	return _load_error


func is_known_socket(socket_type: String) -> bool:
	ensure_loaded()
	return _types.has(socket_type)


func default_polarity(socket_type: String) -> String:
	ensure_loaded()
	if not _types.has(socket_type):
		return ""
	return str((_types[socket_type] as Dictionary).get("default_polarity", ""))


func validate_edge(edge: Dictionary) -> Dictionary:
	## edge keys: from_socket, to_socket, from_polarity, to_polarity, normalization_id?
	ensure_loaded()
	if not _load_error.is_empty():
		return {"ok": false, "code": "catalog_unavailable", "reason": _load_error}

	var from_s := str(edge.get("from_socket", ""))
	var to_s := str(edge.get("to_socket", ""))
	var from_p := str(edge.get("from_polarity", ""))
	var to_p := str(edge.get("to_polarity", ""))
	var norm_id := str(edge.get("normalization_id", ""))

	if not is_known_socket(from_s):
		return {"ok": false, "code": "unknown_socket", "reason": "from_socket=%s" % from_s}
	if not is_known_socket(to_s):
		return {"ok": false, "code": "unknown_socket", "reason": "to_socket=%s" % to_s}

	# Same polarity (except peer-peer) rejects.
	if from_p == to_p and from_p != "peer":
		return {
			"ok": false,
			"code": "same_polarity",
			"reason": "from_polarity=%s to_polarity=%s" % [from_p, to_p],
		}

	# Mutual compatibility both directions.
	if not _mutual_compatible(from_s, to_s):
		return {
			"ok": false,
			"code": "one_way_or_incompatible",
			"reason": "%s not mutually compatible with %s" % [from_s, to_s],
		}

	# Peer launder: directed polarities on peer-default sockets without pair-bound norm.
	var from_def := default_polarity(from_s)
	var to_def := default_polarity(to_s)
	var directed_on_peer := (
		(from_def == "peer" or to_def == "peer")
		and (from_p in ["input", "output"] or to_p in ["input", "output"])
		and not (from_p == "peer" and to_p == "peer")
	)
	if directed_on_peer and norm_id.is_empty():
		return {
			"ok": false,
			"code": "peer_launder",
			"reason": "directed polarity on peer sockets requires pair-bound normalization",
		}

	# Asymmetric catalog pairs may require normalization.
	var needs_norm := _pair_requires_normalization(from_s, to_s)
	if needs_norm and norm_id.is_empty():
		return {
			"ok": false,
			"code": "missing_normalization",
			"reason": "pair %s|%s requires pair-bound normalization" % [from_s, to_s],
		}

	if not norm_id.is_empty():
		if not _norms.has(norm_id):
			return {
				"ok": false,
				"code": "unknown_normalization",
				"reason": "normalization_id=%s" % norm_id,
			}
		var nr: Dictionary = _norms[norm_id]
		var pair: Array = nr.get("pair", []) as Array
		if pair.size() != 2:
			return {"ok": false, "code": "bad_normalization", "reason": "pair incomplete"}
		var a := str(pair[0])
		var b := str(pair[1])
		var covers := (from_s == a and to_s == b) or (from_s == b and to_s == a)
		if not covers:
			return {
				"ok": false,
				"code": "wrong_normalization",
				"reason": "norm %s does not cover pair %s|%s" % [norm_id, from_s, to_s],
			}
		if not _orientation_allowed(nr, from_s, to_s, from_p, to_p):
			return {
				"ok": false,
				"code": "wrong_normalization",
				"reason": "orientation not in allowed_orientations for %s" % norm_id,
			}

	# Classic opposite polarity for directed sockets (output->input).
	if from_p == "output" and to_p != "input" and to_p != "peer":
		return {
			"ok": false,
			"code": "polarity_mismatch",
			"reason": "output must connect to input/peer",
		}
	if from_p == "input" and to_p == "input":
		return {"ok": false, "code": "same_polarity", "reason": "input-input forbidden"}

	return {
		"ok": true,
		"from_socket": from_s,
		"to_socket": to_s,
		"normalization_id": norm_id,
	}


func _mutual_compatible(a: String, b: String) -> bool:
	if not _types.has(a) or not _types.has(b):
		return false
	var ca: PackedStringArray = (_types[a] as Dictionary).get("compatible_with", PackedStringArray())
	var cb: PackedStringArray = (_types[b] as Dictionary).get("compatible_with", PackedStringArray())
	return b in ca and a in cb


func _pair_requires_normalization(a: String, b: String) -> bool:
	var pk := _pair_key(a, b)
	return _pair_to_norms.has(pk)


func _orientation_allowed(
	nr: Dictionary, from_s: String, to_s: String, from_p: String, to_p: String
) -> bool:
	for o in nr.get("orientations", []):
		if not (o is Dictionary):
			continue
		var od: Dictionary = o
		if (
			str(od.get("from_socket", "")) == from_s
			and str(od.get("to_socket", "")) == to_s
			and str(od.get("from_polarity", "")) == from_p
			and str(od.get("to_polarity", "")) == to_p
		):
			return true
	return false


static func _pair_key(a: String, b: String) -> String:
	if a <= b:
		return "%s|%s" % [a, b]
	return "%s|%s" % [b, a]
