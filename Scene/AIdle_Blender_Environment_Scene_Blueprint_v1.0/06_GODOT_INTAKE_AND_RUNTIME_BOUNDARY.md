# Godot Intake and Runtime Boundary

## Blender xuất gì?

- mesh
- material slot
- LOD names
- transform
- socket markers
- collision hints
- navigation hints
- camera focus marker
- manifestation order metadata

## Godot tạo gì?

- StaticBody3D/Area3D
- CollisionShape3D runtime
- NavigationRegion3D bake
- interaction nodes
- ownership
- save IDs
- World Commit references
- dynamic vegetation/water behavior
- gameplay VFX
- materialization state machine

## Manifestation sequence

Theo World Genesis:

1. Grid và địa hình
2. Wireframe
3. Hologram
4. Đường đi
5. Nhà/nơi trú
6. Cây cối
7. Vật thể tương tác
8. Ánh sáng
9. Companion
10. Collision và navigation
11. Save receipt
12. Complete

Blender package cung cấp `content_phase` và `manifestation_order` cho từng
module. Đây chỉ là thứ tự nội dung. Godot mới sở hữu state machine
`wireframe -> hologram -> materializing -> complete` và chỉ kích hoạt collision
sau explicit confirm + World Commit.

P0E không được patch Godot scene hoặc approved catalog. Godot intake chỉ được
mở sau P0E verification và Human G8 decision.

## Required Godot intake tests

- tất cả GLB import
- object IDs unique
- scene origin đúng
- material slots resolve
- socket markers resolve
- collision hint không được dùng như collision chính thức trước commit
- navigation bake thành công
- build plot trống
- camera không bị che
- cancel hologram không để orphan node
- save/reload không duplicate
- revision conflict hiển thị rõ
