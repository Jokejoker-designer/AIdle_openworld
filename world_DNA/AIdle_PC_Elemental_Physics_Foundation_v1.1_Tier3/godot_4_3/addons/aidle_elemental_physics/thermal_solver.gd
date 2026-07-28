class_name AIdleThermalSolver
extends RefCounted

static func step_temperature(current: float, ambient: float, heat_capacity: float,
        conductivity: float, heat_input: float, delta_s: float) -> float:
    var next := current + ((ambient-current)*conductivity + heat_input) / maxf(heat_capacity,0.01) * delta_s
    return clampf(next,0.0,1.0)
