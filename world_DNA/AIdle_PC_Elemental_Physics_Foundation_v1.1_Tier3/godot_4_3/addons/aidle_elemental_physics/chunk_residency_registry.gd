class_name AIdleChunkResidencyRegistry
extends Node

signal chunk_residency_changed(chunk_id: StringName, loaded: bool)
var _loaded_chunks: Dictionary = {}

func set_chunk_loaded(chunk_id: StringName, loaded: bool) -> void:
    _loaded_chunks[chunk_id] = loaded
    chunk_residency_changed.emit(chunk_id, loaded)

func is_chunk_loaded(chunk_id: StringName) -> bool:
    return bool(_loaded_chunks.get(chunk_id, false))
