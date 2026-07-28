## Grid / elevation / rotation snap — contract values only (not free float).
class_name BlockPlacementMath
extends RefCounted

const _C = preload("res://scripts/modules/block_assembly/block_assembly_constants.gd")


static func snap_grid(value: float, step: float = _C.GRID_SNAP_M) -> float:
	if step <= 0.0:
		return value
	return round(value / step) * step


static func snap_elevation(value: float, step: float = _C.ELEVATION_SNAP_M) -> float:
	if step <= 0.0:
		return value
	var s: float = round(value / step) * step
	return maxf(0.0, s)


static func snap_rotation_deg(value: float, step: float = _C.ROTATION_SNAP_DEG) -> float:
	if step <= 0.0:
		return value
	var s: float = fposmod(round(value / step) * step, 360.0)
	if s >= 360.0 - 0.0001:
		return 0.0
	return s


static func is_on_grid(value: float, step: float = _C.GRID_SNAP_M, eps: float = 0.0001) -> bool:
	var sn := snap_grid(value, step)
	return absf(value - sn) <= eps


static func is_on_elevation(value: float, step: float = _C.ELEVATION_SNAP_M, eps: float = 0.0001) -> bool:
	var sn := snap_elevation(value, step)
	return absf(value - sn) <= eps


static func is_on_rotation(value: float, step: float = _C.ROTATION_SNAP_DEG, eps: float = 0.0001) -> bool:
	var sn := snap_rotation_deg(value, step)
	var v := fposmod(value, 360.0)
	return absf(v - sn) <= eps or absf(v - sn - 360.0) <= eps or absf(v - sn + 360.0) <= eps


static func apply_placement(
	raw_x: float,
	raw_y: float,
	raw_elev: float,
	raw_rot: float,
	snap_enabled: bool = true
) -> Dictionary:
	if not snap_enabled:
		# Free float is not allowed for authoritative placement validation.
		return {
			"ok": false,
			"code": "free_float_forbidden",
			"reason": "placement must use contract snap values",
		}
	var x := snap_grid(raw_x)
	var y := snap_grid(raw_y)
	var elev := snap_elevation(raw_elev)
	var rot := snap_rotation_deg(raw_rot)
	return {
		"ok": true,
		"x": x,
		"y": y,
		"elevation": elev,
		"rotation_deg": rot,
		"grid_snap_m": _C.GRID_SNAP_M,
		"elevation_snap_m": _C.ELEVATION_SNAP_M,
		"rotation_snap_deg": _C.ROTATION_SNAP_DEG,
	}
