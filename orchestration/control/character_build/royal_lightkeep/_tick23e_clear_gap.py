import bpy, os, shutil
from mathutils import Vector
from datetime import datetime
BASE = r"E:\AIdle_openworld\orchestration\control\character_build\royal_lightkeep"
path = os.path.join(BASE, "ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_FINAL.blend")
bpy.ops.wm.open_mainfile(filepath=path)
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BASE, f"ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_BACKUP_LOOP_{STAMP}.blend"), copy=True)

def mesh_local_size(obj):
    me = obj.data
    xs=[v.co.x for v in me.vertices]; ys=[v.co.y for v in me.vertices]; zs=[v.co.z for v in me.vertices]
    return Vector((max(xs)-min(xs) or 1e-6, max(ys)-min(ys) or 1e-6, max(zs)-min(zs) or 1e-6))

def set_size(obj, sx, sy, sz, bottom_z=None, center_xy=None):
    loc = mesh_local_size(obj)
    obj.scale = Vector((sx/loc.x, sy/loc.y, sz/loc.z))
    bpy.context.view_layer.update()
    if center_xy is not None:
        obj.location.x, obj.location.y = center_xy
    if bottom_z is not None:
        obj.location.z = bottom_z + obj.dimensions.z/2.0

def assign(obj, mat):
    if obj.data.materials: obj.data.materials[0]=mat
    else: obj.data.materials.append(mat)

MAT_ROOF = bpy.data.materials.get("MAT_SLATE_NAVY")
MAT_STONE = bpy.data.materials.get("MAT_LIMESTONE")

# Force clear gap: any right-side roof/arm with min world X < 12.5 pull right
for o in list(bpy.data.objects):
    if o.type != "MESH" or o.hide_render: continue
    n = o.name.upper()
    if not (n.startswith("RIGHT_") or "CONNECTOR_TO_RIGHT" in n):
        continue
    corners=[o.matrix_world @ Vector(c) for c in o.bound_box]
    minx=min(c.x for c in corners)
    if minx < 12.5:
        delta = 12.5 - minx + 0.5
        o.location.x += delta
        print("PUSH", o.name, "by", round(delta,2), "newx", round(o.location.x,2))

# Explicit layout: L-arm as rear connector only, not tower-side wall
o=bpy.data.objects.get("RIGHT_L_ARM")
if o:
    set_size(o, 8.0, 4.0, 6.5, bottom_z=5.8, center_xy=(16.0, -10.0))
    assign(o, MAT_STONE)
o=bpy.data.objects.get("RIGHT_L_ARM_ROOF")
if o:
    set_size(o, 8.5, 4.5, 2.8, bottom_z=12.5, center_xy=(16.0, -10.0))
    assign(o, MAT_ROOF)

o=bpy.data.objects.get("RIGHT_WING_APRON")
if o:
    set_size(o, 12.0, 10.0, 2.8, bottom_z=5.8, center_xy=(19.0, -1.5))
    assign(o, MAT_STONE)

o=bpy.data.objects.get("RIGHT_WING_ROOF")
if o:
    set_size(o, 11.0, 10.0, 3.2, bottom_z=14.0, center_xy=(19.0, -1.5))
    assign(o, MAT_ROOF)

o=bpy.data.objects.get("RIGHT_WING_MAIN")
if o:
    set_size(o, 11.0, 10.0, 7.5, bottom_z=6.0, center_xy=(19.0, -1.0))
    assign(o, MAT_STONE)

# Rear courtyard roof should not wrap past tower right face as blue slab
o=bpy.data.objects.get("COURTYARD_REAR_WING_ROOF")
if o:
    set_size(o, 12.0, 5.0, 3.0, bottom_z=12.8, center_xy=(0.0, -10.5))
    assign(o, MAT_ROOF)

# Verify
print("---CHECK---")
for name in ["RIGHT_L_ARM_ROOF","RIGHT_WING_ROOF","RIGHT_WING_APRON","RIGHT_GATE_ROOF","RIGHT_WING_MAIN"]:
    o=bpy.data.objects.get(name)
    if not o: continue
    corners=[o.matrix_world @ Vector(c) for c in o.bound_box]
    minx=min(c.x for c in corners)
    print(name, "minx", round(minx,2), "OK" if minx>=12.0 else "BAD")

scene=bpy.context.scene
try: scene.render.engine="BLENDER_EEVEE_NEXT"
except: scene.render.engine="BLENDER_EEVEE"
scene.render.resolution_x=1280; scene.render.resolution_y=960
out=os.path.join(BASE,"renders_final")
for cam,fn in [("CAM_01_FRONT","final_front.png"),("CAM_05_FRONT_3Q","final_front_3q.png"),("CAM_TOP_PLAN","final_top.png"),("CAM_04_RIGHT","final_right.png")]:
    c=bpy.data.objects.get(cam)
    if not c: continue
    scene.camera=c
    scene.render.filepath=os.path.join(out,fn)
    bpy.ops.render.render(write_still=True)
    print("OK", fn)
# work proofs
w=os.path.join(BASE,"renders_pass1d")
for cam,fn in [("CAM_01_FRONT","current_front_work.png"),("CAM_05_FRONT_3Q","current_front_3q_work.png")]:
    scene.camera=bpy.data.objects.get(cam)
    scene.render.filepath=os.path.join(w,fn)
    bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=path)
shutil.copy2(path, os.path.join(BASE,"ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS8_FINAL.blend"))
shutil.copy2(path, os.path.join(BASE,"ROYAL_LIGHTKEEP_WATCHTOWER_BARRACKS_01_PASS1D.blend"))
print("SAVED")
