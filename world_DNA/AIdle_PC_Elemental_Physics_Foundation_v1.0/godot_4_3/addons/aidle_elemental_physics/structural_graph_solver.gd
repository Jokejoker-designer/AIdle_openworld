class_name AIdleStructuralGraphSolver
extends RefCounted

static func evaluate(nodes: Array, edges: Array) -> Dictionary:
    var supported: Dictionary = {}
    for node in nodes:
        supported[node.get("node_id","")] = bool(node.get("is_foundation", false))
    var changed := true
    while changed:
        changed = false
        for edge in edges:
            var a: String = edge.get("supporter","")
            var b: String = edge.get("supported","")
            if supported.get(a,false) and not supported.get(b,false):
                supported[b] = true
                changed = true
    var unsupported: Array[String] = []
    for node_id in supported:
        if not supported[node_id]:
            unsupported.append(node_id)
    unsupported.sort()
    return {"stability_score": 1.0 - float(unsupported.size()) / maxf(float(nodes.size()),1.0),
            "unsupported_nodes": unsupported}
