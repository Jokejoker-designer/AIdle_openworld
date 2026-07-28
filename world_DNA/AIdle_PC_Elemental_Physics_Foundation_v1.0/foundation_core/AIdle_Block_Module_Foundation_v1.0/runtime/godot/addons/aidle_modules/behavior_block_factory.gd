class_name AIdleBehaviorBlockFactory
extends Node
func create_behavior(id: String,config: Dictionary)->Node:
    var n:=Node.new(); n.name=id; n.set_meta("config",config.duplicate(true)); n.process_mode=Node.PROCESS_MODE_DISABLED; return n
