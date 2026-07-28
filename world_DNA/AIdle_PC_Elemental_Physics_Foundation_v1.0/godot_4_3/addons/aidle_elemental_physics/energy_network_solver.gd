class_name AIdleEnergyNetworkSolver
extends RefCounted

static func balance(production: float, storage: float, capacity: float, demand: float, loss: float) -> Dictionary:
    var usable := maxf(production*(1.0-clampf(loss,0.0,1.0)),0.0)
    var served := minf(usable,demand)
    var from_storage := minf(storage,demand-served)
    served += from_storage
    storage -= from_storage
    storage += minf(maxf(usable-demand,0.0),maxf(capacity-storage,0.0))
    return {"served":served,"unserved":maxf(demand-served,0.0),"storage":storage}
