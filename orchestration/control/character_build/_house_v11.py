# -*- coding: utf-8 -*-
import hashlib, json, math
from pathlib import Path
import bpy
from mathutils import Euler

JOB="HOUSE_FIDELITY_V11"
GAME=Path(r"E:\AIdle_openworld\game\assets\p1e_cozy\modules\cozy_house_small_A.glb")
CAT=Path(r"E:\AIdle_openworld\game\resources\p1e_cozy\module_catalog.json")
QUAR=Path(r"E:\AIdle_Blender_Bridge_P0\storage\generated_quarantine")/JOB
QUAR.mkdir(parents=True, exist_ok=True)

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1<<20),b""): h.update(c)
    return h.hexdigest()

def mat(n,rgb,rough=0.55,emit=0.0):
    m=bpy.data.materials.new(n); m.use_nodes=True; m.diffuse_color=(*rgb,1)
    b=next((x for x in m.node_tree.nodes if x.type=="BSDF_PRINCIPLED"),None)
    if b:
        b.inputs["Base Color"].default_value=(*rgb,1)
        if "Roughness" in b.inputs: b.inputs["Roughness"].default_value=rough
        if emit>0:
            if "Emission Color" in b.inputs: b.inputs["Emission Color"].default_value=(*rgb,1)
            if "Emission Strength" in b.inputs: b.inputs["Emission Strength"].default_value=emit
    return m

def fin(o,m,bevel=0.05):
    o.data.materials.clear(); o.data.materials.append(m)
    bpy.context.view_layer.objects.active=o; o.select_set(True)
    try:
        bpy.ops.object.modifier_add(type="BEVEL")
        md=o.modifiers[-1]; md.width=bevel; md.segments=3; md.limit_method="ANGLE"
        bpy.ops.object.modifier_apply(modifier=md.name)
    except: pass
    try: bpy.ops.object.shade_smooth()
    except: pass
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    o.select_set(False); return o

def cube(n,loc,sc,m,bevel=0.05):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    o=bpy.context.active_object; o.name=n; o.scale=sc
    return fin(o,m,bevel)

def sph(n,loc,r,m,sc=(1,1,1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=16, ring_count=10)
    o=bpy.context.active_object; o.name=n; o.scale=sc
    return fin(o,m,0.0)

def cyl(n,loc,r,d,m,rot=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, vertices=14)
    o=bpy.context.active_object; o.name=n
    if rot: o.rotation_euler=Euler(rot,"XYZ")
    return fin(o,m,0.0)

bpy.ops.wm.read_factory_settings(use_empty=True)
Mw=mat("M_wall",(0.98,0.88,0.72),0.7)
Mb=mat("M_base",(0.70,0.52,0.92),0.6)
Mr1=mat("M_roof_a",(1.0,0.62,0.22),0.45)
Mr2=mat("M_roof_b",(1.0,0.82,0.25),0.45)
Mr3=mat("M_roof_c",(0.98,0.70,0.35),0.48)
Mr=mat("M_ridge",(0.99,0.92,0.78),0.55)
Md=mat("M_door",(0.72,0.40,0.18),0.5)
Mf=mat("M_frame",(0.90,0.65,0.42),0.5)
Me=mat("M_emit",(1.0,0.75,0.25),0.3,emit=4.0)
Mp=mat("M_pot",(0.88,0.52,0.30),0.55)
Ml=mat("M_lav",(0.68,0.40,0.90),0.55)
Mleaf=mat("M_leaf",(0.35,0.70,0.32),0.55)
Mstem=mat("M_stem",(0.32,0.50,0.28),0.6)
Mmail=mat("M_mail",(0.65,0.40,0.90),0.4)
Ms=mat("M_stone",(0.82,0.76,0.68),0.7)
Msmoke=mat("M_smoke",(0.78,0.55,0.92),1.0,emit=0.2)
Mchim=mat("M_chim",(0.97,0.90,0.82),0.65)
Mdark=mat("M_dark",(0.35,0.18,0.10),0.8)
Mcurt=mat("M_curt",(0.75,0.40,0.85),0.6)
Mknob=mat("M_knob",(1.0,0.88,0.35),0.25,emit=0.4)

bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0,0,0))
root=bpy.context.active_object; root.name="MOD_cozy_house_small_A"

cube("Base",(0,0,0.06),(2.0,1.8,0.14),Mb,0.14)
cube("Body",(0,0,0.72),(1.35,1.18,1.22),Mw,0.16)
# porch
cube("Porch",(0,0.55,0.45),(0.9,0.22,0.7),Mw,0.1)

# thick gable slopes
for sign,nm in ((1,"GF"),(-1,"GB")):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, sign*0.30, 1.52))
    o=bpy.context.active_object; o.name=nm
    o.scale=(1.55,0.95,0.16)
    o.rotation_euler=Euler((sign*math.radians(34),0,0),"XYZ")
    fin(o,Mr,0.04)

