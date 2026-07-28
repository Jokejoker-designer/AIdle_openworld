# Blender PC Pipeline

PC asset giữ cùng origin, scale, sockets, material slots, animation names và
gameplay bounds với mobile asset. Nó có thể thêm LOD0 chi tiết hơn, LOD3, state
variants, VFX anchors và physics hints.

Blender tạo mesh, Geometry Nodes variation, material slots, armature/action,
state variants, collision/fluid/reaction hints, GLB và manifest. Blender không
thực thi gameplay hay World Commit.
