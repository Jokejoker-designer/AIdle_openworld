class_name AIdleBiologicalSolver
extends RefCounted

static func crop_growth(water: float, light: float, fertility: float, temperature_fit: float, delta_s: float) -> Dictionary:
    var limiting := minf(minf(water,light),minf(fertility,temperature_fit))
    return {"growth_delta":maxf(limiting,0.0)*delta_s*0.001,
            "health_delta":(limiting-0.35)*delta_s*0.0004}
