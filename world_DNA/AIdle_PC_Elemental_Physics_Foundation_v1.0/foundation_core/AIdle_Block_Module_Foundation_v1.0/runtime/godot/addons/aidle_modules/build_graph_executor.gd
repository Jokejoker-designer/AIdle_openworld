class_name AIdleBuildGraphExecutor
extends Node3D
signal preview_ready(graph_id:String)
var preview_root:Node3D
func begin_preview(graph:Dictionary)->void:
    if preview_root!=null: preview_root.queue_free()
    preview_root=Node3D.new(); add_child(preview_root)
    for spec in graph.get("nodes",[]):
        var n:=Node3D.new(); n.name=spec.get("node_id","module"); n.set_meta("module_id",spec.get("module_id","")); n.set_meta("preview_only",true); preview_root.add_child(n)
    preview_ready.emit(graph.get("build_graph_id",""))
func cancel_preview()->void:
    if preview_root!=null: preview_root.queue_free(); preview_root=null
