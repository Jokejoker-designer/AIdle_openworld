# Blender Authoring Integration

Mỗi module Blender có collection MOD_<module_id>, sockets, material slots, optional skeleton/actions, LOD và collider hints. Grok gửi recipe, không gửi Python. Worker chỉ gọi operation allowlist rồi export GLB + preview + manifest vào quarantine.
