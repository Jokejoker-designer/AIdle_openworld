# Grok ↔ Blender MCP — smoke prompts (copy/paste)

**Prereq:** Blender open, BlenderMCP tab → **Connect**, Grok restarted after MCP config.

---

### 1. Connection
```
Dùng MCP blender: kiểm tra kết nối Blender. Liệt kê tên scene, object count, và version Blender nếu có.
```

### 2. Cast animation audit (Bụi Mơ / Cinder)
```
Mở scene hiện tại trong Blender. Liệt kê tất cả Action / animation names.
Kiểm tra có đủ: walk, idle, và (nếu cinder) hammer_loop, stoke_fire, charge_ember.
Với Action "walk": báo số fcurve và có keyframe trên bone leg_L / leg_R không.
```

### 3. Zero-scale hygiene
```
Quét toàn scene: object hoặc bone nào có scale x/y/z ≈ 0.
Liệt kê tên + scale. Không sửa trừ khi tôi bảo "fix scale".
```

### 4. Safe GLB export (staging only)
```
Export GLB (include all actions) tới:
E:\AIdle_openworld\tools\blender-mcp\exports\mcp_smoke_<slug>.glb
Slug lấy từ tên file/character đang mở. Không ghi đè game/assets.
Sau export, in full path + file size.
```

### 5. Material / leaf pass (optional)
```
Liệt kê material names chứa "leaf", "cream", "ember", "dark".
Chỉ report albedo base color — chưa đổi.
```

---

Sau export OK → handoff install Godot (agent/script):

1. Backup live `*_rigged.glb`
2. Copy staging → live path
3. Update `cast_roster.json` `glb_sha256`
4. Clear `.godot/imported/*slug*`
5. Headless Godot smoke
