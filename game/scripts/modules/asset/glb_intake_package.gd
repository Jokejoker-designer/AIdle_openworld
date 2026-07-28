## Bridge quarantine scene package reader.
## Loads scene_manifest.json + validation.json + artifact_hashes.json from an OS path.
## Re-verifies SHA-256 of every listed file; refuses the package on mismatch.
## Never promotes assets into res:// — package stays on the absolute quarantine path.
## Note: avoid class_name self-types — headless -s may miss global class cache.
extends RefCounted

const SCHEMA_HINT := "1.1"
const DEFAULT_QUARANTINE_JOB := "BLD-10A9DEB39E8E"
const DEFAULT_PACKAGE_PATH := (
	"E:/AIdle_Blender_Bridge_P0/storage/generated_quarantine/BLD-10A9DEB39E8E"
)
const _SELF_PATH := "res://scripts/modules/asset/glb_intake_package.gd"

## Absolute OS path to package root (trailing slash stripped).
var package_root: String = ""
var job_id: String = ""
var request_fingerprint: String = ""
var world_profile: String = ""
var scene_manifest: Dictionary = {}
var validation: Dictionary = {}
var artifact_hashes: Dictionary = {}
var modules: Array = []
var collision_hints: Array = []
var navigation_hints: Array = []
var camera_markers: Array = []
var build_plot: Dictionary = {}
var last_error: String = ""
var hash_report: Array = []
var refused: bool = false


static func default_package_path() -> String:
	var env := OS.get_environment("AIDLE_GLB_PACKAGE")
	if not env.is_empty():
		return env.replace("\\", "/").rstrip("/")
	return DEFAULT_PACKAGE_PATH


static func open(path: String = "") -> RefCounted:
	var script: GDScript = load(_SELF_PATH) as GDScript
	var pkg: RefCounted = script.new() as RefCounted
	var root := path if not path.is_empty() else default_package_path()
	pkg.call("load_package", root)
	return pkg


func load_package(path: String) -> bool:
	last_error = ""
	refused = false
	hash_report.clear()
	package_root = path.replace("\\", "/").rstrip("/")
	if package_root.is_empty():
		return _fail("empty_package_path")
	if not DirAccess.dir_exists_absolute(package_root):
		return _fail("package_dir_missing:%s" % package_root)

	var hashes_path := package_root.path_join("artifact_hashes.json")
	var manifest_path := package_root.path_join("scene_manifest.json")
	var validation_path := package_root.path_join("validation.json")

	artifact_hashes = _read_json_dict(hashes_path)
	if artifact_hashes.is_empty():
		return _fail("artifact_hashes_unreadable")

	scene_manifest = _read_json_dict(manifest_path)
	if scene_manifest.is_empty():
		return _fail("scene_manifest_unreadable")

	validation = _read_json_dict(validation_path)
	if validation.is_empty():
		return _fail("validation_unreadable")

	job_id = str(scene_manifest.get("job_id", artifact_hashes.get("job_id", "")))
	request_fingerprint = str(
		scene_manifest.get("request_fingerprint", artifact_hashes.get("request_fingerprint", ""))
	)
	world_profile = str(scene_manifest.get("world_profile", ""))
	modules = scene_manifest.get("modules", []) as Array
	collision_hints = scene_manifest.get("collision_hints", []) as Array
	navigation_hints = scene_manifest.get("navigation_hints", []) as Array
	camera_markers = scene_manifest.get("camera_markers", []) as Array
	if scene_manifest.get("build_plot", {}) is Dictionary:
		build_plot = (scene_manifest.get("build_plot", {}) as Dictionary).duplicate(true)
	else:
		build_plot = {}

	if not bool(validation.get("passed", false)):
		return _fail("validation_not_passed")

	if not reverify_hashes():
		refused = true
		return false

	if modules.is_empty():
		return _fail("no_modules_in_manifest")

	return true


