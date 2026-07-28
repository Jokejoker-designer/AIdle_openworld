import bpy
import os
from mathutils import Vector
import bmesh

# open file
path = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep\ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS1D.blend"
bpy.ops.wm.open_mainfile(filepath=path)
print("OPEN", bpy.data.filepath, "OBJ", len(bpy.data.objects))

def mesh_local_size(obj):
    me = obj.data
    xs=[v.co.x for v in me.vertices]; ys=[v.co.y for v in me.vertices]; zs=[v.co.z for v in me.vertices]
    return Vector((max(xs)-min(xs) or 1e-6, max(ys)-min(ys) or 1e-6, max(zs)-min(zs) or 1e-6))

def set_size(obj, sx,sy,sz, bottom_z=None, center_xy=None):
    loc = mesh_local_size(obj)
    obj.scale = Vector((sx/loc.x, sy/loc.y, sz/loc.z))
    if center_xy is not None:
        obj.location.x, obj.location.y = center_xy
    if bottom_z is not None:
        obj.location.z = bottom_z + sz/2.0

def ensure_cube(name, mat_name='CLAY_TOWER'):
    o = bpy.data.objects.get(name)
    if o:
        o.hide_render = False
        return o
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=2.0); bm.to_mesh(mesh); bm.free()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(o)
    mat = bpy.data.materials.get(mat_name)
    if mat:
        if o.data.materials: o.data.materials[0]=mat
        else: o.data.materials.append(mat)
    return o

CX,CY=1.5,5.0
TERR=5.8

# PASS4 remaining details
for side, x in [('L', CX-4.9), ('R', CX+4.9)]:
    for row, z0 in enumerate([18.5, 22.5, 25.5]):
        for col, yoff in enumerate([-1.5, 1.5]):
            set_size(ensure_cube(f'WIN_FRAME_{side}_{row}_{col}'), 0.35, 1.8, 2.3, bottom_z=z0-0.1, center_xy=(x, CY+yoff))

set_size(ensure_cube('EMBLEM_PLATE_MAIN'), 2.2, 0.25, 2.8, bottom_z=19.5, center_xy=(CX, CY+5.1))
set_size(ensure_cube('EMBLEM_PLATE_UPPER'), 1.6, 0.25, 1.8, bottom_z=30.5, center_xy=(CX, CY+6.0))

for side, x in [('L', CX-4.3), ('R', CX+4.3)]:
    set_size(ensure_cube(f'STAIR_RAIL_{side}'), 0.35, 14.0, 1.0, bottom_z=2.5, center_xy=(x, 16.0))
    set_size(ensure_cube(f'STAIR_RAIL_POST_{side}'), 0.4, 0.4, 3.5, bottom_z=0.5, center_xy=(x, 22.0))

set_size(ensure_cube('BANNER_PANEL_L','CLAY_VOID'), 1.2, 0.15, 2.5, bottom_z=21.0, center_xy=(CX-3.5, CY+5.2))
set_size(ensure_cube('BANNER_PANEL_R','CLAY_VOID'), 1.2, 0.15, 2.5, bottom_z=21.0, center_xy=(CX+3.5, CY+5.2))

base = os.path.dirname(path)
p4f = os.path.join(base, 'ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS4_FINAL.blend')
bpy.ops.wm.save_as_mainfile(filepath=p4f)
print('PASS4_FINAL saved')

# PASS5 materials
def make_mat(name, color, rough=0.7, metal=0.0):
    m = bpy.data.materials.get(name)
    if not m:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (*color, 1)
        bsdf.inputs['Roughness'].default_value = rough
        if 'Metallic' in bsdf.inputs:
            bsdf.inputs['Metallic'].default_value = metal
    m.diffuse_color = (*color, 1)
    return m

