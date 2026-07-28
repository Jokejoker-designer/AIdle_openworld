class_name AIdleTier3FarmSolver
extends RefCounted

static func advance(state: Dictionary, elapsed_seconds: float, config: Dictionary,
        pond_available: bool) -> Dictionary:
    var result := state.duplicate(true)
    var farm: Dictionary = config["farm_solver"]
    var wetness_before := clampf(float(result.get("wetness", 0.0)), 0.0, 1.0)
    var growth_before := clampf(float(result.get("growth", 0.0)), 0.0, 1.0)
    var decay := float(farm["wetness_decay_per_second"])
    var source := float(farm["pond_replenish_per_second"]) if pond_available else 0.0
    var slope := source - decay
    var limiting := minf(
        clampf(float(result.get("light", farm["default_light"])), 0.0, 1.0),
        minf(
            clampf(float(result.get("fertility", farm["default_fertility"])), 0.0, 1.0),
            clampf(float(result.get("temperature_fit", farm["default_temperature_fit"])), 0.0, 1.0)
        )
    )
    var integral := _integral_min_clamped_linear(wetness_before, slope, limiting, elapsed_seconds)
    var growth_delta := float(farm["growth_rate_per_second"]) * float(integral["area"])
    result["wetness"] = clampf(wetness_before + slope * elapsed_seconds, 0.0, 1.0)
    result["growth"] = clampf(growth_before + growth_delta, 0.0, 1.0)
    result["health"] = clampf(float(result.get("health", 1.0)), 0.0, 1.0)
    result["visual_variant"] = "wet" if result["wetness"] >= float(farm["wet_variant_threshold"]) else "default"
    return {
        "state": result,
        "metrics": {
            "wetness_before": wetness_before,
            "wetness_after": result["wetness"],
            "growth_before": growth_before,
            "growth_after": result["growth"],
            "growth_delta": result["growth"] - growth_before,
            "pond_available": pond_available,
            "closed_form_segments": integral["segments"],
            "selected_visual_variant": result["visual_variant"],
        }
    }

static func _integral_min_clamped_linear(w0: float, slope: float, limit: float,
        elapsed: float) -> Dictionary:
    if elapsed <= 0.0:
        return {"area": 0.0, "segments": 0}
    var points: Array[float] = [0.0, elapsed]
    if absf(slope) > 0.000000000000000001:
        for boundary in [0.0, limit, 1.0]:
            var t := (float(boundary) - w0) / slope
            if t > 0.0 and t < elapsed:
                points.append(t)
    points.sort()
    var unique: Array[float] = []
    for point in points:
        if unique.is_empty() or not is_equal_approx(unique[-1], point):
            unique.append(point)
    var area := 0.0
    var segments := 0
    for index in range(unique.size() - 1):
        var a := unique[index]
        var b := unique[index + 1]
        var fa := minf(clampf(w0 + slope * a, 0.0, 1.0), limit)
        var fb := minf(clampf(w0 + slope * b, 0.0, 1.0), limit)
        area += (fa + fb) * 0.5 * (b - a)
        segments += 1
    return {"area": area, "segments": segments}
