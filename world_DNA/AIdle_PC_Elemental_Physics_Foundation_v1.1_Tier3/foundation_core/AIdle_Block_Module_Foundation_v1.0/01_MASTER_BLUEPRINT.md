# Master Blueprint

AIdle là AI-native modular world engine, không phải text-to-image. Thiết kế phức tạp được phân tầng: Primitive → Component → Functional Module → Cluster → Gameplay System → Region Graph → Persistent World.

AI chỉ cấu hình module, socket, material, skeleton, animation, behavior và generator đã đăng ký. Khi thiếu asset, AI tạo Asset Request cho Blender; output phải quarantine và validation.

Blender sở hữu authoring/GLB/LOD. Godot sở hữu animation runtime, behavior, physics, navigation, save, commit và undo.