## Re-hash every file listed in artifact_hashes.json against the bytes on disk.
## Returns false and sets refused on any missing file or digest mismatch.
func reverify_hashes() -> bool:
	hash_report.clear()
	var files: Array = artifact_hashes.get("files", []) as Array
	if files.is_empty():
		return _fail("artifact_hashes_empty_files")
	var all_ok := true
	for entry in files:
		if not (entry is Dictionary):
			all_ok = false
			hash_report.append({"path": "?", "ok": false, "reason": "bad_entry"})
			continue
		var rel := str((entry as Dictionary).get("path", ""))
		var expected := str((entry as Dictionary).get("sha256", "")).to_lower()
		var abs_path := package_root.path_join(rel)
		var row: Dictionary = {
			"path": rel,
			"expected": expected,
			"ok": false,
			"reason": "",
			"actual": "",
		}
		if expected.is_empty():
			row["reason"] = "missing_expected_sha256"
			all_ok = false
			hash_report.append(row)
			continue
		if not FileAccess.file_exists(abs_path):
			row["reason"] = "file_missing"
			all_ok = false
			hash_report.append(row)
			continue
		var actual := sha256_file(abs_path)
		row["actual"] = actual
		if actual.is_empty():
			row["reason"] = "hash_read_failed"
			all_ok = false
		elif actual != expected:
			row["reason"] = "sha256_mismatch"
			all_ok = false
		else:
			row["ok"] = true
			row["reason"] = "match"
		hash_report.append(row)
	if not all_ok:
		last_error = "hash_reverify_failed"
		refused = true
		return false
	return true


## Deliberately corrupt one artifact hash entry for negative tests (in-memory only).
func inject_tampered_hash(rel_path: String, fake_sha: String = "deadbeef") -> void:
	var files: Array = artifact_hashes.get("files", []) as Array
	for i in range(files.size()):
		if files[i] is Dictionary and str((files[i] as Dictionary).get("path", "")) == rel_path:
			var d: Dictionary = (files[i] as Dictionary).duplicate(true)
			d["sha256"] = fake_sha
			files[i] = d
			artifact_hashes["files"] = files
			return


func module_abs_path(module_entry: Dictionary) -> String:
	var rel := str(module_entry.get("artifact_path", ""))
	if rel.is_empty():
		return ""
	return package_root.path_join(rel)


func collision_hint_for(instance_id: String) -> String:
	for h in collision_hints:
		if h is Dictionary and str((h as Dictionary).get("instance_id", "")) == instance_id:
			return str((h as Dictionary).get("hint", "NONE")).to_upper()
	return "NONE"


func instance_ids() -> PackedStringArray:
	var out := PackedStringArray()
	for m in modules:
		if m is Dictionary:
			var id := str((m as Dictionary).get("instance_id", ""))
			if not id.is_empty():
				out.append(id)
	return out


func is_ready() -> bool:
	return not refused and last_error.is_empty() and not modules.is_empty() and not package_root.is_empty()


func summary() -> Dictionary:
	return {
		"package_root": package_root,
		"job_id": job_id,
		"request_fingerprint": request_fingerprint,
		"world_profile": world_profile,
		"module_count": modules.size(),
		"refused": refused,
		"last_error": last_error,
		"hash_ok_count": _hash_ok_count(),
		"hash_total": hash_report.size(),
		"validation_passed": bool(validation.get("passed", false)),
	}


static func sha256_file(abs_path: String) -> String:
	var f := FileAccess.open(abs_path, FileAccess.READ)
	if f == null:
		return ""
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	var remaining: int = f.get_length()
	while remaining > 0:
		var chunk: int = mini(remaining, 65536)
		var buf: PackedByteArray = f.get_buffer(chunk)
		if buf.is_empty():
			break
		ctx.update(buf)
		remaining -= buf.size()
	f.close()
	var digest: PackedByteArray = ctx.finish()
	return digest.hex_encode()


static func sha256_bytes(data: PackedByteArray) -> String:
	var ctx := HashingContext.new()
	ctx.start(HashingContext.HASH_SHA256)
	ctx.update(data)
	return ctx.finish().hex_encode()


func _read_json_dict(abs_path: String) -> Dictionary:
	if not FileAccess.file_exists(abs_path):
		last_error = "missing:%s" % abs_path
		return {}
	var f := FileAccess.open(abs_path, FileAccess.READ)
	if f == null:
		last_error = "open_failed:%s" % abs_path
		return {}
	var text := f.get_as_text()
	f.close()
	var parsed: Variant = JSON.parse_string(text)
	if parsed == null or not (parsed is Dictionary):
		last_error = "json_parse_failed:%s" % abs_path
		return {}
	return (parsed as Dictionary).duplicate(true)


func _hash_ok_count() -> int:
	var n := 0
	for row in hash_report:
		if row is Dictionary and bool((row as Dictionary).get("ok", false)):
			n += 1
	return n


func _fail(reason: String) -> bool:
	last_error = reason
	refused = true
	return false
