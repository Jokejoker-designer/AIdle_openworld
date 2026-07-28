# `environment_worker_entry.py` Outline

```python
def main():
    spec = load_and_validate_job_spec()
    template = load_registered_environment_template(spec["template_id"])
    terrain = build_registered_terrain(spec["terrain"])

    for placement in spec["placements"]:
        module = append_registered_module(placement["module_id"])
        apply_safe_transform(module, placement)
        validate_socket_and_bounds(module, placement)

    create_build_plot_marker(spec["build_plot"])
    create_registered_preview_camera(spec["camera_preview"])
    generate_lods_and_hlods()
    write_scene_manifest()
    render_preview_if_requested()
    export_registered_modules()
    run_environment_validation()
```

Không đọc prompt và không chạy code từ request.