MAT_STONE = make_mat('MAT_LIMESTONE', (0.72, 0.70, 0.65), 0.85, 0.0)
MAT_DARK = make_mat('MAT_DARK_STONE', (0.28, 0.27, 0.26), 0.9, 0.0)
MAT_ROOF = make_mat('MAT_SLATE_NAVY', (0.12, 0.18, 0.32), 0.55, 0.05)
MAT_GOLD = make_mat('MAT_GOLD_TRIM', (0.75, 0.58, 0.22), 0.35, 0.85)
MAT_WOOD = make_mat('MAT_WOOD', (0.25, 0.15, 0.08), 0.7, 0.0)
MAT_GLASS = make_mat('MAT_GLASS', (0.55, 0.65, 0.75), 0.15, 0.0)
MAT_BANNER = make_mat('MAT_BANNER_BLUE', (0.08, 0.15, 0.45), 0.65, 0.0)

def assign(obj, mat):
    if not obj or obj.type != 'MESH':
        return
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

for o in bpy.data.objects:
    if o.type != 'MESH' or o.hide_render:
        continue
    n = o.name.upper()
    if any(k in n for k in ('ROOF', 'HIP', 'RIDGE', 'GABLE_PEAK', 'GABLE_ROOF', 'PAVILION_ROOF', 'PAVILION_PEAK', 'CORNER_CAP', 'FINIAL')):
        assign(o, MAT_ROOF)
    elif 'BANNER_PANEL' in n:
        assign(o, MAT_BANNER)
    elif any(k in n for k in ('BANNER_MOUNT', 'TRIM', 'CORNICE', 'EMBLEM', 'FRAME', 'FINIAL', 'RAIL')):
        assign(o, MAT_GOLD)
    elif any(k in n for k in ('WIN_', 'ARCH', 'VOID', 'INNER_DARK', 'TUNNEL_VOID', 'RECESS', 'SLIT')):
        assign(o, MAT_GLASS if ('WIN' in n or 'ARCH' in n) else MAT_DARK)
    elif any(k in n for k in ('BASE_', 'OUTER_', 'BASTION', 'PARAPET', 'LEVEL', 'TERRACE', 'GROUND', 'PODIUM')):
        assign(o, MAT_DARK if ('LEVEL0' in n or 'GROUND' in n) else MAT_STONE)
    elif 'STAIR' in n or 'DOOR' in n:
        assign(o, MAT_STONE)
    elif any(k in n for k in ('TOWER', 'GH_', 'BARRACKS', 'RIGHT_', 'BAR_', 'GATE', 'WALL', 'PIER', 'LINTEL', 'SHOULDER', 'CONNECTOR', 'PAVILION', 'COURT')):
        assign(o, MAT_STONE)

p5 = os.path.join(base, 'ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS5_V01.blend')
bpy.ops.wm.save_as_mainfile(filepath=p5)
import shutil
shutil.copy2(p5, path)
print('PASS5_V01 + synced to PASS1D')

# render
scene = bpy.context.scene
try:
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
except Exception:
    try:
        scene.render.engine = 'BLENDER_EEVEE'
    except Exception:
        scene.render.engine = 'CYCLES'
out = os.path.join(base, 'renders_pass1d')
out5 = os.path.join(base, 'renders_pass5')
os.makedirs(out, exist_ok=True)
os.makedirs(out5, exist_ok=True)
for cam, fn in [
    ('CAM_01_FRONT', 'current_front_work.png'),
    ('CAM_05_FRONT_3Q', 'current_front_3q_work.png'),
    ('CAM_06_REAR_3Q', 'current_rear_3q_work.png'),
    ('CAM_TOP_PLAN', 'current_top_plan_work.png'),
    ('CAM_01_FRONT', 'pass5_front.png'),
    ('CAM_05_FRONT_3Q', 'pass5_front_3q.png'),
    ('CAM_02_REAR', 'pass5_rear.png'),
    ('CAM_03_LEFT', 'pass5_left.png'),
    ('CAM_04_RIGHT', 'pass5_right.png'),
]:
    c = bpy.data.objects.get(cam)
    if not c:
        print('MISS', cam)
        continue
    scene.camera = c
    dest = out5 if fn.startswith('pass5') else out
    scene.render.filepath = os.path.join(dest, fn)
    bpy.ops.render.render(write_still=True)
    print('OK', fn)

print('DONE OBJ', len(bpy.data.objects))