# fish scales — create at location WITH rotation, apply transform fully
mats=[Mr1,Mr2,Mr3]
for row in range(9):
    t=row/8.0
    y=0.60 - t*0.62
    z=1.18 + t*0.75
    for col in range(11):
        x=(col-5)*0.145
        if row%2: x+=0.07
        if abs(x)>0.82: continue
        m=mats[(row+col)%3]
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(x,y,z), segments=14, ring_count=10)
        o=bpy.context.active_object; o.name=f"T{row}_{col}"
        o.scale=(1.6,1.35,0.24)
        o.rotation_euler=Euler((math.radians(-34),0,0),"XYZ")
        fin(o,m,0.0)

for i,x in enumerate([-0.5,-0.25,0,0.25,0.5]):
    sph(f"Rd{i}",(x,0.0,1.92),0.09,Mr,(1.2,1.0,0.65))

cube("Chim",(0.4,-0.15,2.0),(0.22,0.22,0.45),Mchim,0.04)
cube("ChimC",(0.4,-0.15,2.24),(0.28,0.28,0.08),Mchim,0.03)
for i,(dx,dy,dz,s) in enumerate([(0,0,0.1,0.08),(0.07,0.05,0.22,0.1),(0.14,0.1,0.34,0.08),(0.22,0.15,0.42,0.06)]):
    sph(f"Sm{i}",(0.4+dx,-0.15+dy,2.28+dz),s,Msmoke)

# door
cube("DF",(0,0.50,0.48),(0.52,0.14,0.88),Mw,0.05)
cube("DFr",(0,0.60,0.50),(0.48,0.06,0.88),Mf,0.05)
cube("Door",(0,0.64,0.48),(0.36,0.05,0.70),Md,0.05)
sph("DArch",(0,0.66,0.92),0.22,Mf,(1.0,0.32,0.55))
sph("Knob",(0.12,0.70,0.48),0.045,Mknob)
cube("S1",(0,0.78,0.10),(0.40,0.18,0.08),Mf,0.03)
cube("S2",(0,0.92,0.05),(0.32,0.14,0.05),Mf,0.02)

for nm,x,z,rr in [("W1",-0.38,0.70,0.10),("W2",0.38,0.48,0.09),("W3",-0.28,1.05,0.095),("W4",0.0,1.28,0.11)]:
    cyl(f"{nm}f",(x,0.62,z),rr+0.025,0.05,Mf,rot=(math.pi/2,0,0))
    sph(f"{nm}g",(x,0.66,z),rr,Me)

cube("SideFill",(0.62,0,0.75),(0.14,0.52,0.44),Mdark,0.02)
cube("SideFr",(0.68,0,0.75),(0.08,0.56,0.48),Mf,0.03)
cube("SideGl",(0.72,0,0.75),(0.04,0.48,0.40),Me,0.01)
cube("CL",(0.66,-0.18,0.80),(0.04,0.08,0.36),Mcurt,0.02)
cube("CR",(0.66,0.20,0.80),(0.04,0.08,0.36),Mcurt,0.02)

cyl("MailP",(0.30,0.78,0.16),0.025,0.20,Mmail)
cube("MailB",(0.30,0.78,0.30),(0.16,0.12,0.12),Mmail,0.04)
cube("MailF",(0.38,0.78,0.34),(0.04,0.02,0.08),Ml,0.01)

cyl("PotB",(-0.70,0.70,0.16),0.11,0.16,Mp)
for i,a in enumerate([0,1.2,2.4,3.6,4.8]):
    x=-0.70+0.04*math.cos(a); y=0.70+0.04*math.sin(a)
    cyl(f"St{i}",(x,y,0.32),0.012,0.22,Mstem)
    sph(f"Bl{i}",(x,y,0.48),0.05,Ml,(0.7,0.7,1.35))
cyl("PS1",(0.50,0.78,0.13),0.055,0.10,Mp); sph("PL1",(0.50,0.78,0.24),0.06,Mleaf)
cyl("PS2",(0.64,0.70,0.12),0.05,0.09,Mp); sph("PL2",(0.64,0.70,0.22),0.05,Ml)
for i,(x,y,s) in enumerate([(-0.12,1.12,0.13),(0.08,1.30,0.11),(-0.02,1.48,0.10)]):
    sph(f"Stn{i}",(x,y,0.03),s,Ms,(1.35,1.05,0.22))

for o in list(bpy.data.objects):
    if o!=root and o.type=="MESH" and o.parent is None:
        o.parent=root; o.matrix_parent_inverse.identity()

q=QUAR/"cozy_house_small_A.glb"
bpy.ops.export_scene.gltf(filepath=str(q),export_format="GLB",use_selection=False,export_apply=True,export_cameras=False,export_lights=False,export_materials="EXPORT")
GAME.write_bytes(q.read_bytes())
print("HOUSE_V11", GAME.stat().st_size, sha(GAME)[:16])
data=json.loads(CAT.read_text(encoding="utf-8"))
for m in data.get("modules",[]):
    if m.get("module_id")=="cozy_house_small_A":
        m["glb_sha256"]=sha(GAME); m["bytes"]=GAME.stat().st_size; m["source"]=JOB; m["visual"]="mockup_house_v11"
CAT.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print("HOUSE_V11_OK")
