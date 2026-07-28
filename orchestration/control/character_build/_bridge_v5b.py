
import bpy, math, hashlib, json, shutil
from pathlib import Path
TAU=math.tau
JOB='BUILDINGS_FIDELITY_V5B_BRIDGE'
GAME=Path(r'E:\AIdle_openworld\game\assets\p1e_cozy\modules')
QUAR=Path(r'E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine')/JOB
QUAR.mkdir(parents=True, exist_ok=True)
CAT=Path(r'E:\AIdle_openworld\game\resources\p1e_cozy\module_catalog.json')

def mat(n,rgb,rough=0.55):
    m=bpy.data.materials.new(n); m.use_nodes=True
    m.diffuse_color=(*rgb,1)
    b=next((x for x in m.node_tree.nodes if x.type=='BSDF_PRINCIPLED'),None)
    if b:
        b.inputs['Base Color'].default_value=(*rgb,1)
        if 'Roughness' in b.inputs: b.inputs['Roughness'].default_value=rough
    return m
def setm(o,m):
    o.data.materials.clear(); o.data.materials.append(m)
def cube(n,loc,sc,m):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.active_object; o.name=n; o.scale=sc
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); setm(o,m); return o
def sph(n,loc,r,m,sc=(1,1,1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r,location=loc,segments=10,ring_count=8)
    o=bpy.context.active_object; o.name=n; o.scale=sc
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); setm(o,m); return o
def cyl(n,loc,r,d,m,v=10):
    bpy.ops.mesh.primitive_cylinder_add(radius=r,depth=d,location=loc,vertices=v)
    o=bpy.context.active_object; o.name=n; setm(o,m); return o

bpy.ops.wm.read_factory_settings(use_empty=True)
Ms1=mat('s1',(0.90,0.86,0.88)); Ms2=mat('s2',(0.80,0.76,0.82)); Ms3=mat('s3',(0.94,0.90,0.92))
Mleaf=mat('l',(0.4,0.75,0.45)); Mpk=mat('p',(0.95,0.55,0.70))
bpy.ops.object.empty_add(type='PLAIN_AXES'); root=bpy.context.active_object; root.name='MOD_cozy_bridge_arch_A'
# abutments with clear opening between
cube('AbL',(-1.15,0,0.35),(0.55,0.80,0.70),Ms2)
cube('AbR',(1.15,0,0.35),(0.55,0.80,0.70),Ms2)
# arch ring of boxes along semicircle — leave center void
n=9
for i in range(n):
    t=i/(n-1); ang=math.pi*t
    x=1.05*math.cos(ang); z=0.55+0.75*math.sin(ang)
    o=cube(f'V{i}',(x,0,z),(0.26,0.58,0.20),[Ms1,Ms2,Ms3][i%3])
    # tilt so long axis follows arch tangent
    o.rotation_euler=(0, ang-math.pi/2, 0)
    bpy.context.view_layer.objects.active=o; o.select_set(True)
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=False); o.select_set(False)
cube('Key',(0,0,1.30),(0.30,0.60,0.24),Ms3)
# deck on top of arch only
for i in range(5):
    t=(i+0.5)/5; x=-0.75+t*1.5
    cube(f'D{i}',(x,0,1.42),(0.30,0.70,0.12),[Ms1,Ms2,Ms3][i%3])
for side,y in (('L',0.40),('R',-0.40)):
    for i,t in enumerate([0.25,0.5,0.75]):
        x=-0.7+t*1.4
        cube(f'R{side}{i}',(x,y,1.55),(0.16,0.12,0.18),[Ms1,Ms2,Ms3][i%3])
cyl('St',(-1.35,0.5,0.1),0.025,0.2,Mleaf,5); sph('Bl',(-1.35,0.5,0.25),0.08,Mpk)
for o in list(bpy.data.objects):
    if o!=root and o.type=='MESH' and o.parent is None:
        mw=o.matrix_world.copy(); o.parent=root; o.matrix_world=mw
q=QUAR/'cozy_bridge_arch_A.glb'
bpy.ops.export_scene.gltf(filepath=str(q),export_format='GLB',use_selection=False,export_apply=True)
dest=GAME/'cozy_bridge_arch_A.glb'; shutil.copy2(q,dest)
h=hashlib.sha256(dest.read_bytes()).hexdigest()
print('BRIDGE_V5B',h,dest.stat().st_size)
cat=json.loads(CAT.read_text(encoding='utf-8'))
for m in cat['modules']:
    if m.get('module_id')=='cozy_bridge_arch_A':
        m['glb_sha256']=h; m['bytes']=dest.stat().st_size; m['source']='BUILDINGS_FIDELITY_V5B_BRIDGE'; m['visual']='box_voussoir_clear_arch_v5b'
CAT.write_text(json.dumps(cat,indent=2)+'\n',encoding='utf-8')
print('OK')
