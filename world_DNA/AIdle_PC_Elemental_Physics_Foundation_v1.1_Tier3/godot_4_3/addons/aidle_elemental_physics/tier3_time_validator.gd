class_name AIdleTier3TimeValidator
extends RefCounted

static func validate(saved_wall_clock_unix: float, current_wall_clock_unix: float,
        saved_monotonic_msec: int, current_monotonic_msec: int,
        max_offline_seconds: float) -> Dictionary:
    var observed := current_wall_clock_unix - saved_wall_clock_unix
    var used := observed
    var decision := "ACCEPTED"
    if observed < 0.0:
        used = 0.0
        decision = "CLOCK_BACKWARD_REJECTED"
    elif observed > max_offline_seconds:
        used = max_offline_seconds
        decision = "MAX_OFFLINE_CLAMPED"
    var monotonic_reset := current_monotonic_msec < saved_monotonic_msec
    var monotonic_delta: Variant = null
    if not monotonic_reset:
        monotonic_delta = float(current_monotonic_msec - saved_monotonic_msec) / 1000.0
    return {
        "observed_elapsed_seconds": observed,
        "used_elapsed_seconds": used,
        "time_decision": decision,
        "saved_wall_clock_unix": saved_wall_clock_unix,
        "current_wall_clock_unix": current_wall_clock_unix,
        "saved_monotonic_msec": saved_monotonic_msec,
        "current_monotonic_msec": current_monotonic_msec,
        "monotonic_delta_seconds": monotonic_delta,
        "monotonic_reset_detected": monotonic_reset,
        "max_offline_seconds": max_offline_seconds,
    }
