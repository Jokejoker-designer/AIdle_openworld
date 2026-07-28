class_name AIdleFluidNetworkSolver
extends RefCounted

static func solve(nodes: Array, edges: Array) -> Dictionary:
    var available: Dictionary = {}
    for node in nodes:
        available[node.get("node_id","")] = float(node.get("source_flow",0.0))
    var ordered := edges.duplicate()
    ordered.sort_custom(func(a: Dictionary,b: Dictionary)->bool:
        return String(a.get("edge_id","")) < String(b.get("edge_id","")))
    for edge in ordered:
        var source: String = edge.get("from","")
        var target: String = edge.get("to","")
        var sent := minf(float(available.get(source,0.0)), float(edge.get("capacity",0.0)))
        available[source] = float(available.get(source,0.0)) - sent
        available[target] = float(available.get(target,0.0)) + sent * (1.0 - clampf(float(edge.get("loss",0.0)),0.0,1.0))
    return {"available": available}
