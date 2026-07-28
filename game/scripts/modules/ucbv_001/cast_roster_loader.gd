## Builds a gallery of cast presenters from cast_roster.json.
extends Node3D

const _CastPresenter := preload("res://scripts/modules/ucbv_001/cast_presenter.gd")
const ROSTER := "res://resources/ucbv_001/cast/cast_roster.json"

var _presenters: Array = []
var _last_report: Dictionary = {}


func get_report() -> Dictionary:
	return _last_report.duplicate(true)


func build_gallery(spacing: float = 1.8) -> Dictionary:
	_clear()
	var roster: Variant = _load_json(ROSTER)
	if roster == null or not (roster is Dictionary):
		_last_report = {"ok": false, "error": "roster_missing"}
		return _last_report
	var chars: Array = roster.get("characters", []) as Array
	var built := 0
	var failed: Array = []
	var i := 0
	for c in chars:
		if not (c is Dictionary):
			continue
		var cid := str(c.get("character_id", ""))
		var glb := str(c.get("glb", ""))
		var sha := str(c.get("glb_sha256", ""))
		var p: Node3D = _CastPresenter.new() as Node3D
		p.name = "Cast_%s" % cid.replace("-", "_")
		p.position = Vector3(float(i) * spacing, 0.0, 0.0)
		add_child(p)
		if p.has_method("configure_from_roster_row"):
			p.call("configure_from_roster_row", c)
		elif p.has_method("configure"):
			p.call("configure", cid, glb, sha)
		var st: Dictionary = p.call("build_from_assets") as Dictionary
		_presenters.append(p)
		if bool(st.get("built", false)):
			built += 1
		else:
			failed.append({"id": cid, "error": st.get("error", "unknown"), "detail": st.get("detail", {})})
		i += 1
	_last_report = {
		"ok": failed.is_empty() and built == chars.size(),
		"built": built,
		"total": chars.size(),
		"failed": failed,
	}
	return _last_report


func play_all(clip_id: String = "idle") -> int:
	var n := 0
	for p in _presenters:
		if is_instance_valid(p) and p.has_method("play_clip"):
			if bool(p.call("play_clip", clip_id)):
				n += 1
	return n


func _clear() -> void:
	for p in _presenters:
		if is_instance_valid(p):
			p.queue_free()
	_presenters.clear()


func _load_json(path: String) -> Variant:
	if not FileAccess.file_exists(path):
		return null
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return null
	var t := f.get_as_text()
	f.close()
	return JSON.parse_string(t)
